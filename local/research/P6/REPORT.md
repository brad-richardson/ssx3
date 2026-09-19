# P6 report — ssxdecomp/ssx3 ladder names + structure (read-only research)

No verdicts are given below; tables report recorded values.

**License rule (restated, followed throughout):** the decomp repo has no
license (re-verified below) and matching-decomp source is game-derivative
either way. This report and the CSV contain NAMES, ADDRESSES, and STRUCTURAL
FACTS ONLY. No decompiled function body, comment, or data table was copied
into the report, the CSV, or anywhere else. The committed CSV holds
addr→name pairs only. Every claim cites a file opened (clone path + line
numbers); `grep` output was used only to locate.

**Inputs read first:** `local/research/P1/REPORT.md` Parts 8–10 (P8: MMIO
fold diagnosis at `sub_003912A8`; P9: analyzer fix `f2149e7`, new GS-CSR
park at `0x375d10` in caller `sub_00375A08`; P10: CSR-bit/producer
diagnosis, no runtime writer to bit 14), and the sweep CSV header
(`name,start,end,size`, 9,270 data rows).

## P6-0. Clone + license + target match

| Item | Value |
|---|---|
| Clone command | `git clone --depth 1 https://github.com/ssxdecomp/ssx3.git "/Volumes/Extreme SSD/ssxdecomp-ssx3"`, exit 0 |
| Rev | `9cd4626054ba96143a849978b7c00bca7d85bcc0` ("Fixed Commenting", 2026-03-20 +1100) |
| Tracked files | 419 (`git ls-files`) |
| Apparent size (tracked bytes) | 52,838,197 |
| `du -sk` on-disk | 1,104,896 KB (ExFAT cluster slack; same effect as P1 P2-1) |
| GitHub `size_kb` | 36,941 (~36 MB, as expected) |
| Root license file | NONE: top-level `ls` shows no `LICENSE*`/`COPYING*`/`COPYRIGHT*`; `find -maxdepth 2` for those names returns nothing |
| GitHub license field | `null` (`gh api repos/ssxdecomp/ssx3`, `license: null`) |
| Only license text in tree | `tools/objdiff/LICENSE` (Apache-2.0, 11,342 bytes: `head` lines 1–3) — covers the vendored objdiff binaries only, not the decomp |
| Per-file re-cite | Not triggered (no repo license exists) |
| Their target | `SLUS_207.72`, sha1 `77114dfd1205eaccf1ccc18c5f9650097fa78bd8` (`README.md:3`, `config/ssx3_us.yaml:2`) |
| Our ELF | `$W/P1/SLUS_207.72` sha1 `77114dfd1205eaccf1ccc18c5f9650097fa78bd8` (re-hashed this session, 3,890,784 bytes; matches P1 P2-0) |
| Match | sha1 identical |

`W` = `/Volumes/Extreme SSD/ps2recomp-spike`. Clone path below is
abbreviated `C`.

## P6-1. Q1 — Symbol map + coverage

### Sources

| Source (opened) | Content |
|---|---|
| `C/config/symbol_addrs.txt` (757 lines, `wc -l` 756, last line unterminated; marker `// Spreadsheet Auto Generation` at line 67) | 749 `name = 0xADDR;` pairs: 724 tagged `//type:func`, 25 untagged; 749 unique addrs, 749 unique names, 0 duplicates; range `0x113198`–`0x420378` |
| `C/config/lib_symbol_addrs.txt` | 0 bytes (empty; listed in `config/ssx3_us.yaml:30` but contributes nothing) |
| `C/src/**/*.cpp` `INCLUDE_ASM` labels (112 entries in 6 files) | 60 names already in config; 52 extra `func_<8hex>` labels absent from config, all with unique embedded addrs, 0 overlapping config addrs, range `0x317710`–`0x3ede80` |
| `func_<addr>` convention check | The 1 config entry of that shape (`func_00317890__Fff = 0x00317890`) matches its embedded addr; all 112 `INCLUDE_ASM` labels (config-resolved or embedded) fall inside their file's yaml vram range (6/6 files, 0 outside) |

The 52 extra labels by file: `src/bx/bxstring.cpp` 30,
`src/dirtysock/tags.cpp` 17, `src/bxrandom.cpp` 3, `src/hashvalue.cpp` 2.

### Coverage join vs `$W/P1/ssx3-functions.sweep.csv` (9,270 data rows)

| Item | Value |
|---|---|
| CSV emitted | `local/research/P6/ssx3-decomp-names.csv`, header `addr,name,src_file`, 801 data rows (802 lines), sorted by addr, 0 dup addrs |
| Sweep rows gaining a name (start ∈ table) | 618 / 9,270 = **6.67%** |
| Decomp addrs that are sweep starts | 618 / 801 = 77.2% |
| Decomp addrs that are NOT sweep starts | 183 (analyzed in P6-3) |

Name styles (top): `func_ADDR` 53; `cDirtysock_*` 25; `cOVState_*` 23;
`cBXString_*` 15; `cUITemplate_*` 13; `cSSXApp_*` 13; `cAI_*`,
`cBENewPlayerInterf*`, `cFEMemCard_*`, `cInputMapParser_*` 9 each.
Addr regions: `0x1xxxxx` 281, `0x2xxxxx` 206, `0x3xxxxx` 308, `0x4xxxxx` 6.

### Ladder naming table (one row each; all UNNAMED)

Yaml owners cite `config/ssx3_us.yaml:50-90` (vram = fileoff − 0x1000 +
0x100000). Nearest symbols are from the 801-row table. Sweep rows from the
sweep CSV.

| Addr | Decomp name | Sweep enclosing row | Yaml owner | Nearest below (dist) | Nearest above (dist) |
|---|---|---|---|---|---|
| `0x375a08` | UNNAMED | `sub_00375A08 [0x375a08,0x376938)` (is start) | `asm` unsplit `[0x21e5a8,0x2ec198)` | `0x371600 cDynamicColourEmitter_reset` (17416) | `0x38acd0 cIrradianceDataBase_Load` (86728) |
| `0x3912a8` | UNNAMED | `sub_003912A8 [0x3912a8,0x391360)` (is start) | `asm` unsplit, same span | `0x38dbd0 cLightMan_construct` (14040) | `0x391788 cFont_linkFont` (1248) |
| `0x3dcbd8` | UNNAMED | `sub_003DCBD8 [0x3dcbd8,0x3dcc88)` (is start) | `asm` unsplit, same span | `0x3dc450 USTR_vsprintf` (1928) | `0x3dddf0 FILESYS_atomic` (4632) |
| `0x3e4db8` | UNNAMED | `sub_003E4AF0 [0x3e4af0,0x3e4e98)` (mid-row, +`0xc8`) | `asm` unsplit, same span | `0x3e2768 BIG_locateentryz` (9808) | `0x3e52b0 THREAD_yieldticks` (1272) |
| `0x3e3588` | UNNAMED | `sub_003E3588 [0x3e3588,0x3e35b0)` (is start) | `asm` unsplit, same span | `0x3e2768 BIG_locateentryz` (3616) | `0x3e52b0 THREAD_yieldticks` (7464) |
| `0x3e3968` | UNNAMED | `sub_003E3968 [0x3e3968,0x3e39a8)` (is start) | `asm` unsplit, same span | `0x3e2768 BIG_locateentryz` (4608) | `0x3e52b0 THREAD_yieldticks` (6472) |
| `0x423dd0` | UNNAMED | `sub_00423DD0 [0x423dd0,0x423de0)` (is start) | `asm` unsplit `[0x2eef50,0x32f590)` | `0x420378 ungetc` (14936) | none (above table max `0x420378`) |
| `0x423de0` | UNNAMED | `sub_00423DE0 [0x423de0,0x423df0)` (is start) | `asm` unsplit, same span | `0x420378 ungetc` (14952) | none |
| `0x424020` | UNNAMED | `sub_00424020 [0x424020,0x424050)` (is start) | `asm` unsplit, same span | `0x420378 ungetc` (15528) | none |
| `0x40fc6c` | UNNAMED | `sub_0040FB88 [0x40fb88,0x40fc90)` (mid-row, +`0xe4`) | `asm` unsplit, same span | `0x3ede80 func_003EDE80` (138732) | `0x416404 strchr` (26520) |
| `0x100008` | UNNAMED | `sub_00100008 [0x100008,0x1001c8)` (is start) | `asm:sce/crt0 [0x1000,0x1218)` | none (below table min `0x113198`) | `0x113198 cAirPredictor_reset` (78224) |

## P6-2. Q2 — Boot-path + park-region structure (names/layout only)

No decompiled body was read for this question. Call edges below are `J`/`JAL`
immediates decoded from OUR `$W/P1/SLUS_207.72` bytes (full-segment scan:
8,669 targets, 47,408 sites); endpoints are resolved through the sweep CSV
and the P6 names table (names + addresses only).

| Addr | Decomp name | File (yaml) | Named callers / callees | Structural note |
|---|---|---|---|---|
| `0x100008` (entry) | UNNAMED | `asm:sce/crt0`, file `[0x1000,0x1218)` (yaml:51) — the only named file region covering any Q2 addr | Callers: 0 direct. Callees in row (4): `0x42c300` UNNAMED, `0x424020` UNNAMED, **`0x31af80` = `main`**, `0x42c6e8` UNNAMED | Entry row calls decomp-named `main` at `0x31af80`; decomp naming starts at `0x113198`, i.e. no name within the crt0 span |
| `0x40fc6c` (dispatcher) | UNNAMED | `asm` unsplit, file `[0x2eef50,0x32f590)` (yaml:75); sits mid-sweep-row `sub_0040FB88` | Callers: 0 direct `J`/`JAL`. Callees in enclosing row: 0 direct. Indirect edge (P1 P3-3 boot-2 log): `JALR 0x40fc6c→0x3b07b8`; `0x3b07b8` = UNNAMED, sweep `sub_003B07B8 [0x3b07b8,0x3b07d8)` | A register-indirect dispatch region (no direct edges either side); nearest names are `0x3ede80 func_003EDE80` below and libc `0x416404 strchr` above |
| `0x375a08` (GS-wait caller) | UNNAMED | `asm` unsplit, file `[0x21e5a8,0x2ec198)` (yaml:71) | Caller: 1 direct — `0x226970` in sweep `sub_00226830 [0x226830,0x226b60)` = **`cSSXApp_cSSXApp`**. Callees in row: 49 direct `JAL`, 7 named sites (detail below) | Called from the `cSSXApp` constructor row; its named callees are allocator/operator symbols only; the VIF0 pair (`0x3912a8`, `0x391360`) and all 6 `0x3fdxxx`/`0x3fexxx` targets are UNNAMED |
| `0x3912a8` (VIF0 fn) | UNNAMED | `asm` unsplit, same span as `0x375a08` | Caller: 1 direct — `0x375a8c` (matches P1 P8-1b). Callee: 1 — `0x39134c→0x424020` (UNNAMED; P1 P8-1b: FlushCache trampoline) | Single-caller leaf-ish region; nearest name above is `0x391788 cFont_linkFont` (+1248) |

### `0x375a08` row callee detail (49 `JAL`, 7 named sites; addr → sweep → decomp)

Named: `0x375a20→0x317d70` `sub_00317D70` `cMemMan_alloc`;
`0x375afc,0x375b34→0x317e30` `sub_00317E30` `operator_new`;
`0x375e64,0x375e90→0x317d70` `cMemMan_alloc`;
`0x3762c0,0x3762d0→0x317e50` `sub_00317E50` `operator_delete__FPi`.
Unnamed (42): `0x395288 0x3fdf88 0x3912a8 0x391360 0x3ff060 0x3fe690
0x3febc0 0x3fdab0 0x3fdfb0 0x416210(×2) 0x423da0(×2) 0x423ba0 0x424880(×2)
0x423a90 0x4248e8 0x424950(×2) 0x423ac0 0x4249b8 0x423bc0 0x37bb10 0x394d50
0x3629b8 0x366fe8 0x361eb8 0x37c198 0x37c570 0x37c720 0x423aa0 0x423ad0
0x423bf0 0x423bb0 0x423db0(×2) 0x367360 0x361f40 0x37bd98 0x3950c0 0x364b88`
(each a sweep-row start; full pc→target list in this session's tool output,
not reprinted here).

### File-layout facts bounding all module attribution

| Fact | Cite |
|---|---|
| Only 7 named `asm`/`cpp` file spans exist; everything else is unsplit `asm` | yaml:50-90 |
| The 6 `cpp` spans (vram): `crowdrender2d [0x2db6d8,0x2dbd10)`, `hashvalue [0x317618,0x3177c8)`, `bxrandom [0x3177c8,0x317ae8)`, `bx/bxstring [0x317fe8,0x3191c0)`, `md5 [0x31c350,0x31d5a8)`, `dirtysock/tags [0x3eb198,0x3edf50)` | yaml:55-75 + vram rule yaml:46-47 |
| `src/`: 313 `.cpp` + 82 `.h` + 1 `.c` + 2 `.md` = 398 files | `find` count |
| 307 `.cpp` + 82 `.h` + `dlmalloc.c` are 1-line `//Known file in project` markers | scripted read (all 390 identical) |
| Only the 6 yaml-split `.cpp` files have content (20–111 lines: `INCLUDE_ASM` lists + `#ifdef SKIP_ASM` guards); bodies, if any, were not read | line-class counts; guard cites e.g. `src/hashvalue.cpp:10,31,41,58` |
| `src/` filenames come from **prototype builds** and "may be missing some files from the final build, and some files listed may not actually exist in the final build" — no addr→file attribution can be drawn from them | `src/readme.md:1-3` (398 `wc -l` lines) |
| `src/uncollated/` holds only its readme ("functions that havent been properly split into the correct files") | `src/uncollated/readme.md:1-2`, dir listing |
| `include/`: 5 files (`common.h`, `include_asm.h`, `macro.inc`, `md5.h`, `visualfx/crowdrender2d.h`) | dir listing |
| Decomp names `main` (`0x31af80`), `strchr` (`0x416404`), `ungetc` (`0x420378`) exist (entry/libc landmarks) | P6 CSV rows |

## P6-3. Q3 — Function-boundary truth vs our sweep

Method: 40-sample = every 19th of the 776 func labels (724 `//type:func` +
52 src `func_` labels) sorted by addr, starting at index 9
(`0x11b698`–`0x3e5928`). Decomp end = next higher decomp addr (any of 801).
"Tight" = start/end consecutive `INCLUDE_ASM` labels in one src file (106
such pairs across the 6 files, all monotonic). Classes: EXACT (same
start+end, no interior sweep start); START_MATCH_SPLIT (start matches,
extra sweep starts inside); START_MATCH_LONG (start matches, sweep end
past decomp end); START_MISS (decomp start mid-sweep-row). JAL evidence is
from our ELF bytes (8,669-target scan), not from decomp bodies.

### Agreement

| Population | EXACT | Note |
|---|---|---|
| 40-sample (next-symbol ends) | 9/40 = **22.5%** (19 SPLIT, 11 MISS, 1 LONG, 0 SHORT) | Non-tight ends are upper bounds (next name may be far); see discriminator rows |
| 106 tight in-file pairs (true ends) | 56/106 = **52.8%** (19 LONG + 31 MISS merge-side observations, **0 SPLIT, 0 SHORT**) | All non-exact are sweep rows spanning ≥2 decomp labels |
| Full start census (801) | 618/801 starts match = **77.2%** | Of 183 misses, 183/183 have 0 direct-JAL sites; of 618 hits, 609 JAL-backed + 9 non-JAL (listed below) |
| Sweep recall on JAL-called decomp functions | 609/609 = **100%** | Every directly-called named function is a sweep start |

The 9 non-JAL sweep hits (sweep found via code-pointer/thread-entry
machinery, not `JAL`): `0x1f7198 cOVState_ENTERLODGE_onCreateScreen`,
`0x1f73a8 cOVState_BIGCHALLENGE_START_onCreateScreen`, `0x1f7418
cOVState_BIGCHALLENGE_START_onGainTransition`, `0x2111a0
cOVState_PROFILE_onCreateScreen`, `0x227e68 cSSXApp_flush`, `0x227e98
cSSXApp_preUpdate`, `0x227f58 cSSXApp_timerCallback`, `0x2438f0
cSSXApp__cSSXApp`, `0x371548 cDynamicColourEmitter_Allocate`.
Ladder mid-row entries match the miss profile: `0x3e4db8` and `0x40fc6c`
have 0 direct-JAL sites each.

### Mismatch classes (3 examples each; addr ranges + names only)

**A. Sweep-merged (sweep row spans ≥2 decomp labels; all tight, firm).**
(1) sweep `sub_00318A88 [0x318a88,0x318c18)` spans `func_00318A88`,
`func_00318AF8`, `func_00318B40`, `func_00318BC0`, `func_00318BF8`
(`src/bx/bxstring.cpp`). (2) sweep `sub_003190A8 [0x3190a8,0x3191c0)`
spans `cBXString_cBXString5` + `func_00319120` (same file). (3) sweep
`sub_003EB1E0 [0x3eb1e0,0x3eb6d8)` spans
`cDirtysock_tag__TagFieldSetupTerm` + `func_003EB578` + `func_003EB588`
(`src/dirtysock/tags.cpp`).

**B. Naming-sparser-than-sweep (interior starts are JAL-backed real
functions the decomp has not named — not a sweep error).** (1)
`cSSXScriptEngine_GetScriptFromCategory [0x27b0c0,0x281f30)`: 93 interior
sweep starts, 80 JAL-backed. (2) `cGraphicsMan_AddBlendedMatrix
[0x3698e0,0x370c60)`: 44 interior, 43 JAL-backed. (3)
`cWorldTriggerManager_LoadTriggerInfo [0x2b5a18,0x2b9100)`: 41 interior,
41 JAL-backed. (All 11 sample MISSES also have 0 JAL sites to the decomp
start, matching the full-census 183/183.)

**C. Sweep-split / sweep-short / shifted: none found.** 0/106 tight pairs
show an interior sweep start or a short end. No shifted (start ±4)
pattern was observed in the 40-sample.

### Sweep self-integrity (observed while joining)

| Item | Value |
|---|---|
| Duplicate start | `0x42c1f0` ×2: sweep CSV lines 9229 (`InitSystemCallTableAddress_0x42c1f0`) and 9230 (`sub_0042C1F0`), identical `[0x42c1f0,0x42c2f0)` |
| Overlaps | 1 (the same pair); rows sorted; 9,269 unique starts over 9,270 rows |

## P6-4. Q4 — Their tooling worth stealing

Artifacts are project tooling/config (not game code); mechanisms are facts
only. "Parallels" names the existing sweep/CSV-flow counterpart without
recommending adoption.

| Artifact | File:line | One-line mechanism | Parallels in our flow |
|---|---|---|---|
| Splat auto-undefined | `config/ssx3_us.yaml:25-28` + `configure.py:194` | Splat emits `undefined_funcs/syms_auto.txt`; the link consumes both with `-T` | TOML `untracked_stubs` (P1: 391 informational entries) |
| Split symbol lists | `config/ssx3_us.yaml:30` | `symbol_addrs_path` takes a list (active + `lib_`, currently 0 bytes) | Single `ghidra_output` CSV in TOML |
| Hasm in src | `config/ssx3_us.yaml:16-17` | `hasm_in_src_path: True` keeps hand-asm next to C++ | `output/` vs `runner/` split |
| Section order/link | `config/ssx3_us.yaml:34-35,37` | Fixed `section_order`, `auto_link_sections`, `subalign: 4` | Recomp emission order (implicit) |
| Sheet→symbols pipeline | `scripts/spreadsheet.py` (97 lines) | Downloads the shared sheet (`Found Functions`: `Demangled Name` + `PS2 Address`), truncates `symbol_addrs.txt` below the marker (:27-48), sanitizes C++ names `:73-77`, dedups (`check_name` :51-60), comments out dup addrs (:85-86), appends `name = 0xADDR; //type:func` (:12) | `codeptr_sweep.py` regen of the sweep CSV (same truncate-and-rewrite shape) |
| Unused offset knob | `scripts/spreadsheet.py:13,83` | `address_offset = 0xFF000` defined but commented out at use | — (dead knob) |
| Pinned toolchain fetch | `scripts/setup.sh` (28 lines) | Downloads the ProDG `eegcc` tarball into `tools/cc/` (:17-25) | `/tmp` + `$W/P1/bin` tool builds (unpinned downloads) |
| Ninja generation | `configure.py:190` (403 lines; defs :49,67,79,352) | `ninja_syntax` writes `build.ninja`; splat split API (:11-12); per-segtype rules (:242-250); `clean` (:49); permuter settings (:67) | CMake globs for `runner/` |
| Objdiff progress units | `configure.py:177-188,318` | Per-object `objdiff.json` units with `progress_categories` from top src dir | Per-function recomp logs (no per-unit progress roll-up) |
| Vendored diff tools | `tools/objdiff/` (3 binaries + Apache-2.0 `LICENSE`) | `objdiff-cli`, linux + windows GUI builds pinned in-tree | No pinned binary-diff tool |
| Compile DB | `tools/compdb` (3 lines) | `ninja -t compdb > compile_commands.json` | — (no equivalent) |
| Naming workflow | `Main Workflow.txt:1-19` | 9 steps: split→yaml (:1), Ghidra pseudo (:2), decomp.me SSX 3 scratch from `asm/nonmatchings` (:3), `#ifdef SKIP_ASM` paste (:4-12), ninja+objdiff (:14), name back to `symbol_addrs.txt` above marker (:15-16), `configure.py -c -o` (:17), rebuild+confirm (:18-19) | Sweep→recomp→runner-refresh loop (P1) has no name-feedback step |
| Ignored artifacts | `.gitignore` (21 lines) | `asm/`, `assets/`, `undefined_*_auto.txt`, `disc/`, `venv/`, `temp_sheet.xlsx`, `objdiff.json` never committed | `$W/P1/` outside repo (same effect) |

Gaps recorded: no progress-tracking script exists under `scripts/` (only
the 2 files above; `mapfile_parser` in `requirements.txt:9` has no caller);
`extensions_path: tools/splat_ext` (`config/ssx3_us.yaml:32`) dangles
(`tools/` holds only `compdb`, `objdiff`). Pin set: `requirements.txt`
(12 lines): `splat64==0.27.0`, `spimdisasm`, `rabbitizer`, `ninja`,
`mapfile_parser`, `pandas`/`requests`/`openpyxl`, others.

## P6-5. Exact commands

From `/Users/bradrichardson/dev/ssx3` (`C="/Volumes/Extreme SSD/ssxdecomp-ssx3"`,
`W="/Volumes/Extreme SSD/ps2recomp-spike"`; reads only — no file under `C`
was created, modified, or deleted, including ExFAT `._*` sidecars):

```
git clone --depth 1 https://github.com/ssxdecomp/ssx3.git "$C"
git -C "$C" log -1 --format="REV=%H%nAD=%ad%nSUBJ=%s"
du -sh "$C"; du -sk "$C"; git -C "$C" ls-files | wc -l
ls -la "$C"; find "$C" -maxdepth 2 -iname "*licen*" -o -maxdepth 2 -iname "*copying*" -o -maxdepth 2 -iname "*copyright*"
gh api repos/ssxdecomp/ssx3 --jq '{name, license: .license, size_kb: .size, default_branch, pushed_at}'
python3 (tracked-byte sum via git ls-files -z + os.path.getsize)
cat "$C/README.md"; cat "$C/Main Workflow.txt"; ls "$C/config" "$C/scripts" "$C/tools"
cat -n "$C/config/ssx3_us.yaml"; head -30 + wc -l + marker grep on config/symbol_addrs.txt
find/grep surveys: src extensions, INCLUDE_ASM counts/files, glabel/LEAF/dlabel (0 hits),
  SKIP_ASM files, //type: counts, cpp line sizes, stub/header/distinct-line checks
cat "$C/src/readme.md"; cat "$C/src/uncollated/readme.md"; ls "$C/src" subdirs; find include/ files
grep -n "77114dfd" README.md config/ssx3_us.yaml (sha1 cites)
python3 /tmp/p6/build_names.py   # 801-row CSV build + join + ladder lookup
python3 /tmp/p6/q2_scan.py       # ELF re-hash, nearest/yaml/callers/callees
python3 (49-callee list for 0x375a08; 0x3b07b8 + 0x226970 resolutions)
python3 /tmp/p6/q3_sample.py     # 40-sample boundary classes
python3 /tmp/p6/q3_follow.py     # dup/overlap, JAL discriminator, tight pairs
python3 (full start census 618/801 + JAL split; tight census 56/106)
cat -n scripts/setup.sh scripts/spreadsheet.py requirements.txt tools/compdb
ls tools/ tools/objdiff/; git -C "$C" ls-files tools/; head -3 tools/objdiff/LICENSE
grep -n defs/mechanisms configure.py; sed -n '175,190p' configure.py
wc -l (all cited files); grep -n 0x42c1f0 sweep CSV (dup lines 9229-9230)
git add -f local/research/P6/REPORT.md local/research/P6/ssx3-decomp-names.csv
git commit -m "[P6] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

Analysis scripts live in `/tmp/p6/` (throwaway probes, not committed):
`build_names.py`, `q2_scan.py`, `q3_sample.py`, `q3_follow.py`, plus three
inline `python3 -c` probes (convention validation, callee list, censuses).

## P6-6. What I could not do

- Q1–Q4 all completed inside their caps (90/60/60/30 min) within the 4 h
  box; no partials, nothing unresolved. Time was not the limiter — decomp
  sparsity was: all 11 ladder addrs are UNNAMED and 9,270 − 618 sweep rows
  gain no name.
- "Named callers/callees" (Q2) covers direct `J`/`JAL` edges only; indirect
  (`JR`/`JALR`, vtables, callbacks, thread entries, the `0x40fc6c→0x3b07b8`
  edge) are unenumerable from names/layout, except the single P1-log edge
  cited. No decompiled body was opened to chase any edge.
- Decomp function ends exist only as next-label bounds (upper bounds outside
  the 6 split files); Q3 states both the 40-sample rate (22.5%, loose ends)
  and the tight-pair rate (52.8%, true ends) rather than merging them.
- The 25 untagged `symbol_addrs.txt` entries were included in the CSV as
  addr→name pairs (splat defines them as symbols); their func-vs-data nature
  was not verified by reading any body.
- `src/` prototype filenames (`src/readme.md`) cannot attribute any address
  to a module; module claims in P6-2 rest on yaml spans + nearest names only.
- No `git push` was run in `/Users/bradrichardson/dev/ssx3` (per the brief
  rule); the `[P6]` commit is local-only. No build, boot, emulator run,
  lease, or `adb` was used; the clone was never written to.

