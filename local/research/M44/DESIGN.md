# M44 — Design (recorded before running)

Goal: same-column opposite standings (M34 gap 4): c298 reads a
full 4-row wipe on 709 but extra-only growth on 732 (keeps s0's
4 rows); c311 reads 11 extra-only vs 1 missing-only across 12
movers. Row-list + per-site value comparison of opposite
standings in the SAME column — wipe vs growth at c298 (values
at wiped rows vs kept rows vs grown rows?), the lone c311
missing vs the 11 c311 extras. Tables, no verdicts. Fully
offline: no lease of any kind, no boots, no harness runs, no
fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (mover counts +
standings to reproduce: c298/c311 rows pinned below — match
exactly or table the mismatch and stop). Work dir:
`/Volumes/Extreme SSD/m44/` (new). Evidence:
`local/research/M44/` (committed with `git add -f`, prefix
`[M44]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M34/REPORT.md` (all of it:
gap 4 = this brief; c298 2 movers 1/1/0, c311 12 movers 1/11/0;
the census method) plus `local/research/M35/REPORT.md` (all of
it: c311's missing-only mover is shape 9: missing (296,311)
|δ_s0| 10 noncell ++ — the 1 in the 11-vs-1; M27-style
per-site rows) plus `local/research/M28/REPORT.md` (all of it:
732's c296→c298 move context + 709-c298's [28,29,34,35] wipe
rows) plus `local/research/M36/REPORT.md` (M36-style per-site
rows: s2c311 (259,311), s3c311 (258,311), s700c311 (259,311)).

## Estimator (`m44.py`, `control.py`)

Shared core (M35 `m35.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `attrib_lines`,
`gapsign_lines`, `dstats_lines`, `split_planes`,
`flat_to_planes`, `yuv_to_rgb`; M34 `m34.py` verbatim: full-764
pass + TSV guard + canon/PNG scaffolding). Byte offset o ->
row o//1280; Y bytes at o%4==0/2. No P1/carrier/BFS/
displacement machinery (brief pins row-lists + per-site value
comparison only — no band/decile/streak/carrier joins).

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
  47); 709 97; 732 95.
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus the named 8 [257,277,296,301,321,
  340,342,343]. Want: 33 columns (13 s0-bearing + 20
  pure-private).
- c298 (M34-pinned, from `m34-census.tsv` rows — read from the
  match target before running): s0 rows [28,29,34,35] (n0 4);
  2 movers: s709 n/ov 0/0 (miss-only full wipe, miss rows
  [28,29,34,35]) + s732 n/ov 6/4 (extra-only growth keeping
  s0's 4 rows, +2 extra rows: NEW DATA — row numbers listed by
  the run). Standings 1/1/0. Tails/J: 709 (97, 0.9510), 732
  (95, 0.8942).
- c311 (M34-pinned, from `m34-census.tsv` rows): s0 rows
  [296,297,298,299] (n0 4); 12 movers, standings 1/11/0: s9
  n/ov 3/3 (miss-only, miss row [296] per M35) + 11 extra-only
  each n/ov 5/4 (+1 extra row each): s2 [259], s3 [258],
  s700 [259] per M36 (guarded), s380/s381/s382/s383/s384/
  s386/s387/s389 extra rows NEW DATA. Tails/J: s9 (117,
  0.7520), s2 (103, 0.9159), s3 (103, 0.9340), s380–s389
  (103, 0.9903 each), s700 (114, 0.8462).
- Per-site row (M36-style, both directions): offset, plane,
  (r,c), |δ_Q| on the tail-bearing frame, other-frame status
  (bulk/noncell) + |δ_other| or `n/a`, signed gaps g_Q vs
  g_other. Wiped sites: Q=s0, O=mover. Grown sites: Q=mover,
  O=s0. Kept sites: both-frame |δ| + gaps (both tail by
  construction — asserted).
- Near-miss (M27-pinned): other-frame bulk with |δ_other| in
  {6,7}. Far: bulk with |δ_other| <= 5. Non-cell: not cell-7
  on the other frame. Gap signs g_Q × g_O (+/−/0 each leg).

### Task 1 — c298 wipe-vs-growth (row-lists + values)

c298 recomputed from the dumps FIRST (§Guards — s0 rows, 2
movers, 1/1/0 standings — or table the mismatch and stop; no
further tasks run).

1. Row-list table: s0 [28,29,34,35] vs 709 [] (wipe) vs 732's
   rows (kept 4 + the 2 extra rows — the new data).
2. Value table: 709's 4 wiped sites (|δ_s0|, s709 status +
   |δ_709|, signed gaps s0 vs s709) + 732's 2 extra sites
   (|δ_732|, s0 status + |δ_s0|, signed gaps s732 vs s0) +
   the 4 kept rows' both-frame values (|δ_s0| and |δ_732|,
   gaps) — M36-style per-site rows.
3. Wipe-vs-growth comparison: wiped-row values vs kept-row
   values vs grown-row values (|δ| lists/min/med/mean/max per
   set, bulk/noncell splits, gap-sign splits — numbers only).

### Task 2 — c311 11-vs-1 (row-lists + values)

c311 recomputed from the dumps FIRST (§Guards — s0 rows, 12
movers, 1/11/0 standings, s9's miss row [296], s2/s3/s700
extra rows — or table the mismatch and stop).

1. Mover table: all 12 shapes with standings + n/ov +
   extra/missing rows (the 8 unknown extra-only movers'
   rows: NEW DATA).
2. Value table: s9's (296,311) (|δ_s0|, s9 status + |δ_9|,
   gaps — must reproduce M35's 10/noncell/24/7) vs all 11
   extras' sites (|δ_Q|, s0 status + |δ_s0|, gaps — one
   per-mover row; shared sites tabled per mover).
3. Lone-vs-crowd comparison: the missing site's values vs the
   11 extras' pooled stats (|δ| min/med/mean/max, bulk split,
   gap-sign split — numbers only).

### Task 3 — controls + determinism (M18–M43 precedent)

`control.py` (imports `m44` cell/tail/core; value-level
synthetic truths on s0 mid', M35 C-VAL machinery; v0/full
unchanged so gaps equal both frames at every injected site):

- O-OPP (known opposite standings, 3 synthetic shapes from
  s0):
  - Shape B (wipe + lone): drop all 4 s0 c298 tail rows +
    drop s0 (296,311) tail site (mid'=blend+1, blend−1
    fallback per site if +1 is not strictly inside —
    tabled). Known: c298 moved wipe n/ov 0/0 miss rows
    [28,29,34,35]; c311 moved miss-only n/ov 3/3 miss row
    [296]; per-site |δ| 1 (fallback tabled); J(T_B,T_0) =
    97/102.
  - Shape C1 (growth + crowd-A): add 2 extras in c298 +
    1 extra in c311 (first 2 / first 1 interior-BULK Y
    sites in that column with gap>=17 in offset order,
    strict-interior checked for blend±8 — rows tabled;
    mid'=blend+8 on even (r+c) / blend−8 on odd,
    |δ|=8). Known: c298 n/ov (4+K298)/4 extra-only; c311
    n/ov 5/4 extra-only; J(T_C1,T_0) = 102/(102+K298+1).
  - Shape C2 (crowd-B): add 1 extra in c311 (next suitable
    site after C1's — row tabled; c298 untouched/present).
    Known: c311 n/ov 5/4 extra-only; c298 present;
    J(T_C2,T_0) = 102/103.
  - Then c298 reads 1 wipe (B) + 1 growth (C1) with C2
    present; c311 reads 1 miss-only (B) + 2 extra-only
    (C1, C2). K' adaptive: if a target column holds fewer
    suitable bulk sites than wanted, inject into all
    available (K' tabled, K'>=1 required per targeted
    column — else the control reports infeasible and
    tables why; no silent column substitution).
  - Pass = moved-sets + per-column n/ov/pres + row-lists +
    per-site values (|δ|, statuses, gaps) + standings exact
    on all 3 shapes; P/M sets exact; Jaccards exact;
    cell-7 mask fixed (== s0 mask: every injected site was
    already cell-7); all other tail members' δ unchanged.

Determinism: re-run Tasks 1–2 row-lists + per-site value rows
on s0+709+732+9 + all c311 movers with fresh loads; canonical
text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + 709 + 732 + 9 +
all 11 c311 extra-only movers' triplets + m15 triplets +
`m34-census.tsv` sha; triplet fold sha over all 764x3 bins
(M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M43 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_WIPESET (wiped sites are set changes): share of 709's 4
  c298 wiped sites with s709 non-cell status is >= 0.50.
- H2_GROWSET (grown sites are set changes): share of 732's
  c298 extra sites with s0 non-cell status is >= 0.50.
- H3_CROWDSET (crowd extras are set changes): share of the 11
  c311 extra sites with s0 non-cell status is >= 0.50.
- H4_WIPEGAP (wiped sites read +/+): share of 709's 4 c298
  wiped sites with g_s0 > 0 and g_709 > 0 is >= 0.50.
- H5_CROWDGAP (crowd extras read −/−): share of the 11 c311
  extra sites with g_Q < 0 and g_s0 < 0 is >= 0.50.
- H6_LONEMAG (the lone missing is big): s9's (296,311)
  |δ_s0| is >= the median of the 11 crowd extras' |δ_Q|.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with the
  tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact; tail counts s0 102 exact with
sub-bins 28+74 and max 47 (plus tails/J of
709/732/9/2/3/380–389/700 vs §Definitions — else stop);
UNNAMED == 33 columns (13 s0-bearing + 20 pure-private) with
the census universe matching the TSV header (else stop
everything); FULL unnamed TSV match (all 764 rows: tail + J4
+ all-33-column n/ov/pres) vs `m34-census.tsv` (else stop
everything); c298 row guard (s0 rows [28,29,34,35]; movers
[709,732]; 709 n/ov 0/0 miss-only; 732 n/ov 6/4 extra-only;
standings 1/1/0 — else stop everything); c311 row guard (s0
rows [296,297,298,299]; 12-mover set + per-shape n/ov vs
§Definitions; standings 1/11/0; s9 miss row [296]; s2/s3/s700
extra rows [259]/[258]/[259] — else stop everything); d!=0
throughout cell 7 (all analyzed shapes); P(δ>0)==M19/M20
0.8093 on s0; `loo.txt` 764 rows + top-10 shapes/shares;
self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34-census.tsv` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + c298/c311 row guards (rows or
   stop).
3. Task 1: c298 row-lists + per-site value tables + kept-row
   values + wipe-vs-growth comparison.
4. Task 2: c311 mover table + per-site value tables +
   lone-vs-crowd comparison.
5. Determinism re-run receipt (Tasks 1–2 row-lists + value
   rows on s0+709+732+9 + all c311 movers, canonical sha).
6. PNG split-column value map (s0 geometry; c298 sites: wiped
   red / kept green / grown yellow; c311 sites: kept green /
   lone magenta / crowd cyan; Y only) to work dir; evidence
   copy ONLY if H4 meets AND H5 meets (the gap-sign split
   visible in the pre-registered wipe-vs-growth /
   lone-vs-crowd split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 05:58 EDT, stop by 09:58).
