# M50 — Design (recorded before running)

Goal: 731/733 full-set attribution (M29 gap 10): 733's [303] +
731's [259,279] dest extras read gap 0 on s0 — one frame's
growth sits static (|δ|=0, i.e. g==0 with v0==full) on the
other frame. Wipe reproduction + dest recount (do the rows
reproduce?) + wiped values + static census (where does g==0
live?) + controls. Full-set attribution for 731/733 (wiped
source columns' rows + values — NEW DATA) + static-on-other-
frame census (g==0 sites on BOTH sides: wiped rows with
g_Q==0? dest rows with g_s0==0 = 28/41 reproduced? kept
rows?). Answer by table. Tables, no verdicts. Fully offline:
no lease of any kind, no boots, no harness runs, no fork
changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, baseline guard only — no m15 analysis),
`/Volumes/Extreme SSD/m28/m28-census.tsv` (731/733 named rows
to reproduce — match exactly or table the mismatch and stop)
+ `/Volumes/Extreme SSD/m34/m34-census.tsv` (731/733 unnamed
rows to reproduce — match exactly or table the mismatch and
stop). Work dir: `/Volumes/Extreme SSD/m50/` (new). Evidence:
`local/research/M50/` (committed with `git add -f`, prefix
`[M50]`, trailer `Orchestrated-By: Muse Code`; NEVER `git push`
in ssx3).

Headers read first: `local/research/M29/REPORT.md` (all of it:
M29 gap 10 = this brief — 15/19 733-privates + 13/18
731-privates read gap 0 on s0) plus `local/research/M28/
REPORT.md` (all of it: 731 tail 100 J 0.6833 wipes [257,277]
→ dests 259/279 +2/+2 rows 25–33; 733 tail 100 J 0.6694
wipes [301,321] → dests 303/323 +2/+2 rows 25–33/34) plus
`local/research/M43/REPORT.md` (all of it: the 4 dest cells
WITH values — 37 sites on 731/733 + 761's 4 = 41 pooled,
28/41 g_s0==0 — by reference for dests: reproduce the 28/41
count, then attribute the WIPED sides + full sets).

## Estimator (`m50.py`, `control.py`)

Shared core (M43 `m43.py` verbatim where reused: YUYV 640x448
decode, `synth_w_bytes` at w=0.5, `xdiff`, `fnv1a`,
`parse_loo`, `plane_of_byte`, `plane_coords`, `jaccard`,
`interior_sites` (cell 7 = M19 id 7 verbatim),
`tail_bulk_masks` (|d|>=8 tail), `off_of`, `y_col_rows`,
`tail_y_cols`, `census_unnamed_of`, `attrib_lines`,
`gapsign_lines`, `dstats_lines`, `load_triplet`,
`compute_sets_for`, `split_planes`, `flat_to_planes`,
`yuv_to_rgb`, PNG writer). Byte offset o -> row o//1280; Y
bytes at o%4==0/2. Named-census helper `census_named_of`
(M28 verbatim) added for the 8-column guard. No P1/decile/
streak/carrier/BFS/displacement machinery: the brief pins no
band/decile/streak/carrier joins (wipe rows + values + static
census only), so `compute_dec_masks` / `posjoin_lines` /
`bands_of` / `ROW_BAND` / `p1_gradient` are dropped (disclosed
here; input integrity still rests on the triplet fold sha +
R_s-vs-loo on all 764 + FULL TSV guards ×2 + Model-0
recompute).

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
  47); s731 100; s733 100 (M28-pinned); s761 106 (M34-pinned,
  dest-recount guard only).
- Signed gap g = v0 − full (int16 per byte, M27/M43 verbatim).
  Static site = g==0 (v0==full). Cell-7 requires moved, so
  g!=0 throughout cell-7 (guard): wiped sites read g_s0!=0
  always (s0 tail), dest sites read g_Q!=0 always (Q tail),
  kept sites read g!=0 on both frames always (tail both).
  Staticness is therefore an OTHER-frame property: wiped
  g_Q==0? dest g_s0==0? kept g==0 on either (want 0)?
- NAMED8 (M28-pinned): [257,277,296,301,321,340,342,343].
  S0 named rows (M28-pinned): c257 [23..32] (10), c277
  [23..32] (10), c296 [24,25,26,27,28,31,32,33,34] (9), c301
  [23..33] (11), c321 [23..32] (10), c340
  [24,25,26,27,31,32,33,34] (8), c342 [27,28,29,34,35] (5),
  c343 [26,27] (2).
- UNNAMED domain (M34-pinned): sorted union over all 764 shapes
  of tail-Y columns, minus NAMED8. Want: 33 columns (13
  s0-bearing + 20 pure-private).
- 731/733 pins (M28 named + M34 unnamed rows, read before
  running; s0 tail 102 J 1.0000):
  s731 tail 100 J 0.6833, named moved [257,277]: both 0/0
  full wipe (n0 10/10, miss 10/10, extra 0/0); unnamed moved
  [259,279]: 259: 9/0, n0 0, 0/9/9 extra-only; 279: 9/0, n0
  0, 0/9/9 extra-only. Wiped 20, dest 18, shared 82.
  s733 tail 100 J 0.6694, named moved [301,321]: both 0/0
  full wipe (n0 11/10, miss 11/10, extra 0/0); unnamed moved
  [303,323]: 303: 9/0, n0 0, 0/9/9 extra-only; 323: 10/0,
  n0 0, 0/10/10 extra-only. Wiped 21, dest 19, shared 81.
  No other 731/733 moves (named moved sets == wipes only,
  unnamed moved sets == dests only — verified via FULL TSV
  guards + per-shape moved-set guards).
- s761 pins (dest-recount guard only, M34-pinned): tail 106
  J 0.9623, unnamed moved [54]: 4/0, n0 0, 0/4/4 extra-only.
  Pooled dest recount: 761 4 + 731 18 + 733 19 = 41 extras.
- Wipe row pins (derived from S0_ROWS + full-wipe standings):
  s731 wipes = s0 rows (c257 [23..32], c277 [23..32]), Q rows
  [] (empty — full wipe); s733 wipes = s0 rows (c301
  [23..33], c321 [23..32]), Q rows []. Must reproduce or
  table the mismatch (guard stops everything).
- Dest row pins (M43 §Task 1, recount targets): 731-c259/
  c279 rows 25–33 (9 each), 733-c303 rows 25–33 (9),
  733-c323 rows 25–34 (10), 761-c54 rows [259,261,263,274]
  (4). Must reproduce or table the mismatch (guard stops
  everything).
- M43 dest values CITED (by reference, never recomputed —
  no dest per-site |δ|/status/gap tables are produced here;
  the dest side of the wipe-vs-dest comparison uses these
  cited numbers):
  731-c259 |δ| [10,13,15,16,17,17,17,17,18] med 17.0, 0/9
  bulk, −−2/−0 7; 731-c279 [11,16,16,16,16,17,17,17,19] med
  16.0, 0/9 bulk, −−3/−0 6; 733-c303
  [9,11,12,13,13,13,13,15,16] med 13.0, 0/9 bulk, −−1/−0 8;
  733-c323 [8,11,15,16,16,16,17,18,18,19] med 16.0, 0/10
  bulk, −−3/−0 7. Pooled-41 |δ| med 16.0 mean 14.2927 max
  19; pooled-37 (731/733 dests) med 16.0; s731 pooled med
  16.5 mean 15.8333; s733 pooled med 15.0 mean 14.1579.
  Pooled bulk 4/41 (all 761's; 0/37 on 731/733). Pooled gap
  signs ++0/−−13/−0 28 (731/733 dests: −−9/37, −0 28/37).
- Dest recount (RECOMPUTED, not cited): per-dest-cell extras
  row-lists + g_s0==0 counts. Want: 761-c54 0/4 g_s0==0
  (all −−), 731-c259 7/9, 731-c279 6/9, 733-c303 8/9,
  733-c323 7/10 — pooled 28/41 (731/733: 28/37). Mismatch =
  stop and table (guard).
- Dest |δ| at static sites (Task 2.2 dest leg): derived from
  M43's CITED per-site rows (split cited |δ_Q| lists by
  cited g_s0==0 vs !=0) — no dest triplet re-reads for
  values. Wiped |δ| at static sites: NEW DATA (recomputed).
  Kept |δ| at static sites: recomputed shared sets + g==0
  counts (want 0 static; |δ| tabled as n/a with counts).
- Per-cell sets: wipe M_c = s0-tail Y rows in column c minus
  Q rows (== s0 rows here — Q rows [] full wipe); extra E_c
  = Q-tail Y rows in column c minus s0 rows (== Q rows here
  — s0 rows [] fresh). Q in {731,733} for wipes; Q in
  {761,731,733} for dest recount. Per-site row for a wiped
  site o (M36/M43 verbatim, roles swapped): offset, plane,
  (r,c), |δ_s0|, Q status (bulk/non-cell) + |δ_Q| or `n/a`,
  signed gaps g_s0 vs g_Q.
- Near-miss (M27-pinned): other-frame bulk with |δ_other| in
  {6,7}. Far: bulk with |δ_other| <= 5. Non-cell: not cell-7
  on the other frame.
- Full sets: priv P_Q = T_Q − T_s0, miss M_Q = T_s0 − T_Q,
  shared S_Q = T_Q & T_s0. 0-outside checks: P_Q == union of
  dest extras AND M_Q == union of wiped rows on each shape
  (H4 — exact).

### Task 1 — wipe reproduction + dest recount (do the rows reproduce?)

731/733 recomputed from the dumps FIRST (FULL named TSV +
FULL unnamed TSV guards + each shape's row: tails, J, moved
sets, n/ov, standings, deltas — §Guards — or table the
mismatch and stop; no further tasks run).

1. Wipe tables: all 4 wipe cells s0-rows vs Q-rows (want [] —
   full wipe) vs miss rows (full wiped row lists, the new
   data; `head`-style per-cell rows + pooled counts 20+21).
2. Dest recount: all 5 dest cells (incl. 761-c54) extras
   row-lists + g_s0==0 counts (want 0/4 + 7/9 + 6/9 + 8/9 +
   7/10 = 28/41 pooled; 731/733: 28/37) + kept-row g==0
   counts (want 0 on each shape's shared set, both frames).
3. Full-set table: 731 + 733 priv/miss/shared/tail with
   0-outside checks (are the wipes + dests the whole sets?
   H4 — priv==dest extras, miss==wiped rows, 0 outside).

### Task 2 — wiped values + static census (where does g==0 live?)

1. Wiped-value table: per-site |δ_s0|, Q status, signed gaps,
   gap signs for ALL 41 wiped rows (`attrib_lines` per shape
   × wipe cell, tag `s{Q}w{col}`, offset order; M36-style) +
   per-cell |δ|/status/sign stats (`dstats_lines` +
   `gapsign_lines`) + pooled-41 wiped stats.
2. Static census: g==0 sites by side (wiped g_Q==0 n?
   dest g_s0==0 n? kept g==0 n? — per shape + pooled) +
   |δ| at static sites (wiped: |δ_s0| static vs non-static
   medians/lists, NEW; dest: cited |δ_Q| split by cited
   g_s0==0 vs !=0; kept: n/a with counts — is staticness a
   value regime? numbers only).
3. Wipe-vs-dest comparison: wiped |δ|/status/signs (measured)
   vs M43's dest stats (cited §Definitions) — per-leg table
   (n, |δ| med/mean/lists, bulk/noncell split, gap-sign
   split) + H5 measurement (numbers only — same regime or
   not?).

### Task 3 — controls + determinism (M18–M49 precedent)

`control.py` (imports `m50` cell/tail/core; expectations
analytic; fully synthetic frames — no s0 dependency):

- C-WIPEDEST (known wipe+dest sets incl. KNOWN g==0 sites,
  mimics 731/733 swap + static census): synthetic truth
  frames A/B (full 573440-B, all zeros = static non-cell
  background) with hand-set Y sites via `off_of`:
  N_STATIC=3 wipe sites (tail on A with |δ|=10, g_A!=0;
  static non-cell on B with g_B==0) + N_NONSTATIC=3 wipe
  sites (tail on A |δ|=10; bulk on B |δ|=2, g_B!=0) +
  N_STATIC=3 dest sites (static non-cell on A g_A==0; tail
  on B |δ|=10) + N_NONSTATIC=3 dest sites (bulk on A |δ|=2;
  tail on B |δ|=10) + N_KEPT=2 kept sites (tail both frames
  |δ|=10, g!=0 both). Tail values: v0=0/full=100/blend=50/
  mid=60 (|δ|=10); bulk values: mid=52 (|δ|=2); static
  values: v0=full=50/mid=50 (g==0, non-cell). All other
  bytes v0==mid==full==0. Recompute cell 7 + tail on both:
  wipe set (T_A−T_B) must equal the injected 6 exactly,
  dest set (T_B−T_A) the injected 6 exactly, kept 2 exactly,
  J must equal 2/14 = 0.1429 exactly, per-site |δ| exact
  (10 on tail legs, 2 on bulk legs), Q/A statuses exact
  (3 bulk + 3 noncell per side), gaps exact (g==0 on the 6
  static legs, g=−100 on the 6+6+4 non-static legs),
  static census exact (wiped g_B==0 3/6, dest g_A==0 3/6,
  kept g==0 0/2 either frame), per-column row-lists +
  standings exact (wipe cells missing-only, dest cells
  extra-only, derived from the injection), all background
  bytes non-tail.
- Pass = sets + Jaccard + row-lists + per-site values +
  statuses + gaps + static census exact. Construction
  failure (any injected site misclassified under the
  estimator's own cell/tail recompute) = tabled RED,
  cannot-inject (M38–M43 precedent).

Determinism: re-run Task 1 (per-shape per-cell wipe
row-lists + dest-recount rows + full-set rows) on s0+731+
733 (plus s761 dest-recount rows for the pooled guard) with
fresh loads; canonical text sha byte-identical pass1 vs
pass2.

Input shas (sha256 full, in the receipt): s0 + s731 + s733 +
s761 triplets + m15 triplets + `m28-census.tsv` sha (want
`27872527…7ca15a9e7f` 54296 B) + `m34-census.tsv` sha (want
`83482d1f…926c8aa8` 163262 B); triplet fold sha over all
764x3 bins (M28/M34 precedent — want
`6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1`).
Model-0 recompute: R_0/fnv must match M17–M49 (s0 22815 /
`6b9ffda25bd76c6f`, m15 13418 / `306b5c778898b64a`).
Mismatch = stop and table. R_s vs `loo.txt` cross-check on
ALL 764 shapes (want 764/764 equal; mismatch = stop and
table). `loo.txt` 764 rows + top-10 shapes/shares match M16.

## Falsification bars (recorded before running; tables, no verdicts)

Universe pinned: wiped 41 sites (s731 20 + s733 21) + dest 37
sites (s731 18 + s733 19) + 761's 4 (pooled dest recount 41)
+ kept shared 82 (s731) + 81 (s733) = 163 kept
site-instances (counted per shape). M43's dest stats cited
§Definitions (H2/H5 pool against cited legs).

- H1_WIPESTATIC (wipes sit static on Q — the mirror): share
  of the 41 pooled wiped sites with g_Q==0 is >= 0.50.
- H2_DESTSTATIC (dests sit static on s0 — reproduces M43):
  share of the 37 pooled 731/733 dest sites with g_s0==0 is
  >= 0.50 (M43 reads 28/37 = 0.7568; pooled 28/41 = 0.6829
  with cited 761 0/4).
- H3_WIPEBULK (wiped values sit on Q bulk — asymmetry vs dest
  0/37 bulk on s0): share of the 41 pooled wiped sites with
  Q-bulk status is >= 0.50.
- H4_FULLSET (wipes + dests are the whole sets): priv == dest
  extras AND miss == wiped rows on BOTH 731 and 733 with 0
  outside priv/miss (exact).
- H5_VALUEMED (wiped vs dest value regime — same median or
  not?): median |δ_s0| over the 41 wiped sites differs from
  M43's cited dest pooled median 16.0.
- H6_KEEPSTATIC (kept sites read static on either frame):
  share of the 163 pooled kept site-instances with g==0 on
  either frame is >= 0.50 (tail-both null: want 0).
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); triplet fold sha vs M28/M34; R_s vs loo on all 764;
cell-7 count s0 2475 exact (s731/s733/s761 cell counts NOT
pinned — no prior report lists 731/733/761 cell counts as a
pinned triple — tabled as measured with d!=0 throughout);
tail counts s0 102 exact with sub-bins 28+74 and max 47,
s731/s733 100 exact + J 0.6833/0.6694 exact, s761 106 exact
+ J 0.9623 exact; FULL named TSV match (all 764 rows: tail +
J4 + all-8-column n/ov/pres) vs `m28-census.tsv` (else stop
everything); FULL unnamed TSV match (all 764 rows: tail +
J4 + all-33-column n/ov/pres) vs `m34-census.tsv` (else stop
everything); 731/733 named moved sets == the pinned wipes +
per-cell n/ov 0/0 + standings + n0 (§Definitions, else stop
everything); 731/733/761 unnamed moved sets == the pinned
dests + per-cell n/ov + standings + deltas (§Definitions,
else stop everything); pooled wiped/dest counts == 20+21 /
18+19+4 (else stop everything); all 41 wiped + 41 dest-
recount sites Y-plane (tabled; any non-Y = stop and table);
dest g_s0==0 pooled == 28/41 exact with per-cell 0/4 + 7/9
+ 6/9 + 8/9 + 7/10 (else stop everything); wiped g_s0!=0
throughout + dest g_Q!=0 throughout + kept g!=0 both frames
(cell-7 moved guards; any violation = stop and table);
P(δ>0)==M19/M20 0.8093 on s0; `loo.txt` 764 rows + top-10
shapes/shares; self Jaccard == 1.0.

## Run protocol

1. Input shas + TSV shas + Model-0 recompute + cross-checks
   (§Task 3).
2. Cell-7 + tail recompute on all 764 + count/J guards +
   FULL named TSV guard + FULL unnamed TSV guard +
   731/733/761 row guards (named wipes + unnamed dests or
   stop) + pooled-count guards + dest g_s0==0 guard (28/41
   or stop).
3. Task 1: per-cell wipe row-lists (4 cells) + dest-recount
   rows (5 cells) + kept g==0 counts + full-set + 0-outside
   rows (canon for determinism).
4. Task 2: wiped per-site value tables (41 sites) + per-cell
   stats + pooled-41 wiped stats + static census (counts by
   side + |δ| at static: wiped NEW, dest from cited M43
   rows, kept n/a) + wipe-vs-dest side-by-side (measured vs
   cited).
5. Determinism re-run receipt (Task 1 lines on s0+731+733+
   761 dest rows, canonical sha).
6. PNG static-site maps (s0 geometry; wiped sites: magenta =
   static g_Q==0 / cyan = non-static; dest extras: red =
   static g_s0==0 / yellow = non-static; shared green —
   per-shape maps for 731/733) to work dir; evidence copy
   (at most the s733 map) ONLY if H2 meets AND the wiped
   static share reads split (1..40 of 41 wiped sites static,
   i.e. neither 0 nor 41 — the mirror question visible in
   the pre-registered static/non-static coloring) — else
   absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 06:56 EDT, stop by 10:56).
