# M47 — Shape-711 pair wipe: singleton + far private-column listing: REPORT

M28 gap 3 (= M29 gap 6) worked at table level: 711's wipe
recomputes to tail 95, J 0.9314, moved [342,343] with c342 0/0
+ c343 0/0 (full wipe both), dest no-cand both, and NO unnamed
moves (FULL named + unnamed TSVs byte-identical to
`m28`/`m34-census.tsv` — stop rule not triggered); the 7 wiped
rows read 0/7 bulk on 711 (all non-cell, gaps −−×4 + −0×3,
|δ_s0| med 18.0); no-cand reads trivially (711 holds 0 private
sites, so the M28 ≥2-site candidate set is empty). The 11
singleton private Y-cols on movers are named (9 on shape 9 + 2
on shape 22; 6/11 bulk on s0, |δ| med 9.0); the far pool reads
13 multi-private (shape,col) with 57 sites (|δ| med 15.0);
both pools cover each wiped column by count (11 ≥ 5/2, 57 ≥
5/2 — numbers only, no assignment). Fully offline — no lease
of any kind, no boots, no harness code, no `adb`. No device
work. Runbook `local/muse/prompts/M47.md`. Tables, no verdicts.

Headers read first: `local/research/M28/REPORT.md` (all of it:
711 tail 95 J 0.9314 moved [342,343], c342 0/0 + c343 0/0 full
wipe both, dest no-cand both; 11 singleton private Y-cols on
movers tabled only as a count; M28 displacement rule reused
verbatim) plus `local/research/M34/REPORT.md` (all of it: 711's
census row tail 95 J 0.9314 with NO unnamed moves — the wipe
is purely named-column; union-domain unnamed census reused
verbatim).

Time box 4 hours (start 2026-09-20 06:31 EDT); used about 0.2.
No lease of any kind (brief orders none).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/`, `m16/`, `m17/`–`m46/` — all outputs went to the new
`/Volumes/Extreme SSD/m47/`): the 764 M16 per-shape triplets,
`loo.txt`, the M15 triplet (baseline guard only), and
`m28-census.tsv` + `m34-census.tsv` (FULL TSV match targets).
Work dir `/Volumes/Extreme SSD/m47/`; evidence
`local/research/M47/`.

Input shas (sha256 full, from the run receipt; s0 + m15 prefixes
match M17–M46):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m16-v0-s0711 | `a0ebe252…46e26edf` |
| m16-mid-s0711 | `69329d20…50d14b36f` |
| m16-full-s0711 | `43ec9102…b38a291d` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |
| m28-census.tsv | `27872527…15a9e7f` |
| m34-census.tsv | `83482d1f…926c8aa8` |

(Full hexes in `m47.txt` §inputs. Triplet fold sha over all
764×3 bins: `6c906897…61fd423b1` — matches M28/M34 exactly.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | fnv |
| --- | ---: | --- |
| m15 | 13418 | `306b5c778898b64a` |
| m16 s0 | 22815 | `6b9ffda25bd76c6f` |

Cross-checks: 13418/22815 + both fnvs match M17–M46 exactly.
`loo.txt` parses to 764 rows; top-10 shapes + shares match M16.
R_s vs `loo.txt` reads equal on all 764/764 (0 mismatches).
Triplet fold sha matches M28/M34. δ==0 violations read 0
shapes. s0 cell 2475 + tail 102 (sub-bins 28+74, max 47) +
P(δ>0) 0.8093 + all 8 s0 named reference row lists +
guard-only c341 n=0 match exactly; UNNAMED domain recomputes
to the pinned 33 (41 union; s0-bearing-13 row lists exact;
c341 empty on all 764). FULL named TSV byte-identical vs
`m28-census.tsv` (54296 B); FULL unnamed TSV byte-identical vs
`m34-census.tsv` (163262 B). 711 row: tail 95 + J 0.9314 +
moved [342,343] + c342/c343 0/0 + no unnamed moves; named
mover list matches M28's 10 exactly; singleton count reads 11.
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One `m47.py` invocation (the receipt, 6.1 s, exit 0 — the
estimator was never changed after the receipt run started); one
`control.py` invocation (green, first try).

| Invocation | Wall | Standing |
| --- | --- | --- |
| m47.py receipt | 6.1 s | exit 0; all guards pass; canon `eed7416b…c914322f1f` |
| control.py C-WIPE | <1 s | green; wipe + listing + values exact |

Per-stage wall (receipt run, sequential):

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Full 764 pass (R_s + cell/tail + named/unnamed colrows) | 764 | 5.9 s |
| FULL TSV guards (named + unnamed byte-compare) | 764 | 0.0 s |
| Task 1 (wipe rows + wiped values + no-cand) | 1 | 0.0 s |
| Task 2.1 (singleton table, 11 sites) | 2 | 0.0 s |
| Task 2.2 (far table, 13 cols / 57 sites) | 6 | 0.1 s |
| Determinism re-run (Task 1 on s0+711, fresh loads) | — | in-pass |
| Positive controls (`control.py`) | — | <1 s |
| Total `m47.py` wall | — | 6.1 s |

## Step 2 — estimates

### Task 1 — 711 wipe reproduction (do the 2 columns reproduce?)

Wipe table (s0-rows vs 711-rows vs miss rows — all Y-plane):

| col | s0 rows | s711 rows | miss rows | n/ov |
| ---: | --- | --- | --- | --- |
| 342 | [27,28,29,34,35] | [] | [27,28,29,34,35] | 0/0 |
| 343 | [26,27] | [] | [26,27] | 0/0 |

s711 full sets: priv=0, miss=7, shared=95, tail=95
(95/102 = 0.9314 ✓).

Wiped-value table (all 7: |δ_s0|; s711 status + |δ_711|; signed
gaps s0 vs 711; gap signs):

| cell | offset | plane | (r,c) | \|δ_s0\| | s711 status | \|δ_711\| | g_s0 | g_711 | sign |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 343 | 33966 | Y | (26,343) | 31 | noncell | n/a | −65 | −20 | −− |
| 342 | 35244 | Y | (27,342) | 16 | noncell | n/a | −40 | −1 | −− |
| 343 | 35246 | Y | (27,343) | 26 | noncell | n/a | −54 | −12 | −− |
| 342 | 36524 | Y | (28,342) | 27 | noncell | n/a | −63 | −1 | −− |
| 342 | 37804 | Y | (29,342) | 18 | noncell | n/a | −43 | 0 | −0 |
| 342 | 44204 | Y | (34,342) | 16 | noncell | n/a | −39 | 0 | −0 |
| 342 | 45484 | Y | (35,342) | 17 | noncell | n/a | −41 | 0 | −0 |

(Wiped |δ_s0|: min 16, med 18.0, mean 21.5714, max 31; status
0 near / 0 far / 7 noncell; signed-gap equality 0/7, abs-eq
0/7; gap signs −−×4 + −0×3, ++ 0/7. All 7 g_s0 < 0.)

No-cand table (M28 rule rows — candidates = own-shape private
Y-cols with ≥2 sites):

| Shape | miss col | own private Y-cols | ≥2-site cands | dest | standing |
| ---: | ---: | --- | ---: | --- | --- |
| 711 | 342 | (none — priv=0) | (none) | none | no-cand |
| 711 | 343 | (none — priv=0) | (none) | none | no-cand |

(s711 private U/V sites: 0. The candidate set is empty because
711 holds no private sites at all — not a distance or
occupancy miss.)

### Task 2 — singleton + far private-column listing (the new data)

Singleton table (all 11: 9 on shape 9 + 2 on shape 22; 708 /
709 / 710 / 711 / 731 / 732 / 733 / 734 hold no exact-1
private Y-cols):

| shape | col | row | offset | \|δ_Q\| | s0 status | \|δ_s0\| | g_Q | g_s0 | sign |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 9 | 310 | 252 | 323180 | 8 | noncell | n/a | 22 | 2 | ++ |
| 9 | 312 | 248 | 318064 | 13 | bulk | 1 | 33 | 10 | ++ |
| 9 | 314 | 246 | 315508 | 13 | bulk | 1 | 32 | 9 | ++ |
| 9 | 321 | 266 | 341122 | 9 | bulk | 1 | 19 | 3 | ++ |
| 9 | 322 | 274 | 351364 | 8 | noncell | n/a | 21 | 2 | ++ |
| 9 | 332 | 305 | 391064 | 28 | noncell | n/a | −62 | −55 | −− |
| 9 | 336 | 239 | 306592 | 8 | bulk | 6 | 17 | 14 | ++ |
| 9 | 339 | 239 | 306598 | 15 | noncell | n/a | 39 | 35 | ++ |
| 9 | 351 | 226 | 289982 | 19 | noncell | n/a | −39 | −39 | −− |
| 22 | 295 | 402 | 515150 | 8 | bulk | 1 | 19 | −4 | +− |
| 22 | 307 | 393 | 503654 | 9 | bulk | 1 | 26 | −6 | +− |

(Singleton pooled: near=1 / far=5 / noncell=5, bulk share
6/11 = 0.5455; bulk-|δ_s0| values 1:5 6:1; |δ_Q| min 8, med
9.0, mean 12.5455, max 28; gap signs ++×7 + +−×2 + −−×2, ++
7/11; signed-gap equality 1/11 — the (226,351) site −39/−39.)

Far-column table (13 multi-private (shape,col), 57 sites —
listed not ranked; d342/d343 = column distance to the wipe):

| shape | col | n | rows | \|δ_Q\| list (med) | near/far/non | ++/signs | d342 | d343 |
| ---: | ---: | ---: | --- | --- | --- | --- | ---: | ---: |
| 9 | 313 | 2 | [269,270] | [9,12] (10.5) | 0/2/0 | 2/2 ++ | 29 | 30 |
| 9 | 315 | 3 | [245,289,290] | [11,13,16] (13.0) | 0/1/2 | 1/3 ++ | 27 | 28 |
| 9 | 316 | 2 | [244,245] | [8,14] (11.0) | 0/2/0 | 2/2 ++ | 26 | 27 |
| 9 | 318 | 3 | [240,241,243] | [13,16,25] (16.0) | 0/3/0 | 3/3 ++ | 24 | 25 |
| 9 | 327 | 2 | [232,233] | [12,14] (13.0) | 0/2/0 | 2/2 ++ | 15 | 16 |
| 9 | 337 | 2 | [234,235] | [8,10] (9.0) | 0/2/0 | 2/2 ++ | 5 | 6 |
| 22 | 296 | 2 | [400,401] | [8,8] (8.0) | 0/0/2 | 0/2 (+−×2) | 46 | 47 |
| 731 | 259 | 9 | [25–33] | [10,13,15,16,17,17,17,17,18] (17.0) | 0/0/9 | 0/9 (−−×2,−0×7) | 83 | 84 |
| 731 | 279 | 9 | [25–33] | [11,16,16,16,16,17,17,17,19] (16.0) | 0/0/9 | 0/9 (−−×3,−0×6) | 63 | 64 |
| 732 | 298 | 2 | [26,27] | [8,14] (11.0) | 1/1/0 | 0/2 (−−×2) | 44 | 45 |
| 733 | 303 | 9 | [25–33] | [9,11,12,13,13,13,13,15,16] (13.0) | 0/0/9 | 0/9 (−−×1,−0×8) | 39 | 40 |
| 733 | 323 | 10 | [25–34] | [8,11,15,16,16,16,17,18,18,19] (16.0) | 0/0/10 | 0/10 (−−×3,−0×7) | 19 | 20 |
| 734 | 342 | 2 | [26,33] | [11,21] (16.0) | 0/2/0 | 0/2 (−−×2) | 0 | 1 |

(Far pooled: 13 cols / 57 sites; near=1 / far=15 / noncell=41;
bulk-|δ_s0| values 1:10 2:3 3:1 5:1 6:1; |δ_Q| min 8, med
15.0, mean 14.1228, max 25; gap signs ++×12 + +−×2 + −−×14 +
−0×29, ++ 12/57; signed-gap equality 0/57. The 731/733 dest
cols read 0/37 bulk; shape-9's 6 far cols read 12/14 bulk;
734-c342 is the only zero-distance far col (d342=0). Full
per-site rows in `m47.txt` §Task 2.2.)

Per-move listing (wiped-row counts vs pool counts — numbers
only, no assignment):

| move | wiped | singleton pool | cover? | far pool | cover? |
| --- | ---: | ---: | --- | ---: | --- |
| c342 | 5 | 11 | True (11 ≥ 5) | 57 | True (57 ≥ 5) |
| c343 | 2 | 11 | True (11 ≥ 2) | 57 | True (57 ≥ 2) |

### Positive controls (`control.py`)

| Control | Recovered | Want | Pass |
| --- | --- | --- | --- |
| C-WIPE (known 7-wipe + 3 sing + 1 far) | wipe 7 exact, sing 3 exact, far 1×4 exact, J 0.8716, pool \|δ\| 8×7, wipe \|δ\| 1×7, cell fixed | exact | True |

(Wipe pool: c342[27,28,29,34,35]+c343[26,27], all tail-Y; +1
landing ×7, 0 −1 fallbacks. Bulk gap≥17 fresh-col Y pool: 238
sites. Far col c81 rows [44,45,46,47] (+8/−8 alternating);
sing cols c270 r25 / c334 r25 / c305 r26. Spanned Y cols
81/270/305/334/342/343. Full rows in `control.txt`.)

### Determinism re-run receipt (same inputs, second pass)

Canon sha (Task 1 on s0+711: wipe rows + 7 wiped-value rows +
gapsign + dstats + no-cand rows, fresh loads) pass1
`eed7416b…c914322f1f` vs pass2 `eed7416b…c914322f1f`,
identical=True; 18/18 lines match=True.

## Step 3 — attribute

Model comparison (cell-7 bytes; attribution, not explanation
— no rule, N reads 0 explained):

| Frame | Model | cell-7 R | explained | e |
| --- | --- | ---: | --- | --- |
| m16 s0 | none (attribution only) | 2475 | 0 | 0.0000 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1_PUREWIPE | 711 holds 0 private sites | priv=0 — met |
| H2_SINGBULK | singleton pool bulk share ≥ 0.50 | 6/11 = 0.5455 — met |
| H3_FARPOOL | far (shape,col) count ≥ 6 | 13 — met |
| H4_WIPEBULK | wiped-site bulk share ≥ 0.50 | 0/7 = 0.0000 — not met |
| H5_WIPEGG | wiped-site ++ share ≥ 0.50 | 0/7 = 0.0000 — not met |
| H6_POOLMED | \|far med − sing med\| ≥ 4 | \|15.0 − 9.0\| = 6.0 — met |
| N | cell 7 after attribution + remaining split | 0 explained; 102 tail stands, split below |

Where each test discriminates vs not: Task 1 discriminates by
set (priv=0/miss=7/shared=95 — the wipe is a pure 7-row
deletion), by wiped value (|δ_s0| 16–31, med 18.0 — no small
wiped sites), by wiped status (0/7 bulk — all noncell on 711),
by wiped gap sign (0/7 ++; −−×4 + −0×3 with g_711 = 0 on the
3 upper-c342 rows), and by candidacy (empty candidate set —
no-cand is structural, not a near-miss). Task 2 discriminates
by singleton shape (9 on shape 9 + 2 on shape 22; 8/10 movers
hold none), by singleton status (6 bulk vs 5 noncell with the
sole near at (239,336) |δ_s0| 6), by singleton gap sign (s9:
++×7/−−×2; s22: +−×2), by far-pool shape (13 cols on 6
shapes incl. all 5 fresh M28 dests + 734's c342 at d342=0),
by far-pool status split (shape-9's 6 cols 12/14 bulk vs
731/733's 4 dest cols 0/37 bulk), by far-pool |δ| level (med
15.0 vs singleton med 9.0), and by count coverage (both pools
cover both wiped columns — 11 and 57 vs 5 and 2).

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
| standing interior remainder | 2475 of cell 7 (100%) | no rule; wipe + pool tables in §Step 2 |
| standing remainder (total) | 22815 (100% of R_0) | 0 B explained; rest split above |

(Value-level fits M23–M26 are orthogonal and unchanged.)

Screenshot: present by rule. The wipe/pool map
(`m47-poolmap.png`, 404 B of 5242880 budget, 320x224 native:
x=col//2, y=row//2; red = 7 wiped s0 sites, cyan = 11
singleton pool, yellow = 57 far pool) is copied to evidence;
DESIGN.md admits an evidence copy iff H1 meets AND the
singleton pool holds ≥3 bulk sites — H1 meets (priv=0) with 6
bulk singletons.

Recorded without verdict: 711's c342+c343 recompute to a pure
7-row wipe (0/0 both, no-cand both, 0 privates, no unnamed
moves); wiped rows read 0/7 bulk with −−×4 + −0×3 gaps; the
11 singletons read 9+2 on shapes 9/22 at 6/11 bulk; the far
pool reads 13 cols / 57 sites at med 15.0 with shape-9 bulk
vs 731/733 noncell; both pools cover both wipes by count;
0 B explained.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| wipe suite + falsification bars, recorded before running | recorded | `DESIGN.md`: M28-rule wipe repro + M36-style values + singleton/far listing + C-WIPE control, bars H1–H6/N |
| wipe + listing tables + wall/exit/shas/determinism | measured | §Step 2: 7-row wipe + 11-singleton + 13-far tables; 6.1 s; re-run identical |
| controls (known wipe + pools) | measured | §Step 2: C-WIPE green — wipe + listing + values exact |
| explained-vs-standing update (attribution, not explanation) + gap rows | measured | §Step 3: 0 explained; 102 stands; gaps below |
| screenshot if a wipe/pool map discriminates (or absence reasoned) | measured | present by rule: H1 meets + 6 bulk singletons; 404 B |

## Exact commands

Staging + run (offline; inputs read-only; run from the work
dir; the receipt is the single invocation — §Runs):

```
mkdir -p "/Volumes/Extreme SSD/m47"
cp local/research/M47/m47.py local/research/M47/control.py local/research/M47/DESIGN.md "/Volumes/Extreme SSD/m47/"
python3 m47.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m28/m28-census.tsv" "/Volumes/Extreme SSD/m34/m34-census.tsv" "/Volumes/Extreme SSD/m47" /Users/bradrichardson/dev/ssx3/local/research/M47 > m47.txt 2>&1
python3 control.py "/Volumes/Extreme SSD/m16" > control.txt 2>&1
cp "/Volumes/Extreme SSD/m47/m47-poolmap.png" local/research/M47/m47-poolmap.png
```

## Paths

Evidence (committed): `local/research/M47/` — `DESIGN.md`
(suite + bars, recorded before running), `m47.py` (wipe
repro + singleton/far listing + PNG writer), `control.py`
(known-wipe control), `m47-poolmap.png` (wipe/pool map, 404 B,
rule-met), `REPORT.md` (this file).

Large outputs (not committed): `/Volumes/Extreme SSD/m47/` —
`m47.txt` (receipt: shas, baselines, guards, Task-1/2 tables,
re-run, PNG size), `control.txt`, `m47.py`, `control.py`,
`DESIGN.md` (working copies), `m47-poolmap.png` (working
copy). No writes into `m15/`, `m16/`, `m17/`, `m18/`, `m19/`,
`m20/`, `m21/`, `m22/`, `m23/`, `m24/`, `m25/`, `m26/`, `m27/`,
`m28/`, `m29/`, `m30/`, `m31/`, `m32/`, `m33/`, `m34/`, `m35/`,
`m36/`, `m37/`, `m38/`, `m39/`, `m40/`, `m41/`, `m42/`, `m43/`,
`m44/`, `m45/`, `m46/`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. Wipe-to-noncell mechanism (new): all 7 wiped rows read
   non-cell on 711 (g_711 ∈ {−20,−12,−1,−1,0,0,0}) — why the
   rows left cell-7 is unattributed. Needs its own brief only
   if wipe mechanics matter: per-site v0/mid/full attribution
   for 711's full sets, offline — no new harness code.
2. Singleton-vs-wipe matching (new): the 11 singleton rows +
   values are listed, not assigned to the 7 wiped rows.
   Needs its own brief only if unassigned moves matter: row +
   value comparison per wiped row vs the singleton pool,
   offline — no new harness code.
3. Far-pool status split (new): shape-9's 6 far cols read
   12/14 bulk while 731/733's 4 dest cols read 0/37 bulk —
   located, not attributed. Needs its own brief only if pool
   structure matters: the same per-site attribution split by
   pool block, offline — no new harness code.
4. 734-c342 zero-distance far col (new, minor): the only far
   col at d342=0 (2 rows [26,33], |δ| [11,21], −−×2) sits
   inside the wiped column on another mover. Needs its own
   brief only if collision moves matter: joint listing with
   the M28-gap-4 734 triple move, offline — no new harness
   code.
5. M46 gaps 1–2 (still open, by reference): see M46 REPORT
   gaps 1–2 for the exact brief each needs (far-block
   dec-7/8 seats; band-2 near singleton).
6. M33 gaps 2–5, M35 gaps 1–5 (still open, by reference):
   see M33/M35 REPORT gaps for the exact brief each needs
   (709-c298 missings; s22 bottom cluster; M29 gaps 5–11
   incl. 734 triple move, 732 c296→c298 move, below-0.95
   shape family, static-on-other-frame privates, M26 gaps;
   M32 gap 1 + M31 gap 2; per-cell standing asymmetry;
   near-miss triple; big-|δ| unnamed sites; M34 gaps 3–4).

(M28 gap 3 / M29 gap 6 — this brief — worked at table level
above.)

## What I could not do

1. No assignment: wiped rows vs pools are tabled by count
   only (brief pins list-don't-assign; gap 2 tables the
   follow-up).
2. No per-site far-pool rows in evidence: the 57 far sites
   are tabled per column here with full per-site rows in
   `m47.txt` only (brief pins counts + rows + medians).
3. No byte-level work beyond 711's sets + mover pools: other
   shapes' wipes stay located, not attributed (gaps 5–6
   table the follow-ups by reference).
4. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M47/`: `DESIGN.md`, `m47.py`,
`control.py`, `m47-poolmap.png` (404 B), `REPORT.md` (this
file).
