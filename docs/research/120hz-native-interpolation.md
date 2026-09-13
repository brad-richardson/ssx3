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
| Render starts with real-time debt guard (original, 2 ms tolerance) | 59.20 | 59.20 | 0.988 |
| Render starts with corrected rolling-minimum guard | 87.36 | 58.12 | 0.970 |

The aggressive variant made more extra draws but slowed gameplay severely.
The original debt guard stopped issuing extras when execution fell behind; there
were zero extras in its measured window. That was not a successful protection:
it vetoed every opportunity. On the phone, both user trials on September 13
logged 520 vetoes, zero requests and a performance-limit exit after exactly
three seconds, so the displayed rate stayed at 60.

**Guard correction.** The original check required elapsed guest time to be
within 2 ms of elapsed wall time since the trial started. At the scheduling
seam the guest is normally behind by up to a frame: its virtual clock advances
with executed cycles while the host spent real time running them, and the idle
skip to the next retrace has not happened yet. The corrected `RealTimeBudget`
compares the current host debt against the lowest debt seen over a rolling
half-second window and allows an extra draw only within one 120 Hz period of
that minimum. A steady throttle offset passes; debt that keeps growing blocks
further extras. In the corrected Mac run (window 145–170 s) the guard still
vetoed 1,033 opportunities while allowing 731 extra draws, all of which
completed with zero changes in the watched rider, application, camera and RNG
windows; the course check passed. Guest time ran at 0.970 of host time in that
window, so the allowed slack costs about 3% of real-time speed on this Mac.
This is still a Mac measurement of the guest re-entry mechanism, not a phone
result or a display-rate claim.

**Phone trial with the corrected guard (September 13, 13:28).** One extra draw
completed, 186 opportunities were vetoed, and the performance limit ended the
trial after three seconds. The guard was right. Between consecutive completed
ordinary frames the guest clock advanced 16.7 ms while the wall clock advanced
22.8 ms (median), and application updates ran at 44 per second instead of 60.
The Mac shows the same shape at 17–20 ms per frame. The cost is the trial's
own rendering path: on every ordinary frame it re-uploads the interpolated
palettes through immediate XF commands, a median of 1,725 blended, 481
camera-only and 711 texture matrices per frame on the phone (1,300/208/370 on
the Mac), each as 13–14 host-side FIFO writes. The phone cannot absorb that,
so no budget remains for extra draws. Caching the wall clock instead of reading
it on every native dispatch (`RefreshNow`) did not change the cadence in a
second Mac run (`guard2-run`: 70.0 renders/s, 0.959 guest/host, 17.2 ms median
frame wall time inside the window), so the per-dispatch probe is not the
dominant cost. Retained host-side palettes, priority 1 below, are the
prerequisite for any phone result; tuning the guard further is not.

A second contributor is now known: the scheduler's cooperative yield calls
`CoreTiming::Idle()`, which skips at most one 20,000-cycle slice (about 41 us)
per burst exit. Idle-loop skipping through the same path costs about 30% of
real-time speed on the Mac (see `native/research.md`), so the trial's frame
cadence is not attributable to matrix uploads alone. The SDK cache-range
calls and the system-call vector are now handled by the core (same document),
which removes about one million hook calls and 27,000 exceptions per second
from every frame.

**Phone build policy, review follow-up (September 13):** the temporary unguarded
trial was followed by a speed-floor experiment. Review found that counting 32
idle-seam visits did not measure half a second: those visits can happen in a
fraction of a millisecond. The corrected policy samples at most 50 times per
second, requires at least 0.5 seconds of elapsed history, blocks extras below
0.98 guest seconds per host second and resumes only at 0.995. Clock rewinds,
frequency changes and long observation gaps clear history. It is a reactive
guard, not a guarantee that every future draw fits a deadline.

After three seconds, the whole trial exits if fewer than 15 extras completed
or the measured speed falls below 0.95. This also removes the overhead and
visual delay of ordinary interpolated frames when extras are not useful.
The 35-second maximum and pause/background cancellation remain. Screenshots from the first variant show a
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
the quiescent transition, and requests a second trial. A compile-time test-only
override permits the first extra draw, so an overloaded host cannot silently
skip the cancellation test. The second uses the unchanged app policy. Run that player for 230 seconds
with only `SSX_NATIVE_PROBE` set; the phone path supplies its own policy flags.
The builder regression test checks that this driver is actually included and
dispatched. The runner requires ordered request/cancel/quiescent/restart/
quiescent/complete events and a completed extra draw with unchanged watched
state; missing events fail even if ordinary gameplay succeeds. The driver also
has an independent watchdog. This checks the native control path, not UIKit backgrounding
or actual on-device checkpoint reload.

The corrected-guard run is `guard-run` with trace `guard-events.jsonl` and
player `guard-player` in the same directory.

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
