# M26 — Design (recorded before running)

Goal: within-column hump profiles (M25 gap 1): s0 c257/277/301/321
read rise-then-fall row profiles (e.g. c257 17→30→13, c301
18→47→13) with LINEAR slopes near 0 and top−bottom means within
5 — LINEAR (monotone) scores below CONST (flat) because neither
captures a hump. Per-column hump-shape tables + hump/quadratic
fits on the FIXED list below — no additions mid-run (M20/M25
precedent). Tables, no verdicts. Fully offline: no lease of any
kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m25/m25.txt` (column profiles to
reproduce: per-column row→δ lists + shape stats — match exactly
or table the mismatch and stop). Work dir: `/Volumes/Extreme
SSD/m26/` (new). Evidence: `local/research/M26/` (committed with
`git add -f`, prefix `[M26]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M25/REPORT.md` (all of it:
65/68 named-col bytes, row→δ lists, shape stats, CONST 12/65 +
13/68 with LINEAR below CONST both frames, CONST cross-frame
collapse 0/1) plus M25's Task-1 profile tables in `m25.txt` (the
row→δ lists this run fits).

## Estimator (`m26.py`, `control.py`)

Shared core (M25 `m25.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median` (halves
away from zero), `coarse_hist`, `exact_counts`, `hole_ranges`,
`count_runs`. Byte offset o -> row o//1280; Y bytes at
o%4==0/2. No P1 carrier machinery (no POS/carrier task here).
`k45mag`/`k45pred`/`linfit` unused here (no SIGNC/LINEAR task).

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
- Named columns (profiles + fits): c ∈
  {257,277,296,301,321,340,342,343} (the brief's 8; c341 is
  membership-guarded but not profiled/scored: 0 s0 / 1 m15
  sites). Column membership = all tail-Y sites with Y-column
  == c. Named-column tail bytes: want 65 s0 / 68 m15 (implied
  by the per-column guard rows).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float paths via
rhalf(x)=sign(x)·floor(|x|+0.5).

### Hump metrics (Task 1, pinned, no special-casing)

Per named column per frame, over present rows in row order
(r[0..n-1] ascending, δ[0..n-1]):

- peak = argmax δ, FIRST occurrence on ties. peakrow, peakval.
- first = δ[0] (smallest present row); last = δ[n-1].
- rise = peakval − first; fall = peakval − last;
  sym = |rise − fall|.
- thirds by INDEX: k = argmax index (0-based); top if 3k<n,
  bottom if 3k≥2n, else mid. k/n tabled alongside third.
- Same formulas for all 8 columns both frames, including
  ragged (c296/340) and negative (c342/343) columns — the
  "peak" of a negative column is its least-negative δ.

### Fixed fit list (3 fits, no additions mid-run)

Each fit predicts δ' per named-column tail site from constants
fit on the fit frame. Hit = δ' == δ exactly. Near-hit =
|δ'−δ| ≤ 1 and not exact. Near-hits tabled separately, never
merged. Miss |err| distribution: exact |err| value counts in
the receipt + coarse bins 2–3/4–7/8–15/16+. Per-column
hit breakdowns in the receipt (PNG decision input).

| id | formula |
| --- | --- |
| QUAD | column-quadratic: ordinary least squares on fit-frame (row, δ) pairs per column over present rows: design [r²,r,1] float64 lstsq → (a,b,c); pred(r)=rhalf(a·r²+b·r+c); a/b/c tabled per column (6dp); n<3 falls back to CONST (tabled; expect s0 c343 n=2 only) |
| TRI | column-triangle (symmetric): p = peak row (argmax, first on ties — same as Task 1 peak); h = δ(p); e = min(first δ, last δ) in row order; if h==e → pred=h everywhere, w=1, flat flag tabled; elif Wmax<1 (n=1) → pred=h (tabled; expect none); else w = argmin SSE over integer w∈1..Wmax (ties → smallest w), SSE on unrounded e+(h−e)·max(0,1−\|r−p\|/w), Wmax=max(p−minrow,maxrow−p); pred(r)=rhalf of that; p/h/e/w tabled per column |
| TWO | column-two-level: row-order split (M25 top/bottom convention: top = first n//2 = smaller rows, bottom = rest); pred = int_median(top δ) on top rows, int_median(bottom δ) on bottom rows; medians tabled per column; n<2 falls back to CONST (tabled; expect none — halves are nonempty for all n≥2) |

Details:

- Empty-column fallback (recorded; expect none among the 8 on
  s0/m15): fit frame's global int_median δ over all
  named-column tail bytes. Empties tabled.
- Best fit (fixed rule): highest exact-hit count on the s0
  named-column bytes; tie-break: higher m15 exact-hit count;
  then list order (QUAD, TRI, TWO).
- Explained bytes = best fit's exact hits (per frame + pooled
  s0+m15; scope = named-column bytes only, tabled as such).
  Residual = |δ − δ'_best| hist per frame (exact value counts
  in receipt + coarse bins 0/1/2–3/4–7/8–15/16+).
- CONST baseline (NOT in the fixed list; Task 2.3 + PNG rule
  only): per-column int_median(δ) recomputed M25-verbatim;
  guard: medians must equal M25's table (s0
  [29,27,35,32,26,41,−17,−29], m15
  [19,19,37,23,28,38,−19,−24]) or table the mismatch and stop
  the head-to-head (Task 1/2.1/2.2 already tabled stand).

### Task 1 — profile-shape tables (hump or not?)

Column profiles recomputed from the dumps; row→δ lists +
shape stats must match M25 exactly or table the mismatch and
stop (no further tasks run). Match check: the `prof`
(rowdelta + holes) and `shape` (stats + roworder) receipt
lines, emitted in M25-identical format by the verbatim core,
must equal the corresponding `m25.txt` lines byte-exactly.

1. Hump metrics per named column per frame (§formulas above):
   peak row + value, rise, fall, sym, argmax k/n + third.
2. Non-hump columns tabled the same way (c296/340 ragged,
   c342/343 negative — same metrics, no special-casing).
3. Cross-frame shape match: per column: peak rows s0 vs m15
   (equal?), (rise, fall) pairs s0 vs m15, thirds s0 vs m15.

### Task 2 — hump fits (fixed list, exact-hit scoring)

1. Score each of the 3 fits on s0 + m15 named-column tail
   bytes (fit frame = score frame): exact hits / near hits /
   miss |err| distribution. Best fit (rule above): explained
   bytes + residual |err| hist per frame.
2. Cross-frame check: fit constants on s0, score on m15 (and
   vice versa) — tabled both directions. All 3 fits carry
   fitted constants (QUAD a/b/c, TRI p/h/e/w, TWO medians),
   so all 3 transfer cells are meaningful (no N/A). No
   cross-shape check (brief asks cross-frame only).
3. Beat-the-baseline: best shape fit vs M25 CONST (12/65 +
   13/68) head-to-head per column (col-hits each + diff both
   frames + pooled).

### Task 3 — controls + determinism (M18–M25 precedent)

`control.py` (imports `m26` cell/tail/core; expectations
analytic; feasibility per M25's lesson: interior ⇒ strict
inside, so injections need per-site strict-inside
verification; staging probe confirmed ≥8 passing pool sites
per control row, need 2 — probe counted pool coverage only,
no profiles/fits/results):

- C-P1: synthetic truth mid' on s0: M25 union pool
  (interior-BULK gap≥17 + ENDPOINT gap≥32, offset order),
  distinct rows 26..30, N=10 total: group A (5 sites, one per
  row) with listed TRIANGLE δ = 8,10,12,10,8 over rows
  26,27,28,29,30 (p=28,h=12,e=8,w=2); group B (5 sites, one
  per row) with listed QUADRATIC δ = 8,11,12,11,8 over rows
  26,27,28,29,30 (exactly 8+(r−26)(30−r)). Scan pool in
  offset order; offsets with row outside 26..30 ignored (not
  skips); in-span offset fills group A's row slot if free and
  listed-A δ fits strictly inside, else group B's if free and
  listed-B δ fits, else skips+=1 (while either slot free).
  Shortfall → tabled stop (expect none). Per-site checks:
  currently non-tail (pool ⇒ non-tail), injected value
  strictly inside (v0,full), |δ|≥8 (min listed 8 ✓).
  Recompute cell 7 + tail from (v0,mid',full): the recomputed
  tail set must equal T_s0 ∪ injected exactly (count 112 +
  values + map), original tail members' δ unchanged. Profile
  recovery: per-group row→δ lists must read the listed
  shapes exactly. Restricted fits on injected-only per group:
  A must read TRI 5/5 (w=2, SSE=0 unique min; QUAD 4/5
  expected — OLS vertex value 11.314 rounds to 11 vs listed
  12; TWO 2/5 expected) with argmax TRI; B must read QUAD
  5/5 (exactly quadratic; float residuals ~1e-12 → rhalf
  exact; TRI 3/5 expected at w=2, SSE=2 vs w=1 SSE=18; TWO
  2/5 expected) with argmax QUAD. Pass = profiles exact +
  TRI_A==5/5 + QUAD_B==5/5 + both identities. Full-control-
  frame scores (fit on control frame) tabled for the 3 fixed
  fits (no expectation).

Determinism: re-run Task 1 on s0 (cell-7 + tail recompute +
profile + hump tables); canonical-text sha + counts
byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets.
Model-0 recompute: R_0/fnv must match M17–M25 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_QUAD (columns are quadratic): QUAD exact-hit rate ≥ 0.30
  on the s0 named-column bytes (≥20/65).
- H2_TRI (columns are triangular): TRI exact hits exceed QUAD
  exact hits by ≥5 on the s0 named-column bytes.
- H3_TWO (columns are two-level): TWO exact-hit rate ≥ 0.30
  on the s0 named-column bytes (≥20/65).
- H4_XFER (shape transfers): the s0-best shape fit, fit on s0
  and scored on m15, reads an m15 exact-hit rate within 0.15
  (absolute) of its s0 exact-hit rate.
- H5_PEAKMATCH (frames share peak rows): among the 8 named
  columns, the share with equal s0/m15 peak rows is ≥ 0.50
  (≥4/8).
- H6_HUMP (hump shape prevalent): among s0 named columns with
  n≥4, the share with mid-third argmax AND rise≥3 AND
  fall≥3 is ≥ 0.50.
- H7_BEATCONST (shape beats flat): best shape fit s0 exact
  hits exceed M25 CONST s0 hits (12) by ≥5 (≥17/65).
- N (standing remainder + best fit): named-column tail after
  the best fit's exact hits + remaining split — the
  deliverable whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; per-column membership
(n, minrow, maxrow, sum δ) exact per the M25 table below;
M25 profile-line match (prof/shape lines byte-exact vs
`m25.txt`); CONST medians equal M25's table (for Task 2.3);
δ≠0 throughout cell 7; P(δ>0)==M19/M20 0.8093/0.8019;
`loo.txt` 764 rows + top-10 shapes/shares; self Jaccard == 1.0.

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

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Task 1: per-row δ lists + holes; shape stats; M25
   profile-line match guard (mismatch → stop); hump metrics;
   xframe shape match.
4. Task 2: 3-fit scores; best-fit explained + residual;
   cross-frame both directions; CONST head-to-head per
   column.
5. Determinism re-run receipt (Task 1 on s0, canonical sha).
6. PNG shape-fit map (320x224, <5 MB total) to work
   dir, s0 named-column sites colored by TRI outcome
   (hit/near/miss); evidence copy ONLY if some s0 named
   column with n≥8 reads TRI col-hits − CONST col-hits ≥ 2
   (hump visible in a specific pre-registered-split column)
   — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 02:50 EDT, stop by 06:50).
