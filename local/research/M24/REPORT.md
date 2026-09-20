# M24 — K45+ near-hit mass: residual-sign tables + sub-rounding fits: REPORT

M23 gap 1 worked at table level: the signed K45+ residuals r =
δ−round(0.45·g) on the 102 s0 / 134 m15 tail bytes are tabulated
against (gap sign, frac(0.45·g) half, gap parity, band×decile
cell, gap bin, streak column); 4 fixed sub-rounding corrections
scored by exact byte match (hit = exact, near-hit |err|≤1
tabled separately, never merged). Best is SIGN (δ =
round(0.45·g) ± 1 by gap side: +1 on negative gaps, −1 on
positive): 21/102 s0 + 28/134 m15 exact hits (49 pooled) vs the
14/15 K45+ baseline; FRAC reads uniform −1 both halves both
frames; PARITY/POS drift cross-frame. Fully offline — no lease
of any kind, no boots, no harness code, no `adb`. No device
work. Runbook `local/muse/prompts/M24.md`. Tables, no verdicts.

Headers read first: `local/research/M23/REPORT.md` (all of it:
102/134 tail, 14/15 exact + 32/49 near under K45+, errvalue
counts s0 `0:14 1:32 2:25 3:12 …` max 93 / m15 `0:15 1:49 …`
max 46, POS medians, streak columns c257/277/296/301/321/
340–343, gap bins 16–31/32–63/64+) plus M22's ρ-regime tables
for the gap-context precedent (ρ peak [0.4,0.5), sign-gap
agreement ~90%).

Time box 4 hours (start 2026-09-20 02:28 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m23/` — all outputs went to the new
`/Volumes/Extreme SSD/m24/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15 triplet
(`m15-v0/mid/full.bin`, second sample). Work dir `/Volumes/Extreme
SSD/m24/`; evidence `local/research/M24/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M23):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m24.txt` §inputs.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M23 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m24.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed); two `control.py` invocations (the
first failed N on a control-feasibility defect, tabled below —
not a result; the second is green).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m24.py receipt | 0.2 s | exit 0; all guards pass; canon `fc3b625b…fabd7ccad` |
| control.py run 1 (bulk-only pool) | <1 s | superseded: C-R1 chose 40/60 (see below) |
| control.py run 2 (union pool) | <1 s | green; 162 set exact; identity FRAC 60/60 unique |

Defect (control feasibility: the ±1 pushes small-gap injections
out): rev-1 C-R1 pooled interior-bulk sites with gap≥17 only
(248 candidates) per DESIGN.md, but the injected δ = K45+(g) ± 1
lands outside the strict-inside bound or below |δ|≥8 on most of
them (e.g. g=17: K45+=8, +1 reads 9 outside, −1 reads 7 below
tail) — chose 40/60. Fix (control-only; `m24.py` untouched):
rev-2 pools bulk gap≥17 (248) PLUS endpoint sites with gap≥32
(90, M22 C-T2 precedent), union 338 in offset order; chooses
60 with 8 skips. The `m24.py` receipt is unaffected
(control-only defect; the estimator never changed).

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 residual tables) | 2 | 0.0 s |
| Task 2 (fits + scores + xframe + 3 xshape) | 5 | <1 s |
| Determinism re-run (Task 1 on s0) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m24.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — residual-sign tables

Cell-7 membership + tail membership + K45+ residuals recomputed
from the dumps: 2475/2539 cell + 102/134 tail with sub-bins
28+74 / 50+84 and max 47/48, K45+ exact 14/15 + near 32/49
with errvalue strings matching M23 byte-for-byte — M23's counts
matched EXACTLY (stop rule not triggered). δ==0 count reads 0;
P(δ>0) reproduces M19/M20 0.8093/0.8019. Tail planes read
102/0/0 s0 and 134/0/0 m15 (Y/U/V). SIGN-zero level reads n=0
both frames (g≠0 throughout the tail).

Residual-sign joint per split per frame (r classes m1/z/p1/other
= r=−1 / r=0 / r=+1 / |r|>1; full signed-r lists in `m24.txt`):

| Frame | split | level | n | m1/z/p1/other | mean r |
| --- | --- | ---: | ---: | --- | ---: |
| s0 | SIGN | neg | 17 | 0/4/6/7 | 3.824 |
| s0 | SIGN | pos | 85 | 15/10/11/49 | −6.459 |
| s0 | FRAC | LO | 45 | 8/7/7/23 | −6.378 |
| s0 | FRAC | HI | 57 | 7/7/10/33 | −3.456 |
| s0 | PARITY | even | 52 | 5/7/5/35 | −6.231 |
| s0 | PARITY | odd | 50 | 10/7/12/21 | −3.200 |
| m15 | SIGN | neg | 24 | 3/4/6/11 | 1.083 |
| m15 | SIGN | pos | 110 | 22/11/18/59 | −5.673 |
| m15 | FRAC | LO | 66 | 12/7/15/32 | −5.152 |
| m15 | FRAC | HI | 68 | 13/8/9/38 | −3.794 |
| m15 | PARITY | even | 66 | 12/9/4/41 | −5.712 |
| m15 | PARITY | odd | 68 | 13/6/20/29 | −3.250 |

| Frame | POS cell | n | m1/z/p1/other | mean r |
| --- | --- | ---: | --- | ---: |
| s0 | b0d0 | 2 | 0/1/1/0 | 0.500 |
| s0 | b0d1 | 67 | 14/8/10/35 | −0.761 |
| s0 | b1d0 | 6 | 1/0/1/4 | −13.000 |
| s0 | b1d1 | 19 | 0/2/4/13 | −16.158 |
| s0 | b2d0 | 2 | 0/0/0/2 | −3.000 |
| s0 | b2d1 | 6 | 0/3/1/2 | −7.167 |
| m15 | b0d0 | 3 | 0/2/1/0 | 0.333 |
| m15 | b0d1 | 72 | 18/7/11/36 | −0.125 |
| m15 | b1d0 | 1 | 0/0/1/0 | 1.000 |
| m15 | b1d1 | 4 | 1/2/0/1 | −4.750 |
| m15 | b2d0 | 19 | 3/2/4/10 | −6.842 |
| m15 | b2d1 | 35 | 3/2/7/23 | −12.629 |

(gap, r) joint per M23 gap bin:

| Frame | \|g\| bin | n | m1/z/p1/other | mean r | mean \|r\| |
| --- | --- | ---: | --- | ---: | ---: |
| s0 | 16–31 | 22 | 2/9/5/6 | 1.500 | 4.318 |
| s0 | 32–63 | 40 | 8/3/8/21 | −3.550 | 4.150 |
| s0 | 64+ | 40 | 5/2/4/29 | −9.375 | 10.275 |
| m15 | 16–31 | 24 | 3/9/8/4 | −0.417 | 2.750 |
| m15 | 32–63 | 72 | 20/4/11/37 | −3.819 | 4.681 |
| m15 | 64+ | 38 | 2/2/5/29 | −8.237 | 9.605 |

(±1 mass by bin: s0 7/16/9 of 32; m15 11/31/7 of 49 —
`h4view` lines in the receipt.)

Per top-streak-column r stats (all tail-Y sites in the column;
full r lists in the receipt; band×decile cells = POS table
above, referenced per DESIGN.md):

| Frame | col | n | rows | m1/z/p1/other | mean r |
| --- | ---: | ---: | --- | --- | ---: |
| s0 | 257 | 10 | 23–32 | 0/1/0/9 | −2.200 |
| s0 | 277 | 10 | 23–32 | 3/0/0/7 | −2.000 |
| s0 | 296 | 9 | 24–34 | 1/4/4/0 | 0.333 |
| s0 | 301 | 11 | 23–33 | 6/0/1/4 | −1.273 |
| s0 | 321 | 10 | 23–32 | 3/1/0/6 | −1.600 |
| s0 | 340 | 8 | 24–34 | 1/0/2/5 | 1.875 |
| s0 | 341 | 0 | — | — | — |
| s0 | 342 | 5 | 27–35 | 0/0/3/2 | 1.400 |
| s0 | 343 | 2 | 26–27 | 0/0/0/2 | −2.000 |
| s0 | other | 37 | — | 1/8/7/21 | −11.703 |
| m15 | 257 | 10 | 23–32 | 6/1/0/3 | −1.200 |
| m15 | 277 | 10 | 23–32 | 3/1/0/6 | −1.600 |
| m15 | 296 | 9 | 24–34 | 1/0/4/4 | 1.333 |
| m15 | 301 | 11 | 23–33 | 4/2/3/2 | 0.273 |
| m15 | 321 | 10 | 23–32 | 2/1/0/7 | −1.800 |
| m15 | 340 | 9 | 24–34 | 1/2/1/5 | 1.333 |
| m15 | 341 | 1 | 280–280 | 0/0/0/1 | −18.000 |
| m15 | 342 | 5 | 27–35 | 0/1/1/3 | 1.600 |
| m15 | 343 | 4 | 25–289 | 2/0/0/2 | −1.500 |
| m15 | other | 65 | — | 6/7/15/37 | −8.662 |

(Column r ranges, s0: c257 r∈{−3,−2,0} with 9/10 at −3/−2;
c277 r≤−1 throughout; c296 all |r|≤1; c342 all r≥1
(`1:3 2:2`); c343 `−2:2`. Non-Y tail reads 0 both frames.)

### Task 2 — sub-rounding fits (fixed 4-list, exact-hit scoring)

Fits (DESIGN.md fixed list; no additions; empties none on s0 or
m15):

| Correction | s0 c values | m15 c values |
| --- | --- | --- |
| SIGN (neg/pos) | +1/−1, fb −1 | +1/−1, fb −1 |
| FRAC (LO/HI) | −1/−1, fb −1 | −1/−1, fb −1 |
| PARITY (even/odd) | −1/−1, fb −1 | −1/0, fb −1 |
| POS (b0d0…b2d1) | [1,−1,−1,−1,−1,0], fb −1 | [0,−1,1,−1,−1,−1], fb −1 |

(FRAC reads uniform −1 on both halves both frames; PARITY s0
likewise uniform −1 — tabled as measured.)

Same-frame scores (fit = score frame; exact |err| value counts
in the receipt):

| Predictor | s0 hits/rate | s0 near | s0 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| SIGN | 21 / 0.2059 | 35 | 28/5/3/10 |
| FRAC | 15 / 0.1471 | 35 | 34/5/2/11 |
| PARITY | 15 / 0.1471 | 35 | 34/5/2/11 |
| POS | 19 / 0.1863 | 33 | 32/5/2/11 |

| Predictor | m15 hits/rate | m15 near | m15 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| SIGN | 28 / 0.2090 | 38 | 42/6/0/20 |
| FRAC | 25 / 0.1866 | 37 | 45/7/0/20 |
| PARITY | 18 / 0.1343 | 57 | 34/5/0/20 |
| POS | 28 / 0.2090 | 36 | 43/7/0/20 |

Best correction (DESIGN.md rule: s0 hits, then m15 hits, then
list order): SIGN (21 + 28 = 49 pooled). Explained bytes (tail
bytes removed from cell 7): 21/102 s0, 28/134 m15. Residual
|δ−pred| after SIGN:

| Frame | 0 | 1 | 2–3 | 4–7 | 8–15 | 16+ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 21 | 35 | 28 | 5 | 3 | 10 |
| m15 | 28 | 38 | 42 | 6 | 0 | 20 |

(Exact residual value counts in the receipt; max residual 92
s0 / 45 m15.)

Cross-frame check (fit constants on one frame, score on the
other; all 4 corrections carry fitted constants):

| Direction | Predictor | hits/rate | near |
| --- | --- | ---: | ---: |
| fit-s0 → m15 | SIGN | 28 / 0.2090 | 38 |
| fit-s0 → m15 | FRAC | 25 / 0.1866 | 37 |
| fit-s0 → m15 | PARITY (s0 −1/−1) | 25 / 0.1866 | 37 |
| fit-s0 → m15 | POS (s0 medians) | 25 / 0.1866 | 43 |
| fit-m15 → s0 | SIGN | 21 / 0.2059 | 35 |
| fit-m15 → s0 | FRAC | 15 / 0.1471 | 35 |
| fit-m15 → s0 | PARITY (m15 −1/0) | 12 / 0.1176 | 40 |
| fit-m15 → s0 | POS (m15 medians) | 16 / 0.1569 | 35 |

(SIGN fits are identical both frames, hence identical scores
both directions by construction. Same-frame baselines for
comparison: PARITY 15/102 s0 / 18/134 m15; POS 19/102 s0 /
28/134 m15. Full miss |err| hists + errvalues both directions
in the receipt.)

Cross-shape check (best correction SIGN, s0 constants, 3 non-s0
shapes; each shape's tail recomputed from its dumps):

| Shape | tail n | hits/rate | near | miss 2–3/4–7/8–15/16+ | J vs s0 |
| ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 104 | 21 / 0.2019 | 35 | 29/5/3/11 | 0.9619 |
| 2 | 103 | 24 / 0.2330 | 35 | 26/6/1/11 | 0.9159 |
| 733 | 100 | 21 / 0.2100 | 34 | 27/5/3/10 | 0.6694 |

(Jaccards reproduce M22's table; errvalues + J vs m15 in the
receipt.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-R1 (FRAC injection, N=60, union pool; 8 skips) | 162 sites, set exact, values exact, originals unchanged | exact | True |
| C-R1 pattern (r vs frac-half, injected-only) | HI→+1 all / LO→−1 all, r exact | exact | True |
| C-R1 identity (injected-only fits) | argmax FRAC unique, 60/60 | exact | True |

(Pool: 248 bulk gap≥17 + 90 endpoint gap≥32 = 338 union;
injected r plus1=24/minus1=36 (non-degenerate); injected-only
fits read FRAC LO=−1/HI=+1 exactly; other corrections read
25/42/36 on injected-only — tabled. Full-control-frame scores
(fit on control frame): SIGN 30/162, FRAC 51, PARITY 51, POS
55 — tabled. Full tables in `control.txt`; run-1 shortfall
(40/60) in `control-run1.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0) pass1 `fc3b625b…fabd7ccad` vs pass2
`fc3b625b…fabd7ccad`, identical=True; cell counts identical=True;
tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; best fixed correction SIGN):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | ---: |
| m16 s0 | K45+ + SIGN exact hits | 2475 | 21 | 0.0085 |
| m15 | K45+ + SIGN exact hits | 2539 | 28 | 0.0110 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_CORR | best correction exact-hit rate ≥ 0.30 on s0 tail | SIGN 21/102 = 0.2059 (m15: 28/134 = 0.2090) — not met |
| H2_FRAC | FRAC exact-hit rate ≥ 0.25 on s0 tail | 15/102 = 0.1471 (m15: 25/134 = 0.1866) — not met |
| H3_SEP | some level ≥8 s0 \|r\|=1 sites at ≥0.80 one-sign purity | max purity at npm1≥8: FRAC HI 17 @ 0.5882 — not met |
| H4_GAPCONC | some gap bin ≥0.50 of s0 \|r\|=1 sites | 32–63 holds 16/32 = 0.5000 (m15: 31/49 = 0.6327) — met |
| H5_XFER | s0-best fit-s0→m15 rate within 0.15 of s0 rate | SIGN \|0.2090−0.2059\| = 0.0031 — met |
| H6_COLSIGN | named s0 cols (≥4 \|r\|=1) single-sign share ≥ 0.50 | 0/2 (c296 mixed 5, c301 mixed 7) — not met |
| N | cell 7 after best correction's hits + remaining split | 21/28 explained; 81/106 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
gap bin (mean r +1.5/−3.6/−9.4 across 16–31/32–63/64+ on s0;
±1 shares 7/16/9), by position cell (b0d1 holds 24/32 s0 ±1 at
mixed sign; b1d1/b2d1 hold the far negatives, means −16.2/−7.2),
by streak column (c257/277/321 read r≤0 throughout with −3/−2
heavy; c296 reads all |r|≤1; c342 reads all r≥1), and not by
the SIGN/FRAC/PARITY splits (best s0 purity at npm1≥8 is 0.5882;
SIGN-neg reads 6/6 +1 but n=6). Task 2 discriminates by
correction (SIGN 21/28 vs FRAC 15/25 vs PARITY 15/18 vs POS
19/28 same-frame), by transfer (SIGN identical both directions;
PARITY fit-m15→s0 reads 12 vs 15 same-frame; POS 16/25 vs
19/28), and by shape (SIGN reads 21–24 hits on all 3 transfer
shapes including J-0.6694 shape 733).

Updated deliverable — explained vs standing remainder:

| Content | Bytes (m16 s0) | Behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (M16, unchanged) |
| endpoint-max component | 17089 of R_0 (74.9%) | mid==bright endpoint (M19, unchanged) |
| endpoint-min component | 662 of R_0 (2.9%) | mid==dark endpoint (M19, unchanged) |
| moved-outside component | 221 of R_0 (1.0%) | 159 above / 62 below (M19, unchanged) |
| static-site residual | 2368 of R_0 (10.4%) | v0==full≠mid (M19/M21, unchanged) |
| interior ±1 mass | 2127 of cell 7 (86.0%) | δ=±1 (M20, unchanged) |
| interior mid band 2–7 | 246 of cell 7 (9.9%) | 127 + 119 (M20, unchanged) |
| interior far tail, K45++SIGN-hit | 21 of cell 7 (0.8%) | δ=K45+(g)±1 by gap side, exact (this run) |
| interior far tail, standing | 81 of cell 7 (3.3%) | unpredicted; stands (this run) |
| standing interior remainder | 2454 of cell 7 (99.2%) | 2475 − 21 SIGN hits |
| standing remainder (total) | 22794 (99.9% of R_0) | 21 B tail-explained; rest split above |

Screenshot: absent by rule. The workdir residual-sign map
(`m24-rsignmap.png`, 88723 B) colors tail-Y by r (r0 14 / r+1
17 / r−1 15 / other 56 on s0), but DESIGN.md admits an evidence
copy only if an H3 split exists (none: max purity 0.5882 at
npm1≥8) with a ≥0.25 hit-rate gap between its levels — no
pre-registered split qualifies, so no evidence copy is committed
(0 B of 5242880 budget). The workdir copy is retained,
uncommitted.

Recorded without verdict: the signed K45+ residuals read
r∈{−1,0,+1} on 46/102 s0 and 64/134 m15 tail bytes with the
rest spread to −93/+23 (s0) and −46/+18 (m15); no
SIGN/FRAC/PARITY/POS level separates −1 from +1 above 0.5882
purity at n≥8; the 32–63 gap bin holds 16/32 s0 + 31/49 m15 of
the ±1 mass; streak columns read column-coherent r ranges
(c257/277/321 non-positive, c296 all |r|≤1, c342 all positive);
the fixed-list best SIGN reads 21/102 + 28/134 exact with
35/38 near-hits and 21–24 hits on all 3 transfer shapes;
81/106 tail bytes stand after the best rule.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| residual-sign suite + fixed 4-correction list + falsification bars, recorded before running | recorded | `DESIGN.md`: r-sign joints (SIGN/FRAC/PARITY/POS), gapbin/streakcol joins, clamped-median ±1 corrections + best rule fixed, bars H1–H6/N |
| residual tables + fit scores + wall/exit/shas/determinism | measured | §Step 2: 4-split joints + gapbin + streakcol both frames; 4-correction scores + residual + xframe + 3-shape transfer; 0.2 s; re-run identical |
| explained-vs-standing update (does any correction shrink the tail? by how much?) + gap rows | measured | §Step 3: SIGN explains 21/102 + 28/134; 81/106 stands; gaps below |
| screenshot if a residual-sign map discriminates (or absence reasoned) | measured | absent by rule: no H3 split (max purity 0.5882); workdir copy only, 88723 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
cp local/research/M24/m24.py local/research/M24/control.py "/Volumes/Extreme SSD/m24/"
python3 m24.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m24" /Users/bradrichardson/dev/ssx3/local/research/M24 > m24.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

(`control.py` run 1 shortfall kept as `control-run1.txt`;
rev-2 pool fix re-staged and re-run green — §Runs.)

## Paths

Evidence (committed): `local/research/M24/` — `DESIGN.md`
(suite + fixed correction list + bars, recorded before running),
`m24.py` (residual tables + fits + scoring + transfer + PNG
writer), `control.py` (FRAC tail-injection control, rev 2),
`REPORT.md` (this file). No PNG committed (absence reasoned
above).

Large outputs (not committed): `/Volumes/Extreme SSD/m24/` —
`m24.txt` (receipt: shas, baselines, Task-1 residual tables both
frames, fits, 4-correction scores, residual, xframe, 3-shape
transfer, re-run, PNG size), `control.txt`, `control-run1.txt`
(superseded shortfall), `m24.py`, `control.py` (working copies),
`m24-rsignmap.png` (working copy, 88723 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`,
`m23/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. SIGN-corrected near-hit mass (new): 35 s0 / 38 m15 tail
   bytes read |err|=1 after the best correction vs 21/28 exact
   (pooled near 73 vs exact 49). Needs its own brief only if
   second-order structure matters: residual-sign tables around
   K45++SIGN, offline — no new harness code.
2. Streak-column residual coherence (new): s0 c257 reads
   r∈{−3,−2,0} only (9/10 at −3/−2), c296 reads all |r|≤1,
   c342 reads all r≥1, but H6 reads 0/2 single-sign. Needs its
   own brief only if column-local correction matters:
   per-column r-profile tables + column-constant fits,
   offline — no new harness code.
3. Gap-bin 32–63 ±1 concentration (new, H4 met): 16/32 s0 +
   31/49 m15 |r|=1 sites sit in gap bin 32–63. Needs its own
   brief only if gap-local rounding matters: per-gap-value r
   tables within 32–63, offline — no new harness code.
4. Within-streak-column δ profiles (M23 gap 2, still open):
   streak columns read single-sign means (22.7–36.5 positive,
   c342/343 negative) but per-row δ gradients along the r23–33
   columns are untabled beyond the receipt δ lists. Needs its
   own brief: per-row δ profiles + column-gradient fits,
   offline — no new harness code.
5. POS cross-frame collapse (M23 gap 3, still open): POS cell
   medians read 7/16 same-frame but 1/2 cross-frame (M24's POS
   correction reads 19/28 same-frame vs 16/25 cross-frame —
   tabled, same phenomenon at correction level). Needs its own
   brief only if position-value mapping matters: per-cell
   median drift tables s0 vs m15, offline — no new harness
   code.
6. Shape-733 tail divergence (M23 gap 4, still open): shape
   733's tail map reads Jaccard 0.6694 vs s0 (100 B) while
   727/764 shapes read byte-identical (731 next-lowest at
   0.6833). Needs its own brief: per-byte attribution of
   733's private sites (tail-set change vs δ change),
   offline — no new harness code.
7. m15 private tail sites (M23 gap 5, still open): 64/134 m15
   tail sites never recur on any M16 shape (occ 0; Jaccard
   0.4132). Needs its own brief only if cross-sample tail
   identity matters: second-sample tail family, offline — no
   new harness code.
8. Shape-700 map divergence (M21 gap 1, still open): shape
   700's static map reads Jaccard 0.0747 vs s0 while 518/764
   read byte-identical. Needs its own brief: per-byte
   attribution of 700's private sites, offline — no new
   harness code.
9. m15 static-map disjointness (M21 gap 2, still open): m15
   shares 92/1476 static sites with s0 (Jaccard 0.0245).
   Needs its own brief only if cross-sample map identity
   matters, offline — no new harness code.
10. U/V co-residual mechanism (M21 gap 3, still open): same-pixel
    U&V co-residual reads 16.0×/21.6× independence. Needs its
    own brief only if chroma pairing matters, offline — no new
    harness code.
11. δ-sign mechanism (M20 gap 2, still open, minor): δ>0 on
    80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈
    0.70 on both frames. Needs its own brief only if the sign
    asymmetry matters, offline — no new harness code.
12. m15 below-min far tail (M19 gap 3, still open, minor): 4
    below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
    own brief only if outlier isolation matters, offline — no
    new harness code.
13. Negative-share mechanism (M18 gap 2, still open): 93
    negatives (worst −244) unattributed at byte level. Needs
    its own brief: per-shape added-residual maps + EFB-copy
    diffing, offline — no new harness code.
14. Odin port readiness (M18 gap 3, still open): no Odin
    contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
15. Top-HUD glyph residual isolation (M18 gap 4, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
16. Per-carrier weight centers (M18 gap 5, still open,
    optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers
    matter.

## What I could not do

1. No hit-location split table beyond the 4 fixed splits:
   hits/misses are tabulated against SIGN/FRAC/PARITY/POS
   levels (separation view in the receipt) but no
   pre-registered split meets the H3 bar, so the residual-sign
   map's discrimination claim is unsupported — absence
   reasoned, no evidence PNG.
2. No per-shape tail-r comparison beyond 3 shapes: the
   cross-shape check scores shapes 1, 2, 733 only, per brief.
3. No near-hit merging: 73 pooled near-hits stay separate
   from the 49 exact hits by rule (gap 1 tables the
   follow-up).
4. U/V-native residual joins: tail reads all-Y (non-Y n=0,
   SIGN-zero level n=0 both frames), so the co-located-decile
   fallback paths are unexercised — tabled, not chased.
5. FRAC/PARITY degenerate fits: FRAC reads uniform c=−1 on
   both halves both frames (a uniform-shift equivalent, but
   the fixed list holds no uniform-shift member — scored as
   listed, not reformed post-hoc).
6. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M24/`: `DESIGN.md`, `m24.py`,
`control.py`, `REPORT.md` (this file). No PNG (0 B).
