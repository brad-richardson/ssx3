# M25 — Within-streak-column δ profiles: per-row gradients + column fits: REPORT

M23 gap 2 worked at table level: per-row δ profiles for the 8
named streak columns on s0 + m15 (row→δ tables with holes, shape
stats, cross-frame match) plus 3 fixed column fits scored by
exact byte match (hit = exact, near-hit |err|≤1 tabled
separately, never merged). Columns read single-sign throughout
(all sign-runs 1) but ragged in value (s0 ranges 11–34, cross-frame agreement 6/65 shared sites); best fit is
CONST (column median δ): 12/65 s0 + 13/68 m15 exact hits (25
pooled) with LINEAR below CONST on both frames (7/4) and
cross-frame CONST collapsing to 0/68 fit-s0→m15. Fully offline —
no lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M25.md`. Tables, no
verdicts.

Headers read first: `local/research/M23/REPORT.md` (all of it:
102/134 tail, per-column n/rows/means + full δ dlists in
`m23.txt`) plus `local/research/M24/REPORT.md` (column
r-coherence tables: c257 r∈{−3,−2,0}, c296 all |r|≤1, c342 all
r≥1 — the residual-level precedent for column-local structure).

Time box 4 hours (start 2026-09-20 02:37 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m24/` — all outputs went to the new
`/Volumes/Extreme SSD/m25/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15 triplet
(`m15-v0/mid/full.bin`, second sample). Work dir `/Volumes/Extreme
SSD/m25/`; evidence `local/research/M25/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M24):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m25.txt` §inputs.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M24 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m25.py` invocation (the receipt, 0.1 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try). Two pre-receipt
typos (an extra `.` and an extra `)` in f-strings) were caught
by `py_compile` staging before the receipt run — not results;
DESIGN.md was recorded before either fix and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m25.py receipt | 0.1 s | exit 0; all guards pass; canon `040c9c75…804eb42` |
| control.py C-P1 (known profiles) | <1 s | green; 60/60 chose; set exact; identity CONST |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 profiles + xmatch) | 2 | 0.0 s |
| Task 2 (fits + scores + xframe) | 2 | <1 s |
| Determinism re-run (Task 1 on s0) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m25.py` wall | — | 0.1 s |

## Step 2 — estimates

### Task 1 — per-row δ profiles

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M22/M23 EXACTLY (stop rule
not triggered). Named-column bytes read 65 s0 / 68 m15.
δ==0 count reads 0; P(δ>0) reproduces M19/M20 0.8093/0.8019.
Tail planes read 102/0/0 s0 and 134/0/0 m15 (Y/U/V).
c257/277/301/321 row ranges match M22's single-column bboxes
r[23,32]/r[23,33] on both frames.

Per-row δ lists per named column (row order; row:δ pairs +
hole ranges in the receipt):

| Frame | col | n | rows | δ in row order | holes |
| --- | ---: | ---: | --- | --- | --- |
| s0 | 257 | 10 | 23–32 | 17 28 30 29 29 29 29 28 23 13 | none |
| s0 | 277 | 10 | 23–32 | 16 25 28 27 27 28 28 28 24 13 | none |
| s0 | 296 | 9 | 24–34 | 21 41 47 35 19 … 31 46 39 15 | 29–30 |
| s0 | 301 | 11 | 23–33 | 18 29 33 41 47 46 39 32 25 16 13 | none |
| s0 | 321 | 10 | 23–32 | 14 24 27 27 26 26 26 25 21 11 | none |
| s0 | 340 | 8 | 24–34 | 17 38 47 45 … 44 47 37 17 | 28–30 |
| s0 | 342 | 5 | 27–35 | −16 −27 −18 … −16 −17 | 30–33 |
| s0 | 343 | 2 | 26–27 | −31 −26 | none |
| m15 | 257 | 10 | 23–32 | 12 18 20 20 19 20 20 19 16 8 | none |
| m15 | 277 | 10 | 23–32 | 12 19 20 20 19 20 20 19 15 8 | none |
| m15 | 296 | 9 | 24–34 | 16 37 46 40 30 … 38 46 37 16 | 29–30 |
| m15 | 301 | 11 | 23–33 | 12 18 24 37 48 47 35 23 16 13 18 | none |
| m15 | 321 | 10 | 23–32 | 14 24 29 31 31 29 28 28 24 14 | none |
| m15 | 340 | 9 | 24–34 | 16 38 47 40 30 … 40 48 38 14 | 29–30 |
| m15 | 342 | 5 | 27–35 | −13 −20 −14 … −19 −21 | 30–33 |
| m15 | 343 | 4 | 25–289 | −22 −34 −26 … −15 | 28–288 (261) |

(… marks the hole span; c341 membership-guarded only: 0 s0 /
1 m15 at r280. m15 c340 carries r28, which s0 lacks; m15 c343
carries r25 + r289, which s0 lacks.)

Column shape stats (sd population; runs over present rows in
row order, holes unbroken; top = first n//2 rows):

| Frame | col | range | sd | signruns | valueruns | topmean | botmean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 257 | 17 | 5.626 | 1 | 7 | 26.600 | 24.400 |
| s0 | 277 | 15 | 5.161 | 1 | 7 | 24.600 | 24.200 |
| s0 | 296 | 32 | 11.235 | 1 | 9 | 36.000 | 30.000 |
| s0 | 301 | 34 | 11.312 | 1 | 11 | 33.600 | 28.500 |
| s0 | 321 | 16 | 5.405 | 1 | 7 | 23.600 | 21.800 |
| s0 | 340 | 30 | 11.790 | 1 | 8 | 36.750 | 36.250 |
| s0 | 342 | 11 | 4.167 | 1 | 5 | −21.500 | −17.000 |
| s0 | 343 | 5 | 2.500 | 1 | 2 | −31.000 | −26.000 |
| m15 | 257 | 12 | 3.894 | 1 | 8 | 17.800 | 16.600 |
| m15 | 277 | 12 | 3.970 | 1 | 8 | 18.000 | 16.400 |
| m15 | 296 | 30 | 10.656 | 1 | 9 | 34.750 | 33.400 |
| m15 | 301 | 36 | 12.543 | 1 | 11 | 27.800 | 25.333 |
| m15 | 321 | 17 | 6.046 | 1 | 8 | 25.800 | 24.600 |
| m15 | 340 | 34 | 11.577 | 1 | 9 | 35.250 | 34.000 |
| m15 | 342 | 8 | 3.262 | 1 | 5 | −16.500 | −18.000 |
| m15 | 343 | 19 | 6.869 | 1 | 4 | −28.000 | −20.500 |

Cross-frame profile match (same sites — M22 identical bboxes —
but same values?):

| col | rows equal? | shared | s0-only | m15-only | agree | mean\|Δ\| |
| ---: | --- | ---: | --- | --- | ---: | ---: |
| 257 | True | 10 | — | — | 0 | 8.300 |
| 277 | True | 10 | — | — | 0 | 7.200 |
| 296 | True | 9 | — | — | 1 | 4.000 |
| 301 | True | 11 | — | — | 0 | 5.636 |
| 321 | True | 10 | — | — | 2 | 2.500 |
| 340 | False | 8 | — | 28 | 2 | 1.875 |
| 342 | True | 5 | — | — | 0 | 4.200 |
| 343 | False | 2 | — | 25, 289 | 1 | 1.500 |

Pooled H5: 6/65 shared sites agree exactly (share 0.0923). No
column reads all-equal.

### Task 2 — column-gradient fits (fixed 3-list, exact-hit scoring)

Fits (DESIGN.md fixed list; no additions; empties none;
SIGNC means never hit 0):

| Fit | s0 constants | m15 constants |
| --- | --- | --- |
| CONST medians (c257…c343) | [29,27,35,32,26,41,−17,−29], fb 27 | [19,19,37,23,28,38,−19,−24], fb 20 |
| LINEAR slopes b | [−0.49,−0.18,−0.32,−1.15,−0.37,−0.06,+0.52,+5.00] | [−0.33,−0.41,−0.00,−0.50,−0.10,−0.02,−0.67,+0.05] |
| SIGNC signs | [+ + + + + + − −] | [+ + + + + + − −] |

(Slopes read near-flat except s0 c343 b=+5.00 over n=2 and s0
c301 b=−1.15; full a/b pairs in the receipt. SIGNC signs are
identical both frames.)

Same-frame scores (fit = score frame; exact |err| value counts
in the receipt):

| Predictor | s0 hits/rate | s0 near | s0 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| CONST | 12 / 0.1846 | 14 | 8/11/13/7 |
| LINEAR | 7 / 0.1077 | 7 | 14/12/21/4 |
| SIGNC | 6 / 0.0923 | 24 | 34/1/0/0 |

| Predictor | m15 hits/rate | m15 near | m15 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| CONST | 13 / 0.1912 | 14 | 9/11/15/6 |
| LINEAR | 4 / 0.0588 | 5 | 21/19/12/7 |
| SIGNC | 8 / 0.1176 | 28 | 32/0/0/0 |

Per-column s0 colhits (CONST/LINEAR/SIGNC): c257 4/0/1, c277
2/2/0, c296 1/0/4, c301 1/0/0, c321 3/2/1, c340 0/0/0, c342
1/1/0, c343 0/2/0 (LINEAR's c343 2/2 is the n=2 exact line;
m15 colhits in the receipt).

Best fit (DESIGN.md rule: s0 hits, then m15 hits, then list
order): CONST (12 + 13 = 25 pooled). Explained bytes (named-
column bytes removed from the tail): 12/65 s0, 13/68 m15.
Residual |δ−pred| after CONST:

| Frame | 0 | 1 | 2–3 | 4–7 | 8–15 | 16+ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 12 | 14 | 8 | 11 | 13 | 7 |
| m15 | 13 | 14 | 9 | 11 | 15 | 6 |

(Exact residual value counts in the receipt; max residual 24
s0 / 25 m15.)

Cross-frame check (fit constants on one frame, score on the
other; all 3 carry fitted constants — no N/A):

| Direction | Predictor | hits/rate | near |
| --- | --- | ---: | ---: |
| fit-s0 → m15 | CONST (s0 medians) | 0 / 0.0000 | 2 |
| fit-s0 → m15 | LINEAR (s0 a/b) | 3 / 0.0441 | 1 |
| fit-s0 → m15 | SIGNC (s0 signs) | 8 / 0.1176 | 28 |
| fit-m15 → s0 | CONST (m15 medians) | 1 / 0.0154 | 4 |
| fit-m15 → s0 | LINEAR (m15 a/b) | 2 / 0.0308 | 7 |
| fit-m15 → s0 | SIGNC (m15 signs) | 6 / 0.0923 | 24 |

(SIGNC signs are identical both frames, hence identical scores
both directions by construction. Same-frame baselines for
comparison: CONST 12/65 s0 / 13/68 m15; LINEAR 7/65 / 4/68.
Full miss |err| hists + errvalues both directions in the
receipt. Note: fit-s0 LINEAR → m15 carries one |err|=1299 —
the s0 c343 line (a=−161, b=+5.0) extrapolated to m15's r289
site — tabled as measured.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 (known profiles, N=60, union pool; 6 skips) | 162 sites, set exact, values exact, originals unchanged | exact | True |
| C-P1 profiles (pseudo-col medians) | +10/+14 all-exact | exact | True |
| C-P1 identity (injected-only fits) | CONST 60/60 + LINEAR 60/60 (b=0.0 tie), argmax CONST by list order | exact | True |

(Pool: 248 bulk gap≥17 + 90 endpoint gap≥32 = 338 union;
injected-only SIGNC reads 0/30 + 1/30 — tabled. Full-control-
frame scores, fit on control frame: CONST 13/70, LINEAR 5/70,
SIGNC 6/70 — tabled. Full tables in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0) pass1 `040c9c75…804eb42` vs pass2
`040c9c75…804eb42`, identical=True; cell counts identical=True;
tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; best fixed fit CONST,
named-column scope):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | ---: |
| m16 s0 | CONST exact hits | 2475 | 12 | 0.0048 |
| m15 | CONST exact hits | 2539 | 13 | 0.0051 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_CONST | CONST exact-hit rate ≥ 0.30 on s0 named-col bytes | 12/65 = 0.1846 (m15: 13/68 = 0.1912) — not met |
| H2_GRAD | LINEAR exceeds CONST by ≥5 exact hits on s0 named-col bytes | 7 − 12 = −5 — not met |
| H3_SIGNC | SIGNC exact-hit rate ≥ 0.30 on s0 named-col bytes | 6/65 = 0.0923 (m15: 8/68 = 0.1176) — not met |
| H4_XFER | s0-best fit-s0→m15 rate within 0.15 of s0 rate | \|0.0000−0.1846\| = 0.1846 — not met |
| H5_PROFMATCH | exact-δ agreement share ≥ 0.25 over shared (col,row) sites | 6/65 = 0.0923 — not met |
| H6_COLRANGE | s0 named cols (n≥4) with δ range ≤ 8 share ≥ 0.50 | 0/7 (ranges 11–34; m15: 1/8, c342 range 8) — not met |
| N | named-col tail after best fit's hits + remaining split | 12/13 explained; 53/55 named-col stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
column (c257/277/321 read tight hump profiles sd 3.9–6.0 with
no holes; c296/301/340 read wide ragged profiles sd 10.7–12.5,
ranges 30–36; c342/343 read negative throughout), by holes
(c296/c340/c342 carry 2–4-hole mid gaps on both frames; m15
c343 carries a 261-hole span to r289), and by frame (row sets
match on 6/8 columns but values agree on only 6/65 shared
sites, mean|Δ| 1.5–8.3). Task 2 discriminates by fit family
(CONST 12/13 vs LINEAR 7/4 vs SIGNC 6/8 same-frame; SIGNC
carries 24/28 near-hits vs CONST's 14/14), by transfer (CONST
collapses to 0/1 cross-frame; SIGNC identical by sign
construction; LINEAR 2/3 with one 1299 extrapolation err),
and by column (CONST colhits spread 0–4 with c340 0/8 s0;
LINEAR's only clean column is the n=2 c343 line).

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
| interior far tail, CONST-hit | 12 of cell 7 (0.5%) | δ=column median exact, named-col scope (this run) |
| interior far tail, standing | 90 of cell 7 (3.6%) | 53 named-col + 37 outside-named; stands (this run) |
| standing interior remainder | 2463 of cell 7 (99.5%) | 2475 − 12 CONST hits |
| standing remainder (total) | 22803 (99.9% of R_0) | 12 B tail-explained; rest split above |

Screenshot: absent by rule. The workdir column-profile map
(`m25-colmap.png`, 88615 B) colors s0 named-column sites by
CONST outcome (hit 12 / near 14 / miss 39), but DESIGN.md
admits an evidence copy only if some s0 named column with n≥8
reads LINEAR col-hits − CONST col-hits ≥ 2 (max reads 0:
c277/c340 0, rest negative) — no pre-registered split
qualifies, so no evidence copy is committed (0 B of 5242880
budget). The workdir copy is retained, uncommitted.

Recorded without verdict: the 8 named columns read single-sign
throughout (all sign-runs 1) with per-row value spreads of
11–34 on s0 (sd up to 11.8) and 2–4-hole mid gaps on
c296/c340/c342 both frames plus m15 c343's lone r289 site;
row sets match cross-frame on 6/8 columns but values agree on
6/65 shared sites; the fixed-list best CONST reads 12/65 +
13/68 exact with 14/14 near-hits, LINEAR reads below CONST on
both frames, SIGNC reads 6/8 exact with 24/28 near-hits;
cross-frame CONST reads 0/68 + 1/65; 53/55 named-column bytes
stand after the best fit.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| profile suite + fixed 3-fit list + falsification bars, recorded before running | recorded | `DESIGN.md`: row→δ + holes + shape stats + xmatch, CONST/LINEAR/SIGNC with rounding + fallbacks + best rule fixed, bars H1–H6/N |
| per-row profiles + fit scores + wall/exit/shas/determinism | measured | §Step 2: profile + shape + xmatch tables both frames; 3-fit scores + residual + xframe both directions; 0.1 s; re-run identical |
| explained-vs-standing update (does any column fit shrink the tail? by how much?) + gap rows | measured | §Step 3: CONST explains 12/65 + 13/68; 53/55 named-col stands; gaps below |
| screenshot if a column-profile map discriminates (or absence reasoned) | measured | absent by rule: max LINEAR−CONST col gap 0 at n≥8; workdir copy only, 88615 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
cp local/research/M25/m25.py local/research/M25/control.py local/research/M25/DESIGN.md "/Volumes/Extreme SSD/m25/"
python3 m25.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m25" /Users/bradrichardson/dev/ssx3/local/research/M25 > m25.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M25/` — `DESIGN.md`
(suite + fixed fit list + bars, recorded before running),
`m25.py` (profiles + fits + scoring + PNG writer),
`control.py` (known-profile tail-injection control),
`REPORT.md` (this file). No PNG committed (absence reasoned
above).

Large outputs (not committed): `/Volumes/Extreme SSD/m25/` —
`m25.txt` (receipt: shas, baselines, Task-1 profiles both
frames, fits, 3-fit scores, residual, xframe both directions,
re-run, PNG size), `control.txt`, `m25.py`, `control.py`,
`DESIGN.md` (working copies), `m25-colmap.png` (working copy,
88615 B). No writes into `m15/`, `m16/`, `m17/`, `m18/`,
`m19/`, `m20/`, `m21/`, `m22/`, `m23/`, `m24/`, or other
agents' dirs.

## Gap rows (exact next brief each needs)

1. Within-column hump profiles (new): s0 c257/277/301/321
   read rise-then-fall row profiles (e.g. c257 17→30→13,
   c301 18→47→13) with LINEAR slopes near 0 and top−bottom
   means within 5. Needs its own brief: per-row profile-shape
   tables + hump/quadratic fits, offline — no new harness
   code.
2. CONST cross-frame collapse (new): s0 column medians score
   0/68 on m15 (1/65 the other way) vs 12/13 same-frame —
   the POS-collapse phenomenon (M23 gap 3) at column level.
   Needs its own brief only if column-value mapping matters:
   per-column median drift tables s0 vs m15, offline — no new
   harness code.
3. m15 c343 row-289 site (new): one tail site 262 rows below
   its column's band (hole span 28–288) drawing a 1299 LINEAR
   extrapolation err. Needs its own brief only if outlier
   isolation matters: far-row tail-site census, offline — no
   new harness code.
4. SIGN-corrected near-hit mass (M24 gap 1, still open): 35
   s0 / 38 m15 tail bytes read |err|=1 after the best M24
   correction vs 21/28 exact. Needs its own brief only if
   second-order structure matters: residual-sign tables
   around K45++SIGN, offline — no new harness code.
5. Streak-column residual coherence (M24 gap 2, still open):
   s0 c257 reads r∈{−3,−2,0} only, c296 reads all |r|≤1,
   c342 reads all r≥1 (M25 worked δ-level profiles, not
   r-level). Needs its own brief only if column-local
   correction matters: per-column r-profile tables +
   column-constant fits, offline — no new harness code.
6. Gap-bin 32–63 ±1 concentration (M24 gap 3, still open):
   16/32 s0 + 31/49 m15 |r|=1 sites sit in gap bin 32–63.
   Needs its own brief only if gap-local rounding matters:
   per-gap-value r tables within 32–63, offline — no new
   harness code.
7. POS cross-frame collapse (M23 gap 3, still open): POS cell
   medians read 7/16 same-frame but 1/2 cross-frame (M25's
   CONST collapse reads 12/13 vs 0/1 — tabled, same
   phenomenon at column level). Needs its own brief only if
   position-value mapping matters: per-cell median drift
   tables s0 vs m15, offline — no new harness code.
8. Shape-733 tail divergence (M23 gap 4, still open): shape
   733's tail map reads Jaccard 0.6694 vs s0 (100 B) while
   727/764 shapes read byte-identical (731 next-lowest at
   0.6833). Needs its own brief: per-byte attribution of
   733's private sites (tail-set change vs δ change),
   offline — no new harness code.
9. m15 private tail sites (M23 gap 5, still open): 64/134 m15
   tail sites never recur on any M16 shape (occ 0; Jaccard
   0.4132). Needs its own brief only if cross-sample tail
   identity matters: second-sample tail family, offline — no
   new harness code.
10. Shape-700 map divergence (M21 gap 1, still open): shape
    700's static map reads Jaccard 0.0747 vs s0 while 518/764
    read byte-identical. Needs its own brief: per-byte
    attribution of 700's private sites, offline — no new
    harness code.
11. m15 static-map disjointness (M21 gap 2, still open): m15
    shares 92/1476 static sites with s0 (Jaccard 0.0245).
    Needs its own brief only if cross-sample map identity
    matters, offline — no new harness code.
12. U/V co-residual mechanism (M21 gap 3, still open): same-pixel
    U&V co-residual reads 16.0×/21.6× independence. Needs its
    own brief only if chroma pairing matters, offline — no new
    harness code.
13. δ-sign mechanism (M20 gap 2, still open, minor): δ>0 on
    80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈
    0.70 on both frames. Needs its own brief only if the sign
    asymmetry matters, offline — no new harness code.
14. m15 below-min far tail (M19 gap 3, still open, minor): 4
    below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
    own brief only if outlier isolation matters, offline — no
    new harness code.
15. Negative-share mechanism (M18 gap 2, still open): 93
    negatives (worst −244) unattributed at byte level. Needs
    its own brief: per-shape added-residual maps + EFB-copy
    diffing, offline — no new harness code.
16. Odin port readiness (M18 gap 3, still open): no Odin
    contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
17. Top-HUD glyph residual isolation (M18 gap 4, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
18. Per-carrier weight centers (M18 gap 5, still open,
    optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers
    matter.

## What I could not do

1. No cross-shape check: the brief asks cross-frame only
   (fit-s0→m15 and vice versa), so shapes 1/2/733 are
   unscored — tabled scope, not chased.
2. No near-hit merging: 28 pooled near-hits stay separate
   from the 25 exact hits by rule.
3. c341 unscored: 0 s0 / 1 m15 sites — membership-guarded
   but outside the brief's 8 fit columns.
4. LINEAR float path: OLS runs in float64 with half-away
   rounding (per DESIGN.md), not exact-integer — tabled as
   implemented; the 1299 extrapolation err on m15 r289 is
   measured, not chased.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M25/`: `DESIGN.md`, `m25.py`,
`control.py`, `REPORT.md` (this file). No PNG (0 B).
