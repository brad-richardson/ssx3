# M35 — Design (recorded before running)

Goal: shape-9 unnamed cells per-site value table (M34 gap 1):
shape 9's 15 unnamed moved cells (310–316, 318, 322, 327, 332,
336, 337, 339, 351) incl. the only mixed delta-5 (c315) and a
tied delta-4 (c314) — located in M34, not attributed at byte
level. Per-site value attribution (δ, gaps, bulk status) for
every missing + extra site in all 15 cells + band/decile joins
+ gap-sign + |δ| stats. Tables, no verdicts. Fully offline: no
lease of any kind, no boots, no harness runs, no fork changes,
no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34.txt` + `/Volumes/Extreme SSD/m34/
m34-census.tsv` (shape-9 unnamed row to reproduce: 15 cells +
standings + deltas — match exactly or table the mismatch and
stop). Work dir: `/Volumes/Extreme SSD/m35/` (new). Evidence:
`local/research/M35/` (committed with `git add -f`, prefix
`[M35]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M34/REPORT.md` (all of it:
gap 1 = this brief — 9's 15 unnamed moved cells incl. mixed
delta-5 c315 + tied delta-4 c314; the 15-set + standings +
deltas to reproduce; M34 census method) plus
`local/research/M27/REPORT.md` (all of it: Task-1 per-site
table + joins method reused verbatim, s0-anchored —
offset/plane/row/col, cross-frame |δ|, signed gaps both
frames; band/decile/streak/carrier joins; H1/H2-style
near-miss shares) plus `local/research/M33/REPORT.md` (§Task 1:
s9 cluster 22 priv + 8 miss per-site tables; cluster privates
21/22 band-1; missings +/+ gaps; extras median 13.0 vs
missings 10.0 — the pooled values this brief splits per
cell).

## Estimator (`m35.py`, `control.py`)

Shared core (M34 `m34.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, PNG writer; M33 `m33.py`
verbatim where reused: `split_planes`, `flat_to_planes`,
`yuv_to_rgb`, `bands_of`/`ROW_BAND`, `p1_gradient` (M18 P1
block verbatim), `attrib_lines`, `posjoin_lines`). Byte offset
o -> row o//1280; Y bytes at o%4==0/2. No P1/carrier/BFS/
displacement/component machinery beyond the M27 joins
(band/decile/streak/carrier — streak/carrier tabled as N/A
off the named set where they read so).

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
  47); s9 117.
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- Shape-9 unnamed moved set (M34-pinned, k=15): [310, 311, 312,
  313, 314, 315, 316, 318, 322, 327, 332, 336, 337, 339, 351].
  Per-cell n/ov pinned from the M34 TSV row (shape=9):
  310:1/0, 311:3/3, 312:2/1, 313:6/4, 314:5/4, 315:8/5,
  316:3/1, 318:3/0, 322:1/0, 327:2/0, 332:3/2, 336:1/0,
  337:2/0, 339:1/0, 351:1/0. s0 n0 pinned: 310:0, 311:4,
  312:3, 313:4, 314:7, 315:7, 316:1, 318:0, 322:0, 327:0,
  332:2, 336:0, 337:0, 339:0, 351:0. Derived standings/deltas
  pinned: 310 d1 extra-only; 311 d1 missing-only; 312 d3
  mixed; 313 d2 extra-only; 314 d4 mixed; 315 d5 mixed;
  316 d2 extra-only; 318 d3 extra-only; 322 d1 extra-only;
  327 d2 extra-only; 332 d1 extra-only; 336 d1 extra-only;
  337 d2 extra-only; 339 d1 extra-only; 351 d1 extra-only.
  Pooled: 22 extras + 8 missings = M33's cluster (row,col)
  sets exactly (§Guards).
- Per-cell sets: extra E_c = s9-tail Y rows in column c minus
  s0 rows; missing M_c = s0-tail Y rows minus s9 rows. The
  per-site row for an extra site o (M27 verbatim): offset,
  plane, (r,c), |δ_9|, s0 status (bulk/non-cell) + |δ_s0| or
  `n/a`, signed gaps g_9 vs g_s0. Mirror for missing sites.
- Near-miss (M27-pinned): other-frame bulk with |δ_other| in
  {6,7}. Far: bulk with |δ_other| <= 5. Non-cell: not cell-7
  on the other frame.
- Position joins are s0-ANCHORED (M27-pinned): band =
  geometry thirds; gradient decile = P1 on s0 mid-Y (edges
  guarded vs m18.txt s0 row); streak column = named-9 set
  {257,277,296,301,321,340,341,342,343} + other; carrier mask
  = M22-verbatim top-10 removed masks + the 701 split.

### Task 1 — per-site value tables (all 15 cells)

Shape-9 unnamed row recomputed from the dumps FIRST (full
764×33 TSV rebuild byte-identical to `m34-census.tsv` +
shape-9 row: 15 cells + standings + deltas — §Guards — or
table the mismatch and stop; no further tasks run).

1. Per-site rows for every missing + extra site in all 15
   cells (`attrib_lines` per cell, tag `s9c{col}`; offset
   order within each cell; M27-style rows both directions
   where mixed). Pooled extra/missing summaries alongside.
2. Near-miss shares per cell (H1/H2-style near/far/non-cell
   counts + shares per cell per direction — full swaps read
   100% non-cell, M29 partials bulk-majority, the s9 cluster
   split: tabled per cell).
3. c315 (mixed delta-5) + c314 (delta-4): full row lists (in
   the per-cell tables) + value stats (|δ| lists/min/med/
   mean/max per direction, gap signs, row lists — the two
   headliners, tabled individually).

### Task 2 — joins (where do unnamed values live?)

1. Band/decile joins per cell set (`posjoin_lines` verbatim,
   s0-anchored): aggregate join (tag UNNAMED-ALL: 22 extras /
   8 missings / 94 shared — the M33 cluster join recomputed,
   tabled for equality) + per-cell joins (tag `s9c{col}join`:
   that cell's extras/missings vs the shared 94 — the
   unnamed-cell equivalent of M33's 21/22 band-1). Streak/
   carrier joins tabled as N/A off the named set where they
   read all-other / all-outside (M33 precedent: other 22/8,
   carrier 0).
2. Gap-sign table (signed gaps both frames per site — pooled
   + per-cell sign counts g_Q +/−/0 × g_O +/−/0 with the
   +/+ share; missings read all +/+ in M27/M29/M33 —
   tabled for unnamed).
3. |δ| stats per cell (|δ| sorted lists + min/med/mean/max
   per cell per direction — M29 extras read 8–9 medians vs
   missing 18.0, M33 cluster extras 13.0 vs missings 10.0 —
   tabled per unnamed cell).

### Task 3 — controls + determinism (M18–M34 precedent)

`control.py` (imports `m35` cell/tail/core; expectations
analytic; pools per M22/M27 receipts: 248 bulk gap≥17 sites,
all 102 tail sites gap≥17):

- C-VAL (known unnamed-cell values): synthetic truth mid' on
  s0: N_priv=6 currently-interior-BULK Y sites with gap≥17
  (first 6 in offset order), injected mid'=blend+8 on even
  (r+c) / blend−8 on odd (|δ|=8, the tail boundary;
  per-site strict-interior check) AND N_miss=4 currently-TAIL
  sites (first 4 in offset order), injected mid'=blend+1
  (fall back to blend−1 per site if +1 is not strictly
  inside — tabled). Shape A = s0 orig, shape B = s0 mid'.
  Recompute cell 7 + tail on B: P_B = T_B − T_A must equal
  the injected 6 exactly, M_B = T_A − T_B must equal the
  injected 4 exactly, J(T_B,T_A) must equal 98/108 = 0.9074
  exactly, per-site |δ| exact (privates 8, missings 1),
  gaps equal on both frames at every injected site
  (v0/full unchanged — tabled), other-frame statuses exact
  (privates bulk on A with original |δ| tabled; missings
  bulk on B), spanned Y-column cells tabled with per-cell
  standings exact (derived from the injection), cell-7 mask
  fixed, all other tail members' δ unchanged.
- Pass = sets + Jaccard + per-site values + gaps +
  standings exact.

Determinism: re-run Task 1 (per-cell per-site rows + pooled
summaries + aggregate join) on s0+9 with fresh loads;
canonical text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s9 triplets +
m15 triplets + top-10 carrier triplets + `m34.txt` +
`m34-census.tsv` shas; triplet fold sha over all 764x3 bins
(M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M34 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_CELLNEAR (extras are near-misses): share of the 22
  unnamed-extra sites with s0-bulk status and |δ_s0| in
  {6,7} is >= 0.50.
- H2_CELLSET (extras are set changes, not δ changes): share
  of the 22 unnamed-extra sites with s0 non-cell status is
  >= 0.50.
- H3_CELLMISS (missings are set changes): share of the 8
  unnamed-missing sites with s9 non-cell status is >= 0.50.
- H4_CELLLOCALIZE (unnamed values localize): |extra band-1
  share − shared band-1 share| >= 0.25, or |extra dec-9
  share − shared dec-9 share| >= 0.25 (either leg meets;
  s0-anchored joins).
- H5_MISSGAP (missings read +/+): share of the 8
  unnamed-missing sites with g_s0 > 0 and g_9 > 0 is
  >= 0.50.
- H6_HEADBULK (headliner delta rows read bulk-majority):
  share of the 9 c314+c315 delta-row sites (4 + 5) with
  bulk status on the other frame is >= 0.50.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 counts s0 2475 exact + s9 2670 exact; tail counts s0
102 exact with sub-bins 28+74 and max 47, s9 117 exact +
J 0.7520 exact; FULL unnamed TSV match (all 764 rows:
tail + J4 + all-33-column n/ov/pres) vs `m34-census.tsv`
(else stop everything); shape-9 moved set == the pinned 15
+ per-cell n/ov + standings + deltas (§Definitions, else
stop everything); pooled extras/missings (row,col) sets ==
M33's cluster sets (22 + 8, else stop everything); s0 P1
edges match m18.txt s0 row; carrier removed counts + bands
(M19 values); d!=0 throughout cell 7 (all analyzed shapes);
P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34.txt`/`m34-census.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + shape-9 row guard (15 cells +
   standings + deltas or stop) + M33 cluster-set guard.
3. Task 1: per-cell per-site tables (15 cells) + pooled
   summaries + headliner (c315/c314) value stats.
4. Task 2: aggregate + per-cell s0-anchored joins +
   gap-sign tables + |δ| stats per cell.
5. Determinism re-run receipt (Task 1 on s0+9, canonical
   sha).
6. PNG value map (s0 geometry; extra sites by other-frame
   status: bulk yellow / noncell red; missing sites: bulk
   cyan / noncell magenta; shared green) to work dir;
   evidence copy ONLY if H4 meets on either leg AND the
   winning leg's majority level (band 1 / dec 9) holds ≥8
   extra sites (the value split visible in the
   pre-registered band/decile split) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 04:20 EDT, stop by 08:20).
