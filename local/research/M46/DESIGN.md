# M46 — Design (recorded before running)

Goal: shape-9 far/near private split (M33 gap 1 via M36 gap 6):
the 22 cluster privates split into a far block (16 sites, rows
226–252, dmin 18–49) and a near block (6 sites, rows 269–305,
dmin 1–7, interleaved with the missings in two mixed union
comps). Per-sub-block value/join split: do the far 16 and near
6 differ in |δ|/gaps/signs/band/decile, or is dmin the only
split? Answer by table: displacement reproduction + per-block
value tables + join seats. Tables, no verdicts. Fully offline:
no lease of any kind, no boots, no harness runs, no fork
changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m33/m33.txt` (the 22 dmins + statuses to
reproduce — match exactly or table the mismatch and stop),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (FULL TSV guard).
Work dir: `/Volumes/Extreme SSD/m46/` (new). Evidence:
`local/research/M46/` (committed with `git add -f`, prefix
`[M46]`, trailer `Orchestrated-By: Muse Code`; NEVER `git
push` in ssx3).

Headers read first: `local/research/M33/REPORT.md` (all of it:
22 cluster privates + dmins + statuses; far block 12/16
far-bulk on s0 (1 near, 3 non-cell); near block interleaved
with missings in two mixed union comps; displacement +
8-conn + s0-anchored join machinery reused verbatim) plus
`local/research/M35/REPORT.md` (shape-9's per-site values —
the value side of the split: per-cell |δ|/gaps/signs +
band/decile seats; dstats/gapsign machinery reused verbatim).

## Estimator (`m46.py`, `control.py`)

Shared core (M33 `m33.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|δ|≥8 tail), `plane_of_byte`,
`plane_coords`, `parse_loo`, `jaccard`, `off_of`,
`y_col_rows`, `bands_of`/`ROW_BAND`, `p1_gradient` (M18 P1
block verbatim), `attrib_lines`, `posjoin_lines`,
`displace_lines` core, `comp_lines`, `connected_components`,
`comp_labels`, `occupancy_lines`, `dmin_list`, PNG writer;
M35 `m35.py` verbatim where reused: `tail_y_cols`,
`census_unnamed_of`, `gapsign_lines`, `dstats_lines`). Byte
offset o -> row o//1280; Y bytes at o%4==0/2.

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
- Full sets (shape 9 vs s0): P_9 = T_9 − T_s0 (want 23), M_9
  = T_s0 − T_9 (want 8), S_9 = T_9 ∩ T_s0 (want 94);
  23+94=117 ✓, 8+94=102 ✓, 94/125=0.7520 ✓.
- Cluster privates C_priv = P_9 minus the c321 r266 site
  (want 22, all Y — M33's set, guarded exact).
- FAR block F (want 16, rows 226–252, dmin 18–49):
  (226,351)/26, (232,327)/43, (233,327)/42, (234,337)/48,
  (235,337)/49, (239,336)/45, (239,339)/48, (240,318)/26,
  (241,318)/25, (243,318)/23, (244,316)/20, (245,315)/20,
  (245,316)/19, (246,314)/20, (248,312)/20, (252,310)/18.
- NEAR block Q (want 6, rows 269–305, dmin 1–7):
  (269,313)/3, (270,313)/4, (274,322)/7, (289,315)/3,
  (290,315)/4, (305,332)/1.
- Dmin hist (cluster 22, pinned): 1:1 2:0 3:2 4:2 5+:17
  (d1 share 0.0455).
- Far statuses (pinned, M33): 12 far-bulk / 1 near / 3
  non-cell; near = (239,336) (|δ_s0| 6); non-cell =
  (226,351), (239,339), (252,310); rest far-bulk.
- Near statuses (pinned, M33 per-site rows): 2 far-bulk
  ((269,313) + (270,313), |δ_s0| 1/1) / 0 near / 4 non-cell
  ((274,322), (289,315), (290,315), (305,332)).
- Mixed union comps (pinned, M33 bboxes + counts; membership
  reproduced here): mix-A size 6 cpriv 2 cmiss 2
  bbox r[266,270]c[313,315] with priv {(269,313),(270,313)}
  + miss {(266,315),(269,314)}; mix-B size 5 cpriv 2 cmiss
  2 bbox r[287,290]c[314,315] with priv {(289,315),(290,315)}
  + miss {(288,314),(289,314)}.
- Near-miss (pinned, M27 verbatim): other-frame bulk with
  |δ_other| ∈ {6,7}. Far: bulk with |δ_other| ≤ 5.
  Non-cell: not cell-7 on the other frame.
- Position joins are s0-ANCHORED (pinned, M27 verbatim):
  geometry bands, P1 deciles on s0 mid-Y (edges guarded vs
  m18 constants), named streak columns, M22-verbatim top-10
  carrier masks + 701 split.
- Displacement (pinned, M27 verbatim): nearest-shared-site
  Manhattan distance, same plane, plane-native coords,
  brute-force exact; hist bins {1,2,3,4,5+} (0 impossible by
  construction — guarded).
- Components (pinned, M27 verbatim): 8-conn union-find on
  Y; U/V tabled iff nonempty.

### Task 1 — displacement reproduction (do the 22 dmins reproduce?)

The 22 dmins recomputed from the dumps (M33 method verbatim:
nearest-shared-site same-plane Manhattan; must match exactly
— or table the mismatch and stop):

1. dmin table: all 22 sites with recomputed dmins (far
   18–49 + near 1–7 + hist 1:1 2:0 3:2 4:2 5+:17) vs the
   `m33.txt` parse (§Guards).
2. Status table: far-bulk/near/noncell per site (far block
   12/1/3 + near block 2/0/4 — the new data), via
   `attrib_lines` per block.
3. Comp table: the two mixed union comps' membership (which
   near privates + which missings per comp + shared fill),
   via `comp_labels` core + per-member flags.

### Task 2 — per-sub-block value/join split (values-deep or dmin-only?)

1. Value tables: far-16 vs near-6 |δ_9| lists/meds
   (`dstats_lines` verbatim), gap lists, gap-sign splits
   (`gapsign_lines` verbatim), bulk statuses (numbers only).
2. Join seats: band + gradient-decile distributions per
   block (M35 §Task 2 joins recomputed per block via
   `posjoin_lines` verbatim — do the blocks share seats?).
   Streak/carrier tabled alongside (M33 precedent: all
   other / 0 in any mask).
3. Missing-contrast table: the 8 missings (dmin 1–2, d1
   share 0.75) vs the near block (dmin 1–7 — do near
   privates read missing-like in values/seats?).

### Task 3 — controls + determinism (M18–M45 precedent)

`control.py` (mid-level synthetic truth, M33-style —
feasible because block flips keep cell-7 membership):

- C-SPLIT (known far/near blocks, mimics the 16+6 split at
  small N): s0 mid' with N_far=6 far-dmin + N_near=6
  near-dmin currently-interior-BULK gap≥17 Y sites flipped
  to tail (mid'=blend+8 even / blend−8 odd, |δ|=8;
  per-site strict-interior check; far = first 6 in offset
  order with dmin≥18 vs the post-miss shared set, near =
  first 6 with dmin≤7) AND N_miss=4 currently-TAIL Y sites
  flipped to bulk (mid'=blend+1, fallback blend−1 per site
  if +1 is not strictly inside — tabled). Known:
  priv = the 12, miss = the 4, tail' = 102−4+12 = 110,
  J = 98/114 = 0.8596 (`f"{J:.4f}"`; inter 102−4, union
  102+12 per the M33 union rule — corrected pre-receipt from
  98/110), per-site values exact, dmin ranges exact (far ≥18,
  near ≤7), seat counts sum-exact per block, cell-7 mask
  fixed.
- Pass = sets-exact + J-exact + dmin-range-exact +
  values-exact + seats-sum-exact.

Determinism: re-run Task 1 (pooled + per-block per-site
rows + block dmins + mixed-comp membership) on s0+9 with
fresh loads; canonical text sha byte-identical pass1 vs
pass2.

Input shas (sha256 full, in the receipt): s0 + s9 + m15
triplets + top-10 carrier triplets + `m33.txt` +
`m34-census.tsv` shas; triplet fold sha over all 764×3 bins
(M28/M34/M35 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M45 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.
FULL unnamed TSV byte-identical vs `m34-census.tsv` (M35
guard verbatim; mismatch = stop and table).

## Falsification bars (recorded before running; tables, no verdicts)

Denominators: F = 16 far-block privates, Q = 6 near-block
privates, M = 8 missings.

- H1_FARNEAR_BULK (blocks differ in bulk status): |far bulk
  share − near bulk share| ≥ 0.25.
- H2_FARNEAR_GAP (blocks differ in gap signs): |far ++
  share − near ++ share| ≥ 0.25 (g_9 × g_s0 signs).
- H3_FARNEAR_SEAT (blocks differ in join seats): |far
  band-1 share − near band-1 share| ≥ 0.25, or |far dec-9
  share − near dec-9 share| ≥ 0.25 (either leg meets;
  s0-anchored joins; M33-H4 analog re-anchored to blocks).
- H4_NEARMISS (near block reads missing-like in bulk
  status): |near bulk share − miss bulk share| < 0.25
  (met = missing-like; miss bulk share pinned 4/8).
- H5_FARNEAR_MED (blocks differ in |δ| level): |far median
  |δ_9| − near median |δ_9|| ≥ 4.
- H6_NEARMIX (near block interleaves with missings): share
  of near-block privates sitting in a mixed union comp
  (cpriv>0 and cmiss>0) ≥ 0.50.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34/M35; R_s vs loo on all
764; FULL unnamed TSV byte-identical (764 rows) vs
`m34-census.tsv`; s9 tail 117 + J 0.7520 + full sets priv
23 / miss 8 / shared 94; cluster (row,col) SETS exact vs
M33 (22 + 8); `m33.txt` parse vs DESIGN pins (22 dmins +
22 statuses + 8 miss dmins + mixed-comp counts/bboxes —
transcription check); recomputed 22 dmins exact (far
18–49 list + near 1–7 list + hist 1:1 2:0 3:2 4:2 5+:17);
recomputed far statuses 12/1/3 + near statuses 2/0/4 exact
per site; mixed union comps exactly 2 with (size, cpriv,
cmiss, bbox) + priv/miss membership exact; in-c321 priv
rows == [266]; s9 c321 rows == s0 c321 rows + [266]; s0
cell 2475 + s9 cell 2670; s0 tail 102 with sub-bins 28+74
and max 47; δ≠0 throughout cell 7 (all analyzed shapes);
P(δ>0)==M19/M20 0.8093 on s0; P1 rounded edges match m18.txt
s0 row; `loo.txt` 764 rows + top-10 shapes/shares; removed
counts + bands (M19 values); self Jaccard == 1.0.

## Run protocol

1. Input shas + `m33.txt`/`m34-census.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Full 764 pass + FULL TSV guard + s9 row guard + M33
   cluster-set guard + `m33.txt` transcription guard (or
   stop).
3. Task 1: pooled + per-block per-site tables + block dmin
   rows + hists + mixed-comp membership (dmin/status/comp
   guards or stop).
4. Task 2: per-block dstats + gapsign + s0-anchored joins +
   missing-contrast rows.
5. Determinism re-run receipt (Task 1 on s0+9, canonical
   sha).
6. PNG sub-block map (320x224, <5 MB total) to work dir;
   evidence copy ONLY if H1 meets AND the far block's
   majority status holds ≥8 far sites (the split visible
   in the pre-registered far/near block map) — else
   absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 06:21 EDT, stop by 10:21).
