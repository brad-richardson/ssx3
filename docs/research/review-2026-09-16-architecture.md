# Architecture review of September 15–16 changes

Read-only review of the last two days of commits (`f43ac70`..`9604488`), focused
on the 120 Hz direction (`native/diagnostics/*.h`, `native/ios/App.mm`, the
trial tooling) with a lighter pass over the startup, texture-pack, memory-card
and audio changes. Nothing was edited or run other than reading files and
grepping existing traces under `local/research/120hz/`.

## 1. Combined trial never interpolates: the pose history rejects every frame under F doubling

**Severity: high.** This invalidates the "MECHANICS GREEN" gate-4b verdict and
the phone Combined oracle as recorded in `120hz-f-spike.md` and `docs/todo.md`.

Mechanism. `NativeInterpolation::Before` bumps `generation` on every update
return:

```
if(update.pending&&c.pc==update.ret){++generation;update_ticks=timing.GetTicks();}
```

Under F/Combined the repeat half also returns through `update.ret` with
`update.pending` still set, so a doubled tick advances `generation` by two.
`PoseHistory::Begin(next)` only keeps `previous` when `next == generation+1`;
otherwise it clears it. Every render in a doubled window therefore starts with
an empty `previous`, `Sample` fails for every key including the camera,
`has_camera_delta` is false, `prepared` is false, and the upload hooks never
fire. Extras are drawn at the current pose, exactly like a plain repeat draw.

Evidence already on disk:

| trace | extras | extras with `blended > 0` |
| --- | ---: | ---: |
| `interpolation/guard-events.jsonl` (smoothing only) | 806 | 804 |
| `interp-fx-events.jsonl` (F + schedule + interpolation, the gate-4b run) | 36 | 0 |
| `lifecycle-combined3.jsonl` leg 4 (Combined kind) | all | 0 |

Every `interpolation` row in the F runs reads `loaded:0, blended:0,
camera_only:0` with `generation` stepping by 2 per tick, alpha nonetheless in
0.58–0.78. The alpha is computed independently of the history, which is why
the doc could report "36/36 interpolated extras at alpha 0.60–0.78 — genuine
mid-blend draws" while zero matrices were blended.

Consequences for the direction:

- The phone Combined result (278 extras at 16/s, floor limit at 0.946) ran with
  the immediate-XF upload path effectively disabled, so it understates the
  composed cost. A working Combined re-adds the per-frame palette re-upload
  that the September 13 doc identified as the phone's dominant smoothing cost.
  Expect the honest number to be worse, not better.
- `present.csv` presents/s cannot distinguish an interpolated extra from a
  duplicate frame, so the display oracle passed on duplicates. Any >60
  displayed/s claim for Combined needs the `blended` column alongside it.
- `validate_trial_trace` in `tools/gamecube_schedule_check.py` checks
  `same_rider`, `same_view`, and the offset lists but never `blended`, so the
  lifecycle check cannot catch this. Neither can `collect` on the phone.

Fix shape (not applied): count a generation once per tick, at the first half's
return, e.g. `if(update.pending&&c.pc==update.ret&&!update.repeated)`.
At that dispatch `update.repeated` is still false for body1 and true for body2,
and non-doubled ticks have it false, so every tick counts exactly once. Then
add `blended > 0` to the extra-draw assertions for the smoothing and combined
legs in `validate_trial_trace`, and surface a blended count in the phone
metrics next to `trialExtras` so the present oracle is paired with it.

## 2. The trial state machine is scattered across four headers of file-scope statics

**Severity: medium (maintainability, latent bugs).** The trial lifecycle is now
carried by `NativeTrial::{status,kind,cancel,limited}`, `NativeProbe::{update,
render,f_patched,tick_*,...}`, `NativeSchedule::{schedule_started,mode_changed,
mode_address,first_xfb,budget,speed_floor}` and `NativeInterpolation::{active,
prepared,generation,...}`, with the ordering invariant "Interpolation::Before →
Schedule::Step → Probe::Step, and Finished may only be set after FRestore and
the mode restore" expressed as comments at three sites (`native_callback_trace.h`
lines ~465–477 and ~586–597, `native_render_schedule.h` lines ~112–126).

`SSXResetNativeTrial` hand-enumerates the statics to reset and misses several:
`tick_have/tick_saved/tick_restores`, `update_repeats`, `interleave_armed`,
`half_cadence_updates`, `emit_rows`, the per-render counters, `saved_mode`,
`NativeInterpolation::alpha/loaded/blended`, and all of `CallbackTimer::{update,
render}`. Today these are benign (counters, or re-seeded at the next entry),
but each new trial kind adds to the list by hand. Finding 1 is a symptom of the
same thing: the interpolation layer did not know the probe layer had started
re-entering updates.

Suggestion: one `TrialState` struct per namespace with `= {}` on reset, and
a single `Finish(kind)` that owns the "restore consts → restore mode → set
Finished" order instead of three call sites each re-deriving it from `kind`.

## 3. Restore drift persists a halved guest into checkpoints

**Severity: medium consequence, low likelihood.** `FRestore` on verify failure
logs "guest stays halved", sets `limited`, clears `f_patched`, and (for pure F)
sets `Finished`. The frontend's pause path waits only for a terminal status,
then checkpoints. That savestate then carries 1/120 dt consts forever; every
later F trial's `FPatch` verify fails against them and cancels gracefully, and
the menu reports "Sim trial ended to maintain game speed", which is the wrong
message. This contradicts the stated invariant in `App.mm` that "a checkpoint
must never capture ... an F trial's halved dt consts".

Suggestion: a sticky `NativeTrial::tainted` (or a `Tainted` status) that
`savePausedSession` and the boot-checkpoint path refuse to save through, plus
its own menu string. Drift should be near-impossible since the consts live in
`.data` and nothing writes them, so this is cheap insurance rather than a
live bug.

## 4. Doubling is gated on rider-state stability, which is a product-path timestep hazard

**Severity: design question, not a defect.** The repeat requires
`update.before.state==b.state`. With the consts patched, a tick whose first
half changes rider state runs once at dt = 1/120 and advances half a frame of
game time. The research doc treats these as "skips" and shows they do not
perturb the counter, which is right for parity analysis. For the shipped 120 Hz
sim mode it is a systematic slowdown proportional to the state-transition rate,
concentrated at landings, crashes and rail mounts, which are the moments where
physics fidelity matters most. Worth deciding explicitly whether the ship path
doubles unconditionally (with the +1 counter check as the safety) or keeps the
gate and accepts the time loss.

## 5. Smaller items in the 120 Hz path

- `NativeSchedule::Step` returns before anything else when `Output()` is null.
  The app always passes a log path, but `Output()` aborts the process on
  `fopen(...,"wx")` failure (disk full, stale file). On device that is a crash at
  the first trial dispatch instead of `Status::Unavailable`.
- `App.mm` now has three copies of the scheduled-trial block
  (`_scheduledTrialAt`, `_scheduledFAt`, `_scheduledCombinedAt`) and three
  matching argument parsers. A small table of `{flag, ivar, Kind}` would stop
  them drifting; the F copy already differs from the smoothing copy only in the
  request call.
- `refreshSessionMenu` reads `NativeTrial::kind` to pick the "ended to
  maintain game speed" string, but `kind` is whatever the last `Begin` set, so a
  stale `limited` from an earlier trial can be labelled with a later kind.
- `Deadline` uses `TicksPerSecond/120` and interpolation alpha uses
  `TicksPerSecond/59.94`. Consistent today because F doubles inside a VI tick,
  but if the queue ever moves to VI-paced 2-deep (backlog 10) the alpha period
  needs to follow.

## 6. Non-120 Hz changes

- **Boot checkpoint (`8fc984f`)** — `_bootCheckpointInFlight` is set around a
  synchronous call, and `savePausedSession` checks `_sequence` at its top before
  going async, so the exception works. The `_checkpointAgain` deferral path is
  unreachable from here because the tick condition already requires
  `!_pendingCheckpoint`. Fine.
- **Pack pruning (`1c8b837`)** — deletes up to ~8.8k files synchronously on the
  main thread inside `startGame`, keyed on a marker file the installer writes.
  The comment acknowledges the cost. It is the only destructive filesystem
  action added; the `tex1_` prefix and extension check are a reasonable guard.
- **Course cache (`_coursesCache`)** never invalidates within a process. Correct
  as long as installs always relaunch, which the README checklist says they do.
- **`SSXLaunchTrace`** appends to `Documents/launch-trace.txt` forever across
  launches. Cheap, but worth a truncate-on-launch or a size cap.
- **Memory card read-rate patch** parses the env var per transfer by design;
  a handful of DMAs per boot, so no cost. The patch header still says "writes
  are deliberately left at hardware rate", but the same patch defines
  `MC_TRANSFER_RATE_WRITE` through `SSX3_MEMCARD_WRITE_SPEEDUP` and `App.mm`
  sets it to the read factor. Behaviour is what the app intends; the comment
  is stale.
- **DC blocker patch** — first-order high-pass on the render thread, per-channel
  float state, clamped. Correct and cheap. It also removes any legitimate DC
  in game audio, which the 38 Hz cutoff makes inaudible.
- **`metal_capture.py`** has an uncommitted working-tree change; not reviewed
  since another agent owns it.

## Suggested order

1. Fix the generation double-count, rerun `interp-fx` and the lifecycle
   combined leg, and confirm `blended > 0` before re-issuing the gate-4b
   verdict. Add the `blended` assertion to `validate_trial_trace`.
2. Re-run the phone Combined trial with blending actually on. That number,
   not the current one, decides whether retained host palettes (priority 1 in
   `120hz-native-interpolation.md`) are the next block of work.
3. Add the tainted-guest guard (item 3) while the F code is fresh.
4. Decide item 4 explicitly and record it in the plan of record.
