# M18 — Remainder character: filtering-scale tests on the synth residual: REPORT

M17's 22815-B non-translational remainder tested for filtering-scale
character (M17 gap 5): blend-weight sweep + rounding variants (Test
W), sub-pixel edge-phase tables (Test P), one gated non-translational
warp family — global affine (Test A) — and per-carrier masked weight
sweeps (Test C). Fully offline — no harness code, no replays, no
lease, no `adb`. No device work. Runbook
`local/muse/prompts/M18.md`. Tables, no verdicts.

Headers read first: `local/research/M17/REPORT.md` (all of it: rigid
falsified at integer, half-pel, and block scales; the 22815-B
remainder with 93.6% of residual Y px at |d|=1) plus the M16 carrier
table (top carriers 694/693/701 + bottom-HUD ranks, where the
remainder lives per draw).

Time box 4 hours (start 2026-09-20 00:55 EDT); used about 0.5. No
lease of any kind (brief orders none; P-lane briefs share nothing).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, or `m17/` — all outputs went to the new
`/Volumes/Extreme SSD/m18/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15 triplet
(`m15-v0/mid/full.bin`, second sample). Work dir
`/Volumes/Extreme SSD/m18/`; evidence `local/research/M18/`.

Input shas (sha256 full, from the run receipt):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m18.txt` §inputs; prefixes match M17's.)

Model 0 recompute (blend baseline, byte-exact from the dumps;
w=0.5 floor == M15 blend, fnv-verified):

| Frame | R_0 | xdmax | xdmean | respx | Y-|d| hist [1,2–3,4–7,8–15,16+] | bands t/m/b | fnv |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| m15 | 13418 | 102 | 1.712 | 8584 | [7474, 398, 339, 172, 201] | 2191/3072/3321 | `306b5c778898b64a` |
| m16 s0 | 22815 | 49 | 1.361 | 14984 | [14021, 368, 280, 140, 175] | 5678/5300/4006 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 match M15/M16/`loo.txt`/M17 exactly,
fnvs match M17's. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

Three `m18.py` invocations, one receipt. The first two runs are
superseded (estimator defects, tabled below — not results); the
third run is the receipt (`m18.txt`, 19.9 s, exit 0).

| Invocation | Wall | Standing |
| --- | --- | --- |
| run 1 (origin-based affine rotation) | 24.8 s | superseded: A control failed (tx missed) |
| run 2 (center-based affine; float-sum blend) | 24.8 s | superseded: R(w) spiked 2–4× at w=0.30/0.425 on both frames |
| run 3 (receipt) | 19.9 s | exit 0; all 3 controls pass |

Defect 1 (affine parametrization): rotation about the frame
origin couples catastrophically with translation in coordinate
descent — the A control (injected tx=+1.0, θ=+0.5°) recovered
(tx=+0.000, θ=+0.250°) with SAD 3640168→966467. Fix:
rotation/scale/shear about the frame center (translation-only
still byte-identical to `shift_frac`; self-check max diff
0.0). Post-fix control passes.

Defect 2 (float floor): `floor(w·a+(1−w)·b)` rounds
`w+(1−w)` below 1 for some w, flipping static bytes to v−1
(isolated 2–4× R spikes at the same w on both frames).
Fix: `full+floor(w·(v0−full))` (w·0==0 exact on statics;
still byte-identical to blend at w=0.5). Post-fix static-flip
guard reads 0/0 over the fine grid on both frames.

Per-stage wall (receipt run, sequential, no pool):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| W fine sweeps (s0 + m15, 17 pts) | 2 | 0.6 s |
| W coarse sweep (11 pts × 764) | 764 | 14.8 s |
| P tables (s0 + m15) | 2 | <1 s |
| A fits (s0 + m15) + B-field fit | 2 | 1.9 s |
| C masked sweeps (top 10 × 17 pts) | 10 | <1 s |
| Determinism re-run (W+A on s0) | — | in-pass |
| Positive controls (`control.py`) | — | 0.5 s |
| Total `m18.py` wall | — | 19.9 s |

## Step 2 — estimates

### Test W — blend-weight sweep (fine + coarse)

Fine-grid R(w) curves (17 pts, 0.30–0.70 step 0.025):

| w | R(s0) | R(m15) |
| ---: | ---: | ---: |
| 0.300 | 27026 | 16283 |
| 0.350 | 26428 | 15849 |
| 0.400 | 26220 | 15598 |
| 0.450 | 26097 | 15399 |
| 0.475 | 25938 | 15212 |
| **0.500** | **22815** | **13418** |
| 0.525 | 26030 | 14983 |
| 0.550 | 26051 | 15011 |
| 0.600 | 26282 | 15307 |
| 0.650 | 26462 | 15551 |
| 0.700 | 26966 | 15961 |

(Full 17-pt rows + hists + bands in `m18.txt`; every other row
elided here.) Sharp cusp minimum exactly at w=0.5 on both
frames: Δw=±0.025 adds ~3100 B (s0) / ~1600 B (m15).
Best-w detail at 0.5 == baseline row (§Baseline note).
e_W = 0.0000 on s0, 0.0000 on m15.

Coarse sweep (w ∈ {0.0,…,1.0}, all 764 M16 triplets):
argmin distribution {0.5: 764}. Explained bytes: 0 on every
shape (Rmin == R_s(M16) for all 764 rows; `loo.txt`
cross-parse 764/764 rows matched). Full 764-row per-shape
table (argmin w / Rmin / R_s / explained) in `m18.txt`.

Rounding variants at w=0.5:

| Frame | floor (blend) | half-up | half-even | ceil |
| --- | ---: | ---: | ---: | ---: |
| s0 | 22815 | 22421 (−394, 1.7%) | 22350 (−465, 2.0%) | 22421 (−394) |
| m15 | 13418 | 13081 (−337, 2.5%) | 13132 (−286, 2.1%) | 13081 (−337) |

Weight-feasibility bound (mid outside [v0,full] — unmatchable
by ANY blend weight): s0 2589 raw bytes (11.35% of R_0),
670 Y px; m15 1674 bytes (12.48%), 602 Y px.

Mid-position 5-way split of the blend residual (raw bytes;
caveat: the `static` cell as coded counts residual bytes with
v0==full AND mid inside [v0,full], which is empty by
construction — static-site residual bytes land in `outside`;
P4's Y-px membership is the clean static/moved split):

| Frame | n | outside | static* | mid==v0 | mid==full | interior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 22815 | 2589 (11.4%) | 0 | 9412 (41.3%) | 8339 (36.6%) | 2475 (10.9%) |
| m15 | 13418 | 1674 (12.5%) | 0 | 5281 (39.4%) | 3924 (29.2%) | 2539 (18.9%) |

### Test P — edge-phase tables (s0 + m15)

P1 residual rate per truth-gradient-magnitude decile
(monotone rising on both frames):

| dec | s0 rate | m15 rate |
| ---: | ---: | ---: |
| 0 (flat) | 0.0151 | 0.0030 |
| 1 | 0.0254 | 0.0083 |
| 4 | 0.0539 | 0.0173 |
| 7 | 0.0666 | 0.0379 |
| 8 | 0.0794 | 0.0513 |
| 9 (top) | 0.1150 | 0.1120 |

(Decile edges + full 10-row tables in `m18.txt`; s0 dec-2
reads empty — tied integer-magnitude quantile edges, tabled
as measured.) Top-dec/bottom-dec ratio: 7.6× (s0),
37× (m15). Top-quartile carry: s0 6748/14984 = 45.0%
(mag≥14); m15 5248/8584 = 61.1% (mag≥16).

P2/P3 per orientation bin (8 gradient-direction bins + flat;
posfrac = P(synth>truth) on residual px):

| obin | s0 rate | s0 posfrac | m15 rate | m15 posfrac |
| ---: | ---: | ---: | ---: | ---: |
| 0 (−180..−135) | 0.0866 | 0.136 | 0.0542 | 0.193 |
| 1 | 0.0499 | 0.088 | 0.0285 | 0.129 |
| 2 | 0.0379 | 0.057 | 0.0195 | 0.118 |
| 3 | 0.0689 | 0.071 | 0.0422 | 0.121 |
| 4 (+0..+45) | 0.0857 | 0.076 | 0.0566 | 0.133 |
| 5 | 0.0571 | 0.058 | 0.0391 | 0.083 |
| 6 | 0.0372 | 0.067 | 0.0208 | 0.104 |
| 7 | 0.0509 | 0.100 | 0.0323 | 0.186 |
| 8 (flat) | 0.0114 | 0.017 | 0.0030 | 0.063 |

Diagonal-gradient bins 0+4 carry 28.0% (s0) / 28.4% (m15) of
residual px on ~17% of px; max single bin 16.2% (s0 bin 7) /
15.7% (m15 bin 4) — no dominant orientation. Sign is
systematically negative in every bin on both frames
(synth−truth < 0 on 91.7% (s0) / 86.5% (m15) of residual Y px).

P4 moved-mask membership (Y px):

| Frame | inside (v0≠full) | outside |
| --- | --- | --- |
| s0 | 14521/33389 (rate 0.435) | 463/253331 (rate 0.0018) |
| m15 | 8145/17533 (rate 0.465) | 439/269187 (rate 0.0016) |

Residual Y px inside the moved mask: 96.9% (s0), 94.9% (m15).

### Test A — affine (gated RUNS: e_W = 0 < 0.5)

Coordinate-descent fits from identity (masked Y-SAD):

| Frame | p=(tx,ty,θ,s,shx,shy) | est sad00→sadbest | R_A | e_A |
| --- | --- | ---: | ---: | ---: |
| s0 | identity (all 0 / s=1) | 81268→81268 | 22815 | 0.0000 |
| m15 | identity | 66599→66599 | 13418 | 0.0000 |

Descent never moves: every 1D step reads ≥ sad00. Synth_A ==
blend byte-identically (s0 fnv `6b9ffda25bd76c6f`; m15
`306b5c778898b64a`). R_A rows == baseline rows.

Corroboration — least-squares affine fit to the re-run
M17-Model-B block vector field (s0, 655/1120 non-degenerate
blocks): vx R²=0.0066, vy R²=0.0087 (coefficients in
`m18.txt`) — no affine coherence in the field.

### Test C — per-carrier masked weight sweeps

Top-10 derived from `loo.txt` matches M16 REPORT exactly
(shapes 694/693/701/368/369/366/370/376/748/750, shares
6525/1580/1126/441/393/372/262/260/245/239). Removed-mask
recompute matches M16's removed-residual maps exactly
(rank 1: 4888 Y px, 3415/1442/31; rank 2: 1208,
824/384/0; rank 3: 649, 186/463/0; ranks 4–9
bottom-band-only; rank 10: 202, 0/187/15).

Masked fine-grid sweep per carrier (Rk(w) = residual Y px
over the carrier's removed mask; full 17-pt curves in
`m18.txt`):

| rank | shape | Rk(0.5) | argmin w | Rk(min) | Δ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 694 | 4888 | 0.675 (grid edge) | 4634 | −254 (−5.2%) |
| 2 | 693 | 1208 | 0.675 (grid edge) | 1127 | −81 (−6.7%) |
| 3 | 701 | 649 | 0.550 | 492 | −157 (−24.2%) |
| 4 | 368 | 448 | 0.300 (grid edge) | 441 | −7 (−1.6%) |
| 5 | 369 | 248 | 0.300 (grid edge) | 247 | −1 |
| 6 | 366 | 244 | flat (all 244) | 244 | 0 |
| 7 | 370 | 191 | flat (all 191) | 191 | 0 |
| 8 | 376 | 174 | flat (all 174) | 174 | 0 |
| 9 | 748 | 190 | 0.675 (grid edge) | 176 | −14 (−7.4%) |
| 10 | 750 | 202 | 0.300 (grid edge) | 181 | −21 (−10.4%) |

Ranks 6–8 curves are perfectly flat over all 17 grid points
(weight-invariant removed px — static-site residual, mid
differing where v0==full). Ranks 1–3 (effect draws) prefer
the v0 side (0.55–0.675); ranks 1–2 argmins sit at the grid
edge (true per-carrier argmin outside 0.30–0.70 — tabled,
not chased).

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| W synthetic truth @0.3 | argmin 0.3 | 0.3 | True |
| P synthetic top-dec residual | top/bottom rate ∞ (0.50/0.00) | ratio ≥5 | True |
| A injected (tx=+1.0, θ=+0.5°) | tx∈[0.5,1.5] ✓ θ∈[0.25,0.75] ✓ | both | True |

(All three pass on the receipt code; the A control failed on
the superseded origin-based parametrization — §Runs.)

### Determinism re-run receipt (same inputs, second pass)

W s0: R-curve identical=True, best fnv `6b9ffda25bd76c6f`
vs `6b9ffda25bd76c6f`, identical=True. A s0: p
identical=True, fnv `6b9ffda25bd76c6f` vs
`6b9ffda25bd76c6f`, identical=True.

## Step 3 — attribute

Model comparison (bytes + distributions, M16-loo table shape):

| Frame | Model | R | explained (R_0 − R) | e | xdmax | xdmean | respx | Y-|d| hist | bands t/m/b |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| m16 s0 | 0 blend | 22815 | 0 | 0.0000 | 49 | 1.361 | 14984 | [14021, 368, 280, 140, 175] | 5678/5300/4006 |
| m16 s0 | W best-w | 22815 | 0 | 0.0000 | 49 | 1.361 | 14984 | [14021, 368, 280, 140, 175] | 5678/5300/4006 |
| m16 s0 | W half-even | 22350 | 465 | 0.0204 | — | — | — | — | — |
| m16 s0 | A affine | 22815 | 0 | 0.0000 | 49 | 1.361 | 14984 | [14021, 368, 280, 140, 175] | 5678/5300/4006 |
| m15 | 0 blend | 13418 | 0 | 0.0000 | 102 | 1.712 | 8584 | [7474, 398, 339, 172, 201] | 2191/3072/3321 |
| m15 | W best-w | 13418 | 0 | 0.0000 | 102 | 1.712 | 8584 | [7474, 398, 339, 172, 201] | 2191/3072/3321 |
| m15 | W half-up | 13081 | 337 | 0.0251 | — | — | — | — | — |
| m15 | A affine | 13418 | 0 | 0.0000 | 102 | 1.712 | 8584 | [7474, 398, 339, 172, 201] | 2191/3072/3321 |

(— = detail rows not emitted for rounding variants; R only.)

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_W | e_W ≥ 0.5 on s0 | e_W = 0.0000 — not met |
| H2_W | best rounding R ≤ 0.75·R_0 on s0 | 22350 (0.9796·R_0) — not met |
| H_P | top-gradient-quartile carries ≥75% of residual Y px on s0 | 45.0% (m15: 61.1%) — not met |
| H_A | e_A ≥ 0.5 on s0 | e_A = 0.0000 — not met |
| N | remainder after best model as bytes + hist + bands | 22815 B, [14021, 368, 280, 140, 175], 5678/5300/4006 (best = tie 0/W/A) |

Where each test discriminates vs not (region/carrier table):
Test W discriminates nowhere globally (cusp at 0.5 in all
three bands on both frames — best-w bands == baseline
bands) but per-carrier (Test C): effect draws 694/693/701
prefer the v0 side (−5 to −24% on their masks) while HUD
draws 366/370/376 are weight-invariant (static-site
residual). Test P discriminates by gradient magnitude
(monotone rate rise, 7.6×/37× top/bottom) and sign
(systematic synth<truth in every orientation bin) but not
by orientation (max bin 16%) or quartile carry (bar not
met). Test A discriminates nowhere (identity, all bands).

Updated deliverable — explained vs standing remainder:

| Content | Bytes (m16 s0) | Behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (M16, unchanged) |
| blend-weight component (W) | 0 explained | argmin 0.5 on 764/764 + m15; e_W = 0 |
| rounding component | 465 explained (2.0%) | half-even best; bar (25%) not met |
| affine component (A) | 0 explained | identity both frames; field R²≈0.007 |
| standing remainder | 22815 (100% of R_0) | below |
| · weight-unmatchable floor | 2589 (11.4%) | mid outside [v0,full]; no w can match |
| · endpoint residual | 17751 (77.8%) | mid exactly at v0 (41.3%) or full (36.6%) |
| · interior residual | 2475 (10.9%) | strict interior, the only w-sensitive class |
| · sign structure | 91.7%/86.5% synth<truth | systematic −1 bias, all orientations |
| · mask structure | 96.9% in moved mask | rate 0.435 in / 0.0018 out; 463 static-site Y px |

Screenshots (committed): `m18-wcurve.png` 8573 B (R(w)
fine-grid curves, s0 yellow + m15 cyan, cusp minimum at
the w=0.5 vline), `m18-phasemap.png` 121939 B (dimmed
truth + residual px colored by edge-orientation quartile:
red/green/blue/yellow, white where truth is flat).
Total 130512 B (budget 5242880).

Recorded without verdict: blend weight explains 0 of 22815
B on 764/764 shapes with a sharp cusp at w=0.5; rounding
explains ≤2.5%; global affine explains 0 on both frames
with a validated estimator; the full 22815 B stands,
77.8% of it with mid exactly at an endpoint and 91.7%
of residual Y px reading synth<truth (86.5% on M15's).

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| test suite + "explained" definition + falsification bars, recorded before running | recorded | `DESIGN.md`: W sweep + rounding + bound + split, P1–P4, gated affine, per-carrier C, bars H1_W/H2_W/H_P/H_A/N |
| weight-sweep curve, edge-phase tables, warp-family fit if triggered, wall/exit/shas/determinism | measured | §Step 2: fine+764 coarse curves; P1–P4 both frames; A identity both frames; 19.9 s; re-run identical |
| bytes + structure of the remainder; per-band and per-carrier where tests discriminate; explained-vs-standing deliverable | measured | §Step 3: comparison + bars + region + deliverable tables; C per-carrier argmins; bands at best-w |
| screenshot(s) if they discriminate (or absence reasoned) | measured | 2 PNGs, 130512 B: weight-curve cusp + orientation phase map |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the third invocation — §Runs):

```
cp local/research/M18/m18.py local/research/M18/control.py "/Volumes/Extreme SSD/m18/"
python3 m18.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m18" /Users/bradrichardson/dev/ssx3/local/research/M18 > m18.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M18/` — `DESIGN.md`
(suite + bars, recorded before running), `m18.py` (core +
Tests W/P/A/C + PNG writer), `control.py` (3 synthetic
positive controls), `REPORT.md` (this file),
`m18-wcurve.png`, `m18-phasemap.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m18/` —
`m18.txt` (receipt: shas, baselines, fine curves, rounding,
bound, split, 764-row table, P1–P4, A fits, field fit,
per-carrier curves, re-run, PNG sizes), `control.txt`,
`m18-synth-W-s0000.bin` / `m18-synth-W-m15.bin` /
`m18-synth-A-s0000.bin` / `m18-synth-A-m15.bin` (4 × 573440
B; all four are byte-identical to their frame's blend by
measurement), `m18.py`, `control.py` (working copies). No
writes into `m15/`, `m16/`, `m17/`, `/tmp/p1-link`, or other
agents' dirs.

## Gap rows (exact next brief each needs)

1. Endpoint-direction split (new — the joint hypothesis this
   run cannot close): is mid the BRIGHTER endpoint on the
   17751 endpoint residual bytes (mid==max vs mid==min
   counts), which side do the 2589 outside-interval bytes
   fall on, and how many raw residual bytes sit on static
   sites (v0==full)? Needs its own brief: one offline
   direction-split test over the SSD dumps — no new harness
   code. (M18 tables the marginals: 77.8% endpoint +
   91.7%/86.5% synth<truth; the joint needs the split.)
2. Negative-share mechanism (M16 gap 3, still open): 93
   negatives (worst −244) unattributed at byte level. Needs
   its own brief: per-shape added-residual maps (residual_s
   pixels absent from residual_0) + EFB-copy diffing, offline
   on the SSD dumps — no new harness code.
3. Odin port readiness (M16 gap 2, still open): no Odin
   contract in-repo; handoff artifact stays `loo.txt` +
   dumps + synths. Needs its own brief once the consumer
   names its interface (input format, per-draw weights vs
   pixel masks, frame coverage).
4. Top-HUD glyph residual isolation (M16 gap 4, still open):
   bottom-HUD draws identified; top-band glyph edges in the
   long tail. Needs its own brief if draw-level top-HUD
   isolation matters: HUD-region masked re-attribution,
   offline — no new harness code. Note for that brief:
   bottom-HUD carriers' removed px read weight-invariant
   (static-site residual, Test C ranks 6–8).
5. Per-carrier weight centers (new, optional): effect-draw
   argmins sit at the fine-grid edge (ranks 1–2 at 0.675).
   Needs its own brief only if per-draw filter centers
   matter: full-grid (0.0–1.0) masked sweeps per top
   carrier + sign-split curves, offline — no new harness
   code.

## What I could not do

1. Perspective warp family: rejected by design (recorded in
   DESIGN.md — unidentifiable at ±1-px residual scale);
   affine was the single allowed family and reads identity.
2. Finer weight grids: 0.025 fine + 0.1 coarse recorded and
   run; the cusp at exactly 0.5 (±0.025 → +3100 B) leaves no
   room a finer grid could fill — tabled, not chased.
3. Per-shape affine fits: s0 + M15 only (M17-Model-B scope
   precedent); the per-shape question is carried by the
   764-shape weight sweep.
4. U/V-independent estimation: P tables are Y-plane, W counts
   are raw bytes; independent chroma analysis not attempted.
5. Joint endpoint-direction test: gap 1 above — the one test
   this run's tables point at but do not contain.
6. 5-way split `static` cell is vacuous as coded (inside +
   v0==full is empty by construction); static-site residual
   is carried by P4's Y-px membership (463/439 px) and gap
   1's raw-byte count. Tabled, not re-run.
7. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M18/`: `DESIGN.md`, `m18.py`,
`control.py`, `REPORT.md` (this file), `m18-wcurve.png`,
`m18-phasemap.png` (130512 B total).
