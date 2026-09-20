# M23 — Tail value mechanism: per-site value tables + predictor fits: REPORT

M22 gap 1 worked at table level: the 102 s0 / 134 m15 tail δ
values are tabulated against (gap, position, carrier-context);
9 fixed predictors scored by exact byte match (hit = exact,
near-hit |err|≤1 tabled separately, never merged). Best is
K45+ (δ = round(0.45·g)): 14/102 s0 + 15/134 m15 exact hits
(29 pooled), 32/49 near-hits; STEP 0/102; COMP 13/102; POS
7/102 collapsing to 1/102 cross-frame. Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M23.md`. Tables, no
verdicts.

Headers read first: `local/research/M22/REPORT.md` (all of it:
102/134 tail, max 47/48, 100% luma, top-band + dec-9 heavy,
25/31 8-conn comps, streak columns c257/277/296/301/321/
340–343, max 1 B in any carrier mask, 727/764 maps
byte-identical to s0, Jaccard 0.4132, gaps 17–115 mean ~54, ρ
peak [0.4,0.5) mean|ρ| 0.42/0.40, sign-gap agreement
90.2%/89.6%) plus M20's stencil-fit precedent (fixed candidate
list in DESIGN.md, no additions mid-run) and M21's Task-1.1
map machinery (Jaccard precedent for the cross-shape check).

Time box 4 hours (start 2026-09-20 02:19 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m22/` — all outputs went to the new
`/Volumes/Extreme SSD/m23/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15 triplet
(`m15-v0/mid/full.bin`, second sample). Work dir `/Volumes/Extreme
SSD/m23/`; evidence `local/research/M23/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M22):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m23.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M22 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m23.py` invocation (the receipt, 1.3 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m23.py receipt | 1.3 s | exit 0; all guards pass; canon `fecaa0f8…799cd345` |
| control.py C-V1 (K45+ injection) | <1 s | green; 162/162 set exact, identity K45+ 60/60 unique |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 value tables) | 2 | 0.2 s |
| Carrier masks (10 resynths) | 10 | <1 s |
| Task 2 (fits + scores + xframe + 3 xshape) | 5 | <1 s |
| Determinism re-run (Task 1 on s0) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m23.py` wall | — | 1.3 s |

## Step 2 — estimates

### Task 1 — per-site value tables

Cell-7 membership + tail membership recomputed from the dumps:
2475/2539 cell + 102/134 tail with sub-bins 28+74 / 50+84 and max
47/48 — M22's counts matched EXACTLY (stop rule not triggered).
δ==0 count reads 0; P(δ>0) reproduces M19/M20 0.8093/0.8019.
Tail planes read 102/0/0 s0 and 134/0/0 m15 (Y/U/V).

(gap, δ) joint per frame (|g| bins from M22's hist edges; full
sorted δ lists in `m23.txt`):

| Frame | \|g\| bin | n | distinct δ | mean δ | mean \|δ\| |
| --- | --- | ---: | ---: | ---: | ---: |
| s0 | 2–3 / 4–7 / 8–15 | 0 | 0 | — | — |
| s0 | 16–31 | 22 | 12 | 4.773 | 10.864 |
| s0 | 32–63 | 40 | 21 | 10.650 | 20.500 |
| s0 | 64+ | 40 | 22 | 25.875 | 33.825 |
| m15 | 2–3 / 4–7 / 8–15 | 0 | 0 | — | — |
| m15 | 16–31 | 24 | 10 | 3.917 | 9.833 |
| m15 | 32–63 | 72 | 32 | 9.167 | 18.306 |
| m15 | 64+ | 38 | 21 | 23.842 | 31.684 |

(Exact signed-gap-value table: every distinct g value with n +
δ list in the receipt, collisions flagged. H6 row: s0 23 gap
values with ≥2 sites, 5 all-equal (share 0.2174); m15 30 with
≥2 sites, 4 all-equal (share 0.1333).)

(position, δ) joint: δ stats per band × decile-9/not cell (full
δ lists in the receipt):

| Frame | band | dec9 | n | mean δ | mean \|δ\| |
| --- | ---: | ---: | ---: | ---: | ---: |
| s0 | 0 | 0 | 2 | 4.500 | 12.500 |
| s0 | 0 | 1 | 67 | 21.582 | 27.194 |
| s0 | 1 | 0 | 6 | 5.667 | 18.000 |
| s0 | 1 | 1 | 19 | 3.105 | 18.684 |
| s0 | 2 | 0 | 2 | 14.500 | 14.500 |
| s0 | 2 | 1 | 6 | −1.833 | 12.167 |
| m15 | 0 | 0 | 3 | −9.000 | 14.333 |
| m15 | 0 | 1 | 72 | 16.833 | 24.722 |
| m15 | 1 | 0 | 1 | 10.000 | 10.000 |
| m15 | 1 | 1 | 4 | −6.250 | 10.250 |
| m15 | 2 | 0 | 19 | 12.263 | 16.684 |
| m15 | 2 | 1 | 35 | 7.343 | 16.200 |

Per top-streak-column δ stats (all tail-Y sites in the column;
full δ lists in the receipt):

| Frame | col | n | rows | mean δ | mean \|δ\| |
| --- | ---: | ---: | --- | ---: | ---: |
| s0 | 257 | 10 | 23–32 | 25.500 | 25.500 |
| s0 | 277 | 10 | 23–32 | 24.400 | 24.400 |
| s0 | 296 | 9 | 24–34 | 32.667 | 32.667 |
| s0 | 301 | 11 | 23–33 | 30.818 | 30.818 |
| s0 | 321 | 10 | 23–32 | 22.700 | 22.700 |
| s0 | 340 | 8 | 24–34 | 36.500 | 36.500 |
| s0 | 341 | 0 | — | — | — |
| s0 | 342 | 5 | 27–35 | −18.800 | 18.800 |
| s0 | 343 | 2 | 26–27 | −28.500 | 28.500 |
| s0 | other | 37 | — | 1.784 | 16.486 |
| m15 | 257 | 10 | 23–32 | 17.200 | 17.200 |
| m15 | 277 | 10 | 23–32 | 17.200 | 17.200 |
| m15 | 296 | 9 | 24–34 | 34.000 | 34.000 |
| m15 | 301 | 11 | 23–33 | 26.455 | 26.455 |
| m15 | 321 | 10 | 23–32 | 25.200 | 25.200 |
| m15 | 340 | 9 | 24–34 | 34.556 | 34.556 |
| m15 | 341 | 1 | 280–280 | −9.000 | 9.000 |
| m15 | 342 | 5 | 27–35 | −17.400 | 17.400 |
| m15 | 343 | 4 | 25–289 | −24.250 | 24.250 |
| m15 | other | 65 | — | 5.369 | 16.323 |

(carrier-context, δ): δ stats inside/outside each top-10 mask
(removed counts + bands reproduce M19 exactly — guards OK;
U_in/V_in read 0 on all 10 masks both frames):

| Frame | rank/shape | Y-inside n/mean | Y-outside n/mean/amean |
| --- | --- | ---: | ---: |
| s0 | 1/694, 2/693, 3/701 | 0 | 102 / 15.353 / 23.647 |
| s0 | 4/368 | 1 / 12.000 | 101 / 15.386 / 23.762 |
| s0 | 5–10 | 0 | 102 / 15.353 / 23.647 |
| m15 | all 10 | 0 | 134 / 12.388 / 20.582 |

701 split: s0 tail-Y in/out = 0/102; m15 = 0/134 (M20's
s0 0/102 reproduced; m15 outside-701 mean 12.388, amean 20.582;
inside rows empty — full δ lists in the receipt).

### Task 2 — predictor fits (fixed 9-list, exact-hit scoring)

Fits (DESIGN.md fixed list; no additions): COMP 8-conn
components read 25 s0 / 31 m15 (M22 values reproduced);
per-component predictions + fallbacks (15 s0 / 12 m15) in the
receipt. POS 6-cell medians (band×dec9 order 00/01/10/11/20/21):
s0 [5, 27, 10, 10, 15, −2] fallback 20, empties none; m15
[−14, 20, 10, −9, 15, 10] fallback 16, empties none.

Same-frame scores (fit = score frame; exact |err| value counts
in the receipt):

| Predictor | s0 hits/rate | s0 near | s0 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| K40+ | 9 / 0.0882 | 35 | 26/18/4/10 |
| K40− | 1 / 0.0098 | 5 | 2/1/2/91 |
| K45+ | 14 / 0.1373 | 32 | 37/6/2/11 |
| K45− | 2 / 0.0196 | 3 | 2/1/1/93 |
| STEP1 | 0 / 0.0000 | 0 | 0/2/30/70 |
| STEP2 | 0 / 0.0000 | 0 | 0/5/31/66 |
| STEP3 | 0 / 0.0000 | 0 | 0/8/32/62 |
| COMP | 13 / 0.1275 | 9 | 24/19/27/10 |
| POS | 7 / 0.0686 | 11 | 15/9/33/27 |

| Predictor | m15 hits/rate | m15 near | m15 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| K40+ | 15 / 0.1119 | 42 | 28/29/5/15 |
| K40− | 1 / 0.0075 | 2 | 1/0/5/125 |
| K45+ | 15 / 0.1119 | 49 | 46/3/1/20 |
| K45− | 2 / 0.0149 | 2 | 0/0/0/130 |
| STEP1 | 0 / 0.0000 | 0 | 0/7/49/78 |
| STEP2 | 0 / 0.0000 | 0 | 0/12/45/77 |
| STEP3 | 0 / 0.0000 | 0 | 0/17/46/71 |
| COMP | 17 / 0.1269 | 13 | 27/34/35/8 |
| POS | 16 / 0.1194 | 10 | 6/27/24/51 |

Best predictor (DESIGN.md rule: s0 hits, then m15 hits, then
list order): K45+ (14 + 15 = 29 pooled). Explained bytes (tail
bytes removed from cell 7): 14/102 s0, 15/134 m15. Residual
|δ−pred| after K45+:

| Frame | 0 | 1 | 2–3 | 4–7 | 8–15 | 16+ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 14 | 32 | 37 | 6 | 2 | 11 |
| m15 | 15 | 49 | 46 | 3 | 1 | 20 |

(Exact residual value counts in the receipt; max residual 93
s0 / 46 m15.)

Cross-frame check (fit constants on one frame, score on the
other; K*/STEP* constant-free hence identical by construction;
COMP N/A frame-local per DESIGN.md):

| Direction | Predictor | hits/rate | near |
| --- | --- | ---: | ---: |
| fit-s0 → m15 | K45+ | 15 / 0.1119 | 49 |
| fit-s0 → m15 | K40+ | 15 / 0.1119 | 42 |
| fit-s0 → m15 | POS (s0 medians) | 2 / 0.0149 | 3 |
| fit-s0 → m15 | K−/STEP | 0–2 | 0–2 |
| fit-m15 → s0 | K45+ | 14 / 0.1373 | 32 |
| fit-m15 → s0 | K40+ | 9 / 0.0882 | 35 |
| fit-m15 → s0 | POS (m15 medians) | 1 / 0.0098 | 7 |
| fit-m15 → s0 | K−/STEP | 0–2 | 0–5 |

(Full miss |err| hists + errvalues both directions in the
receipt. Same-frame POS baselines for comparison: 7/102 s0,
16/134 m15.)

Cross-shape check (best predictor K45+, s0 constants, 3 non-s0
shapes; each shape's tail recomputed from its dumps):

| Shape | tail n | hits/rate | near | miss 2–3/4–7/8–15/16+ | J vs s0 |
| ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 104 | 15 / 0.1442 | 32 | 36/7/2/12 | 0.9619 |
| 2 | 103 | 15 / 0.1456 | 34 | 38/4/0/12 | 0.9159 |
| 733 | 100 | 14 / 0.1400 | 31 | 36/6/2/11 | 0.6694 |

(Jaccards reproduce M22's table; errvalues + J vs m15 in the
receipt.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-V1 (K45+ injection, N=60, gap≥17 bulk; 11 skips) | 162 sites, set exact, values exact, originals unchanged | exact | True |
| C-V1 identity (restricted, injected-only) | argmax K45+ unique, 60/60 | exact | True |

(Pool: 248 bulk gap≥17 candidates; injected δ values span
−14…+16 with |δ|≥8 throughout, exact counts in `control.txt`. Full-frame control
scores: K45+ reads 74/162 = 14 baseline + 60 injected; COMP
reads 66/162 with 53/60 on injected-only — tabled. K40+ near
reads 87 = 35 + 52. Full 9-predictor control tables in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0) pass1 `fecaa0f8…799cd345` vs pass2
`fecaa0f8…799cd345`, identical=True; cell counts identical=True;
tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; best fixed predictor K45+):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | ---: |
| m16 s0 | K45+ exact hits | 2475 | 14 | 0.0057 |
| m15 | K45+ exact hits | 2539 | 15 | 0.0059 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_KFIT | best K exact-hit rate ≥ 0.25 on s0 tail | K45+ 14/102 = 0.1373 (m15: 15/134 = 0.1119) — not met |
| H2_STEP | best STEP exact-hit rate ≥ 0.10 on s0 tail | 0/102 all three — not met |
| H3_COMP | COMP exact-hit rate ≥ 0.25 on s0 tail | 13/102 = 0.1275 (m15: 17/134 = 0.1269) — not met |
| H4_POS | POS exact-hit rate ≥ 0.25 on s0 tail | 7/102 = 0.0686 (m15: 16/134 = 0.1194) — not met |
| H5_XFER | s0-best transferable fit-s0→m15 rate within 0.15 of s0 rate | K45+ \|0.1119−0.1373\| = 0.0254 — met |
| H6_GAPDET | signed-gap values (≥2 s0-tail sites) all-equal-δ share ≥ 0.50 | 5/23 = 0.2174 (m15: 4/30 = 0.1333) — not met |
| N | cell 7 after best predictor's hits + remaining split | 14/15 explained; 88/119 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
gap bin (mean |δ| 10.9/20.5/33.8 across 16–31/32–63/64+ on s0;
9.8/18.3/31.7 on m15 — every bin multi-valued, 12/21/22
distinct δ on s0), by position cell (band-0/dec-9 holds 67/102
s0 and 72/134 m15 with the highest cell means), by streak
column (positive columns read means 22.7–36.5, c342/343 read
negative means, c341 reads 0/1 sites), and by carrier
negatively (max 1 B inside any top-10 mask on s0, 0 on m15;
701 holds 0 both frames). Task 2 discriminates by predictor
family (K+ 9–15 exact hits + 32–49 near-hits per frame; K−
1–2 hits; STEP 0; COMP 13/17; POS 7/16 same-frame collapsing
to 1/2 cross-frame), by transfer (K45+ reads 14–15 hits on all
5 scored frames including J-0.6694 shape 733), and by sign
asymmetry (K+ outscores K− 14:2 s0 / 15:2 m15).

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
| interior far tail, K45+-hit | 14 of cell 7 (0.6%) | δ=round(0.45·g) exact (this run) |
| interior far tail, standing | 88 of cell 7 (3.6%) | \|δ\|≥8 unpredicted; stands (this run) |
| standing interior remainder | 2461 of cell 7 (99.4%) | 2475 − 14 K45+ hits |
| standing remainder (total) | 22801 (99.9% of R_0) | 14 B tail-explained; rest split above |

Screenshot: absent by rule. The workdir residual map
(`m23-residmap.png`, 88698 B) colors tail-Y by K45+ outcome
(hit 14 / near 32 / miss 56 on s0), but DESIGN.md admits an
evidence copy only if hits/misses separate by a tabled split
and no pre-registered hit-location split table exists to
support that claim — so no evidence copy is committed (0 B of
5242880 budget). The workdir copy is retained, uncommitted.

Recorded without verdict: the tail reads 102/134 bytes at
100% luma with multi-valued δ in every gap bin (H6 0.2174/
0.1333); streak columns read single-sign means (positive
22.7–36.5 except c342/343 negative); no carrier mask holds
more than 1 tail byte; the fixed-list best K45+ reads 14/102
+ 15/134 exact with 32/49 near-hits and 14–15 hits on all 3
transfer shapes; cross-frame POS reads 1–2 hits vs 7–16
same-frame; 88/119 tail bytes stand after the best rule.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| value-table suite + fixed 9-predictor list + falsification bars, recorded before running | recorded | `DESIGN.md`: (gap,δ)/(position,δ)/(carrier,δ) joints, K40±/K45±/STEP1-3/COMP/POS with rounding + fallbacks + best rule fixed, bars H1–H6/N |
| per-site value tables + fit scores + wall/exit/shas/determinism | measured | §Step 2: gapbin/gapval/poscell/streakcol/carrier tables both frames; 9-predictor scores + residual + xframe + 3-shape transfer; 1.3 s; re-run identical |
| explained-vs-standing update (does any predictor shrink the tail? by how much?) + gap rows | measured | §Step 3: K45+ explains 14/102 + 15/134; 88/119 stands; gaps below |
| screenshot if a predictor-residual map discriminates (or absence reasoned) | measured | absent by rule: no pre-registered hit-location split table; workdir copy only, 88698 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
cp local/research/M23/m23.py local/research/M23/control.py "/Volumes/Extreme SSD/m23/"
python3 m23.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m23" /Users/bradrichardson/dev/ssx3/local/research/M23 > m23.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M23/` — `DESIGN.md`
(suite + fixed predictor list + bars, recorded before running),
`m23.py` (value tables + fits + scoring + transfer + PNG
writer), `control.py` (K45+ tail-injection control),
`REPORT.md` (this file). No PNG committed (absence reasoned
above).

Large outputs (not committed): `/Volumes/Extreme SSD/m23/` —
`m23.txt` (receipt: shas, baselines, Task-1 value tables both
frames, fits, 9-predictor scores, residual, xframe, 3-shape
transfer, re-run, PNG size), `control.txt`, `m23.py`,
`control.py` (working copies), `m23-residmap.png` (working
copy, 88698 B). No writes into `m15/`, `m16/`, `m17/`, `m18/`,
`m19/`, `m20/`, `m21/`, `m22/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. K45+ near-hit mass (new): 32 s0 / 49 m15 tail bytes read
   |err|=1 under round(0.45·g) vs 14/15 exact (pooled near
   81 vs exact 29). Needs its own brief: residual-sign tables
   + sub-rounding fits around 0.45·g, offline — no new
   harness code.
2. Within-streak-column δ profiles (new): streak columns read
   single-sign means (22.7–36.5 positive, c342/343 negative)
   but per-row δ gradients along the r23–33 columns are
   untabled beyond the receipt δ lists. Needs its own brief:
   per-row δ profiles + column-gradient fits, offline — no
   new harness code.
3. POS cross-frame collapse (new): POS cell medians read 7/16
   same-frame but 1/2 cross-frame. Needs its own brief only
   if position-value mapping matters: per-cell median drift
   tables s0 vs m15, offline — no new harness code.
4. Shape-733 tail divergence (M22 gap 2, still open): shape
   733's tail map reads Jaccard 0.6694 vs s0 (100 B) while
   727/764 shapes read byte-identical (731 next-lowest at
   0.6833). Needs its own brief: per-byte attribution of
   733's private sites (tail-set change vs δ change),
   offline — no new harness code.
5. m15 private tail sites (M22 gap 3, still open): 64/134 m15
   tail sites never recur on any M16 shape (occ 0; Jaccard
   0.4132). Needs its own brief only if cross-sample tail
   identity matters: second-sample tail family, offline — no
   new harness code.
6. Shape-700 map divergence (M21 gap 1, still open): shape
   700's static map reads Jaccard 0.0747 vs s0 while 518/764
   read byte-identical. Needs its own brief: per-byte
   attribution of 700's private sites, offline — no new
   harness code.
7. m15 static-map disjointness (M21 gap 2, still open): m15
   shares 92/1476 static sites with s0 (Jaccard 0.0245).
   Needs its own brief only if cross-sample map identity
   matters, offline — no new harness code.
8. U/V co-residual mechanism (M21 gap 3, still open): same-pixel
   U&V co-residual reads 16.0×/21.6× independence. Needs its
   own brief only if chroma pairing matters, offline — no new
   harness code.
9. δ-sign mechanism (M20 gap 2, still open, minor): δ>0 on
   80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈
   0.70 on both frames. Needs its own brief only if the sign
   asymmetry matters, offline — no new harness code.
10. m15 below-min far tail (M19 gap 3, still open, minor): 4
    below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
    own brief only if outlier isolation matters, offline — no
    new harness code.
11. Negative-share mechanism (M18 gap 2, still open): 93
    negatives (worst −244) unattributed at byte level. Needs
    its own brief: per-shape added-residual maps + EFB-copy
    diffing, offline — no new harness code.
12. Odin port readiness (M18 gap 3, still open): no Odin
    contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
13. Top-HUD glyph residual isolation (M18 gap 4, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
14. Per-carrier weight centers (M18 gap 5, still open,
    optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers
    matter.

## What I could not do

1. No hit-location split table: hits/misses are not tabulated
   against component/band/decile splits (not pre-registered),
   so the residual map's discrimination claim is unsupported
   — absence reasoned, no evidence PNG.
2. No per-shape tail-δ value comparison beyond 3 shapes: the
   cross-shape check scores shapes 1, 2, 733 only, per brief.
3. No near-hit merging: 81 pooled near-hits stay separate
   from the 29 exact hits by rule (gap 1 tables the
   follow-up).
4. U/V-native value joins: U/V tail reads n=0 everywhere, so
   the co-located-decile fallback paths are unexercised —
   tabled, not chased.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M23/`: `DESIGN.md`, `m23.py`,
`control.py`, `REPORT.md` (this file). No PNG (0 B).
