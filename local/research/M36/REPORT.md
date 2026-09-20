# M36 — Still-below unnamed cells: per-site value attribution for 2/3/700: REPORT

M35 gap 4 (= M34 gap 2) worked at table level: 2/3/700's
unnamed rows recompute to the pinned k 6/7/8 with standings +
deltas exact on all 21 cells (FULL 764×33 TSV byte-identical
to `m34-census.tsv` — stop rule not triggered), splitting
into 24 extras + 10 missings. The 24 extras read 14 near / 0
far / 10 non-cell on s0 (H1 0.5833 — met; H2 0.4167 — not
met); the 10 missings read 0/0/10 on their own shapes (H3
1.0000 — met); extras read 23/24 band-1 pooled with all 3
shapes meeting the band leg (H4 met — 0.7755/0.7778/0.7111,
plus s3's decile leg 0.3990); missings read 7/10 +/+ gaps
(H5 0.7000 — met); 700's 18 headliner rows read 11/18 bulk
(H6 0.6111 — met, c54 10/10 bulk). Streak joins read N/A off
the named set (all other); carrier joins do NOT read N/A —
700-c54's 10 extras sit 10/10 inside the 701 mask. Fully
offline — no lease of any kind, no boots, no harness code, no
`adb`. No device work. Runbook `local/muse/prompts/M36.md`.
Tables, no verdicts.

Headers read first: `local/research/M35/REPORT.md` (all of it:
gap 4 = this brief — 2/3/700 move unnamed at k 6/7/8
(J 0.9159/0.9340/0.8462), their below-but-still divergence
located in unnamed columns by M34, not attributed; the M35
Task-1/2 method reused verbatim per shape, s0-anchored;
shape-9's reads this brief tables against: extras 1/14/7,
missings 2/2/4, 21/22 band-1, 8/8 ++ missings, extras med
13.0 / missings med 10.0).

Time box 4 hours (start 2026-09-20 04:27 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m35/` — all outputs went to the new
`/Volumes/Extreme SSD/m36/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), the top-10
carrier triplets, and `m34.txt` + `m34-census.tsv` (match
targets). Work dir `/Volumes/Extreme SSD/m36/`; evidence
`local/research/M36/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M35):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0002 | `56dccaff…8d2c8f8` |
| m16-mid-s0002 | `40f70d53…bd38be2` |
| m16-full-s0002 | `1593526a…0ed2417` |
| m16-v0-s0003 | `484d8499…e7fe462` |
| m16-mid-s0003 | `f0feefa7…93351fd` |
| m16-full-s0003 | `b11ecaa5…47f73d36` |
| m16-v0-s0700 | `cd5c2106…21af964` |
| m16-mid-s0700 | `d09dd3bb…25ae20` |
| m16-full-s0700 | `790c0826…dd5c482` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m34.txt | `21241ba5…babbf7f44` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m36.txt` §inputs, plus all 30 top-10-carrier
triplet bins. `m34.txt` 10762 B; `m34-census.tsv` 163262 B —
matches M34's committed size.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M35 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha over all 764×3 bins matches M28/M34/M35
(`6c906897…61fd423b1`). δ==0 violations read 0 shapes. s0
cell 2475 + tail 102 (sub-bins 28+74, max 47) + P(δ>0) 0.8093
match exactly; s2/s3/s700 cell reads 2469/2484/2605
(unpinned — tabled as measured); FULL unnamed TSV match
(all 764 rows: tail + J4 + all-33-column n/ov/pres) vs
`m34-census.tsv`; 2/3/700 rows match the pinned k 6/7/8 +
n/ov + standings + deltas exactly (§Task 1); pooled counts
read 5+4 / 4+3 / 15+3 exactly; all 34 pooled sites Y-plane.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m36.py` invocation (the receipt, 3.8 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m36.py receipt | 3.8 s | exit 0; all guards pass; canon `4f46798a…c9c2a54` |
| control.py C-VAL | <1 s | green; sets + J + values + standings exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + Y colrows) | 764 | 2.7 s |
| Task 1 (per-shape per-cell per-site + pooled + headliner + joins) | 4 | 0.2 s |
| Task 2 (per-cell joins + gap-sign + \|δ\| stats) | 4 | <1 s |
| Determinism re-run (Task 1 on s0+2/3/700, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m36.py` wall | — | 3.8 s |

## Step 2 — estimates

### Task 1 — 2/3/700 row reproduction + per-cell value tables

2/3/700 unnamed rows recomputed from the dumps (FULL TSV guard
passed first — all 764 rows byte-identical): k 6/7/8 with
n/ov/standings/deltas all exact (match=True on all 21 cells):

s2 (tail 103, J 0.9159):

| col | n/ov | n0 | miss/extra | delta | standing |
| ---: | --- | ---: | --- | ---: | --- |
| 311 | 5/4 | 4 | 0/1 | 1 | extra-only |
| 312 | 2/2 | 3 | 1/0 | 1 | missing-only |
| 313 | 4/3 | 4 | 1/1 | 2 | mixed |
| 314 | 6/6 | 7 | 1/0 | 1 | missing-only |
| 332 | 3/1 | 2 | 1/2 | 3 | mixed |
| 339 | 1/0 | 0 | 0/1 | 1 | extra-only |

s3 (tail 103, J 0.9340 — all 7 cells delta-1):

| col | n/ov | n0 | miss/extra | delta | standing |
| ---: | --- | ---: | --- | ---: | --- |
| 311 | 5/4 | 4 | 0/1 | 1 | extra-only |
| 313 | 3/3 | 4 | 1/0 | 1 | missing-only |
| 314 | 6/6 | 7 | 1/0 | 1 | missing-only |
| 316 | 2/1 | 1 | 0/1 | 1 | extra-only |
| 332 | 1/1 | 2 | 1/0 | 1 | missing-only |
| 336 | 1/0 | 0 | 0/1 | 1 | extra-only |
| 339 | 1/0 | 0 | 0/1 | 1 | extra-only |

s700 (tail 114, J 0.8462):

| col | n/ov | n0 | miss/extra | delta | standing |
| ---: | --- | ---: | --- | ---: | --- |
| 38 | 0/0 | 1 | 1/0 | 1 | missing-only (wipe) |
| 54 | 10/0 | 0 | 0/10 | 10 | extra-only |
| 299 | 1/0 | 0 | 0/1 | 1 | extra-only |
| 311 | 5/4 | 4 | 0/1 | 1 | extra-only |
| 313 | 5/4 | 4 | 0/1 | 1 | extra-only |
| 314 | 6/6 | 7 | 1/0 | 1 | missing-only |
| 332 | 2/1 | 2 | 1/1 | 2 | mixed |
| 620 | 1/0 | 0 | 0/1 | 1 | extra-only |

(Pooled: s2 5 extras + 4 missings; s3 4 + 3; s700 15 + 3;
grand 24 + 10 = 34 sites. Shared sites across shapes: the
(278,314) missing on all three; (276,313) missing on s2+s3;
(295,332) missing on all three; the (259,311) extra on s2+s700;
the (296,332) extra on s2+s700.)

Near-miss shares per shape per cell (H1/H2-style: near/far/
noncell on the other frame; extras vs s0, missings vs own Q):

| shape/col | extras near/far/non | missings near/far/non |
| ---: | --- | --- |
| s2 c311 | 0/0/1 | — |
| s2 c312 | — | 0/0/1 |
| s2 c313 | 1/0/0 | 0/0/1 |
| s2 c314 | — | 0/0/1 |
| s2 c332 | 0/0/2 | 0/0/1 |
| s2 c339 | 0/0/1 | — |
| s2 pooled | 1/0/4 | 0/0/4 |
| s3 c311 | 0/0/1 | — |
| s3 c313 | — | 0/0/1 |
| s3 c314 | — | 0/0/1 |
| s3 c316 | 1/0/0 | — |
| s3 c332 | — | 0/0/1 |
| s3 c336 | 1/0/0 | — |
| s3 c339 | 0/0/1 | — |
| s3 pooled | 2/0/2 | 0/0/3 |
| s700 c38 | — | 0/0/1 |
| s700 c54 | 10/0/0 | — |
| s700 c299 | 0/0/1 | — |
| s700 c311 | 0/0/1 | — |
| s700 c313 | 1/0/0 | — |
| s700 c314 | — | 0/0/1 |
| s700 c332 | 0/0/1 | 0/0/1 |
| s700 c620 | 0/0/1 | — |
| s700 pooled | 11/0/4 | 0/0/3 |
| grand pooled | 14/0/10 | 0/0/10 |

(Shape-9 reads extras 1/14/7, missings 2/2/4 — tabled for
contrast. All 14 extra-side nears: s2c313's (|δ_s0| 7) +
s3c316/c336's (7, 7) + all 10 c54's (6:2 7:8) + s700c313's
(7). Zero far sites on either side. Signed-gap equality:
extras 9/24 (s2 3/5: c311 + both c332; s3 2/4: c311 + c316;
s700 4/15: c311 + c313 + 2 c54 rows), missings 3/10 (s2c312,
s3c314, s700c314).)

Extra-site table s2 (all 5: cell, offset, plane, row, col;
|δ_2|; s0 status + |δ_s0|; signed gaps s2 vs s0):

| cell | offset | plane | (r,c) | \|δ_2\| | s0 status | \|δ_s0\| | g_2 | g_s0 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 311 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 313 | 375666 | Y | (293,313) | 8 | bulk | 7 | −18 | −19 |
| 332 | 379544 | Y | (296,332) | 20 | noncell | n/a | −41 | −41 |
| 332 | 380824 | Y | (297,332) | 9 | noncell | n/a | −20 | −20 |
| 339 | 307878 | Y | (240,339) | 9 | noncell | n/a | 19 | 17 |

Missing-site table s2 (all 4: |δ_s0|; s2 status + |δ_2|;
signed gaps s0 vs s2):

| cell | offset | plane | (r,c) | \|δ_s0\| | s2 status | \|δ_2\| | g_s0 | g_2 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 312 | 383344 | Y | (299,312) | 10 | noncell | n/a | 22 | 22 |
| 313 | 353906 | Y | (276,313) | 8 | noncell | n/a | 17 | 16 |
| 314 | 356468 | Y | (278,314) | 20 | noncell | n/a | 42 | 40 |
| 332 | 378264 | Y | (295,332) | 10 | noncell | n/a | −22 | −21 |

Extra-site table s3 (all 4):

| cell | offset | plane | (r,c) | \|δ_3\| | s0 status | \|δ_s0\| | g_3 | g_s0 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 311 | 330862 | Y | (258,311) | 34 | noncell | n/a | −71 | −71 |
| 316 | 339832 | Y | (265,316) | 8 | bulk | 7 | 18 | 18 |
| 336 | 305312 | Y | (238,336) | 8 | bulk | 7 | 17 | 16 |
| 339 | 305318 | Y | (238,339) | 8 | noncell | n/a | 17 | 18 |

Missing-site table s3 (all 3):

| cell | offset | plane | (r,c) | \|δ_s0\| | s3 status | \|δ_3\| | g_s0 | g_3 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 313 | 353906 | Y | (276,313) | 8 | noncell | n/a | 17 | 16 |
| 314 | 356468 | Y | (278,314) | 20 | noncell | n/a | 42 | 42 |
| 332 | 378264 | Y | (295,332) | 10 | noncell | n/a | −22 | −21 |

Extra-site table s700 (all 15):

| cell | offset | plane | (r,c) | \|δ_700\| | s0 status | \|δ_s0\| | g_700 | g_s0 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 54 | 313708 | Y | (245,54) | 8 | bulk | 7 | −23 | −22 |
| 54 | 314988 | Y | (246,54) | 8 | bulk | 7 | −23 | −23 |
| 54 | 316268 | Y | (247,54) | 8 | bulk | 7 | −24 | −23 |
| 54 | 322668 | Y | (252,54) | 8 | bulk | 7 | −22 | −21 |
| 54 | 323948 | Y | (253,54) | 8 | bulk | 7 | −23 | −22 |
| 54 | 330348 | Y | (258,54) | 8 | bulk | 7 | −23 | −22 |
| 54 | 331628 | Y | (259,54) | 8 | bulk | 7 | −22 | −22 |
| 54 | 355948 | Y | (278,54) | 8 | bulk | 6 | −22 | −21 |
| 54 | 357228 | Y | (279,54) | 8 | bulk | 6 | −22 | −21 |
| 54 | 362348 | Y | (283,54) | 8 | bulk | 7 | −22 | −21 |
| 299 | 32598 | Y | (25,299) | 34 | noncell | n/a | −71 | −72 |
| 311 | 332142 | Y | (259,311) | 17 | noncell | n/a | −37 | −37 |
| 313 | 373106 | Y | (291,313) | 8 | bulk | 7 | −19 | −19 |
| 332 | 379544 | Y | (296,332) | 20 | noncell | n/a | −42 | −41 |
| 620 | 218840 | Y | (170,620) | 11 | noncell | n/a | −24 | −23 |

Missing-site table s700 (all 3):

| cell | offset | plane | (r,c) | \|δ_s0\| | s700 status | \|δ_700\| | g_s0 | g_700 |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| 38 | 275276 | Y | (215,38) | 12 | noncell | n/a | 25 | 23 |
| 314 | 356468 | Y | (278,314) | 20 | noncell | n/a | 42 | 42 |
| 332 | 378264 | Y | (295,332) | 10 | noncell | n/a | −22 | −21 |

Headliner shape 700, tabled individually (full row lists +
value stats per cell):

c38 (missing-only wipe): s0 rows [215], s700 rows [] — miss
row [215]. Missing |δ_s0| [12], noncell, gap ++.

c54 (extra-only +10): s0 rows [], s700 rows [245, 246, 247,
252, 253, 258, 259, 278, 279, 283] — extra rows all 10.
Extras |δ_700| [8×10] (med 8.0, mean 8.0000), 10/10 bulk
(|δ_s0| 6:2 7:8), gaps 10/10 −−.

c299 (extra-only): s0 rows [], s700 rows [25] — extra row
[25]. Extra |δ_700| [34], noncell, gap −−.

c311 (extra-only): s0 rows [296, 297, 298, 299], s700 rows
[259, 296, 297, 298, 299] — extra row [259] (= s2's c311
extra site). Extra |δ_700| [17], noncell, gap −− (gap-equal
−37/−37).

c313 (extra-only): s0 rows [274, 275, 276, 292], s700 rows
[274, 275, 276, 291, 292] — extra row [291]. Extra |δ_700|
[8], bulk (|δ_s0| 7), gap −− (gap-equal −19/−19).

c314 (missing-only): s0 rows [269, 276, 277, 278, 287, 288,
289], s700 rows [269, 276, 277, 287, 288, 289] — miss row
[278] (= the s2/s3 c314 miss site). Missing |δ_s0| [20],
noncell, gap ++ (gap-equal 42/42).

c332 (mixed delta-2): s0 rows [295, 304], s700 rows [296, 304]
— miss row [295] (= the s2/s3 c332 miss site), extra row
[296] (= s2's c332 extra site). Extra |δ_700| [20], noncell,
gap −−; missing |δ_s0| [10], noncell, gap −−.

c620 (extra-only): s0 rows [], s700 rows [170] — extra row
[170]. Extra |δ_700| [11], noncell, gap −−.

### Task 2 — joins (where do still-below values live?)

Aggregate joins per shape (`s{Q}all`: that shape's extras /
missings / own shared — s2 5/4/98, s3 4/3/99, s700 15/3/99;
recomputed with M27/M35 machinery verbatim):

Band (pooled extras 23/24 band-1; pooled missings 9/10 band-1):

| shape | band | priv n/share | miss n/share | shared n/share |
| --- | ---: | --- | --- | --- |
| s2 | 0 | 0 / 0.0000 | 0 / 0.0000 | 69 / 0.7041 |
| s2 | 1 | 5 / 1.0000 | 3 / 0.7500 | 22 / 0.2245 |
| s2 | 2 | 0 / 0.0000 | 1 / 0.2500 | 7 / 0.0714 |
| s3 | 0 | 0 / 0.0000 | 0 / 0.0000 | 69 / 0.6970 |
| s3 | 1 | 4 / 1.0000 | 3 / 1.0000 | 22 / 0.2222 |
| s3 | 2 | 0 / 0.0000 | 0 / 0.0000 | 8 / 0.0808 |
| s700 | 0 | 1 / 0.0667 | 0 / 0.0000 | 69 / 0.6970 |
| s700 | 1 | 14 / 0.9333 | 3 / 1.0000 | 22 / 0.2222 |
| s700 | 2 | 0 / 0.0000 | 0 / 0.0000 | 8 / 0.0808 |

(The pooled band-0 extra is s700c299's (25,299); the pooled
band-2 missing is s2c312's (299,312).)

Gradient decile (extras spread 1/7/8 below dec-9; missings
all dec-9):

| shape | dec | priv | miss | shared |
| ---: | ---: | ---: | ---: | ---: |
| s2 | 0–6 | 0 | 0 | 2 (dec-6) |
| s2 | 7 | 1 | 0 | 2 |
| s2 | 8 | 0 | 0 | 6 |
| s2 | 9 | 4 | 4 | 88 |
| s3 | 0–6 | 0 | 0 | 2 (dec-6) |
| s3 | 7 | 1 | 0 | 2 |
| s3 | 8 | 1 | 0 | 6 |
| s3 | 9 | 2 | 3 | 89 |
| s700 | 1 | 1 | 0 | 0 |
| s700 | 0,2–6 | 0 | 0 | 2 (dec-6) |
| s700 | 7 | 1 | 0 | 2 |
| s700 | 8 | 2 | 0 | 6 |
| s700 | 9 | 11 | 3 | 89 |

(Dec-9 shares: s2 priv 4/5 = 0.8000, miss 4/4 = 1.0000,
shared 88/98 = 0.8980; s3 priv 2/4 = 0.5000, miss 3/3 =
1.0000, shared 89/99 = 0.8990; s700 priv 11/15 = 0.7333,
miss 3/3 = 1.0000, shared 89/99 = 0.8990.)

Streak columns (all 34 still-below sites in `other`; streak
joins N/A off the named set):

| shape | col | priv | miss | shared |
| --- | --- | ---: | ---: | ---: |
| s2/s3/s700 | 257/277/296/301/321/340/342/343 | 0 | 0 | 10/10/9/11/10/8/5/2 |
| s2/s3/s700 | 341 | 0 | 0 | 0 |
| s2 | other | 5 | 4 | 33 |
| s3 | other | 4 | 3 | 34 |
| s700 | other | 15 | 3 | 34 |

Carrier cut (NOT N/A: 700-c54's 10 extras sit 10/10 inside
the rank-3/s701 mask; every other priv/miss reads 0 in every
mask; the 1 shared byte in 368's mask is M22's tabled max-1
byte): all ranks priv_in=0 miss_in=0 except s700 rank3/s701
priv_in=10. 701 split: s2 priv 0/5, miss 0/4, shared 0/98;
s3 priv 0/4, miss 0/3, shared 0/99; s700 priv 10/15, miss
0/3, shared 0/99.

Per-cell band/decile table (extras band/dec, missings band/dec):

| shape/col | extras band | extras dec | missings band | missings dec |
| ---: | --- | --- | --- | --- |
| s2 c311 | 1 | 9:1 | — | — |
| s2 c312 | — | — | 2 | 9:1 |
| s2 c313 | 1 | 9:1 | 1 | 9:1 |
| s2 c314 | — | — | 1 | 9:1 |
| s2 c332 | 1,1 | 9:2 | 1 | 9:1 |
| s2 c339 | 1 | 7:1 | — | — |
| s3 c311 | 1 | 9:1 | — | — |
| s3 c313 | — | — | 1 | 9:1 |
| s3 c314 | — | — | 1 | 9:1 |
| s3 c316 | 1 | 9:1 | — | — |
| s3 c332 | — | — | 1 | 9:1 |
| s3 c336 | 1 | 7:1 | — | — |
| s3 c339 | 1 | 8:1 | — | — |
| s700 c38 | — | — | 1 | 9:1 |
| s700 c54 | 1×10 | 1:1 7:1 8:1 9:7 | — | — |
| s700 c299 | 0 | 9:1 | — | — |
| s700 c311 | 1 | 9:1 | — | — |
| s700 c313 | 1 | 9:1 | — | — |
| s700 c314 | — | — | 1 | 9:1 |
| s700 c332 | 1 | 9:1 | 1 | 9:1 |
| s700 c620 | 1 | 8:1 | — | — |

(The pooled dec-1 extra is a c54 row; the pooled dec-7
extras are s2c339's + s3c336's + a c54 row; the pooled dec-8
extras are s3c339's + a c54 row + s700c620's. Per-cell
streak/carrier lines: every cell reads all-other / 0-in /
701-all-out except s700c54 (701 10/10 in) — full lines in
`m36.txt`.)

Gap-sign table (pooled + per shape + per cell; g_Q × g_O signs):

Pooled extras (n=24): ++=4 −−=20 (++ share 0.1667).
Pooled missings (n=10): ++=7 −−=3 (++ share 0.7000).
s2 extras (n=5): ++=1 −−=4 (0.2000); s2 missings (n=4): ++=3
−−=1 (0.7500). s3 extras (n=4): ++=3 −−=1 (0.7500); s3
missings (n=3): ++=2 −−=1 (0.6667). s700 extras (n=15):
−−=15 (0.0000); s700 missings (n=3): ++=2 −−=1 (0.6667).

| shape/col | extras signs | missings signs |
| ---: | --- | --- |
| s2 c311 | −− | — |
| s2 c312 | — | ++ |
| s2 c313 | −− | ++ |
| s2 c314 | — | ++ |
| s2 c332 | −−,−− | −− |
| s2 c339 | ++ | — |
| s3 c311 | −− | — |
| s3 c313 | — | ++ |
| s3 c314 | — | ++ |
| s3 c316 | ++ | — |
| s3 c332 | — | −− |
| s3 c336 | ++ | — |
| s3 c339 | ++ | — |
| s700 c38 | — | ++ |
| s700 c54 | −−×10 | — |
| s700 c299 | −− | — |
| s700 c311 | −− | — |
| s700 c313 | −− | — |
| s700 c314 | — | ++ |
| s700 c332 | −− | −− |
| s700 c620 | −− | — |

(The pooled extras' 4 ++ are s2c339's + s3c316/c336/c339's;
the pooled missings' 3 −− are the shared (295,332) site on
all three shapes. No zero gaps anywhere — 34/34 sites read
++/−−.)

|δ| stats per shape per cell (|δ_Q| on extras, |δ_s0| on missings):

| shape/col | extras list (med) | missings list (med) |
| ---: | --- | --- |
| s2 c311 | [17] (17.0) | — |
| s2 c312 | — | [10] (10.0) |
| s2 c313 | [8] (8.0) | [8] (8.0) |
| s2 c314 | — | [20] (20.0) |
| s2 c332 | [9,20] (14.5) | [10] (10.0) |
| s2 c339 | [9] (9.0) | — |
| s3 c311 | [34] (34.0) | — |
| s3 c313 | — | [8] (8.0) |
| s3 c314 | — | [20] (20.0) |
| s3 c316 | [8] (8.0) | — |
| s3 c332 | — | [10] (10.0) |
| s3 c336 | [8] (8.0) | — |
| s3 c339 | [8] (8.0) | — |
| s700 c38 | — | [12] (12.0) |
| s700 c54 | [8×10] (8.0) | — |
| s700 c299 | [34] (34.0) | — |
| s700 c311 | [17] (17.0) | — |
| s700 c313 | [8] (8.0) | — |
| s700 c314 | — | [20] (20.0) |
| s700 c332 | [20] (20.0) | [10] (10.0) |
| s700 c620 | [11] (11.0) | — |

(Pooled extras: s2 min 8, med 9.0, mean 12.6000, max 20; s3
min 8, med 8.0, mean 14.5000, max 34; s700 min 8, med 8.0,
mean 11.3333, max 34. Pooled missings: s2 min 8, med 10.0,
mean 12.0000, max 20; s3 min 8, med 10.0, mean 12.6667, max
20; s700 min 10, med 12.0, mean 14.0000, max 20. Largest
extra |δ|: 34 (s3c311, s700c299), 20 (s2c332, s700c332), 17
(s2c311, s700c311); largest missing |δ|: 20 (c314 on all
three shapes), 12 (s700c38). Shape-9 reads extras med 13.0 /
missings med 10.0 — tabled for contrast.)

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-VAL (known 6 priv + 4 miss) | priv 6 exact, miss 4 exact, J 0.9074, values + gaps + standings exact, cell fixed, orig kept | exact | True |

(Priv pool: 248 bulk gap≥17 Y; +8×2/−8×4 at
(25,334)/(26–28,305)/(42,98)/(44,81) with orig |δ| all 1.
Miss pool: 102 tail; +1 landing ×4 at r23 of c257/277/301/
321, 0 −1 fallbacks. Spanned Y cols 81/98/257/277/301/305/
321/334 with per-cell standings 4×extra-only + 4×missing-
only, rows exact on all 8. Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+2/3/700: per-shape per-cell per-site
rows + per-shape pooled summaries + headliner stats +
aggregate joins, fresh loads incl. carriers) pass1
`4f46798a…c9c2a54` vs pass2 `4f46798a…c9c2a54`,
identical=True; 406/406 lines match=True; sets
identical=True (s2 extras 5, missings 4, shared 98; s3 4/3/99;
s700 15/3/99).

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_STILLNEAR | extras with s0-bulk \|δ\|∈{6,7}, share ≥ 0.50 | 14/24 = 0.5833 — met |
| H2_STILLSET | extras non-cell on s0, share ≥ 0.50 | 10/24 = 0.4167 — not met |
| H3_STILLMISS | missings non-cell on own shape, share ≥ 0.50 | 10/10 = 1.0000 — met |
| H4_STILLLOCALIZE | per shape: \|extra−shared band-1\| ≥ 0.25 or \|extra−shared dec-9\| ≥ 0.25 | s2 0.7755/0.0980, s3 0.7778/0.3990, s700 0.7111/0.1657 — met (band leg all 3 + s3 dec leg) |
| H5_STILLMISSGAP | missings +/+, share ≥ 0.50 | 7/10 = 0.7000 — met |
| H6_700BULK | 700's 18 delta-row sites bulk, share ≥ 0.50 | 11/18 = 0.6111 (c54 10/10) — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
reproduction (FULL 764×33 TSV byte-identical; all 21 cells +
standings + deltas exact), by cell standing (s3 all-delta-1
with 4 extra-only vs 3 missing-only; s2's 2 mixed cells hold
the only multi-site deltas outside c54; s700's delta-10 c54
vs 7 delta-1/2 cells), by other-frame status per shape (s700
extras 11/15 near with c54 10/10 bulk while s2 extras read
1/5 near; missings read 10/10 noncell on all three), by
near-miss identity (all 14 nears in c54/c313/c316/c336 with
zero far sites either side), and by headliner contrast
(c54's 10 extras all |δ| 8 bulk −− while c299/c311 read
|δ| 34/17 noncell). Task 2 discriminates by band (23/24
extras band-1 with the stragglers c299/c312), by decile
(17/24 extras dec-9 with the c54 tail down to dec-1), by gap
sign (s700 extras 15/15 −− while s3 extras read 3/4 ++; the
3 missing −− are one shared site), by |δ| (extra medians
9.0/8.0/8.0 per shape vs missing medians 10.0/10.0/12.0),
by streak negatively (0 unnamed bytes in any named column),
and by carrier positively (c54 10/10 in the 701 mask — the
first unnamed carrier hit in the M35/M36 value tables).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; per-cell tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The evidence value map
(`m36-valuemap-s0700.png`, 88753 B of 5242880 budget) colors
s700's tail-Y by shared (green 99) / extra-bulk (yellow 11)
/ extra-noncell (red 4) / missing-noncell (magenta 3);
DESIGN.md admits an evidence copy iff H4 meets on some shape
AND that shape's winning-leg majority level holds ≥8 of that
shape's extra sites — the band leg meets on s700 (0.7111)
with band 1 holding 14/15 extras. (s2/s3 maps stay in the
work dir only: 5/5 and 4/4 band-1 extras miss the ≥8
count leg.)

Recorded without verdict: 2/3/700's 21 unnamed cells read 24
+ 10 sites at 100% luma with extras at 14 near / 0 far / 10
non-cell on s0 and missings at 0/0/10 on their own shapes;
s700's c54 holds 10/10 bulk near-misses at |δ| 8 while its
c299/c311 read |δ| 34/17 noncell; 23/24 extras sit in band-1
and all 34 sites sit outside the named streak columns while
c54's 10 sit inside the 701 carrier mask; s700 extras read
15/15 −− gaps while missings read 7/10 ++; 0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| value suite + falsification bars, recorded before running | recorded | `DESIGN.md`: per-shape cross-value tables, s0-anchored band/decile/streak/carrier joins, gap-sign + \|δ\| stats, C-VAL control, bars H1–H6/N |
| 2/3/700 rows + per-site + joins + wall/exit/shas/determinism | measured | §Step 2: 21-cell rows exact + 34 per-site rows + joins + gap/\|δ\| stats; 3.8 s; re-run identical |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a value map discriminates (or absence reasoned) | measured | present by rule: H4 band leg on s700 + 14 extras in band 1; 88753 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m36"
cp local/research/M36/m36.py local/research/M36/control.py local/research/M36/DESIGN.md "/Volumes/Extreme SSD/m36/"
python3 m36.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m34/m34.txt" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m36" /Users/bradrichardson/dev/ssx3/local/research/M36 > m36.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m36/m36-valuemap-s0700.png" local/research/M36/m36-valuemap-s0700.png
```

## Paths

Evidence (committed): `local/research/M36/` — `DESIGN.md`
(suite + bars, recorded before running), `m36.py`
(per-shape per-cell values + joins + gap-sign + |δ| stats +
PNG writer), `control.py` (known-value control),
`m36-valuemap-s0700.png` (value map, 88753 B, rule-met),
`REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m36/` —
`m36.txt` (receipt: shas, baselines, guards, Task-1 per-shape
tables, joins, gap-sign, |δ| stats, re-run, PNG sizes),
`control.txt`, `m36.py`, `control.py`, `DESIGN.md` (working
copies), `m36-valuemap-s0002/s0003/s0700.png` (working
copies). No writes into `m15/`, `m16/`, `m17/`, `m18/`,
`m19/`, `m20/`, `m21/`, `m22/`, `m23/`, `m24/`, `m25/`,
`m26/`, `m27/`, `m28/`, `m29/`, `m30/`, `m31/`, `m32/`,
`m33/`, `m34/`, `m35/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. c54 carrier coincidence (new): 700-c54's 10 extras read
   10/10 bulk near-miss at |δ| 8 AND 10/10 inside the 701
   carrier mask — the first unnamed carrier hit in the
   M35/M36 value tables, vs 0/24 for every other still-below
   extra. Needs its own brief only if carrier-membership of
   unnamed growth matters: mask-geometry + row-list
   comparison of c54 vs the other 23 extras, offline — no
   new harness code.
2. Shared-site triple (new, minor): the (278,314) + (295,332)
   missings on all three shapes and the (276,313) missing on
   s2+s3 — 3 sites recurring across shapes with identical s0
   values but per-shape gaps. Needs its own brief only if
   recurring unnamed sites matter: cross-shape value/gap
   comparison at shared (r,c), offline — no new harness
   code.
3. s3 all-delta-1 row (new, minor): all 7 of shape 3's cells
   read delta-1 (4 extra-only + 3 missing-only, zero mixed)
   — the only still-below row with no mixed cell. Needs its
   own brief only if standing uniformity matters: row-list +
   value comparison vs s2/s700's mixed cells, offline — no
   new harness code.
4. M35 gaps 1–3 (still open, by reference): see M35 REPORT
   gaps 1–3 for the exact brief each needs (per-cell
   standing asymmetry; near-miss triple; big-|δ| unnamed
   sites).
5. M34 gaps 3–4 (still open, by reference): see M34 REPORT
   gaps 3–4 for the exact brief each needs (big-delta
   fresh columns — 700-c54's values now tabled here, the
   731/733/761 dest cells still open; same-column opposite
   standings).
6. M33 gaps 1, 4–5 (still open, by reference): see M33
   REPORT gaps 1, 4–5 for the exact brief each needs
   (far/near private split; M29 gaps 5–11; M32 gap 1 + M31
   gap 2).

(M34 gap 2 / M35 gap 4 — this brief — worked at table level
above. M34 gap 1 / shape-9 cells worked in M35.)

## What I could not do

1. No per-site values beyond the 21 still-below cells: δ
   values, gaps, and bulk status at other unnamed moved
   cells are unattributed (brief pins 2/3/700 only).
2. No destination assignment for unnamed moves: row-deltas
   are tabled without the M28-style displacement step (brief
   pins per-site values + joins only).
3. No s2/s3/s700 cell-7 count pins: no prior report lists
   them, so they read as measured (2469/2484/2605) with d!=0
   guarded rather than count-guarded.
4. No explanation: values are attributed per shape per cell,
   no rule; 0 B explained.
5. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M36/`: `DESIGN.md`, `m36.py`,
`control.py`, `m36-valuemap-s0700.png` (88753 B, rule-met),
`REPORT.md` (this file).