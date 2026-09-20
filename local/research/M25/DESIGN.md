# M25 — Design (recorded before running)

Goal: within-streak-column δ profiles (M23 gap 2): streak columns
read single-sign δ means (22.7–36.5 positive except c342/343
negative) but per-row δ gradients along the r23–33 columns are
untabled beyond receipt δ lists. Is δ constant along a column
(one value), graded (top-to-bottom slope), or ragged (per-row
noise)? And do the two frames' profiles match column-by-column?
Per-row δ profiles + column-gradient fits on the FIXED list
below — no additions mid-run (M20/M23 precedent). Tables, no
verdicts. Fully offline: no lease of any kind, no boots, no
harness runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m22/m22.txt` + M23's streakcol
table (column membership to reproduce: per-column n/rows/means —
match exactly or table the mismatch and stop). Work dir:
`/Volumes/Extreme SSD/m25/` (new). Evidence:
`local/research/M25/` (committed with `git add -f`, prefix
`[M25]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M23/REPORT.md` (all of it:
102/134 tail, streak columns c257/277/296/301/321/340–343 with
per-column n/rows/means, full δ dlists in `m23.txt`) plus
`local/research/M24/REPORT.md` (column r-coherence tables: c257
r∈{−3,−2,0}, c296 all |r|≤1, c342 all r≥1 — the residual-level
precedent for column-local structure).

## Estimator (`m25.py`, `control.py`)

Shared core (M24 `m24.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `k45mag`,
`int_median` (halves away from zero), `coarse_hist`,
`exact_counts`. Byte offset o -> row o//1280; Y bytes at
o%4==0/2. No P1 carrier machinery (no POS/carrier task here).

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
- Named columns (profiles + fits): c ∈
  {257,277,296,301,321,340,342,343} (the brief's 8; c341 is
  membership-guarded but not profiled/scored: 0 s0 / 1 m15
  sites). Column membership = all tail-Y sites with Y-column
  == c. Named-column tail bytes: want 65 s0 / 68 m15 (implied
  by the per-column guard rows).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, LINEAR float path via
rhalf(x)=sign(x)·floor(|x|+0.5).

### Fixed fit list (3 fits, no additions mid-run)

Each fit predicts δ' per named-column tail site from constants
fit on the fit frame. Hit = δ' == δ exactly. Near-hit =
|δ'−δ| ≤ 1 and not exact. Near-hits tabled separately, never
merged. Miss |err| distribution: exact |err| value counts in
the receipt + coarse bins 2–3/4–7/8–15/16+. Per-column
hit breakdowns in the receipt (PNG decision input).

| id | formula |
| --- | --- |
| CONST | column-constant: per-column int_median(δ) of fit-frame tail sites in that column (M23 int_median verbatim: even-n mean-of-middles, halves away from zero) |
| LINEAR | column-linear: ordinary least squares on fit-frame (row, δ) pairs per column: b=Sxy/Sxx, a=δ̄−b·r̄ (float64); pred(r)=rhalf(a+b·r); slope+intercept tabled per column (4dp); n<2 or Sxx==0 falls back to CONST (tabled; expect none) |
| SIGNC | column-sign × gap magnitude: sign_col · |K45+(g_site)|, where sign_col = sign of the fit-frame column mean δ (+1 if mean>0, −1 if mean<0, +1 if ==0 — tabled if hit) and |K45+(g)| = (9|g|+10)//20 at the SCORED site's gap (the brief's "K45+?" pinned: K45+ magnitude, exact integer arith) |

Details:

- Empty-column fallback (recorded; expect none among the 8 on
  s0/m15): fit frame's global int_median δ over all
  named-column tail bytes. Empties tabled.
- Best fit (fixed rule): highest exact-hit count on the s0
  named-column bytes; tie-break: higher m15 exact-hit count;
  then list order (CONST, LINEAR, SIGNC).
- Explained bytes = best fit's exact hits (per frame + pooled
  s0+m15; scope = named-column bytes only, tabled as such).
  Residual = |δ − δ'_best| hist per frame (exact value counts
  in receipt + coarse bins 0/1/2–3/4–7/8–15/16+).

### Task 1 — per-row δ profiles (s0 + m15)

Column membership recomputed from the dumps; per-column
n/rows/sum must match the guard table EXACTLY or table the
mismatch and stop (no further tasks run).

1. Per-row δ lists: per named column per frame: present rows
   sorted with δ (row:δ pairs in the receipt) + holes (rows in
   [min,max] with no tail site, as ranges + hole count).
2. Column shape stats: n, min, max, range, sd (population,
   float64, 3dp), sign runs + value runs (maximal runs over
   present rows in row order; holes do NOT break runs —
   tabled separately), top-half mean vs bottom-half mean
   (row-order split: top = first n//2 = smaller rows,
   bottom = rest; 3dp), full row-order δ list in the receipt.
3. Cross-frame profile match: per column: row sets equal?
   shared-row n, s0-only rows, m15-only rows, δ agreement on
   shared rows (n_agree + all-equal?), mean |Δ| over shared
   rows (3dp; n/a if no shared rows — expect none).

### Task 2 — column-gradient fits (fixed list, exact-hit scoring)

1. Score each of the 3 fits on s0 + m15 named-column tail
   bytes (fit frame = score frame): exact hits / near hits /
   miss |err| distribution. Best fit (rule above): explained
   bytes + residual |err| hist per frame.
2. Cross-frame check: fit constants on s0, score on m15 (and
   vice versa) — tabled both directions. All 3 fits carry
   fitted constants (CONST medians, LINEAR a/b, SIGNC signs),
   so all 3 transfer cells are meaningful (no N/A). No
   cross-shape check (brief asks cross-frame only).

### Task 3 — controls + determinism (M18–M24 precedent)

`control.py` (imports `m25` cell/tail/core; expectations
analytic; feasibility per M22/M24's lesson: interior ⇒ |δ| <
|gap|/2, so injections need per-site strict-inside
verification):

- C-P1: synthetic truth mid' on s0: N=60 sites from the M24
  union pool (interior-BULK gap≥17 + ENDPOINT gap≥32, offset
  order; skips counted), first 30 passing → pseudo-column A
  with listed δ=+10 (constant, listed gradient 0), next 30
  passing → pseudo-column B with listed δ=+14 (constant,
  listed gradient 0). Per-site checks: currently non-tail,
  injected value strictly inside (v0,full), |δ|≥8. Recompute
  cell 7 + tail from (v0,mid',full): the recomputed tail set
  must equal T_s0 ∪ injected exactly (count 162 + values +
  map), original tail members' δ unchanged. Profile recovery:
  pseudo-column row→δ lists + medians must read the listed
  constants exactly (+10/+14). Restricted fits on the
  injected-only (known-truth) set must read CONST 60/60 and
  LINEAR 60/60 (slope exactly 0.0 on constant data, hence
  tie) with argmax = CONST by the pre-registered list-order
  tie-break (identity recovered exactly); SIGNC tabled
  (expect low). Full-control-frame scores (fit on control
  frame) tabled.

Determinism: re-run Task 1 on s0 (cell-7 + tail recompute +
profile tables); canonical-text sha + counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets.
Model-0 recompute: R_0/fnv must match M17–M24 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_CONST (columns are constant): CONST exact-hit rate ≥ 0.30
  on the s0 named-column bytes (≥20/65).
- H2_GRAD (columns are graded): LINEAR exact hits exceed CONST
  exact hits by ≥5 on the s0 named-column bytes.
- H3_SIGNC (columns carry sign, magnitude gap-driven): SIGNC
  exact-hit rate ≥ 0.30 on the s0 named-column bytes (≥20/65).
- H4_XFER (profiles transfer): the s0-best fit, fit on s0 and
  scored on m15, reads an m15 exact-hit rate within 0.15
  (absolute) of its s0 exact-hit rate.
- H5_PROFMATCH (frames share profiles): among shared (col,row)
  sites present on both frames (pooled over named columns),
  exact-δ agreement share ≥ 0.25.
- H6_COLRANGE (within-column spread is small): among s0 named
  columns with n≥4, the share with δ range ≤ 8 is ≥ 0.50.
- N (standing remainder + best fit): named-column tail after
  the best fit's exact hits + remaining split — the
  deliverable whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; per-column membership
(n, minrow, maxrow, sum δ) exact per the table below (sums
derived read-only from `m23.txt` dlists; means = sum/n
reproduce M23's table); δ≠0 throughout cell 7;
P(δ>0)==M19/M20 0.8093/0.8019; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0.

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

(M22's identical-bbox fact cross-checked: c257/277/301/321
row ranges match M22's single-column bboxes r[23,32]/r[23,33]
on both frames.)

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Task 1: per-row δ lists + holes; shape stats; xframe match.
4. Task 2: 3-fit scores; best-fit explained + residual;
   cross-frame both directions.
5. Determinism re-run receipt (Task 1 on s0, canonical sha).
6. PNG column-profile map (320x224, <5 MB total) to work
   dir; evidence copy ONLY if some s0 named column with n≥8
   reads LINEAR col-hits − CONST col-hits ≥ 2 (gradient
   visible in a specific pre-registered-split column) — else
   absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 02:37 EDT, stop by 06:37).
