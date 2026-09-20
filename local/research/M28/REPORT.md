# M28 — Streak-column census: which shapes move which columns, by how far: REPORT

M27 gap 1 worked at table level: 10/764 shapes move ≥1 of the 8
named s0 streak columns (exact-column-match rule — 754 shapes
read present on all 8), with 15 moved cells split 6
singles / 3 pairs / 1 triple; 7/15 moved cells assign a
destination (6 at +2, 1 at −1; 5 fresh, 2 named via 734's c342
collision), 3 extra-only + 5 no-cand unassigned; 6/10 movers read
below J 0.95 while 3/9 below-0.95 shapes (2/3/700) move nothing.
733/731 swap rows recomputed pairs + offsets + private-column
rows matching M27 exactly (stop rule not triggered). All 764
tail maps 100% luma (0 private U/V sites). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M28.md`. Tables, no
verdicts.

Headers read first: `local/research/M27/REPORT.md` (all of it:
733 100 B at 0.6694 = 19 + 21 + 81, miss = all of c301/c321,
priv = c303/c323; 731 mirror 100 B at 0.6833, c257/c277 →
c259/c279, set Jaccards 0.0000) plus M22's streak-column
definitions (s0 named columns + row spans, reproduced as the s0
reference) and `local/research/M25/REPORT.md` (per-row profiles
confirming the 8 row sets + holes).

Time box 4 hours (start 2026-09-20 03:09 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m27/` — all outputs went to the new
`/Volumes/Extreme SSD/m28/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and `m27.txt`
(match target). Work dir `/Volumes/Extreme SSD/m28/`; evidence
`local/research/M28/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M27):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0733 | `e60cd548…79444a0` |
| m16-mid-s0733 | `49a17a53…eb017ab67` |
| m16-full-s0733 | `97d16216…c8895df70` |
| m16-v0-s0731 | `a3812010…86a34135` |
| m16-mid-s0731 | `f2349d19…5833d8290` |
| m16-full-s0731 | `e1d2d409…38f80ecfe7` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m27.txt | `ea777f91…713b401a` |

(Full hexes in `m28.txt` §inputs. Triplet fold sha over all
764×3 bins: `6c906897…61fd423b1`.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M27 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 reference
row lists + guard-only c341 n=0 match exactly. 733/731 swap
rows (pairs + offsets + private-column n/rows) match M27
exactly. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m28.py` invocation (the receipt, 34.5 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m28.py receipt | 34.5 s | exit 0; all guards pass; canon `7f353f79…e064e8d2fe` |
| control.py S1–S5 | <1 s | green; census + displacements exact on all 5 |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + census fields) | 764 | 33.8 s |
| Task 1 (census matrix + movers + pairing) | 764 | 0.1 s |
| Task 2 (displacement + destinations) | 10 | 0.0 s |
| Task 2.3 (below-0.95 join) | 764 | 0.0 s |
| Determinism re-run (Task 1 on s0+733+731) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m28.py` wall | — | 34.5 s |

## Step 2 — estimates

### Task 1 — presence census (which shapes move which columns?)

733/731 swap rows recomputed from the dumps (pairs + offsets +
private-column rows match M27 exactly — stop rule not
triggered):

| Shape | tail | J vs s0 | moved | dests | offsets |
| ---: | ---: | ---: | --- | --- | --- |
| 733 | 100 | 0.6694 | [301, 321] | 301→303 (9, r25–33), 321→323 (10, r25–34) | +2/+2 |
| 731 | 100 | 0.6833 | [257, 277] | 257→259 (9, r25–33), 277→279 (9, r25–33) | +2/+2 |

Census matrix: all 764 × 8 with n/ov/present per column —
committed as `m28-census.tsv` (764 rows + header, 54296 B;
columns shape, tail_n, J_vs_s0, then n/ov/pres per named
column in fixed order). 754 shapes read present on all 8.

Mover census (shapes moving ≥1 named column): 10 shapes, 15
moved cells (k-hist 1:6 2:3 3:1):

| Shape | tail | J vs s0 | moved set | per-moved-col n/ov |
| ---: | ---: | ---: | --- | --- |
| 9 | 117 | 0.7520 | [321] | c321 11/10 (extra-only) |
| 22 | 106 | 0.9623 | [296] | c296 11/9 (extra-only) |
| 708 | 101 | 0.9902 | [296] | c296 8/8 (missing-only −1) |
| 709 | 97 | 0.9510 | [301] | c301 10/10 (missing-only −1) |
| 710 | 100 | 0.9804 | [340] | c340 6/6 (missing-only −2) |
| 711 | 95 | 0.9314 | [342, 343] | c342 0/0, c343 0/0 (full wipe) |
| 731 | 100 | 0.6833 | [257, 277] | both 0/0 (full swap pair) |
| 732 | 95 | 0.8942 | [296] | c296 0/0 (full wipe) |
| 733 | 100 | 0.6694 | [301, 321] | both 0/0 (full swap pair) |
| 734 | 94 | 0.8846 | [340, 342, 343] | c340 0/0, c342 7/5 (+2), c343 0/0 |

Per-column mover counts (which columns move most — c296 with
3; rest 1–2):

| col | movers | rate | miss-only | extra-only | mixed |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 257 | 1 | 0.0013 | 1 | 0 | 0 |
| 277 | 1 | 0.0013 | 1 | 0 | 0 |
| 296 | 3 | 0.0039 | 2 | 1 | 0 |
| 301 | 2 | 0.0026 | 2 | 0 | 0 |
| 321 | 2 | 0.0026 | 1 | 1 | 0 |
| 340 | 2 | 0.0026 | 2 | 0 | 0 |
| 342 | 2 | 0.0026 | 1 | 1 | 0 |
| 343 | 2 | 0.0026 | 2 | 0 | 0 |

Pair co-occurrence (shapes moving both; diagonal = per-column;
block-diagonal: 257/277, 301/321, 340/342/343 blocks; c296
solitary ×3):

| col | 257 | 277 | 296 | 301 | 321 | 340 | 342 | 343 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 257 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 277 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 296 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| 301 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| 321 | 0 | 0 | 0 | 1 | 2 | 0 | 0 | 0 |
| 340 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 |
| 342 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 2 |
| 343 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 2 |

Moved-set patterns (8 distinct; only [296] repeats, ×3):

| Moved set | n | shapes |
| --- | ---: | --- |
| [296] | 3 | 22, 708, 732 |
| [257, 277] | 1 | 731 |
| [301] | 1 | 709 |
| [301, 321] | 1 | 733 |
| [321] | 1 | 9 |
| [340] | 1 | 710 |
| [340, 342, 343] | 1 | 734 |
| [342, 343] | 1 | 711 |

### Task 2 — displacement census (where do movers go?)

15 moved cells: 7 assigned + 3 extra-only + 5 no-cand.
Singleton private Y-columns on movers read 11; private U/V
sites over all 764 read 0.

Displacement distribution (signed column offset; +2 reads 6/7
with one −1):

| offset | n |
| ---: | ---: |
| −1 | 1 |
| +2 | 6 |

Summary: min −1, med +2, mean 1.5714, max +2.

Row-shift distribution (median(priv) − median(s0 rows)):

| rshift | n |
| ---: | ---: |
| −1.5 | 1 |
| +0.5 | 1 |
| +1.0 | 1 |
| +1.5 | 2 |
| +2.0 | 1 |
| +3.0 | 1 |

Summary: min −1.5, med +1.5, mean 1.1429, max +3.0.

Destination analysis (dest col → n moves; fresh 5, named 2 —
the 2 named both point at c342 on shape 734, a collision):

| dest | n | fresh? | from |
| ---: | ---: | --- | --- |
| 259 | 1 | yes | s731 c257 |
| 279 | 1 | yes | s731 c277 |
| 298 | 1 | yes | s732 c296 |
| 303 | 1 | yes | s733 c301 |
| 323 | 1 | yes | s733 c321 |
| 342 | 2 | no | s734 c340 (+2), s734 c343 (−1) |

Per-shape move→dest rows (all 15 moved cells):

| Shape | miss col | dest | off | rshift | minshift | standing |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 9 | 321 | none | — | — | — | extra-only |
| 22 | 296 | none | — | — | — | extra-only |
| 708 | 296 | none | — | — | — | no-cand |
| 709 | 301 | none | — | — | — | no-cand |
| 710 | 340 | none | — | — | — | no-cand |
| 711 | 342 | none | — | — | — | no-cand |
| 711 | 343 | none | — | — | — | no-cand |
| 731 | 257 | 259 | +2 | +1.5 | +2 | fresh |
| 731 | 277 | 279 | +2 | +1.5 | +2 | fresh |
| 732 | 296 | 298 | +2 | −1.5 | +2 | fresh |
| 733 | 301 | 303 | +2 | +1.0 | +2 | fresh |
| 733 | 321 | 323 | +2 | +2.0 | +2 | fresh |
| 734 | 340 | 342 | +2 | +0.5 | +2 | named (collision) |
| 734 | 342 | none | — | — | — | extra-only |
| 734 | 343 | 342 | −1 | +3.0 | +0 | named (collision) |

Below-0.95 join (recomputed below set matches the M22 9-list
exactly — tail + J4 on all 9; guard OK):

| Shape | tail | J vs s0 | mover? |
| ---: | ---: | ---: | --- |
| 2 | 103 | 0.9159 | no (all 8 present) |
| 3 | 103 | 0.9340 | no (all 8 present) |
| 9 | 117 | 0.7520 | yes ([321]) |
| 700 | 114 | 0.8462 | no (all 8 present) |
| 711 | 95 | 0.9314 | yes ([342, 343]) |
| 731 | 100 | 0.6833 | yes ([257, 277]) |
| 732 | 95 | 0.8942 | yes ([296]) |
| 733 | 100 | 0.6694 | yes ([301, 321]) |
| 734 | 94 | 0.8846 | yes ([340, 342, 343]) |

2×2 (mover × below-0.95):

|  | below-0.95 | above-0.95 |
| --- | --- | --- |
| mover | 6: 9, 711, 731, 732, 733, 734 | 4: 22, 708, 709, 710 |
| still | 3: 2, 3, 700 | 751 |

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| S1 (move c301→c303) | moved [301], dest 303 +2 rs 1.0 | exact | True |
| S2 (move c257+c277→c259+c279) | moved [257, 277], +2/+2 rs 1.5/1.5 | exact | True |
| S3 (move c342→c345) | moved [342], dest 345 +3 rs 0.0 | exact | True |
| S4 (c296 drop 2 rows) | moved [296], dest none (no-cand) | exact | True |
| S5 (c343 +1 row) | moved [343], dest none (extra-only) | exact | True |

(All 5: moved-sets + per-column n/ov/pres + dests/offsets/
row-shifts exact. Full tables in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+733+731) pass1 `7f353f79…e064e8d2fe`
vs pass2 `7f353f79…e064e8d2fe`, identical=True; moved sets
identical=True (s0 [], 733 [301, 321], 731 [257, 277]).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_PAIR | movers moving exactly 2 cols, share ≥ 0.50 | 3/10 = 0.3000 — not met |
| H2_PLUS2 | assigned offsets equal to +2, share ≥ 0.50 | 6/7 = 0.8571 — met |
| H3_FRESH | dests outside the census 8, share ≥ 0.50 | 5/7 = 0.7143 — met |
| H4_CONCENTRATE | moved cells in {257,277,301,321}, share ≥ 0.50 | 6/15 = 0.4000 — not met |
| H5_BELOW95 | movers with J < 0.95, share ≥ 0.50 | 6/10 = 0.6000 — met |
| H6_PAIRREPEAT | modal size-2 moved-set on ≥2 shapes | [342, 343] on 1 (all three size-2 sets n=1) — not met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
mover count (10/764 move anything; 754 read byte-identical on
all 8), by moved-set size (6 singles, 3 pairs, 1 triple), by column
(c296 moves most with 3;
257/277 move only together on 731), by co-occurrence
(block-diagonal: 257/277, 301/321, 340/342/343 blocks with
c296 solitary on all 3 of its shapes), and by pattern
repetition negatively (only [296] repeats, ×3 with three
different standings: extra-only, no-cand, assigned). Task 2
discriminates by offset (+2 on 6/7 assigned with a single −1),
by row-shift spread (−1.5…+3.0 over 6 distinct values on 7
moves), by destination (5 fresh incl.
c298 vs 734's c342 collision taking 2), by assignment failure
(8/15 unassigned: 3 extra-only + 5 no-cand, incl. 711's full
pair wipe with no dest), and by the join (6/10 movers below
0.95; 3/9 below shapes move nothing; 4 movers read above
0.95 at J 0.9510–0.9902).

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

Screenshot: present by rule. The evidence census heatmap
(`m28-census.png`, 1270 B of 5242880 budget) colors the 764×8
census matrix (x = shape 0–763, y = named columns, green =
present, magenta = moved); DESIGN.md admits an evidence copy
iff H5 meets AND ≥3 mover shapes read below 0.95 — H5 meets
(0.6000) with 6 movers below 0.95.

Recorded without verdict: 10/764 shapes move ≥1 named column
(15 moved cells: 6 singles, 3 pairs, 1 triple; only the [296]
singleton repeats); assigned offsets read 6×+2 + 1×−1 with
row-shifts spread over 6 values; destinations read 5 fresh +
734's c342 collision; 8/15 moved cells assign no destination;
6/10 movers read below 0.95 while 2/3/700 read below with all
8 columns present; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| census suite + falsification bars, recorded before running | recorded | `DESIGN.md`: exact-match presence + overlap, nearest-private displacement, below-0.95 join, bars H1–H6/N |
| presence + displacement + join tables + wall/exit/shas/determinism | measured | §Step 2: 764×8 TSV + mover/pairing + offset/dest + 2×2 tables; 34.5 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a mover map discriminates (or absence reasoned) | measured | present by rule: H5 meets + 6 movers below 0.95; 1270 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m28"
cp local/research/M28/m28.py local/research/M28/control.py local/research/M28/DESIGN.md "/Volumes/Extreme SSD/m28/"
python3 m28.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m27/m27.txt" "/Volumes/Extreme SSD/m28" /Users/bradrichardson/dev/ssx3/local/research/M28 > m28.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m28/m28-census.tsv" local/research/M28/m28-census.tsv
cp "/Volumes/Extreme SSD/m28/m28-census.png" local/research/M28/m28-census.png
```

## Paths

Evidence (committed): `local/research/M28/` — `DESIGN.md`
(suite + bars, recorded before running), `m28.py`
(census + displacement + join + PNG writer), `control.py`
(known-column-move controls), `m28-census.tsv` (full 764×8
matrix, 54296 B), `m28-census.png` (heatmap, 1270 B,
rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m28/` —
`m28.txt` (receipt: shas, baselines, swap guard, Task-1/2
tables, join, re-run, PNG size), `control.txt`, `m28.py`,
`control.py`, `DESIGN.md` (working copies),
`m28-census.tsv` + `m28-census.png` (working copies). No
writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`,
`m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, or
other agents' dirs.

## Gap rows (exact next brief each needs)

1. Mover-above partial moves (new): 22/708/709/710 move single
   columns by 1–2 rows at J 0.9510–0.9902 (2 extra-only + 2
   no-cand, 0 assigned). Needs its own brief: per-byte
   attribution of the partial-move rows (values, gaps, bulk
   status on s0), offline — no new harness code.
2. Still-below divergence (new): 2/3/700 read below 0.95
   (0.9159/0.9340/0.8462) with all 8 named columns present —
   their divergence lies outside the named set. Needs its own
   brief: the same private/missing/displacement attribution
   for 2/3/700, offline — no new harness code.
3. Shape-711 pair wipe (new, minor): c342 + c343 fully missing
   with no assigned dest (no-cand both — 11 singleton private
   Y-cols exist on movers, tabled only as a count). Needs its
   own brief only if unassigned moves matter: singleton +
   far private-column listing per unassigned move, offline —
   no new harness code.
4. Shape-734 triple move (new, minor): c340 + c343 fully
   missing with a dest collision at c342 (+2/−1), c342 itself
   +2 rows extra-only. Needs its own brief only if collision
   moves matter: dest-row listing + value table for 734,
   offline — no new harness code.
5. Shape-732 c296→c298 move (new, minor): the only full
   single-column wipe with a fresh dest (rshift −1.5, the
   sole negative row-shift). Needs its own brief only if
   single full moves matter: dest-row listing + value table
   for 732, offline — no new harness code.
6. Below-0.95 shape family (M27 gap 2, still open — join half
   worked here): 9/700/734/732/2/711/3 unattributed at byte
   level (this run tables the 2×2 only). Needs its own brief:
   the same private/missing/displacement attribution for
   9/700/734/732/2/711/3, offline — no new harness code.
7. Static-on-other-frame privates (M27 gap 3, still open):
   15/19 733-privates + 13/18 731-privates read gap 0 on s0.
   Needs its own brief only if cross-shape membership
   matters, offline — no new harness code.
8. M26 gaps 1–10, 12–21 (still open, by reference): see M27
   REPORT gaps 4–23 for the exact brief each needs (TRI/POS/
   CONST collapse, peak agreement, index-top argmax, QUAD
   underfit, m15 c343 r289, SIGN near-hits, r-coherence,
   gap-bin 32–63, m15 privates, 700 map, m15 static maps, U/V
   co-residuals, δ-sign, m15 below-min tail, negatives,
   Odin readiness, top-HUD glyphs, carrier weight centers).

(M27 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No dest-row lists for non-guard moves: 732/734 assignments
   are tabled as offset/row-shift/min-shift only (brief pins
   row lists for 733/731 only).
2. No value-level attribution: δ values, gaps, and bulk
   status at moved/private sites are unattributed (census is
   set-level by brief).
3. No byte-level attribution beyond the join: 2/3/700's
   outside-named divergence is located, not attributed
   (gap 2 tables the follow-up).
4. c341 outside the census: guard-only (0 s0 sites) per
   brief's 8-column scope.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M28/`: `DESIGN.md`, `m28.py`,
`control.py`, `m28-census.tsv` (54296 B), `m28-census.png`
(1270 B), `REPORT.md` (this file).
