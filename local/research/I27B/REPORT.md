# I27B — iOS drawable-scale candidate and Simulator gate

Worker: Codex. Brief: `local/muse/prompts/I27B.md`. Source base `4ebb2ac5c8037ea747d580c34e594015a6df6849`; pinned remote `fork/ssx3` `ddaee780288adb076ce40050d87969b20bc4bb05`. Local fork candidate `04f3ace599e3d9d52b94803150688f54dbf330ec` (`i27b-ios-drawable`), trailer `Orchestrated-By: Codex`. No iPhone, iPad or Odin action, no fork push.

| Gate | Result | Receipt |
| --- | --- | --- |
| Fork candidate and raylib patch | Fresh `i27b-ios-drawable` worktree from `4ebb2ac`; commit `04f3ace`. The iOS CMake path runs a checked-in, source-hash-pinned patch hook on raylib `c1ab645ca298a2801097931d1079b10ff7eb9df8`. It derives SDL2 x/y scale from drawable/window sizes when all sizes are positive. A compile guard preserves desktop behavior; SDL3 branch is untouched. Original raylib source SHA `30db3e9f…`, patched source SHA `df666c29…`. | `source-diff.patch`, `sim-release-configure.log`; fork commit |
| Mac taps-OFF build and suite | Release build passed; suite **585/585**, zero failed, run from fork worktree root. Canonical codegen `register_functions.cpp` SHA matched E54F2: `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`. | `mac-cmake.log`, `mac-build.log`, `mac-suite.log` |
| Simulator build and install | Initial sandboxed configure failed on Xcode services; escalated rerun produced a **misconfigured O0** build, interrupted by the orchestrator before completion or run. One authorized repair used a fresh `ios-runtime-sim-release` directory, escalated configure from the outset, explicit `-O3 -DNDEBUG` C/C++ Release flags, Xcode build-settings and compiler response-file verification. Repaired build passed, app staged, ad-hoc signed and installed on Simulator `7662ACD6-6294-4676-B426-26A3F8C7B258`. Binary SHA pair `0b40cdd0a5757c365fd76ee791994d37879a4b15b73bbd100f4019c9b89806d8`; ELF and ISO source/stage SHA pairs match. | `sandbox-configure-error.txt`, `config-flags.txt`, `sim-o0-interrupted-build.log`, `sim-release-{configure,build,buildsettings,raylib-buildsettings,install}.log`, `sim-{input,stage,binary}-sha.txt` |
| Drawable/render/viewport geometry | Live SDL window 874×402, drawable 2622×1206 (**3×3**); raylib screen 874×402, render 2622×1206 (**1× drawable**). Each 2622×1206 PNG decoded; nonblack bbox reaches x=2616 (I27A content and pad stayed below x≈874). W1 16:9 game region and virtual pad placement remain visually aligned with W1F2, with no detected 3× geometry distortion. No GL state readback. | `sim-console.log`, `acceptance.txt`, viewed PNGs in `~/dev/ssx3-work/I27B/run-i27b/` |
| I26-FAST route | One Simulator boot, bundled `ps2x.env`, 31 vsync-clock presses armed. Race HUD at 100 s shows 00:00:04 / 1%; 160 s shows 00:00:11 / 2%; last tick **2363**, above 1714. No speed claim. | `sim-run.txt`, `sim-console.log`, race PNGs |
| Four viewed frames and SHA pairs | Title, Select Peak, race at 100 s and race at 160 s viewed against W1F2/I27A. All four SHA pairs match and occupy 3,314,427 B total. Guest font detail is visually **same** as W1F2; the original 512×448 guest image is still enlarged. Native virtual-pad outlines appear smoother. I27A's lower-left rendering regression is gone. | Frame table below, `acceptance.txt` |
| Limits and cleanup | Run elapsed 160 s (<180). Four PNGs 3.16 MiB (<12 MiB); copied text logs 2,777,760 B (<8 MiB); I27B scratch 4.4 GiB (<8 GiB); global ssx3 usage 124.6 GB (<200 GB). Lease slots 1/2 free; own launch PID 95744 exited. Runner-dir diff against `14b1e5cb` empty; local fork branch clean. | `sim-run.txt`, `cleanup.txt`, `disk-budget.txt`, `acceptance.txt`, fork git checks |

## Source path and patch

| Pinned source location | Observation |
| --- | --- |
| raylib `src/platforms/rcore_desktop_sdl.c:1064-1080` | SDL2 `GetWindowScaleDPI()` returned `(1,1)`; SDL3 separately reads display scale. The patched SDL2 path reads `SDL_GetWindowSize` and `SDL_GL_GetDrawableSize` on iOS, guards null/zero sizes, and divides each drawable dimension by its window dimension. |
| raylib `src/platforms/rcore_desktop_sdl.c:1436-1446` | `SDL_WINDOWEVENT_SIZE_CHANGED` sends point dimensions to `SetupViewport` and stores logical screen/current-FBO dimensions. |
| raylib `src/rcore.c:809-831,3537-3561` | Apple render getters and GL viewport multiply logical dimensions by `GetWindowScaleDPI`; projection remains in logical coordinates. |
| fork `ps2xRuntime/src/lib/ps2_ios_runtime.mm:178` | UIKit resize forwarding sends the 874×402 SDL window size as logical points. |

`source-diff.patch` is the exact fork candidate diff. `ps2xRuntime/CMakeLists.txt` invokes the checked-in hook only for `PS2X_IS_IOS` after raylib FetchContent setup and before compilation. The hook accepts only the pinned original source hash, applies one replacement, and is idempotent on reconfigure. The patched source lives in the private I27B raylib clone, not as an untracked edit to a shared `_deps` checkout. The fork commit has no generated guest or runner changes.

## Simulator configure repair

| Attempt | Evidence | Outcome |
| --- | --- | --- |
| First sandboxed configure | Xcode could not access CoreSimulator and DerivedData (`Operation not permitted`); CMake reported no C/C++ compiler. | Retried escalated, as required for sandbox failures. |
| Escalated retry in the same build dir | I27B cache `CMAKE_C_FLAGS_RELEASE` and `CMAKE_CXX_FLAGS_RELEASE` empty; generated-code response has `-O0`, no `-DNDEBUG`. I27A cache/response has `-O3 -DNDEBUG`. A partial first cache causing the mismatch is an inference. User sampled active LLVM `Localizer::localizeIntraBlock`; orchestrator stopped the invalid build before completion. | **Not accepted or run.** No speed comparison. |
| Authorized fresh `ios-runtime-sim-release` configure/build | Escalated configure from the outset with explicit C/C++ `-O3 -DNDEBUG`. Cache shows both flags; Xcode `ps2_game_objects` and raylib build settings show optimization level 3 and `-DNDEBUG`; actual generated-code response has `-O3 -DNDEBUG` and no `-O0`. | Build/install succeeded; this is the only Simulator app run. |

`sandbox-configure-error.txt`, `config-flags.txt`, `sim-o0-interrupted-build.log`, `clang-sample.txt`, and the Release build-settings logs are the repair receipts.

## Viewed frame table

All PNGs decoded as 2622×1206; SHA-256 matched on two reads. Frames stayed in `~/dev/ssx3-work/I27B/run-i27b/` and were not committed.

| Frame | Viewed result relative to W1F2 and I27A | SHA-256, both reads |
| --- | --- | --- |
| `shot-0010s.png` | Title/logo and pad fill intended width. I27A's lower-left 874×402 output is gone; title layout matches W1F2. Native pad outlines look smoother, guest copyright font has the same source detail. | `ca7999fdae957c1e680be75c640f7c5bdafcc8ac7cfc358d9538a04eaa561b93` |
| `shot-0035s.png` | Select Peak menu spans intended game region. This differs in menu phase from I27A's 35 s Select Mode frame, so exact frame content is not compared. Guest menu font detail appears same as W1F2. | `9c4f3aa4b86e6587b2ab462c9ce48361d913ee4252dc1fdb5408cfd0ff642694` |
| `shot-0100s.png` | Race HUD 00:00:04 / 1%. Geometry fills width; known dark GS region remains, as in W1F2/I27A. | `c9ab4c1a321e7925f8a06512e44e2600dac2f70686df935696ee90db0954f457` |
| `shot-0160s.png` | Race HUD 00:00:11 / 2%. Same full-width geometry and dark GS region. | `869fd9cfa8b4cae586cc7503387294f7392c5169e4d451ebb1d0f35994c98847` |

## Exact commands

```sh
git ls-remote fork refs/heads/ssx3
git worktree add -b i27b-ios-drawable ~/dev/ssx3-work/I27B/PS2Recomp 4ebb2ac5c8037ea747d580c34e594015a6df6849
git clone --shared ~/dev/ssx3-work/E46-build/_deps/raylib-src ~/dev/ssx3-work/I27B/raylib-src
shasum -a 256 ~/dev/ssx3-work/codegen-ssx3/register_functions.cpp ~/dev/ssx3-work/E54F2/codegen/register_functions.cpp
bash ~/dev/ssx3-work/I27B/build.sh
# From ~/dev/ssx3-work/I27B/PS2Recomp:
~/dev/ssx3-work/I27B/build/ps2xTest/ps2x_tests > ~/dev/ssx3-work/I27B/suite.log 2>&1
bash ~/dev/ssx3-work/I27B/sim-build-install.sh  # sandbox configure failure, then escalated O0 attempt
# Orchestrator stopped the misconfigured Xcode process before it completed.
bash ~/dev/ssx3-work/I27B/sim-configure-release.sh  # escalated from start
xcodebuild -project ~/dev/ssx3-work/I27B/ios-runtime-sim-release/PS2RetroX.xcodeproj -target ps2_game_objects -configuration Release -showBuildSettings
xcodebuild -project ~/dev/ssx3-work/I27B/ios-runtime-sim-release/PS2RetroX.xcodeproj -target raylib -configuration Release -showBuildSettings
bash ~/dev/ssx3-work/I27B/sim-build-install-release.sh  # escalated from start
bash ~/dev/ssx3-work/I27B/sim-run.sh  # escalated, one 160 s boot, slot 1
PYTHONPATH=local/tooling/visual-review-python python3 -B local/research/I27B/accept.py > local/research/I27B/acceptance.txt
python3 local/tooling/p_lane_lease.py status
local/tooling/disk_budget.sh
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner  # empty, fork worktree
```

The five scripts in this report directory hold the exact CMake, Xcode, stage, install, lease, screenshot and own-PID cleanup commands. Binary and pinned input SHA pairs are in `sim-{binary,input,stage}-sha.txt`.

## Gaps

No GL viewport state readback; live raylib render dimensions and decoded full-width screenshots establish occupancy. Touch mapping was not exercised. Guest texture and font detail is unchanged at its 512×448/640-stride source; native viewport scaling only improves native overlay edges. No device build or run was within scope.
