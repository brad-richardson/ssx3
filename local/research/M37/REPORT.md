# M37 — c54 carrier coincidence: 701-mask geometry + row-list comparison: REPORT

M36 gap 1 worked at table level: 700-c54's 10 extras recompute
to the M36-pinned rows with per-site values exact (24/24 pins
match — stop rule not triggered), and the 701 removed-Y mask
reads 133 of its 649 px in Y-column 54 (12 touched columns,
54–65 contiguous; named-8 0, other unnamed-32 0) with c54's
10/10 rows inside, the other 14 extras 14/14 outside, and
c54's rows inside 0 of the other 9 carrier masks (H1 met, H2
not, H3 not, H6 met). c54's row numbers recur twice among the
other extras' rows (258, 259 — H4 met); the value contrast
reproduces M36 side-by-side (c54 10/10 |δ| 8 bulk −− vs others
5/14 |δ| 8, 4/14 bulk, 4 ++ / 10 −−). The 701 tail census reads
s0 0/102 + M19's cell row exact, with 2/764 shapes holding tail
in the mask (s700 10, s761 4 — all 14 in column 54; H5 met).
Fully offline — no lease of any kind, no boots, no harness
code, no `adb`. No device work. Runbook
`local/muse/prompts/M37.md`. Tables, no verdicts.

Headers read first: `local/research/M36/REPORT.md` (all of it:
gap 1 = this brief — 700-c54's 10 extras
[245, 246, 247, 252, 253, 258, 259, 278, 279, 283], all
|δ_700| = 8, all bulk on s0 (|δ_s0| 6:2 7:8), all gaps −−, all
inside the rank-3 701 removed-Y mask; the other 23 still-below
extras read 0 in every carrier mask — but see the brief-count
note below: M36's exact universe is 24 pooled extra sites =
c54's 10 + 14 others) plus the M19 carrier table (the 701 mask
definition + rank context: rank 3 / shape 701, removed 649 Y
px, bands [186, 463, 0], 367/649 = 56.6% interior-Y; mask =
res0 & ~ress on Y) and M22's 701 split (s0 tail inside 0, bulk
inside 367).

Brief-count note (recorded in DESIGN.md before running; tabled
here): the brief says "the other 23 extras" / "other-23 row
lists", but M36's exact universe is 24 pooled extra sites (s2
5 + s3 4 + s700 15) = c54's 10 + 14 others (12 unique (r,c)
across shapes — (259,311) and (296,332) recur on s2+s700).
"23" matches no M36 extras count (plausibly a slip from M36's
"23/24 band-1" pooled-extras line, or 33−10 from the unnamed
column count). The brief's own stop rule names M36 as the match
target, so all guards pin M36's exact 24-site universe; the
brief proceeds on it with the discrepancy tabled, not stopped
on.

Time box 4 hours (start 2026-09-20 04:40 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`–`m36/` — all outputs went to the new
`/Volumes/Extreme SSD/m37/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), the top-10
carrier triplets, `m34-census.tsv` (universe + TSV guard), and
`m36.txt` (24-site match target). Work dir
`/Volumes/Extreme SSD/m37/`; evidence `local/research/M37/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M36):

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

(Full hexes in `m37.txt` §inputs, plus all 30 top-10-carrier
triplet bins. `m34-census.tsv` 163262 B; `m36.txt` 102945 B.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M36 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34/M35/M36
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s2/s3/s700 cell reads 2469/2484/2605 (M36's
measured values — equal, not just tabled); FULL unnamed TSV
match (all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv`; 2/3/700 rows match the pinned k 6/7/8 +
n/ov + standings + deltas exactly; pooled counts read 5+4 /
4+3 / 15+3 exactly; all 24 pooled extras Y-plane; all 24
per-site pins (offset + adQ + ostat + adO + gQ + gO) match
M36 exactly (§Task 1). Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m37.py` invocation (the receipt, 6.8 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m37.py receipt | 6.8 s | exit 0; all guards pass; canon `0bc18bec…f692c9f` |
| control.py C-MASK | <1 s | green; sets + membership + values exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 4.7 s |
| Task 1 (701 column profile + overlaps + coverage) | 3 | <1 s |
| Task 2 (rowlists + recurrence + contrast + census) | 764 | 1.7 s |
| Determinism re-run (Task 1 on s0+700, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m37.py` wall | — | 6.8 s |

## Step 2 — estimates

### Task 1 — mask geometry (does 701 cover c54?)

c54's 10 rows + the other-14 row lists recomputed from the
dumps (FULL TSV guard passed first — all 764 rows byte-identical;
24/24 per-site pins match M36 exactly — offsets, |δ|, bulk
status, gaps all exact):

701-mask column profile (per-Y-column mask-row counts; 12
touched columns, all in 54–65 contiguous; full row lists in
`m37.txt`):

| col | n | row span |
| ---: | ---: | --- |
| 54 | 133 | 113–296 |
| 55 | 42 | 113–296 |
| 56 | 133 | 114–297 |
| 57 | 3 | 259–272 |
| 58 | 2 | 191–218 |
| 59 | 13 | 158–188 |
| 60 | 4 | 220–261 |
| 61 | 6 | 190–261 |
| 62 | 77 | 114–270 |
| 63 | 30 | 116–296 |
| 64 | 67 | 117–296 |
| 65 | 139 | 113–297 |

(Group sums: named-8 0 px in 0 columns; unnamed-33 133 px in 1
column (c54 — the only unnamed column the mask touches);
rest 516 px in 11 columns. 628/640 Y columns hold 0 mask rows.
Column counts sum to 649 = the M19 removed count.)

Overlap table — c54's 10 rows × 701 mask (all inside per M36 —
reproduced):

| row | in 701 |
| ---: | --- |
| 245 | 1 |
| 246 | 1 |
| 247 | 1 |
| 252 | 1 |
| 253 | 1 |
| 258 | 1 |
| 259 | 1 |
| 278 | 1 |
| 279 | 1 |
| 283 | 1 |

(10/10 in.)

Overlap table — the other 14 extras × 701 mask (all outside
per M36 — reproduced):

| site | in 701 |
| --- | --- |
| s2 (259,311) | 0 |
| s2 (293,313) | 0 |
| s2 (296,332) | 0 |
| s2 (297,332) | 0 |
| s2 (240,339) | 0 |
| s3 (258,311) | 0 |
| s3 (265,316) | 0 |
| s3 (238,336) | 0 |
| s3 (238,339) | 0 |
| s700 (25,299) | 0 |
| s700 (259,311) | 0 |
| s700 (291,313) | 0 |
| s700 (296,332) | 0 |
| s700 (170,620) | 0 |

(14/14 out.)

Overlap table — c54's 10 rows × the other 9 carrier masks
(inside anywhere else?):

| mask (rank/shape) | c54 rows in |
| --- | --- |
| 1/694 | 0/10 |
| 2/693 | 0/10 |
| 4/368 | 0/10 |
| 5/369 | 0/10 |
| 6/366 | 0/10 |
| 7/370 | 0/10 |
| 8/376 | 0/10 |
| 9/748 | 0/10 |
| 10/750 | 0/10 |

(0/90 site-mask hits outside 701.)

Coverage answer as a TABLE (mask rows per column: c54's column
vs the other-extras' columns):

| column | 701-mask rows |
| ---: | --- |
| 54 (c54) | 133 |
| 299 | 0 |
| 311 | 0 |
| 313 | 0 |
| 316 | 0 |
| 332 | 0 |
| 336 | 0 |
| 339 | 0 |
| 620 | 0 |

(Column 54 holds 133 mask rows — 29.7% of its 448 rows;
the 8 other-extra columns hold 0 each.)

### Task 2 — row-list comparison (c54 vs the other 14)

Row lists per extra-bearing cell (all 14 cells, M36-headliner
style):

| cell | s0 rows | Q rows | extra rows |
| --- | --- | --- | --- |
| s2 c311 | [296,297,298,299] | [259,296,297,298,299] | [259] |
| s2 c313 | [274,275,276,292] | [274,275,292,293] | [293] |
| s2 c332 | [295,304] | [296,297,304] | [296,297] |
| s2 c339 | [] | [240] | [240] |
| s3 c311 | [296,297,298,299] | [258,296,297,298,299] | [258] |
| s3 c316 | [264] | [264,265] | [265] |
| s3 c336 | [] | [238] | [238] |
| s3 c339 | [] | [238] | [238] |
| s700 c54 | [] | [245,246,247,252,253,258,259,278,279,283] | all 10 |
| s700 c299 | [] | [25] | [25] |
| s700 c311 | [296,297,298,299] | [259,296,297,298,299] | [259] |
| s700 c313 | [274,275,276,292] | [274,275,276,291,292] | [291] |
| s700 c332 | [295,304] | [296,304] | [296] |
| s700 c620 | [] | [170] | [170] |

Row-number recurrence (same rows recurring across shapes? c54
rows unique?):

| set | rows |
| --- | --- |
| c54's 10 | [245,246,247,252,253,258,259,278,279,283] |
| pooled other-extra rows (11 unique) | [25,170,238,240,258,259,265,291,293,296,297] |
| overlap | [258,259] (2/10) |

(Per-shape other rows: s2 [240,259,293,296,297]; s3
[238,258,265]; s700 [25,170,259,291,296]. Row 259 recurs as an
extra row on s2c311 + s700c311 + c54; row 258 recurs on s3c311
+ c54; row 238 recurs on s3c336 + s3c339; row 296 recurs on
s2c332 + s700c332.)

Value contrast (c54's uniform |δ| 8 bulk −− vs the other 14 —
M36 numbers reproduced + side-by-side; per-cell per-site rows
in `m37.txt`):

| group | n | \|δ_Q\| list | bulk/noncell | gaps |
| --- | ---: | --- | --- | --- |
| c54 | 10 | [8×10] (med 8.0, mean 8.0000) | 10/0 | 0 ++ / 10 −− |
| others | 14 | [8,8,8,8,8,9,9,11,17,17,20,20,34,34] (med 8.5, mean 15.0714) | 4/10 | 4 ++ / 10 −− |

(The others' 5 |δ| 8 sites: s2c313's + s3c316/c336/c339's +
s700c313's; the 4 bulk sites are s2c313's + s3c316/c336's +
s700c313's (|δ_s0| 7:4); the 4 ++ sites are s2c339's +
s3c316/c336/c339's.)

701-mask tail census (is the mask tail-dense generally?):

| cut | n |
| --- | ---: |
| s0 tail bytes in 701 | 0/102 (M22 reproduced) |
| s0 bulk bytes in 701 | 367 (M22 reproduced) |
| s0 cells in 701 (c0–c7) | [233,20,22,1,2,2,2,367] (M19 row reproduced) |
| shapes (of 764) with ≥1 tail byte in 701 | 2: s700 (10/114), s761 (4/106) |
| s2 / s3 tail in 701 | 0/103, 0/103 |
| all-764 in-mask counts | min 0, med 0.0, max 10 |

(s761: tail 106, J 0.9623 vs s0; its 4 in-mask tail bytes sit
at (259,54), (261,54), (263,54), (274,54) — all in column 54,
via a read-only supplementary probe reusing the receipt
`m37.py` core, disclosed here. All 14 in-mask tail bytes
across the 764 shapes sit in column 54.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-MASK (known 6-in + 4-out) | priv 10 exact, miss 0, membership 6/6-in + 4/4-out, \|δ\| 8, cell fixed, orig kept | exact | True |

(In-mask pool: 367 bulk-Y; out-of-mask pool: 1952 bulk-Y.
In-sites (115,56)/(116,56)/(116,63)/(117,56)/(118,56)/(119,56);
out-sites (25,334)/(26–28,305). J(T_B,T_A) = 0.9107. Full rows
in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+700: 701 column profile + c54 overlap
tables + coverage table, fresh loads incl. carriers) pass1
`0bc18bec…f692c9f` vs pass2 `0bc18bec…f692c9f`,
identical=True; 44/44 lines match=True; c54 rows identical
([245, 246, 247, 252, 253, 258, 259, 278, 279, 283]).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_GEOM_COVER | col-54 701-mask rows > max over the 8 other-extra columns | 133 vs 0 — met |
| H2_MASK_SPAN | 701 mask touches ≥5 of the 8 other-extra columns | 0/8 — not met |
| H3_C54_OTHER_CARRIER | ≥1 of c54's 10 sites inside another top-10 carrier mask | 0 rows — not met |
| H4_ROW_RECURRENCE | ≥1 of c54's 10 row numbers recurs among other-extra rows | [258,259], 2 — met |
| H5_TAILWIDE | ≥2 of 764 shapes hold ≥1 tail byte in the 701 mask | 2 (700, 761) — met |
| H6_OTHERS_BARE | ≥5 of the 8 other-extra columns hold 0 mask rows | 8/8 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (24/24 per-site pins exact — offsets, |δ|, bulk
status, gaps), by mask placement (649 px in 12 contiguous
columns 54–65; column 54 alone holds 133 while the named-8
hold 0 and the other unnamed-32 hold 0), by overlap (c54
10/10 in, others 14/14 out, c54 0/90 in the other 9 masks),
and by coverage (133 vs 0 × 8). Task 2 discriminates by row
recurrence (2 of c54's 10 row numbers recur elsewhere — 258
on s3c311, 259 on s2/s700c311), by value split (c54 uniform
8/bulk/−− vs others med 8.5, 4/14 bulk, 4/14 ++), and by
census (s0 0 tail in-mask vs s700 10 + s761 4, all column 54).

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

Screenshot: present by rule. The evidence overlap map
(`m37-overlap-701.png`, 89403 B of 5242880 budget) colors the
701 mask slate with s700's shared tail green, c54's 10 extras
yellow, and the other 14 extras red; DESIGN.md admits an
evidence copy iff H1 meets AND ≥12/14 other-extra sites read
outside the 701 mask — H1 meets (133 > 0) with 14/14 outside.

Recorded without verdict: c54's 10 extras recompute to M36's
rows + values exactly with 10/10 inside the 701 mask while the
other 14 extras read 14/14 outside and 0/90 in the other 9
carrier masks; the mask sits in 12 contiguous columns 54–65
with column 54 holding 133 px and the 8 other-extra columns
holding 0; 2 of c54's 10 row numbers recur among other-extra
rows; c54 reads uniform |δ| 8 bulk −− against others at med
8.5 with 4/14 bulk; 2/764 shapes hold tail in the mask (s700
10, s761 4, all column 54); 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| mask-geometry suite + falsification bars, recorded before running | recorded | `DESIGN.md`: 701 column profile, overlap tables (c54×701, others×701, c54×other-9), coverage table, rowlists + recurrence + value contrast, 701 tail census, C-MASK control, bars H1–H6/N |
| c54 rows + other-extras rows + geometry + comparison + wall/exit/shas/determinism | measured | §Step 2: 24/24 pins exact + 12-column profile + overlaps + coverage + rowlists + contrast + census; 6.8 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a mask-overlap map discriminates (or absence reasoned) | measured | present by rule: H1 + 14/14 outside; 89403 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m37"
cp local/research/M37/m37.py local/research/M37/control.py local/research/M37/DESIGN.md "/Volumes/Extreme SSD/m37/"
python3 m37.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m36/m36.txt" "/Volumes/Extreme SSD/m37" /Users/bradrichardson/dev/ssx3/local/research/M37 > m37.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m37/m37-overlap-701.png" local/research/M37/m37-overlap-701.png
```

(Supplementary: `/tmp/m37_probe761.py` — read-only s761
tail-in-mask rows via the receipt `m37.py` core; disclosed in
§Task 2.3.)

## Paths

Evidence (committed): `local/research/M37/` — `DESIGN.md`
(suite + bars, recorded before running), `m37.py`
(701-mask geometry + rowlists + contrast + census + PNG
writer), `control.py` (known-membership control),
`m37-overlap-701.png` (overlap map, 89403 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m37/` —
`m37.txt` (receipt: shas, baselines, guards, 24-site pins,
Task-1 geometry, rowlists, contrast, census, re-run, PNG
size), `control.txt`, `m37.py`, `control.py`, `DESIGN.md`
(working copies), `m37-overlap-701.png` (working copy). No
writes into `m15/`, `m16/`, `m17/`–`m36/`, or other agents'
dirs.

## Gap rows (exact next brief each needs)

1. s761's column-54 tail quartet (new): shape 761 (tail 106, J
   0.9623) is the only shape besides 700 with tail inside the
   701 mask — 4 bytes at (259,54)/(261,54)/(263,54)/(274,54),
   all column 54, one row (259) shared with c54. Needs its
   own brief only if second-carrier-hit values matter:
   row-list + per-site value comparison of 761's 4 vs c54's
   10, offline — no new harness code.
2. 701 mask column block 54–65 (new): the mask spans 12
   contiguous columns with a 133/133/139-px triple at 54/56/65
   and near-empty singles at 57/58/60/61 — substructure
   untabled. Needs its own brief only if mask shape matters:
   per-column row-pattern + band/bulk split within the mask,
   offline — no new harness code.
3. M36 gaps 2–6 (still open, by reference): see M36 REPORT
   gaps 2–6 for the exact brief each needs (shared-site
   triple; s3 all-delta-1 row; M35 gaps 1–3; M34 gaps 3–4;
   M33 gaps 1, 4–5).
4. M35 gaps 1–3 (still open, by reference): see M35 REPORT
   gaps 1–3 for the exact brief each needs (per-cell
   standing asymmetry; near-miss triple; big-|δ| unnamed
   sites).
5. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns; same-column opposite standings).

(M36 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No per-site values beyond the 24 pooled extra sites: δ
   values, gaps, and bulk status at other unnamed moved
   cells are unattributed (brief pins c54 + the other extras
   only).
2. No destination assignment for unnamed moves: row-deltas
   are tabled without the M28-style displacement step (brief
   pins geometry + rowlists + values only).
3. No s761 cell-7 count pin: s761's tail (106) and J (0.9623)
   read as measured via the supplementary probe (brief pins
   s0/2/3/700 counts only).
4. No explanation: membership is attributed geometrically per
   column per row, no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M37/`: `DESIGN.md`, `m37.py`,
`control.py`, `m37-overlap-701.png` (89403 B, rule-met),
`REPORT.md` (this file).
