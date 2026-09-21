# T43 report — accumulate lock-QA-gated on→on pairs: SAME shape, crash-free hold goal, hold-step vs no-input distribution (bytesize, no lease)

Brief: T43 (T42 §recipe arm 1: accumulate; arm 2 = the static
gradient-lock test as a cheap tabled comparison that does NOT gate the
run). Tables, no verdicts. Time box 4 h.

Stale-reading guard: `local/research/T42/REPORT.md` (all of it: the ROI
retune converts 11/12-flooded into 9/12-gated with a rider-locked pair
straddling the hold — control floods 11/12 again on the new stretch —
GATING PROVEN — but MOTION is not solved: per-snap intrusion bias (±50
px) survives inside VALID pairs, the hold hop contains a TREE CRASH (7
MPH, 5TH→6TH — crash-vs-input-vs-bias UNRESOLVED), and the no-input
floor is a single sample). This brief executes arm 1 ONLY: accumulate
on→on VALID pairs (lock-QA-gated) toward the distribution verdict, with
a crash-free hold goal. Arm 2 (gradient static test) is Task 1 below.

Experiment contract (up front): hypothesis — re-running T42 R3's SAME
shape (same `sleep 0.5` blind cadence, same ≈1038 ms Left hold, same
slot, phase-matched pre-hold window) yields a crash-free hold straddled
by an on→on VALID pair, and the accumulated hold-step distribution
(T42's + this run's on→on pairs) separates from the no-input
distribution; observable — the run chain (park → menus → LIVE), the
hold row (keydown→keyup walls + phase match vs T42), blind 10-snap
series + per-snap HUD + tracking metrics from ALL THREE trackers (frozen
control + ROI-retuned + gradient) + per-hop whole diffs, all scored
post-hoc from fetched snaps, with lock-QA grades (marked-crop montage
method) on every VALID pair; screen content read off viewed snaps;
alternatives — the hold crashes AGAIN (→ table speed/position/HUD and
STOP the motion verdict at one more data point; no third run in this
brief), the distributions overlap (→ table exact counts + recipe), the
run never reaches live gameplay at a matched phase (→ environment
NO-PARK per T27 §4, bounded re-run); stop — table the distribution
verdict + recipe. One input shape per attempt (the hold is FIXED), one
accumulation run max (crash or clean).

## T43-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T43; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T43]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; disk
pins taken on VM-H51, VM-independent across turnover):

| Item | T4 value | T43 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Pad binding (Left) | — | `Left = Keyboard/Left`, `PCSX2.ini:576` (the hold key; re-verified) | yes |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…` reproduces T35 | yes |
| T42 reference snaps present | — | on-box `t42-npre1.jpg` 53597 B = committed size (116 `t42-*.jpg` intact) | yes |
| Free space | — | WSL `/` 852 G pre; C: 11 G pre (GATE ~5 GB+ PASSES — T42's post-session level; ~2 GB/run drain watched) | yes |
| Live trace pre-run | — | `emulog.txt` 2751948037 B = T42 R3 (preserved at R1 boot via `emulog-pre-t43-20260921T194932Z.txt`) | yes |
| WSLg audio pre-run | — | socket PRESENT (informational ONLY — T42 lesson: presence gave false healthy); behavioral gate at boot (modal census, §T43-5) | gate |

Phase-match targets (tabled BEFORE the run — T42 R3's hold window, match
PHASE not seed; AI lineup/RNG differ run to run):

| Item | T42 hold-window value | T43 hold-window target |
|---|---|---|
| Hold slot | T+502.49 (keydown) | ≈T+502.5 (same script slot) |
| Pre-pair race clocks | 00:01:27 / 00:01:28 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | 5TH/5TH/6 | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 36% / 37% | ≈36–37% ±5 pp |
| Series span | 10 snaps over +7.37 s wall / +11 s race | 10 snaps over ≈+7.4 s wall (same `sleep 0.5` blind capture) |

Same-shape record (tabled BEFORE the run — the deliberate NON-change):

| Item | T42 R3 (`sleep 0.5`) | T43 (this run) |
|---|---|---|
| Dense-phase shape | `sleep 0.5` + capture only; ns wall stamps per snap; ZERO scoring calls | identical (script rename-only, verified: dense span zero scoring calls) |
| Pre-pair gap | `sleep 0.5`, no scoring (measured 0.5761 s) | identical call |
| Hold | ONE `press_hold Left` (1 s `sleep`, T38's body) | identical call, same slot |
| Post-hold | 10 × (`sleep 0.5`, `bsnap d-postN`) | identical calls |
| Dense span (npre1→d-post10) | 7.3708 s wall | ≈7.4 s wall expected |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log | scp via C: staging (T25 recipe) | `t43r1-*.jpg`, `t43r1-poll.log` |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t43-cropdiff.py`, bit-exact validated (T39/T40/T41/T42 protocol); committed tool reproduces any score | screen chain table + xrun frame identities vs T42 R3 |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking, CONTROL | committed `t41-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. Dense 12-snap tracking, ROI | committed `t42-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 6. Dense 12-snap tracking, GRADIENT | committed `t43-track.py` (Task 1 variant) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 7. View all snaps | local reads | HUD per snap (clock/position/progress/speed/score) |
| 8. Lock-QA every VALID pair | marked-crop montage method (T42) | on/borderline/off + named intruder per snap; on→on distribution |
| 9. Distribution verdict | — | hold-step vs no-input separation verdict + exact counts + recipe |

Distributions to separate (tabled BEFORE the run — T42 R3 baseline):

| Distribution | T42 pairs (retuned) | T42 pairs (gradient, Task 1) |
|---|---|---|
| No-input | npre1→npre2 Δ(−0.7,−22.2) on→on (1 sample) | npre1→npre2 Δ(+1.8,+4.8) on→on (1 sample) |
| Hold-step | npre2→d-post1 Δ(+11.2,−39.5) on→borderline (crash inside) | npre2→d-post1 Δ(−4.4,−24.1) on→borderline (crash inside) |
| Extra on→on (cruise) | none (d6d7/d7d8 borderline-grade) | d5d6 (+0.0,+10.6), d6d7 (+2.7,−3.9), d7d8 (−2.1,−4.2) |

## T43-1. Task 1 — gradient static test (no run)

### T43-1a. Reproduction gate (controls on T42 R3's 12 committed dense snaps FIRST)

| Check | Result |
|---|---|
| `t41-track.py` on T41 R4 12 snaps vs T41 §hold table | 12/12 RDC + 11/11 SCPS40 + 11/11 SCPS120 reproduce EXACTLY (corr to 4 dp) — environment/decoder sound |
| `t42-track.py` on T41 R4 12 snaps vs T42 §T42-1 calibration | 12/12 RDC (cx/cy/npix/gate) reproduce EXACTLY — T42's retuned pipeline trustworthy |
| `t42-track.py` RDC on T42 R3 12 snaps vs T42 §T42-6 retuned column | 12/12 reproduce EXACTLY |
| `t41-track.py` RDC on T42 R3 12 snaps vs T42 §T42-6 frozen column | gate PATTERN reproduces (11/12 INVALID, npre2 singleton VALID) but exact cx/cy/npix differ on 10/12 — T43 re-scored values tabled below |
| SCPS (all three tools agree bit-identically) on T42 R3 snaps vs T42 §T42-6 | pre-pair + hold hop + all 4 SCPS40 rail rows + SCPS120 rails match; middle 5 rows (d2d3–d6d7) differ; d1d2 SCPS120 same lag (+118), corr 0.19 vs 0.48 — re-scored values tabled below |
| Rail rates vs T42 §T42-6 claims | SCPS40 4/11 ✓, SCPS120 strict 2/11 ✓, hold rows exact ✓, `SCPS 22/22 identical` across tools ✓ (all three tools, `cmp` clean) |
| `t41-track.py`/`t42-track.py` byte-identical | untouched (tracked tree clean; T43 adds new files only) |

Reproduction-gap finding (tabled, load-bearing claims survive): T42's
R3 frozen-RDC exact centroids/counts and middle SCPS rows do not
reproduce from the committed bytes via the committed tools, while every
other cell of T42's tracking pipeline does (retuned 12/12, T41 34/34,
calibration 12/12, rails/hold rows). Same bytes + same deterministic
code must give same output — so those cells were scored from different
bytes than committed (mechanism unknowable from here; most likely a
different fetch state of the middle snaps at scoring time — the
mismatching rows all involve d-post3–d-post6). The load-bearing T42
claims all survive: control floods 11/12 with the npre2 singleton,
retuned 9/12 gated exact, the hold-straddling pair values exact (the
distribution input), SCPS rail rates + hold rows exact. T43's own run is
scored fresh with all three trackers — no dependence on the stale cells.

T43 re-scored frozen RDC + SCPS on T42 R3's 12 snaps (committed tools,
committed bytes — the corrected record):

| Snap | Frozen cx/cy/npix | Gate | Retuned (T42, exact ✓) |
|---|---|---|---|
| npre1 | 381.2/245.9, 12942 | INVALID | 332.7/314.5, 3515 VALID |
| npre2 | 350.1/238.3, 3563 | VALID | 332.0/292.3, 1484 VALID |
| d-post1 | 434.9/199.8, 26354 | INVALID | 343.2/252.8, 5000 VALID |
| d-post2 | 386.5/229.0, 31267 | INVALID | 327.8/264.2, 10162 INVALID |
| d-post3 | 299.9/212.9, 15708 | INVALID | 270.4/245.3, 8316 INVALID |
| d-post4 | 326.1/220.7, 28282 | INVALID | 258.5/259.5, 5147 VALID |
| d-post5 | 330.1/182.6, 23085 | INVALID | 279.0/234.3, 5026 VALID |
| d-post6 | 320.3/218.7, 20346 | INVALID | 287.9/275.0, 4333 VALID |
| d-post7 | 338.2/159.2, 14016 | INVALID | 295.3/247.1, 3050 VALID |
| d-post8 | 438.6/152.4, 11680 | INVALID | 303.4/285.1, 1492 VALID |
| d-post9 | 381.9/149.0, 19617 | INVALID | 350.2/231.9, 2622 VALID |
| d-post10 | 260.0/182.1, 33192 | INVALID | 289.9/225.7, 9389 INVALID |

| Hop | SCPS40 re-scored (T42 table) | SCPS120 re-scored (T42 table) |
|---|---|---|
| npre1→npre2 | +9 @ 0.83 ✓ | +9 @ 0.83 ✓ |
| npre2→d-post1 (HOLD) | +13 @ 0.23 ✓ | +120 @ 0.60 RAIL ✓ |
| d-post1→d-post2 | +40 @ −0.25 RAIL ✓ | +118 @ 0.19 (+118 @ 0.48) |
| d-post2→d-post3 | +14 @ 0.74 (−6 @ 0.28) | +14 @ 0.74 (−115 @ 0.53) |
| d-post3→d-post4 | −34 @ 0.13 (+3 @ 0.73) | −115 @ 0.27 (+119 @ 0.60) |
| d-post4→d-post5 | −18 @ 0.04 (−4 @ 0.72) | +119 @ 0.34 (−4 @ 0.72) |
| d-post5→d-post6 | −31 @ 0.73 (+33 @ 0.64) | −31 @ 0.73 (+33 @ 0.64) |
| d-post6→d-post7 | −24 @ 0.84 (+18 @ 0.35) | −24 @ 0.84 (−98 @ 0.44) |
| d-post7→d-post8 | −40 @ 0.84 RAIL ✓ | −46 @ 0.85 (−40 @ 0.84) |
| d-post8→d-post9 | +40 @ 0.31 RAIL ✓ | +103 @ 0.81 (+40 @ 0.31) |
| d-post9→d-post10 | −40 @ 0.24 RAIL ✓ | −120 @ 0.80 RAIL (−120 @ 0.35) |

(Rail/✓ marks: 6/11 SCPS40 rows match incl. all rails + hold; SCPS120
rails + hold lag match with corr deltas on d1d2/d9d10. Full-corr
profiles from committed bytes are smooth single-peaked — e.g. d1d2
+118:0.1858, +119:0.1857, +117:0.1850 — the tabled 0.48/0.53/0.60 middle
corrs cannot come from these bytes.)

### T43-1b. The gradient variant (ONE new file + calibration)

Design (T40's third shape, specified here — prior reports name it but
never specify it): same ROI x[220,420] y[180,360], same DARK_MAX 80, but
the dark mask is AND-gated with a Sobel gradient-magnitude floor
(`|Gx|+|Gy| >= GRAD_MIN`, numpy-only, edge-padded): smooth dark
expanses (shade glow, trunk interiors, totem faces, wall faces) carry
little gradient and drop out, while the rider complex (limbs / board /
helmet edges against snow) survives. Counts scale ~30–50% of dark
counts on rider snaps → the validity gate is RECALIBRATED (see sweep).
SCPS untouched.

| Constant | ROI (`t42-track.py`) | Gradient (`t43-track.py`) |
|---|---|---|
| `RIDER_ROI` | x[220,420] y[180,360] | identical |
| `DARK_MAX` | 80 | 80 (frozen) |
| Gradient floor | — | `GRAD_MIN = 60` (Sobel `\|Gx\|+\|Gy\|`, luma units) |
| Gate | 200 ≤ npix ≤ 6000 | 500 ≤ npix ≤ 3000 (recalibrated — see sweep) |
| `SNOW_ROWS`/`SNOW_COLS`, lags | y[380,460] x[150,540], ±40/±120 | identical (SCPS bit-identical 3-way, `cmp` clean) |

Gradient-threshold sweep on T42 R3's 12 snaps (npix per GRAD_MIN;
GRAD_MIN 0 reproduces the retuned column exactly — sanity ✓):

| Snap | g0 | g10 | g20 | g30 | g40 | g60 | g80 |
|---|---|---|---|---|---|---|---|
| npre1 | 3515 | 2522 | 1992 | 1616 | 1316 | 928 | 650 |
| npre2 | 1484 | 1467 | 1417 | 1324 | 1221 | 1027 | 869 |
| d-post1 | 5000 | 4807 | 4285 | 3676 | 3113 | 2252 | 1656 |
| d-post2 (flood) | 10162 | 9129 | 7874 | 6740 | 5825 | 4448 | 3520 |
| d-post3 (flood) | 8316 | 7565 | 5960 | 4422 | 3252 | 2046 | 1577 |
| d-post4 | 5147 | 4736 | 4048 | 3411 | 2858 | 1993 | 1437 |
| d-post5 | 5026 | 3697 | 2159 | 1449 | 1151 | 845 | 624 |
| d-post6 | 4333 | 3196 | 2232 | 1834 | 1568 | 1271 | 1070 |
| d-post7 | 3050 | 2391 | 1729 | 1542 | 1395 | 1176 | 981 |
| d-post8 | 1492 | 1482 | 1435 | 1347 | 1248 | 1069 | 912 |
| d-post9 | 2622 | 2060 | 1736 | 1564 | 1429 | 1171 | 985 |
| d-post10 (flood) | 9389 | 4917 | 3550 | 2815 | 2384 | 1824 | 1509 |

Sweep verdict (centroid tracks + montages at g40/g60): the gradient
RECENTERS smooth-intruder bias at any floor ≥40 (d5 cy 234→276→283
toward the rider; d9 cx 350→329→326; d1 cx/cy 343/253→334/260→328/267)
while on-rider snaps stay put (npre2/d8 move ≤2 px across the whole
sweep); but flood counts NEVER separate — bark/wall edges are
gradient-rich (d3 < d1 at every floor: 3252 vs 3113 at g40, 2046 vs
2252 at g60 — inverted: the off-rider trunk has FEWER edge pixels than
the rider crash snap, so no count band gates d3 while keeping d1).
Operating point g60 + band 500–3000: min margin 1.7× (d5 845), max
margin 1.33× above the largest rider lock (d1 2252) and 1.48× below the
d2 flood (4448); gates exactly d2 by count; d3/d10 stay VALID (d3
off-rider = the gate hole, caught by lock-QA; d10 borderline-on-head =
rider-dominated here, failure mode tabled).

Gradient calibration table (committed `t43-track.py` on T42 R3's 12
snaps; lock quality judged on marked ROI crops: gradient-gated pixels
tinted red, centroid crosshair — `/tmp` scratch montages, T42's method):

| Snap | Gradient npix + gate | Gradient cx/cy | ROI cx/cy | Centroid sits on | Verdict |
|---|---|---|---|---|---|
| npre1 | 928 VALID | 330.3/285.8 | 332.7/314.5 | rider mid-body | on-rider |
| npre2 | 1027 VALID | 332.1/290.6 | 332.0/292.3 | rider mid-body | on-rider |
| d-post1 | 2252 VALID | 327.7/266.5 | 343.2/252.8 | tumbling body edge (trunk-edge intrudes right) | borderline-on |
| d-post2 | 4448 INVALID | 321.2/263.4 | 327.8/264.2 | black tree (flood) | off-rider — correctly gated |
| d-post3 | 2046 VALID | 288.7/279.5 | 270.4/245.3 | LEFT TRUNK (bark texture) | off-rider — GATE HOLE |
| d-post4 | 1993 VALID | 268.1/264.5 | 258.5/259.5 | rider, left edge (trunk-edge pulls) | borderline-on |
| d-post5 | 845 VALID | 302.8/283.0 | 279.0/234.3 | rider upper body (shade rejected) | on-rider (was off ~40 px) |
| d-post6 | 1271 VALID | 302.8/293.6 | 287.9/275.0 | rider torso | on-rider (was borderline) |
| d-post7 | 1176 VALID | 305.5/289.7 | 295.3/247.1 | rider legs/body | on-rider (was borderline) |
| d-post8 | 1069 VALID | 303.4/285.5 | 303.4/285.1 | rider | on-rider |
| d-post9 | 1171 VALID | 325.5/260.6 | 350.2/231.9 | ~15 px right of shoulder (chevron edges) | borderline-on (was off ~50 px) |
| d-post10 | 1824 VALID | 309.2/258.6 | 289.9/225.7 | rider head/helmet (rider-dominated HERE) | borderline-on (ROI gated — wall failure mode noted) |

Gradient deltas on T42 R3 (VALID pairs, with lock QA — the Task-2
baseline; ROI deltas in T42 §T42-6):

| Pair | Δcx/Δcy | Lock QA | Note |
|---|---|---|---|
| npre1→npre2 (no-input floor) | +1.8 / +4.8 | on→on | cx floor ≈ 0 (1 sample) |
| npre2→d-post1 (HOLD) | −4.4 / −24.1 | on→borderline | hop contains the TREE CRASH — unresolved |
| d-post3→d-post4 | −20.6 / −15.0 | off→borderline | lock change — bias-contaminated |
| d-post4→d-post5 | +34.7 / +18.5 | borderline→on | same-quality-ish pair |
| d-post5→d-post6 | +0.0 / +10.6 | on→on | — |
| d-post6→d-post7 | +2.7 / −3.9 | on→on | — |
| d-post7→d-post8 | −2.1 / −4.2 | on→on | — |
| d-post8→d-post9 | +22.1 / −24.9 | on→borderline | chevron bias survives |
| d-post9→d-post10 | −16.3 / −2.0 | borderline→borderline | — |

(d1→d2, d2→d3: d2 INVALID — no pair. Gradient yields 4 on→on pairs on
T42R3 vs the ROI's 1 — the accumulation gain, if the new run agrees.)

Held-out check (T41 R4's 12 dense snaps — reported as-is, ZERO tuning):

| Snap | Gradient npix + gate | Lock QA (montage) | ROI verdict (T42 calib) |
|---|---|---|---|
| npre1 | 893 VALID | on-rider | on-rider |
| npre2 | 1521 VALID | borderline-on (tree-edge pulls right) | borderline-on |
| d-post1 | 2073 VALID | on-rider | on-rider |
| d-post2 | 1936 VALID | off-rider ~25 px above (tree) — NOT fixed | off-rider (tree) |
| d-post3 | 1739 VALID | off-rider (arch/tree) — NOT fixed | off-rider (tree) |
| d-post4 | 976 VALID | on-rider | borderline-on |
| d-post5 | 794 VALID | on-rider | on-rider |
| d-post6 | 1114 VALID | on/borderline (helmet) — recentered | off-rider (barrier) |
| d-post7 | 1273 VALID | on-rider | borderline-on |
| d-post8 | 891 VALID | on-rider | on-rider |
| d-post9 | 1409 VALID | on-rider — recentered | off-rider (gate pole) |
| d-post10 | 1433 VALID | borderline-on (crash debris + wall mix) | wall — ROI gated |

Held-out 12/12 VALID (ROI: 11/11 non-wall + wall gated): the gradient
fixes smooth-intruder bias (T41 d6 barrier, d9 gate pole — same class
as T42 d5 shade / d9 totem faces) but NOT textured-intruder bias (T41
d2/d3 tree/arch — same class as the T42 d3 trunk hole) and does NOT
gate floods (T41 d10 wall VALID). Consistent in both directions — the
overfit risk T42 warned about does not materialize as a sign flip, but
the gate hole generalizes too.

Task-1 verdict (tabled — the run proceeds regardless): the gradient
separates SMOOTH dark intruders (shade glow, totem faces, barrier, gate
pole) and recenters d5 off→on, d9 50px→~15px, d1 slightly — but it
cannot gate edge-rich floods (d2/d3/d10-class: bark, foliage edges,
wall panels all survive the gradient floor, and no count band separates
d3 from d1 at any floor). The ROI gate remains the operative flood
defense; the gradient's value is centroid quality (more on→on pairs),
not gating. Both score the new run in parallel.

Script receipts (frozen BEFORE the run):

| Item | Value |
|---|---|
| `t43-track.py` | T42's + Sobel gradient AND-gate (`GRAD_MIN=60`) + recalibrated band (500–3000) + header note, sha `2e532a2d…b3fcd` (4323 B) |
| `t43-cropdiff.py` | byte-identical to T42's (`cmp` clean), sha `ac114212…0826a53` |
| `t43-vcount.sh` | byte-identical to T42's (`cmp` clean), sha `105cd092…39107d76` |
| `t43-analyze.sh` | output-name deltas only (`t43-census/samples`), sha `2b402210…4a131f`; `bash -n` clean |
| `t43-auto.sh` | T42 copy + renames ONLY (every diff line contains `t42-`/`t43-`/`T42`/`T43`), sha `0b501c38…c0cd4e`; `bash -n` clean; zero `sham` references; exactly one `press_hold Left` call; dense block zero scoring calls; `sleep 0.5` count 14 = T42's 14 |
| `t43-dialogwatch2.sh` | byte-identical to T42's v2 (`cmp` clean), sha `d9c7a4c1…41faa` (zero `t42` references — generic) |
| Staged shas | all 5 WSL-staged shas match local (auto `0b501c38…`, analyze `2b402210…`, vcount `105cd092…`, cropdiff `ac114212…`, dialogwatch2 `d9c7a4c1…`) |
| PPM self-check | panel ref 0.0000/0 on the run VM pre-run |
| T41/T42 originals | untouched (tracked tree clean at commit; T43 dir is new) |
| Rename-completeness fix | `t43-auto.sh:305/317` `xvfb-t42.log`/`boot-t42.log` → `t43` (the `t42-` sed missed `t42.` log paths; R1 wrote its boot logs over T42's ON-BOX copies — committed T42 evidence intact; behavior-neutral log sinks; fix staged only if R2 runs) |

## T43-2. Session log (H51 — no turnover, activity-held throughout)

Clocks: WSL `date -u` true UTC; `wevtutil` renders local-as-Z (+4 h →
UTC); H-numbers continue T42's H50.

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 19:46:58 ([0] VM-H51) | H51 demand-boot (WSL fully Stopped at session start) | btime 1790020016 |
| 2 | 19:47–19:49 | Pins (binary/tree/inputs/NVM/bindings/9 refs/T42 snaps/live trace/C:/socket-present-informational) | §T43-0 table |
| 3 | 19:49 | Staging (5 files, shas match) + X11 tmpfs mount (root) + PPM 0.0000/0 + dmesg-pre + eventlog-pre | `t43-dmesg-h51-pre.txt` (519 lines, 1 AcceptAsync [93.67] boot noise); eventlog-pre 120 entries |
| 4 | 19:49:32–19:58:51 ([156]→[682] H51) | R1: A1 title-detect @poll01 → full chain → ONE 1037.2 ms Left hold → blind 10-snap series; `DENSE-BLIND-COMPLETE`, `T43_DONE`, exit 0 | stdout 460 lines, stderr 2551 lines, poll log 168 lines |
| 5 | 19:50:33 (T+61.9) | Dialogwatch v2a: SKIP-GAME 2097159 + DISMISS 2097162 `pcsx2-qt` + DISMISSED-EXIT (no modal; R3 pattern) | `t43r1-dialogwatch.txt` |
| 6 | ~T+85 | Window census: game 2097159 present, no `Error` modal → no v2b | census output |
| 7 | 19:59–20:0x | Post-R1 dmesg (SAME VM) + fetch 61 JPGs + poll log + analyze + boot logs + NVM/C: post + eventlog-final + trace stream + refs fetch | files below |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` (as root, T4 recipe) on H51 pre-R1; does not persist reboot |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the run |
| Dirs/files created | `/home/brad/pcsx2-t4/t43-{auto,analyze,vcount,cropdiff}.sh/.py`, `t43-dialogwatch2.sh`, `t43-{census,samples}.txt` (via analyze), `t43-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t43-20260921T194932Z.txt` (T42R3's trace, 2751948037 B), `C:\Users\bradr\pcsx2-t4\t43*` staging (removed after each batch) |
| Dirs/files OVERWRITTEN | `…/logs/boot-t42.log` + `boot-t42.stdout` now hold R1's boot (rename miss, §T43-1b receipt; T42's committed copies intact; R1's content fetched as `t43r1-boot.*`) |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| Restarts by me | None (no shutdown, no service bounce — audio healthy on first boot) |
| VM restarts (not by me) | None this session (H51 held 0→682+ by activity; zero turnover) |

## T43-3. R1 — full chain + ONE hold + blind dense series (the run)

R1 booted on VM-H51 (T_BOOT 1790020172, uptime 156; 19:49:32 UTC) under
HEALTHY audio (cubeb-pulse negotiated [0.4689/0.4709], zero
null-fallback/CUBEB_ERROR lines in 2.79 GB, full libsd IOP set, no modal
on 61/61 snaps) and reproduced the T42 R3 chain: A1 title-detect @poll01
(remote 0.4337/6 — T42 R3's 0.4331/6), all 8 menu gates, MR panel settle,
X countdown, LIVE race, pre-hold pair, ONE 1037.2 ms Left hold, 10-snap
blind series. `DENSE-BLIND-COMPLETE`, `T43_DONE`, exit 0, clean SIGTERM
shutdown at uptime 682 (T+526; T42 R3: T+518). 460-line stdout /
2551-line stderr (T42 R3: 514/2551). WID 2097159 (same as T31–T42).

| Item | Value |
|---|---|
| R1 window | 19:49:32–19:58:51 UTC (T+0–519), VM-H51 uptime 156→682 (ZERO in-window flaps: 1 AcceptAsync [93.67] pre + [731.82] post; ZERO in-window event-log entries — 15:46:56 pre-window newest, nothing 15:49–15:58) |
| Dialogwatch v2 | ROUND:1 @T+61.9: SKIP-GAME 2097159 + DISMISS 2097162 `pcsx2-qt` + DISMISSED-EXIT (main-window, inert — R3 pattern; NO modal existed to dismiss; window census ~T+85: game-only, no modal) → no v2b |
| Title detect | A1 `poll01` remote 0.4337/6 (PIL 0.0453/0) — parked FIRST attempt (a2/a3 never ran; no stale) |
| Presses | 10 menu/Start Cross (all 535.0–538.7 ms) + ONE hold (§press log); ZERO other game inputs (11 KEYDOWN/KEYUP pairs total in 168-line poll log = T42 R3's 168) |

### R1 press log (poll-log walls; T+ = wall − 1790020172)

| Press | Keydown wall (T+) | Keyup wall (T+) | Width |
|---|---|---|---|
| A1 Cross (attract-skip) | 1790020270.474 (T+98.47) | 1790020271.010 (T+99.01) | 535.5 ms |
| A1 Start (on title) | 1790020273.768 (T+101.77) | 1790020274.303 (T+102.30) | 535.6 ms |
| MENU Cross (Single Event) | 1790020313.254 (T+141.25) | 1790020313.789 (T+141.79) | 535.1 ms |
| ZOE Cross | 1790020355.506 (T+183.51) | 1790020356.044 (T+184.04) | 537.6 ms |
| CONT Cross | 1790020385.146 (T+213.15) | 1790020385.682 (T+213.68) | 535.5 ms |
| PEAK Cross (Peak 1) | 1790020414.336 (T+242.34) | 1790020414.871 (T+242.87) | 535.0 ms |
| RACE Cross | 1790020444.213 (T+272.21) | 1790020444.752 (T+272.75) | 538.7 ms |
| SNOWJAM Cross | 1790020475.949 (T+303.95) | 1790020476.484 (T+304.48) | 535.0 ms |
| ENTER Cross | 1790020504.951 (T+332.95) | 1790020505.488 (T+333.49) | 536.5 ms |
| X Cross (X Continue) | 1790020612.440 (T+440.44) | 1790020612.978 (T+440.98) | 538.0 ms |
| HOLD Left | 1790020681.339 (T+509.34) | 1790020682.376 (T+510.38) | 1037.2 ms |

### R1 chain table (61/61 fetched; T+ = scored MENU_T+ anchors, else T42-offset interpolation; PIL panel scores; viewed frames marked)

| Snap (T+) | Size | Band vs title (PIL) | Best ref (PIL) | Content |
|---|---|---|---|---|
| start (T+97) | 37310 | 45.6884/224 | attract | attract (remote 45.6797/224) |
| a1-now (T+98) | 57173 | 25.3186/142 | attract | attract (remote 25.3158/142) |
| a1-poll01 (T+101) | 58388 | 0.0453/0 | TITLE | TRUE TITLE (viewed; remote 0.4337/6) |
| a1-pre (T+101) | 58388 | 0.0453/0 | TITLE | = poll01 (cp-identical scores) |
| a1-post3 (T+106) | 49992 | 16.2601/138 | menu 0.0624/1 | Main Menu (remote 16.2581/139) |
| a1-post8 (T+112) | 50010 | 16.2929/138 | menu 0.0621/1 | Main Menu |
| a1-post15 (T+120) | 49625 | 16.2622/138 | menu 0.0260/0 | Main Menu |
| a1-post25 (T+130) | 49730 | 16.2622/138 | menu 0.0403/0 | Main Menu |
| menupre (T+140) | 49938 | 16.2622/138 | menu 0.0566/0 | Main Menu (viewed; Single Event; remote vs-menu 0.3132/5) |
| mc-post1 (T+145) | 70536 | 12.5423/163 | sc 0.2774/5 | Select Character (remote vs-sc 0.6230/9) |
| mc-post3 (T+150) | 70394 | 12.5018/163 | sc 0.1402/3 | Select Character |
| mc-post8 (T+158) | 70919 | 12.4626/163 | sc 0.1639/4 | Select Character |
| mc-post15 (T+167) | 70882 | 12.4626/163 | sc 0.1477/4 | Select Character |
| scpre (T+181) | 70834 | 12.4557/163 | sc 0.1903/4 | Select Character (viewed; Zoe; remote vs-sc 0.5315/8) |
| zc-post1 (T+187) | 51277 | 15.8334/128 | zc 0.2750/6 | Setup Character (remote vs-zc 0.5106/8) |
| zc-post3 (T+192) | 51434 | 15.8398/128 | zc 0.2510/6 | Setup Character |
| zc-post8 (T+200) | 51744 | 15.7355/128 | zc 0.2669/7 | Setup Character |
| ccpre (T+211) | 51498 | 15.8342/128 | zc 0.2647/7 | Setup Character (viewed; Zoe/Continue; remote vs-zc 0.4943/9) |
| sp-post1 (T+217) | 65415 | 23.1259/171 | sp 0.0356/0 | Select Peak (remote vs-sp 0.3818/6) |
| sp-post3 (T+222) | 65279 | 23.1259/171 | sp 0.0098/0 | Select Peak |
| sp-post8 (T+230) | 65347 | 23.1185/171 | sp 0.0266/0 | Select Peak |
| sppre (T+240) | 65353 | 23.1259/171 | sp 0.0117/0 | Select Peak (re-captured, NOT a cp: scores differ from sp-post3; remote vs-sp 0.3611/5) |
| pc-post1 (T+246) | 67319 | 26.3051/183 | sm 0.0395/0 | Select Mode (remote vs-sm 0.3894/6) |
| pc-post3 (T+251) | 67341 | 26.3050/183 | sm 0.0355/0 | Select Mode |
| pc-post8 (T+259) | 67472 | 26.3054/183 | sm 0.0521/0 | Select Mode |
| smpre (T+269) | 67353 | 26.3022/183 | sm 0.0413/0 | Select Mode (viewed; Race; remote vs-sm 0.3914/6) |
| rc-post1 (T+276) | 69450 | 26.1933/183 | se 0.0324/0 + setag 0.0094/0 | Select Event (remote se-tag 2.6271/11 — reproduces T42's exact) |
| rc-post3 (T+281) | 69570 | 26.1855/183 | se 0.0508/0 + setag 0.0094/0 | Select Event |
| rc-post8 (T+289) | 69605 | 26.1964/183 | se 0.0583/0 + setag 0.0094/0 | Select Event |
| sepre (T+300) | 69495 | 26.1964/183 | se 0.0380/0 + setag 0.0652/2 | Select Event (viewed; Snow Jam; remote se-tag 2.6271/11) |
| sj-post1 (T+308) | 58803 | 9.8197/135 | mr 0.1223/1 | My Rules (remote vs-mr 0.4361/7) |
| sj-post3 (T+313) | 58611 | 9.8274/135 | mr 0.1000/1 | My Rules |
| sj-post8 (T+321) | 59131 | 9.8142/135 | mr 0.1612/2 | My Rules |
| mrpre (T+331) | 58756 | 9.8138/135 | mr 0.1102/1 | My Rules (viewed; all Off; remote vs-mr 0.4258/7) |
| mr-post1 (T+337) | 66795 | 17.2333/167 | loading | Race loading 18% (viewed) |
| mr-post3 (T+342) | 67135 | 17.5522/171 | loading | Race loading 98% (viewed) |
| mr-post8 (T+349) | 55048 | 32.8344/237 | pre-race | Pre-race cinematic (viewed; EA Radio, Press X to skip) |
| mr-post15 (T+359) | 60007 | 34.5153/184 | pp 0.4276/6 | Panel |
| mr-post25 (T+372) | 59954 | 34.5130/184 | pp 0.3927/6 | Panel |
| mr-post40 (T+390) | 59842 | 34.5106/184 | pp 0.4883/8 | Panel |
| mr-stab1 (T+414) | 59529 | 34.5105/184 | pp 0.7280/19 | Settled panel (remote vs-pp 0.9854/19) |
| mr-stab2 (T+427) | 59873 | 34.5068/184 | pp 0.4314/6 | Settled panel (remote vs-pp 0.6963/9) |
| pppre (T+438) | 59935 | 34.5131/184 | pp 0.3974/6 | Settled panel (viewed; 6 riders, Zoe; remote vs-pp 0.6734/9) |
| x-post1 (T+443) | 70533 | 18.6949/149 | departed | Start gate countdown 2, 00:00:00 (viewed; remote vs-pp 14.4698/153) |
| x-post3 (T+447) | 67976 | 21.1836/141 | live | LIVE 5TH/6, 00:00:02, 1%, 38 MPH (viewed) |
| x-post8 (T+454) | 68154 | 13.9170/130 | live | LIVE 3RD/6, 00:00:10, 5%, 50 MPH, rival wipeout right (viewed) |
| x-post15 (T+462) | 65221 | 15.7112/153 | live | LIVE 3RD/6, 00:00:23, 11%, 50 MPH (viewed) |
| x-post25 (T+474) | 55854 | 13.7229/135 | live | LIVE 1ST/6, 00:00:38, 20%, 58 MPH (viewed) |
| x-post40 (T+491) | 62329 | 18.8927/133 | live | LIVE 1ST/6, 00:01:01, 32%, 62 MPH, score 1390 (viewed) |
| npre1 (T+508.7) | 59433 | 20.4673/133 | live | LIVE 1ST/6, 00:01:27, 43%, 29 MPH — TREE CRASH, RECOVER meter (viewed) |
| npre2 (T+509.3) | 58059 | 19.3001/132 | live | LIVE 1ST/6, 00:01:27, 44%, 16 MPH, snow-spray whiteout, rider obscured (viewed) |
| d-post1 (T+510.9) | 49146 | 40.4057/191 | live | LIVE 1ST/6, 00:01:30, 45%, 10 MPH — WALL TUMBLE (viewed) |
| d-post2 (T+511.5) | 50441 | 41.1452/192 | live | LIVE 2ND/6, 00:01:30, 45%, 5 MPH — PINNED AT WALL (viewed) |
| d-post3 (T+512.0) | 49288 | 38.9446/189 | live | LIVE 2ND/6, 00:01:31, 45%, 17 MPH, pushing off wall (viewed) |
| d-post4 (T+512.6) | 54531 | 28.1577/142 | live | LIVE 2ND/6, 00:01:32, 45%, 30 MPH, racing under bridge (viewed) |
| d-post5 (T+513.2) | 57887 | 16.2430/105 | live | LIVE 2ND/6, 00:01:33, 46%, 40 MPH (viewed) |
| d-post6 (T+513.8) | 61539 | 24.4588/129 | live | LIVE 2ND/6, 00:01:34, 46%, 44 MPH (viewed) |
| d-post7 (T+514.3) | 60075 | 21.4536/120 | live | LIVE 2ND/6, 00:01:35, 47%, 44 MPH (viewed) |
| d-post8 (T+514.9) | 60567 | 20.0701/114 | live | LIVE 2ND/6, 00:01:35, 47%, 44 MPH (viewed) |
| d-post9 (T+515.5) | 58089 | 13.6229/106 | live | LIVE 2ND/6, 00:01:36, 47%, 47 MPH, banked turn (viewed) |
| d-post10 (T+516.1) | 57859 | 13.9084/133 | live | LIVE 2ND/6, 00:01:37, 47%, 49 MPH, bank carve (viewed) |

### R1 transition hops (whole-frame PIL; dense hops have NO in-script remote counterpart)

| Hop | Whole (PIL) | Hop | Whole (PIL) |
|---|---|---|---|
| start→a1-now | 16.8323/173 | a1-now→a1-poll01 | 17.6636/164 |
| a1-poll01→a1-pre | 0.0000/0 | a1-pre→a1-post3 | 14.1119/151 |
| a1-post3→a1-post8 | 0.0757/1 | a1-post8→a1-post15 | 0.0393/0 |
| a1-post15→a1-post25 | 0.0151/0 | a1-post25→menupre | 0.0441/0 |
| menupre→mc-post1 | 10.1552/105 | mc-post1→mc-post3 | 0.3376/9 |
| mc-post3→mc-post8 | 0.1985/5 | mc-post8→mc-post15 | 0.0500/1 |
| mc-post15→scpre | 0.2561/7 | scpre→zc-post1 | 7.2280/100 |
| zc-post1→zc-post3 | 0.2428/5 | zc-post3→zc-post8 | 0.1813/4 |
| zc-post8→ccpre | 0.3332/10 | ccpre→sp-post1 | 9.4178/153 |
| sp-post1→sp-post3 | 0.0377/0 | sp-post3→sp-post8 | 0.0287/0 |
| sp-post8→sppre | 0.0305/0 | sppre→pc-post1 | 5.1850/121 |
| pc-post1→pc-post3 | 0.0053/0 | pc-post3→pc-post8 | 0.0189/0 |
| pc-post8→smpre | 0.0247/0 | smpre→rc-post1 | 0.4822/7 |
| rc-post1→rc-post3 | 0.0207/0 | rc-post3→rc-post8 | 0.0467/0 |
| rc-post8→sepre | 0.0338/0 | sepre→sj-post1 | 10.5730/143 |
| sj-post1→sj-post3 | 0.0784/0 | sj-post3→sj-post8 | 0.1174/1 |
| sj-post8→mrpre | 0.1277/1 | mrpre→mr-post1 | 12.4310/148 |
| mr-post1→mr-post3 | 0.9936/37 | mr-post3→mr-post8 | 25.3249/253 |
| mr-post8→mr-post15 | 18.4047/190 | mr-post15→mr-post25 | 0.0584/2 |
| mr-post25→mr-post40 | 0.1602/7 | mr-post40→mr-stab1 | 0.2598/11 |
| mr-stab1→mr-stab2 | 0.3234/14 | mr-stab2→pppre | 0.1062/4 |
| pppre→x-post1 | 14.5388/153 | x-post1→x-post3 | 14.0529/135 |
| x-post3→x-post8 | 13.0222/121 | x-post8→x-post15 | 10.2645/135 |
| x-post15→x-post25 | 8.1158/124 | x-post25→x-post40 | 16.7728/123 |
| x-post40→npre1 | 9.0453/134 | npre1→npre2 | 7.6524/123 |
| npre2→d-post1 (HOLD) | 15.9403/154 | d-post1→d-post2 | 4.3899/127 |
| d-post2→d-post3 | 5.6765/128 | d-post3→d-post4 | 10.3266/125 |
| d-post4→d-post5 | 9.3505/104 | d-post5→d-post6 | 10.3419/134 |
| d-post6→d-post7 | 7.8717/125 | d-post7→d-post8 | 5.8318/99 |
| d-post8→d-post9 | 8.6629/136 | d-post9→d-post10 | 7.8104/100 |

Dense whole-hop range 4.39–15.94 (T42: 5.07–18.39 — same motion class,
wider); hold hop 15.9403/154 (T42: 7.6624/97 — whiteout→wall-tumble =
large whole-frame); d-post1→d-post2 4.3899/127 = smallest dense hop in
T-lane history (rider pinned near-motionless at the wall, 10→5 MPH);
pre-pair 7.6524/123 (T42: 6.2614/84 — crash-spray evolution).

### R1 cross-run identities vs T42 R3 (whole-frame PIL per snap)

| Snap | T43 vs T42 | Snap | T43 vs T42 |
|---|---|---|---|
| start | 13.4188/151 | a1-now | 5.7417/102 |
| a1-poll01 | 0.0308/0 | a1-pre | 0.0308/0 |
| a1-post3 | 0.0327/0 | a1-post8 | 0.0435/0 |
| a1-post15 | 0.0006/0 | a1-post25 | 0.0200/0 |
| menupre | 0.0332/0 | mc-post1 | 0.3326/8 |
| mc-post3 | 0.1892/4 | mc-post8 | 0.3177/8 |
| mc-post15 | 0.1687/4 | scpre | 0.2534/6 |
| zc-post1 | 0.0937/1 | zc-post3 | 0.3165/8 |
| zc-post8 | 0.1912/5 | ccpre | 0.2193/6 |
| sp-post1 | 0.0507/0 | sp-post3 | 0.0265/0 |
| sp-post8 | 0.0228/0 | sppre | 0.0284/0 |
| pc-post1 | 0.0871/0 | pc-post3 | 0.0320/0 |
| pc-post8 | 0.0413/0 | smpre | 0.0383/0 |
| rc-post1 | 0.0373/0 | rc-post3 | 0.0248/0 |
| rc-post8 | 0.0366/0 | sepre | 0.0461/0 |
| sj-post1 | 0.1423/2 | sj-post3 | 0.1290/1 |
| sj-post8 | 0.1423/1 | mrpre | 0.1283/1 |
| mr-post1 | 1.9921/71 | mr-post3 | 2.0187/73 |
| mr-post8 | 7.6391/130 | mr-post15 | 0.8590/22 |
| mr-post25 | 0.8102/20 | mr-post40 | 0.5610/8 |
| mr-stab1 | 0.6050/10 | mr-stab2 | 0.5836/9 |
| pppre | 0.6835/14 | x-post1 | 1.7207/56 |
| x-post3 | 3.3046/60 | x-post8 | 5.1156/92 |
| x-post15 | 5.2180/105 | x-post25 | 10.5968/166 |
| x-post40 | 11.2741/124 | npre1 | 11.5477/124 |
| npre2 | 10.6671/117 | d-post1 | 10.9382/93 |
| d-post2 | 12.6678/134 | d-post3 | 15.6326/137 |
| d-post4 | 11.5182/120 | d-post5 | 9.9758/134 |
| d-post6 | 8.4306/132 | d-post7 | 10.3684/126 |
| d-post8 | 9.2327/117 | d-post9 | 13.4594/179 |
| d-post10 | 10.4662/161 | — | — |

Menus reproduce T42 near-pixel-identical through sepre (≤0.33);
loading/panel/countdown jitter 0.4–7.6 (rival lineup + % jitter +
cinematic-vs-panel timing at mr-post8); gameplay diverges 3–16 (AI/RNG
lottery — the T-lane pattern). a1-poll01 0.0308/0 = T42's exact xrun
value (title determinism).

### R1 HUD table (viewed; score 0 through x-post25, 1390 from x-post40 on — one trick landed mid-race)

| Snap | Pos | Clock | Prog | Speed | Snap | Pos | Clock | Prog | Speed |
|---|---|---|---|---|---|---|---|---|---|
| x-post1 | gate | 00:00:00 | 0% | 0 MPH | x-post3 | 5TH/6 | 00:00:02 | 1% | 38 MPH |
| x-post8 | 3RD/6 | 00:00:10 | 5% | 50 MPH | x-post15 | 3RD/6 | 00:00:23 | 11% | 50 MPH |
| x-post25 | 1ST/6 | 00:00:38 | 20% | 58 MPH | x-post40 | 1ST/6 | 00:01:01 | 32% | 62 MPH |
| npre1 | 1ST/6 | 00:01:27 | 43% | 29 MPH | npre2 | 1ST/6 | 00:01:27 | 44% | 16 MPH |
| d-post1 | 1ST/6 | 00:01:30 | 45% | 10 MPH | d-post2 | 2ND/6 | 00:01:30 | 45% | 5 MPH |
| d-post3 | 2ND/6 | 00:01:31 | 45% | 17 MPH | d-post4 | 2ND/6 | 00:01:32 | 45% | 30 MPH |
| d-post5 | 2ND/6 | 00:01:33 | 46% | 40 MPH | d-post6 | 2ND/6 | 00:01:34 | 46% | 44 MPH |
| d-post7 | 2ND/6 | 00:01:35 | 47% | 44 MPH | d-post8 | 2ND/6 | 00:01:35 | 47% | 44 MPH |
| d-post9 | 2ND/6 | 00:01:36 | 47% | 47 MPH | d-post10 | 2ND/6 | 00:01:37 | 47% | 49 MPH |

Progress monotonic 0→47%; ONE position decay in the dense window
(1ST→2ND between d-post1 and d-post2, wall-pin-driven); speed collapses
29→16→10→5 MPH across npre1→d-post2 (tree crash → whiteout → wall
tumble → wall pin) then rebuilds 17→30→40→44→44→44→47→49 MPH.

### R1 dense exposures (poll-log ns SNAPSTART stamps; cadence check)

| Gap | Exposure | Gap | Exposure |
|---|---|---|---|
| npre1→npre2 (pre-pair, no input) | 0.5818 s | npre2→d-post1 (hold span) | 1.6214 s |
| d-post1→d-post2 | 0.5744 s | d-post2→d-post3 | 0.5765 s |
| d-post3→d-post4 | 0.5791 s | d-post4→d-post5 | 0.5787 s |
| d-post5→d-post6 | 0.5773 s | d-post6→d-post7 | 0.5817 s |
| d-post7→d-post8 | 0.5766 s | d-post8→d-post9 | 0.5719 s |
| d-post9→d-post10 | 0.5827 s | npre1→d-post10 span | 7.4022 s wall / +10 s race (1.35×; integer-second quantization [1.22,1.49] overlaps T42's [1.36,1.63]) |

10× ≈0.578 s (T42: 10× ≈0.575 s) — SAME cadence ✓. Hold span 1.6214 s =
0.5 sleep + 1037.2 ms hold + 0.5 sleep + snap overheads.

### R1 phase-match verdict (vs §T43-0 targets — match phase not seed)

| Item | Target | R1 observed | Match |
|---|---|---|---|
| Hold slot | ≈T+502.5 (same script slot) | T+509.34 (keydown) | yes — same script slot; wall +6.8 s (phases ran long) |
| Pre-pair clocks | ≈00:01:2x–3x | 00:01:27 / 00:01:27 | yes |
| Pre-pair positions | racing pack | 1ST/1ST/6 | yes (lottery — front, vs T42's back) |
| Pre-pair progress | ≈36–37% ±5 pp (31–42%) | 43% / 44% | 1–2 pp over band edge (T42 precedent: proceeded 4 pp under edge; slot/clock/pack match — NO re-attempt) |
| Series span | ≈+7.4 s wall | +7.40 s wall | yes |

## T43-4. R1 tracking (ALL THREE trackers on all 12 dense snaps) + lock QA

### R1 RDC table (frozen + ROI + gradient; SCPS 22/22 bit-identical 3-way, `cmp` clean)

| Snap | Frozen cx/cy/npix | F-gate | ROI cx/cy/npix | R-gate | Grad cx/cy/npix | G-gate |
|---|---|---|---|---|---|---|
| npre1 | 305.7/188.7, 23891 | INVALID | 355.8/239.7, 7672 | INVALID | 348.9/264.2, 1226 | VALID |
| npre2 | 302.8/165.8, 14443 | INVALID | 378.7/231.8, 6 | INVALID | 372.4/229.6, 5 | INVALID |
| d-post1 | 406.6/252.3, 88831 | INVALID | 341.8/256.1, 25807 | INVALID | 300.5/256.0, 2909 | VALID |
| d-post2 | 429.7/277.9, 76158 | INVALID | 360.9/278.2, 19781 | INVALID | 312.2/309.6, 2593 | VALID |
| d-post3 | 377.8/250.3, 105774 | INVALID | 325.4/265.4, 32932 | INVALID | 298.1/321.1, 2293 | VALID |
| d-post4 | 377.3/313.8, 8943 | INVALID | 359.6/302.3, 4410 | VALID | 335.0/277.9, 1379 | VALID |
| d-post5 | 302.3/212.4, 3169 | VALID | 326.7/271.4, 1751 | VALID | 327.7/273.4, 1231 | VALID |
| d-post6 | 345.2/180.5, 9420 | INVALID | 329.5/258.7, 3322 | VALID | 329.3/260.6, 1914 | VALID |
| d-post7 | 336.0/173.0, 16683 | INVALID | 356.4/237.7, 4209 | VALID | 352.3/244.8, 2384 | VALID |
| d-post8 | 382.6/169.3, 19603 | INVALID | 366.1/257.2, 2534 | VALID | 360.7/262.3, 1556 | VALID |
| d-post9 | 212.0/210.5, 5104 | VALID | 335.8/297.2, 1322 | VALID | 335.0/296.8, 921 | VALID |
| d-post10 | 267.6/230.3, 2410 | VALID | 331.3/290.2, 1329 | VALID | 330.3/289.1, 940 | VALID |

| Hop | SCPS40 (all three tools) | SCPS120 (all three tools) |
|---|---|---|
| npre1→npre2 (pre-pair) | −12 @ −0.35 (off-rail, no match) | −120 @ 0.11 RAIL |
| npre2→d-post1 (HOLD) | −40 @ −0.75 RAIL | −120 @ −0.05 RAIL |
| d-post1→d-post2 | −12 @ 0.96 | −12 @ 0.96 |
| d-post2→d-post3 | +29 @ 0.84 | +29 @ 0.84 |
| d-post3→d-post4 | −15 @ 0.73 | −15 @ 0.73 |
| d-post4→d-post5 | +40 @ −0.26 RAIL | +120 @ −0.02 RAIL |
| d-post5→d-post6 | −36 @ 0.73 | −36 @ 0.73 |
| d-post6→d-post7 | +29 @ −0.01 (off-rail, no match) | +29 @ −0.01 (off-rail, no match) |
| d-post7→d-post8 | +40 @ 0.74 RAIL | +40 @ 0.74 |
| d-post8→d-post9 | −18 @ 0.97 | −18 @ 0.97 |
| d-post9→d-post10 | +40 @ −0.15 RAIL | +120 @ 0.35 RAIL |

### R1 rail-rate comparison vs T42 (per tracker)

| Metric | T42 R3 (1036.5 ms hold) | T43 R1 (1037.2 ms hold) |
|---|---|---|
| RDC frozen gate-out | 11/12 (npre2 singleton) | 9/12 (d-post5/9/10 VALID) |
| RDC ROI gate-out | 3/12 (d2/d3/d10 floods) | 5/12 (npre1 flood, npre2 empty, d1/d2/d3 wall floods) |
| RDC gradient gate-out | 1/12 (d2, Task-1 calib) | 1/12 (npre2 empty) |
| Gated pair straddling hold | YES (ROI npre2→d-post1) | NO — npre2 ~empty under ALL THREE (6/5 px whiteout) |
| SCPS40 rails | 4/11 (hold +13 @ 0.23 off-rail weak) | 4/11 (hold −40 @ −0.75 RAILED) — count repeats, hold differs |
| SCPS120 strict rails | 2/11 (hold +120 @ 0.60 + d9d10) | 4/11 (pre + hold + d4d5 + d9d10, all ≤0.35 corr) |
| Dense whole-hop range | 5.07–18.39 | 4.39–15.94 — same motion class, wider |

### R1 lock QA (every VALID pair graded; marked-crop montage method, `/tmp` scratch)

ROI grades: npre1 off-rider INVALID (trunk + crash debris flood, gated);
npre2 empty INVALID (whiteout, gated); d1/d2/d3 wall-flood INVALID
(gated); d4 borderline-on (board/shadow pulls down-right); d5 ON; d6 ON
(head); d7 OFF ~35 px up-right (dark tree/arch mass — in-band bias,
T42-d9 class); d8 borderline-on (~25 px right of head, tree-edge);
d9 ON; d10 ON.

Gradient grades: npre1 borderline-on-DEBRIS (board wreckage + trunk
edge — crash-contaminated regardless); npre2 empty INVALID (gated);
d1 ON-tumbling-rider (smooth wall drops out, rider edges dominate);
d2 ON-pinned-rider; d3 ON-recovering-rider; d4 ON (shadow pull FIXED vs
ROI); d5/d6 ON; d7 OFF ~30 px (tree/arch EDGES survive — textured
intruder, Task-1 verdict confirmed on new data); d8 borderline-on; d9/d10 ON.

| Pair | ROI Δcx/Δcy | ROI lock QA | Grad Δcx/Δcy | Grad lock QA |
|---|---|---|---|---|
| npre1→npre2 (no-input) | — (both INVALID) | ungated (crash + whiteout) | — (npre2 INVALID) | ungated (whiteout) |
| npre2→d-post1 (HOLD) | — (both INVALID) | UNGATED under all three | — (npre2 INVALID) | UNGATED under all three |
| d-post1→d-post2 | — (both INVALID) | wall floods gated | +11.7 / +53.6 | tumbling→pinned (crash-sequence, not clean motion) |
| d-post2→d-post3 | — (both INVALID) | wall floods gated | −14.1 / +11.5 | pinned→recovering (crash-sequence) |
| d-post3→d-post4 | — (d3 INVALID) | wall flood gated | +36.9 / −43.2 | recovering→racing (crash-dynamics-adjacent) |
| d-post4→d-post5 | −32.9 / −30.9 | borderline→on | −7.3 / −4.5 | on→on |
| d-post5→d-post6 | +2.8 / −12.7 | on→on | +1.6 / −12.8 | on→on |
| d-post6→d-post7 | +26.9 / −21.0 | on→off — BIAS-CONTAMINATED | +23.0 / −15.8 | on→off — BIAS-CONTAMINATED |
| d-post7→d-post8 | +9.7 / +19.5 | off→borderline — BIAS-CONTAMINATED | +8.4 / +17.5 | off→borderline — BIAS-CONTAMINATED |
| d-post8→d-post9 | −30.3 / +40.0 | borderline→on | −25.7 / +34.5 | borderline→on |
| d-post9→d-post10 | −4.5 / −7.0 | on→on | −4.7 / −7.7 | on→on |

Cross-tracker agreement on R1: both trackers' VALID set on d4–d10 is
identical (7/7); both flag d7 off-rider (same tree intruder — the
textured class gradient cannot fix); both yield on→on d5d6 + d9d10 with
Δcx agreeing to ≤1.2 px (+2.8/+1.6, −4.5/−4.7) and Δcy to ≤0.7 px.
Gradient additionally locks the crash sequence (d1–d3 VALID on-rider —
rider edges vs smooth wall) where ROI correctly flood-gates: the
Task-1 gate-hole verdict inverts by scene class (smooth wall HERE lets
the rider dominate; textured bark THERE dominates instead).

## T43-5. Distribution verdict + recipe (the STOP deliverable)

Crash table (the brief's crash-again clause — tabled, no third run):

| Item | T42 R3 | T43 R1 |
|---|---|---|
| Crash site | tree in hold hop (d-post1) | tree AT npre1 (pre-pair) + wall d-post1–d-post3 |
| Speeds | 51→7 MPH (npre2→d-post1) | 29→16→10→5 MPH (npre1→npre2→d-post1→d-post2) |
| Positions | 5TH→6TH decay in hold hop | 1ST→2ND decay d-post1→d-post2 |
| HUD markers | 7 MPH, 37%, 00:01:31 | RECOVER meter (npre1), whiteout (npre2), 5 MPH wall pin (d-post2) |
| Hold pair gated? | YES (on→borderline, crash inside) | NO (npre2 ~empty under all three) |
| Pre-pair clean? | YES (on→on floor sample) | NO (tree crash + whiteout) |

Accumulation counts (on→on VALID pairs only; crash-sequence and
bias-contaminated pairs excluded):

| Distribution | Tracker | T42 | + T43 R1 | Total |
|---|---|---|---|---|
| No-input (clean cruise + pre-pair) | ROI | 1 (npre1npre2 −0.7/−22.2) | 2 (d5d6 +2.8/−12.7, d9d10 −4.5/−7.0) | 3 |
| No-input (clean cruise + pre-pair) | Gradient | 4 (npre1npre2 +1.8/+4.8, d5d6 +0.0/+10.6, d6d7 +2.7/−3.9, d7d8 −2.1/−4.2) | 3 (d4d5 −7.3/−4.5, d5d6 +1.6/−12.8, d9d10 −4.7/−7.7) | 7 |
| Hold-step | ROI | 1 (npre2d-post1 +11.2/−39.5, crash inside) | 0 (hold ungated) | 1, crash-confounded |
| Hold-step | Gradient | 1 (npre2d-post1 −4.4/−24.1, crash inside) | 0 (hold ungated) | 1, crash-confounded |

Distribution verdict: DOESN'T SEPARATE — cannot: the hold-step side
stands at n=1 crash-confounded sample under both trackers (no clean
hold sample exists in either run), and R1 adds ZERO hold samples plus
ZERO clean no-input pre-pair samples (the crash lottery took the whole
hold window). Cruise accumulation works exactly as designed (ROI 1→3,
gradient 4→7 on→on, cross-tracker Δ agreement ≤1.2 px) — the no-input
side grows, the hold side is empty. Per the brief: STOP the motion
verdict at one more data point (this crash) — needs more samples, with
the counts above.

Recipe (the STOP deliverable):

1. ACCUMULATION: WORKS where the track reads clean — 5 new on→on pairs
   (2 ROI + 3 gradient, d4–d10 cruise) with cross-tracker agreement;
   lock-QA keeps carrying its weight (d7 tree intruder flagged under
   BOTH trackers, contaminated pairs excluded, never motion).
2. HOLD: NOT solved — crash lottery is 2/2 at this phase (T42's back-of-
   pack tree crash, R1's front-of-pack tree+wall crash): the hold window
   itself is crash-prone, and a crashed hold yields no hold-step sample
   under ANY tracker (R1: npre2 ~empty = total whiteout gate-out).
3. NEXT (one variant): keep the SAME shape and accumulate runs until a
   crash-free hold lands (lottery tolerance, not a retry condition — each
   crashed run still banks cruise pairs + a crash datapoint); or steer
   the phase (earlier/later window, or a leader-gap filter) — but that
   changes the phase-match contract, so table it as a new variant. Do
   NOT tighten gates to manufacture hold pairs (npre2's 5 px is not a
   lock under any honest band).
4. TRACKERS (carried): ROI gate remains the flood defense (5/5 R1 floods
   correctly gated, incl. the whiteout-empty case); gradient adds
   centroid quality + crash-sequence locks (d1–d3 on-rider VALIDs), with
   the textured-intruder hole confirmed on new data (d7 tree). Score
   both in parallel; lock-QA every VALID pair.
5. ENVIRONMENT (carried): WSLg audio healthy first-boot this session —
   keep the BEHAVIORAL gate (modal census, never socket-presence);
   activity holds VMs (zero turnover H51); parallel-launch protocol =
   run-background → sleep 35 → v2a → verify log → conditional v2b;
   watch C: (11→7.6 G this run ≈ 3.4 GB drain — the ~5 GB gate has
   ~1 run of headroom left at this drain rate; future lanes: rotate
   traces/PPMs off C: or free space BEFORE the run).

## T43-6. R1 census + trace + forensics

| Item | Value |
|---|---|
| Census | `t43r1-census.txt` (lines=43623520, ts_span=0.1213..515.9212; T42 R3: 42967628/0.1271..508.62 — same class, +1.5% lines for the +7 s longer run) |
| EE | 12201871 calls, distinct=52 (top: GetThreadId 5080483, WaitSema 2205292, SignalSema 1955538, sceSifGetReg 1260327) |
| IOP | 19119797 calls, distinct=155 (top: sceSdGetAddr 3797952, QueryIntrContext 3464616, CpuSuspendIntr 3238354, CpuResumeIntr 2191953) |
| libsd (G5 positive) | set incl. sceSdInit 1 + sceSdGetParam 15700 (T42: 15879 — audio initialized) |
| MARK | ERROR NONE (only benign: cdvdRead06(Error) [4.7557] + patches.zip warning; first: BIOS Found [0.1217], cdvdLoadElf SLUS_207.72 [0.1278]) |
| cubeb (G5 positive) | "Creating Cubeb audio stream" [0.4596] + pulse negotiation [0.4689/0.4709] + init/started successful; ZERO null-fallback/CUBEB_ERROR lines in 2.79 GB (the only `null` matches are benign `(null)` RFU BIOS-call names); tail: stream stopped/destroyed successfully + "NVRAM has not changed" |
| Vblank stream | first `WaitVblankStart` L417043 [1.0799] (T42: L417043 [1.2023] — same line); 397 total, ALL ≤90 (LE90/110/140/350 all 397 — IDENTICAL to T42/T41) |
| Vcount | vcount logic on the SSD copy (path operand swapped; program byte-identical logic) |
| Live trace | `emulog.txt` 2789610604 B sha `b8a27b83…e82e03` (T42 R3's preserved via `emulog-pre-t43-20260921T194932Z.txt`) |
| SSD stream | `COPYFILE_DISABLE=1`, declared cap 4 GB (used 2.79 GB, 1.43× headroom); `/Volumes/Extreme SSD/ps2x-t4/emulog-t43r1.txt` size+sha MATCH (2789610604 B, `b8a27b83…e82e03`); head/tail 30-line slices committed (`t43r1-emulog-head/tail.txt`) |
| Boot logs | `t43r1-boot.log` (4231 B, R1 content — differs from T42's at char 10) + `t43r1-boot.stdout` (210 B, byte-identical to T42's — deterministic DRI3+CTRL+C text); fetched from the overwritten on-box paths (§T43-1b) |
| NVM post-run | `da021d2a3d4b4e43…` first-16 match — UNCHANGED |
| C: post-session | 7.6 G avail (11→7.6 G ≈ 3.4 GB drain: 2.79 GB trace + 61 PPMs/JPGs; gate still passes — ~1 run headroom left) |

Forensics (observed events, tables only — no verdicts): tree crash at
npre1 (1ST/43%, RECOVER meter, 29 MPH) → snow-spray whiteout at npre2
(16 MPH, rider obscured, ROI/gradient ~5 px) → wall tumble d-post1 (10
MPH) → wall pin d-post2 (2ND/5 MPH, 1ST→2ND decay, smallest dense whole
hop in T-lane history 4.3899/127) → push-off d-post3 (17 MPH) → racing
d-post4 (30 MPH under bridge); x-post8 rival wipeout (right foreground);
x-post25→x-post40 trick (score 0→1390); v2a main-window dismissal @T+61.9
(inert, R3 pattern) + ~T+85 window census (game-only, no modal); d7 tree
intruder (in-band off-rider under BOTH trackers, §T43-4); sppre
re-captured (NOT a cp — scores differ from sp-post3); mr-post8 cinematic
frame (EA Radio, vs T42's rider panel — timing jitter).

## T43-7. Exact commands (reproduce-from-scratch)

Pre-run pins (one `wsl` call per ssh; single-quote outer, double-quote
inner — the remote shell is PowerShell: bare `;`/`|` break):
`ssh bytesize 'wsl bash -c "…"'` for btime/uptime (boot), `sha256sum` +
`stat` (binary), `git rev-parse HEAD` + `status --short` (tree),
`ls -la inputs/`, `sha256sum` + `stat` (live NVM), `grep -n Cross/Left`
(bindings), 9-ref `sha256sum`, T42 snap `ls` (spot size), live-trace
`ls`, `df -h /` + `/mnt/c`, `ls PulseServer` (informational only),
dmesg (`wsl dmesg` → local), eventlog (`wevtutil qe System /c:120
/rd:true /f:text` → local).
X11: `wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs
/tmp/.X11-unix`. PPM: `wsl python3 t43-cropdiff.py t35-ref-panel.ppm
t35-ref-panel.ppm` → `mean=0.0000 p99=0`.
Staging: `scp … bytesize:C:/Users/bradr/pcsx2-t4/` →
`wsl cp /mnt/c/… /home/brad/pcsx2-t4/` → `wsl sha256sum` (match) →
`wsl rm` C: files.
Run: `ssh bytesize 'wsl bash -c "cd /home/brad/pcsx2-t4 && stdbuf -oL
-eL ./t43-auto.sh"'` (local redirect, short yield → background) → local
`sleep 35` → `wsl t43-dialogwatch2.sh` (local redirect) → window census
(`xdotool search --onlyvisible --name SSX/Error`).
Fetch: `wsl cp` snaps → C: → `scp` (rename `t43-*.jpg` → `t43r1-*.jpg`,
61/61 + poll log) → `wsl rm`. Analyze: `wsl t43-analyze.sh`
(census/samples). Boot logs: `wsl cp logs/boot-t42.log/.stdout` → C: →
`scp` (R1 content at T42-named paths — rename miss, §T43-1b).
Trace: `COPYFILE_DISABLE=1 ssh … 'wsl bash -c "cat
…/emulog.txt"' > /Volumes/Extreme SSD/ps2x-t4/emulog-t43r1.txt` (cap
4 GB) → size+sha+head/tail verify. Refs: `wsl cp` 9 PPMs → C: → `scp`
→ `/tmp/t43refs` (shas match pins) → `wsl rm`.
Post-hoc (local): `t41-track.py` + `t42-track.py` + `t43-track.py`
(dense 12), `/tmp/t43-batch.py` (panels/hops/xrun; bit-exact 4/4 vs
committed + reproduces 3/3 published T42 hops), marked-crop montages
(`/tmp`, T42's method: gated pixels tinted + centroid crosshair, ROI +
gradient variants), vcount awk on SSD copy, `grep` cubeb/Vblank/MARK on
SSD copy.

Gaps (tabled, none load-bearing): H51 teardown time unrecorded (evidence
complete before any turnover; final eventlog read pre-teardown);
interpolated T+ on non-scored chain snaps (±1 s; scored anchors exact;
ns-exact on hold + dense); stdout 460 vs T42's 514 lines (unexplained
54-line delta, stderr identical 2551 — forensic note); the T42 R3
frozen-exact + middle-SCPS reproduction gap (§T43-1a — stale cells,
corrected record tabled); hold-step distribution still n=1
crash-confounded (the brief's stop condition, not a gap); no-input floor
still n=1 clean pre-pair (R1's pre-pair crashed); d7 textured intruder
under both trackers (quantified, excluded via lock-QA).

## T43-8. Tail receipt (truncated tail FAILS the gate)

T43 executed: Task 1 = gradient static test (ONE new file `t43-track.py`:
Sobel AND-gate GRAD_MIN=60 + band 500–3000, sha `2e532a2d…`, SCPS 3-way
bit-identical; reproduction gate tabled — retuned 12/12 + T41 34/34
exact, T42-R3 frozen-exact + middle-SCPS gap found and corrected;
calibration 11/12 VALID with d5 off→on + d9 50px→15px + d3 trunk gate
hole; held-out 12/12 consistent both ways; verdict: smooth intruders
separate, textured floods don't — ROI gate stays load-bearing); Task 2 =
SAME-shape accumulation run (T4 build reuse on all pins; chain to LIVE
1ST/6 + ONE 1037.2 ms Left hold @T+509.34 + 10-snap blind series at
10×≈0.578 s, R1 first attempt, exit 0); the hold window crashed AGAIN
(tree→whiteout→wall, 29→5 MPH, 1ST→2ND — tabled, no third run per the
brief); all three trackers scored all 12 dense snaps (frozen 9/12 out,
ROI 5/12 out, gradient 1/12 out; SCPS40 4/11, SCPS120 4/11 strict);
lock-QA per VALID pair (d7 tree flagged under both; crash-sequence
pairs separated); distribution verdict = DOESN'T SEPARATE (hold-step
n=1 crash-confounded, no-input ROI 1→3 / gradient 4→7 on→on — cruise
accumulates, hold side empty); full chain/hops/HUD/xrun tables in T42's
shapes; trace streamed + verified (2789610604 B, sha MATCH); recipe =
accumulate runs at the same shape (lottery tolerance) or table a phase
steer as a new variant. Evidence: `local/research/T43/` (STANDALONE: 6
scripts + REPORT + 61 R1 snaps + logs + census + slices + dmesg/eventlog
×sets). Commit `[T43]` with trailer `Orchestrated-By: Muse Code`, no
push. END-OF-REPORT.

