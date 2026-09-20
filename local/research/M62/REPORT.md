# M62 — c311 gap-13 interval: row-interval contents rows 323–334, both columns: REPORT

M61 gap 1 worked at table level: the flanks recompute
value-exactly (c311 322:+10/d0 + 335:+46/d3, c312 319:+9/d1
+ 341:+14/d1, all band-2 d1 with the pinned lo/hi), the
323–334 interval reads 2 bulk + 10 noncell + 0 tail on
m15 c311 (bulk at the head: 323:+3/d0, 324:+1/d0) vs 0
bulk + 12 noncell + 0 tail on m15 c312 and 0 bulk on s0
both columns, deciles drift across the gap (c311
d0:5/d3:6/d4:1, c312 d0:4/d1:1/d3:7, decspan 3 both), and
the hole join reads m15-c311 bulkshare 0.1667 (2/12) vs
c343-hole m15 0.0038 (1/261) with 0 tail on all 8 join
rows and the c343-hole re-itemization matching M56
(counts + |δ| rows, True/True). Fully offline — no lease
of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M62.md`. Tables,
no verdicts.

Headers read first: `local/research/M61/REPORT.md` (all of
it: c311 6/0 sum +129 rows 317–336 gaps 3/1/1/13/1 ndec 4
d0:2/d1:1/d3:2/d5:1 dhist 1:5 3:1; c312 13/10 sum +130 runs
7/10/6 rows 316–379 span 63 ndec 6 d0:8/d1:6/d3:6/d4:1/
d5:1/d7:1 dhist 1:22 2:1; site-29 + decpair + missing +
rowgeom + runs + seats; M61 gap 1 = this brief) plus
`local/research/M60/REPORT.md` (all of it: spans c311 19 /
c312 63 nested; unanimity; decmix; dprof) plus
`local/research/M56/REPORT.md` (all of it: hole machinery
— c343 hole 28–288 ×261: m15 bulk 1 (r30 |δ|=1) / noncell
260 / tail 0; s0 bulk 8 (r132–272 all |δ|=1) / noncell 253
/ tail 0; the shape model).

Time box 4 hours (start 2026-09-20 14:10 EDT); used about
0.3. No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no
writes into `m15/`, `m16/`, `m17/`–`m61/` — all outputs went
to the new `/Volumes/Extreme SSD/m62/`): the 764 M16
per-shape triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`,
the M15 triplet (`m15-v0/mid/full.bin`, second sample), the
top-10 carrier triplets (30 bins), and `m61.txt`
(pair rows to reproduce). Work dir
`/Volumes/Extreme SSD/m62/`; evidence `local/research/M62/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17–M61; `m61.txt` 20214 B):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m61.txt | `287ef182…e1ca89a7` |

(Full hexes in `m62.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the
dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M61
exactly. `loo.txt` parses to 764 rows; top-10 shapes +
shares match M16. R_s vs `loo.txt` reads 22815 on s0,
equal. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m62.py` invocation (the receipt, 0.2 s, exit 0);
one `control.py` invocation (green, first try on the
staged copy; one holerecheck |δ|-convention fix landed
after a first receipt run — the M56 pins table |δ| while
the first recheck compared signed δ, so counts matched
but the flag read False; the receipt below is the re-run
with magnitudes compared — DESIGN.md unaffected).
DESIGN.md was recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m62.py receipt | 0.2 s | exit 0; all guards pass; canon `2eddd16c…0efc93390` |
| control.py C-INTERVAL (known interval contents) | <1 s | green; census + holejoin exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Census recompute + M61 guard | 2 | in-pass |
| Task 1 (flank + interval tables) | 2 | in-pass |
| Task 2 (bulk + deciles + holejoin) | 2 | in-pass |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m62.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — interval reproduction (do the flanking rows reproduce?)

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
split (both match `m61.txt` AND the design pins):

| col | s0_n | m15_n | pos | neg | pos share | min | max | sum | class |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 311 | 4 | 6 | 6 | 0 | 1.0000 | +9 | +46 | +129 | all-pos |
| 312 | 3 | 23 | 13 | 10 | 0.5652 | −9 | +33 | +130 | split |

Flank table: c311 rows 322/335 + c312 rows 319/341 with
full value rows (all 4 match the design pins):

| col | row | δ | sign | dec | band | streak | carrier | 701 | peak | atpeak | d | lo | hi |
| ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| 311 | 322 | +10 | pos | 0 | 2 | other | none | out | 335 | False | 1 | 321 | 335 |
| 311 | 335 | +46 | pos | 3 | 2 | other | none | out | 335 | True | 1 | 322 | 336 |
| 312 | 319 | +9 | pos | 1 | 2 | other | none | out | 373 | False | 1 | 318 | 341 |
| 312 | 341 | +14 | pos | 1 | 2 | other | none | out | 373 | False | 1 | 319 | 342 |

(Gap structure reproduces: c311 gaps [3,1,1,13,1] span 19
with 322→335 = 13 the unique max; c312 gaps
[1,1,1,22,1,1,10,1,1,1,6,1,1,1,1,1,2,4,1,3,1,1] span 63
with 319→341 = 22; rows overlapping 323–334 read NONE on
both columns. Runs read 1×6 vs 7/10/6; spans + decile
hists + d-hists match `m61.txt` AND the design pins.)

Interval table: rows 323–334 on c311, m15 (kind + δ +
decile + band per row, 12 rows):

| row | kind | δ | dec | band |
| ---: | --- | ---: | ---: | ---: |
| 323 | bulk | +3 | 0 | 2 |
| 324 | bulk | +1 | 0 | 2 |
| 325 | noncell | None | 0 | 2 |
| 326 | noncell | None | 3 | 2 |
| 327 | noncell | None | 3 | 2 |
| 328 | noncell | None | 3 | 2 |
| 329 | noncell | None | 3 | 2 |
| 330 | noncell | None | 4 | 2 |
| 331 | noncell | None | 3 | 2 |
| 332 | noncell | None | 0 | 2 |
| 333 | noncell | None | 0 | 2 |
| 334 | noncell | None | 3 | 2 |

Interval table: rows 323–334 on c312, m15 (same 12 rows):

| row | kind | δ | dec | band |
| ---: | --- | ---: | ---: | ---: |
| 323 | noncell | None | 3 | 2 |
| 324 | noncell | None | 3 | 2 |
| 325 | noncell | None | 3 | 2 |
| 326 | noncell | None | 3 | 2 |
| 327 | noncell | None | 3 | 2 |
| 328 | noncell | None | 3 | 2 |
| 329 | noncell | None | 3 | 2 |
| 330 | noncell | None | 0 | 2 |
| 331 | noncell | None | 0 | 2 |
| 332 | noncell | None | 0 | 2 |
| 333 | noncell | None | 1 | 2 |
| 334 | noncell | None | 0 | 2 |

(s0 auxiliary: all 24 s0 probes read noncell + band 2;
s0 per-row deciles are identical to the m15 rows above —
deciles are s0-anchored, one shared plane — tabled in
`m62.txt`, not re-printed. All 48 probes carry δ iff
incell: 2 bulk with δ, 46 noncell with None, 0 tail.)

### Task 2 — interval census (what's inside gap-13?)

Bulk table: bulk sites in 323–334, both columns both
frames (rows + δ + deciles — or NONE tabled):

| frame | col | n | rows |
| --- | ---: | ---: | --- |
| m15 | 311 | 2 | 323:+3/dec0 324:+1/dec0 |
| m15 | 312 | 0 | NONE |
| s0 | 311 | 0 | NONE |
| s0 | 312 | 0 | NONE |

(The only bulk in 48 probes sits at the interval head on
m15 c311: rows 323–324, δ +3/+1, both dec 0 — 1–2 rows
below the 322 flank.)

Decile table: per-row deciles over the interval, both
columns (m15 rows; s0 rows identical — one shared
s0-anchored plane):

| row | c311 dec | c312 dec |
| ---: | ---: | ---: |
| 323 | 0 | 3 |
| 324 | 0 | 3 |
| 325 | 0 | 3 |
| 326 | 3 | 3 |
| 327 | 3 | 3 |
| 328 | 3 | 3 |
| 329 | 3 | 3 |
| 330 | 4 | 0 |
| 331 | 3 | 0 |
| 332 | 0 | 0 |
| 333 | 0 | 1 |
| 334 | 3 | 0 |

(Decile drift tabled: c311 reads d0×3 → d3×4 → d4×1 →
d3×1 → d0×2 → d3×1 (hist d0:5/d3:6/d4:1, decspan 3);
c312 reads d3×7 → d0×3 → d1×1 → d0×1 (hist
d0:4/d1:1/d3:7, decspan 3). Neither column holds one
decile across the gap.)

Hole-join table: gap-13 counts vs M56's c343 hole (28–288:
bulk 1/8, 0 tail — counts tabled, no verdict):

| label | bulk | noncell | tail | n | bulkshare | tailshare |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m15-c311 | 2 | 10 | 0 | 12 | 0.1667 | 0.0000 |
| m15-c312 | 0 | 12 | 0 | 12 | 0.0000 | 0.0000 |
| m15-pooled | 2 | 22 | 0 | 24 | 0.0833 | 0.0000 |
| s0-c311 | 0 | 12 | 0 | 12 | 0.0000 | 0.0000 |
| s0-c312 | 0 | 12 | 0 | 12 | 0.0000 | 0.0000 |
| s0-pooled | 0 | 24 | 0 | 24 | 0.0000 | 0.0000 |
| c343hole-m15 | 1 | 260 | 0 | 261 | 0.0038 | 0.0000 |
| c343hole-s0 | 8 | 253 | 0 | 261 | 0.0307 | 0.0000 |

(c343-hole re-itemization from the dumps, table-only:
m15 1/260/0 bulkrows [30:−1], s0 8/253/0 bulkrows
[132:+1 140:+1 186:+1 233:+1 235:−1 236:−1 242:+1
272:+1] — counts + |δ| row sets match M56, True/True.
All 8 join rows read 0 tail.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-INTERVAL cen c0 (rows 3–6) | bulk [(3,+2,d3),(6,−1,d3)] noncell [4] tail [(5,+9,d1)] counts 2/1/1 dec [3,0,1,3] span 3 hist {0:1,1:1,3:2} | exact | True |
| C-INTERVAL cen c1 (rows 3–6) | bulk [(4,+1,d1)] noncell [3,5,6] tail [] counts 1/3/0 dec [5,1,0,7] span 4 hist {0:1,1:1,5:1,7:1} | exact | True |
| C-INTERVAL join gap/ref | gap 2/1/1 bulkshare 0.5000 tailshare 0.2500; ref 1/2/1 bulkshare 0.2500 tailshare 0.2500 | exact | True |

(6 `match=True` lines + `pass=True`, exit 0. Full rows in
`control.txt`. The known 2-bulk/1-noncell/1-tail +
1-bulk/3-noncell synthetic interval with known δ/deciles
recovers exactly, incl. per-row probes, decspans, and the
join shares.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: margins + flanks + sets +
spans + gaps + 48 interval probes + census, fresh loads)
pass1 `2eddd16c…0efc93390` vs pass2 `2eddd16c…0efc93390`,
identical=True; 70/70 lines match=True; cell counts
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
| H1_FLANKMATCH | c311 6 + c312 23 match M61 value-exactly (sets + sums +129/+130 + runs 7/10/6 + spans/gaps/hists) | sets + margins + spans + runs + gaps all exact — met |
| H2_GAP13 | c311 gaps [3,1,1,13,1] max 13; c312 319→341 = 22; rows in 323–334 NONE both cols | [3,1,1,13,1]/22; []/[] — met |
| H3_FLANKSEAT | flanks +10/d0, +46/d3, +9/d1, +14/d1, all band-2 d1 + pinned lo/hi | 4/4 exact — met |
| H4_INTERVAL12 | 12/12 rows × 2 cols probed m15 + s0 aux; δ iff incell | 48/48 probes, 2 with δ — met |
| H5_BAND2GEOM | all 48 interval probes read band 2 | 48/48 — met |
| H6_NOTAIL | 0 tail in 323–334 either column either frame | 0/48 — met |
| H7_HOLEJOIN | gap-13 counts beside M56 ref + c343 recheck flags | 8-row join + True/True — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates
by reproduction (both (row,δ,dec) sets + margins + spans +
runs + gaps match M61 value-exactly on every guard) and by
flank values (4/4 pinned δ/dec/band/d/lo/hi) and by
interval content (2 bulk at the m15-c311 head vs 0
elsewhere across 48 probes). Task 2 discriminates by bulk
(2-vs-0 across columns on m15, 0-vs-0 on s0) and by decile
drift (decspan 3 both, hists d0:5/d3:6/d4:1 vs
d0:4/d1:1/d3:7, neither column flat) and by hole density
(m15-c311 bulkshare 0.1667 vs c343-hole m15 0.0038 at 0
tail everywhere), and not by band (48/48 band 2) nor by
tail presence (0/48 probes, 0/8 join rows) nor by
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

Screenshot: present by rule. The evidence interval map
(`m62-intervalmap.png`, 492 B of 5242880 budget) colors m15
tail-Y by pair class (yellow c311 6 / green c312-pos 13 /
red c312-neg 10 / gray other tail 105) with the 323–334
interval overlay on cols 311/312 (cyan bulk / magenta tail
/ dark-blue noncell); DESIGN.md admits an evidence copy
iff m15 interval bulk counts differ between c311 and c312
(column-asymmetric interval — the pre-registered asymmetry
split) — bulk reads 2-vs-0, met.

Recorded without verdict: the 4 flanks read +10/d0 +46/d3
+9/d1 +14/d1 all band-2 d1; the 323–334 interval reads 2
bulk (323:+3, 324:+1, both d0) + 10 noncell on m15 c311
vs 12 noncell on m15 c312 and 12 + 12 noncell on s0; per-row
deciles drift d0:5/d3:6/d4:1 vs d0:4/d1:1/d3:7 (decspan 3
both); the hole join reads bulkshare 0.1667/0.0000 vs
c343-hole 0.0038/0.0307 with 0 tail on all 8 rows; 0 B
explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| interval suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: flank + 12-row tables + bulk + deciles + holejoin + C-INTERVAL control, bars H1–H7/N |
| interval reproduction + census + wall/exit/shas/determinism | measured | §Step 2: 4 flanks + 48 probes + bulk + deciles + 8-row join + c343 recheck; 0.2 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained, 102 stands; gaps below |
| screenshot if an interval map discriminates (or absence reasoned) | measured | present by rule: asymmetry 2-vs-0; 492 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir —
§Runs):

```
mkdir -p "/Volumes/Extreme SSD/m62" local/research/M62
python3 -m py_compile local/research/M62/m62.py local/research/M62/control.py
cp local/research/M62/m62.py local/research/M62/control.py local/research/M62/DESIGN.md "/Volumes/Extreme SSD/m62/"
python3 "/Volumes/Extreme SSD/m62/m62.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m61/m61.txt" "/Volumes/Extreme SSD/m62" /Users/bradrichardson/dev/ssx3/local/research/M62 > "/Volumes/Extreme SSD/m62/m62.txt" 2>&1
python3 "/Volumes/Extreme SSD/m62/control.py" > "/Volumes/Extreme SSD/m62/control.txt" 2>&1
cp "/Volumes/Extreme SSD/m62/m62-intervalmap.png" local/research/M62/m62-intervalmap.png
```

## Paths

Evidence (committed): `local/research/M62/` — `DESIGN.md`
(suite + interval pins + bars, recorded before running),
`m62.py` (flank + interval tables + bulk + deciles +
holejoin + PNG writer), `control.py` (known-interval
synthetic control), `m62-intervalmap.png` (interval map,
492 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m62/`
— `m62.txt` (receipt: shas, baselines, guards, census +
M61 guard, flank + interval tables, bulk + deciles +
holejoin + c343 recheck, bars, re-run, PNG size — 18766
B), `control.txt` (983 B), `m62.py`, `control.py`,
`DESIGN.md` (working copies), `m62-intervalmap.png`
(working copy, 492 B). No writes into `m15/`, `m16/`,
`m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`, `m23/`,
`m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`, `m30/`,
`m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`,
`m38/`, `m39/`, `m40/`, `m41/`, `m42/`, `m43/`, `m44/`,
`m45/`, `m46/`, `m47/`, `m48/`, `m49/`, `m50/`, `m51/`,
`m52/`, `m53/`, `m54/`, `m55/`, `m56/`, `m57/`, `m58/`,
`m59/`, `m60/`, `m61/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Interval-head bulk pair (new): m15 (323,311) +3 and
   (324,311) +1, both dec 0 — the only bulk in 48
   interval probes, 1–2 rows below the 322 flank. Needs
   its own brief only if head bulk matters: row-323/324
   neighborhood bulk census across neighboring columns,
   offline — no new harness code.
2. Interval column asymmetry (new): m15 interval bulk
   reads 2-vs-0 across c311/c312 while s0 reads 0-vs-0.
   Needs its own brief only if asymmetry matters:
   per-frame bulk census over the pair's full row ranges,
   offline — no new harness code.
3. Interval decile drift (new): c311 deciles read
   0,0,0,3,3,3,3,4,3,0,0,3 vs c312 3×7,0×3,1,0 —
   decspan 3 both, neither flat. Needs its own brief only
   if drift matters: decile-gradient tables across the
   gap on both columns with flank deciles joined, offline
   — no new harness code.
4. Hole-density contrast (new): gap-13 m15-c311 bulkshare
   reads 0.1667 (2/12) vs c343-hole m15 0.0038 (1/261)
   at 0 tail both. Needs its own brief only if density
   matters: bulk-density census across all pair column
   gaps, offline — no new harness code.
5. Counterpart bulk pair (M61 gap 2, still open): the only
   bulk counterparts — (341,311) +1 at a c312 d1-pos row
   and (320,312) +2 at a c311 d1-pos row — both |δ|≤2,
   both dec 3 on the probed column. Needs its own brief
   only if counterpart bulk matters: bulk-at-tail-rows
   census over the pair's 28 distinct rows, offline — no
   new harness code.
6. r316 dec-7 noncell (M61 gap 3, still open): (316,311)
   reads dec 7 yet noncell while (316,312) reads dec 7
   tail +11 — same row, same decile, tail vs noncell one
   column apart. Needs its own brief only if dec-7
   adjacency matters: row-316 Y-band cell census across
   neighboring columns, offline — no new harness code.
7. c312 run-boundary gap (M61 gap 4 = M60 gap 3, still
   open): the only non-1 d on c312 (r369 d=2, lo=367
   hi=373) sits at the first site of the third (pos) run
   while the pos→neg boundary (r343→r353, gap 10) reads
   d=1 both sides; M61 adds c311's d3 at its min row
   (r317, gap 3). Needs its own brief only if
   run-boundary gaps matter: sign-run boundary gap census
   over c312's runs, offline — no new harness code.
8. c343 row-span vs unanimity (M61 gap 5 = M60 gap 1,
   still open): c343 is the widest m15 column (row-span
   264, rows 25–289) yet reads unanimous-neg (0/4).
   Needs its own brief only if span-vs-unanimity matters:
   row-span × unanimity-class census with the far-site row
   included/excluded, offline — no new harness code.
9. c313 all-pos span runner-up (M61 gap 6 = M60 gap 4,
   still open): c313 (all-pos, n=5) reads row-span 41
   (rows 338–379), the widest unanimous all-pos column,
   vs c312's 63. Needs its own brief only if all-pos span
   matters: wide all-pos column census (311/313/315) with
   row positions, offline — no new harness code.
10. Null-4 all-positive (M61 gap 7 = M60 gap 5 = M59 gap
    2, still open): pooled null-4 m15 reads 13/0 (313:
    5/0, 314: 2/0, 311: 6/0, 332: no m15 tail) while c312
    splits 13/10. Needs its own brief only if null-column
    sign matters: null-4 vs c312 sign census across
    frames, offline — no new harness code.
11. Named-9 sign polarity (M61 gap 8 = M60 gap 6 = M59 gap
    3, still open): 6 named streak columns read all-pos
    (257/277/296/301/321/340, 59 sites) vs 3 all-neg
    (341/342/343, 10 sites). Needs its own brief only if
    streak-column polarity matters: named-column sign
    census with row positions, offline — no new harness
    code.
12. Dec-9 column disjointness (M61 gap 9 = M60 gap 7 = M59
    gap 4, still open): 0/75 dec-9 sites share a column
    with dec-1 (likewise dec-8 0/5, dec-6 0/1), while
    dec-0 reads 12/13 and dec-3 13/19 on dec-1 columns.
    Needs its own brief only if bin-column disjointness
    matters: full bin×column contingency over all 10 bins,
    offline — no new harness code.
13. Column decile-mode vs sign (M61 gap 10 = M60 gap 8 =
    M59 gap 5, still open): decile mode 9 sits on 12 m15
    columns split 7 pos-mode / 5 neg-mode — the mode does
    not predict sign. Needs its own brief only if the
    joint distribution matters: mode-decile × mode-sign
    contingency with per-column margins, offline — no new
    harness code.
14. Band-1 off-mode trio (M61 gap 11 = M60 gap 9 = M59 gap
    6 = M58 gap 3, still open): 3/51 read band 1 (far c343
    r289, c344 r287, c353 r272) vs 48 band 2 and 0 band 0.
    Needs its own brief only if the band-1 minority
    matters: band-1 off-mode vs band-1 tail seats, offline
    — no new harness code.
15. m15 null-column dec-9 avoidance (M61 gap 12 = M60 gap
    10 = M59 gap 7 = M58 gap 4 = M57 gap 2, still open):
    m15 null-column frames read 0 dec-9 (313: 0/5 mode 4;
    314: 0/2 mode 3; 311: 0/6 mode 3; 332: no m15 tail)
    while their s0 counterparts read 14/17 dec-9. Needs
    its own brief only if column-frame decile splits
    matter: full per-column-frame decile census over all
    33 union cols, offline — no new harness code.
16. Hole bulk asymmetry (M61 gap 13 = M60 gap 11 = M59 gap
    8 = M58 gap 5 = M57 gap 4, still open): m15's 28–288
    hole holds 1 bulk (r30 |δ|=1) vs s0's 8 bulk
    (r132–272, all |δ|=1), 0 tail either frame; this run
    re-itemizes both from the dumps (True/True, signs
    +/− tabled). Needs its own brief only if hole contents
    matter: per-hole-row bulk tables on c343, offline — no
    new harness code.
17. Null max d=16 (M61 gap 14 = M60 gap 12 = M59 gap 9 =
    M58 gap 6 = M57 gap 5, still open): the next-nearest
    non-far reads d=16 (s0 c313 r292), 246 rows below
    289's 262. Needs its own brief only if the near-far
    margin matters: threshold-sweep census (d≥50/25/10),
    offline — no new harness code.
18. Median-drift no-keep split (M61 gap 15 = M60 gap 13 =
    M59 gap 10 = M58 gap 7 = M57 gap 6, still open):
    |Δ|≤2 columns (296/321/342) keep 0 pooled CONST hits
    while the single kept hit sits on c340 (|Δ|=3). Needs
    its own brief only if drift-vs-survival matters:
    per-site cross-frame err tables joined with
    within-column δ spread, offline — no new harness code.
19. Median-below-peak offset (M61 gap 16 = M60 gap 14 =
    M59 gap 11 = M57 gap 7, still open): 0/16 col-frames
    read median==TRI peak h; med−h reads −1..−25, all
    negative. Needs its own brief only if median-peak
    offset matters: median-vs-hump-position tables, offline
    — no new harness code.
20. c340 transfer cluster (M61 gap 17 = M60 gap 15 = M59
    gap 12 = M58 gap 9 = M57 gap 8, still open): both
    fit-s0→m15 nears + the single fit-m15→s0 hit + 1 of 4
    reverse nears all sit on c340. Needs its own brief
    only if column-local transfer matters: c340 site-level
    transfer census, offline — no new harness code.
21. M61 gap 18 = M60 gap 16 = M59 gap 13 = M58 gap 10 =
    M57 gap 9 = M55 gaps 4–11, 13–27 (still open, by
    reference): see M55 REPORT gaps 4–11, 13–27 for the
    exact brief each needs (interior-run failure;
    ragged-column miss; c343 span-264 leverage;
    peak-seat asymmetry; low-drift no-keep; height-vs-edge
    legs; c340 peak-shift; peak-row/value split; SIGN
    near-hit mass; streak r-coherence; gap-bin 32–63; POS
    collapse; 733 divergence; m15 privates; 700 divergence;
    static-map disjointness; U/V co-residual; δ-sign;
    below-min tail; negatives; Odin port; top-HUD; carrier
    centers).

(Worked this run, dropped from the open list: M61 gap 1 /
c311 candidate-break gap 13 — the interval contents above.
Narrowed this run: M61 gap 13 / hole bulk asymmetry — the
c343 hole re-itemizes True/True with signs tabled.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 interval status) are
   unscored — tabled scope, not chased.
2. No neighboring-column neighborhood: rows 323–334 are
   probed on c311/c312 only (the brief asks both columns,
   not neighbors) — narrowed scope, gap 1 above.
3. No per-site detail beyond the pair + interval in
   REPORT tables: the other 105 m15 tail-Y sites live in
   `m61.txt` (prior receipt, uncommitted here) —
   disclosed, not re-printed.
4. Control seat/carrier N/A: the pure-synthetic control
   recovers interval census + holejoin tables exactly;
   band/streak/carrier/peak seats need dumps (status-map
   synthetic carries band/dec as data, disclosed).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M62/`: `DESIGN.md`, `m62.py`,
`control.py`, `m62-intervalmap.png`, `REPORT.md` (this file).
Total PNG 492 B.
