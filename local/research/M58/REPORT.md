# M58 — m15 off-mode decile mass: per-site tables of the 51: REPORT

M57 gap 1 worked at table level: all four tail-Y decile
histograms recompute value-exactly (m15 0:13/1:12/3:19/4:5/
5:2 + 75 dec-9, s0 0 in deciles 0–5, shared 67/69 dec-9,
pooled 167/236), and the 51 m15 off-mode sites (dec ≤ 5)
table to 13 active columns led by c312 with 22/51 (0.4314),
48/51 in band 2 (0.9412), 51/51 carrier-none / 701-out, d
262 ×1 (the far site) + 3/2 ×1 each + 1 ×44 + singleton-N/A
×4, with the far site's nearest off-mode neighbor at
Manhattan 3 (m15 c344 r287, untied). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M58.md`. Tables, no
verdicts.

Headers read first: `local/research/M57/REPORT.md` (all of
it: m15 0:13/1:12/2:0/3:19/4:5/5:2/6:1/7:2/8:5/9:75 n=134;
s0 0 in 0–5; shared 67/69 dec-9 Jaccard 0.4132; pooled
167/236; far m15 (289,343) δ −15 d=262 band 1 dec 3) plus
`local/research/M33/REPORT.md` (decile-seat machinery:
band/decile/streak/carrier/701 seats) plus
`local/research/M56/REPORT.md` (far census: 33 union cols,
221 non-far + 14 singletons; `far_info` d machinery).

Time box 4 hours (start 2026-09-20 09:03 EDT); used about
0.2. No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no
writes into `m15/`, `m16/`, `m17/`–`m57/` — all outputs went
to the new `/Volumes/Extreme SSD/m58/`): the 764 M16
per-shape triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`,
the M15 triplet (`m15-v0/mid/full.bin`, second sample), the
top-10 carrier triplets (30 bins), and `m57.txt` (histograms
+ far seat to reproduce). Work dir `/Volumes/Extreme
SSD/m58/`; evidence `local/research/M58/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17–M57; `m57.txt` 17168 B):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m57.txt | `b1daeafa…5ecf2dc0` |

(Full hexes in `m58.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the
dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M57
exactly. `loo.txt` parses to 764 rows; top-10 shapes +
shares match M16. R_s vs `loo.txt` reads 22815 on s0,
equal. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m58.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try). DESIGN.md
was recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m58.py receipt | 0.2 s | exit 0; all guards pass; canon `f5e58d04…c9afc43` |
| control.py C-OFF51 (known off-mode seats) | <1 s | green; 12 seats + selection + col/band tables exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Far census recompute + M57 guard | 2 | in-pass |
| Task 1 (hist-4 + site-51 + bins) | 2 | in-pass |
| Task 2 (columns + band/d + far-join) | 2 | in-pass |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m58.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — histogram reproduction (do the 51 reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail
with sub-bins 28+74 / 50+84 and max 47/48, all 18
per-column guard rows (n/minrow/maxrow/sum) matching
M22/M23/M25/M26/M56 EXACTLY, and the far census
recomputing to far n=1 + null top-5 + aux (221 non-far,
max d=16, singletons 6/8, 1 distinct far col [343])
matching `m57.txt` value-exactly (stop rule not triggered).
Named-column bytes read 65 s0 / 68 m15. δ==0 count reads 0;
P(δ>0) reproduces M19/M20 0.8093/0.8019. Tail planes read
102/0/0 s0 and 134/0/0 m15 (Y/U/V). s0 P1 edges + all 10
carrier removed counts+bands match M18/M19 exactly. Far
seat recomputes to band 1 / dec 3 / streak 343 /
carrier-none / 701-out / peak 289 / at-peak True (M57
triple-match).

Hist-4 table: all four tail-Y decile histograms recomputed
+ M57 match flags (m57.txt AND design pins, all True):

| Scope | n | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | dec-9 share | mode | m57txt | design |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| s0 | 102 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 6 | 92 | 0.9020 | 9 | True | True |
| m15 | 134 | 13 | 12 | 0 | 19 | 5 | 2 | 1 | 2 | 5 | 75 | 0.5597 | 9 | True | True |
| shared | 69 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 67 | 0.9710 | 9 | True | True |
| pooled | 236 | 13 | 12 | 0 | 19 | 5 | 2 | 3 | 4 | 11 | 167 | 0.7076 | 9 | True | True |

Shared aux: n=69, Jaccard 0.4132 (m57txt + design match,
True). Off-51 guard: n=51, match=True.

Site-51 table: each off-mode site's (row,col)/δ/decile +
band/streak/carrier/701/peak/at-peak seats + d/lo/hi (M33/
M56 machinery on 51 sites; order (dec, col, row)):

| dec | col | row | δ | band | streak | carrier | 701 | peak | atpeak | d | lo | hi |
| ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| 0 | 311 | 321 | +20 | 2 | other | none | out | 335 | False | 1 | 320 | 322 |
| 0 | 311 | 322 | +10 | 2 | other | none | out | 335 | False | 1 | 321 | 335 |
| 0 | 312 | 353 | −9 | 2 | other | none | out | 373 | False | 1 | 343 | 354 |
| 0 | 312 | 354 | −9 | 2 | other | none | out | 373 | False | 1 | 353 | 355 |
| 0 | 312 | 355 | −9 | 2 | other | none | out | 373 | False | 1 | 354 | 356 |
| 0 | 312 | 356 | −9 | 2 | other | none | out | 373 | False | 1 | 355 | 362 |
| 0 | 312 | 365 | −9 | 2 | other | none | out | 373 | False | 1 | 364 | 366 |
| 0 | 312 | 366 | −9 | 2 | other | none | out | 373 | False | 1 | 365 | 367 |
| 0 | 312 | 367 | −8 | 2 | other | none | out | 373 | False | 1 | 366 | 369 |
| 0 | 312 | 377 | +18 | 2 | other | none | out | 373 | False | 1 | 374 | 378 |
| 0 | 314 | 339 | +15 | 2 | other | none | out | 338 | False | 1 | 338 | None |
| 0 | 315 | 334 | +18 | 2 | other | none | out | 336 | False | 1 | 333 | 335 |
| 0 | 315 | 335 | +20 | 2 | other | none | out | 336 | False | 1 | 334 | 336 |
| 1 | 307 | 320 | +9 | 2 | other | none | out | 320 | True | N/A | None | None |
| 1 | 309 | 327 | +10 | 2 | other | none | out | 327 | True | 1 | None | 328 |
| 1 | 310 | 321 | +10 | 2 | other | none | out | 321 | True | N/A | None | None |
| 1 | 311 | 320 | +22 | 2 | other | none | out | 335 | False | 1 | 317 | 321 |
| 1 | 312 | 318 | +19 | 2 | other | none | out | 373 | False | 1 | 317 | 319 |
| 1 | 312 | 319 | +9 | 2 | other | none | out | 373 | False | 1 | 318 | 341 |
| 1 | 312 | 341 | +14 | 2 | other | none | out | 373 | False | 1 | 319 | 342 |
| 1 | 312 | 373 | +33 | 2 | other | none | out | 373 | True | 1 | 369 | 374 |
| 1 | 312 | 374 | +15 | 2 | other | none | out | 373 | False | 1 | 373 | 377 |
| 1 | 312 | 378 | +23 | 2 | other | none | out | 373 | False | 1 | 377 | 379 |
| 1 | 313 | 339 | +29 | 2 | other | none | out | 339 | True | 1 | 338 | 340 |
| 1 | 315 | 336 | +21 | 2 | other | none | out | 336 | True | 1 | 335 | 337 |
| 3 | 289 | 375 | −16 | 2 | other | none | out | 376 | False | 1 | None | 376 |
| 3 | 289 | 376 | −8 | 2 | other | none | out | 376 | True | 1 | 375 | None |
| 3 | 308 | 326 | −18 | 2 | other | none | out | 327 | False | 1 | None | 327 |
| 3 | 309 | 328 | +8 | 2 | other | none | out | 327 | False | 1 | 327 | None |
| 3 | 311 | 335 | +46 | 2 | other | none | out | 335 | True | 1 | 322 | 336 |
| 3 | 311 | 336 | +22 | 2 | other | none | out | 335 | False | 1 | 335 | None |
| 3 | 312 | 342 | +22 | 2 | other | none | out | 373 | False | 1 | 341 | 343 |
| 3 | 312 | 343 | +9 | 2 | other | none | out | 373 | False | 1 | 342 | 353 |
| 3 | 312 | 362 | −8 | 2 | other | none | out | 373 | False | 1 | 356 | 363 |
| 3 | 312 | 364 | −9 | 2 | other | none | out | 373 | False | 1 | 363 | 365 |
| 3 | 312 | 369 | +14 | 2 | other | none | out | 373 | False | 2 | 367 | 373 |
| 3 | 312 | 379 | +10 | 2 | other | none | out | 373 | False | 1 | 378 | None |
| 3 | 313 | 338 | +22 | 2 | other | none | out | 339 | False | 1 | None | 339 |
| 3 | 313 | 378 | +19 | 2 | other | none | out | 339 | False | 1 | 340 | 379 |
| 3 | 314 | 338 | +24 | 2 | other | none | out | 338 | True | 1 | None | 339 |
| 3 | 315 | 333 | +11 | 2 | other | none | out | 336 | False | 1 | None | 334 |
| 3 | 315 | 337 | +13 | 2 | other | none | out | 336 | False | 1 | 336 | None |
| 3 | 343 | 289 | −15 | 1 | 343 | none | out | 289 | True | 262 | 27 | None |
| 3 | 353 | 272 | −9 | 1 | other | none | out | 272 | True | N/A | None | None |
| 4 | 308 | 327 | −8 | 2 | other | none | out | 327 | True | 1 | 326 | None |
| 4 | 312 | 363 | −8 | 2 | other | none | out | 373 | False | 1 | 362 | 364 |
| 4 | 313 | 340 | +26 | 2 | other | none | out | 339 | False | 1 | 339 | 378 |
| 4 | 313 | 379 | +17 | 2 | other | none | out | 339 | False | 1 | 378 | None |
| 4 | 344 | 287 | +8 | 1 | other | none | out | 287 | True | N/A | None | None |
| 5 | 311 | 317 | +9 | 2 | other | none | out | 335 | False | 3 | None | 320 |
| 5 | 312 | 317 | +20 | 2 | other | none | out | 373 | False | 1 | 316 | 318 |

(51/51 carrier-none, 51/51 701-out. Streak: 50 other + far
343. At-peak 13/51: dec-0 0/13, dec-1 6/12, dec-3 5/19,
dec-4 2/5, dec-5 0/2. Band: 48 band-2 / 3 band-1 / 0
band-0. The c312 r317 row pins lo=316: c312's 23rd m15
tail-Y site sits at r316 outside the 51 — decile/δ
untabled, out of scope.)

Decile-bin table: per-bin δ summaries over m15 tail-Y (all
10 bins; bin 2 empty as pinned):

| dec | n | δ counts | min | max | sum | pos | neg |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 13 | −9:6 −8:1 +10:1 +15:1 +18:2 +20:2 | −9 | +20 | +39 | 6 | 7 |
| 1 | 12 | +9:2 +10:2 +14:1 +15:1 +19:1 +21:1 +22:1 +23:1 +29:1 +33:1 | +9 | +33 | +214 | 12 | 0 |
| 2 | 0 | — | None | None | 0 | 0 | 0 |
| 3 | 19 | −18:1 −16:1 −15:1 −9:2 −8:2 +8:1 +9:1 +10:1 +11:1 +13:1 +14:1 +19:1 +22:3 +24:1 +46:1 | −18 | +46 | +137 | 12 | 7 |
| 4 | 5 | −8:2 +8:1 +17:1 +26:1 | −8 | +26 | +35 | 3 | 2 |
| 5 | 2 | +9:1 +20:1 | +9 | +20 | +29 | 2 | 0 |
| 6 | 1 | −35:1 | −35 | −35 | −35 | 0 | 1 |
| 7 | 2 | +11:1 +46:1 | +11 | +46 | +57 | 2 | 0 |
| 8 | 5 | −14:1 −9:2 +14:1 +23:1 | −14 | +23 | +5 | 2 | 3 |
| 9 | 75 | (75 sites; full counts in receipt) | −36 | +48 | +1179 | 59 | 16 |

(Off-51 pooled δ: sum +454 (39+214+137+35+29), pos 35 /
neg 16. Dec-1 reads all-positive (+9..+33); dec-0 splits
6/7; dec-3 splits 12/7; dec-5 reads +9/+20. The +46 max
sits on dec-3 m15 c311 r335; a second +46 sits on dec-7.)

### Task 2 — off-mode geography (where do the 51 sit?)

Column table: off-51 counts by column over the 33 union
cols (M56's column table joined with decile; 13 active
cols, 20 read 0):

| col | s0_n | m15_n | off51_n | off51 share | off-51 sites (row:δ/dec) |
| ---: | ---: | ---: | ---: | ---: | --- |
| 38 | 1 | 0 | 0 | 0.0000 | — |
| 65 | 0 | 2 | 0 | 0.0000 | — |
| 76 | 0 | 1 | 0 | 0.0000 | — |
| 257 | 10 | 10 | 0 | 0.0000 | — |
| 277 | 10 | 10 | 0 | 0.0000 | — |
| 289 | 0 | 2 | 2 | 0.0392 | 375:−16/d3 376:−8/d3 |
| 292 | 1 | 0 | 0 | 0.0000 | — |
| 293 | 1 | 0 | 0 | 0.0000 | — |
| 296 | 9 | 9 | 0 | 0.0000 | — |
| 298 | 4 | 7 | 0 | 0.0000 | — |
| 299 | 0 | 1 | 0 | 0.0000 | — |
| 301 | 11 | 11 | 0 | 0.0000 | — |
| 306 | 0 | 2 | 0 | 0.0000 | — |
| 307 | 1 | 1 | 1 | 0.0196 | 320:+9/d1 |
| 308 | 0 | 2 | 2 | 0.0392 | 326:−18/d3 327:−8/d4 |
| 309 | 0 | 2 | 2 | 0.0392 | 327:+10/d1 328:+8/d3 |
| 310 | 0 | 1 | 1 | 0.0196 | 321:+10/d1 |
| 311 | 4 | 6 | 6 | 0.1176 | 317:+9/d5 320:+22/d1 321:+20/d0 322:+10/d0 335:+46/d3 336:+22/d3 |
| 312 | 3 | 23 | 22 | 0.4314 | 317:+20/d5 318:+19/d1 319:+9/d1 341:+14/d1 342:+22/d3 343:+9/d3 353:−9/d0 354:−9/d0 355:−9/d0 356:−9/d0 362:−8/d3 363:−8/d4 364:−9/d3 365:−9/d0 366:−9/d0 367:−8/d0 369:+14/d3 373:+33/d1 374:+15/d1 377:+18/d0 378:+23/d1 379:+10/d3 |
| 313 | 4 | 5 | 5 | 0.0980 | 338:+22/d3 339:+29/d1 340:+26/d4 378:+19/d3 379:+17/d4 |
| 314 | 7 | 2 | 2 | 0.0392 | 338:+24/d3 339:+15/d0 |
| 315 | 7 | 5 | 5 | 0.0980 | 333:+11/d3 334:+18/d0 335:+20/d0 336:+21/d1 337:+13/d3 |
| 316 | 1 | 0 | 0 | 0.0000 | — |
| 321 | 10 | 10 | 0 | 0.0000 | — |
| 332 | 2 | 0 | 0 | 0.0000 | — |
| 340 | 8 | 9 | 0 | 0.0000 | — |
| 341 | 0 | 1 | 0 | 0.0000 | — |
| 342 | 5 | 5 | 0 | 0.0000 | — |
| 343 | 2 | 4 | 1 | 0.0196 | 289:−15/d3 |
| 344 | 0 | 1 | 1 | 0.0196 | 287:+8/d4 |
| 353 | 0 | 1 | 1 | 0.0196 | 272:−9/d3 |
| 372 | 1 | 0 | 0 | 0.0000 | — |
| 617 | 0 | 1 | 0 | 0.0000 | — |

Modal off-51 column: c312 with 22/51 (0.4314), untied (H5
input). c343 carries 1/51 (the far site, 0.0196); null-4
(313/332/314/311) carries 13/51 (5+0+2+6, 0.2549; H7
input). All 8 named streak columns with m15 tail (257/277/
296/301/321/340/342) read 0 off-mode; named c343 reads 1
(far), named c341 reads 0. c312 reads 22/23 off-mode (the
23rd m15 tail site at r316 is non-off-mode, untabled).

Band/d table: band seats + nearest-neighbor d for the 51
(M56 d machinery on 51 sites; d desc order):

| col | row | dec | band | d | lo | hi |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 343 | 289 | 3 | 1 | 262 | 27 | None |
| 311 | 317 | 5 | 2 | 3 | None | 320 |
| 312 | 369 | 3 | 2 | 2 | 367 | 373 |
| 289 | 375 | 3 | 2 | 1 | None | 376 |
| 289 | 376 | 3 | 2 | 1 | 375 | None |
| 308 | 326 | 3 | 2 | 1 | None | 327 |
| 308 | 327 | 4 | 2 | 1 | 326 | None |
| 309 | 327 | 1 | 2 | 1 | None | 328 |
| 309 | 328 | 3 | 2 | 1 | 327 | None |
| 311 | 320 | 1 | 2 | 1 | 317 | 321 |
| 311 | 321 | 0 | 2 | 1 | 320 | 322 |
| 311 | 322 | 0 | 2 | 1 | 321 | 335 |
| 311 | 335 | 3 | 2 | 1 | 322 | 336 |
| 311 | 336 | 3 | 2 | 1 | 335 | None |
| 312 | 317 | 5 | 2 | 1 | 316 | 318 |
| 312 | 318 | 1 | 2 | 1 | 317 | 319 |
| 312 | 319 | 1 | 2 | 1 | 318 | 341 |
| 312 | 341 | 1 | 2 | 1 | 319 | 342 |
| 312 | 342 | 3 | 2 | 1 | 341 | 343 |
| 312 | 343 | 3 | 2 | 1 | 342 | 353 |
| 312 | 353 | 0 | 2 | 1 | 343 | 354 |
| 312 | 354 | 0 | 2 | 1 | 353 | 355 |
| 312 | 355 | 0 | 2 | 1 | 354 | 356 |
| 312 | 356 | 0 | 2 | 1 | 355 | 362 |
| 312 | 362 | 3 | 2 | 1 | 356 | 363 |
| 312 | 363 | 4 | 2 | 1 | 362 | 364 |
| 312 | 364 | 3 | 2 | 1 | 363 | 365 |
| 312 | 365 | 0 | 2 | 1 | 364 | 366 |
| 312 | 366 | 0 | 2 | 1 | 365 | 367 |
| 312 | 367 | 0 | 2 | 1 | 366 | 369 |
| 312 | 373 | 1 | 2 | 1 | 369 | 374 |
| 312 | 374 | 1 | 2 | 1 | 373 | 377 |
| 312 | 377 | 0 | 2 | 1 | 374 | 378 |
| 312 | 378 | 1 | 2 | 1 | 377 | 379 |
| 312 | 379 | 3 | 2 | 1 | 378 | None |
| 313 | 338 | 3 | 2 | 1 | None | 339 |
| 313 | 339 | 1 | 2 | 1 | 338 | 340 |
| 313 | 340 | 4 | 2 | 1 | 339 | 378 |
| 313 | 378 | 3 | 2 | 1 | 340 | 379 |
| 313 | 379 | 4 | 2 | 1 | 378 | None |
| 314 | 338 | 3 | 2 | 1 | None | 339 |
| 314 | 339 | 0 | 2 | 1 | 338 | None |
| 315 | 333 | 3 | 2 | 1 | None | 334 |
| 315 | 334 | 0 | 2 | 1 | 333 | 335 |
| 315 | 335 | 0 | 2 | 1 | 334 | 336 |
| 315 | 336 | 1 | 2 | 1 | 335 | 337 |
| 315 | 337 | 3 | 2 | 1 | 336 | None |
| 307 | 320 | 1 | 2 | N/A | None | None |
| 310 | 321 | 1 | 2 | N/A | None | None |
| 344 | 287 | 4 | 1 | N/A | None | None |
| 353 | 272 | 3 | 1 | N/A | None | None |

Band histogram: band 0: 0 / band 1: 3 / band 2: 48 (modal
48/51 = 0.9412; H6 input). d-defined 47/51; singleton-N/A
4/51 (c307 r320, c310 r321, c344 r287, c353 r272). d
histogram over the 47: 262 ×1 (far), 3 ×1 (m15 null
c311 r317), 2 ×1 (c312 r369), 1 ×44.

Far-join table: the far site (289,343) against the 51:

| Field | Measured |
| --- | --- |
| far row | m15 c343 r289 δ −15 dec 3 band 1 streak 343 carrier-none 701-out peak 289 at-peak True |
| far in off-51 | True (H4) |
| nearest by \|Δrow\| | m15 c344 r287 δ +8 dec 4, drow 2 dcol 1 Manhattan 3 |
| nearest by \|Δcol\| | m15 c344 r287 δ +8 dec 4, drow 2 dcol 1 Manhattan 3 |
| nearest by Manhattan | m15 c344 r287 δ +8 dec 4, drow 2 dcol 1 Manhattan 3 |
| ties | drow_min 2 (n=1), dcol_min 1 (n=1), Manhattan_min 3 (n=1) — all untied |

(Far itself excluded from the ranking. The nearest
off-mode site on all three metrics is the singleton c344
r287 dec-4 site, 2 rows above and 1 column right of the
far site.)

Dec-3 bin co-members (all 19, row order, far marked):

| col | row | δ | is_far |
| ---: | ---: | ---: | --- |
| 353 | 272 | −9 | False |
| 343 | 289 | −15 | True |
| 308 | 326 | −18 | False |
| 309 | 328 | +8 | False |
| 315 | 333 | +11 | False |
| 311 | 335 | +46 | False |
| 311 | 336 | +22 | False |
| 315 | 337 | +13 | False |
| 313 | 338 | +22 | False |
| 314 | 338 | +24 | False |
| 312 | 342 | +22 | False |
| 312 | 343 | +9 | False |
| 312 | 362 | −8 | False |
| 312 | 364 | −9 | False |
| 312 | 369 | +14 | False |
| 289 | 375 | −16 | False |
| 289 | 376 | −8 | False |
| 313 | 378 | +19 | False |
| 312 | 379 | +10 | False |

(The far site is the 2nd-lowest row of the 19; 17/19 sit
at rows 326–379, all band 2 except the far + c353 r272.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-OFF51 M1–M6 (mode block) | dec 9 ×6, band 0 ×6, streak other ×6 | exact | True |
| C-OFF51 F1–F6 (off-mode block) | dec 3/3/0/1/4/5, band 0 ×6, streak other ×6 | exact | True |
| C-OFF51 select (off-mode 6) | (dec,col,row) sorted ×6 | exact | True |
| C-OFF51 coltable (off-mode 6) | {6:1,7:1,8:1,9:1,10:1,11:1} | exact | True |
| C-OFF51 bandhist (12 sites) | {0:12} | exact | True |
| C-OFF51 hist (12 sites) | {0:1,1:1,3:2,4:1,5:1,9:6}, n=12, dec-9 0.5000, mode 9 @0.5000, rank-3 = 2 | exact | True |

(Carrier/peak N/A synthetic — no masks/cols, disclosed. 30
`match=True` lines + `pass=True`, exit 0. Full rows in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: hist-4 + site-51 + decile-bin,
fresh loads) pass1 `f5e58d04…c9afc43` vs pass2
`f5e58d04…c9afc43`, identical=True; 67/67 lines match=True;
cell counts identical=True; tail counts identical=True.

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
| H1_HIST51 | m15 tail-Y decile histogram matches M57 value-exactly (all 10 bins) | 0:13/1:12/2:0/3:19/4:5/5:2/6:1/7:2/8:5/9:75 — met |
| H2_S0CLEAN | s0 tail-Y sites in deciles 0–5 == 0 | 0 — met |
| H3_SHAREDMODE | shared tail-Y dec-9 share ≥ 0.90 | 67/69 = 0.9710 — met |
| H4_FAROFF | far site m15 (289,343) is a member of the 51 | dec 3, in — met |
| H5_COLCONC | largest single-column count among the 51 ≥ 13 | 22 (c312) — met |
| H6_BANDMODE | modal band among the 51 holds ≥ 26/51 | 48 band-2 (0.9412) — met |
| H7_NULLCOL | share of the 51 on null-4 cols (313/332/314/311) ≥ 0.25 | 13/51 = 0.2549 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates
by reproduction (all four histograms match M57 value-exactly
on both m57.txt and design pins; the 51 select to
0:13/1:12/2:0/3:19/4:5/5:2) and by bin-δ sign (dec-1 reads
12/12 positive, +9..+33, vs dec-0 6/7 and dec-3 12/7; dec-5
reads +9/+20; pooled off-51 δ sums to +454 at pos 35 /
neg 16). Task 2 discriminates by column (c312 carries 22/51
= 0.4314 untied; next 311:6, 313/315:5; 20/33 union cols
read 0 off-mode; all 8 m15-tailed named streak columns
except c343 read 0), by band (48/51 band-2 vs 3 band-1 —
far, c344 r287, c353 r272 — vs 0 band-0), by d (262/3/2
×1 each + 1 ×44 + N/A ×4), and by far-join (nearest
off-mode site on all three metrics is c344 r287 at
Manhattan 3, untied; the far is 2nd-lowest of the 19
dec-3s). Carrier/701 do not split (51/51 none/out); streak
splits 1 far vs 50 other; at-peak splits 13 vs 38.

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
| interior far tail | 102 of cell 7 (4.1%) | \|δ\|≥8, max 47; 100% Y; stands (this run) |
| standing interior remainder | 2475 of cell 7 (100%) | no rule; census tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence off-mode map
(`m58-offmap.png`, 517 B of 5242880 budget) colors pooled
s0∪m15 tail-Y by off-mode class (red far 1 / yellow off-51
non-far 50 / green dec-9 tail / gray dec-6–8 tail);
DESIGN.md admits an evidence copy iff H5_COLCONC meets (a
single column holds ≥13 of the 51) — c312 holds 22, met.

Recorded without verdict: the 51 m15 off-mode sites read
0:13/1:12/3:19/4:5/5:2 with pooled δ sum +454 (pos 35 /
neg 16), sitting on 13/33 union columns led by c312 (22),
in band 2 except the far + c344 r287 + c353 r272 (band 1),
at d 262/3/2/1 ×1/1/1/44 + N/A ×4, all carrier-none /
701-out, 13/51 at-peak; the far site is a member (dec 3)
with its nearest off-mode neighbor at Manhattan 3 (c344
r287, untied); s0 reads 0 off-mode sites and shared reads
67/69 dec-9; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| off-mode suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: hist-4 + site-51 + decile-bin + columns + band/d + far-join + C-OFF51 control, bars H1–H7/N |
| hist-4 + site-51 + bins + geography + wall/exit/shas/determinism | measured | §Step 2: 4 hists + 51 sites + 10 bins + 33-col table + 51 band/d rows + far-join; 0.2 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained, 102 stands; gaps below |
| screenshot if an off-mode map discriminates (or absence reasoned) | measured | present by rule: H5 colconc (c312: 22 ≥ 13); 517 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir —
§Runs):

```
mkdir -p "/Volumes/Extreme SSD/m58" local/research/M58
python3 -m py_compile local/research/M58/m58.py local/research/M58/control.py
cp local/research/M58/m58.py local/research/M58/control.py local/research/M58/DESIGN.md "/Volumes/Extreme SSD/m58/"
python3 "/Volumes/Extreme SSD/m58/m58.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m57/m57.txt" "/Volumes/Extreme SSD/m58" /Users/bradrichardson/dev/ssx3/local/research/M58 > "/Volumes/Extreme SSD/m58/m58.txt" 2>&1
python3 "/Volumes/Extreme SSD/m58/control.py" > "/Volumes/Extreme SSD/m58/control.txt" 2>&1
cp "/Volumes/Extreme SSD/m58/m58-offmap.png" local/research/M58/m58-offmap.png
```

## Paths

Evidence (committed): `local/research/M58/` — `DESIGN.md`
(suite + off-51 pins + bars, recorded before running),
`m58.py` (hist-4 + site-51 + bins + geography + PNG
writer), `control.py` (known off-mode synthetic control),
`m58-offmap.png` (off-mode map, 517 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m58/`
— `m58.txt` (receipt: shas, baselines, guards, census +
M57 guard, hist-4 + site-51 + bins, columns + band/d +
far-join, bars, re-run, PNG size), `control.txt`,
`m58.py`, `control.py`, `DESIGN.md` (working copies),
`m58-offmap.png` (working copy, 517 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`,
`m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`,
`m43/`, `m44/`, `m45/`, `m46/`, `m47/`, `m48/`, `m49/`,
`m50/`, `m51/`, `m52/`, `m53/`, `m54/`, `m55/`, `m56/`,
`m57/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. c312 r316 non-off-mode site (new, minor): the modal
   column's 23rd m15 tail-Y site (r316, lo pin for r317)
   reads non-off-mode (dec 6+, 22/23 off-mode on c312);
   its decile/δ/seat are untabled. Needs its own brief only
   if the exception matters: decile/δ/seat of r316 + the
   22/1 split, offline — no new harness code.
2. Dec-1 all-positive δ (new): all 12 dec-1 off-mode sites
   read δ>0 (+9..+33, sum +214) while dec-0 splits 6/7,
   dec-3 splits 12/7, and dec-4 splits 3/2. Needs its own
   brief only if bin-sign splits matter: per-bin δ-sign
   census over all 10 m15 bins joined with columns,
   offline — no new harness code.
3. Band-1 off-mode trio (new, minor): 3/51 read band 1 (far
   c343 r289, c344 r287, c353 r272) vs 48 band 2 and 0
   band 0. Needs its own brief only if the band-1 minority
   matters: band-1 off-mode vs band-1 tail seats, offline
   — no new harness code.
4. m15 null-column dec-9 avoidance (M57 gap 2, still open):
   m15 null-column frames read 0 dec-9 (313: 0/5 mode 4;
   314: 0/2 mode 3; 311: 0/6 mode 3; 332: no m15 tail)
   while their s0 counterparts read 14/17 dec-9; this run
   adds the null-4 off-mode count (13/51). Needs its own
   brief only if column-frame decile splits matter: full
   per-column-frame decile census over all 33 union cols
   (this run tables off-mode members only), offline — no
   new harness code.
5. Hole bulk asymmetry (M57 gap 4 = M56 gap 2, still open):
   m15's 28–288 hole holds 1 bulk (r30 |δ|=1) vs s0's 8
   bulk (r132–272, all |δ|=1), 0 tail either frame. Needs
   its own brief only if hole contents matter: per-hole-row
   bulk tables on c343, offline — no new harness code.
6. Null max d=16 (M57 gap 5 = M56 gap 3, still open): the
   next-nearest non-far reads d=16 (s0 c313 r292), 246 rows
   below 289's 262; the null-5 span d 16/9/9/7/3. Needs its
   own brief only if the near-far margin matters:
   threshold-sweep census (d≥50/25/10), offline — no new
   harness code.
7. Median-drift no-keep split (M57 gap 6 = M55 gap 1, still
   open): |Δ|≤2 columns (296/321/342) keep 0 pooled CONST
   hits while the single kept hit sits on c340 (|Δ|=3).
   Needs its own brief only if drift-vs-survival matters:
   per-site cross-frame err tables joined with
   within-column δ spread, offline — no new harness code.
8. Median-below-peak offset (M57 gap 7 = M55 gap 2, still
   open): 0/16 col-frames read median==TRI peak h; med−h
   reads −1..−25, all negative. Needs its own brief only if
   median-peak offset matters: median-vs-hump-position
   tables, offline — no new harness code.
9. c340 transfer cluster (M57 gap 8 = M55 gap 3, still open):
   both fit-s0→m15 nears + the single fit-m15→s0 hit + 1 of
   4 reverse nears all sit on c340. Needs its own brief only
   if column-local transfer matters: c340 site-level
   transfer census, offline — no new harness code.
10. M57 gap 9 = M55 gaps 4–11, 13–27 (still open, by
    reference): see M55 REPORT gaps 4–11, 13–27 for the
    exact brief each needs (interior-run failure;
    ragged-column miss; c343 span-264 leverage; peak-seat
    asymmetry; low-drift no-keep; height-vs-edge legs; c340
    peak-shift; peak-row/value split; SIGN near-hit mass;
    streak r-coherence; gap-bin 32–63; POS collapse; 733
    divergence; m15 privates; 700 divergence; static-map
    disjointness; U/V co-residual; δ-sign; below-min tail;
    negatives; Odin port; top-HUD; carrier centers).

(Worked this run, dropped from the open list: M57 gap 1 /
the 51 off-mode sites — the tables above — and M57 gap 3 /
second pooled dec-5 site — m15 c312 r317 δ +20, the site-51
dec-5 pair alongside the m15 null c311 r317.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 off-mode status) are
   unscored — tabled scope, not chased.
2. No c312 r316 identity: the modal column's lone
   non-off-mode tail site is pinned by lo only (r316);
   its decile/δ/seat are untabled (gap 1 above).
3. No full column-frame decile census: the column table
   carries off-51 members + counts over 33 cols, not the
   per-column-frame decile splits M57 gap 2 asks (gap 4
   above).
4. Control carrier/peak N/A: the pure-synthetic control
   recovers seats + selection + col/band tables + histogram
   + shares + ranks exactly; carrier/peak need dumps/cols
   (N/A synthetic, disclosed).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M58/`: `DESIGN.md`, `m58.py`,
`control.py`, `m58-offmap.png`, `REPORT.md` (this file).
Total PNG 517 B.
