# M47 — Design (recorded before running)

Goal: shape-711 pair wipe (M28 gap 3 via M29 gap 6): c342 + c343
fully missing with no assigned dest (no-cand both). Singleton +
far private-column listing per unassigned move: name the 11
singleton private Y-cols on movers (M28 tabled only the count),
list the multi-private far pool, and table 711's wiped rows +
values so a later brief can judge assignment. Answer by table
(list, don't assign). Tables, no verdicts. Fully offline: no
lease of any kind, no boots, no harness runs, no fork changes,
no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m34/m34-census.tsv` (711's unnamed row to
reproduce: NO unnamed moves — the wipe is purely named-column;
FULL TSV guard per M35/M36 precedent),
`/Volumes/Extreme SSD/m28/m28-census.tsv` (FULL named-TSV guard
per M34 precedent — 711's named row must read c342 0/0 + c343
0/0). Work dir: `/Volumes/Extreme SSD/m47/` (new). Evidence:
`local/research/M47/` (committed with `git add -f`, prefix
`[M47]`, trailer `Orchestrated-By: Muse Code`; NEVER `git
push` in ssx3).

Headers read first: `local/research/M28/REPORT.md` (all of it:
711 tail 95 J 0.9314 moved [342,343], c342 0/0 + c343 0/0 full
wipe both, dest no-cand both; 11 singleton private Y-cols on
movers tabled only as a count; M28 displacement rule reused
verbatim) plus `local/research/M34/REPORT.md` (all of it: 711's
census row tail 95 J 0.9314 with NO unnamed moves; union-domain
unnamed census method reused verbatim; s0-bearing-13 row lists
+ pure-private-20 list pinned below).

## Estimator (`m47.py`, `control.py`)

Shared core (M28 `m28.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|δ|≥8 tail), `plane_of_byte`,
`plane_coords`, `parse_loo`, `jaccard`, `off_of`,
`y_col_rows`, `priv_y_cols`, `census_of_shape` named exact-match
presence, `assign_one` displacement; M34 `m34.py` verbatim where
reused: `tail_y_cols`, `census_unnamed_of`, union-domain rule;
M36 `m36.py` verbatim where reused: `attrib_lines`,
`gapsign_lines`, `dstats_lines`; M28 PNG writer). Byte offset o
-> row o//1280; Y bytes at o%4==0/2.

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
- Named columns (the census 8, fixed order): [257,277,296,301,
  321,340,342,343].
- s0 named reference row lists (M27/M28 pins — guard: recomputed
  s0 per-column n + row lists must match exactly or stop):
  - 257: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 277: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 296: n=9 [24,25,26,27,28,31,32,33,34]
  - 301: n=11 [23,24,25,26,27,28,29,30,31,32,33]
  - 321: n=10 [23,24,25,26,27,28,29,30,31,32]
  - 340: n=8 [24,25,26,27,31,32,33,34]
  - 342: n=5 [27,28,29,34,35]
  - 343: n=2 [26,27]
- 711 wipe pins (M28/M34 — guard: recompute must match exactly
  or table the mismatch and stop; no further tasks run):
  tail 95, J 0.9314, moved [342,343], c342 0/0 + c343 0/0
  (full wipe both), dest no-cand both, NO unnamed moves
  (all 33 unnamed present).
- Wiped rows (derived from the pins): c342 [27,28,29,34,35]
  (5 rows) + c343 [26,27] (2 rows) = 7 wiped rows.
- M28 movers (pool domain, pinned): [9,22,708,709,710,711,731,
  732,733,734].
- Singleton pool (pinned): private Y-columns with EXACTLY 1
  site on the 10 movers. Count guard: must read 11 (M28's
  count) or table the mismatch and stop.
- Far pool (pinned): private Y-columns with ≥2 sites on the
  10 movers (the multi-private candidate pool, listed not
  ranked). Per-column col distance to the wipe tabled as
  d342=|col−342| + d343=|col−343| (the "at distance?" is
  answered by table, not by threshold).
- UNNAMED domain (M34 union rule verbatim): union tail-Y
  columns over all 764 minus the named 8. Pinned: 41 union
  cols, 33 unnamed (13 s0-bearing + 20 pure-private):
  - s0-bearing (n0>0): 38:[215], 292:[400], 293:[405],
    298:[28,29,34,35], 307:[404], 311:[296,297,298,299],
    312:[299,300,301], 313:[274,275,276,292],
    314:[269,276,277,278,287,288,289],
    315:[266,267,268,273,274,275,276], 316:[264],
    332:[295,304], 372:[221] (37 sites).
  - pure-private (n0==0): [54,145,259,279,295,299,303,310,
    318,322,323,327,328,336,337,339,351,602,611,620].
  - c341 bears tail on no shape (stays empty across all 764).
- Near-miss (pinned, M27 verbatim): other-frame bulk with
  |δ_other| ∈ {6,7}. Far: bulk with |δ_other| ≤ 5.
  Non-cell: not cell-7 on the other frame.
- Signed gap g = v0 − full (int16 per byte, M36 verbatim).
  Gap signs: g_Q × g_O per site (++/−−/mixed/zero tabled).
- Displacement (pinned, M28 `assign_one` verbatim): per moved
  column c with NONEMPTY missing rows; extra-only moves get no
  destination (`dest=none(extra-only)`); candidates = private
  Y-columns with ≥2 sites on the SAME shape; dest(c) = argmin
  |col_priv − c|, tie-break 1: max row-overlap with rows_0(c),
  tie-break 2: smallest column; no candidates →
  `dest=none(no-cand)`.

### Task 1 — 711 wipe reproduction (do the 2 columns reproduce?)

711's row recomputed from the dumps (must match M28/M34 exactly
— tail, J, moved cells, 0/0 standings, no unnamed moves — or
table the mismatch and stop):

1. Wipe table: c342 + c343 s0-rows vs 711-rows (empty) vs
   miss rows (full s0 row lists — the wiped rows).
2. Wiped-value table: per-site |δ_s0|, s711 status, signed
   gaps, gap signs for all 7 wiped rows (M36-style:
   `attrib_lines` + `gapsign_lines` + `dstats_lines` verbatim
   on the wiped miss set).
3. No-cand table: M28's dest candidacy rows for c342/c343
   reproduced (711's full private-Y-col listing + the ≥2-site
   candidate set + per-move rule rows — why no-cand?
   distance? occupancy? — table the rule's rows, don't
   re-judge).

### Task 2 — singleton + far private-column listing (the new data)

1. Singleton table: all 11 singleton private Y-cols (shape,
   column, the 1 private row, |δ_Q|, s0 status + |δ_s0|,
   signed gaps, gap signs — M36-style per-site rows; must
   count 11 or table the mismatch and stop).
2. Far-column table: multi-private Y-columns on movers with
   per-column priv counts + rows + |δ| lists/meds
   (`dstats_lines` verbatim) + s0-status splits + d342/d343
   (the far-candidate pool, listed not ranked).
3. Per-move listing: c342's (5) + c343's (2) wiped-row counts
   vs the singleton pool (11 rows) + far pool (total rows)
   (which pools COULD cover the wiped rows by count? numbers
   only — no assignment).

### Task 3 — controls + determinism (M18–M46 precedent)

`control.py` (mid-level synthetic truth, M36 C-VAL-style —
feasible because tail↔bulk flips keep cell-7 membership):

- C-WIPE (known wipe + singleton/far pools, mimics 711 at
  small N): s0 mid' with N_wipe=7 currently-TAIL Y sites in
  c342[27,28,29,34,35]+c343[26,27] flipped to bulk
  (mid'=blend+1, fallback blend−1 per site if +1 is not
  strictly inside — tabled) AND N_sing=3 currently-
  interior-BULK gap≥17 Y sites in 3 fresh cols flipped to
  tail (mid'=blend+8 even / blend−8 odd, |δ|=8; per-site
  strict-interior check) AND N_far=4 currently-interior-BULK
  gap≥17 Y sites in 1 fresh col flipped to tail (|δ|=8).
  Known: wipe rows = the 7, singleton cols = the 3 (1 row
  each), far col = the 1 (4 rows), per-site values exact,
  cell-7 mask fixed.
- Pass = wipe-rows-exact + singleton/far-listing-exact +
  values-exact + gaps-exact + standings-exact.

Determinism: re-run Task 1 (711 wipe rows + wiped values +
no-cand rows + singleton/far pools) on s0+711 with fresh
loads; canonical text sha byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + s711 + m15
triplets + `m28-census.tsv` + `m34-census.tsv` shas; triplet
fold sha over all 764×3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M46 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.
FULL named TSV byte-identical vs `m28-census.tsv` + FULL
unnamed TSV byte-identical vs `m34-census.tsv` (mismatch =
stop and table).

## Falsification bars (recorded before running; tables, no verdicts)

Denominators: W = 7 wiped rows (c342: 5, c343: 2), S = 11
singleton-pool sites, F = far-pool (shape,col) count
(tabled at runtime).

- H1_PUREWIPE (711's wipe is purely named-column): 711 holds
  0 private sites (priv=0, miss=7, shared=95, J=95/102).
- H2_SINGBULK (singleton pool reads bulk on s0): share of
  the 11 singleton sites reading bulk (near+far) on s0 is
  ≥ 0.50.
- H3_FARPOOL (far pool is non-trivial): multi-private
  Y-columns on movers read ≥ 6 distinct (shape,col).
- H4_WIPEBULK (wiped rows read bulk on 711): share of the 7
  wiped sites reading bulk (near+far) on s711 is ≥ 0.50.
- H5_WIPEGG (wiped rows read ++ gaps): share of the 7 wiped
  sites with ++ gap signs (g_s0 × g_711) is ≥ 0.50.
- H6_POOLMED (pools differ in |δ| level): |far-pool median
  |δ_Q| − singleton-pool median |δ_Q|| ≥ 4.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
FULL named TSV byte-identical (764 rows) vs `m28-census.tsv`;
FULL unnamed TSV byte-identical (764 rows) vs
`m34-census.tsv`; UNNAMED domain = pinned 33 (41 union);
s0-bearing-13 row lists exact; c341 empty on all 764; s711
tail 95 + J 0.9314 + moved [342,343] + c342/c343 0/0 +
no unnamed moves; 711 dest no-cand both under the M28 rule;
singleton count == 11; s0 cell 2475 + tail 102 with sub-bins
28+74 and max 47; δ≠0 throughout cell 7 (all analyzed
shapes); P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + `m28-census.tsv`/`m34-census.tsv` shas +
   Model-0 recompute + cross-checks (§Task 3).
2. Full 764 pass + FULL TSV guards + UNNAMED-domain guard +
   711-row guard + singleton-count guard (or stop).
3. Task 1: wipe table + wiped-value tables + no-cand
   candidacy rows.
4. Task 2: singleton per-site table + far-column table +
   per-move count listing.
5. Determinism re-run receipt (Task 1 on s0+711, canonical
   sha).
6. PNG wipe/pool map (320x224 native, <5 MB total) to work
   dir; evidence copy ONLY if H1 meets AND the singleton
   pool holds ≥3 bulk sites (the pool structure visible in
   the pre-registered wipe/singleton/far split) — else
   absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 06:31 EDT, stop by 10:31).
