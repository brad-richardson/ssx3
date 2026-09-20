# M43 — Design (recorded before running)

Goal: big-delta fresh columns (M34 gap 3): the 5 delta≥9 cells
are all fresh-column growth — 700-c54 (+10), 733-c323 (+10),
731-c259 (+9), 731-c279 (+9), 733-c303 (+9) — plus 761-c54
(+4); 731/733's moves are their M27/M28 named-swap
destinations. Dest-row listing + per-site value table (|δ|,
bulk status, gaps, signs) for the 5 fresh cells (761-c54,
731-c259, 731-c279, 733-c303, 733-c323; 700-c54 cited WITH
values from M36 by reference, not re-attributed),
side-by-side with 700-c54's uniform-8/bulk/−− values. Is
fresh-column growth values-uniform like c54, or does each
dest cell read its own values? Answer by table. Tables, no
verdicts. Fully offline: no lease of any kind, no boots, no
harness runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (n/ov + miss/extra +
deltas to reproduce — match exactly or table the mismatch and
stop). Work dir: `/Volumes/Extreme SSD/m43/` (new). Evidence:
`local/research/M43/` (committed with `git add -f`, prefix
`[M43]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M34/REPORT.md` (all of it:
gap 3 = this brief — the 5 delta≥9 cells are all fresh-column
growth — 700-c54 (+10), 733-c323 (+10), 731-c259 (+9),
731-c279 (+9), 733-c303 (+9) — plus 761-c54 (+4); 731/733's
moves are their M27/M28 named-swap destinations; big-delta
table: 761 c54 4/0 0/4 d4, 731 c259 9/0 0/9 d9, 731 c279 9/0
0/9 d9, 733 c303 9/0 0/9 d9, 733 c323 10/0 0/10 d10, all
fresh) plus `local/research/M36/REPORT.md` (700-c54's 10 extras
WITH values — rows [245,246,247,252,253,258,259,278,279,283],
all |δ| 8 bulk −− — by reference, do not re-attribute) plus
`local/research/M37/REPORT.md` (761's 4 in-mask tail bytes at
(259,54)/(261,54)/(263,54)/(274,54) — row-list cross-check).

## Estimator (`m43.py`, `control.py`)

Shared core (M36 `m36.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `attrib_lines`,
`gapsign_lines`, `dstats_lines`, `load_triplet`,
`compute_sets_for`, `split_planes`, `flat_to_planes`,
`yuv_to_rgb`, PNG writer). Byte offset o -> row o//1280; Y
bytes at o%4==0/2. No P1/decile/streak/carrier/BFS/
displacement machinery: the brief pins no band/decile/streak/
carrier joins (row-lists + values only), so `compute_dec_masks`
/ `posjoin_lines` / `bands_of` / `ROW_BAND` / `p1_gradient` are
dropped (disclosed here; input integrity still rests on the
triplet fold sha + R_s-vs-loo on all 764 + FULL TSV guard +
Model-0 recompute).

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- d = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so d!=0
  throughout (guard).
- Bulk = cell-7 bytes with |d|<8. Tail = cell-7 bytes with
  |d|>=8. Tail MAP of shape s: T_s = tail boolean mask (N
  bytes). Want: s0 102 (sub-bins 28 in 8–15 + 74 in 16+, max
  47); s761 106; s731 100; s733 100 (M34-pinned).
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- Fresh-cell pins (M34 big-delta table + TSV rows for
  761/731/733, read before running; s0 tail 102 J 1.0000):
  s761 tail 106 J 0.9623, moved [54]: 54: 4/0, n0 0,
  miss/extra/delta 0/4/4 extra-only. Pooled 4+0.
  s731 tail 100 J 0.6833, moved [259,279]: 259: 9/0, n0 0,
  0/9/9 extra-only; 279: 9/0, n0 0, 0/9/9 extra-only.
  Pooled 18+0.
  s733 tail 100 J 0.6694, moved [303,323]: 303: 9/0, n0 0,
  0/9/9 extra-only; 323: 10/0, n0 0, 0/10/10 extra-only.
  Pooled 19+0.
  Grand pooled: 41 extras + 0 missings over 5 cells. All 5
  cells want n0==0 + ov==0 + miss==0 (fresh growth, not
  moves).
- 761 row pins (M37 §Task 2.3 probe, cross-check): 761-c54
  rows [259,261,263,274] (s0 rows [] — fresh). Must
  reproduce or table the mismatch (H1; guard stops Task 2
  value tables on mismatch — the row-list IS the new data).
- 700-c54 citation (M36 §Task 1 headliner, by reference — do
  NOT re-attribute): rows [245,246,247,252,253,258,259,278,
  279,283], extras |δ_700| [8×10] (med 8.0), 10/10 bulk
  (|δ_s0| 6:2 7:8), gaps 10/10 −−. Side-by-side target only.
- Per-cell sets: extra E_c = sQ-tail Y rows in column c minus
  s0 rows (== sQ rows here — s0 rows [] fresh); missing M_c
  = s0 rows minus sQ rows (want empty on all 5). Q in
  {761,731,733}. Per-site row for an extra site o (M36
  verbatim): offset, plane, (r,c), |δ_Q|, s0 status
  (bulk/non-cell) + |δ_s0| or `n/a`, signed gaps g_Q vs g_s0.
- Near-miss (M27-pinned): other-frame bulk with |δ_other| in
  {6,7}. Far: bulk with |δ_other| <= 5. Non-cell: not cell-7
  on the other frame.
- c54-like cell (H5): a dest cell reading all-sites |δ_Q|==8
  AND all-sites bulk-on-s0 AND all-sites −− (fully uniform
  like 700-c54 on all three legs).

### Task 1 — dest-row listing (do the 5 cells reproduce?)

The 5 cells recomputed from the dumps FIRST (FULL 764×33 TSV
rebuild byte-identical to `m34-census.tsv` + each shape's row:
k + cell list + n/ov + standings + deltas — §Guards — or
table the mismatch and stop; no further tasks run).

1. Row-list table: all 5 cells s0-rows (want [] — fresh) vs
   Q-rows vs extra rows (full row lists, the new data;
   `head`-style per-cell rows + pooled counts).
2. Fresh-column proof table: ov==0 + n0==0 + miss==0 per cell
   (fresh growth, not moves — 5/5 want fresh).
3. Cross-check table: 761's 4 rows vs M37's (259,261,263,274)
   (H1 — exact or table the mismatch) + 700-c54's 10 rows
   cited from M36 (do 761's rows overlap c54's? H6 — overlap
   list, numbers only).

### Task 2 — value table (uniform like c54, or per-cell?)

1. Per-site value table: all 41 sites (4+9+9+9+10) with
   offset, |δ_Q|, s0 status + |δ_s0|, signed gaps both
   frames, gap signs (`attrib_lines` per shape × cell, tag
   `s{Q}c{col}`; offset order within each cell; M36-style).
2. Per-cell value stats: |δ| list/med (`dstats_lines`), bulk/
   noncell split (`attrib` summaries), gap-sign split
   (`gapsign_lines`) per cell (5 rows) + pooled-41 lines.
3. c54 side-by-side: each cell's stats vs 700-c54's
   uniform-8/bulk/−− (numbers only — uniform or not? per-leg
   per-cell table + H5 measurement).

### Task 3 — controls + determinism (M18–M42 precedent)

`control.py` (imports `m43` cell/tail/core; expectations
analytic):

- C-FRESH (known fresh cells, mimics dest-row growth):
  synthetic truth mid' on s0: N_priv=5 currently-interior-
  BULK Y sites in Y columns bearing NO s0 tail (first 5 in
  offset order passing the per-site strict-interior check),
  injected mid'=blend+8 on even (r+c) / blend−8 on odd
  (|δ|=8, the tail boundary), spanning ≥1 fresh column
  (tabled how many + which columns + per-column rows — the
  KNOWN row-lists). Shape A = s0 orig, shape B = s0 mid'.
  Recompute cell 7 + tail on B: P_B = T_B − T_A must equal
  the injected 5 exactly, M_B = T_A − T_B must be empty
  exactly, J(T_B,T_A) must equal 102/107 = 0.9533 exactly,
  per-site |δ| exact (8), gaps equal on both frames at every
  injected site (v0/full unchanged — tabled), other-frame
  statuses exact (privates bulk on A with original |δ|
  tabled), per-column row-lists + standings exact
  (extra-only on fresh columns, derived from the injection),
  cell-7 mask fixed, all other tail members' δ unchanged.
- Pass = sets + Jaccard + row-lists + per-site values + gaps
  + standings exact. Pool shortfall (fewer than 5 injectable
  bulk-Y sites in no-s0-tail columns) = tabled RED,
  cannot-inject (M38/M39/M40/M41/M42 precedent).

Determinism: re-run Task 1 (per-shape per-cell row-lists +
fresh-proof rows + per-site value rows + per-cell stats +
pooled summaries) on s0+761+731+733 with fresh loads;
canonical text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s761 + s731 +
s733 triplets + m15 triplets + `m34-census.tsv` sha (want
`83482d1f…926c8aa8` 163262 B); triplet fold sha over all
764x3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M42 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned from the M34 TSV: 41 pooled extra sites + 0
missings over 5 fresh cells (s761: 4+0; s731: 18+0; s733:
19+0). 700-c54's uniform-8/bulk/−− cited from M36 (H2/H3/H4
pool the 41 against c54's legs; H5 tests per-cell full match).

- H1_761ROWS (761 rows reproduce M37): 761-c54's 4 rows ==
  [259,261,263,274] exactly (sorted order).
- H2_UNIFORM8 (dest values read |δ| 8): share of the 41
  pooled dest extra sites with |δ_Q| == 8 is >= 0.50.
- H3_BULK (dest values sit on s0 bulk): share of the 41
  pooled dest extra sites with s0-bulk status is >= 0.50.
- H4_GAPMM (dest values read −−): share of the 41 pooled
  dest extra sites with g_Q < 0 and g_s0 < 0 is >= 0.50.
- H5_C54LIKE (cells read fully c54-like): ≥3 of the 5 dest
  cells read all-sites |δ_Q|==8 AND all-sites bulk-on-s0 AND
  all-sites −− (per §Definitions c54-like).
- H6_ROWOVERLAP (761 rows recur in c54): ≥1 of 761's 4 rows
  recurs among 700-c54's cited 10 rows.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact (s761/s731/s733 cell counts NOT
pinned — no prior report lists them — tabled as measured
with d!=0 throughout); tail counts s0 102 exact with
sub-bins 28+74 and max 47, s761 106 exact, s731/s733 100
exact + J 0.9623/0.6833/0.6694 exact; FULL unnamed TSV match
(all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv` (else stop everything); 761/731/733 moved
sets == the pinned 1/2/2 + per-cell n/ov + standings +
deltas (§Definitions, else stop everything); pooled
per-shape extra/missing counts == 4+0 / 18+0 / 19+0 (else
stop everything); all 41 pooled sites Y-plane (tabled; any
non-Y = stop and table); P(δ>0)==M19/M20 0.8093 on s0;
`loo.txt` 764 rows + top-10 shapes/shares; self Jaccard ==
1.0.

## Run protocol

1. Input shas + `m34-census.tsv` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + 761/731/733 row guards (k 1/2/2
   + standings + deltas or stop) + pooled-count guards.
3. Task 1: per-cell row-lists (5 cells) + fresh-proof table +
   761-vs-M37 cross-check + 761-vs-c54 overlap (canon for
   determinism).
4. Task 2: per-site value tables (41 sites) + per-cell stats
   + pooled-41 stats + c54 side-by-side.
5. Determinism re-run receipt (Task 1+2 lines on
   s0+761+731+733, canonical sha).
6. PNG dest-cell map (s0 geometry; dest extra sites:
   c54-like yellow / non-c54-like red per §Definitions;
   shared green — per-shape maps; at most the 733 map) to
   work dir; evidence copy ONLY if H1 meets AND H5 reads
   split (1–4 of 5 cells fully c54-like, i.e. neither 0 nor
   5 — the uniform-vs-per-cell split visible in the
   pre-registered per-cell coloring) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 05:49 EDT, stop by 09:49).
