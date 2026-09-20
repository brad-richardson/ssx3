# M34 — Design (recorded before running)

Goal: unnamed-column partial scan (M33 gap 2 = M29 gap 3): 709's
c298 holds 4 missing rows (r28/29/34/35) — a second partial
column on 709 OUTSIDE the census 8, located in M29 but never
scanned for across the 764. Generalize M28's exact-match census
method to every tail-bearing non-named Y column: full presence
matrix + mover census + row-delta distribution + named/unnamed/
Jaccard joins. Tables, no verdicts. Fully offline: no lease of
any kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m28/m28.txt` + `/Volumes/Extreme SSD/m28/
m28-census.tsv` (named census to reproduce: 10 movers + all-764
tail/J4/n/ov/pres rows — match exactly or table the mismatch
and stop). 709-c298's 4 missing rows pinned from M29 REPORT
(r28/29/34/35 — match exactly or table the mismatch and stop).
Work dir: `/Volumes/Extreme SSD/m34/` (new). Evidence:
`local/research/M34/` (committed with `git add -f`, prefix
`[M34]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M33/REPORT.md` (all of it:
gap 2 = this brief; s9 cluster method + Jaccard/set machinery)
plus `local/research/M28/REPORT.md` (all of it: the exact-match
census method to generalize — per-shape x per-column presence
with row overlap; 10 movers / 15 cells; below-0.95 9-list) plus
`local/research/M29/REPORT.md` (§Task 1: 709 tail 97 J 0.9510 =
0 priv + 5 miss + 97 shared with outside-col miss 4 = c298
r28/29/34/35; M28 DESIGN/REPORT for the TSV format).

## Estimator (`m34.py`, `control.py`)

Shared core (M28 `m28.py` verbatim where reused): YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`, `parse_loo`,
PNG writer, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`priv_y_cols`, `census_of_shape` (named-8, guard only),
`fmt_f`. Byte offset o -> row o//1280; Y bytes at o%4==0/2. No
P1/carrier/BFS/displacement machinery (no gradient, carrier, or
destination task here — brief pins presence + overlap + joins).

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- d = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so d!=0
  throughout (guard).
- Bulk = cell-7 bytes with |d|<8. Tail = cell-7 bytes with
  |d|>=8. Tail MAP of shape s: T_s = tail boolean mask (N
  bytes). Want: s0 102 (sub-bins 28 in 8–15 + 74 in 16+, max
  47); 709 97.
- Named columns (M28 guard only, fixed order): [257,277,296,
  301,321,340,342,343]. s0 reference row lists (M27/M28,
  guarded exact): 257:[23–32], 277:[23–32],
  296:[24,25,26,27,28,31,32,33,34], 301:[23–33],
  321:[23–32], 340:[24,25,26,27,31,32,33,34],
  342:[27,28,29,34,35], 343:[26,27].
- UNNAMED domain (pinned): sorted union over all 764 shapes of
  tail-Y columns, minus the named 8. I.e. every Y column that
  bears >=1 tail site on >=1 shape, excluding the census 8.
  Rationale (recorded before running): the brief's "(hundreds)"
  cannot mean s0-only (s0's 37 other-tail sites span <=37
  columns); the union reading covers both the s0-bearing
  unnamed columns (n0>0 subset, the strict M28 generalization)
  and pure-private columns (n0==0, where 2/3/700's
  outside-named divergence must live). The estimator tables
  |UNNAMED| + the n0>0 vs n0==0 split; s0-only counts are
  tabled alongside wherever they differ.
- Column rows of shape s at column c: rows_s(c) = sorted Y-tail
  rows in column c (tail & Y & col==c). s0 rows rows_0(c)
  likewise (possibly empty for pure-private columns).
  Overlap ov_s(c) = |rows_s(c) ∩ rows_0(c)|. Missing m_s(c) =
  n0(c) − ov; extra e_s(c) = n_s(c) − ov. Row-delta d_s(c) =
  m + e (total differing rows; 709-c298 wants 4+0 = 4).
- PRESENT (pinned, M28 verbatim): rows_s(c) == rows_0(c)
  exactly (n equal + overlap == n0 — byte-identical column;
  for n0==0 columns: present iff the shape also holds none).
  ABSENT = moved = any difference. No tolerance rule (the
  RT-PRES/RT-DEST rules stay NOT adopted per M29).
- Unnamed-mover shape: >=1 absent unnamed column. Named-mover:
  >=1 absent named column (M28 guard: the 10-list).
- Moved-cell standings: missing-only (m>0,e==0), extra-only
  (m==0,e>0), mixed (m>0,e>0). Full wipe: ov==0 with n0>0 and
  n_s==0 (M28 usage: 711's pair). Fresh-column move: moved
  cell on an n0==0 column (always extra-only by construction).

### Task 1 — unnamed-column scan (all columns, all shapes)

Named census + 709-c298 rows recomputed from the dumps first
(FULL named TSV match on all 764 rows + mover 10-list +
709-c298 missing [28,29,34,35] — §Guards — or table the
mismatch and stop; no further tasks run).

1. Per-shape x unnamed-column presence matrix: all 764 x all
   |UNNAMED| with n_s(c), ov_s(c), present(1/0) + row-delta —
   the census matrix, committed as TSV `m34-census.tsv`
   (header: shape, tail_n, J_vs_s0, then per unnamed column in
   fixed ascending order: n{c}, ov{c}, pres{c}); summarized in
   the report (mover count, |UNNAMED|, n0>0 split).
2. Unnamed-mover census: shapes moving >=1 unnamed column
   (count, full shape list, moved-count hist, per-mover moved
   cells); per-column mover counts (all in the receipt;
   top-20 table in the report: movers, rate, miss-only/
   extra-only/mixed split).
3. Row-delta distribution over all unnamed moved cells: full
   value-count list (no binning) + summary (min/med/mean/max)
   + standing splits (missing-only/extra-only/mixed, full
   wipes, fresh-column moves, n0>0 vs n0==0).

### Task 2 — joins (named vs unnamed vs Jaccard)

1. Named∩unnamed 2x2: counts + shape lists in each cell
   (named-mover x unnamed-mover). Are the 10 named movers also
   unnamed movers? Is any unnamed mover named-still? — tabled.
2. Below-0.95 join: the 9 M28 shapes (tail+J4 guarded vs M28
   constants — §Guards — or stop the join only) vs the
   unnamed-mover census: unnamed-mover x below-0.95 2x2 with
   counts + shape lists; named-still+below rows (2/3/700:
   unnamed moved counts + cells) — do unnamed moves explain
   the below-but-still readings? — tabled.
3. 709-c298 row (the seed): s0 vs 709 row lists, n/ov/miss/
   extra/delta + rank: counts of unnamed moved cells with
   delta > 4 / == 4 / >= 4 (match-or-exceed) — tabled.

### Task 3 — controls + determinism (M18–M33 precedent)

`control.py` (mask-level synthetic truths — M28 pinned: the
census logic under test operates on tail masks, so the control
builds synthetic tail masks directly from the s0 tail mask
with KNOWN unnamed moves and checks exact recovery; universe
= s0-bearing unnamed columns + the injected fresh columns):

- U1 unnamed missing-only partial (mimics 709-c298): drop s0
  c298 rows 28,29, add nothing. Known: moved {298}, n/ov =
  (n0−2)/(n0−2), delta 2, missing-only.
- U2 fresh-column extra-only (n0==0 move): add rows 100,101 in
  the first Y column with no s0 tail (tabled which). Known:
  moved {that col}, n/ov = 2/0, delta 2, extra-only.
- U3 unnamed full wipe: drop ALL s0 rows of the smallest-n0>0
  unnamed column (tabled which). Known: moved {that col},
  n/ov = 0/0, delta = n0, missing-only wipe.
- U4 unnamed mixed: drop 1 s0 row + add 1 fresh row in the
  largest-n0>0 unnamed column (tabled which/rows). Known:
  moved {that col}, delta 2, mixed.
- Pass = moved-sets + per-column n/ov/pres + row-deltas +
  standings exact on all 4 (N=4 shapes). Target columns are
  derived from the s0 tail at control time (tabled); the
  KNOWN part is the injected edit + expected census rows.

Determinism: re-run Task 1 presence (unnamed census rows +
row-deltas + J values) on s0+709 with fresh loads; canonical
text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + 709 triplets +
m15 triplets + `m28.txt` + `m28-census.tsv` shas; triplet fold
sha over all 764x3 bins (M28 precedent). Model-0 recompute:
R_0/fnv must match M17–M33 (s0 22815 / `6b9ffda25bd76c6f`,
m15 13418 / `306b5c778898b64a`). Mismatch = stop and table.
R_s vs `loo.txt` cross-check on ALL 764 shapes (want 764/764
equal; mismatch = stop and table). `loo.txt` 764 rows +
top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_NAMEDINUNNAMED (named movers also move unnamed): share of
  the 10 named movers moving >=1 unnamed column is >= 0.50.
- H2_STILLMOVE (unnamed movers are new faces): share of
  unnamed movers that are named-still is >= 0.50 (reads 0 —
  not met — if no unnamed mover exists).
- H3_SMALLDELTA (unnamed moves are <=2-row partials): share of
  unnamed moved cells with row-delta <= 2 is >= 0.50.
- H4_WIPE (unnamed moves are wipes): share of unnamed moved
  cells with ov == 0 is >= 0.50.
- H5_BELOW95 (unnamed movers read below 0.95): share of
  unnamed movers with J(T_s,T_s0) < 0.95 is >= 0.50 (reads 0
  — not met — if no unnamed mover exists).
- H6_C298RANK (the seed delta is big): 709-c298's row-delta
  (want 4) is >= the median unnamed moved-cell row-delta.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with the
  tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 + m15);
R_s vs loo on all 764; cell-7 counts s0 2475 exact + tail counts
s0 102 exact with sub-bins 28+74 and max 47; s0 per-named-column
n + row lists exact (§Definitions); FULL named TSV match (all
764 rows: tail + J4 + all-8-column n/ov/pres) vs
`m28-census.tsv` (else stop everything); named mover list ==
M28's [9,22,708,709,710,711,731,732,733,734] (else stop
everything); 709-c298 missing rows == [28,29,34,35] exactly
(else stop everything); below-0.95 9-list tail+J4 exact vs M28
constants (else stop before the join only — Tasks 1–2.1
already tabled stand); d!=0 throughout cell 7 (all analyzed
shapes); P(d>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m28.txt`/`m28-census.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards + s0
   reference guard + FULL named TSV guard + 709-c298 guard
   (rows or stop).
3. Task 1: unnamed census matrix (TSV to work dir + evidence
   copy) + mover census + top-20 columns + delta hist.
4. Task 2: named∩unnamed 2x2 + below-0.95 join + 709-c298
   rank row.
5. Determinism re-run receipt (Task 1 on s0+709, canonical
   sha).
6. PNG unnamed census heatmap (764 shapes x |UNNAMED| columns,
   green=present magenta=moved) to work dir; evidence copy
   ONLY if H5 meets AND >=3 unnamed movers read below 0.95
   (the mover/below-0.95 overlap visible in the pre-registered
   2x2 split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 04:09 EDT, stop by 08:09).
