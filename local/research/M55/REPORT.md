# M55 — CONST cross-frame collapse: per-column median drift tables: REPORT

M25 gap 2 (via M26 gap 5) worked at table level: per-column
median drift (Δmedian = m15 − s0 + |Δ| rank) for the 8 named
columns plus the collapse anatomy (kept-hit + near-hit site
rows both directions, per-column xerr), with M25's 8+8 CONST
medians + 12/65 + 13/68 same-frame + 0/68 + 1/65 cross-frame
reproduced exactly (hit = exact, near-hit |err|≤1 tabled
separately, never merged). Medians reproduce M25 16/16 with
fallbacks 27/20 and empties none; drift reads widest on c257
(−10) and narrowest on c296/c321/c342 (|Δ|=2); low-drift
columns keep 0 pooled hits while the single kept hit sits on
c340 (|Δ|=3); medians read below TRI peaks on all 16
col-frames (med−h −1..−25, never equal). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M55.md`. Tables, no
verdicts.

Headers read first: `local/research/M25/REPORT.md` (all of it:
M25 gap 2 = this brief via M26 gap 5; s0 column medians score
0/68 on m15, 1/65 the other way, vs 12/13 same-frame; 65/68
named-column bytes, row→δ lists, shape stats, CONST 12/65 +
13/68 with LINEAR below CONST both frames) plus
`local/research/M26/REPORT.md` (all of it: CONST-vs-M25 median
guard match=True both frames; TRI p/h/e/w + hump peak
row/value table — the peaks Task 2.3 joins).

Time box 4 hours (start 2026-09-20 07:45 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m54/` — all outputs went to the new
`/Volumes/Extreme SSD/m55/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), `m25.txt` (medians +
scores to reproduce), and `m26.txt` (TRI peaks for the
median-vs-peak join). Work dir `/Volumes/Extreme SSD/m55/`;
evidence `local/research/M55/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M54):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m25.txt | `dbbe5d66…567f63b3` |
| m26.txt | `9a3d522b…060ff8f8` |

(Full hexes in `m55.txt` §inputs; `m25.txt` 15578 B, `m26.txt`
18821 B. Both txt sha prefixes match the M26/M51 records.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M54 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m55.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try). DESIGN.md was
recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m55.py receipt | 0.2 s | exit 0; all guards pass; canon `a95907f6…a71f348` |
| control.py C-P1 (known medians + drift) | <1 s | green; 4 medians + 4 drifts + ranks exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 profiles + fits + scores + xframe) | 2 | 0.0 s |
| Task 2 (drift + driftx + medpeak + xerr) | 2 | <1 s |
| Determinism re-run (Task 1 on s0+m15 + drift) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m55.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — CONST reproduction (do the medians + scores reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M22/M23/M25/M26 EXACTLY,
and all 16 CONST medians + both fallbacks matching `m25.txt`
fit lines exactly on BOTH frames (stop rule not triggered).
Named-column bytes read 65 s0 / 68 m15. δ==0 count reads 0;
P(δ>0) reproduces M19/M20 0.8093/0.8019. Tail planes read
102/0/0 s0 and 134/0/0 m15 (Y/U/V).

Median table: all 8 columns × s0/m15 medians + fallback rows
(empties=[] both frames — no column uses fb):

| col | s0 med | m15 med |
| ---: | ---: | ---: |
| 257 | 29 | 19 |
| 277 | 27 | 19 |
| 296 | 35 | 37 |
| 301 | 32 | 23 |
| 321 | 26 | 28 |
| 340 | 41 | 38 |
| 342 | −17 | −19 |
| 343 | −29 | −24 |
| fallback (used by: none) | 27 | 20 |

(M25 fit-line match: 8/8 cols + fallback both frames; DESIGN
pins match. Median rule M25-verbatim: even-n mean-of-middles,
halves away from zero; no n<3 case for CONST — s0 c343 n=2
reads int_median(−31,−26)=−29 as-is.)

Same-frame table: CONST hits/near/miss per frame with
per-column colhits (12 + 13 reproduced with nears 14/14):

| Frame | hits/rate | near | miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| s0 | 12 / 0.1846 | 14 | 8/11/13/7 |
| m15 | 13 / 0.1912 | 14 | 9/11/15/6 |

| Frame | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 colhits | 4/10 | 2/10 | 1/9 | 1/11 | 3/10 | 0/8 | 1/5 | 0/2 |
| m15 colhits | 2/10 | 3/10 | 2/9 | 1/11 | 2/10 | 2/9 | 1/5 | 0/4 |

(Errvalues both frames match the M25 pins value-for-value;
receipt lines 99/103.)

Collapse table: fit-s0→m15 0/68 (near-2 rows named) +
fit-m15→s0 1/65 (the 1 kept hit named) + errvalues:

| Direction | hits/rate | near | miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| fit-s0→m15 | 0 / 0.0000 | 2 | 16/15/24/11 |
| fit-m15→s0 | 1 / 0.0154 | 4 | 13/15/22/10 |

Errvalues fit-s0→m15: 1:2 2:7 3:9 4:2 5:6 6:1 7:6 8:4 9:5
10:2 11:4 12:3 13:1 14:3 15:2 16:2 17:1 19:4 20:1 21:1 25:1
27:1. Errvalues fit-m15→s0: 0:1 1:4 2:9 3:4 4:3 5:2 6:6 7:4
8:3 9:10 10:7 11:1 14:1 16:2 17:1 18:2 21:2 22:1 23:1 24:1.
(Both match the M25 pins value-for-value.)

Kept-hit site rows (the 0/68 anatomy, hit side):

| Direction | Site rows |
| --- | --- |
| fit-s0→m15 | none (nrows=0) |
| fit-m15→s0 | c340 r25 d=38 pred=38 (nrows=1) |

Near-hit site rows (the 0/68 anatomy, near side; err =
pred − δ):

| Direction | Site rows |
| --- | --- |
| fit-s0→m15 | c340 r27 d=40 pred=41 err=+1; c340 r31 d=40 pred=41 err=+1 (nrows=2) |
| fit-m15→s0 | c321 r25 d=27 pred=28 err=+1; c321 r26 d=27 pred=28 err=+1; c340 r33 d=37 pred=38 err=+1; c342 r29 d=−18 pred=−19 err=−1 (nrows=4) |

### Task 2 — median drift (which columns drift? who keeps hits?)

Drift table: Δmedian per column (m15 − s0) + |Δ| rank:

| col | s0 | m15 | Δ | |Δ| | rank |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 257 | 29 | 19 | −10 | 10 | 1 |
| 301 | 32 | 23 | −9 | 9 | 2 |
| 277 | 27 | 19 | −8 | 8 | 3 |
| 343 | −29 | −24 | +5 | 5 | 4 |
| 340 | 41 | 38 | −3 | 3 | 5 |
| 296 | 35 | 37 | +2 | 2 | 6 |
| 321 | 26 | 28 | +2 | 2 | 7 |
| 342 | −17 | −19 | −2 | 2 | 8 |

(Rank by |Δ| desc; ties → smaller column first: the three
|Δ|=2 columns order 296/321/342. Widest drift c257 −10;
narrowest the |Δ|=2 triple.)

Drift-vs-keep table: per-column |Δmedian| vs same-frame
colhits vs cross-frame kept hits:

| col | |Δ| | low | same s0 | same m15 | k_s0m15 | k_m15s0 | pooled |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 257 | 10 | False | 4/10 | 2/10 | 0/10 | 0/10 | 0 |
| 277 | 8 | False | 2/10 | 3/10 | 0/10 | 0/10 | 0 |
| 296 | 2 | True | 1/9 | 2/9 | 0/9 | 0/9 | 0 |
| 301 | 9 | False | 1/11 | 1/11 | 0/11 | 0/11 | 0 |
| 321 | 2 | True | 3/10 | 2/10 | 0/10 | 0/10 | 0 |
| 340 | 3 | False | 0/8 | 2/9 | 0/9 | 1/8 | 1 |
| 342 | 2 | True | 1/5 | 1/5 | 0/5 | 0/5 | 0 |
| 343 | 5 | False | 0/2 | 0/4 | 0/4 | 0/2 | 0 |

(Low = |Δ|≤2. The three low-drift columns keep 0 pooled
hits; the single pooled kept hit sits on c340, |Δ|=3 —
cf. M51's L1 finding: low-drift 296/301 (L1 2/4) kept 0
pooled TRI hits while high-drift 257/340 (L1 15/10) kept 2
each.)

Median-vs-peak table: CONST medians vs M26 argmax peaks per
column per frame (M26 p/h pinmatch 8/8 both frames):

| Frame | col | med | p | h | med==h? | med−h |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 257 | 29 | 25 | 30 | False | −1 |
| s0 | 277 | 27 | 25 | 28 | False | −1 |
| s0 | 296 | 35 | 26 | 47 | False | −12 |
| s0 | 301 | 32 | 27 | 47 | False | −15 |
| s0 | 321 | 26 | 25 | 27 | False | −1 |
| s0 | 340 | 41 | 26 | 47 | False | −6 |
| s0 | 342 | −17 | 27 | −16 | False | −1 |
| s0 | 343 | −29 | 27 | −26 | False | −3 |
| m15 | 257 | 19 | 25 | 20 | False | −1 |
| m15 | 277 | 19 | 25 | 20 | False | −1 |
| m15 | 296 | 37 | 26 | 46 | False | −9 |
| m15 | 301 | 23 | 27 | 48 | False | −25 |
| m15 | 321 | 28 | 26 | 31 | False | −3 |
| m15 | 340 | 38 | 32 | 48 | False | −10 |
| m15 | 342 | −19 | 27 | −13 | False | −6 |
| m15 | 343 | −24 | 289 | −15 | False | −9 |

(Median==peak on 0/16 col-frames; med−h reads −1..−25,
all negative — medians sit strictly below TRI peaks.)

Per-column xerr (err distribution of cross-frame medians by
column; mean|err| + max|err|):

| Direction | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fit-s0→m15 mean/max | 11.800/21 | 9.800/19 | 8.556/19 | 12.636/20 | 4.800/12 | 9.333/27 | 3.200/4 | 7.250/14 |
| fit-m15→s0 mean/max | 8.100/11 | 7.200/9 | 9.889/22 | 11.818/24 | 5.300/17 | 9.250/21 | 3.400/8 | 4.500/7 |

(Smallest mean|err| both directions is c342 (3.200/3.400);
largest is c301 (12.636/11.818). Max|err| 27 reads on
fit-s0→m15 c340.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 P1 (odd n=5) | med 10/12, drift +2, abs 2, rank 3 | exact | True |
| C-P1 P2 (even n=4, halves) | med 11/12, drift +1, abs 1, rank 4 | exact | True |
| C-P1 P3 (even-negative n=2/4) | med −29/−24, drift +5, abs 5, rank 2 | exact | True |
| C-P1 P4 (even n=10, c257-shaped) | med 29/19, drift −10, abs 10, rank 1 | exact | True |
| C-P1 pooled | medians + drifts + abs + ranks on all 4 | exact | True |

(Pure-synthetic row→δ lists per DESIGN.md — deviation
reasoned per M53/M54: median/drift logic operates on row→δ
lists, so synthetic lists exercise the identical code path
with zero dump coupling. P2/P3 exercise the even-n
halves-away-from-zero rule on positive and negative sums;
P4 replays the c257 δ lists. Full tables in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 fits+scores on s0+m15 + drift lines) pass1
`a95907f6…a71f348` vs pass2 `a95907f6…a71f348`,
identical=True; fits+scores+drift identical=True; cell counts
identical=True; tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; CONST named-column scope —
attribution, 0 new bytes beyond M25 CONST):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | CONST exact hits | 2475 | 12 | 0.0048 |
| m15 | CONST exact hits | 2539 | 13 | 0.0051 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_COLLAPSE | s0-fit CONST m15 rate within 0.15 of s0 rate | \|0.0000−0.1846\| = 0.1846 — not met |
| H2_BIGDRIFT | share of 8 cols with \|Δmedian\|≥5 ≥ 0.50 | 4/8 (257/277/301/343) — met |
| H3_SMALLDRIFT | share of 8 cols with \|Δmedian\|≤2 ≥ 0.25 | 3/8 (296/321/342) — met |
| H4_LOWDRIFTKEEPS | among \|Δ\|≤2 cols, share with pooled kept ≥1 ≥ 0.50 | 0/3 — not met |
| H5_MEDPEAK | among 16 col-frames, share with median==TRI h ≥ 0.25 | 0/16 — not met |
| H6_ERRMASS | among 68 fit-s0→m15 \|err\|, share with \|err\|≥8 ≥ 0.50 | 35/68 = 0.5147 — met |
| H7_MAXDRIFT | argmax \|Δmedian\| is c257 (no tie) | c257, \|Δ\|=10 unique — met |
| N | named-col tail after CONST hits + drift attribution | 12/13 explained; 53/55 named-col stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
frame (medians match M25 16/16 both frames; scores read
12/65 + 13/68 same-frame vs 0/68 + 1/65 cross-frame) and by
column (same-frame colhits spread 0–4 with c340 0/8 s0 and
c343 0/6 pooled; cross-frame colhits read all-zero except
c340 1/8 fit-m15→s0). Task 2 discriminates by drift (|Δ|
reads 10/9/8 on 257/301/277 vs 2 on the 296/321/342 triple,
c343 +5 the lone positive wide drift), by keep (pooled kept
reads 1 on c340 only — the low-drift triple keeps 0), and by
median-vs-peak (med−h reads −1 on the tight 257/277/321
columns vs −9..−25 on the ragged 296/301/340 columns).

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
| interior far tail, CONST-hit | 12 of cell 7 (0.5%) | δ=column median exact, named-col scope (M25, unchanged — 0 new this run) |
| interior far tail, standing | 90 of cell 7 (3.6%) | 53 named-col + 37 outside-named; stands (this run) |
| standing interior remainder | 2463 of cell 7 (99.5%) | 2475 − 12 CONST hits |
| standing remainder (total) | 22803 (99.9% of R_0) | 12 B tail-explained; rest split above |

Screenshot: absent by rule. The workdir drift-collapse map
(`m55-driftmap.png`, 88546 B) colors s0 named-column sites by
fit-m15→s0 kept-hit outcome (kept 1 / lost 64), but DESIGN.md
admits an evidence copy only if some s0 named column with n≥8
reads pooled cross-frame kept hits ≥ 3 (max reads 1: c340;
rest 0) — no pre-registered split qualifies, so no evidence
copy is committed (0 B of 5242880 budget). The workdir copy
is retained, uncommitted.

Recorded without verdict: the 8+8 CONST medians reproduce M25
exactly with fallbacks 27/20 and no empty columns, same-frame
scores read 12/65 + 13/68 with nears 14/14, cross-frame reads
0/68 + 1/65 with nears 2/4; median drift reads −10..+5 with
|Δ| rank 257/301/277/343/340/296/321/342; the three |Δ|≤2
columns keep 0 pooled hits while the single kept hit (c340
r25, δ=38) sits at |Δ|=3; both fit-s0→m15 nears sit on c340
(r27/r31, δ=40 vs pred 41); medians read strictly below TRI
peaks on all 16 col-frames (med−h −1..−25); per-column
cross-frame mean|err| reads 3.2–12.6 with max 27 on c340.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| profile suite + median rule + falsification bars, recorded before running | recorded | `DESIGN.md`: M25-verbatim CONST + no-n<3 pin, drift/kept/medpeak/xerr formats, bars H1–H7/N |
| median + score reproduction + wall/exit/shas/determinism | measured | §Step 2: 16/16 medians + 12/13 + 0/1 + nears 14/14 + 2/4; 0.2 s; re-run identical |
| drift + drift-vs-keep + median-vs-peak + 0/68 anatomy + gap rows | measured | §Step 2: Δ/rank + keep join + 0/16 medpeak + xkept/xnear/xerr; gaps below |
| screenshot if a drift map discriminates (or absence reasoned) | measured | absent by rule: max pooled kept 1 at n≥8 (need ≥3); workdir copy only, 88546 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p local/research/M55 "/Volumes/Extreme SSD/m55"
cp local/research/M51/m51.py local/research/M55/m55.py
python3 -m py_compile local/research/M55/m55.py local/research/M55/control.py
cp local/research/M55/m55.py local/research/M55/control.py local/research/M55/DESIGN.md "/Volumes/Extreme SSD/m55/"
python3 m55.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m25/m25.txt" "/Volumes/Extreme SSD/m26/m26.txt" "/Volumes/Extreme SSD/m55" /Users/bradrichardson/dev/ssx3/local/research/M55 > m55.txt 2>&1
python3 control.py > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M55/` — `DESIGN.md`
(suite + median rule + bars, recorded before running),
`m55.py` (CONST + drift + medpeak + xerr + PNG writer),
`control.py` (known-median/known-drift synthetic control),
`REPORT.md` (this file). No PNG committed (absence reasoned
above).

Large outputs (not committed): `/Volumes/Extreme SSD/m55/` —
`m55.txt` (receipt: shas, baselines, Task-1 medians + scores
both frames, xkept/xnear site rows, drift + driftx + medpeak
+ xerr, re-run, PNG size), `control.txt`, `m55.py`,
`control.py`, `DESIGN.md` (working copies),
`m55-driftmap.png` (working copy, 88546 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`–`m54/`, or
other agents' dirs.

## Gap rows (exact next brief each needs)

1. Median-drift no-keep split (new): |Δ|≤2 columns
   (296/321/342) keep 0 pooled CONST hits while the single
   kept hit sits on c340 (|Δ|=3) — the M51 L1 finding
   mirrored at median level (there: low-drift 296/301 kept
   0, high-drift 257/340 kept 2 each). Needs its own brief
   only if drift-vs-survival matters: per-site cross-frame
   err tables joined with within-column δ spread, offline —
   no new harness code.
2. Median-below-peak offset (new): 0/16 col-frames read
   median==TRI peak h; med−h reads −1..−25, all negative
   (widest m15 c301 −25, then s0 c301 −15 and m15 c340
   −10). Needs its own brief only if median-peak offset
   matters: median-vs-hump-position tables, offline — no new
   harness code.
3. c340 transfer cluster (new): both fit-s0→m15 nears
   (r27/r31, δ=40 vs pred 41) + the single fit-m15→s0 hit
   (r25, δ=38) + 1 of 4 reverse nears (r33, δ=37 vs pred
   38) all sit on c340. Needs its own brief only if
   column-local transfer matters: c340 site-level transfer
   census, offline — no new harness code.
4. Interior-run failure structure (M54 gap 1, still open):
   37/55 pooled 2–3 sites read interior seats with 5–7 sign
   runs per n≥8 column. Needs its own brief only if
   run-local structure matters: per-run residual tables,
   offline — no new harness code.
5. Ragged-column catastrophic miss (M54 gap 2, still open):
   c296/c340 read max|res| 18/15 with mean|res| 9.44/7.56
   while smooth 257/277/321 read max ≤4. Needs its own
   brief only if ragged-vs-smooth matters: per-site
   profile-vs-fit tables on ragged columns, offline — no new
   harness code.
6. m15 c343 span-264 leverage (M54 gap 3, still open, minor):
   the r289 far-row site stretches the fit span to 264 rows.
   Needs its own brief only if outlier leverage matters:
   leave-one-row-out QUAD tables on c343, offline — no new
   harness code.
7. Peak-seat failure asymmetry (M54 gap 4, still open, minor):
   s0 2–3 sites read 5/32 peak seats vs m15 1/23. Needs its
   own brief only if peak failure matters: per-peak residual
   tables across further frames, offline — no new harness
   code.
8. Low-drift no-keep split (M54 gap 5 / M53 gap 3 / M51 gap 1,
   still open): c296/c301 read L1 2/4 but pooled kept 0/0,
   while c257/c340 (L1 15/10) keep 2 each (M55 tables the
   median-level mirror: gap 1 above — not worked). Needs its
   own brief only if drift-vs-survival matters: per-site
   kept-hit residual tables, offline — no new harness code.
9. Height-vs-edge leg attribution (M54 gap 6 / M53 gap 4 / M51
   gap 2, still open): |Δh|≥5 reads 3/8 while |Δe|≥3 reads
   6/8. Needs its own brief only if leg attribution matters:
   per-leg ablation tables, offline — no new harness code.
10. c340 peak-shift survival (M54 gap 7 / M53 gap 5 / M51 gap 3,
    still open, minor): c340 Δp=+6 (26→32) keeps pooled 2
    (TRI; M55: pooled 1 CONST + both s0-fit nears — tabled,
    not worked). Needs its own brief only if peak-shift
    survival matters: per-row prediction tables around
    shifted peaks, offline — no new harness code.
11. Peak-row agreement without value agreement (M54 gap 8 /
    M53 gap 6 / M51 gap 4 / M26 gap 2, still open): 5/8
    columns share peak rows cross-frame but only 6/65
    shared-site δ values agree (M25 H5). Needs its own brief
    only if peak anchoring matters: peak-anchored residual
    tables, offline — no new harness code.
12. m15 c343 row-289 site (M54 gap 10 / M53 gap 9 / M51 gap 8 /
    M26 gap 6 / M25 gap 3, still open): one tail site 262
    rows below its column's band (hole span 28–288), also
    m15 c343's argmax peak. Needs its own brief only if
    outlier isolation matters: far-row tail-site census,
    offline — no new harness code.
13. SIGN-corrected near-hit mass (M54 gap 11 / M53 gap 10 / M51
    gap 9 / M26 gap 7 / M24 gap 1, still open): 35 s0 / 38
    m15 tail bytes read |err|=1 after the best M24 correction
    vs 21/28 exact. Needs its own brief only if second-order
    structure matters: residual-sign tables around K45++SIGN,
    offline — no new harness code.
14. Streak-column residual coherence (M54 gap 12 / M53 gap 11 /
    M51 gap 10 / M26 gap 8 / M24 gap 2, still open): s0 c257
    reads r∈{−3,−2,0} only, c296 reads all |r|≤1, c342 reads
    all r≥1 (M55 worked δ-level, not r-level). Needs its own
    brief only if column-local correction matters:
    per-column r-profile tables + column-constant fits,
    offline — no new harness code.
15. Gap-bin 32–63 ±1 concentration (M54 gap 13 / M53 gap 12 /
    M51 gap 11 / M26 gap 9 / M24 gap 3, still open): 16/32 s0
    + 31/49 m15 |r|=1 sites sit in gap bin 32–63. Needs its
    own brief only if gap-local rounding matters:
    per-gap-value r tables within 32–63, offline — no new
    harness code.
16. POS cross-frame collapse (M54 gap 14 / M53 gap 13 / M51 gap
    12 / M26 gap 10 / M23 gap 3, still open): POS cell
    medians read 7/16 same-frame but 1/2 cross-frame. Needs
    its own brief only if position-value mapping matters:
    per-cell median drift tables s0 vs m15, offline — no new
    harness code.
17. Shape-733 tail divergence (M54 gap 15 / M53 gap 14 / M51 gap
    13 / M26 gap 11 / M23 gap 4, still open): shape 733's
    tail map reads Jaccard 0.6694 vs s0 (100 B) while
    727/764 shapes read byte-identical. Needs its own brief:
    per-byte attribution of 733's private sites, offline — no
    new harness code.
18. m15 private tail sites (M54 gap 16 / M53 gap 15 / M51 gap 14
    / M26 gap 12 / M23 gap 5, still open): 64/134 m15 tail
    sites never recur on any M16 shape (occ 0; Jaccard
    0.4132). Needs its own brief only if cross-sample tail
    identity matters: second-sample tail family, offline — no
    new harness code.
19. Shape-700 map divergence (M54 gap 17 / M53 gap 16 / M51 gap
    15 / M26 gap 13 / M21 gap 1, still open): shape 700's
    static map reads Jaccard 0.0747 vs s0 while 518/764 read
    byte-identical. Needs its own brief: per-byte attribution
    of 700's private sites, offline — no new harness code.
20. m15 static-map disjointness (M54 gap 18 / M53 gap 17 / M51
    gap 16 / M26 gap 14 / M21 gap 2, still open): m15 shares
    92/1476 static sites with s0 (Jaccard 0.0245). Needs its
    own brief only if cross-sample map identity matters,
    offline — no new harness code.
21. U/V co-residual mechanism (M54 gap 19 / M53 gap 18 / M51 gap
    17 / M26 gap 15 / M21 gap 3, still open): same-pixel U&V
    co-residual reads 16.0×/21.6× independence. Needs its own
    brief only if chroma pairing matters, offline — no new
    harness code.
22. δ-sign mechanism (M54 gap 20 / M53 gap 19 / M51 gap 18 /
    M26 gap 16 / M20 gap 2, still open, minor): δ>0 on
    80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full)
    ≈ 0.70 on both frames. Needs its own brief only if the
    sign asymmetry matters, offline — no new harness code.
23. m15 below-min far tail (M54 gap 21 / M53 gap 20 / M51 gap
    19 / M26 gap 17 / M19 gap 3, still open, minor): 4
    below-side bytes with dout ≥ 16 (max 47) on m15. Needs
    its own brief only if outlier isolation matters, offline
    — no new harness code.
24. Negative-share mechanism (M54 gap 22 / M53 gap 21 / M51 gap
    20 / M26 gap 18 / M18 gap 2, still open): 93 negatives
    (worst −244) unattributed at byte level. Needs its own
    brief: per-shape added-residual maps + EFB-copy diffing,
    offline — no new harness code.
25. Odin port readiness (M54 gap 23 / M53 gap 22 / M51 gap 21 /
    M26 gap 19 / M18 gap 3, still open): no Odin contract
    in-repo; handoff artifact stays `loo.txt` + dumps +
    synths. Needs its own brief once the consumer names its
    interface.
26. Top-HUD glyph residual isolation (M54 gap 24 / M53 gap 23 /
    M51 gap 22 / M26 gap 20 / M18 gap 4, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
27. Per-carrier weight centers (M54 gap 25 / M53 gap 24 / M51
    gap 23 / M26 gap 21 / M18 gap 5, still open, optional):
    effect-draw argmins at the fine-grid edge. Needs its own
    brief only if per-draw filter centers matter.

(Worked this run, dropped from the open list: M54 gap 9 /
M53 gap 8 / M51 gap 7 / M26 gap 5 / M25 gap 2 — CONST
cross-frame collapse, the median drift tables above.)

## What I could not do

1. No cross-shape check: the brief asks cross-frame only
   (fit-s0→m15 and vice versa), so shapes 1/2/733 are
   unscored — tabled scope, not chased.
2. No near-hit merging: 20 pooled near-hits (14/14 same-frame
   + 2/4 cross-frame) stay separate from the 26 pooled exact
   hits by rule.
3. c341 unscored: 0 s0 / 1 m15 sites — membership-guarded
   but outside the brief's 8 fit columns.
4. CONST is exact-integer throughout (no float path in this
   run outside shape-stat sds) — tabled as implemented.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M55/`: `DESIGN.md`, `m55.py`,
`control.py`, `REPORT.md` (this file). No PNG (0 B).
