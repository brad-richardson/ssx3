# M38 — Design (recorded before running)

Goal: shared-site triple (M36 gap 2): the (278,314) + (295,332)
missings on all three shapes (s2+s3+s700) and the (276,313)
missing on s2+s3 — 3 sites recurring across shapes with
identical s0 values but per-shape gaps. Cross-shape value/gap
comparison at shared (r,c): at shared (r,c), s0's values are
identical — do the Q shapes' gaps agree (same standing, same
magnitude) or diverge per shape (s2's 40 vs 42 at (278,314)
already hints divergence)? Answer by table: per-site per-shape
values + recurrence context (do these rows/cols recur at other
missing/extra sites?) + gap-sign pattern vs the pooled missings
(7/10 ++, M36). Tables, no verdicts. Fully offline: no lease of
any kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (FULL TSV guard,
M34–M37 precedent), `/Volumes/Extreme SSD/m36/m36.txt` (the 3
shared sites + per-shape gaps to reproduce — match exactly or
table the mismatch and stop). Work dir:
`/Volumes/Extreme SSD/m38/` (new). Evidence:
`local/research/M38/` (committed with `git add -f`, prefix
`[M38]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M36/REPORT.md` (all of it:
gap 2 = this brief — the 3 shared missing sites with identical
s0 values but per-shape gaps; the pooled missings read 7/10 ++
with the 3 −− one shared site, 0/0/10 standings on own shapes;
the 24 extras read 14 near / 0 far / 10 non-cell on s0) plus
`local/research/M37/REPORT.md` (all of it: the corrected pooled
universe — 24 pooled extra sites = c54's 10 + 14 others; M36's
"23" matches no M36 extras count, M37 brief-count note; use
14).

## Estimator (`m38.py`, `control.py`)

Shared core (M37 `m37.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `attrib_lines`,
`gapsign_lines`, `dstats_lines`, `load_triplet`,
`compute_sets_for`, `split_planes`, `flat_to_planes`,
`yuv_to_rgb`; M36 `SHAPES` pins verbatim). Byte offset o -> row
o//1280; Y bytes at o%4==0/2. No P1/decile/streak/carrier/BFS/
displacement machinery: the brief pins no band/decile/streak/
carrier joins, so `compute_dec_masks` / `posjoin_lines` /
`direction_split` / `y_cell_map` / `bands_of` are dropped
(disclosed here; input integrity still rests on the triplet
fold sha + R_s-vs-loo on all 764 + FULL TSV guard + Model-0
recompute).

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
  47); s2 103; s3 103; s700 114 (M34-pinned).
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- Shared-site pins (M36 missing-site tables, the brief's stop
  rule; (r,c) -> offset + |δ_s0| + g_s0 + missing-shape set +
  per-shape Q gaps; all Y-plane, all noncell on each missing Q):
  (278,314): off 356468, |δ_s0| 20, g_s0 42, missing on
  s2+s3+s700, g_2 40, g_3 42, g_700 42.
  (295,332): off 378264, |δ_s0| 10, g_s0 −22, missing on
  s2+s3+s700, g_2 −21, g_3 −21, g_700 −21.
  (276,313): off 353906, |δ_s0| 8, g_s0 17, missing on s2+s3
  only, g_2 16, g_3 16 (s700-present: not missing on s700 —
  s700's status + |δ_700| + gap tabled as measured).
- Full missing pins (M36 missing tables, all 10 pooled sites;
  (Q,r,c) -> offset + |δ_s0| + qstat + g_s0 + g_Q):
  s2 (299,312): 383344/10/noncell/22/22;
  s2 (276,313): 353906/8/noncell/17/16;
  s2 (278,314): 356468/20/noncell/42/40;
  s2 (295,332): 378264/10/noncell/−22/−21;
  s3 (276,313): 353906/8/noncell/17/16;
  s3 (278,314): 356468/20/noncell/42/42;
  s3 (295,332): 378264/10/noncell/−22/−21;
  s700 (215,38): 275276/12/noncell/25/23;
  s700 (278,314): 356468/20/noncell/42/42;
  s700 (295,332): 378264/10/noncell/−22/−21.
- Full extra pins (M36 extra tables via M37 §Definitions, all
  24 pooled sites; guards the Task-2 recurrence universe):
  s2 (259,311)/17/noncell/−37/−37, (293,313)/8/bulk7/−18/−19,
  (296,332)/20/noncell/−41/−41, (297,332)/9/noncell/−20/−20,
  (240,339)/9/noncell/19/17; s3 (258,311)/34/noncell/−71/−71,
  (265,316)/8/bulk7/18/18, (238,336)/8/bulk7/17/16,
  (238,339)/8/noncell/17/18; s700 c54 rows
  [245,246,247,252,253,258,259,278,279,283] all adQ=8 bulk
  (−−), (25,299)/34/noncell/−71/−72,
  (259,311)/17/noncell/−37/−37, (291,313)/8/bulk7/−19/−19,
  (296,332)/20/noncell/−42/−41, (170,620)/11/noncell/−24/−23.
- Q status taxonomy at a shared (r,c) (per shape Q): "missing"
  = in T_0 but not in T_Q; "tail" = in T_Q (shared tail);
  "bulk" = in maskQ with |δ_Q|<8; "noncell" = not in maskQ.
  For a missing site the Q-side cell status reads noncell per
  M36 (reproduced, not assumed).
- Pooled-missing sign split (M36 match target): 7/10 ++ over
  the 10 pooled missings (the 3 −− are the shared (295,332)
  site on all three shapes). Pooled-extra standing split
  (M36 match target): 14 bulk / 10 noncell on s0.

### Task 1 — shared-site recompute (do the 3 sites reproduce?)

The 3 shared sites recomputed from the dumps FIRST (§Guards —
offsets, |δ_s0|, s0 gaps, per-shape statuses, |δ_Q| n/a,
per-shape gaps must match M36 exactly — or table the mismatch
and stop; no further tasks run).

1. Per-site per-shape table: (r,c) × s2/s3/s700 — Q status
   (missing/tail/bulk/noncell per §Definitions), signed gaps
   g_s0 + g_Q, gap signs, |δ_s0| (+ |δ_Q| where Q holds tail,
   i.e. s700 at (276,313), tabled as measured).
2. Divergence table: per-site range of Q gaps across shapes
   (max−min over the missing shapes; the all-3 range tabled
   alongside for (276,313) with s700's measured gap — numbers
   only: agree / diverge-by-1 / diverge-more).
3. Sign table: per-site per-shape signs vs the pooled-missing
   7/10 ++ split (which side does each shared site fall on? +
   the pooled 10 recomputed).

### Task 2 — recurrence + standing context

1. Row/col recurrence: rows {276, 278, 295} + cols
   {313, 314, 332} at OTHER missing/extra sites across the 24
   pooled extras + 10 pooled missings (per-row: other pooled
   sites sharing the row; per-column: other pooled sites in
   the column; shared rows beyond the shared sites? shared
   columns? — per-shape multiplicity + unique (r,c)).
2. Standing context: the 3 sites' noncell-Q standing vs the
   pooled missings' standings (all 10 noncell on own Q per
   M36 — reproduce the 0/0/10 split) + vs the extras'
   bulk/noncell split (14/10 per M36 — reproduce).
3. s700-absent check: (276,313) is s0-present and
   s700-present (not missing on s700) — table s700's row-list
   at c313 around r276 (full s0 vs s700 row lists + a
   per-row window r∈[270,282] of T_0/T_700 membership: does
   s700 hold the row s2/s3 drop?).

### Task 3 — controls + determinism (M18–M37 precedent)

`control.py` (imports `m38` cell/tail core; expectations
analytic):

- C-SHARED (known shared sites, mimics the shared-missing
  triple): synthetic truth mid' on s0: N_both=3
  currently-TAIL Y sites (offset order, first 3 passing the
  per-site strict-interior landing check) injected on BOTH
  shape B and shape C (shared-missing, all-3-shapes style) +
  N_B=2 further tail sites injected on B only + N_C=2 further
  tail sites injected on C only, each mid'=blend+1 (fall back
  to blend−1 per site if +1 is not strictly inside —
  tabled). Shapes A = s0 orig, B = s0 mid'_B, C = s0 mid'_C.
  Recompute cell 7 + tail on B and C: M_B = T_A − T_B must
  equal the injected 5 exactly, M_C = T_A − T_C must equal
  the injected 5 exactly, M_B ∩ M_C must equal the injected
  shared 3 exactly, per-site |δ| exact (1), gaps equal on all
  three frames at every injected site (v0/full unchanged —
  the known gaps recovered), other-frame statuses exact
  (missings bulk on B/C with |δ|=1), the per-site per-shape
  table (status on B × status on C + gaps) recovered exactly,
  cell-7 masks fixed on both, all other tail members' δ
  unchanged.
- Pass = sets + shared intersection + per-site per-shape table
  + gaps + standings exact.

Determinism: re-run Task 1 (per-site per-shape table +
divergence + sign tables) on s0+2+3+700 with fresh loads;
canonical text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s2 + s3 + s700
triplets + m15 triplets + `m34-census.tsv` + `m36.txt` shas;
triplet fold sha over all 764x3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M37 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned from M36: the 3 shared missing sites (2 on all
three shapes, 1 on s2+s3) + the 24 pooled extras + 10 pooled
missings.

- H1_GAP_AGREE (Q gaps agree across missing shapes): ≥2 of the
  3 shared sites read gap-range 0 across their missing shapes
  (exact agreement, not just sign).
- H2_SHARED_SIGN_SPLIT (shared sites straddle the missing
  ++/−− line): ≥1 shared site reads ++ on all its missing
  shapes AND ≥1 shared site reads −− on all its missing
  shapes.
- H3_ROW_RECURRENCE (shared rows recur elsewhere): ≥1 of rows
  {276, 278, 295} appears at another pooled extra/missing
  site beyond the shared triple (per-shape multiplicity
  ignored).
- H4_COL_RECURRENCE (shared columns bear other sites): ≥1 of
  cols {313, 314, 332} bears another pooled extra/missing
  site beyond the shared triple (per-shape multiplicity
  ignored).
- H5_MISS_NONCELL (missings are set changes, M36 reproduce):
  10/10 pooled missings read noncell on their own shape Q.
- H6_S700_HOLDS (s700 holds the s2/s3-dropped row in tail):
  (276,313) reads tail (in T_700), not bulk or noncell, on
  s700.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact (s2/s3/s700 cell counts tabled as
measured, must equal M36's measured 2469/2484/2605 or table
the mismatch and stop, with d!=0 throughout); tail counts s0
102 exact with sub-bins 28+74 and max 47, s2/s3 103 exact,
s700 114 exact + J 0.9159/0.9340/0.8462 exact; FULL unnamed
TSV match (all 764 rows: tail + J4 + all-33-column n/ov/pres)
vs `m34-census.tsv` (else stop everything); 2/3/700 moved
sets == the pinned 6/7/8 + per-cell n/ov + standings +
deltas (§Definitions via SHAPES, else stop everything);
pooled per-shape extra/missing counts == 5+4 / 4+3 / 15+3
(else stop everything); the 3 shared sites' offsets + |δ_s0|
+ s0 gaps + per-shape missing statuses + per-shape Q gaps ==
§Definitions pins (else stop everything); all 10 pooled
missings' (offset + |δ_s0| + qstat + g_s0 + g_Q) == pins
(else stop everything); all 24 pooled extras' (offset + adQ
+ ostat + adO + gQ + gO) == pins (else stop everything); all
34 pooled sites Y-plane (tabled; any non-Y = stop and table);
P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34-census.tsv`/`m36.txt` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + 2/3/700 row guards (k 6/7/8 +
   standings + deltas or stop) + pooled-count guards +
   shared-site pins + 10-missing pins + 24-extra pins (or
   stop).
3. Task 1: per-site per-shape table (3 sites × 3 shapes) +
   divergence table + sign table (shared + pooled).
4. Task 2: row/col recurrence tables + standing-context
   tables + s700 c313 row-list + window.
5. Determinism re-run receipt (Task 1 on s0+2/3/700,
   canonical sha).
6. PNG shared-site map (s0 geometry; shared sites by gap-sign:
   ++ yellow / −− cyan; other pooled missings magenta;
   pooled extras red; s700 shared tail green) to work dir;
   evidence copy ONLY if H1 meets AND H2 meets (the
   agree/diverge + sign split visible in the pre-registered
   per-site coloring) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 04:56 EDT, stop by 08:56).
