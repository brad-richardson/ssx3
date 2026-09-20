# M57 — far vs null-5 decile seats: does the far site's dec-3 seat discriminate?: REPORT

M56 gap 1 worked at table level: the far seat reproduces
exactly (m15 (289,343), δ −15, d=262, band 1, s0-P1 dec 3,
streak 343, carrier-none, 701-out, at-peak) with the null-5
frame/col/row/d/δ/lo/hi matching `m56.txt` value-exactly;
the seat-6 deciles read far dec-3 vs nulls dec-9 ×4 + dec-5
×1 (H6 far-unique met), against a pooled tail-Y dec-9 share
of 167/236 = 0.7076 (s0 92/102, m15 75/134, shared 67/69;
M33 shared 85/94 cited). Fully offline — no lease of any
kind, no boots, no harness code, no `adb`. No device work.
Runbook `local/muse/prompts/M57.md`. Tables, no verdicts.

Headers read first: `local/research/M56/REPORT.md` (all of
it: far m15 (289,343) δ −15 d=262 band 1 dec 3 streak 343
carrier-none 701-out at-peak; null-5 s0 c313 r292 d16 δ−16
/ s0 c332 r295 d9 δ+10 / s0 c332 r304 d9 δ−12 / s0 c314
r269 d7 δ+12 / m15 c311 r317 d3 δ+9; H5 0/1) plus
`local/research/M33/REPORT.md` (decile-seat machinery +
dec-9 mode: shared-tail decile histogram dec 0–5:0 / 6:1 /
7:2 / 8:6 / 9:85, dec-9 85/94 = 0.9043) plus
`local/research/M19/REPORT.md` (P(δ>0) 0.8093/0.8019 + s0
P1 edges).

Time box 4 hours (start 2026-09-20 08:06 EDT); used about
0.1. No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no
writes into `m15/`, `m16/`, `m17/`–`m56/` — all outputs went
to the new `/Volumes/Extreme SSD/m57/`): the 764 M16
per-shape triplets (`m16-v0/mid/full-sNNNN.bin`), `loo.txt`,
the M15 triplet (`m15-v0/mid/full.bin`, second sample), the
top-10 carrier triplets (30 bins), and `m56.txt` (far seat +
null-5 to reproduce). Work dir `/Volumes/Extreme SSD/m57/`;
evidence `local/research/M57/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17–M56; `m56.txt` 14067 B):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m56.txt | `69ba1941…90deaabd` |

(Full hexes in `m57.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the
dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M56
exactly. `loo.txt` parses to 764 rows; top-10 shapes +
shares match M16. R_s vs `loo.txt` reads 22815 on s0,
equal. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m57.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try). DESIGN.md
was recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m57.py receipt | 0.2 s | exit 0; all guards pass; canon `ac7cb03d…ed04b77` |
| control.py C-DEC1 (known decile seats) | <1 s | green; 12 seats + histogram exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Census recompute + M56 guard | 2 | in-pass |
| Task 1 (seat-6 + context + d-dec) | 2 | in-pass |
| Task 2 (histograms + margin + columns) | 2 | in-pass |
| Determinism re-run (Task 1+2 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m57.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — seat reproduction (do the 6 seats reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail
with sub-bins 28+74 / 50+84 and max 47/48, all 18
per-column guard rows (n/minrow/maxrow/sum) matching
M22/M23/M25/M26/M56 EXACTLY, and the far census
recomputing to far n=1 + null-5 + aux (221 non-far, max
d=16, singletons 6/8) matching `m56.txt` value-exactly
(stop rule not triggered). Named-column bytes read 65 s0 /
68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V). s0 P1 edges + all 10 carrier removed counts+bands
match M18/M19 exactly.

Seat-6 table: far + null-5 rows with band + s0-P1 decile +
streak + carrier + 701 + at-peak + d + δ (M33 machinery on
6 sites; far seat matches M56 exactly):

| Role | Frame | col | row | d | δ | lo | hi | band | dec | streak | carrier_in | 701 | peak | atpeak |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |
| far | m15 | 343 | 289 | 262 | −15 | 27 | None | 1 | 3 | 343 | none | out | 289 | True |
| null | s0 | 313 | 292 | 16 | −16 | 276 | None | 1 | 9 | other | none | out | 275 | False |
| null | s0 | 332 | 295 | 9 | +10 | None | 304 | 1 | 9 | other | none | out | 295 | True |
| null | s0 | 332 | 304 | 9 | −12 | 295 | None | 2 | 9 | other | none | out | 295 | False |
| null | s0 | 314 | 269 | 7 | +12 | None | 276 | 1 | 9 | other | none | out | 277 | False |
| null | m15 | 311 | 317 | 3 | +9 | None | 320 | 2 | 5 | other | none | out | 335 | False |

(Null deciles: 9/9/9/9/5. Null bands: 1/1/2/1/2. All 6
carrier-none, all 6 701-out. Far at-peak True; nulls
at-peak 1/5 — s0 c332 r295 at its column peak.)

Decile-context table: each site's decile against the M33
shared-tail decile histogram (dec-9 85/94 mode — cited, not
recomputed: s0/s9 frames):

| dec | M33 shared n/94 | share | seat-6 marks |
| ---: | ---: | ---: | --- |
| 0 | 0 | 0.0000 | — |
| 1 | 0 | 0.0000 | — |
| 2 | 0 | 0.0000 | — |
| 3 | 0 | 0.0000 | far m15 c343 r289 |
| 4 | 0 | 0.0000 | — |
| 5 | 0 | 0.0000 | null m15 c311 r317 |
| 6 | 1 | 0.0106 | — |
| 7 | 2 | 0.0213 | — |
| 8 | 6 | 0.0638 | — |
| 9 | 85 | 0.9043 | null s0 c313 r292, s0 c332 r295, s0 c332 r304, s0 c314 r269 |

(The far dec-3 sits in a zero-count M33-shared bin; the
m15 null dec-5 likewise; the 4 s0 nulls sit on the 85/94
mode.)

Distance-decile table: d vs decile for the 6 (d desc):

| Frame | col | row | d | dec |
| --- | ---: | ---: | ---: | ---: |
| m15 | 343 | 289 | 262 | 3 |
| s0 | 313 | 292 | 16 | 9 |
| s0 | 332 | 295 | 9 | 9 |
| s0 | 332 | 304 | 9 | 9 |
| s0 | 314 | 269 | 7 | 9 |
| m15 | 311 | 317 | 3 | 5 |

(d 262 → dec 3; d 16–7 → dec 9 ×4; d 3 → dec 5.)

### Task 2 — decile-margin census (is dec-3 off-mode?)

Tail-decile table: full s0+m15 tail-Y decile histogram
recomputed (M33 shared + per-frame splits; shared S =
T_s0 ∩ T_m15, n=69, Jaccard 0.4132; pooled = multiset
union, shared counted twice):

| Scope | n | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | dec-9 share | mode |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 102 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 6 | 92 | 0.9020 | 9 |
| m15 | 134 | 13 | 12 | 0 | 19 | 5 | 2 | 1 | 2 | 5 | 75 | 0.5597 | 9 |
| shared | 69 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 67 | 0.9710 | 9 |
| pooled | 236 | 13 | 12 | 0 | 19 | 5 | 2 | 3 | 4 | 11 | 167 | 0.7076 | 9 |

(Modes all 9, untied. s0 tail-Y reads 0 sites in deciles
0–5; all 51 pooled off-6+ sites outside dec-9 sit on m15:
0:13 / 1:12 / 3:19 / 4:5 / 5:2.)

Margin table: far dec-3's distance from the mode in rank
and share (rank = 1 + #deciles strictly above; ties
tabled via the histogram row above):

| Scope | n | dec-3 rank | dec-3 n | dec-3 share | mode n | mode share | gap n | gap share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 102 | 5 | 0 | 0.0000 | 92 | 0.9020 | 92 | 0.9020 |
| m15 | 134 | 2 | 19 | 0.1418 | 75 | 0.5597 | 56 | 0.4179 |
| shared | 69 | 3 | 0 | 0.0000 | 67 | 0.9710 | 67 | 0.9710 |
| pooled | 236 | 2 | 19 | 0.0805 | 167 | 0.7076 | 148 | 0.6271 |

(s0 dec-3 rank 5: four deciles above (9/8/7/6 at
92/6/2/2), six tied at 0. Shared dec-3 rank 3: deciles 9
and 8 above, eight tied at 0.)

Null-5 deciles' per-scope shares (null deciles 9 ×4 + 5;
dec-9 rows repeat the tail-decile table; dec-5 rows new):

| dec | s0 n/share | m15 n/share | shared n/share | pooled n/share |
| ---: | --- | --- | --- | --- |
| 9 | 92 / 0.9020 | 75 / 0.5597 | 67 / 0.9710 | 167 / 0.7076 |
| 5 | 0 / 0.0000 | 2 / 0.0149 | 0 / 0.0000 | 2 / 0.0085 |

(The m15 null's dec-5 is shared with 1 other m15 tail-Y
site pooled; 0 s0 tail sites read dec-5.)

Column table: decile seats by column for c343 + the 4 null
columns (313/332/314/311; per-site row:δ/dec):

| col | frame | n | sites (row:δ/dec) | dec-9 share | mode |
| ---: | --- | ---: | --- | ---: | ---: |
| 343 | s0 | 2 | 26:−31/d9 27:−26/d9 | 1.0000 | 9 |
| 343 | m15 | 4 | 25:−22/d9 26:−34/d9 27:−26/d9 289:−15/d3 | 0.7500 | 9 |
| 313 | s0 | 4 | 274:+18/d9 275:+19/d9 276:+8/d9 292:−16/d9 | 1.0000 | 9 |
| 313 | m15 | 5 | 338:+22/d3 339:+29/d1 340:+26/d4 378:+19/d3 379:+17/d4 | 0.0000 | 4 |
| 332 | s0 | 2 | 295:+10/d9 304:−12/d9 | 1.0000 | 9 |
| 332 | m15 | 0 | — | n/a | None |
| 314 | s0 | 7 | 269:+12/d9 276:+11/d6 277:+25/d8 278:+20/d9 287:−23/d9 288:−45/d9 289:−23/d9 | 0.7143 | 9 |
| 314 | m15 | 2 | 338:+24/d3 339:+15/d0 | 0.0000 | 3 |
| 311 | s0 | 4 | 296:−10/d9 297:−31/d9 298:−37/d7 299:−15/d9 | 0.7500 | 9 |
| 311 | m15 | 6 | 317:+9/d5 320:+22/d1 321:+20/d0 322:+10/d0 335:+46/d3 336:+22/d3 | 0.0000 | 3 |

Pooled splits (H7 input): c343 pooled n=6, dec-9 5/6 =
0.8333; null-4 (313/332/314/311) pooled n=30, dec-9 14/30
= 0.4667; |diff| = 0.3667.

(m15 null-column frames read 0 dec-9 on 313 (0/5), 314
(0/2), 311 (0/6); 332 has no m15 tail. s0 null-column
frames read 4/4, 2/2, 5/7, 3/4 dec-9.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-DEC1 M1–M6 (mode block) | dec 9 ×6, band 0 ×6, streak other ×6 | exact | True |
| C-DEC1 F1–F3 (off-mode block) | dec 3 ×3, band 0 ×3, streak other ×3 | exact | True |
| C-DEC1 E1–E3 (edge cols) | dec 6/7/8, band 0, streak other | exact | True |
| C-DEC1 hist (12 sites) | {3:3,6:1,7:1,8:1,9:6}, n=12, dec-9 0.5000, mode 9 @0.5000, rank-3 = 2 | exact | True |

(Carrier/peak N/A synthetic — no masks/cols, disclosed. 27
`match=True` lines + `pass=True`, exit 0. Full rows in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1+2 on s0+m15: seat-6 + context + d-dec +
histograms + margin + columns, fresh loads) pass1
`ac7cb03d…ed04b77` vs pass2 `ac7cb03d…ed04b77`,
identical=True; 43/43 lines match=True; cell counts
identical=True; tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not
explanation — no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes
tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_TAILMODE | pooled s0+m15 tail-Y dec-9 share ≥ 0.50 | 167/236 = 0.7076 — met |
| H2_S0MODE | s0 tail-Y dec-9 share ≥ 0.50 | 92/102 = 0.9020 — met |
| H3_M15MODE | m15 tail-Y dec-9 share ≥ 0.50 | 75/134 = 0.5597 — met |
| H4_FARDEC9 | pooled far sites with s0-P1 dec==9, share ≥ 0.50 | 0/1 = 0.0000 (dec 3) — not met |
| H5_NULLDEC9 | null-5 with s0-P1 dec==9, share ≥ 0.50 | 4/5 = 0.8000 — met |
| H6_FARUNIQUE | far decile differs from all 5 null deciles | 3 vs 9/9/9/9/5 — met |
| H7_COLDIFF | \|c343 pooled dec-9 − null-4 pooled dec-9\| ≥ 0.25 | \|0.8333−0.4667\| = 0.3667 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates
by reproduction (far seat + null-5 frame/col/row/d/δ/lo/hi
match M56 value-exactly; far band 1 / dec 3 / streak 343 /
carrier-none / 701-out / at-peak) and by seat-6 decile
split (far dec-3 alone vs nulls 9/9/9/9/5 — the two
off-9 seats are the two m15 sites; carrier/701 do not
split: 6/6 none/out; at-peak splits 1 far + 1 null vs 4
nulls). Task 2 discriminates by frame (s0 tail-Y 92/102
dec-9 with 0 sites in deciles 0–5 vs m15 tail-Y 75/134
dec-9 with off-mode mass 0:13/1:12/3:19/4:5/5:2; shared
67/69 dec-9), by margin (dec-3 pooled rank 2 at 19/236 vs
the 167/236 mode, gap 148; s0/shared dec-3 n=0), and by
column (pooled c343 5/6 dec-9 vs pooled null-4 14/30,
|diff| 0.3667; m15 null-column frames 0 dec-9 on 313/314/
311 vs s0 null-column frames 14/17 dec-9).

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

Screenshot: present by rule. The evidence decile map
(`m57-decmap.png`, 527 B of 5242880 budget) colors pooled
s0∪m15 tail-Y by decile class (red far 1 / yellow null-5 /
green dec-9 tail / gray other-decile tail); DESIGN.md
admits an evidence copy iff H6_FARUNIQUE meets (far
decile unique among seat-6) — far dec-3 vs nulls
9/9/9/9/5, met.

Recorded without verdict: the far seat reads m15 (289,343)
δ −15 d=262 band 1 dec 3 streak 343 carrier-none 701-out
at-peak with null-5 d 16/9/9/7/3 deciles 9/9/9/9/5; the
s0+m15 tail-Y reads pooled dec-9 167/236 (s0 92/102, m15
75/134, shared 67/69, Jaccard 0.4132) with dec-3 pooled
rank 2 at 19/236 (s0/shared n=0); c343 pooled reads 5/6
dec-9 vs null-4 pooled 14/30 (|diff| 0.3667); 0 B
explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| decile suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: seat-6 + M33-context + d-dec + tail hists + margin + columns + C-DEC1 control, bars H1–H7/N |
| seat-6 + histograms + margin + columns + wall/exit/shas/determinism | measured | §Step 2: 6 seats + M33 context + d-dec + 4 hists + margin + 10 col rows; 0.2 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained, 102 stands; gaps below |
| screenshot if a decile map discriminates (or absence reasoned) | measured | present by rule: H6 far-unique (3 vs 9/9/9/9/5); 527 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir —
§Runs):

```
mkdir -p "/Volumes/Extreme SSD/m57" local/research/M57
python3 -m py_compile local/research/M57/m57.py local/research/M57/control.py
cp local/research/M57/m57.py local/research/M57/control.py local/research/M57/DESIGN.md "/Volumes/Extreme SSD/m57/"
python3 "/Volumes/Extreme SSD/m57/m57.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m56/m56.txt" "/Volumes/Extreme SSD/m57" /Users/bradrichardson/dev/ssx3/local/research/M57 > "/Volumes/Extreme SSD/m57/m57.txt" 2>&1
python3 "/Volumes/Extreme SSD/m57/control.py" > "/Volumes/Extreme SSD/m57/control.txt" 2>&1
cp "/Volumes/Extreme SSD/m57/m57-decmap.png" local/research/M57/m57-decmap.png
```

## Paths

Evidence (committed): `local/research/M57/` — `DESIGN.md`
(suite + decile pins + bars, recorded before running),
`m57.py` (census + seat-6 + histograms + margin + columns +
PNG writer), `control.py` (known-decile synthetic control),
`m57-decmap.png` (decile map, 527 B, rule-met), `REPORT.md`
(this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m57/`
— `m57.txt` (receipt: shas, baselines, guards, census +
M56 guard, seat-6 + M33 context + d-dec, histograms +
margin + columns, bars, re-run, PNG size), `control.txt`,
`m57.py`, `control.py`, `DESIGN.md` (working copies),
`m57-decmap.png` (working copy, 527 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`,
`m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`,
`m43/`, `m44/`, `m45/`, `m46/`, `m47/`, `m48/`, `m49/`,
`m50/`, `m51/`, `m52/`, `m53/`, `m54/`, `m55/`, `m56/`, or
other agents' dirs.

## Gap rows (exact next brief each needs)

1. m15 off-mode decile mass (new): m15 tail-Y carries all 51
   pooled off-6+ non-9 sites (0:13 / 1:12 / 3:19 / 4:5 /
   5:2) while s0 tail-Y reads 0 in deciles 0–5 and shared
   reads 67/69 dec-9. Needs its own brief only if
   frame-asymmetric deciles matter: per-site m15 off-mode
   tables (row/col/δ/decile), offline — no new harness
   code.
2. m15 null-column dec-9 avoidance (new): m15 null-column
   frames read 0 dec-9 (313: 0/5 mode 4; 314: 0/2 mode 3;
   311: 0/6 mode 3; 332: no m15 tail) while their s0
   counterparts read 14/17 dec-9. Needs its own brief only
   if column-frame decile splits matter: per-column-frame
   decile census over all 33 union cols, offline — no new
   harness code.
3. Second pooled dec-5 site (new, minor): pooled dec-5 n=2
   (m15 2/134, s0/shared 0) — one is the m15 null
   (311,317); the other is unidentified this run. Needs its
   own brief only if the dec-5 pair matters: locate + value
   the pair, offline — no new harness code.
4. Hole bulk asymmetry (M56 gap 2, still open): m15's 28–288
   hole holds 1 bulk (r30 |δ|=1) vs s0's 8 bulk (r132–272,
   all |δ|=1), 0 tail either frame. Needs its own brief
   only if hole contents matter: per-hole-row bulk tables
   on c343, offline — no new harness code.
5. Null max d=16 (M56 gap 3, still open): the next-nearest
   non-far reads d=16 (s0 c313 r292), 246 rows below 289's
   262; the null-5 span d 16/9/9/7/3. Needs its own brief
   only if the near-far margin matters: threshold-sweep
   census (d≥50/25/10), offline — no new harness code.
6. Median-drift no-keep split (M55 gap 1, still open):
   |Δ|≤2 columns (296/321/342) keep 0 pooled CONST hits
   while the single kept hit sits on c340 (|Δ|=3). Needs
   its own brief only if drift-vs-survival matters:
   per-site cross-frame err tables joined with
   within-column δ spread, offline — no new harness code.
7. Median-below-peak offset (M55 gap 2, still open): 0/16
   col-frames read median==TRI peak h; med−h reads −1..−25,
   all negative. Needs its own brief only if median-peak
   offset matters: median-vs-hump-position tables, offline
   — no new harness code.
8. c340 transfer cluster (M55 gap 3, still open): both
   fit-s0→m15 nears + the single fit-m15→s0 hit + 1 of 4
   reverse nears all sit on c340. Needs its own brief only
   if column-local transfer matters: c340 site-level
   transfer census, offline — no new harness code.
9. M55 gaps 4–11, 13–27 (still open, by reference): see M55
   REPORT gaps 4–11, 13–27 for the exact brief each needs
   (interior-run failure; ragged-column miss; c343 span-264
   leverage; peak-seat asymmetry; low-drift no-keep;
   height-vs-edge legs; c340 peak-shift; peak-row/value
   split; SIGN near-hit mass; streak r-coherence; gap-bin
   32–63; POS collapse; 733 divergence; m15 privates;
   700 divergence; static-map disjointness; U/V co-residual;
   δ-sign; below-min tail; negatives; Odin port; top-HUD;
   carrier centers).

(Worked this run, dropped from the open list: M56 gap 1 /
289 dec-3 seat — the seat-6 + margin census above.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 decile status) are
   unscored — tabled scope, not chased.
2. No second-dec-5 identity: pooled dec-5 n=2 is tabled
   with 1 member (the m15 null); the other member's
   (row,col) is untabled (gap 3 above).
3. M33 histogram cited, not recomputed: the s0/s9 shared
   85/94 context column is M33's value by citation (this
   run's frames are s0/m15) — disclosed, not re-derived.
4. Control carrier/peak N/A: the pure-synthetic control
   recovers seats + histogram + shares + ranks exactly;
   carrier/peak need dumps/cols (N/A synthetic, disclosed).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M57/`: `DESIGN.md`, `m57.py`,
`control.py`, `m57-decmap.png`, `REPORT.md` (this file).
Total PNG 527 B.
