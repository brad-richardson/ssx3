# M17 — Sub-pixel / local motion model for the synth residual: REPORT

M16's 22815-B synth-vs-truth residual tested for a rigid component
at sub-pixel scale (M16 gap 1 = M15 gap 2, open twice): global
half-pixel bilinear SAD per shape (Model G) plus 16×16 block
matching with half-pel refine (Model B), compensated residuals
against R_0 = 22815. Fully offline — no harness code, no replays,
no lease, no `adb`. No device work. Runbook
`local/muse/prompts/M17.md`. Tables, no verdicts.

Headers read first: `local/research/M16/REPORT.md` (all of it: the
leave-one-out shares, R_0 = 22815 with 93.6% of residual Y px at
|d| = 1, all 764 integer warps reading (0,0)) plus the M15
`synth.py` estimator section it reuses (masked-SAD dominant shift,
plane-separated warp + blend, `xdiff` byte diffs).

Time box 4 hours; used about 0.5. No lease of any kind (brief
orders none; P-lane briefs share nothing).

## Baseline note (read before the tables)

Inputs are the committed dumps on the SSD, read-only (no writes
into `m15/` or `m16/` — all outputs went to the new
`/Volumes/Extreme SSD/m17/`): the 764 M16 per-shape triplets
(`m16-v0/mid/full-sNNNN.bin`), `loo.txt`, and the M15 triplet
(`m15-v0/mid/full.bin`, second sample). Work dir
`/Volumes/Extreme SSD/m17/`; evidence `local/research/M17/`.

Input shas (sha256 full, from the run receipt):

| Input | sha256 |
| --- | --- |
| m16-v0-s0000 | `279a5bfb…dc8ca7a` |
| m16-mid-s0000 | `9db73827…c83013` |
| m16-full-s0000 | `6c7c4b1b…edfcef` |
| m15-v0 | `879c74ec…102458` |
| m15-mid | `10e2514a…20284` |
| m15-full | `b4053af3…2426a` |

(Full hexes in `m17.txt` §inputs.)

Model 0 recompute (blend baseline, byte-exact from the dumps):

| Frame | R_0 | xdmax | xdmean | respx | Y-\|d\| hist [1,2–3,4–7,8–15,16+] | bands t/m/b | fnv |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| m15 | 13418 | 102 | 1.712 | 8584 | [7474, 398, 339, 172, 201] | 2191/3072/3321 | `306b5c778898b64a` |
| m16 s0 | 22815 | 49 | 1.361 | 14984 | [14021, 368, 280, 140, 175] | 5678/5300/4006 | `6b9ffda25bd76c6f` |

Cross-checks: m15 13418 = M15 report's residual; m16 s0 22815 =
`loo.txt`'s R_0 with the same synth fnv (`6b9ffda25bd76c6f`).
Mismatch rule (DESIGN.md) not triggered.

## Runs (offline estimators)

One script, one completed run (exit 0); an earlier invocation was
cut by a display-pipe SIGPIPE after Model G and re-ran whole
(the re-run is the receipt; 82.2 s total). Sequential, no pool.

| Stage | Shapes | Wall |
| --- | ---: | --- |
| Model G single (m15 frame) | 1 | 0.1 s |
| Model G all M16 triplets | 764 | 82.2 s |
| Model B m16 shape 0 | 1 | 1.4 s |
| Model B m15 frame | 1 | 0.9 s |
| Determinism re-run (G+B on s0) | — | in-pass |
| Positive controls (`control.py`) | — | ~2 s |
| Total `m17.py` wall | — | 82.2 s |

Bilinear-shift validation (recorded before the run): `shift_frac`
at integer offsets is byte-identical to M15 `shift_plane` on
(1,0)/(0,1)/(−1,0)/(0,−1)/(2,−3); half-shift output is float64
in [16, 235].

## Step 2 — estimates

### Model G — global half-pixel (25 candidates, ±1 grid)

Shift distribution over all 764 M16 triplets: {(0.0, 0.0): 764}.
M15 frame: (0.0, 0.0). Explained bytes: 0 on every shape
(R_s^G == R_s for all 764 rows; `loo.txt` cross-parse 764/764
rows matched). e_G = 0.0000 on both frames. Synth_G ==
blend byte-identically (fnv `6b9ffda25bd76c6f` on s0).

Masked-SAD 5×5 grids (s0 left, m15 right — rows dy, cols dx;
minimum at (0,0), strict):

| dy\dx | −1.0 | −0.5 | 0.0 | +0.5 | +1.0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| s0 −1.0 | 612900 | 447998 | 347679 | 362936 | 497155 |
| s0 −0.5 | 543406 | 342876 | 197804 | 253685 | 435989 |
| s0 +0.0 | 514105 | 286624 | 81268 | 205186 | 433135 |
| s0 +0.5 | 507318 | 309773 | 181623 | 272093 | 465705 |
| s0 +1.0 | 553643 | 399478 | 329356 | 388532 | 545850 |
| m15 −1.0 | 481956 | 356003 | 279458 | 291354 | 392910 |
| m15 −0.5 | 429382 | 273990 | 161142 | 202289 | 342256 |
| m15 +0.0 | 408231 | 231213 | 66599 | 162080 | 340887 |
| m15 +0.5 | 400798 | 248905 | 152662 | 217688 | 367982 |
| m15 +1.0 | 439264 | 322420 | 270754 | 311434 | 430888 |

Nearest half-pel neighbor reads ≥2.2× the (0,0) minimum on s0
(181623 vs 81268) and ≥2.3× on m15 (152662 vs 66599). Full
764-row per-shape table (G shift / nmoved / R_s(M16) / R_s^G /
explained) in `m17.txt`.

### Model B — block matching (B=16, 40×28 grid, ±4 + half refine)

| Frame | moved blks | degen blks | est sad00 | est sadbest | est gain |
| --- | ---: | ---: | ---: | ---: | ---: |
| m16 s0 | 655 | 465 | 81268 | 74732 | −8.1% |
| m15 | 317 | 803 | 66599 | 59794 | −10.2% |

Estimation SAD improves 8–10%; the compensated residual does
not (below). s0 vector histogram: (0,0) on 831/1120 blocks;
289 nonzero, |v|_1 = {0.5: 124, 1.0: 51, 1.5: 6, 2.0: 49,
2.5: 7, 3.0: 27, 4.0: 8, 4.5: 1, 5.0: 6, 5.5: 2, 6.0: 3,
6.5: 2, 7.0: 2, 8.0: 1} (full 56-entry histogram in `m17.txt`).
m15: (0,0) on 1025/1120; 95 nonzero, tail to |v|_1 = 7.0.
No concentrated nonzero mode on either frame.

### Positive controls (`control.py`, synthetic shifts on s0 v0)

| Control | Recovered | Want | est sad00 → sadbest |
| --- | --- | --- | --- |
| G half (+0.5 x) | (0.5, 0.0) | (0.5, 0.0) | 1001352 → 52106 |
| G int (+1 x) | (1.0, 0.0) | (1.0, 0.0) | 1998317 → 0 |
| B int (+2 x) | (2.0, 0.0) on 1120/1120 | majority (2.0, 0.0) | 3182474 → 0 |
| B half (+0.5,+0.5) | (0.5, 0.5) on 983/1120 | majority (0.5, 0.5) | 1373196 → 74915 |

The estimators recover synthetic sub-pixel and per-block motion
exactly where it exists; the (0,0)/negative readings on real
data are measurements, not estimator failure.

### Determinism re-run receipt (same inputs, second pass)

G s0: shift (0.0, 0.0) vs (0.0, 0.0), fnv `6b9ffda25bd76c6f`
vs `6b9ffda25bd76c6f`, identical=True. B s0: vecs
identical=True, fnv `b6ae162420549163` vs `b6ae162420549163`,
identical=True.

## Step 3 — attribute

Model comparison (bytes + distributions, M16-loo table shape):

| Frame | Model | R | explained (R_0 − R) | e | xdmax | xdmean | respx | Y-\|d\| hist | bands t/m/b |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| m16 s0 | 0 blend | 22815 | 0 | 0.0000 | 49 | 1.361 | 14984 | [14021, 368, 280, 140, 175] | 5678/5300/4006 |
| m16 s0 | G half-pel | 22815 | 0 | 0.0000 | 49 | 1.361 | 14984 | [14021, 368, 280, 140, 175] | 5678/5300/4006 |
| m16 s0 | B block16 | 48261 | −25446 | −1.1153 | 96 | 1.631 | 36949 | [31729, 3178, 1001, 493, 548] | 7980/8636/20333 |
| m15 | 0 blend | 13418 | 0 | 0.0000 | 102 | 1.712 | 8584 | [7474, 398, 339, 172, 201] | 2191/3072/3321 |
| m15 | G half-pel | 13418 | 0 | 0.0000 | 102 | 1.712 | 8584 | [7474, 398, 339, 172, 201] | 2191/3072/3321 |
| m15 | B block16 | 23064 | −9646 | −0.7189 | 102 | 1.866 | 15936 | [12229, 2016, 941, 458, 292] | 3827/4843/7266 |

Falsification bars (recorded before running; outcomes tabled):

| Bar | Bar text | Measured |
| --- | --- | --- |
| H1 | e_G ≥ 0.5 on s0 | e_G = 0.0000 — not met |
| H2 | modal per-shape half shift ≥50% AND nonzero | modal (0.0,0.0) at 100%, zero — not met |
| L1 | e_G < 0.1 while e_B ≥ 0.5 | e_G = 0.0000, e_B = −1.1153 — not met |
| N | remainder after best model as bytes + hist + bands | 22815 B, [14021, 368, 280, 140, 175], 5678/5300/4006 (best = tie 0/G) |

Where each model succeeds vs fails (region table): Model G
explains 0 bytes in every band on both frames (no carrier
changes anywhere — per-shape carrier overlays would be
pixel-identical to M16's, so none are re-cut). Model B fails
in all three bands and worst at the bottom: s0 bottom-band
residual Y px rise 4006 → 20333 (top 5678 → 7980, mid 5300 →
8636); m15 bottom 3321 → 7266. Block compensation adds
residual everywhere it moves vectors.

Updated deliverable — rigid vs genuinely non-rigid remainder:

| Content | Bytes (m16 s0) | Behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (M16, unchanged) |
| integer rigid | 0 explained | (0,0) on 764/764 (M16, unchanged) |
| sub-pixel rigid (G) | 0 explained | (0.0,0.0) on 764/764 + m15; e_G = 0 |
| local rigid (B block16) | −25446 explained | estimation −8.1% SAD, compensation +25446 B residual |
| genuinely non-rigid remainder | 22815 (100% of R_0) | xdmean 1.36; 93.6% of residual Y px at \|d\|=1 |

Screenshots (committed, 320x224 PNG): `m17-diffmap-B.png`
126727 B (truth + red Model-B residual overlay: red denser
than M16's map, bottom band heaviest), `m17-field-B.png`
98415 B (dimmed truth + per-block motion vectors, yellow ≤0.5
/ orange ≤2 / red above, ×4 scale). Total 225142 B (budget
5242880). The Model-G diff-map was rendered and found
sha256-identical to `m16-diffmap.png` (`a6799b73…340`) —
omitted as a duplicate, noted here as the G==blend receipt.

Recorded without verdict: global half-pel explains 0 of 22815
B on 764/764 shapes; 16×16 block compensation widens the
residual to 48261 B; the full 22815 B stands as the
non-translational remainder on this frame (13418 B on M15's).

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| estimator suite + "explained" definition + falsification bars, recorded before running | recorded | `DESIGN.md`: 25-cand half-pel G, B=16 ±4+refine B, e_M bars H1/H2/L1/N |
| per-shape sub-pixel shifts, per-block motion field, compensated residuals, wall/exit/shas/determinism | measured | §Step 2: 764×(0,0); 1120-vec fields; R_G/R_B both frames; 82.2 s; re-run identical |
| bytes + distributions each model explains; where sub-pixel succeeds vs fails; rigid vs non-rigid deliverable | measured | §Step 3: comparison + bars + region + deliverable tables |
| screenshots that discriminate | measured | 2 PNGs, 225142 B; G map omitted as M16-duplicate (sha receipt) |

## Exact commands

Validation + run (offline; inputs read-only; the first
invocation died to a display-pipe SIGPIPE after Model G and
was re-run whole — the re-run below is the receipt):

```
python3 -c "shift_frac vs shift_plane integer-equivalence check (see REPORT §Runs)"
python3 m17.py "/Volumes/Extreme SSD/m16" "/Volumes/Extreme SSD/m15" "/Volumes/Extreme SSD/m17" /Users/bradrichardson/dev/ssx3/local/research/M17 > m17.txt 2>&1
python3 control.py 2>&1 | tee control.txt
```

(All run from `/Volumes/Extreme SSD/m17/`; `m17.txt` holds the
full stdout including the 764-row per-shape table.)

## Paths

Evidence (committed): `local/research/M17/` — `DESIGN.md`
(suite + bars, recorded before running), `m17.py` (estimators:
M15/M16 core + bilinear shift + Models G/B + PNG writer),
`control.py` (4 synthetic-shift positive controls), `REPORT.md`
(this file), `m17-diffmap-B.png`, `m17-field-B.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m17/` —
`m17.txt` (43561 B receipt: shas, baselines, SAD grids, 764-row
table, B vectors, re-run, PNG sizes), `control.txt`,
`m17-synth-G-s0000.bin` / `m17-synth-B-s0000.bin` /
`m17-synth-G-m15.bin` / `m17-synth-B-m15.bin` (4 × 573440 B),
`m17.py`, `control.py` (working copies). No writes into
`m15/`, `m16/`, `/tmp/p1-link`, or other agents' dirs.

## Gap rows (exact next brief each needs)

1. M16 gap 1 / M15 gap 2 (this brief — measured): sub-pixel
   rigid reads exactly zero (764/764 half-pel (0,0), both
   frames); 16×16 translational block compensation reads
   negative (−25446 B). No follow-up brief from the rigid
   side; the remainder question is gap 2/5 below.
2. Negative-share mechanism (M16 gap 3, still open): 93
   negatives (worst −244) unattributed at byte level. Needs
   its own brief: per-shape added-residual maps (residual_s
   pixels absent from residual_0) + EFB-copy diffing, offline
   on the SSD dumps — no new harness code.
3. Odin port readiness (M16 gap 2, still open): no Odin
   contract in-repo; handoff artifact stays `loo.txt` +
   dumps + synths. Needs its own brief once the consumer
   names its interface (input format, per-draw weights vs
   pixel masks, frame coverage).
4. Top-HUD glyph residual isolation (M16 gap 4, still open):
   bottom-HUD draws identified, top-band glyph edges in the
   long tail. Needs its own brief if draw-level top-HUD
   isolation matters: HUD-region masked re-attribution,
   offline — no new harness code.
5. Remainder character beyond translation (new): the 22815-B
   remainder survives global half-pel and per-block
   translational compensation with 93.6% of Y px at |d|=1.
   Needs its own brief if mechanism matters: filtering-scale
   tests (blend-weight sweeps, sub-pixel edge-phase analysis)
   or non-translational warp families, offline on the SSD
   dumps — no new harness code.

## What I could not do

1. Quarter-pel grids: the brief orders half-pixel bilinear
   SAD; the 5×5 grids bottom sharply at (0,0) (nearest
   neighbor ≥2.2×), but a ±0.25 grid was not run — tabled,
   not chased.
2. Per-shape block fields: Model B ran on shape 0 + M15 only
   (per DESIGN.md — 764 × 1120-block searches exceed the
   box's share); the per-shape question is carried by Model G.
3. Alternate block sizes / search ranges: B=16, ±4 recorded
   before running and run as recorded; no sweep.
4. U/V motion: Y-estimated, U/V halved per the M15 precedent
   (recorded in DESIGN.md); independent chroma estimation not
   attempted.
5. Carrier re-attribution under compensation: Model G changes
   no carrier (explains 0 everywhere); Model B changes all of
   them for the worse — no new carrier table is cut.
6. Desktop only; no device work. NEVER `git push` in ssx3
   (this commit is local-only by rule).

## Files

Committed under `local/research/M17/`: `DESIGN.md`, `m17.py`,
`control.py`, `REPORT.md` (this file), `m17-diffmap-B.png`,
`m17-field-B.png` (320x224, 225142 B total).
