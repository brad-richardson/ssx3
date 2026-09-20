# M41 — Near-miss triple: boundary-|δ| census at unnamed cells: REPORT

M35 gap 2 worked at table level: the 3 near-miss sites recompute
to the M35-pinned offsets, |δ| both frames, statuses, signed
gaps both frames, and gap signs exactly (3/3 — stop rule not
triggered), with (301,312) the only gap-equal site (28/28) and
all 3 in-band at other-frame |δ| 6/6/7. s9's boundary census
reads exact: 3/30 nears with 0 boundary-5 bulk sites on either
side and splits recounting to extras 1/14/7 + missings 2/2/4
(H3 met); still-below recounts to extras 14/0/10 + missings
0/0/10 with 0 boundary-5 (H2/H4 met); the cross-row extra-side
near-rate gap reads |0.0455−0.5833| = 0.5379 (H5 met). All 3
nears sit at row-list edges (H6 met; c336's singleton noted).
The supplemental raw-|δ|==8 scan reads empty on s9 both sides
and on all still-below extras, with the single hit the shared
(276,313) missing on s2+s3 (raw 8, noncell standing). Fully
offline — no lease of any kind, no boots, no harness code, no
`adb`. No device work. Runbook `local/muse/prompts/M41.md`.
Tables, no verdicts.

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 2 = this brief — the 3 near-miss sites; extras 1/14/7 +
missings 2/2/4; extra-side bulk |δ_s0| 1:11 2:3 6:1;
missing-side bulk |δ_9| 2:1 3:1 6:1 7:1) plus
`local/research/M36/REPORT.md` (all of it: the still-below
near split — extras 14/0/10 with all 14 nears at
|δ_s0|∈{6,7}, missings 0/0/10; per-shape per-site tables this
brief recounts) plus `local/research/M40/REPORT.md` (all of
it: the c312 missing values (299,312) bulk6 gaps 22/16,
(301,312) bulk7 gaps 28/28; measured s0c312 rows
[299,300,301]; s9 c312 rows [248,300]).

Time box 4 hours (start 2026-09-20 05:26 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m40/` — all outputs went to the new
`/Volumes/Extreme SSD/m41/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m34-census.tsv` + `m35.txt` + `m36.txt` (match targets). Work
dir `/Volumes/Extreme SSD/m41/`; evidence `local/research/M41/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M40; s9 prefixes match M35; s2/s3/s700 match M36):

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
| m16-v0-s0009 | `1926a151…ea086fe0` |
| m16-mid-s0009 | `a9fa67fb…bd5e9806` |
| m16-full-s0009 | `a9a5339d…207ae486` |
| m16-v0-s0700 | `cd5c2106…21af964` |
| m16-mid-s0700 | `d09dd3bb…25ae20` |
| m16-full-s0700 | `790c0826…dd5c482` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m34-census.tsv | `83482d1f…926c8aa8` |
| m35.txt | `ff29739c…49349c` |
| m36.txt | `bf2c5d81…8213ae1` |

(Full hexes in `m41.txt` §inputs. `m34-census.tsv` 163262 B;
`m35.txt` 69947 B; `m36.txt` 102945 B.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M40 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34–M40
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s2/s3/s9/s700 cell reads 2469/2484/2670/2605
(M36/M35-measured — equal, not just tabled); FULL unnamed TSV
match (all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv`; moved rows match the pinned k 15/6/7/8 +
n/ov + standings + deltas exactly on all 36 cells; pooled
counts read 22+8 / 5+4 / 4+3 / 15+3 exactly; all 64 pooled
sites Y-plane; all 64 pooled sites' (offset + |δ| + status +
gaps) match M35/M36 exactly; c336/c312 row pins match
§Task 1. Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m41.py` invocation (the receipt, 6.8 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m41.py receipt | 6.8 s | exit 0; all guards pass; canon `beb43158…78027206` |
| control.py C-NEAR | <1 s | green; standings + census + values + gaps exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 6.3 s |
| Task 1 (triple + near-def + rowlists) | 1 | <1 s |
| Task 2 (s9 census + still recount + cross-row) | 4 | <1 s |
| Determinism re-run (Task 1 on s0+9, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m41.py` wall | — | 6.8 s |

## Step 2 — estimates

### Task 1 — near-miss triple recompute (do the 3 sites reproduce?)

All 3 sites recomputed from the dumps (3/3 pins match M35
exactly — offsets, |δ| both frames, statuses, signed gaps both
frames, gap signs; gap-equal on (301,312) only):

| side | (r,c) | offset | plane | \|δ_own\| | other status | \|δ_other\| | g_own | g_other | sign | gapequal |
| --- | --- | ---: | --- | ---: | --- | ---: | ---: | ---: | --- | --- |
| extra | (239,336) | 306592 | Y | 8 (s9) | bulk (s0) | 6 | 17 | 14 | ++ | False |
| miss | (299,312) | 383344 | Y | 10 (s0) | bulk (s9) | 6 | 22 | 16 | ++ | False |
| miss | (301,312) | 385904 | Y | 9 (s0) | bulk (s9) | 7 | 28 | 28 | ++ | True |

Near-definition table (other-frame |δ| vs the {6,7} band):

| site | other-frame \|δ\| | in {6,7}? |
| --- | ---: | --- |
| extra (239,336) | 6 | True |
| miss (299,312) | 6 | True |
| miss (301,312) | 7 | True |

(In-band 3/3.)

Row-list context (c336's + c312's s0/s9 rows; edge = min/max
of the site's own-frame row-list, singletons noted):

| cell | s0 rows | s9 rows | extra rows | miss rows |
| --- | --- | --- | --- | --- |
| c336 | [] | [239] | [239] | [] |
| c312 | [299, 300, 301] | [248, 300] | [248] | [299, 301] |

| site | own-frame rows | row vs list | edge? |
| --- | --- | --- | --- |
| extra (239,336) | s9 [239] | only row | True (singleton) |
| miss (299,312) | s0 [299, 300, 301] | min | True |
| miss (301,312) | s0 [299, 300, 301] | max | True |

(Edge 3/3: the c312 nears bracket s0's 3-row list at min/max;
the c336 near is the cell's only s9 row.)

### Task 2 — boundary-|δ| census (is 3/30 exact? how do rows compare?)

s9 boundary census (all 30 pooled sites; other-frame |δ|
histogram over bulk + noncell count + boundary-5 count +
raw-|δ|==8 scan at any status):

| side | \|δ\| hist (bulk) | noncell | b5 | raw-8 hits |
| --- | --- | ---: | ---: | --- |
| extras (n=22) | 1:11 2:3 6:1 | 7 | 0 | none |
| missings (n=8) | 2:1 3:1 6:1 7:1 | 4 | 0 | none |

s9 near/far/noncell recount vs M35's splits:

| side | near/far/non | want | near (r,c) |
| --- | --- | --- | --- |
| extras | 1/14/7 | 1/14/7 | (239,336) |
| missings | 2/2/4 | 2/2/4 | (299,312), (301,312) |
| pooled | 3/30 | 3/30 | — |

(Bulk-8 is structurally 0 — cell-7 with |δ|≥8 on the other
frame would be tail there, contradicting extra/missing; the
raw-8 scan above closes the noncell hiding place: empty on
s9 both sides.)

Still-below recount (24 extras' |δ_s0| + 10 missings' |δ_Q|):

| shape/side | \|δ\| hist (bulk) | noncell | b5 | raw-8 hits |
| --- | --- | ---: | ---: | --- |
| s2 extras (n=5) | 7:1 | 4 | 0 | none |
| s2 missings (n=4) | — (all noncell) | 4 | 0 | (276,313) |
| s3 extras (n=4) | 7:2 | 2 | 0 | none |
| s3 missings (n=3) | — (all noncell) | 3 | 0 | (276,313) |
| s700 extras (n=15) | 6:2 7:9 | 4 | 0 | none |
| s700 missings (n=3) | — (all noncell) | 3 | 0 | none |
| pooled extras (n=24) | 6:2 7:12 | 10 | 0 | none |
| pooled missings (n=10) | — (all noncell) | 10 | 0 | (276,313) ×2 shapes |

Still-below near/far/noncell recount vs M36's splits:

| shape/side | near/far/non | want |
| --- | --- | --- |
| s2 extras | 1/0/4 | 1/0/4 |
| s2 missings | 0/0/4 | 0/0/4 |
| s3 extras | 2/0/2 | 2/0/2 |
| s3 missings | 0/0/3 | 0/0/3 |
| s700 extras | 11/0/4 | 11/0/4 |
| s700 missings | 0/0/3 | 0/0/3 |
| pooled extras | 14/0/10 | 14/0/10 |
| pooled missings | 0/0/10 | 0/0/10 |

(The 14 extra-side nears: s2c313's (7) + s3c316/c336's (7,7)
+ c54's ten (6:2 7:8) + s700c313's (7). Zero far sites on
either still-below side. The raw-8 scan's only hits across
all 64 pooled sites are the shared (276,313) missing on s2
and s3 — raw other-frame |mid−blend| 8 with noncell
standing.)

Cross-row near table (s9 vs s2/s3/s700, extra-side +
missing-side):

| side | row | near/far/non | n | near share |
| --- | --- | --- | ---: | --- |
| extra | s9 | 1/14/7 | 22 | 0.0455 |
| extra | s2 | 1/0/4 | 5 | 0.2000 |
| extra | s3 | 2/0/2 | 4 | 0.5000 |
| extra | s700 | 11/0/4 | 15 | 0.7333 |
| extra | still-pooled | 14/0/10 | 24 | 0.5833 |
| miss | s9 | 2/2/4 | 8 | 0.2500 |
| miss | s2 | 0/0/4 | 4 | 0.0000 |
| miss | s3 | 0/0/3 | 3 | 0.0000 |
| miss | s700 | 0/0/3 | 3 | 0.0000 |
| miss | still-pooled | 0/0/10 | 10 | 0.0000 |

(Extra-side gap |0.0455−0.5833| = 0.5379; missing-side gap
|0.2500−0.0000| = 0.2500, tabled with no bar.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-NEAR (known 2 near + 1 b5 + 1 far + 1 noncell) | standings 5×missing-only exact, rows exact, J 97/102, census 2/1/1/1 exact, values + gaps + statuses exact, other cols fixed, mask shrinks exact, orig kept | exact | True |

(Near pool: 2 injected ±6/±7 landings at (23,257)/(23,277)
with |δ| 6/7 bulk on B. Boundary pool: 1 injected ±5 landing
at (23,301), |δ| 5 bulk on B. Far pool: 1 injected ±2 landing
at (23,321), |δ| 2 bulk on B. Noncell pool: 1 injected
endpoint landing at (24,296), v0-endpoint, verified noncell
on B (no fallback fired). All 5 cells missing-only d1 with
mirows [23]/[23]/[23]/[23]/[24]; gaps equal both frames at
all 5 sites (42/37/43/36/46); cell-7 mask = maskA minus
exactly the noncell site; J 97/102. Full rows in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+9: 3-site rows + near-def + row-list
context, fresh loads) pass1 `beb43158…78027206` vs pass2
`beb43158…78027206`, identical=True; 11/11 lines
match=True; sets identical=True (s2 extras 5, missings 4;
s3 4/3; s9 22/8; s700 15/3).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_TRIPLE_REPRO | 3/3 near-miss sites read the pins exactly | 3/3, gapequal on (301,312) only — met |
| H2_STILL_REPRO | still-below near counts reproduce M36 (per-shape + pooled) | s2 1/0/4+0/0/4, s3 2/0/2+0/0/3, s700 11/0/4+0/0/3; pooled 14/0/10+0/0/10 — met |
| H3_S9_EXACT | pooled near is 3 AND b5 0 both sides AND splits 1/14/7 + 2/2/4 | 3/30, b5 0/0, splits exact — met |
| H4_STILL_EXACT | extras b5 0 AND near 14 AND far 0 AND noncell 10; missings 10/10 noncell | 0 + 14/0/10 + 0/0/10 — met |
| H5_CROSSROW | \|s9 extra near share − still-below extra near share\| ≥ 0.25 | \|0.0455−0.5833\| = 0.5379 — met |
| H6_ROWEDGE | 3/3 near sites read row-list-edge | 3/3 (c336 singleton noted) — met |
| H7_GAPEQUAL | exactly 1/3 near sites gap-equal, namely (301,312) | [(301, 312)] — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (3/3 pins exact — offsets, both-frame |δ|,
statuses, both-frame gaps, signs; gap-equal only on
(301,312) 28/28), by near-band membership (in-band 3/3 at
6/6/7), and by row position (c312's nears bracket s0's
3-row list at min/max while c336's near is its cell's only
s9 row). Task 2 discriminates by boundary histogram (s9
extra bulk |δ| 1:11 2:3 6:1 with b5 0; s9 missing bulk 2:1
3:1 6:1 7:1 with b5 0; still-below extra 6:2 7:12 with b5
0 and far 0), by split recount (1/14/7 + 2/2/4 on s9;
14/0/10 + 0/0/10 still-below), by the cross-row extra-side
gap (0.0455 vs 0.5833), and by the raw-8 scan positively
(the shared (276,313) missing on s2+s3 is the only raw-8
hit among all 64 pooled sites) and negatively everywhere
else (empty on s9 both sides, all still-below extras, and
all s700 missings).

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

Screenshot: present by rule. The evidence near-miss map
(`m41-nearmissmap.png`, 88761 B of 5242880 budget) colors
56 unique pooled (r,c) on s0 geometry by precedence — near
cyan 17 (any row) over far yellow 16 (any row) over s9
noncell magenta 11 over still-below noncell red 12;
DESIGN.md admits an evidence copy iff H1 meets AND H2 meets
AND H5 meets — all three meet (3/3 + 14/0/10 + 0.5379).

Recorded without verdict: s9's near-miss triple recomputes
to (239,336) bulk-6 17/14 ++, (299,312) bulk-6 22/16 ++,
and (301,312) bulk-7 28/28 gap-equal ++, all 3 in-band and
all 3 row-list-edge; s9's 3/30 stands exact with 0
boundary-5 bulk sites either side and empty raw-8 scans
while still-below reads 14/24 extra-side nears at 6:2 7:12
with 0 far and the only raw-8 hits at the shared (276,313)
missing (noncell standing); the cross-row extra-side
near-rate gap reads 0.5379; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| census suite + falsification bars, recorded before running | recorded | `DESIGN.md`: triple + near-def + rowlist tables, s9/still boundary hists + raw-8 scan, cross-row table, C-NEAR control, bars H1–H7/N |
| triple + census + wall/exit/shas/determinism | measured | §Step 2: 3/3 sites + hists + splits + cross-row; 6.8 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a near-miss map discriminates (or absence reasoned) | measured | present by rule: H1 + H2 + H5; 88761 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m41"
cp local/research/M41/m41.py local/research/M41/control.py local/research/M41/DESIGN.md "/Volumes/Extreme SSD/m41/"
python3 m41.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m35/m35.txt" "/Volumes/Extreme SSD/m36/m36.txt" "/Volumes/Extreme SSD/m41" /Users/bradrichardson/dev/ssx3/local/research/M41 > m41.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m41/m41-nearmissmap.png" local/research/M41/m41-nearmissmap.png
```

## Paths

Evidence (committed): `local/research/M41/` — `DESIGN.md`
(suite + bars, recorded before running), `m41.py`
(triple + census + cross-row + PNG writer), `control.py`
(known-census control), `m41-nearmissmap.png` (near-miss
map, 88761 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m41/` —
`m41.txt` (receipt: shas, baselines, guards, Task-1 triple
tables, census hists, cross-row table, re-run, PNG size;
32766 B), `control.txt` (2105 B), `m41.py`, `control.py`,
`DESIGN.md` (working copies), `m41-nearmissmap.png`
(working copy, 88761 B). No writes into `m15/`, `m16/`,
`m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`, `m23/`,
`m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`, `m30/`,
`m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`,
`m38/`, `m39/`, `m40/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Raw-8 noncell site (new, minor): the shared (276,313)
   missing on s2+s3 reads raw other-frame |mid−blend| 8 with
   noncell standing — the only raw-8 hit among all 64 pooled
   sites (s9's scans read empty both sides). Needs its own
   brief only if raw-boundary values at noncell sites matter:
   value/row listing of raw-|δ|==8 noncell sites across all
   rows, offline — no new harness code.
2. M40 gaps 1–2 (still open, by reference): see M40 REPORT
   gaps 1–2 for the exact brief each needs (missing-side
   magnitude split; extra-side sign split).
3. M39 gaps 1–2 (still open, by reference): see M39 REPORT
   gaps 1–2 for the exact brief each needs (extra-side sign
   asymmetry; extra-side |δ| spread).
4. M38 gap 1 (still open, by reference): see M38 REPORT gap
   1 for the exact brief it needs ((278,314) diverge-by-2).
5. M37 gaps 1–2 (still open, by reference): see M37 REPORT
   gaps 1–2 for the exact brief each needs (s761's
   column-54 tail quartet; 701 mask column block 54–65).
6. M36 gaps 1–3 (still open, by reference): see M36 REPORT
   gaps 1–3 for the exact brief each needs (c54 carrier
   coincidence; shared-site triple; s3 all-delta-1 row).
7. M35 gap 3 (still open, by reference): see M35 REPORT gap
   3 for the exact brief it needs (big-|δ| unnamed sites).
8. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns; same-column opposite standings).
9. M33 gaps 1, 4–5 (still open, by reference): see M33
   REPORT gaps 1, 4–5 for the exact brief each needs
   (far/near private split; M29 gaps 5–11; M32 gap 1 + M31
   gap 2).

(M35 gap 2 — this brief — worked at table level above. M35
gap 1 worked in M40.)

## What I could not do

1. No per-site values beyond s9's + 2/3/700's pooled cells:
   δ values and gaps at other unnamed moved cells are M35's
   and M36's tables by reference (brief pins s9 +
   still-below only).
2. No rule for the cross-row near-rate gap (0.0455 vs
   0.5833) or the raw-8 noncell hit: both are attributed
   per site per side, no rule (gap row 1).
3. No destination assignment for unnamed moves: row-lists
   are tabled without the M28-style displacement step
   (brief pins row-lists + values only).
4. No explanation: values are attributed per site per
   side, no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M41/`: `DESIGN.md`, `m41.py`,
`control.py`, `m41-nearmissmap.png` (88761 B, rule-met),
`REPORT.md` (this file).
