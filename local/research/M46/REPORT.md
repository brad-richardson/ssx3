# M46 — Shape-9 far/near private split: per-sub-block value/join split: REPORT

M33 gap 1 worked at table level: the 22 cluster dmins recompute
exactly (far 18–49 + near 1–7 + hist 1:1 2:0 3:2 4:2 5+:17 —
stop rule not triggered), splitting into a far block (16, 12
far-bulk / 1 near / 3 non-cell on s0) and a near block (6, 2
far-bulk / 0 near / 4 non-cell) whose 4/6 sit in the two mixed
union comps (2 priv + 2 miss each, memberships reproduced). The
blocks differ in bulk status (0.8125 vs 0.3333, H1 0.4792) and
gap signs (++/15/16 vs 3/6, H2 0.4375), share seats (band-1
1.0000 vs 0.8333, dec-9 0.6250 vs 0.8333 — H3 not met on
either leg), read 13.0 vs 11.5 in median |δ_9| (H5 1.5), and
the near block reads missing-like in bulk status (0.3333 vs
0.5000, H4 met). Fully offline — no lease of any kind, no
boots, no harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M46.md`. Tables, no verdicts.

Headers read first: `local/research/M33/REPORT.md` (all of it:
M33 gap 1 = this brief — 16/22 cluster privates (rows
226–252) at dmin 18–49 with 12/16 far-bulk on s0 (1 near, 3
non-cell), 6/22 (rows 269–305) at dmin 1–7 interleaved with
the missings in two mixed union comps; displacement + 8-conn
+ s0-anchored join machinery reused verbatim) plus
`local/research/M35/REPORT.md` (shape-9's per-site values —
the value side of the split: pooled |δ|/gaps/signs +
band/decile seats; dstats/gapsign machinery reused verbatim).

Time box 4 hours (start 2026-09-20 06:21 EDT); used about 0.3.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m45/` — all outputs went to the new
`/Volumes/Extreme SSD/m46/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), `m33.txt`
(the 22 dmins + statuses to reproduce) and `m34-census.tsv`
(FULL TSV guard). Work dir `/Volumes/Extreme SSD/m46/`;
evidence `local/research/M46/`.

Input shas (sha256 full, from the run receipt; s0/s9 + m15
prefixes match M17–M45; `m34-census.tsv` matches M34/M35):

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
| m33.txt | `af6f50f6…f61b89a` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m46.txt` §inputs, plus all 30 top-10-carrier
triplet bins. `m33.txt` 30001 B; `m34-census.tsv` 163262 B —
matches M34's committed size.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M45 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34/M35
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s9 cell reads 2670. FULL unnamed TSV match
(all 764 rows) vs `m34-census.tsv`; s9 tail 117 + J 0.7520 +
full sets priv 23 / miss 8 / shared 94; cluster (row,col) SETS
(22 + 8) equal M33's exactly; far/near partition 16/6
disjoint with union == cpriv; `m33.txt` parse vs DESIGN pins
(22 dmins + 22 statuses + mixed-comp counts/bboxes) matches.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m46.py` receipt invocation (7.1 s, exit 0); one
`control.py` invocation (green). A first `m46.py` attempt died
pre-guard (`NameError`: the `m33.txt` parser sat below the
`__main__` guard — no receipt, no guard reached); the
definition was moved above the guard and the receipt run
started fresh. The C-SPLIT J expectation was corrected
pre-receipt from 98/110 to 98/114 = 0.8596 per the M33 union
rule (DESIGN.md notes the correction).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m46.py receipt | 7.1 s | exit 0; all guards pass; canon `5fe1965b…ef6de5d` |
| control.py C-SPLIT | <1 s | green; sets + J + dmins + values + seats exact |
| m46.py attempt 1 | — | pre-guard NameError; tabled, not a receipt |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows + TSV guard) | 764 | 6.3 s |
| Task 1 (pooled + per-block per-site + dmins + comps) | 2 | 0.1 s |
| Task 2 (per-block dstats + gapsign + joins + contrast) | 2 | 0.1 s |
| Determinism re-run (Task 1 on s0+9, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m46.py` wall | — | 7.1 s |

## Step 2 — estimates

### Task 1 — displacement reproduction (do the 22 dmins reproduce?)

All 22 dmins recomputed from the dumps (M33 method verbatim:
nearest-shared-site same-plane Manhattan) match the DESIGN
pins and the `m33.txt` parse exactly:

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

Hist: 1:1 2:0 3:2 4:2 5+:17 (d1 share 0.0455). Far block
(16): all 5+ (d1 share 0.0000). Near block (6): 1:1 2:0 3:2
4:2 5+:1 (d1 share 0.1667; the 5+ is (274,322)/7). Missing
mirror: 1:6 2:2 (d1 share 0.7500), per-site equal to the
`m33.txt` parse.

Status table (s0 status per site; far 12/1/3 + near 2/0/4):

| Block | (r,c) | s0 status | \|δ_s0\| |
| --- | --- | --- | ---: |
| far | (226,351) | noncell | n/a |
| far | (232,327) | bulk (far) | 2 |
| far | (233,327) | bulk (far) | 1 |
| far | (234,337) | bulk (far) | 1 |
| far | (235,337) | bulk (far) | 1 |
| far | (239,336) | bulk (near) | 6 |
| far | (239,339) | noncell | n/a |
| far | (240,318) | bulk (far) | 1 |
| far | (241,318) | bulk (far) | 2 |
| far | (243,318) | bulk (far) | 1 |
| far | (244,316) | bulk (far) | 1 |
| far | (245,315) | bulk (far) | 2 |
| far | (245,316) | bulk (far) | 1 |
| far | (246,314) | bulk (far) | 1 |
| far | (248,312) | bulk (far) | 1 |
| far | (252,310) | noncell | n/a |
| near | (269,313) | bulk (far) | 1 |
| near | (270,313) | bulk (far) | 1 |
| near | (274,322) | noncell | n/a |
| near | (289,315) | noncell | n/a |
| near | (290,315) | noncell | n/a |
| near | (305,332) | noncell | n/a |

Far summary: n=16 near=1 (0.0625) far=12 (0.7500) noncell=3
(0.1875); bulk-adO values 1:9 2:3 6:1; signed-gap equality
1/16 ((226,351) −39/−39). Near summary: n=6 near=0 far=2
(0.3333) noncell=4 (0.6667); bulk-adO values 1:2;
signed-gap equality 0/6.

Comp table (union-mask T_9 ∪ T_s0: 37 comps; the two mixed
comps with full membership — priv + miss + shared fill):

| comp | size | cpriv | cmiss | bbox | priv | miss | shared |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| li=6 | 6 | 2 | 2 | r[266,270]c[313,315] | (269,313) (270,313) | (266,315) (269,314) | (267,315) (268,315) |
| li=9 | 5 | 2 | 2 | r[287,290]c[314,315] | (289,315) (290,315) | (288,314) (289,314) | (287,314) |

(All other 35 union comps hold no priv+miss mix; cpriv-covered
22/22, cmiss-covered 8/8. The in-column r266 site is a union
singleton.)

### Task 2 — per-sub-block value/join split (values-deep or dmin-only?)

Value tables (|δ_9| lists, gap lists, gap-sign splits, bulk
statuses — numbers only):

| Block | n | \|δ_9\| list | min | med | mean | max |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| far-16 | 16 | [8,8,8,8,10,12,13,13,13,13,14,14,15,16,19,25] | 8 | 13.0 | 13.0625 | 25 |
| near-6 | 6 | [8,9,11,12,16,28] | 8 | 11.5 | 14.0000 | 28 |
| miss-8 | 8 | [9,10,10,10,10,12,23,45] (\|δ_s0\|) | 9 | 10.0 | 16.1250 | 45 |

Gap lists (g_9 / g_s0 per site, offset order):

| Block | (r,c) | g_9 | g_s0 | sign |
| --- | --- | ---: | ---: | --- |
| far | (226,351) | −39 | −39 | −− |
| far | (232,327) | 25 | 5 | ++ |
| far | (233,327) | 29 | 4 | ++ |
| far | (234,337) | 21 | 4 | ++ |
| far | (235,337) | 17 | 4 | ++ |
| far | (239,336) | 17 | 14 | ++ |
| far | (239,339) | 39 | 35 | ++ |
| far | (240,318) | 34 | 5 | ++ |
| far | (241,318) | 93 | 11 | ++ |
| far | (243,318) | 53 | 11 | ++ |
| far | (244,316) | 59 | 7 | ++ |
| far | (245,315) | 60 | 6 | ++ |
| far | (245,316) | 56 | 8 | ++ |
| far | (246,314) | 32 | 9 | ++ |
| far | (248,312) | 33 | 10 | ++ |
| far | (252,310) | 22 | 2 | ++ |
| near | (269,313) | 39 | 7 | ++ |
| near | (270,313) | 28 | 6 | ++ |
| near | (274,322) | 21 | 2 | ++ |
| near | (289,315) | −34 | 0 | −0 |
| near | (290,315) | −26 | −2 | −− |
| near | (305,332) | −62 | −55 | −− |

Gap-sign splits: far ++=15 −−=1 (++ share 0.9375); near
++=3 −−=2 −0=1 (++ share 0.5000); miss ++=8 (++ share
1.0000). Bulk statuses: far 13/16 bulk (0.8125), near 2/6
bulk (0.3333), miss 4/8 bulk (0.5000).

Join seats (s0-anchored band + gradient-decile distributions
per block; shared 94 alongside):

Band (far 16/16 band-1; near 5/6 band-1 + the (305,332)
band-2 site; miss 6/8 band-1):

| band | far n/share | near n/share | miss n/share | shared n/share |
| ---: | --- | --- | --- | --- |
| 0 | 0 / 0.0000 | 0 / 0.0000 | 0 / 0.0000 | 69 / 0.7340 |
| 1 | 16 / 1.0000 | 5 / 0.8333 | 6 / 0.7500 | 19 / 0.2021 |
| 2 | 0 / 0.0000 | 1 / 0.1667 | 2 / 0.2500 | 6 / 0.0638 |

Gradient decile (far spread 7/8/9; near 8/9; miss 6/9):

| dec | far | near | miss | shared |
| ---: | ---: | ---: | ---: | ---: |
| 0–5 | 0 | 0 | 0 | 0 |
| 6 | 0 | 0 | 1 | 1 |
| 7 | 2 | 0 | 0 | 2 |
| 8 | 4 | 1 | 0 | 6 |
| 9 | 10 | 5 | 7 | 85 |

(Dec-9 shares: far 10/16 = 0.6250, near 5/6 = 0.8333, miss
7/8 = 0.8750, shared 85/94 = 0.9043. Far+near per-decile n
sums to the pooled cluster join: 7:2 8:5 9:15 ✓.)

Streak columns (both blocks all-other; every named s0 site
shared): named cols priv=0 on all 9 levels for far, near,
and miss joins; other = 16/6/8 with shared other = 29.
Carrier cut: 0 block bytes in any top-10 mask on all three
joins (shared_in=0 except 368: 1 — M22's tabled max-1 byte).
701 split: far 0/16, near 0/6, miss 0/8 in (all outside).

Missing-contrast table (8 missings vs the near block):

| Measure | near-6 | miss-8 |
| --- | --- | --- |
| dmin list | [1,3,3,4,4,7] | [1,1,1,1,1,1,2,2] |
| d1 share | 0.1667 | 0.7500 |
| \|δ\| med (own frame) | 11.5 | 10.0 |
| \|δ\| mean | 14.0000 | 16.1250 |
| bulk share (other frame) | 2/6 = 0.3333 | 4/8 = 0.5000 |
| ++ share | 3/6 = 0.5000 | 8/8 = 1.0000 |
| band-1 share | 5/6 = 0.8333 | 6/8 = 0.7500 |
| dec-9 share | 5/6 = 0.8333 | 7/8 = 0.8750 |

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-SPLIT (known 6 far + 6 near + 4 miss) | priv 12 exact (far 6 + near 6), miss 4 exact, J 0.8596, far dmins 169–192, near dmins 1–6, values exact, seats 6/6 per block, cell fixed, orig kept | exact | True |

(Far pool: 248 bulk gap≥17 Y; +8×5/−8×7. Miss pool: 102
tail; +1 landing ×4, 0 −1 fallbacks. Miss dmins recomputed
[1,1,1,1]. Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+9: pooled + per-block per-site rows +
block dmins + union occupancy + mixed membership, fresh
loads) pass1 `5fe1965b…ef6de5d` vs pass2 `5fe1965b…ef6de5d`,
identical=True; 167/167 lines match=True; sets
identical=True (priv 23, cpriv 22, far 16, near 6, miss 8,
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
| H1_FARNEAR_BULK | \|far bulk − near bulk\| ≥ 0.25 | 0.8125 vs 0.3333, \|diff\| 0.4792 — met |
| H2_FARNEAR_GAP | \|far ++ − near ++\| ≥ 0.25 | 0.9375 vs 0.5000, \|diff\| 0.4375 — met |
| H3_FARNEAR_SEAT | \|far band-1 − near band-1\| ≥ 0.25 or \|far dec-9 − near dec-9\| ≥ 0.25 | 0.1667 (band leg) / 0.2083 (decile leg) — not met |
| H4_NEARMISS | \|near bulk − miss bulk\| < 0.25 | 0.3333 vs 0.5000, \|diff\| 0.1667 — met |
| H5_FARNEAR_MED | \|far med − near med\| ≥ 4 | 13.0 vs 11.5, \|diff\| 1.5 — not met |
| H6_NEARMIX | near in mixed comps ≥ 0.50 | 4/6 = 0.6667 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
displacement exactly (22/22 dmins + hist + 8/8 miss dmins
reproduced), by status asymmetrically (far 13/16 bulk with
the only near-miss vs near 2/6 bulk), and by union
interleave (exactly the pinned 2 mixed comps with full
priv/miss/shared memberships). Task 2 discriminates by bulk
status (H1 0.4792), by gap signs (far 15/16 ++ vs near 3/6
with the only −0 site — H2 0.4375), by band negatively
(both blocks band-1 except the single (305,332) band-2 near
site), by decile negatively (far holds all 6 non-dec-9
cluster seats yet H3's decile leg reads 0.2083), by |δ|
negatively (medians 13.0 vs 11.5 — H5 1.5), and by the
missing contrast (near reads missing-like in bulk status at
0.1667 while missing-like in seats at 0.0833/0.0417 but not
in gap signs at 0.5000).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; per-block tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence split map
(`m46-splitmap.png`, 88748 B of 5242880 budget) colors s0
tail-Y by shared (green 94) / far-block (yellow 16) /
near-block (orange 6) / cluster-miss (magenta 8) /
in-column priv (red 1); DESIGN.md admits an evidence copy
iff H1 meets AND the far block's majority status holds ≥8
far sites — H1 meets (0.4792) with far bulk at 13/16.

Recorded without verdict: the 22 dmins reproduce exactly
with far at 12 far-bulk / 1 near / 3 non-cell and near at 2
far-bulk / 0 near / 4 non-cell; the near block's 4/6 sit in
the two mixed union comps (2+2 each with shared fill 2/1)
while 0/16 far sites do; the blocks split on bulk status
(0.4792) and gap signs (0.4375) but share seats (band leg
0.1667, decile leg 0.2083) and |δ| level (13.0 vs 11.5);
the near block reads missing-like in bulk status (0.1667)
and seats but not in gap signs; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| split suite + falsification bars, recorded before running | recorded | `DESIGN.md`: pooled + per-block per-site tables, block Manhattan displacement, s0-anchored band/decile/streak/carrier joins, gap-sign + \|δ\| stats, union comps + mixed membership, C-SPLIT control, bars H1–H6/N |
| displacement reproduction + split tables + wall/exit/shas/determinism | measured | §Step 2: 22 dmins exact + 22 statuses + mixed membership + per-block value/seat tables + missing contrast; 7.1 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a sub-block map discriminates (or absence reasoned) | measured | present by rule: H1 + 13 far-bulk sites; 88748 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single exit-0 invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m46"
cp local/research/M46/m46.py local/research/M46/control.py local/research/M46/DESIGN.md "/Volumes/Extreme SSD/m46/"
python3 m46.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m33/m33.txt" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m46" /Users/bradrichardson/dev/ssx3/local/research/M46 > m46.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m46/m46-splitmap.png" local/research/M46/m46-splitmap.png
```

## Paths

Evidence (committed): `local/research/M46/` — `DESIGN.md`
(suite + bars, recorded before running), `m46.py`
(displacement + per-block values + joins + comps + PNG
writer), `control.py` (known far/near-block control),
`m46-splitmap.png` (split map, 88748 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m46/` —
`m46.txt` (receipt: shas, baselines, full-764 pass, TSV
guard, Task-1 per-block tables, Task-2 split tables, re-run,
PNG size; 31174 B), `control.txt` (1111 B), `m46.py`,
`control.py`, `DESIGN.md` (working copies),
`m46-splitmap.png` (working copy, 88748 B). No writes into
`m15/`, `m16/`, `m17/`–`m45/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Far-block dec-7/8 seats (new, minor): the far block
   holds all 6 non-dec-9 cluster seats (dec 7:2 / 8:4)
   while the near block reads 5/6 dec-9 — per-site seat
   identities are tabled only as distributions here.
   Needs its own brief only if sub-block seat identities
   matter: per-site band/decile rows for the 22, offline —
   no new harness code.
2. Band-2 near singleton (new, minor): (305,332) is the
   only band-2 cluster private and the max-|δ| private
   (28, −− gaps) at dmin 1. Needs its own brief only if
   band-2 privates matter: band-2 tail census across
   shapes, offline — no new harness code.
3. M33 gaps 2–5 (still open, by reference): see M33 REPORT
   gaps 2–5 for the exact brief each needs (709-c298
   missings; s22 bottom cluster; M29 gaps 5–11; M32 gap 1
   + M31 gap 2).
4. M35 gaps 1–5 (still open, by reference): see M35 REPORT
   gaps 1–5 for the exact brief each needs (per-cell
   standing asymmetry; near-miss triple; big-|δ| unnamed
   sites; still-below unnamed cells; M34 gaps 3–4).

(M33 gap 1 — this brief — worked at table level above.)

## What I could not do

1. No per-site seat identities: band/decile seats are
   tabled as per-block distributions only (gap 1 tables
   the follow-up).
2. No explanation: values are attributed per block, no
   rule; 0 B explained.
3. No byte-level work beyond shape 9's own sets: other
   shapes' splits stay located, not attributed (gaps 3–4
   table the follow-ups by reference).
4. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M46/`: `DESIGN.md`, `m46.py`,
`control.py`, `m46-splitmap.png` (88748 B), `REPORT.md` (this
file).
