# M33 — Design (recorded before running)

Goal: shape-9 full-set attribution (M29 gap 2): shape 9's tail
recomputes to 117 B at Jaccard 0.7520 vs s0 (M29: priv 23 —
1 in-column c321 r266 + 22 outside-col r226–305 cluster —
miss 8, shared 94). The c321 delta row is attributed (M29);
the other 30 sites are located, not attributed. Per-byte
cluster tables (M27 Task-1/Task-2 method: cross-frame |δ| +
cell/bulk status on the other shape, signed gaps both shapes,
s0-anchored band/decile/streak/carrier joins, Manhattan
displacement, 8-conn components) for all 22 outside-col
privates + all 8 missings. Tables, no verdicts. Fully
offline: no lease of any kind, no boots, no harness runs, no
fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`; only s0 + s9 + m15 +
top-10 carriers are loaded — no full 764 pass),
`/Volumes/Extreme SSD/m15/` (triplet, baseline guard only —
no m15 analysis), `/Volumes/Extreme SSD/m29/m29.txt`
(shape-9 full-set counts to reproduce: tail 117, priv 23,
miss 8, shared 94, J 0.7520, outside-col 22/8 + (row,col)
lists — match exactly or table the mismatch and stop). Work
dir: `/Volumes/Extreme SSD/m33/` (new). Evidence:
`local/research/M33/` (committed with `git add -f`, prefix
`[M33]`, trailer `Orchestrated-By: Muse Code`; NEVER `git
push` in ssx3).

Headers read first: `local/research/M29/REPORT.md` (all of it:
6 recomputed partial cells, 9 delta-row sites, 7/9 far bulk +
2/9 non-cell, 8/9 dec-9, extra medians 8–9 vs missing 18.0;
s9 full sets priv 23 / miss 8 / shared 94 with the 22+8
outside-col (row,col) lists pinned below) plus
`local/research/M27/REPORT.md` (Task-1 per-site table
precedent: offset/plane/row/col, cross-frame |δ|, signed gaps
both frames; full-swap reference: priv/miss 100% band-0, miss
100% dec-9, priv ~21% dec-9, all non-cell on the other frame;
displacement + 8-conn component + s0-anchored join machinery
reused verbatim).

## Estimator (`m33.py`, `control.py`)

Shared core (M27 `m27.py` / M29 `m29.py` verbatim where
reused): `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|δ|≥8 tail), `plane_of_byte`,
`plane_coords`, `parse_loo`, `jaccard`, `off_of`,
`y_col_rows`, `bands_of`/`ROW_BAND` thirds, `p1_gradient`
(M18 P1 block verbatim), `attrib_lines` (per-site cross-value
rows), `posjoin_lines` (s0-anchored band/decile/streak/
carrier + 701 split), `displace_lines` (nearest-shared-site
Manhattan dmin + hist), `comp_lines` (8-conn comps on Y +
U/V counts), `connected_components` (union-find 8-conn),
`flat_to_planes`, `split_planes`, `yuv_to_rgb`, PNG writer.
Byte offset o -> row o//1280; Y bytes at o%4==0/2.

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
- Full sets (shape 9 vs s0): P_9 = T_9 − T_s0 (want 23), M_9
  = T_s0 − T_9 (want 8), S_9 = T_9 ∩ T_s0 (want 94);
  23+94=117 ✓, 8+94=102 ✓, 94/125=0.7520 ✓.
- In-column private (pinned, M29): the single c321 r266 Y
  site (offset 341122), attributed in M29 — recomputed as a
  guard (in-c321 priv rows == [266]) but NOT re-attributed.
- Cluster privates C_priv = P_9 sites with Y-col ≠ 321
  (want 22, all Y): [(226,351), (232,327), (233,327),
  (234,337), (235,337), (239,336), (239,339), (240,318),
  (241,318), (243,318), (244,316), (245,315), (245,316),
  (246,314), (248,312), (252,310), (269,313), (270,313),
  (274,322), (289,315), (290,315), (305,332)] (M29 receipt
  order; guarded exact as a SET).
- Cluster missings C_miss = M_9 (want 8, all outside c321,
  all Y): [(266,315), (269,314), (273,315), (288,314),
  (289,314), (296,311), (299,312), (301,312)] (guarded exact
  as a SET; asserted disjoint from c321).
- Near-miss (pinned, M27 verbatim): a cluster site whose
  other-frame status is bulk with |δ_other| ∈ {6,7}. Far:
  bulk with |δ_other| ≤ 5. Non-cell: not cell-7 on the other
  frame.
- Position joins are s0-ANCHORED (pinned, M27 verbatim):
  geometry bands, P1 deciles on s0 mid-Y (edges guarded vs
  m18 constants), named streak columns, M22-verbatim top-10
  carrier masks + 701 split.
- Displacement (pinned, M27 verbatim): nearest-shared-site
  Manhattan distance, same plane, plane-native coords,
  brute-force exact; hist bins {1,2,3,4,5+} (0 impossible by
  construction — guarded).
- Components (pinned, M27 verbatim): 8-conn union-find on
  Y; U/V tabled iff nonempty. Cluster occupancy: per-s9-comp
  count of C_priv sites; per-union-comp (T_9 ∪ T_s0) counts
  of C_priv + C_miss sites.

### Task 1 — cluster per-site tables (what are the 30 sites?)

Shape-9 full sets recomputed from the dumps (tail 117 + priv
23 + miss 8 + shared 94 + J 0.7520 + outside-col 22/8 + both
(row,col) SETS must match M29 exactly — §Guards — or table
the mismatch and stop; no further tasks run).

1. Per-site rows for all 22 outside-col privates (M27
   `attrib_lines` verbatim: offset, plane, row, col, |δ_9|,
   s0 status + |δ_s0|, signed gaps both), offset-ordered, in
   the receipt; full-priv (23) rows tabled alongside (the
   22 + the guarded in-column r266 site, labeled).
2. Per-site rows for all 8 missings (mirror: |δ_s0|, shape-9
   status + |δ_9|, signed gaps both), offset-ordered.
3. Near-miss check: H1/H2-style shares per set — cluster
   priv (22), full priv (23), cluster/full miss (8) —
   near (bulk |δ|∈{6,7}) vs far (bulk ≤5) vs non-cell;
   tabled against the two pinned references (full swaps
   100% non-cell; M29 partials 7/9 bulk).

### Task 2 — cluster joins (one cluster or scatter?)

1. Position joins (M27 `posjoin_lines` verbatim,
   s0-anchored): cluster sets (C_priv 22 / C_miss 8 / S_9
   94) by band / decile / streak column / carrier mask +
   701 split, plus the full-set join (P_9 23 / M_9 8 / S_9
   94) alongside — tabled.
2. Displacement: `displace_lines` verbatim per set
   (cluster priv, cluster miss, full priv alongside):
   per-site dmin rows + hist {1,2,3,4,5+} + d1 share —
   tabled against the full-swap reference (privates dmin
   5–19, d1 share 0).
3. Component view: `comp_lines` verbatim (s0 vs s9: count,
   sizes, sizelist, comp5+ bboxes) + per-s9-comp C_priv
   occupancy + union-mask (T_9 ∪ T_s0) comps with per-comp
   C_priv/C_miss counts — one comp or several? — tabled.

### Task 3 — controls + determinism (M18–M32 precedent)

`control.py` (mid-level synthetic truth, M27-style —
feasible because cluster flips keep cell-7 membership):

- C-CLUS (known cluster sets, mimics shape 9's 22+8): s0
  mid' with the FIRST 22 offset-order interior-BULK gap≥17
  Y sites flipped to tail (mid'=blend+8 even / blend−8 odd,
  |δ|=8; per-site strict-interior check) AND the FIRST 8
  offset-order s0-tail Y sites flipped to bulk
  (mid'=blend+1, fallback blend−1 per site if +1 is not
  strictly inside — tabled). Known: priv = the 22, miss =
  the 8, tail' = 102−8+22 = 116, J = 94/124 = 0.7581
  (`f"{J:.4f}"`), per-site values exact, all other tail
  members' δ unchanged, cell-7 mask fixed.
- Pass = priv-set-exact + miss-set-exact + J-exact +
  values-exact + rest-unchanged.

Determinism: re-run Task 1 (full + cluster per-site rows +
both joins) on s0+9; canonical text sha byte-identical
pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s9 + m15
triplets + top-10 carrier triplets + `m29.txt` sha. Model-0
recompute: R_0/fnv must match M17–M32 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
s0+9 (want both equal; mismatch = stop and table).
`loo.txt` 764 rows + top-10 shapes/shares match M16. P1
edges + carrier removed counts/bands (M19 values) guarded.

## Falsification bars (recorded before running; tables, no verdicts)

Cluster denominator = 22 C_priv sites unless named
(C_miss = 8; pooled cluster = 30).

- H1_CLUSNEAR (cluster privates are near-misses): share of
  C_priv sites with s0-bulk status and |δ_s0| ∈ {6,7} is
  ≥ 0.50.
- H2_CLUSSET (cluster privates are set changes, not δ
  changes): share of C_priv sites with s0 non-cell status
  is ≥ 0.50.
- H3_DISPLACE (cluster privates are 1-px displacements):
  share of C_priv sites within Manhattan distance 1 (same
  plane) of a shared tail site is ≥ 0.50.
- H4_LOCALIZE (cluster localizes): |C_priv band-1 share −
  shared band-1 share| ≥ 0.25, or |C_priv dec-9 share −
  shared dec-9 share| ≥ 0.25 (either leg meets;
  s0-anchored joins; band-1 = the cluster's mid-frame band
  r150–299, the M27-H4 analog re-anchored from band-0).
- H5_ONECOMP (cluster forms one component): the largest
  s9-tail 8-conn component's C_priv count / 22 is ≥ 0.50.
- H6_MISSSET (cluster missings are set changes): share of
  C_miss sites with shape-9 non-cell status is ≥ 0.50.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0+9; cell-7 counts s0 2475 exact +
tail counts s0 102 exact with sub-bins 28+74 and max 47;
s9 tail 117 + J 0.7520 + full sets priv 23 / miss 8 /
shared 94 + outside-col counts 22/8 + both (row,col) SETS
exact vs M29; in-c321 priv rows == [266]; s9 c321 rows ==
s0 c321 rows + [266]; δ≠0 throughout cell 7 (s0+9);
P(δ>0)==M19/M20 0.8093 on s0; P1 rounded edges match m18.txt
s0 row; `loo.txt` 764 rows + top-10 shapes/shares; removed
counts + bands (M19 values); self Jaccard == 1.0.

## Run protocol

1. Input shas + `m29.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute on s0 + s9 + count/J/set/list
   guard (or stop).
3. Task 1: full + cluster per-site tables + near-miss
   shares per set.
4. Task 2: full + cluster position joins; displacement
   per-site rows + hists; 8-conn components s0 vs s9 +
   per-comp cluster occupancy + union-mask comps.
5. Determinism re-run receipt (Task 1 on s0+9, canonical
   sha).
6. PNG cluster map (320x224, <5 MB total) to work dir;
   evidence copy ONLY if H4 meets on either leg AND the
   winning leg's majority level holds ≥8 C_priv sites
   (localization visible in the pre-registered band/decile
   split; M27 rule verbatim) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 03:55 EDT, stop by 07:55).
