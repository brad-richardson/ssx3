# M60 — Design (recorded before running)

Goal: c312 unique sign-split column (M59 gap 1, taken on
orchestrator judgment): c312 is the ONLY m15 tail-Y column
with n>=2 reading both signs (13/10, pos share 0.5652, sum
+130); the other 18 multi-site columns read unanimous (12
all-pos, 6 all-neg). Per-column sign-unanimity census over
all 27 m15 tail-Y columns joined with row-span +
decile-span — what distinguishes c312 (span? decile mix? d
profile?) from the 18 unanimous multi-site columns? Answer
by table. Tables, no verdicts. Fully offline: no lease of
any kind, no boots, no harness runs, no fork changes, no
`adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles + tails + s0 P1 edges),
`/Volumes/Extreme SSD/m59/m59.txt` (column-sign table to
reproduce — match exactly per §Guards or table the mismatch
and stop). Work dir: `/Volumes/Extreme SSD/m60/` (new).
Evidence: `local/research/M60/` (committed with
`git add -f`, prefix `[M60]`, trailer `Orchestrated-By: Muse
Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M59/REPORT.md` (all of it:
c312 the only split at n>=2, 13/10 pos/neg, min -9 max +33
sum +130, pos share 0.5652; 16 all-pos + 10 all-neg + 6
s0-only columns; c312's 23 sites 316:+11/d7 317:+20/d5
318:+19/d1 319:+9/d1 341:+14/d1 342:+22/d3 343:+9/d3
353-356:-9/d0 362:-8/d3 363:-8/d4 364:-9/d3 365-366:-9/d0
367:-8/d0 369:+14/d3 373:+33/d1 374:+15/d1 377:+18/d0
378:+23/d1 379:+10/d3; bincol c312 d0:8/d1:6/d3:6/d4:1/d5:1/
d7:1) plus `local/research/M58/REPORT.md` (c312's 23 sites:
22/23 off-mode, r316 d+11 dec-7 the exception; band/d
machinery) plus `local/research/M56/REPORT.md` (33 union
cols, d machinery via `far_info`).

## Estimator (`m60.py`, `control.py`)

Shared core (M59 `m59.py` verbatim where reused: YUYV 640x448
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
`col_counts`, `band_hist`). Byte offset o -> row o//1280; Y
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
- Unanimity class (per column over m15 tail-Y, n>=1): split
  iff pos>0 and neg>0; else all-pos (pos==n) / all-neg
  (neg==n). Singletons (n==1) are unanimous by construction,
  disclosed. m15-empty union cols read s0-only (n/a sign).
- Row-span = max row - min row over the column's m15 tail-Y
  rows (0 when n==1, disclosed; n/a when n==0).
- Decile-span = distinct s0-P1 deciles over the column's m15
  tail-Y sites (1 when n==1, disclosed; n/a when n==0).
- Sign run = maximal run of equal sign in row order over a
  column's m15 tail-Y sites (row,delta) sorted by row.
- d (M56-verbatim `far_info` on the m15 tail-Y column
  profiles): nearest-neighbor row gap within the same column
  same frame; singleton columns (n==1) -> d=N/A, tabled.
- d-profile row (per column): n + d histogram {d:count} over
  d-defined sites + N/A count + d max + d mode (ties ->
  smallest d, disclosed).
- Decile-mix row (per column): n + decile histogram
  {dec:count} + decile-span + max share (top/n, 4dp).
- Shared tail S = T_s0 ∩ T_m15 (Y-plane intersection).
  Pooled = multiset union (disclosed; Jaccard tabled).

M59 pins (must reproduce or stop, §Guards):

- 33 union tail-Y cols: 38/65/76/257/277/289/292/293/296/
  298/299/301/306/307/308/309/310/311/312/313/314/315/316/
  321/332/340/341/342/343/344/353/372/617 (27 m15 + 6
  s0-only 38/292/293/316/332/372).
- Column-sign (col: s0_n/m15_n/pos/neg/min/max/sum):
  - 38: 1/0/0/0/None/None/0; 65: 0/2/0/2/-17/-8/-25;
    76: 0/1/0/1/-35/-35/-35; 257: 10/10/10/0/+8/+20/+172;
    277: 10/10/10/0/+8/+20/+172; 289: 0/2/0/2/-16/-8/-24;
    292: 1/0; 293: 1/0; 296: 9/9/9/0/+16/+46/+306;
    298: 4/7/0/7/-26/-8/-114; 299: 0/1/0/1/-36/-36/-36;
    301: 11/11/11/0/+12/+48/+291; 306: 0/2/2/0/+23/+46/+69;
    307: 1/1/1/0/+9/+9/+9; 308: 0/2/0/2/-18/-8/-26;
    309: 0/2/2/0/+8/+10/+18; 310: 0/1/1/0/+10/+10/+10;
    311: 4/6/6/0/+9/+46/+129; 312: 3/23/13/10/-9/+33/+130;
    313: 4/5/5/0/+17/+29/+113; 314: 7/2/2/0/+15/+24/+39;
    315: 7/5/5/0/+11/+21/+83; 316: 1/0;
    321: 10/10/10/0/+14/+31/+252; 332: 2/0;
    340: 8/9/9/0/+14/+48/+311; 341: 0/1/0/1/-9/-9/-9;
    342: 5/5/0/5/-21/-13/-87; 343: 2/4/0/4/-34/-15/-97;
    344: 0/1/1/0/+8/+8/+8; 353: 0/1/0/1/-9/-9/-9;
    372: 1/0; 617: 0/1/1/0/+10/+10/+10.
- All-pos columns (16): 257/277/296/301/306/307/309/310/311/
  313/314/315/321/340/344/617 (of which n>=2: 12).
- All-neg columns (10): 65/76/289/298/299/308/341/342/343/
  353 (of which n>=2: 6 — 65/289/298/308/342/343).
- Split columns: c312 alone (13/10, pos share 0.5652).
- c312 m15 sites (row:delta/dec, row order, n=23):
  316:+11/d7 317:+20/d5 318:+19/d1 319:+9/d1 341:+14/d1
  342:+22/d3 343:+9/d3 353:-9/d0 354:-9/d0 355:-9/d0
  356:-9/d0 362:-8/d3 363:-8/d4 364:-9/d3 365:-9/d0
  366:-9/d0 367:-8/d0 369:+14/d3 373:+33/d1 374:+15/d1
  377:+18/d0 378:+23/d1 379:+10/d3.
- c312 decile mix: d0:8/d1:6/d3:6/d4:1/d5:1/d7:1 (M59 bincol).
- c312 row-span pin: 379-316 = 63. c312 d pin (M58 band/d +
  r316 neighbor rows 316/317): 22x d1 + r369 d2 (lo=367
  hi=373); r316 d1 (min row, hi=317).

Unanimity/span helpers (factored for the control to import):

- `unanimity_rows(sites, deltas)`: sites = list of (r,c);
  deltas = {(r,c): d}. Returns {col: {n, pos, neg, posshare,
  min, max, sum, uclass}} sorted by col (uclass in
  all-pos/all-neg/split). Pure function of (sites, deltas).
- `span_rows(sites, dec_plane)`: dec_plane = (H,W) int
  deciles. Returns {col: {n, rowmin, rowmax, rowspan,
  decspan, dechist, decmaxshare}} sorted by col. Pure
  function of (plane, sites).
- `runs_rows(rows_sorted, deltas)`: rows_sorted = sorted
  [(r,c)] of one column; returns [(sign, rstart, rend,
  length)] in row order. Pure function of (rows, deltas).
- `dprof_rows(sites)`: returns {col: {n, dhist, na, dmax,
  dmode}} via `far_info` on sorted rows (singleton -> na=1,
  dmax/dmode None). Pure function of sites.
- Dump path calls all four with m15 tail-Y sites + `dec_s0`
  + m15 deltas; control path calls all four with synthetic
  sites + a synthetic plane + synthetic deltas (identical
  code path).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float shares printed `:.4f`.

### Task 1 — unanimity reproduction (does the split reproduce?)

All 27 m15 tail-Y columns recomputed from the dumps (must
match M59's column-sign table exactly — n, pos/neg,
min/max/sum per column, c312 13/10 +130 — or table the
mismatch and stop; §Guards):

1. Unanimity table: per-column n + pos/neg + unanimous?/
   split? (is c312 the only split at n>=2?).
2. c312 row table: the 23 sites in row order with d/sign/
   decile + run structure (do signs cluster in runs? where
   does r316 sit?) + d/lo/hi per site (M56 machinery).
3. Span table: per-column row-span (max-min row) +
   decile-span (distinct deciles) + n (does c312's span
   discriminate?).

### Task 2 — split-vs-unanimous census (what distinguishes c312?)

1. Span-join table: unanimous vs split columns by row-span
   and decile-span (do unanimous columns read narrower?) —
   per-column join rows sorted by row-span desc + class
   summaries (split vs unanimous-n>=2 vs singleton).
2. Decile-mix table: per-column decile histogram class
   (does c312's 8/6/6/1/1/1 mix discriminate?) — full
   {dec:count} per column + ndec ranking.
3. d-profile table: per-column d histogram class (M56 d
   machinery — does c312's d profile discriminate?) — full
   {d:count} per column + dmax/dmode.

### Task 3 — controls + determinism (M18–M59 precedent)

`control.py` (imports `m60` unanimity/span core; expectations
analytic hand-computed; pure-synthetic dec plane + site
lists + delta dict, NOT dump-injected — deviation reasoned
per M53/M59: unanimity/span helpers operate on (plane,
sites, deltas), so a synthetic plane exercises the identical
code path with zero dump coupling):

- C-UNAN: synthetic truth with KNOWN column signs on a
  10x6 synthetic plane (rows 0-9, cols 0-5):
  - Plane: col 0 reads dec 9; col 1 reads dec 3; col 2
    rows 1-2 read dec 0 and rows 5-6 read dec 1 (rest
    dec 9, unused); (7,3) reads dec 9; (0,4) and (5,4)
    read dec 9; col 5 reads dec 9 (empty, no sites).
  - Sites + deltas (12 sites; 3 unanimous multi-site + 1
    split + 1 singleton):
    - c0 unanimous-pos (N=3): (2,0):+12 (3,0):+18
      (4,0):+20 — want n=3 pos=3 neg=0 posshare 1.0000
      min=+12 max=+20 sum=+50 class all-pos; rows 2-4
      rowspan 2 decspan 1 hist {9:3}; runs [posx3];
      d [1,1,1] hist {1:3} dmax 1 dmode 1.
    - c1 unanimous-neg (N=2): (5,1):-8 (6,1):-16 — want
      n=2 pos=0 neg=2 sum=-24 class all-neg; rows 5-6
      rowspan 1 decspan 1 hist {3:2}; runs [negx2];
      d [1,1] hist {1:2} dmax 1 dmode 1.
    - c2 split (N=4): (1,2):+9 (2,2):+10 (5,2):-9
      (6,2):-8 — want n=4 pos=2 neg=2 posshare 0.5000
      min=-9 max=+10 sum=+2 class split; rows 1-6
      rowspan 5 decspan 2 hist {0:2,1:2}; runs
      [pos rows1-2 x2, neg rows5-6 x2] (2 runs); d
      [1,1,1,1] hist {1:4} dmax 1 dmode 1.
    - c3 singleton-neg (N=1): (7,3):-9 — want n=1 pos=0
      neg=1 class all-neg; rows 7-7 rowspan 0 decspan 1
      hist {9:1}; runs [negx1]; d N/A na=1 dmax/dmode
      None.
    - c4 unanimous-pos gapped (N=2): (0,4):+10 (5,4):+14
      — want n=2 pos=2 neg=0 sum=+24 class all-pos;
      rows 0-5 rowspan 5 decspan 1 hist {9:2}; runs
      [posx2]; d [5,5] hist {5:2} dmax 5 dmode 5.
    - c5 empty (N=0): absent from all row dicts.
  - Want: unanimity rows exact (5 cols, keys + margins +
    class); span rows exact (rowmin/rowmax/rowspan +
    decspan/dechist/decmaxshare); runs exact (all 5
    cols); d-profile rows exact (dhist/na/dmax/dmode).
  - Pass = unanimity + span + runs + dprof exact.

Determinism: re-run Task 1 (unanimity + c312 rows + span) on
s0+m15 (fresh loads); canonical-text sha byte-identical
pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m59.txt`
sha (tabled; parsed colsign values guarded per §Guards —
non-guarding sha comparison, tabled). Model-0 recompute:
R_0/fnv must match M17–M59 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table. R_s vs `loo.txt` cross-check on s0 (want equal;
mismatch = stop and table, M22 precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_COLMATCH (columns reproduce): recomputed m15 tail-Y
  column-sign table matches M59 value-exactly (all 27 m15
  columns: s0_n, m15_n, pos/neg, min/max/sum; plus all 6
  s0-only cols' s0_n/m15_n==0).
- H2_C312SPLIT (modal column splits): c312's 23 m15 tail-Y
  sites read 13/10 pos/neg (pos share 0.5652; min -9 max
  +33; sum +130).
- H3_C312UNIQUE (split unique at scale): c312 is the ONLY
  column with n>=2 reading both signs (split set at n>=2
  == [312]; the other 18 multi-site columns unanimous:
  12 all-pos + 6 all-neg).
- H4_SPANWIDE (c312 row-span wide): c312 row-span >= 50
  (pin 63 = 379-316).
- H5_DECMIX6 (c312 decile mix unique): c312 decile-span ==
  6 distinct deciles AND strictly exceeds every other m15
  column's decile-span (unique max; pin d0:8/d1:6/d3:6/
  d4:1/d5:1/d7:1).
- H6_RUNS3 (c312 signs cluster in 3 runs): c312 reads
  exactly 3 sign runs in row order with lengths 7/10/6
  (pos rows 316-343 / neg rows 353-367 / pos rows
  369-379); r316 sits in run 1 (leading pos run).
- H7_DSHARED (d profile shared): c312 modal d == 1 AND
  every unanimous n>=2 column also reads modal d == 1
  (d profile does not discriminate c312).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum d)
exact per the M56 table below (all 9 cols incl. c341);
m59.txt colsign guard: recomputed colsign over the 33 union
cols (per-column s0_n + m15_n + pos/neg + min/max/sum) +
c312 site set {(row,delta,dec)x23} vs `m59.txt` lines AND vs
the DESIGN pins above (mismatch -> stop, tabled); d!=0
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

1. Input shas + `m59.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Unanimity recompute + m59.txt/design guard (mismatch ->
   stop); c312 row table + runs; span table.
4. Span-join table + decile-mix table + d-profile table.
5. Determinism re-run receipt (Task 1 on s0+m15,
   canonical sha).
6. PNG unanimity map (320x224, <5 MB total) to work dir:
   m15 tail-Y sites colored by unanimity class (yellow =
   split column c312 iff the only split; green =
   unanimous-pos column; red = unanimous-neg column;
   precedence yellow > red > green); evidence copy ONLY if
   H3_C312UNIQUE meets (c312 the only split at n>=2 —
   the pre-registered unanimity split) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 11:07 EDT, stop by 15:07).
