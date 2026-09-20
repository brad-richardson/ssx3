# M62 — Design (recorded before running)

Goal: c311 gap-13 interval contents (M61 gap 1, taken on
orchestrator judgment): c311's largest inter-site gap (322->335,
13 rows) vs its other gaps (3/1/1/1) — the tabled locus where runs
would break if c311 split. Per-row contents of rows 323-334 on BOTH
columns (bulk/noncell/tail per row + d where bulk + decile + band)
— is the gap-13 interval empty on both columns, and what
deciles/bands do its rows carry? Answer by table. Tables, no
verdicts. Fully offline: no lease of any kind, no boots, no harness
runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles + tails + s0 P1 edges),
`/Volumes/Extreme SSD/m61/m61.txt` (pair rows to
reproduce — match exactly per §Guards or table the mismatch
and stop). Work dir: `/Volumes/Extreme SSD/m62/` (new).
Evidence: `local/research/M62/` (committed with
`git add -f`, prefix `[M62]`, trailer `Orchestrated-By: Muse
Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M61/REPORT.md` (all of it:
c311 6/0 sum +129 rows 317-336 gaps 3/1/1/13/1 ndec 4
d0:2/d1:1/d3:2/d5:1 dhist 1:5 3:1; c312 13/10 sum +130 runs
7/10/6 rows 316-379 gaps 1/1/1/22/... span 63 ndec 6
d0:8/d1:6/d3:6/d4:1/d5:1/d7:1 dhist 1:22 2:1; site-29 rows;
rowgeom; counterparts; M61 gap 1 = this brief) plus
`local/research/M60/REPORT.md` (all of it: spans c311 19 /
c312 63 nested; unanimity; decmix; dprof) plus
`local/research/M56/REPORT.md` (all of it: hole machinery —
c343 hole 28-288 x261: m15 bulk 1 (r30 |d|=1) / noncell 260 /
tail 0; s0 bulk 8 (r132-272 all |d|=1) / noncell 253 / tail 0;
the M56 c343-hole itemization is the shape model).

## Estimator (`m62.py`, `control.py`)

Shared core (M61 `m61.py` verbatim where reused: YUYV 640x448
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
- Flanks = c311 rows 322/335 + c312 rows 319/341 (the 4
  tail-Y sites bracketing the 323-334 interval on the m15
  frame).
- Interval = rows 323-334 inclusive (12 rows) on columns 311
  + 312 (the open interval between c311's 322 and 335; also
  interior to c312's 319->341 22-row gap).
- Interval probe (dump path, `cell_status` verbatim): for a Y
  (row, col), the byte offset `off_y` reads noncell (mask
  False) vs bulk (mask True, |d|<8) vs tail (mask True,
  |d|>=8), with delta (None when noncell) + decile + band.
  Primary frame m15; s0 auxiliary (same rows/cols, for the
  M56-shape join).
- Interval census (factored, control-covered): per-column
  {rows, probes, bulk/noncell/tail row lists, counts,
  deciles row order, decspan, dechist} over the 12 rows.
- Hole join: gap-13 per-column-per-frame bulk/noncell/tail
  counts (of 12 rows) beside the M56 c343-hole reference
  (28-288 x261: m15 1/260/0, s0 8/253/0, 0 tail either
  frame) + a dump-path re-itemization of the c343 hole
  (table-only match flags, NOT a stop guard — reference,
  not input).
- Shared tail S = T_s0 ∩ T_m15 (Y-plane intersection).
  Pooled = multiset union (disclosed; Jaccard tabled).

M61 pins (must reproduce or stop, §Guards):

- Pair margins (col: s0_n/m15_n/pos/neg/min/max/sum/class):
  - 311: 4/6/6/0/+9/+46/+129/all-pos.
  - 312: 3/23/13/10/-9/+33/+130/split.
- c311 m15 sites (row:delta/dec, row order, n=6):
  317:+9/d5 320:+22/d1 321:+20/d0 322:+10/d0 335:+46/d3
  336:+22/d3.
- c312 m15 sites (row:delta/dec, row order, n=23):
  316:+11/d7 317:+20/d5 318:+19/d1 319:+9/d1 341:+14/d1
  342:+22/d3 343:+9/d3 353:-9/d0 354:-9/d0 355:-9/d0
  356:-9/d0 362:-8/d3 363:-8/d4 364:-9/d3 365:-9/d0
  366:-9/d0 367:-8/d0 369:+14/d3 373:+33/d1 374:+15/d1
  377:+18/d0 378:+23/d1 379:+10/d3.
- Flank value rows (row: delta/dec/band/d/lo/hi):
  - (322,311): +10/d0/band2/d1/lo321/hi335.
  - (335,311): +46/d3/band2/d1/lo322/hi336.
  - (319,312): +9/d1/band2/d1/lo318/hi341.
  - (341,312): +14/d1/band2/d1/lo319/hi342.
- c311 rows [317,320,321,322,335,336], gaps [3,1,1,13,1].
- c312 rows [316,317,318,319,341,342,343,353,354,355,356,
  362,363,364,365,366,367,369,373,374,377,378,379], gaps
  [1,1,1,22,1,1,10,1,1,1,6,1,1,1,1,1,2,4,1,3,1,1].
- c312 rows overlapping 323-334: NONE (319->341 22-row gap
  covers the interval; likewise c311 322->335 covers it).
- M56 c343-hole reference (join target, table-only):
  span 28-288 x261; m15 bulk 1 (r30 |d|=1) / noncell 260 /
  tail 0; s0 bulk 8 (r132/140/186/233/235/236/242/272 all
  |d|=1) / noncell 253 / tail 0.

Interval helpers (factored for the control to import):

- `interval_census(row_lo, row_hi, cols, status)`: row_lo/hi
  ints inclusive; cols = [c311, c312]; status =
  {(r,c): {kind, delta, dec, band}}. Returns {col: {rows,
  probes, bulk [(r,delta,dec)], noncell [r], tail
  [(r,delta,dec)], counts {bulk,noncell,tail}, deciles [row
  order], decspan, dechist}} sorted by col. Pure function of
  (rows, cols, status).
- `holejoin_compare(gap_counts, ref_counts)`: gap_counts =
  {label: {bulk, noncell, tail, n}}; ref_counts likewise.
  Returns {label: {bulk, noncell, tail, n, bulkshare,
  tailshare}} with shares rounded .4f (None when n==0).
  Pure function of counts.
- Dump path calls interval_census with rows 323-334 +
  [311,312] + status maps built from `cell_status` on m15
  (primary) and s0 (auxiliary); control path calls the same
  two with a synthetic status map + synthetic ref (identical
  code path).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float shares printed `:.4f`.

### Task 1 — interval reproduction (do the flanking rows reproduce?)

c311's 6 + c312's flanking rows (319/341) recomputed from
the dumps (must match M61 exactly — rows, d, deciles, gaps
— or table the mismatch and stop; §Guards):

1. Flank table: c311 rows 322/335 + c312 rows 319/341 with
   full value rows (d/decile/band/d).
2. Interval table: rows 323–334 on c311 (kind + d + decile
   + band per row, 12 rows).
3. Interval table: rows 323–334 on c312 (same 12 rows).

### Task 2 — interval census (what's inside gap-13?)

1. Bulk table: any bulk sites in 323–334 either column?
   (rows + d + deciles — or NONE tabled).
2. Decile table: per-row deciles over the interval both
   columns (do deciles drift across the gap?).
3. Hole-join table: gap-13 vs M56's c343 hole (28–288:
   bulk 1/8, 0 tail) — same shape class? (counts tabled,
   no verdict).

### Task 3 — controls + determinism (M18–M61 precedent)

`control.py` (imports `m62` interval core; expectations
analytic hand-computed; pure-synthetic status map + ref
counts, NOT dump-injected — deviation reasoned per M53/M61:
interval helpers operate on (rows, cols, status), so a
synthetic status map exercises the identical code path with
zero dump coupling):

- C-INTERVAL: synthetic truth with KNOWN interval contents
  (rows 3-6 x cols 0-1; bulk + noncell + tail rows, known
  d/deciles/bands):
  - status: (3,0) bulk +2 d3 b2; (4,0) noncell None d0 b2;
    (5,0) tail +9 d1 b2; (6,0) bulk -1 d3 b2;
    (3,1) noncell None d5 b2; (4,1) bulk +1 d1 b2;
    (5,1) noncell None d0 b2; (6,1) noncell None d7 b2.
  - Want c0: rows [3,4,5,6]; bulk [(3,+2,d3),(6,-1,d3)];
    noncell [4]; tail [(5,+9,d1)]; counts 2/1/1;
    deciles [3,0,1,3]; decspan 3; dechist {0:1,1:1,3:2}.
  - Want c1: rows [3,4,5,6]; bulk [(4,+1,d1)];
    noncell [3,5,6]; tail []; counts 1/3/0;
    deciles [5,1,0,7]; decspan 4; dechist {0:1,1:1,5:1,7:1}.
  - Want holejoin vs synthetic ref {gap: {2,1,1,4}, ref:
    {1,2,1,4}}: gap bulkshare 0.5000 tailshare 0.2500; ref
    bulkshare 0.2500 tailshare 0.2500.
  - Pass = interval_census + holejoin_compare exact.

Determinism: re-run Task 1 (flank + interval tables + margins)
on s0+m15 (fresh loads); canonical-text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m61.txt`
sha (tabled; parsed pair values guarded per §Guards —
non-guarding sha comparison, tabled). Model-0 recompute:
R_0/fnv must match M17–M61 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table. R_s vs `loo.txt` cross-check on s0 (want equal;
mismatch = stop and table, M22 precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_FLANKMATCH (flanks reproduce): recomputed m15 tail-Y
  pair (c311 6 + c312 23) matches M61 value-exactly
  (both (row,d,dec) sets + sums +129/+130 + c312 runs
  7/10/6 + spans/gaps/decile-hists/d-hists).
- H2_GAP13 (gap structure): c311 gaps read [3,1,1,13,1]
  with 322->335 = 13 the unique max; c312 gaps read
  [1,1,1,22,...] with 319->341 = 22; c311 AND c312 rows
  overlapping 323-334 read NONE.
- H3_FLANKSEAT (flank value rows): flanks read
  (322,311):+10/d0, (335,311):+46/d3, (319,312):+9/d1,
  (341,312):+14/d1, all band-2 + d1 with lo/hi
  321/335, 322/336, 318/341, 319/342.
- H4_INTERVAL12 (interval probes complete): 12/12 rows x
  2 cols probed on m15 (+ s0 auxiliary); each probe reads
  exactly one of bulk/noncell/tail with delta iff incell.
- H5_BAND2GEOM (band geometry): all 24 m15 interval
  probes (+ 24 s0) read band 2 (rows 323-334 all in
  r299-447 by construction).
- H6_NOTAIL (no tail in the gap): 0 tail probes in
  323-334 on either column either frame (entailed by the
  H2 gap structure — a probe/profile consistency check).
- H7_HOLEJOIN (join tabled): gap-13 per-column-per-frame
  bulk/noncell/tail counts tabled beside the M56 c343-hole
  reference (m15 1/260/0, s0 8/253/0) + dump-path
  c343-hole re-itemization match flags.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum d)
exact per the M56 table below (all 9 cols incl. c341);
m61.txt pair guard: recomputed pair over the 33 union
cols (per-column s0_n + m15_n + pos/neg + min/max/sum for
311/312) + c311/c312 site sets {(row,delta,dec)} vs
DESIGN pins AND vs `m61.txt` lines (pair margins +
site-29 + runs + spans for 311/312; rowgeom gaps) + c312 runs
7/10/6 (mismatch -> stop, tabled); d!=0
throughout cell 7; P(d>0)==M19/M20 0.8093/0.8019; tail
planes Y/U/V 102/0/0 s0 + 134/0/0 m15 (non-Y tabled,
census-gating disclosed); `loo.txt` 764 rows + top-10
shapes/shares; s0 P1 edges match m18.txt s0 row; carrier
removed counts + bands (M19 values); self Jaccard == 1.0.
Task 2 joins the measured values.

Per-column guard table (n / rows / sum d; mean=sum/n):

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

1. Input shas + `m61.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Pair recompute + m61.txt/design guard (mismatch ->
   stop); flank table + interval tables (m15 primary, s0
   auxiliary).
4. Bulk table + decile table + hole-join table (+ c343-hole
   re-itemization, table-only).
5. Determinism re-run receipt (Task 1 on s0+m15,
   canonical sha).
6. PNG interval map (320x224, <5 MB total) to work dir:
   m15 tail-Y sites colored by pair class (yellow =
   c311 6; green = c312-pos 13; red = c312-neg 10; gray =
   other tail 105) + interval-row overlay on cols 311/312
   rows 323-334 (cyan = bulk, magenta = tail, dark blue =
   noncell; precedence interval-overlay > pair colors);
   evidence copy ONLY if m15 interval bulk counts differ
   between c311 and c312 (column-asymmetric interval —
   the pre-registered asymmetry split) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 14:10 EDT, stop by 18:10).
