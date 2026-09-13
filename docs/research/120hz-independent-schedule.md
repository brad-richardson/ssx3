# Independent native render scheduling experiment

September 13, 2026. Follow-up to the [repeated-render seam](120hz-render-seam.md).
This work runs in isolated desktop research players. The installed phone app,
production native player, game module and course assets are unchanged.

**The final host-copy variant succeeds as an independent-rendering proof.** In
a 25-second gameplay window it completes and submits 1,888 draws (75.52/s),
while application updates continue at 59.72/s. All 396 extra draws in that
window leave the watched state unchanged and use zero readiness retries.
This is not 120 Hz presentation or interpolated motion, and is not ready for
installation on the phone.

## Completed evidence

| Metric, host seconds 145–170 | Final host-copy run |
| --- | ---: |
| Completed native renders / matching host submissions | 1,888 / 1,888 |
| Completed extra draws | 396 of 396 attempts |
| Render/submission rate | 75.52/s |
| Application update callback rate | 59.72/s |
| Update callbacks per guest second | 59.9406 |
| Guest seconds per host second | 0.9961 |
| Readiness retries / full-queue deadline events | 0 / 0 |
| Extra draws changing any watched state | 0 |
| Median extra callback wall duration | 7.90 ms |
| Median extra / regular callback guest duration | 3.35 / 6.63 ms |
| Final Metal command-buffer GPU time, median / p95 | 1.36 / 2.62 ms |
| Positive drawable presentation timestamps | 0; actual display rate unknown |

The full bounded experiment completes 404 extra draws and skips each duplicate
timing helper 404 times, with zero changes in any watched rider, application,
view or RNG window. The ordinary update path continues throughout. Submission
mode restoration is observed at host second 175.008. Screenshots during the
experiment and afterward show coherent gameplay continuing through the course.
The 190-second course check passes, with no invalid-memory, unknown-instruction,
malformed-GPU-command or JIT-fallback-run evidence.

The initial normal-queue control completed only one extra draw in its 25-second
window. It retained approximately 59.94 updates per guest second, but used the
older, more expensive probe and 3x internal resolution. It is evidence that
queue ownership matters, not a clean throughput comparison with the final
1x-resolution run. No speedup percentage is claimed.

The scheduler records 1,200 missed grid opportunities and 1,359 opportunities
covered by a recent ordinary render in the final window. The policy is
conservative and uses the last **completion** time; ordinary renders also run
on their original schedule. It is not a unified 120 Hz frame pacer. Callbacks
also still consume guest time and host work, so passing correctness checks does
not establish enough headroom for twice as many draws. GPU measurements above
cover the final command buffer only, not the whole frame.

## Recommendation, in priority order

1. **Keep the native route, but unify rendering around owned render state and
   one presentation clock.** Publish state after the validated update, retain
   host-owned texture/buffer versions, and schedule both ordinary and extra
   draws together. Move the once-per-update helpers outside the repeatable draw
   path. This removes the competition between immediate ordinary rendering and
   conservative extra deadlines. Keep gameplay/input at their validated rate
   and drop render opportunities under load.
2. **Recover and interpolate camera plus rider/board transforms together.**
   This experiment repeats the current pose; the prior frozen-camera test proves
   reversible view changes but not complete visibility or animation handling.
   Add history, discontinuity handling and culling validation before calling the
   extra frames useful high-refresh motion. This remains executable-wide work,
   followed by course validation, rather than per-track patches.
3. **Measure the actual mobile presentation and input path.** The current Mac
   path returns zero `presentedTime` values, so submissions are the strongest
   presentation evidence here. Obtain positive display/frame-ID observations on
   a high-refresh device and separate CPU draw, guest-time accounting, complete
   GPU cost, drawable waits and input-to-display latency. Share the state and
   scheduling contract across iOS/Android; implement Metal/Vulkan ownership and
   presentation adapters separately. Leave higher-rate physics for later.

The result justifies continuing native render-state work. It does not justify
shipping a global speed change, the completion-mode flag alone, or the current
bounded adapter as a production 120 Hz feature.

## What was implemented

An authored C++ deadline policy requests rendering on a 120 Hz **guest-time**
grid. At the main application's idle callback, the adapter yields a normal
CoreTiming CPU slice instead of sleeping the application until video retrace.
It attempts a draw only when the original queue has room, considers a recently
completed ordinary draw to cover a deadline, and drops overdue opportunities
without a catch-up burst. It retains the renderer's readiness check and skips
the two previously identified duplicate timing helpers on extra draws.

The deadline is cooperative: a long game update or render can delay reaching
this safe boundary. This does not create a rendering thread or guarantee an
8.33 ms host deadline. The original input producer, update callbacks, VI rate,
interrupt delivery and graphics completion handlers remain in use.

`render_deadline.h` has no game or platform dependencies. The GXBE69 adapter
checks the pinned executable, active application type and main-idle call site.
There are no Garibaldi coordinates or asset conditions. Other courses and
platforms still need validation; the adapter assumes the current single-player
application and does not support graphics reinitialization after allocating a
spare framebuffer.

## The framebuffer fault and durable correction

The original graphics submission protocol has two queue entries, but that does
**not** imply two allocated output framebuffers. Initialization allocates the
first XFB and explicitly sets graphics+7560, the second pointer, to zero.
Submission normally always selects the first XFB. A separate submission flag
both enables release on graphics completion and selects XFBs by queue index.

The initial completion-mode test changed that flag without allocating the
second XFB. It faulted immediately after enabling the mode, before any extra
render. The guest reached PC 0x400 containing repeated 0x01fe01fe values. The
null second copy destination and overwritten exception-vector pattern support
an XFB-to-zero overwrite as the cause. That failed test is excluded from
performance and correctness evidence.

The next probes exposed two additional limitations. Returning from the allocator
to a location in the same generated chunk bypassed the dispatch observer. A
cross-chunk return sentinel fixed observation, but the late allocation then
failed validation. Its returned pointer was not logged, so pool exhaustion is
not established. Neither run produced a successful completion-mode experiment.

Reserving two buffers inside the original allocation at initialization succeeded
(1,146,880 bytes total), but that run stopped producing screenshots during course
loading and never reached riding. It also is excluded from successful evidence.
This establishes a regression with that configuration, not a proven diagnosis
of guest memory exhaustion or an allocation-accounting bug.

The final variant preserves the original single guest framebuffer. In the
bounded completion-mode window, it aliases the second queue destination to that
same existing framebuffer and requires the host's uncapped immediate-XFB-copy
path. FIFO ordering still serializes copies to the original address; retained
host texture versions are responsible for frame lifetime. It does not allocate
guest memory, forge readiness, decrement pending work, alter queue indices, or
synthesize completion. Copy calls observed at the original frame-end call site
must continue to target the first framebuffer.

This is specifically a **host immediate-copy experiment**, not a double-buffered
physical-GameCube implementation. The submission mode is restored after host
second 175. The alias remains until process exit so any queued index-one work
can still resolve its destination. Production needs explicit resource-version
tracking, draining, reset/resize validation and presentation ownership. The
experiment does not establish that all forms of CPU-side framebuffer access or
other games would be compatible.

The diagnostic runner now stops on an unknown guest instruction and rejects
such a run even if shutdown counters are present. Regression tests cover that
failure. Repeated environment lookups were cached and the scheduler's wall
clock is checked only at relevant boundaries, reducing probe overhead. These
changes mean early failed/slow probes are not comparable performance baselines.

Immediate XFB presentation is an independent host setting. Dolphin's public
[Hybrid XFB explanation](https://dolphin-emu.org/blog/2017/11/19/hybridxfb/)
describes presenting completed XFB copies before the VI path. The checked-out
runtime calls `Presenter::ImmediateSwap` at an XFB copy when enabled; its optional
per-field cap is disabled for this experiment. Neither setting establishes
higher-rate game simulation or distinct interpolated motion.

## Measurement and limits

The common analysis window is host seconds 145–170. Course entry uses the
existing host-timed controller sequence and a fresh profile for each run; these
are not deterministic state-matched replays. Both native callback traces and
Metal presentation observations are enabled. The Mac display is 60 Hz.

A completed render requires a successful callback result plus observed view
setup and graphics frame-end traversal. Merely requesting a draw, passing a
readiness check, or completing a rejected callback is not counted. Actual
presentation counts use positive Metal drawable presentation timestamps;
submissions and zero timestamps are reported separately. A monotonic host-clock
anchor using `mach_absolute_time` aligns those observations to the callback
window. The earlier use of libc++ steady-clock time was wrong on this machine:
it includes suspended time and had a large constant offset from Metal uptime.
Old traces without a valid alignment cannot establish a display rate. Zero
presentation timestamps mean the rate is unknown, rather than zero frames.

Extra-draw comparisons cover the same bounded rider, application, camera and
RNG windows as the previous experiment. They do not establish whole-game
purity, correctness of particles/animations/streaming, or deterministic replay.
Callback duration includes guest preemption and host waits, and is not isolated
renderer CPU time. Update callback counts are not a fully recovered count of
physics steps. No input-latency measurement has been made.

## Local evidence

The final run is `shared-xfb`, profile `sched6`, runtime receipt
`local/reports/native-runs/20260913-105534.json`. The local
`verified-evidence.json` records player, trace and production hashes. Final
callback trace SHA-256:
`1902107e02558cb603abc903a4313c7a5a8d7582f08a7585f96be227e6d3797a`.
The normal-queue control is `normal-queue`; failed variants are `completion`,
`owned-xfb` (raw JSONL preserved losslessly as gzip), `sentinel-1x`, and
`reserved-1x`. Their failed paths are retained as local research evidence, not
as production alternatives. The final builder snapshots the authored probe,
policy and adapter and records the linked presentation observer's hash.

## Reproduction

Generated players, raw traces, captures and game-derived material stay ignored
under `local/research/120hz/independent-schedule/`. The executable pin and normal
course checker remain enforced. Build presentation tracing once, then combine
it with the scheduling adapter:

```sh
python3 tools/gamecube_present_trace.py \
  --output local/research/120hz/schedule-present-new
python3 tools/gamecube_native_trace.py build \
  --game local/game/gc-gari-027 \
  --output local/research/120hz/schedule-player-new --scheduler \
  --presentation-object local/research/120hz/schedule-present-new/MTLGfx.o

SSX_NATIVE_PROBE="$PWD/local/research/120hz/schedule-new.jsonl" \
SSX_NATIVE_SCHEDULE=1 SSX_NATIVE_COMPLETION_RELEASE=1 \
SSX_NATIVE_SKIP_BOOKKEEPING=1 \
SSX_PRESENT_TRACE="$PWD/local/research/120hz/schedule-present-new.csv" \
python3 tools/gamecube_schedule_check.py \
  --player-dir local/research/120hz/schedule-player-new --immediate-xfb \
  --resolution 640x528 --game local/game/gc-gari-027 \
  --profile schedule-new --output local/research/120hz/schedule-run-new \
  --seconds 190

python3 tools/gamecube_schedule_trace.py \
  local/research/120hz/schedule-new.jsonl \
  --present local/research/120hz/schedule-present-new.csv
```

The scheduler flags are presence-based: unset them to disable. The scheduler
requires helper skipping and rejects the previous double-render, wait and frozen
sweep modes. Use fresh output names and profiles. The standalone native trace
summarizer is for paired-render experiments; use the scheduling summarizer for
mixed callback/deadline traces.
