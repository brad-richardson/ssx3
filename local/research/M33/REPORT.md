# M33 — Shape-9 full-set attribution: mid-frame cluster privates + missings: REPORT

M29 gap 2 worked at table level: shape 9's tail recomputes to
117 B at Jaccard 0.7520 vs s0 (inter 94, union 125 — M29
matched exactly, stop rule not triggered), splitting into 23
private + 8 missing + 94 shared sites, all luma on both
sides. The 22 outside-col privates read 1 near / 14 far / 7
non-cell on s0 (H1 0.0455, H2 0.3182); the 8 missings read
2 near / 2 far / 4 non-cell on shape 9 (H6 0.5000); 21/22
privates read band-1 vs 19/94 shared (H4 met on the band
leg, 0.7524); the 22 privates span 14 s9-tail comps with at
most 4 in one (H5 0.1818); all 8 missings sit within d2 of
shared (d1 share 0.7500) while 17/22 privates read dmin ≥5
(H3 0.0455). Fully offline — no lease of any kind, no boots,
no harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M33.md`. Tables, no verdicts.

Headers read first: `local/research/M29/REPORT.md` (all of it:
6 recomputed partial cells, 9 delta-row sites at 7 far-bulk
/ 2 non-cell / 0 near, 8/9 dec-9, extra medians 8–9 vs
missing 18.0; s9 full sets priv 23 / miss 8 / shared 94 with
the 22+8 outside-col (row,col) lists) plus
`local/research/M27/REPORT.md` (Task-1 per-site table
precedent: offset/plane/row/col, cross-frame |δ|, signed gaps
both frames; full-swap reference: priv/miss 100% band-0, miss
100% dec-9, all non-cell on the other frame; displacement +
8-conn + s0-anchored join machinery reused verbatim).

Time box 4 hours (start 2026-09-20 03:55 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m32/` — all outputs went to the new
`/Volumes/Extreme SSD/m33/`): the s0/s9 triplets, `loo.txt`,
the M15 triplet (baseline guard only), the top-10 carrier
triplets, and `m29.txt` (match target). Work dir `/Volumes/
Extreme SSD/m33/`; evidence `local/research/M33/`.

Input shas (sha256 full, from the run receipt; s0/s9 + m15
prefixes match M17–M32):

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
| m29.txt | `d3a33d3c…7278fde` |

(Full hexes in `m33.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M32 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads 22815/23043 on s0/s9, both equal.
δ==0 violations read 0 on both shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 match exactly; s9
cell reads 2670. s9 c321 rows == s0 c321 rows + [266];
in-c321 priv rows == [266]; planes all-Y on both cluster
sets. M29 set guard (tail 117 + J 0.7520 + priv 23 / miss 8 /
shared 94 + outside-col 22/8 + both (row,col) SETS) matches
exactly. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m33.py` invocation (the receipt, 2.2 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m33.py receipt | 2.2 s | exit 0; all guards pass; canon `9a2553e5…f3a31ae2` |
| control.py C-CLUS | <1 s | green; sets + Jaccard + values exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Task 1 (full + cluster per-site + both joins) | 2 | 0.4 s |
| Task 2 (displace + comps + occupancy) | 2 | <1 s |
| Determinism re-run (Task 1 on s0+9, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m33.py` wall | — | 2.2 s |

## Step 2 — estimates

### Task 1 — cluster per-site tables (s9)

Cell-7 membership + tail membership recomputed from the dumps:
s0 2475 cell + 102 tail; s9 2670 cell + 117 tail with
J(T_9,T_s0) = 0.7520 (inter 94, union 125) — M29's counts
matched EXACTLY (stop rule not triggered). Full sets read
all-Y: priv 23/0/0, miss 8/0/0, shared 94/0/0 (Y/U/V).

Sets: priv P_9 = 23, miss M_9 = 8, shared S_9 = 94
(23 + 94 = 117 ✓, 8 + 94 = 102 ✓, 94/125 = 0.7520 ✓).
Cluster privates C_priv = 22 (P_9 minus the c321 r266 site);
cluster missings C_miss = 8 (all of M_9, all outside c321).

Cluster private-site table (all 22: offset, plane, row, col;
|δ_9|; s0 status + |δ_s0|; signed gaps s9 vs s0):

| offset | plane | (r,c) | \|δ_9\| | s0 status | \|δ_s0\| | g_9 | g_s0 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 289982 | Y | (226,351) | 19 | noncell | n/a | −39 | −39 |
| 297614 | Y | (232,327) | 12 | bulk | 2 | 25 | 5 |
| 298894 | Y | (233,327) | 14 | bulk | 1 | 29 | 4 |
| 300194 | Y | (234,337) | 10 | bulk | 1 | 21 | 4 |
| 301474 | Y | (235,337) | 8 | bulk | 1 | 17 | 4 |
| 306592 | Y | (239,336) | 8 | bulk | 6 | 17 | 14 |
| 306598 | Y | (239,339) | 15 | noncell | n/a | 39 | 35 |
| 307836 | Y | (240,318) | 16 | bulk | 1 | 34 | 5 |
| 309116 | Y | (241,318) | 25 | bulk | 2 | 93 | 11 |
| 311676 | Y | (243,318) | 13 | bulk | 1 | 53 | 11 |
| 312952 | Y | (244,316) | 14 | bulk | 1 | 59 | 7 |
| 314230 | Y | (245,315) | 13 | bulk | 2 | 60 | 6 |
| 314232 | Y | (245,316) | 8 | bulk | 1 | 56 | 8 |
| 315508 | Y | (246,314) | 13 | bulk | 1 | 32 | 9 |
| 318064 | Y | (248,312) | 13 | bulk | 1 | 33 | 10 |
| 323180 | Y | (252,310) | 8 | noncell | n/a | 22 | 2 |
| 344946 | Y | (269,313) | 12 | bulk | 1 | 39 | 7 |
| 346226 | Y | (270,313) | 9 | bulk | 1 | 28 | 6 |
| 351364 | Y | (274,322) | 8 | noncell | n/a | 21 | 2 |
| 370550 | Y | (289,315) | 16 | noncell | n/a | −34 | 0 |
| 371830 | Y | (290,315) | 11 | noncell | n/a | −26 | −2 |
| 391064 | Y | (305,332) | 28 | noncell | n/a | −62 | −55 |

Summary: near 1 (0.0455), far 14 (0.6364), noncell 7 (0.3182).
Bulk |δ_s0| values: 1:11 2:3 6:1. Signed-gap equality 1/22
((226,351) −39/−39), abs-gap equality 1/22. |δ_9|: min 8,
median 13.0, max 28. Gap signs g_9 +/−/0 = 18/4/0, g_s0
+/−/0 = 18/3/1 (the zero is (289,315), static on s0).

Cluster missing-site table (all 8: |δ_s0|; s9 status + |δ_9|;
signed gaps s0 vs s9):

| offset | plane | (r,c) | \|δ_s0\| | s9 status | \|δ_9\| | g_s0 | g_9 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 341110 | Y | (266,315) | 10 | bulk | 2 | 64 | 46 |
| 344948 | Y | (269,314) | 12 | noncell | n/a | 41 | 29 |
| 350070 | Y | (273,315) | 10 | bulk | 3 | 23 | 23 |
| 369268 | Y | (288,314) | 45 | noncell | n/a | 107 | 84 |
| 370548 | Y | (289,314) | 23 | noncell | n/a | 54 | 31 |
| 379502 | Y | (296,311) | 10 | noncell | n/a | 24 | 7 |
| 383344 | Y | (299,312) | 10 | bulk | 6 | 22 | 16 |
| 385904 | Y | (301,312) | 9 | bulk | 7 | 28 | 28 |

Summary: near 2 (0.2500), far 2 (0.2500), noncell 4 (0.5000).
Bulk |δ_9| values: 2:1 3:1 6:1 7:1. Signed-gap equality 2/8
((273,315) 23/23, (301,312) 28/28), abs-gap equality 2/8.
|δ_s0|: min 9, median 10.0, max 45. Gap signs both frames
all + (8/8 +/+).

Full-priv 23rd site (in-column c321 r266, attributed M29 —
recomputed values match M29's row exactly): o=341122 Y
(266,321) |δ_9|=9 s0 bulk |δ_s0|=1 g_9=19 g_s0=3. Full-priv
summary alongside: near 1 (0.0435), far 15 (0.6522), noncell
7 (0.3043); bulk-adO 1:12 2:3 6:1; gap equalities 1/23.

Near-miss check per set (pinned references: full swaps 100%
non-cell; M29 partials 7/9 = 0.7778 bulk):

| Set | n | near | far | noncell | bulk share |
| --- | ---: | --- | --- | --- | --- |
| cluster priv (22) | 22 | 1 (0.0455) | 14 (0.6364) | 7 (0.3182) | 15/22 (0.6818) |
| full priv (23) | 23 | 1 (0.0435) | 15 (0.6522) | 7 (0.3043) | 16/23 (0.6957) |
| cluster/full miss (8) | 8 | 2 (0.2500) | 2 (0.2500) | 4 (0.5000) | 4/8 (0.5000) |

(The cluster-priv bulk share 0.6818 falls on the M29-partial
side of the two references; the miss set splits 4/4.)

### Task 2 — cluster joins (one cluster or scatter?)

Position joins (s0-anchored M27 machinery verbatim; cluster
join C_priv 22 / C_miss 8 / S_9 94, full join alongside
where it differs):

Band (cluster priv 21/22 band-1; shared 69/19/6 = s0's
69/25/8 minus the 6 band-1 + 2 band-2 missings):

| band | priv n/share | miss n/share | shared n/share |
| ---: | --- | --- | --- |
| 0 | 0 / 0.0000 | 0 / 0.0000 | 69 / 0.7340 |
| 1 | 21 / 0.9545 | 6 / 0.7500 | 19 / 0.2021 |
| 2 | 1 / 0.0455 | 2 / 0.2500 | 6 / 0.0638 |

(Full-priv bands: 0/22/1 — the in-column r266 site is also
band-1.)

Gradient decile (cluster privates spread 7/8/9; missings
dec-9 except one dec-6):

| dec | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 0–5 | 0 | 0 | 0 |
| 6 | 0 | 1 | 1 |
| 7 | 2 | 0 | 2 |
| 8 | 5 | 0 | 6 |
| 9 | 15 | 7 | 85 |

(Dec-9 shares: priv 15/22 = 0.6818, miss 7/8 = 0.8750,
shared 85/94 = 0.9043; full-priv dec-9 16/23 = 0.6957.
Miss + shared per-decile n sums to s0's tail deciles: 2/2/6
/92 ✓.)

Streak columns (all 30 cluster sites outside the named set;
every named s0 site is shared):

| col | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 257 | 0 | 0 | 10 |
| 277 | 0 | 0 | 10 |
| 296 | 0 | 0 | 9 |
| 301 | 0 | 0 | 11 |
| 321 | 0 | 0 | 10 |
| 340 | 0 | 0 | 8 |
| 341 | 0 | 0 | 0 |
| 342 | 0 | 0 | 5 |
| 343 | 0 | 0 | 2 |
| other | 22 | 8 | 29 |

(Full-priv streak: c321 = 1 (the in-column site), other =
22. Shared other 29 = s0's 37 minus the 8 missings ✓.)

Carrier cut (inside counts; the 1 shared byte in 368's mask is
M22's tabled max-1 byte; the 1 full-priv byte in 693's mask
is the in-column r266 site per M29):

| rank/shape | cluster priv_in | miss_in | shared_in | full priv_in |
| ---: | ---: | ---: | ---: | ---: |
| 1/694, 3/701, 5–10 | 0 | 0 | 0 | 0 |
| 2/693 | 0 | 0 | 0 | 1 |
| 4/368 | 0 | 0 | 1 | 0 |

701 split: priv 0/22, miss 0/8, shared 0/94 (all outside;
full priv 0/23).

Displacement: nearest-shared-site dmin per cluster-private
site (same plane Manhattan; 0 impossible by construction —
guarded):

| (r,c) | dmin | (r,c) | dmin |
| --- | ---: | --- | ---: |
| (226,351) | 26 | (248,312) | 20 |
| (232,327) | 43 | (252,310) | 18 |
| (233,327) | 42 | (269,313) | 3 |
| (234,337) | 48 | (270,313) | 4 |
| (235,337) | 49 | (274,322) | 7 |
| (239,336) | 45 | (289,315) | 3 |
| (239,339) | 48 | (290,315) | 4 |
| (240,318) | 26 | (305,332) | 1 |
| (241,318) | 25 | — | — |
| (243,318) | 23 | — | — |
| (244,316) | 20 | — | — |
| (245,315) | 20 | — | — |
| (245,316) | 19 | — | — |
| (246,314) | 20 | — | — |

Hist: 1:1 2:0 3:2 4:2 5+:17 (d1 share 0.0455; full-priv hist
1:1 2:0 3:2 4:2 5+:18 — the in-column r266 site reads dmin
7). Rows 226–252 (16 sites) read dmin 18–49; rows 269–305
(6 sites) read dmin 1–7. Full-swap reference: privates dmin
5–19 with d1 share 0.

Missing mirror (all within d2 of shared):

| (r,c) | dmin | (r,c) | dmin |
| --- | ---: | --- | ---: |
| (266,315) | 1 | (289,314) | 2 |
| (269,314) | 2 | (296,311) | 1 |
| (273,315) | 1 | (299,312) | 1 |
| (288,314) | 1 | (301,312) | 1 |

Hist: 1:6 2:2 3:0 4:0 5+:0 (d1 share 0.7500).

Component view (8-conn on Y, M22 verbatim; U/V read 0/0 both
frames):

| Frame | comps | sizes 1/2/3–4/5–8/9+ | largest (share) |
| --- | ---: | ---: | --- |
| s0 | 25 | 9/3/5/3/5 | 11 (0.1078) |
| s9 | 39 | 17/10/5/2/5 | 11 (0.0940) |

s0 sizelist: `11 10 10 10 10 7 5 5 4 4 4 4 3 2 2 2 1×9`
(M22 reproduced). s9 sizelist:
`11 10 10 10 9 5 5 4×5 2×10 1×17`.

s9's comp5+ rows (named-column streak comps intact; the
r273–278 mid-frame comp shrinks 10→9):

| size | centroid (r,c) | bbox |
| ---: | ---: | --- |
| 11 | (28.0,301.0) | r[23,33]c[301,301] |
| 10 | (27.5,321.0) | r[23,32]c[321,321] |
| 10 | (27.5,277.0) | r[23,32]c[277,277] |
| 10 | (27.5,257.0) | r[23,32]c[257,257] |
| 9 | (275.7,314.0) | r[274,278]c[313,315] |
| 5 | (27.4,342.4) | r[26,29]c[342,343] |
| 5 | (26.0,296.0) | r[24,28]c[296,296] |

Per-s9-comp cluster-private occupancy (the 22 privates span
14 comps; max 4 in one):

| comp | size | cpriv | bbox |
| ---: | ---: | ---: | --- |
| li=10 | 4 | 4 | r[244,246]c[314,316] |
| li=15 | 2 | 2 | r[232,233]c[327,327] |
| li=16 | 2 | 2 | r[234,235]c[337,337] |
| li=17 | 2 | 2 | r[240,241]c[318,318] |
| li=19 | 2 | 2 | r[269,270]c[313,313] |
| li=20 | 2 | 2 | r[289,290]c[315,315] |
| li=21 | 2 | 1 | r[304,305]c[332,332] |
| li=24–29,32 | 1 | 1 each | (226,351) (239,336) (239,339) (243,318) (248,312) (252,310) (274,322) |

(All other 25 s9 comps hold 0 cluster privates, including
the li=31 in-column r266 singleton. cpriv-covered 22/22.)

Union-mask (T_9 ∪ T_s0) comps holding ≥1 of the 30 cluster
sites (16 comps; priv+miss interleave in two of them):

| comp | size | cpriv | cmiss | bbox |
| ---: | ---: | ---: | ---: | --- |
| li=6 | 6 | 2 | 2 | r[266,270]c[313,315] |
| li=9 | 5 | 2 | 2 | r[287,290]c[314,315] |
| li=13 | 4 | 4 | 0 | r[244,246]c[314,316] |
| li=5 | 7 | 0 | 3 | r[296,301]c[311,312] |
| li=4 | 10 | 0 | 1 | r[273,278]c[313,315] |
| li=17–19 | 2 | 2 each | 0 | pairs above |
| li=20 | 2 | 1 | 0 | r[304,305]c[332,332] |
| 7 singles | 1 | 1 each | 0 | as above |

(Union: 37 comps; max-cpriv-in-one 4; cmiss-covered 8/8.
The in-column r266 site is a union singleton.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-CLUS (known 22 priv + 8 miss) | priv 22 exact, miss 8 exact, J 0.7581, tailB 116, values exact, cell fixed, orig kept | exact | True |

(Priv pool: 248 bulk gap≥17 Y; +8×9/−8×13. Miss pool: 102
tail; +1 landing ×8, 0 −1 fallbacks. Full rows in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+9: full + cluster per-site rows +
both joins, fresh loads incl. carriers) pass1
`9a2553e5…f3a31ae2` vs pass2 `9a2553e5…f3a31ae2`,
identical=True; 163/163 lines match=True; sets
identical=True (priv 23, cpriv 22, miss 8, shared 94).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_CLUSNEAR | C_priv with s0-bulk \|δ\|∈{6,7}, share ≥ 0.50 | 1/22 = 0.0455 — not met |
| H2_CLUSSET | C_priv non-cell on s0, share ≥ 0.50 | 7/22 = 0.3182 — not met |
| H3_DISPLACE | C_priv within d1 of shared, share ≥ 0.50 | 1/22 = 0.0455 — not met |
| H4_LOCALIZE | \|cpriv−shared band-1\| ≥ 0.25 or \|cpriv−shared dec-9\| ≥ 0.25 | 0.7524 (band leg) / 0.2224 (decile leg) — met on band leg |
| H5_ONECOMP | largest s9 comp's C_priv count / 22 ≥ 0.50 | 4/22 = 0.1818 — not met |
| H6_MISSSET | C_miss non-cell on s9, share ≥ 0.50 | 4/8 = 0.5000 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
other-frame status (cluster privates 14/22 far bulk with
|δ| mostly 1–2 vs 7/22 non-cell — the inverse of full swaps'
100% non-cell and near M29 partials' 7/9 bulk; missings
split 4 bulk / 4 non-cell with both near-misses on the miss
side), by gap (1/22 signed-equal on privates vs 2/8 on
missings; private gaps run 17–93 with 4 negatives while
their s0 gaps read 2–14 except 35/0/−2/−39/−55), by band (priv
21/22 band-1 vs shared 19/94), by decile (priv 15/22 dec-9
vs miss 7/8 vs shared 85/94), by streak column (all 30
outside the named set while every named s0 site is shared),
and by carrier negatively (0 cluster bytes in any mask).
Task 2 discriminates by displacement asymmetrically (miss
d1 share 0.7500 with all ≤2; priv d1 share 0.0455 with
16 sites at 18–49 and 6 at 1–7), by component count (39 s9
comps vs 25 s0 comps with the 22 privates across 14 of
them, max 4 — scatter, not one comp), and by union
interleave (two comps mix 2 priv + 2 miss each at r266–270
and r287–290).

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
(`m33-clusmap.png`, 88752 B of 5242880 budget) colors s0
tail-Y by shared (green 94) / cluster-priv (yellow 22) /
cluster-miss (magenta 8) / in-column priv (red 1);
DESIGN.md admits an evidence copy iff H4 meets AND the
winning leg's majority level holds ≥8 C_priv sites — the
band leg meets (0.7524) with band 1 holding 21/22 privates.

Recorded without verdict: shape 9's divergence reads 23 + 8
sites at 100% luma with the 22 cluster privates at 1 near /
14 far / 7 non-cell on s0 and the 8 missings at 2/2/4 on
shape 9; the cluster sits 21/22 in band-1 and fully outside
the named streak columns with 0 bytes in any carrier mask;
missings hug shared (6/8 at d1) while privates split 16 far
(dmin 18–49) vs 6 near (dmin 1–7); the 22 privates scatter
across 14 s9-tail comps (max 4) with two union comps mixing
2 priv + 2 miss; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| attribution suite + falsification bars, recorded before running | recorded | `DESIGN.md`: full + cluster per-site cross-value tables, s0-anchored band/decile/streak/carrier joins, Manhattan displacement, 8-conn components + per-comp occupancy + union comps, C-CLUS control, bars H1–H6/N |
| cluster per-site + joins + displacement + comps + wall/exit/shas/determinism | measured | §Step 2: 30 per-site rows + joins + hists + 39/25 comps + occupancy; 2.2 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a cluster map discriminates (or absence reasoned) | measured | present by rule: H4 band leg + 21 privates in band 1; 88752 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m33"
cp local/research/M33/m33.py local/research/M33/control.py local/research/M33/DESIGN.md "/Volumes/Extreme SSD/m33/"
python3 m33.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m29/m29.txt" "/Volumes/Extreme SSD/m33" /Users/bradrichardson/dev/ssx3/local/research/M33 > m33.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m33/m33-clusmap.png" local/research/M33/m33-clusmap.png
```

## Paths

Evidence (committed): `local/research/M33/` — `DESIGN.md`
(suite + bars, recorded before running), `m33.py`
(attribution + joins + displacement + comps + occupancy +
PNG writer), `control.py` (known-cluster control),
`m33-clusmap.png` (cluster map, 88752 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m33/` —
`m33.txt` (receipt: shas, baselines, Task-1 per-site tables
both scopes, joins, displacement, comps, occupancy, re-run,
PNG size), `control.txt`, `m33.py`, `control.py`, `DESIGN.md`
(working copies), `m33-clusmap.png` (working copy, 88752 B).
No writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`,
`m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Far/near private split (new, minor): 16/22 cluster
   privates (rows 226–252) read dmin 18–49 with 12/16
   far-bulk on s0 (1 near, 3 non-cell), while 6/22 (rows
   269–305) read dmin 1–7
   interleaved with the missings in two mixed union comps.
   Needs its own brief only if sub-cluster structure
   matters: per-sub-block value/join split, offline — no new
   harness code.
2. Shape-709 c298 missings (M29 gap 3, still open): 4 missing
   rows in UNNAMED column c298 (r28/29/34/35) — a second
   partial column on 709 outside the census 8. Needs its own
   brief: unnamed-column partial scan (which shapes move
   unnamed columns by ≤2 rows), offline — no new harness
   code.
3. Shape-22 bottom cluster (M29 gap 4, still open): 2
   outside-col privates (393,307)/(402,295) + the 2 c296 far
   extras form a rows-393–402 group, all non-cell/bulk-unknown
   on s0 at byte level except the 2 delta rows. Needs its own
   brief only if bottom-frame privates matter: full-set
   attribution for shape 22, offline — no new harness code.
4. M29 gaps 5–11 (still open, by reference): see M29 REPORT
   gaps 5–11 for the exact brief each needs (still-below
   divergence 2/3/700, 711 pair wipe, 734 triple move, 732
   c296→c298 move, below-0.95 shape family,
   static-on-other-frame privates, M26 gaps 1–10/12–21) —
   with 9's windowed standing crossing at K=234 per M32.
5. M32 gap 1 + M31 gap 2 (still open, by reference): see M32
   REPORT gap 1 (between-grid K spot sweep) and M31 REPORT
   gap 2 (K=0 census standing) for the exact brief each
   needs.

(M29 gap 2 — this brief — worked at table level above.)

## What I could not do

1. No byte-level attribution beyond shape 9's own sets: the
   709-c298 missings and s22 bottom group stay located, not
   attributed (gaps 2–3 table the follow-ups).
2. No adopted rule or split: the far/near private blocks are
   tabled WITHOUT splitting the H-bars (gap 1 tables the
   follow-up).
3. No sub-cluster value fits: per-site |δ|/gaps are tabled
   as rows only (brief pins attribution, not value models).
4. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M33/`: `DESIGN.md`, `m33.py`,
`control.py`, `m33-clusmap.png` (88752 B), `REPORT.md` (this
file).
