# M40 — Design (recorded before running)

Goal: shape-9 per-cell standing asymmetry (M35 gap 1): shape 9's
8 missings concentrate in 4/15 cells (311/312/314/315) while 11
cells read extra-only; the missing sides read all-bulk in
c312/c315 vs all-noncell in c311/c314 (M35 §Step 3). Row-list +
value comparison across the 4 missing-bearing cells: is the
bulk/noncell split row-deep (the cells' extras and row-lists
split the same way) or missing-only (extra sides + row shapes
agree across the 4 cells)? Answer by table: per-cell row-lists
+ per-site values + standing splits, c311 vs c312 vs c314 vs
c315. Tables, no verdicts. Fully offline: no lease of any
kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (FULL TSV guard,
M34–M39 precedent), `/Volumes/Extreme SSD/m35/m35.txt` (the 4
cells to reproduce — match exactly or table the mismatch and
stop). Work dir: `/Volumes/Extreme SSD/m40/` (new). Evidence:
`local/research/M40/` (committed with `git add -f`, prefix
`[M40]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 1 = this brief — 4 missing-bearing cells 311/312/314/315
with standings + deltas + per-site |δ|/status/gap tables this
brief reproduces; c314's 3 missings all noncell at |δ|
12/23/45 vs c315's 2 all bulk at 10/10; headliner row-lists
for c314/c315) plus `local/research/M39/REPORT.md` (all of it:
comparison precedent — missing-side agreement vs extra-side
split; corrected pooled universe 24 = c54's 10 + 14 others).

## Estimator (`m40.py`, `control.py`)

Shared core (M39 `m39.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `load_triplet`,
`compute_sets_for`, `split_planes`, `flat_to_planes`,
`yuv_to_rgb`). Byte offset o -> row o//1280; Y bytes at o%4==0/2.
No P1/decile/streak/carrier/BFS/displacement machinery: the
brief pins no band/decile/streak/carrier joins, so that
machinery stays out (disclosed here; input integrity still
rests on the triplet fold sha + R_s-vs-loo on all 764 + FULL
TSV guard + Model-0 recompute).

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
  47); s9 117 (M35-pinned).
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- Shape-9 unnamed moved set (M34/M35-pinned, k=15): [310, 311,
  312, 313, 314, 315, 316, 318, 322, 327, 332, 336, 337, 339,
  351] with per-cell n/ov + n0 + standings + deltas per the
  M35 REPORT Task-1 table (row guard covers all 15 per M38/M39
  precedent — the brief's 4 cells are the Task-1/2 universe).
- Brief universe (4 cells = the missing-bearing cells):
  s9 c311 (missing-only d1) + c312 (mixed d3) + c314 (mixed
  d4) + c315 (mixed d5). 5 extra sites + 8 missing sites =
  13 sites.
- Row-list pins (M35 REPORT + m35.txt headliners):
  c314: s0 [269,276,277,278,287,288,289], s9
  [246,276,277,278,287], miss [269,288,289], extra [246];
  c315: s0 [266,267,268,273,274,275,276], s9
  [245,267,268,274,275,276,289,290], miss [266,273], extra
  [245,289,290]. c311/c312: s0 rows MEASURED-not-pinned (M38
  s700-held / M39 s0c316 precedent — M35 pins n0 + the
  extra/miss rows, not the overlap rows): c311 n0=4 miss
  [296] extra []; c312 n0=3 miss [299,301] extra [248];
  guard n0 exact + extra/miss rows exact + n/ov exact.
- Value pins (M35 extra/missing tables, the brief's stop
  rule; 5 extras (r,c) -> offset/ad9/ostat/adO/g9/gO):
  (248,312) 318064/13/bulk/1/33/10;
  (246,314) 315508/13/bulk/1/32/9;
  (245,315) 314230/13/bulk/2/60/6;
  (289,315) 370550/16/noncell/n/a/−34/0;
  (290,315) 371830/11/noncell/n/a/−26/−2.
  8 missings (r,c) -> offset/adS0/qstat/adQ/gS0/g9:
  (296,311) 379502/10/noncell/n/a/24/7;
  (299,312) 383344/10/bulk/6/22/16;
  (301,312) 385904/9/bulk/7/28/28;
  (269,314) 344948/12/noncell/n/a/41/29;
  (288,314) 369268/45/noncell/n/a/107/84;
  (289,314) 370548/23/noncell/n/a/54/31;
  (266,315) 341110/10/bulk/2/64/46;
  (273,315) 350070/10/bulk/3/23/23.
  Standings: c311 missing-only d1 (1/0); c312 mixed d3
  (2/1); c314 mixed d4 (3/1); c315 mixed d5 (2/3).
- Missing-side groups: BULK-side cells c312/c315 (4 missing
  sites) vs NONCELL-side cells c311/c314 (4 missing sites).
  Extra-side grouping follows the same cell line: extras of
  bulk-side cells (c312's 1 + c315's 3 = 4) vs extras of
  noncell-side cells (c314's 1; c311 has none — tabled).
- Gap signs: g_Q × g_O per site (extra: g9×g_s0; missing:
  g_s0×g9). M35 reads 8/8 ++ on missings; extras read
  ++/++/++/−−/−0 across the 5 brief extras — reproduced,
  not assumed.
- Row shape: n0/n/ov per cell (c311 4/3/3, c312 3/2/1, c314
  7/5/4, c315 7/8/5). Separation = both bulk-side values on
  one side of both noncell-side values (strict, either
  direction).

### Task 1 — 4-cell recompute (do the cells reproduce?)

The 4 missing-bearing cells recomputed from the dumps FIRST
(§Guards — row lists, standings, deltas, per-site |δ|/status/
gaps must match M35 exactly — or table the mismatch and stop;
no further tasks run).

1. Row-list table: all 4 cells s0-rows vs s9-rows vs
   extra/missing rows (M35-headliner style).
2. Standing table: c311 missing-only d1 vs c312/c314/c315
   mixed d3/d4/d5 (extra counts + missing counts + deltas).
3. Value table: per-site |δ_9|/|δ_s0|, statuses, signed gaps,
   gap signs for all 4 cells' sites (8 missings + 5 extras).

### Task 2 — asymmetry comparison (row-deep or missing-only?)

1. Missing-side comparison: all-bulk c312/c315 (|δ|, gaps,
   signs) vs all-noncell c311/c314 (same columns —
   med/match per site, numbers only).
2. Extra-side comparison: c312's 1 + c314's 1 + c315's 3
   extras (|δ|, bulk status, gaps, signs — do the extra
   sides split along the cells' missing-side bulk line?).
3. Row-shape comparison: n0/n/ov per cell (does s0's row
   count or the overlap predict the bulk/noncell side?).

### Task 3 — controls + determinism (M18–M39 precedent)

`control.py` (imports `m40` cell/tail core; expectations
analytic):

- C-SPLIT (known split cells, mimics the bulk-vs-noncell
  missing split): synthetic truth mid' on s0: N_BULK=2 known
  all-bulk-missing cells (1 injected bulk landing each at a
  currently-TAIL Y site, mid'=blend+1 falling back to
  blend−1 per site if +1 is not strictly inside) +
  N_NONCELL=2 known all-noncell-missing cells (1 injected
  noncell landing each at a currently-TAIL Y site,
  mid'=endpoint v0[o] falling back to full[o] per site —
  endpoint reads noncell by construction since strict
  interior fails; verified per site after recompute), all 4
  cells in distinct Y columns (columns assigned greedily in
  numeric order, tabled). Shape A = s0 orig, shape B = s0
  mid'. Recompute cell 7 + tail on B: per-cell standings
  must equal the injected 4×missing-only delta-1 exactly,
  per-site values exact (bulk landings |δ|=1 bulk on B;
  noncell landings status noncell on B), gaps equal on both
  frames at every injected site (v0/full unchanged —
  tabled), J(T_B,T_A) must equal 98/102 exactly, row-lists
  exact per cell, cell-7 mask = maskA minus exactly the 2
  injected noncell sites, all other tail members' δ
  unchanged.
- Pass = standings + row-lists + per-site values + gaps
  exact. Pool shortfall (no greedy assignment spans 2+2
  cells) = tabled RED, cannot-inject (M38/M39 precedent).

Determinism: re-run Task 1 (row-lists + standings + per-site
values for the 4 cells) on s0+9 with fresh loads; canonical
text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s9 triplets +
m15 triplets + `m34-census.tsv` + `m35.txt` shas (m35.txt want
`ff29739c…49349c` 69947 B, read-only pre-measurement);
triplet fold sha over all 764x3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M39 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned from M35: s9's 4 missing-bearing cells (c311
missing-only d1, c312/c314/c315 mixed d3/d4/d5); 5 extra
sites + 8 missing sites = 13 sites. H1/H2/H7 are reproduce
bars; H3–H6 are row-deep-vs-missing-only agreement bars
(meet = the facet agrees across the bulk/noncell cell line,
i.e. missing-only on that facet; miss = the facet splits
with the line, i.e. row-deep on that facet — tabled, no
verdicts).

- H1_ROW_REPRO (row-lists reproduce): 4/4 brief cells read
  the §Definitions row pins exactly (c314/c315 full
  s0-rows + s9-rows; c311/c312 n0 + extra/miss rows with
  s0-rows measured; n/ov exact on all 4).
- H2_VALUE_REPRO (values reproduce): 13/13 brief sites read
  the §Definitions value pins exactly (offset + |δ| +
  status + signed gaps both frames).
- H3_MISS_AD_DEEP (missing magnitudes agree): |median
  bulk-side-missing |δ_s0| − median noncell-side-missing
  |δ_s0|| ≤ 2.
- H4_MISS_SIGN_DEEP (missing signs agree): |++ share bulk-side
  missings − ++ share noncell-side missings| ≤ 0.25.
- H5_EXTRA_SIGN_DEEP (extra signs agree): |++ share extras of
  bulk-side cells − ++ share extras of noncell-side cells|
  ≤ 0.25 (noncell-side extras n=1 — 1-site granularity
  tabled).
- H6_ROW_PREDICT (row shape predicts the side): n0 separates
  the bulk-side cells from the noncell-side cells exactly
  OR the overlap separates them exactly (either leg meets).
- H7_CELL_PURITY (missing sides read pure): each of the 4
  brief cells' missing side reads all-bulk or all-noncell
  (4/4 pure).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact (s9 cell count tabled as measured,
must equal M35's measured 2670 or table the mismatch and
stop, with d!=0 throughout); tail counts s0 102 exact with
sub-bins 28+74 and max 47, s9 117 exact + J 0.7520 exact;
FULL unnamed TSV match (all 764 rows: tail + J4 + all-33-column
n/ov/pres) vs `m34-census.tsv` (else stop everything); s9 moved
set == the pinned 15 + per-cell n/ov + standings + deltas
(else stop everything); pooled per-shape extra/missing counts
== 22+8 (else stop everything); the 4 brief cells' row pins
== §Definitions (else stop everything); all 13 brief sites'
(offset + |δ| + status + gaps) == pins (else stop everything);
all 13 brief sites Y-plane (tabled; any non-Y = stop and
table); P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34-census.tsv`/`m35.txt` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + s9 row guard (k 15 +
   standings + deltas or stop) + pooled-count guard +
   brief row pins + 13-site value pins (or stop).
3. Task 1: row-list table (4 cells) + standing table +
   value table (13 sites).
4. Task 2: missing-side comparison + extra-side comparison
   + row-shape comparison (n0/n/ov per cell + separation
   legs).
5. Determinism re-run receipt (Task 1 on s0+9, canonical
   sha).
6. PNG asymmetry map (s0 geometry; bulk-side missings cyan /
   noncell-side missings magenta / bulk-side extras green /
   noncell-side extras red) to work dir; evidence copy ONLY
   if H1 meets AND H2 meets AND exactly one of {H3, H4}
   meets (the missing-side magnitude-vs-sign agreement
   asymmetry visible in the pre-registered
   bulk-vs-noncell coloring) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 05:18 EDT, stop by 09:18).
