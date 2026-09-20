# M27 — Design (recorded before running)

Goal: shape-733 tail divergence attribution (M22 gap 2, carried M23
gap 4 → M26 gap 11): shape 733's tail map reads Jaccard 0.6694 vs
s0 on 100 B while 727/764 shapes read byte-identical (731
next-lowest at 0.6833, 100 B). Per-byte attribution of 733's
private sites (T_733 − T_s0) and missing sites (T_s0 − T_733):
near-misses (|δ| just below 8 on the other frame?) vs displaced
versions of shared sites (same component, shifted rows?) vs a
genuinely different set (different band/decile/carrier)? Tables,
no verdicts. Fully offline: no lease of any kind, no boots, no
harness runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m22/m22.txt` (733's tail membership +
Jaccard to reproduce: 100 B, J 0.6694 — match exactly or table
the mismatch and stop). Work dir: `/Volumes/Extreme SSD/m27/`
(new). Evidence: `local/research/M27/` (committed with
`git add -f`, prefix `[M27]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M22/REPORT.md` (all of it: 102
s0 tail, 100% luma, top-band + dec-9 heavy, 25 8-conn comps,
streak columns c257/277/296/301/321/340–343, max 1 B in any
carrier mask, 727/764 maps byte-identical to s0, J(T_s0,T_m15)
0.4132, gaps ≥17 mean ~54, ρ peak [0.4,0.5), sign-gap agreement
90.2%) plus `local/research/M23/REPORT.md` (K45+ transfer table:
733 scores 14/100 like s0 — values transfer, the SET diverges;
733 row: 100 B, 14/0.1400 exact, near 31, J 0.6694).

## Estimator (`m27.py`, `control.py`)

Shared core (M22 `m22.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `bands_of` (thirds via
`np.array_split(arange(448),3)`), `fnv1a`, `parse_loo`, PNG
writer, `plane_of_byte`, `plane_coords`, `p1_gradient` (M18 P1
block verbatim), `connected_components` (union-find 4/8-conn),
`jaccard`. Byte offset o -> row o//1280; Y bytes at o%4==0/2.
No BFS edge machinery (no edge-distance task here).

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
- Private sites P_733 = T_733 − T_s0; missing sites M_733 =
  T_s0 − T_733; shared sites S = T_733 ∩ T_s0. Same with 731
  for the cross-check (P_731, M_731, S_731).
- At-a-site cross values: for a private site o (tail on 733),
  s0 status = tail (o ∈ T_s0 — impossible by construction,
  guarded) / bulk (o ∈ cell7_s0, |δ_s0|<8) / non-cell (o ∉
  cell7_s0; δ_s0 undefined — tabled as `n/a`). δ_733(o) always
  defined with |δ|≥8. Mirror for missing sites (733 status at
  s0-tail sites). Signed gaps g_733(o) = v0_733(o)−full_733(o),
  g_s0(o) = v0_s0(o)−full_s0(o) always defined (int16).
- Near-miss (pinned): a private site whose other-frame status
  is bulk with |δ_other| ∈ {6,7} (within 2 of the |δ|≥8
  boundary). Far: bulk with |δ_other| ≤ 5. Non-cell: not
  cell-7 on the other frame (neither near nor far — its own
  row).
- Position joins are s0-ANCHORED (pinned): band = geometry
  (same for all frames); gradient decile = P1 on s0 mid-Y
  (M22-verbatim call, edges guarded vs m18.txt s0 row);
  streak column = Y-column membership in the named set
  {257,277,296,301,321,340,341,342,343} + other (U/V sites, if
  any, join via co-located Y (r,2c) M22-verbatim and are
  tabled on their own rows); carrier mask = inside/outside
  each M22-verbatim top-10 removed mask (res0 & ~ress on Y;
  U/V via co-located Y) + the 701 split. One common
  coordinate so private/missing/shared compare directly.

### Task 1 — private/missing site tables (what differs?)

733's tail membership recomputed from the dumps (100 B +
Jaccard 0.6694 vs s0 must match M22 exactly — counts exact +
`f"{J:.4f}" == "0.6694"` — or table the mismatch and stop; no
further tasks run).

1. Private-site table: per private site (offset, plane, row,
   col): |δ_733|, s0 status (bulk/non-cell) + |δ_s0| or `n/a`
   (near-miss? far?), gap_733 vs gap_s0 (signed + abs). Full
   per-site rows in the receipt (offset order); summary:
   near/far/non-cell counts + shares, |δ_other| hist on the
   bulk-status sites, signed-gap equality share (gap_733 ==
   gap_s0 exactly?).
2. Missing-site table: mirror (sites tail on s0, not on 733):
   |δ_s0|, 733 status (bulk/non-cell) + |δ_733| or `n/a`,
   gap_s0 vs gap_733. Same summaries.
3. Position join: private/missing/shared sites by band /
   gradient decile (s0-anchored) / streak column / carrier
   mask (M22 machinery verbatim — §above): per-level n for
   the three sets side by side (+ shares within each set).
   Does the divergence localize — tabled.

### Task 2 — displacement check (shifted or different?)

1. Nearest-shared-site distance for each private site (same
   plane, Manhattan px on plane-native coords, brute force
   over the shared set — exact): per-site distances in the
   receipt (offset order) + distance histogram bins
   {1,2,3,4,5+} (0 impossible by construction — guarded).
   1-px displacements vs far scatters — tabled. Missing-site
   mirror (distance to nearest shared site) tabled the same
   way.
2. Component view: 733's tail components vs s0's
   (M22 `connected_components` verbatim, 8-conn on Y; U/V
   tabled iff nonempty): count, sizes (1/2/3–4/5–8/9+ bins +
   full sorted size list + comp5+ bbox rows), and the r23–33
   streak columns — per named column (n, rows, row-overlap
   with s0's rows in that column): present? shifted? absent?
3. 731 cross-check (second-lowest Jaccard 0.6833, 100 B —
   counts exact + `f"{J:.4f}" == "0.6833"` or table the
   mismatch and stop the cross-check only; Tasks 1–2.2
   already tabled stand): same private-site position table
   (band/decile/streak/carrier n for P_731/M_731/S_731) +
   set overlaps J(P_733,P_731) and J(M_733,M_731) with
   inter/union integers. Is 731's divergence the same shape
   as 733's, or a different one — tabled.

### Task 3 — controls + determinism (M18–M26 precedent)

`control.py` (imports `m27` cell/tail/core; expectations
analytic; feasibility: interior ⇒ strict inside, so
injections need per-site strict-inside verification; pools
confirmed by M22's receipts: 248 bulk gap≥17 sites for
checker injections, all 102 tail sites gap≥17 for bulk
injections):

- C-P1 (known privates): synthetic truth mid' on s0: N=20
  currently-interior-BULK sites with gap≥17 (first 20 in
  offset order), injected mid'=blend+8 on even / blend−8 on
  odd (|δ|=8, the tail boundary). Shape A = s0 orig, shape B
  = s0 mid'. Recompute cell 7 + tail on B: the recomputed
  private set P_B = T_B − T_A must equal the injected set
  exactly (count + map), M_B = ∅ exactly, J(T_B,T_A) must
  equal 102/122 = 0.8361 (`f"{J:.4f}"`) exactly, original
  tail members' δ unchanged, injected values exact.
- C-P2 (known missings): synthetic truth mid'' on s0: N=20
  currently-TAIL sites (first 20 in offset order), injected
  mid''=blend+1 (fall back to blend−1 per site if +1 is not
  strictly inside — tabled). Recompute: M_B = T_A − T_B must
  equal the injected set exactly, P_B = ∅ exactly,
  J(T_B,T_A) must equal 82/102 = 0.8039 exactly, all other
  tail members' δ unchanged.
- Pass = set-exact + J-exact + values-exact on both.

Determinism: re-run Task 1 on s0+733 (cell-7 + tail recompute
+ private/missing/shared sets + Jaccards + position joins);
canonical-text sha + counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + 733 + 731 +
m15 triplets + top-10 carrier triplets + `m22.txt` sha.
Model-0 recompute: R_0/fnv must match M17–M26 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
s0/733/731 (want all equal; mismatch = stop and table, M22
precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_NEARMISS (privates are near-misses): share of 733-private
  sites with s0-bulk status and |δ_s0| ∈ {6,7} is ≥ 0.50.
- H2_SETCHANGE (privates are set changes, not δ changes):
  share of 733-private sites with s0 non-cell status is
  ≥ 0.50.
- H3_DISPLACE (privates are 1-px displacements): share of
  733-private sites within Manhattan distance 1 (same plane)
  of a shared tail site is ≥ 0.50.
- H4_LOCALIZE (divergence localizes): |private band-0 share −
  shared band-0 share| ≥ 0.25, or |private dec-9 share −
  shared dec-9 share| ≥ 0.25 (either leg meets; s0-anchored
  joins).
- H5_STREAK (streak columns survive): at least 4 of the 6 s0
  r23–33 single-column components (c257/277/296/301/321 +
  c340, per M22's comp5+ bbox table) read present in 733
  (same column, ≥8 sites, row overlap ≥5 with s0's rows in
  that column).
- H6_731SAME (731 diverges the same way): J(P_733, P_731)
  ≥ 0.50.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0/733/731; cell-7 counts s0 2475 exact
+ tail counts s0 102 exact with sub-bins 28+74 and max 47;
733 tail 100 B + J 0.6694 exact (else stop everything); 731
tail 100 B + J 0.6833 exact (else stop the cross-check
only); δ≠0 throughout cell 7 (all analyzed shapes);
P(δ>0)==M19/M20 0.8093 on s0; P1 rounded edges match m18.txt
s0 row; `loo.txt` 764 rows + top-10 shapes/shares; removed
counts + bands (M19 values); self Jaccard == 1.0.

## Run protocol

1. Input shas + `m22.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute on s0 + 733 + count/J guard (100 B
   + 0.6694 or stop).
3. Task 1: private/missing per-site tables + summaries +
   s0-anchored position joins.
4. Task 2: displacement distances + hist (private + missing
   mirror); 8-conn components s0 vs 733 + streak-column
   presence; 731 guard + cross-check tables + set overlaps.
5. Determinism re-run receipt (Task 1 on s0+733, canonical
   sha).
6. PNG private-site map (320x224, <5 MB total) to work dir, s0
   named-column sites colored by shared/private/missing;
   evidence copy ONLY if H4 meets on either leg AND the
   winning leg's majority level holds ≥8 private sites
   (divergence visible in a specific pre-registered-split
   level) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 03:00 EDT, stop by 07:00).
