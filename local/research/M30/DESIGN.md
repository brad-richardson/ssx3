# M30 — Design (recorded before running)

Goal: span-windowed census rule proposal (M29 gap 1): M29's 3
far-flung extras (9 c321 r266 at +234 rows; 22 c296 r400/r401
at +366/+367 rows) read in-column but hundreds of rows from
their streak spans — the exact-match census column definition
counts them as column members, not ±1–2 moves. Test the
proposal: column membership requires rows within ±K of the s0
span (far sites tabled separately as off-span tail, never
dropped). Re-run the presence census with the ±K window over
all 764 + off-span tables + stability tables. Tables, no
verdicts. Fully offline: no lease of any kind, no boots, no
harness runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m28/m28.txt` +
`/Volumes/Extreme SSD/m28/m28-census.tsv` (exact-match census
to reproduce: 10 movers / 15 cells / standings — match exactly
or table the mismatch and stop). Work dir:
`/Volumes/Extreme SSD/m30/` (new). Evidence:
`local/research/M30/` (committed with `git add -f`, prefix
`[M30]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M29/REPORT.md` (all of it:
6 partial cells, 9 delta-row sites — 5 extra + 4 missing; the 4
missing rows in-span, 734-c342 r26/r33 span-adjacent at ±1 row,
9 r266 + 22 r400/r401 far-flung at +234/+366/+367) plus
`local/research/M28/REPORT.md` (all of it: 10 movers / 15 moved
cells, 7 assigned + 3 extra-only + 5 no-cand; M28
`census_of_shape` / `assign_one` / `BELOW95` constants pinned
below) and `local/research/M28/DESIGN.md` + `local/research/
M29/DESIGN.md` (estimator + bar precedent).

## Estimator (`m30.py`, `control.py`)

Shared core (M28 `m28.py` verbatim where reused):
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

Definitions (raw bytes, full 573440-B frame):

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
- s0 reference row lists (M27/M28/M29, guarded exact):
  257:[23–32], 277:[23–32], 296:[24,25,26,27,28,31,32,33,34],
  301:[23–33], 321:[23–32], 340:[24,25,26,27,31,32,33,34],
  342:[27,28,29,34,35], 343:[26,27].
- Column rows rows_s(c) = sorted Y-tail rows in column c.
  Exact-match presence (M28 pinned): rows_s(c) == rows_0(c)
  exactly. Exact ov/miss/extra: ov = |∩|, miss = n0−ov,
  extra = n_s−ov.
- FIXED K LIST (pinned before running — NO additions mid-run):
  K ∈ {2, 5, 10}.
- Span window (pinned): W_K(c) = {r : min_{r0 ∈ rows_0(c)}
  |r − r0| ≤ K} (rows within ±K of the s0 span ROWS). Note:
  for every K in the fixed list this equals the span-interval
  window [min−K, max+K] on all 8 columns, because every s0
  hole bridges at d≤2 (c296 hole r29–30: d≤2; c340 hole
  r28–30: d≤2; c342 hole r30–33: d≤2; other columns
  contiguous) — the receipt asserts the equivalence per
  column per K and tables any violation (none expected).
- Windowed column rows rows_s^K(c) = sorted in-window subset
  of rows_s(c). Windowed presence pres_K = 1 iff
  rows_s^K(c) == rows_0(c) (s0 rows all sit at d=0, so s0 is
  present under every K by construction — guarded). Windowed
  ov_K = |rows_s^K ∩ rows_0|; miss_K = n0 − ov_K; extra_K =
  |rows_s^K| − ov_K. Far extras beyond ±K stop counting as
  column members (extra_K drops) and move to the off-span
  tail; missing rows (all M29 missings in-span at d=0) are
  unaffected by construction — bar W6 checks this.
- Off-span tail sites (pinned): O_s^K = named-column Y-tail
  sites (r,c) with c ∈ NAMED8 and r ∉ W_K(c). Per-shape:
  count + sorted (col,row) list with span distances; pooled
  totals per K. Pinned scope: ONLY named-column sites count
  as off-span. Non-named-column tail sites (e.g. full-swap
  dests c303/c323/c259/c279/c298) have no window and are
  tabled separately as outside-census counts per shape — they
  never pollute the off-span tail (a window is a per-column
  presence rule, not a global mask). Nothing is silently
  dropped: every tail byte is in-window, off-span, or
  outside-census, and the receipt asserts the three-way
  partition sums to the tail count per shape.
- Windowed standings per K (pinned): M28 rule verbatim on
  windowed miss/extra — extra-only iff miss_K == 0; else
  `assign_one` on the FULL private Y-columns (≥2-site
  nearest-column + overlap + smallest tie-breaks, M28
  verbatim). Assignment candidates are NOT windowed: the
  window is a presence rule only; displacement still reads
  the observed privates. Fresh-vs-named dest split as M28.
- J values are full-tail Jaccard (unchanged by the window);
  the window affects presence/miss/extra/standings only.
- Exact-match reproduction targets (M28): mover list
  [9,22,708,709,710,711,731,732,733,734] (10 movers);
  per-moved-col n/ov — 9 c321 11/10, 22 c296 11/9, 708 c296
  8/8, 709 c301 10/10, 710 c340 6/6, 711 c342+c343 0/0,
  731/733 pairs 0/0, 732 c296 0/0, 734 c340 0/0 + c342 7/5 +
  c343 0/0 (15 cells); standings — 7 assigned
  (731×2, 732, 733×2, 734 c340→c342 +2, 734 c343→c342 −1) +
  3 extra-only (9, 22, 734-c342) + 5 no-cand (708, 709, 710,
  711×2); full TSV match on all 764 (tail + J4 + all-8
  n/ov/pres); below-0.95 9-list
  (733/731/9/700/734/732/2/711/3 with M28 tail+J4).

### Task 1 — rule proposal (fixed K list, exact-hit comparison)

Exact-match census recomputed from the dumps FIRST (§Guards —
or table the mismatch and stop; no further tasks run).

1. Per K ∈ {2,5,10}: windowed presence re-run over all 764
   (movers / moved cells / standings per K — full tables, not
   just counts: mover shape lists, per-moved-cell n_K/ov_K/
   pres_K + standing rows, per-K windowed census TSV to the
   work dir + evidence copies).
2. Off-span tail tables per K: per shape with O_s^K nonempty —
   count + sorted (col,row+d) list; pooled off-span totals per
   K; outside-census (non-named-column) tail counts per mover
   shape (the partition the window does NOT touch).
3. Delta table exact-vs-windowed per K: which movers survive
   (exact movers still moving under K), which standings change
   per cell, M29's 3 far extras (9 r266, 22 r400/r401) —
   off-span under every K? — and 734-c342's 2 near extras —
   in-window under every K? — tabled per K.

### Task 2 — window behavior (does ±K stabilize the census?)

1. Standing stability: extra-only / no-cand / assigned counts
   per K (exact + K2/K5/K10 side-by-side — does the window
   REDUCE unassigned cells, or just move bytes to off-span?).
2. Below-0.95 join per K: the M28 2×2 (mover × below-0.95)
   recomputed with windowed movers (J values unchanged) —
   does the mover/below overlap change?
3. K-sensitivity: adjacent-K diff tables (K 2→5, 5→10): which
   cells flip pres, which shapes flip mover standing — the
   rule's stability margin, tabled. (Exact→K2 diffs are Task
   1.3; Task 2.3 is K-vs-K only.)

### Task 3 — controls + determinism (M18–M29 precedent)

`control.py` (mask-level synthetic truths from the s0 tail
mask with KNOWN far extras at known row distances — mid-level
injection infeasible per M28 DESIGN: dest-column sites are
non-cell/static on s0; the windowed census operates on tail
masks, so the control builds synthetic tail masks directly):

- W1 far extra (mimics s9): add c321 r266 (d=+234).
  Known: exact n/ov 11/10 extra-only; windowed pres=1
  (non-mover) + off-span {(321,266)} at EVERY K.
- W2 far pair (mimics s22): add c296 r400+r401 (d=+366/+367).
  Known: exact 11/9 extra-only; windowed pres=1 +
  off-span {(296,400),(296,401)} at EVERY K.
- W3 boundary extra: add c296 r41 (d=+7 from max 34).
  Known: off-span + windowed-present at K=2,5; in-window
  extra-only (n_K/ov_K 10/9) with EMPTY off-span at K=10.
  (The K-sensitivity boundary probe.)
- W4 near extra (mimics s734): add c342 r26 (d=1).
  Known: extra-only (n_K/ov_K 6/5) with EMPTY off-span at
  EVERY K.
- W5 missing-only (mimics s710): drop c340 r24.
  Known: moved at every K with miss_K=1, no-cand (no
  privates → no candidates), off-span empty at every K.
  (Missing rows never hide behind the window.)
- Pass = per-K windowed n_K/ov_K/pres_K + off-span sets +
  standings exact on all 5 (N=5 shapes).

Determinism: re-run Task 1 exact-match census (per-shape rows
+ move rows + J values) on s0+9+22; canonical text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + all 10 M28
movers + m15 triplets + top-10 carrier triplets + `m28.txt` +
`m28-census.tsv` shas; triplet fold sha over all 764×3 bins
tabled (want M28's `6c906897…61fd423b1`). Model-0 recompute:
R_0/fnv must match M17–M29 (s0 22815 / `6b9ffda25bd76c6f`,
m15 13418 / `306b5c778898b64a`). Mismatch = stop and table.
R_s vs `loo.txt` cross-check on ALL 764 shapes (want 764/764
equal; mismatch = stop and table). `loo.txt` 764 rows +
top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

- W1_FAROFF (far extras leave the census): M29's 3 far extras
  (9-c321 r266; 22-c296 r400/r401) are off-span at EVERY K
  (3/3 per K).
- W2_NEARIN (near extras stay): 734-c342's 2 near extras
  (r26/r33) are in-window at EVERY K (2/2 per K).
- W3_UNMOVE (the window un-moves shapes): windowed mover
  count < 10 (exact) at EVERY K.
- W4_KSTABLE (the rule is K-stable): windowed mover SETS
  identical across adjacent K (2v5 AND 5v10 both identical).
- W5_BELOW95 (windowed movers read below 0.95): share of
  windowed movers with J < 0.95 is ≥ 0.50 at EVERY K (M28
  H5 analogue; denominators tabled per K).
- W6_MISSIN (the window never hides a missing row): M29's 4
  missing rows (708-c296 r28; 709-c301 r33; 710-c340 r31/r34)
  are in-window at EVERY K (4/4 per K).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with the
  tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on all 764; cell-7 counts s0 2475 exact +
tail counts s0 102 exact with sub-bins 28+74 and max 47; s0
per-named-column n + row lists exact (§Definitions); s0
windowed-present on all 8 at every K; window==interval check
per column per K; partition check (in-window + off-span +
outside-census == tail) on all 764 per K; M28 TSV match on
ALL 764 shapes (tail + J4 + all-8-column n/ov/pres exact);
mover list == the M28 10 exactly; all 15 move standings match
`m28.txt` move lines exactly; below-0.95 9-list tail+J4 exact
vs M28 constants; δ≠0 throughout cell 7 (all analyzed
shapes); P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m28.txt`/`m28-census.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards + s0
   reference guard + exact-match M28 guard (TSV + movers +
   standings, or stop).
3. Task 1: windowed re-run per K (TSVs to work dir + evidence
   copies) + off-span tables + exact-vs-windowed deltas.
4. Task 2: standing stability + below-0.95 joins per K +
   adjacent-K diffs.
5. Determinism re-run receipt (Task 1 exact-match on s0+9+22,
   canonical sha).
6. PNG windowed-census mover map (4×764: exact + K2/K5/K10
   mover rows; green=still magenta=mover) to work dir;
   evidence copy ONLY if W3 meets AND W1 meets (the window
   un-moves ≥1 shape at every K with the 3 far extras
   off-span at every K — the exclusion visible in the
   pre-registered exact-vs-windowed mover split) — else
   absence reasoned. Budget 5242880 B total.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 03:31 EDT, stop by 07:31).
