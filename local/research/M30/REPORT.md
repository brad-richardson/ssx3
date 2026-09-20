# M30 — Span-windowed census rule: proposal + 764-shape re-run: REPORT

M29 gap 1 worked at table level: the exact-match census
recomputed from the dumps (10 movers / 15 cells / standings
matching M28 exactly — TSV bad=0 on all 764, 15/15 standings,
stop rule not triggered) re-run under the ±K span window with
the DESIGN-fixed K ∈ {2, 5, 10} reads 8 movers / 13 cells at
every K (9 + 22 un-moved; the three K tables row-identical, 0
flipping cells); the off-span tail at every K is exactly M29's
3 far extras (9 c321 r266 d+234; 22 c296 r400/r401 d+366/+367)
with no 4th off-span site anywhere in the 764; standings read
7 assigned + 1 extra-only (734-c342) + 5 no-cand at every K;
the below-0.95 join shifts 9 to still+below (5/3/4/752 at
every K). Fully offline — no lease of any kind, no boots, no
harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M30.md`. Tables, no verdicts.

Headers read first: `local/research/M29/REPORT.md` (all of it:
6 partial cells, 9 delta-row sites — 4 missings in-span,
734-c342 r26/r33 at ±1 row, 9 r266 + 22 r400/r401 far-flung at
+234/+366/+367) plus `local/research/M28/REPORT.md` (all of
it: 10 movers / 15 moved cells, 7 assigned + 3 extra-only + 5
no-cand; per-cell n/ov/standings) and the M28/M29 DESIGN.md
estimator + bar precedent.

Time box 4 hours (start 2026-09-20 03:31 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m29/` — all outputs went to the new
`/Volumes/Extreme SSD/m30/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and `m28.txt`
+ `m28-census.tsv` (match targets). Work dir `/Volumes/Extreme
SSD/m30/`; evidence `local/research/M30/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M29):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0009 | `1926a151…ea086fe0` |
| m16-mid-s0009 | `a9fa67fb…bd5e9806` |
| m16-full-s0009 | `a9a5339d…207ae486` |
| m16-v0-s0022 | `09dd96f3…bd274439` |
| m16-mid-s0022 | `5e05bc20…58758688` |
| m16-full-s0022 | `ed846091…000d8bf3` |
| m16-v0-s0734 | `82467b1f…4bddbb` |
| m16-mid-s0734 | `45de5504…5977d26` |
| m16-full-s0734 | `f60ddd16…e038600f` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m28.txt | `87a12157…398faf25` |
| m28-census.tsv | `27872527…7ca15a9e7f` |

(Full hexes in `m30.txt` §inputs: 68 input lines — s0 + all 10
M28 movers + m15 + top-10 carrier triplets + `m28.txt` +
`m28-census.tsv`. Triplet fold sha over all 764×3 bins:
`6c906897…61fd423b1` — matches M28/M29 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M29 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 reference
row lists + guard-only c341 n=0 match exactly. M28 TSV match
on all 764 (bad=0: tail + J4 + all-8-column n/ov/pres) +
mover list == the M28 10 + 15/15 move standings match
`m28.txt` + below-0.95 9-list tail+J4 exact. Window geometry:
dist-rows == span-interval on all 8 columns at every K (24/24
interval-match). s0 windowed-present on all 8 at every K.
Partition (in-window + off-span + outside-census == tail)
holds on all 764 per K (0 violations). Mismatch rule
(DESIGN.md) not triggered.

## Runs (offline estimators)

One `m30.py` invocation (the receipt, 19.4 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m30.py receipt | 19.4 s | exit 0; all guards pass; canon `8a608a70…69534182` |
| control.py W1–W5 | <1 s | green; windowed standings + off-span exact on all 5 |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + census fields) | 764 | 18.2 s |
| Exact-match M28 guard (TSV + movers + standings) | 764 | 0.0 s |
| Task 1 (windowed re-run per K + TSVs) | 764 × 3 | 0.7 s |
| Task 1.2/1.3 + Task 2 (off-span + deltas + joins + diffs) | — | 0.0 s |
| Determinism re-run (Task 1 exact on s0+9+22) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m30.py` wall | — | 19.4 s |

## Step 2 — estimates

### Task 1 — windowed census (fixed K ∈ {2, 5, 10})

Exact-match guard detail (recomputed vs M28 — stop rule not
triggered): movers [9,22,708,709,710,711,731,732,733,734]
(10/10); moved cells 15/15 with standings:

| Shape | col | n/ov | standing | m28.txt | match |
| ---: | ---: | --- | --- | --- | --- |
| 9 | 321 | 11/10 | none(extra-only) | none(extra-only) | True |
| 22 | 296 | 11/9 | none(extra-only) | none(extra-only) | True |
| 708 | 296 | 8/8 | none(no-cand) | none(no-cand) | True |
| 709 | 301 | 10/10 | none(no-cand) | none(no-cand) | True |
| 710 | 340 | 6/6 | none(no-cand) | none(no-cand) | True |
| 711 | 342 | 0/0 | none(no-cand) | none(no-cand) | True |
| 711 | 343 | 0/0 | none(no-cand) | none(no-cand) | True |
| 731 | 257 | 0/0 | ok | ok | True |
| 731 | 277 | 0/0 | ok | ok | True |
| 732 | 296 | 0/0 | ok | ok | True |
| 733 | 301 | 0/0 | ok | ok | True |
| 733 | 321 | 0/0 | ok | ok | True |
| 734 | 340 | 0/0 | ok | ok | True |
| 734 | 342 | 7/5 | none(extra-only) | none(extra-only) | True |
| 734 | 343 | 0/0 | ok | ok | True |

Windowed movers / moved cells per K (full 764×8 matrices
committed as `m30-census-K2/5/10.tsv`, 54295 B each):

| K | movers (n) | shape list | cells (n) |
| --- | ---: | --- | ---: |
| 2 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 5 | 8 | [708,709,710,711,731,732,733,734] | 13 |
| 10 | 8 | [708,709,710,711,731,732,733,734] | 13 |

Full per-cell windowed table (K=2 receipt rows; the K=5 and
K=10 tables are row-identical — 0 flipping cells, §Task 2.3):

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

Per-column windowed mover counts (identical at every K):

| col | movers | shapes |
| ---: | ---: | --- |
| 257 | 1 | [731] |
| 277 | 1 | [731] |
| 296 | 2 | [708, 732] |
| 301 | 2 | [709, 733] |
| 321 | 1 | [733] |
| 340 | 2 | [710, 734] |
| 342 | 2 | [711, 734] |
| 343 | 2 | [711, 734] |

Off-span tail tables per K (identical at every K — pooled
3 sites on 2 shapes; no 4th off-span site in any of the 764):

| K | shapes | pooled sites | per-shape rows |
| --- | ---: | ---: | --- |
| 2 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 5 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |
| 10 | 2 | 3 | s9: c321 r266 (d+234); s22: c296 r400 (d+366), r401 (d+367) |

Outside-census (non-named-column) tail per M28 mover
(K-invariant by construction; 764/764 shapes hold
outside-census tail):

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

Delta table exact-vs-windowed per K (identical at every K):
exact movers surviving 8/10
([708,709,710,711,731,732,733,734]); un-moved 2 ([9, 22]);
newly moving 0:

| Exact cell | exact standing | windowed (every K) | flag |
| --- | --- | --- | --- |
| s9 c321 | none(extra-only) | present | CHANGED |
| s22 c296 | none(extra-only) | present | CHANGED |
| s708 c296 | none(no-cand) | none(no-cand) | SAME |
| s709 c301 | none(no-cand) | none(no-cand) | SAME |
| s710 c340 | none(no-cand) | none(no-cand) | SAME |
| s711 c342 | none(no-cand) | none(no-cand) | SAME |
| s711 c343 | none(no-cand) | none(no-cand) | SAME |
| s731 c257/c277 | ok/ok | ok/ok | SAME |
| s732 c296 | ok | ok | SAME |
| s733 c301/c321 | ok/ok | ok/ok | SAME |
| s734 c340/c343 | ok/ok | ok/ok | SAME |
| s734 c342 | none(extra-only) | none(extra-only) | SAME |

M29 extras classification per K: 3/3 far extras off-span at
every K (9 r266 d+234; 22 r400 d+366, r401 d+367); 2/2 near
extras in-window at every K (734 r26/r33 at d=1 each);
4/4 missing rows in-window at every K (all d=0).

### Task 2 — window behavior (does ±K stabilize the census?)

Standing stability (exact + per K):

| Rule | movers | cells | assigned | extra-only | no-cand |
| --- | ---: | ---: | ---: | ---: | ---: |
| exact | 10 | 15 | 7 | 3 | 5 |
| K=2 | 8 | 13 | 7 | 1 | 5 |
| K=5 | 8 | 13 | 7 | 1 | 5 |
| K=10 | 8 | 13 | 7 | 1 | 5 |

Below-0.95 join per K (J values unchanged; exact + windowed
2×2 — windowed identical at every K):

|  | below-0.95 | above-0.95 |
| --- | --- | --- |
| exact mover | 6: 9, 711, 731, 732, 733, 734 | 4: 22, 708, 709, 710 |
| exact still | 3: 2, 3, 700 | 751 |
| K mover (every K) | 5: 711, 731, 732, 733, 734 | 3: 708, 709, 710 |
| K still (every K) | 4: 2, 3, 9, 700 | 752 |

K-sensitivity (adjacent-K diffs):

| Pair | flipping cells | mover flips | identical |
| --- | ---: | ---: | --- |
| K2→K5 | 0 | 0 | True |
| K5→K10 | 0 | 0 | True |

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| W1 (c321 +r266, d+234) | exact extra-only; windowed present + off {(321,266)} every K | exact | True |
| W2 (c296 +r400/401, d+366/+367) | exact extra-only; windowed present + off {(296,400),(296,401)} every K | exact | True |
| W3 (c296 +r41, d+7) | off-span + present K=2,5; extra-only 10/9, off empty, K=10 | exact | True |
| W4 (c342 +r26, d=1) | extra-only 6/5, off empty, every K | exact | True |
| W5 (c340 −r24) | moved every K, missK=1, no-cand, off empty | exact | True |

(Full per-K rows in `control.txt`. W3 exercises the
K-sensitivity boundary the real data never hits: d+7 flips
between K=5 and K=10.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 exact-match on s0+9+22, fresh loads)
pass1 `8a608a70…69534182` vs pass2 `8a608a70…69534182`,
identical=True; 5/5 lines match=True; mover sets s0=[] s9=[321]
s22=[296] identical.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| W1_FAROFF | 3/3 far extras off-span at every K | 3/3 at K=2,5,10 — met |
| W2_NEARIN | 2/2 near extras in-window at every K | 2/2 at K=2,5,10 — met |
| W3_UNMOVE | windowed movers < 10 at every K | 8 at K=2,5,10 — met |
| W4_KSTABLE | windowed mover sets identical K2v5 + K5v10 | True/True — met |
| W5_BELOW95 | windowed movers below-0.95 share ≥ 0.50 every K | 5/8 = 0.6250 every K — met |
| W6_MISSIN | 4/4 missing rows in-window at every K | 4/4 at K=2,5,10 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
un-moving exactly the 2 far-extra shapes (9 + 22 → present at
every K, newly-moving 0) while the other 13 cells keep byte-
identical standings (dests/offsets/rshifts unchanged,
734-c342 stays extra-only at 7/5); by off-span scope (pooled
3 sites on 2 shapes at every K — no other named-column site
in the 764 sits beyond ±2 of its span, so K=2 already
excludes everything excludable); and by geometry (dist-rows
== span-interval 24/24, all holes bridge at d≤2). Task 2
discriminates by standing response (extra-only 3→1, assigned
7 and no-cand 5 untouched — the window removes far-extra
cells without resolving any unassigned cell), by the join
(9 moves to still+below, growing the all-present below-0.95
set 3→4; 22 leaves mover+above), and by K-sensitivity
negatively (0 flips on both pairs — the rule has no observable
stability margin inside {2,5,10} on real data; only the W3
synthetic at d+7 flips).

Rule recommendation as a TABLE (cost/benefit per K with the
numbers — no verdict):

| K | movers/cells | standings (a/e/n) | off-span (shapes/sites) | join (mb/ma/sb/sa) | flips vs neighbor | boundary probe |
| --- | ---: | --- | ---: | --- | ---: | --- |
| exact (no window) | 10/15 | 7/3/5 | n/a | 6/4/3/751 | — | — |
| 2 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 5) | W3 off-span |
| 5 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 2, 10) | W3 off-span |
| 10 | 8/13 | 7/1/5 | 2/3 | 5/3/4/752 | 0 (vs 5) | W3 in-window extra |

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; window tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence windowed-census
mover map (`m30-windowmap.png`, 1241 B of 5242880 budget)
colors exact + K2/K5/K10 mover rows (green = still, magenta =
mover); DESIGN.md admits an evidence copy iff W3 meets AND W1
meets — W3 meets (8 < 10 at every K) with W1 meets (3/3
off-span at every K).

Recorded without verdict: 10 movers / 15 cells / standings
recomputed exactly (stop rule not triggered); the ±K window
un-moves 9 + 22 at every K (8/13, row-identical across K, 0
flips) with off-span exactly the 3 far extras and no 4th site
in the 764; standings shift extra-only 3→1 with assigned and
no-cand untouched; the join grows still+below 3→4 (9 joins
2/3/700); 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| rule proposal + falsification bars + fixed K list, recorded before running | recorded | `DESIGN.md`: ±K window + off-span + outside-census partition, M28-verbatim standings on windowed miss/extra, W1–W5 controls, bars W1–W6/N, K ∈ {2,5,10} |
| windowed census + off-span + delta tables + wall/exit/shas/determinism | measured | §Step 2: 8/13 per K + 3-site off-span + 2-CHANGED deltas + joins + 0-flip diffs; 19.4 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; rule table; gaps below |
| screenshot if a windowed-census map discriminates (or absence reasoned) | measured | present by rule: W3 + W1 meet; 1241 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m30"
cp local/research/M30/m30.py local/research/M30/control.py local/research/M30/DESIGN.md "/Volumes/Extreme SSD/m30/"
python3 m30.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28" "/Volumes/Extreme SSD/m30" /Users/bradrichardson/dev/ssx3/local/research/M30 > m30.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m30/m30-census-K2.tsv" "/Volumes/Extreme SSD/m30/m30-census-K5.tsv" "/Volumes/Extreme SSD/m30/m30-census-K10.tsv" "/Volumes/Extreme SSD/m30/m30-windowmap.png" local/research/M30/
```

## Paths

Evidence (committed): `local/research/M30/` — `DESIGN.md`
(suite + bars + fixed K list, recorded before running),
`m30.py` (exact guard + windowed census + off-span + joins +
diffs + PNG writer), `control.py` (known-far-extra controls),
`m30-census-K2.tsv` + `m30-census-K5.tsv` +
`m30-census-K10.tsv` (full 764×8 windowed matrices, 54295 B
each), `m30-windowmap.png` (mover map, 1241 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m30/` —
`m30.txt` (receipt: shas, baselines, exact guard, Task-1/2
tables, joins, diffs, re-run, PNG size), `control.txt`,
`m30.py`, `control.py`, `DESIGN.md` (working copies),
`m30-census-K*.tsv` + `m30-windowmap.png` (working copies). No
writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`,
`m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`,
`m28/`, `m29/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. K-boundary emptiness (new): no named-column site in any of
   the 764 sits at span distance 3–10, so the window is
   identical at K=2/5/10 and the rule's stability margin is
   unobserved on real data (only synthetic W3 at d+7 flips).
   Needs its own brief: a wider K sweep (K ∈ {0,1} below to
   probe 734-c342's d=1 extras + K ∈ {15,20,50,100} above to
   find the first real-data flip), offline — no new harness
   code.
2. Still+below growth (new): 9 joins 2/3/700 as below-0.95
   with all 8 columns present under every K (still+below
   3→4). Needs its own brief only if the below-0.95 family
   matters: the M28-gap-2 attribution extended with shape 9's
   windowed standing, offline — no new harness code.
3. Shape-9 mid-frame cluster (M29 gap 2, still open): 22
   privates + 8 missings outside c321 (rows 226–305)
   unattributed at byte level; the c321 r266 off-span site is
   one site of that cluster. Needs its own brief: the same
   private/missing/displacement attribution for shape 9's full
   sets, offline — no new harness code.
4. Shape-709 c298 missings (M29 gap 3, still open): 4 missing
   rows in UNNAMED column c298 (r28/29/34/35) — a second
   partial column on 709 outside the census 8 (unaffected by
   the window, which covers named columns only). Needs its own
   brief: unnamed-column partial scan, offline — no new
   harness code.
5. Shape-22 bottom cluster (M29 gap 4, still open): 2
   outside-col privates (393,307)/(402,295) + the 2 c296
   off-span extras form a rows-393–402 group. Needs its own
   brief only if bottom-frame privates matter: full-set
   attribution for shape 22, offline — no new harness code.
6. M29 gaps 5–11 (still open, by reference): see M29 REPORT
   gaps 5–11 for the exact brief each needs (still-below
   divergence now incl. 9 per gap 2 above, 711 pair wipe, 734
   triple move, 732 c296→c298 move, below-0.95 shape family,
   static-on-other-frame privates, M26 gaps 1–10/12–21).

(M29 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No K outside {2,5,10}: the K list was fixed in DESIGN.md
   before running (no mid-run additions by brief); other K
   values need their own brief (gap 1).
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

Committed under `local/research/M30/`: `DESIGN.md`, `m30.py`,
`control.py`, `m30-census-K2.tsv`, `m30-census-K5.tsv`,
`m30-census-K10.tsv` (54295 B each), `m30-windowmap.png`
(1241 B), `REPORT.md` (this file).
