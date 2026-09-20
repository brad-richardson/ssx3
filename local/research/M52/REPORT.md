# M52 — Peak-row vs value agreement: peak-anchored residual tables: REPORT

M26 gap 2 worked at table level: peak-anchored residual tables
(res = δ − column-peak-δ, off = row − peak-row, exact integer
arith) for the 8 named streak columns on s0 + m15 plus
agreement-vs-distance-from-peak (do the 6 δ-agreeing sites sit
AT peaks? do peak rows agree in residual while disagreeing in
δ?). H5 + peaks reproduce M25/M26-verbatim byte-exactly (6/65
with per-column 0/0/1/0/2/2/0/1; 5/8 peaks); the 6 δ-agrees sit
at s0-peak distance 0 on 2/6 sites and m15-peak distance 0 on
0/6, with 5/6 held by peak-disagreeing columns; H5 re-scored on
residuals reads 14/65 (near 17), disjoint from the 6 δ-agrees
(overlap 0). Fully offline — no lease of any kind, no boots, no
harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M52.md`. Tables, no verdicts.

Headers read first: `local/research/M26/REPORT.md` (all of it:
5/8 peak rows agree — 257:25/25, 277:25/25, 296:26/26,
301:27/27, 342:27/27; differ 321:25/26, 340:26/32, 343:27/289)
plus `local/research/M25/REPORT.md` (H5: 6/65 pooled,
per-column agrees 0/0/1/0/2/2/0/1 over n 10/10/9/11/10/8/5/2;
no column all-equal).

Time box 4 hours (start 2026-09-20 07:14 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m51/` — all outputs went to the new
`/Volumes/Extreme SSD/m52/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), `m25.txt` (H5 xmatch
lines to reproduce) and `m26.txt` (hump + xshape lines to
reproduce). Work dir `/Volumes/Extreme SSD/m52/`; evidence
`local/research/M52/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M51; m25.txt prefix matches M26):

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

(Full hexes in `m52.txt` §inputs.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M51 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m52.py` invocation (the receipt, 0.1 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try). No pre-receipt fixes;
DESIGN.md was recorded before either invocation and is
unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m52.py receipt | 0.1 s | exit 0; all guards pass; canon `f8bec621…278e38` |
| control.py C-P1 (known peaks+agrees) | <1 s | green; peaks/agrees/distances/residuals exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 profiles + H5/peak guards) | 2 | 0.0 s |
| Task 2 (residuals + distances + xres) | 2 | <1 s |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m52.py` wall | — | 0.1 s |

## Step 2 — estimates

### Task 1 — H5 + peak reproduction (do the splits reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M25/M26 EXACTLY, all 32+32
M25 profile lines matching `m25.txt` byte-exactly on BOTH
frames, all 9 xmatch lines matching `m25.txt` byte-exactly and
all 16 hump + 9 xshape lines matching `m26.txt` byte-exactly
(stop rule not triggered). Named-column bytes read 65 s0 /
68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V).

Agreement table (H5 reproduced: 6/65 shared sites agree exactly,
share 0.0923; per-column agrees 0/0/1/0/2/2/0/1 over n
10/10/9/11/10/8/5/2; no column all-equal — the 6 agreeing sites
named):

| col | r | s0-δ | m15-δ | agree | d_s0 | d_m15 |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 296 | 32 | 46 | 46 | True | 6 | 6 |
| 321 | 23 | 14 | 14 | True | 2 | 3 |
| 321 | 24 | 24 | 24 | True | 1 | 2 |
| 340 | 25 | 38 | 38 | True | 1 | 7 |
| 340 | 26 | 47 | 47 | True | 0 | 6 |
| 343 | 27 | −26 | −26 | True | 0 | 262 |

(All 65 shared-site `agree` lines in the receipt; the 59
disagreeing sites tabled there with |diff| values.)

Peak table (M26 reproduced: peak rows agree 5/8; tie rule
M26-verbatim, first on ties):

| col | peak s0/m15 | equal? | peakval s0/m15 |
| ---: | --- | --- | --- |
| 257 | 25/25 | True | 30/20 |
| 277 | 25/25 | True | 28/20 |
| 296 | 26/26 | True | 47/46 |
| 301 | 27/27 | True | 47/48 |
| 321 | 25/26 | False | 27/31 |
| 340 | 26/32 | False | 47/48 |
| 342 | 27/27 | True | −16/−13 |
| 343 | 27/289 | False | −26/−15 |

Peak×agree join (per column peak-agree × n-agree):

| col | peak-agree? | shared | n-agree |
| ---: | --- | ---: | ---: |
| 257 | True | 10 | 0 |
| 277 | True | 10 | 0 |
| 296 | True | 9 | 1 |
| 301 | True | 11 | 0 |
| 321 | False | 10 | 2 |
| 340 | False | 8 | 2 |
| 342 | True | 5 | 0 |
| 343 | False | 2 | 1 |

Pooled: in-peakagree-cols shared=45 agree=1; outside
shared=20 agree=5.

### Task 2 — peak-anchored residuals (positional vs value split?)

Residual tables: per column per frame res = δ − peakval with
row offsets off = row − peakrow (exact integer arith; full
(row:δ:res:off) quads in the receipt `resid` lines):

| Frame | col | peak p/h | res in row order | off in row order |
| --- | ---: | ---: | --- | --- |
| s0 | 257 | 25/30 | −13 −2 0 −1 −1 −1 −1 −2 −7 −17 | −2 −1 0 1 2 3 4 5 6 7 |
| s0 | 277 | 25/28 | −12 −3 0 −1 −1 0 0 0 −4 −15 | −2 −1 0 1 2 3 4 5 6 7 |
| s0 | 296 | 26/47 | −26 −6 0 −12 −28 … −16 −1 −8 −32 | −2 −1 0 1 2 … 5 6 7 8 |
| s0 | 301 | 27/47 | −29 −18 −14 −6 0 −1 −8 −15 −22 −31 −34 | −4 −3 −2 −1 0 1 2 3 4 5 6 |
| s0 | 321 | 25/27 | −13 −3 0 0 −1 −1 −1 −2 −6 −16 | −2 −1 0 1 2 3 4 5 6 7 |
| s0 | 340 | 26/47 | −30 −9 0 −2 … −3 0 −10 −30 | −2 −1 0 1 … 5 6 7 8 |
| s0 | 342 | 27/−16 | 0 −11 −2 … 0 −1 | 0 1 2 … 7 8 |
| s0 | 343 | 27/−26 | −5 0 | −1 0 |
| m15 | 257 | 25/20 | −8 −2 0 0 −1 0 0 −1 −4 −12 | −2 −1 0 1 2 3 4 5 6 7 |
| m15 | 277 | 25/20 | −8 −1 0 0 −1 0 0 −1 −5 −12 | −2 −1 0 1 2 3 4 5 6 7 |
| m15 | 296 | 26/46 | −30 −9 0 −6 −16 … −8 0 −9 −30 | −2 −1 0 1 2 … 5 6 7 8 |
| m15 | 301 | 27/48 | −36 −30 −24 −11 0 −1 −13 −25 −32 −35 −30 | −4 −3 −2 −1 0 1 2 3 4 5 6 |
| m15 | 321 | 26/31 | −17 −7 −2 0 0 −2 −3 −3 −7 −17 | −3 −2 −1 0 1 2 3 4 5 6 |
| m15 | 340 | 32/48 | −32 −10 −1 −8 −18 … −8 0 −10 −34 | −8 −7 −6 −5 −4 … −1 0 1 2 |
| m15 | 342 | 27/−13 | 0 −7 −1 … −6 −8 | 0 1 2 … 7 8 |
| m15 | 343 | 289/−15 | −7 −19 −11 … 0 | −264 −263 −262 … 0 |

(… marks hole spans; m15 c343's shared rows sit at off
−263/−262 under its r289 peak.)

Distance table: each shared site's row distance from its column
peak vs agree flag (all 65 `dist` lines in the receipt; the 6
δ-agreeing rows excerpted in Task 1 above; the 14
residual-agreeing rows below):

| col | r | δ s0/m15 | agree_δ | d_s0 | d_m15 | res s0/m15 | agree_res |
| ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| 257 | 24 | 28/18 | False | 1 | 1 | −2/−2 | True |
| 257 | 25 | 30/20 | False | 0 | 0 | 0/0 | True |
| 257 | 27 | 29/19 | False | 2 | 2 | −1/−1 | True |
| 277 | 25 | 28/20 | False | 0 | 0 | 0/0 | True |
| 277 | 27 | 27/19 | False | 2 | 2 | −1/−1 | True |
| 277 | 28 | 28/20 | False | 3 | 3 | 0/0 | True |
| 277 | 29 | 28/20 | False | 4 | 4 | 0/0 | True |
| 296 | 26 | 47/46 | False | 0 | 0 | 0/0 | True |
| 301 | 27 | 47/48 | False | 0 | 0 | 0/0 | True |
| 301 | 28 | 46/47 | False | 1 | 1 | −1/−1 | True |
| 321 | 26 | 27/31 | False | 1 | 0 | 0/0 | True |
| 340 | 32 | 47/48 | False | 6 | 0 | 0/0 | True |
| 340 | 33 | 37/38 | False | 7 | 1 | −10/−10 | True |
| 342 | 27 | −16/−13 | False | 0 | 0 | 0/0 | True |

Overlap: the 6 δ-agreeing sites all read agree_res=False and
the 14 residual-agreeing sites all read agree_δ=False —
δ∩res overlap 0/65.

Marginals (agree rates by peak-distance bin, pooled over the 65
shared sites):

| anchor | d=0 (n/agd/agr) | d=1 | d=2 | d=3 | d=4+ |
| --- | --- | --- | --- | --- | --- |
| d_s0 | 8 / 2 / 5 | 14 / 2 / 3 | 12 / 1 / 2 | 5 / 0 / 1 | 26 / 1 / 3 |
| d_m15 | 7 / 0 / 7 | 13 / 0 / 3 | 12 / 1 / 2 | 6 / 1 / 1 | 27 / 4 / 1 |

(agd = δ-agrees, agr = residual-agrees per bin. All 7 shared
sites at d_m15==0 res-agree (res 0=0 at m15 peaks); 5/8 at
d_s0==0 res-agree — the 3 exceptions read (321,25): 0 vs −2,
(340,26): 0 vs −1, (343,27): 0 vs −11.)

Residual-agreement table (H5 re-scored on peak-subtracted δ):

| col | shared | res-agree | share | near (|Δres|=1) | sites |
| ---: | ---: | ---: | --- | ---: | --- |
| 257 | 10 | 3 | 0.3000 | 4 | 24, 25, 27 |
| 277 | 10 | 4 | 0.4000 | 3 | 25, 27, 28, 29 |
| 296 | 9 | 1 | 0.1111 | 2 | 26 |
| 301 | 11 | 2 | 0.1818 | 0 | 27, 28 |
| 321 | 10 | 1 | 0.1000 | 5 | 26 |
| 340 | 8 | 2 | 0.2500 | 2 | 32, 33 |
| 342 | 5 | 1 | 0.2000 | 1 | 27 |
| 343 | 2 | 0 | 0.0000 | 0 | — |

Pooled: 14/65 res-agree (share 0.2154), near 17 (δ baseline for
comparison: 6/65 agree).

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 peaks (listed A/B, 4 pseudo-cols) | 28/28, 26/27, 26/26, 26/27 exact incl. first-tie c904 | exact | True |
| C-P1 residuals (quads via `peak_residual`) | all 30 listed res values exact | exact | True |
| C-P1 δ-agrees (sites + counts) | 4/15 at (901,26),(901,28),(902,29),(904,27) | exact | True |
| C-P1 distances (agree-site d_A/d_B) | (2,2),(0,0),(3,2),(1,0) exact | exact | True |
| C-P1 peak-agree (2/4: 901,903) | exact | exact | True |
| C-P1 res-agrees (sites + counts) | 6/15 at listed sites incl. c902-r28 ≠ δ site + c903 2/3 from 0/3 δ | exact | True |

(Full per-site lines in `control.txt`; the control runs m52's
exact Task-1/Task-2 join functions on the listed profiles. The
`dist` line labels read s0/m15 for the A/B frames — format
artifact, values exact.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15) pass1 `f8bec621…278e38` vs pass2
`f8bec621…278e38`, identical=True; cell counts identical=True;
tail counts identical=True.

## Step 3 — attribute

Model comparison (shared-site agreement, peak-anchored scope —
attribution, not explanation):

| Scope | Model | shared | agree | e |
| --- | --- | ---: | ---: | --- |
| 65 shared (col,row) sites | δ exact (H5) | 65 | 6 | 0.0923 |
| 65 shared (col,row) sites | residual exact (peak-subtracted) | 65 | 14 | 0.2154 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_ATPEAK_S0 | δ-agreeing sites with d_s0==0 share ≥ 0.50 | 2/6 = 0.3333 — not met |
| H2_ATPEAK_M15 | δ-agreeing sites with d_m15==0 share ≥ 0.50 | 0/6 = 0.0000 — not met |
| H3_RESRISE | residual agrees exceed δ agrees by ≥10 sites | 14 − 6 = 8 — not met |
| H4_RESLEVEL | residual agree share ≥ 0.25 over 65 shared | 14/65 = 0.2154 — not met |
| H5_PEAKHOLD | δ-agrees in peak-agreeing cols share ≥ 0.75 | 1/6 = 0.1667 — not met |
| H6_DISTGRAD | δ-agree rate at d_s0==0 exceeds rate at d_s0≥4 by ≥ 0.20 | 2/8 − 1/26 = 0.2115 — met |
| H7_RESATPEAK | residual-agrees with d_s0==0 share ≥ 0.50 | 5/14 = 0.3571 — not met |
| N | shared-site δ after peak-anchored residuals + remaining split | 14 res-agree + 17 res-near; 51/65 non-agreeing stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
column (the 6 δ-agrees sit in 4/8 columns — 296/321/340/343 —
with 5/6 in the 3 peak-disagreeing columns), by distance (the 2
δ-agrees at s0 peaks read d_m15 6 and 262; the other 4 read
d_s0 1–6), and by frame peak (m15 c343's r289 peak strands its
2 shared sites at d_m15 262–263). Task 2 discriminates by
agreement type (14 res-agrees disjoint from the 6 δ-agrees;
17 res-near tabled separately), by anchor (7/7 d_m15==0 sites
res-agree vs 5/8 at d_s0==0; the 3 s0-peak exceptions read
0-vs-negative), and by column (res-agrees spread 0–4 with c343
0/2 and c277 4/10; off-peak res-agrees read 7/58 outside
d_m15==0).

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
| interior far tail, TRI-hit | 18 of cell 7 (0.7%) | δ=TRI pred exact, named-col scope (M26, unchanged) |
| interior far tail, standing | 84 of cell 7 (3.4%) | 47 named-col + 37 outside-named; stands (M26, unchanged) |
| shared-site residual agreement | 14 of 65 shared sites | res_s0==res_m15 exact, disjoint from 6 δ-agrees (this run) |
| shared-site residual near | 17 of 65 shared sites | |res_s0−res_m15|==1, separate (this run) |
| shared-site residual disagree | 34 of 65 shared sites | stands (this run) |
| standing interior remainder | 2457 of cell 7 (99.3%) | 2475 − 18 TRI hits (M52 adds no byte fits) |
| standing remainder (total) | 22797 (99.9% of R_0) | 18 B tail-explained; rest split above |

Screenshot: present by rule. The evidence residual map
(`m52-resmap.png`, 102706 B of 5242880 budget) colors s0
named-column sites by residual-agreement outcome (agree 14 /
near 17 / disagree 34); DESIGN.md admits an evidence copy iff
some named column with shared-n≥8 reads residual-agree-count −
δ-agree-count ≥ 2 — c257 (+3, n=10), c277 (+4, n=10) and c301
(+2, n=11) qualify.

Recorded without verdict: H5 + peaks reproduce byte-exactly
(6/65 with per-column 0/0/1/0/2/2/0/1; 5/8 peaks); the 6
δ-agreeing sites read (296,32),(321,23),(321,24),(340,25),
(340,26),(343,27) with s0-peak distances 6/2/1/1/0/0 and
m15-peak distances 6/3/2/7/6/262, 5/6 held by peak-disagreeing
columns; peak-subtracted residuals agree on 14/65 shared sites
with 17 near, per-column 3/4/1/2/1/2/1/0, disjoint from the 6
δ-agrees; 7/7 d_m15==0 sites res-agree vs 5/8 at d_s0==0;
51/65 shared sites stand non-agreeing in residual.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| peak-anchored suite + falsification bars, recorded before running | recorded | `DESIGN.md`: H5/peak guards, res/off/d definitions, bars H1–H7/N |
| H5 + peak reproduction tables + residual tables + wall/exit/shas/determinism | measured | §Step 2: 65 agree lines + peaks + peakjoin; resid + dist + xres tables; 0.1 s; re-run identical |
| explained-vs-standing update (do peak rows agree in residual while disagreeing in δ? by how much?) + gap rows | measured | §Step 3: 14/65 res-agree, disjoint from 6/65 δ; 51/65 stands; gaps below |
| screenshot if a residual map discriminates (or absence reasoned) | measured | present by rule: c257/c277/c301 gap +3/+4/+2 at n≥8; 102706 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m52"
cp local/research/M52/DESIGN.md local/research/M52/m52.py local/research/M52/control.py "/Volumes/Extreme SSD/m52/"
python3 m52.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m25/m25.txt" "/Volumes/Extreme SSD/m26/m26.txt" "/Volumes/Extreme SSD/m52" /Users/bradrichardson/dev/ssx3/local/research/M52 > m52.txt 2>&1
python3 control.py > control.txt 2>&1
cp "/Volumes/Extreme SSD/m52/m52-resmap.png" local/research/M52/m52-resmap.png
```

## Paths

Evidence (committed): `local/research/M52/` — `DESIGN.md`
(suite + bars, recorded before running), `m52.py` (H5/peak
guards + residual tables + PNG writer), `control.py`
(known-peak/known-agree listed-truth control),
`m52-resmap.png` (residual map, 102706 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m52/` —
`m52.txt` (receipt: shas, baselines, Task-1 agree + peakjoin,
Task-2 resid + dist + xres, pngrule, re-run, PNG size),
`control.txt`, `m52.py`, `control.py`, `DESIGN.md` (working
copies), `m52-resmap.png` (working copy, 102706 B). No writes
into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`–`m51/`, or other
agents' dirs.

## Gap rows (exact next brief each needs)

1. δ∩residual disjointness (new): 0/65 shared sites agree in
   BOTH δ and peak-subtracted residual — the 6 δ-agrees all
   read res-disagree and the 14 res-agrees all read δ-
   disagree. Needs its own brief only if joint-agreement
   structure matters: joint (agree_δ × agree_res) contingency
   tables + |Δδ| vs |Δres| scatter tables, offline — no new
   harness code.
2. Off-peak residual agreement (new): 7/7 d_m15==0 sites
   res-agree by peak construction (res 0=0), leaving 7/58
   off-peak res-agrees as the informative mass. Needs its own
   brief only if off-peak structure matters: off-peak-only
   residual tables (d_s0>0 AND d_m15>0), offline — no new
   harness code.
3. c343 r289 peak anchoring (new): m15 c343's peak at r289
   strands its 2 shared sites at d_m15 262–263 and off
   −263/−262, the only degenerate-anchored column (0/2
   res-agree). Needs its own brief only if outlier anchoring
   matters: band-anchored (non-peak) residual tables for
   c343, offline — no new harness code.
4. H6 small-n gradient (new, minor): the d_s0==0 vs d_s0≥4
   δ-agree gap reads 0.2115 but on numerators 2/8 vs 1/26.
   Needs its own brief only if distance-graded agreement
   matters: per-distance agreement pooled over wider frame
   pairs, offline — no new harness code.
5. TRI cross-frame collapse (M26 gap 1, still open): TRI
   fit-s0→m15 reads 4/68 (2/65 the other way) vs 18/16
   same-frame. Needs its own brief only if shape transfer
   matters: per-column triangle-drift (p/h/e/w s0 vs m15)
   tables, offline — no new harness code.
6. Index-top argmax concentration (M26 gap 3, still open):
   6/8 s0 + 5/8 m15 argmax read top-third by index under the
   first-tie rule. Needs its own brief only if peak-position
   convention matters: plateau-aware peak tables (all-tie
   rows + run-center rules), offline — no new harness code.
7. QUAD underfit (M26 gap 4, still open, minor): smooth
   quadratic reads 4/65 + 3/68 with 32/23 mass in the 2–3
   miss bin. Needs its own brief only if curvature matters:
   per-column quadratic-residual tables, offline — no new
   harness code.
8. CONST cross-frame collapse (M25 gap 2, still open): s0
   column medians score 0/68 on m15 (1/65 the other way) vs
   12/13 same-frame. Needs its own brief only if column-value
   mapping matters: per-column median drift tables s0 vs m15,
   offline — no new harness code.
9. m15 c343 row-289 site (M25 gap 3, still open): one tail
   site 262 rows below its column's band, now also m15 c343's
   argmax peak and M52's degenerate anchor. Needs its own
   brief only if outlier isolation matters: far-row tail-site
   census, offline — no new harness code.
10. SIGN-corrected near-hit mass (M24 gap 1, still open): 35
    s0 / 38 m15 tail bytes read |err|=1 after the best M24
    correction vs 21/28 exact. Needs its own brief only if
    second-order structure matters: residual-sign tables
    around K45++SIGN, offline — no new harness code.
11. Streak-column residual coherence (M24 gap 2, still open):
    s0 c257 reads r∈{−3,−2,0} only, c296 reads all |r|≤1,
    c342 reads all r≥1 (M52 worked δ-level residuals, not
    r-level). Needs its own brief only if column-local
    correction matters: per-column r-profile tables +
    column-constant fits, offline — no new harness code.
12. Gap-bin 32–63 ±1 concentration (M24 gap 3, still open):
    16/32 s0 + 31/49 m15 |r|=1 sites sit in gap bin 32–63.
    Needs its own brief only if gap-local rounding matters:
    per-gap-value r tables within 32–63, offline — no new
    harness code.
13. POS cross-frame collapse (M23 gap 3, still open): POS cell
    medians read 7/16 same-frame but 1/2 cross-frame (M52's
    δ/res disjointness reads 6 vs 14 with 0 overlap — tabled,
    same family at residual level). Needs its own brief only
    if position-value mapping matters: per-cell median drift
    tables s0 vs m15, offline — no new harness code.
14. Shape-733 tail divergence (M23 gap 4, still open): shape
    733's tail map reads Jaccard 0.6694 vs s0 (100 B) while
    727/764 shapes read byte-identical (731 next-lowest at
    0.6833). Needs its own brief: per-byte attribution of
    733's private sites (tail-set change vs δ change),
    offline — no new harness code.
15. m15 private tail sites (M23 gap 5, still open): 64/134 m15
    tail sites never recur on any M16 shape (occ 0; Jaccard
    0.4132). Needs its own brief only if cross-sample tail
    identity matters: second-sample tail family, offline — no
    new harness code.
16. Shape-700 map divergence (M21 gap 1, still open): shape
    700's static map reads Jaccard 0.0747 vs s0 while 518/764
    read byte-identical. Needs its own brief: per-byte
    attribution of 700's private sites, offline — no new
    harness code.
17. m15 static-map disjointness (M21 gap 2, still open): m15
    shares 92/1476 static sites with s0 (Jaccard 0.0245).
    Needs its own brief only if cross-sample map identity
    matters, offline — no new harness code.
18. U/V co-residual mechanism (M21 gap 3, still open): same-pixel
    U&V co-residual reads 16.0×/21.6× independence. Needs its
    own brief only if chroma pairing matters, offline — no new
    harness code.
19. δ-sign mechanism (M20 gap 2, still open, minor): δ>0 on
    80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈
    0.70 on both frames. Needs its own brief only if the sign
    asymmetry matters, offline — no new harness code.
20. m15 below-min far tail (M19 gap 3, still open, minor): 4
    below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
    own brief only if outlier isolation matters, offline — no
    new harness code.
21. Negative-share mechanism (M18 gap 2, still open): 93
    negatives (worst −244) unattributed at byte level. Needs
    its own brief: per-shape added-residual maps + EFB-copy
    diffing, offline — no new harness code.
22. Odin port readiness (M18 gap 3, still open): no Odin
    contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
23. Top-HUD glyph residual isolation (M18 gap 4, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
24. Per-carrier weight centers (M18 gap 5, still open,
    optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers
    matter.

(M26 gap 2 — this brief — is worked above and drops off the
open list.)

## What I could not do

1. No cross-shape check: the brief asks cross-frame only
   (s0 vs m15), so shapes 1/2/733 are unscored — tabled
   scope, not chased.
2. No near-hit merging: 17 pooled res-near stay separate
   from the 14 exact res-agrees by rule.
3. c341 unscored: 0 s0 / 1 m15 sites — membership-guarded
   but outside the brief's 8 columns.
4. Exact-integer paths: res/off/d run exact-integer with no
   rounding (per DESIGN.md); float64 appears only in the
   reused profile sd/topmean/botmean stats — tabled as
   implemented.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M52/`: `DESIGN.md`, `m52.py`,
`control.py`, `m52-resmap.png` (102706 B), `REPORT.md` (this
file).
