# M50 — 731/733 full-set attribution: static rows on the other frame?: REPORT

M29 gap 10 worked at table level: 731/733 recompute to the
pinned tails, Jaccards, wipe/dest standings, and row-lists
exactly on all 4 wipe + 5 dest cells (FULL 764×8 named TSV +
FULL 764×33 unnamed TSV byte-identical to `m28-census.tsv` /
`m34-census.tsv` — stop rule not triggered), splitting into
41 wiped + 37 dest + 4 (761) sites. Wipe row-lists read
731-c257/c277 rows 23–32 + 733-c301 rows 23–33 + 733-c321
rows 23–32 (Q rows [] — full wipes); dest recount reads
g_s0==0 on 28/41 pooled (7/9 + 6/9 + 8/9 + 7/10 + 0/4 —
H2 met). Static census reads wiped g_Q==0 on 33/41 (H1 met:
10/10 + 10/10 + 3/11 + 10/10) with 0/41 Q-bulk (H3 — not
met, symmetric with dests' cited 0/37 s0-bulk), kept g==0 on
0/163 either frame (H6 — not met); priv==dest + miss==wipe
on both shapes with 0 outside (H4 met). Wiped |δ_s0| medians
read 28.5/27.0/32.0/25.5 (pooled med 27.0) vs dests' cited
pooled med 16.0 (H5 — differs); wiped gap signs read +0
33/41 + ++ 8/41 (all s0 gaps positive) vs dests' cited −0
28/37 + −− 9/37 (all Q gaps negative). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M50.md`. Tables, no
verdicts.

Headers read first: `local/research/M29/REPORT.md` (all of it:
M29 gap 10 = this brief — 15/19 733-privates + 13/18
731-privates read gap 0 on s0) plus `local/research/M28/
REPORT.md` (all of it: 731 tail 100 J 0.6833 wipes [257,277]
→ dests 259/279 +2/+2 rows 25–33; 733 tail 100 J 0.6694
wipes [301,321] → dests 303/323 +2/+2 rows 25–33/34) plus
`local/research/M43/REPORT.md` (all of it: the 4 dest cells
WITH values — 37 sites, 28/41 g_s0==0 pooled with 761's 4 —
by reference for dests: the 28/41 count reproduced here,
then the WIPED sides + full sets attributed).

Time box 4 hours (start 2026-09-20 06:56 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m49/` — all outputs went to the new
`/Volumes/Extreme SSD/m50/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m28-census.tsv` + `m34-census.tsv` (match targets). Work dir
`/Volumes/Extreme SSD/m50/`; evidence `local/research/M50/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M49; 761/731/733 prefixes match M43):

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
| m28-census.tsv | `27872527…7ca15a9e7f` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m50.txt` §inputs. `m28-census.tsv` 54296 B +
`m34-census.tsv` 163262 B — both match the committed sizes.
Triplet fold sha over all 764×3 bins:
`6c906897…61fd423b1` — matches M28/M34/M43 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M49 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
δ==0 violations read 0 shapes. s0 cell 2475 + tail 102
(sub-bins 28+74, max 47) + P(δ>0) 0.8093 + all 8 s0 named
reference row lists match exactly; s761/s731/s733 cell reads
2484/2436/2454 (unpinned — tabled as measured; the triple
matches M43's tabled 2484/2436/2454). FULL named TSV match
(all 764 rows) vs `m28-census.tsv` + FULL unnamed TSV match
(all 764 rows) vs `m34-census.tsv`; 731/733/761 rows match
the pinned wipes + dests + n/ov + standings + deltas exactly
(§Task 1); pooled counts read dest 4+18+19 / wipe 0+20+21
exactly; dest g_s0==0 reads 28/41 with per-cell 0/4 + 7/9 +
6/9 + 8/9 + 7/10 exactly; all 41 wiped + 41 dest-recount
sites Y-plane; wiped g_s0!=0 throughout + dest g_Q!=0
throughout + kept g!=0 both frames (cell-7 moved guards).
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m50.py` invocation (the receipt, 5.5 s, exit 0 — the
estimator was never changed after the receipt run started);
one `control.py` invocation (green, first try — a want-label
typo for synthetic cell counts was fixed before the receipt
control run started, no measurements taken).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m50.py receipt | 5.5 s | exit 0; all guards pass; canon `e826de9a…96832c18a` |
| control.py C-WIPEDEST | <1 s | green; sets + J + rows + values + census exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 5.2 s |
| Task 1 (wipe rows + dest recount + full-set) | 3 | 0.0 s |
| Task 2 (wiped values + static census) | 2 | 0.0 s |
| Determinism re-run (Task 1 on s0+731+733+761) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m50.py` wall | — | 5.5 s |

## Step 2 — estimates

### Task 1 — wipe reproduction + dest recount (do the rows reproduce?)

731/733/761 recomputed from the dumps (FULL named + FULL
unnamed TSV guards passed first — all 764 rows byte-identical
on both): tails, Jaccards, moved sets, n/ov, standings,
deltas all exact (match=True on all 4 wipe + 5 dest cells).

1. Wipe tables: all 4 wipe cells s0-rows vs Q-rows (empty —
   full wipe) vs miss rows (full wiped row lists, the new
   data).

| cell | s0 rows | Q rows | miss rows |
| --- | --- | --- | --- |
| 731 c257 | [23..32] (10) | [] | all 10 |
| 731 c277 | [23..32] (10) | [] | all 10 |
| 733 c301 | [23..33] (11) | [] | all 11 |
| 733 c321 | [23..32] (10) | [] | all 10 |

(Wipe row-lists read s0 rows exactly (c257/c277 rows 23–32,
c301 rows 23–33, c321 rows 23–32); Q rows read [] on all 4
cells — full wipes, not moves.)

2. Wipe-proof table: nQ 0 + ov 0 + extra 0 per cell (full
   wipe, not partial).

| cell | nQ | ov | miss | extra | delta | wipe |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 731 c257 | 0 | 0 | 10 | 0 | 10 | True |
| 731 c277 | 0 | 0 | 10 | 0 | 10 | True |
| 733 c301 | 0 | 0 | 11 | 0 | 11 | True |
| 733 c321 | 0 | 0 | 10 | 0 | 10 | True |

(4/4 cells read nQ==0 + ov==0 + extra==0.)

3. Dest recount: all 5 dest cells (incl. 761-c54) extras
   row-lists + g_s0==0 counts (28/41 reproduced?).

| cell | Q rows | extra rows | g_s0==0 |
| --- | --- | --- | --- |
| 761 c54 | [259,261,263,274] | all 4 | 0/4 |
| 731 c259 | [25..33] (9) | all 9 | 7/9 |
| 731 c279 | [25..33] (9) | all 9 | 6/9 |
| 733 c303 | [25..33] (9) | all 9 | 8/9 |
| 733 c323 | [25..34] (10) | all 10 | 7/10 |

(Pooled dest g_s0==0 reads 28/41 — 731/733: 28/37 with
per-cell 7/9 + 6/9 + 8/9 + 7/10; 761-c54: 0/4. Row-lists +
per-cell counts match M43 exactly.)

4. Full-set table: 731 + 733 priv/miss/shared/tail with
   0-outside checks (are the wipes + dests the whole sets?).

| Shape | tail | J vs s0 | priv | miss | shared | dest_ex | wipe_mi | outside priv/miss |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 731 | 100 | 0.6833 | 18 | 20 | 82 | 18 | 20 | 0 / 0 |
| 733 | 100 | 0.6694 | 19 | 21 | 81 | 19 | 21 | 0 / 0 |

(761 by reference for the pooled recount: tail 106, priv 4,
miss 0, shared 102, dest_ex 4, outside 0/0. priv==dest
extras AND miss==wiped rows on BOTH 731 and 733 — H4.)

No other 731/733 moves per M28/M34 (verified via FULL TSV
guards + moved-set guards): 731 named moved == [257,277]
only, unnamed moved == [259,279] only; 733 named moved ==
[301,321] only, unnamed moved == [303,323] only; 761 named
moved == [] with unnamed moved == [54] only.

### Task 2 — wiped values + static census (where does g==0 live?)

1. Per-site wiped-value table: all 41 wiped sites (10+10+11+
   10) with offset, |δ_s0|, Q status + |δ_Q|, signed gaps
   both frames, gap signs (M36-style; miss leg: adQ=|δ_s0|,
   gQ=g_s0, gO=g_Q).

Wiped-site table s731w257 (all 10):

| cell | offset | plane | (r,c) | |δ_s0| | Q status | |δ_Q| | g_s0 | g_731 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 257 | 29954 | Y | (23,257) | 17 | noncell | n/a | 42 | 0 | +0 |
| 257 | 31234 | Y | (24,257) | 28 | noncell | n/a | 66 | 0 | +0 |
| 257 | 32514 | Y | (25,257) | 30 | noncell | n/a | 71 | 0 | +0 |
| 257 | 33794 | Y | (26,257) | 29 | noncell | n/a | 70 | 0 | +0 |
| 257 | 35074 | Y | (27,257) | 29 | noncell | n/a | 70 | 0 | +0 |
| 257 | 36354 | Y | (28,257) | 29 | noncell | n/a | 70 | 0 | +0 |
| 257 | 37634 | Y | (29,257) | 29 | noncell | n/a | 70 | 0 | +0 |
| 257 | 38914 | Y | (30,257) | 28 | noncell | n/a | 67 | 0 | +0 |
| 257 | 40194 | Y | (31,257) | 23 | noncell | n/a | 55 | 0 | +0 |
| 257 | 41474 | Y | (32,257) | 13 | noncell | n/a | 28 | 0 | +0 |

Wiped-site table s731w277 (all 10):

| cell | offset | plane | (r,c) | |δ_s0| | Q status | |δ_Q| | g_s0 | g_731 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 277 | 29994 | Y | (23,277) | 16 | noncell | n/a | 37 | 0 | +0 |
| 277 | 31274 | Y | (24,277) | 25 | noncell | n/a | 60 | 0 | +0 |
| 277 | 32554 | Y | (25,277) | 28 | noncell | n/a | 66 | 0 | +0 |
| 277 | 33834 | Y | (26,277) | 27 | noncell | n/a | 66 | 0 | +0 |
| 277 | 35114 | Y | (27,277) | 27 | noncell | n/a | 66 | 0 | +0 |
| 277 | 36394 | Y | (28,277) | 28 | noncell | n/a | 66 | 0 | +0 |
| 277 | 37674 | Y | (29,277) | 28 | noncell | n/a | 69 | 0 | +0 |
| 277 | 38954 | Y | (30,277) | 28 | noncell | n/a | 67 | 0 | +0 |
| 277 | 40234 | Y | (31,277) | 24 | noncell | n/a | 56 | 0 | +0 |
| 277 | 41514 | Y | (32,277) | 13 | noncell | n/a | 30 | 0 | +0 |

Wiped-site table s733w301 (all 11):

| cell | offset | plane | (r,c) | |δ_s0| | Q status | |δ_Q| | g_s0 | g_733 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 301 | 30042 | Y | (23,301) | 18 | noncell | n/a | 43 | 0 | +0 |
| 301 | 31322 | Y | (24,301) | 29 | noncell | n/a | 67 | 0 | +0 |
| 301 | 32602 | Y | (25,301) | 33 | noncell | n/a | 79 | 5 | ++ |
| 301 | 33882 | Y | (26,301) | 41 | noncell | n/a | 93 | 21 | ++ |
| 301 | 35162 | Y | (27,301) | 47 | noncell | n/a | 106 | 34 | ++ |
| 301 | 36442 | Y | (28,301) | 46 | noncell | n/a | 104 | 33 | ++ |
| 301 | 37722 | Y | (29,301) | 39 | noncell | n/a | 90 | 18 | ++ |
| 301 | 39002 | Y | (30,301) | 32 | noncell | n/a | 76 | 4 | ++ |
| 301 | 40282 | Y | (31,301) | 25 | noncell | n/a | 59 | 0 | +0 |
| 301 | 41562 | Y | (32,301) | 16 | noncell | n/a | 37 | 5 | ++ |
| 301 | 42842 | Y | (33,301) | 13 | noncell | n/a | 27 | 20 | ++ |

Wiped-site table s733w321 (all 10):

| cell | offset | plane | (r,c) | |δ_s0| | Q status | |δ_Q| | g_s0 | g_733 | sgn |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 321 | 30082 | Y | (23,321) | 14 | noncell | n/a | 36 | 0 | +0 |
| 321 | 31362 | Y | (24,321) | 24 | noncell | n/a | 57 | 0 | +0 |
| 321 | 32642 | Y | (25,321) | 27 | noncell | n/a | 63 | 0 | +0 |
| 321 | 33922 | Y | (26,321) | 27 | noncell | n/a | 63 | 0 | +0 |
| 321 | 35202 | Y | (27,321) | 26 | noncell | n/a | 62 | 0 | +0 |
| 321 | 36482 | Y | (28,321) | 26 | noncell | n/a | 64 | 0 | +0 |
| 321 | 37762 | Y | (29,321) | 26 | noncell | n/a | 63 | 0 | +0 |
| 321 | 39042 | Y | (30,321) | 25 | noncell | n/a | 61 | 0 | +0 |
| 321 | 40322 | Y | (31,321) | 21 | noncell | n/a | 49 | 0 | +0 |
| 321 | 41602 | Y | (32,321) | 11 | noncell | n/a | 25 | 0 | +0 |

(Signed-gap equality: 0/41 — wiped g_s0 in +25…+106 against
g_Q in {0,4,5,18,20,21,33,34}. All 41 sites Y-plane; all 41
g_s0 > 0; all 41 Q-noncell.)

2. Per-cell wiped stats: |δ| list/med, bulk/noncell split,
   gap-sign split per wipe cell (4 rows) + per-shape pools.

| cell | n | |δ_s0| list (med) | bulk/noncell | gap signs |
| --- | ---: | --- | --- | --- |
| 731 w257 | 10 | [13,17,23,28,28,29,29,29,29,30] (28.5) | 0/10 | +0 10 |
| 731 w277 | 10 | [13,16,24,25,27,27,28,28,28,28] (27.0) | 0/10 | +0 10 |
| 733 w301 | 11 | [13,16,18,25,29,32,33,39,41,46,47] (32.0) | 0/11 | ++ 8 / +0 3 |
| 733 w321 | 10 | [11,14,21,24,25,26,26,26,27,27] (25.5) | 0/10 | +0 10 |

(Per-shape wiped pools: s731 n=20 med 28.0 mean 24.9500, +0
20/20; s733 n=21 med 26.0 mean 26.9524, ++ 8/21 + +0 13/21.
Pooled-41 wiped |δ_s0|: [11,13×3,14,16×2,17,18,21,23,24×2,
25×3,26×3,27×4,28×6,29×5,30,32,33,39,41,46,47], min 11, med
27.0, max 47. Pooled Q-bulk 0/41. Pooled gap signs: ++ 8 /
+0 33; g_Q==0 on 33/41 — all +0 sites. Largest |δ|: 47 on
s733w301 r27; smallest: 11 on s733w321 r32.)

3. Static census: g==0 sites by side (wiped g_Q==0 n? dest
   g_s0==0 n? kept g==0 n?) + |δ| at static sites (is
   staticness a value regime?).

| side | shape | n | g_s0==0 | g_Q==0 | either0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| wiped | 731 | 20 | 0 | 20 | 20 |
| wiped | 733 | 21 | 0 | 13 | 13 |
| wiped | pooled | 41 | 0 | 33 | 33 |
| dest (recount) | 731 | 18 | 13 | 0 | 13 |
| dest (recount) | 733 | 19 | 15 | 0 | 15 |
| dest (recount) | pooled-37 | 37 | 28 | 0 | 28 |
| dest (recount) | pooled-41 (+761) | 41 | 28 | 0 | 28 |
| kept | 731 | 82 | 0 | 0 | 0 |
| kept | 733 | 81 | 0 | 0 | 0 |
| kept | pooled | 163 | 0 | 0 | 0 |

(Dest g_Q==0 reads 0 throughout by the cell-7 moved guard —
dest sites are Q-tail; wiped g_s0==0 reads 0 throughout —
wiped sites are s0-tail; kept reads 0/163 either frame —
tail on both. The 8 non-static wiped sites are all s733w301
rows 25–30/32/33 with g_733 in {4,5,5,18,20,21,33,34}.)

|δ| at static sites (wiped NEW; dest from M43's CITED
per-site rows split by cited g_s0==0 vs !=0 — no dest
triplet re-reads for values; kept n/a with counts):

| set | static n | |δ| static (med) | nonstatic n | |δ| nonstatic (med) |
| --- | ---: | --- | ---: | --- |
| wiped s731 | 20 | med 28.0, mean 24.9500 | 0 | (empty) |
| wiped s733 | 13 | med 25.0, mean 23.0000 | 8 | med 36.0, mean 33.3750 |
| wiped pooled-41 | 33 | med 26.0, mean 24.1818 | 8 | med 36.0, mean 33.3750 |
| dest cited pooled-37 | 28 | med 16.0, mean 15.0714 | 9 | med 16.0, mean 14.6667 |
| kept pooled-163 | 0 | n/a | 163 | n/a (no static split) |

(Wiped static |δ_s0| list (33):
[11,13,13,14,16,17,18,21,23,24,24,25,25,25,26,26,26,27×4,
28×6,29×5,30]; wiped nonstatic (8): [13,16,32,33,39,41,46,
47]. Cited dest static |δ_Q| (28):
[10,11×3,12,13×4,15×2,16×7,17×7,18×3]; cited dest
nonstatic (9): [8,9,13,15,16,16,17,19,19].)

4. Wipe-vs-dest comparison: wiped |δ|/status/signs (measured)
   vs M43's dest stats (cited §Baseline note — numbers only).

| leg | wiped (measured 41) | dest (M43-cited 37) |
| --- | --- | --- |
| n | 41 | 37 |
| |δ| med / mean | 27.0 / 25.98 | 16.0 / 14.97 |
| |δ| range | 11–47 | 8–19 |
| other-frame bulk | 0/41 | 0/37 |
| gap signs | +0 33 / ++ 8 | −0 28 / −− 9 |
| own-frame gap polarity | all g_s0 > 0 | all g_Q < 0 |
| static-on-other share | 33/41 = 0.8049 | 28/37 = 0.7568 |

(Dest pooled-37 mean = 554/37 = 14.97 derived from cited
per-cell lists in DESIGN.md; wiped pooled-41 mean =
(499+566)/41 = 25.98 with s731 pool sum 499 + s733 pool sum
566. Per-cell wiped
medians 28.5/27.0/32.0/25.5 vs cited dest medians
17.0/16.0/13.0/16.0.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-WIPEDEST (known 6 wipe + 6 dest + 2 kept) | wipe 6 exact, dest 6 exact, kept 2, J 0.1429, rows + values + gaps + census exact | exact | True |

(Spanned wipe cols [100,101] missing-only 3/0 each + dest
cols [102,103] extra-only 0/3 each + kept col [104] rows
[25,26] both frames; injected tail |δ|=10 ×(6+6+4 legs) with
bulk |δ|=2 ×6 legs; static legs g==0 ×6 (3 wipe-B + 3
dest-A), non-static legs g=−100; census wiped gB==0 3/6 +
dest gA==0 3/6 + kept either0 0/2 exact; cellA/cellB read
11/11 = 8 tail + 3 bulk each; background non-tail. Full rows
in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+731+733+761: per-shape wipe
row-lists + wipe-proof rows + dest-recount rows + kept g==0
rows + full-set rows, fresh loads) pass1
`e826de9a…96832c18a` vs pass2 `e826de9a…96832c18a`,
identical=True; 27/27 lines match=True; sets
identical=True (s761 dest 4 wipe 0 shared 102; s731 dest 18
wipe 20 shared 82; s733 dest 19 wipe 21 shared 81).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_WIPESTATIC | pooled wiped sites with g_Q==0, share ≥ 0.50 | 33/41 = 0.8049 — met |
| H2_DESTSTATIC | pooled 731/733 dest sites with g_s0==0, share ≥ 0.50 | 28/37 = 0.7568 — met |
| H3_WIPEBULK | pooled wiped sites bulk on Q, share ≥ 0.50 | 0/41 = 0.0000 — not met |
| H4_FULLSET | priv==dest + miss==wipe both shapes, 0 outside | True — met |
| H5_VALUEMED | median wiped |δ_s0| differs from cited dest med 16.0 | 27.0 vs 16.0 — met (differs) |
| H6_KEEPSTATIC | pooled kept sites with g==0 either frame, share ≥ 0.50 | 0/163 = 0.0000 — not met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (4/4 wipe + 5/5 dest cells n/ov + standings +
deltas exact with BOTH TSVs byte-identical on all 764 rows),
by wipe row-list (Q rows [] on all 4 — full wipes of s0 rows
23–32/33), by dest recount (28/41 g_s0==0 with per-cell
0/4 + 7/9 + 6/9 + 8/9 + 7/10 exact), and by full-set closure
(0 outside priv/miss on both shapes). Task 2 discriminates by
other-frame status symmetrically (0/41 wiped Q-bulk vs
cited 0/37 dest s0-bulk — all 78 moved sites non-cell on the
other frame), by static share (wiped 33/41 vs dest 28/37
with kept 0/163), by static seat (the 8 non-static wiped
sites sit together on s733w301 rows 25–30/32/33 while the 9
non-static dest sites split 2/3/1/3 across all 4 dest cells),
by |δ| (wiped medians 25.5–32.0 over range 11–47 vs dest
medians 13.0–17.0 over range 8–19, with wiped static med
26.0 vs nonstatic med 36.0 while cited dest static and
nonstatic both med 16.0), and by gap-sign polarity (wiped
+0/++ with all g_s0 > 0 vs dest −0/−− with all g_Q < 0, 0/41
wiped + 0/37 dest signed-equal).

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
| interior far tail | 102 of cell 7 (4.1%) | |δ|≥8, max 47; 100% Y; stands (this run) |
| standing interior remainder | 2475 of cell 7 (100%) | no rule; attribution tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence static-site map
(`m50-staticmap-s0733.png`, 88708 B of 5242880 budget) colors
s733's shared tail green with wiped sites magenta/cyan
(static/non-static g_733==0: 13/8) and dest extras red/yellow
(static/non-static g_s0==0: 15/4); DESIGN.md admits an
evidence copy (at most the s733 map) iff H2 meets AND the
wiped static share reads split (1..40 of 41) — H2 meets
(0.7568) with wiped static at 33/41. Per-map counts table the
split: s731 wipe 20/0 + dest 13/5 (shared 82), s733 wipe 13/8
+ dest 15/4 (shared 81); the s731 map (88711 B) stays in the
work dir only.

Recorded without verdict: 4/4 wipes + 5/5 dests reproduce
M28/M34/M43 exactly with row-lists Q-[] on wipes +
25–33/34 on dests; dest g_s0==0 reads 28/41 with per-cell
counts exact; static census reads wiped 33/41 + dest 28/37 +
kept 0/163 with 0/41 wiped Q-bulk; priv==dest + miss==wipe
on both shapes with 0 outside; wiped |δ| medians 25.5–32.0
vs dest 13.0–17.0 with wiped static med 26.0 vs nonstatic
36.0; gap signs read +0/++ on wipes vs −0/−− on dests; 0 B
explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| wipe + recount + census suite + falsification bars, recorded before running | recorded | `DESIGN.md`: wipe rowlists + wipe-proof, 5-cell dest recount + 28/41 guard, full-set + 0-outside, 41-site wiped values + static census + ad splits, C-WIPEDEST control, bars H1–H6/N |
| wipe/dest tables + static census + wall/exit/shas/determinism | measured | §Step 2: 4 wipelists + 5/5 recount + full-set 0-outside + 41 site rows + census + side-by-side; 5.5 s; re-run identical |
| controls (known wipe+dest + known g==0 sites) | measured | §Step 2: C-WIPEDEST green (6+6+2 exact, J 0.1429, rows + values + gaps + census exact) |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a static-site map discriminates (or absence reasoned) | measured | present by rule: H2 + wiped split 33/41; 88708 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m50"
cp local/research/M50/m50.py local/research/M50/control.py local/research/M50/DESIGN.md "/Volumes/Extreme SSD/m50/"
python3 m50.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28/m28-census.tsv" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m50" /Users/bradrichardson/dev/ssx3/local/research/M50 > m50.txt 2>&1
python3 control.py > control.txt 2>&1
cp "/Volumes/Extreme SSD/m50/m50-staticmap-s0733.png" local/research/M50/m50-staticmap-s0733.png
```

## Paths

Evidence (committed): `local/research/M50/` — `DESIGN.md`
(suite + bars, recorded before running), `m50.py`
(wipe rows + dest recount + full-set + wiped values + static
census + PNG writer), `control.py` (known-wipe+dest
synthetic control), `m50-staticmap-s0733.png` (static-site
map, 88708 B, rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m50/` —
`m50.txt` (receipt: shas, baselines, guards, wipe rows,
recount, 41-site wiped values, census, side-by-side, re-run,
PNG sizes, 24492 B), `control.txt`, `m50.py`, `control.py`,
`DESIGN.md` (working copies), `m50-staticmap-s0731.png` +
`m50-staticmap-s0733.png` (working copies). No writes into
`m15/`, `m16/`, `m17/`–`m49/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. s733w301 non-static seat (new): the 8 non-static wiped
   sites sit together on s733w301 rows 25–30/32/33 (g_733 in
   4–34, all ++, |δ_s0| med 36.0) while the other 3 wipe
   cells read 30/30 static — located, not joined. Needs its
   own brief only if wipe-seat splits matter: per-site
   v0/mid/full triple comparison at wiped sites across the 4
   wipe cells, offline — no new harness code.
2. Wipe/dest polarity flip (new): wiped sites read all g_s0
   > 0 (+0/++) while dests cite all g_Q < 0 (−0/−−) —
   tabled, not attributed. Needs its own brief only if gap
   polarity matters: signed-gap polarity census over all
   moved cells, offline — no new harness code.
3. Wiped |δ| regime (new): wiped medians 25.5–32.0 (range
   11–47) vs dests' 13.0–17.0 (range 8–19) with wiped static
   med 26.0 vs nonstatic 36.0 — tabled, not modeled. Needs
   its own brief only if value regimes matter: |δ|
   distribution comparison across wipe/dest/kept sets,
   offline — no new harness code.
4. M43 gaps 1–3 (still open, by reference): see M43 REPORT
   gaps 1–3 for the exact brief each needs (dest-row band
   25–34; g_s0==0 dest sites — partially worked here as the
   recount + census; 761c54 near/far split).
5. M37 gap 2 (still open, by reference): see M37 REPORT gap 2
   for the exact brief it needs (701 mask column block
   54–65).
6. M36 gaps 2–6 (still open, by reference): see M36 REPORT
   gaps 2–6 for the exact brief each needs (shared-site
   triple; s3 all-delta-1 row; M35 gaps 1–3; M34 gaps 3–4;
   M33 gaps 1, 4–5).
7. M35 gaps 1–3 (still open, by reference): see M35 REPORT
   gaps 1–3 for the exact brief each needs (per-cell
   standing asymmetry; near-miss triple; big-|δ| unnamed
   sites).
8. M34 gaps 4–5 (still open, by reference): see M34 REPORT
   gaps 4–5 for the exact brief each needs (same-column
   opposite standings; shape-22 bottom cluster).

(M29 gap 10 — this brief — worked at table level above.)

## What I could not do

1. No dest per-site re-attribution: dest |δ|/status/gap
   values are cited WITH values from M43 by reference per
   the brief (never recomputed — dest triplet reads cover
   row-lists + g_s0==0 counts only); the dest |δ| at-static
   split derives from M43's cited per-site rows.
2. No wipe-triple analysis: wiped sites are attributed as
   |δ_s0| + Q status + signed gaps only (no v0/mid/full
   triple decomposition — gap 1 tables the follow-up).
3. No band/decile/streak/carrier joins: the brief pins no
   position joins, so that machinery is dropped per
   DESIGN.md (input integrity rests on the fold sha +
   R_s-vs-loo + FULL TSV guards ×2 + Model-0 recompute).
4. No explanation: values are attributed per site per cell,
   no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M50/`: `DESIGN.md`, `m50.py`,
`control.py`, `m50-staticmap-s0733.png` (88708 B, rule-met),
`REPORT.md` (this file).
