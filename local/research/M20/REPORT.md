# M20 — Interior-cell mechanism: mid-vs-blend offsets + filter-tap fits: REPORT

M19 gap 1 closed at table level: cell 7's per-byte offset δ =
mid − blend is ±1 on 85.9% of bytes (s0; 83.5% m15), 97.8% luma
(s0-Y; 94.2% m15), δ>0 on 80.9% (s0; 80.2% m15, reproducing M19's
cell-7 negrates exactly), edge-hugging (78.6% within d≤2 of a
static site, s0-Y), top-gradient-decile-heavy (62.8% in P1 dec-9,
s0-Y); the 701-mask cut splits the mean (−0.967 inside vs +1.489
outside, s0-Y) while all 102 |δ|≥8 bytes fall outside it; no
fixed 2–4-tap stencil over v0/full exceeds 5.3% exact-hit (best
131/2475 B, s0). Fully offline — no lease of any kind, no boots,
no harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M20.md`. Tables, no verdicts.

Headers read first: `local/research/M19/REPORT.md` (all of it:
cell 7 = 2475 B s0 / 2539 B m15, negrate 0.81/0.80, 53.1%
mid-band s0-Y, 15.2% of interior Y in 701's mask, the only
w-sensitive residual class) plus M18's Test W/P tables (weight
cusp at 0.5, P1 gradient deciles, top-quartile carry).

Time box 4 hours (start 2026-09-20 01:35 EDT); used about 0.3.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m18/`, `m19/` — all outputs went to the
new `/Volumes/Extreme SSD/m20/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), and the shape-701
triplet for the carrier cut. Work dir `/Volumes/Extreme
SSD/m20/`; evidence `local/research/M20/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17/M18/M19; 701 re-verified, not trusted):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m16-v0-s0701 | `b258ae26…387a7cc` |
| m16-mid-s0701 | `2cd8f165…3f38a7` |
| m16-full-s0701 | `3e7acd7a…367ca81` |

(Full hexes in `m20.txt` §inputs.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17/M18/M19
exactly. `loo.txt` parses to 764 rows; shape-701 share 1126
matches M16. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m20.py` invocation (the receipt, 1.4 s, exit 0 — the
estimator was never changed); two `control.py` invocations
(the first failed C-dpm on a control-feasibility defect,
tabled below — not a result; the second is green).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m20.py receipt | 1.4 s | exit 0; all guards pass; canon `111c5f91…8a103d` |
| control.py run 1 (gap<4 −1 injection) | <1 s | superseded: C-dpm recovered 726/1215 minus, set inexact (see below) |
| control.py run 2 (gap≥4 feasibility fix) | <1 s | green; both controls pass exactly |

Defect (control feasibility asymmetry): the C-dpm checker
injected blend−1 wherever blend≥1, but −1 stays strict-interior
only where hi−lo≥4 (else blend−1 lands on/below lo — an
endpoint cell, not interior), so 489 gap<4 checker-odd sites
dropped out of the recomputed cell 7. The +1 side needs only
hi−lo≥3, which holds on all of cell 7 (gap 2 forces
mid==blend, hence non-residual — confirmed by C-d1's exact
2475/2475 recovery). Fix: inject −1 only on gap≥4 sites and
count the 489 gap<4 sites as edges. Post-fix C-dpm recovers
1260+726 exactly with set equality. The `m20.py` receipt is
unaffected (control-only defect; the estimator never changed).

Per-stage wall (receipt run, sequential, no pool):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Task 1 (s0 + m15 offsets incl. 6 BFS passes) | 2 | 0.8 s |
| Task 2 (20 stencils + parity + 701 cut) | 2 + 1 | <1 s |
| Determinism re-run (Task 1 on s0, 3 BFS passes) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m20.py` wall | — | 1.4 s |

## Step 2 — estimates

### Task 1 — offset distribution (cell-7 δ)

Cell-7 membership recomputed from the dumps: 2475 s0 / 2539
m15 — M19's counts matched EXACTLY (stop rule not triggered).
δ==0 count reads 0 on both frames (residual by construction).

δ signed range + |δ| distribution (full per-value counts in
`m20.txt`):

| Frame | range | |δ| hist [1,2–3,4–7,8–15,16+] | max | mean | P(|δ|=1) |
| --- | --- | --- | ---: | ---: | ---: |
| s0 | [−45,+47] | [2127, 127, 119, 28, 74] | 47 | 2.228 | 0.8594 |
| m15 | [−36,+48] | [2121, 189, 95, 50, 84] | 48 | 2.290 | 0.8354 |

Per-plane split (Y vs U/V — interior is a luma phenomenon):

| Frame | plane | n | share | mean δ | mean |δ| |
| --- | --- | ---: | ---: | ---: | ---: |
| s0 | Y | 2421 | 0.978 | 1.117 | 2.246 |
| s0 | U | 27 | 0.011 | −1.074 | 1.593 |
| s0 | V | 27 | 0.011 | 1.222 | 1.222 |
| m15 | Y | 2391 | 0.942 | 1.197 | 2.350 |
| m15 | U | 88 | 0.035 | 0.432 | 1.409 |
| m15 | V | 60 | 0.024 | 0.783 | 1.183 |

δ vs edge distance (Manhattan px to nearest static site, same
plane; dmin=1 both frames by construction; dmax 9 s0-Y / 6
m15-Y; U/V dmax ≤3):

| Frame | plane | d=1 n/mean/amean | d=2 | d=3 | d=4 | d=5+ |
| --- | --- | --- | --- | --- | --- | --- |
| s0 | Y | 1059/0.72/2.73 | 844/1.50/1.94 | 298/1.57/2.26 | 122/0.94/1.14 | 98/0.93/1.01 |
| m15 | Y | 1161/0.73/2.41 | 940/1.70/2.32 | 233/1.55/2.42 | 44/1.14/1.59 | 13/0.62/1.08 |

(s0-Y d≤2: 1903/2421 = 78.6%; m15-Y d≤2: 2101/2391 = 87.9%.
Full sd rows + U/V rows in `m20.txt`.)

(dr,dc) component cross (s0-Y n; column-dominated: dr=0 row
holds 1574/2421 = 65.0%; m15-Y: 1596/2391 = 66.7%):

| dr\\dc | 0 | 1 | 2 | 3+ |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0 | 941 | 468 | 165 |
| 1 | 118 | 215 | 83 | 48 |
| 2 | 161 | 58 | 24 | 12 |
| 3+ | 74 | 36 | 11 | 7 |

(m15 cross + per-cell means in `m20.txt`; means read +0.5…+2.6
wherever n>10.)

δ vs M18-P1 gradient decile (M18 code verbatim; rounded edges
match m18.txt exactly on both frames — guard OK). Interior Y
bytes per decile (n / mean δ / mean |δ|):

| dec | s0 | m15 |
| ---: | --- | --- |
| 0 | 5 / 0.60 / 1.00 | 4 / 1.00 / 1.00 |
| 1 | 13 / 0.31 / 1.54 | 4 / 1.00 / 1.00 |
| 2 | 0 (tied edges, as M18) | 12 / 0.50 / 1.33 |
| 3 | 21 / 0.90 / 1.10 | 23 / 0.65 / 1.61 |
| 4 | 44 / 0.86 / 1.05 | 34 / 1.76 / 2.18 |
| 5 | 54 / 0.83 / 1.09 | 61 / 0.75 / 1.77 |
| 6 | 123 / 0.76 / 1.35 | 76 / 1.47 / 2.16 |
| 7 | 181 / 0.48 / 1.61 | 212 / 0.50 / 1.78 |
| 8 | 460 / 0.36 / 1.61 | 412 / 0.34 / 1.75 |
| 9 | 1520 / 1.48 / 2.69 | 1553 / 1.52 / 2.65 |

(Dec-9 share of interior Y: 62.8% s0 / 65.0% m15. U/V
secondary join counts in `m20.txt`; both chroma planes read
dec-9-heavy too: s0 14/27 U + 21/27 V in dec-9.)

δ sign vs (v0−full) sign joint table (d=v0−full, o=δ):

| Frame | d>0/o>0 | d>0/o<0 | d<0/o>0 | d<0/o<0 | P(o>0) | P(o>0\|d>0) | P(o>0\|d<0) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 1160 | 132 | 843 | 340 | 0.8093 | 0.8978 | 0.7126 |
| m15 | 1220 | 150 | 816 | 353 | 0.8019 | 0.8905 | 0.6980 |

(P(o>0) reproduces M19's cell-7 byte negrates 0.8093/0.8019
exactly — same quantity. δ leans + on both endpoint sides,
stronger when v0>full.)

ρ = δ/|v0−full| (max|ρ| 0.4945/0.4906 — the <0.5 guard holds;
mean|ρ| 0.2560/0.2452; bins [−0.5..0.5/0.1]):

| Frame | ρ hist |
| --- | --- |
| s0 | [19, 107, 168, 94, 84, 254, 237, 347, 1048, 117] |
| m15 | [28, 77, 200, 111, 87, 287, 284, 436, 899, 130] |

(Top bin [0.3,0.4): 1048/2475 = 42.3% s0; 899/2539 = 35.4%
m15 — the δ=+1-on-gap-3 mass.)

### Task 2 — filter-tap fits (fixed stencil list)

Per-stencil exact-hit rates over cell-7 bytes (ALL planes;
per-plane sub-rows + coverage n in `m20.txt`; s0 coverage is
full 2475 on every stencil — no border sites; m15 excludes
31/51 right/bottom-border sites on h2/b22/h3/h4):

| stencil | src | rnd | s0 hits/rate | m15 hits/rate |
| --- | --- | --- | ---: | ---: |
| h2 | v0 | floor | 31 / 0.0125 | 55 / 0.0219 |
| h2 | v0 | halfup | 30 / 0.0121 | 57 / 0.0227 |
| h2 | full | floor | 61 / 0.0246 | 46 / 0.0183 |
| h2 | full | halfup | 62 / 0.0251 | 38 / 0.0152 |
| v2 | v0 | floor | 94 / 0.0380 | 108 / 0.0425 |
| v2 | v0 | halfup | 89 / 0.0360 | 94 / 0.0370 |
| v2 | full | floor | 96 / 0.0388 | 63 / 0.0248 |
| v2 | full | halfup | 105 / 0.0424 | 70 / 0.0276 |
| b22 | v0 | floor | 42 / 0.0170 | 50 / 0.0199 |
| b22 | v0 | halfup | 33 / 0.0133 | 66 / 0.0263 |
| b22 | full | floor | 55 / 0.0222 | 80 / 0.0319 |
| b22 | full | halfup | 59 / 0.0238 | 64 / 0.0255 |
| h3 | v0 | floor | 110 / 0.0444 | 102 / 0.0407 |
| h3 | v0 | halfup | 131 / 0.0529 | 101 / 0.0403 |
| h3 | full | floor | 127 / 0.0513 | 114 / 0.0455 |
| h3 | full | halfup | 116 / 0.0469 | 105 / 0.0419 |
| h4 | v0 | floor | 39 / 0.0158 | 40 / 0.0161 |
| h4 | v0 | halfup | 32 / 0.0129 | 30 / 0.0121 |
| h4 | full | floor | 47 / 0.0190 | 48 / 0.0193 |
| h4 | full | halfup | 57 / 0.0230 | 43 / 0.0173 |

(Best cell: h3/v0/halfup on s0, 131 B = 5.3%; best on m15:
h3/full/floor, 114 B = 4.5%. No stencil × source × rounding
cell reaches double digits on either frame.)

Positional fit — δ by (v0−full) parity (n / mean / sd / amean):

| Frame | even | odd |
| --- | --- | --- |
| s0 | 653 / 0.69 / 7.50 / 3.35 | 1822 / 1.24 / 4.45 / 1.83 |
| m15 | 732 / 0.60 / 6.93 / 3.13 | 1807 / 1.39 / 4.67 / 1.95 |

δ by coordinate parity (plane-native (r%2,c%2); n / mean):

| Frame | (0,0) | (0,1) | (1,0) | (1,1) |
| --- | --- | --- | --- | --- |
| s0 | 698 / 0.54 | 533 / 1.79 | 682 / 0.60 | 562 / 1.72 |
| m15 | 711 / 0.69 | 585 / 1.60 | 665 / 0.78 | 578 / 1.73 |

(Odd-column classes read the higher mean on both frames;
per-plane parity rows in `m20.txt`.)

Carrier cut — 701-mask interior vs rest (s0 interior Y;
guards OK: removed 649 Y px, bands [186,463,0], interior-in-mask
367 — M18/M19 values reproduced):

| cut | n | mean δ | sd | mean \|δ\| | pos/neg |
| --- | ---: | ---: | ---: | ---: | ---: |
| inside 701 mask | 367 | −0.967 | 2.868 | 2.226 | 222/145 |
| outside mask | 2054 | 1.489 | 5.747 | 2.250 | 1748/306 |

Inside range [−7,+6] (`-7:33 -6:18 -5:10 -4:19 -3:21 -2:14
-1:30 1:217 2:4 6:1`); outside carries the full [−45,+47]
range — all 102 s0 |δ|≥8 bytes fall outside the 701 mask.
Pos share: 60.5% inside vs 85.1% outside.

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-d1 (mid=blend+1) | 2475 sites, all δ==+1, set exact | exact | True |
| C-dpm (checker ±1) | 1260 +1 / 726 −1, set exact; 489 gap<4 edges counted | exact | True |

(Both pass on the fixed control code; run-1 C-dpm failed
pre-fix — §Runs. Edge sites (blend=255 / gap<4) drop out of
cell 7 by construction and are counted, not forced.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0) pass1 `111c5f91…8a103d` vs pass2
`111c5f91…8a103d`, identical=True; cell counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; best stencil per frame):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | ---: |
| m16 s0 | 0 blend (δ≠0 stands) | 2475 | 0 | 0.0000 |
| m16 s0 | best stencil (h3/v0/halfup) | 2344 | 131 | 0.0529 |
| m15 | 0 blend | 2539 | 0 | 0.0000 |
| m15 | best stencil (h3/full/floor) | 2425 | 114 | 0.0449 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_DSPREAD | P(\|δ\|==1) ≥ 0.75 on s0 | 0.8594 (m15: 0.8354) — met |
| H2_LEAN | majority δ-sign share ≥ 0.75 on s0 | 0.8093 + (m15: 0.8019) — met |
| H3_EDGE | max−min mean\|δ\| over d_edge bins ≥ 1.0 on s0 | 2.733−1.010 = 1.723 (s0-Y) — met |
| H4_STENCIL | some stencil hit rate ≥ 0.50 on s0 | max 0.0529 (h3/v0/halfup) — not met |
| H5_CARRIER | \|mean δ in−out\| ≥ 1.0 or \|δ\|-mean factor ≥ 2 (s0-Y) | 2.456 (mean leg) / 1.01 (factor leg) — met on mean leg |
| N | cell 7 after best stencil + remaining split | 131 explained; 2344 B stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
plane (97.8%/94.2% Y), by |δ| (86%/84% ±1 with a ±45 tail),
by sign (80.9%/80.2% δ>0, stronger when v0>full: 89.8%/89.0%
vs 71.3%/69.8%), by edge distance (78.6%/87.9% at d≤2 with
amean falling 2.7→1.0 outward on s0-Y), by gradient decile
(62.8%/65.0% in dec-9), and by parity (even-gap amean
3.35/3.13 vs odd-gap 1.83/1.95; odd-column mean ~1.7 vs
even-column ~0.6). Task 2 discriminates by carrier (701-mask
mean −0.97 vs +1.49 outside; all |δ|≥8 outside) but no
stencil explains cell 7 (best 5.3%/4.5%).

Updated deliverable — explained vs standing remainder:

| Content | Bytes (m16 s0) | Behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (M16, unchanged) |
| endpoint-max component | 17089 of R_0 (74.9%) | mid==bright endpoint (M19, unchanged) |
| endpoint-min component | 662 of R_0 (2.9%) | mid==dark endpoint (M19, unchanged) |
| moved-outside component | 221 of R_0 (1.0%) | 159 above / 62 below (M19, unchanged) |
| static-site residual | 2368 of R_0 (10.4%) | v0==full≠mid (M19, unchanged) |
| interior ±1 mass | 2127 of cell 7 (86.0%) | δ=±1; δ>0 on 1827/2127 (85.9%) |
| stencil-explained interior | 131 of cell 7 (5.3%) | h3/v0/halfup exact hits |
| standing interior remainder | 2344 of cell 7 (94.7%) | split above; δ/sign/edge/decile/carrier tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 131 B stencil-explained within cell 7; rest split above |

Screenshot (committed): `m20-deltamap.png` 93233 B (dimmed
truth + interior Y px colored by δ sign: red δ>0 on the rider
glow and god-ray shafts, blue δ<0 clustered mid-frame on the
mountain slope, yellow/magenta |δ|≥4 sparse). The map
discriminates spatially (sign separates by region, matching
the 701-cut split), so it is included. Total 93233 B (budget
5242880).

Recorded without verdict: δ is ±1 on 2127/2475 interior bytes
(86.0% s0, 83.5% m15) with a ±45 tail confined outside the
701 mask; δ>0 on 80.9%/80.2% (stronger when v0>full);
interior is 97.8%/94.2% luma, 78.6%/87.9% within d≤2 of an
edge, 62.8%/65.0% in the top gradient decile; the best fixed
tap set (centered (1,2,1)/4 over v0, half-up) hits 131/2475
(5.3%); 2344 B of cell 7 stands.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| offset suite + δ definition + falsification bars, recorded before running | recorded | `DESIGN.md`: δ hists + plane split, BFS edge + (dr,dc) cross, P1 join, sign joint + ratio, 20 stencil cells, parity, 701 cut, bars H1–H5/N |
| δ distribution + stencil hit rates + carrier cut + wall/exit/shas/determinism | measured | §Step 2: δ/edge/decile/joint/ratio tables both frames; 20 stencil rates; 701 cut; 1.4 s; re-run identical |
| explained-vs-standing update (does any stencil shrink cell 7? by how much?) + gap rows | measured | §Step 3: best stencil 131 B (5.3%); 2344 B stands; gaps below |
| screenshot if a δ map discriminates (or absence reasoned) | measured | 1 PNG, 93233 B: δ-sign map, spatially discriminating |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
cp local/research/M20/m20.py local/research/M20/control.py "/Volumes/Extreme SSD/m20/"
python3 m20.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m20" /Users/bradrichardson/dev/ssx3/local/research/M20 > m20.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M20/` — `DESIGN.md`
(suite + bars, recorded before running), `m20.py` (offsets +
BFS edge + P1 join + stencils + parity + 701 cut + PNG
writer), `control.py` (2 synthetic δ controls),
`REPORT.md` (this file), `m20-deltamap.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m20/` —
`m20.txt` (receipt: shas, baselines, Task-1 offsets both
frames, 20 stencil rates × per-plane rows, parity tables, 701
cut, re-run, PNG size), `control.txt`, `m20.py`,
`control.py` (working copies), `m20-deltamap.png` (working
copy). No writes into `m15/`, `m16/`, `m18/`, `m19/`, or other
agents' dirs.

## Gap rows (exact next brief each needs)

1. Interior far-tail mechanism (new): 102 B with |δ|≥8 on s0
   (max 47; all outside the 701 mask; 134 B on m15) unattributed
   at value level. Needs its own brief: locate + plane/region
   isolation of the tail bytes, offline — no new harness code.
2. δ-sign mechanism (new, minor): δ>0 on 80.9%/80.2% with
   P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈ 0.70 on both
   frames. Needs its own brief only if the sign asymmetry
   matters: joint (gap, parity, carrier) sign tables, offline
   — no new harness code.
3. Static-site residual mechanism (M19 gap 2, still open): 2368
   raw bytes where v0==full≠mid (10.4% of R_0). Needs its own
   brief: static-site maps per shape + EFB-copy diffing,
   offline — no new harness code.
4. m15 below-min far tail (M19 gap 3, still open, minor): 4
   below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
   own brief only if outlier isolation matters, offline — no
   new harness code.
5. Negative-share mechanism (M18 gap 2, still open): 93
   negatives (worst −244) unattributed at byte level. Needs
   its own brief: per-shape added-residual maps + EFB-copy
   diffing, offline — no new harness code.
6. Odin port readiness (M18 gap 3, still open): no Odin
   contract in-repo; handoff artifact stays `loo.txt` +
   dumps + synths. Needs its own brief once the consumer
   names its interface.
7. Top-HUD glyph residual isolation (M18 gap 4, still open):
   bottom-HUD draws identified; top-band glyph edges in the
   long tail. Needs its own brief if draw-level top-HUD
   isolation matters.
8. Per-carrier weight centers (M18 gap 5, still open,
   optional): effect-draw argmins at the fine-grid edge.
   Needs its own brief only if per-draw filter centers
   matter.

## What I could not do

1. Mixed/adaptive stencils: only the 20 fixed stencil ×
   source × rounding cells were tabled; per-region or blended
   predictors not attempted.
2. Coarse 764-shape offset pass: s0 + m15 (+701 resynth) only;
   the brief asks for no per-shape sweep.
3. U/V-native gradient join: P1 deciles are Y-native (M18
   verbatim); U/V bytes got the co-located-Y secondary join
   only — tabled, not chased.
4. Independent verification probes (`/tmp/m20_verify.py`:
   brute-force BFS 0/200 mismatches, python-loop δ 0/500)
   are throwaway by rule — kept under `/tmp`, not committed.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M20/`: `DESIGN.md`, `m20.py`,
`control.py`, `REPORT.md` (this file), `m20-deltamap.png`
(93233 B total).
