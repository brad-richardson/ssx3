# RV6 — SSX 3 simulation timing and true 120 Hz

**Finding:** the inspected PS2 application machinery implements **VBlank-driven, buffered
fixed-step work with catch-up and separately gated rendering**. It does not derive a fresh
physics delta from elapsed host time. Nominal rate and duration are explicitly 60 and 1/60,
but they are not the only timing inputs: independent 1/60 literals and timer-count consumers
exist elsewhere. Doubling VBlank alone predicts accelerated gameplay; halving one duration
field cannot establish normal-speed 120 Hz. The exact rider integrator and HUD clock still
need live attribution. This is a source model, not a new runtime measurement. [§1–§4]

**Recommendation:** do the bounded timing census now; queue one deliberately incomplete
rate/duration experiment to expose unconverted consumers; park a shipped 120 Hz mode until
both behavior and Odin service budgets pass. Two physics steps per stock VBlank can test
finer integration without changing the emulated hardware clock, but cannot prove evenly
spaced 120 Hz input or presentation. [§5; RV4 §4]

## Scope, pins and evidence convention

- SSX3 initial HEAD: `bd2853319ddf1085b4be4a9743076db2210f2aea`; initially clean.
- Runtime inspected: `~/dev/PS2Recomp`, branch of record `ssx3`, HEAD
  `f949ff060d9a0c53f3ab47998068b771f20653e3`; initial status clean.
- `G` means `~/dev/ssx3-work/codegen-ssx3/`. Guest addresses identify instructions in
  `sub_<owning start>_0x<owning start>.cpp`; merged functions can contain multiple entries.
  These names are addresses, not recovered semantic symbols. Semantic names inherited from
  X2/X3 are labels for orientation; the conclusions below use instructions and data edges.
- `R` means the runtime checkout above. `S` means
  `R/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`; `M` means
  `R/ps2xRuntime/src/lib/ps2_memory.cpp`.
- `E` means `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72`, SHA256
  `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`.
  Two independent reads matched. ELF PT_LOAD maps file offset `0x1000` to VA `0x100000`,
  file size `0x3a4bf4`; cited initialized data use file offset `VA - 0xff000`.
  ELF `.reginfo` gives `gp=0x4a30f0`, independently constructed at guest `0x31a724–0x31a728`.
- X2/X3 mean their reports **and** `ORCH-CORRECTIONS.md`, read corrections first.
  RV4 means [the performance review](review-2026-09-26-astra-perf.md), especially §4.
- No builds, boots, device operations, source changes, or performance measurements.
  Generated game code was read locally; this report contains derived descriptions and
  addresses, not copied implementations. Only this report is written.

## 1. The recovered scheduling chain

Let **A** be the application-manager object stored at `gp+0x2a74` (`0x4a5b64`). Its
constructor stores that pointer and initializes the fields below. Its derived constructor
installs vtable `0x47d9c8` at `A+0x5c`. This resolves the previously unknown manager virtual
calls without guessing their names. [G `sub_00316CD0`: `0x316ce8–0x316d20`;
G `sub_00226830`: `0x22683c–0x226854`; E vtable `0x47d9c8`]

| Field | Established use / initial value | Evidence |
| --- | --- | --- |
| `A+0x10` | Integer nominal rate, initialized to 60; converted to float by consumers | `0x316d6c, 0x316d98`; e.g. `0x3413c0–0x3413d4` |
| `A+0x14` | Float duration, initialized from `0x4a01f8` = `0x3c888889` = float(1/60) | `0x316d64, 0x316d88`; E constant |
| `A+0x18` | Count of accumulator/timer-wrapper invocations, incremented once per invocation | `0x317374–0x317380` |
| `A+0x1c` | Count incremented immediately before the active application's update call | `0x317198–0x3171b4` |
| `A+0x20` | Catch-up threshold, initially 12; not an elapsed-vsync count | `0x316ce4–0x316cec`; `0x317188–0x317190` |
| `A+0x24`, `A+0x28` | Producer multiplier (initially 1.0), fractional accumulator (initially 0) | `0x316cd4–0x316d10`; `0x317364–0x3173c8` |
| `A+0x2c`, `A+0x30` | Smoothed rate-like metric, initially 0 and 0.9; not the physics dt | `0x316cfc–0x316d14`, `0x316cf8`; E `0x4a01f4`; `0x317254–0x3172c0` |
| `A+0x34` | Render gate mode, initially 0; mode 1 requires at least two counted steps | `0x316cfc`; `0x3171e0–0x317244` |
| `A+0x58` | Application-transition state; 0 is the normal path considered here | `0x316f70–0x316fac`, `0x316e84` |

**Clock source is VBlank-end, via an interrupt and semaphore.** Execution-manager setup
constructs vtable `0x48db68`, passes it to `0x316d60`, and that routine calls slot `+0x14`
with nominal rate argument 60. The slot resolves to `0x31a6d8`; its inspected body does not
use that rate argument to program a 60 Hz hardware timer. It creates the worker whose entry
is `0x31ac08`, then registers INTC cause **3**, handler `0x31a490`, handler argument
`0x31abd0`. The handler saves FP registers and calls its supplied argument at `0x31a598`.
The latter function signals the worker semaphore using `iSignalSema`; the worker waits on
it, then calls `0x317500 → 0x317348`. Thus changing the initializer's 60 argument alone does
not increase production frequency. [G `sub_0031AF80`: `0x31afd0–0x31afec`;
G `sub_00316D60`: `0x316d94–0x316dac`; E `0x48db7c=0x31a6d8`;
G `sub_0031A6B8`: `0x31a86c–0x31a8ec`; G `sub_0031A490`: `0x31a598`;
G `sub_0031AAF0`: `0x31abd0–0x31ac34`; G `sub_00317500`: `0x317504–0x31750c`]

The syscall labels are independently checked: wrappers `0x423a90`, `0x423dd0`, `0x423de0`
select `0x10`, `-0x43`, `0x44`; Dispatcher maps these to AddIntcHandler, iSignalSema,
WaitSema. S dispatches cause 3 at VBlankEnd. Existing E24 §thread identity and E26's
semaphore-31 evidence corroborate this worker path during the older movie stall; they do
not measure its race cadence. [R `Kernel/Syscalls/Dispatcher.cpp:125,270,273`;
S:2868–2870; `local/research/E24/REPORT.md:78`, `E26/REPORT.md:113`]

**Producer:** `0x317348` adds `A+0x24` to the fractional accumulator, computes the difference
between integer conversions before and after, retains the remainder, and calls manager
vtable slot `+0x3c` that many times. With the initialized nonnegative accumulator and
multiplier 1, this is one call per timer wake. That slot is `0x227f58`, which calls
`0x326b88` on the object at `gp-0x850` (`0x4a28a0`). The latter polls registered channels
through a virtual read, stores records, and advances its producer index modulo **30**.
This is buffered sampling; the integer 30 is ring capacity, not proof of a 30 Hz clock.
[G `sub_00317348`: `0x317364–0x3173c8`; E `0x47da04=0x227f58`;
G `sub_00227F58`: `0x227f5c–0x227f68`; G `sub_00326B88`: `0x326bc0–0x326c4c`]

**Consumer:** manager slot `+0x34` is `0x227e98`. It calls `0x326b48`, which advances the
consumer modulo 30 unless the next index equals the producer. On success, `0x227e98`
retrieves two channels with `0x326ca0/0x326cc8`, passes them to `0x321298`, and returns 1;
otherwise it returns 0. The main loop's `0x3171d0` calls this consumer; a nonzero return
branches to `0x317180`, increments `$s1`, checks the catch-up threshold, increments
`A+0x1c`, and invokes the active application's vtable slot `+0x34`. It repeats until no
sample is available, subject to the catch-up escape below. [E `0x47d9fc=0x227e98`;
G `sub_00326B48`: `0x326b4c–0x326b84`; G `sub_00227E98`: `0x227eb8–0x227f3c`;
G `sub_00316F00`: `0x317180–0x3171dc`]

A concrete active-app table exists at `0x47d110`: slot `+0x34` points to `0x2306b8`, which
contains the Metro render-gate stores and a substantial application update; slot `+0x3c`
points to `0x22b008`. Capture the live `A+0`, its vtable, and the call targets before asserting
that these are the active targets throughout a particular race. Static table contents alone
are not a live race receipt. [E `0x47d144`, `0x47d14c`; G `sub_002306A8`, entry `0x2306b8`]

**Timing model:** for the normal initialized path, update work is proportional to buffered
VBlank-derived sample production, not one update per rendered frame and not a variable dt
computed from elapsed EE timer reads. Catch-up can execute multiple updates before rendering.
This establishes the application-level cadence. It does **not** prove one rider integration,
one AI tick, or one animation evaluation per application update. [Chain above; §3]

## 2. Correcting the earlier loop map and interpreting slow frames

X3's correction file fixes a delay-slot attribution, but the report still has erroneous
forward targets. Recomputing `PC+4+(signed immediate×4)` from the instruction words gives:

| Site | Correct edge / meaning | Consequence |
| --- | --- | --- |
| `0x316f84`, immediate `0x6e` | Taken branch reaches `0x317140` | Normal state checks whether a replacement app is pending; it does not enter the reported `0x317138` edge |
| `0x3171d8`, immediate `-0x17` | Taken branch reaches `0x317180` | `checkHalt` executes, including its increment delay slot at `0x317184`; not a jump directly into that delay slot |
| `0x317190`, immediate `-0x1b` | Branch on **limit < counter** reaches `0x317128` | Exceeding the limit goes to the resynchronizer, not another ordinary physics step |
| `0x317138`, immediate `0x29` | Reaches `0x3171e0`, adding the resynchronizer's return to `$s1` in the delay slot | Exits catch-up into render gating; does not return to `0x31718c` |
| `0x317140`, immediate `0x21` | Reaches `0x3171c8` when pending-app pointer is zero | `10.0` and `0x317530` are on the transition path, not in the normal per-step body |
| `0x2306e4`, immediate `0xb` | Reaches `0x230714` | The store of mode 1 and the later conditional-store path are alternatives, not consecutive writes |

Evidence: G `sub_00316F00_0x316f00.cpp:547,1623,1651,1794,1820,1828,1983`;
G `sub_002306A8_0x2306a8.cpp:682`. Guest words were read directly, not copied from X3's
computed-target column. X3 also places a counter reset at `0x317064`; it is at `0x31706c`.

Manager slot `+0x2c`, reached after the threshold is exceeded, resolves to `0x227e68`, then
`0x326c60`. That function resets the consumer to `(producer+29)%30` and computes a
backlog-related return from the old producer/consumer positions. It does not run the active
application's update for each discarded record. Therefore the default **12** is a cap on
ordinary catch-up updates across the current counted interval, followed by queue
resynchronization; do not model unbounded faithful simulation catch-up. `$s1` includes
resynchronization accounting as well as executed updates, so it is not a unique-physics
counter. The complete overflow/alias behavior of the 30-entry ring is a runtime test gap.
[E `0x47d9f4=0x227e68`; G `sub_00227E68`: `0x227e80`;
G `sub_00326C60`: `0x326c60–0x326c98`; `0x31713c`, `0x3171a4`]

**Render mode 0:** after draining available work, the main loop requests the active-app
slot `+0x3c` when `$s1 != 0`. **Mode 1:** it first requires `$s1 >= 2`. When the render
callback reports success, the loop resets `$s1`; otherwise it takes execution-manager
wait/poll work and retains the count. Thus mode 1 can deliberately produce approximately
one successful render per two updates under steady service, while retaining the nominal
update cadence. It is not merely an automatic frame-rate-dependent dt adjustment.
[G `sub_00316F00`: `0x3171e0–0x317250`, `0x3172c4–0x3172ec`]

The Metro path writes mode 1 when `[[this+0x84]+0x10] >= 2`; otherwise it compares a result
from `0x2ee400(6)` against float 0.9 at `0x49df34`, writing 1 when that result exceeds 0.9,
else 0. The semantic identity of that result was not recovered. The published two NOPs at
`0x230704/0x230710` suppress this conditional path's store; they do not globally force a
specific mode or remove the separate mode-1 store at `0x2306e8`. [G `0x2306cc–0x230710`;
E `0x49df34`; X3 ORCH-CORRECTIONS]

The published counter increment 1→2 can meet the two-count render threshold after one real
update, but also reaches the catch-up threshold sooner. It changes **accounting and render
policy**, not the physics timestep. X3's “halves the passes per frame” is only a conditional
behavioral summary, not a general proof or a 120 Hz implementation. Also, `10.0` feeds an
object initialized by `0x317530` at `A+0x38`; it is not established as milliseconds of physics.
[G `0x317184`, `0x3171ec`, `0x317188`; `sub_00317530`: `0x317530–0x317548`]

When the host cannot keep up, distinguish two effects: guest backlog can trigger the above
catch-up/render behavior; a cycle-driven runtime executing slowly can simply advance fewer
guest seconds per wall second. The latter does not guarantee the guest sees corresponding
missed wall-clock VBlanks. [S:2680–2775; §4]

## 3. Timestep consumers: a mixed, distributed contract

There is direct evidence against “change one dt and everything follows.” The following are
semantic descriptions of arithmetic, not unsupported rider/AI function names:

| Timing input / consumer | What the code establishes | 120 Hz implication |
| --- | --- | --- |
| Manager rate and dt | `0x316d6c/0x316d98` set integer 60; `0x316d64/0x316d88` independently copy float(1/60) from `0x4a01f8` | Keep `rate × dt ≈ 1`; changing either alone leaves the other unchanged |
| Rate-derived integer lifetime | `0x3413c0–0x3413d4` converts `A+0x10` to float, multiplies a supplied duration, converts to integer, stores it | Initialize at the new rate or migrate cached counts; changing rate halfway through a race can leave old counts |
| Manager-dt countdown | `0x35253c–0x352550` subtracts `A+0x14` from object `+0x1c` and checks expiration | This consumer would follow a halved manager dt |
| Mixed vector update | `0x352450–0x352498` uses both reciprocal rate and manager dt; `0x352688–0x3526cc` adds stored displacement, then adds a dt-scaled vertical term | Some stored values are per-step quantities; blindly halving every coefficient would double-scale some terms |
| Independent countdown | `0x101534–0x101550` subtracts float(1/60) at `0x49b15c` from a field | Does not follow manager dt; expires twice as fast if invoked twice as often |
| Independent vector integration | `0x1139a4–0x1139e4` uses float(1/60) at `0x49b4a0`, multiplies the vector at `a2`, adds it to the vector at `a1`, writes `a3` | Explicit position-like integration bypasses manager dt; whether this is the live rider integrator remains unproved |
| Independent scaled helper input | `0x1048c4–0x1048f0` multiplies its float argument by float(1/60) at `0x49b1ac` before calling `0x3135b0` | Caller/callee units must be resolved before substitution |
| Producer-count periodic work | `0x1b2340–0x1b2354` tests `A+0x18` modulo 10,000 | Doubling producer wakes changes this wall-time interval; doubling only the producer multiplier does not |
| Update-count elapsed time | `0x3175b4–0x3175d8` uses `(A+0x1c - savedCount) × A+0x14` | Count and duration changes can compensate here; dropped steps and cached timestamps still matter |

Evidence files for these address ranges: G `sub_00316D60`, `sub_00341388`, `sub_00352230`,
`sub_001013A8`, `sub_001139A0`, `sub_001048C0`, `sub_001B2320`, `sub_003175A0`; constants
independently read from E. A gp-relative constant scan found many additional 1/60 loads.
Merged generated entries duplicate addresses, so source-file occurrence counts are not a
count of distinct subsystems. No blanket replacement list is proposed.

**Physics:** trace the live rider position write back to integration and collision, including
VU0 operations, before changing its duration. The known position lead is `0x5409c0`, three
floats; this is in `docs/runtime-validation.json:104` and `tools/track_position.py:1,9`, not
in the current `docs/facts.md` despite the brief's pointer. Confirm it follows the rider on
this route. Recover velocity, gravity, friction, collision thresholds and any internal
substeps. A rate-normalized translation can still have wrong turning, jumps or collisions.
For a multiplicative per-step damping coefficient `d`, equal damping over one old step
requires two half-steps whose coefficients multiply to `d`; simply dividing `d` by two is
wrong. This is an experiment-design requirement, not a recovered SSX damping formula.

**Animation and AI:** no complete live ownership/cadence map was recovered. Audit frame-index
advancement, blend filters, tick divisors, cooldowns and random draws. Keep authored duration
in seconds, convert frame-authored values using the original sample rate, and decide explicitly
which systems run twice as often. More calls can consume more RNG even when dt is correct;
G `0x3523b8–0x352440` is a concrete example of repeated calls to `0x3177f0` interleaved with
rate-derived arithmetic. Its gameplay role is not established here.

**Race clock and records:** the exact HUD timer/finish-time accumulator is **not found** in
this review. Identify both; an unchanged displayed integer second can hide a wrongly scaled
underlying score. Require the same normal-time race duration semantics for countdown, finish
ordering, penalties and trick windows. Keeping a UI clock at 1× while the rider goes 2× is a
failure, as is halving movement while leaving AI or timeout logic at 2×. [Unresolved consumers
above; requested observables in §5]

## 4. What a “120 Hz vsync” change would actually change

The runtime currently uses **16,667 µs** for VBlank period and **500 µs** for VBlank duration,
with corresponding cycle constants computed at **294,912,000 EE cycles/s**. That period is
approximately 59.9988 Hz, not exact NTSC 59.94. Keep the project's 59.94 speed-reporting divisor
separate from the clock the scheduler actually emits; do not quietly replace either while
assessing a timestep change. [S:70–90; M:287; AGENTS.md Speed numbers]

S schedules each subsequent VBlankStart and its VBlankEnd using those constants. Start
increments its VBlank tick, updates GS FIELD/VSINT, completes vsync waiters and dispatches
INTC 2; End dispatches INTC 3, which drives the guest path in §1. With cycle-only events,
host time does not determine delivery order; the other path requires both cycle and host
deadlines. Slowing the host therefore is not equivalent to changing the guest clock.
[S:2680–2775,2782–2798,2807–2869]

EE timers are a separate path: accountCycles advances the timer model, which derives ticks
from its selected clock (147,456,000 / 9,216,000 / 576,000 / 15,734 Hz), COUNT/COMPARE and MODE.
Pending timer IRQs dispatch on causes 9–12. No RCNT COUNT/COMPARE or COP0 Count read appears
in the recovered producer/consumer timing arithmetic. This is a bounded negative result,
**not** proof that all race, audio or SDK code ignores those clocks. [S:1002–1012,2649–2655;
M:287–293,533–603; guest chain §1]

| Proposed change | Predicted behavior / limitation |
| --- | --- |
| Host display at 120, unchanged guest clocks | More presentation opportunities; no additional guest simulation caused by this change |
| Twice the runtime throughput, unpaced | More guest seconds per wall second; not finer simulation steps |
| VBlank period halved, original guest timing | Roughly twice as many producer wakes and fixed-size updates if service keeps up; accelerated vsync-linked game time, original-rate EE timers/audio can disagree |
| Only manager dt halved | Slows dt consumers; literals, rate-derived counts and sample production remain unchanged |
| Manager rate 120, dt 1/120, multiplier 2, stock VBlank | Two buffered update opportunities per timer wake; useful conversion probe, but independent literals remain wrong and input opportunities are clustered |
| Complete timestep conversion plus a separate 120 Hz simulation schedule | Candidate for normal-speed finer simulation; requires subsystem, input and determinism validation, not just a counter change |

Audio must retain its own timebase. Music is EE-mixed at **36 kHz**, **384 frames/tick**,
then resampled to **48 kHz**; that is **93.75 sound ticks per guest second**. Runtime sound
scheduling uses **3,145,728 EE cycles/tick**, separate from VBlank. Halving all scheduler
periods or changing EE-clock scaling would alter audio production too. Doubling simulation
callbacks can instead leave audio pitch unchanged but make music/game events disagree;
exact symptoms depend on buffers and consumption. Track PCM samples, queue fill and event
alignment, not pitch alone. [docs/facts.md Guest, AU8; R `ps2xRuntime/include/ps2_snd_spike.h:47–48`;
S:2873–2877]

## 5. Ranked plan and the first bounded experiment

| Rank / tag | Action | Gate / next decision |
| --- | --- | --- |
| 1 — **do now** | Observe one stock race's full scheduling chain and live update/position/clock writes | Confirms static model and supplies the actual patchable physics boundary; no speed claim |
| 2 — **queue** | One reversible three-field conversion probe: rate 120, dt 1/120, producer multiplier 2; keep hardware clocks stock | If only some observables preserve normal time, identify the first unconverted consumer; do not add patches in the same run |
| 3 — **queue** | Convert the attributed physics/time consumers; define update ownership for AI, animation, input and records | Deterministic same-mode repeats, normal-time motion/clock tests, discontinuity tests, complete-race validation |
| 4 — **queue** | Measure 60 Hz service budgets first, then split simulation/render cadence and measure 120 Hz scheduling on Odin | Actual unique updates per wall second plus frame-time distributions; RV4 §4's budget remains separate from timing correctness |
| 5 — **park** | Ship/claim true 120, globally double EE/VBlank/audio clocks, global 1/60 search-and-replace, or use the published FPS patches as timestep patches | None establishes the coherent behavior required above |
| 6 — **park** | Revive GameCube host replay/interpolation | Different output and explicitly reserved route; §6 |

**First-experiment brief sketch:** E lane owns the runtime mutation and lease. Budget one
small diagnostic build and two fresh deterministic I26-FAST boots on bradflix, each capped
at t2400 and 600 wall seconds, with at most 32 MiB of bounded text per run and 2 GiB new
build/receipt output excluding an existing shared build. Start from pinned runtime/codegen,
ELF, route and save hashes, checked twice. Add an observation-only tap, armed for established
race ticks, recording monotonic time, EE cycle, VBlank tick, `A`/active-app/vtable pointers,
`A+0x10..0x34`, producer/consumer indices, timer-wrapper count, successful consumer count,
actual update-entry/return count, render-call/success count, and the position triple before
and after updates. Add a bounded write/caller trace for the timer that drives the HUD; report
“not found” if attribution exceeds the cap. The correct model predicts one produced record
per wrapper wake at multiplier 1, one application update per successful consume below the
cap, and no constant-dt inflation when rendering lags; alternatives are render-coupled
updates, additional physics substeps, or variable-time consumers. Compare both controls at
identical guest-time points, using existing deterministic hash and trace tooling. Stop on
foreign lease, error, unexpected pointers, lost trace rows or a repeat mismatch; hand back
counts and first disagreement, not a candidate fix. Do not infer overload behavior if the
controls never create backlog; queue a separately budgeted guest-load perturbation.

For rank 2, authorize a separate build/run only after rank 1 resolves the active object and
update boundary. A guarded experimental initializer can set `A+0x10=120`,
`A+0x14=float(1/120)` (`0x3c088889`), `A+0x24=2.0`, before rate-dependent objects are created;
verify their original values and initialize the fractional accumulator consistently. Keep
`A+0x20`, render mode, hardware clocks and audio unchanged so they remain observable controls.
This is intentionally a **partial conversion probe**, not a claim of correct 120 Hz. Its
scope is three manager fields; if cached counts were initialized earlier, stop and move the
hook in a new brief. A cold-start arm also changes menu timing, so verify the route still
reaches the same event before comparing racing. Do not silently compensate a broken route.

Report the following for both stock and candidate, without requiring cross-mode bit equality:

- **Unique update count:** count completed, state-mutating rider integrations as well as
  application updates; report per EE-time second, VBlank, and wall second separately.
  `$s1`, rendered frames, changed screenshots, and position changes alone are insufficient.
- **Game-time pace:** slope of the underlying race clock and HUD clock against monotonic wall
  time on a paced host with measured headroom; also against EE time for slow diagnostic runs.
- **Motion:** distance/path progress, velocity, turn response and jump trajectory over equal
  time under constant input. Use a short collision-free segment first; establish position
  units and baseline repeat noise. Compare complete races later, since finer integration
  need not reproduce an identical long chaotic trajectory.
- **Input:** timestamp physical/script sample, buffered record and consumption. Hold input
  constant through the measurement segment, or index its transitions by elapsed time, not
  raw callback count. I26-FAST's vsync-indexed navigation is not itself a 120 Hz input oracle.
- **Synchronization:** sound sample production and queue drift; animation/event progression;
  AI and finish-time behavior. Keep all diagnostic throughput explicitly diagnostic.

Acceptance separates mechanism from performance: two real integrations per old interval
with half-step behavior is a finer-step result even if the diagnostic run is slow; it is
**not** demonstrated normal-speed 120 Hz on Odin. Conversely, a faster clean run with the
old integration interval is only faster execution. For normal-speed acceptance, set motion
and clock tolerances from baseline controls before candidate runs, then require roughly twice
as many actual integrations per wall second without doubled clock or movement slopes.

## 6. Risks, reserve-work relevance and open questions

**Determinism and saved behavior:** deterministic mode fixes RTC and guest event order
(docs/facts.md Runtime semantics; E55A2/E55B2/E55C2). Changing the timestep intentionally
changes operation order and possibly RNG consumption; require exact repeats within each
mode, not equality between 60 and 120 modes. Input movies/ghosts indexed by ticks need
rate metadata or resampling, and sampled poses are not a resimulation oracle. Audit saved
countdowns and cached per-step velocities. Treat record comparability as unproved until
race-time and finish rules are validated; keep experimental records separate. An online
protocol and its timing assumptions were not inspected, so no compatibility claim is made.

**Reserve is useful methodology, not a PS2 result.** The GameCube timing study resolved
an analogous accumulator and buffered input path, while explicitly warning that input
callbacks are not physics substeps. The September 17 plan defined 120 distinct presented
frames with either 60 or 120 Hz simulation; its replay route does not meet today's stronger
simulation goal. Host replay requires rendering/resource/event isolation and clean guest
continuation. Those lessons transfer; GameCube addresses, replay timings and determinism
receipts do not prove PS2 physics conversion or performance. D6's callback/engagement evidence
is similarly platform-specific. Leave the route parked. [docs/reserve.md; docs/reserve/
plan-120fps-2026-09-17.md Definition; docs/research/120hz-analysis.md Resolved callback
boundaries; docs/research/120hz-host-replay.md Current correctness milestone;
local/research/reserve-gc/android-spike/D6/REPORT.md Gate and method / Per-arm race anchors]

Remaining questions, in dependency order:

1. Are the decoded static vtables the live race targets, and how often do the rider and AI
   integrate per active-app update? Does position `0x5409c0` remain the correct live observable?
2. Which literal/rate/dt consumers lie on that path, and where do the race clock, finish time,
   animation and collision code obtain time? What already runs at a different internal rate?
3. How much backlog occurs in stock single-player and split-screen? How does ring overflow
   interact with the threshold, and what elapsed time is intentionally discarded?
4. Which producer samples contain newly polled hardware input? Two samples produced in one
   wake may repeat the same pad state; fresh 120 Hz input needs a separate cadence decision.
5. Which timer/RCNT consumers depend on the existing ratio to VBlank? Can a 120 Hz simulation
   clock be introduced while leaving GS fields, sound and SDK timeout semantics intact?
6. After conversion, can clean Odin builds sustain the needed cadence under full-race load?
   RV4's service-budget targets are requirements, not evidence that this is achievable.

## Read receipts and limitations

Commands used: `git status --short`, `git log -1 --format='%H %s'` in this repo and the
runtime; `cat`/`sed` on the named reports/instructions; targeted `rg -n`/`rg --files` on G and
R; inline read-only Python using `pathlib`, `re`, `struct`, `hashlib` to extract instruction
comments, compute addresses, read ELF program headers/GP/vtable words/constants, and hash E.
No EE-helper index was built: `local/tooling/ee/ee.py` was read and its cache-writing behavior
avoided. No new LSP index or other artifact was written.

The source-read batch encountered a missing guessed path:
`sed: /Users/brad/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/Syscalls/Interrupts.cpp: No such file or directory`.
Per the worker first-failure rule, further source investigation stopped there; this report
uses the already-read syscall wrappers, Dispatcher mappings and scheduler dispatch instead.
The same batch returned the audio constants above. No runtime experiment failed or ran.
Consequently the full interrupt-registration implementation, live race targets and remaining
consumer graph are not claimed audited. The specific scheduling/branch/constant findings
are supported by the cited successful reads; the proposed experiment is future work.

## Orchestrator adoption (2026-09-26)

Adopted rank 1 as **TM1** (observation-only timing tap on bradflix, RV6 §5's brief). Rank 2 (the
three-field rate 120 / dt 1/120 / multiplier 2 probe) waits for TM1's live chain and for RV7's survey of
published SSX 3 fps patches. Ranks 3–4 stay queued behind the 60 Hz service budget work (RV4); rank 5–6
parked as recommended.
