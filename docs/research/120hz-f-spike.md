# F spike: true 120 Hz simulation — kill-first plan

Branch `spike/f-120hz-sim`, worktree `/tmp/ssx3-f120`. Main checkout untouched.
F = double update cadence, halve dt. No interpolation, no reprojection, no
renderer changes in this spike. Motion correctness first; presentation later.

## Kill order (stop at first failure)

1. **2x-update, unchanged dt, unchanged render (desktop).** Re-enter
   `0x8010550C` twice per tick, zero extra renders. Back-to-back 180 s runs,
   window host 145–170 s, `gamecube_schedule_trace.py` on each.
   Kill: `guest_seconds_per_host_second` < ~0.95, or update-pair wall > 8.33 ms.
   Desktop CPUs dwarf the phone — failing here ends F before any dt work.
2. **Time-normalized 30 Hz (half cadence, doubled dt).** Cheap stable direction.
   Enumerates timestep consumers: which systems track guest time vs outliers
   (camera smoothing, trick windows, anim phase, collision, `update_count/60`
   bookkeeping at application+168).
3. **Time-normalized 120 Hz (double cadence, halved dt).** Candidate F behavior;
   same guest-time-parity metrics plus queue/gate health and veto rates.
4. **Regression suite + phase-tagged phone attribution.** Only if 1–3 pass.

Deliberate controls throughout: wrong-control half-cadence/unchanged-dt
(fingerprints cadence-dependent advancement) and render decimation (separates
sim from render effects). Per handoff §02B runbook.

## What the scouts established

- **No update-cadence/dt hook exists.** `native_callback_trace.h` (update
  `0x8010550C` / render `0x8010A4C8` entry-return, bookkeeping-helper skip
  sites, gate counter, view-matrix/frame-end markers) is the only dispatch
  touchpoint; `native_render_schedule.h` / `render_deadline.h` are render-side
  only. F must ADD an update-injection path, ideally behind a new builder mode
  in `tools/gamecube_native_trace.py` (e.g. `--sim-rate`), never in prod sources.
- **Inner hooks unlocated.** `0x8001FB58` (game update), `0x8006AF2C` (view
  update), the application+168 increment site, and the `count/60.0` division
  have no code citation — first disassembly task before halving anything.
  Zero 1/60 or smoother constants in repo code; they live in the DOL.
- **Budget says F is tight.** Phone ordinary update ~3.3–3.5 ms = ~40% of an
  8.33 ms period; update+render ~9–13 ms > one full period. Trial load already
  drops updates to 44/s at 1x cadence. Extra-draw wall 4–9 ms, mostly CPU-busy
  (wall−CPU ~0.03–0.04 ms), final GPU buffer partial only.
- **Compare single-core movie replays only.** `SSX3_MOVIE_PLAY` + guest-XFB-
  arming gives byte-identical world color/depth across runs; dual-core diverges
  within ~3 s and is unusable as a comparator. `compare --strict` is the
  control-flow floor; gameplay gate (distance/speed/airtime/tricks/rail/reset/
  anim-phase at equal GUEST time) is new work. Missing guest-aligned fields:
  sim_step_id, velocity, trick_timer, camera_pose, animation_phase, RNG call
  counts, streaming_flags, camera_cut.
- **First hook to change:** application-update entry/exit in
  `native/diagnostics/native_callback_trace.h`, after locating the app+168
  increment by disassembly. Step 4 (30 Hz) validates the dt path before step 5.

## Stop rules

- Distance-per-guest-second does not halve-and-recover across wrong-control →
  30 Hz: dt path wrong, stop.
- Queue `Full` / readiness-retry storm on doubled updates: scheduling unfit, stop.
- Systematic trick-window / reset-destination / anim-phase drift at parity:
  consumer not normalizable without per-system work — cost and decide, do not
  hand-tune constants globally.

## Token budget (order-of-magnitude, ±2x)

- Phase 1 kill experiment: ~1–2M (one driver flag + desktop runs).
- Phases 2–3 + regression suite: ~8–15M additional.
- Phone attribution + ship gate after: separate, unbudgeted here.

## Phase 1 results (2026-09-15, desktop, PASS on quiet host)

Quiet triple (player3/4 matched drivers, 190 s, back-to-back, load ~2):

| Arm | guest/host (145–170 s) | updates/guest-s | update wall med |
|---|---|---|---|
| 1x baseline | 1.0002 | 59.94 | 2.46 ms |
| 2x updates | 0.9726 (97.2% of base) | 118.35 | pair 5.31 ms (p95 10.31) |
| 0.5x updates | 1.0009 | 59.94 callbacks, 30 Hz executed | 2.4 ms executed, ~0 skipped |

2x holds 97% guest speed — above the 0.95 kill floor and the 90%
calibration line. F survives phase 1 on desktop. Phone headroom is still
open (desktop pair ≈ 5.3 ms vs phone update ≈ 3.4 ms singles), and pair
p95 (10.31 ms) exceeds 8.33 — tail needs attribution before any ship claim.

Bonus finding, corrected — locomotion is FIXED-STEP per update (an early
whole-run read suggested mixed fixed/measured-dt, but that was
trajectory-confounded). In matched windows: in-window distances 2.11x /
0.48x, speeds 1.96x / 0.47x, per-update step constant within 7%. The
binary reads no hardware clock on the update path (the 8 mftb reads in
the DOL sit in three OS/SDK clock helpers at file+0x284438, 0x286a60 and
0x2ad3ac, none of them reached from an update; 1 DEC site in OS code,
MMIO only in OS drivers) and renders never
move the rider — advancement happens only in executed update bodies. The
half driver itself had a real bug en route: the hook observes
post-execution pc, so an armed skip misses its completion and wedges
pending (40 Hz effective, 700 guard trips); fixed by emitting a zero-work
marker row without arming (guard 0, skips 50.0%, executed gaps 33.37 ms).

## Phase 2 results (2026-09-15, desktop)

Disassembly (pinned DOL b92162d6, capstone PPC32-BE; prior doc claims now
carry code citations):

- app+168 increment: `80105be0 lwz r3,0xa8(r31)` / `80105bec addi r0,r3,1`
  / `80105bf0 stw r0,0xa8(r31)` — the only app+168 write in update.
- Game-update virtual chain, exactly as documented: `80105b00 lwz
  r3,0xc(r31)` (app+12) / `80105b04 lwz r12,0x24(r3)` (obj+36) /
  `80105b08 lwz r12,0x10(r12)` (slot+16) / `80105b10 bctrl`, with
  0x8001FB58 sitting in vtable 0x802CDC34+16. No direct callers (virtual
  only, word-wise verified).
- View update 0x8006AF2C confirmed: obj+0x90 virtual slot 0xC
  ("controller") then `bl 0x80069B04` ("reconstruction"); vtable slot at
  0x802D2C54; no direct callers.
- count/60.0 division: render tail `8010abf0 lwz r3,0xa8(r27)` ...
  int→double bit trick ... `8010ac0c lfs f0,-0x6580(r2)` (the 60.0 const
  at 0x803DCEE0) ... `8010ac1c fdivs f1,f1,f0` ... `8010ac20 bl
  0x8015c5a0` (elapsed helper), then count cleared at 0x8010AC34. A
  second identical sequence exists at 0x80109CA8 (other render-flavored
  path, r29 object).
- dt-const census (SDA-resolved): 1/60 has ~209 loads (biggest clusters
  91 in 0x8000xxxx, 40 in 0x8019xxxx-0x801Axxxx, 21-22 in 0x8005xxxx /
  0x8007xxxx-0x800Cxxxx, 10 in 0x8006xxxx view region); 60.0 has ~50
  (render divisor const used only at 0x8010AC0C + 0x80109CB4); 1/30 has
  25 (engine already runs some systems at 30 Hz — mixed-rate precedent).
  Singleton hits may be data misdecoded; clusters are real code.

Time-normalized 30 Hz (combo mode: HALF_CADENCE + DOUBLE_UPDATE —
skip alternates, double survivors, 60 executions/guest-s in pairs):

| Check | Result |
|---|---|
| row pattern | ERSERS… exact; 750 exec + 733 repeats + 749 skips in window |
| guest/host | 1.0007, guard trips 0 |
| in-window distance parity | 51,668 vs baseline 53,389 = 0.968 |
| median speed parity | 2,085 vs 2,209 u/s = 0.94 |

Normalization mechanics VALIDATED: paired execution ≡ baseline for
locomotion within trajectory noise.

## Phase 3a results (2026-09-15, desktop): 120 Hz candidate v0

Const attribution: call-graph BFS from the frame callbacks over direct
edges reaches 1,526 functions but only 44 of 259 dt-const loads — the
engine is heavily virtual (5 indirect calls in update, 18 in render),
so most per-frame const users sit downstream of virtual edges the
static BFS cannot cross. Directly reached users include update callees
0x801046B0, 0x801B2774, 0x80047D4C, 0x800BDD9C and game-update staged
calls (0x800279D0, 0x80193FE4, 0x801ACC8C, 0x801A86C0, 0x801A4BE0).
No hardware-clock dt on the update path (the DOL's 8 mftb reads are all
in OS/SDK clock helpers, none reached from an update; single DEC site is
OS code; MMIO only in 16 OS-driver sites).

Candidate v0 (player6): DOUBLE_UPDATE (120 exec/guest-s) + HALF_DT
one-shot guest-RAM patch (eleven 1/60 floats → 1/120, render divisor
60.0 → 120.0; verify-before-write, aborts on drift; "patched 12
consts" in run log):

| Check | v0 | baseline | unpatched 2x |
|---|---|---|---|
| updates/guest-s | 119.19 | 59.94 | 118.35 |
| guest/host | 0.989 | 1.000 | 0.973 |
| in-window distance | 39,820 (0.75x) | 53,389 | 112,682 (2.11x) |
| median speed | 1,609 u/s | 2,209 | 4,324 |

The patch OVER-corrected: 0.75x game speed instead of 1x. Decomposition:
const-driven integration normalized (that half of the 2.11x is gone),
but fixed-step damping now applies twice per tick (vel *= k per
execution → k^2 per tick), dragging net speed below baseline. Renders
never move the rider, so the slowdown is update-side.

## Phase 3b results (2026-09-15, desktop): damping renormalization

Damping hunt: body-offset mining (offsets changing every update) plus
an x = x*k loopback scan over the 688-function game-update subtree.
Prime find: 0x8002784C, called per rider-element from game update,
scales six +0x718-subobject fields by SDA consts 0.98 / 0.956 /
0.978333 (0x803DB7E8/EC/F0) every tick. (Caveat: the +0x718 base means
these fields sit outside the probe's rider window — the hot-offset
overlap that ranked it was numerically coincidental; the run below is
the real evidence.) The 0.98 const has two more users (0x8002DFD4,
0x800495A4, enclosing functions unidentified — fallout risk noted).

Candidate v1 (player7): v0 patch + sqrt renormalization of the three
factors → in-window distance 0.932x, median speed 0.973x baseline
(from 0.746x / 0.73x). Noise floor from a fresh baseline pair: 3.0%
distance, 2.1% speed run-to-run. (Later movie comparison showed the
free-run 0.97 was regime-lucky — see phase 4.)

## Phase 4 results (2026-09-15, desktop): determinism + comparator

Asset: `det-base-run.dtm` (200 s movie, prod path). Strict dispatch
compare record-vs-replay: 915/915 identical rows, control-flow gate
passed. Rider state-transition prefix identical (76 transitions; length
differs only because host-timed 200 s runs cover slightly different
guest spans — tails, not divergence).

Tool: `tools/gamecube_parity_compare.py` (+ 4 unit tests) aligns update
ticks across arms by ABSOLUTE guest tb (same-movie runs share the boot
epoch; per-run normalization misaligns when a host-window edge falls on
different guest ticks — caught live by a 0% self-check, fixed) and
compares tick-end body hashes. Self-check on two probe replays:
1496/1496 exact. Telemetry agrees to 0.07% on path.

First finding — v1 diverges on the movie: 0% hash parity from tick 0
(expected: two half-steps never bit-match one full step), and
behaviorally v1 runs 2.2x median speed in the movie's braking section
(base decays 2170→174 u/s over the window; v1 stays 710–2151; ratio
grows 1.0→6x across buckets). Double-only (no patch) is worse: 3.7x
speed, erratic shape, endpoint 210% off-path. Two hypotheses died:
input desync is IMPOSSIBLE here (no --route passed anywhere, so riding
sticks stay neutral — consume-per-poll confirmed in Movie.cpp but
neutral == neutral at any rate) and render-side const damage is
confined (only 0x8014AAD0 uses 1/60 render-side, 2 loads, const
exclusive to it). Standing hypothesis: fixed-step ACCELERATION
(additive vel terms, no dt const) applies 2x per tick — v1 normalized
drag but not accel, and the braking section is accel-dominated while
the free-run cruise section was drag-dominated. Next: accel-site hunt
(additive writers to speed-relevant fields) → candidate v2, measured by
movie drift rate.

Superseded contended runs (load 40–85, both arms 0.27 guest/host):

Driver: `SSX_NATIVE_DOUBLE_UPDATE=1` re-enters `0x8010550C` once per
ordinary update in host window 140–175 s when rider state is stable across
the callback. (First gate `b.state==0`, copied from the render path, never
fires while riding — in-window states are 6/13; state-0 rows only appear
after 175 s. Fixed to `update.before.state==b.state`, 99.7% coverage.)
`summarize` counts `update_repeats`/`verified_update_repeats` and no longer
lets update repeats pollute render-pair counters. Unit tests: 10 + 8 pass.

Player `local/research/120hz/f-phase1-player2` (matched binary, both arms),
190 s each, riding observed, zero resets, `gc-gari-027`:

| Arm | Profile | guest/host (145–170 s) | updates/guest-s | update CPU med |
|---|---|---|---|---|
| 1x baseline | f-p1-base3 | 0.267 | 59.93 | 7.60 ms |
| 2x updates | f-p1-2x2 | 0.278 | 118.87 | 7.47 + 7.82 ms (pair 15.37) |

583/583 update repeats verified with ordinary predecessors. Doubling worked
mechanically and the game stayed stable — but host load was 40–85 (another
agent compiling + running emulation concurrently), so both arms ran at 27%
guest speed and the 0.95 kill floor is untestable from these runs. Note the
earlier quieter baseline hit 0.87 guest/host with 4.1 ms wall medians, and
one baseline attempt flaked entirely (menu mistiming under load, rejected by
the riding gate). No relative slowdown from doubling was observed (0.278 vs
0.267), but under contention that comparison is vacuous, not a pass.

Reproducibility note (same 1x config, two contention regimes): the quieter
baseline ran guest/host 0.87 with update/render CPU medians 3.23/3.64 ms,
vs 0.27 and 7.60/27.52 ms under load. Thread-CPU inflates 2–7x under
contention (clocks/cache), so neither wall nor CPU compares across regimes —
arms must run back-to-back on a quiet host. Directional budget read from the
quiet run: update-pair ≈ 6.5 ms CPU vs the 8.33 ms period, consistent with
phone update ≈ 3.4 ms. Rider path length agreed within 5% across runs
(263k vs 275k units), supporting guest-aligned distance as a regression
signal. This tightens but does not replace the quiet 2x measurement.

Wrong-control driver (ready, unrun): `SSX_NATIVE_HALF_CADENCE=1` skips every
other in-window update (entry jumps to return, same dt), marked with a new
`skipped_update` trace field counted by `summarize` as `skipped_updates`.
Aborts if combined with `DOUBLE_UPDATE`. Player
`local/research/120hz/f-phase1-player3` carries both drivers (matched binary
for all three arms). Expectation: distance-per-guest-second halves vs
baseline, fingerprinting cadence-dependent advancement; also validates the
comparison harness before any dt work.

Next: run the triple back-to-back on a quiet machine (load < ~10), then
apply the kill criterion (guest/host < ~0.95) and the 90%/75% calibration:

```
P=/tmp/ssx3-f120/local/research/120hz
G=/tmp/ssx3-f120/local/game/gc-gari-027
env -u SSX_NATIVE_DOUBLE_UPDATE SSX_NATIVE_PROBE=$P/f-base3-events.jsonl \
  python3 $P/f-phase1-player3/course_check.py --game $G \
  --profile f-p1-base4 --output $P/f-base3-run --seconds 190
env SSX_NATIVE_DOUBLE_UPDATE=1 SSX_NATIVE_PROBE=$P/f-2x3-events.jsonl \
  python3 $P/f-phase1-player3/course_check.py --game $G \
  --profile f-p1-2x3 --output $P/f-2x3-run --seconds 190
env SSX_NATIVE_HALF_CADENCE=1 SSX_NATIVE_PROBE=$P/f-half3-events.jsonl \
  python3 $P/f-phase1-player3/course_check.py --game $G \
  --profile f-p1-half3 --output $P/f-half3-run --seconds 190
python3 tools/gamecube_schedule_trace.py $P/f-base3-events.jsonl --start 145 --end 170
python3 tools/gamecube_schedule_trace.py $P/f-2x3-events.jsonl --start 145 --end 170
```

## Phase 3b-c results (2026-09-15, desktop): v2 gate + bifurcation

v2 hypothesis: the +696 inflow word runs 1.97x in v1 (blend applied twice
per tick), fed by 0x8002DE04 under 0x80027B08. v2 entry-gate skips
0x8002DE04 in repeat updates. Gate ENGAGED (onset +696 ratio 1.97x→1.0x)
but movie drift did not improve: whole-run rider path v2b 1.16x / v1
0.93x base (det-*runs, same DTM). Direction says the gated blend is
net-BRAKING (removing it lengthens path), so the accel is elsewhere —
but see the variance caveat below: ±15% build/rerun swings in 2x modes
make "worsened" a weak claim. v2 as a candidate is dead; the gate was a
useful negative.

Eliminated: the 0x8002AD44 velocity governor (scales all four 0x100–0x10C
words by const-ratio k when over ~251 u/s). v1's sqrt patch moves k
0.99929→0.99970 — a 0.7%/s bleed change, two orders below the drift.

Main result — drift is BIFURCATION, not uniform rate error, measured
on the tick-end body-word grid (basedump vs v1dump, order-aligned;
median |Δtb| 3 units vs 675675-unit tick steps, so alignment is exact).
Ticks 0–2125: v1 ≡ base BIT-EXACTLY (all 512 words, 2126 ticks). Tick
2126 = first doubled tick (host window opens at wall 140 s). Tick-end
epsilon there: position 3 ulp, velocity +5.8e-4 systematic (relative),
plus five integer counters (body+0x30 stride 0x20) incrementing twice.
Velocity excess grows ~+6e-4/doubled-tick monotonically (5.6% by tick
2144) — v1 UNDER-BRAKES in state 8, a real unnormalized term, not
rounding noise. Counters run +2/tick vs +1; a mod-6-gated periodic
(5-elem array, body+0x24/0x28 stride 0x20, float accumulators) fires
every 3 ticks in v1 vs every 6 in base (noffs oscillation 74/84).
First branch flip at tick 2129 (same state, different write sets),
cascading ~300 ticks later into the early state-5 exit (48.6 vs 48.9 s)
and a different line through the 43–52 s cluster. Per-state speeds
match (~1.1x). Spatial separation base-vs-v1: <100 units at 40 s, 1349
at 50 s, 19k at 90 s. This reconciles phase 4's local 2.2x braking
median with whole-run ~1x: v1 takes a less-braked LINE, not 2x speed.

REGIME CORRECTION (2026-09-15 late): the repeat driver only fires in
host window 140–175 s AND the HALF_DT const patch is one-shot with no
restore — so every HALF_DT arm has THREE regimes: ticks 0–2125
identical 1x; 2126–4223 true v1 (98.6% repeat coverage); 4224+ HALF
SPEED (1x cadence, dt/2 consts). Behavioral proof: v1dump median speed
2205 u/s in the 10 s before close (rider-t 78.8 s) → 1083 u/s after
(0.49x; base control shows no such step). Whole-run ratios therefore
MIX all three regimes and must not be quoted as v1 drift: the honest
comparison point is window close (rider-t ~79 s), where time-aligned
cumulative path reads 2x 2.14x, v1 1.24x, v1dump 1.61x, v2 1.47x,
v2b 1.71x (t=75 s; post-close ratios are half-speed contaminated, and
the late "rejoin" dip is v1 slowing down, not lines rejoining — the 2x
arm's tail is clean since it never patches consts). The v2b-vs-v1
"gate worsened drift" claim HOLDS on the clean window (1.71x vs 1.24x),
but so does the variance caveat, more strongly (v1 vs v1dump: 1.24x vs
1.61x — 30% apart on identical mode). Rerun pairs (same binary, same
movie, same window) are the only way to split gate effect from noise.

Variance warning (phase 4 prerequisite): v1 vs v1dump differ 30% on
the clean window (1.24x vs 1.61x at t=75 s), v2 vs v2b similarly, but
base vs basedump only 1.8% whole-run — 2x modes are an order more
timing/build sensitive (different player builds + probe load + host-timed
window edges falling on different guest ticks flip wall-clock-adjacent
branches). Same-config rerun pairs (det-base2, det-v1r — same binaries,
same movie, same window) fired 2026-09-15 20:23 to measure the 2x noise
floor. Base pair landed first: base2/base whole-run path 1.0346x, time-
aligned separation ≤62 units through 75 s (same line; 225 max at 90 s),
state sequences identical for all 75 of base's transitions (base2 runs 5
extra tail transitions — host-timed 200 s covers slightly different guest
spans, as predicted in phase 4). 1x noise floor ≈ 0% on common span, ~3%
whole-run from tail-span difference. v1 pair (same player7 binary, same
movie, same host window): v1r/v1 whole-run path 1.209x, 1.323x on the
clean window (t=75 s; v1/base 1.24x vs v1r/base 1.64x). Separation 0
through 40 s, 197 at 50 s, 10k at 60 s, 29k at 75 s — different lines
from the same state path (43-state common prefix, then same states,
different positions). Repeat sets differ slightly (2047 vs 2065; window
edges identical in wall, guest ticks differ). 2x noise floor ≈ ±30%: AS
BIG AS THE SIGNAL. Significance reckoning: v1-vs-v2b clean-window gaps
(1.24x vs 1.71x) sit INSIDE rerun noise — the "gate worsened drift"
claim is NOT statistically supported (nor refuted); only these survive:
(a) 1x determinism, (b) unnormalized-2x drift (2.14x, far outside noise),
(c) single-run mechanism facts (tick-2126 epsilon, counters/periodic 2x,
+6e-4/tick systematic), (d) the half-speed tail (0.49x + mechanism).
Comparing 2x candidates requires either guest-timed windows (kill the
host-timing seed) or N-run distributions, not single pairs. Next after that: (a) window-from-tick-0 +
const-restore driver (new player build) for clean full-run experiments
and a cruise-state systematic check — current data has NO doubled ticks
outside state 8, so state-dependence of the +6e-4/tick term is untested;
(b) trap runs (SSX_NATIVE_WATCH/TRAP) on body+0x24/0x30 to ID the
periodic/counter code sites and their gameplay role; (c) hunt the
state-8 unnormalized velocity term (+6e-4/tick signature) — the standing
fixed-step-accel hypothesis is REVIVED in weakened form: not a global
2x term (per-state speeds match to ~1.1x) but a state-8-specific
under-braking of ~6e-4/tick, plus integer bookkeeping (counters,
mod-6 periodic) running at 2x rate. REVIEW NOTE: the whole-run path
table in the pre-correction paragraph above (0.93x/1.09x/...) is
three-regime mixture — superseded by the clean-window numbers.

Numbers caveat: a compaction summary quoted whole-run "1.53x/2.23x,
2.54x/3.82x" for v1/v2 — NOT reproduced from rider.jsonl (all det pairs
≤1.16x cumulative; 2.2x exists only as the phase-4 braking-window
median). Likely a lost sub-window metric; treat as unverified.

## Phase 3d results (2026-09-15, desktop): guest window + determinism

Driver (players 14–16, working header): SSX_NATIVE_GUEST_WINDOW
replaces the host-clock window with guest-timed edges — arms on the
first stable update that moves the rider, engages (consts patch)
SSX_NATIVE_WINDOW_SKIP ordinary ticks later, repeats start the next
tick (no 1.5x transitional tick; the arming/engaging ticks run 1x
base-identical), closes after SSX_NATIVE_WINDOW_TICKS doubled ticks
and restores consts under the same drift check. SSX_NATIVE_SPEED_GATE
re-arms the v2 0x8002DE04 skip (previously implied by HALF_DT — a flaw
that contaminated gw1; now off by default).
SSX_NATIVE_WATCH_OFFS="0x24,..." logs pc/lr/body of in-window
rider-word changers (cap 500). Validation (gw1, 4000-tick window from
riding start): exactly 4000 repeats, armed/engaged/closed ×1, zero
drift, no movie desync, post-close speeds full (1910→2320 u/s —
restore works, no half-speed tail). All edges land on identical guest
ticks across runs by construction (pre-engage prefix is base-identical;
gw3's SKIP=40 landed first-doubled-tick at exactly the calibrated
events idx 1167).

Determinism (the payoff): gw4 (player15+gate) vs gw1 (player14+gate)
whole-run path 0.9973x, separation ≤368 units through 100 s, state
sequences IDENTICAL 113/113 — different binaries, identical
trajectories. Guest edges kill the ±30% host-window noise completely;
it was all window-edge seed. Gate isolation (same binary ±gate):
gw4/gw2 = 1.138x path, separating from t=40 s with identical curves in
both builds — the v2 gate effect (+14%, removes braking, first bite at
the first state-8 repeats) is now deterministically reproduced and
statistically SUPPORTED, superseding the 3b-c "not supported" verdict
(which still holds for host-window single pairs).

Corrections to 3b-c: (a) body+0x100 (word64) is NOT velocity — true
speed (Δpos/tick) composes to ±1e-3 (endpoint-epsilon noise) in state
8; word64 is carve-like (bit-frozen in idle/cruise, evolves only in
state 8). The "+6e-4/tick under-braking" is a phase-shifted bounded
dynamic (rises +0.06%→+8.4% then sign-flips through a zero-crossing
landing on different ticks), not runaway. (b) +696 inflow is
state-dependent: 1.97x only in state 8; 1.00x in states 6/0 with or
without the gate (gw2/gw3, gate off) — the blend re-applies in repeats
only in state 8, which is also the only place the gate can bite. (c)
Pre-ride (state 6) motion is sparse and scripted: doubling perturbs it
immediately (+30% first doubled tick, extra move at +7) — a
counter-gated signature that shifts start-of-cruise initial conditions.
(d) Cruise composes: gw3's window opens mid state-0-entry; the first
doubled tick flips 6→0 one tick EARLY (integer-seed smoking gun —
float epsilon cannot flip tick 0 from identical state); age-aligned
(+1 tick) speed deficit −0.87% DECAYS to −0.38% over 80 ticks
(transient-shape artifact converging, not a rate error) and w64 shows
bounded ±1% wobble (phase-shifted oscillation).

Standing model: float physics composes everywhere (bounded phase
jitter); the only true-2x divergences are INTEGER bookkeeping
(counters +2/tick, mod-6 periodic firing every 3 ticks, script phase),
which gate transitions/periodics/scripts and seed the flips (±1-tick
early firings cascade into line changes at speed). v3 direction:
once-per-tick integer normalization (gate counter/periodic/script
updates to first-body-only, mirroring the speed gate) + accept float
jitter.

Trap results (gw5, WATCH_OFFS=0x24/0x30/0x100/0x2B8, 120-tick window,
500-line cap): +696 control fires in caller 0x80027B08's frame both
bodies (validates the trap; pc granularity is per-dispatch, so sites
are neighborhoods, not exact stores). Counter 0x30: both bodies at
0x8001F400 (a pointer-chain getter — notice point, not the store) and
0x801D9DD0-prologue, callers 0x80040F50/68 — but NO lwz/addi-1/stw
idiom exists at +0x30 anywhere: all five counters are ALWAYS EQUAL
(0x4a1…), i.e. a GLOBAL tick counter STAMPED into each element per
update (timestamp pattern). v3 must gate the global's increment, not
five local ones (exact increment site still open — scan the stamp loop
near 0x80040xxx for SDA-load→stw-0x10). Periodic 0x24: body1 ONLY
(20/0) at 0x802BEDB4 — it does NOT double-execute; its 2x rate comes
from reading the 2x global counter (mod gate), so fixing the counter
fixes the periodic too (single fix point). Carve 0x100: both bodies at
lr=0x8002AD48 (governor block). CORRECTIONS (adversarial review,
September 16, verified): r2 is the canonical 0x803E3460 (DOL
section 0x803DB460+0x8000), not 0x803E37E4 by consensus — the old
value cannot reach const 0x803DB490. And k is COMPUTED (k≈1/f1
with div-guard; FDIVs in the callee), not the E8/F0 const — so the
old k²-vs-k sign contradiction (predicted −7e-4/tick vs measured
+5.8e-4) was a wrong-k-model artifact, and the governor
double-applies unnormalized (~3%/window), making it a v2-style
renorm candidate rather than a replay item; the state-8 0x100
writer question is separately closed by the gate-1 trap
(phase-routed float physics, no integer writer).
Also seen: early-window 0x100 writers at 0x80007xxx (start-gate
setup, both bodies — the +30% script perturbation's likely source).

## Phase 3e results (2026-09-15, desktop): v3 integer replay

v3 (SSX_NATIVE_COUNTER_RESTORE, player17): saves the race tick
counter at each in-window ordinary entry, restores it at repeat entry
so both halves observe and advance the same tick (aborts unless the
first half advanced exactly +1). The counter address resolves through
the 0x8001F400 getter chain (-22632(r13)→116→12→8); first restores read
186, 187… — exactly the predicted global values. gw6 (4000-tick early
window): suite counter_rate PASS (max_step 2→1), zero model aborts —
mechanically perfect. But the early flip (+20, same transition) and
drift (1.58x @75 s vs 1.61x) did NOT move: the epsilon growth curve
shows a whole subsystem firing 8 ticks early (84 vs 5 words) — the
signature of MOVIE-INPUT DESYNC (consume-per-poll eats timed
start-button inputs at 2x; shift +1/doubled-tick). The early window is
desync-poisoned; v3's effect is unmeasurable there. Product
requirement (merge plan): consume-per-tick input latching — both
halves must observe the same latched inputs. Spike constraint until
then: windows open post-race-start (all-neutral sticks).

gw7 (v3, mid-ride window SKIP=999/TICKS=300, first-doubled exactly
2126): periodic NEVER fires (vs every-6 base, every-3 v1) and the
branch flip moves EARLIER (+0 vs +3) — restoring only the global
inverts mid-tick comparisons (global < elem during body2), breaking
comparison gates. +696 inflow drops to 1.02x (vs 1.97x): the blend is
tick-driven (pure function of counter phase — body2 recomputes the
same output), so v3 accidentally replicates the v2 gate's effect.
Lesson: compensation must replay ALL integer state, and per-tick
(either-half) is the correct branch comparison — half-2-vs-full
changeset diffs are expected artifacts, not flips.

v3b (player18): full integer replay — race counter, five stamps,
app+168 flag, 48 RNG bytes restored at repeat entry. gw8 (same
mid-ride window): periodic back IN PHASE with base (every-6 H pattern
identical), +696 1.02x, suite PASS — integer bookkeeping SOLVED, no
residual. But first S1 flip at +97 (tick 2223, 8→0) IDENTICAL to v1dump
(same tick, same transition) — the flip is integer-independent, i.e.
FLOAT-DRIVEN (the epsilon series is identical across integer
treatments and crosses the exit threshold deterministically). F's
ceiling is therefore statistical parity, not trajectory parity:
integers exact, inputs latched (product), floats bounded-jitter with
threshold flips.

## F verdict (spike decision): CONDITIONAL-GO to mainline bias trial

gw9 (v3b, SKIP=999, 3513 doubled mid-ride ticks — run ended 87 short of
3600): suite counter_rate PASS; drift vs base 1.04x@50 s, 1.14x@60 s,
1.64x@75 s, 1.48x@90 s, 1.30x@100 s — essentially IDENTICAL to v1dump
(1.04x/1.10x/1.61x/1.35x/1.13x; late gap is v1dump's half-speed tail,
not v3b regression). Integer normalization did not move the drift:
the +97 flip (8→0 exit) is float-driven and identical across integer
treatments, and one such flip cascades into a 64% longer line. Per-state
speeds still match (~1.1x); the rider rides healthily (1016 samples,
no stuck/crash) on a carvier line at the same pace. CONCLUSION: F can
never hold a trajectory (float epsilon flips some threshold within
~100 doubled ticks; butterfly does the rest) — the only viable F bar
is STATISTICAL: rate parity (per-state speeds) + line plausibility (no
pathology, tricks work) + UNBIASED across movies. The multi-movie bias
battery (≥3 movies: record more DTMs, run v3b on each, require |mean
drift| small with mixed signs) is THE F gate — post-merge mainline
work, using the Phase 4a suite (drift report) on each movie. Desktop
pair CPU (gw9 in-window, probe overhead included): med 4.51 ms, p90
5.03 ms, max 8.94 ms vs 1.69 ms ordinary singles — production drops
hashing/writes from both bodies, so the phone projection stands at
≈6.6–7.0 ms vs 8.33 ms (restore itself is ~20 RAM accesses —
immeasurable). If the bias battery shows systematic handling change
(always longer/shorter, regime avoidance), F is NO-GO without deeper
(float-compositional) work; if unbiased, F is GO with the live phone
trial as the last gate.

## Phase 4a: regression battery (tool + tests, merged)

tools/gamecube_f_regression.py + tests/test_gamecube_f_regression.py
(10 tests): counter_rate (tick stamp ≤+1/ordinary-tick; creation jump
allowed), repeat_count (exact N with --expect-repeats), restore (post-
vs pre-close median speed within --restore-band 2x), drift
(time-aligned cumulative path deciles vs baseline, --max-drift assert).
Calibrated on real traces: base PASS, v1 FAIL (max_step 2 from tick
2127), gw6/gw8/gw9 PASS (gw9: 3513/3600 repeats — run ended first, not
a driver miss). Full file: 27/27 green with the native-trace and
parity suites. --max-drift stays report-only by default: a single
movie cannot set the bound (v3b reads 1.64x worst on det — a different
valid line, not a rate error); the bound comes from the multi-movie
bias battery (post-merge). Merge gate = counter_rate + repeat_count +
restore PASS (deterministic invariants); drift REPORTED per movie.

## Phase 4b: phone attribution (trial shipped; first live fire in progress)

The F phone trial is implemented on main: `NativeTrial::Kind::{Smoothing,F}`
in native/diagnostics/trial_control.h, trial-armed v3b drivers (no
environment) in native/diagnostics/native_callback_trace.h, kind-gated
schedule/interpolation in native_render_schedule.h and
native_pose_interpolation.h, a Try 120Hz sim menu entry plus `-ssxFAt` in
native/ios, and `--f-at` in tools/mobile_gamecube.py. F renders normally
through production double-buffering with production idle waits; smoothing
keeps the XFB alias, extra renders and high-refresh hint. Const patch on the
first live F update, restore before finish, graceful (limited + cancel)
drift handling, no display-rate change. Analytical projection
(desktop pair CPU × phone singles): desktop ordinary+repeat ≈ 5.3–6.5
ms CPU (probe overhead included; production drops hashing/writes);
phone ordinary update ≈ 3.3–3.5 ms (prior trials) → projected phone
pair ≈ 6.6–7.0 ms vs the 8.33 ms period, before render/system — tight
but plausible; trial load already drops 1x updates to 44/s, so margin
is thin and the live trial decides. Desktop pair CPU for the exact
projection: recompute from gw9's in-window cpu_duration_ms
(ordinary+repeat) when it lands.
First live fire (2026-09-15 night, iPhone 16 Pro Max, single-core to match
desktop methodology): snow-jam-smoke.json with `--f-at 155`. 533/534 updates
doubled over 10.0 s, 15 consts patched and restored, zero drift/aborts,
thermal nominal; the guard correctly ended it at the 10 s grace on speed
(0.97→0.82, long 0.819). Pair CPU med 5.12 ms (ordinary 3.02 + repeat 2.06,
p95 5.92) fits the period, but render med 12.25 ms at the saved 3x internal
dominates — the binding constraint is render, not the doubled update. Speed
recovered to 1.00 within 5 s of restore (no half-speed tail). A 1x-internal
run is still needed to isolate F update headroom. Never use the simulator —
its timing is unrepresentative. Attribution is update-pair cpu_duration_ms
from native-trial.jsonl plus metric speed/fps/thermal rows; the always-on
callback timer stays quiet during trials by design. PASS = pair + render +
system < 8.33 ms sustained with no readiness/queue regressions.

Watch-report from that run, both checked against the trace: (1) the "late
start" is stock script behavior, not F — both race starts ran with no trial
active and the script gives zero launch input (menu A presses only), so the
rider coasts while AI sprints. F has still never covered a countdown→GO
anywhere; an `--f-at` over the start is the open test. (2) No crash occurred
under F in the window (states 0/5 only, no stalls), so "tumbling 2x" is no
controlled crash comparison — but it is consistent with unnormalized
per-body consumers running 2x/tick against a world dragged to 0.82x (exact
2:1 relative contrast), and crash-under-F is genuinely uncovered: desktop
movies diverge before their crashes (base crashes, v3b takes a clean line),
and the v3 replay set covers only the race counter, five stamps, app+168
and RNG. Crash/state-timer coverage is the next desktop work.

Second live fire (same night, manual play, dual-core, 3x): 1770 doubled
over ~30 s before the guard limited on 0.879 speed — 3x the single-core
trial length, still render-bound. Three rails ridden under F (1.28/5.01/
0.39 s, state 7 = grind inferred from 0→7 mount / 7→4→5 dismount) show
speeds in the ordinary range (~2364 vs ~2572 u/s) — no F rail-speed effect
in this sample; one F rail ended in a crash (7→4→5→8→9), single sample,
unattributed. Back-to-back trials in one runtime died instantly (stale
schedule epoch — fixed, with an F-first lifecycle test). Separately, the
run's 40% zone dips (fps 57.5, audio underruns) are heavy-vertex load
(190–234 MB/s vertex bytes, render ~12 ms, primitives flat, software
vertex decode) with the F trial long over — a vertex-pipeline issue, not
an F issue, and dual-core did not cover it.

## Mainline merge plan (spike/f-120hz-sim → main)

Do NOT merge: local/ (players, runs, reports — gitignored build/run
artifacts; reproducers rebuild via the tool), third_party/ (untracked
local vendor drop; main ignores it via .git/info/exclude — leave alone).
Proposed merge (after the v3 verdict + suite calibration below):
TRACKED EDITS: native/diagnostics/native_callback_trace.h (all F
drivers; research-only header, inert unless env-armed),
tools/gamecube_native_trace.py (flag docs + update-repeat summarize),
tests/test_gamecube_native_trace.py (repeat/skip summarize tests).
NEW: docs/research/120hz-f-spike.md (this file),
tools/gamecube_parity_compare.py + tests/test_gamecube_parity_compare.py
(tick-end body-hash comparator), tools/gamecube_f_regression.py +
tests/test_gamecube_f_regression.py (Phase 4a battery: counter rate,
repeat count, restore band, drift report). Pre-merge gate: full pytest
green + battery counter_rate/repeat_count/restore PASS on a base trace
and on the v3 trace (drift report-only; the bound comes from the
post-merge multi-movie bias battery). Suite state 2026-09-15: 529
passed, 3 skipped; test_native_float_module_spike's private-paths test
is worktree-path-sensitive (hardcodes the main-checkout path) and
passes on main — not F-related, leave it. Post-merge mainline work, in
order: (1) multi-movie bias battery (THE F gate — §F verdict),
(2) consume-per-tick input latching (product requirement — windows must
currently open post-race-start), (3) live F phone trial (§Phase 4b
runbook), (4) production 120 Hz mode without probe scaffolding.

## Bias battery results (overnight, post-merge)

Four movies (det-base + rec2/3/4, same course, naturally divergent
lines: endpoints 14–47k units apart), one matched probe player, base +
v3b (SKIP=999/TICKS=300) replays each. Divergence starts at the first
doubled tick in all four (flip == engage: float epsilon, then
butterfly cascade — consistent mechanism). End displacement decomposed
against each movie's base heading:

| movie | flip | along | lateral | path F/B | note |
|---|---|---|---|---|---|
| det-base | 2126 | +39,754 | −6,759 | 1.130 | crash-confounded: base crashed @4676, F clean |
| rec2 | 1859 | −1,355 | +1,689 | 1.010 | clean |
| rec3 | 2105 | +4,493 | −1,636 | 1.018 | clean |
| rec4 | 2128 | +28,750 | −2,642 | 1.089 | clean, no hazards either arm |

Lateral (the bias axis): signs mixed, mean over the three clean pairs
−863 units (<1% of ~100k-unit runs). Along-track: mixed signs, cascade
scale varies (rec4 +28k crash-free both arms — terrain cascade, not
drift; det-base +40k is crash-miss). Path ratios ≥1 throughout (F
travels farther — carvier lines, consistent with v3b in-window
findings). Crash rate 1 base vs 0 F (thin, noted not concluded).
Verdict: PASS-leaning — no systematic pull detected, magnitudes small,
mechanism consistent. n=3 clean is thin and all one course; strengthen
opportunistically, not as a blocker. Repro: det-rec{2,3,4}.dtm +
/tmp/battery.sh + /tmp/battery_analysis.py (scratch; rerun via the
crash-player recipe above).

## Crash/state-timer coverage (desktop, gate 1 closed September 16)

Convention: 0-based update-row indices; u = ordinary tick, r =
file row (repeats interleave). Adversarially reviewed same day;
all review findings below were independently re-verified.

Reset sequencer (state 9, crash-player pair): base entry r4676
(5→9) → exit r4717 (9→4), envelope 41; F entry r5059 rep=1
(0→9, SECOND HALF of u4784 — mid-tick entry) → exit r5140
(u4825), envelope 41 = 41 EXACT — matched, not 2x. The mid-reset
phase event: base r4696 (+20 entry/+21 exit), F r5100 (u4805:
+21/+20) — a genuine 1-tick residual under every alignment, so
the phase gate has a non-counter input (float threshold or
half-parity artifact); the envelope is counter-exact. Entry
one-shots fire once per transition (r5061 doesn't refire r5060's
set — no double-fire at entry), but 484/664/676 are
transition/event one-shots, NOT crash-only (whole-file base
7/3/3, F 18/14/14: tumble entry/exit, settle, pre-ride, cruise),
and F fires them at ~11x the base cruise rate in-window (open:
line-divergence vs spurious setup). The phase follow-up subset
(36/40/68/…) refires in the repeat half — sub-tick smear. App
side: only the +168 flag, always 0→1 (confirmed; 0/600 repeats
touch app). Body no-countdown is offsets-level only (values
unseen; only reset-correlated per-tick word is float 696).
Caveat: the two crashes differ (5→9 vs 0→9, ~110 ticks apart) —
cross-context, n=1.

Tumble (state 8) under F, first coverage (tumble-f run, det-base,
SKIP=712/TICKS=150 over 0-based rows 1839–2141: 153 ordinary +
150 repeats): entry EXACT u1852 both arms, same 0→4→5→8 path
(F's 0→4 lands in u1850's repeat half — same tick, second half),
no double-transition; the no-repeat-on-unstable rule verified
both directions over all 153 in-window ticks. Exit +2 (u1956 vs
u1954, 2%) — float-threshold-mediated, the only viable class:
skip-delay is directionally ruled out (skips don't perturb the
counter trajectory, and per-body counting would exit F earlier,
but F is later). Post-window butterfly confirmed exactly (F
rail-mount u2010 post-close; base 0→3/3→8 later). Pre-window
determinism holds (states match, hashes identical through the
engage tick, first flip at the first doubled tick = engage+1).
F's exit write set = base's +664/676/680 (3/100 words,
pose-driven).

0x100 trap over the tumble (500 lines; joint WATCH↔events walk
via tag transitions replaces the unsafe line-count thirds): the
governor site is silent across the WHOLE tumble (u1850–1952 incl.
margins vs tumble u1852–1956; skip-merge ±1) and active in
cruise on both sides — governor is state-0-only, tumble sites
tumble-exclusive. Cap hit ≈u1963, ~29 ticks before close; exit
rows merge. Two write classes, not "LSB jitter": float-recompute
(8002acf4 med 43K ULP, governor med 284K ULP) and ±1–2 ULP
small-evolution (215+ lines). WATCH pcs are lag/observation
points (callee-entry/post-return thunks), not stores: 2
writer-pairs × lag points = the 10 sites. Disassembly (review;
structurally corroborated: FDIVs in the callee, float-op
writers, zero integer ALU on 0x100 data) confirms no integer
writer statically — stronger than offsets reasoning. Governor
recategorized: k is COMPUTED (k≈1/f1 with div-guard), not the
E8/F0 const (§3b attribution corrected), and double-applies
unnormalized (~3%/window — F-ceiling-harmless, but a v2-style
RENORM candidate, not replay). §3d r2 corrected to the canonical
0x803E3460 (DOL section 0x803DB460+0x8000; the old 0x803E37E4
cannot reach const 0x803DB490). Residual: router integer flags
unreplayed (n=1 coverage).

Pair tail (headroom backlog 5, crash-f window, all 600 pairs):
CPU med 4.13 / p95 4.79 / max 5.35 ms, wall med 4.14 / p95 4.85
/ max 7.90 ms, zero over 8.33. Stalls are repeat-half-only
(ordinary max wall−cpu gap 0.048 ms vs 3.44 repeat) —
preemption/quantum on the 2nd half (Emit I/O not ruled out);
burst-clustered early+late with a 260-tick mid-gap, not spread;
state-0 for the top 5, mixed below (15/5 in top 20). CPU-tail
and wall-tail disjoint. The Phase-1 wall p95 10.31 does not
reproduce in the crash-player window (max 7.90): desktop tail
is host-side, not pair-work. Ship tail risk moves to phone-side
measurement.

Gate (1) verdict: CLOSED with accepted risks — (i) same-context
reset replication to ID the phase gate's non-counter input,
(ii) 484/664/676 cruise-rate attribution, (iii) governor
renorm-vs-accept decision, (iv) router-flag coverage beyond one
tumble. Next gate: (2) consume-per-tick input latching.

## Gate 2 scoping: input latching is research tooling, not product (September 16)

Desync mechanism confirmed in vendor source: PlayController
advances m_current_byte on EVERY SI poll (Movie.cpp), and the game
polls ~2x/VI (~117/s over the 200 s runs) — so doubled updates
consume the DTM stream 2x and post-window inputs shift. But all
four battery movies carry exactly neutral sticks in all ~24k
frames, and buttons are menu/briefing-only: the last cluster is
state-6 A presses (≈ rows 817–841), riding starts at row 1168,
and zero input frames vary from 1168 to movie end. Every F window
plus all post-window regions consumed byte-identical neutral
frames — body1/body2 inputs identical, post-window shift landing
on identical frames — so the input-drift confound is ZERO for
every F result to date, and flip==engage stands as float epsilon.

Live/phone inputs need no latch either: natural re-poll is already
correct (consumed edges are consumed once, matching stock; held
levels are identical across halves; a tap landing between halves
registers in the same tick — half-tick-faster response, not loss).
Latching live inputs would DOUBLE-fire consumed edges. No shipped
input-path change is required.

Remaining gate-2 work is desktop research tooling only and does
NOT block phone/render progress: movie-stream gating (repeat-half
polls re-serve the current frame without advancing) to unblock
early/menu-window measurement — v3's early-window effect is still
desync-poisoned and unmeasurable. Design: a shared repeat-half
flag set by the probe around update re-entry plus a vendor-patch
branch in PlayController; inert unless doubling, phone unaffected
(no movie there). Note the build cost: the probe.o single-TU
trick does not cover Movie.cpp, so gating needs a vendor core
rebuild — or a probe-TU-only alternative.

## Gate 4a desktop: mid-tick draws work, the queue evicts (September 16)

New probe mode SSX_NATIVE_INTERLEAVE_RENDER (research header only,
env-gated, no trial branch): each doubled tick runs body1 →
mid-tick draw → body2 → ordinary draw, with the +1 counter check
at body1 completion and the integer restore deferred to body2
dispatch so the mid-tick draw observes the consistent post-body1
snapshot. Rows carry interleaved=1; the analyzer excludes them
from ordinary repeat pairing (+2 tests). First run (det-base,
clean riding, SKIP=1946/TICKS=60): 60/60 mid-tick draws complete
the full scene path (result=1, view+frame-end) on post-body1
state, zero wedges/aborts, pre-window determinism intact
(3074/3074 states, flip at 3073 = engage).

But the game's single-slot graphics queue cannot drain 2
draws/tick: all 59 subsequent ordinary draws are REJECTED
(result=0, gate not ready, no scene traversal) — 56 dropped, 4
retried-and-accepted at ~12-tick queue-depth periods. Net
presentation over the window is ~60 Hz of HALF-STALE frames
(post-body1 states drawn; post-body2 computed but never drawn).
Back-to-back "render every update" therefore does NOT yield 120
Hz presentation on this queue — the end architecture must be
VI-paced with a 2-deep queue (headroom backlog 10) or the
smoothing/XFB presentation path. Open question carried to the
phone: whether smoothing extra draws also evict ordinaries
(answerable from present.csv presented/s in existing trial data).
ANSWERED same day from the manual smoothing run (274 extras over
8.5 s): 783 displays in the trial window = ~60/s ordinaries + ~32/s
extras, EXACTLY additive — every extra draw presents, zero
eviction on the phone XFB/high-refresh path. Desktop eviction is
a desktop-queue phenomenon. Gate-4b (F sim + smoothing-path extra
draws) is therefore de-risked for presentation: the path already
presents 92 displayed/s. (Pre-trial dip and post-trial present
gap are manual-session menu/pause artifacts.) The F phone trial
itself is unaffected (no extra draws, no eviction). Repro:
interleave-player + SKIP=1946/TICKS=60.

## Update breakdown: physics traversal, not bookkeeping (September 16)

New probe mode SSX_NATIVE_PC_HIST=path (desktop-only, separate
file, main schema untouched): per-callback-class dispatch-pc
histogram over the window. Sizing run (det-base, guest window,
no doubling, engage→end): ordinary update 48.8M dispatches,
render 97.4M (2.0x — render executes twice the guest
instructions of update, consistent with phone render 12.25 ms
vs pair 5.12 ms).

Update split: integer bookkeeping (counter getter 0.43% +
stamp loop 0.38% + speed 0.15% + governor caller 0.08%) ≈ 1%;
view-marker work (view-matrix/frame-end/queue/gate pcs) = 0% —
view runs in render, not update. The update is ~99%
game/physics. Top: 0x802b16 loop 9.1% (counted loop over a
CTR-dispatched virtual call = per-object update fan-out —
dispatch shape, hard to optimize), governor/damping 0x802bf5
7.4%, math/geometry lib 0x80008a 5.8% (paired-single + FPU),
FPU physics cluster 0x801c47/48 ~7.2%.

Decisions: (a) backlog 4 CLOSED — the 3 ms update is
traversal+physics; bookkeeping is noise. (b) backlog 9 CLOSED
as answered-NO — there is no view work inside the doubled
update to split out; the 60/120 view/physics split has no
premise. (c) update optimization = object traversal + the FPU
regions above; render remains the binding constraint either
way. Repro: pchist-player + SKIP=1946, no DOUBLE_UPDATE.

## Quiet probe delta: ~0.1 ms, ~2% (September 16)

New probe mode SSX_NATIVE_QUIET=1 (desktop-only): skips per-row
Diff/Hash/word-dump compute and flushes every 128 rows; timing,
states, counts, and results stay exact. A/B on the identical
tumble window (SKIP=712/TICKS=150, trajectories verified
bit-identical over 5908 update rows — the probe is read-only so
the guest cannot tell): pair CPU med 4.614 → 4.510 ms, p95
5.279 → 5.085 ms. The full probe costs ~0.1 ms med (~2%) per
pair; production-quiet buys ~0.1 ms, not headroom. Phone pair
5.12 ms projects to ~5.0 ms ship — still render-bound. Backlog 3
CLOSED. Repro: quiet-player + SKIP=712/TICKS=150 + QUIET.
