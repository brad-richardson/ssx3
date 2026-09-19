# P5 REPORT — 360/N64/PSP recomp tooling for the PS2 ladder + ps2xGS (read-only research)

Runbook: `local/muse/prompts/P5.md` + orchestrator redirect (Q6 xboxrecomp).
Tables, no verdicts (license column re-cites P3 §8.3, plus the Q6 LICENSE read).
Read first (per runbook): P3 §8.3–§8.4 (sibling licenses + N64ModernRuntime
message-not-nesting, NOT redone), P4 §4 (EeScheduler delivery point:
`queueInvocation` enqueue, `run()` Sites A/B dequeue, `invokeCurrent*` negative),
ps2xGS plan `docs/plan-gs-gpu-backend-2026-09-18.md` §5/S0–S8 (Q3/Q6c only).
No builds, no boots, no emulator runs, no leases, no `adb`, no clone edits,
no edits to `tools/`/`native/`/`vendor`/other evidence dirs. No `git push`.
Every `file:line` below is a path I opened; `grep`/`find`/`diff` only located.
Revs are full SHAs from `git rev-parse HEAD` (short forms match P3 §8.1).

Our-side anchors cited in mappings (all read-only): our fork
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`
`ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp` (numeric-switch dispatch,
`default: return false` at :405-406, P1c diag histogram :1-80),
`ps2xRecomp/src/lib/control_flow_emitter.cpp:256-271`
(`PS2X_STRICT_RETURN_DIAGNOSTICS` JR-$ra dispatch),
`ps2xRecomp/tools/ghidra/ExportPS2Functions.java:626-717`
(`[general].stubs` / `untracked_stubs` TOML emission),
`ps2xTest/src/elf_analyzer_tests.cpp:141-186` (hand-built `Instruction` vectors);
P1 REPORT `codeptr_sweep.py` + `ssx3-functions.csv` + 39-entry constructor table
(P3-4), alarm-callback split Fix 1 (`0x3E3588`), comparator leaf `0x3e3968`.

## 1. Q1 — Kernel-export HLE tooling (60 min cap)

### 1a. XenonRecomp `ddd128b` — 360 kernel imports by ordinal

Repo is recompiler-only (dirs `XenonAnalyse/ XenonRecomp/ XenonTests/ XenonUtils/`;
no runtime dir). The "stub table" is generated at recompile time and resolved
at link time via weak symbols.

| Aspect | File:line (opened) | Mechanism (quoted) |
|---|---|---|
| Generator: ordinal→name maps | `XenonUtils/xex.cpp:12`, `:117-125` | `#define XE_EXPORT(MODULE, ORDINAL, NAME, TYPE) { (ORDINAL), "__imp__" STRINGIFY(NAME) }`; `XamExports` / `XboxKernelExports` unordered_maps built from `#include "xbox/xam_table.inc"` / `"xbox/xboxkrnl_table.inc"` |
| Generator: export tables | `XenonUtils/xbox/xboxkrnl_table.inc` (922 `XE_EXPORT` rows), `xbox/xam_table.inc` (1735 rows) | `XE_EXPORT(xboxkrnl, 0x0000000D, ExCreateThread, kFunction),` header notes Xenia derivation (BSD) |
| Generator: import parse | `XenonUtils/xex.cpp:296-347` | walks XEX import libraries; `xam.xex`→XamExports, `xboxkrnl.exe`→XboxKernelExports (:318-325); hit inserts `image.symbols.insert({ name->second, descriptors[im].firstThunk, sizeof(thunk), Symbol_Function })` (:336-340); thunk bytes overwritten with `{ 0x00000060×3, 0x2000804E }` (:335, :342) |
| Emission: stub symbols | `XenonRecomp/recompiler.cpp:2388`, `:2384-2386`, `:2448-2452` | every function emitted as `PPC_FUNC_IMPL(__imp__NAME)`; weak alias or weak wrapper `PPC_WEAK_FUNC(NAME) { __imp__NAME(ctx, base); }` so HLE implementations override at link |
| Emission: shared decl + mapping | `XenonRecomp/recompiler.cpp:2586-2602` | `ppc_recomp_shared.h` gets `PPC_EXTERN_FUNC(name)` per symbol; `ppc_func_mapping.cpp` gets `PPCFuncMapping PPCFuncMappings[] = { { 0xADDR, name }, …, { 0, nullptr } };` |
| Unknown ordinal / unknown branch target | `XenonUtils/xex.cpp:336-340` (find-fail inserts nothing); `XenonRecomp/recompiler.cpp:400-403` | call to address with no symbol emits only `// ERROR {address}` — NO call, NO trap, falls through |
| Runtime tracer | ABSENT | no runtime in repo; no `NOT_IMPLEMENTED`/trace/log facility anywhere in `XenonRecomp/` |
| Coverage tracking | ABSENT | nearest: stdout diagnostics `Unable to decode instruction` (:2422), `Unrecognized instruction` (:2432), `Found a switch jump table … with no switch table entry present` (:2427-2428), `Recompiling functions... {}%` (:2614) |

PS2Recomp analogue (function-level prose, NOT applied): in the recompiler,
resolve each imported EE-side stub address to a `__imp__<name>`-style symbol at
emit time and emit a weak default per symbol that routes to
`dispatchNumericSyscall`, so a later real implementation overrides by link
instead of by editing the switch; emit alongside an address→name mapping table
serving the role of `PPCFuncMappings` for the dispatcher's strict-return and
missing-target diagnostics. The `// ERROR` fall-through is the anti-pattern to
avoid: our `default: return false` already reports better.

### 1b. psprecomp `caca759` — NID imports

| Aspect | File:line (opened) | Mechanism (quoted) |
|---|---|---|
| Generator: census | `tools/allegrexrecomp/main.c:574-649` (`funcs` subcommand) | `psp_collect_imports` (:612-615) → `imports: %d distinct firmware calls` (:603) + `firmware libraries needed (%d functions across %d libraries)` per-lib counts (:630-633); `--list` prints `lib NID thunk` rows (:636-641). Header comment (:605-607): `This is the HLE work list: everything here has to exist before the game runs, and nothing outside it does.` |
| Generator: collector API | `tools/allegrexrecomp/container.h:216-223` | `psp_import_entry { uint32_t addr; /* thunk in .sceStub.text */ uint32_t nid; char lib[32]; }`; `psp_collect_imports(data, len, mi, load_bias, out, max)` two-call count-then-fill |
| Generator: stub emission | `tools/allegrexrecomp/emit.c:893-930` (`emit_imports` → `<prefix>_imports.c`) | per import: `/* lib :: NID */ void psp_import_%08X(void) { PSP_ENTER(addr); psp_hle_call(NID); }` (:913-919); thunk called but absent from import table → `psp_unimplemented(addr, "unlisted import")` trap (:921-927: `guessing a NID would route it to the wrong function`) |
| Runtime tracer: unimplemented NID | `src/hle/hle.c:105-127` (`psp_hle_call`) | miss prints `psprecomp: unimplemented firmware call 0x%08X` to stderr and `psp_ret(0)`; comment (:121-124): `Returning 0 rather than aborting is deliberate … One that genuinely needed the result will fail visibly soon after, with this line already in the log.` |
| Runtime tracer: zero-history | `src/hle/hle.c:71-103` | last-16 firmware calls returning 0 (`note_zero` on every `:111` hit incl. misses at `:115`); `psp_hle_dump_recent` prints newest-first with the documented `SCE_KERNEL_ERROR_OK is also zero` ambiguity caveat (:87-95) |
| Runtime tracer: entry trace | `tools/allegrexrecomp/emit.c:839-850`; `include/psprecomp/dispatch.h:44-69` | `-DPSPRECOMP_TRACE` maps `PSP_ENTER(a)`→`psp_trace_enter(a)` else no-op (`one store per call when on, and nothing at all when off`); API: enter/dump/reset/last/watch/loop/mark/sp-checks; `psp_hle_init` registers miss context printing trace + recent-zeros (`hle.c:141-144`) |
| Coverage: registry API | `include/psprecomp/hle.h:43-55` | `psp_hle_name/count/entries`: `Every registered entry, for the coverage report a game repo wants: which of a module's imports actually exist yet.` |
| Coverage: self-verification | `tests/test_hle.c:83-104`; `tools/allegrexrecomp/crypto/sha1.c:69-74` | `test_nids_match_names` recomputes `psp_nid(name)` = SHA-1(name)[0:4] LE for every named entry; unnamed entries skipped `by construction` (`if (!e[i].name) { unnamed++; continue; }`) |
| Override policy | `src/hle/hle.c:16-28`, `:42-44` | re-registering a NID replaces (`a game repo can override one function without forking the table`); `psp_hle_register_unnamed` for observed-but-unidentified NIDs (`invent a name … produces a table which runs, looks right, and lies`) |

PS2Recomp analogue (function-level prose, NOT applied): add an analyzer-side
`funcs`-equivalent that prints the distinct syscall/stub surface per ELF before
any run (the HLE work list); give `Dispatcher.cpp`'s `default:` arm the
psp_hle_call shape (stderr line with number + named-when-known + deliberate
return value); keep a bounded recent-miss/zero-return ring alongside the P1c
histogram for the `wild pointer far from cause` class; add a table self-test
recomputing every registered number↔name pair from one source of truth; allow
title repos to replace one stub by re-registration instead of fork edits.

### 1c. wtf-psp-recomp `ebaeed4` — consumer, no own tooling

| Aspect | File:line (opened) | Mechanism |
|---|---|---|
| Generator / tracer / coverage | — (none local) | game repo; toolkit is git submodule `psprecomp/` (`README.md:152`), EMPTY locally (uninitialized — no bodies to read) |
| Consumption evidence | `README.md:140-146`; `docs/NOTES.md:165-172`, `:194-200`, `:202-216` | runs `info` / `funcs` / `emit` per module; records per-module tables (functions/reached/imports/indirect); shared-engine inference from identical import counts; Lumberjack layout with `import thunks (163 stubs)` |
| Status anchor | `README.md:55-62` | stage table to `13,682 dispatch entries … 109 firmware functions`; stall documented, tool-output-not-assertion policy |

PS2Recomp analogue: none beyond psprecomp rows — the borrowable item is the
*policy* (per-title import/coverage tables checked into the game repo as the
bring-up contract), applicable to our `ssx3-functions.csv` + sweep counts.

## 2. Q2 — Indirect-branch / function-detection tooling (60 min cap)

### 2a. N64Recomp `ffb39cd` — symbol-driven boundaries + recompile-time JR/JALR resolution

| Mechanism | File:line (opened) | Quoted body |
|---|---|---|
| Boundary: ELF symtab | `src/elf.cpp:99-110` | STT_FUNC/STT_NOTYPE/STT_OBJECT accepted; `uint32_t num_instructions = type == ELFIO::STT_FUNC ? size / 4 : 0;` — non-FUNC symbols get dummy zero-word entries `so that their symbol can be looked up for function calls` |
| Boundary: entrypoint special-case | `src/elf.cpp:118-125` | rom `0x1000` + zero size → `num_instructions = 0x50 / 4`, renamed `recomp_entrypoint` |
| Boundary: manual functions | `src/main.cpp:17-69` | `add_manual_functions` appends config-declared functions to context |
| Boundary: static-function synthesis | `src/recompilation.cpp:78-80`, `:313-317` (`CreateStatic`); `src/main.cpp:803-820` | JAL to in-section address with no exact symbol → `static_<sec>_<vram>` recorded in `static_funcs_out`; end = next known `function_addrs` entry or section end |
| JAL disambiguation | `src/recompilation.cpp:24-102` (`resolve_jal`) | same-section exact match wins immediately (:55-60); in-section-no-match → CreateStatic (:71-81); cross-section 0/1/N candidates → NoMatch/Match/Ambiguous (:84-98); `use_lookup_for_all_function_calls` forces Ambiguous (:26-28) |
| JALR by register | `src/recompilation.cpp:480-488`, `:252-260` | `jalr can only be handled with $ra as the return address register` else stderr error; emits `generator.emit_function_call_by_register(reg)` = runtime lookup, delay slot first |
| JR $ra | `src/recompilation.cpp:527-529` | `print_return_with_delay_slot()` |
| JR non-$ra + known jtbl | `src/recompilation.cpp:531-554` | match on `jtbl.jr_vram == instr_vram` → `emit_switch` + `emit_case(entry_index, L_<addr>)` per entry + `emit_switch_error` default |
| JR non-$ra, no jtbl (indirect tail call) | `src/recompilation.cpp:556-560` | `[Info] Indirect tail call in {}` + call-by-register + `emit_return`; analysis side warns `TODO stricter validation on tail calls, since not all indirect jumps can be treated as one` (`src/analysis.cpp:253`) |
| JAL ambiguous → lookup fallback | `src/recompilation.cpp:319-327` | `[Info] Ambiguous jal target … falling back to function lookup`, `call_by_lookup = true` |
| JAL no match (cross-section) | `src/recompilation.cpp:307-309` | hard error `No function found for jal target` — fail, unlike Xenon's `// ERROR` fall-through |
| Jump-table discovery: LUI base | `src/analysis.cpp:126-135` | `addu` with exactly one operand carrying valid LUI → copy LUI state to rd, record `prev_addend_reg`/`prev_addu_vram` |
| Jump-table discovery: LW load | `src/analysis.cpp:183-204` | `lw` with base = valid-LUI + valid-addend → `valid_loaded` with `loaded_address = prev_lui + lo16`; rejects double-lo16 (`nonzero_immediate && valid_addiu`) |
| Jump-table discovery: GOT variant | `src/analysis.cpp:106-124`, `:205-214`, `:284-297` | GOT-offset + addend → `valid_got_loaded`; absolute address fixed up after scan (`cur_jtbl.vram += section->ram_addr + got_word`) |
| Jump-table discovery: JR anchor | `src/analysis.cpp:222-252` | `jr` non-$ra with `valid_loaded`/`valid_got_loaded` source reg → `stats.jump_tables.emplace_back(...)`; `jr $ra` ignored |
| Jump-table sizing | `src/analysis.cpp:306-348` | sorted by vram; entries valid while inside `[func.vram, func.vram + words*4)`; next-table addr caps scan; zero entries → `Failed to determine size of jump table …` hard error. Caveat (:277): `A linear search through the func won't be accurate due to not taking control flow into account, but it'll work for finding jtables` |
| Stack spill tracking | `src/analysis.cpp:146-182` | `sw`/`lw` to `sp` copies RegState to/from `stack_states[]` so LUI state survives spills |
| Noreturn analysis | ABSENT | no `noreturn`/`no_return`/`does_not_return` match anywhere under `src/`; `syscall` treated as tail call + return (`recompilation.cpp:563-569`) |
| Unhandled out-of-function branch | `src/recompilation.cpp:521-524` | `Unhandled branch in {} at … to …` hard error; in-function `j` → goto (:498-500); `j` to known symbol → tail call (:513-520) |

### 2b. XenonRecomp `ddd128b` — pdata + BL-sweep + gap-fill Analyse + offline switch TOML

| Mechanism | File:line (opened) | Quoted body |
|---|---|---|
| Entry: config lists | `XenonRecomp/recompiler.cpp:171-175` (+ save/rest VMX :100-169) | `config.functions` address→size pairs emitted as `sub_<X>` symbols |
| Entry: .pdata unwind records | `XenonRecomp/recompiler.cpp:177-194` | `IMAGE_CE_RUNTIME_FUNCTION` array: `f.size = fn.FunctionLength * 4` unless symbol already known |
| Entry: BL-target sweep | `XenonRecomp/recompiler.cpp:206-221` | linear scan of code sections for `PPC_OP_B && PPC_BL`; in-section unknown target → `Function::Analyze` + `sub_<X>` symbol |
| Entry: gap-fill sweep | `XenonRecomp/recompiler.cpp:223-251` | second linear pass: skip known symbols, `Function::Analyze` every gap; final sort by base (:254) |
| Size: recursive-descent Analyse | `XenonAnalyse/function.cpp:41-211` | block-stack CFG walk from entry over `BC` (cond, :94-139), `B`/zero/`bctr`-family terminators (:140-205); `blr` ends block; unknown opcode pops block (:206-210) |
| Size: tail-call + back-branch rules | `XenonAnalyse/function.cpp:45-49`, `:154-159` | `0x04000048` second-word → 8-byte shifted-ptr tail call; `branchDest < base` → `Branches before base are just tail calls, no need to chase` |
| Size: truncation | `XenonAnalyse/function.cpp:213-245` | sort blocks, erase at first discontinuity; `fn.size = max(block.base + block.size)` |
| Noreturn analysis | ABSENT | no `noreturn`/`no_return`/`does_not_return` match anywhere in repo; `BLR` → bare `return;` (`recompiler.cpp:710-712`); `BLRL` → `__builtin_debugtrap()` (:714-716) |
| Jump tables: offline pattern scan | `XenonAnalyse/main.cpp:215-251` (`scanPattern`), `:253-306` | `SearchMask` over code sections for 4 opcode-id sequences (absolute/computed/byte-offset/short-offset `… MTCTR [BCTR]`); emits `[[switch]]` TOML (`base`/`r`/labels) |
| Jump tables: bound/default recovery | `XenonAnalyse/main.cpp:104-135` (`ScanTable`) | back-scan ≤32 insns for `BGT/BGTLR/BLE/BLELR` (default label) then `CMPLWI cr` (index reg + `labels.resize(count+1)`) |
| Jump tables: label resolution | `XenonAnalyse/main.cpp:24-102` (`ReadTable`) | per-type `lis`+`addi` pair reads (fixed offsets per idiom) + base/shift arithmetic |
| Jump tables: recompile use | `XenonRecomp/recompiler.cpp:609-635` | `BCTR` with TOML entry → C `switch (rN)` + `goto loc_<X>` per label; out-of-function label → `// ERROR` + stderr `trying to jump outside function` + `return;`; default → `__builtin_unreachable()` |
| Jump tables: missing-entry diag | `XenonRecomp/recompiler.cpp:2427-2428` | `Found a switch jump table at {:X} with no switch table entry present` (heuristic: BCTR preceded by `mtctr`-idiom words) |
| Indirect call/branch | `XenonRecomp/recompiler.cpp:636-648`, `:730-734`; `XenonUtils/ppc_context.h:110-113` | BCTR-without-table / BCTRL / BNECTR → `PPC_CALL_INDIRECT_FUNC(ctr)` = `(PPC_LOOKUP_FUNC(base, x))(ctx, base)`; lookup = pointer table at `base + IMAGE_BASE + IMAGE_SIZE + (addr - CODE_BASE)*2` |
| Function-end check | `XenonRecomp/recompiler.cpp:2441-2444` | present but `#if 0`-disabled: `Function at {:X} ends prematurely …` |

### 2c. Mapping onto our sweep CSV + strict-return diagnostics

Our misses (P1 REPORT): 39-entry constructor table (P3-4), alarm-callback split
Fix 1 (`0x3E3588`), comparator leaf `0x3e3968`; our tooling:
`codeptr_sweep.py` + `ssx3-functions.csv` + `PS2X_STRICT_RETURN_DIAGNOSTICS`
(`control_flow_emitter.cpp:256-271`).

| Their pass | Which of our misses it would have caught earlier |
|---|---|
| N64 `CreateStatic` (JAL to unknown in-section addr becomes a function) | alarm-callback split: any JAL/JR-target census that auto-creates entries would have surfaced `0x3E3588` as a function at sweep time instead of at strict-return time |
| Xenon BL-target sweep (`recompiler.cpp:206-221`) | same class: constructor-table entries reached only by indirect/BL patterns get `sub_<X>` entries before recompilation, not after a diagnostic fires |
| Xenon gap-fill `Function::Analyze` (:223-251) | comparator leaf `0x3e3968`: bytes between known symbols are analysed as code rather than left unclaimed; our sweep's unclaimed-range remainder is the equivalent hook |
| N64 jump-table size validation within function bounds (`analysis.cpp:333-337`) | constructor table: entries must land inside the owning function or the table ends — a check our CSV has no analogue of; size failure is a hard error, not a silent short table |
| Xenon missing-switch-entry diag (`recompiler.cpp:2427-2428`) | the direct analogue of our strict-return JR-$ra diagnostic, but firing at recompile time on the *idiom* (BCTR after mtctr) rather than at runtime on the address |
| N64 hard errors on `NoMatch` jal / unhandled branch vs Xenon `// ERROR` fall-through | policy choice: N64 fails the build on unknown call targets, Xenon emits a comment and falls through; our `default: return false` + histogram sits between — reported but non-fatal |
| Neither has noreturn analysis | no borrowable pass for the "call that never returns" class; both treat link-register returns as unconditional (`blr`→`return`, `jr $ra`→return) |

## 3. Q3 — UnleashedRecomp GPU path vs ps2xGS (60 min cap)

Headline: there is NO 360 command-stream capture/replay. The GPU path is
API-level HLE: fixed-address guest D3D9-style entry points are hooked,
translated to `RenderCommand` structs on the guest thread, and consumed on
a render thread that drives a D3D12/Vulkan abstraction. Shaders are
translated OFFLINE (XenosRecomp) into shipped SPIR-V/DXIL blobs.

### 3a. UnleashedRecomp `cf829a9` GPU path

| Aspect | File:line (opened) | Mechanism (quoted) |
|---|---|---|
| Capture point: fixed-address hooks | `UnleashedRecomp/gpu/video.cpp:7818-7844` | `GUEST_FUNCTION_HOOK(sub_82BE5900, DrawPrimitive);` / `sub_82BE5CF0 → DrawIndexedPrimitive` / `sub_82BE52F8 → DrawPrimitiveUP` / `sub_82BDA8C0 → Video::Present`, plus ~40 resource/state hooks (`CreateTexture`, `SetRenderTarget`, `Clear`, `SetVertexShader`…) and `GUEST_FUNCTION_STUB`s for no-op'd entries (e.g. `sub_82BDD370 // SetGammaRamp`) |
| Capture: guest-thread batching | `video.cpp:4280-4294` (`LocalRenderCommandQueue`), `:4611-4623` | stack queue of ≤20 `RenderCommand`s (`assert(count < std::size(commands))`); `DrawPrimitive` = `FlushRenderStateForMainThread(device, queue)` + one enqueue + `queue.submit()` → `g_renderQueue.enqueue_bulk(commands, count)` |
| Handoff: MPSC queue | `video.cpp:1006` | `static moodycamel::BlockingConcurrentQueue<RenderCommand> g_renderQueue;` |
| Replay/diff harness | ABSENT | no capture/replay/diff/golden facility under `gpu/` (grep `replay\|capture\|renderdoc\|golden` hits only pixel-shader names and an "inverse capture ratio" comment); `imgui/imgui_snapshot.h:1-30` is a font-atlas snapshot, not GPU capture; `cache/pipeline_state_cache.h` is a precomputed hash-keyed PSO table, not a trace |
| Translation: guest state structs | `UnleashedRecomp/gpu/video.h:34-66`, `:137-289` | size-asserted mirrors (`static_assert(sizeof(GuestDevice) == 0x5E00)`); `GuestTexture/Buffer/Surface/VertexDeclaration/Shader` carry host handles (`sourceSurface`, `shaderCacheEntry`) |
| Translation: render-thread dispatch | `video.cpp:5270-5298` | `switch` over `RenderCommandType` → `Proc*` per command; `default: assert(false && "Unrecognized render command type.")` |
| Translation: draw lowering | `video.cpp:4625-4650`, `:4668-4680` | `ProcDrawPrimitive`: `SetPrimitiveType` + instancing check + `FlushRenderStateForRenderThread()` → `commandList->drawInstanced(...)` / `drawIndexedInstanced(...)` on `g_commandLists[g_frame]` |
| Translation: shader identity | `video.cpp:5055-5092` (`CreateShader`) | guest microcode hashed `XXH3_64bits(function, function[1] + function[2])`; `FindShaderCacheEntry` binary-searches the sorted table (`:5046-5054`); 3 hardcoded hashes redirect to hand-written HLSL (`blend_color_alpha_ps`, `csd_no_tex_vs`, `csd_vs`); unknown hash → refcounted empty `GuestShader` (renders nothing, no error) |
| Translation: shader blobs | `UnleashedRecompLib/shader/shader_cache.h:1-24`; `video.cpp:778-792`, `:3854-3880` | `ShaderCacheEntry { hash, dxilOffset/Size, spirvOffset/Size, specConstantsMask }`; ZSTD blob decompressed at init; `GetOrLinkShader` smolv-decodes SPIR-V (Vulkan) or uses DXIL bytes (D3D12) via `g_device->createShader(..., "main", ...)` |
| Translation: offline shader compiler | `video.cpp:43`; `tools/XenosRecomp/` (EMPTY) | `#include "../../tools/XenosRecomp/XenosRecomp/shader_common.h"` — submodule `hedge-dev/XenosRecomp` is uninitialized locally, so no bodies to quote; translation itself is not in-repo |
| Backend selection | `video.cpp:1663-1720` (`Video::CreateHostDevice`) | ordered try-list of factories: `g_vulkan ? Vulkan-first : D3D12-first`; `g_vulkan = DetectWine() \|\| Config::GraphicsAPI == Vulkan`; crash-retry flips order and disables Vulkan redirection; D3D12 creation wrapped in `__try/__except`; non-D3D12 builds are Vulkan-only |
| Swapchain/present | `video.cpp:1878`, `:2791-2851` (`Video::Present`) | `g_queue->createSwapChain(GameWindow::s_renderWindow, bufferCount, BACKBUFFER_FORMAT, Config::MaxFrameLatency)`; `Present` hooked from guest, drives `CheckSwapChain` + frame profilers |

### 3b. Mapping onto ps2xGS plan §5/S0–S8 (same shape or change?)

| Plan element | Same shape? | What UnleashedRecomp suggests (cite = plan section) |
|---|---|---|
| §2 `gsharness`: recording backend + `gsreplay --backend cpu\|gpu` + diff table | NOT the same shape — they have no equivalent | the plan's record/replay/diff harness has no counterpart here; nothing to borrow, and nothing contradicts it. Their closest artifact (precomputed PSO table) argues the plan's *synthetic* per-feature captures (§2 "Synthetic streams") are the right analogue of "known-good inputs", since live-game capture (Gate C) is not yet available |
| §5.1 exact-compute-rasterizer-over-VRAM-buffer first | Different domain, same lesson | their guest→host split keeps guest state (`Guest*`) and host handles in one struct; for ps2xGS the analogue is keeping the VRAM buffer as the single source of truth (§5.1) rather than mirroring state per backend — the `GuestDevice` size-assert pattern (`video.h:66`) supports asserting our `GSDrawState` layout instead of re-describing it per backend |
| S1 transfers + `Present` from DISPFB | Borrowable sequencing | their bring-up order (device → swapchain → upload/translate → present hook) matches S0→S1; their `DrawPrimitiveUP` path (guest pointer → `g_intermediaryUploadAllocator.allocate`, `:4688-4693`) is the shape our `UploadImage` staging wants |
| S6 batching by draw state | Directly borrowable | `FlushRenderStateForMainThread` (guest thread, `:4297`) + `FlushRenderStateForRenderThread` (render thread) is exactly the "batch across primitives is the backend's job" split (plan §1 Consequences): dirty-flag state flush, not per-call host calls |
| Backend factory (their `CreateD3D12Interface`/`CreateVulkanInterface` try-list) | Borrowable factory shape | our `GS::setRasterBackend` injection + `gsreplay --backend` flag is the same seam; their crash-retry order flip (`:1685-1695`) suggests a `--backend` fallback order for S7 (Odin) rather than a hard failure |
| Shader/pipeline precompilation (`StartPipelinePrecompilation`, PSO table) | S6 analogue | precompute the hot draw-state → pipeline map from the census (plan §3) the way their PSO table precomputes hot guest-state combos — a census consumer for S6, not S1 |
| What I would change in the plan | — | nothing structural. One addition to §2: record the *backend-selection + device description* row in every replay table (their `getDescription` log at `:1712+`), so S7 Odin diffs are attributable to device vs. backend |

## 4. Q4 — Patch/override systems (30 min cap)

### 4a. N64Recomp `ffb39cd` — TOML `[patches]`, all applied at recompile time

Config table `[patches]` (`src/config.cpp:447`); every entry validated
against the symbol table with fail-fast `exit_failure` on typos.

| Override | Config format | Application point (file:line) |
|---|---|---|
| `stubs` (name list) | `stubs = ["func", …]` (`config.cpp:58-81`) | `main.cpp:513-523` sets `func.stubbed`; `recompilation.cpp:777` skips analysis+recompilation of the body (emits decl only) |
| `ignored` (name list) | `ignored = […]` (`config.cpp:84-104`) | `main.cpp:525-535` sets `func.ignored`; skipped at emit (`main.cpp:740`) |
| `renamed` (name list) | `renamed = […]` (`config.cpp:107-127`) | `main.cpp:538-549`: `func->name + "_recomp"` (frees the name for a native reimplementation) |
| `instruction` patches | `[[patches.instruction]]` `{func, vram, value}` (`config.cpp:160-202`; word-alignment enforced) | `main.cpp:556-577`: bounds-checked (`patch.vram` inside function) direct word rewrite `func.words[index] = byteswap(value)` BEFORE analysis |
| `hook` text injection | `[[patches.hook]]` `{func, before_vram?, text}` (`config.cpp:204-252`) | `main.cpp:579-612` records `func.function_hooks[index] = text` (index `-1` = function start when no `before_vram`); emitted verbatim into output C at `recompilation.cpp:129-135` (per-instr) and `:782-785` (function head) |
| manual sizes / manual functions | `FunctionSize`/`ManualFunction` (`config.h:20-36`) | `main.cpp:395` sizes; `main.cpp:17-69` adds whole functions to context |
| reimplemented (compiled-in) | `reimplemented_funcs` unordered_set (`symbol_lists.cpp:3`; e.g. libultra names) | `elf.cpp:85-86`, `main.cpp:455-457`: decl emitted, body not (`main.cpp:788-791`) |
| patch-section promotion | ELF sections named `PatchSectionName`/`ForcedPatchSectionName` + reference syms (`main.cpp:744-771`) | strict-mode cross-check recompile-time: replacement without reference symbol (or vice versa) fails the build |

Worked example (reconstructing the format from the parser): with
`func = "osCreateThread"`, `vram = 0x80012340`, `value = 0x03E00008`
(`jr $ra`), the recompiler byteswaps the word into `func.words` at
`(vram - func.vram)/4` before `analyze_function` ever runs — i.e. patches
compose with jump-table analysis rather than bypassing it.

### 4b. XenonRecomp `ddd128b` — TOML `[main]` + `[[midasm_hook]]`, all at recompile time

| Override | Config format | Application point (file:line) |
|---|---|---|
| `functions` (addr/size list) | `[[main.functions]]` `{address, size}` (`recompiler_config.cpp:50-59`) | `recompiler.cpp:171-175` seeds entries (overrides Analyse sizing) |
| `invalid_instructions` | `{data, size}` (`recompiler_config.cpp:61-70`) | `recompiler.cpp:227-234`: gap-fill sweep skips `size` bytes at matching word (data-in-code escape hatch) |
| `[[midasm_hook]]` | `{address, name, registers[], return?, return_on_true/false?, jump_address[_on_true/false]?, after_instruction?}` (`recompiler_config.cpp:95-138`; mutual-exclusion diagnostics) | `recompiler.cpp:436-518`: emits `name(r3, f1, ctr, …)` call before (or after, if `after_instruction`) the instruction at `address`, with optional `return;` / `goto loc_<X>` / `if (…)` conditional variants; register names resolved per-class (`r/f/v/c/x`, `:452-477`) |
| XEX patch files | `patch_file_path` / `patched_file_path` (`recompiler_config.cpp:16-17`) | `XenonUtils/xex_patcher.cpp:225` (`XexPatcher::apply`: LZX delta/full title-update application) — input preprocessing, loaded where the XEX is opened, before any analysis |
| No function-stub/ignore/rename lists | — | no name-based stub/ignore mechanism exists; the analogue is link-time weak-symbol override (Q1a) |

Worked example (from the emitter): `address = 0x82001000, name =
"MyHook", registers = ["r3", "r4"], return_on_true = true` emits
`if (MyHook(ctx.r3, ctx.r4)) { return; } else { }` before the instruction
at that address.

### 4c. Mapping onto our TOML `stubs` + `untracked`

Our mechanism (`ExportPS2Functions.java:626-717`): `[general].stubs` /
`untracked_stubs` name lists emitted from Ghidra.

| What they express | Ours cannot |
|---|---|
| N64 `instruction` patch (rewrite one guest word pre-analysis) | ours has no word-level patch: a bad instruction can only be stubbed whole or left to fail |
| N64 `hook` text injection (verbatim host code at instr/function granularity) | ours has no mid-function injection; closest is editing the recompiler |
| N64 `ignored` vs `stubs` distinction (skip entirely vs emit decl-only) | ours conflates "don't compile" and "declare but don't define" |
| N64 `renamed` (free a symbol name for native reimplementation) | ours has no rename; a native replacement must keep the guest name |
| N64 fail-fast on unknown names (`exit_failure`, `main.cpp:513-523`…) | ours silently accepts stale stub names (typo-class bugs survive) |
| Xenon `midasm_hook` (address-keyed host call with return/jump variants) | ours is name-keyed only; no address-keyed hook, no conditional return/jump emission |
| Xenon `invalid_instructions` (data-in-code skip ranges) | ours has no sweep escape hatch for data words inside code ranges |
| Xenon XEX patch-file input stage | ours has no title-update/patch input stage (single-ELF assumption) |

## 5. Q5 — Recompiler testing patterns (30 min cap)

### 5a. Harness table

| Project | Harness (file:line opened) | What it covers |
|---|---|---|
| N64Recomp static recompiler | NONE — no test files, no test target for `src/` | analysis (`analyze_function`), `resolve_jal`, C emission: all untested in-repo |
| N64Recomp LiveRecomp | `LiveRecomp/live_recompiler_test.cpp:1-364` — data-driven golden-output execution test | per test `<name>_data.bin` (header: text/init/good offsets + load addresses, `:98-109`); JITs via `recompile_function_live` (`:253`), runs with `sp` set (`:271-272`), `byteswap_compare`s the data section against expected (`:278`); mismatch dumps `<name>_data_out.bin` (`:281-288`); reports codegen/execution µs + code size (`:292-296`, `:322-325`). Error classes: open/recompile/struct/data-diff (`:50-56`) |
| N64Recomp corpus | ABSENT | no `*_data.bin` files in repo; runner takes `[test directory] [test 1] …` (`:303-306`) — corpus lives elsewhere or never landed |
| XenonRecomp | `XenonRecomp/test_recompiler.cpp:1-291` (`TestRecompiler::RecompileTests`) — annotated-asm golden execution-test *generator* | per `.o` in src dir: `Analyse` (gap-walk `Function::Analyze`, `:8-34`), emit recompiled C++ (`:59-70`), generate `main.cpp` (4 GB mmap/VirtualAlloc guest memory, `:280-284`) with per-test `REGISTER_IN`/`MEMORY_IN` setup (`:151-192`) and `REGISTER_OUT`/`MEMORY_OUT` checks (`:207-254`) parsed from `#_`-comment annotations in the paired `.s` file; checks print `EXPECTED/ACTUAL` via `PPC_CHECK_VALUE_U/F` (`:114-115`) but do NOT fail the binary (no exit-code verdict) |
| XenonRecomp corpus + runner | ABSENT | no `.s`/`.o` test files in repo; `XenonTests/` contains only `CMakeLists.txt` (glob-builds nothing when empty); CR-out checks explicitly `continue; // TODO` (`:217`) |
| Neither | differential tests vs interpreter | ABSENT in both; no side-by-side interpreter comparison anywhere |
| Contrast: psprecomp (out of Q5 scope, one row) | `tests/test_emit.c:1-50` | hand-assembled 8-word MIPS functions + `CHECK` assertions on the *shape* of generated C (`The assertions are about the *shape* of the generated C, because that shape is the contract`); covers delay-slot temporaries and `jr $ra` emission — the unit-test shape neither N64 nor Xenon has |

### 5b. Mapping onto our `ps2xTest` + record-test gaps

Our harness (`ps2xTest/src/elf_analyzer_tests.cpp:141-186`): hand-built
`Instruction` vectors asserting analyzer facts.

| Gap | Borrowable pattern (source) |
|---|---|
| **The LUI+ORI fold**: a constant-fold miscompile needs an *execution* oracle, which hand-built analyzer vectors cannot give | Xenon's annotated-asm generator (`test_recompiler.cpp:140-254`): a test written as MIPS asm with `#_ REGISTER_IN r4 0x…` / `#_ REGISTER_OUT r5 0x…` comments, recompiled and run natively; the fold's wrong value would print as `EXPECTED/ACTUAL`. N64's live-test binary (`*_data.bin` + memcmp, `live_recompiler_test.cpp:278`) is the same idea with a binary instead of annotated-asm encoding |
| Analysis passes (sweep, jump-table) untested beyond vectors | psprecomp's `test_emit.c` shape-assertions: assert on emitted-C substrings (e.g. "LUI+ORI pair emits single constant assignment") without needing execution |
| No verdict | both harnesses report-but-don't-fail (Xenon prints, exit 0; N64 prints `Passed n/m`, `return 0` always at `:361`); our harness should keep its exit-code verdict — this is one place to NOT copy them |

## 6. Q6 — xboxrecomp (45 min cap, LICENSE FIRST)

Repo: `https://github.com/sp00nznet/xboxrecomp` (remote verified),
rev `6f55eaa`, local clone `/Volumes/Extreme SSD/q3-siblings/xboxrecomp`.

**LICENSE: MIT** (`LICENSE`: `MIT License / Copyright (c) 2026 sp00nz`),
with third-party attributions under `LICENSES/` (incl. `LGPL-2.1.txt`)
described by `NOTICE` (`xboxrecomp is MIT licensed (see LICENSE). The
components listed below are not…`). Licensed → quoted below at the same
level as Q1–Q5; license re-cited (not re-verdict) in the borrowable table.

### 6a. Xbox kernel-HLE

| Aspect | File:line (opened) | Mechanism (quoted) |
|---|---|---|
| Stub table generation | `src/kernel/kernel_thunks.c:106-338` (`xbox_resolve_ordinal`) | ordinal→implementation `switch` over the canonical 366-export table; DATA exports return `&xbox_…` addresses (e.g. `:129` `case 16: return (ULONG_PTR)&xbox_ExEventObjectType`), code exports return function pointers. Header warns: `Numbering the callable exports sequentially and skipping those slots shifts every later ordinal and silently dispatches the wrong function` (`:95-101`); `Where no implementation exists the case is omitted entirely, so the default arm logs it` (`:103-104`) |
| Unimplemented at init | `src/kernel/kernel_thunks.c:334-338`, `:444-454` | `default:` logs `Unresolved kernel ordinal %u` at ERROR and returns 0; init points the slot at `xbox_unresolved_thunk` and counts it |
| Unimplemented at runtime | `src/kernel/kernel_thunks.c:376-382` | `xbox_unresolved_thunk`: logs `Call to unresolved kernel thunk! Return address is on the stack.` + `DebugBreak()` under `_DEBUG` |
| Init: title-true import order | `src/kernel/kernel_thunks.c:424-444` | reads ordinals from the loaded XBE's in-memory thunk table (`0x80000000\|ordinal` entries); static 147-ordinal fallback `g_thunk_ordinals` (`:353-369`) only when no XBE is mapped |
| Coverage headline | `src/kernel/kernel_thunks.c:456-466` | `Thunk table: %u/%u resolved, %u unresolved` + `WARNING: %u kernel imports are unresolved - game may crash!` |
| Coverage audit tool | `tools/kernel_audit/coverage.py:1-60` | per-title `what it imports vs what the bridge routes`, remainder split A (xbox_* exists, needs bridge wrapper) / B (data export) / C (no implementation); documents the generic-stub stack-cleanup hazard (`A missing size entry is the dangerous case: the stub then pops nothing`) and two Halo-2276 mis-routing war stories (guest-VA vs host-heap ownership) |
| Function tracing | `src/kernel/recomp_trace.c:1-56` | stderr unbuffered (`what was the last thing that happened before it died`); `RECOMP_TRACE_BUDGET` (default 400000) anti-disk-fill; `RECOMP_TRACE_PROFILE=1` turns entry counting into a hottest-first call profile |
| Indirect-call feedback | `src/kernel/icall_feedback.c:1-91` | (91 lines; supplements Q2-class resolution — not opened past the header under the cap; recorded for follow-up) |

### 6b. SSX3-Xbox specifics

**ABSENT.** No `ssx`/`tricky`/`amaze` match anywhere under
`src/ include/ tools/ docs/ tests/`. The proven title is **Burnout 3:
Takedown** (`docs/technical/candidate-games.md`: `The first game
successfully targeted by this toolkit… Code size: 2.73 MB .text (~22,000
functions)… Kernel imports: 147 functions`); `Halo 2276` appears as a
second bring-up data point (`tools/kernel_audit/coverage.py`); the NV2A
menu captures below are Burnout 3 menus (WORLD TOUR / ROAD RAGE / CRASH).
Nothing SSX3-Xbox-specific exists to borrow.

### 6c. NV2A path vs ps2xGS

| Aspect | File:line (opened) | Mechanism (quoted) |
|---|---|---|
| Capture | `src/nv2a/nv2a_pb_replay.c:1-36` + `menu_pb_*.h` | pushbuffers captured from xemu, compiled in as per-menu-state headers (8 menu states); replay switches on live menu-navigation state — capture is a *content* source, not a test input |
| Replay | `src/nv2a/nv2a_pb_replay.c:254-323` (`nv2a_pb_replay_frame`) | replays captured words through the PGRAPH→D3D11 translator for display; frame counter + periodic stderr log only |
| Replay/diff harness | ABSENT | no pixel/VRAM comparison anywhere in `src/nv2a/`; closest is `RECOMP_FB_DUMP=<prefix>` writing `<prefix>NNN.bmp` `so the result can be looked at without a display` (`src/kernel/nv2a_pb_exec.c:27-28`) — eyeball diff, not automated |
| Census (read-only survey) | `src/kernel/nv2a_pb_scan.c:1-41`, `:134-142` | `RECOMP_PB_SCAN` walks the title's pushbuffer counting (subchannel, method) with parse-health unknowns (`a decoder that desynchronises produces plausible looking method numbers out of parameter data`); report to stderr ranked by count |
| Minimal executor + remainder ranking | `src/kernel/nv2a_pb_exec.c:1-28` | `RECOMP_PB_EXEC`: surfaces + clears + flat screen-space UI raster straight into the guest framebuffer; vertex-program batches `counted and skipped rather than drawn somewhere wrong`; `nv2a_pb_exec_report()` ranks the unhandled remainder; `RECOMP_RASTER_TEST` draws one known triangle after every clear |
| Translation layer | `src/nv2a/nv2a_pgraph_d3d11.c:1-14`; `src/d3d/README.md:45-59` | NV2A methods → D3D8 calls → D3D11 (dirty-state flush per draw: depth/blend/rasterizer states created+bound on demand); menu profile documented (INLINE_ARRAY 5-dword verts, TRIANGLE_STRIP, ~448 verts/frame) |
| MMIO capture | `src/nv2a/nv2a_mmio_hook.c:1-22` | Win32 VEH hook decoding x86-64 MOVs to `0xFD000000/16MB`, routing through register handlers and advancing RIP; read/write/decode-fail counters |
| Backend selection | `src/d3d/d3d8_gl.c:1-21` | compile-time platform split: Windows → D3D11 (`d3d8_device/resources/states/combiners/vsh/shaders.c`), POSIX → OpenGL 3.3 (`d3d8_gl.c`, SDL2 + epoxy). No runtime factory/try-list (contrast UnleashedRecomp §3a) |

### 6d. NV2A vs ps2xGS plan (§5/S0–S8) mapping

| Their artifact | Plan analogue | Borrowable? |
|---|---|---|
| `pb_scan` census (`nv2a_pb_scan.c`) | §3 `gscensus` | YES — same shape (count what the stream asks for, rank it); their parse-health unknown-word tell belongs in our census as a "decoder desync" row |
| xemu captures compiled in (`menu_pb_*.h`) | §2 `.gscap` reference set | YES in concept, NO in form: our captures stay out-of-git on the mini/SSD per §2; their compile-in is a stopgap that bakes title content into the binary |
| `RECOMP_FB_DUMP` BMPs | §2 per-`Present` reference pixels | theirs is manual-eyeball; the plan's automated diff table is strictly stronger — nothing to change |
| `RECOMP_RASTER_TEST` known triangle | §2 synthetic streams | same idea (separate pixel-path health from content health); our per-feature synthetic set generalizes it |
| Remainder ranking (`pb_exec_report`) | §6 one-feature-per-iteration in census frequency order | same loop fuel; adopt the "ranked remainder" report shape for our loop status rows |
| Missing: any automated diff | §2 `gsreplay` exit-code verdict | the plan already has what they lack — no change |
| Compile-time backend split | §5.2 Vulkan-via-MoltenVK single path | no conflict; their split is platform-driven where ours is interface-driven (`setRasterBackend`) |

## 7. Borrowable/tooling table

Idea → source (project, rev, file:line, quoted body) → PS2Recomp/ps2xGS
analogue (function-level prose, NOT applied) → license re-cite (P3 §8.3
for Q1–Q5 rows; Q6 rows re-cite this report's §6 LICENSE read; no new
verdicts anywhere).

| # | Idea | Source | PS2Recomp/ps2xGS analogue (NOT applied) | License re-cite |
|---|---|---|---|---|
| B1 | Weak-symbol HLE override at link | Xenon `ddd128b` / `recompiler.cpp:2384-2386,2448-2452` / `PPC_WEAK_FUNC(NAME) { __imp__NAME(ctx, base); }` | emit a weak default per imported stub symbol routing to `dispatchNumericSyscall`, so real implementations override by link instead of by editing the switch | MIT per P3 §8.3 (hedge-dev) |
| B2 | Address→name mapping table alongside emit | Xenon `ddd128b` / `recompiler.cpp:2586-2602` / `PPCFuncMappings[] = { { 0xADDR, name }… }` | emit an address→name table for the dispatcher's strict-return and missing-target diagnostics | MIT per P3 §8.3 |
| B3 | HLE work-list census before any run | psprecomp `caca759` / `main.c:603-641` / `This is the HLE work list: everything here has to exist before the game runs` | analyzer-side `funcs`-equivalent printing the distinct syscall/stub surface per ELF | MIT per P3 §8.3 (sp00nznet) |
| B4 | Miss log with deliberate return value | psprecomp `caca759` / `hle.c:105-127` / `Returning 0 rather than aborting is deliberate…` | give `Dispatcher.cpp`'s `default:` arm the miss shape: stderr line (number + name-when-known) + documented return value | MIT per P3 §8.3 |
| B5 | Bounded recent-miss/zero ring | psprecomp `caca759` / `hle.c:71-103` / last-16 zeros + `SCE_KERNEL_ERROR_OK is also zero` caveat | keep a recent-miss ring next to the P1c histogram for the wild-pointer-far-from-cause class | MIT per P3 §8.3 |
| B6 | Compile-free entry trace | psprecomp `caca759` / `emit.c:839-850`, `dispatch.h:44-69` / `one store per call when on, and nothing at all when off` | `-D`-gated per-call entry trace feeding the miss-context printer | MIT per P3 §8.3 |
| B7 | Table self-test from one source of truth | psprecomp `caca759` / `test_hle.c:83-104` / recompute `psp_nid(name)` per entry | self-test recomputing every registered syscall-number↔name pair | MIT per P3 §8.3 |
| B8 | Per-title single-stub override by re-registration | psprecomp `caca759` / `hle.c:16-28` / `a game repo can override one function without forking the table` | title repos replace one stub by re-registration instead of fork edits | MIT per P3 §8.3 |
| B9 | Auto-create function on unknown in-section call target | N64 `ffb39cd` / `recompilation.cpp:78-80,313-317` / `CreateStatic` + `static_<sec>_<vram>` | sweep auto-creates CSV entries for JAL/JR targets with no symbol (would have caught the alarm-callback split at sweep time) | MIT per P3 §8.3 (Wiseguy) |
| B10 | BL-target sweep + gap-fill Analyse | Xenon `ddd128b` / `recompiler.cpp:206-251` / `PPC_OP_B && PPC_BL` sweep then `Function::Analyze` every gap | two sweep passes: call-target census first, recursive-descent size analysis of every unclaimed range second | MIT per P3 §8.3 |
| B11 | Jump-table entries must land in-function (hard error) | N64 `ffb39cd` / `analysis.cpp:333-344` / `If it's not then this is the end of the jump table` + `Failed to determine size…` | CSV validation: table entries outside the owning function fail the sweep, not silently short | MIT per P3 §8.3 |
| B12 | Offline idiom-pattern scan → TOML fact file | Xenon `ddd128b` / `XenonAnalyse/main.cpp:215-306` / `SearchMask` 4 switch idioms → `[[switch]]` | offline pre-pass emitting jump-table facts (base/reg/labels) the recompiler consumes, instead of inline discovery | MIT per P3 §8.3 |
| B13 | Recompile-time missing-idiom diagnostic | Xenon `ddd128b` / `recompiler.cpp:2427-2428` / `Found a switch jump table … with no switch table entry present` | sweep diagnostic firing on the JR-table *idiom* at analysis time, complementing the runtime strict-return diagnostic | MIT per P3 §8.3 |
| B14 | LUI/addiu/addu + LW + JR register-state tracking (incl. GOT + stack spills) | N64 `ffb39cd` / `analysis.cpp:106-252` / `RegState` + `stack_states[]` | the jump-table discovery algorithm for our sweep's JR-target pass | MIT per P3 §8.3 |
| B15 | Guest-thread batch + render-thread dispatch split | Unleashed `cf829a9` / `video.cpp:4280-4294,5270-5298` / `LocalRenderCommandQueue` + `Proc*` switch | ps2xGS S6: dirty-flag state flush split across the submit/render boundary ("batching is the backend's job") | GPL-3 per P3 §8.3 |
| B16 | Hash-keyed precomputed pipeline/shader tables | Unleashed `cf829a9` / `video.cpp:5046-5092`, `cache/pipeline_state_cache.h` / `XXH3_64bits` + `lower_bound` | ps2xGS S6: precompute the hot draw-state→pipeline map from the census | GPL-3 per P3 §8.3 |
| B17 | Backend try-list with crash-retry order flip | Unleashed `cf829a9` / `video.cpp:1679-1720` / `interfaceFunctions` + `g_vulkan = !g_vulkan` retry | `gsreplay --backend` fallback order for S7 Odin instead of hard failure | GPL-3 per P3 §8.3 |
| B18 | Upload-allocator staging for caller-owned pointers | Unleashed `cf829a9` / `video.cpp:4688-4693` / `g_intermediaryUploadAllocator.allocate` | S1 `UploadImage` staging shape | GPL-3 per P3 §8.3 |
| B19 | Pre-analysis single-word patch | N64 `ffb39cd` / `main.cpp:556-577` / `func.words[index] = byteswap(value)` | TOML word-patch entry applied before sweep analysis | MIT per P3 §8.3 |
| B20 | Verbatim host-code injection at instr/function points | N64 `ffb39cd` / `recompilation.cpp:129-135,782-785` / `function_hooks[index] = text` | mid-function injection hook for sweep/recomp diagnostics | MIT per P3 §8.3 |
| B21 | ignored-vs-stubs + fail-fast on unknown names | N64 `ffb39cd` / `main.cpp:513-535` / `Function {} is stubbed out … but does not exist!` | split our `stubs`/`untracked` semantics and fail the sweep on stale names | MIT per P3 §8.3 |
| B22 | Address-keyed host call with return/jump variants | Xenon `ddd128b` / `recompiler.cpp:436-518` / `[[midasm_hook]]` emission | address-keyed sweep/recomp hooks with conditional return/jump | MIT per P3 §8.3 |
| B23 | Data-in-code skip ranges | Xenon `ddd128b` / `recompiler.cpp:227-234` / `invalidInstructions` | sweep escape hatch for data words inside code ranges | MIT per P3 §8.3 |
| B24 | Annotated-asm execution tests (REGISTER/MEMORY IN/OUT) | Xenon `ddd128b` / `test_recompiler.cpp:140-254` / `PPC_CHECK_VALUE_U/F … EXPECTED/ACTUAL` | the test that would have caught the LUI+ORI fold: MIPS asm + expected register values, recompiled and run natively | MIT per P3 §8.3 |
| B25 | Binary golden-data tests (input + expected dump + memcmp) | N64 `ffb39cd` / `live_recompiler_test.cpp:98-109,278,281-288` / `byteswap_compare` + `_data_out.bin` | record-test encoding for recompiler execution tests | MIT per P3 §8.3 |
| B26 | Shape assertions on generated C | psprecomp `caca759` / `test_emit.c:1-50` / `assertions are about the *shape* of the generated C` | emitter unit tests without execution (e.g. "LUI+ORI emits one constant assignment") | MIT per P3 §8.3 |
| B27 | Omit-the-case default-arm logging + unresolved-call trap | xboxrecomp `6f55eaa` / `kernel_thunks.c:103-104,334-382` / `the case is omitted entirely, so the default arm logs it` | dispatcher `default:` logs + routes to a trapping unresolved handler instead of neighbouring-function fallthrough | MIT per §6 LICENSE read (sp00nz 2026); no verdict |
| B28 | Title-true import order from the binary + static fallback | xboxrecomp `6f55eaa` / `kernel_thunks.c:424-454,353-369` / `0x80000000\|ordinal` + `g_thunk_ordinals` | read import order from the ELF/XBE; keep a static fallback for headerless inputs | MIT per §6; no verdict |
| B29 | A/B/C remainder split for coverage audits | xboxrecomp `6f55eaa` / `coverage.py:1-60` / wrapper-needed / data-value / real-work + guest-VA-vs-host-heap warning | HLE work-list remainder split by cost class | MIT per §6; no verdict |
| B30 | Trace budget + call-count profile via env vars | xboxrecomp `6f55eaa` / `recomp_trace.c:30-56` / `RECOMP_TRACE_BUDGET` + `RECOMP_TRACE_PROFILE` | env-gated diag knobs for sweep/dispatcher tracing | MIT per §6; no verdict |
| B31 | Read-only stream census with parse-health tell | xboxrecomp `6f55eaa` / `nv2a_pb_scan.c:1-41` / `RECOMP_PB_SCAN` + desync-unknowns warning | `gscensus` decoder-desync row | MIT per §6; no verdict |
| B32 | Ranked unhandled-remainder report + known-primitive health check | xboxrecomp `6f55eaa` / `nv2a_pb_exec.c:1-28` / `pb_exec_report()` + `RECOMP_RASTER_TEST` | loop status rows in ranked-remainder shape; one known-primitive synthetic for pixel-path health | MIT per §6; no verdict |

Anti-borrowables (observed, NOT recommended): Xenon `// ERROR`
fall-through on unknown call targets (`recompiler.cpp:400-403`); both
Q5 harnesses report-but-don't-fail (exit 0 always); xboxrecomp
compile-in of captured title content (`menu_pb_*.h`).

## 8. Clone revs + paths

| Clone | Full SHA (`git rev-parse HEAD`) | Path |
|---|---|---|
| XenonRecomp | `ddd128bcca99fe8bfbb99bea583c972351fa6ace` | `/Volumes/Extreme SSD/q3-siblings/XenonRecomp` |
| UnleashedRecomp | `cf829a9eca8fb680fba4b0409ddeb6ca92f22e3c` | `/Volumes/Extreme SSD/q3-siblings/UnleashedRecomp` |
| N64Recomp | `ffb39cdad1da5de07eaaa48bd1db4a89a7986771` | `/Volumes/Extreme SSD/q3-siblings/N64Recomp` |
| psprecomp | `caca7595251410ae7887aa209ba56397a835d0e1` | `/Volumes/Extreme SSD/q3-siblings/psprecomp` |
| wtf-psp-recomp | `ebaeed4d33058c30673a36435aec29d470d47723` | `/Volumes/Extreme SSD/q3-siblings/wtf-psp-recomp` |
| xboxrecomp | `6f55eaa29d369860c950f442649e23ca86a3c275` | `/Volumes/Extreme SSD/q3-siblings/xboxrecomp` |

Short SHAs match P3 §8.1 where overlapping. `psxrecomp`/`SaturnRecomp`
untouched per runbook (existing P3 license rows stand).

## 9. Exact commands (representative; all read-only)

```
git -C <clone> rev-parse HEAD            # per-clone rev (loop over q3-siblings/*/)
ls /Volumes/Extreme\ SSD/q3-siblings/
grep -rn -i "noreturn|no_return|…" <src>  # absence checks (Q2)
grep -rn "Function::Analyze|…" .          # caller location (Q2)
grep -n "GUEST_FUNCTION_HOOK|…" gpu/video.cpp  # capture points (Q3)
grep -n -i "replay|capture|golden" …      # harness absence checks (Q3/Q5)
find <clone> -iname "*test*" / -name "*_data.bin" / -name "*.s"  # corpora checks (Q5)
git remote -v; cat LICENSE; ls LICENSES  # Q6 license gate
grep -rln -i "ssx|tricky|amaze" src include tools docs tests  # Q6b absence check
```

All quoting bodies were opened with file reads; `grep`/`find` only
located. No builds, no boots, no emulator runs, no leases, no `adb`, no
clone edits, no `git push`.

## 10. What I could not do

- Q1 was recovered from disk (pre-restart session wrote §1); Q2–Q6 plus
  §7–§10 are this session's work. Time boxes observed per question; Q6
  held to its 45 min cap (`icall_feedback.c` recorded unopened: §6a).
- `tools/XenosRecomp/` (UnleashedRecomp) and `psprecomp/` (wtf-psp-recomp)
  are uninitialized submodules — empty locally, no bodies to quote.
- No test corpora exist in N64Recomp or XenonRecomp (runners without
  inputs); no differential-vs-interpreter tests exist in either.
- Noreturn analysis is absent in both Q2 projects (negative result, not
  an omission of method — full-tree case-insensitive greps).
- SSX3-Xbox specifics are absent in xboxrecomp (negative result —
  full-tree grep); its titles are Burnout 3 (+ Halo 2276 data point).
- No `psxrecomp`/`SaturnRecomp` reads beyond the runbook's carve-out.
- Commit covers `local/research/P5/` only, `git add -f`, `[P5]` prefix,
  `Orchestrated-By: Muse Code` trailer. No push (runbook rule).
