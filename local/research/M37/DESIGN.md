# M37 — Design (recorded before running)

Goal: c54 carrier coincidence (M36 gap 1): 700-c54's 10 extras
read 10/10 bulk near-miss at |δ| 8 AND 10/10 inside the 701
carrier mask — the first unnamed carrier hit in the M35/M36
value tables, vs 0/24 for every other still-below extra.
Coincidence question: is c54's 701-membership geometric (the
701 mask COVERS column 54's rows — any extra there would read
inside) or selective (the mask covers many columns but only
c54's extras land in it)? Answer by geometry: 701-mask column
profile + row-list comparison of c54's 10 rows vs the other
extras' rows against the 701 mask (other 9 carrier masks as
controls) + 701 tail census. Tables, no verdicts. Fully
offline: no lease of any kind, no boots, no harness runs, no
fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (unnamed-universe +
TSV guard, M36 precedent),
`/Volumes/Extreme SSD/m36/m36.txt` (c54's 10 rows + the
other-extras row lists to reproduce — match exactly or table
the mismatch and stop). Work dir: `/Volumes/Extreme SSD/m37/`
(new). Evidence: `local/research/M37/` (committed with
`git add -f`, prefix `[M37]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M36/REPORT.md` (all of it:
gap 1 = this brief — 700-c54's 10 extras [245, 246, 247, 252,
253, 258, 259, 278, 279, 283], all |δ_700| = 8, all bulk on s0
(|δ_s0| 6:2 7:8), all gaps −−, all inside the rank-3 701
removed-Y mask; the other still-below extras read 0 in every
carrier mask; pooled extras 24 = s2 5 + s3 4 + s700 15) plus
the M19 carrier table (the 701 mask definition + rank context:
rank 3 / shape 701, removed 649 Y px, bands [186, 463, 0],
367/649 = 56.6% interior-Y; mask = res0 & ~ress on Y,
M22-verbatim) and M22's 701 split (s0 tail inside 0, bulk
inside 367).

Brief-count note (recorded before running; table, don't stop):
the brief says "the other 23 extras" / "other-23 row lists",
but M36's exact universe is 24 pooled extra sites = c54's 10 +
14 others (s2 5 + s3 4 + s700 non-c54 5; 12 unique (r,c) across
shapes — (259,311) and (296,332) recur on s2+s700). The brief's
"23" matches no M36 extras count (plausibly a slip from M36's
"23/24 band-1" pooled-extras line, or 33−10 from the unnamed
column count). The brief's own stop rule names M36 as the match
target ("must match M36 exactly"), so the guards pin M36's
exact 24-site universe below; the "23" discrepancy is tabled in
the report and the brief proceeds on M36's universe.

## Estimator (`m37.py`, `control.py`)

Shared core (M36 `m36.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `attrib_lines`,
`gapsign_lines`, `dstats_lines`, `load_triplet`,
`compute_sets_for`, `compute_dec_masks` (masks + P1 guard),
`split_planes`, `flat_to_planes`, `yuv_to_rgb`, `bands_of` /
`ROW_BAND`; M36 `SHAPES` pins verbatim). Byte offset o -> row
o//1280; Y bytes at o%4==0/2. No P1/decile/streak/BFS/
displacement machinery beyond the M36 joins reused for
value-contrast side-by-side.

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
  340,342,343]. Want: 33 columns [38,54,145,259,279,292,293,
  295,298,299,303,307,310,311,312,313,314,315,316,318,322,
  323,327,328,332,336,337,339,351,372,602,611,620] (13
  s0-bearing + 20 pure-private).
- Carrier mask (M22-verbatim): removed-Y = res0 & ~ress on the
  Y plane, res0 = (synth0 != mid0), ress = (blend_s != mid_s).
  Top-10 ranks/shapes/shares/removed/bands pinned (M16/M19):
  694/6525/4888/[3415,1442,31], 693/1580/1208/[824,384,0],
  701/1126/649/[186,463,0], 368/441/448/[0,0,448],
  369/393/248/[0,0,248], 366/372/244/[0,0,244],
  370/262/191/[0,0,191], 376/260/174/[0,0,174],
  748/245/190/[0,0,190], 750/239/202/[0,187,15].
- M36 extra universe (match target, pinned from `m36.txt`
  per-site rows + head lines; guard §Guards):
  c54 (700): rows [245,246,247,252,253,258,259,278,279,283],
  all adQ=8 ostat=bulk, adO=[7,7,7,7,7,7,7,6,6,7],
  gQ=[-23,-23,-24,-22,-23,-23,-22,-22,-22,-22],
  gO=[-22,-23,-23,-21,-22,-22,-22,-21,-21,-21].
  others (14): s2 (259,311)/17/noncell/-37/-37,
  (293,313)/8/bulk7/-18/-19, (296,332)/20/noncell/-41/-41,
  (297,332)/9/noncell/-20/-20, (240,339)/9/noncell/19/17;
  s3 (258,311)/34/noncell/-71/-71, (265,316)/8/bulk7/18/18,
  (238,336)/8/bulk7/17/16, (238,339)/8/noncell/17/18;
  s700 (25,299)/34/noncell/-71/-72, (259,311)/17/noncell/
  -37/-37, (291,313)/8/bulk7/-19/-19, (296,332)/20/noncell/
  -42/-41, (170,620)/11/noncell/-24/-23.
  Other-extra columns (unique): [299,311,313,316,332,336,339,
  620] (8 columns).
- M36 carrier reads (match target): c54 10/10 inside the 701
  mask; every other extra/missing 0 in every mask; s700 shared
  0 in 701; the 1 shared byte in 368's mask (M22's tabled
  max-1 byte).
- M19 701 cell row (s0 Y-residual bytes in the 701 mask, match
  target): [233,20,22,1,2,2,2,367] over cells 0–7 (c7=367 =
  M22's bulk-inside; tail-inside 0).

### Task 1 — mask geometry (does 701 cover c54?)

c54's 10 rows + the other-14 row lists recomputed from the
dumps FIRST (§Guards — or table the mismatch and stop; no
further tasks run).

1. 701-mask column profile: per-Y-column mask-row counts for
   ALL 640 Y columns (nonzero columns listed individually +
   group summaries named-8 / unnamed-33 / rest — where does
   the mask sit? is c54 fully covered? partially?).
2. Overlap table: c54's 10 rows × 701 mask (all inside per M36
   — reproduce, per-row in/out) + the other 14 extras × 701
   mask (all outside per M36 — reproduce, per-site in/out) +
   c54's 10 rows × the other 9 carrier masks (inside anywhere
   else? per-row per-mask in/out).
3. Coverage answer as a TABLE: 701-mask rows per column for
   column 54 vs the 8 other-extra columns (geometric if c54's
   column is covered and others aren't; selective otherwise;
   numbers only) + H1/H2/H6 measurements.

### Task 2 — row-list comparison (c54 vs the other extras)

1. Row lists: c54's 10 rows vs each other extra's row — full
   (s0 rows, Q rows) per extra-bearing cell on s2/s3/s700
   (M36-headliner style for all 14 cells: s2 c311/c313/c332/
   c339, s3 c311/c316/c336/c339, s700 c54/c299/c311/c313/c332/
   c620) + row-number recurrence table (same rows recurring
   across shapes? c54 rows unique? H4).
2. Value contrast: c54's uniform |δ| 8 bulk −− vs the other 14
   (|δ| lists, bulk/noncell splits, gap signs — M36 numbers
   reproduced + side-by-side via `attrib_lines` /
   `gapsign_lines` / `dstats_lines`).
3. 701-mask tail census: s0 tail bytes in the 701 mask (want
   0, M22) + M19 cell-breakdown row reproduced + tail-in-mask
   counts for ALL 764 shapes (min/med/max + shapes with ≥1 +
   s2/s3/s700 rows — is the mask tail-dense generally? H5).

### Task 3 — controls + determinism (M18–M36 precedent)

`control.py` (imports `m37` cell/tail/mask core; expectations
analytic):

- C-MASK (known mask membership): synthetic truth mid' on s0:
  N_in=6 currently-interior-BULK Y sites INSIDE the 701 mask
  (bulk-Y offset order, first 6 passing the per-site check) +
  N_out=4 same-pool sites OUTSIDE the 701 mask (first 4
  passing), injected mid'=blend+8 on even (r+c) / blend−8 on
  odd (|δ|=8, the tail boundary; per-site strict-interior
  check; pool shortfall = tabled red). Shape A = s0 orig,
  shape B =
  s0 mid'. Recompute tail on B: P_B = T_B − T_A must equal the
  injected 10 exactly, M_B = T_A − T_B must be empty exactly,
  membership of P_B vs the 701 mask must read in=6/out=4 on
  the injected sets exactly (per-site in/out exact),
  per-site |δ| exact (8), cell-7 mask fixed, all other tail
  members' δ unchanged.
- Pass = sets + membership table exact.

Determinism: re-run Task 1 (mask column profile + overlap
tables + coverage table) on s0+700 with fresh loads; canonical
text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s2 + s3 + s700
triplets + m15 triplets + top-10 carrier triplets + `m34-
census.tsv` + `m36.txt` shas; triplet fold sha over all 764x3
bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M36 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned from M36: c54's 10 rows + 14 other-extra sites
in 8 other-extra columns [299,311,313,316,332,336,339,620].
(H2/H6 can both fail on a 4/4 split — tabled.)

- H1_GEOM_COVER (c54's column is the covered one): column-54
  701-mask-row count > the max over the 8 other-extra
  columns.
- H2_MASK_SPAN (mask covers others' columns too — selective
  leg): the 701 mask touches (≥1 mask row in) ≥5 of the 8
  other-extra columns.
- H3_C54_OTHER_CARRIER (c54 not 701-unique): ≥1 of c54's 10
  (r,c) sites inside any of the other 9 top-10 carrier masks.
- H4_ROW_RECURRENCE (rows recur, not unique): ≥1 of c54's 10
  row numbers recurs among the pooled other-extra row numbers
  (14 sites, multiplicity ignored).
- H5_TAILWIDE (mask tail-dense beyond s700): ≥2 of the 764
  shapes have ≥1 tail byte inside the 701 mask (s700 reads ≥10
  via c54 per M36 — the bar needs ≥1 further shape).
- H6_OTHERS_BARE (others' columns uncovered — geometric leg):
  ≥5 of the 8 other-extra columns hold 0 701-mask rows.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact (s2/s3/s700 cell counts NOT pinned
— no prior report pins them except as measured 2469/2484/2605
in M36 §Baseline — tabled as measured, must equal M36's
measured values or table the mismatch and stop, with d!=0
throughout); tail counts s0 102 exact with sub-bins 28+74
and max 47, s2/s3 103 exact, s700 114 exact + J 0.9159/
0.9340/0.8462 exact; FULL unnamed TSV match (all 764 rows:
tail + J4 + all-33-column n/ov/pres) vs `m34-census.tsv`
(else stop everything); 2/3/700 moved sets == the pinned
6/7/8 + per-cell n/ov + standings + deltas (§Definitions,
else stop everything); pooled per-shape extra/missing counts
== 5+4 / 4+3 / 15+3 (else stop everything); c54's 10 (r,c) +
per-site adQ/ostat/adO/gQ/gO == §Definitions pins (else stop
everything); the other 14 (r,c) + per-site values ==
§Definitions pins (else stop everything); all 24 pooled
extras Y-plane (tabled; any non-Y = stop and table);
carrier removed counts + bands (M19 values); s0 P1 edges
match m18.txt s0 row; s0-701 split tail-in 0 + bulk-in 367
(M22); M19 701 cell row [233,20,22,1,2,2,2,367]; d!=0
throughout cell 7 (all analyzed shapes); P(δ>0)==M19/M20
0.8093 on s0; `loo.txt` 764 rows + top-10 shapes/shares;
self Jaccard == 1.0.

## Run protocol

1. Input shas + `m34-census.tsv`/`m36.txt` shas + Model-0
   recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL unnamed TSV guard + 2/3/700 row guards (k 6/7/8 +
   standings + deltas or stop) + pooled-count guards + M36
   24-site value pins (or stop).
3. Task 1: 701-mask column profile (all 640 Y columns +
   group summaries) + overlap tables (c54×701, others×701,
   c54×other-9) + coverage table (col 54 vs 8 others).
4. Task 2: row lists per extra-bearing cell (all 14 cells) +
   row-recurrence table + value-contrast side-by-side +
   701 tail census (s0 + M19 row + all-764).
5. Determinism re-run receipt (Task 1 on s0+700, canonical
   sha).
6. PNG 701-overlap map (s0 geometry; 701-mask px slate /
   c54 extra rows yellow / other-extra rows red / s700
   shared green) to work dir; evidence copy ONLY if H1 meets
   AND ≥12/14 other-extra sites read outside the 701 mask
   (the geometric split visible in the pre-registered
   in/out split) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 04:40 EDT, stop by 08:40).
