# M18 — Design (recorded before running)

Goal: characterize WHAT the non-translational remainder is (M17 gap
5): filtering-scale tests on the synth residual. Translation is
exhausted (M17: global half-pel 0 on 764/764 shapes + M15 frame;
block16 compensation negative, −25446 B on s0). What stands is
22815 B of edge-concentrated, mostly-±1 differences between
blend-synth and exact-mid truth on M16 shape 0 (13418 B on M15's
frame), with 93.6% of residual Y px at |d|=1. Candidate
characters: filtering (blend weights, rounding, bilinear taps,
edge phase), sub-pixel coverage/AA decisions, or genuinely
non-rigid content. Fully offline: no harness code, no replays, no
lease, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(shape-0 triplet + all 764 per-shape triplets + `loo.txt`),
`/Volumes/Extreme SSD/m15/` (`m15-v0/mid/full.bin`, second sample),
`/Volumes/Extreme SSD/m17/` (`m17.txt` cross-check values only).
Work dir: `/Volumes/Extreme SSD/m18/` (new). Evidence:
`local/research/M18/` (committed with `git add -f`).

## Estimator suite (`m18.py`, `control.py`)

Shared core (M17 `m17.py` verbatim where reused): YUYV 640x448
decode, plane split/join, `xdiff` byte diff, Y-|d| histograms,
top/mid/bot bands, `shift_frac` bilinear shift, `fnv1a`, PNG
writer. New: weighted-blend synth, truth-gradient tables,
affine warp + coordinate-descent fit.

Mask rule (inherited): estimation uses the moved-Y mask
(v0≠full) where a mask applies; residual byte counts stay raw
full-frame (M14 shape), with masked splits tabled alongside.

### Test W — blend-weight sweep (+ rounding variants)

Generalized blend: synth_w = floor(w·v0 + (1−w)·full) per byte
in float64, clipped to uint8. At w=0.5 this reproduces the M15
blend `(v0+full)//2` byte-exactly (verified by fnv against
M17's `6b9ffda25bd76c6f` before trusting the sweep).
R(w) = xd(synth_w, mid), raw bytes.

Grids (recorded before running): coarse w ∈
{0.0,0.1,…,1.0} (11 pts) over all 764 M16 triplets
(per-shape argmin distribution + per-shape R^W table, M17-G
scope analogy); fine w ∈ {0.30,0.325,…,0.70} (17 pts) on the
shape-0 triplet and the M15 frame. Best-w detail tabled as
bytes + Y-|d| hist + bands (M16-loo table shape), per band.

Rounding variants at w=0.5 (the ±1 question): floor (blend),
round-half-up, round-half-even, ceil — 4 residual counts on
s0 + M15.

Weight-feasibility bound (analytic, no sweep needed): as w
ranges over [0,1], synth_w at one byte covers every integer
between v0 and full inclusive, so bytes where mid lies
strictly outside [min(v0,full),max(v0,full)] can NEVER match
any blend weight — a hard floor under Test W. Tabled as raw
bytes + Y-plane px on s0 + M15.

Mid-position 4-way split of residual bytes (coverage/AA
probe): mid==v0 / mid==full / strict interior /
outside-interval counts. Winner-take-all (endpoint) residual
reads as coverage decisions; interior residual reads as
filtering-scale.

Explained: E_W = R_0 − R_best, e_W = E_W / R_0 on s0.

### Test P — sub-pixel edge-phase analysis (no fit, tables only)

On truth (mid) Y, int16 central differences (edge replicate):
gx, gy, mag = |gx|+|gy|, 8 orientation bins of atan2(gy,gx).
Tables on s0 + M15, over residual-Y px vs all px:

- P1 residual rate per gradient-magnitude decile (deciles over
  all frame px) + top-quartile carry share.
- P2 residual count/rate per orientation bin + max-bin share.
- P3 sign coherence: sign(synth−truth) vs gradient direction
  per orientation bin (systematic ±1 bias along gradients =
  filter-phase signature).
- P4 moved-mask membership: residual px inside/outside v0≠full
  mask, rates both; R_out(w) is constant under any w (tabled
  floor).

No thresholds are fit; P discriminates by concentration.

### Test A — affine warp family (CONDITIONAL, one family only)

Family choice (recorded before running): global affine, 6-dof
param p=(tx,ty,θ,s,shx,shy), inverse-map warp with bilinear
sampling. Perspective rejected: at ±1-px residual scale its
extra dof is unidentifiable; affine nests translation so the
M17-G (0,0) reading is the null it must beat.

Trigger rule (recorded before running): Test A runs iff
e_W < 0.5 on s0 — i.e. Test W fails bar H1_W and a structured
remainder stands. Otherwise skipped per the brief's gate.

Estimation: coordinate descent on masked Y-SAD of
warp(v0,M(p)) vs full from identity; per-param 5-point line
searches, fixed small deltas (t ±1/±0.5, θ ±1°/±0.5°/±0.25°,
s 1±0.005/0.002/0.001, shear ±0.005/0.002/0.001), 2 passes.
Compensation: synth_A = //2 mean of warp(v0,M(p/2)) and
warp(full,M(−p/2)) on Y (M/2 = halved t/θ/shear, sqrt s);
U/V translation-only with (tx/4,ty/4) (M17 precedent),
linear part identity. R_A = xd(synth_A, mid).
Explained: E_A = R_0 − R_A, e_A = E_A / R_0 on s0 + M15.

Corroboration (runs with A): least-squares affine fit to the
M17-Model-B block vector field (re-run `model_b` verbatim
from the vendored core on s0): R² of the field vs the fitted
affine — coherence check, not compensation.

### Per-carrier discrimination (runs under W)

Top-10 carriers derived from `loo.txt` (sorted removed
share; cross-checked against M16 REPORT's top-10 — mismatch
= stop and table). Per carrier k: removed-residual mask =
res0 Y px vanishing in res_s (resynth per shape as blend_s
vs mid_s — valid: all integer shifts measured (0,0), synth
== blend byte-identical). Masked fine-grid sweep R_k(w) over
Y-plane |d| counts: argmin w_k vs global 0.5. A carrier
preferring w≠0.5 reads as per-draw filtering difference.

### Positive controls (`control.py`, recorded before running)

- W control: synthetic truth = 0.3·v0+0.7·full (floor) on s0
  → coarse sweep argmin must read 0.3 exactly.
- P control: synthetic ±1 residual correlated with top-decile
  gradient px → P1 top-decile rate ratio ≥5× bottom decile.
- A control (runs iff A triggers): s0-v0 warped by known
  p=(tx=+1.0, θ=+0.5°, rest identity) → fit must recover
  tx∈[0.5,1.5], θ∈[0.25°,0.75°].

## Falsification bars (recorded before running; tables, no verdicts)

- H1_W (blend weight explains): e_W ≥ 0.5 on s0
  (R_best ≤ 0.5·R_0 at some swept w).
- H2_W (rounding explains): best rounding variant R ≤ 0.75·R_0
  on s0 (rounding alone explains ≥25%).
- H_P (edge-phase/filtering structure): top-gradient-quartile
  px carry ≥75% of residual Y px on s0.
- H_A (affine explains; if triggered): e_A ≥ 0.5 on s0.
- N (standing remainder): bytes + |d| hist + bands after the
  best model — the deliverable whatever the bars read.

## Run protocol

1. Input shas (sha256 full, in the receipt): m16 s0
   v0/mid/full bins, m15 v0/mid/full bins, top-10 carrier
   triplet bins.
2. Model 0 recompute + cross-check vs `loo.txt` (22815),
   M17 `m17.txt` (22815/13418 + fnv `6b9ffda25bd76c6f`).
   Mismatch = stop and table.
3. Test W: s0+M15 fine + rounding + feasibility bound +
   4-way split; then 764-shape coarse sweep (argmin
   distribution, per-shape table).
4. Test P: P1–P4 tables on s0 + M15.
5. Gate: run Test A (+ B-field affine fit) iff e_W < 0.5.
6. Per-carrier masked sweeps (top 10).
7. Determinism re-run receipt: W fine sweep + rounding on s0
   twice; A fit twice if triggered — identical numbers/bytes.
8. PNGs if they discriminate (320x224 or small plots, <5 MB
   total): R(w) curve plot, orientation-colored residual
   phase map, affine field overlay in M17 style.
9. `control.py` receipts.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 00:55 EDT, stop by 04:55).
