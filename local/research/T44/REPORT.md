# T44 report — accumulate again (crash-lottery tolerance: stop at first crash-free run)

Brief: T44 (goal: one crash-free T41-shape run scored by ROI + gradient
in parallel; T43 R1 crashed, freezing its Task 1; distributions carried
forward unchanged). Tables, no verdicts.

Carried distributions (DO NOT re-tune, append only):
ROI no-input floor n=3 (cx {+19.7, +1.8, +11.9}, all |cx|<=20, μ=+11.1);
gradient no-input floor n=7 (all |cx|<=20); gradient accumulation pool 10
on→on pairs (|Δcx|<=35, |Δcy|<=29); hold hop n=1 crash-confounded;
d7-class intruder dual-gated VALID, lock-QA-gated, never auto-counted.

Experiment contract (up front): hypothesis — re-running the T43 shape
(same `sleep 0.5` blind cadence, same ≈1037 ms Left hold, same slot)
lands a crash-free hold straddled by an on→on VALID pair under ROI +
gradient in parallel, growing the hold-step distribution toward
separation from the no-input floor; observable — the run chain, the hold
row, the blind 10-snap series + per-snap HUD + all-three-tracker
post-hoc scoring + lock-QA per VALID pair; alternatives — the hold
crashes (→ full 3-row crash receipts + R2 ONCE, same pins), R2 crashes
too (→ freeze Task 1, report both, STOP, no R3), the run never reaches
live (→ environment NO-PARK per T27 §4, bounded re-run); stop — first
crash-free run scored + REPORT, or both runs crash-confounded.

## T44-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T44]`, trailer `Orchestrated-By: Muse Code`, push when done) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; disk
pins taken on VM-H52, VM-independent across turnover):

| Item | T4 value | T44 observed | Match |
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
| T43 reference snaps present | — | on-box `t43-npre1.jpg` 59433 B = committed size (61 `t43-*.jpg` intact; 116 `t42-*.jpg` intact, `t42-npre1.jpg` 53597 B) | yes |
| Free space | — | WSL `/` 902 G avail pre; C: 23 G pre (GATE ~5 GB+ PASSES) | yes |
| Live trace pre-run | — | `emulog.txt` 2789610604 B = T43 R1 (preserved at R1 boot via `emulog-pre-t44-20260921T215827Z.txt`) | yes |
| WSLg audio pre-run | — | socket PRESENT on H52 (informational ONLY — T42 lesson); behavioral gate at boot (modal census, §T44-3) | gate |

Phase-match targets (tabled BEFORE the run — T42 R3's hold window via
T43 R1's; match PHASE not seed; AI lineup/RNG differ run to run):

| Item | Hold-window value (T42 R3 / T43 R1) | T44 hold-window target |
|---|---|---|
| Hold slot | T+502.49 / T+509.34 (keydown) | ≈T+502.5–509.5 (same script slot) |
| Pre-pair race clocks | 00:01:27-ish / 00:01:27 / 00:01:27 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | back-of-pack / front-of-pack | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 36–37% / 43–44% | ≈36–44% ±5 pp |
| Series span | 10 snaps over +7.37–7.40 s wall / +10–11 s race | 10 snaps over ≈+7.4 s wall (same `sleep 0.5` blind capture) |

Same-shape record (tabled BEFORE the run — the deliberate NON-change):

| Item | T43 R1 (`sleep 0.5`) | T44 (this run) |
|---|---|---|
| Dense-phase shape | `sleep 0.5` + capture only; ns wall stamps per snap; ZERO scoring calls | identical (script rename-only, verified: dense span zero scoring calls) |
| Pre-pair gap | `sleep 0.5`, no scoring (measured 0.5818 s) | identical call |
| Hold | ONE `press_hold Left` (1 s `sleep`, T38's body) | identical call, same slot |
| Post-hold | 10 × (`sleep 0.5`, `bsnap d-postN`) | identical calls |
| Dense span (npre1→d-post10) | 7.4022 s wall | ≈7.4 s wall expected |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log | scp via C: staging (T25 recipe) | `t44r2-*.jpg`, `t44r2-poll.log` |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t44-cropdiff.py`, bit-exact validated (T39–T43 protocol); committed tool reproduces any score | screen chain table + xrun frame identities vs T43 R1 |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking, CONTROL | committed `t41-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. Dense 12-snap tracking, ROI | committed `t42-track.py` (frozen, byte-identical) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 6. Dense 12-snap tracking, GRADIENT | committed `t44-track.py` (§T44-1a variant) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 7. View all snaps | local reads | HUD per snap (clock/position/progress/speed/score) |
| 8. Lock-QA every VALID pair | marked-crop montage method (T42) | on/borderline/off + named intruder per snap; on→on distribution |
| 9. Distribution verdict | — | crash-free hold + appended distributions, or crash receipts + recipe |

Brief-vs-REPORT baseline reconciliation (tabled BEFORE the run —
the brief's carried numbers vs the T42/T43-REPORT-derived series; grep
verified over `T41/REPORT.md`, `T42/REPORT.md`, `T43/REPORT.md`):

| Distribution | Brief-carried (T44 §carried) | REPORT-derived (T42 §T42-6 + T43 §§T43-1b,T43-5) | Match |
|---|---|---|---|
| ROI no-input floor | n=3, cx {+19.7, +1.8, +11.9}, μ=+11.1 | n=3, cx {−0.7, +2.8, −4.5} | NO — brief values unprovenanced (no `19.7`/`11.9/` delta in any REPORT; `+1.8` matches gradient's T42 floor Δcx, not an ROI value) |
| Gradient no-input floor | n=7, all \|cx\|<=20 (no values listed) | n=7, cx {+1.8, +0.0, +2.7, −2.1, −7.3, +1.6, −4.7}, all \|cx\|<=20 | YES (count + bound) |
| Gradient accumulation pool | 10 on→on pairs (\|Δcx\|<=35, \|Δcy\|<=29) | 10 = ROI 3 + gradient 7; max \|Δcx\| 7.3, max \|Δcy\| 22.2 | YES (count + bounds) |
| Hold hop | n=1 crash-confounded; T43: ROI +34.3/−25.1 borderline, gradient −71.9/+26.4 off-rider, SCPS40 −40@−0.75, SCPS120 −120@−0.05 | n=1 crash-confounded (T42: ROI +11.2/−39.5, gradient −4.4/−24.1); T43 hold UNGATED under all three (no centroid pair exists); T43 hold SCPS −40@−0.75 / −120@−0.05 | PARTIAL — n-count + SCPS match; T43 centroid deltas (+34.3/−25.1, −71.9/+26.4) unprovenanced (no `34.3`/`71.9` delta in any REPORT; T43's hold has no pair by construction) |
| d7-class intruder | dual-gated VALID, rider-mixed (T42) / off-rider (T43), lock-QA-gated | T42 d7: ROI borderline / gradient on (rider-mixed); T43 d7: off-rider under BOTH (textured tree) | YES |

Disposition: append-only applies to the REPORT-derived series below
(every value reproducible from committed bytes + committed tools —
§T44-1b re-verified them); the brief's unprovenanced values are carried
verbatim above for orchestrator reconciliation and are NOT used as
arithmetic inputs. No re-tune performed.

Distributions to separate (tabled BEFORE the run — REPORT-derived
T42 R3 + T43 R1 baseline):

| Distribution | Tracker | T42 pairs | + T43 R1 pairs | Total in |
|---|---|---|---|---|
| No-input (clean cruise + pre-pair) | ROI | 1 (cx −0.7) | 2 (cx +2.8, −4.5) | 3 |
| No-input (clean cruise + pre-pair) | Gradient | 4 (cx +1.8, +0.0, +2.7, −2.1) | 3 (cx −7.3, +1.6, −4.7) | 7 |
| Hold-step | ROI | 1 (cx +11.2, crash inside) | 0 (hold ungated) | 1, crash-confounded |
| Hold-step | Gradient | 1 (cx −4.4, crash inside) | 0 (hold ungated) | 1, crash-confounded |

## T44-1. Rename audit + control scoring (T44 tools, pre-run)

### T44-1a. Rename audit (T43's six scripts → `t44-*`)

| Item | Value |
|---|---|
| `t44-auto.sh` diff vs `t43-auto.sh` | 488 diff lines: 484 contain `t43-`/`t44-`/`T43`/`T44`; 4 are the §step-2 log-path fix (`xvfb-t43.log`→`xvfb-t44.log`, `boot-t43.log`→`boot-t44.log`, `boot-t43.stdout`→`boot-t44.stdout` — `t43.`→`t44.` dot-tokens, the T43-found rename miss, FIXED pre-run so R1 cannot overwrite T43's on-box boot logs); `bash -n` clean; zero `sham` refs; exactly one `press_hold Left`; dense block zero scoring calls; `sleep 0.5` count 14 = T43's 14; sha `a3acb2d6…54e9cb` |
| `t44-analyze.sh` | output-name deltas only (`t44-census/samples`), 6/6 diff lines dash-tokened, sha `bf966f02…6ae966`; `bash -n` clean |
| `t44-vcount.sh` | byte-identical to T43's (`cmp` clean), sha `105cd092…39107d76`; `bash -n` clean |
| `t44-cropdiff.py` | byte-identical to T43's (`cmp` clean), sha `ac114212…0826a53` |
| `t44-dialogwatch2.sh` | byte-identical to T43's v2 (`cmp` clean), sha `d9c7a4c1…41faa` (zero `t43` refs — generic); `bash -n` clean |
| `t44-track.py` | header/usage renames ONLY (8/8 diff lines tokened); token-normalized `diff` vs `t43-track.py` clean = FUNCTIONALLY IDENTICAL; sha `cb56c827…fcbd0d` (4323 B) |
| Residual `t43`/`T43` refs in `T44/` | ZERO (`grep` clean) |
| `post43`→`post44` label drift | 2 comment/log-string lines (`post43->stab1`, `post43-stab1=` — the `43`→`44` sed also rewrites the `post43` hop label; behavior-neutral log sink, same class as T42→T43's `post42`→`post43`) |
| Frozen trackers byte-identical | `t41-track.py` `58afa004…`, `t42-track.py` `a951f782…`, `t43-track.py` `2e532a2d…` (first-8 reproduce the brief); T43 dir read-only reference, untouched |
| Staged shas | all 5 WSL-staged shas match local (auto `a3acb2d6…`, analyze `bf966f02…`, vcount `105cd092…`, cropdiff `ac114212…`, dialogwatch2 `d9c7a4c1…`) |
| PPM self-check | panel ref 0.0000/0 on H52 pre-run (`mean=0.0000 p99=0 max=0 npix=224000 mode=PPM`) |
| T41/T42/T43 originals | untouched (tracked tree clean at commit; T44 dir is new) |

### T44-1b. Control scoring (T44 tools on T42 R3 + T41 R4 committed bytes)

| Check | Result |
|---|---|
| `t41-track.py` on T41 R4 12 snaps vs T41 §hold table | 12/12 RDC + 11/11 SCPS40 + 11/11 SCPS120 reproduce EXACTLY (corr to 4 dp) = 34/34 — environment/decoder sound |
| `t42-track.py` on T41 R4 12 snaps vs T42 §T42-1 calibration | 12/12 RDC (cx/cy/npix/gate) reproduce EXACTLY (1319/2534/3655/3926/3158/1450/1138/2265/2091/1219/3771/12609-INVALID) |
| `t42-track.py` RDC on T42 R3 12 snaps vs T42 §T42-6 retuned column | 12/12 reproduce EXACTLY (incl. hold-straddling pair values) |
| `t44-track.py` on T42 R3 12 snaps vs T43 §T43-1b gradient calibration | 12/12 RDC reproduce EXACTLY (928/1027/2252/4448-INVALID/2046/1993/845/1271/1176/1069/1171/1824 + centroids to 1 dp) |
| `t44-track.py` on T41 R4 12 held-out snaps vs T43 §T43-1b held-out | 12/12 npix+gate reproduce EXACTLY (893/1521/2073/1936/1739/976/794/1114/1273/891/1409/1433, all VALID) |
| `t43-track.py` vs `t44-track.py` outputs on T42 R3 | BIT-IDENTICAL (`cmp` clean) |
| SCPS 3-way (`t41` vs `t42` vs `t44`) on T42 R3 | 22/22 lines bit-identical (`cmp` clean); hold rows +13 @ 0.23 / +120 @ 0.60 exact; SCPS40 rails 4/11; SCPS120 strict rails 2/11 |
| SCPS 3-way on T41 R4 | 22/22 lines bit-identical (`cmp` clean) |
| `t41-track.py` RDC on T42 R3 (stale-cell check) | reproduces T43's CORRECTED record exactly (11/12 INVALID + npre2 singleton VALID; e.g. npre1 381.2/245.9/12942) — the stale T42 frozen-exact cells stay stale (T42 REPORT untouched, per brief) |
| SCPS on T42 R3 middle rows (stale-cell check) | reproduces T43's re-scored middle rows (d2d3–d6d7), NOT T42's tabled values — the stale T42 middle-SCPS cells stay stale (untouched, per brief) |
| T43-E1 errata close-out | `t44-track.py` (and `t43-track.py`) on committed `t43r1-npre2.jpg` give 372.4/229.6 npix=5 INVALID — the re-run value, NOT the errata'd 343.5/189.2; classification identical (INVALID), snap excluded either way — no verdict impact |

## T44-2. Session log (H52 → H53 → H54 → H55 → H56, then outage wait)

Clocks: WSL `date -u` true UTC; `wevtutil` renders local-as-Z (+4 h →
UTC); H-numbers continue T43's H51.

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 21:56:33 ([0] VM-H52) | H52 demand-boot (WSL fully Stopped at session start) | btime 1790027793 |
| 2 | 21:56–21:58 | Pins (binary/tree/inputs/NVM/bindings/9 refs/T43 snaps/live trace/C:/socket-present-informational) | §T44-0 table |
| 3 | 21:57–21:58 | Staging (5 files, shas match) + X11 tmpfs mount (root) + PPM 0.0000/0 + dmesg-pre + eventlog-pre | `t44-dmesg-h52-pre.txt` (441 lines, 0 AcceptAsync); eventlog-pre 120 entries |
| 4 | 21:58:21–22:01:59 ([108]→[326] H52) | R1: A1 title-detect @poll01 → menus → SC → NO-ZC-PARK (slow character load), `T44_DONE`, exit 0 — environment abort, NOT an attempt on the question | stdout 143 lines, stderr 883 lines, poll log 62 lines, 17 abort snaps |
| 5 | 21:59:27 (T+60.2) | Dialogwatch v2a: SKIP-GAME 2097159 + DISMISS 2097162 `pcsx2-qt` + DISMISSED-EXIT (no modal; R3 pattern) | `t44r1-dialogwatch.txt` |
| 6 | ~T+97 | Window census: game 2097159 present, no `Error` modal → no v2b | census output |
| 7 | 22:02–22:08 | R1 abort forensics (viewed poll01/zc-post1/zc-post3; cubeb grep on partial trace) + abort-evidence fetch (17 JPGs + poll log, C: cleaned) | files below; §T44-3 |
| 8 | ~22:05:49 | H52 teardown (NOT by me — idle gap; WSL Stopped) → H53 (btime 1790028349), audio DOWN (no PulseServer) | socket checks |
| 9 | 22:08–22:10 | H53 pins (binary/NVM/staged shas persist — all match) + H53 dmesg + R1-audio-healthy receipt (6 cubeb lines, 0 null-fallback) | `t44-dmesg-h53-audiodown.txt` (491 lines) |
| 10 | 22:10 | `wsl --shutdown` BY ME (clean, rc=0 — audio-recovery attempt; tabled, justified) → H54 (btime 1790028496), audio DOWN | socket checks |
| 11 | 22:10–22:12 | H54 WSLg inspection (weston/Xwayland up, NO pulse leg) + host audio check (6 sound devices, all OK → WSLg defect, T42 signature) + H54 dmesg | `t44-dmesg-h54-audiodown.txt` (453 lines) |
| 12 | 22:12 | `wsl --shutdown` BY ME (clean, rc=0) → H55 (btime 1790028557), audio DOWN (immediate + delayed @uptime 40) | socket checks + `t44-dmesg-h55-audiodown.txt` (445 lines) |
| 13 | 22:14 | `wsl --shutdown` BY ME (clean, rc=0) + 60 s cold wait (WSL fully Stopped) → H56 demand-boot (btime 1790028685), audio DOWN (@uptime 34) | socket checks + `t44-dmesg-h56-audiodown.txt` (445 lines) |
| 14 | 22:16 | `wsl --shutdown` BY ME (clean, rc=0); WSL left Stopped for outage wait (T42 precedent: bounces don't recover it, time+turnover does; `sc` bounce NOT repeated — T42 already ran that experiment negative) | — |
| 15 | 22:16–22:22 | Outage wait #1 (WSL Stopped ~6 min) + local work (REPORT draft §§T44-0–T44-3; R1 forensics; T43-E1 close-out) | this file |
| 16 | 22:22 | H57 demand-boot (btime 1790029333), audio DOWN (@uptime 35) — 5th consecutive down boot | socket checks + `t44-dmesg-h57-audiodown.txt` (438 lines) |
| 17 | 22:23 | `sc stop/start WslService` BY ME (STOPPED clean → START_PENDING; T42-precedented second recovery lever — T42's instance ran negative, repeated here as a different layer than `--shutdown`) | sc output |
| 18 | 22:23–22:40 | Outage wait #2 (15+ min, WSL down; local work: pre-run tables §§targets/shape/plan/distributions + brief-vs-REPORT reconciliation) | this file |
| 19 | 22:41 | H58 demand-boot (btime 1790030458), audio DOWN (@uptime 35 + recheck @68: no PulseServer, no `runtime-dir/pulse/`, no pulseaudio.log — full T41 signature) — 6th consecutive down boot, ~36 min outage | socket checks + `t44-dmesg-h58-audiodown.txt` (446 lines) |
| 20 | 22:42 | STALL: all recovery levers exhausted (table §T44-4); R2 NOT RUN; recipe returned to orchestrator; evidence committed `[T44]` + pushed | this file |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` (as root, T4 recipe) on H52 pre-R1; does not persist reboot (re-landed per run VM) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by R1 (dead with H52) |
| Dirs/files created | `/home/brad/pcsx2-t4/t44-{auto,analyze,vcount,cropdiff}.sh/.py`, `t44-dialogwatch2.sh`, `t44-*.jpg/.ppm/.log` (R1 abort set: 17 JPGs + PPMs), `…/logs/emulog-pre-t44-20260921T215827Z.txt` (T43R1's trace, 2789610604 B), `C:\Users\bradr\pcsx2-t4\t44*` staging (removed after each batch) |
| Dirs/files OVERWRITTEN | NONE this session (the `t44.` log-path fix held: `logs/boot-t42.log`/`.stdout` still hold T43 R1's content; R1 wrote `logs/boot-t44.log`/`.stdout`) |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| Restarts by me | 4× `wsl --shutdown` (all clean rc=0: 3 audio-recovery + 1 pre-wait; tabled, justified — T42 precedent) |
| VM restarts (not by me) | H52 teardown (idle gap ~22:05) |

## T44-3. R1 — environment NO-PARK at SC→ZC (not an attempt on the question)

R1 booted on VM-H52 (T_BOOT 1790027907, uptime 114; 21:58:27 UTC) under
HEALTHY audio (cubeb-pulse negotiated [0.5563/0.5679/0.5681], zero
null-fallback lines in the 1.22 GB partial trace, clean stop/destroy at
shutdown [201.99/202.03]; TRUE TITLE viewed on a1-poll01 with no modal;
v2a R3-pattern + game-only census) and ran the chain through SC before
the ZC gate refused the park: the Setup Character screen arrived late
(character model still loading at +1 s), so the p1-p3 whole hop
(1.7110) exceeded the static threshold (mean < 1.0). `NO-ZC-PARK`,
`T44_DONE`, exit 0, clean shutdown at uptime 326 (T+212). 143-line
stdout / 883-line stderr. WID 2097159 (same as T31–T43).

| Item | Value |
|---|---|
| R1 window | 21:58:27–22:01:59 UTC (T+0–212), VM-H52 uptime 114→326 |
| Dialogwatch v2 | ROUND:1 @T+60.2: SKIP-GAME 2097159 + DISMISS 2097162 `pcsx2-qt` + DISMISSED-EXIT (main-window, inert — R3 pattern; NO modal existed to dismiss; window census ~T+97: game-only, no modal) → no v2b |
| Title detect | A1 `poll01` remote 0.4379/5 (PIL TBD post-hoc) — parked FIRST attempt (a2/a3 never ran; no stale) |
| Presses | 4 menu/Start Cross (all 533.6–534.4 ms); ZERO other game inputs (4 KEYDOWN/KEYUP pairs in the 62-line poll log) |

### R1 press log (poll-log walls; T+ = wall − 1790027907)

| Press | Keydown wall (T+) | Keyup wall (T+) | Width |
|---|---|---|---|
| A1 Cross (attract-skip) | 1790028005.645 (T+98.65) | 1790028006.178 (T+99.18) | 533.6 ms |
| A1 Start (on title) | 1790028008.920 (T+101.92) | 1790028009.454 (T+102.45) | 534.4 ms |
| MENU Cross (Single Event) | 1790028048.101 (T+141.10) | 1790028048.636 (T+141.64) | 534.4 ms |
| ZOE Cross | 1790028088.304 (T+181.30) | 1790028088.838 (T+181.84) | 534.0 ms |

### R1 ZC-gate forensics (the refusal)

| Hop / snap | Value | Gate leg |
|---|---|---|
| scpre→zc-post1 whole | 7.8218 | DEPARTED (> 5.0) ✓ |
| zc-post1 vs-sc | 7.8594/112 | non-SC ✓ |
| zc-post1 vs-zc | 1.8755/82 | mid-transition (viewed: empty Setup Character — mountain, no Zoe, no menu items; model still loading) |
| zc-post1→zc-post3 whole | 1.7110 | arrival-static (< 1.0) ✗ — THE REFUSAL |
| zc-post3 vs-zc | 0.5203/10 | parked (viewed: Zoe + Continue/Equip Gear/Rider Details/Music) |
| zc-post3→zc-post8 whole | 0.2556 | static ✓ (screen DID park — the gate's p1-p3 leg just couldn't span the slow load) |
| zc-post8 vs-zc | 0.4260/7 | parked ✓ |

T43 R1 comparison: its zc-post1 vs-zc was 0.5106/8 (model already
loaded at +1 s); T44 R1's character load arrived between +1 s and +3 s.
Transient load-timing jitter; the gate behaved correctly. Per T42's
rule this run is not an attempt on the question → bounded re-run as
R2 (next audio-healthy VM).

### R1 abort snaps (17 fetched + poll log; sizes = on-box bytes)

| Snap | Size | Content (viewed: poll01, zc-post1, zc-post3; rest per scores) |
|---|---|---|
| start | 50238 | attract (remote 11.9612/142) |
| a1-now | 58336 | attract (remote 11.8076/123) |
| a1-poll01 | 58424 | TRUE TITLE (viewed; remote 0.4379/5) |
| a1-pre | 58424 | = poll01 (cp-identical size) |
| a1-post3/8/15/25 | 50267/49639/49852/49856 | Main Menu (remote 16.30–16.24/139, static hops 0.0179/0.0393) |
| menupre | 49878 | Main Menu (remote vs-menu 0.3009/5) |
| mc-post1/3/8/15 | 70340/70080/70457/70516 | Select Character (vs-sc 0.42/0.40/0.62/0.45) |
| scpre | 70473 | Select Character (vs-sc 0.4438/7) |
| zc-post1 | 42441 | Setup Character EMPTY, model loading (viewed; vs-zc 1.8755/82) |
| zc-post3 | 51667 | Setup Character PARKED with Zoe (viewed; vs-zc 0.5203/10) |
| zc-post8 | 51459 | Setup Character parked (vs-zc 0.4260/7) |

## T44-4. WSLg-audio outage + STALL (R2 not run; recipe returned)

### Outage table (6 consecutive audio-down boots after healthy H52)

| VM | btime | Socket checks | dmesg | Note |
|---|---|---|---|---|
| H52 | 1790027793 | PRESENT (pre-run) | 441 lines, 0 AcceptAsync | HEALTHY — R1 ran, cubeb-pulse negotiated, no modal |
| H53 | 1790028349 | absent | 491 lines | post-turnover; pins persist-OK; R1-audio-healthy receipt taken here |
| H54 | 1790028496 | absent (immediate + delayed @26) | 453 lines | WSLg inspected: weston/Xwayland up, NO pulse leg; host 6/6 sound devices OK → WSLg defect (T42 signature) |
| H55 | 1790028557 | absent (immediate + delayed @40) | 445 lines | post-`--shutdown` |
| H56 | 1790028685 | absent (@34) | 445 lines | post-`--shutdown` + 60 s cold wait (WSL fully Stopped, H51-like pre-state) |
| H57 | 1790029333 | absent (@35) | 438 lines | post-6-min stopped wait; `sc` bounce follows |
| H58 | 1790030458 | absent (@35 + @68; no PulseServer, no `runtime-dir/pulse/`, no pulseaudio.log) | 446 lines | post-`sc` bounce + 15-min stopped wait |

### Recovery levers attempted (all tabled, all negative)

| Lever | Precedent | Result |
|---|---|---|
| `wsl --shutdown` ×3 + demand-boot (H54/H55/H56, incl. 60 s cold Stopped) | T42 (negative there too) | next boots STILL down |
| Outage wait #1 (WSL Stopped ~6 min) → H57 | T42 (time+turnover recovered H49) | STILL down |
| `sc stop/start WslService` (STOPPED clean → START_PENDING) | T42 (negative) | — (leads into wait #2) |
| Outage wait #2 (WSL down 15+ min) → H58 | T42 (~36 min outage cleared) | STILL down at the 36-min mark |
| `sc` bounce repeat / host reboot / host audio-service bounce | — | NOT attempted (host-wide; no lane authority — orchestrator options) |
| User-distro null-sink pulseaudio (satisfy cubeb without WSLg) | NONE (new environment deviation: install + daemon + audio-path change on the measurement critical path) | NOT attempted (needs orchestrator approval — proposed below) |
| Boot the run on a down VM (behavioral probe) | — | NOT attempted (`run boots ONLY on an audio-healthy VM`; absent⇒modal established n=2 in T41 — zero information gain) |

### Stall disposition (no verdicts; recipe returned)

| Item | Value |
|---|---|
| R2 | NOT RUN — blocked on the outage (no audio-healthy VM in 6 boots / ~36 min) |
| R1 | Environment NO-PARK (§T44-3) — not an attempt on the question; does NOT consume the crash-lottery budget |
| Crash-lottery budget | UNSCATHED (0 live runs this session) — R2 + the recipe's crash branches remain for the re-drive |
| Task 1 | Still frozen from T43 (no new samples banked); freeze neither lifted nor extended |
| Distributions | Unchanged (REPORT-derived series §targets; brief-unprovenanced values flagged, not used) |
| Re-drive recipe | On the next audio-healthy VM: re-pin the T43 way (btime/binary/tree/NVM-mtime/bindings/staged-shas/C:/socket) + X11 tmpfs + PPM 0.0000/0 + dmesg/eventlog pre; verify `t44.` boot logs exist from R1 (`logs/boot-t44.log`/`.stdout` — R1's content; R2 OVERWRITES them, so fetch R1's FIRST if forensics are wanted — NOTE: not yet fetched, tabled as gap); launch R2 (background → sleep 35 → v2a → census); on live reach: full T44 recipe (score 3 trackers, lock-QA, REPORT R2 sections, commit `[T44r2]`) |
| Orchestrator options | (a) re-drive T44-R2 in a fresh session when WSLg audio recovers; (b) approve/decline the null-sink pulseaudio experiment (deviation from the T4→T43 audio environment — table as variant if approved); (c) host-side recovery (reboot/audio-stack — lane has no authority) |

## T44-5. Exact commands (reproduce-from-scratch)

Pre-run pins (one `wsl` call per ssh; single-quote outer, double-quote
inner — the remote shell is PowerShell: bare `;`/`|` break):
`ssh bytesize 'wsl bash -c "…"'` for btime/uptime (boot), `sha256sum` +
`stat` (binary), `git -C pcsx2 rev-parse HEAD` + `status --short`
(tree), `ls -la inputs/`, `sha256sum` + `stat` (live NVM
`dat/PCSX2/bios/ps2-bios-0200a-20040614-100909.nvm`), `grep -n
Cross/Left` (bindings), 9-ref `sha256sum`, T43 snap `ls` (spot size +
counts), live-trace `ls`, `df -h /` + `/mnt/c`, `ls
/mnt/wslg/PulseServer` (informational only), dmesg (`wsl dmesg` →
local), eventlog (`wevtutil qe System /c:120 /rd:true /f:text` →
local).
X11: `wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs
/tmp/.X11-unix`. PPM: `wsl python3 t44-cropdiff.py t35-ref-panel.ppm
t35-ref-panel.ppm` → `mean=0.0000 p99=0`.
Staging: `scp … bytesize:C:/Users/bradr/pcsx2-t4/` →
`wsl cp /mnt/c/… /home/brad/pcsx2-t4/` → `wsl sha256sum` (match) →
`wsl rm` C: files.
Run: `ssh bytesize 'wsl bash -c "cd /home/brad/pcsx2-t4 && stdbuf -oL
-eL ./t44-auto.sh"'` (local redirect, managed background) → local
`sleep 35` → `wsl t44-dialogwatch2.sh` (local redirect) → window census
(`DISPLAY=:99 xdotool search --onlyvisible --name SSX/Error`).
Fetch (abort set): `wsl cp` 17 JPGs + poll log → C: →
`scp 'bytesize:C:/Users/bradr/pcsx2-t4/t44-*'` (glob — multi-arg scp
misparses on macOS) → rename `t44-*` → `t44r1-*` → `wsl rm`.
Post-hoc (local): `t41-track.py` + `t42-track.py` + `t44-track.py`
(control sets), `t43-track.py` (identity check), viewed snaps (local
reads), `grep Cubeb/null-fallback` on the on-box partial trace.
Recovery: `wsl --shutdown` (rc=0) → demand-boot → socket recheck
(immediate + delayed @25–70 uptime); `sc stop/start WslService`;
host audio `powershell Get-CimInstance Win32_SoundDevice`.

Gaps (tabled, none load-bearing for the stall): R1's on-box boot logs
(`logs/boot-t44.log`/`.stdout`) not yet fetched (R2 overwrites them —
fetch FIRST on re-drive); R1's partial trace (1.22 GB) never streamed
(only cubeb greps — the full stream is pointless for a menu abort);
interpolated T+ on R1 chain snaps (±1 s; scored anchors exact);
eventlog-final not taken (session ends mid-outage — next session takes
fresh pre); H52 post-R1 dmesg MISSED (turnover before capture —
T42-R2-class receipt gap); hold-step distribution still n=1
crash-confounded (no live run banked); no-input floor still ROI n=3 /
gradient n=7 (no live run banked); brief-vs-REPORT baseline mismatch
(§reconciliation — orchestrator to resolve provenance).

## T44-6. Tail receipt (truncated tail FAILS the gate)

T44 executed through the stall: rename audit (6 scripts: 484/488
dash-tokened diff lines + the 4-line `t43.`→`t44.` log-path FIX
pre-landed; `bash -n` clean ×4; zero `sham`; one `press_hold Left`;
14× `sleep 0.5`; 3 byte-identical tools; track functionally identical;
frozen shas reproduce; staged shas match; PPM 0.0000/0) + control
scoring (T41 34/34 exact; T42-calib 12/12; retuned 12/12; gradient
calib 12/12; held-out 12/12; T43-vs-T44 bit-identical; SCPS 3-way
22/22 on both sets; stale T42 cells stay stale; T43-E1 closed out) +
pre-run tables (targets/shape/plan/distributions + brief-vs-REPORT
reconciliation: ROI-floor and T43-hold-delta values unprovenanced —
flagged, REPORT-derived series carried) + R1 (NO-ZC-PARK environment
abort on healthy H52: slow Zoe load, p1-p3 1.7110 ≥ 1.0, gate correct;
cubeb-healthy + TRUE TITLE viewed; 17 abort snaps + 62-line poll log
fetched) + outage (6 consecutive audio-down boots H53–H58 over ~36 min,
host 6/6 OK → WSLg defect; shutdowns/cold/sc-bounce/waits all negative;
R2 NOT RUN — crash budget unscathed, Task 1 still T43-frozen, recipe
returned). Evidence: `local/research/T44/` (6 scripts + REPORT + R1
abort set + logs + dmesg ×7 + eventlog-pre; no census/samples — no
live run reached the analyze phase). Commit `[T44]`
with trailer `Orchestrated-By: Muse Code`, push. END-OF-REPORT.
