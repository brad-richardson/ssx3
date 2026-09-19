# I4 — SDL2-for-iOS build + raylib-SDL integration to a runtime configure (tables, no verdicts)

- Date: 2026-09-19. Runbook `local/muse/prompts/I4.md` (raylib-wall Option C). Tables, no verdicts, no recommendation.
- I3 (`local/research/I3/REPORT.md`, all of Step 3: C2 shape, TU probes, SDL-version wrinkle, C1–C5) + I2 (toolchain v2, G4/G5/G6) read first.
- Fork: `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`, base `de7ff17` → 2 CMake-only commits → `53bac61`; `fork ssx3` pushed (`ls-remote` confirms `53bac61`, first try, no rebase). Only `ps2xRuntime/CMakeLists.txt` staged/committed.
- Shared-tree note: P1u agent active concurrently. Their commit `de7ff17` (P22-2) landed as my base mid-run (was `58c9144` at session start); their `ps2xRuntime/src/runner/register_functions.cpp` (398k-line diff) stayed `M` (unstaged) throughout and was never staged. Desktop builds below compiled the tree including it.
- Rules honored: no lease (no emulator/Simulator boots); no `adb`; no `simctl`; one commit per change with the two P-series trailers; `git push` ONLY in the fork clone to `fork` (this report's `[I4]` commit in ssx3 is NOT pushed).
- Disk: ALL clones/builds/installs on `/Volumes/Extreme SSD/ps2x-i4/`; internal disk holds only this report + small logs. `/tmp/p1-link`, `/tmp/ps2xgs-build*`, `/tmp/ps2x-ios-spike`, `ps2x-i3`, other agents' dirs never touched. (`._*` AppleDouble sidecars purged in own dirs + fork tree per P1/I2 precedent; `COPYFILE_DISABLE=1` on desktop builds.)
- Simulator: installed iOS 27.0 SDK only (`xcrun --show-sdk-path` → `iPhoneSimulator27.0.sdk`, Xcode 27.0 27A266a, Apple clang 21.0.0); no runtime/platform download. Device slice not attempted (simulator path + box time; scope rule).
- Network reads + source clones only: SDL `release-2.32.10`, raylib `5.5`, fresh FetchContent clones (imgui/rlImGui/sse2neon). No pushes outside `fork ssx3`, no PRs.
- Compiler choice: AppleClang (`/usr/bin/cc`, `env -u CC -u CXX`) for Steps 1–2 to match the Step-3 Xcode-generator runtime configure on one toolchain (I3 C2 used homebrew LLVM clang; recorded, not re-verified here).

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i4/`, `FORK` = fork clone, `TC` = `W/ios-sim.toolchain.cmake` (I4 Ninja toolchain: I1 v2 + `CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY`).

## Step 1 — SDL2 for iphonesimulator (no fork writes)

Source: `release-2.32.10` (`5d24957`, matches I3), shallow clone to `W/SDL`. Flags: `-G Ninja`, I4 toolchain, `Release`, `SDL_SHARED=OFF SDL_STATIC=ON SDL_TEST=OFF`, prefix `W/sdl2-ios-sim`. First attempt; no retry needed.

| Item | Receipt |
|---|---|
| Configure | exit 0: `Configuring done (195.9s) / Generating done (1.1s) / Build files written to W/sdl2-build-sim` (`logs/sdl2-configure-tail.log`) |
| Build | exit 0: `[266/266] Linking C static library libSDL2.a`; diagnostics = Metal `supportsFeatureSet:` iOS-27 deprecation warnings only (`logs/sdl2-build-tail.log`) |
| Install | exit 0; `lib/libSDL2.a` (2163368 bytes, `lipo: Non-fat arm64`, 187 objects) + `lib/libSDL2main.a` (`lipo: Non-fat arm64`; `main`→`SDL_UIKitRunApp`, `SDL_main` undefined-as-expected); 79 headers under `include/SDL2/` |
| Consumer config | `lib/cmake/SDL2/SDL2Config.cmake`: `SDL2::SDL2` ALIAS → `SDL2::SDL2-static` for static-only builds (CMake ≥3.18; have 4.4.3) — exactly what raylib's `LIBS_PRIVATE SDL2::SDL2` needs; `SDL2-staticTargets.cmake:65` exports `m, pthread` + iOS frameworks (CoreVideo, CoreAudio, AudioToolbox, AVFoundation, CoreBluetooth, CoreGraphics, Coremotion, Foundation, GameController[weak], Metal, OpenGLES, QuartzCore, UIKit, CoreHaptics[weak]) |
| Cache record | `CMAKE_C_COMPILER=/usr/bin/cc`, `CMAKE_OSX_SYSROOT=iphonesimulator`, `CMAKE_OSX_ARCHITECTURES=arm64`, `SDL_SHARED=OFF/SDL_STATIC=ON/SDL_TEST=OFF`, `CMAKE_BUILD_TYPE=Release` |
| Size note | `du` reports 209M for the install prefix (ExFAT cluster inflation on small files; real lib is 2.1M); SSD has 639G free |

## Step 2 — raylib-SDL against it (no fork writes yet)

Source: pinned raylib `5.5` (`c1ab645`, verified), shallow clone to `W/raylib-5.5`. Shape: C2 + `-DSDL2_DIR=W/sdl2-ios-sim/lib/cmake/SDL2`.

| Attempt | Setup | Result |
|---|---|---|
| 1 (direct) | `-DPLATFORM=SDL -DOPENGL_VERSION="ES 2.0" -DBUILD_EXAMPLES=OFF`, build dir `W/raylib-sdl-sim` | Configure exit 0 (`PLATFORM_DESKTOP_SDL` + `GRAPHICS_API_OPENGL_ES2`, `logs/raylib-configure.log`). Build exit 1: first failure `raudio.c.o` — ObjC-in-C, 20 errors from `NSObjCRuntime.h` (`NSString` unknown), matching I3's syntax probe (`logs/raylib-build-attempt1-first-error.log`) |
| 2 (one retry variant) | Fresh dir `W/raylib-sdl-sim-objc` + `-DCMAKE_C_FLAGS="-x objective-c"` | Configure exit 0; build exit 0: `[8/8] Linking C static library raylib/libraylib.a` (warnings only, e.g. `ALIGN` vs `arm/param.h`). Product: `libraylib.a`, Non-fat arm64, 1940168 bytes; `build.ninja` shows `-DGRAPHICS_API_OPENGL_ES2 -DPLATFORM_DESKTOP_SDL`, `-x objective-c` in FLAGS, Step-1 `-I` paths (`logs/raylib-build-objc-tail.log`) |

ObjC-mode handling (how CMake selects it): raylib's own CMake selects nothing — the consumer must add `-x objective-c`. Integration rehearsal (`W/linkprobe`, FetchContent-raylib + consumer exe) fixed the mechanism:

| Probe | Mechanism | Result |
|---|---|---|
| linkprobe build 1 | `-x objective-c` via `CMAKE_C_FLAGS` | FAIL at exe link: `-x` also hit the link line, clang re-parsed `main.c.o` as ObjC source (`source file is not valid UTF-8`, 20 errors) |
| linkprobe build 2 | `target_compile_options(raylib PRIVATE -x objective-c)` from parent scope after `FetchContent_MakeAvailable` | PASS (exit 0): `probe.app/probe` Mach-O 64-bit arm64; `raylib INTERFACE_LINK_LIBRARIES=SDL2::SDL2` (plain-signature link propagates); link line contains Step-1 `libSDL2.a` + UIKit et al; `otool -L` shows the SDL framework set (`logs/linkprobe-build2-tail.log`) |

Finding carried to Step 3: the `-x` flag must be compile-scoped via `target_compile_options` on the raylib target (works from parent scope, Xcode generator included — verified below).

## Step 3 — fork integration (CMake-only commits, then configure)

### Fork diffs (2 commits, both trailers, pushed)

| # | Commit | File | Change |
|---|---|---|---|
| 1 | `4eb7a8e` | `ps2xRuntime/CMakeLists.txt` | `elseif(PS2X_IS_IOS)`: `PLATFORM=SDL` + `OPENGL_VERSION="ES 2.0"` (cache FORCE, Android-block pattern); `FATAL_ERROR` when `SDL2_DIR` unset. SDL2 via `SDL2_DIR` passthrough, NOT FetchContent — why: cache var flows into the raylib sub-configure (I3 C2 shape), keeps SDL's ~196s configure out of every runtime configure, reuses the Step-1 prebuilt bit-for-bit |
| 2 | `53bac61` | `ps2xRuntime/CMakeLists.txt` | After `FetchContent_MakeAvailable(raylib)`: `if(PS2X_IS_IOS) target_compile_options(raylib PRIVATE -x objective-c)` — compile-scoped per the linkprobe finding (`CMAKE_C_FLAGS` form poisons links) |

Both blocks are guarded by `PS2X_IS_IOS` (OFF when `CMAKE_SYSTEM_NAME=Darwin`): desktop-inert by construction. What was deliberately NOT changed: debug-UI gating (imgui/rlImGui still build on iOS; G7 touch gap unchanged), `SDL2main` linkage (not linked: entry/lifecycle mapping stays open for I5 — with SDL2main unlinked, `main.cpp`'s `main` still links normally), no Vita/Android stanza touched.

### Diff 1 — iOS SDL selection (`4eb7a8e`)

```diff
     if(PS2X_IS_ANDROID)
         set(PLATFORM "Android" CACHE STRING "" FORCE)
+    elseif(PS2X_IS_IOS)
+        # I4: iOS uses raylib's SDL backend (raylib-wall Option C) with GLES2.
+        # SDL2 itself comes from a prebuilt SDL2-for-iOS via SDL2_DIR
+        # passthrough (SDL2_DIR is a cache var, so it flows into the raylib
+        # FetchContent configure): no FetchContent for SDL, keeping SDL's own
+        # configure out of every runtime configure and reusing one proven
+        # prebuilt bit-for-bit.
+        set(PLATFORM "SDL" CACHE STRING "" FORCE)
+        set(OPENGL_VERSION "ES 2.0" CACHE STRING "" FORCE)
+        if(NOT SDL2_DIR)
+            message(FATAL_ERROR "PS2X: iOS builds need -DSDL2_DIR=<SDL2-for-iOS install>/lib/cmake/SDL2 (prebuilt SDL2 release-2.32.10 for iphonesimulator)")
+        endif()
     endif()
```

### Diff 2 — raylib ObjC compile mode (`53bac61`)

```diff
     FetchContent_MakeAvailable(raylib)
+
+    if(PS2X_IS_IOS)
+        # I4: miniaudio (raylib raudio.c) includes AVFoundation on Apple
+        # targets, so the raylib TU set compiles as ObjC. Scoped to the raylib
+        # target on purpose: -x in CMAKE_C_FLAGS would also poison link lines.
+        target_compile_options(raylib PRIVATE -x objective-c)
+    endif()
```

### Desktop-proof table (Ninja, macOS arm64, Release, `PS2X_BUILD_STUDIO=OFF`)

Build dir `W/desktop` (fresh; fully fresh FetchContent, no `_deps` reuse). Baseline built BEFORE any fork edit; reconfigure+retest AFTER both commits (same dir).

| Fix | Desktop-neutral evidence |
|---|---|
| Baseline (pre-edit) | Configure exit 0 (264.3s); build exit 0 (`ps2EntryRunner` linked); `ps2xTest` 425/424/1, failing = `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` (same test as I2's pre-existing failure) |
| After `4eb7a8e` + `53bac61` | Reconfigure exit 0 (25.2s); rebuild: `ninja: no work to do` (zero compile inputs changed); `ps2xTest` 425/424/1, failing = same `sceGsSyncVCallback` test |
| Structural | Both new blocks sit under `PS2X_IS_IOS` (= OFF on Darwin); `ninja: no work to do` confirms no desktop compile line changed |

### Runtime configure for iphonesimulator (I2 pattern, new SSD dir)

`cmake -G Xcode`, I1 `ios-simulator.toolchain.v2.cmake`, `Debug`, runtime-only flags (`RECOMP/ANALYZER/TEST/STUDIO OFF`, `SCCACHE OFF`), `-DSDL2_DIR=<Step-1 config>`, `-DFETCHCONTENT_SOURCE_DIR_RAYLIB=W/raylib-5.5` (own Step-2 clone; imgui/rlImGui/sse2neon fresh network), `-B W/ios-runtime`.

| Probe | Result |
|---|---|
| Runtime configure | PASS (exit 0): `Configuring done (55.6s) / Generating done (17.7s)`; `FFmpeg disabled; MPEG video decode falls back to stub frames` (G6 path); rlImGui/imgui/sse2neon populated; generated raylib Xcode project contains `GRAPHICS_API_OPENGL_ES2`, `-x objective-c`, `PLATFORM_DESKTOP_SDL` (commit 2 propagates under Xcode) (`logs/ios-runtime-configure-tail.log`) |
| Raylib-wall clearance | G1 gone (`PLATFORM=SDL` accepted by raylib enum — no `EnumOption` error); G3 gone (SDL stanza runs no `find_library(OpenGL)` — no `OPENGL_LIBRARY NOTFOUND`); G2 sidestepped (no GLFW configured) |

### Runtime build for iphonesimulator (attempt + one retry variant)

| Attempt | Setup | Result |
|---|---|---|
| 1 | `--config Debug` in `W/ios-runtime` | No error and no completion: log froze at 3251 lines / 0 `error:` for 45+ min on the last TU (289/290 unity objects). `unity_0` contains `register_functions.cpp` (32MB, 398775 lines, P1u WIP, unchanged all session); `sample` shows clang-23 at 100% in `llvm::Localizer::localizeIntraBlock` (-O0 codegen pathology on a giant function). Terminated after the retry succeeded (`logs/ios-runtime-build-debug-stall.log`) |
| 2 (one retry variant) | Fresh dir `W/ios-runtime-rel`, `CMAKE_CONFIGURATION_TYPES=Release`, `--config Release` (only the config changed; Debug evidence above is the justification) | BUILD SUCCEEDED (exit 0, 0 errors, 80 warnings). Product: `ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app/ps2EntryRunner`, Mach-O 64-bit arm64, 120264240 bytes; 292 `T _SDL_` symbols; `_InitWindow` + `_SDL_Init` present; `otool -L` = libSystem + the SDL framework set (CoreVideo…UIKit, OpenGLES, AVFAudio, …) (`logs/ios-runtime-build-tail.log`) |

Compiler-provenance note: the runtime configures ran with env `CC=/opt/homebrew/opt/llvm/bin/clang` (not unset), so the Xcode projects compile with homebrew clang-23 while Steps 1–2 used AppleClang (`/usr/bin/cc`). Same target triple, static libs; the Release link across the two proves they compose. Not re-run single-compiler.

## Exact commands

```sh
# --- Step 1: SDL2 release-2.32.10 for iphonesimulator arm64 (all on SSD) ---
mkdir -p "/Volumes/Extreme SSD/ps2x-i4"
git clone --depth 1 --branch release-2.32.10 https://github.com/libsdl-org/SDL.git "/Volumes/Extreme SSD/ps2x-i4/SDL"
# toolchain W/ios-sim.toolchain.cmake = I1 v2 + CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY (content in Receipt paths)
find "/Volumes/Extreme SSD/ps2x-i4" -name "._*" -delete
env -u CC -u CXX cmake -S W/SDL -B W/sdl2-build-sim -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=W/ios-sim.toolchain.cmake -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=W/sdl2-ios-sim -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TEST=OFF
cmake --build W/sdl2-build-sim            # [266/266] libSDL2.a
cmake --install W/sdl2-build-sim
lipo -info W/sdl2-ios-sim/lib/libSDL2.a W/sdl2-ios-sim/lib/libSDL2main.a
ar t W/sdl2-ios-sim/lib/libSDL2main.a; nm -g W/sdl2-ios-sim/lib/libSDL2main.a

# --- Step 2: raylib 5.5 PLATFORM=SDL ES2 against Step-1 SDL2 ---
git clone --depth 1 --branch 5.5 https://github.com/raysan5/raylib.git W/raylib-5.5
env -u CC -u CXX cmake -S W/raylib-5.5 -B W/raylib-sdl-sim -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=W/ios-sim.toolchain.cmake -DCMAKE_BUILD_TYPE=Release \
  -DPLATFORM=SDL -DOPENGL_VERSION="ES 2.0" -DBUILD_EXAMPLES=OFF \
  -DSDL2_DIR=W/sdl2-ios-sim/lib/cmake/SDL2
cmake --build W/raylib-sdl-sim            # exit 1: raudio.c.o ObjC-in-C (first failure)
env -u CC -u CXX cmake -S W/raylib-5.5 -B W/raylib-sdl-sim-objc -G Ninja \
  ... (same) -DCMAKE_C_FLAGS="-x objective-c"
cmake --build W/raylib-sdl-sim-objc       # exit 0: libraylib.a arm64
lipo -info W/raylib-sdl-sim-objc/raylib/libraylib.a
# linkprobe: W/linkprobe/{CMakeLists.txt,main.c} (FetchContent raylib + target_compile_options + probe exe)
env -u CC -u CXX cmake -S W/linkprobe -B W/linkprobe-build2 -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=W/ios-sim.toolchain.cmake -DSDL2_DIR=W/sdl2-ios-sim/lib/cmake/SDL2
cmake --build W/linkprobe-build2          # exit 0: probe.app/probe arm64

# --- Step 3: fork commits (named file only) + push (fork clone ONLY) ---
cd "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"
git add ps2xRuntime/CMakeLists.txt   # commit 1 (4eb7a8e), then commit 2 (53bac61), each with the two P-series trailers
git push fork ssx3                   # first try; ls-remote confirms 53bac61

# desktop baseline (pre-edit) + post-edit reconfigure + test
cmake -S FORK -B W/desktop -G Ninja -DPS2X_BUILD_STUDIO=OFF -DCMAKE_BUILD_TYPE=Release
find W/desktop -name "._*" -delete; COPYFILE_DISABLE=1 cmake --build W/desktop
(cd FORK && W/desktop/ps2xTest/ps2x_tests)                    # baseline 425/424/1
cmake -S FORK -B W/desktop                                    # post-edit reconfigure
COPYFILE_DISABLE=1 cmake --build W/desktop                    # ninja: no work to do
(cd FORK && W/desktop/ps2xTest/ps2x_tests)                    # post-edit 425/424/1, same failure

# runtime iOS configure (I2 pattern) + build attempt (-DPLATFORM NOT passed; fork sets PLATFORM=SDL)
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE=/Users/bradrichardson/dev/ssx3/local/research/I1/logs/ios-simulator.toolchain.v2.cmake \
  -DCMAKE_CONFIGURATION_TYPES=Debug \
  -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF \
  -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR=W/sdl2-ios-sim/lib/cmake/SDL2 \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB=W/raylib-5.5 \
  -S FORK -B W/ios-runtime                          # exit 0
cmake --build W/ios-runtime --config Debug          # stalls in -O0 codegen (see Runtime build row); terminated
# retry: same with -DCMAKE_CONFIGURATION_TYPES=Release -B W/ios-runtime-rel, then:
cmake --build W/ios-runtime-rel --config Release    # BUILD SUCCEEDED -> ps2EntryRunner.app arm64
```

## Receipt paths

- `local/research/I4/REPORT.md` (this file)
- `local/research/I4/logs/sdl2-configure-tail.log`, `sdl2-build-tail.log`
- `local/research/I4/logs/raylib-configure.log`, `raylib-build-attempt1-first-error.log`, `raylib-build-objc-tail.log`
- `local/research/I4/logs/linkprobe-build2-tail.log`
- `local/research/I4/logs/ios-runtime-configure-tail.log`, `ios-runtime-build-debug-stall.log`, `ios-runtime-build-tail.log`
- `W/ios-sim.toolchain.cmake` (I4 toolchain), `W/sdl2-ios-sim/` (install), `W/raylib-sdl-sim-objc/raylib/libraylib.a`
- SSD scratch (not committed): `W/{SDL,sdl2-build-sim,raylib-5.5,raylib-sdl-sim,raylib-sdl-sim-objc,linkprobe,linkprobe-build,linkprobe-build2,desktop,ios-runtime,ios-runtime-rel,logs/}`
- Fork commits `4eb7a8e`, `53bac61` on `fork ssx3` (base `de7ff17`)

## What I could not do

- Entry/lifecycle mapping: `SDL_main`/`SDL_UIKitRunApp` interplay with `PS2Runtime::run` untested; `SDL2main` deliberately unlinked (I5).
- Device slice (`ios-arm64`): not attempted per scope rule (simulator first).
- First Simulator launch / window / crash log (no boots in this brief; I5 owns first launch).
- Debug-config codegen: `--config Debug` never completed (Localizer stall, 289/290); only Release is proven. Whether Debug finishes given hours, or needs batch-size/`-mllvm` mitigation, is unmeasured (one retry used).
- The 80 Release-build warnings are un-triaged (counts only).
- No Simulator boot/install/launch (per brief); the Release `.app` has never run. No window, crash log, touch/keyboard/MFi, audio-session, or GLES-render verification.
- Anything on device (signing, bundle/`IoPaths` sandbox, Metal-vs-deprecated-GLES behavior) — unchanged from I3.
