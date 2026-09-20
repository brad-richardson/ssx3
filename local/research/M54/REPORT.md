# M54 — QUAD underfit: per-column quadratic-residual tables: REPORT

M26 gap 4 worked at table level: per-column quadratic-residual
tables (res = δ − QUAD pred per site + |res| + seat + hole flags
for all 133 named-column sites) plus the 2–3-bin census (which
columns hold the 32/23 mass?) plus per-column ∩ depth vs
residual spread, with M26's 8×2 QUAD fits + 4/65 + 3/68 scores
reproduced exactly (hit = exact, near-hit |res|≤1 tabled
separately, never merged). The 2–3 mass reads interior-heavy
(37/55 pooled interior seats, 6/55 peak, 12/55 edge, 6/55
hole-adjacent) with s0 columns 257/277/321 carrying 7/8/8 of the
32 s0 sites while ragged c296/c340 fail outside the 2–3 bin
(max|res| 18/15); depth reads deepest on s0 c340 (138.55) but
mean|res| reads worst on s0 c296 (9.44). Fully offline — no
lease of any kind, no boots, no harness code, no `adb`. No
device work. Runbook `local/muse/prompts/M54.md`. Tables, no
verdicts.

Headers read first: `local/research/M26/REPORT.md` (all of it:
QUAD 4/65 s0 + 3/68 m15 exact hits, miss mass 32/23 in 2–3,
8×2 a/b/c fits, per-column colhits, miss bins, errvalues) plus
`local/research/M51/REPORT.md` (TRI 18/16 for the fit comparison
— QUAD 4/3 vs TRI 18/16 vs TWO 15/13 vs CONST 12/13).

Time box 4 hours (start 2026-09-20 07:36 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m53/` — all outputs went to the new
`/Volumes/Extreme SSD/m54/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, the M15 triplet
(`m15-v0/mid/full.bin`, second sample), and `m26.txt` (8×2 QUAD
fits + QUAD scores to reproduce). Work dir `/Volumes/Extreme
SSD/m54/`; evidence `local/research/M54/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M53):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m26.txt | `9a3d522b…060ff8f8` |

(Full hexes in `m54.txt` §inputs; `m26.txt` 18821 B; sha
matches M51's record.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | --- | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M53 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

Two `m54.py` invocations (first red on a determinism-section
ordering bug: the second-pass canon list interleaved ladder
lines per frame while the first-pass list appends all score
lines before all ladder lines — pass1/pass2 sha mismatch with
identical content; fixed with no design change) plus two
pre-receipt syntax-typo fixes (a `CONST"]` bracket typo across
two edits, caught by `py_compile` before the receipt run — not
results). The receipt is the single clean re-run (0.1 s, exit 0
— the estimator was never changed after the receipt run
started); one `control.py` invocation (green, first try).
DESIGN.md was recorded before running and is unaffected.

| Invocation | Wall | Standing |
| --- | --- | --- |
| m54.py receipt | 0.1 s | exit 0; all guards pass; canon `ef39e866…909` |
| control.py C-P1 (known quadratics) | <1 s | green; 4 fits + 4 residual tables exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | --- | --- |
| Task 1 (s0 + m15 profiles + fits + scores + ladder) | 2 | 0.0 s |
| Task 2 (residuals + census + curvature) | 2 | <1 s |
| Determinism re-run (Task 1 on s0+m15) | — | in-pass |
| Positive control (`control.py`) | — | <1 s |
| Total `m54.py` wall | — | 0.1 s |

## Step 2 — estimates

### Task 1 — QUAD reproduction (do the fits + scores reproduce?)

Cell-7 membership + tail membership + column membership
recomputed from the dumps: 2475/2539 cell + 102/134 tail with
sub-bins 28+74 / 50+84 and max 47/48, all 18 per-column guard
rows (n/minrow/maxrow/sum) matching M22/M23/M25/M26 EXACTLY,
and all 16 QUAD a/b/c (6dp) matching `m26.txt` fit lines
exactly on BOTH frames with qfb=[343] s0 / [] m15 (stop rule
not triggered). Named-column bytes read 65 s0 / 68 m15. δ==0
count reads 0; P(δ>0) reproduces M19/M20 0.8093/0.8019. Tail
planes read 102/0/0 s0 and 134/0/0 m15 (Y/U/V).

Fit table: all 8 columns × s0/m15 a/b/c (16 fits, the s0-c343
fb + m15 ~0 curvatures):

| col | s0 a/b/c | m15 a/b/c |
| ---: | --- | --- |
| 257 | −0.689394 / 37.425758 / −476.666667 | −0.481061 / 26.131061 / −333.633333 |
| 277 | −0.640152 / 35.026515 / −449.433333 | −0.481061 / 26.046212 / −331.300000 |
| 296 | −0.404340 / 23.168490 / −294.304058 | −0.868259 / 50.447612 / −688.249615 |
| 301 | −1.159674 / 63.787179 / −834.441958 | −1.143357 / 63.527972 / −844.503497 |
| 321 | −0.678030 / 36.921970 / −474.300000 | −0.795455 / 43.653030 / −567.133333 |
| 340 | −1.385542 / 80.305890 / −1108.425033 | −0.936376 / 54.382935 / −743.708269 |
| 342 | +0.205138 / −12.255931 / +161.966235 | −0.021758 / 0.681633 / −17.653034 |
| 343 | CONST-fb (n=2) | +0.007831 / −2.419882 / +30.284514 |

(M26 fit-line match: 8/8 cols both frames; DESIGN 2dp a-pins
match. s0 c342 reads ∪ (+0.21); m15 c342/c343 read ~0
(−0.02/+0.01).)

Score table: QUAD hits/near/miss-bins per frame (4 + 3 with
32/23 in 2–3 — per-column mass below):

| Frame | hits/rate | near | miss 2–3/4–7/8–15/16+ |
| --- | ---: | ---: | --- |
| s0 | 4 / 0.0615 | 8 | 32/14/6/1 |
| m15 | 3 / 0.0441 | 18 | 23/12/12/0 |

Errvalues s0: 0:4 1:8 2:20 3:12 4:8 5:4 6:1 7:1 8:1 9:2 11:1
12:1 13:1 18:1. Errvalues m15: 0:3 1:18 2:18 3:5 4:2 5:2 6:3
7:5 9:4 10:4 11:2 14:1 15:1. (Both match M26 exactly.)

Per-column QUAD colhits + 2–3 mass (reproduced; which columns
hold the 32/23?):

| Frame | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 hits (n) | 1/10 | 1/10 | 0/9 | 0/11 | 2/10 | 0/8 | 0/5 | 0/2 |
| s0 2–3 mass | 7 | 8 | 0 | 3 | 8 | 1 | 3 | 2 |
| m15 hits (n) | 1/10 | 0/10 | 0/9 | 1/11 | 0/10 | 0/9 | 0/5 | 1/4 |
| m15 2–3 mass | 5 | 4 | 1 | 1 | 6 | 2 | 2 | 2 |

(s0 2–3 pooled 32: c277/c321 carry 8 each, c257 7; c296 carries
0 (its 8 misses read 4+). m15 2–3 pooled 23: c321 carries 6,
c257 5, c277 4.)

Fit-ladder table: QUAD vs TRI vs TWO vs CONST per column
(TRI/TWO/CONST refit M26-verbatim; where is QUAD worst?):

| Frame | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 | pooled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| s0 QUAD | 1 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 4 |
| s0 TRI | 3 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 18 |
| s0 TWO | 3 | 5 | 1 | 1 | 2 | 0 | 1 | 2 | 15 |
| s0 CONST | 4 | 2 | 1 | 1 | 3 | 0 | 1 | 0 | 12 |
| m15 QUAD | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 3 |
| m15 TRI | 3 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 16 |
| m15 TWO | 2 | 3 | 1 | 1 | 3 | 1 | 1 | 0 | 12 |
| m15 CONST | 2 | 3 | 2 | 1 | 2 | 2 | 1 | 0 | 13 |

(All 64 ladder cells + 8 pooled counts match M26 exactly.
QUAD reads worst-or-tied on 8/8 s0 columns (strictly worst on
c257/c277/c296/c301/c342; tied CONST on c343, TWO+CONST on
c340, TRI+TWO on c321) and on 7/8 m15 columns (m15 c343: QUAD
1 beats TWO/CONST 0/0, trails TRI 2).)

### Task 2 — quadratic residuals (where does smooth fail?)

Residual tables: per site row:δ/pred/res/abs/seat/holeadj per
column per frame (res = δ − QUAD pred, SIGNED — opposite sign
to M26's err = pred − δ; seat ∈ peak/edge/interior with peak >
edge > interior; holeadj 1 = row±1 holed within the band).
s0 (65 sites):

```
res s0 c=257: 23:17/19/−2/2/edge/0 24:28/24/+4/4/interior/0 25:30/28/+2/2/peak/0 26:29/30/−1/1/interior/0 27:29/31/−2/2/interior/0 28:29/31/−2/2/interior/0 29:29/29/0/0/interior/0 30:28/26/+2/2/interior/0 31:23/21/+2/2/interior/0 32:13/15/−2/2/edge/0
res s0 c=277: 23:16/18/−2/2/edge/0 24:25/22/+3/3/interior/0 25:28/26/+2/2/peak/0 26:27/29/−2/2/interior/0 27:27/30/−3/3/interior/0 28:28/29/−1/1/interior/0 29:28/28/0/0/interior/0 30:28/25/+3/3/interior/0 31:24/21/+3/3/interior/0 32:13/16/−3/3/edge/0
res s0 c=296: 24:21/29/−8/8/edge/0 25:41/32/+9/9/interior/0 26:47/35/+12/12/peak/0 27:35/36/−1/1/interior/0 28:19/37/−18/18/interior/1 31:31/35/−4/4/interior/1 32:46/33/+13/13/interior/0 33:39/30/+9/9/interior/0 34:15/26/−11/11/edge/0
res s0 c=301: 23:18/19/−1/1/edge/0 24:29/28/+1/1/interior/0 25:33/35/−2/2/interior/0 26:41/40/+1/1/interior/0 27:47/42/+5/5/peak/0 28:46/42/+4/4/interior/0 29:39/40/−1/1/interior/0 30:32/35/−3/3/interior/0 31:25/29/−4/4/interior/0 32:16/19/−3/3/interior/0 33:13/8/+5/5/edge/0
res s0 c=321: 23:14/16/−2/2/edge/0 24:24/21/+3/3/interior/0 25:27/25/+2/2/peak/0 26:27/27/0/0/interior/0 27:26/28/−2/2/interior/0 28:26/28/−2/2/interior/0 29:26/26/0/0/interior/0 30:25/23/+2/2/interior/0 31:21/19/+2/2/interior/0 32:11/13/−2/2/edge/0
res s0 c=340: 24:17/21/−4/4/edge/0 25:38/33/+5/5/interior/0 26:47/43/+4/4/peak/0 27:45/50/−5/5/interior/1 31:44/50/−6/6/interior/1 32:47/43/+4/4/interior/0 33:37/33/+4/4/interior/0 34:17/20/−3/3/edge/0
res s0 c=342: 27:−16/−19/+3/3/peak/0 28:−27/−20/−7/7/interior/0 29:−18/−21/+3/3/interior/1 34:−16/−18/+2/2/interior/1 35:−17/−16/−1/1/edge/0
res s0 c=343: 26:−31/−29/−2/2/edge/0 27:−26/−29/+3/3/peak/0
```

m15 (68 sites):

```
res m15 c=257: 23:12/13/−1/1/edge/0 24:18/16/+2/2/interior/0 25:20/19/+1/1/peak/0 26:20/21/−1/1/interior/0 27:19/21/−2/2/interior/0 28:20/21/−1/1/interior/0 29:20/20/0/0/interior/0 30:19/17/+2/2/interior/0 31:16/14/+2/2/interior/0 32:8/10/−2/2/edge/0
res m15 c=277: 23:12/13/−1/1/edge/0 24:19/17/+2/2/interior/0 25:20/19/+1/1/peak/0 26:20/21/−1/1/interior/0 27:19/21/−2/2/interior/0 28:20/21/−1/1/interior/0 29:20/19/+1/1/interior/0 30:19/17/+2/2/interior/0 31:15/14/+1/1/interior/0 32:8/10/−2/2/edge/0
res m15 c=296: 24:16/22/−6/6/edge/0 25:37/30/+7/7/interior/0 26:46/36/+10/10/peak/0 27:40/41/−1/1/interior/0 28:30/44/−14/14/interior/1 31:38/41/−3/3/interior/1 32:46/37/+9/9/interior/0 33:37/31/+6/6/interior/0 34:16/23/−7/7/edge/0
res m15 c=301: 23:12/12/0/0/edge/0 24:18/22/−4/4/interior/0 25:24/29/−5/5/interior/0 26:37/34/+3/3/interior/0 27:48/37/+11/11/peak/0 28:47/38/+9/9/interior/0 29:35/36/−1/1/interior/0 30:23/32/−9/9/interior/0 31:16/26/−10/10/interior/0 32:13/18/−5/5/interior/0 33:18/7/+11/11/edge/0
res m15 c=321: 23:14/16/−2/2/edge/0 24:24/22/+2/2/interior/0 25:29/27/+2/2/interior/0 26:31/30/+1/1/peak/0 27:31/32/−1/1/interior/0 28:29/32/−3/3/interior/0 29:28/30/−2/2/interior/0 30:28/27/+1/1/interior/0 31:24/22/+2/2/interior/0 32:14/15/−1/1/edge/0
res m15 c=340: 24:16/22/−6/6/edge/0 25:38/31/+7/7/interior/0 26:47/37/+10/10/interior/0 27:40/42/−2/2/interior/0 28:30/45/−15/15/interior/1 31:40/42/−2/2/interior/1 32:48/38/+10/10/peak/0 33:38/31/+7/7/interior/0 34:14/23/−9/9/edge/0
res m15 c=342: 27:−13/−15/+2/2/peak/0 28:−20/−16/−4/4/interior/0 29:−14/−16/+2/2/interior/1 34:−19/−20/+1/1/interior/1 35:−21/−20/−1/1/edge/0
res m15 c=343: 25:−22/−25/+3/3/edge/0 26:−34/−27/−7/7/interior/0 27:−26/−29/+3/3/interior/1 289:−15/−15/0/0/peak/1
```

Per-column residual aggregates (hits/near/2–3/4+ + sign split —
derived from the tables above):

| Frame | col | n | 0 | 1 | 2–3 | 4+ | pos | neg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 257 | 10 | 1 | 1 | 7 | 1 | 4 | 5 |
| s0 | 277 | 10 | 1 | 1 | 8 | 0 | 4 | 5 |
| s0 | 296 | 9 | 0 | 1 | 0 | 8 | 4 | 5 |
| s0 | 301 | 11 | 0 | 4 | 3 | 4 | 5 | 6 |
| s0 | 321 | 10 | 2 | 0 | 8 | 0 | 4 | 4 |
| s0 | 340 | 8 | 0 | 0 | 1 | 7 | 4 | 4 |
| s0 | 342 | 5 | 0 | 1 | 3 | 1 | 3 | 2 |
| s0 | 343 | 2 | 0 | 0 | 2 | 0 | 1 | 1 |
| m15 | 257 | 10 | 1 | 4 | 5 | 0 | 4 | 5 |
| m15 | 277 | 10 | 0 | 6 | 4 | 0 | 5 | 5 |
| m15 | 296 | 9 | 0 | 1 | 1 | 7 | 4 | 5 |
| m15 | 301 | 11 | 1 | 1 | 1 | 8 | 4 | 6 |
| m15 | 321 | 10 | 0 | 4 | 6 | 0 | 5 | 5 |
| m15 | 340 | 9 | 0 | 0 | 2 | 7 | 4 | 5 |
| m15 | 342 | 5 | 0 | 2 | 2 | 1 | 3 | 2 |
| m15 | 343 | 4 | 1 | 0 | 2 | 1 | 2 | 1 |

Sign-run table (auxiliary, no bar — maximal runs of equal res
sign (+/−/0) over row order per column per frame):

| Frame | c257 | c277 | c296 | c301 | c321 | c340 | c342 | c343 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 runs | 6 | 6 | 5 | 6 | 7 | 5 | 4 | 2 |
| m15 runs | 6 | 5 | 5 | 5 | 5 | 5 | 4 | 4 |

(Residuals alternate sign down every column: 5–7 runs on the
n≥8 positive columns both frames; no column reads single-signed
beyond n=2.)

2–3-bin census: the 32 s0 + 23 m15 sites with |res|∈{2,3} by
column + row seat (c:row:res:seat):

s0 n23=32: 257:23:−2:edge 257:25:+2:peak 257:27:−2:interior
257:28:−2:interior 257:30:+2:interior 257:31:+2:interior
257:32:−2:edge 277:23:−2:edge 277:24:+3:interior
277:25:+2:peak 277:26:−2:interior 277:27:−3:interior
277:30:+3:interior 277:31:+3:interior 277:32:−3:edge
301:25:−2:interior 301:30:−3:interior 301:32:−3:interior
321:23:−2:edge 321:24:+3:interior 321:25:+2:peak
321:27:−2:interior 321:28:−2:interior 321:30:+2:interior
321:31:+2:interior 321:32:−2:edge 340:34:−3:edge
342:27:+3:peak 342:29:+3:interior 342:34:+2:interior
343:26:−2:edge 343:27:+3:peak.

m15 n23=23: 257:24:+2:interior 257:27:−2:interior
257:30:+2:interior 257:31:+2:interior 257:32:−2:edge
277:24:+2:interior 277:27:−2:interior 277:30:+2:interior
277:32:−2:edge 296:31:−3:interior 301:26:+3:interior
321:23:−2:edge 321:24:+2:interior 321:25:+2:interior
321:28:−3:interior 321:29:−2:interior 321:31:+2:interior
340:27:−2:interior 340:31:−2:interior 342:27:+2:peak
342:29:+2:interior 343:25:+3:edge 343:27:+3:interior.

Census seat split:

| Frame | n23 | peak | edge | interior | holeadj |
| --- | ---: | ---: | ---: | ---: | ---: |
| s0 | 32 | 5 | 8 | 19 | 2 |
| m15 | 23 | 1 | 4 | 18 | 4 |
| pooled | 55 | 6 | 12 | 37 | 6 |

(s0 peak seats: 257:25, 277:25, 321:25, 342:27, 343:27. m15
peak seat: 342:27 only. s0 holeadj: 342:29, 342:34. m15
holeadj: 296:31, 340:31, 342:29, 343:27.)

Curvature table: per-column ∩ depth (−a×span²) vs residual
spread (mean|res| + max|res|):

| Frame | col | a | span | depth | mean\|res\| | max\|res\| |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s0 | 257 | −0.689394 | 9 | 55.8409 | 1.9000 | 4 |
| s0 | 277 | −0.640152 | 9 | 51.8523 | 2.2000 | 3 |
| s0 | 296 | −0.404340 | 10 | 40.4340 | 9.4444 | 18 |
| s0 | 301 | −1.159674 | 10 | 115.9674 | 2.7273 | 5 |
| s0 | 321 | −0.678030 | 9 | 54.9205 | 1.7000 | 3 |
| s0 | 340 | −1.385542 | 10 | 138.5542 | 4.3750 | 6 |
| s0 | 342 | +0.205138 | 8 | −13.1288 | 3.2000 | 7 |
| s0 | 343 | fb | 1 | N/A | 2.5000 | 3 |
| m15 | 257 | −0.481061 | 9 | 38.9659 | 1.4000 | 2 |
| m15 | 277 | −0.481061 | 9 | 38.9659 | 1.4000 | 2 |
| m15 | 296 | −0.868259 | 10 | 86.8259 | 7.0000 | 14 |
| m15 | 301 | −1.143357 | 10 | 114.3357 | 6.1818 | 11 |
| m15 | 321 | −0.795455 | 9 | 64.4318 | 1.7000 | 3 |
| m15 | 340 | −0.936376 | 10 | 93.6376 | 7.5556 | 15 |
| m15 | 342 | −0.021758 | 8 | 1.3925 | 2.0000 | 4 |
| m15 | 343 | +0.007831 | 264 | −545.7964 | 3.2500 | 7 |

(s0 max depth c340 138.55; s0 max mean|res| c296 9.44. m15 max
depth c301 114.34; m15 max mean|res| c340 7.56. m15 c343
span=264 via the r289 far-row site. Sign split pooled:
pos=60 neg=66 zero=7 over 133 sites; nonzero pos share
60/126=0.4762.)

### Positive control (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 P1 (parabolic 8,11,12,11,8) | a/b/c ±3.3e-11, preds exact, res 0×5, 5/5, depth 16.0 | exact | True |
| C-P1 P2 (parabolic 16,19,20,19,16) | a/b/c ±3.3e-11, preds exact, res 0×5, 5/5, depth 16.0 | exact | True |
| C-P1 T1 (triangle 8,10,12,10,8) | a/b/c ±2.9e-11, preds 8,10,11,10,8, res 0,0,+1,0,0, 4/5, depth 96/7 | exact | True |
| C-P1 T2 (asymmetric 8,9,12,10,8) | a/b/c ±3.5e-11, preds 8,10,11,10,8, res 0,−1,+1,0,0, 3/5, depth 88/7 | exact | True |

(All 4 pseudo-columns: seats edge/interior/peak/interior/edge
+ holeadj all False + empty 2–3 census exact. Pooled
pass=True. Full tables in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+m15: fits + scores + ladder both
frames) pass1 `ef39e866…909` vs pass2 `ef39e866…909`,
identical=True; cell counts identical=True; tail counts
identical=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; M26 TRI exact hits reproduced
by refit scope — 0 new explained, attribution not explanation):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | TRI exact hits (M26) | 2475 | 18 | 0.0073 |
| m15 | TRI exact hits (M26) | 2539 | 16 | 0.0063 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_QUADLAST | QUAD fewest hits among 4 fits, s0 AND m15 | 4<12/15/18 + 3<12/13/16 — met |
| H2_MASS23 | pooled QUAD 2–3 sites ≥ 50 | 55 (32+23) — met |
| H3_PEAKSEAT | pooled 2–3 at peak rows, share ≥ 0.50 | 6/55 = 0.1091 — not met |
| H4_EDGESEAT | pooled 2–3 at band edges, share ≥ 0.50 | 12/55 = 0.2182 — not met |
| H5_SIGNBIAS | pooled nonzero res>0, share ≥ 0.60 | 60/126 = 0.4762 — not met |
| H6_DEPTH | s0 max-depth col reads max mean\|res\| | c340 depth vs c296 spread — not met |
| H7_ZEROCOL | s0 cols with 0 QUAD hits, share ≥ 0.50 | 5/8 = 0.6250 — met |
| N | residual + census + curvature tables + standing | 18/16 explained (M26, 0 new); 47/52 named-col stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (16/16 a/b/c 6dp + 4/3 hits + all miss bins +
errvalues + colhits match M26 exactly) and by ladder column
(QUAD worst-or-tied on 8/8 s0 + 7/8 m15 columns; m15 c343 the
sole exception at 1v2/0/0). Task 2 discriminates by seat (2–3
mass reads 37/55 interior vs 6/55 peak vs 12/55 edge with 6/55
hole-adjacent), by column (s0 c277/c321 carry 8/8 of the 32
while c296 carries 0 with max|res| 18; m15 c321 carries 6/23),
by sign (residuals alternate down-column at 5–7 sign runs with
pooled pos share 0.4762), and by depth-vs-spread (s0 deepest ∩
c340 138.55 vs worst spread c296 9.44; m15 deepest c301 114.34
vs worst spread c340 7.56).

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
| interior far tail, TRI-hit | 18 of cell 7 (0.7%) | δ=TRI pred exact, named-col scope (M26, refit) |
| interior far tail, standing | 84 of cell 7 (3.4%) | 47 named-col + 37 outside-named; stands (this run) |
| standing interior remainder | 2457 of cell 7 (99.3%) | 2475 − 18 TRI hits |
| standing remainder (total) | 22797 (99.9% of R_0) | 18 B tail-explained; rest split above |

Screenshot: present by rule. The evidence residual map
(`m54-residmap.png`, 88595 B of 5242880 budget) colors s0
named-column sites by QUAD |res| bin (hit 4 / near 8 / 2–3 32 /
4+ 21); DESIGN.md admits an evidence copy iff some s0 named
column with n≥8 reads QUAD 2–3 mass ≥ 6 — c321 (mass 8, n=10)
qualifies (c277 mass 8 and c257 mass 7 also clear the bar).

Recorded without verdict: the 8×2 QUAD fits read 16/16
M26-exact with same-frame 4/65 + 3/68 and miss bins 32/14/6/1 +
23/12/12/0 (all errvalues + colhits M26-exact); the ladder
reads QUAD worst-or-tied on 15/16 column-frames with all 64
cells M26-exact; per-site residuals read 133 sites with pooled
sign split 60/66/7 and 5–7 sign runs per n≥8 column; the 2–3
census reads pooled 55 with seats 6 peak / 12 edge / 37
interior and 6 hole-adjacent; ∩ depth reads max on s0 c340
(138.55) and m15 c301 (114.34) while mean|res| reads max on s0
c296 (9.44) and m15 c340 (7.56); 47/52 named-column bytes stand
after TRI with 0 new bytes explained (attribution, not
explanation).

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| QUAD suite + residual/seat/census/depth pins + falsification bars, recorded before running | recorded | `DESIGN.md`: M26-verbatim QUAD + scoring + res/seat/census/depth joins, bars H1–H7/N |
| 8×2 fits + same-frame + ladder + wall/exit/shas/determinism | measured | §Step 2: 16/16 fits + 4/3 same-frame + 64-cell ladder; 0.1 s; re-run identical |
| residual + census + curvature tables + explained-vs-standing + gap rows | measured | §Step 2/3: 133-site residuals + 55-site census + 16-row curvature; 0 new explained, 47/52 stands; gaps below |
| screenshot if a residual map discriminates (or absence reasoned) | measured | present by rule: s0 c321 mass-8 2–3 at n=10 (want ≥6 at n≥8); 88595 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the second invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m54"
cp local/research/M54/m54.py local/research/M54/control.py local/research/M54/DESIGN.md "/Volumes/Extreme SSD/m54/"
python3 m54.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m26/m26.txt" "/Volumes/Extreme SSD/m54" /Users/bradrichardson/dev/ssx3/local/research/M54 > m54.txt 2>&1
python3 control.py > control.txt 2>&1
cp "/Volumes/Extreme SSD/m54/m54-residmap.png" local/research/M54/m54-residmap.png
```

## Paths

Evidence (committed): `local/research/M54/` — `DESIGN.md`
(suite + residual pins + bars, recorded before running),
`m54.py` (profiles + QUAD fits + scoring + ladder + residuals +
census + curvature + PNG writer), `control.py`
(known-quadratic synthetic control),
`m54-residmap.png` (residual map, 88595 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m54/` —
`m54.txt` (receipt: shas, baselines, Task-1 profiles both
frames, 8×2 fits, M26 match, same-frame scores, ladder, Task-2
residuals + census + curvature + sign, re-run, PNG size),
`control.txt`, `m54.py`, `control.py`, `DESIGN.md` (working
copies), `m54-residmap.png` (working copy, 88595 B). No writes
into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`, `m28/`, `m29/`,
`m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`, `m36/`, `m37/`,
`m38/`, `m39/`, `m40/`, `m41/`, `m42/`, `m43/`, `m44/`, `m45/`,
`m46/`, `m47/`, `m48/`, `m49/`, `m50/`, `m51/`, `m52/`, `m53/`,
or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Interior-run failure structure (new): 37/55 pooled 2–3
   sites read interior seats with 5–7 sign runs per n≥8
   column — residuals alternate down-column rather than
   pooling at peaks/edges. Needs its own brief only if
   run-local structure matters: per-run residual tables
   (run lengths + within-run |res| profiles), offline — no
   new harness code.
2. Ragged-column catastrophic miss (new): c296/c340 read
   max|res| 18/15 with mean|res| 9.44/7.56 while smooth
   257/277/321 read max ≤4 with mean ≤2.2 — ragged profiles
   fail outside the 2–3 bin entirely (s0 c296 carries 0 of
   the 32). Needs its own brief only if ragged-vs-smooth
   matters: per-site profile-vs-fit tables on ragged columns,
   offline — no new harness code.
3. m15 c343 span-264 leverage (new, minor): the r289 far-row
   site stretches the fit span to 264 rows, pinning m15 c343
   curvature at +0.01 with depth −545.80. Needs its own brief
   only if outlier leverage matters: leave-one-row-out QUAD
   tables on c343, offline — no new harness code.
4. Peak-seat failure asymmetry (new, minor): s0 2–3 sites read
   5/32 peak seats vs m15 1/23 (342:27 only). Needs its own
   brief only if peak failure matters: per-peak residual
   tables across further frames, offline — no new harness
   code.
5. Low-drift no-keep split (M53 gap 3 / M51 gap 1, still open):
   c296/c301 read L1 2/4 but pooled kept 0/0, while c257/c340
   (L1 15/10) keep 2 each. Needs its own brief only if
   drift-vs-survival matters: per-site kept-hit residual
   tables, offline — no new harness code.
6. Height-vs-edge leg attribution (M53 gap 4 / M51 gap 2, still
   open): |Δh|≥5 reads 3/8 while |Δe|≥3 reads 6/8. Needs its
   own brief only if leg attribution matters: per-leg ablation
   tables, offline — no new harness code.
7. c340 peak-shift survival (M53 gap 5 / M51 gap 3, still open,
   minor): c340 Δp=+6 (26→32) keeps pooled 2. Needs its own
   brief only if peak-shift survival matters: per-row
   prediction tables around shifted peaks, offline — no new
   harness code.
8. Peak-row agreement without value agreement (M53 gap 6 / M51
   gap 4 / M26 gap 2, still open): 5/8 columns share peak rows
   cross-frame but only 6/65 shared-site δ values agree (M25
   H5). Needs its own brief only if peak anchoring matters:
   peak-anchored residual tables, offline — no new harness
   code.
9. CONST cross-frame collapse (M53 gap 8 / M51 gap 7 / M26 gap
   5 / M25 gap 2, still open): s0 column medians score 0/68 on
   m15 (1/65 the other way) vs 12/13 same-frame. Needs its own
   brief only if column-value mapping matters: per-column
   median drift tables s0 vs m15, offline — no new harness
   code.
10. m15 c343 row-289 site (M53 gap 9 / M51 gap 8 / M26 gap 6 /
    M25 gap 3, still open): one tail site 262 rows below its
    column's band (hole span 28–288), also m15 c343's argmax
    peak and QUAD hit (res 0) under the near-flat fit. Needs
    its own brief only if outlier isolation matters: far-row
    tail-site census, offline — no new harness code.
11. SIGN-corrected near-hit mass (M53 gap 10 / M51 gap 9 / M26
    gap 7 / M24 gap 1, still open): 35 s0 / 38 m15 tail bytes
    read |err|=1 after the best M24 correction vs 21/28 exact.
    Needs its own brief only if second-order structure
    matters: residual-sign tables around K45++SIGN, offline —
    no new harness code.
12. Streak-column residual coherence (M53 gap 11 / M51 gap 10 /
    M26 gap 8 / M24 gap 2, still open): s0 c257 reads r∈{−3,−2,0}
    only, c296 reads all |r|≤1, c342 reads all r≥1 (M26/M51/M53/
    M54 worked δ-level, not r-level). Needs its own brief only
    if column-local correction matters: per-column r-profile
    tables + column-constant fits, offline — no new harness
    code.
13. Gap-bin 32–63 ±1 concentration (M53 gap 12 / M51 gap 11 /
    M26 gap 9 / M24 gap 3, still open): 16/32 s0 + 31/49 m15
    |r|=1 sites sit in gap bin 32–63. Needs its own brief only
    if gap-local rounding matters: per-gap-value r tables
    within 32–63, offline — no new harness code.
14. POS cross-frame collapse (M53 gap 13 / M51 gap 12 / M26 gap
    10 / M23 gap 3, still open): POS cell medians read 7/16
    same-frame but 1/2 cross-frame. Needs its own brief only
    if position-value mapping matters: per-cell median drift
    tables s0 vs m15, offline — no new harness code.
15. Shape-733 tail divergence (M53 gap 14 / M51 gap 13 / M26 gap
    11 / M23 gap 4, still open): shape 733's tail map reads
    Jaccard 0.6694 vs s0 (100 B) while 727/764 shapes read
    byte-identical. Needs its own brief: per-byte attribution
    of 733's private sites, offline — no new harness code.
16. m15 private tail sites (M53 gap 15 / M51 gap 14 / M26 gap 12
    / M23 gap 5, still open): 64/134 m15 tail sites never recur
    on any M16 shape (occ 0; Jaccard 0.4132). Needs its own
    brief only if cross-sample tail identity matters:
    second-sample tail family, offline — no new harness code.
17. Shape-700 map divergence (M53 gap 16 / M51 gap 15 / M26 gap
    13 / M21 gap 1, still open): shape 700's static map reads
    Jaccard 0.0747 vs s0 while 518/764 read byte-identical.
    Needs its own brief: per-byte attribution of 700's private
    sites, offline — no new harness code.
18. m15 static-map disjointness (M53 gap 17 / M51 gap 16 / M26
    gap 14 / M21 gap 2, still open): m15 shares 92/1476 static
    sites with s0 (Jaccard 0.0245). Needs its own brief only if
    cross-sample map identity matters, offline — no new harness
    code.
19. U/V co-residual mechanism (M53 gap 18 / M51 gap 17 / M26 gap
    15 / M21 gap 3, still open): same-pixel U&V co-residual
    reads 16.0×/21.6× independence. Needs its own brief only if
    chroma pairing matters, offline — no new harness code.
20. δ-sign mechanism (M53 gap 19 / M51 gap 18 / M26 gap 16 / M20
    gap 2, still open, minor): δ>0 on 80.9%/80.2% with
    P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full) ≈ 0.70 on both
    frames. Needs its own brief only if the sign asymmetry
    matters, offline — no new harness code.
21. m15 below-min far tail (M53 gap 20 / M51 gap 19 / M26 gap 17
    / M19 gap 3, still open, minor): 4 below-side bytes with
    dout ≥ 16 (max 47) on m15. Needs its own brief only if
    outlier isolation matters, offline — no new harness code.
22. Negative-share mechanism (M53 gap 21 / M51 gap 20 / M26 gap
    18 / M18 gap 2, still open): 93 negatives (worst −244)
    unattributed at byte level. Needs its own brief: per-shape
    added-residual maps + EFB-copy diffing, offline — no new
    harness code.
23. Odin port readiness (M53 gap 22 / M51 gap 21 / M26 gap 19 /
    M18 gap 3, still open): no Odin contract in-repo; handoff
    artifact stays `loo.txt` + dumps + synths. Needs its own
    brief once the consumer names its interface.
24. Top-HUD glyph residual isolation (M53 gap 23 / M51 gap 22 /
    M26 gap 20 / M18 gap 4, still open): bottom-HUD draws
    identified; top-band glyph edges in the long tail. Needs its
    own brief if draw-level top-HUD isolation matters.
25. Per-carrier weight centers (M53 gap 24 / M51 gap 23 / M26 gap
    21 / M18 gap 5, still open, optional): effect-draw argmins
    at the fine-grid edge. Needs its own brief only if per-draw
    filter centers matter.

## What I could not do

1. No cross-shape check: the brief asks same-frame residuals
   only, so shapes 1/2/733 are unscored — tabled scope, not
   chased.
2. No near-hit merging: 26 pooled near-hits stay separate
   from the 7 exact hits by rule.
3. c341 unscored: 0 s0 / 1 m15 sites — membership-guarded
   but outside the brief's 8 fit columns.
4. Float paths: QUAD runs OLS in float64 with half-away
   rounding (per DESIGN.md), not exact-integer — tabled as
   implemented; control a/b/c gated by ±1e-6 tolerance.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M54/`: `DESIGN.md`, `m54.py`,
`control.py`, `m54-residmap.png` (88595 B), `REPORT.md` (this
file).
