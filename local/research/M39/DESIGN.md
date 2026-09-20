# M39 — Design (recorded before running)

Goal: s3 all-delta-1 row (M36 gap 3): all 7 of shape 3's
still-below unnamed cells read delta-1 (4 extra-only + 3
missing-only, zero mixed) — the only still-below row with no
mixed cell. Row-list + value comparison vs s2/s700's mixed
cells (s2 c313 + s2 c332 + s700 c332, same method, same
pins): is s3's uniformity values-deep (its extras + missings
read like the mixed cells' extras/missings at delta 1) or
standing-only (mixed cells' delta-1 sides differ in
|δ|/gaps/signs)? Answer by table: per-cell row-lists +
per-site values + gap-sign splits, s3's 7 vs the 3 mixed
cells. Tables, no verdicts. Fully offline: no lease of any
kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (FULL TSV guard,
M34–M38 precedent), `/Volumes/Extreme SSD/m36/m36.txt` (s3's
7 cells + the 3 mixed cells to reproduce — match exactly or
table the mismatch and stop). Work dir:
`/Volumes/Extreme SSD/m39/` (new). Evidence:
`local/research/M39/` (committed with `git add -f`, prefix
`[M39]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M36/REPORT.md` (all of it:
gap 3 = this brief — s3's 7 cells extra-only c311/c316/c336/
c339 + missing-only c313/c314/c332, zero mixed; s2's mixed
c313/c332 + s700's mixed c332; per-site |δ|/status/gap tables
this brief reproduces) plus `local/research/M38/REPORT.md`
(all of it: the pooled splits — missings 10/10 noncell on own
Q, extras 14/10 bulk/noncell on s0; corrected pooled universe
24 = c54's 10 + 14 others).

## Estimator (`m39.py`, `control.py`)

Shared core (M38 `m38.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `load_triplet`,
`compute_sets_for`, `split_planes`, `flat_to_planes`,
`yuv_to_rgb`; M38 `SHAPES`/`M36_MISS`/`M36_EXTRAS` pins
verbatim). Byte offset o -> row o//1280; Y bytes at o%4==0/2.
No P1/decile/streak/carrier/BFS/displacement machinery: the
brief pins no band/decile/streak/carrier joins, so that
machinery stays out (disclosed here; input integrity still
rests on the triplet fold sha + R_s-vs-loo on all 764 + FULL
TSV guard + Model-0 recompute).

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
- Still-below unnamed moved sets (M34-pinned): s2 k=6, s3 k=7,
  s700 k=8 (21 cells; row guards cover all 21 per M38
  precedent — the brief's 10 cells are the Task-1/2 universe).
- Brief universe (10 cells = s3's 7 + the 3 mixed cells):
  s3 c311/c313/c314/c316/c332/c336/c339 (all delta-1:
  extra-only c311/c316/c336/c339, missing-only c313/c314/
  c332) + s2 c313 (mixed 1/1 d2) + s2 c332 (mixed 1/2 d3) +
  s700 c332 (mixed 1/1 d2). 8 extra sites + 6 missing sites
  = 14 sites.
- Row-list pins (M36 REPORT + m36.txt headliner; M36 exact):
  s0 c311 [296,297,298,299]; s0 c313 [274,275,276,292]; s0
  c314 [269,276,277,278,287,288,289]; s0 c332 [295,304]; s0
  c336 []; s0 c339 [] (n0=0 both). s0 c316: ONE row,
  measured-not-pinned (M36 states n0=1 only — M38 s700-held
  precedent); guard n0==1, Q-row == s0row+[265], extra row
  [265] pinned. Q-row pins: s3c311 [258]+s0rows extra [258];
  s3c313 s0minus[276] miss [276]; s3c314 s0minus[278] miss
  [278]; s3c332 [304] miss [295]; s3c336 [238] extra [238];
  s3c339 [238] extra [238]; s2c313 [274,275,292,293] extra
  [293] miss [276]; s2c332 [296,297,304] extras [296,297]
  miss [295]; s700c332 [296,304] extra [296] miss [295].
- Value pins (M36 extra/missing tables, the brief's stop
  rule; 8 extras (Q,r,c) -> offset/adQ/ostat/adO/gQ/gO):
  s3 (258,311) 330862/34/noncell/n/a/−71/−71;
  s3 (265,316) 339832/8/bulk/7/18/18;
  s3 (238,336) 305312/8/bulk/7/17/16;
  s3 (238,339) 305318/8/noncell/n/a/17/18;
  s2 (293,313) 375666/8/bulk/7/−18/−19;
  s2 (296,332) 379544/20/noncell/n/a/−41/−41;
  s2 (297,332) 380824/9/noncell/n/a/−20/−20;
  s700 (296,332) 379544/20/noncell/n/a/−42/−41.
  6 missings (Q,r,c) -> offset/adS0/qstat/gS0/gQ:
  s3 (276,313) 353906/8/noncell/17/16;
  s3 (278,314) 356468/20/noncell/42/42;
  s3 (295,332) 378264/10/noncell/−22/−21;
  s2 (276,313) 353906/8/noncell/17/16;
  s2 (295,332) 378264/10/noncell/−22/−21;
  s700 (295,332) 378264/10/noncell/−22/−21.
  Standings: s3 4×extra-only + 3×missing-only, all delta 1;
  s2c313 mixed d2; s2c332 mixed d3; s700c332 mixed d2.
- Extra side vs missing side: extra-side |δ| = |δ_Q| judged
  vs s0 (status bulk/noncell + |δ_s0|); missing-side |δ| =
  |δ_s0| judged on own Q (status + |δ_Q| n/a per M36 — all
  noncell). Gap signs: g_Q × g_O per site (++/−−, no zeros
  per M36 — reproduced, not assumed).
- Per-side delta: |extra delta| = extra count, |missing
  delta| = missing count per cell (delta = sum). M36:
  magnitude >1 lives only on s2c332's extra side (2);
  check the rest (all other sides read 0/1).

### Task 1 — s3 row + mixed cells recompute (do the cells reproduce?)

s3's 7 cells + s2's 2 + s700's 1 mixed cells recomputed from
the dumps FIRST (§Guards — row lists, standings, deltas,
per-site |δ|/status/gaps must match M36 exactly — or table
the mismatch and stop; no further tasks run).

1. Row-list table: all 10 cells s0-rows vs Q-rows vs
   extra/missing rows (M36-headliner style).
2. Standing table: 7 × delta-1-uniform vs 3 × mixed (extra
   counts + missing counts + deltas per cell).
3. Value table: per-site |δ_Q|/|δ_s0|, statuses, signed gaps,
   gap signs for all 10 cells' 14 sites.

### Task 2 — uniformity comparison (values-deep or standing-only?)

1. Extra-side comparison: s3's 4 extras (|δ|, bulk status,
   gaps, signs) vs the mixed cells' extra sides (same
   columns — med/match per site, numbers only).
2. Missing-side comparison: s3's 3 missings vs the mixed
   cells' missing sides (same columns).
3. Delta split: per-cell |extra delta| vs |missing delta|
   across the 10 cells (where does magnitude >1 live?
   extra side, missing side, or both?).

### Task 3 — controls + determinism (M18–M38 precedent)

`control.py` (imports `m39` cell/tail core; expectations
analytic):

- C-UNIFORM (known uniform + mixed cells, mimics the s3-vs-
  mixed split): synthetic truth mid' on s0: N_UNI=3 known
  delta-1 cells (2 extra-only: 1 injected tail landing each
  at currently-interior-BULK Y sites with gap≥17, first in
  offset order, mid'=blend+8 on even (r+c) / blend−8 on odd,
  per-site strict-interior check; 1 missing-only: 1 injected
  bulk landing at a currently-TAIL Y site, mid'=blend+1
  falling back to blend−1 per site if +1 is not strictly
  inside) + N_MIX=1 known mixed cell (1 extra landing + 1
  missing landing in the SAME Y column, same injection
  rules), all 4 cells in distinct Y columns except the mixed
  cell's shared column (columns assigned greedily in
  numeric order, tabled). Shape A = s0 orig, shape B = s0
  mid'. Recompute cell 7 + tail on B: per-cell standings
  must equal the injected 3×delta-1 (2 extra-only + 1
  missing-only) + 1×mixed (1/1 d2) exactly, per-site |δ|
  exact (extras 8, missings 1), gaps equal on both frames
  at every injected site (v0/full unchanged — tabled),
  other-frame statuses exact (extras bulk on A with
  original |δ| tabled; missings bulk on B), row-lists exact
  per cell, cell-7 mask fixed, all other tail members' δ
  unchanged.
- Pass = standings + row-lists + per-site values + gaps
  exact. Pool shortfall (no greedy assignment spans 3+1
  cells) = tabled RED, cannot-inject (M38 precedent).

Determinism: re-run Task 1 (row-lists + standings + per-site
values for the 10 cells) on s0+2/3/700 with fresh loads;
canonical text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s2 + s3 + s700
triplets + m15 triplets + `m34-census.tsv` + `m36.txt` shas
(m36.txt want `bf2c5d81…8213ae1` per M38);
triplet fold sha over all 764x3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M38 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned from M36: s3's 7 delta-1 cells (4 extra-only
+ 3 missing-only) + the 3 mixed cells (s2c313 1/1 d2,
s2c332 1/2 d3, s700c332 1/1 d2); 8 extra sites + 6 missing
sites = 14 sites. H1/H2/H7 are reproduce bars; H3–H6 are
values-deep agreement bars (meet = values-deep on that
facet; miss = standing-only on that facet — tabled, no
verdicts).

- H1_ROW_REPRO (row-lists reproduce): 10/10 brief cells read
  the §Definitions row-lists exactly (s0-rows + Q-rows +
  extra/missing rows; s0c316's single row measured with
  n0==1 + extra row [265]).
- H2_VALUE_REPRO (values reproduce): 14/14 brief sites read
  the §Definitions value pins exactly (offset + |δ| +
  status + signed gaps both frames).
- H3_EXTRA_AD_DEEP (extra magnitudes agree): |median s3-extra
  |δ_Q| − median mixed-extra-side |δ_Q|| ≤ 2.
- H4_MISS_AD_DEEP (missing magnitudes agree): |median s3-miss
  |δ_s0| − median mixed-missing-side |δ_s0|| ≤ 2.
- H5_EXTRA_SIGN_DEEP (extra signs agree): |++ share s3 extras
  − ++ share mixed extra sides| ≤ 0.25.
- H6_MISS_SIGN_DEEP (missing signs agree): |++ share s3
  missings − ++ share mixed missing sides| ≤ 0.34 (1-site
  granularity 1/3).
- H7_DELTA_SIDE (magnitude >1 lives extra-side-only): across
  the 10 cells, per-side deltas >1 count == 1 on the extra
  side (s2c332's 2) AND == 0 on the missing side.
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
deltas (else stop everything); pooled per-shape
extra/missing counts == 5+4 / 4+3 / 15+3 (else stop
everything); the 10 brief cells' row-lists == §Definitions
pins (else stop everything); all 14 brief sites' (offset +
|δ| + status + gaps) == pins (else stop everything); all 14
brief sites Y-plane (tabled; any non-Y = stop and table);
P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34-census.tsv`/`m36.txt` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + 2/3/700 row guards (k 6/7/8 +
   standings + deltas or stop) + pooled-count guards +
   brief row-list pins + 14-site value pins (or stop).
3. Task 1: row-list table (10 cells) + standing table +
   value table (14 sites).
4. Task 2: extra-side comparison + missing-side comparison
   + delta split (per-cell |extra| vs |missing| deltas).
5. Determinism re-run receipt (Task 1 on s0+2/3/700,
   canonical sha).
6. PNG uniformity map (s0 geometry; s3 extras green / mixed
   extras red / s3 missings yellow / mixed missings magenta)
   to work dir; evidence copy ONLY if H1 meets AND H2 meets
   AND exactly one of {H3, H4} meets (the extra-side vs
   missing-side agreement asymmetry visible in the
   pre-registered extra-vs-missing coloring) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 05:09 EDT, stop by 09:09).
