# M29 — Design (recorded before running)

Goal: partial-move attribution (M28 gap 1): shapes 22/708/709/710
move single named columns by 1–2 rows at J 0.9510–0.9902 (2
extra-only + 2 no-cand... precisely: 22 extra-only, 708/709/710
missing-only no-cand, 0 assigned). Per-byte delta-row tables
(M27 Task-1 method: cross-frame |δ| + cell/bulk status on the
other shape, signed gaps both shapes, s0-anchored
band/decile/streak/carrier joins) for the ±1–2 delta rows, plus
the extra-only vs missing-only comparison + 734-c342 +
row-tolerant standings. Tables, no verdicts. Fully offline: no
lease of any kind, no boots, no harness runs, no fork changes,
no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`; only s0 + the 6 analyzed
shapes + m15 + top-10 carriers are loaded — no full 764 pass),
`/Volumes/Extreme SSD/m15/` (triplet, baseline guard only — no
m15 analysis), `/Volumes/Extreme SSD/m28/m28.txt` (partial-move
standings to reproduce) + `/Volumes/Extreme SSD/m28/
m28-census.tsv` (per-shape tail/J + n/ov/pres to reproduce —
match exactly or table the mismatch and stop). Work dir:
`/Volumes/Extreme SSD/m29/` (new). Evidence:
`local/research/M29/` (committed with `git add -f`, prefix
`[M29]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M28/REPORT.md` (all of it:
10 movers / 15 moved cells, 7 assigned + 3 extra-only + 5
no-cand; partials 22 c296 11/9 extra-only, 708 c296 8/8
missing-only −1, 709 c301 10/10 missing-only −1, 710 c340 6/6
missing-only −2, all at J 0.9510–0.9902 with no destination;
extras also 9 c321 11/10 + 734 c342 7/5) plus
`local/research/M27/REPORT.md` (Task-1 per-site table
precedent: offset/plane/row/col, cross-frame |δ|, signed gaps
both frames; full-swap reference: priv/miss 100% band-0, miss
100% dec-9, priv ~21% dec-9, all non-cell on the other frame).

## Estimator (`m29.py`, `control.py`)

Shared core (M27 `m27.py` / M28 `m28.py` verbatim where
reused): `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`interior_sites` (cell 7 = M19 id 7 verbatim), `tail_bulk_masks`
(|δ|≥8 tail), `plane_of_byte`, `plane_coords`, `parse_loo`,
`jaccard`, `off_of`, `y_col_rows`, `priv_y_cols`,
`census_of_shape` (exact-match presence), `assign_one`
(≥2-site private columns, nearest-column + overlap + smallest
tie-breaks), `bands_of`/`ROW_BAND` thirds, `p1_gradient` (M18 P1
block verbatim), `attrib_lines` (per-site cross-value rows),
`posjoin_lines` (s0-anchored band/decile/streak/carrier + 701
split). Byte offset o -> row o//1280; Y bytes at o%4==0/2. No
BFS/component/displacement machinery (no Task-2-of-M27 here).

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard on analyzed shapes).
- Bulk = cell-7 bytes with |δ|<8. Tail = cell-7 bytes with
  |δ|≥8. Tail MAP of shape s: T_s = tail boolean mask.
- Named columns (the census 8, fixed order): [257,277,296,301,
  321,340,342,343]. s0 reference row lists (M27/M28, guarded
  exact): 257:[23–32], 277:[23–32], 296:[24,25,26,27,28,31,32,
  33,34], 301:[23–33], 321:[23–32], 340:[24,25,26,27,31,32,33,
  34], 342:[27,28,29,34,35], 343:[26,27].
- Column rows rows_s(c), overlap ov, missing m = n0−ov, extra
  e = n_s−ov, PRESENT = exact row-list match (M28 pinned).
- PARTIAL-move cell (pinned): a moved cell (pres==0) with
  overlap ov>0 AND miss+extra ≤ 2 (a ±1–2 row delta on an
  otherwise-present column, not a wipe or swap). Full wipes
  (ov==0) are pinned OUT of the delta-row tables.
- Analyzed shapes (pinned): 22 (c296), 708 (c296), 709 (c301),
  710 (c340) — Task 1; 9 (c321, M28's other extra) + 734
  (c342 only — 734's c340/c343 full wipes are OUT of scope)
  — Task 2. The estimator asserts the recomputed partial-cell
  set over the 10 M28 movers equals exactly these 6 cells
  (else table the mismatch and stop — a 7th partial, or a
  missing one, changes every pooled denominator).
- Delta rows of a partial cell: extra rows rows_s(c)−rows_0(c)
  + missing rows rows_0(c)−rows_s(c). Delta-row SITES: Y-tail
  sites at those (row,col) on the owning frame (extra sites
  tail on shape s; missing sites tail on s0).
- Full priv/miss/shared sets per analyzed shape are also
  recomputed (counts + J + tail, guarded vs the TSV); priv/
  miss sites OUTSIDE the moved column are tabled as counts +
  (row,col) lists (no per-site values — brief pins values for
  delta rows only), so no divergence is hidden.
- Near-miss (pinned, M27 verbatim): delta-row site whose
  other-frame status is bulk with |δ_other| ∈ {6,7}. Far:
  bulk with |δ_other| ≤ 5. Non-cell: not cell-7 on the other
  frame.
- Position joins are s0-ANCHORED (pinned, M27 verbatim):
  geometry bands, P1 deciles on s0 mid-Y (edges guarded vs
  m18 constants), named streak columns, M22-verbatim top-10
  carrier masks + 701 split.
- Span position (pinned, Task 2.1): a delta row is EDGE iff
  row ≤ min(rows_0(c)) or row ≥ max(rows_0(c)) of its moved
  column's s0 span, else INTERIOR (hole-fill or mid-span);
  half is TOP iff row ≤ median(rows_0(c)) else BOTTOM.
- Row-tolerant rules (pinned, tabled WITHOUT adopting — the
  census rule stays exact-match):
  - RT-PRES (presence tolerance): column present-tolerant iff
    miss ≤ 2 AND extra ≤ 2. Tabled: per-cell tolerant
    standing on the 6 partial cells + the mover list over the
    10 M28 movers under RT-PRES (non-movers cannot change —
    tolerance only un-moves cells).
  - RT-DEST (destination tolerance): for each MISSING delta
    row (r,c): nearest private-Y site by Manhattan distance
    (M27 displace machinery, but vs the shape's PRIVATE set,
    same column set as M28 candidates — all private Y sites,
    singletons allowed); assigned iff dmin ≤ 2, dest = that
    site's column (ties → smallest column). Extra-only cells
    have no missing rows → unassignable (tabled as such).

### Task 1 — delta-row tables (what are the ±1–2 rows?)

Partial-move rows recomputed from the dumps (per-shape n/ov/
standing must match M28 exactly — §Guards — or table the
mismatch and stop; no further tasks run).

1. Per-shape delta rows: for each of the 6 partial cells, the
   extra + missing row lists, then M27-style per-site rows
   for every delta-row site (offset, plane, row, col, |δ|
   here, other-shape status + |δ|, signed gaps both),
   offset-ordered, in the receipt; near/far/non-cell summary
   + gap-equality shares per shape (M27 `attrib_lines`
   verbatim, called with priv=extra-row sites,
   miss=missing-row sites of that shape).
2. Near-miss check: per-shape H1/H2-style shares (near =
   bulk |δ|∈{6,7} vs non-cell) + pooled shares over all
   delta-row sites — tabled.
3. Position join: per-shape `posjoin_lines` verbatim (priv=
   extra sites, miss=missing sites, shared=that shape's FULL
   shared set S_s) + one POOLED join (priv=all extra-row
   sites, miss=all missing-row sites, shared=s0 tail T_s0 as
   the common baseline, labeled as such). Do partials
   localize like full swaps (band-0, streak columns, dec-9)?
   — tabled.

### Task 2 — extra-only vs missing-only (two populations?)

1. Pooled extra-row sites (22 + 9: 3 sites... precisely 2+1)
   vs pooled missing-row sites (708 + 709 + 710: 1+1+2 = 4
   sites): value stats (|δ| min/med/max per pool, gap-sign
   splits both frames, other-frame status splits) +
   position stats (EDGE/INTERIOR + TOP/BOTTOM per pool).
2. 734-c342 row (extra-only +2): same delta-row table as
   Task 1 (it is the 6th partial cell) + side-by-side vs
   22's extra (n/ov, |δ| ranges, gap signs, other-frame
   status, decile/band, EDGE/INTERIOR) — same phenomenon or
   different? — tabled.
3. Standing update: RT-PRES per-cell standings + RT-PRES
   mover list + RT-DEST per-missing-row dmin/dest rows —
   tabled WITHOUT adopting (exact-match census stands).

### Task 3 — controls + determinism (M18–M28 precedent)

`control.py` (mid-level synthetic truths, M27-style — feasible
because partial flips keep cell-7 membership: tail→bulk needs
gap≥1... precisely: missing-row injection flips tail→bulk
(|δ|=1, stays strictly inside iff gap≥3... tabled per site
with fallback blend−1); extra-row injection flips bulk→tail
(|δ|=8 at bulk gap≥17 sites, M27 C-P1 pool verbatim)):

- C-PART-MISS (known missing-only partial, mimics 710): s0
  mid'' with the FIRST 2 offset-order s0-tail Y sites in
  column c340 flipped to bulk (mid''=blend+1, fallback
  blend−1 per site if +1 is not strictly inside — tabled).
  Known: delta rows = those 2 rows, n/ov = 6/6, standing
  no-cand (priv=∅ → no candidates), per-site values exact.
- C-PART-EXTRA (known extra-only partial, mimics 22): s0
  mid' with the FIRST 2 offset-order interior-BULK gap≥17 Y
  sites in column c296 flipped to tail (mid'=blend+8 even /
  blend−8 odd, |δ|=8; if c296 holds <2 such sites, take the
  remainder from c343, then anywhere in offset order —
  tabled). Known: delta rows = those rows, n/ov exact,
  standing extra-only, per-site values exact.
- Pass = delta-row sets + n/ov/pres + standing + per-site
  |δ|/status/gaps exact on both (N=2 shapes).

Determinism: re-run Task 1 (delta rows + per-site rows +
per-shape joins) on s0+22+708; canonical text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + 9/22/708/709/
710/734 + m15 triplets + top-10 carrier triplets + `m28.txt`
+ `m28-census.tsv` shas. Model-0 recompute: R_0/fnv must match
M17–M28 (s0 22815 / `6b9ffda25bd76c6f`, m15 13418 /
`306b5c778898b64a`). Mismatch = stop and table. R_s vs
`loo.txt` cross-check on ALL analyzed shapes (0/9/22/708/709/
710/734 — want all equal; mismatch = stop and table).
`loo.txt` 764 rows + top-10 shapes/shares match M16. P1 edges
+ carrier removed counts/bands (M19 values) guarded.

## Falsification bars (recorded before running; tables, no verdicts)

Pooled denominator = all delta-row sites over the 6 partial
cells (want 9: extras 2+1+2, missings 1+1+2 — tabled; per-shape
shares tabled alongside).

- H1_NEARMISS (delta rows are near-misses): share of pooled
  delta-row sites with other-frame bulk status and |δ_other|
  ∈ {6,7} is ≥ 0.50.
- H2_SETCHANGE (delta rows are set changes, not δ changes):
  share of pooled delta-row sites with other-frame non-cell
  status is ≥ 0.50.
- H3_DEC9 (delta rows sit in dec-9 like full-swap missings):
  share of pooled delta-row sites in s0-P1 decile 9 is
  ≥ 0.50.
- H4_EDGE (deltas grow at column-span edges, not holes):
  share of pooled delta rows at EDGE span position is
  ≥ 0.50.
- H5_EXTRAMISS (extra vs missing are two value populations):
  median |δ| over pooled extra-row sites differs from median
  |δ| over pooled missing-row sites (meets iff strictly
  unequal — tabled with both medians + ranges).
- H6_TOLASSIGN (row tolerance resolves a destination): ≥1
  missing delta row assigns under RT-DEST (dmin ≤ 2 to a
  private-Y site).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on 0/9/22/708/709/710/734; cell-7 counts s0
2475 exact + tail counts s0 102 exact with sub-bins 28+74 and
max 47; s0 per-named-column n + row lists exact
(§Definitions); M28 TSV match on all 6 shapes (tail + J4 +
all-8-column n/ov/pres exact); M28 standing match on the 6
partial cells (22/c296, 9/c321, 734/c342 extra-only;
708/c296, 709/c301, 710/c340 no-cand); recomputed partial-cell
set over the 10 M28 movers equals exactly the 6 pinned cells;
δ≠0 throughout cell 7 (all analyzed shapes);
P(δ>0)==M19/M20 0.8093 on s0; P1 rounded edges match m18.txt
s0 row; `loo.txt` 764 rows + top-10 shapes/shares; removed
counts + bands (M19 values); self Jaccard == 1.0.

## Run protocol

1. Input shas + `m28.txt`/`m28-census.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on s0 + 6 shapes + count/J guard +
   s0 reference guard + M28 n/ov/standing guard (or stop).
3. Task 1: delta-row lists + per-site tables + near-miss +
   per-shape + pooled position joins.
4. Task 2: extra/missing pooled comparison + 734-c342
   side-by-side + RT-PRES/RT-DEST tables.
5. Determinism re-run receipt (Task 1 on s0+22+708, canonical
   sha).
6. PNG delta-row map (320x224, <5 MB total) to work dir;
   evidence copy ONLY if H3 meets AND ≥6 pooled delta-row
   sites share decile 9 (localization visible in the
   pre-registered decile split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 03:19 EDT, stop by 07:19).

Amendment (03:24 EDT, before the receipt run — guard scope
strengthened, no bar or definition changed): the estimator runs
the full 764-shape cell-7/tail/census pass (M28 §full-pass
verbatim, ~35 s, with R_s-vs-loo + triplet-fold-sha over all
764) instead of loading only the analyzed shapes, so the
partial-cell-set assertion is global (over all 764 shapes, not
just the 10 M28 movers). Task-1/2 analysis scope stays the 6
pinned partial cells; the pooled want stays 9 delta sites
(extras 2+1+2, missings 1+1+2).
