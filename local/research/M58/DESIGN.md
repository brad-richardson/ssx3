# M58 — Design (recorded before running)

Goal: m15 off-mode decile mass (M57 gap 1, taken on
orchestrator judgment): m15 tail-Y carries ALL 51 pooled
off-6+ non-9 sites (dec 0:13 / 1:12 / 3:19 / 4:5 / 5:2)
while s0 tail-Y reads 0 in deciles 0–5 and shared reads
67/69 dec-9. Per-site tables of the 51 m15 off-mode sites
(row/col/δ/decile + seats + d) — where do they sit
(columns? bands? near the far site?) and what δ do they
carry? Answer by table. Tables, no verdicts. Fully
offline: no lease of any kind, no boots, no harness runs,
no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles), `/Volumes/Extreme SSD/m57/m57.txt`
(histograms to reproduce — match exactly per §Guards
or table the mismatch and stop). Work dir: `/Volumes/Extreme
SSD/m58/` (new). Evidence: `local/research/M58/` (committed
with `git add -f`, prefix `[M58]`, trailer `Orchestrated-By:
Muse Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M57/REPORT.md` (all of it:
m15 0:13/1:12/2:0/3:19/4:5/5:2/6:1/7:2/8:5/9:75 n=134;
s0 0 in deciles 0–5; shared 67/69 dec-9; pooled 167/236;
far m15 (289,343) δ −15 d=262 band 1 dec 3) plus
`local/research/M33/REPORT.md` (decile-seat machinery:
band/decile/streak/carrier/701 seats; decile_hist) plus
`local/research/M56/REPORT.md` (far census: 33 union cols,
221 non-far + 14 singletons; far_info d machinery;
column table).

## Estimator (`m58.py`, `control.py`)

Shared core (M57 `m57.py` verbatim where reused: YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median`
(halves away from zero), `hole_ranges`, `off_y`
(o=r*1280+(c//2)*4+(0 if c even else 2)), `y_col_dict`
(tail-Y column profiles sorted by row), `far_info`
(nearest-neighbor row gap, singleton N/A), `aux_dist`,
`pooled_d`, `hump_metrics` (first-tie argmax peak),
`bands_of`/`ROW_BAND` (geometry thirds via
`np.array_split(arange(448),3)` → band0 r0–149, band1 r150–298,
band2 r299–447), `p1_gradient` (M18 P1 block verbatim:
|gx|+|gy| on s0 mid-Y, quantile edges, `digitize` deciles),
carrier removed masks (res0 & ~ress on Y, M22-verbatim),
`seat_of`, `decile_hist`, `tail_y_sites`). Byte offset o ->
row o//1280; Y bytes at o%4==0/2.

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard).
- Bulk = cell-7 bytes with |δ|<8 (want 2373 s0 / 2405 m15).
  Tail = cell-7 bytes with |δ|≥8 (want 102 s0 / 134 m15; s0
  sub-bins 28 in 8–15 + 74 in 16+, m15 50 + 84; max 47/48).
- Tail-Y = tail bytes on the Y plane (expect 102/0/0 s0 +
  134/0/0 m15; non-Y tabled, census-gating disclosed).
- Column membership = all tail-Y sites with Y-column == c.
- Seat (s0-anchored, M33/M57-verbatim): band = ROW_BAND[r];
  decile = s0 mid-Y P1 decile at (r,c) (`dec_s0[r,c]`,
  edges guarded vs m18 constants); streak = Y-column in the
  named-9 set {257,277,296,301,321,340,341,342,343} else
  `other`; carrier = inside/outside each M22-verbatim top-10
  removed mask (shapes [694,693,701,368,369,366,370,376,748,
  750]) + the 701 split (in/out); peak seat = column-frame
  first-tie argmax peak row (`hump_metrics` verbatim),
  at-peak? tabled per site.
- Shared tail S = T_s0 ∩ T_m15 (Y-plane intersection).
  Pooled = multiset union (s0 sites + m15 sites, shared
  counted twice — disclosed; Jaccard tabled alongside).
- The 51 (this brief's set): m15 tail-Y sites with s0-P1
  decile ≤ 5 (off-mode = outside deciles 6+; dec-2 bin
  expected empty per M57, tabled either way). Want n=51
  with bin counts 0:13 / 1:12 / 2:0 / 3:19 / 4:5 / 5:2.
- d (M56-verbatim `far_info` on the m15 tail-Y column
  profiles): nearest-neighbor row gap within the same column
  same frame; singleton columns (n==1) → d=N/A, excluded
  from d ranking, tabled as such.

M57 pins (must reproduce or stop, §Guards):

- dechist s0: n=102, 0:0 1:0 2:0 3:0 4:0 5:0 6:2 7:2 8:6 9:92.
- dechist m15: n=134, 0:13 1:12 2:0 3:19 4:5 5:2 6:1 7:2 8:5
  9:75.
- dechist shared: n=69, 0:0 1:0 2:0 3:0 4:0 5:0 6:0 7:0 8:2
  9:67; jaccard=0.4132.
- dechist pooled: n=236, 0:13 1:12 2:0 3:19 4:5 5:2 6:3 7:4
  8:11 9:167.
- Far: m15 (289,343), δ −15, d=262 (lo 27, hi None), band 1,
  dec 3, streak 343, carrier-none, 701-out, peak 289,
  at-peak True.
- Census margins: 33 union tail-Y cols; singletons 6 s0 +
  8 m15.

Off-51 helpers (factored for the control to import):

- `off51_select(sites, dec_plane)`: sites = list of (r,c);
  returns the off-mode subset (dec ≤ 5), sorted by
  (dec, col, row). Pure function of (plane, sites).
- `col_counts(sites)`: sites = list of (r,c); returns
  {col: n} sorted by col. Pure function of sites.
- `band_hist(sites)`: sites = list of (r,c); returns
  {band: n} via ROW_BAND. Pure function of sites.
- Dump path calls all three with m15 tail-Y sites +
  `dec_s0`; control path calls all three with synthetic
  sites + a synthetic plane (identical code path).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float shares printed `:.4f`.

### Task 1 — histogram reproduction (do the 51 reproduce?)

m15 + s0 + shared + pooled tail-Y decile histograms
recomputed from the dumps (must match M57 exactly — m15
0:13/1:12/3:19/4:5/5:2, s0 0 in 0–5, shared 67/69, pooled
167/236 — or table the mismatch and stop; §Guards):

1. Hist-4 table: all four histograms recomputed + M57
   match flags (per-scope per-decile counts + dec-9 share
   + mode + match=True/False vs `m57.txt` and vs the
   DESIGN pins above).
2. Site-51 table: each off-mode site's (row,col)/δ/decile
   + band/streak/carrier/701 seats (M33/M56 machinery on
   51 sites, via `seat_of` + m15 column-profile δ) + d
   where ranked (M56 `far_info` d/lo/hi; singleton → N/A).
   Order: (dec, col, row).
3. Decile-bin table: per-bin δ summaries for all 10 m15
   bins (n + exact δ counts + min/max/sum + pos/neg split;
   bin 2 expected n=0, tabled either way).

### Task 2 — off-mode geography (where do the 51 sit?)

1. Column table: 51 counts by column over the 33 union
   cols (M56's column table joined with decile): per union
   col the m15 tail-Y n + off-51 n + off-51 share +
   per-site (row:δ/dec) rows for off-51 members;
   modal off-51 column + null-4 (313/332/314/311) and c343
   splits tabled (H5/H7 inputs).
2. Band/d table: band seats + nearest-neighbor d for the
   51 (M56 d machinery on 51 sites): per-site band + d +
   lo/hi (d desc order) + band histogram + d-defined vs
   singleton-N/A split (H6 input).
3. Far-join table: the far site (289,343) against the 51:
   far membership in the 51 (yes/no + far row); nearest
   off-mode site by |Δrow| / by |Δcol| / by Manhattan
   (ties tabled, far itself excluded from the ranking);
   the dec-3 bin co-members (all 19 with the far marked).

### Task 3 — controls + determinism (M18–M57 precedent)

`control.py` (imports `m58` off-51/seat/histogram core;
expectations analytic hand-computed; pure-synthetic dec
plane + site lists, NOT dump-injected — deviation reasoned
per M53/M57: seats/histograms operate on (plane, sites),
so a synthetic plane exercises the identical code path
with zero dump coupling; band path uses the real ROW_BAND
on synthetic rows, disclosed):

- C-OFF51: synthetic truth with KNOWN decile seats on a
  8×12 synthetic plane (rows 0–7, cols 0–11):
  - Plane: col 0–5 read dec 9 (mode block, 48 cells);
    col 6–7 read dec 3 (off-mode block, 16 cells);
    col 8 reads dec 0, col 9 reads dec 1, col 10 reads
    dec 4, col 11 reads dec 5 (singleton-decile columns,
    8 cells each).
  - Sites: M1–M6 mode sites at (0,0) (1,1) (2,2) (3,3)
    (4,4) (5,5) — want dec 9 ×6; F1–F6 off-mode sites at
    (0,6) (1,7) [dec 3 ×2] (2,8) [dec 0] (3,9) [dec 1]
    (4,10) [dec 4] (5,11) [dec 5].
  - Want: per-site deciles exact (12 sites); off-51
    selection exact (6 sites: F1–F6, sorted (dec,col,row)
    = (2,8)d0 (3,9)d1 (0,6)d3 (1,7)d3 (4,10)d4 (5,11)d5);
    column table over the off-mode 6 exact
    ({6:1,7:1,8:1,9:1,10:1,11:1}); band histogram over
    the 12 exact (all rows 0–5 → band 0 ×12); histogram
    over the 12 exact ({0:1,1:1,2:0,3:2,4:1,5:1,6:0,7:0,
    8:0,9:6}, n=12, dec-9 share 0.5000, mode 9 @0.5000,
    dec-3 rank 2); streak seats exact (all synthetic cols
    <257 → other); carrier/peak N/A synthetic (no
    masks/cols — disclosed, no expectation).
  - Pass = seats + selection + column table + band hist +
    histogram + shares + ranks exact.

Determinism: re-run Task 1 (hist-4 + site-51 + decile-bin)
on s0+m15 (fresh loads); canonical-text sha byte-identical
pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m57.txt`
sha (tabled; parsed histogram values guarded per §Guards —
non-guarding sha comparison, tabled). Model-0 recompute:
R_0/fnv must match M17–M57 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table. R_s vs `loo.txt` cross-check on s0 (want equal;
mismatch = stop and table, M22 precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_HIST51 (m15 histogram reproduces): recomputed m15
  tail-Y decile histogram matches M57 value-exactly (all 10
  bins; off-mode 0:13/1:12/2:0/3:19/4:5/5:2, n=51).
- H2_S0CLEAN (s0 carries no off-mode mass): recomputed s0
  tail-Y sites in deciles 0–5 == 0.
- H3_SHAREDMODE (shared tail dec-9 mode): shared tail-Y
  dec-9 share ≥ 0.90.
- H4_FAROFF (far site is off-mode): the far site m15
  (289,343) is a member of the 51 (dec ≤ 5).
- H5_COLCONC (off-mode column concentration): the largest
  single-column count among the 51 is ≥ 13 (≥1/4 of 51).
- H6_BANDMODE (off-mode band mode): the modal band among
  the 51 holds ≥ 26/51 (share ≥ 0.50).
- H7_NULLCOL (off-mode on null columns): the share of the
  51 on null-4 columns (313/332/314/311) is ≥ 0.25.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum δ)
exact per the M56 table below (all 9 cols incl. c341);
m57.txt histogram guard: recomputed dechist s0/m15/shared/
pooled (per-decile counts + n) + shared n/jaccard vs
`m57.txt` dechist lines AND vs the DESIGN pins above
(mismatch → stop, tabled); m57.txt far-site guard
(frame/col/row/d/δ/lo/hi, M56-format census line in
m57.txt); δ≠0 throughout cell 7; P(δ>0)==M19/M20 0.8093/
0.8019; tail planes Y/U/V 102/0/0 s0 + 134/0/0 m15
(non-Y tabled, census-gating disclosed); `loo.txt` 764 rows
+ top-10 shapes/shares; s0 P1 edges match m18.txt s0 row;
carrier removed counts + bands (M19 values); self Jaccard
== 1.0. Task 2 joins the measured values.

Per-column guard table (n / rows / sum δ; mean=sum/n):

| col | s0 n/rows/sum | m15 n/rows/sum |
| --- | --- | --- |
| 257 | 10 / 23–32 / +255 | 10 / 23–32 / +172 |
| 277 | 10 / 23–32 / +244 | 10 / 23–32 / +172 |
| 296 | 9 / 24–34 / +294 | 9 / 24–34 / +306 |
| 301 | 11 / 23–33 / +339 | 11 / 23–33 / +291 |
| 321 | 10 / 23–32 / +227 | 10 / 23–32 / +252 |
| 340 | 8 / 24–34 / +292 | 9 / 24–34 / +311 |
| 341 | 0 / — / 0 | 1 / 280–280 / −9 |
| 342 | 5 / 27–35 / −94 | 5 / 27–35 / −87 |
| 343 | 2 / 26–27 / −57 | 4 / 25–289 / −97 |

## Run protocol

1. Input shas + `m57.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Hist-4 recompute + m57.txt/design guard (mismatch →
   stop); site-51 table; decile-bin table.
4. Column table (33 union cols) + band/d table + far-join
   table.
5. Determinism re-run receipt (Task 1 on s0+m15,
   canonical sha).
6. PNG off-mode map (320x224, <5 MB total) to work dir:
   pooled s0∪m15 tail-Y sites colored by off-mode class
   (red = far site; yellow = off-51 non-far; green = dec-9
   tail; gray = other-decile (6–8) tail; precedence red >
   yellow > green > gray); evidence copy ONLY if
   H5_COLCONC meets (a single column holds ≥13 of the 51 —
   the pre-registered modal-column split) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 09:03 EDT, stop by 13:03).
