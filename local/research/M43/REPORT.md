# M43 — Big-delta fresh columns: dest-row listing + value table for 761/731/733: REPORT

M34 gap 3 worked at table level: the 5 fresh cells recompute
to the pinned n/ov + miss/extra + deltas exactly on all 5
cells (FULL 764×33 TSV byte-identical to `m34-census.tsv` —
stop rule not triggered), splitting into 41 extras + 0
missings. Row-lists read 761-c54 [259,261,263,274] (M37's 4
reproduced exactly — H1 met) + 731-c259/c279 and 733-c303
rows 25–33 contiguous + 733-c323 rows 25–34; 761's rows
overlap 700-c54's cited 10 in 1 row ([259] — H6 met). Values
read pooled 5/41 |δ| 8 (H2 0.1220 — not met), 4/41 bulk on s0
(H3 0.0976 — not met), 13/41 −− with 28/41 −0 (H4 0.3171 —
not met); 1/5 cells fully c54-like (H5 — not met; the one is
761-c54 at 4/4 8s + 4/4 bulk + 4/4 −−). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M43.md`. Tables, no
verdicts.

Headers read first: `local/research/M34/REPORT.md` (all of it:
gap 3 = this brief — the 5 delta≥9 cells are all fresh-column
growth — 700-c54 (+10), 733-c323 (+10), 731-c259 (+9),
731-c279 (+9), 733-c303 (+9) — plus 761-c54 (+4); 731/733's
moves are their M27/M28 named-swap destinations; big-delta
pins 761 c54 4/0 0/4 d4, 731 c259/c279 9/0 0/9 d9, 733 c303
9/0 0/9 d9, 733 c323 10/0 0/10 d10, all fresh) plus
`local/research/M36/REPORT.md` (700-c54's 10 extras WITH
values — rows [245,246,247,252,253,258,259,278,279,283], all
|δ| 8 bulk −− — by reference, do not re-attribute) plus
`local/research/M37/REPORT.md` (761's 4 in-mask tail bytes at
(259,54)/(261,54)/(263,54)/(274,54) — row-list cross-check).

Time box 4 hours (start 2026-09-20 05:49 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m42/` — all outputs went to the new
`/Volumes/Extreme SSD/m43/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m34-census.tsv` (match target). Work dir
`/Volumes/Extreme SSD/m43/`; evidence `local/research/M43/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M42):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0761 | `d0de9408…99c352` |
| m16-mid-s0761 | `72e4dbc3…f67d1e3` |
| m16-full-s0761 | `b22064cc…afc9209` |
| m16-v0-s0731 | `a3812010…6a34135` |
| m16-mid-s0731 | `f2349d19…5833d8290` |
| m16-full-s0731 | `e1d2d409…f80ecfe7` |
| m16-v0-s0733 | `e60cd548…79444a0` |
| m16-mid-s0733 | `49a17a53…eb017ab67` |
| m16-full-s0733 | `97d16216…8895df70` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m43.txt` §inputs. `m34-census.tsv` 163262 B —
matches M34's committed size. Triplet fold sha over all 764×3
bins: `6c906897…61fd423b1` — matches M28/M34 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M42 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 match exactly;
s761/s731/s733 cell reads 2484/2436/2454 (unpinned — tabled
as measured); FULL unnamed TSV match (all 764 rows: tail + J4
+ all-33-column n/ov/pres) vs `m34-census.tsv`; 761/731/733
rows match the pinned k 1/2/2 + n/ov + standings + deltas
exactly (§Task 1); pooled counts read 4+0 / 18+0 / 19+0
exactly; all 41 pooled sites Y-plane. Mismatch rule
(DESIGN.md) not triggered.

## Runs (offline estimators)

One `m43.py` invocation (the receipt, 6.9 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m43.py receipt | 6.9 s | exit 0; all guards pass; canon `5f50c7f2…ada337dc4` |
| control.py C-FRESH | <1 s | green; sets + J + rows + values + standings exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 6.3 s |
| Task 1+2 (rowlists + per-site values + stats) | 3 | 0.1 s |
| Determinism re-run (Tasks on s0+761+731+733, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m43.py` wall | — | 6.9 s |

## Step 2 — estimates

### Task 1 — dest-row listing (do the 5 cells reproduce?)

The 5 cells recomputed from the dumps (FULL TSV guard passed
first — all 764 rows byte-identical): k 1/2/2 with n/ov/
standings/deltas all exact (match=True on all 5 cells).

1. Row-list table: all 5 cells s0-rows (empty — fresh) vs
   Q-rows vs extra rows (full row lists, the new data).

| cell | s0 rows | Q rows | extra rows |
| --- | --- | --- | --- |
| 761 c54 | [] | [259,261,263,274] | all 4 |
| 731 c259 | [] | [25,26,27,28,29,30,31,32,33] | all 9 |
| 731 c279 | [] | [25,26,27,28,29,30,31,32,33] | all 9 |
| 733 c303 | [] | [25,26,27,28,29,30,31,32,33] | all 9 |
| 733 c323 | [] | [25,26,27,28,29,30,31,32,33,34] | all 10 |

(731/733 dest rows read contiguous rows 25–33 in three cells
plus c323's 25–34; 761-c54's 4 read [259,261,263,274].)

2. Fresh-column proof table: ov 0 + n0 0 + miss 0 per cell
   (fresh growth, not moves).

| cell | n0 | ov | miss | extra | delta | fresh |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 761 c54 | 0 | 0 | 0 | 4 | 4 | True |
| 731 c259 | 0 | 0 | 0 | 9 | 9 | True |
| 731 c279 | 0 | 0 | 0 | 9 | 9 | True |
| 733 c303 | 0 | 0 | 0 | 9 | 9 | True |
| 733 c323 | 0 | 0 | 0 | 10 | 10 | True |

(5/5 cells read n0==0 + ov==0 + miss==0.)

3. Cross-check table: 761's 4 rows vs M37's (259,261,263,274)
   + 700-c54's 10 rows cited from M36 (do 761's rows overlap
   c54's?).

| check | want | read |
| --- | --- | --- |
| 761 rows vs M37 | [259,261,263,274] | [259,261,263,274], match=True |
| 700-c54 cited (M36, by reference) | 10 rows | [245,246,247,252,253,258,259,278,279,283] |
| 761 ∩ c54 overlap | — | [259] (1/4 of 761's; 1/10 of c54's) |

### Task 2 — value table (uniform like c54, or per-cell?)

1. Per-site value table: all 41 sites (4+9+9+9+10) with
   offset, |δ_Q|, s0 status + |δ_s0|, signed gaps both
   frames, gap signs (M36-style).

Extra-site table s761c54 (all 4: cell, offset, plane, row, col;
|δ_761|; s0 status + |δ_s0|; signed gaps s761 vs s0; sign):

| cell | offset | plane | (r,c) | \|δ_761\| | s0 status | \|δ_s0\| | g_761 | g_s0 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 54 | 331628 | Y | (259,54) | 8 | bulk | 7 | −22 | −22 | −− |
| 54 | 334188 | Y | (261,54) | 8 | bulk | 4 | −22 | −10 | −− |
| 54 | 336748 | Y | (263,54) | 8 | bulk | 1 | −23 | −6 | −− |
| 54 | 350828 | Y | (274,54) | 8 | bulk | 7 | −22 | −22 | −− |

Extra-site table s731c259 (all 9):

| cell | offset | plane | (r,c) | \|δ_731\| | s0 status | \|δ_s0\| | g_731 | g_s0 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 259 | 32518 | Y | (25,259) | 10 | noncell | n/a | −23 | 0 | −0 |
| 259 | 33798 | Y | (26,259) | 15 | noncell | n/a | −37 | 0 | −0 |
| 259 | 35078 | Y | (27,259) | 17 | noncell | n/a | −43 | 0 | −0 |
| 259 | 36358 | Y | (28,259) | 18 | noncell | n/a | −44 | 0 | −0 |
| 259 | 37638 | Y | (29,259) | 17 | noncell | n/a | −43 | 0 | −0 |
| 259 | 38918 | Y | (30,259) | 17 | noncell | n/a | −42 | 0 | −0 |
| 259 | 40198 | Y | (31,259) | 17 | noncell | n/a | −40 | 0 | −0 |
| 259 | 41478 | Y | (32,259) | 16 | noncell | n/a | −38 | −1 | −− |
| 259 | 42758 | Y | (33,259) | 13 | noncell | n/a | −30 | −6 | −− |

Extra-site table s731c279 (all 9):

| cell | offset | plane | (r,c) | \|δ_731\| | s0 status | \|δ_s0\| | g_731 | g_s0 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 279 | 32558 | Y | (25,279) | 11 | noncell | n/a | −27 | 0 | −0 |
| 279 | 33838 | Y | (26,279) | 16 | noncell | n/a | −39 | 0 | −0 |
| 279 | 35118 | Y | (27,279) | 17 | noncell | n/a | −41 | 0 | −0 |
| 279 | 36398 | Y | (28,279) | 17 | noncell | n/a | −40 | 0 | −0 |
| 279 | 37678 | Y | (29,279) | 16 | noncell | n/a | −40 | 0 | −0 |
| 279 | 38958 | Y | (30,279) | 16 | noncell | n/a | −41 | 0 | −0 |
| 279 | 40238 | Y | (31,279) | 17 | noncell | n/a | −43 | −1 | −− |
| 279 | 41518 | Y | (32,279) | 19 | noncell | n/a | −46 | −3 | −− |
| 279 | 42798 | Y | (33,279) | 16 | noncell | n/a | −38 | −9 | −− |

Extra-site table s733c303 (all 9):

| cell | offset | plane | (r,c) | \|δ_733\| | s0 status | \|δ_s0\| | g_733 | g_s0 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 303 | 32606 | Y | (25,303) | 11 | noncell | n/a | −24 | 0 | −0 |
| 303 | 33886 | Y | (26,303) | 16 | noncell | n/a | −38 | 0 | −0 |
| 303 | 35166 | Y | (27,303) | 15 | noncell | n/a | −39 | 0 | −0 |
| 303 | 36446 | Y | (28,303) | 13 | noncell | n/a | −35 | 0 | −0 |
| 303 | 37726 | Y | (29,303) | 13 | noncell | n/a | −32 | 0 | −0 |
| 303 | 39006 | Y | (30,303) | 13 | noncell | n/a | −31 | 0 | −0 |
| 303 | 40286 | Y | (31,303) | 13 | noncell | n/a | −31 | 0 | −0 |
| 303 | 41566 | Y | (32,303) | 12 | noncell | n/a | −31 | 0 | −0 |
| 303 | 42846 | Y | (33,303) | 9 | noncell | n/a | −25 | −3 | −− |

Extra-site table s733c323 (all 10):

| cell | offset | plane | (r,c) | \|δ_733\| | s0 status | \|δ_s0\| | g_733 | g_s0 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 323 | 32646 | Y | (25,323) | 11 | noncell | n/a | −29 | 0 | −0 |
| 323 | 33926 | Y | (26,323) | 18 | noncell | n/a | −42 | 0 | −0 |
| 323 | 35206 | Y | (27,323) | 18 | noncell | n/a | −42 | 0 | −0 |
| 323 | 36486 | Y | (28,323) | 17 | noncell | n/a | −40 | 0 | −0 |
| 323 | 37766 | Y | (29,323) | 16 | noncell | n/a | −39 | 0 | −0 |
| 323 | 39046 | Y | (30,323) | 16 | noncell | n/a | −41 | 0 | −0 |
| 323 | 40326 | Y | (31,323) | 16 | noncell | n/a | −41 | 0 | −0 |
| 323 | 41606 | Y | (32,323) | 19 | noncell | n/a | −44 | −3 | −− |
| 323 | 42886 | Y | (33,323) | 15 | noncell | n/a | −38 | −9 | −− |
| 323 | 44166 | Y | (34,323) | 8 | noncell | n/a | −20 | −11 | −− |

(Signed-gap equality: 2/41 — 761's rows 259+274 at −22/−22;
731/733 read 0/37 with g_s0 in {0,−1,−3,−6,−9,−11} against
g_Q in −20…−46. All 41 sites Y-plane; all 41 g_Q < 0.)

2. Per-cell value stats: |δ| list/med, bulk/noncell split,
   gap-sign split per cell (5 rows).

| cell | n | \|δ_Q\| list (med) | bulk/noncell | \|δ_s0\| (bulk) | gap signs |
| --- | ---: | --- | --- | --- | --- |
| 761 c54 | 4 | [8,8,8,8] (8.0) | 4/0 | 1:1 4:1 7:2 (near 2 far 2) | −− 4 |
| 731 c259 | 9 | [10,13,15,16,17,17,17,17,18] (17.0) | 0/9 | — | −− 2 / −0 7 |
| 731 c279 | 9 | [11,16,16,16,16,17,17,17,19] (16.0) | 0/9 | — | −− 3 / −0 6 |
| 733 c303 | 9 | [9,11,12,13,13,13,13,15,16] (13.0) | 0/9 | — | −− 1 / −0 8 |
| 733 c323 | 10 | [8,11,15,16,16,16,17,18,18,19] (16.0) | 0/10 | — | −− 3 / −0 7 |

(Pooled-41 |δ_Q|: [8×5,9,10,11×3,12,13×5,15×3,16×9,17×8,
18×3,19×2], min 8, med 16.0, mean 14.2927, max 19. Pooled
bulk 4/41 (all 761's). Pooled gap signs: ++ 0 / −− 13 / −0
28; g_s0==0 on 28/41 — all −0 sites. Per-shape pooled:
s761 med 8.0; s731 med 16.5 mean 15.8333; s733 med 15.0 mean
14.1579. Largest |δ|: 19 on s731c279 (r32) + s733c323 (r32);
smallest non-8: 9 on s733c303 (r33).)

3. c54 side-by-side: each cell's stats vs 700-c54's
   uniform-8/bulk/−− (numbers only — uniform or not?).

| cell | n | ad8 | bulk | mm | c54like |
| --- | ---: | --- | --- | --- | --- |
| 700 c54 (M36, cited) | 10 | 10/10 | 10/10 | 10/10 | True |
| 761 c54 | 4 | 4/4 | 4/4 | 4/4 | True |
| 731 c259 | 9 | 0/9 | 0/9 | 2/9 | False |
| 731 c279 | 9 | 0/9 | 0/9 | 3/9 | False |
| 733 c303 | 9 | 0/9 | 0/9 | 1/9 | False |
| 733 c323 | 10 | 1/10 | 0/10 | 3/10 | False |

(1/5 cells read fully c54-like (761c54 — H5). 761c54's bulk
|δ_s0| reads 1:1 4:1 7:2 (near 2 / far 2) against c54's 6:2
7:8 (near 10/10) — tabled alongside. The pooled non-761
|δ| 8 count is 1 (s733c323 r34); the pooled non-761 bulk
count is 0.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-FRESH (known 5 fresh) | priv 5 exact, miss 0, J 0.9533, rows + values + gaps + standings exact, cell fixed, orig kept | exact | True |

(Spanned fresh Y cols [98,305,334] with rows [42] / [26,27,28]
/ [25] — all no-s0-tail, all extra-only, rows exact; injected
+8×2/−8×3 with orig |δ| all 1; tailB 107. Full rows in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Tasks on s0+761+731+733: per-shape per-cell
rowlists + fresh-proof rows + per-site value rows + per-cell
stats + pooled summaries + cross-checks, fresh loads) pass1
`5f50c7f2…ada337dc4` vs pass2 `5f50c7f2…ada337dc4`,
identical=True; 199/199 lines match=True; sets
identical=True (s761 extras 4, missings 0, shared 102; s731
18/0/82; s733 19/0/81).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_761ROWS | 761-c54's 4 rows == [259,261,263,274] exactly | exact — met |
| H2_UNIFORM8 | pooled dest sites with \|δ_Q\|==8, share ≥ 0.50 | 5/41 = 0.1220 — not met |
| H3_BULK | pooled dest sites bulk on s0, share ≥ 0.50 | 4/41 = 0.0976 — not met |
| H4_GAPMM | pooled dest sites with gaps −−, share ≥ 0.50 | 13/41 = 0.3171 — not met |
| H5_C54LIKE | dest cells fully c54-like (all 8s + all bulk + all −−), ≥3 of 5 | 1/5 (761c54) — not met |
| H6_ROWOVERLAP | ≥1 of 761's 4 rows recurs in c54's cited 10 | [259], 1 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (5/5 cells n/ov + standings + deltas exact with
the FULL TSV byte-identical), by row-list (761's
[259,261,263,274] vs three cells at contiguous rows 25–33
plus c323's 25–34), by fresh proof (5/5 n0==0 + ov==0 +
miss==0), and by recurrence (761 ∩ c54 = [259]). Task 2
discriminates by |δ| (761c54 uniform 8 vs dest medians
17.0/16.0/13.0/16.0 with pooled med 16.0), by standing (4/4
bulk on 761c54 vs 0/37 bulk on 731/733), by gap sign (4/4 −−
on 761c54 vs 28/37 −0 on 731/733 with g_s0==0), and by
c54-likeness (1/5 cells fully c54-like — 761c54 only, itself
2 near/2 far against c54's 10 near).

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

Screenshot: present by rule. The evidence dest-cell map
(`m43-destmap-s0733.png`, 88678 B of 5242880 budget) colors
s733's shared tail green with its 19 dest extras red
(non-c54-like cells); DESIGN.md admits an evidence copy iff
H1 meets AND H5 reads split (1–4 of 5 cells fully c54-like)
— H1 meets with H5 at 1/5. Per-map counts table the split:
s761 4 yellow / 0 red (shared 102), s731 0 / 18 (shared 82),
s733 0 / 19 (shared 81); the s761/s731 maps stay in the work
dir only.

Recorded without verdict: 5/5 fresh cells reproduce M34's
n/ov + standings + deltas exactly with row-lists 761
[259,261,263,274] + 731/733 at rows 25–33/34; 761's rows
match M37 exactly with 1-row overlap ([259]) vs c54's cited
10; pooled values read 5/41 |δ| 8, 4/41 bulk, 13/41 −− with
28/41 −0; 1/5 cells read fully c54-like (761c54, itself 2
near/2 far vs c54's 10 near); 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| dest-row + value suite + falsification bars, recorded before running | recorded | `DESIGN.md`: rowlists + fresh proof + cross-checks, 41-site values + per-cell stats + c54 side-by-side, C-FRESH control, bars H1–H6/N |
| row-list tables + value tables + wall/exit/shas/determinism | measured | §Step 2: 5 rowlists + 5/5 fresh + 41 site rows + stats + side-by-side; 6.9 s; re-run identical |
| controls (known fresh cells) | measured | §Step 2: C-FRESH green (5 exact, J 0.9533, rows + values + standings exact) |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a dest-cell map discriminates (or absence reasoned) | measured | present by rule: H1 + H5 split 1/5; 88678 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m43"
cp local/research/M43/m43.py local/research/M43/control.py local/research/M43/DESIGN.md "/Volumes/Extreme SSD/m43/"
python3 m43.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m43" /Users/bradrichardson/dev/ssx3/local/research/M43 > m43.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m43/m43-destmap-s0733.png" local/research/M43/m43-destmap-s0733.png
```

## Paths

Evidence (committed): `local/research/M43/` — `DESIGN.md`
(suite + bars, recorded before running), `m43.py`
(dest-row listing + value tables + side-by-side + PNG
writer), `control.py` (known-fresh-cell control),
`m43-destmap-s0733.png` (dest-cell map, 88678 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m43/` —
`m43.txt` (receipt: shas, baselines, guards, rowlists,
41-site values, stats, side-by-side, re-run, PNG sizes,
21156 B), `control.txt`, `m43.py`, `control.py`, `DESIGN.md`
(working copies), `m43-destmap-s0761.png` +
`m43-destmap-s0731.png` + `m43-destmap-s0733.png` (working
copies). No writes into `m15/`, `m16/`, `m17/`–`m42/`, or
other agents' dirs.

## Gap rows (exact next brief each needs)

1. Dest-row band 25–34 (new): 731/733's 37 dest rows all sit
   in rows 25–34 (three cells contiguous 25–33 + c323's
   25–34) vs c54/761c54's rows 245–283 — located, not
   joined. Needs its own brief only if dest-row seats
   matter: row-seat comparison of dest rows vs the named-row
   band, offline — no new harness code.
2. g_s0==0 dest sites (new): 28/37 dest sites read g_s0==0
   (static on s0) with −0 gap signs — tabled, not
   attributed. Needs its own brief only if static-site
   growth matters: per-site v0/mid/full triple comparison at
   dest sites, offline — no new harness code.
3. 761c54 near/far split (new, minor): 761c54 reads fully
   c54-like on all H5 legs but bulk |δ_s0| 2 near/2 far vs
   c54's 10 near — tabled, not split further. Needs its own
   brief only if near-miss gradation matters: |δ_s0|-value
   comparison across c54-like cells, offline — no new
   harness code.
4. M37 gap 2 (still open, by reference): see M37 REPORT gap 2
   for the exact brief it needs (701 mask column block
   54–65).
5. M36 gaps 2–6 (still open, by reference): see M36 REPORT
   gaps 2–6 for the exact brief each needs (shared-site
   triple; s3 all-delta-1 row; M35 gaps 1–3; M34 gaps 3–4;
   M33 gaps 1, 4–5).
6. M35 gaps 1–3 (still open, by reference): see M35 REPORT
   gaps 1–3 for the exact brief each needs (per-cell
   standing asymmetry; near-miss triple; big-|δ| unnamed
   sites).
7. M34 gaps 4–5 (still open, by reference): see M34 REPORT
   gaps 4–5 for the exact brief each needs (same-column
   opposite standings; shape-22 bottom cluster).

(M34 gap 3 — this brief — worked at table level above. M37
gap 1 — 761's 4 vs c54's 10 row-list + value comparison — is
also worked at table level above: §Task 1.3 + §Task 2.)

## What I could not do

1. No 700-c54 re-attribution: 700-c54's rows + values are
   cited WITH values from M36 by reference per the brief
   (never recomputed — no s700 triplet loads).
2. No destination assignment for fresh growth: row-deltas
   are tabled without the M28-style displacement step (brief
   pins row-lists + values only).
3. No band/decile/streak/carrier joins: the brief pins no
   position joins, so that machinery is dropped per
   DESIGN.md (input integrity rests on the fold sha +
   R_s-vs-loo + FULL TSV guard + Model-0 recompute).
4. No explanation: values are attributed per site per cell,
   no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M43/`: `DESIGN.md`, `m43.py`,
`control.py`, `m43-destmap-s0733.png` (88678 B, rule-met),
`REPORT.md` (this file).
