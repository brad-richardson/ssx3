# M51 — Design (recorded before running)

Goal: TRI cross-frame collapse (M26 gap 1 via M29 gap 11, taken
on orchestrator judgment): TRI fit-s0→m15 reads 4/68 (2/65 the
other way) vs 18/16 same-frame — the CONST-collapse phenomenon
at shape level. Per-column triangle-drift tables (Δp/Δh/Δe/Δw
s0 vs m15 per column — which TRI leg collapses?) + collapse
recount (which columns keep hits cross-frame?). Answer by
table. Tables, no verdicts. Fully offline: no lease of any
kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme
SSD/m15/` (triplet, column profiles), `/Volumes/Extreme
SSD/m26/m26.txt` (the 8×2 TRI fits + TRI scores to reproduce:
p/h/e/w per column per frame + same-frame 18/16 + cross-frame
4/68 + 2/65 with per-column colhits — match exactly per §Guards
or table the mismatch and stop). Work dir: `/Volumes/Extreme
SSD/m51/` (new). Evidence: `local/research/M51/` (committed
with `git add -f`, prefix `[M51]`, trailer `Orchestrated-By:
Muse Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M26/REPORT.md` (all of it:
TRI 18/65 s0 + 16/68 m15 exact hits, cross-frame 4/68 + 2/65,
8×2 p/h/e/w fits, per-column colhits, miss bins, errvalues) plus
`local/research/M25/REPORT.md` (all of it: CONST collapse +
peak-anchored residual method, 65/68 named-column bytes,
row→δ lists, CONST 12/65 + 13/68, cross-frame 0/1).

## Estimator (`m51.py`, `control.py`)

Shared core (M26 `m26.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median` (halves
away from zero), `coarse_hist`, `exact_counts`, `hole_ranges`,
`count_runs`. Byte offset o -> row o//1280; Y bytes at
o%4==0/2. No P1 carrier machinery (no POS/carrier task here).
`quadfit`/`twolevel`/`hump_metrics` unused here (TRI-only brief;
dropped, disclosed here — input integrity still rests on the
M26 profile-line guard + R_0/fnv + cell/tail/column guards).

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

### TRI fit (M26-verbatim, pinned)

Column-triangle (symmetric): p = peak row (argmax δ, FIRST
occurrence on ties); h = δ(p); e = min(first δ, last δ) in
row order; if h==e → pred=h everywhere, w=1, flat flag tabled;
elif Wmax<1 (n=1) → pred=h (tabled; expect none); else w =
argmin SSE over integer w∈1..Wmax (ties → smallest w), SSE on
unrounded e+(h−e)·max(0,1−|r−p|/w),
Wmax=max(p−minrow,maxrow−p); pred(r)=rhalf of that; p/h/e/w
tabled per column. Empty-column fallback (recorded; expect
none among the 8 on s0/m15): fit frame's global int_median δ
over all named-column tail bytes. Empties + flat flags tabled.

M26 TRI pins to reproduce (s0 then m15, c257…c343 order):

- s0: 25/30/13/7, 25/28/13/7, 26/47/15/8, 27/47/13/6,
  25/27/11/7, 26/47/17/8, 27/−16/−17/1, 27/−26/−31/1.
- m15: 25/20/8/7, 25/20/8/7, 26/46/16/8, 27/48/12/4,
  26/31/14/6, 32/48/14/8, 27/−13/−21/4, 289/−15/−22/1.

Scoring (M26-verbatim): hit = δ' == δ exactly. Near-hit =
|δ'−δ| ≤ 1 and not exact. Near-hits tabled separately, never
merged. Miss |err| distribution: exact |err| value counts in
the receipt + coarse bins 2–3/4–7/8–15/16+. Per-column hit
breakdowns in the receipt (collapse + PNG decision input).

M26 TRI score pins to reproduce:

- Same-frame: s0 18/65 hits + 8 near + miss 8/9/14/8;
  m15 16/68 hits + 5 near + miss 12/20/9/6.
- Same-frame colhits s0: c257 3, c277 2, c296 2, c301 3,
  c321 2, c340 2, c342 2, c343 2 (of 10/10/9/11/10/8/5/2).
- Same-frame colhits m15: c257 3, c277 2, c296 2, c301 2,
  c321 2, c340 1, c342 2, c343 2 (of 10/10/9/11/10/9/5/4).
- Cross-frame fit-s0→m15: 4/68 hits + 8 near; colhits c257 1,
  c277 1, c296 0, c301 0, c321 0, c340 1, c342 0, c343 1.
- Cross-frame fit-m15→s0: 2/65 hits + 11 near; colhits c257 1,
  c277 0, c296 0, c301 0, c321 0, c340 1, c342 0, c343 0.

### Drift (M51 §Task 2, pinned)

Per column c: Δp = p_m15 − p_s0, Δh = h_m15 − h_s0,
Δe = e_m15 − e_s0, Δw = w_m15 − w_s0 (signed, m15 − s0).
L1 drift = |Δp|+|Δh|+|Δe|+|Δw| (integer, per column).
Low-drift = L1 ≤ 5 (fixed threshold, H6 input).
Kept hits per column: k_s0m15 = fit-s0→m15 TRI colhits on
m15, k_m15s0 = fit-m15→s0 TRI colhits on s0,
pooled kept = k_s0m15 + k_m15s0 (per column; the
drift-vs-collapse join key). Kept-hit site rows: for every
cross-frame TRI hit, (direction, col, row, δ, pred) — the
collapse recount at site level.

### Task 1 — TRI fit reproduction (do the 8×2 fits reproduce?)

TRI fits recomputed M26-verbatim from the dumps (must match
exactly — p/h/e/w per column per frame + same-frame hit counts
18/16 — or table the mismatch and stop; §Guards):

1. Fit table: all 8 columns × s0/m15 p/h/e/w (16 fits) +
   flat/empty flags + M26 line-match (byte-exact vs `m26.txt`
   `fit s0 TRI` / `fit m15 TRI` lines, parsed p/h/e/w per
   column; mismatch → stop, tabled).
2. Same-frame score table: TRI hits/near/miss-bins per frame
   (18 + 16 reproduced with miss bins + errvalues +
   per-column colhits? mismatch on hits → stop, tabled;
   near/miss/errvalues/colhits tabled as measured with M26
   comparison).
3. Collapse table: fit-s0→m15 hits (4/68) + fit-m15→s0 hits
   (2/65) with per-column kept-hit colhits both directions +
   kept-hit site rows (which columns keep hits cross-frame?
   measured with M26 comparison; mismatch tabled, not
   stopping — Task 2 joins the measured kept hits).

### Task 2 — triangle drift (which leg collapses?)

1. Drift table: Δp/Δh/Δe/Δw (m15 − s0) per column + L1 per
   column (which leg drifts most? peak p? height h?).
2. Drift-vs-collapse table: per-column L1 vs kept hits
   (k_s0m15 / k_m15s0 / pooled — do low-drift columns keep
   hits?).
3. c343/c342 table: the negative columns' fits + drifts +
   row→δ + TRI predictions per row per frame (c343's m15
   p=289 vs s0 p=27 — the peak jump itemized at site level:
   rows, δ, same-frame pred/err, cross-frame pred/err).

### Task 3 — controls + determinism (M18–M50 precedent)

`control.py` (imports `m51` cell/tail/core; expectations
analytic; feasibility per M25's lesson: interior ⇒ strict
inside, so injections need per-site strict-inside
verification; staging probe confirmed ≥8 passing pool sites
per control row in M26, need 2 — probe counted pool coverage
only, no profiles/fits/results):

- C-P1: synthetic truth mid'_A + mid'_B on s0 (same
  v0/full/synth as s0, different mids): M25 union pool
  (interior-BULK gap≥17 + ENDPOINT gap≥32, offset order),
  distinct rows 26..30, N=2 pseudo-columns × 5 sites (one
  per row per pseudo-col, 10 offsets total, shared across
  frames A/B):
  X listed-A TRIANGLE δ = 8,10,12,10,8 over rows
  26,27,28,29,30 (p=28,h=12,e=8,w=2);
  X listed-B DRIFTED δ = 9,12,14,12,9 (p=28,h=14,e=9,w=2;
  known drift Δ=0/+2/+1/0);
  Y listed-A TRIANGLE δ = 8,10,12,10,8 over rows
  26,27,28,29,30 (p=28,h=12,e=8,w=2);
  Y listed-B PEAK-SHIFTED δ = 8,8,10,12,10 (p=29,h=12,
  e=8,w=2; known drift Δ=+1/0/0/0).
  Scan pool in offset order; offsets with row outside
  26..30 ignored (not skips); in-span offset fills X's row
  slot if free and BOTH listed-A and listed-B δ fit
  strictly inside, else Y's if free and both fit, else
  skips+=1 (while either slot free). Shortfall → tabled
  stop (expect none). Per-site checks: currently non-tail
  (pool ⇒ non-tail), BOTH injected values strictly inside
  (v0,full), |δ|≥8 both (min listed 8 ✓).
  Recompute cell 7 + tail from (v0,mid'_A,full) and
  (v0,mid'_B,full): each recomputed tail set must equal
  T_s0 ∪ injected exactly (count 112 + values + map),
  original tail members' δ unchanged on both frames.
  Profile recovery: per-pseudo-col row→δ lists must read
  the listed shapes exactly on both frames. Fits: trifit
  per pseudo-col per frame must recover the 4 known
  p/h/e/w exactly (X-A 28/12/8/2, X-B 28/14/9/2, Y-A
  28/12/8/2, Y-B 29/12/8/2). Drift: Δ per pseudo-col must
  equal the known drift exactly (X 0/+2/+1/0, Y
  +1/0/0/0). Pass = sets + values + originals + profiles +
  4 fits + 2 drifts exact. Full-control-frame TRI fits on
  named columns tabled (no expectation — injections are
  outside named-column tail sets by pool construction;
  n Hit counts tabled as measured).

Determinism: re-run Task 1 (cell-7 + tail + TRI fits on
s0+m15 + drift lines); canonical-text sha + fits byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
`m26.txt` sha (tabled; no prior pin — bytes + sha recorded).
Model-0 recompute: R_0/fnv must match M17–M50 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_PEAKSTABLE (peaks stable): among the 8 named columns,
  the share with Δp==0 is ≥ 0.50 (≥4/8).
- H2_HEIGHTDRIFT (height drifts): among the 8 named columns,
  the share with |Δh|≥5 is ≥ 0.50 (≥4/8).
- H3_EDGEDRIFT (edge drifts): among the 8 named columns, the
  share with |Δe|≥3 is ≥ 0.50 (≥4/8).
- H4_WIDTHSTABLE (width stable): among the 8 named columns,
  the share with Δw==0 is ≥ 0.50 (≥4/8).
- H5_COLLAPSE (TRI collapses cross-frame): the s0-fit TRI,
  scored on m15, reads an m15 exact-hit rate within 0.15
  (absolute) of its s0 exact-hit rate.
- H6_LOWDRIFTKEEPS (low drift keeps hits): among columns
  with L1≤5, the share with pooled kept ≥1 is ≥ 0.50.
- H7_NEGPEAK (c343 peak jump): c343 |Δp|≥100 (m15 p=289 vs
  s0 p=27 itemized).
- N (standing remainder + attribution): named-column tail
  after TRI exact hits + drift attribution — the deliverable
  whatever the bars read (attribution, not explanation:
  drift tables attribute the collapse legs; 0 new bytes
  explained beyond M26 TRI).

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; per-column membership
(n, minrow, maxrow, sum δ) exact per the M25/M26 table below;
M26 TRI fit-line match (16/16 p/h/e/w exact vs `m26.txt` —
mismatch → stop, tabled); same-frame TRI hits 18/65 + 16/68
exact (mismatch → stop, tabled); δ≠0 throughout cell 7;
P(δ>0)==M19/M20 0.8093/0.8019; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0. Near/miss/errvalues/
colhits/cross-frame counts tabled as measured with M26
comparison (mismatch tabled, not stopping).

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
3. Task 1: TRI fits + M26 fit-line match guard (mismatch →
   stop); same-frame TRI scores + hit-count guard (mismatch
   → stop); cross-frame both directions + kept-hit site rows.
4. Task 2: drift table + drift-vs-collapse + c342/c343 site
   tables.
5. Determinism re-run receipt (Task 1 TRI fits on s0+m15,
   canonical sha).
6. PNG drift-collapse map (320x224, <5 MB total) to work dir,
   s0 named-column sites colored by pooled cross-frame
   kept-hit outcome (green=kept in either direction /
   red=lost both); evidence copy ONLY if some s0 named
   column with n≥8 reads pooled cross-frame kept hits ≥ 3
   (collapse survival visible in a specific
   pre-registered-split column) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 07:06 EDT, stop by 11:06).
