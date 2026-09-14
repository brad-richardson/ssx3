# 120 Hz by depth reprojection — design, September 13, 2026

**Proposal:** stop producing the in-between frame with the emulator at all.
Keep the game at 60 Hz on its two threads and let the GPU synthesize every
second displayed frame by reprojecting the last real frame with its depth
buffer and the camera's predicted half-step motion, with the HUD composited
unwarped. This is the "timewarp" technique from VR, applied to the emulated
picture. It is the only approach found so far whose cost fits the phone at
2× internal detail and comes close at 3×.

Target stated by the user: 3× Match at 100–120 displayed frames per second
with no drop below 0.95 game speed. The game never does extra work in this
design, so the speed condition holds by construction; the display-rate
condition is bounded by the GPU budget measured below.

## What has been tried, and why none of it can reach the target

| Approach | Status | Why it cannot reach the target |
| --- | --- | --- |
| Native re-entry: re-run the guest render callback with interpolated palettes (`120hz-native-interpolation.md`, the phone's "Try smoothing") | Built, measured on the phone through September 13 | Each extra frame costs the guest's whole render callback on the CPU thread: 7.8 ms after dual-core. Update plus render already take 11.1 ms of a 16.7 ms frame; a second render is 18.9 ms. Every phone trial ended through the speed guard, and relaxing the guard only lengthens a trial that cannot fit. Structural, not a tuning problem. |
| Color-only frame generation: block-matching motion estimation between two presented frames (`spike/120hz`, approach 1) | Built and measured once on the Mac, September 11 | 10.4 ms GPU per synthesized frame at 1556 × 966 and the game fell to 4.9 FPS at 0.36× because the presentation path blocked the emulation thread. Motion estimated from color is expensive and wrong where color is ambiguous (snow). |
| Camera-aware interpolation with depth feeding Apple's MetalFX frame interpolator (`spike/120hz`, approach 2) | Designed, camera trace written, **never built or run** (the runtime rebuild was blocked by a full disk, then the native path took priority) | Sound inputs, but interpolation needs the *next* real frame before it can show the in-between one, adding a frame of input latency, and its cost on the phone is unmeasured. Kept here as the alternative backend. |
| Camera-only re-render by FIFO replay (`spike/120hz` approach 3; `120hz-host-replay.md`) | Capture and private audit only; rendering deliberately blocked | Re-rasterizes the whole frame: at 3× that is a second 7.4 ms median GPU frame, about 15 ms per 16.7 ms with p95 over 20. Fits at 1×, marginal at 2×, out at 3×. |

To be precise about the question that prompted this document: MetalFX was
never attempted. The failed attempt was the color-only block matcher.

## Measured budget

From the user's September 13 session at every detail and output setting
(`local/reports/mobile/20260913-231157/Reports/1789354928.040`, build
`060197cd`, dual-core, riding seconds only). GPU time is the presenting
command buffer's duration, which is close to the whole frame's GPU work here.

| Internal detail | GPU per real frame, median / p95 / max | CPU thread per frame (update + render) | Render wall minus CPU |
| --- | ---: | ---: | ---: |
| 1× | 1.8–2.3 / 3.0 / 5.5 ms | 3.0 + 8.3 ms | ≤ 0.06 ms |
| 2× | 4.4–5.0 / 6–7 / 9.9 ms | 3.2 + 6.9 ms | ≤ 0.05 ms |
| 3× | 7.1–7.4 / 9–10.5 / 15.5 ms | 3.4 + 8.1 ms | ≤ 0.05 ms |
| 4× | 8.5–8.8 / 13.5 / 16.0 ms | 3.3 + 8.1 ms | ≤ 0.05 ms |

Two conclusions. Internal detail costs the CPU thread nothing and the GPU
thread has kept up at every setting, so a synthesized frame must be paid for
on the GPU alone, and it must be cheap: at 3× the real frame already uses
about 7.4 ms of every 8.33 ms display slot at the median and exceeds it at
the 95th percentile. A full-screen reprojection pass at output resolution is
in the 1–2 ms class on this GPU. Expected result: 2× Match at a consistent
120 with margin; 3× Match mostly at 120 with real frames occasionally landing a
slot late in the heaviest sections (about 100–110 effective); 4× is out.

## The design

```text
CPU thread (unchanged 60 Hz game)
  update → render → FIFO ……………………………………………… side channel: view matrix V_k, frame id k
GPU thread (Dolphin video thread, dual-core)
  decode frame k → EFB → at the XFB copy:
      keep color_k (before HUD) , depth_k , HUD_k (ortho draws) , P_k (projection)
      present real frame k
      C = V_pred × V_k⁻¹  with V_pred = extrapolate(V_{k-1}, V_k, +½ step)
      synth = warp(color_k, depth_k, P_k, C)  ⊕  HUD_k  → present at k + ½
  decode frame k+1 …
```

- **Inputs already available.** Depth: `FramebufferManager::GetEFBDepthTexture()`
  (R32F, inverted when the backend supports a reversed range). Projection:
  `VertexShaderManager` holds the expanded 4×4; `xfmem.projection` gives the
  raw GX form and its perspective/orthographic type. Color: the EFB at the
  XFB copy. View matrix: GX has no separate view matrix, but the native
  pose-interpolation adapter already recovers the camera from the guest's
  view-matrix call (`0x80224cc8`, `120hz-native-path.md`) and interpolates it;
  that recovery becomes a per-frame side channel to the renderer instead of a
  reason to re-enter the guest.
- **Capture point.** The XFB copy (`TextureCacheBase::CopyRenderTargetToTexture`,
  `is_xfb_copy`) is the end of the guest's frame and precedes the next clear;
  capturing at `Presenter::Present` is too late. Color must be split before
  the HUD: record the EFB color when the first orthographic-projection draw of
  the frame starts, and let the HUD draws land in a separate target. Whether
  every HUD element is orthographic is an assumption to verify with a capture.
- **Warp.** Per output pixel: reconstruct the view-space point from depth and
  P_k⁻¹, apply C, project with P_k, sample color_k at the resulting position.
  Implement as a gather with a small forward-splat fallback for disocclusion
  holes, or as a coarse depth-mesh drawn with C (the common VR form); either
  is one pass at output resolution. Holes appear at screen edges and behind
  foreground objects only for half a frame of camera motion.
- **Prediction, not interpolation.** V_pred extrapolates from the last two
  camera poses, so the synthesized frame is shown before the next real frame
  exists and no input latency is added. Extrapolation errors are bounded by
  half a frame of camera acceleration; camera cuts, respawns and teleports
  reset history and skip synthesis for that frame, using the adapter's
  existing teleport detection.
- **Scheduling.** Reuse the deadline and pacing machinery from the native
  trial (`render_deadline.h`, presentation trace, pacing acceptance), moved to
  the GPU thread: after presenting real frame k, if the synthesized frame can
  be encoded before the next 8.33 ms slot, encode and present it; otherwise
  drop it. Never wait on the CPU thread and never block the video thread on
  a drawable: the September 11 prototype fell to 5 FPS precisely because its
  presentation path stalled emulation. Keep three drawables and measure
  `nextDrawable` waits.
- **Fallback.** Any budget miss, missing history or unsupported state presents
  real frames only. The game is never slowed.

## Known limitations

- Objects with their own motion (rider, opponents, snow spray, gates) move at
  60 Hz inside a 120 Hz camera. With a chase camera their screen-space motion
  is small, so this reads as slight softness of motion on the rider, not judder
  of the world. Per-object reprojection would need object palettes and depth
  IDs and is out of scope for the first version.
- Transparent and unlit passes (spray, lens flares, skybox drawn at infinity)
  reproject with the depth that was written, which may be wrong for them.
- Disocclusion at edges and behind the rider for half a frame of motion.
- Depth conventions (GX Z range, Dolphin's inverted R32F depth, any vertex
  depth remap) must be derived once and verified on captures.
- The HUD split relies on identifying HUD draws; UIKit touch controls are not
  part of the image and are unaffected.
- This is presentation smoothing: physics, input polling and animation stay at
  60 Hz.

## True 120 Hz simulation, and the hybrid that could actually work

Running the whole game loop at 120 Hz, fixing every timestep consumer with
targeted decompilation, is the approach that would need no synthesis at
all. On this phone it is blocked by budget before it is blocked by math:

- **CPU thread.** Update plus render is 11.1 ms per game frame after
  dual-core; at 120 Hz that is 22.2 ms per 16.7 ms, 133% of a core. The
  render callback alone (7.8 ms) would have to be halved. Generated-code
  work (fast floating point, fewer chassis round trips) is expected to
  recover tens of percent, not half, and the callback is the game's own
  scene traversal.
- **GPU.** At 3× internal a real frame costs 7.4 ms median; 120 real frames
  is 14.8 ms per 16.7 ms with p95 over 20. Same wall as re-rasterizing.
- **Timestep consumers.** Physics substeps, trick windows, camera smoothing
  constants, animation and particle rates, AI, UI timers. The handoff's
  time-normalized experiments (`ssx3-120hz-handoff-2026-09-13.md` §02) are
  the way to find them, and the engine has leads: the application loop's
  accumulator at `0x801CD248` derives an integer update count per iteration,
  and the render callback consumes an elapsed count (`application+168`,
  incremented per update, converted with `/60.0`), which suggests the game
  already separates simulation steps from rendered frames.

Those same leads point at a hybrid that fits the budget: **simulate at
120 Hz, rasterize at 60 Hz, present at 120 Hz by reprojection.** The update
callback is only 3.3 ms, so two updates per rendered frame is 6.6 + 7.8 =
14.4 ms on the CPU thread, inside the 16.7 ms frame with fast floating
point's margin on top. Input is polled and integrated at 120 Hz, so input
latency halves. The camera pose at the half step is then *real*, not
predicted, so the reprojected frame is exact for the camera and all
static geometry; only objects with their own motion keep a 60 Hz cadence,
and the elapsed-count bookkeeping suggests animation would advance by the
right amount when render runs every second update. This still needs the
timestep work (halved dt everywhere it is baked in) and a controlled way
to run the render callback on alternate updates, which is the readiness
gate and elapsed-count seam already mapped in `120hz-native-path.md`.

Sequence that keeps risk low: build the reprojection presentation first
(it works with either simulation rate and is the deliverable), and run the
time-normalized experiments as the research track: half cadence with
doubled dt on the Mac under movie playback to list what does not honor a
common timestep, then double cadence with halved dt. If the simulation can
be made to run at 120 Hz cleanly, plug it into the same presentation path
and the extrapolation step disappears.

## MetalFX as the alternative backend

`MTLFXFrameInterpolator` (iOS 26, iPhone 16 Pro Max supported) takes previous
and current color, depth, per-pixel motion, a separate UI texture and the
projection scalars, and produces the in-between frame in hardware, with
learned disocclusion filling. The same capture (color before HUD, depth, HUD
layer, projection) feeds it; motion vectors come from the same reprojection
math (static-geometry motion from depth and the camera delta). Its two costs
are one frame of added latency, because it interpolates between k and k+1
rather than predicting, and an unmeasured GPU time. Build the capture and the
camera side channel once; try our warp first, MetalFX second if edge quality
is unacceptable.

## Batch 3 plan

1. **Instrument** (small): GPU-thread busy fraction per second; total GPU
   time per frame across all command buffers; `nextDrawable` wait; per-frame
   view matrix from the adapter side channel logged with the frame id.
2. **Capture** (medium): at the XFB copy keep color-before-HUD, HUD, depth and
   projection for the last frame; verify on captures that depth covers the
   whole frame at that point and that HUD draws are orthographic.
3. **Warp and present** (medium): the reprojection pass and the GPU-thread
   scheduler behind the existing "Try smoothing" control, real-frames-only
   fallback everywhere.
4. **Measure** on the phone with the existing pacing acceptance tool
   (117 presentations per second, p95 spacing ≤ 10 ms, speed ≥ 0.98, thermal
   fair or better, 25 continuous seconds): 2× Match first, then 3× Match.
   Compare synthesized frames against the real frame that follows them from
   frame dumps to quantify edge artifacts before judging by eye.

Acceptance is the user's target restated: 3× Match, sustained 100–120
presentations per second, game speed never below 0.95, with frame dumps that
show the synthesized frames are distinct and coherent.

## Evidence

Phone session and GPU-time buckets: `local/reports/mobile/20260913-231157/`
and `docs/research/performance-review-2026-09-13.md` (batch 1 and 2
results). Earlier attempts: `spike/120hz` worktree
(`native/spike-120hz/README.md`, September 11 measurement),
`120hz-analysis.md`, `120hz-native-interpolation.md`, `120hz-host-replay.md`.
