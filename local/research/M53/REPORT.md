# M53 — Index-top argmax concentration: plateau-aware peak tables: REPORT

M26 gap 3 worked at table level: plateau-aware peak tables (all-tie
rows + tie shapes + submax census + run-center rules R1/R2 with
thirds + peak-row agreement recomputed under run-center), with M26's
16 first-tie hump lines + 9 xshape lines + M25's 64 profile lines
reproduced byte-exactly. Max-ties read 8/16 multi-tie column-frames
(s0 c277 T=4 multirun, c321/c340/c342 T=2; m15 c257/c277 T=4
multirun, c296/c321 T=2) with the named c257 29x4 submax run + c340
twin 47s recovered; R1 (middle-of-longest-run) moves 1/16 peaks (s0
c277 25→29, top→mid) with top-third 5/8 + 5/8 and agreement 4/8,
while R2 (mean-of-ties) moves 8/16 with top-third 3/8 + 1/8 and
agreement 1/8; cited M51 TRI p equals R1 on 15/16. Fully offline —
no lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M53.md`. Tables, no
verdicts.

Headers read first: `local/research/M26/REPORT.md` (all of it: hump
table 8x2 peaks/thirds, 6/8 s0 + 5/8 m15 top-third, 5/8 peak
agreement, TRI p/h/e/w, c257's 29x4 run + c340's twin 47s) plus
`local/research/M25/REPORT.md` (all of it: the 32 profile lines —
row→δ lists with holes — plus CONST collapse) plus
`local/research/M51/REPORT.md` (TRI p values cited in Task 2.3, not
refit).

Time box 4 hours (start 2026-09-20 07:27 EDT); used about 0.1. No
lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m52/` — all outputs went to the new
`/Volumes/Extreme SSD/m53/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), `m25.txt` (column profiles
to reproduce) and `m26.txt` (hump + xshape lines to reproduce).
Work dir `/Volumes/Extreme SSD/m53/`; evidence
`local/research/M53/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M52):

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

(Full hexes in `m53.txt` §inputs; `m25.txt` 15578 B, `m26.txt`
18821 B. `m26.txt` sha matches M51's record.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M52 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m53.py` invocation (the receipt, 0.4 s, exit 0 — the estimator
was never changed after the receipt run started); two `control.py`
invocations (first red on a hand-estimate transcription: T2's
R2 row 82 is present, DESIGN pinned absent — thirds unaffected;
DESIGN + control expectation corrected pre-receipt, second green).
DESIGN.md was recorded before running; the correction is staging,
not results.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m53.py receipt | 0.4 s | exit 0; all guards pass; canon `9793fcc2…ef45` |
| control.py C-P1 (known plateaus) | <1 s | green; 6 pseudo-cols exact (2nd try) |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 profiles + ties + census) | 2 | 0.0 s |
| Task 2 (R1/R2 + agreement + p-impact) | 2 | <1 s |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m53.py` wall | — | 0.4 s |

## Step 2 — estimates

### Task 1 — first-tie reproduction + all-tie rows

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M22/M23/M25/M26 EXACTLY, all
64 M25 profile lines (prof rowdelta + holes + shape stats +
roworder) matching `m25.txt` byte-exactly, and all 16 M26 hump
lines + 9 xshape lines matching `m26.txt` byte-exactly on BOTH
frames (stop rule not triggered). Named-column bytes read 65 s0 /
68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V).

First-tie table: all 8 columns × s0/m15 peak/third (16 rows,
M26-verbatim reproduced):

| Frame | col | peakrow/peakval | k/n | third |
| --- | ---: | ---: | --- | --- |
| s0 | 257 | 25/30 | 2/10 | top |
| s0 | 277 | 25/28 | 2/10 | top |
| s0 | 296 | 26/47 | 2/9 | top |
| s0 | 301 | 27/47 | 4/11 | mid |
| s0 | 321 | 25/27 | 2/10 | top |
| s0 | 340 | 26/47 | 2/8 | top |
| s0 | 342 | 27/−16 | 0/5 | top |
| s0 | 343 | 27/−26 | 1/2 | mid |
| m15 | 257 | 25/20 | 2/10 | top |
| m15 | 277 | 25/20 | 2/10 | top |
| m15 | 296 | 26/46 | 2/9 | top |
| m15 | 301 | 27/48 | 4/11 | mid |
| m15 | 321 | 26/31 | 3/10 | top |
| m15 | 340 | 32/48 | 6/9 | bottom |
| m15 | 342 | 27/−13 | 0/5 | top |
| m15 | 343 | 289/−15 | 3/4 | bottom |

First-tie thirds pooled: s0 top 6/8 mid 2/8 bottom 0/8; m15 top
5/8 mid 1/8 bottom 2/8. First-tie agreement 5/8 (257/277/296/301/
342 agree).

All-tie table: every row attaining column max per column per frame
(tie counts + rows — the new data):

| Frame | col | max | T | rows |
| --- | ---: | ---: | ---: | --- |
| s0 | 257 | 30 | 1 | [25] |
| s0 | 277 | 28 | 4 | [25, 28, 29, 30] |
| s0 | 296 | 47 | 1 | [26] |
| s0 | 301 | 47 | 1 | [27] |
| s0 | 321 | 27 | 2 | [25, 26] |
| s0 | 340 | 47 | 2 | [26, 32] |
| s0 | 342 | −16 | 2 | [27, 34] |
| s0 | 343 | −26 | 1 | [27] |
| m15 | 257 | 20 | 4 | [25, 26, 28, 29] |
| m15 | 277 | 20 | 4 | [25, 26, 28, 29] |
| m15 | 296 | 46 | 2 | [26, 32] |
| m15 | 301 | 48 | 1 | [27] |
| m15 | 321 | 31 | 2 | [26, 27] |
| m15 | 340 | 48 | 1 | [32] |
| m15 | 342 | −13 | 1 | [27] |
| m15 | 343 | −15 | 1 | [289] |

(Multi-tie column-frames: 8/16 — s0 c277/c321/c340/c342, m15
c257/c277/c296/c321.)

Tie-shape table: per column per frame tie pattern (singleton / run
/ scattered / multirun + run lengths):

| Frame | col | shape | nruns | runlens | runs |
| --- | ---: | --- | ---: | --- | --- |
| s0 | 257 | singleton | 1 | [1] | [[25]] |
| s0 | 277 | multirun | 2 | [1, 3] | [[25], [28, 29, 30]] |
| s0 | 296 | singleton | 1 | [1] | [[26]] |
| s0 | 301 | singleton | 1 | [1] | [[27]] |
| s0 | 321 | run | 1 | [2] | [[25, 26]] |
| s0 | 340 | scattered | 2 | [1, 1] | [[26], [32]] |
| s0 | 342 | scattered | 2 | [1, 1] | [[27], [34]] |
| s0 | 343 | singleton | 1 | [1] | [[27]] |
| m15 | 257 | multirun | 2 | [2, 2] | [[25, 26], [28, 29]] |
| m15 | 277 | multirun | 2 | [2, 2] | [[25, 26], [28, 29]] |
| m15 | 296 | scattered | 2 | [1, 1] | [[26], [32]] |
| m15 | 301 | singleton | 1 | [1] | [[27]] |
| m15 | 321 | run | 1 | [2] | [[26, 27]] |
| m15 | 340 | singleton | 1 | [1] | [[32]] |
| m15 | 342 | singleton | 1 | [1] | [[27]] |
| m15 | 343 | singleton | 1 | [1] | [[289]] |

(Among T>1 column-frames: single-run 2/8 — s0 c321 + m15 c321;
scattered 3/8 — s0 c340/c342 + m15 c296; multirun 3/8 — s0 c277 +
m15 c257/c277.)

Submax plateau census (auxiliary, pinned — maximal equal-δ runs
L≥2, row-number-consecutive, any value):

| Frame | col | nruns | runs |
| --- | ---: | ---: | --- |
| s0 | 257 | 1 | 26-29:29x4 |
| s0 | 277 | 2 | 26-27:27x2;28-30:28x3 |
| s0 | 296 | 0 | none |
| s0 | 301 | 0 | none |
| s0 | 321 | 2 | 25-26:27x2;27-29:26x3 |
| s0 | 340 | 0 | none |
| s0 | 342 | 0 | none |
| s0 | 343 | 0 | none |
| m15 | 257 | 2 | 25-26:20x2;28-29:20x2 |
| m15 | 277 | 2 | 25-26:20x2;28-29:20x2 |
| m15 | 296 | 0 | none |
| m15 | 301 | 0 | none |
| m15 | 321 | 2 | 26-27:31x2;29-30:28x2 |
| m15 | 340 | 0 | none |
| m15 | 342 | 0 | none |
| m15 | 343 | 0 | none |

(The named c257 29x4 run reads s0 c257 26-29 at δ=29 = max−1; c340
carries no equal-δ run — its twin 47s are 6 rows apart across the
28–30 hole.)

### Task 2 — run-center rules

Run-center table: peak recomputed as run center per column per
frame (R1 primary + R2 auxiliary) + thirds under run-center:

| Frame | col | FT peak/third | R1 peak/k/third | R1 moved? | R2 peak/pres/k/third | R2 moved? |
| --- | ---: | --- | --- | --- | --- | --- |
| s0 | 257 | 25/top | 25/2/10/top | False | 25/T/2/10/top | False |
| s0 | 277 | 25/top | 29/6/10/mid | True | 28/T/5/10/mid | True |
| s0 | 296 | 26/top | 26/2/9/top | False | 26/T/2/9/top | False |
| s0 | 301 | 27/mid | 27/4/11/mid | False | 27/T/4/11/mid | False |
| s0 | 321 | 25/top | 25/2/10/top | False | 26/T/3/10/top | True |
| s0 | 340 | 26/top | 26/2/8/top | False | 29/F/4/8/mid | True |
| s0 | 342 | 27/top | 27/0/5/top | False | 31/F/3/5/mid | True |
| s0 | 343 | 27/mid | 27/1/2/mid | False | 27/T/1/2/mid | False |
| m15 | 257 | 25/top | 25/2/10/top | False | 27/T/4/10/mid | True |
| m15 | 277 | 25/top | 25/2/10/top | False | 27/T/4/10/mid | True |
| m15 | 296 | 26/top | 26/2/9/top | False | 29/F/5/9/mid | True |
| m15 | 301 | 27/mid | 27/4/11/mid | False | 27/T/4/11/mid | False |
| m15 | 321 | 26/top | 26/3/10/top | False | 27/T/4/10/mid | True |
| m15 | 340 | 32/bottom | 32/6/9/bottom | False | 32/T/6/9/bottom | False |
| m15 | 342 | 27/top | 27/0/5/top | False | 27/T/0/5/top | False |
| m15 | 343 | 289/bottom | 289/3/4/bottom | False | 289/T/3/4/bottom | False |

(R1 moves 1/16 peaks: s0 c277 25→29. R2 moves 8/16: every
multi-tie column-frame (s0 c277/c321/c340/c342, m15
c257/c277/c296/c321); R2 rows absent on s0 c340 (r29, hole),
s0 c342 (r31, hole), m15 c296 (r29, hole).)

Thirds pooled per rule per frame:

| Rule | s0 top/mid/bottom | m15 top/mid/bottom |
| --- | --- | --- |
| FT (first-tie) | 6/8, 2/8, 0/8 | 5/8, 1/8, 2/8 |
| R1 | 5/8, 3/8, 0/8 | 5/8, 1/8, 2/8 |
| R2 | 3/8, 5/8, 0/8 | 1/8, 5/8, 2/8 |

Agreement table: peak-row agreement under run-center (R1 primary +
R2 auxiliary):

| col | FT s0/m15 | R1 s0/m15 | R1 eq? | R2 s0/m15 | R2 eq? |
| ---: | --- | --- | --- | --- | --- |
| 257 | 25/25 | 25/25 | True | 25/27 | False |
| 277 | 25/25 | 29/25 | False | 28/27 | False |
| 296 | 26/26 | 26/26 | True | 26/29 | False |
| 301 | 27/27 | 27/27 | True | 27/27 | True |
| 321 | 25/26 | 25/26 | False | 26/27 | False |
| 340 | 26/32 | 26/32 | False | 29/32 | False |
| 342 | 27/27 | 27/27 | True | 31/27 | False |
| 343 | 27/289 | 27/289 | False | 27/289 | False |

(Pooled: FT 5/8 agree; R1 4/8 agree (c277 flips to disagree, rest
unchanged); R2 1/8 agree (c301 only).)

Plateau table: c257's 29x4 + c340's twins under first-tie vs
run-center (peak rows + thirds + TRI-p impact — M51's p values
cited, not refit; citation check 16/16 match):

| col | frame | FT peak/third | R1 peak/third | R2 peak/third | p cited | R1 p-impact? | R2 p-impact? |
| ---: | --- | --- | --- | --- | ---: | --- | --- |
| 257 | s0 | 25/top | 25/top | 25/top | 25 | False | False |
| 257 | m15 | 25/top | 25/top | 27/mid | 25 | False | True |
| 340 | s0 | 26/top | 26/top | 29/mid | 26 | False | True |
| 340 | m15 | 32/bottom | 32/bottom | 32/bottom | 32 | False | False |

(Full 16-line p-impact: R1 p-impact True on 1/16 — s0 c277 only;
R2 p-impact True on 8/16 — every multi-tie column-frame. Cited p
equals R1 on 15/16.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 S1/S2 (singleton) | first-tie + alltie + shape + census + R1 + R2 + thirds exact | exact | True |
| C-P1 R1/R2 (run) | first-tie + alltie + shape + census + R1 (mid-flip on R1) + R2 + thirds exact | exact | True |
| C-P1 T1/T2 (scattered/multirun) | first-tie + alltie + shape + census + R1 + R2 (absent-row T1) + thirds exact | exact | True |

(Pooled pass=True. Full per-pseudo-column tables in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: profiles + humps + xshape + ties +
shapes + census both frames) pass1 `9793fcc2…ef45` vs pass2
`9793fcc2…ef45`, identical=True; cell counts identical=True; tail
counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; M26 TRI exact hits reproduced by
citation scope — 0 new explained, attribution not explanation):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | TRI exact hits (M26) | 2475 | 18 | 0.0073 |
| m15 | TRI exact hits (M26) | 2539 | 16 | 0.0063 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_MULTITIE | ≥4/16 column-frames carry >1 max-tie row | 8/16 — met |
| H2_RUNMOVE | under R1, ≥1/16 peak rows differ from first-tie | 1/16 (s0 c277) — met |
| H3_TOPTHIRD | under R1, top-third share ≥ 0.50 on s0 AND m15 | 5/8 + 5/8 — met |
| H4_AGREE | under R1, peak-row agreement ≥ 4/8 | 4/8 — met |
| H5_SINGLERUN | among T>1 column-frames, single-run share ≥ 0.50 | 2/8 = 0.25 — not met |
| H6_SUBMAX4 | submax census recovers an equal-δ run of length ≥4 on s0 c257 | 26-29:29x4 — met |
| H7_TRIP | cited M51 TRI p equals R1 peak on ≥14/16 column-frames | 15/16 — met |
| N | tie + rule tables + standing remainder | 18/16 explained (M26, 0 new); 47/52 named-col stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (64/64 M25 lines + 16/16 M26 hump lines + 9/9 xshape
lines byte-exact), by tie count (8/16 multi-tie with T=2–4), by
tie shape (2/8 single-run vs 3/8 scattered vs 3/8 multirun among
T>1), and by census (plateau runs read only on c257/c277/c321 both
frames; c296/301/340/342/343 read none). Task 2 discriminates by
rule (R1 moves 1/16 peaks vs R2 moves 8/16), by thirds (R1 5/8 +
5/8 top vs R2 3/8 + 1/8 top with 5/8 mid both frames), by agreement
(FT 5/8 vs R1 4/8 vs R2 1/8), and by p-impact (R1 moves cited p on
1/16 vs R2 on 8/16).

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
| interior far tail, TRI-hit | 18 of cell 7 (0.7%) | δ=TRI pred exact, named-col scope (M26, cited) |
| interior far tail, standing | 84 of cell 7 (3.4%) | 47 named-col + 37 outside-named; stands (this run) |
| standing interior remainder | 2457 of cell 7 (99.3%) | 2475 − 18 TRI hits |
| standing remainder (total) | 22797 (99.9% of R_0) | 18 B tail-explained; rest split above |

Screenshot: present by rule. The evidence plateau map
(`m53-plateaumap.png`, 88598 B of 5242880 budget) colors s0
named-column sites by tie status (max-tie run-member 5 /
singleton-or-scattered max-tie 9 / other 51); DESIGN.md admits an
evidence copy iff some s0 named column with n≥8 reads R1 peak row
!= first-tie peak row — c277 (n=10, 25→29) qualifies.

Recorded without verdict: the 16 first-tie peak rows read
M26-exact with thirds 6/8 + 5/8 top and agreement 5/8; max-ties
read 8/16 multi-tie (T=2–4) with shapes 8 singleton / 2 run / 3
scattered / 3 multirun and submax runs only on c257/c277/c321
including the named 29x4; R1 moves 1/16 peaks (s0 c277) with
thirds 5/8 + 5/8 top and agreement 4/8, R2 moves 8/16 with thirds
3/8 + 1/8 top and agreement 1/8; cited TRI p equals R1 on 15/16;
47/52 named-column bytes stand after TRI with 0 new bytes
explained (attribution, not explanation).

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| plateau suite + run-center rules + falsification bars, recorded before running | recorded | `DESIGN.md`: all-tie + shapes + census + R1/R2 + p-impact joins, bars H1–H7/N |
| first-tie + tie + rule tables + wall/exit/shas/determinism | measured | §Step 2: 16/16 humps + 16 ties + shapes + census + R1/R2 + agreement + p-impact; 0.4 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 new explained, 47/52 stands; gaps below |
| screenshot if a plateau map discriminates (or absence reasoned) | measured | present by rule: s0 c277 R1-moved at n=10 (want n≥8); 88598 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m53"
cp local/research/M53/m53.py local/research/M53/control.py local/research/M53/DESIGN.md "/Volumes/Extreme SSD/m53/"
python3 m53.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m25/m25.txt" "/Volumes/Extreme SSD/m26/m26.txt" "/Volumes/Extreme SSD/m53" /Users/bradrichardson/dev/ssx3/local/research/M53 > m53.txt 2>&1
python3 control.py > control.txt 2>&1
cp "/Volumes/Extreme SSD/m53/m53-plateaumap.png" local/research/M53/m53-plateaumap.png
```

## Paths

Evidence (committed): `local/research/M53/` — `DESIGN.md`
(suite + rule pins + bars, recorded before running),
`m53.py` (profiles + ties + rules + PNG writer),
`control.py` (known-plateau synthetic control),
`m53-plateaumap.png` (plateau map, 88598 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m53/` —
`m53.txt` (receipt: shas, baselines, Task-1 profiles both
frames, M25/M26 match, ties + shapes + census, R1/R2 +
thirds + agreement, pcheck + p-impact, re-run, PNG size),
`control.txt`, `m53.py`, `control.py`, `DESIGN.md` (working
copies), `m53-plateaumap.png` (working copy, 88598 B). No
writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`,
`m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`,
`m28/`, `m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`,
`m35/`, `m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`,
`m42/`, `m43/`, `m44/`, `m45/`, `m46/`, `m47/`, `m48/`,
`m49/`, `m50/`, `m51/`, `m52/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. R2 mean-of-ties collapse (new): R2 top-third reads 3/8 + 1/8
   with agreement 1/8 (c301 only) vs R1 5/8 + 5/8 and 4/8 —
   mean-of-ties destroys positional structure while run-center
   preserves it. Needs its own brief only if convention choice
   matters: per-column mean-vs-run peak tables on further
   frames, offline — no new harness code.
2. s0 c277 longest-run flip (new, minor): the only R1 move
   (25→29 via the 28×3 run beating the r25 singleton) and the
   only R1 p-impact — single-column convention sensitivity.
   Needs its own brief only if flip isolation matters: per-row
   prediction tables around c277's competing maxima, offline —
   no new harness code.
3. Low-drift no-keep split (M51 gap 1, still open): c296/c301
   read L1 2/4 but pooled kept 0/0, while c257/c340 (L1 15/10)
   keep 2 each. Needs its own brief only if drift-vs-survival
   matters: per-site kept-hit residual tables, offline — no new
   harness code.
4. Height-vs-edge leg attribution (M51 gap 2, still open):
   |Δh|≥5 reads 3/8 while |Δe|≥3 reads 6/8. Needs its own brief
   only if leg attribution matters: per-leg ablation tables,
   offline — no new harness code.
5. c340 peak-shift survival (M51 gap 3, still open, minor): c340
   Δp=+6 (26→32) keeps pooled 2. Needs its own brief only if
   peak-shift survival matters: per-row prediction tables around
   shifted peaks, offline — no new harness code.
6. Peak-row agreement without value agreement (M51 gap 4 / M26
   gap 2, still open): 5/8 columns share peak rows cross-frame
   but only 6/65 shared-site δ values agree (M25 H5). Needs its
   own brief only if peak anchoring matters: peak-anchored
   residual tables, offline — no new harness code.
7. QUAD underfit (M51 gap 6 / M26 gap 4, still open, minor):
   smooth quadratic reads 4/65 + 3/68 with 32/23 mass in the 2–3
   miss bin. Needs its own brief only if curvature matters:
   per-column quadratic-residual tables, offline — no new
   harness code.
8. CONST cross-frame collapse (M51 gap 7 / M26 gap 5 / M25 gap 2,
   still open): s0 column medians score 0/68 on m15 (1/65 the
   other way) vs 12/13 same-frame. Needs its own brief only if
   column-value mapping matters: per-column median drift tables
   s0 vs m15, offline — no new harness code.
9. m15 c343 row-289 site (M51 gap 8 / M26 gap 6 / M25 gap 3,
   still open): one tail site 262 rows below its column's band
   (hole span 28–288), also m15 c343's argmax peak. Needs its own
   brief only if outlier isolation matters: far-row tail-site
   census, offline — no new harness code.
10. SIGN-corrected near-hit mass (M51 gap 9 / M26 gap 7 / M24 gap
    1, still open): 35 s0 / 38 m15 tail bytes read |err|=1 after
    the best M24 correction vs 21/28 exact. Needs its own brief
    only if second-order structure matters: residual-sign tables
    around K45++SIGN, offline — no new harness code.
11. Streak-column residual coherence (M51 gap 10 / M26 gap 8 / M24
    gap 2, still open): s0 c257 reads r∈{−3,−2,0} only, c296
    reads all |r|≤1, c342 reads all r≥1 (M26/M51/M53 worked
    δ-level, not r-level). Needs its own brief only if
    column-local correction matters: per-column r-profile tables
    + column-constant fits, offline — no new harness code.
12. Gap-bin 32–63 ±1 concentration (M51 gap 11 / M26 gap 9 / M24
    gap 3, still open): 16/32 s0 + 31/49 m15 |r|=1 sites sit in
    gap bin 32–63. Needs its own brief only if gap-local
    rounding matters: per-gap-value r tables within 32–63,
    offline — no new harness code.
13. POS cross-frame collapse (M51 gap 12 / M26 gap 10 / M23 gap 3,
    still open): POS cell medians read 7/16 same-frame but 1/2
    cross-frame. Needs its own brief only if position-value
    mapping matters: per-cell median drift tables s0 vs m15,
    offline — no new harness code.
14. Shape-733 tail divergence (M51 gap 13 / M26 gap 11 / M23 gap
    4, still open): shape 733's tail map reads Jaccard 0.6694 vs
    s0 (100 B) while 727/764 shapes read byte-identical. Needs
    its own brief: per-byte attribution of 733's private sites,
    offline — no new harness code.
15. m15 private tail sites (M51 gap 14 / M26 gap 12 / M23 gap 5,
    still open): 64/134 m15 tail sites never recur on any M16
    shape (occ 0; Jaccard 0.4132). Needs its own brief only if
    cross-sample tail identity matters: second-sample tail
    family, offline — no new harness code.
16. Shape-700 map divergence (M51 gap 15 / M26 gap 13 / M21 gap 1,
    still open): shape 700's static map reads Jaccard 0.0747 vs
    s0 while 518/764 read byte-identical. Needs its own brief:
    per-byte attribution of 700's private sites, offline — no
    new harness code.
17. m15 static-map disjointness (M51 gap 16 / M26 gap 14 / M21 gap
    2, still open): m15 shares 92/1476 static sites with s0
    (Jaccard 0.0245). Needs its own brief only if cross-sample
    map identity matters, offline — no new harness code.
18. U/V co-residual mechanism (M51 gap 17 / M26 gap 15 / M21 gap
    3, still open): same-pixel U&V co-residual reads 16.0×/21.6×
    independence. Needs its own brief only if chroma pairing
    matters, offline — no new harness code.
19. δ-sign mechanism (M51 gap 18 / M26 gap 16 / M20 gap 2, still
    open, minor): δ>0 on 80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90
    vs P(δ>0|v0<full) ≈ 0.70 on both frames. Needs its own brief
    only if the sign asymmetry matters, offline — no new harness
    code.
20. m15 below-min far tail (M51 gap 19 / M26 gap 17 / M19 gap 3,
    still open, minor): 4 below-side bytes with dout ≥ 16 (max
    47) on m15. Needs its own brief only if outlier isolation
    matters, offline — no new harness code.
21. Negative-share mechanism (M51 gap 20 / M26 gap 18 / M18 gap 2,
    still open): 93 negatives (worst −244) unattributed at byte
    level. Needs its own brief: per-shape added-residual maps +
    EFB-copy diffing, offline — no new harness code.
22. Odin port readiness (M51 gap 21 / M26 gap 19 / M18 gap 3,
    still open): no Odin contract in-repo; handoff artifact stays
    `loo.txt` + dumps + synths. Needs its own brief once the
    consumer names its interface.
23. Top-HUD glyph residual isolation (M51 gap 22 / M26 gap 20 /
    M18 gap 4, still open): bottom-HUD draws identified; top-band
    glyph edges in the long tail. Needs its own brief if
    draw-level top-HUD isolation matters.
24. Per-carrier weight centers (M26 gap 21 / M18 gap 5, still
    open, optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers matter.

## What I could not do

1. No cross-shape check: the brief asks cross-frame only
   (s0 vs m15), so shapes 1/2/733 are unscored — tabled scope,
   not chased.
2. No near-hit merging: no fits scored here (attribution run —
   TRI 18/16 cited from M26/M51, 0 new bytes).
3. No refits: M51 TRI p cited, never refit, per the brief.
4. c341 unscored: 0 s0 / 1 m15 sites — membership-guarded
   but outside the brief's 8 peak columns.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M53/`: `DESIGN.md`, `m53.py`,
`control.py`, `m53-plateaumap.png` (88598 B), `REPORT.md` (this
file).
