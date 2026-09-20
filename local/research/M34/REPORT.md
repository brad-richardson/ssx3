# M34 — Unnamed-column partial scan: which shapes move unnamed columns: REPORT

M33 gap 2 (= M29 gap 3) worked at table level: union tail-Y
columns over all 764 read 41, so UNNAMED reads 33 (13
s0-bearing + 20 pure-private — the brief's "(hundreds)" reads
33, tabled below); 33/764 shapes move ≥1 unnamed column (79
moved cells: 21 missing-only / 50 extra-only / 8 mixed; delta
hist 1:55 2:10 3:5 4:3 5:1 9:3 10:2, med 1.0); named∩unnamed
reads 6/4/27/727; below-0.95 join reads 7/26/2/729 with 2/3/700
all moving unnamed (k 6/7/8); 709-c298 recomputes to a 0/0
wipe (delta 4) with 9/79 cells match-or-exceed. Named census
TSV (all 764 rows) + 709-c298 rows match M28/M29 exactly
(stop rule not triggered). Fully offline — no lease of any
kind, no boots, no harness code, no `adb`. No device work.
Runbook `local/muse/prompts/M34.md`. Tables, no verdicts.

Headers read first: `local/research/M33/REPORT.md` (all of it:
gap 2 = this brief — 709's c298 holds 4 missing rows
(r28/29/34/35), a second partial column on 709 outside the
census 8, located in M29 but never scanned for across the
764) plus `local/research/M28/REPORT.md` (all of it: the
exact-match census method generalized here — per-shape x
per-column presence with row overlap; 10 movers / 15 cells;
below-0.95 9-list) plus `local/research/M29/REPORT.md`
(§Task 1: 709 tail 97 J 0.9510 = 0 priv + 5 miss + 97 shared
with outside-col miss 4 = c298 r28/29/34/35).

Time box 4 hours (start 2026-09-20 04:09 EDT); used about 0.3.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m33/` — all outputs went to the new
`/Volumes/Extreme SSD/m34/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m28.txt` + `m28-census.tsv` (match targets). Work dir
`/Volumes/Extreme SSD/m34/`; evidence `local/research/M34/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M33; 709 prefixes match M29):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0709 | `6b776020…85fb471f` |
| m16-mid-s0709 | `bb35990e…2dcdac9f` |
| m16-full-s0709 | `6d1e6b6d…00cb5a1` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m28.txt | `87a12157…398faf25` |
| m28-census.tsv | `27872527…15a9e7f` |

(Full hexes in `m34.txt` §inputs. Triplet fold sha over all
764×3 bins: `6c906897…61fd423b1` — matches M28's fold exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M33 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 named
reference row lists + guard-only c341 n=0 match exactly. FULL
named TSV match (all 764 rows: tail + J4 + all-8-column
n/ov/pres) vs `m28-census.tsv`; named mover list matches
M28's 10 exactly. 709-c298 missing rows match M29's
[28,29,34,35] exactly (s0 c298 n=4 rows [28,29,34,35]; 709
c298 n=0). Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m34.py` invocation (the receipt, 6.2 s, exit 0 — a first
attempt died at import on a quote typo, fixed before any
receipt run started, no measurements taken); one `control.py`
invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m34.py receipt | 6.2 s | exit 0; all guards pass; canon `9d98af67…cea0162b` |
| control.py U1–U4 | <1 s | green; census + row-deltas exact on all 4 |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 6.0 s |
| Task 1 (census matrix + movers + top-20 + delta) | 764 | 0.0 s |
| Task 2 (joins + seed rank) | 764 | 0.0 s |
| Determinism re-run (Task 1 on s0+709, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m34.py` wall | — | 6.2 s |

## Step 2 — estimates

### Task 1 — unnamed-column scan (all columns, all shapes)

UNNAMED domain (DESIGN-pinned union rule): 41 union tail-Y
columns over all 764 minus the named 8 = 33 unnamed columns
(the brief's "(hundreds)" reads 33 — the tail-Y column space
is 41 wide, tabled as measured). c341 bears tail on no shape
(stays empty across all 764).

s0-bearing unnamed (n0>0): 13 columns, 37 sites (= s0's 37
other-tail sites ✓):

| col | n0 | rows |
| ---: | ---: | --- |
| 38 | 1 | [215] |
| 292 | 1 | [400] |
| 293 | 1 | [405] |
| 298 | 4 | [28,29,34,35] |
| 307 | 1 | [404] |
| 311 | 4 | [296,297,298,299] |
| 312 | 3 | [299,300,301] |
| 313 | 4 | [274,275,276,292] |
| 314 | 7 | [269,276,277,278,287,288,289] |
| 315 | 7 | [266,267,268,273,274,275,276] |
| 316 | 1 | [264] |
| 332 | 2 | [295,304] |
| 372 | 1 | [221] |

Pure-private unnamed (n0==0): 20 columns —
[54,145,259,279,295,299,303,310,318,322,323,327,328,336,337,
339,351,602,611,620].

Census matrix: all 764 × 33 with n/ov/present per column —
committed as `m34-census.tsv` (764 rows + header, 163262 B;
columns shape, tail_n, J_vs_s0, then n/ov/pres per unnamed
column in fixed ascending order). 731 shapes read present on
all 33.

Unnamed-mover census (shapes moving ≥1 unnamed column): 33
shapes, 79 moved cells (k-hist 1:18 2:9 3:1 4:1 6:1 7:1 8:1
15:1):

| Shape | tail | J vs s0 | k | moved set |
| ---: | ---: | ---: | ---: | --- |
| 1 | 104 | 0.9619 | 3 | [313, 332, 339] |
| 2 | 103 | 0.9159 | 6 | [311, 312, 313, 314, 332, 339] |
| 3 | 103 | 0.9340 | 7 | [311, 313, 314, 316, 332, 336, 339] |
| 5 | 103 | 0.9903 | 1 | [336] |
| 6 | 104 | 0.9619 | 4 | [318, 328, 332, 336] |
| 9 | 117 | 0.7520 | 15 | [310–316, 318, 322, 327, 332, 336, 337, 339, 351] |
| 19 | 100 | 0.9804 | 2 | [292, 293] |
| 21 | 106 | 0.9623 | 2 | [295, 307] |
| 22 | 106 | 0.9623 | 2 | [295, 307] |
| 27 | 100 | 0.9804 | 2 | [292, 293] |
| 284 | 101 | 0.9902 | 1 | [372] |
| 346 | 103 | 0.9903 | 1 | [602] |
| 366 | 105 | 0.9714 | 1 | [145] |
| 368 | 100 | 0.9804 | 2 | [292, 307] |
| 380 | 103 | 0.9903 | 1 | [311] |
| 381 | 103 | 0.9903 | 1 | [311] |
| 382 | 103 | 0.9903 | 1 | [311] |
| 383 | 103 | 0.9903 | 1 | [311] |
| 384 | 103 | 0.9903 | 1 | [311] |
| 386 | 103 | 0.9903 | 1 | [311] |
| 387 | 103 | 0.9903 | 1 | [311] |
| 389 | 103 | 0.9903 | 1 | [311] |
| 394 | 101 | 0.9902 | 1 | [313] |
| 411 | 104 | 0.9808 | 2 | [611, 620] |
| 579 | 101 | 0.9902 | 1 | [307] |
| 694 | 100 | 0.9612 | 2 | [332, 372] |
| 700 | 114 | 0.8462 | 8 | [38, 54, 299, 311, 313, 314, 332, 620] |
| 709 | 97 | 0.9510 | 1 | [298] |
| 731 | 100 | 0.6833 | 2 | [259, 279] |
| 732 | 95 | 0.8942 | 1 | [298] |
| 733 | 100 | 0.6694 | 2 | [303, 323] |
| 737 | 101 | 0.9902 | 1 | [38] |
| 761 | 106 | 0.9623 | 1 | [54] |

(Shape 9's 15: [310, 311, 312, 313, 314, 315, 316, 318, 322,
327, 332, 336, 337, 339, 351].)

Per-column mover counts (all 33 unnamed columns move on ≥1
shape; top-20 by mover count):

| col | movers | rate | n0 | miss-only | extra-only | mixed |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 311 | 12 | 0.0157 | 4 | 1 | 11 | 0 |
| 332 | 7 | 0.0092 | 2 | 2 | 2 | 3 |
| 313 | 6 | 0.0079 | 4 | 2 | 2 | 2 |
| 307 | 4 | 0.0052 | 1 | 2 | 2 | 0 |
| 314 | 4 | 0.0052 | 7 | 3 | 0 | 1 |
| 336 | 4 | 0.0052 | 0 | 0 | 4 | 0 |
| 339 | 4 | 0.0052 | 0 | 0 | 4 | 0 |
| 292 | 3 | 0.0039 | 1 | 3 | 0 | 0 |
| 38 | 2 | 0.0026 | 1 | 2 | 0 | 0 |
| 54 | 2 | 0.0026 | 0 | 0 | 2 | 0 |
| 293 | 2 | 0.0026 | 1 | 2 | 0 | 0 |
| 295 | 2 | 0.0026 | 0 | 0 | 2 | 0 |
| 298 | 2 | 0.0026 | 4 | 1 | 1 | 0 |
| 312 | 2 | 0.0026 | 3 | 1 | 0 | 1 |
| 316 | 2 | 0.0026 | 1 | 0 | 2 | 0 |
| 318 | 2 | 0.0026 | 0 | 0 | 2 | 0 |
| 372 | 2 | 0.0026 | 1 | 2 | 0 | 0 |
| 620 | 2 | 0.0026 | 0 | 0 | 2 | 0 |
| 145 | 1 | 0.0013 | 0 | 0 | 1 | 0 |
| 259 | 1 | 0.0013 | 0 | 0 | 1 | 0 |

(Remaining 13 singleton-mover cols: 279, 299, 303, 310, 315,
322, 323, 327, 328, 337, 351, 602, 611 — each movers=1.)

Row-delta distribution over all 79 unnamed moved cells
(delta = miss + extra; c298's seed delta wants 4):

| delta | n |
| ---: | ---: |
| 1 | 55 |
| 2 | 10 |
| 3 | 5 |
| 4 | 3 |
| 5 | 1 |
| 9 | 3 |
| 10 | 2 |

Summary: min 1, med 1.0, mean 1.9494, max 10. delta≤2: 65/79.
ov==0: 43/79. Standings: missing-only 21, extra-only 50,
mixed 8; full wipes 12; fresh-column (n0==0) moves 30; n0>0
moves 49 vs n0==0 moves 30.

Big-delta cells (delta ≥ 4, all 9 incl. the seed — derived
read-only from the committed TSV; hist matches the receipt
exactly):

| Shape | col | n/ov | miss/extra | delta |
| ---: | ---: | --- | --- | ---: |
| 700 | 54 | 10/0 | 0/10 | 10 |
| 733 | 323 | 10/0 | 0/10 | 10 |
| 731 | 259 | 9/0 | 0/9 | 9 |
| 731 | 279 | 9/0 | 0/9 | 9 |
| 733 | 303 | 9/0 | 0/9 | 9 |
| 9 | 315 | 8/5 | 2/3 | 5 |
| 9 | 314 | 5/4 | 3/1 | 4 |
| 709 | 298 | 0/0 | 4/0 | 4 (seed) |
| 761 | 54 | 4/0 | 0/4 | 4 |

(731's [259, 279] and 733's [303, 323] unnamed moves are
their M27/M28 named-swap destinations; 732's [298] is its
M28 c296→c298 dest, reading extra-only here.)

### Task 2 — joins (named vs unnamed vs Jaccard)

Named∩unnamed 2×2 (named movers = M28's 10):

|  | unnamed mover | unnamed still |
| --- | --- | --- |
| named mover | 6: 9, 22, 709, 731, 732, 733 | 4: 708, 710, 711, 734 |
| named still | 27: 1, 2, 3, 5, 6, 19, 21, 27, 284, 346, 366, 368, 380, 381, 382, 383, 384, 386, 387, 389, 394, 411, 579, 694, 700, 737, 761 | 727 |

Below-0.95 join (recomputed below set matches the M28 9-list
exactly — tail + J4 on all 9; guard OK):

| Shape | tail | J vs s0 | unnamed? |
| ---: | ---: | ---: | --- |
| 2 | 103 | 0.9159 | yes (k=6) |
| 3 | 103 | 0.9340 | yes (k=7) |
| 9 | 117 | 0.7520 | yes (k=15) |
| 700 | 114 | 0.8462 | yes (k=8) |
| 711 | 95 | 0.9314 | no |
| 731 | 100 | 0.6833 | yes (k=2) |
| 732 | 95 | 0.8942 | yes (k=1) |
| 733 | 100 | 0.6694 | yes (k=2) |
| 734 | 94 | 0.8846 | no |

2×2 (unnamed-mover × below-0.95):

|  | below-0.95 | above-0.95 |
| --- | --- | --- |
| unnamed mover | 7: 2, 3, 9, 700, 731, 732, 733 | 26 (list in receipt) |
| unnamed still | 2: 711, 734 | 729 |

Named-still+below rows (M28's below-but-still shapes — all
three move unnamed columns):

| Shape | tail | J vs s0 | k | unnamed cols |
| ---: | ---: | ---: | ---: | --- |
| 2 | 103 | 0.9159 | 6 | [311, 312, 313, 314, 332, 339] |
| 3 | 103 | 0.9340 | 7 | [311, 313, 314, 316, 332, 336, 339] |
| 700 | 114 | 0.8462 | 8 | [38, 54, 299, 311, 313, 314, 332, 620] |

(The 2 still+below shapes 711/734 are both named movers, so
9/9 below-0.95 shapes move ≥1 of the 41 union tail-Y columns:
7 unnamed + 2 named-only.)

709-c298 row (the seed): n=0 ov=0 miss=4 extra=0 delta=4 (a
full wipe of s0's 4-row column). Rank over the 79 unnamed
moved cells: delta>4: 6, ==4: 3, ≥4 (match-or-exceed): 9
(seed included); seed delta 4 ≥ median 1.0.

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| U1 (c298 drop 28,29) | moved [298], 2/2 miss-only d2 | exact | True |
| U2 (fresh col 0 +100,101) | moved [0], 2/0 extra-only d2 | exact | True |
| U3 (wipe col 38, n0=1) | moved [38], 0/0 wipe d1 | exact | True |
| U4 (col 314 mixed −269/+0) | moved [314], 7/6 mixed d2 | exact | True |

(All 4: moved-sets + per-column n/ov/pres + row-deltas +
standings exact; non-moved universe cols all present. Full
rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+709: full unnamed census rows +
deltas + J) pass1 `9d98af67…cea0162b` vs pass2
`9d98af67…cea0162b`, identical=True; 4/4 lines match=True;
sets identical=True (s0 [], 709 [298]).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_NAMEDINUNNAMED | named movers moving ≥1 unnamed, share ≥ 0.50 | 6/10 = 0.6000 — met |
| H2_STILLMOVE | unnamed movers named-still, share ≥ 0.50 | 27/33 = 0.8182 — met |
| H3_SMALLDELTA | unnamed moved cells delta≤2, share ≥ 0.50 | 65/79 = 0.8228 — met |
| H4_WIPE | unnamed moved cells ov==0, share ≥ 0.50 | 43/79 = 0.5443 — met |
| H5_BELOW95 | unnamed movers below-0.95, share ≥ 0.50 | 7/33 = 0.2121 — not met |
| H6_C298RANK | seed delta (4) ≥ median unnamed delta | 4 ≥ 1.0 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
domain (33 unnamed columns, not hundreds — 13 s0-bearing
holding 37 sites + 20 pure-private; c341 empty on all 764),
by mover count (33/764 move anything; 731 read present on all
33), by moved-set size (18 singles vs 9's k=15 and 700's
k=8), by column (c311 moves most with 12, all-but-one
extra-only; every one of the 33 columns moves somewhere), by
delta (55/79 read delta 1 while 5 cells read 9–10, all
extra-only), and by standing (50 extra-only vs 21
missing-only vs 8 mixed with 12 full wipes). Task 2
discriminates by overlap (6/10 named movers also move
unnamed; 27 unnamed movers are new faces), by destination
identity (731/733/732's unnamed moves ARE their named
destinations), by the still+below split (2/3/700 all move
unnamed at k 6/7/8 while 711/734 move nothing unnamed), and
by seed rank (c298's wipe delta 4 ties 7th of 79 with 6 cells
strictly bigger).

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

Screenshot: absent by rule. The working census heatmap
(`m34-census.png`, 462 B of 5242880 budget, 764×33 native)
stays in the work dir only; DESIGN.md admits an evidence copy
iff H5 meets AND ≥3 unnamed movers read below 0.95 — H5 does
not meet (0.2121).

Recorded without verdict: 33/764 shapes move ≥1 of 33 unnamed
columns (79 moved cells: 50 extra-only, 21 missing-only, 8
mixed; deltas 1:55 2:10 3:5 4:3 5:1 9:3 10:2); 6/10 named
movers also move unnamed while 27 unnamed movers are
named-still; 2/3/700 move unnamed at k 6/7/8 while 711/734
move nothing unnamed; 709-c298 recomputes to a full 4-row
wipe with 9/79 cells match-or-exceed; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| unnamed scan suite + falsification bars, recorded before running | recorded | `DESIGN.md`: union-domain census + overlap + row-delta, named/unnamed/below joins, seed rank, U1–U4 controls, bars H1–H6/N |
| presence matrix + mover census + top-20 + delta hist + wall/exit/shas/determinism | measured | §Step 2: 764×33 TSV + 33-mover census + top-20 + hist; 6.2 s; re-run identical |
| joins (named∩unnamed, below-0.95, seed rank) | measured | §Step 2: 6/4/27/727 + 7/26/2/729 + 9/79 match-or-exceed |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a mover map discriminates (or absence reasoned) | measured | absent by rule: H5 not met (0.2121); 462 B working copy only |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m34"
cp local/research/M34/m34.py local/research/M34/control.py local/research/M34/DESIGN.md "/Volumes/Extreme SSD/m34/"
python3 m34.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28/m28.txt" "/Volumes/Extreme SSD/m28/m28-census.tsv" "/Volumes/Extreme SSD/m34" /Users/bradrichardson/dev/ssx3/local/research/M34 > m34.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m34/m34-census.tsv" local/research/M34/m34-census.tsv
```

## Paths

Evidence (committed): `local/research/M34/` — `DESIGN.md`
(suite + bars, recorded before running), `m34.py`
(unnamed census + joins + rank + PNG writer), `control.py`
(known-unnamed-move controls), `m34-census.tsv` (full 764×33
matrix, 163262 B), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m34/` —
`m34.txt` (receipt: shas, baselines, guards, Task-1/2 tables,
joins, rank, re-run, PNG size), `control.txt`, `m34.py`,
`control.py`, `DESIGN.md` (working copies),
`m34-census.tsv` + `m34-census.png` (working copies, 462 B
PNG). No writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`,
`m20/`, `m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`,
`m28/`, `m29/`, `m30/`, `m31/`, `m32/`, `m33/`, or other
agents' dirs.

## Gap rows (exact next brief each needs)

1. Shape-9 unnamed cells (new): 15 unnamed moved cells
   (310–316, 318, 322, 327, 332, 336, 337, 339, 351) incl.
   the only mixed delta-5 (c315) and a tied delta-4 (c314) —
   located, not attributed at byte level. Needs its own
   brief: per-site value table (δ, gaps, bulk status) for
   9's unnamed cells, offline — no new harness code.
2. Still-below unnamed cells (new): 2/3/700 move unnamed at
   k 6/7/8 (J 0.9159/0.9340/0.8462) — their below-but-still
   divergence is now located in unnamed columns, not
   attributed. Needs its own brief: the same per-site value
   attribution for 2/3/700's unnamed cells, offline — no new
   harness code.
3. Big-delta fresh columns (new, minor): 700-c54 (+10 rows),
   761-c54 (+4), 731/733 dests (+9/+10) — the 5 delta≥9
   cells are all fresh-column growth. Needs its own brief
   only if fresh-column growth matters: dest-row listing +
   value table, offline — no new harness code.
4. Same-column opposite standings (new, minor): c298 reads a
   full 4-row wipe on 709 but extra-only growth on 732 (keeps
   s0's 4 rows); c311 reads 11 extra-only vs 1 missing-only
   across 12 movers. Needs its own brief only if per-column
   standing splits matter: row-list + value comparison,
   offline — no new harness code.
5. Shape-22 bottom cluster (M33 gap 3, still open): 2
   outside-col privates (393,307)/(402,295) + the 2 c296 far
   extras form a rows-393–402 group. Needs its own brief
   only if bottom-frame privates matter: full-set
   attribution for shape 22, offline — no new harness code.
6. M33 gaps 1, 4–5 (still open, by reference): see M33 REPORT
   gaps 1, 4–5 for the exact brief each needs (far/near
   private split; M29 gaps 5–11 incl. 711 pair wipe, 734
   triple move, 732 c296→c298 move, below-0.95 shape family,
   static-on-other-frame privates, M26 gaps; M32 gap 1 + M31
   gap 2).

(M33 gap 2 — this brief — worked at table level above. M29
gap 3 — the 709-c298 seed — is reproduced + ranked above.)

## What I could not do

1. No per-site values: δ values, gaps, and bulk status at
   unnamed moved/private sites are unattributed (census is
   set-level by brief).
2. No destination assignment for unnamed moves: row-deltas
   are tabled without the M28-style displacement step (brief
   pins presence + overlap + joins only).
3. No per-cell row lists beyond the seed + big-delta rows:
   the other 70 moved cells are tabled as counts in the
   receipt with full n/ov/pres in the TSV.
4. Brief's "(hundreds)" reads 33: the union tail-Y column
   space is 41 wide (8 named + 33 unnamed) — the method
   stands, the parenthetical does not.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M34/`: `DESIGN.md`, `m34.py`,
`control.py`, `m34-census.tsv` (163262 B), `REPORT.md` (this
file).
