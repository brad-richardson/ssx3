# M55 — Design (recorded before running)

Goal: CONST cross-frame collapse (M25 gap 2 via M26 gap 5, taken
on orchestrator judgment): s0 column medians score 0/68 on m15
(1/65 the other way) vs 12/13 same-frame. Per-column median
drift tables (Δmedian = m15 − s0 per column + drift-vs-kept-hit
join — which columns keep hits under drift?) + the 0/68 anatomy
(near 2 + err distribution of s0 medians on m15). Answer by
table. Tables, no verdicts. Fully offline: no lease of any kind,
no boots, no harness runs, no fork changes, no `adb`. Desktop
only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles), `/Volumes/Extreme SSD/m25/m25.txt`
(medians + scores to reproduce: 8+8 medians + fallbacks,
same-frame 12/65 + 13/68 with nears 14/14, cross-frame 0/68 +
1/65 with nears 2/4 — match exactly per §Guards or table the
mismatch and stop), `/Volumes/Extreme SSD/m26/m26.txt` (M26
TRI p/h per column per frame — the argmax-peak input to the
median-vs-peak table; pins below, non-guarding comparison).
Work dir: `/Volumes/Extreme SSD/m55/` (new). Evidence:
`local/research/M55/` (committed with `git add -f`, prefix
`[M55]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M25/REPORT.md` (all of it:
M25 gap 2 = this brief via M26 gap 5; s0 column medians score
0/68 on m15, 1/65 the other way, vs 12/13 same-frame; 65/68
named-column bytes, row→δ lists, shape stats) plus
`local/research/M26/REPORT.md` (all of it: CONST-vs-M25 median
guard match=True both frames; TRI p/h/e/w + hump peak
row/value table — the peaks Task 2.3 joins).

## Estimator (`m55.py`, `control.py`)

Shared core (M51 `m51.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median` (halves
away from zero), `coarse_hist`, `exact_counts`, `hole_ranges`,
`count_runs`, `task1_profile_lines` (M25-format prof/shape
lines). Byte offset o -> row o//1280; Y bytes at o%4==0/2. No
P1 carrier machinery (no POS/carrier task here). `trifit`/
`tri_apply` dropped (CONST-only brief; disclosed here — input
integrity still rests on the per-column membership guard +
R_0/fnv + cell/tail guards + the M25 fit-line match guard).

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
integer paths exact (CONST is exact-integer throughout; no
float path in this run outside shape-stat sds).

### CONST fit (M25-verbatim, pinned — median rule)

Column-constant: per-column int_median(δ) of fit-frame tail
sites in that column. int_median (M25 verbatim): sort ascending
ints; odd n → middle; even n → mean of the two middles with
halves away from zero (s=m1+m2; s≥0 → (s+1)//2, else
−((−s+1)//2)).

- The brief's "fallback for n<3?" is pinned from M25's
  `fit_frame` BEFORE running: CONST has NO n<3 fallback —
  n<3→CONST is QUAD-only (M26), n<2→CONST is LINEAR-only
  (M25); CONST applies int_median to every nonempty column
  as-is, including s0 c343 (n=2). The only CONST fallback is
  the empty-column fallback: fit frame's global int_median δ
  over all named-column tail bytes. Empties tabled; expect
  none among the 8 on s0/m15.
- Fallback values pinned (computed regardless, used iff a
  column is empty): 27 s0 / 20 m15.

M25 CONST pins to reproduce (c257…c343 order):

- s0 medians: [29,27,35,32,26,41,−17,−29], fallback 27.
- m15 medians: [19,19,37,23,28,38,−19,−24], fallback 20.

Scoring (M25-verbatim): hit = δ' == δ exactly. Near-hit =
|δ'−δ| ≤ 1 and not exact. Near-hits tabled separately, never
merged. Miss |err| distribution: exact |err| value counts in
the receipt + coarse bins 2–3/4–7/8–15/16+. Signed err =
pred − δ (`%+d` in site rows). Per-column hit breakdowns in
the receipt (drift-vs-keep + PNG decision input).

M25 CONST score pins to reproduce:

- Same-frame: s0 12/65 hits + 14 near + miss 8/11/13/7;
  m15 13/68 hits + 14 near + miss 9/11/15/6.
- Same-frame colhits s0: c257 4, c277 2, c296 1, c301 1,
  c321 3, c340 0, c342 1, c343 0 (of 10/10/9/11/10/8/5/2).
- Same-frame colhits m15: c257 2, c277 3, c296 2, c301 1,
  c321 2, c340 2, c342 1, c343 0 (of 10/10/9/11/10/9/5/4).
- Cross-frame fit-s0→m15: 0/68 hits + 2 near + miss
  16/15/24/11; colhits all 0.
- Cross-frame fit-m15→s0: 1/65 hits + 4 near + miss
  13/15/22/10; colhits c340=1 rest 0.
- Errvalues fit-s0→m15: 1:2 2:7 3:9 4:2 5:6 6:1 7:6 8:4 9:5
  10:2 11:4 12:3 13:1 14:3 15:2 16:2 17:1 19:4 20:1 21:1
  25:1 27:1. Errvalues fit-m15→s0: 0:1 1:4 2:9 3:4 4:3 5:2
  6:6 7:4 8:3 9:10 10:7 11:1 14:1 16:2 17:1 18:2 21:2 22:1
  23:1 24:1.

### Drift + kept hits + medpeak + xerr (M55 §Task 2, pinned)

Per column c: Δ = med_m15 − med_s0 (signed, m15 − s0).
|Δ| rank: descending |Δ|; ties → smaller column first.
Kept hits per column: k_s0m15 = fit-s0→m15 CONST colhits on
m15, k_m15s0 = fit-m15→s0 CONST colhits on s0,
pooled kept = k_s0m15 + k_m15s0 (per column; the
drift-vs-kept join key). Low-drift = |Δ|≤2 (fixed threshold,
H4 input — cf. M51's L1≤5 low-drift rule).
Kept-hit site rows: for every cross-frame CONST hit,
(direction, col, row, δ, pred). Near-hit site rows: for every
cross-frame CONST near (|err|==1), (direction, col, row, δ,
pred, signed err) — the near-2 + near-4 named.
Median-vs-peak: CONST median vs M26 TRI peak per column per
frame (p/h parsed from `m26.txt` `fit {tag} TRI:` lines):
median==h? + signed med−h. Per-column xerr: mean|err| (3dp) +
max|err| of cross-frame CONST per column per direction.

M26 peak pins (p/h per column; non-guarding comparison):

- s0: 257 25/30, 277 25/28, 296 26/47, 301 27/47,
  321 25/27, 340 26/47, 342 27/−16, 343 27/−26.
- m15: 257 25/20, 277 25/20, 296 26/46, 301 27/48,
  321 26/31, 340 32/48, 342 27/−13, 343 289/−15.

Receipt formats (new lines; fit/score/xframe lines stay
M25-identical):

- `xkept {tag}: c={c} r={r} d={d} pred={p}` +
  `xkept {tag}: nrows={n}` (M51-identical; tag =
  fit-s0->m15 | fit-m15->s0).
- `xnear {tag}: c={c} r={r} d={d} pred={p} err={e:+d}` +
  `xnear {tag}: nrows={n}` (signed err = pred − δ).
- `drift c={c}: s0={m0} m15={m1} delta={d:+d} abs={a}
  rank={r}`.
- `driftx c={c}: abs={a} low={low} sames0={h0}/{n0}
  samem15={h1}/{n1} k_s0m15={k1}/{n1} k_m15s0={k2}/{n0}
  pooled={p}`.
- `medpeak {tag} c={c}: med={m} p={p} h={h} eq={eq}
  med-h={d:+d}`.
- `xerr {tag} c={c}: n={n} meanabs={m:.3f} maxabs={M}`
  (tag = fit-s0->m15 | fit-m15->s0).

### Task 1 — CONST reproduction (do the medians + scores reproduce?)

CONST medians + scores recomputed M25-verbatim from the dumps
(must match exactly — 8+8 medians, 12/65 + 13/68, 0/68 + 1/65,
nears 14/14 + 2/4 — or table the mismatch and stop; §Guards):

1. Median table: all 8 columns × s0/m15 medians + fallback
   rows (which columns use fb? — expect none) + M25
   fit-line match (byte-exact vs `m25.txt` `fit s0 CONST` /
   `fit m15 CONST` lines, parsed medians + fallbacks per
   column; mismatch → stop, tabled).
2. Same-frame table: CONST hits/near/miss per frame with
   per-column colhits (12 + 13 reproduced; hit+near count
   mismatch → stop, tabled; miss/errvalues/colhits tabled
   as measured with M25 comparison).
3. Collapse table: fit-s0→m15 0/68 (near-2 rows named) +
   fit-m15→s0 1/65 (the 1 kept hit named) + errvalues +
   near-site rows both directions (hit+near+colhit
   mismatch → stop, tabled; errvalues tabled as measured
   with M25 comparison).

### Task 2 — median drift (which columns drift? who keeps hits?)

1. Drift table: Δmedian per column (m15 − s0) + |Δ| rank
   (which column drifts most? least?).
2. Drift-vs-keep table: per-column |Δmedian| vs same-frame
   colhits vs cross-frame kept hits (do low-drift columns
   keep hits? — cf. M51's L1 finding; joins the measured
   colhits/kept hits).
3. Median-vs-peak table: CONST medians vs M26 argmax peaks
   per column per frame (median==peak? median-vs-TRI-p?
   — medians measured, peaks parsed from `m26.txt` with
   pin comparison).

### Task 3 — controls + determinism (M18–M54 precedent)

`control.py` (imports `m55` median/drift core; expectations
analytic hand-computed; pure-synthetic row→δ lists, NOT
dump-injected — deviation reasoned per M53/M54: median/drift
logic operates on row→δ lists, so synthetic lists exercise
the identical code path with zero dump coupling):

- C-P1: synthetic truth with KNOWN medians + KNOWN drift,
  N=4 pseudo-columns × frames A/B (rows ascending):
  - P1 (odd n=5): A δ 8 10 12 10 8 → med 10; B δ 9 12 14
    12 9 → med 12; drift +2, abs 2.
  - P2 (even n=4, positive halves): A δ 8 10 12 14 →
    middles 10+12=22 → med 11; B δ 9 11 13 15 → middles
    11+13=24 → med 12; drift +1, abs 1.
  - P3 (even-negative, n=2 A / n=4 B): A rows 26,27 δ
    −31 −26 → s=−57 → med −29; B rows 25,26,27,289 δ
    −22 −34 −26 −15 → sorted −34,−26,−22,−15, middles
    −26+−22=−48 → med −24; drift +5, abs 5.
  - P4 (even n=10, c257-shaped): A δ 17 28 30 29 29 29 29
    28 23 13 → sorted 13,17,23,28,28,29,29,29,29,30,
    middles 28+29=57 → med 29; B δ 12 18 20 20 19 20 20
    19 16 8 → sorted 8,12,16,18,19,19,20,20,20,20,
    middles 19+19=38 → med 19; drift −10, abs 10.
  - |Δ| rank (desc, ties → name order): P4(10) r1, P3(5)
    r2, P1(2) r3, P2(1) r4.
  - Pass = medians A/B + drifts + abs + ranks exact on
    all 4.

Determinism: re-run Task 1 on s0+m15 (cell-7 + tail + CONST
fits + same-frame/xframe scores); canonical-text sha (fit +
score + xframe + drift + driftx lines) byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
`m25.txt` (sha must equal `dbbe5d66…567f63b3` per M26's record
or table the mismatch — non-guarding comparison, tabled) +
`m26.txt` (bytes + sha recorded; sha must equal M51's record
`9a3d522b…060ff8f8` prefix or table the mismatch —
non-guarding comparison, tabled). Model-0 recompute: R_0/fnv
must match M17–M54 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_COLLAPSE (CONST collapses cross-frame): the s0-fit CONST,
  scored on m15, reads an m15 exact-hit rate within 0.15
  (absolute) of its s0 exact-hit rate.
- H2_BIGDRIFT (medians drift): among the 8 named columns, the
  share with |Δmedian|≥5 is ≥ 0.50 (≥4/8).
- H3_SMALLDRIFT (some medians hold): among the 8 named
  columns, the share with |Δmedian|≤2 is ≥ 0.25 (≥2/8).
- H4_LOWDRIFTKEEPS (low drift keeps hits — cf. M51's L1
  finding): among columns with |Δmedian|≤2, the share with
  pooled kept hits ≥1 is ≥ 0.50.
- H5_MEDPEAK (median equals peak): among the 16 col-frames,
  the share with CONST median == M26 TRI peak value h is ≥
  0.25 (≥4/16).
- H6_ERRMASS (0/68 errs run large): among the 68 fit-s0→m15
  |err|, the share with |err|≥8 is ≥ 0.50 (≥34/68).
- H7_MAXDRIFT (c257 drifts most): argmax |Δmedian| over the 8
  named columns is c257 (ties → tabled, bar not met on tie).
- N (standing remainder + drift attribution): named-column
  tail after CONST exact hits + drift attribution — the
  deliverable whatever the bars read (attribution, not
  explanation: drift tables attribute the collapse; 0 new
  bytes explained beyond M25 CONST).

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; per-column membership
(n, minrow, maxrow, sum δ) exact per the M25/M26 table below;
M25 CONST fit-line match (8+8 medians + fallbacks exact vs
`m25.txt` — mismatch → stop, tabled); same-frame CONST
hits+nears 12+14 / 13+14 exact (mismatch → stop, tabled);
cross-frame CONST hits+nears+colhits 0+2+allzero / 1+4+c340
(mismatch → stop, tabled); δ≠0 throughout cell 7;
P(δ>0)==M19/M20 0.8093/0.8019; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0. Miss bins / errvalues /
same-frame colhits / M26 peak pins / txt shas tabled as
measured with M25/M26 comparison (mismatch tabled, not
stopping; Task 2 joins the measured values).

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
3. Task 1: CONST fits + M25 fit-line match guard (mismatch →
   stop); same-frame CONST scores + hit+near guard (mismatch
   → stop); cross-frame both directions + hit+near+colhit
   guard (mismatch → stop); kept-hit + near-hit site rows.
4. Task 2: drift table + drift-vs-keep + median-vs-peak +
   per-column xerr.
5. Determinism re-run receipt (Task 1 on s0+m15 + drift
   lines, canonical sha).
6. PNG drift-collapse map (320x224, <5 MB total) to work dir,
   s0 named-column sites colored by fit-m15→s0 kept-hit
   outcome (green=kept / red=lost, M51-identical); evidence
   copy ONLY if some s0 named column with n≥8 reads pooled
   cross-frame kept hits ≥ 3 (collapse survival visible in
   a specific pre-registered-split column) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 07:45 EDT, stop by 11:45).
