# M57 — Design (recorded before running)

Goal: far vs null-5 decile seats (M56 gap 1, taken on
orchestrator judgment): the lone far site m15 c343 r289 reads
s0-P1 decile 3 while tail seats read dec-9 heavy (M33 shared
85/94 dec-9; M56 H5 0/1). Do the far site's dec-3 seat and the
null-5 decile seats discriminate the far site from its 5
nearest neighbors, and where does each sit against the tail's
dec-9 mode? Answer by table. Tables, no verdicts. Fully
offline: no lease of any kind, no boots, no harness runs, no
fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles), `/Volumes/Extreme SSD/m56/m56.txt`
(far seat + null-5 to reproduce — match exactly per §Guards
or table the mismatch and stop). Work dir: `/Volumes/Extreme
SSD/m57/` (new). Evidence: `local/research/M57/` (committed
with `git add -f`, prefix `[M57]`, trailer `Orchestrated-By:
Muse Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M56/REPORT.md` (all of it:
far m15 (289,343) δ −15 d=262 band 1 dec 3 streak 343
carrier-none 701-out at-peak; null-5 s0 c313 r292 d16 δ−16 /
s0 c332 r295 d9 δ+10 / s0 c332 r304 d9 δ−12 / s0 c314 r269
d7 δ+12 / m15 c311 r317 d3 δ+9; 33-col table; H5 0/1) plus
`local/research/M33/REPORT.md` (decile-seat machinery +
dec-9 mode: shared-tail decile histogram dec 0–5:0 / 6:1 /
7:2 / 8:6 / 9:85, dec-9 85/94 = 0.9043; s0 tail deciles
6:2 / 7:2 / 8:6 / 9:92; per-shape seats) plus
`local/research/M19/REPORT.md` (P(δ>0) 0.8093/0.8019 + s0 P1
edges `0 1 2 2 4 6 8 12 18 29 176`).

## Estimator (`m57.py`, `control.py`)

Shared core (M56 `m56.py` verbatim where reused: YUYV 640x448
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
carrier removed masks (res0 & ~ress on Y, M22-verbatim)).
Byte offset o -> row o//1280; Y bytes at o%4==0/2.

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
- Far-row census (M56-verbatim, FAR_THRESH=100 pinned): per
  frame per column, d(r) = nearest-neighbor row gap within
  the same column same frame (singleton n==1 → d=N/A,
  excluded from far/null ranking); far = d≥100; null-5 =
  top-5 non-far by d desc (pooled s0+m15, d defined, <100).
- Seat (s0-anchored, M33/M56-verbatim): band = ROW_BAND[r];
  decile = s0 mid-Y P1 decile at (r,c) (`dec_s0[r,c]`,
  edges guarded vs m18 constants); streak = Y-column in the
  named-9 set {257,277,296,301,321,340,341,342,343} else
  `other`; carrier = inside/outside each M22-verbatim top-10
  removed mask (shapes [694,693,701,368,369,366,370,376,748,
  750]) + the 701 split (in/out); peak seat = column-frame
  first-tie argmax peak row (`hump_metrics` verbatim), far
  site at-peak? tabled per seat-6 site.
- Shared tail S = T_s0 ∩ T_m15 (Y-plane intersection;
  s0+m15 analog of the M33 s0∩s9 shared set). Per-frame
  splits: s0 tail-Y, m15 tail-Y. Pooled = multiset union
  (s0 sites + m15 sites, shared sites counted twice —
  disclosed; Jaccard tabled alongside).
- M33 reference histogram (cited, not recomputed — different
  frames s0/s9): shared dec 0–5:0 / 6:1 / 7:2 / 8:6 / 9:85
  (n=94, dec-9 0.9043). Tabled as the context column in
  Task 1.2; mismatch N/A (citation, disclosed).

M56 pins (must reproduce or stop, §Guards):

- Far: m15 (289,343), δ −15, |δ| 15, d=262 (lo 27, hi None),
  band 1, dec 3, streak 343, carrier-none (n_in 0/10),
  701-out, peak 289, at-peak True. Offsets: o=370606 Y.
- Null-5 (m56.txt order, d desc): s0 c313 r292 d16 δ−16
  (lo 276, hi None); s0 c332 r295 d9 δ+10 (lo None, hi 304);
  s0 c332 r304 d9 δ−12 (lo 295, hi None); s0 c314 r269 d7
  δ+12 (lo None, hi 276); m15 c311 r317 d3 δ+9 (lo None,
  hi 320).
- Census margins: pooled far n=1, null max d=16,
  n_nonfar=221, singletons 6 s0 + 8 m15, 33 union cols.

Seat-6 helpers (factored for the control to import):

- `seat_of(frame, r, c, cols, dec_plane, masks)`: returns
  (band, dec, streak, carrier_in list, split701, peakrow,
  atpeak) via the pinned machinery above. `dec_plane` is
  (H,W) int deciles; `masks` maps shape → (H,W) bool.
- `decile_hist(sites, dec_plane)`: sites = list of (r,c);
  returns per-decile counts 0–9 + n + dec-9 share +
  mode dec + modal share. Pure function of the plane.
- Dump path calls both with `dec_s0`/`masks` from
  `compute_dec_masks`; control path calls both with a
  synthetic plane + synthetic sites (identical code path).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float shares printed `:.4f`.

### Task 1 — seat reproduction (do the 6 seats reproduce?)

Far seat + null-5 recomputed from the dumps (must match M56
exactly — far dec 3 / band 1 / streak 343 / none / out /
at-peak; null-5 frame/col/row/d/δ — or table the mismatch
and stop; §Guards):

1. Seat-6 table: far + null-5 rows with band + s0-P1 decile +
   streak + carrier + 701 + at-peak + d + δ (M33 machinery
   on 6 sites, via `seat_of` + M56 census d/δ/lo/hi).
2. Decile-context table: each site's decile against the M33
   shared-tail decile histogram (dec-9 85/94 mode — where
   does dec-3 sit? where do the null-5 deciles sit? cited
   counts + shares per decile alongside the seat-6 marks).
3. Distance-decile table: d vs decile for the 6 (does decile
   track distance from the band? d desc order).

### Task 2 — decile-margin census (is dec-3 off-mode?)

1. Tail-decile table: full s0+m15 tail-Y decile histogram
   recomputed (M33 shared + per-frame splits — dec-9 share
   on each frame?): per-decile counts for s0 tail-Y (n=102),
   m15 tail-Y (n=134), shared-Y S (n tabled), pooled (n=236),
   each with dec-9 share + mode + modal share (via
   `decile_hist`).
2. Margin table: far dec-3's distance from the mode in rank
   and share (how many tail sites share dec-3? null-5
   deciles' shares?): per-scope (s0 / m15 / shared / pooled)
   rank of dec-3 by count desc (ties tabled), count + share
   at dec-3, count + share at the mode, gap (mode−dec3 in
   count and share points); null-5 deciles' per-scope
   counts + shares alongside.
3. Column table: decile seats by column for c343 + the 4
   null columns (313/332/314/311 — do far/null columns
   differ from the tail mode?): per column per frame the
   tail-Y n + per-site (row, δ, dec) rows + column dec-9
   share + modal dec; pooled-null-4 vs c343 vs pooled-tail
   dec-9 shares tabled (H7 input).

### Task 3 — controls + determinism (M18–M56 precedent)

`control.py` (imports `m57` seat/histogram core;
expectations analytic hand-computed; pure-synthetic dec
plane + site lists, NOT dump-injected — deviation reasoned
per M53/M56: seats/histograms operate on (plane, sites),
so a synthetic plane exercises the identical code path
with zero dump coupling; band/peak legs use the real
ROW_BAND/hump path on synthetic rows, disclosed):

- C-DEC1: synthetic truth with KNOWN decile seats on a
  6×12 synthetic plane (rows 0–5, cols 0–11):
  - Plane: col 0–5 read dec 9 (mode block, 36 cells);
    col 6–7 read dec 3 (off-mode block, 12 cells);
    col 8 reads dec 6, col 9 reads dec 7, col 10 reads
    dec 8, col 11 reads dec 0 (singleton-decile columns,
    6 cells each).
  - Sites: M1–M6 mode sites at (0,0) (1,1) (2,2) (3,3)
    (4,4) (5,5) — want dec 9 ×6; F1–F3 off-mode sites at
    (0,6) (1,7) (2,6) — want dec 3 ×3; E1–E3 edge sites
    at (0,8) (0,9) (0,10) — want dec 6/7/8.
  - Want: per-site deciles exact (12 sites); histogram
    over the 12 sites exact ({0:0,1:0,2:0,3:3,4:0,5:0,
    6:1,7:1,8:1,9:6}, n=12, dec-9 share 0.5000, mode 9
    @0.5000, dec-3 rank 2 @0.2500); band seats exact via
    ROW_BAND on rows 0–5 (all band 0); streak seats exact
    (all synthetic cols <257 → other); carrier N/A
    synthetic (no masks — disclosed, no expectation).
  - Pass = seats + histogram + shares + ranks exact.

Determinism: re-run Task 1 seat-6 on s0+m15 (far census +
null-5 + `seat_of` rows + Task-2 histograms, fresh loads);
canonical-text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m56.txt`
sha (tabled; parsed far/null values guarded per §Guards —
non-guarding sha comparison, tabled). Model-0 recompute:
R_0/fnv must match M17–M56 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table. R_s vs `loo.txt` cross-check on s0 (want equal;
mismatch = stop and table, M22 precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_TAILMODE (pooled tail dec-9 mode): pooled s0+m15
  tail-Y dec-9 share ≥ 0.50.
- H2_S0MODE (s0 tail dec-9 mode): s0 tail-Y dec-9 share
  ≥ 0.50.
- H3_M15MODE (m15 tail dec-9 mode): m15 tail-Y dec-9 share
  ≥ 0.50.
- H4_FARDEC9 (far site dec-9; M56 H5 re-test): among pooled
  far sites (n=1), the share with s0-P1 decile == 9 is
  ≥ 0.50.
- H5_NULLDEC9 (null-5 dec-9): among the null-5, the share
  with s0-P1 decile == 9 is ≥ 0.50.
- H6_FARUNIQUE (dec-3 discriminates seat-6): the far site's
  decile differs from all 5 null-5 deciles.
- H7_COLDIFF (far column vs null columns): |c343 pooled
  (s0+m15) tail-Y dec-9 share − null-4-column pooled
  tail-Y dec-9 share| ≥ 0.25 (null-4 = 313/332/314/311).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum δ)
exact per the M56 table below (all 9 cols incl. c341);
m56.txt far/null guard: recomputed far site (frame/col/row/
d/δ/lo/hi) + null-5 (frame/col/row/d/δ/lo/hi, d-desc order)
+ far seat (band/dec/streak/carrier-none/701-out/peak/
at-peak) vs `m56.txt` census lines (mismatch → stop,
tabled); δ≠0 throughout cell 7; P(δ>0)==M19/M20 0.8093/
0.8019; tail planes Y/U/V 102/0/0 s0 + 134/0/0 m15
(non-Y tabled, census-gating disclosed); `loo.txt` 764 rows
+ top-10 shapes/shares; s0 P1 edges match m18.txt s0 row;
carrier removed counts + bands (M19 values); self Jaccard
== 1.0. M33 histogram values tabled as cited (mismatch N/A,
citation disclosed); Task 2 joins the measured values.

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

1. Input shas + `m56.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Task 1: far census recompute + m56.txt far/null/seat
   guard (mismatch → stop); seat-6 table; decile-context
   table (M33 cited); distance-decile table.
4. Task 2: tail-decile histograms (s0 / m15 / shared /
   pooled) + margin table + column table (c343 + 313/332/
   314/311).
5. Determinism re-run receipt (Task 1 + Task 2 on s0+m15,
   canonical sha).
6. PNG decile map (320x224, <5 MB total) to work dir:
   pooled s0∪m15 tail-Y sites colored by decile class
   (red = far site; yellow = null-5; green = dec-9 tail;
   gray = other-decile tail; precedence red > yellow >
   green > gray); evidence copy ONLY if H6_FARUNIQUE meets
   (far decile unique among seat-6 — the pre-registered
   seat-6 split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 08:06 EDT, stop by 12:06).
