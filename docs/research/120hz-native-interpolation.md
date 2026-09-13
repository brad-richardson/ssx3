# Native pose interpolation prototype — September 13, 2026

Continue investigating native rendering, with an optional phone trial. This
prototype establishes an authored transform-history path, but its immediate
matrix uploads are too expensive to recommend as the default renderer. It does
not establish 120 displayed frames per second or lower input latency.

## What is implemented

The pinned GXBE69 adapter identifies model instances before their bone palettes
are submitted. It records previous/current affine matrices, then interpolates
the camera, model palettes and their paired lighting/texture matrices. Static
scene batches receive a camera correction; camera-centred backgrounds receive
rotation only. The HUD's ordinary screen-space matrix is excluded.

The output is sent through immediate XF commands, without modifying the game's
authoritative poses or matrix RAM. Original simulation updates, clocks, input,
interrupts and collision logic continue. Extra draws use the existing
[independent schedule](120hz-independent-schedule.md) and host immediate-XFB
ownership arrangement. Missed deadlines are dropped.

This uses previous-to-current poses for **all** participating frames in the
trial. Ordinary draws start near the previous pose and extras advance toward
the current pose. Showing a current pose and then an earlier midpoint would
move backward in time. The consistent history approach costs approximately one
simulation frame of visual age; it is not a latency improvement.

## Identity and lifecycle findings

Palette slots, double-buffer addresses, render packets, and global skeleton
scratch buffers are all reused. None is sufficient as an actor identity.
The validated body/shadow callers preserve a model-instance pointer with its
own bone arrays. The key combines that instance, weighted bone descriptor,
pass type and matrix kind. It is independent of palette allocation order.
The instance's two input matrix arrays are multiplied during rendering; their
existence does not mean the game already exposes previous/current time samples.
The first ownership capture mapped 16,129 of 18,865 position loads to the two
model draw paths; the remaining loads included camera, background and static
batches. Those counts are diagnostic coverage, not percentages of visible
pixels or complete animation coverage.

History rejects ambiguous keys, missing generations, non-finite matrices,
large transform changes and camera teleports. It is bounded to 8,192 keys.
Affine interpolation also handles the game's already weighted skinning
matrices; it does not reconstruct the original animation curves or perform
quaternion interpolation. CPU-generated particles, moving vertices and every
special effect have not been recovered.

Pausing during an injected draw needs special handling. The host saves a return
context which is absent from guest savestates. The frontend cancels the trial,
allows the CPU to reach its normal idle seam, then pauses and saves. A background
task covers that short drain. The saved single-XFB alias can persist; its mode
is normalized on restore. Full Reset clears the adapter, history and report
file before starting a new runtime. Headers, frontend, Info.plist and injection
recipe are included in checkpoint compatibility identity.

The portable history and time-budget policies can be reused on Android. The
executable-specific owner adapter is shared by courses using this pinned game
revision. Android presentation pacing still needs its own platform integration;
this work does not implement it.

## Measured limitations

These are bounded Mac runs, using native-resolution Metal output. The measured
window is host seconds 145–170. Course trajectories and motion-state coverage
vary, so these are diagnostic observations rather than a controlled speedup
comparison. The guarded run also overlapped part of an iPhone link build.

| Variant | Complete draws/s | Updates/s | Guest seconds / host second |
| --- | ---: | ---: | ---: |
| Immediate matrix interpolation, conservative schedule | 61.56 | 59.28 | 0.989 |
| Spacing from render starts, broader motion states | 63.56 | 38.52 | 0.642 |
| Render starts with real-time debt guard | 59.20 | 59.20 | 0.988 |

The aggressive variant made more extra draws but slowed gameplay severely.
The debt guard stopped issuing extras when execution fell behind; there were
zero extras in its measured window. This is a successful protection, not a
successful high-refresh result. Screenshots from the first variant show a
coherent rider, board, shadow, terrain and HUD. Scoped extra-draw comparisons
reported no changes in watched rider, application, camera and RNG windows in
these runs. That is not a whole-game purity or determinism proof.

No valid device display timestamps or input-latency measurement were collected.
Matrix interpolation counts include unchanged transforms and must not be
reported as distinct displayed frames.

## Phone trial

The menu offers **Try smoothing (up to 35 seconds)**. It starts during riding,
ends when opening the menu or entering the background, and returns to normal
within 35 seconds. If fewer than 15 extras complete in its first three seconds,
it ends early and reports the performance limit. The default remains ordinary
rendering. A `CADisplayLink` requests the available high refresh range while
the trial is running, and Info.plist enables that request on iPhone. Apple's
[ProMotion documentation](https://developer.apple.com/documentation/quartzcore/optimizing-iphone-and-ipad-apps-to-support-promotion-displays)
explicitly treats this as a hint, not a guaranteed display rate.

The iOS build compiles one locally generated copy of the runtime dispatch
source with the authored hook. It leaves the pinned upstream checkout and
generated game module unchanged. Raw traces, captures, generated sources,
executables, signing information and assets remain ignored under `local/`.

## Next priorities

1. Preserve indexed matrix uploads and supply retained host pose palettes to
   the graphics backend. The current immediate-command approach expands FIFO
   traffic and repeats transform processing. Any replacement must associate
   immutable palette snapshots with GPU execution order, not a mutable global
   CPU-frame flag.
2. Unify ordinary and extra presentation deadlines, preserving simulation
   priority and a strict queue bound. Measure actual drawable presentation and
   input-to-photon timing on both mobile platforms.
3. Improve rotation interpolation and cover dynamic vertex effects, shadows
   and camera transitions with repeatable visual comparisons across courses.
   Keep exact current poses as a safe fallback wherever ownership is unknown.

## Local reproduction

Use fresh profiles and output names. The normal course checker retains the DOL
pin and native fault checks. For the guarded desktop experiment:

```sh
python3 tools/gamecube_native_trace.py build \
  --game local/game/gc-gari-027 --scheduler --interpolation \
  --output local/research/120hz/interpolation-new-player

SSX_NATIVE_PROBE="$PWD/local/research/120hz/interpolation-new.jsonl" \
SSX_NATIVE_SCHEDULE=1 SSX_NATIVE_COMPLETION_RELEASE=1 \
SSX_NATIVE_SKIP_BOOKKEEPING=1 SSX_NATIVE_START_SPACING=1 \
SSX_NATIVE_REALTIME_GUARD=1 \
python3 tools/gamecube_schedule_check.py \
  --player-dir local/research/120hz/interpolation-new-player \
  --immediate-xfb --resolution 640x528 --game local/game/gc-gari-027 \
  --profile interpolation-new --output local/research/120hz/interpolation-new-run \
  --seconds 190
```

Add `--app-trial-check` to the builder to compile the phone control path with a
desktop driver. It requests a trial, cancels during an injected render, verifies
the idle transition, and requests a second trial. The first trial grants time
credit until one extra draw is reached, so an overloaded host cannot silently
skip the cancellation test. The second uses the unchanged app policy. Run that player for 230 seconds
with only `SSX_NATIVE_PROBE` set; the phone path supplies its own policy flags.
The driver reports quiescent transitions and fails if the lifecycle sequence
does not finish. This checks the native control path, not UIKit backgrounding
or actual on-device checkpoint reload.

The completed `lifecycle` run passed its 230-second course check. Cancellation
during an injected draw at 141.312 seconds reached the idle seam at 141.325;
the second trial started at 147.022 and returned through the performance guard
at 150.022. The one forced extra left all watched state windows unchanged.
Its trace SHA-256 is
`f9d6dd22748104be3a03373f8a81aa2352b0d5007e38ebee70a627417e4edb07`.
All 198 captured palette allocations also satisfy the final adapter bounds.
The focused history, scheduling, runtime, mobile and session checks total 41
passing tests. On-device trial execution remains unverified.

Evidence is under `local/research/120hz/interpolation/`. The `blend`,
`start-spacing`, and `budget` traces have SHA-256 values respectively:

- `efe0ccd939ca46761d1d1749111a6b7b7ee0ce328b97e0ef33eceb1cfc38bb9c`
- `ddd9ef3ea9b97aedae7809cafc73923087a9353b59355dcd29cd15562d58f0c1`
- `0a5d1615495f9ec67be5ac5df5821e90149a0b7575b9337e0b13a599d37101c6`
