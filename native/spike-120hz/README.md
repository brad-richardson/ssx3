# 120 Hz presentation spike (branch `spike/120hz`)

Date: 2026-09-11. Status: **prototype written and syntax-checked, not yet built or run.**
The runtime rebuild that the prototype needs was blocked by the machine's disk being full
(see [Blocker](#blocker-and-how-to-resume)). Nothing in this document is a measured result
unless the table says so; every number the task asked for is still "not measured".

## What was tried

| Step | Outcome |
| --- | --- |
| Locate the Metal present path | Done. `Presenter::Present` (VideoCommon/Present.cpp) renders the XFB into the bound backbuffer and calls `Metal::Gfx::BindBackbuffer` / `PresentBackbuffer` (VideoBackends/Metal/MTLGfx.mm), which take a `CAMetalLayer` drawable and present it from a scheduled handler of the render command buffer. |
| Color-only interpolation prototype (approach 1) | Written as `MTLFrameGen.{h,mm}` plus hooks in `MTLGfx.{h,mm}`; passes `clang++ -fsyntax-only`. Not compiled into the runtime, not run. |
| Camera extraction for depth-aware interpolation (approach 2) | Code reading done and documented below; a per-frame trace (`SSX3_CAMERA_TRACE=1`, `VideoCommon/CameraTrace.cpp`) is in the patch, syntax-checked, not run. MetalFX frame interpolator API confirmed in the macOS 26 SDK headers. |
| Camera-only re-render (approach 3) | Research only, below. |
| Runtime rebuild with the patch | **Blocked.** The worktree's `local/native/runtime-build` was a copy whose `CMakeCache.txt`/`build.ninja` pointed at the main checkout's sources and build directory, so it could not build the spike sources; a fresh configure failed with `No space left on device` (about 0.5 to 1.0 GiB free on the Data volume during the attempt). |

## Measurements

| Metric | 640x480 window | 1280x960 window | Notes |
| --- | --- | --- | --- |
| Presented frames/s (framegen on) | not measured | not measured | `[ssx3-framegen] ... rate=` in the run log |
| Presented frames/s (stock, `SSX3_FRAMEGEN=stats`) | not measured | not measured | |
| Added latency of the real frame (ms) | not measured | not measured | `latency_ms real_avg` framegen minus stats mode |
| GPU time per synthesized frame (ms) | not measured | not measured | `gpu_ms avg/max` from `MTLCommandBuffer` GPU timestamps |
| Visible artifacts | not observed | not observed | dump triplets with `SSX3_FRAMEGEN_DUMP` |

The Mac used for this spike (Apple M4, built-in "Liquid Retina" display) reports
`NSScreen.maximumFramesPerSecond = 60`. It can measure GPU cost, the presented-frame counters,
and the artifacts (through the frame dumps and the `SSX3_FRAMEGEN_ONLY=1` mode), but it cannot
show a 120 Hz cadence; the second present of each game frame will be dropped or immediately
replaced on this display. A 120 Hz display (the iPhone 16 Pro Max, the Odin 3, or an external
monitor) is needed to see the cadence.

## Blocker and how to resume

1. Free disk space: a Release build of the Dolphin-derived runtime needs a few GiB. The largest
   spike-irrelevant copies inside this worktree are `local/builds` (1.1 GiB, PS2 build
   archives), `local/evidence` (0.8 GiB), `local/native/ios-device` (0.6 GiB),
   `local/native/ios-simulator` (0.6 GiB), and `local/native/swift-module-cache` (0.1 GiB).
   Deleting them from the worktree was attempted and refused by the tool permission policy,
   so a person has to decide. Note `local/native/ios-simulator` is the copy a simulator check
   would use; without it the simulator part of the task needs a fresh
   `python3 tools/mobile_gamecube.py build --simulator`.
2. Reconfigure the worktree build against the worktree sources (the previous, mis-pathed copy
   of `runtime-build` was removed; a partial cache from the failed configure may remain):

   ```sh
   cd /Users/bradrichardson/dev/ssx3-120hz
   rm -rf local/native/runtime-build
   python3 tools/native_gamecube.py configure
   python3 tools/native_gamecube.py build --jobs 4
   ```

   `configure` and `run` verify that the vendored Dolphin equals the pinned revision plus
   `recompcore-platform.patch` plus `spike-120hz.patch`, applied in that order (the runner's
   `check_stacked_patches`). The module (`local/native/ssx3-module`) is unchanged.
3. Run the measurements (below).

## Approach 1: color-only interpolation (prototype)

Files (all inside `third_party/ModernGekko/vendor/dolphin/Source/Core`, recorded in
`native/patches/spike-120hz.patch`):

- `VideoBackends/Metal/MTLFrameGen.h`, `MTLFrameGen.mm`: the interpolator and its statistics.
- `VideoBackends/Metal/MTLGfx.mm`: `Gfx::Gfx` creates the interpolator when `SSX3_FRAMEGEN` is
  set and turns off `framebufferOnly` on the layer; `BindBackbuffer` binds the offscreen
  history texture instead of a drawable; `PresentBackbuffer` commits the game's command buffer
  and calls `FrameGen::Present`; `SetupSurface` resizes the history. With the variable unset
  none of these branches execute.
- `VideoBackends/Metal/CMakeLists.txt`: adds the two files.

Pipeline per game frame (one `MTLCommandBuffer` labelled `FrameGen`, committed after the game's
own `Draw` buffer on the same queue, so ordering is guaranteed):

1. Luma (R8) of the current frame, then a four-level 2x box pyramid (`fg_luma`, `fg_down`).
   The previous frame's pyramid is kept in the other history slot.
2. Bilateral, hierarchical 8x8 block matching (`fg_match`): at the coarsest level (1/8) an
   exhaustive +-6 px search (about +-96 px of full-resolution motion between frames); at each
   finer level the parent block vector and its four neighbours are candidates, followed by a
   +-1 px refinement, with a small penalty for leaving the parent vector. The cost is
   `SAD(prev(p - v/2), cur(p + v/2))` over the block, so the vector is estimated at the
   position of the synthesized frame and there are no holes to fill.
3. Vector-median style smoothing at the finest level (`fg_smooth`).
4. Synthesis (`fg_warp`): each pixel evaluates the bilinearly interpolated vector plus the four
   nearest block vectors, keeps the one whose motion-compensated pair agrees best at that pixel,
   and writes the average of the two samples. This keeps motion boundaries sharper than a
   bilinear vector field alone.
5. Present: the synthesized frame is blitted into a drawable and presented; the real frame is
   blitted into a second drawable and presented with `presentAfterMinimumDuration:1/120`.
   So the real frame is delayed by half a game frame (8.3 ms) plus the interpolation GPU time,
   which is the "one extra frame" budget the task allows (it is actually half of one).

Shaders are MSL compiled at runtime with `newLibraryWithSource:`, the same mechanism the
Metal backend already uses for the game's own shaders; no CPU code generation is involved.
For shipping on iOS they should move into a precompiled `.metallib`.

Environment variables:

| Variable | Effect |
| --- | --- |
| `SSX3_FRAMEGEN=1` | Enable interpolation (two presents per game frame). |
| `SSX3_FRAMEGEN=stats` | Stock presentation; only records presented-time statistics for the latency baseline. |
| `SSX3_FRAMEGEN_ONLY=1` | Present only synthesized frames. On a 60 Hz display this shows the interpolation quality directly (the game looks normal only if the synthesis is good) and lets `screencapture -l<windowid>` grab synthesized frames. |
| `SSX3_FRAMEGEN_DUMP=DIR` | Every `SSX3_FRAMEGEN_DUMP_EVERY` (default 600) game frames after `SSX3_FRAMEGEN_DUMP_FROM` (default 1200), write `frame-N-{prev,cur,interp}.bgra` into DIR. Convert with `python3 native/spike-120hz/convert_dumps.py DIR --scale 0.5` to get PNGs and a prev/interp/cur contact sheet. |
| `SSX3_CAMERA_TRACE=1` | Approach 2 trace, see below. |

Statistics are printed every 300 game frames as `[ssx3-framegen] ...`: interpolation GPU time
(average/max from `GPUStartTime`/`GPUEndTime`), presented drawables per second (from
`CAMetalDrawable.presentedTime`, counting only drawables that reached the screen), the number
of presented intervals at or below 12 ms versus above (a 120 Hz cadence shows as mostly "<=12
ms"), and the submit-to-presented latency of real and synthesized frames.

Planned measurement procedure (not executed):

```sh
# Fresh profile, window sized to the native XFB (640x480) or 2x.
P=framegen-640; mkdir -p local/native/profiles/$P/Config
printf '[Core]\nCPUThread = False\nDSPHLE = True\nSkipIPL = True\n[DSP]\nEnableJIT = False\n[Interface]\nConfirmStop = False\n[Display]\nRenderWindowWidth = 640\nRenderWindowHeight = 480\n' > local/native/profiles/$P/Config/Dolphin.ini
SSX3_FRAMEGEN=1 SSX3_FRAMEGEN_DUMP=local/reports/framegen-dumps python3 tools/native_gamecube.py run --profile $P --seconds 250 --pipe-controller &
python3 tools/native_replay.py --profile $P --sequence native/ios/snow-jam-smoke.json   # reaches the Snow Jam ride
# Repeat with SSX3_FRAMEGEN=stats for the latency baseline, then with a 1280x960 window.
python3 native/spike-120hz/convert_dumps.py local/reports/framegen-dumps --scale 0.5
```

Expected artifacts to look for in the dumps (known failure modes of color-only interpolation,
none observed yet because nothing ran): the HUD (speed, score, boost bar, minimap) is static
over moving terrain, so blocks that straddle HUD edges get either the HUD's zero vector or the
terrain's vector and the losing side ghosts or wobbles by up to half the motion; thin rails and
tree trunks against sky may smear; the rider's limbs move differently from the board and can
tear at the 8x8 block scale; scene cuts (restart, camera snaps) produce one garbage frame,
which a scene-change detector (mean block cost above a threshold, fall back to the real frame)
should suppress. The prototype has no scene-change fallback yet.

## Approach 2: camera-aware interpolation with depth

What Dolphin exposes (all under `Source/Core/VideoCommon`):

- **Projection.** `xfmem.projection` (`XFMemory.h`) holds the GX projection: `type`
  (perspective/orthographic) and `rawProjection[6]`. `VertexShaderManager::LoadProjectionMatrix`
  (VertexShaderManager.cpp lines 41-120) expands it into the 4x4 uploaded to the vertex shader:
  `m[0]=raw[0]`, `m[2]=raw[1]`, `m[5]=raw[2]`, `m[6]=raw[3]`, `m[10]=raw[4]`, `m[11]=raw[5]`,
  `m[14]=-1`. From that, `near = raw[5]/raw[4]`, `far = raw[4]*near/(raw[4]+1)`,
  `fov_y = 2*atan(1/raw[2])`, `aspect = raw[2]/raw[0]`, which are exactly the scalars the MetalFX
  interpolator wants (`nearPlane`, `farPlane`, `fieldOfView`, `aspectRatio`). The projection
  changes several times per frame (skybox, world, rider, HUD in ortho), so the trace groups
  perspective flushes by raw projection and counts indices per group.
- **View matrix.** GX has no separate view matrix. Each draw's position matrix is
  `xfmem.posMatrices[idx*4 .. idx*4+12]` (3x4, row-major), selected by
  `g_main_cp_state.matrix_index_a.PosNormalMtxIdx` (or per vertex when the vertex format has a
  matrix index, `vert_decl.posmtx`). `VertexShaderManager::SetConstants` copies the whole table
  into `constants.transformmatrices`. For static geometry drawn with the identity model
  transform folded into the camera (typical for terrain), the dominant position matrix *is* the
  view matrix. The trace reports the three position-matrix indices that transformed the most
  indices per frame with their values; the one that stays consistent across frames and moves
  smoothly with the camera is the candidate.
- **Depth.** `FramebufferManager::GetEFBDepthTexture()` (FramebufferManager.h line 63) is the
  live EFB depth. The right moment to snapshot it, together with the frame's dominant matrices,
  is the XFB copy (`TextureCacheBase::CopyRenderTargetToTexture`, TextureCacheBase.cpp line
  2129, `is_xfb_copy` at line 2193): that is when the game has finished the frame, and before the
  next frame's clear. Snapshotting at `Presenter::Present` is too late in single-core mode
  because the next frame may already be drawing. `ResolveEFBDepthTexture` handles MSAA. The
  depth is in GX's convention (the vertex shader may remap it, see
  `UseVertexDepthRange`), so the reprojection must use the same `near/far` derivation.
- **Motion vectors for static geometry.** With depth `d` at pixel `p`, the previous frame's
  view-projection `VP0` and the current `VP1`: unproject `(p, d)` with `VP1^-1`, project with
  `VP0`, motion = `p_prev - p`. Dynamic objects (rider, opponents, particles) get the camera
  motion only; that is the standard limitation without per-object matrices, and SSX's third
  person camera follows the rider so the rider's screen-space motion is small.
- **MetalFX.** The macOS 26 SDK ships `MetalFX/MTLFXFrameInterpolator.h`, `API_AVAILABLE(macos(26.0),
  ios(26.0))`: `MTLFXFrameInterpolatorDescriptor` (color/depth/motion/output/UI formats, input
  and output sizes, optional scaler) creates an `id<MTLFXFrameInterpolator>` with
  `colorTexture`, `prevColorTexture`, `depthTexture`, `motionTexture` (pixel units after
  `motionVectorScaleX/Y`, pointing from the current pixel to its location in the previous
  frame), `deltaTime`, `nearPlane`, `farPlane`, `fieldOfView` (vertical, degrees),
  `aspectRatio`, `depthReversed`, an optional `uiTexture` (with `uiTextureComposited`) that it
  overlays without interpolating, `shouldResetHistory`, `outputTexture`, and
  `encodeToCommandBuffer:`. The `uiTexture` input is the direct fix for HUD ghosting: Dolphin
  can split ortho-projection draws (HUD) into a separate render target and hand them to the
  interpolator as UI. It does not need a full matrix, only the scalars above plus motion.

What is still unknown until the trace runs: which position-matrix index SSX 3 uses for the
world, whether terrain vertices carry per-vertex matrix indices, how many perspective
projections the game sets per frame, and whether the EFB depth at XFB-copy time is a full
frame (the game may clear depth between passes).

## Approach 3: camera-only re-render (research only)

Dolphin consumes the game's GP FIFO once; there is no retained per-frame draw list. Re-rendering
with an interpolated camera would need one of:

- **FIFO recording and replay.** Dolphin's `Core/FifoPlayer` (`FifoRecorder`, `FifoPlayer`)
  already captures the GP command stream and the memory it reads per frame and can replay it.
  A per-frame in-memory recorder plus a replay with `xfmem.posMatrices[dominant]` and
  `xfmem.projection` overridden (the same interception point `FreeLookCamera` uses in
  `LoadProjectionMatrix`) is the most direct route. Costs: the whole frame's vertex loading and
  draws run twice on the GPU (and the vertex loader runs on the CPU in this no-JIT build,
  `VertexLoaderType::Software`, so the CPU cost doubles too), texture cache and EFB copies must
  be isolated from the replay, and only the camera moves: the rider animation, opponents and
  particles stay frozen in the synthesized frame. The HUD renders correctly (no ghosting).
- **Interpolating XF matrices in place** during the next frame's decode is not possible: the
  synthesized frame must exist before the next real frame is decoded.

Verdict: feasible with existing Dolphin infrastructure but a multi-week change with double the
per-frame CPU/GPU load, which is the wrong direction for the phone. Not recommended before
approach 2 has been tried.

## Recommendation

1. Finish approach 1 first (unblock the build, run the measurement plan, inspect dumps). It is
   self-contained, needs no game knowledge, and gives the GPU-cost and cadence numbers on the
   real hardware. Add the scene-change fallback before judging quality.
2. Run `SSX3_CAMERA_TRACE=1` during a Snow Jam ride to identify the world matrix index and
   projection. If one perspective projection dominates and one position matrix is consistent,
   build the depth-reprojection motion vectors at XFB-copy time and feed `MTLFXFrameInterpolator`
   with the HUD split into `uiTexture`; that removes the HUD ghosting that approach 1 cannot
   fix and needs no block matching of our own. Keep the color-only path as the fallback for
   devices below iOS 26.
3. Do not pursue approach 3.

## Remaining work for iOS (estimate)

- Build the interpolation into the iOS app's render path (`native/ios/App.mm` hands a
  `CAMetalLayer` to the same `Metal::Gfx`, so the hook is shared; only the env-var switch needs
  a settings toggle): small.
- 120 Hz presentation on ProMotion: `CADisableMinimumFrameDurationOnPhone` in `Info.plist` and
  a `CADisplayLink`/`CAMetalLayer` frame-rate range of 120; verify `maximumDrawableCount`
  (three drawables, two presents per game frame) does not stall `nextDrawable`, and disable the
  second present on 60 Hz displays (`UIScreen.maximumFramesPerSecond`), otherwise the emulation
  would be throttled to 30 game frames per second: one to two days including device runs.
- Precompile the MSL into a `.metallib` for the app bundle: small.
- Thermal/power measurement on the phone with the same `snow-jam-smoke.json` sequence: the GPU
  cost of block matching at 1x is unmeasured; on the phone the interpolation competes with the
  game's own rendering and the interpreter CPU load.
- MetalFX path (approach 2): one to two weeks after the trace confirms the camera, mostly in
  Dolphin's XFB-copy path and the HUD split.

## Files

- `native/patches/spike-120hz.patch`: all runtime changes (diff against the platform-patched
  vendored Dolphin). Apply after bootstrap with
  `git -C third_party/ModernGekko/vendor/dolphin apply native/patches/spike-120hz.patch`;
  regenerate with `native/spike-120hz/make_patch.sh`.
- `native/spike-120hz/convert_dumps.py`: raw dump to PNG/contact sheet converter.
- `tools/native_gamecube.py`: `check_stacked_patches` so `configure`/`run` accept the stacked
  patch.
- No screenshots yet: none were produced because the runtime was not built.

## First measurement (2026-09-11, Mac, 60 Hz display, 1556x966 window)

Two 250 s runs with the Snow Jam smoke sequence; statistics windows after
the first 120 s (menus and load excluded). Logs: `local/reports/native-runs/
20260911-113258.log` (stats) and `20260911-113715.log` (framegen).

| Measure | `SSX3_FRAMEGEN=stats` | `SSX3_FRAMEGEN=1` |
| --- | ---: | ---: |
| Emulated game FPS / speed | 59.4 / 0.99 | **4.9 / 0.36** |
| Presented frames per second | 58.9 | 8.1 (437 real + 494 synthesized) |
| GPU time per synthesized frame | n/a | 10.4 ms avg, 16.7 ms max |
| Submit-to-present latency, real frames | 46.3 ms avg | 204.9 ms avg, 1049.9 max |
| Scene-cut fallbacks | n/a | 0 |
| Frame dumps written | n/a | none (dump threshold of 1200 frames not reached) |

Conclusion: the prototype as built is not usable. The synthesized frame's GPU
cost alone (10 ms at native resolution) would leave no room for two presents
per 16.7 ms game frame, and something in the pipeline blocks the emulation
thread hard enough to cut the game to a third of its speed, most likely a
CPU-side wait on the interpolation command buffer or the delayed present.
Before any quality judgement: make the pass fully asynchronous (no waits on
the CPU thread; present the synthesized frame from a completion handler),
cut the motion search to one coarse level with 16x16 blocks, and re-measure.
If GPU cost stays above about 4 ms, the color-only approach is out on the
phone and the remaining option is MetalFX with depth-reprojected motion
vectors (approach 2), which does its estimation in hardware.
