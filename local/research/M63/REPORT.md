# M63 — interval-head bulk pair: row-323/324 neighborhood bulk census across neighboring columns: REPORT

M62 gap 1 worked at table level: the head bulk reproduces
value-exactly (m15 c311 323:+3/d0 + 324:+1/d0 bulk, band 2
both; c312 noncell dec3 both rows; 48/48 interval probes
match `m62.txt`), the row slices read m15 r323 bulk on
310/311/315 (−3/+3/−1) + r324 bulk on 311 alone (+1) with 0
tail on all 132 neighborhood probes, s0 reads 1 bulk (c76
r323 +1/d9) + 131 noncell, neighbor δ reads all-neg on m15
(−3/−1) against c311 all-pos (+3/+1), and dec-0 echoes on 6
non-311 union cols with 0 bulk there. Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M63.md`. Tables,
no verdicts.

Headers read first: `local/research/M62/REPORT.md` (all of
it: flanks 322:+10/d0 + 335:+46/d3 / 319:+9/d1 + 341:+14/d1;
interval 323–334 m15 c311 2 bulk (323:+3/d0, 324:+1/d0) + 10
noncell vs m15 c312 12 noncell vs s0 12+12 noncell; decspans
3/3; hole join 0.1667 vs 0.0038; M62 gap 1 = this brief)
plus `local/research/M61/REPORT.md` (all of it: the pair
c311 6/0 sum +129 / c312 13/10 sum +130, spans nested
19-in-63, site-29, decpair d0 2-vs-8 / d1 1-vs-6 / d3 2-vs-6
/ d5 1-vs-1, runs 1×6 vs 7/10/6, seats) plus
`local/research/M59/REPORT.md` (all of it: column signs 16
all-pos + 10 all-neg + c312 split 13/10 + 6 s0-only;
dec-1 cols 307/309/310/311/312/313/315).

Time box 4 hours (start 2026-09-20 15:11 EDT); used about
0.5. No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no
writes into `m15/`, `m16/`, `m17/`–`m62/` — all outputs went
to the new `/Volumes/Extreme SSD/m63/`): the 764 M16
per-shape triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`,
the M15 triplet (`m15-v0/mid/full.bin`, second sample), the
top-10 carrier triplets (30 bins), and `m62.txt`
(pair + interval tables to reproduce). Work dir
`/Volumes/Extreme SSD/m63/`; evidence `local/research/M63/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17–M62; `m62.txt` 18766 B):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…9dc8ca7a` |
| m16-mid-s0000 | `9db73827…405c83013` |
| m16-full-s0000 | `6c7c4b1b…d2edfcef` |
| m15-v0 | `879c74ec…2d102458` |
| m15-mid | `10e2514a…c2e20284` |
| m15-full | `b4053af3…e2c2426a` |
| m62.txt | `e971e4af…6918591d` |

(Full hexes in `m63.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the
dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M62
exactly. `loo.txt` parses to 764 rows; top-10 shapes +
shares match M16. R_s vs `loo.txt` reads 22815 on s0,
equal. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m63.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try on the
staged copy). DESIGN.md was recorded before running and is
unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m63.py receipt | 0.2 s | exit 0; all guards pass; canon `dfc5ae8a…ea4eaca8` |
| control.py C-NEIGHBOR (known row bulk) | <1 s | green; census + both row slices exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Census recompute + M62 guard | 2 | in-pass |
| Task 1 (head pair + row slices + recheck) | 2 | in-pass |
| Task 2 (bulk-neighbor + delta + deciles) | 2 | in-pass |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m63.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — pair reproduction (does the head bulk reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail
with sub-bins 28+74 / 50+84 and max 47/48, all 18
per-column guard rows (n/minrow/maxrow/sum) matching
M22/M23/M25/M26/M56 EXACTLY. Named-column bytes read 65 s0 /
68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V). s0 P1 edges + all 10 carrier removed counts+bands
match M18/M19 exactly.

Pair margins: c311 6/0 +129 all-pos vs c312 13/10 +130
split (both match `m62.txt` AND the design pins):

| col | s0_n | m15_n | pos | neg | pos share | min | max | sum | class |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 311 | 4 | 6 | 6 | 0 | 1.0000 | +9 | +46 | +129 | all-pos |
| 312 | 3 | 23 | 13 | 10 | 0.5652 | −9 | +33 | +130 | split |

(Runs read 1×6 vs 7/10/6; spans + gaps + decile hists +
d-hists match `m62.txt` AND the design pins. Site sets
match the design pins; `m62.txt` carries no per-site lines,
disclosed. 48-probe recheck reads 48/48 vs `m62.txt`.)

Head-pair table: rows 323–324 on c311 + c312, m15, with
full value rows (d = nearest-m15-tail-row distance on the
same column, lo/hi bracketing tail rows — probe-d
convention, disclosed; all 4 match the design pins):

| col | row | kind | δ | dec | band | d | lo | hi |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 311 | 323 | bulk | +3 | 0 | 2 | 1 | 322 | 335 |
| 311 | 324 | bulk | +1 | 0 | 2 | 2 | 322 | 335 |
| 312 | 323 | noncell | None | 3 | 2 | 4 | 319 | 341 |
| 312 | 324 | noncell | None | 3 | 2 | 5 | 319 | 341 |

Row-323 table: row 323 across ALL 33 union cols, m15
(kind + δ + decile per column; band 2 all 33):

| col | kind | δ | dec |
| ---: | --- | ---: | ---: |
| 38 | noncell | None | 0 |
| 65 | noncell | None | 9 |
| 76 | noncell | None | 9 |
| 257 | noncell | None | 3 |
| 277 | noncell | None | 3 |
| 289 | noncell | None | 1 |
| 292 | noncell | None | 0 |
| 293 | noncell | None | 3 |
| 296 | noncell | None | 3 |
| 298 | noncell | None | 3 |
| 299 | noncell | None | 0 |
| 301 | noncell | None | 1 |
| 306 | noncell | None | 3 |
| 307 | noncell | None | 3 |
| 308 | noncell | None | 3 |
| 309 | noncell | None | 1 |
| 310 | bulk | −3 | 3 |
| 311 | bulk | +3 | 0 |
| 312 | noncell | None | 3 |
| 313 | noncell | None | 3 |
| 314 | noncell | None | 4 |
| 315 | bulk | −1 | 1 |
| 316 | noncell | None | 1 |
| 321 | noncell | None | 1 |
| 332 | noncell | None | 1 |
| 340 | noncell | None | 3 |
| 341 | noncell | None | 0 |
| 342 | noncell | None | 3 |
| 343 | noncell | None | 1 |
| 344 | noncell | None | 4 |
| 353 | noncell | None | 4 |
| 372 | noncell | None | 5 |
| 617 | noncell | None | 0 |

(3 bulk / 30 noncell / 0 tail. Bulk cols [310, 311, 315].)

Row-324 table: row 324 across ALL 33 union cols, m15
(same columns; band 2 all 33):

| col | kind | δ | dec |
| ---: | --- | ---: | ---: |
| 38 | noncell | None | 0 |
| 65 | noncell | None | 9 |
| 76 | noncell | None | 8 |
| 257 | noncell | None | 4 |
| 277 | noncell | None | 1 |
| 289 | noncell | None | 4 |
| 292 | noncell | None | 3 |
| 293 | noncell | None | 1 |
| 296 | noncell | None | 3 |
| 298 | noncell | None | 3 |
| 299 | noncell | None | 1 |
| 301 | noncell | None | 3 |
| 306 | noncell | None | 3 |
| 307 | noncell | None | 3 |
| 308 | noncell | None | 3 |
| 309 | noncell | None | 3 |
| 310 | noncell | None | 3 |
| 311 | bulk | +1 | 0 |
| 312 | noncell | None | 3 |
| 313 | noncell | None | 1 |
| 314 | noncell | None | 1 |
| 315 | noncell | None | 3 |
| 316 | noncell | None | 3 |
| 321 | noncell | None | 0 |
| 332 | noncell | None | 3 |
| 340 | noncell | None | 3 |
| 341 | noncell | None | 3 |
| 342 | noncell | None | 1 |
| 343 | noncell | None | 3 |
| 344 | noncell | None | 3 |
| 353 | noncell | None | 3 |
| 372 | noncell | None | 4 |
| 617 | noncell | None | 0 |

(1 bulk / 32 noncell / 0 tail. Bulk cols [311].)

(s0 auxiliary: r323 reads 1 bulk (c76 +1/d9) + 32 noncell;
r324 reads 33 noncell; all band 2. s0 per-column deciles
are identical to the m15 rows above — deciles are
s0-anchored, one shared plane — receipt-verified
(`neighdec` diff empty), not re-printed. All 132 probes
carry δ iff incell: 5 bulk with δ, 127 noncell with None,
0 tail.)

### Task 2 — neighborhood census (is the pair column-local?)

Bulk-neighbor table: bulk counts at rows 323–324 per
neighbor column, m15 (named 310/311/312/313/314/315 + the
only union hits, which are all named — the other 27 union
cols read 0/2/0 each):

| col | bulk | noncell | tail | bulk rows |
| ---: | ---: | ---: | ---: | --- |
| 310 | 1 | 1 | 0 | 323:−3/dec3 |
| 311 | 2 | 0 | 0 | 323:+3/dec0 324:+1/dec0 |
| 312 | 0 | 2 | 0 | NONE |
| 313 | 0 | 2 | 0 | NONE |
| 314 | 0 | 2 | 0 | NONE |
| 315 | 1 | 1 | 0 | 323:−1/dec1 |

(s0 auxiliary: c76 reads 1/1/0 (323:+1/dec9); the other 32
union cols read 0/2/0 each. 0 tail on all 66 per-column
censuses either frame.)

δ table: δ values of every bulk/tail probe at 323–324
(no tail anywhere — bulk δ only):

| frame | col | row | kind | δ | sign |
| --- | ---: | ---: | --- | ---: | --- |
| m15 | 310 | 323 | bulk | −3 | neg |
| m15 | 311 | 323 | bulk | +3 | pos |
| m15 | 311 | 324 | bulk | +1 | pos |
| m15 | 315 | 323 | bulk | −1 | neg |
| s0 | 76 | 323 | bulk | +1 | pos |

(m15 neighbor bulk reads all-neg (310/315: −3/−1) while
c311 reads all-pos (+3/+1); |δ| reads 3/1 on the neighbors
vs 3/1 on c311. The +3/+1 magnitudes echo on c310 (−3) and
c315 (−1) with flipped signs. s0's lone bulk reads +1.)

Decile table: deciles at 323–324 per named neighbor column
(m15 rows; s0 rows identical — one shared s0-anchored
plane):

| row | c310 | c311 | c312 | c313 | c314 | c315 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 323 | 3 | 0 | 3 | 3 | 4 | 1 |
| 324 | 3 | 0 | 3 | 1 | 1 | 3 |

(Dec-0 echoes beyond c311: cols reading dec-0 at 323 or
324 are 38 (both rows), 292 (323), 299 (323), 311 (both),
321 (324), 341 (323), 617 (both) — 7 cols, bulk on c311
only. Full-33 decspans: 12 cols read decspan 1
(38/65/296/298/306/307/308/310/311/312/340/617), 21 cols
read decspan 2; no col spans wider over the 2 rows.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-NEIGHBOR cen c0 (rows 5–6) | bulk [(5,+3,d0),(6,+1,d0)] noncell [] tail [] counts 2/0/0 dec [0,0] span 1 hist {0:2} | exact | True |
| C-NEIGHBOR cen c1 (rows 5–6) | bulk [] noncell [5,6] tail [] counts 0/2/0 dec [3,3] span 1 hist {3:2} | exact | True |
| C-NEIGHBOR cen c2 (rows 5–6) | bulk [] noncell [6] tail [(5,+9,d1)] counts 0/1/1 dec [1,0] span 2 hist {0:1,1:1} | exact | True |
| C-NEIGHBOR slice r5 | c0 bulk/+3/d0, c1 noncell/None/d3, c2 tail/+9/d1 | exact | True |
| C-NEIGHBOR slice r6 | c0 bulk/+1/d0, c1 noncell/None/d3, c2 noncell/None/d0 | exact | True |

(7 `match=True` lines + `pass=True`, exit 0. Full rows in
`control.txt`. The known 2-bulk/0-noncell/0-tail +
0-bulk/2-noncell + 1-tail synthetic neighborhood with known
δ/deciles recovers exactly, incl. both row slices.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: margins + head pair + runs +
setguards + spans + gaps + 48-probe recheck + 132
neighborhood probes + censuses + slices, fresh loads)
pass1 `dfc5ae8a…ea4eaca8` vs pass2 `dfc5ae8a…ea4eaca8`,
identical=True; 269/269 lines match=True; cell counts
identical=True; tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not
explanation — no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes
tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_HEADMATCH | c311 6 + c312 23 match M62 value-exactly; 323:+3/d0 + 324:+1/d0 bulk on c311, noncell dec3 on c312 | sets + margins + spans + gaps + 4/4 head rows exact — met |
| H2_PROBE48 | all 48 M62 interval probes match `m62.txt` value-exactly | 48/48 (kind,delta,dec,band) — met |
| H3_SLICES66 | rows 323 + 324 probed across all 33 union cols m15 + s0 aux; δ iff incell | 132/132 probes, 5 with δ — met |
| H4_BAND2GEOM | all 132 neighborhood probes read band 2 | 132/132 — met |
| H5_BULKNEIGHBOR | bulk counts at 323–324 per neighbor column tabled | m15 [310,311,315]; s0 [76] — met |
| H6_DELTAGRAD | δ of every neighbor bulk/tail probe at 323–324 tabled | m15 −3/+3/+1/−1; s0 +1 — met |
| H7_DECGRAD | deciles at 323–324 per neighbor column tabled | named gradients + dec-0 echo on 7 cols — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates
by reproduction (both (row,δ,dec) sets + margins + spans +
runs + gaps match M62/design value-exactly on every guard;
48/48 recheck; 4/4 head rows) and by slice content (m15
r323 3 bulk vs r324 1 bulk; s0 1 bulk vs 0 bulk). Task 2
discriminates by bulk-neighbor (c311 2 vs 310/315 1 each vs
0 on the other 30 m15 cols; s0 c76 alone) and by δ sign
(m15 neighbors all-neg vs c311 all-pos, magnitudes 3/1
echoed flipped) and by decile gradient (named r323
3/0/3/3/4/1 vs r324 3/0/3/1/1/3; dec-0 on 7 cols with bulk
on 1), and not by band (132/132 band 2) nor by tail
presence (0/132 probes, 0/66 censuses) nor by
frame-anchored deciles (s0 rows identical to m15).

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
| interior far tail | 102 of cell 7 (4.1%) | |δ|≥8, max 47; 100% Y; stands (this run) |
| standing interior remainder | 2475 of cell 7 (100%) | no rule; census tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence neighborhood map
(`m63-neighbormap.png`, 511 B of 5242880 budget) colors m15
tail-Y by pair class (yellow c311 6 / green c312-pos 13 /
red c312-neg 10 / gray other tail 105) with the row-323/324
overlay on all 33 union cols (cyan bulk / magenta tail /
dark-blue noncell); DESIGN.md admits an evidence copy iff
any non-311 union column reads bulk OR tail at rows 323–324
on m15 (neighbor activity — the pre-registered neighbor
split) — active reads [310, 315], met.

Recorded without verdict: the head pair reads 323:+3/d0 +
324:+1/d0 bulk on c311 (probe-d 1/2, lo322/hi335) vs
noncell dec3 on c312 (probe-d 4/5, lo319/hi341); row slices
read m15 r323 bulk on 310/311/315 + r324 bulk on 311 alone
with 0 tail on all 132 probes; s0 reads 1 bulk (c76 r323
+1/d9) + 131 noncell; δ reads m15 −3/+3/+1/−1 (neighbors
neg, c311 pos) + s0 +1; deciles read named 3/0/3/3/4/1 vs
3/0/3/1/1/3 with dec-0 echoing on 7 cols (bulk on 1); 0 B
explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| neighborhood suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: head pair + row slices + bulk-neighbor + delta + deciles + C-NEIGHBOR control, bars H1–H7/N |
| pair reproduction + neighborhood census + wall/exit/shas/determinism | measured | §Step 2: 4 head rows + 132 probes + bulk/δ/dec tables + s0 aux; 0.2 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained, 102 stands; gaps below |
| screenshot if a neighborhood map discriminates (or absence reasoned) | measured | present by rule: neighbor split (active [310,315]); 511 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir —
§Runs):

```
mkdir -p "/Volumes/Extreme SSD/m63" local/research/M63
python3 -m py_compile local/research/M63/m63.py local/research/M63/control.py
cp local/research/M63/m63.py local/research/M63/control.py local/research/M63/DESIGN.md "/Volumes/Extreme SSD/m63/"
python3 "/Volumes/Extreme SSD/m63/m63.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m62/m62.txt" "/Volumes/Extreme SSD/m63" /Users/bradrichardson/dev/ssx3/local/research/M63 > "/Volumes/Extreme SSD/m63/m63.txt" 2>&1
python3 "/Volumes/Extreme SSD/m63/control.py" > "/Volumes/Extreme SSD/m63/control.txt" 2>&1
cp "/Volumes/Extreme SSD/m63/m63-neighbormap.png" local/research/M63/m63-neighbormap.png
```

## Paths

Evidence (committed): `local/research/M63/` — `DESIGN.md`
(suite + neighborhood pins + bars, recorded before running),
`m63.py` (head pair + row slices + recheck + bulk-neighbor +
delta + deciles + PNG writer), `control.py`
(known-neighborhood synthetic control),
`m63-neighbormap.png` (neighborhood map, 511 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m63/`
— `m63.txt` (receipt: shas, baselines, guards, census +
M62 guard, head pair + slices + recheck, bulk-neighbor +
delta + deciles, bars, re-run, PNG size — 41284 B),
`control.txt` (1385 B), `m63.py`, `control.py`,
`DESIGN.md` (working copies), `m63-neighbormap.png`
(working copy, 511 B). No writes into `m15/`, `m16/`,
`m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`, `m23/`,
`m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`, `m30/`,
`m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`,
`m38/`, `m39/`, `m40/`, `m41/`, `m42/`, `m43/`, `m44/`,
`m45/`, `m46/`, `m47/`, `m48/`, `m49/`, `m50/`, `m51/`,
`m52/`, `m53/`, `m54/`, `m55/`, `m56/`, `m57/`, `m58/`,
`m59/`, `m60/`, `m61/`, `m62/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Neighbor bulk at row 323 (new): m15 r323 reads bulk on
   c310 (−3/d3) + c315 (−1/d1) alongside c311 (+3/d0) —
   same row, neighbor δ negative while c311 positive,
   magnitudes 3/1 echoed flipped. Needs its own brief only
   if neighbor bulk matters: row-323 bulk-sign census
   across a wider column range with δ magnitudes, offline
   — no new harness code.
2. Row-324 c311-alone drop (new): r324 reads bulk on c311
   alone while r323 reads bulk on 3 cols — the neighbor
   bulk vanishes one row down. Needs its own brief only if
   the row-drop matters: row-324 vs row-323 bulk census
   across the full Y width, offline — no new harness code.
3. s0 c76 lone bulk (new): s0's only neighborhood bulk sits
   on c76 (r323 +1/d9) while m15 reads noncell there (dec
   9) — a frame-asymmetric single. Needs its own brief
   only if frame asymmetry matters: per-frame bulk census
   at rows 323–324 over all 640 Y cols, offline — no new
   harness code.
4. Dec-0 echo without bulk (new): 6 non-311 union cols
   (38/292/299/321/341/617) read dec-0 at 323/324 with 0
   bulk — dec-0 does not imply bulk. Needs its own brief
   only if decile-vs-bulk matters: dec-0 row census joined
   with bulk status across union cols, offline — no new
   harness code.
5. Interval column asymmetry (M62 gap 2, still open): m15
   interval bulk reads 2-vs-0 across c311/c312 while s0
   reads 0-vs-0. Needs its own brief only if asymmetry
   matters: per-frame bulk census over the pair's full row
   ranges, offline — no new harness code.
6. Interval decile drift (M62 gap 3, still open): c311
   deciles drift d0:5/d3:6/d4:1 vs c312 d0:4/d1:1/d3:7 —
   decspan 3 both, neither flat. Needs its own brief only
   if drift matters: decile-gradient tables across the gap
   on both columns with flank deciles joined, offline — no
   new harness code.
7. Hole-density contrast (M62 gap 4, still open): gap-13
   m15-c311 bulkshare 0.1667 (2/12) vs c343-hole m15 0.0038
   (1/261) at 0 tail both. Needs its own brief only if
   density matters: bulk-density census across all pair
   column gaps, offline — no new harness code.
8. Counterpart bulk pair (M62 gap 5 = M61 gap 2, still
   open): the only bulk counterparts — (341,311) +1 and
   (320,312) +2 — both |δ|≤2, both dec 3. Needs its own
   brief only if counterpart bulk matters: bulk-at-tail-rows
   census over the pair's 28 distinct rows, offline — no
   new harness code.
9. r316 dec-7 noncell (M62 gap 6 = M61 gap 3, still open):
   (316,311) reads dec 7 yet noncell while (316,312) reads
   dec 7 tail +11. Needs its own brief only if dec-7
   adjacency matters: row-316 Y-band cell census across
   neighboring columns, offline — no new harness code.
10. c312 run-boundary gap (M62 gap 7 = M61 gap 4 = M60 gap
    3, still open): the only non-1 d on c312 (r369 d=2) sits
    at the first site of the third run; c311's d3 sits at
    its min row (r317). Needs its own brief only if
    run-boundary gaps matter: sign-run boundary gap census
    over c312's runs, offline — no new harness code.
11. c343 row-span vs unanimity (M62 gap 8 = M61 gap 5 = M60
    gap 1, still open): c343 is the widest m15 column
    (row-span 264) yet reads unanimous-neg (0/4). Needs its
    own brief only if span-vs-unanimity matters: row-span ×
    unanimity-class census with the far-site row
    included/excluded, offline — no new harness code.
12. c313 all-pos span runner-up (M62 gap 9 = M61 gap 6 =
    M60 gap 4, still open): c313 (all-pos, n=5) reads
    row-span 41, the widest unanimous all-pos column, vs
    c312's 63. Needs its own brief only if all-pos span
    matters: wide all-pos column census (311/313/315) with
    row positions, offline — no new harness code.
13. Null-4 all-positive (M62 gap 10 = M61 gap 7 = M60 gap
    5 = M59 gap 2, still open): pooled null-4 m15 reads
    13/0 while c312 splits 13/10. Needs its own brief only
    if null-column sign matters: null-4 vs c312 sign census
    across frames, offline — no new harness code.
14. Named-9 sign polarity (M62 gap 11 = M61 gap 8 = M60
    gap 6 = M59 gap 3, still open): 6 named streak columns
    read all-pos (59 sites) vs 3 all-neg (10 sites). Needs
    its own brief only if streak-column polarity matters:
    named-column sign census with row positions, offline —
    no new harness code.
15. Dec-9 column disjointness (M62 gap 12 = M61 gap 9 = M60
    gap 7 = M59 gap 4, still open): 0/75 dec-9 sites share
    a column with dec-1 (likewise dec-8 0/5, dec-6 0/1).
    Needs its own brief only if bin-column disjointness
    matters: full bin×column contingency over all 10 bins,
    offline — no new harness code.
16. Column decile-mode vs sign (M62 gap 13 = M61 gap 10 =
    M60 gap 8 = M59 gap 5, still open): decile mode 9 sits
    on 12 m15 columns split 7 pos-mode / 5 neg-mode. Needs
    its own brief only if the joint distribution matters:
    mode-decile × mode-sign contingency with per-column
    margins, offline — no new harness code.
17. Band-1 off-mode trio (M62 gap 14 = M61 gap 11 = M60 gap
    9 = M59 gap 6 = M58 gap 3, still open): 3/51 read band
    1 vs 48 band 2 and 0 band 0. Needs its own brief only
    if the band-1 minority matters: band-1 off-mode vs
    band-1 tail seats, offline — no new harness code.
18. m15 null-column dec-9 avoidance (M62 gap 15 = M61 gap
    12 = M60 gap 10 = M59 gap 7 = M58 gap 4 = M57 gap 2,
    still open): m15 null-column frames read 0 dec-9 while
    their s0 counterparts read 14/17 dec-9. Needs its own
    brief only if column-frame decile splits matter: full
    per-column-frame decile census over all 33 union cols,
    offline — no new harness code.
19. Hole bulk asymmetry (M62 gap 16 = M61 gap 13 = M60 gap
    11 = M59 gap 8 = M58 gap 5 = M57 gap 4, still open):
    m15's 28–288 hole holds 1 bulk vs s0's 8 bulk, 0 tail
    either frame. Needs its own brief only if hole contents
    matter: per-hole-row bulk tables on c343, offline — no
    new harness code.
20. Null max d=16 (M62 gap 17 = M61 gap 14 = M60 gap 12 =
    M59 gap 9 = M58 gap 6 = M57 gap 5, still open): the
    next-nearest non-far reads d=16 (s0 c313 r292). Needs
    its own brief only if the near-far margin matters:
    threshold-sweep census (d≥50/25/10), offline — no new
    harness code.
21. Median-drift no-keep split (M62 gap 18 = M61 gap 15 =
    M60 gap 13 = M59 gap 10 = M58 gap 7 = M57 gap 6, still
    open): |Δ|≤2 columns keep 0 pooled CONST hits while the
    single kept hit sits on c340 (|Δ|=3). Needs its own
    brief only if drift-vs-survival matters: per-site
    cross-frame err tables joined with within-column δ
    spread, offline — no new harness code.
22. Median-below-peak offset (M62 gap 19 = M61 gap 16 = M60
    gap 14 = M59 gap 11 = M57 gap 7, still open): 0/16
    col-frames read median==TRI peak h; med−h reads −1..−25.
    Needs its own brief only if median-peak offset matters:
    median-vs-hump-position tables, offline — no new
    harness code.
23. c340 transfer cluster (M62 gap 20 = M61 gap 17 = M60
    gap 15 = M59 gap 12 = M58 gap 9 = M57 gap 8, still
    open): both fit-s0→m15 nears + the single fit-m15→s0
    hit + 1 of 4 reverse nears all sit on c340. Needs its
    own brief only if column-local transfer matters: c340
    site-level transfer census, offline — no new harness
    code.
24. M62 gap 21 = M61 gap 18 = M60 gap 16 = M59 gap 13 =
    M58 gap 10 = M57 gap 9 = M55 gaps 4–11, 13–27 (still
    open, by reference): see M55 REPORT gaps 4–11, 13–27
    for the exact brief each needs.

(Worked this run, dropped from the open list: M62 gap 1 /
interval-head bulk pair — the neighborhood census above.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 neighborhood status) are
   unscored — tabled scope, not chased.
2. No rows beyond 323–324: only the head-pair rows are
   probed on neighbors (the brief asks rows 323–324, not
   the full 323–334 interval) — narrowed scope, gaps 1–2
   above.
3. No per-site detail beyond the pair + slices in REPORT
   tables: the other 105 m15 tail-Y sites live in prior
   receipts (uncommitted here) — disclosed, not re-printed.
4. Control seat/carrier N/A: the pure-synthetic control
   recovers neighborhood census + row slices exactly;
   band/streak/carrier/peak seats need dumps (status-map
   synthetic carries band/dec as data, disclosed).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M63/`: `DESIGN.md`, `m63.py`,
`control.py`, `m63-neighbormap.png`, `REPORT.md` (this file).
Total PNG 511 B.
