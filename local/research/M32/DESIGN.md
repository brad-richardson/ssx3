# M32 — Design (recorded before running)

Goal: upper-K confirmation (M31 gap 1): the nearest would-be
real-data flip needs K≥234 (d+234 → admit; d+366/+367 need
K≥366/367) — computed, not run, since K=234/366/367 sit
outside M31's DESIGN-fixed list. Bracket both far admissions
with a narrow windowed-census sweep at K ∈ {233, 234, 366,
367} (below/at each threshold) + off-span tails + adjacent-K
diffs + admission/standing/join tables. Tables, no verdicts.
Fully offline: no lease of any kind, no boots, no harness
runs, no fork changes, no `adb`. Desktop only. SSD dumps
read-only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme
SSD/m15/` (triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m28/m28.txt` +
`/Volumes/Extreme SSD/m28/m28-census.tsv` (exact-match census
guard: 10 movers / 15 cells / standings),
`/Volumes/Extreme SSD/m31/m31.txt` +
`/Volumes/Extreme SSD/m31/m31-census-K1.tsv` (K=1 windowed
census to reproduce: 8 movers / 13 cells / standings — match
exactly or table the mismatch and stop) +
`/Volumes/Extreme SSD/m31/m31-census-K100.tsv` (K=100 diff
baseline — loaded read-only, never recomputed; the fixed list
below is final). Work dir: `/Volumes/Extreme SSD/m32/`
(new). Evidence: `local/research/M32/` (committed with `git
add -f`, prefix `[M32]`, trailer `Orchestrated-By: Muse
Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M31/REPORT.md` (all of it:
K=1..100 plateau row-identical at 8 movers / 13 cells; off-span
exactly the 3 far extras at every K≥1; 0 flips on all 7 pairs
spanning K=1..100; extras census exactly 5 sites — d=1×2,
d+234, d+366, d+367, nothing at d=2; join 5/3/4/752
throughout; gap 1 is this brief) plus
`local/research/M30/DESIGN.md` (the ±K window definition,
reused verbatim below) and the M28/M29/M30/M31 DESIGN.md
estimator + bar precedent.

## Estimator (`m32.py`, `control.py`)

Shared core (M31 `m31.py` verbatim where reused):
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

Definitions (raw bytes, full 573440-B frame) — M30/M31 verbatim:

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
- s0 reference row lists (M27–M31, guarded exact):
  257:[23–32], 277:[23–32], 296:[24,25,26,27,28,31,32,33,34],
  301:[23–33], 321:[23–32], 340:[24,25,26,27,31,32,33,34],
  342:[27,28,29,34,35], 343:[26,27].
- Column rows rows_s(c) = sorted Y-tail rows in column c.
  Exact-match presence (M28 pinned): rows_s(c) == rows_0(c)
  exactly. Exact ov/miss/extra: ov = |∩|, miss = n0−ov,
  extra = n_s−ov.
- FIXED K LIST (pinned before running — NO additions mid-run):
  K ∈ {233, 234, 366, 367} (the 4 bracketing values in the
  brief title — below/at each far-admission threshold). The
  estimator additionally recomputes K=1 from the dumps (the
  reproduction gate — brief-mandated, not a sweep addition).
  K=100 is NOT recomputed: its windowed pres rows come
  read-only from M31's committed `m31-census-K100.tsv` (M31:
  the K=1..100 TSVs byte-identical — verified by sha against
  the K=1 recompute, tabled). Full ordered diff list:
  {100, 233, 234, 366, 367} (4 adjacent pairs).
- Span window (M30 pinned, reused verbatim): W_K(c) =
  {r : min_{r0 ∈ rows_0(c)} |r − r0| ≤ K} (rows within ±K of
  the s0 span ROWS). Geometry note (pre-registered): the
  span-interval equivalence ([min−K, max+K]) holds at every
  computed K≥233 on all 8 columns (every s0 hole bridges at
  d≤2 — trivially covered); at the K=1 gate the M31-pinned
  exclusions hold (c340 r29; c342 r31/r32 — the three d=2
  hole rows excluded). The receipt asserts the equivalence per
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
- K=1 reproduction targets (M31 — the gate): mover list
  [708,709,710,711,731,732,733,734] (8 movers); per-moved-col
  n_K/ov_K — 708 c296 8/8, 709 c301 10/10, 710 c340 6/6, 711
  c342+c343 0/0, 731 c257+c277 0/0, 732 c296 0/0, 733
  c301+c321 0/0, 734 c340 0/0 + c342 7/5 + c343 0/0 (13
  cells); standings — 7 assigned (731×2 →+2, 732 →+2, 733×2
  →+2, 734 c340→c342 +2, 734 c343→c342 −1) + 1 extra-only
  (734-c342) + 5 no-cand (708, 709, 710, 711×2); TSV
  byte-identical to `m31-census-K1.tsv` (sha compared).
- Exact-match reproduction targets (M28, secondary guard):
  mover list [9,22,708,709,710,711,731,732,733,734] (10
  movers); 15 moved cells with the M30/M31-pinned standings;
  full TSV match on all 764 (tail + J4 + all-8 n/ov/pres);
  below-0.95 9-list (733/731/9/700/734/732/2/711/3 with M28
  tail+J4).
- Predictions to table (not to believe — brief-pinned):
  K=233 keeps all 3 off-span; K=234 admits r266 only; K=366
  admits r266 + r400; K=367 admits all 3. Standing
  predictions: s9-c321 present at K≤233, extra-only (11/10)
  at K≥234; s22-c296 present at K≤234, extra-only (10/9 at
  K=366, 11/9 at K=367) at K≥366. Mover-count predictions:
  8/9/10/10 movers and 13/14/15/15 cells at K=233/234/366/367.

### Task 1 — bracket confirmation (4 K values, full tables)

K=1 reproduction from the dumps FIRST (§Guards — or table the
mismatch and stop; no further tasks run).

1. Per K ∈ {233,234,366,367} (+ K=1 gate): windowed presence
   re-run over all 764 (movers / moved cells / standings +
   dests/offsets per K — full per-cell rows, not just counts:
   mover shape lists, per-moved-cell n_K/ov_K/pres_K +
   standing rows, per-K windowed census TSV to the work dir +
   evidence copies of the 4 sweep TSVs).
2. Off-span tail tables per computed K: per shape with O_s^K
   nonempty — count + sorted (col,row+d) list; pooled
   off-span totals per K; outside-census (non-named-column)
   tail counts per M28-mover shape (K-invariant by
   construction).
3. Adjacent-K diffs across the FULL ordered list
   {100,233,234,366,367} (4 pairs: flipping pres cells +
   mover flips per pair — the bracket, tabled). K=100 pres
   rows from M31's TSV (sha-verified identical to the K=1
   recompute first).

### Task 2 — admission analysis (what crosses, what changes?)

1. Per-site admission table (r266 / r400 / r401 × computed K
   values: off-span vs in-window at each K — do the
   admissions land exactly at K=234/366/367?) + extras
   re-enumeration guard (any other named-column extra site
   that would flip a bracket leg? M31: none — confirmed by
   enumeration).
2. Standing response: s9-c321 / s22-c296 standings per
   computed K (present? moved? extra-only? — the cells the
   admissions flip, tabled with n_K/ov_K).
3. Below-0.95 join per computed K (+ K=100 from the loaded
   TSV — M31's 2×2 recomputed: does any admission move a
   shape across the mover line?).

### Task 3 — controls + determinism (M18–M31 precedent)

`control.py` (mask-level synthetic truths from the s0 tail
mask with KNOWN far extras at known row distances —
mid-level injection infeasible per M28 DESIGN; the windowed
census operates on tail masks, so the control builds
synthetic tail masks directly; N=9 shapes: C0 + 8 bracket
probes at d ∈ {233,234,366,367} ± 1):

- C0 missing-only (d=0 probe): drop c340 r24. Known: moved
  at every computed K with miss_K=1, no-cand (no privates →
  no candidates), off-span empty.
- C232 (c321 + r264, d=232 — just below the lower bracket):
  Known: exact extra-only 11/10; windowed present + off-span
  {(321,264)} at K=1; extra-only (11/10) with EMPTY off-span
  at K≥233 (233,234,366,367).
- C233 (c321 + r265, d=233 — lower-bracket floor): Known:
  exact extra-only 11/10; windowed present + off-span
  {(321,265)} at K=1; extra-only (11/10) with EMPTY
  off-span at K≥233 (233,234,366,367).
- C234 (c321 + r266, d=234 — the s9 site): Known: exact
  extra-only 11/10; windowed present + off-span {(321,266)}
  at K∈{1,233}; extra-only (11/10) with EMPTY off-span at
  K≥234 (234,366,367).
- C235 (c321 + r267, d=235 — just above the lower bracket):
  Known: exact extra-only 11/10; windowed present + off-span
  {(321,267)} at K∈{1,233,234}; extra-only (11/10) with
  EMPTY off-span at K≥366 (366,367).
- C365 (c296 + r399, d=365 — just below the upper bracket):
  Known: exact extra-only 10/9; windowed present + off-span
  {(296,399)} at K∈{1,233,234}; extra-only (10/9) with
  EMPTY off-span at K≥366 (366,367).
- C366 (c296 + r400, d=366 — the s22 site): Known: exact
  extra-only 10/9; windowed present + off-span {(296,400)}
  at K∈{1,233,234}; extra-only (10/9) with EMPTY off-span
  at K≥366 (366,367).
- C367 (c296 + r401, d=367 — the s22 site): Known: exact
  extra-only 10/9; windowed present + off-span {(296,401)}
  at K∈{1,233,234,366}; extra-only (10/9) with EMPTY
  off-span at K=367.
- C368 (c296 + r402, d=368 — just above the upper bracket):
  Known: exact extra-only 10/9; windowed present + off-span
  {(296,402)} at EVERY computed K (1,233,234,366,367).
- Pass = per-computed-K windowed n_K/ov_K/pres_K + off-span
  sets + standings exact on all 9.

Determinism: re-run Task 1 K=233 windowed census
(per-shape windowed rows + move rows + standings) on
s0+9+22 with fresh loads; canonical text sha byte-identical
pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + all 10 M28
movers + m15 triplets + top-10 carrier triplets + `m28.txt` +
`m28-census.tsv` + `m31.txt` + `m31-census-K1.tsv` +
`m31-census-K100.tsv` shas; triplet fold sha over all 764×3
bins tabled (want M28's `6c906897…61fd423b1`). Model-0
recompute: R_0/fnv must match M17–M31 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

- B1_K1REPRO (gate — the K=1 census reproduces M31): K=1
  from the dumps reads 8 movers / 13 cells / M31 standings
  (7 assigned + 1 extra-only + 5 no-cand, dests/offsets as
  pinned) AND the recomputed K=1 TSV is byte-identical (sha)
  to `m31-census-K1.tsv`. Else table the mismatch and stop.
- B2_OFF233 (lower bracket floor — nothing admitted yet):
  off-span at K=233 is exactly the 3 far extras (2 shapes /
  3 sites).
- B3_ADMIT234 (lower admission — r266 only): off-span at
  K=234 is exactly {(22,296,400),(22,296,401)} (r266
  admitted, r400/r401 still out).
- B4_ADMIT366 (upper admission, first site): off-span at
  K=366 is exactly {(22,296,401)} (r266 + r400 admitted).
- B5_ALLIN367 (upper admission, last site): off-span at
  K=367 is EMPTY (all 3 admitted; no 4th off-span site in
  any of the 764).
- B6_S9STAND (s9-c321 standing response): s9-c321 reads
  present at K∈{1,233} and extra-only (n_K/ov_K 11/10) at
  K∈{234,366,367}.
- B7_S22STAND (s22-c296 standing response): s22-c296 reads
  present at K∈{1,233,234} and extra-only (10/9 at K=366,
  11/9 at K=367) at K≥366.
- B8_KDIFFS (the bracket diffs): 100→233 flips 0 cells + 0
  mover flips; 233→234 flips exactly 1 cell (9,c321) + 1
  mover flip (9 re-moves); 234→366 flips exactly 1 cell
  (22,c296) + 1 mover flip (22 re-moves); 366→367 flips 0
  pres cells + 0 mover flips.
- B9_BELOW95 (windowed movers read below 0.95): share of
  windowed movers with J < 0.95 is ≥ 0.50 at EVERY computed K
  (M28 H5 analogue; denominators tabled per K).
- B10_MISSIN (the window never hides a missing row): M29's 4
  missing rows (708-c296 r28; 709-c301 r33; 710-c340 r31/r34;
  all d=0) are in-window at EVERY computed K including K=1
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
False EXPECTED at K=1 on c340/c342 only — the three d=2
hole rows, pre-registered above, not a failure; True at
every K≥233); partition check (in-window + off-span +
outside-census == tail) on all 764 per computed K; M28 TSV
match on ALL 764 shapes (tail + J4 + all-8-column n/ov/pres
exact); mover list == the M28 10 exactly; all 15 move
standings match `m28.txt` move lines exactly; below-0.95
9-list tail+J4 exact vs M28 constants; δ≠0 throughout cell 7
(all analyzed shapes); P(δ>0)==M19/M20 0.8093 on s0;
`loo.txt` 764 rows + top-10 shapes/shares; self Jaccard ==
1.0; M31 K100 TSV sha equals the K=1 recompute sha (else the
100→233 diff leg is tabled from the loaded bytes as-is with
the mismatch flagged).

## Run protocol

1. Input shas + `m28.txt`/`m28-census.tsv`/`m31.txt`/
   `m31-census-K1.tsv`/`m31-census-K100.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards + s0
   reference guard + exact-match M28 guard (TSV + movers +
   standings, or stop).
3. Task 1: K=1 gate recompute (sha vs M31 K1 TSV + movers /
   cells / standings, or stop) + windowed re-run per sweep K
   (TSVs to work dir + evidence copies of the 4 sweep TSVs) +
   off-span tables + full ordered adjacent-K diffs.
4. Task 2: per-site admission table + extras re-enumeration +
   s9/s22 standing response + below-0.95 joins per K.
5. Determinism re-run receipt (Task 1 K=233 windowed census
   on s0+9+22, canonical sha).
6. PNG K-sweep cell map (x = 10 M28 movers × 8 named cols =
   80 cells, rows = 100,233,234,366,367; green=present
   magenta=moved) to work dir; evidence copy ONLY if B2
   meets AND B5 meets (the bracket visible in the
   pre-registered K233-vs-K367 off-span collapse 3→0 with
   both far admissions landing — a mover-level map would
   also discriminate here: 8→10 movers) — else absence
   reasoned. Budget 5242880 B total.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 03:48 EDT, stop by 07:48).
