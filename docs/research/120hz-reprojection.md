# 120 Hz reprojection research — bounded first batch, September 14, 2026

**Recommendation:** keep the original 60 Hz simulation as the reference and test
camera/depth reprojection as a small presentation experiment. The first milestone
is a matched capture and an offline half-step warp, not a live 120 Hz mode. Course
restoration remains the main project priority.

The initial September 13 proposal made stronger claims than the evidence supports.
This revision replaces those claims with explicit gates. No phone speed, resolution,
image-quality or latency target has yet been demonstrated by reprojection.

## What the evidence supports

The September 13 phone session (`local/reports/mobile/20260913-231157/`, build
`060197cd`, dual-core) recorded these riding costs:

| Internal detail | Presenting GPU command buffer median / p95 / max | CPU update + render |
| --- | --- | --- |
| 1× | 1.8–2.3 / 3.0 / 5.5 ms | 3.0 + 8.3 ms |
| 2× | 4.4–5.0 / 6–7 / 9.9 ms | 3.2 + 6.9 ms |
| 3× | 7.1–7.4 / 9–10.5 / 15.5 ms | 3.4 + 8.1 ms |
| 4× | 8.5–8.8 / 13.5 / 16.0 ms | 3.3 + 8.1 ms |

These are **presenting command buffer** timings, not verified total GPU work for
each frame. One real and one synthetic frame share a 16.67 ms aggregate budget:
real rendering + capture + warp + HUD composition. Scheduling must also meet the
individual 8.33 ms presentation deadlines. A real frame does not inherently need to
finish within 8.33 ms, but command ordering and drawable waits can spoil pacing.

The proposed 1–2 ms warp is unmeasured. “2× consistent 120,” “3× 100–110,” and
“4× impossible” were predictions, not results. GPU, memory and thermal contention
can slow the game even if simulation remains at 60 Hz. There is no game-speed
guarantee “by construction.” Fixed 3× internal resolution is a quality preference;
lower or adaptive resolution remains a reasonable way to protect pacing.

Repeated guest render callbacks are too expensive in the current phone build:
update + render is about 11.1 ms; another 7.8 ms callback exceeds a 16.67 ms CPU
budget. This constrains the present implementation, not every future renderer or
native optimization. The color-only block matcher was built and failed: 10.4 ms
GPU at 1556×966 and a blocking presentation path that dropped the game to 4.9 FPS.
MetalFX frame interpolation was **not** the failed prototype; it was never built.

## The first batch

`tools/gamecube_reprojection.py` compiles isolated copies of three renderer source
files into a fresh `local/` output and links them ahead of the existing libraries.
It checks injection anchors and records source/header/player hashes. It never edits
vendor sources, the production player, the module, phone settings, simulation or
the presentation scheduler. Generated assets and players stay ignored under
`local/research/120hz/reprojection-batch/`.

The GPU decoder captures at most eight consecutive XFB intervals after the chosen
start time:

1. Observe GX indexed position-matrix array slot zero (48-byte stride) after the
   decoder has consumed the load. The existing native palette investigation
   identifies slot zero as the camera candidate. Record the actual decoded values,
   array ownership, load count and frame association. This avoids reading a CPU
   “latest camera” that may already belong to another frame. Semantic camera
   validation remains separate from transport/frame matching.
2. At the first perspective-to-orthographic draw transition, read back EFB world
   color and depth before the orthographic draw executes. Save the preceding
   perspective projection, viewport, scissor offsets, pixel-center correction and
   backend depth convention together with the camera candidate.
3. At the XFB copy, before clear/reuse, read back final EFB color and record its
   source rectangle/address, draw-batch flush counts and any perspective draws after the split.
   Later perspective work invalidates a simple “orthographic tail = HUD” assumption.

These are deliberately blocking readbacks for correctness research. Their FPS and
wall time must **not** be used to estimate live capture or phone performance.
Unsupported formats or missing attachment/camera data fail the offline input gate.

`tools/gamecube_reprojection_warp.py` reconstructs view-space positions using the
captured GX projection, depth range and viewport, predicts half a camera step from
two consecutive rigid camera poses, then uses a depth-tested forward splat.
It rejects camera cuts/teleports and non-rigid camera candidates. Holes remain
magenta instead of being concealed by inpainting. An identity transform must
reproduce the original pixels, and synthetic translation controls check the
expected perspective/parallax direction and magnitude.

The tool exports source/final/depth views, a half-step image, coverage and motion
statistics, and a visual contact sheet. This is an offline geometry proof, not a
realtime implementation.

Each source pixel splats either as a point or as its own screen-space footprint.
The footprint half-extent comes from the warped step to that pixel's own
neighbours, capped at two pixels, and a step across a depth discontinuity is
discarded rather than used — a silhouette is not a stretched surface, so
foreground must not be widened over the background behind it. Because the
half-extent never falls below half a pixel, the footprint splat always covers
everything the point splat covers. This approximates rasterizing the depth
buffer as a mesh; it is not that rasterizer, and no live backend uses it.

**HUD gate:** final-minus-world color is a useful diagnostic of what the candidate
tail changed, but is not a separate alpha HUD texture. Given one composited image,
alpha and foreground color cannot generally be recovered. Adding that residual to
a warped background is explicitly labeled approximate and is not an acceptable
live HUD implementation. Proper draw routing or another validated isolation method
is required; perspective/orthographic classification alone does not prove ownership.

### Paired-background HUD alpha (September 14)

One composite has two unknowns per pixel and one equation, so no amount of care
recovers alpha from a single run. Two runs do, provided they render the *same*
guest frame. Under `SSX3_MOVIE_PLAY` a single-core run replays recorded pad
input against a fixed guest clock, so guest frame numbers repeat exactly where
host wall time does not — hence `SSX_REPROJECTION_FROM_FRAME`, which arms the
capture on the guest's XFB counter rather than `SSX_REPROJECTION_AFTER`.

`SSX_REPROJECTION_HUD_CLEAR=RRGGBB` clears the EFB colour, and only the colour,
at the split. Depth survives, so the tail still depth-tests against real
scenery, and the presented frame is deliberately wrong for that run. Writing the
tail over two known constants `B0` and `B1` gives

    C0 = F + k*B0        C1 = F + k*B1        k = 1 - alpha

per channel, so `k = (C1-C0)/(B1-B0)` and `F = C0 - k*B0`. `F` is the
premultiplied foreground; `1-k` is the alpha.

This is exact only where the tail's effect on the destination is affine, which
covers ordinary source-over and additive blending but not a blend that reads
destination colour non-linearly. A **third, untouched run** of the same movie
frame is therefore the acceptance test rather than a convenience: `F + k*world`
must reproduce that run's real composite. `tools/gamecube_reprojection_hud.py`
solves the pair, runs that check, and only reports `hud_alpha_layer` true when
the reconstruction stays within two levels. Before solving it requires both runs
to agree on frame ID, draw counts, camera, projection, viewport, EFB pixel
format, and the world colour and depth buffers byte-for-byte — the last being
the strongest available evidence that two runs reached the same guest frame.

Recovering the layer offline still says nothing about compositing it live.

#### Result: the HUD layer is recovered and checked (September 14)

Three 200-second runs of `det-record-1.dtm` against the pinned baseline module,
single-core, armed at `SSX_REPROJECTION_FROM_FRAME=7500`, captured frames
7500–7507 in each: `capture-natural`, `capture-dark` (`000000`) and
`capture-light` (`ffffff`). Replay determinism held exactly — every frame in
every run reports the same draw, perspective and orthographic counts (703/619/84
at 7500), and world colour and depth match byte-for-byte inside the presented
area.

`efb_pixel_format` is **0, `RGB8_Z24`**: this EFB carries no destination alpha.
Routing the tail to a transparent target would not have produced an alpha
channel, so the paired-background route was necessary, not merely convenient.

All eight frames solve and pass the check:

| Frame | HUD coverage | Mean alpha where covered | Reconstruction mean / max error | Within one level |
| --- | ---: | ---: | ---: | ---: |
| 7500 | 7.045% | 0.727 | 0.0142 / 1.73 | 99.992% |
| 7501 | 7.044% | 0.727 | 0.0142 / 1.77 | 99.992% |
| 7502 | 7.043% | 0.727 | 0.0142 / 1.79 | 99.991% |
| 7503 | 7.042% | 0.727 | 0.0143 / 1.68 | 99.992% |
| 7504 | 6.986% | 0.725 | 0.0142 / 1.64 | 99.993% |
| 7505 | 7.045% | 0.727 | 0.0143 / 1.63 | 99.992% |
| 7506 | 7.045% | 0.727 | 0.0143 / 1.71 | 99.992% |
| 7507 | 7.044% | 0.727 | 0.0143 / 1.71 | 99.992% |

Errors are in 0–255 channel units over the presented area. Every pixel of every
frame reconstructs within two levels and 99.99% within one, so **the tail is
affine in the destination colour and this is a real alpha layer**, not another
approximation. The 7.04% coverage independently agrees with the 7.00% that the
old final-minus-world residual mask reported changed — the residual was counting
the right pixels, it just could not say how much of each belonged to the HUD.

One trap is worth recording. The first gate compared whole buffers and rejected
frames 7501 onward for differing world colour. The difference was exactly 240 of
1584 rows — precisely the EFB rows outside the 1344-row XFB area. The game never
redraws them, so each run keeps whichever clear it applied there for the rest of
the run. Those rows are not part of the frame; the gate now compares the
presented area, and all eight frames pass.

This still does not composite anything live. It gives the offline pipeline a
correct HUD layer to composite over a warped background instead of the residual
approximation, and it gives a per-frame alpha to test a live implementation
against.

## First-batch run and validation

Build and run commands (choose fresh output/profile names):

```sh
python3 tools/gamecube_reprojection.py build \
  --output local/research/120hz/reprojection-batch/player
SSX_REPROJECTION_CAPTURE="$PWD/local/research/120hz/reprojection-batch/capture" \
SSX_REPROJECTION_AFTER=140 SSX3_DISPATCH_SAMPLES=0 \
python3 tools/gamecube_reprojection.py check \
  --player-dir local/research/120hz/reprojection-batch/player \
  --game local/game/gc-gari-027 --profile reprojection-example \
  --output local/research/120hz/reprojection-batch/run --seconds 180
```

Offline analysis requires NumPy and Pillow; install into a private research venv.
The standard tests skip numerical controls when these optional dependencies are
absent; run the numerical controls explicitly in that venv:

```sh
local/research/120hz/reprojection-batch/venv/bin/python -m unittest discover \
  -s tests -p test_gamecube_reprojection.py -v
```

Current first-batch controls: injection anchors, identity reprojection, known camera
translation, depth-dependent parallax, half-step pose prediction, camera cut/nonrigid
rejection and explicit holes. Live capture evidence is recorded below when available.

### September 14 capture result

The isolated `player-v3` build and 180-second desktop run completed with Metal
validation enabled against `gc-gari-027`. The run used a fresh profile and the
unchanged production module. Eight consecutive frame intervals, 7558–7565, captured
at around 140 seconds all contain world color, depth, final color and a GPU-consumed
camera candidate. None has later perspective batches after the candidate HUD split.
The source interval is visibly midair riding (75 MPH, game timer around eight seconds),
with moving rider-state telemetry; it is not a loading/menu capture.

Active XFB area is 1920×1344 within a 1920×1584 EFB at 3×. The palette source
alternates between two buffers; requiring the same source pointer would incorrectly
reject this history. Matching uses GPU decoder order and actual matrix values.

For frame 7559, the identity control reproduces every active pixel exactly. Predicted
half-step motion is 4.0 pixels median / 13.2 pixels p95, with 1.875% uncovered pixels
left magenta under a point splat. These include sampling cracks as well as
disocclusion; they are not a final image-quality score. The candidate HUD tail
changes 7.00% of active pixels and visually contains the expected HUD elements.

**Most of that hole area is sampling cracks, not newly exposed scenery.** The
footprint splat on the same frame leaves **0.440%** uncovered, closing 1.435% of
the active area — 77% of the point splat's holes. The remaining 0.440% is still
not established to be disocclusion, and a widened splat can overdraw a true
silhouette; the depth-edge guard and the accuracy check below are what argue
against that here.

Frame 7559 turns out to be an easy frame. Four consecutive pairs from the
movie-driven capture (`capture-natural`, frames 7500–7507) are much harder, and
they are the ones to plan against:

| Pair | Motion p50 / p95 (px) | Point-splat holes | Footprint holes | Cracks closed |
| --- | ---: | ---: | ---: | ---: |
| 7500→7501 | 14.3 / 127.8 | 10.01% | 2.35% | 77% |
| 7502→7503 | 10.6 / 97.6 | 8.33% | 1.64% | 80% |
| 7504→7505 | 1.6 / 83.0 | 7.38% | 1.39% | 81% |
| 7506→7507 | 1.3 / 76.2 | 6.63% | 1.23% | 81% |
| 7558→7559 (earlier capture) | 4.0 / 13.2 | 1.88% | 0.44% | 77% |

Two things hold across all five, and one does not. The share of holes that are
cracks is stable at **77–81%** regardless of how fast the frame moves, and the
footprint splat never covers less than the point splat. But the **absolute**
hole fraction is not a property of the method: it ranges from 0.44% on the calm
frame to 2.35% on the fastest, an over-fivefold spread. Planning from frame 7559
alone would have understated the problem.

The p50/p95 split is itself informative. A median under two pixels beside a p95
near a hundred means most of the image is nearly still while a small near-field
population — rider, board, close scenery — sweeps across it. That is where
camera-only reprojection is weakest, and it is not something better rasterizing
can fix.

An independent check warps frame 7558 using the **actual next camera** and compares
it with the captured frame 7559, on two visible static-wall candidate regions:

| Region | Covered pixels | Unwarped RGB MAE | Warped RGB MAE | Footprint covered | Footprint MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| Left wall | 93.78% | 10.28 | 1.12 | 99.73% | 1.14 |
| Right wall | 95.39% | 14.50 | 2.60 | 99.06% | 2.60 |

Errors use the same covered pixels on both comparisons, in 0–255 channel units;
each footprint column is scored over its own covered pixels, so coverage and
colour accuracy stay separate measurements. The extra coverage is close to free:
on these regions the footprint splat reaches over 99% while changing MAE by 0.02
and 0.005 units. That is evidence on two static walls of one frame, not a general
quality result — the rider, moving objects and transparency are not measured here.
This supports the camera/depth convention on this scene beyond the identity
round trip. It does not certify all render passes, independent object motion,
transparency, or half-step prediction under acceleration. The report keeps broad
camera-semantic acceptance false pending more scenes.

Visual QA confirms that world geometry and rider depth are recognizable and the
predicted scene moves coherently. It also exposes cracks around the rider and on
expanding surfaces, plus edge holes; the rider has no independently advanced pose.
The residual-composited HUD remains an approximation.

Raster coverage is now addressed offline by the footprint splat above, and the
contact sheet shows both splats side by side. **The open item for the next small
batch is a proper alpha HUD layer, then GPU-resident cost measurement**, before
adding a live scheduler. No phone-performance conclusion follows from this run:
both splats are NumPy on the host, and the footprint splat's extra work is real
but unmeasured on a GPU.

Evidence, all ignored and local:

- `local/research/120hz/reprojection-batch/player-v3/build.json`: immutable-source
  build receipt and hashes, including the unchanged production player.
- `local/research/120hz/reprojection-batch/run-002/`: runtime/input/observer logs,
  rider observations and the course check result.
- `local/research/120hz/reprojection-batch/capture-002/`: eight matching raw captures
  and per-frame draw-batch metadata (about 279 MiB).
- `local/research/120hz/reprojection-batch/analysis-002/contact-sheet.png` and
  `report.json`: visually checked proof and scene-specific comparison metrics.

Ten focused controls pass in the private NumPy/Pillow environment, including an
analytic world plane test for both ordinary and Metal vertex depth conventions,
and rejection of missing scene depth or mismatched frame attachments.

## Next gates, after the offline proof

- Validate depth convention against recognizable course geometry and camera motion;
  match the GPU camera candidate to the game's recovered view seam. Exercise tricks,
  rails, close obstacles, opponents, spray, reset/camera cuts and fast transitions.
- Establish a compositable HUD layer and coherent frame ownership. Confirm world
  color/depth correspond across multiple projection and transparent passes.
- Implement GPU-resident attachments and the warp behind a desktop research switch.
  Measure **all** command-buffer work, GPU-thread busy time, queue/drawable waits,
  memory and capture/warp/composition costs. Never infer phone budget from NumPy.
- Only then investigate a bounded presentation scheduler: submit extra frames when
  ready and drop them on deadline misses. It must not block CPU progress on an extra
  drawable. Measure the actual outcome; fallback is not proof against contention.
- Phone comparison comes later, beginning at 2× and comparing 3× and lower/adaptive
  resolution. Consistent 120 means coherent distinct motion and regular pacing,
  not merely 100–120 average presentations. Existing acceptance targets include
  ≥117 presentations/s, p95 spacing ≤10 ms, speed ≥0.98 and 25 continuous seconds;
  longer sustained/thermal acceptance remains a separate step.

Camera-only reprojection does not advance the rider, opponents or particles. Chase
camera proximity does not establish that 60 Hz rider motion is acceptable: spins,
grabs and obstacle encounters are the important quality cases. Disoccluded scenery
cannot be recovered from one image. Transparent effects may have inappropriate
background depth. Prediction avoids waiting for a future real frame but does not
prove zero added end-to-end latency; queues and presentation timing still matter.

## Long-term options

| Option | Role |
| --- | --- |
| 60 Hz simulation + camera/depth reprojection | First bounded experiment; preserve original handling. |
| Reproject scenery and separately redraw rider/board/opponents | Possible later response to dynamic-object artifacts; requires ownership and composition work. |
| 60 Hz simulation + retained host render state + 120 real renders | Preferred long-term faithful-smoothness direction if effort is justified: avoid repeated guest traversal and interpolate presentation transforms. |
| MetalFX frame interpolation | Unmeasured alternative using two frames, depth, motion and UI inputs; requires a later frame and a latency/scheduling comparison. Color-only prototype failure does not rule it out. |
| 120 Hz simulation + 60 Hz rendering + reprojection | Later timestep/scheduling research, not a demonstrated budget fit. |
| Full 120 Hz simulation/rendering | Largest behavioral and performance scope; remains research rather than a prerequisite for restoration. |

The hybrid arithmetic `2 × 3.3 + 7.8 = 14.4 ms` is only an average CPU budget. The
update and render callbacks share a thread; an 11.1 ms update+render interval does
not yield evenly spaced updates every 8.33 ms. The input producer must acquire fresh
input at 120 Hz; two updates may otherwise consume the same sample. Even ideal
polling changes reduce average polling wait from 8.3 to 4.2 ms, not necessarily
halve total input-to-display latency.

The discovered render elapsed-time calculation is `update_count / 60`. Two half-dt
updates would report `2/60` unless that bookkeeping changes. It is a useful seam,
not evidence that animation automatically advances correctly. Physics, collision,
trick windows, camera filters, animation, particles, AI and UI timers need their own
time-normalized validation. A true half-step camera also cannot restore disoccluded
pixels or independently moving objects. Do not begin this physics conversion in the
same batch as the capture proof.

## Prior evidence

Phone measurements: `performance-review-2026-09-13.md`,
`local/reports/mobile/20260913-231157/`. Native callback/timestep seams:
`120hz-native-path.md`, `../archive/ssx3-120hz-handoff-2026-09-13.md`.
Earlier alternatives: `120hz-analysis.md`, `120hz-native-interpolation.md`,
`120hz-host-replay.md`, and the local `spike/120hz` worktree.
