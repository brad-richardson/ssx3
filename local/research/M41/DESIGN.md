# M41 — Design (recorded before running)

Goal: near-miss triple (M35 gap 2): shape 9's only extra-side
near (c336, |δ_s0| 6) + only 2 missing-side nears (both c312,
|δ_9| 6/7, one gap-equal 28/28) — 3/30 sites. Boundary-|δ|
census at unnamed cells: is 3/30 exact (no other boundary-|δ|
sites hiding at |δ| 5 or 8), and how does s9's 3/30 near rate
compare with the still-below rows' 14/24 extra-side near rate?
Answer by table: the 3 sites + full boundary census +
cross-row near table. Tables, no verdicts. Fully offline: no
lease of any kind, no boots, no harness runs, no fork changes,
no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (FULL TSV guard,
M34–M40 precedent), `/Volumes/Extreme SSD/m35/m35.txt` (the 3
sites to reproduce — match exactly or table the mismatch and
stop), `/Volumes/Extreme SSD/m36/m36.txt` (still-below near
counts to reproduce). Work dir: `/Volumes/Extreme SSD/m41/`
(new). Evidence: `local/research/M41/` (committed with
`git add -f`, prefix `[M41]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 2 = this brief — the 3 near-miss sites with offsets, |δ|
both frames, statuses, signed gaps both frames, gap signs;
extras 1/14/7 + missings 2/2/4; extra-side bulk |δ_s0| 1:11
2:3 6:1; missing-side bulk |δ_9| 2:1 3:1 6:1 7:1) plus
`local/research/M36/REPORT.md` (all of it: the still-below
near split — extras 14 near / 0 far / 10 noncell with all 14
nears at |δ_s0|∈{6,7}, missings 0/0/10; per-shape per-site
tables this brief recounts) plus `local/research/M40/REPORT.md`
(all of it: the c312 missing values (299,312) bulk6 gaps
22/16, (301,312) bulk7 gaps 28/28; measured s0c312 rows
[299,300,301]; s9 c312 rows [248,300]).

## Estimator (`m41.py`, `control.py`)

Shared core (M40 `m40.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `load_triplet`,
`compute_sets_for`, `split_planes`, `flat_to_planes`,
`yuv_to_rgb`). Byte offset o -> row o//1280; Y bytes at o%4==0/2.
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
  47); s9 117 (M35-pinned); s2/s3/s700 103/103/114
  (M36-pinned).
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- Shape-9 unnamed moved set (M34/M35-pinned, k=15): [310, 311,
  312, 313, 314, 315, 316, 318, 322, 327, 332, 336, 337, 339,
  351] with per-cell n/ov + n0 + standings + deltas per the
  M35 REPORT Task-1 table (row guard covers all 15 per
  M38/M39/M40 precedent — pooled 22 extras + 8 missings).
- Still-below unnamed moved sets (M34/M36-pinned): s2 k=6
  [311,312,313,314,332,339] (pool 5+4, tail 103, J 0.9159);
  s3 k=7 [311,313,314,316,332,336,339] (pool 4+3, tail 103,
  J 0.9340); s700 k=8 [38,54,299,311,313,314,332,620] (pool
  15+3, tail 114, J 0.8462); per-cell n/ov + n0 + standings
  + deltas per the M36 REPORT Task-1 tables (row guard
  covers all 21).
- Other-frame standing (M35/M36 convention): a pooled site
  evaluated on the other frame O reads noncell (o not cell-7
  on O), near (bulk on O with |δ_O|∈{6,7}), or far (bulk on
  O with |δ_O|∉{6,7}, i.e. 1–5 since bulk ⇒ |δ|<8 and
  cell-7 ⇒ δ≠0).
- Boundary-5 = bulk with |δ_O|=5 (near-adjacent below the
  {6,7} band). Boundary-8 = |δ_O|=8: structurally impossible
  on a pooled site (cell-7 with |δ|≥8 on O would be tail on
  O ⇒ shared, contradicting extra/missing) — tabled as 0
  with the structural reason, plus a supplemental raw-|δ|==8
  scan (other-frame raw |mid−blend|==8 at any status) so no
  hiding place goes untabled.
- Brief universe (3 near-miss sites, M35-pinned — reproduce
  exactly or table the mismatch and stop):
  extra-side (239,336) off 306592, Y, |δ_9| 8, bulk on s0,
  |δ_s0| 6, gaps 17/14, ++ (c336 extra-only d1);
  missing-side (299,312) off 383344, |δ_s0| 10, bulk on s9,
  |δ_9| 6, gaps 22/16, ++; (301,312) off 385904, |δ_s0| 9,
  bulk on s9, |δ_9| 7, gaps 28/28 (gap-equal), ++.
- Row-list pins (M35/M40): c336 s0 rows [] (n0=0), s9 rows
  [239], extra [239], miss []; c312 s0 rows [299,300,301]
  (M40-measured), s9 rows [248,300], extra [248], miss
  [299,301].
- Row-edge: a near site reads row-list-edge iff its row is the
  min or max of its cell's own-frame row-list (extra-side:
  s9 rows; missing-side: s0 rows); singleton row-lists table
  as edge-trivially (noted, not hidden).
- Value pins: all 30 s9 sites (M35 extra/missing tables,
  M40-verbatim) + all 34 still-below sites (M36 extra/missing
  tables — offsets, |δ| both frames, statuses, signed gaps
  both frames). Mismatch on ANY pin = stop and table.
- Gap-equal: g_Q==g_O (extra) or g_s0==g_Q (missing). M35
  reads extras 1/22 (c351 −39/−39), missings 2/8 (c315
  (273,315) 23/23, c312 (301,312) 28/28) — reproduced, not
  assumed.

### Task 1 — near-miss triple recompute (do the 3 sites reproduce?)

The 3 sites recomputed from the dumps FIRST (§Guards — pins
must match M35 exactly or table the mismatch and stop; no
further tasks run).

1. Per-site table: (239,336) + (299,312) + (301,312) with all
   pins + the gap-equal flag on (301,312).
2. Near-definition table: each site's other-frame |δ| against
   the {6,7} near band (in-band all 3?).
3. Row-list context: c336's + c312's s0/s9 rows around the
   sites (edge flags per §Definitions).

### Task 2 — boundary-|δ| census (is 3/30 exact? how do rows compare?)

1. s9 boundary census: all 30 pooled sites' other-frame |δ|
   histogram (|δ| 1–7 over bulk sites + noncell count, both
   sides; counts at 5/6/7/8 called out; raw-|δ|==8 scan) +
   near/far/noncell recount vs M35's 1/14/7 + 2/2/4 splits.
2. Still-below near recount: 24 extras' |δ_s0| histogram at
   {5,6,7,8} (14 nears reproduced? boundary counts?) +
   10 missings' |δ_Q| histogram (M36: 0 nears?) +
   near/far/noncell recount per shape vs M36.
3. Cross-row near table: s9 vs s2/s3/s700 near/far/noncell
   counts extra-side + missing-side, with near shares and
   the extra-side share gap (s9 1/22 vs still-below 14/24).

### Task 3 — controls + determinism (M18–M40 precedent)

`control.py` (imports `m41` cell/tail core; expectations
analytic):

- C-NEAR (known boundary census, mimics the near/far/noncell
  split): synthetic truth mid' on s0: N_NEAR=2 known
  near-missing cells (|δ_B| 6 and 7, one injected site each)
  + N_B5=1 known boundary-5-missing cell (|δ_B| 5) +
  N_FAR=1 known far-missing cell (|δ_B| 2) + N_NONCELL=1
  known noncell-missing cell (endpoint landing), each at a
  currently-TAIL Y site in a distinct Y column (columns
  assigned greedily in numeric offset order, tabled).
  Injected dv = sign(d[o])·k (k=6,7,5,2) — strictly inside
  by construction (|d|≥8 strictly inside ⇒ blend+k·sign(d)
  strictly inside; verified per site after recompute).
  Noncell landing mid'=v0 endpoint, falling back to full per
  site (endpoint reads noncell by construction since strict
  interior fails; verified per site after recompute).
  Shape A = s0 orig, shape B = s0 mid'. Recompute cell 7 +
  tail on B: per-cell standings must equal the injected
  5×missing-only delta-1 exactly, per-site values exact
  (near/b5/far landings |δ|=6/7/5/2 bulk on B; noncell
  landing status noncell on B), boundary census exact
  (near=2, b5=1, far=1, noncell=1), gaps equal on both
  frames at every injected site (v0/full unchanged —
  tabled), J(T_B,T_A) must equal 97/102 exactly, row-lists
  exact per cell, cell-7 mask = maskA minus exactly the
  injected noncell site, all other tail members' δ
  unchanged.
- Pass = standings + row-lists + per-site values + boundary
  census + gaps exact. Pool shortfall (no greedy assignment
  spans 2+1+1+1 cells) = tabled RED, cannot-inject (M38/M39/
  M40 precedent).

Determinism: re-run Task 1 (3-site rows + near-def + row-list
context) on s0+9 with fresh loads; canonical text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s2 + s3 + s9 +
s700 triplets + m15 triplets + `m34-census.tsv` +
`m35.txt` + `m36.txt` shas (m34-census.tsv want
`83482d1f…926c8aa8` 163262 B; m35.txt want `ff29739c…49349c`
69947 B; m36.txt want `bf2c5d81…8213ae1` 102945 B, read-only
pre-measurements); triplet fold sha over all 764x3 bins
(M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M40 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned from M35/M36: s9's 30 pooled sites (22 extras
+ 8 missings) + still-below's 34 (24 + 10). H1/H2/H7 are
reproduce bars; H3/H4 are exactness bars (meet = no boundary
hiding place — the pooled near counts stand as tabled);
H5/H6 are comparison bars (tabled, no verdicts).

- H1_TRIPLE_REPRO (triple reproduces): 3/3 near-miss sites
  read the §Definitions pins exactly (offset + |δ| both
  frames + status + signed gaps both frames + gap-equal on
  (301,312) only).
- H2_STILL_REPRO (still-below recount reproduces): extras
  14/0/10 + missings 0/0/10 (near/far/noncell), with
  per-shape splits s2 1/0/4 + 0/0/4, s3 2/0/2 + 0/0/3,
  s700 11/0/4 + 0/0/3.
- H3_S9_EXACT (s9 3/30 exact): pooled near count is 3 AND
  boundary-5 bulk count is 0 on both sides AND splits
  recount to extras 1/14/7 + missings 2/2/4.
- H4_STILL_EXACT (still-below boundary census exact): extras
  boundary-5 count is 0 AND near count is 14 AND far is 0
  AND noncell is 10; missings read 10/10 noncell.
- H5_CROSSROW (cross-row extra-side near-rate gap):
  |s9 extra near share − still-below extra near share|
  ≥ 0.25.
- H6_ROWEDGE (nears sit at row-list edges): 3/3 near sites
  read row-list-edge per §Definitions (singletons noted).
- H7_GAPEQUAL (gap-equal among nears): exactly 1/3 near
  sites gap-equal, namely (301,312) 28/28.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact (s9/s2/s3/s700 counts tabled as
measured, must equal M35/M36's measured 2670/2469/2484/2605
or table the mismatch and stop, with d!=0 throughout); tail
counts s0 102 exact with sub-bins 28+74 and max 47, s9 117
exact + J 0.7520 exact, s2/s3/s700 103/103/114 exact + J
0.9159/0.9340/0.8462 exact; FULL unnamed TSV match (all 764
rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv` (else stop everything); moved sets ==
pinned 15/6/7/8 + per-cell n/ov + standings + deltas (else
stop everything); pooled per-shape extra/missing counts ==
22+8 / 5+4 / 4+3 / 15+3 (else stop everything); all 64
pooled sites' (offset + |δ| + status + gaps) == pins (else
stop everything); all 64 pooled sites Y-plane (tabled; any
non-Y = stop and table); c336/c312 row-list pins ==
§Definitions (else stop everything); P(δ>0)==M19/M20 0.8093
on s0; `loo.txt` 764 rows + top-10 shapes/shares; self
Jaccard == 1.0.

## Run protocol

1. Input shas + `m34-census.tsv`/`m35.txt`/`m36.txt` shas +
   Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + row guards (k 15/6/7/8 +
   standings + deltas or stop) + pooled-count guards +
   64-site value pins (or stop) + c336/c312 row pins (or
   stop).
3. Task 1: per-site triple table + near-def table + row-list
   context (canon for determinism).
4. Task 2: s9 boundary census + still-below recount +
   cross-row near table.
5. Determinism re-run receipt (Task 1 on s0+9, canonical
   sha).
6. PNG near-miss map (s0 geometry; near cyan wins over s9
   far yellow over s9 noncell magenta over still-below
   noncell red; s9's 30 sites + still-below's 34 pooled
   sites; per-color counts tabled) to work dir; evidence
   copy ONLY if H1 meets AND H2 meets AND H5 meets (the
   cross-row near-rate gap visible in the pre-registered
   near-vs-far/noncell coloring) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 05:26 EDT, stop by 09:26).
