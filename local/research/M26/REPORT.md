# M26 — Within-column hump profiles: shape tables + hump/quadratic fits: REPORT

M25 gap 1 worked at column level: hump-shape tables (peak row +
value, rise, fall, symmetry, index-third argmax) for the 8 named
streak columns on s0 + m15 plus 3 fixed shape fits scored by
exact byte match (hit = exact, near-hit |err|≤1 tabled
separately, never merged). Profiles reproduce M25's row→δ lists
+ shape stats byte-exactly (32/32 receipt lines both frames);
peak rows agree cross-frame on 5/8 columns while argmax reads
top-third on 6/8 s0 columns (first-tie rule on plateaus); best
fixed shape fit is TRI (symmetric triangle): 18/65 s0 + 16/68
m15 exact hits (34 pooled) vs M25 CONST 12/65 + 13/68, with
QUAD below TWO on both frames (4/3) and cross-frame TRI
collapsing to 4/68 fit-s0→m15. Fully offline — no lease of any
kind, no boots, no harness code, no `adb`. No device work.
Runbook `local/muse/prompts/M26.md`. Tables, no verdicts.

Headers read first: `local/research/M25/REPORT.md` (all of it:
65/68 named-column bytes, row→δ lists, shape stats, CONST
12/65 + 13/68 with LINEAR below CONST both frames, CONST
cross-frame collapse 0/1) plus M25's Task-1 profile tables in
`m25.txt` (the row→δ lists this run fits).

Time box 4 hours (start 2026-09-20 02:50 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m25/` — all outputs went to the new
`/Volumes/Extreme SSD/m26/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), and `m25.txt` (column
profiles to reproduce). Work dir `/Volumes/Extreme SSD/m26/`;
evidence `local/research/M26/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M25):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m25.txt | `dbbe5d66…567f63b3` |

(Full hexes in `m26.txt` §inputs.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M25 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

Two `m26.py` invocations (first crashed at the PNG stage: the
Task-2.3 loop variable `H` shadowed the global frame height —
TypeError; fixed with no design change) plus one no-op
`control.py` invocation (missing `__main__` guard — exit 0,
empty output; guard added, no design change). The receipt is
the single clean re-run (0.5 s, exit 0 — the estimator was
never changed after the receipt run started); one `control.py`
invocation (green, first try after the guard fix). One
pre-receipt edit (a `prof`/`shape` line-filter mismatch in the
M25-match guard) was caught by reading before the receipt run
— not results; DESIGN.md was recorded before every fix and is
unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m26.py receipt | 0.5 s | exit 0; all guards pass; canon `c90512b4…b0337fd` |
| control.py C-P1 (known humps) | <1 s | green; profiles exact; identities TRI/QUAD |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 shapes + xmatch) | 2 | 0.0 s |
| Task 2 (fits + scores + xframe + h2h) | 2 | <1 s |
| Determinism re-run (Task 1 on s0) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m26.py` wall | — | 0.5 s |

## Step 2 — estimates

### Task 1 — profile-shape tables (hump or not?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M22/M23 EXACTLY, and all
32 M25 profile lines (prof rowdelta + holes + shape stats +
roworder) matching `m25.txt` byte-exactly on BOTH frames
(stop rule not triggered). Named-column bytes read 65 s0 /
68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V).

Hump metrics per named column per frame (peak = argmax δ,
first on ties; rise = peak−first, fall = peak−last;
thirds by argmax index; same formulas all columns, no
special-casing):

| Frame | col | peakrow/peakval | first | last | rise | fall | sym | k/n | third |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| s0 | 257 | 25/30 | 17 | 13 | 13 | 17 | 4 | 2/10 | top |
| s0 | 277 | 25/28 | 16 | 13 | 12 | 15 | 3 | 2/10 | top |
| s0 | 296 | 26/47 | 21 | 15 | 26 | 32 | 6 | 2/9 | top |
| s0 | 301 | 27/47 | 18 | 13 | 29 | 34 | 5 | 4/11 | mid |
| s0 | 321 | 25/27 | 14 | 11 | 13 | 16 | 3 | 2/10 | top |
| s0 | 340 | 26/47 | 17 | 17 | 30 | 30 | 0 | 2/8 | top |
| s0 | 342 | 27/−16 | −16 | −17 | 0 | 1 | 1 | 0/5 | top |
| s0 | 343 | 27/−26 | −31 | −26 | 5 | 0 | 5 | 1/2 | mid |
| m15 | 257 | 25/20 | 12 | 8 | 8 | 12 | 4 | 2/10 | top |
| m15 | 277 | 25/20 | 12 | 8 | 8 | 12 | 4 | 2/10 | top |
| m15 | 296 | 26/46 | 16 | 16 | 30 | 30 | 0 | 2/9 | top |
| m15 | 301 | 27/48 | 12 | 18 | 36 | 30 | 6 | 4/11 | mid |
| m15 | 321 | 26/31 | 14 | 14 | 17 | 17 | 0 | 3/10 | top |
| m15 | 340 | 32/48 | 16 | 14 | 32 | 34 | 2 | 6/9 | bottom |
| m15 | 342 | 27/−13 | −13 | −21 | 0 | 8 | 8 | 0/5 | top |
| m15 | 343 | 289/−15 | −22 | −15 | 7 | 0 | 7 | 3/4 | bottom |

(Non-hump columns tabled identically: c296/340 ragged read
top-third argmax on s0 with sym 0–6; c342 reads peak at its
first row both frames (rise 0); c343 reads peak at its last
row both frames (fall 0), m15's at r289.)

Cross-frame shape match (same peak row? same rise/fall?):

| col | peak s0/m15 | equal? | (rise,fall) s0 | (rise,fall) m15 | third s0/m15 |
| ---: | --- | --- | --- | --- | --- |
| 257 | 25/25 | True | (13,17) | (8,12) | top/top |
| 277 | 25/25 | True | (12,15) | (8,12) | top/top |
| 296 | 26/26 | True | (26,32) | (30,30) | top/top |
| 301 | 27/27 | True | (29,34) | (36,30) | mid/mid |
| 321 | 25/26 | False | (13,16) | (17,17) | top/top |
| 340 | 26/32 | False | (30,30) | (32,34) | top/bottom |
| 342 | 27/27 | True | (0,1) | (0,8) | top/top |
| 343 | 27/289 | False | (5,0) | (7,0) | mid/bottom |

Pooled H5: 5/8 peak rows agree (share 0.6250).

### Task 2 — hump fits (fixed 3-list, exact-hit scoring)

Fits (DESIGN.md fixed list; no additions; qfb = s0 c343 n=2
only, as expected; tfb/wfb/empties none):

| Fit | s0 constants | m15 constants |
| --- | --- | --- |
| QUAD a (curvature) | [−0.69,−0.64,−0.40,−1.16,−0.68,−1.39,+0.21,fb] | [−0.48,−0.48,−0.87,−1.14,−0.80,−0.94,−0.02,+0.01] |
| TRI p/h/e/w (c257…c343) | 25/30/13/7, 25/28/13/7, 26/47/15/8, 27/47/13/6, 25/27/11/7, 26/47/17/8, 27/−16/−17/1, 27/−26/−31/1 | 25/20/8/7, 25/20/8/7, 26/46/16/8, 27/48/12/4, 26/31/14/6, 32/48/14/8, 27/−13/−21/4, 289/−15/−22/1 |
| TWO top/bot | 29/28, 27/28, 38/31, 33/29, 26/25, 42/41, −22/−17, −31/−26 | 19/19, 19/19, 39/37, 24/21, 29/28, 39/38, −17/−19, −28/−21 |

(QUAD a reads negative (∩) on all positive columns both
frames except ~0 on m15 c342/c343; full a/b/c 6dp in the
receipt. TRI w reads 6–8 on positive columns except m15
c301 w=4. CONST-vs-M25 median guard reads match=True both
frames.)

Same-frame scores (fit = score frame; exact |err| value counts
in the receipt; CONST recomputed M25-verbatim for Task 2.3):

| Predictor | s0 hits/rate | s0 near | s0 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| QUAD | 4 / 0.0615 | 8 | 32/14/6/1 |
| TRI | 18 / 0.2769 | 8 | 8/9/14/8 |
| TWO | 15 / 0.2308 | 11 | 7/11/15/6 |
| CONST | 12 / 0.1846 | 14 | 8/11/13/7 |

| Predictor | m15 hits/rate | m15 near | m15 miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| QUAD | 3 / 0.0441 | 18 | 23/12/12/0 |
| TRI | 16 / 0.2353 | 5 | 12/20/9/6 |
| TWO | 12 / 0.1765 | 14 | 9/15/12/6 |
| CONST | 13 / 0.1912 | 14 | 9/11/15/6 |

Per-column s0 colhits (TRI/QUAD/TWO): c257 3/1/3, c277
2/1/5, c296 2/0/1, c301 3/0/1, c321 2/2/2, c340 2/0/0, c342
2/0/1, c343 2/0/2 (TRI's c343 2/2 is the n=2 exact triangle;
m15 colhits in the receipt).

Best fit (DESIGN.md rule: s0 hits, then m15 hits, then list
order): TRI (18 + 16 = 34 pooled). Explained bytes (named-
column bytes removed from the tail): 18/65 s0, 16/68 m15.
Residual |δ−pred| after TRI:

| Frame | 0 | 1 | 2–3 | 4–7 | 8–15 | 16+ |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| s0 | 18 | 8 | 8 | 9 | 14 | 8 |
| m15 | 16 | 5 | 12 | 20 | 9 | 6 |

(Exact residual value counts in the receipt; max residual 23
s0 / 26 m15.)

Cross-frame check (fit constants on one frame, score on the
other; all 3 carry fitted constants — no N/A):

| Direction | Predictor | hits/rate | near |
| --- | --- | ---: | ---: |
| fit-s0 → m15 | QUAD (s0 a/b/c) | 1 / 0.0147 | 3 |
| fit-s0 → m15 | TRI (s0 p/h/e/w) | 4 / 0.0588 | 8 |
| fit-s0 → m15 | TWO (s0 medians) | 1 / 0.0147 | 4 |
| fit-m15 → s0 | QUAD (m15 a/b/c) | 2 / 0.0308 | 4 |
| fit-m15 → s0 | TRI (m15 p/h/e/w) | 2 / 0.0308 | 11 |
| fit-m15 → s0 | TWO (m15 medians) | 0 / 0.0000 | 4 |

(Same-frame baselines for comparison: TRI 18/65 s0 / 16/68
m15; QUAD 4/65 / 3/68; TWO 15/65 / 12/68. Full miss |err|
hists + errvalues both directions in the receipt.)

Beat-the-baseline (best shape TRI vs M25 CONST head-to-head
per column; + = shape ahead):

| Frame | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 | pooled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| s0 | 3v4 −1 | 2v2 +0 | 2v1 +1 | 3v1 +2 | 2v3 −1 | 2v0 +2 | 2v1 +1 | 2v0 +2 | 18v12 +6 |
| m15 | 3v2 +1 | 2v3 −1 | 2v2 +0 | 2v1 +1 | 2v2 +0 | 1v2 −1 | 2v1 +1 | 2v0 +2 | 16v13 +3 |

(TRI beats-or-ties CONST on 6/8 s0 columns (loses c257/c321
by 1) and 6/8 m15 columns (loses c277/c340 by 1).)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 (known humps, N=10, 0 skips) | 112 sites, set exact, values exact, originals unchanged | exact | True |
| C-P1 profiles (listed triangle/quadratic) | row→δ + hump (peak 28/12, rise 4, fall 4, mid) exact both groups | exact | True |
| C-P1 identity (injected-only fits) | A: TRI 5/5 (w=2), argmax TRI; B: QUAD 5/5, argmax QUAD | exact | True |

(Off-expectation tabled: restricted TWO reads 1/5 per group,
not the DESIGN.md hand estimate 2/5 — the top-half median
(9/10) misses r27; the estimate was arithmetic, the gated
criteria (profiles exact + TRI_A 5/5 + QUAD_B 5/5 + both
identities) read exact. QUAD_A 4/5 + TRI_B 3/5 (w=2) match
their estimates. Full-control-frame scores, fit on control
frame: QUAD 4/65, TRI 18/65, TWO 15/65 — tabled. Full tables
in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0) pass1 `c90512b4…b0337fd` vs pass2
`c90512b4…b0337fd`, identical=True; cell counts identical=True;
tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; best fixed shape fit TRI,
named-column scope):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | TRI exact hits | 2475 | 18 | 0.0073 |
| m15 | TRI exact hits | 2539 | 16 | 0.0063 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_QUAD | QUAD exact-hit rate ≥ 0.30 on s0 named-col bytes | 4/65 = 0.0615 (m15: 3/68 = 0.0441) — not met |
| H2_TRI | TRI exact hits exceed QUAD exact hits by ≥5 on s0 named-col bytes | 18 − 4 = 14 — met |
| H3_TWO | TWO exact-hit rate ≥ 0.30 on s0 named-col bytes | 15/65 = 0.2308 (m15: 12/68 = 0.1765) — not met |
| H4_XFER | s0-best fit-s0→m15 rate within 0.15 of s0 rate | \|0.0588−0.2769\| = 0.2181 — not met |
| H5_PEAKMATCH | share of 8 named columns with equal s0/m15 peak rows ≥ 0.50 | 5/8 = 0.6250 — met |
| H6_HUMP | s0 named cols (n≥4) with mid-third argmax AND rise≥3 AND fall≥3, share ≥ 0.50 | 1/7 (c301 only; 6/7 read top-third) — not met |
| H7_BEATCONST | best shape fit s0 hits exceed M25 CONST s0 hits (12) by ≥5 | 18 − 12 = 6 — met |
| N | named-col tail after best fit's hits + remaining split | 18/16 explained; 47/52 named-col stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
peak position (argmax reads top-third on 6/8 s0 + 5/8 m15
columns under the first-tie rule, mid on s0 c301/c343 and
m15 c301, bottom on m15 c340/c343), by symmetry (sym 0 on
s0 c340 + m15 c296/c321, 7–8 on m15 c342/c343), and by frame
(peak rows match on 5/8 columns but (rise,fall) pairs match
on none exactly). Task 2 discriminates by fit family (TRI
18/16 vs TWO 15/12 vs QUAD 4/3 same-frame; QUAD carries
32/23 of its mass in the 2–3 miss bin), by transfer (all
three collapse to 0–4 cross-frame), and by column (TRI
colhits read 2–3 on every s0 column including the n=2
c343; QUAD reads 0 on 5/8 s0 columns).

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
| interior far tail, TRI-hit | 18 of cell 7 (0.7%) | δ=TRI pred exact, named-col scope (this run) |
| interior far tail, standing | 84 of cell 7 (3.4%) | 47 named-col + 37 outside-named; stands (this run) |
| standing interior remainder | 2457 of cell 7 (99.3%) | 2475 − 18 TRI hits |
| standing remainder (total) | 22797 (99.9% of R_0) | 18 B tail-explained; rest split above |

Screenshot: present by rule. The evidence shape-fit map
(`m26-shapemap.png`, 88484 B of 5242880 budget) colors s0
named-column sites by TRI outcome (hit 18 / near 8 / miss
39); DESIGN.md admits an evidence copy iff some s0 named
column with n≥8 reads TRI col-hits − CONST col-hits ≥ 2 —
c301 (+2, n=11) and c340 (+2, n=8) qualify.

Recorded without verdict: the 8 named columns read peak rows
agreeing cross-frame on 5/8 columns with (rise,fall) pairs
matching on none, argmax in the top third on 6/8 s0 columns
under the pinned first-tie/index-thirds convention, and
sym 0–8; the fixed-list best TRI reads 18/65 + 16/68 exact
with 8/5 near-hits, TWO reads 15/12, QUAD reads 4/3 with
32/23 mass in the 2–3 miss bin; cross-frame shape fits read
0–4 hits both directions; TRI beats-or-ties CONST on 6/8
columns per frame (+6/+3 pooled); 47/52 named-column bytes
stand after the best fit.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| profile suite + fixed 3-fit list + falsification bars, recorded before running | recorded | `DESIGN.md`: hump metrics + xshape match, QUAD/TRI/TWO with rounding + fallbacks + best rule fixed, bars H1–H7/N |
| per-row shape tables + fit scores + wall/exit/shas/determinism | measured | §Step 2: hump + xshape tables both frames; 3-fit scores + residual + xframe both directions + CONST h2h; 0.5 s; re-run identical |
| explained-vs-standing update (does any shape fit shrink the tail? by how much?) + gap rows | measured | §Step 3: TRI explains 18/65 + 16/68; 47/52 named-col stands; gaps below |
| screenshot if a shape-fit map discriminates (or absence reasoned) | measured | present by rule: c301/c340 TRI−CONST +2 at n≥8; 88484 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single clean invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m26"
cp local/research/M26/m26.py local/research/M26/control.py local/research/M26/DESIGN.md "/Volumes/Extreme SSD/m26/"
python3 m26.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m25/m25.txt" "/Volumes/Extreme SSD/m26" /Users/bradrichardson/dev/ssx3/local/research/M26 > m26.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m26/m26-shapemap.png" local/research/M26/m26-shapemap.png
```

## Paths

Evidence (committed): `local/research/M26/` — `DESIGN.md`
(suite + fixed fit list + bars, recorded before running),
`m26.py` (shapes + fits + scoring + PNG writer),
`control.py` (known-hump tail-injection control),
`m26-shapemap.png` (shape-fit map, 88484 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m26/` —
`m26.txt` (receipt: shas, baselines, Task-1 shapes both
frames, fits, 3-fit scores, residual, xframe both directions,
head-to-head, re-run, PNG size), `control.txt`, `m26.py`,
`control.py`, `DESIGN.md` (working copies),
`m26-shapemap.png` (working copy, 88484 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. TRI cross-frame collapse (new): TRI fit-s0→m15 reads 4/68
   (2/65 the other way) vs 18/16 same-frame — the
   CONST-collapse phenomenon (M25 gap 2) at shape level.
   Needs its own brief only if shape transfer matters:
   per-column triangle-drift (p/h/e/w s0 vs m15) tables,
   offline — no new harness code.
2. Peak-row agreement without value agreement (new): 5/8
   columns share peak rows cross-frame but only 6/65
   shared-site δ values agree (M25 H5) — positional vs value
   structure split. Needs its own brief only if peak
   anchoring matters: peak-anchored residual tables,
   offline — no new harness code.
3. Index-top argmax concentration (new): 6/8 s0 + 5/8 m15
   argmax read top-third by index under the first-tie rule
   (plateau peaks: c257's 29×4 run, c340's twin 47s).
   Needs its own brief only if peak-position convention
   matters: plateau-aware peak tables (all-tie rows +
   run-center rules), offline — no new harness code.
4. QUAD underfit (new, minor): smooth quadratic reads 4/65 +
   3/68 with 32/23 mass in the 2–3 miss bin — below TWO and
   CONST on both frames despite ∩ curvature on every
   positive column. Needs its own brief only if curvature
   matters: per-column quadratic-residual tables, offline —
   no new harness code.
5. CONST cross-frame collapse (M25 gap 2, still open): s0
   column medians score 0/68 on m15 (1/65 the other way) vs
   12/13 same-frame. Needs its own brief only if column-value
   mapping matters: per-column median drift tables s0 vs m15,
   offline — no new harness code.
6. m15 c343 row-289 site (M25 gap 3, still open): one tail
   site 262 rows below its column's band (hole span 28–288),
   now also m15 c343's argmax peak. Needs its own brief only
   if outlier isolation matters: far-row tail-site census,
   offline — no new harness code.
7. SIGN-corrected near-hit mass (M24 gap 1, still open): 35
   s0 / 38 m15 tail bytes read |err|=1 after the best M24
   correction vs 21/28 exact. Needs its own brief only if
   second-order structure matters: residual-sign tables
   around K45++SIGN, offline — no new harness code.
8. Streak-column residual coherence (M24 gap 2, still open):
   s0 c257 reads r∈{−3,−2,0} only, c296 reads all |r|≤1,
   c342 reads all r≥1 (M26 worked δ-level shapes, not
   r-level). Needs its own brief only if column-local
   correction matters: per-column r-profile tables +
   column-constant fits, offline — no new harness code.
9. Gap-bin 32–63 ±1 concentration (M24 gap 3, still open):
   16/32 s0 + 31/49 m15 |r|=1 sites sit in gap bin 32–63.
   Needs its own brief only if gap-local rounding matters:
   per-gap-value r tables within 32–63, offline — no new
   harness code.
10. POS cross-frame collapse (M23 gap 3, still open): POS cell
    medians read 7/16 same-frame but 1/2 cross-frame (M26's
    TRI collapse reads 18/16 vs 4/2 — tabled, same
    phenomenon at shape level). Needs its own brief only if
    position-value mapping matters: per-cell median drift
    tables s0 vs m15, offline — no new harness code.
11. Shape-733 tail divergence (M23 gap 4, still open): shape
    733's tail map reads Jaccard 0.6694 vs s0 (100 B) while
    727/764 shapes read byte-identical (731 next-lowest at
    0.6833). Needs its own brief: per-byte attribution of
    733's private sites (tail-set change vs δ change),
    offline — no new harness code.
12. m15 private tail sites (M23 gap 5, still open): 64/134 m15
    tail sites never recur on any M16 shape (occ 0; Jaccard
    0.4132). Needs its own brief only if cross-sample tail
    identity matters: second-sample tail family, offline — no
    new harness code.
13. Shape-700 map divergence (M21 gap 1, still open): shape
    700's static map reads Jaccard 0.0747 vs s0 while 518/764
    read byte-identical. Needs its own brief: per-byte
    attribution of 700's private sites, offline — no new
    harness code.
14. m15 static-map disjointness (M21 gap 2, still open): m15
    shares 92/1476 static sites with s0 (Jaccard 0.0245).
    Needs its own brief only if cross-sample map identity
    matters, offline — no new harness code.
15. U/V co-residual mechanism (M21 gap 3, still open): same-pixel
    U&V co-residual reads 16.0×/21.6× independence. Needs its
    own brief only if chroma pairing matters, offline — no new
    harness code.
16. δ-sign mechanism (M20 gap 2, still open, minor): δ>0 on
    80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈
    0.70 on both frames. Needs its own brief only if the sign
    asymmetry matters, offline — no new harness code.
17. m15 below-min far tail (M19 gap 3, still open, minor): 4
    below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
    own brief only if outlier isolation matters, offline — no
    new harness code.
18. Negative-share mechanism (M18 gap 2, still open): 93
    negatives (worst −244) unattributed at byte level. Needs
    its own brief: per-shape added-residual maps + EFB-copy
    diffing, offline — no new harness code.
19. Odin port readiness (M18 gap 3, still open): no Odin
    contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
20. Top-HUD glyph residual isolation (M18 gap 4, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
21. Per-carrier weight centers (M18 gap 5, still open,
    optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers
    matter.

## What I could not do

1. No cross-shape check: the brief asks cross-frame only
   (fit-s0→m15 and vice versa), so shapes 1/2/733 are
   unscored — tabled scope, not chased.
2. No near-hit merging: 13 pooled near-hits stay separate
   from the 34 exact hits by rule.
3. c341 unscored: 0 s0 / 1 m15 sites — membership-guarded
   but outside the brief's 8 fit columns.
4. Float paths: QUAD runs OLS + TRI runs its w-search SSE in
   float64 with half-away rounding (per DESIGN.md), not
   exact-integer — tabled as implemented.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M26/`: `DESIGN.md`, `m26.py`,
`control.py`, `m26-shapemap.png` (88484 B), `REPORT.md` (this
file).
