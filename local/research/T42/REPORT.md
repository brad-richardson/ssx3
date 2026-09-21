# T42 report — ROI retune for forest/wall scenes at the same `sleep 0.5` cadence (bytesize, no lease)

Brief: T42 (T40-G1 second arm, T41 §G1/G2 recipe: ROI/gate retune,
NOT a further cadence change). Tables, no verdicts. Time box 4 h.

Stale-reading guard: `local/research/T41/REPORT.md` (all of it: R1/R2
environment NO-PARKs (WSLg-audio-down cubeb modal on every snap);
R3 game-side NO-SP-PARK (SP→SM advance, zero input in-window); R4
reproduced the chain to LIVE gameplay + ONE 1038.4 ms Left hold @T+503.19
on live 2ND/6 + 10-snap blind series at 10×≈0.57 s; at ≈0.57 s exposures
SCPS40 leaves the hold hop off-rail but uncorrelated (+29 @ 0.02),
SCPS120 loses T40's clean resolve (+119 @ 0.37 weak), and RDC floods
11/12 on forest/arch-shade/wall scenes with only a d-post5 singleton
VALID — no gated pair straddles the hold). Also `local/research/T40/
REPORT.md` (the G1 proposal: sub-second cadence OR ROI/gate retune,
never both — T41 took the cadence arm, this brief takes the ROI arm).
This brief executes T41 §G1/G2's recipe ONLY: ONE tracking variant at
the SAME cadence. T41's scripts reused (copied, not modified).

Experiment contract (up front): hypothesis — T41's ≈0.57 s exposures
flood RDC 11/12 because the rider ROI (x[150,540] y[100,460]) catches
forest trunks / arch shade / barrier tops / walls, so shrinking the ROI
to x[220,420] y[180,360] (26% area, same dark threshold 80, same gate
200–6000) excludes the flood sources while keeping the rider complex,
and a gated RDC pair can straddle the hold at the SAME `sleep 0.5`
cadence with the SAME ≈1038 ms hold; observable — pre-hold pair = live
race at a matched phase (race clock + position/progress HUD read off the
viewed snaps), the hold row (proven 1 s keydown→keyup + phase match vs
T41's hold), blind 10-snap series + per-snap HUD + tracking metrics from
BOTH trackers + per-hop whole diffs, all scored post-hoc from fetched
snaps; screen content read off viewed snaps; alternatives — retuned RDC
still floods (→ table the exact flooded rate + noise floors and STOP
with a recipe), run provably never reached live gameplay at a matched
phase (→ ONE bounded re-attempt allowed); stop — table the rail-rate
comparison vs T41 per tracker + gated-pair verdicts + recipe, one input
variant per attempt (the hold is FIXED), one tracking variant per
attempt (the retune is FIXED once tabled), never blind multi-presses.

## T42-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T42; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T42]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; disk
pins taken on VM-H40, VM-independent across turnover):

| Item | T4 value | T42 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 (`dat/PCSX2/bios/ps2-bios-0200a-20040614-100909.nvm`) | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Pad binding (Left) | — | `Left = Keyboard/Left`, `PCSX2.ini:576` (the hold key; re-verified) | yes |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…580eb6` reproduces T35 | yes |
| T41 reference snaps present | — | 4/4 spot-check sizes reproduce T41 §chain (`npre1/2` 58926/62190, `d-post1/10` 58794/57916) | yes |
| Free space | — | WSL `/` 859 G pre; C: 18 G pre (GATE ~5 GB+ PASSES — no wedge risk); laptop `/` 13 Gi avail; SSD 222 Gi free | yes |
| Live trace pre-run | — | `emulog.txt` 2745300674 B sha `5b0a7349…53d3f` = T41 R4 (preserved at R1 boot) | yes |
| WSLg audio pre-run | — | DOWN on every pre-run VM (H40-era, H42, H43 — no `/mnt/wslg/PulseServer`, no `runtime-dir/pulse/`; host 6 OK sound devices → WSLg defect, T41 R1/R2 signature); run boots ONLY on an audio-healthy VM (table the pre-run audio state per the T41 lesson) | gate |

Phase-match targets (tabled BEFORE the run — T41 R4's hold window, match
PHASE not seed; AI lineup/RNG differ run to run):

| Item | T41 hold-window value | T42 hold-window target |
|---|---|---|
| Hold slot | T+503.19 (keydown) | ≈T+503 (same script slot) |
| Pre-pair race clocks | 00:01:29 / 00:01:29 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | 2ND/6 / 2ND/6 | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 45% / 46% | ≈45% ±5 pp |
| Series span | 10 snaps over +6.8 s wall / +11 s race | 10 snaps over ≈+7 s wall (same `sleep 0.5` blind capture) |

Same-cadence record (tabled BEFORE the run — the deliberate NON-change):

| Item | T41 (`sleep 0.5`) | T42 (`sleep 0.5`) |
|---|---|---|
| Dense-phase shape | `sleep 0.5` + capture only; ns wall stamps per snap; ZERO scoring calls | identical (script rename + comment-only diff, verified) |
| Pre-pair gap | `sleep 0.5`, no scoring (measured 0.571 s) | identical call |
| Hold | ONE `press_hold Left` (1 s `sleep`, T38's body) | identical call, same slot |
| Post-hold | 10 × (`sleep 0.5`, `bsnap d-postN`) | identical calls |
| Dense span (npre1→d-post10) | 7.326 s wall | ≈7.3 s wall expected |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log | scp via C: staging (T25 recipe) | `t42r1-*.jpg`, `t42r1-poll.log` |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t42-cropdiff.py`, bit-exact validated 4/4 (T39/T40/T41 protocol); committed tool reproduces any score | screen chain table + xrun frame identities vs T41 R4 |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking, CONTROL | committed `t41-track.py` (frozen, byte-identical — scores every snap in parallel as the control) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. Dense 12-snap tracking, RETUNED | committed `t42-track.py` (the ONE variant) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags (SCPS code untouched — expect bit-identical to control) |
| 6. View all snaps | local reads | HUD per snap (clock/position/progress/speed/score) |
| 7. Rail-rate comparison | — | RDC gate-out / SCPS40 / SCPS120 rates vs T41 per tracker + gated-pair verdicts |

Rates to beat / question (tabled BEFORE the run — T41 R4 hold dense
phase, 12 snaps / 11 hops at ≈0.57 s):

| Metric | T41 (1038.4 ms hold, ≈0.57 s gaps) | T42 question |
|---|---|---|
| RDC gated out (frozen) | 11/12 (d-post5 singleton VALID) | does the retune gate fewer? |
| Gated pair straddling hold | NO (singleton) | does any VALID pair straddle the hold now? |
| SCPS40 rails | 4/11 (hold hop +29 @ 0.02 off-rail, no match) | repeats? (unchanged tools) |
| SCPS120 rails | 1/11 (hold hop +119 @ 0.37 weak) | repeats? (unchanged tools) |
| Dense whole-hop range | 6.36–17.47 | motion-class floor at ≈0.57 s? |

## T42-1. The ONE retune (tabled BEFORE the run) + calibration

Retune choice (exactly one — smaller ROI; threshold/gradient rejected
with data):

| Candidate | Test on T41's 12 static dense snaps | Outcome |
|---|---|---|
| Higher dark threshold (80→40/30) | th40 locks TREES not rider (d-post4 → (481,147) on-tree; npre1 → (170,198) compact off-rider); th30 locks HUD text (d-post10 → (310,448) RECOVER meter) and kills signal (≤68 px on 5/12 snaps) | REJECTED |
| Smaller ROI (same threshold 80, same gate) | x[220,420] y[180,360]: 11/11 non-wall VALID (1138–3926), wall correctly INVALID (12609); gate band untouched | CHOSEN |
| Gradient-based rider lock | Unneeded complexity — the ROI separates; extra knobs = tuning/overfit risk against a 12-snap set | REJECTED |

The variant (frozen in committed `t42-track.py` — a COPY of
`t41-track.py`; the frozen control stays byte-identical):

| Constant | Frozen (`t41-track.py`) | Retuned (`t42-track.py`) |
|---|---|---|
| `RIDER_ROI` | x[150,540] y[100,460] (140400 px) | x[220,420] y[180,360] (36000 px, 26%) |
| `DARK_MAX` | 80 | 80 (frozen) |
| Gate | 200 ≤ npix ≤ 6000 | 200 ≤ npix ≤ 6000 (frozen — calibration separates without touching it) |
| `SNOW_ROWS`/`SNOW_COLS` | y[380,460] x[150,540] | identical (SCPS untouched — expect bit-identical lags) |
| Lags | ±40 / ±120 | identical |

Reproduction gate (frozen control on T41's committed dense snaps FIRST):

| Check | Result |
|---|---|
| `t41-track.py` on T41 R4 12 dense snaps vs T41 §hold table | 12/12 RDC (cx/cy/npix/gate) + 11/11 SCPS40 + 11/11 SCPS120 reproduce EXACTLY (corr to 4 dp) |
| `t42-track.py` SCPS vs `t41-track.py` SCPS, same snaps | 22/22 lines bit-identical (`cmp` clean — SCPS code untouched) |
| `t41-track.py`/`t40-track.py` byte-identical | untouched (tracked tree clean; T42 adds new files only) |

Retune calibration table (committed `t42-track.py` on T41 R4's 12 dense
snaps — STATIC separation before any run; centroid quality judged on
marked ROI crops: dark pixels tinted, centroid crosshair — `/tmp`
scratch montages, method tabled here):

| Snap | Retuned npix + gate | Retuned cx/cy | Frozen npix + gate | Centroid sits on | Verdict |
|---|---|---|---|---|---|
| npre1 | 1319 VALID | 308.2 / 280.7 | 20385 INVALID | rider legs/board | on-rider |
| npre2 | 2534 VALID | 335.8 / 249.8 | 9058 INVALID | rider helmet/right edge | borderline-on |
| d-post1 | 3655 VALID | 324.3 / 306.1 | 11848 INVALID | rider torso (carve) | on-rider |
| d-post2 | 3926 VALID | 290.6 / 239.6 | 12083 INVALID | ~25 px above head (tree pulls up) | off-rider, in-band |
| d-post3 | 3158 VALID | 333.2 / 248.4 | 11081 INVALID | ~35 px right of rider (adjacent tree) | off-rider, in-band |
| d-post4 | 1450 VALID | 322.8 / 288.1 | 9615 INVALID | rider lower body, right edge | borderline-on |
| d-post5 | 1138 VALID | 308.4 / 295.3 | 1261 VALID | rider | on-rider |
| d-post6 | 2265 VALID | 289.3 / 242.2 | 9717 INVALID | ~20 px above head (barrier) | off-rider, in-band |
| d-post7 | 2091 VALID | 288.2 / 249.1 | 11670 INVALID | rider head/helmet | borderline-on |
| d-post8 | 1219 VALID | 316.8 / 300.1 | 7540 INVALID | rider | on-rider |
| d-post9 | 3771 VALID | 353.2 / 257.3 | 13757 INVALID | ~50 px right of rider (gate pole) | off-rider, in-band |
| d-post10 | 12609 INVALID | 360.6 / 273.1 | 73670 INVALID | wall fills frame | correctly gated |

Calibration margins: VALID band 1138–3926 vs gate [200,6000] (5.7× min
margin, 1.53× max headroom); wall 12609 = 2.1× over max (gates out).
Centroids on/borderline-on the rider complex 7/11; off-rider but
in-band 4/11 with NAMED causes (d2/d3 adjacent tree, d6 barrier, d9 gate
pole — background geometry adjacent to the rider that no rider-containing
rectangle excludes; biases ≤60 px).

Calibration deltas (tabled — the honesty rows): pre-pair no-input floor
npre1→npre2 = (+27.6, −30.9); hold pair npre2→d-post1 = (−11.5, +56.3).
On T41's own snaps the hold cx step does NOT exceed the no-input floor
(intrusion bias shifts between snaps dominate) — the run tests whether
it does on a new stretch. Gating (the brief's question) separates;
motion-vs-bias disentangling is read off the new run.

Held-out check (T40 R2's 12 dense snaps — reported as-is, ZERO tuning):

| Snap | Retuned npix + gate | Note |
|---|---|---|
| npre1 | 1065 VALID | — |
| npre2 | 6288 INVALID | marginal (5% over max) |
| d-post1 | 25809 INVALID | rock wall at the hold (T40 report) — flood-gates |
| d-post2 | 1310 VALID | — |
| d-post3 | 17894 INVALID | dark cliff/shade fills ROI, rider present-but-unseparated (viewed) |
| d-post4 | 35179 INVALID | heavy shade flood (same class) |
| d-post5 | 1650 VALID | — |
| d-post6 | 5158 VALID | — |
| d-post7 | 3397 VALID | — |
| d-post8 | 5242 VALID | — |
| d-post9 | 1544 VALID | — |
| d-post10 | 1523 VALID | — |

Held-out 8/12 VALID vs frozen 2/12 — generalizes directionally; the
boundary is heavy shade (T40 d3/d4: rider visible but unseparated).
T40's hold pair (npre2→d-post1) stays ungated under BOTH trackers (wall
AT the hold there — nothing gates; the T42 question is about the new run).

Script receipts (frozen BEFORE the run):

| Item | Value |
|---|---|
| `t42-track.py` | copy of T41's + ONE constant (`RIDER_ROI` → x[220,420] y[180,360]) + header note, sha `a951f782…06b00` (3254 B) |
| `t42-cropdiff.py` | byte-identical to T41's (`cmp` clean), sha `ac114212…0826a53` |
| `t42-vcount.sh` | byte-identical to T41's (`cmp` clean), sha `105cd092…39107d76` |
| `t42-analyze.sh` | output-name deltas only (`t42-census/samples`), sha `8f0c5afa…0cc5eb`; `bash -n` clean |
| `t42-auto.sh` | T41 copy + renames + comment updates ONLY (diff vs `t41-auto.sh` is rename + `#`-comment lines, verified), sha `8854af97…b6ccd4`; `bash -n` clean; zero `sham` references; exactly one `press_hold Left` call; dense block contains zero scoring calls (2 `score_` mentions in comments); 11 × `sleep 0.5` intact |
| `t42-dialogwatch2.sh` | byte-identical to T41's v2 (`cmp` clean), sha `d9c7a4c1…41faa` |
| Staged shas | all 5 WSL-staged shas match local (auto `8854af97…`, analyze `8f0c5afa…`, vcount `105cd092…`, cropdiff `ac114212…`, dialogwatch2 `d9c7a4c1…`) |
| PPM self-check | panel ref 0.0000/0 on the run VM pre-run (routine below) |
| T41 originals | untouched (tree clean at commit; T42 dir is new) |

## T42-2. Session log + audio-block forensics + modal probe (all pre-R3)

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC; H-numbers continue T41's H39):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 17:28:37 ([0] VM-H40) | H40 create (pre-existing at session start) | eventlog-pre (teardown 13:31:43) + btime 1790011717 |
| 2 | 17:29–17:31 | Pins on H40 (binary/tree/inputs/NVM/bindings/9 refs/T41 snaps/logs/live trace/C:/audio-DOWN) | §T42-0 table |
| 3 | 17:31:43 | H40 teardown (NOT by me) | eventlog-pre (IDs 71/69/233/234/234) |
| 4 | 17:31:56–17:35:11 | H41 (lived 3.5 min; never directly observed; mid-prep ssh served transparently) | eventlog-pre (create + teardown pairs) |
| 5 | 17:37:22 ([0] VM-H42) | H42 create | eventlog-pre + btime 1790012242 |
| 6 | 17:37–17:39 | Staging (5 files, shas match) + dmesg-pre + eventlog-pre on H42; audio DOWN | `t42-dmesg-h42-pre.txt` (470 lines, 2 AcceptAsync [16.92][64.10] boot noise, 34 Ioctl ≤[110]) |
| 7 | 17:43:10–17:44:27 | H43 (btime 1790012590), audio DOWN | postr2 eventlog boundaries |
| 8 | 17:45:00–17:46:17 | H44 (btime 1790012700), audio DOWN | postr2 boundaries |
| 9 | 17:49:40–17:50:09 | H45 (btime 1790012979), audio DOWN | postr2 boundaries |
| 10 | 17:50:10 | `wsl --shutdown` BY ME (clean, rc=0 — first audio-recovery attempt after 5 down boots; tabled, justified) | H45-teardown 13:50:09 = the shutdown |
| 11 | 17:50:26–17:51:43 | H46 (btime 1790013025, demand-boot), audio DOWN (incl. delayed recheck) | socket checks |
| 12 | 17:51:45–17:58:38 | H47 (btime 1790013105); 5-min activity-hold test 6/6 same btime (uptime 46→296 s) — an ACTIVE ssh HOLDS the VM; idle gaps get reaped | hold-test output |
| 13 | 17:5x | `sc stop WslService` → STOPPED (clean) → `sc start` → START_PENDING, BY ME (second recovery attempt; T40 recipe minus taskkills) | sc query outputs |
| 14 | 17:59:29–18:03:53 | H48 (btime 1790013569, post-bounce), audio DOWN (immediate + delayed) | socket checks |
| 15 | 18:04:08 ([0] VM-H49) | H49 create | postr2 boundaries + btime 1790013847 |
| 16 | 18:04–18:08 | R1 pre-run on H49 (X11 mount, PPM 0.0000/0, staged shas, socket PRESENT — FALSE healthy, see §T42-3) | receipts below |
| 17 | 18:08:08–18:12:27 ([240]→[499] H49) | R1: 3 attempts, cubeb modal on EVERY snap, NO-PARK, T42_DONE exit 0 (dialogwatch NOT started — launch error, tabled) | stdout 378 lines, 11 forensics snaps, poll log 98 lines, census |
| 18 | 18:12–18:17 | Post-R1 dmesg (SAME VM) + forensics fetches + analyze + socket-LIVENESS test (PULSE_LIVE — raw connect succeeds!) | `t42-dmesg-h49-postr1.txt` (789 lines; ZERO in R1's window) |
| 19 | 18:17:29–18:21:49 ([802]→[1061] H49) | R2: same modal failure, NO-PARK, T42_DONE exit 0 (dialogwatch started SEQUENTIALLY after — guarded nothing; launch error, tabled) | stdout 379 lines, 3 forensics snaps |
| 20 | 18:21–18:26 | Post-R2 forensics (3 snaps) + R1 census fetch + eventlog-postr2 (120 entries) | files below |
| 21 | 18:26:34 | H49 teardown (NOT by me — analysis gap) | postr2 boundaries (R2's dmesg MISSED — receipt gap, tabled) |
| 22 | 18:27:50 ([0] VM-H50) | H50 create | postr2/final boundaries + btime 1790015270 |
| 23 | 18:28–18:29 | R3 pre-run on H50 (X11 mount, PPM 0.0000/0, socket present, C: 14 G) + modal probe evidence applied | receipts below |
| 24 | 18:29:01– | R3 (run + delayed v2a + window census): §T42-5 | — |

Audio-block forensics (pre-run; the T41 R1/R2 signature, persistent):

| Item | Value |
|---|---|
| Socket absent | H40-era, H42, H43, H44, H45, H46 (6 consecutive boots, incl. immediate + delayed checks) |
| Host sound | 6 OK devices (same list as T41) → WSLg-side defect, not host audio |
| `.wslconfig` | `[wsl2] memory=10GB` only — no `guiApplications=false`; config clean (read-only, untouched) |
| weston.log | weston 9.0.0 starts normally (`WSL2_GUI_APPS_ENABLED=1`, `PULSE_SERVER=unix:/mnt/wslg/PulseServer` expected); only benign app-list noise + one shared-memory I/O error — no smoking gun |
| `wsl --shutdown` (by me) | Clean rc=0; next boot (H46) STILL down — full stack bounce does NOT recover it |
| `sc stop/start WslService` (by me) | STOPPED clean (no taskkills needed — unlike T40's wedge) → START_PENDING; next boot (H48) STILL down |
| pulseaudio in guest | NOT installed (`which` rc=1) — dummy-pulse workaround would need apt install (not pursued; v2 mitigation pursued instead) |
| T4 precedent | T4 (Sep 20) also recorded WSLg down ("no wslg.exe/weston.exe") — recurring box condition; T-lane runs on Xvfb regardless |
| Resolution path | Modal PROBE (below) proves stock v2-order dismissal removes the modal → run WITH v2 mitigation; R3 boots healthy (cubeb succeeds) and parks |

Modal probe (`t42-probe.sh`, forensics/hygiene script — committed; boot +
snap + ONE v2-order dismissal + snap + kill; emulog preserved first via
rotation-style `cp`):

| Item | Value |
|---|---|
| Windows at T+25 | root 511 (skip) + game 2097159 `SSX 3 [Devel]` 640x480 (skip) + modal 2097176 `Error` 500x100 → `PROBE_DISMISS:2097176:Error` (modal enumerated AFTER game — v2-order first-hit = the modal) |
| Dismissal mechanics | `windowfocus` ok; `key --window Return` printed KEY-FAILED (race: modal closed in response, post-send verify failed) — dismissal EFFECTIVE despite the nonzero print |
| probe1 (T+25) | cubeb modal over black game window (viewed) — audio-down signature reproduced live |
| probe2 (T+30) | modal GONE, black screen (viewed) — v2-order dismissal PROVEN end-to-end |
| WID | 2097159 (same as T31–T41 runs) |
| Cleanup | `PROBE_PCSX2_DEAD`, `T42_PROBE_DONE`, exit 0; NVM sha re-verified `da021d2a…` post-probe (unchanged) |
| Caveat (found on R3) | Probe had NO separate `pcsx2-qt` main window; R3's v2a met root+game+main (no modal) — window ORDER differs by boot phase; the probe proves Return-to-modal works, NOT that stock v2 always hits the modal first (R3 §T42-5) |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` (as root, T4 recipe) on H49 pre-R1 and H50 pre-R3; does NOT persist reboot (re-landed per run VM); belt-and-braces (probe + Xvfb start cleanly regardless — T32 G11 – T41 G11 stand) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by each run/probe |
| Dirs/files created | `/home/brad/pcsx2-t4/t42-{auto,analyze,vcount,cropdiff}.sh/.py`, `t42-dialogwatch2.sh`, `t42-probe.sh`, `t42-{r1-census,samples}.txt` (via analyze), `t42-*.jpg/.ppm/.log`, `t42probe1/2.jpg/.ppm`, `…/logs/emulog-pre-t42-probe.txt` + `emulog-pre-t42-*.txt` (rotation chain, see trace table), `boot-t42probe.log/.stdout`, `boot-t42.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t42*` staging (removed after each batch) |
| Untouched | `.wslconfig` (read-only), BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| Restarts by me | `wsl --shutdown` (clean, 13:50:10) + `sc stop/start WslService` (clean) — both tabled above with justification; all VM turnovers NOT by me (idle reaper) |
| VM restarts (not by me) | H40→H50 chain above; ZERO in R1's window (H49 held 240→1061 by activity); R2 same VM; R3 §T42-5 |

## T42-3. R1 — NO-PARK (environment failure: cubeb modal despite pre-run socket-present)

R1 booted on VM-H49 (T_BOOT 1790014087, uptime 240; 18:08:08 UTC) and ran
all 3 park attempts, each ending NO-TITLE-IN-WINDOW: the PCSX2 cubeb
modal sat over the game window on EVERY snap (viewed: `a1-poll12` TRUE
TITLE + modal at band 16.7906/151 remote, 16.6061/147 PIL), pushing
attract scores to 23.4–46.8 and the title plateau to 16.60–16.79 (bar:
mean < 2.0 AND p99 ≤ 10) so the detector never fired. NO-PARK,
`T42_DONE`, exit 0, clean SIGTERM shutdown at uptime 499 (T+259).
Environment failure: effects on the question unverifiable per the T27 §4
rule → not an attempt on the question → re-run as R2.

Pre-run audio trap (new T42 lesson): the R1 pre-run socket check PASSED
(`/mnt/wslg/PulseServer` present, SOCK_RC=0) yet cubeb STILL failed at
boot — socket-PRESENCE ≠ audio-healthy (stale/unserved socket). Post-R1,
a raw-connect liveness test reports PULSE_LIVE while R2 (same VM,
minutes later) STILL modals — even a live raw connect ≠ cubeb-healthy
(cubeb needs an authed protocol session, not just an accepting socket).
The T42 audio gate is therefore BEHAVIORAL (modal present/absent at
boot, probe-verified dismissal) not socket-based.

Launch error (tabled): dialogwatch was NOT started for R1 (single launch
call instead of two) — R1 ran unguarded. R1's modal would have been
dismissible (probe-proven order on the probe boot).

### R1 attempt table (all 3 attempts NO-TITLE-IN-WINDOW)

| Attempt | Detect (attract/title-band) | Presses | Outcome |
|---|---|---|---|
| A1 | `a1-now` attract 30.5644/153 (30.6052/151 PIL); polls 01–18 span 25.23–42.25: poll12–17 plateau 16.60–16.79 = TRUE TITLE under the modal (viewed poll12; PIL 16.40–16.61/145–147) | Cross 535.5 ms @T+98.99→99.53 (attract-skip) | no-title in window |
| A2 | `a2-now` attract 26.8035/163; polls span 23.42–46.83, all attract-under-modal | Cross 535.0 ms @T+149.54→150.07 | no-title in window |
| A3 | `a3-now` attract 28.1919/157; polls span 24.91–44.79, all attract-under-modal | Cross 536.1 ms @T+200.16→200.69 | no-title in window |

### R1 forensics snaps (committed 11; PIL title-band / whole-vs-menu cross-check of the remote)

| Snap (T+) | Size / sha12 | Band vs title (remote → PIL) | Whole vs menu (PIL) | Content |
|---|---|---|---|---|
| start (T+97) | 60359 B / `03425d740c3e` | → 42.2285/192 | 21.0332/174 | attract + modal |
| a1-now (T+98) | 59704 B / `5c2d04bb7d61` | 30.5644/153 → 30.6052/151 | 17.5286/184 | attract + modal |
| a1-poll01 (T+102) | 61074 B / `e8bc3a80d960` | 27.5169/147 → 27.5389/145 | 19.1313/194 | attract + modal |
| a1-poll12 (T+132) | 61279 B / `0963b126e1cc` | 16.7906/151 → 16.6061/147 | 17.1508/165 | TRUE TITLE + modal (viewed) |
| a1-poll13 (T+135) | 62678 B / `a6d3055b327c` | 16.6677/147 → 16.4728/145 | 17.1122/165 | TRUE TITLE + modal |
| a1-poll14 (T+137) | 62711 B / `538f1b1bef56` | 16.6116/147 → 16.4180/145 | 17.1364/165 | TRUE TITLE + modal |
| a1-poll15 (T+140) | 62594 B / `cf91657257dc` | 16.6012/147 → 16.4016/145 | 17.1313/165 | TRUE TITLE + modal |
| a1-poll16 (T+143) | 62744 B / `36623a98e416` | 16.6331/147 → 16.4416/145 | 17.1396/165 | TRUE TITLE + modal |
| a1-poll17 (T+146) | 62499 B / `1c9ebfc11fab` | 16.6012/147 → 16.4016/145 | 17.1304/165 | TRUE TITLE + modal |
| a1-poll18 (T+148) | 50549 B / `d9a15d843a22` | 25.2817/168 → 25.3168/168 | 20.2155/166 | attract + modal |
| a3-poll18 (T+250) | 60728 B / `d01a5e209475` | 40.2876/212 → 40.3246/212 | 22.1466/205 | attract + modal |

| Item | Value |
|---|---|
| R1 window | 18:08:08–18:12:27 UTC (T+0–259), VM-H49 uptime 240→499 |
| Modal text (viewed) | identical cubeb text/geometry to T41 R1/R2 + T42 probe |
| In-trace smoking gun | R1 census: `MARK ERROR 197 [0.5850] cubeb_stream_init() failed: CUBEB_ERROR (-1)` (audio dies 0.59 s into the boot; T41 R1: [0.5826]) |
| Census | `t42r1-census.txt` (11627 B) / `t42r1-samples.txt` (5840 B): lines 29226569, span 0.1334..249.2522 (≈T41 R1's 29223690/..249.05) |
| Flaps | ZERO in-window AcceptAsync (6 H49 flaps: [66.88][89.71][154.92][206.19] pre-window + [514.46][582.43] post-window; R1 = 240–499) + ZERO event-log entries in-window (14:05:08 IUM pair pre-window; 14:13:08 IUM single post-window) |
| R1 verdict | NO-PARK as an environment failure (modal occludes the detector band), effects-unverifiable per T27 §4 → re-run as R2; partial trace preserved bytesize-only via R2-boot rotation |

## T42-4. R2 — NO-PARK (same environment failure, same VM; dialogwatch guarded nothing)

R2 booted on the SAME VM-H49 (T_BOOT 1790014649, uptime 802; 18:17:29
UTC) and reproduced R1 exactly: 3/3 attempts NO-TITLE-IN-WINDOW with the
identical cubeb modal on every snap (A1 poll12–18 plateau 16.60–16.79 =
TRUE TITLE under modal; PIL poll12 16.6009/147). NO-PARK, `T42_DONE`,
exit 0, clean shutdown at uptime 1061 (T+260). Environment failure (2/2
runs on H49) → R3 on a fresh VM with the corrected parallel-launch
protocol.

Launch error (tabled): the R2 run + dialogwatch calls issued in ONE
message executed SEQUENTIALLY — the run (260 s) completed first, THEN
dialogwatch ran 40 root-only rounds (NO-DIALOG-SEEN, exit 0) against the
post-run display. R2 ran UNGUARDED. R3 protocol fix: run-ssh with short
yield (backgrounds, holds VM) → local sleep 35 → dialogwatch-ssh (lands
~T+37, modal-certain) → verify log → conditional re-watch.

### R2 attempt table (all 3 attempts NO-TITLE-IN-WINDOW)

| Attempt | Detect (attract/title-band) | Presses | Outcome |
|---|---|---|---|
| A1 | `a1-now` attract 34.5459/180; polls 01–11 span 25.79–44.24, poll12–18 plateau 16.60–16.79 = TRUE TITLE under the modal | Cross @T+98.6 (attract-skip; walls in overwritten poll log — see gap) | no-title in window |
| A2 | `a2-now` attract 28.0775/157; polls span 23.29–48.39, all attract-under-modal | Cross @T+149.2 | no-title in window |
| A3 | `a3-now` attract 33.3646/166; polls span 26.22–44.52, all attract-under-modal | Cross @T+199.9 | no-title in window |

### R2 forensics snaps (committed 3; duplicates R1 — mechanism pair + tail only, T41-R2 precedent)

| Snap (T+) | Size / sha12 | Band vs title (remote → PIL) | Whole vs menu (PIL) | Content |
|---|---|---|---|---|
| start (T+97) | 65466 B / `141ad7f8afc3` | → 31.8575/196 | 17.0339/171 | attract + modal |
| a1-poll12 (T+132) | 61057 B / `b8bb41577d4d` | 16.7872/151 → 16.6009/147 | 17.1449/165 | TRUE TITLE + modal |
| a3-poll18 (T+250) | 62766 B / `66b2a1953697` | → 41.1270/223 | 22.8421/209 | attract + modal |

| Item | Value |
|---|---|
| R2 window | 18:17:29–18:21:49 UTC (T+0–260), VM-H49 uptime 802→1061 |
| Modal | identical text/geometry to R1 (viewed R1's poll12; R2's poll12 scores identically) |
| Census | R2 analyze NOT run (no `t42r2-census/samples` — same failure as R1, skipped deliberately, T41 precedent) |
| Poll log | R2's `t42-poll.log` NOT fetched (R3 overwrote it on-box before fetch — receipt gap, tabled; press walls lost, MENU_T+ from stdout retained) |
| dmesg | R2's post-run dmesg MISSED (H49 turned over during the analysis gap — receipt gap, tabled; R1's dmesg covers the same VM) |
| Flaps | ZERO event-log entries in-window (14:13:08 IUM pre-window; next entries post-window) |
| R2 verdict | NO-PARK as an environment failure (2/2 on H49), effects-unverifiable per T27 §4 → R3 on VM-H50 with corrected protocol; partial trace preserved bytesize-only via R3-boot rotation |

## T42-5. R3 — full chain + ONE hold + blind dense series (the run)

R3 booted on VM-H50 (T_BOOT 1790015341, uptime 71; 18:29:01 UTC) under
HEALTHY audio (cubeb-pulse negotiated [0.5852/0.5876], zero
null-fallback lines in 2.75 GB, full libsd IOP set, no modal on 61/61
snaps) and reproduced the T41 R4 chain: A1 title-detect @poll01 (remote
0.4331/6 — T40 R2's exact reading), all 8 menu gates, MR panel settle,
X countdown, LIVE race, pre-hold pair, ONE 1036.5 ms Left hold, 10-snap
blind series. `DENSE-BLIND-COMPLETE`, `T42_DONE`, exit 0, clean SIGTERM
shutdown at uptime 589 (T+518; T41 R4: T+520). 514-line stdout / 2551-line
stderr (T41 R4: 512/2551). WID 2097159 (same as T31–T41).

| Item | Value |
|---|---|
| R3 window | 18:29:01–18:37:40 UTC (T+0–519), VM-H50 uptime 71→589 (ZERO in-window flaps: 2 AcceptAsync [17.68] pre + [604.84] post; ZERO in-window event-log entries — H50 create 14:27:50 → teardown 14:55:16 brackets the run with no interior entries) |
| Dialogwatch v2 | ROUND:1 @T+54.5: SKIP-GAME 2097159 + DISMISS 2097162 `pcsx2-qt` + DISMISSED-EXIT (main-window, inert — R4 pattern; NO modal existed to dismiss; mid-run window census @T+75: only the game window visible) |
| Title detect | A1 `poll01` remote 0.4331/6 (PIL 0.0467/1) — parked FIRST attempt (a2/a3 never ran; on-box a2/a3 snaps are R1/R2 stale, NOT fetched) |
| Presses | 10 menu/Start Cross (all 535.3–538.9 ms) + ONE hold (§press log); ZERO other game inputs (11 KEYDOWN/KEYUP pairs total in 168-line poll log = T41 R4's 168) |

### R3 press log (poll-log walls; T+ = wall − 1790015341)

| Press | Keydown wall (T+) | Keyup wall (T+) | Width |
|---|---|---|---|
| A1 Cross (attract-skip) | 1790015439.753 (T+98.75) | 1790015440.290 (T+99.29) | 536.5 ms |
| A1 Start (on title) | 1790015443.044 (T+102.04) | 1790015443.580 (T+102.58) | 535.7 ms |
| MENU Cross (Single Event) | 1790015482.260 (T+141.26) | 1790015482.797 (T+141.80) | 537.0 ms |
| ZOE Cross | 1790015522.469 (T+181.47) | 1790015523.005 (T+182.00) | 536.6 ms |
| CONT Cross | 1790015551.318 (T+210.32) | 1790015551.853 (T+210.85) | 535.4 ms |
| PEAK Cross (Peak 1) | 1790015580.287 (T+239.29) | 1790015580.823 (T+239.82) | 536.2 ms |
| RACE Cross | 1790015609.809 (T+268.81) | 1790015610.345 (T+269.34) | 535.5 ms |
| SNOWJAM Cross | 1790015641.116 (T+300.12) | 1790015641.651 (T+300.65) | 535.3 ms |
| ENTER Cross | 1790015669.899 (T+328.90) | 1790015670.436 (T+329.44) | 536.7 ms |
| X Cross (X Continue) | 1790015775.937 (T+434.94) | 1790015776.476 (T+435.48) | 538.9 ms |
| HOLD Left | 1790015843.488 (T+502.49) | 1790015844.525 (T+503.52) | 1036.5 ms |

### R3 chain table (61/61 fetched; T+ from wall lines; PIL panel scores; viewed frames marked)

| Snap (T+) | Size | Band vs title (PIL) | Best ref (PIL) | Content |
|---|---|---|---|---|
| start (T+97) | 56779 | 36.0713/191 | attract | attract (remote 36.0769/191) |
| a1-now (T+98) | 56195 | 26.9600/156 | attract | attract (remote 26.9/156) |
| a1-poll01 (T+101) | 58352 | 0.0467/1 | TITLE | TRUE TITLE (viewed; remote 0.4331/6) |
| a1-pre (T+101) | 58352 | 0.0467/1 | TITLE | = poll01 (cp-identical scores) |
| a1-post3 (T+105) | 49851 | 16.2604/138 | menu 0.0599/1 | Main Menu |
| a1-post8 (T+111) | 49991 | 16.2911/138 | menu 0.0609/1 | Main Menu |
| a1-post15 (T+119) | 49619 | 16.2622/138 | menu 0.0260/0 | Main Menu |
| a1-post25 (T+129) | 49729 | 16.2622/138 | menu 0.0401/0 | Main Menu |
| menupre (T+139) | 49663 | 16.2622/138 | menu 0.0278/0 | Main Menu (viewed; Single Event) |
| mc-post1 (T+142) | 70228 | 12.4592/163 | sc 0.0833/1 | Select Character (remote vs-sc 0.4470/7) |
| mc-post3 (T+147) | 70355 | 12.4890/163 | sc 0.0721/1 | Select Character |
| mc-post8 (T+155) | 70415 | 12.4641/163 | sc 0.2768/5 | Select Character |
| mc-post15 (T+164) | 70338 | 12.4587/163 | sc 0.0235/0 | Select Character |
| scpre (T+178) | 70640 | 12.7296/163 | sc 0.1320/2 | Select Character (viewed; Zoe) |
| zc-post1 (T+183) | 51397 | 15.8360/128 | zc 0.2860/7 | Setup Character (remote vs-zc 0.5189/9) |
| zc-post3 (T+187) | 51487 | 15.8827/129 | zc 0.2444/7 | Setup Character |
| zc-post8 (T+195) | 51367 | 15.8334/128 | zc 0.2195/5 | Setup Character |
| ccpre (T+207) | 51507 | 15.9068/129 | zc 0.2480/7 | Setup Character (viewed; Zoe/Continue) |
| sp-post1 (T+211) | 65320 | 23.1232/171 | sp 0.0232/0 | Select Peak (remote vs-sp 0.3698/6) |
| sp-post3 (T+216) | 65495 | 23.1273/171 | sp 0.0244/0 | Select Peak |
| sp-post8 (T+224) | 65226 | 23.1259/171 | sp 0.0038/0 | Select Peak |
| sppre (T+216) | 65495 | 23.1273/171 | sp 0.0244/0 | = sp-post3 (cp-identical scores) |
| pc-post1 (T+240) | 67873 | 26.3046/183 | sm 0.1175/1 | Select Mode (remote vs-sm 0.4631/7) |
| pc-post3 (T+245) | 67573 | 26.3046/183 | sm 0.0663/0 | Select Mode |
| pc-post8 (T+253) | 67472 | 26.3029/183 | sm 0.0580/0 | Select Mode |
| smpre (T+265) | 67569 | 26.3036/183 | sm 0.0670/0 | Select Mode (viewed; Race) |
| rc-post1 (T+270) | 69815 | 26.1964/183 | se 0.0673/0 + setag 0.0094/0 | Select Event (remote se-tag 2.6271/11) |
| rc-post3 (T+274) | 69451 | 26.1964/183 | se 0.0364/0 + setag 0.0094/0 | Select Event |
| rc-post8 (T+281) | 69468 | 26.1973/183 | se 0.0404/0 + setag 0.0207/1 | Select Event |
| sepre (T+295) | 69757 | 26.1964/183 | se 0.0703/0 + setag 0.0094/0 | Select Event (viewed; Snow Jam) |
| sj-post1 (T+301) | 59031 | 9.8313/135 | mr 0.1643/3 | My Rules (remote vs-mr 0.4692/8) |
| sj-post3 (T+306) | 59340 | 9.8190/135 | mr 0.1747/3 | My Rules |
| sj-post8 (T+313) | 58831 | 10.0700/135 | mr 0.1234/1 | My Rules |
| mrpre (T+326) | 59101 | 9.8188/135 | mr 0.1620/3 | My Rules (viewed; all Off) |
| mr-post1 (T+330) | 67128 | 18.3745/168 | loading | Race loading 15% (viewed) |
| mr-post3 (T+335) | 67270 | 17.8905/173 | loading | Race loading 96% (viewed) |
| mr-post8 (T+342) | 54550 | 28.8051/237 | pre-race | Pre-race rider panel (viewed) |
| mr-post15 (T+352) | 59505 | 34.4937/184 | pp 0.7527/19 | Panel |
| mr-post25 (T+365) | 59523 | 34.4945/184 | pp 0.7490/19 | Panel |
| mr-post40 (T+383) | 59911 | 34.4829/184 | pp 0.4218/7 | Panel |
| mr-stab1 (T+406) | 59701 | 34.4826/184 | pp 0.5938/11 | Settled panel (remote vs-pp 0.8460/12) |
| mr-stab2 (T+419) | 59713 | 34.4927/184 | pp 0.5897/11 | Settled panel |
| pppre (T+432) | 59681 | 34.4831/184 | pp 0.6228/12 | Settled panel (viewed; 6 riders, Zoe) |
| x-post1 (T+436) | 69553 | 19.1417/162 | departed | Start gate countdown 2, 00:00:00 (viewed) |
| x-post3 (T+440) | 68082 | 21.7861/142 | live | LIVE 5TH/6, 00:00:02, 1%, 39 MPH (viewed) |
| x-post8 (T+447) | 69336 | 12.7655/123 | live | LIVE 4TH/6, 00:00:10, 5%, 51 MPH (viewed) |
| x-post15 (T+455) | 63416 | 14.7127/135 | live | LIVE 3RD/6, 00:00:23, 12%, 50 MPH (viewed) |
| x-post25 (T+467) | 68064 | 12.2804/159 | live | LIVE 1ST/6, 00:00:40, 21%, 53 MPH, OUT-OF-BOUNDS banner (viewed) |
| x-post40 (T+484) | 69356 | 18.2694/136 | live | LIVE 2ND/6, 00:01:02, 28%, 45 MPH (viewed) |
| npre1 (T+501) | 53597 | 28.0213/138 | live | LIVE 5TH/6, 00:01:27, 36%, 55 MPH (viewed) |
| npre2 (T+502) | 56398 | 23.0738/126 | live | LIVE 5TH/6, 00:01:28, 37%, 51 MPH, rival wipeout left (viewed) |
| d-post1 (T+504) | 52225 | 23.4787/162 | live | LIVE 6TH/6, 00:01:31, 37%, 7 MPH — TREE CRASH (viewed) |
| d-post2 (T+504) | 59571 | 19.3842/170 | live | LIVE 6TH/6, 00:01:32, 37%, 18 MPH, dense forest (viewed) |
| d-post3 (T+505) | 59173 | 16.6628/114 | live | LIVE 6TH/6, 00:01:32, 37%, 32 MPH, trunk gap (viewed) |
| d-post4 (T+505) | 58920 | 22.8622/143 | live | LIVE 6TH/6, 00:01:33, 37%, 43 MPH (viewed) |
| d-post5 (T+506) | 56425 | 25.4875/158 | live | LIVE 6TH/6, 00:01:34, 38%, 58 MPH (viewed) |
| d-post6 (T+506) | 54158 | 27.6065/134 | live | LIVE 6TH/6, 00:01:35, 38%, 51 MPH (viewed) |
| d-post7 (T+507) | 55360 | 24.1813/126 | live | LIVE 6TH/6, 00:01:36, 38%, 49 MPH (viewed) |
| d-post8 (T+508) | 55778 | 15.5661/121 | live | LIVE 6TH/6, 00:01:36, 39%, 48 MPH (viewed) |
| d-post9 (T+508) | 59171 | 11.9045/124 | live | LIVE 6TH/6, 00:01:37, 39%, 48 MPH (viewed) |
| d-post10 (T+509) | 53864 | 15.5300/106 | live | LIVE 6TH/6, 00:01:38, 40%, 48 MPH, wall (viewed) |

### R3 transition hops (whole-frame PIL; dense hops have NO in-script remote counterpart)

| Hop | Whole (PIL) | Hop | Whole (PIL) |
|---|---|---|---|
| menupre→mc-post1 | 10.1510/105 | mc-post1→mc-post3 | 0.1245/2 |
| mc-post3→mc-post8 | 0.3285/8 | mc-post8→mc-post15 | 0.2995/6 |
| mc-post15→scpre | 0.1547/3 | scpre→zc-post1 | 7.1068/100 |
| zc-post1→zc-post3 | 0.3173/9 | zc-post3→zc-post8 | 0.2962/8 |
| zc-post8→ccpre | 0.3016/8 | ccpre→sp-post1 | 9.3908/153 |
| sp-post1→sp-post3 | 0.0405/0 | sp-post3→sp-post8 | 0.0206/0 |
| sp-post8→sppre | 0.0206/0 | sppre→pc-post1 | 5.2743/121 |
| pc-post1→pc-post3 | 0.1141/0 | pc-post3→pc-post8 | 0.0545/0 |
| pc-post8→smpre | 0.0552/0 | smpre→rc-post1 | 0.5402/12 |
| rc-post1→rc-post3 | 0.0413/0 | rc-post3→rc-post8 | 0.0148/0 |
| rc-post8→sepre | 0.0489/0 | sepre→sj-post1 | 10.6491/143 |
| sj-post1→sj-post3 | 0.1953/4 | sj-post3→sj-post8 | 0.1545/1 |
| sj-post8→mrpre | 0.1418/2 | mrpre→mr-post1 | 12.6147/149 |
| mr-post1→mr-post3 | 1.7886/61 | mr-post3→mr-post8 | 25.2149/253 |
| mr-post8→mr-post15 | 19.2369/190 | mr-post15→mr-post25 | 0.0409/1 |
| mr-post25→mr-post40 | 0.3669/16 | mr-post40→mr-stab1 | 0.2035/9 |
| mr-stab1→mr-stab2 | 0.0336/1 | mr-stab2→pppre | 0.0588/2 |
| pppre→x-post1 | 14.4485/152 | x-post1→x-post3 | 13.7389/132 |
| x-post3→x-post8 | 13.9213/126 | x-post8→x-post15 | 9.8186/139 |
| x-post15→x-post25 | 11.3744/163 | x-post25→x-post40 | 14.4408/160 |
| x-post40→npre1 | 11.6679/107 | npre1→npre2 | 6.2614/84 |
| npre2→d-post1 (HOLD) | 7.6624/97 | d-post1→d-post2 | 5.9760/105 |
| d-post2→d-post3 | 9.3201/116 | d-post3→d-post4 | 8.5433/120 |
| d-post4→d-post5 | 6.2231/81 | d-post5→d-post6 | 5.5869/94 |
| d-post6→d-post7 | 5.0733/109 | d-post7→d-post8 | 10.2079/104 |
| d-post8→d-post9 | 13.5190/127 | d-post9→d-post10 | 18.3941/180 |

Dense whole-hop range 5.07–18.39 (T41: 6.36–17.47 — same motion class);
hold hop 7.6624/97 (T41: 17.4716/192 — smaller whole-frame: crash =
low-speed tumble vs T41's fast carve); pre-pair 6.2614/84 (T41: 6.3620/69).

### R3 cross-run identities vs T41 R4 (whole-frame PIL per snap)

| Snap | T42 vs T41 | Snap | T42 vs T41 |
|---|---|---|---|
| start | 0.0000/0 | a1-now | 3.2149/79 |
| a1-poll01 | 0.0308/0 | a1-pre | 0.0308/0 |
| a1-post3 | 0.0678/1 | a1-post8 | 0.0712/1 |
| a1-post15 | 0.0004/0 | a1-post25 | 0.0258/0 |
| menupre | 0.0035/0 | mc-post1 | 0.1818/4 |
| mc-post3 | 0.2003/5 | mc-post8 | 0.1750/4 |
| mc-post15 | 0.1798/3 | scpre | 0.1597/3 |
| zc-post1 | 0.0360/0 | zc-post3 | 0.0938/2 |
| zc-post8 | 0.0349/0 | ccpre | 0.0402/0 |
| sp-post1 | 0.0222/0 | sp-post3 | 0.0201/0 |
| sp-post8 | 0.0000/0 | sppre | 0.0406/0 |
| pc-post1 | 0.1228/1 | pc-post3 | 0.0561/0 |
| pc-post8 | 0.0286/0 | smpre | 0.0573/0 |
| rc-post1 | 0.0676/0 | rc-post3 | 0.0099/0 |
| rc-post8 | 0.0478/0 | sepre | 0.0786/0 |
| sj-post1 | 0.1276/2 | sj-post3 | 0.1988/4 |
| sj-post8 | 0.0744/0 | mrpre | 0.2159/5 |
| mr-post1 | 1.6994/57 | mr-post3 | 1.5460/60 |
| mr-post8 | 4.6937/96 | mr-post15 | 0.4074/6 |
| mr-post25 | 0.8046/22 | mr-post40 | 0.4773/7 |
| mr-stab1 | 0.3830/6 | mr-stab2 | 0.6331/14 |
| pppre | 0.6022/12 | x-post1 | 1.3298/39 |
| x-post3 | 7.0837/109 | x-post8 | 6.4105/99 |
| x-post15 | 4.3002/74 | x-post25 | 9.2379/121 |
| x-post40 | 15.5982/134 | npre1 | 12.1853/99 |
| npre2 | 11.1980/110 | d-post1 | 8.6340/93 |
| d-post2 | 9.8538/102 | d-post3 | 10.2267/123 |
| d-post4 | 11.2546/137 | d-post5 | 13.2405/147 |
| d-post6 | 19.6241/150 | d-post7 | 11.6824/98 |
| d-post8 | 7.4390/93 | d-post9 | 13.7424/149 |
| d-post10 | 18.0215/194 | — | — |

Menus reproduce T41 near-pixel-identical through mrpre (start 0.0000/0
byte-class; menus ≤0.22); loading/panel/countdown jitter 0.4–4.7 (rival
lineup + % jitter); gameplay diverges 4–20 (AI/RNG lottery — the T-lane
pattern).

### R3 HUD table (viewed; score 0 on all 18 — back-of-pack survival, no tricks)

| Snap | Pos | Clock | Prog | Speed | Snap | Pos | Clock | Prog | Speed |
|---|---|---|---|---|---|---|---|---|---|
| x-post1 | gate | 00:00:00 | 0% | 0 MPH | x-post3 | 5TH/6 | 00:00:02 | 1% | 39 MPH |
| x-post8 | 4TH/6 | 00:00:10 | 5% | 51 MPH | x-post15 | 3RD/6 | 00:00:23 | 12% | 50 MPH |
| x-post25 | 1ST/6 | 00:00:40 | 21% | 53 MPH | x-post40 | 2ND/6 | 00:01:02 | 28% | 45 MPH |
| npre1 | 5TH/6 | 00:01:27 | 36% | 55 MPH | npre2 | 5TH/6 | 00:01:28 | 37% | 51 MPH |
| d-post1 | 6TH/6 | 00:01:31 | 37% | 7 MPH | d-post2 | 6TH/6 | 00:01:32 | 37% | 18 MPH |
| d-post3 | 6TH/6 | 00:01:32 | 37% | 32 MPH | d-post4 | 6TH/6 | 00:01:33 | 37% | 43 MPH |
| d-post5 | 6TH/6 | 00:01:34 | 38% | 58 MPH | d-post6 | 6TH/6 | 00:01:35 | 38% | 51 MPH |
| d-post7 | 6TH/6 | 00:01:36 | 38% | 49 MPH | d-post8 | 6TH/6 | 00:01:36 | 39% | 48 MPH |
| d-post9 | 6TH/6 | 00:01:37 | 39% | 48 MPH | d-post10 | 6TH/6 | 00:01:38 | 40% | 48 MPH |

Progress monotonic 0→40%; ONE position decay in the dense window
(5TH→6TH inside the hold hop, crash-driven); x-post25 carries an
OUT-OF-BOUNDS banner (rider recovered — x-post40 races normally).

### R3 dense exposures (poll-log ns SNAPSTART stamps; cadence check)

| Gap | Exposure | Gap | Exposure |
|---|---|---|---|
| npre1→npre2 (pre-pair, no input) | 0.5761 s | npre2→d-post1 (hold span) | 1.6148 s |
| d-post1→d-post2 | 0.5772 s | d-post2→d-post3 | 0.5737 s |
| d-post3→d-post4 | 0.5785 s | d-post4→d-post5 | 0.5747 s |
| d-post5→d-post6 | 0.5757 s | d-post6→d-post7 | 0.5757 s |
| d-post7→d-post8 | 0.5733 s | d-post8→d-post9 | 0.5746 s |
| d-post9→d-post10 | 0.5767 s | npre1→d-post10 span | 7.3708 s wall / +11 s race (1.49×; integer-second quantization [1.36,1.63] overlaps T41's [1.47,1.76]) |

10× ≈0.575 s (T41: 10× ≈0.57 s) — SAME cadence ✓. Hold span 1.6148 s =
0.5 sleep + 1036.5 ms hold + 0.5 sleep + snap overheads.

### R3 phase-match verdict (vs §T42-0 targets — match phase not seed)

| Item | Target | R3 observed | Match |
|---|---|---|---|
| Hold slot | ≈T+503 | T+502.49 (keydown) | yes (0.7 s) |
| Pre-pair clocks | ≈00:01:2x–3x | 00:01:27 / 00:01:28 | yes (−1–2 s) |
| Pre-pair positions | racing pack | 5TH/5TH/6 | yes (lottery) |
| Pre-pair progress | ≈45% ±5 pp | 36% / 37% | 4 pp under band edge (back-of-pack correlates; T41 precedent: proceeded on band-edge; slot/clock/pack match — NO re-attempt) |
| Series span | ≈+7 s wall | +7.37 s wall | yes |

## T42-6. R3 tracking (BOTH trackers on all 12 dense snaps) + comparison + recipe

### R3 RDC + SCPS table (control = frozen `t41-track.py`; retuned = `t42-track.py`; SCPS 22/22 identical)

| Snap | Control cx/cy/npix | C-gate | Retuned cx/cy/npix | R-gate | Retuned lock (marked-crop montage) |
|---|---|---|---|---|---|
| npre1 | 338.5/252.6, 10595 (0.0755) | INVALID | 332.7/314.5, 3515 (0.0976) | VALID | on-rider (legs/board) |
| npre2 | 342.7/274.4, 3563 (0.0254) | VALID | 332.0/292.3, 1484 (0.0412) | VALID | on-rider (mid-body; rival crash excluded) |
| d-post1 | 342.5/280.3, 26354 (0.1877) | INVALID | 343.2/252.8, 5000 (0.1389) | VALID | borderline-on (head/shoulder; trunk intrudes right) |
| d-post2 | 338.2/187.2, 22396 (0.1595) | INVALID | 327.8/264.2, 10162 (0.2823) | INVALID | flood (bilateral trees) — correctly gated |
| d-post3 | 304.3/164.2, 21597 (0.1538) | INVALID | 270.4/245.3, 8316 (0.2310) | INVALID | flood (bilateral trunks) — correctly gated |
| d-post4 | 270.7/206.4, 23764 (0.1693) | INVALID | 258.5/259.5, 5147 (0.1430) | VALID | on-rider (trunks excluded by ROI) |
| d-post5 | 319.5/161.6, 19982 (0.1423) | INVALID | 279.0/234.3, 5026 (0.1396) | VALID | off-rider ~40 px above (shade/totem pulls up) |
| d-post6 | 348.4/169.5, 16605 (0.1183) | INVALID | 287.9/275.0, 4333 (0.1204) | VALID | borderline-on (head/left side) |
| d-post7 | 347.0/160.3, 18297 (0.1303) | INVALID | 295.3/247.1, 3050 (0.0847) | VALID | borderline-on (~15 px left of head) |
| d-post8 | 309.5/173.2, 11880 (0.0846) | INVALID | 303.4/285.1, 1492 (0.0414) | VALID | on-rider |
| d-post9 | 327.1/180.6, 22757 (0.1621) | INVALID | 350.2/231.9, 2622 (0.0728) | VALID | off-rider ~50 px right (totem wall pulls) |
| d-post10 | 397.0/223.5, 19125 (0.1362) | INVALID | 289.9/225.7, 9389 (0.2608) | INVALID | flood (wall) — correctly gated |

| Hop | SCPS40 (both tools) | SCPS120 (both tools) |
|---|---|---|
| npre1→npre2 (pre-pair) | +9 @ 0.83 | +9 @ 0.83 |
| npre2→d-post1 (HOLD) | +13 @ 0.23 (off-rail, weak) | +120 @ 0.60 RAIL |
| d-post1→d-post2 | +40 @ −0.25 RAIL | +118 @ 0.48 |
| d-post2→d-post3 | −6 @ 0.28 | −115 @ 0.53 |
| d-post3→d-post4 | +3 @ 0.73 | +119 @ 0.60 |
| d-post4→d-post5 | −4 @ 0.72 | −4 @ 0.72 |
| d-post5→d-post6 | +33 @ 0.64 | +33 @ 0.64 |
| d-post6→d-post7 | +18 @ 0.35 | −98 @ 0.44 |
| d-post7→d-post8 | −40 @ 0.84 RAIL | −40 @ 0.84 |
| d-post8→d-post9 | +40 @ 0.31 RAIL | +40 @ 0.31 |
| d-post9→d-post10 | −40 @ 0.24 RAIL | −120 @ 0.35 RAIL |

### R3 rail-rate comparison vs T41 (per tracker — the brief's success bars)

| Metric | T41 R4 (1038.4 ms hold) | T42 R3 (1036.5 ms hold) |
|---|---|---|
| RDC control gate-out | 11/12 (d-post5 singleton) | 11/12 (npre2 singleton) — REPEATS |
| RDC retuned gate-out | — | 3/12 (d2/d3/d10, all correct flood-gates) |
| Gated pair straddling hold | NO (singleton) | YES — npre2→d-post1, BOTH rider-locked (on + borderline-on) |
| Gated pairs total (retuned) | — | 7 (npre1-npre2, npre2-d1, d4d5, d5d6, d6d7, d7d8, d8d9) |
| SCPS40 rails | 4/11 (hold +29 @ 0.02) | 4/11 (hold +13 @ 0.23) — count REPEATS, both holds off-rail weak |
| SCPS120 rails | 1/11 strict (hold +119 @ 0.37 weak) | 2/11 strict (hold +120 @ 0.60 RAIL + d9d10 −120) — hold UNRESOLVED here |
| Dense whole-hop range | 6.36–17.47 | 5.07–18.39 — same motion class |

### R3 retuned deltas (VALID pairs only, with per-pair lock QA)

| Pair | Δcx/Δcy | Lock QA | Note |
|---|---|---|---|
| npre1→npre2 (no-input floor) | −0.7 / −22.2 | on→on | cx floor ≈ 0 (1 sample) |
| npre2→d-post1 (HOLD) | +11.2 / −39.5 | on→borderline-on | cx step 16× the 1-sample floor; hop contains the TREE CRASH (7 MPH, 5TH→6TH) — motion-vs-crash-vs-bias UNRESOLVED |
| d-post4→d-post5 | +20.5 / −25.2 | on→off | lock change inside pair — bias-contaminated |
| d-post5→d-post6 | +8.9 / +40.7 | off→borderline | lock change inside pair — bias-contaminated |
| d-post6→d-post7 | +7.4 / −27.9 | borderline→borderline | same-quality pair |
| d-post7→d-post8 | +8.1 / +38.0 | borderline→on | same-quality pair |
| d-post8→d-post9 | +46.8 / −53.2 | on→off | lock change DOMINATES (+46.8 cx = totem bias, not rider) |

Direction note (no verdict): the hold cx step is RIGHTWARD (+11.2)
under a LEFT hold — consistent with chase-cam rider-recentering, crash
tumble, or trunk-bias shift; isolation needs a crash-free hold pair
(single run, rival crashed too without input).

Recipe (the STOP deliverable — T40-G1's ROI arm, proven on gating,
bounded on motion):

1. GATING: PROVEN — the retune converts 11/12-flooded into 9/12-gated
   with a rider-locked pair straddling the hold (control floods 11/12
   again on the new stretch). The ROI (not threshold/gradient) is the
   operative change; the frozen gate band separates without touching.
2. MOTION: NOT solved — per-snap intrusion bias (±50 px) survives
   inside VALID pairs (d5 shade, d9 totem, d1 trunk-shoulder); deltas
   across lock-quality changes are bias-dominated (d8→d9 +46.8 cx);
   the hold hop's crash confounds attribution; the no-input floor is a
   single sample.
3. NEXT (one variant): re-run the SAME shape and accumulate ONLY
   on→on VALID pairs (lock-QA-gated, montage method) until the
   hold-step distribution separates from the no-input distribution; or
   test T40's third shape (gradient lock) against this run's 12 snaps
   as a static gate before any new run. Do NOT tighten the ROI further
   (rider-clip risk; calibration margins already 30 px).
4. ENVIRONMENT (carried): WSLg audio flaps per-boot — gate BEHAVIORALLY
   (boot-probe the modal; socket-presence AND raw-liveness both gave
   false healthies); idle reaper kills VMs in ~1–4 min (activity holds —
   5-min test + 27-min H50); parallel-launch protocol = run-background
   → sleep 35 → v2a → verify log → conditional v2b (R2 lesson).

## T42-7. R3 census + trace + forensics

| Item | Value |
|---|---|
| Census | `t42r3-census.txt` (lines=42967628, ts_span=0.1271..508.6201; T41 R4: 42915867/0.1272..508.8612 — same class) |
| EE | 11808311 calls, distinct=52 (top: GetThreadId 4854561, WaitSema 2142285, SignalSema 1894435, sceSifGetReg 1260327) |
| IOP | 18976178 calls, distinct=155 (top: sceSdGetAddr 3772320, QueryIntrContext 3438179, CpuSuspendIntr 3213307, CpuResumeIntr 2174233) |
| libsd (G5 positive) | 12-entry set incl. sceSdInit 1 + sceSdGetParam 15879 (T41 R1's missing call PRESENT — audio initialized) |
| MARK | 21 lines, ERROR NONE (first: BIOS Found [0.1275], cdvdLoadElf SLUS_207.72 [0.1342]) |
| cubeb (G5 positive) | "Creating Cubeb audio stream" [0.5716] + pulse negotiation [0.5852/0.5876]; ZERO null-fallback/CUBEB_ERROR lines in 2.75 GB |
| Vblank stream | first `WaitVblankStart` L417043 [1.2023] (T41: L417043 [1.1963] — same line); 397 total, ALL ≤90 (LE90/110/140/350 all 397 — IDENTICAL to T41) |
| Vcount | vcount program on the SSD copy (path operand swapped; program byte-identical logic) |
| Live trace | `emulog.txt` 2751948037 B sha `5b23c553…d092` (T41 R4's preserved via `emulog-pre-t42-20260921T182901Z.txt`) |
| Rotation | 37 files (T17→T42 chain + probe + R1/R2/R3 boots); R1/R2 partials preserved bytesize-only |
| SSD stream | `COPYFILE_DISABLE=1`, declared cap 4 GB (used 2.75 GB, 1.45× headroom); `/Volumes/Extreme SSD/ps2x-t4/emulog-t42r3.txt` size+sha MATCH (2751948037 B, `5b23c553…d092`); head/tail 30-line slices committed (`t42r3-emulog-head/tail.txt`) |
| Boot logs | `t42r3-boot.log` (4231 B) + `t42r3-boot.stdout` (210 B: DRI3 warnings + CTRL+C graceful shutdown) |
| NVM post-run | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961` — UNCHANGED across probe + 3 runs |
| C: post-session | 11 G avail (18→16→14→11 G across probe+R1+R2+R3 ≈ 2 GB/run trace+rotation drain; still 2× the 5 GB gate — future lanes: watch this) |

Forensics (observed events, tables only — no verdicts): x-post25
OUT-OF-BOUNDS banner at 1ST/21% (rider recovered — x-post40 races 2ND
normally); hold-hop tree crash (d-post1 7 MPH, 5TH→6TH decay — crash vs
input attribution UNRESOLVED, single run, rival crashed too without
input); npre2 rival wipeout (left foreground, x<220 — inside frozen ROI,
excluded from retuned ROI); v2a main-window dismissal @T+54.5 (inert,
R4 pattern) + T+75 window census (game-only, no modal); R1/R2 cubeb-modal
NO-PARKs (§T42-3/4); d5 shade-bias + d9 totem-bias (in-band off-riders,
§T42-6).

## T42-8. Exact commands (reproduce-from-scratch)

Pre-run pins (one `wsl` call per ssh; double-quote grouping only — the
remote shell is PowerShell: bare `;`/`|`/`||` break): `wsl sha256sum`
+ `stat` (binary), `git rev-parse HEAD` + `status --short` (tree),
`ls -la inputs/`, `sha256sum` + `stat` (live NVM), `grep -n Cross/Left`
(bindings), 9-ref `sha256sum`, T41 snap `ls -la` (4/4 spot), logs `ls`,
live-trace `sha256sum` (2.7 GB), `df -h /` + `/mnt/c`, `ls PulseServer`
(audio gate), host sound `powershell Get-CimInstance Win32_SoundDevice`,
`.wslconfig` (`type`), weston.log (`cat` → local grep), `wsl -l -v`,
`sc query/start/stop WslService`, `wsl --shutdown` (by me, once),
`tasklist /FI wslg*`, socket liveness (`python3 -c "import socket; …"`
with `;` INSIDE double quotes), eventlog (`wevtutil qe System /c:N
/rd:true /f:text` → local, `grep -a`), dmesg (`wsl dmesg` → local).
X11: `wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs
/tmp/.X11-unix` (per run VM). PPM: `wsl python3 t42-cropdiff.py
t35-ref-panel.ppm t35-ref-panel.ppm` → `mean=0.0000 p99=0` (H49 + H50).
Staging: `scp … bytesize:C:/Users/bradr/pcsx2-t4/` →
`wsl cp /mnt/c/… /home/brad/pcsx2-t4/` → `wsl sha256sum` (match) →
`wsl rm` C: files. Probe: `wsl stdbuf -oL -eL t42-probe.sh` (local
redirect). Runs: R1 `wsl stdbuf … t42-auto.sh` (local redirect, NO
dialogwatch — error); R2 same + SEQUENTIAL dialogwatch (error —
guarded nothing); R3 run (short yield → background) → local `sleep 35`
→ `wsl t42-dialogwatch2.sh` (local redirect) → window census
(`wsl sh -c "DISPLAY=:99 xdotool search …"`). Fetch: `wsl cp` snaps →
C: → `scp` (rename `t42-*.jpg` → `t42rN-*.jpg`) → `wsl rm`. Analyze:
`wsl t42-analyze.sh` (census/samples). Trace: `COPYFILE_DISABLE=1 ssh …
'wsl cat …/emulog.txt' > /Volumes/Extreme SSD/ps2x-t4/emulog-t42r3.txt`
(cap 4 GB) → size+sha+head/tail verify. Post-hoc (local): `t41-track.py`
+ `t42-track.py` (dense 12), `/tmp/t42-batch.py` (panels/hops/xrun;
bit-exact 4/4 vs committed), marked-crop montages (`/tmp`, method
tabled). Liveness one-liner (quotable): `wsl python3 -c "import
socket;s=socket.socket(socket.AF_UNIX);s.settimeout(4);s.connect(
'…/PulseServer');print('PULSE_LIVE')"`.

Gaps (tabled, none load-bearing): R2's `t42-poll.log` (R3 overwrote
on-box before fetch — press walls lost, MENU_T+ retained); R2's post-run
dmesg (H49 turnover during analysis gap); R2 analyze skipped
(deliberate — same failure as R1); on-box R1/R2 a2/a3 + a1-poll02-18
stale (deliberate — R3 parked A1); H41 never directly observed (3.5-min
life; disk pins unaffected); H42-teardown gap CLOSED via 250-entry deep
read (13:41:49); no-input floor is a single sample; hold-hop crash
attribution unresolved; d5/d9 in-band off-rider biases (quantified).

## T42-9. Tail receipt (truncated tail FAILS the gate)

T42 executed: ONE retune (smaller ROI x[220,420] y[180,360], frozen
threshold/gate) tabled + calibrated on static snaps BEFORE the run
(reproduction gate 12/12 + 11/11 + 11/11; SCPS control≡retuned 22/22);
T4 build reuse verified on all pins; chain to LIVE gameplay + ONE
1036.5 ms Left hold @T+502.49 on live 5TH/6 + 10-snap blind series at
10×≈0.575 s (R3; R1/R2 environment NO-PARKs, probe-proven mitigation,
corrected parallel protocol); BOTH trackers scored all 12 dense snaps
(control 11/12 flooded — REPEATS T41; retuned 9/12 gated with a
rider-locked pair straddling the hold — the brief's question, YES);
SCPS40 4/11 (hold +13@0.23 off-rail weak) and SCPS120 2/11 strict (hold
+120@0.60 RAIL — unresolved here); full chain/hops/HUD tables in T41's
shapes; trace streamed + verified (2751948037 B, sha MATCH); recipe =
gating PROVEN, motion bounded (lock-QA per pair required; crash
confound; single-sample floor). Evidence: `local/research/T42/`
(STANDALONE: 6 scripts + REPORT + 61 R3 snaps + R1/R2/probe forensics +
logs + census + slices + dmesg/eventlog ×sets). Commit `[T42]` with
trailer `Orchestrated-By: Muse Code`, no push. END-OF-REPORT.







