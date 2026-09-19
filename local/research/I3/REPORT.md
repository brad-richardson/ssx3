# I3 — Raylib decision spike: upgrade / fork-patch / SDL (tables, no verdicts)

- Date: 2026-09-19. Runbook `local/muse/prompts/I3.md`. Tables, no verdicts, no recommendation.
- Target context: iphonesimulator arm64 + eventual iOS device. GLES-vs-Metal noted per option.
- Fork clone READ ONLY honored: the fork (`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`) was only grepped/sed-read; no edits, commits, or pushes there. No `git push` run anywhere in ssx3.
- Host only: no `adb`, no device, no Simulator boot/launch. Installed iOS 27.0 SDKs inspected only (`xcrun --show-sdk-path`); no runtime/platform download.
- Disk: all probe clones/builds on `/Volumes/Extreme SSD/ps2x-i3/`; internal disk holds only this report + small logs. `/tmp/p1-link`, `/tmp/ps2xgs-build*`, `/tmp/ps2x-ios-spike`, other agents' dirs never touched.
- Network reads only: `git ls-remote`, shallow clones to SSD scratch, two doc-page fetches + one GitHub API read. No pushes, PRs, or `gh` writes.

Path shorthands: `R5` = pinned raylib 5.5 (`/Volumes/Extreme SSD/ps2x-ios-spike-attempt1/_deps/raylib-src`), `R6` = raylib 6.0 clone, `RM` = raylib master clone, `RF` = `ghera/raylib-iOS` 5.5.7-iOS clone (all under `/Volumes/Extreme SSD/ps2x-i3/`), `FORK` = fork clone (read-only).

## Step 1 — Option A: upgrade the pin

Releases 5.5 → newest: exactly two tags exist (`git ls-remote --tags raysan5/raylib`): `5.5` (`c1ab645`) and `6.0` (`dbc56a8`, 23 Apr 2026). Master HEAD `a365e56` added as a non-release reference row.

### Version table (file:line per cell)

| Candidate | Platform enum accepts iOS? | `rcore_ios` / UIKit backend present? | GLES selection for iOS | rlImGui / imgui pin compat |
|---|---|---|---|---|
| 5.5 (`c1ab645`) | No: `CMakeOptions.txt:5` enum is `Desktop;Web;Android;Raspberry Pi;DRM;SDL` | No: `src/platforms/` holds only `rcore_{android,desktop_glfw,desktop_rgfw,desktop_sdl,drm,template,web}.c`; 0 `UIKit`/`TARGET_OS_IPHONE` in `src/` outside `external/miniaudio.h`; bundled `external/RGFW.h` 0 refs | None for iOS. `OPENGL_VERSION` enum (`CMakeOptions.txt:7`) offers `ES 2.0`/`ES 3.0` but no iOS platform consumes it. rlgl APIs are GL-only (`src/rlgl.h:24-29`: 11/21/33/43/ES2/ES3); `metal` hits = 2, both PBR map names (`rlgl.h:519,532`); `vulkan` hits = 0 | Baseline: rlImGui `Raylib_5_5` (`118221c`) + imgui `v1.92.7-docking` (`7d22736`) as pinned |
| 6.0 (`dbc56a8`) | No: `CMakeOptions.txt:9` enum is `Desktop;Web;WebRGFW;Android;Raspberry Pi;DRM;SDL;RGFW;Memory` | No: `src/platforms/` = 5.5 set + `rcore_desktop_win32.c`, `rcore_memory.c`, `rcore_web_emscripten.c`; whole-tree grep for `TARGET_OS_IPHONE`/`PLATFORM_IOS`/`rcore_ios`/`UIKit` = 0 outside `miniaudio.h`/`minigamepad.h`; `external/RGFW/RGFW.h` 0 `TARGET_OS_IPHONE` (macOS Cocoa path only, `:224`) | None for iOS. `OPENGL_VERSION` enum (`CMakeOptions.txt:9`) adds `Software`; rlgl adds `GRAPHICS_API_OPENGL_SOFTWARE` (`rlgl.h:24-30`), still no Metal/Vulkan (same 2 PBR-name `metal` hits, 0 `vulkan`) | rlImGui `Raylib_6_0` tag (`3bc5731`, "Bind to just raylib 6.0 and Imgui 1.92.7") exists; `rlImGui.cpp`/`rlImGui.h` byte-identical to `Raylib_5_5` tag (`diff` empty); tag README "built against ImGui 1.92.1 … incompatible with older" (`rlimgui-6.0/README.md:7-8`), and 5.5-tag README pairs "Raylib 6.0 with ImGui 1.92.7 → Raylib_6_0" (`rlimgui-src/README.md:13`): pinned `v1.92.7-docking` satisfies both. (Newer `v1.92.8/9-docking` also exist upstream.) |
| master `a365e56` (non-release ref) | No: `CMakeOptions.txt:9` enum adds `Win32`, still no iOS | No: same `platforms/` set as 6.0; 0 iOS refs in `src/` outside external | None for iOS (same rlgl GL-only set as 6.0) | No rlImGui tag tracks master; drift below is a superset of 6.0's |

Upstream PR state (read-only API check): raysan5/raylib#3880 "[rcore] Porting raylib to iOS" (`blueloveTH`) is `state: closed`, `merged_at: null` (closed 2025-07-27, labels `help needed`, `on hold`). No merged iOS backend exists upstream at any pin.

### API breaks 5.5 → candidate (raylib.h `RLAPI` lines: 581 / 600 / 619)

| Break class | 5.5 → 6.0 (evidence) | 5.5 → master |
|---|---|---|
| Functions removed | 4: `DrawModelPoints`, `DrawModelPointsEx`, `UnloadModelAnimation`, `UpdateModelAnimationBones` | 7: those 4 + `GetSplinePointBezierQuad`, `ImageDraw`, `ImageDrawTriangleEx` |
| Functions added | 23 (`ComputeSHA256`, `FileCopy/Move/Remove/Rename`, `FileTextFindIndex/Replace`, `GetDirectoryFileCount{,Ex}`, `GetKeyName`, `GetTextBetween`, `LoadTextLines`, `MeasureTextCodepoints`, `TextInsertAlloc`, `TextRemoveSpaces`, `TextReplaceAlloc`, `TextReplaceBetween{,Alloc}`, `UnloadTextLines`, `UpdateModelAnimationEx`, `DrawEllipse{V,LinesV}`, `DrawLineDashed`) | 45 (the 23 + 22 more, incl. `ImageDrawImage*`, `DrawCircleLinesEx`, `LoadRenderTextureEx`, `IsFileHidden`, `IsPathAbsolute`) |
| Signature changes (breaking/behavioral) | `UpdateModelAnimation` `int frame` → `float frame` (`raylib.h:1605` → `R6:1641`); `DrawCircleGradient(int,int,…)` → `(Vector2,…)` (`:1257` → `R6:1283`); `LoadFontData` +7th param `int *glyphCount` (`:1466` → `R6:1495`); `DrawRectangleGradientEx` 3rd/4th `Color` swapped meaning, same shape — silent (`:1271` → `R6:1300`); `TextSplit` `const char**` → `char**`; `TextJoin` `(const char**,…):const char*` → `(char**,…):char*`; `TextTo{Lower,Upper,Camel,Pascal,Snake}` return `const char*` → `char*` (impl still static buffer, `R6/src/rtext.c:2119-2121`); `DecodeDataBase64` `(const unsigned char*)` → `(const char*)` (`:1152` → `R6:1177`) | Superset (not itemized; same method) |
| Signature changes (source-compatible) | `SaveFileText`, `LoadFontEx`, `LoadFontFromMemory`, `ImageDrawTriangleFan/Strip` gain `const`; `TextReplace`/`TextFindIndex`/`ChangeDirectory`/`ImageResizeNN` param renames only | Superset |
| Struct/enum changes | `Mesh`: `boneIds` → `boneIndices`, `boneMatrices` moved out; `Model`: `boneCount/bones/bindPose` → `skeleton/currentPose/boneMatrices` (+ new `ModelSkeleton`, `ModelAnimPose`); `ModelAnimation`: `frameCount/bones/framePoses` → `keyframeCount/keyframePoses` (`R6:434-440`); `FilePathList.capacity` removed; `SHADER_LOC_BONE_MATRICES` removed, `SHADER_LOC_MATRIX_BONETRANSFORMS` + `SHADER_LOC_VERTEX_INSTANCETRANSFORM` added; `SHADER_UNIFORM_UINT{,2,3,4}` added; Camera comments only | Superset |
| Fewest-breaks count (no recommendation) | 4 removed / 23 added / 9 breaking-or-behavioral signature changes | 7 removed / 45 added / superset |

Intersection with this project's raylib use (identifier cross-check `funcs-5.5.txt` × sources):

| Consumer | raylib APIs used | Removed/changed in 6.0 used? | Structs touched? |
|---|---|---|---|
| Fork runtime (`FORK/ps2xRuntime/{src,include}`, excl. generated `register_functions.cpp`) | 38 real (`InitWindow`, `DrawTexturePro`, `UpdateTexture`, `IsGamepad*`, `IsKeyDown`, `Wave`/`Sound` set, `GetApplicationDirectory`, etc.; +2 comment-noise words) — all present in 6.0 | 0 hits for all 21 changed/removed names | None of Mesh/Model/FilePathList/Shader touched; no `raymath.h`, no `rlgl.h` use |
| Pinned rlImGui (`rlImGui.cpp`/`.h` only — fork compiles just `rlImGui.cpp`, `FORK/ps2xRuntime/CMakeLists.txt:130-131`) | 74 identifiers, all present in 6.0 | 0 hits for all 21 changed/removed names | None (`LoadDirectoryFiles` appears only in `examples/asset_browser/`, never compiled) |

### Option A: evidence / effort proxies / open questions

| # | Evidence | Effort proxy | Open question it leaves |
|---|---|---|---|
| A1 | No release (5.5, 6.0) and no master HEAD has an iOS backend; enum rejects `iOS` at all three pins | Upgrade alone closes 0 of G1/G2/G3 (an iOS backend is still unwritten at every pin) | None on this row: the backend gap is pin-independent |
| A2 | 6.0-vs-5.5 break surface itemized above; project consumers use 0 removed/changed APIs or structs | API-adaptation cost for this project's sources ≈ 0 lines (mechanical risk only: `DrawRectangleGradientEx` arg-order and `UpdateModelAnimation` float-frame are silent if ever adopted) | Desktop behavior drift outside the used subset (tessellation, animation redesign, `GetRandomValue` modulo-bias fix per 6.0 CHANGELOG) is unmeasured |
| A3 | rlImGui `Raylib_6_0` tag binds raylib 6.0 + imgui 1.92.7 with zero source delta vs `Raylib_5_5` tag | rlImGui/imgui pin move ≈ tag-only (imgui pin already `v1.92.7-docking`) | Whether to track newer imgui `v1.92.8/9-docking` (unexamined) |
| A4 | Device note: rlgl has no Metal/Vulkan backend at any pin; device SDK still ships (deprecated) OpenGLES (`iPhoneOS27.0.sdk/.../OpenGLES.framework`, `OpenGLESAvailability.h:7-10`, `GLES_SILENCE_DEPRECATION`) | Any upgrade still needs a GLES route (ANGLE or system GLES) + a Metal-vs-GLES device decision | Longevity of deprecated device GLES; simulator GLES unaffected |

## Step 2 — Option B: fork-patch 5.5

Prior art (read-only): community fork `ghera/raylib-iOS` has a 5.5-based line (`5.5-iOS` … `5.5.7-iOS`) and a 6.0-based line (`6.0.0-iOS` … `6.0.4-iOS`); inspected tag `5.5.7-iOS` (shallow clone to SSD). Its README: based on upstream PR #3880, "experimental … not production-ready", callback lifecycle (`ios_ready`/`ios_update`/`ios_destroy`), Xcode26 example + prebuilt ANGLE.

### File table: what an iOS backend needs (fork prior-art sizes)

| File | Role | Size / delta | Evidence |
|---|---|---|---|
| NEW `src/platforms/rcore_ios.c` | Windowing (UIKit view+viewcontroller+delegate), input incl. touch, GLES surface via ANGLE EGL, app entry | 789 lines: header+limits `:1-44` (LIMITS: no keyboard, no gamepad); `MapPointId` `:96`; window/monitor/clipboard/cursor stubs `:130-333`; `GetTime`/`OpenURL` `:340-360`; gamepad stubs `:366-372`; `PollInputEvents` `:394-430`; `SetupWindowSizes` `:435`; `InitPlatform` `:448-559` (~112); `ClosePlatform` `:560-581`; `RecreatePlatformSurface` `:582-638`; `SyncAllTouches` `:639-651`; `SendGestureEvent` `:658+`; `main`→`UIApplicationMain` `:785-789` | `RF/src/platforms/rcore_ios.c`, `wc -l` 789 |
| EDIT `src/rcore.c` | Backend dispatch | +4 lines: `#elif defined(PLATFORM_IOS)` include `:551-552` + TRACELOG `:622-623` | `diff R5 RF` |
| EDIT `src/rlgl.h` | GLES3-via-ANGLE headers + guards | ~+25: `PLATFORM_IOS` stanza requiring `GRAPHICS_API_OPENGL_ES3` + `GL_GLEXT_PROTOTYPES`, includes `libGLESv2/...` `:869-881`; ES2/ES3 guard tweak ×2; `RLGL_ENABLE_GLES_DEFAULT_HIGHP_PRECISION` option | `diff R5 RF` |
| GAP: `CMakeOptions.txt` + `cmake/LibraryConfigurations.cmake` | Enum + link stanza so `-DPLATFORM=iOS` configures | 0 lines in fork: enum still 6 values (`RF/CMakeOptions.txt:5`), no iOS stanza (its only `LibraryConfigurations` diff is Android ES2→ES3, unrelated) — new work, Android stanza (`R5/cmake/LibraryConfigurations.cmake:63-76`) is the ~14-line analogy | `diff R5 RF` |
| NEW `projects/Xcode26/` | Xcode project + ANGLE xcframeworks + ObjC bridge | `main.c`, `raylib.xcodeproj/project.pbxproj`, `raylib/bridge/IOSBridge.{h,mm}` + `ANGLE/{libEGL,libGLESv2}.xcframework` (192M, `ios-arm64` + `ios-arm64-simulator` slices) | `find`, `du -sh` |
| EDIT app `main` | Callback lifecycle (no blocking loop on iOS) | Pattern: `ios_ready/update/destroy` (`RF/README.md:29-54`, `RF/projects/Xcode26/main.c:20,49,62,165`); runtime's loop is `PS2Runtime::run` `:2614-2743` + `main.cpp:217-239` (I1) | I1 + RF README |
| Audio: no new files | miniaudio CoreAudio path + ObjC compile mode + framework links | `ma_backend_coreaudio` covers "macOS, iOS" (`miniaudio.h:3599,8074`); iOS session categories `:6871-6894`, config `:7262`; "iOS build needs to be compiled as Objective-C" (`:481`); fork marks `raudio.c` as `sourcecode.c.objc` (`project.pbxproj:43`); link needs `CoreFoundation/CoreAudio/AudioToolbox` (`:497-498`) + `AVFAudio/AVFoundation` (fork pbxproj); `rcore_ios.c` has 0 audio refs; runtime uses `Wave`/`Sound` only (`ps2_audio.cpp:298-306`, I1) | R5 `miniaudio.h` + RF pbxproj + syntax probes (§C) |

### Line-count proxies from neighboring backends (R5 `src/platforms/`, `wc -l`)

| Backend file | Lines | What it proxies |
|---|---|---|
| `rcore_android.c` | 1339 | Nearest mobile analogue (lifecycle, touch, GLES-EGL, app glue) |
| `rcore_desktop_glfw.c` | 1933 | Desktop windowing/input reference |
| `rcore_desktop_rgfw.c` | 1387 | Single-header-windowing reference |
| `rcore_desktop_sdl.c` | 1978 | Delegated-windowing reference |
| `rcore_drm.c` | 1942 | EGL/direct-surface reference |
| `rcore_template.c` | 597 | Stub floor (every function stubbed) |
| `rcore_web.c` | 1792 | Constrained-loop reference |
| fork `rcore_ios.c` (prior art, same 5.5 line) | 789 | Worked iOS example: between template floor and android size, with keyboard+gamepad unimplemented |
| `raudio.c` / `rgestures.h` / `rcore.c` / `rlgl.h` / `miniaudio.h` | 2879 / 555 / 4070 / 5262 / 92633 | Unchanged by fork (identical in `diff R5 RF` except `rcore.c`/`rlgl.h` deltas above) |

### Touch-input gap (G7) folded in

| # | Finding | Evidence |
|---|---|---|
| B-G7a | Fork fills `CORE.Input.Touch.pointCount/position/pointId` from `UITouch` set + feeds `ProcessGestureEvent`/`UpdateGestures`, so `GetTouch*` + `GetGesture*` work | `rcore_ios.c:639-649,658-677,394-430` |
| B-G7b | Touch positions carry a `TODO: Normalize … for screen.width/height` (`:649`); header LIMITS say no keyboard, no gamepad (`:10-11`) — PS2 pad input has no iOS source in this backend | `rcore_ios.c:10-11,649` |
| B-G7c | rlImGui input stays mouse/keyboard/gamepad-only at both tags (`grep -c GetTouch rlImGui.cpp` = 0, I1) → debug-UI touch gap persists under B unless rlImGui is extended or the panel stays gated off (Android precedent `FORK/ps2xRuntime/CMakeLists.txt:86,513`, I1) | I1 + §A tag diff |

### Option B: effort proxies / open questions

| # | Effort proxy | Open question it leaves |
|---|---|---|
| B1 | Prior-art backport ≈ 789 (new backend) + ~30 (rcore/rlgl edits) + ~14 (CMake stanza, unwritten) + Xcode/ANGLE packaging (192M vendored) + app lifecycle split | Who owns the forked backend going forward (I2); fork is monthly-synced + "not production-ready" |
| B2 | Audio ≈ 0 new lines (compile-mode + links); runtime audio surface is `Wave`/`Sound` only | AVAudioSession category choice (`:6874-6881` options) incl. silent-switch/mix behavior; iOS-27 `AVAudioSessionInterruptionType` deprecation warnings (observed, §C) |
| B3 | GLES route in prior art is ES3-via-ANGLE (GLES→Metal translation); SDK ships system GLES on simulator AND device (`OpenGLES.framework`, ES3 headers both SDKs) | EAGL/system-GLES vs ANGLE: prior art never tries system GLES; device GLES is deprecated-but-present |
| B4 | Device note: ANGLE xcframeworks ship `ios-arm64` + simulator slices; Metal never touched directly | ANGLE build provenance/refresh (fork: monthly from Chromium stable) vs prebuilt trust; device signing/sandbox untouched by this spike |

## Step 3 — Option C: SDL

### Configure probe (build dir on SSD; first error)

| Attempt | Command shape | Result |
|---|---|---|
| C1 | `cmake -G Ninja -DCMAKE_TOOLCHAIN_FILE=…/I1/logs/ios-simulator.toolchain.v2.cmake -DPLATFORM=SDL -DOPENGL_VERSION="ES 2.0" -DBUILD_EXAMPLES=OFF -DCMAKE_PREFIX_PATH=/opt/homebrew -S R5 -B …/ps2x-i3/sdl-probe-es2` | FAIL (exit 1): `cmake/LibraryConfigurations.cmake:96 (find_package): Could not find … SDL2Config.cmake …` — cross-compile package-search scoping, not an iOS verdict |
| C2 (retry) | Same + `-DSDL2_DIR=/opt/homebrew/lib/cmake/SDL2` (sdl2-compat config) | PASS (exit 0): `PLATFORM=PLATFORM_DESKTOP_SDL`, `GRAPHICS=GRAPHICS_API_OPENGL_ES2`; `build.ninja:174,186 DEFINES = -DGRAPHICS_API_OPENGL_ES2 -DPLATFORM_DESKTOP_SDL` |

Probe log tail (`logs/configure-sdl-es2-ios.log`): `Audio Backend: miniaudio / Building raylib static library / Generated build type: Debug / PLATFORM=PLATFORM_DESKTOP_SDL / GRAPHICS=GRAPHICS_API_OPENGL_ES2 / Configuring done (5.8s) / Generating done (0.4s)`.

Compile-level probes (`-fsyntax-only`, zero build output; same defines/includes/arch/sysroot as `build.ninja:184-189`):

| TU | Mode | Result |
|---|---|---|
| `rcore.c` (SDL backend + ES2 rlgl path) | C | exit 0, 0 diagnostics (`logs/syntaxonly-rcore-sdl-es2-ios.log`, 0 bytes) |
| `raudio.c` (miniaudio) | C | exit 1, 20 errors: `miniaudio.h:31811` → `AVFoundation.h` → ObjC `@class` in C TU (`logs/syntaxonly-raudio-sdl-es2-ios.log`) |
| `raudio.c` | ObjC (`-x objective-c`) | exit 0, 0 errors + deprecation warnings: `AVAudioSessionInterruptionType{Began,Ended}` deprecated in iOS 27.0 (`miniaudio.h:33929,33946`; `logs/syntaxonly-raudio-objc-ios.log`) |

### What selects GLES

| Item | Evidence |
|---|---|
| CMake `OPENGL_VERSION="ES 2.0"/"ES 3.0"` (`CMakeOptions.txt:7`) overrides the empty SDL-stanza default (SDL stanza sets no `GRAPHICS`, `LibraryConfigurations.cmake:95-98`, unlike Desktop/Android/Web/DRM) | C2 log + `build.ninja` |
| ES2+`PLATFORM_DESKTOP_SDL` uses bundled `glad_gles2` — no system GLES headers (`rlgl.h:867-870`); procs via `rlLoadExtensions(SDL_GL_GetProcAddress)` (`rcore_desktop_sdl.c:1903`); context attrs `PROFILE_ES` 2.0 (`:1841-1846`) | R5 sources |
| ES3 needs `<GLES3/gl3.h>` + `<GLES2/gl2ext.h>` unconditionally (`rlgl.h:861-864`); iOS SDK has no `/usr/include/GLES*` (only `OpenGLES.framework/Headers/ES3/{gl,glext}.h`) → ES3/SDL needs ANGLE headers or an include shim | SDK `ls` receipts |
| SDL side: SDL2 `release-2.32.10` (latest; `5d24957`) ships `src/video/uikit/` (26 files, 5526 lines) incl. `SDL_uikitopengles.{h,m}` + `SDL_uikitopenglview.{h,m}` and `SDL_UIKitRunApp` (`:53`) → `UIApplicationMain` (`:69`); SDL3 latest `release-3.4.16` (`fa2c02b`) | sparse clone to SSD |

### Input / audio mapping + G7

| raylib surface | SDL mapping (R5 `rcore_desktop_sdl.c`) | iOS note |
|---|---|---|
| Window close | `SDL_QUIT` → `shouldClose` (`:1384`) | SDL appdelegate owns lifecycle; blocking `while(!WindowShouldClose())` runs inside `SDL_main` after `UIApplicationMain` (SDL structure; untested here) |
| Window events | `SDL_WINDOWEVENT` resize/enter/leave/hide/minimize/focus/show/maximize/restore (`:1431-1462`) | Mapped; backgrounding semantics untested |
| Keyboard | `SDL_KEYDOWN/UP` (`:1472,1502`), `SDL_TEXTINPUT` (`:1513`), scancode map (`:96+`) | No physical keyboard on device; software-keyboard path untested |
| Mouse | `SDL_MOUSEBUTTONDOWN/UP/WHEEL/MOTION` (`:1529-1560`) | Touch-as-mouse synthesis is SDL-side behavior, not inspected |
| Touch | `SDL_FINGERDOWN/UP/MOTION` → `UpdateTouchPointsSDL` fills `CORE.Input.Touch.*` (`:1276-1307`; SDL3 branch `#ifdef PLATFORM_DESKTOP_SDL3` `:1278`, auto-detected from SDL headers `:71-75`; SDL2 branch `:1292`) | Touch state available if SDL delivers fingers; G7 debug-UI gap persists (rlImGui 0 `GetTouch`, §A) |
| Gamepad | `SDL_JOYDEVICE*` + `SDL_CONTROLLER*` → `GAMEPAD_BUTTON_*` (`:1598-1660+`) | MFi controller mapping is SDL-side, untested |
| Audio | Unchanged: `SDL_INIT_AUDIO` not used, "managed by miniaudio" (`:1777`) → same ObjC-compile + CoreAudio path as Option B | Same session-category + deprecation open questions as B2 |
| Cursor/clipboard | `SDL_GetKeyName` passthrough (`:1271-1274`); clipboard via SDL (`SetClipboardText` used by runtime, present) | Untested on device |

SDL-version wrinkle: 5.5 CMake links SDL2 only (`find_package(SDL2 REQUIRED)`, `:96-98`); the SDL3 code path activates only if SDL3 headers are found (`:71-75`). Host brew provides `sdl2-compat` + `sdl3` (macOS arm64 dylibs — link-incompatible with iOS; an SDL2-for-iOS build is still required and was not attempted). Third-party pointer (unverified): jlt-commons/raylib-android CHANGELOG claims `PLATFORM=SDL` + `GRAPHICS_API_OPENGL_ES2` against iOS-built SDL2 works with `SDL_UIKitRunApp` as entry.

### Option C: effort proxies / open questions

| # | Effort proxy | Open question it leaves |
|---|---|---|
| C1 | raylib-side SDL backend has 0 iOS-specific lines (1 comment mention, `:338`) — iOS-ness comes entirely from SDL's 5526-line uikit backend | SDL2-for-iOS build + CMake integration (FetchContent/submodule/package); `SDL2_DIR` cross-search scoping seen in C1 |
| C2 | GLES2 route is header-clean (glad) and TU-compiles against the iOS 27.0 SDK (exit 0) | ES2-vs-ES3 choice (ES3 needs ANGLE/shim); link never attempted (no iOS SDL2 lib on hand) |
| C3 | Audio = same as B (ObjC TU + links), input mapping table above; main-loop shape preserved inside `SDL_main` per SDL structure | `SDL_main`/UIApplicationMain interplay with `PS2Runtime::run` (game thread + host loop) untested; backgrounding/audio-session behavior untested |
| C4 | G7: touch state filled by SDL path, debug UI still mouse-only | Same rlImGui touch decision as B-G7c |
| C5 | Device note: SDL uikit ships both opengles and metal views; raylib side stays GLES either way | Which SDL video driver activates for an ES context on device; deprecated-device-GLES applies as in A4 |

## Exact commands

```sh
# --- setup (all heavy work on SSD) ---
mkdir -p local/research/I3/logs "/Volumes/Extreme SSD/ps2x-i3"

# --- Option A: tags + shallow clones (network reads) ---
git ls-remote --tags https://github.com/raysan5/raylib.git
git ls-remote https://github.com/raysan5/raylib.git HEAD
git clone --depth 1 --branch 6.0 https://github.com/raysan5/raylib.git "/Volumes/Extreme SSD/ps2x-i3/raylib-6.0"
git clone --depth 1 https://github.com/raysan5/raylib.git "/Volumes/Extreme SSD/ps2x-i3/raylib-master"
git ls-remote --tags https://github.com/raylib-extras/rlImGui.git
git ls-remote --tags https://github.com/ocornut/imgui.git | grep -E "1.92.[5-9]"
git clone --depth 1 --branch Raylib_6_0 https://github.com/raylib-extras/rlImGui.git "/Volumes/Extreme SSD/ps2x-i3/rlimgui-6.0"
git clone --depth 1 --branch 5.5.7-iOS https://github.com/ghera/raylib-iOS.git "/Volumes/Extreme SSD/ps2x-i3/raylib-ios-5.5.7"
git ls-remote --tags https://github.com/ghera/raylib-iOS.git
git ls-remote --tags https://github.com/libsdl-org/SDL.git | grep -E "release-2.3|release-3"
git clone --depth 1 --branch release-2.32.10 --filter=blob:none --sparse https://github.com/libsdl-org/SDL.git "/Volumes/Extreme SSD/ps2x-i3/SDL-uikit"
(cd "/Volumes/Extreme SSD/ps2x-i3/SDL-uikit" && git sparse-checkout set src/video/uikit)

# --- Option A: API extraction + diffs (outputs on SSD, not committed) ---
OUT="/Volumes/Extreme SSD/ps2x-i3"
for v in 5.5 6.0 master; do :; done  # api-$v.txt from grep '^RLAPI' raylib.h, funcs-$v.txt names, sig-$v.txt comment-stripped, structs-$v.txt typedef blocks
# usage intersections:
grep -rhoE "[A-Za-z_][A-Za-z0-9_]*" FORK/ps2xRuntime/src FORK/ps2xRuntime/include --exclude=register_functions.cpp | sort -u
# upstream PR state (read-only): fetch https://api.github.com/repos/raysan5/raylib/pulls/3880

# --- Option B: inspection ---
diff -rq R5 RF -x .git | grep -v "._"
wc -l R5/src/platforms/*.c R5/src/raudio.c R5/src/rgestures.h R5/src/rcore.c R5/src/rlgl.h R5/src/external/miniaudio.h
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path); ls -d $SDK/System/Library/Frameworks/{OpenGLES,Metal,UIKit,AVFoundation,CoreAudio}.framework
SDK=$(xcrun --sdk iphoneos --show-sdk-path); ls $SDK/System/Library/Frameworks/OpenGLES.framework/Headers/ES3/

# --- Option C: configure probe C1 (fail) then C2 (pass) ---
cmake -S R5 -B "/Volumes/Extreme SSD/ps2x-i3/sdl-probe-es2" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=local/research/I1/logs/ios-simulator.toolchain.v2.cmake \
  -DCMAKE_BUILD_TYPE=Debug -DPLATFORM=SDL -DOPENGL_VERSION="ES 2.0" \
  -DBUILD_EXAMPLES=OFF -DCMAKE_PREFIX_PATH=/opt/homebrew   # C1: SDL2 discovery error
cmake -S R5 -B "/Volumes/Extreme SSD/ps2x-i3/sdl-probe-es2" -G Ninja \
  ... -DSDL2_DIR=/opt/homebrew/lib/cmake/SDL2               # C2: exit 0 (log kept)

# --- Option C: single-TU syntax probes (no build output) ---
CC=$(grep CMAKE_C_COMPILER: .../sdl-probe-es2/CMakeCache.txt | cut -d= -f2)  # /opt/homebrew/opt/llvm/bin/clang
$CC -fsyntax-only -DGRAPHICS_API_OPENGL_ES2 -DPLATFORM_DESKTOP_SDL -fno-strict-aliasing \
  -Werror=implicit-function-declaration -Werror=pointer-arith -g -std=gnu99 -arch arm64 \
  -isysroot $SDKiPhoneSimulator -IR5/src -isystem /opt/homebrew/include -isystem /opt/homebrew/include/SDL2 \
  R5/src/rcore.c        # exit 0
$CC -fsyntax-only ... R5/src/raudio.c                 # exit 1, 20 errors (C mode)
$CC -fsyntax-only -x objective-c ... R5/src/raudio.c  # exit 0, deprecation warnings only

# --- commit (no push) ---
git add -f local/research/I3 && git commit -m "[I3] ..." --trailer "Orchestrated-By: Muse Code"
```

## Receipt paths

- `local/research/I3/REPORT.md` (this file)
- `local/research/I3/logs/configure-sdl-es2-ios.log` (C2 exit 0; C1 error quoted in Step 3)
- `local/research/I3/logs/syntaxonly-rcore-sdl-es2-ios.log` (0 bytes = 0 diagnostics)
- `local/research/I3/logs/syntaxonly-raudio-sdl-es2-ios.log` (exit 1, 20 ObjC-in-C errors)
- `local/research/I3/logs/syntaxonly-raudio-objc-ios.log` (exit 0, iOS-27 deprecation warnings)
- SSD scratch (not committed): `/Volumes/Extreme SSD/ps2x-i3/{raylib-6.0,raylib-master,rlimgui-6.0,raylib-ios-5.5.7,SDL-uikit,sdl-probe-es2,api-*.txt,funcs-*.txt,sig-*.txt,structs-*.txt,runtime-*.txt,rlimgui-raylib-apis.txt}`

## What I could not do

- Build or link any iOS target: probes stopped at configure + `-fsyntax-only` per the brief (no build-the-world). The SDL link (needs SDL2-for-iOS), ANGLE integration, and every runtime link are unobserved.
- Boot/install/launch on Simulator, record any window or crash log (no binary exists).
- Anything on device: signing, bundle/`IoPaths` sandbox mapping, Metal-vs-GLES runtime behavior, MFi/touch/keyboard end-to-end, AVAudioSession category audibility.
- Judge third-party claims beyond file presence: `ghera/raylib-iOS` was inspected (not built); omardev29/jlt-commons READMEs are pointers only; App Store / CI assertions unverified.
- Resolve the orchestrator decision: per the brief, no verdict and no recommendation are given.
