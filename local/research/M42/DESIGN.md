# M42 — Design (recorded before running)

Goal: big-|δ| unnamed sites (M35 gap 3): c332 extra (28),
c318 extra (25), c351 extra (19), c314 missings (45, 23) —
the 5 largest |δ| among the 30, 4/5 non-cell on the other
frame. Value/row listing beyond the headliners: do the big-|δ|
sites share row geometry (edges? clusters?), gap-sign sides,
or band/decile seats, or is each big site sui generis? Answer
by table: the 5 sites + full top-|δ| listing (top 10 per side:
are there near-big sites at 16–18?) + row/band/decile seats.
Tables, no verdicts. Fully offline: no lease of any kind, no
boots, no harness runs, no fork changes, no `adb`. Desktop
only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m35/
m35.txt` (the 5 sites to reproduce — match exactly or table the
mismatch and stop), `/Volumes/Extreme SSD/m34/m34-census.tsv`
(FULL TSV guard, M34–M41 precedent). Work dir: `/Volumes/Extreme
SSD/m42/` (new). Evidence: `local/research/M42/` (committed with
`git add -f`, prefix `[M42]`, trailer `Orchestrated-By: Muse
Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 3 = this brief — the 5 big sites with offsets, |δ| both
frames, statuses, signed gaps both frames, gap signs; extras
1/14/7 + missings 2/2/4; extra |δ_9| pooled min 8 med 13.0
mean 13.3182 max 28; missing |δ_s0| min 9 med 10.0 mean
16.1250 max 45; per-cell band/decile + gap-sign + |δ| tables;
c314 s0 rows [269,276,277,278,287,288,289] s9 rows
[246,276,277,278,287]) plus `local/research/M41/REPORT.md` (all
of it: the boundary census — s9 splits 1/14/7 + 2/2/4; the far
side is where these 5 live; other-frame standing convention;
row-edge convention).

## Estimator (`m42.py`, `control.py`)

Shared core (M35 `m35.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `load_triplet`,
`compute_sets` (s0+9 cell/tail/per-cell extra+missing masks),
`split_planes`, `flat_to_planes`, `yuv_to_rgb`,
`bands_of`/`ROW_BAND`, `p1_gradient` (M18 P1 block verbatim),
`attrib_lines`, `posjoin_lines`, `gapsign_lines`,
`dstats_lines`, PNG writer). Byte offset o -> row o//1280; Y
bytes at o%4==0/2. No BFS/displacement/component machinery
beyond the M35 joins (band/decile s0-anchored for the 5 seats;
streak/carrier not re-tabled — M35 reads all-other / 0-in for
all 30, cited by reference).

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
  47); s9 117 (M35-pinned).
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- Shape-9 unnamed moved set (M34/M35-pinned, k=15): [310, 311,
  312, 313, 314, 315, 316, 318, 322, 327, 332, 336, 337, 339,
  351] with per-cell n/ov + n0 + standings + deltas per the
  M35 REPORT Task-1 table (row guard covers all 15 —
  pooled 22 extras + 8 missings).
- Other-frame standing (M35 convention): a pooled site
  evaluated on the other frame O reads noncell (o not cell-7
  on O), near (bulk on O with |δ_O|∈{6,7}), or far (bulk on
  O with |δ_O|∉{6,7}).
- Brief universe (5 big-|δ| sites, M35-pinned — reproduce
  exactly or table the mismatch and stop):
  extra-side (305,332) off 391064, Y, |δ_9| 28, noncell on s0,
  gaps g_9 −62 / g_s0 −55, −− (c332 extra-only d1);
  extra-side (241,318) off 309116, Y, |δ_9| 25, bulk on s0
  with |δ_s0| 2, gaps 93/11, ++ (c318 extra-only d3 — the one
  bulk among the 5);
  extra-side (226,351) off 289982, Y, |δ_9| 19, noncell on s0,
  gaps −39/−39 (gap-equal), −− (c351 extra-only d1);
  missing-side (288,314) off 369268, Y, |δ_s0| 45, noncell on
  s9, gaps g_s0 107 / g_9 84, ++ (c314 missing);
  missing-side (289,314) off 370548, Y, |δ_s0| 23, noncell on
  s9, gaps 54/31, ++ (c314 missing).
  Noncell count want: 4/5 (the bulk one is (241,318)).
- Rank: competition rank (1 + count strictly greater) per side
  (extras by |δ_9| among 22; missings by |δ_s0| among 8) plus
  pooled rank among all 30 by own-frame |δ| (extras |δ_9|,
  missings |δ_s0|). Listing order: |δ| desc, offset asc
  (deterministic tie-break). Want (M35-derived): extras 28
  rank 1, 25 rank 2, 19 rank 3; missings 45 rank 1, 23 rank
  2; pooled order 45 > 28 > 25 > 23 > 19 (19 is 5th pooled).
- Top-10 per side: extras top 10 by |δ_9| (|δ| desc, offset
  asc) + missings top 8 (= all 8) by |δ_s0| with
  statuses/gaps/signs. Near-big band: |δ| ∈ {16,17,18}.
- Row-edge: a big site reads row-list-edge iff its row is the
  min or max of its cell's own-frame row-list (extra-side:
  s9 rows; missing-side: s0 rows); singleton row-lists table
  as edge-trivially (noted, not hidden). Pairwise row
  distance: |r_i − r_j| over the 5 rows (cluster = small
  distances tabled, no threshold verdict).
- Band/decile seats: s0-ANCHORED (M35-pinned): band = geometry
  thirds via ROW_BAND[row]; gradient decile = P1 on s0 mid-Y
  at (r,c) (edges guarded vs m18.txt s0 row). Seats tabled
  per big site + checked for compatibility with M35's
  per-cell band/dec distributions (c332 extra band 2 dec 9;
  c318 extras band 1,1,1 dec 8:1 9:2; c351 extra band 1 dec
  9; c314 missings band 1,1,1 dec 9:3 — mismatch = table and
  stop).
- Value pins: all 30 s9 sites (M35 extra/missing tables —
  offsets, |δ| both frames, statuses, signed gaps both
  frames, gap signs). Mismatch on ANY pin = stop and table.
- Gap signs: ++ / −− / −0 etc. from signed gaps (extra: g_9 ×
  g_s0; missing: g_s0 × g_9). Want among big-5: 3 ++
  ((241,318), (288,314), (289,314)) + 2 −− ((305,332),
  (226,351)).

### Task 1 — big-5 recompute (do the 5 sites reproduce?)

The 5 sites recomputed from the dumps FIRST (§Guards — pins
must match M35 exactly or table the mismatch and stop; no
further tasks run).

1. Per-site table: all 5 with pins + the 4/5-noncell count
   (which site is bulk?).
2. Rank table: each site's |δ| rank among s9's 22 extras / 8
   missings (competition rank per §Definitions) + pooled
   rank among 30 (is 45 the max? is 19 the 5th?).
3. Headliner-overlap table: which of the 5 sit in
   already-headlined cells (c314/c315 per M35 §Task 1:
   c315 mixed delta-5 + c314 delta-4) vs unheadlined cells.

### Task 2 — beyond the headliners (top-|δ| listing + seats)

1. Top-10 per side: s9 extras top 10 by |δ_9| + missings top
   8 by |δ_s0| with statuses/gaps/signs (near-big sites at
   16–18?).
2. Row geometry: each big-5 site's row vs its cell's s0/s9
   row-lists (edge? interior? singleton?) + pairwise row
   distances (cluster?).
3. Band/decile seats: each big-5 site's band + gradient
   decile (M35 §Task 2 joins recomputed for the 5: do big
   sites share seats?) + compatibility vs M35 per-cell
   distributions.

### Task 3 — controls + determinism (M18–M41 precedent)

`control.py` (imports `m42` cell/tail core; expectations
analytic):

- C-BIG (known big-site ranking, mimics big vs near-big):
  synthetic truth mid' on s0: N_BIG_PRIV=3 known big
  privates (|δ_B| 16, 14, 12, one injected site each) +
  N_DECOY_PRIV=2 known near-boundary decoys (|δ_B| 10, 8)
  at currently-BULK Y sites (largest-first greedy in numeric
  offset order: for each dv in [16,14,12,10,8], first unused
  bulk-Y site where blend+dv lands strictly inside, else
  blend−dv; sign tabled per site) AND N_BIG_MISS=3 known
  big missings (currently-TAIL Y sites with |δ_A| 47, 46,
  45 — first site at each value in offset order: (26,296),
  (28,301), (27,340)) + N_DECOY_MISS=2 known near-big
  decoys (currently-TAIL Y sites with |δ_A| 17, 16 — first
  at each value: (23,257), (23,277)), each injected
  mid'=blend+1 (fall back to blend−1 per site if +1 is not
  strictly inside — tabled; pre-measured: +1 lands inside
  at all 5). Shape A = s0 orig, shape B = s0 mid'.
  Recompute cell 7 + tail on B: P_B = T_B − T_A must equal
  the injected 5 privates exactly, M_B = T_A − T_B must
  equal the injected 5 missings exactly, J(T_B,T_A) must
  equal 97/107 exactly, per-site |δ| exact (privates
  16/14/12/10/8, missings 1 on B), gaps equal on both
  frames at every injected site (v0/full unchanged —
  tabled), other-frame statuses exact (privates bulk on A
  with original |δ| tabled; missings bulk on B), extra-side
  top-5 listing by |δ_B| must equal [16,14,12,10,8] in
  rank order 1–5 exactly, missing-side top-5 listing by
  |δ_A| must equal [47,46,45,17,16] in rank order 1–5
  exactly (competition ranks 1–5, all distinct), spanned
  Y-column cells tabled with per-cell standings + row-lists
  exact (derived from the injection), cell-7 mask fixed,
  all other tail members' δ unchanged.
- Pass = sets + Jaccard + per-site values + gaps + standings
  + both top-5 listings + ranks exact. Pool shortfall (no
  greedy assignment spans 5 privates at 16/14/12/10/8, or
  missing tail values 47/46/45/17/16 absent) = tabled RED,
  cannot-inject (M38/M39/M40/M41 precedent).

Determinism: re-run Task 1 (big-5 rows + ranks + headliner
overlap) on s0+9 with fresh loads; canonical text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s9 triplets +
`m35.txt` + `m34-census.tsv` shas (m34-census.tsv want
`83482d1f…926c8aa8` 163262 B; m35.txt want `ff29739c…49349c`
69947 B, read-only pre-measurements); triplet fold sha over
all 764x3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M41 (s0 22815 /
`6b9ffda25bd76c6f`). Mismatch = stop and table. R_s vs
`loo.txt` cross-check on ALL 764 shapes (want 764/764 equal;
mismatch = stop and table). `loo.txt` 764 rows + top-10
shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned from M35: s9's 30 pooled sites (22 extras +
8 missings); brief universe = the 5 big sites. H1/H2/H3 are
reproduce bars; H4/H5/H6/H7 are comparison bars (tabled, no
verdicts).

- H1_BIG_REPRO (big-5 reproduce): 5/5 big sites read the
  §Definitions pins exactly (offset + |δ| both frames +
  status + signed gaps both frames + gap signs + gap-equal
  on (226,351) only).
- H2_RANK (ranks reproduce): extras 28 rank 1 + 25 rank 2 +
  19 rank 3 among 22; missings 45 rank 1 + 23 rank 2 among
  8; pooled order 45 > 28 > 25 > 23 > 19 (19 is 5th pooled,
  competition ranks 1–5 with no ties above 19).
- H3_NONCELL (4/5 non-cell): exactly 4/5 big sites read
  non-cell on the other frame, namely all but (241,318)
  (which reads bulk with |δ_s0| 2).
- H4_NEARBIG (near-big sites exist below the bigs): the
  extras top-10 by |δ_9| contains ≥1 site at |δ_9| ∈
  {16,17,18}.
- H5_ROWEDGE (bigs sit at row-list edges): share of the 5
  big sites reading row-list-edge per §Definitions is
  >= 0.50 (singletons noted).
- H6_BANDSHARE (bigs share band 1): share of the 5 big
  sites in band 1 (s0-anchored geometry thirds) is >= 0.50.
- H7_GAPSPLIT (bigs split gap-sign sides): both ++ and −−
  signs are present among the 5 big sites' gap signs.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0);
triplet fold sha vs M28/M34; R_s vs loo on all 764; cell-7
count s0 2475 exact (s9 2670 exact, d!=0 throughout); tail
counts s0 102 exact with sub-bins 28+74 and max 47, s9 117
exact + J 0.7520 exact; FULL unnamed TSV match (all 764 rows:
tail + J4 + all-33-column n/ov/pres) vs `m34-census.tsv`
(else stop everything); moved set == pinned 15 + per-cell
n/ov + standings + deltas (else stop everything); pooled
extra/missing counts == 22+8 (else stop everything); all 30
pooled sites' (offset + |δ| + status + gaps + signs) == M35
pins (else stop everything); all 30 pooled sites Y-plane
(tabled; any non-Y = stop and table); big-5 seats compatible
with M35 per-cell band/dec distributions (else stop and
table); s0 P1 edges match m18.txt s0 row; P(δ>0)==M19/M20
0.8093 on s0; `loo.txt` 764 rows + top-10 shapes/shares;
self Jaccard == 1.0.

## Run protocol

1. Input shas + `m35.txt`/`m34-census.tsv` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + row guard (k 15 + standings +
   deltas or stop) + pooled-count guard + 30-site value pins
   (or stop).
3. Task 1: big-5 per-site table + rank table + headliner
   overlap (canon for determinism).
4. Task 2: top-10 per side + row geometry + band/decile
   seats.
5. Determinism re-run receipt (Task 1 on s0+9, canonical
   sha).
6. PNG big-|δ| map (s0 geometry; big |δ|≥19 magenta wins over
   near-big 16–18 cyan over rest-of-30 yellow over shared
   green; s9's 30 pooled sites; per-color counts tabled) to
   work dir; evidence copy ONLY if H1 meets AND H2 meets AND
   H4 meets (the big-vs-near-big split visible in the
   pre-registered |δ|≥19 / 16–18 / <16 coloring) — else
   absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 05:40 EDT, stop by 09:40).
