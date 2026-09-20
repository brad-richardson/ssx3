# M52 — Design (recorded before running)

Goal: peak-row vs value agreement (M26 gap 2): 5/8 columns share
peak rows cross-frame but only 6/65 shared-site δ values agree
(M25 H5) — positional vs value structure split. Peak-anchored
residual tables: residuals (δ − column-peak-δ) per column per
frame + agreement-vs-distance-from-peak (do the 6 agreeing sites
sit AT peaks? do peak rows agree in residual while disagreeing
in δ?). Answer by table. Tables, no verdicts. Fully offline: no
lease of any kind, no boots, no harness runs, no fork changes,
no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m25/m25.txt` (H5 xmatch lines to
reproduce — match exactly or table the mismatch and stop),
`/Volumes/Extreme SSD/m26/m26.txt` (hump + xshape lines to
reproduce — match exactly or table the mismatch and stop). Work
dir: `/Volumes/Extreme SSD/m52/` (new). Evidence:
`local/research/M52/` (committed with `git add -f`, prefix
`[M52]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M26/REPORT.md` (all of it:
5/8 peak rows agree — 257:25/25, 277:25/25, 296:26/26,
301:27/27, 342:27/27; differ 321:25/26, 340:26/32, 343:27/289)
plus `local/research/M25/REPORT.md` (H5: 6/65 pooled, per-column
agrees 0/0/1/0/2/2/0/1 over n 10/10/9/11/10/8/5/2; no column
all-equal).

## Estimator (`m52.py`, `control.py`)

Shared core (M26 `m26.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median` (halves
away from zero), `coarse_hist`, `exact_counts`, `hole_ranges`,
`count_runs`, `hump_metrics` (peak = argmax δ, FIRST on ties),
`task1_profile_lines` (emits M25-identical prof/shape + M26-
identical hump lines), `xframe_match_lines` (M25-identical
xmatch), `xshape_lines` (M26-identical xshape). Byte offset o ->
row o//1280; Y bytes at o%4==0/2. No fit machinery (no QUAD/
TRI/TWO task here).

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
- Named columns (profiles + peaks + residuals): c ∈
  {257,277,296,301,321,340,342,343} (the brief's 8; c341 is
  membership-guarded but not profiled/scored: 0 s0 / 1 m15
  sites). Column membership = all tail-Y sites with Y-column
  == c. Named-column tail bytes: want 65 s0 / 68 m15 (implied
  by the per-column guard rows).

Peak-anchored quantities (pinned, exact integer arith, no
rounding — all inputs and outputs are ints):

- Peak per column per frame (M26-verbatim): peak = argmax δ,
  FIRST occurrence on ties; peakrow p, peakval h. Same formula
  all 8 columns both frames, including ragged (c296/340) and
  negative (c342/343) columns — the "peak" of a negative
  column is its least-negative δ.
- Residual: res(r) = δ(r) − h (int; res(p) = 0 always).
- Row offset: off(r) = r − p (signed int); distance:
  d(r) = |off(r)| = |r − p| (int ≥ 0).
- Per shared (col,row) site (present on BOTH frames): two
  residuals (res_s0 via s0 peak, res_m15 via m15 peak), two
  distances (d_s0 = |r−p_s0|, d_m15 = |r−p_m15|). When peaks
  agree, d_s0 == d_m15 row-for-row.
- δ agreement (H5, M25-verbatim): δ_s0 == δ_m15 exactly.
- Residual agreement (this run): res_s0 == res_m15 exactly.
  Near (|| 1, not exact) tabled separately for both, never
  merged.

### Task 1 — H5 + peak reproduction (do the splits reproduce?)

M25 H5 + M26 peak rows recomputed M25/M26-verbatim from the
dumps. Must match exactly or table the mismatch and stop (no
further tasks run):

1. Agreement table: all 65 shared sites with s0-δ vs m15-δ +
   agree flag (name the 6 agreeing sites). Receipt: one
   `agree` line per shared site (col,row order) + M25-
   identical `xmatch` lines (per-column + pooled H5).
   Pins: 6/65 shared (share 0.0923), per-column agrees
   0/0/1/0/2/2/0/1 over n 10/10/9/11/10/8/5/2; no column
   all-equal.
2. Peak table: all 8 columns' argmax rows both frames + agree
   flag. Receipt: M26-identical `hump` lines (per column per
   frame) + `xshape` lines (per column + pooled). Pins: peak
   rows agree 5/8 (257: 25/25, 277: 25/25, 296: 26/26,
   301: 27/27, 342: 27/27; differ 321: 25/26, 340: 26/32,
   343: 27/289); tie rule M26-verbatim (first on ties).
3. Peak×agree join: per column peak-agree × n-agree (do
   peak-agreeing columns hold the 6 agrees?). Receipt: one
   `peakjoin` line per column + pooled split (agrees inside
   vs outside peak-agreeing columns).

Match checks (stop-and-table guards): the `xmatch` receipt
lines must equal the corresponding `m25.txt` lines
byte-exactly; the `hump` + `xshape` receipt lines must equal
the corresponding `m26.txt` lines byte-exactly. First-diff
tabled on mismatch.

### Task 2 — peak-anchored residuals (positional vs value split?)

1. Residual tables: per column per frame δ − peak-δ +
   row-offset profiles. Receipt: one `resid` line per column
   per frame: peak p/h + row order with (row:δ:res:off)
   quads. Exact integer arith throughout.
2. Distance table: each shared site's row distance from its
   column peak vs agree flag (agrees at distance 0?).
   Receipt: one `dist` line per shared site (col,row order):
   δ_s0, δ_m15, agree_δ, d_s0, d_m15, res_s0, res_m15,
   agree_res. Plus marginal `distmarg` lines: δ-agree rate by
   d_s0 bin (0 / 1 / 2 / 3 / 4+) and by d_m15 bin, pooled
   over shared sites; counts + rates per bin.
3. Residual-agreement table: H5 re-scored on residuals
   (peak-subtracted δ — does agreement rise above 6/65?).
   Receipt: M25-xmatch-format `xres` lines: per-column
   residual agrees over shared rows + pooled (shared=65
   denominator, same shared sets as H5) + near counts
   (|res_s0−res_m15|==1) per column + pooled. No N/A: all 8
   columns carry fitted peaks on both frames.

### Task 3 — controls + determinism (M18–M51 precedent)

`control.py` (imports `m52` peak/residual/agreement core; pure
listed-truth logic control — no pool injection: the gated
quantities are cross-frame peak/agreement/residual functions,
so the control feeds them two listed pseudo-frames with KNOWN
peaks + KNOWN agreeing sites at KNOWN distances and requires
exact recovery):

- C-P1: pseudo-frames A/B, pseudo-cols 901–904, listed δ:
  - c901 (peak-agree, rows 26–30): A = 10,14,20,14,10
    (peak 28/20); B = 10,12,20,12,8 (peak 28/20). Want: δ
    agrees 2/5 at r26 (d 2/2) + r28 (d 0/0); res A =
    −10,−6,0,−6,−10; res B = −10,−8,0,−8,−12; residual
    agrees 2/5 at r26 + r28.
  - c902 (peak-disagree, rows 26–29): A = 18,12,10,8
    (peak 26/18); B = 10,20,12,8 (peak 27/20). Want: δ
    agrees 1/4 at r29 (d_A 3, d_B 2); res A =
    0,−6,−8,−10; res B = −10,0,−8,−12; residual agrees 1/4
    at r28 (≠ δ-agree site).
  - c903 (peak-agree negative, rows 26–28): A =
    −10,−20,−12 (peak 26/−10, least-negative); B =
    −12,−22,−16 (peak 26/−12). Want: δ agrees 0/3; res A
    = 0,−10,−2; res B = 0,−10,−4; residual agrees 2/3 at
    r26 + r27 (residual rises above δ).
  - c904 (first-tie rule, rows 26–28): A = 15,15,10
    (peak 26/15, first tie); B = 12,15,15 (peak 27/15,
    first tie). Want: peaks 26/27 (differ); δ agrees 1/3
    at r27 (d_A 1, d_B 0); res A = 0,0,−5; res B =
    −3,0,0; residual agrees 1/3 at r27.
  - Pooled want: shared 15; δ agrees 4/15 (sites
    (901,26),(901,28),(902,29),(904,27)); peak agree 2/4
    (901,903); residual agrees 6/15 (sites (901,26),
    (901,28),(902,28),(903,26),(903,27),(904,27)).
  - Pass = peaks exact all cols both frames + δ agree
    sites + counts exact + distances exact all shared
    sites + residual agree sites + counts exact + pooled
    lines exact. Any deviation tabled (control red).

Determinism: re-run Task 1 on s0+m15 (cell-7 + tail recompute
+ profiles + hump + xmatch + xshape); canonical-text sha over
both frames' Task-1 lines byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
m25.txt + m26.txt. Model-0 recompute: R_0/fnv must match
M17–M51 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_ATPEAK_S0 (agrees sit at s0 peaks): among δ-agreeing
  shared sites, the share with d_s0 == 0 is ≥ 0.50 (≥3 of 6
  if H5 pins reproduce).
- H2_ATPEAK_M15 (agrees sit at m15 peaks): among δ-agreeing
  shared sites, the share with d_m15 == 0 is ≥ 0.50 (≥3 of 6
  if H5 pins reproduce).
- H3_RESRISE (peak-subtraction recovers agreement): pooled
  residual exact-agrees exceed pooled δ exact-agrees by ≥10
  sites (≥16/65 if H5 pins reproduce).
- H4_RESLEVEL (residual agreement reaches profile level):
  pooled residual exact-agreement share over the 65 shared
  sites is ≥ 0.25 (≥17/65 if H5 pins reproduce).
- H5_PEAKHOLD (peak-agreeing columns hold the δ agrees):
  among δ-agreeing shared sites, the share sitting in
  peak-agreeing columns is ≥ 0.75 (≥5 of 6 if pins
  reproduce).
- H6_DISTGRAD (agreement falls with peak distance): δ-agree
  rate over shared sites at d_s0 == 0 exceeds the rate at
  d_s0 ≥ 4 by ≥ 0.20 absolute. If either bin is empty the
  bar reads n/a (tabled, not met).
- H7_RESATPEAK (residual agrees concentrate at peaks): among
  residual-agreeing shared sites, the share with d_s0 == 0
  is ≥ 0.50. If zero residual agrees the bar reads n/a
  (tabled, not met).
- N (standing remainder + residual split): shared-site δ
  after peak-anchored residuals + remaining split — the
  deliverable whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; per-column membership
(n, minrow, maxrow, sum δ) exact per the M25/M26 table below;
M25 xmatch-line match + M26 hump/xshape-line match
(byte-exact vs `m25.txt` / `m26.txt`); H5 pins 6/65 +
per-column 0/0/1/0/2/2/0/1 + peak pins 5/8 (values above);
δ≠0 throughout cell 7; P(δ>0)==M19/M20 0.8093/0.8019;
`loo.txt` 764 rows + top-10 shapes/shares; self Jaccard == 1.0.

Per-column guard table (n / rows / sum δ; mean=sum/n):

| col | s0 n/rows/sum | m15 n/rows/sum |
| --- | --- | --- |
| 257 | 10 / 23–32 / +255 | 10 / 23–32 / +172 |
| 277 | 10 / 23–32 / +244 | 10 / 23–32 / +172 |
| 296 | 9 / 24–34 / +294 | 9 / 24–34 / +306 |
| 301 | 11 / 23–33 / +339 | 11 / 23–33 / +291 |
| 321 | 10 / 23–32 / +227 | 10 / 23–32 / +252 |
| 340 | 8 / 24–34 / +292 | 9 / 24–34 / +311 |
| 341 | 0 / — / 0 | 1 / 280–280 / −9 |
| 342 | 5 / 27–35 / −94 | 5 / 27–35 / −87 |
| 343 | 2 / 26–27 / −57 | 4 / 25–289 / −97 |

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Task 1: per-site agree table (65 lines); M25 xmatch match
   guard + M26 hump/xshape match guards (mismatch → stop);
   peak×agree join.
4. Task 2: residual tables; distance table + marginals;
   residual-agreement (xres) table.
5. Determinism re-run receipt (Task 1 on s0+m15, canonical
   sha).
6. PNG residual map (320x224, <5 MB total) to work dir, s0
   named-column sites colored by residual-agree outcome
   (agree / near / disagree on shared sites; unshared grey);
   evidence copy ONLY if some named column with shared-n≥8
   reads residual-agree-count − δ-agree-count ≥ 2
   (peak-subtraction visibly recovers agreement in a specific
   pre-registered-split column) — else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 07:14 EDT, stop by 11:14).
