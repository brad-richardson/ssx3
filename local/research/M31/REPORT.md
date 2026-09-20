# M31 — K-boundary sweep: K ∈ {0,1} below + {15,20,50,100} above: REPORT

M30 gap 1 worked at table level: the K=2 windowed census
recomputed from the dumps reads 8 movers / 13 cells / standings
matching M30 exactly (TSV sha `471f2862…85e30b6a7`
byte-identical to `m30-census-K2.tsv`, 13/13 cell rows,
stop rule not triggered); the sweep over the DESIGN-fixed K ∈
{0, 1, 15, 20, 50, 100} reads 8 movers at every K with 12 cells
at K=0 and 13 cells at every K≥1 (the K=1/15/20/50/100 TSVs
byte-identical to the K=2 recompute; M30's K5/K10 TSV shas
equal the same bytes); the off-span tail is 5 sites (far 3 +
734-c342's 2 d=1 extras) at K=0 and exactly the 3 far extras
at every K≥1; the full ordered diff list
{exact,0,1,2,5,10,15,20,50,100} flips 3 cells on exact→0, 1
cell (734-c342) on 0→1, and 0 cells on all 7 remaining pairs
(no real-data flip anywhere in K=1..100); the extras-distance
census over all 764 finds exactly 5 extra sites
(d=1×2, d+234, d+366, d+367 — no d=2 extras, no other d≤2
sites); the below-0.95 join reads 5/3/4/752 at every computed
K and at K=5,10 from the loaded TSVs. Fully offline — no lease
of any kind, no boots, no harness code, no `adb`. No device
work. Runbook `local/muse/prompts/M31.md`. Tables, no verdicts.

Headers read first: `local/research/M30/REPORT.md` (all of it:
8 movers / 13 cells at every K in {2,5,10}, row-identical; the
three TSVs byte-identical; off-span exactly the 3 far extras;
0 flipping cells on both adjacent pairs; gap 1 is this brief)
plus `local/research/M30/DESIGN.md` (the ±K window definition,
reused verbatim).

Time box 4 hours (start 2026-09-20 03:40 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m30/` — all outputs went to the new
`/Volumes/Extreme SSD/m31/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), `m28.txt` +
`m28-census.tsv` (exact-match guard), and `m30.txt` +
`m30-census-K2/5/10.tsv` (K=2 reproduction target + K=5,10
diff inputs). Work dir `/Volumes/Extreme SSD/m31/`; evidence
`local/research/M31/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M30; m30 K2/K5/K10 shas equal each other):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…c8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0009 | `1926a151…086fe0` |
| m16-mid-s0009 | `a9fa67fb…5e9806` |
| m16-full-s0009 | `a9a5339d…7ae486` |
| m16-v0-s0022 | `09dd96f3…274439` |
| m16-mid-s0022 | `5e05bc20…758688` |
| m16-full-s0022 | `ed846091…0d8bf3` |
| m16-v0-s0734 | `82467b1f…bddbb2` |
| m16-mid-s0734 | `45de5504…977d26` |
| m16-full-s0734 | `f60ddd16…38600f` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…e20284` |
| m15-full | `b4053af3…c2426a` |
| m28.txt | `87a12157…8faf25` |
| m28-census.tsv | `27872527…5a9e7f` |
| m30.txt | `8bc64599…4492c3` |
| m30-census-K2.tsv | `471f2862…30b6a7` |
| m30-census-K5.tsv | `471f2862…30b6a7` |
| m30-census-K10.tsv | `471f2862…30b6a7` |

(Full hexes in `m31.txt` §inputs: 72 input lines — s0 + all 10
M28 movers + m15 + top-10 carrier triplets + `m28.txt` +
`m28-census.tsv` + `m30.txt` + `m30-census-K2/5/10.tsv`.
Triplet fold sha over all 764×3 bins:
`6c906897…61fd423b1` — matches M28/M29/M30 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M30 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 reference
row lists + guard-only c341 n=0 match exactly. M28 TSV match
on all 764 (bad=0: tail + J4 + all-8-column n/ov/pres) +
mover list == the M28 10 + 15/15 move standings match
`m28.txt` + below-0.95 9-list tail+J4 exact. Window geometry:
dist-rows == span-interval on all 8 columns at every K≥2
(40/40 interval-match); the 5 pre-registered K=0/K=1
hole-row exclusions tabled in §Task 2.1 (c296/c340/c342 at
K=0; c340/c342 at K=1 — DESIGN-expected, not a failure). s0
windowed-present on all 8 at every computed K. Partition
(in-window + off-span + outside-census == tail) holds on all
764 per computed K (0 violations). K=2 gate (DESIGN.md) not
triggered: 8 movers / 13 cells / standings + TSV bytes all
match M30. M30 K5/K10 TSV shas equal the K=2 recompute sha
(diff legs verified, not assumed).

## Runs (offline estimators)

One `m31.py` invocation (the receipt, 6.6 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m31.py receipt | 6.6 s | exit 0; all guards pass; canon `ac6a3780…fc4d1263` |
| control.py C0–C234 | <1 s | green; windowed standings + off-span exact on all 6 |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + census fields) | 764 | 5.6 s |
| Exact-match M28 guard (TSV + movers + standings) | 764 | 0.0 s |
| Task 1 (K=2 gate + windowed re-run per K + TSVs) | 764 × 7 | 0.7 s |
| Task 1.2/1.3 + Task 2 (off-span + deltas + joins + diffs) | — | 0.0 s |
| Determinism re-run (Task 1 K=2 on s0+9+22) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m31.py` wall | — | 6.6 s |

## Step 2 — estimates

### Task 1 — the sweep (fixed K ∈ {0, 1, 15, 20, 50, 100} + K=2 gate)

K=2 gate detail (recomputed vs M30 — stop rule not
triggered): movers [708,709,710,711,731,732,733,734] (8/8);
moved cells 13/13 with standings + dests:

| Shape | col | n_K/ov_K | standing | dest | match |
| ---: | ---: | --- | --- | ---: | --- |
| 708 | 296 | 8/8 | none(no-cand) | — | True |
| 709 | 301 | 10/10 | none(no-cand) | — | True |
| 710 | 340 | 6/6 | none(no-cand) | — | True |
| 711 | 342 | 0/0 | none(no-cand) | — | True |
| 711 | 343 | 0/0 | none(no-cand) | — | True |
| 731 | 257 | 0/0 | ok | 259 | True |
| 731 | 277 | 0/0 | ok | 279 | True |
| 732 | 296 | 0/0 | ok | 298 | True |
| 733 | 301 | 0/0 | ok | 303 | True |
| 733 | 321 | 0/0 | ok | 323 | True |
| 734 | 340 | 0/0 | ok | 342 | True |
| 734 | 342 | 7/5 | none(extra-only) | — | True |
| 734 | 343 | 0/0 | ok | 342 | True |

TSV bytes: recomputed K=2 sha == M30 K2 sha
(`471f2862…85e30b6a7`), identical=True. (Offsets/rshifts
re-verify M30's: +2/+2/+2/+2/+2/+2/−1 and
+1.5/+1.5/−1.5/+1.0/+2.0/+0.5/+3.0.)

Windowed movers / moved cells per computed K (full 764×8
matrices committed as `m31-census-K0/1/15/20/50/100.tsv`,
54295 B each; K=2 matrix in the work dir only,
sha-recorded above):

| K | movers (n) | shape list | cells (n) |
| --- | ---: | --- | ---: |
| 0 | 8 | [708,709,710,711,731,732,733,734] | 12 |
| 1 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 2 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 15 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 20 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 50 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 100 | 8 | [708,709,710,711,731,732,733,734] | 13 |

TSV identity: K=1/2/15/20/50/100 shas all
`471f2862…85e30b6a7` (K=1 vs K=2 vs K=15 `cmp` byte-identical);
K=0 sha `f459e623…636a2d2` (differs by the 734-c342 row).
M30's K5/K10 input shas equal the same `471f2862…` bytes
(§Baseline note).

Full per-cell windowed table at K=0 (12 rows; the only K
whose table differs):

| Shape | col | n_K/ov_K | standing | dest | off | rshift |
| ---: | ---: | --- | --- | ---: | ---: | ---: |
| 708 | 296 | 8/8 | none(no-cand) | — | — | — |
| 709 | 301 | 10/10 | none(no-cand) | — | — | — |
| 710 | 340 | 6/6 | none(no-cand) | — | — | — |
| 711 | 342 | 0/0 | none(no-cand) | — | — | — |
| 711 | 343 | 0/0 | none(no-cand) | — | — | — |
| 731 | 257 | 0/0 | ok | 259 | +2 | +1.5 |
| 731 | 277 | 0/0 | ok | 279 | +2 | +1.5 |
| 732 | 296 | 0/0 | ok | 298 | +2 | −1.5 |
| 733 | 301 | 0/0 | ok | 303 | +2 | +1.0 |
| 733 | 321 | 0/0 | ok | 323 | +2 | +2.0 |
| 734 | 340 | 0/0 | ok | 342 | +2 | +0.5 |
| 734 | 343 | 0/0 | ok | 342 | −1 | +3.0 |

(734-c342 at K=0: n_K/ov_K 5/5, present — §Task 2.1.)

Full per-cell windowed table at K=1/15/20/50/100 (13 rows;
byte-identical TSVs to the K=2 gate table above — the same 13
rows with the same n_K/ov_K/standings/dests/offsets/rshifts;
K=5/10 pres rows from M30's TSVs verified sha-identical):

| Shape | col | n_K/ov_K | standing | dest | off | rshift |
| ---: | ---: | --- | --- | ---: | ---: | ---: |
| 708 | 296 | 8/8 | none(no-cand) | — | — | — |
| 709 | 301 | 10/10 | none(no-cand) | — | — | — |
| 710 | 340 | 6/6 | none(no-cand) | — | — | — |
| 711 | 342 | 0/0 | none(no-cand) | — | — | — |
| 711 | 343 | 0/0 | none(no-cand) | — | — | — |
| 731 | 257 | 0/0 | ok | 259 | +2 | +1.5 |
| 731 | 277 | 0/0 | ok | 279 | +2 | +1.5 |
| 732 | 296 | 0/0 | ok | 298 | +2 | −1.5 |
| 733 | 301 | 0/0 | ok | 303 | +2 | +1.0 |
| 733 | 321 | 0/0 | ok | 323 | +2 | +2.0 |
| 734 | 340 | 0/0 | ok | 342 | +2 | +0.5 |
| 734 | 342 | 7/5 | none(extra-only) | — | — | — |
| 734 | 343 | 0/0 | ok | 342 | −1 | +3.0 |

Per-column windowed mover counts (K=0 vs every K≥1 — the only
column that differs is c342):

| col | K=0 movers | K≥1 movers |
| ---: | --- | --- |
| 257 | 1: [731] | 1: [731] |
| 277 | 1: [731] | 1: [731] |
| 296 | 2: [708, 732] | 2: [708, 732] |
| 301 | 2: [709, 733] | 2: [709, 733] |
| 321 | 1: [733] | 1: [733] |
| 340 | 2: [710, 734] | 2: [710, 734] |
| 342 | 1: [711] | 2: [711, 734] |
| 343 | 2: [711, 734] | 2: [711, 734] |

Off-span tail tables per computed K (5 sites at K=0; exactly
the 3 far extras at every K≥1; no 4th/6th off-span site in any
of the 764 at any computed K):

| K | shapes | pooled sites | per-shape rows |
| --- | ---: | ---: | --- |
| 0 | 3 | 5 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367); s734: c342 r26 (d+1), r33 (d+1) |
| 1 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 2 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 15 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 20 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 50 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 100 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |

Outside-census (non-named-column) tail per M28 mover
(K-invariant by construction; matches M30's table):

| Shape | nout | tail |
| ---: | ---: | ---: |
| 9 | 51 | 117 |
| 22 | 39 | 106 |
| 708 | 37 | 101 |
| 709 | 33 | 97 |
| 710 | 37 | 100 |
| 711 | 37 | 95 |
| 731 | 55 | 100 |
| 732 | 39 | 95 |
| 733 | 56 | 100 |
| 734 | 37 | 94 |

Adjacent-K diffs across the FULL ordered list
{exact,0,1,2,5,10,15,20,50,100} (9 pairs — the stability
margin, tabled):

| Pair | flipping cells | mover flips | identical |
| --- | ---: | ---: | --- |
| exact→0 | 3: (9,c321→present), (22,c296→present), (734,c342→present) | 2: 9, 22 un-move | False |
| 0→1 | 1: (734,c342→moved) | 0 | True |
| 1→2 | 0 | 0 | True |
| 2→5 | 0 | 0 | True |
| 5→10 | 0 | 0 | True |
| 10→15 | 0 | 0 | True |
| 15→20 | 0 | 0 | True |
| 20→50 | 0 | 0 | True |
| 50→100 | 0 | 0 | True |

### Task 2 — boundary analysis (where does the rule bite?)

Lower boundary: 734-c342's d=1 extras across K=0/1/2:

| Site | K=0 | K=1 | K=2 |
| --- | --- | --- | --- |
| r26 (d+1) in-window? | False (off-span) | True | True |
| r33 (d+1) in-window? | False (off-span) | True | True |
| 734-c342 n_K/ov_K/pres_K | 5/5/present | 7/5/extra-only | 7/5/extra-only |

Extras-distance census over all 764 shapes × 8 named columns
(every named-column extra site with its span distance — the
d≤2 confirm):

| Measure | Value |
| --- | --- |
| pooled extra sites | 5 on shapes [9, 22, 734] |
| distance histogram | d=1×2, d+234×1, d+366×1, d+367×1 |
| per-site rows | s9 c321 r266 d+234; s22 c296 r400 d+366, r401 d+367; s734 c342 r26 d+1, r33 d+1 |
| other d≤2 sites | none (no d=2 extras anywhere in the 764) |
| pooled missing rows | 71 (all d=0 by construction) |

Window geometry (dist-rows vs span-interval per column per
computed K — the 5 DESIGN-expected K=0/K=1 exclusions;
interval-match True on all 8 columns at every K≥2):

| K | col | span | win | interval-match | excluded hole rows |
| ---: | ---: | --- | --- | --- | --- |
| 0 | 296 | [24,34] | [24,34] | False | [29, 30] |
| 0 | 340 | [24,34] | [24,34] | False | [28, 29, 30] |
| 0 | 342 | [27,35] | [27,35] | False | [30, 31, 32, 33] |
| 1 | 340 | [24,34] | [23,35] | False | [29] |
| 1 | 342 | [27,35] | [26,36] | False | [31, 32] |

(All other (K, col) pairs: interval-match True.)

Upper boundary: first real-data flip at K>10:

| Upper leg | flipping cells | mover flips |
| --- | ---: | ---: |
| 10→15 | 0 | 0 |
| 15→20 | 0 | 0 |
| 20→50 | 0 | 0 |
| 50→100 | 0 | 0 |

First real-data flip at K>10: None (negative through K=100).

Minimum K that WOULD admit each off-span site (computed, not
run — union of off-span sites across computed Ks):

| Site | d | min admitting K |
| --- | ---: | ---: |
| s734 c342 r26 | +1 | 1 |
| s734 c342 r33 | +1 | 1 |
| s9 c321 r266 | +234 | 234 |
| s22 c296 r400 | +366 | 366 |
| s22 c296 r401 | +367 | 367 |

Standing stability (exact + per K; K=5,10 movers/cells from
M30's sha-verified TSVs):

| Rule | movers | cells | assigned | extra-only | no-cand |
| --- | ---: | ---: | ---: | ---: | ---: |
| exact | 10 | 15 | 7 | 3 | 5 |
| K=0 | 8 | 12 | 7 | 0 | 5 |
| K=1 | 8 | 13 | 7 | 1 | 5 |
| K=2 | 8 | 13 | 7 | 1 | 5 |
| K=5 | 8 | 13 | per-M30 (TSV-identical) | — | — |
| K=10 | 8 | 13 | per-M30 (TSV-identical) | — | — |
| K=15 | 8 | 13 | 7 | 1 | 5 |
| K=20 | 8 | 13 | 7 | 1 | 5 |
| K=50 | 8 | 13 | 7 | 1 | 5 |
| K=100 | 8 | 13 | 7 | 1 | 5 |

Below-0.95 join per K (J values unchanged; exact + windowed
2×2 — windowed identical at every computed K and at K=5,10):

|  | below-0.95 | above-0.95 |
| --- | --- | --- |
| exact mover | 6: 9, 711, 731, 732, 733, 734 | 4: 22, 708, 709, 710 |
| exact still | 3: 2, 3, 700 | 751 |
| K mover (every K 0–100) | 5: 711, 731, 732, 733, 734 | 3: 708, 709, 710 |
| K still (every K 0–100) | 4: 2, 3, 9, 700 | 752 |

(No K moves a shape across the mover line: the join is
5/3/4/752 at K=0,1,2,5,10,15,20,50,100 alike.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C0 (c340 −r24, d=0) | moved every K, missK=1, no-cand, off empty | exact | True |
| C1 (c342 +r26, d=1) | present + off {(342,26)} K=0; extra-only 6/5, off empty, K≥1 | exact | True |
| C2 (c342 +r31, d=2) | present + off {(342,31)} K=0,1; extra-only 6/5, off empty, K≥2 | exact | True |
| C7 (c296 +r41, d=7) | present + off {(296,41)} K=0,1,2; extra-only 10/9, off empty, K≥15 | exact | True |
| C15 (c296 +r49, d=15) | present + off {(296,49)} K=0,1,2; extra-only 10/9, off empty, K≥15 | exact | True |
| C234 (c321 +r266, d+234) | present + off {(321,266)} every K | exact | True |

(Full per-K rows in `control.txt`. C1/C2 bracket the observed
real-data lower flip (d=1 in, d=2 absent); C7/C15 bracket the
unobserved upper region (flip thresholds K≥7/K≥15, computed
grid straddles them); C234 pins the far tail (K≥234 to admit).
C7's analytic flip threshold K≥7 sits between computed grid
points 2 and 15 — computed, not run.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 K=2 windowed census on s0+9+22, fresh loads)
pass1 `ac6a3780…fc4d1263` vs pass2 `ac6a3780…fc4d1263`,
identical=True; 3/3 lines match=True; windowed mover sets
s0=[] s9=[] s22=[] identical.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| B1_K2REPRO | K=2 reads 8 movers / 13 cells / M30 standings + TSV bytes | 8/13 + 13/13 rows + sha-identical — met (gate) |
| B2_LOWIN | 734-c342's 2 d=1 extras in-window at K=1 | 2/2 — met |
| B3_LOWOUT | 734-c342's 2 d=1 extras off-span at K=0 | 2/2 — met |
| B4_K0SET | K=0 mover set == K=2 8-shape set | identical — met |
| B5_K1EQK2 | K=1 census row-identical to K=2 | 0 pres-flips, 0 offspan-symdiff, standings identical, TSV bytes identical — met |
| B6_UPSTABLE | 0 flipping cells + 0 mover flips on 10→15→20→50→100 | 0/True on all 4 legs — met |
| B7_OFF100 | off-span at K=100 exactly the 3 far extras | 3 sites == far-3 — met |
| B8_BELOW95 | windowed movers below-0.95 share ≥ 0.50 every computed K | 5/8 = 0.6250 at all 7 — met |
| B9_MISSIN | 4/4 missing rows in-window every computed K incl. K=0 | 4/4 at all 7 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
the K=0 lower flip (734-c342's 2 d=1 extras leave the census
at K=0 — the only cell in the 764 whose standing changes
below K=1 — while 9 + 22 stay un-moved at every computed K,
so K=0 keeps the K=2 mover set with 12 cells and 0
extra-only); by off-span scope (5 sites on 3 shapes at K=0,
exactly the far 3 on 2 shapes at every K≥1 — the extras
census confirms these are the only 5 extra sites in the 764,
with nothing at d=2); and by geometry (the 5 pre-registered
K=0/K=1 hole-row exclusions, interval-match everywhere else).
Task 2 discriminates the stability margin exactly: the rule
bites only twice on real data — exact→0 (3 cells: the far-2
shapes plus 734-c342 go present) and 0→1 (734-c342 returns) —
with 0 flips on all 7 pairs spanning K=1..100; the upper
boundary is a tabled negative (first flip None through
K=100; the nearest would-be flip needs K≥234, computed not
run); the join never moves (5/3/4/752 at all 9 K rules).

Stability-margin summary as a TABLE (per-K
movers/cells/off-span/join — no verdict):

| K | movers/cells | standings (a/e/n) | off-span (shapes/sites) | join (mb/ma/sb/sa) | flips vs next |
| --- | ---: | --- | ---: | --- | ---: |
| exact (no window) | 10/15 | 7/3/5 | n/a | 6/4/3/751 | 3 cells, 2 movers (vs 0) |
| 0 | 8/12 | 7/0/5 | 3/5 | 5/3/4/752 | 1 cell, 0 movers (vs 1) |
| 1 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 2) |
| 2 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 5) |
| 5 | 8/13 | per-M30 | 2/3 (M30) | 5/3/4/752 | 0 (vs 10) |
| 10 | 8/13 | per-M30 | 2/3 (M30) | 5/3/4/752 | 0 (vs 15) |
| 15 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 20) |
| 20 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 50) |
| 50 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 100) |
| 100 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | — |

(K=5,10 standings/off-span per M30, whose TSVs verify
sha-identical to the K=2 recompute.)

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; K-boundary tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence K-sweep cell map
(`m31-cellmap.png`, 435 B of 5242880 budget) colors
exact + 0/1/2/5/10/15/20/50/100 presence per (mover, col) cell
(green = present, magenta = moved); DESIGN.md admits an
evidence copy iff B3 meets AND B2 meets — B3 meets (2/2
off-span at K=0) with B2 meets (2/2 in-window at K=1), the
K=0 lower-boundary exclusion visible in the pre-registered
K0-vs-K1 cell split.

Recorded without verdict: K=2 reproduces M30 exactly (stop
rule not triggered); the sweep reads 8 movers at every K with
the single lower flip at 734-c342 between K=0 (present, 12
cells, 0 extra-only, 5 off-span sites) and K=1 (extra-only,
13 cells, 3 off-span sites); K=1..100 is one flat plateau (0
flips on all 7 pairs, byte-identical TSVs, join 5/3/4/752
throughout); the extras census finds exactly 5 extra sites
with nothing at d=2; the upper boundary is negative through
K=100 with the nearest would-be flip at K≥234; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| K-boundary sweep + falsification bars + fixed K list, recorded before running | recorded | `DESIGN.md`: M30-verbatim ±K window + off-span + outside-census partition, M28-verbatim standings on windowed miss/extra, C0–C234 controls, bars B1–B9/N, K ∈ {0,1,15,20,50,100} + K=2 gate |
| windowed census + off-span + full ordered diffs + wall/exit/shas/determinism | measured | §Step 2: 8 movers every K (12 cells K=0, 13 K≥1) + 5/3-site off-span + 3/1/0-flip diffs + joins + 0-flip upper legs; 6.6 s; re-run identical |
| boundary analysis (lower flip + extras census + upper negative + min-K) | measured | §Task 2: 734-c342 flips 0→1; 5 extras (no d=2); first flip None; min-K 1/1/234/366/367 |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; margin table; gaps below |
| screenshot if a K-sweep map discriminates (or absence reasoned) | measured | present by rule: B3 + B2 meet; 435 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m31"
cp local/research/M31/m31.py local/research/M31/control.py local/research/M31/DESIGN.md "/Volumes/Extreme SSD/m31/"
python3 m31.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28" "/Volumes/Extreme SSD/m30" "/Volumes/Extreme SSD/m31" /Users/bradrichardson/dev/ssx3/local/research/M31 > m31.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m31/m31-census-K0.tsv" "/Volumes/Extreme SSD/m31/m31-census-K1.tsv" "/Volumes/Extreme SSD/m31/m31-census-K15.tsv" "/Volumes/Extreme SSD/m31/m31-census-K20.tsv" "/Volumes/Extreme SSD/m31/m31-census-K50.tsv" "/Volumes/Extreme SSD/m31/m31-census-K100.tsv" "/Volumes/Extreme SSD/m31/m31-cellmap.png" local/research/M31/
```

## Paths

Evidence (committed): `local/research/M31/` — `DESIGN.md`
(suite + bars + fixed K list, recorded before running),
`m31.py` (K=2 gate + windowed census + off-span + full
ordered diffs + boundary tables + joins + PNG writer),
`control.py` (known-boundary-extra controls),
`m31-census-K0.tsv` + `m31-census-K1.tsv` +
`m31-census-K15.tsv` + `m31-census-K20.tsv` +
`m31-census-K50.tsv` + `m31-census-K100.tsv` (full 764×8
windowed matrices, 54295 B each), `m31-cellmap.png`
(K-sweep cell map, 435 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m31/` —
`m31.txt` (receipt: shas, baselines, K=2 gate, Task-1/2
tables, joins, diffs, re-run, PNG size), `control.txt`,
`m31.py`, `control.py`, `DESIGN.md` (working copies),
`m31-census-K*.tsv` (incl. K=2 gate matrix) +
`m31-cellmap.png` (working copies). No writes into `m15/`,
`m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`,
`m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`,
`m30/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. K≥234 upper confirmation (new): the nearest would-be
   real-data flip needs K≥234 (d+234 → admit; d+366/+367 need
   K≥366/367) — computed, not run, since K=234/366/367 sit
   outside the DESIGN-fixed list. Needs its own brief: a
   narrow upper-confirmation sweep (K ∈ {233, 234, 366, 367}
   to bracket both far admissions), offline — no new harness
   code.
2. K=0 census standing (new): at K=0 the windowed census has
   0 extra-only cells (734-c342 present) with 5 off-span
   sites — the tightest window that still un-moves 9 + 22.
   Needs its own brief only if the K=0 rule matters: the
   exact-vs-K0 standing comparison extended (which rule
   text pins K=0 vs K≥1?), offline — no new harness code.
3. M30 gaps 2–6 (still open, by reference): see M30 REPORT
   gaps 2–6 for the exact brief each needs (still+below
   growth now K-invariant at 5/3/4/752 per the join table
   above, shape-9 mid-frame cluster, shape-709 c298
   missings, shape-22 bottom cluster, M29 gaps 5–11).

(M30 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No K outside {0,1,2,15,20,50,100} computed ({5,10} via
   M30's sha-verified TSVs): the K list was fixed in
   DESIGN.md before running (no mid-run additions by brief);
   other K values need their own brief (gap 1).
2. No value-level off-span attribution: off-span sites are
   tabled as counts + (col,row,d) lists only (brief pins the
   census + tail tables, not per-site values).
3. No adopted window: the ±K rule is tabled WITHOUT adopting
   (exact-match census stands by brief).
4. c341 outside the census: guard-only (0 s0 sites) per
   brief's 8-column scope.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M31/`: `DESIGN.md`, `m31.py`,
`control.py`, `m31-census-K0.tsv`, `m31-census-K1.tsv`,
`m31-census-K15.tsv`, `m31-census-K20.tsv`,
`m31-census-K50.tsv`, `m31-census-K100.tsv` (54295 B each),
`m31-cellmap.png` (435 B), `REPORT.md` (this file).
