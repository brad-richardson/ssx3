# M36 — Design (recorded before running)

Goal: still-below unnamed cells per-site value attribution
(M34 gap 2): shapes 2/3/700's unnamed moved cells at k 6/7/8
(J 0.9159/0.9340/0.8462) — located in M34, not attributed at
byte level. Per-site value attribution (δ, gaps, bulk status)
for every missing + extra site in all 21 cells + band/decile
joins + gap-sign + |δ| stats. Tables, no verdicts. Fully
offline: no lease of any kind, no boots, no harness runs, no
fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34.txt` + `/Volumes/Extreme SSD/m34/
m34-census.tsv` (2/3/700 unnamed rows to reproduce: k 6/7/8 +
cell lists + standings + deltas — match exactly or table the
mismatch and stop). Work dir: `/Volumes/Extreme SSD/m36/` (new).
Evidence: `local/research/M36/` (committed with `git add -f`,
prefix `[M36]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 4 = this brief — 2/3/700 move unnamed at k 6/7/8
(J 0.9159/0.9340/0.8462), their below-but-still divergence
located in unnamed columns by M34, not attributed; the M35
Task-1/2 method reused verbatim per shape, s0-anchored —
per-site rows, near-miss shares, headliner treatment,
band/decile/streak/carrier joins, gap-sign, |δ| stats; the
shape-9 reads this brief tables 2/3/700 against: extras
1/14/7 near/far/noncell, missings 2/2/4, 21/22 band-1,
8/8 ++ missings, extras med 13.0 / missings med 10.0).

## Estimator (`m36.py`, `control.py`)

Shared core (M35 `m35.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `attrib_lines`,
`posjoin_lines`, `gapsign_lines`, `dstats_lines`, PNG writer;
M33 `m33.py` verbatim where reused: `split_planes`,
`flat_to_planes`, `yuv_to_rgb`, `bands_of`/`ROW_BAND`,
`p1_gradient` (M18 P1 block verbatim)). Byte offset o -> row
o//1280; Y bytes at o%4==0/2. No P1/carrier/BFS/
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
  47); s2 103; s3 103; s700 114 (M34-pinned).
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- Still-below unnamed moved sets (M34-pinned): s2 k=6 [311,
  312, 313, 314, 332, 339]; s3 k=7 [311, 313, 314, 316, 332,
  336, 339]; s700 k=8 [38, 54, 299, 311, 313, 314, 332, 620].
  21 cells total. Per-cell n/ov pinned from the M34 TSV rows
  (shapes 2/3/700, read before running):
  s2: 311:5/4, 312:2/2, 313:4/3, 314:6/6, 332:3/1, 339:1/0;
  s3: 311:5/4, 313:3/3, 314:6/6, 316:2/1, 332:1/1, 336:1/0,
  339:1/0;
  s700: 38:0/0, 54:10/0, 299:1/0, 311:5/4, 313:5/4, 314:6/6,
  332:2/1, 620:1/0.
  s0 n0 pinned (M34 s0-bearing table): 38:1, 54:0, 299:0,
  311:4, 312:3, 313:4, 314:7, 316:1, 332:2, 336:0, 339:0,
  620:0. Derived standings/deltas pinned (miss/extra/delta/
  standing; miss=n0−ov, extra=n−ov):
  s2: 311 d1 extra-only (0/1); 312 d1 missing-only (1/0);
  313 d2 mixed (1/1); 314 d1 missing-only (1/0); 332 d3
  mixed (1/2); 339 d1 extra-only (0/1). Pooled: 4 miss + 5
  extra = 9 sites.
  s3: 311 d1 extra-only (0/1); 313 d1 missing-only (1/0);
  314 d1 missing-only (1/0); 316 d1 extra-only (0/1); 332 d1
  missing-only (1/0); 336 d1 extra-only (0/1); 339 d1
  extra-only (0/1). Pooled: 3 miss + 4 extra = 7 sites.
  s700: 38 d1 missing-only wipe (1/0); 54 d10 extra-only
  (0/10); 299 d1 extra-only (0/1); 311 d1 extra-only (0/1);
  313 d1 extra-only (0/1); 314 d1 missing-only (1/0); 332 d2
  mixed (1/1); 620 d1 extra-only (0/1). Pooled: 3 miss + 15
  extra = 18 sites.
  Grand pooled: 10 miss + 24 extra = 34 sites over 21 cells.
- Per-cell sets: extra E_c = sQ-tail Y rows in column c minus
  s0 rows; missing M_c = s0-tail Y rows minus sQ rows (Q in
  {2,3,700}). The per-site row for an extra site o (M27/M35
  verbatim): offset, plane, (r,c), |δ_Q|, s0 status
  (bulk/non-cell) + |δ_s0| or `n/a`, signed gaps g_Q vs g_s0.
  Mirror for missing sites.
- Near-miss (M27-pinned): other-frame bulk with |δ_other| in
  {6,7}. Far: bulk with |δ_other| <= 5. Non-cell: not cell-7
  on the other frame.
- Position joins are s0-ANCHORED (M27-pinned): band =
  geometry thirds; gradient decile = P1 on s0 mid-Y (edges
  guarded vs m18.txt s0 row); streak column = named-9 set
  {257,277,296,301,321,340,341,342,343} + other; carrier mask
  = M22-verbatim top-10 removed masks + the 701 split.
- Shape-700 headliner (k=8 max of the three + J 0.8462
  lowest): full row lists + value stats tabled individually
  (M35's c314/c315 treatment), incl. the c54 +10 fresh-column
  cell individually.

### Task 1 — per-site value tables (all 21 cells, 3 shapes)

2/3/700 unnamed rows recomputed from the dumps FIRST (full
764×33 TSV rebuild byte-identical to `m34-census.tsv` + each
shape's row: k + cell list + n/ov + standings + deltas —
§Guards — or table the mismatch and stop; no further tasks
run).

1. Per-site rows for every missing + extra site in all 21
   cells (`attrib_lines` per shape × cell, tag `s{Q}c{col}`;
   offset order within each cell; M27-style rows both
   directions where mixed). Per-shape pooled extra/missing
   summaries + grand pooled summaries alongside.
2. Near-miss shares pooled + per shape (H1/H2/H3-style
   near/far/non-cell counts + shares per cell per direction
   per shape; shape-9 reads extras 1/14/7, missings 2/2/4 —
   table 2/3/700's).
3. Shape-700 headliner: full row lists (in the per-cell
   tables) + value stats (|δ| lists/min/med/mean/max per
   direction, gap signs, row lists — all 8 cells tabled
   individually, with the c54 +10 cell split out).

### Task 2 — joins (where do still-below values live?)

1. Band/decile joins pooled + per shape (`posjoin_lines`
   verbatim, s0-anchored): aggregate joins per shape (tags
   `s2all`/`s3all`/`s700all`: that shape's extras/missings vs
   its own shared set) + grand pooled extras/missings table
   + per-cell joins (tag `s{Q}c{col}join`: that cell's
   extras/missings vs the shape's shared set). Streak/
   carrier joins tabled as N/A off the named set where they
   read all-other / all-outside (M35 precedent: other 22/8,
   carrier 0).
2. Gap-sign table (signed gaps both frames per site — pooled
   + per shape + per-cell sign counts g_Q +/−/0 × g_O +/−/0
   with the +/+ share; shape-9 missings read 8/8 ++ —
   table 2/3/700's).
3. |δ| stats pooled + per shape + per cell (|δ| sorted lists
   + min/med/mean/max per cell per direction — shape-9
   extras med 13.0 / missings med 10.0 — table 2/3/700's +
   largest-|δ| sites).

### Task 3 — controls + determinism (M18–M35 precedent)

`control.py` (imports `m36` cell/tail/core; expectations
analytic; pools per M22/M27 receipts: 248 bulk gap≥17 sites,
all 102 tail sites gap≥17):

- C-VAL (known still-below values): synthetic truth mid' on
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

Determinism: re-run Task 1 (per-shape per-cell per-site rows
+ per-shape pooled summaries + headliner stats + aggregate
joins) on s0+2/3/700 with fresh loads; canonical text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s2 + s3 + s700
triplets + m15 triplets + top-10 carrier triplets + `m34.txt`
+ `m34-census.tsv` shas; triplet fold sha over all 764x3 bins
(M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M35 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Pooled denominators pinned from the M34 TSV: 24 extras + 10
missings over 21 cells (s2: 5+4; s3: 4+3; s700: 15+3).

- H1_STILLNEAR (extras are near-misses): share of the 24
  pooled still-below extra sites with s0-bulk status and
  |δ_s0| in {6,7} is >= 0.50.
- H2_STILLSET (extras are set changes, not δ changes): share
  of the 24 pooled still-below extra sites with s0 non-cell
  status is >= 0.50.
- H3_STILLMISS (missings are set changes): share of the 10
  pooled still-below missing sites with sQ non-cell status
  (each missing judged on its own shape Q) is >= 0.50.
- H4_STILLLOCALIZE (still-below values localize): evaluated
  PER SHAPE (that shape's extras vs its own shared set,
  s0-anchored): |extra band-1 share − shared band-1 share|
  >= 0.25, or |extra dec-9 share − shared dec-9 share|
  >= 0.25 (either leg meets on any of the 3 shapes; all 6
  legs tabled; grand-pooled extra band-1/dec-9 shares
  table-only).
- H5_STILLMISSGAP (missings read +/+): share of the 10
  pooled still-below missing sites with g_s0 > 0 and g_Q > 0
  (each missing judged on its own shape Q) is >= 0.50.
- H6_700BULK (700 headliner delta rows read bulk-majority):
  share of shape 700's 18 delta-row sites (3 miss + 15
  extra) with bulk status on the other frame is >= 0.50
  (c54's 10 extras split out alongside).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact (s2/s3/s700 cell counts NOT pinned
— no prior report lists them — tabled as measured with d!=0
throughout); tail counts s0 102 exact with sub-bins 28+74
and max 47, s2/s3 103 exact, s700 114 exact + J 0.9159/
0.9340/0.8462 exact; FULL unnamed TSV match (all 764 rows:
tail + J4 + all-33-column n/ov/pres) vs `m34-census.tsv`
(else stop everything); 2/3/700 moved sets == the pinned
6/7/8 + per-cell n/ov + standings + deltas (§Definitions,
else stop everything); pooled per-shape extra/missing counts
== 5+4 / 4+3 / 15+3 (else stop everything); all 34 pooled
sites Y-plane (tabled; any non-Y = stop and table); s0 P1
edges match m18.txt s0 row; carrier removed counts + bands
(M19 values); d!=0 throughout cell 7 (all analyzed shapes);
P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34.txt`/`m34-census.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + 2/3/700 row guards (k 6/7/8 +
   standings + deltas or stop) + pooled-count guards.
3. Task 1: per-shape per-cell per-site tables (21 cells) +
   per-shape pooled + grand pooled summaries + 700
   headliner value stats.
4. Task 2: per-shape aggregate + per-cell s0-anchored joins +
   gap-sign tables + |δ| stats per shape per cell.
5. Determinism re-run receipt (Task 1 on s0+2/3/700,
   canonical sha).
6. PNG value map (s0 geometry; extra sites by other-frame
   status: bulk yellow / noncell red; missing sites: bulk
   cyan / noncell magenta; shared green — per-shape maps; at
   most the 700 map) to work dir; evidence copy ONLY if H4
   meets on some shape AND that shape's winning leg majority
   level (band 1 / dec 9) holds ≥8 of that shape's extra
   sites (the value split visible in the pre-registered
   band/decile split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 04:27 EDT, stop by 08:27).
