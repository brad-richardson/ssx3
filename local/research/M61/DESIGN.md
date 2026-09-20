# M61 — Design (recorded before running)

Goal: c311-vs-c312 per-site decile/delta join (M60 gap 2, taken on
orchestrator judgment): c311 (all-pos, n=6) reads ndec 4 (d0:2/d1:1/
d3:2/d5:1, maxshare 0.3333), closest to c312's 6/0.3478, with the same
d0/d1/d3/d5 deciles minus d4/d7. Per-site decile/delta join of c311 vs
c312 — same-decile sites compared (d0/d1/d3/d5 pairs), row positions,
d values, seats — what separates the unanimous runner-up from the split
column? Answer by table. Tables, no verdicts. Fully offline: no lease
of any kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles + tails + s0 P1 edges),
`/Volumes/Extreme SSD/m60/m60.txt` (span/decile tables to
reproduce — match exactly per §Guards or table the mismatch
and stop). Work dir: `/Volumes/Extreme SSD/m61/` (new).
Evidence: `local/research/M61/` (committed with
`git add -f`, prefix `[M61]`, trailer `Orchestrated-By: Muse
Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M60/REPORT.md` (all of it:
c311 6/0 sum +129, ndec 4, d0:2/d1:1/d3:2/d5:1, maxshare
0.3333, rows 317-336 span 19, dhist 1:5 3:1; c312 13/10 sum
+130, runs 7/10/6, rows 316-379 span 63, ndec 6,
d0:8/d1:6/d3:6/d4:1/d5:1/d7:1, dhist 1:22 2:1; M60 gap 2 =
this brief) plus `local/research/M59/REPORT.md` (all of it:
column signs c311 6/0 sum +129, c312 13/10 sum +130; c312's
23 sites row:delta/dec; bincol d0:8/d1:6/d3:6/d4:1/d5:1/d7:1;
dec-1 site seats) plus `local/research/M58/REPORT.md` (all of
it: site-51 rows for both columns with band/streak/carrier/
701/peak/at-peak + d/lo/hi; c311 6/6 off-mode; c312 22/23
off-mode, r316 dec-7 the exception).

## Estimator (`m61.py`, `control.py`)

Shared core (M60 `m60.py` verbatim where reused: YUYV 640x448
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
`runs_rows`, `dprof_rows`). Byte offset o -> row o//1280; Y
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
- Pair = m15 tail-Y columns 311 (n=6) + 312 (n=23); 29 sites
  pooled (1 shared row 317 -> 28 distinct rows).
- Decile-pair row (per decile 0-9): {A_n, B_n, A_deltas
  sorted asc, B_deltas sorted asc} over the pair's m15 tail-Y
  sites (A=c311, B=c312).
- Missing decile = decile with B_n>0 and A_n==0 (want d4/d7).
- Cell status (missing-decile probe, dump path only): for a
  Y (row, col), the byte offset `off_y` reads noncell (mask
  False) vs bulk (mask True, |d|<8) vs tail (mask True,
  |d|>=8), with delta (None when noncell) + decile + band.
- Row geometry: per-column sorted rows + successive gaps
  (r[i+1]-r[i]) + span (max-min) + intersection + union +
  overlap range [max(minA,minB), min(maxA,maxB)] + nested?
  (one range inside the other) + merged unique-row label
  sequence (311/312/both) + label-run count.
- Sign run = maximal run of equal sign in row order over a
  column's m15 tail-Y sites (row,delta) sorted by row.
- Candidate break loci (c311, tabled no verdict): c311
  inter-site gaps sorted desc (gap, row pair) — where runs
  would break if c311 split.
- d (M56-verbatim `far_info` on the m15 tail-Y column
  profiles): nearest-neighbor row gap within the same column
  same frame; singleton columns (n==1) -> d=N/A, tabled.
- Seat distribution (per column): {n, bandhist, streakhist,
  carrierhist (None synthetic), split701hist (None
  synthetic), peak, atpeak_n}.
- Shared tail S = T_s0 ∩ T_m15 (Y-plane intersection).
  Pooled = multiset union (disclosed; Jaccard tabled).

M60 pins (must reproduce or stop, §Guards):

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
- Same-decile pairs (dec: A_n-vs-B_n, deltas sorted asc):
  - d0: 2-vs-8, A [+10,+20], B [-9,-9,-9,-9,-9,-9,-8,+18].
  - d1: 1-vs-6, A [+22], B [+9,+14,+15,+19,+23,+33].
  - d3: 2-vs-6, A [+22,+46], B [-9,-8,+9,+10,+14,+22].
  - d5: 1-vs-1, A [+9], B [+20].
  - d4: 0-vs-1, B [-8] (r363). d7: 0-vs-1, B [+11] (r316).
  - d2/d6/d8/d9: 0-vs-0.
- c311 span: rows 317-336 rowspan 19 decspan 4 dechist
  d0:2/d1:1/d3:2/d5:1 decmaxshare 0.3333.
- c312 span: rows 316-379 rowspan 63 decspan 6 dechist
  d0:8/d1:6/d3:6/d4:1/d5:1/d7:1 decmaxshare 0.3478.
- c311 rows [317,320,321,322,335,336], gaps [3,1,1,13,1].
- c312 rows [316,317,318,319,341,342,343,353,354,355,356,
  362,363,364,365,366,367,369,373,374,377,378,379], gaps
  [1,1,1,22,1,1,10,1,1,1,6,1,1,1,1,1,2,4,1,3,1,1].
- Shared rows [317]; union_n 28; overlap range 317-336;
  c311 range nested inside c312 range.
- c311 runs: [pos 317-336x6] (1 run).
- c312 runs: [pos 316-343x7, neg 353-367x10, pos 369-379x6].
- c311 d per site (row: d lo hi): 317: 3 None 320; 320: 1
  317 321; 321: 1 320 322; 322: 1 321 335; 335: 1 322 336;
  336: 1 335 None. dhist {1:5,3:1} dmax 3 dmode 1.
- c312 d: 22x d1 + r369 d2 (lo=367 hi=373); dhist {1:22,2:1}
  dmax 2 dmode 1.
- Seats (expected, H6 bar): all 29 band-2 + streak-other +
  carrier-none + 701-out; c311 peak 335 at-peak 1/6 (r335);
  c312 peak 373 at-peak 1/23 (r373).

Pair-join helpers (factored for the control to import):

- `decpair_rows(sitesA, sitesB, dec_plane, deltas)`: sitesA/B
  = lists of (r,c); dec_plane = (H,W) int deciles; deltas =
  {(r,c): d}. Returns {dec: {A_n, B_n, A_deltas sorted,
  B_deltas sorted}} for dec 0-9. Pure function of (plane,
  sites, deltas).
- `rowgeom_rows(rowsA, rowsB)`: rowsA/B = sorted [r] of one
  column each. Returns {A_rows, B_rows, A_span, B_span,
  A_gaps, B_gaps, intersection, union_n, overlap_range,
  nested, merged_labels, label_runs}. Pure function of rows.
- `seatdist_rows(sites, dec_plane, masks, cols)`: sites =
  list of (r,c); masks None -> carrier/split701 None;
  cols None or col-missing -> peak/atpeak None. Returns
  {col: {n, bandhist, streakhist, carrierhist, split701hist,
  peak, atpeak_n}} sorted by col. Pure function of (plane,
  sites, masks, cols).
- `cell_status(r, c, mask, delta, dec_plane)`: dump-path
  probe returning {incell, istail, isbulk, delta, dec,
  band} for one Y (r,c) via `off_y`. NOT control-covered
  (dump-coupled, disclosed).
- Dump path calls decpair/rowgeom/seatdist with m15 tail-Y
  pair sites + `dec_s0` + m15 deltas + masks + cols15;
  control path calls the same three with synthetic sites +
  a synthetic plane + synthetic deltas + masks None +
  synthetic cols (identical code path).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float shares printed `:.4f`.

### Task 1 — pair reproduction (do the 29 reproduce?)

c311's 6 + c312's 23 sites recomputed from the dumps (must
match M59/M60 exactly — (row,δ,dec) sets, sums +129/+130,
c312 runs 7/10/6 — or table the mismatch and stop; §Guards):

1. Site-29 table: all 29 sites with (row,col)/δ/decile +
   band/streak/carrier/701/at-peak + d (M33/M56 machinery).
2. Decile-pair table: same-decile cross-column pairs
   (d0: 2-vs-8, d1: 1-vs-6, d3: 2-vs-6, d5: 1-vs-1 —
   δ values side by side).
3. Missing-decile table: d4/d7 on c312 (363:−8/d4,
   316:+11/d7) vs their absence on c311 (what sits at
   those rows on c311? bulk? noncell?).

### Task 2 — separator census (what separates them?)

1. Row-geometry table: row sets + gaps + spans compared
   (c311 317–336 span 19 vs c312 316–379 span 63 —
   interleaved? disjoint? overlapping?).
2. Sign-run table: sign runs compared (c311 1 run ×6 vs
   c312 3 runs 7/10/6 — where would c311's runs break
   if it split? candidate gap loci tabled, no verdict).
3. Seat table: band/streak/carrier/701/at-peak/d
   distributions compared (do seats separate the pair?).

### Task 3 — controls + determinism (M18–M60 precedent)

`control.py` (imports `m61` pair-join core; expectations
analytic hand-computed; pure-synthetic dec plane + site
lists + delta dict + synthetic cols, NOT dump-injected —
deviation reasoned per M53/M60: join helpers operate on
(plane, sites, deltas, cols), so a synthetic plane exercises
the identical code path with zero dump coupling):

- C-PAIR: synthetic truth with KNOWN column pairs (1
  unanimous + 1 split, known δ/rows/deciles) on a 10x2
  synthetic plane (rows 0-9, cols 0-1):
  - Plane: (1,0) dec 0; (2,0) dec 1; (5,0) dec 0;
    (1,1) dec 0; (2,1) dec 1; (5,1) dec 0; (6,1) dec 4;
    rest dec 9 (unused).
  - Sites + deltas (7 sites; 1 unanimous + 1 split):
    - c0 unanimous-pos (N=3): (1,0):+10 (2,0):+12
      (5,0):+14 — want n=3 pos=3 neg=0 posshare 1.0000
      min=+10 max=+14 sum=+36 class all-pos; rows 1-5
      rowspan 4 decspan 2 hist {0:2,1:1}; runs [posx3];
      d [1,1,3] hist {1:2,3:1} dmax 3 dmode 1; peak 5
      at-peak 1/3 (r5).
    - c1 split (N=4): (1,1):+9 (2,1):-8 (5,1):-9
      (6,1):+11 — want n=4 pos=2 neg=2 posshare 0.5000
      min=-9 max=+11 sum=+3 class split; rows 1-6
      rowspan 5 decspan 3 hist {0:2,1:1,4:1}; runs
      [pos r1x1, neg r2-5x2, pos r6x1] (3 runs);
      d [1,1,1,1] hist {1:4} dmax 1 dmode 1; peak 6
      at-peak 1/4 (r6).
  - Want: unanimity rows exact (2 cols, keys + margins +
    class); span rows exact (rowmin/rowmax/rowspan +
    decspan/dechist/decmaxshare); runs exact (both cols);
    d-profile rows exact (dhist/na/dmax/dmode); decpair
    exact (d0: 2-vs-2 A[+10,+14] B[+9,-9] sorted
    [-9,+9]; d1: 1-vs-1 A[+12] B[-8]; d4: 0-vs-1
    B[+11]; rest 0-vs-0); rowgeom exact (A rows
    [1,2,5] gaps [1,3] span 4; B rows [1,2,5,6] gaps
    [1,3,1] span 5; intersection [1,2,5]; union_n 4;
    overlap 1-5; nested A-in-B True; merged labels
    [(1,both),(2,both),(5,both),(6,B)] label_runs 2);
    seatdist exact (c0 band {0:3} streak {other:3}
    carrier None split701 None peak 5 atpeak 1; c1 band
    {0:4} streak {other:4} carrier None split701 None
    peak 6 atpeak 1).
  - Pass = unanimity + span + runs + dprof + decpair +
    rowgeom + seatdist exact.

Determinism: re-run Task 1 (site-29 + decpair + missing +
margins) on s0+m15 (fresh loads); canonical-text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m60.txt`
sha (tabled; parsed pair values guarded per §Guards —
non-guarding sha comparison, tabled). Model-0 recompute:
R_0/fnv must match M17–M60 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table. R_s vs `loo.txt` cross-check on s0 (want equal;
mismatch = stop and table, M22 precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_PAIRMATCH (pair reproduces): recomputed m15 tail-Y
  pair (c311 6 + c312 23) matches M59/M60 value-exactly
  (both (row,δ,dec) sets + sums +129/+130 + c312 runs
  7/10/6 + spans/decile-hists/d-hists).
- H2_SAMEDEC (shared deciles pair): same-decile counts
  read d0 2-vs-8, d1 1-vs-6, d3 2-vs-6, d5 1-vs-1 with
  the pinned δ multisets.
- H3_MISSING47 (missing deciles): c312 reads d4×1
  (363:−8) + d7×1 (316:+11) and c311 reads d4×0 + d7×0.
- H4_SPANNEST (spans nest): c311 rows 317-336 span 19;
  c312 rows 316-379 span 63; shared rows == [317];
  c311 range nested inside c312 range.
- H5_RUNS13 (runs separate 1-vs-3): c311 reads 1 run ×6
  (all-pos) and c312 reads 3 runs 7/10/6 (pos/neg/pos).
- H6_SEATSHARED (seats shared): all 29 read band-2 +
  streak-other + carrier-none + 701-out.
- H7_DGAP312 (d gaps pinned): c311 dhist {1:5,3:1} dmax 3
  at r317 modal 1 AND c312 dhist {1:22,2:1} dmax 2 at
  r369 modal 1.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum d)
exact per the M56 table below (all 9 cols incl. c341);
m60.txt pair guard: recomputed pair over the 33 union
cols (per-column s0_n + m15_n + pos/neg + min/max/sum for
311/312) + c311/c312 site sets {(row,delta,dec)} vs
DESIGN pins AND vs `m60.txt` lines (unanim margins +
c312 sites + span + decmix + dprof for 311/312;
m60.txt carries no c311 per-site lines — c311 site set
guards vs DESIGN pins only, disclosed) + c312 runs
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

1. Input shas + `m60.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Pair recompute + m60.txt/design guard (mismatch ->
   stop); site-29 table + decpair + missing-decile probe.
4. Row-geometry table + sign-run table + seat table.
5. Determinism re-run receipt (Task 1 on s0+m15,
   canonical sha).
6. PNG pair map (320x224, <5 MB total) to work dir:
   m15 tail-Y sites colored by pair class (yellow =
   c311 runner-up 6; green = c312-pos 13; red = c312-neg
   10; gray = other tail 105; precedence yellow > red >
   green > gray); evidence copy ONLY if H5_RUNS13 meets
   (c311 1 run vs c312 3 runs — the pre-registered run
   split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 12:10 EDT, stop by 16:10).
