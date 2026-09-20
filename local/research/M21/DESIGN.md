# M21 — Design (recorded before running)

Goal: static-site residual mechanism (M19 gap 2): maps per shape +
EFB-copy diffing on cell 6 (v0==full≠mid: 2368 raw B s0 / 1476 m15;
Y subset = P4's 463/439 px; U/V majority 1905 B s0). Tables, no
verdicts. Fully offline: no lease of any kind, no boots, no harness
runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m19/m19.txt` (receipt values to
re-verify, not to trust). Work dir: `/Volumes/Extreme SSD/m21/`
(new). Evidence: `local/research/M21/` (committed with
`git add -f`, prefix `[M21]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M19/REPORT.md` (all of it: cell 6
= 2368/1476 raw B, Y 463/439, negrate 0.51/0.51, s0-Y bands
15/186/262, carrier row ≤0.0842, 8-cell partition + dout + band/
carrier machinery) plus `local/research/M20/REPORT.md` (all of it:
δ-hist machinery, BFS edge distance + (dr,dc) cross, M18-P1 gradient
deciles, 701-cut precedent).

## Estimator (`m21.py`, `control.py`)

Shared core (M19 `m19.py` / M20 `m20.py` verbatim where reused):
YUYV 640x448 decode (`split_planes`, `flat_to_planes`), `synth_w_bytes`
at w=0.5, `xdiff`, `mag_hist`/`y_hist`, `bands_of` (thirds via
`np.array_split(arange(448),3)`), `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `bfs_edge` (exact BFS + source
tracking), `p1_gradient` (M18 P1 block verbatim). Byte offset o ->
row o//1280; Y bytes at o%4==0/2.

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid. n = R_0 (want 22815 s0 / 13418 m15).
- Cell 6 (M19 id 6 verbatim): residual + static site (v0==full).
  On static sites synth==v0==full, so residual ⟺ mid≠v0.
- ε = mid−v0 (= mid−full; identity guarded byte-for-byte) on
  cell-6 bytes only — the δ-analog. ε≠0 throughout (guard).
  P(ε>0) is M19's cell-6 byte negrate (0.5110/0.5136) — same
  quantity, cross-checked, not re-derived.
- Plane of a byte: Y (o%4==0/2), U (o%4==1), V (o%4==3).
- Static-site MAP of shape s: R_s = cell-6 boolean mask (N bytes).

### Task 1 — static-site maps (s0 + m15 + 764-shape coarse pass)

Cell-6 membership recomputed from the dumps; counts must match M19's
2368/1476 raw + 463/439 Y EXACTLY or table the mismatch and stop (no
further tasks run).

1. Per-shape maps: R_s for all 764 M16 triplets (+ m15 as an extra
   row): raw counts + Y/U/V split; distribution min/med/mean/max.
   Overlap: Jaccard(R_t,R_s0) over all 764 (t=0 reads 1.0 by
   construction — tabled, distribution also quoted over t≠0),
   Jaccard(R_s0,R_m15), Jaccard(R_t,R_m15) distribution;
   per-site persistence occ[o] = #{t : o ∈ R_t} over 764 shapes:
   histogram of occ (0 / 1 / 2–3 / 4–7 / 8+ bins + exact universal
   count occ=764), occ restricted to R_s0 sites (do s0's sites
   recur?) and to R_m15 sites.
2. Value table: ε signed per-value counts (full observed range) +
   |ε| hist (bins [1,2–3,4–7,8–15,16+], max, mean, P(|ε|==1)) +
   per-plane split (Y / U / V rows: n, mean ε, mean |ε|) +
   P(ε>0) vs M19 negrates. Compared against M20's interior-δ
   shape (86%/84% ±1, 98%/94% luma) at table level only.
3. Position table:
   - Band (M19 thirds verbatim): static-Y + raw counts per band,
     s0 + m15 (guards: s0-Y [15,186,262], s0-raw [803,840,725],
     m15-Y [40,217,182]).
   - Edge distance: M20 `bfs_edge` verbatim BUT the source set is
     flipped to MOVED sites (v0≠full) of the same plane —
     adaptation recorded here because static sites read d≡0 to
     static by construction (guarded analytically, not run).
     Table: d over cell-6 sites per plane (bins {1,2,3,4,5+},
     dmin/dmax — d≥1 by construction), (dr,dc) cross verbatim,
     plus one background row per frame/plane (mean d over ALL
     static sites, same BFS output).
   - Gradient decile: M18 P1 verbatim; rounded edges guarded vs
     m18.txt (`0 1 2 2 4 6 8 12 18 29 176` s0 /
     `0 0 1 2 4 6 9 13 19 30 181` m15). Primary join: static-Y
     bytes (n, mean ε, sd, mean |ε| per decile); U/V secondary
     join via co-located Y decile (r,2c) (M20 verbatim).

### Task 2 — EFB-copy diffing (is mid noisier on static regions?)

1. Cross-shape static-region noise (the non-tautological form of
   "mid-vs-v0 inside vs outside the residual set"): with the s0
   residual mask R_s0 fixed, for each shape t (764 + m15 row):
   S_t = static sites (v0==full) on t; inside = S_t ∩ R_s0,
   outside = S_t ∖ R_s0; in_rate = |R_t ∩ R_s0|/|inside|,
   out_rate = (|R_t|−|R_t ∩ R_s0|)/|outside|. Table: pooled
   in/out rates + ratio over t≠0 (bar H4), per-shape in_rate
   distribution, self-frame row t=0 (1.0/0.0 by construction —
   arithmetic guard), same block with the R_m15 mask. Within
   one frame the inside/outside rates are 1.0/0.0 by
   construction — tabled once as the guard, never as a result.
2. U/V joint at chroma pixels: population = chroma px (r,c) in
   the 320x448 grid with BOTH U and V bytes static (v0==full).
   2×2 joint (U_res × V_res; residual ⟺ mid≠v0 on static) +
   P(V|U), P(V|¬U), expected both-count under independence,
   ratio actual/expected. Both frames.
3. Carrier cut: top-10 carriers from `loo.txt` (guarded vs M16's
   shapes + shares; removed masks = M19 Test-C verbatim res0 &
   ~ress on Y; guards: removed counts [4888,1208,649,448,248,
   244,191,174,190,202], bands per m19.txt, static-Y-in-mask
   [12,5,2,39,6,19,12,10,17,8]). Static bytes inside each mask:
   Y exact + U/V via co-located Y (r,2c) (M20 co-location
   verbatim; new measurement, no guard). HUD-region split:
   HUD region = UNION of the removed-Y masks of the six
   all-bottom-band top-10 carriers {368,369,366,370,376,748}
   (M18's bottom-HUD draws; definition fixed here before
   running). Table static-Y + raw inside/outside counts, s0 +
   m15 (m15 joined against the same s0-derived masks, labeled).

Static-site rule synths (explained-vs-standing rule table, s0 +
m15; fixed rules only): on static sites predict v0+1 / v0−1
(clipped), elsewhere Model 0; table cell-6 hits + full-frame
R/explained/e (reference: predict-v0 == Model 0, 0 explained).

### Task 3 — controls + determinism (M18–M20 precedent)

`control.py` (imports `m21` cell/ε core; expectations analytic):

- C-S1: synthetic truth mid' on s0: N=500 currently-triple-equal
  static sites (first 500 in offset order with 1≤v0≤254, so ±1
  never clips), injected mid'=v0+1 on even / v0−1 on odd
  (known values). Recompute cell 6 from (v0,mid',full): the
  recomputed set must equal R_s0 ∪ injected exactly (count +
  values + map), original members' ε unchanged.
- C-S2: same injection with ±2 values (known-value variant):
  exact recovery of count + values + map.

Determinism: re-run Task 1 on s0 (cell-6 recompute + ε hist +
bands); canonical-text sha + counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
top-10 carrier triplets. Model-0 recompute: R_0/fnv must match
M17–M20 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_MAP (map determinism): median Jaccard(R_t, R_s0) over t≠0
  ≥ 0.50 (same sites recurring vs every shape its own scatter).
- H2_VAL (±1 dominance, M20-H1 analog): P(|ε|==1) over s0
  static bytes ≥ 0.75.
- H3_SIGN (offset side, M20-H2 analog): majority ε-sign share
  ≥ 0.75 on s0.
- H4_EFB (cross-shape noise concentration): pooled in/out rate
  ratio (R_s0 mask over t≠0 static sites) ≥ 2.
- H5_CONC (spatial concentration, M19-H5 analog): some band
  holds ≥75% of s0 static Y, or some top-10 carrier mask holds
  ≥50%, or the HUD region holds ≥75%.
- N (standing remainder + best static-site rule): cell 6 after
  the best fixed rule's hits + remaining split — the deliverable
  whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-6
counts 2368/1476 raw + 463/439 Y exact (else stop before Task
1.1); ε==mid−full identity + ε≠0; P(ε>0)==M19 negrates;
s0-Y/s0-raw/m15-Y band rows; `loo.txt` 764 rows + top-10 shapes/
shares; removed counts + bands + static-Y-in-mask rows; P1 edges;
self Jaccard == 1.0.

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-6 recompute + count guard (2368/1476 + 463/439 or stop).
3. Task 1: 764-shape map pass (counts + Jaccards + persistence);
   ε hists + plane split; band/edge/P1 joins.
4. Task 2: cross-shape EFB rates (both masks); U/V joint;
   carrier cut + HUD split; rule synths.
5. Determinism re-run receipt (Task 1 on s0, canonical sha).
6. PNG static-site map (320x224, <5 MB total) to work dir;
   evidence copy ONLY if the map discriminates spatially
   (ε-sign or site structure separates by a tabled split —
   band/HUD/carrier/sign); else absence reasoned.
7. `control.py` receipts.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 01:45 EDT, stop by 05:45).
