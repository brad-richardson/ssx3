# M51 — TRI cross-frame collapse: per-column triangle-drift tables: REPORT

M26 gap 1 worked at table level: per-column TRI drift (Δp/Δh/Δe/Δw
m15−s0 + L1) for the 8 named columns plus the collapse recount
(kept-hit site rows both directions), with M26's 8×2 TRI fits +
18/16 same-frame + 4/68 + 2/65 cross-frame reproduced exactly
(hit = exact, near-hit |err|≤1 tabled separately, never merged).
Fits reproduce M26 16/16 p/h/e/w; peaks read stable on 5/8
columns (Δp==0) while c343 jumps +262 (27→289) and c340 shifts
+6 (26→32); edge drifts broadly (|Δe|≥3 on 6/8) while height
drifts narrowly (|Δh|≥5 on 3/8); low-drift columns (296/301,
L1 2/4) keep 0 pooled hits while high-drift 257/340 (L1 15/10)
keep 2 each. Fully offline — no lease of any kind, no boots, no
harness code, no `adb`. No device work. Runbook
`local/muse/prompts/M51.md`. Tables, no verdicts.

Headers read first: `local/research/M26/REPORT.md` (all of it:
TRI 18/65 s0 + 16/68 m15 exact hits, cross-frame 4/68 + 2/65,
8×2 p/h/e/w fits, per-column colhits, miss bins, errvalues)
plus `local/research/M25/REPORT.md` (all of it: CONST collapse
+ peak-anchored residual method, 65/68 named-column bytes,
row→δ lists, CONST 12/65 + 13/68, cross-frame 0/1).

Time box 4 hours (start 2026-09-20 07:06 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m50/` — all outputs went to the new
`/Volumes/Extreme SSD/m51/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), and `m26.txt` (8×2 TRI
fits + TRI scores to reproduce). Work dir `/Volumes/Extreme
SSD/m51/`; evidence `local/research/M51/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M50):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m26.txt | `9a3d522b…060ff8f8` |

(Full hexes in `m51.txt` §inputs; `m26.txt` 18821 B.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M50 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m51.py` invocation (the receipt, 0.1 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try). DESIGN.md was
recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m51.py receipt | 0.1 s | exit 0; all guards pass; canon `1307c07b…85099e` |
| control.py C-P1 (known triangles + drift) | <1 s | green; 4 fits + 2 drifts exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 profiles + fits + scores + xframe) | 2 | 0.0 s |
| Task 2 (drift + driftx + neg sites) | 2 | <1 s |
| Determinism re-run (TRI fits on s0+m15 + drift) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m51.py` wall | — | 0.1 s |

## Step 2 — estimates

### Task 1 — TRI fit reproduction (do the 8×2 fits reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M22/M23/M25/M26 EXACTLY,
and all 16 TRI p/h/e/w matching `m26.txt` fit lines exactly on
BOTH frames (stop rule not triggered). Named-column bytes read
65 s0 / 68 m15. δ==0 count reads 0; P(δ>0) reproduces M19/M20
0.8093/0.8019. Tail planes read 102/0/0 s0 and 134/0/0 m15
(Y/U/V).

Fit table: all 8 columns × s0/m15 p/h/e/w (16 fits, tfb=[] both
frames, empties none, fallback 27 s0 / 20 m15):

| col | s0 p/h/e/w | m15 p/h/e/w |
| ---: | --- | --- |
| 257 | 25/30/13/7 | 25/20/8/7 |
| 277 | 25/28/13/7 | 25/20/8/7 |
| 296 | 26/47/15/8 | 26/46/16/8 |
| 301 | 27/47/13/6 | 27/48/12/4 |
| 321 | 25/27/11/7 | 26/31/14/6 |
| 340 | 26/47/17/8 | 32/48/14/8 |
| 342 | 27/−16/−17/1 | 27/−13/−21/4 |
| 343 | 27/−26/−31/1 | 289/−15/−22/1 |

(M26 fit-line match: 8/8 cols both frames; DESIGN pins match.)

Same-frame score table: TRI hits/near/miss-bins per frame (18 +
16 reproduced with miss bins + errvalues + colhits):

| Frame | hits/rate | near | miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| s0 | 18 / 0.2769 | 8 | 8/9/14/8 |
| m15 | 16 / 0.2353 | 5 | 12/20/9/6 |

Errvalues s0: 0:18 1:8 2:4 3:4 4:3 5:2 6:4 8:7 9:4 10:2
11:1 16:2 18:1 20:2 22:1 23:2. Errvalues m15: 0:16 1:5 2:9
3:3 4:4 5:9 6:4 7:3 8:4 9:2 11:1 12:1 13:1 17:1 20:1 22:1
23:1 24:1 26:1. (Both match M26 exactly.)

Per-column same-frame TRI colhits (reproduced):

| Frame | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 (n) | 3/10 | 2/10 | 2/9 | 3/11 | 2/10 | 2/8 | 2/5 | 2/2 |
| m15 (n) | 3/10 | 2/10 | 2/9 | 2/11 | 2/10 | 1/9 | 2/5 | 2/4 |

Collapse table: fit-s0→m15 hits (4/68) + fit-m15→s0 hits (2/65)
with per-column kept-hit colhits (which columns keep hits
cross-frame?):

| Direction | hits/rate | near | miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| fit-s0 → m15 | 4 / 0.0588 | 8 | 13/15/21/7 |
| fit-m15 → s0 | 2 / 0.0308 | 11 | 7/15/19/11 |

Errvalues fit-s0→m15: 0:4 1:8 2:4 3:9 4:2 5:5 6:6 7:2 8:4
9:4 10:4 11:2 12:6 13:1 16:1 17:1 18:1 23:3 24:1.
Errvalues fit-m15→s0: 0:2 1:11 2:2 3:5 4:6 5:4 6:1 7:4 8:2
9:4 10:3 11:2 12:2 13:3 14:2 15:1 16:1 17:2 18:2 19:1 20:2
22:1 23:1 24:1. (Both match M26 exactly.)

Per-column cross-frame TRI colhits (reproduced):

| Direction | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fit-s0 → m15 | 1/10 | 1/10 | 0/9 | 0/11 | 0/10 | 1/9 | 0/5 | 1/4 |
| fit-m15 → s0 | 1/10 | 0/10 | 0/9 | 0/11 | 0/10 | 1/8 | 0/5 | 0/2 |

Kept-hit site rows (the 4 + 2 hits itemized):

| Direction | col | row | δ | pred |
| --- | ---: | ---: | ---: | ---: |
| fit-s0 → m15 | 257 | 29 | 20 | 20 |
| fit-s0 → m15 | 277 | 31 | 15 | 15 |
| fit-s0 → m15 | 340 | 26 | 47 | 47 |
| fit-s0 → m15 | 343 | 27 | −26 | −26 |
| fit-m15 → s0 | 257 | 23 | 17 | 17 |
| fit-m15 → s0 | 340 | 31 | 44 | 44 |

(Columns keeping hits: fit-s0→m15 c257/c277/c340/c343;
fit-m15→s0 c257/c340. c296/c301/c321/c342 keep 0 both
directions.)

### Task 2 — triangle drift (which leg collapses?)

Drift table: Δp/Δh/Δe/Δw (m15 − s0) per column + L1 (which leg
drifts most? peak p? height h?):

| col | Δp | Δh | Δe | Δw | L1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 257 | +0 | −10 | −5 | +0 | 15 |
| 277 | +0 | −8 | −5 | +0 | 13 |
| 296 | +0 | −1 | +1 | +0 | 2 |
| 301 | +0 | +1 | −1 | −2 | 4 |
| 321 | +1 | +4 | +3 | −1 | 9 |
| 340 | +6 | +1 | −3 | +0 | 10 |
| 342 | +0 | +3 | −4 | +3 | 10 |
| 343 | +262 | +11 | +9 | +0 | 282 |

(|Δp|≥1 on 3/8: c321 +1, c340 +6, c343 +262. |Δh|≥5 on 3/8:
c257 −10, c277 −8, c343 +11. |Δe|≥3 on 6/8: c257/277/321/340/
342/343. Δw≠0 on 3/8: c301 −2, c321 −1, c342 +3.)

Drift-vs-collapse table: per-column L1 vs cross-frame kept hits
(do low-drift columns keep hits?):

| col | L1 | low (L1≤5)? | k_s0m15 | k_m15s0 | pooled |
| ---: | ---: | --- | ---: | ---: | ---: |
| 257 | 15 | False | 1/10 | 1/10 | 2 |
| 277 | 13 | False | 1/10 | 0/10 | 1 |
| 296 | 2 | True | 0/9 | 0/9 | 0 |
| 301 | 4 | True | 0/11 | 0/11 | 0 |
| 321 | 9 | False | 0/10 | 0/10 | 0 |
| 340 | 10 | False | 1/9 | 1/8 | 2 |
| 342 | 10 | False | 0/5 | 0/5 | 0 |
| 343 | 282 | False | 1/4 | 0/2 | 1 |

(Low-drift columns 296/301 read pooled kept 0/0; pooled kept
≥1 reads on 257/277/340/343 with L1 15/13/10/282.)

c343/c342 table: the negative columns' fits + drifts (c343's
m15 p=289 vs s0 p=27 — the peak jump itemized):

| col | s0 p/h/e/w | m15 p/h/e/w | Δp/Δh/Δe/Δw | L1 |
| ---: | --- | --- | --- | ---: |
| 342 | 27/−16/−17/1 | 27/−13/−21/4 | +0/+3/−4/+3 | 10 |
| 343 | 27/−26/−31/1 | 289/−15/−22/1 | +262/+11/+9/+0 | 282 |

c342 site rows (row, δ, same-frame pred/err, cross-frame
pred/err):

| Frame | row | δ | pred_same | err_same | pred_x | err_x |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 27 | −16 | −16 | 0 | −13 | +3 |
| s0 | 28 | −27 | −17 | +10 | −15 | +12 |
| s0 | 29 | −18 | −17 | +1 | −17 | +1 |
| s0 | 34 | −16 | −17 | −1 | −21 | −5 |
| s0 | 35 | −17 | −17 | 0 | −21 | −4 |
| m15 | 27 | −13 | −13 | 0 | −16 | −3 |
| m15 | 28 | −20 | −15 | +5 | −17 | +3 |
| m15 | 29 | −14 | −17 | −3 | −17 | −3 |
| m15 | 34 | −19 | −21 | −2 | −17 | +2 |
| m15 | 35 | −21 | −21 | 0 | −17 | +4 |

c343 site rows (the peak jump: s0 peak r27 δ=−26; m15 peak
r289 δ=−15; m15 rows 25/26/27 carry −22/−34/−26):

| Frame | row | δ | pred_same | err_same | pred_x | err_x |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 26 | −31 | −31 | 0 | −22 | +9 |
| s0 | 27 | −26 | −26 | 0 | −22 | +4 |
| m15 | 25 | −22 | −22 | 0 | −31 | −9 |
| m15 | 26 | −34 | −22 | +12 | −31 | +3 |
| m15 | 27 | −26 | −22 | +4 | −26 | 0 |
| m15 | 289 | −15 | −15 | 0 | −31 | −16 |

(c343's fit-s0→m15 kept hit is m15 r27: s0 peak pred −26 reads
m15's mid-row δ −26. c343's m15 r289 peak (δ=−15) reads
err_x=−16 under the s0 fit.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 (known triangles + drift, N=10, 0 skips) | 112/112 tail both frames, sets exact, values exact, originals unchanged, maps J 1.0/1.0 | exact | True |
| C-P1 profiles (X-A/X-B/Y-A/Y-B row→δ) | 8,10,12,10,8 / 9,12,14,12,9 / 8,10,12,10,8 / 8,8,10,12,10 exact | exact | True |
| C-P1 fits (trifit per pseudo-col per frame) | X-A 28/12/8/2 + X-B 28/14/9/2 + Y-A 28/12/8/2 + Y-B 29/12/8/2, all TRI 5/5 | exact | True |
| C-P1 drift (B−A per pseudo-col) | X 0/+2/+1/0 + Y +1/0/0/0 | exact | True |

(Full-control-frame named TRI fits tabled: n=65 both frames A/B
with s0's 8×2 p/h/e/w reproduced — injections fall outside
named-column tail sets by pool construction. Full tables in
`control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 TRI fits on s0+m15 + Task 2 drift/driftx)
pass1 `1307c07b…85099e` vs pass2 `1307c07b…85099e`,
identical=True; fits+drift identical=True; cell counts
identical=True; tail counts identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; TRI exact hits, named-column
scope — M26's fit, reproduced, 0 new):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | TRI exact hits | 2475 | 18 | 0.0073 |
| m15 | TRI exact hits | 2539 | 16 | 0.0063 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_PEAKSTABLE | share of 8 named columns with Δp==0 ≥ 0.50 | 5/8 = 0.6250 (257/277/296/301/342) — met |
| H2_HEIGHTDRIFT | share of 8 named columns with \|Δh\|≥5 ≥ 0.50 | 3/8 = 0.3750 (257/277/343) — not met |
| H3_EDGEDRIFT | share of 8 named columns with \|Δe\|≥3 ≥ 0.50 | 6/8 = 0.7500 (257/277/321/340/342/343) — met |
| H4_WIDTHSTABLE | share of 8 named columns with Δw==0 ≥ 0.50 | 5/8 = 0.6250 (257/277/296/340/343) — met |
| H5_COLLAPSE | s0-fit TRI scored on m15 reads m15 rate within 0.15 of s0 rate | \|0.0588−0.2769\| = 0.2181 — not met |
| H6_LOWDRIFTKEEPS | among L1≤5 columns, share with pooled kept ≥1 ≥ 0.50 | 0/2 (296/301 keep 0/0) — not met |
| H7_NEGPEAK | c343 \|Δp\|≥100 (m15 p=289 vs s0 p=27) | 262 — met |
| N | named-col tail after TRI hits + drift attribution | 18/16 explained (M26, 0 new); 47/52 named-col stands; legs tabled above |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (16/16 p/h/e/w + 18/16 same-frame + 4/2
cross-frame + all per-column colhits + errvalues match M26
exactly) and by kept-hit column (c257/c340 keep both
directions, c277/c343 keep fit-s0→m15 only, c296/c301/c321/
c342 keep neither). Task 2 discriminates by leg (peak stable
5/8 with c343 +262 and c340 +6; height |Δh|≥5 on 3/8;
edge |Δe|≥3 on 6/8; width Δw==0 on 5/8 with c301 −2, c321 −1,
c342 +3), by drift-vs-collapse (L1 reads 2/4 on the kept-0
low columns vs 10–15 on the kept-2 columns and 282 on c343),
and by negative site (c343's kept hit is m15 r27 under the s0
peak pred; c343's m15 r289 peak reads err_x −16; c342 keeps 0
with per-site |err_x| 1–5).

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
| interior far tail, TRI-hit | 18 of cell 7 (0.7%) | δ=TRI pred exact, named-col scope (M26, reproduced) |
| interior far tail, standing | 84 of cell 7 (3.4%) | 47 named-col + 37 outside-named; stands (this run) |
| standing interior remainder | 2457 of cell 7 (99.3%) | 2475 − 18 TRI hits |
| standing remainder (total) | 22797 (99.9% of R_0) | 18 B tail-explained; rest split above |

Screenshot: absent by rule. The workdir drift-collapse map
(`m51-driftmap.png`, 88557 B) colors s0 named-column sites by
fit-m15→s0 kept outcome (green kept 2 / red lost 63), but
DESIGN.md admits an evidence copy only if some s0 named column
with n≥8 reads pooled cross-frame kept hits ≥ 3 (max reads 2:
c257/c340 at n=10/8) — no pre-registered split qualifies, so
no evidence copy is committed (0 B of 5242880 budget). The
workdir copy is retained, uncommitted.

Recorded without verdict: the 8×2 TRI fits read 16/16 M26-exact
with same-frame 18/65 + 16/68 and cross-frame 4/68 + 2/65
(all colhits + errvalues M26-exact); per-column drift reads
Δp==0 on 5/8 (c343 +262, c340 +6, c321 +1), |Δh|≥5 on 3/8
(−10/−8/+11), |Δe|≥3 on 6/8, Δw==0 on 5/8 (c301 −2, c321 −1,
c342 +3), L1 2–15 plus c343 282; kept hits read pooled 2/1/0/
0/0/2/0/1 across c257…c343 with low-drift 296/301 at 0/0; c343
itemizes s0 peak r27 vs m15 peak r289 with the kept hit at m15
r27; 47/52 named-column bytes stand after TRI with 0 new bytes
explained (attribution, not explanation).

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| TRI suite + drift definitions + falsification bars, recorded before running | recorded | `DESIGN.md`: M26-verbatim TRI + scoring + Δ/L1/kept joins, bars H1–H7/N |
| 8×2 fits + same-frame + collapse recount + wall/exit/shas/determinism | measured | §Step 2: 16/16 fits + 18/16 same-frame + 4/2 collapse + 6 kept-hit site rows; 0.1 s; re-run identical |
| drift tables + drift-vs-collapse + c342/c343 + explained-vs-standing + gap rows | measured | §Step 2/3: Δ/L1 per column + kept join + neg site rows; 0 new explained, 47/52 stands; gaps below |
| screenshot if a drift map discriminates (or absence reasoned) | measured | absent by rule: max pooled kept 2 at n≥8 (want ≥3); workdir copy only, 88557 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m51"
cp local/research/M51/m51.py local/research/M51/control.py local/research/M51/DESIGN.md "/Volumes/Extreme SSD/m51/"
python3 m51.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m26/m26.txt" "/Volumes/Extreme SSD/m51" /Users/bradrichardson/dev/ssx3/local/research/M51 > m51.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
```

## Paths

Evidence (committed): `local/research/M51/` — `DESIGN.md`
(suite + drift joins + bars, recorded before running),
`m51.py` (profiles + TRI fits + scoring + drift + PNG writer),
`control.py` (known-triangle + known-drift tail-injection
control), `REPORT.md` (this file). No PNG committed (absence
reasoned above).

Large outputs (not committed): `/Volumes/Extreme SSD/m51/` —
`m51.txt` (receipt: shas, baselines, Task-1 profiles both
frames, 8×2 fits, M26 match, same-frame scores, xframe both
directions, kept-hit rows, drift + driftx + neg sites, re-run,
PNG size), `control.txt`, `m51.py`, `control.py`, `DESIGN.md`
(working copies), `m51-driftmap.png` (working copy, 88557 B).
No writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`,
`m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`,
`m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`,
`m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`, `m43/`, `m44/`,
`m45/`, `m46/`, `m47/`, `m48/`, `m49/`, `m50/`, or other agents'
dirs.

## Gap rows (exact next brief each needs)

1. Low-drift no-keep split (new): c296/c301 read L1 2/4 but
   pooled kept 0/0, while c257/c340 (L1 15/10) keep 2 each —
   drift magnitude does not predict kept hits. Needs its own
   brief only if drift-vs-survival matters: per-site kept-hit
   residual tables (same-frame err vs cross-frame err per
   kept/lost site), offline — no new harness code.
2. Height-vs-edge leg attribution (new): |Δh|≥5 reads 3/8
   while |Δe|≥3 reads 6/8 — the edge leg drifts more broadly
   than the height leg. Needs its own brief only if leg
   attribution matters: per-leg ablation tables (hold
   p/h/e/w fixed one at a time cross-frame), offline — no new
   harness code.
3. c340 peak-shift survival (new, minor): c340 Δp=+6 (26→32)
   keeps pooled 2 — the only positive-column peak shift that
   keeps hits both directions. Needs its own brief only if
   peak-shift survival matters: per-row prediction tables
   around shifted peaks, offline — no new harness code.
4. Peak-row agreement without value agreement (M26 gap 2, still
   open): 5/8 columns share peak rows cross-frame but only
   6/65 shared-site δ values agree (M25 H5) — positional vs
   value structure split. Needs its own brief only if peak
   anchoring matters: peak-anchored residual tables, offline
   — no new harness code.
5. Index-top argmax concentration (M26 gap 3, still open): 6/8
   s0 + 5/8 m15 argmax read top-third by index under the
   first-tie rule (plateau peaks: c257's 29×4 run, c340's twin
   47s). Needs its own brief only if peak-position convention
   matters: plateau-aware peak tables (all-tie rows +
   run-center rules), offline — no new harness code.
6. QUAD underfit (M26 gap 4, still open, minor): smooth
   quadratic reads 4/65 + 3/68 with 32/23 mass in the 2–3 miss
   bin — below TWO and CONST on both frames despite ∩
   curvature on every positive column. Needs its own brief
   only if curvature matters: per-column quadratic-residual
   tables, offline — no new harness code.
7. CONST cross-frame collapse (M26 gap 5 / M25 gap 2, still
   open): s0 column medians score 0/68 on m15 (1/65 the other
   way) vs 12/13 same-frame. Needs its own brief only if
   column-value mapping matters: per-column median drift
   tables s0 vs m15, offline — no new harness code.
8. m15 c343 row-289 site (M26 gap 6 / M25 gap 3, still open):
   one tail site 262 rows below its column's band (hole span
   28–288), now also m15 c343's argmax peak (M51 H7 itemizes
   the +262 peak jump; why r289 is tail stands). Needs its own
   brief only if outlier isolation matters: far-row tail-site
   census, offline — no new harness code.
9. SIGN-corrected near-hit mass (M26 gap 7 / M24 gap 1, still
   open): 35 s0 / 38 m15 tail bytes read |err|=1 after the
   best M24 correction vs 21/28 exact. Needs its own brief
   only if second-order structure matters: residual-sign
   tables around K45++SIGN, offline — no new harness code.
10. Streak-column residual coherence (M26 gap 8 / M24 gap 2,
    still open): s0 c257 reads r∈{−3,−2,0} only, c296 reads
    all |r|≤1, c342 reads all r≥1 (M26/M51 worked δ-level
    shapes, not r-level). Needs its own brief only if
    column-local correction matters: per-column r-profile
    tables + column-constant fits, offline — no new harness
    code.
11. Gap-bin 32–63 ±1 concentration (M26 gap 9 / M24 gap 3, still
    open): 16/32 s0 + 31/49 m15 |r|=1 sites sit in gap bin
    32–63. Needs its own brief only if gap-local rounding
    matters: per-gap-value r tables within 32–63, offline — no
    new harness code.
12. POS cross-frame collapse (M26 gap 10 / M23 gap 3, still
    open): POS cell medians read 7/16 same-frame but 1/2
    cross-frame (M26's TRI collapse reads 18/16 vs 4/2,
    M51's drift tables read L1 2–282 — tabled, same phenomenon
    at shape level). Needs its own brief only if
    position-value mapping matters: per-cell median drift
    tables s0 vs m15, offline — no new harness code.
13. Shape-733 tail divergence (M26 gap 11 / M23 gap 4, still
    open): shape 733's tail map reads Jaccard 0.6694 vs s0
    (100 B) while 727/764 shapes read byte-identical (731
    next-lowest at 0.6833). Needs its own brief: per-byte
    attribution of 733's private sites (tail-set change vs δ
    change), offline — no new harness code.
14. m15 private tail sites (M26 gap 12 / M23 gap 5, still open):
    64/134 m15 tail sites never recur on any M16 shape (occ 0;
    Jaccard 0.4132). Needs its own brief only if cross-sample
    tail identity matters: second-sample tail family, offline
    — no new harness code.
15. Shape-700 map divergence (M26 gap 13 / M21 gap 1, still
    open): shape 700's static map reads Jaccard 0.0747 vs s0
    while 518/764 read byte-identical. Needs its own brief:
    per-byte attribution of 700's private sites, offline — no
    new harness code.
16. m15 static-map disjointness (M26 gap 14 / M21 gap 2, still
    open): m15 shares 92/1476 static sites with s0 (Jaccard
    0.0245). Needs its own brief only if cross-sample map
    identity matters, offline — no new harness code.
17. U/V co-residual mechanism (M26 gap 15 / M21 gap 3, still
    open): same-pixel U&V co-residual reads 16.0×/21.6×
    independence. Needs its own brief only if chroma pairing
    matters, offline — no new harness code.
18. δ-sign mechanism (M26 gap 16 / M20 gap 2, still open,
    minor): δ>0 on 80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs
    P(δ>0|v0<full) ≈ 0.70 on both frames. Needs its own brief
    only if the sign asymmetry matters, offline — no new
    harness code.
19. m15 below-min far tail (M26 gap 17 / M19 gap 3, still open,
    minor): 4 below-side bytes with dout ≥ 16 (max 47) on m15.
    Needs its own brief only if outlier isolation matters,
    offline — no new harness code.
20. Negative-share mechanism (M26 gap 18 / M18 gap 2, still
    open): 93 negatives (worst −244) unattributed at byte
    level. Needs its own brief: per-shape added-residual maps
    + EFB-copy diffing, offline — no new harness code.
21. Odin port readiness (M26 gap 19 / M18 gap 3, still open): no
    Odin contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
22. Top-HUD glyph residual isolation (M26 gap 20 / M18 gap 4,
    still open): bottom-HUD draws identified; top-band glyph
    edges in the long tail. Needs its own brief if draw-level
    top-HUD isolation matters.
23. Per-carrier weight centers (M26 gap 21 / M18 gap 5, still
    open, optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers matter.

## What I could not do

1. No cross-shape check: the brief asks cross-frame only
   (fit-s0→m15 and vice versa), so shapes 1/2/733 are
   unscored — tabled scope, not chased.
2. No near-hit merging: 13 pooled near-hits stay separate
   from the 34 exact hits by rule (8/5 same-frame, 8/11
   cross-frame, all tabled separately).
3. c341 unscored: 0 s0 / 1 m15 sites — membership-guarded
   but outside the brief's 8 fit columns.
4. Float paths: TRI runs its w-search SSE in float64 with
   half-away rounding (per DESIGN.md, M26-verbatim), not
   exact-integer — tabled as implemented.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M51/`: `DESIGN.md`, `m51.py`,
`control.py`, `REPORT.md` (this file). No PNG (0 B).
