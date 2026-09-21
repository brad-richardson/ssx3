# T41 report — sub-second `sleep 0.5` blind cadence around the 1 s hold: does SCPS40 resolve the hold hop? (bytesize, no lease)

Brief: T41 (T40's G1, first arm only: sub-second `sleep 0.5` blind
cadence, NOT the ROI retune). Tables, no verdicts. Four boots ran on
bytesize (R1/R2: environment NO-PARKs — WSLg-audio-down cubeb modal;
R3: game-side NO-SP-PARK; R4: full chain + ONE 1 s hold + blind
10-snap series at ≈0.57 s exposures, scored post-hoc); laptop-side work
was ssh/scp + local reads/analysis only. Time box 4 h (+ T41F finish
session post-restart: verify + SSD stream + tables, no new run).

Supersession note: the §T41-9 wrap note committed pre-restart
(`64d252e`) is superseded by T41-1…T41-8 below; every core fact it
stated is retained in tables. No number moves (no errata table); one
receipt-status note on R3's parallel Start lives in §T41-4.

Stale-reading guard: `local/research/T40/REPORT.md` (all of it: R1
DISCARDED (C:-full guest wedge at T+185 — environment failure, full
forensics + C: fix: cleared 20 stale emulog transfer copies ~30 GB, C:
116 KB → 29.1 GB; C: headroom ~5 GB+ is now a pre-run gate); R2 reproduced
the chain to LIVE gameplay, ONE 1038.0 ms D-pad Left hold @T+503.09 on a
live race (pre-pair 00:01:28 6TH/6 36% / 00:01:29 6TH/6 36%), blind
back-to-back 10-snap series at ≈1.07 s exposures scored post-hoc to
00:01:46 6TH/6 41%: SCPS120 railing drops 7/11 → 3/11 with the hold hop
RESOLVED (+49 @ 0.79 — first resolved input hop in T36–T40), SCPS40 rails
4/11 INCLUDING the hold hop (+40 @ 0.74), RDC gated out 10/12 with no gated
pair straddling the hold; G1 proposes ONE variant — this brief takes the
`sleep 0.5` arm, NOT the ROI retune). This brief executes T40's G1 (first
arm only). T40's scripts reused (copied, not modified).

Experiment contract (up front): hypothesis — T40's ≈1.07 s blind exposures
resolved the hold hop at SCPS120 (+49 @ 0.79) but SCPS40 still railed it
(+40 @ 0.74), so halving the dense-phase cadence (`sleep 1` → `sleep 0.5`,
still blind, capture-bound at ~70 ms + scheduler) yields ≈0.6 s exposures
where SCPS40 resolves the hold hop too and a gated RDC pair can straddle
it; observable — pre-hold pair = live race (race clock + position/progress
HUD read off the viewed snaps), the hold row (proven 1 s keydown→keyup +
phase match vs T40's hold), dense 10-snap series + per-snap HUD + tracking
metrics + per-hop whole diffs, all scored post-hoc from fetched snaps;
screen content read off viewed snaps; alternatives — SCPS40 still rails
the hold hop / RDC still floods at ≈0.6 s exposures (→ table the exact
observed rates + noise floors and STOP with a recipe), run provably never
reached live gameplay at a matched phase (→ ONE bounded re-attempt
allowed); stop — table the rail-rate comparison vs T40 + gated-pair
verdict + recipe, one input variant per attempt, never blind multi-presses.

## T41-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T41; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T41]` finish, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; verified
on VM-H32 before R1):

| Item | T4 value | T41 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Pad binding (Left) | — | `Left = Keyboard/Left`, `PCSX2.ini:576` (the hold key; T38's binding re-verified) | yes |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…580eb6` reproduces T35 | yes |
| T40 reference snaps present | — | all 12 sizes reproduce T40 §chain (`npre1/2` 52069/50992, `d-post1..10` 48456/51050/57207/53965/56852/50871/54132/53532/59421/62473) | yes |
| Free space | — | WSL `/` 867 G pre; C: 27 G pre (GATE ~5 GB+ PASSES — no wedge risk); laptop `/` 11 Gi avail; SSD 237 Gi free | yes |
| Live trace pre-run | — | `emulog.txt` 2782052936 B sha `6fb03830…a367c` = T40 R2 (preserved at R1 boot) | yes |

Post-restart (T41F) re-verify — every pin + input ref re-checked on a
fresh post-restart VM; drift tabled (drift does not invalidate the
committed R4 snaps/scores, which are immutable):

| Item | Pre-run value | T41F re-verify | Drift |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | none |
| Binary size | 130929856 B | 130929856 B | none |
| Tree rev / status | `9056c08349…95af` / clean | same rev, empty `status --short` | none |
| Inputs (ISO + BIOS trio) | 3005415424 / 4194304 / 4 / 1024 | same sizes | none |
| NVM sha / mtime | `da021d2a…` / Sep 20 15:20 | same sha, `2026-09-20 15:20:11 -0400` | none |
| Pad bindings | `:576` Left, `:579` Cross | `576:Left = Keyboard/Left`, `579:Cross = Keyboard/K` | none |
| 9 ref PPM shas | T27–T35 pins (§T41-0) | all 9 full shas reproduce exactly | none |
| T40 ref snaps | 12/12 sizes (§T41-0) | 4/4 spot-check sizes reproduce (`npre1/2` 52069/50992, `d-post1/10` 48456/62473) | none |
| Staged `t41-*.sh/.py` shas | match local at stage time | all 4 match committed (`auto 4533904a…`, `analyze 0b0cc435…`, `vcount 105cd092…`, `cropdiff ac114212…`) | none |
| WSL `/` avail | 867 G | 859 G | −8 G (4 runs' VHDX growth; expected) |
| C: avail | 27 G | 18 G | −9 G (VHDX growth; gate ~5 GB+ still PASSES) |
| `…/logs/` size | ~43 G (T40 final) | 51 G (33 emulogs: T17→T41 chain + 4 T41 rotations) | +8 G (4 T41 traces; expected) |
| SSD avail | 237 Gi | 236 Gi | −1 Gi (this session's R4 stream 2.7 GB; expected) |
| Live trace = R4 original | 2745300674 B `5b0a7349…53d3f` | same size + full sha `5b0a734900d41722718155925fecd1deffa879aeb7852cad69c7bcf198853d3f` + head/tail slices match committed | none |

Phase-match targets (tabled BEFORE the run — T40 R2's hold window, match
PHASE not seed; AI lineup/RNG differ run to run):

| Item | T40 hold-window value | T41 hold-window target |
|---|---|---|
| Hold slot | T+503.09 (keydown) | ≈T+502.5 (same script slot; ≈0.5 s earlier from shorter pre-pair gap) |
| Pre-pair race clocks | 00:01:28 / 00:01:29 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | 6TH/6 / 6TH/6 | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 36% / 36% | ≈36–45% (±5 pp) |
| Series span | 10 snaps over +11.8 s wall / +17 s race | 10 snaps over ≈+7 s wall (shorter: `sleep 0.5` blind capture) |

Blind-capture cadence (tabled BEFORE the run — the deliberate change):

| Item | T40 (blind `sleep 1`) | T41 (blind `sleep 0.5`) |
|---|---|---|
| Dense-phase shape | `sleep 1` + capture only; ns wall stamps per snap; ZERO scoring calls | `sleep 0.5` + capture only; ns wall stamps per snap; ZERO scoring calls |
| Expected exposure gap | ~1–2 s (measured 10 × 1.071–1.074 s) | ~0.5–0.7 s (0.5 s sleep + ~70 ms snap overhead + scheduler; measured post-hoc from ns stamps) |
| Pre-pair gap | `sleep 1`, no scoring (measured 1.074 s) | `sleep 0.5`, no scoring (≈0.6 s expected) |
| Hold-hop span | hold 1.038 s + `sleep 1` + overhead (measured 2.111 s) | hold ≈1.04 s + `sleep 0.5` + overhead (≈1.6 s expected) |
| Dense span (npre1→d-post10) | 12.90 s wall | ≈7.9 s wall expected |
| Run length | T40 R2 524 s | shorter by ≈5.5 s (11 × 0.5 s saved); delta tabled |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps
with the committed tools):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log | scp via C: staging (T25 recipe) | `t41r4-*.jpg`, `t41r4-poll.log` (+ R1/R2/R3 forensics subsets) |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t41-cropdiff.py`, bit-exact validated 4/4 (T39/T40 protocol); committed tool reproduces any score | screen chain table + xrun frame identities vs T40 R2 |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking | committed `t41-track.py` (byte-identical to T40's = T38's frozen) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. View all snaps | local reads | HUD per snap (clock/position/progress/speed/score) |
| 6. Rail-rate comparison | — | RDC gate-out / SCPS40 / SCPS120 rates vs T40 + gated-pair verdict |

Rail rates to beat (tabled BEFORE the run — T40 R2 hold dense phase,
12 snaps / 11 hops at ≈1.07 s):

| Metric | T40 (1038.0 ms hold, ≈1.07 s gaps) | T41 question |
|---|---|---|
| RDC gated out | 10/12 | does any gated pair now straddle the hold? |
| SCPS40 rails | 4/11 (INCL the hold hop +40 @ 0.74) | does the hold hop resolve at ≈0.6 s? |
| SCPS120 rails | 3/11 (hold hop RESOLVED +49 @ 0.79) | stays resolved? |
| Input-hop SCPS40 | +40 @ 0.74 RAIL | resolved or still railed? |
| Dense whole-hop range | 6.72–16.60 | motion-class floor at ≈0.6 s? |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) on VM-H32 pre-run; re-landed per fresh VM by the pre-run routine (H34/H35/H36); R1/R2/R3/R4 each started Xvfb `:99 -screen 0 1280x1024x24` detached by the script (`pkill` + `setsid nohup`) and exited 0 — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 – T40 G11 stand) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by each run |
| Dirs/files created | `/home/brad/pcsx2-t4/t41-{auto,analyze,vcount,cropdiff}.sh/.py`, `t41-dialogwatch.sh`, `t41-dialogwatch2.sh`, `t41-{r1,r4-census,samples}.txt` (via analyze; R2/R3 analyze not run — no census committed), `t41-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t41-*.txt` (4-file rotation chain, see trace table), `boot-t41.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t41*` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | pre-run section below; ZERO in-window (see WSL session log) |

Script receipts (frozen BEFORE the run; staged shas re-verified
post-restart — match):

| Item | Value |
|---|---|
| `t41-cropdiff.py` | byte-identical to T40's (`cmp` clean), sha `ac114212…0826a53` |
| `t41-track.py` | byte-identical to T40's (`cmp` clean), sha `58afa004…91c108` (T38's frozen value) |
| `t41-vcount.sh` | byte-identical to T40's (`cmp` clean), sha `105cd092…39107d76` |
| `t41-analyze.sh` | output-name deltas only (`t41-census/samples`), sha `0b0cc435…bc2a655` |
| `t41-auto.sh` | T40 copy + T41 renames + comment updates + 11 × `sleep 1` → `sleep 0.5` in the dense phase (ONLY code change), sha `4533904a…b6b727d`; `bash -n` clean; zero `sham` references; exactly one `press_hold Left` call; dense block contains zero scoring calls; one inert cosmetic label (`post41-stab1` plog string @L796 — the computed hop uses post40 files; remote value unaffected) |
| `t41-dialogwatch.sh` (v1) | environment-hygiene helper (NOT part of the experiment script): polls Xvfb :99 from a second ssh session, Returns any non-SSX window; sha `158842d4…286ccf`; carries the v1 root-dismiss bug (found on R3) |
| `t41-dialogwatch2.sh` (v2) | same role; skips root by geometry + game by name; sha `d9c7a4c1…41faa` |
| Staged shas | all 4 WSL-staged shas match local pre-run AND post-restart (auto `4533904a…`, analyze `0b0cc435…`, vcount `105cd092…`, cropdiff `ac114212…`) |
| PPM self-check | panel ref 0.0000/0 pre-run; all 11 in-script self-tests 0.0000/0 every run |
| T40 originals | untouched (tree clean at commit; T41 dir is new) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 12:46:03 ([0] VM-H31) | H31 create (T40's post-everything VM) | eventlog-pre (IDs 292/67/291/233/232/102/291/291 @08:46:03) |
| 2 | 12:48:50 | H31 teardown (pre-session restart, NOT by me) | eventlog-pre (IDs 71/69/233/234/234 @08:48:50) |
| 3 | 13:44:29 ([0] VM-H32) | VM-H32 started fresh ~3 min before pre-run checks | btime-derived, eventlog-pre (IDs @09:44:29) |
| 4 | 13:44–13:47 | Pre-run checks (§T41-0 pins + C:-staging + WSL-staging (shas match local) + X11 mount + PPM self-check 0.0000/0, all on VM-H32 | `t41-dmesg-h32-pre.txt` (0 AcceptAsync, 416 lines) |
| 5 | 13:47:20–13:51:39 ([171]→[430] H32) | R1: 3 attempts, cubeb modal on EVERY snap, NO-PARK, T41_DONE exit 0 | poll log 98 lines, 15 forensics snaps, partial trace `2452f1da…` |
| 6 | 13:51–13:55 | Post-R1 dmesg + analyze (R1 census/samples) + forensics fetches on VM-H32 | `t41-dmesg-h32-postr1.txt` (523 lines, 4 AcceptAsync — all outside 171–430) |
| 7 | 13:55:33–13:59:52 ([664]→[923] H32) | R2: same failure, NO-PARK, T41_DONE exit 0 (R2 analyze not run — no R2 census) | poll log 98 lines, 3 forensics snaps, partial trace `e5f6ef2b…` |
| 8 | 13:59–14:02 | Post-R2 dmesg + forensics fetches on VM-H32 | `t41-dmesg-h32-postr2.txt` (587 lines, 6 AcceptAsync — all outside 664–923) |
| 9 | 14:02:46 | H32 teardown (post-R2 idle, NOT by me) | eventlog-final (IDs 71/69/233/234/234 @10:02:46) |
| 10 | 14:02:51–14:08:42 | H33 (forensics VM: WSLg-audio checks — no PulseServer socket; dialogwatch v1 staged); no committed dmesg reads isolate H33 | create/teardown pairs @10:02:51/@10:08:42; `t41-dialogwatch.sh` header documents the audio finding |
| 11 | 14:08:47 ([0] VM-H34) | H34 create | eventlog-final (IDs @10:08:47) |
| 12 | 14:09:20–14:13:21 ([33]→[274] H34) | R3 (dialogwatch v1 ×2 in parallel, both root-dismissed): chain nominal to SP, game-side SP→SM advance, NO-SP-PARK, T41_DONE exit 0 | stdout 255 lines, dialogcheck snap, partial trace `98d17eb2…` |
| 13 | 14:13–14:14 | Post-R3 dmesg + dialogcheck fetch on VM-H34 | `t41-dmesg-h34-postr3.txt` (416 lines, 0 AcceptAsync, 0 Ioctl) |
| 14 | 14:14:37 | H34 teardown (NOT by me) | eventlog-final (IDs @10:14:37) |
| 15 | 14:14:54–14:17:51 | H35 (pre-R4 checks: pins/refs/staging re-verified; dialogwatch v2 staged) | `t41-dmesg-h35-pre.txt` (423 lines, 0 AcceptAsync) |
| 16 | 14:17:51 | H35 teardown (NOT by me) | eventlog-final (IDs @10:17:51) |
| 17 | 14:17:58 ([0] VM-H36) | H36 create | eventlog-final (IDs @10:17:58) |
| 18 | 14:18:32–14:27:11 ([33]→[553] H36) | R4 (dialogwatch v2 in parallel, one inert dismissal @T+10.65): FULL CHAIN + hold + blind dense series, exit 0, `T41_DONE`, clean shutdown | 61 snaps, poll log 168 lines, trace sha `5b0a7349…` |
| 19 | 14:27–14:31 | Post-R4 dmesg (IMMEDIATELY after run ssh) + analyze + vcount + all R4 fetches on VM-H36 | `t41-dmesg-h36-postr4.txt` (450 lines, 1 AcceptAsync [568.52] — post-window) |
| 20 | 14:31:21 | H36 teardown (NOT by me) | eventlog-final (IDs @10:31:21) |
| 21 | 14:31:36–14:32:53 | H37 (77 s, unattributed — no committed reads isolate it) | create/teardown pairs @10:31:36/@10:32:53 |
| 22 | 14:39:56–14:41:13 | H38 (77 s, unattributed — SSD-stream attempt window; SSD detached, stream BLOCKED) | create/teardown pairs @10:39:56/@10:41:13 |
| 23 | ~14:41 | Final eventlog read (newest-120; newest entry = H38 teardown) | `t41-eventlog-final.txt` (120 entries, all Hyper-V-VmSwitch lifecycle) |
| 24 | ~14:4x | H39 post-everything reads (create postdates the final eventlog read) | `t41-dmesg-h39-final.txt` (422 lines, 0 AcceptAsync) |
| 25 | T41F session | Post-restart re-verifies (pins/refs/staged/shas/slices) + SSD stream + verify on a fresh VM (btime 1790007578) | current-VM dmesg (474 lines, 1 AcceptAsync [68.26] boot noise, different VM — outside all windows) |
| 26 | event log | Pre/postr1/final reads: boundaries H31-create 08:46:03 → H31-teardown 08:48:50 → H32-create 09:44:29 → H32-teardown 10:02:46 → H33-create 10:02:51 → H33-teardown 10:08:42 → H34-create 10:08:47 → H34-teardown 10:14:37 → H35-create 10:14:54 → H35-teardown 10:17:51 → H36-create 10:17:58 → H36-teardown 10:31:21 → H37-create 10:31:36 → H37-teardown 10:32:53 → H38-create 10:39:56 → H38-teardown 10:41:13; in-window entries: ZERO of any kind in all 4 run windows; pre==postr1 byte-identical (zero new entries during R1) | `t41-eventlog-{pre,postr1,final}.txt` |
| 27 | dmesg noise | `Ioctl failed` 5/75/121/0/5/23/5 across the 7 files (H32-pre/H35-pre/H39-final 5-line boot bursts @~3.2–3.4; H36-postr4 23 lines @3.21–21.20, all pre-window; H32-postr1/2 carry 18-line pcsx2-boot dxg-query bursts at the run start edge — uptime 171–174.3 (R1 T+0–3 s) and 664–667.6 (R2 T+0–3 s) — plus pre-window boot noise; ZERO Ioctl lines mid-run in any window; H34-postr3 has 0 Ioctl of any kind); kill-pattern grep matches only the 2 `panic=-1` cmdline echoes per file | dmesg files |

AcceptAsync exact counts with uptime-stamp positions relative to the run
windows (R1: T_BOOT uptime 171 → end 430 on H32; R2: 664 → 923 on H32;
R3: 33 → 274 on H34; R4: 33 → 553 on H36):

| Committed file | Lines | AcceptAsync count | Uptime stamps | Position vs run window |
|---|---|---|---|---|
| `t41-dmesg-h32-pre.txt` | 416 | 0 | — | same VM, pre-window; outside |
| `t41-dmesg-h32-postr1.txt` | 523 | 4 | [23.23] [97.56] [123.52] [445.66] | same VM; first 3 pre-window (R1 starts 171), last post-window (R1 ends 430); ZERO in-window |
| `t41-dmesg-h32-postr2.txt` | 587 | 6 | [23.23] [97.56] [123.52] [445.66] [601.77] [938.79] | same VM; first 5 pre-window (R2 starts 664), last post-window (R2 ends 923); ZERO in-window |
| `t41-dmesg-h34-postr3.txt` | 416 | 0 | — | same VM, full-window coverage; ZERO in-window |
| `t41-dmesg-h35-pre.txt` | 423 | 0 | — | different VM (pre-R4 checks, no run); outside |
| `t41-dmesg-h36-postr4.txt` | 450 | 1 | [568.52] | same VM, post-window (run ended uptime 553); ZERO in-window |
| `t41-dmesg-h39-final.txt` | 422 | 0 | — | different VM (post-everything, no run); outside |

## T41-1. Hold + blind-series shape + tracking method (frozen BEFORE the run) + LIVE calibration

Tool: `t41-cropdiff.py` (copy of T40's, byte-identical; `cmp` clean;
`t41-vcount.sh` byte-identical to T40's; `t41-analyze.sh` differs only in
output names). Title text-band method unchanged (thresholds frozen: TITLE
band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu
mean < 2.0; NONMENU / NONSC / NONZC / NONSP / NONSE / NONMR whole-vs-ref
mean > 5.0; DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). Panel
reference reused (`t35-ref-panel.ppm`, already staged, sha re-verified).
No new reference (no new static screen to gate on). Remote PPM-mode
self-check pre-run: panel ref 0.0000/0.

Hold selection (tabled BEFORE the run — T40's input class, kept):

| Item | Value |
|---|---|
| Input | ONE `press_hold Left` (1 s `sleep` between keydown/keyup; body verbatim T38's) |
| Binding | `Left = Keyboard/Left` (`PCSX2.ini:576`, re-verified pre-run) |
| Slot | Same script slot the T38 hold / T39 sham / T40 hold occupied (≈T+503, after the pre-pair) |
| When | After the X arrival series, on the LIVE-LIKE proxy gate (deep in live gameplay per T35's–T40's race shape) |

Blind-series shape (tabled BEFORE the run — the ONLY deliberate change vs
T40):

| Item | Value |
|---|---|
| Pre-pair | `bsnap npre1`, `sleep 0.5`, `bsnap npre2` — no input between, no scoring |
| Hold | `press_hold Left "HOLD_LEFT"` |
| Post-hold | 10 × (`sleep 0.5`, `bsnap d-postN`) — no scoring |
| Stamps | each `bsnap` logs `SNAPSTART_WALL`/`SNAPEND_WALL` (ns precision) + uptime + T+ to the poll log; exposure gaps recovered post-hoc |
| Post-hoc | per-snap HUD + full vs-ref panel + all 11 dense hops + RDC/SCPS40/SCPS120, all from fetched snaps |

Tracking method (tabled BEFORE the run — frozen in committed
`t41-track.py`, byte-identical to T40's, sha `58afa004…91c108`):

| Metric | Definition (fixed) | Rationale |
|---|---|---|
| RDCX/RDCY | T37-frozen: centroid (0.1 px) of dark pixels (luminance < 80) inside rider ROI x[150,540] y[100,460]. Reports cx/cy/npix/dark-fraction; npix is the validity channel | Rider outfit is near-black against bright snow; a Left carve displaces the rider sprite laterally before the chase cam re-centers |
| RDC gate | VALID iff 200 ≤ npix ≤ 6000 (rider-scale band; T37 calibration: valid snaps npix 1299–3786, mixed 8595–12177, flooded ≥ 18624; T36 npre rider-clean 2462). Gated-out snaps print INVALID and their cx/cy must not be used for deltas | T37 recipe: validity-gated RDC (skip snaps with npix ≫ rider-scale) |
| SCPS40 | T37-frozen: snow column-profile shift (integer lag px in [−40,+40]) between consecutive snaps over x[150,540] of rows y[380,460], normalized xcorr best lag (+ = scene moved right). Reports lag + peak corr; corr is the validity channel | Under a chase cam the world rotates around the rider, so a heading change reads as background lateral shift even when the rider stays centered |
| SCPS120 | Same normalized-xcorr column-profile shift over lag in [−120,+120] (3× the T37 window) | T37 recipe: wider SCPS lag window (motion exceeded ±40 px at ~3 s exposure gaps under turbo — T37/T38/T39 railed nearly every step incl. no-input gaps) |

LIVE calibration (T36's, reused unchanged; T35 R1 receipts; no new
calibration run — the gate is a proxy, the criterion is HUD-read):

| Leg | T35 R1 receipt | Bar | Margin |
|---|---|---|---|
| Panel→countdown departure hop (pppre→x-post1) | 14.18–14.19 | > 5.0 (DEPARTED) | 2.8× |
| X-snaps vs-panel-ref | 12.98–21.27 | > 5.0 (NONPP) | 2.6× |
| Late-tail motion hops (x-post15→x-post25, x-post25→x-post40) | 11.52, 9.51 | > 5.0 (DEPARTED) | 1.9× |
| All 66 X-pair hops | 7.97–20.23 (never static) | — | static gate cannot fire |

LIVE-LIKE proxy gate (as frozen pre-run): in-script hold criterion =
decisively left the panel (pppre→x-post1 hop > 5.0) AND arrival non-panel
(x-post40 vs-pp > 5.0) AND motion ×2 (x-post15→x-post25, x-post25→x-post40
hops > 5.0). The TRUE live-race criterion — race clock advancing +
position/progress HUD read off the VIEWED snaps. Every proxy leg carries
≥1.9× margin on the T35 receipts.

Script deltas vs `t40-auto.sh` (committed originals untouched; `t41-auto.sh`
is the adapted copy):

| Area | T40 script | T41 script |
|---|---|---|
| Chain | park phase + full menu→MR chain + PP gate + XCROSS + x series to +40 + LIVE gate + pre-pair + hold + dense d-post1..10, all blind in the dense phase | identical through the LIVE-LIKE gate; dense cadence differs (see below) |
| Dense input | ONE `press_hold Left` (1 s `sleep`, T38's input class) | identical (same call, same slot) |
| Dense capture | `bsnap` (capture + ns stamps, NO scoring); `sleep 1` pre-pair gap + 10 × `sleep 1` | `bsnap` unchanged; `sleep 0.5` pre-pair gap + 10 × `sleep 0.5` (11-line code change; comments updated) |
| Self-tests | SELF_TEST + … + SELF_MR + SELF_PP | unchanged (all 11 re-run) |
| No-park paths | explicit `NO-PARK` + … + `NO-LIVE-PARK` | unchanged (still clean shutdown + `T41_DONE`, trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
batch port of `t41-cropdiff.py` (`/tmp/t41-batch.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical)
against the committed tool on 4 diverse pairs (same 4-pair protocol as
T39/T40; pairs + scores tabled in §T41-5). Any score reproduces with the
committed `t41-cropdiff.py`, slower. The 9 ref PPMs were re-fetched from
bytesize for post-hoc scoring (all 9 shas reproduce §T41-0 exactly).

## T41-2. R1 — NO-PARK (environment failure: WSLg-audio-down cubeb modal occludes the title band)

R1 booted on VM-H32 (T_BOOT 1789998440, uptime 171; 13:47:20 UTC) and ran
all 3 park attempts, each ending NO-TITLE-IN-WINDOW: a PCSX2 modal —
"Failed to create or configure audio stream, falling back to null
output. The error was: cubeb_stream_init() failed: CUBEB_ERROR (-1)" —
sat over the game window on EVERY snap (viewed: `start`, `a1-now`-class
attract, `a1-poll01` attract, `a1-poll12`–`17` TRUE TITLE), pushing the
title-band score to 16.4–46.8 (bar: mean < 2.0 AND p99 ≤ 10) so the
detector never fired. NO-PARK, `T41_DONE`, exit 0, clean SIGTERM
shutdown at uptime 430 (T+259). Environment failure: effects on the
question unverifiable per the T27 §4 rule → re-run as R2.

### R1 attempt table (all 3 attempts NO-TITLE-IN-WINDOW)

| Attempt | Detect (attract/title-band) | Presses | Outcome |
|---|---|---|---|
| A1 | `a1-now` attract 35.8995/186 remote (35.9361/186 PIL); polls 01–18 span 16.60–43.75: poll12–17 plateau 16.60–16.79 = TRUE TITLE under the modal (viewed poll12: SSX 3 logo + © 2003 EA + modal; PIL 16.40–16.61/145–147) | Cross 535.5 ms @T+98.55→99.09 (attract-skip) | no-title in window |
| A2 | `a2-now` attract 25.0242/158 (25.0743/159 PIL); polls span 24.18–46.83, all attract-under-modal (viewed: none; start-class forensics) | Cross 536.2 ms @T+149.06→149.59 | no-title in window |
| A3 | `a3-now` attract 28.1674/157 (28.2081/157 PIL); polls span 24.81–44.55, all attract-under-modal | Cross 535.7 ms @T+199.59→200.13 | no-title in window |

### R1 forensics snaps (committed 15; PIL title-band / whole-vs-menu cross-check of the remote)

| Snap (T+) | Size / sha12 | Band vs title (remote → PIL) | Whole vs menu (PIL) | Content |
|---|---|---|---|---|
| start (T+97) | 66739 B / `682de379b03a` | 29.0476/177 → 29.0664/176 | 16.2724/171 | attract cinematic (rider on rail) + modal (viewed) |
| a1-now (T+97) | 62347 B / `f0ffa2073450` | 35.8995/186 → 35.9361/186 | 18.0968/191 | attract + modal |
| a1-poll01 (T+101) | 63779 B / `1ca00ef1aecd` | 43.7518/206 → 43.7864/206 | 18.7378/184 | attract (rider over vista) + modal (viewed) |
| a1-poll12 (T+131) | 61394 B / `39d4d8ee54cf` | 16.7942/151 → 16.6113/147 | 17.1555/165 | TRUE TITLE + modal (viewed) |
| a1-poll13 (T+134) | 62875 B / `d2d1da0d7a25` | 16.6748/147 → 16.4797/145 | 17.0988/165 | TRUE TITLE + modal |
| a1-poll14 (T+137) | 62812 B / `1acf659c501f` | 16.6218/147 → 16.4302/145 | 17.1347/165 | TRUE TITLE + modal |
| a1-poll15 (T+140) | 62625 B / `b91b06bffd9b` | 16.6012/147 → 16.4016/145 | 17.1320/165 | TRUE TITLE + modal |
| a1-poll16 (T+142) | 62854 B / `d32b6407f877` | 16.6470/147 → 16.4593/145 | 17.1367/165 | TRUE TITLE + modal |
| a1-poll17 (T+145) | 62563 B / `bbad4f3bc9ef` | 16.6012/147 → 16.4016/145 | 17.1344/165 | TRUE TITLE + modal |
| a1-poll18 (T+148) | 50345 B / `f81a5226efb3` | 25.1357/163 → 25.1667/163 | 20.0705/166 | attract + modal |
| a2-now (T+148) | 54725 B / `c65bd6b66cfe` | 25.0242/158 → 25.0743/159 | 19.4947/166 | attract + modal |
| a2-poll01 (T+152) | 51003 B / `8a6cff7d70bb` | 34.2101/184 → 34.2568/184 | 18.3802/177 | attract + modal |
| a3-now (T+198) | 71893 B / `357365e44fe8` | 28.1674/157 → 28.2081/157 | 17.1429/169 | attract + modal |
| a3-poll01 (T+202) | 48135 B / `fd14718b756a` | 28.8220/174 → 28.7735/174 | 22.8117/200 | attract + modal |
| a3-poll18 (T+249) | 60748 B / `6988325a7050` | 41.6069/218 → 41.6421/217 | 22.7398/212 | attract + modal |

| Item | Value |
|---|---|
| R1 window | 13:47:20–13:51:39 UTC (T+0–259), VM-H32 uptime 171→430 |
| Modal text (viewed) | `Failed to create or configure audio stream, falling back to null output. The error was: cubeb_stream_init() failed: CUBEB_ERROR (-1)` + OK button; occludes the title text-band (380,200,1180,480) |
| In-trace smoking gun | R1 census: `MARK ERROR 197 [0.5826] cubeb_stream_init() failed: CUBEB_ERROR (-1)` + `MARK Error 196 [0.5826] ReportErrorAsync: Error: Failed to create or configure audio stream…` (audio dies 0.58 s into the boot) |
| Guest-side correlate | R1 census IOP set = 154/155 vs T40 R2 — missing ONLY `libsd.006: sceSdGetParam` (audio never initializes; EE 52/52 identical; R1 EE 4547465 · IOP 13222130 · 29223690 lines, span ..249.05) |
| WSLg-audio root cause | Host WSLg audio down on H32 (no `/mnt/wslg/PulseServer` socket, no `runtime-dir/pulse/`; host has 6 OK sound devices → WSLg defect); documented in committed `t41-dialogwatch.sh` header (finding level: tool-header text, no separate probe log committed) |
| Flaps | ZERO in-window AcceptAsync (4 H32 flaps all outside 171–430) + ZERO event-log entries in-window (pre==postr1 byte-identical); 18-line `Ioctl failed` pcsx2-boot dxg burst at T+0–3 s (uptime 171–174.3), zero mid-run |
| R1 verdict | NO-PARK as an environment failure (modal occludes the detector band), effects-unverifiable per T27 §4 → re-run as R2; partial trace `2452f1da…` (1914391860 B) preserved bytesize-only |

## T41-3. R2 — NO-PARK (same environment failure, same VM)

R2 booted on the SAME VM-H32 (T_BOOT 1789998933, uptime 664; 13:55:33
UTC) and reproduced R1 exactly: 3/3 attempts NO-TITLE-IN-WINDOW with the
identical cubeb modal on every snap (viewed: `start` attract + modal,
`a1-poll12` TRUE TITLE + modal at band 16.79/151 remote, 16.61/147 PIL).
NO-PARK, `T41_DONE`, exit 0, clean shutdown at uptime 923 (T+259).
Environment failure (2/2 runs on H32) → WSLg-audio forensics on H33 +
dialogwatch v1 → R3 on a fresh VM.

### R2 attempt table (all 3 attempts NO-TITLE-IN-WINDOW)

| Attempt | Detect (attract/title-band) | Presses | Outcome |
|---|---|---|---|
| A1 | `a1-now` attract 31.4403/149; polls span 16.60–43.93: poll12–17 plateau 16.60–16.79 = TRUE TITLE under the modal (viewed poll12) | Cross 535.4 ms @T+98.76→99.29 (attract-skip) | no-title in window |
| A2 | `a2-now` attract 26.0675/163; polls span 24.79–46.82, all attract-under-modal | Cross 535.7 ms @T+149.24→149.78 | no-title in window |
| A3 | `a3-now` attract 28.1293/157; polls span 23.60–44.04, all attract-under-modal | Cross 534.7 ms @T+199.89→200.42 | no-title in window |

### R2 forensics snaps (committed 3; the failure duplicates R1, so only the mechanism pair + tail)

| Snap (T+) | Size / sha12 | Band vs title (remote → PIL) | Whole vs menu (PIL) | Content |
|---|---|---|---|---|
| start (T+98) | 45038 B / `7a409701ee0b` | 46.7531/222 → 46.7971/222 | 25.1356/210 | attract + modal (viewed) |
| a1-poll12 (T+132) | 61269 B / `9b39eeba3d43` | 16.7908/151 → 16.6066/147 | 17.1612/165 | TRUE TITLE + modal (viewed) |
| a3-poll18 (T+249) | 60378 B / `7641b2157259` | 42.4857/220 → 42.5190/220 | 23.7528/213 | attract + modal |

| Item | Value |
|---|---|
| R2 window | 13:55:33–13:59:52 UTC (T+0–259), VM-H32 uptime 664→923 |
| Modal | identical text/geometry to R1 (viewed both snaps) |
| Census | R2 analyze NOT run (no `t41r2-census/samples` — same failure as R1, skipped deliberately) |
| Flaps | ZERO in-window AcceptAsync (6 H32 flaps all outside 664–923) + ZERO event-log entries in-window; 18-line `Ioctl failed` pcsx2-boot dxg burst at T+0–3 s (uptime 664–667.6), zero mid-run |
| R2 verdict | NO-PARK as an environment failure (2/2 on H32), effects-unverifiable per T27 §4 → forensics + dialogwatch → R3 on VM-H34; partial trace `e5f6ef2b…` (1913796712 B) preserved bytesize-only |

## T41-4. R3 — NO-SP-PARK (game-side SP→SM advance with zero input in-window)

R3 booted on fresh VM-H34 (T_BOOT 1789999760, uptime 33; 14:09:20 UTC)
with dialogwatch v1 running twice in parallel (both hit the v1
root-dismiss bug: ROUND:1 @T+5.1 and @T+56.2 each Returned the root
window 511 and exited — never reaching a real dialog; v2 written after
this run). The chain ran nominally through TITLE → menu → SC → ZC → SP
(all gates fired on clean scores, no modal anywhere — WSLg audio was
back on H34), then Select Peak advanced to Select Mode BY ITSELF between
sp-post1 (clean SP, vs-sp 0.3695/6 @T+214) and sp-post3 (full SM,
titleband 26.3182 = SM band, vs-sp 5.3584 @T+218): the SP→SM hop reads
5.1808 with p3-p8 static at 0.0138, and ZERO scripted inputs fall in
T+211.08–218 (last press: CONT Cross keyup @T+211.08). NO-SP-PARK (no
Peak Cross pressed), `T41_DONE`, exit 0, clean shutdown at uptime 274
(T+241). Not an attempt on the question (never reached live gameplay) →
R4 on a fresh VM.

### R3 chain (all in-script remote scores; nominal to SP)

| Step | Receipt |
|---|---|
| A1 Cross 535.0 ms @T+98.98→99.52 | `a1-now` attract 24.5459/157 → `a1-poll01` TITLE 0.4329/6 @T+102 (58374 B) |
| A1 Start 535.8 ms @T+102.26→102.80 | `a1-post3/8/15/25` menu 16.26–16.29/139; whole815 0.0337, whole1525 0.0118, post25-vs-menu 0.2951/5 → MENU-LIKE |
| Menu Cross 537.0 ms @T+141.50→142.04 | `menupre` vs-menu 0.2871/5; `mc-post1/3/8/15` vs-sc 0.42–0.62/7–9; hops 10.1439/0.1025/0.3016/0.2789 → SC-LIKE |
| Zoe Cross 537.1 ms @T+181.70→182.24 | `scpre` (70642 B) vs-sc 0.4680/7; `zc-post1/3/8` vs-zc 0.45–0.52/8–9; hops 7.0891/0.2891/0.2675 → ZC-LIKE |
| Cont Cross 535.2 ms @T+210.54→211.08 | `ccpre` (51442 B) vs-zc 0.4766/8; `sp-post1` (65297 B) vs-sp 0.3695/6 @T+214 — clean SP |
| SP stall | `sp-post3` (67467 B) titleband 26.3182/vs-sp 5.3584 @T+218; `sp-post8` (67340 B) titleband 26.3170/vs-sp 5.3469 @T+226; hops pre-post1 9.3415, p1-p3 5.1808, p3-p8 0.0138 → NO-SP-PARK |

### R3 forensics

| Item | Value |
|---|---|
| R3 window | 14:09:20–14:13:21 UTC (T+0–241), VM-H34 uptime 33→274 |
| SP→SM advance | sp-post1 clean SP @T+214 → sp-post3 full SM @T+218 (band 26.3182 = SM band; vs-sp 5.36 ≈ R4's SP→SM hop 5.26; p3-p8 0.0138 static) — game-side, mechanism unknown (no freeze/menu/reclaim; a dwell/timeout-class advance, tabled as observed) |
| Zero input in-window | last scripted press CONT keyup @T+211.08; sp-post1 @T+214 clean; advance lands by T+218; no scripted press in T+211.08–226 (poll log + stderr agree) |
| Parallel Start@T+155 (wrap-note claim) | stated pre-restart; NO in-log receipt survives (a manual second-ssh press leaves no stdout/poll trace) — receipt status: UNVERIFIED but consistent-with-inert (`ccpre` vs-zc 0.4766/8 clean, `sp-post1` vs-sp 0.3695/6 clean, ZC hops static 0.29/0.27, SP arrival clean). Timeline cross-check: T+155 per the script timeline falls in the SC phase (`mc-post3`→`mc-post8` gap), not on ZC — either the T+ recall is off or the target-screen recall is; both readings are consistent with "inert" (Start advances neither screen). Tabled as stated + cross-checked, not silently corrected |
| Dialog evidence | `t41r3-dialogcheck.jpg` (51322 B, manually captured): clean Setup Character, Zoe + Continue, "Continue to peak selection." — PIL vs-zc 0.2393/6, NO dialog visible; `t41r4`-class midrun hygiene confirmed clean |
| Dialogwatch v1 ×2 | `t41r3-dialogwatch.txt` + `t41r3-dialogwatch2.txt` (688 B each): ROUND:1 @T+5.1 / @T+56.2, both `DISMISS:511:` (root, empty name) + `XGetInputFocus` warnings → `DISMISSED`, exit 0 — the v1 bug (search matches root; first non-SSX = root); no real dialog ever seen on R3, none needed dismissing |
| Census | R3 analyze NOT run (no `t41r3-census/samples` — run ended at a no-park, skipped deliberately) |
| Flaps | ZERO AcceptAsync of any kind on H34 (416-line file, full-window coverage) + ZERO `Ioctl failed` lines + ZERO event-log entries in-window |
| R3 verdict | NO-SP-PARK (game-side advance, zero input in-window), not an attempt on the question → R4 on VM-H36; partial trace `98d17eb2…` (1435642909 B) preserved bytesize-only |

## T41-5. R4 — race reproduced, ONE 1 s hold + blind sub-second series on live gameplay

Run: `t41-auto.sh`, ONE fresh boot, T_BOOT wall 1790000312 (uptime 33,
VM-H36), 14:18:32–14:27:11 UTC (uptime 33→553 = 520 s; 160 s over the
≤6 min guidance — the X phase + dense tail; full dmesg coverage, zero
flaps in-window; −4 s vs T40 R2's 524 s from the 11 × 0.5 s sleep
savings minus ~1.5 s overhead jitter), WID 2097159 (same as T31 R1 /
T32 R1 / T33 R1 / T33 R2 / T34 R1 / T35 R1 / T36 R1 / T37 R1 / T38 R1 /
T39 R1 / T40 R1-wedged / T40 R2 / T41 R1 / T41 R2 / T41 R3), exit 0,
`T41_DONE`, clean SIGTERM shutdown. SELF_TEST 0.0000/0, SELF_WHOLE
0.0000, SELF_MENU 0.0000/0, SELF_SC 0.0000/0, SELF_ZC 0.0000/0, SELF_SP
0.0000/0, SELF_SM 0.0000/0, SELF_SE 0.0000/0, SELF_SETAG 0.0000/0,
SELF_MR 0.0000/0, SELF_PP 0.0000/0. Question attempts: 1 (R4 — R1/R2
were environment failures and R3 never reached live gameplay, none an
attempt on the question). No bounded re-attempt run (pre-hold = racing
at a matched phase — re-attempt condition not met, brief stops here).
Dialogwatch v2 ran in parallel: one dismissal at ROUND:1 @T+10.65
(window 2097162 `pcsx2-qt` 640x480, Return) — provably inert: R4's trace
carries ZERO cubeb-error lines with `Cubeb stream init successful` at
L198, no modal appears in any of the 61 snaps, and the chain ran
nominally (the dismissed window was the main Qt window at boot, not a
modal). Midrun hygiene: manual `t41-r4check.jpg` (54833 B, T+~40–90)
shows clean attract, no modal.

### R4 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+101, score 0.4337/6 remote / 0.0453/0 PIL (T40 R2: 0.4331/6 / 0.0467/1 — same detector reading, near-identical frame, see xrun) | Cross 536.6 ms @T+98.61 (attract-skip) + Start 535.5 ms @T+101.87 (on title, ≤1.8 s after exposure) | Main Menu by +5 s; menu-like gate (non-title + whole-static 0.0366/0.0121) + post25-vs-menu 0.2953/5 → park for menu Cross |
| A2–A3 | not run (chain advanced) | — | — |

### R4 cross-run frame identities (T41 R4 vs T40 R2; T41 names)

| Frame | T41 R4 size / sha12 | T40 R2 size | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | 58388 B / `4a9c7cf6b67d` (cp-identical, pair 0.0000/0) | 58352 B | whole pair 0.0308/0 max 49 (title snowflake shimmer) |
| a1-post3 | 50085 B / `f1287a7be3a6` | 49992 B | whole pair 0.0634/1 max 56 |
| a1-post8 | 50017 B / `878f14c4eef4` | 49991 B | whole pair 0.0712/1 max 58 |
| a1-post15 | 49634 B / `4c56f8159c76` | 49640 B | whole pair 0.0007/0 max 6 (near-identical) |
| a1-post25 | 49738 B / `4e4e15409746` | 49739 B | whole pair 0.0273/0 max 42 |
| menupre | 49674 B / `5195c600a276` | 49677 B | whole pair 0.0042/0 max 15 |
| mc-post1/3/8/15 | 70217/70283/70339/70272 B | 70373/70335/70346/70398 B | whole pairs 0.204/5, 0.217/5, 0.177/4, 0.210/5 |
| scpre | 70597 B / `ab72ef1460ee` | 70592 B | whole pair 0.1946/4 |
| zc-post1/3/8 | 51417/51426/51357 B | 51461/51434/51362 B | whole pairs 0.048/0, 0.039/1, 0.041/0 |
| ccpre | 51500 B / `be46a8d15427` | 51493 B | whole pair 0.0345/1 |
| sp-post1/3/8 | 65290/65532/65226 B | 65282/65525/65228 B | whole pairs 0.012/0, 0.029/0, 0.0004/0 (sp-post8 near-identical, max 16) |
| sppre | 65540 B / `cd20a9f6c817` | 65510 B | whole pair 0.0276/0 |
| pc-post1/3/8 | 67889/67480/67483 B | 67992/67564/67443 B | whole pairs 0.092/0, 0.054/0, 0.027/0 |
| smpre | 67563 B / `167de61e4b4c` | 67563 B | same SIZE, different bytes; whole pair 0.0569/0 |
| rc-post1/3 | 69634/69430 B | 69843/69493 B | whole pairs 0.069/0, 0.011/0 (near-identical) |
| rc-post8 | 69720 B / `b423ad2fcb5e` | 69445 B | whole pair 0.0481/0 |
| sepre | 69614 B / `85b3ea20db55` | 69847 B | whole pair 0.1004/1 |
| sj-post1/3/8 | 58680/59040/58474 B | 58989/59213/58883 B | whole pairs 0.093/1, 0.203/5, 0.071/0 |
| mrpre vs T40 `mrpre` | 59373 B / `6c9425806da9` | 59416 B | whole pair 0.1462/3 |
| mr-post1 (load) | 66749 B / `023fa9d54af9` | 66749 B | BIT-IDENTICAL 0.0000/0/0 (17% Loading) |
| mr-post3 (load) | 67323 B / `c6278a3256f8` | 67057 B | differ; pair 1.3151/51 (97% both; shimmer/progress phase) |
| mr-post8 | 52351 B / `b82c29f1db26` | 54901 B | differ; pair 5.9161/104 (both race-intro cinematic, different phase/track: Like This X-ecutioners SSX 3 vs Jerk it Out Caesars 39 Minutes of Bliss) |
| mr-post15/25/40 | 59793/60288/60067 B | 59569/59642/59793 B | whole pairs 0.3879/6, 0.5620/14, 0.3522/6 (both pre-race panel; AI lineup differs run to run) |
| mr-stab1/2 | 59973/60235 B | 59607/59601 B | whole pairs 0.3391/6, 0.6083/16 (both pre-race panel; lineup differs) |
| pppre vs T40 `pppre` | 60188 B / `32bd0828591f` | 59550 B | whole pair 0.5453/13; whole-vs-panel-ref 0.4191/6 PIL |
| x-post1 (countdown) | 68871 B / `04f0b0f4ca46` | 69196 B | differ; pair 1.2737/34 (both countdown `2` gates — near-frozen) |
| x-post3 | 68103 B / `768c88735c4b` | 67575 B | whole pair 9.3812/120 (similar gate exit: 5TH/5TH at 00:00:02, 1%, 38/39 MPH) |
| x-post8/15/25/40 | 68844/59906/68628/61825 B | 68820/59321/64756/66355 B | whole pairs 6.62/102, 4.45/87, 13.64/137, 13.13/124 (gameplay lottery) |
| npre1/2 | 58926/62190 B | 52069/50992 B | whole pairs 14.08/151, 13.24/103 (gameplay lottery) |
| d-post1..10 | 58794/57284/59061/60104/58218/60261/58187/58948/56783/57916 B | 48456/51050/57207/53965/56852/50871/54132/53532/59421/62473 B | whole pairs 10.51/124, 7.19/106, 10.28/145, 15.52/150, 12.31/143, 23.28/195, 12.24/121, 11.97/119, 11.48/143, 19.43/162 (gameplay lottery) |

ONE bit-identical frame this run (mr-post1 load 17% — the loading
screen is frozen); near-identical: a1-post15 0.0007/0 max 6, sp-post8
0.0004/0 max 16, rc-post3 0.0109/0 (snowflake shimmer breaks
bit-equality everywhere else).

### R4 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1790000410.611 → 1790000411.147 | 536.6 ms | T+98.61→99.15 | 132 | `a1-now` attract (25.3156/160 remote; 25.3062/160 PIL — viewed) | `a1-poll01` TITLE (0.4337/6; 0.0453/0 — viewed) |
| A1 Start (Return) | 1790000413.875 → 1790000414.410 | 535.5 ms | T+101.87→102.41 | 135 | `a1-pre` ≡ `a1-poll01` (sha `4a9c7cf6b67d`, TITLE) | `a1-post3` Main Menu (16.2542/139; 16.2552/138) |
| MENU Cross (K) | 1790000453.084 → 1790000453.620 | 535.2 ms | T+141.08→141.62 | 174→175 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2871/5 remote; 0.0276/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2148/106; vs-sc 0.4862/8; titleband 12.5510/164) |
| ZOE Cross (K) | 1790000493.361 → 1790000493.898 | 536.8 ms | T+181.36→181.90 | 214→215 | `scpre` Select Character, Zoe selected (vs-sc 0.5311/8 remote; 0.1812/4 PIL; vs-menu 10.1400/105; vs-title 12.7890/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.1978/100; vs-zc 0.5191/9; titleband 15.8539/128) |
| CONT Cross (K) | 1790000522.242 → 1790000522.778 | 535.6 ms | T+210.24→210.78 | 243→244 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4804/9 remote; 0.2480/7 PIL; vs-sc 7.2884/100; vs-title 15.9280/128 — viewed) | `sp-post1` Select Peak (vs-zc 9.4675/154; vs-sp 0.3699/6; titleband 23.1251/171) |
| PEAK Cross (K) | 1790000551.270 → 1790000551.805 | 535.9 ms | T+239.27→239.81 | 272→273 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.3737/6 remote; 0.0258/0 PIL; vs-zc 9.4713/154; vs-title 23.1293/171 — viewed) | `pc-post1` Select Mode (vs-sp 5.4066/121; vs-sm 0.4467/7; titleband 26.3170/183) |
| RACE Cross (K) | 1790000580.938 → 1790000581.476 | 538.1 ms | T+268.94→269.48 | 302→303 | `smpre` Select Mode, Race highlighted (vs-sm 0.4079/6 remote; 0.0601/0 PIL; se-tag 14.3278/89 remote; vs-sp 5.3678/121; vs-title 26.3170/183 — viewed) | `rc-post1` Select Event (vs-sm 0.8351/13; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1790000612.361 → 1790000612.898 | 537.5 ms | T+300.36→300.90 | 333→334 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6271/11 remote, 0.0094/0 PIL; vs-se 0.4339/6, 0.0704/0; vs-sm 0.8379/12; vs-sp 5.4781/121; vs-title 26.2104/183 — viewed) | `sj-post1` My Rules (vs-se 10.6413/143; vs-mr 0.4183/7; titleband 9.8539/137) |
| ENTER Cross (K) | 1790000641.125 → 1790000641.662 | 536.7 ms | T+329.13→329.66 | 362→363 | `mrpre` My Rules, Continue highlighted (vs-mr 0.4921/8 remote; 0.1833/4 PIL; vs-se 10.7110/143; vs-title 9.8519/137 — viewed) | `mr-post1` game load 17% (vs-mr 12.6253/150; vs-pp 21.0600/169; titleband 17.6707/170 — viewed) |
| XCROSS (K) | 1790000747.230 → 1790000747.766 | 536.3 ms | T+435.23→435.77 | 468→469 | `pppre` pre-race panel, X Continue (vs-pp 0.6815/9 remote; 0.4191/6 PIL — viewed) | `x-post1` countdown 2, starting gate (vs-pp 14.6034/153; titleband 18.4994/151 — viewed) |
| HOLD_LEFT (Left) | 1790000815.194 → 1790000816.233 | 1038.4 ms | T+503.19→504.23 | 536→537 | `npre2` live race 00:01:29 2ND/6 46% (post-hoc PIL only — blind: vs-pp 18.3071/150; band 12.7472/107 — viewed) | `d-post1` live race 00:01:32 2ND/6 46% (vs-pp 14.2612/132; band 27.6286/139 — viewed) |

Within-dwell receipts R4: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (1 s resolution) → Start-keydown ≤1.8 s; T33-R2-measured title
persistence 15–17 s ⇒ press inside the window with an order of magnitude
to spare. Start-keyup → MenuCross-keydown 38.7 s; MenuCross-keyup →
ZoeCross-keydown 39.7 s; ZoeCross-keyup → ContCross-keydown 28.3 s;
ContCross-keyup → PeakCross-keydown 28.5 s; PeakCross-keyup →
RaceCross-keydown 29.1 s; RaceCross-keyup → SnowJamCross-keydown 30.9 s;
SnowJamCross-keyup → EnterCross-keydown 28.2 s; EnterCross-keyup →
XCross-keydown 105.6 s (panel settling + PP gate); XCross-keyup →
Hold-keydown 67.4 s (X arrival series + LIVE gate; no dwell pressure — the
race runs input-free, T35 G1 precedent).

### R4 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / whole vs panel-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT
(dense-phase T+ refined to 0.01 s from ns `bsnap` stamps in the hold
table below).

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | Whole vs panel | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+97) | 56779B / `144478da32a8` | 36.0713/191 | 20.1115/172 | 18.5225/164 | 19.6796/158 | 15.8333/164 | 16.0201/166 | 16.1181/166 | 17.3356/144 | 10.7183/136 | 67.8656/172 | Attract |
| a1-now (T+97, pre-Cross) | 57174B / `541db04d299c` | 25.3062/160 | 16.6379/184 | 16.1125/151 | 17.0546/167 | 16.0227/157 | 15.9547/154 | 16.0113/156 | 15.5783/146 | 13.7333/140 | 95.8266/222 | Attract (viewed) |
| a1-poll01 (T+101, pre-Start) | 58388B / `4a9c7cf6b67d` | 0.0453/0 T | 14.1348/151 | 11.3077/152 | 12.2562/146 | 15.3709/156 | 16.1499/158 | 16.2477/160 | 9.7680/142 | 22.1504/183 | 106.6222/205 | TITLE (viewed) |
| a1-pre (T+101) | 58388B / `4a9c7cf6b67d` | 0.0453/0 | 14.1348/151 | 11.3077/152 | 12.2562/146 | 15.3709/156 | 16.1499/158 | 16.2477/160 | 9.7680/142 | 22.1504/183 | 106.6222/205 | TITLE (identical cp) |
| a1-post3 (T+105) | 50085B / `f1287a7be3a6` | 16.2552/138 | 0.0786/1 | 10.1367/105 | 6.9271/93 | 10.4114/170 | 10.9394/177 | 10.9548/177 | 10.1028/96 | 19.3220/178 | 26.1710/106 | Main Menu |
| a1-post8 (T+111) | 50017B / `878f14c4eef4` | 16.2990/139 | 0.0655/1 | 10.1186/105 | 6.9220/93 | 10.3929/170 | 10.9177/177 | 10.9427/177 | 10.0923/96 | 19.3332/178 | 26.1705/106 | Main Menu |
| a1-post15 (T+118) | 49634B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | 10.1073/105 | 6.9081/93 | 10.3855/170 | 10.9184/177 | 10.9433/177 | 10.0761/96 | 19.2985/178 | 26.1710/106 | Main Menu |
| a1-post25 (T+129) | 49738B / `4e4e15409746` | 16.2622/138 | 0.0408/0 | 10.1145/105 | 6.9042/92 | 10.3854/170 | 10.9186/177 | 10.9407/177 | 10.0815/96 | 19.3062/178 | 26.1687/106 | Main Menu |
| menupre (T+139, pre-MCross) | 49674B / `5195c600a276` | 16.2622/138 | 0.0276/0 | 10.1076/105 | 6.9076/93 | 10.3851/170 | 10.9180/177 | 10.9429/177 | 10.0752/96 | 19.2995/178 | 26.1393/106 | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+142) | 70217B / `1b60bc3da8ae` | 12.4783/163 | 10.1471/105 | 0.1379/3 | 7.1903/100 | 11.3702/158 | 11.8336/157 | 11.9043/157 | 5.6395/117 | 19.4437/172 | 26.5689/90 | Select Character, Zoe |
| mc-post3 (T+147) | 70283B / `13d325f05051` | 12.4949/163 | 10.1542/107 | 0.1831/4 | 7.1699/100 | 11.3802/158 | 11.8409/157 | 11.9122/157 | 5.6483/117 | 19.4593/172 | 26.5768/90 | Select Character |
| mc-post8 (T+154) | 70339B / `c61b7b2402e8` | 12.4579/163 | 10.1585/105 | 0.2356/4 | 7.2297/101 | 11.3651/158 | 11.8346/157 | 11.9061/157 | 5.6338/117 | 19.4572/172 | 26.5695/90 | Select Character |
| mc-post15 (T+164) | 70272B / `f528deb0525b` | 12.4587/163 | 10.1417/105 | 0.2025/4 | 7.1201/100 | 11.3539/158 | 11.8177/157 | 11.8884/157 | 5.6282/117 | 19.4316/172 | 26.5705/90 | Select Character |
| scpre (T+178, pre-ZCross) | 70597B / `ab72ef1460ee` | 12.7230/163 | 10.0739/105 | 0.1812/4 | 7.1121/100 | 11.3818/158 | 11.8396/160 | 11.9104/159 | 5.6689/117 | 19.4692/172 | 26.5696/90 | Select Character, Zoe selected (viewed) |
| zc-post1 (T+182) | 51417B / `543d60c3de99` | 15.8338/128 | 6.9273/92 | 7.1693/100 | 0.2858/7 | 9.3552/153 | 10.1410/164 | 10.2520/165 | 7.0390/103 | 20.1885/165 | 15.2956/91 | Setup Character, Zoe |
| zc-post3 (T+187) | 51426B / `0f020f3fe6ef` | 15.8687/128 | 6.9188/92 | 7.2439/99 | 0.2393/7 | 9.3709/154 | 10.1294/164 | 10.2426/165 | 7.0412/103 | 20.1885/164 | 15.2967/91 | Setup Character |
| zc-post8 (T+195) | 51357B / `9174b5e14717` | 15.8335/128 | 6.9314/93 | 7.1414/100 | 0.2193/5 | 9.3799/153 | 10.1257/164 | 10.2370/164 | 7.0894/103 | 20.1699/164 | 15.2956/91 | Setup Character |
| ccpre (T+207, pre-ContCross) | 51500B / `be46a8d15427` | 15.9045/129 | 6.9244/93 | 7.2596/100 | 0.2480/7 | 9.3755/153 | 10.1316/164 | 10.2447/164 | 7.0401/103 | 20.1906/164 | 15.2984/91 | Setup Character, Zoe + Continue (viewed) |
| sp-post1 (T+211) | 65290B / `7cb82834805b` | 23.1227/171 | 10.4217/170 | 11.3412/158 | 9.3878/153 | 0.0233/0 | 5.2204/121 | 5.3272/121 | 9.8247/138 | 16.5538/157 | 14.0026/89 | Select Peak, Peak 1 |
| sp-post3 (T+216) | 65532B / `a77d02472095` | 23.1275/171 | 10.4228/170 | 11.3478/158 | 9.3928/153 | 0.0252/0 | 5.2273/121 | 5.3297/121 | 9.8346/138 | 16.5617/157 | 14.0209/89 | Select Peak |
| sp-post8 (T+224) | 65226B / `4e70c45e9081` | 23.1259/171 | 10.4059/170 | 11.3501/158 | 9.3725/153 | 0.0038/0 | 5.2069/121 | 5.3095/121 | 9.8372/138 | 16.5439/157 | 14.0026/89 | Select Peak |
| sppre (T+236, pre-PeakCross) | 65540B / `cd20a9f6c817` | 23.1268/171 | 10.4216/170 | 11.3589/158 | 9.3911/153 | 0.0258/0 | 5.2274/121 | 5.3278/121 | 9.8468/138 | 16.5617/157 | 14.0565/89 | Select Peak, Peak 1 highlighted (viewed) |
| pc-post1 (T+240) | 67889B / `c519e85840f4` | 26.3046/183 | 10.9706/178 | 11.8579/157 | 10.1544/164 | 5.2420/121 | 0.1036/1 | 0.5400/11 | 10.5226/143 | 16.4535/160 | 14.1390/88 | Select Mode, Race |
| pc-post3 (T+245) | 67480B / `8fdc4e2e4b45` | 26.3046/183 | 10.9313/178 | 11.8211/157 | 10.1204/164 | 5.2015/121 | 0.0612/0 | 0.5327/11 | 10.4826/143 | 16.4316/160 | 14.1390/88 | Select Mode |
| pc-post8 (T+253) | 67483B / `9b637bb606b4` | 26.2937/183 | 10.9264/178 | 11.7952/157 | 10.1129/164 | 5.1940/121 | 0.0536/0 | 0.5251/10 | 10.4550/143 | 16.4256/160 | 14.1390/88 | Select Mode |
| smpre (T+265, pre-RaceCross) | 67563B / `167de61e4b4c` | 26.3046/183 | 10.9302/178 | 11.8183/157 | 10.1186/164 | 5.2005/121 | 0.0601/0 | 0.5311/11 | 10.4798/143 | 16.4307/160 | 14.1390/88 | Select Mode, Race highlighted (viewed) |
| rc-post1 (T+270) | 69634B / `750151052aea` | 26.1964/183 | 10.9672/178 | 11.8848/157 | 10.2450/164 | 5.3125/121 | 0.5407/12 | 0.0627/0 | 10.6180/144 | 16.4550/160 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+274) | 69430B / `f3b6cb718cbe` | 26.1964/183 | 10.9408/178 | 11.8604/157 | 10.2182/164 | 5.2863/121 | 0.5139/10 | 0.0357/0 | 10.5918/144 | 16.4292/160 | 0.0883/2 | Select Event |
| rc-post8 (T+282) | 69720B / `b423ad2fcb5e` | 26.2295/183 | 10.9705/178 | 11.8797/157 | 10.2470/164 | 5.3188/121 | 0.5071/9 | 0.0667/0 | 10.5801/144 | 16.4600/161 | 0.0597/2 | Select Event |
| sepre (T+296, pre-SnowJamCross) | 69614B / `85b3ea20db55` | 26.1964/183 | 10.9668/178 | 11.8831/157 | 10.2257/164 | 5.3185/121 | 0.5452/11 | 0.0704/0 | 10.6146/144 | 16.4598/160 | 0.0094/0 | Select Event, Snow Jam highlighted (viewed) |
| sj-post1 (T+301) | 58680B / `ab8a732d8ede` | 9.8283/136 | 10.0823/96 | 5.6228/117 | 7.0572/104 | 9.8325/137 | 10.4331/143 | 10.5973/143 | 0.1065/1 | 19.5464/153 | 26.4097/92 | My Rules, Continue |
| sj-post3 (T+306) | 59040B / `634d2247540d` | 9.8417/135 | 10.1339/98 | 5.6609/118 | 7.1045/105 | 9.8713/137 | 10.4769/143 | 10.6411/143 | 0.1677/3 | 19.6033/153 | 26.4122/92 | My Rules |
| sj-post8 (T+314) | 58474B / `a79e39002ec8` | 9.8533/135 | 10.0522/96 | 5.6250/117 | 7.0497/104 | 9.7962/137 | 10.4053/143 | 10.5693/143 | 0.0937/1 | 19.5306/152 | 26.4126/92 | My Rules |
| mrpre (T+326, pre-EnterCross) | 59373B / `6c9425806da9` | 9.8260/135 | 10.1627/100 | 5.7051/118 | 7.1253/105 | 9.9010/138 | 10.5021/143 | 10.6665/143 | 0.1833/4 | 19.6383/154 | 26.4117/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+330) | 66749B / `023fa9d54af9` | 17.6261/169 | 15.3901/157 | 14.3024/157 | 13.7599/154 | 14.8373/154 | 15.2048/153 | 15.3320/154 | 12.5965/149 | 21.0483/169 | 91.0281/224 | Loading 17% (viewed) |
| mr-post3 (T+335) | 67323B / `c6278a3256f8` | 17.9370/170 | 15.5002/157 | 14.3526/158 | 13.7827/154 | 14.9086/154 | 15.2753/153 | 15.4032/155 | 12.6344/150 | 21.0815/169 | 91.9155/225 | Loading 97% (viewed) |
| mr-post8 (T+343) | 52351B / `b82c29f1db26` | 29.9067/237 | 21.5427/219 | 21.1327/200 | 21.3168/190 | 20.2928/219 | 21.1893/219 | 21.0974/219 | 20.6449/196 | 18.4602/190 | 41.7836/132 | Race intro cinematic, nightclub, EA RADIO BIG / Like This / X-ecutioners / SSX 3 (viewed) |
| mr-post15 (T+352) | 59793B / `4461919595cd` | 34.4995/184 | 19.0066/177 | 19.1600/173 | 19.8910/162 | 16.3802/157 | 16.1739/159 | 16.1834/159 | 19.3240/154 | 0.7758/21 | 50.7588/135 | Pre-race panel |
| mr-post25 (T+365) | 60288B / `981e7e152f42` | 34.4976/184 | 19.4229/178 | 19.5280/173 | 20.2845/164 | 16.6357/157 | 16.5203/161 | 16.5291/160 | 19.7042/154 | 0.4639/7 | 50.7588/135 | Pre-race panel |
| mr-post40 (T+383) | 60067B / `4d1fbef443b5` | 34.4995/184 | 19.2630/178 | 19.3854/173 | 20.1251/163 | 16.5154/157 | 16.3869/160 | 16.3961/160 | 19.5481/154 | 0.4927/7 | 50.7588/135 | Pre-race panel |
| mr-stab1 (T+406) | 59973B / `266b752ee34a` | 34.5050/184 | 19.1806/178 | 19.3157/173 | 20.0563/163 | 16.4775/157 | 16.3110/160 | 16.3204/159 | 19.4824/154 | 0.5929/11 | 50.7588/135 | Pre-race panel |
| mr-stab2 (T+419) | 60235B / `7e5d6662eee3` | 34.5035/184 | 19.4181/179 | 19.5226/173 | 20.2781/164 | 16.6278/157 | 16.5141/161 | 16.5229/160 | 19.6969/154 | 0.4524/6 | 50.7588/135 | Pre-race panel |
| pppre (T+432, pre-XCross) | 60188B / `32bd0828591f` | 34.4949/184 | 19.3511/178 | 19.4631/173 | 20.2076/164 | 16.5718/157 | 16.4649/160 | 16.4739/160 | 19.6281/154 | 0.4191/6 | 50.7588/135 | Pre-race panel, X Continue (viewed) |
| x-post1 (T+436) | 68871B / `04f0b0f4ca46` | 18.4891/151 | 15.8191/161 | 13.8425/135 | 15.6772/152 | 15.7613/158 | 15.9085/157 | 15.9897/158 | 13.2038/129 | 14.5533/153 | 93.2905/174 | Countdown 2, starting gate, 00:00:00, 0 MPH (viewed) |
| x-post3 (T+440) | 68103B / `768c88735c4b` | 23.2886/152 | 14.5554/155 | 13.6193/134 | 12.9423/143 | 13.6130/145 | 13.7306/150 | 13.7798/150 | 12.8627/126 | 15.6324/140 | 22.6408/95 | 5TH/6, 00:00:02, 1%, 38 MPH (viewed) |
| x-post8 (T+447) | 68844B / `ee6ef3c1c31f` | 11.6952/126 | 16.8608/140 | 13.8197/154 | 15.3598/157 | 17.1039/162 | 17.6035/160 | 17.7391/163 | 12.1618/121 | 22.9600/172 | 109.8775/195 | 4TH/6, 00:00:10, 5%, 55 MPH (viewed) |
| x-post15 (T+456) | 59906B / `5d7293a0891a` | 14.6319/141 | 19.8036/159 | 15.3756/153 | 16.6445/158 | 18.2984/164 | 19.0356/167 | 19.1359/169 | 14.0270/129 | 23.5875/177 | 123.5219/205 | 2ND/6, 00:00:23, 12%, 50 MPH (viewed) |
| x-post25 (T+468) | 68628B / `5c980d5a359e` | 11.9822/112 | 14.9846/137 | 13.0941/134 | 13.4226/125 | 16.0305/156 | 16.7631/154 | 16.8516/155 | 11.8829/128 | 21.2681/187 | 95.4948/176 | 1ST/6, 00:00:40, 21%, 51 MPH, 611 pts (viewed) |
| x-post40 (T+484) | 61825B / `47ec8c5b1f5f` | 20.4636/152 | 13.6933/127 | 15.4027/153 | 13.9971/123 | 15.2345/138 | 15.4134/143 | 15.3524/143 | 15.0971/136 | 13.8248/150 | 42.6493/127 | 1ST/6, 00:01:03, 33%, 55 MPH, 1851 pts (viewed) |
| npre1 (T+502.56, pre-hold pair) | 58926B / `7dea309c51f1` | 14.4447/117 | 15.0458/159 | 13.9458/128 | 14.0254/143 | 16.0795/155 | 16.6802/155 | 16.7665/156 | 13.3125/126 | 17.2981/145 | 61.8421/145 | 2ND/6, 00:01:29, 45%, 41 MPH (viewed) |
| npre2 (T+503.13, pre-hold) | 62190B / `1f1724e7701f` | 12.7472/107 | 13.5691/133 | 12.4596/122 | 12.1078/126 | 15.2755/149 | 15.6092/146 | 15.6541/146 | 11.4346/123 | 18.3071/150 | 70.7309/157 | 2ND/6, 00:01:29, 46%, 43 MPH (viewed) |
| d-post1 (T+504.74) | 58794B / `c8b74e8f44aa` | 27.6286/139 | 15.0727/144 | 13.8302/144 | 13.6484/137 | 13.1703/142 | 13.1372/142 | 13.2363/142 | 13.4169/127 | 14.2612/132 | 26.2193/108 | 2ND/6, 00:01:32, 46%, 14 MPH (viewed) |
| d-post2 (T+505.31) | 57284B / `2a6aebe0c2f2` | 22.5814/120 | 15.8744/127 | 13.5643/136 | 12.5935/129 | 13.3368/126 | 13.7595/128 | 13.8544/129 | 11.4694/121 | 16.8614/147 | 40.8298/120 | 2ND/6, 00:01:33, 47%, 26 MPH (viewed) |
| d-post3 (T+505.88) | 59061B / `08271bf0cab1` | 17.3960/104 | 16.0621/128 | 13.3667/131 | 12.9440/130 | 14.9832/131 | 15.2528/130 | 15.3593/131 | 12.0151/123 | 18.1988/152 | 61.8140/142 | 2ND/6, 00:01:33, 47%, 33 MPH (viewed) |
| d-post4 (T+506.45) | 60104B / `a3b243a088fa` | 18.3236/105 | 16.8590/164 | 14.0071/137 | 13.6850/141 | 15.9551/151 | 16.4969/157 | 16.6038/158 | 12.8466/132 | 19.6544/156 | 63.2393/143 | 2ND/6, 00:01:34, 47%, 38 MPH (viewed) |
| d-post5 (T+507.02) | 58218B / `76ce0a311ccc` | 13.9816/112 | 13.0860/119 | 11.5481/128 | 11.5089/126 | 14.9411/138 | 14.8538/140 | 14.9675/142 | 10.6340/123 | 19.5262/152 | 71.2195/153 | 2ND/6, 00:01:35, 47%, 48 MPH (viewed) |
| d-post6 (T+507.59) | 60261B / `10cc670ebb0d` | 14.4264/143 | 15.0135/134 | 13.6876/145 | 14.8181/134 | 18.4083/179 | 18.9060/181 | 19.0531/182 | 13.2202/132 | 23.2388/185 | 123.4810/214 | 2ND/6, 00:01:36, 48%, 49 MPH (viewed) |
| d-post7 (T+508.16) | 58187B / `acc02832e875` | 12.0805/104 | 12.9108/112 | 11.9326/127 | 11.9252/127 | 15.1834/136 | 15.4598/140 | 15.5726/142 | 10.7769/120 | 17.3807/137 | 73.8682/155 | 2ND/6, 00:01:37, 48%, 48 MPH (viewed) |
| d-post8 (T+508.73) | 58948B / `9f5d5cd617c0` | 18.1653/109 | 14.5091/125 | 12.7428/119 | 12.5717/123 | 13.6858/129 | 14.2617/129 | 14.3535/130 | 11.3182/112 | 15.5471/122 | 54.1565/134 | 2ND/6, 00:01:38, 49%, 48 MPH (viewed) |
| d-post9 (T+509.31) | 56783B / `e24ad6eef9be` | 15.1590/112 | 13.0211/121 | 12.1349/121 | 12.2673/117 | 14.6982/140 | 14.8081/139 | 14.9352/140 | 10.8357/112 | 17.4408/136 | 81.0496/161 | 2ND/6, 00:01:39, 49%, 47 MPH (viewed) |
| d-post10 (T+509.88) | 57916B / `444e78cb7c31` | 36.9294/181 | 20.2426/193 | 18.6502/169 | 18.3337/180 | 16.6472/187 | 17.3493/190 | 17.4172/190 | 18.6847/163 | 15.3756/187 | 26.5851/102 | 2ND/6, 00:01:40, 49%, 16 MPH, RECOVER-0 (viewed) |

In-script (remote) vs PIL agreement: ≤0.07 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr/vs-pp scores at scale (e.g. scpre band 12.7890 vs
12.7230; x-post40 vs-pp 13.8331 vs 13.8248; mr-post8 band 29.9256 vs
29.9067); the known ~3–6× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.4921/8 remote vs 0.1833/4 PIL; sepre vs-se 0.4339/6
vs 0.0704/0 ≈ 6× — T27–T40 precedent); chain hops ≤0.06 (max Δ 0.052 on
x-post3→x-post8 16.5736 vs 16.6259). Dense hops have NO in-script remote
counterpart (blind — PIL only). Vs-panel remote receipt reads 0.68–1.02/
p99 9–21 on panel-side PIL 0.42–0.78 (≈1.3–1.6× inflation at the ~0.5
scale), so the < 2.0 whole bar holds even remotely (worst remote 1.0209,
~2.0× margin). The TAG crop gap re-confirmed at ~280× (2.6271 vs 0.0094).
Standing pattern holds: whole-frame bars calibrated in PIL transfer to
remote with single-digit inflation near zero and ~1× at scale ≥5;
text-dense crops need remote receipts or generous bars.

Batch-scorer bit-exact validation (committed `t41-cropdiff.py` vs numpy
batch port, mean/p99/max/npix identical 4/4): panel-panel
(`mr-stab2`→`pppre`) 0.0961/3/112; gameplay-motion (`d-post1`→`d-post2`)
9.9706/138/234; title-vs-ref (`a1-poll01`) 0.0453/0/31; SE-vs-ref
(`sepre`) 0.0704/0/52.

### R4 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1195 | 10.1267/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1175 | 0.1487/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2221 | 0.2501/6 | same screen |
| post8 → post15 (mc) | 0.1755 | 0.2010/5 | same screen |
| post15 → scpre (park span) | — | 0.1888/4 | same screen |
| scpre → zc-post1 | 7.1126 | 7.1394/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.2863 | 0.3098/9 | arrival settling |
| post3 → post8 (zc) | 0.2652 | 0.2875/7 | same screen |
| post8 → ccpre (park span) | — | 0.3011/8 | same screen |
| ccpre → sp-post1 | 9.3507 | 9.3885/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0364 | 0.0412/0 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0196 | 0.0214/0 | same screen |
| post8 → sppre (park span) | — | 0.0220/0 | same screen |
| sppre → pc-post1 | 5.2357 | 5.2596/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0893 | 0.0950/1 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0402 | 0.0451/0 | same screen |
| post8 → smpre (park span) | — | 0.0439/0 | same screen |
| smpre → rc-post1 | 0.5032 | 0.5315/11 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps in T32/T33) |
| post1 → post3 (rc) | 0.0329 | 0.0362/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0366 | 0.0429/0 | same screen |
| post8 → sepre (park span) | — | 0.0774/1 | same screen |
| sepre → sj-post1 | 10.5764 | 10.5989/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.1172 | 0.1313/2 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.1097 | 0.1189/1 | same screen |
| post8 → mrpre (park span) | — | 0.1505/2 | same screen |
| mrpre → mr-post1 | 12.6217 | 12.5849/150 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 1.7076 | 1.7269/65 | loading progress 17% → 97% |
| post3 → post8 (mr) | 25.3705 | 25.3827/253 | loading screen → race intro cinematic (no black frame captured this run — transition timing lottery) |
| post8 → post15 (mr) | 18.5578 | 18.5591/190 | cinematic → pre-race panel (panel arrived by +15, one sample early vs T34) |
| post15 → post25 (mr) | 0.4579 | 0.4642/21 | same screen (panel shimmer/animation) |
| post25 → post40 (mr) | 0.1909 | 0.1966/8 | same screen |
| post40 → stab1 (mr) | 0.1113 | 0.1177/4 | same screen |
| stab1 → stab2 (mr) | 0.2653 | 0.2669/12 | same screen |
| stab2 → pppre (park span) | — | 0.0961/3 | same screen |
| pppre → x-post1 | 14.6078 | 14.5899/153 | screen change within +1 s (pre-race panel → countdown/gate; decisive hop) |
| post1 → post3 (x) | 14.3456 | 14.3318/128 | countdown → live gameplay (gate → slope) |
| post3 → post8 (x) | 16.5736 | 16.6259/134 | live gameplay motion |
| post8 → post15 (x) | 7.7964 | 7.8295/126 | live gameplay motion |
| post15 → post25 (x) | 11.6945 | 11.7041/145 | live gameplay motion |
| post25 → post40 (x) | 17.8619 | 17.9043/158 | live gameplay motion |
| post40 → npre1 (span) | — | 15.2999/131 | live gameplay motion |
| npre1 → npre2 | BLIND (no in-script) | 7.5781/134 | live gameplay motion (PRE-hold pair, NO input between; 0.571 s exposure gap) |
| npre2 → d-post1 | BLIND (no in-script) | 12.8020/122 | live gameplay motion (hold window lands inside this hop; 1.611 s span incl. 1.038 s hold) |
| d1 → d2 | BLIND (no in-script) | 9.9706/138 | live gameplay motion (0.574 s gap) |
| d2 → d3 | BLIND (no in-script) | 7.9321/131 | live gameplay motion (0.571 s gap) |
| d3 → d4 | BLIND (no in-script) | 6.3576/126 | live gameplay motion (0.567 s gap) |
| d4 → d5 | BLIND (no in-script) | 8.5536/143 | live gameplay motion (0.567 s gap) |
| d5 → d6 | BLIND (no in-script) | 11.3822/106 | live gameplay motion (0.573 s gap) |
| d6 → d7 | BLIND (no in-script) | 9.4714/94 | live gameplay motion (0.572 s gap) |
| d7 → d8 | BLIND (no in-script) | 8.1467/108 | live gameplay motion (0.573 s gap) |
| d8 → d9 | BLIND (no in-script) | 8.0250/110 | live gameplay motion (0.571 s gap) |
| d9 → d10 | BLIND (no in-script) | 17.4674/155 | live gameplay motion (0.576 s gap; wall crash + RECOVER lands inside) |

### R4 arrival park (pre-race panel)

| Item | Value |
|---|---|
| Post-Enter frames | `t41r4-mr-post1.jpg` @T+330 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 17% Loading…; `mr-post3` @T+335: same screen, 97% Loading…; `mr-post8` @T+343: race intro cinematic, nightclub (`EA RADIO BIG / Like This / X-ecutioners / SSX 3` overlay); `mr-post15` @T+352: pre-race panel = arrival (one sample early vs T34's +25) |
| Stability N (panel) | 6 snaps (post15/25/40 + stab1/2 + pppre) spanning T+352→T+432 (80 s) |
| Whole-frame pairwise (PIL) | 0.0365–0.4642/p99 ≤21 across all 15 pairs (panel shimmer/animation; min post25–stab2 0.0365/1, max post15–post25 0.4642/21; JPEG shas distinct) |
| Vs-panel-ref (whole) | 0.42–0.78/p99 6–21 across all 6 (all under the 2.0 gate; margins 2.6–4.8×) |
| Vs-MR (whole) | 19.32–19.70/p99 154 across all 6 (not My Rules) |
| Vs-SE (whole) | 16.18–16.53/p99 159–160 across all 6 (not Select Event) |
| Vs-SM (whole) | 16.17–16.52/p99 159–161 across all 6 (not Select Mode) |
| Vs-SP (whole) | 16.38–16.64/p99 157 across all 6 (not Select Peak) |
| Vs-ZC (whole) | 19.89–20.28/p99 162–164 across all 6 (not Setup Character) |
| Vs-SC (whole) | 19.16–19.53/p99 173 across all 6 (not Select Character) |
| Vs-menu (whole) | 19.01–19.42/p99 177–179 across all 6 (not menu) |
| Vs-title (band) | 34.49–34.51/p99 184 across all 6 (not title) |
| SE-TAG (crop) | 50.7588/135 identical across all 6 (tagline band static within run; T40's run read 48.5996/133, T39's 50.7398/131, T38's 49.4844/132, T37's 48.2320/132, T36's 48.5186/132, T35's 48.5040/133, T34's 50.8209/132 — run-dependent, lineup/background phase) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Psymon / Marty / Griff / Moby / Viggo` (AI lineup differs run to run — T40: `Zoe/Griff/Viggo/Allegra/Elise/Seeiah`, T39: `Zoe/Marisol/Viggo/Nate/Allegra/Moby`, T38: `Zoe/Seeiah/Elise/Viggo/Kaori/Moby`, T37: `Zoe/Viggo/Eddie/Allegra/Kaori/Nate`, T36: `Zoe/Moby/Nate/Luther/Griff/Marty`, T35: `Zoe/Kaori/Brodi/Viggo/Elise/Griff`, T34: `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`); `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 80 s (all 6 snaps pre-race panel) |

### R4 arrival (countdown → live gameplay; input-free throughout)

| Snap (wall T+) | Race clock | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|
| x-post1 (T+436, +0.2 s after XCROSS keyup) | 00:00:00 | gates | 0% | 0 MPH | 0 | countdown `2` over the starting gate; riders in gates |
| x-post3 (T+440) | 00:00:02 | 5TH/6 | 1% | 38 MPH | 0 | leaving the gate, start straight, gondola |
| x-post8 (T+447) | 00:00:10 | 4TH/6 | 5% | 55 MPH | 0 | open slope, jump ramp ahead, two riders |
| x-post15 (T+456) | 00:00:23 | 2ND/6 | 12% | 50 MPH | 0 | banked icy turn, chevron fence |
| x-post25 (T+468) | 00:00:40 | 1ST/6 | 21% | 51 MPH | 611 | groomed run, fireworks arch, `2X COMBO 221`, `BS Rail` trick text |
| x-post40 (T+484) | 00:01:03 | 1ST/6 | 33% | 55 MPH | 1851 | slope with banners, rail structure |

Race-clock vs wall-clock (wall since XCROSS keyup 1790000747.766; race
clock read off HUD, HH:MM:SS; walls from 1 s stdout dates ±0.5 s):

| Snap | Wall since keyup (s) | Race clock (s) | Ratio |
|---|---|---|---|
| x-post1 | 0.2 | 0 | — (countdown) |
| x-post3 | 4.2 | 2 | 0.47 |
| x-post8 | 11.2 | 10 | 0.89 |
| x-post15 | 20.2 | 23 | 1.14 |
| x-post25 | 32.2 | 40 | 1.24 |
| x-post40 | 48.2 | 63 | 1.31 |

Stability N (X): not a static arrival — 6 snaps over 48 s, all 15
whole-frame pairs 7.83–22.83/p99 ≤165 (live gameplay motion; min
x-post8–x-post15 7.8295/126, max x-post15–x-post40 22.8266/165; JPEG shas
distinct). Vs-panel-ref 13.82–23.59 across all 6 (decisively non-panel);
vs-MR 11.88–15.10 (non-MR). No reclaim to any menu/panel (all 6 snaps
countdown/live gameplay, positions/progress/timer all advancing).

### R4 hold (1 s Left on live gameplay + blind sub-second series + tracking)

Hold row (proven keydown→keyup / phase match / delivery):

| Item | Value |
|---|---|
| Input | ONE `press_hold Left` (body verbatim T38's; `Left = Keyboard/Left` @ `PCSX2.ini:576`) |
| KEYDOWN wall | 1790000815.194264356 (T+503.19, uptime 536) |
| KEYUP wall | 1790000816.232688812 (T+504.23, uptime 537) |
| Hold duration | 1038.4 ms (T40's hold: 1038.0 ms — same input class delivery) |
| Pre-hold pair | `npre1` @T+502.56 (0.64 s before KEYDOWN) + `npre2` @T+503.13 (68 ms before KEYDOWN), NO input between |
| Last input before hold | XCROSS keyup @T+435.77 — 67.4 s of input-free racing before KEYDOWN |

Phase match (hold window vs T40's hold — match PHASE, not seed):

| Item | T40 hold window | T41 hold window | Δ vs T40 |
|---|---|---|---|
| Slot | T+503.09 (keydown) | T+503.19 (KEYDOWN) | +0.10 s (≈same slot; the 0.5 s pre-pair saving lands inside scheduler jitter) |
| Pre-pair race clocks | 00:01:28 / 00:01:29 | 00:01:29 / 00:01:29 | +1 s / +0 s |
| Pre-pair positions | 6TH/6 / 6TH/6 | 2ND/6 / 2ND/6 | front-of-pack vs back-of-pack (AI lineup/RNG differ run to run) |
| Pre-pair progress | 36% / 36% | 45% / 46% | +9/+10 pp (1 pp above the pre-tabled ≈36–45% band on npre2 — front-of-pack correlates with faster progress; clocks/slot match) |
| Series span | 10 snaps, +11.8 s wall / +17 s race | 10 snaps, +6.8 s wall / +11 s race | blind `sleep 0.5` shortens the span (same 10-snap shape) |

Pre-hold HUD (read off the viewed `npre1`/`npre2` snaps):

| Item | npre1 | npre2 |
|---|---|---|
| Race clock | 00:01:29 | 00:01:29 |
| Position | 2ND/6 | 2ND/6 |
| Progress | 45% | 46% |
| Speed | 41 MPH | 43 MPH |
| Score | 1851 pts | 1851 pts |
| Scene | Groomed run under wooden arch, totem poles | Same stretch, forest chute right |

Dense post-hold HUD series (read off viewed snaps; wall since hold keyup
1790000816.233; race advanced = race clock minus npre2 89 s; wall span =
SNAPSTART wall minus npre2 SNAPSTART 1790000815.126; nominal cadence =
`sleep 0.5` + ~65 ms snap, NO scoring):

| Snap (wall T+) | Wall span | Race clock (+adv) | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|---|
| npre1 (T+502.56) | −0.571 s (pre) | 00:01:29 (+0) | 2ND/6 | 45% | 41 MPH | 1851 | pre-hold baseline, groomed run under arch |
| npre2 (T+503.13) | +0 (pre) | 00:01:29 (+0) | 2ND/6 | 46% | 43 MPH | 1851 | pre-hold baseline, forest chute |
| d-post1 (T+504.74) | +1.611 s | 00:01:32 (+3) | 2ND/6 | 46% | 14 MPH | 1851 | carving left by trees (slow corner) |
| d-post2 (T+505.31) | +2.185 s | 00:01:33 (+4) | 2ND/6 | 47% | 26 MPH | 1851 | forest slope |
| d-post3 (T+505.88) | +2.756 s | 00:01:33 (+4) | 2ND/6 | 47% | 33 MPH | 1851 | forest slope, blue barrier |
| d-post4 (T+506.45) | +3.323 s | 00:01:34 (+5) | 2ND/6 | 47% | 38 MPH | 1851 | forest slope, blue barrier |
| d-post5 (T+507.02) | +3.891 s | 00:01:35 (+6) | 2ND/6 | 47% | 48 MPH | 1851 | banked turn, chevron barrier |
| d-post6 (T+507.59) | +4.464 s | 00:01:36 (+7) | 2ND/6 | 48% | 49 MPH | 1851 | banked turn |
| d-post7 (T+508.16) | +5.035 s | 00:01:37 (+8) | 2ND/6 | 48% | 48 MPH | 1851 | banked turn, chevron banners |
| d-post8 (T+508.73) | +5.608 s | 00:01:38 (+9) | 2ND/6 | 49% | 48 MPH | 1851 | banked turn, chevron banners |
| d-post9 (T+509.31) | +6.179 s | 00:01:39 (+10) | 2ND/6 | 49% | 47 MPH | 1851 | airborne through chevron gate |
| d-post10 (T+509.88) | +6.755 s | 00:01:40 (+11) | 2ND/6 | 49% | 16 MPH | 1851 | down/sliding against wall, `RECOVER - 0` meter |

Race-advance vs wall-span (race-advanced-since-npre2 / wall-since-npre2):

| Snap | Race adv (s) | Wall span (s) | Ratio |
|---|---|---|---|
| d-post1 | 3 | 1.611 | 1.86 |
| d-post2 | 4 | 2.185 | 1.83 |
| d-post3 | 4 | 2.756 | 1.45 |
| d-post4 | 5 | 3.323 | 1.50 |
| d-post5 | 6 | 3.891 | 1.54 |
| d-post6 | 7 | 4.464 | 1.57 |
| d-post7 | 8 | 5.035 | 1.59 |
| d-post8 | 9 | 5.608 | 1.60 |
| d-post9 | 10 | 6.179 | 1.62 |
| d-post10 | 11 | 6.755 | 1.63 |

Exposure gaps (SNAPSTART→SNAPSTART from ns `bsnap` stamps; snap capture
itself 63–72 ms START→END):

| Gap | Duration (s) | Contents |
|---|---|---|
| npre1 → npre2 | 0.571 | `sleep 0.5` + snap (≈0.57 s exposure) |
| npre2 → d-post1 | 1.611 | hold 1.038 s + `sleep 0.5` + keydown/focus overhead |
| d1 → d2 | 0.574 | `sleep 0.5` + snap |
| d2 → d3 | 0.571 | `sleep 0.5` + snap |
| d3 → d4 | 0.567 | `sleep 0.5` + snap |
| d4 → d5 | 0.567 | `sleep 0.5` + snap |
| d5 → d6 | 0.573 | `sleep 0.5` + snap |
| d6 → d7 | 0.572 | `sleep 0.5` + snap |
| d7 → d8 | 0.573 | `sleep 0.5` + snap |
| d8 → d9 | 0.571 | `sleep 0.5` + snap |
| d9 → d10 | 0.576 | `sleep 0.5` + snap |

Dense span npre1→d-post10: 7.326 s wall (T40: 12.90 s) for the same
12-snap shape — blind `sleep 0.5` capture delivers ≈0.57 s exposures vs
T40's ≈1.07 s.

Rider-pixel tracking series (committed `t41-track.py`, byte-identical to
T40's; RDC = rider dark-centroid + validity gate; SCPS40 = T37-frozen
±40 window; SCPS120 = wide ±120 window; whole hop = PIL per-hop from
§hops; T41F re-run reproduces the committed numbers exactly):

| Snap | RDC cx/cy (px) | RDC npix (frac) + gate | SCPS40 lag (corr) into this snap | SCPS120 lag (corr) into this snap | Whole hop into this snap |
|---|---|---|---|---|---|
| npre1 | 338.8 / 158.7 | 20385 (0.1452) INVALID (arch shade/forest floods ROI) | — | — | — |
| npre2 | 372.1 / 173.8 | 9058 (0.0645) INVALID (forest/shade) | +40 (0.63) RAIL | +56 (0.73) resolved | 7.5781/134 |
| d-post1 | 264.3 / 261.6 | 11848 (0.0844) INVALID (trees/shade) | +29 (0.02) off-rail, no match | +119 (0.37) off-rail, weak | 12.8020/122 |
| d-post2 | 286.4 / 168.6 | 12083 (0.0861) INVALID (forest/shade) | +39 (0.91) resolved | +39 (0.91) resolved | 9.9706/138 |
| d-post3 | 362.2 / 164.7 | 11081 (0.0789) INVALID (trees/trunks) | +0 (0.79) resolved | +0 (0.79) resolved | 7.9321/131 |
| d-post4 | 453.3 / 163.6 | 9615 (0.0685) INVALID (trees/shade) | +34 (0.90) resolved | +34 (0.90) resolved | 6.3576/126 |
| d-post5 | 303.0 / 285.2 | 1261 (0.0090) VALID | +40 (0.05) RAIL | +120 (0.64) RAIL | 8.5536/143 |
| d-post6 | 253.9 / 167.6 | 9717 (0.0692) INVALID (barrier/shade) | −20 (0.54) resolved | −20 (0.54) resolved | 11.3822/106 |
| d-post7 | 262.4 / 165.2 | 11670 (0.0831) INVALID (trees/shade) | +10 (0.33) weak | +93 (0.34) weak | 9.4714/94 |
| d-post8 | 290.8 / 153.9 | 7540 (0.0537) INVALID (trees/barrier) | +40 (−0.20) rail, no match | +119 (0.39) off-rail, weak | 8.1467/108 |
| d-post9 | 312.2 / 185.8 | 13757 (0.0980) INVALID (gate/shade) | −40 (0.63) RAIL | −48 (0.65) resolved | 8.0250/110 |
| d-post10 | 416.9 / 288.5 | 73670 (0.5247) INVALID (wall fills frame) | +37 (0.68) resolved | +37 (0.68) resolved | 17.4674/155 |

Sub-second distribution (11 hops at ≈0.57 s exposures + hold hop):

| Metric | Sub-second value (this run) |
|---|---|
| HUD position | 2ND/6 throughout — zero swaps, no decay (front-of-pack; AI lottery) |
| HUD progress/clock | monotonic 45% → 49%, +11 s race over +6.8 s wall (~1.6×, matches turbo) |
| RDC gate | gated OUT on 11/12 snaps (npix ≫ rider-scale: forest/arch-shade/wall flood the ROI); only d-post5 (1261) VALID — a singleton, so no gated delta exists anywhere in the series and no gated pair straddles the hold |
| SCPS40 | rails ±40 on 4/11 hops; the hold hop npre2→d-post1 reads +29 @ 0.02 — OFF-rail but uncorrelated (no match) |
| SCPS120 | rails ±120 on 1/11 hops (d4→d5 +120 @ 0.64); the hold hop reads +119 @ 0.37 — 1 px off-rail, weak (vs T40's +49 @ 0.79 clean resolve); d7→d8 also +119 @ 0.39 weak |
| Whole hops | 6.36–17.47 dense (motion-class throughout; smallest d3→d4 6.36, largest d9→d10 17.47 with the wall crash inside) |

Observed behavior characterization (tabled, not verdicts):

| Question | Observed |
|---|---|
| Did position change? | No — 2ND/6 on all 12 snaps (front-of-pack throughout; the hold hop holds 2ND→2ND and the pre-pair gap holds 2ND→2ND) |
| Did progress change? | Advances monotonically 45% → 49% (race-clock-driven, no jumps) |
| Did the clock change? | Advances steadily: +11 s race over +6.8 s wall (~1.6×, matches turbo) |
| Did speed change? | 41→43 (pre-pair) →14 (d1, slow carve by trees) →26→33→38→48→49→48→48→47 (banked-turn cruise) →16 (d10, down/sliding vs wall + `RECOVER - 0` meter) — one slow corner straddling the hold hop, one wall crash in the last hop |
| Did score change? | 1851 pts flat on all 12 snaps (no scoring events anywhere in the series; the 1851 was banked earlier — x-post25 611 → x-post40 1851) |
| Did heading change (rider pixels)? | RDC gated OUT on 11/12 snaps (forest/shade/wall flood the ROI); only 1 VALID snap, so no gated delta exists. SCPS40 rails ±40 on 4/11 hops with the hold hop OFF-rail at +29 @ 0.02 (no match). SCPS120 rails ±120 on 1/11 hops with the hold hop at +119 @ 0.37 (1 px off-rail, weak) — the T40 clean resolve (+49 @ 0.79) does not repeat at ≈0.57 s exposures on this forest/wall stretch |
| Any HUD discontinuity at the hold? | Position holds 2ND→2ND; speed drops 43→14 MPH across the hold hop (d1 carving by trees) and recovers to 26 by d2; progress/clock monotonic; no freeze, no menu, no reclaim |
| Isolation note | Single hold run at ~0.6 s exposures, no same-seed pairing (AI lineup/RNG differ run to run); compared against T40 below |
| Recipe (one variant per attempt) | The ±40 window at ≈0.57 s exposures leaves the hold hop off-rail but uncorrelated (+29 @ 0.02), the ±120 window loses T40's clean resolve (+119 @ 0.37 weak), and RDC still floods (forest/shade scenes) — a steer-discriminating window needs the OTHER T40-G1 arm: an ROI/gate retune for forest/wall scenes (higher dark threshold, smaller ROI, or a gradient-based rider lock), never combined with a further cadence change in one attempt. Next, ONE variant per attempt: the ROI retune with the same hold at the same `sleep 0.5` cadence, testing whether a gated RDC pair can straddle the hold |

Rail-rate comparison (T40 hold at ≈1.07 s gaps vs this ≈0.57 s hold run;
T40 values from its report):

| Item | T40 (1038.0 ms hold, ≈1.07 s) | T41 (1038.4 ms hold, ≈0.57 s) |
|---|---|---|
| Pre-input baseline | pair 00:01:28 / 00:01:29 | pair 00:01:29 / 00:01:29 |
| Pre-pair positions | 6TH / 6TH | 2ND / 2ND |
| Series-end position | 6TH/6 @00:01:46 41% (shorter span: blind capture) | 2ND/6 @00:01:40 49% (still shorter span: `sleep 0.5`) |
| Position swaps in series | 0 (6TH throughout) | 0 (2ND throughout) |
| Input-hop position step? | none (6TH→6TH) | none (2ND→2ND) |
| RDC gate-out rate | gated out 10/12 | gated out 11/12 |
| Gated RDC delta anywhere? | no (2 valids, non-adjacent) | no (1 valid — d-post5 singleton) |
| Gated-pair verdict | NO — none straddles the hold | NO — only one VALID snap in the series, none straddling the hold |
| SCPS40 rail rate | rails 4/11 | rails 4/11 |
| SCPS120 rail rate | rails 3/11 | rails 1/11 |
| Input-hop SCPS40 | +40 @ 0.74 RAIL | +29 @ 0.02 OFF-RAIL, no match |
| Input-hop SCPS120 | +49 @ 0.79 RESOLVED | +119 @ 0.37 off-rail (1 px), weak |
| Pre-pair-gap SCPS40 | −38 @ 0.55 resolved | +40 @ 0.63 RAIL |
| Pre-pair-gap SCPS120 | −38 @ 0.55 resolved | +56 @ 0.73 resolved |
| Whole-hop range (dense) | 6.72–16.60 | 6.36–17.47 |
| Clock ratio (race/wall) | ~1.5× | ~1.6× |

Stability N (dense): 12 snaps over 7.3 s, all 66 whole-frame pairs
6.16–25.17/p99 ≤180 (live gameplay motion throughout; min d5–d7
6.1599/107, max d6–d10 25.1706/180; all receiving distinct JPEG
frames). Vs-panel-ref 14.26–23.24 across all 12 (decisively non-panel).
No reclaim to any menu/panel anywhere in the series.

### R4 parked panel gate (PP-park gate)

| Item | Value |
|---|---|
| Gate definition | in-script: mrpre→mr-post1 hop > 5.0 (DEPARTED) AND (post40→stab1 hop < 1.0 AND stab1→stab2 hop < 1.0) AND stab2 vs-mr > 5.0 (NONMR), remote lossless scores |
| mrpre → mr-post1 hop (remote) | 12.6217 (12.5849/150 PIL) |
| PP-park run-up (remote) | post15→post25 0.4579 (0.4642/21 PIL); post25→post40 0.1909 (0.1966/8 PIL) |
| PP gate legs (remote) | post40→stab1 0.1113 (0.1177/4 PIL); stab1→stab2 0.2653 (0.2669/12 PIL); stab2 vs-mr 19.7056/154 (19.6969/154 PIL) |
| Gate | passes 3/3 legs → `PP-LIKE (departed + static x3 + non-MR) -> park for X-Continue Cross`, X-Continue Cross pressed |
| Local PIL gate | mrpre→mr-post1 = 12.5849 (> 1.0), post40→stab1 = 0.1177 (< 1.0), stab1→stab2 = 0.2669 (< 1.0), stab2 vs-mr = 19.6969 (> 5.0) — agrees 4/4 |

### R4 LIVE-LIKE proxy gate (in-script)

| Item | Value |
|---|---|
| Gate definition | in-script: pppre→x-post1 hop > 5.0 (DEPARTED) AND x-post40 vs-pp > 5.0 (NONPP) AND x-post15→x-post25 hop > 5.0 AND x-post25→x-post40 hop > 5.0 (motion ×2), remote lossless scores |
| Departure leg (remote) | pppre→x-post1 14.6078 (14.5899/153 PIL) |
| Arrival leg (remote) | x-post40 vs-pp 13.8331/150 (13.8248/150 PIL) |
| Motion leg ×2 (remote) | x-post15→x-post25 11.6945 (11.7041/145 PIL); x-post25→x-post40 17.8619 (17.9043/158 PIL) |
| Gate | passes 4/4 legs → `LIVE-LIKE (departed + non-panel + motion x2) -> blind pre-hold pair + hold + blind dense series` |
| Local PIL gate | legs read 14.5899/13.8248/11.7041/17.9043 (all > 5.0) — agrees 4/4 |
| TRUE live-race criterion | race clock advancing + positions/progress HUD read off the VIEWED snaps — x-post3→x-post40: 5TH→4TH→2ND→1ST→1ST, 00:00:02→00:01:03, 1%→33%, 38→55 MPH — live race, input-free |

### R4 success bars

| # | Bar | Result |
|---|---|---|
| G1 | full menu→MR chain + PP gate + XCROSS + x series to +40 + LIVE gate + pre-pair (0.57 s) + hold + dense 10-snap series (10 × ≈0.57 s) + live-racing hold phase, all scored post-hoc | observed: full R4 chain 61/61 snaps; menu→MR→panel→race→hold; pre-hold pair racing (00:01:29 2ND/6 45/46%), hold phase 2ND/6 mid-race, dense 10-snap series blind + fully post-hoc scored |
| G2 | rail rate vs T40 exact: track all 12 dense snaps (RDC gate/RDC deltas/SCPS40/SCPS120) + gated-pair verdict + hold-hop rows vs T40 | observed: full 12-snap tracking + all comparison rows in §hold + gated-pair verdict NO (singleton VALID) |
| G3 | xrun frame identities vs T40 (menu IC-pack) | observed: full 61-frame panel + identities (1 bit-identical load frame, near-identical menu tail) |
| G4 | all four T-lane input classes still tally-clean (534 ms-class + 67 ms tap + 1038 ms hold + 500 ms sham) | observed: R1/R2/R3/R4 add 21 × 534 ms-class (535.0–538.1 ms) + 1 × 1038.4 ms hold: 153/153 × 534 ms-class presses, 2/2 × 67 ms taps, 3/3 × 1 s Left steering holds (T38/T40/T41), 1/1 × 500 ms sham recorded, 0 delays > 5 ms beyond sleeps, 0 missing/unscheduled |
| G5 | run length + stop discipline | observed: T+520 vs T40 R2's T+524 (−4 s; expected −5.5 s from sleeps, ~1.5 s overhead jitter tabled); no bounded re-attempt (condition not met); stopping here with the recipe |

### R4 guest/trace receipts

| Item | Value |
|---|---|
| Guest clock | UPTIME:33 → UPTIME:553 |
| Vblank stream | first `WaitVblankStart` L417043 [1.1963]; 397 total, ALL ≤90 (LE90/LE110/LE140/LE350 all 397 — frozen) |
| BIOS + boot markers | `BIOS Found` L2; `ExecPS2` L142330 [0.8385] / L142426 [0.8662]; `ReBootStart` L142725 [0.8768]; first `UpdateVSyncRate` L456189 [1.4836] (`Mode Changed to DVD NTSC`), 15 total |
| Cubeb audio | ZERO `CUBEB_ERROR`/`cubeb_stream_init() failed`/`ReportErrorAsync` lines; L198 `Cubeb stream init successful` [0.5807]; tail streams stopped/destroyed normally (WSLg audio healthy on H36 — no modal) |
| Modules / errors | `LoadStartModule` ×18; `ERROR` ×0 |
| Syscall census | EE 11782578 (52 names, SET-IDENTICAL to T40 R2) · IOP 18935616 (155 names, SET-IDENTICAL) · lines 42868452, span 0.1287..509.4153; headline counts `GetThreadId` 4857338 (T40: 5032714), `libsd.006: sceSdGetParam` 16372 (T40: 17919), `libsd.010: sceSdGetAddr` 3766992 (T40: 3804768) |
| Trace tail | clean shutdown `[509.3981] NVRAM has not changed` → `[509.4153] Releasing host memory` (kill -TERM at T+~512, T41_DONE) |

### R4 stop table

| # | Condition | Hits? | Evidence |
|---|---|---|---|
| S1 | Park failure in ×3 attempts → NO-PARK | no (R4; R1/R2 hit it as ENVIRONMENT failures — re-ran per T27 §4) | R4: TITLE poll01; R1/R2: §T41-2/§T41-3 |
| S2 | Chain no-park (`NO-NONMENU` / `NO-MENU-PARK` / `NO-SC-PARK` / `NO-ZC-PARK` / `NO-SP-PARK` / `NO-SM-PARK` / `NO-SE-PARK` / `NO-MR-PARK`) | no (R4; R3 hit NO-SP-PARK game-side — tabled in §T41-4, not an attempt) | R4 chain nominal |
| S3 | PP no-park (`NO-PP-PARK`) | no | PP gate 3/3 |
| S4 | LIVE no-park (`NO-LIVE-PARK`) | no | LIVE gate 4/4 + TRUE live-race criterion HUD-read |
| S5 | NO phases (trial `sleep 10`) | no (frozen protocol) | `t41-auto.sh` (no trial-phase code) |
| S6 | 30-minute watchdog | no | R4 ran 520 s in one ssh call, exit 0 |
| S7 | Exit-nonzero run / dirty shutdown | no | exit 0, `T41_DONE`, clean SIGTERM; trace tail clean |
| S8 | SSD | STREAMED + VERIFIED post-restart (T41F): size + full sha + head/tail all match (§T41-6) | `/Volumes/Extreme SSD/ps2x-t4/emulog-t41r4.txt` |

## T41-6. Traces

| Trace | Size / sha | Identity | Location |
|---|---|---|---|
| `emulog.txt` (T41 R4) | 2745300674 B / `5b0a734900d41722718155925fecd1deffa879aeb7852cad69c7bcf198853d3f` | T41 R4, 42868452 lines, span 0.1287..509.4153 | bytesize live + SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t41r4.txt` (same size + same sha + head/tail slices match committed) + committed head/tail slices (149019 B sha `db4c6165…0257d4b` / 123878 B sha `230134d2…b805a`, 2000 lines each) |
| `emulog-pre-t41-20260921T141832Z.txt` (R3 NO-SP-PARK partial) | 1435642909 B / `98d17eb2caa6191a03366b248935344881eb1b0dbbe7b7abc42cd0e4f96e43ca` | T41 R3 | bytesize-only |
| `emulog-pre-t41-20260921T140920Z.txt` (R2 NO-PARK partial) | 1913796712 B / `e5f6ef2b7fdb0e864658c172ea42d70cb8ca098e7dc8fc50ba1bfc3e208765df` | T41 R2 | bytesize-only |
| `emulog-pre-t41-20260921T135533Z.txt` (R1 NO-PARK partial) | 1914391860 B / `2452f1dafb512aa0fea486ad5dec7dd34425bb7e54d91a1bb17974a99f9f07e7` | T41 R1 | bytesize-only |
| `emulog-pre-t41-20260921T134720Z.txt` (T40 R2 preserved at R1 boot) | 2782052936 B / `6fb038303bf95f6e7bce1a4e913e59201ec86c44831d3943491ba3a0dea367c` | T40 R2 (pre-run §T41-0; sizes re-verified in rotation post-restart) | bytesize-only |
| `emulog-pre-t40-20260921T114358Z.txt` (T40 R2's now-frozen ref) | re-verified `749b8c93dcb961ec047f5e0d506aedf11e92041c9f751a47ab6f3f3be1744249` | T40's frozen trace (reproduces T40) | bytesize-only |

SSD stream (T41F, post-restart): declared byte cap 2900000000 B for
`emulog-t41r4.txt` (expected 2745300674 B); streamed via
`ssh bytesize 'wsl cat …/logs/emulog.txt'` with `COPYFILE_DISABLE=1`;
landed rc=0 at exactly 2745300674 B (cap tracked, not exceeded); sha
`5b0a7349…53d3f` matches bytesize original; head-2000 sha `db4c6165…`
+ tail-2000 sha `230134d2…` match the committed pre-restart slices AND
re-streamed live slices. Stream VERIFIED (S8 passes).

Trace-head note: `t41r4-trace-head.txt` (149019 B) matches the T34–T40
heads' byte count but its sha (`db4c6165…`) differs from theirs
(`63af8334…`) — the standing pattern (boot-prefix content identical
except the run's own timestamps/addresses).

R1 census (R1's own trace, `t41r1-census.txt` 11980 B /
`t41r1-samples.txt` 5979 B): lines 29223690, span 0.1342..249.0483; EE
4547465 (52 names, SET-IDENTICAL to T40 R2 — incl. the cubeb
`MARK ERROR` pair at [0.5826]); IOP 13222130 (154 names — missing ONLY
`libsd.006: sceSdGetParam`, the audio-never-initialized correlate).
R4 census (`t41r4-census.txt` 11699 B / `t41r4-samples.txt` 5872 B):
per §guest/trace. R2/R3 censuses: not run (no-park runs, skipped
deliberately — no `t41r2/t41r3-census/samples` committed).

## T41-7. Exact commands

Pre-run pins (each line = one `ssh bytesize 'wsl …'` call, one `wsl` call
per ssh — WSL-tag rule):

- `wsl date -u; cat /proc/uptime; grep btime /proc/stat` — identity
- `wsl sha256sum /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt` + `wsl stat -c '%s %y' …` — binary pin
- `wsl git -C /home/brad/pcsx2-t4/pcsx2 rev-parse HEAD` + `wsl git -C … status --short` — tree pin
- `wsl ls -la /home/brad/pcsx2-t4/inputs/` — input sizes
- `wsl sha256sum …/dat/PCSX2/bios/….nvm` + `stat` — NVM pin
- `wsl grep -n 'Cross *= *Keyboard' …/inis/PCSX2.ini` + `Left` — bindings
- `wsl sha256sum t27-ref-title.ppm … t35-ref-panel.ppm` (9 refs) — ref pins
- `wsl ls -la …/dat/PCSX2/logs/` — rotation chain; `wsl df -h / /mnt/c` + `du -sh …/logs/` — headroom
- `wsl dmesg` → `t41-dmesg-hNN-*.txt`; `wevtutil qe System /c:30 (or 120) /rd:true /f:text` → `t41-eventlog-*.txt`

Staging + runs + fetches (T25 recipe; `export COPYFILE_DISABLE=1` on SSD
steps; byte caps declared + tracked):

- Stage: `scp` local `t41-*` → `C:\Users\bradr\pcsx2-t4\`, `wsl cp` → `/home/brad/pcsx2-t4/`, `wsl sha256sum` compare (match pre-run + post-restart)
- Run: `ssh bytesize 'wsl stdbuf -oL -eL /home/brad/pcsx2-t4/t41-auto.sh >…/boot-t41.log 2>…/boot-t41.stderr; echo EXIT:$?'` (one call, 30-min ceiling; R1/R2/R3/R4 each a single call)
- Dialogwatch (parallel, second ssh): `ssh bytesize 'wsl …/t41-dialogwatch[2].sh'` → local `t41r{3,4}-dialogwatch*.txt`
- Fetch: `wsl cp` snaps+logs → `/mnt/c/Users/bradr/pcsx2-t4/`, `scp` → local `t41r*-*`, `wsl rm` C: staging after each batch
- Analyze: `ssh bytesize 'wsl /home/brad/pcsx2-t4/t41-analyze.sh'` (R1 + R4 only) → `t41r{1,4}-{census,samples}.txt`; vcount piped on the SSD copy (post-restart)
- Manual snaps: `wsl DISPLAY=:99 import -window root t41-dialogcheck.jpg` (R3) / `t41-r4check.jpg` (R4 midrun)
- SSD stream (T41F): `ssh -o ConnectTimeout=30 bytesize 'wsl cat …/logs/emulog.txt' > '/Volumes/Extreme SSD/ps2x-t4/emulog-t41r4.txt'` (cap 2900000000 B; landed 2745300674 B rc=0); verify `shasum -a 256` + `head/tail -n 2000 | shasum`
- Post-hoc scoring: `python3 t41-track.py <12 dense snaps>` (committed, frozen); `/tmp/t41-batch.py --pairs …` (scratch, bit-exact 4/4 vs committed)

## T41-8. Gap rows

| # | Gap | Status |
|---|---|---|
| T41-G1 | Does SCPS40 resolve the hold hop at ≈0.57 s exposures? | OBSERVED: off-rail at +29 @ 0.02 (no match) — the other T40-G1 arm (ROI/gate retune for forest/wall scenes) is the next ONE variant, never combined with a further cadence change |
| T41-G2 | Can a gated RDC pair straddle the hold? | OBSERVED: NO — 11/12 gated out (forest/arch-shade/wall flood), only a d-post5 singleton VALID — same recipe as G1 |
| T41-G3 | Does SCPS120 stay resolved at ≈0.57 s? | OBSERVED: no clean resolve on this stretch — hold hop +119 @ 0.37 (1 px off-rail, weak) vs T40's +49 @ 0.79 |
| T41-G4 | Input-class tallies (534 ms / 67 ms / 1038 ms / 500 ms) | 153/153 · 2/2 · 3/3 · 1/1, 0 delays > 5 ms beyond sleeps, 0 missing/unscheduled |
| T41-G5 | In-guest audio-assert channel | cubeb-error grep on the R4 trace (0 lines) + cubeb init/success lifecycle + R1's in-trace `MARK ERROR` pair (R1) + IOP `sceSdGetParam` presence/absence (R4 present 16372, R1 absent) — POSITIVE + NEGATIVE controls both tabled |
| T41-G6 | C: headroom gate | 18 G post-session (gate ~5 GB+ PASSES); next session re-checks at pre-run |
| T41-G7 | R1's `start` + `a1-now` vs T40 (`start` brown-roadside, `a1-now` rail-grind) | attract lottery confirmed again (R4: rail-grind attract `start`, mid-trick `a1-now`); the ONLY fixed frames are title→menu→…→panel + load 17% (bit-identical) |
| T41-G8 | dc1394/IIDC error line in `dmesg` | absent on all 7 H32/H34/H35/H36/H39 reads AND the post-restart VM's dmesg (standing absence) |
| T41-G9 | `/tmp/.X11-unix` mount | belt-and-braces, not load-bearing (Xvfb starts cleanly per run regardless); T32 G11 – T40 G11 stand |
| T41-G10 | Boot-to-boot `Ioctl failed`/`AcceptAsync` | AcceptAsync ZERO in-window all 4 runs; Ioctl 18-line pcsx2-boot dxg bursts at R1/R2 T+0–3 s edges + pre-window boot noise only, zero mid-run (H34: zero Ioctl of any kind) |
| T41-G11 | Batch-scorer status | numpy batch port bit-exact 4/4; stays uncommitted scratch (same as T39/T40); every score reproduces with committed `t41-cropdiff.py` |
| T41-G12 | H33 + H37 + H38 unattributed VMs | H33 = WSLg-audio forensics + dialogwatch-v1 staging (tool-header receipt only); H37/H38 = 77 s each, unattributed (H38 overlaps the BLOCKED pre-restart SSD-stream attempt); no committed reads isolate any of the three — receipt gap, tabled |
| T41-G13 | R3's parallel Start@T+155 | no in-log receipt survives (manual second-ssh press); consistent-with-inert + timeline cross-checked in §T41-4 — precision unrecoverable, tabled as stated |
| T41-G14 | R2/R3 censuses | deliberately not run (no-park runs) — no `t41r2/t41r3-census/samples`; R1 census covers the cubeb failure, R4 census the full run |
| T41-G15 | T41F post-restart drift | ZERO drift on every pin/ref/staged/sha/slice re-verified; disk deltas are run-growth, tabled in §T41-0 |

## Evidence files (`local/research/T41/`)

Scripts/tools: `t41-auto.sh` (50912 B, `4533904a…b6b727d`),
`t41-analyze.sh` (762 B, `0b0cc435…bc2a655`),
`t41-cropdiff.py` (3441 B, `ac114212…0826a53`, = T40's),
`t41-track.py` (3312 B, `58afa004…91c108`, = T40's),
`t41-vcount.sh` (435 B, `105cd092…39107d76`, = T40's),
`t41-dialogwatch.sh` (1411 B, `158842d4…286ccf`),
`t41-dialogwatch2.sh` (1592 B, `d9c7a4c1…41faa`).
Snaps: 81 JPGs (15 R1 + 3 R2 + 1 R3 dialogcheck + 62 R4 incl.
midrun-check), 4910746 B total.
R1: `t41r1-stdout.txt` (24003 B, 373 lines), `t41r1-stderr.txt`
(90812 B, 1975 lines), `t41r1-poll.log` (5068 B, 98 lines),
`t41r1-census.txt` (11980 B), `t41r1-samples.txt` (5979 B).
R2: `t41r2-stdout.txt` (24087 B, 374 lines), `t41r2-stderr.txt`
(90812 B, 1975 lines), `t41r2-poll.log` (5068 B, 98 lines).
R3: `t41r3-stdout.txt` (17345 B, 255 lines), `t41r3-stderr.txt`
(56206 B, 1060 lines), `t41r3-dialogwatch.txt` + `t41r3-dialogwatch2.txt`
(688 B each).
R4: `t41r4-stdout.txt` (34720 B, 512 lines), `t41r4-stderr.txt`
(136991 B, 2551 lines), `t41r4-poll.log` (10313 B, 168 lines),
`t41r4-census.txt` (11699 B), `t41r4-samples.txt` (5872 B),
`t41r4-dialogwatch.txt` (1470 B), `t41r4-trace-head.txt` (149019 B),
`t41r4-trace-tail.txt` (123878 B).
Session: `t41-dmesg-h32-pre.txt` (28266 B, 416 lines),
`t41-dmesg-h32-postr1.txt` (36594 B, 523 lines),
`t41-dmesg-h32-postr2.txt` (41610 B, 587 lines),
`t41-dmesg-h34-postr3.txt` (28103 B, 416 lines),
`t41-dmesg-h35-pre.txt` (28706 B, 423 lines),
`t41-dmesg-h36-postr4.txt` (30729 B, 450 lines),
`t41-dmesg-h39-final.txt` (28650 B, 422 lines),
`t41-eventlog-pre.txt` = `t41-eventlog-postr1.txt` (16279 B each,
byte-identical), `t41-eventlog-final.txt` (64372 B, 120 entries).
SSD (not in git): `/Volumes/Extreme SSD/ps2x-t4/emulog-t41r4.txt`
(2745300674 B, `5b0a7349…53d3f`).

---
Report tail receipt: T41 complete — R1/R2 environment NO-PARKs (cubeb
modal, full forensics), R3 game-side NO-SP-PARK (full forensics), R4
exit 0 with FULL CHAIN + ONE 1038.4 ms Left hold @T+503.19 on live
2ND/6 + 10-snap blind series at 10×≈0.57 s; scoring COMPLETE (RDC
11/12 gated, SCPS40 4/11 with hold hop OFF-rail +29 @ 0.02, SCPS120
1/11 with hold hop +119 @ 0.37, dense hops 6.36–17.47); SSD trace
stream VERIFIED (size + sha + head/tail); T41-1…T41-8 complete in
T40's shapes; evidence committed `[T41]` finish (no push).
