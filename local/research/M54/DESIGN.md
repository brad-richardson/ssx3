# M54 — Design (recorded before running)

Goal: QUAD underfit (M26 gap 4, taken on orchestrator judgment):
smooth quadratic reads 4/65 + 3/68 with 32/23 mass in the 2–3
miss bin — below TWO and CONST on both frames despite ∩
curvature on every positive column. Per-column quadratic-residual
tables (residual = δ − QUAD pred per site — where does the
smooth fit fail? at peaks? at holes? in runs?) + the 2–3-bin
census (which columns hold the 32/23 mass?). Answer by table.
Tables, no verdicts. Fully offline: no lease of any kind, no
boots, no harness runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles), `/Volumes/Extreme SSD/m26/m26.txt`
(the 8×2 QUAD fits + QUAD scores to reproduce: a/b/c per column
per frame + same-frame 4/65 + 3/68 with per-column colhits —
match exactly per §Guards or table the mismatch and stop). Work
dir: `/Volumes/Extreme SSD/m54/` (new). Evidence:
`local/research/M54/` (committed with `git add -f`, prefix
`[M54]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M26/REPORT.md` (all of it:
QUAD 4/65 s0 + 3/68 m15 exact hits, miss mass 32/23 in 2–3,
8×2 a/b/c fits, per-column colhits, miss bins, errvalues) plus
`local/research/M51/REPORT.md` (TRI 18/16 for the fit
comparison — QUAD 4/3 vs TRI 18/16 vs TWO 15/13 vs CONST
12/13).

## Estimator (`m54.py`, `control.py`)

Shared core (M26 `m26.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median` (halves
away from zero), `coarse_hist`, `exact_counts`, `hole_ranges`,
`count_runs`, `quadfit` (OLS [r²,r,1] float64 lstsq),
`rhalf` (half-away), `trifit`/`tri_apply`, `twolevel`/`two_apply`
(ladder only), `hump_metrics` (first-tie peak — seat input),
`fit_frame`, `apply_fit`, `named_truth`, `score_fit_lines`. Byte
offset o -> row o//1280; Y bytes at o%4==0/2. No P1 carrier
machinery (no POS/carrier task here).

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
- Named columns (profiles + fits): c ∈
  {257,277,296,301,321,340,342,343} (the brief's 8; c341 is
  membership-guarded but not profiled/scored: 0 s0 / 1 m15
  sites). Column membership = all tail-Y sites with Y-column
  == c. Named-column tail bytes: want 65 s0 / 68 m15 (implied
  by the per-column guard rows).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float paths via
rhalf(x)=sign(x)·floor(|x|+0.5).

### QUAD fit (M26-verbatim, pinned)

Column-quadratic: OLS on fit-frame (row, δ) pairs per column
over present rows: design [r²,r,1] float64 lstsq → (a,b,c);
pred(r)=rhalf(a·r²+b·r+c); a/b/c tabled per column (6dp); n<3
falls back to CONST (tabled; expect s0 c343 n=2 only).

M26 QUAD a pins (c257…c343 order; full a/b/c 6dp matched
against parsed `m26.txt` fit lines at runtime):

- s0 a: [−0.69,−0.64,−0.40,−1.16,−0.68,−1.39,+0.21,fb].
- m15 a: [−0.48,−0.48,−0.87,−1.14,−0.80,−0.94,−0.02,+0.01].

M26 QUAD score pins to reproduce:

- Same-frame: s0 4/65 hits + 8 near + miss 32/14/6/1;
  m15 3/68 hits + 18 near + miss 23/12/12/0.
- Same-frame colhits s0: c257 1, c277 1, c296 0, c301 0,
  c321 2, c340 0, c342 0, c343 0 (of 10/10/9/11/10/8/5/2).
- Same-frame colhits m15: c257 1, c277 0, c296 0, c301 1,
  c321 0, c340 0, c342 0, c343 1 (of 10/10/9/11/10/9/5/4).
- Errvalues s0: 0:4 1:8 2:20 3:12 4:8 5:4 6:1 7:1 8:1 9:2
  11:1 12:1 13:1 18:1. Errvalues m15: 0:3 1:18 2:18 3:5 4:2
  5:2 6:3 7:5 9:4 10:4 11:2 14:1 15:1.

Fit-ladder pins (M26, comparison — not guards): TRI 18/65 +
16/68, TWO 15/65 + 12/68, CONST 12/65 + 13/68, with M26
per-column colhits (s0 TRI 3/2/2/3/2/2/2/2, TWO 3/5/1/1/2/0/1/2,
CONST 4/2/1/1/3/0/1/0; m15 TRI 3/2/2/2/2/1/2/2, TWO
2/3/1/1/3/1/1/0, CONST 2/3/2/1/2/2/1/0).

### Residuals + seats + census + curvature (M54 §Task 2, pinned)

Per named-column tail site, same-frame QUAD (fit frame = score
frame):

- pred = QUAD prediction (rhalf; CONST value on fb columns).
- res = δ − pred (SIGNED; note the sign is opposite to M26's
  err = pred − δ — pinned here, applied everywhere).
- abs = |res|.
- seat: peak if row == first-tie peak row (`hump_metrics`
  verbatim argmax, first on ties) of its column-frame; else
  edge if row == minrow or maxrow present; else interior.
  Precedence peak > edge > interior (a peak at a band edge
  labels peak). One label per site.
- holeadj: True if row−1 or row+1 within [minrow,maxrow] is
  absent from present rows (boolean, alongside the seat).
- 2–3-bin site: abs ∈ {2,3}.
- Sign classes: pos (res>0, δ>pred, underpredict), neg
  (res<0, overpredict), zero (hit).
- Curvature depth: depth = −a × span², span = maxrow − minrow
  over present rows (positive for ∩ since a<0); fb columns
  (n<3): depth N/A, tabled. Spread per column: mean|res|
  (4dp) + max|res|.

Receipt formats (new lines; fit/score lines stay M26-identical):

- `res {tag} c={c}: n={n} sites=[row:d/pred/res/abs/seat/hole
  ...]` with res `%+d` (e.g. `23:17/15/+2/2/edge/0`).
- `mass23 {tag}: c257={m}/10 ... pooled={M}` (2–3 mass per
  column + frame pooled).
- `census {tag}: n23={n} sites=[c:row:res:seat ...]` (|res|
  implied ∈{2,3}; res `%+d`).
- `census {tag} seats: peak={p} edge={e} interior={i}
  holeadj={h}` + `census pooled: n23={n} peak={p} edge={e}
  interior={i} holeadj={h}`.
- `curve {tag} c={c}: a={a:.6f} span={s} depth={d:.4f}
  meanabs={m:.4f} maxabs={M}` (fb: `... c={c}: CONST-fb
  depth=N/A meanabs=.. maxabs=..`).
- `ressign {tag}: nres={n} pos={p} neg={g} zero={z}` +
  `ressign pooled: nres={n} pos={p} neg={g} zero={z}`.
- `ladder {tag} c={c}: QUAD={h}/{n} TRI={h}/{n} TWO={h}/{n}
  CONST={h}/{n}`.

### Task 1 — QUAD reproduction (do the fits + scores reproduce?)

QUAD fits recomputed M26-verbatim from the dumps (must match
exactly — a/b/c 6dp per column per frame + 4/65 + 3/68 — or
table the mismatch and stop; §Guards):

1. Fit table: all 8 columns × s0/m15 a/b/c (16 fits + the
   s0-c343 fb + m15 ~0 curvatures) + M26 fit-line match
   (byte-exact vs `m26.txt` `fit s0 QUAD` / `fit m15 QUAD`
   lines, parsed a/b/c per column; mismatch → stop, tabled).
2. Score table: QUAD hits/near/miss-bins per frame (4 + 3
   with 32/23 in 2–3 — which columns? via `mass23`) with
   errvalues + per-column colhits (hit-count mismatch →
   stop, tabled; near/miss/errvalues/colhits tabled as
   measured with M26 comparison).
3. Fit-ladder table: QUAD 4/3 vs TRI 18/16 vs TWO 15/13 vs
   CONST 12/13 per column (TRI/TWO/CONST refit M26-verbatim;
   where is QUAD worst? measured with M26 comparison;
   mismatch tabled, not stopping).

### Task 2 — quadratic residuals (where does smooth fail?)

1. Residual tables: per site δ − QUAD pred + |res| per column
   per frame (`res` lines: row/δ/pred/res/abs/seat/holeadj —
   peaks? holes? runs?).
2. 2–3-bin census: the 32 s0 + 23 m15 sites with |res|∈{2,3}
   by column + row seat (`census` lines: peak rows? band
   edges? + holeadj + pooled seat split).
3. Curvature table: per-column ∩ depth (−a×span²) vs residual
   spread (mean|res| + max|res|) per column per frame (does
   deeper ∩ mean worse fit? `curve` lines).

### Task 3 — controls + determinism (M18–M53 precedent)

`control.py` (imports `m54` quad/residual/seat/census/depth
core; expectations analytic hand-computed, OLS recovery
tolerance pre-checked on synthetic vectors only — max |Δ|
3.5e-11 at 1e-6 tolerance; pure-synthetic row→δ lists, NOT
dump-injected — deviation reasoned per M53: residual logic
operates on row→δ lists, so synthetic lists exercise the
identical code path with zero dump coupling):

- C-P1: synthetic truth with KNOWN quadratics, N=2 parabolic
  + N=2 non-parabolic pseudo-columns (rows 26..30 asc);
  recover the fit + residual tables exactly.
  - P1 (parabolic): d = 8 11 12 11 8 = 8+(r−26)(30−r).
    Want: a/b/c = (−1, 56, −772) ±1e-6; preds 8 11 12 11 8;
    res 0 0 0 0 0; QUAD 5/5; census {}; seats
    edge/interior/peak/interior/edge; holeadj all False;
    depth 16.0 ±1e-4 (span 4).
  - P2 (parabolic): d = 16 19 20 19 16 = 20−(r−28)².
    Want: a/b/c = (−1, 56, −764) ±1e-6; preds exact; res all
    0; QUAD 5/5; census {}; seats edge/interior/peak/
    interior/edge; holeadj all False; depth 16.0 ±1e-4.
  - T1 (triangle, non-parabolic): d = 8 10 12 10 8. Want:
    a/b/c = (−6/7, 48, −23124/35) ±1e-6; preds 8 10 11 10 8;
    res 0 0 +1 0 0; QUAD 4/5; census {}; seats
    edge/interior/peak/interior/edge; holeadj all False;
    depth 96/7 ≈ 13.7143 ±1e-4.
  - T2 (asymmetric, non-parabolic): d = 8 9 12 10 8. Want:
    a/b/c = (−11/14, 44.1, −607.8285714285714) ±1e-6; preds
    8 10 11 10 8; res 0 −1 +1 0 0; QUAD 3/5; census {};
    seats edge/interior/peak/interior/edge; holeadj all
    False; depth 88/7 ≈ 12.5714 ±1e-4.
  - Pass = a/b/c (within tol) + preds + res + census +
    seats + holeadj + depths (within tol) exact on all 4
    pseudo-columns.

Determinism: re-run Task 1 on s0+m15 (fits + scores + ladder
lines both frames); canonical-text sha byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
`m26.txt` (bytes + sha recorded; sha must equal M51's record
`9a3d522b…060ff8f8` prefix or table the mismatch — non-guarding
comparison, tabled). Model-0 recompute: R_0/fnv must match
M17–M53 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_QUADLAST (QUAD fits worst): QUAD exact hits are fewest
  among QUAD/TRI/TWO/CONST on s0 AND on m15.
- H2_MASS23 (2–3 mass pooled): pooled QUAD 2–3-bin sites ≥ 50
  (pins 32+23=55).
- H3_PEAKSEAT (failures at peaks): among pooled 2–3 sites,
  the share at peak rows is ≥ 0.50.
- H4_EDGESEAT (failures at band edges): among pooled 2–3
  sites, the share at band edges (non-peak) is ≥ 0.50.
- H5_SIGNBIAS (underpredict bias): among pooled nonzero QUAD
  residuals, the share with res>0 (δ>pred) is ≥ 0.60.
- H6_DEPTH (deepest ∩ fits worst): on s0, the column with max
  ∩ depth reads max mean|res| (fb column excluded).
- H7_ZEROCOL (QUAD scoreless columns): among s0 named
  columns, the share with 0 QUAD hits is ≥ 0.50.
- N (standing remainder + residual attribution): residual +
  census + curvature tables + named-col tail after M26 TRI
  hits (18/16 explained, 0 new — attribution, not
  explanation) + remaining split — the deliverable whatever
  the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; per-column membership
(n, minrow, maxrow, sum δ) exact per the M25/M26 table below;
M26 QUAD fit-line match (16/16 a/b/c 6dp exact vs `m26.txt` —
mismatch → stop, tabled); same-frame QUAD hits 4/65 + 3/68
exact (mismatch → stop, tabled); δ≠0 throughout cell 7;
P(δ>0)==M19/M20 0.8093/0.8019; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0. Near/miss/errvalues/
colhits/ladder counts tabled as measured with M26 comparison
(mismatch tabled, not stopping).

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
3. Task 1: QUAD fits + M26 fit-line match guard (mismatch →
   stop); same-frame QUAD scores + hit-count guard (mismatch
   → stop); ladder refits + per-column tables.
4. Task 2: residual tables + 2–3 census + curvature table +
   sign table.
5. Determinism re-run receipt (Task 1 on s0+m15, canonical
   sha).
6. PNG residual map (320x224, <5 MB total) to work dir, s0
   named-column sites colored by QUAD |res| bin (green hit /
   yellow near / orange 2–3 / red 4+); evidence copy ONLY if
   some s0 named column with n≥8 reads QUAD 2–3 mass ≥ 6
   (concentrated underfit visible in a specific
   pre-registered-split column) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 07:36 EDT, stop by 11:36).
