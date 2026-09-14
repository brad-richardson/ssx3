# Output size, internal detail and callback CPU timing

These are separate controls. Full/75%/Match/Half output changes the final Metal drawable;
1×/2× internal detail changes Dolphin's EFB resolution. Delivered build
`113c9b20` starts at Full output and 1×. Each choice survives Full Reset during
that app process. Direct menu choices, remembered settings, and an initial
Half-output/2× default are requested follow-up work, currently in progress;
they are not part of the delivered build documented here.

| Control on iPhone 16 Pro Max | Dimensions | Pixel count relative to its baseline |
| --- | --- | ---: |
| Full output | 2868 × 1320 | 1 |
| 75% output | 2151 × 990 | 0.5625 |
| Match at 2× for the observed SSX picture | 1947 × 896 | ≈0.461 |
| Half output | 1434 × 660 | 0.25 |
| 1× internal detail | 640 × 528 | 1 |
| 2× internal detail | 1280 × 1056 | 4 |

UIKit text and controls retain their normal screen resolution. Manual changes
are allowed only after a trial drains and the paused checkpoint finishes. Both
changes synchronize with the CPU/FIFO guard; Dolphin performs the resulting
GPU allocation on its renderer thread. The internal-scale change uses the
existing configuration path, including viewport/scissor updates. Reports keep
requested scale separate from actual renderer-sampled EFB size and sample time.

The default pacing gate remains an explicit 1×, Full/Half output comparison.
`--internal-scale 2` selects a separate 1280 × 1056 EFB expectation; it retains
the same pacing, audio, speed, thermal and minimum-duration requirements.
Neither policy accepts mixed internal dimensions. Higher internal detail needs
its own ordinary-play and smoothing checks.
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

## Phone run on build 971dc928

Session `1789341970.715`, collected September 13 at 19:35, verifies on-phone
internal-detail transitions and includes the first measured Half-output
smoothing trials. The user reports Garibaldi first and Metro second, but the
exact course boundary is unrecorded. Do not assign individual trials to courses
or treat these rides as matched trajectories.

The following times are lifecycle `active_seconds`, which exclude pauses.
They mark configured/applied requests; subsequent renderer samples confirm the
EFB transition rather than relying on the stale dimensions present in the
configuration event itself.

| Active time | Change | Confirmed internal size | Output |
| ---: | --- | --- | --- |
| 0.883 s | 1× → 2× | 1280 × 1056 | Full |
| 159.113 s | 2× → 1× | 640 × 528 | Full |
| 213.955 s | 1× → 2× | 1280 × 1056 | Full |
| 288.687 s | Full → Half | 1280 × 1056 | 1434 × 660 |
| 347.505 s | Half → Full | 1280 × 1056 | 2868 × 1320 |
| 351.345 s | Full → Half | 1280 × 1056 | 1434 × 660 |

The session contains 291 measured 2× EFB snapshots and 54 at 1×. Actual Metal
submits include 17,670 Full and 4,994 Half drawables. All 16 checkpoint saves
committed. This establishes ordinary rendering and pause/resume after detail
and output changes in this process; checkpoint restoration across a fresh
launch after changing detail still needs a separate check.

Trial boundaries below use native `start` through `restore_mode`, aligned to
the shared host clock. Rates count positive Metal `presentedTime` values inside
each complete trial span, including warm-up. Each span also has one or two
submitted drawables whose presentation timestamp is zero; these remain unknown
and are not counted as displays.

| Trial | Internal / output | Duration | Positive displays/s | Complete extras | End trigger |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | 2× / Full | 3.041 s | 70.70 | 39 | Performance guard |
| 2 | 2× / Full | 4.103 s | 74.34 | 67 | Performance guard |
| 3 | 1× / Full | 4.279 s | 78.52 | 85 | Performance guard |
| 4 | 1× / Full | 6.869 s | 88.23 | 199 | Performance guard |
| 5 | 2× / Full | 3.541 s | 75.97 | 61 | Performance guard |
| 6 | 2× / Full | 3.250 s | 75.39 | 53 | Cancel for pause |
| 7 | 2× / Half | 8.917 s | 102.94 | 386 | Performance guard |
| 8 | 2× / Half | 18.382 s | 112.67 | 972 | Performance guard |

All eight native trials restored ordinary rendering. Trial 6 records an
explicit cancellation for pause followed by drain/restoration, providing one
phone check of that path. There is **no Half-output 1× smoothing measurement**.
The higher rates in the later Half/2× trials are promising observations, but
different courses/trajectories prevent attributing the difference to output size.

With the explicit 2× policy, trial 8's warmed window lasts **15.882 seconds**
and records **114.34 positive displays/s**, median/p95 spacing 8.334/8.334 ms
and p99 16.668 ms. Its complete speed intervals stay at or above 0.9844x,
audio starvation remains unchanged across close bracketing snapshots, and
thermal state is nominal. This still misses the 117 displays/s and 25-second
continuous warmed requirements. Trial 7's warmed rate is 107.52 over 6.417 s.
Do not extend the 35-second guard or lower its speed floor to obtain acceptance.

Trial 8's extra draw has a 5.699 ms wall median and 5.443 ms callback-thread
CPU median. Its final Metal command buffer has a 3.995 ms GPU median, while
drawable acquisition takes only 0.012 ms. Full/2× trials show roughly 5.2 ms
for that final GPU buffer; Full/1× trials show 1.8–2.0 ms. These are unmatched
sections and the GPU timer covers only the final command buffer. CPU and GPU
work overlap, so do not add their times. The active callback CPU cost makes
leaf-function profiling the next priority alongside matched-route output tests.

The strict report remains unaccepted. Seven bounded watched-state/restoration
checks pass; trial 7 retains a **failed legacy integrity verdict** because
three extra callbacks changed offsets `[632, 640, 644, 924, 928]` in the
1,024-byte app watch. Body, rider identity/state/position, RNG and view were
unchanged. The changes occurred at native wall times 342.188963, 342.225414
and 342.261592; the same pattern also appears in ordinary renders nearby.

Static audit of the pinned DOL shows GameModule requests only 540 bytes:
`0x8010ebb4` loads that size before allocator `0x801ccb88`, and constructor
`0x801073ac` installs vtable `0x802e543c`. Thus the changed offsets are beyond
the known GameModule extent. **Applying that ownership interpretation to this
older trace is an inference**: it contains no before/after app-vtable or word
value provenance. The neighboring owner and writer remain unknown. The next
diagnostic adds those values and separate owned/adjacent labels while preserving
the entire raw span and existing verdicts; it does not whitelist these changes.

Four adjacent lifecycle records have backwards timestamps in delivery order,
with a maximum reversal of 0.0784 ms. Asynchronous delivery may explain them,
but the strict gate keeps this evidence unknown rather than sorting it away.
Native/Metal anchor spread is only 0.0000015 s. There are no Metal trace drops
or incomplete records; 33 zero presentation timestamps across the session
remain unknown. Warmed trial windows contain no zero-timestamp submits. Audio
boundary ambiguity, sparse samples and trial 6's interruption remain explicit
in the per-window report. Trials 3–4 additionally mismatch the explicit 2×
EFB expectation. Trial 7 stays failed; the other sustained verdicts are
inconclusive. No sustained 120 Hz, distinct-motion or causal speedup claim is made.

Reproduction:

```sh
python3 tools/mobile_pacing_check.py PHONE_SESSION --internal-scale 2 \
  --require-sustained --output local/research/120hz/internal-resolution-phone-2x-policy.json
```

This report exits 1 as expected. Raw evidence is
`local/reports/mobile/20260913-193545/Reports/1789341970.715`. The unchanged
`internal-resolution-phone-baseline-policy.json`, new `internal-resolution-phone-2x-policy.json`
and descriptive `internal-resolution-phone-results.json` are under
`local/research/120hz/`, with logs, source/evidence hashes and exact windows.

## 75% and Match internal output

The pause-menu action cycles Full → 75% → Match internal → Half → Full.
75% requests 2151 × 990 on this phone, or 56.25% of Full output's pixels.
Match uses Dolphin's post-present, aspect-correct source suggestion and expands
its surface around the picture with bars to retain the screen's aspect ratio.
For the measured 2× picture, 1556 × 896 fits inside **1947 × 896** output.
The 1280 × 1056 EFB allocation includes unused image area; copying its height
would not establish one-to-one image scaling. iOS still scales the drawable to
the panel, and Dolphin's horizontal pixel-aspect correction remains necessary.

Automatic Match updates use the CPU/FIFO guard during ordinary running or a
fully paused/drained state. They do not resize during waiting/active trials,
checkpoints, start/stop or lifecycle transitions. An internal-detail change
waits for fresh source measurements with matching EFB dimensions and two
consistent unique presents. Missing XFBs invalidate the source suggestion;
there is no extrapolation from a stale framebuffer sample. The menu reports
an adjustment pending until actual output matches. Sizes beyond native output
are capped and labeled in telemetry.

The iOS Metal backend now uses the host's explicit integer drawable dimensions.
Previously it recomputed them through a float content scale: the desired
1947 × 896 would become 1946 × 895. Desktop surface sizing is unchanged.

Simulator build `113c9b20` completed the state-anchored Match/2× ride, including
a 22.412-second smoothing trial and restoration through the existing load
guard. All 181 metrics report EFB 1280 × 1056, drawable 1947 × 896 and both
source picture and target rectangle 1556 × 896. Metal confirms 12,253 submits
at the matched size after four initial Full-size startup submits. No resize
occurs during the trial. All 1,233 completed extras preserve the watched state;
every new app ownership sample identifies the 540-byte GameModule extent.
No trace drops, GPU errors, invalid accesses, code-verification failures or
JIT fallback runs occurred, and the runtime stopped cleanly. Captures show
coherent riding. These Null-audio Simulator observations verify graphics and
startup behavior; they do not establish phone audio or sustained performance.

Evidence: `local/research/120hz/active-title-match-simulator-check/`, including
raw reports, captures, source hashes, `validation.json` and strict `pacing.json`.
The full integrated Python suite passes all 262 tests. Phone delivery is recorded below; menu/1× ↔ 2× Match transitions still need
on-device validation.

## Phone Match/2× run on build 113c9b20

Session `1789345362.689`, collected September 13 at 20:29, was **Garibaldi
only**, according to the user. Fast start worked well and the picture looked
fine; smoothing did not hold. The phone reached the real main menu at
**20.614526 seconds after guest execution began**, excluding runtime creation
and asset verification. All ten checkpoint saves committed.

Metal records 10,306 submits at **1947 × 896**. In 164 Match samples, both the
aspect-corrected source picture and visible target rectangle are **1556 × 896**;
the internal EFB is **1280 × 1056**. These describe different stages of the
same image. The screenshot's confusing dimension labels did not demonstrate
a sizing failure. Label output, visible picture and internal detail separately;
iOS compositor scaling to the physical panel still applies.

All three trials used Match output and 2× detail. Rates below count positive
Metal `presentedTime` values over native start-to-restoration spans, including
warm-up; they are not callback rates.

| Trial | Duration | Positive displays/s | Complete extras | Extra CPU / wall median |
| --- | ---: | ---: | ---: | ---: |
| 1 | 3.493 s | 73.86 | 55 | 9.112 / 9.155 ms |
| 2 | 4.879 s | 94.28 | 172 | 6.045 / 6.076 ms |
| 3 | 13.546 s | 78.18 | 267 | 4.728 / 4.861 ms |

All **494 extra callbacks** preserve the complete watched fields, including
the original raw app span. The new vtable diagnostic validates the 540-byte
GameModule extent in every extra; no owned or adjacent app changes occur.
This does not clear the older session's three unresolved alerts. All three
trials hit the existing speed guard and restored ordinary rendering.

Thermal state remains nominal. Trial 1's audio-starvation counter rises by
five between snapshots strictly inside the trial. Trial 2's inside snapshots
show zero increase, but its enclosing bracket rises by one; the event's exact
time is unknown. Trial 3 also has zero inside-snapshot increase without a valid
full-trial bracket. These zeros do not prove uninterrupted audio throughout
either trial. There are no Metal trace drops; 20 session presentation timestamps
are zero, and lifecycle delivery-order clock reversals remain unknown.
All sustained verdicts are inconclusive, with warmed windows at most 11.046 s
and rates below target. No sustained-120 or causal output-speedup claim follows.

Raw evidence: `local/reports/mobile/20260913-202904/Reports/1789345362.689`.
The source/evidence hashes, descriptive results and explicit 2× pacing report
are in `local/research/120hz/match-startup-phone-user-results.json` and
`match-startup-phone-user-pacing.json`. Remaining checks include remembered
settings across relaunch, menu Match transitions at both detail levels, and
matched-route output comparisons.

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
course assets remain 027. The later phone run above verifies ordinary 2× play
and detail transitions in-process; checkpoint/relaunch behavior across detail
changes remains open. The installed build and evidence paths are recorded in
`local/research/120hz/internal-resolution-delivery.json`. The integrated Python
suite passed all 245 tests before installation.

## Delivery on September 13 at 20:22 EDT

Signed build `113c9b20` is installed on Brad’s iPhone. Course assets remain
027. Fast cold start is enabled by default, including Full Reset; normal boot
remains a menu preference and explicit launch override. Output still starts
at Full/1× independently of the startup preference.

Three fresh Simulator launches of this final build reached the real main menu
in 20.492, 20.530 and 20.467 seconds after guest execution began. The latter two
used the default startup behavior with no override. The 75%/2× check confirms
2151 × 990 output. Match/1× confirms 973 × 448 output with a 778 × 448 source and
target picture. The earlier Match/2× ride supplies the smoothing check above.
All three stopped cleanly with no runtime/graphics faults or JIT fallback runs.
They used Null audio. The later phone run above confirms startup and Match/2×
dimensions; menu transitions, audio continuity and sustained pacing remain
separate acceptance checks.

Delivery, archived build/signing receipts, signed executable hash, installation
receipt, validation hashes and remaining checks are indexed in
`local/research/120hz/match-startup-delivery.json`. The additional default-start
checks are in `active-title-default-repeat1-check/` and
`active-title-default-repeat2-check/` under the same research directory.


## Direct pause-menu choices and saved defaults

The direct menu replaces cycling actions with Half / 75% / Full / Match output
and 1× / 2× detail selections. Both stay in the paused panel, with Resume and
Try smoothing always visible. Initial settings are Half output + 2× detail,
chosen by the user after the earlier phone comparison. Successful manual
changes persist independently across launches and Full Reset; command-line
choices override only the current process, including explicit Full and 1×.

The resolution text distinguishes the measured visible image from total output
including bars. A paused detail change displays “updates on resume” until a
fresh render supplies dimensions. A requested trial resumes first, then waits
for a stable source at the selected detail after both configuration and surface
resize. This applies to every output mode. Match also requires its exact target
surface size before requesting a trial. Another pause cancels the pending
request. Existing trial duration, speed, audio and ownership gates remain.

Preference tests use an isolated Foundation defaults suite to verify reopening,
invalid stored values, launch precedence and cross-dimension isolation. The
source-readiness checks cover stale detail/resize samples, the first unstable
source, invalid dimensions and fresh measured replacements. Simulator UI
inspection caught and fixed a cross-row constraint activated before its views
shared an ancestor; the corrected menu opens and accepts multiple selections.
Phone interaction and performance still need verification on the delivered build.


Build **f40bfef6** was installed on the phone September 13 at 20:59 EDT,
retaining course assets 027. Forty-nine relevant tests passed (preferences,
lifecycle/store/diagnostics, mobile launch/pacing/report tools, output readiness
and startup). The final Simulator build completed both a 100-active-second
interactive menu run and a 40-second fresh-launch preferences check with clean
shutdown and zero runtime faults/JIT entries. Six successful manual setting
changes occur while the menu stays open. The deferred trial request follows
both a measured 2× picture and the actual post-resize presentation, at output
1947 × 896; reopening Menu cancels the waiting trial. No riding extras occur in
this UI check. A later unqualified launch uses the saved 75%/1× selection,
confirming persistence rather than merely falling back to Half/2× defaults.

Evidence: `local/research/120hz/direct-menu-ui-check/` and
`direct-menu-persist-check/`, with delivery receipts in `direct-menu-delivery.json`.
`direct-menu-open.png`, `direct-menu-match-2x.png` and `direct-menu-half-2x.png`
record the actual Simulator UI. These are Null-audio automated checks and do
not close phone audio, checkpoint/Full Reset or sustained-pacing acceptance.
