# M29 — Partial-move attribution: per-byte rows for 22/708/709/710: REPORT

M28 gap 1 worked at table level: the 6 recomputed partial-move
cells (global scan over all 764 — exactly the 6 pinned cells,
n/ov/standing matching M28 exactly, stop rule not triggered)
hold 9 delta-row sites (5 extra + 4 missing, all Y): the 4
missing rows sit in-span (708 c296 r28; 709 c301 r33; 710 c340
r31/r34) while only 2 of the 5 extra rows sit span-adjacent
(734-c342 r26/r33, ±1 row); the other 3 extras read far outside
their column spans (9 c321 r266, +234 rows; 22 c296 r400/r401,
+366/+367 rows). 7/9 delta sites read other-frame bulk
(|δ| 1–5, 0 near-misses) and 2/9 non-cell (both s22); 8/9 read
s0-P1 dec-9; extra |δ| medians 8–9 vs missing 18.0; RT-PRES
tolerates all 6 cells (movers 10→5) while RT-DEST assigns 0/4
(all 3 missing-only shapes hold zero private-Y sites). Fully
offline — no lease of any kind, no boots, no harness code, no
`adb`. No device work. Runbook `local/muse/prompts/M29.md`.
Tables, no verdicts.

Headers read first: `local/research/M28/REPORT.md` (all of it:
10 movers / 15 moved cells, 7 assigned + 3 extra-only + 5
no-cand; partials 22 c296 11/9 extra-only, 708 c296 8/8 −1,
709 c301 10/10 −1, 710 c340 6/6 −2 at J 0.9510–0.9902, 0
assigned; extras also 9 c321 11/10 + 734 c342 7/5) plus
`local/research/M27/REPORT.md` (Task-1 per-site table
precedent: offset/plane/row/col, cross-frame |δ|, signed gaps
both frames; full-swap reference: priv/miss 100% band-0, miss
100% dec-9, all non-cell on the other frame).

Time box 4 hours (start 2026-09-20 03:19 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m28/` — all outputs went to the new
`/Volumes/Extreme SSD/m29/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and `m28.txt`
+ `m28-census.tsv` (match targets). Work dir `/Volumes/Extreme
SSD/m29/`; evidence `local/research/M29/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M28):

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
| m16-v0-s0708 | `301701b2…48b3bf` |
| m16-mid-s0708 | `cbc5bf18…3d36a0c1` |
| m16-full-s0708 | `c1a5d5f7…884146b` |
| m16-v0-s0709 | `6b776020…85fb471f` |
| m16-mid-s0709 | `bb35990e…2dcdac9f` |
| m16-full-s0709 | `6d1e6b6d…00cb5a1` |
| m16-v0-s0710 | `bd8485ef…4c4ab58` |
| m16-mid-s0710 | `af6b7eb2…4c5108d8c4` |
| m16-full-s0710 | `842e402f…3eeb2c6` |
| m16-v0-s0734 | `82467b1f…4bddbb` |
| m16-mid-s0734 | `45de5504…5977d26` |
| m16-full-s0734 | `f60ddd16…e038600f` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m28.txt | `87a12157…398faf25` |
| m28-census.tsv | `27872527…7ca15a9e7f` |

(Full hexes in `m29.txt` §inputs, plus all 30 top-10-carrier
triplet bins. Triplet fold sha over all 764×3 bins:
`6c906897…61fd423b1` — matches M28 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M28 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 reference
row lists + guard-only c341 n=0 match exactly. M28 TSV match
on all 6 shapes (tail + J4 + all-8-column n/ov/pres) + M28
standing match on the 6 partial cells (3 extra-only + 3
no-cand) + global partial-cell scan (exactly the 6 pinned
cells over all 764). Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m29.py` invocation (the receipt, 24.7 s, exit 0); one
`control.py` invocation (green). Two pre-receipt estimator
fixes (determinism canon line order; control fallback-column
handling for non-named columns) — the receipt run below is the
single recorded invocation.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m29.py receipt | 24.7 s | exit 0; all guards pass; canon `f086446f…3cacb517` |
| control.py C-PART-MISS + C-PART-EXTRA | <1 s | green; sets + J + standings + values exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + census fields) | 764 | 22.7 s |
| Task 1 (delta rows + per-site + joins) | 6 | 0.3 s |
| Task 2 (pools + RT rules) | 6 | 0.0 s |
| Determinism re-run (Task 1 on s0+22+708) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m29.py` wall | — | 24.7 s |

## Step 2 — estimates

### Task 1 — delta-row tables (what are the ±1–2 rows?)

Per-shape delta rows recomputed from the dumps (n/ov/standing
match M28 exactly — stop rule not triggered). Span distance =
|row − nearest s0 span row| in the moved column (0 = in-span;
derived from receipt rows + DESIGN-pinned spans):

| Shape | col | n/ov | extra rows | missing rows | span dist |
| ---: | ---: | --- | --- | --- | --- |
| 9 | 321 | 11/10 | [266] | [] | 266:+234 |
| 22 | 296 | 11/9 | [400, 401] | [] | 400:+366, 401:+367 |
| 708 | 296 | 8/8 | [] | [28] | 28:0 |
| 709 | 301 | 10/10 | [] | [33] | 33:0 |
| 710 | 340 | 6/6 | [] | [31, 34] | 31:0, 34:0 |
| 734 | 342 | 7/5 | [26, 33] | [] | 26:1, 33:1 |

Full priv/miss/shared sets per analyzed shape (counts + J;
delta rows are the in-column subset — asserted in-receipt):

| Shape | tail | J vs s0 | priv | miss | shared | outside-col priv | outside-col miss |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 9 | 117 | 0.7520 | 23 | 8 | 94 | 22 (r226–305 cluster) | 8 (r266–301) |
| 22 | 106 | 0.9623 | 4 | 0 | 102 | 2: (393,307), (402,295) | 0 |
| 708 | 101 | 0.9902 | 0 | 1 | 101 | 0 | 0 |
| 709 | 97 | 0.9510 | 0 | 5 | 97 | 0 | 4: c298 r28/29/34/35 |
| 710 | 100 | 0.9804 | 0 | 2 | 100 | 0 | 0 |
| 734 | 94 | 0.8846 | 2 | 10 | 92 | 0 | 10: c340 ×8 + c343 ×2 |

(s9 outside-col privates: (226,351), (232,327), (233,327),
(234,337), (235,337), (239,336), (239,339), (240,318),
(241,318), (243,318), (244,316), (245,315), (245,316),
(246,314), (248,312), (252,310), (269,313), (270,313),
(274,322), (289,315), (290,315), (305,332); missings:
(266,315), (269,314), (273,315), (288,314), (289,314),
(296,311), (299,312), (301,312) — full lists in `m29.txt`.)

Per-site delta-row table (all 9: offset, plane, row, col;
|δ| here; other-shape status + |δ|; signed gaps here vs
other; s0-P1 decile, band, span position):

| shape | offset | plane | (r,c) | kind | \|δ\| | other status | \|δ_o\| | g_here | g_other | dec | band | pos |
| ---: | ---: | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 9 | 341122 | Y | (266,321) | extra | 9 | bulk | 1 | 19 | 3 | 9 | 1 | EDGE/BOTTOM |
| 22 | 512592 | Y | (400,296) | extra | 8 | noncell | n/a | 22 | −1 | 9 | 2 | EDGE/BOTTOM |
| 22 | 513872 | Y | (401,296) | extra | 8 | noncell | n/a | 24 | −2 | 9 | 2 | EDGE/BOTTOM |
| 708 | 36432 | Y | (28,296) | miss | 19 | bulk | 5 | 40 | 12 | 9 | 0 | INTERIOR/TOP |
| 709 | 42842 | Y | (33,301) | miss | 13 | bulk | 3 | 27 | 7 | 9 | 0 | EDGE/BOTTOM |
| 710 | 40360 | Y | (31,340) | miss | 44 | bulk | 5 | 90 | 11 | 9 | 0 | INTERIOR/BOTTOM |
| 710 | 44200 | Y | (34,340) | miss | 17 | bulk | 4 | 35 | 10 | 8 | 0 | EDGE/BOTTOM |
| 734 | 33964 | Y | (26,342) | extra | 21 | bulk | 3 | −50 | −8 | 9 | 0 | EDGE/TOP |
| 734 | 42924 | Y | (33,342) | extra | 11 | bulk | 5 | −26 | −13 | 9 | 0 | INTERIOR/BOTTOM |

Summary: near 0 (0.0000), far 7 (0.7778, bulk |δ| 1/3/3/4/5/5/5),
noncell 2 (0.2222, both s22). Signed-gap equality 0/9,
abs-gap equality 0/9.

Per-shape near-miss shares (H1/H2-style):

| Shape | n | near | far | noncell |
| ---: | ---: | --- | --- | --- |
| 9 | 1 | 0 (0.0000) | 1 (1.0000) | 0 (0.0000) |
| 22 | 2 | 0 (0.0000) | 0 (0.0000) | 2 (1.0000) |
| 708 | 1 | 0 (0.0000) | 1 (1.0000) | 0 (0.0000) |
| 709 | 1 | 0 (0.0000) | 1 (1.0000) | 0 (0.0000) |
| 710 | 2 | 0 (0.0000) | 2 (1.0000) | 0 (0.0000) |
| 734 | 2 | 0 (0.0000) | 2 (1.0000) | 0 (0.0000) |

Position join, pooled (extra 5 / missing 4 / shared = s0 tail
102; s0-anchored M27 machinery verbatim):

Band (missing all band-0; extras split 2/1/2):

| band | priv n/share | miss n/share | shared n/share |
| ---: | --- | --- | --- |
| 0 | 2 / 0.4000 | 4 / 1.0000 | 69 / 0.6765 |
| 1 | 1 / 0.2000 | 0 / 0.0000 | 25 / 0.2451 |
| 2 | 2 / 0.4000 | 0 / 0.0000 | 8 / 0.0784 |

Gradient decile (extras all dec-9; missings 3 dec-9 + 1 dec-8):

| dec | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 0–5 | 0 | 0 | 0 |
| 6 | 0 | 0 | 2 |
| 7 | 0 | 0 | 2 |
| 8 | 0 | 1 | 6 |
| 9 | 5 | 3 | 92 |

(Dec-9 shares: priv 5/5 = 1.0000, miss 3/4 = 0.7500, shared
92/102 = 0.9020. The dec-8 missing site is s710 r34.)

Streak columns (delta sites in their moved column by
construction; shared = s0 baseline):

| col | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 257 | 0 | 0 | 10 |
| 277 | 0 | 0 | 10 |
| 296 | 2 | 1 | 9 |
| 301 | 0 | 1 | 11 |
| 321 | 1 | 0 | 10 |
| 340 | 0 | 2 | 8 |
| 341 | 0 | 0 | 0 |
| 342 | 2 | 0 | 5 |
| 343 | 0 | 0 | 2 |
| other | 0 | 0 | 37 |

Carrier cut (inside counts; the 1 shared byte in 368's mask is
M22's tabled max-1 byte; the 1 extra byte in 693's mask is
s9's (266,321)):

| rank/shape | priv_in | miss_in | shared_in |
| ---: | ---: | ---: | ---: |
| 1/694, 3/701, 5–10 | 0 | 0 | 0 |
| 2/693 | 1 | 0 | 0 |
| 4/368 | 0 | 0 | 1 |

701 split: priv 0/5, miss 0/4, shared 0/102 (all outside).

Per-shape joins: band — s9 extra band-1 (shared 69/19/6),
s22 extras band-2 (shared 69/25/8), s708/s709/s710 missings
band-0, s734 extras band-0; dec-9 shares — s9 1/1, s22 2/2,
s708 1/1, s709 1/1, s710 1/2, s734 2/2; carriers — all 0
except s9's extra in 693; 701 splits all outside (full
per-shape rows in `m29.txt`).

### Task 2 — extra-only vs missing-only (two populations?)

Pooled extra[22,9] (n=3) vs missing[708,709,710] (n=4) vs
extra[all] (n=5, the H5 denominator):

| Pool | n | \|δ\| vals | med | gQ +/−/0 | gO +/−/0 | ostat | EDGE | TOP |
| --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| extra[22,9] | 3 | 8, 8, 9 | 8 | 3/0/0 | 1/2/0 | bulk 1, noncell 2 | 3/3 | 0/3 |
| missing | 4 | 13, 17, 19, 44 | 18.0 | 4/0/0 | 4/0/0 | bulk 4 | 2/4 | 1/4 |
| extra[all] | 5 | 8, 8, 9, 11, 21 | 9 | 3/2/0 | 1/4/0 | bulk 3, noncell 2 | 4/5 | 1/5 |

734-c342 vs 22-c296 side-by-side (both +2 extra-only):

| Shape | col | n/ov | rows | \|δ\| | gQ | gO | ostat | dec | pos |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 22 | 296 | 11/9 | 400, 401 | 8, 8 | 22, 24 | −1, −2 | noncell ×2 | 9, 9 | EB, EB |
| 734 | 342 | 7/5 | 26, 33 | 21, 11 | −50, −26 | −8, −13 | bulk ×2 | 9, 9 | ET, IB |

Row-tolerant standings (NOT adopted — the census rule stays
exact-match):

RT-PRES (present-tolerant iff miss ≤ 2 and extra ≤ 2): all 6
partial cells read present-tolerant; mover list over the M28
10 reads n=5 [711, 731, 732, 733, 734] (exact: n=10).

RT-DEST (missing row → nearest private-Y site, assigned iff
dmin ≤ 2): 0/4 assigned — s708 r28, s709 r33, s710 r31/r34
all read dmin=n/a (their shapes hold zero private-Y sites);
s9/s22/s734 are extra-only (no missing rows → unassignable).

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-PART-MISS (2 tail→bulk flips, c340 r24/25, +1 landing) | miss {24,25}, priv ∅, J 0.9804, n/ov 6/6, no-cand, ad_orig 17/38, synth bulk ad1, rest unchanged | exact | True |
| C-PART-EXTRA (2 bulk→tail flips, ±8 landing) | priv exact, miss ∅, J 0.9808, ad_new 8/8, s0 bulk ad 1/1, rest unchanged | exact | True |

(C-PART-EXTRA pool note, tabled per DESIGN fallback: c296 and
c343 hold 0 bulk gap≥17 Y sites, so the 2 injections landed in
non-named fallback columns c270 r25 (+8) and c334 r25 (−8);
per-column extra rows + miss==0 + extra-only standing verified
by direct row-list comparison; all 8 named columns present.
Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+22+708, fresh loads incl. carriers)
pass1 `f086446f…3cacb517` vs pass2 `f086446f…3cacb517`,
identical=True; 107/107 lines match=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_NEARMISS | pooled delta sites with other-frame bulk \|δ\|∈{6,7}, share ≥ 0.50 | 0/9 = 0.0000 — not met |
| H2_SETCHANGE | pooled delta sites non-cell on other frame, share ≥ 0.50 | 2/9 = 0.2222 — not met |
| H3_DEC9 | pooled delta sites in s0-P1 dec-9, share ≥ 0.50 | 8/9 = 0.8889 — met |
| H4_EDGE | pooled delta rows at EDGE span position, share ≥ 0.50 | 6/9 = 0.6667 — met |
| H5_EXTRAMISS | median \|δ\| extra ≠ median \|δ\| missing | 9 vs 18.0 — met (differs) |
| H6_TOLASSIGN | ≥1 missing delta row assigns under RT-DEST | 0/4 — not met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
span adjacency (4/4 missing rows in-span vs extras split 2
adjacent / 3 far-flung at +234/+366/+367 rows), by
other-frame status (7/9 far bulk with |δ| 1–5 vs 2/9 non-cell,
both s22 — the inverse of full swaps' 100% non-cell), by gap
(0/9 signed- or abs-equal), by band (missing 100% band-0 vs
extras 2/1/2 across bands), by decile (8/9 dec-9 with the lone
dec-8 on s710 r34), and by carrier (1 extra byte inside 693's
mask — s9's r266 — vs 0/40 full-swap priv/miss bytes in any
mask). Task 2 discriminates by value (extra medians 8–9 vs
missing 18.0 over non-overlapping ranges 8–21 / 13–44), by gap
sign (missing 4/4 +/+ both frames; extras mixed with 734's
−/− pair), by span position (extras 4/5 EDGE 1/5 TOP vs
missings 2/4 EDGE), and by tolerance response negatively
(RT-PRES un-moves all 6 cells while RT-DEST assigns 0/4 for
lack of any private-Y site).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; attribution tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence delta-row map
(`m29-deltamap.png`, 88510 B of 5242880 budget) colors pooled
delta-row sites on s0 geometry (yellow = 5 extra, magenta = 4
missing); DESIGN.md admits an evidence copy iff H3 meets AND
≥6 pooled sites share dec-9 — H3 meets (0.8889) with 8/9
sites in dec-9.

Recorded without verdict: 6/6 partial cells match M28's
n/ov/standing exactly with no 7th partial anywhere in the 764
shapes; the 9 delta-row sites split 7 far-bulk / 2 non-cell /
0 near with 0/9 gap equality; missing rows read in-span with
|δ| 13–44 (all g +/+) while extra rows split span-adjacent
(734, |δ| 11/21, g −/−) vs far-flung (9 r266, 22 r400/401,
|δ| 8–9); 8/9 sites read dec-9 across all three bands; RT-PRES
un-moves all 6 cells while RT-DEST assigns nothing; 0 B
explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| attribution suite + falsification bars, recorded before running | recorded | `DESIGN.md`: delta-row lists, M27-verbatim per-site rows + s0-anchored joins, extra/missing pools, RT-PRES/RT-DEST (not adopted), mid-level partial controls, bars H1–H6/N |
| delta-row + extra/missing + RT tables + wall/exit/shas/determinism | measured | §Step 2: 9 per-site rows + joins + pools + 22/734 side-by-side + RT tables; 24.7 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a delta-row map discriminates (or absence reasoned) | measured | present by rule: H3 meets + 8/9 sites in dec-9; 88510 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m29"
cp local/research/M29/m29.py local/research/M29/control.py local/research/M29/DESIGN.md "/Volumes/Extreme SSD/m29/"
python3 m29.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28" "/Volumes/Extreme SSD/m29" /Users/bradrichardson/dev/ssx3/local/research/M29 > m29.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m29/m29-deltamap.png" local/research/M29/m29-deltamap.png
```

## Paths

Evidence (committed): `local/research/M29/` — `DESIGN.md`
(suite + bars, recorded before running), `m29.py`
(delta-rows + joins + pools + RT rules + PNG writer),
`control.py` (known-partial mid-level controls),
`m29-deltamap.png` (delta-row map, 88510 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m29/` —
`m29.txt` (receipt: shas, baselines, M28 guard, Task-1/2
tables, joins, RT rows, re-run, PNG size), `control.txt`,
`m29.py`, `control.py`, `DESIGN.md` (working copies),
`m29-deltamap.png` (working copy, 88510 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`, or
other agents' dirs.

## Gap rows (exact next brief each needs)

1. Far-flung extras (new): 9 c321 r266 (+234 rows) + 22 c296
   r400/r401 (+366/+367 rows) read in-column but hundreds of
   rows from their streak spans — the census column
   definition, not a ±1–2 move. Needs its own brief: exact
   next step is a span-windowed census rule proposal (rows
   within ±K of the s0 span count; far sites tabled
   separately) re-run over all 764, offline — no new harness
   code.
2. Shape-9 mid-frame cluster (new): 22 privates + 8 missings
   outside c321 (rows 226–305) unattributed at byte level;
   the c321 +1 extra is one site of that cluster. Needs its
   own brief: the same private/missing/displacement
   attribution for shape 9's full sets, offline — no new
   harness code.
3. Shape-709 c298 missings (new): 4 missing rows in UNNAMED
   column c298 (r28/29/34/35) — a second partial column on
   709 outside the census 8. Needs its own brief: unnamed-
   column partial scan (which shapes move unnamed columns by
   ≤2 rows), offline — no new harness code.
4. Shape-22 bottom cluster (new): 2 outside-col privates
   (393,307)/(402,295) + the 2 c296 far extras form a
   rows-393–402 group, all non-cell/bulk-unknown on s0 at
   byte level except the 2 delta rows. Needs its own brief
   only if bottom-frame privates matter: full-set
   attribution for shape 22, offline — no new harness code.
5. Still-below divergence (M28 gap 2, still open): 2/3/700
   read below 0.95 with all 8 named columns present. Needs
   its own brief: the same private/missing/displacement
   attribution for 2/3/700, offline — no new harness code.
6. Shape-711 pair wipe (M28 gap 3, still open, minor): c342
   + c343 fully missing with no assigned dest. Needs its own
   brief only if unassigned moves matter: singleton + far
   private-column listing per unassigned move, offline — no
   new harness code.
7. Shape-734 triple move (M28 gap 4, still open, minor):
   c340 + c343 full wipes with dest collision at c342. Needs
   its own brief only if collision moves matter: dest-row
   listing + value table for 734's full sets, offline — no
   new harness code.
8. Shape-732 c296→c298 move (M28 gap 5, still open, minor):
   the only full single-column wipe with a fresh dest
   (rshift −1.5). Needs its own brief only if single full
   moves matter: dest-row listing + value table for 732,
   offline — no new harness code.
9. Below-0.95 shape family (M28 gap 6, still open — M28 join
   half worked): 9/700/734/732/2/711/3 unattributed at byte
   level (this run tables 9's c321 delta row + 734's c342
   delta rows only). Needs its own brief: the same
   private/missing/displacement attribution for
   9/700/734/732/2/711/3, offline — no new harness code.
10. Static-on-other-frame privates (M28 gap 7, still open):
    15/19 733-privates + 13/18 731-privates read gap 0 on s0.
    Needs its own brief only if cross-shape membership
    matters, offline — no new harness code.
11. M26 gaps 1–10, 12–21 (still open, by reference): see M27
    REPORT gaps 4–23 for the exact brief each needs (TRI/POS/
    CONST collapse, peak agreement, index-top argmax, QUAD
    underfit, m15 c343 r289, SIGN near-hits, r-coherence,
    gap-bin 32–63, m15 privates, 700 map, m15 static maps, U/V
    co-residuals, δ-sign, m15 below-min tail, negatives,
    Odin readiness, top-HUD glyphs, carrier weight centers).

(M28 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No per-site values outside delta rows: outside-column
   priv/miss sites are tabled as counts + (row,col) lists
   only (brief pins values for delta rows).
2. No byte-level attribution beyond the 9 delta sites: s9's
   cluster, s709's c298, s22's bottom group are located, not
   attributed (gaps 2–4 table the follow-ups).
3. No adopted tolerance: RT-PRES/RT-DEST are tabled WITHOUT
   adopting (exact-match census stands by brief).
4. c341 outside the census: guard-only (0 s0 sites) per
   brief's 8-column scope.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M29/`: `DESIGN.md`, `m29.py`,
`control.py`, `m29-deltamap.png` (88510 B), `REPORT.md` (this
file).
