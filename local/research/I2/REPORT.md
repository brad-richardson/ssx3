# I2 — iOS fork fixes: BUNDLE DESTINATION + FFmpeg default + sse2neon guard, then configure

- Date: 2026-09-19. Runbook `local/muse/prompts/I2.md`. Tables, no verdicts.
- Fork: `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`,
  base `e73e36a` → 3 CMake-only commits → `66d992c`; `fork ssx3` pushed
  (`ls-remote` confirms `66d992c`). No other files staged or committed.
- I1 (`local/research/I1/REPORT.md`, all of it + v1/v2 toolchains) read first.
- Lease `I2` not taken (CMake only, no emulator boots). No `adb`. No Simulator
  launch. No runtime/platform download (only the installed iOS 27.0 SDK path
  was used; `xcrun --sdk iphonesimulator --show-sdk-version` = 27.0,
  Xcode 27.0 27A266a; no `simctl` invocation at all).
- Disk: all heavy build dirs on `/Volumes/Extreme SSD/`; I1 `_deps` reused via
  `FETCHCONTENT_SOURCE_DIR_*` (raylib/imgui/rlImGui sources from
  `ps2x-ios-spike-attempt1`, sse2neon source from `ps2x-ios-spike-attempt3`);
  raylib was NOT re-cloned. `/tmp/p1-link`, `/tmp/ps2xgs-build*`, and other
  agents' dirs never listed, cleaned, or deleted. Small logs only in
  `/tmp/ps2x-i2/`.
- Shared-tree note: a P1s agent edited the same fork worktree concurrently
  (`ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, then committed `be01146` on
  top of `66d992c` after my push; `register_functions.cpp` stayed `M`
  throughout). My commits contain only the two CMake files; their files were
  never staged. Push went through first try (no rebase needed). The desktop
  build below compiled the tree including the then-uncommitted P1s edit.

## Step 1 — three CMake fixes (one commit each)

| # | Gap | Commit | File | Change |
|---|---|---|---|---|
| 1 | G4 | `abc6f6c` | `ps2xRuntime/CMakeLists.txt` | Apple-only `install()` stanza adds `BUNDLE DESTINATION bin`; non-Apple stanza unchanged |
| 2 | G6 | `d62c4b5` | `ps2xRuntime/CMakeLists.txt` | New `PS2X_IS_IOS` detector (`CMAKE_SYSTEM_NAME STREQUAL "iOS"`); `PS2X_ENABLE_FFMPEG` default OFF when `PS2X_IS_ANDROID OR PS2X_IS_IOS` |
| 3 | G5 | `66d992c` | `CMakeLists.txt` (top) | ARM inference from `CMAKE_OSX_ARCHITECTURES` (arm64) or ARM-only Apple OS (`iOS\|tvOS\|watchOS\|visionOS`) with STATUS note; `FATAL_ERROR` when still unknown while cross-compiling |

All three carry the two P-series trailers (`Co-Authored-By: Claude Fable 5.1
<noreply@anthropic.com>`, `Claude-Session:
https://claude.ai/code/session_01H9JEyNpHtANpAU2dB1YuC7`).

### Diff 1 — G4 (`abc6f6c`)

```diff
-install(TARGETS ps2_runtime ps2EntryRunner
-    RUNTIME DESTINATION bin
-    LIBRARY DESTINATION lib
-    ARCHIVE DESTINATION lib
-)
+if(APPLE)
+    # iOS/tvOS/watchOS executables are bundles: install() requires a BUNDLE
+    # DESTINATION for them. No-op on macOS desktop (ps2EntryRunner is not a
+    # MACOSX_BUNDLE there, so no extra install rule is generated).
+    install(TARGETS ps2_runtime ps2EntryRunner
+        RUNTIME DESTINATION bin
+        LIBRARY DESTINATION lib
+        ARCHIVE DESTINATION lib
+        BUNDLE DESTINATION bin
+    )
+else()
+    install(TARGETS ps2_runtime ps2EntryRunner
+        RUNTIME DESTINATION bin
+        LIBRARY DESTINATION lib
+        ARCHIVE DESTINATION lib
+    )
+endif()
```

### Diff 2 — G6 (`d62c4b5`)

```diff
+set(PS2X_IS_IOS OFF)
+
+if(CMAKE_SYSTEM_NAME STREQUAL "iOS")
+    set(PS2X_IS_IOS ON)
+endif()
@@
-if(PS2X_IS_ANDROID)
+if(PS2X_IS_ANDROID OR PS2X_IS_IOS)
     set(PS2X_ENABLE_FFMPEG_DEFAULT OFF)
```

### Diff 3 — G5 (`66d992c`)

```diff
 elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^arm|^ARM")
     set(PS2X_IS_ARM_TARGET ON)
+elseif(CMAKE_OSX_ARCHITECTURES MATCHES "arm64|aarch64")
+    # The Xcode generator leaves CMAKE_SYSTEM_PROCESSOR unset; honor the
+    # requested Apple architectures instead so sse2neon still fetches.
+    message(STATUS "CMAKE_SYSTEM_PROCESSOR unset; inferring ARM target from CMAKE_OSX_ARCHITECTURES")
+    set(PS2X_IS_ARM_TARGET ON)
+    set(PS2X_IS_AARCH64_TARGET ON)
+elseif(CMAKE_SYSTEM_NAME MATCHES "^(iOS|tvOS|watchOS|visionOS)$")
+    # Apple mobile OSes are ARM-only; assume ARM when the toolchain names
+    # no processor rather than silently skipping sse2neon.
+    message(STATUS "CMAKE_SYSTEM_PROCESSOR unset; inferring ARM target from CMAKE_SYSTEM_NAME=${CMAKE_SYSTEM_NAME}")
+    set(PS2X_IS_ARM_TARGET ON)
+    set(PS2X_IS_AARCH64_TARGET ON)
@@
     set(PS2X_IS_ARM_TARGET ON)
 endif()
+
+if(NOT PS2X_IS_ARM_TARGET AND NOT CMAKE_SYSTEM_PROCESSOR AND CMAKE_CROSSCOMPILING)
+    message(FATAL_ERROR "PS2X: CMAKE_SYSTEM_PROCESSOR is unset while cross-compiling and no ARM target could be inferred; set CMAKE_SYSTEM_PROCESSOR in the toolchain file")
+endif()
```

The FATAL branch sits after the Vita compiler-match block and requires
`NOT PS2X_IS_ARM_TARGET`, so Vita (compiler-matched) and native builds (not
cross-compiling) can never trip it.

### Desktop-proof table (Ninja, macOS arm64, Release, `PS2X_BUILD_STUDIO=OFF`)

Build dir `/Volumes/Extreme SSD/ps2x-i2-desktop` (fresh; `_deps` reused, no
raylib re-clone). Baseline configure ran BEFORE any fix; reconfigure after each.

| Fix | Desktop-neutral evidence |
|---|---|
| G4 | Generated `ps2xRuntime/cmake_install.cmake` byte-identical before vs after: sha256 `790994cb…08a27e` both sides (`diff -q` silent; re-verified after all three fixes). Reconfigure exit 0. |
| G6 | Default predicate `CMAKE_SYSTEM_NAME STREQUAL "iOS"` is false on desktop (Darwin); cache still `PS2X_ENABLE_FFMPEG:BOOL=ON`; baseline configure found pkg-config `libavcodec 63.1.101` etc. Reconfigure exit 0. |
| G5 | Desktop takes the original first branch (`CMAKE_SYSTEM_PROCESSOR=arm64`): log shows `ARM target detected, fetching sse2neon` with NO `inferring` line. Reconfigure exit 0. |
| All | Full `cmake --build`: exit 0, `ps2EntryRunner` linked (`build-desktop.log`). One ExFAT AppleDouble incident (`._*.c` globbed in fresh `_deps`): purged with `find … -name "._*" -delete` per P1 precedent, rebuilt green. |

### `ps2xTest` receipt (CWD fork root, as P1)

| Run | Total | Passed | Failed |
|---|---|---|---|
| Post-fix tree (`66d992c` + uncommitted P1s edit + generated runner glue) | 425 | 424 | 1: `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` (`callback invocation should use the reserved async stack pool`) — same test + assertion as the P13-1d pre-existing failure |

## Step 2 — configure (+ build if it passes)

I1 toolchains reused as-is (`local/research/I1/logs/ios-simulator.toolchain*.cmake`).
Runtime-only flags, `-DPS2X_ENABLE_SCCACHE=OFF`, Xcode generator,
`CMAKE_CONFIGURATION_TYPES=Debug`, build dirs on the SSD, `_deps` reused
(same four `FETCHCONTENT_SOURCE_DIR_*`).

| Probe | Setup | Result |
|---|---|---|
| A | Toolchain v1 (no `CMAKE_SYSTEM_PROCESSOR`), `-DPLATFORM=iOS`, `-B …/ps2x-i2-ios-a` | FAIL (exit 1). G5 proof in log: `CMAKE_SYSTEM_PROCESSOR unset; inferring ARM target from CMAKE_OSX_ARCHITECTURES` then `ARM target detected, fetching sse2neon`. FIRST error = G1: `EnumOption.cmake:7: Unknown value iOS. Only -DPLATFORM=Desktop;Web;Android;Raspberry Pi;DRM;SDL allowed.` (via `CMakeOptions.txt:5`) |
| B | Toolchain v2, `-DPLATFORM=Desktop`, `-B …/ps2x-i2-ios-b` | FAIL at generate step (exit 1). Passed G4 (`Configuring done (43.6s)`, 0 `BUNDLE DESTINATION` mentions in log). G6 proof: `FFmpeg disabled; MPEG video decode falls back to stub frames`. FIRST error = G3: `CMake Error: The following variables are used in this project, but they are set to NOTFOUND: OPENGL_LIBRARY — linked by target "raylib" in directory …/_deps/raylib-src/src`; `CMake Generate step failed.` |

No iOS build was attempted (generate did not pass for either probe, so no build
files exist). No Simulator launch (per brief: needs a built binary + a backend
decision). G2 (bundled GLFW has no iOS path) remains predicted-only: no build
was reachable to observe it.

### Raylib-wall statement + exact next decision (options only, no verdict)

All three I1 config-class gaps (G4/G5/G6) are fixed in the fork and the iOS
configure now stops inside pinned raylib 5.5 itself: `-DPLATFORM=iOS` is
rejected by its platform enum (G1), and the Desktop-platform escape fails its
`find_library(OpenGL)` against the iOS SDK, which ships only OpenGLES (G3);
behind both sits a GLFW with no iOS path (G2). G1/G2/G3 were out of scope for
this brief (raylib untouched, pins unchanged).

| Option | What it would address | Open question it leaves |
|---|---|---|
| Upgrade the raylib pin to a release with an iOS backend | G1 (enum accepts iOS), G2/G3 (backend uses UIKit + GLES) | Which pin; imgui/rlImGui `Raylib_5_5` tag compatibility; desktop behavior drift |
| Fork-patch raylib 5.5 with an iOS backend in the fork | Same three, without moving the pin | Size of the backport; who owns the forked backend going forward |
| SDL switch (raylib `PLATFORM=SDL`, or replace raylib windowing with SDL) | Sidesteps GLFW (G2); GLES selection still required (G3) | Whether raylib-SDL targets iOS SDK cleanly here; input/audio mapping; G7 touch still open either way |

## Exact commands

```sh
# desktop baseline (pre-fix) + per-fix reconfigures + build + test
cmake -S "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" -B "/Volumes/Extreme SSD/ps2x-i2-desktop" -G Ninja \
  -DPS2X_BUILD_STUDIO=OFF -DCMAKE_BUILD_TYPE=Release \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-ios-spike-attempt1/_deps/raylib-src" \
  -DFETCHCONTENT_SOURCE_DIR_IMGUI="/Volumes/Extreme SSD/ps2x-ios-spike-attempt1/_deps/imgui-src" \
  -DFETCHCONTENT_SOURCE_DIR_RLIMGUI="/Volumes/Extreme SSD/ps2x-ios-spike-attempt1/_deps/rlimgui-src" \
  -DFETCHCONTENT_SOURCE_DIR_SSE2NEON="/Volumes/Extreme SSD/ps2x-ios-spike-attempt3/build/_deps/sse2neon-src"
cp "/Volumes/Extreme SSD/ps2x-i2-desktop/ps2xRuntime/cmake_install.cmake" /tmp/ps2x-i2/cmake_install.cmake.base
# (apply fix) ; cmake -S ... -B /Volumes/Extreme\ SSD/ps2x-i2-desktop   # after each fix
diff /tmp/ps2x-i2/cmake_install.cmake.base "/Volumes/Extreme SSD/ps2x-i2-desktop/ps2xRuntime/cmake_install.cmake"
find "/Volumes/Extreme SSD/ps2x-i2-desktop" -name "._*" -delete
find "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" -name "._*" -delete
cmake --build "/Volumes/Extreme SSD/ps2x-i2-desktop"          # COPYFILE_DISABLE=1
cd "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" && "/Volumes/Extreme SSD/ps2x-i2-desktop/ps2xTest/ps2x_tests"

# fork commits (one per fix, named files only) + push (fork clone ONLY)
git add ps2xRuntime/CMakeLists.txt   # G4, G6 (separate commits)
git add CMakeLists.txt               # G5
git push fork ssx3                   # e73e36a..66d992c, first try

# probe A (v1 toolchain, PLATFORM=iOS — expect G1)
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE=/Users/bradrichardson/dev/ssx3/local/research/I1/logs/ios-simulator.toolchain.cmake \
  -DCMAKE_CONFIGURATION_TYPES=Debug -DPLATFORM=iOS \
  -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF \
  -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB=... -DFETCHCONTENT_SOURCE_DIR_IMGUI=... \
  -DFETCHCONTENT_SOURCE_DIR_RLIMGUI=... -DFETCHCONTENT_SOURCE_DIR_SSE2NEON=... \
  -S "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" -B "/Volumes/Extreme SSD/ps2x-i2-ios-a"
# probe B: same with ios-simulator.toolchain.v2.cmake, -DPLATFORM=Desktop, -B .../ps2x-i2-ios-b
```

## Receipt paths

- `local/research/I2/REPORT.md` (this file)
- `local/research/I2/logs/configure-desktop.log` (post-fix reconfigure, exit 0)
- `local/research/I2/logs/build-desktop.log` (exit 0, `ps2EntryRunner` linked)
- `local/research/I2/logs/ps2x-tests.log` (424/425, 1 pre-existing failure)
- `local/research/I2/logs/configure-ios-a.log` (exit 1: G5 inference + G1 wall)
- `local/research/I2/logs/configure-ios-b.log` (exit 1: G4 passed, G6 off, G3 wall)
- Fork commits `abc6f6c`, `d62c4b5`, `66d992c` on `fork ssx3` (base `e73e36a`)
- Scratch: `/tmp/ps2x-i2/` (logs + `cmake_install.cmake.base`, small files);
  `/Volumes/Extreme SSD/ps2x-i2-desktop`, `/Volumes/Extreme SSD/ps2x-i2-ios-a`,
  `/Volumes/Extreme SSD/ps2x-i2-ios-b`

## What I could not do

- Build any iOS target (generate fails at G3 before build files exist); so the
  sse2neon compile for arm64-ios, the G2 GLFW failure, and miniaudio CoreAudio
  init on Simulator are all still unobserved, not confirmed.
- Install to a booted Simulator / launch / record first window or crash log
  (needs a built binary; game ISO out of scope in any case).
- Touch input (G7), bundle resources / signing / `IoPaths` sandbox mapping —
  unchanged from I1, still open.
- Re-verify the desktop build against a tree WITHOUT the P1s concurrent edit
  (their `EeScheduler.cpp` change was in the worktree at build time and is now
  committed as `be01146`; the CMake fixes themselves touch no source).
