# M32 — Upper-K confirmation: K ∈ {233,234,366,367} bracketing both far admissions: REPORT

M31 gap 1 worked at table level: the K=1 windowed census
recomputed from the dumps reads 8 movers / 13 cells / standings
matching M31 exactly (TSV sha `471f2862…85e30b6a7`
byte-identical to `m31-census-K1.tsv`, 13/13 cell rows,
stop rule not triggered); the sweep over the DESIGN-fixed K ∈
{233, 234, 366, 367} reads 8/9/10/10 movers with 13/14/15/15
cells; the off-span tail collapses 3→2→1→0 sites with the
admissions landing exactly at K=234 (r266), K=366 (r400),
K=367 (r401); the full ordered diff list {100, 233, 234, 366,
367} flips 0/1/1/0 cells with 0/1/1/0 mover flips (9 re-moves
at 233→234, 22 re-moves at 234→366); the extras
re-enumeration confirms exactly 5 extra sites (d=1×2, d+234,
d+366, d+367 — no other sites); the K=367 TSV is byte-identical
to `m28-census.tsv` (windowed == exact at full admission);
the below-0.95 join reads 5/3/4/752 at K≤233, 6/3/3/752 at
K=234, and 6/4/3/751 at K≥366. Fully offline — no lease
of any kind, no boots, no harness code, no `adb`. No device
work. Runbook `local/muse/prompts/M32.md`. Tables, no verdicts.

Headers read first: `local/research/M31/REPORT.md` (all of it:
K=1..100 plateau row-identical at 8 movers / 13 cells;
off-span exactly the 3 far extras at every K≥1; 0 flips on
all 7 pairs spanning K=1..100; extras census exactly 5 sites;
join 5/3/4/752 throughout; gap 1 is this brief) plus
`local/research/M30/DESIGN.md` (the ±K window definition,
reused verbatim).

Time box 4 hours (start 2026-09-20 03:48 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m31/` — all outputs went to the new
`/Volumes/Extreme SSD/m32/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), `m28.txt` +
`m28-census.tsv` (exact-match guard), and `m31.txt` +
`m31-census-K1.tsv` (K=1 reproduction target) +
`m31-census-K100.tsv` (K=100 diff baseline). Work dir
`/Volumes/Extreme SSD/m32/`; evidence `local/research/M32/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M31; m31 K1/K100 shas equal each other):

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
| m31.txt | `5507adfb…15e4718` |
| m31-census-K1.tsv | `471f2862…30b6a7` |
| m31-census-K100.tsv | `471f2862…30b6a7` |

(Full hexes in `m32.txt` §inputs: 71 input lines — s0 + all 10
M28 movers + m15 + top-10 carrier triplets + `m28.txt` +
`m28-census.tsv` + `m31.txt` + `m31-census-K1.tsv` +
`m31-census-K100.tsv`. Triplet fold sha over all 764×3 bins:
`6c906897…61fd423b1` — matches M28/M29/M30/M31 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M31 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 reference
row lists + guard-only c341 n=0 match exactly. M28 TSV match
on all 764 (bad=0: tail + J4 + all-8-column n/ov/pres) +
mover list == the M28 10 + 15/15 move standings match
`m28.txt` + below-0.95 9-list tail+J4 exact. Window geometry:
interval-match True on all 8 columns at every K≥233 (32/32);
the 2 pre-registered K=1 hole-row exclusions tabled in §Task
2.1 (c340/c342 at K=1 — DESIGN-expected, not a failure). s0
windowed-present on all 8 at every computed K. Partition
(in-window + off-span + outside-census == tail) holds on all
764 per computed K (0 violations). K=1 gate (DESIGN.md) not
triggered: 8 movers / 13 cells / standings + TSV bytes all
match M31. M31 K100 TSV sha equals the K=1 recompute sha
(diff leg verified, not assumed).

## Runs (offline estimators)

One `m32.py` invocation (the receipt, 13.0 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m32.py receipt | 13.0 s | exit 0; all guards pass; canon `ac6a3780…fc4d1263` |
| control.py C0–C368 | <1 s | green; windowed standings + off-span exact on all 9 |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + census fields) | 764 | 11.6 s |
| Exact-match M28 guard (TSV + movers + standings) | 764 | 0.0 s |
| Task 1 (K=1 gate + windowed re-run per K + TSVs) | 764 × 5 | 1.0 s |
| Task 1.2/1.3 + Task 2 (off-span + deltas + joins + diffs) | — | 0.0 s |
| Determinism re-run (Task 1 K=233 on s0+9+22) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m32.py` wall | — | 13.0 s |

## Step 2 — estimates

### Task 1 — the bracket (fixed K ∈ {233, 234, 366, 367} + K=1 gate)

K=1 gate detail (recomputed vs M31 — stop rule not
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

TSV bytes: recomputed K=1 sha == M31 K1 sha
(`471f2862…85e30b6a7`), identical=True. (Offsets/rshifts
re-verify M31's: +2/+2/+2/+2/+2/+2/−1 and
+1.5/+1.5/−1.5/+1.0/+2.0/+0.5/+3.0.)

Windowed movers / moved cells per computed K (full 764×8
matrices committed as `m32-census-K233/234/366/367.tsv`,
54295/54295/54296/54296 B; K=1 matrix in the work dir only,
sha-recorded above):

| K | movers (n) | shape list | cells (n) |
| --- | ---: | --- | ---: |
| 1 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 100 (M31 TSV) | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 233 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 234 | 9 | [9,708,709,710,711,731,732,733,734] | 14 |
| 366 | 10 | [9,22,708,709,710,711,731,732,733,734] | 15 |
| 367 | 10 | [9,22,708,709,710,711,731,732,733,734] | 15 |

TSV identity: K=1/233 shas both `471f2862…85e30b6a7` (==
M31 K1/K100 input shas, §Baseline note); K=234 sha
`c565fc60…1148b40e`; K=366 sha `eeff5a1e…d81590f`; K=367
sha `27872527…5a9e7f` — byte-identical (`cmp`) to
`m28-census.tsv` (windowed == exact at full admission).

Full per-cell windowed table at K=1/233 (13 rows; the plateau
rows — K=233 TSV bytes equal the K=1 recompute):

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

Admission rows added above the plateau (all other moved cells
keep the K=1/233 rows byte-identical — same n_K/ov_K,
standings, dests, offsets, rshifts at every computed K):

| K | Shape | col | n_K/ov_K | standing |
| ---: | ---: | --- | --- | --- |
| 234 | 9 | 321 | 11/10 | none(extra-only) |
| 366 | 9 | 321 | 11/10 | none(extra-only) |
| 366 | 22 | 296 | 10/9 | none(extra-only) |
| 367 | 9 | 321 | 11/10 | none(extra-only) |
| 367 | 22 | 296 | 11/9 | none(extra-only) |

Per-column windowed mover counts (only c296/c321 change;
other 6 columns constant at every computed K and K=100):

| col | K≤233 movers | K=234 movers | K≥366 movers |
| ---: | --- | --- | --- |
| 257 | 1: [731] | 1: [731] | 1: [731] |
| 277 | 1: [731] | 1: [731] | 1: [731] |
| 296 | 2: [708, 732] | 2: [708, 732] | 3: [22, 708, 732] |
| 301 | 2: [709, 733] | 2: [709, 733] | 2: [709, 733] |
| 321 | 1: [733] | 2: [9, 733] | 2: [9, 733] |
| 340 | 2: [710, 734] | 2: [710, 734] | 2: [710, 734] |
| 342 | 2: [711, 734] | 2: [711, 734] | 2: [711, 734] |
| 343 | 2: [711, 734] | 2: [711, 734] | 2: [711, 734] |

Off-span tail tables per computed K (3→2→1→0 sites; no 4th
off-span site in any of the 764 at any computed K):

| K | shapes | pooled sites | per-shape rows |
| --- | ---: | ---: | --- |
| 1 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 233 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 234 | 1 | 2 | s22: c296 r400 (d+366), r401 (d+367) |
| 366 | 1 | 1 | s22: c296 r401 (d+367) |
| 367 | 0 | 0 | — |

Outside-census (non-named-column) tail per M28 mover
(K-invariant by construction; matches M30/M31's table):

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
{100,233,234,366,367} (4 pairs — the bracket, tabled;
K=100 pres rows from M31's sha-verified TSV):

| Pair | flipping cells | mover flips | identical |
| --- | ---: | ---: | --- |
| 100→233 | 0 | 0 | True |
| 233→234 | 1: (9,c321 1→0) | 1: 9 re-moves | False |
| 234→366 | 1: (22,c296 1→0) | 1: 22 re-moves | False |
| 366→367 | 0 | 0 | True |

### Task 2 — admission analysis (what crosses, what changes?)

Per-site admission table (off-span vs in-window at each
computed K — admissions land exactly at K=234/366/367):

| Site | K=1 | K=233 | K=234 | K=366 | K=367 |
| --- | --- | --- | --- | --- | --- |
| s9 c321 r266 (d+234) | off | off | IN | IN | IN |
| s22 c296 r400 (d+366) | off | off | off | IN | IN |
| s22 c296 r401 (d+367) | off | off | off | off | IN |

Standing response (the cells the admissions flip, tabled
with n_K/ov_K):

| Cell | K=1 | K=233 | K=234 | K=366 | K=367 |
| --- | --- | --- | --- | --- | --- |
| s9-c321 | present 10/10 | present 10/10 | extra-only 11/10 | extra-only 11/10 | extra-only 11/10 |
| s22-c296 | present 9/9 | present 9/9 | present 9/9 | extra-only 10/9 | extra-only 11/9 |

Extras-distance census over all 764 shapes × 8 named columns
(re-enumeration — any site that would flip a bracket leg
unannounced?):

| Measure | Value |
| --- | --- |
| pooled extra sites | 5 on shapes [9, 22, 734] |
| distance histogram | d=1×2, d+234×1, d+366×1, d+367×1 |
| per-site rows | s9 c321 r266 d+234; s22 c296 r400 d+366, r401 d+367; s734 c342 r26 d+1, r33 d+1 |
| other d≤2 sites | none |
| pooled missing rows | 71 (all d=0 by construction) |

Window geometry (dist-rows vs span-interval per column per
computed K — the 2 DESIGN-expected K=1 exclusions;
interval-match True on all 8 columns at every K≥233):

| K | col | span | win | interval-match | excluded hole rows |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 340 | [24,34] | [23,35] | False | [29] |
| 1 | 342 | [27,35] | [26,36] | False | [31, 32] |

(All other (K, col) pairs: interval-match True.)

Upper boundary: first real-data flip past K=100:

| Bracket leg | flipping cells | mover flips |
| --- | ---: | ---: |
| 100→233 | 0 | 0 |
| 233→234 | 1 | 1 |
| 234→366 | 1 | 1 |
| 366→367 | 0 | 0 |

First real-data flip past K=100: (233, 234).

Minimum K that admits each off-span site (run-confirmed —
union of off-span sites across computed Ks):

| Site | d | min admitting K |
| --- | ---: | ---: |
| s9 c321 r266 | +234 | 234 |
| s22 c296 r400 | +366 | 366 |
| s22 c296 r401 | +367 | 367 |

Standing stability (exact + per K; K=100 movers/cells from
M31's sha-verified TSV):

| Rule | movers | cells | assigned | extra-only | no-cand |
| --- | ---: | ---: | ---: | ---: | ---: |
| exact | 10 | 15 | 7 | 3 | 5 |
| K=1 | 8 | 13 | 7 | 1 | 5 |
| K=100 | 8 | 13 | per-M31 (TSV-identical) | — | — |
| K=233 | 8 | 13 | 7 | 1 | 5 |
| K=234 | 9 | 14 | 7 | 2 | 5 |
| K=366 | 10 | 15 | 7 | 3 | 5 |
| K=367 | 10 | 15 | 7 | 3 | 5 |

Below-0.95 join per K (J values unchanged; K=100 from the
loaded TSV — each admission moves its shape across the mover
line, tabled):

|  | below-0.95 | above-0.95 |
| --- | --- | --- |
| exact mover | 6: 9, 711, 731, 732, 733, 734 | 4: 22, 708, 709, 710 |
| exact still | 3: 2, 3, 700 | 751 |
| K mover (1/100/233) | 5: 711, 731, 732, 733, 734 | 3: 708, 709, 710 |
| K still (1/100/233) | 4: 2, 3, 9, 700 | 752 |
| K=234 mover | 6: 9, 711, 731, 732, 733, 734 | 3: 708, 709, 710 |
| K=234 still | 3: 2, 3, 700 | 752 |
| K mover (366/367) | 6: 9, 711, 731, 732, 733, 734 | 4: 22, 708, 709, 710 |
| K still (366/367) | 3: 2, 3, 700 | 751 |

(The join reads 5/3/4/752 at K=1/100/233, 6/3/3/752 at
K=234, and 6/4/3/751 — the exact join — at K=366/367.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C0 (c340 −r24, d=0) | moved every K, missK=1, no-cand, off empty | exact | True |
| C232 (c321 +r264, d=232) | present + off {(321,264)} K=1; extra-only 11/10, off empty, K≥233 | exact | True |
| C233 (c321 +r265, d=233) | present + off {(321,265)} K=1; extra-only 11/10, off empty, K≥233 | exact | True |
| C234 (c321 +r266, d=234) | present + off {(321,266)} K=1,233; extra-only 11/10, off empty, K≥234 | exact | True |
| C235 (c321 +r267, d=235) | present + off {(321,267)} K=1,233,234; extra-only 11/10, off empty, K≥366 | exact | True |
| C365 (c296 +r399, d=365) | present + off {(296,399)} K=1,233,234; extra-only 10/9, off empty, K≥366 | exact | True |
| C366 (c296 +r400, d=366) | present + off {(296,400)} K=1,233,234; extra-only 10/9, off empty, K≥366 | exact | True |
| C367 (c296 +r401, d=367) | present + off {(296,401)} K=1,233,234,366; extra-only 10/9, off empty, K=367 | exact | True |
| C368 (c296 +r402, d=368) | present + off {(296,402)} every K | exact | True |

(Full per-K rows in `control.txt`. C232/C233/C234/C235
straddle the lower admission (flip thresholds K≥232/233/234/
235); C365/C366/C367/C368 straddle the upper admissions
(K≥365/366/367/368); C234/C366/C367 pin the exact real-data
sites. C235/C365 flip between grid points 234 and 366 —
computed, not run.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 K=233 windowed census on s0+9+22, fresh loads)
pass1 `ac6a3780…fc4d1263` vs pass2 `ac6a3780…fc4d1263`,
identical=True; 3/3 lines match=True; windowed mover sets
s0=[] s9=[] s22=[] identical. (The canon sha equals M31's K=2
canon — the same rows: all 3 far extras off-span at both
K=2 and K=233.)

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| B1_K1REPRO | K=1 reads 8 movers / 13 cells / M31 standings + TSV bytes | 8/13 + 13/13 rows + sha-identical — met (gate) |
| B2_OFF233 | off-span at K=233 exactly the 3 far extras | 3 sites == far-3 — met |
| B3_ADMIT234 | off-span at K=234 exactly r400+r401 | 2 sites — met |
| B4_ADMIT366 | off-span at K=366 exactly r401 | 1 site — met |
| B5_ALLIN367 | off-span at K=367 empty | 0 sites — met |
| B6_S9STAND | s9-c321 present K≤233, extra-only 11/10 K≥234 | 5/5 rows — met |
| B7_S22STAND | s22-c296 present K≤234, extra-only 10/9→11/9 K≥366 | 5/5 rows — met |
| B8_KDIFFS | 100→233 0/0, 233→234 1/1, 234→366 1/1, 366→367 0/0 | 0/1/1/0 cells, 0/1/1/0 movers — met |
| B9_BELOW95 | windowed movers below-0.95 share ≥ 0.50 every computed K | 5/8, 5/8, 6/9, 6/10, 6/10 — met |
| B10_MISSIN | 4/4 missing rows in-window every computed K incl. K=1 | 4/4 at all 5 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
the two far admissions (r266 enters at K=234 — s9-c321 flips
present→extra-only while s22 stays put with 2 off-span
sites; r400 enters at K=366 — s22-c296 flips with n_K 10/9;
r401 enters at K=367 — s22-c296 stays moved with n_K 11/9
and off-span empties); by mover scope (8→9→10 movers,
13→14→15 cells — the only shapes in the 764 whose standing
changes above K=100 are 9 + 22); and by TSV bytes (K=233 ==
K=1 plateau bytes; K=367 == the M28 exact-match bytes).
Task 2 discriminates the bracket exactly: the rule bites only
twice on real data above K=100 — 233→234 (s9-c321) and
234→366 (s22-c296) — with 0 flips on 100→233 and 366→367;
the extras re-enumeration confirms the 3 far sites are the
only admittable sites (nothing else at any d); the join
crosses twice (9 below-0.95 at K=234, 22 above-0.95 at
K=366, reaching the exact join at K≥366).

Upper-boundary closure as a TABLE (per-K
movers/cells/off-span/join — no verdict):

| K | movers/cells | standings (a/e/n) | off-span (shapes/sites) | join (mb/ma/sb/sa) | flips vs next |
| --- | ---: | --- | ---: | --- | ---: |
| exact (no window) | 10/15 | 7/3/5 | n/a | 6/4/3/751 | — |
| 1 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 100, M31 TSV) |
| 100 (M31 TSV) | 8/13 | per-M31 | 2/3 (M31) | 5/3/4/752 | 0 (vs 233) |
| 233 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 1 cell, 1 mover (vs 234) |
| 234 | 9/14 | 7/2/5 | 1/2 | 6/3/3/752 | 1 cell, 1 mover (vs 366) |
| 366 | 10/15 | 7/3/5 | 1/1 | 6/4/3/751 | 0 (vs 367) |
| 367 | 10/15 | 7/3/5 | 0/0 | 6/4/3/751 | — (== exact bytes) |

(K=367 standings/off-span/join equal the exact-match row;
the K=367 TSV is byte-identical to `m28-census.tsv`.)

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
(`m32-cellmap.png`, 269 B of 5242880 budget) colors
100/233/234/366/367 presence per (mover, col) cell (green =
present, magenta = moved); DESIGN.md admits an evidence copy
iff B2 meets AND B5 meets — B2 meets (3 off-span sites at
K=233) with B5 meets (0 off-span sites at K=367), both far
admissions visible in the pre-registered K233-vs-K367 split
(8→10 movers).

Recorded without verdict: K=1 reproduces M31 exactly (stop
rule not triggered); the bracket reads 8 movers at K=233, 9
at K=234 (s9-c321 extra-only), 10 at K≥366 (s22-c296
extra-only), with off-span collapsing 3→2→1→0 at exactly
K=234/366/367; the 233→234 and 234→366 legs flip 1 cell
each while 100→233 and 366→367 flip 0; the extras census
re-confirms exactly 5 sites; K=367 equals the exact-match
census byte-for-byte; the join crosses the mover line twice
(6/3/3/752 at K=234, 6/4/3/751 at K≥366); 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| Upper-K confirmation + falsification bars + fixed K list, recorded before running | recorded | `DESIGN.md`: M30-verbatim ±K window + off-span + outside-census partition, M28-verbatim standings on windowed miss/extra, C0–C368 controls, bars B1–B10/N, K ∈ {233,234,366,367} + K=1 gate |
| windowed census + off-span + full ordered diffs + wall/exit/shas/determinism | measured | §Step 2: 8/9/10/10 movers (13/14/15/15 cells) + 3/2/1/0-site off-span + 0/1/1/0-flip diffs + joins; 13.0 s; re-run identical |
| admission analysis (per-site + standing response + join) | measured | §Task 2: r266/r400/r401 admit at 234/366/367; s9/s22 extra-only on admission; join crosses at 234 + 366 |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; closure table; gaps below |
| screenshot if a K-sweep map discriminates (or absence reasoned) | measured | present by rule: B2 + B5 meet; 269 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m32"
cp local/research/M32/m32.py local/research/M32/control.py local/research/M32/DESIGN.md "/Volumes/Extreme SSD/m32/"
python3 m32.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28" "/Volumes/Extreme SSD/m31" "/Volumes/Extreme SSD/m32" /Users/bradrichardson/dev/ssx3/local/research/M32 > m32.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m32/m32-census-K233.tsv" "/Volumes/Extreme SSD/m32/m32-census-K234.tsv" "/Volumes/Extreme SSD/m32/m32-census-K366.tsv" "/Volumes/Extreme SSD/m32/m32-census-K367.tsv" "/Volumes/Extreme SSD/m32/m32-cellmap.png" local/research/M32/
```

## Paths

Evidence (committed): `local/research/M32/` — `DESIGN.md`
(suite + bars + fixed K list, recorded before running),
`m32.py` (K=1 gate + windowed census + off-span + full
ordered diffs + admission tables + joins + PNG writer),
`control.py` (known-far-extra controls),
`m32-census-K233.tsv` + `m32-census-K234.tsv` +
`m32-census-K366.tsv` + `m32-census-K367.tsv` (full 764×8
windowed matrices, 54295/54295/54296/54296 B),
`m32-cellmap.png` (K-sweep cell map, 269 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m32/` —
`m32.txt` (receipt: shas, baselines, K=1 gate, Task-1/2
tables, joins, diffs, re-run, PNG size), `control.txt`,
`m32.py`, `control.py`, `DESIGN.md` (working copies),
`m32-census-K*.tsv` (incl. K=1 gate matrix) +
`m32-cellmap.png` (working copies). No writes into `m15/`,
`m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`,
`m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`,
`m30/`, `m31/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Between-grid K values (new): the census ran at
   {1,233,234,366,367} (+ K=100 via M31's sha-verified TSV);
   K in (100,233), (234,366), (367,∞) is uncomputed. The
   extras census (only d∈{1,234,366,367}) plus the empty
   off-span at K=367 pin every other K by computation (K in
   (100,233) == K=100 rows; K in (234,366) == K=234 rows;
   K>367 == exact rows) — computed, not run. Needs its own
   brief only if run-level confirmation matters: a spot-K
   sweep (e.g. K ∈ {150, 300, 400}), offline — no new harness
   code.
2. M31 gap 2 (still open, by reference): see M31 REPORT gap 2
   for the exact brief it needs (K=0 census standing —
   0 extra-only cells with 5 off-span sites).
3. M30 gaps 2–6 (still open, by reference): see M30 REPORT
   gaps 2–6 for the exact brief each needs (still+below
   growth now K-dependent per the join table above — 9
   crosses at K=234, 22 at K=366 — shape-9 mid-frame
   cluster, shape-709 c298 missings, shape-22 bottom
   cluster, M29 gaps 5–11).

(M31 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No K outside {1,100,233,234,366,367} computed (100 via
   M31's sha-verified TSV): the K list was fixed in
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

Committed under `local/research/M32/`: `DESIGN.md`, `m32.py`,
`control.py`, `m32-census-K233.tsv`, `m32-census-K234.tsv`,
`m32-census-K366.tsv`, `m32-census-K367.tsv`
(54295/54295/54296/54296 B), `m32-cellmap.png` (269 B),
`REPORT.md` (this file).
