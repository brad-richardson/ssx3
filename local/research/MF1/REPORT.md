# MF1 REPORT — MetalFX frame-interpolation spike, session 1 (GameCube track)

Tables + receipts, no verdicts. Time box: 6 h. Evidence dir: `local/research/MF1/`
(STANDALONE). Isolated harness only: no tracked file modified (`git status`
clean apart from new `local/research/MF1/` paths, added with `git add -f`);
vendor sources, production player, and phone settings untouched; no lease of
any kind; no PS2 boots; PS2Recomp fork untouched.

Docs read first (per brief): `docs/research/120hz-reprojection.md` (all of it),
`docs/plan-120fps-2026-09-17.md` (layering), `docs/research/120hz-pacing-acceptance.md`
(bars). Prior art respected: the color-only block matcher (10.4 ms GPU + 4.9 FPS)
was not repeated; the offline warp precedent (footprint splat, HUD alpha solved)
is cited as the motion-derivation starting point below.

## 1. Device table (first-hour reachability)

Both Apple devices were reachable over WiFi (localNetwork/tcp tunnel, paired)
in the first hour. No stall occurred; all three targets produced numbers.

| Device | Identity | OS | Link | Trial-harness state | MF1 result |
| --- | --- | --- | --- | --- | --- |
| iPhone 16 Pro Max (iPhone17,2, A18 Pro) | `00008140-0002505001F3001C` | iOS 27.0 (24A437) | WiFi, paired | SSX Native 0.1 (1) installed, untouched | `supportsFrameInterp=true`; 3 configs measured |
| iPad Air 11" (M2, iPad14,9) | `00008112-001224302184A01E` | iPadOS 27.0 (24A437) | WiFi, paired | SSX Native 0.1 (1) installed, untouched | `supportsFrameInterp=true`; 3 configs measured |
| Mac (Apple M4) | host | macOS 27.0 (26A428), Xcode 27.0 (27A266a), MacOSX27.0.sdk | local | n/a | `supportsDevice=1`, `supportsMetal4FX=1`; full matrix |

Receipts: `receipts/iphone-details.json`, `receipts/ipad-details.json`
(devicectl details JSON), `runs-ios/iphone/MF1/mf1-result.json`,
`runs-ios/ipad/MF1/mf1-result.json`.

Device notes (tabled, no settings changed):

- One transient launch failure on the iPhone (`FBSOpenApplicationErrorDomain
  error 7 ... device ... Locked`); the immediate retry launched. No phone
  setting was viewed or changed.
- First iOS probe build crashed at startup (`EXC_BREAKPOINT` in
  `___UIApplicationEvaluateRuntimeIssueForNoSceneLifecycleAdoption_block_invoke`;
  receipt `receipts/mf1probe-crash1.ips`). Fix: adopted the scene lifecycle
  (`UISceneDelegate` + `UIApplicationSceneManifest` in `ios/Info.plist`) and
  set the minimum OS to 27.0 (both devices are 27.0; the harness sets the
  27.0-only `contentWidth/Height`).
- iOS signing: local Apple Development identity `295EFB42...`, wildcard
  development profile `iOS Team Provisioning Profile: *`
  (`f0793278-...`, team `LQ3V7772Q2`, `get-task-allow=true`, both device
  UDIDs listed). Fresh bundle id `com.bradrichardson.mf1probe` — the SSX
  trial app was never re-signed, replaced, or launched.
- No queued-for-user iPhone run: the device ran in-session.

## 2. Input table (capture path vs MetalFX descriptor needs)

MetalFX entry used: `MTLFXFrameInterpolatorDescriptor` /
`MTLFXFrameInterpolator` (Metal 3 API) with `input == output` (no scaling),
`scaler = nil`.

| # | MetalFX input | Descriptor need (this session) | Capture path emits (`tools/gamecube_reprojection.py` + `native/diagnostics/reprojection_capture.h`) | Match / gap |
| --- | --- | --- | --- | --- |
| 1 | color | `BGRA8Unorm` or `RGBA16Float` (both constructed + interpolated; see matrix) | EFB world color + final color, `RGBA8`/`BGRA8` raw at EFB res (precedent: 1920x1584 EFB, 1920x1344 active XFB at 3x) | MATCH (format-compatible; BGRA8 path measured end to end) |
| 2 | depth | `Depth32Float`, `depthReversed` YES/NO | `D32F` resolved and dumped as `R32F` raw float; per-frame `reversed_depth` backend flag + `efb_pixel_format` (precedent: 0 = `RGB8_Z24`) recorded in metadata | MATCH with conversion tabled (R32F file to Depth32Float texture upload not built; `depthReversed=YES` used in harness, `NO` + inverted values probed identically) |
| 3 | motion | `RG16Float` per-pixel vectors pointing to the pixel's location in `prevColorTexture`, times (`motionVectorScaleX/Y`); scale 1.0 = pixel units | NOTHING — the GX path emits no motion vectors | GAP (open input per brief). Session-1 fallback tabled below |
| 4 | UI (optional) | `BGRA8Unorm` texture + `uiTextureComposited` flag | Paired-background alpha layer, offline-exact (all 8 precedent frames reconstruct within 2 levels, 99.99% within 1; 7.04% coverage) | MATCH offline (live draw routing still open). Harness measured the separate-UI path: HUD MAE 0.0 |
| 5 | camera | `nearPlane`, `farPlane`, `fieldOfView`, `aspectRatio`, `jitterOffsetX/Y`, `deltaTime` | Per-frame GPU-consumed camera candidate (slot 0), perspective projection, viewport, scissor offsets, pixel-center correction, vertex-depth-range flag | MATCH unvalidated (values exist; mapping GX projection to near/far/fov not checked; harness used near=0.1, far=100, fov=60, aspect=W/H, jitter=0, dt=1/60) |

Motion-fallback table (session-1 rule: exact synthetic motion; estimated/uniform
where the API demands it, tabled exactly):

| Motion source | Definition in harness | Quality effect (720p, BGRA8) | Status |
| --- | --- | --- | --- |
| exact | rect pixels `(-32,0)` px (32 px A-to-B travel), background/HUD `(0,0)` | interior MAE 0.0 (bit-exact), band 2.3, static 0.0 | measured on all 3 devices |
| zero | all `(0,0)` | interior MAE 95.7 (Mac) / 89.4 (iPhone/iPad): moving region not interpolated | measured (Mac + iPhone + iPad) |
| uniform | all `(-4,0)` px (global mean-ish flow) | interior MAE 93.4: moving region not interpolated | measured (Mac) |

Session-2 motion starting point (precedent, not built): the offline warp tool
already computes per-pixel displacement from camera + depth
(`tools/gamecube_reprojection_warp.py`: `warp()` returns per-pixel `motion`;
`predict_view()` half-step pose). That is a camera-only motion-vector source;
rider, objects, particles, transparency have no independent vectors there either.

## 3. Integration table (does MetalFX run in the harness?)

Yes — on all three targets, in an isolated harness, with two drive-pattern
findings that cost the middle of the session (both tabled with probe receipts).

### 3a. Harness shape (files added; player untouched proof)

All new files live under `local/research/MF1/` (standalone evidence dir).
`tools/`, `native/`, `third_party/`, the production player, and phone settings
were not modified; no emulator or player build was run. Proof: `git status
--short` shows no modified tracked file (only the new `local/research/MF1/`
paths, committed with `git add -f`).

| Path | Role |
| --- | --- |
| `harness/mf1_scene.h` | shared synthetic scene: BGRA8 frames (32 px checker bg, striped translating rect, HUD strip), R32F depth (0.1 far / 0.9 near, reversed), RG16F motion, BGRA8<->RGBA16F conversion, timing/RSS helpers |
| `harness/mf1_interp.m` | macOS CLI: fresh-instance quality encode + fresh-instance 30-iter timing loop; JSON to stdout, raw frames to `--out` |
| `harness/mf1_probe.m` | macOS CLI: per-encode-output experiment matrix (`--exp`) that established the drive pattern |
| `analyze.py` | offline metrics (MAE per region + A/B baselines), PNGs, 4x diff, contact sheet |
| `run-matrix.sh` | macOS build + 8-config matrix + analysis driver |
| `ios/mf1_ios_probe.m` | headless UIKit probe (scene lifecycle): 3 configs, results to `Documents/MF1/`, writes `DONE`, exits |
| `ios/Info.plist` | bundle `com.bradrichardson.mf1probe`, min OS 27.0, scene manifest, `arm64`+`metal` caps |
| `ios/run-ios.sh` | compile + wildcard-profile sign + `devicectl` install/launch/poll/pull driver |
| `runs/res*/` | 8 macOS matrix runs (raw frames, `run.json`, `metrics.json`, PNGs) + stability repeats (`stab-*`, `*-r2`) |
| `runs-ios/iphone/`, `runs-ios/ipad/` | device pulls + per-config analysis dirs |
| `probes/` | 10 drive-pattern experiments with per-encode outputs |
| `receipts/` | device details JSON, crash report, crash-log pull dir |

### 3b. MetalFX version/entry used

| Item | Value |
| --- | --- |
| API | `MTLFXFrameInterpolator` (Metal 3 protocol) from MacOSX27.0.sdk / iPhoneOS27.0.sdk |
| Support check | `+[MTLFXFrameInterpolatorDescriptor supportsDevice:]` = YES on Apple M4, Apple A18 Pro GPU, Apple M2 GPU |
| Descriptor | color/output `BGRA8Unorm` (primary) or `RGBA16Float` (one arm); depth `Depth32Float`; motion `RG16Float`; UI `BGRA8Unorm`; input == output; `scaler` = nil |
| Texture usage (queried) | color 1 (`ShaderRead`), output 4 (`RenderTarget`), depth/motion/UI 1 |
| Storage | color/depth/motion/UI `Shared` (CPU-filled, incl. shared Depth32Float — works on M4 macOS AND on A18 Pro / M2 iOS); output `Private` + blit to shared staging for readback |
| Camera params | near 0.1, far 100, fov 60 deg, aspect W/H, jitter 0, dt 1/60, `depthReversed` YES, `motionVectorScale` 1.0, `contentWidth/Height` = W/H |

### 3c. Drive-pattern findings (probe receipts in `probes/`)

| # | Experiment | Observation |
| --- | --- | --- |
| 1 | `bgra-prime`: e0 (A,nil,RESET), e1 (B,A,NO) | OUT0 == A, OUT1 == B, both bit-exact passthrough. A reset-prime breaks the following encode |
| 2 | `bgra-noreset`: e0 (A,A,NO), e1 (B,A,NO) (+2 warmup encodes before) | OUT1 vs GT MAE 0.19 — first true interpolation. (Warmup masked finding 4) |
| 3 | `bgra-steady`: (A,A),(B,A),(C,B),(D,C), no reset | OUT1/2/3 vs respective middle-GT MAE 0.19/0.21/0.22 — steady state engages and holds |
| 4 | fresh-instance quality in `mf1_interp` (2 encodes, no warmup) | 2nd-encode OUT is passthrough (interior 98.3). A fresh instance needs TWO history-establishing encodes; interpolation engages on the 3rd encode. Quality OUT is therefore the 3rd encode |
| 5 | `bgra-recover`, `bgra-recover8`: reset mid-stream | reset encode = bit-exact passthrough (0.14 ms); the next TWO non-reset encodes also pass through bit-exact; interpolation resumes on the 3rd post-reset encode (repeated-pair resumed MAE 2.02 vs fresh-pair 0.2 — history-pollution or repeated-pair artifact, open) |
| 6 | `rgba16-prime` / `rgba16-noreset` | same reset/no-reset behavior in RGBA16Float; color format does not change engagement |
| 7 | `bgra-ndcmot` (motion/scale in NDC halves), `bgra-norev` (`depthReversed=NO` + inverted values) | both with reset-prime: passthrough, same as `bgra-prime`. Not re-tested without reset (open, low priority) |

Working rule used for all reported numbers: never set `shouldResetHistory`;
per fresh instance, run 2 establishing encodes, then interpolation outputs
`interp(prev, color)` from the 3rd encode on.

### 3d. First successful interpolated frame

`probes/bgra-noreset/OUT1.rgba`: 640x360 BGRA8, Mac Apple M4, OUT1 vs GT
MAE 0.19 (interior/band/static in `probes/` analysis notes). First
matrix-quality frame: `runs/res720-exact-none/OUT.rgba` (1280x720, interior
bit-exact). First device frame: `runs-ios/iphone/MF1/ios528-exact-OUT.rgba`
(640x528, A18 Pro, bit-identical to the Mac output — see section 4).

## 4. First numbers (quality? cost? latency?)

Scene (all configs): 32 px-checker gradient background (static, depth far),
striped rect translating +32 px/frame A-to-B (depth near), optional static HUD
strip (top 8%). Ground truth = re-rendered middle (rect at +16). Regions:
`static` (never covered by the rect in A/B/GT, excl. HUD), `interior` (GT rect
eroded 4 px), `band` (within 4 px of the GT rect edge, outside it), `hud` (top
8% rows), `all`. Errors in 0–255 channel units. Baselines `A`/`B` = repeating
frame A/B instead of interpolating.

### 4a. Quality table (interpolated vs real-next-frame diffs)

| Run | Device | OUT vs GT: all / static / interior / band / hud | A vs GT all | B vs GT all |
| --- | --- | --- | --- | --- |
| `res720-exact-none` | Mac M4 | 0.29 / 0.00 / 0.00 / 2.31 / 0.00 | 12.63 | 12.62 |
| `res720-exact-comp` (HUD in color) | Mac M4 | 0.29 / 0.00 / 0.00 / 2.37 / 0.00 | 12.63 | 12.62 |
| `res720-exact-sep` (separate UI texture) | Mac M4 | 0.29 / 0.00 / 0.00 / 2.31 / 0.00 | 22.39* | 22.39* |
| `res720-exact-none-16f` (RGBA16Float) | Mac M4 | 0.32 / 0.03 / 0.04 / 2.40 / 0.03 | 12.63 | 12.62 |
| `res720-zero-none` | Mac M4 | 12.22 / 0.00 / 95.66 / 3.54 / 0.00 | 12.63 | 12.62 |
| `res720-uniform-none` | Mac M4 | 12.03 / 0.23 / 93.41 / 3.79 / 0.18 | 12.63 | 12.62 |
| `res528-exact-none` (640x528 = phone internal) | Mac M4 | 0.19 / 0.02 / 0.00 / 1.36 / 0.00 | 12.76 | 12.76 |
| `res1080-exact-none` | Mac M4 | 0.04 / 0.01 / 0.00 / 0.73 / 0.00 | 12.58 | 12.58 |
| `ios528-exact` | iPhone A18 Pro | 0.19 / 0.02 / 0.00 / 1.36 / 0.00 | 12.76 | 12.76 |
| `ios528-zero` | iPhone A18 Pro | 11.44 / 0.00 / 89.43 / 3.89 / 0.00 | 12.76 | 12.76 |
| `ios720-exact` | iPhone A18 Pro | 0.29 / 0.00 / 0.00 / 2.31 / 0.00 | 12.63 | 12.62 |
| `ios528-exact` | iPad M2 | 0.19 / 0.02 / 0.00 / 1.36 / 0.00 | 12.76 | 12.76 |
| `ios528-zero` | iPad M2 | 11.44 / 0.00 / 89.43 / 3.89 / 0.00 | 12.76 | 12.76 |
| `ios720-exact` | iPad M2 | 0.29 / 0.00 / 0.00 / 2.31 / 0.00 | 12.63 | 12.62 |

`*` separate-UI baselines compare color-only A/B against the UI-composited GT;
the OUT row uses the same composited GT, so the OUT-vs-baseline gap is the
like-for-like read.

Quality notes (tabled, per region):

- With exact motion, the moving-rect interior is bit-exact (MAE 0.00) at all
  three resolutions on all three devices; residual error sits in the 4 px
  motion-boundary band (0.7–2.4) and near-zero elsewhere. Static-wall MAE
  precedent comparison: the warp report's static walls scored warped-RGB MAE
  1.12/2.60 on real captures; this session's `static` region (0.00–0.03) is a
  synthetic flat/gradient background, NOT comparable — listed for scale only.
- With zero or uniform motion, the moving region is not interpolated
  (interior 89–96, vs the ~98 no-interp baseline): at 32 px/frame the
  interpolator does not recover the motion on its own. Motion-boundary notes:
  band error stays low (3.5–3.9) because the band is mostly background.
- HUD/alpha regions separated: static HUD strip reproduces exactly (0.00) both
  composited-in-color and via the separate `uiTexture` path (against a
  UI-composited GT for the latter).
- Cross-device determinism: `OUT.rgba` bytes are IDENTICAL across Mac M4,
  iPhone A18 Pro, and iPad M2 for the exact-motion configs at 640x528 and
  1280x720 (byte-compared with numpy; receipt command in section 6).
  Zero-motion outputs differ slightly by platform family (Mac interior 95.66
  vs iPhone/iPad 89.43).
- Contact sheets + 4x diffs: `runs/res*/contact.png`, `runs/res*/diff4x.png`,
  `runs-ios/*/ios*/contact.png`. Full per-region max/%>4 + pixel counts:
  `runs/*/metrics.json`, `runs-ios/*/*/metrics.json`.

### 4b. Cost table (GPU ms per interpolated frame)

Timing = `commandBuffer.GPUEndTime - GPUStartTime` per steady-state (B,A)
encode (5th+ encode on a warmed instance, repeated-pair history), 30 iters,
plus host `submit` (encode + commit, no wait) and process RSS delta. Phone
numbers are on-device GPU times from the headless probe (no presentation).

| Run | Device | GPU med / p95 / min / max (ms) | wall med (ms) | submit med (ms) | RSS delta |
| --- | --- | --- | --- | --- | --- |
| `res720-exact-none` | Mac M4 | 3.47 / 4.40 / 3.05 / 4.57 | 3.92 | 0.046 | 27.3 MB |
| `res720-exact-none` R2 (repeat) | Mac M4 | 3.48 / 4.62 / 3.17 / 5.36 | 3.82 | 0.037 | 27.3 MB |
| `stab-none` interleaved x3 (15 iters) | Mac M4 | 3.59 / 4.79; 2.61 / 3.37; 2.64 / 3.07 | — | — | — |
| `stab-composited` interleaved x3 (15 iters) | Mac M4 | 3.56 / 4.57; 2.65 / 3.05; 2.55 / 3.06 | — | — | — |
| `res720-exact-comp` (matrix) | Mac M4 | 2.53 / 3.00 / 2.50 / 3.07 | 2.93 | 0.055 | 27.3 MB |
| `res720-exact-sep` (matrix) | Mac M4 | 2.53 / 3.04 / 2.46 / 3.16 | 2.93 | 0.026 | 27.3 MB |
| `res720-zero-none` | Mac M4 | 3.26 / 4.46 / 2.95 / 4.77 | 3.64 | 0.049 | 27.3 MB |
| `res720-uniform-none` | Mac M4 | 2.92 / 4.08 / 2.49 / 4.13 | 3.29 | 0.052 | 27.3 MB |
| `res720-exact-none-16f` | Mac M4 | 2.54 / 3.05 / 2.49 / 3.07 | 2.89 | 0.053 | 41.9 MB |
| `res528-exact-none` | Mac M4 | 2.21 / 7.35 / 1.39 / 8.23 | 2.64 | 0.048 | 15.5 MB |
| `res528-exact-none` R2 (repeat) | Mac M4 | 1.29 / 1.79 / 1.19 / 1.88 | 1.65 | 0.043 | 15.4 MB |
| `res1080-exact-none` | Mac M4 | 5.34 / 6.18 / 5.31 / 6.20 | 5.72 | 0.053 | 50.5 MB |
| `ios528-exact` | iPhone A18 Pro | 2.20 / 3.58 / 1.69 / 3.84 | 2.39 | n/a (device) | n/a |
| `ios528-zero` | iPhone A18 Pro | 1.42 / 1.57 / 1.31 / 1.58 | 1.66 | n/a | n/a |
| `ios720-exact` | iPhone A18 Pro | 3.41 / 3.54 / 3.31 / 3.55 | 3.67 | n/a | n/a |
| `ios528-exact` | iPad M2 | 2.96 / 5.00 / 2.47 / 5.40 | 3.47 | n/a | n/a |
| `ios528-zero` | iPad M2 | 2.48 / 2.51 / 2.15 / 2.76 | 3.03 | n/a | n/a |
| `ios720-exact` | iPad M2 | 4.42 / 6.29 / 4.36 / 6.31 | 5.01 | n/a | n/a |

Baselines to beat/table (comparability stated, not claimed):

| Baseline | Value | Comparable? |
| --- | --- | --- |
| color-only block matcher (failed) | 10.4 ms GPU at 1556x966 + blocking path at 4.9 FPS | Same order of scene scale, different algorithm/GPU/scene. Listed for scale: all MF1 interpolation medians (1.3–5.9 ms) sit below 10.4 ms on their own hardware |
| 1–2 ms warp hope | unmeasured | Not comparable: NumPy-offline hope, never a GPU measurement. Nearest MF1 datum: 640x528 Mac R2 med 1.29 ms; iPhone 640x528 med 2.20 ms (exact) / 1.42 ms (zero) |
| extra-draw bursts ~117 displays/s | 8–16 s windows, no sustained pass | Not comparable: presentation-path bursts, not interpolation cost |

Cost notes:

- Run-to-run drift dominates small config deltas on the Mac: the 720p matrix
  showed 3.47 (`none`) vs 2.53 (`comp`/`sep`), but an interleaved none/comp
  repeat (`runs/stab-*`, 3x15 iters, receipted `run.json`) shows no separation
  (interleaved pairs 3.59/3.56, 2.61/2.65, 2.64/2.55) and a downward drift
  across the six runs (GPU warm-up/clock). Repeat R2 reproduces R1 (3.48 vs
  3.47). The 640x528 matrix p95/max (7.35/8.23) is a one-off spike; R2 is
  tight (1.79/1.88).
- Zero-motion encodes are consistently CHEAPER than exact-motion on all three
  GPUs (iPhone 1.42 vs 2.20; iPad 2.48 vs 2.96; Mac 3.26 vs 3.47): cost is
  content/motion-dependent, not fixed.
- Host CPU submit overhead on Mac: 0.02–0.06 ms per encode (encode + commit,
  no wait). Device submit overhead not measured (no host-side counter in the
  probe; wall-minus-GPU on device is 0.2–0.6 ms including wait).
- Memory delta (Mac process RSS, before-alloc to after-run, includes host
  frame buffers + MetalFX internals + two interpolator instances): 15 MB
  (640x528), 27 MB (1280x720 BGRA8), 42 MB (1280x720 RGBA16F), 51 MB
  (1920x1080). Per-instance MetalFX-internal delta not isolated.

### 4c. Latency table (end-to-end added latency)

No presentation runs in session 1 (headless harness/probe); GPU terms measured,
structural terms bounded, composite/present terms unmeasured.

| Component | Value | How known |
| --- | --- | --- |
| later-frame wait (frame N+1 must exist before mid(N,N+1) can emit) | 16.67 ms at 60 Hz guest | structural bound (one guest frame interval); measured wall not taken |
| interpolation GPU (640x528, phone internal res) | iPhone med 2.20 / p95 3.58; iPad med 2.96 / p95 5.00; Mac med 1.29–2.21 | measured (this session) |
| interpolation GPU (1280x720) | iPhone med 3.41 / p95 3.54; iPad med 4.42 / p95 6.29; Mac med 2.5–3.9 band | measured (this session) |
| HUD composite over interpolated background | unmeasured | no composite in harness (separate-UI path verified for correctness only, hud MAE 0.0) |
| extra drawable acquire + present + pacing | unmeasured | no presentation scheduler in session 1 |
| history warmup (2 establishing encodes per instance; 2 passthrough encodes after a reset) | 2–3 frame intervals of non-interpolated output at start / after reset | measured behaviorally (probes 4–5); wall-time cost equals the frames' own intervals |

Budget frame (from `120hz-pacing-acceptance.md`, no pass/fail read):

| Budget | Value | MF1 terms against it |
| --- | --- | --- |
| aggregate 16.67 ms (one real + one synthetic share it: real render + capture + warp + HUD) | 16.67 ms | interpolation GPU 1.3–4.4 ms (device/res-dependent) fits inside the aggregate alongside the real-frame terms; the later-frame wait is ADDITIVE latency, not aggregate GPU work |
| presentation deadlines 8.33 ms | 8.33 ms per present | interpolation GPU medians (max 4.42 ms iPad 720p) sit below one 8.33 ms slot; p95s (max 6.31 ms) also below; scheduling/queue effects unmeasured |

## 5. Exact commands / builds

All from `/Users/bradrichardson/dev/ssx3/local/research/MF1/` with
`export COPYFILE_DISABLE=1`, unless noted.

```sh
# macOS harness build + full matrix (8 configs) + analysis
clang -fobjc-arc -framework Metal -framework MetalFX -framework Foundation \
  -o harness/mf1_interp harness/mf1_interp.m
sh run-matrix.sh
python3 analyze.py runs/res*

# drive-pattern probes (10 experiments)
clang -fobjc-arc -framework Metal -framework MetalFX -framework Foundation \
  -o harness/mf1_probe harness/mf1_probe.m
for e in bgra-prime bgra-noreset bgra-seq rgba16-prime rgba16-seq bgra-ndcmot \
         bgra-norev bgra-steady bgra-recover bgra-recover8; do
  ./harness/mf1_probe --out probes/$e --exp $e
done

# stability repeats
./harness/mf1_interp --out runs/res720-exact-none-r2 --width 1280 --height 720 \
  --iters 30 --motion exact --ui none
./harness/mf1_interp --out runs/res528-exact-none-r2 --width 640 --height 528 \
  --iters 30 --motion exact --ui none
# interleaved none/comp x3 (15 iters) -> runs/stab-*

# iOS probe: build + wildcard-profile sign + install + launch + pull
sh ios/run-ios.sh "Brad’s iPhone" ../runs-ios/iphone
sh ios/run-ios.sh "Brad’s iPad" ../runs-ios/ipad

# cross-device byte-equality receipt
python3 -c "
import numpy as np
a = np.fromfile('runs/res720-exact-none/OUT.rgba', dtype=np.uint8)
b = np.fromfile('runs-ios/iphone/ios720-exact/OUT.rgba', dtype=np.uint8)
c = np.fromfile('runs-ios/ipad/ios720-exact/OUT.rgba', dtype=np.uint8)
print('mac==iphone:', bool((a == b).all()), 'mac==ipad:', bool((a == c).all()))"
# -> mac==iphone: True mac==ipad: True
```

Device install receipt: bundle `com.bradrichardson.mf1probe`, signed with
`295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1`, wildcard profile
`f0793278-...`; install + launch via `devicectl` (see `ios/run-ios.sh`);
results pulled from `Documents/MF1` via `device copy from --domain-type
appDataContainer`.

## 6. Gaps / session-2 needs

| # | Gap | Session-1 state |
| --- | --- | --- |
| 1 | motion vectors from the GX path | open input; session 1 used exact synthetic motion. Starting point: warp-tool per-pixel displacement from camera + depth (camera-only; object motion open). Zero/uniform fallbacks measured as non-viable at 32 px/frame |
| 2 | sustained pass | not attempted: isolated encodes only (30 iters each, no 25 s continuous window, no thermal soak) |
| 3 | HUD composite + presentation scheduler cost | unmeasured (correctness of the separate-UI path only) |
| 4 | reset/recovery with fresh pairs | recovery length measured with repeated pairs (2 passthroughs, resume on 3rd); fresh-pair recovery length + resumed quality open |
| 5 | NDC motion scale + non-reversed depth without reset | probed only with reset-prime (passthrough); retest open, low priority |
| 6 | live-path warmup handling | 2 establishing encodes per instance produce non-interpolated output; startup behavior for a live path not designed |
| 7 | min-OS question | harness sets 27.0-only `contentWidth/Height` and targets 27.0; whether 26.x works (and what the content-region default does there) open |
| 8 | real-capture inputs | synthetic scene only; `local/research/120hz/` captures absent in this checkout (tooling present, data not run). Reprojection-batch capture + MetalFX on real frames open |
| 9 | device CPU submit + memory counters | host submit measured on Mac only (0.02–0.06 ms); no device-side CPU/memory counters |
| 10 | near/far/fov mapping from GX projection | harness used nominal values; mapping from captured GX projection/viewport unvalidated |

What I could not do: phone numbers beyond the headless probe (no on-screen
presentation, no EGL/drawable timing — out of scope for the isolated
harness); `local/research/120hz/` reuse was tooling-only (no capture data in
the checkout, no fresh capture run — no emulator run was made this session).

## 7. TAIL RECEIPT

Report written in 4 chunks (sections 1–2, 3, 4, 5–7) plus a stab-numbers
correction with receipted reruns. Pre-receipt measure of sections 1–6:
340 lines, sha256 `bfcafbb6833397136a18d7351285120c60210270432a8bf97b998640cf04e4c1`.
Tail content line: "the checkout, no fresh capture run — no emulator run was
made this session)." This receipt line ends the report. END-MF1-REPORT.
