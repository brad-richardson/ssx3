# P13 — Analyzer silent-fold triage (files beyond elf_analyzer.cpp)

Brief `local/muse/prompts/P13.md`. Read-only audit + patch spec, no
implementation. Tables, no verdicts. Stale-reading guard: P1 REPORT
Part 24 §P24-1f/g (179-site census, 12 exclusion rules, the explicit
boundary: analyzer files beyond `elf_analyzer.cpp` untriaged) and the
P1g/P8-1a MMIO-fold notes (LUI-only detector silently narrowing guest
semantics to page base) + P1h/P9-1 (low-half fold; sibling LUI-only
scans left untouched). P1ad/M16 run concurrently in other panes —
nothing shared.
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`, HEAD `da6a2d5` at read time), `S=/Volumes/Extreme
SSD/ps2x-p13` (scratch). File:line refs below are `$R`-relative
unless noted. Receipts: `local/research/P13/receipts/`.

## P13-0. Rules record

| Rule | Compliance |
|---|---|
| READ ONLY (no fork writes/commits/pushes, no boots, no lease, no `adb`) | Held: fork touched only by `grep`/`sed`/`awk`/*read*; `git -C $R` read-only (`log`); no boot, no lease file read or written, no `adb` |
| Installed tools only, no downloads | Held: `python3` stdlib, `grep`/`sed`/`awk`/`sort`/`uniq`/`find`/`stat`/`ls`, `git`; macOS `objdump` present but unused |
| Scratch `S` only; never `/tmp/p1-link`, `ps2x-i*`, `ps2x-p1*`, `m*/`, others' dirs | Held: all scripts + intermediates under `S`; `ls /tmp/p1-link` never run |
| Evidence `local/research/P13/` ONLY, never `P1/REPORT.md` | Held: this file + `receipts/` only; `P1/REPORT.md` opened read-only |
| Commit `git add -f`, prefix `[P13]`, trailer `Orchestrated-By: Muse Code`, NEVER `git push` in ssx3 | Commit per §P13-6; no push |
| 4 h box | Single session, no boots/builds; regression runs are file greps + stdlib sweeps only |

## P13-1. Inventory (analyzer pipeline beyond elf_analyzer.cpp)

`elf_analyzer.cpp` (1934 lines, P1w-covered) excluded from findings;
referenced only for consequence routing. Order follows the
ELF→TOML→recomp data flow.

| # | File | Lines | Pass role | Input → output |
|---|---|---|---|---|
| A1 | `ps2xAnalyzer/src/analyzer_main.cpp` | 73 | CLI front-end | argv (elf, toml, dbdir) → `ElfAnalyzer::{analyze,generateToml}` rc |
| A2 | `ps2xAnalyzer/src/elf_analysis_context.cpp` | 83 | Shared analysis store | functions/symbols/sections/relocs → indexed store + decode cache |
| A3 | `ps2xAnalyzer/src/sce_symbol_scanner.cpp` | 793 | SCE SDK fingerprint matcher | code sections + symbol DB (embedded JSON / override dir) → `SceSymbolMatch` list |
| A4 | `ps2xAnalyzer/src/function_classifier.cpp` | 218 | Lib-vs-game name classifier | symbol name → lib bool (runtime-handler / SCE / kernel-regex / libc / prefix rules) |
| A5 | `ps2xAnalyzer/src/analysis_passes.cpp` | 446 | Heuristic passes | decoded instructions + sections → HW/MMI/SMC signals, jump tables, recursion set |
| A6 | `ps2xAnalyzer/src/toml_generator.cpp` | 237 | TOML emitter | context + lib sets + mmio + tables + patches + perf → `[general]/[mmio]/[jump_tables]/[patches]/[performance]` |
| R1 | `ps2xRecomp/src/lib/elf_parser.cpp` | 1436 | ELF + map ingestion | ELF + DWARF + Ghidra CSV → sections/symbols/relocs/functions |
| R2 | `ps2xRecomp/src/lib/config_manager.cpp` | 348 | TOML config loader | TOML bytes → `RecompilerConfig` (stubs/skip/patches/mmio/jump tables/flags) |
| R3 | `ps2xRecomp/src/lib/r5900_decoder.cpp` | 1066 | Disassembler front-end | (addr, raw) → `Instruction` (Rabbitizer flags + hand `modificationInfo`) |
| R4 | `ps2xRecomp/src/lib/ps2_recompiler.cpp` | 2251 | Pipeline driver | config + ELF → stub/skip/decode decisions → per-function codegen → headers/register |
| R5 | `ps2xRecomp/src/lib/control_flow_analyzer.cpp` | 431 | Static CFG + JR resolution | function + instructions → entryPoints/resume/indirectFallback/jumpTableTargets |
| R6 | `ps2xRecomp/src/lib/control_flow_emitter.cpp` | 581 | Branch/jump emitter | branch + delay slot + analysis → C++ (`goto`/dispatch/conditions) |
| R7 | `ps2xRecomp/src/lib/instruction_translator.cpp` | 365 | Base-ISA translator | I-type/load/store/unprivileged → C++ (+ MemoryAccessHint fast paths) |
| R8 | `ps2xRecomp/src/lib/special_translator.cpp` | 188 | SPECIAL translator | R-type ALU/shift/mult/div/trap/syscall → C++ |
| R9 | `ps2xRecomp/src/lib/regimm_translator.cpp` | 57 | REGIMM translator | branches (comment) + traps + MTSAB/MTSAH → C++ |
| R10 | `ps2xRecomp/src/lib/cop0_translator.cpp` | 167 | COP0 translator | MF/MT/BC/CO → C++ (masks + ignores + TLB/ERET runtime calls) |
| R11 | `ps2xRecomp/src/lib/fpu_translator.cpp` | 146 | FPU translator | MFC1/MTC1/CFC1/CTC1/S/W → C++ |
| R12 | `ps2xRecomp/src/lib/mmi_translator.cpp` | 139 | MMI dispatch | MMI fn → SIMD C++ or MMI0–3/PMFHL/PMTHL helpers |
| R13 | `ps2xRecomp/src/lib/mmi_translation_helpers.cpp` | 608 | MMI0–3/PMFH[L]/PMTH[L] cases | subfunction → `_mm_*` C++ |
| R14 | `ps2xRecomp/src/lib/vu_translator.cpp` | 399 | VU0-macro translator | QMFC2/CFC2/QMTC2/CTC2/BC2/CO → C++ |
| R15 | `ps2xRecomp/src/lib/vu_translation_helpers.cpp` | 886 | VU arithmetic cases | Special1/Special2 fn → SSE C++ |
| R16 | `ps2xRecomp/src/lib/gif_dma_kick_analyzer.cpp` | 374 | Const tracker + kick fusion | linear const-prop + 4×SW pattern → `MemoryAccessHint` / `GifDmaKickPlan` |
| R17 | `ps2xRecomp/src/lib/function_emitter.cpp` | 239 | Function body emitter | instructions + analysis → labels, pc publishes, GIF suppression, delay slots |
| R18 | `ps2xRecomp/src/lib/jump_table_switch_emitter.cpp` | 46 | Jump-table emitter | (index reg, entries) → `switch` + calls |
| R19 | `ps2xRecomp/src/lib/function_table_emitter.cpp` | 176 | Registration emitter | functions + stub map → dispatch tables |
| R20 | `ps2xRecomp/src/lib/code_generator.cpp` | 308 | Translator dispatch + `emitUnhandledInstruction` | `Instruction` → translator string; unhandled → reporter error + runtime `throw` |
| R21 | `ps2xRecomp/src/lib/recompiler_reporter.cpp` | 243 | Loud channel (counts/warnings/errors/summary) | events → recomp log + noted terminal summary |

Placement notes: `ResliceEntryFunctions`/`DiscoverAdditionalEntryPoints`
(public statics, `ps2_recompiler.cpp:2210-2231`) are called only from
`ps2xTest/src/ps2_recompiler_tests.cpp` (8 call sites) — the
pending/reslice lane (same file :275-730) is test-only; SSX3
`$W/P1/output/` holds 0 `entry_*` files (receipt: `ls|grep -c` = 0).

## P13-2. Audit (per-file silent folds/drops)

Each row: the exact discard + minimal trigger. Loud paths
(`emitUnhandledInstruction`, reporter warning/error, `cerr`) are
listed once in §P13-2b, not per finding.

### A. Reached in SSX3 output (strongest first)

| ID | Site | Exact discard | Minimal trigger |
|---|---|---|---|
| F1 | R17 `function_emitter.cpp:128-141` (`makeSyntheticDelaySlot`) | Branch whose delay slot is not the next decoded word gets an **invisible NOP** (no comment, no marker, no warning); the real word compiles (if at all) as another function's entry | Function bound splits a branch from its delay slot and no merge extends past it |
| F2 | R1 `elf_parser.cpp:1421-1423` + `:1085-1110` + `:722` (JAL pre-population → CSV merge, max-end-wins) | 347 CSV function ends silently **widened** to JAL-fallback ends (next-JAL-start or section end); same-start dedup keeps the **largest** end; JAL rows pruned without count | CSV start ∈ JAL-target set with JAL-end > CSV end |
| F3 | R4 `ps2_recompiler.cpp:768-793` (stub selector install) | Stub/skip selectors matching **zero** functions are silently inert (no coverage check, no warning); intent (stub that code) silently unfulfilled | TOML stub `name@addr` with neither name nor start in the function list |
| F4 | R6 `control_flow_emitter.cpp:400-427` (`conditionalBranchExpression`) | BLEZ/BLEZL/BGTZ/BGTZL/REGIMM branches compare **`GPR_S32`** (low 32) while BEQ/BNE use `GPR_U64`: 64-bit Rs values silently narrowed (e.g. `0xFFFFFFFF_00000001` reads positive) | Any 64-bit (non-sign-extended-32) Rs at a BLEZ/BGTZ/REGIMM branch |
| F5a | R8 `special_translator.cpp:49-50` | `SYNC` → comment only (barrier ignored) | `SYNC` in a recompiled function |
| F5b | R7 `instruction_translator.cpp:342-343` | `CACHE` → comment only (ignored) | `CACHE` in a recompiled function |
| F5c | R14 `vu_translator.cpp:72-74,84-86` | `CTC2` to VI0 / MAC(17) → comment only (write discarded) | `CTC2` with rd 0/17 |
| F6 | R1 `elf_parser.cpp:1085-1110` (same-start sort: real-name-first) | Same-start CSV rows collapse to one; **name** half of the dedup is silent (no count) | Duplicate CSV starts |
| F7 | R4 `generateOutput`/`writeToFile` (`ps2_recompiler.cpp:1077-1090,2095-2110`) | Regen never purges **stale** output files (renamed functions orphan dead files that still compile into the build) | Any function rename between regens |
| F8 | A2 `elf_analysis_context.cpp:36-44` (`buildFunctionIndex`) | Duplicate starts overwrite the index **last-wins**, no warning | Duplicate function starts in the loaded map |

### B. Reached-partially / armed-but-unmatched (latent true-unknowns)

| ID | Site | Exact discard | Minimal trigger |
|---|---|---|---|
| F9a | R10 `cop0_translator.cpp:74` | `MFC0` unknown rd → `SET_GPR_S32(...,0)` + comment (folds to 0) | `MFC0` rd ∉ 22 known regs |
| F9b | R10 `cop0_translator.cpp:124` | `MTC0` unknown rd → comment only (write discarded) | `MTC0` rd ∉ known set |
| F10a | R11 `fpu_translator.cpp:36` | `CFC1` fs∉{0,31} → `SET_GPR_U32(...,0)` + comment | `CFC1` to other FCR |
| F10b | R11 `fpu_translator.cpp:42` (+ dead `return ""` :43) | `CTC1` fs≠31 → comment only; unreachable statement after | `CTC1` to FCR≠31 |
| F11a | R14 `vu_translator.cpp:62` | `CFC2` rd∉({<16}∪known CRs) → comment only, **GPR left stale** (no write at all — worse than a 0-fold) | `CFC2` rd ∈ {19,23,24,25,30} |
| F11b | R14 `vu_translator.cpp:101` | `CTC2` rd∉known → comment only | `CTC2` rd ∈ {19,23,24,25,30} |
| F12a | R6 `control_flow_emitter.cpp:426` | Unknown REGIMM rt in branch position → condition `"false"` (**never taken**) | REGIMM branch rt ∉ 8 handled |
| F12b | R6 `control_flow_emitter.cpp:447` (+ missing `OPCODE_COP0` case) | Any other `isBranch` opcode → `"false"`; in particular **BC0** (TLB/exception branches) never taken | BC0* in code (0 today) |
| F12c | R6 `control_flow_emitter.cpp:63-78` (`isLikelyBranch` lacks COP0) | BC0FL/BC0TL treated as non-likely (delay slot always runs) | BC0 likely-branches |
| F12d | R6 `control_flow_emitter.cpp:431-444` | COP1/COP2 BC with reserved rt (∉{0..3}) folds to **BCT** semantics | Reserved BC rt encodings |
| F13 | R18 `jump_table_switch_emitter.cpp:38-40` (+ `:24-30` `func_<hex>` invented callee) | Runtime index outside table entries → comment + `return` (falls through, no trap/census); unknown target names invented silently | Indirect jump with out-of-table index |
| F14a | R16 `gif_dma_kick_analyzer.cpp:136-161` (`isDirectMemoryAccess`) | LWL/LWR/LDL/LDR/LDC1/LWC2/SWL/SWR/SDL/SDR/SDC1/SWC2/LL/SC are **not** memory accesses here: interleaved with a kick pattern they neither abort the plan nor get suppressed (deferred-write reordering vs in-place access) | Unlisted memop inside a matched 4×SW kick window |
| F14b | R16 `gif_dma_kick_analyzer.cpp:324-326` | Scan aborts on mid-pattern labels only after ≥1 store matched (`matched>0`); setup-phase labels (incl. every-address labels under indirect fallback) simulate past the jump-in point | Plan setup crossing a label, then runtime jump-in |
| F15a | R2 `config_manager.cpp:95-122` | Patch rows missing addr/value, or non-string/int addr/value, silently skipped (no count) | Malformed `[[patches.instructions]]` row |
| F15b | R2 `config_manager.cpp:115-121` | Duplicate patch addresses: **last-wins**, no warning (cf. reloc-dedup which warns) | Two patch rows, same address |
| F15c | R2 `config_manager.cpp:134-143` | MMIO value of non-string/int TOML type → address **0** recorded silently | `[mmio]` value of bool/float/array type |
| F15d | R2 `config_manager.cpp:156-158,187-189,197-201,233-237,241` | Jump-table rows: non-table node / addr-0 / no entries / non-table entry / entry-without-target silently skipped (no counts); `fallbackIndex` renumbering silent | Malformed `[[jump_tables.table]]` rows |
| F15e | R2 `config_manager.cpp:101,105,134,138,142,168,172,181,205,222` + R1 `:1009-1010` + R4 `:1943` | `std::stoul` (64-bit) → `uint32_t` **narrowing without range check** (patch addr, MMIO key/value, jt addr/base/index/target, CSV start/end, patch apply) | Any configured value > 0xFFFFFFFF or negative |
| F16a | R1 `elf_parser.cpp:570,577,583,593,608,614,620,733,738,1242` | Symbol-table path drops (non-function/imported, auto-not-in-map, non-executable, clamped-invalid, empty-name) are **uncounted and unwarned** — asymmetric with the CSV path, which counts + warns (`skippedNonExecutable/skippedInvalidRange`) | Stripped-ELF Resort: any ELF *with* a symtab |
| F16b | R1 `elf_parser.cpp:59,65-66,80-86` | Segments with vaddr/file/mem >32 bits silently pruned (no warning); `offset` narrowed **unchecked** (unlike the guarded fields); BSS `vaddr+fileSize` wraps silently | 64-bit ELF |
| F16c | R1 `elf_parser.cpp:1319-1324,1325-1341` | Reloc `offset`/`addend` 64→32 narrowing; `info` keeps `type&0xFF` only; unresolvable symbol index → empty name, no warning | ELF with relocations |
| F16d | R4 `ps2_recompiler.cpp:900-903` | Relocations with empty `symbolName` skipped **without warning** | Anonymous/failed reloc symbols |
| F17 | R3 `r5900_decoder.cpp:591,641,712,775,979` | Unknown MMI0/1/2/3 sub-op → silent `break` (no `cerr`, unlike REGIMM/MMI siblings); PMFHL-unknown → `0xFF` sentinel | Novel MMI sub-encodings |
| F18a | A5 `analysis_passes.cpp:240-243,272-275` + `tryBuildTable` reject + `:191-204` unreadable-entry `continue` | Jump-table candidates silently discarded (numEntries 0/≥1000, baseAddr 0, <2 valid targets, unreadable words); no candidate/discard counts anywhere | Any `SLTIU+BNE/BEQ … LW/LD … JR` shape in code |
| F18b | A5 `analysis_passes.cpp:160-165,277-281` | `LD`-table second-word read failure silently falls back to w0 (width confusion); stride-8→stride-4 retry silently reinterprets pairs | `LD`-loaded jump tables |
| F19a | A3 `sce_symbol_scanner.cpp:726-729,737-740` | Candidates rejected for staticBits<256 or ambiguous identity **without count/log** (no candidate census at all) | Weak/aliased SDK fingerprints |
| F19b | A3 `sce_symbol_scanner.cpp:479-483` | Match size silently **grown** over trailing zero words (`actualSize` > DB size; only the overflow half has a P1w drop) | SDK function followed by zero padding |
| F19c | A3 `sce_symbol_scanner.cpp:695-698` | Out-of-range reloc entries silently skipped during hash masking (→ hash mismatch → missed match) | DB reloc past symbol end |
| F20a | A5 `analysis_passes.cpp:63-72` | Self-modifying signal uses a **LUI-only** ≤5 scanback (ignores ORI/ADDIU low half — the exact P1g bug class; P1h notes it deferred) | Store with LUI+low-half base into `.text` |
| F20b | A5 `analysis_passes.cpp:13-27` | HW-I/O signal checks LUI-upper only (misses low half; scratchpad range folded in) | MMIO access via LUI+ORI |
| F21a | R4 `ps2_recompiler.cpp:237-273` | Unparseable `@addr` selectors silently become never-matching **bare names** (backward-compat); bare names from `name@addr` match **globally** (any same-named function, any address) | Typo'd selector address; duplicate real names |
| F21b | R4 `ps2_recompiler.cpp:756-767` | Skip selectors: same inert-when-unmatched shape as F3 | Unmatched `skip` entries |
| F22 | R1 `elf_parser.cpp:100-106,136-143,1159-1163` + R4/R1 `section.address+section.size` adds (`FindSectionByAddress`, `isValidAddress`, extract-final-loop, JAL `secEnd`) | ELF64→u32 field narrowings + **unguarded 32-bit** `address+size` adds (cf. `ClampFunctionEndToSection`, which guards via 64-bit) | Sections near 4 GiB |
| F23 | R7 `instruction_translator.cpp:37` (`memoryValueType` default) | Unknown width → empty type string (would emit broken C++) | `genFastWrite` with width ∉ {8,16,32,64} |
| F24 | R19 `function_table_emitter.cpp:62-63` | Functions in the none-state (¬recompiled ∧ ¬stub ∧ ¬skipped) silently omitted from registration | Post-loop residue (none observed) |
| F25 | A6 `toml_generator.cpp:63-69,213-226` | `functionNameCounts` computed, never read (dead); `escapeBackslashes` escapes backslash only (a `"`/control in a name breaks TOML) | Adversarial/odd symbol names |
| F26 | R4 `ps2_recompiler.cpp:2080-2089` | `.ctors/.init_array` targets `0`/`0xFFFFFFFF` + unreadable sections silently filtered (no count) | Initializer tables |
| F27 | R3 `r5900_decoder.cpp:1029-1065` (`getBranchTarget`/`getJumpTarget`) | Dead code (0 callers); verified correct regardless (`simmediate`-based, sign-safe) | — (kept for the record) |

### C. By-design ignores (exclusion-rule proposals, not drops)

| ID | Site | Discard (by design) | Trigger |
|---|---|---|---|
| X1 | R8 `:49-50`, R7 `:342-345` | SYNC/CACHE/PREF → comment only | Barrier/hint instructions |
| X2 | R10 `:83,95,109,113`, R14 `:72-74,84-86`, R11 `:42` | Writes to read-only/zero control regs ignored (MTC0 RANDOM/BADVADDR/PRID/BADPADDR; CTC2 VI0/MAC/TPC/VPU_STAT; CTC1 non-31) | Control writes without architectural effect |
| X3 | A6 `:141-151`, A5-print sites, R4-test-lane | `untracked_stubs` (informational), HW/MMI/SMC prints, entry discovery/reslice statics | Informational/test-only paths |

### D. Reviewed-clean (no finding; recorded so the audit is total)

`emitUnhandledInstruction` (R20 `:282-290`: reporter error + runtime
`throw`) backs every translator `default` (R7/R8/R9/R10-CO/R11-S/W/R12/R13/R14-CO/S1/S2);
decoder REGIMM/MMI `cerr` lines; `control_flow_analyzer` JR windows
funnel to the **loud** indirect-fallback promotion (reporter warning +
counters); `ConstantRegisterState` models `$0` exactly
(`gif_dma_kick_analyzer.h:20-30`, `:82-114`); all `SET_GPR_*` guard reg
0 (`ps2_runtime_macros.h:764-802`); decoder branch/load/store flags
come from Rabbitizer, not hand tables; `tryParseU32AddressLiteral`
(R4 `:206-229`) range-checks (the pattern §P13-4 reuses);
`output_worker_threads` clamp warns (R2 `:53-61`, the model warning);
`shouldApplyConfiguredPatch` default is exhaustive;
`escapeCStringLiteral` passthrough is correct;
`collectFunctionSelectors` dup-name sharing is coherent;
`findRecursiveFunctions` is pure Tarjan; `parseRelocationType` unknown
arm is unreachable with the embedded DB (vocabulary receipt §P13-3);
`isFunction` filter never fires with the embedded DB (all 9201
`FUNCTION`); BGEZAL/BLTZAL link writes are emitted (R6 `:468-477`);
JAL/JALR links emitted (R6 `:322-339`, R4-J-type flags set);
`sanitizeFunctionName` empty→`func` + reserved-word guard are total.

## P13-3. Reachability

Code universe: 833,638 words in 9,274 CSV functions
(`receipts/code_fields.txt`); output universe: 9,097 current files in
`$W/P1/output` (22:46 regen) + 177 stubs = 9,274 = CSV rows − 1 dup
(`receipts/range_check.txt`, `receipts/jal_replica.txt`).
`[drop]` baseline in boots unchanged (6 lines in `boot-p1ac-1/2.log`).

| ID | Reachability | Receipt |
|---|---|---|
| F1 | **Reached 1×** (static; runtime unknown) | `sub_00141728` JR @`0x14187c`; emitted file has **zero** delay-slot code for it (tail receipt §P13-6/9); real word `0x27bd0130` (`ADDIU $sp,$sp,+0x130`) compiles instead as `sub_00141880` head; no JAL to either (JAL-target grep: NONE); boot-log pcs: 0 hits (sampled diags) |
| F2 | **Reached 347×** (316 emitted + 31 stubbed) | Exact replica: 46,308 JAL words → 8,143 starts ⊆ CSV starts (0 pruned); predicted 347 = observed 316 + 31 stubbed-no-file, **316/316 exact** (`receipts/jal_replica.txt`); 315 adjacent overlaps (`receipts/range_check.txt`); 0 shrunk; `output-p11` reproduces the same ranges |
| F3 | **Reached 4×** | 181 stub selectors → 177 matched by start; 4 unmatched (`_sceSifCmdIntrHdlr@0x426230`, `sceSifLoadIopHeap@0x42AD28`, `sceSifLoadFileReset@0x42B1F8`, `InitTLB@0x42CD58`), each mid-function inside a recompiled owner (containment grep §P13-6/11) |
| F4 | **Reached statically** 4,205 sites; value-hit unknown | BLEZ/BGTZ(+L) 2,179 + REGIMM branches 2,026 in code ranges (`receipts/code_fields.txt`); no runtime value profile exists (read-only box) |
| F5a/b/c | **Reached** 66 / 4 / 1+1 | Output marker census (`receipts/output_markers.txt`); CTC2 sites both in `sub_003FE828` (:506 MAC, :536 VI0) |
| F6 | **Reached 1×** (name half; same end) | `0x42c1f0`: `InitSystemCallTableAddress_0x42c1f0` + `sub_0042C1F0`, same end `0x42c2f0`; winner = real name |
| F7 | **Reached 1×** (dead file) | `sub_0042C1F0_0x42c1f0.cpp` mtime Sep 18 (stale) vs current `Init…` file; register refs only the current name (1 ref); 0 markers in stale file |
| F8 | **Reached 1×** (analyzer side, same dup) | Same `0x42c1f0` input; analyzer `importGhidraMap` update-or-create converges to one row (name = last = `sub_…`); benign |
| F9 | **Unreachable** (SSX3) | Code census: MFC0 rd ∈ {8,9,12,13,14,23,28} ⊂ known; MTC0 rd ∈ {6,12,14} ⊂ known; CO fn ∈ {24 ERET, 56 EI, 57 DI} ⊂ known; 0 `Unimplemented COP0/MTC0` in output |
| F10 | **Unreachable** | 0 `CFC1` in code ranges; 1 `CTC1` (fs=31, handled); 0 FCR markers in output |
| F11 | **Unreachable** (unknown arms) | CFC2 rd: {0..18,20,21,22,26,28,29} all handled (incl. 275× Q22); CTC2 rd ⊇ {0:1, 17:1} (F5c) and no {19,23,24,25,30}; 0 `Unimplemented CFC2/CTC2` in output |
| F12a/b/c/d | **Unreachable** | REGIMM rt ∈ {0,1,2,3,24 MTSAB,25 MTSAH} ⊂ handled; BC0 count 0 in code (19 raw hits were data pollution); COP1-BC rt ∈ {0..3} (4,724, 0 invalid); COP2-BC absent; **0** `= (false)` in output |
| F13 | **Unreachable** (no tables) | 0 `[[jump_tables.table]]` in TOML; 0 `Unknown jump table target` in output |
| F14 | **Armed, unmatched** | 18,434 unlisted-memop sites present (LDL/LDR 4,527×2, SDL/SDR 4,462×2, LWL/LWR/SWL/SWR ~109–119; LL/SC/LDC1/LWC2/SDC1/SWC2 = 0); **0** `kickGifDmaChainFromMMIO` in output → plan body never runs |
| F15 | **Unreachable** (SSX3 TOML) | TOML has only `[general]/[mmio]/[performance]` (no `[data]/[patches]/[jump_tables]`); MMIO 273/273 parse (max `0x1000f520`); stubs 181 + skip 0 all well-formed |
| F16 | **Unreachable** (SSX3 ELF) | `symtab_sections=0 reloc_sections=0` (`receipts/elf_sections.txt`); 32-bit LE ELF; max section end ≪ 4 GiB |
| F17 | **Unreached** (0 downstream errors) | 0 `Unknown MMI*` in `recomp-p1l/p1h/p1w-tracked.log`; recomp errors 0; MMI pairs all in handled groups (`receipts/code_mmi_pairs.txt`) |
| F18 | **Unknown** (uncountable by construction) | 0 tables in TOML + 0 switches in output, but the detector logs no candidate/discard counts — "no candidates" vs "all discarded" indistinguishable |
| F19a/b/c | **Unknown** (uncountable) | Scanner matched ≥181 (stubs list) + 13 CSV names; no candidate/reject/growth log exists |
| F19-parse | **Unreachable** (embedded DB) | DB vocabulary = {FUNCTION, MIPS_26, MIPS_GPREL16, MIPS_HI16, MIPS_LO16, MIPS_LITERAL} ⊂ known (81,779 tags); override-DB dir could still inject novel types |
| F20a | **Unreached both ways** | 64,530 stores: 678 with LUI≤5 (259 with writers), **0** code-targets LUI-only *or* full (`receipts/smc_sweep.txt`); consequence is print-only anyway |
| F20b | **Latent, print-only** | Same LUI-only shape; consequence print-only (`elf_analyzer.cpp:1728-1736`) |
| F21a/b | **Unreachable** | skip=[]; 0 unparseable selectors (all 181 parse); 0 dup reliable names (`receipts/csv_dup_names.txt`) → global-name half inert (matching observed via starts: 177/177) |
| F22 | **Unreachable** | 32-bit ELF; `.text` ends ≈ `0x4xxxxxx`; no section near wrap |
| F23 | **Unreachable** (proven) | `genRead/genWrite` call widths ∈ {8,16,32,64,128} only (16 call sites grepped) |
| F24 | **Unreachable** (proven by case split) | Every process-loop path sets exactly one state; manual initializers flow through the same loop; entry-lane test-only |
| F25 | **Latent** (dead code / odd names) | Dead store confirmed by grep (3 refs, all writes); no `"`/controls in 9,275 names |
| F26 | **Unreachable** | No `.ctors/.init_array/.preinit_array` sections (`receipts/elf_sections.txt`) |
| F27 | Dead, correct | 0 callers repo-wide (decl + def only) |
| X1/X2/X3 | By design (counts for the record) | SYNC 66 / CACHE 4 / PREF 0; MTC0-readonly 0 / CTC1-non31 0 / CTC2-VI0+MAC 1+1; untracked 391; 0 `entry_*` files |

MMIO opcode note (rules out F-adjacent fears): all 273 TOML MMIO
pcs are LW (134) / SW (139) — LB/SB/LH/SH/LQ/SQ detector arms never
fired, and LWL/LWR+MMIO interaction is impossible by construction
(detector never marks them). PREF-ignored: 0 in code. MTC0-readonly:
0. `throw std::runtime_error`: 0 in output (no unhandled escaped).
`Errorfunc_`: 0. CSV health: 0 empty ranges, 0 malformed rows
(`csv` module reads all 9,275).

## P13-4. Patch spec (ranked by reachability × silence-severity)

Conventions (P1w, `ps2_log.h:126-154`): analyzer/recomp-time
instruments use `ps2_log::emitDropTo(std::cout, site, reason, args)`
(stdout = the analyzer/import channel captured by `tee`); runtime
guards use `ps2_log::emitDrop(site, reason, args)` (`cerr`, default
ON, `PS2X_DROP_SILENCE` kill-switch, fresh `getenv` per call). Site
namespace: `recomp/<area>` for the recomp side (new; P1w used
`analyzer/…` for the 5 analyzer sites — keep that prefix for A-file
sites).

| Rank | ID | Exact line to add (site + reason + args) | Anchor + args in scope |
|---|---|---|---|
| 1 | F1 | `ps2_log::emitDropTo(std::cout, "recomp/emit", "synthetic-delay-slot", dropArgs);` with `snprintf(dropArgs,…,"func=%s pc=0x%x nextpc=0x%x", function.name.c_str(), inst.address, inst.address+4)` | R17 `:135-139` (the `else` that builds `syntheticDelaySlot`); extend `CodeGenerator` with a section-word read if `raw=` is wanted (sections are already on `m_gen`) |
| 2 | F2a | `…("recomp/csv-merge", "end-extended", "func=%s start=0x%x csvend=0x%x newend=0x%x src=jal-fallback")` | R1 `:720-723` (`existing.end = newFunction.end` max-wins arm) + `:1089-1110` (sort/unique keep-largest: log loser `name/end`) |
| 3 | F2b | `…("recomp/csv-merge", "jal-row-pruned", "count=%d")` (one summary + keep the existing per-row silence) | R1 `:1066-1072` (`remove_if`): count erasures, emit one line |
| 4 | F3 | `m_reporter.warning("config", "stub selector '<sel>' matched 0 functions")` **and** `…("recomp/stub-selector", "unmatched", "sel=%s")` | R4 after `:793` (post-install coverage pass over `m_functions`); same loop covers F21b `skip` (`"recomp/skip-selector"`) |
| 5 | F9/F10/F11 | Replace each comment-only unknown arm with `return m_codeGenerator.emitUnhandledInstruction(inst, msg);` (5 arms: R10 `:74,124`; R11 `:36,42`; R14 `:62,101` — F11a's stale-GPR arm first) | Translators already include the reporter path; 0 SSX3 hits → no output diff |
| 6 | F12 | `…("recomp/branch-cond", "fold-false", "func=%s pc=0x%x op=0x%x rt=%u")` at both `return "false"` sites (R6 `:426,447`); add the missing `OPCODE_COP0` case (BC0F/T/FL/TL + likely-bit) mirroring COP1 | R6 `:391-450`; 0 SSX3 hits → no output diff |
| 7 | F4 | Runtime guard (emitted alongside each S32 condition): `if ((int64_t)GPR_S64(ctx,N)!=(int64_t)(int32_t)GPR_S32(ctx,N)) ps2_log::emitDrop("recomp/branch-narrow","blez-s32-narrow","pc=0x%x");` — measurement only; probable follow-up fix is unconditional S64 widening (semantically exact) | R6 `:400-427`; recompiled TU needs `ps2_log.h` (already pulled by `PS2_FUNCTION_LOG_TRACKER`; otherwise add the include) |
| 8 | F13 | Emit a runtime drop in the default leg: `ss << "ps2_log::emitDrop(\"recomp/jump-table\",\"unknown-target\", …index…);"` before `return;` | R18 `:38-40`; needs `ps2_log.h` in emitted TU (same note as rank 7) |
| 9 | F14 | (a) extend `isDirectMemoryAccess` with LWL/LWR/LDL/LDR/LDC1/LWC2/SWL/SWR/SDL/SDR/SDC1/SWC2/LL/SC (fix, no drop — aborts are safe); (b) drop the `matched>0` gate so **any** mid-scan label aborts (fix); (c) `m_reporter` info + counter on plan match (visibility; 0 today) | R16 `:136-161`, `:324-326`, `:333-339` |
| 10 | F15 | Route every `continue`/fallthrough in the patch/MMIO/jump-table loaders through `m_reporter->warning("config",…)` + `("recomp/config", …)` drops (malformed-row / invalid-value / unknown-type / dup-addr-last-wins with both values); replace bare `std::stoul→u32` with `tryParseU32AddressLiteral`-style range checks (pattern exists, R4 `:206-229`) | R2 `:95-122,134-143,156-241`; mirrors P1w `analyzer/csv-load` drops |
| 11 | F16 | Mirror the CSV-path counters on the symbol path: `skippedNonExecutable/skippedInvalidRange`-style counts + `warning("elf",…)` at R1 `:583,593,614,620,738,1242`; warn on sym-OOB→empty-name (`:1325-1341`) and on R4 `:900-903` empty-reloc skip; range-check the `:59` prune + `:65-66,80-86,1319-1324` narrowings (drop on truncation) | R1/R4 as listed; 0 SSX3 hits |
| 12 | F18 | `("analyzer/jump-detect", …)` drops: `empty-window`/`num-entries-range` (with `n=`), `no-base` (with `pc=`), `table-rejected` (`valid=/total=`), `entry-unreadable` (`pc=`), `ld-width-fallback` (`pc=`) | A5 `:191-204,240-243,272-281,160-165` + a final `candidates=N tables=M` summary to stdout |
| 13 | F19 | `("analyzer/sce-scan", …)` drops: `low-static-bits` (`bits=`), `ambiguous-identity` (`n=`), `reloc-oob-skipped` (`off=`), `size-grown` (`addr= old= new=`) + a `candidates=/matches=` summary | A3 `:479-483,695-698,726-740` |
| 14 | F17 | `std::cerr << "Unknown MMI0/1/2/3 …"` mirroring the existing REGIMM/MMI lines (or the same `analyzer/` drops if decoder gains the header) | R3 `:591,641,712,775,979` |
| 15 | F6/F8 | Fold into ranks 2–3 (dedup loser log) + one `("analyzer/context-index","dup-start-last-wins","start=0x%x")` | R1 `:1089-1110`, A2 `:36-44` |
| 16 | F7 | Purge-or-warn: on `generateOutput`, delete `*.cpp` in the output dir not in the current rename set (or warn per orphan) | R4 `:1077-1090` (`m_functionRenames` is the live set) |
| 17 | F20 | Apply the P1h low-half fold to `hasSelfModifyingSignal` (same 5-line shape); prints stay prints (X3) | A5 `:63-72` |
| 18 | F22/F23/F24/F25/F26 | Range-check + `warning` (F22 narrowings), `assert` unreachable (F23/F24), delete-or-use (F25 counts), count initializer filters (F26) | As listed in §P13-2 |

Exclusion-rule updates (append to the P24 §P24-1g list of 12):

| # | Excluded path | Rule |
|---|---|---|
| 13 | `SYNC` barrier / `CACHE`+`PREF` hints → comment-only (R8 `:49-50`, R7 `:342-345`) | By-design ISA ignores on a single-threaded TSO host; counted here (66/4/0) |
| 14 | Control writes without architectural effect ignored (MTC0 RANDOM/BADVADDR/PRID/BADPADDR; CTC2 VI0/MAC/TPC/VPU_STAT; CTC1 non-31) | Read-only/zero-reg semantics; counted here (MTC0 0, CTC2 1+1, CTC1 0) |
| 15 | `untracked_stubs` list + HW/MMI/SMC heuristic prints (A6 `:141-151`, A5 via `elf_analyzer.cpp:1728-1752`) | Informational-only by design (volumes already on stdout) |
| 16 | Entry discovery/reslice public statics (R4 `:275-730` lane) | Test-only; unreachable in production regens (0 `entry_*` files in SSX3 output) |

Deferred implementation brief (sketch, for the applying brief):
files = the 14 anchors above (≈20 hunks: 2 emitter + 3 elf_parser +
2 recompiler + 1 control-flow + 5 translator-arm swaps + 2 analyzer +
1 config + 1 gif + 1 jump-emitter + 1 reporter-counter); proof =
tracked-TOML regen (expect: +1 `synthetic-delay-slot` line for
`sub_00141728`, +347 `end-extended` lines, +4 `unmatched` lines, +1
prune summary, +0 translator/branch/detector/scanner lines on SSX3) +
`ps2x_tests` green + 1 boot with the unchanged 6-line runtime census
(ranks 7–8 add no boot lines unless hit). Rank-7 guard is the only
emitted-code change on the hot path; keep it behind the existing
drop kill-switch semantics (default ON, exceptional by construction).

## P13-5. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted;
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp`,
`S=/Volumes/Extreme SSD/ps2x-p13`. All reads; the only writes are
`S` (scratch) and `local/research/P13/` (evidence).

```
# Step 0 (context; lease-free, read-only)
grep -n "P24-1f|P24-1g|Part 24|P15-2|emitDrop|exclusion" local/research/P1/REPORT.md
sed -n '7983,8252p' local/research/P1/REPORT.md            # Part 24 (census + 12 rules + boundary)
sed -n '3260,3345p' local/research/P1/REPORT.md            # P1g MMIO-fold shape
grep -n "emitDrop" $R/ps2xAnalyzer/src/elf_analyzer.cpp    # 5 P1w analyzer sites
sed -n '110,160p' $R/ps2xRuntime/include/ps2_log.h         # drop-helper contract
# Step 1 (inventory)
wc -l $R/ps2xAnalyzer/src/*.cpp $R/ps2xRecomp/src/lib/*.cpp; find $R/ps2xAnalyzer -type f
cat $R/ps2xAnalyzer/include/ps2recomp/{analysis_passes,elf_analysis_context,elf_analyzer,function_classifier,sce_symbol_scanner,toml_generator}.h
# Step 2 (audit sweeps; each followed by paged reads of the hits)
grep -rn "default:" $R/ps2xRecomp/src/lib/ $R/ps2xAnalyzer/src/ --include="*.cpp" | grep -v elf_analyzer.cpp
grep -rn "unhandled|Unknown|unsupported|TODO|FIXME|ignore|skip|fallback" $R/ps2xRecomp/src/lib/ $R/ps2xAnalyzer/src/ --include="*.cpp" | grep -v elf_analyzer.cpp
grep -n "continue;" $R/ps2xRecomp/src/lib/{ps2_recompiler,elf_parser}.cpp   # 50 + 32, read in batches
grep -n "m_reporter|reporter->" $R/ps2xRecomp/src/lib/*.cpp                  # loud-vs-silent partition
sed reads: translators (cop0/fpu/vu/mmi/special/regimm/instruction), control_flow_{analyzer,emitter},
  function_emitter, function_table_emitter, gif_dma_kick_analyzer, jump_table_switch_emitter,
  code_generator, config_manager, elf_parser (segments/clamp/merge/relocs/DWARF/JAL), ps2_recompiler
  (selectors/stubs/decode/emit/reslice/entry-lane), analysis_passes, function_classifier,
  sce_symbol_scanner (all 793 lines), toml_generator, elf_analysis_context, analyzer_main
grep -rn "DiscoverAdditionalEntryPoints|ResliceEntryFunctions" $R/ --include="*.cpp" --include="*.h"  # test-only proof
grep -rn "getBranchTarget|getJumpTarget" $R/ps2xRecomp/ $R/ps2xAnalyzer/     # dead-code proof
# Step 3 (reachability; scripts in receipts/)
mkdir -p "$S" local/research/P13
python3 $S/p13_elf_sweep.py  $W/P1/SLUS_207.72 $W/P1/ssx3-functions.sweep.csv         $S/elf    # raw (data-polluted; superseded)
python3 $S/p13_elf_sweep2.py $W/P1/SLUS_207.72 $W/P1/ssx3-functions.sweep.csv         $S/code   # code-only fields
python3 $S/p13_smc_sweep.py                                                                # LUI-only SMC miss census
cd $W/P1/output && LC_ALL=C grep -roh -E "Unimplemented …|…ignored|…Unknown jump table target|kickGifDma…|throw …|Errorfunc_" . | sort | uniq -c   # markers
cd $W/P1/output && LC_ALL=C grep -rl "= (false)" . ; LC_ALL=C grep -roh "MMIO: 0x[0-9a-fA-F]*" . | sort | uniq -c   # folds + MMIO
cd $W/P1/output && LC_ALL=C grep -rh "^// Address: 0x" . | sort > $S/output_ranges.txt   # 9,097 ranges
python3 $S/p13_range_check.py $W/P1/SLUS_207.72 $R/games/ssx3/ssx3-functions.sweep.csv $S/output_ranges.txt > $S/range_check.txt
python3 $S/p13_jal_replica.py > $S/jal_replica.txt                                      # 316/316 mechanism proof
tail $W/P1/output/sub_00141728_0x14a130.cpp files; grep boot-p1*.log for pcs + [drop]  # F1 + baseline
stat -f "%Sm %N" $W/P1/output/*42c1f0* ; find $W/P1/output -type f ! -newermt "2026-09-19 22:45"  # stale-file proof
LC_ALL=C grep -o '"type": "[A-Z_0-9]*"' $R/ps2xAnalyzer/include/ps2recomp/sce_symbol_database_data.h | sort | uniq -c  # DB vocab
python one-liners: stub-selector coverage (181→177+4), MMIO opcodes (LW/SW only), CSV health (0/0),
  COP1-BC rt (all valid), JAL-to-0x141728/0x141880 (NONE), config maxima, TOML sections, dup names (0)
# Step 4 (evidence + commit; NO push)
cp $S/{output_markers,output_ranges,range_check,jal_replica,smc_sweep}.txt $S/code/{code_fields,code_mmi_pairs,func_end_detail}.txt \
   $S/elf/{elf_sections,csv_dup_names}.txt $S/p13_*.py local/research/P13/receipts/
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P13/REPORT.md local/research/P13/receipts/
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P13] ..." -m "Orchestrated-By: Muse Code"   # NO push
```

## P13-6. Receipt paths

| # | Claim | Receipt |
|---|---|---|
| 1 | Drop-helper contract + P1w analyzer sites | `ps2_log.h:126-154`; `elf_analyzer.cpp:169,1570,1663,1869,1887` (live reads) |
| 2 | Code-only field census (833,638 words) | `receipts/code_fields.txt`, `receipts/code_mmi_pairs.txt` |
| 3 | Output marker census (66/4/1+1/0s) | `receipts/output_markers.txt` (+ §P13-3 table for the 0-counts) |
| 4 | Output ranges (9,097) + match/ext/shrink + 315 overlaps + 1 end-branch | `receipts/output_ranges.txt`, `receipts/range_check.txt` |
| 5 | JAL-merge mechanism (316/316 exact, 31 stubbed) | `receipts/jal_replica.txt` + replica script |
| 6 | 8 CSV end-branch functions + 8 next-words | `receipts/func_end_detail.txt` |
| 7 | SMC LUI-only miss census (0/0 over 64,530 stores) | `receipts/smc_sweep.txt` |
| 8 | ELF sections (no symtab/relocs/debug/ctors) | `receipts/elf_sections.txt` |
| 9 | F1 emission (no delay code) vs healed sibling (delay code present) | `$W/P1/output/sub_00141728_0x14a130.cpp` tails (quoted §P13-3/F1 row); `sub_00141880` head |
| 10 | Stale-file proof (mtime + register refs + 1-file find) | Command outputs §P13-5 (Sep 18 vs Sep 19 22:46; 1 ref; find count 1) |
| 11 | 4 unmatched stub selectors + mid-function containment | Command outputs §P13-5 (181→177+4; owners table) |
| 12 | DB vocabulary ⊂ known (81,779 tags) | Command output §P13-5 (6 distinct values) |
| 13 | Boot `[drop]` baseline holds (6+6) | `boot-p1ac-1.log`, `boot-p1ac-2.log` grep counts |
| 14 | All sweeps re-runnable | `receipts/p13_*.py` (5 scripts, stdlib only) |

## P13-7. What I could not do

- Implement anything (read-only brief; P1ad owns the in-flight fix lane).
- Boot, lease, or build (forbidden); hence no runtime value profile for
  F4 (S32 narrowing needs a value census — rank 7's guard-drop is the
  measuring instrument), no dynamic hit-counts for F1/F5 sites (boot
  logs sample pcs; 0 hits is absence-of-evidence, not evidence-of-absence),
  and no post-P1w analyzer stdout (F18/F19 discards stay uncountable
  until the rank 12–13 drops land).
- Regenerate from a controlled TOML (would need a fresh `ps2_recomp`
  build; `$W/P1/bin/ps2_recomp` is Sep 18, stale vs HEAD) — the F2
  mechanism is instead proven by exact input-output replica (316/316).
- Exhaustively audit handled-case arithmetic inside `vu_translation_helpers`
  (886 lines) / `mmi_translation_helpers` (608 lines): defaults are
  loud (`emitUnhandled`, 0 hits), but per-case SIMD semantics were
  spot-checked, not proven.
- Attribute the 31 stubbed-extended functions' stub ranges beyond
  start-matching (register/dispatch containment is runtime-side, out of
  the analyzer brief).
- Time box respected: single session, no overrun.


