# M48 — Shape-734 triple move: dest-row listing + value table: REPORT

M28 gap 4 (= M29 gap 7) worked at table level: 734's triple
move recomputes to tail 94, J 0.8846, moved [340,342,343] with
c340 0/0 + c343 0/0 (full wipe both) draining into c342 7/5
(+2 extras [26,33] on 5 kept rows) under the M28 rule (sole
≥2-site candidate; +2/+0.5/+2 and −1/+3.0/+0; FULL named +
unnamed TSVs byte-identical to `m28`/`m34-census.tsv` — stop
rule not triggered). The 10 wiped rows read 0/10 bulk on 734
(all non-cell, |δ_s0| med 37.5, ++×8 on c340 / −−×2 on c343);
the 2 dest extras read far-bulk on s0 (|δ| 21,11 vs 3,5,
−−×2, gaps −50,−26/−8,−13 — M29 reproduced); the 5 kept rows
read 5/5 tail-both (−−×5, 2/5 gap-equal). Counts close fully:
10 wiped vs +2 growth vs 5 kept with 0 privates outside c342
and 0 missings outside c340/c343. Fully offline — no lease of
any kind, no boots, no harness code, no `adb`. No device
work. Runbook `local/muse/prompts/M48.md`. Tables, no
verdicts.

Headers read first: `local/research/M28/REPORT.md` (all of it:
M28 gap 4 = this brief via M29 gap 7 — 734's c340 + c343 full
wipes with dest collision at c342; moved [340,342,343], c342
7/5 (+2) extra-only, displacement +2/+0.5/+2 and −1/+3.0/+0)
plus `local/research/M29/REPORT.md` (all of it: 734-c342 n/ov
7/5, rows [26,33], |δ| 21,11, gaps −50,−26/−8,−13, bulk ×2,
dec 9,9) plus `local/research/M34/REPORT.md` (all of it:
734's census row — NO unnamed moves; union-domain method).

Time box 4 hours (start 2026-09-20 06:41 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m47/` — all outputs went to the new
`/Volumes/Extreme SSD/m48/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m28-census.tsv` + `m34-census.tsv` (FULL TSV match targets).
Work dir `/Volumes/Extreme SSD/m48/`; evidence
`local/research/M48/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M47):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0734 | `82467b1f…4bddbb2` |
| m16-mid-s0734 | `45de5504…5977d26` |
| m16-full-s0734 | `f60ddd16…e038600f` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m28-census.tsv | `27872527…15a9e7f` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m48.txt` §inputs. Triplet fold sha over all
764×3 bins: `6c906897…61fd423b1` — matches M28/M34 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M47 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha matches M28/M34. δ==0 violations read 0
shapes. s0 cell 2475 + tail 102 (sub-bins 28+74, max 47) +
P(δ>0) 0.8093 match exactly; all 8 s0 named reference row
lists + guard-only c341 n=0 match exactly; UNNAMED domain 33
(41 union) + s0-bearing-13 row lists + c341-empty-on-764 match
exactly; FULL named TSV byte-identical (54296 B) + FULL
unnamed TSV byte-identical (163262 B); 734 row (tail 94, J
0.8846, moved [340,342,343], c340/c343 0/0, c342 7/5, no
unnamed moves) + displacement rows (+2/+0.5/+2, −1/+3.0/+0,
extra-only) + M29 dest values ([26,33], |δ| 21,11, bulk 3,5,
gaps −50,−26/−8,−13, offsets 33964/42924) all match exactly.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m48.py` invocation (the receipt, 3.9 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m48.py receipt | 3.9 s | exit 0; all guards pass; canon `d7f43602…031e3cd` |
| control.py C-COLLISION | <1 s | green; wipe + dest + values + collision exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 3.7 s |
| Task 1 (wipe + dest + displacement) | 1 | 0.0 s |
| Task 2 (wiped/dest values + collision) | 1 | 0.0 s |
| Determinism re-run (Task 1 on s0+734, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m48.py` wall | — | 3.9 s |

## Step 2 — estimates

### Task 1 — 734 wipe reproduction (do the 3 columns reproduce?)

734's row recomputed from the dumps (FULL TSV guards passed
first — both byte-identical): tail 94, J 0.8846, moved
[340,342,343] with all standings + no unnamed moves exact
(match=True throughout).

Wipe table (c340 + c343 — full wiped row lists):

| col | s0-rows | s734-rows | miss rows | n/ov |
| ---: | --- | --- | --- | --- |
| 340 | [24,25,26,27,31,32,33,34] | [] | [24,25,26,27,31,32,33,34] | 0/0 |
| 343 | [26,27] | [] | [26,27] | 0/0 |

Dest table (c342 — full row-list: kept + extras):

| col | s0-rows | s734-rows | kept | extra | n/ov |
| ---: | --- | --- | --- | --- | --- |
| 342 | [27,28,29,34,35] | [26,27,28,29,33,34,35] | [27,28,29,34,35] | [26,33] | 7/5 |

(Extras [26,33] reproduce M29 exactly. All 5 s0 rows kept.)

Displacement table (M28 rule rows reproduced — tabled, not
re-judged; 734's ≥2-site candidate set is the singleton
{(342,[26,33])}; 0 private U/V sites):

| move | dest | off | rshift | minshift | npriv | fresh? |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| c340→342 | 342 | +2 | +0.5 | +2 | 2 | no (named) |
| c343→342 | 342 | −1 | +3.0 | +0 | 2 | no (named) |
| c342→none | — | — | — | — | — | extra-only |

(All three rows match M28 exactly: offsets +2/−1, rshifts
+0.5/+3.0, minshifts +2/+0, prows [26,33] both.)

### Task 2 — full-set value table (wiped + dest + unnamed?)

734 full sets: priv 2, miss 10, shared 92, tail 94/102 (all
sites Y-plane). Unnamed: 734 moves 0 unnamed columns (FULL
unnamed TSV guard + umv734 == [] — M34 reproduced).

Wiped-value table (all 10: cell, offset, plane, row, col;
|δ_s0|; s734 status + |δ_734|; signed gaps s0 vs s734):

| cell | offset | plane | (r,c) | |δ_s0| | s734 status | |δ_734| | g_s0 | g_734 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 340 | 31400 | Y | (24,340) | 17 | noncell | n/a | 40 | 10 |
| 340 | 32680 | Y | (25,340) | 38 | noncell | n/a | 82 | 34 |
| 340 | 33960 | Y | (26,340) | 47 | noncell | n/a | 99 | 59 |
| 343 | 33966 | Y | (26,343) | 31 | noncell | n/a | −65 | −3 |
| 340 | 35240 | Y | (27,340) | 45 | noncell | n/a | 91 | 71 |
| 343 | 35246 | Y | (27,343) | 26 | noncell | n/a | −54 | −2 |
| 340 | 40360 | Y | (31,340) | 44 | noncell | n/a | 90 | 79 |
| 340 | 41640 | Y | (32,340) | 47 | noncell | n/a | 97 | 70 |
| 340 | 42920 | Y | (33,340) | 37 | noncell | n/a | 78 | 50 |
| 340 | 44200 | Y | (34,340) | 17 | noncell | n/a | 35 | 25 |

Wiped summaries: near 0 (0.0000), far 0 (0.0000), noncell 10
(1.0000); signed-gap equality 0/10, abs-gap equality 0/10;
gap signs ++×8 (all c340) + −−×2 (both c343), 0 mixed/zero;
|δ_s0| list [17,17,26,31,37,38,44,45,47,47], min 17, med
37.5, mean 34.9000, max 47 (= s0 tail max, at (26,340) and
(32,340)).

Dest-value table, extras (both M29 rows reproduced exactly):

| offset | plane | (r,c) | |δ_734| | s0 status | |δ_s0| | g_734 | g_s0 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| 33964 | Y | (26,342) | 21 | bulk | 3 | −50 | −8 |
| 42924 | Y | (33,342) | 11 | bulk | 5 | −26 | −13 |

Extra summaries: near 0, far 2 (bulk |δ| 3,5), noncell 0;
signed/abs-gap equality 0/2; gap signs −−×2; |δ_734|
list [11,21], med 16.0, mean 16.0000.

Dest-value table, kept rows (all 5 shared-tail in c342):

| offset | plane | (r,c) | |δ_734| | |δ_s0| | g_734 | g_s0 | sign |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 35244 | Y | (27,342) | 35 | 16 | −84 | −40 | −− |
| 36524 | Y | (28,342) | 32 | 27 | −79 | −63 | −− |
| 37804 | Y | (29,342) | 18 | 18 | −43 | −43 | −− |
| 44204 | Y | (34,342) | 19 | 16 | −47 | −39 | −− |
| 45484 | Y | (35,342) | 17 | 17 | −41 | −41 | −− |

Kept summaries: tail-both 5/5; gap signs −−×5; signed-gap
equality 2/5 (r29 −43/−43, r35 −41/−41), abs-gap equality
2/5; |δ_734| [17,18,19,32,35] med 19.0 mean 24.2000;
|δ_s0| [16,16,17,18,27] med 17.0 mean 18.8000.

Collision table (numbers only — no assignment of rows to
source columns):

| side | count |
| --- | ---: |
| wiped rows (c340 8 + c343 2) | 10 |
| dest growth (c342 extras) | +2 |
| dest kept rows | 5 |
| full priv / miss / shared | 2 / 10 / 92 |
| net tail delta (94−102) | −8 (= +2 − 10) |
| privates outside c342 | 0 |
| missings outside c340/c343 | 0 |

(Counts admit a full accounting: miss == wiped 10, priv ==
growth 2, outside 0.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-COLLISION (known 10-wipe + 2-dest) | wipe rows exact, dest rows exact, tail'=94, J 0.8846, both → dest col, dest \|δ'\|=8×2, wipe \|δ'\|=1×10, statuses + gaps exact, cell fixed | exact | True |

(Dest-col fallback, tabled per DESIGN: c342 holds <2 landable
bulk gap≥17 Y sites, so the shared dest landed in c54 rows
[143,144] (+8/−8); displacement reads c340→54 (off −286) +
c343→54 (off −289) — the KNOWN part (rows, values, shared
dest) recovers exactly. Wipe landings +1 ×10, 0 −1 fallbacks.
Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+734: wipe + dest + displacement rows
+ wiped/dest/kept value rows, fresh loads) pass1
`d7f43602…031e3cd` vs pass2 `d7f43602…031e3cd`,
identical=True; 41/41 lines match=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_WIPENEAR | wiped sites near-miss (\|δ_734\|∈{6,7}), share ≥ 0.50 | 0/10 = 0.0000 — not met |
| H2_WIPESET | wiped sites non-cell on 734, share ≥ 0.50 | 10/10 = 1.0000 — met |
| H3_DESTNEAR | dest extras near-miss (\|δ_s0\|∈{6,7}), share ≥ 0.50 | 0/2 = 0.0000 — not met |
| H4_WIPEGG | wiped sites ++ gap signs, share ≥ 0.50 | 8/10 = 0.8000 — met |
| H5_VALMED | median \|δ_s0\| wiped ≠ median \|δ_734\| dest-extra | 37.5 vs 16.0 — met (differs) |
| H6_COLLISION | both wiped cols assign to c342 | 342 + 342 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
row-list (10 wiped rows all in c340/c343 with 0 outside; all
5 s0 c342 rows kept with exactly [26,33] added), by
candidacy (singleton candidate set — the collision is
structural, both wipes see one dest), and by offset
asymmetry (+2 vs −1 into the same column). Task 2
discriminates by other-frame status (wiped 10/10 noncell vs
dest extras 2/2 far-bulk vs kept 5/5 tail-both), by gap sign
(wiped ++×8 on c340 vs −−×2 on c343; dest side −−×7 across
extras + kept), by |δ| level (wiped med 37.5 over 17–47 vs
extras med 16.0 over 11–21 vs kept meds 19.0/17.0), by gap
equality (0/10 wiped, 0/2 extras, 2/5 kept), and by
accounting closure (10/2/5 with 0 outside on either side).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; wipe + dest tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The collision map
(`m48-collision.png`, 323 B of 5242880 budget, 320x224 native:
x=col//2, y=row//2; green = 5 kept, red = 8 wiped c340,
magenta = 2 wiped c343, yellow = 2 dest extras; 6 pixels hold
>1 class, tabled in the receipt) is copied to evidence;
DESIGN.md admits an evidence copy iff H6 meets AND H2 meets —
H6 meets (342 + 342) with H2 at 10/10 noncell.

Recorded without verdict: 734's c340+c343 recompute to a pure
10-row wipe draining into c342's +2 extras on 5 kept rows
under the M28 rule (singleton candidate, +2/−1 offsets, no
unnamed moves); wiped rows read 10/10 noncell at med 37.5
with a ++/−− per-column split; dest extras read far-bulk
−−×2 reproducing M29; kept rows read tail-both −−×5 with
2/5 gap-equal; counts close fully with 0 outside sites; 0 B
explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| collision suite + falsification bars, recorded before running | recorded | `DESIGN.md`: M28-rule triple repro + M36-style values + kept-row rows + C-COLLISION control, bars H1–H6/N |
| wipe/dest + value tables + wall/exit/shas/determinism | measured | §Step 2: 10-row wipe + 7-row dest + 17-site values; 3.9 s; re-run identical |
| controls (known collision) | measured | §Step 2: C-COLLISION green — wipe + dest + values + collision exact |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a collision map discriminates (or absence reasoned) | measured | present by rule: H6 meets + H2 meets; 323 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m48"
cp local/research/M48/m48.py local/research/M48/control.py local/research/M48/DESIGN.md "/Volumes/Extreme SSD/m48/"
python3 m48.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28/m28-census.tsv" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m48" /Users/bradrichardson/dev/ssx3/local/research/M48 > m48.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m48/m48-collision.png" local/research/M48/m48-collision.png
```

## Paths

Evidence (committed): `local/research/M48/` — `DESIGN.md`
(suite + bars, recorded before running), `m48.py`
(triple repro + value tables + PNG writer), `control.py`
(known-collision control), `m48-collision.png` (collision
map, 323 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m48/` —
`m48.txt` (receipt: shas, baselines, guards, Task-1/2 tables,
re-run, PNG size), `control.txt`, `m48.py`, `control.py`,
`DESIGN.md` (working copies), `m48-collision.png` (working
copy). No writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`,
`m20/`, `m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`,
`m28/`, `m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`,
`m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`, `m43/`,
`m44/`, `m45/`, `m46/`, `m47/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Wipe-to-noncell mechanism (new): all 10 wiped rows read
   non-cell on 734 (g_734 ∈ {10,34,59,−3,71,−2,79,70,50,25})
   — why the rows left cell-7 is unattributed. Needs its own
   brief only if wipe mechanics matter: per-site v0/mid/full
   attribution for 734's full sets, offline — no new harness
   code.
2. Per-column gap-sign split (new): c340's 8 wipes read ++
   while c343's 2 wipes read −− — located, not attributed.
   Needs its own brief only if wipe structure matters: the
   same gap-sign split across the other full wipes (711's
   pair, 732's single), offline — no new harness code.
3. Kept-row value drift (new, minor): c342's 5 kept rows
   read tail-both but at different |δ| per frame (adQ med
   19.0 vs adO med 17.0; 2/5 gap-equal). Needs its own brief
   only if kept-row values matter: shared-site value
   comparison for 734's full shared set, offline — no new
   harness code.
4. Wipe-to-dest non-assignment (new): the 10 wiped rows vs
   the 2 dest rows are listed, not assigned to each other
   (brief pins list-don't-assign). Needs its own brief only
   if collision moves matter: row + value comparison per
   wiped row vs the dest rows, offline — no new harness
   code.
5. M47 gaps 1–3, 5–6 (still open, by reference): see M47
   REPORT gaps 1–3, 5–6 for the exact brief each needs
   (711 wipe-to-noncell mechanics; singleton-vs-wipe
   matching; far-pool status split; M46/M33/M35 refs).
6. Shape-732 c296→c298 move (M28 gap 5, still open, minor):
   the only full single-column wipe with a fresh dest
   (rshift −1.5). Needs its own brief only if single full
   moves matter: dest-row listing + value table for 732,
   offline — no new harness code.

(M28 gap 4 / M29 gap 7 — this brief — worked at table level
above. M47 gap 4 — the 734-c342 joint listing — is
superseded by this run's full 734 tables.)

## What I could not do

1. No assignment: wiped rows vs dest rows are tabled by
   count only (brief pins list-don't-assign; gap 4 tables
   the follow-up).
2. No P1/carrier joins: M29's dec 9,9 is cited, not
   recomputed (no gradient/carrier machinery in this
   estimator; brief pins rows + values only).
3. No byte-level work beyond 734's sets: other shapes'
   collisions stay located, not attributed (gaps 5–6 table
   the follow-ups by reference).
4. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M48/`: `DESIGN.md`, `m48.py`,
`control.py`, `m48-collision.png` (323 B), `REPORT.md` (this
file).
