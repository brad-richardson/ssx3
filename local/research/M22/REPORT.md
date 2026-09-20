# M22 — Interior far-tail mechanism: locate + isolate the |δ|≥8 bytes: REPORT

M20 gap 1 closed at table level: the 102 s0 / 134 m15 tail bytes are
100% luma on both frames (and on all 764 M16 shapes), top-band-heavy
(67.6% s0 / 56.0% m15 in band 0 vs 25.4%/33.8% bulk), dec-9-heavy
(90.2%/82.8% vs 61.6%/63.9% bulk), scattered over 25/31 8-connected
components (largest 11/13 px: vertical streaks at rows 23–33 plus
mid-frame clusters), in essentially no top-10 carrier mask (max 1 B in 368's),
727/764 shape maps byte-identical to s0 (median Jaccard 1.0000) while
m15 shares 69/134 sites (Jaccard 0.4132), and in a different ρ regime
from the bulk (69.6%/63.4% in [0.4,0.5) vs the bulk's 43.8%/37.2% in
[0.3,0.4); sign agrees with the gap direction on 90.2%/89.6% vs
59.3%/60.4% bulk). Fully offline — no lease of any kind, no boots,
no harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M22.md`. Tables, no verdicts.

Headers read first: `local/research/M20/REPORT.md` (all of it: cell 7
= 2475 B s0 / 2539 B m15, |δ| hist [2127,127,119,28,74] s0 /
[2121,189,95,50,84] m15, max 47/48, all 102 s0 tail outside the 701
mask) plus M21's Task-1.1 map machinery (per-shape persistence +
Jaccard precedent: 518/764 byte-identical maps, median 1.0000).

Time box 4 hours (start 2026-09-20 02:05 EDT); used about 0.2. No
lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m21/` — all outputs went to the new
`/Volumes/Extreme SSD/m22/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15 triplet
(`m15-v0/mid/full.bin`, second sample). Work dir `/Volumes/Extreme
SSD/m22/`; evidence `local/research/M22/`.

Input shas (sha256 full, from the run receipt; s0 + m15 + 701
prefixes match M17/M18/M19/M20/M21):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m22.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M21 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m22.py` invocation (the receipt, 7.4 s, exit 0 — the
estimator was never changed); two `control.py` invocations (the
first failed N on a control-feasibility defect, tabled below —
not a result; the second is green).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m22.py receipt | 7.4 s | exit 0; all guards pass; canon `e3ab4f89…29cc4e7` |
| control.py run 1 (±20/cycled on bulk) | <1 s | superseded: C-T1 injected 2/60, C-T2 7/60 (see below) |
| control.py run 2 (pool fix) | <1 s | green; both controls pass exactly |

Defect (control feasibility: large gaps live on the tail
itself): rev-1 C-T1/C-T2 assumed bulk sites with gap≥50/32 were
plentiful enough for N=60 ±20/cycled injections, but the dumps
read bulk gap≥50: 2 sites, gap≥32: 7 (moved-exact gap≥50: 0) —
large gaps are almost exclusively tail sites (tail gap min 17,
mean 56.5/52.1). Fix: C-T1 injects checker ±8 (|δ|=8, the tail
boundary) on N=60 bulk sites with gap≥17 (248 candidates);
C-T2 injects cycled [+8,−12,+15] on N=60 ENDPOINT sites (moved,
mid at an endpoint, not cell 7) with gap≥32 (90 candidates).
Post-fix both recover 162/162 tail sets exactly with values +
maps. The `m22.py` receipt is unaffected (control-only defect;
the estimator never changed).

Per-stage wall (receipt run, sequential, no pool):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Task 1 (s0 + m15 locate incl. 6 BFS passes) | 2 | 0.8 s |
| Task 2.2 (764-shape tail pass) | 764 | 5.3 s |
| Task 2.1 + 2.3 (10 resynths + joins) | 10 | <1 s |
| Determinism re-run (Task 1 on s0) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m22.py` wall | — | 7.4 s |

## Step 2 — estimates

### Task 1 — locate (tail vs bulk side by side)

Cell-7 membership + tail membership recomputed from the dumps:
2475/2539 cell + 102/134 tail with sub-bins 28+74 / 50+84 and max
47/48 — M20's counts matched EXACTLY (stop rule not triggered).
δ==0 count reads 0; P(δ>0) reproduces M19/M20 0.8093/0.8019.

Plane split — the tail is all luma (bulk: 97.8%/94.2% Y):

| Frame | plane | tail n/share | tail range | tail mean/amean | bulk n | bulk mean/amean |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| s0 | Y | 102 / 1.0000 | [−45,+47] | 15.353 / 23.647 | 2319 | 0.491 / 1.305 |
| s0 | U | 0 / 0.0000 | — | — | 27 | −1.074 / 1.593 |
| s0 | V | 0 / 0.0000 | — | — | 27 | 1.222 / 1.222 |
| m15 | Y | 134 / 1.0000 | [−36,+48] | 12.388 / 20.582 | 2257 | 0.533 / 1.268 |
| m15 | U | 0 / 0.0000 | — | — | 88 | 0.432 / 1.409 |
| m15 | V | 0 / 0.0000 | — | — | 60 | 0.783 / 1.183 |

(Zero tail bytes on U/V on both frames; the 764-shape pass reads
0/764 shapes with any tail U/V — §Task 2.2.)

Band cut (M19 thirds verbatim; tail top-heavy, bulk mid-spread):

| Frame | unit | top | mid | bot |
| --- | --- | ---: | ---: | ---: |
| s0 | tail Y | 69 | 25 | 8 |
| s0 | bulk Y | 588 | 1261 | 470 |
| m15 | tail Y | 75 | 5 | 54 |
| m15 | bulk Y | 762 | 784 | 711 |

(Tail top share: 67.6% s0 / 56.0% m15; bulk: 25.4%/33.8%. m15
tail reads bimodal top+bottom with 5/134 mid-band.)

δ vs edge distance (Manhattan px to nearest static site, same
plane, M20 BFS verbatim; dmin=1 on tail and bulk by
construction; dmax 4 tail / 9+6 bulk):

| Frame | d | tail n/mean/amean | bulk n/mean/amean |
| --- | ---: | --- | --- |
| s0 | 1 | 56 / 11.98 / 23.66 | 1003 / 0.09 / 1.56 |
| s0 | 2 | 33 / 19.67 / 22.03 | 811 / 0.76 / 1.12 |
| s0 | 3 | 12 / 19.67 / 29.17 | 286 / 0.81 / 1.13 |
| s0 | 4 | 1 / 10.00 / 10.00 | 121 / 0.87 / 1.07 |
| s0 | 5+ | 0 | 98 / 0.93 / 1.01 |
| m15 | 1 | 70 / 6.64 / 17.53 | 1091 / 0.35 / 1.44 |
| m15 | 2 | 51 / 17.88 / 23.45 | 889 / 0.77 / 1.11 |
| m15 | 3 | 11 / 24.00 / 28.73 | 222 / 0.44 / 1.12 |
| m15 | 4 | 2 / 9.50 / 9.50 | 42 / 0.74 / 1.21 |
| m15 | 5+ | 0 | 13 / 0.62 / 1.08 |

(Tail d≤2 share: 87.3% s0 / 90.3% m15; bulk: 78.2%/87.7%.
Tail+bulk d-bins sum to M20's all-interior rows exactly:
1059/844/298/122/98 s0-Y. U/V tail rows read n=0 — in
`m22.txt`.)

(dr,dc) component cross (s0 tail-Y n; column-dominated like the
bulk: dr=0 row holds 76/102 = 74.5%; bulk 64.6%):

| dr\\dc | 0 | 1 | 2 | 3+ |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0 | 53 | 17 | 6 |
| 1 | 3 | 9 | 3 | 0 |
| 2 | 7 | 3 | 0 | 0 |
| 3+ | 1 | 0 | 0 | 0 |

(m15 tail cross + per-cell means + bulk crosses in `m22.txt`;
m15 tail dr=0 row holds 95/134 = 70.9%.)

δ vs M18-P1 gradient decile (M18 code verbatim; rounded edges
match m18.txt exactly on both frames — guard OK). Tail vs bulk
Y bytes per decile (n / mean δ / mean |δ|):

| dec | s0 tail | s0 bulk |
| ---: | --- | --- |
| 0–5 | 0 | 5/13/0/21/44/54 (means +0.3…+0.9) |
| 6 | 2 / 10.00 / 10.00 | 121 / 0.61 / 1.21 |
| 7 | 2 / −14.00 / 23.00 | 179 / 0.64 / 1.37 |
| 8 | 6 / 13.33 / 16.00 | 454 / 0.19 / 1.42 |
| 9 | 92 / 16.24 / 24.46 | 1428 / 0.53 / 1.29 |

| dec | m15 tail | m15 bulk |
| ---: | --- | --- |
| 0–3 | 0 | 4/4/12/23 |
| 4 | 2 / 15.50 / 15.50 | 32 / 0.91 / 1.34 |
| 5 | 3 / −1.67 / 10.33 | 58 / 0.88 / 1.33 |
| 6 | 3 / 19.00 / 19.00 | 73 / 0.75 / 1.47 |
| 7 | 6 / 4.50 / 16.83 | 206 / 0.39 / 1.34 |
| 8 | 9 / 11.78 / 16.67 | 403 / 0.08 / 1.42 |
| 9 | 111 / 13.01 / 21.51 | 1442 / 0.64 / 1.20 |

(Dec-9 share: tail 90.2% s0 / 82.8% m15; bulk 61.6%/63.9%.
Tail+bulk per-decile n sums to M20's rows exactly. U/V tail
n-by-dec reads all zeros both frames — in `m22.txt`.)

Region — connected components of tail-Y sites (scattered
singles + vertical streaks, no dominant region):

| Frame | conn | comps | sizes 1/2/3–4/5–8/9+ | largest (share) |
| --- | --- | ---: | ---: | ---: |
| s0 | 4 | 26 | 10/3/5/3/5 | 11 (0.1078) |
| s0 | 8 | 25 | 9/3/5/3/5 | 11 (0.1078) |
| m15 | 4 | 35 | 9/6/8/8/4 | 11 (0.0821) |
| m15 | 8 | 31 | 8/6/6/5/6 | 13 (0.0970) |

s0 8-conn sizelist: `11 10 10 10 10 7 5 5 4 4 4 4 3 2 2 2 1×9`.
m15 8-conn sizelist: `13 11 10 10 10 9 6 6 5 5 5 4×6 2×6 1×8`.
U/V sizelists read empty both frames.

Components ≥5 px (Y, 8-conn; the top streak columns recur on
both frames):

| Frame | size | centroid (r,c) | bbox |
| ---: | ---: | ---: | --- |
| s0 | 11 | (28.0,301.0) | r[23,33]c[301,301] |
| s0 | 10 | (275.4,314.1) | r[273,278]c[313,315] |
| s0 | 10 | (27.5,321.0) | r[23,32]c[321,321] |
| s0 | 10 | (27.5,277.0) | r[23,32]c[277,277] |
| s0 | 10 | (27.5,257.0) | r[23,32]c[257,257] |
| s0 | 7 | (298.6,311.4) | r[296,301]c[311,312] |
| s0 | 5 | (27.4,342.4) | r[26,29]c[342,343] |
| s0 | 5 | (26.0,296.0) | r[24,28]c[296,296] |
| m15 | 13 | (338.1,313.7) | r[333,343]c[312,315] |
| m15 | 11 | (28.0,301.0) | r[23,33]c[301,301] |
| m15 | 10 | (27.5,321.0) | r[23,32]c[321,321] |
| m15 | 10 | (27.5,277.0) | r[23,32]c[277,277] |
| m15 | 10 | (27.5,257.0) | r[23,32]c[257,257] |
| m15 | 9 | (319.0,311.3) | r[316,322]c[310,312] |
| m15 | 6 | (364.5,312.0) | r[362,367]c[312,312] |
| m15 | 6 | (27.0,342.5) | r[25,29]c[342,343] |
| m15 | 5 | (378.2,312.4) | r[377,379]c[312,313] |
| m15 | 5 | (26.0,340.0) | r[24,28]c[340,340] |
| m15 | 5 | (26.0,296.0) | r[24,28]c[296,296] |

(The r23–33 single-column streaks at c257/277/296/301/321/340–343
read on both frames with identical bboxes; the lower clusters
differ: s0 r273–301 vs m15 r316–379 around c310–315.)

### Task 2 — isolate (distinct population or smooth tail?)

Carrier cut — tail bytes inside each top-10 removed mask
(removed counts + bands reproduce M18/M19 exactly — guards OK;
U/V via co-located Y (r,2c)):

| rank | shape | nrem | s0tailY in | Y share | s0tailU in | s0tailV in |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 694 | 4888 | 0 | 0.0000 | 0 | 0 |
| 2 | 693 | 1208 | 0 | 0.0000 | 0 | 0 |
| 3 | 701 | 649 | 0 | 0.0000 | 0 | 0 |
| 4 | 368 | 448 | 1 | 0.0098 | 0 | 0 |
| 5 | 369 | 248 | 0 | 0.0000 | 0 | 0 |
| 6 | 366 | 244 | 0 | 0.0000 | 0 | 0 |
| 7 | 370 | 191 | 0 | 0.0000 | 0 | 0 |
| 8 | 376 | 174 | 0 | 0.0000 | 0 | 0 |
| 9 | 748 | 190 | 0 | 0.0000 | 0 | 0 |
| 10 | 750 | 202 | 0 | 0.0000 | 0 | 0 |

(Max tail-Y share 0.0098 — no carrier concentrates the tail.
701 holds 0 tail bytes: inside/outside-701 split below.)

Inside/outside-701 split (s0 interior Y; guards OK: removed 649
Y px, interior-in-mask 367 — M18/M19 values reproduced):

| cut | n | mean δ | mean |δ| | pos/neg |
| --- | ---: | ---: | ---: | ---: |
| tail inside | 0 | — | — | 0/0 |
| tail outside | 102 | 15.353 | 23.647 | 81/21 |
| bulk inside | 367 | −0.967 | 2.226 | 222/145 |
| bulk outside | 1952 | 0.765 | 1.132 | 1667/285 |

(Bulk-inside row reproduces M20's inside cut exactly
(−0.967/2.226, dhist `−7:33 … 6:1`). Tail-outside dhist spans
the full [−45,+47] range — in `m22.txt`.)

Cross-shape persistence (M21 Task-1.1 machinery verbatim,
s0-anchored like M21):

Per-shape tail counts (764 M16 triplets; R_s recompute matches
`loo.txt` on 764/764, 0 mismatches; full 764-row table in
`m22.txt`; every shape's tail reads 100% Y):

| Field | min | med | mean | max |
| --- | ---: | ---: | ---: | ---: |
| tail bytes | 94 | 102 | 102.0 | 117 |

Map overlap (Jaccard of byte sets; printed 1.0000 ⟹
byte-identical: a one-byte diff on 102 B reads 101/103 =
0.9806):

| Field | min | med | mean | max |
| --- | ---: | ---: | ---: | ---: |
| J(T_t, T_s0) all 764 | 0.6694 | 1.0000 | 0.9973 | 1.0000 |
| J(T_t, T_s0) t≠0 | 0.6694 | 1.0000 | 0.9973 | 1.0000 |
| J(T_t, T_m15) | 0.2581 | 0.4132 | 0.4124 | 0.4182 |

727/764 shapes read byte-identical maps to s0 (t=0 included);
below 0.99: 22 shapes; below 0.95: 9. J(T_s0, T_m15) = 0.4132
(inter 69, union 167).

Below-0.95 rows (shape, tail B, Jaccard):

| shape | tail | J vs s0 |
| ---: | ---: | ---: |
| 733 | 100 | 0.6694 |
| 731 | 100 | 0.6833 |
| 9 | 117 | 0.7520 |
| 700 | 114 | 0.8462 |
| 734 | 94 | 0.8846 |
| 732 | 95 | 0.8942 |
| 2 | 103 | 0.9159 |
| 711 | 95 | 0.9314 |
| 3 | 103 | 0.9340 |

Per-site persistence occ[o] = #{t : o ∈ T_t} over 764 shapes:

| Population | 0 | 1 | 2–3 | 4–7 | 8–15 | 16–63 | 64–763 | 764 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all offsets | 573234 | 95 | 8 | 0 | 1 | 0 | 87 | 15 |
| T_s0 sites | 0 | 0 | 0 | 0 | 0 | 0 | 87 | 15 |
| T_m15 sites | 64 | 1 | 0 | 0 | 0 | 0 | 69 | 0 |

Max occ = 764 (15 sites). T_s0 sites: mean occ 762.9, ≥50% on
102/102. T_m15 sites: mean occ 392.9, ≥50% on 69/134. (The 206
offsets ever tail = 95+8+1+87+15; the 69 recurring T_m15 sites
are the T_s0 ∩ T_m15 set — tabled as measured.)

δ-shape join — tail |δ| vs (v0−full) gap (ρ = δ/|gap|; tail in
a different ρ regime from the bulk):

| Frame | pop | gap min/med/mean/max | gap hist 2–3/4–7/8–15/16–31/32–63/64+ |
| --- | --- | ---: | --- |
| s0 | tail | 17/58/56.5/115 | 0/0/0/22/40/40 |
| s0 | bulk | 3/4/6.8/87 | 1025/741/322/278/6/1 |
| m15 | tail | 17/48/52.1/106 | 0/0/0/24/72/38 |
| m15 | bulk | 3/5/7.2/76 | 856/861/405/261/19/3 |

| Frame | pop | max|ρ| | mean|ρ| | ρ hist [−0.5..0.5/0.1] |
| --- | --- | ---: | ---: | --- |
| s0 | tail | 0.4945 | 0.4223 | [17, 3, 0, 1, 0, 0, 1, 1, 8, 71] |
| s0 | bulk | 0.4667 | 0.2489 | [2, 104, 168, 93, 84, 254, 236, 346, 1040, 46] |
| m15 | tail | 0.4906 | 0.4041 | [21, 5, 0, 10, 0, 0, 3, 5, 5, 85] |
| m15 | bulk | 0.4545 | 0.2363 | [7, 72, 200, 101, 87, 287, 281, 431, 894, 45] |

(Tail+bulk ρ hists sum to M20's all-interior rows exactly on
both frames. Tail [0.4,0.5) share: 69.6% s0 / 63.4% m15; bulk
[0.3,0.4) share: 43.8%/37.2%. The <0.5 guard holds on tail and
bulk.)

δ sign vs (v0−full) sign joint table on the tail (d=v0−full,
o=δ; tail sign agrees with the gap direction on 90.2%/89.6% vs
59.3%/60.4% bulk):

| Frame | pop | d>0/o>0 | d>0/o<0 | d<0/o>0 | d<0/o<0 | P(o>0) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| s0 | tail | 78 | 7 | 3 | 14 | 0.7941 |
| s0 | bulk | 1082 | 125 | 840 | 326 | 0.8099 |
| m15 | tail | 97 | 13 | 1 | 23 | 0.7313 |
| m15 | bulk | 1123 | 137 | 815 | 330 | 0.8058 |

(Tail P(o>0|d>0) = 0.9176/0.8818 vs P(o>0|d<0) =
0.1765/0.0417; bulk 0.8964/0.8913 vs 0.7204/0.7118. Tail+bulk
joint cells sum to M20's rows exactly.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-T1 (±8 checker, N=60, gap≥17 bulk) | 162 sites, set exact, values exact, cell fixed | exact | True |
| C-T2 ([+8,−12,+15], N=60, gap≥32 endpoint) | 162 sites, set exact, cell exact, values exact | exact | True |

(Both pass on the fixed control code; run-1 C-T1/C-T2 injected
2/7 on the infeasible pool — §Runs. C-T1: +8×29/−8×31;
C-T2: +8×20/−12×20/+15×20; injected disjoint from the
original tail/cell; original members' δ unchanged.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0) pass1 `e3ab4f89…29cc4e7` vs pass2
`e3ab4f89…29cc4e7`, identical=True; cell counts identical=True;
tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; brief names no tail-value rule,
so N reads the no-rule row):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | ---: |
| m16 s0 | 0 blend (tail stands) | 2475 | 0 | 0.0000 |
| m15 | 0 blend (tail stands) | 2539 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_POS | \|tail−bulk dec-9\| ≥ 0.25 or \|tail−bulk d≤2\| ≥ 0.25 (s0-Y) | 0.2862 (decile leg) / 0.0903 (edge leg) — met on decile leg |
| H2_PLANE | tail Y share ≤ 0.75 on s0 | 1.0000 (m15: 1.0000) — not met |
| H3_REGION | largest s0 8-conn tail comp ≥ 0.50 of tail-Y | 0.1078 (m15: 0.0970) — not met |
| H4_CARRIER | some top-10 mask ≥ 0.50 of s0 tail-Y | max 0.0098 (368) — not met |
| H5_PERSIST | median J(T_t,T_s0) over t≠0 ≥ 0.50 | 1.0000 (727/764 byte-identical) — met |
| H6_RHO | \|tail−bulk ρ[0.3,0.4)\| ≥ 0.25 on s0 | 0.3599 (m15: 0.3344) — met |
| N | cell 7 after best tail rule + remaining split | 0 explained; 102/134 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
plane (100%/100% Y tail vs 97.8%/94.2% bulk — more luma, not
less), by band (67.6%/56.0% top-band vs 25.4%/33.8% bulk), by
gradient decile (90.2%/82.8% dec-9 vs 61.6%/63.9% bulk), by
edge distance only weakly (87.3%/90.3% at d≤2 vs 78.2%/87.7%
bulk), and by region only as scatter (25/31 8-conn comps,
largest 11/13 px — no dominant region, but the r23–33 streak
columns recur on both frames). Task 2 discriminates by carrier
negatively (max 1 B in any top-10 mask; 701 holds 0), by map
identity (727/764 byte-identical to s0; 9 shapes below 0.95,
min 0.6694) and by sample (m15 Jaccard 0.4132 vs ≥0.95 for
755/764 M16 shapes), by gap (tail min 17, mean 56.5/52.1 vs
bulk min 3, mean 6.8/7.2), by ρ regime (tail 69.6%/63.4% in
[0.4,0.5) vs bulk 43.8%/37.2% in [0.3,0.4)), and by sign-gap
agreement (90.2%/89.6% vs 59.3%/60.4% bulk).

Updated deliverable — explained vs standing remainder:

| Content | Bytes (m16 s0) | Behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (M16, unchanged) |
| endpoint-max component | 17089 of R_0 (74.9%) | mid==bright endpoint (M19, unchanged) |
| endpoint-min component | 662 of R_0 (2.9%) | mid==dark endpoint (M19, unchanged) |
| moved-outside component | 221 of R_0 (1.0%) | 159 above / 62 below (M19, unchanged) |
| static-site residual | 2368 of R_0 (10.4%) | v0==full≠mid (M19/M21, unchanged) |
| interior ±1 mass | 2127 of cell 7 (86.0%) | δ=±1 (M20, unchanged) |
| interior mid band 2–7 | 246 of cell 7 (9.9%) | 127 + 119 (M20, unchanged) |
| interior far tail | 102 of cell 7 (4.1%) | \|δ|≥8, max 47; 100% Y; stands (this run) |
| standing interior remainder | 2475 of cell 7 (100%) | no tail rule; locate/isolate tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B tail-explained; rest split above |

Screenshot (committed): `m22-tailmap.png` 93171 B (dimmed
truth + interior Y px colored by bulk/tail × δ sign: red/blue
bulk spread over rider glow, god-ray shafts and slopes,
yellow/magenta tail clustered at the top band — score digits,
peak-ridge streaks, and the tower-top column). The map
discriminates spatially (tail separates by region, matching
the 67.6% top-band table), so it is included. Total 93171 B
(budget 5242880).

Recorded without verdict: the tail is 102/134 bytes (4.1%/5.3%
of cell 7) at 100% luma with nothing on chroma on any of 764
shapes; top-band- and dec-9-heavy beyond the bulk; scattered
over 25/31 small components whose top streak columns recur on
both frames; in no carrier mask; 727/764 maps byte-identical
to s0 with m15 at Jaccard 0.4132; at gaps ≥17 (mean ~54) with
ρ peaking in [0.4,0.5) and sign agreeing with the gap
direction on ~90%; no tail rule shrinks cell 7.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| tail suite + \|δ\|≥8 definition + falsification bars, recorded before running | recorded | `DESIGN.md`: tail/bulk plane split, band/BFS/P1 joins, 4/8-conn regions, 10-carrier cut + 701 split, 764-shape Jaccard/persistence, gap/ρ/sign joins, bars H1–H6/N |
| locate + isolate tables + wall/exit/shas/determinism | measured | §Step 2: plane/band/edge/decile/region tables both frames; carrier + persistence + ρ tables; 7.4 s; re-run identical |
| explained-vs-standing update (does any tail rule shrink cell 7? by how much?) + gap rows | measured | §Step 3: no tail rule, 0 explained; 102/134 stands; gaps below |
| screenshot if a tail map discriminates (or absence reasoned) | measured | 1 PNG, 93171 B: bulk/tail δ-sign map, top-band-separated, spatially discriminating |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
cp local/research/M22/m22.py local/research/M22/control.py "/Volumes/Extreme SSD/m22/"
python3 m22.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m22" /Users/bradrichardson/dev/ssx3/local/research/M22 > m22.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M22/` — `DESIGN.md`
(suite + bars, recorded before running), `m22.py` (locate +
BFS edge + P1 join + regions + carrier cut + 764-shape pass +
ρ join + PNG writer), `control.py` (2 synthetic tail-injection
controls, rev 2), `REPORT.md` (this file), `m22-tailmap.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m22/` —
`m22.txt` (receipt: shas, baselines, Task-1 locate tables both
frames, 764-row tail table, carrier + 701 splits, ρ joins,
re-run, PNG size), `control.txt`, `m22.py`, `control.py`
(working copies), `m22-tailmap.png` (working copy). No writes
into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Tail value mechanism (new): 102/134 tail δ values
   unattributed at value level (ρ≈0.42 regime, sign follows
   the gap on ~90%, gaps ≥17). Needs its own brief: per-site
   (gap, position, carrier) value tables + predictor fits,
   offline — no new harness code.
2. Shape-733 tail divergence (new): shape 733's tail map reads
   Jaccard 0.6694 vs s0 (100 B) while 727/764 shapes read
   byte-identical (731 next-lowest at 0.6833). Needs its own
   brief: per-byte attribution of 733's private sites (tail-set
   change vs δ change), offline — no new harness code.
3. m15 private tail sites (new): 64/134 m15 tail sites never
   recur on any M16 shape (occ 0; Jaccard 0.4132). Needs its
   own brief only if cross-sample tail identity matters:
   second-sample tail family, offline — no new harness code.
4. Shape-700 map divergence (M21 gap 1, still open): shape
   700's static map reads Jaccard 0.0747 vs s0 while 518/764
   read byte-identical. Needs its own brief: per-byte
   attribution of 700's private sites, offline — no new
   harness code.
5. m15 static-map disjointness (M21 gap 2, still open): m15
   shares 92/1476 static sites with s0 (Jaccard 0.0245).
   Needs its own brief only if cross-sample map identity
   matters, offline — no new harness code.
6. U/V co-residual mechanism (M21 gap 3, still open): same-pixel
   U&V co-residual reads 16.0×/21.6× independence. Needs its
   own brief only if chroma pairing matters, offline — no new
   harness code.
7. δ-sign mechanism (M20 gap 2, still open, minor): δ>0 on
   80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈
   0.70 on both frames. Needs its own brief only if the sign
   asymmetry matters, offline — no new harness code.
8. m15 below-min far tail (M19 gap 3, still open, minor): 4
   below-side bytes with dout ≥ 16 (max 47) on m15. Needs its
   own brief only if outlier isolation matters, offline — no
   new harness code.
9. Negative-share mechanism (M18 gap 2, still open): 93
   negatives (worst −244) unattributed at byte level. Needs
   its own brief: per-shape added-residual maps + EFB-copy
   diffing, offline — no new harness code.
10. Odin port readiness (M18 gap 3, still open): no Odin
    contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
11. Top-HUD glyph residual isolation (M18 gap 4, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
12. Per-carrier weight centers (M18 gap 5, still open,
    optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers
    matter.

## What I could not do

1. No per-shape tail-δ value comparison: the 764-shape pass
   compares tail maps only; δ values are s0 + m15.
2. No tail-value predictor attempted: the brief names no
   tail-value rule, so N reads the no-rule row (0 explained).
3. U/V-native gradient join: P1 deciles are Y-native (M18
   verbatim); U/V tail reads n=0 everywhere, so the
   secondary join rows are all zeros — tabled, not chased.
4. Independent verification probes (`/tmp/m22_pool_probe.py`,
   `/tmp/m22_pool_probe2.py`: control-pool sizing) are
   throwaway by rule — kept under `/tmp`, not committed.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M22/`: `DESIGN.md`, `m22.py`,
`control.py`, `REPORT.md` (this file), `m22-tailmap.png`
(93171 B total).

