# M59 — dec-1 all-positive δ: per-bin δ-sign census over m15 bins joined with columns: REPORT

M58 gap 2 worked at table level: all 10 m15 tail-Y decile
bins recompute value-exactly (dec-1 12/12 positive at
+9..+33 sum +214; all-pos bins 1/5/7 with n 12/2/2, so
dec-1 is the only all-positive bin at n≥10), and the 33
union columns read 16 all-positive + 10 all-negative + 1
split (c312 13/10, the only multi-site column with both
signs) + 6 s0-only; pooled null-4 m15 reads 13/0
all-positive; named streak columns split 6 all-pos (59
sites) vs 3 all-neg (341/342/343, 10 sites); 0/75 dec-9
sites share a column with dec-1. Fully offline — no lease
of any kind, no boots, no harness code, no `adb`. No device
work. Runbook `local/muse/prompts/M59.md`. Tables, no
verdicts.

Headers read first: `local/research/M58/REPORT.md` (all of
it: dec-1 12/12 positive +9..+33 sum +214 on cols 307/309/
310/311/312×6/313/315; dec-0 6/7; dec-3 12/7; dec-4 3/2;
dec-5 +9/+20; dec-9 59/16 sum +1179; off-51 pooled +454 at
35/16; 33 union cols; c312 22/23 off-mode) plus
`local/research/M57/REPORT.md` (hist-4: m15 0:13/1:12/3:19/
4:5/5:2 + 75 dec-9; s0 0 in 0–5; shared 67/69) plus
`local/research/M19/REPORT.md` (P(δ>0) 0.8093/0.8019 — the
background sign rate).

Time box 4 hours (start 2026-09-20 10:03 EDT); used about
0.3. No lease of any kind (brief orders none).

Brief-text note (tabled, not a stop-guard): Task 2.2 says
"dec-1's 8 columns" but the 12 sites sit on 7 distinct
columns (307/309/310/311/312/313/315) — the brief's own
Facts section lists 7 (`312×6` + 6 singletons), M58's
site-51 table lists 7, and the recompute reads 7
(`bincol dec1cols: n=7`). The bin table itself (the
stop-guarded reproduction) matches M58 exactly, so the run
proceeds; the "8" is a brief-text miscount, tabled here.

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no
writes into `m15/`, `m16/`, `m17/`–`m58/` — all outputs went
to the new `/Volumes/Extreme SSD/m59/`): the 764 M16
per-shape triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`,
the M15 triplet (`m15-v0/mid/full.bin`, second sample), the
top-10 carrier triplets (30 bins), and `m58.txt` (bin table
to reproduce). Work dir `/Volumes/Extreme SSD/m59/`;
evidence `local/research/M59/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17–M58; `m58.txt` 29888 B):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m58.txt | `d5751823…2d1593da` |

(Full hexes in `m59.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the
dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M58
exactly. `loo.txt` parses to 764 rows; top-10 shapes +
shares match M16. R_s vs `loo.txt` reads 22815 on s0,
equal. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m59.py` invocation (the receipt, 0.6 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try). DESIGN.md
was recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m59.py receipt | 0.6 s | exit 0; all guards pass; canon `fdbe9ec4…c2f77878c` |
| control.py C-SIGN (known bin signs) | <1 s | green; 12 deciles + bin/col/mode tables exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Census recompute + M58 guard | 2 | in-pass |
| Task 1 (binsign + dec-1 + background) | 2 | in-pass |
| Task 2 (colsign + bincol + colmode) | 2 | in-pass |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m59.py` wall | — | 0.6 s |

## Step 2 — estimates

### Task 1 — bin-sign reproduction (do the splits reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail
with sub-bins 28+74 / 50+84 and max 47/48, all 18
per-column guard rows (n/minrow/maxrow/sum) matching
M22/M23/M25/M26/M56 EXACTLY. Named-column bytes read 65 s0 /
68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V). s0 P1 edges + all 10 carrier removed counts+bands
match M18/M19 exactly. Hist m15 recomputes to n=134 0:13/
1:12/2:0/3:19/4:5/5:2/6:1/7:2/8:5/9:75 (dec-9 0.5597, mode
9), matching `m58.txt` AND the design pins (stop rule not
triggered).

Bin-sign table: per-bin n + pos/neg + pos share + δ
min/max/sum over m15 tail-Y (all 10 bins; every row matches
`m58.txt` AND the design pins):

| dec | n | pos | neg | pos share | min | max | sum |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 13 | 6 | 7 | 0.4615 | −9 | +20 | +39 |
| 1 | 12 | 12 | 0 | 1.0000 | +9 | +33 | +214 |
| 2 | 0 | 0 | 0 | n/a | None | None | 0 |
| 3 | 19 | 12 | 7 | 0.6316 | −18 | +46 | +137 |
| 4 | 5 | 3 | 2 | 0.6000 | −8 | +26 | +35 |
| 5 | 2 | 2 | 0 | 1.0000 | +9 | +20 | +29 |
| 6 | 1 | 0 | 1 | 0.0000 | −35 | −35 | −35 |
| 7 | 2 | 2 | 0 | 1.0000 | +11 | +46 | +57 |
| 8 | 5 | 2 | 3 | 0.4000 | −14 | +23 | +5 |
| 9 | 75 | 59 | 16 | 0.7867 | −36 | +48 | +1179 |

(All-pos bins: 1/5/7 with n 12/2/2. At n≥10 the all-pos
set is [1] alone. Full δ counts per bin in the receipt,
matching M58 value-exactly.)

Dec-1 site table: the 12 sites' (row,col)/δ + seats
(band/streak/carrier/701/peak/at-peak — M33 machinery on
12 sites) + d/lo/hi (identity pins; order (col, row)):

| col | row | δ | band | streak | carrier | 701 | peak | atpeak | d | lo | hi |
| ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 307 | 320 | +9 | 2 | other | none | out | 320 | True | N/A | None | None |
| 309 | 327 | +10 | 2 | other | none | out | 327 | True | 1 | None | 328 |
| 310 | 321 | +10 | 2 | other | none | out | 321 | True | N/A | None | None |
| 311 | 320 | +22 | 2 | other | none | out | 335 | False | 1 | 317 | 321 |
| 312 | 318 | +19 | 2 | other | none | out | 373 | False | 1 | 317 | 319 |
| 312 | 319 | +9 | 2 | other | none | out | 373 | False | 1 | 318 | 341 |
| 312 | 341 | +14 | 2 | other | none | out | 373 | False | 1 | 319 | 342 |
| 312 | 373 | +33 | 2 | other | none | out | 373 | True | 1 | 369 | 374 |
| 312 | 374 | +15 | 2 | other | none | out | 373 | False | 1 | 373 | 377 |
| 312 | 378 | +23 | 2 | other | none | out | 373 | False | 1 | 377 | 379 |
| 313 | 339 | +29 | 2 | other | none | out | 339 | True | 1 | 338 | 340 |
| 315 | 336 | +21 | 2 | other | none | out | 336 | True | 1 | 335 | 337 |

(12/12 band-2, 12/12 streak-other, 12/12 carrier-none,
12/12 701-out. At-peak 6/12. d: N/A ×2 (c307/c310
singletons) + 1 ×10. The {(row,col,δ)×12} set matches
`m58.txt` site-51 dec-1 lines AND the design pins.)

Background table: dec-1's 12/12 against the M19 P(δ>0)
background + the pooled off-51 35/16 + the dec-9 59/16
(shares tabled, no tests beyond counts):

| Scope | n | pos/neg | pos share | δ sum |
| --- | ---: | --- | ---: | ---: |
| dec-1 | 12 | 12/0 | 1.0000 | +214 |
| M19 m15 P(δ>0), cell-7 (recomputed 0.8019) | 2539 | — | 0.8019 | — |
| M19 s0 P(δ>0), cell-7 (recomputed 0.8093) | 2475 | — | 0.8093 | — |
| pooled off-51 (dec ≤ 5) | 51 | 35/16 | 0.6863 | +454 |
| dec-9 | 75 | 59/16 | 0.7867 | +1179 |

(Dec-1 pos share 1.0000 reads above all three tabled
shares: 0.8019, 0.6863, 0.7867. Off-51/ dec-9 pos/neg
match M58 35/16 + 59/16.)

### Task 2 — sign-by-column census (does sign track columns?)

Column-sign table: pos/neg splits per column over the 33
union cols on m15 tail-Y (16 all-pos + 10 all-neg + c312
split 13/10 + 6 s0-only):

| col | s0_n | m15_n | pos | neg | pos share | min | max | sum |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 38 | 1 | 0 | 0 | 0 | n/a | — | — | — |
| 65 | 0 | 2 | 0 | 2 | 0.0000 | −17 | −8 | −25 |
| 76 | 0 | 1 | 0 | 1 | 0.0000 | −35 | −35 | −35 |
| 257 | 10 | 10 | 10 | 0 | 1.0000 | +8 | +20 | +172 |
| 277 | 10 | 10 | 10 | 0 | 1.0000 | +8 | +20 | +172 |
| 289 | 0 | 2 | 0 | 2 | 0.0000 | −16 | −8 | −24 |
| 292 | 1 | 0 | 0 | 0 | n/a | — | — | — |
| 293 | 1 | 0 | 0 | 0 | n/a | — | — | — |
| 296 | 9 | 9 | 9 | 0 | 1.0000 | +16 | +46 | +306 |
| 298 | 4 | 7 | 0 | 7 | 0.0000 | −26 | −8 | −114 |
| 299 | 0 | 1 | 0 | 1 | 0.0000 | −36 | −36 | −36 |
| 301 | 11 | 11 | 11 | 0 | 1.0000 | +12 | +48 | +291 |
| 306 | 0 | 2 | 2 | 0 | 1.0000 | +23 | +46 | +69 |
| 307 | 1 | 1 | 1 | 0 | 1.0000 | +9 | +9 | +9 |
| 308 | 0 | 2 | 0 | 2 | 0.0000 | −18 | −8 | −26 |
| 309 | 0 | 2 | 2 | 0 | 1.0000 | +8 | +10 | +18 |
| 310 | 0 | 1 | 1 | 0 | 1.0000 | +10 | +10 | +10 |
| 311 | 4 | 6 | 6 | 0 | 1.0000 | +9 | +46 | +129 |
| 312 | 3 | 23 | 13 | 10 | 0.5652 | −9 | +33 | +130 |
| 313 | 4 | 5 | 5 | 0 | 1.0000 | +17 | +29 | +113 |
| 314 | 7 | 2 | 2 | 0 | 1.0000 | +15 | +24 | +39 |
| 315 | 7 | 5 | 5 | 0 | 1.0000 | +11 | +21 | +83 |
| 316 | 1 | 0 | 0 | 0 | n/a | — | — | — |
| 321 | 10 | 10 | 10 | 0 | 1.0000 | +14 | +31 | +252 |
| 332 | 2 | 0 | 0 | 0 | n/a | — | — | — |
| 340 | 8 | 9 | 9 | 0 | 1.0000 | +14 | +48 | +311 |
| 341 | 0 | 1 | 0 | 1 | 0.0000 | −9 | −9 | −9 |
| 342 | 5 | 5 | 0 | 5 | 0.0000 | −21 | −13 | −87 |
| 343 | 2 | 4 | 0 | 4 | 0.0000 | −34 | −15 | −97 |
| 344 | 0 | 1 | 1 | 0 | 1.0000 | +8 | +8 | +8 |
| 353 | 0 | 1 | 0 | 1 | 0.0000 | −9 | −9 | −9 |
| 372 | 1 | 0 | 0 | 0 | n/a | — | — | — |
| 617 | 0 | 1 | 1 | 0 | 1.0000 | +10 | +10 | +10 |

All-pos columns (16): 257/277/296/301/306/307/309/310/
311/313/314/315/321/340/344/617 (of which n≥2: 12).
All-neg columns (10): 65/76/289/298/299/308/341/342/343/
353 (of which n≥2: 6 — 65/289/298/308/342/343). Split
columns: c312 alone (13/10) — every other multi-site
column (18/19) reads unanimous. s0-only columns (6):
38/292/293/316/332/372. Per-site (row:δ/dec) detail for
all 27 m15 columns is in the receipt; c312's 23:
316:+11/d7 317:+20/d5 318:+19/d1 319:+9/d1 341:+14/d1
342:+22/d3 343:+9/d3 353:−9/d0 354:−9/d0 355:−9/d0
356:−9/d0 362:−8/d3 363:−8/d4 364:−9/d3 365:−9/d0
366:−9/d0 367:−8/d0 369:+14/d3 373:+33/d1 374:+15/d1
377:+18/d0 378:+23/d1 379:+10/d3.

c312 split (H4 input): 23 sites, 13/10, pos share 0.5652.
Null-4 split (H5 input): 313: 5/0, 332: m15_n=0, 314:
2/0, 311: 6/0 — pooled 13/0, pos share 1.0000
(all-positive, not split). Named streak cols: 257: 10/0,
277: 10/0, 296: 9/0, 301: 11/0, 321: 10/0, 340: 9/0
(59 sites all-pos) vs 341: 0/1, 342: 0/5, 343: 0/4 (10
sites all-neg).

Bin-column table: dec-1's 7 distinct columns vs other
bins' columns (measured 7 — see the brief-text note up
top; per-column per-bin site counts + per-bin neg counts):

| col | d0 | d1 | d3 | d4 | d5 | d7 | negs by bin |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 307 | 0 | 1 | 0 | 0 | 0 | 0 | none |
| 309 | 0 | 1 | 1 | 0 | 0 | 0 | none |
| 310 | 0 | 1 | 0 | 0 | 0 | 0 | none |
| 311 | 2 | 1 | 2 | 0 | 1 | 0 | none |
| 312 | 8 | 6 | 6 | 1 | 1 | 1 | d0:7 d3:2 d4:1 |
| 313 | 0 | 1 | 2 | 2 | 0 | 0 | none |
| 315 | 2 | 1 | 2 | 0 | 0 | 0 | none |

(Bins 2/6/8/9 read 0 on all 7 dec-1 columns. The 12 share
columns with dec-0/dec-3 negatives only via c312 — 7
dec-0 negs + 2 dec-3 negs (+ 1 dec-4 neg); the other 6
dec-1 columns read zero negatives across all bins.)

Per-bin counts on dec-1-shared columns (do other bins sit
where the 12 sit?):

| dec | n | on dec-1 cols | off dec-1 cols |
| ---: | ---: | ---: | ---: |
| 0 | 13 | 12 | 1 (c314 r339 +15) |
| 1 | 12 | 12 | 0 |
| 2 | 0 | 0 | 0 |
| 3 | 19 | 13 | 6 (c289×2 c308 c314 c343 c353) |
| 4 | 5 | 3 | 2 (c308 c344) |
| 5 | 2 | 2 | 0 |
| 6 | 1 | 0 | 1 (c76) |
| 7 | 2 | 1 | 1 (c306) |
| 8 | 5 | 0 | 5 (c298×2 c306 c341 c340) |
| 9 | 75 | 0 | 75 |

(Off-column identities derived from the column-sign
per-site detail: dec-0's lone off-column site reads
positive; dec-3's 6 off-column sites carry 5 of its 7
negs — c289 −16/−8, c308 −18, c343 −15, c353 −9 — plus
c314 +24; dec-8's 5 read c298 r29 −14 / r36 −9, c306
r315 +23, c341 r280 −9, c340 r34 +14.)

Mode table: per-column modal decile joined with modal
δ-sign over m15 tail-Y (m15-empty union cols read n/a;
decile ties → highest dec, disclosed; no sign ties
observed):

| col | m15_n | modal dec (n/share) | modal sign (n/share) |
| ---: | ---: | --- | --- |
| 38 | 0 | n/a | n/a |
| 65 | 2 | 9 (2/2 1.0000) | neg (2/2 1.0000) |
| 76 | 1 | 6 (1/1 1.0000) | neg (1/1 1.0000) |
| 257 | 10 | 9 (10/10 1.0000) | pos (10/10 1.0000) |
| 277 | 10 | 9 (10/10 1.0000) | pos (10/10 1.0000) |
| 289 | 2 | 3 (2/2 1.0000) | neg (2/2 1.0000) |
| 292 | 0 | n/a | n/a |
| 293 | 0 | n/a | n/a |
| 296 | 9 | 9 (9/9 1.0000) | pos (9/9 1.0000) |
| 298 | 7 | 9 (5/7 0.7143) | neg (7/7 1.0000) |
| 299 | 1 | 9 (1/1 1.0000) | neg (1/1 1.0000) |
| 301 | 11 | 9 (11/11 1.0000) | pos (11/11 1.0000) |
| 306 | 2 | 8 (1/2 0.5000, tie d7/d8) | pos (2/2 1.0000) |
| 307 | 1 | 1 (1/1 1.0000) | pos (1/1 1.0000) |
| 308 | 2 | 4 (1/2 0.5000, tie d3/d4) | neg (2/2 1.0000) |
| 309 | 2 | 3 (1/2 0.5000, tie d1/d3) | pos (2/2 1.0000) |
| 310 | 1 | 1 (1/1 1.0000) | pos (1/1 1.0000) |
| 311 | 6 | 3 (2/6 0.3333, tie d0/d3) | pos (6/6 1.0000) |
| 312 | 23 | 0 (8/23 0.3478) | pos (13/23 0.5652) |
| 313 | 5 | 4 (2/5 0.4000, tie d3/d4) | pos (5/5 1.0000) |
| 314 | 2 | 3 (1/2 0.5000, tie d0/d3) | pos (2/2 1.0000) |
| 315 | 5 | 3 (2/5 0.4000, tie d0/d3) | pos (5/5 1.0000) |
| 316 | 0 | n/a | n/a |
| 321 | 10 | 9 (10/10 1.0000) | pos (10/10 1.0000) |
| 332 | 0 | n/a | n/a |
| 340 | 9 | 9 (8/9 0.8889) | pos (9/9 1.0000) |
| 341 | 1 | 8 (1/1 1.0000) | neg (1/1 1.0000) |
| 342 | 5 | 9 (5/5 1.0000) | neg (5/5 1.0000) |
| 343 | 4 | 9 (3/4 0.7500) | neg (4/4 1.0000) |
| 344 | 1 | 4 (1/1 1.0000) | pos (1/1 1.0000) |
| 353 | 1 | 3 (1/1 1.0000) | neg (1/1 1.0000) |
| 372 | 0 | n/a | n/a |
| 617 | 1 | 9 (1/1 1.0000) | pos (1/1 1.0000) |

(Modal decile 9 reads on 12 m15 columns: 7 with modal
sign pos (257/277/296/301/321/340/617) + 5 with modal
sign neg (65/298/299/342/343) — the decile mode does not
predict the sign mode. Off-9-mode columns: pos-mode on
306/307/309/310/311/312/313/314/315/344, neg-mode on
76/289/308/341/353.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-SIGN deciles (12 sites) | 1×4, 0×2, 3×3, 9×3 | exact | True |
| C-SIGN bin-sign (10 bins) | d1 4/0 +70; d0 1/1 +11; d3 2/1 +18; d9 2/1 +11; rest n=0 | exact | True |
| C-SIGN col-sign (7 cols) | c9 4/0; c8 1/1; c6 1/1; c7 1/0; c0 1/0; c1 0/1; c2 1/0 | exact | True |
| C-SIGN col-mode (7 cols) | c9 d1/pos; c8 d0/tie; c6 d3/tie; c7 d3/pos; c0 d9/pos; c1 d9/neg; c2 d9/pos | exact | True |

(38 `match=True` lines + `pass=True`, exit 0. Full rows in
`control.txt`. The all-pos bin + 3 split bins with known
δ/cols recover exactly, incl. empty bins and sign ties.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: hist + binsign + dec-1 sites
+ background, fresh loads) pass1 `fdbe9ec4…c2f77878c` vs
pass2 `fdbe9ec4…c2f77878c`, identical=True; 30/30 lines
match=True; cell counts identical=True; tail counts
identical=True.

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
| H1_BINMATCH | m15 tail-Y decile-bin table matches M58 value-exactly (all 10 bins) | n/δ-counts/min/max/sum/pos/neg all exact — met |
| H2_DEC1POS | dec-1 reads 12/12 positive (+9..+33, sum +214, cols pinned) | 12/12, +9..+33, +214 — met |
| H3_DEC1UNIQUE10 | dec-1 the only bin with n≥10 at pos share 1.0000 | all-pos n≥10 = [1] (d5/d7 n=2) — met |
| H4_C312SPLIT | c312's 23 m15 sites split sign | 13/10 — met |
| H5_NULL4SPLIT | pooled null-4 m15 sites split sign | 13/0 all-positive — not met |
| H6_COLVAR | ≥1 n≥2 column all-pos AND ≥1 n≥2 column with ≥1 neg | 12 all-pos + 7 with neg — met |
| H7_ABOVEBG | dec-1 1.0000 exceeds M19 m15 + off-51 + dec-9 shares | 1.0000 > 0.8019/0.6863/0.7867 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates
by reproduction (all 10 bins match M58 value-exactly on
both m58.txt and design pins; the 12 select to the pinned
{(row,col,δ)} set) and by bin-sign (all-pos bins 1/5/7 at
n 12/2/2 vs splits 0:6/7, 3:12/7, 4:3/2, 8:2/3, 9:59/16
and the lone dec-6 neg; background shares 1.0000 vs
0.8019/0.6863/0.7867). Task 2 discriminates by column
(16 all-pos + 10 all-neg + c312 the lone split at 13/10;
null-4 pooled 13/0 all-pos; named-9 59 all-pos vs 10
all-neg on 341/342/343), by bin-column join (dec-1's 7
columns carry negatives only on c312 — d0:7 d3:2 d4:1;
dec-0 12/13 and dec-3 13/19 on dec-1 cols while dec-9
0/75, dec-8 0/5, dec-6 0/1 sit fully off), and by mode
join (decile mode 9 splits 7 pos-mode vs 5 neg-mode
columns, so it does not predict sign; 7 decile ties
resolved highest-dec, no sign ties). Seats do not split
the 12 (12/12 band-2/other/none/out; at-peak 6/6).

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

Screenshot: present by rule. The evidence sign map
(`m59-signmap.png`, 456 B of 5242880 budget) colors m15
tail-Y by (bin-1, sign) class (yellow dec-1 pos 12 /
orange dec-1 neg 0 / green other-bin pos / red other-bin
neg); DESIGN.md admits an evidence copy iff H3_DEC1UNIQUE10
meets (dec-1 the only bin with n≥10 at pos share 1.0000)
— all-pos n≥10 reads [1], met.

Recorded without verdict: the 10 m15 bins read pos
shares 0.4615/1.0000/n-a/0.6316/0.6000/1.0000/0.0000/
1.0000/0.4000/0.7867 with dec-1 12/12 at +9..+33 sum
+214 on 7 distinct columns; the 33 union columns read 16
all-pos + 10 all-neg + c312 split 13/10 + 6 s0-only;
null-4 pooled m15 reads 13/0; named streak columns read
59 all-pos vs 10 all-neg; dec-9/dec-8/dec-6 sit fully off
dec-1 columns (0/75, 0/5, 0/1); 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| sign-census suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: binsign + dec-1 + background + colsign + bincol + colmode + C-SIGN control, bars H1–H7/N |
| bin-sign + column census + wall/exit/shas/determinism | measured | §Step 2: 10 bins + 12 sites + background + 33-col table + 7-col join + 33-col modes; 0.6 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained, 102 stands; gaps below |
| screenshot if a sign map discriminates (or absence reasoned) | measured | present by rule: H3 dec1unique10 ([1]); 456 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir —
§Runs):

```
mkdir -p "/Volumes/Extreme SSD/m59" local/research/M59
python3 -m py_compile local/research/M59/m59.py local/research/M59/control.py
cp local/research/M59/m59.py local/research/M59/control.py local/research/M59/DESIGN.md "/Volumes/Extreme SSD/m59/"
python3 "/Volumes/Extreme SSD/m59/m59.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m58/m58.txt" "/Volumes/Extreme SSD/m59" /Users/bradrichardson/dev/ssx3/local/research/M59 > "/Volumes/Extreme SSD/m59/m59.txt" 2>&1
python3 "/Volumes/Extreme SSD/m59/control.py" > "/Volumes/Extreme SSD/m59/control.txt" 2>&1
cp "/Volumes/Extreme SSD/m59/m59-signmap.png" local/research/M59/m59-signmap.png
```

## Paths

Evidence (committed): `local/research/M59/` — `DESIGN.md`
(suite + sign pins + bars, recorded before running),
`m59.py` (binsign + dec-1 + background + colsign + bincol
+ colmode + PNG writer), `control.py` (known-sign
synthetic control), `m59-signmap.png` (sign map, 456 B,
rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m59/`
— `m59.txt` (receipt: shas, baselines, guards, census +
M58 guard, binsign + dec-1 + background, colsign + bincol
+ colmode, bars, re-run, PNG size), `control.txt`,
`m59.py`, `control.py`, `DESIGN.md` (working copies),
`m59-signmap.png` (working copy, 456 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`,
`m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`,
`m43/`, `m44/`, `m45/`, `m46/`, `m47/`, `m48/`, `m49/`,
`m50/`, `m51/`, `m52/`, `m53/`, `m54/`, `m55/`, `m56/`,
`m57/`, `m58/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. c312 unique sign-split column (new): c312 is the ONLY
   m15 tail-Y column with n≥2 reading both signs (13/10);
   the other 18 multi-site columns read unanimous (12
   all-pos, 6 all-neg). Needs its own brief only if
   column-unanimity matters: per-column sign-unanimity
   census joined with row-span/decile-span, offline — no
   new harness code.
2. Null-4 all-positive (new; H5 not met): pooled null-4
   m15 reads 13/0 (313: 5/0, 314: 2/0, 311: 6/0, 332: no
   m15 tail) while c312 splits 13/10. Needs its own brief
   only if null-column sign matters: null-4 vs c312 sign
   census across frames, offline — no new harness code.
3. Named-9 sign polarity (new): 6 named streak columns
   read all-pos (257/277/296/301/321/340, 59 sites) vs 3
   all-neg (341/342/343, 10 sites). Needs its own brief
   only if streak-column polarity matters: named-column
   sign census with row positions, offline — no new
   harness code.
4. Dec-9 column disjointness (new): 0/75 dec-9 sites share
   a column with dec-1 (likewise dec-8 0/5, dec-6 0/1),
   while dec-0 reads 12/13 and dec-3 13/19 on dec-1
   columns. Needs its own brief only if bin-column
   disjointness matters: full bin×column contingency over
   all 10 bins, offline — no new harness code.
5. Column decile-mode vs sign (new): decile mode 9 sits on
   12 m15 columns split 7 pos-mode / 5 neg-mode — the mode
   does not predict sign. Needs its own brief only if the
   joint distribution matters: mode-decile × mode-sign
   contingency with per-column margins, offline — no new
   harness code.
6. Band-1 off-mode trio (M58 gap 3, still open): 3/51 read
   band 1 (far c343 r289, c344 r287, c353 r272) vs 48 band
   2 and 0 band 0. Needs its own brief only if the band-1
   minority matters: band-1 off-mode vs band-1 tail seats,
   offline — no new harness code.
7. m15 null-column dec-9 avoidance (M58 gap 4 = M57 gap 2,
   still open): m15 null-column frames read 0 dec-9 (313:
   0/5 mode 4; 314: 0/2 mode 3; 311: 0/6 mode 3; 332: no
   m15 tail) while their s0 counterparts read 14/17 dec-9;
   this run adds the null-4 sign split (13/0 all-pos) and
   the mode rows above. Needs its own brief only if
   column-frame decile splits matter: full
   per-column-frame decile census over all 33 union cols,
   offline — no new harness code.
8. Hole bulk asymmetry (M58 gap 5 = M57 gap 4, still open):
   m15's 28–288 hole holds 1 bulk (r30 |δ|=1) vs s0's 8
   bulk (r132–272, all |δ|=1), 0 tail either frame. Needs
   its own brief only if hole contents matter: per-hole-row
   bulk tables on c343, offline — no new harness code.
9. Null max d=16 (M58 gap 6 = M57 gap 5, still open): the
   next-nearest non-far reads d=16 (s0 c313 r292), 246 rows
   below 289's 262; the null-5 span d 16/9/9/7/3. Needs its
   own brief only if the near-far margin matters:
   threshold-sweep census (d≥50/25/10), offline — no new
   harness code.
10. Median-drift no-keep split (M58 gap 7 = M57 gap 6,
    still open): |Δ|≤2 columns (296/321/342) keep 0 pooled
    CONST hits while the single kept hit sits on c340
    (|Δ|=3). Needs its own brief only if drift-vs-survival
    matters: per-site cross-frame err tables joined with
    within-column δ spread, offline — no new harness code.
11. Median-below-peak offset (M58 gap 8 = M57 gap 7, still
    open): 0/16 col-frames read median==TRI peak h; med−h
    reads −1..−25, all negative. Needs its own brief only
    if median-peak offset matters: median-vs-hump-position
    tables, offline — no new harness code.
12. c340 transfer cluster (M58 gap 9 = M57 gap 8, still
    open): both fit-s0→m15 nears + the single fit-m15→s0
    hit + 1 of 4 reverse nears all sit on c340. Needs its
    own brief only if column-local transfer matters: c340
    site-level transfer census, offline — no new harness
    code.
13. M58 gap 10 = M57 gap 9 = M55 gaps 4–11, 13–27 (still
    open, by reference): see M55 REPORT gaps 4–11, 13–27
    for the exact brief each needs (interior-run failure;
    ragged-column miss; c343 span-264 leverage; peak-seat
    asymmetry; low-drift no-keep; height-vs-edge legs; c340
    peak-shift; peak-row/value split; SIGN near-hit mass;
    streak r-coherence; gap-bin 32–63; POS collapse; 733
    divergence; m15 privates; 700 divergence; static-map
    disjointness; U/V co-residual; δ-sign; below-min tail;
    negatives; Odin port; top-HUD; carrier centers).

(Worked this run, dropped from the open list: M58 gap 2 /
dec-1 all-positive δ — the sign census above. Narrowed
this run: M58 gap 1 / c312 r316 — the 23rd c312 site reads
r316 δ+11 dec 7 (receipt `colsign c=312` detail), the
22/1 off-mode split confirms (d0:8/d1:6/d3:6/d4:1/d5:1
vs d7:1), and receipt-derivable seats read band 2 (r316 ∈
299–447) / streak other / peak 373 (max δ +33 unique at
r373) / at-peak False; carrier/701 seats stay untabled —
needs its own brief only if the carrier seat matters.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 sign status) are
   unscored — tabled scope, not chased.
2. No r316 carrier/701 seat: the c312 r316 site's decile
   (7), δ (+11), band/streak/peak/at-peak are tabled, but
   its carrier-in/701 split needs the removed masks on
   that site (not emitted this run) — narrowed gap above.
3. No per-site detail in REPORT column tables: the REPORT
   column-sign table carries margins only; the 134
   per-site (row:δ/dec) rows live in `m59.txt` (receipt,
   uncommitted) — disclosed, not re-printed.
4. Control carrier/peak N/A: the pure-synthetic control
   recovers deciles + bin-sign + col-sign + col-mode
   tables exactly; carrier/peak need dumps/cols (N/A
   synthetic, disclosed).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M59/`: `DESIGN.md`, `m59.py`,
`control.py`, `m59-signmap.png`, `REPORT.md` (this file).
Total PNG 456 B.
