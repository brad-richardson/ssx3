# M24 — Design (recorded before running)

Goal: K45+ near-hit mass (M23 gap 1): 32 s0 / 49 m15 tail bytes
read |err|=1 under δ=round(0.45·g) vs 14/15 exact (pooled near
81 vs exact 29). If the ±1 residuals carry a sign/position/gap
pattern, a sub-rounding correction converts near-hits to hits.
Residual-sign tables + sub-rounding fits on the FIXED
correction list below — no additions mid-run (M20/M23
precedent). Tables, no verdicts. Fully offline: no lease of any
kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m23/m23.txt` (tail membership +
K45+ scores to reproduce: 102/134 counts, 14/15 exact, 32/49
near — match exactly or table the mismatch and stop). Work dir:
`/Volumes/Extreme SSD/m24/` (new). Evidence:
`local/research/M24/` (committed with `git add -f`, prefix
`[M24]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M23/REPORT.md` (all of it:
102/134 tail, 14/15 exact + 32/49 near under K45+, errvalue
counts s0 `0:14 1:32 2:25 3:12 …` max 93 / m15 `0:15 1:49 …`
max 46, POS medians s0 `[5,27,10,10,15,-2]` m15
`[-14,20,10,-9,15,10]`, streak columns c257/277/296/301/321/
340–343, gap bins 16–31/32–63/64+) plus M22's ρ-regime tables
for the gap-context precedent (ρ peak [0.4,0.5), sign-gap
agreement ~90%).

## Estimator (`m24.py`, `control.py`)

Shared core (M23 `m23.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `bands_of` (thirds via
`np.array_split(arange(448),3)`), `fnv1a`, `parse_loo`, PNG
writer, `plane_of_byte`, `plane_coords`, `p1_gradient` (M18 P1
block verbatim), `jaccard`, `k45mag`, `int_median` (halves away
from zero), `site_cells` (POS cells verbatim), `coarse_hist`,
`exact_counts`. Byte offset o -> row o//1280; Y bytes at
o%4==0/2.

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
- K45+(g) = sign(g)·((9|g|+10)//20) (M23 verbatim,
  = round(0.45·g) half-away-from-zero, exact integer arith).
- Residual r = δ − K45+(g), SIGNED (int64). Near-hit ⟺
  |r|=1; exact ⟺ r=0.

Rounding convention (fixed): round-half-away-from-zero in
exact integer arithmetic (no floats), M23 verbatim.

### Fixed correction list (4 corrections, no additions mid-run)

Each correction predicts δ' = K45+(g) + c(level), where level
is the tail site's level in a FIXED split and c(level) is fit
on the fit frame as:

  c(level) = clamp(int_median(r over fit-frame tail sites in
               the level), −1, +1)

i.e. the M23 median, clamped to a ±1 LSB sub-rounding step.
Hit = δ' == δ exactly. Near-hit = |δ'−δ| ≤ 1 and not exact.
Near-hits tabled separately, never merged. Miss |err|
distribution: exact |err| value counts in the receipt + coarse
bins 2–3/4–7/8–15/16+.

| id | split | levels (fixed) |
| --- | --- | --- |
| SIGN | sign(gap) | `neg` (g<0), `pos` (g>0); fallback level `zero` (g==0, c=0 — expect n=0) |
| FRAC | frac(0.45·g) half | `LO` (frac<0.5), `HI` (frac≥0.5); frac = ((9·g) mod 20)/20, mathematical non-negative mod, exact integer arith: HI ⟺ ((9·g) % 20) ≥ 10 |
| PARITY | gap parity | `even` (\|g\| even), `odd` (\|g\| odd) |
| POS | position cell (M23's POS cells verbatim) | band (M19 thirds 0/1/2) × P1-decile-9/not (M18 P1 verbatim; U/V tail bytes, if any, via co-located Y decile (r,2c)); 6 cells band*2+(dec==9) |

Details:

- Empty-level fallback (recorded; expect none on s0/m15):
  fit frame's global clamped median of r. Empties tabled.
- FRAC % semantics: NumPy `%` with positive divisor yields
  the non-negative remainder (Python convention) — verified
  by construction, no float path anywhere.
- Best correction (fixed rule): highest exact-hit count on
  the s0 tail after correction; tie-break: higher m15
  exact-hit count; then list order (SIGN, FRAC, PARITY, POS).
- Explained bytes = best correction's exact hits (per frame +
  pooled s0+m15). Residual = |δ − δ'_best| hist per frame
  (exact value counts in receipt + coarse bins
  0/1/2–3/4–7/8–15/16+).

### Task 1 — residual-sign tables (s0 + m15)

Tail membership + K45+ residuals recomputed from the dumps;
102/134 + 14/15 exact + 32/49 near must match M23 EXACTLY or
table the mismatch and stop (no further tasks run).

1. Residual-sign joint: per split (SIGN / FRAC / PARITY / POS
   cell — the 4 fixed splits above) per frame: per level, n +
   r-class counts (r=−1 / r=0 / r=+1 / other, where other =
   |r|>1 any sign) + mean r + mean |r| + full signed-r list in
   the receipt. One table per split per frame.
2. (gap, r) joint: residual stats per M23 gap bin (16–31 /
   32–63 / 64+): n + r-class counts + mean r + mean |r| +
   full signed-r list in the receipt.
3. Position join: residual stats per streak column (M23's
   columns verbatim: c ∈ {257,277,296,301,321,340,341,342,343}
   over all tail-Y sites in that column + `other` over
   remaining tail-Y sites) + per band×decile cell (= the POS
   split table from §1, referenced not re-emitted): n +
   r-class counts + mean r + mean |r| + full signed-r list in
   the receipt.

### Task 2 — sub-rounding fits (fixed list, exact-hit scoring)

1. Score each of the 4 corrections on s0 + m15 tail bytes (fit
   frame = score frame): exact hits / near hits / miss |err|
   distribution. Best correction (rule above): explained
   bytes + residual |err| hist per frame.
2. Cross-frame check: fit rule constants (per-level c values)
   on s0, score on m15 (and vice versa) — tabled both
   directions. All 4 corrections carry fitted constants, so
   all 4 transfer cells are meaningful (no N/A).
3. Cross-shape check (cheap): score the best correction on 3
   non-s0 shapes: shapes {1, 2, 733} (M23's 3 verbatim: 1, 2
   per brief; 733 = min-Jaccard shape 0.6694), each shape's
   tail recomputed from its dumps, constants from s0. Table
   per shape: tail n, exact hits, near hits, miss |err|
   coarse hist, Jaccard vs s0 (+ vs m15, M23 precedent).

### Task 3 — controls + determinism (M18–M23 precedent)

`control.py` (imports `m24` cell/tail/core; expectations
analytic; feasibility per M22's lesson: interior ⇒ |δ| <
|gap|/2, so injections need gap ≥ 17 minimum and per-site
strict-inside verification):

- C-R1: synthetic truth mid' on s0: N=60
  currently-interior-BULK sites with gap≥17 (first 60 in
  offset order passing the strict-inside check for the
  injected value; skips counted), injected δ = K45+(g) + r
  with r = +1 where frac(0.45·g) ≥ 0.5 else −1 (the FRAC
  rule; |δ|≥8 verified per site). Recompute cell 7 + tail
  from (v0,mid',full): the recomputed tail set must equal
  T_s0 ∪ injected exactly (count 162 + values + map),
  original tail members' δ unchanged. Residual-pattern
  recovery: r-sign vs frac-half joint on injected sites must
  read the injected rule exactly (HI→+1 all, LO→−1 all).
  Correction fits on the injected-only (known-truth) set;
  restricted scoring on the 60 injected sites must read
  argmax = FRAC unique with 60/60 exact hits (identity
  recovered exactly). Full-control-frame scores (fit on
  control frame) tabled. Non-degeneracy guard: injected r
  takes both values (else tabled, identity N/A).

Determinism: re-run Task 1 on s0 (cell-7 + tail recompute +
residual tables); canonical-text sha + counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets.
Model-0 recompute: R_0/fnv must match M17–M23 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_CORR (sub-rounding converts near-hits): best correction
  exact-hit rate ≥ 0.30 on the s0 tail (≥31/102 — ≥17 net
  converted beyond the 14 K45+ exact hits).
- H2_FRAC (fractional-part mechanism): FRAC correction
  exact-hit rate ≥ 0.25 on the s0 tail (≥26/102).
- H3_SEP (a split separates −1 from +1): some level of some
  fixed split (SIGN/FRAC/PARITY/POS) reads ≥8 s0 |r|=1 sites
  of which ≥0.80 share one sign.
- H4_GAPCONC (±1 mass concentrates by gap): some M23 gap bin
  (16–31/32–63/64+) holds ≥0.50 of the s0 |r|=1 sites (≥16
  of 32).
- H5_XFER (constants transfer): the s0-best correction, fit
  on s0 and scored on m15, reads an m15 exact-hit rate
  within 0.15 (absolute) of its s0 exact-hit rate.
- H6_COLSIGN (column sign coherence): among the 9 named s0
  streak columns with ≥4 |r|=1 sites, the share that are
  single-sign (all +1 or all −1) ≥ 0.50.
- N (standing remainder + best correction): tail after the
  best correction's exact hits + remaining split — the
  deliverable whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; K45+ exact 14/15 +
near 32/49 exact (full errvalue strings printed for eyeball
comparison); δ≠0 throughout cell 7; P(δ>0)==M19/M20
0.8093/0.8019; P1 rounded edges match m18.txt; `loo.txt` 764
rows + top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute + K45+ count guard (102/134 +
   14/15 exact + 32/49 near or stop).
3. Task 1: residual-sign joints (4 splits × 2 frames);
   (gap,r) joints; streak-column joins.
4. Task 2: 4-correction scores; best-correction explained +
   residual; cross-frame both directions; 3-shape transfer.
5. Determinism re-run receipt (Task 1 on s0, canonical sha).
6. PNG residual-sign map (320x224, <5 MB total) to work
   dir; evidence copy ONLY if some Task-1.1 split level
   reads ≥0.80 sign purity with n≥8 on s0 |r|=1 sites (the
   H3 split) AND best-correction hits/misses separate by
   that same split (hit-rate gap ≥0.25 between its most- and
   least-hit levels on s0) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 02:28 EDT, stop by 06:28).
