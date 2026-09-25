# UP1 Part 1 report: read-only map of upstream `feature/iop-emulator` vs fork `ssx3`

Worker: Muse Code (E lane). Read-only: no builds, no fork edits, no boots.
Upstream scope: `git log --no-merges 14b1e5cb..fork/feature/iop-emulator`
(17 commits) plus the branch tip commit `39251a0` on `upstream/feature/iop-emulator`.

## 0. Topology correction (read this first)

- `fork/feature/iop-emulator` tips at `78ecbae` (09-14). It is **not**
  identical to the squash: `git diff 75d729c 78ecbae` = 31 files, +8220/−118.
- `upstream/feature/iop-emulator` tips at `39251a0` "feat: remove LLE IOPs"
  (09-19), and `git diff 75d729c 39251a0` is **empty**: the squash equals the
  upstream branch tip, not the fork snapshot.
- The upstream branch = the same 17 commits + 4 merges-from-main
  (`c09e90a`, `7159330`, `a673939`, `590b884`) + `39251a0`.
- Structural finding: most feature branches in the series forked from a
  **stale main** (pre-`#203`/pre-split). Large parts of `cc941d2`, `3e5fb2b`,
  `d91d2c1`, `4fff583`, `3b9b14c` **re-create base-era (`14b1e5cb`) state**
  our fork inherited and kept: EE scheduler + timers, SIF/IOP heap split,
  GS `gs/` split, presentation snapshot, vsync helpers, MMI `rt`, cri_dtx
  reply write, thread-info params. They read as fixes but are no-ops for us.
  Verified per item against base with `git grep <symbol> 14b1e5cb` (§2 rows).

Pins: base `14b1e5cb`, fork `ssx3` = `fb11e18`, upstream tip `39251a0` =
squash `75d729c` (tree-identical). Fork checkout `~/dev/PS2Recomp`.
Line numbers below are fork tip (`ssx3`) unless marked `base:` / `tip:`.

## 1. Map table

Class key: **HAVE** already fixed/have ours · **NEED** we have the bug ·
**N/A-SSX3** irrelevant to SSX 3 · **CONFLICT** conflicts with our design.

| # | Upstream commit / sub-item | Upstream files / functions | Fork equivalent (commit + file:line) | Class | Notes |
| --- | --- | --- | --- | --- | --- |
| 1a | `cc941d2` EE scheduler refactor (guest threads → `EeScheduler`; drops `Lifecycle.*`; rewrites Interrupt/Sync/Thread/RPC syscalls) | `ps2xRuntime/.../EeScheduler.cpp` (new), `ee_scheduler.h`, `Syscalls/*`, `ps2_runtime.cpp`, tests | base `14b1e5cb` has the scheduler; fork evolved it (E40/E55 determinism etc.). `ee_scheduler.h:263` `kEeClockHz`, `:449` pending timer IRQs, `EeScheduler.cpp:2655` `dispatchIrq(false, 9u+timer)` | HAVE | Upstream re-did base-era work on a stale branch. Fork is ahead on SSX3 specifics. Nothing to port. |
| 1b | `9f99d61` MPEG WIP fix (Code Veronica) | `Stubs/MPEG.cpp` +183/−39, `MPEG.h`, `EeScheduler.cpp`, `CD.cpp` | Fork MPEG HLE is +448/−0 vs tip (`Stubs/MPEG.cpp`), E48/E49 + `PS2X_SKIP_MOVIE` bypass | HAVE | Other-game WIP; we are ahead. No port. |
| 1c | `3e5fb2b` cheap copy from host (presentation: VRAM snapshot under lock, render on thread-local backend) + `m_presentationMutex` | `ps2_gs_gpu.cpp`, `ps2_gs_gpu.h` | base: `gs_cpu_backend.cpp` has `snapshotBackend`, `gs_frontend.h:241` `m_presentationMutex`; fork `gs_cpu_backend.cpp:1860`, `gs_frontend.cpp:778` same | HAVE | In base; kept. No port. |
| 1d | `3e5fb2b` small perf on vsync tick (debug publish every 4096 dispatches) + `eeWaitVSyncTicks` | `EeScheduler.cpp`, `ee_scheduler.h`, `ps2_runtime.cpp` | base has all three; fork `ee_scheduler.h:459`, `EeScheduler.cpp:769`, `ps2_runtime.h:417` | HAVE | In base; kept. No port. |
| 1e | `3e5fb2b` VU1 MSCAL/MSCNT use scheduler `currentContext()` for FBRST/VPU_STAT | `ps2_runtime.cpp` VU1 callbacks | base; fork `ps2_runtime.cpp:1034,1052` identical | HAVE | In base; kept. No port. |
| 1f | `d91d2c1` EE clock Hz + MPEG/CD re-sync with scheduler clock | `ee_scheduler.h`, `EeScheduler.cpp`, `Stubs/CD.cpp`, `Stubs/MPEG.cpp` | base `kEeClockHz=294912000`; fork CD/MPEG +274/+448 lines over tip | HAVE | We are ahead; tip adds 16 drift lines only. No port. |
| 1g | `f9332d6` fix lotr tests | `ps2xTest/.../ps2_sif_rpc_tests.cpp` (LOTR sound RPC scheduler harness) | — (other-game test) | N/A-SSX3 | Test-only, Lord of the Rings. No port. |
| 1h | `4fff583` fix wrong MMI translation (7× `inst.rs`→`inst.rt`: PEXEH, PREVH, PEXEW, PROT3W, PEXCH, PCPYH, PEXCW) | `ps2xRecomp/.../mmi_translation_helpers.cpp:456–579` | base has `rt`; fork `mmi_translation_helpers.cpp:455–582` all `rt` (remaining `rs`: MFHI line 252, PMTHI/PMTLO 588/594 — all correct uses) | HAVE | Never regressed in fork. (AU7's lane bugs were elsewhere.) No port. |
| 1i | `4fff583` EE timers decoder + consumer (`decodeEeTimerRegister` TIM0–3, `advanceEeTimers`, IRQ 9–12, `cyclesUntilNext…`) | `ps2_memory.{h,cpp}`, `EeScheduler.cpp`, `ee_scheduler.h` | base `#203` (`8d7e8a5`); fork `ps2_memory.cpp:533`, clocks `:288–293` identical to tip (`147456000/9216000/576000/15734`) | HAVE | Identical semantics. No port. |
| 1j | `4fff583` split SIF and IOP memory (heap `0x01A…→0x04000000–0x04500000`, `g_sifHeapStorage` backing, `is/read/write/zeroSifIopHeap` routing) | `SIF.{h,cpp}`, `Support.h`, `ps2_iop_host.cpp` | base `#203`; fork `Support.h:32` base `0x04000000`, `SIF.cpp:69,169,197,296–431` full routing | HAVE | Fully present. No port. |
| 1k | `4fff583` fix cri dtx loading (write `eeObjectAddress` reply at `commandAddress+4`) | `ps2xIOP/.../cri_dtx.cpp` | base line 1185; fork `cri_dtx.cpp:1185` identical | HAVE | Present; also moot at tip (file deleted by `39251a0`). No port. |
| 1l | `4fff583` fix thread info params (`setupCurrentThread(stack,stackSize,gp)`, main-thread stack 0 until SetupThread) | `Syscalls/System.cpp`, `EeScheduler.cpp`, `ee_scheduler.h` | base; fork `ee_scheduler.h:287`, `System.cpp:662`, `EeScheduler.cpp:1039` | HAVE | Present. No port. |
| 2 | `8b57926` revert wrong changes (un-commit 61,954-line generated `runner/register_functions.cpp`, `.gitignore` churn) | `ps2xRuntime/src/runner/register_functions.cpp`, `.gitignore` | — (our standing rule already bans generated runner code) | N/A-SSX3 | Hygiene only. No port. |
| 3 | `3b9b14c` GS architecture change (`ps2_gs_gpu.cpp`+rasterizer → `gs/` frontend/CPU-backend split) | 31 files, `gs/*` new | base already has `gs/` split; fork extended (GB2 worker/queue, G44 shadow, parallel backend) | HAVE | Base-era layout; fork ahead. No port. |
| 4a | `a293fa4` IOP emulator core (cpu/kernel/memory/rpc/module_loader/cdvd/imports/sysclib, +8k lines) + "codegen to catch callbacks on MIPS code" (`GprRegisters`, `entryPointHints`, control-flow/function emitter, config) | `ps2xIOP/src/emulator/*`, `ps2xRecomp` (`instructions.h`, `types.h`, `ps2_recompiler.cpp`, `elf_parser.cpp`, …) | Fork has **no** `ps2xIOP/src/emulator/`; HLE instead (8 modules + `plugin_loader`), AU sound HLE. `entryPointHints` ≈ our `extra_function_starts` (`games/ssx3/ssx3.toml`, E46/E56/AU3) | CONFLICT | Whole-emulator direction; we keep HLE per milestone. No port. |
| 4b | `a293fa4` Ghidra exporter gains MIPS decoder + `looksLikeCallableEntry` | `ExportPS2Functions.java` (+~350) | Fork has own E46 sweep CSV + extras; one-time artifact, game boots | N/A-SSX3 | Tooling; re-running the sweep is not planned. No port. |
| 5 | `cc9e075` analyzer constant-producing scan (replace 5-insn LUI backscan with `resolveMemoryAccessHint`/`updateConstantRegisters`) | `ps2xAnalyzer/src/elf_analyzer.cpp` (29/−45) | Fork keeps old backscan (`elf_analyzer.cpp:434–437`); **but** SSX3 `[mmio]` TOML (273 entries, `ssx3.toml:643ff`) spot-checks correct 3/3 incl. full LUI+ORI resolution the crude scan cannot produce (`0x375b84→0x1000e010` renderer init; `0x42433c→0x1000f000`; `0x4096c4→0x1000f520`, all verified with `ee-at`) | N/A-SSX3 | Producer feeds a pinned, accurate table. No failing case; improving the producer changes nothing shipped. No port. |
| 6a | `b9dba60` emulator split core/imports/services + heaplib/intrman/ioman/loadcore/stdio/sysmem/timrman/vblank + module manager + `iop_import_tests` | `ps2xIOP/src/emulator/{core,imports,services}/*`, `iop_module_manager.*` | Absent in fork (no emulator, no module manager) | CONFLICT | Same direction as 4a. No port. |
| 6b | `b9dba60` HLE module touch-ups (mcserv op-decode restructure + aliases; libsd/dbcman `moduleAliases`; tsnddrv; cri_dtx) | `ps2xIOP/src/modules/*` | Fork kept all 8 HLE modules; mcserv mappings identical (0x01/0x78→GetInfo, 0x0D/0x76→GetDir); aliases serve the module manager we lack | N/A-SSX3 | Refactor + emulator plumbing; no new SSX3-visible behavior. No port. |
| 6c | `b9dba60` `ps2_path` shared path lib | `ps2_path.{h,cpp}` (123 lines) | Absent; tip users are emulator/VFS/FileIO paths we don't have | CONFLICT | Tied to 6a/8a. No port. |
| 6d | `b9dba60` GetRomName removed from `RUNTIME_HANDLER_NAMES` (guest 0x0040B938 recompiled, not stubbed) | `ExportPS2Functions.java` (1 line) | Fork `ssx3.toml:127` pins `GetRomName@0x0040B938`; game boots as-is | N/A-SSX3 | One-time export artifact. No port. |
| 7 | `5ebc247` ELF parser callable-entry detection (prologue heuristics → reachability: `HasReachableReturnByControlFlow`, `IsConsumedAsCodePointerInControlFlow`, GPR propagation; +934/−99) | `ps2xRecomp/src/lib/elf_parser.cpp` | Fork has old `LooksLikeCallableEntry` + explicit `extra_function_starts` + `PS2X_MISSING_FUNCTION_POLICY` (E46/E56/AU3); boots to race | N/A-SSX3 | No missing-target gap on SSX3; 934-line heuristic risks false entries. No port. |
| 8a | `6560a37` memory-hint handling: **disable** MMIO override in `effectiveMemoryHintFor` ("causing issues with some games") | `instruction_translator.cpp:69` | Fork keeps override **enabled** (`instruction_translator.cpp:70–81`) + hard-codes TOML addresses in `translateMemory{Read,Write}` | N/A-SSX3 | Upstream disabled a feature we rely on; our pinned TOML samples correct. Porting = perf + regen risk for no demonstrated bug. Explicitly do **not** port. |
| 8b | `6560a37` LBU/LHU/LWU → `SET_GPR_ZE32` (+ `08dc217` macro; note `SET_GPR_U32` sign-extends despite its name) | `instruction_translator.cpp`, `ps2_runtime_macros.h:762` | **E54D** fork `1aaed05`: LWU via `SET_GPR_U64((uint64_t)(uint32_t))` (`instruction_translator.cpp:196–197`) + `ps2_lwu_tests.cpp`; LBU/LHU via `U32` on ≤16-bit values were never buggy; both preserve upper 64 via `Ps2SetGprLow64` | HAVE | Same semantics, own fix + own test. No port. |
| 8c | `6560a37` entry discovery (seed entries, section-end clamp, synthesize standalone configured entries) | `ps2_recompiler.cpp` (+98/−30) | Fork has own discovery (`discoverAdditionalEntryPointsImpl`, T5 `1a76df4` materialized-pointer entries) + explicit extras; lacks only the extension that decodes previously-skipped entries | N/A-SSX3 | No dropped-entry evidence on SSX3; tied to `entryPointHints`/callback flow (4a). No port. |
| 9 | `08dc217` `SET_GPR_ZE32` macro (definition only; users came in `6560a37`) | `ps2_runtime_macros.h` (+11) | See 8b (E54D equivalent) | HAVE | No port. |
| 10a | `c8c8666` VFS + ROM device + FileIO rewrite (fd table → `PS2Vfs` mounts + `PS2RomDevice` profiles) | `ps2_vfs.{h,cpp}` (new, 312), `ps2_rom_device.{h,cpp}` (new), `FileIO.cpp` (62/−162) | Absent in fork; our FileIO path works (boots, E55D14 GetDir) | CONFLICT | Large refactor of working code; no SSX3 file-I/O gap. No port. |
| 10b | `c8c8666` IOP host adapter refactor (serve emulator/VFS memory management) | `ps2_iop_host.{cpp,h}`, `ps2_memory.cpp` | Fork adapter serves HLE (`SIF.cpp` routing, §1j); tip serves emulator | CONFLICT | Wrong direction for us. No port. |
| 10c | `c8c8666` VIF1 GIF image packets (`gifImageQwcFromTag` → `pendingGifImageQwc`: walk **all** DIRECT tags, return **pending** IMAGE qwc) | `ps2_vif1_interpreter.cpp` (±73) | Fork still has old code (`ps2_vif1_interpreter.cpp:127` + call `:737`) | **NEED** | **Rank 1.** §3. Runtime-only, no regen. Test: upstream "VIF1 DIRECT finds an image continuation after packed setup" (`2a61ba0`, `ps2_memory_tests.cpp`). |
| 11 | `2a61ba0` "a lot of tests" (+1472/−97, 12 files) | codegen (ZE32, stale-MMIO), GS CLUT/page-buffer (old-cache), IOP (ps2_path, module activation), memory (MSKPATH3/TTE/SPR/DMA + VIF1 continuation), recompiler (VU ELF, debug sections), SIF | Fork overlaps: `ps2_lwu_tests.cpp` (E54D), TTE (14 hits) + SPR tests (own names, e.g. `:2196`), MSKPATH3 tests (`:871,935`) | HAVE (mostly) | Only portable-new item is the VIF1 continuation test → folded into Rank 1. Stale-MMIO test encodes upstream's divergent consumer (8a) — not portable alone. Rest superseded/overlapping. |
| 12a | `78ecbae` fix texture caching (logical `PageId`-keyed mirror → physical `TexturePageCache`, `ReadTexture` shares swizzle with direct reads; func-ptr tables) | `gs_texture_page_cache.h` (new), `gs_cpu_backend.{h,cpp}`, `ps2_gs_memory.{h,cpp}` | Fork CPU backend has **no** texture cache: direct `ReadVramUnlocked` reads (`gs_cpu_backend.cpp:631,646`), "coherent with local memory" | N/A-SSX3 | The bug (stale logical-page mirror) cannot exist in our backend. G46(b) artifacts are wrong stream bytes *upstream* of sampling, not sampler caching. No port. |
| 12b | `78ecbae` `ps2xTest/gs_cache/*` (fixture + texture/CLUT/memory-cache cases: unaligned TBP, 4 MiB wrap, page alternation, TEXFLUSH visibility) | 4 new test files + CMake | Absent; our backend API differs (worker/queue/shadow/parallel) but still exposes `WriteVram`/`ReadVram` | **NEED (tests only)** | **Rank 2.** §3. Adapt goldens to our API; locks swizzle behavior behind the G46(b) hunt. No codegen change. |
| 12c | `78ecbae` dbcman "multi version" (report 0x0310 not 0x0320 + `rpc_reply.h` + version metrics) + `iop_import_version_tests` + `iop_compatibility_tests` | `ps2xIOP/.../dbcman.cpp`, `rpc_reply.h` (new), tests | Fork reports `0x0320` (`dbcman.cpp:15`); no SSX3 DBCMAN-version case known | N/A-SSX3 | Other-game WIP ("wip multi version"). No port. |
| 13 | `39251a0` remove LLE IOPs (delete cri_dtx/tsnddrv/sdrdrv/clfile/sound_update_stub/plugin_loader/builtin_profiles + 2.3k test lines; tip == squash) | 31 files, +118/−8220 | Fork keeps the HLE system (AU sound HLE) | CONFLICT | Explicit design fork; we keep HLE. No port. |

## 2. Recommended ports (ranked)

### Rank 1 — VIF1 pending IMAGE continuation (`10c` + its test from `11`)

- **Value.** Directly targets the G46(b) family (wrong texture-page contents
  upstream of the GS: striped snowflakes, atlas-in-photo-panel, bars-for-glyphs;
  `local/research/G46/REPORT.md` §1) via the PATH2 IMAGE-upload path, and the
  E51 upload shortfall mechanism (uploads misplaced/truncated, not just missing).
- **Failing case (stated).** VIF1 DIRECT packet whose GIF stream is
  `[PACKED setup tag(s)] … [IMAGE tag, NLOOP=N]` with the IMAGE payload
  overrunning the end of the DIRECT packet. Expected (HW/upstream): the
  interpreter continues feeding the next `pendingGifImageQwc` quadwords as
  IMAGE payload on PATH2. Ours (`gifImageQwcFromTag` reads only tag 0):
  tag 0 PACKED → returns 0 → continuation bytes are parsed as new VIF/GIF
  commands → texture bytes dropped or misrouted into wrong pages.
  Single-IMAGE-tag packets behave identically before/after (verified by
  reading both functions), so the port is a strict improvement.
- **Smallest port.** Replace `gifImageQwcFromTag` with `pendingGifImageQwc`
  + 6-line call-site update in `ps2_vif1_interpreter.cpp` (~65 lines,
  `c8c8666`), plus upstream's `tc.Run("VIF1 DIRECT finds an image
  continuation after packed setup", …)` from `2a61ba0` (`ps2_memory_tests.cpp`).
- **Proof.** New test fails before (returns 0 continuation), passes after.
- **Codegen impact.** None (runtime interpreter only) — no regen, no boot
  strictly required; an I26-FAST boot comparing texture-upload counters would
  strengthen it.

### Rank 2 — `gs_cache` swizzle goldens adapted to our CPU backend (`12b`, tests only)

- **Value.** Locks VRAM swizzle/page behavior (unaligned TBP, 4 MiB wrap
  carry, page alternation, TEXFLUSH visibility, CSM1 CLUT) that menu/race
  rendering depends on; regression net for G-lane backend work.
- **Smallest port.** Adapt `BackendFixture` (`gs_test_support.h`) to our
  `GSCpuBackend` API and import the case list; no shipped-code change.
- **Proof.** Suite passes; each case guards a documented address behavior.
- **Codegen impact.** None. Effort unmeasured (fixture API differs) — the
  only cost; no runtime risk.

### Not recommended (explicit)

- MMIO consumer disable (`8a`) + stale-MMIO test: no wrong `[mmio]` entry
  demonstrated (3/3 sampled correct); would need regen + perf validation.
- ELF heuristics (`7`), entry synthesis (`8c`), analyzer scan (`5`): no SSX3
  gap; our explicit lists + policy work.
- VFS/ROM (`10a`), IOP emulator + module manager + ps2_path (`4a/6a/6c`),
  host-adapter refactor (`10b`), LLE removal (`13`): wrong direction (HLE kept).
- Texture-cache runtime fix (`12a`): nothing to fix (no cache in fork).
- dbcman version (`12c`), lotr tests (`1g`), revert (`2`), MPEG/CD (`1b/1f`):
  other-game / hygiene / we-are-ahead.

## 3. Gaps

1. `[mmio]` table: 270/273 entries not individually verified (3/3 sampled
   correct, incl. two needing full LUI+ORI resolution). A scripted audit
   (simulate constant chains per entry) is possible follow-up; not a port.
2. Whether SSX3 menu/race traffic actually contains multi-tag DIRECT packets
   with IMAGE continuations (the Rank 1 trigger) is not confirmed from
   traces — G46(b) fits but does not prove it. The port is still safe
   (single-tag behavior identical by inspection).
3. Rank 2 adaptation effort unmeasured (Part 1 allows no builds).
4. `ee-label`/`ee-func` used for the two named SSX3 sites (`0x375b84` in
   renderer init `sub_00375A08`; `0x42433c`, `0x4096c4` verified by address
   only); nothing named that `ee-label` calls unknown.
5. Upstream `main` may have moved after the read-only fetch at Part 1 start;
   pins above are what was mapped.

## 4. Receipts (Part 1)

- Commands (all read-only; run in `~/dev/PS2Recomp` unless noted):
  `git fetch upstream` (read-only); `git log --no-merges --reverse
  14b1e5cb..fork/feature/iop-emulator`; per-commit `git diff <c>^ <c>
  [--stat] [-- <paths>]`; `git show <rev>:<path>`; `git grep <sym> <rev>`;
  `git diff 75d729c 39251a0` (empty); `git diff 75d729c 78ecbae` (+8220/−118);
  `git diff --stat ssx3 39251a0 -- <subsystem>`; `grep` over pinned
  `~/dev/ssx3-work/codegen-ssx3` (pre-generated dir, not a build);
  `local/tooling/ee/{ee-at,ee-func,ee-label}`.
- Scratch: `~/dev/ssx3-work/UP1/{commits.txt,diffstats.txt,namestat.txt}`
  (commit/file lists only).

## Orchestrator gate, Part 1 (2026-09-24)

**A.** Read the whole map. Spot-checked the Rank 1 claim in fork `fb11e18`:
`ps2_vif1_interpreter.cpp:127` `gifImageQwcFromTag` reads only the first GIF tag, and the DIRECT
handler (`:737`) records a pending PATH2 IMAGE continuation only when that first tag is IMAGE; a
PACKED setup tag followed by an overrunning IMAGE tag loses the continuation. Upstream `c8c8666`'s
`pendingGifImageQwc` walks all tags. Accepted: Rank 1 (runtime-only port + upstream test), Rank 2
(gs_cache goldens, tests only) if it fits. Not porting the MMIO disable, ELF/entry heuristics,
VFS/IOP emulator or LLE removal (HLE kept). Upstream's MMI fix and texture-cache fix don't apply
(present at base / no cache in our backend). Part 2 released with an observable: E51 measured ~60
IMAGE uploads/vsync here vs 73–74 in PCSX2 at a matched scene.

---

# UP1 Part 2: Rank 1 port + I26-FAST before/after (2026-09-24)

Worktree `~/dev/ssx3-work/UP1/PS2Recomp`, branch `up1-ports` from fork
`ssx3` `fb11e18`. Build `~/dev/ssx3-work/UP1/build`: Release, ninja,
`PS2X_ENABLE_DIAG_TAPS=OFF`, canonical
`PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3` (no regen; port is
runtime-only). No push anywhere.

## Port

- Commit `cab22bd6121928428989bc16e6ee9a09c82b50cb`
  `[UP1-R1] Port VIF1 pending IMAGE continuation from upstream c8c8666`
  (2 files, +98/−15): `pendingGifImageQwc` replaces `gifImageQwcFromTag`
  in `ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp`; test
  `VIF1 DIRECT finds an image continuation after packed setup` from
  upstream `2a61ba0` added verbatim to `ps2xTest/src/ps2_memory_tests.cpp`
  next to its single-tag companion.
- Fail-before: suite from worktree root 593 pass + 1 fail (only the new
  test; `suite-before.log`). Pass-after: **594/594** (`suite-after.log`).
  (First run from `build/` also failed `VU0 macro mappings` on CWD —
  `"instructions.h should be readable from the test working directory"`;
  from the worktree root it passes. No product relevance.)
- Runner-dir check empty:
  `git diff --stat 14b1e5cb up1-ports -- ps2xRuntime/src/runner` → no output.

## Boots (I26-FAST, `PS2X_DETERMINISTIC=1`, `PS2X_PKLOG=1`, gfx-stats 600–1900, tick frames)

Valid pair (route as released): `up1b` = pre-fix runner, `up1a` = post-fix
runner, 480 s wall each, slot 1, rc 0, lease released. Race HUD reached;
tick 1780 = race (2ND/2, timer running). Frames:
`frames/up1{b,a}-{charselect-820,race-1780}.png` (+ `.txt` sidecars with
tick/fnv). Before/after PNGs are MD5-identical
(`5ab5e8d0…` char-select, `8fffd048…` race).

### Observable: per-vsync packet census, valid pair (from `ps2_pklog.txt`)

| Window (ticks) | src | n/vsync before → after | KB/vsync before → after |
| --- | --- | --- | --- |
| menus-title 600–760 | 1 / 2 / 3 | 84.57 / 42.17 / 1.55 → same | 17.18 / 9.70 / 178.12 → same |
| char-select 880–990 | 1 / 2 / 3 | 314.76 / 77.04 / 2.14 → same | 192.22 / 16.91 / 325.17 → same |
| peak/mode/event 1000–1440 | 1 / 2 / 3 | 75.29 / 59.45 / 2.20 → same | 15.29 / 13.16 / 334.99 → same |
| loading/card 1441–1708 | 1 / 2 / 3 | 593.28 / 81.18 / 1.70 → same | 594.65 / 10.56 / 117.86 → same |
| race-start 1709–1900 | 1 / 2 / 3 | 1206.15 / 167.83 / 2.39 → same | 1252.58 / 9.83 / 273.31 → same |

`cmp` on full pklogs (1,989,672 packets each, ticks 0–~2861, 2M-line cap):
**byte-identical**. gfx-stats files: **identical**. Frames: identical.
**On the true I26-FAST path the fix is a behavior-preserving no-op through
tick ~2861: no regression, and no measurable upload change in these windows.**

Caveat on the brief's letter: pklog labels path (`1/2/3/img/packed`), not
GIF mode, and the P6 native path (`img`) never fires on this route, so a
literal "IMAGE transfers per vsync" count is not available from the in-ssx3
capture (E51's `PS2X_GIF_DUMP` commit `0af7eed` is not in `ssx3`; PKCAP caps
at 64 packets). Closest reported signals: PATH2 packets+bytes/vsync (VIF1
DIRECT, the fix's path) and bulk PATH3 transfers above.

### The trigger exists in real SSX3 traffic (stim pair)

The first boot pair (`up1before`/`up1after`, same inputs) ran with pad-stim
accidentally left armed (my wrapper missed the `--no-stim` that
`e46_boot.py`/`i26_boot.py` force-append; stim holds all buttons after wall
60 s, so card taps failed and the route derailed — those runs are NOT
I26-FAST and carry no race frames). Their comparison still proved the
mechanism live:

- Streams bit-identical through tick 1605 (determinism harness rigorous).
- First divergence tick 1606 (loading screen): PATH1 packet **bytes**
  diverge (~99% fnv mismatch) while counts and PATH2/3 stay identical.
- `xgkick == p1_pkt` (PATH1 is VU1 XGKICK output): VU1 ran −703 cycles at
  1606 with equal MSCAL counts; draws +6/verts +18 by 1608; sub-pixel box
  shifts. Before-fix, overrun bytes decoded as VIF commands issued spurious
  VU1 work and corrupted VU1 state (fewer draws); after-fix they are
  consumed as IMAGE. PATH2 (guest-RDRAM passthrough) identical ⇒ guest
  logic path unchanged — pure rendering-correctness delta, no guest
  divergence.
- Part 1 gap closed: the multi-tag DIRECT + IMAGE-overrun trigger fires in
  real game traffic (it just does not fire on the I26-FAST menus/race-start
  windows measured).

## Budget and gaps

- Executed: 2 full builds + 2 incremental runner relinks (pre/post-fix swap
  for boot purity), 4 boot executions (2 invalid stim runs from the setup
  error above + the 2 valid measurement boots). No regen (runtime-only).
- Rank 2 (gs_cache goldens) NOT done: no 45 min remained after the redo.
  Gap, as the release allows.
- Literal IMAGE-mode/vsync census needs GIF-tag parsing of a byte capture;
  not available in-ssx3 (see caveat). A future lane could revive the E51
  GIF-dump approach on a diagnostics branch (not on the port branch).
- Scratch (not committed): `~/dev/ssx3-work/UP1/{build,build*.log,
  suite-*.log,run-*,up1_boot.{py,sh},up1_census.py,commits.txt,diffstats.txt,
  namestat.txt}`; worktree branch `up1-ports` (local, no push).
