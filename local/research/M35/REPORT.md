# M35 — Shape-9 unnamed cells: per-site value table: REPORT

M34 gap 1 worked at table level: shape 9's unnamed row
recomputes to the pinned 15 cells with standings + deltas
exact (FULL 764×33 TSV byte-identical to `m34-census.tsv` —
stop rule not triggered), splitting into 22 extras + 8
missings whose (row,col) sets equal M33's cluster sets
exactly. The 22 extras read 1 near / 14 far / 7 non-cell on
s0 (H1 0.0455, H2 0.3182); the 8 missings read 2 near / 2
far / 4 non-cell on shape 9 (H3 0.5000 — met); extras read
21/22 band-1 vs 19/94 shared (H4 met on the band leg,
0.7524); missings read 8/8 +/+ gaps (H5 1.0000 — met); the
9 c314+c315 headliner rows read 4/9 bulk (H6 0.4444).
Streak/carrier joins read N/A off the named set (all
other, 0 in any mask). Fully offline — no lease of any
kind, no boots, no harness code, no `adb`. No device work.
Runbook `local/muse/prompts/M35.md`. Tables, no verdicts.

Headers read first: `local/research/M34/REPORT.md` (all of it:
gap 1 = this brief — 9's 15 unnamed moved cells
(310–316, 318, 322, 327, 332, 336, 337, 339, 351) incl. the
only mixed delta-5 (c315) and a tied delta-4 (c314) —
located, not attributed at byte level; the census method)
plus `local/research/M27/REPORT.md` (all of it: Task-1
per-site table + joins method reused verbatim, s0-anchored)
plus `local/research/M33/REPORT.md` (§Task 1: s9 cluster
22 priv + 8 miss per-site values; 21/22 band-1; +/+
missings; extras median 13.0 vs missings 10.0 — the pooled
values this brief splits per cell).

Time box 4 hours (start 2026-09-20 04:20 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m34/` — all outputs went to the new
`/Volumes/Extreme SSD/m35/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), the top-10
carrier triplets, and `m34.txt` + `m34-census.tsv` (match
targets). Work dir `/Volumes/Extreme SSD/m35/`; evidence
`local/research/M35/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M34; s9 prefixes match M33):

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
| m34.txt | `21241ba5…babbf7f44` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m35.txt` §inputs, plus all 30 top-10-carrier
triplet bins. `m34.txt` 10762 B; `m34-census.tsv` 163262 B —
matches M34's committed size.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M34 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s9 cell reads 2670. FULL unnamed TSV match
(all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv`; shape-9 row matches the pinned 15 cells +
standings + deltas exactly (§Task 1); pooled 22 extras + 8
missings (row,col) sets equal M33's cluster sets exactly.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m35.py` invocation (the receipt, 13.8 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m35.py receipt | 13.8 s | exit 0; all guards pass; canon `658873e1…0eff01b` |
| control.py C-VAL | <1 s | green; sets + J + values + standings exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 11.5 s |
| Task 1 (per-cell per-site + pooled + headliners + join) | 2 | 0.4 s |
| Task 2 (per-cell joins + gap-sign + \|δ\| stats) | 2 | <1 s |
| Determinism re-run (Task 1 on s0+9, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m35.py` wall | — | 13.8 s |

## Step 2 — estimates

### Task 1 — shape-9 row reproduction + per-cell value tables

Shape-9 unnamed row recomputed from the dumps (FULL TSV guard
passed first — all 764 rows byte-identical): 15 cells with
n/ov/standings/deltas all exact (match=True on all 15):

| col | n/ov | n0 | miss/extra | delta | standing |
| ---: | --- | ---: | --- | ---: | --- |
| 310 | 1/0 | 0 | 0/1 | 1 | extra-only |
| 311 | 3/3 | 4 | 1/0 | 1 | missing-only |
| 312 | 2/1 | 3 | 2/1 | 3 | mixed |
| 313 | 6/4 | 4 | 0/2 | 2 | extra-only |
| 314 | 5/4 | 7 | 3/1 | 4 | mixed |
| 315 | 8/5 | 7 | 2/3 | 5 | mixed |
| 316 | 3/1 | 1 | 0/2 | 2 | extra-only |
| 318 | 3/0 | 0 | 0/3 | 3 | extra-only |
| 322 | 1/0 | 0 | 0/1 | 1 | extra-only |
| 327 | 2/0 | 0 | 0/2 | 2 | extra-only |
| 332 | 3/2 | 2 | 0/1 | 1 | extra-only |
| 336 | 1/0 | 0 | 0/1 | 1 | extra-only |
| 337 | 2/0 | 0 | 0/2 | 2 | extra-only |
| 339 | 1/0 | 0 | 0/1 | 1 | extra-only |
| 351 | 1/0 | 0 | 0/1 | 1 | extra-only |

(Pooled: 22 extras + 8 missings; missings live in 4/15 cells
(311/312/314/315); 11 cells read extra-only. c315's delta-5
(n/ov 8/5) and c314's delta-4 (5/4) confirmed as the only
mixed delta-5 and a tied delta-4.)

Near-miss shares per cell (H1/H2-style: near/far/noncell on
the other frame; extras vs s0, missings vs s9):

| col | extras near/far/non | missings near/far/non |
| ---: | --- | --- |
| 310 | 0/0/1 | — |
| 311 | — | 0/0/1 |
| 312 | 0/1/0 | 2/0/0 |
| 313 | 0/2/0 | — |
| 314 | 0/1/0 | 0/0/3 |
| 315 | 0/1/2 | 0/2/0 |
| 316 | 0/2/0 | — |
| 318 | 0/3/0 | — |
| 322 | 0/0/1 | — |
| 327 | 0/2/0 | — |
| 332 | 0/0/1 | — |
| 336 | 1/0/0 | — |
| 337 | 0/2/0 | — |
| 339 | 0/0/1 | — |
| 351 | 0/0/1 | — |
| pooled | 1/14/7 | 2/2/4 |

(All 3 near-misses: c336's extra (|δ_s0| 6) + c312's two
missings (|δ_9| 6, 7). Extra-side bulk |δ_s0| values:
1:11 2:3 6:1; missing-side bulk |δ_9| values: 2:1 3:1
6:1 7:1. Signed-gap equality: extras 1/22 (c351 −39/−39),
missings 2/8 (c315 (273,315) 23/23, c312 (301,312) 28/28).)

Extra-site table (all 22: cell, offset, plane, row, col;
|δ_9|; s0 status + |δ_s0|; signed gaps s9 vs s0):

| cell | offset | plane | (r,c) | \|δ_9\| | s0 status | \|δ_s0\| | g_9 | g_s0 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 310 | 323180 | Y | (252,310) | 8 | noncell | n/a | 22 | 2 |
| 312 | 318064 | Y | (248,312) | 13 | bulk | 1 | 33 | 10 |
| 313 | 344946 | Y | (269,313) | 12 | bulk | 1 | 39 | 7 |
| 313 | 346226 | Y | (270,313) | 9 | bulk | 1 | 28 | 6 |
| 314 | 315508 | Y | (246,314) | 13 | bulk | 1 | 32 | 9 |
| 315 | 314230 | Y | (245,315) | 13 | bulk | 2 | 60 | 6 |
| 315 | 370550 | Y | (289,315) | 16 | noncell | n/a | −34 | 0 |
| 315 | 371830 | Y | (290,315) | 11 | noncell | n/a | −26 | −2 |
| 316 | 312952 | Y | (244,316) | 14 | bulk | 1 | 59 | 7 |
| 316 | 314232 | Y | (245,316) | 8 | bulk | 1 | 56 | 8 |
| 318 | 307836 | Y | (240,318) | 16 | bulk | 1 | 34 | 5 |
| 318 | 309116 | Y | (241,318) | 25 | bulk | 2 | 93 | 11 |
| 318 | 311676 | Y | (243,318) | 13 | bulk | 1 | 53 | 11 |
| 322 | 351364 | Y | (274,322) | 8 | noncell | n/a | 21 | 2 |
| 327 | 297614 | Y | (232,327) | 12 | bulk | 2 | 25 | 5 |
| 327 | 298894 | Y | (233,327) | 14 | bulk | 1 | 29 | 4 |
| 332 | 391064 | Y | (305,332) | 28 | noncell | n/a | −62 | −55 |
| 336 | 306592 | Y | (239,336) | 8 | bulk | 6 | 17 | 14 |
| 337 | 300194 | Y | (234,337) | 10 | bulk | 1 | 21 | 4 |
| 337 | 301474 | Y | (235,337) | 8 | bulk | 1 | 17 | 4 |
| 339 | 306598 | Y | (239,339) | 15 | noncell | n/a | 39 | 35 |
| 351 | 289982 | Y | (226,351) | 19 | noncell | n/a | −39 | −39 |

Missing-site table (all 8: cell, |δ_s0|; s9 status + |δ_9|;
signed gaps s0 vs s9):

| cell | offset | plane | (r,c) | \|δ_s0\| | s9 status | \|δ_9\| | g_s0 | g_9 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 311 | 379502 | Y | (296,311) | 10 | noncell | n/a | 24 | 7 |
| 312 | 383344 | Y | (299,312) | 10 | bulk | 6 | 22 | 16 |
| 312 | 385904 | Y | (301,312) | 9 | bulk | 7 | 28 | 28 |
| 314 | 344948 | Y | (269,314) | 12 | noncell | n/a | 41 | 29 |
| 314 | 369268 | Y | (288,314) | 45 | noncell | n/a | 107 | 84 |
| 314 | 370548 | Y | (289,314) | 23 | noncell | n/a | 54 | 31 |
| 315 | 341110 | Y | (266,315) | 10 | bulk | 2 | 64 | 46 |
| 315 | 350070 | Y | (273,315) | 10 | bulk | 3 | 23 | 23 |

Headliners, tabled individually (full row lists + value stats):

c315 (mixed delta-5): s0 rows [266, 267, 268, 273, 274, 275,
276], s9 rows [245, 267, 268, 274, 275, 276, 289, 290] —
miss rows [266, 273], extra rows [245, 289, 290]. Extras
|δ_9| [11, 13, 16] (med 13.0, mean 13.3333), 1 bulk / 2
noncell, gaps ++/−−/−0 (1/3 ++); missings |δ_s0| [10, 10]
(med 10.0), 2/2 bulk, gaps 2/2 ++.

c314 (delta-4): s0 rows [269, 276, 277, 278, 287, 288, 289],
s9 rows [246, 276, 277, 278, 287] — miss rows [269, 288,
289], extra row [246]. Extra |δ_9| [13], bulk, gap ++;
missings |δ_s0| [12, 23, 45] (med 23.0, mean 26.6667),
0/3 bulk (all noncell), gaps 3/3 ++.

### Task 2 — joins (where do unnamed values live?)

Aggregate join (s9all: 22 extras / 8 missings / 94 shared —
recomputed with M27 machinery verbatim; every count below
equals M33's cluster join exactly):

Band (extras 21/22 band-1; shared 69/19/6):

| band | priv n/share | miss n/share | shared n/share |
| ---: | --- | --- | --- |
| 0 | 0 / 0.0000 | 0 / 0.0000 | 69 / 0.7340 |
| 1 | 21 / 0.9545 | 6 / 0.7500 | 19 / 0.2021 |
| 2 | 1 / 0.0455 | 2 / 0.2500 | 6 / 0.0638 |

Gradient decile (extras spread 7/8/9; missings dec-9 except
one dec-6):

| dec | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 0–5 | 0 | 0 | 0 |
| 6 | 0 | 1 | 1 |
| 7 | 2 | 0 | 2 |
| 8 | 5 | 0 | 6 |
| 9 | 15 | 7 | 85 |

(Dec-9 shares: priv 15/22 = 0.6818, miss 7/8 = 0.8750,
shared 85/94 = 0.9043.)

Streak columns (all 30 unnamed sites in `other`; every named
s0 site shared — streak joins N/A off the named set):

| col | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 257/277/296/301/321/340/342/343 | 0 | 0 | 10/10/9/11/10/8/5/2 |
| 341 | 0 | 0 | 0 |
| other | 22 | 8 | 29 |

Carrier cut (0 unnamed bytes in any top-10 mask — carrier
joins N/A; the 1 shared byte in 368's mask is M22's tabled
max-1 byte): all ranks priv_in=0 miss_in=0 (shared_in=0
except 368: 1). 701 split: priv 0/22, miss 0/8, shared
0/94 (all outside).

Per-cell band/decile table (the unnamed-cell equivalent of
M33's 21/22 band-1 — extras band/dec, missings band/dec):

| col | extras band | extras dec | missings band | missings dec |
| ---: | --- | --- | --- | --- |
| 310 | 1 | 8:1 | — | — |
| 311 | — | — | 1 | 9:1 |
| 312 | 1 | 9:1 | 2,2 | 6:1 9:1 |
| 313 | 1,1 | 9:2 | — | — |
| 314 | 1 | 9:1 | 1,1,1 | 9:3 |
| 315 | 1,1,1 | 8:1 9:2 | 1,1 | 9:2 |
| 316 | 1,1 | 8:1 9:1 | — | — |
| 318 | 1,1,1 | 8:1 9:2 | — | — |
| 322 | 1 | 9:1 | — | — |
| 327 | 1,1 | 9:2 | — | — |
| 332 | 2 | 9:1 | — | — |
| 336 | 1 | 7:1 | — | — |
| 337 | 1,1 | 7:1 8:1 | — | — |
| 339 | 1 | 9:1 | — | — |
| 351 | 1 | 9:1 | — | — |

(The pooled band-2 extras (1) + band-2 missings (2) are
c332's extra + c312's two missings; the pooled dec-6
missing is c312's (301,312); the pooled dec-7 extras are
c336's + c337's (235,337). Per-cell streak/carrier lines:
every cell reads all-other / 0-in / 701-all-out — full
lines in `m35.txt`.)

Gap-sign table (pooled + per cell; g_Q × g_O signs):

Pooled extras (n=22): ++=18 −−=3 −0=1 (++ share 0.8182).
Pooled missings (n=8): ++=8 (++ share 1.0000).

| col | extras signs | missings signs |
| ---: | --- | --- |
| 310 | ++ | — |
| 311 | — | ++ |
| 312 | ++ | ++,++ |
| 313 | ++,++ | — |
| 314 | ++ | ++,++,++ |
| 315 | ++,−−,−0 | ++,++ |
| 316 | ++,++ | — |
| 318 | ++,++,++ | — |
| 322 | ++ | — |
| 327 | ++,++ | — |
| 332 | −− | — |
| 336 | ++ | — |
| 337 | ++,++ | — |
| 339 | ++ | — |
| 351 | −− | — |

(The pooled extras' 3 −− are c315's (290,315) + c332's
(305,332) + c351's (226,351); the −0 is c315's (289,315),
static on s0.)

|δ| stats per cell (|δ_9| on extras, |δ_s0| on missings):

| col | extras list (med) | missings list (med) |
| ---: | --- | --- |
| 310 | [8] (8.0) | — |
| 311 | — | [10] (10.0) |
| 312 | [13] (13.0) | [9,10] (9.5) |
| 313 | [9,12] (10.5) | — |
| 314 | [13] (13.0) | [12,23,45] (23.0) |
| 315 | [11,13,16] (13.0) | [10,10] (10.0) |
| 316 | [8,14] (11.0) | — |
| 318 | [13,16,25] (16.0) | — |
| 322 | [8] (8.0) | — |
| 327 | [12,14] (13.0) | — |
| 332 | [28] (28.0) | — |
| 336 | [8] (8.0) | — |
| 337 | [8,10] (9.0) | — |
| 339 | [15] (15.0) | — |
| 351 | [19] (19.0) | — |

(Pooled extras: min 8, med 13.0, mean 13.3182, max 28.
Pooled missings: min 9, med 10.0, mean 16.1250, max 45.
Largest extra |δ|: 28 (c332), 25 (c318), 19 (c351); largest
missing |δ|: 45 + 23 (both c314).)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-VAL (known 6 priv + 4 miss) | priv 6 exact, miss 4 exact, J 0.9074, values + gaps + standings exact, cell fixed, orig kept | exact | True |

(Priv pool: 248 bulk gap≥17 Y; +8×2/−8×4 at
(25,334)/(26–28,305)/(42,98)/(44,81) with orig |δ| all 1.
Miss pool: 102 tail; +1 landing ×4 at r23 of c257/277/301/
321, 0 −1 fallbacks. Spanned Y cols 81/98/257/277/301/305/
321/334 with per-cell standings 4×extra-only + 4×missing-
only, rows exact on all 8. Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+9: per-cell per-site rows + pooled
summaries + headliner stats + aggregate join, fresh loads
incl. carriers) pass1 `658873e1…0eff01b` vs pass2
`658873e1…0eff01b`, identical=True; 215/215 lines
match=True; sets identical=True (extras 22, missings 8,
shared 94).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_CELLNEAR | extras with s0-bulk \|δ\|∈{6,7}, share ≥ 0.50 | 1/22 = 0.0455 — not met |
| H2_CELLSET | extras non-cell on s0, share ≥ 0.50 | 7/22 = 0.3182 — not met |
| H3_CELLMISS | missings non-cell on s9, share ≥ 0.50 | 4/8 = 0.5000 — met |
| H4_CELLLOCALIZE | \|extra−shared band-1\| ≥ 0.25 or \|extra−shared dec-9\| ≥ 0.25 | 0.7524 (band leg) / 0.2224 (decile leg) — met on band leg |
| H5_MISSGAP | missings +/+, share ≥ 0.50 | 8/8 = 1.0000 — met |
| H6_HEADBULK | c314+c315 delta rows bulk, share ≥ 0.50 | 4/9 = 0.4444 — not met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (FULL 764×33 TSV byte-identical; all 15 cells +
standings + deltas exact), by cell standing (11 extra-only
vs 1 missing-only vs 3 mixed with missings in only 4/15
cells), by other-frame status per cell (6 extra-only cells
read all-bulk while 5 read all-noncell with c315 split
1/2; missings read all-bulk in c312/c315 vs all-noncell in
c311/c314), by near-miss identity (all 3 nears in c336/
c312), and by headliner contrast (c315's missings all bulk
at |δ| 10/10 while c314's read all noncell at 12/23/45).
Task 2 discriminates by band (21/22 extras band-1 with the
band-2 stragglers in c332/c312), by decile (15/22 extras
dec-9 with the dec-7 pair in c336/c337), by gap sign
(missings 8/8 ++ while extras split 18 ++ / 3 −− / 1 −0
across 3 cells), by |δ| (extra medians 8.0–28.0 per cell
vs missing medians 9.5–23.0), and by streak/carrier
negatively (0 unnamed bytes in any named column or mask).

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

Screenshot: present by rule. The evidence value map
(`m35-valuemap.png`, 88748 B of 5242880 budget) colors s0
tail-Y by shared (green 94) / extra-bulk (yellow 15) /
extra-noncell (red 7) / missing-bulk (cyan 4) /
missing-noncell (magenta 4); DESIGN.md admits an evidence
copy iff H4 meets AND the winning leg's majority level
holds ≥8 extra sites — the band leg meets (0.7524) with
band 1 holding 21/22 extras.

Recorded without verdict: shape 9's 15 unnamed cells read 22
+ 8 sites at 100% luma with extras at 1 near / 14 far / 7
non-cell on s0 and missings at 2/2/4 on shape 9; c315's
delta-5 splits 3 extras (1 bulk) + 2 missings (both bulk)
while c314's delta-4 splits 1 extra (bulk) + 3 missings
(all noncell at |δ| up to 45); 21/22 extras sit in band-1
and all 30 sites sit outside the named streak columns with
0 bytes in any carrier mask; missings read 8/8 +/+ gaps
while extras read 18/22 ++; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| value suite + falsification bars, recorded before running | recorded | `DESIGN.md`: per-cell cross-value tables, s0-anchored band/decile/streak/carrier joins, gap-sign + \|δ\| stats, C-VAL control, bars H1–H6/N |
| shape-9 row + per-site + joins + wall/exit/shas/determinism | measured | §Step 2: 15-cell row exact + 30 per-site rows + joins + gap/\|δ\| stats; 13.8 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a value map discriminates (or absence reasoned) | measured | present by rule: H4 band leg + 21 extras in band 1; 88748 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m35"
cp local/research/M35/m35.py local/research/M35/control.py local/research/M35/DESIGN.md "/Volumes/Extreme SSD/m35/"
python3 m35.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34.txt" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m35" /Users/bradrichardson/dev/ssx3/local/research/M35 > m35.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m35/m35-valuemap.png" local/research/M35/m35-valuemap.png
```

## Paths

Evidence (committed): `local/research/M35/` — `DESIGN.md`
(suite + bars, recorded before running), `m35.py`
(per-cell values + joins + gap-sign + \|δ\| stats + PNG
writer), `control.py` (known-value control),
`m35-valuemap.png` (value map, 88748 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m35/` —
`m35.txt` (receipt: shas, baselines, guards, Task-1 per-cell
tables, joins, gap-sign, \|δ\| stats, re-run, PNG size),
`control.txt`, `m35.py`, `control.py`, `DESIGN.md` (working
copies), `m35-valuemap.png` (working copy, 88748 B). No
writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`,
`m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, or other
agents' dirs.

## Gap rows (exact next brief each needs)

1. Per-cell standing asymmetry (new): missings concentrate
   in 4/15 cells (311/312/314/315) while 11 cells read
   extra-only; c314's 3 missings read all non-cell (|δ|
   12/23/45) while c315's 2 read all bulk (|δ| 10/10).
   Needs its own brief only if per-cell standing splits
   matter: row-list + value comparison across the 4
   missing-bearing cells, offline — no new harness code.
2. Near-miss triple (new, minor): the only extra-side near
   (c336, |δ_s0| 6) + the only 2 missing-side nears (both
   c312, |δ_9| 6/7, one gap-equal 28/28) — 3/30 sites.
   Needs its own brief only if near-miss sites matter:
   boundary-|δ| census at unnamed cells, offline — no new
   harness code.
3. Big-|δ| unnamed sites (new, minor): c332 extra (28),
   c318 extra (25), c351 extra (19), c314 missings (45,
   23) — the 5 largest |δ| among the 30, 4/5 non-cell on
   the other frame. Needs its own brief only if large-|δ|
   values matter: value/row listing beyond the headliners,
   offline — no new harness code.
4. Still-below unnamed cells (M34 gap 2, still open): 2/3/700
   move unnamed at k 6/7/8 (J 0.9159/0.9340/0.8462). Needs
   its own brief: the same per-site value attribution for
   2/3/700's unnamed cells, offline — no new harness code.
5. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns; same-column opposite standings).
6. M33 gaps 1, 4–5 (still open, by reference): see M33
   REPORT gaps 1, 4–5 for the exact brief each needs
   (far/near private split; M29 gaps 5–11; M32 gap 1 + M31
   gap 2).

(M34 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No displacement/components: per-site values + joins are
   tabled without the M27-style dmin/component step (brief
   pins δ/gaps/bulk status; M33's cluster displacement
   stands).
2. No destination assignment for unnamed moves: standings
   are tabled without a displacement step (brief pins
   presence + values + joins only).
3. No explanation: values are attributed per cell, no rule;
   0 B explained.
4. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M35/`: `DESIGN.md`, `m35.py`,
`control.py`, `m35-valuemap.png` (88748 B, rule-met),
`REPORT.md` (this file).

