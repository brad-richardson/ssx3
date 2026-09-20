# M44 — Same-column opposite standings: c298 wipe-vs-growth + c311 11-vs-1: REPORT

M34 gap 4 worked at table level: c298 recomputes to the pinned
s0 rows [28,29,34,35] with 2 movers at 1/1/0 standings (FULL
764×33 TSV byte-identical to `m34-census.tsv` — stop rule not
triggered), splitting into 709's full 4-row wipe (all noncell
on 709, gaps −−/−0/−0/−0) vs 732's +2 growth at rows [26,27]
(both bulk on s0, |δ| 8/14, gaps −−/−−); c311 recomputes to
the pinned s0 rows [296,297,298,299] with 12 movers at 1/11/0
standings, splitting into s9's lone (296,311) missing (|δ| 10,
noncell, ++ — M35's values reproduced exactly) vs 11 extras
that read 10× (259,311) at byte-identical values (|δ| 17,
gaps −37/−37) + s3's (258,311) at |δ| 34. Bars read H1 met /
H2 not / H3 met / H4 not / H5 met / H6 not (lone 10 < crowd
med 17.0). Fully offline — no lease of any kind, no boots, no
harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M44.md`. Tables, no verdicts.

Headers read first: `local/research/M34/REPORT.md` (all of it:
gap 4 = this brief — c298 2 movers 1/1/0, c311 12 movers
1/11/0; the census method) plus `local/research/M35/REPORT.md`
(all of it: c311's missing-only mover is shape 9: missing
(296,311) |δ_s0| 10 noncell ++ — the 1 in the 11-vs-1) plus
`local/research/M28/REPORT.md` (all of it: 732's c296→c298
move context + 709-c298's [28,29,34,35] wipe rows) plus
`local/research/M36/REPORT.md` (M36-style per-site rows: s2
[259], s3 [258], s700 [259]).

Time box 4 hours (start 2026-09-20 05:58 EDT); used about 0.3.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m43/` — all outputs went to the new
`/Volumes/Extreme SSD/m44/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m34-census.tsv` (match target). Work dir
`/Volumes/Extreme SSD/m44/`; evidence `local/research/M44/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M43; 709 prefixes match M29/M34; s9 prefixes match
M33/M35; s2/s3/s700 prefixes match M36):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0709 | `6b776020…85fb471f` |
| m16-mid-s0709 | `bb35990e…2dcdac9f` |
| m16-full-s0709 | `6d1e6b6d…00cb5a1` |
| m16-v0-s0732 | `581154c1…2b158343` |
| m16-mid-s0732 | `9d1e9e78…01277b69` |
| m16-full-s0732 | `edaf6fc9…1b77c3ff` |
| m16-v0-s0009 | `1926a151…ea086fe0` |
| m16-mid-s0009 | `a9fa67fb…bd5e9806` |
| m16-full-s0009 | `a9a5339d…207ae486` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m44.txt` §inputs, plus all s2/s3/s380–s389/
s700 triplet bins. `m34-census.tsv` 163262 B — matches M34's
committed size. Triplet fold sha over all 764×3 bins:
`6c906897…61fd423b1` — matches M28/M34 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M43 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 match exactly. FULL
unnamed TSV match (all 764 rows: tail + J4 + all-33-column
n/ov/pres) vs `m34-census.tsv`; c298 row (s0 rows, movers
[709,732], 709 0/0, 732 6/4, 1/1/0) + c311 row (s0 rows,
12-mover set, per-shape n/ov, 1/11/0) match exactly (§Tasks
1–2); 732 keeps all 4 s0 c298 rows; s9's c311 miss row [296]
+ s2/s3/s700 extra rows [259]/[258]/[259] reproduce M35/M36;
lone (296,311) values reproduce M35 exactly (10/noncell/24/7).
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m44.py` invocation (the receipt, 3.0 s, exit 0 — a first
attempt died at the bar-measurement section on a NameError
(`m0` vs `mask0`), fixed before the receipt run; the receipt
is the single green invocation below, estimator unchanged
after it started); `control.py` green after two tabled
control-only fixes (§Controls — receipt estimator untouched).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m44.py receipt | 3.0 s | exit 0; all guards pass; canon `d322f6d3…caae677` |
| control.py O-OPP | <1 s | green; sets + J + rows + values + standings exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 2.6 s |
| Tasks 1–2 (row-lists + per-site values + comparisons) | 15 | 0.1 s |
| Determinism re-run (Tasks 1–2, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m44.py` wall | — | 3.0 s |

## Step 2 — estimates

### Task 1 — c298 wipe-vs-growth (row-lists + values)

c298 recomputed from the dumps (FULL TSV guard passed first —
all 764 rows byte-identical): s0 rows [28,29,34,35], movers
[709 (0/0 wipe), 732 (6/4 growth)], standings 1/1/0 — all
exact.

Row-list table (the 2 grown rows are the new data):

| Shape | n | rows |
| --- | ---: | --- |
| s0 | 4 | [28, 29, 34, 35] |
| s709 (wipe) | 0 | [] |
| s732 (growth) | 6 | [26, 27, 28, 29, 34, 35] |

Wipe rows [28,29,34,35] (n=4); grow rows [26,27] (n=2); keep
rows [28,29,34,35] (n=4 — 732 keeps all of s0's rows).

Wiped-site table (all 4: |δ_s0|; s709 status + |δ_709|;
signed gaps s0 vs s709):

| offset | plane | (r,c) | \|δ_s0\| | s709 status | \|δ_709\| | g_s0 | g_709 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 36436 | Y | (28,298) | 11 | noncell | n/a | −26 | −1 |
| 37716 | Y | (29,298) | 8 | noncell | n/a | −18 | 0 |
| 44116 | Y | (34,298) | 13 | noncell | n/a | −28 | 0 |
| 45396 | Y | (35,298) | 13 | noncell | n/a | −28 | 0 |

Grown-site table (both: |δ_732|; s0 status + |δ_s0|; signed
gaps s732 vs s0):

| offset | plane | (r,c) | \|δ_732\| | s0 status | \|δ_s0\| | g_732 | g_s0 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 33876 | Y | (26,298) | 8 | bulk | 1 | −19 | −5 |
| 35156 | Y | (27,298) | 14 | bulk | 6 | −33 | −17 |

Kept-row table (all 4: both-frame |δ| + gaps, both tail):

| offset | plane | (r,c) | \|δ_s0\| | \|δ_732\| | g_s0 | g_732 |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 36436 | Y | (28,298) | 11 | 14 | −26 | −32 |
| 37716 | Y | (29,298) | 8 | 8 | −18 | −18 |
| 44116 | Y | (34,298) | 13 | 14 | −28 | −32 |
| 45396 | Y | (35,298) | 13 | 13 | −28 | −28 |

(Signed-gap equality on kept rows: 2/4 — (29,298) −18/−18 and
(35,298) −28/−28.)

Wipe-vs-growth comparison (numbers only):

| Set | \|δ\| list | med | mean | bulk/noncell (other) | gap signs |
| --- | --- | ---: | ---: | --- | --- |
| wiped (on s0) | [8,11,13,13] | 12.0 | 11.2500 | 0/4 on 709 | −−=1 −0=3 |
| grown (on 732) | [8,14] | 11.0 | 11.0000 | 2/0 on s0 (1 near, 1 far) | −−=2 |
| kept (on s0) | [8,11,13,13] | 12.0 | 11.2500 | 4/0 tail both | −−=4 |
| kept (on 732) | [8,13,14,14] | 13.5 | 12.2500 | 4/0 tail both | −−=4 |

(The grown (27,298) site reads s0-bulk |δ_s0| 6 — the only
near-miss in Task 1. Wiped gaps: 3/4 read g_709 = 0 with the
4th at −1.)

### Task 2 — c311 11-vs-1 (row-lists + values)

c311 recomputed from the dumps: s0 rows [296,297,298,299], 12
movers, standings 1/11/0 — all exact.

Mover table (all 12 with standings + rows; the 8 unknown
extra-only movers' rows are the new data — all read [259]):

| Shape | tail | J vs s0 | n/ov | rows | ex/mi | standing |
| ---: | ---: | ---: | --- | --- | --- | --- |
| 2 | 103 | 0.9159 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 3 | 103 | 0.9340 | 5/4 | [258,296,297,298,299] | ex [258] | extra-only |
| 9 | 117 | 0.7520 | 3/3 | [297,298,299] | mi [296] | missing-only |
| 380 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 381 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 382 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 383 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 384 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 386 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 387 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 389 | 103 | 0.9903 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |
| 700 | 114 | 0.8462 | 5/4 | [259,296,297,298,299] | ex [259] | extra-only |

Lone-site row (s9's (296,311) — M35's 10/noncell/24/7
reproduced exactly):

| offset | plane | (r,c) | \|δ_s0\| | s9 status | \|δ_9\| | g_s0 | g_9 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 379502 | Y | (296,311) | 10 | noncell | n/a | 24 | 7 |

Crowd-site rows (all 11, one per mover — the 10 (259,311)
rows read byte-identical values across 10 shapes):

| Mover | offset | plane | (r,c) | \|δ_Q\| | s0 status | \|δ_s0\| | g_Q | g_s0 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 2 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 3 | 330862 | Y | (258,311) | 34 | noncell | n/a | −71 | −71 |
| 380 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 381 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 382 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 383 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 384 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 386 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 387 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 389 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 700 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |

(Signed-gap equality: 11/11 crowd rows (gap-equal −37/−37 ×10
+ −71/−71 ×1); lone 0/1 (24/7). Crowd union sites n=2 over 11
pairs.)

Lone-vs-crowd comparison (numbers only):

| Set | \|δ\| list | med | mean | bulk/noncell (other) | gap signs |
| --- | --- | ---: | ---: | --- | --- |
| lone (on s0) | [10] | 10.0 | 10.0000 | 0/1 on s9 | ++=1 |
| crowd (on Q) | [17×10, 34] | 17.0 | 18.5455 | 0/11 on s0 | −−=11 |

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| O-OPP B (wipe+lone) | P 0 exact, M 5 exact, J 97/102=0.9510, rows + values + gaps + standings exact, mask fixed, orig kept | exact | True |
| O-OPP C1 (growth+crowd-A) | P 2 exact, M 0 exact, J 102/104=0.9808, rows + values + gaps + standings exact, mask fixed, orig kept | exact | True |
| O-OPP C2 (crowd-B) | P 1 exact, M 0 exact, J 102/103=0.9903, rows + values + gaps + standings exact, mask fixed, orig kept | exact | True |

(Injected sets: B misses (28–29,34–35,298) + (296,311) at
|δ|=1, 0 −1 fallbacks; C1 extras (27,298) + (300,311) at
|δ|=8; C2 extra (301,311) at |δ|=8. Orig |δ_s0| at extra
sites: 6/5/5. c298 reads B-wipe + C1-growth(+1) + C2-present;
c311 reads B-miss1 + C1-extra1 + C2-extra1. Full rows in
`control.txt`. Two tabled control-only deviations from the
DESIGN pin, receipt estimator untouched: (a) as-pinned
parity-sign picking is infeasible on c298 — its sole bulk
gap≥17 candidate (27,298) admits only +8 (parity wants −8,
lands on lo) — so the run uses parity-first with per-site
other-sign fallback (1 fallback: (27,298) +8; evidence
`control-pinned-infeasible.txt` in the work dir preserves the
as-pinned infeasible report); (b) c298 want-2 reads K'=1
(only 1 suitable site exists in the column — tabled per the
DESIGN K' rule), so C1 grows c298 by 1 row. KNOWN properties
(rows, |δ| 8/1, gap equality, statuses, J rationals) and pass
criteria unchanged.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Tasks 1–2 row-lists + per-site value rows on
s0+709+732+9 + all c311 movers, fresh loads) pass1
`d322f6d3…caae677` vs pass2 `d322f6d3…caae677`,
identical=True; 150/150 lines match=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_WIPESET | wiped noncell on 709, share ≥ 0.50 | 4/4 = 1.0000 — met |
| H2_GROWSET | grown noncell on s0, share ≥ 0.50 | 0/2 = 0.0000 — not met |
| H3_CROWDSET | crowd noncell on s0, share ≥ 0.50 | 11/11 = 1.0000 — met |
| H4_WIPEGAP | wiped ++, share ≥ 0.50 | 0/4 = 0.0000 — not met |
| H5_CROWDGAP | crowd −−, share ≥ 0.50 | 11/11 = 1.0000 — met |
| H6_LONEMAG | lone \|δ\| ≥ crowd \|δ\| med | 10 ≥ 17.0 — not met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
row-list (732 grows exactly [26,27] above s0's 4 kept rows
while 709 wipes all 4), by other-frame status (wiped 4/4
noncell on 709 while grown 2/2 bulk on s0 with the (27,298)
near at |δ_s0| 6), by gap sign (wiped −−/−0/−0/−0 with 3
g_709 zeros while grown −−/−− and kept −−×4), and by |δ|
(wiped [8,11,13,13] vs grown [8,14] vs kept [8,13,14,14] on
732). Task 2 discriminates by row identity (all 8 unknown
crowd extras read the same row [259] as s2/s700, s3 alone
[258]), by value identity (10/11 crowd rows byte-identical at
17/noncell/−37/−37 with s3's 34/−71/−71 the outlier), by gap
sign (lone ++ vs crowd −−×11, all gap-equal), and by |δ|
(lone 10.0 vs crowd med 17.0).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; per-site tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: absent by rule. The working split-column map
(`m44-splitmap.png`, 88538 B of 5242880 budget) stays in the
work dir only; DESIGN.md admits an evidence copy iff H4 meets
AND H5 meets — H4 does not meet (0.0000).

Recorded without verdict: c298 reads a 4-row wipe (all
noncell, gaps −−/−0/−0/−0) against +2 growth at rows [26,27]
(both bulk, |δ| 8/14) over 4 kept rows (kept |δ| up on 3/4
rows); c311 reads 1 lone missing at (296,311) (|δ| 10, ++) vs
11 extras at 2 union sites (10× (259,311) byte-identical at
17/−− plus s3's (258,311) at 34/−−); H1/H3/H5 meet while
H2/H4/H6 do not; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| opposite-standings suite + falsification bars, recorded before running | recorded | `DESIGN.md`: c298/c311 row-lists + M36-style per-site rows + kept-row values + wipe-vs-growth / lone-vs-crowd comparisons, O-OPP control, bars H1–H6/N |
| c298 row-lists + values + comparison + wall/exit/shas/determinism | measured | §Task 1: s0/709/732 rows + 4 wiped + 2 grown + 4 kept per-site rows + comparison; 3.0 s; re-run identical |
| c311 mover table + values + comparison | measured | §Task 2: 12-mover table + lone + 11 crowd per-site rows + comparison |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a split-column map discriminates (or absence reasoned) | measured | absent by rule: H4 not met (0.0000); 88538 B working copy only |
| controls (known opposite standings, rows + values exact) | measured | §Controls: O-OPP B/C1/C2 all exact; 2 control-only deviations tabled (sign fallback, K'=1) |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single green invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m44"
cp local/research/M44/m44.py local/research/M44/control.py local/research/M44/DESIGN.md "/Volumes/Extreme SSD/m44/"
python3 m44.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m44" /Users/bradrichardson/dev/ssx3/local/research/M44 > m44.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

(No evidence PNG copy — the DESIGN.md rule is not met.)

## Paths

Evidence (committed): `local/research/M44/` — `DESIGN.md`
(suite + bars, recorded before running), `m44.py`
(row-lists + per-site values + comparisons + PNG writer),
`control.py` (known-opposite-standings control),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m44/` —
`m44.txt` (receipt: shas, baselines, guards, Task-1/2 tables,
re-run, PNG size), `control.txt`,
`control-pinned-infeasible.txt` (as-pinned control run,
infeasible per the DESIGN K' rule — kept for audit), `m44.py`,
`control.py`, `DESIGN.md` (working copies),
`m44-splitmap.png` (working copy, 88538 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`,
`m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`, `m30/`,
`m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`, `m38/`,
`m39/`, `m40/`, `m41/`, `m42/`, `m43/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Crowd site identity (new): 10/11 c311 crowd extras are the
   SAME site (259,311) with byte-identical values (|δ| 17,
   gaps −37/−37) across 10 shapes; s3 alone reads (258,311)
   at |δ| 34. Needs its own brief only if shared extra sites
   matter: cross-shape identity census at unnamed extras +
   value table, offline — no new harness code.
2. Kept-row value shift (new): c298 kept rows read |δ|
   [11,8,13,13] on s0 vs [14,8,14,13] on 732 — 3/4 rows gain
   |δ| under growth. Needs its own brief only if kept-row
   drift matters: both-frame |δ| comparison at kept rows,
   offline — no new harness code.
3. Wiped-gap zeros (new, minor): 3/4 wiped c298 sites read
   g_709 = 0 (endpoint-static on 709) with the 4th at −1.
   Needs its own brief only if wipe statics matter:
   endpoint-static census at wiped sites, offline — no new
   harness code.
4. Earlier gaps (still open, by reference): see the M34–M43
   REPORT gap rows for the exact brief each needs (M34 gap 4
   — this brief — worked at table level above).

## What I could not do

1. Control as pinned is infeasible on c298: its sole bulk
   gap≥17 candidate admits only +8, and want-2 reads K'=1 —
   ran parity-first-with-fallback at K'=1 with the as-pinned
   infeasible report preserved (tabled in §Controls).
2. No position joins: band/decile/streak/carrier attribution
   is out of scope (brief pins row-lists + per-site values
   only).
3. No destination/displacement analysis for the grown rows
   (census is presence + values by brief).
4. Screenshot absent by rule (H4 not met) — working copy
   only.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M44/`: `DESIGN.md`, `m44.py`,
`control.py`, `REPORT.md` (this file).
