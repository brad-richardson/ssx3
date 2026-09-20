# M56 — Design (recorded before running)

Goal: far-row tail-site census (M25 gap 3 via M26 gap 6, taken
on orchestrator judgment): one m15 c343 tail site 262 rows
below its column's band (hole span 28–288), also m15 c343's
argmax peak. Is 289 alone? ALL tail sites sitting ≥100 rows
from their column's band limits on s0+m15 (which columns? how
far? what δ?) + the 289 site's full value row (|δ|, gaps,
signs, band/decile seats, streak/carrier). Answer by table.
Tables, no verdicts. Fully offline: no lease of any kind, no
boots, no harness runs, no fork changes, no `adb`. Desktop
only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles), `/Volumes/Extreme SSD/m25/m25.txt`
(c343 rows + 289 site to reproduce — match exactly per §Guards
or table the mismatch and stop). Work dir: `/Volumes/Extreme
SSD/m56/` (new). Evidence: `local/research/M56/` (committed
with `git add -f`, prefix `[M56]`, trailer `Orchestrated-By:
Muse Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M25/REPORT.md` (all of it:
m15 c343 rows [25,26,27,289], δ values, hole span 28–288,
peak 289; s0 c343 rows [26,27]; row→δ lists) plus
`local/research/M26/REPORT.md` (m15 c343 peak 289, TRI p=289)
plus `local/research/M51/REPORT.md` (r289 peak err_x −16 under
s0 peak; c343 kept hit = m15 r27) plus `local/research/M54/
REPORT.md` (QUAD near-flat fit res 0 at r289) plus
`local/research/M27/REPORT.md` + `M33/REPORT.md` + `M35/
REPORT.md` (per-site value + s0-anchored join method reused
verbatim: offset/plane/row/col, cross-frame |δ|, signed gaps
both frames, band/decile/streak/carrier).

## Estimator (`m56.py`, `control.py`)

Shared core (M26 `m26.py` verbatim where reused: YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median`
(halves away from zero), `coarse_hist`, `exact_counts`,
`hole_ranges`, `count_runs`, `quadfit` (OLS [r²,r,1] float64
lstsq), `rhalf` (half-away), `trifit`/`tri_apply` (symmetric
triangle, first-tie peak, integer w SSE), `hump_metrics`
(first-tie peak — argmax input); M33 `m33.py` verbatim where
reused: `bands_of`/`ROW_BAND` (geometry thirds via
`np.array_split(arange(448),3)` → band0 r0–149, band1 r150–298,
band2 r299–447), `p1_gradient` (M18 P1 block verbatim),
carrier removed masks (res0 & ~ress on Y, M22-verbatim)).
Byte offset o -> row o//1280; Y bytes at o%4==0/2. Y offset
of (r,c): o=r*1280+(c//2)*4+(0 if c even else 2).

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
- Signed gap g = v0−full (int16, ≠0 on moved sites, hence on
  all tail sites).
- Column membership = all tail-Y sites with Y-column == c.
  Non-Y tail sites (expect 0 both frames) tabled if any but
  excluded from the Y-column census (disclosed).
- Named columns (c343 scope): c343 (this brief; c341
  membership-guarded: 0 s0 / 1 m15 at r280). Census scope:
  ALL tail-Y columns on s0+m15 (named + unnamed).
- 289 site pins (must reproduce or stop, §Guards): m15
  (289,343), δ −15, |δ| 15, m15 c343 argmax peak row 289
  (first-tie), TRI p=289 (full 289/−15/−22/1), QUAD res 0
  under the near-flat fit (a≈+0.01), hole span 28–288
  (261 holes, 262-row gap below the 25–27 band).
- m15 c343 pins: rows [25,26,27,289] (n=4, sum −97),
  rowdelta 25:−22 26:−34 27:−26 289:−15, holes 28–288
  (nholes=261). s0 c343 pins: rows [26,27] (n=2, sum −57),
  rowdelta 26:−31 27:−26, holes none.

### Far-row definition (pinned, threshold pinned)

For each frame f ∈ {s0,m15}, for each Y column c bearing ≥1
tail site on f, let rows_f(c) sorted ascending, n=|rows_f(c)|.

- If n==1: distance d=N/A (singleton: no band; cannot be far
  by construction; tabled as singleton, excluded from the
  far/null ranking).
- Else: d(r) = min_{r' ∈ rows_f(c), r'≠r} |r − r'|
  (nearest-neighbor row gap within the same column same
  frame — the distance to the nearest other tail row in its
  column band). For m15 c343 r289: rows [25,26,27,289],
  d=289−27=262.
- Band limits for site (f,r,c) with n≥2: lo=max{r'<r} if any
  else None; hi=min{r'>r} if any else None. d=min(r−lo if lo
  else INF, hi−r if hi else INF). Hole span on the far side:
  if lo is the nearer (or only) neighbor above: rows
  lo+1..r−1 (count r−lo−1); if hi nearer below: r+1..hi−1.
- Far-row site = d ≥ 100 (FAR_THRESH=100, pinned). Primary
  scope per-frame (each site judged against its own frame's
  column rows). Pooled-union rows (s0∪m15 per column) tabled
  as auxiliary (does the far site stay far pooled?).
- Auxiliary distances (tabled alongside d, not gating): d_out
  = distance outside the rest interval (0 if min_rest<r<
  max_rest with n≥3, else gap to the nearest rest edge;
  for n==2 equals d); d_lim = min(|r−min_rest|,|r−max_rest|)
  over rest rows (for edge far sites all three coincide;
  interior splits tabled if any).
- Null set: top-5 non-far sites by d desc (pooled s0+m15,
  d defined and <100, singletons excluded). REQUIRED table
  if pooled far count ≤1 (brief: if 289 alone); always
  tabled (auxiliary when far ≥2).
- Peak seat (H7 input, auxiliary): per far column-frame,
  first-tie argmax peak row (hump_metrics verbatim); far
  site at-peak? tabled per far site.

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float paths via
rhalf(x)=sign(x)·floor(|x|+0.5).

### TRI/QUAD (M26-verbatim, pinned, comparison tabled)

- TRI: p=peak row (argmax δ, first on ties); h=δ(p);
  e=min(first δ, last δ) row order; if h==e → pred=h, w=1,
  flat; elif Wmax<1 → pred=h; else w=argmin SSE over integer
  w∈1..Wmax (ties → smallest), SSE on unrounded
  e+(h−e)·max(0,1−|r−p|/w), Wmax=max(p−minrow,maxrow−p);
  pred(r)=rhalf of that. Pins: s0 c343 27/−26/−31/1, m15
  c343 289/−15/−22/1 (M51).
- QUAD: OLS on (row,δ) over present rows, design [r²,r,1]
  float64 lstsq → (a,b,c); pred(r)=rhalf(a·r²+b·r+c); n<3
  → CONST fallback (expect s0 c343 n=2 only). Pins: m15
  c343 a/b/c=+0.007831/−2.419882/+30.284514 (6dp, M54),
  res=δ−pred=0 at r289; s0 c343 CONST-fb.
- Mismatch on TRI/QUAD pins tabled with M51/M54 comparison
  (not stopping; stopping set is rows/δ/peak/hole per
  §Guards).

### 289 value row (M33–M35 machinery on 1 site, pinned)

For m15 offset o=(289,343) Y (o=370606):

- |δ_m15| (=15), m15 status tail (by construction).
- s0 status at o ∈ {tail, bulk, noncell} (tail impossible
  for privates in M27 sets but possible here — handled, not
  asserted): if tail → |δ_s0|≥8; if bulk → |δ_s0|<8 with
  near (|δ|∈{6,7}) / far (≤5); if noncell → n/a.
- Signed gaps g_m15 vs g_s0 (int16, always defined) + abs +
  signed equality + abs equality + gap signs (+/−/0 both).
- Band seat = ROW_BAND[289] (=1, geometry thirds).
- Decile seat = P1 decile on s0 mid-Y at (289,343)
  (s0-anchored, M22-verbatim call, edges guarded vs m18.txt
  s0 row "0 1 2 2 4 6 8 12 18 29 176").
- Streak seat = Y-column membership in the named-9 set
  {257,277,296,301,321,340,341,342,343} + other (c343
  named).
- Carrier seats = inside/outside each M22-verbatim top-10
  removed mask (res0 & ~ress on Y; shapes
  [694,693,701,368,369,366,370,376,748,750]) + the 701
  split (in/out).

### Task 1 — 289-site reproduction (does the site reproduce?)

m15 c343 recomputed from the dumps (must match M25/M26
exactly — rows [25,26,27,289], δ values, peak 289, hole
span 28–288 — or table the mismatch and stop; §Guards):

1. c343 table: both frames' rows + δ + argmax (first-tie
   peak row/val) + TRI p/h/e/w + QUAD a/b/c/res per site
   (M51/M54 cited values reproduced? tabled).
2. 289 value row: |δ|, bulk status, signed gaps both
   frames, gap signs, band + decile seats, streak/carrier
   (§fields above).
3. Isolation table: 262-row gap itemized (nearest band row
   above =27 with δ; nearest tail row below =none, 289 is
   max; hole rows 28–288 contents: per-frame bulk vs
   noncell counts over the 261 hole offsets in column 343
   + any bulk rows listed with |δ|; pooled-union
   auxiliary).

### Task 2 — far-row census (is 289 alone?)

1. Census table: all s0+m15 tail sites with d≥100 (frame,
   column, row, d, δ, lo/hi, hole span/count + auxiliary
   d_out/d_lim/pooled-d — threshold FAR_THRESH=100 pinned
   above; if 289 alone, the next-5 nearest as the null
   set, always tabled).
2. Seat table: each far site's band/decile/streak/carrier
   (s0-anchored §machinery; do far sites share seats?) +
   peak seat auxiliary (far at argmax?).
3. Column table: far-site counts by column (s0 far / m15
   far / pooled far per column + total tail n per column
   per frame + singleton-column counts; is c343 the only
   far-row column? distinct far columns tabled).

### Task 3 — controls + determinism (M18–M55 precedent)

`control.py` (imports `m56` far/census/band core;
expectations analytic hand-computed; pure-synthetic
row→δ lists, NOT dump-injected — deviation reasoned per
M53/M54: far census operates on row→δ lists, so synthetic
lists exercise the identical code path with zero dump
coupling; gaps/decile/carrier N/A synthetic, disclosed):

- C-P1: synthetic truth with KNOWN far sites, 4
  pseudo-columns (rows ascending):
  - F1 (far, c343-mirror, col 343): rows [25,26,27,289] δ
    [−22,−34,−26,−15]. Want: d=[1,1,1,262], far=[289]
    (d 262, δ −15, lo 27, hi None, hole 28–288 ×261),
    band seats [0,0,0,1], peak 289 (first-tie argmax
    −15), far-at-peak True.
  - F2 (second far, col 257): rows [30,31,200] δ
    [20,22,−18]. Want: d=[1,1,169], far=[200] (d 169,
    δ −18, lo 31, hi None, hole 32–199 ×168), band
    seats [0,0,1], peak 31 (argmax 22), far-at-peak
    False.
  - B1 (band, no far, col 301): rows [23,24,25,26,27] δ
    [10,12,14,12,10]. Want: d all 1, far [], band all
    0, peak 25 (argmax 14), null top d=1.
  - S1 (singleton, col 372): rows [100] δ [12]. Want: d
    N/A, far [], singleton, band 0, peak 100,
    far-at-peak False (N/A d).
  - Pooled: far count 2 (F1:289 d262, F2:200 d169),
    distinct far cols 2 (343,257), null top-5 all d=1,
    |δ| lists exact, holes exact, band seats exact.
  - Pass = far sets + d + δ + lo/hi + holes + |δ| +
    band seats + peak seats exact on all 4; decile/
    carrier N/A synthetic (tabled, no expectation).

Determinism: re-run Task 1 on s0+m15 (cell-7 + tail +
c343 profiles + TRI/QUAD fits + 289 value + isolation
lines, fresh loads); canonical-text sha byte-identical
pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m25.txt`
sha (tabled; must equal M26's record `dbbe5d66…567f63b3`
prefix or table the mismatch — non-guarding comparison,
tabled). Model-0 recompute: R_0/fnv must match M17–M55
(22815/13418, `6b9ffda25bd76c6f` / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check
on s0 (want equal; mismatch = stop and table, M22
precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_FARONE (289 alone): pooled far (d≥100) count == 1.
- H2_FARCOL (c343 only): distinct far columns == 1.
- H3_ISOLATED (null far below): largest non-far d (defined,
  <100, pooled s0+m15, singletons excluded) ≤ 50.
- H4_FARNEG (far sites negative): among pooled far sites,
  the share with δ<0 is ≥ 0.50.
- H5_FARDEC9 (far sites dec-9): among pooled far sites, the
  share with s0-anchored P1 decile == 9 is ≥ 0.50.
- H6_FARBAND1 (far sites band-1): among pooled far sites,
  the share with band == 1 is ≥ 0.50.
- H7_FARPEAK (far sites at peaks): among pooled far sites,
  the share at their column-frame first-tie argmax peak is
  ≥ 0.50.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum δ)
exact per the M25/M26 table below (all 9 cols incl. c341);
m25.txt c343 guard: colguard n/rows/sum + prof rowdelta +
holes per frame vs `m25.txt` c343 lines (mismatch → stop,
tabled); c343 peak guard: first-tie argmax 27/−26 s0 +
289/−15 m15 (mismatch → stop, tabled); δ≠0 throughout cell
7; P(δ>0)==M19/M20 0.8093/0.8019; tail planes Y/U/V
102/0/0 s0 + 134/0/0 m15 (non-Y tabled, census-gating
disclosed); `loo.txt` 764 rows + top-10 shapes/shares; s0
P1 edges match m18.txt s0 row; carrier removed counts +
bands (M19 values); self Jaccard == 1.0. TRI p/h/e/w +
QUAD a/b/c/res + txt sha tabled as measured with M51/M54
comparison (mismatch tabled, not stopping; Task 1.2/1.3 +
Task 2 join the measured values).

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

1. Input shas + `m25.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Task 1: c343 profiles + m25.txt c343 guard (mismatch →
   stop) + peak guard (mismatch → stop); TRI/QUAD refits +
   comparison (tabled); 289 value row; isolation table.
4. Task 2: far census + null set + seats + columns.
5. Determinism re-run receipt (Task 1 on s0+m15, canonical
   sha).
6. PNG far-row map (320x224, <5 MB total) to work dir, m15
   tail-Y sites colored by far outcome (red far d≥100 /
   green band non-far / gray singleton-N/A); evidence copy
   ONLY if pooled far count ≥ 2 (census discriminates with
   ≥2 far sites in a specific pre-registered count split)
   — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 07:55 EDT, stop by 11:55).
