# M45 — Shape-22 bottom cluster: full-set attribution: REPORT

M34 gap 5 (= M33 gap 3 = M29 gap 4) worked at table level: s22's
row recomputes to tail 106 at Jaccard 0.9623 vs s0 (s22 TSV row
+ k=2 + n/ov match M34 exactly, c296's [400,401] + pair values
match M29 exactly — stop rule not triggered), splitting into 3
moved cells (named c296 11/9 + unnamed c295 1/0 + unnamed c307
2/1, all extra-only, deltas 2/1/1) holding 4 privates + 0
missings, all Y, all inside rows 393–402 (H4 whole-set met —
the bottom group IS the full moved set). The 2 NEW outside-col
privates read (393,307): |δ_22| 9, s0 far-bulk |δ| 1, gaps
26/−6, dec 9; (402,295): |δ_22| 8, s0 far-bulk |δ| 1, gaps
19/−4, dec 8 — against the pair's 8,8/noncell. Pooled 4 read
0 near / 2 far / 2 noncell (H1 0.0000, H2 0.5000); gaps read
4/4 +/− (H5 1.0000); dec-9 reads 3/4 (H3 0.7500); the new
magnitudes read 9,8 (H6 not met). Pairwise row distances over
the 4 run 1–9 (span 9); the c296 pair {400,401} shares no row
or column with the outside pair; col seats read c295 −1 /
c307 +11 vs c296. Fully offline — no lease of any kind, no
boots, no harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M45.md`. Tables, no verdicts.

Headers read first: `local/research/M33/REPORT.md` (all of it:
gap 3 = this brief via M34 gap 5; s9 cluster method +
Jaccard/set machinery) plus `local/research/M29/REPORT.md`
(all of it: s22 c296 n/ov 11/9 extras [400,401], |δ| 8,8,
gaps gQ 22,24 / gO −1,−2, noncell ×2, dec 9,9; s22 full sets
priv 4 / miss 0 / shared 102, tail 106, J 0.9623; outside-col
privates (393,307)/(402,295); pooled extra[all] n=5 bulk 3 /
noncell 2, near 0) plus `local/research/M34/REPORT.md` (all of
it: s22's census row — k=2 moved [295,307], tail 106, J
0.9623; s0 c307 rows [404] n0=1; c295 pure-private n0=0;
UNNAMED 33 = 13 s0-bearing + 20 pure-private) plus
`local/research/M36/REPORT.md` (§Task 1: M36-style per-site
rows + grand pooled extras n=24 near/far/non 14/0/10 — pinned
side-by-side reference).

Time box 4 hours (start 2026-09-20 06:15 EDT); used about 0.5.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m44/` — all outputs went to the new
`/Volumes/Extreme SSD/m45/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m34-census.tsv` (s22-row match target). Work dir `/Volumes/
Extreme SSD/m45/`; evidence `local/research/M45/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M44; s22 prefixes match M29):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0022 | `09dd96f3…bd274439` |
| m16-mid-s0022 | `5e05bc20…58758688` |
| m16-full-s0022 | `ed846091…000d8bf3` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m45.txt` §inputs. `m34-census.tsv` 163262 B —
matches M34's committed size and M36's sha.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M44 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
+ all 8 s0 named reference row lists match exactly. UNNAMED
domain recomputes to 41 union tail-Y cols → 33 unnamed (13
s0-bearing + 20 pure-private) with the universe matching the
TSV header. s22 TSV row (tail + J4 + all-33-column n/ov/pres)
matches `m34-census.tsv` exactly. s22 spot guards (unnamed k=2
[295,307], c295 1/0, c307 2/1, named [296] only, c296 11/9,
tail/J 106/0.9623, s0 c295 [] + c307 [404]) all match.
Tier-2 row-list/set guards (c296 ex [400,401]; c295 ex [402];
c307 ex [393] kept [404]; priv set == BOT; miss empty; shared
102) all match. c296-pair value cross-check vs M29 (8,8 /
noncell ×2 / 22,24/−1,−2 / dec 9,9) matches exactly. Mismatch
rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m45.py` receipt invocation (5.4 s, exit 0); two
`control.py` invocations (v1 infeasible-as-pinned, tabled; v2
re-scoped, green). Two pre-receipt estimator fixes (bars-section
`mask0` name crash — first attempt died after Task 2, before any
H-bar measurement; `geo_lines` shared-function refactor + control
re-scope per the DESIGN.md timed amendment) — the receipt run
below is the single recorded invocation, and the estimator was
never changed after it started (Task-1 canon sha identical
across the refactor).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m45.py receipt | 5.4 s | exit 0; all guards pass; canon `1a3d2534…e5656661` |
| control.py v1 (C-BOT as pinned) | <1 s | infeasible, tabled; in-band candidates n=0 |
| control.py v2 (C-BOTM + C-BOTV) | <1 s | green; census + values + geometry exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 5.2 s |
| Task 1 (moved cells + privates + completeness) | 2 | 0.0 s |
| Task 2 (values + geometry + side-by-side) | 2 | 0.0 s |
| Determinism re-run (Task 1 on s0+22, fresh loads) | — | in-pass |
| Positive controls (`control.py` v2) | — | <1 s |
| Total `m45.py` wall | — | 5.4 s |

## Step 2 — estimates

### Task 1 — s22 moved-set census (is the bottom group the whole set?)

s22's row recomputed from the dumps (TSV row + k + cells +
n/ov + standings + deltas + J all match M34/M29 exactly —
stop rule not triggered). Full sets: tail 106, J 0.9623, priv
4, miss 0, shared 102 (4+102=106 ✓, 0+102=102 ✓,
102/106=0.9623 ✓). Planes: priv 4/0/0, miss 0/0/0, shared
102/0/0 (Y/U/V) — all luma.

Moved-cell table (all s22 cells over named-8 + unnamed-33
checked; 3 moved, 7 named still + 31 unnamed still):

| cell | n/ov | n0 | miss/extra | delta | standing |
| ---: | --- | ---: | --- | ---: | --- |
| named 296 | 11/9 | 9 | 0/2 | 2 | extra-only |
| unnam 295 | 1/0 | 0 | 0/1 | 1 | extra-only |
| unnam 307 | 2/1 | 1 | 0/1 | 1 | extra-only |

Row lists: c296 s0 [24,25,26,27,28,31,32,33,34], s22 +[400,401]
(ex [400,401], mi []); c295 s0 [], s22 [402] (ex [402]); c307
s0 [404], s22 [393,404] (ex [393], kept [404]). Named still:
[257,277,301,321,340,342,343].

Private table (outside-col sites + their columns' s0 rows):

| site | s0 rows of col | seat | s22 rows of col |
| --- | --- | --- | --- |
| (393,307) | [404] | s0-bearing | [393, 404] |
| (402,295) | [] | s0-empty | [402] |

Completeness table (bottom group vs full moved set; INBAND =
rows 393–402):

| set | in-band | out-of-band |
| --- | --- | --- |
| priv (4) | 4: (393,307), (400,296), (401,296), (402,295) | 0: [] |
| miss (0) | 0: [] | 0: [] |
| c296 ex | [400, 401] | [] |
| c295 ex | [402] | [] |
| c307 ex | [393] | [] |

wholeset=True (priv == BOT[4] and miss empty) — nothing
outside rows 393–402 at either the site or the cell level.

### Task 2 — full-set attribution + cluster geometry

Per-site value table (ALL s22 moved sites: 4 priv + 0 miss;
M36-style rows + s0-P1 decile; offset-ordered):

| cell | offset | plane | (r,c) | \|δ_22\| | s0 status | \|δ_s0\| | g_22 | g_s0 | signs | dec |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- | ---: |
| 307 | 503654 | Y | (393,307) | 9 | bulk | 1 | 26 | −6 | +− | 9 |
| 296 | 512592 | Y | (400,296) | 8 | noncell | n/a | 22 | −1 | +− | 9 |
| 296 | 513872 | Y | (401,296) | 8 | noncell | n/a | 24 | −2 | +− | 9 |
| 295 | 515150 | Y | (402,295) | 8 | bulk | 1 | 19 | −4 | +− | 8 |

Summary: near 0 (0.0000), far 2 (0.5000), noncell 2 (0.5000).
Bulk |δ_s0| values: 1:2. Signed-gap equality 0/4, abs-gap
equality 0/4. |δ_22|: min 8, median 8.0, mean 8.2500, max 9.
Gap signs all +− (4/4 ++=0). The c296 pair rows reproduce
M29's pinned values exactly (guarded); the (393,307)/(402,295)
rows are NEW DATA (this run).

Cluster geometry (pairwise distances over the 4 bottom sites;
span 9, rows 393–402):

| pair | drow | dcol |
| --- | ---: | ---: |
| (400,296)-(401,296) | 1 | 0 |
| (400,296)-(393,307) | 7 | 11 |
| (400,296)-(402,295) | 2 | 1 |
| (401,296)-(393,307) | 8 | 11 |
| (401,296)-(402,295) | 1 | 1 |
| (393,307)-(402,295) | 9 | 12 |

Shared rows c296-pair {400,401} vs outside-pair {393,402}:
none. Shared cols {296} vs {307,295}: none. Column seats vs
c296: c295 Δ=−1 (abs 1); c307 Δ=+11 (abs 11). Rowspan:
min 393, max 402, span 9.

c296 side-by-side (measured pair + pooled splits vs pinned
pooled-extra references):

| pool | n | near | far | noncell |
| --- | ---: | --- | --- | --- |
| s22 c296 pair (measured) | 2 | 0 | 0 | 2 |
| s22 pooled 4 (measured) | 4 | 0 | 2 | 2 |
| M29 extra[all] (pinned) | 5 | 0 | 3 | 2 |
| M29 extra[22,9] (pinned) | 3 | 0 | 1 | 2 |
| M36 grand extras (pinned) | 24 | 14 | 0 | 10 |

(The pair's 0/0/2 sits on the noncell side of every pooled
reference; the 4-site 0/2/2 matches M29 extra[all]'s 0/3/2
shape at n=4 vs n=5 with zero nears on both — tabled, no
verdict. Pinned refs from committed REPORTs, cited in
DESIGN.md, not recomputed.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-BOT/inband probe (as-pinned leg) | in-band bulk gap≥17 Y n=0 | ≥1 | infeasible, tabled |
| C-BOTM (mask-level 2+2) | moved {300,305}, n/ov 2/0 + 2/0 extra-only, P/M sets exact, J 102/106=0.9623, completeness 2/2, geo 8/8 lines | exact | True |
| C-BOTV (mid-level 4 out-of-band) | P 4 exact, M ∅, J 102/106=0.9623, \|δ\| 8×4, s0-bulk, gaps equal, dec 9×4, cols exact, mask fixed, rest unchanged | exact | True |

(C-BOTM coords: in (394,300)/(399,305), out (100,300)/(200,305)
— zero s0-tail clashes; per-column rows [100,394]/[200,399]
exact; geometry drow/dcol + span 299 match independently
computed expectations 8/8. C-BOTV picks: (25,270)/(25,334)/
(26,305)/(27,298) with signs +8/−8/−8/+8, 2 sign-fallbacks,
orig |δ| 1/1/1/6; affected columns c270/c298/c305/c334 rows
exact incl. c298 5/4 growth over s0's 4 rows. Full rows in
`control.txt`. C-BOTV's J 102/106=0.9623 equals s22's by
arithmetic (102/(102+4)), tabled as such.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+22: moved-cell + private + completeness
+ set-list rows, fresh loads, guarded universe) pass1
`1a3d2534…e5656661` vs pass2 `1a3d2534…e5656661`,
identical=True; 19/19 lines match=True; sets identical=True
(priv 4, miss 0, shared 102). (Canon sha identical across the
pre-receipt `geo_lines` refactor — Task 1 untouched.)

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_BOTNEAR | bottom sites s0-bulk \|δ\|∈{6,7}, share ≥ 0.50 | 0/4 = 0.0000 — not met |
| H2_BOTSET | bottom sites non-cell on s0, share ≥ 0.50 | 2/4 = 0.5000 — met |
| H3_BOTDEC9 | bottom sites in s0-P1 dec-9, share ≥ 0.50 | 3/4 = 0.7500 — met |
| H4_WHOLESET | full priv set == BOT and miss empty | True — met (tier-2 pass) |
| H5_GAPOPP | bottom sites with g_22·g_s0<0, share ≥ 0.50 | 4/4 = 1.0000 — met |
| H6_NEWMAG | both new privates \|δ_22\|==8 | 9,8 — not met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
cell count (3 moved of 41 checked — 1 named + 2 unnamed, all
extra-only, deltas 2/1/1), by column seat (c307 s0-bearing
with kept row 404 vs c295 s0-empty fresh growth), and by
completeness (4/4 privates + all 4 delta rows in-band, 0
outside at every level — the bottom group is the whole set).
Task 2 discriminates by status split (pair 2/2 noncell vs new
sites 2/2 far-bulk with |δ_s0| 1,1 — the inverse pairing
inside one cluster), by value (new magnitudes 9,8 vs pair
8,8; pooled med 8.0), by gap (0/4 signed- or abs-equal; all 4
read +/− with g_22 19–26 vs g_s0 −1…−6), by decile (3/4 dec-9
with the lone dec-8 on (402,295)), by geometry (row distances
1–9 over span 9 with no shared row/col between the pairs;
col seats −1/+11), and by pooled contrast (pair 0/0/2 vs
4-site 0/2/2 vs M29 0/3/2 / M36 14/0/10 — zero nears on the
s22 side throughout).

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

Screenshot: present by rule. The evidence cluster map
(`m45-clusmap.png`, 88665 B of 5242880 budget) colors s22 tail-Y
by shared (green 102) / c296 extras (yellow 2) / outside-col
privates (red 2); DESIGN.md admits an evidence copy iff H3 meets
AND ≥3 bottom sites share dec-9 — H3 meets (0.7500) with 3/4
sites in dec-9.

Recorded without verdict: s22's divergence reads 3 extra-only
cells holding 4 + 0 sites at 100% luma, all inside rows
393–402 with nothing outside; the c296 pair reads 8,8/noncell
while the new privates read 9,8/far-bulk (|δ_s0| 1,1); all 4
read +/− gaps and 3/4 read dec-9; the pairs share no row or
column across a row-span of 9 with col seats −1/+11; the pair
sits 0/0/2 against pooled references while the 4-site pool
reads 0/2/2; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| attribution suite + falsification bars, recorded before running | recorded | `DESIGN.md`: moved-cell census (named+unnamed), private table, completeness, M36-style+dec value rows, pairwise geometry, c296 side-by-side, C-BOT control (amended to C-BOTM+C-BOTV, timed), bars H1–H6/N |
| moved-set census + attribution + geometry + wall/exit/shas/determinism | measured | §Step 2: 3 cells + 2 privates + completeness + 4 value rows + 6 pairs + side-by-side; 5.4 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a cluster map discriminates (or absence reasoned) | measured | present by rule: H3 meets + 3/4 sites in dec-9; 88665 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single recorded invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m45"
cp local/research/M45/m45.py local/research/M45/control.py local/research/M45/DESIGN.md "/Volumes/Extreme SSD/m45/"
python3 m45.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m45" /Users/bradrichardson/dev/ssx3/local/research/M45 > m45.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m45/m45-clusmap.png" local/research/M45/m45-clusmap.png
```

## Paths

Evidence (committed): `local/research/M45/` — `DESIGN.md`
(suite + bars, recorded before running; timed control
amendment), `m45.py` (census + attribution + geometry + PNG
writer), `control.py` (C-BOT probe + C-BOTM + C-BOTV),
`m45-clusmap.png` (cluster map, 88665 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m45/` —
`m45.txt` (receipt: shas, baselines, guards, Task-1/2 tables,
re-run, PNG size), `control.txt`, `m45.py`, `control.py`,
`DESIGN.md` (working copies), `m45-clusmap.png` (working copy,
88665 B). No writes into `m15/`, `m16/`, `m17/`, `m18/`,
`m19/`, `m20/`, `m21/`, `m22/`, `m23/`, `m24/`, `m25/`,
`m26/`, `m27/`, `m28/`, `m29/`, `m30/`, `m31/`, `m32/`,
`m33/`, `m34/`, `m35/`, `m36/`, `m37/`, `m38/`, `m39/`,
`m40/`, `m41/`, `m42/`, `m43/`, `m44/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. In-cluster status split (new, minor): the c296 pair reads
   2/2 noncell on s0 while the 2 new privates read 2/2
   far-bulk (|δ_s0| 1,1) — same +/− gap signs, same band,
   magnitudes 8,8 vs 9,8. Needs its own brief only if
   within-cluster status splits matter: per-subset value/join
   split, offline — no new harness code.
2. Lone dec-8 (new, minor): (402,295) reads dec-8 while the
   other 3 bottom sites read dec-9. Needs its own brief only
   if single-decile deviations matter: decile-edge case table,
   offline — no new harness code.
3. Earlier gaps (still open, by reference): see the M34–M44
   REPORT gap rows for the exact brief each needs (M34 gap 5
   — this brief — worked at table level above).

(M29 gap 4 / M33 gap 3 — the s22 bottom cluster seed — is
attributed above.)

## What I could not do

1. No mid-level in-band control leg: rows 393–402 hold zero
   interior-bulk gap≥17 Y sites on s0, so no |δ|=8 injection
   is possible in-band — the pre-registered leg is tabled
   infeasible with its measured reason, and census/geometry
   coverage comes from mask-level C-BOTM (DESIGN.md timed
   amendment; any future bottom-band value control must be
   mask-level).
2. No band/streak/carrier joins: brief pins |δ| + statuses +
   gaps + signs + deciles + geometry only.
3. No destination/displacement analysis for the bottom sites
   (brief pins pairwise cluster geometry, not
   nearest-shared displacement).
4. No byte-level attribution beyond shape 22's own sets (brief
   scope is s22 full-set only).
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M45/`: `DESIGN.md`, `m45.py`,
`control.py`, `m45-clusmap.png` (88665 B), `REPORT.md` (this
file).
