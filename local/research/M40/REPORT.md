# M40 — Shape-9 per-cell standing asymmetry: row-list + value comparison: REPORT

M35 gap 1 worked at table level: s9's 4 missing-bearing cells
recompute to the M35-pinned rows, standings, deltas, and
per-site values exactly (4/4 row pins + 13/13 value pins match
— stop rule not triggered), with s0's c311/c312 rows measured
at [296,297,298,299]/[299,300,301] (the two measured-not-pinned
row-lists). The missing sides split in medians (10.0 vs 17.5
— H3 not met) while agreeing in signs (4/4 vs 4/4 ++ — H4
met); the extra sides agree in medians (13.0 vs 13) while
splitting in signs (2/4 vs 1/1 ++ — H5 not met) and bulk
status (2/4 vs 1/1); neither n0 nor overlap separates the
bulk-side cells from the noncell-side cells (H6 not met);
all 4 missing sides read pure (H7 met). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M40.md`. Tables, no
verdicts.

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 1 = this brief — 4 missing-bearing cells 311/312/314/315
with standings + deltas + per-site |δ|/status/gap tables this
brief reproduces; c314's 3 missings all noncell at |δ|
12/23/45 vs c315's 2 all bulk at 10/10; headliner row-lists
for c314/c315) plus `local/research/M39/REPORT.md` (all of it:
comparison precedent — missing-side agreement vs extra-side
split; corrected pooled universe 24 = c54's 10 + 14 others).

Time box 4 hours (start 2026-09-20 05:18 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`–`m39/` — all outputs went to the new
`/Volumes/Extreme SSD/m40/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only),
`m34-census.tsv` (FULL TSV guard), and `m35.txt` (the 4 cells
to reproduce). Work dir `/Volumes/Extreme SSD/m40/`; evidence
`local/research/M40/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M39; s9 prefixes match M35):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0009 | `1926a151…ea086fe0` |
| m16-mid-s0009 | `a9fa67fb…bd5e9806` |
| m16-full-s0009 | `a9a5339d…207ae486` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m34-census.tsv | `83482d1f…926c8aa8` |
| m35.txt | `ff29739c…49349c` |

(Full hexes in `m40.txt` §inputs. `m34-census.tsv` 163262 B;
`m35.txt` 69947 B.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M39 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34–M39
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s9 cell reads 2670 (M35's measured value —
equal, not just tabled); FULL unnamed TSV match (all 764 rows:
tail + J4 + all-33-column n/ov/pres) vs `m34-census.tsv`; s9
row matches the pinned k 15 + n/ov + standings + deltas
exactly; pooled counts read 22+8 exactly; all pooled sites
Y-plane; all 4 brief row pins + all 13 brief value pins match
M35 exactly (§Task 1; s0c311/s0c312 rows measured at
[296,297,298,299]/[299,300,301]). Mismatch rule (DESIGN.md)
not triggered.

## Runs (offline estimators)

Two `m40.py` invocations (the receipt, 6.4 s, exit 0 — the
estimator was changed once between runs for a receipt-cosmetic
H7 numerator label, outside the determinism canon; canon sha
identical across both runs); one `control.py` invocation
(green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m40.py receipt | 6.4 s | exit 0; all guards pass; canon `b1458cf8…e24339` |
| control.py C-SPLIT | <1 s | green; standings + rows + values + gaps exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 6.1 s |
| Task 1 (row-lists + standings + values, 4 cells) | 1 | <1 s |
| Task 2 (missing/extra/row-shape comparisons) | 4 | <1 s |
| Determinism re-run (Task 1 on s0+9, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m40.py` wall | — | 6.4 s |

## Step 2 — estimates

### Task 1 — 4-cell recompute (do the cells reproduce?)

All 4 brief cells recomputed from the dumps (FULL TSV guard
passed first — all 764 rows byte-identical; 4/4 row pins +
13/13 value pins match M35 exactly — offsets, |δ|, statuses,
signed gaps both frames):

Row-list table (all 4 cells: s0-rows vs s9-rows vs
extra/missing rows; s0c311/s0c312 measured, not pinned):

| cell | s0 rows | s9 rows | extra rows | miss rows |
| --- | --- | --- | --- | --- |
| c311 | [296, 297, 298, 299] (measured) | [297, 298, 299] | [] | [296] |
| c312 | [299, 300, 301] (measured) | [248, 300] | [248] | [299, 301] |
| c314 | [269, 276, 277, 278, 287, 288, 289] | [246, 276, 277, 278, 287] | [246] | [269, 288, 289] |
| c315 | [266, 267, 268, 273, 274, 275, 276] | [245, 267, 268, 274, 275, 276, 289, 290] | [245, 289, 290] | [266, 273] |

Standing table (1 × missing-only d1 vs 3 × mixed d3/d4/d5):

| cell | n/ov | n0 | miss/extra | delta | standing |
| --- | --- | ---: | --- | ---: | --- |
| c311 | 3/3 | 4 | 1/0 | 1 | missing-only |
| c312 | 2/1 | 3 | 2/1 | 3 | mixed |
| c314 | 5/4 | 7 | 3/1 | 4 | mixed |
| c315 | 8/5 | 7 | 2/3 | 5 | mixed |

Value table — extra sites (all 5: cell, offset, (r,c);
|δ_9|; s0 status + |δ_s0|; signed gaps g_9 vs g_s0; sign):

| cell | offset | (r,c) | \|δ_9\| | s0 status | \|δ_s0\| | g_9 | g_s0 | sign |
| ---: | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| 312 | 318064 | (248,312) | 13 | bulk | 1 | 33 | 10 | ++ |
| 314 | 315508 | (246,314) | 13 | bulk | 1 | 32 | 9 | ++ |
| 315 | 314230 | (245,315) | 13 | bulk | 2 | 60 | 6 | ++ |
| 315 | 370550 | (289,315) | 16 | noncell | n/a | −34 | 0 | −0 |
| 315 | 371830 | (290,315) | 11 | noncell | n/a | −26 | −2 | −− |

Value table — missing sites (all 8: |δ_s0|; s9 status +
|δ_9|; signed gaps g_s0 vs g_9; sign):

| cell | offset | (r,c) | \|δ_s0\| | s9 status | \|δ_9\| | g_s0 | g_9 | sign |
| ---: | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| 311 | 379502 | (296,311) | 10 | noncell | n/a | 24 | 7 | ++ |
| 312 | 383344 | (299,312) | 10 | bulk | 6 | 22 | 16 | ++ |
| 312 | 385904 | (301,312) | 9 | bulk | 7 | 28 | 28 | ++ |
| 314 | 344948 | (269,314) | 12 | noncell | n/a | 41 | 29 | ++ |
| 314 | 369268 | (288,314) | 45 | noncell | n/a | 107 | 84 | ++ |
| 314 | 370548 | (289,314) | 23 | noncell | n/a | 54 | 31 | ++ |
| 315 | 341110 | (266,315) | 10 | bulk | 2 | 64 | 46 | ++ |
| 315 | 350070 | (273,315) | 10 | bulk | 3 | 23 | 23 | ++ |

### Task 2 — asymmetry comparison (row-deep or missing-only?)

Missing-side comparison (all-bulk c312/c315 vs all-noncell
c311/c314; numbers only):

| group | sites (\|δ_s0\|, status, gaps, sign) |
| --- | --- |
| bulk-side (n=4) | (266,315) 10 bulk2 64/46 ++; (273,315) 10 bulk3 23/23 ++; (299,312) 10 bulk6 22/16 ++; (301,312) 9 bulk7 28/28 ++ |
| noncell-side (n=4) | (269,314) 12 noncell 41/29 ++; (288,314) 45 noncell 107/84 ++; (289,314) 23 noncell 54/31 ++; (296,311) 10 noncell 24/7 ++ |

| group | \|δ\| list | med | gaps (g_s0,g_9) | signs |
| --- | --- | ---: | --- | --- |
| bulk-side missings | [9, 10, 10, 10] | 10.0 | (64,46) (23,23) (22,16) (28,28) | 4 ++ / 0 −− |
| noncell-side missings | [10, 12, 23, 45] | 17.5 | (41,29) (107,84) (54,31) (24,7) | 4 ++ / 0 −− |

(Match rows: medians 10.0 vs 17.5, gap 7.5; ++ shares 1.0000
vs 1.0000, gap 0.0000. Bulk-side |δ_9| list [2, 3, 6, 7].)

Extra-side comparison (extras of bulk-side cells vs extras of
noncell-side cells; c311 has no extras — tabled; numbers
only):

| group | sites (\|δ_9\|, status, gaps, sign) |
| --- | --- |
| bulk-side (n=4) | (245,315) 13 bulk2 60/6 ++; (248,312) 13 bulk1 33/10 ++; (289,315) 16 noncell −34/0 −0; (290,315) 11 noncell −26/−2 −− |
| noncell-side (n=1) | (246,314) 13 bulk1 32/9 ++ |

| group | \|δ\| list | med | bulk | gaps (g_9,g_s0) | signs |
| --- | --- | ---: | --- | --- | --- |
| bulk-side extras | [11, 13, 13, 16] | 13.0 | 2/4 | (60,6) (33,10) (−34,0) (−26,−2) | 2 ++ / 1 −− / 1 −0 |
| noncell-side extras | [13] | 13 | 1/1 | (32,9) | 1 ++ / 0 −− |

(Match rows: medians 13.0 vs 13, gap 0.0; bulk 2/4 vs 1/1;
++ shares 0.5000 vs 1.0000, gap 0.5000.)

Row-shape comparison (n0/n/ov per cell; does row shape
predict the bulk/noncell side?):

| cell | side | n0 | n | ov | miss/extra/delta |
| --- | --- | ---: | ---: | ---: | --- |
| c311 | noncell | 4 | 3 | 3 | 1/0/1 |
| c312 | bulk | 3 | 2 | 1 | 2/1/3 |
| c314 | noncell | 7 | 5 | 4 | 3/1/4 |
| c315 | bulk | 7 | 8 | 5 | 2/3/5 |

(Separation legs: n0 bulk-side [3, 7] vs noncell-side [4, 7],
separates=False; overlap bulk-side [1, 5] vs noncell-side
[3, 4], separates=False.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-SPLIT (known 2×bulk-missing + 2×noncell-missing) | standings 4×missing-only exact, rows exact, J 0.9608, values + gaps + statuses exact, other cols fixed, mask shrinks exact, orig kept | exact | True |

(Bulk pool: 2 injected ±1 landings at (23,257)/(23,277) with
|δ|=1 bulk on B. Noncell pool: 2 injected endpoint landings
at (23,301)/(23,321), v0-endpoint, verified noncell on B. All
4 cells missing-only d1 with mirows [23] over s0 rows
[23..32]/[23..33]; gaps equal both frames at all 4 sites
(42/37/43/36); cell-7 mask = maskA minus exactly the 2
noncell sites; J 98/102. Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+9: row-lists + standings + per-site
values for the 4 cells, fresh loads) pass1
`b1458cf8…e24339` vs pass2 `b1458cf8…e24339`,
identical=True; 21/21 lines match=True; brief-cell sets
identical=True (extras 5, missings 8).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_ROW_REPRO | 4/4 brief row pins match M35 (c314/c315 full rows; c311/c312 n0 + extra/miss rows) | 4/4, s0c311=[296,297,298,299] s0c312=[299,300,301] — met |
| H2_VALUE_REPRO | 13/13 brief value pins match M35 exactly | 13/13 — met |
| H3_MISS_AD_DEEP | \|med bulk-miss − med noncell-miss\| ≤ 2 | 10.0 vs 17.5, gap 7.5 — not met |
| H4_MISS_SIGN_DEEP | \|++ share bulk missings − noncell missings\| ≤ 0.25 | 1.0000 vs 1.0000, gap 0.0000 — met |
| H5_EXTRA_SIGN_DEEP | \|++ share bulk-side extras − noncell-side extras\| ≤ 0.25 | 0.5000 vs 1.0000, gap 0.5000 — not met |
| H6_ROW_PREDICT | n0 separates OR overlap separates the sides | n0 [3,7] vs [4,7] no; ov [1,5] vs [3,4] no — not met |
| H7_CELL_PURITY | each brief missing side reads pure (4/4) | 0/1, 2/2, 0/3, 2/2 bulk — 4/4 pure — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (4/4 row pins + 13/13 value pins exact —
offsets, |δ|, statuses, both-frame gaps; the two
measured-not-pinned rows s0c311=[296,297,298,299] with s9
holding [297,298,299] and s0c312=[299,300,301] with s9
holding [248,300]), by standing (c311 missing-only d1 vs
c312/c314/c315 mixed d3/d4/d5), and by missing-side purity
(c312/c315 2/2 + 2/2 bulk with |δ_9| 6/7/2/3 while c311/c314
read 0/1 + 0/3 bulk). Task 2 discriminates by missing-side
split (|δ| medians 10.0 vs 17.5 with the noncell 45/23 pair
unmatched on the bulk side; signs 4/4 ++ both), by
extra-side split (|δ| medians 13.0 vs 13 with bulk 2/4 vs
1/1; signs 2/4 ++ vs 1/1 ++ — c315's −0/−− pair lives on
the bulk-side cell), and by row shape negatively (n0 3/7 vs
4/7 and overlap 1/5 vs 3/4 interleave — neither leg
separates).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; per-cell tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence asymmetry map
(`m40-asymmetrymap.png`, 88545 B of 5242880 budget) colors
bulk-side missings cyan, noncell-side missings magenta,
bulk-side extras green, and noncell-side extras red; DESIGN.md
admits an evidence copy iff H1 meets AND H2 meets AND exactly
one of {H3, H4} meets — H1 + H2 meet (4/4 + 13/13) and
exactly H4 meets (missing signs 4/4 vs 4/4; missing medians
10.0 vs 17.5).

Recorded without verdict: s9's 4 missing-bearing cells
recompute to c311 missing-only d1 + c312/c314/c315 mixed
d3/d4/d5 with s0c311/s0c312 rows measuring [296,297,298,299]/
[299,300,301]; the missing sides split at medians 10.0 vs
17.5 with ++ shares 4/4 vs 4/4 while the extra sides agree at
medians 13.0 vs 13 with ++ shares 2/4 vs 1/1; neither n0 nor
overlap separates the bulk-side cells from the noncell-side
cells; all 4 missing sides read pure; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| asymmetry suite + falsification bars, recorded before running | recorded | `DESIGN.md`: row-list + standing + value tables, missing/extra-side comparisons, row-shape split, C-SPLIT control, bars H1–H7/N |
| 4-cell row + comparisons + wall/exit/shas/determinism | measured | §Step 2: 4/4 rows + standings + 13 values + comparisons + split; 6.4 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if an asymmetry map discriminates (or absence reasoned) | measured | present by rule: H1 + H2 + exactly one of H3/H4; 88545 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the second invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m40"
cp local/research/M40/m40.py local/research/M40/control.py local/research/M40/DESIGN.md "/Volumes/Extreme SSD/m40/"
python3 m40.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m35/m35.txt" "/Volumes/Extreme SSD/m40" /Users/bradrichardson/dev/ssx3/local/research/M40 > m40.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m40/m40-asymmetrymap.png" local/research/M40/m40-asymmetrymap.png
```

## Paths

Evidence (committed): `local/research/M40/` — `DESIGN.md`
(suite + bars, recorded before running), `m40.py`
(row-lists + standings + values + comparisons + row-shape
split + PNG writer), `control.py` (known-split control),
`m40-asymmetrymap.png` (asymmetry map, 88545 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m40/` —
`m40.txt` (receipt: shas, baselines, guards, row pins, 30-site
pins, Task-1/2 tables, re-run, PNG size), `control.txt`,
`m40.py`, `control.py`, `DESIGN.md` (working copies),
`m40-asymmetrymap.png` (working copy). No writes into
`m15/`–`m39/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Missing-side magnitude split (new, minor): bulk-side
   missings read [9,10,10,10] (med 10.0) vs noncell-side
   [10,12,23,45] (med 17.5) — the 45/23 pair is unmatched on
   the bulk side (the signs agree 4/4 vs 4/4). Needs its own
   brief only if missing-side magnitudes matter: |δ_s0|
   distribution per missing-bearing cell across all
   still-below rows, offline — no new harness code.
2. Extra-side sign split (new, minor): bulk-side extras read
   2/4 ++ (c315's −0/−− pair) vs noncell-side 1/1 ++ —
   the extra-side sign line does not follow the missing-side
   bulk line cleanly. Needs its own brief only if extra-side
   gap signs matter: per-cell extra-side gap-sign comparison
   across all still-below rows, offline — no new harness
   code.
3. M39 gaps 1–2 (still open, by reference): see M39 REPORT
   gaps 1–2 for the exact brief each needs (extra-side sign
   asymmetry; extra-side |δ| spread).
4. M38 gap 1 (still open, by reference): see M38 REPORT gap
   1 for the exact brief it needs ((278,314) diverge-by-2).
5. M37 gaps 1–2 (still open, by reference): see M37 REPORT
   gaps 1–2 for the exact brief each needs (s761's
   column-54 tail quartet; 701 mask column block 54–65).
6. M36 gaps 4–6 (still open, by reference): see M36 REPORT
   gaps 4–6 for the exact brief each needs (M35 gaps 1–3;
   M34 gaps 3–4; M33 gaps 1, 4–5).
7. M35 gaps 2–3 (still open, by reference): see M35 REPORT
   gaps 2–3 for the exact brief each needs (near-miss
   triple; big-|δ| unnamed sites).
8. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns; same-column opposite standings).

(M35 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No per-site values beyond the 4 brief cells: δ values
   and gaps at other unnamed moved cells are M35's tables
   by reference (brief pins the 4 missing-bearing cells
   only).
2. No rule for the missing-side magnitude split: the median
   gap (10.0 vs 17.5) and the extra-side sign split (2/4
   vs 1/1 ++) are attributed per side per site, no rule
   (gap rows 1–2).
3. No destination assignment for unnamed moves: row-lists
   are tabled without the M28-style displacement step
   (brief pins row-lists + values only).
4. No explanation: values are attributed per site per
   side, no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M40/`: `DESIGN.md`, `m40.py`,
`control.py`, `m40-asymmetrymap.png` (88545 B, rule-met),
`REPORT.md` (this file).
