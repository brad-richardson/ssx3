# M48 — Design (recorded before running)

Goal: shape-734 triple move (M28 gap 4 via M29 gap 7): c340 +
c343 full wipes with a dest collision at c342 (+2/−1), c342
itself +2 rows extra-only. Dest-row listing (full c342 row-list:
kept + [26,33]) + per-site value table for 734's full sets
(wiped c340/c343 rows + c342 dest rows + any unnamed 734 moves
per M34). Answer by table (list, don't assign rows to source
columns). Tables, no verdicts. Fully offline: no lease of any
kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m28/m28-census.tsv` (FULL named-TSV guard
per M34 precedent — 734's named row must read tail 94 J 0.8846
moved [340,342,343] with c340 0/0 + c343 0/0 + c342 7/5),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (FULL unnamed-TSV
guard per M35/M36 precedent — 734's unnamed row must read NO
unnamed moves). Work dir: `/Volumes/Extreme SSD/m48/` (new).
Evidence: `local/research/M48/` (committed with `git add -f`,
prefix `[M48]`, trailer `Orchestrated-By: Muse Code`; NEVER `git
push` in ssx3).

Headers read first: `local/research/M28/REPORT.md` (all of it:
734 tail 94 J 0.8846 moved [340,342,343]; c340 0/0 wipe → dest
c342 (+2 rows); c343 0/0 wipe → dest c342 (−1 row); c342 7/5
(+2) extra-only; displacement rows +2/+0.5/+2 and −1/+3.0/+0;
M28 displacement rule reused verbatim) plus
`local/research/M29/REPORT.md` (all of it: 734-c342 n/ov 7/5,
dest rows [26,33], |δ| 21,11, gaps −50,−26/−8,−13, bulk ×2,
dec 9,9; M27/M29 per-site machinery reused verbatim) plus
`local/research/M34/REPORT.md` (all of it: 734's census row —
NO unnamed moves; union-domain unnamed census reused verbatim;
s0-bearing-13 row lists + pure-private-20 list pinned below).

## Estimator (`m48.py`, `control.py`)

Shared core (M28 `m28.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|δ|≥8 tail), `plane_of_byte`,
`plane_coords`, `parse_loo`, `jaccard`, `off_of`,
`y_col_rows`, `priv_y_cols`, `census_of_shape` named exact-match
presence, `assign_one` displacement; M34 `m34.py` verbatim where
reused: `tail_y_cols`, `census_unnamed_of`, union-domain rule;
M36 `m36.py` verbatim where reused: `attrib_lines`,
`gapsign_lines`, `dstats_lines`; M28 PNG writer). New small
helper `shared_lines` (kept-row value rows: both-frames |δ| +
gaps + signs — `attrib_lines` covers priv/miss only). Byte
offset o -> row o//1280; Y bytes at o%4==0/2. No P1/carrier/BFS
machinery (no gradient, carrier, or edge task here — M29's dec
9,9 is cited, not recomputed).

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard).
- Bulk = cell-7 bytes with |δ|<8. Tail = cell-7 bytes with
  |δ|≥8. Tail MAP of shape s: T_s = tail boolean mask.
- Named columns (the census 8, fixed order): [257,277,296,301,
  321,340,342,343].
- s0 named reference row lists (M27/M28 pins — guard: recomputed
  s0 per-column n + row lists must match exactly or stop):
  - 257: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 277: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 296: n=9 [24,25,26,27,28,31,32,33,34]
  - 301: n=11 [23,24,25,26,27,28,29,30,31,32,33]
  - 321: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 340: n=8 [24,25,26,27,31,32,33,34]
  - 342: n=5 [27,28,29,34,35]
  - 343: n=2 [26,27]
- 734 triple-move pins (M28/M29/M34 — guard: recompute must
  match exactly or table the mismatch and stop; no further
  tasks run):
  tail 94, J 0.8846, moved [340,342,343], c340 0/0 + c343 0/0
  (full wipe both), c342 7/5 (+2, extra-only), dest rows
  [26,33], NO unnamed moves (all 33 unnamed present).
- Wiped rows (derived from the pins): c340
  [24,25,26,27,31,32,33,34] (8 rows) + c343 [26,27] (2 rows) =
  10 wiped rows.
- Dest rows (derived): c342 s0 [27,28,29,34,35] kept (5) +
  extras [26,33] (2) = 734 c342 rows [26,27,28,29,33,34,35].
- M29 dest-value pins (guard): extras |δ_734| [21,11] (rows
  [26,33]), s0 bulk |δ| [3,5], signed gaps g_734 [−50,−26] /
  g_s0 [−8,−13], M29 offsets [33964,42924], Y-plane.
  (M29's dec 9,9 cited, not recomputed — no P1 machinery.)
- Displacement pins (M28 rule rows — guard): c340→342 off +2
  rshift +0.5 minshift +2; c343→342 off −1 rshift +3.0
  minshift +0; c342 extra-only (no dest).
- UNNAMED domain (M34 union rule verbatim): union tail-Y
  columns over all 764 minus the named 8. Pinned: 41 union
  cols, 33 unnamed (13 s0-bearing + 20 pure-private):
  - s0-bearing (n0>0): 38:[215], 292:[400], 293:[405],
    298:[28,29,34,35], 307:[404], 311:[296,297,298,299],
    312:[299,300,301], 313:[274,275,276,292],
    314:[269,276,277,278,287,288,289],
    315:[266,267,268,273,274,275,276], 316:[264],
    332:[295,304], 372:[221] (37 sites).
  - pure-private (n0==0): [54,145,259,279,295,299,303,310,
    318,322,323,327,328,336,337,339,351,602,611,620].
  - c341 bears tail on no shape (stays empty across all 764).
- Near-miss (pinned, M27 verbatim): other-frame bulk with
  |δ_other| ∈ {6,7}. Far: bulk with |δ_other| ≤ 5.
  Non-cell: not cell-7 on the other frame.
- Signed gap g = v0 − full (int16 per byte, M36 verbatim).
  Gap signs: g_Q × g_O per site (++/−−/mixed/zero tabled).
- Displacement (pinned, M28 `assign_one` verbatim): per moved
  column c with NONEMPTY missing rows; extra-only moves get no
  destination (`dest=none(extra-only)`); candidates = private
  Y-columns with ≥2 sites on the SAME shape; dest(c) = argmin
  |col_priv − c|, tie-break 1: max row-overlap with rows_0(c),
  tie-break 2: smallest column; no candidates →
  `dest=none(no-cand)`. Collisions allowed (tabled as
  measured, no forced bijection).

### Task 1 — 734 wipe reproduction (do the 3 columns reproduce?)

734's row recomputed from the dumps (must match M28/M34
exactly — tail, J, moved cells, standings, unnamed moves — or
table the mismatch and stop):

1. Wipe table: c340 + c343 s0-rows vs 734-rows (empty) vs
   miss rows (full wiped row lists).
2. Dest table: c342 s0-rows vs 734-rows (kept + [26,33])
   vs extra rows ([26,33] must reproduce M29).
3. Displacement table: M28's c340→c342 + c343→c342 rows
   reproduced (+2/+0.5/+2, −1/+3.0/+0 — table the rule's
   rows, don't re-judge) + c342 extra-only standing.

### Task 2 — full-set value table (wiped + dest + unnamed?)

1. Wiped-value table: per-site |δ_s0|, s734 status, signed
   gaps, gap signs for ALL c340/c343 wiped rows (M36-style:
   `attrib_lines` + `gapsign_lines` + `dstats_lines` verbatim
   on the wiped miss set).
2. Dest-value table: c342's [26,33] extras (`attrib_lines` +
   `gapsign_lines` + `dstats_lines` on the priv set; |δ|
   21,11 bulk must reproduce) + kept rows (`shared_lines`:
   per-site |δ| both frames, gaps both, signs; all 5 must
   read tail on both frames).
3. Collision table: wiped-row count (c340 + c343) vs dest
   growth (+2) vs kept rows (5) + full-set accounting
   (priv/miss/shared vs tail 94/102) + outside-column
   priv/miss (pins: privates outside c342 = 0, missings
   outside {c340,c343} = 0 — tabled as measured; numbers
   only, no assignment of rows to source columns).

### Task 3 — controls + determinism (M18–M47 precedent)

`control.py` (mid-level synthetic truth, M36 C-VAL-style —
feasible because tail↔bulk flips keep cell-7 membership):

- C-COLLISION (known collision: 2 wipe cols + 1 shared dest,
  mimics 734's counts exactly): s0 mid' with N_wipe=10
  currently-TAIL Y sites in c340's 8 + c343's 2 rows flipped
  to bulk (mid'=blend+1, fallback blend−1 per site if +1 is
  not strictly inside — tabled) AND N_dest=2
  currently-interior-BULK gap≥17 Y sites in ONE shared dest
  column flipped to tail (mid'=blend+8 even / blend−8 odd,
  |δ|=8; per-site strict-interior check). Dest column: c342
  if it holds ≥2 landable sites, else the first offset-order
  column with ≥2 (tabled which — M29 C-PART-EXTRA fallback
  precedent).
  Known: wipe rows = the 10, dest rows = the 2, tail'=94,
  J=92/104=0.8846, cell-7 mask fixed, both wipe cols assign
  to the dest col under `assign_one`, dest |δ'|=8×2, wipe
  |δ'|=1×10, gaps equal on both frames (v0/full unchanged).
- Pass = wipe+dest-rows-exact + n/ov + displacement-collision-
  exact + values-exact + gaps-exact + standings-exact.

Determinism: re-run Task 1 (734 wipe rows + dest rows +
displacement rows + wiped/dest values) on s0+734 with fresh
loads; canonical text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s734 + m15
triplets + `m28-census.tsv` + `m34-census.tsv` shas; triplet
fold sha over all 764×3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M47 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.
FULL named TSV byte-identical vs `m28-census.tsv` + FULL
unnamed TSV byte-identical vs `m34-census.tsv` (mismatch =
stop and table).

## Falsification bars (recorded before running; tables, no verdicts)

Denominators: W = 10 wiped rows (c340: 8, c343: 2), E = 2
dest extras, K = 5 kept rows.

- H1_WIPENEAR (wiped rows are near-misses): share of the 10
  wiped sites with s734-bulk status and |δ_734| ∈ {6,7} is
  ≥ 0.50.
- H2_WIPESET (wiped rows are set changes, not δ changes):
  share of the 10 wiped sites with s734 non-cell status is
  ≥ 0.50.
- H3_DESTNEAR (dest extras are near-misses): share of the 2
  dest-extra sites with s0-bulk status and |δ_s0| ∈ {6,7}
  is ≥ 0.50.
- H4_WIPEGG (wiped rows read ++ gaps): share of the 10 wiped
  sites with ++ gap signs (g_s0 × g_734) is ≥ 0.50.
- H5_VALMED (wiped vs dest are two value populations):
  median |δ_s0| over the 10 wiped rows differs from median
  |δ_734| over the 2 dest extras (meets iff strictly
  unequal — tabled with both medians + ranges).
- H6_COLLISION (the collision reproduces under the M28
  rule): both wiped columns assign to c342 (meets iff
  dest(c340) == 342 AND dest(c343) == 342).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
FULL named TSV byte-identical (764 rows) vs `m28-census.tsv`;
FULL unnamed TSV byte-identical (764 rows) vs
`m34-census.tsv`; UNNAMED domain = pinned 33 (41 union);
s0-bearing-13 row lists exact; c341 empty on all 764; s734
tail 94 + J 0.8846 + moved [340,342,343] + c340/c343 0/0 +
c342 7/5 + no unnamed moves; 734 displacement rows
c340→342 (+2/+0.5/+2) + c343→342 (−1/+3.0/+0) + c342
extra-only; dest rows [26,33] + |δ| [21,11] + gaps
−50,−26/−8,−13; s0 cell 2475 + tail 102 with sub-bins
28+74 and max 47; δ≠0 throughout cell 7 (all analyzed
shapes); P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m28-census.tsv`/`m34-census.tsv` shas +
   Model-0 recompute + cross-checks (§Task 3).
2. Full 764 pass + FULL TSV guards + UNNAMED-domain guard +
   734-row guard + displacement guard + M29-value guard
   (or stop).
3. Task 1: wipe table + dest table + displacement table.
4. Task 2: wiped-value tables + dest-value tables (extras +
   kept) + collision count table.
5. Determinism re-run receipt (Task 1 on s0+734, canonical
   sha).
6. PNG collision map (320x224 native, <5 MB total) to work
   dir; evidence copy ONLY if H6 meets AND H2 meets (the
   collision + set-change structure visible in the
   pre-registered wipe/dest split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 06:41 EDT, stop by 10:41).
