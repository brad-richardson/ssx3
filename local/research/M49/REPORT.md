# M49 — Shape-732 c296→c298 move: dest-row listing + value table: REPORT

M28 gap 5 (via M48 gap 6, taken on orchestrator judgment) worked
at table level: 732's c296 recomputes to a 0/0 full wipe of all
9 s0 rows with dest c298 at +2/−1.5/+2 fresh (FULL named TSV +
FULL unnamed TSV byte-identical to `m28`/`m34-census.tsv` —
stop rule not triggered); the 9 wiped sites read |δ_s0|
15–47 (med 35.0, all ++, all noncell on 732) against the 2
dest extras at |δ_732| 8/14 (−−, bulk — M44's values reproduced
exactly) over 4 kept rows (kept |δ| up on 2/4 rows, −−×4);
full-set accounting closes exactly (miss 9 = wiped 9, priv 2 =
growth 2, outside 0). Bars read H1 not / H2 met / H3 met / H4
not / H5 met / H6 met. Fully offline — no lease of any kind, no
boots, no harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M49.md`. Tables, no verdicts.

Headers read first: `local/research/M28/REPORT.md` (all of it:
gap 5 = this brief — 732 tail 95 J 0.8942 moved [296], c296
0/0 wipe → dest c298 +2/−1.5/+2 fresh, the only full
single-column wipe with a fresh dest) plus
`local/research/M44/REPORT.md` (all of it: 732's c298 dest
rows [26,27] over kept s0 rows [28,29,34,35] — must reproduce;
per-site dest + kept values) plus `local/research/M34/REPORT.md`
(all of it: 732's census row — unnamed moved [298] k=1 —
must reproduce).

Time box 4 hours (start 2026-09-20 06:48 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m48/` — all outputs went to the new
`/Volumes/Extreme SSD/m49/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m28-census.tsv` + `m34-census.tsv` (match targets). Work dir
`/Volumes/Extreme SSD/m49/`; evidence `local/research/M49/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M48; s732 prefixes match M44; TSV shas match M28/M34):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0732 | `581154c1…2b158343` |
| m16-mid-s0732 | `9d1e9e78…01277b69` |
| m16-full-s0732 | `edaf6fc9…1b77c3ff` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m28-census.tsv | `27872527…15a9e7f` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m49.txt` §inputs. `m28-census.tsv` 54296 B;
`m34-census.tsv` 163262 B — both match the committed sizes.
Triplet fold sha over all 764×3 bins:
`6c906897…61fd423b1` — matches M28/M34 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M48 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 reference
row lists + guard-only c341 n=0 match exactly. FULL named TSV
+ FULL unnamed TSV byte-identical (all 764 rows each);
UNNAMED == pinned 33 (41 union, 13 s0-bearing + 20
pure-private); c341 empty on all 764; recomputed named movers
match M28's 10 exactly. 732 row (tail 95, J 0.8942, named
moved [296] 0/0, unnamed moved [298] 6/4) + displacement row
(c296→c298 +2/−1.5/+2 fresh) + dest values ([26,27], |δ|
8/14, gaps −19,−33/−5,−17) match M28/M34/M44 exactly
(§Tasks 1–2). Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m49.py` invocation (the receipt, 3.9 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green after one tabled control-only
fix: a missing `__main__` guard printed nothing on the first
attempt — receipt estimator untouched).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m49.py receipt | 3.9 s | exit 0; all guards pass; canon `33a667ef…dd202b3f6` |
| control.py C-MOVE | <1 s | green; sets + rows + disp + values exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + census fields) | 764 | 3.7 s |
| TSV guards (named + unnamed recompute) | 764 | 0.0 s |
| Tasks 1–2 (row-lists + per-site values + accounting) | 1 | 0.0 s |
| Determinism re-run (Task 1 on s0+732, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m49.py` wall | — | 3.9 s |

## Step 2 — estimates

### Task 1 — 732 wipe + dest reproduction (do the columns reproduce?)

732's row recomputed from the dumps (FULL TSV guards passed
first — all 764 named + all 764 unnamed rows byte-identical):
tail 95, J 0.8942, named moved [296] (0/0), unnamed moved [298]
(6/4) — all exact.

Wipe table (c296 — full 9-row wipe):

| col | s0 rows | s732 rows | miss rows | n/ov |
| ---: | --- | --- | --- | --- |
| 296 | [24,25,26,27,28,31,32,33,34] | [] | [24,25,26,27,28,31,32,33,34] | 0/0 |

Dest table (c298 — 4 kept + 2 extras):

| col | s0 rows | s732 rows | kept | extra | n/ov |
| ---: | --- | --- | --- | --- | --- |
| 298 | [28,29,34,35] | [26,27,28,29,34,35] | [28,29,34,35] | [26,27] | 6/4 |

Displacement table (M28 rule row — tabled, not re-judged):

| Shape | miss col | dest | off | rshift | minshift | standing |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 732 | 296 | 298 | +2 | −1.5 | +2 | fresh |

(732's private Y-cols read exactly [(298, [26,27])] — the sole
≥2-site candidate; private U/V sites 0. c298 reads extra-only
on 732 (miss==0).)

### Task 2 — full-set value table (wiped + dest + unnamed?)

Unnamed 732 moves per M34: [298] only (k=1, extra-only) — the
dest column itself; no other unnamed 732 moves exist.

Wiped-value table (all 9: |δ_s0|; s732 status + |δ_732|; signed
gaps s0 vs s732 — the new data):

| offset | plane | (r,c) | \|δ_s0\| | s732 status | \|δ_732\| | g_s0 | g_732 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 31312 | Y | (24,296) | 21 | noncell | n/a | 46 | 5 |
| 32592 | Y | (25,296) | 41 | noncell | n/a | 93 | 19 |
| 33872 | Y | (26,296) | 47 | noncell | n/a | 104 | 28 |
| 35152 | Y | (27,296) | 35 | noncell | n/a | 75 | 28 |
| 36432 | Y | (28,296) | 19 | noncell | n/a | 40 | 28 |
| 40272 | Y | (31,296) | 31 | noncell | n/a | 67 | 31 |
| 41552 | Y | (32,296) | 46 | noncell | n/a | 101 | 32 |
| 42832 | Y | (33,296) | 39 | noncell | n/a | 87 | 26 |
| 44112 | Y | (34,296) | 15 | noncell | n/a | 33 | 13 |

(Wiped |δ_s0| list [15,19,21,31,35,39,41,46,47]: min 15, med
35.0, mean 32.6667, max 47. Gap signs: ++×9. Signed-gap
equality 0/9.)

Dest-value table, extras (both — M44's 8/14 + bulk 1/6 +
gaps −19,−33/−5,−17 reproduced exactly):

| offset | plane | (r,c) | \|δ_732\| | s0 status | \|δ_s0\| | g_732 | g_s0 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 33876 | Y | (26,298) | 8 | bulk | 1 | −19 | −5 |
| 35156 | Y | (27,298) | 14 | bulk | 6 | −33 | −17 |

(Extras |δ_732| list [8,14]: med 11.0, mean 11.0000. Near/far/
noncell on s0: 1/1/0. Gap signs: −−×2. Signed-gap equality
0/2.)

Dest-value table, kept rows (all 4: both-frame |δ| + gaps,
tail on both — M44's kept values reproduced exactly):

| offset | plane | (r,c) | \|δ_s0\| | \|δ_732\| | g_s0 | g_732 |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 36436 | Y | (28,298) | 11 | 14 | −26 | −32 |
| 37716 | Y | (29,298) | 8 | 8 | −18 | −18 |
| 44116 | Y | (34,298) | 13 | 14 | −28 | −32 |
| 45396 | Y | (35,298) | 13 | 13 | −28 | −28 |

(Kept tail-on-both 4/4. Kept |δ| on s0 [8,11,13,13] med 12.0;
on 732 [8,13,14,14] med 13.5. Gap signs −−×4. Signed-gap
equality 2/4 — (29,298) −18/−18 and (35,298) −28/−28.)

Wipe-vs-dest comparison (numbers only):

| Set | \|δ\| list | med | mean | bulk/noncell (other) | gap signs |
| --- | --- | ---: | ---: | --- | --- |
| wiped (on s0) | [15,19,21,31,35,39,41,46,47] | 35.0 | 32.6667 | 0/9 on 732 | ++=9 |
| grown (on 732) | [8,14] | 11.0 | 11.0000 | 2/0 on s0 (1 near, 1 far) | −−=2 |
| kept (on s0) | [8,11,13,13] | 12.0 | 11.2500 | 4/0 tail both | −−=4 |
| kept (on 732) | [8,13,14,14] | 13.5 | 12.2500 | 4/0 tail both | −−=4 |

Accounting table (numbers only — no assignment of wiped rows
to dest rows):

| Quantity | n |
| --- | ---: |
| wiped rows (c296) | 9 |
| dest growth (c298 extras) | +2 |
| kept rows (c298) | 4 |
| full privates | 2 |
| full missings | 9 |
| full shared | 93 |
| tail 732 / tail s0 | 95 / 102 |
| net tail delta (growth−wiped) | −7 |
| privates outside c298 | 0 |
| missings outside c296 | 0 |
| miss==wiped / priv==growth / outside==0 | 9==9 / 2==2 / 0==0 |

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-MOVE (known 9 wipe + 2 dest) | wipe [] exact, dest +2 exact, tail' 95, J 93/104=0.8942, disp → dest, \|δ'\| 8×2 + 1×9, bulk 2/9, gaps 11/11 | exact | True |

(One tabled control-only deviation from the DESIGN pin,
receipt estimator untouched: as-pinned c298 holds <2 landable
bulk gap≥17 sites, so the run uses the DESIGN fallback — first
offset-order column with ≥2, c54 rows [143,144] — per the M29
C-PART-EXTRA precedent. Wipe landings +1 ×9, 0 −1 fallbacks;
dest landings +8/−8. Cell-7 mask fixed. Full rows in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+732: wipe + dest + displacement rows +
wiped/dest/kept value rows, fresh loads) pass1
`33a667ef…dd202b3f6` vs pass2 `33a667ef…dd202b3f6`,
identical=True; 37/37 lines match=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_WIPENEAR | wiped s732-bulk near, share ≥ 0.50 | 0/9 = 0.0000 — not met |
| H2_WIPESET | wiped noncell on 732, share ≥ 0.50 | 9/9 = 1.0000 — met |
| H3_DESTNEAR | dest-extra s0-bulk near, share ≥ 0.50 | 1/2 = 0.5000 — met |
| H4_WIPEMM | wiped −−, share ≥ 0.50 | 0/9 = 0.0000 — not met |
| H5_VALMED | wiped \|δ\| med ≠ dest-extra \|δ\| med | 35.0 vs 11.0 — met |
| H6_FRESHDEST | c296 assigns to c298 (+2, fresh) | 298/+2/fresh — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
row-list (c296 wipes all 9 s0 rows while c298 keeps all 4 and
grows exactly [26,27]), by census row (named [296] 0/0 +
unnamed [298] 6/4 — the only shape pairing a full named wipe
with its own unnamed growth), and by displacement (the sole
−1.5 rshift over the only ≥2-site candidate). Task 2
discriminates by other-frame status (wiped 9/9 noncell on 732
while grown 2/2 bulk on s0), by gap sign (wiped ++×9 vs grown
−−×2 vs kept −−×4), by |δ| (wiped 15–47 med 35.0 vs grown
8/14 med 11.0 vs kept 8–14), and by accounting (miss 9 =
wiped 9, priv 2 = growth 2, outside 0 — the full priv/miss
sets sit exactly in the two columns).

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

Screenshot: present by rule. The evidence move map
(`m49-movemap.png`, 320 B of 5242880 budget) marks kept c298
green / wiped c296 red / dest extras yellow at x=col//2
y=row//2; DESIGN.md admits an evidence copy iff H6 meets AND
H2 meets — both meet (fresh dest + 9/9 set change). Pixel
overlaps read 6 same-class pairs only (downsampling doubles —
no cross-class overlap).

Recorded without verdict: c296 reads a full 9-row wipe (|δ|
15–47, ++×9, all noncell on 732) against +2 growth at rows
[26,27] (|δ| 8/14, −−×2, both bulk) over 4 kept rows (−−×4,
kept |δ| up on 2/4); full accounting closes (9/2/0); H2/H3/H5/
H6 meet while H1/H4 do not; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| single-move suite + falsification bars, recorded before running | recorded | `DESIGN.md`: c296/c298 row-lists + M36-style per-site rows + kept-row values + accounting, C-MOVE control, bars H1–H6/N |
| 732 wipe + dest reproduction + wall/exit/shas/determinism | measured | §Task 1: 0/0 wipe + 6/4 dest + M28 row; 3.9 s; re-run identical |
| full-set value table (wiped + dest + unnamed?) | measured | §Task 2: 9 wiped + 2 grown + 4 kept per-site rows + comparison + accounting |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a move map discriminates (or absence reasoned) | measured | present by rule: H6 + H2 meet; 320 B |
| controls (known single move, rows + values exact) | measured | §Controls: C-MOVE exact; 1 control-only deviation tabled (c54 fallback) |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single green invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m49"
cp local/research/M49/m49.py local/research/M49/control.py local/research/M49/DESIGN.md "/Volumes/Extreme SSD/m49/"
python3 m49.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28/m28-census.tsv" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m49" /Users/bradrichardson/dev/ssx3/local/research/M49 > m49.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m49/m49-movemap.png" local/research/M49/m49-movemap.png
```

## Paths

Evidence (committed): `local/research/M49/` — `DESIGN.md`
(suite + bars, recorded before running), `m49.py`
(row-lists + per-site values + accounting + PNG writer),
`control.py` (known-single-move control), `m49-movemap.png`
(move map, 320 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m49/` —
`m49.txt` (receipt: shas, baselines, guards, Task-1/2 tables,
accounting, re-run, PNG size), `control.txt`, `m49.py`,
`control.py`, `DESIGN.md` (working copies),
`m49-movemap.png` (working copy, 320 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`, `m22/`,
`m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`, `m30/`,
`m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`, `m38/`,
`m39/`, `m40/`, `m41/`, `m42/`, `m43/`, `m44/`, `m45/`, `m46/`,
`m47/`, `m48/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Wiped-vs-dest value populations (new): c296 wiped |δ|
   15–47 (med 35.0, all ++) vs dest extras 8/14 (med 11.0,
   −−) — two non-overlapping value populations. Needs its
   own brief only if wipe-vs-dest magnitudes matter:
   cross-shape wiped-vs-grown |δ| comparison, offline — no
   new harness code.
2. Wiped-gap ++ vs dest/kept −− (new): all 9 wiped sites read
   ++ while all 6 dest + kept sites read −−. Needs its own
   brief only if gap-sign splits matter: gap-sign census at
   wipe/dest/kept sites, offline — no new harness code.
3. Earlier gaps (still open, by reference): see the M28–M48
   REPORT gap rows for the exact brief each needs (M28 gap 5
   — this brief — worked at table level above).

## What I could not do

1. Control dest column fell back to c54: as-pinned c298 holds
   <2 landable bulk gap≥17 Y sites — ran the DESIGN fallback
   (first offset-order column with ≥2) with the fallback
   tabled (C-MOVE still green).
2. No position joins: band/decile/streak/carrier attribution
   is out of scope (brief pins row-lists + per-site values
   only).
3. No wiped-to-dest assignment: wiped rows are listed, not
   assigned to dest rows (brief pins listing only).
4. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M49/`: `DESIGN.md`, `m49.py`,
`control.py`, `m49-movemap.png` (320 B), `REPORT.md` (this
file).
