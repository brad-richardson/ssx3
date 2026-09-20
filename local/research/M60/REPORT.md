# M60 — c312 unique sign-split column: per-column sign-unanimity census joined with row-span/decile-span: REPORT

M59 gap 1 worked at table level: all 27 m15 tail-Y
column-sign rows recompute value-exactly (c312 13/10 pos/neg,
min −9 max +33 sum +130, pos share 0.5652; 16 all-pos + 10
all-neg + 6 s0-only columns), c312 is the only split at
n≥2, its 23 sites read 3 sign runs in row order (pos
316–343×7 / neg 353–367×10 / pos 369–379×6, r316 in run 1),
and the span join reads c312 row-span 63 (2nd after c343's
264) with decile-span 6 the unique max (next c311 at 4),
while modal d=1 is shared by all 19 multi-site columns
(c312 dmax 2 at r369; c343 dmax 262). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M60.md`. Tables, no
verdicts.

Headers read first: `local/research/M59/REPORT.md` (all of
it: c312 the only split at n≥2, 13/10, min −9 max +33 sum
+130, pos share 0.5652; 16 all-pos + 10 all-neg + 6 s0-only;
c312's 23 sites with δ/dec; bincol d0:8/d1:6/d3:6/d4:1/d5:1/
d7:1) plus `local/research/M58/REPORT.md` (c312's 23 sites:
22/23 off-mode, r316 δ+11 dec-7 the exception; band/d
machinery) plus `local/research/M56/REPORT.md` (33 union
cols, d machinery via `far_info`).

Time box 4 hours (start 2026-09-20 11:07 EDT); used about
0.2. No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no
writes into `m15/`, `m16/`, `m17/`–`m59/` — all outputs went
to the new `/Volumes/Extreme SSD/m60/`): the 764 M16
per-shape triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`,
the M15 triplet (`m15-v0/mid/full.bin`, second sample), the
top-10 carrier triplets (30 bins), and `m59.txt`
(column-sign table to reproduce). Work dir
`/Volumes/Extreme SSD/m60/`; evidence `local/research/M60/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17–M59; `m59.txt` 22367 B):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m59.txt | `0b95ccc1…df54045c` |

(Full hexes in `m60.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the
dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M59
exactly. `loo.txt` parses to 764 rows; top-10 shapes +
shares match M16. R_s vs `loo.txt` reads 22815 on s0,
equal. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m60.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try). DESIGN.md
was recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m60.py receipt | 0.2 s | exit 0; all guards pass; canon `ecb9c49a…e755e5d730` |
| control.py C-UNAN (known column signs) | <1 s | green; unanimity + span + runs + dprof exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Census recompute + M59 guard | 2 | in-pass |
| Task 1 (unanim + c312 rows/runs + span) | 2 | in-pass |
| Task 2 (spanjoin + decmix + dprof) | 2 | in-pass |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m60.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — unanimity reproduction (does the split reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail
with sub-bins 28+74 / 50+84 and max 47/48, all 18
per-column guard rows (n/minrow/maxrow/sum) matching
M22/M23/M25/M26/M56 EXACTLY. Named-column bytes read 65 s0 /
68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V). s0 P1 edges + all 10 carrier removed counts+bands
match M18/M19 exactly.

Unanimity table: per-column n + pos/neg + unanimous?/split?
over the 33 union cols on m15 tail-Y (every row matches
`m59.txt` AND the design pins; 33/33 col-guards True):

| col | s0_n | m15_n | pos | neg | pos share | min | max | sum | class |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 38 | 1 | 0 | 0 | 0 | n/a | — | — | — | s0-only |
| 65 | 0 | 2 | 0 | 2 | 0.0000 | −17 | −8 | −25 | all-neg |
| 76 | 0 | 1 | 0 | 1 | 0.0000 | −35 | −35 | −35 | all-neg |
| 257 | 10 | 10 | 10 | 0 | 1.0000 | +8 | +20 | +172 | all-pos |
| 277 | 10 | 10 | 10 | 0 | 1.0000 | +8 | +20 | +172 | all-pos |
| 289 | 0 | 2 | 0 | 2 | 0.0000 | −16 | −8 | −24 | all-neg |
| 292 | 1 | 0 | 0 | 0 | n/a | — | — | — | s0-only |
| 293 | 1 | 0 | 0 | 0 | n/a | — | — | — | s0-only |
| 296 | 9 | 9 | 9 | 0 | 1.0000 | +16 | +46 | +306 | all-pos |
| 298 | 4 | 7 | 0 | 7 | 0.0000 | −26 | −8 | −114 | all-neg |
| 299 | 0 | 1 | 0 | 1 | 0.0000 | −36 | −36 | −36 | all-neg |
| 301 | 11 | 11 | 11 | 0 | 1.0000 | +12 | +48 | +291 | all-pos |
| 306 | 0 | 2 | 2 | 0 | 1.0000 | +23 | +46 | +69 | all-pos |
| 307 | 1 | 1 | 1 | 0 | 1.0000 | +9 | +9 | +9 | all-pos |
| 308 | 0 | 2 | 0 | 2 | 0.0000 | −18 | −8 | −26 | all-neg |
| 309 | 0 | 2 | 2 | 0 | 1.0000 | +8 | +10 | +18 | all-pos |
| 310 | 0 | 1 | 1 | 0 | 1.0000 | +10 | +10 | +10 | all-pos |
| 311 | 4 | 6 | 6 | 0 | 1.0000 | +9 | +46 | +129 | all-pos |
| 312 | 3 | 23 | 13 | 10 | 0.5652 | −9 | +33 | +130 | split |
| 313 | 4 | 5 | 5 | 0 | 1.0000 | +17 | +29 | +113 | all-pos |
| 314 | 7 | 2 | 2 | 0 | 1.0000 | +15 | +24 | +39 | all-pos |
| 315 | 7 | 5 | 5 | 0 | 1.0000 | +11 | +21 | +83 | all-pos |
| 316 | 1 | 0 | 0 | 0 | n/a | — | — | — | s0-only |
| 321 | 10 | 10 | 10 | 0 | 1.0000 | +14 | +31 | +252 | all-pos |
| 332 | 2 | 0 | 0 | 0 | n/a | — | — | — | s0-only |
| 340 | 8 | 9 | 9 | 0 | 1.0000 | +14 | +48 | +311 | all-pos |
| 341 | 0 | 1 | 0 | 1 | 0.0000 | −9 | −9 | −9 | all-neg |
| 342 | 5 | 5 | 0 | 5 | 0.0000 | −21 | −13 | −87 | all-neg |
| 343 | 2 | 4 | 0 | 4 | 0.0000 | −34 | −15 | −97 | all-neg |
| 344 | 0 | 1 | 1 | 0 | 1.0000 | +8 | +8 | +8 | all-pos |
| 353 | 0 | 1 | 0 | 1 | 0.0000 | −9 | −9 | −9 | all-neg |
| 372 | 1 | 0 | 0 | 0 | n/a | — | — | — | s0-only |
| 617 | 0 | 1 | 1 | 0 | 1.0000 | +10 | +10 | +10 | all-pos |

Split set: [312] (all n) and [312] at n≥2 — c312 is the
only split. All-pos n≥2 (12): 257/277/296/301/306/309/311/
313/314/315/321/340. All-neg n≥2 (6): 65/289/298/308/342/
343. Singletons (8): 76/299/307/310/341/344/353/617
(unanimous by construction, disclosed). s0-only (6):
38/292/293/316/332/372.

c312 row table: the 23 sites in row order with δ/sign/decile
+ d/lo/hi (M56 machinery) + run id (the {(row,δ,dec)×23}
set matches `m59.txt` AND the design pins):

| row | δ | sign | dec | d | lo | hi | run |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 316 | +11 | pos | 7 | 1 | None | 317 | 1 |
| 317 | +20 | pos | 5 | 1 | 316 | 318 | 1 |
| 318 | +19 | pos | 1 | 1 | 317 | 319 | 1 |
| 319 | +9 | pos | 1 | 1 | 318 | 341 | 1 |
| 341 | +14 | pos | 1 | 1 | 319 | 342 | 1 |
| 342 | +22 | pos | 3 | 1 | 341 | 343 | 1 |
| 343 | +9 | pos | 3 | 1 | 342 | 353 | 1 |
| 353 | −9 | neg | 0 | 1 | 343 | 354 | 2 |
| 354 | −9 | neg | 0 | 1 | 353 | 355 | 2 |
| 355 | −9 | neg | 0 | 1 | 354 | 356 | 2 |
| 356 | −9 | neg | 0 | 1 | 355 | 362 | 2 |
| 362 | −8 | neg | 3 | 1 | 356 | 363 | 2 |
| 363 | −8 | neg | 4 | 1 | 362 | 364 | 2 |
| 364 | −9 | neg | 3 | 1 | 363 | 365 | 2 |
| 365 | −9 | neg | 0 | 1 | 364 | 366 | 2 |
| 366 | −9 | neg | 0 | 1 | 365 | 367 | 2 |
| 367 | −8 | neg | 0 | 1 | 366 | 369 | 2 |
| 369 | +14 | pos | 3 | 2 | 367 | 373 | 3 |
| 373 | +33 | pos | 1 | 1 | 369 | 374 | 3 |
| 374 | +15 | pos | 1 | 1 | 373 | 377 | 3 |
| 377 | +18 | pos | 0 | 1 | 374 | 378 | 3 |
| 378 | +23 | pos | 1 | 1 | 377 | 379 | 3 |
| 379 | +10 | pos | 3 | 1 | 378 | None | 3 |

Run structure: 3 runs — run 1 pos rows 316–343 ×7, run 2
neg rows 353–367 ×10, run 3 pos rows 369–379 ×6. Signs
cluster in runs (no alternation: the 10 negs are
contiguous). r316 sits in run 1 (its first site; d=1,
lo=None, hi=317). The only non-1 d on c312 is r369 (d=2,
the first site of run 3; lo=367 hi=373).

Span table: per-column row-span (max−min row) + decile-span
(distinct deciles) + n (s0-only cols read n/a):

| col | m15_n | rows | rowspan | decspan | dechist |
| ---: | ---: | --- | ---: | ---: | --- |
| 38 | 0 | n/a | n/a | n/a | — |
| 65 | 2 | 311–312 | 1 | 1 | d9:2 |
| 76 | 1 | 350–350 | 0 | 1 | d6:1 |
| 257 | 10 | 23–32 | 9 | 1 | d9:10 |
| 277 | 10 | 23–32 | 9 | 1 | d9:10 |
| 289 | 2 | 375–376 | 1 | 1 | d3:2 |
| 292 | 0 | n/a | n/a | n/a | — |
| 293 | 0 | n/a | n/a | n/a | — |
| 296 | 9 | 24–34 | 10 | 1 | d9:9 |
| 298 | 7 | 27–36 | 9 | 2 | d8:2 d9:5 |
| 299 | 1 | 26–26 | 0 | 1 | d9:1 |
| 301 | 11 | 23–33 | 10 | 1 | d9:11 |
| 306 | 2 | 314–315 | 1 | 2 | d7:1 d8:1 |
| 307 | 1 | 320–320 | 0 | 1 | d1:1 |
| 308 | 2 | 326–327 | 1 | 2 | d3:1 d4:1 |
| 309 | 2 | 327–328 | 1 | 2 | d1:1 d3:1 |
| 310 | 1 | 321–321 | 0 | 1 | d1:1 |
| 311 | 6 | 317–336 | 19 | 4 | d0:2 d1:1 d3:2 d5:1 |
| 312 | 23 | 316–379 | 63 | 6 | d0:8 d1:6 d3:6 d4:1 d5:1 d7:1 |
| 313 | 5 | 338–379 | 41 | 3 | d1:1 d3:2 d4:2 |
| 314 | 2 | 338–339 | 1 | 2 | d0:1 d3:1 |
| 315 | 5 | 333–337 | 4 | 3 | d0:2 d1:1 d3:2 |
| 316 | 0 | n/a | n/a | n/a | — |
| 321 | 10 | 23–32 | 9 | 1 | d9:10 |
| 332 | 0 | n/a | n/a | n/a | — |
| 340 | 9 | 24–34 | 10 | 2 | d8:1 d9:8 |
| 341 | 1 | 280–280 | 0 | 1 | d8:1 |
| 342 | 5 | 27–35 | 8 | 1 | d9:5 |
| 343 | 4 | 25–289 | 264 | 2 | d3:1 d9:3 |
| 344 | 1 | 287–287 | 0 | 1 | d4:1 |
| 353 | 1 | 272–272 | 0 | 1 | d3:1 |
| 372 | 0 | n/a | n/a | n/a | — |
| 617 | 1 | 183–183 | 0 | 1 | d9:1 |

(c312: rows 316–379, rowspan 63, decspan 6 — the
d0:8/d1:6/d3:6/d4:1/d5:1/d7:1 mix matches the M59 bincol
pin.)

### Task 2 — split-vs-unanimous census (what distinguishes c312?)

Span-join table: unanimous vs split columns by row-span and
decile-span (row-span desc):

| col | class | m15_n | rowspan | decspan |
| ---: | --- | ---: | ---: | ---: |
| 343 | all-neg | 4 | 264 | 2 |
| 312 | split | 23 | 63 | 6 |
| 313 | all-pos | 5 | 41 | 3 |
| 311 | all-pos | 6 | 19 | 4 |
| 296 | all-pos | 9 | 10 | 1 |
| 301 | all-pos | 11 | 10 | 1 |
| 340 | all-pos | 9 | 10 | 2 |
| 257 | all-pos | 10 | 9 | 1 |
| 277 | all-pos | 10 | 9 | 1 |
| 298 | all-neg | 7 | 9 | 2 |
| 321 | all-pos | 10 | 9 | 1 |
| 342 | all-neg | 5 | 8 | 1 |
| 315 | all-pos | 5 | 4 | 3 |
| 65 | all-neg | 2 | 1 | 1 |
| 289 | all-neg | 2 | 1 | 1 |
| 306 | all-pos | 2 | 1 | 2 |
| 308 | all-neg | 2 | 1 | 2 |
| 309 | all-pos | 2 | 1 | 2 |
| 314 | all-pos | 2 | 1 | 2 |
| 76 | all-neg | 1 | 0 | 1 |
| 299 | all-neg | 1 | 0 | 1 |
| 307 | all-pos | 1 | 0 | 1 |
| 310 | all-pos | 1 | 0 | 1 |
| 341 | all-neg | 1 | 0 | 1 |
| 344 | all-pos | 1 | 0 | 1 |
| 353 | all-neg | 1 | 0 | 1 |
| 617 | all-pos | 1 | 0 | 1 |

Class summaries (n≥2; singletons rowspan 0 / decspan 1 by
construction):

| class | ncols | cols | rowspans | decspans |
| --- | ---: | --- | --- | --- |
| split | 1 | 312 | [63] | [6] |
| all-pos | 12 | 257/277/296/301/306/309/311/313/314/315/321/340 | [1,1,1,4,9,9,9,10,10,10,19,41] | [1,1,1,1,1,2,2,2,2,3,3,4] |
| all-neg | 6 | 65/289/298/308/342/343 | [1,1,1,8,9,264] | [1,1,1,2,2,2] |
| singleton | 8 | 76/299/307/310/341/344/353/617 | all 0 | all 1 |

(c312 row-span 63 ranks 2nd after c343's 264; c312
decile-span 6 exceeds every unanimous column — all-pos max
4 (c311), all-neg max 2.)

Decile-mix table: per-column decile histogram class (ndec
desc: 312/311/313/315/340/298/343/306/308/309/314, then
ndec 1):

| col | class | m15_n | ndec | hist | maxshare |
| ---: | --- | ---: | ---: | --- | ---: |
| 312 | split | 23 | 6 | d0:8 d1:6 d3:6 d4:1 d5:1 d7:1 | 0.3478 |
| 311 | all-pos | 6 | 4 | d0:2 d1:1 d3:2 d5:1 | 0.3333 |
| 313 | all-pos | 5 | 3 | d1:1 d3:2 d4:2 | 0.4000 |
| 315 | all-pos | 5 | 3 | d0:2 d1:1 d3:2 | 0.4000 |
| 340 | all-pos | 9 | 2 | d8:1 d9:8 | 0.8889 |
| 298 | all-neg | 7 | 2 | d8:2 d9:5 | 0.7143 |
| 343 | all-neg | 4 | 2 | d3:1 d9:3 | 0.7500 |
| 306 | all-pos | 2 | 2 | d7:1 d8:1 | 0.5000 |
| 308 | all-neg | 2 | 2 | d3:1 d4:1 | 0.5000 |
| 309 | all-pos | 2 | 2 | d1:1 d3:1 | 0.5000 |
| 314 | all-pos | 2 | 2 | d0:1 d3:1 | 0.5000 |
| 257 | all-pos | 10 | 1 | d9:10 | 1.0000 |
| 277 | all-pos | 10 | 1 | d9:10 | 1.0000 |
| 296 | all-pos | 9 | 1 | d9:9 | 1.0000 |
| 301 | all-pos | 11 | 1 | d9:11 | 1.0000 |
| 321 | all-pos | 10 | 1 | d9:10 | 1.0000 |
| 342 | all-neg | 5 | 1 | d9:5 | 1.0000 |
| 65 | all-neg | 2 | 1 | d9:2 | 1.0000 |
| 289 | all-neg | 2 | 1 | d3:2 | 1.0000 |
| 76 | all-neg | 1 | 1 | d6:1 | 1.0000 |
| 299 | all-neg | 1 | 1 | d9:1 | 1.0000 |
| 307 | all-pos | 1 | 1 | d1:1 | 1.0000 |
| 310 | all-pos | 1 | 1 | d1:1 | 1.0000 |
| 341 | all-neg | 1 | 1 | d8:1 | 1.0000 |
| 344 | all-pos | 1 | 1 | d4:1 | 1.0000 |
| 353 | all-neg | 1 | 1 | d3:1 | 1.0000 |
| 617 | all-pos | 1 | 1 | d9:1 | 1.0000 |

(c312 ndec 6 is the unique max — next c311 at 4. ndec
distribution over the 27 m15 columns: 6×1 / 4×1 / 3×2 /
2×7 / 1×16. Sixteen columns read single-decile, of which
13 read pure dec-9.)

d-profile table: per-column d histogram class (M56 d
machinery; singletons d=N/A):

| col | class | m15_n | dhist | na | dmax | dmode |
| ---: | --- | ---: | --- | ---: | ---: | ---: |
| 65 | all-neg | 2 | 1:2 | 0 | 1 | 1 |
| 76 | all-neg | 1 | — | 1 | None | None |
| 257 | all-pos | 10 | 1:10 | 0 | 1 | 1 |
| 277 | all-pos | 10 | 1:10 | 0 | 1 | 1 |
| 289 | all-neg | 2 | 1:2 | 0 | 1 | 1 |
| 296 | all-pos | 9 | 1:9 | 0 | 1 | 1 |
| 298 | all-neg | 7 | 1:7 | 0 | 1 | 1 |
| 299 | all-neg | 1 | — | 1 | None | None |
| 301 | all-pos | 11 | 1:11 | 0 | 1 | 1 |
| 306 | all-pos | 2 | 1:2 | 0 | 1 | 1 |
| 307 | all-pos | 1 | — | 1 | None | None |
| 308 | all-neg | 2 | 1:2 | 0 | 1 | 1 |
| 309 | all-pos | 2 | 1:2 | 0 | 1 | 1 |
| 310 | all-pos | 1 | — | 1 | None | None |
| 311 | all-pos | 6 | 1:5 3:1 | 0 | 3 | 1 |
| 312 | split | 23 | 1:22 2:1 | 0 | 2 | 1 |
| 313 | all-pos | 5 | 1:5 | 0 | 1 | 1 |
| 314 | all-pos | 2 | 1:2 | 0 | 1 | 1 |
| 315 | all-pos | 5 | 1:5 | 0 | 1 | 1 |
| 321 | all-pos | 10 | 1:10 | 0 | 1 | 1 |
| 340 | all-pos | 9 | 1:9 | 0 | 1 | 1 |
| 341 | all-neg | 1 | — | 1 | None | None |
| 342 | all-neg | 5 | 1:5 | 0 | 1 | 1 |
| 343 | all-neg | 4 | 1:3 262:1 | 0 | 262 | 1 |
| 344 | all-pos | 1 | — | 1 | None | None |
| 353 | all-neg | 1 | — | 1 | None | None |
| 617 | all-pos | 1 | — | 1 | None | None |

(Modal d=1 on all 19 multi-site columns incl. c312 — the
mode does not discriminate. Non-1 d sites: c343 r289 d262
(the M56 far site), c311 r317 d3, c312 r369 d2. dmax
ranking: 343:262 / 311:3 / 312:2 / rest 1; 16/19
multi-site columns read pure d1.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-UNAN unanimity (5 cols) | c0 3/0 all-pos +50; c1 0/2 all-neg −24; c2 2/2 split +2; c3 0/1 all-neg; c4 2/0 all-pos +24 | exact | True |
| C-UNAN span (5 cols) | c0 rows 2–4 sp 2 ndec 1; c1 rows 5–6 sp 1 ndec 1; c2 rows 1–6 sp 5 ndec 2; c3 row 7 sp 0 ndec 1; c4 rows 0–5 sp 5 ndec 1 | exact | True |
| C-UNAN runs (5 cols) | c0 [pos×3]; c1 [neg×2]; c2 [pos×2, neg×2]; c3 [neg×1]; c4 [pos×2] | exact | True |
| C-UNAN dprof (5 cols) | c0 {1:3}; c1 {1:2}; c2 {1:4}; c3 N/A; c4 {5:2} dmax/dmode 5 | exact | True |

(23 `match=True` lines + `pass=True`, exit 0. Full rows in
`control.txt`. The 3 unanimous multi-site + 1 split + 1
singleton columns with known δ/rows/deciles recover
exactly, incl. the empty c5 absence, the c2 2-run split,
and the c4 gapped d=5 pair.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: unanim + c312 rows/runs +
span, fresh loads) pass1 `ecb9c49a…e755e5d730` vs pass2
`ecb9c49a…e755e5d730`, identical=True; 95/95 lines
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
| H1_COLMATCH | m15 tail-Y column-sign table matches M59 value-exactly (all 27 m15 cols + 6 s0-only) | union + 33/33 col-guards True — met |
| H2_C312SPLIT | c312 reads 13/10 pos/neg (pos share 0.5652; min −9 max +33; sum +130) | 13/10, −9..+33, +130 — met |
| H3_C312UNIQUE | c312 the only split at n≥2 (split set == [312]; 12 all-pos + 6 all-neg) | [312]; 12 + 6 — met |
| H4_SPANWIDE | c312 row-span ≥ 50 | 63 (379−316) — met |
| H5_DECMIX6 | c312 decile-span == 6 AND unique max | 6 (d0:8/d1:6/d3:6/d4:1/d5:1/d7:1); next c311 at 4 — met |
| H6_RUNS3 | c312 reads exactly 3 sign runs 7/10/6 (pos/neg/pos); r316 in run 1 | pos 316–343×7 / neg 353–367×10 / pos 369–379×6; r316 first of run 1 — met |
| H7_DSHARED | c312 modal d == 1 AND every unanimous n≥2 column modal d == 1 | 19/19 multi-site modal d 1 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates
by reproduction (all 27 m15 column-sign rows + 6 s0-only
counts match M59 value-exactly on both m59.txt and design
pins; the 23 select to the pinned {(row,δ,dec)} set) and by
unanimity (split set [312] alone vs 12 all-pos + 6 all-neg
multi-site columns + 8 singletons + 6 s0-only) and by runs
(c312's 10 negs contiguous in run 2 of 3 runs 7/10/6, r316
leading run 1). Task 2 discriminates by decile-span (c312
ndec 6 unique max vs next 4/3/3 and sixteen single-decile
columns, 13 pure dec-9), partially by row-span (c312 63
2nd after the unanimous-neg c343 at 264; all-pos max 41),
and not by d mode (1 on all 19 multi-site columns —
dmax reads 262/3/2 on c343/c311/c312 with 16/19 pure d1).

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

Screenshot: present by rule. The evidence unanimity map
(`m60-unanmap.png`, 455 B of 5242880 budget) colors m15
tail-Y by column unanimity class (yellow split c312 23 /
green unanimous-pos / red unanimous-neg); DESIGN.md admits
an evidence copy iff H3_C312UNIQUE meets (c312 the only
split at n≥2 — the pre-registered unanimity split) —
split_n2 reads [312], met.

Recorded without verdict: the 27 m15 columns read 16
all-pos + 10 all-neg + c312 split 13/10 (+ 6 s0-only);
c312's 23 sites read 3 runs 7/10/6 with r316 leading run 1
and the sole non-1 d (r369 d2) opening run 3; row-span
reads 63 2nd after c343's 264; decile-span reads 6 the
unique max (next 4); modal d reads 1 on all 19 multi-site
columns; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| unanimity suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: unanim + c312 rows/runs + span + spanjoin + decmix + dprof + C-UNAN control, bars H1–H7/N |
| unanimity + span + census + wall/exit/shas/determinism | measured | §Step 2: 33-col table + 23 sites + 3 runs + 33-col spans + join + 27 decmix + 27 dprof; 0.2 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained, 102 stands; gaps below |
| screenshot if a unanimity map discriminates (or absence reasoned) | measured | present by rule: H3 c312unique ([312]); 455 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir —
§Runs):

```
mkdir -p "/Volumes/Extreme SSD/m60" local/research/M60
python3 -m py_compile local/research/M60/m60.py local/research/M60/control.py
cp local/research/M60/m60.py local/research/M60/control.py local/research/M60/DESIGN.md "/Volumes/Extreme SSD/m60/"
python3 "/Volumes/Extreme SSD/m60/m60.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m59/m59.txt" "/Volumes/Extreme SSD/m60" /Users/bradrichardson/dev/ssx3/local/research/M60 > "/Volumes/Extreme SSD/m60/m60.txt" 2>&1
python3 "/Volumes/Extreme SSD/m60/control.py" > "/Volumes/Extreme SSD/m60/control.txt" 2>&1
cp "/Volumes/Extreme SSD/m60/m60-unanmap.png" local/research/M60/m60-unanmap.png
```

## Paths

Evidence (committed): `local/research/M60/` — `DESIGN.md`
(suite + unanimity pins + bars, recorded before running),
`m60.py` (unanim + c312 rows/runs + span + spanjoin +
decmix + dprof + PNG writer), `control.py` (known-sign
synthetic control), `m60-unanmap.png` (unanimity map,
455 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m60/`
— `m60.txt` (receipt: shas, baselines, guards, census +
M59 guard, unanim + c312 rows/runs + span, spanjoin +
decmix + dprof, bars, re-run, PNG size), `control.txt`,
`m60.py`, `control.py`, `DESIGN.md` (working copies),
`m60-unanmap.png` (working copy, 455 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`,
`m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`,
`m43/`, `m44/`, `m45/`, `m46/`, `m47/`, `m48/`, `m49/`,
`m50/`, `m51/`, `m52/`, `m53/`, `m54/`, `m55/`, `m56/`,
`m57/`, `m58/`, `m59/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. c343 row-span vs unanimity (new): c343 is the widest
   m15 column (row-span 264, rows 25–289) yet reads
   unanimous-neg (0/4) — row-span does not separate split
   from unanimous. Needs its own brief only if
   span-vs-unanimity matters: row-span × unanimity-class
   census with the far-site row included/excluded, offline
   — no new harness code.
2. c311 decile-span runner-up (new): c311 (all-pos, n=6)
   reads ndec 4 (d0:2/d1:1/d3:2/d5:1, maxshare 0.3333),
   closest to c312's 6/0.3478, with the same d0/d1/d3/d5
   deciles minus d4/d7. Needs its own brief only if
   runner-up structure matters: c311-vs-c312 per-site
   decile/delta join, offline — no new harness code.
3. c312 run-boundary gap (new): the only non-1 d on c312
   (r369 d=2, lo=367 hi=373) sits at the first site of the
   third (pos) run — the neg→pos run boundary — while the
   pos→neg boundary (r343→r353, gap 10) reads d=1 both
   sides. Needs its own brief only if run-boundary gaps
   matter: sign-run boundary gap census over c312's runs,
   offline — no new harness code.
4. c313 all-pos span runner-up (new): c313 (all-pos, n=5)
   reads row-span 41 (rows 338–379), the widest unanimous
   all-pos column, vs c312's 63. Needs its own brief only
   if all-pos span matters: wide all-pos column census
   (311/313/315) with row positions, offline — no new
   harness code.
5. Null-4 all-positive (M59 gap 2, still open): pooled
   null-4 m15 reads 13/0 (313: 5/0, 314: 2/0, 311: 6/0,
   332: no m15 tail) while c312 splits 13/10. Needs its
   own brief only if null-column sign matters: null-4 vs
   c312 sign census across frames, offline — no new
   harness code.
6. Named-9 sign polarity (M59 gap 3, still open): 6 named
   streak columns read all-pos (257/277/296/301/321/340,
   59 sites) vs 3 all-neg (341/342/343, 10 sites). Needs
   its own brief only if streak-column polarity matters:
   named-column sign census with row positions, offline —
   no new harness code.
7. Dec-9 column disjointness (M59 gap 4, still open): 0/75
   dec-9 sites share a column with dec-1 (likewise dec-8
   0/5, dec-6 0/1), while dec-0 reads 12/13 and dec-3
   13/19 on dec-1 columns. Needs its own brief only if
   bin-column disjointness matters: full bin×column
   contingency over all 10 bins, offline — no new harness
   code.
8. Column decile-mode vs sign (M59 gap 5, still open):
   decile mode 9 sits on 12 m15 columns split 7 pos-mode /
   5 neg-mode — the mode does not predict sign; this run
   adds decile-span 6 unique on the split column vs ≤4
   elsewhere. Needs its own brief only if the joint
   distribution matters: mode-decile × mode-sign
   contingency with per-column margins, offline — no new
   harness code.
9. Band-1 off-mode trio (M59 gap 6 = M58 gap 3, still
   open): 3/51 read band 1 (far c343 r289, c344 r287,
   c353 r272) vs 48 band 2 and 0 band 0. Needs its own
   brief only if the band-1 minority matters: band-1
   off-mode vs band-1 tail seats, offline — no new
   harness code.
10. m15 null-column dec-9 avoidance (M59 gap 7 = M58 gap 4
    = M57 gap 2, still open): m15 null-column frames read
    0 dec-9 (313: 0/5 mode 4; 314: 0/2 mode 3; 311: 0/6
    mode 3; 332: no m15 tail) while their s0 counterparts
    read 14/17 dec-9. Needs its own brief only if
    column-frame decile splits matter: full
    per-column-frame decile census over all 33 union cols,
    offline — no new harness code.
11. Hole bulk asymmetry (M59 gap 8 = M58 gap 5 = M57 gap 4,
    still open): m15's 28–288 hole holds 1 bulk (r30
    |δ|=1) vs s0's 8 bulk (r132–272, all |δ|=1), 0 tail
    either frame. Needs its own brief only if hole
    contents matter: per-hole-row bulk tables on c343,
    offline — no new harness code.
12. Null max d=16 (M59 gap 9 = M58 gap 6 = M57 gap 5,
    still open): the next-nearest non-far reads d=16 (s0
    c313 r292), 246 rows below 289's 262. Needs its own
    brief only if the near-far margin matters:
    threshold-sweep census (d≥50/25/10), offline — no new
    harness code.
13. Median-drift no-keep split (M59 gap 10 = M58 gap 7 =
    M57 gap 6, still open): |Δ|≤2 columns (296/321/342)
    keep 0 pooled CONST hits while the single kept hit
    sits on c340 (|Δ|=3). Needs its own brief only if
    drift-vs-survival matters: per-site cross-frame err
    tables joined with within-column δ spread, offline —
    no new harness code.
14. Median-below-peak offset (M59 gap 11 = M57 gap 7,
    still open): 0/16 col-frames read median==TRI peak h;
    med−h reads −1..−25, all negative. Needs its own
    brief only if median-peak offset matters:
    median-vs-hump-position tables, offline — no new
    harness code.
15. c340 transfer cluster (M59 gap 12 = M58 gap 9 = M57
    gap 8, still open): both fit-s0→m15 nears + the single
    fit-m15→s0 hit + 1 of 4 reverse nears all sit on c340.
    Needs its own brief only if column-local transfer
    matters: c340 site-level transfer census, offline —
    no new harness code.
16. M59 gap 13 = M58 gap 10 = M57 gap 9 = M55 gaps 4–11,
    13–27 (still open, by reference): see M55 REPORT gaps
    4–11, 13–27 for the exact brief each needs
    (interior-run failure; ragged-column miss; c343
    span-264 leverage; peak-seat asymmetry; low-drift
    no-keep; height-vs-edge legs; c340 peak-shift;
    peak-row/value split; SIGN near-hit mass; streak
    r-coherence; gap-bin 32–63; POS collapse; 733
    divergence; m15 privates; 700 divergence; static-map
    disjointness; U/V co-residual; δ-sign; below-min tail;
    negatives; Odin port; top-HUD; carrier centers).

(Worked this run, dropped from the open list: M59 gap 1 /
c312 unique sign-split column — the unanimity + span census
above. Narrowed this run: M59 gap 5 / column decile-mode vs
sign — decile-span joins the table: 6 unique on c312 vs ≤4
elsewhere.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 unanimity status) are
   unscored — tabled scope, not chased.
2. No seat join on spans: band/streak/carrier/701 seats
   are untabled per column (the brief asks row-span +
   decile-span + d only) — narrowed scope, not chased.
3. No per-site detail in REPORT span tables: the REPORT
   unanimity table carries margins only; the 134 per-site
   (row:δ/dec) rows live in `m59.txt` (prior receipt,
   uncommitted here) — disclosed, not re-printed.
4. Control carrier/peak N/A: the pure-synthetic control
   recovers unanimity + span + runs + dprof tables
   exactly; carrier/peak need dumps/cols (N/A synthetic,
   disclosed).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M60/`: `DESIGN.md`, `m60.py`,
`control.py`, `m60-unanmap.png`, `REPORT.md` (this file).
Total PNG 455 B.
