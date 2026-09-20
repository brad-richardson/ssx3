# M59 — Design (recorded before running)

Goal: dec-1 all-positive δ (M58 gap 2, taken on orchestrator
judgment): all 12 dec-1 off-mode sites read δ>0 (+9..+33,
sum +214) while dec-0 splits 6/7, dec-3 splits 12/7, and
dec-4 splits 3/2. Per-bin δ-sign census over ALL 10 m15
tail-Y bins (0–9, n=134) joined with columns — is dec-1's
12/12 positive unique among bins, and does the sign split
track columns (c312? null-4? named streak cols?)? Answer by
table. Tables, no verdicts. Fully offline: no lease of any
kind, no boots, no harness runs, no fork changes, no `adb`.
Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet, column profiles), `/Volumes/Extreme SSD/m58/m58.txt`
(bin table to reproduce — match exactly per §Guards or table
the mismatch and stop). Work dir: `/Volumes/Extreme SSD/m59/`
(new). Evidence: `local/research/M59/` (committed with
`git add -f`, prefix `[M59]`, trailer `Orchestrated-By: Muse
Code`; NEVER `git push` in ssx3).

Headers read first: `local/research/M58/REPORT.md` (all of it:
dec-1 12/12 positive +9..+33 sum +214 on cols 307/309/310/
311/312×6/313/315; dec-0 6/7; dec-3 12/7; dec-4 3/2; dec-5
+9/+20; dec-9 59/16 sum +1179; off-51 pooled +454 at 35/16;
33 union cols; c312 22/51 off-mode with a 23rd m15 tail site
at r316) plus `local/research/M57/REPORT.md` (hist-4: m15
0:13/1:12/3:19/4:5/5:2 + 75 dec-9; s0 0 in 0–5; shared 67/69)
plus `local/research/M19/REPORT.md` (P(δ>0) 0.8093/0.8019 —
the background sign rate).

## Estimator (`m59.py`, `control.py`)

Shared core (M58 `m58.py` verbatim where reused: YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, PNG writer,
`plane_of_byte`, `plane_coords`, `jaccard`, `int_median`
(halves away from zero), `hole_ranges`, `off_y`
(o=r*1280+(c//2)*4+(0 if c even else 2)), `y_col_dict`
(tail-Y column profiles sorted by row), `far_info`
(nearest-neighbor row gap, singleton N/A), `aux_dist`,
`pooled_d`, `hump_metrics` (first-tie argmax peak),
`bands_of`/`ROW_BAND` (geometry thirds via
`np.array_split(arange(448),3)` → band0 r0–149, band1 r150–298,
band2 r299–447), `p1_gradient` (M18 P1 block verbatim:
|gx|+|gy| on s0 mid-Y, quantile edges, `digitize` deciles),
carrier removed masks (res0 & ~ress on Y, M22-verbatim),
`seat_of`, `decile_hist`, `tail_y_sites`, `off51_select`,
`col_counts`, `band_hist`). Byte offset o -> row o//1280; Y
bytes at o%4==0/2.

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard) — every site reads strictly pos or neg.
- Bulk = cell-7 bytes with |δ|<8 (want 2373 s0 / 2405 m15).
  Tail = cell-7 bytes with |δ|≥8 (want 102 s0 / 134 m15; s0
  sub-bins 28 in 8–15 + 74 in 16+, m15 50 + 84; max 47/48).
- Tail-Y = tail bytes on the Y plane (expect 102/0/0 s0 +
  134/0/0 m15; non-Y tabled, census-gating disclosed).
- Column membership = all tail-Y sites with Y-column == c.
- Seat (s0-anchored, M33/M58-verbatim): band = ROW_BAND[r];
  decile = s0 mid-Y P1 decile at (r,c) (`dec_s0[r,c]`,
  edges guarded vs m18 constants); streak = Y-column in the
  named-9 set {257,277,296,301,321,340,341,342,343} else
  `other`; carrier = inside/outside each M22-verbatim top-10
  removed mask (shapes [694,693,701,368,369,366,370,376,748,
  750]) + the 701 split (in/out); peak seat = column-frame
  first-tie argmax peak row (`hump_metrics` verbatim),
  at-peak? tabled per site.
- Bin-sign row (per decile d over a site set): n + pos/neg +
  pos share (pos/n, 4dp; n==0 → n/a) + δ min/max/sum + exact
  δ counts.
- Column-sign row (per column over m15 tail-Y): n + pos/neg +
  pos share + δ min/max/sum.
- Column-mode row (per column over m15 tail-Y): n + modal
  decile (count/share; ties → highest dec, disclosed — same
  convention as `decile_hist`) + modal δ-sign (pos/neg/tie;
  pos==neg → tie, disclosed).
- Shared tail S = T_s0 ∩ T_m15 (Y-plane intersection).
  Pooled = multiset union (disclosed; Jaccard tabled).
- The 12 (this brief's set): m15 tail-Y sites with s0-P1
  decile == 1. Want n=12, all δ>0, sum +214, δ +9..+33, on
  cols 307/309/310/311/312×6/313/315 (M58 site-51 pins).
- d (M56-verbatim `far_info` on the m15 tail-Y column
  profiles): nearest-neighbor row gap within the same column
  same frame; singleton columns (n==1) → d=N/A, tabled.

M58 pins (must reproduce or stop, §Guards):

- dechist m15: n=134, 0:13 1:12 2:0 3:19 4:5 5:2 6:1 7:2 8:5
  9:75.
- decbin m15 (n / δ counts / min / max / sum / pos / neg):
  - dec 0: 13 / −9:6 −8:1 +10:1 +15:1 +18:2 +20:2 / −9 / +20
    / +39 / 6 / 7.
  - dec 1: 12 / +9:2 +10:2 +14:1 +15:1 +19:1 +21:1 +22:1
    +23:1 +29:1 +33:1 / +9 / +33 / +214 / 12 / 0.
  - dec 2: 0 / — / None / None / 0 / 0 / 0.
  - dec 3: 19 / −18:1 −16:1 −15:1 −9:2 −8:2 +8:1 +9:1 +10:1
    +11:1 +13:1 +14:1 +19:1 +22:3 +24:1 +46:1 / −18 / +46 /
    +137 / 12 / 7.
  - dec 4: 5 / −8:2 +8:1 +17:1 +26:1 / −8 / +26 / +35 / 3 / 2.
  - dec 5: 2 / +9:1 +20:1 / +9 / +20 / +29 / 2 / 0.
  - dec 6: 1 / −35:1 / −35 / −35 / −35 / 0 / 1.
  - dec 7: 2 / +11:1 +46:1 / +11 / +46 / +57 / 2 / 0.
  - dec 8: 5 / −14:1 −9:2 +14:1 +23:1 / −14 / +23 / +5 /
    2 / 3.
  - dec 9: 75 / (35 distinct values; full counts in the
    receipt) / −36 / +48 / +1179 / 59 / 16.
- dec-1 sites (col/row/δ): 307/320/+9, 309/327/+10,
  310/321/+10, 311/320/+22, 312/318/+19, 312/319/+9,
  312/341/+14, 312/373/+33, 312/374/+15, 312/378/+23,
  313/339/+29, 315/336/+21.
- off-51 pooled δ: sum +454, pos 35 / neg 16 (pos share
  35/51 = 0.6863).
- dec-9 δ: sum +1179, pos 59 / neg 16 (pos share 59/75 =
  0.7867).
- M19 background P(δ>0): 0.8093 s0 / 0.8019 m15 (cell-7).
- 33 union tail-Y cols: 38/65/76/257/277/289/292/293/296/
  298/299/301/306/307/308/309/310/311/312/313/314/315/316/
  321/332/340/341/342/343/344/353/372/617.
- c312 m15 tail-Y n=23 (22 off-mode + r316 non-off-mode).
- null-4 cols: 313/332/314/311. Named streak cols: 257/277/
  296/301/321/340/341/342/343.

Sign-census helpers (factored for the control to import):

- `bin_sign_rows(sites, dec_plane, deltas)`: sites = list of
  (r,c); dec_plane = (H,W) int deciles; deltas = {(r,c): δ}.
  Returns per-decile dict {n, counts, min, max, sum, pos,
  neg, posshare}. Pure function of (plane, sites, deltas).
- `col_sign_rows(sites, deltas)`: sites = list of (r,c);
  returns {col: {n, pos, neg, posshare, min, max, sum}}
  sorted by col. Pure function of (sites, deltas).
- `col_mode_rows(sites, dec_plane, deltas)`: returns {col:
  {n, modedec, modedec_n, modedec_share, modesign,
  modesign_n, modesign_share}} sorted by col (tie
  conventions above). Pure function of (plane, sites,
  deltas).
- Dump path calls all three with m15 tail-Y sites + `dec_s0`
  + m15 deltas; control path calls all three with synthetic
  sites + a synthetic plane + synthetic deltas (identical
  code path).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float shares printed `:.4f`.

### Task 1 — bin-sign reproduction (do the splits reproduce?)

All 10 m15 tail-Y decile bins recomputed from the dumps
(must match M58's decile-bin table exactly — counts, δ
lists, sums, pos/neg per bin, incl. dec-9's 59/16 — or
table the mismatch and stop; §Guards):

1. Bin-sign table: per-bin n + pos/neg + pos share + δ
   min/max/sum (is dec-1 the only 1.0000?).
2. Dec-1 site table: the 12 sites' (row,col)/δ + seats
   (band/streak/carrier/701/at-peak — M33 machinery on
   12 sites) + peak + d/lo/hi (identity pins).
3. Background table: dec-1's 12/12 against the M19 P(δ>0)
   background + the pooled off-51 35/16 + the dec-9
   59/16 (shares tabled, no tests beyond counts).

### Task 2 — sign-by-column census (does sign track columns?)

1. Column-sign table: pos/neg splits per column over the 33
   union cols on m15 tail-Y (which columns read all-pos?
   c312's 23? null-4? named streak cols?) + per-site
   (row:δ/dec) detail per column.
2. Bin-column table: dec-1's 8 columns vs other bins'
   columns — per dec-1 column the per-bin site counts (do
   the 12 share columns with dec-0/dec-3 negatives?) +
   per-bin counts on dec-1-shared columns.
3. Mode table: per-column modal decile joined with modal
   δ-sign over m15 tail-Y (does column decile mode predict
   sign?; m15-empty union cols read n/a).

### Task 3 — controls + determinism (M18–M58 precedent)

`control.py` (imports `m59` sign-census core; expectations
analytic hand-computed; pure-synthetic dec plane + site
lists + delta dict, NOT dump-injected — deviation reasoned
per M53/M58: sign/bin helpers operate on (plane, sites,
deltas), so a synthetic plane exercises the identical code
path with zero dump coupling):

- C-SIGN: synthetic truth with KNOWN bin signs on a
  8×12 synthetic plane (rows 0–7, cols 0–11):
  - Plane: col 0–5 read dec 9 (mode block, 48 cells);
    col 6–7 read dec 3 (off-mode block, 16 cells);
    col 8 reads dec 0, col 9 reads dec 1, col 10 reads
    dec 4, col 11 reads dec 5.
  - Sites + deltas (12 sites; 1 all-pos bin + 3 split bins):
    - dec-1 all-pos bin (N=4): (0,9):+9 (1,9):+10
      (2,9):+22 (3,9):+29 — want n=4 pos=4 neg=0
      posshare 1.0000 min=+9 max=+29 sum=+70.
    - dec-0 split bin (N=2): (0,8):+20 (1,8):−9 — want
      n=2 pos=1 neg=1 sum=+11.
    - dec-3 split bin (N=3): (0,6):+22 (1,6):−18
      (2,7):+14 — want n=3 pos=2 neg=1 sum=+18.
    - dec-9 split bin (N=3): (0,0):+19 (1,1):−16
      (2,2):+8 — want n=3 pos=2 neg=1 sum=+11.
    - bins 2/4/5/6/7/8 empty (n=0, posshare n/a).
  - Want: bin-sign rows exact (all 10 bins incl. empties);
    column-sign rows exact (c0: 1/0; c1: 0/1; c2: 1/0;
    c6: 1/1; c7: 1/0; c8: 1/1; c9: 4/0); column-mode rows
    exact (c0: dec9/pos; c1: dec9/neg; c2: dec9/pos; c6:
    dec3/tie; c7: dec3/pos; c8: dec0/tie; c9: dec1/pos);
    per-site deciles exact (12 sites).
  - Pass = bin-sign + column-sign + column-mode + deciles
    exact.

Determinism: re-run Task 1 (bin-sign + dec-1 sites +
background) on s0+m15 (fresh loads); canonical-text sha
byte-identical pass1 vs pass2.

Input shas (sha256 full, in the receipt): s0 + m15
triplets + top-10 carrier triplets (30 bins) + `m58.txt`
sha (tabled; parsed bin values guarded per §Guards —
non-guarding sha comparison, tabled). Model-0 recompute:
R_0/fnv must match M17–M58 (22815/13418,
`6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch = stop
and table. R_s vs `loo.txt` cross-check on s0 (want equal;
mismatch = stop and table, M22 precedent).

## Falsification bars (recorded before running; tables, no verdicts)

- H1_BINMATCH (bins reproduce): recomputed m15 tail-Y
  decile-bin table matches M58 value-exactly (all 10 bins:
  n, δ counts, min/max/sum, pos/neg).
- H2_DEC1POS (dec-1 all-positive): dec-1 reads 12/12
  positive (pos share 1.0000; δ +9..+33; sum +214; on cols
  307/309/310/311/312×6/313/315).
- H3_DEC1UNIQUE10 (dec-1 uniquely all-pos at scale):
  dec-1 is the only bin with n≥10 reading pos share 1.0000
  (M58 pins dec-5/dec-7 all-pos at n=2 each, below the
  bar's n floor).
- H4_C312SPLIT (modal column splits): c312's 23 m15 tail-Y
  sites split sign (pos>0 and neg>0).
- H5_NULL4SPLIT (null columns split): pooled null-4
  (313/332/314/311) m15 tail-Y sites split sign (pos>0 and
  neg>0).
- H6_COLVAR (columns discriminate sign): per-column modal
  δ-sign varies across m15 tail-Y columns (≥1 column with
  n≥2 reads all-positive AND ≥1 column with n≥2 reads ≥1
  negative).
- H7_ABOVEBG (dec-1 above background): dec-1 pos share
  (1.0000) exceeds all three tabled shares: M19 m15
  P(δ>0)=0.8019, pooled off-51 pos share, dec-9 pos share.
- N (standing remainder + attribution): cell 7 after any
  attribution — the deliverable whatever the bars read
  (attribution, not explanation: N reads 0 explained with
  the tail standing, tabled).

Guards (stop-and-table, not bars): baseline R_0/fnv (s0 +
m15); R_s vs loo on s0; cell-7 counts 2475/2539 exact +
tail counts 102/134 exact with sub-bins 28+74 / 50+84 and
max 47/48; per-column membership (n, minrow, maxrow, sum δ)
exact per the M56 table below (all 9 cols incl. c341);
m58.txt bin guard: recomputed decbin m15 (per-bin n + δ
counts + min/max/sum + pos/neg) + hist4 m15 (per-decile
counts + n) + dec-1 site set {(row,col,δ)×12} vs `m58.txt`
lines AND vs the DESIGN pins above (mismatch → stop,
tabled); δ≠0 throughout cell 7; P(δ>0)==M19/M20 0.8093/
0.8019; tail planes Y/U/V 102/0/0 s0 + 134/0/0 m15
(non-Y tabled, census-gating disclosed); `loo.txt` 764 rows
+ top-10 shapes/shares; s0 P1 edges match m18.txt s0 row;
carrier removed counts + bands (M19 values); self Jaccard
== 1.0. Task 2 joins the measured values.

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

1. Input shas + `m58.txt` sha + Model-0 recompute +
   cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Bin-sign recompute + m58.txt/design guard (mismatch →
   stop); dec-1 site table; background table.
4. Column-sign table (33 union cols) + bin-column table +
   mode table.
5. Determinism re-run receipt (Task 1 on s0+m15,
   canonical sha).
6. PNG sign map (320x224, <5 MB total) to work dir:
   m15 tail-Y sites colored by (bin-1, sign) class (yellow
   = dec-1 pos; orange = dec-1 neg, expect 0; green =
   other-bin pos; red = other-bin neg; precedence yellow >
   orange > red > green); evidence copy ONLY if
   H3_DEC1UNIQUE10 meets (dec-1 the only bin with n≥10 at
   pos share 1.0000 — the pre-registered all-pos split) —
   else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 10:03 EDT, stop by 14:03).
