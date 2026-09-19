# I1 — iOS spike: what does the PS2Recomp runtime need to build for Simulator?

- Date: 2026-09-19. Target: iphonesimulator arm64, Debug.
- Source: fork clone `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch
  `ssx3` @ `e73e36a`, READ ONLY (no edits, commits, or pushes there; all
  configures used separate `-B` build dirs).
- Toolchain: written for this spike, not found in repo (v1 and v2 saved under
  `logs/`; v2 adds `CMAKE_SYSTEM_PROCESSOR`).
- Step 3 result: FAIL (4 attempts, 2 generators). Step 4 skipped per brief
  (build only if configure passes).

## Constraints obeyed (orchestrator amendment)

| Constraint | How obeyed |
|---|---|
| Simulator: only installed iOS 27.0 runtime + existing device | No runtime/platform/simulator download was run (no `-downloadPlatform`, no `xcodes install`). `simctl list` showed installed `iOS 27.0` runtime with existing devices incl. iPhone 17 (`4DE6C37C-77EF-45AE-827E-26286E68D022`). No device was booted: Step 4 was never reached. |
| Disk: scratch in `/tmp/ps2x-ios-spike`; >500 MB on `/Volumes/Extreme SSD/`; do not touch other agents' dirs | `/tmp/ps2x-ios-spike` holds only small files (104K: logs + toolchains). Heavy build dirs live on `/Volumes/Extreme SSD/` (`ps2x-ios-spike-attempt1` via symlink, `ps2x-ios-spike-attempt3`). Internal disk still shows 42 GB free. `/tmp/p1-link`, `/tmp/ps2xgs-build*`, and other agents' dirs were never listed, cleaned, or deleted. |

## Step 1 — Dep inventory

Fork paths below are under `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`
(`FORK/`); fetched-source paths are under the attempt-1 `_deps/`
(`DEPS/ = /Volumes/Extreme SSD/ps2x-ios-spike-attempt1/_deps/`, also readable
via `/tmp/ps2x-ios-spike/build-attempt1/_deps/`).

| Dep | Pin | iOS-ready | Evidence |
|---|---|---|---|
| raylib (window/input/GL/audio) | `5.5` (`FORK/ps2xRuntime/CMakeLists.txt:78-84`, full clone, no `GIT_SHALLOW`) | N | `DEPS/raylib-src/CMakeOptions.txt:5` enum rejects `iOS` (attempt-1 error); no `rcore_ios`/`PLATFORM_IOS` anywhere in `DEPS/raylib-src/src` (only `platforms/rcore_{android,desktop_glfw,desktop_rgfw,desktop_sdl,drm,template,web}.c`); 0 `UIKit`/`TARGET_OS_IPHONE` refs in bundled `src/external/glfw`; 0 in bundled `src/external/RGFW.h` (and no CMake option selects RGFW) |
| imgui (debug panel core) | `v1.92.7-docking` (`FORK/ps2xRuntime/CMakeLists.txt:87-92`, `GIT_SHALLOW`) | Y (core only) | Pure C++ widgets/draw (`DEPS/imgui-src/imgui.cpp` etc.); platform fitness rides on the rlImGui backend + a working raylib backend, neither of which exists for iOS here |
| rlImGui (debug panel backend) | `Raylib_5_5` (`FORK/ps2xRuntime/CMakeLists.txt:110-115`, `GIT_SHALLOW`) | unknown | Compiles against raylib+imgui APIs, but input is mouse/keyboard/gamepad only (`DEPS/rlimgui-src/rlImGui.cpp:60-63,849-883`); `grep -c GetTouch rlImGui.cpp` = 0. Android precedent gates the whole debug UI off (`NOT PS2X_IS_ANDROID`, `FORK/ps2xRuntime/CMakeLists.txt:86,513`) |
| Audio backend | raylib `raudio` -> bundled miniaudio (`DEPS/raylib-src/src/raudio.c`, `src/external/miniaudio.h`) | unknown | iOS CoreAudio path exists in miniaudio (`miniaudio.h:6874-6881` `ma_ios_*` session categories); unreachable without an iOS raylib backend, and raylib Desktop+APPLE links macOS-only `OpenGL` (`LibraryConfigurations.cmake:13-21`). Runtime side uses `Wave`/`Sound` API only (`FORK/ps2xRuntime/src/lib/ps2_audio.cpp:298-306`) |
| sse2neon (ARM `_mm_*` shim) | `v1.9.1` (`FORK/CMakeLists.txt:48-53`, `GIT_SHALLOW`) | Y (with toolchain fix) | Header-only; attempt 3 log shows `ARM target detected, fetching sse2neon` and `_deps/sse2neon-src` populated once the toolchain sets `CMAKE_SYSTEM_PROCESSOR=arm64`. Needed: runtime uses `_mm_*` unconditionally (`FORK/ps2xRuntime/src/lib/ps2_runtime.cpp:501-504`) |
| FFmpeg (MPEG decode) | none pinned; pkg-config host libs accepted | N (as configured) | Configure finds host macOS arm64 dylibs `libavcodec 63.1.101` etc. (`/opt/homebrew/Cellar/ffmpeg/9.0.1_1/lib`, `Mach-O 64-bit ... arm64` macOS dylib) for the iOS target; a macOS dylib cannot link into an iOS binary. Android precedent defaults it OFF (`FORK/ps2xRuntime/CMakeLists.txt:245-249`); non-Android path requires pkg-config (`:342-349`) |
| CMake | 4.4.3 present | Y | Project minima are 3.20/3.21 (`FORK/CMakeLists.txt:1`, `FORK/ps2xRuntime/CMakeLists.txt:1`, `FORK/ps2xIOP/CMakeLists.txt:1`); raylib emits only a `<3.10 compat` deprecation warning, then proceeds |
| Xcode / SDK / Simulator | Xcode 27.0 (27A266a), iphonesimulator SDK 27.0, installed SimRuntime iOS 27.0 | Y | `xcodebuild -version`, `xcrun --sdk iphonesimulator --show-sdk-version`, `simctl list devices available` (iPhone 17 `4DE6C37C-...` present, Shutdown) |

## Step 2 — Platform surface (what an iOS runtime file must implement)

Precedent sizes: `FORK/ps2xRuntime/src/lib/ps2_android_runtime.cpp` = **3
lines** (a TODO comment + empty `__ANDROID__` guard — the real Android shape
is CMake `SHARED` + `-Wl,--undefined=ANativeActivity_onCreate`
(`FORK/ps2xRuntime/CMakeLists.txt:451-456`) + `NativeActivity` manifest +
gradle `PS2X_DEFAULT_BOOT_ELF`); `ps2_vita_runtime.cpp` = **64 lines** (heap
sizes + `debugNet*` TTY overrides).

| Surface | Current shape (file:line) | iOS file must provide |
|---|---|---|
| Entry / boot ELF | `int main` in `FORK/ps2xRuntime/src/main.cpp:167`; ELF from `argv[1]` or `PS2X_DEFAULT_BOOT_ELF` (`src/main.cpp:143-164`); Android gets the path via gradle `-DPS2X_DEFAULT_BOOT_ELF`, Vita uses it directly (`:153-155`) | Boot-ELF resolution without `argv` (bundle path / default define); iOS entry must still reach `PS2Runtime::initialize` + `loadELF` + `run` (`src/main.cpp:217-239`) |
| Window | `SetConfigFlags(FLAG_WINDOW_RESIZABLE)` + `InitWindow(960x544)` in `PS2Runtime::initialize` (`src/lib/ps2_runtime.cpp:699-707`); Vita skips audio (`:699-700`) | Window creation on an iOS-capable backend (the missing piece: pinned raylib has none — G1/G2/G3) |
| Main-loop shape | `PS2Runtime::run` (`src/lib/ps2_runtime.cpp:2614-2743`): `std::thread` game thread (`EeScheduler::run`, `:2639-2658`) + host loop `UploadFrame` -> `BeginDrawing` -> `DrawTexturePro` -> debug-UI callback -> `EndDrawing` -> `WindowShouldClose` check (`:2694-2726`) | No new shape needed once a window exists; `WindowShouldClose`/backgrounding semantics on iOS need mapping |
| Input | Gamepad (`IsGamepadAvailable/ButtonDown/AxisMovement`) + keyboard (`IsKeyDown`) fallback in `src/lib/ps2_pad.cpp:41-123`; zero touch handling anywhere in runtime | Touch input (`GetTouch*` or overlay); Android file TODOs the same overlay (`ps2_android_runtime.cpp:1`) |
| Audio session | `InitAudioDevice()` + `IsAudioDeviceReady` in `initialize` (`:704-705`); `CloseAudioDevice` in dtor (`:549-555`); SPU sounds via `Wave`/`Sound` (`src/lib/ps2_audio.cpp:298-306`); Vita has no audio path | Audio-session init mapping to miniaudio CoreAudio once a backend exists (G3 blocks this) |
| Bundle / FS paths | `IoPaths{elfPath,elfDirectory,hostRoot,cdRoot,mcRoot,cdImage}` (`include/ps2_runtime.h:295-303`); defaults from `std::filesystem::current_path` (`src/lib/ps2_runtime.cpp:332-347`); `GetApplicationDirectory` for IOP plugins (Win/Linux only, `:487-494`); `PS2X_CD_IMAGE` env (`src/main.cpp:229-237`) | Bundle/app-container mapping for all six `IoPaths` (`current_path` is meaningless in a sandbox); env-var path is unavailable on device |
| Threads | `std::thread` game thread; `ThreadNaming::SetCurrentThreadName` has an `__APPLE__` branch using one-arg `pthread_setname_np` (`include/ThreadNaming.h:42-43`) | Already Apple-ready; no work |
| IOP plugins | Gated to Win/Linux (`src/lib/ps2_runtime.cpp:487-488,690-691`); `ps2xIOP` is plain C++20 static lib (`FORK/ps2xIOP/CMakeLists.txt:6-13`, plugins OFF by default) | No work (excluded by existing guards) |
| Graphics API | No direct GL in runtime (`grep rlgl\|glEnable` over `src/lib` + `include` = 0 hits); all GL goes through raylib/rlgl `GRAPHICS_API_*` | Backend selects GLES; blocked by G3 |
| Debug UI | `ps2_debug_panel.cpp` (2275 lines) + imgui/rlImGui, gated by `PS2X_ENABLE_DEBUG_UI AND NOT VITA AND NOT ANDROID` (`FORK/ps2xRuntime/CMakeLists.txt:513-519`) | Gate off for iOS (same one-line pattern as Android) or wire touch through rlImGui (G7) |

## Step 3 — Configure attempts (iphonesimulator arm64, Debug)

Scratch: `/tmp/ps2x-ios-spike` (fresh; small files only after the heavy dir
moved — see disk row). Toolchain v1/v2 recorded in `logs/` (written, not
found). FetchContent network access was used (raylib full clone 493 MB incl.
419 MB `.git`, imgui 23 MB, rlImGui 12 MB, sse2neon small); no other network
writes.

| Attempt | Setup | Result |
|---|---|---|
| 1 | Xcode gen, toolchain v1, `-DPLATFORM=iOS`, runtime-only (`RECOMP/ANALYZER/TEST/STUDIO=OFF`), `SCCACHE=OFF` | FAIL: `EnumOption.cmake:7` — `Unknown value iOS. Only -DPLATFORM=Desktop;Web;Android;Raspberry Pi;DRM;SDL allowed.` (G1) |
| 2 | Same build dir, `-DPLATFORM=Desktop` (flag retry, minutes; `_deps` reused) | FAIL: `ps2xRuntime/CMakeLists.txt:592 install()` — `given no BUNDLE DESTINATION for MACOSX_BUNDLE executable target "ps2EntryRunner"` (G4). raylib Desktop + imgui + rlImGui + host FFmpeg all configured past this point |
| 3 | New build dir on Extreme SSD, toolchain **v2** (`CMAKE_SYSTEM_PROCESSOR=arm64`, `CMAKE_OSX_ARCHITECTURES` forced), `_deps` reused via `FETCHCONTENT_SOURCE_DIR_*` | FAIL: same G4 error. `ARM target detected, fetching sse2neon` + `sse2neon-src` populated (G5 fixed by the retry) |
| 4 | Same as 3 but `-G Ninja` (generator retry for G4) | FAIL: identical G4 error — generator-independent, unfixable by flags |

### Gap rows

`status` = observed in a configure log, vs predicted (inspected in source;
no build was run, correctly, since configure never passed).

| ID | File | Error / finding | Fix class | Status |
|---|---|---|---|---|
| G1 | `DEPS/raylib-src/cmake/EnumOption.cmake:7` (via `CMakeOptions.txt:5`) | `Unknown value iOS. Only -DPLATFORM=Desktop;Web;Android;Raspberry Pi;DRM;SDL allowed.` No `rcore_ios`/`PLATFORM_IOS` in pinned raylib | dep-code | observed (attempt 1) |
| G2 | `DEPS/raylib-src/src/external/glfw/*` | 0 `UIKit`/`TARGET_OS_IPHONE` refs: bundled GLFW has no iOS path, so `PLATFORM_DESKTOP` cannot target the iOS SDK | dep-code | predicted build failure (inspected) |
| G3 | `DEPS/raylib-src/cmake/LibraryConfigurations.cmake:13-21` | Desktop+APPLE hardcodes `GRAPHICS_API_OPENGL_33` + `find_library(OpenGL)`; iOS SDK ships only OpenGLES | dep-code | predicted build failure (inspected) |
| G4 | `FORK/ps2xRuntime/CMakeLists.txt:592` | `install TARGETS given no BUNDLE DESTINATION for MACOSX_BUNDLE executable target "ps2EntryRunner"` — needs a repo CMake edit; fork is READ ONLY so no retry can pass it | config | observed (attempts 2, 3, 4) |
| G5 | `FORK/CMakeLists.txt:30-37` | Xcode generator leaves `CMAKE_SYSTEM_PROCESSOR` unset, silently skipping the sse2neon block while code uses `_mm_*` (`src/lib/ps2_runtime.cpp:501`); toolchain v2 (`set(CMAKE_SYSTEM_PROCESSOR arm64)`) fixes it — attempt 3 confirms | config | observed, fixed by retry |
| G6 | `FORK/ps2xRuntime/CMakeLists.txt:342-352` (pkg-config path) | Host macOS arm64 FFmpeg dylibs (63.1.101, `/opt/homebrew`) accepted for the iOS target; cannot link into an iOS binary. Mirror Android (`PS2X_ENABLE_FFMPEG=OFF`, `:245-249`) or ship an iOS FFmpeg build | config | observed at configure / predicted at link |
| G7 | `DEPS/rlimgui-src/rlImGui.cpp` (whole file) | 0 `GetTouch` refs; input is mouse/keyboard/gamepad only (`:60-63,849-883`); no touch code anywhere in runtime either | platform-code | inspected |

## Step 4 — Build attempt

Not run: Step 3 did not pass (blocked by G4 on all attempts/generators), and
the brief allows a build only if configure passes. No install to Simulator,
no launch, no first-window/crash log.

## Effort read (counts by class, not a verdict)

| Fix class | Gaps |
|---|---|
| dep-code (pinned raylib has no iOS windowing/input/GL path: G1, G2, G3) | 3 |
| config (G4 install rule, G5 toolchain var, G6 FFmpeg) | 3 |
| platform-code (G7 touch input) | 1 |
| flag | 0 |
| **Total** | **7** |

G5 is already resolved by the recorded toolchain-v2 retry. G1/G2/G3 share one
root (no iOS backend in raylib 5.5 as pinned). G4 is the single gate in front
of any build attempt.

## Exact commands

```sh
# scratch + toolchain (written, not found)
rm -rf /tmp/ps2x-ios-spike && mkdir -p /tmp/ps2x-ios-spike
# v1: CMAKE_SYSTEM_NAME=iOS, CMAKE_OSX_SYSROOT=iphonesimulator,
#     CMAKE_OSX_ARCHITECTURES=arm64, ONLY_ACTIVE_ARCH=YES  (logs/ios-simulator.toolchain.cmake)
# v2: v1 + CMAKE_SYSTEM_PROCESSOR=arm64, arch forced in cache  (logs/ios-simulator.toolchain.v2.cmake)

# attempt 1 (FAIL G1)
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE=/tmp/ps2x-ios-spike/ios-simulator.toolchain.cmake \
  -DCMAKE_CONFIGURATION_TYPES=Debug -DPLATFORM=iOS \
  -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF \
  -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -S "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" -B /tmp/ps2x-ios-spike/build-attempt1

# attempt 2 (FAIL G4) — same build dir, _deps reused
cmake -DPLATFORM=Desktop .

# attempt 3 (FAIL G4; G5 fixed) — build dir on Extreme SSD, sources reused
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE=/tmp/ps2x-ios-spike/ios-simulator.toolchain.v2.cmake \
  -DCMAKE_CONFIGURATION_TYPES=Debug -DPLATFORM=Desktop \
  -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF \
  -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB=/tmp/ps2x-ios-spike/build-attempt1/_deps/raylib-src \
  -DFETCHCONTENT_SOURCE_DIR_IMGUI=/tmp/ps2x-ios-spike/build-attempt1/_deps/imgui-src \
  -DFETCHCONTENT_SOURCE_DIR_RLIMGUI=/tmp/ps2x-ios-spike/build-attempt1/_deps/rlimgui-src \
  -S "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" \
  -B "/Volumes/Extreme SSD/ps2x-ios-spike-attempt3/build"

# attempt 4 (FAIL G4, generator-independent) — same flags as 3 with -G Ninja
# -B "/Volumes/Extreme SSD/ps2x-ios-spike-attempt3/build-ninja", -DCMAKE_BUILD_TYPE=Debug

# heavy-dir move (disk amendment): mv build-attempt1 to Extreme SSD, symlink back
mv /tmp/ps2x-ios-spike/build-attempt1 "/Volumes/Extreme SSD/ps2x-ios-spike-attempt1" \
  && ln -s "/Volumes/Extreme SSD/ps2x-ios-spike-attempt1" /tmp/ps2x-ios-spike/build-attempt1
```

Key inspection receipts: `grep -rln PLATFORM_IOS|TARGET_OS_IPHONE
DEPS/raylib-src/src` -> only `external/miniaudio.h`; `grep -rln
UIKit|TARGET_OS_IPHONE DEPS/raylib-src/src/external/glfw` -> 0 hits; `grep
-n UIKit|TARGET_OS_IPHONE DEPS/raylib-src/src/external/RGFW.h` -> 0 hits;
`grep -c GetTouch DEPS/rlimgui-src/rlImGui.cpp` -> 0; `grep -rn
rlgl|glEnable FORK/ps2xRuntime/src/lib FORK/ps2xRuntime/include` -> 0 hits;
`pkg-config --modversion libavcodec` -> 63.1.101;
`file /opt/homebrew/lib/libavcodec.dylib` -> `Mach-O 64-bit ... arm64`
(macOS); `wc -l` android runtime 3 / vita runtime 64 / main.cpp 260 /
ps2_runtime.cpp 2743 / ps2_debug_panel.cpp 2275.

## Receipt paths

- `local/research/I1/REPORT.md` (this file)
- `local/research/I1/logs/configure-attempt1.log` (G1), `configure-attempt2.log`
  (G4, Xcode), `configure-attempt3.log` (G4 + sse2neon fetch, Xcode),
  `configure-attempt4-ninja.log` (G4, Ninja)
- `local/research/I1/logs/ios-simulator.toolchain.cmake` (v1),
  `ios-simulator.toolchain.v2.cmake` (v2)
- Scratch: `/tmp/ps2x-ios-spike` (104K: logs + toolchains + symlink);
  `/Volumes/Extreme SSD/ps2x-ios-spike-attempt1` (attempt-1 `_deps`: raylib
  493 MB / imgui 23 MB / rlImGui 12 MB);
  `/Volumes/Extreme SSD/ps2x-ios-spike-attempt3/build{,-ninja}` (attempt 3/4)

## What I could not do

- Build any target (blocked by G4 before compilation); so sse2neon compile
  for arm64-ios, miniaudio CoreAudio init on Simulator, and the FFmpeg link
  failure are all unobserved, not confirmed.
- Install to a booted Simulator / launch / record first window or crash log
  (needs a built binary; game ISO out of scope in any case).
- Device follow-ups this spike cannot answer: signing (nothing here needed a
  paid dev account or signing), bundle resources (ELF/CD-image/MC packaging
  into the app bundle), touch input end-to-end, Metal-vs-GL (pinned raylib
  speaks only GL variants; iOS Simulator supports GLES, device prefers
  Metal — no backend exists here for either on iOS).

## Incidental note (not caused by this spike)

The fork working tree contains one pre-existing modification outside this
spike's scope: `ps2xRuntime/src/runner/register_functions.cpp` (+398773/-5,
mtime 2026-09-18 23:37, before this session). It was inspected read-only via
`git diff` and left untouched.
