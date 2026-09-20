# M17 — Design (recorded before running)

Goal: test whether the rigid component of the M16 synth residual
(R_0 = 22815 B on the M16 frame; M15's frame read 13418 B — frames
differ per run) lives at sub-pixel scale (M16 gap 1 = M15 gap 2,
open twice). Integer global warp measured (0,0) on 764/764 shapes
(M16 §Step 3) and on the M15 frame — yet 93.6% of residual Y px sit
at |d|=1, edge-concentrated. Fully offline: no harness code, no
replays, no lease, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(shape-0 triplet + all 764 per-shape triplets + `loo.txt`) and
`/Volumes/Extreme SSD/m15/` (`m15-v0/mid/full.bin`, second sample).
Work dir: `/Volumes/Extreme SSD/m17/` (new). Evidence:
`local/research/M17/` (committed with `git add -f`).

## Estimator suite (`m17.py`)

Shared core (M15 `synth.py` / M16 `loo.py` verbatim where reused):
YUYV 640x448 decode, plane split/join, `xdiff` byte diff, Y-|d|
histograms, top/mid/bot bands, `shift_plane` integer shift. New:
`shift_frac` — bilinear resample with edge replicate, float
(dx,dy), +dx moves content right (same sign convention as
`shift_plane`).

Mask rule (inherited): motion estimation uses the moved-Y mask
(v0≠full) only; unmasked SAD degenerates to (0,0) on
static-dominated frames (M15 precedent).

### Model G — global half-pixel (per shape + M15 frame)

Rationale for the grid: integer ±24 already ruled out |shift|≥1
on all 764 shapes, so a rigid sub-pixel component must live
within ±1 px. Candidates: (dx,dy) with dx,dy ∈
{−1,−0.5,0,0.5,1} (25 candidates), masked SAD of
shift_frac(v0) vs full on Y. Best = strict minimum (first wins
ties, scan order dy-outer/dx-inner — deterministic).

Compensation: synth_G = mean(shift_frac(v0,+h/2),
shift_frac(full,−h/2)) per plane (Y full h, U/V halved h —
M15 `half_uv` precedent, float halving here); bilinear outputs
rounded to uint8, then integer //2 mean (M15 blend precedent).
R_G = xd(synth_G, mid), raw bytes (M14 shape).

Run over: all 764 M16 triplets (per-shape half-pel shift
distribution + per-shape R_s^G) and the M15 triplet (second
sample). Cost ≈ 25 masked SADs per shape — cheap.

### Model B — block matching (shape 0 + M15 frame only)

Recorded before running: block size B=16 (Y 640x448 → exact
40×28 grid, 1120 blocks); integer search ±4 px (9×9=81
candidates) per block, masked SAD of shift(v0-block-source) vs
full on Y; half-pel refine: 8 half-pel neighbors of the best
integer vector via bilinear SAD. Per-block degenerate rule
(recorded before running): blocks with <4 moved-Y px take
vector (0,0) without search (no motion to find; tabled count).

Motion target: v0→full (full is the reference, v0 is shifted),
same direction convention as Model G.

Compensation: comp0 = per-block shift_frac(v0, +v_b/2),
comp1 = per-block shift_frac(full, −v_b/2) (U/V: halved
vectors); synth_B = //2 mean; R_B = xd(synth_B, mid).

Run over: shape-0 triplet (the verbatim total — where R_0
lives) and the M15 triplet. NOT all 764 shapes (1120 blocks ×
~89 SADs × 764 shapes exceeds the box; the per-shape question
is carried by Model G). Motion-field tables: vector histogram,
|v| histogram, moved-block count, per-block SAD gain.

### Model 0 — baseline (recomputed, not trusted from memory)

R_0 = xd(synth_0, mid_0) with synth_0 = blend (all integer
shifts measured (0,0); recompute byte-exact from the dumps and
cross-check against `loo.txt`'s 22815 / M15's 13418).

## What "explained" means numerically

For model M on the verbatim triplet: explained bytes
E_M = R_0 − R_M (positive = explained; M16 removed-share
shape); explained fraction e_M = E_M / R_0. Tabled per model:
bytes + Y-|d| histogram after compensation + bands
(M16-loo table shape), per-shape R_s^G table for Model G,
block vector field summary for Model B.

## Falsification bars (recorded before running; tables, no verdicts)

- H1 (sub-pixel rigid explains the residual): e_G ≥ 0.5 on the
  shape-0 triplet (R_G ≤ 0.5·R_0).
- H2 (rigid = concentrated): the modal per-shape half-pel shift
  covers ≥50% of the 764 shapes AND is nonzero.
- L1 (needs local model): e_G < 0.1 (global half-pel explains
  <10%) while e_B ≥ 0.5 (block matching explains ≥50%).
- N (genuinely non-rigid remainder): R_best after the best
  model, tabled as bytes + |d| histogram + bands — the
  deliverable remainder whatever the bars read.

Bar outcomes are tabled as measured; the report carries no
verdicts. The updated deliverable: rigid (integer + sub-pixel
+ block) vs genuinely non-rigid remainder, with byte counts.

## Run protocol

1. Input shas (sha256 full, in the receipt): m16 shape-0
   v0/mid/full bins, m15 v0/mid/full bins.
2. Model 0 recompute + cross-check vs `loo.txt` (22815) and
   M15 report (13418). Mismatch = stop and table.
3. Model G: M15 frame first (timed single), then all 764 M16
   shapes; shift distribution, per-shape R_s^G table,
   e_G on shape 0.
4. Model B: shape-0 triplet + M15 frame; vector tables,
   e_B on both.
5. Determinism re-run receipt: Model G + Model B on shape 0
   twice — same inputs → same numbers (tabled diff).
6. PNGs if they discriminate (320x224, <5 MB total): compensated
   diff-map(s), block motion-field overlay, carrier overlay in
   M16 green/red style if a carrier survives compensation.

Wall time, exit, and exact commands recorded. Time box 4 hours.
