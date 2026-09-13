# Review follow-up: load protection and overhead

September 13, 2026. First delivery after the implementation review. The phone
candidate retains the original simulation and the opt-in 35-second guest-render
trial. Host FIFO replay remains a separate research prototype.

## Changes

- The speed floor now measures at least 0.5 seconds of wall/guest history,
  samples at most 50 Hz, and uses 0.98/0.995 stop/resume hysteresis. Hundreds
  of idle-slice visits cannot evict the elapsed-time window. Invalid clocks,
  rewinds and long gaps restart warm-up. Trace rows include window duration
  and measured speed.
- The full trial exits after three seconds when extras are not useful or
  simulation falls below 0.95 speed. Guarding extras alone could leave the
  costly ordinary interpolated path active indefinitely.
- The desktop lifecycle driver is back under the interpolation build branch.
  The checker now requires explicit lifecycle events and an actual unchanged
  extra draw; a healthy ordinary run cannot substitute for the test.
- The interpolation adapter skips unrelated native dispatches before guest
  reads, runtime lookups or atomics. Queue-after observation moved to callback
  completion, removing a guest-memory read from every render dispatch.
- The course checker exposes `--metal-validation on|off`, defaulting to on.
  The native runner exposes `SSX3_DISPATCH_SAMPLES=0` for measuring sampling
  overhead and records both choices in run receipts.

## Bounded performance spike

`tools/gamecube_perf_spike.py` runs five sequential, fresh-profile cases:
original probe, filtered probe, filtered probe without Metal validation, and
the latter without dispatch sampling, followed by `RushFramePresentation`.
That final case changes host throttling placement between presents without
changing guest clock frequency. It is a desktop research knob, not enabled
in the first phone delivery. All use the same DOL/module/course,
native resolution, immediate XFB and speed-floor policy. Each case retains
native fault, code verification and course-state checks. Measurements use
host seconds 145–170 and reject changed watched state on extras.

All five cases passed their course/runtime checks and reported zero changes
in the watched extra-draw state windows:

| Case | Complete renders/s | Guest/host speed | Median ordinary callback ms | Extras in 25 s |
| --- | ---: | ---: | ---: | ---: |
| Original probe | 59.00 | 0.957 | 11.86 | 40 |
| Filtered probe | 59.80 | 0.963 | 10.41 | 53 |
| Metal validation off | 60.00 | 0.956 | 6.27 | 68 |
| Dispatch sampling also off | 60.00 | 0.958 | 8.92 | 65 |
| RushFramePresentation also on | 60.00 | 0.955 | 8.69 | 69 |

The filter removes unnecessary work and reduced the observed ordinary callback
median in this comparison. The large callback-time variation across settings
did not produce a meaningful game-speed improvement. Do not interpret those
medians as isolated CPU work or claim a precise speedup: they include waits,
and trajectories and rendering loads differ. These results do not justify a
new phone configuration. Keep the validated filter/load protection and pursue
the host replay correctness and timing gates next.

The desktop comparison intentionally leaves interpolation active for the full
35-second research window. The phone control path exits early when extras are
not useful; its final lifecycle check demonstrates that fallback. The table
therefore does not describe how long the phone build remains in a slow trial.

These are host-timed rides, not deterministic trajectory-matched replays.
They cannot establish an exact speedup, actual 120 Hz presentation, phone
performance or input latency. Metal validation is a desktop diagnostic cost;
the iPhone app did not force it on.

The audited defaults already disable emulated CPU data-cache accuracy and
CPU EFB reads, retain EFB copies as textures, and use native render scale.
The runtime builds with Release optimization; generated game code uses O2.
CPU/GPU threading, guest clocks, instruction verification and JIT policy are
left intact. Previously failed idle-skipping configurations are not enabled.
LTO, generated-code O3, shader strategies and asynchronous renderer ownership
need their own experiments rather than being bundled into this comparison.

## First phone delivery

Build `2250d8d9`, built at 20:27:46 UTC, was signed with the existing development
profile and installed on the paired iPhone 16 Pro Max. Course assets remain
gc-gari-027. A changed app identity invalidates old quick-resume snapshots;
memory-card saves are preserved. The user's subsequent manual trials are
recorded below.

All 194 unit tests pass. The final 230-second Mac lifecycle check completed
six extra draws with no changes in the watched state windows. Cancellation
at 140.026 s reached quiescence at 140.038 s. The second trial started at
147.000 s and stopped through the performance fallback at 150.025 s. Gameplay
continued afterward and the course/runtime checks passed. Captures show
coherent riding after the trial. This does not test UIKit backgrounding or
on-device snapshot reload.

Local receipts: `local/research/120hz/review-delivery.json`,
`review-lifecycle-final-run/`, and `review-perf-spike/`. The final lifecycle
trace SHA-256 is
`12461c5167e3f786bae86d6c7834b36c72b3a4b3b336bb354c8cec8bf85d94d1`.

## Phone trials after delivery

Collected September 13 at 21:05 UTC. Session `1789333174.053` started at
20:59:34 UTC on the iPhone 16 Pro Max. The checkpoint manifest identifies
build `2250d8d9` and references the third successful save UUID in this session's
runtime log. The two trial windows come from their own `start` and
`restore_mode` events; older reports from previous builds are excluded.

| Trial | Duration | Completed extras | Complete renders/s | Guest/host speed | Stop reason |
| --- | ---: | ---: | ---: | ---: | --- |
| First | 16.568 s | 732 | 104.06 | 0.999 | Speed guard |
| Second | 5.160 s | 115 | 80.62 | 0.985 | Speed guard |

All 847 extra callbacks completed without retries or changes in the watched
rider/view identity, state, position, RNG, body/app/view windows. All have
interpolation rows with blended matrices. This remains bounded observation,
not proof that every guest-visible side effect is absent.

The first trial contains a seven-second interval (native wall 172–179 s)
with 837 completed renders: 119.57/s at 1.003 guest/host speed. Independent
one-second app metrics also report about 120 frame events/s during the first
trial. Their selected six-sample window has a 12.12 ms worst per-window p95
frame interval, so the average alone does not establish uniform 8.33 ms
pacing. Neither counter measures actual Metal presentation or proves distinct
visible frames. No fresh screenshot or screen recording accompanies this run.

Both trials restored the original submission mode after the performance
guard fired, in 0.614 ms and 21.574 ms respectively. The second ends after
a 50.9 ms ordinary render callback. Nearby app metrics contain a brief dip
to 0.679 and 0.823 speed, with audio DMA starvation counter increases, before
recovering to about 60 frame events/s and normal speed. The logs do not
establish whether that dip is caused by rendering, loading, or another stall.
Metric seconds exclude app pauses while native wall time includes them;
their timestamps must not be equated. Post-trial metrics 200–212 s show a
59.995 FPS median, 1.001 speed median and no additional DMA starvation.
Thermal state stays nominal throughout the collected metrics.

The log contains four pauses, three resumes, three successful checkpoint
commits and one failed final save. The checkpoint manifest still references
the third successful save. Snapshot bytes and relaunch restore were not
tested. Existing logging cannot distinguish a missing-file timeout from
a checkpoint validation/hash/manifest failure; diagnose this before closing
phone lifecycle acceptance. Both smoothing trials ended by load protection,
so these reports also do not establish cancellation during an active extra.

No invalid memory accesses, GPU command errors, unknown guest instructions
or forbidden executable allocations were reported. This live session has
no final shutdown counters. Evidence and file hashes are preserved in
`local/research/120hz/review-phone-trials.json`.

This is useful evidence of phone rendering headroom in some sections. Next
measurement work should add actual drawable presentation timing, a common
clock/build identity to app reports, and specific checkpoint failure reasons.
Retain the speed guard and experimental scope while addressing those gaps;
the host replay correctness gate below remains required for that prototype.

The user reported a small slowdown and audio blip followed shortly by the
trial ending. That is consistent with the logged speed/audio dip; the original
report's separate clocks cannot establish the exact cancellation latency.

## Diagnostic follow-up build

Build `c2e098d3` adds the measurement work above: actual Metal presented-time
callbacks on the phone, buffered acquire/submit/final-command-buffer GPU events,
common uptime anchors, explicit checkpoint stages/errors and lifecycle timing.
Existing Dolphin workload and recomp/fallback/HLE counters are sampled at
their owning thread boundaries. It retains the same speed guard and graphics
configuration. Detailed report fields and analysis commands are in the
[iOS diagnostic notes](../../native/ios/README.md).

All 199 unit tests pass, including delayed Metal callbacks across reset,
bounded trace overflow, missing timestamps, selection by presentation time
despite late callbacks, and preservation of the prior snapshot after a failed
manifest write. The diagnostic build does not claim to fix the final phone
save failure: its next reproduction should identify the failing stage.

The signed build was installed on the iPhone 16 Pro Max at 21:36 UTC, with
matching executable checksum after installation. A 170-second simulator run
completed with riding visible in the captures, populated workload/recomp/GPU
events, zero dropped trace events and no reported GPU command errors or invalid
guest accesses. The simulator SDK explicitly lacks presentation timestamps;
its audio backend also emitted queue-full warnings, so this is functional
telemetry evidence rather than phone-performance or audio acceptance. The
final phone build additionally guards a nonfinite optional max-speed estimate.
Receipts are in `local/research/120hz/phone-diagnostic-delivery.json`.

## Phone presentation confirmed

The user completed six trials on `c2e098d3` and reported that the brief smoothing
sections felt good. Session `1789335561.641`, collected at 21:44 UTC on September
13, provides positive Metal `presentedTime` evidence of high-refresh screen
delivery. The signed app contains `CADisableMinimumFrameDurationOnPhone=true`;
the trial's display link requests a 60–120 Hz range with 120 preferred on this
phone. These settings were already enabled, so no flag change is required.
Apple documents the flag as the opt-in for frame rates above the system default
([property-list reference](https://developer.apple.com/documentation/bundleresources/information-property-list/cadisableminimumframedurationonphone)).

| Trial | Duration | Actual displays/s | Guest/host speed | Completed extras |
| --- | ---: | ---: | ---: | ---: |
| 1 | 13.723 s | 103.47 | 0.997 | 603 |
| 2 | 3.862 s | 77.67 | 0.990 | 74 |
| 3 | 4.375 s | 90.29 | 0.992 | 137 |
| 4 | 3.099 s | 85.83 | 0.997 | 84 |
| 5 | 10.780 s | 105.85 | 0.998 | 499 |
| 6 | 3.572 s | 98.55 | 0.995 | 142 |

In trial 5, host seconds 41925.465949–41929.465949 contain 479 positive
presentation timestamps in four seconds: **119.75 displayed frames/s**.
Median and p95 display spacing are both 8.334 ms, with one 16.668 ms interval.
There are no duplicate positive timestamps or dropped trace events. A later
16-second ordinary-rendering window contains exactly 960 displayed frames
(60/s) at 16.668 ms median spacing. This establishes delivery above 60 Hz,
including a short near-120 FPS section. It does not yet establish sustained
120 FPS, distinct interpolated motion in every frame, or input latency.

All six trials ended through load protection. Submission mode restoration
followed the cutoff by 0.5–12.5 ms. All 1,539 extra draws preserved the watched
state windows. Eight checkpoint attempts completed successfully in 97–137 ms;
the earlier save failure did not recur. The session includes background/audio
transitions and resume, but no cancellation during an active trial or relaunch
restore. Thermal state remained nominal. No GPU command errors or trace
overflow were reported; 19 display callbacks across the whole session had
zero presentation timestamps and remain unknown.

The sampled trial windows contain no new vertex/pixel shader creations.
Final command buffer medians range from 1.88 to 2.53 ms, and drawable waits
are generally small, rising in the section near 120 FPS. These values do not
include all GPU work or isolate CPU cost. The next performance investigation
should focus on sustained rendering/pacing and account for drawable waiting;
the evidence does not support a missing ProMotion opt-in as the current limit.
Full event hashes and summaries: `local/research/120hz/phone-diagnostic-trial-results.json`.

## Next gate for host replay

Before live or on-phone replay: apply memory updates at their recorded FIFO
positions, preserve all guest-visible state and completion events, restore
the recorded starting state for each replay, and compare against the exact
original frame. Identical repeated screenshots do not establish original-frame
fidelity. Then measure full capture/copy/decode/GPU/present cost and advance to
consecutive-frame camera/rider interpolation with culling and cut tests.
