# M61 — c311-vs-c312 per-site decile/delta join: what separates the runner-up from the split: REPORT

M60 gap 2 worked at table level: c311's 6 + c312's 23 m15
tail-Y sites recompute value-exactly (c311 6/0 all-pos sum
+129, rows 317–336 span 19, ndec 4; c312 13/10 sum +130, 3
runs 7/10/6, rows 316–379 span 63, ndec 6), the same-decile
pairs read d0 2-vs-8 / d1 1-vs-6 / d3 2-vs-6 / d5 1-vs-1
with the pinned δ multisets, the missing deciles read d4×1
(363:−8) + d7×1 (316:+11) on c312 vs 0 on c311 with
noncell at both rows on c311, the row ranges nest (c311
317–336 inside c312 316–379, shared row 317 only), and all
29 seats read band-2/other/none/out with peaks 335/373
1-at-peak each and d 3-at-r317 vs 2-at-r369 (modal 1 both).
Fully offline — no lease of any kind, no boots, no harness
code, no `adb`. No device work. Runbook
`local/muse/prompts/M61.md`. Tables, no verdicts.

Headers read first: `local/research/M60/REPORT.md` (all of
it: c311 6/0 sum +129, ndec 4, d0:2/d1:1/d3:2/d5:1,
maxshare 0.3333, rows 317–336 span 19, dhist 1:5 3:1; c312
13/10 sum +130, runs 7/10/6, rows 316–379 span 63, ndec 6,
d0:8/d1:6/d3:6/d4:1/d5:1/d7:1, dhist 1:22 2:1; M60 gap 2 =
this brief) plus `local/research/M59/REPORT.md` (all of it:
column signs 6/0 sum +129 vs 13/10 sum +130; c312's 23
sites with δ/dec; bincol d0:8/d1:6/d3:6/d4:1/d5:1/d7:1)
plus `local/research/M58/REPORT.md` (all of it: site-51
rows for both columns with band/streak/carrier/701/peak/
at-peak + d/lo/hi).

Time box 4 hours (start 2026-09-20 12:10 EDT); used about
0.2. No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no
writes into `m15/`, `m16/`, `m17/`–`m60/` — all outputs went
to the new `/Volumes/Extreme SSD/m61/`): the 764 M16
per-shape triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`,
the M15 triplet (`m15-v0/mid/full.bin`, second sample), the
top-10 carrier triplets (30 bins), and `m60.txt`
(span/decile tables to reproduce). Work dir
`/Volumes/Extreme SSD/m61/`; evidence `local/research/M61/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17–M60; `m60.txt` 28650 B):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m60.txt | `7287cba4…b34da1f4` |

(Full hexes in `m61.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the
dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M60
exactly. `loo.txt` parses to 764 rows; top-10 shapes +
shares match M16. R_s vs `loo.txt` reads 22815 on s0,
equal. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m61.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try on the
staged copy; one synthetic-path carrier-seat fix landed
before staging — DESIGN.md unaffected). DESIGN.md was
recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m61.py receipt | 0.2 s | exit 0; all guards pass; canon `f9b19670…de58b54` |
| control.py C-PAIR (known column pair) | <1 s | green; unanim + span + runs + dprof + decpair + rowgeom + seatdist exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Census recompute + M60 guard | 2 | in-pass |
| Task 1 (site-29 + decpair + missing) | 2 | in-pass |
| Task 2 (rowgeom + runs + seats) | 2 | in-pass |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m61.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — pair reproduction (do the 29 reproduce?)

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
split (both match `m60.txt` AND the design pins):

| col | s0_n | m15_n | pos | neg | pos share | min | max | sum | class |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 311 | 4 | 6 | 6 | 0 | 1.0000 | +9 | +46 | +129 | all-pos |
| 312 | 3 | 23 | 13 | 10 | 0.5652 | −9 | +33 | +130 | split |

Site-29 table: all 29 sites with (row,col)/δ/decile +
band/streak/carrier/701/peak/at-peak + d/lo/hi (order
(col, row); the c311 {(row,δ,dec)×6} set matches the design
pins — `m60.txt` carries no c311 per-site lines, disclosed
— and the c312 {(row,δ,dec)×23} set matches `m60.txt` AND
the design pins):

| col | row | δ | sign | dec | band | streak | carrier | 701 | peak | atpeak | d | lo | hi |
| ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| 311 | 317 | +9 | pos | 5 | 2 | other | none | out | 335 | False | 3 | None | 320 |
| 311 | 320 | +22 | pos | 1 | 2 | other | none | out | 335 | False | 1 | 317 | 321 |
| 311 | 321 | +20 | pos | 0 | 2 | other | none | out | 335 | False | 1 | 320 | 322 |
| 311 | 322 | +10 | pos | 0 | 2 | other | none | out | 335 | False | 1 | 321 | 335 |
| 311 | 335 | +46 | pos | 3 | 2 | other | none | out | 335 | True | 1 | 322 | 336 |
| 311 | 336 | +22 | pos | 3 | 2 | other | none | out | 335 | False | 1 | 335 | None |
| 312 | 316 | +11 | pos | 7 | 2 | other | none | out | 373 | False | 1 | None | 317 |
| 312 | 317 | +20 | pos | 5 | 2 | other | none | out | 373 | False | 1 | 316 | 318 |
| 312 | 318 | +19 | pos | 1 | 2 | other | none | out | 373 | False | 1 | 317 | 319 |
| 312 | 319 | +9 | pos | 1 | 2 | other | none | out | 373 | False | 1 | 318 | 341 |
| 312 | 341 | +14 | pos | 1 | 2 | other | none | out | 373 | False | 1 | 319 | 342 |
| 312 | 342 | +22 | pos | 3 | 2 | other | none | out | 373 | False | 1 | 341 | 343 |
| 312 | 343 | +9 | pos | 3 | 2 | other | none | out | 373 | False | 1 | 342 | 353 |
| 312 | 353 | −9 | neg | 0 | 2 | other | none | out | 373 | False | 1 | 343 | 354 |
| 312 | 354 | −9 | neg | 0 | 2 | other | none | out | 373 | False | 1 | 353 | 355 |
| 312 | 355 | −9 | neg | 0 | 2 | other | none | out | 373 | False | 1 | 354 | 356 |
| 312 | 356 | −9 | neg | 0 | 2 | other | none | out | 373 | False | 1 | 355 | 362 |
| 312 | 362 | −8 | neg | 3 | 2 | other | none | out | 373 | False | 1 | 356 | 363 |
| 312 | 363 | −8 | neg | 4 | 2 | other | none | out | 373 | False | 1 | 362 | 364 |
| 312 | 364 | −9 | neg | 3 | 2 | other | none | out | 373 | False | 1 | 363 | 365 |
| 312 | 365 | −9 | neg | 0 | 2 | other | none | out | 373 | False | 1 | 364 | 366 |
| 312 | 366 | −9 | neg | 0 | 2 | other | none | out | 373 | False | 1 | 365 | 367 |
| 312 | 367 | −8 | neg | 0 | 2 | other | none | out | 373 | False | 1 | 366 | 369 |
| 312 | 369 | +14 | pos | 3 | 2 | other | none | out | 373 | False | 2 | 367 | 373 |
| 312 | 373 | +33 | pos | 1 | 2 | other | none | out | 373 | True | 1 | 369 | 374 |
| 312 | 374 | +15 | pos | 1 | 2 | other | none | out | 373 | False | 1 | 373 | 377 |
| 312 | 377 | +18 | pos | 0 | 2 | other | none | out | 373 | False | 1 | 374 | 378 |
| 312 | 378 | +23 | pos | 1 | 2 | other | none | out | 373 | False | 1 | 377 | 379 |
| 312 | 379 | +10 | pos | 3 | 2 | other | none | out | 373 | False | 1 | 378 | None |

Decile-pair table: same-decile cross-column pairs, δ values
side by side (A=c311, B=c312; δ sorted asc; all 10 deciles
match the design pins):

| dec | A_n | A δ | B_n | B δ |
| ---: | ---: | --- | ---: | --- |
| 0 | 2 | +10, +20 | 8 | −9, −9, −9, −9, −9, −9, −8, +18 |
| 1 | 1 | +22 | 6 | +9, +14, +15, +19, +23, +33 |
| 2 | 0 | — | 0 | — |
| 3 | 2 | +22, +46 | 6 | −9, −8, +9, +10, +14, +22 |
| 4 | 0 | — | 1 | −8 |
| 5 | 1 | +9 | 1 | +20 |
| 6 | 0 | — | 0 | — |
| 7 | 0 | — | 1 | +11 |
| 8 | 0 | — | 0 | — |
| 9 | 0 | — | 0 | — |

(Shared deciles d0/d1/d3/d5 read 2-vs-8 / 1-vs-6 / 2-vs-6 /
1-vs-1. d2/d6/d8/d9 read 0-vs-0 on both columns.)

Missing-decile table: d4/d7 on c312 vs their absence on
c311 (cell-status probe at those rows on c311 — kind +
delta + decile + band):

| dec | c312 site | c311 n | at same row on c311 |
| ---: | --- | ---: | --- |
| 4 | r363 −8 | 0 | r363: noncell, delta None, dec 3, band 2 |
| 7 | r316 +11 | 0 | r316: noncell, delta None, dec 7, band 2 |

(Both missing-decile rows read noncell on c311 — no bulk,
no tail. The r316 probe reads dec 7 at (316,311), the same
decile as c312's d7 site; the r363 probe reads dec 3 at
(363,311), not dec 4.)

### Task 2 — separator census (what separates them?)

Row-geometry table: row sets + gaps + spans compared:

| col | rows | gaps | span |
| ---: | --- | --- | ---: |
| 311 | 317, 320, 321, 322, 335, 336 | 3, 1, 1, 13, 1 | 19 (317–336) |
| 312 | 316, 317, 318, 319, 341, 342, 343, 353, 354, 355, 356, 362, 363, 364, 365, 366, 367, 369, 373, 374, 377, 378, 379 | 1, 1, 1, 22, 1, 1, 10, 1, 1, 1, 6, 1, 1, 1, 1, 1, 2, 4, 1, 3, 1, 1 | 63 (316–379) |

Row join: intersection [317] (1 shared row); union 28
distinct rows (6+23−1); overlap range 317–336; nested True
(c311 317–336 inside c312 316–379 — overlapping, not
disjoint). Merged label runs (A=311-only, B=312-only,
both=shared): B×1, both×1, B×2, A×5, B×19 — 5 runs:

| merged order (row:label) |
| --- |
| 316:B 317:both 318:B 319:B 320:A 321:A 322:A 335:A 336:A 341:B 342:B 343:B 353:B 354:B 355:B 356:B 362:B 363:B 364:B 365:B 366:B 367:B 369:B 373:B 374:B 377:B 378:B 379:B |

(The 5 c311-only rows sit contiguous 320–336 between c312
blocks — one A block, not alternating.)

Counterpart table: cell status on the other column at each
column's rows (kind + delta + decile + band):

| at c312's rows, on c311 | kind | delta | dec | band |
| ---: | --- | ---: | ---: | ---: |
| 316 | noncell | None | 7 | 2 |
| 317 | tail | +9 | 5 | 2 |
| 318 | noncell | None | 3 | 2 |
| 319 | noncell | None | 0 | 2 |
| 341 | bulk | +1 | 3 | 2 |
| 342 | noncell | None | 3 | 2 |
| 343 | noncell | None | 1 | 2 |
| 353 | noncell | None | 0 | 2 |
| 354 | noncell | None | 0 | 2 |
| 355 | noncell | None | 0 | 2 |
| 356 | noncell | None | 1 | 2 |
| 362 | noncell | None | 1 | 2 |
| 363 | noncell | None | 3 | 2 |
| 364 | noncell | None | 3 | 2 |
| 365 | noncell | None | 3 | 2 |
| 366 | noncell | None | 3 | 2 |
| 367 | noncell | None | 3 | 2 |
| 369 | noncell | None | 0 | 2 |
| 373 | noncell | None | 4 | 2 |
| 374 | noncell | None | 3 | 2 |
| 377 | noncell | None | 1 | 2 |
| 378 | noncell | None | 1 | 2 |
| 379 | noncell | None | 1 | 2 |

| at c311's rows, on c312 | kind | delta | dec | band |
| ---: | --- | ---: | ---: | ---: |
| 317 | tail | +20 | 5 | 2 |
| 320 | bulk | +2 | 3 | 2 |
| 321 | noncell | None | 3 | 2 |
| 322 | noncell | None | 3 | 2 |
| 335 | noncell | None | 0 | 2 |
| 336 | noncell | None | 0 | 2 |

(At c312's 23 rows, c311 reads 1 tail + 1 bulk (r341 +1)
+ 21 noncell. At c311's 6 rows, c312 reads 1 tail + 1 bulk
(r320 +2) + 4 noncell. The shared row 317 reads tail on
both (+9/+20, dec 5 both). All 29 counterpart probes read
band 2.)

Sign-run table: sign runs compared + c311 candidate break
loci (gaps sorted desc — where c311's runs would break if
it split; tabled, no verdict):

| col | class | nruns | runs |
| ---: | --- | ---: | --- |
| 311 | all-pos | 1 | pos 317–336 ×6 |
| 312 | split | 3 | pos 316–343 ×7 / neg 353–367 ×10 / pos 369–379 ×6 |

| c311 gap desc | row pair |
| ---: | --- |
| 13 | 322 → 335 |
| 3 | 317 → 320 |
| 1 | 335 → 336 |
| 1 | 321 → 322 |
| 1 | 320 → 321 |

Seat table: band/streak/carrier/701/at-peak/d distributions
compared:

| col | n | band | streak | carrier | 701 | peak | at-peak | dhist | dmax | dmode |
| ---: | ---: | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| 311 | 6 | 2:6 | other:6 | none:6 | out:6 | 335 | 1/6 (r335) | 1:5 3:1 | 3 (r317) | 1 |
| 312 | 23 | 2:23 | other:23 | none:23 | out:23 | 373 | 1/23 (r373) | 1:22 2:1 | 2 (r369) | 1 |

(Band/streak/carrier/701 read identical distributions —
6/6 vs 23/23 band-2/other/none/out. Peaks read 335
(+46 max) vs 373 (+33 max), 1 at-peak each. Non-1 d sites:
c311 r317 d3 (lo None, hi 320, the min row); c312 r369 d2
(lo 367, hi 373, first site of run 3). Modal d reads 1 on
both.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-PAIR unanimity (2 cols) | c0 3/0 all-pos +36; c1 2/2 split +3 | exact | True |
| C-PAIR span (2 cols) | c0 rows 1–5 sp 4 ndec 2; c1 rows 1–6 sp 5 ndec 3 | exact | True |
| C-PAIR runs (2 cols) | c0 [pos×3]; c1 [pos×1, neg×2, pos×1] | exact | True |
| C-PAIR dprof (2 cols) | c0 {1:2,3:1} dmax/dmode 3/1; c1 {1:4} dmax/dmode 1 | exact | True |
| C-PAIR decpair (10 decs) | d0 2-vs-2 A[+10,+14] B[−9,+9]; d1 1-vs-1 A[+12] B[−8]; d4 0-vs-1 B[+11]; rest 0-vs-0 | exact | True |
| C-PAIR rowgeom | A [1,2,5] gaps [1,3] sp 4; B [1,2,5,6] gaps [1,3,1] sp 5; inter [1,2,5]; union 4; overlap 1–5; nested True; merged both×3,B×1 | exact | True |
| C-PAIR seatdist (2 cols) | c0 band {0:3} streak {other:3} carrier/split701 None peak 5 atpeak 1; c1 band {0:4} streak {other:4} carrier/split701 None peak 6 atpeak 1 | exact | True |

(26 `match=True` lines + `pass=True`, exit 0. Full rows in
`control.txt`. The 1 unanimous + 1 split columns with known
δ/rows/deciles recover exactly, incl. the shared deciles
0/1, the missing decile 4, the 1-vs-3 run split, the nested
ranges, and the gapped d=3 site.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: margins + site-29 + decpair +
missing + runs + setguards + spans, fresh loads) pass1
`f9b19670…de58b54` vs pass2 `f9b19670…de58b54`,
identical=True; 53/53 lines match=True; cell counts
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
| H1_PAIRMATCH | c311 6 + c312 23 match M59/M60 value-exactly (sets + sums +129/+130 + runs 7/10/6 + spans/hists) | sets + margins + spans + runs + decpair all exact — met |
| H2_SAMEDEC | same-decile counts d0 2-vs-8, d1 1-vs-6, d3 2-vs-6, d5 1-vs-1 + δ multisets | counts + multisets exact — met |
| H3_MISSING47 | c312 d4×1 (363:−8) + d7×1 (316:+11); c311 d4×0 + d7×0 | 1/1 vs 0/0 — met |
| H4_SPANNEST | c311 317–336 span 19; c312 316–379 span 63; shared [317]; c311 nested in c312 | 19/63, [317], nested True — met |
| H5_RUNS13 | c311 1 run ×6 all-pos; c312 3 runs 7/10/6 pos/neg/pos | 1×6; 7/10/6 — met |
| H6_SEATSHARED | all 29 band-2 + streak-other + carrier-none + 701-out | 29/29 on all four — met |
| H7_DGAP312 | c311 {1:5,3:1} dmax 3 at r317 modal 1; c312 {1:22,2:1} dmax 2 at r369 modal 1 | exact — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates
by reproduction (both (row,δ,dec) sets + margins + spans +
runs + decpair match M60/design value-exactly on every
guard) and by decile-pair (shared d0/d1/d3/d5 with δ
multisets tabled: d0 B 7-neg/1-pos vs A 2-pos; d1 all-pos
1-vs-6; d3 A 2-pos vs B 2-neg/4-pos; d5 1-vs-1 +9/+20)
and by missing deciles (d4/d7 0-vs-1 each, noncell at both
rows on c311). Task 2 discriminates by row geometry (spans
19 vs 63 nested with 1 shared row; merged 5 label-runs
with one contiguous A block; counterparts 1-tail/1-bulk/
21-noncell vs 1-tail/1-bulk/4-noncell) and by runs (1×6
vs 7/10/6 with c311 candidate gaps 13/3/1/1/1), and not by
band/streak/carrier/701 (identical 6/6 vs 23/23) nor by d
mode (1 both — dmax reads 3-at-min-row vs 2-at-run-3-open)
nor by at-peak rate shape (1 each, peaks 335/373).

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

Screenshot: present by rule. The evidence pair map
(`m61-pairmap.png`, 463 B of 5242880 budget) colors m15
tail-Y by pair class (yellow c311 6 / green c312-pos 13 /
red c312-neg 10 / gray other tail 105); DESIGN.md admits
an evidence copy iff H5_RUNS13 meets (c311 1 run vs c312 3
runs — the pre-registered run split) — runs read 1×6 vs
7/10/6, met.

Recorded without verdict: the 29 pair sites read 6/0 +129
vs 13/10 +130 with same-decile pairs d0 2-vs-8 / d1 1-vs-6
/ d3 2-vs-6 / d5 1-vs-1 and missing d4/d7 0-vs-1 each
(noncell at both rows on c311); row ranges nest 317–336 in
316–379 with shared row 317 only and 5 merged label-runs;
runs read 1×6 vs 7/10/6 with c311 candidate gaps
13/3/1/1/1; seats read 29/29 band-2/other/none/out with
peaks 335/373 and dmax 3-at-r317 vs 2-at-r369 (modal 1
both); 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| pair-join suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: site-29 + decpair + missing + rowgeom + runs + seats + C-PAIR control, bars H1–H7/N |
| pair reproduction + separator census + wall/exit/shas/determinism | measured | §Step 2: 29 sites + 10 decpairs + 2 probes + rowgeom + runs + seats + 29 counterparts; 0.2 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained, 102 stands; gaps below |
| screenshot if a pair map discriminates (or absence reasoned) | measured | present by rule: H5 runs13 (1×6 vs 7/10/6); 463 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir —
§Runs):

```
mkdir -p "/Volumes/Extreme SSD/m61" local/research/M61
python3 -m py_compile local/research/M61/m61.py local/research/M61/control.py
cp local/research/M61/m61.py local/research/M61/control.py local/research/M61/DESIGN.md "/Volumes/Extreme SSD/m61/"
python3 "/Volumes/Extreme SSD/m61/m61.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m60/m60.txt" "/Volumes/Extreme SSD/m61" /Users/bradrichardson/dev/ssx3/local/research/M61 > "/Volumes/Extreme SSD/m61/m61.txt" 2>&1
python3 "/Volumes/Extreme SSD/m61/control.py" > "/Volumes/Extreme SSD/m61/control.txt" 2>&1
cp "/Volumes/Extreme SSD/m61/m61-pairmap.png" local/research/M61/m61-pairmap.png
```

## Paths

Evidence (committed): `local/research/M61/` — `DESIGN.md`
(suite + pair pins + bars, recorded before running),
`m61.py` (site-29 + decpair + missing + rowgeom + runs +
seats + PNG writer), `control.py` (known-pair synthetic
control), `m61-pairmap.png` (pair map, 463 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m61/`
— `m61.txt` (receipt: shas, baselines, guards, census +
M60 guard, site-29 + decpair + missing, rowgeom + runs +
seats, bars, re-run, PNG size), `control.txt`, `m61.py`,
`control.py`, `DESIGN.md` (working copies),
`m61-pairmap.png` (working copy, 463 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`,
`m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`,
`m43/`, `m44/`, `m45/`, `m46/`, `m47/`, `m48/`, `m49/`,
`m50/`, `m51/`, `m52/`, `m53/`, `m54/`, `m55/`, `m56/`,
`m57/`, `m58/`, `m59/`, `m60/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. c311 candidate-break gap 13 (new): c311's largest
   inter-site gap (322→335, 13 rows) vs its other gaps
   (3/1/1/1) — the tabled locus where runs would break if
   c311 split. Needs its own brief only if break loci
   matter: gap-13 row-interval contents (bulk/noncell per
   row, both columns) with deciles, offline — no new
   harness code.
2. Counterpart bulk pair (new): the only bulk
   counterparts — (341,311) +1 at a c312 d1-pos row and
   (320,312) +2 at a c311 d1-pos row — both |δ|≤2, both
   dec 3 on the probed column. Needs its own brief only
   if counterpart bulk matters: bulk-at-tail-rows census
   over the pair's 28 distinct rows, offline — no new
   harness code.
3. r316 dec-7 noncell (new): (316,311) reads dec 7 yet
   noncell while (316,312) reads dec 7 tail +11 — same
   row, same decile, tail vs noncell one column apart.
   Needs its own brief only if dec-7 adjacency matters:
   row-316 Y-band cell census across neighboring columns,
   offline — no new harness code.
4. c312 run-boundary gap (M60 gap 3, still open): the only
   non-1 d on c312 (r369 d=2, lo=367 hi=373) sits at the
   first site of the third (pos) run — the neg→pos run
   boundary — while the pos→neg boundary (r343→r353, gap
   10) reads d=1 both sides; this run adds c311's d3 at
   its min row (r317, gap 3). Needs its own brief only
   if run-boundary gaps matter: sign-run boundary gap
   census over c312's runs, offline — no new harness
   code.
5. c343 row-span vs unanimity (M60 gap 1, still open):
   c343 is the widest m15 column (row-span 264, rows
   25–289) yet reads unanimous-neg (0/4) — row-span does
   not separate split from unanimous. Needs its own brief
   only if span-vs-unanimity matters: row-span ×
   unanimity-class census with the far-site row
   included/excluded, offline — no new harness code.
6. c313 all-pos span runner-up (M60 gap 4, still open):
   c313 (all-pos, n=5) reads row-span 41 (rows 338–379),
   the widest unanimous all-pos column, vs c312's 63.
   Needs its own brief only if all-pos span matters: wide
   all-pos column census (311/313/315) with row
   positions, offline — no new harness code.
7. Null-4 all-positive (M60 gap 5 = M59 gap 2, still
   open): pooled null-4 m15 reads 13/0 (313: 5/0, 314:
   2/0, 311: 6/0, 332: no m15 tail) while c312 splits
   13/10. Needs its own brief only if null-column sign
   matters: null-4 vs c312 sign census across frames,
   offline — no new harness code.
8. Named-9 sign polarity (M60 gap 6 = M59 gap 3, still
   open): 6 named streak columns read all-pos
   (257/277/296/301/321/340, 59 sites) vs 3 all-neg
   (341/342/343, 10 sites). Needs its own brief only if
   streak-column polarity matters: named-column sign
   census with row positions, offline — no new harness
   code.
9. Dec-9 column disjointness (M60 gap 7 = M59 gap 4, still
   open): 0/75 dec-9 sites share a column with dec-1
   (likewise dec-8 0/5, dec-6 0/1), while dec-0 reads
   12/13 and dec-3 13/19 on dec-1 columns. Needs its own
   brief only if bin-column disjointness matters: full
   bin×column contingency over all 10 bins, offline — no
   new harness code.
10. Column decile-mode vs sign (M60 gap 8 = M59 gap 5,
    still open): decile mode 9 sits on 12 m15 columns
    split 7 pos-mode / 5 neg-mode — the mode does not
    predict sign. Needs its own brief only if the joint
    distribution matters: mode-decile × mode-sign
    contingency with per-column margins, offline — no new
    harness code.
11. Band-1 off-mode trio (M60 gap 9 = M59 gap 6 = M58 gap
    3, still open): 3/51 read band 1 (far c343 r289, c344
    r287, c353 r272) vs 48 band 2 and 0 band 0. Needs its
    own brief only if the band-1 minority matters: band-1
    off-mode vs band-1 tail seats, offline — no new
    harness code.
12. m15 null-column dec-9 avoidance (M60 gap 10 = M59 gap
    7 = M58 gap 4 = M57 gap 2, still open): m15
    null-column frames read 0 dec-9 (313: 0/5 mode 4;
    314: 0/2 mode 3; 311: 0/6 mode 3; 332: no m15 tail)
    while their s0 counterparts read 14/17 dec-9. Needs
    its own brief only if column-frame decile splits
    matter: full per-column-frame decile census over all
    33 union cols, offline — no new harness code.
13. Hole bulk asymmetry (M60 gap 11 = M59 gap 8 = M58 gap
    5 = M57 gap 4, still open): m15's 28–288 hole holds
    1 bulk (r30 |δ|=1) vs s0's 8 bulk (r132–272, all
    |δ|=1), 0 tail either frame. Needs its own brief
    only if hole contents matter: per-hole-row bulk
    tables on c343, offline — no new harness code.
14. Null max d=16 (M60 gap 12 = M59 gap 9 = M58 gap 6 =
    M57 gap 5, still open): the next-nearest non-far
    reads d=16 (s0 c313 r292), 246 rows below 289's 262.
    Needs its own brief only if the near-far margin
    matters: threshold-sweep census (d≥50/25/10), offline
    — no new harness code.
15. Median-drift no-keep split (M60 gap 13 = M59 gap 10 =
    M58 gap 7 = M57 gap 6, still open): |Δ|≤2 columns
    (296/321/342) keep 0 pooled CONST hits while the
    single kept hit sits on c340 (|Δ|=3). Needs its own
    brief only if drift-vs-survival matters: per-site
    cross-frame err tables joined with within-column δ
    spread, offline — no new harness code.
16. Median-below-peak offset (M60 gap 14 = M59 gap 11 =
    M57 gap 7, still open): 0/16 col-frames read
    median==TRI peak h; med−h reads −1..−25, all
    negative. Needs its own brief only if median-peak
    offset matters: median-vs-hump-position tables,
    offline — no new harness code.
17. c340 transfer cluster (M60 gap 15 = M59 gap 12 = M58
    gap 9 = M57 gap 8, still open): both fit-s0→m15
    nears + the single fit-m15→s0 hit + 1 of 4 reverse
    nears all sit on c340. Needs its own brief only if
    column-local transfer matters: c340 site-level
    transfer census, offline — no new harness code.
18. M60 gap 16 = M59 gap 13 = M58 gap 10 = M57 gap 9 =
    M55 gaps 4–11, 13–27 (still open, by reference): see
    M55 REPORT gaps 4–11, 13–27 for the exact brief each
    needs (interior-run failure; ragged-column miss; c343
    span-264 leverage; peak-seat asymmetry; low-drift
    no-keep; height-vs-edge legs; c340 peak-shift;
    peak-row/value split; SIGN near-hit mass; streak
    r-coherence; gap-bin 32–63; POS collapse; 733
    divergence; m15 privates; 700 divergence; static-map
    disjointness; U/V co-residual; δ-sign; below-min
    tail; negatives; Odin port; top-HUD; carrier
    centers).

(Worked this run, dropped from the open list: M60 gap 2 /
c311 decile-span runner-up — the per-site decile/delta
join above. Narrowed this run: M60 gap 3 / c312
run-boundary gap — c311's d3-at-min-row joins the table.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 pair status) are
   unscored — tabled scope, not chased.
2. No gap-13 interval contents: rows 323–334 on either
   column are untabled except at c312's site rows (the
   brief asks candidate loci, not interval contents) —
   narrowed scope, gap 1 above.
3. No per-site detail beyond the pair in REPORT tables:
   the other 105 m15 tail-Y sites live in `m60.txt`
   (prior receipt, uncommitted here) — disclosed, not
   re-printed.
4. Control carrier/peak N/A: the pure-synthetic control
   recovers unanimity + span + runs + dprof + decpair +
   rowgeom + seatdist tables exactly; carrier needs
   dumps (N/A synthetic, disclosed); peaks recover via
   synthetic cols.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M61/`: `DESIGN.md`, `m61.py`,
`control.py`, `m61-pairmap.png`, `REPORT.md` (this file).
Total PNG 463 B.
