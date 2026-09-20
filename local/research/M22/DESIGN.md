# M22 — Design (recorded before running)

Goal: interior far-tail mechanism (M20 gap 1): locate + isolate the
|δ|≥8 bytes on cell 7 (strict interior: 102 B s0 / 134 B m15, max
47/48, all 102 s0 outside the 701 mask). Distinct population
(region? plane? carrier? shape-persistent? different δ regime?) or
the smooth tail of the ±1 mass? Tables, no verdicts. Fully offline:
no lease of any kind, no boots, no harness runs, no fork changes,
no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m20/m20.txt` (cell-7 δ tables to
reproduce: 2475/2539 counts, 102/134 tail counts — match exactly or
table the mismatch and stop). Work dir: `/Volumes/Extreme SSD/m22/`
(new). Evidence: `local/research/M22/` (committed with
`git add -f`, prefix `[M22]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M20/REPORT.md` (all of it: cell 7
= 2475 B s0 / 2539 B m15, |δ| hist [2127,127,119,28,74] s0 /
[2121,189,95,50,84] m15, max 47/48, 97.8%/94.2% Y, 78.6%/87.9% at
d≤2, 62.8%/65.0% in P1 dec-9, ρ [0.3,0.4) peak 42.3%/35.4%, 701-cut
mean −0.967 inside vs +1.489 outside with all 102 s0 tail outside)
plus `local/research/M21/REPORT.md` Task-1.1 map machinery (per-shape
persistence + Jaccard precedent: 518/764 byte-identical maps, median
Jaccard 1.0000, occ-hist bins) for the cross-shape question below.

## Estimator (`m22.py`, `control.py`)

Shared core (M20 `m20.py` / M21 `m21.py` verbatim where reused):
YUYV 640x448 decode (`split_planes`, `flat_to_planes`),
`synth_w_bytes` at w=0.5, `xdiff`, `mag_hist`/`y_hist`, `bands_of`
(thirds via `np.array_split(arange(448),3)`), `fnv1a`, `parse_loo`,
PNG writer, `plane_of_byte`, `plane_coords`, `bfs_edge` (exact BFS +
source tracking, source = STATIC sites — M20 verbatim, same edges,
same BFS), `p1_gradient` (M18 P1 block verbatim). Byte offset o ->
row o//1280; Y bytes at o%4==0/2.

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard).
- Bulk = cell-7 bytes with |δ|<8 (want 2373 s0 / 2405 m15).
  Tail = cell-7 bytes with |δ|≥8 (want 102 s0 / 134 m15; s0
  sub-bins 28 in 8–15 + 74 in 16+, m15 50 + 84; max 47/48).
- Plane of a byte: Y (o%4==0/2), U (o%4==1), V (o%4==3).
- Tail MAP of shape s: T_s = tail boolean mask (N bytes).

### Task 1 — locate (tail vs bulk side by side, s0 + m15)

Cell-7 membership + tail membership recomputed from the dumps;
counts must match M20's 2475/2539 cell + 102/134 tail EXACTLY or
table the mismatch and stop (no further tasks run).

1. Position (M20 machinery verbatim — same static-source BFS,
   same P1 edges):
   - Band (M19 thirds verbatim): tail-Y + tail-raw + bulk-Y +
     bulk-raw counts per band, s0 + m15 (bulk guards: s0-Y bulk
     bands = M19/M20 interior-Y bands minus tail-Y bands —
     tabled, not pre-guarded; M20 s0 interior-Y bands are not
     separately quoted, so no numeric guard here).
   - Edge distance: M20 `bfs_edge` verbatim (source = static
     sites of the same plane). Table: d over tail sites per
     plane (bins {1,2,3,4,5+}, dmin/dmax — d≥1 by construction)
     with the bulk side by side in the same bins, plus the
     (dr,dc) cross verbatim for tail-Y and bulk-Y.
   - Gradient decile: M18 P1 verbatim; rounded edges guarded vs
     m18.txt (`0 1 2 2 4 6 8 12 18 29 176` s0 /
     `0 0 1 2 4 6 9 13 19 30 181` m15). Primary join: tail-Y
     bytes (n, mean δ, sd, mean |δ| per decile) + bulk-Y
     side by side (same deciles). U/V secondary join via
     co-located Y decile (r,2c) (M20 verbatim): tail n-by-dec
     + bulk n-by-dec.
2. Plane: tail Y/U/V rows (n, share, |δ| hist, signed range,
   mean δ, mean |δ|) + bulk Y/U/V rows side by side (bulk
   guards: s0 Y 2421−tailY / U 27−tailU / V 27−tailV with M20
   means reproduced net of the tail — tabled, arithmetic
   cross-checked).
3. Region: connected-component clustering of tail sites per
   plane (Y on the 640x448 grid, U/V on 320x448): 4-connectivity
   (von Neumann) and 8-connectivity (Moore) via union-find.
   Table per frame × plane × connectivity: component count +
   size distribution (n=1 singles / 2 / 3–4 / 5–8 / 9+; largest
   component size + share; full sorted size list in the
   receipt). One region or scattered singles — tabled.

### Task 2 — isolate (distinct population or smooth tail?)

1. Carrier cut: top-10 carriers from `loo.txt` (guarded vs M16's
   shapes + shares; removed masks = M19 Test-C verbatim res0 &
   ~res701-style res0 & ~ress on Y; guards: removed counts
   [4888,1208,649,448,248,244,191,174,190,202], bands per
   m19.txt, 701 interior-in-mask 367, tail-outside-701 102 —
   M20 values reproduced). Tail bytes inside each mask: Y exact
   + U/V via co-located Y (r,2c) (M20 co-location verbatim).
   Table per carrier: tail-Y-in + tail-U-in + tail-V-in +
   tail-Y share. Plus inside/outside-701 split for the tail
   (n, mean δ, mean |δ|, signed range) with the bulk split
   side by side. Any carrier CONCENTRATES the tail — tabled.
2. Cross-shape persistence (M21 Task-1.1 machinery verbatim,
   s0-anchored like M21): T_s for all 764 M16 triplets (+ m15
   as an extra row): tail-count distribution min/med/mean/max;
   Jaccard(T_t,T_s0) over all 764 (t=0 reads 1.0 by
   construction — tabled, distribution also quoted over t≠0),
   Jaccard(T_s0,T_m15), Jaccard(T_t,T_m15) distribution;
   per-site persistence occ[o] = #{t : o ∈ T_t} over 764
   shapes: histogram of occ (bins 0 / 1 / 2–3 / 4–7 / 8–15 /
   16–63 / 64–763 / 764, M21 verbatim) + occ restricted to T_s0
   sites (do s0's tail sites recur?) and to T_m15 sites. Full
   764-row table (shape, R_s, R_loo, tail, Y/U/V, jacc_s0,
   jacc_m15) in the receipt. Same sites recurring
   (deterministic) or per-shape scatter — tabled.
3. δ-shape join: tail |δ| values vs (v0−full) gap at those
   sites: gap=|v0−full| distribution on the tail (min/med/mean/
   max + coarse hist) with the bulk side by side; ρ = δ/|gap|
   on the tail (max|ρ| with the <0.5 guard, mean|ρ|, hist bins
   of width 0.1 over (−0.5,0.5], M20 verbatim) with the bulk
   ρ hist side by side (bulk guards: M20 s0
   [19,107,168,94,84,254,237,347,1048,117] / m15
   [28,77,200,111,87,287,284,436,899,130] reproduced net of
   the tail — tabled, arithmetic cross-checked); sign joint on
   the tail (d>0/o>0 etc + P(o>0)) with bulk P(o>0) 0.8093/
   0.8019 side by side. Same [0.3,0.4) peak as the bulk, or a
   different regime — tabled.

### Task 3 — controls + determinism (M18–M21 precedent)

`control.py` (imports `m22` cell/tail core; expectations analytic;
feasibility: interior ⇒ |δ| < |gap|/2, so a |δ|≥8 injection needs
gap ≥ 17 minimum; both controls select bulk sites with large
enough gaps that mid'=blend+δ stays strictly inside (lo,hi) —
verified per site, edges counted):

- C-T1: synthetic truth mid' on s0: N=60 currently-interior-BULK
  sites with gap≥50 (first 60 in offset order), injected
  mid'=blend+20 on even / blend−20 on odd (known tail values,
  |δ|=20≥8). Recompute cell 7 + tail from (v0,mid',full): the
  recomputed tail set must equal T_s0 ∪ injected exactly
  (count + values + map), original tail members' δ unchanged.
- C-T2: same pool shape with varied tail magnitudes: N=60
  bulk sites with gap≥32 (first 60 in offset order), injected
  values cycled [+8,−12,+15] (known values spanning the
  8–15 sub-bin and both signs). Exact recovery of count +
  values + map; original tail members' δ unchanged.

Determinism: re-run Task 1 on s0 (cell-7 + tail recompute +
hists + bands); canonical-text sha + counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
top-10 carrier triplets. Model-0 recompute: R_0/fnv must match
M17–M21 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_POS (tail lives elsewhere): |tail dec-9 share − bulk dec-9
  share| ≥ 0.25 on s0-Y, or |tail d≤2 share − bulk d≤2 share|
  ≥ 0.25 on s0-Y (either leg meets).
- H2_PLANE (chroma enrichment): tail Y share ≤ 0.75 on s0
  (bulk 0.978).
- H3_REGION (single region): largest 8-connected component of
  s0 tail-Y sites holds ≥ 0.50 of s0 tail-Y.
- H4_CARRIER (carrier concentration, M19-H5 analog): some
  top-10 removed mask holds ≥ 0.50 of s0 tail-Y.
- H5_PERSIST (deterministic sites, M21-H1 analog): median
  Jaccard(T_t, T_s0) over t≠0 ≥ 0.50.
- H6_RHO (different δ regime): tail ρ[0.3,0.4) share differs
  from bulk ρ[0.3,0.4) share by ≥ 0.25 on s0.
- N (standing remainder + best tail rule): cell 7 after the
  best tail rule's hits + remaining split — the deliverable
  whatever the bars read (brief names no tail-value rule; if
  no locate/isolate finding yields a non-oracle rule, N reads
  0 explained with the tail standing 102/134 inside cell 7).

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with sub-bins
28+74 / 50+84 and max 47/48 (else stop before Task 1.1); δ≠0
throughout cell 7; P(δ>0)==M19/M20 0.8093/0.8019; P1 rounded
edges match m18.txt; `loo.txt` 764 rows + top-10 shapes/shares;
removed counts + bands; 701 interior-in-mask 367 +
tail-outside-701 102; ρ max|ρ|<0.5; self Jaccard == 1.0.

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (2475/2539 + 102/134
   or stop).
3. Task 1: plane split (tail vs bulk); band/edge/P1 joins
   (tail vs bulk side by side); region components (4/8-conn).
4. Task 2: carrier cut (10 masks + 701 split); 764-shape tail
   pass (counts + Jaccards + persistence); δ-shape join (gap +
   ρ + sign joint, tail vs bulk).
5. Determinism re-run receipt (Task 1 on s0, canonical sha).
6. PNG tail map (320x224, <5 MB total) to work dir; evidence
   copy ONLY if the map discriminates spatially (tail sites
   separate by a tabled split — region/carrier/decile/sign);
   else absence reasoned.
7. `control.py` receipts.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 02:05 EDT, stop by 06:05).
