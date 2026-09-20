# M45 — Design (recorded before running)

Goal: shape-22 bottom-cluster full-set attribution (M34 gap 5 =
M33 gap 3 = M29 gap 4, taken on orchestrator judgment): 2
outside-col privates (393,307)/(402,295) + the 2 c296 far
extras (400,296)/(401,296) form a rows-393–402 group. Full-set
per-site attribution for shape 22 (|δ|, statuses, gaps, signs,
deciles) + bottom-cluster geometry (pairwise distances, shared
rows/cols with the c296 pair?). Tables, no verdicts. Fully
offline: no lease of any kind, no boots, no harness runs, no
fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (s22's unnamed row to
reproduce: tail + J + all-33-column n/ov/pres — match exactly or
table the mismatch and stop). Work dir: `/Volumes/Extreme SSD/m45/`
(new). Evidence: `local/research/M45/` (committed with `git add -f`,
prefix `[M45]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M33/REPORT.md` (all of it:
gap 3 = this brief via M34 gap 5; s9 cluster method + Jaccard/set
machinery) plus `local/research/M29/REPORT.md` (all of it: s22 c296
n/ov 11/9 extras [400,401], |δ| 8,8, gaps gQ 22,24 / gO −1,−2,
noncell ×2, dec 9,9; s22 full sets priv 4 / miss 0 / shared 102,
tail 106, J 0.9623; outside-col privates (393,307)/(402,295);
pooled extra[all] n=5 ostat bulk 3 / noncell 2, near 0) plus
`local/research/M34/REPORT.md` (all of it: s22's census row —
k=2 moved [295,307], tail 106, J 0.9623; s0 c307 rows [404] n0=1;
c295 pure-private n0=0; UNNAMED 33 = 13 s0-bearing + 20
pure-private) plus `local/research/M36/REPORT.md` (§Task 1:
M36-style per-site rows; grand pooled extras n=24 near/far/non
14/0/10 — pinned side-by-side reference).

## Estimator (`m45.py`, `control.py`)

Shared core (M44 `m44.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `attrib_lines`,
`gapsign_lines`, `dstats_lines`, `split_planes`,
`flat_to_planes`, `yuv_to_rgb`; M36 `m36.py` verbatim:
`p1_gradient` + M18 edge guard + per-site s0-P1 decile lookup;
M34/M44 verbatim: full-764 pass + fold sha + TSV-guard/canons/PNG
scaffolding). Byte offset o -> row o//1280; Y bytes at o%4==0/2.
No band/streak/carrier joins (brief pins |δ| + statuses + gaps +
signs + deciles + geometry only — no band thirds, no streak
columns, no carrier masks, no displacement-to-shared).

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
  47); s22 106.
- Full sets (shape 22 vs s0): P_22 = T_22 − T_s0 (want 4),
  M_22 = T_s0 − T_22 (want 0), S_22 = T_22 ∩ T_s0 (want 102);
  4+102=106 ✓, 0+102=102 ✓, 102/106=0.9623 ✓ (`f"{J:.4f}"`).
- Bottom group (pinned, M29/M34): B = {(400,296), (401,296),
  (393,307), (402,295)} — the 2 c296 far extras + the 2
  outside-col privates. INBAND = rows 393–402 inclusive (the
  M34-gap-5 band; all 4 pinned sites lie inside by pinning —
  the run RECOMPUTES membership, it does not assume it).
- Named census (exact-match, M28 rule): NAMED8 =
  [257,277,296,301,321,340,342,343] with s0 reference rows
  (M27/M28, guarded exact): 257:[23–32], 277:[23–32],
  296:[24,25,26,27,28,31,32,33,34], 301:[23–33], 321:[23–32],
  340:[24,25,26,27,31,32,33,34], 342:[27,28,29,34,35],
  343:[26,27]. s22 named want: moved [296] only, n/ov 11/9,
  extra rows [400,401], standing extra-only (M29).
- Unnamed census (exact-match, M34 rule): UNNAMED = sorted
  union over all 764 of tail-Y columns minus NAMED8 (want 33
  = 13 s0-bearing + 20 pure-private; universe must match the
  TSV header). s22 unnamed want (m34-census.tsv row, read
  before running): k=2, moved [295,307], c295 n/ov 1/0
  (s0 rows [], pure-private; extra row [402]), c307 n/ov 2/1
  (s0 rows [404]; extra row [393], kept [404]), standing
  extra-only both, tail 106, J 0.9623.
- Full moved-cell set of s22 (want): 3 cells — named c296 +
  unnamed c295 + unnamed c307 — holding 4 delta sites, all in
  B. "All s22 cells" = all 8 named + all 33 unnamed checked;
  anything else moved is tabled (completeness fails open).
- c296 pair values (pinned, M29 — guarded, not re-derived):
  (400,296): |δ_22|=8, s0 noncell, g_22=22, g_s0=−1, dec 9;
  (401,296): |δ_22|=8, s0 noncell, g_22=24, g_s0=−2, dec 9.
- New data (this run attributes): (393,307) + (402,295)
  values — |δ_22|, s0 status + |δ_s0|, signed gaps both
  frames, gap signs, s0-P1 decile.
- Per-site row (M36-style + dec): offset, plane, (r,c), cell,
  |δ_Q| on the tail-bearing frame, other-frame status
  (bulk/noncell) + |δ_other| or `n/a`, signed gaps g_Q vs
  g_other, gap signs, s0-P1 decile (Y-native lookup;
  U/V — if any — via co-located decimation, M22 verbatim).
- Near-miss (M27-pinned): other-frame bulk with |δ_other| in
  {6,7}. Far: bulk with |δ_other| <= 5. Non-cell: not cell-7
  on the other frame. Gap signs g_Q × g_O (+/−/0 each leg).
- Cluster geometry: pairwise row distances |Δr| over the 6
  site pairs of B + column seats (|Δc| + Δ vs c296) + shared
  row set + shared column set between the c296 pair
  {400,401} and the outside-col pair {393,402-rows}.
- Pooled-extra side-by-side references (pinned constants from
  committed REPORTs, cited, not recomputed): M29 extra[all]
  n=5 near/far/non 0/3/2; M29 extra[22,9] n=3 bulk 1 /
  noncell 2, near 0; M36 grand pooled extras n=24 near/far/non
  14/0/10. Measured against: s22's c296 pair split (want
  0/0/2) + s22's 4-site pooled split.

### Task 1 — s22 moved-set census (is the bottom group the whole set?)

s22's row recomputed from the dumps FIRST (§Guards — tier-1 TSV
+ tier-2 row-lists/sets — or table the mismatch and stop; no
further tasks run).

1. Moved-cell table: all s22 cells over named-8 + unnamed-33
   with n/ov + standings + deltas + row-lists (want 3 moved:
   c296 11/9 extra-only ex [400,401]; c295 1/0 extra-only ex
   [402]; c307 2/1 extra-only ex [393] kept [404]).
2. Private table: (393,307)/(402,295) with s0 rows of their
   columns (c307 s0 rows [404] s0-bearing? c295 s0 rows []
   s0-empty? — recomputed, not assumed).
3. Completeness table: bottom-group sites vs full s22 moved
   set — priv in-band/out + miss in-band/out (want priv 4/0,
   miss 0/0) + full (row,col) set lists + moved-cell delta
   rows in-band/out (is anything outside rows 393–402?).

### Task 2 — full-set attribution + cluster geometry

1. Per-site value table: ALL s22 moved sites (want P_22 4 +
   M_22 0) with offset, |δ_22|/|δ_s0|, statuses, signed gaps
   both frames, gap signs, deciles (M36-style rows + dec) +
   pooled near/far/non + `dstats` + `gapsign` lines.
2. Cluster geometry: pairwise row distances over the 4 bottom
   sites (6 pairs) + column seats (do 307/295 relate to
   c296? Δc tabled) + shared rows/cols between the c296 pair
   and the outside-col pair.
3. c296 side-by-side: s22's pair (8,8/noncell — guarded)
   pooled split vs the pinned pooled-extra splits (M29
   extra[all] 0/3/2, M29 extra[22,9] bulk-1/noncell-2,
   M36 grand 14/0/10) + s22's 4-site pooled split — which
   side? — tabled.

### Task 3 — controls + determinism (M18–M44 precedent)

`control.py` (imports `m45` cell/tail/core/P1; value-level
synthetic truth on s0 mid', M35 C-VAL machinery; v0/full
unchanged so gaps equal both frames at every injected site):

- C-BOT (known bottom-band + outside census, mimics s22's
  miss-0 shape): s0 mid' with K_in extras inside rows 393–402
  + K_out extras outside rows 393–402 (want K_in=K_out=2;
  first offset-order interior-BULK gap>=17 Y sites per zone,
  strict-interior checked for blend±8 — parity even (r+c)
  → +8 else −8, sign-fallback tabled; K'-adaptive: if a zone
  holds fewer suitable sites than wanted, inject into all
  available — K' tabled, K'>=1 required per zone, else the
  control reports infeasible and tables why; no cross-zone
  substitution). Known: priv = the K_in+K_out picked sites,
  miss = ∅, tail = 102+K_in+K_out, J = 102/(102+K_in+K_out)
  (`f"{J:.4f}"`), per-site |δ|=8, s0-bulk statuses with orig
  |δ| tabled, gaps gQ==gO, deciles = s0-anchored recompute,
  completeness K_in in-band / K_out out, per-column n/ov/pres
  + standings exact on every affected column, cell-7 mask
  fixed (== s0 mask: every injected site was already
  cell-7), all other tail members' δ unchanged.
- Pass = moved-sets + per-column n/ov/pres + row-lists +
  per-site values (|δ|, statuses, gaps, signs, deciles) +
  standings + completeness exact; P/M sets exact; Jaccard
  exact; mask fixed; rest unchanged.

Determinism: re-run Task 1 (moved-cell table + private table +
completeness + set lists + full-set counts) on s0+22 with fresh
loads; canonical text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s22 triplets +
m15 triplets + `m34-census.tsv` sha; triplet fold sha over all
764x3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M44 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.
P1 edges guarded vs m18 constants (`0 1 2 2 4 6 8 12 18 29 176`).

## Falsification bars (recorded before running; tables, no verdicts)

Bottom denominator = the 4 pinned bottom-group sites B unless
named (tier-2 passing; if tier-2 stops, H4 reads not-met with
the measured sets tabled).

- H1_BOTNEAR (bottom sites are near-misses): share of B with
  s0-bulk status and |δ_s0| ∈ {6,7} is ≥ 0.50.
- H2_BOTSET (bottom sites are set changes, not δ changes):
  share of B with s0 non-cell status is ≥ 0.50.
- H3_BOTDEC9 (bottom sites sit in dec-9 like the c296 pair):
  share of B in s0-P1 decile 9 is ≥ 0.50.
- H4_WHOLESET (the bottom group is the whole moved set):
  full s22 private set == B AND miss empty (meets iff the
  tier-2 set guard passes; nothing outside rows 393–402).
- H5_GAPOPP (bottom sites read opposite-sign gaps like the
  c296 pair's +/−): share of B with strictly opposite nonzero
  gaps (g_22 · g_s0 < 0) is ≥ 0.50.
- H6_NEWMAG (the new privates match the pair's magnitude):
  both (393,307) and (402,295) read |δ_22| == 8 (the c296
  pair's 8,8).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with the
  tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact; tail counts s0 102 exact with
sub-bins 28+74 and max 47 (plus s22 tail 106 — else stop);
UNNAMED == 33 columns (13 s0-bearing + 20 pure-private) with
the census universe matching the TSV header (else stop
everything); s22 TSV row match (tail + J4 + all-33-column
n/ov/pres vs `m34-census.tsv` line for shape 22 — else stop
everything); s22 pinned spot guards (unnamed k=2 moved
[295,307], c295 n/ov 1/0, c307 n/ov 2/1, tail/J 106/0.9623;
named moved [296] only, c296 n/ov 11/9; s0 named c296 rows;
s0 c295 rows [] + s0 c307 rows [404] — else stop everything);
tier-2 row-list/set guards (named c296 ex [400,401]; unnamed
c295 ex [402]; unnamed c307 ex [393] kept [404]; full priv set
== B as (row,col) SET; miss empty; shared 102; J 0.9623 —
else table the mismatch and stop); c296-pair value
cross-check vs M29 (|δ| 8,8 noncell ×2, g 22,24/−1,−2, dec
9,9 — else table the mismatch and stop); all moved sites
Y-plane (else table and stop); d!=0 throughout cell 7 (s0,
s22); P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34-census.tsv` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards + s0
   reference guards + UNNAMED-domain guard + s22 TSV-row
   guard + pinned spot guards + tier-2 row-list/set guards
   + c296-pair value cross-check (rows or stop).
3. Task 1: moved-cell table + private table + completeness
   table (canon).
4. Task 2: per-site value table + geometry + c296
   side-by-side + dstats + gapsign.
5. Determinism re-run receipt (Task 1 on s0+22, canonical
   sha).
6. PNG bottom-cluster map (s0 geometry; s22 shared green /
   c296 extras yellow / outside-col privates red; Y only) to
   work dir; evidence copy ONLY if H3 meets AND ≥3 bottom
   sites share decile 9 (localization visible in the
   pre-registered decile split; M29 rule verbatim, scaled to
   n=4) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 06:15 EDT, stop by 10:15).

Amendment (06:35 EDT, after a green receipt run + an infeasible
control run — bars, guards, and Task 1–2 definitions unchanged;
the final green receipt re-run below is the single recorded
invocation): the pre-registered mid-level C-BOT proved
INFEASIBLE as specified — rows 393–402 hold ZERO interior-BULK
gap>=17 Y sites on s0 (measured: in-zone candidates n=0), so no
|δ|=8 injection is possible in-band (gap>=17 is necessary for
blend±8 strictly inside). The control is re-scoped to two legs
in one `control.py` invocation (both must pass):
C-BOTM (mask-level, M28/M34-pinned: census logic operates on
tail masks — synthetic tail mask = s0 tail + 2 in-band sites +
2 out-of-band sites at known coords; recover moved-cells,
n/ov/pres, standings, row-lists, P/M sets, J, completeness 2/2,
and shared-`geo_lines` pairwise distances + span exactly) and
C-BOTV (mid-level value leg, out-of-band pool only: K'=4
|δ|=8 extras with known values; recover sets, J, per-site
values, gaps, signs, deciles, per-column census, completeness,
mask-fixed, rest-unchanged exactly). The original in-band
mid-level leg stays tabled infeasible with its measured reason.
Supporting refactor: pairwise geometry factored into shared
`geo_lines(sites, tag)` used by both `task2_lines` and C-BOTM
(same lines; Task-1 canon untouched). Pre-receipt estimator
fixes tabled in REPORT (bars-section `mask0` name; this
refactor).
