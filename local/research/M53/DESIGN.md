# M53 — Design (recorded before running)

Goal: index-top argmax concentration (M26 gap 3): 6/8 s0 + 5/8 m15
argmax read top-third by index under the first-tie rule; plateau
peaks: c257's 29x4 run, c340's twin 47s. Plateau-aware peak tables:
all-tie rows (every row attaining column max) per column per frame
+ run-center rules + thirds + peak-row agreement RECOMPUTED under
run-center (does 6/8+5/8 top-third survive? does 5/8 agreement
survive?). Answer by table. Tables, no verdicts. Fully offline: no
lease of any kind, no boots, no harness runs, no fork changes, no
`adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m25/m25.txt` (column profiles to
reproduce: per-column row->d lists + shape stats — match exactly
or table the mismatch and stop), `/Volumes/Extreme SSD/m26/m26.txt`
(hump lines + xshape lines to reproduce — match exactly or table
the mismatch and stop). Work dir: `/Volumes/Extreme SSD/m53/`
(new). Evidence: `local/research/M53/` (committed with `git add -f`,
prefix `[M53]`, trailer `Orchestrated-By: Muse Code`; NEVER
`git push` in ssx3).

Headers read first: `local/research/M26/REPORT.md` (all of it: hump
table 8x2 peaks/thirds, 6/8 s0 + 5/8 m15 top-third, 5/8 peak
agreement, TRI p/h/e/w, c257's 29x4 run + c340's twin 47s) plus
`local/research/M25/REPORT.md` (all of it: the 32 profile lines —
row->d lists with holes — plus CONST collapse + peak-anchored
method) plus `local/research/M51/REPORT.md` (TRI p values cited in
Task 2.3, not refit).

## Estimator (`m53.py`, `control.py`)

Shared core (M26 `m26.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `fnv1a`, `parse_loo`, `plane_of_byte`,
`plane_coords`, `jaccard`, `int_median` (halves away from zero),
`coarse_hist`, `exact_counts`, `hole_ranges`, `count_runs`,
`hump_metrics` (first-tie argmax + thirds), `task1_profile_lines`
(incl. hump lines), `m25_match_lines`, `xshape_lines`. Byte offset
o -> row o//1280; Y bytes at o%4==0/2. No P1 carrier machinery (no
POS/carrier task here). `quadfit`/`trifit`/`twolevel` unused here
(no refits — TRI p cited from M51, not refit).

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- d = mid - blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so d!=0
  throughout (guard).
- Bulk = cell-7 bytes with |d|<8 (want 2373 s0 / 2405 m15).
  Tail = cell-7 bytes with |d|>=8 (want 102 s0 / 134 m15; s0
  sub-bins 28 in 8-15 + 74 in 16+, m15 50 + 84; max 47/48).
- Named columns (profiles + peaks): c in
  {257,277,296,301,321,340,342,343} (the brief's 8; c341 is
  membership-guarded but not profiled/scored: 0 s0 / 1 m15
  sites). Column membership = all tail-Y sites with Y-column
  == c. Named-column tail bytes: want 65 s0 / 68 m15 (implied
  by the per-column guard rows).

Rounding convention (fixed): round-half-away-from-zero;
integer paths exact, float paths via
rhalf(x)=sign(x)*floor(|x|+0.5).

### Tie + plateau definitions (Task 1, pinned, no special-casing)

Per named column per frame, over present rows in row order
(r[0..n-1] ascending, d[0..n-1]):

- colmax = max d. All-tie rows = every present row with
  d == colmax, ascending. T = tie count.
- Max-tie runs = maximal runs of all-tie rows consecutive in ROW
  NUMBER (adjacent rows differ by 1 — a hole breaks a run).
- Tie shape: singleton (T==1) / run (T>1, exactly one run) /
  scattered (T>1, every run has L==1) / multirun (T>1, >=2 runs
  with at least one L>=2).
- Submax plateau census (auxiliary, pinned — captures the named
  c257 29x4 case which sits at max-1): maximal equal-d runs with
  L>=2 over present rows in row order, consecutive in ROW NUMBER
  (hole breaks a run), any value. Tabled as start-end:valxL
  (`;`-joined, `none` when empty).
- First-tie peak = M26 `hump_metrics` verbatim (argmax, FIRST on
  ties; thirds by index k: top if 3k<n, bottom if 3k>=2n, else
  mid). Same formulas all 8 columns both frames, including
  ragged (c296/340) and negative (c342/343) columns.

### Run-center rules (Task 2, pinned)

- R1 middle-of-longest-run (PRIMARY): longest maximal max-tie
  run; ties between equal-length runs -> smallest starting row;
  peak = run[(L-1)//2] (lower-middle for even L). Thirds by the
  index of that row in present rows (same thirds formula).
- R2 mean-of-ties (AUXILIARY): mean of all-tie rows, rounded
  half-away (rhalf); the R2 row may be absent/holed — tabled
  as-is with present=True/False. Thirds by rank
  k' = #{present rows < R2} with the same 3k'/n formula.
- Agreement under run-center: per column, R1 peak row s0 vs m15
  equal? (primary) + R2 peak row s0 vs m15 equal? (auxiliary).
- TRI-p impact (Task 2.3): M51's TRI p values CITED, not refit
  (s0: 25,25,26,27,25,26,27,27; m15: 25,25,26,27,26,32,27,289
  for c257..c343 in order). p-impact = (R1 peak != cited p)?
  per column per frame (+ R2 likewise, auxiliary). Citation
  check: cited p must equal recomputed first-tie peak on all 16
  column-frames or table the mismatch and stop Task 2.3 only
  (Tasks 1/2.1/2.2 already tabled stand).

### Task 1 — first-tie reproduction + all-tie rows (what ties?)

Column profiles recomputed from the dumps; row->d lists + shape
stats must match M25 exactly AND hump lines + xshape lines must
match M26 exactly, or table the mismatch and stop (no further
tasks run). Match checks: the `prof` (rowdelta + holes) and
`shape` (stats + roworder) receipt lines, emitted in M25-identical
format by the verbatim core, must equal the corresponding `m25.txt`
lines byte-exactly; the `hump` + `xshape` receipt lines, emitted in
M26-identical format by the verbatim core, must equal the
corresponding `m26.txt` lines byte-exactly.

1. First-tie table: all 8 columns x s0/m15 peak/third (16 rows
   reproduced; thirds pooled top/mid/bottom per frame).
2. All-tie table: every row attaining column max per column per
   frame (tie counts + rows). Receipt: `{tag} tie c={c}:
   max={m} T={t} rows=[...]`.
3. Tie-shape table: per column per frame tie pattern (singleton /
   run / scattered / multirun + run lengths) + submax plateau
   census. Receipt: `{tag} tieshape c={c}: shape={s} nruns={n}
   runlens=[...]` + `{tag} plateau c={c}: nruns={n} runs={...}`.

### Task 2 — run-center rules (does top-third survive?)

1. Run-center table: peak recomputed as run center per column per
   frame (R1 primary + R2 auxiliary) + thirds under run-center.
   Receipt: `{tag} rc1 c={c}: peak={r} k={k}/{n} third={t}
   moved={b}` + `{tag} rc2 c={c}: peak={r} present={b}
   k={k'}/{n} third={t} moved={b}` (moved = peak != first-tie
   peak row) + pooled thirds lines per rule per frame.
2. Agreement table: peak-row agreement under run-center (R1
   primary + R2 auxiliary). Receipt: `rcagree R1 c={c}:
   s0={r} m15={r} equal={b}` + pooled `rcagree R1 pooled:
   agree={a}/8` (same for R2).
3. Plateau table: c257's 29x4 + c340's twins under first-tie vs
   run-center (peak rows + thirds + TRI-p impact — M51's p values
   cited, not refit). Receipt: `trip c={c} {tag}: p_cited={p}
   rc1={r} pimpact={b} rc2={r} pimpact2={b}` per column per frame
   (16 lines; plateau columns c257/c340 foregrounded in REPORT).

### Task 3 — controls + determinism (M18–M52 precedent)

`control.py` (imports `m53` tie/rule core; expectations analytic;
pure-synthetic row->d lists, NOT dump-injected — deviation reasoned:
tie + run-center logic operates on row->d lists, so synthetic lists
exercise the identical code path with zero dump coupling):

- C-P1: synthetic truth with KNOWN plateaus, N=2 singleton + N=2
  run + N=2 scattered-tie pseudo-columns; recover the first-tie +
  all-tie + run-center tables exactly. Listed profiles (rows asc):
  - S1 (singleton): rows 20..24, d = 10 14 18 14 10. Want:
    first-tie r22 (k=2/5 mid), alltie [22], shape singleton,
    census none, R1 r22 mid, R2 22 mid.
  - S2 (singleton, negative): rows 40,41,42, d = -20 -12 -15.
    Want: first-tie r41 (k=1/3 mid), alltie [41], shape
    singleton, census none, R1 r41 mid, R2 41 mid.
  - R1 (run, odd): rows 50..54, d = 9 15 15 15 11. Want:
    first-tie r51 (k=1/5 top), alltie [51,52,53], shape run,
    census 51-53:15x3, R1 r52 (k=2/5 mid), R2 52 mid.
  - R2 (run, even): rows 60..64, d = 8 12 20 20 12. Want:
    first-tie r62 (k=2/5 mid), alltie [62,63], shape run,
    census 62-63:20x2, R1 r62 lower-middle (k=2/5 mid),
    R2 rhalf(62.5)=63 (present, k'=3/5 mid).
  - T1 (scattered): rows 70,71,75,76, d = 30 22 30 25. Want:
    first-tie r70 (k=0/4 top), alltie [70,75], shape scattered,
    census none, R1 r70 first-run (k=0/4 top), R2 rhalf(72.5)=73
    (absent, k'=2/4 mid).
  - T2 (multirun): rows 80..85, d = 40 40 31 40 40 33. Want:
    first-tie r80 (k=0/6 top), alltie [80,81,83,84], shape
    multirun, census 80-81:40x2;83-84:40x2, R1 r80 first-run
    lower-middle (k=0/6 top), R2 rhalf(82.0)=82 (present,
    k'=2/6 mid).
  - Pass = first-tie + alltie + shape + census + R1 + R2 +
    thirds(x3 rules) exact on all 6 pseudo-columns.

Determinism: re-run Task 1 on s0+m15 (cell-7 + tail recompute +
profiles + humps + ties + shapes + census both frames);
canonical-text sha + counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
m25.txt + m26.txt. Model-0 recompute: R_0/fnv must match M17–M52
(22815/13418, `6b9ffda25bd76c6f` / `306b5c778898b64a`). Mismatch =
stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_MULTITIE (ties are common): >=4/16 column-frames carry >1
  max-tie row.
- H2_RUNMOVE (run-center moves peaks): under R1, >=1/16 peak rows
  differ from the first-tie peak row.
- H3_TOPTHIRD (top-third survives run-center): under R1, top-third
  share >= 0.50 on s0 AND on m15 (>=4/8 each).
- H4_AGREE (agreement survives run-center): under R1, peak-row
  agreement >= 4/8.
- H5_SINGLERUN (multi-ties form one run): among column-frames with
  T>1, the share with a single max-tie run is >= 0.50.
- H6_SUBMAX4 (named submax plateau recovered): the submax census
  recovers an equal-d run of length >=4 on s0 c257.
- H7_TRIP (TRI p convention-stable): cited M51 TRI p equals the R1
  run-center peak row on >=14/16 column-frames.
- N (standing remainder + tie/rule tables): tie + rule tables +
  named-col tail after M26 TRI hits (18/16 explained, 0 new —
  attribution, not explanation) + remaining split — the
  deliverable whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48; per-column membership
(n, minrow, maxrow, sum d) exact per the M25 table below;
M25 profile-line match (prof/shape lines byte-exact vs
`m25.txt`); M26 hump-line match (16 hump lines byte-exact vs
`m26.txt`) + xshape-line match (8 + pooled byte-exact vs
`m26.txt`); M51 p-citation check (Task 2.3 only); d!=0 throughout
cell 7; P(d>0)==M19/M20 0.8093/0.8019; `loo.txt` 764 rows +
top-10 shapes/shares; self Jaccard == 1.0.

Per-column guard table (n / rows / sum d; mean=sum/n):

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

M51 cited TRI p (Task 2.3 citation, not refit):

| col | s0 p | m15 p |
| ---: | ---: | ---: |
| 257 | 25 | 25 |
| 277 | 25 | 25 |
| 296 | 26 | 26 |
| 301 | 27 | 27 |
| 321 | 25 | 26 |
| 340 | 26 | 32 |
| 342 | 27 | 27 |
| 343 | 27 | 289 |

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48) + column-membership guard (table above or stop).
3. Task 1: per-row d lists + holes; shape stats; M25
   profile-line match guard (mismatch -> stop); hump metrics;
   M26 hump+xshape match guard (mismatch -> stop); all-tie rows;
   tie shapes; submax census.
4. Task 2: R1/R2 peaks + thirds; agreement under run-center;
   M51 p-citation check (mismatch -> stop Task 2.3 only);
   TRI-p impact.
5. Determinism re-run receipt (Task 1 on s0+m15, canonical sha).
6. PNG plateau map (320x224, <5 MB total) to work
   dir, s0 named-column sites colored by tie status
   (max-tie run-member / singleton-or-scattered max-tie /
   other); evidence copy ONLY if some s0 named column with n>=8
   reads R1 peak row != first-tie peak row (a plateau visible in
   a specific pre-registered-split column) — else absence
   reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 07:27 EDT, stop by 11:27).
