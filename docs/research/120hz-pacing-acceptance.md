# Phone pacing and drawable-resolution acceptance

`tools/mobile_pacing_check.py` separates two questions: whether a bounded trial
preserved the watched guest state and restored ordinary rendering, and whether
it supplied enough continuous evidence to qualify for the 120 Hz pacing target.
A functional pass is deliberately narrower than proof that all guest state is
unchanged. A short high-refresh burst never passes the sustained target.

## Measurement policy

The script uses native `schedule/start` through `schedule/restore_mode` to pair
trials. `performance_limit` records the cutoff; it does not end the trial before
an in-flight extra render returns. The whole native trial is checked for watched
state changes, including the tail excluded from performance measurement.

Each steady window excludes the first **2 seconds** and last **0.5 seconds**.
Qualification requires **25 continuous seconds** after those exclusions, fitting
within the existing 35-second trial cap. A short guarded exit remains useful
diagnostic evidence but receives `inconclusive` for sustained acceptance, with
the actual duration, cutoff and observed target misses retained. A 25-second
pass is bounded evidence; it is not a long-session thermal guarantee. The script
neither changes the guard nor recommends keeping a slowed trial running longer.

These are explicit research acceptance thresholds, not claims about a perceptual
boundary:

| Measurement | Qualification threshold |
| --- | --- |
| Actual presentations | At least 117 per second |
| Median spacing | At most 8.6 ms |
| p95 spacing | At most 10 ms |
| p99 spacing | At most 17 ms |
| Game speed | At least 0.98x in complete metric intervals and native timebase span |
| Audio starvation | No increase across snapshots bracketing the full window; boundary-only increases are unknown |
| Thermal state | Nominal or fair, never serious or critical |
| Internal framebuffer | Measured consistently at 640 × 528 |
| Drawable | One consistent positive size in actual Metal submits |

The source of displayed FPS is positive Metal `presentedTime`, selected by the
presentation timestamp even when the callback arrives after the window. Request,
render completion, submit and video-event counters are not substituted for it.
Median/p95/p99 come from adjacent positive presentation times in that window;
they are not averages of one-second percentiles. Presented frames need not
contain distinct interpolated motion. Input latency is not measured.

All streams use `host_seconds`, with native wall time aligned by the measured
schedule anchors. More than 10 ms of anchor drift makes the result inconclusive.
App active seconds exclude pauses and cannot be used to align these streams.
Metric rows cover preceding intervals: only intervals with both endpoints
inside the steady window and outside pauses contribute game-speed samples.
Audio deltas use the nearest snapshot at/before start and at/after end, each
within 1.5 seconds, and report that expanded observation span. They detect
counter resets. A positive delta only across a window boundary cannot be
assigned to an exact instant, so it is inconclusive rather than a clean zero.
An increase between snapshots entirely inside the window is a known target
miss. Missing runtime startup/module/interpreter evidence or null/wrong-typed
watched fields also prevents acceptance; shutdown counters are not required
from a live phone collection.

Missing/zero display times, duplicate positive timestamps, missing callbacks,
missing submit records, incomplete final records, and trace overflow are unknown
evidence. Overflow affects all windows because lost events cannot reliably be
located. Session-wide zero timestamps outside the selected window remain
reported, without invalidating an otherwise complete window. GPU duration
measures the final command buffer only; it does not represent all GPU work.

New native traces also carry nullable `cpu_duration_ms`, measured with the
callback thread's CPU clock at entry and completion. The analyzer reports it
beside callback wall time and their paired difference. CPU time includes
nested work and diagnostic hooks before record emission; it excludes work on
other threads and the GPU. Wall minus CPU includes both waiting and scheduler
descheduling, so it is not a named GPU-stall counter. Older traces and unavailable
clocks remain missing evidence, never zero CPU cost. This metric is diagnostic
and does not change the acceptance thresholds or smoothing guard.

The default rejects windows crossing pause, background or audio interruption
intervals. `--segment-pauses` measures each active segment separately, warming
each again; it never stitches short segments together to reach 25 seconds.
Output-scale changes and mixed actual drawable sizes also invalidate a steady
window. Native restoration must have been observed before acceptance.

## Run and compare

Analyze every recorded native trial in a collected session:

```sh
python3 tools/mobile_pacing_check.py local/reports/mobile/COLLECTION/Reports/SESSION \
  --output local/research/120hz/pacing-session.json
```

Compare a full-output trial and a half-output trial, including two trials from
the same session:

```sh
python3 tools/mobile_pacing_check.py FULL_SESSION --compare HALF_SESSION \
  --baseline-trial 1 --candidate-trial 2 \
  --output local/research/120hz/pacing-full-half.json
```

The comparison uses the shorter common warmed duration. It requires matching
build, disc, module ABI, assets, DOL, OS, device/GPU and core settings, measured
`outputScale` values of 1.0 and 0.5, and actual Metal submit sizes that differ by
two in both dimensions. Both must retain 640 × 528 internally. For the current
phone the expected drawable pair is 2868 × 1320 and 1434 × 660. The comparison
uses actual dimensions instead of trusting a requested resize event.

Manual routes are not matched workloads. The output labels differences as
observations and always sets `causal_speedup_established=false`. Use the same
phone and build, the same course/rider/camera/checkpoint, and alternating full /
half / full order; retain the input trace and captures. Start at a comparable
thermal state and record previous trial exposure. Repeat guarded attempts
without relaxing load protection. A deterministic route and matched initial
state would be needed to attribute a cost difference to resolution alone.

By default the command prints diagnostic evidence and exits successfully even
when acceptance is inconclusive. Add `--require-sustained` for a gate that exits
nonzero unless a trial has passed both bounded integrity and sustained pacing.
With `--compare`, that option requires a valid comparison and both selected
windows passing. This is stricter than merely observing a promising candidate.

## Existing phone evidence

Reanalysis of build `c2e098d3`, session `1789335561.641`, is recorded in
`local/research/120hz/pacing-c2e098d3.json`, with hashes of the raw input files.
All six trials pass the bounded watched-state/restoration check. None contains
25 continuous warmed seconds, so none qualifies as sustained 120 Hz.

| Trial | Entire native trial | Warmed span | Displayed FPS in warmed span | Audio delta across window bracket |
| --- | ---: | ---: | ---: | ---: |
| 1 | 13.723 s | 11.223 s | 105.67 | +3; at least +1 inside |
| 2 | 3.862 s | 1.362 s | 77.81 | +1; exact window attribution unknown |
| 3 | 4.375 s | 1.875 s | 90.67 | +1; exact window attribution unknown |
| 4 | 3.099 s | 0.599 s | 93.49 | +1; exact window attribution unknown |
| 5 | 10.780 s | 8.280 s | 109.18 | +1 |
| 6 | 3.572 s | 1.072 s | 101.69 | +1; exact window attribution unknown |

Trials 1 and 5 each have a known +1 audio delta between snapshots fully inside
their warmed windows. The expanded brackets also catch increases near other
trial boundaries; those cannot establish that an audible event occurred in
the exact selected window. These counters are consistent with the reported
brief audio disturbance but do not identify its cause. Thermal state remained
nominal. There are no trace drops or
incomplete records in this collection. Nineteen session display callbacks have
zero timestamps; none belongs to a submit in these warmed windows.

The earlier four-second 119.75 FPS section remains valid evidence of actual
high-refresh presentation. This fixed-window audit does not cherry-pick that
section or replace the shorter whole-trial results with it. New full/half output
comparisons still require new phone data with the resolution metadata.

Focused validation: `python3 -m unittest tests.test_mobile_pacing_check` covers
late callbacks, short bursts, guard/restoration boundaries, zero timestamps,
lost and incomplete trace evidence, pause segmentation, metric boundaries,
audio counter resets, clock drift, configuration mismatches and actual resize.
