# M63 — Design (recorded before running)

Goal: interval-head bulk pair neighborhood census (M62 gap 1,
taken on orchestrator judgment): m15 (323,311) +3 and (324,311)
+1, both dec 0 — the only bulk in 48 M62 interval probes, 1–2
rows below the 322 flank. Row-323/324 neighborhood bulk census
across neighboring columns (310/311/312/313/314/315 + any union
col with rows 323–324 in tail) — is the head bulk pair
column-local to c311, and what do the same rows carry on
neighbors (bulk? noncell? tail? what δ?)? Answer by table.
Tables, no verdicts. Fully offline: no lease of any kind, no
boots, no harness runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles + tails + s0 P1 edges),
`/Volumes/Extreme SSD/m62/m62.txt` (interval tables to
reproduce — match exactly per §Guards or table the mismatch
and stop). Work dir: `/Volumes/Extreme SSD/m63/` (new).
Evidence: `local/research/M63/` (committed with
`git add -f`, prefix `[M63]`, trailer `Orchestrated-By: Muse
Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M62/REPORT.md` (all of it:
flanks 322:+10/d0 + 335:+46/d3 / 319:+9/d1 + 341:+14/d1;
interval 323–334: m15 c311 2 bulk (323:+3/d0, 324:+1/d0) +
10 noncell vs m15 c312 12 noncell vs s0 12+12 noncell;
decspans 3/3; hole join 0.1667 vs 0.0038; M62 gap 1 = this
brief) plus `local/research/M61/REPORT.md` (all of it: the
pair c311 6/0 +129 / c312 13/10 +130, spans nested 19-in-63,
site-29, decpair, rowgeom, runs, seats) plus
`local/research/M59/REPORT.md` (all of it: column signs —
16 all-pos + 10 all-neg + c312 split + 6 s0-only; dec-1
cols 307/309/310/311/312/313/315).

## Estimator (`m63.py`, `control.py`)

Shared core (M62 `m62.py` verbatim where reused: YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median`
(halves away from zero), `hole_ranges`, `off_y`
(o=r*1280+(c//2)*4+(0 if c even else 2)), `y_col_dict`
(tail-Y column profiles sorted by row), `far_info`
(nearest-neighbor row gap, singleton N/A), `aux_dist`,
`pooled_d`, `hump_metrics` (first-tie argmax peak),
`bands_of`/`ROW_BAND` (geometry thirds via
`np.array_split(arange(448),3)` -> band0 r0-149, band1 r150-298,
band2 r299-447), `p1_gradient` (M18 P1 block verbatim:
|gx|+|gy| on s0 mid-Y, quantile edges, `digitize` deciles),
carrier removed masks (res0 & ~ress on Y, M22-verbatim),
`seat_of`, `decile_hist`, `tail_y_sites`, `off51_select`,
`col_counts`, `band_hist`, `unanimity_rows`, `span_rows`,
`runs_rows`, `dprof_rows`, `decpair_rows`, `rowgeom_rows`,
`seatdist_rows`, `cell_status`). Byte offset o -> row o//1280; Y
bytes at o%4==0/2.

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- d = mid - blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so d!=0
  throughout (guard) — every site reads strictly pos or neg.
- Bulk = cell-7 bytes with |d|<8 (want 2373 s0 / 2405 m15).
  Tail = cell-7 bytes with |d|>=8 (want 102 s0 / 134 m15; s0
  sub-bins 28 in 8-15 + 74 in 16+, m15 50 + 84; max 47/48).
- Tail-Y = tail bytes on the Y plane (expect 102/0/0 s0 +
  134/0/0 m15; non-Y tabled, census-gating disclosed).
- Column membership = all tail-Y sites with Y-column == c.
- Seat (s0-anchored, M33/M58-verbatim): band = ROW_BAND[r];
  decile = s0 mid-Y P1 decile at (r,c) (`dec_s0[r,c]`,
  edges guarded vs m18 constants); streak = Y-column in the
  named-9 set {257,277,296,301,321,340,341,342,343} else
  `other`; carrier = inside/outside each M22-verbatim top-10
  removed mask (shapes [694,693,701,368,369,366,370,376,748,
  750]) + the 701 split (in/out); peak seat = column-frame
  first-tie argmax peak row (`hump_metrics` verbatim),
  at-peak? tabled per site.
- Head pair = m15 rows 323–324 on c311/c312 (the M62
  interval-head rows: bulk +3/+1 on c311, noncell on c312).
- Neighborhood rows = {323, 324} (both frames probed; m15
  primary, s0 auxiliary).
- Neighbor columns = 310/311/312/313/314/315 (the brief's
  named set) + every other union column probed at rows
  323–324 (the row slices cover ALL 33 union cols, so any
  union col with rows 323–324 in tail/bulk is found by
  table, not by pre-listing).
- Neighborhood probe (dump path, `cell_status` verbatim):
  for a Y (row, col), the byte offset `off_y` reads noncell
  (mask False) vs bulk (mask True, |d|<8) vs tail (mask True,
  |d|>=8), with delta (None when noncell) + decile + band.
- Probe-d convention (disclosed): probes are not tail
  sites, so `far_info` d does not apply; the tabled d is
  the nearest-m15-tail-row distance on the SAME column
  (min |r−x| over the column's m15 tail-Y rows; None when
  the column has no m15 tail) with lo = max tail row ≤ r
  (or None) and hi = min tail row ≥ r (or None). Uniform
  for bulk/noncell/tail probes.
- Row slice (factored, control-covered): per-column probes
  at one fixed row over a column list.
- Neighborhood census (factored, control-covered):
  per-column {rows, probes, bulk/noncell/tail row lists,
  counts, deciles row order, decspan, dechist} over rows
  323–324 (= `interval_census` with row_lo/hi 323/324).
- Shared tail S = T_s0 ∩ T_m15 (Y-plane intersection).
  Pooled = multiset union (disclosed; Jaccard tabled).

M62 pins (must reproduce or stop, §Guards):

- Pair margins (col: s0_n/m15_n/pos/neg/min/max/sum/class):
  - 311: 4/6/6/0/+9/+46/+129/all-pos.
  - 312: 3/23/13/10/−9/+33/+130/split.
- Head bulk (row: kind/delta/dec/band, m15):
  - (323,311): bulk/+3/d0/band2; (324,311): bulk/+1/d0/band2.
  - (323,312): noncell/dec3/band2; (324,312): noncell/dec3/band2.
- The other 44/48 M62 interval probes noncell (rows 325–334
  both cols both frames + rows 323–324 on s0 both cols):
  full 48-probe (kind,delta,dec,band) set vs `m62.txt`
  interval lines.
- c311 m15 sites (row:delta/dec, row order, n=6):
  317:+9/d5 320:+22/d1 321:+20/d0 322:+10/d0 335:+46/d3
  336:+22/d3.
- c312 m15 sites (row:delta/dec, row order, n=23):
  316:+11/d7 317:+20/d5 318:+19/d1 319:+9/d1 341:+14/d1
  342:+22/d3 343:+9/d3 353:−9/d0 354:−9/d0 355:−9/d0
  356:−9/d0 362:−8/d3 363:−8/d4 364:−9/d3 365:−9/d0
  366:−9/d0 367:−8/d0 369:+14/d3 373:+33/d1 374:+15/d1
  377:+18/d0 378:+23/d1 379:+10/d3.

Neighborhood helpers (factored for the control to import):

- `interval_census(row_lo, row_hi, cols, status)`: M62-verbatim
  (see M62 DESIGN.md). Dump path calls it with rows 323–324
  + all 33 union cols + status maps built from `cell_status`
  on m15 (primary) and s0 (auxiliary); control path calls
  the same function with a synthetic status map (identical
  code path).
- `row_slice(row, cols, status)`: row int; cols list;
  status = {(r,c): {kind, delta, dec, band}}. Returns
  {col: {kind, delta, dec, band}} sorted by col. Pure
  function of (row, cols, status).
- Dump path calls row_slice with rows 323/324 + all 33
  union cols + the m15/s0 status maps; control path calls
  the same function with the synthetic status map.

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float shares printed `:.4f`.

### Task 1 — pair reproduction (does the head bulk reproduce?)

Rows 323–324 on c311/c312 recomputed from the dumps (must
match M62 exactly — 323:+3/d0 + 324:+1/d0 bulk on c311,
noncell on c312 — or table the mismatch and stop; §Guards):

1. Pair table: rows 323–324 on c311 + c312 with full value
   rows (kind/δ/decile/band/d).
2. Row-323 table: row 323 across ALL 33 union cols (kind +
   δ + decile per column — which columns read bulk/tail
   at 323?).
3. Row-324 table: row 324 across ALL 33 union cols (same).

### Task 2 — neighborhood census (is the pair column-local?)

1. Bulk-neighbor table: bulk counts at rows 323–324 per
   neighbor column (310/312/313/314/315 + union hits —
   is c311 alone?).
2. δ table: δ values of any neighbor bulk/tail at 323–324
   (+3/+1 echoed anywhere? what signs?).
3. Decile table: deciles at 323–324 per neighbor column
   (dec-0 echoed? decile gradient across columns?).

### Task 3 — controls + determinism (M18–M62 precedent)

`control.py` (imports `m63` neighborhood core; expectations
analytic hand-computed; pure-synthetic status map, NOT
dump-injected — deviation reasoned per M53/M62:
neighborhood helpers operate on (rows, cols, status), so a
synthetic status map exercises the identical code path with
zero dump coupling):

- C-NEIGHBOR: synthetic truth with KNOWN row bulk
  (1 column-pair + 1 neighbor col, rows 5–6; known
  kinds/δ/deciles/bands):
  - status: (5,0) bulk +3 d0 b2; (6,0) bulk +1 d0 b2;
    (5,1) noncell None d3 b2; (6,1) noncell None d3 b2;
    (5,2) tail +9 d1 b2; (6,2) noncell None d0 b2.
  - Want census rows 5–6 cols [0,1,2]:
    c0: rows [5,6]; bulk [(5,+3,d0),(6,+1,d0)];
    noncell []; tail []; counts 2/0/0;
    deciles [0,0]; decspan 1; dechist {0:2}.
    c1: rows [5,6]; bulk []; noncell [5,6]; tail [];
    counts 0/2/0; deciles [3,3]; decspan 1;
    dechist {3:2}.
    c2: rows [5,6]; bulk []; noncell [6];
    tail [(5,+9,d1)]; counts 0/1/1; deciles [1,0];
    decspan 2; dechist {0:1,1:1}.
  - Want row_slice r5 cols [0,1,2]: c0 bulk/+3/d0/b2;
    c1 noncell/None/d3/b2; c2 tail/+9/d1/b2.
  - Want row_slice r6 cols [0,1,2]: c0 bulk/+1/d0/b2;
    c1 noncell/None/d3/b2; c2 noncell/None/d0/b2.
  - Pass = neighborhood census + both row slices exact.

Determinism: re-run Task 1 (pair + row slices + margins)
on s0+m15 (fresh loads); canonical-text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m62.txt`
sha (tabled; parsed interval values guarded per §Guards —
non-guarding sha comparison, tabled). Model-0 recompute:
R_0/fnv must match M17–M62 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table. R_s vs `loo.txt` cross-check on s0 (want equal;
mismatch = stop and table, M22 precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_HEADMATCH (head bulk reproduces): recomputed m15
  tail-Y pair (c311 6 + c312 23) matches M62 value-exactly
  (both (row,δ,dec) sets + sums +129/+130 + spans/gaps),
  AND rows 323–324 read bulk +3/d0 + bulk +1/d0 on c311
  (band 2 both) and noncell dec3/band2 both rows on c312.
- H2_PROBE48 (48-probe reproduction): all 48 M62 interval
  probes (rows 323–334 × cols 311/312 × frames m15/s0)
  match `m62.txt` interval lines value-exactly
  (kind,delta,dec,band) — the other 44/48 read noncell.
- H3_SLICES66 (row slices complete): rows 323 + 324 each
  probed across all 33 union cols on m15 (+ s0 auxiliary,
  132 probes total); each probe reads exactly one of
  bulk/noncell/tail with delta iff incell.
- H4_BAND2GEOM (band geometry): all 132 neighborhood
  probes read band 2 (rows 323–324 in r299-447 by
  construction).
- H5_BULKNEIGHBOR (bulk-neighbor table tabled): bulk
  counts at rows 323–324 per neighbor column (named
  310/312/313/314/315 + any union hits) tabled —
  the c311-alone question answered by table.
- H6_DELTAGRAD (δ table tabled): δ values of every
  neighbor bulk/tail probe at 323–324 tabled
  (+3/+1 echoed anywhere? what signs?).
- H7_DECGRAD (decile table tabled): deciles at 323–324
  per neighbor column tabled (dec-0 echoed? decile
  gradient across columns?).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum δ)
exact per the M56 table below (all 9 cols incl. c341);
m62.txt pair+interval guard: recomputed pair over the 33
union cols (per-column s0_n + m15_n + pos/neg + min/max/sum
for 311/312) + c311/c312 site sets {(row,delta,dec)} vs
DESIGN pins AND vs `m62.txt` lines (pair margins +
interval probes 48/48; rowgeom gaps) + c312 runs 7/10/6
(mismatch -> stop, tabled); δ!=0 throughout cell 7;
P(δ>0)==M19/M20 0.8093/0.8019; tail planes Y/U/V 102/0/0
s0 + 134/0/0 m15 (non-Y tabled, census-gating disclosed);
`loo.txt` 764 rows + top-10 shapes/shares; s0 P1 edges
match m18.txt s0 row; carrier removed counts + bands (M19
values); self Jaccard == 1.0. Task 2 joins the measured
values.

Per-column guard table (n / rows / sum δ; mean=sum/n):

| col | s0 n/rows/sum | m15 n/rows/sum |
| --- | --- | --- |
| 257 | 10 / 23-32 / +255 | 10 / 23-32 / +172 |
| 277 | 10 / 23-32 / +244 | 10 / 23-32 / +172 |
| 296 | 9 / 24-34 / +294 | 9 / 24-34 / +306 |
| 301 | 11 / 23-33 / +339 | 11 / 23-33 / +291 |
| 321 | 10 / 23-32 / +227 | 10 / 23-32 / +252 |
| 340 | 8 / 24-34 / +292 | 9 / 24-34 / +311 |
| 341 | 0 / — / 0 | 1 / 280-280 / -9 |
| 342 | 5 / 27-35 / -94 | 5 / 27-35 / -87 |
| 343 | 2 / 26-27 / -57 | 4 / 25-289 / -97 |

## Run protocol

1. Input shas + `m62.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Pair recompute + m62.txt/design guard (mismatch ->
   stop); head-pair table + row slices (m15 primary, s0
   auxiliary) + 48-probe interval re-itemization.
4. Bulk-neighbor table + δ table + decile table.
5. Determinism re-run receipt (Task 1 on s0+m15,
   canonical sha).
6. PNG neighborhood map (320x224, <5 MB total) to work dir:
   m15 tail-Y sites colored by pair class (yellow =
   c311 6; green = c312-pos 13; red = c312-neg 10; gray =
   other tail 105) + neighborhood-row overlay on all 33
   union cols rows 323–324 (cyan = bulk, magenta = tail,
   dark blue = noncell; precedence neighborhood-overlay >
   pair colors); evidence copy ONLY if any non-311 union
   column reads bulk OR tail at rows 323–324 on m15
   (neighbor activity — the pre-registered neighbor split)
   — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 15:11 EDT, stop by 19:11).
