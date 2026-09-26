# TM4 — where does the rider's per-update step come from?

Worker: Muse Code, brief `local/muse/prompts/TM4.md`, 2026-09-26 ~04:00–06:30 EDT.
Research only; nothing ships. No push. No `docs/` edits.

## Outcome

The rider's per-update step is `delta = [obj+0x1e0] × ([obj+0x300] × K)` with
`obj=0x1465c40`, `K = 1/60` from a function-private `.rodata` word
(`K1=*(0x49be9c)` for writer 1, `K2=*(0x49c08c)` for writer 2), and the
per-object time scale `[obj+0x300] = 1.0` (derived 1.0003 ± 0.0003 over 100
per-update pairings; zero writes in the race window, i.e. init-set). The
coherent probe (`PS2X_TM_RATE120=2`: TM3's manager patch plus K1/K2/K3
1/60→1/120) lands the position half-step **exactly** (per-update timescale
median 0.5002, 2 updates/VBlank on all 601 VBlanks) but motion per VBlank is
**1.148× stock — outside the ±5% acceptance**. The excess is velocity running
hot (+17% mean |v|), and it is **mode-1-specific** (mode-1 vel 1.216×,
mode-2 vel 0.935×). First unconverted consumer: **`sub_00121AA0`'s per-update
1/60 use (`0x49b828` @ `0x121e64`)**, called every mode-1 update from
`0x1381cc` with time-scale-derived args — the only unpatched 1/60-scale on
mode 1's exercised path. No tuning loops (per brief); the one-word follow-up
(halve `0x49b828`) is queued as next. The HUD formatter is still not located
(TM2's negative stands); the HUD runs at 2× as predicted.

## Part A — the delta chain (static + live)

`gp=0x4a30f0` (assumed from TM1's `A=[gp+0x2a74]@0x4a5b64`; confirmed live:
`snd.log` `addcmdhandler … gp=0x4a30f0`).

| Stage | Writer 1 (`sub_00137D18`) | Writer 2 (`sub_0013D818`) |
| --- | --- | --- |
| Store | `0x1380b4`: `sqc2 vf5,[v1+0x110]`, `vf5=[v1+0x110]+[sp+0x60]` | `0x13e0dc`: `sqc2 vf5,[v1+0x110]`, `vf5=[v1+0x110]+[sp+0x50]` |
| Delta | `[sp+0x60]=[obj+0x1e0]×f22` (`0x138088–0x1380a4`) | `[sp+0x50]=[obj+0x1e0]×f25` (`0x13e0a8–0x13e0cc`) |
| Scale | `f22=[obj+0x300]×K1` (`0x137dac`, sole write) | `f25=[obj+0x300]×K2` (`0x13d8f0`, sole write) |
| K | `*(gp-0x7254)=*(0x49be9c)=0x3c888889=1/60` | `*(gp-0x7064)=*(0x49c08c)=0x3c888889=1/60` |

- K1/K2/K3 (`K3=*(0x49c12c)`, second 1/60 in writer 2 @ `0x13ee80`: scales the
  f12 arg to `func_11DFE0`) are **single-reader-private**: a whole-image scan
  of gp-relative loads finds only `0x137d68` → K1, `0x13d8e4` → K2,
  `0x13ee80` → K3. Patching them moves only the two integrators.
- `f22` feeds the delta plus 5 clamp/compare/div uses; `f25` is writer 2's
  general per-update time-scale (16 mul/mov/neg/mfc1 uses). Halving K1/K2
  halves every per-update scaled quantity in both owning functions.
- Live (B1 watch, `tm4-stock-watch.txt`, 518 lines = 259 stores): pos 101
  stores (56× `0x1380b4` + 45× `0x13e0dc`, TM3's split reproduced bit-exact
  from the same first store); per-update `tscale = step×60/|v_used|`: n=100,
  mean 1.0003, median 1.0003, min 1.0001, max 1.0006.
- Velocity `[obj+0x1e0]` writers (158 stores): `0x1380e4` ×56
  (`vel += aux×f22`), `0x138448` ×56 (`vel += [obj+0x370]×f22×(…)`,
  scalar from `0x138418 mul f0,f22,f0`), `0x13e120` ×45 (`vel += f25-scaled`,
  `0x13e0e8 mfc1 f25` block), `0x13c86c` ×1 (pure `vel *= f0` rescale in
  callee `func_13C878`, mode-switch one-off).
- Aux-state writers (B3 watch, `tm4-aux-watch.txt`, 404 lines = 202 stores):
  `[obj+0x370]` ← `0x13820c` ×56 (plain `sq` after `jal func_138960`) +
  `0x13d66c` ×45 (plain `sq` in callee `sub_0013D1B8`); `[obj+0x3d0]` ←
  `0x138200` ×56 + `0x13d684` ×45. Aux vectors are computed in callees that
  read no 1/60 literal of their own (census).
- `[obj+0x300]`: zero writes ticks 1799–1899 in all boots → constant during
  the race; value established by derivation (1.0003) since no read-watch
  exists (gap: direct value read would need a tap).
- Immediate (lui/mtc1) physics gains/clamps on the path — none is a timestep
  scale: writer 1: 5.0, 3.0, 1.5, 1.0, 40.0, −1800.0, 10.0; writer 2: 100.0,
  −1000.0, 0.5, 2.0, 20.0, 10.0, 1.0, −20.0, −1.0. Nearby pool floats are
  gains/thresholds (0.0125, 0.001, 0.3, 3333.33, 0.8661, 0.9).

## Part B — timestep-literal census (whole ELF + gp-reader scan)

14877 gp-relative mem ops scanned; no DIAG read-watch exists (write-only),
so use = code references, as the brief allows. Caveat: the executable LOAD
spans `0x100000–0x4a4bf4`, so two `.rodata` words that decode as gp loads
are data false-positives (noted below); all tree claims below are verified
code PCs.

| Literal | Addrs | True code readers | Tree refs (rider path) | Verdict |
| --- | --- | --- | --- | --- |
| 1/60 | 193 | 193 (each exactly 1; 2 addrs +1 data alias) | 4: K1, K2, K3, `0x49b828` | per-function private pools |
| 1/30 | 43 | 43 (all single) | 0 | not on rider path |
| 60.0 | 5 | 2 (`sub_002636A8` 60/180 select; `sub_002639E0` struct store) | 0 | not HUD; 3 lui/absolute-or-data (gap) |
| 30.0 | 6 | 1 shared by ten `sub_0029…` fns (12 readers) | 0 | not on rider path |
| 1/120 | 8 | 8 (all single) | 2 (`sub_0031BE50`, `sub_0031C040`) | sin/cos Taylor coeffs (1/5! in 1/9!,−1/7!,1/5!,−1/3! pools), not timestep |
| 120.0 | 1 | 0 | 0 | unread via gp (gap) |
| 0.5 | 70 | 3 (rest are code words, e.g. `lui`) | 0 | not on rider path |
| 2.0 | 18 | 3 | 0 | not on rider path |

- The 4th tree 1/60, `0x49b828` @ `0x121e64` (`sub_00121AA0`:
  `min(f23,f20×f24)×1/60` → f12 arg to `func_31BE50`), is the §C consumer.
- Correction vs. interim notes: `sub_00114298`'s 1/60 (`0x49b544`) is NOT on
  the rider path — its `jal` site `0x13f19c` is in `sub_0013F178` (dump
  overflow, caught by `ee-func`). True `sub_0013D818` callee list in receipts.
- HUD `/60` formatter: **not found**. The two gp-reachable 60.0 words sit in
  unknown-label `0x26xxxx` functions (callers `sub_001B45E8`,
  `sub_00259098`), not render-path; TM2's render-body + 10-callee negative
  stands. Physics/animation/camera/HUD/audio split beyond the tree is not
  attributable without labels (stated gap).

## Part C — coherent probe (`PS2X_TM_RATE120=2`)

Manager rate/dt/mult/acc as TM3 plus K1/K2/K3 1/60→1/120 (verified stock
first; `tm4-probe-armed`, no refuse). HUD divisor unpatched (not found).
FR1-R1 to t2400, det, mini, tap + pos/vel/tscale watch + dumps 1800/2100/2400.

| Observable (ticks 1800–2400) | Stock (`tm4-stock`) | Probe (`tm4-probe`) |
| --- | --- | --- |
| Producer records (`dv_pslot`/`dv_ringp`) | 1 / 1 (601/601) | 2 / 2 (601/601) |
| Consumes (`dv_cons` / `dv_consOK`) | 3 / 1 | 4 / 2 |
| App updates (`dv_upd`, `tm1-update` lines) | 1 (601) | 2 (1202, 0 susp) |
| Renders (`dv_rnd` / `dv_rndOK`) | 1 / 1 | 1 / 1 |
| `A+0x10`/`A+0x14`/`A+0x24`/`A+0x28`; `A+0x20`/`A+0x34` | 60/1/60/1.0/0.0; 12/0 | 120/1/120/2.0/0.0; 12/0 |
| `A+0x1c` at 1800/2400 | 1750 / 2350 (+1/VB) | 3480 / 4680 (+2/VB) |
| Rider path 1800→2400 (600 steps) | 7692.8, mean **12.82**/VB, max 153.7 (teleport) | 8831.6, mean **14.72**/VB (**1.148×**), max 168.9 |
| Per-update tscale (watch window) | mean 1.0003 (n=100) | mean 0.5128 / median **0.5002** (n=203; median = half-step exact, mean skewed by one-offs) |
| Mean `|v|` in window, by writer | 613.3 (mode 1) / 592.4 (mode 2) | 745.9 (**1.216×**) / 554.1 (0.935×) |
| Rider per HUD second (info; HUD unpatched) | 769.3 (10 HUD-s) | 441.6 (20 HUD-s; 0.574×) |
| HUD clock 1800 / 2100 / 2400 (frames viewed) | 00:00:01 / 06 / 11 | 00:00:02 / 12 / 22 (2× slope) |
| SND final | 3666/0xf3b/531/531/531/4261/3665, ee 11846455777 | identical counters, ee +0.0002%; underruns +5.0% (host-side) |
| Route reaches race? | Yes (2ND/2, race HUD) | Yes (2ND/2, race HUD; diverged: tumbling at 1800, riding 27 MPH at 2400) |
| det-hash vs `a3efbfe-…-a5f2f32d` | IDENTICAL | DIFFER from tick 39 (intended) |

`[obj+0x110]` probe-window stores: 204 over 101 VBlanks (128× `0x1380b4`,
71× `0x13e0dc`, extras `0x113950` ×3 / `0x10655c` ×2 — same one-off family as
TM3's probe). `[obj+0x1e0]`: 334 (128/128/71 + 7 one-offs at |v| 860–1040).
`[obj+0x300]`: 0 stores (both). Vel one-offs (`0x113958`, `0x136e00/64`,
`0x137aa0`) are mode-switch artifacts of the diverged trajectory, not the
sustained +17% (excluded: mode-1 mean still 1.216×).

**Verdict: 1.148× per VBlank FAILS the ±5% acceptance. First unconverted
consumer: `sub_00121AA0:0x121e64` (K=`0x49b828`, single-reader, unpatched
1/60), called every mode-1 update from `sub_00137D18:0x1381cc` (on-path:
precedes the always-taken aux-store sequence; float args from `[obj+0x300]`
at `0x1381c0–0x1381d0`).** It is the only unpatched 1/60-scale on mode 1's
exercised path, and the heat is mode-1-specific. Gaps: (1) the `0x121e64`
use sits behind `bc1f` (`0.8661 < [sp+0x48)`), so per-call execution is
inferred, not observed; (2) the dataflow 121AA0-output → `func_138960` →
`[obj+0x370]/[obj+0x3d0]` → vel adds is plausible but untraced (an unscaled
per-call add inside `121AA0`/`138960` is the alternative). Recommended next:
one-word follow-up probe halving `0x49b828` + re-measure (one build, one
boot; not this brief — no tuning loops).

## Exact commands, pins, SHAs

- Worktree `~/dev/ssx3-work/TM4/PS2Recomp`, branch `tm4` (never pushed):
  fork `ssx3` tip `5d5c382` (`[VR3] Android: -Pps2xVu0RecompDir…`, fetched
  2026-09-26; local `~/dev/PS2Recomp` was stale at `f949ff0`) + `4f47f83`
  (TM1) + `6034bae` (TM2) + `a3ce1b7` (TM3, all cherry-picked clean) +
  `c89c6eb` (`[TM4] Coherent conversion probe PS2X_TM_RATE120=2…`, 2 files,
  +86). Runner-dir check `git diff --stat 14b1e5cb HEAD --
  ps2xRuntime/src/runner` empty (0 lines, after `c89c6eb`).
- Build 1/3: `local/tooling/build/mac_build.sh …/TM4/PS2Recomp
  …/TM4/build-det-diag --det --diag` → runner
  `dbfc9ad2e0731b28962d78daeaa668012d0d3726332843c8f71b58b238f67145`
  (2 reads match), 430,527,200 B, 527 s wall (38% ccache miss on new base).
- Boot 1/6 `tm4-stock`: `ssx3_boot.py --host mini --mode det --backend
  parallel --runner …/build-det-diag/…/ps2EntryRunner --label tm4-stock --out
  …/TM4/tm4-stock --route fr1r1 --stop-tick 2400 --sound on --wall 600
  --dump-ticks 1800,2100,2400 --env PS2X_TIMING_TAP=1 --env
  PS2X_DIAG_WATCH=0x1465D50,0x1465D58,0x1465E20,0x1465E28,0x1465F40 --env
  PS2X_DIAG_WATCH_TICKS=1799-1899` → target, t2412, 66.0 s, slot 2 (script
  claim; my parallel manual claim of slot 1 released after — one slot held
  during the boot), log 1,086,776 B.
- Boot 2/6 `tm4-probe`: same + `--env PS2X_TM_RATE120=2`, out `tm4-probe` →
  target, t2412, 64.9 s, slot 1 (`SSX3_HELD_SLOT`), log 1,257,431 B.
- Boot 3/6 `tm4-aux`: B1 watch replaced by
  `0x1465FB0,0x1465FB8,0x1466010,0x1466018` ([obj+0x370]/[obj+0x3d0]), no
  dumps, out `tm4-aux` → target, t2405, 64.0 s, slot 1 (held), log
  1,750,156 B. (Slot 2 meanwhile held by SS3 — one slot per TM4 boot
  throughout.)
- Compares: `baseline.py compare --key
  a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand …/TM4/tm4-stock` →
  IDENTICAL (ticks 1–2400 + snd/coverage; also validates base `5d5c382` +
  cherry-picks as non-perturbing); `tm4-probe` → DIFFER from tick 39
  (intended). `tm4-aux` not compared (stock env, same binary as IDENTICAL
  B1; tap counts 601/601 nominal).
- Receipts: `tm4-stock-watch.txt` (518 lines, sha `51632812…`), 
...[truncated 1273 chars]
## Orchestrator gate (2026-09-26)

**Pass.** The step chain is named (`delta = vel × ([obj+0x300] × K)`, K1/K2/K3 private 1/60 words), the coherent
probe gives exact half-steps, and the residual 1.148×/VBlank is localised to mode-1 velocity with a named first
unconverted consumer (`sub_00121AA0`'s 1/60 at `0x49b828`).

## Part 2 brief (orchestrator)
One more coherent probe step: `PS2X_TM_RATE120=3` = `=2` plus halving `0x49b828` (check it has a single reader on
the exercised path first, as you did for K1–K3; if it has several, list them and patch only the rider-path one).
Same measurement as the `=2` run. Accept if motion per VBlank is within ±5 % of stock in **both** modes; otherwise
name the next unconverted consumer and stop. ≤ 1 build, ≤ 2 boots. Also note, as a gap, what remains for the HUD
clock and for AI riders (do they use the same integrators?). Then stop.

## Part 2 — K4 halve (`=3`): K4 exonerated, residual is pre-window divergence (2026-09-26)

K4 (`0x49b828`) re-verified single-reader (`0x121e64`, true code in
`sub_00121AA0 [0x121aa0,0x121f30)`) before patching — no multi-reader split
needed. `=3` armed once (`tm4-probe-armed mode=3 … k4=3c088889`, no refuse).

| Observable (ticks 1800–2400) | Stock | `=3` (`tm4-probe3`) |
| --- | --- | --- |
| Updates/VBlank; renders | 1; 1 | 2 (601/601, 1202 lines, 0 susp); 1 |
| `A+0x1c` at 1800/2400 | 1750 / 2350 | 3480 / 4680 (+2/VB) |
| Rider path (600 steps) | 7692.8, 12.82/VB | 8863.2, 14.77/VB (**1.152×**; `=2` was 1.148×) |
| Per-update tscale (window) | mean 1.0003 (n=100) | mean 0.5128 / median **0.5003** (n=203) |
| Mode-1 per-update step (by `0x1380b4`) | 10.228 (n=55) | 6.245 (n=128) → 2×/stock = **1.221 FAIL** |
| Mode-2 per-update step (by `0x13e0dc`) | 9.91 (n=45) | 4.635 (n=71) → 2×/stock = **0.935 FAIL** |
| Mode-1 `|v|`: first-10 / last-10 in window | 634.7 / 601.8 | **1002.5 / 624.6** (decays to +3.8%) |
| Mode-2 `|v|`: first-10 / last-10 | 645.4 / 502.3 | 646.9 / 489.6 (matches throughout) |
| HUD clock 1800 / 2400 (viewed; 2100 not viewed) | 01 / 11 | 02 / 22 (2×; tumbling at 1800, 27 MPH at 2400, 2ND/2) |
| SND final | 3666/0xf3b/…/3665 | identical counters (ee cycle bit-identical to `=2`); underruns +6.8% host-side |
| det-hash vs `a3efbfe-…` | IDENTICAL | DIFFER from tick 39 (intended) |

**Verdict: FAIL the ±5%-in-both-modes acceptance — but the Part-1 conviction
is overturned, not extended.** The K4 halve perturbs the trajectory only
microscopically (`pos[0]` differs at 1e-3; `=2` vs `=3` agree on every
macro number incl. the 128/71 mode split and both decay curves), so
**`sub_00121AA0`'s 1/60 is exonerated as the velocity driver**. The mode-1
residual is a **pre-window initial-condition difference**: the probe enters
the window at |v|≈1000 vs stock ≈635 and **decays** to +3.8% by window end
(reproduced identically in `=2`: 1002.4 → 624.6). A per-update scaling error
would sustain or grow, not decay. Mode 2 matches stock end-to-end
(646.9/489.6 vs 645.4/502.3) — the conversion is working there; its −6.5%
mean is segment/trajectory noise.

**Next unconverted consumer (named, evidence-graded): the race-start/accel-phase
velocity input, ticks ~1690–1799 (before the cruise window).** The probe rider
must gain its excess speed during race-start acceleration; the cruise-window
data cannot see that phase. Prime static suspect: `sub_00138960`'s per-call
aux rewrite (reads `[obj+0x370]` at `0x1389a0`, unscaled gain 200.0
(`lui 0x4348`), no dt factor, writes back fresh `[obj+0x370]/[obj+0x3d0]`
state every mode-1 update) — but this is static plausibility only, after the
K4 lesson. Recommended next measurement (not this brief): aligned early-race
window (stock + probe watch, ticks 1690–1760) to catch the accel-phase term
live; do not halve blind. The spare Part-2 boot was intentionally unused —
one boot cannot supply both sides of that comparison.

**Gap — HUD clock:** formatter still unlocated (Part-1 negative stands). What
remains: render-`jalr` dispatch-target tap or digit-buffer watch to find the
`/60` site and the −1690 race-start base, then scale both with rate.

**Gap — AI riders:** single static call site per integrator
(`0x136eb8 → 137D18`, `0x11143c → 13D818`) with single-site dispatchers above
(`0x11145c → 136E98`, `0x1216e8 → 111408`) — no per-rider loop below
`sub_001216E0`, and the exercised path carries one obj (`0x1465c40`). Whether
the rival flows through the same chain with a different obj (loop above
`sub_001216E0`) or a separate tree is unresolved; TM2's untaken second
snapshot call site (`0x128bc0`) hints at a second path. Live resolution needs
a watch on a second rider's position (address unknown). If AI shares the
integrators, K1–K4 halves apply to it automatically; its aux/accel inputs
would need the same accel-phase audit as the player.

Part-2 pins: worktree `tm4` + `d27e6c1` (`[TM4P2] …=3…`, 1 file);
runner-dir check empty; build 1/1 `mac_build.sh --det --diag` → runner
`669bd52d143b749345818d42d6765c8d27480d65c2c989487aa1769d95e7468f`
(2 reads match), 430,527,248 B; boot 1/2 `tm4-probe3` (`=3`, B2 setup) →
target, t2400, 67.0 s, slot 1 (held), log 1,255,235 B. Receipts:
`tm4-probe3-watch.txt` (1076 lines, sha `5e7fc297…`), `tm4-probe3-arm.txt`.
Test-collateral note: dev-only research probe (default off, nothing ships;
TM1–TM3 precedent has no maintained harness for guest-behavior probes) —
verification is the lane's established det-boot + `baseline.py` + tap counts,
not a committed test.

## Orchestrator gate, Part 2 (2026-09-26)

**Pass (good call not to halve blind).** K4 exonerated by a clean experiment; mode 2 matches stock end to end; the
mode-1 residual is an initial-condition excess from the race-start phase that decays in cruise.

## Part 3 brief (orchestrator)
Aligned early-race window, stock vs `=3`, ticks 1690–1790 (race HUD ~1714): watch `[obj+0x1e0]` (velocity) and the
aux state `[obj+0x370]/[obj+0x3d0]` writers; name the term that makes the probe's launch speed ~1.58× stock
(a per-update gain without dt, e.g. `sub_00138960`'s 200.0, or a per-frame vs per-update event). One targeted
change only if a single mechanism is named and proven live; measure as before. Also, if cheap, a
dispatch-target tap to find the HUD clock formatter (`/60` and the −1690 base). ≤ 2 builds, ≤ 4 boots; then stop.

## Part 3 — countdown time base named and proven; `=4` fixes launch speed but breaks phase timing (2026-09-26)

Early window ticks 1689–1799 (store ticks; +1 vs TM1 lines), stock vs `=3`,
pos+vel+aux watch. obj=`0x1465c40` confirmed valid pre-1800 (known writer
PCs fire). Launch structure (stock): init one-offs → one mode-2 update →
countdown-copy phase (`0x113950/0x113958` + `0x139a80/0x139a8c`, 34 VBs) →
mode-1 ride (55 VBs). The probe's countdown **accelerates ~3×**: VB-aligned
`|v|` ratio stock→`=3` runs 1.000 → 1.340 over 14 VBs (stock +9.6/VB,
probe +30/VB), generated inside the window (not pre-existing divergence).

**Named term: the countdown-phase time base — six unpatched 1/60 words, four
of them rate scales.** Countdown update `sub_00139A20` → `sub_00113648`
integrates a sub-object at `[obj+0x788]` and copies `[sub+0x70]/[sub+0x80]` →
pos/vel. Its dt-terms: `C1=*(0x49b480)` (`[s0+0x98] += 1/60` accumulator,
`0x1132cc`), `C2=*(0x49b48c)` (mul chain, `0x11346c`), `C3=*(0x49b4a0)`
(vector scale, `0x1139a4`), `C4=K5=*(0x49bf1c)` (`f12=[obj+0x300]×1/60` timer
scale, `0x139a58`) — all single-reader, all rate-shaped — plus two compare
thresholds deliberately left at stock (`0x49b494`, `0x49bf20`). Census
correction: an earlier interim note said `sub_00113200`/`sub_001139A0` read
no 1/60 — wrong (name-padding bug in a scratch printout); the committed
`literal_readers.json` mapping was always correct, and the K1–K4/tree claims
are unaffected. `sub_00138960`'s 200.0 is exonerated for launch (cruise
mode-1 aux only).

**Targeted change `=4` = `=3` + halve C1–C4 (one mechanism; thresholds
untouched so per-VB branch behaviour should hold). Result: launch speed
FIXED, phase timing BROKEN.** Countdown `|v|` ratio `=4`/stock: 0.977 →
**1.000** over 33 VBs (vs `=3`'s →1.340) — the vel-compounding mechanism is
proven live. But `=4` destabilises the countdown→ride phase selection: the
`sub_00111408` jump table flickers between countdown-case and mode-1-case
(`=4` early: 73 countdown + 106 mode-1 stores interleaved over 111 VBs vs
stock's sequential 34 + 55), the compute-path variant (`0x113940/0x1138e8`)
fires 33× (stock: 0×), countdown pos trails stock by 230 units at matched
`|v|` (steering/phase difference, next lead), and stale countdown writers +
displaced ~89-unit teleports leak into the cruise window. Cruise under `=4`:
1.108×/VBlank overall (better than `=3`'s 1.152×; per-mode FAIL — confounded
by the phase leak, not a clean read). So C1–C4 halves are **proven as the
vel driver but rejected as a coherent conversion**: the phase machine reads
per-update timer values, and control-flow-aware conversion is future work.
No further change (brief allows one; budget spent as planned anyway).

| `=4` observable | Stock | `=4` |
| --- | --- | --- |
| Countdown `|v|` ratio (VB-aligned, 33 VBs) | 1.000 | 0.977 → **1.000** |
| Countdown pos gap at phase end | — | 230 units (direction/phase; next lead) |
| Cruise path 1800–2400 | 7692.8, 12.82/VB | 8520.8, 14.20/VB (**1.108×**) |
| Cruise per-update tscale median | 1.0003 | **0.5002** (half-steps still exact) |
| Updates/VBlank; `A+0x1c` slope | 1; +1 | 2 (601/601, 0 susp); +2 |
| SND final | 3666/0xf3b/…/3665 | identical counters (ee = `=2`/`=3` bit-exact); underruns +9.2% host-side |
| det-hash | IDENTICAL (B5/B1) | DIFFER from tick 39 (B7/B8, intended) |
| Route reaches race | Yes | Yes (target-bound t2404/2405, race writers, motion; frames not kept — see quirk) |
| HUD clock | 01/06/11 | 2× inferred from updcnt slope (formatter untouched; not viewed) |

**HUD tap (cheap item): 40 indirect render targets enumerated, formatter
still NOT found.** `PS2X_TM4_JALR=1` (`tm4-jalr.txt`, 55 first-seen pairs, no
cap): render range `[0x22add8,0x22c078)` calls into 40 targets beyond TM2's
10 direct (0x22aXXX helpers, 0x395XXX/0x386XXX/0x376XXX/0x377XXX UI cluster,
manager slots). No integer `div`/`divu` in any; `cvt.w.s` only in
`sub_00376938` (giant 0x3928-B UI fn; 0x376XXX targets are its interior
labels), `sub_00386128`, `sub_002CC0C0) — and none of the three loads any
timestep literal. The `/60` + −1690 base remain unlocated; next: digit-buffer
watch or deeper `jalr` chains from the UI cluster.

**Gap — AI riders:** unchanged from Part 2 (single call sites to
`sub_001216E0`; live resolution needs a second-rider-pos watch). Note the
countdown finding applies to whatever obj flows through the chain.

Worker error note: B7/B8 passed `--dump-ticks 1800,2400` (2 ticks) but the
script contract is "exactly 3" — the runner dumped every frame (2330/2318
dump lines; only first+latest PNGs kept), so no viewable `=4` frames. Tap,
watch and det data unaffected.

Part-3 pins: worktree `tm4` + `5ce906c` (`[TM4P3] =4 (countdown
C1-C4 halves) + PS2X_TM4_JALR render dispatch tap`, 3 files); runner-dir
check empty; build 1/2 `mac_build.sh --det --diag` → runner
`ffeb244d427c791ebacc1ae9950b6fc9b41edf0f75357f01a3a0eb1c5b00c781`
(2 reads match); boots: B5 `tm4-early-stock` (target, t2400, 63.5 s),
B6 `tm4-early-probe3` (target, t2407, 65.0 s), B7 `tm4-early-probe4`
(target, t2405, 67.5 s), B8 `tm4-cruise-probe4`+JALR (target, t2404,
65.5 s) — all slot 1 (held), one slot each. Receipts:
`tm4-early-stock-watch.txt` (875, `fe5ee67d…`),
`tm4-early-probe3-watch.txt` (1487, `3ccfc72e…`),
`tm4-early-probe4-watch.txt` (1696, `e19cfb4f…`),
`tm4-cruise-probe4-watch.txt` (1027, `7f8b8a11…`), `tm4-jalr.txt` (55),
`tm4-probe4-arm.txt`.
