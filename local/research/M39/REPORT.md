# M39 — s3 all-delta-1 row: row-list + value comparison vs mixed cells: REPORT

M36 gap 3 worked at table level: s3's 7 cells recompute to the
M36-pinned row-lists, standings, deltas, and per-site values
exactly (10/10 row-lists + 14/14 value pins match — stop rule
not triggered), with s0's c316 row measured at [264] (the one
measured-not-pinned row-list). s3 reads 7/7 delta-1 (4
extra-only + 3 missing-only, zero mixed) against the 3 mixed
cells' d2/d3/d2. The missing sides agree values-deep
(medians 10 vs 10 — H4 met; ++ shares 2/3 vs 1/3 — H6 met)
while the extra sides differ in medians (8.0 vs 14.5 — H3
not met) and signs (3/4 vs 0/4 ++ — H5 not met); magnitude
>1 lives extra-side-only (s2c332's 2 — H7 met). Fully
offline — no lease of any kind, no boots, no harness code,
no `adb`. No device work. Runbook `local/muse/prompts/M39.md`.
Tables, no verdicts.

Headers read first: `local/research/M36/REPORT.md` (all of it:
gap 3 = this brief — s3's 7 cells extra-only c311/c316/c336/
c339 + missing-only c313/c314/c332, zero mixed, the only
still-below row with no mixed cell; s2's mixed c313/c332 +
s700's mixed c332 with deltas >1; the per-site |δ|/status/gap
tables this brief reproduces) plus `local/research/M38/
REPORT.md` (all of it: the pooled splits — missings 10/10
noncell on own Q, extras 14/10 bulk/noncell on s0; corrected
pooled universe 24 = c54's 10 + 14 others).

Time box 4 hours (start 2026-09-20 05:09 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`–`m38/` — all outputs went to the new
`/Volumes/Extreme SSD/m39/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only),
`m34-census.tsv` (FULL TSV guard), and `m36.txt` (s3's 7
cells + the 3 mixed cells to reproduce). Work dir
`/Volumes/Extreme SSD/m39/`; evidence `local/research/M39/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M38):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0002 | `56dccaff…8d2c8f8` |
| m16-mid-s0002 | `40f70d53…bd38be2` |
| m16-full-s0002 | `1593526a…0ed2417` |
| m16-v0-s0003 | `484d8499…e7fe462` |
| m16-mid-s0003 | `f0feefa7…93351fd` |
| m16-full-s0003 | `b11ecaa5…47f73d36` |
| m16-v0-s0700 | `cd5c2106…21af964` |
| m16-mid-s0700 | `d09dd3bb…25ae20` |
| m16-full-s0700 | `790c0826…dd5c482` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m34-census.tsv | `83482d1f…926c8aa8` |
| m36.txt | `bf2c5d81…8213ae1` |

(Full hexes in `m39.txt` §inputs. `m34-census.tsv` 163262 B;
`m36.txt` 102945 B — both match M38's committed sizes.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M38 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34–M38
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s2/s3/s700 cell reads 2469/2484/2605 (M36's
measured values — equal, not just tabled); FULL unnamed TSV
match (all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv`; 2/3/700 rows match the pinned k 6/7/8 +
n/ov + standings + deltas exactly; pooled counts read 5+4 /
4+3 / 15+3 exactly; all 34 pooled sites Y-plane; all 10
brief row-lists + all 14 brief value pins match M36 exactly
(§Task 1; s0c316's row measured at [264]). Mismatch rule
(DESIGN.md) not triggered.

## Runs (offline estimators)

One `m39.py` invocation (the receipt, 7.7 s, exit 0 — the
estimator was never changed after the receipt run started;
one earlier run stopped at the row-list guard on an estimator
set-expression bug — union/difference precedence in the
expected-Q-row construction, fixed before the receipt run;
all recomputed rows/values already matched M36 in that run);
one `control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m39.py receipt | 7.7 s | exit 0; all guards pass; canon `29130f5c…00dc26` |
| control.py C-UNIFORM | <1 s | green; standings + rows + values + gaps exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 7.2 s |
| Task 1 (row-lists + standings + values, 10 cells) | 3 | <1 s |
| Task 2 (extra/missing comparisons + delta split) | 10 | <1 s |
| Determinism re-run (Task 1 on s0+2+3+700, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m39.py` wall | — | 7.7 s |

## Step 2 — estimates

### Task 1 — s3 row + mixed cells recompute (do the cells reproduce?)

All 10 brief cells recomputed from the dumps (FULL TSV guard
passed first — all 764 rows byte-identical; 10/10 row-lists
+ 14/14 value pins match M36 exactly — offsets, |δ|,
statuses, signed gaps both frames):

Row-list table (all 10 cells: s0-rows vs Q-rows vs
extra/missing rows; s0c316 measured, not pinned):

| cell | s0 rows | Q rows | extra rows | miss rows |
| --- | --- | --- | --- | --- |
| s3 c311 | [296, 297, 298, 299] | [258, 296, 297, 298, 299] | [258] | [] |
| s3 c313 | [274, 275, 276, 292] | [274, 275, 292] | [] | [276] |
| s3 c314 | [269, 276, 277, 278, 287, 288, 289] | [269, 276, 277, 287, 288, 289] | [] | [278] |
| s3 c316 | [264] (measured) | [264, 265] | [265] | [] |
| s3 c332 | [295, 304] | [304] | [] | [295] |
| s3 c336 | [] | [238] | [238] | [] |
| s3 c339 | [] | [238] | [238] | [] |
| s2 c313 | [274, 275, 276, 292] | [274, 275, 292, 293] | [293] | [276] |
| s2 c332 | [295, 304] | [296, 297, 304] | [296, 297] | [295] |
| s700 c332 | [295, 304] | [296, 304] | [296] | [295] |

Standing table (7 × delta-1-uniform vs 3 × mixed):

| cell | n/ov | n0 | miss/extra | delta | standing |
| --- | --- | ---: | --- | ---: | --- |
| s3 c311 | 5/4 | 4 | 0/1 | 1 | extra-only |
| s3 c313 | 3/3 | 4 | 1/0 | 1 | missing-only |
| s3 c314 | 6/6 | 7 | 1/0 | 1 | missing-only |
| s3 c316 | 2/1 | 1 | 0/1 | 1 | extra-only |
| s3 c332 | 1/1 | 2 | 1/0 | 1 | missing-only |
| s3 c336 | 1/0 | 0 | 0/1 | 1 | extra-only |
| s3 c339 | 1/0 | 0 | 0/1 | 1 | extra-only |
| s2 c313 | 4/3 | 4 | 1/1 | 2 | mixed |
| s2 c332 | 3/1 | 2 | 1/2 | 3 | mixed |
| s700 c332 | 2/1 | 2 | 1/1 | 2 | mixed |

Value table — extra sites (all 8: cell, offset, (r,c);
|δ_Q|; s0 status + |δ_s0|; signed gaps g_Q vs g_s0; sign):

| cell | offset | (r,c) | \|δ_Q\| | s0 status | \|δ_s0\| | g_Q | g_s0 | sign |
| ---: | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| s3 c311 | 330862 | (258,311) | 34 | noncell | n/a | −71 | −71 | −− |
| s3 c316 | 339832 | (265,316) | 8 | bulk | 7 | 18 | 18 | ++ |
| s3 c336 | 305312 | (238,336) | 8 | bulk | 7 | 17 | 16 | ++ |
| s3 c339 | 305318 | (238,339) | 8 | noncell | n/a | 17 | 18 | ++ |
| s2 c313 | 375666 | (293,313) | 8 | bulk | 7 | −18 | −19 | −− |
| s2 c332 | 379544 | (296,332) | 20 | noncell | n/a | −41 | −41 | −− |
| s2 c332 | 380824 | (297,332) | 9 | noncell | n/a | −20 | −20 | −− |
| s700 c332 | 379544 | (296,332) | 20 | noncell | n/a | −42 | −41 | −− |

Value table — missing sites (all 6: |δ_s0|; Q status;
signed gaps g_s0 vs g_Q; sign):

| cell | offset | (r,c) | \|δ_s0\| | Q status | g_s0 | g_Q | sign |
| ---: | ---: | --- | ---: | --- | ---: | ---: | --- |
| s3 c313 | 353906 | (276,313) | 8 | noncell | 17 | 16 | ++ |
| s3 c314 | 356468 | (278,314) | 20 | noncell | 42 | 42 | ++ |
| s3 c332 | 378264 | (295,332) | 10 | noncell | −22 | −21 | −− |
| s2 c313 | 353906 | (276,313) | 8 | noncell | 17 | 16 | ++ |
| s2 c332 | 378264 | (295,332) | 10 | noncell | −22 | −21 | −− |
| s700 c332 | 378264 | (295,332) | 10 | noncell | −22 | −21 | −− |

### Task 2 — uniformity comparison (values-deep or standing-only?)

Extra-side comparison (s3's 4 vs the mixed cells' 4;
numbers only):

| group | sites (|δ_Q|, status, gaps, sign) |
| --- | --- |
| s3 (n=4) | (258,311) 34 noncell −71/−71 −−; (265,316) 8 bulk7 18/18 ++; (238,336) 8 bulk7 17/16 ++; (238,339) 8 noncell 17/18 ++ |
| mixed (n=4) | (293,313) 8 bulk7 −18/−19 −−; (296,332) 20 noncell −41/−41 −−; (297,332) 9 noncell −20/−20 −−; (296,332) 20 noncell −42/−41 −− |

| group | \|δ\| list | med | bulk | gaps (g_Q,g_s0) | signs |
| --- | --- | ---: | --- | --- | --- |
| s3 extras | [8, 8, 8, 34] | 8.0 | 2/4 | (17,16) (17,18) (−71,−71) (18,18) | 3 ++ / 1 −− |
| mixed extras | [8, 9, 20, 20] | 14.5 | 1/4 | (−18,−19) (−41,−41) (−20,−20) (−42,−41) | 0 ++ / 4 −− |

(Match rows: medians 8.0 vs 14.5, gap 6.5; bulk 2/4 vs 1/4;
++ shares 0.7500 vs 0.0000, gap 0.7500.)

Missing-side comparison (s3's 3 vs the mixed cells' 3;
numbers only):

| group | sites (|δ_s0|, status, gaps, sign) |
| --- | --- |
| s3 (n=3) | (276,313) 8 noncell 17/16 ++; (278,314) 20 noncell 42/42 ++; (295,332) 10 noncell −22/−21 −− |
| mixed (n=3) | (276,313) 8 noncell 17/16 ++; (295,332) 10 noncell −22/−21 −−; (295,332) 10 noncell −22/−21 −− |

| group | \|δ\| list | med | noncell | gaps (g_s0,g_Q) | signs |
| --- | --- | ---: | --- | --- | --- |
| s3 missings | [8, 10, 20] | 10 | 3/3 | (17,16) (42,42) (−22,−21) | 2 ++ / 1 −− |
| mixed missings | [8, 10, 10] | 10 | 3/3 | (17,16) (−22,−21) (−22,−21) | 1 ++ / 2 −− |

(Match rows: medians 10 vs 10, gap 0.0; noncell 3/3 vs 3/3;
++ shares 0.6667 vs 0.3333, gap 0.3333.)

Delta split (per-cell |extra delta| vs |missing delta|;
magnitude >1 lives extra-side-only):

| cell | extrad | missd | delta | mag>1 side |
| --- | ---: | ---: | ---: | --- |
| s3 c311 | 1 | 0 | 1 | none |
| s3 c313 | 0 | 1 | 1 | none |
| s3 c314 | 0 | 1 | 1 | none |
| s3 c316 | 1 | 0 | 1 | none |
| s3 c332 | 0 | 1 | 1 | none |
| s3 c336 | 1 | 0 | 1 | none |
| s3 c339 | 1 | 0 | 1 | none |
| s2 c313 | 1 | 1 | 2 | none |
| s2 c332 | 2 | 1 | 3 | extra |
| s700 c332 | 1 | 1 | 2 | none |

(Summary: extra-side deltas >1 count 1 (s2c332's 2);
missing-side deltas >1 count 0.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-UNIFORM (known 3×delta-1 + 1×mixed) | standings 2 extra-only + 1 missing-only + 1 mixed exact, rows exact, J 0.9524, values + gaps + statuses exact, other cols fixed, cell fixed, orig kept | exact | True |

(Uniform pool: 248 bulk gap≥17 Y; +8/−8/+8 landings at
(25,270)/(25,334)/(27,298) with orig |δ| 1/1/6. Missing
pool: 102 tail-Y; +1/+1 landings at (23,257)/(28,298), 0 −1
fallbacks. Spanned Y cols 257/270/298/334 with per-cell
standings extra-only ×2 + missing-only ×1 + mixed ×1 (col
298: extra r27 + miss r28 over s0 rows [28,29,34,35]),
rows exact on all 4, all other Y columns unchanged. Full
rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+2+3+700: row-lists + standings +
per-site values for the 10 cells, fresh loads) pass1
`29130f5c…00dc26` vs pass2 `29130f5c…00dc26`,
identical=True; 34/34 lines match=True; brief-cell sets
identical=True (s2 extras 3, missings 2; s3 4/3; s700 1/1).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_ROW_REPRO | 10/10 brief row-lists match M36 pins (s0c316 measured, n0=1) | 10/10, s0c316=[264] — met |
| H2_VALUE_REPRO | 14/14 brief value pins match M36 exactly | 14/14 — met |
| H3_EXTRA_AD_DEEP | \|med s3-extra − med mixed-extra\| ≤ 2 | 8.0 vs 14.5, gap 6.5 — not met |
| H4_MISS_AD_DEEP | \|med s3-miss − med mixed-miss\| ≤ 2 | 10 vs 10, gap 0.0 — met |
| H5_EXTRA_SIGN_DEEP | \|++ share s3 extras − mixed extras\| ≤ 0.25 | 0.7500 vs 0.0000, gap 0.7500 — not met |
| H6_MISS_SIGN_DEEP | \|++ share s3 missings − mixed missings\| ≤ 0.34 | 0.6667 vs 0.3333, gap 0.3333 — met |
| H7_DELTA_SIDE | per-side deltas >1: extra side 1 AND missing side 0 | 1/0 (s2c332) — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (10/10 row-lists + 14/14 value pins exact —
offsets, |δ|, statuses, both-frame gaps; the single
measured-not-pinned row s0c316=[264] with s3 holding
[264,265]), by standing (s3 7/7 delta-1 with 4 extra-only vs
3 missing-only and zero mixed; the 3 mixed cells read d2/d3/
d2), and by value identity (the mixed missing sides reuse
s3's own missing sites (276,313)/(295,332) with identical
gaps, while s3's (278,314)/20 stands alone). Task 2
discriminates by extra-side split (|δ| medians 8.0 vs 14.5
with s3's 34 the out-of-range high and the mixed 20/20 pair
unmatched on s3; bulk 2/4 vs 1/4; signs 3/4 ++ vs 0/4 ++ —
the extra-side sign line splits s3 from mixed exactly), by
missing-side agreement (medians 10 vs 10 with identical
multisets up to s3's 20-for-10 swap at the third site;
noncell 3/3 both; ++ shares 2/3 vs 1/3), and by delta side
(the only per-side magnitude >1 is s2c332's extra side at 2;
all 7 s3 sides and all 6 mixed non-extra sides read 0/1).

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

Screenshot: present by rule. The evidence uniformity map
(`m39-uniformmap.png`, 88526 B of 5242880 budget) colors
s3 extras green, mixed extras red, s3 missings yellow, and
mixed missings magenta; DESIGN.md admits an evidence copy
iff H1 meets AND H2 meets AND exactly one of {H3, H4} meets
— H1 + H2 meet (10/10 + 14/14) and exactly H4 meets (missing
medians 10 vs 10; extra medians 8.0 vs 14.5).

Recorded without verdict: s3's 7 cells recompute to all
delta-1 with 4 extra-only + 3 missing-only and zero mixed
while the 3 mixed cells read d2/d3/d2; s0c316's row measures
[264]; the missing sides agree at medians 10 vs 10 with ++
shares 2/3 vs 1/3 while the extra sides differ at medians
8.0 vs 14.5 with ++ shares 3/4 vs 0/4; the only per-side
magnitude >1 is s2c332's extra side; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| uniformity suite + falsification bars, recorded before running | recorded | `DESIGN.md`: row-list + standing + value tables, extra/missing-side comparisons, delta split, C-UNIFORM control, bars H1–H7/N |
| s3 row + mixed cells + wall/exit/shas/determinism | measured | §Step 2: 10/10 rows + 7-vs-3 standings + 14 values + comparisons + split; 7.7 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a uniformity map discriminates (or absence reasoned) | measured | present by rule: H1 + H2 + exactly one of H3/H4; 88526 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m39"
cp local/research/M39/m39.py local/research/M39/control.py local/research/M39/DESIGN.md "/Volumes/Extreme SSD/m39/"
python3 m39.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m36/m36.txt" "/Volumes/Extreme SSD/m39" /Users/bradrichardson/dev/ssx3/local/research/M39 > m39.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m39/m39-uniformmap.png" local/research/M39/m39-uniformmap.png
```

## Paths

Evidence (committed): `local/research/M39/` — `DESIGN.md`
(suite + bars, recorded before running), `m39.py`
(row-lists + standings + values + comparisons + delta split
+ PNG writer), `control.py` (known-uniform+mixed control),
`m39-uniformmap.png` (uniformity map, 88526 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m39/` —
`m39.txt` (receipt: shas, baselines, guards, 34-site pins,
row-list pins, Task-1/2 tables, re-run, PNG size),
`control.txt`, `m39.py`, `control.py`, `DESIGN.md` (working
copies), `m39-uniformmap.png` (working copy). No writes into
`m15/`–`m38/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Extra-side sign asymmetry (new, minor): s3's extras read
   3/4 ++ while the mixed cells' extra sides read 0/4 ++ —
   the extra-side sign line splits s3 from mixed exactly
   (the missing sides agree 2/3 vs 1/3). Needs its own brief
   only if extra-side gap signs matter: per-cell extra-side
   gap-sign comparison across all 21 still-below cells,
   offline — no new harness code.
2. Extra-side |δ| spread (new, minor): s3 extras read
   [8,8,8,34] (med 8.0) vs mixed extra sides [8,9,20,20]
   (med 14.5) — s3's 34 and the mixed 20/20 pair are
   unmatched on the other side (the missing sides agree at
   med 10). Needs its own brief only if extra-side
   magnitudes matter: |δ_Q| distribution per cell across
   the 21 still-below cells, offline — no new harness code.
3. M38 gap 1 (still open, by reference): see M38 REPORT gap
   1 for the exact brief it needs ((278,314) diverge-by-2).
4. M37 gaps 1–2 (still open, by reference): see M37 REPORT
   gaps 1–2 for the exact brief each needs (s761's
   column-54 tail quartet; 701 mask column block 54–65).
5. M36 gaps 4–6 (still open, by reference): see M36 REPORT
   gaps 4–6 for the exact brief each needs (M35 gaps 1–3;
   M34 gaps 3–4; M33 gaps 1, 4–5).
6. M35 gaps 1–3 (still open, by reference): see M35 REPORT
   gaps 1–3 for the exact brief each needs (per-cell
   standing asymmetry; near-miss triple; big-|δ| unnamed
   sites).
7. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns; same-column opposite standings).

(M36 gap 3 — this brief — worked at table level above.)

## What I could not do

1. No per-site values beyond the 10 brief cells: δ values
   and gaps at other unnamed moved cells are M36's tables
   by reference (brief pins s3's 7 + the 3 mixed cells
   only).
2. No rule for the extra-side splits: the extra-side median
   gap (8.0 vs 14.5) and sign split (3/4 vs 0/4 ++) are
   attributed per side per site, no rule (gap rows 1–2).
3. No destination assignment for unnamed moves: row-deltas
   are tabled without the M28-style displacement step
   (brief pins row-lists + values only).
4. No explanation: values are attributed per site per
   side, no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M39/`: `DESIGN.md`, `m39.py`,
`control.py`, `m39-uniformmap.png` (88526 B, rule-met),
`REPORT.md` (this file).
