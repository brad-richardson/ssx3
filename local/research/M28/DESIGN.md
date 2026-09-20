# M28 — Design (recorded before running)

Goal: streak-column census across all 764 M16 shapes (M27 gap 1):
733 swaps s0's c301/c321 for c303/c323 (+2 columns), 731 swaps
c257/c277 for c259/c279 (+2 columns) — which shapes move which
named columns, where do movers go (displacement distribution),
do movers correlate (pairs move together?). Tables, no verdicts.
Fully offline: no lease of any kind, no boots, no harness runs,
no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m27/m27.txt` (733/731 swap rows to
reproduce: swapped pairs + offsets — match exactly or table the
mismatch and stop). Work dir: `/Volumes/Extreme SSD/m28/` (new).
Evidence: `local/research/M28/` (committed with `git add -f`,
prefix `[M28]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M27/REPORT.md` (all of it: 733
100 B at J 0.6694 = 19 priv + 21 miss + 81 shared, all luma, all
non-cell on the other frame; miss = all of c301 (11, r23–33) +
c321 (10, r23–32); priv = c303 (9, r25–33) + c323 (10, r25–34);
731 mirror 100 B at 0.6833 = 18 + 20 + 82, c257/c277 → c259/c279,
J(P_733,P_731) = 0.0000) plus M22's streak-column definitions
(s0 named columns + row spans below, reproduced as the s0
reference) and `local/research/M25/REPORT.md` (per-row δ profiles
confirming the 8 named-column row sets + holes).

## Estimator (`m28.py`, `control.py`)

Shared core (M27 `m27.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`. Byte offset o -> row
o//1280; Y bytes at o%4==0/2. No P1/carrier/BFS machinery (no
gradient, carrier, or edge task here).

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard).
- Bulk = cell-7 bytes with |δ|<8. Tail = cell-7 bytes with
  |δ|≥8. Tail MAP of shape s: T_s = tail boolean mask (N
  bytes). Want: s0 102 (sub-bins 28 in 8–15 + 74 in 16+, max
  47); 733 100 B; 731 100 B.
- Named columns (the census 8, fixed order): [257,277,296,301,
  321,340,342,343]. c341 is guard-only (0 s0 sites — M27
  streak table), outside the census.
- s0 reference row lists (M27 streak rowlists, reproducing
  M22/M25 — guard: recomputed s0 per-column n + row lists must
  match exactly or stop):
  - 257: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 277: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 296: n=9 [24,25,26,27,28,31,32,33,34]
  - 301: n=11 [23,24,25,26,27,28,29,30,31,32,33]
  - 321: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 340: n=8 [24,25,26,27,31,32,33,34]
  - 342: n=5 [27,28,29,34,35]
  - 343: n=2 [26,27]
- Column rows of shape s at column c: rows_s(c) = sorted Y-tail
  rows in column c (tail & Y & col==c). Overlap ov_s(c) =
  |rows_s(c) ∩ rows_0(c)|. Missing m_s(c) = n0(c) − ov; extra
  e_s(c) = n_s(c) − ov.
- PRESENT (pinned): rows_s(c) == rows_0(c) exactly (n equal +
  overlap == n0 — byte-identical column). ABSENT = moved =
  any difference (n differs or rows differ; covers missing-only,
  extra-only, and swapped cases). The H5-style ≥8/≥5 rule is
  pinned OUT: it excludes c342/c343 and hides partial moves;
  exact-match keeps the census sensitive and the overlap column
  quantifies partiality.
- Mover shape: ≥1 absent named column.
- Private sites P_s = T_s − T_s0; missing M_s = T_s0 − T_s.
  Private Y-columns: group P_s Y-sites by column → {col: sorted
  rows}. Missing rows per named column: rows_0(c) − rows_s(c).
- Displacement assignment (pinned, per moved column c with
  NONEMPTY missing rows; extra-only moves get no destination —
  tabled as `dest=none(extra-only)`):
  - Candidate destinations = private Y-columns with ≥2 sites
    (pinned threshold; singleton private columns are noise,
    counted separately).
  - dest(c) = argmin |col_priv − c|; tie-break 1: max
    row-overlap |rows_priv ∩ rows_0(c)|; tie-break 2: smallest
    column. Collisions allowed (two missing cols may map to one
    dest — tabled as measured, no forced bijection).
  - Signed offset = dest_col − c. Row-shift = median(priv_rows)
    − median(rows_0(c)) as float (even-n medians average the two
    middles). Min-row shift = min(priv) − min(rows0) tabled per
    move in the receipt.
  - No candidates → `dest=none(no-cand)`.
- Destination fresh-vs-named: dest outside the census 8 = fresh;
  dest inside the 8 = swap-with-named (tabled per move).

### Task 1 — presence census (which shapes move which columns?)

733/731 swap rows recomputed from the dumps first (pairs +
offsets + private-column n/rows must match M27 exactly — §Guards
— or table the mismatch and stop; no further tasks run).

1. Per-shape × named-column presence table: all 764 × 8 with
   n_s(c), ov_s(c), present(1/0) — the census matrix, committed
   as TSV `m28-census.tsv` (header: shape, tail_n, J4, then per
   column in fixed order: n{c}, ov{c}, pres{c}); summarized in
   the report (mover count, per-column rates).
2. Mover census: shapes moving ≥1 named column (count, full shape
   list, moved-count hist k=1..8); per-column mover counts (8
   rows: movers, rate, missing-only/extra-only/mixed split).
3. Pairing: pair co-occurrence — symmetric 8×8 counts (shapes
   moving both i and j; diagonal = per-column mover counts) +
   exact moved-set pattern table (moved-set → count + shape
   list). Pairs move together or singles — tabled.

### Task 2 — displacement census (where do movers go?)

1. Displacement distribution over all moved columns with dest
   assigned: full signed-offset value counts (offset → n, no
   binning) + summary (min/med/mean/max); row-shift full
   value-count list + summary. Always +2 — tabled.
2. Destination analysis: per-destination-column counts (dest col
   → n moves pointing at it) + fresh-vs-named split per move +
   per-shape move→dest rows (shape: miss col → dest col, offset,
   row-shift). Fresh columns or swaps with each other — tabled.
3. Below-0.95 join: the 9 M22 shapes (733/731/9/700/734/732/2/
   711/3 with tail+J: 733 100/0.6694, 731 100/0.6833, 9
   117/0.7520, 700 114/0.8462, 734 94/0.8846, 732 95/0.8942, 2
   103/0.9159, 711 95/0.9314, 3 103/0.9340 — guard: recomputed
   J4 + tail counts on all 9 must match m22.txt rows exactly or
   stop) vs the mover census: 2×2 (mover × below-0.95) with
   counts + shape lists in each cell. Are all 9 movers, are all
   movers below 0.95 — tabled.

### Task 3 — controls + determinism (M18–M27 precedent)

`control.py` (mask-level synthetic truths — pinned: mid-level
injection is infeasible at the true dest columns because M27
reads 733/731 privates non-cell on s0, 15/19 + 13/18 static
there with gap 0, so no mid edit can make them cell-7; the
census/displacement logic under test operates on tail masks, so
the control builds synthetic tail masks directly from the s0
tail mask with KNOWN moved columns and checks exact recovery):

- S1 single move: remove s0 c301 rows, add c303 rows 25–33 (9
  sites, mimics 733's dest rows exactly). Known: moved {301},
  offset +2.
- S2 pair move: remove s0 c257 + c277 rows, add c259 + c279 rows
  25–33 (9 each, mimics 731). Known: moved {257,277}, +2/+2.
- S3 odd offset: remove s0 c342 rows [27,28,29,34,35], add the
  same rows in c345. Known: moved {342}, offset +3, row-shift
  0.0.
- S4 missing-only: remove s0 c296 rows 24,25, add nothing.
  Known: moved {296}, dest none (no candidates).
- S5 extra-only: add row 28 to s0 c343 (n 2→3, overlap 2).
  Known: moved {343}, dest none (extra-only).
- Pass = census moved-sets + per-column n/ov/pres + displacement
  dests/offsets/row-shifts exact on all 5 (N=5 shapes).

Determinism: re-run Task 1 presence + displacement assignment on
s0+733+731; canonical text (per-shape census rows + displacement
rows + J values) sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): all 764×3 M16 triplet
bins are read; receipt prints full shas for s0/733/731 + m15
triplets + `m27.txt` sha (the full-bin sha list is folded into
one sha256 over the concatenated per-file hexes — tabled).
Model-0 recompute: R_0/fnv must match M17–M27 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on ALL
764 shapes (M22 precedent 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_PAIR (movers move PAIRS like 733/731): share of mover
  shapes moving exactly 2 named columns is ≥ 0.50.
- H2_PLUS2 (displacements are +2): share of assigned column
  offsets equal to +2 is ≥ 0.50 (denominator = moved columns
  with dest assigned; unassigned excluded, counts tabled).
- H3_FRESH (destinations are fresh, not swaps): share of
  destination columns outside the census 8 is ≥ 0.50
  (per-move denominator = moves with dest assigned).
- H4_CONCENTRATE (moves concentrate on 733/731's four columns):
  share of all moved-column instances in {257,277,301,321} is
  ≥ 0.50 (denominator = all 764×8 moved cells).
- H5_BELOW95 (movers read below 0.95): share of mover shapes
  with J(T_s,T_s0) < 0.95 is ≥ 0.50.
- H6_PAIRREPEAT (pairs repeat across shapes): the most frequent
  exact moved-set of size 2 occurs on ≥2 mover shapes (reads 0
  — not met — if no size-2 moved set exists).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with the
  tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 + m15);
R_s vs loo on all 764; cell-7 counts s0 2475 exact + tail counts
s0 102 exact with sub-bins 28+74 and max 47; s0 per-named-column
n + row lists exact (§Definitions); 733 tail 100 B + J 0.6694
exact with missing {301,321} + dests {303,323} + offsets +2/+2
+ private-col n/rows (303: 9, r25–33; 323: 10, r25–34) exact
(else stop everything); 731 tail 100 B + J 0.6833 exact with
missing {257,277} + dests {259,279} + offsets +2/+2 +
private-col n/rows (259: 9, r25–33; 279: 9, r25–33) exact (else
stop everything); below-0.95 9-list tail+J4 exact vs m22.txt
reprint in m27.txt (else stop before the join only — Tasks 1–2.2
already tabled stand); δ≠0 throughout cell 7 (all analyzed
shapes); P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m27.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards + s0
   reference guard + 733/731 swap guard (pairs + offsets + rows
   or stop).
3. Task 1: census matrix (TSV to work dir + evidence copy) +
   mover census + pair co-occurrence.
4. Task 2: displacement distribution + destinations +
   below-0.95 2×2 join.
5. Determinism re-run receipt (Task 1 on s0+733+731, canonical
   sha).
6. PNG census heatmap (764 shapes × 8 columns, green=present
   magenta=moved) to work dir; evidence copy ONLY if H5 meets
   AND ≥3 mover shapes read below 0.95 (the mover/below-0.95
   overlap visible in the pre-registered 2×2 split) — else
   absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 03:09 EDT, stop by 07:09).

Amendment (03:20 EDT, before the receipt run — clarification only,
no bar or definition changed): the below-0.95 9-list tail+J4
targets are the DESIGN-pinned constants above, verified pre-run
against `/Volumes/Extreme SSD/m22/m22.txt` (read-only grep: all 9
rows identical); m27.txt reprints only the 733/731 rows, so the
guard compares recomputed values to these pinned constants.
