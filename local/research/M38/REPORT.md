# M38 — Shared-site triple: cross-shape value/gap comparison: REPORT

M36 gap 2 worked at table level: the 3 shared missing sites
recompute to the M36-pinned offsets, |δ_s0|, s0 gaps,
per-shape statuses, and per-shape Q gaps exactly (34/34
pooled-site pins match — stop rule not triggered), with s700
holding (276,313) in tail (|δ_700| 8, gap 17 — the one
measured-not-pinned shared cell). Q gaps agree exactly on 2/3
sites (range 0 at (276,313) and (295,332)) and diverge by 2 at
(278,314) (s2's 40 vs s3/s700's 42 — H1 met); the shared
triple straddles the pooled-missing sign line (2 all-++ sites
+ 1 all-−− site — H2 met) with the pooled 7/10 ++ split
reproduced. Row 278 recurs once elsewhere (a c54 extra row);
rows 276/295 recur nowhere; columns 313/332 bear 2/3 other
pooled sites while 314 bears none. All 10 pooled missings read
noncell on their own shapes (H5 met); s700's c313 row-list
holds r276 in tail between r274/275 (H6 met). Fully offline —
no lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M38.md`. Tables, no
verdicts.

Headers read first: `local/research/M36/REPORT.md` (all of it:
gap 2 = this brief — the (278,314) + (295,332) missings on
all three shapes and the (276,313) missing on s2+s3, 3 sites
recurring across shapes with identical s0 values but
per-shape gaps; the pooled missings' 3 −− are the shared
(295,332) site on all three shapes; missings read 0/0/10 on
their own shapes) plus `local/research/M37/REPORT.md` (all of
it: the corrected pooled universe — 24 pooled extra sites =
c54's 10 + 14 others; M36's "23" matches no M36 extras
count, M37 §Brief-count note; use 14).

Time box 4 hours (start 2026-09-20 04:56 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`–`m37/` — all outputs went to the new
`/Volumes/Extreme SSD/m38/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only),
`m34-census.tsv` (FULL TSV guard), and `m36.txt` (the 3
shared sites + per-shape gaps to reproduce). Work dir
`/Volumes/Extreme SSD/m38/`; evidence `local/research/M38/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M37):

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

(Full hexes in `m38.txt` §inputs. `m34-census.tsv` 163262 B;
`m36.txt` 102945 B — both match M37's committed sizes.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M37 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34–M37
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s2/s3/s700 cell reads 2469/2484/2605 (M36's
measured values — equal, not just tabled); FULL unnamed TSV
match (all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv`; 2/3/700 rows match the pinned k 6/7/8 +
n/ov + standings + deltas exactly (§Task 1); pooled counts
read 5+4 / 4+3 / 15+3 exactly; all 34 pooled sites Y-plane;
all 3 shared sites + all 10 pooled missings + all 24 pooled
extras match M36's per-site pins exactly (§Task 1). Mismatch
rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m38.py` invocation (the receipt, 5.9 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m38.py receipt | 5.9 s | exit 0; all guards pass; canon `0ec5cee5…b0deb1e05c` |
| control.py C-SHARED | <1 s | green; sets + shared table + gaps exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 5.6 s |
| Task 1 (shared-site recompute, 3 sites × 3 shapes) | 3 | <1 s |
| Task 2 (recurrence + standing + s700c313) | 34 | <1 s |
| Determinism re-run (Task 1 on s0+2+3+700, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m38.py` wall | — | 5.9 s |

## Step 2 — estimates

### Task 1 — shared-site recompute (do the 3 sites reproduce?)

All 3 shared sites recomputed from the dumps (FULL TSV guard
passed first — all 764 rows byte-identical; 34/34 pooled-site
pins + 3/3 shared-shape sets match M36 exactly — offsets,
|δ_s0|, s0 gaps, per-shape statuses, |δ_Q| n/a, per-shape
gaps):

Per-site per-shape table ((r,c) × s2/s3/s700; s700 at
(276,313) measured, not pinned):

| site | shape | status | \|δ_s0\| | \|δ_Q\| | g_s0 | g_Q | sign |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| (276,313) | s2 | missing | 8 | n/a | 17 | 16 | ++ |
| (276,313) | s3 | missing | 8 | n/a | 17 | 16 | ++ |
| (276,313) | s700 | tail | 8 | 8 | 17 | 17 | ++ |
| (278,314) | s2 | missing | 20 | n/a | 42 | 40 | ++ |
| (278,314) | s3 | missing | 20 | n/a | 42 | 42 | ++ |
| (278,314) | s700 | missing | 20 | n/a | 42 | 42 | ++ |
| (295,332) | s2 | missing | 10 | n/a | −22 | −21 | −− |
| (295,332) | s3 | missing | 10 | n/a | −22 | −21 | −− |
| (295,332) | s700 | missing | 10 | n/a | −22 | −21 | −− |

(Offsets 353906/356468/378264, all Y-plane, all in T_0 —
exact. The s700-held (276,313) cell reads |δ_700| = 8 at the
tail boundary with gap 17, one above s2/s3's 16.)

Divergence table (per-site range of Q gaps across shapes —
numbers only):

| site | missing-shape gaps | range | all-3 gaps | all-3 range |
| --- | --- | ---: | --- | ---: |
| (276,313) | [16, 16] | 0 (agree) | [16, 16, 17] | 1 (diverge-by-1) |
| (278,314) | [40, 42, 42] | 2 (diverge-by-2) | [40, 42, 42] | 2 (diverge-by-2) |
| (295,332) | [−21, −21, −21] | 0 (agree) | [−21, −21, −21] | 0 (agree) |

Sign table (per-site signs vs the pooled-missing 7/10 ++
split, recomputed):

| site | per-shape signs | side |
| --- | --- | --- |
| (278,314) | ++/++/++ | ++ side (3/3) |
| (276,313) | ++/++ (+ s700 ++ in tail) | ++ side (2/2 missing) |
| (295,332) | −−/−−/−− | −− side (3/3 = the pooled 3 −−) |

(Pooled missings recomputed: ++=7 −−=3 over the 10 sites
(s2: 3 ++ / 1 −−; s3: 2 ++ / 1 −−; s700: 2 ++ / 1 −−) —
M36's 7/10 split exact. The non-shared missings read ++ on
both frames: s2 (299,312) 22/22, s700 (215,38) 25/23.)

### Task 2 — recurrence + standing context

Row recurrence (rows {276, 278, 295} at OTHER pooled sites):

| row | other pooled sites | n |
| ---: | --- | ---: |
| 276 | (none) | 0 |
| 278 | s700 extra (278,54) [c54 row] | 1 |
| 295 | (none) | 0 |

Column recurrence (cols {313, 314, 332} at OTHER pooled
sites):

| col | other pooled sites | n |
| ---: | --- | ---: |
| 313 | s2 extra (293,313), s700 extra (291,313) | 2 |
| 314 | (none) | 0 |
| 332 | s2 extra (296,332), s2 extra (297,332), s700 extra (296,332) | 3 |

(Unique (r,c) beyond the shared triple: rows [(278,54)];
columns [(291,313), (293,313), (296,332), (297,332)]. All
recurrences are extras; no other missing shares a shared row
or column. Column 314 is sterile beyond its shared site.)

Standing context (the 3 sites' noncell-Q standing vs the
pooled splits — both M36 splits reproduced):

| group | standing | reads |
| --- | --- | --- |
| shared (276,313) | s2/s3 missing-noncell, s700 tail | matches pins |
| shared (278,314) | missing-noncell on s2+s3+s700 | matches pins |
| shared (295,332) | missing-noncell on s2+s3+s700 | matches pins |
| pooled missings (10) | noncell on own Q | 10/10 (M36 0/0/10) |
| pooled extras (24) | bulk/noncell on s0 | 14/10 (M36 14/10) |

(Per-missing qstat rows, all `noncell` + `inmi=True`: s2
(276,313)/(278,314)/(295,332)/(299,312); s3
(276,313)/(278,314)/(295,332); s700
(215,38)/(278,314)/(295,332).)

s700-absent check (s700's row-list at c313 around r276):

s0 rows [274, 275, 276, 292]; s700 rows [274, 275, 276, 291,
292] — miss [], extra [291]. s700 holds r276 in tail; s2/s3
drop exactly that row (their c313 miss row is [276] per the
M36 pins).

| r | in T_0 | in T_700 | \|δ_700\| |
| ---: | --- | --- | ---: |
| 270 | 0 | 0 | 1 (bulk) |
| 271 | 0 | 0 | 1 (bulk) |
| 272 | 0 | 0 | n/a (noncell) |
| 273 | 0 | 0 | 6 (bulk) |
| 274 | 1 | 1 | 19 |
| 275 | 1 | 1 | 20 |
| 276 | 1 | 1 | 8 |
| 277–282 | 0 | 0 | n/a (noncell) |

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-SHARED (known 3 shared + 2B + 2C) | missB 5 exact, missC 5 exact, inter 3 exact, J 0.9510, per-site table + gaps exact, cell fixed, orig kept | exact | True |

(Shared pool: 102 tail-Y; injected 3 shared at
(23,257)/(23,277)/(23,301) + 2 B-only at (23,321)/(24,257) +
2 C-only at (24,277)/(24,296), all dv=+1 (|δ|=1 landings,
no −1 fallbacks). Privates 0/0 on both frames. Known gaps
36–66 recovered equal on all three frames at all 7 sites.
Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+2/3/700: per-site per-shape rows +
divergence + sign tables, fresh loads) pass1
`0ec5cee5…b0deb1e05c` vs pass2 `0ec5cee5…b0deb1e05c`,
identical=True; 26/26 lines match=True; s700 holds (276,313)
in tail on both passes.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_GAP_AGREE | ≥2/3 shared sites read gap-range 0 across missing shapes | ranges 0/2/0, 2 agree — met |
| H2_SHARED_SIGN_SPLIT | ≥1 shared site all-++ AND ≥1 all-−− | [278,276] ++ / [295] −− — met |
| H3_ROW_RECURRENCE | ≥1 of rows {276,278,295} at another pooled site | [278] — met |
| H4_COL_RECURRENCE | ≥1 of cols {313,314,332} bears another pooled site | [313,332] — met |
| H5_MISS_NONCELL | 10/10 pooled missings noncell on own Q | 10/10 — met |
| H6_S700_HOLDS | (276,313) reads tail on s700 | inT700 True — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (34/34 pooled-site pins + 3/3 shared-shape sets
exact — offsets, |δ|, statuses, gaps), by divergence (2
agree-0 sites vs 1 diverge-by-2 site, s2 the odd shape out at
(278,314)), by the measured s700-held cell ((276,313) tail
on s700 at |δ| 8 / gap 17 — the triple's only cross-shape
status split), and by sign side (2 ++ sites vs the 1 −− site
that carries the pooled missings' 3 −−). Task 2
discriminates by recurrence (row 278's single c54-extra echo
vs rows 276/295 recurring nowhere; columns 313/332 bearing
2/3 other extras vs column 314 sterile), by standing (shared
missings 8/8 noncell on their missing shapes against
pooled 10/10 noncell missings and 14/10 extras), and by
row-list (s700 holds r276 between r274/275 at |δ| 19/20/8
while s2/s3 drop it).

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

Screenshot: present by rule. The evidence shared-site map
(`m38-sharedmap.png`, 88749 B of 5242880 budget) colors
s700's shared tail green, pooled extras red, other pooled
missings magenta, and the shared triple by sign (++ yellow /
−− cyan); DESIGN.md admits an evidence copy iff H1 meets AND
H2 meets — both meet (2/3 agree-0; 2 ++ sites + 1 −− site).

Recorded without verdict: the 3 shared missings recompute to
M36's values exactly with Q gaps agreeing on 2/3 sites and
diverging by 2 at (278,314) (s2's 40 vs 42); s700 holds
(276,313) in tail at |δ| 8 / gap 17; the triple straddles
the missing sign line 2-to-1 with the pooled 7/10 ++ split
reproduced; row 278 echoes once as a c54 extra row while
rows 276/295 and column 314 recur nowhere and columns
313/332 bear 2/3 other extras; missings read 10/10 noncell
against extras at 14/10; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| shared-site suite + falsification bars, recorded before running | recorded | `DESIGN.md`: per-site per-shape tables, divergence + sign tables, row/col recurrence, standing context, s700c313 window, C-SHARED control, bars H1–H6/N |
| 3 shared sites + context + wall/exit/shas/determinism | measured | §Step 2: 34/34 pins exact + divergence + signs + recurrence + standings + window; 5.9 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a shared-site map discriminates (or absence reasoned) | measured | present by rule: H1 + H2; 88749 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m38"
cp local/research/M38/m38.py local/research/M38/control.py local/research/M38/DESIGN.md "/Volumes/Extreme SSD/m38/"
python3 m38.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m36/m36.txt" "/Volumes/Extreme SSD/m38" /Users/bradrichardson/dev/ssx3/local/research/M38 > m38.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m38/m38-sharedmap.png" local/research/M38/m38-sharedmap.png
```

## Paths

Evidence (committed): `local/research/M38/` — `DESIGN.md`
(suite + bars, recorded before running), `m38.py`
(shared-site recompute + recurrence + standing + s700c313 +
PNG writer), `control.py` (known-shared-sites control),
`m38-sharedmap.png` (shared-site map, 88749 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m38/` —
`m38.txt` (receipt: shas, baselines, guards, 34-site pins,
Task-1 shared tables, recurrence, standings, window,
re-run, PNG size), `control.txt`, `m38.py`, `control.py`,
`DESIGN.md` (working copies), `m38-sharedmap.png` (working
copy). No writes into `m15/`–`m37/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. (278,314) diverge-by-2 (new, minor): s2's gap 40 vs
   s3/s700's 42 is the only per-shape gap divergence among
   the shared triple (the other two sites agree exactly).
   Needs its own brief only if gap divergence matters:
   pooled gap-magnitude comparison per shape across all 34
   pooled sites (is s2 systematically low?), offline — no
   new harness code.
2. M37 gaps 1–2 (still open, by reference): see M37 REPORT
   gaps 1–2 for the exact brief each needs (s761's
   column-54 tail quartet; 701 mask column block 54–65).
3. M36 gaps 3–6 (still open, by reference): see M36 REPORT
   gaps 3–6 for the exact brief each needs (s3 all-delta-1
   row; M35 gaps 1–3; M34 gaps 3–4; M33 gaps 1, 4–5).
4. M35 gaps 1–3 (still open, by reference): see M35 REPORT
   gaps 1–3 for the exact brief each needs (per-cell
   standing asymmetry; near-miss triple; big-|δ| unnamed
   sites).
5. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns; same-column opposite standings).

(M36 gap 2 — this brief — worked at table level above.)

## What I could not do

1. No per-site values beyond the shared triple + pooled
   standing splits: δ values and gaps at other unnamed
   moved cells are M36's tables by reference (brief pins
   the shared triple + recurrence/standing context only).
2. No rule for s2's 40 vs 42 at (278,314): the divergence
   is attributed per shape per site, no rule (gap row 1).
3. No destination assignment for unnamed moves: row-deltas
   are tabled without the M28-style displacement step
   (brief pins values + context only).
4. No explanation: values are attributed per site per
   shape, no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M38/`: `DESIGN.md`, `m38.py`,
`control.py`, `m38-sharedmap.png` (88749 B, rule-met),
`REPORT.md` (this file).
