# M19 — Endpoint-direction split on the M18 residual: REPORT

M18 gap 1 closed at table level: on the 17751 endpoint residual
bytes mid reads the BRIGHTER endpoint 96.3% of the time (s0;
92.7% on m15); moved-outside bytes split 159 above / 62 below
(s0); 2368 raw residual bytes sit on static sites (s0; 1476 on
m15), whose Y subset is exactly P4's 463/439 px. Fully offline —
no lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M19.md`. Tables, no
verdicts.

Headers read first: `local/research/M18/REPORT.md` (all of it:
the 22815-B remainder, 77.8% endpoint + 91.7%/86.5%
synth<truth marginals, P4 463/439 static-site Y px, Test C
carrier behavior) plus the M16 carrier table (effect draws
694/693/701 vs HUD draws, per-draw context).

Time box 4 hours (start 2026-09-20 01:26 EDT); used about 0.5.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`, `m18/` — all outputs went to the
new `/Volumes/Extreme SSD/m19/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15 triplet
(`m15-v0/mid/full.bin`, second sample). Work dir
`/Volumes/Extreme SSD/m19/`; evidence `local/research/M19/`.

Input shas (sha256 full, from the run receipt; s0 + m15
prefixes match M17/M18):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m19.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17/M18 exactly.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

Three `m19.py` invocations, one receipt. The first run is
superseded (estimator defect, tabled below — not a result); the
second and third runs are both green with identical canon text
— the third is the receipt (`m19.txt`, 37.2 s, exit 0).

| Invocation | Wall | Standing |
| --- | --- | --- |
| run 1 (band-share `int()` truncation) | 31.3 s | superseded: concentration rows read 0.0000 (see below) |
| run 2 (float-share fix) | 37.0 s | green; all guards pass; canon `70b2ce5b…cff2` |
| run 3 (receipt; helper refactor) | 37.2 s | exit 0; canon sha identical to run 2 |

Defect (band-share truncation): the per-cell band-share line
wrapped the fraction in `int()`, printing 0.0000 for every
cell (in both the Task-2 section and the determinism second
pass — determinism still read identical, but the values were
wrong). Fix: float shares in a `cell_band_shares` helper used
by both passes, plus a B-share regression check in
`control.py` (fractional, unit-sum, matches band counts). The
B-share assertions were proven against the pre-fix formula
(`pass=False` on `int()`-truncated shares). Post-fix runs 2
and 3 agree canon-byte-for-byte.

Per-stage wall (receipt run, sequential, no pool):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Task 1 (s0 + m15 splits) | 2 | <1 s |
| Task 2 (bands + 10 carrier resynths) | 10 | <1 s |
| Coarse direction pass | 764 | 28.7 s |
| Rule synths + determinism re-run | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m19.py` wall | — | 37.2 s |

## Step 2 — estimates

### Task 1 — direction split (the joint test)

8-cell partition of residual bytes (DESIGN.md ids; partition
sums == R_0 on both frames):

| id | cell | s0 n | s0 share | s0 negrate | m15 n | m15 share | m15 negrate |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | ep-v0-max | 9004 | 0.3947 | 1.0000 | 4908 | 0.3658 | 1.0000 |
| 1 | ep-v0-min | 408 | 0.0179 | 0.0000 | 373 | 0.0278 | 0.0000 |
| 2 | ep-full-max | 8085 | 0.3544 | 1.0000 | 3629 | 0.2705 | 1.0000 |
| 3 | ep-full-min | 254 | 0.0111 | 0.0000 | 295 | 0.0220 | 0.0000 |
| 4 | above | 159 | 0.0070 | 1.0000 | 108 | 0.0080 | 1.0000 |
| 5 | below | 62 | 0.0027 | 0.0000 | 90 | 0.0067 | 0.0000 |
| 6 | static | 2368 | 0.1038 | 0.5110 | 1476 | 0.1100 | 0.5136 |
| 7 | interior | 2475 | 0.1085 | 0.8093 | 2539 | 0.1892 | 0.8019 |

(The 1.0000/0.0000 negrates in cells 0–5 are floor-blend
arithmetic: synth sits strictly inside [v0,full], so
mid==max/above reads synth<mid always and mid==min/below
reads synth>mid always. Tabled as measured.)

Marginals:

| Marginal | s0 | m15 |
| --- | ---: | ---: |
| mid==max (c0+c2) / endpoint | 17089 / 17751 = 0.9627 | 8537 / 9205 = 0.9274 |
| mid==min (c1+c3) / endpoint | 662 / 17751 = 0.0373 | 668 / 9205 = 0.0726 |
| mid==v0 (c0+c1) | 9412 (M18: 9412) | 5281 (M18: 5281) |
| mid==full (c2+c3) | 8339 (M18: 8339) | 3924 (M18: 3924) |
| interior (c7) | 2475 (M18: 2475) | 2539 (M18: 2539) |
| static+above+below | 2368+159+62 = 2589 (M18 outside: 2589) | 1476+108+90 = 1674 (M18: 1674) |

Outside-moved distance distribution (dout = mid−hi / lo−mid):

| Frame | side | n | hist [1,2–3,4–7,8–15,16+] | max | mean |
| --- | --- | ---: | --- | ---: | ---: |
| s0 | above | 159 | [92, 61, 5, 1, 0] | 9 | 1.623 |
| s0 | below | 62 | [52, 10, 0, 0, 0] | 3 | 1.177 |
| s0 | combined | 221 | [144, 71, 5, 1, 0] | 9 | 1.498 |
| m15 | above | 108 | [83, 19, 4, 1, 1] | 16 | 1.556 |
| m15 | below | 90 | [58, 20, 4, 4, 4] | 47 | 3.711 |
| m15 | combined | 198 | [141, 39, 8, 5, 5] | 47 | 2.535 |

Static-site byte count (gap 1's ask) + sign reconciliation:

| Frame | static raw bytes | of R_0 | Y subset (= P4) | U/V subset | byte negrate | Y-byte negrate (= M18 Y-px) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 2368 | 0.1038 | 463 (P4: 463) | 1905 | 20461/22815 = 0.8968 | 13743/14984 = 0.9172 (M18: 91.7%) |
| m15 | 1476 | 0.1100 | 439 (P4: 439) | 1037 | 11439/13418 = 0.8525 | 7423/8584 = 0.8647 (M18: 86.5%) |

Sign cross (synth<truth rate inside each direction cell): cells
0/2/4 read 1.0000, cells 1/3/5 read 0.0000 (arithmetic, above);
static reads 0.5110/0.5136 (no bias); interior reads
0.8093/0.8019. The −1 bias lives in the max-side + interior
cells; the min-side cells read the opposite sign throughout.

Coarse pass (all 764 M16 triplets; R_s recompute matches
`loo.txt` on 764/764, 0 mismatches; full 764-row table in
`m19.txt`):

| Field | min | med | mean | max |
| --- | ---: | ---: | ---: | ---: |
| R_s | 16290 | 22815 | 22793.8 | 23059 |
| epmax bytes | 11745 | 17089 | 17071.1 | 17134 |
| epmin bytes | 501 | 662 | 662.2 | 723 |
| above | 142 | 159 | 159.1 | 196 |
| below | 46 | 62 | 62.1 | 92 |
| static | 1649 | 2368 | 2365.9 | 2523 |
| interior | 2110 | 2475 | 2473.3 | 2670 |
| epmax share of endpoint | 0.9591 | 0.9627 | 0.9627 | 0.9640 |
| above share of moved-outside | 0.6630 | 0.7195 | 0.7194 | 0.7778 |
| byte negrate | 0.8882 | 0.8968 | 0.8967 | 0.9009 |

Shapes with epmax share ≥ 0.75: 764/764. Extremes: lowest
shape 694 (0.9591), highest shape 701 (0.9640); max static
shape 700 (2523 B), min static shape 694 (1649 B).

### Task 2 — carrier/band cut (where the direction lives)

Band cut (s0 Y-residual bytes; rows 0–149 / 150–298 / 299–447;
m15 + raw-byte tables in `m19.txt`):

| s0 band | nY | c0 | c1 | c2 | c3 | c4 | c5 | c6 | c7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| top | 5678 | 2441 | 142 | 2341 | 60 | 5 | 17 | 15 | 657 |
| mid | 5300 | 1860 | 157 | 1599 | 100 | 97 | 15 | 186 | 1286 |
| bot | 4006 | 1659 | 26 | 1457 | 51 | 50 | 23 | 262 | 478 |

Per-cell band shares (s0 Y; max single-band share 0.6382 —
bar H5's band leg not met):

| cell | nY | top/mid/bot |
| --- | ---: | --- |
| 0 ep-v0-max | 5960 | 0.4096/0.3121/0.2784 |
| 1 ep-v0-min | 325 | 0.4369/0.4831/0.0800 |
| 2 ep-full-max | 5397 | 0.4338/0.2963/0.2700 |
| 3 ep-full-min | 211 | 0.2844/0.4739/0.2417 |
| 4 above | 152 | 0.0329/0.6382/0.3289 |
| 5 below | 55 | 0.3091/0.2727/0.4182 |
| 6 static | 463 | 0.0324/0.4017/0.5659 |
| 7 interior | 2421 | 0.2714/0.5312/0.1974 |

Per-carrier masked cell shares (s0 Y-residual bytes inside each
top-10 removed mask; removed counts + bands match M18 Test C
exactly):

| rank | shape | nrem | c0 | c1 | c2 | c3 | c4 | c5 | c6 | c7 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 694 | 4888 | 2160 | 94 | 2250 | 74 | 1 | 4 | 12 | 293 |
| 2 | 693 | 1208 | 542 | 22 | 506 | 19 | 0 | 0 | 5 | 114 |
| 3 | 701 | 649 | 233 | 20 | 22 | 1 | 2 | 2 | 2 | 367 |
| 4 | 368 | 448 | 206 | 1 | 186 | 7 | 0 | 1 | 39 | 8 |
| 5 | 369 | 248 | 120 | 0 | 117 | 4 | 1 | 0 | 6 | 0 |
| 6 | 366 | 244 | 123 | 0 | 102 | 0 | 0 | 0 | 19 | 0 |
| 7 | 370 | 191 | 86 | 0 | 93 | 0 | 0 | 0 | 12 | 0 |
| 8 | 376 | 174 | 92 | 0 | 72 | 0 | 0 | 0 | 10 | 0 |
| 9 | 748 | 190 | 61 | 5 | 83 | 1 | 0 | 0 | 17 | 23 |
| 10 | 750 | 202 | 73 | 0 | 77 | 2 | 0 | 0 | 8 | 42 |

Per-cell carrier shares (s0 Y; share of each cell's Y bytes in
each mask; max 0.4169 — bar H5's carrier leg not met):

| cell | nY | 694/693/701/368/369/366/370/376/748/750 |
| --- | ---: | --- |
| 0 | 5960 | 0.3624/0.0909/0.0391/0.0346/0.0201/0.0206/0.0144/0.0154/0.0102/0.0122 |
| 1 | 325 | 0.2892/0.0677/0.0615/0.0031/0/0/0/0/0.0154/0 |
| 2 | 5397 | 0.4169/0.0938/0.0041/0.0345/0.0217/0.0189/0.0172/0.0133/0.0154/0.0143 |
| 3 | 211 | 0.3507/0.0900/0.0047/0.0332/0.0190/0/0/0/0.0047/0.0095 |
| 4 | 152 | 0.0066/0/0.0132/0/0.0066/0/0/0/0/0 |
| 5 | 55 | 0.0727/0/0.0364/0.0182/0/0/0/0/0/0 |
| 6 | 463 | 0.0259/0.0108/0.0043/0.0842/0.0130/0.0410/0.0259/0.0216/0.0367/0.0173 |
| 7 | 2421 | 0.1210/0.0471/0.1516/0.0033/0/0/0/0/0.0095/0.0173 |

Notable concentrations (tabled, not explained): rank-3
(701) mask reads 367/649 = 56.6% interior (15.2% of all
interior Y); ranks 6–8 (366/370/376) masks read zero
interior/above/below bytes (max-endpoint + static only —
the weight-invariant draws of M18 Test C); above/below/static
cells never exceed 0.0842 in any carrier mask.

### Direction-rule synths (does direction shrink R_0?)

| Frame | rule | R | explained (R_0 − R) | e |
| --- | --- | ---: | ---: | ---: |
| s0 | max | 30255 | −7440 | −0.3261 |
| s0 | min | 30620 | −7805 | −0.3421 |
| s0 | v0 | 29601 | −6786 | −0.2974 |
| s0 | full | 31274 | −8459 | −0.3708 |
| m15 | max | 17797 | −4379 | −0.3264 |
| m15 | min | 18130 | −4712 | −0.3512 |
| m15 | v0 | 17255 | −3837 | −0.2860 |
| m15 | full | 18672 | −5254 | −0.3916 |

No single-endpoint rule shrinks R_0 on either frame (all
explained ≤ −3837; fnvs in `m19.txt`).

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| D-min (mid=lo) | c1+c3 = n (12464); rest 0 | all endpoint-min | True |
| D-max (mid=hi) | c0+c2 = n (44976); rest 0 | all endpoint-max | True |
| D-v0 (mid=v0) | c0+c1 = n (28783); rest 0 | all ep-v0 | True |
| D-out (mid=lo−1) | cells == independent count exactly; above/interior 0 | exact | True |
| B-share (band fractions) | fractional, unit-sum, match band counts on D-min | exact | True |

(All five pass; D-out's 8 cells match the independently
counted expectation byte-for-byte:
below 44976 / static 528464 / rest 0. B-share is the
regression pin for the run-1 `int()` defect — §Runs.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1+2 on s0) pass1 `70b2ce5b…cff2` vs pass2
`70b2ce5b…cff2`, identical=True; cell counts identical=True.

## Step 3 — attribute

Model comparison (bytes, M16-loo table shape):

| Frame | Model | R | explained (R_0 − R) | e |
| --- | --- | ---: | ---: | ---: |
| m16 s0 | 0 blend | 22815 | 0 | 0.0000 |
| m16 s0 | D rule max | 30255 | −7440 | −0.3261 |
| m16 s0 | D rule min | 30620 | −7805 | −0.3421 |
| m16 s0 | D rule v0 | 29601 | −6786 | −0.2974 |
| m16 s0 | D rule full | 31274 | −8459 | −0.3708 |
| m15 | 0 blend | 13418 | 0 | 0.0000 |
| m15 | D rule max | 17797 | −4379 | −0.3264 |
| m15 | D rule min | 18130 | −4712 | −0.3512 |
| m15 | D rule v0 | 17255 | −3837 | −0.2860 |
| m15 | D rule full | 18672 | −5254 | −0.3916 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_DIR | mid==max share of endpoint ≥ 0.75 on s0 | 0.9627 (m15: 0.9274; 764/764 shapes ≥ 0.75) — met |
| H2_CELL | max 4-cell share of endpoint ≥ 0.50 on s0 | 0.5072 (c0=9004; m15: 0.5330 c0) — met |
| H3_OUT | majority-side share of moved-outside ≥ 0.75 on s0 | 0.7195 above (m15: 0.5455 above) — not met |
| H4_SIGN | max−min byte negrate over cells 0–5 ≥ 0.40 on s0 | 1.0000 − 0.0000 = 1.0000 — met (arithmetic) |
| H5_CONC | some cell ≥ 75% in one band or ≥ 50% in one carrier mask (s0 Y) | max 0.6382 band (above/mid) / 0.4169 carrier (c2/694) — not met |
| N | R after best direction rule + remaining split | best rule explains −6786 (v0); full 22815 B stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
endpoint side (96.3%/92.7% max-side; 4-cell split
9004/408/8085/254 on s0) and by sign (max-side/above read
synth<truth throughout, min-side/below the opposite,
static unbiased at 0.51, interior 0.80) but not by a
shrink rule (all four rules read negative). Task 2
discriminates per carrier (701's mask reads 56.6% interior;
366/370/376 read zero interior/outside; above/below/static
avoid all top-10 masks) and per band (above 63.8% mid,
static 56.6% bottom, interior 53.1% mid) but no cell
concentrates to bar level.

Updated deliverable — explained vs standing remainder:

| Content | Bytes (m16 s0) | Behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (M16, unchanged) |
| endpoint-max component | 17089 of R_0 (74.9%) | mid==bright endpoint; synth<truth throughout |
| endpoint-min component | 662 of R_0 (2.9%) | mid==dark endpoint; synth>truth throughout |
| moved-outside component | 221 of R_0 (1.0%) | 159 above (dout ≤ 9) / 62 below (dout ≤ 3) |
| static-site residual | 2368 of R_0 (10.4%) | v0==full≠mid; Y subset = P4's 463 px exactly |
| interior residual | 2475 of R_0 (10.9%) | strict interior; negrate 0.81 |
| direction-rule component | 0 explained | all 4 rules negative (−6786 best) |
| standing remainder | 22815 (100% of R_0) | split above; sign/band/carrier tables in §Step 2 |

Screenshot (committed): `m19-splitmap.png` 121067 B (dimmed
truth + residual Y px colored by direction cell:
yellow/orange = max-endpoint on the god-ray shafts, rider
glow, and HUD glyph edges; gray = interior mid-frame; red /
magenta / white = above / below / static, sparse). The map
discriminates spatially (cells separate by region), so it is
included. Total 121067 B (budget 5242880).

Recorded without verdict: mid is the brighter endpoint on
17089/17751 endpoint residual bytes (96.3% s0, 92.7% m15,
764/764 shapes above 0.95); moved-outside reads 159/62
above/below on s0 (m15 below-tail reaches dout 47); 2368 raw
static-site bytes stand on s0 (1476 m15); no single-endpoint
rule shrinks R_0 (best −6786).

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| direction-split suite + "explained" definition + falsification bars, recorded before running | recorded | `DESIGN.md`: 8-cell partition + dout + sign cross, band/carrier cuts, rule synths, bars H1–H5/N |
| direction split + carrier/band cut + wall/exit/shas/determinism | measured | §Step 2: 8-cell tables both frames; band + per-carrier shares; 37.0 s; re-run identical |
| explained-vs-standing update (does direction shrink R_0? by what rule?) + per-band/per-carrier discrimination | measured | §Step 3: rule table (all negative) + region rows + deliverable table |
| screenshot if the split map discriminates (or absence reasoned) | measured | 1 PNG, 121067 B: cell-colored split map, spatially discriminating |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the second invocation — §Runs):

```
cp local/research/M19/m19.py local/research/M19/control.py "/Volumes/Extreme SSD/m19/"
python3 m19.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m19" /Users/bradrichardson/dev/ssx3/local/research/M19 > m19.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M19/` — `DESIGN.md`
(suite + bars, recorded before running), `m19.py` (8-cell
split + band/carrier cuts + coarse pass + rule synths + PNG
writer), `control.py` (4 synthetic direction controls +
B-share regression),
`REPORT.md` (this file), `m19-splitmap.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m19/` —
`m19.txt` (receipt: shas, baselines, Task-1 splits, band
tables, per-carrier shares, 764-row table, rule synths,
re-run, PNG size), `control.txt`, `m19.py`, `control.py`
(working copies). No synths dumped (rule R/fnv tabled only).
No writes into `m15/`, `m16/`, `m17/`, `m18/`, or other
agents' dirs.

## Gap rows (exact next brief each needs)

1. Interior-cell mechanism (new): 2475 B strict-interior
   residual (10.9% of R_0, negrate 0.81, 53.1% mid-band,
   15.2% in 701's mask) unattributed at value level. Needs
   its own brief: per-byte mid-vs-blend offset distribution
   + filter-tap fits, offline on the SSD dumps — no new
   harness code.
2. Static-site residual mechanism (new): 2368 raw bytes
   where v0==full≠mid (10.4% of R_0; Y subset = P4's 463
   px; U/V majority 1905 B) — genuinely non-interpolative
   content. Needs its own brief: static-site maps per shape
   + EFB-copy diffing, offline — no new harness code.
3. m15 below-min far tail (new, minor): 4 below-side bytes
   with dout ≥ 16 (max 47) on the m15 frame; s0's tail ends
   at 9. Needs its own brief only if outlier isolation
   matters: locate + plane-split the far-tail bytes,
   offline — no new harness code.
4. Negative-share mechanism (M18 gap 2, still open): 93
   negatives (worst −244) unattributed at byte level. Needs
   its own brief: per-shape added-residual maps + EFB-copy
   diffing, offline — no new harness code.
5. Odin port readiness (M18 gap 3, still open): no Odin
   contract in-repo; handoff artifact stays `loo.txt` +
   dumps + synths. Needs its own brief once the consumer
   names its interface.
6. Top-HUD glyph residual isolation (M18 gap 4, still open):
   bottom-HUD draws identified; top-band glyph edges in the
   long tail. Needs its own brief if draw-level top-HUD
   isolation matters. Note for that brief: the split map
   reads max-endpoint (yellow/orange) on HUD glyph edges
   top and bottom.
7. Per-carrier weight centers (M18 gap 5, still open,
   optional): effect-draw argmins at the fine-grid edge.
   Needs its own brief only if per-draw filter centers
   matter.

## What I could not do

1. Mixed direction rules: only the 4 single-endpoint rules
   (max/min/v0/full) were tabled; per-cell or per-carrier
   mixed predictors not attempted.
2. U/V-independent estimation: counts are raw bytes with a
   Y-px join; independent chroma analysis not attempted.
3. Per-shape carrier cuts: carrier/band cuts are s0 (+ m15
   bands) only; the 764-shape question is carried by the
   coarse direction pass.
4. H4's 1.0000/0.0000 cell negrates are floor-blend
   arithmetic, not an empirical bias discovery — tabled
   with the arithmetic noted, not chased.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M19/`: `DESIGN.md`, `m19.py`,
`control.py`, `REPORT.md` (this file), `m19-splitmap.png`
(121067 B total).
