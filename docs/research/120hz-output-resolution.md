# Output size, internal detail and callback CPU timing

These are separate controls. Full/Half output changes the final Metal drawable;
1×/2× internal detail changes Dolphin's EFB resolution. Normal launches use
Full output at 1×. Each choice survives Full Reset during that app process.

| Control on iPhone 16 Pro Max | Dimensions | Pixel count relative to its baseline |
| --- | --- | ---: |
| Full output | 2868 × 1320 | 1 |
| Half output | 1434 × 660 | 0.25 |
| 1× internal detail | 640 × 528 | 1 |
| 2× internal detail | 1280 × 1056 | 4 |

UIKit text and controls retain their normal screen resolution. Resizing is
allowed only after a trial drains and the paused checkpoint finishes. Both
changes synchronize with the CPU/FIFO guard; Dolphin performs the resulting
GPU allocation on its renderer thread. The internal-scale change uses the
existing configuration path, including viewport/scissor updates. Reports keep
requested scale separate from actual renderer-sampled EFB size and sample time.

The default pacing gate remains an explicit 1×, Full/Half output comparison.
It rejects mixed dimensions and does not qualify 2× observations under that
policy. Higher internal detail needs its own ordinary-play and smoothing checks.
The runtime supports integer internal scales; this control exposes only 1 and 2.

## Phone run on build 1747c62a

Collected September 13 from session `1789338548.428`. The user changed output
Full → Half → Full. Actual Metal submits include **421 at 1434 × 660** and
16,265 at 2868 × 1320. All 280 sampled internal sizes remain 640 × 528.
Both changes completed, and all five checkpoint saves succeeded. These are
on-device checks of the output control, including resume after resizing.

Both smoothing trials occurred after the return to Full output, so this run
does not establish a Full/Half smoothing comparison.

| Full-output trial | Duration | Actual displays/s | Complete extras | Extra wall median | Extra thread-CPU median |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 3.005 s | 74.87 | 52 | 8.638 ms | 8.453 ms |
| 2 | 3.007 s | 57.53 | 3 | 11.858 ms | 11.789 ms |

All 55 extra callbacks preserved the watched state. Both trials ended through
load protection and restored ordinary rendering. The first cutoff recorded a
0.941 speed window; the second had only three extras after three seconds.
Neither is sustained-120 evidence. Thermal state was nominal. Audio counter
snapshots strictly inside each entire trial increased by three; the counter
does not identify an exact audible instant or its cause. There were no Metal
trace drops, duplicate positive presentation times, GPU errors or incomplete
records. Nine session display callbacks have zero timestamps and remain unknown.

The median paired wall-minus-CPU difference is 0.039 ms in trial 1 and 0.030 ms
in trial 2. The second has only three extra samples. This points to active
callback-thread work in these sections; that includes guest code, software
vertex/renderer work and nested diagnostics. It does not identify a particular
function or establish that every course section has the same bottleneck.
The current Emit's own formatting/flush is outside the callback time measurement.

Raw evidence: `local/reports/mobile/20260913-184102/Reports/1789338548.428`.
Analysis and hashes: `local/research/120hz/output-resolution-phone-pacing.json`
and `output-resolution-phone-results.json`. The delivery receipt is
`output-resolution-delivery.json` in the same research folder.

## Simulator checks and limits

The first three Simulator launches aborted in Apple's `AURemoteIO::Start`
with an RPC timeout before gameplay. Restarting the dedicated Simulator did
not resolve it. The phone's audio startup and the backend source were unchanged.
An explicit `--simulator-null-audio` option now selects Dolphin's Null backend
only for a bounded automated Simulator session. It records disabled audio;
it cannot be enabled on the phone. This does not fix or validate Simulator audio.

Build `f06f7a6b` completed separate 200-second Full/Half graphics checks with
this option. They submitted the expected output sizes, retained 640 × 528 EFB,
showed coherent riding in captures and stopped cleanly with no guest invalid
accesses, GPU errors, unknown instructions or JIT fallback runs. Compiler and
collision workloads ran concurrently: these are functional checks only.
They do not establish phone performance, audio quality or equal trajectories.

Evidence: `local/research/120hz/output-full-null-simulator-check/` and
`output-half-null-simulator-check/`.

Build `971dc928` completed a separate 200-second launch at 2× with Full output
and Null audio. All measured EFB sizes were 1280 × 1056; output stayed
2868 × 1320. It stopped cleanly, with zero invalid accesses, GPU errors, unknown
instructions, code-verification failures or JIT fallback runs. All 1,900
completed extra draws preserved every watched field. The last capture
shows coherent riding at 23% course progress. Evidence is in
`local/research/120hz/internal-2x-null-simulator-check/`. This establishes the
launch configuration and graphics path on Simulator, not phone performance.

The signed `971dc928` build was installed on the iPhone September 13 at 19:10 EDT;
course assets remain 027. Device validation still needs ordinary play at 2×,
the menu's 1× → 2× → 1× transitions, and checkpoint/relaunch behavior across
detail changes. The installed build and evidence paths are recorded in
`local/research/120hz/internal-resolution-delivery.json`. The integrated Python
suite passed all 245 tests before installation.
