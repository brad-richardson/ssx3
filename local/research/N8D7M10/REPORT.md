# N8D7M10 — same-stream Odin offline replay feasibility (read-only)

**State: design COMPLETE, verdict B. Read-only: no source edit, build,
replay, boot, Odin/device/lease action, stream copy, push, board/global
edit, or upstream contact. No Turnip/shader/barrier/driver cause is
claimed. The orchestrator gates any implementation or Odin run. Cited
source strings cannot prove Android runtime behavior; the checker
verifies pins, cited rows, and table invariants only.**

Brief: `local/muse/prompts/N8D7M10.md`. Question: can the existing
Android app/test build path replay the exact N8D7M6 captured stream on
the Odin with paraLLEl/Turnip but without live EE→GS scheduling, and
collect the same tick2050 selected 4 MiB snapshot + 448-tile census?

Facts to start from: the one closed stream is N8D7M6 SHA
`f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593`,
1,100,696,462 B, `PS2XGSC1`, 862,958 packets / 11,499 priv / 25,445
transfers / 2,050 markers / 0 readbacks / 0 clears, EOF marker tick 2050
(N8D7M6 REPORT §2, ORCH-GATE). Mac paraLLEl replay of those exact bytes:
selected input/oracle 300/448 active; live Odin 23/448; all 11
descriptor fields equal (N8D7M6 REPORT §§3–4, ORCH-GATE verdict A).
N8D7M8 verdict B: no nonperturbing tap on the original Present order
separates late writes from absent writes (ORCH-GATE). N8D7M9 verdict B:
identity can be carried to record/submit but per-draw completion is
unattributed (ORCH-GATE). The Android vehicle is the N8D7M1 APK
`e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1`,
153,736,732 B, arm64 runner + Turnip + HAL shim (N8D7M1 REPORT §§1–4,
ORCH-GATE PASS for package contents only).

LSP hover was attempted on the pinned fork and returned no results (no
LSP server for this file type — same basis as N8D7M7 REPORT §1, N8D7M8
§2); every code link below rests on direct source reads at the pinned
revs.

## 1. Pins read in this design

| Item | Pin |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7L/PS2Recomp`, branch `n8d7l-oracle`, HEAD `a8cfefad109134767b0810b7707b4b58a5dfcca7` |
| Parallel-GS worktree | `~/dev/ssx3-work/N8D7F/parallel-gs`, HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` |
| Reference stream | N8D7M6 `n8d7m6.gs`, SHA `f6a78f71…a593`, 1,100,696,462 B |
| Mac replay binary | N8D7M5 `ps2x_tests` (N8D7M6 REPORT §3 cites `d06ff1aa…0b77f`; accept.py `BIN = …/N8D7M5/build/ps2xTest/ps2x_tests`) |
| Android APK | N8D7M1 `e077bef8…758a1`, 153,736,732 B; arm64 runner `f3de999a…81e3c1bf`; Turnip `717812c3…1ac29d`; HAL `1b49d27c…fc387` |
| Repo HEAD (receipts only) | read at commit time by `check.py` (not pinned here) |

## 2. Build/entrypoint/path table

Mac replay chain (exists, gated in N8D7M6):

| # | Stage | Code site (pinned rev) | Fact |
| --- | --- | --- | --- |
| R1 | CMake target | `ps2xTest/CMakeLists.txt:154` (`add_executable(ps2x_tests …)`); linked `ps2_test_lib` + `ps2_runtime` (`:173-178`) | Desktop `ps2x_tests` is a real executable target; suite entry `main.cpp` registers `register_ps2_gs_replay_tests()` (`main.cpp:19,68`) |
| R2 | Replay entrypoint | `ps2xTest/src/ps2_gs_replay_tests.cpp:145` (`replay(TestCase &t)`), dispatched `:693-719` (`MiniTest::Case("PS2GSReplay"…)`) | Reads `PS2X_GS_REPLAY_CAPTURE`, checks `PS2XGSC1` magic (`:157-166`) |
| R3 | Backend creation | same file `:217-225`: `PS2X_GS_REPLAY_BACKEND=parallel` → `ps2x_gs_parallel::available()` gate → `gs.setRasterBackend(ps2x_gs_parallel::create(&regs))`; `available()` true iff `PS2X_HAS_PARALLEL_SHADOW` (`ps2_gs_parallel_backend.cpp:1028-1034`); `create()` returns `GSParallelBackend` iff same guard (`:1046-1052`) | Same `GSParallelBackend` class serves Mac replay and the live device path |
| R4 | Stream parser | same file `:145-360`: magic, path bytes, priv/transfer/marker records; optional `PS2X_GS_REPLAY_PATH_FILE` override (`:184-202`); `PS2X_GS_REPLAY_STEP` stride (`:203-208`); per-tick presents; summary `:640-648` | N8D7M6 Mac run: `mode=queue backend=parallel`, counts identical to capture (`mac-parallel.log:78300`) |
| R5 | Selected-capture env | `ps2_gs_parallel_backend.cpp:439-446`: `selectedRequested` iff `request.vsyncTick==2050` and `PS2X_N8D7F_SELECTED_CAPTURE==1`; N8D7M6 Mac env adds `PS2X_N8D7F_SELECTED_CAPTURE=1` + `PS2X_N8D7L_ORACLE=1` + `PS2X_N8D5_TILE_CAPTURE=1` (accept.py `:240-248`, N8D7M6 REPORT §3) | Tick-gated (`==2050`), default off |
| R6 | Snapshot decoder | same file `:64-156` (`selectedTileCounts`, `selectedDecode`), `:190-222` (`oracleDecodeCensus`); host map + decode `:621-729` (SHAs, 448-vectors, `input_circuit_equal`, `oracle_input_equal`, 8 controls) | Shared by Mac replay and live device Present: Mac `[n8d7f] … active=300` (`mac-parallel.log:78287`), Odin active 23 (N8D7M6 `result.json`) |

Android chain (exists) and the replay gap:

| # | Stage | Code site (pinned rev) | Fact |
| --- | --- | --- | --- |
| A1 | Android native target | `ps2xRuntime/CMakeLists.txt:579-585` (`ps2EntryRunner` SHARED on Android, `ANativeActivity_onCreate` undefined ref) | Device native code is a shared library, not an executable |
| A2 | App entrypoint | `android/app/src/main/AndroidManifest.xml`: `android.app.NativeActivity`, `android.app.lib_name = ps2EntryRunner`, no `uses-permission` element | Sole launch path is the activity intent; manifest declares zero permissions |
| A3 | Env/loader | `ps2xRuntime/src/lib/ps2_android_runtime.cpp:13-36`: reads `<files dir>/ps2x.env` (`KEY=VALUE`, `#` comments) via `PS2X_DEFAULT_BOOT_ELF`-derived path, `setenv` per entry | N8D7M6 live run drove all env (incl. `PS2X_GS_CAPTURE`, `PS2X_GS_TURNIP=1`, selected/oracle flags) through `ps2x.env` (launch.py `:573-580`) |
| A4 | Test build disabled | `android/app/build.gradle:31` (`-DPS2X_BUILD_TEST=OFF`); `ps2xEntryRunner` links only `ps2_runtime` (+ game objects) (`ps2xRuntime/CMakeLists.txt:635-639`); `PS2X_GS_REPLAY_*` readers exist only in `ps2xTest/src/ps2_gs_replay_tests.cpp` (zero hits under `ps2xRuntime/` except a comment in `gs_cpu_backend.h`) | **No replay parser, no replay driver, no `PS2X_GS_REPLAY_CAPTURE` reader is linked into the APK** |
| A5 | APK members | N8D7M1 `mac-apk-gate.json`: exactly `lib/arm64-v8a/libps2EntryRunner.so`, `libvulkan_freedreno.so` (Turnip), `libhardware.so` (HAL shim); arm64-v8a only (`build.gradle:47`) | No headless executable, no `ps2x_tests`, no x86 member |
| A6 | Turnip bundle | `ps2_gs_parallel_backend.cpp:324` (`dlopen("libvulkan_freedreno.so")`), `:923-931` (`GRANITE_VULKAN_LIBRARY` log, `PS2X_GS_TURNIP=1` request); N8D7M1 pins Turnip `717812c3…1ac29d` via `-Pps2xJniLibsDir` (build.sh) | Turnip ships in-APK as a jniLibs member; requested at runtime by env, not by manifest |
| A7 | Capture side | `ps2xRuntime/src/lib/gs/gs_stream_capture.cpp:27-40` (`PS2X_GS_CAPTURE` path, `PS2XGSC1` magic), `:138-147` (`PS2X_GS_CAPTURE_STOP_TICK`), `:246-276` (stop-at-marker, closed-bytes log) | The app can *write* a stream; nothing in the app can *read* one back |

Stream-closure and path-identity checks (this design, from receipts):

| Check | Evidence | Result |
| --- | --- | --- |
| Closed stream | N8D7M6 ORCH-GATE: EOF marker tick 2050; `comparison.json` `last=[4,2050]`; capture `closed bytes=1100696462` (result.json stop_marker); Mac `GB4_REPLAY_SUMMARY … markers=2050` (`mac-parallel.log:78300`) | PASS: complete tick2050 stream, both ends agree |
| Path sidecar identity | Capture writes per-packet path byte (`gs_stream_capture.cpp:153-158`); replay uses recorded paths unless `PS2X_GS_REPLAY_PATH_FILE` overrides (`ps2_gs_replay_tests.cpp:184-202`); N8D7M6 accept.py env (`:240-248`) sets no `PATH_FILE` | PASS: recorded EE paths preserved end to end, no override in the gated run |
| 11-field descriptor | `comparison.json` `same_descriptor=true`; N8D7M6 REPORT §3 (Mac metadata byte-equal to Odin) | PASS (input precondition for any future comparison) |

Headless on-device executable or app replay mode: **none exists**.
The APK's only native entry is the NativeActivity library (A1/A2/A5);
the only stream-replay implementation is desktop `ps2x_tests` (R1/R2),
which the Android build explicitly excludes (A4). Do not assume desktop
tests run on Android: `ps2x_tests` is an x86-64/Mac Mach-O (or
Linux/Windows per host) binary linking host Vulkan/Granite and the
desktop test harness — no arm64 build, no `main()` entry, and no
`PS2X_GS_REPLAY_*` handling exist anywhere in the shipped package.

## 3. Predeclared future same-stream comparison (conditional, not run)

Conditional on a faithful replay harness AND identical 11-field
descriptor/input byte hash. Active = 448-tile active count; sparse
≤100, broad ≥250 (N8D7M6 §4):

| Branch | Predeclared requirement | What it would make a lead (not a proved cause) | What it cannot conclude |
| --- | --- | --- | --- |
| (i) Odin offline replay broad ≥250/448, near Mac 300 | Same `f6a78f71…a593` bytes, same descriptor, same decoder, Mac same-binary control broad | Live-only threading/interleave or EE→GS scheduling becomes a lead | Copy timing and the exact faulty packet remain unresolved; per-draw completion still unattributed (N8D7M8 M5, N8D7M9 §4) |
| (ii) Odin offline replay sparse ≤100/448, near live 23 | Same as above | Device/backend/driver path (Turnip/Granite/Adreno execution of this stream) becomes a lead | Same: which draw/packet fails and when the copy ran relative to it remain unresolved; no Turnip/shader/barrier cause claimed |
| (iii) 101–249, descriptor/input/hash/path mismatch, or replay-harness difference | Any | OTHER: no award to either branch | Nothing: the run is void as a same-stream comparison; diagnose the harness/descriptor first |

Both live branches require a Mac same-binary control (same stream,
same decoder rev) and a viewed Odin frame. No speed number comes from
any diagnostic replay (AGENTS.md speed rule; N8D7M6 REPORT §5).

## 4. Prospective plan (unexecuted — no harness exists, so no run is budgeted executable yet)

If a headless replay harness is built and gated, the bounded device run
would be (plan only, not executed, not authorized by this design):

```sh
# 1. Push the exact stream (verify two matching SHA reads; never copy inside git)
# adb push ~/dev/ssx3-work/N8D7M6/n8d7m6.gs \
#   /storage/emulated/0/Android/data/com.ps2x.runner/files/n8d7m6.gs
# 2. ps2x.env selects replay mode (harness-defined keys) + selected/oracle flags +
#    PS2X_GS_TURNIP=1; install APK (always install); check keyguard showing=false,
#    battery ≥20% charging, free ≥10 GiB; claim Odin lease; one launch; BACK once
#    for the USB dialog; stop at first complete tick2050 receipt+frame+closed census
# 3. Pull census + frame; force-stop app; release lease
```

Caps for that prospective run: one install, one launch, ≤600 s boot cap
(AGENTS.md boots rule); device storage ≈ 1.10 GB stream + ~5 MiB census
text + one 512×448 frame; text receipts <512 KiB (this brief's cap);
logs ≤16 MiB (N8D7M6 precedent). Quoted only if the harness path is
real — it is not (verdict B), so no device run follows from this
report.

## 5. Verdict: B — missing integration link

No realistic bounded same-stream replay path exists in the current
source/package tree: the stream parser + replay driver
(`ps2_gs_replay_tests.cpp:145-360`) is compiled only into desktop
`ps2x_tests` (A4), which the Android build disables and the APK does
not ship (A5). The app can write but not read a GS stream (A7 vs A4).

Precise missing link: an on-device replay entrypoint that (a) opens
`PS2XGSC1` bytes from the app files dir, (b) feeds them through
`GSParallelBackend` Present tick 2050 with the selected/oracle env, and
(c) emits the mapped 4 MiB snapshot census + frame — without live EE
scheduling. Smallest preparatory task (read-only design first, no
implementation authorized here): a source-grounded harness design
stating the binary form (new `main()` executable cross-compiled arm64
vs new app-mode intent flag), exact NDK link set (Granite/Turnip
loader on Android), ABI (arm64-v8a), input path + scoped-storage write
route for the 1.10 GB stream, env/permission surface, Turnip bundle
reuse, and the nonperturbation gate (OFF/ON census equality + Mac
same-binary control) — gated before any build or Odin run.

## 6. Gaps (each forces OTHER until closed)

- **G1 (harness gap):** no on-device replay entrypoint (A4/A5). Fatal to A.
- **G2 (push gap):** the 1.10 GB stream has never been staged to the Odin
  files dir; two-matching-SHA staging is unproven (no copy was made in
  this read-only part).
- **G3 (loader gap):** whether `GRANITE_VULKAN_LIBRARY` / Turnip dlopen
  resolves identically from a headless executable vs the NativeActivity
  process is unproven from source strings alone.
- **G4 (array/cost gaps inherited):** N8D7M9 G5 (prim-array bound), M4
  (Turnip timestamp support) remain open and are not needed for this
  verdict.
- **G5 (execution caveat):** per N8D7M8/N8D7M9 gates, even a faithful
  offline replay separates scheduling-class from device-class leads
  only; it never attributes per-draw completion.

## 7. Receipts / commands (all read-only, repo root unless noted)

Reads: this brief; `~/dev/AGENTS.md`; repo `AGENTS.md`;
`local/AGENTS.local.md`; N8D7M6 `REPORT.md` + `ORCH-GATE.md` +
`comparison.json` + `result.json` + `mac-parallel.log:78278-78300` +
`accept.py:50,133-140,234-276` + `launch.py:6-9,32,153-155,564-580`;
N8D7M8 `REPORT.md` + `ORCH-GATE.md`; N8D7M9 `REPORT.md` +
`ORCH-GATE.md`; N8D7M1 `REPORT.md` + `ORCH-GATE.md` + `build.sh` +
`mac-apk-gate.json`. Sources (direct reads at `a8cfefa` /
`3a66c19`): `ps2xTest/CMakeLists.txt:150-200`,
`ps2xTest/src/main.cpp:19-68`,
`ps2xTest/src/ps2_gs_replay_tests.cpp:145-260,640-719`,
`ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:64-222,286-360,439-729,923-931,1028-1052`,
`ps2xRuntime/src/lib/gs/gs_stream_capture.cpp:27-40,138-276`,
`ps2xRuntime/src/lib/ps2_android_runtime.cpp:13-39`,
`ps2xRuntime/CMakeLists.txt:485-530,579-660`,
`android/app/build.gradle:1-60`,
`android/app/src/main/AndroidManifest.xml`. One LSP hover attempt (no
server). `git rev-parse` in both worktrees for pins. New text <512 KiB
(see `check-result.json`).

(End of file)
