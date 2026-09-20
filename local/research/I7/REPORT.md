# I7 — Wire UIKit entry: SDL video init to first window (or next wall)

- Date: 2026-09-19/20. Runbook `local/muse/prompts/I7.md` (I6 gap 1's exact next brief). Tables, no verdicts.
- I6 (`local/research/I6/REPORT.md`, all of it: the `bdae295` identifier fix, install exit 0, the argv probe's `WARNING: SDL: Failed to initialize SDL` + SEGV in `rlLoadTexture`, the 6 gap rows, the standing measurement rules) read first.
- Two fork commits (both entry-only, `Orchestrated-By: Muse Code` trailer): `9c7b028` (SDL2main link + `SDL.h` include in `main.cpp`) and `2655264` (scene-manifest plist template). `9c7b028` pushed to `fork ssx3` (first try, `ls-remote` confirms); `2655264` push deferred — remote moved ahead with P-lane `2caf17c` (P1y) while measuring and `pull --rebase` refuses on P-lane's unstaged file, which this brief must not touch (exact state + retry in Step 1b).
- Product: `/Volumes/Extreme SSD/ps2x-i7/ios-runtime-rel2/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app` (binary `ps2EntryRunner`, 120337968 bytes, Mach-O 64-bit arm64). Fresh dirs; nothing reused from other briefs except read-only `-DSDL2_DIR` / `-DFETCHCONTENT_SOURCE_DIR_RAYLIB` inputs.
- Rules honored: no PS2 boots → no lease; builds `-jobs 4`; Simulator = installed iOS 27.0 runtime + existing iPhone 17 `4DE6C37C-77EF-45AE-827E-26286E68D022` only, no substitution, no downloads, booted by me (shutdown at end); build + logs under `/Volumes/Extreme SSD/ps2x-i7/` (new dir); `/tmp/p1-link`, `/tmp/ps2xgs-build*`, `/tmp/ps2x-ios-spike`, `ps2x-i3`, `ps2x-i4` (read-only inputs only), `ps2x-i5`, `ps2x-i6` (read-only), other agents' dirs never written; evidence `local/research/I7/` committed with `git add -f`, prefix `[I7]`, trailer `Orchestrated-By: Muse Code`; no `git push` in ssx3; one screenshot committed (71 KB, under the 5 MB cap).
- Outcome shape: UIKit entry wired and proven end-to-end. First wall after SDL2main: the iOS 27 sim traps in UIKit scene setup without a scene manifest (before `SDL_main` runs) — fixed in-brief as `2655264` after a probe A/B proof. With both changes: SDL video init passes, `InitWindow` completes (GL ES 2.0, shaders, default font), first window photographed (black, foreground). Next wall: `PS2Runtime::initialize` aborts in `InitAudioDevice` (CoreAudio `AURemoteIO::Initialize` RPC timeout → deliberate `abort()`); `loadELF` still never ran. SDL audio itself works on this sim (probe C).

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i7/`, `APP1` = build-1 `.app` (rel), `APP2` = build-2 `.app` (rel2), `UDID` = `4DE6C37C-77EF-45AE-827E-26286E68D022`, `FORK` = fork clone, `SDLPRE` = `/Volumes/Extreme SSD/ps2x-i4/sdl2-ios-sim`.

## Step 1 — Wire UIKit entry (commit 1: SDL2main)

Choice: link `SDL2::SDL2main` + `#include <SDL2/SDL.h>` in `main.cpp` under `TARGET_OS_IPHONE`. This is SDL's documented iOS bootstrap: SDL2main provides the real `main()` (UIKit app delegate + runloop) and `SDL_main.h` renames our `main` to `SDL_main`.

| Item | Receipt |
|---|---|
| Why not manual `UIApplicationMain` | Re-implements `SDL_uikitappdelegate.m` (event pump, orientation, lifecycle); SDL2main already ships and maintains it |
| Why not direct `SDL_UIKitRunApp` from plain `main` | Bypasses SDL2main's argv/setup; non-idiomatic; SDL docs prescribe SDL2main for iOS |
| Rename chain verified (simulator) | Compiler predefines `TARGET_OS_IPHONE=1` (both Xcode and Homebrew clang, sim and device, `-dM` receipt in report pedigree); `SDL.h` → `SDL_main.h` → `SDL_stdinc.h` → `SDL_config.h` → `SDL_platform.h` defines `__IPHONEOS__=1` from it → `SDL_MAIN_NEEDED` → `#define main SDL_main` (`SDLPRE/include/SDL2/` line refs in Exact commands) |
| C linkage | `SDL_main.h` declares `SDL_main` inside `extern "C"` before our definition, so the renamed definition keeps C linkage and resolves SDL2main's reference |
| Include dirs | `SDL2::SDL2main` carries `INTERFACE_INCLUDE_DIRECTORIES`; no extra include path needed |
| Own `find_package` | raylib's is scoped to its FetchContent subdir (imported targets are not global); ours re-reads the same `SDL2_DIR` config in our scope. `SDL2_DIR` guaranteed set by the I4 `FATAL_ERROR` above |
| Only SDL2main linked | `libSDL2.a` already links via raylib (`PLATFORM SDL`; I6 `nm` showed 292 SDL symbols); only the entry object was missing |
| Unity-build containment | Trailing `#undef main` under the same guard keeps the rename inside `main.cpp`'s TU. Measured: no `src/runner/*.cpp` TU uses the identifier `main` today (grep receipt); the `#undef` is insurance while P-lane edits `src/runner/` |
| Desktop-inert | `TARGET_OS_IPHONE=0` on macOS (no include/rename); CMake link gated on `PS2X_IS_IOS` (OFF on Darwin) |

```diff
# ps2xRuntime/CMakeLists.txt (inside the existing if(PS2X_IS_IOS) block)
+    find_package(SDL2 REQUIRED)
+    target_link_libraries(ps2EntryRunner PRIVATE SDL2::SDL2main)
# ps2xRuntime/src/main.cpp (after the __ANDROID__ include block)
+#if defined(__APPLE__)
+#include <TargetConditionals.h>
+// I7: ... (comment, see commit)
+#if TARGET_OS_IPHONE
+#include <SDL2/SDL.h>
+#endif
+#endif
# ps2xRuntime/src/main.cpp (end of file)
+#if defined(__APPLE__)
+#if TARGET_OS_IPHONE
+#undef main
+#endif
+#endif
```

| Item | Receipt |
|---|---|
| Diff | 2 files, 33 insertions, 0 deletions: `ps2xRuntime/CMakeLists.txt` (+10), `ps2xRuntime/src/main.cpp` (+23) |
| Staged | Those 2 NAMED files only (`git add` with paths); P-lane `register_functions.cpp` stayed `M` (unstaged) throughout, never staged |
| Commit | `9c7b028` `Entry: wire UIKit bootstrap via SDL2main for iOS sim (I7)` + body + `Orchestrated-By: Muse Code` (`logs/fork-commit.log`) |
| P-lane motion during step | HEAD moved `5b5ac3d` → `ed387c7` (P24-2) between my first status check and my commit; my commit sits on `ed387c7` |
| Pull --rebase | Attempted; refused (`cannot pull with rebase: You have unstaged changes` — P-lane's file). Proven no-op instead: fresh `fetch fork ssx3`, `fork/ssx3` ancestor of HEAD, `HEAD..fork/ssx3` empty (remote strictly behind) |
| Push | `git push fork ssx3` → `ed387c7..9c7b028`, first try; `ls-remote` confirms `9c7b028` (`logs/fork-push.log`). ONLY in the fork clone to the `fork` remote |

## Step 1b — Scene manifest (commit 2, same brief)

Why a second change in this brief: after commit 1, BOTH launch shapes trap in UIKit scene setup before `SDL_main` runs (Step 3a), making the runbook's own Step 3 questions ("does SDL video init pass now?") unanswerable — our code never executes. A minimal probe pair (Step 3b, scratch only, no fork touch) proved the cause is the missing `UIApplicationSceneManifest` and the exact minimal fix. The manifest is therefore a prerequisite of "wire UIKit entry", inside the same entry-only discipline (PS2X_IS_IOS CMake block + one new entry file), so it was implemented, committed, rebuilt, and re-measured in this box rather than deferred.

| Item | Receipt |
|---|---|
| Template | New `ps2xRuntime/ios/Info.plist` (mirrors the `ps2xRuntime/vita/` platform-dir pattern): verbatim copy of CMake's generated `ps2xRuntime/CMakeFiles/ps2EntryRunner.dir/Info.plist` (14 keys, `$(EXECUTABLE_NAME)` + hardcoded identifier kept) + the probe-B-proven manifest (`UIApplicationSupportsMultipleScenes=false`, `UISceneConfigurations/UIWindowSceneSessionRoleApplication/Default`, NO scene delegate class). `plutil -lint`: OK |
| CMake | `MACOSX_BUNDLE_INFO_PLIST` pointed at the template in the PS2X_IS_IOS block. Configure receipt: rel2's generated `Info.plist` = our template (comment + manifest present, identifier intact; diff in Step 2b) |
| Not added | `UIApplicationSupportsIndirectInputEvents` (probe logs note it for mouse support; informational only — no behavioral need observed) and `UISceneDelegateClassName` (probe B proves the no-delegate shape works; no deviation from the proven shape) |
| Diff | 2 files, 68 insertions, 0 deletions: `ps2xRuntime/CMakeLists.txt` (+11), `ps2xRuntime/ios/Info.plist` (+57, new) |
| Staged | Those 2 NAMED files only; the `._Info.plist` AppleDouble sidecar on the ExFAT volume was NOT staged (staged-name list verified pre-commit); P-lane file never staged |
| Commit | `2655264` `Entry: add iOS scene manifest so UIKit entry reaches SDL_main (I7b)` + body + `Orchestrated-By: Muse Code` (`logs/fork-commit2.log`) |
| Push | DEFERRED, not failed-open: between commit and push, P-lane pushed `2caf17c` (P1y test) to `fork/ssx3`; `git push fork ssx3` rejected (non-fast-forward, `logs/fork-push2.log`); `pull --rebase` refuses on P-lane's still-unstaged `register_functions.cpp` (retried at end of brief, same refusal). No force-push (would destroy `2caf17c`), no stash/autostash (would touch a concurrently-written P-lane file). Retry when P-lane's tree is clean: `git -C FORK pull --rebase fork ssx3` (replays only `2655264` onto `2caf17c`) then `git -C FORK push fork ssx3`. All Step 2b/3c measurements below were built from the `2655264` tree |

## Step 2 — Rebuilds (two fresh dirs)

Same I6 configure shape, fresh `W/ios-runtime-rel` (commit-1 tree) and `W/ios-runtime-rel2` (commit-2 tree): `-G Xcode`, I1 `ios-simulator.toolchain.v2.cmake`, `CMAKE_CONFIGURATION_TYPES=Release`, `RECOMP/ANALYZER/TEST/STUDIO OFF`, `SCCACHE OFF`, `-DSDL2_DIR=SDLPRE/lib/cmake/SDL2`, `-DFETCHCONTENT_SOURCE_DIR_RAYLIB=W-i4/raylib-5.5`. Env `CC=/opt/homebrew/opt/llvm/bin/clang`, `CXX` unset. Build `--config Release -- -jobs 4`. Both trees include P-lane's committed P24-1/P24-2 plus their unstaged `register_functions.cpp` WIP (398775 lines at final check), as in I6.

### Build 1 (rel, commit-1 tree)

| Item | Receipt |
|---|---|
| Configure | Exit 0: `Configuring done (73.9s) / Generating done (18.5s)` (`logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, 9m19s wall (20:56:22→21:05:41) (`logs/ios-runtime-build-tail.log`; full 1.0 MB log stays in `W/logs/`) |
| Binary | 120337968 bytes (I6: 120264208, +73760 — SDL2main + P-lane P24 content), Mach-O 64-bit arm64 |
| Entry symbols | `T _SDL_main` (our renamed main), `T _SDL_Init`, `T _InitWindow` present; `T _SDL_UIKitRunApp` NEW (pulled from libSDL2.a by SDL2main's reference); `_main` present as LOCAL `t _main` at `0x10632e1c0` (`logs/nm-entry.log`) |
| LC_MAIN | `entryoff 103997888` = `0x632E1C0` → entry VM `0x10632E1C0` = SDL2main's `_main` exactly. (Local visibility is SDL's `-fvisibility=hidden` on SDL2main; LC_MAIN is authoritative for launch, not symbol visibility.) |
| `U _UIApplicationMain` | Undefined → UIKit framework (called by SDL's delegate) |
| SDL count | 296 `T _SDL_` symbols (I6: 292; delta includes `_SDL_main`, `_SDL_UIKitRunApp`, `_SDL_iPhoneSetEventPump`) (`logs/nm-sdl-count.log`) |
| Link set | Unchanged shape vs I6 (libSystem + SDL iOS frameworks) (`logs/otool-L.log`) |
| Signature | Adhoc, `TeamIdentifier=not set`; `Identifier=org.ps2x.ps2entryrunner` (`logs/codesign.log`) |
| `Info.plist` | 20 keys, `CFBundleIdentifier=org.ps2x.ps2entryrunner`, NO scene manifest (`logs/Info.plist.txt`) |
| Warnings | 81 total, 19 unique — same counts as I6; bundle-identifier/`PRODUCT_BUNDLE_IDENTIFIER` warning still present (1×); rest untriaged (`logs/warnings-uniq.log`) |

### Build 2 (rel2, commit-2 tree)

| Item | Receipt |
|---|---|
| Configure | Exit 0: `Configuring done (66.9s) / Generating done (20.0s)` (`logs/ios-runtime-configure2.log`, full). Generated template now = our template (I7 comment + manifest; identifier intact) |
| Build | Exit 0, `BUILD SUCCEEDED`, 5m10s wall (21:20:11→21:25:21) (`logs/ios-runtime-build2-tail.log`; full 1.0 MB log stays in `W/logs/`) |
| Binary | 120337968 bytes, symbol addresses IDENTICAL to build 1 (`_SDL_main 0x103e93fd0`, `_main 0x10632e1c0`, …) — only the plist changed; P-lane WIP stable across both builds |
| `Info.plist` | 25 keys (20 + 5 manifest keys): identifier intact + full `UIApplicationSceneManifest` dict (`/usr/libexec/PlistBuddy Print` receipt in Step 2 commands; `logs/Info2.plist.txt`) |
| Warnings | 81 total (same) |

## Step 3 — Re-measure

Sim: iOS 27.0 runtime installed, nothing downloaded; iPhone 17 `4DE6C37C-…` was `(Shutdown)`; no substitution. Boot exit 0, `bootstatus -b` exit 0. Install exit 0 for APP1 (`logs/install.log`, empty) and APP2 (`logs/install2.log`, empty); `listapps` shows `org.ps2x.ps2entryrunner` both times.

### Step 3a — Commit-1 tree: scene trap (both shapes)

| Launch | Command shape | Result |
|---|---|---|
| 3 (no-arg) | `launch --console` (shell redirect) | Exit 0 in ~1.6s. Console (complete, 30 bytes): PID line ONLY — `SDL_main` never ran, no fatal text. `crash-noarg.ips` (18 KB, pid 5033) |
| 4 (argv probe) | `launch --console` + `/nonexistent-boot.elf` | Exit 0 in ~1.5s. Console (complete, 30 bytes): PID line ONLY — no `Using argv boot path`. `crash-argv.ips` (35 KB, pid 5722; report delivery lagged the first `ls` by seconds) |

Both `.ips` identical in fault: `EXC_BREAKPOINT` / `SIGTRAP`, codes `0x1, 0x1c48c336c`, `Trace/BPT trap: 5`, faulting thread 0 = main thread:

```text
___UIApplicationEvaluateRuntimeIssueForNoSceneLifecycleAdoption_block_invoke <- UIKitCore  (TRAP)
_dispatch_client_callout <- libdispatch.dylib
_dispatch_once_callout <- libdispatch.dylib
-[UIApplication workspace:didCreateScene:withTransitionContext:completion:] <- UIKitCore
... (scene creation frames)
UIApplicationMain <- UIKitCore
SDL_UIKitRunApp <- ps2EntryRunner (statically linked)
start_sim <- dyld_sim
start <- dyld
```

(The `main` frame between `start_sim` and `SDL_UIKitRunApp` is unnamed — local `t _main` has no global symbol for symbolication; the LC_MAIN→`_main` address proof is in Step 2. Non-triggered threads captured with no frames.)

Notes: (1) No window could exist — scene creation precedes `SDL_main`. (2) Device log shows `BUG in libdispatch: 26A428 24A434 - 612 - 0x4` at the same second, but the SAME line appears in the later HEALTHY runs (Step 3c `logshow-app.log:160`) — incidental sim noise, not the trap mechanism. Full window excerpt: `logs/logshow-crash-excerpt.log` (614 lines; the 3.3 MB unfiltered pull stays in `W/logs/`).

### Step 3b — Miniprobes (scratch only, no fork touch)

Standalone C probes, same prebuilt SDL (`libSDL2main.a`+`libSDL2.a`, same framework set), `LC_BUILD_VERSION minos 27.0/sdk 27.0` to match APP1/APP2, adhoc-signed, installed alongside (`logs/minprobe{,B,C}-install.log` all exit 0). A/B share one binary (`T _SDL_main`, `T _SDL_UIKitRunApp`, local `t _main` — same shape as APP1); plists differ only by the manifest (`logs/A.plist`, `logs/B.plist` diff receipt).

| Probe | Plist | Result |
|---|---|---|
| A (`org.ps2x.minprobea`) | Copy of APP1's plist (no manifest) | Console: PID line only. `minprobeA-crash.ips`: IDENTICAL trap (same codes, same UIKitCore block, `SDL_UIKitRunApp <- minprobeA`). The trap reproduces with a 1.3 MB trivial binary — our 120 MB binary, raylib, and P-lane code are exonerated |
| B (`org.ps2x.minprobeb`) | A + minimal manifest (no scene delegate class) | Console (complete, `logs/minprobeB-console.log`): `SDL_main` RAN, `SDL_Init OK video=uikit`, `SDL_CreateWindow` non-NULL, `clean exit`. No `.ips`. Benign side logs: `UIApplicationSupportsIndirectInputEvents` mouse note, `Unbalanced calls to begin/end appearance transitions` at teardown |
| C (`org.ps2x.minprobec`) | B's shape | SDL AUDIO discriminator (see Step 3c): `SDL_Init AUDIO ok driver=coreaudio`, `device=2 ... have=48000Hz ch=2`, `clean exit` (`logs/minprobeC-console.log`). No `.ips` |

Sources: `logs/probe.c`, `logs/probe-audio.c`. Probe binaries + `.app` bundles stay in `W/minprobe/` (not committed).

### Step 3c — Commit-2 tree: SDL init passes, first window, audio wall

| Launch | Command shape | Result |
|---|---|---|
| 5 (no-arg) | `launch --console` (shell redirect) | Exit 0 in ~1.7s. Console (complete): the I6 clean fatal, byte-identical modulo PID — `[main] fatal exception: Unable to determine executable path. …` + PID line. No `.ips`. The runbook's expected no-arg behavior now holds |
| 6 (argv probe) | `launch --console` + `/nonexistent-boot.elf` | Exit 0 in ~10.3s wall (app ALIVE ~10s). Console (`logs/launch6-argv2-console.log`, complete, 43 lines): `Using argv boot path`, raylib 5.5 all modules, NO `Failed to initialize SDL`, `DISPLAY: Device initialized successfully` (402×874 display, 640×448 screen/render), `GLAD: OpenGL ES 2.0`, Apple Software Renderer, VAO/shaders/default texture+font all loaded, `PLATFORM: DESKTOP (SDL): Initialized successfully`, `Working Directory: …/ps2EntryRunner.app`. Neither `Failed to initialize PS2 runtime` nor `Failed to load ELF` printed. `crash-argv2.ips` (29 KB, pid 8981) |
| 7 (argv repeat) | Same as 6 | Console byte-identical to launch 6 except PID/timestamp (diff receipt kept). Deterministic |
| 8 (argv, screenshot run) | `launch` (no `--console`) + `screenshot` at +4s | Screenshot `logs/i7-window-live2.png` (71 KB): app foreground, full-screen black window + iOS status bar — FIRST WINDOW. Then the same SIGABRT (`212753.ips`, spot-checked: same `abort` top, `InitAudioDevice` + `SDL_main` frames) |

New crash (launches 6–8, all three identical): `EXC_CRASH` / `SIGABRT`, `Abort trap: 6`, self-abort:

```text
__pthread_kill <- libsystem_kernel.dylib
pthread_kill <- libsystem_pthread.dylib
abort <- libsystem_c.dylib
_ReportRPCTimeout(char const*, int) <- AudioToolboxCore
_CheckRPCError(char const*, int, int) <- AudioToolboxCore
AURemoteIO::Initialize() <- bEmbeddedSystemAUs.dylib
... (ausdk AUBase)
AudioUnitInitialize <- AudioToolboxCore
ma_device_init_internal__coreaudio <- ps2EntryRunner
ma_device_init__coreaudio <- ps2EntryRunner
ma_device_init <- ps2EntryRunner
InitAudioDevice <- ps2EntryRunner
PS2Runtime::initialize(char const*) <- ps2EntryRunner
SDL_main <- ps2EntryRunner
-[SDLUIKitDelegate postFinishLaunch] <- ps2EntryRunner
__NSFireDelayedPerform <- Foundation
... (runloop timer → CFRunLoopRun → UIApplicationMain → SDL_UIKitRunApp)
```

Device-log smoking gun (`logs/logshow-app.log:416`, Fault level): `Initialize: RPC timeout. Apparently deadlocked. Aborting now.` (~9s after the last prior line; also `libAudioDSP: cannot migrate AudioUnit assets for current process` just before). So: `InitWindow` COMPLETED (past the I6 `rlLoadTexture` SEGV site); `initialize()` proceeded to `InitAudioDevice` (miniaudio → CoreAudio `AudioUnitInitialize(RemoteIO)`), whose XPC deadlocked and AudioToolbox deliberately aborted. `loadELF` still never ran — the probe path's fate (I6 gap 6) remains unobserved. Probe C proves sim CoreAudio/RemoteIO is functional via SDL's backend — the wall is specific to miniaudio's init path as invoked here (3 identical aborts vs probe C's clean exit interleaved after).

### Screenshots

| File | Content | Disposition |
|---|---|---|
| `logs/i7-window-live2.png` (71 KB) | App foreground, black full-screen window + status bar (9:27) — first window | COMMITTED |
| `W/logs/i7-window-check.png` (3.8 MB) | Home screen after the Step 3a trap (ps2EntryRunner icon visible, no window) | Scratch only (miss-by-design: trap runs show nothing) |
| `W/logs/i7-window-live.png` (3.8 MB) | Home screen — MISSED the Step 3c window: taken ~9s after the crash; inter-tool-call latency exceeded the ~10s life window | Scratch only; retry as launch 8 (single command, +4s) captured it |

All screenshots to the internal path first (`~/*.png`), then `mv` to scratch — the standing rule held; both writes succeeded.

## Entry/lifecycle map from REAL logs (I6 gaps 2/4 + I7)

Measured call order, commit-2 tree, argv probe:

```text
SpringBoard bootstrap → posix_spawn (launchd_sim) → start_sim → _main [SDL2main, local t]
  → SDL_UIKitRunApp → UIApplicationMain → scene creation (manifest present — no trap)
  → [SDLUIKitDelegate postFinishLaunch] → SDL_main (main.cpp, renamed; argc/argv intact)
  → getExecutablePath → "Using argv boot path" → PS2Runtime::initialize
  → InitWindow (raylib 5.5, DESKTOP/SDL backend) → SDL_Init VIDEO OK (video=uikit)
  → DISPLAY+GL ES 2.0+shaders+font all initialized → window live (photographed)
  → InitAudioDevice → miniaudio coreaudio → AudioUnitInitialize(RemoteIO)
  → RPC timeout (~9s) → AudioToolbox abort (SIGABRT). loadELF/run never reached.
```

Commit-1 tree order (both shapes): same through `SDL_UIKitRunApp → UIApplicationMain`, then scene creation traps (`NoSceneLifecycleAdoption`, SIGTRAP) before `SDL_main`; our code never runs (PID-only consoles).

I6 gap disposition:

| I6 gap | Status after I7 evidence |
|---|---|
| 1 — SDL video init fails without UIKit entry | Closed: with SDL2main + manifest, SDL video init passes (`video=uikit`, DISPLAY + GL init complete, window photographed) |
| 2 — `loadELF`/`run` order + missing-resource behavior | Still blocked, one stage later: crash now lands in `InitAudioDevice` inside `initialize()`; `loadELF`/`run` still unreached |
| 3 — Harness: simctl-owned writes fail on external volume | Rule re-held: all stdout via `--console` + shell redirect; screenshots to internal path first (both succeeded) |
| 4 — simctl exit code never propagates app fate | Re-confirmed: exit 0 observed for clean-fatal (launch 5), SIGTRAP (launches 3–4), and SIGABRT-after-10s (launches 6–8) |
| 5 — `PRODUCT_BUNDLE_IDENTIFIER` warning | Still present (1× in both I7 builds); still install-irrelevant |
| 6 — First-launch boot-path strategy | Still open: `loadELF` never ran in any I7 launch (trap/audio walls precede it); observe-only per brief |

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | `InitAudioDevice` aborts: miniaudio CoreAudio `AudioUnitInitialize(RemoteIO)` RPC-times-out ("Apparently deadlocked") and AudioToolbox calls `abort()`; `initialize()` never returns, `loadELF` never runs | `logs/launch6-argv2-console.log` (GL init complete, no failure lines) + `logs/crash-argv2.ips` (SIGABRT stack `… ← InitAudioDevice ← initialize ← SDL_main`) + `logs/logshow-app.log:416` (`RPC timeout. Apparently deadlocked. Aborting now.`) | Brief that makes audio init succeed on the sim (miniaudio coreaudio config / audio-session setup / init threading or ordering — implementer's call; note probe C exonerates sim audio itself), rebuilds, and re-runs this brief's argv probe to `loadELF` |
| 2 | `loadELF` behavior with the probe path + `run()` order still unmeasured | Absence: abort precedes `loadELF` in launches 6–8; `Failed to load ELF` never printed | Re-run of this brief's launch measurement after gap 1 clears (argv probe + no-arg + screenshot if rendering starts), capturing console + `.ips` if any |
| 3 | Push of `2655264` deferred (remote ahead with P-lane `2caf17c`; rebase refused on P-lane's unstaged file) | `logs/fork-push2.log` (non-fast-forward rejection) + `logs/fork-commit2.log` (two `pull --rebase` refusals) | No code brief — process retry when P-lane's tree is clean: `git -C FORK pull --rebase fork ssx3` (replays only `2655264`) then `git -C FORK push fork ssx3`; verify with `ls-remote`. Commit is already the measured tree for all Step 2b/3c evidence |
| 4 | `simctl launch --console` stays attached ~10s for a living app; crash `.ips` delivery can lag the launch return by seconds | Launch 6 wall 10.291s; launch-4 `.ips` absent at first `ls`, present 3s later | Standing measurement note (extends I6 gap-4 rule): after each launch, `sleep` + re-`ls` DiagnosticReports before concluding "no crash"; screenshot runs must be single-command (inter-call latency exceeds short life windows) |
| 5 | Xcode `PRODUCT_BUNDLE_IDENTIFIER` warning (I6 gap 5 carried) | 1× in both I7 build logs | Optional hardening brief (unchanged): also set `XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER`, confirm warning clears with install still exit 0 |
| 6 | First-launch boot-path strategy (I6 gap 6 carried) | No-arg fatal names `argv[1]`/`PS2X_DEFAULT_BOOT_ELF` (launch 5); argv forwarding intact through SDL2main (probe B `argc=1`; launch 6 `Using argv boot path`) | Strategy brief (unchanged, still blocked behind gap 1): what first launch is given — only meaningful once `loadELF` runs |

## Step 4 — Report (this file)

| Item | Receipt |
|---|---|
| Evidence dir | `local/research/I7/` (REPORT.md + `logs/`, 42 files, ~700 KB total, under the 5 MB cap; one 71 KB screenshot) |
| Scratch | `W/logs/` holds the same files plus full build logs (1.0 MB each), the unfiltered 3.3 MB `logshow-crash.log`, and the two home-screen PNGs; `W/ios-runtime-rel/` + `W/ios-runtime-rel2/` (5.4G each) are the build trees; `W/minprobe/` holds probe sources/binaries/bundles |
| Sim shutdown | `simctl shutdown` exit 0; device verified `(Shutdown)` |
| Commit | `[I7]` + `Orchestrated-By: Muse Code` trailer; `git add -f` (dir is git-ignored); no push |
| Time box | ~2.9h wall (configures ~3 min, builds ~15 min, remainder measurement + probes + report); 4h box not binding |

## Exact commands

```sh
# --- Step 1: fork edits (entry files ONLY), commits, pull --rebase attempts, pushes ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"
W="/Volumes/Extreme SSD/ps2x-i7"
git -C "$FORK" log --oneline -8; git -C "$FORK" branch --show-current
git -C "$FORK" status --short   # P-lane WIP unstaged throughout; never staged
# SDL mechanism verification (all read-only):
grep -n "define main\|SDL_MAIN_NEEDED" SDLPRE/include/SDL2/SDL_main.h  # L143 rename, L63 __IPHONEOS__->NEEDED
sed -n '108,111p' SDLPRE/include/SDL2/SDL_platform.h                   # __IPHONEOS__=1 from TARGET_OS_IPHONE
grep -n "SDL_main.h\|SDL_stdinc.h" SDLPRE/include/SDL2/SDL.h           # L31/L32; chain via stdinc->config->platform
grep -n "SDL_main.h" SDLPRE/include/SDL2/SDL_main.h | head -1          # L25: #include SDL_stdinc.h (chain order proof)
nm -g SDLPRE/lib/libSDL2main.a | grep " T "                           # T _main only
echo 'int x;' > /tmp/macro-check.c
xcrun --sdk iphonesimulator clang -arch arm64 -dM -E /tmp/macro-check.c | grep -E "IPHONE|SIMULATOR"  # TARGET_OS_IPHONE=1, no __IPHONEOS__
grep -lnw "main" "$FORK/ps2xRuntime/src/runner/"*.cpp                  # no match (unity-leak risk assessed)
# (edit 1: CMake SDL2main link + main.cpp SDL.h include + #undef main)
git -C "$FORK" diff ps2xRuntime/CMakeLists.txt ps2xRuntime/src/main.cpp  # 2 files, +33/-0
git -C "$FORK" add ps2xRuntime/CMakeLists.txt ps2xRuntime/src/main.cpp   # NAMED files only
git -C "$FORK" commit -m "Entry: wire UIKit bootstrap via SDL2main for iOS sim (I7)" -m "<body>" -m "Orchestrated-By: Muse Code"  # 9c7b028
git -C "$FORK" pull --rebase fork ssx3                # refused: unstaged P-lane file; proven no-op instead:
git -C "$FORK" fetch fork ssx3; git -C "$FORK" log --oneline HEAD..fork/ssx3  # empty
git -C "$FORK" merge-base --is-ancestor fork/ssx3 HEAD && echo ancestor-ok
git -C "$FORK" push fork ssx3                         # ed387c7..9c7b028; ONLY in fork clone to fork remote
git -C "$FORK" ls-remote fork ssx3                    # 9c7b028…
# (edit 2: ps2xRuntime/ios/Info.plist new + MACOSX_BUNDLE_INFO_PLIST)
plutil -lint "$FORK/ps2xRuntime/ios/Info.plist"        # OK
git -C "$FORK" add ps2xRuntime/CMakeLists.txt ps2xRuntime/ios/Info.plist  # NAMED (._ sidecar NOT added)
git -C "$FORK" diff --cached --name-only              # exactly those 2
git -C "$FORK" commit -m "Entry: add iOS scene manifest so UIKit entry reaches SDL_main (I7b)" -m "<body>" -m "Orchestrated-By: Muse Code"  # 2655264
git -C "$FORK" pull --rebase fork ssx3                # refused (P-lane file); remote now ahead with P1y 2caf17c
git -C "$FORK" push fork ssx3                         # REJECTED non-fast-forward (no force-push); deferred, retried at end (same)

# --- Step 2: two fresh Release-iphonesimulator builds in W ---
mkdir -p "$W/logs"
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE=/Users/bradrichardson/dev/ssx3/local/research/I1/logs/ios-simulator.toolchain.v2.cmake \
  -DCMAKE_CONFIGURATION_TYPES=Release \
  -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF \
  -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i4/sdl2-ios-sim/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -S "$FORK" -B "$W/ios-runtime-rel"                  # exit 0 (73.9s + 18.5s)
cmake --build "$W/ios-runtime-rel" --config Release -- -jobs 4   # BUILD SUCCEEDED, 9m19s
# (same pair with -B "$W/ios-runtime-rel2" → configure2.log / build2.log: exit 0, 5m10s)
APP1="$W/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app"
APP2="$W/ios-runtime-rel2/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app"
stat -f "%z bytes" "$APP1/ps2EntryRunner"; file "$APP1/ps2EntryRunner"
nm -g "$APP1/ps2EntryRunner" | grep -E " T _(main|SDL_main|SDL_Init|InitWindow|SDL_UIKitRunApp|UIApplicationMain)$"
nm "$APP1/ps2EntryRunner" | grep -E " _main$"; otool -l "$APP1/ps2EntryRunner" | grep -A3 LC_MAIN
nm -g "$APP1/ps2EntryRunner" | grep -c " T _SDL_"; nm -g "$APP1/ps2EntryRunner" | grep -E "iPhone|UIKit"
otool -L "$APP1/ps2EntryRunner"; codesign -dvv "$APP1"
/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" "$APP2/Info.plist"
/usr/libexec/PlistBuddy -c "Print UIApplicationSceneManifest" "$APP2/Info.plist"
plutil -convert xml1 -o "$W/logs/Info2.plist.txt" "$APP2/Info.plist"
grep "warning:" "$W/logs/ios-runtime-build.log" | sed 's/.*warning: //' | sort | uniq -c | sort -rn

# --- Step 3a/3c: boot + installs + launches ---
UDID="4DE6C37C-77EF-45AE-827E-26286E68D022"
xcrun simctl boot "$UDID"; xcrun simctl bootstatus "$UDID" -b
xcrun simctl install "$UDID" "$APP1"                  # exit 0
xcrun simctl launch --console "$UDID" org.ps2x.ps2entryrunner                    # launch 3: exit 0, PID only + SIGTRAP
xcrun simctl launch --console "$UDID" org.ps2x.ps2entryrunner /nonexistent-boot.elf  # launch 4: exit 0, PID only + SIGTRAP
xcrun simctl install "$UDID" "$APP2"                  # exit 0 (overwrite)
xcrun simctl launch --console "$UDID" org.ps2x.ps2entryrunner                    # launch 5: exit 0, clean fatal
xcrun simctl launch --console "$UDID" org.ps2x.ps2entryrunner /nonexistent-boot.elf  # launch 6: exit 0, ~10s, GL init + SIGABRT
# launch 7: repeat of 6 (determinism); launch 8: no-console launch + screenshot at +4s in ONE command
xcrun simctl spawn "$UDID" log show --last 6m --style compact --predicate 'process == "ps2EntryRunner" OR ...'
xcrun simctl spawn "$UDID" log show --last 12m --style compact --predicate 'process == "ps2EntryRunner"'
xcrun simctl io "$UDID" screenshot ~/i7-window-live2.png   # internal path first, then mv to scratch
cp ~/Library/Logs/DiagnosticReports/ps2EntryRunner-*.ips "$W/logs/"

# --- Step 3b: miniprobes (scratch only) ---
SDLPRE="/Volumes/Extreme SSD/ps2x-i4/sdl2-ios-sim"; SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
xcrun --sdk iphonesimulator clang -arch arm64 -mios-simulator-version-min=27.0 -isysroot "$SDK" \
  -I"$SDLPRE/include" "$W/minprobe/probe.c" "$SDLPRE/lib/libSDL2main.a" "$SDLPRE/lib/libSDL2.a" \
  -lm -lpthread -framework CoreVideo -framework CoreAudio -framework AudioToolbox -framework AVFoundation \
  -framework CoreBluetooth -framework CoreGraphics -framework Coremotion -framework Foundation \
  -weak_framework GameController -framework Metal -framework OpenGLES -framework QuartzCore -framework UIKit \
  -weak_framework CoreHaptics -o "$W/minprobe/probe"     # exit 0, no warnings at minos 27.0
# (bundle A: APP1 plist copy with new id/exec; bundle B: A + scene manifest; bundle C: audio probe + B plist)
codesign -s - "$W/minprobe/minprobeA.app"  # same B, C
xcrun simctl install "$UDID" "$W/minprobe/minprobeA.app"   # exit 0 (same B, C)
xcrun simctl launch --console "$UDID" org.ps2x.minprobea   # A: PID only + same SIGTRAP
xcrun simctl launch --console "$UDID" org.ps2x.minprobeb   # B: SDL_main runs, uikit video, window, clean exit
xcrun simctl launch --console "$UDID" org.ps2x.minprobec   # C: coreaudio device opens, clean exit

# --- Step 4: evidence + commit + shutdown ---
cp W/logs/{...41 files...} W/minprobe/{probe.c,probe-audio.c,A.plist,B.plist} local/research/I7/logs/
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/I7/
git -C /Users/bradrichardson/dev/ssx3 commit -m "[I7] …" -m "Orchestrated-By: Muse Code"
xcrun simctl shutdown "$UDID"; xcrun simctl list devices | grep "$UDID"   # (Shutdown)
```

(`W` = `/Volumes/Extreme SSD/ps2x-i7/`; full untruncated commands in shell history; log files hold the outputs.)

## Receipt paths

- `local/research/I7/REPORT.md` (this file)
- `local/research/I7/logs/fork-commit.log`, `fork-push.log` (9c7b028 receipt + push receipt)
- `local/research/I7/logs/fork-commit2.log`, `fork-push2.log` (2655264 receipt, rebase refusals, non-fast-forward rejection)
- `local/research/I7/logs/ios-runtime-configure.log` (full), `ios-runtime-build-tail.log` (last 80; full log in `W/logs/`); same pair with `2` suffix for rel2
- `local/research/I7/logs/nm-entry.log`, `nm-sdl-count.log`, `otool-L.log`, `codesign.log`, `Info.plist.txt` (build 1, 20 keys), `Info2.plist.txt` (build 2, 25 keys), `warnings-uniq.log`
- `local/research/I7/logs/boot.log` (empty), `bootstatus.log`, `install.log` (empty), `install2.log` (empty)
- `local/research/I7/logs/launch3-console.log`, `launch4-argv-console.log` (PID-only trap runs, complete)
- `local/research/I7/logs/launch5-noarg2-console.log` (clean fatal, complete), `launch6-argv2-console.log` (GL init + window, complete), `launch7-argv3-console.log` (repeat)
- `local/research/I7/logs/crash-noarg.ips`, `crash-argv.ips` (SIGTRAP pair), `crash-argv2.ips` (SIGABRT audio)
- `local/research/I7/logs/minprobeA-console.log`, `minprobeA-crash.ips`, `minprobeB-console.log`, `minprobeC-console.log`, `minprobe{,B,C}-install.log` (empty), `probe.c`, `probe-audio.c`, `A.plist`, `B.plist`
- `local/research/I7/logs/logshow-crash-excerpt.log` (614-line trap window), `logshow-app.log` (919-line app-process log with the RPC-timeout Fault)
- `local/research/I7/logs/i7-window-live2.png` (first window, 71 KB)
- `W/logs/` (same 41 files + full build logs + unfiltered `logshow-crash.log` + 2 home-screen PNGs); `W/ios-runtime-rel/`, `W/ios-runtime-rel2/` (build trees, 5.4G each); `W/minprobe/` (probe sources/binaries/bundles)
- Measured products: APP1 (rel, commit-1 tree) and APP2 (rel2, commit-2 tree) under `W/`
- Fork `9c7b028` on `fork ssx3` (pushed); fork `2655264` local (push deferred — gap 3)

## What I could not do

- Reach `loadELF` / `run` / rendered content — audio init aborts first (gap 1 owns the next step).
- Push `2655264` — deferred on P-lane's concurrent state (gap 3; retry documented, no force-push).
- Root-cause the miniaudio CoreAudio RPC deadlock beyond the Fault line + SDL-audio discriminator — next brief's work (gap 1). Notably untested: raw-miniaudio probe (raylib's bundled `miniaudio.h` alone), audio-session category effects, init-thread variations.
- Define the first-launch boot path — still blocked behind gap 1 (gap 6).
- Symbolicate app frames to source lines — Release without `-g`/dSYM; function-level stacks from `.ips` only.
- Screenshot a RENDERED frame — the window is black (initialize never completes, run loop never starts); first presented content awaits gap 1.
- Device slice (`ios-arm64`) — unchanged from I6 (not attempted per scope rule).
- Signing beyond observing adhoc — `TeamIdentifier=not set`; no provisioning profiles touched.
- `IoPaths` sandbox behavior — still unwritten by the app (it never reaches file I/O).
- Touch / keyboard / MFi / GLES-render verification — unchanged from I6 (no running loop).
- Debug-config codegen question — unchanged from I4 (Release only).
- The 81 Release-build warnings — still untriaged beyond the identifier warning's identification (counts identical across I6/I7 builds).
- Uninstall the three `minprobe*` helper apps from the sim — left installed (documented here); `simctl uninstall` per bundle id removes them.
