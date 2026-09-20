# M21 — Static-site residual mechanism: maps per shape + EFB-copy diffing: REPORT

M19 gap 2 closed at table level: 518/764 shapes read byte-identical
static-site maps to s0 (median Jaccard 1.0000; only shapes 700/694
read below 0.90), while m15 shares 92/1476 sites (Jaccard 0.0245);
ε = mid−v0 is ±1 on 98.9% of static bytes (s0; 96.8% m15) with
chroma all-±1 on both frames; static sites hug moved edges (71.3%
at d=1 s0-Y, 82.5% m15-Y, vs background means 11.7/31.8); same-pixel
U&V co-residual reads 16.0×/21.6× the independence expectation (s0/
m15); the HUD-region union holds 103/463 s0-Y static px (22.2%).
Fully offline — no lease of any kind, no boots, no harness code, no
`adb`. No device work. Runbook `local/muse/prompts/M21.md`. Tables,
no verdicts.

Headers read first: `local/research/M19/REPORT.md` (all of it: cell 6
= 2368/1476 raw B, Y 463/439, negrate 0.51/0.51, s0-Y bands
15/186/262, carrier row ≤0.0842, 8-cell + band/carrier machinery)
plus `local/research/M20/REPORT.md` (all of it: δ-hist machinery,
BFS edge + (dr,dc) cross, P1 deciles, 701-cut precedent).

Time box 4 hours (start 2026-09-20 01:45 EDT); used about 0.2. No
lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/` — all outputs
went to the new `/Volumes/Extreme SSD/m21/`): the 764 M16 per-shape
triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15
triplet (`m15-v0/mid/full.bin`, second sample). Work dir
`/Volumes/Extreme SSD/m21/`; evidence `local/research/M21/`.

Input shas (sha256 full, from the run receipt; s0 + m15 + 701
prefixes match M17/M18/M19/M20):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m21.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M20 exactly.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m21.py` invocation (the receipt, 7.5 s, exit 0 — the estimator
was never changed); one `control.py` invocation (green first try).
No defects, no superseded runs.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m21.py receipt | 7.5 s | exit 0; all guards pass; canon `70ab3af9…f969d` |
| control.py | <1 s | green; both controls pass exactly |

Per-stage wall (receipt run, sequential, no pool):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Task 1 (s0 + m15 incl. 6 BFS passes) | 2 | 1.0 s |
| Task 1.1 (764-shape map pass) | 764 | 5.7 s |
| Task 2 (EFB pool + joint + 10 resynths + rules) | 10 | <1 s |
| Determinism re-run (Task 1 on s0, 3 BFS passes) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m21.py` wall | — | 7.5 s |

## Step 2 — estimates

### Task 1.1 — static-site maps (deterministic or scattered?)

Cell-6 membership recomputed from the dumps: 2368 s0 / 1476 m15
raw, Y 463/439 — M19's counts matched EXACTLY (stop rule not
triggered). ε==0 count reads 0, ε==mid−full identity True, both
frames.

Per-shape static counts (764 M16 triplets; R_s recompute matches
`loo.txt` on 764/764, 0 mismatches; full 764-row table in
`m21.txt`):

| Field | min | med | mean | max |
| --- | ---: | ---: | ---: | ---: |
| static bytes | 1649 | 2368 | 2365.9 | 2523 |

(The min/med/mean/max row reproduces M19's coarse static row
1649/2368/2365.9/2523 exactly — same quantity.)

Map overlap (Jaccard of byte sets; printed 1.0000 ⟹ byte-identical:
a one-byte diff reads 2367/2369 = 0.9992):

| Field | min | med | mean | max |
| --- | ---: | ---: | ---: | ---: |
| J(R_t, R_s0) all 764 | 0.0747 | 1.0000 | 0.9953 | 1.0000 |
| J(R_t, R_s0) t≠0 | 0.0747 | 1.0000 | 0.9953 | 1.0000 |
| J(R_t, R_m15) | 0.0207 | 0.0245 | 0.0245 | 0.0303 |

518/764 shapes read byte-identical maps to s0 (t=0 included);
below 0.99: 65 shapes; below 0.95: 9; below 0.90: 2.
J(R_s0, R_m15) = 0.0245 (inter 92, union 3752).

Below-0.95 rows (shape, static B, Jaccard):

| shape | stat | J vs s0 |
| ---: | ---: | ---: |
| 700 | 2523 | 0.0747 |
| 694 | 1649 | 0.6565 |
| 693 | 2202 | 0.9161 |
| 368 | 2305 | 0.9358 |
| 367 | 2355 | 0.9412 |
| 342 | 2358 | 0.9449 |
| 3 | 2414 | 0.9447 |
| 4 | 2434 | 0.9481 |
| 410 | 2354 | 0.9472 |

Per-site persistence occ[o] = #{t : o ∈ R_t} over 764 shapes:

| Population | 0 | 1 | 2–3 | 4–7 | 8–15 | 16–63 | 64–763 | 764 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all offsets | 566796 | 4064 | 207 | 4 | 1 | 0 | 2368 | 0 |
| R_s0 sites | 0 | 0 | 0 | 0 | 0 | 0 | 2368 | 0 |
| R_m15 sites | 1297 | 76 | 11 | 0 | 0 | 0 | 92 | 0 |

Max occ = 763 (163 sites; no site reads 764). R_s0 sites:
mean occ 761.4, ≥50% on 2368/2368. R_m15 sites: mean occ 47.5,
≥50% on 92/1476. (The 2368 offsets with occ≥64 are exactly R_s0's
sites; the 92 recurring R_m15 sites are the R_s0 ∩ R_m15 set —
tabled as measured.)

### Task 1.2 — value table (ε = mid−v0)

ε signed range + |ε| distribution (full per-value counts in
`m21.txt`):

| Frame | range | ε hist | |ε| hist [1,2–3,4–7,8–15,16+] | max | mean | P(|ε|=1) |
| --- | --- | --- | --- | ---: | ---: | ---: |
| s0 | [−2,+3] | −2:1 −1:1157 +1:1184 +2:23 +3:3 | [2341, 27, 0, 0, 0] | 3 | 1.013 | 0.9886 |
| m15 | [−7,+3] | −7:1 −4:1 −2:2 −1:714 +1:715 +2:42 +3:1 | [1429, 45, 2, 0, 0] | 7 | 1.037 | 0.9682 |

Per-plane split (Y vs U/V — static is a chroma-majority
phenomenon; chroma reads all-±1 on both frames):

| Frame | plane | n | share | mean ε | mean |ε| |
| --- | --- | ---: | ---: | ---: | ---: |
| s0 | Y | 463 | 0.196 | 0.201 | 1.065 |
| s0 | U | 883 | 0.373 | 0.012 | 1.000 |
| s0 | V | 1022 | 0.432 | −0.023 | 1.000 |
| m15 | Y | 439 | 0.297 | 0.296 | 1.125 |
| m15 | U | 475 | 0.322 | −0.078 | 1.000 |
| m15 | V | 562 | 0.381 | −0.036 | 1.000 |

P(ε>0) = 0.5110 s0 / 0.5136 m15 — reproduces M19's cell-6 byte
negrates exactly (same quantity: 1210/2368, 758/1476).
Table-level comparison vs M20's interior δ: ±1 mass 98.9%/96.8%
here vs 85.9%/83.5% interior; luma share 19.6%/29.7% here vs
97.8%/94.2% interior.

### Task 1.3 — position table (band / edge / gradient joins)

Band cut (M19 thirds verbatim; s0-Y [15,186,262], s0-raw
[803,840,725], m15-Y [40,217,182] all match M19 exactly;
m15-raw [235,613,628] is new):

| Frame | unit | top | mid | bot |
| --- | --- | ---: | ---: | ---: |
| s0 | Y (want) | 15 | 186 | 262 |
| s0 | raw (want) | 803 | 840 | 725 |
| m15 | Y (want) | 40 | 217 | 182 |
| m15 | raw (new) | 235 | 613 | 628 |

ε vs edge distance (Manhattan px to nearest MOVED site, same
plane — DESIGN.md source flip; dmin=1 on all 6 plane/frames by
construction; bg = mean d over ALL static sites, same BFS):

| Frame | plane | d=1 n/mean/amean | d=2 | d=3 | d=4 | d=5+ | bg n/meand | dmax |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| s0 | Y | 330/0.16/1.07 | 72/0.47/1.08 | 21/−0.05/1.00 | 13/−0.39/1.00 | 27/0.48/1.00 | 253331/11.66 | 15 |
| s0 | U | 393/−0.01/1.00 | 290/0.07/1.00 | 128/0.05/1.00 | 43/−0.21/1.00 | 29/−0.10/1.00 | 137400/8.67 | 19 |
| s0 | V | 431/−0.02/1.00 | 313/0.02/1.00 | 162/−0.17/1.00 | 68/−0.03/1.00 | 48/0.17/1.00 | 137733/8.77 | 15 |
| m15 | Y | 362/0.24/1.10 | 62/0.84/1.29 | 7/−0.43/1.00 | 2/−1.00/1.00 | 6/−0.33/1.00 | 269187/31.77 | 10 |
| m15 | U | 249/−0.12/1.00 | 141/−0.08/1.00 | 54/0.04/1.00 | 16/0.25/1.00 | 15/−0.07/1.00 | 139666/23.11 | 14 |
| m15 | V | 283/0.06/1.00 | 167/−0.19/1.00 | 65/−0.08/1.00 | 26/0.08/1.00 | 21/−0.14/1.00 | 139729/22.29 | 14 |

(d=1 shares of static sites: s0-Y 71.3% / s0-U 44.5% / s0-V
42.2%; m15-Y 82.5% / m15-U 52.4% / m15-V 50.4%. Full sd rows +
(dr,dc) crosses in `m21.txt`; s0-Y cross peaks at (dr,dc)=(1,0)
with 215/463.)

ε vs M18-P1 gradient decile (M18 code verbatim; rounded edges
match m18.txt exactly on both frames — guard OK). Static Y
bytes per decile (n / mean ε / mean |ε|):

| dec | s0 | m15 |
| ---: | --- | --- |
| 0 | 50 / 0.28 / 1.00 | 9 / −0.11 / 1.00 |
| 1 | 37 / 0.19 / 1.00 | 23 / 0.26 / 1.04 |
| 2 | 0 (tied edges, as M18) | 26 / −0.15 / 1.00 |
| 3 | 53 / −0.02 / 1.04 | 42 / 0.17 / 1.02 |
| 4 | 43 / 0.14 / 1.02 | 26 / 0.35 / 1.04 |
| 5 | 35 / 0.06 / 1.03 | 37 / 0.46 / 1.11 |
| 6 | 75 / 0.45 / 1.23 | 102 / 0.78 / 1.29 |
| 7 | 59 / 0.32 / 1.10 | 59 / 0.27 / 1.15 |
| 8 | 63 / 0.10 / 1.02 | 52 / −0.12 / 1.00 |
| 9 | 48 / 0.12 / 1.04 | 63 / 0.10 / 1.14 |

(Dec-9 share of static Y: 10.4% s0 / 14.4% m15 — vs 62.8%/65.0%
for interior Y. U/V secondary joins rise toward dec-9: s0-U
137/883, s0-V 143/1022, m15-U 126/475, m15-V 161/562 in dec-9;
full rows in `m21.txt`.)

### Task 2.1 — EFB-copy diffing (cross-shape static-region rates)

Pooled mid≠v0 rates on static sites inside vs outside the fixed
residual mask (DESIGN.md §Task 2.1):

| Mask / shapes | in_diff/in_n | in_rate | out_diff/out_n | out_rate | ratio |
| --- | --- | ---: | --- | ---: | ---: |
| R_s0, t≠0 | 1800689/1805836 | 0.997150 | 4518/401447144 | 0.000011 | 88601.8 |
| R_s0, all 764 | 1803057/1808204 | 0.997154 | 4518/401973240 | 0.000011 | 88718.2 |
| R_m15, all 764 | 70137/926819 | 0.075675 | 1737438/402854625 | 0.004313 | 17.547 |

Self-frame arithmetic guard t=0: in=1.0000, out=0.0000 (want
1.0/0.0 — OK). in0(t≠0) distribution: min/med/mean/max =
0.1630/1.0000/0.9970/1.0000 (min on shape 700).

### Task 2.2 — U/V-majority joint (same chroma pixel)

Population = chroma px with BOTH planes static; residual ⟺ mid≠v0:

| Frame | pop | both | U-only | V-only | neither | P(U) | P(V) | P(V\|U) | P(V\|¬U) | exp. | act/exp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 133432 | 83 | 697 | 803 | 131849 | 0.0058 | 0.0066 | 0.1064 | 0.0061 | 5.2 | 16.025 |
| m15 | 137603 | 28 | 366 | 424 | 136785 | 0.0029 | 0.0033 | 0.0711 | 0.0031 | 1.3 | 21.635 |

### Task 2.3 — carrier cut + HUD split + rule synths

Static bytes inside each top-10 removed mask (removed counts +
bands + s0-Y-in-mask reproduce M18/M19 exactly — guards OK; U/V
via co-located Y (r,2c), new):

| rank | shape | nrem | s0-Y in (want) | s0-U in | s0-V in | Y share |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 694 | 4888 | 12 (12) | 132 | 128 | 0.0259 |
| 2 | 693 | 1208 | 5 (5) | 16 | 36 | 0.0108 |
| 3 | 701 | 649 | 2 (2) | 3 | 5 | 0.0043 |
| 4 | 368 | 448 | 39 (39) | 2 | 13 | 0.0842 |
| 5 | 369 | 248 | 6 (6) | 4 | 10 | 0.0130 |
| 6 | 366 | 244 | 19 (19) | 4 | 6 | 0.0410 |
| 7 | 370 | 191 | 12 (12) | 3 | 3 | 0.0259 |
| 8 | 376 | 174 | 10 (10) | 0 | 4 | 0.0216 |
| 9 | 748 | 190 | 17 (17) | 7 | 4 | 0.0367 |
| 10 | 750 | 202 | 8 (8) | 7 | 5 | 0.0173 |

(Max Y share 0.0842 — M19's bound reproduced. Max U/V shares:
0.1495/0.1252, both in the rank-1/694 mask.)

HUD region = union of removed-Y masks {368,369,366,370,376,748}
(DESIGN.md definition, fixed before running): nYpx = 1480, bands
[0, 0, 1480] (all bottom band).

| Frame | statY in/out (share) | statU in | statV in | raw in (share) |
| --- | --- | ---: | ---: | --- |
| s0 | 103/360 (0.2225) | 20 | 40 | 163 (0.0688) |
| m15 | 7/432 (0.0159) | 6 | 8 | 21 (0.0142) |

(m15 joined against the same s0-derived masks, labeled. s0 Y_in
103 = 39+6+19+12+10+17 — the six HUD masks are disjoint on
static-Y, tabled as measured.)

Static-site rule synths (fixed rules: predict v0±1 clipped on
static sites, Model 0 elsewhere; reference predict-v0 == Model 0):

| Frame | rule | cell-6 hits | R | explained (R_0 − R) | e | fnv |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| s0 | v0+1 | 1184 | 547727 | −524912 | −23.0073 | `2272316e4160df15` |
| s0 | v0−1 | 1157 | 547754 | −524939 | −23.0085 | `e692e49d9df77261` |
| m15 | v0+1 | 715 | 559809 | −546391 | −40.7207 | `6084cc3b24e7d6b8` |
| m15 | v0−1 | 714 | 559810 | −546392 | −40.7208 | `afc2cd5c2fe85688` |

(Cell-6 hits equal #{ε==±1} exactly (1184/1157 s0, 715/714
m15); full-frame R explodes because the rule breaks every
triple-equal static site — tabled both ways.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-S1 (±1, N=500) | 2868 sites, set exact, values exact, orig kept | exact | True |
| C-S2 (±2, N=500) | 2868 sites, set exact, values exact, orig kept | exact | True |

(Both pass first try: injected +1×250/−1×250 (C-S1) and
+2×250/−2×250 (C-S2) on disjoint triple-equal sites; recomputed
cell 6 = R_s0 ∪ injected exactly, original members' ε unchanged.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0) pass1 `70ab3af9…f969d` vs pass2
`70ab3af9…f969d`, identical=True; cell counts identical=True.

## Step 3 — attribute

Model comparison (cell-6 bytes; best fixed rule per frame, with
full-frame R alongside):

| Frame | Model | cell-6 R | explained | e | full-frame R / e |
| --- | --- | ---: | ---: | ---: | --- |
| m16 s0 | 0 blend (ε≠0 stands) | 2368 | 0 | 0.0000 | 22815 / 0.0000 |
| m16 s0 | rule v0+1 | 1184 | 1184 | 0.5000 | 547727 / −23.0073 |
| m16 s0 | rule v0−1 | 1211 | 1157 | 0.4886 | 547754 / −23.0085 |
| m15 | 0 blend | 1476 | 0 | 0.0000 | 13418 / 0.0000 |
| m15 | rule v0+1 | 761 | 715 | 0.4844 | 559809 / −40.7207 |
| m15 | rule v0−1 | 762 | 714 | 0.4837 | 559810 / −40.7208 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_MAP | median J(R_t, R_s0) over t≠0 ≥ 0.50 | 1.0000 (518/764 byte-identical) — met |
| H2_VAL | P(\|ε\|==1) over s0 static bytes ≥ 0.75 | 0.9886 (m15: 0.9682) — met |
| H3_SIGN | majority ε-sign share ≥ 0.75 on s0 | 0.5110 (m15: 0.5136) — not met |
| H4_EFB | pooled in/out rate ratio (R_s0, t≠0) ≥ 2 | 88601.8 (0.997150/0.000011) — met |
| H5_CONC | some band ≥75% of s0 static Y, or some carrier ≥50%, or HUD ≥75% | max 0.5659 band / 0.0842 carrier / 0.2225 HUD — not met |
| N | cell 6 after best fixed rule + remaining split | +1 hits 1184; 1184 B stands in cell 6 (full-frame −524912), split below |

Where each test discriminates vs not: Task 1.1 discriminates by
map identity (518/764 byte-identical to s0; 9 shapes below 0.95,
2 below 0.90) and by sample (m15 Jaccard 0.0245 vs ≥0.94 for
755/764 M16 shapes). Task 1.2 discriminates by magnitude
(98.9%/96.8% ±1, chroma all-±1) but not by sign (0.51/0.51).
Task 1.3 discriminates by edge distance (71%/82% Y at d=1 vs
background means 11.7/31.8) but not by gradient decile on Y
(flat s0, dec-6 bump m15 — unlike interior's 63%/65% dec-9).
Task 2.1 discriminates inside/outside 88602× pooled (the map
identity restated) with m15's mask at 17.5×. Task 2.2
discriminates U&V pairing (16.0×/21.6× independence). Task 2.3
discriminates per carrier (694 holds 15%/13% of static U/V; HUD
draws hold 0–39 Y each) but nothing concentrates to bar level;
no fixed rule shrinks R_0 (best full-frame −524912).

Updated deliverable — explained vs standing remainder:

| Content | Bytes (m16 s0) | Behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (M16, unchanged) |
| endpoint-max component | 17089 of R_0 (74.9%) | mid==bright endpoint (M19, unchanged) |
| endpoint-min component | 662 of R_0 (2.9%) | mid==dark endpoint (M19, unchanged) |
| moved-outside component | 221 of R_0 (1.0%) | 159 above / 62 below (M19, unchanged) |
| interior residual | 2475 of R_0 (10.9%) | strict interior (M19/M20, unchanged) |
| static-site ε=+1 mass | 1184 of cell 6 (50.0%) | + rule-+1-explained (full-frame −524912) |
| static-site ε=−1 mass | 1157 of cell 6 (48.9%) | − rule-−1-explained (full-frame −524939) |
| static-site \|ε\|≥2 | 27 of cell 6 (1.1%) | +2:23 +3:3 −2:1, all Y |
| standing static remainder | 1184 of cell 6 (50.0%) | after best fixed rule; ε/sign/edge/decile/carrier tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 1184 B rule-explained within cell 6 only; rest split above |

Screenshot (committed): `m21-staticmap.png` 91498 B (dimmed
truth + static Y px colored by ε sign: red/blue tracing mountain
silhouettes, god-ray shafts, rider, fence, and HUD glyphs). The
map discriminates spatially (sites hug edges/structures, matching
the 71%/82% d=1 table), so it is included. Total 91498 B (budget
5242880).

Recorded without verdict: 518/764 shapes read byte-identical
static-site maps to s0 (only 700/694 below 0.90) while m15 shares
92/1476 sites; ε is ±1 on 2341/2368 static bytes (98.9% s0,
96.8% m15) with chroma all-±1; static sites read 71.3%/82.5% at
d=1 from moved edges with flat Y gradient-decile spread;
same-pixel U&V co-residual reads 16.0×/21.6× independence; the
HUD union holds 103/463 s0-Y static px; the best fixed rule hits
1184/2368 cell-6 bytes and breaks full-frame R (−524912).

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| static-site suite + ε definition + HUD-region definition + falsification bars, recorded before running | recorded | `DESIGN.md`: 764-shape maps + Jaccard/persistence, ε hists + plane split, band/BFS/P1 joins, cross-shape EFB rates, U/V joint, carrier + HUD cuts, fixed rules, bars H1–H5/N |
| map/ε/position tables + EFB-diff tables + wall/exit/shas/determinism | measured | §Step 2: Jaccard/persistence dists; ε hists both frames; band/edge/P1 joins; pooled EFB ratios; U/V joints; carrier + HUD splits; rules; 7.5 s; re-run identical |
| explained-vs-standing update (does any static-site rule shrink cell 6? by how much?) + gap rows | measured | §Step 3: best fixed rule 1184 B in-cell (full-frame negative); 1184 B stands; gaps below |
| screenshot if a static-site map discriminates (or absence reasoned) | measured | 1 PNG, 91498 B: ε-sign map, edge-hugging, spatially discriminating |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
cp local/research/M21/m21.py local/research/M21/control.py "/Volumes/Extreme SSD/m21/"
python3 m21.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m21" /Users/bradrichardson/dev/ssx3/local/research/M21 > m21.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M21/` — `DESIGN.md`
(suite + bars, recorded before running), `m21.py` (map pass +
Jaccard/persistence + ε hists + BFS edge + P1 join + EFB rates +
U/V joint + carrier/HUD cuts + rule synths + PNG writer),
`control.py` (2 synthetic static-site injection controls),
`REPORT.md` (this file), `m21-staticmap.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m21/` —
`m21.txt` (receipt: shas, baselines, Task-1 ε/edge/P1 tables both
frames, 764-row map table, pooled EFB rates, U/V joints, carrier
+ HUD splits, rule synths, re-run, PNG size), `control.txt`,
`m21.py`, `control.py` (working copies), `m21-staticmap.png`
(working copy). No writes into `m15/`, `m16/`, `m17/`, `m18/`,
`m19/`, `m20/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Shape-700 map divergence (new): shape 700's static map reads
   Jaccard 0.0747 vs s0 (2523 B) while 518/764 shapes read
   byte-identical (694 next-lowest at 0.6565). Needs its own
   brief: per-byte attribution of 700's private sites (static-set
   change vs mid change), offline — no new harness code.
2. m15 map disjointness (new): m15 shares 92/1476 sites with s0
   (Jaccard 0.0245); 1297/1476 never recur on any M16 shape.
   Needs its own brief only if cross-sample map identity
   matters: second-sample map family, offline — no new harness
   code.
3. U/V co-residual mechanism (new): same-pixel U&V co-residual
   reads 16.0×/21.6× the independence expectation. Needs its own
   brief only if chroma pairing matters: joint (εu, εv)
   sign/magnitude table, offline — no new harness code.
4. Interior far-tail mechanism (M20 gap 1, still open): 102 B
   with |δ|≥8 on s0 (max 47; all outside the 701 mask; 134 B on
   m15). Needs its own brief: locate + plane/region isolation of
   the tail bytes, offline — no new harness code.
5. δ-sign mechanism (M20 gap 2, still open, minor): δ>0 on
   80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈
   0.70 on both frames. Needs its own brief only if the sign
   asymmetry matters: joint (gap, parity, carrier) sign tables,
   offline — no new harness code.
6. m15 below-min far tail (M19 gap 3, still open, minor): 4
   below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
   own brief only if outlier isolation matters, offline — no new
   harness code.
7. Negative-share mechanism (M18 gap 2, still open): 93
   negatives (worst −244) unattributed at byte level. Needs its
   own brief: per-shape added-residual maps + EFB-copy diffing,
   offline — no new harness code.
8. Odin port readiness (M18 gap 3, still open): no Odin
   contract in-repo; handoff artifact stays `loo.txt` +
   dumps + synths. Needs its own brief once the consumer names
   its interface.
9. Top-HUD glyph residual isolation (M18 gap 4, still open):
   bottom-HUD draws identified; top-band glyph edges in the long
   tail. Needs its own brief if draw-level top-HUD isolation
   matters.
10. Per-carrier weight centers (M18 gap 5, still open,
    optional): effect-draw argmins at the fine-grid edge. Needs
    its own brief only if per-draw filter centers matter.

## What I could not do

1. Jaccard printed to 4 decimals: 1.0000 ⟹ byte-identical sets
   (a one-byte diff reads 2367/2369 = 0.9992) — tabled with the
   arithmetic noted, not chased.
2. No per-shape ε-value comparison: the 764-shape pass compares
   maps only; ε values are s0 + m15.
3. U/V-native gradient join: P1 deciles are Y-native (M18
   verbatim); U/V bytes got the co-located-Y secondary join
   only — tabled, not chased.
4. Fixed ±1 rules only: no mixed, per-plane, or adaptive
   static-site predictors attempted.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M21/`: `DESIGN.md`, `m21.py`,
`control.py`, `REPORT.md` (this file), `m21-staticmap.png`
(91498 B total).
