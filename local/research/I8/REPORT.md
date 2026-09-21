# I8 — Audio-wall device repro: device slice + install + miniaudio diagnosis on iPhone

- Date: 2026-09-20. Tables, no verdicts.
- `local/research/I7/REPORT.md` read first (all of it: entry/lifecycle map, gap 1 = this brief's parent, standing measurement rules) + `local/research/MF1/REPORT.md` device sections (fresh-bundle provisioning/install flow — mechanism reused, deltas tabled).
- Fork: separate worktree `/Volumes/Extreme SSD/ps2x-i8/fork-wt` at pinned `b6252bb` (detached) + 1 commit `3006a07` (CFBundleName plist fix), pushed to FORK remote topic branch `i8-device-bundle-name` (`ls-remote` confirms, first try). Shared clone untouched except the one `worktree add` + read-only inspection (E3b owns it).
- Product: `/Volumes/Extreme SSD/ps2x-i8/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app` (binary `ps2EntryRunner`, 2944712 bytes, Mach-O 64-bit arm64, device slice). Installed on the iPhone as `org.ps2x.ps2entryrunner`.
- Rules honored: no PS2 boots → no lease; no `adb`; builds `-jobs 2` / `--parallel 2` everywhere, never 4; all trees under `/Volumes/Extreme SSD/ps2x-i8/`; caps declared up front + tracked (below); app fate from console + `.ips`, never exit code; screenshots to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; no `--force-install`; evidence `local/research/I8/` standalone, `[I8]` commit, no push.
- Outcome shape: device toolchain configures; Release device build exits 0; app installs; argv probe reaches PAST I7's sim wall — miniaudio CoreAudio init SUCCEEDS on hardware (48 kHz), `loadELF` runs for the first time (`Failed to open/load ELF` on the probe path), orderly teardown, then idle (no crash, no `.ips` across 4 launches). The I7 audio abort does not reproduce on device; it is a sim-environment wall. One config fork fix was required along the way (CFBundleName for `devicectl install`).

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i8/`, `WT` = `W/fork-wt` (fork worktree), `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `D` = iPhone UDID `00008140-0002505001F3001C`, `FORK` = shared clone (E3b-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | The I7 miniaudio `AudioUnitInitialize(RemoteIO)` abort reproduces on device (same wall), OR device shows a new wall; either way the failing layer is nameable from console + `.ips` + screenshot |
| Observable | Device toolchain configure exit; Release build exit; install exit + apps-list; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`) + screenshot; same-vs-new table against I7 sim |
| Alternatives | H-a same wall (audio abort on device) → layer = miniaudio/init path, config fix or I9 recipe. H-b new wall (scene/entry/signing) → table + recipe. H-c no wall (runs past audio) → wall is sim-specific; name the sim layer with evidence |
| Stop | All bars tabled (configure/build/install/repro/diagnosis) or any cap (partial tabled as gap). Verdict + ONE next action in Task 3 |
| Time box | 6 h (used ~1 h wall; box not binding) |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 20 GB | 5.2 GB (26%) | `du -sh W` after receipts step |
| Evidence `local/research/I8/` | ≤ 5 MB | ~340 KB, 31 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i8-window-live.png`, 116 KB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (SDL Ninja `--parallel 2`, Xcode `-jobs 2`) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only | 1 file, topic branch push | `logs/fork-commit.log`, `logs/fork-push.log` |

## Task 0 — Pin + worktree (no phone)

| Item | Receipt |
|---|---|
| Pin | `b6252bb` (`Diag: env-gated presentation-frame capture PS2X_FRAME_DUMP_DIR (K1 P0)`), the brief's default; no newer commit required |
| Why this pin is clean | K1 P0 is env-gated (unset = zero behavior change); parent of E3b's active `b34b481` (excludes E3b instrumentation); I7 entry wiring verified present by ancestry (next row) |
| I7 content proof | `merge-base --is-ancestor 9c7b028 b6252bb` AND `c41efce b6252bb` both true: SDL2main link + rebased scene manifest are in the pin |
| Base-not-moved | Remote `fork/ssx3` sits at `b34b481` (E3b, pushed); the I8 fix rides a topic branch instead of moving the worktree base (reason + receipts in Task 2) |
| Worktree | `git -C FORK worktree add --detach W/fork-wt b6252bb` → `HEAD is now at b6252bb` (`logs/worktree-add.log`); `status` clean |
| I7 files present | `ps2xRuntime/ios/Info.plist` exists; `SDL2::SDL2main` link at `CMakeLists.txt:644`; `#include <SDL2/SDL.h>` at `main.cpp:35` |
| Shared-clone contact | One `worktree add` + read-only `remote -v / log / rev-parse / merge-base / worktree list / status`; no reads of its working tree, no builds, no stash/pull/checkout |
| Fork remote | `fork https://github.com/brad-richardson/PS2Recomp.git`; `origin` = `ran-j` upstream (never pushed) |

## Task 1 — Device toolchain + build (worktree, no phone)

### Toolchain: every delta vs I1 sim v2 (file: `logs/ios-device.toolchain.cmake`)

| # | Setting | Sim v2 | Device (I8) | Why |
|---|---|---|---|---|
| 1 | `CMAKE_OSX_SYSROOT` | `iphonesimulator` | `iphoneos` | The device slice |
| 2 | `CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED` | unset | `NO` | Device `.app` needs profile + entitlements; build stays unsigned, Task 2 signs manually (MF1 mechanism) |
| 3 | `CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_REQUIRED` | unset | `NO` | Belt-and-braces with #2 |
| — | `CMAKE_SYSTEM_NAME` / `PROCESSOR` / `ARCHITECTURES` / `ONLY_ACTIVE_ARCH` | `iOS` / `arm64` / `arm64` / `YES` | unchanged | Same arch, same generator behavior |
| — | `CMAKE_OSX_DEPLOYMENT_TARGET` | unset | unset (SDK default 27.0; phone runs 27.0) | No deviation from I7 |

### SDL2 for iphoneos (no device prebuilt existed; I4 built sim-only)

Source: fresh shallow clone of `release-2.32.10` to `W/SDL` (own dir; I4's `SDL/` never read). HEAD `5d24957` — same commit as I4.

| Item | Receipt |
|---|---|
| Configure | Exit 0 (`Configuring done (165.1s)`, `logs/sdl2-configure2.log`): `-G Ninja`, I8 device toolchain + `-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY` (I4's Ninja/iOS passthrough as `-D`, not a second file), `Release`, `SDL_SHARED=OFF SDL_STATIC=ON SDL_TEST=OFF`, AppleClang (`env -u CC -u CXX`) |
| Build | Exit 0, `[266/266]`, `--parallel 2` (`logs/sdl2-build2-tail.log`); 242 `warning:` lines, deprecation-only (EAGLContext/mainScreen/gl\*/statusBarOrientation/gamepad; `logs/sdl2-warnings-uniq.log`) |
| Install | Exit 0 (`logs/sdl2-install2.log`); `libSDL2.a` 2162728 bytes Non-fat arm64 (I4 sim: 2163368, Δ −640); `libSDL2main.a` 816 bytes arm64, `T _main` + `U _SDL_UIKitRunApp/_SDL_main` (same shape as I4) |
| First-build failure (ExFAT class) | Exit 1: SDL's CMake globbed 2132 AppleDouble `._*` sidecars as sources (`src/._SDL.c`, `src/main/uikit/._SDL_uikit_main.c` → `source file is not valid UTF-8`; `logs/sdl2-build-first-error.log`). Fix: recursive purge + wipe build dir + reconfigure (build lists are configure-time). Worktree had 310 sidecars too — purged, `status` clean after |
| Allocated bytes note | `W/SDL` reads 2.2 GB after purge (ExFAT cluster inflation on small files; real content is tens of MB). Purging freed ~2 GB across `W` |

### Runtime configure + build (I7 flags shape)

`CC=/opt/homebrew/opt/llvm/bin/clang`, `CXX` unset (I7 provenance). raylib source reused read-only from I4 (`-DFETCHCONTENT_SOURCE_DIR_RAYLIB=/Volumes/Extreme SSD/ps2x-i4/raylib-5.5`, 0 sidecars at check); imgui/rlImGui/sse2neon fresh FetchContent (network).

| Item | I7 sim | I8 device (this brief) |
|---|---|---|
| `-S` / `-B` | shared clone / `W-i7/ios-runtime-rel2` | worktree `WT` / `W/ios-runtime-device` |
| Toolchain | I1 sim v2 | `logs/ios-device.toolchain.cmake` |
| `SDL2_DIR` | `W-i4/sdl2-ios-sim/...` | `W/sdl2-ios-device/lib/cmake/SDL2` |
| Config flags | `-G Xcode`, `ConfigurationTypes=Release`, `RECOMP/ANALYZER/TEST/STUDIO OFF`, `SCCACHE OFF` | identical |
| Configure | Exit 0 (66.9s + 20.0s) | Exit 0 (`71.4s` + `3.1s`; `logs/ios-runtime-configure.log`, full) |
| Generated plist | = I7b template | = template (pre-fix; `diff` clean) |
| Build | Exit 0, 5m10s, `-jobs 4` | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (E3b subordination) |
| Build tree | 5.4 GB | 1.8 GB (clean pin: no P-lane 398k-line WIP TU) |

### Device binary record (`Release-iphoneos`, unsigned)

| Item | Receipt |
|---|---|
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 2944712 bytes (I7: 120337968 — clean pin, no P-lane WIP); `77d1a3960a3e26102786a1b980fd56111b6a4698a9b8cd975ed0edb370510ce7` |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2` (iOS device), `minos 27.0 / sdk 27.0` (`logs/build-version.log`) |
| Entry symbols | `T _SDL_main`, `T _SDL_UIKitRunApp`, `T _SDL_Init`, `T _InitWindow`; local `t _main` at `0x1000eb938`; `LC_MAIN entryoff 964920 = 0xEB938` → SDL2main's `_main` exactly (I7's proof shape; `logs/nm-entry.log`) |
| SDL count | 296 `T _SDL_` symbols — identical to I7 (`logs/nm-sdl-count.log`) |
| Link set | libSystem + SDL iOS frameworks (`logs/otool-L.log`) |
| Signature | `code object is not signed at all` (`logs/codesign-unsigned.log`) — by toolchain design |
| Identifier | `org.ps2x.ps2entryrunner` (bundle stays; no provisioning rename) |
| Built plist | `MinimumOSVersion 27.0`, `UIDeviceFamily {1}`, `CFBundleSupportedPlatforms {iPhoneOS}` (Xcode-injected, as predicted from I7's key list), `UIRequiredDeviceCapabilities` (new vs sim: device-only injection), scene manifest intact (`logs/Info.plist.txt`) |
| Warnings | 74 total (I7: 81 — fewer TUs without P-lane WIP); identifier/`PRODUCT_BUNDLE_IDENTIFIER` warning still 1× (`logs/warnings-uniq.log`) |
| Binary stability | sha prefix `77d1a3960a3e2610` identical across the initial build + 2 plist-only rebuilds (Task 2) |

## Task 2 — Provision + install + repro (iPhone)

Phone: iPhone 16 Pro Max (`iPhone17,2`), iOS 27.0 (`24A437`), UDID `D`, WiFi, paired (`logs/iphone-details.json`; matches MF1's record).

### Phone state before install (running sessions are the user's — reported, not killed)

| Item | Receipt |
|---|---|
| Reachability | `available (paired)` at every check; no stall, no substitution |
| Lock state | `passcodeRequired: true` pre-install → `false` post-cleanup, `unlockedSinceBoot: true` both (`logs/lockstate.log` = post-cleanup read; pre-install read in session transcript). No `Locked` failure hit in I8 (cf. MF1's transient error 7) |
| Running processes | 393-line list at cleanup check; user's sessions active throughout. Only our 3 probe PIDs ever signaled (53762, 53808 via `--terminate-existing`; 53817 via `process terminate`); nothing else touched |
| Installed apps | No prior `org.ps2x.*`; `MF1Probe` present, never launched/touched. Post-install: `ps2EntryRunner org.ps2x.ps2entryrunner` listed |
| Post-brief state | Our instance terminated (processes grep = 0); app left installed (MF1 precedent: `MF1Probe` still installed) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout`; 2 top-level `list devices` ran bare before discovering the flag also applies there — re-ran receipted with `--timeout 30`, exit 0 |

### Provision + sign + install (MF1 mechanism reused; every delta tabled)

Profile: `f0793278-...` (`iOS Team Provisioning Profile: *`, XC Wildcard, team `LQ3V7772Q2`, `get-task-allow=true`, expires 2027-09-17, `D` in `ProvisionedDevices`). Identity: `295EFB42...` (Apple Development). Signed bundle keeps `org.ps2x.ps2entryrunner` (wildcard covers it; no rename).

| Step | MF1 shape | I8 delta |
|---|---|---|
| Stage | build `MF1Probe.app` in-tree | `cp -R` unsigned `APP` → `SAPP` (build tree stays pristine); purge regenerated `._*` in the copy |
| Embed profile | `cp profile APP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys (`application-identifier`, `team-identifier`, `get-task-allow`) | identical shape; `application-identifier=LQ3V7772Q2.org.ps2x.ps2entryrunner` (`logs/entitlements.plist`) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements` | identical, ON ExFAT (MF1 signed on APFS) — exit 0, `codesign --verify --strict` exit 0 |
| Signed identity | — | `Identifier=org.ps2x.ps2entryrunner`, `TeamIdentifier=LQ3V7772Q2`, `Authority=Apple Development: Brad Richardson (E4R78PLLKY)` (`logs/codesign-signed.log`) |
| Install | `devicectl device install app` (no timeout in MF1 script) | explicit `--timeout 180`; no `--force-install` (fresh install) |

### Install wall 1 (config class): missing CFBundleName → fork fix `3006a07`

| Item | Receipt |
|---|---|
| Install-1 | Exit 1, `CoreDeviceError 3000`: `CFBundleName: ABSENT, CFBundleDisplayName: ABSENT` → `Failed to get the localized bundle name` (`logs/install.log`, complete). Mechanism: I7b template sets `CFBundleName` to EMPTY string; Xcode drops empty-string keys; `simctl` never checked, `devicectl` does |
| Fix (plist-only) | `CFBundleName` → `ps2EntryRunner` + 3-line comment in `ps2xRuntime/ios/Info.plist` (1 file, +4/−1). `plutil -lint`: OK |
| Plist-staleness learning | First rebuild still lacked the key: `INFOPLIST_FILE` points at the BUILD-DIR copy (`CMakeFiles/ps2EntryRunner.dir/Info.plist`), refreshed only at configure time. Re-configure (exit 0, 11.4s; `logs/ios-runtime-configure2.log`) → copy == template → rebuild exit 0 → built `.app` shows `ps2EntryRunner`. Binary sha unchanged throughout |
| Commit | `3006a07` `Bundle: set CFBundleName so devicectl installs the device .app (I8)` + body + `Orchestrated-By` (`logs/fork-commit.log`); named-file `git add` (1 file); worktree only |
| Push | `git push fork HEAD:refs/heads/i8-device-bundle-name` → exit 0, first try; `ls-remote` confirms `3006a07` (`logs/fork-push.log`). Topic branch because remote `fork/ssx3` sits at E3b's `b34b481` (ahead of the pin) — no non-fast-forward attempt on E3b's line, no rebase onto active instrumentation |
| Install-2 | Exit 0: `App installed: bundleID org.ps2x.ps2entryrunner`, `installationURL .../ps2EntryRunner.app/` (`logs/install2.log`); `info apps` confirms |

### Launches (argv probe to the wall)

All `devicectl` with explicit `--timeout`. Fate from console + `.ips`, never exit code (device `devicectl` DOES propagate fate: exit 1 = clean-fatal, exit 2 = timeout-abort — a device-vs-`simctl` harness delta; the rule was still held).

| Launch | Shape | Result |
|---|---|---|
| A (no-arg) | `--console`, `--timeout 120`, shell redirect | Exit 1 in 1.6s. Console (complete, `logs/launch-noarg-console.log`): the I7 clean fatal, same text — `[main] fatal exception: Unable to determine executable path. …` + `The app terminated with the exit code 1.` No `.ips` (clean `_Exit(1)`) |
| B (argv probe) | `--console`, `--timeout 120` + `/nonexistent-boot.elf` | Exit 2 (timeout). Console (complete, 64 lines, `logs/launch-argv-console.log`): `Using argv boot path`, raylib 5.5 all modules, `DISPLAY: Device initialized successfully` (440×956 display, 640×448 screen/render), `GLAD: OpenGL ES 2.0`, **Renderer: Apple A18 Pro GPU**, shaders/font/batch all loaded, `PLATFORM: DESKTOP (SDL): Initialized successfully`, then **`INFO: AUDIO: Device initialized successfully` (`miniaudio \| Core Audio`, 32-bit float, 2ch, 48000 Hz)**, then **`Failed to open ELF file` + `Failed to load ELF file`** (`loadELF` RAN — first observation ever), then orderly teardown (`AUDIO closed`, textures/shaders unloaded, `Window closed`) + benign appearance-transition warnings. All app output within ~0.5s (22:48:26.473→26.972); the remaining 119s the process idled (PID 53762 verified alive post-timeout) |
| B2 (argv repeat) | `--console`, `--timeout 30`, `--terminate-existing` (fresh process) | Exit 2 (timeout). Console byte-identical to B modulo timestamps/PID/addresses/timeout-value (diff receipt in session; both 64 lines). Deterministic. Fresh PID 53808 proves `--terminate-existing` replaced the idle B instance |
| C (screenshot run) | no-console launch + 2 screenshots in ONE command | Launch ok; `i8-shot1.png` (117 KB) + `i8-shot2.png` (76 KB), 1320×2868, to internal path first then `mv`. Both: app foreground, full-screen black + iOS status bar (10:52) — same black-window shape as I7's sim photo. Shot 1 committed as `logs/i8-window-live.png`; shot 2 scratch |

Crash-log record: `device info files --domain-type systemCrashLogs -s ps2EntryRunner` → `0 files:` after B (mechanism proven), and again `0 files:` after sleep + re-`ls` post-C (`logs/crashlog-recheck.log`). No `.ips` on device across all 4 launches.

### Same-wall-vs-new-wall table vs I7 sim

| I7 sim behavior | I8 device behavior | Wall status |
|---|---|---|
| No-arg: clean fatal, exit 0 (`simctl`) | No-arg: same fatal text, exit 1 (`devicectl` propagates) | SAME (modulo harness exit code) |
| Argv: GL init complete on Software Renderer, then SIGABRT in `InitAudioDevice` (RPC timeout, `.ips`) | Argv: GL init complete on A18 Pro GPU, audio init OK, `loadELF` runs, clean teardown, idle, no `.ips` | WALL GONE — H-c (no wall), not H-a/H-b |
| Sim-only console lines | Device-only console lines: `You need UIApplicationSupportsIndirectInputEvents …` (benign note), `WARNING: GL: NPOT textures extension not found`, `WARNING: PLATFORM: Unable to open game controller`, `INFO: GL: PVRT compressed textures supported` | New-but-benign device characteristics |
| `.ips` SIGABRT + Fault `RPC timeout. Apparently deadlocked` | 0 crash logs; process survives (PIDs observed alive) | No failing layer on device |
| Screenshot: black window pre-crash | Screenshot: black window post-teardown idle | Same pixels, different process state |

## Task 3 — Diagnosis (+ fix recipe; no device fix needed)

### Diagnosis: the failing layer is the SIM audio-server bridge, below miniaudio

| # | Claim | Evidence |
|---|---|---|
| 1 | The app's audio call sequence is valid | Same sequence succeeds on hardware: device console `AUDIO: Device initialized successfully (miniaudio \| Core Audio, 48 kHz)` (`logs/launch-argv-console.log`); call site `ps2_runtime.cpp:805-808` (`SetConfigFlags` → `InitWindow` → `InitAudioDevice` → `setAudioReady`) |
| 2 | The sim abort fires below app/miniaudio code | I7 stack: `abort ← _ReportRPCTimeout ← _CheckRPCError ← AURemoteIO::Initialize ← AudioUnitInitialize ← ma_device_init* ← InitAudioDevice`; Fault line `Initialize: RPC timeout. Apparently deadlocked. Aborting now.` — AudioToolbox's own verdict on its XPC to the sim audio server (`bEmbeddedSystemAUs`) |
| 3 | The trigger is miniaudio's specific RemoteIO configuration, not "audio on sim" | I7 probe C (SDL audio path) opens CoreAudio cleanly on the SAME sim; device runs miniaudio's path cleanly on hardware. Fails only at (miniaudio sequence × sim shim) |
| 4 | "miniaudio doesn't manage the session" is REFUTED | `raylib-5.5/src/external/miniaudio.h` mentions `AVAudioSession` 100× with `setActive:true/false`; SDL's `SDL_coreaudio.m` sets category + active too. Both manage the session — the discriminator is finer (category/mode/options or AudioUnit property sequence), NOT isolated this brief |
| 5 | P-lane-WIP confound excluded | Device tree is clean `b6252bb` (no WIP) vs sim tree with WIP — but the sim abort stack pre-dates all runner code (`initialize` → raylib → AudioToolbox) and the Fault verdict is AudioToolbox's, not app-state-dependent |
| 6 | Post-teardown idle is by construction, not a hang | `main.cpp:236-240`: `loadELF` fail → plain `return 1` from `SDL_main` (destructor teardown runs → teardown logs) → returns into SDL → UIKit runloop idles. Only the `_Exit` paths (`main.cpp:259/272`) terminate. Hence `--console` correctly waits until `--timeout` |

Fix attempted on device: NONE — no device wall exists to fix. (The one fork change this brief, `3006a07`, is the install-blocking plist config fix from Task 2, already committed + pushed.)

### I9 recipe: sim audio parity (only if sim remains a target — device is green)

| Option | Files + change shape | Proof lines | Risks |
|---|---|---|---|
| 1 (harness unblock): env-gated `InitAudioDevice` skip | `ps2_runtime.cpp:805-808`: `if (!std::getenv("PS2X_NO_AUDIO")) InitAudioDevice();` (readiness already modeled via `IsAudioDeviceReady()` → `m_audioBackend.setAudioReady`) | Device console proves the non-audio path runs to `loadELF`; sim needs the skip only where the shim hangs | Silent-audio sim runs; must verify `run()` tolerates `!audioReady` |
| 2 (real fix): pre-activate `AVAudioSession` on iOS | New small ObjC++ helper (category Playback + `setActive`) called in `initialize()` under `TARGET_OS_IPHONE`, before `InitAudioDevice` | SDL's path (session + unit config) works on the same sim (probe C) | Session category affects mixing/background; MUST re-verify the now-working device path does not regress |
| 3 (isolate trigger): raw-miniaudio probe on sim | Scratch probe (raylib's `miniaudio.h` alone, like I7 probe C): vary session category / unit properties until the RPC timeout reproduces or clears | Narrows option 2 to the exact property | Probe-only; no app change |

Contract verdict: **H-c** — no wall on device; I7 gap 1's abort is sim-environment-specific. The ONE next action: **boot a real ELF on the device** (I7 gap 6 / I6 gap 6, now unblocked: `loadELF` runs) — that is the next wall-finding probe, not more audio work.

## Exact commands

```sh
# --- Task 0: read-only pin verification + worktree (FORK otherwise untouched) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i8"
git -C "$FORK" remote -v; git -C "$FORK" log --oneline -12; git -C "$FORK" rev-parse b6252bb
git -C "$FORK" merge-base --is-ancestor c41efce b6252bb && echo ancestor-ok   # I7b in pin
git -C "$FORK" merge-base --is-ancestor 9c7b028 b6252bb && echo ancestor-ok   # I7 in pin
git -C "$FORK" worktree list; git -C "$FORK" status --short | head
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I8/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" b6252bb     # the one metadata write
git -C "$W/fork-wt" log --oneline -3; git -C "$W/fork-wt" status --short
ls "$W/fork-wt/ps2xRuntime/ios/"; grep -n SDL2main "$W/fork-wt/ps2xRuntime/CMakeLists.txt"

# --- Task 1: SDL2 device prebuilt (fresh clone, own dir) ---
git clone --depth 1 --branch release-2.32.10 https://github.com/libsdl-org/SDL.git "$W/SDL"
git -C "$W/SDL" rev-parse --short HEAD                          # 5d24957 (== I4)
env -u CC -u CXX cmake -S "$W/SDL" -B "$W/sdl2-build-device" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=$PWD/local/research/I8/logs/ios-device.toolchain.cmake \
  -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$W/sdl2-ios-device" \
  -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TEST=OFF               # exit 0
# (first build exit 1 on 2132 ._* sidecars -> purge + wipe + reconfigure, same flags)
find "$W/SDL" -name "._*" -delete; find "$W/fork-wt" -name "._*" -delete
cmake --build "$W/sdl2-build-device" --parallel 2               # [266/266], exit 0
cmake --install "$W/sdl2-build-device"                          # exit 0
lipo -info "$W/sdl2-ios-device/lib/libSDL2.a" "$W/sdl2-ios-device/lib/libSDL2main.a"

# --- Task 1: runtime configure + build (I7 shape, -j2) ---
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE=$PWD/local/research/I8/logs/ios-device.toolchain.cmake \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="$W/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -S "$W/fork-wt" -B "$W/ios-runtime-device"                   # exit 0 (71.4s+3.1s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2   # BUILD SUCCEEDED
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; file "$APP/ps2EntryRunner"
shasum -a 256 "$APP/ps2EntryRunner"
otool -l "$APP/ps2EntryRunner" | grep -A4 LC_BUILD_VERSION
nm -g "$APP/ps2EntryRunner" | grep -E " T _(SDL_main|SDL_UIKitRunApp|SDL_Init|InitWindow)$"
codesign -dvv "$APP"   # not signed at all (by design)

# --- Task 2: stage + sign (MF1 mechanism) + install ---
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
# (write 3-key entitlements.plist with LQ3V7772Q2.org.ps2x.ps2entryrunner; see logs/entitlements.plist)
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0
codesign --verify --strict "$SAPP"                              # exit 0
D="00008140-0002505001F3001C"
xcrun devicectl list devices --timeout 30   # 2 earlier bare calls pre-discovery; receipted re-run
xcrun devicectl device info lockState --device "$D" --timeout 30
xcrun devicectl device info details --device "$D" --timeout 30 --json-output "$W/logs/iphone-details.json"
xcrun devicectl device install app --device "$D" --timeout 180 "$SAPP"   # exit 1 first (CFBundleName), 0 after fix
# (CFBundleName fix -> reconfigure 11.4s -> rebuild -> re-stage -> re-sign -> install exit 0)
xcrun devicectl device info apps --device "$D" --timeout 60 | grep -i ps2x

# --- Task 2: launches + crash-log + screenshots ---
xcrun devicectl device process launch --device "$D" --timeout 120 --console \
  org.ps2x.ps2entryrunner >"$W/logs/launch-noarg-console.log" 2>&1        # A: exit 1, clean fatal
xcrun devicectl device process launch --device "$D" --timeout 120 --console \
  org.ps2x.ps2entryrunner /nonexistent-boot.elf >"$W/logs/launch-argv-console.log" 2>&1  # B: exit 2 (idle)
xcrun devicectl device process launch --device "$D" --timeout 30 --console --terminate-existing \
  org.ps2x.ps2entryrunner /nonexistent-boot.elf >"$W/logs/launch-argv2-console.log" 2>&1 # B2: exit 2, identical
xcrun devicectl device info files --device "$D" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i8 -s ps2EntryRunner --no-recurse  # 0 files
xcrun devicectl device process launch --device "$D" --timeout 60 --terminate-existing \
  org.ps2x.ps2entryrunner /nonexistent-boot.elf              # C: no-console, then:
xcrun devicectl device capture screenshot --device "$D" --timeout 60 --destination ~/i8-shot1.png
sleep 3; xcrun devicectl device capture screenshot --device "$D" --timeout 60 --destination ~/i8-shot2.png
mv ~/i8-shot1.png ~/i8-shot2.png "$W/logs/"
sleep 10; xcrun devicectl device info files ... -s ps2EntryRunner  # re-ls: 0 files
xcrun devicectl device process terminate --device "$D" --timeout 60 --pid <own-pid>  # cleanup only

# --- Fork commit + push (worktree only, named file, fork remote only) ---
WT="$W/fork-wt"
git -C "$WT" add ps2xRuntime/ios/Info.plist
git -C "$WT" commit -m "Bundle: set CFBundleName so devicectl installs the device .app (I8)" \
  -m "<body>" -m "Orchestrated-By: Muse Code"                   # 3006a07
git -C "$WT" push fork HEAD:refs/heads/i8-device-bundle-name    # exit 0, first try
git -C "$WT" ls-remote fork i8-device-bundle-name               # 3006a07 confirmed
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Property-level sim-audio trigger unisolated (category/mode/unit sequence?) | Miniaudio manages the session too (100 `AVAudioSession` hits) — blanket theories exhausted; sim shim hangs only on miniaudio's sequence | Raw-miniaudio sim probe brief (Task 3 option 3), ONLY if sim parity still matters — device is green |
| 2 | `loadELF`-fail path idles instead of exiting (plain `return` from `SDL_main`) | `main.cpp:236-240` + PIDs observed alive + `--console` timeouts | Harness-note brief (short `--timeout` + console text as fate); optional 1-line `_Exit(1)` for harness-friendliness (app-code, so recipe-only here) |
| 3 | `3006a07` rides topic branch `i8-device-bundle-name`, not `fork/ssx3` | Remote `ssx3` at E3b's `b34b481`, ahead of the pin; push receipt `logs/fork-push.log` | No code brief — merge/cherry-pick onto `ssx3` when E3b's line allows (trivial 1-file plist change) |
| 4 | First REAL boot path now observable (`loadELF` runs) but unmeasured | `Failed to open/load ELF` lines are the probe-path fate (I6 gap 6 / I7 gap 2 first observed) | Boot brief: ship a real ELF to the device container + argv probe to `run()` (the ONE next action) |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6/I7 carried) | 1× in device build log | Optional hardening brief (unchanged) |
| 6 | Standing rules extended for device | `--console` + healthy app = timeout (use short timeout); template edits need re-configure; purge `._*` before configure + staging | Standing measurement notes (extend I6/I7 rules) |

## Receipt paths

- `local/research/I8/REPORT.md` (this file)
- `local/research/I8/logs/ios-device.toolchain.cmake` (the derived device toolchain)
- `local/research/I8/logs/worktree-add.log`, `fork-commit.log`, `fork-push.log` (`3006a07` receipt + topic-branch push)
- `local/research/I8/logs/sdl2-configure2.log` (full), `sdl2-build2-tail.log`, `sdl2-install2.log`, `sdl2-build-first-error.log` (sidecar failure), `sdl2-warnings-uniq.log`
- `local/research/I8/logs/ios-runtime-configure.log` (full), `ios-runtime-configure2.log` (plist-refresh reconfigure), `ios-runtime-build-tail.log`, `ios-runtime-build3-tail.log`
- `local/research/I8/logs/nm-entry.log`, `build-version.log`, `nm-sdl-count.log`, `otool-L.log`, `codesign-unsigned.log`, `codesign-signed.log`, `Info.plist.txt`, `warnings-uniq.log`
- `local/research/I8/logs/iphone-details.json`, `lockstate.log`, `entitlements.plist`
- `local/research/I8/logs/install.log` (CFBundleName failure), `install2.log` (exit 0)
- `local/research/I8/logs/launch-noarg-console.log`, `launch-argv-console.log`, `launch-argv2-console.log` (complete consoles)
- `local/research/I8/logs/crashlog-recheck.log` (0 files after sleep + re-`ls`)
- `local/research/I8/logs/i8-window-live.png` (device window, 116 KB)
- `W/logs/` (same files + full build logs + `i8-shot2.png`); `W/ios-runtime-device/` (1.8 GB build tree); `W/SDL`, `W/sdl2-build-device`, `W/sdl2-ios-device` (SDL source/build/install); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `3006a07`)
- Fork `3006a07` on `fork i8-device-bundle-name` (pushed); base pin `b6252bb` (K1 P0, on `fork/ssx3`)

## What I could not do

- Isolate the property-level sim-audio trigger — needs the raw-miniaudio probe (gap 1); device evidence bounds it to (miniaudio sequence × sim shim).
- Boot a real ELF — no guest binary was shipped to the device (gap 4 owns it); `loadELF`'s success path + `run()` still unobserved.
- Merge `3006a07` onto `fork/ssx3` — E3b's line is ahead (gap 3; topic branch pushed instead).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I7); no crash occurred anyway.
- Screenshot a RENDERED frame — window is black (probe path never reaches `run()`); first presented content awaits gap 4.
- Explain the `passcodeRequired true→false` drift across the session — both readings tabled verbatim; no launch/install ever failed with `Locked`.
- Explain AppleDouble `._*` provenance on the ExFAT volume — counts + purge points tabled; counts were 0 at re-checks after purge.
- Debug-config codegen question — unchanged from I4 (Release only).
- The 74 Release-build warnings — still untriaged beyond the identifier warning's identification.

## TAIL RECEIPT

Report written in 4 chunks (header + contract + Task 0; Task 1; Task 2; Task 3 + commands + gaps + receipts). Pre-receipt measure: 311 lines, sha256 `f11f54e21c5a8002e9bc2be7cbe8767a0f7862e0a8aaca778df3cf27d202b147`.
Tail content line: "The 74 Release-build warnings — still untriaged beyond the identifier warning's identification." This receipt line ends the report. END-I8-REPORT.
