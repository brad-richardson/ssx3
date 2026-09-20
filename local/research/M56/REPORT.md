# M56 — m15 c343 row-289 site: far-row tail-site census: REPORT

M25 gap 3 (= M26 gap 6) worked at table level: the 289 site
reproduces exactly (m15 (289,343), δ −15, argmax peak 289,
TRI p=289, QUAD res 0, hole span 28–288) with the full value
row (|δ| 15, s0 noncell, gaps −32/0, signs −/0, band 1, dec 3,
streak 343, carrier none / 701-out) plus the far-row census
over all s0+m15 tail-Y sites at threshold d≥100 (nearest-
neighbor row gap within the same column same frame): 1 far
pooled (289 alone at d=262, c343 the only far-row column)
with the next-5 nearest as the null set (max d=16). Fully
offline — no lease of any kind, no boots, no harness code, no
`adb`. No device work. Runbook `local/muse/prompts/M56.md`.
Tables, no verdicts.

Headers read first: `local/research/M25/REPORT.md` (all of it:
m15 c343 rows [25,26,27,289], δ values, hole span 28–288,
peak 289; s0 c343 rows [26,27]; row→δ lists) plus
`local/research/M26/REPORT.md` (m15 c343 peak 289, TRI p=289)
plus `local/research/M51/REPORT.md` (r289 peak err_x −16; c343
kept hit = m15 r27) plus `local/research/M54/REPORT.md` (QUAD
near-flat fit res 0 at r289).

Time box 4 hours (start 2026-09-20 07:55 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m55/` — all outputs went to the new
`/Volumes/Extreme SSD/m56/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), the top-10 carrier
triplets (30 bins), and `m25.txt` (c343 rows + 289 site to
reproduce). Work dir `/Volumes/Extreme SSD/m56/`; evidence
`local/research/M56/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M55; `m25.txt` matches M26's record):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m25.txt | `dbbe5d66…567f63b3` |

(Full hexes in `m56.txt` §inputs, plus all 30 top-10-carrier
triplet bins. `m25.txt` 15578 B.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M55 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads 22815 on s0, equal. Mismatch rule
(DESIGN.md) not triggered.

## Runs (offline estimators)

One `m56.py` invocation (the receipt, 0.2 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try). DESIGN.md was
recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m56.py receipt | 0.2 s | exit 0; all guards pass; canon `511b821c…f07cdef` |
| control.py C-P1 (known far sites) | <1 s | green; 2 far + bands + singleton exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (c343 + 289 value + isolation) | 2 | in-pass |
| Task 2 (census + seats + columns) | 2 | in-pass |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m56.py` wall | — | 0.2 s |

## Step 2 — estimates

### Task 1 — 289-site reproduction (does the site reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M22/M23/M25/M26 EXACTLY,
and both c343 colguard + prof rowdelta + holes matching
`m25.txt` c343 lines value-exactly (stop rule not triggered).
Named-column bytes read 65 s0 / 68 m15. δ==0 count reads 0;
P(δ>0) reproduces M19/M20 0.8093/0.8019. Tail planes read
102/0/0 s0 and 134/0/0 m15 (Y/U/V). s0 P1 edges + all 10
carrier removed counts+bands match M18/M19 exactly.

c343 table: both frames' rows + δ + argmax + TRI + QUAD
(M51/M54 cited values reproduced? yes, all match=True):

| Frame | rows (n) | δ row order | argmax peak | TRI p/h/e/w | QUAD a/b/c + res |
| --- | --- | --- | --- | --- | --- |
| s0 | [26,27] (2) | −31 −26 | 27/−26 (mid) | 27/−26/−31/1 | CONST-fb med −29; res −2/+3 |
| m15 | [25,26,27,289] (4) | −22 −34 −26 −15 | 289/−15 (bottom) | 289/−15/−22/1 | +0.007831/−2.419882/+30.284514; res +3/−7/+3/+0 |

(Holes: s0 none; m15 28–288 ×261. m15 QUAD res at r289 = +0.
s0 QUAD CONST-fb (n=2). All TRI/QUAD pins match M51/M54
exactly.)

289 value row (|δ|, bulk status, signed gaps both frames, gap
signs, band + decile seats, streak/carrier):

| Field | Measured |
| --- | --- |
| offset / plane / (r,c) | 370606 / Y / (289,343) |
| m15 status / δ / \|δ\| | tail / −15 / 15 |
| s0 status / \|δ_s0\| | noncell / n/a |
| gaps g_m15 / g_s0 | −32 / 0 |
| gap equality signed / abs | False / False |
| gap signs m15/s0 (pair) | −/0 (−0) |
| band seat | 1 (r150–298) |
| decile seat (s0 P1) | 3 |
| streak seat | 343 (named) |
| carrier inside | none (n_in 0/10) |
| 701 split | out |

(s0 at the 289 offset reads static noncell: v0=mid=full=143,
gap 0 — tabled from the probe-free receipt path; m15 reads
v0=132 mid=133 full=164 syn=148 gap=−32.)

Isolation table: the 262-row gap itemized (nearest band row
above? nearest tail row below? hole contents?):

| Field | Measured |
| --- | --- |
| lo (nearest band row above) | 27 (δ −26) |
| hi (nearest tail row below) | None (289 is max) |
| d (nearest-neighbor) | 262 |
| hole span / count | 28–288 / 261 |
| d_out / d_lim / d_pool | 262 / 262 / 262 |
| hole m15 bulk/noncell/tail | 1 / 260 / 0 |
| hole m15 bulk rows (\|δ\|) | 30:1 |
| hole s0 bulk/noncell/tail | 8 / 253 / 0 |
| hole s0 bulk rows (\|δ\|) | 132:1 140:1 186:1 233:1 235:1 236:1 242:1 272:1 |

(All 9 hole bulk sites read \|δ\|=1, far below the tail
threshold 8; 0 tail sites in the hole on either frame.)

### Task 2 — far-row census (is 289 alone?)

Census table: all s0+m15 tail-Y sites with d≥100 (nearest-
neighbor row gap, FAR_THRESH=100 pinned; singletons N/A:
6 s0 + 8 m15 cols; non-far with d: 221 sites):

| Frame | col | row | d | δ | lo | hi | hole | d_out/d_lim/d_pool |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| m15 | 343 | 289 | 262 | −15 | 27 | None | 28–288×261 | 262/262/262 |

(Pooled far n=1: 289 alone. d_out/d_lim/d_pool all 262 —
edge far site, all three coincide.)

Null set (next-5 nearest non-far by d desc, REQUIRED since
far≤1; max non-far d=16):

| Frame | col | row | d | δ | lo | hi |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| s0 | 313 | 292 | 16 | −16 | 276 | None |
| s0 | 332 | 295 | 9 | +10 | None | 304 |
| s0 | 332 | 304 | 9 | −12 | 295 | None |
| s0 | 314 | 269 | 7 | +12 | None | 276 |
| m15 | 311 | 317 | 3 | +9 | None | 320 |

(246 rows separate 289's 262 from the null max 16.)

Seat table: each far site's band/decile/streak/carrier (do
far sites share seats? n=1, tabled):

| Frame | col | row | band | dec | streak | carrier_in | 701 | peak | atpeak |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- |
| m15 | 343 | 289 | 1 | 3 | 343 | none | out | 289 | True |

Column table: far-site counts by column (is c343 the only
far-row column? yes — 1/33 union cols; full 33-col table):

| col | s0_n | m15_n | s0_far | m15_far | pooled |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 38 | 1 | 0 | 0 | 0 | 0 |
| 65 | 0 | 2 | 0 | 0 | 0 |
| 76 | 0 | 1 | 0 | 0 | 0 |
| 257 | 10 | 10 | 0 | 0 | 0 |
| 277 | 10 | 10 | 0 | 0 | 0 |
| 289 | 0 | 2 | 0 | 0 | 0 |
| 292 | 1 | 0 | 0 | 0 | 0 |
| 293 | 1 | 0 | 0 | 0 | 0 |
| 296 | 9 | 9 | 0 | 0 | 0 |
| 298 | 4 | 7 | 0 | 0 | 0 |
| 299 | 0 | 1 | 0 | 0 | 0 |
| 301 | 11 | 11 | 0 | 0 | 0 |
| 306 | 0 | 2 | 0 | 0 | 0 |
| 307 | 1 | 1 | 0 | 0 | 0 |
| 308 | 0 | 2 | 0 | 0 | 0 |
| 309 | 0 | 2 | 0 | 0 | 0 |
| 310 | 0 | 1 | 0 | 0 | 0 |
| 311 | 4 | 6 | 0 | 0 | 0 |
| 312 | 3 | 23 | 0 | 0 | 0 |
| 313 | 4 | 5 | 0 | 0 | 0 |
| 314 | 7 | 2 | 0 | 0 | 0 |
| 315 | 7 | 5 | 0 | 0 | 0 |
| 316 | 1 | 0 | 0 | 0 | 0 |
| 321 | 10 | 10 | 0 | 0 | 0 |
| 332 | 2 | 0 | 0 | 0 | 0 |
| 340 | 8 | 9 | 0 | 0 | 0 |
| 341 | 0 | 1 | 0 | 0 | 0 |
| 342 | 5 | 5 | 0 | 0 | 0 |
| 343 | 2 | 4 | 0 | 1 | 1 |
| 344 | 0 | 1 | 0 | 0 | 0 |
| 353 | 0 | 1 | 0 | 0 | 0 |
| 372 | 1 | 0 | 0 | 0 | 0 |
| 617 | 0 | 1 | 0 | 0 | 0 |

(Distinct far cols 1 ([343]); union tail-Y cols 33 (21 s0 +
27 m15); singleton cols 6 s0 (38/292/293/307/316/372) + 8
m15 (76/299/307/310/341/344/353/617).)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 F1 (c343-mirror 25,26,27,289) | d 1/1/1/262, far [289], hole 28–288×261, band 0/0/0/1, peak 289, atpeak True | exact | True |
| C-P1 F2 (second far 30,31,200) | d 1/1/169, far [200], hole 32–199×168, band 0/0/1, peak 31, atpeak False | exact | True |
| C-P1 B1 (band 23–27) | d all 1, far [], band all 0, peak 25 | exact | True |
| C-P1 S1 (singleton 100) | d N/A, far [], singleton, band 0, peak 100 | exact | True |
| C-P1 pooled | far 2 (289 d262 + 200 d169), cols [257,343], null top-5 all d=1 | exact | True |

(Decile/carrier N/A synthetic — no dumps, disclosed. Full
tables in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: c343 + TRI/QUAD + 289 value +
isolation, fresh loads) pass1 `511b821c…f07cdef` vs pass2
`511b821c…f07cdef`, identical=True; 23/23 lines match=True;
cell counts identical=True; tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_FARONE | pooled far (d≥100) count == 1 | 1 (m15 c343 r289 d262) — met |
| H2_FARCOL | distinct far columns == 1 | 1 ([343]) — met |
| H3_ISOLATED | largest non-far d ≤ 50 | 16 (s0 c313 r292) — met |
| H4_FARNEG | far sites with δ<0, share ≥ 0.50 | 1/1 = 1.0000 — met |
| H5_FARDEC9 | far sites with s0-P1 dec==9, share ≥ 0.50 | 0/1 = 0.0000 (dec 3) — not met |
| H6_FARBAND1 | far sites with band==1, share ≥ 0.50 | 1/1 = 1.0000 — met |
| H7_FARPEAK | far sites at column-frame argmax, share ≥ 0.50 | 1/1 = 1.0000 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (c343 rows/δ/holes/peak match M25/M26 value-
exactly on both frames; TRI 27/289 + QUAD +0.01/res-0 match
M51/M54 exactly) and by hole content (m15 hole 1 bulk at
r30 \|δ\|=1 vs s0 hole 8 bulk all \|δ\|=1, 0 tail either
frame). Task 2 discriminates by count (1 far pooled of 236
tail-Y sites with 14 singletons N/A + 221 non-far), by
column (1/33 union cols, c343 only), by distance (262 vs
null max 16, 246-row margin), and by seat (band 1 / dec 3 /
streak 343 / carrier-none / at-peak — dec 3 off the tail's
dec-9 mode).

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

Screenshot: absent by rule. The workdir far-row map
(`m56-farmap.png`, 450 B) colors m15 tail-Y by far outcome
(red far 1 / green band 119 / gray singleton 8), but
DESIGN.md admits an evidence copy only if pooled far count
≥ 2 (max reads 1: 289 alone) — no pre-registered split
qualifies, so no evidence copy is committed (0 B of 5242880
budget). The workdir copy is retained, uncommitted.

Recorded without verdict: m15 c343 reads rows [25,26,27,289]
with δ −22/−34/−26/−15, peak 289, TRI 289/−15/−22/1, QUAD
+0.01 with res +3/−7/+3/+0, hole 28–288; the 289 site reads
\|δ\| 15 with s0 noncell, gaps −32/0 (−/0), band 1, dec 3,
streak 343, carrier-none, 701-out, lo 27 / hi none / d 262,
hole bulk 1/8 at \|δ\|=1; the s0+m15 census reads 1 far
pooled (c343 only) with null max 16 across 221 non-far
sites and 14 singletons; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| far suite + threshold + falsification bars, recorded before running | recorded | `DESIGN.md`: d≥100 nearest-neighbor + singleton-N/A + per-frame primary + pooled auxiliary + null-5 + s0-anchored seats + TRI/QUAD pins, bars H1–H7/N |
| c343 table + 289 value row + isolation + wall/exit/shas/determinism | measured | §Step 2: c343 both frames + TRI/QUAD match + 289 row + 262-gap isolation; 0.2 s; re-run identical |
| far census + seats + columns + explained-vs-standing + gap rows | measured | §Step 2/3: 1 far + null-5 + seats + 33-col table; 0 explained, 102 stands; gaps below |
| screenshot if a far-row map discriminates (or absence reasoned) | measured | absent by rule: far 1 at n≥2 rule (want ≥2); workdir copy only, 450 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the repo
root for staging, receipt redirect to the work dir — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m56" local/research/M56
python3 -m py_compile local/research/M56/m56.py local/research/M56/control.py
cp local/research/M56/m56.py local/research/M56/control.py local/research/M56/DESIGN.md "/Volumes/Extreme SSD/m56/"
python3 "/Volumes/Extreme SSD/m56/m56.py" "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m25/m25.txt" "/Volumes/Extreme SSD/m56" /Users/bradrichardson/dev/ssx3/local/research/M56 > "/Volumes/Extreme SSD/m56/m56.txt" 2>&1
python3 "/Volumes/Extreme SSD/m56/control.py" > "/Volumes/Extreme SSD/m56/control.txt" 2>&1
```

## Paths

Evidence (committed): `local/research/M56/` — `DESIGN.md`
(suite + far pins + bars, recorded before running), `m56.py`
(c343 + 289 value + isolation + census + seats + PNG writer),
`control.py` (known-far synthetic control), `REPORT.md` (this
file). No PNG committed (absence reasoned above).

Large outputs (not committed): `/Volumes/Extreme SSD/m56/` —
`m56.txt` (receipt: shas, baselines, guards, Task-1 c343 both
frames, TRI/QUAD compare, 289 value + isolation, Task-2 census
+ null + seats + 33-col table, re-run, PNG size),
`control.txt`, `m56.py`, `control.py`, `DESIGN.md` (working
copies), `m56-farmap.png` (working copy, 450 B). No writes
into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`,
`m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`,
`m38/`, `m39/`, `m40/`, `m41/`, `m42/`, `m43/`, `m44/`, `m45/`,
`m46/`, `m47/`, `m48/`, `m49/`, `m50/`, `m51/`, `m52/`, `m53/`,
`m54/`, `m55/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. 289 dec-3 seat (new): the far site reads s0-P1 decile 3
   while tail seats read dec-9 heavy (M33 shared 85/94
   dec-9; H5 0/1). Needs its own brief only if far-seat
   decile matters: decile seats of far vs null-5 sites,
   offline — no new harness code.
2. Hole bulk asymmetry (new): m15's 28–288 hole holds 1 bulk
   (r30 \|δ\|=1) vs s0's 8 bulk (r132–272, all \|δ\|=1),
   0 tail either frame. Needs its own brief only if hole
   contents matter: per-hole-row bulk tables on c343,
   offline — no new harness code.
3. Null max d=16 (new): the next-nearest non-far reads d=16
   (s0 c313 r292), 246 rows below 289's 262; the null-5
   span d 16/9/9/7/3. Needs its own brief only if the
   near-far margin matters: threshold-sweep census
   (d≥50/25/10), offline — no new harness code.
4. Median-drift no-keep split (M55 gap 1, still open):
   |Δ|≤2 columns (296/321/342) keep 0 pooled CONST hits
   while the single kept hit sits on c340 (|Δ|=3). Needs
   its own brief only if drift-vs-survival matters:
   per-site cross-frame err tables joined with
   within-column δ spread, offline — no new harness code.
5. Median-below-peak offset (M55 gap 2, still open): 0/16
   col-frames read median==TRI peak h; med−h reads −1..−25,
   all negative. Needs its own brief only if median-peak
   offset matters: median-vs-hump-position tables, offline
   — no new harness code.
6. c340 transfer cluster (M55 gap 3, still open): both
   fit-s0→m15 nears + the single fit-m15→s0 hit + 1 of 4
   reverse nears all sit on c340. Needs its own brief only
   if column-local transfer matters: c340 site-level
   transfer census, offline — no new harness code.
7. M55 gaps 4–11, 13–27 (still open, by reference): see M55
   REPORT gaps 4–11, 13–27 for the exact brief each needs
   (interior-run failure; ragged-column miss; c343 span-264
   leverage; peak-seat asymmetry; low-drift no-keep;
   height-vs-edge legs; c340 peak-shift; peak-row/value
   split; SIGN near-hit mass; streak r-coherence; gap-bin
   32–63; POS collapse; 733 divergence; m15 privates;
   700 divergence; static-map disjointness; U/V co-residual;
   δ-sign; below-min tail; negatives; Odin port; top-HUD;
   carrier centers).

(Worked this run, dropped from the open list: M55 gap 12 /
M54 gap 10 / M53 gap 9 / M51 gap 8 / M26 gap 6 / M25 gap 3 —
m15 c343 row-289 site, the far-row census above.)

## What I could not do

1. No cross-shape check: the brief asks s0+m15 only, so
   shapes 1–764 (incl. 9/700/733 far-row status) are
   unscored — tabled scope, not chased.
2. No threshold sweep: the census pins FAR_THRESH=100;
   d≥50/25/10 counts are untabled (gap 3 above).
3. Singletons N/A: 6 s0 + 8 m15 singleton-column sites carry
   no d by construction (no band) — excluded from the
   far/null ranking, tabled as such.
4. Control decile/carrier N/A: the pure-synthetic control
   recovers census + \|δ\| + band + peak seats exactly;
   gaps/decile/carrier need dumps (N/A synthetic,
   disclosed).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M56/`: `DESIGN.md`, `m56.py`,
`control.py`, `REPORT.md` (this file). No PNG (0 B).
