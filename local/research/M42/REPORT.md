# M42 — Big-|δ| unnamed sites: value/row listing beyond the headliners: REPORT

M35 gap 3 worked at table level: the 5 big-|δ| sites recompute
to the M35-pinned offsets, |δ| both frames, statuses, signed
gaps both frames, and gap signs exactly (5/5 — stop rule not
triggered), with (226,351) the only gap-equal site (−39/−39)
and 4/5 non-cell on the other frame (the bulk one is
(241,318) at |δ_s0| 2). Ranks read exact: extras 28/25/19 at
1/2/3 of 22, missings 45/23 at 1/2 of 8, pooled order
45 > 28 > 25 > 23 > 19 (H2 met); 2/5 sit in the headlined
c314 (both missings) with 0/5 in c315. The top-10 extras list
reads two near-big sites at 16 ((240,318) bulk ++,
(289,315) noncell −0) with no 17/18 anywhere among the 30
(H4 met); missings read 45/23 then 12/10/10/10/10/9. Row
geometry reads 3/5 edge (c351 singleton, c332 max, c314-289
max) with the c314 big pair at row distance 1 and all other
pairwise distances ≥15 (H5 met); seats read 5/5 dec-9 with
bands 1/1/1/1/2 (H6 met); gap signs read 3 ++ / 2 −− (H7
met). Fully offline — no lease of any kind, no boots, no
harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M42.md`. Tables, no verdicts.

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 3 = this brief — the 5 big sites; extras 1/14/7 +
missings 2/2/4; extra |δ_9| min 8 med 13.0 mean 13.3182 max
28; missing |δ_s0| min 9 med 10.0 mean 16.1250 max 45;
per-cell band/decile + gap-sign + |δ| tables; c314 s0 rows
[269,276,277,278,287,288,289] s9 rows [246,276,277,278,287])
plus `local/research/M41/REPORT.md` (all of it: the boundary
census — s9 splits 1/14/7 + 2/2/4; the far side is where
these 5 live; standing + row-edge conventions).

Time box 4 hours (start 2026-09-20 05:40 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m41/` — all outputs went to the new
`/Volumes/Extreme SSD/m42/`): the 764 M16 per-shape triplets,
`loo.txt`, and `m35.txt` + `m34-census.tsv` (match targets).
Work dir `/Volumes/Extreme SSD/m42/`; evidence
`local/research/M42/`.

Input shas (sha256 full, from the run receipt; s0 + s9 prefixes
match M17–M41):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0009 | `1926a151…ea086fe0` |
| m16-mid-s0009 | `a9fa67fb…bd5e9806` |
| m16-full-s0009 | `a9a5339d…207ae486` |
| m35.txt | `ff29739c…49349c` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m42.txt` §inputs. `m35.txt` 69947 B;
`m34-census.tsv` 163262 B — matches M35's/M34's committed
sizes.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 22815 + fnv match M17–M41 exactly (s0-only
baseline this brief — DESIGN pins no m15 input).
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34–M41
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s9 cell reads 2670. FULL unnamed TSV match
(all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv`; shape-9 row matches the pinned 15 cells +
standings + deltas exactly; pooled 22 extras + 8 missings
(row,col) sets equal M33's cluster sets exactly; all 30
pooled sites' (offset + |δ| + status + gaps + signs) match
M35 exactly; all 30 pooled sites Y-plane; big-5 seats
compatible with M35's per-cell band/dec distributions.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m42.py` invocation (the receipt, 9.0 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m42.py receipt | 9.0 s | exit 0; all guards pass; canon `d91493af…a70d86` |
| control.py C-BIG | <1 s | green; sets + J + values + listings + ranks exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 8.6 s |
| Task 1 (big-5 rows + ranks + headliner overlap) | 1 | <1 s |
| Task 2 (top listing + row geometry + seats) | 1 | <1 s |
| Determinism re-run (Task 1 on s0+9, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m42.py` wall | — | 9.0 s |

## Step 2 — estimates

### Task 1 — big-5 recompute (do the 5 sites reproduce?)

All 5 sites recomputed from the dumps (5/5 pins match M35
exactly — offsets, |δ| both frames, statuses, signed gaps both
frames, gap signs; gap-equal on (226,351) only):

| (r,c) | offset | plane | side | \|δ_own\| | other status | \|δ_other\| | g_own | g_other | sign | geq |
| --- | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- | --- |
| (305,332) | 391064 | Y | extra | 28 (s9) | noncell (s0) | n/a | −62 | −55 | −− | False |
| (241,318) | 309116 | Y | extra | 25 (s9) | bulk (s0) | 2 | 93 | 11 | ++ | False |
| (226,351) | 289982 | Y | extra | 19 (s9) | noncell (s0) | n/a | −39 | −39 | −− | True |
| (288,314) | 369268 | Y | miss | 45 (s0) | noncell (s9) | n/a | 107 | 84 | ++ | False |
| (289,314) | 370548 | Y | miss | 23 (s0) | noncell (s9) | n/a | 54 | 31 | ++ | False |

(Noncell 4/5; the bulk one is (241,318) with |δ_s0| 2.)

Rank table (competition rank = 1 + count strictly greater;
per side + pooled among 30):

| (r,c) | side | \|δ\| | side rank | pooled rank |
| --- | --- | ---: | --- | --- |
| (305,332) | extra | 28 | 1/22 | 2/30 |
| (241,318) | extra | 25 | 2/22 | 3/30 |
| (226,351) | extra | 19 | 3/22 | 5/30 |
| (288,314) | miss | 45 | 1/8 | 1/30 |
| (289,314) | miss | 23 | 2/8 | 4/30 |

(Pooled order top 5: (288,314):45 > (305,332):28 >
(241,318):25 > (289,314):23 > (226,351):19. 45 is the max;
19 is the 5th.)

Headliner-overlap table (headlined = c314/c315 per M35 §Task 1):

| (r,c) | cell | headlined |
| --- | ---: | --- |
| (305,332) | 332 | False |
| (241,318) | 318 | False |
| (226,351) | 351 | False |
| (288,314) | 314 | True |
| (289,314) | 314 | True |

(Overlap 2/5 in [314, 315] — both c314 missings; 0/5 in c315;
3/5 unheadlined: c332/c318/c351.)

### Task 2 — beyond the headliners (top-|δ| listing + seats)

Top-10 extras by |δ_9| (|δ| desc, offset asc) with
statuses/gaps/signs:

| rank | (r,c) | offset | \|δ_9\| | s0 status | \|δ_s0\| | g_9 | g_s0 | sign |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 1 | (305,332) | 391064 | 28 | noncell | n/a | −62 | −55 | −− |
| 2 | (241,318) | 309116 | 25 | bulk | 2 | 93 | 11 | ++ |
| 3 | (226,351) | 289982 | 19 | noncell | n/a | −39 | −39 | −− |
| 4 | (240,318) | 307836 | 16 | bulk | 1 | 34 | 5 | ++ |
| 5 | (289,315) | 370550 | 16 | noncell | n/a | −34 | 0 | −0 |
| 6 | (239,339) | 306598 | 15 | noncell | n/a | 39 | 35 | ++ |
| 7 | (233,327) | 298894 | 14 | bulk | 1 | 29 | 4 | ++ |
| 8 | (244,316) | 312952 | 14 | bulk | 1 | 59 | 7 | ++ |
| 9 | (243,318) | 311676 | 13 | bulk | 1 | 53 | 11 | ++ |
| 10 | (245,315) | 314230 | 13 | bulk | 2 | 60 | 6 | ++ |

(Near-big 16–18 in top 10: 2 — both 16, no 17/18. The
rank-4 16 sits in the same cell as the rank-2 25 (c318);
the rank-5 16 is the headlined c315's −0 site, static on s0.)

Top-8 missings by |δ_s0| (= all 8) with statuses/gaps/signs:

| rank | (r,c) | offset | \|δ_s0\| | s9 status | \|δ_9\| | g_s0 | g_9 | sign |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 1 | (288,314) | 369268 | 45 | noncell | n/a | 107 | 84 | ++ |
| 2 | (289,314) | 370548 | 23 | noncell | n/a | 54 | 31 | ++ |
| 3 | (269,314) | 344948 | 12 | noncell | n/a | 41 | 29 | ++ |
| 4 | (266,315) | 341110 | 10 | bulk | 2 | 64 | 46 | ++ |
| 5 | (273,315) | 350070 | 10 | bulk | 3 | 23 | 23 | ++ |
| 6 | (296,311) | 379502 | 10 | noncell | n/a | 24 | 7 | ++ |
| 7 | (299,312) | 383344 | 10 | bulk | 6 | 22 | 16 | ++ |
| 8 | (301,312) | 385904 | 9 | bulk | 7 | 28 | 28 | ++ |

(No missing-side site at 16–18; the missing side drops from
23 to 12. All 8 missings ++.)

Row geometry (own-frame row-list: extras s9, missings s0;
edge = min/max, singletons noted):

| (r,c) | side | s0 rows | s9 rows | own | pos | edge? |
| --- | --- | --- | --- | --- | --- | --- |
| (226,351) | extra | [] | [226] | [226] | singleton | True |
| (241,318) | extra | [] | [240,241,243] | [240,241,243] | interior | False |
| (288,314) | miss | [269,276,277,278,287,288,289] | [246,276,277,278,287] | [269,276,277,278,287,288,289] | interior | False |
| (289,314) | miss | [269,276,277,278,287,288,289] | [246,276,277,278,287] | [269,276,277,278,287,288,289] | max | True |
| (305,332) | extra | [295,304] | [295,304,305] | [295,304,305] | max | True |

(Edge 3/5: the c351 singleton, the c332 max, the c314-289 max;
interior 2/5: (241,318) mid-list, (288,314) second-max.)

Pairwise row distances (|r_i − r_j| over the 5 rows):

| pair | \|Δr\| |
| --- | ---: |
| (226,351)-(241,318) | 15 |
| (226,351)-(288,314) | 62 |
| (226,351)-(289,314) | 63 |
| (226,351)-(305,332) | 79 |
| (241,318)-(288,314) | 47 |
| (241,318)-(289,314) | 48 |
| (241,318)-(305,332) | 64 |
| (288,314)-(289,314) | 1 |
| (288,314)-(305,332) | 17 |
| (289,314)-(305,332) | 16 |

(The c314 big pair sits at row distance 1; all other pairs
read ≥15.)

Band/decile seats (s0-anchored: band = geometry thirds,
decile = P1 on s0 mid-Y):

| (r,c) | band | dec |
| --- | ---: | ---: |
| (226,351) | 1 | 9 |
| (241,318) | 1 | 9 |
| (288,314) | 1 | 9 |
| (289,314) | 1 | 9 |
| (305,332) | 2 | 9 |

(Seats 5/5 dec-9; bands 4×1 + 1×2 (c332). Compatible with
M35's per-cell distributions: c332 extra band 2 dec 9; c318
extras dec 8:1 9:2 with (241,318) one of the dec-9 pair;
c351 extra band 1 dec 9; c314 missings band 1,1,1 dec 9:3.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-BIG (known 5 priv + 5 miss) | priv 5 exact, miss 5 exact, J 97/107, values + gaps + standings exact, topx [16,14,12,10,8] ranks 1–5 exact, topm [47,46,45,17,16] ranks 1–5 exact, cell fixed, orig kept | exact | True |

(Priv pool: bulk-Y n=2319; greedy largest-first dv +16/+14/
+12 at (46,81)/(45,81)/(47,81) with orig |δ| 2/2/2, +10 at
(42,98) orig 1, +8 at (25,270) orig 1 — all + sign, no
fallback. Miss pool: tail-Y at |δ| 47/46/45/17/16 — first at
each value (26,296)/(28,301)/(27,340)/(23,257)/(23,277),
all +1 landings, 0 −1 fallbacks. Spanned Y cols
81/98/257/270/277/296/301/340 with per-cell standings
3×extra-only (81 d3, 98 d1, 270 d1) + 5×missing-only d1,
rows exact on all 8. Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+9: big-5 rows + ranks + headliner
overlap, fresh loads) pass1 `d91493af…a70d86` vs pass2
`d91493af…a70d86`, identical=True; 18/18 lines
match=True; sets identical=True (extras 22/22, missings 8/8,
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
| H1_BIG_REPRO | 5/5 big sites read the pins exactly | 5/5, geq on (226,351) only — met |
| H2_RANK | extras 28/25/19 rank 1/2/3; missings 45/23 rank 1/2; pooled 45>28>25>23>19 | (1,2)+(2,3)+(3,5)+(1,1)+(2,4) — met |
| H3_NONCELL | exactly 4/5 non-cell, bulk = (241,318) adO 2 | 4/5, bulk [(241,318)] — met |
| H4_NEARBIG | extras top-10 contains ≥1 site at 16–18 | 2 ([(240,318):16, (289,315):16]) — met |
| H5_ROWEDGE | big sites row-list-edge, share ≥ 0.50 | 3/5 = 0.6000 — met |
| H6_BANDSHARE | big sites band-1, share ≥ 0.50 | 4/5 = 0.8000 — met |
| H7_GAPSPLIT | both ++ and −− present among big-5 signs | [++,++,++,−−,−−] — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (5/5 pins exact — offsets, both-frame |δ|,
statuses, both-frame gaps, signs; gap-equal only on
(226,351) −39/−39), by rank (extra side 28/25/19 at 1/2/3
with pooled 2/3/5; missing side 45/23 at 1/2 with pooled
1/4 — no ties above 19), and by headliner overlap (2/5 in
c314, 0/5 in c315, 3/5 unheadlined). Task 2 discriminates by
top listing (extra top-10 runs 28/25/19/16/16/15/14/14/
13/13 with the near-big pair at ranks 4–5; missing top-8
runs 45/23 then 12/10/10/10/10/9 with a 23→12 gap), by row
position (3/5 edge incl. the c351 singleton vs 2/5 interior;
the c314 pair at distance 1 vs ≥15 elsewhere), by seats (5/5
dec-9 with the band-2 singleton at c332), and by gap signs
(3 ++ on the bulk extra + both missings vs 2 −− on the two
noncell extras).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; big-5 tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence big-|δ| map
(`m42-bigmap.png`, 88749 B of 5242880 budget) colors s0
tail-Y by shared (green 94) / rest-of-30 (yellow 23) /
near-big 16–18 (cyan 2) / big ≥19 (magenta 5); DESIGN.md
admits an evidence copy iff H1 meets AND H2 meets AND H4
meets — all three meet (5/5 + ranks exact + 2 near-big).

Recorded without verdict: s9's big-5 recompute to (305,332)
28 −−, (241,318) 25 ++ bulk-2, (226,351) 19 −− gap-equal,
(288,314) 45 ++, and (289,314) 23 ++, at side ranks
1/2/3 + 1/2 and pooled 45 > 28 > 25 > 23 > 19 with 2/5 in
c314; the extra top-10 reads two 16s below the big-3 with no
17/18 anywhere while missings drop 23→12; rows read 3/5 edge
with the c314 pair adjacent (distance 1) and all other pairs
≥15; seats read 5/5 dec-9 at bands 1/1/1/1/2; signs read
3 ++ / 2 −−; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| value/row suite + falsification bars, recorded before running | recorded | `DESIGN.md`: big-5 + rank + headliner tables, top-10 per side + row/seat tables, C-BIG control, bars H1–H7/N |
| big-5 + listing/seats + wall/exit/shas/determinism | measured | §Step 2: 5/5 sites + ranks + overlap + top-10/8 + rows + seats; 9.0 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a big-\|δ\| map discriminates (or absence reasoned) | measured | present by rule: H1 + H2 + H4; 88749 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m42"
cp local/research/M42/m42.py local/research/M42/control.py local/research/M42/DESIGN.md "/Volumes/Extreme SSD/m42/"
python3 m42.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m35/m35.txt" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m42" /Users/bradrichardson/dev/ssx3/local/research/M42 > m42.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m42/m42-bigmap.png" local/research/M42/m42-bigmap.png
```

## Paths

Evidence (committed): `local/research/M42/` — `DESIGN.md`
(suite + bars, recorded before running), `m42.py`
(big-5 + listing + rows + seats + PNG writer), `control.py`
(known-ranking control), `m42-bigmap.png` (big-|δ| map,
88749 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m42/` —
`m42.txt` (receipt: shas, baselines, guards, Task-1 big-5
tables, Task-2 listing/rows/seats, re-run, PNG size; 15075
B), `control.txt` (2274 B), `m42.py`, `control.py`,
`DESIGN.md` (working copies), `m42-bigmap.png` (working
copy, 88749 B). No writes into `m15/`, `m16/`, `m17/`,
`m18/`, `m19/`, `m20/`, `m21/`, `m22/`, `m23/`, `m24/`,
`m25/`, `m26/`, `m27/`, `m28/`, `m29/`, `m30/`, `m31/`,
`m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`, `m38/`,
`m39/`, `m40/`, `m41/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Adjacent-row big pair (new, minor): the c314 big missings
   (288,314) + (289,314) sit at row distance 1 — the only
   big-5 pair below 15 (next-smallest 15/16/17); one reads
   interior, one max. Needs its own brief only if
   adjacent-row big pairs matter: row-adjacency census of
   big-|δ| sites across all rows, offline — no new harness
   code.
2. Band-2 big singleton (new, minor): (305,332) is the only
   big-5 site in band 2 (4/5 band 1) and M35's only band-2
   extra among all 22 — also the pooled rank-2 site at 28.
   Needs its own brief only if big-site band seats matter:
   band-seat listing of top-|δ| sites per row, offline — no
   new harness code.
3. Near-big pair (new, minor): the only 16–18 sites among
   the 30 are the two extras at 16 — (240,318) bulk ++ in
   the big c318 cell vs (289,315) noncell −0 in the
   headlined c315 cell. Needs its own brief only if
   near-big values matter: value/row listing of |δ| 16–18
   sites across all rows, offline — no new harness code.
4. M41 gap 1 (still open, by reference): see M41 REPORT gap
   1 for the exact brief it needs (raw-8 noncell site).
5. M40 gaps 1–2 (still open, by reference): see M40 REPORT
   gaps 1–2 for the exact brief each needs (missing-side
   magnitude split; extra-side sign split).
6. M39 gaps 1–2 (still open, by reference): see M39 REPORT
   gaps 1–2 for the exact brief each needs (extra-side sign
   asymmetry; extra-side |δ| spread).
7. M38 gap 1 (still open, by reference): see M38 REPORT gap
   1 for the exact brief it needs ((278,314) diverge-by-2).
8. M37 gaps 1–2 (still open, by reference): see M37 REPORT
   gaps 1–2 for the exact brief each needs (s761's
   column-54 tail quartet; 701 mask column block 54–65).
9. M36 gaps 1–3 (still open, by reference): see M36 REPORT
   gaps 1–3 for the exact brief each needs (c54 carrier
   coincidence; shared-site triple; s3 all-delta-1 row).
10. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns; same-column opposite standings).
11. M33 gaps 1, 4–5 (still open, by reference): see M33
   REPORT gaps 1, 4–5 for the exact brief each needs
   (far/near private split; M29 gaps 5–11; M32 gap 1 + M31
   gap 2).

(M35 gaps 1–3 — worked in M40/M41/this brief at table level
above.)

## What I could not do

1. No per-site values beyond s9's pooled cells: δ values and
   gaps at other unnamed moved cells are M35's tables by
   reference (brief pins s9 big-5 + top listing only).
2. No rule for the adjacent-row big pair, the band-2
   singleton, or the near-big pair: all are attributed per
   site, no rule (gap rows 1–3).
3. No destination assignment for unnamed moves: row-lists
   are tabled without the M28-style displacement step
   (brief pins row-lists + values + seats only).
4. No explanation: values are attributed per site, no rule;
   0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M42/`: `DESIGN.md`, `m42.py`,
`control.py`, `m42-bigmap.png` (88749 B, rule-met),
`REPORT.md` (this file).
