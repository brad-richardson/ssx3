# M31 — Design (recorded before running)

Goal: K-boundary sweep (M30 gap 1): no named-column site in any
of the 764 sits at span distance 3–10, so the ±K window is
identical at K=2/5/10 and the rule's stability margin is
unobserved on real data (only synthetic W3 at d+7 flips).
Sweep K below (0, 1 — probe 734-c342's d=1 extras) and above
(15, 20, 50, 100 — find the first real-data flip past K=10, or
table the negative). Tables, no verdicts. Fully offline: no
lease of any kind, no boots, no harness runs, no fork changes,
no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m28/m28.txt` +
`/Volumes/Extreme SSD/m28/m28-census.tsv` (exact-match census
guard: 10 movers / 15 cells / standings),
`/Volumes/Extreme SSD/m30/m30.txt` +
`/Volumes/Extreme SSD/m30/m30-census-K2.tsv` (K=2 windowed
census to reproduce: 8 movers / 13 cells / standings — match
exactly or table the mismatch and stop) +
`/Volumes/Extreme SSD/m30/m30-census-K5.tsv` +
`/Volumes/Extreme SSD/m30/m30-census-K10.tsv` (adjacent-K diff
inputs for K=5,10 — loaded read-only, never recomputed; the
fixed list below is final). Work dir:
`/Volumes/Extreme SSD/m31/` (new). Evidence:
`local/research/M31/` (committed with `git add -f`, prefix
`[M31]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M30/REPORT.md` (all of it:
8 movers / 13 cells at every K in {2,5,10}, row-identical; the
three TSVs byte-identical; off-span exactly the 3 far extras;
0 flipping cells on both adjacent pairs; gap 1 is this brief)
plus `local/research/M30/DESIGN.md` (the ±K window definition,
reused verbatim below) and the M28/M29 DESIGN.md estimator +
bar precedent.

## Estimator (`m31.py`, `control.py`)

Shared core (M30 `m30.py` verbatim where reused):
`synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|δ|≥8 tail), `plane_of_byte`,
`plane_coords`, `parse_loo`, `jaccard`, `off_of`,
`y_col_rows`, `priv_y_cols`, `census_of_shape` (exact-match
presence), `assign_one` (≥2-site private columns,
nearest-column + overlap + smallest tie-breaks), PNG writer.
Byte offset o -> row o//1280; Y bytes at o%4==0/2. No
P1/carrier/BFS machinery (no gradient, carrier, or edge task
here).

Definitions (raw bytes, full 573440-B frame) — M30 verbatim:

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard).
- Bulk = cell-7 bytes with |δ|<8. Tail = cell-7 bytes with
  |δ|≥8. Tail MAP of shape s: T_s = tail boolean mask.
- Named columns (the census 8, fixed order): [257,277,296,301,
  321,340,342,343]. c341 is guard-only (0 s0 sites), outside
  the census.
- s0 reference row lists (M27/M28/M29/M30, guarded exact):
  257:[23–32], 277:[23–32], 296:[24,25,26,27,28,31,32,33,34],
  301:[23–33], 321:[23–32], 340:[24,25,26,27,31,32,33,34],
  342:[27,28,29,34,35], 343:[26,27].
- Column rows rows_s(c) = sorted Y-tail rows in column c.
  Exact-match presence (M28 pinned): rows_s(c) == rows_0(c)
  exactly. Exact ov/miss/extra: ov = |∩|, miss = n0−ov,
  extra = n_s−ov.
- FIXED K LIST (pinned before running — NO additions mid-run):
  K ∈ {0, 1, 15, 20, 50, 100} (the 6 sweep values in the
  brief title). The estimator additionally recomputes K=2
  from the dumps (the reproduction gate — brief-mandated, not
  a sweep addition). K=5 and K=10 are NOT recomputed: their
  windowed pres rows come read-only from M30's committed
  `m30-census-K5.tsv` / `m30-census-K10.tsv` (M30: the three
  TSVs byte-identical — verified by sha against the K=2
  recompute, tabled). Full ordered diff list:
  {exact, 0, 1, 2, 5, 10, 15, 20, 50, 100} (9 adjacent pairs).
- Span window (M30 pinned, reused verbatim): W_K(c) =
  {r : min_{r0 ∈ rows_0(c)} |r − r0| ≤ K} (rows within ±K of
  the s0 span ROWS). Geometry note (pre-registered): the
  span-interval equivalence ([min−K, max+K]) holds iff K≥2 on
  all 8 columns (every s0 hole bridges at d≤2: c340 r29 at
  d=2; c342 r31/r32 at d=2). EXPECTED, tabled (not a guard
  failure): interval-match False at K=0 (c296/c340/c342 —
  all d≥1 hole rows excluded) and at K=1 (c340/c342 — the
  three d=2 hole rows excluded); True at every K≥2
  (2,15,20,50,100). The receipt asserts the equivalence per
  column per computed K and tables violations.
- Windowed column rows rows_s^K(c) = sorted in-window subset
  of rows_s(c). Windowed presence pres_K = 1 iff
  rows_s^K(c) == rows_0(c) (s0 rows all sit at d=0, so s0 is
  present under every K by construction — guarded). Windowed
  ov_K = |rows_s^K ∩ rows_0|; miss_K = n0 − ov_K; extra_K =
  |rows_s^K| − ov_K.
- Off-span tail sites (pinned): O_s^K = named-column Y-tail
  sites (r,c) with c ∈ NAMED8 and r ∉ W_K(c). Per-shape:
  count + sorted (col,row) list with span distances; pooled
  totals per K. Pinned scope: ONLY named-column sites count
  as off-span. Non-named-column tail sites have no window and
  are tabled separately as outside-census counts per shape.
  Nothing is silently dropped: every tail byte is in-window,
  off-span, or outside-census, and the receipt asserts the
  three-way partition sums to the tail count per shape per
  computed K.
- Windowed standings per K (pinned): M28 rule verbatim on
  windowed miss/extra — extra-only iff miss_K == 0; else
  `assign_one` on the FULL private Y-columns (≥2-site
  nearest-column + overlap + smallest tie-breaks, M28
  verbatim). Assignment candidates are NOT windowed: the
  window is a presence rule only; displacement still reads
  the observed privates. Fresh-vs-named dest split as M28.
- J values are full-tail Jaccard (unchanged by the window);
  the window affects presence/miss/extra/standings only.
- K=2 reproduction targets (M30): mover list
  [708,709,710,711,731,732,733,734] (8 movers); per-moved-col
  n_K/ov_K — 708 c296 8/8, 709 c301 10/10, 710 c340 6/6, 711
  c342+c343 0/0, 731 c257+c277 0/0, 732 c296 0/0, 733
  c301+c321 0/0, 734 c340 0/0 + c342 7/5 + c343 0/0 (13
  cells); standings — 7 assigned (731×2 →+2, 732 →+2, 733×2
  →+2, 734 c340→c342 +2, 734 c343→c342 −1) + 1 extra-only
  (734-c342) + 5 no-cand (708, 709, 710, 711×2); TSV
  byte-identical to `m30-census-K2.tsv` (sha compared).
- Exact-match reproduction targets (M28, secondary guard):
  mover list [9,22,708,709,710,711,731,732,733,734] (10
  movers); 15 moved cells with the M30-pinned standings; full
  TSV match on all 764 (tail + J4 + all-8 n/ov/pres);
  below-0.95 9-list (733/731/9/700/734/732/2/711/3 with M28
  tail+J4).

### Task 1 — the sweep (6 K values + K=2 gate, full tables)

K=2 reproduction from the dumps FIRST (§Guards — or table the
mismatch and stop; no further tasks run).

1. Per K ∈ {0,1,15,20,50,100} (+ K=2 gate): windowed presence
   re-run over all 764 (movers / moved cells / standings per
   K — full tables, not just counts: mover shape lists,
   per-moved-cell n_K/ov_K/pres_K + standing rows, per-K
   windowed census TSV to the work dir + evidence copies of
   the 6 sweep TSVs).
2. Off-span tail tables per computed K: per shape with O_s^K
   nonempty — count + sorted (col,row+d) list; pooled
   off-span totals per K; outside-census (non-named-column)
   tail counts per M28-mover shape (K-invariant by
   construction).
3. Adjacent-K diffs across the FULL ordered list
   {exact,0,1,2,5,10,15,20,50,100} (9 pairs: flipping pres
   cells + mover flips per pair — the stability margin,
   tabled). K=5/10 pres rows from M30's TSVs (sha-verified
   identical to the K=2 recompute first).

### Task 2 — boundary analysis (where does the rule bite?)

1. Lower boundary: 734-c342's d=1 extras (r26/r33) across
   K=0/1/2 (in-window at K≥1? out at K=0? — tabled) +
   extras-distance census over all 764 (every named-column
   extra site with its span distance — any other d≤2 sites?
   M30: only the far 3 beyond ±2 — confirmed by enumeration).
2. Upper boundary: first real-data flip at K>10 from the
   diffs (if none through K=100, table the negative + the
   minimum K that WOULD flip per off-span site — d+234 →
   K≥234, d+366 → K≥366, d+367 → K≥367 — computed, not run).
3. Below-0.95 join per computed K (+ K=5,10 from loaded TSVs
   — M28's 2×2 recomputed: does any K move a shape across
   the mover line?).

### Task 3 — controls + determinism (M18–M30 precedent)

`control.py` (mask-level synthetic truths from the s0 tail
mask with KNOWN boundary extras at known row distances —
mid-level injection infeasible per M28 DESIGN; the windowed
census operates on tail masks, so the control builds
synthetic tail masks directly; N=6 shapes):

- C0 missing-only (d=0 probe — the window never hides a
  missing row; M30 W5 analogue): drop c340 r24. Known: moved
  at every computed K with miss_K=1, no-cand (no privates →
  no candidates), off-span empty.
- C1 near extra (d=1; M30 W4 analogue): add c342 r26.
  Known: exact extra-only 6/5; windowed present + off-span
  {(342,26)} at K=0; extra-only (n_K/ov_K 6/5) with EMPTY
  off-span at K≥1 (1,2,15,20,50,100).
- C2 second-ring extra (d=2): add c342 r31 (d=2 from r29).
  Known: exact extra-only 6/5; windowed present + off-span
  {(342,31)} at K∈{0,1}; extra-only (6/5) with EMPTY
  off-span at K≥2 (2,15,20,50,100).
- C7 boundary extra (d=7; M30 W3 analogue): add c296 r41
  (d=+7 from max 34). Known: exact extra-only 10/9;
  windowed present + off-span {(296,41)} at K∈{0,1,2};
  extra-only (10/9) with EMPTY off-span at K≥15
  (15,20,50,100). (Analytic flip threshold K≥7 — between
  computed grid points, tabled as computed-not-run.)
- C15 upper-grid extra (d=15): add c296 r49 (d=+15 from max
  34). Known: exact extra-only 10/9; windowed present +
  off-span {(296,49)} at K∈{0,1,2}; extra-only (10/9) with
  EMPTY off-span at K∈{15,20,50,100} (flip exactly at the
  K=15 grid point).
- C234 far extra (d=+234; M30 W1 analogue): add c321 r266.
  Known: exact extra-only 11/10; windowed present + off-span
  {(321,266)} at EVERY computed K (0,1,2,15,20,50,100).
- Pass = per-computed-K windowed n_K/ov_K/pres_K + off-span
  sets + standings exact on all 6.

Determinism: re-run Task 1 K=2 windowed census
(per-shape windowed rows + move rows + standings) on
s0+9+22 with fresh loads; canonical text sha byte-identical
pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + all 10 M28
movers + m15 triplets + top-10 carrier triplets + `m28.txt` +
`m28-census.tsv` + `m30.txt` + `m30-census-K2/5/10.tsv` shas;
triplet fold sha over all 764×3 bins tabled (want M28's
`6c906897…61fd423b1`). Model-0 recompute: R_0/fnv must match
M17–M30 (s0 22815 / `6b9ffda25bd76c6f`, m15 13418 /
`306b5c778898b64a`). Mismatch = stop and table. R_s vs
`loo.txt` cross-check on ALL 764 shapes (want 764/764 equal;
mismatch = stop and table). `loo.txt` 764 rows + top-10
shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

- B1_K2REPRO (gate — the K=2 census reproduces M30): K=2
  from the dumps reads 8 movers / 13 cells / M30 standings
  (7 assigned + 1 extra-only + 5 no-cand, dests/offsets as
  pinned) AND the recomputed K=2 TSV is byte-identical (sha)
  to `m30-census-K2.tsv`. Else table the mismatch and stop.
- B2_LOWIN (lower boundary, in): 734-c342's 2 d=1 extras
  (r26/r33) are in-window at K=1 (2/2).
- B3_LOWOUT (lower boundary, out): 734-c342's 2 d=1 extras
  are off-span at K=0 (2/2).
- B4_K0SET (K=0 un-moves exactly the far-extra shapes): K=0
  mover set == the K=2 8-shape set (9/22 stay un-moved; no
  newly-moving shapes vs exact).
- B5_K1EQK2 (no d=2 extras anywhere): K=1 census is
  row-identical to K=2 (movers + per-cell n_K/ov_K/pres_K +
  standings + off-span sets).
- B6_UPSTABLE (no upper flip on real data): 0 flipping cells
  on every adjacent pair at/above K=10 (10→15, 15→20, 20→50,
  50→100) AND 0 mover flips on the same pairs.
- B7_OFF100 (far tail stays out): off-span at K=100 is
  exactly the 3 far extras (2 shapes / 3 sites).
- B8_BELOW95 (windowed movers read below 0.95): share of
  windowed movers with J < 0.95 is ≥ 0.50 at EVERY computed K
  (M28 H5 analogue; denominators tabled per K).
- B9_MISSIN (the window never hides a missing row): M29's 4
  missing rows (708-c296 r28; 709-c301 r33; 710-c340 r31/r34;
  all d=0) are in-window at EVERY computed K including K=0
  (4/4 per K).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with the
  tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on all 764; cell-7 counts s0 2475 exact +
tail counts s0 102 exact with sub-bins 28+74 and max 47; s0
per-named-column n + row lists exact (§Definitions); s0
windowed-present on all 8 at every computed K; window
geometry tabled per column per computed K (interval-match
False EXPECTED at K=0 on c296/c340/c342 and at K=1 on
c340/c342 — pre-registered above, not a failure); partition
check (in-window + off-span + outside-census == tail) on all
764 per computed K; M28 TSV match on ALL 764 shapes (tail +
J4 + all-8-column n/ov/pres exact); mover list == the M28 10
exactly; all 15 move standings match `m28.txt` move lines
exactly; below-0.95 9-list tail+J4 exact vs M28 constants;
δ≠0 throughout cell 7 (all analyzed shapes);
P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0; M30 K5/K10 TSV shas equal
the K=2 recompute sha (else the 2→5→10 diff legs are tabled
from the loaded bytes as-is with the mismatch flagged).

## Run protocol

1. Input shas + `m28.txt`/`m28-census.tsv`/`m30.txt`/
   `m30-census-K2/5/10.tsv` shas + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards + s0
   reference guard + exact-match M28 guard (TSV + movers +
   standings, or stop).
3. Task 1: K=2 gate recompute (sha vs M30 K2 TSV + movers /
   cells / standings, or stop) + windowed re-run per sweep K
   (TSVs to work dir + evidence copies of the 6 sweep TSVs) +
   off-span tables + full ordered adjacent-K diffs.
4. Task 2: lower-boundary tables + extras-distance census +
   upper-boundary min-K table + below-0.95 joins per K.
5. Determinism re-run receipt (Task 1 K=2 windowed census on
   s0+9+22, canonical sha).
6. PNG K-sweep cell map (x = 10 M28 movers × 8 named cols =
   80 cells, rows = exact + 0,1,2,5,10,15,20,50,100;
   green=present magenta=moved) to work dir; evidence copy
   ONLY if B3 meets AND B2 meets (the K=0 lower-boundary
   exclusion visible in the pre-registered K0-vs-K1 cell
   split — a mover-level map would NOT discriminate: K=0..100
   mover sets are predicted identical) — else absence
   reasoned. Budget 5242880 B total.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 03:40 EDT, stop by 07:40).
