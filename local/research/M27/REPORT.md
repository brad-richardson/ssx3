# M27 — Shape-733 tail divergence: per-byte attribution of private sites: REPORT

M22 gap 2 (carried M23 gap 4 → M26 gap 11) worked at table level:
shape 733's tail recomputes to 100 B at Jaccard 0.6694 vs s0
(inter 81, union 121 — M22 matched exactly, stop rule not
triggered), splitting into 19 private + 21 missing + 81 shared
sites, all luma on both sides. All 19 privates and all 21
missings read non-cell on the other frame (0 near-misses, 0 far:
H1 0.0000, H2 1.0000); 15/19 privates read static (gap 0) on s0.
The divergence is two whole-column swaps: s0's c301 (11 sites,
r23–33) + c321 (10 sites, r23–32) read absent on 733, replaced
by c303 (9 sites, r25–33) + c323 (10 sites, r25–34); no private
lies within 1 px of a shared site (H3 0.0000); 4/6 H5 streak
columns survive (H5 met at the bar). 731 cross-check: 100 B at
0.6833 (inter 82, union 120), 18 + 20 + 82, the same column-swap
shape on a disjoint column pair (c257/c277 → c259/c279) with
J(P_733,P_731) = 0.0000 (H6 not met). Fully offline — no lease
of any kind, no boots, no harness code, no `adb`. No device
work. Runbook `local/muse/prompts/M27.md`. Tables, no verdicts.

Headers read first: `local/research/M22/REPORT.md` (all of it:
102 s0 tail, 100% luma, top-band + dec-9 heavy, 25 8-conn comps,
streak columns c257/277/296/301/321/340–343, max 1 B in any
carrier mask, 727/764 maps byte-identical to s0, J(T_s0,T_m15)
0.4132, gaps ≥17 mean ~54, ρ peak [0.4,0.5), sign-gap agreement
90.2%) plus `local/research/M23/REPORT.md` (K45+ transfer table:
733 scores 14/100 like s0 — values transfer, the SET diverges).

Time box 4 hours (start 2026-09-20 03:00 EDT); used about 0.1.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m26/` — all outputs went to the new
`/Volumes/Extreme SSD/m27/`): the s0/733/731 triplets,
`loo.txt`, the M15 triplet (baseline guard only), the top-10
carrier triplets, and `m22.txt` (match target). Work dir
`/Volumes/Extreme SSD/m27/`; evidence `local/research/M27/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M26):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0733 | `e60cd548…79444a0` |
| m16-mid-s0733 | `49a17a53…eb017ab67` |
| m16-full-s0733 | `97d16216…c8895df70` |
| m16-v0-s0731 | `a3812010…86a34135` |
| m16-mid-s0731 | `f2349d19…5833d8290` |
| m16-full-s0731 | `e1d2d409…38f80ecfe7` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m22.txt | `6d38452e…d626aac` |

(Full hexes in `m27.txt` §inputs, plus all 30 top-10-carrier
triplet bins.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M26 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads 22815/22780/22766 on s0/733/731, all
equal. M22 target rows reprinted from `m22.txt` in the receipt
(733: 100 B, 0.6694; 731: 100 B, 0.6833). Mismatch rule
(DESIGN.md) not triggered.

## Runs (offline estimators)

One `m27.py` invocation (the receipt, 1.5 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m27.py receipt | 1.5 s | exit 0; all guards pass; canon `05b0ed74…d4fba3` |
| control.py C-P1 + C-P2 | <1 s | green; sets + Jaccards exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Task 1 (733 attrib + joins) | 2 | 0.1 s |
| Task 2 (displace + comps + 731) | 3 | <1 s |
| Determinism re-run (Task 1 on s0+733) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m27.py` wall | — | 1.5 s |

## Step 2 — estimates

### Task 1 — private/missing site tables (733)

Cell-7 membership + tail membership recomputed from the dumps:
s0 2475 cell + 102 tail (sub-bins 28+74, max 47); 733 tail
100 B with J(T_733,T_s0) = 0.6694 (inter 81, union 121) —
M22's counts matched EXACTLY (stop rule not triggered). δ==0
count reads 0; P(δ>0) reproduces M19/M20 0.8093 on s0. Tail
planes read 100/0/0 on 733 (Y/U/V).

Sets: priv P_733 = 19, miss M_733 = 21, shared S = 81
(19 + 81 = 100 ✓, 21 + 81 = 102 ✓, 81/121 = 0.6694 ✓).

Private-site table (all 19: offset, plane, row, col; |δ_733|;
s0 status + |δ_s0|; signed gaps 733 vs s0):

| offset | plane | (r,c) | \|δ_733\| | s0 status | \|δ_s0\| | g_733 | g_s0 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 32606 | Y | (25,303) | 11 | noncell | n/a | −24 | 0 |
| 32646 | Y | (25,323) | 11 | noncell | n/a | −29 | 0 |
| 33886 | Y | (26,303) | 16 | noncell | n/a | −38 | 0 |
| 33926 | Y | (26,323) | 18 | noncell | n/a | −42 | 0 |
| 35166 | Y | (27,303) | 15 | noncell | n/a | −39 | 0 |
| 35206 | Y | (27,323) | 18 | noncell | n/a | −42 | 0 |
| 36446 | Y | (28,303) | 13 | noncell | n/a | −35 | 0 |
| 36486 | Y | (28,323) | 17 | noncell | n/a | −40 | 0 |
| 37726 | Y | (29,303) | 13 | noncell | n/a | −32 | 0 |
| 37766 | Y | (29,323) | 16 | noncell | n/a | −39 | 0 |
| 39006 | Y | (30,303) | 13 | noncell | n/a | −31 | 0 |
| 39046 | Y | (30,323) | 16 | noncell | n/a | −39 | 0 |
| 40286 | Y | (31,303) | 13 | noncell | n/a | −31 | 0 |
| 40326 | Y | (31,323) | 16 | noncell | n/a | −41 | 0 |
| 41566 | Y | (32,303) | 12 | noncell | n/a | −31 | 0 |
| 41606 | Y | (32,323) | 19 | noncell | n/a | −44 | −3 |
| 42846 | Y | (33,303) | 9 | noncell | n/a | −25 | −3 |
| 42886 | Y | (33,323) | 15 | noncell | n/a | −38 | −9 |
| 44166 | Y | (34,323) | 8 | noncell | n/a | −20 | −11 |

Summary: near 0 (0.0000), far 0 (0.0000), noncell 19 (1.0000).
Signed-gap equality 0/19, abs-gap equality 0/19. Other-frame
(s0) gaps: 15 zeros (static on s0) + −3/−3/−9/−11.

Missing-site table (all 21: |δ_s0|; 733 status + |δ_733|;
signed gaps s0 vs 733):

| offset | plane | (r,c) | \|δ_s0\| | 733 status | \|δ_733\| | g_s0 | g_733 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 30042 | Y | (23,301) | 18 | noncell | n/a | 43 | 0 |
| 30082 | Y | (23,321) | 14 | noncell | n/a | 36 | 0 |
| 31322 | Y | (24,301) | 29 | noncell | n/a | 67 | 0 |
| 31362 | Y | (24,321) | 24 | noncell | n/a | 57 | 0 |
| 32602 | Y | (25,301) | 33 | noncell | n/a | 79 | 5 |
| 32642 | Y | (25,321) | 27 | noncell | n/a | 63 | 0 |
| 33882 | Y | (26,301) | 41 | noncell | n/a | 93 | 21 |
| 33922 | Y | (26,321) | 27 | noncell | n/a | 63 | 0 |
| 35162 | Y | (27,301) | 47 | noncell | n/a | 106 | 34 |
| 35202 | Y | (27,321) | 26 | noncell | n/a | 62 | 0 |
| 36442 | Y | (28,301) | 46 | noncell | n/a | 104 | 33 |
| 36482 | Y | (28,321) | 26 | noncell | n/a | 64 | 0 |
| 37722 | Y | (29,301) | 39 | noncell | n/a | 90 | 18 |
| 37762 | Y | (29,321) | 26 | noncell | n/a | 63 | 0 |
| 39002 | Y | (30,301) | 32 | noncell | n/a | 76 | 4 |
| 39042 | Y | (30,321) | 25 | noncell | n/a | 61 | 0 |
| 40282 | Y | (31,301) | 25 | noncell | n/a | 59 | 0 |
| 40322 | Y | (31,321) | 21 | noncell | n/a | 49 | 0 |
| 41562 | Y | (32,301) | 16 | noncell | n/a | 37 | 5 |
| 41602 | Y | (32,321) | 11 | noncell | n/a | 25 | 0 |
| 42842 | Y | (33,301) | 13 | noncell | n/a | 27 | 20 |

Summary: near 0 (0.0000), far 0 (0.0000), noncell 21 (1.0000).
Signed-gap equality 0/21, abs-gap equality 0/21. Other-frame
(733) gaps: 13 zeros (static on 733) + 4/5/5/18/20/21/33/34.

Position join (s0-anchored: geometry bands, s0 P1 deciles with
edges matching m18.txt, named streak columns, M22-verbatim
carrier masks with removed counts + bands reproduced):

Band (all priv/miss in band 0; shared 48/25/8 = s0's 69/25/8
minus the 21 band-0 missings):

| band | priv n/share | miss n/share | shared n/share |
| ---: | ---: | ---: | ---: |
| 0 | 19 / 1.0000 | 21 / 1.0000 | 48 / 0.5926 |
| 1 | 0 / 0.0000 | 0 / 0.0000 | 25 / 0.3086 |
| 2 | 0 / 0.0000 | 0 / 0.0000 | 8 / 0.0988 |

Gradient decile (missings all dec-9; privates spread
0/1/3/7/8/9):

| dec | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 0 | 3 | 0 | 0 |
| 1 | 1 | 0 | 0 |
| 2 | 0 | 0 | 0 |
| 3 | 8 | 0 | 0 |
| 4 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 |
| 6 | 0 | 0 | 2 |
| 7 | 2 | 0 | 2 |
| 8 | 1 | 0 | 6 |
| 9 | 4 | 21 | 71 |

(Dec-9 shares: priv 4/19 = 0.2105, miss 21/21 = 1.0000,
shared 71/81 = 0.8765. Miss + shared per-decile n sums to
M22's s0 tail deciles: 92 in dec-9 ✓.)

Streak columns (missings = all of c301 + c321; privates all
outside the named set, in c303/c323 — §Task 2.2):

| col | priv | miss | shared |
| ---: | ---: | ---: | ---: |
| 257 | 0 | 0 | 10 |
| 277 | 0 | 0 | 10 |
| 296 | 0 | 0 | 9 |
| 301 | 0 | 11 | 0 |
| 321 | 0 | 10 | 0 |
| 340 | 0 | 0 | 8 |
| 341 | 0 | 0 | 0 |
| 342 | 0 | 0 | 5 |
| 343 | 0 | 0 | 2 |
| other | 19 | 0 | 37 |

Carrier cut (inside counts; the 1 shared byte in 368's mask is
M22's tabled max-1 byte):

| rank/shape | priv_in | miss_in | shared_in |
| ---: | ---: | ---: | ---: |
| 1/694 – 3/701, 5–10 | 0 | 0 | 0 |
| 4/368 | 0 | 0 | 1 |

701 split: priv 0/19, miss 0/21, shared 0/81 (all outside).

### Task 2 — displacement check (733)

Nearest-shared-site Manhattan distance per private site (same
plane; 0 impossible by construction — guarded):

| (r,c) | dmin | (r,c) | dmin |
| --- | ---: | --- | ---: |
| (25,303) | 7 | (25,323) | 17 |
| (26,303) | 7 | (26,323) | 17 |
| (27,303) | 6 | (27,323) | 17 |
| (28,303) | 5 | (28,323) | 18 |
| (29,303) | 5 | (29,323) | 19 |
| (30,303) | 6 | (30,323) | 18 |
| (31,303) | 7 | (31,323) | 17 |
| (32,303) | 7 | (32,323) | 17 |
| (33,303) | 6 | (33,323) | 17 |
| — | — | (34,323) | 17 |

Hist: 1:0 2:0 3:0 4:0 5+:19 (d1 share 0.0000).

Missing mirror (c301 sites at dmin 3–6, c321 sites at 19–21):

Hist: 1:0 2:0 3:2 4:3 5+:16 (d1 share 0.0000; full per-site
rows in `m27.txt`).

Component view (8-conn on Y, M22 verbatim; U/V read 0/0 both
frames):

| Frame | comps | sizes 1/2/3–4/5–8/9+ | largest (share) |
| --- | ---: | ---: | --- |
| s0 | 25 | 9/3/5/3/5 | 11 (0.1078) |
| s733 | 25 | 9/3/5/3/5 | 10 (0.1000) |

s0 sizelist: `11 10 10 10 10 7 5 5 4 4 4 4 3 2 2 2 1×9`
(M22 reproduced). s733 sizelist:
`10 10 10 10 9 7 5 5 4 4 4 4 3 2 2 2 1×9`.

733's comp5+ rows (unchanged bboxes except the two swapped
streak columns):

| size | centroid (r,c) | bbox |
| ---: | ---: | --- |
| 10 | (275.4,314.1) | r[273,278]c[313,315] |
| 10 | (29.5,323.0) | r[25,34]c[323,323] |
| 10 | (27.5,277.0) | r[23,32]c[277,277] |
| 10 | (27.5,257.0) | r[23,32]c[257,257] |
| 9 | (29.0,303.0) | r[25,33]c[303,303] |
| 7 | (298.6,311.4) | r[296,301]c[311,312] |
| 5 | (27.4,342.4) | r[26,29]c[342,343] |
| 5 | (26.0,296.0) | r[24,28]c[296,296] |

(s0's c301 r[23,33] size-11 and c321 r[23,32] size-10 comps
read absent; c303 r[25,33] + c323 r[25,34] read in their
place. All other comp5+ bboxes identical to s0's.)

Streak-column presence (per named column n/rows/row-overlap):

| col | s0 n/rows | s733 n/rows | overlap | H5 present |
| ---: | --- | --- | ---: | --- |
| 257 | 10 / 23–32 | 10 / 23–32 | 10 | True |
| 277 | 10 / 23–32 | 10 / 23–32 | 10 | True |
| 296 | 9 / 24–34 | 9 / 24–34 | 9 | True |
| 301 | 11 / 23–33 | 0 / — | 0 | False |
| 321 | 10 / 23–32 | 0 / — | 0 | False |
| 340 | 8 / 24–34 | 8 / 24–34 | 8 | True |
| 341 | 0 / — | 0 / — | 0 | — |
| 342 | 5 / 27–35 | 5 / 27–35 | 5 | — |
| 343 | 2 / 26–27 | 2 / 26–27 | 2 | — |

(Row lists identical where overlap is full — in `m27.txt`.
H5: 4/6 present.)

### Task 2.3 — 731 cross-check

731 guard reads 100 B + J(T_731,T_s0) = 0.6833 (inter 82,
union 120) — M22 matched exactly, cross-check runs. Sets:
priv 18, miss 20, shared 82.

731 private sites (all Y, all noncell on s0; c259 r25–33 +
c279 r25–33):

| (r,c) range | n | \|δ_731\| range | g_731 sign | g_s0 values |
| --- | ---: | --- | --- | --- |
| c259 r25–33 | 9 | 10–18 | all − | 0×8, −1 |
| c279 r25–33 | 9 | 11–19 | all − | 0×5, −1/−3/−6/−9 |

(Full 18 per-site rows in `m27.txt`. Summary: near 0, far 0,
noncell 18 (1.0000); gap equalities 0/18 + 0/18.)

731 missing sites (all Y, all noncell on 731; c257 r23–32 +
c277 r23–32 — all of both s0 columns):

| (r,c) range | n | \|δ_s0\| range | g_s0 sign | g_731 values |
| --- | ---: | --- | --- | --- |
| c257 r23–32 | 10 | 13–30 | all + | all 0 |
| c277 r23–32 | 10 | 13–28 | all + | all 0 |

(Summary: near 0, far 0, noncell 20 (1.0000); gap
equalities 0/20 + 0/20.)

731 position join (same s0-anchored tables):

| cut | priv | miss | shared |
| --- | --- | --- | --- |
| band 0/1/2 | 18/0/0 | 20/0/0 | 49/25/8 |
| dec-9 share | 4/18 (0.2222) | 20/20 (1.0000) | 72/82 (0.8780) |
| dec rest (priv) | 0:4, 3:8, 7:2 | — | 6:2, 7:2, 8:6 |
| streak miss cols | — | c257:10, c277:10 | c301:11, c321:10 |
| streak priv | other:18 | — | other:37 |
| carrier inside | all 0 | all 0 | 1 (in 368) |
| 701 split in/out | 0/18 | 0/20 | 0/82 |

731 displacement hists: priv 1:0 2:0 3:0 4:0 5+:18
(d1 0.0000; c259 sites at 37–38, c279 at 17–18); miss 1:0
2:0 3:0 4:0 5+:20 (d1 0.0000; c257 at 39–40, c277 at 19–20).

Set overlaps: J(P_733,P_731) = 0.0000 (inter 0, union 37);
J(M_733,M_731) = 0.0000 (inter 0, union 41).

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-P1 (known privates, N=20, ±8) | 20 priv, 0 miss, J 0.8361, values exact, originals unchanged | exact | True |
| C-P2 (known missings, N=20, +1) | 20 miss, 0 priv, J 0.8039, values exact, others unchanged | exact | True |

(Pool: 248 bulk gap≥17 candidates for C-P1 (+8×8/−8×12);
102 tail candidates for C-P2 with 0 −1 fallbacks. Both
cells read fixed. Full tables in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+733) pass1 `05b0ed74…d4fba3` vs
pass2 `05b0ed74…d4fba3`, identical=True; sets
identical=True (priv 19, miss 21, shared 81).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | ---: | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_NEARMISS | 733-privates with s0-bulk \|δ\|∈{6,7}, share ≥ 0.50 | 0/19 = 0.0000 — not met |
| H2_SETCHANGE | 733-privates non-cell on s0, share ≥ 0.50 | 19/19 = 1.0000 — met |
| H3_DISPLACE | 733-privates within d1 of shared, share ≥ 0.50 | 0/19 = 0.0000 — not met |
| H4_LOCALIZE | \|priv−shared band-0\| ≥ 0.25 or \|priv−shared dec-9\| ≥ 0.25 | 0.4074 (band leg) / 0.6660 (decile leg) — met on both legs |
| H5_STREAK | ≥4 of 6 s0 streak columns present in 733 | 4/6 (c301/c321 absent) — met |
| H6_731SAME | J(P_733,P_731) ≥ 0.50 | 0.0000 (inter 0, union 37) — not met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
other-frame status absolutely (40/40 private+missing sites
non-cell, 0 bulk of any |δ| — neither near nor far), by gap
(0/40 signed- or abs-equal; other-frame gaps read 0 on 15/19
privates and 13/21 missings), by band (priv/miss 100% band-0
vs shared 59.3%), by decile (miss 100% dec-9 vs priv 21.1%
vs shared 87.7%), by streak column (miss = all of c301+c321;
priv = c303+c323, outside the named set), and by carrier
negatively (0 private/missing bytes in any top-10 mask).
Task 2 discriminates by displacement negatively (0/40 sites
of either set within d1 of shared; private columns sit 5–19
px from the nearest shared site), by component identity (25
comps both frames with identical bboxes except the two
swapped streak columns), and by cross-shape overlap
negatively (731's swap is disjoint from 733's: both set
Jaccards 0.0000).

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
| interior far tail | 102 of cell 7 (4.1%) | \|δ\|≥8, max 47; 100% Y; stands (this run) |
| standing interior remainder | 2475 of cell 7 (100%) | no rule; attribution tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence private-site map
(`m27-privmap.png`, 88708 B of 5242880 budget) colors s0
tail-Y by shared (green 81) / 733-private (yellow 19) /
missing (magenta 21); DESIGN.md admits an evidence copy iff
H4 meets AND the winning leg's majority level holds ≥8
private sites — the band leg meets (0.4074) with band 0
holding 19/19 privates.

Recorded without verdict: 733's divergence reads 19 + 21
sites at 100% luma with every last one non-cell on the other
frame (28/40 static there); the missing set is exactly s0's
c301 + c321 streak columns and the private set is exactly
two replacement streak columns c303 + c323; no private or
missing site lies within 1 px of a shared site; 4/6 H5
streak columns survive; 731 reads the same column-swap shape
(c257/c277 → c259/c279) on a fully disjoint site set; 0 B
explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| attribution suite + falsification bars, recorded before running | recorded | `DESIGN.md`: per-site cross-value tables, s0-anchored band/decile/streak/carrier joins, Manhattan displacement, 8-conn components + streak presence, 731 cross-check + set overlaps, bars H1–H6/N |
| private/missing/displacement/731 tables + wall/exit/shas/determinism | measured | §Step 2: 40 per-site rows + joins + hists + comps + 731 mirror; 1.5 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a private-site map discriminates (or absence reasoned) | measured | present by rule: H4 band leg + 19 privates in band 0; 88708 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m27"
cp local/research/M27/m27.py local/research/M27/control.py local/research/M27/DESIGN.md "/Volumes/Extreme SSD/m27/"
python3 m27.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m22/m22.txt" "/Volumes/Extreme SSD/m27" /Users/bradrichardson/dev/ssx3/local/research/M27 > m27.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m27/m27-privmap.png" local/research/M27/m27-privmap.png
```

## Paths

Evidence (committed): `local/research/M27/` — `DESIGN.md`
(suite + bars, recorded before running), `m27.py`
(attribution + joins + displacement + comps + 731 + PNG
writer), `control.py` (known-private/known-missing controls),
`m27-privmap.png` (private-site map, 88708 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m27/` —
`m27.txt` (receipt: shas, baselines, Task-1 per-site tables
both shapes, joins, displacement, comps, streak presence,
731 cross-check, re-run, PNG size), `control.txt`, `m27.py`,
`control.py`, `DESIGN.md` (working copies),
`m27-privmap.png` (working copy, 88708 B). No writes into
`m15/`, `m16/`, `m17/`, `m18/`, `m19/`, `m20/`, `m21/`,
`m22/`, `m23/`, `m24/`, `m25/`, `m26/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Column-pair swap mechanism (new): 733 swaps s0's
   c301/c321 for c303/c323 (+2 columns), 731 swaps c257/c277
   for c259/c279 (+2 columns) — why these pairs, why +2,
   what moves the columns? Needs its own brief: per-shape
   streak-column census across all 764 (which shapes move
   which columns, by how far), offline — no new harness
   code.
2. Below-0.95 shape family (new): M22 lists 9 shapes below
   0.95 (733/731/9/700/734/732/2/711/3); only 733 + 731 are
   attributed here. Needs its own brief: the same
   private/missing/displacement attribution for
   9/700/734/732/2/711/3, offline — no new harness code.
3. Static-on-other-frame privates (new, minor): 15/19
   733-privates + 13/18 731-privates read gap 0 (static) on
   s0 while tail on their own shape. Needs its own brief
   only if cross-shape membership matters: moved/static
   membership census s0 vs 733/731 at private sites, offline
   — no new harness code.
4. TRI cross-frame collapse (M26 gap 1, still open): TRI
   fit-s0→m15 reads 4/68 (2/65 the other way) vs 18/16
   same-frame. Needs its own brief only if shape transfer
   matters: per-column triangle-drift (p/h/e/w s0 vs m15)
   tables, offline — no new harness code.
5. Peak-row agreement without value agreement (M26 gap 2,
   still open): 5/8 columns share peak rows cross-frame but
   only 6/65 shared-site δ values agree. Needs its own
   brief only if peak anchoring matters: peak-anchored
   residual tables, offline — no new harness code.
6. Index-top argmax concentration (M26 gap 3, still open):
   6/8 s0 + 5/8 m15 argmax read top-third by index under
   the first-tie rule. Needs its own brief only if
   peak-position convention matters: plateau-aware peak
   tables, offline — no new harness code.
7. QUAD underfit (M26 gap 4, still open, minor): smooth
   quadratic reads 4/65 + 3/68 with 32/23 mass in the 2–3
   miss bin. Needs its own brief only if curvature
   matters: per-column quadratic-residual tables, offline —
   no new harness code.
8. CONST cross-frame collapse (M26 gap 5, still open): s0
   column medians score 0/68 on m15 (1/65 the other way) vs
   12/13 same-frame. Needs its own brief only if
   column-value mapping matters: per-column median drift
   tables s0 vs m15, offline — no new harness code.
9. m15 c343 row-289 site (M26 gap 6, still open): one tail
   site 262 rows below its column's band, m15 c343's argmax
   peak. Needs its own brief only if outlier isolation
   matters: far-row tail-site census, offline — no new
   harness code.
10. SIGN-corrected near-hit mass (M26 gap 7, still open): 35
    s0 / 38 m15 tail bytes read |err|=1 after the best M24
    correction vs 21/28 exact. Needs its own brief only if
    second-order structure matters: residual-sign tables
    around K45++SIGN, offline — no new harness code.
11. Streak-column residual coherence (M26 gap 8, still open):
    s0 c257 reads r∈{−3,−2,0} only, c296 reads all |r|≤1,
    c342 reads all r≥1. Needs its own brief only if
    column-local correction matters: per-column r-profile
    tables + column-constant fits, offline — no new harness
    code.
12. Gap-bin 32–63 ±1 concentration (M26 gap 9, still open):
    16/32 s0 + 31/49 m15 |r|=1 sites sit in gap bin 32–63.
    Needs its own brief only if gap-local rounding matters:
    per-gap-value r tables within 32–63, offline — no new
    harness code.
13. POS cross-frame collapse (M26 gap 10, still open): POS
    cell medians read 7/16 same-frame but 1/2 cross-frame.
    Needs its own brief only if position-value mapping
    matters: per-cell median drift tables s0 vs m15, offline
    — no new harness code.
14. m15 private tail sites (M26 gap 12, still open): 64/134
    m15 tail sites never recur on any M16 shape (occ 0;
    Jaccard 0.4132). Needs its own brief only if
    cross-sample tail identity matters: second-sample tail
    family, offline — no new harness code.
15. Shape-700 map divergence (M26 gap 13, still open): shape
    700's static map reads Jaccard 0.0747 vs s0 while
    518/764 read byte-identical. Needs its own brief:
    per-byte attribution of 700's private sites, offline —
    no new harness code.
16. m15 static-map disjointness (M26 gap 14, still open): m15
    shares 92/1476 static sites with s0 (Jaccard 0.0245).
    Needs its own brief only if cross-sample map identity
    matters, offline — no new harness code.
17. U/V co-residual mechanism (M26 gap 15, still open):
    same-pixel U&V co-residual reads 16.0×/21.6×
    independence. Needs its own brief only if chroma pairing
    matters, offline — no new harness code.
18. δ-sign mechanism (M26 gap 16, still open, minor): δ>0 on
    80.9%/80.2% with P(δ>0|v0>full) ≈ 0.90 vs P(δ>0|v0<full)
    ≈ 0.70 on both frames. Needs its own brief only if the
    sign asymmetry matters, offline — no new harness code.
19. m15 below-min far tail (M26 gap 17, still open, minor): 4
    below-side bytes with dout ≥ 16 (max 47) on m15. Needs
    its own brief only if outlier isolation matters, offline
    — no new harness code.
20. Negative-share mechanism (M26 gap 18, still open): 93
    negatives (worst −244) unattributed at byte level. Needs
    its own brief: per-shape added-residual maps + EFB-copy
    diffing, offline — no new harness code.
21. Odin port readiness (M26 gap 19, still open): no Odin
    contract in-repo; handoff artifact stays `loo.txt` +
    dumps + synths. Needs its own brief once the consumer
    names its interface.
22. Top-HUD glyph residual isolation (M26 gap 20, still open):
    bottom-HUD draws identified; top-band glyph edges in the
    long tail. Needs its own brief if draw-level top-HUD
    isolation matters.
23. Per-carrier weight centers (M26 gap 21, still open,
    optional): effect-draw argmins at the fine-grid edge.
    Needs its own brief only if per-draw filter centers
    matter.

(M26 gap 11 — this brief — worked at table level above.)

## What I could not do

1. No below-0.95 family beyond 731: shapes 9/700/734/732/2/
   711/3 are unattributed (gap 2 tables the follow-up).
2. No δ-sign columns: per-site tables carry |δ| magnitudes
   only, per brief (gap signs are signed in the receipt).
3. No per-shape column census: the +2 swap pattern is
   tabled for 733/731 only (gap 1 tables the 764-shape
   census).
4. U/V-native joins: tails read all-Y on every analyzed
   shape, so the co-located-U/V fallback paths are
   unexercised — tabled, not chased.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M27/`: `DESIGN.md`, `m27.py`,
`control.py`, `m27-privmap.png` (88708 B), `REPORT.md` (this
file).
