# T40 report — sub-second exposure series around the 1 s hold: post-hoc scoring, no in-script gaps (bytesize, no lease)

Brief: T40 (T39's G1: T38 G1(b) — sub-second exposures). Tables, no
verdicts. One boot ran on bytesize (R1: chain reproduced to live
gameplay, ONE 1 s D-pad Left HOLD on the live race at a matched phase,
PRE-hold pair + BLIND back-to-back 10-snap post-hold series scored
post-hoc with rider-pixel tracking + T38/T39 rail-rate comparison);
laptop-side work was ssh/scp + local reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T39/REPORT.md` (all of it: R1
reproduced the chain to LIVE gameplay, sham window with NO input
(1003.7 ms gap @T+504.62) at a matched phase (pre-pair 00:01:24 4TH/6 36% /
00:01:29 4TH/6 38%), dense 10-snap no-input series to 00:02:10 6TH/6 55%
showing the CONTROL distribution — 4 position swaps + decay 4TH→6TH, RDC
gated out 9/12, SCPS40 rails 5/11, SCPS120 rails 4/11 incl. the pre-pair gap
and the sham hop — matching T36's tap / T37's tap / T38's hold behavior
class; G1 proposes T38 G1(b), still open: sub-second exposures — this brief
takes it). This brief executes T39's G1. T39's scripts reused (copied, not
modified).

Experiment contract (up front): hypothesis — T36–T39's ~3 s exposure gaps
(1 s sleep + ~2 s in-script scoring per snap) rail SCPS at ±40 AND ±120
and flood RDC, so capturing the dense phase back-to-back at ~1 s wall
cadence (sleep 1, NO per-snap scoring calls) and scoring post-hoc yields
sub-second-class exposures where SCPS stops railing and a gated RDC pair
can straddle the hold; observable — pre-hold pair = live race (race clock
+ position/progress HUD read off the viewed snaps), the hold row (proven
1 s keydown→keyup + phase match vs T38's hold / T39's sham window), dense
10-snap series + per-snap HUD + tracking metrics + per-hop whole diffs,
all scored post-hoc from fetched snaps; screen content read off viewed
snaps; alternatives — SCPS still rails / RDC still floods at ~1 s
exposures (→ table the exact observed rates + noise floors and STOP with a
recipe), run provably never reached live gameplay at a matched phase (→
ONE bounded re-attempt allowed); stop — table the rail-rate comparison vs
T38/T39 + gated-pair verdict + recipe, one input variant per attempt,
never blind multi-presses.

## T40-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T40; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T40]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; verified
on VM-H29 before R1):

| Item | T4 value | T40 observed | Match |
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
| T39 reference snaps present | — | all 12 sizes reproduce T39 §chain (`npre1/2` 49082/62601, `d-post1..10` 58956/49671/61062/61678/54200/60878/59677/56302/70901/53087) | yes |
| Free space | — | WSL `/` 871 G pre; C: 1.4 G pre (100%, CRITICAL — T39 G8; trace streamed via `wsl cat`, no C: staging); laptop `/` 4.5 Gi avail; SSD 255 Gi free | yes |
| Live trace pre-run | — | `emulog.txt` 2898445035 B sha `749b8c93…74249` = T39 R1 (preserved at R1 boot) | yes |

Phase-match targets (tabled BEFORE the run — T38 R1's hold window /
T39 R1's sham window, match PHASE not seed; AI lineup/RNG differ run to
run):

| Item | T38 hold-window value | T39 sham-window value | T40 hold-window target |
|---|---|---|---|
| Hold slot | T+504.54 (keydown) | T+504.62 (SHAMSTART) | ≈T+505 (same script slot) |
| Pre-pair race clocks | 00:01:25 / 00:01:31 | 00:01:24 / 00:01:29 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | 2ND/6 / 2ND/6 | 4TH/6 / 4TH/6 | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 40% / 44% | 36% / 38% | ≈36–45% (±5 pp) |
| Series span | 10 snaps over +26 s wall / +41 s race | 10 snaps, +26 s wall / +41 s race | 10 snaps over ≈+15 s wall (shorter: blind capture) |

Blind-capture cadence (tabled BEFORE the run — the deliberate change):

| Item | T39 (in-script scoring) | T40 (blind + post-hoc) |
|---|---|---|
| Dense-phase shape | `sleep 1` + 2 scoring calls per snap + 11 in-script whole hops at end | `sleep 1` + capture only; ns wall stamps per snap; ZERO scoring calls |
| Expected exposure gap | ~3 s (1 s sleep + ~2 s scoring) | ~1–2 s (1 s sleep + snap overhead xwd→ppm→jpg; measured post-hoc from ns stamps) |
| Pre-pair gap | `sleep 2` + scoring (~4 s: T39 T+498→T+502) | `sleep 1`, no scoring (≈1–2 s) |
| Dense span (npre1→d-post10) | +34 s wall (T39 T+498→T+532) | ≈+15 s wall expected |
| Run length | T39 R1 562 s (202 s over ≤6 min guidance) | shorter by ≈20 s (scoring removed); delta tabled |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps
with the committed tools):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log | scp via C: staging (T25 recipe) | `t40r1-*.jpg`, `t40r1-poll.log` |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t40-cropdiff.py`, bit-exact validated 4/4 (T39 protocol); committed tool reproduces any score | screen chain table + xrun frame identities vs T39 R1 |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking | committed `t40-track.py` (byte-identical to T39's) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. View all snaps | local reads | HUD per snap (clock/position/progress/speed/score) |
| 6. Rail-rate comparison | — | RDC gate-out / SCPS40 / SCPS120 rates vs T38/T39 + gated-pair verdict |

Rail rates to beat (tabled BEFORE the run — T38 hold / T39 control dense
phases, 12 snaps / 11 hops each):

| Metric | T38 (1037.3 ms hold, ~3 s gaps) | T39 (no-input sham, ~3 s gaps) | T40 question |
|---|---|---|---|
| RDC gated out | 10/12 | 9/12 | does any gated pair now straddle the hold? |
| SCPS40 rails | 6/11 | 5/11 | does the ±40 railing stop at ~1 s? |
| SCPS120 rails | 7/11 | 4/11 | does the ±120 railing stop at ~1 s? |
| Input-hop SCPS120 | −120 @ 0.15 RAIL | −120 @ 0.16 RAIL | resolved or still railed? |
| Dense whole-hop range | 10.07–22.33 | 8.58–20.62 | motion-class floor at ~1 s? |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) on VM-H29 |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t40-{auto,analyze,vcount,cropdiff}.sh/.py`, `t40-{r1-census,samples}.txt` (via analyze), `t40-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t40-*.txt` (rotation chain, see trace table), `boot-t40.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t40*` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | pre-run section below; ZERO in-window (see WSL session log) |

Script receipts (frozen BEFORE the run):

| Item | Value |
|---|---|
| `t40-cropdiff.py` | byte-identical to T39's (`cmp` clean), sha `ac114212…0826a53` |
| `t40-track.py` | byte-identical to T39's (`cmp` clean), sha `58afa004…91c108` (T38's frozen value) |
| `t40-vcount.sh` | byte-identical to T39's (`cmp` clean), sha `105cd092…39107d76` |
| `t40-analyze.sh` | output-name deltas only (`t40-census/samples`), sha `f8b6c8f3…fa954db` |
| `t40-auto.sh` | T39 copy + T40 renames + `press_hold` restored (body verbatim T38's; 2 comment lines differ) + `bsnap` blind-capture wrapper + blind dense phase (ONLY deliberate change), sha `1325cb04…e350d`; `bash -n` clean; zero `sham` references; exactly one `press_hold Left` call; dense block contains zero scoring calls (one `score_` mention in a comment) |
| Staged shas | all 4 WSL-staged shas match local (auto `1325cb04…`, analyze `f8b6c8f3…`, vcount `105cd092…`, cropdiff `ac114212…`) |
| PPM self-check | panel ref 0.0000/0 pre-run |
| T39 originals | untouched (tree clean at commit; T40 dir is new; a pre-existing untracked `ps2_log.txt` seen at session start was removed externally mid-session, not by me) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 11:02:40 (H28) | H28 create (T39's post-everything VM, after T39's session) | eventlog-pre (IDs 292/67/291/233/232/102/291/291 @07:02:40) |
| 2 | 11:08:25 | H28 teardown (pre-session restart, NOT by me) | eventlog-pre (IDs 71/69/233/234/234 @07:08:25) |
| 3 | 11:41:32 ([0] VM-H29) | VM-H29 started fresh ~2 s before first ssh | btime `…892`, eventlog-pre (IDs 292/67/291/233/232/102/291/291 @07:41:33) |
| 4 | 11:41:34–11:42:5x | Pre-run checks (all ssh exit 0) + C:-staging + WSL-staging (shas match local) + X11 mount + PPM self-check 0.0000/0, all on VM-H29 | `t40-dmesg-vmH29-pre.txt` (0 AcceptAsync, 440 lines — captured at uptime ~2 s) |
| 5 | 11:43:52–11:47:13 ([145]→[~230] H29) | R1 single-shot wedged at T+185 (ZC hops): C: drained 1.4 G → 116 KB by VHDX growth → guest exec wedged permanently; run ssh killed by me ~12:13; NO T40_DONE | wedged stdout 8771 B + stderr 41831 B (local copies), 48-line NUL-torn poll log, 1.1 GB partial trace `b77089b3…` |
| 6 | 11:46:44–12:05:15 | Volsnap ID 24 (shadow storage cannot grow) + ID 35 (shadow copies aborted); `wsl --shutdown` + `wsl --terminate` stuck; recovery by me: `sc stop WslService` → taskkill vmwp 17860 → taskkill wslservice 7252 → STOPPED → start → RUNNING | eventlog-post (no H29 teardown pair — VM was killed; partial 71/69 @08:31:23 + 233 @08:29:20 + 7034 @08:30:51) |
| 7 | ~12:04 | Cleared 20 stale `emulog-*.txt` transfer copies (~30 GB) from `C:\Users\bradr\pcsx2-t4\` (by me; redundant staging, WSL originals + SSD copies retained) | C: 116 KB → 29.1 GB (`fsutil`) |
| 8 | 12:31:23 ([0] VM-H30) | VM-H30 fresh boot (my service-restart recovery) | btime `…883`, eventlog-post (create IDs @08:31:23) |
| 9 | 12:31:25–12:32:30 | Emulog preservation + wedge forensics + R2 re-verifies (T39 R1 `749b8c93…` intact, wedge partial `b77089b3…`, NVM/build/scripts intact, wedged-R1 snaps deleted) + X11 mount + PPM self-check 0.0000/0, all on VM-H30 | `t40-dmesg-vmH30-fresh.txt` (0 AcceptAsync, 423 lines, 5 `Ioctl failed` — captured at uptime ~2 s, before dxg queries complete) |
| 10 | 12:33:58–12:41:22 ([75]→[599] H30) | R2 single-shot exit 0, `T40_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage; ZERO event entries in-window) | exit 0, 61 snaps, trace sha `6fb03830…` |
| 11 | 12:41:22–~12:45 | R2 dmesg read (IMMEDIATELY after run ssh) + analyze (exit 0) + vcount + poll wc + all R2 fetches (exit 0) on VM-H30 | `t40-dmesg-vmH30-post.txt` (451 lines, 1 AcceptAsync [614.65] — post-window) |
| 12 | 12:45:45 | VM-H30 teardown (post-everything restart, NOT by me) | eventlog-post head (IDs 71/69/233/234/234 teardown @08:45:45) |
| 13 | 12:46:03–~12:50 (VM-H31) | VM-H31 fresh: identity + dmesg + NVM/trace/rotation re-verifies + head/tail slices + SSD stream + df/du-final (exit 0) | `t40-dmesg-vmH31-post.txt` (450 lines, 0 AcceptAsync) |
| 14 | event log | Newest-30 reads (pre/post/final): boundaries H28-create 07:02:40 → H28-teardown 07:08:25 → H29-create 07:41:33 → Volsnap 24 @07:46:44 → Volsnap 35 @08:05:15 → H29-kill (partial 71/69 @08:31:23) → H30-create 08:31:23 → H30-teardown 08:45:45 → H31-create 08:46:03; in-window R2 (08:33:58–08:41:22 local) entries: ZERO of any kind | `t40-eventlog-{pre,post,final}.txt` |
| 15 | dmesg noise | `Ioctl failed` 23/5/23/5 across the 4 files (H29-pre 23 boot noise; H30-fresh 5 — early read at uptime ~2 s; H30-post 23, all at uptime 3.08–16.43, pre-window — the run adds zero new dxg lines; H31-post 5 — early read at uptime ~2 s); kill-pattern grep matches only the 2 `panic=-1` cmdline echoes per file; H30-post notes a torn systemd journal (from the wedge kill — benign, tabled) | dmesg files |

AcceptAsync exact counts with uptime-stamp positions relative to the R2
window (T_BOOT uptime 75 → end 599, all on VM-H30):

| Committed file | Lines | AcceptAsync count | Uptime stamps | Position vs run window |
|---|---|---|---|---|
| `t40-dmesg-vmH29-pre.txt` | 440 | 0 | — | earlier VM, pre-window; outside |
| `t40-dmesg-vmH30-fresh.txt` | 423 | 0 | — | same VM, pre-window; outside |
| `t40-dmesg-vmH30-post.txt` | 451 | 1 | [614.65] | same VM, post-window (run ended uptime 599); ZERO in-window |
| `t40-dmesg-vmH31-post.txt` | 450 | 0 | — | different VM (post-everything, no run); outside |

## T40-1. Hold + blind-series shape + tracking method (frozen BEFORE the run) + LIVE calibration

Tool: `t40-cropdiff.py` (copy of T39's, byte-identical; `cmp` clean;
`t40-vcount.sh` byte-identical to T39's; `t40-analyze.sh` differs only in
output names). Title text-band method unchanged (thresholds frozen: TITLE
band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu
mean < 2.0; NONMENU / NONSC / NONZC / NONSP / NONSE / NONMR whole-vs-ref
mean > 5.0; DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). Panel
reference reused (`t35-ref-panel.ppm`, already staged, sha re-verified).
No new reference (no new static screen to gate on). Remote PPM-mode
self-check pre-run: panel ref 0.0000/0.

Hold selection (tabled BEFORE the run — T38's input class, restored):

| Item | Value |
|---|---|
| Input | ONE `press_hold Left` (1 s `sleep` between keydown/keyup; body verbatim T38's) |
| Binding | `Left = Keyboard/Left` (`PCSX2.ini:576`, re-verified pre-run) |
| Slot | Same script slot the T38 hold / T39 sham occupied (≈T+505, after the pre-pair) |
| When | After the X arrival series, on the LIVE-LIKE proxy gate (deep in live gameplay per T35's/T36's/T37's/T38's/T39's race shape) |

Blind-series shape (tabled BEFORE the run — the ONLY deliberate change vs
T39):

| Item | Value |
|---|---|
| Pre-pair | `bsnap npre1`, `sleep 1`, `bsnap npre2` — no input between, no scoring |
| Hold | `press_hold Left "HOLD_LEFT"` |
| Post-hold | 10 × (`sleep 1`, `bsnap d-postN`) — no scoring |
| Stamps | each `bsnap` logs `SNAPSTART_WALL`/`SNAPEND_WALL` (ns precision) + uptime + T+ to the poll log; exposure gaps recovered post-hoc |
| Post-hoc | per-snap HUD + full vs-ref panel + all 11 dense hops + RDC/SCPS40/SCPS120, all from fetched snaps |

Tracking method (tabled BEFORE the run — frozen in committed
`t40-track.py`, byte-identical to T39's, sha `58afa004…91c108`):

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

Script deltas vs `t39-auto.sh` (committed originals untouched; `t40-auto.sh`
is the adapted copy):

| Area | T39 script | T40 script |
|---|---|---|
| Chain | park phase + full menu→MR chain + PP gate + XCROSS + x series to +40 + LIVE gate + pre-pair + sham + dense d-post1..10 + 11 per-hop whole diffs | identical through the LIVE-LIKE gate; dense phase differs (see below) |
| Dense input | ONE `sham_window` (1 s `sleep`, NO xdotool) | ONE `press_hold Left` (1 s `sleep`, T38's input class, body verbatim) |
| Dense capture | `snap` + 2 scoring calls per snap; `sleep 2` pre-pair gap; 11 in-script whole hops at end | `bsnap` (capture + ns stamps, NO scoring); `sleep 1` pre-pair gap; NO in-script hops — all scored post-hoc |
| Self-tests | SELF_TEST + … + SELF_MR + SELF_PP | unchanged (all 11 re-run) |
| No-park paths | explicit `NO-PARK` + … + `NO-LIVE-PARK` | unchanged (still clean shutdown + `T40_DONE`, trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
batch port of `t40-cropdiff.py` (`/tmp/t40-batch.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical)
against the committed tool on 4 diverse pairs (same 4-pair protocol as
T39; pairs + scores tabled in §T40-2). Any score reproduces with the
committed `t40-cropdiff.py`, slower. The 9 ref PPMs were reused from
`/tmp/t36-refs/` for post-hoc scoring (all 9 shas re-verified, match
§T40-0).

## T40-2. R1 — DISCARDED (environment failure: C:-full guest wedge at T+185)

R1 booted on VM-H29 (T_BOOT 1789991038, 11:43:58 UTC) and ran the chain
normally through MENU-LIKE + SC-LIKE into the ZC series (last output: `ZC
post+8` @T+185, 11:47:13 UTC), then the guest wedged permanently: zero
script output for 25+ min, all WSL exec (`wsl echo`, new `wsl` calls) timing
out while Windows-side calls (`echo`, `wsl --list`, `wevtutil`, `sc`,
`taskkill`, `fsutil`) kept working. Root cause: C: drained 1.4 GB → 116 KB
by VHDX growth (1.1 GB partial emulog + PPMs by T+185); Volsnap ID 24
(11:46:44, shadow storage cannot grow) + ID 35 (12:05:15, shadow copies
aborted). `wsl --shutdown` and `wsl --terminate Ubuntu` both stuck;
recovery (by me, all Windows-side): `sc stop WslService` (STOP_PENDING) →
`taskkill /F /IM vmwp.exe` (PID 17860) → `taskkill /F /IM wslservice.exe`
(PID 7252) → STOPPED → `sc start WslService` → RUNNING → fresh VM-H30.
No VM restart/teardown entry exists for the wedge in the event log (the
VM was killed, not shut down).

| Item | Value |
|---|---|
| R1 window | 11:43:52–11:47:13 UTC (last output), stall to ~12:13, VM killed ~12:30 |
| Last chain state | MENU-LIKE + SC-LIKE fired; ZC post+8 scored; wedged in ZC hops |
| Poll log | 48 lines on disk (BEHIND stdout's ZC series — `tee` appends failed on full disk) + ~600 NUL-byte torn tail (allocated-but-unwritten blocks) |
| Partial trace | `emulog.txt` 1103446016 B sha `b77089b3…ab22f5`, mtime frozen at wedge (rotated at R2 boot; bytesize-only) |
| Preserved T39 R1 | `emulog-pre-t40-20260921T114358Z.txt` 2898445035 B sha `749b8c93…` re-verified intact — zero evidence lost |
| NVM / build / scripts | all re-verified intact post-wedge (`da021d2a…`, `6719f5d6…`, 4 staged shas match) |
| R1 verdict | DISCARDED as an environment failure (disk-full guest wedge), effects-unverifiable per the T27 §4 rule → re-run as R2; wedged-R1 snaps deleted unfetched (mid-chain duplicates of a discarded run); stdout/stderr/eventlog/poll-log/trace tails preserved in the record above |
| C: fix (by me) | cleared 20 stale `emulog-*.txt` transfer copies (~30 GB, T17→T36 era) from `C:\Users\bradr\pcsx2-t4\` — redundant staging (WSL originals + SSD copies retained); NOT the owner's game installs (Steam 342 G / Ubisoft 110 G / GOG 85 G untouched) nor Docker (16 G) nor Temp (7 G); C: 116 KB → 29.1 GB (27 G at R2 boot) |

## T40-3. R2 — race reproduced, ONE 1 s hold + blind sub-second series on live gameplay

Run: `t40-auto.sh`, ONE fresh boot, T_BOOT wall 1789993958 (uptime 75,
VM-H30), 12:33:58–12:41:22 UTC (uptime 75→599 = 524 s; 164 s over the
≤6 min guidance — the X phase + dense tail; full dmesg coverage, zero
flaps in-window; −38 s vs T39 R1's 562 s from blind capture), WID 2097159
(same as T31 R1 / T32 R1 / T33 R1 / T33 R2 / T34 R1 / T35 R1 / T36 R1 /
T37 R1 / T38 R1 / T39 R1), exit 0, `T40_DONE`, clean SIGTERM shutdown.
SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC
0.0000/0, SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM 0.0000/0, SELF_SE
0.0000/0, SELF_SETAG 0.0000/0, SELF_MR 0.0000/0, SELF_PP 0.0000/0.
Attempt 1 of ≤3 consumed; attempts 2–3 not needed (chain advanced to the
hold, dense series mapped). No bounded re-attempt run (pre-hold = racing
at a matched phase — re-attempt condition not met, brief stops here).

### R2 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+101, score 0.4331/6 remote / 0.0467/1 PIL (T39 R1: 0.4329/6 / 0.0468/1 — same detector reading, near-identical frame, see xrun) | Cross 536.1 ms @T+98.68 (attract-skip) + Start 538.0 ms @T+101.96 (on title, ≤1.8 s after exposure) | Main Menu by +5 s; menu-like gate (non-title + whole-static 0.0312/0.0131) + post25-vs-menu 0.2964/5 → park for menu Cross |
| A2–A3 | not run (chain advanced) | — | — |

### R2 cross-run frame identities (T40 R2 vs T39 R1; T40 names)

| Frame | T40 R2 size / sha12 | T39 R1 size | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | 58352 B / `d977309dd891` (cp-identical, pair 0.0000/0) | 58374 B | differ; pair 0.0358/0 max 60 (title snowflake shimmer) |
| a1-post3 | 49992 B / `aac721f29b0f` | 50085 B | whole pair 0.0634/1 max 56 |
| a1-post8 | 49991 B / `3b452bae03c2` | 50006 B | whole pair 0.0768/1 max 60 |
| a1-post15 | 49640 B / `c1663a1045f8` | 49634 B | whole pair 0.0007/0 max 6 (near-identical — shimmer breaks the 5-run bit-identity streak) |
| a1-post25 | 49739 B / `703c5ebfa619` | 49786 B | whole pair 0.0323/0 max 44 |
| menupre | 49677 B / `595d8d8925d3` | 49618 B | whole pair 0.0044/0 max 7 |
| mc-post1/3/8/15 | 70373/70335/70346/70398 B | 70264/70525/70313/69999 B | whole pairs 0.143/3, 0.146/3, 0.149/4, 0.100/2 |
| scpre | 70592 B / `0cd2cd562599` | 70172 B | whole pair 0.3007/7 |
| zc-post1/3/8 | 51461/51434/51362 B | 51477/51639/51209 B | whole pairs 0.109/2, 0.158/4, 0.153/3 |
| ccpre | 51493 B / `5d64bee7fe60` | 51452 B | whole pair 0.2170/6 |
| sp-post1/3/8 | 65282/65525/65228 B | 65460/65481/65238 B | whole pairs 0.072/1, 0.070/0, 0.002/0 |
| sppre | 65510 B / `75cfba411fb7` | 65741 B | whole pair 0.1045/0 |
| pc-post1/3/8 | 67992/67564/67443 B | 67682/67446/67675 B | whole pairs 0.098/0, 0.036/0, 0.066/1 |
| smpre | 67563 B / `2531d09a10f9` | 67471 B | whole pair 0.0376/0 |
| rc-post1/3 | 69843/69493 B | 69432/69450 B | whole pairs 0.0374/0, 0.0098/0 (near-identical; snowflake shimmer breaks bit-equality) |
| rc-post8 | 69445 B / `ae268aad5b7b` | 69757 B | whole pair 0.0617/0 |
| sepre | 69847 B / `6f652d2d20d0` | 69541 B | whole pair 0.0672/0 |
| sj-post1/3/8 | 58989/59213/58883 B | 58893/58515/59006 B | whole pairs 0.101/1, 0.139/1, 0.123/1 |
| mrpre vs T39 `mrpre` | 59416 B / `64f73d74dc98` | 58502 B | whole pair 0.1326/1 |
| mr-post1 (load) | 66749 B / `023fa9d54af9` | 66795 B | differ; pair 1.5941/57 (17% vs 18% Loading) |
| mr-post3 (load) | 67057 B / `2f737ddbe777` | 67359 B | differ; pair 2.0559/73 (97% vs 98% Loading) |
| mr-post8 | 54901 B / `b443c29af553` | 54859 B | differ; pair 3.3798/76 (both race-intro cinematic, different phase/track: Jerk it Out Caesars 39 Minutes of Bliss vs Deep End Utah Saints Remix Swollen Members Balance) |
| mr-post15/25/40 | 59569/59642/59793 B | 60179/60222/60071 B | whole pairs 0.6464/15, 0.6209/14, 0.3994/7 (both pre-race panel; AI lineup differs run to run) |
| mr-stab1/2 | 59607/59601 B | 59732/60267 B | whole pairs 0.4881/8, 0.6789/17 (both pre-race panel; lineup differs) |
| pppre vs T39 `pppre` | 59550 B / `b9453f3dc224` | 60157 B | whole pair 0.6103/13; whole-vs-panel-ref 0.6447/14 PIL |
| x-post1 (countdown) | 69196 B / `b4ba253030bc` | 69714 B | differ; pair 0.8667/29 (both countdown `2` gates — near-frozen) |
| x-post3 | 67575 B / `b7a7e10e2af2` | 68085 B | whole pair 4.8181/74 (similar gate exit: 5TH/5TH at 00:00:02, 1%, 39 MPH) |
| x-post8/15/25/40 | 68820/59321/64756/66355 B | 68371/63871/68572/72684 B | whole pairs 4.68/84, 6.66/94, 14.98/140, 10.70/104 (gameplay lottery) |
| npre1/2 | 52069/50992 B | 49082/62601 B | whole pairs 17.13/148, 7.30/82 (gameplay lottery) |
| d-post1..10 | 48456/51050/57207/53965/56852/50871/54132/53532/59421/62473 B | 58956/49671/61062/61678/54200/60878/59677/56302/70901/53087 B | whole pairs 12.38/134, 8.28/103, 10.05/126, 13.98/148, 8.33/102, 14.93/176, 12.85/112, 14.96/170, 8.85/134, 16.27/154 (gameplay lottery) |

No bit-identical frames this run (nearest: a1-post15 0.0007/0 max 6 —
snowflake shimmer breaks the T35→T39 five-run bit-identity streak).

### R2 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789994056.682 → 1789994057.218 | 536.1 ms | T+98.68→99.21 | 173 | `a1-now` attract (16.6484/167 remote; 16.6487/167 PIL — viewed) | `a1-poll01` TITLE (0.4331/6; 0.0467/1 — viewed) |
| A1 Start (Return) | 1789994059.962 → 1789994060.500 | 538.0 ms | T+101.96→102.50 | 176→177 | `a1-pre` ≡ `a1-poll01` (sha `d977309dd891`, TITLE) | `a1-post3` Main Menu (16.2581/139; 16.2601/138) |
| MENU Cross (K) | 1789994099.256 → 1789994099.791 | 535.6 ms | T+141.25→141.79 | 216 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2873/5 remote; 0.0279/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2436/106; vs-sc 0.4542/7; titleband 12.5576/164) |
| ZOE Cross (K) | 1789994139.434 → 1789994139.971 | 536.6 ms | T+181.43→181.97 | 256 | `scpre` Select Character, Zoe selected (vs-sc 0.4794/7 remote; 0.1251/2 PIL; vs-menu 10.1443/105; vs-title 12.7765/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.1968/100; vs-zc 0.5205/9; titleband 15.8476/128) |
| CONT Cross (K) | 1789994168.280 → 1789994168.820 | 540.0 ms | T+210.27→210.81 | 285 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4818/9 remote; 0.2495/7 PIL; vs-sc 7.2924/100; vs-title 15.9280/128 — viewed) | `sp-post1` Select Peak (vs-zc 9.4666/154; vs-sp 0.3695/6; titleband 23.1245/171) |
| PEAK Cross (K) | 1789994197.274 → 1789994197.810 | 536.1 ms | T+239.27→239.81 | 314 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.3750/6 remote; 0.0274/0 PIL; vs-zc 9.4729/154; vs-title 23.1294/171 — viewed) | `pc-post1` Select Mode (vs-sp 5.4209/121; vs-sm 0.4610/7; titleband 26.3170/183) |
| RACE Cross (K) | 1789994226.826 → 1789994227.368 | 541.5 ms | T+268.82→269.36 | 343→344 | `smpre` Select Mode, Race highlighted (vs-sm 0.4151/6 remote; 0.0666/0 PIL; se-tag 14.3278/89 remote; vs-sp 5.3751/121; vs-title 26.3170/183 — viewed) | `rc-post1` Select Event (vs-sm 0.8409/13; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789994258.278 → 1789994258.816 | 538.1 ms | T+300.27→300.81 | 375 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6271/11 remote, 0.0094/0 PIL; vs-se 0.4258/6, 0.0624/0; vs-sm 0.8581/14; vs-sp 5.4986/121; vs-title 26.2104/183 — viewed) | `sj-post1` My Rules (vs-se 10.6617/143; vs-mr 0.4407/8; titleband 9.8968/137) |
| ENTER Cross (K) | 1789994287.154 → 1789994287.690 | 536.1 ms | T+329.15→329.69 | 403→404 | `mrpre` My Rules, Continue highlighted (vs-mr 0.4842/8 remote; 0.1750/4 PIL; vs-se 10.7145/143; vs-title 9.8533/137 — viewed) | `mr-post1` game load 17% (vs-mr 12.6253/150; vs-pp 21.0600/169; titleband 17.6707/170 — viewed) |
| XCROSS (K) | 1789994392.980 → 1789994393.518 | 537.7 ms | T+434.98→435.51 | 509→510 | `pppre` pre-race panel, X Continue (vs-pp 0.8996/15 remote; 0.6447/14 PIL — viewed) | `x-post1` countdown 2, starting gate (vs-pp 14.5795/153; titleband 18.6775/149 — viewed) |
| HOLD_LEFT (Left) | 1789994461.098 → 1789994462.136 | 1038.0 ms | T+503.09→504.13 | 577→578 | `npre2` live race 00:01:29 6TH/6 36% (post-hoc PIL only — blind: vs-pp 13.0530/110; vs-title 29.1488/142 — viewed) | `d-post1` live race 00:01:33 6TH/6 37% (vs-pp 10.7711/128; titleband 35.6838/185 — viewed) |

Within-dwell receipts R2: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (1 s resolution) → Start-keydown ≤1.8 s; T33-R2-measured title
persistence 15–17 s ⇒ press inside the window with an order of magnitude
to spare. Start-keyup → MenuCross-keydown 38.8 s; MenuCross-keyup →
ZoeCross-keydown 39.6 s; ZoeCross-keyup → ContCross-keydown 28.3 s;
ContCross-keyup → PeakCross-keydown 28.5 s; PeakCross-keyup →
RaceCross-keydown 29.0 s; RaceCross-keyup → SnowJamCross-keydown 30.9 s;
SnowJamCross-keyup → EnterCross-keydown 28.3 s; EnterCross-keyup →
XCross-keydown 105.3 s (panel settling + PP gate); XCross-keyup →
Hold-keydown 67.6 s (X arrival series + LIVE gate; no dwell pressure — the
race runs input-free, T35 G1 precedent).

### R2 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / whole vs panel-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT
(dense-phase T+ refined to 0.01 s from ns `bsnap` stamps in the hold
table below).

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | Whole vs panel | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+97) | 54982B / `6dc6289a3c89` | 24.6767/172 | 17.3873/153 | 15.8016/166 | 15.6356/141 | 14.8785/155 | 15.4260/154 | 15.4041/154 | 14.7944/145 | 14.1722/148 | 29.4170/85 | Attract |
| a1-now (T+97, pre-Cross) | 69681B / `ad97b87f290a` | 16.6487/167 | 11.9963/140 | 13.2403/140 | 11.5399/132 | 14.9940/179 | 15.7657/176 | 15.8198/177 | 12.8239/135 | 21.7680/179 | 56.3118/165 | Attract (viewed) |
| a1-poll01 (T+101, pre-Start) | 58352B / `d977309dd891` | 0.0467/1 T | 14.1355/151 | 11.3102/152 | 12.2550/146 | 15.3725/156 | 16.1512/158 | 16.2492/160 | 9.7697/143 | 22.1514/183 | 106.6242/205 | TITLE (viewed) |
| a1-pre (T+101) | 58352B / `d977309dd891` | 0.0467/1 | 14.1355/151 | 11.3102/152 | 12.2550/146 | 15.3725/156 | 16.1512/158 | 16.2492/160 | 9.7697/143 | 22.1514/183 | 106.6242/205 | TITLE (identical cp) |
| a1-post3 (T+105) | 49992B / `aac721f29b0f` | 16.2601/138 | 0.0624/1 | 10.1228/105 | 6.9106/93 | 10.3947/170 | 10.9243/177 | 10.9433/177 | 10.0896/96 | 19.3208/178 | 26.1710/106 | Main Menu |
| a1-post8 (T+111) | 49991B / `3b452bae03c2` | 16.2911/138 | 0.0609/1 | 10.1205/105 | 6.9194/93 | 10.3888/170 | 10.9253/177 | 10.9502/177 | 10.0893/96 | 19.3283/178 | 26.1557/106 | Main Menu |
| a1-post15 (T+118) | 49640B / `c1663a1045f8` | 16.2622/138 | 0.0263/0 | 10.1069/105 | 6.9076/93 | 10.3850/170 | 10.9180/177 | 10.9429/177 | 10.0757/96 | 19.2981/178 | 26.1710/106 | Main Menu |
| a1-post25 (T+129) | 49739B / `703c5ebfa619` | 16.2622/138 | 0.0413/0 | 10.1115/105 | 6.9039/92 | 10.3880/170 | 10.9211/177 | 10.9461/177 | 10.0806/96 | 19.3098/178 | 26.1713/106 | Main Menu |
| menupre (T+139, pre-MCross) | 49677B / `595d8d8925d3` | 16.2622/138 | 0.0279/0 | 10.1065/105 | 6.9066/93 | 10.3845/170 | 10.9174/177 | 10.9424/177 | 10.0747/96 | 19.2990/178 | 26.1323/106 | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+142) | 70373B / `6073e4aa13e2` | 12.4794/163 | 10.1758/105 | 0.0887/1 | 7.2782/100 | 11.4069/158 | 11.8726/158 | 11.9411/158 | 5.6660/117 | 19.4745/172 | 26.5695/90 | Select Character, Zoe |
| mc-post3 (T+147) | 70335B / `83398b128299` | 12.4964/163 | 10.1553/106 | 0.0749/1 | 7.2540/101 | 11.3844/158 | 11.8447/157 | 11.9134/157 | 5.6496/117 | 19.4570/172 | 26.5673/90 | Select Character |
| mc-post8 (T+155) | 70346B / `a1810c450aa9` | 12.4732/163 | 10.1525/105 | 0.2752/5 | 7.2426/100 | 11.3633/158 | 11.8284/157 | 11.8994/157 | 5.6334/117 | 19.4628/172 | 26.5695/90 | Select Character |
| mc-post15 (T+164) | 70398B / `64a80a06f6cc` | 12.4587/163 | 10.1452/105 | 0.0645/1 | 7.2251/100 | 11.3643/158 | 11.8246/157 | 11.8939/157 | 5.6299/117 | 19.4320/172 | 26.5695/90 | Select Character |
| scpre (T+178, pre-ZCross) | 70592B / `0cd2cd562599` | 12.7091/163 | 10.0773/105 | 0.1251/2 | 7.1706/100 | 11.3504/158 | 11.8155/157 | 11.8844/157 | 5.6615/117 | 19.4653/172 | 26.5696/90 | Select Character, Zoe selected (viewed) |
| zc-post1 (T+182) | 51461B / `aab4a4c8cf32` | 15.8255/128 | 6.9272/92 | 7.1680/100 | 0.2875/7 | 9.3534/153 | 10.1413/164 | 10.2523/164 | 7.0369/103 | 20.1898/165 | 15.2956/91 | Setup Character, Zoe |
| zc-post3 (T+187) | 51434B / `18d5a8d5e70e` | 15.8687/128 | 6.9184/92 | 7.2509/99 | 0.2427/7 | 9.3697/154 | 10.1284/164 | 10.2417/165 | 7.0396/103 | 20.1882/164 | 15.2967/91 | Setup Character |
| zc-post8 (T+195) | 51362B / `fe15d322e27b` | 15.8313/128 | 6.9299/93 | 7.1399/100 | 0.2187/5 | 9.3779/153 | 10.1244/164 | 10.2356/164 | 7.0886/103 | 20.1696/164 | 15.2956/91 | Setup Character |
| ccpre (T+207, pre-ContCross) | 51493B / `5d64bee7fe60` | 15.9045/129 | 6.9257/93 | 7.2638/100 | 0.2495/7 | 9.3764/153 | 10.1318/164 | 10.2450/164 | 7.0409/103 | 20.1913/164 | 15.2984/91 | Setup Character, Zoe + Continue (viewed) |
| sp-post1 (T+211) | 65282B / `07d12e8db93f` | 23.1216/171 | 10.4212/170 | 11.3415/158 | 9.3869/153 | 0.0229/0 | 5.2208/121 | 5.3268/121 | 9.8255/138 | 16.5530/157 | 14.0026/89 | Select Peak, Peak 1 |
| sp-post3 (T+216) | 65525B / `13375d6f0f98` | 23.1274/171 | 10.4234/170 | 11.3526/158 | 9.3934/153 | 0.0273/0 | 5.2294/121 | 5.3306/121 | 9.8400/138 | 16.5628/157 | 14.0316/89 | Select Peak |
| sp-post8 (T+224) | 65228B / `69848c733b64` | 23.1259/171 | 10.4061/170 | 11.3503/158 | 9.3729/153 | 0.0042/0 | 5.2073/121 | 5.3099/121 | 9.8376/138 | 16.5440/157 | 14.0026/89 | Select Peak |
| sppre (T+236, pre-PeakCross) | 65510B / `75cfba411fb7` | 23.1275/171 | 10.4235/170 | 11.3551/158 | 9.3929/153 | 0.0274/0 | 5.2291/121 | 5.3301/121 | 9.8424/138 | 16.5628/157 | 14.0254/89 | Select Peak, Peak 1 highlighted (viewed) |
| pc-post1 (T+240) | 67992B / `67907d4a0b37` | 26.3046/183 | 10.9857/178 | 11.8744/157 | 10.1747/164 | 5.2554/121 | 0.1167/1 | 0.5649/14 | 10.5386/143 | 16.4428/160 | 14.1390/88 | Select Mode, Race |
| pc-post3 (T+245) | 67564B / `d43712b487e8` | 26.3046/183 | 10.9388/178 | 11.8267/157 | 10.1263/164 | 5.2068/121 | 0.0662/0 | 0.5373/11 | 10.4881/143 | 16.4379/160 | 14.1390/88 | Select Mode |
| pc-post8 (T+253) | 67443B / `2cfcf235871d` | 26.3028/183 | 10.9296/178 | 11.7933/157 | 10.1180/164 | 5.1976/121 | 0.0575/0 | 0.5289/11 | 10.4534/143 | 16.4296/160 | 14.1390/88 | Select Mode |
| smpre (T+265, pre-RaceCross) | 67563B / `2531d09a10f9` | 26.3046/183 | 10.9392/178 | 11.8266/157 | 10.1265/164 | 5.2068/121 | 0.0666/0 | 0.5376/11 | 10.4883/143 | 16.4382/160 | 14.1390/88 | Select Mode, Race highlighted (viewed) |
| rc-post1 (T+270) | 69843B / `6282f16249b8` | 26.1964/183 | 10.9728/178 | 11.8823/157 | 10.2442/164 | 5.3186/122 | 0.5469/12 | 0.0686/0 | 10.6238/144 | 16.4611/160 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+274) | 69493B / `6eee3742e523` | 26.1964/183 | 10.9428/178 | 11.8628/157 | 10.2199/164 | 5.2875/121 | 0.5151/10 | 0.0375/0 | 10.5937/144 | 16.4310/160 | 0.0494/2 | Select Event |
| rc-post8 (T+282) | 69445B / `ae268aad5b7b` | 26.1943/183 | 10.9549/178 | 11.8509/157 | 10.2307/164 | 5.3031/121 | 0.5151/9 | 0.0529/0 | 10.5729/144 | 16.4388/160 | 0.0367/1 | Select Event |
| sepre (T+296, pre-SnowJamCross) | 69847B / `6f652d2d20d0` | 26.1964/183 | 10.9884/178 | 11.9041/157 | 10.2563/164 | 5.3399/121 | 0.5690/13 | 0.0624/0 | 10.6414/144 | 16.4707/160 | 0.0094/0 | Select Event, Snow Jam highlighted (viewed) |
| sj-post1 (T+301) | 58989B / `dc4791b6c2e3` | 9.8737/136 | 10.0931/97 | 5.6337/117 | 7.0780/104 | 9.8481/137 | 10.4533/143 | 10.6173/143 | 0.1308/2 | 19.5689/153 | 26.4884/93 | My Rules, Continue |
| sj-post3 (T+306) | 59213B / `8cef8804cc97` | 9.8275/135 | 10.1580/99 | 5.6971/118 | 7.1209/105 | 9.8997/137 | 10.4966/143 | 10.6607/143 | 0.1871/4 | 19.6333/154 | 26.4136/92 | My Rules |
| sj-post8 (T+314) | 58883B / `de95625787ec` | 9.9686/135 | 10.0277/96 | 5.6475/117 | 7.0008/104 | 9.8005/138 | 10.4115/143 | 10.5755/143 | 0.1201/1 | 19.5641/153 | 26.4126/92 | My Rules |
| mrpre (T+326, pre-EnterCross) | 59416B / `64f73d74dc98` | 9.8273/135 | 10.1580/100 | 5.7018/118 | 7.1273/105 | 9.8975/138 | 10.5048/143 | 10.6693/143 | 0.1750/4 | 19.6340/154 | 26.4124/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+330) | 66749B / `023fa9d54af9` | 17.6261/169 | 15.3901/157 | 14.3024/157 | 13.7599/154 | 14.8373/154 | 15.2048/153 | 15.3320/154 | 12.5965/149 | 21.0483/169 | 91.0281/224 | Loading 17% (viewed) |
| mr-post3 (T+335) | 67057B / `2f737ddbe777` | 17.8430/171 | 15.4460/157 | 14.3034/158 | 13.7455/154 | 14.8456/154 | 15.2125/153 | 15.3404/154 | 12.5836/150 | 21.0779/169 | 88.4285/222 | Loading 97% (viewed) |
| mr-post8 (T+343) | 54901B / `b443c29af553` | 27.7056/237 | 21.5858/218 | 21.1974/205 | 21.4300/192 | 20.6437/218 | 21.2770/218 | 21.1946/218 | 20.4315/197 | 19.2603/190 | 52.1536/159 | Race intro cinematic, nightclub, EA RADIO BIG / Jerk it Out / Caesars / 39 Minutes of Bliss (viewed) |
| mr-post15 (T+352) | 59569B / `b4d855b86abe` | 34.5204/184 | 19.0633/177 | 19.1917/171 | 19.9337/162 | 16.3987/157 | 16.2087/159 | 16.2131/159 | 19.3576/153 | 0.6854/16 | 48.5996/133 | Pre-race panel |
| mr-post25 (T+365) | 59642B / `cfabb63df87f` | 34.5245/184 | 19.1533/178 | 19.2714/171 | 20.0114/163 | 16.4425/157 | 16.2919/160 | 16.2962/159 | 19.4325/153 | 0.5862/11 | 48.5996/133 | Pre-race panel |
| mr-post40 (T+383) | 59793B / `b8e9a08a0345` | 34.5208/184 | 19.2795/178 | 19.3826/171 | 20.1348/164 | 16.5257/157 | 16.3945/160 | 16.3985/160 | 19.5519/153 | 0.4553/7 | 48.5996/133 | Pre-race panel |
| mr-stab1 (T+406) | 59607B / `a74567bed1c4` | 34.5226/184 | 19.1149/178 | 19.2386/171 | 19.9834/163 | 16.4280/157 | 16.2527/159 | 16.2570/159 | 19.4054/153 | 0.6263/13 | 48.5996/133 | Pre-race panel |
| mr-stab2 (T+419) | 59601B / `1360d954fb45` | 34.5209/184 | 19.0978/178 | 19.2208/171 | 19.9592/163 | 16.4099/157 | 16.2441/160 | 16.2485/159 | 19.3819/153 | 0.6362/14 | 48.5996/133 | Pre-race panel |
| pppre (T+432, pre-XCross) | 59550B / `b9453f3dc224` | 34.5226/184 | 19.1014/178 | 19.2265/171 | 19.9703/163 | 16.4210/157 | 16.2408/160 | 16.2452/159 | 19.3930/153 | 0.6447/14 | 48.5996/133 | Pre-race panel, X Continue (viewed) |
| x-post1 (T+436) | 69196B / `b4ba253030bc` | 18.6687/149 | 15.8270/161 | 13.8801/136 | 15.6592/151 | 15.6777/157 | 15.9032/156 | 15.9767/157 | 13.2570/129 | 14.5291/153 | 93.2604/175 | Countdown 2, starting gate, 00:00:00, 0 MPH (viewed) |
| x-post3 (T+440) | 67575B / `b7a7e10e2af2` | 23.8897/138 | 13.5259/142 | 13.2108/139 | 12.9109/134 | 12.3667/136 | 12.3227/138 | 12.4304/138 | 11.7191/108 | 15.9818/146 | 50.6782/139 | 5TH/6, 00:00:02, 1%, 39 MPH (viewed) |
| x-post8 (T+447) | 68820B / `8d36fdff88a9` | 13.6816/127 | 16.2801/142 | 13.2296/149 | 14.1104/154 | 15.6302/158 | 16.3272/161 | 16.4465/162 | 11.6065/116 | 20.8697/165 | 96.2006/180 | 4TH/6, 00:00:10, 5%, 50 MPH (viewed) |
| x-post15 (T+455) | 59321B / `e818a8fb05a7` | 13.1242/135 | 18.3940/147 | 14.1782/148 | 15.1770/154 | 17.4048/154 | 17.9328/161 | 18.0224/164 | 12.6426/124 | 22.6164/170 | 117.4152/198 | 1ST/6, 00:00:24, 12%, 49 MPH (viewed) |
| x-post25 (T+467) | 64756B / `47ca430fd5d6` | 17.8189/137 | 13.5277/153 | 12.5867/145 | 11.2937/147 | 12.5375/154 | 12.8654/156 | 12.9673/156 | 11.3123/118 | 18.7435/163 | 25.7906/101 | 1ST/6, 00:00:40, 21%, 58 MPH, `OUT OF BOUNDS` banner (viewed) |
| x-post40 (T+484) | 66355B / `eca5de3c06cc` | 20.0960/144 | 13.4626/143 | 12.9546/128 | 12.1852/127 | 13.8002/147 | 14.4433/155 | 14.5431/155 | 11.8833/123 | 16.2926/147 | 39.5193/119 | 5TH/6, 00:01:02, 28%, 46 MPH (viewed) |
| npre1 (T+501.96, pre-hold pair) | 52069B / `472885825e6a` | 30.6517/144 | 14.9711/179 | 14.4554/143 | 13.0278/159 | 12.7903/159 | 13.1104/159 | 13.1716/159 | 13.4934/139 | 15.4835/147 | 25.7106/107 | 6TH/6, 00:01:28, 36%, 75 MPH (viewed) |
| npre2 (T+503.03, pre-hold) | 50992B / `842efd94afc5` | 29.1488/142 | 14.8314/154 | 14.6006/149 | 14.2093/146 | 12.9155/147 | 13.2028/148 | 13.2710/148 | 13.8223/129 | 13.0530/110 | 22.4110/92 | 6TH/6, 00:01:29, 36%, 60 MPH (viewed) |
| d-post1 (T+505.14) | 48456B / `861c6d83fc1a` | 35.6838/185 | 18.2378/175 | 18.0313/173 | 18.2278/157 | 15.1769/171 | 15.4404/172 | 15.5269/172 | 17.4476/157 | 10.7711/128 | 21.3832/98 | 6TH/6, 00:01:33, 37%, 16 MPH, rock wall (viewed) |
| d-post2 (T+506.21) | 51050B / `4ff839e86ee4` | 18.5611/103 | 11.6595/109 | 10.6896/118 | 9.6773/106 | 12.0672/120 | 12.1110/121 | 12.2155/121 | 9.1680/102 | 17.6685/132 | 41.3513/121 | 6TH/6, 00:01:35, 37%, 48 MPH (viewed) |
| d-post3 (T+507.28) | 57207B / `73409c340664` | 20.7673/113 | 15.6776/140 | 15.1618/130 | 14.5600/130 | 14.5317/140 | 14.9101/141 | 14.9925/142 | 13.5512/118 | 14.1791/130 | 31.7105/115 | 6TH/6, 00:01:36, 38%, 55 MPH (viewed) |
| d-post4 (T+508.35) | 53965B / `c127e2ffa179` | 31.1481/154 | 18.4348/160 | 18.3271/156 | 18.0980/151 | 15.2639/158 | 15.5641/160 | 15.6235/160 | 17.1022/136 | 11.4768/124 | 23.4459/93 | 6TH/6, 00:01:38, 38%, 51 MPH (viewed) |
| d-post5 (T+509.43) | 56852B / `cfc30116d6ad` | 24.8908/144 | 16.2431/157 | 14.4396/142 | 12.6253/144 | 14.4082/155 | 15.0321/159 | 15.1515/159 | 12.7456/137 | 20.1171/164 | 32.1538/110 | 6TH/6, 00:01:39, 39%, 49 MPH (viewed) |
| d-post6 (T+510.50) | 50871B / `4c3b66450455` | 40.6581/206 | 17.7154/214 | 18.1506/176 | 18.0326/203 | 16.0579/207 | 15.7918/206 | 15.8491/206 | 17.7458/171 | 14.1059/148 | 24.3362/99 | 6TH/6, 00:01:41, 39%, 27 MPH, `RECOVER` meter (viewed) |
| d-post7 (T+511.57) | 54132B / `d24e2c9d8ee4` | 23.4132/156 | 9.4290/134 | 12.3769/146 | 10.5569/124 | 13.0911/167 | 12.9224/170 | 12.9722/170 | 11.9399/132 | 16.8288/154 | 20.9385/95 | 6TH/6, 00:01:42, 40%, 9 MPH, rider down/sliding (viewed) |
| d-post8 (T+512.64) | 53532B / `dc3db34c4d95` | 34.5874/179 | 17.9715/204 | 16.5208/152 | 15.9204/194 | 14.7595/194 | 14.7198/193 | 14.8537/193 | 15.7309/143 | 16.4959/153 | 23.6807/100 | 6TH/6, 00:01:43, 40%, 19 MPH (viewed) |
| d-post9 (T+513.71) | 59421B / `18e0c82192f9` | 12.7244/124 | 16.1214/163 | 13.6559/146 | 14.9991/159 | 16.6105/165 | 16.7639/170 | 16.8873/172 | 12.0026/124 | 21.5867/163 | 88.7915/173 | 6TH/6, 00:01:45, 41%, 39 MPH (viewed) |
| d-post10 (T+514.78) | 62473B / `bf4c86e81ee7` | 19.6826/122 | 17.6955/154 | 15.2473/146 | 16.0610/160 | 17.6457/161 | 17.5007/169 | 17.6640/172 | 14.1600/130 | 21.4729/170 | 113.3681/205 | 6TH/6, 00:01:46, 41%, 51 MPH, SSX arch (viewed) |

In-script (remote) vs PIL agreement: ≤0.06 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr/vs-pp scores at scale (e.g. scpre band 12.7765 vs
12.7091; x-post40 vs-pp 16.3076 vs 16.2926; mr-post8 band 27.7333 vs
27.7056); the known ~5–11× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.4842/8 remote vs 0.1750/4 PIL; sepre vs-se 0.4258/6
vs 0.0624/0 ≈ 7× — T27 title / T28 menu / T29 SC / T30 ZC / T31 SP /
T32 SM / T33 SE / T34 MR / T35 / T36 / T37 / T38 / T39 precedent); chain
hops ≤0.05 (max Δ 0.049 on x-post3→x-post8 13.4669 vs 13.5162). Dense
hops have NO in-script remote counterpart (blind — PIL only). Vs-panel
remote receipt reads 0.71–0.93/p99 10–16 on panel-side PIL 0.46–0.69
(≈1.4× inflation at the ~0.5 scale), so the < 2.0 whole bar holds even
remotely (worst remote 0.9340, 2.1× margin). The TAG crop gap re-confirmed
at ~280× (2.6271 vs 0.0094). Standing pattern holds: whole-frame bars
calibrated in PIL transfer to remote with single-digit inflation near zero
and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars.

Batch-scorer bit-exact validation (committed `t40-cropdiff.py` vs numpy
batch port, mean/p99/max/npix identical 4/4): panel-panel
(`mr-stab2`→`pppre`) 0.0251/0/115; gameplay-motion (`d-post1`→`d-post2`)
14.6272/133/198; title-vs-ref (`a1-poll01`) 0.0467/1/25; SE-vs-ref
(`sepre`) 0.0624/0/50.

### R2 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1472 | 10.1543/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1164 | 0.1459/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2982 | 0.3228/7 | same screen |
| post8 → post15 (mc) | 0.2687 | 0.2908/6 | same screen |
| post15 → scpre (park span) | — | 0.1532/3 | same screen |
| scpre → zc-post1 | 7.0742 | 7.1021/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.2941 | 0.3177/9 | arrival settling |
| post3 → post8 (zc) | 0.2713 | 0.2930/7 | same screen |
| post8 → ccpre (park span) | — | 0.3040/8 | same screen |
| ccpre → sp-post1 | 9.3511 | 9.3892/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0372 | 0.0429/0 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0212 | 0.0239/0 | same screen |
| post8 → sppre (park span) | — | 0.0240/0 | same screen |
| sppre → pc-post1 | 5.2516 | 5.2746/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.1095 | 0.1130/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0495 | 0.0538/0 | same screen |
| post8 → smpre (park span) | — | 0.0543/0 | same screen |
| smpre → rc-post1 | 0.5162 | 0.5441/12 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps in T32/T33) |
| post1 → post3 (rc) | 0.0407 | 0.0437/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0239 | 0.0287/0 | same screen |
| post8 → sepre (park span) | — | 0.0835/1 | same screen |
| sepre → sj-post1 | 10.6221 | 10.6457/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.1692 | 0.1831/4 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.1639 | 0.1729/2 | same screen |
| post8 → mrpre (park span) | — | 0.1730/2 | same screen |
| mrpre → mr-post1 | 12.6283 | 12.5910/150 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 1.4725 | 1.4923/58 | loading progress 17% → 97% |
| post3 → post8 (mr) | 25.5342 | 25.5390/253 | loading screen → race intro cinematic (no black frame captured this run — transition timing lottery) |
| post8 → post15 (mr) | 19.1778 | 19.1740/190 | cinematic → pre-race panel (panel arrived by +15, one sample early vs T34) |
| post15 → post25 (mr) | 0.1127 | 0.1252/5 | same screen (panel shimmer/animation) |
| post25 → post40 (mr) | 0.1542 | 0.1606/7 | same screen |
| post40 → stab1 (mr) | 0.1897 | 0.1952/8 | same screen |
| stab1 → stab2 (mr) | 0.0395 | 0.0521/1 | same screen |
| stab2 → pppre (park span) | — | 0.0251/0 | same screen |
| pppre → x-post1 | 14.4162 | 14.4007/152 | screen change within +1 s (pre-race panel → countdown/gate; decisive hop) |
| post1 → post3 (x) | 13.3389 | 13.3238/135 | countdown → live gameplay (gate → slope) |
| post3 → post8 (x) | 13.4669 | 13.5162/129 | live gameplay motion |
| post8 → post15 (x) | 8.6251 | 8.6659/123 | live gameplay motion |
| post15 → post25 (x) | 13.1516 | 13.2009/125 | live gameplay motion |
| post25 → post40 (x) | 11.1224 | 11.1619/130 | live gameplay motion |
| post40 → npre1 (span) | — | 10.6473/122 | live gameplay motion |
| npre1 → npre2 | BLIND (no in-script) | 6.7246/109 | live gameplay motion (PRE-hold pair, NO input between; 1.074 s exposure gap) |
| npre2 → d-post1 | BLIND (no in-script) | 6.9656/89 | live gameplay motion (hold window lands inside this hop; 2.111 s span incl. 1.038 s hold) |
| d1 → d2 | BLIND (no in-script) | 14.6272/133 | live gameplay motion (1.074 s gap) |
| d2 → d3 | BLIND (no in-script) | 9.4279/132 | live gameplay motion (1.072 s gap) |
| d3 → d4 | BLIND (no in-script) | 8.8677/110 | live gameplay motion (1.073 s gap) |
| d4 → d5 | BLIND (no in-script) | 13.2983/156 | live gameplay motion (1.072 s gap) |
| d5 → d6 | BLIND (no in-script) | 14.4837/157 | live gameplay motion (1.071 s gap) |
| d6 → d7 | BLIND (no in-script) | 12.1934/174 | live gameplay motion (1.072 s gap) |
| d7 → d8 | BLIND (no in-script) | 12.0508/164 | live gameplay motion (1.071 s gap) |
| d8 → d9 | BLIND (no in-script) | 16.6016/163 | live gameplay motion (1.073 s gap) |
| d9 → d10 | BLIND (no in-script) | 8.6114/134 | live gameplay motion (1.072 s gap) |

### R2 arrival park (pre-race panel)

| Item | Value |
|---|---|
| Post-Enter frames | `t40r2-mr-post1.jpg` @T+330 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 17% Loading…; `mr-post3` @T+335: same screen, 97% Loading…; `mr-post8` @T+343: race intro cinematic, nightclub (`EA RADIO BIG / Jerk it Out / Caesars / 39 Minutes of Bliss` overlay, `Press X to skip`); `mr-post15` @T+352: pre-race panel = arrival (one sample early vs T34's +25) |
| Stability N (panel) | 6 snaps (post15/25/40 + stab1/2 + pppre) spanning T+352→T+432 (80 s) |
| Whole-frame pairwise (PIL) | 0.0251–0.2575/p99 ≤11 across all 15 pairs (panel shimmer/animation; min stab2–pppre 0.0251/0, max post15–post40 0.2575/11; JPEG shas distinct) |
| Vs-panel-ref (whole) | 0.46–0.69/p99 7–16 across all 6 (all under the 2.0 gate; margins 2.9–4.4×) |
| Vs-MR (whole) | 19.36–19.55/p99 153 across all 6 (not My Rules) |
| Vs-SE (whole) | 16.21–16.40/p99 159–160 across all 6 (not Select Event) |
| Vs-SM (whole) | 16.21–16.39/p99 159–160 across all 6 (not Select Mode) |
| Vs-SP (whole) | 16.40–16.53/p99 157 across all 6 (not Select Peak) |
| Vs-ZC (whole) | 19.93–20.13/p99 162–164 across all 6 (not Setup Character) |
| Vs-SC (whole) | 19.19–19.38/p99 171 across all 6 (not Select Character) |
| Vs-menu (whole) | 19.06–19.28/p99 177–178 across all 6 (not menu) |
| Vs-title (band) | 34.52–34.52/p99 184 across all 6 (not title) |
| SE-TAG (crop) | 48.5996/133 identical across all 6 (tagline band static within run; T39's run read 50.7398/131, T38's 49.4844/132, T37's 48.2320/132, T36's 48.5186/132, T35's 48.5040/133, T34's 50.8209/132 — run-dependent, lineup/background phase) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Griff / Viggo / Allegra / Elise / Seeiah` (AI lineup differs run to run — T39: `Zoe/Marisol/Viggo/Nate/Allegra/Moby`, T38: `Zoe/Seeiah/Elise/Viggo/Kaori/Moby`, T37: `Zoe/Viggo/Eddie/Allegra/Kaori/Nate`, T36: `Zoe/Moby/Nate/Luther/Griff/Marty`, T35: `Zoe/Kaori/Brodi/Viggo/Elise/Griff`, T34: `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`); `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 80 s (all 6 snaps pre-race panel) |

### R2 arrival (countdown → live gameplay; input-free throughout)

| Snap (wall T+) | Race clock | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|
| x-post1 (T+436, +0.5 s after XCROSS keyup) | 00:00:00 | gates | 0% | 0 MPH | 0 | countdown `2` over the starting gate; riders in gates |
| x-post3 (T+440) | 00:00:02 | 5TH/6 | 1% | 39 MPH | 0 | leaving the gate, start straight, gondola |
| x-post8 (T+447) | 00:00:10 | 4TH/6 | 5% | 50 MPH | 0 | open slope, jump ramp ahead, two riders |
| x-post15 (T+455) | 00:00:24 | 1ST/6 | 12% | 49 MPH | 0 | banked icy turn, chevron fence |
| x-post25 (T+467) | 00:00:40 | 1ST/6 | 21% | 58 MPH | 0 | groomed run, `OUT OF BOUNDS` banner, SSX arch |
| x-post40 (T+484) | 00:01:02 | 5TH/6 | 28% | 46 MPH | 0 | open slope, pines, rail structure |

Race-clock vs wall-clock (wall since XCROSS keyup 1789994393.518; race
clock read off HUD, HH:MM:SS):

| Snap | Wall since keyup (s) | Race clock (s) | Ratio |
|---|---|---|---|
| x-post1 | 0.5 | 0 | — (countdown) |
| x-post3 | 4.5 | 2 | 0.44 |
| x-post8 | 11.5 | 10 | 0.87 |
| x-post15 | 19.5 | 24 | 1.23 |
| x-post25 | 31.5 | 40 | 1.27 |
| x-post40 | 48.5 | 62 | 1.28 |

Stability N (X): not a static arrival — 6 snaps over 48 s, all 15
whole-frame pairs 8.67–15.18/p99 ≤170 (live gameplay motion; min
x-post8–x-post15 8.6659/123, max x-post3–x-post15 15.1752/140; JPEG shas
distinct). Vs-panel-ref 14.53–22.62 across all 6 (decisively non-panel);
vs-MR 11.31–13.26 (non-MR). No reclaim to any menu/panel (all 6 snaps
countdown/live gameplay, positions/progress/timer all advancing).

### R2 hold (1 s Left on live gameplay + blind sub-second series + tracking)

Hold row (proven keydown→keyup / phase match / delivery):

| Item | Value |
|---|---|
| Input | ONE `press_hold Left` (body verbatim T38's; `Left = Keyboard/Left` @ `PCSX2.ini:576`) |
| KEYDOWN wall | 1789994461.098337663 (T+503.09, uptime 577) |
| KEYUP wall | 1789994462.136290270 (T+504.13, uptime 578) |
| Hold duration | 1038.0 ms (T38's hold: 1037.3 ms — same input class delivery) |
| Pre-hold pair | `npre1` @T+501.96 (1.14 s before KEYDOWN) + `npre2` @T+503.03 (0.07 s before KEYDOWN), NO input between |
| Last input before hold | XCROSS keyup @T+435.51 — 67.6 s of input-free racing before KEYDOWN |

Phase match (hold window vs T38's hold / T39's sham — match PHASE, not
seed):

| Item | T38 hold window | T39 sham window | T40 hold window | Δ vs T38/T39 |
|---|---|---|---|---|
| Slot | T+504.54 (keydown) | T+504.62 (SHAMSTART) | T+503.09 (KEYDOWN) | −1.45 s / −1.53 s (shorter pre-pair gap: blind `sleep 1` vs scored `sleep 2`) |
| Pre-pair race clocks | 00:01:25 / 00:01:31 | 00:01:24 / 00:01:29 | 00:01:28 / 00:01:29 | +3/−2 s, +4/+0 s |
| Pre-pair positions | 2ND/6 / 2ND/6 | 4TH/6 / 4TH/6 | 6TH/6 / 6TH/6 | back-of-pack (AI lineup/RNG differ run to run) |
| Pre-pair progress | 40% / 44% | 36% / 38% | 36% / 36% | −4/−8 pp, +0/−2 pp |
| Series span | 10 snaps, +26 s wall / +41 s race | 10 snaps, +26 s wall / +41 s race | 10 snaps, +11.8 s wall / +17 s race | blind capture shortens the span (same 10-snap shape) |

Pre-hold HUD (read off the viewed `npre1`/`npre2` snaps):

| Item | npre1 | npre2 |
|---|---|---|
| Race clock | 00:01:28 | 00:01:29 |
| Position | 6TH/6 | 6TH/6 |
| Progress | 36% | 36% |
| Speed | 75 MPH | 60 MPH |
| Score | 0 pts | 0 pts |
| Scene | Foggy forest chute, airborne spray | Forest chute, rider mid-distance, groomed run |

Dense post-hold HUD series (read off viewed snaps; wall since hold keyup
1789994462.136; race advanced = race clock minus npre2 89 s; wall span =
SNAPSTART wall minus npre2 SNAPSTART 1789994461.030; nominal cadence =
`sleep 1` + ~70 ms snap, NO scoring):

| Snap (wall T+) | Wall span | Race clock (+adv) | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|---|
| npre1 (T+501.96) | −1.074 s (pre) | 00:01:28 (−1) | 6TH/6 | 36% | 75 MPH | 0 | pre-hold baseline, foggy chute |
| npre2 (T+503.03) | +0 (pre) | 00:01:29 (+0) | 6TH/6 | 36% | 60 MPH | 0 | pre-hold baseline, forest chute |
| d-post1 (T+505.14) | +2.111 s | 00:01:33 (+4) | 6TH/6 | 37% | 16 MPH | 0 | against rock wall, streambed |
| d-post2 (T+506.21) | +3.185 s | 00:01:35 (+6) | 6TH/6 | 37% | 48 MPH | 0 | open snow slope, forest edge |
| d-post3 (T+507.28) | +4.257 s | 00:01:36 (+7) | 6TH/6 | 38% | 55 MPH | 0 | forest slope, tree trunks |
| d-post4 (T+508.35) | +5.330 s | 00:01:38 (+9) | 6TH/6 | 38% | 51 MPH | 0 | forest, red chevron barrier |
| d-post5 (T+509.43) | +6.402 s | 00:01:39 (+10) | 6TH/6 | 39% | 49 MPH | 0 | banked turn, chevron banners |
| d-post6 (T+510.50) | +7.473 s | 00:01:41 (+12) | 6TH/6 | 39% | 27 MPH | 0 | against barrier/rock, `RECOVER` meter |
| d-post7 (T+511.57) | +8.545 s | 00:01:42 (+13) | 6TH/6 | 40% | 9 MPH | 0 | rider down/sliding by barrier |
| d-post8 (T+512.64) | +9.616 s | 00:01:43 (+14) | 6TH/6 | 40% | 19 MPH | 0 | recovering through trees |
| d-post9 (T+513.71) | +10.689 s | 00:01:45 (+16) | 6TH/6 | 41% | 39 MPH | 0 | open slope, forest gates |
| d-post10 (T+514.78) | +11.760 s | 00:01:46 (+17) | 6TH/6 | 41% | 51 MPH | 0 | open slope, SSX arch |

Race-advance vs wall-span (race-advanced-since-npre2 / wall-since-npre2):

| Snap | Race adv (s) | Wall span (s) | Ratio |
|---|---|---|---|
| d-post1 | 4 | 2.111 | 1.89 |
| d-post2 | 6 | 3.185 | 1.88 |
| d-post3 | 7 | 4.257 | 1.64 |
| d-post4 | 9 | 5.330 | 1.69 |
| d-post5 | 10 | 6.402 | 1.56 |
| d-post6 | 12 | 7.473 | 1.61 |
| d-post7 | 13 | 8.545 | 1.52 |
| d-post8 | 14 | 9.616 | 1.46 |
| d-post9 | 16 | 10.689 | 1.50 |
| d-post10 | 17 | 11.760 | 1.45 |

Exposure gaps (SNAPSTART→SNAPSTART from ns `bsnap` stamps; snap capture
itself 65–70 ms START→END):

| Gap | Duration (s) | Contents |
|---|---|---|
| npre1 → npre2 | 1.074 | `sleep 1` + snap (≈1.07 s exposure) |
| npre2 → d-post1 | 2.111 | hold 1.038 s + `sleep 1` + keydown/focus overhead |
| d1 → d2 | 1.074 | `sleep 1` + snap |
| d2 → d3 | 1.072 | `sleep 1` + snap |
| d3 → d4 | 1.073 | `sleep 1` + snap |
| d4 → d5 | 1.072 | `sleep 1` + snap |
| d5 → d6 | 1.071 | `sleep 1` + snap |
| d6 → d7 | 1.072 | `sleep 1` + snap |
| d7 → d8 | 1.071 | `sleep 1` + snap |
| d8 → d9 | 1.073 | `sleep 1` + snap |
| d9 → d10 | 1.072 | `sleep 1` + snap |

Dense span npre1→d-post10: 12.90 s wall (T39: 34 s) for the same 12-snap
shape — blind capture delivers ≈1.07 s exposures vs T36–T39's ≈3 s.

Rider-pixel tracking series (committed `t40-track.py`, byte-identical to
T39's; RDC = rider dark-centroid + validity gate; SCPS40 = T37-frozen
±40 window; SCPS120 = wide ±120 window; whole hop = PIL per-hop from
§hops):

| Snap | RDC cx/cy (px) | RDC npix (frac) + gate | SCPS40 lag (corr) into this snap | SCPS120 lag (corr) into this snap | Whole hop into this snap |
|---|---|---|---|---|---|
| npre1 | 486.0 / 326.3 | 12620 (0.090) INVALID (fog/spray floods ROI) | — | — | — |
| npre2 | 383.1 / 268.7 | 20273 (0.144) INVALID (forest/shade) | −38 (0.55) resolved | −38 (0.55) resolved | 6.7246/109 |
| d-post1 | 406.1 / 261.9 | 92720 (0.660) INVALID (rock wall fills frame) | +40 (0.74) RAIL | +49 (0.79) resolved | 6.9656/89 |
| d-post2 | 333.8 / 246.8 | 1310 (0.009) VALID | −12 (0.01) no match | −12 (0.01) no match | 14.6272/133 |
| d-post3 | 300.1 / 195.1 | 38044 (0.271) INVALID (trees/trunks) | −7 (0.49) resolved | −7 (0.49) resolved | 9.4279/132 |
| d-post4 | 355.2 / 265.5 | 124528 (0.887) INVALID (wall/barrier fills frame) | +39 (−0.62) anti-corr | −120 (0.37) RAIL | 8.8677/110 |
| d-post5 | 427.8 / 200.9 | 9127 (0.065) INVALID (over gate) | +7 (0.68) resolved | +7 (0.68) resolved | 13.2983/156 |
| d-post6 | 449.0 / 281.7 | 43689 (0.311) INVALID (barrier/rock fills ROI) | −40 (0.55) RAIL | −72 (0.59) resolved | 14.4837/157 |
| d-post7 | 304.7 / 302.9 | 5155 (0.037) VALID | −23 (0.02) no match | −110 (0.14) weak | 12.1934/174 |
| d-post8 | 450.9 / 230.7 | 33164 (0.236) INVALID (trees/barrier) | +40 (−0.30) rail, no match | −120 (0.58) RAIL | 12.0508/164 |
| d-post9 | 306.3 / 191.1 | 9608 (0.068) INVALID (over gate) | +40 (0.20) rail, weak | +50 (0.23) resolved | 16.6016/163 |
| d-post10 | 299.5 / 216.3 | 6821 (0.049) INVALID (over gate) | +10 (−0.52) anti-corr | +120 (−0.22) rail, no match | 8.6114/134 |

Sub-second distribution (11 hops at ≈1.07 s exposures + hold hop):

| Metric | Sub-second value (this run) |
|---|---|
| HUD position | 6TH/6 throughout — zero swaps, no decay (back-of-pack: nowhere to fall; AI lottery) |
| HUD progress/clock | monotonic 36% → 41%, +17 s race over +11.8 s wall (~1.5×, matches turbo) |
| RDC gate | gated OUT on 10/12 snaps (npix ≫ rider-scale: fog/forest/wall/barrier flood the ROI); only d-post2 (1310), d-post7 (5155) VALID — non-adjacent, so no gated delta exists anywhere in the series and no gated pair straddles the hold |
| SCPS40 | rails ±40 on 4/11 hops (incl. the hold hop npre2→d-post1 at +40 @ 0.74) |
| SCPS120 | rails ±120 on 3/11 hops; resolves 8/11 — INCL the hold hop (+49 @ 0.79) and the pre-pair gap (−38 @ 0.55) |
| Whole hops | 6.72–16.60 dense (motion-class throughout; the two smallest are the pre-pair gap 6.72 and the hold hop 6.97) |

Observed behavior characterization (tabled, not verdicts):

| Question | Observed |
|---|---|
| Did position change? | No — 6TH/6 on all 12 snaps (back-of-pack throughout; the hold hop holds 6TH→6TH and the pre-pair gap holds 6TH→6TH) |
| Did progress change? | Advances monotonically 36% → 41% (race-clock-driven, no jumps) |
| Did the clock change? | Advances steadily: +17 s race over +11.8 s wall (~1.5×, matches turbo) |
| Did speed change? | 75→60 (pre-pair) →16 (d1, rock wall) →48→55→51→49→27 (d6, `RECOVER`) →9 (d7, down/sliding) →19→39→51 MPH — two slow corners with wall/barrier contact (d1 @16, d6–d7 @27/9 + `RECOVER` meter), one straddling the hold hop, one mid-series |
| Did score change? | 0 pts flat on all 12 snaps (no scoring events anywhere in the series) |
| Did heading change (rider pixels)? | RDC gated OUT on 10/12 snaps (fog/forest/wall/barrier flood the ROI); only 2 VALID snaps, non-adjacent, so no gated delta exists. SCPS40 rails ±40 on 4/11 hops. SCPS120 rails ±120 on 3/11 hops and RESOLVES the hold hop (+49 @ 0.79) and the pre-pair gap (−38 @ 0.55) — the first resolved input hop in T36–T40 |
| Any HUD discontinuity at the hold? | Position holds 6TH→6TH; speed drops 60→16 MPH across the hold hop (d1 against rock wall) and recovers to 48 by d2; progress/clock monotonic; no freeze, no menu, no reclaim |
| Isolation note | Single hold run at ~1 s exposures, no same-seed pairing (AI lineup/RNG differ run to run); compared against T36/T37/T38 input runs + T39 control below |
| Recipe (one variant per attempt) | The ±120 window now resolves the input hop at ~1 s exposures but RDC still floods (forest/wall scenes) and SCPS40 still rails the hold hop — a steer-discriminating window needs EITHER still-shorter exposures (sub-`sleep-1` cadence: capture-bound, ~70 ms + scheduler) OR an ROI/gate retune for forest/wall scenes (higher dark threshold, smaller ROI, or a gradient-based rider lock); next, ONE variant per attempt: sub-second `sleep 0.5` cadence with the same hold, testing whether SCPS40 resolves the hold hop too |

Rail-rate comparison (T36 tap / T37 tap / T38 hold / T39 control, all
~3 s gaps, vs this ~1.07 s hold run; T36/T37/T38/T39 values from their
reports):

| Item | T36 (338.6 ms tap) | T37 (338.2 ms tap) | T38 (1037.3 ms hold) | T39 (NO input) | T40 (1038.0 ms hold, ~1.07 s) |
|---|---|---|---|---|---|
| Pre-input baseline | single `npre` 00:01:18 6TH/6 30% (no pair; sparse shape) | pair 00:01:26 / 00:01:31 | pair 00:01:25 / 00:01:31 | pair 00:01:24 / 00:01:29 | pair 00:01:28 / 00:01:29 |
| Pre-pair positions | 6TH/6 (single) | 2ND / 3RD (swap in gap) | 2ND / 2ND | 4TH / 4TH | 6TH / 6TH |
| Series-end position | 6TH/6 @00:02:29 59% (sparse +1/+3/+8/+15/+25/+40) | 3RD/6 @00:02:11 60% | 6TH/6 @00:02:12 58% | 6TH/6 @00:02:10 55% | 6TH/6 @00:01:46 41% (shorter span: blind capture) |
| Position swaps in series | 0 (6TH throughout sparse tail) | 2ND↔3RD swaps with and without tap | 3 swaps, decay 2ND→6TH | 4 swaps, decay 4TH→6TH | 0 (6TH throughout) |
| Input-hop position step? | none separable | none separable | none (2ND→2ND) | none (4TH→4TH) | none (6TH→6TH) |
| RDC gate-out rate | n/a (no tracking in T36) | validity-flooded 6/12 | gated out 10/12 | gated out 9/12 | gated out 10/12 |
| Gated RDC delta anywhere? | n/a | no | no (non-adjacent valids) | no (non-adjacent valids) | no (2 valids, non-adjacent) |
| SCPS40 rail rate | n/a (no tracking in T36) | rails nearly every step | rails 6/11 | rails 5/11 | rails 4/11 |
| SCPS120 rail rate | n/a (T38+ metric) | n/a (T38+ metric) | rails 7/11 | rails 4/11 | rails 3/11 |
| Input-hop SCPS120 | n/a | n/a | −120 @ 0.15 RAIL | −120 @ 0.16 RAIL | +49 @ 0.79 RESOLVED |
| Pre-pair-gap SCPS120 | n/a | n/a | +120 @ 0.20 RAIL | +120 @ 0.25 RAIL | −38 @ 0.55 resolved |
| Whole-hop range (dense) | n/a (sparse shape) | X+D 8.48–20.26 (dense subset incl. 8.48 tap hop) | 10.07–22.33 | 8.58–20.62 | 6.72–16.60 |
| Clock ratio (race/wall) | ~1.35× | ~1.4× | ~1.4× | ~1.4× | ~1.5× |

Post-hold frame motion (whole-frame PIL): all 66 D pairs 5.86–21.08/p99
≤174 (min d-post1–d-post4 5.8554/72, max d-post1–d-post9 21.0752/155;
JPEG shas distinct). Motion throughout — no static frame, no freeze, no
menu/panel reclaim in the 12.9 s tail. Vs-panel-ref 10.77–21.59 across all
12 (decisively non-panel).

### R2 PP-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Departure mrpre→post1 | 12.6283 | > 5.0 | yes |
| Arrival static p25→p40 | 0.1542 | < 1.0 | yes |
| Arrival static p40→s1 | 0.1897 | < 1.0 | yes |
| Arrival static s1→s2 | 0.0395 | < 1.0 | yes → `PP-LIKE`, X-Continue Cross pressed |
| Non-MR (stab2 vs-mr) | 19.3864/153 | > 5.0 | yes |
| Vs-pp receipt (post15/25/40) | 0.9340/16, 0.8391/12, 0.7129/10 | (not a leg — receipt) | tabled (≈1.4× vs PIL 0.46–0.69; under 2.0 even remotely) |
| Vs-pp receipt (stab1/2) | 0.8795/14, 0.8930/15 | (not a leg — receipt) | tabled |
| Vs-pp receipt (pppre) | 0.8996/15 | (not a leg — receipt) | tabled (≈1.4× vs PIL 0.6447) |

### R2 LIVE gate legs (in-script proxy, remote)

| Gate leg | Value | Bar | Margin | Pass? |
|---|---|---|---|---|
| Departure pppre→x-post1 | 14.4162 | > 5.0 | 2.9× | yes |
| Non-panel (x-post40 vs-pp) | 16.3076/147 | > 5.0 | 3.3× | yes |
| Motion (x-post15→x-post25) | 13.1516 | > 5.0 | 2.6× | yes |
| Motion (x-post25→x-post40) | 11.1224 | > 5.0 | 2.2× | yes → `LIVE-LIKE`, blind pre-hold pair + hold + blind dense series |

### R2 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Live race reproduced at a matched phase (HUD advancing, phase-match tabled) | countdown `2` at +0.5 s, live gameplay from +4.5 s, race 6TH/6 at 41% by +79 s wall; clock/progress advance monotonically, all X+D hops 6.72–16.60 (motion); hold @T+503.09 vs T38's @T+504.54 / T39's @T+504.62, clocks +3/−2 s vs T38 (+4/+0 vs T39), progress −4/−8 pp vs T38 (+0/−2 vs T39) (positions 6TH/6TH vs 2ND/2ND vs 4TH/4TH — back-of-pack vs lead/mid-pack, AI lottery) |
| Hold acted on it (pre-hold = racing with HUD read) | HOLD_LEFT keydown→keyup 1038.0 ms wall; 67.6 s input-free before; pre-hold pair = racing 00:01:28 6TH/6 36% / 00:01:29 6TH/6 36% with HUD read off viewed snaps |
| Sub-second dense series (HUD + tracking + hops, post-hoc scored) | 12-snap HUD series above (position 6TH flat, progress 36→41%, clock +17 s, two slow wall/barrier corners @d1 16 MPH + @d6–d7 27/9 MPH with `RECOVER`, score 0 flat) + exposure-gap table (10 × ≈1.07 s + hold hop 2.111 s, from ns stamps) + RDC/SCPS40/SCPS120 per-snap table + sub-second distribution (RDC gated out 10/12, SCPS40 rails 4/11, SCPS120 rails 3/11 with hold hop +49 @ 0.79 resolved) + comparison + recipe |
| Rail-rate comparison vs T38/T39 + gated-pair verdict | tabled above (SCPS40 4/11 vs 6/11 vs 5/11; SCPS120 3/11 vs 7/11 vs 4/11; hold-hop SCPS120 RESOLVED +49 @ 0.79 vs railed in both; gated-pair verdict: NO — only 2 VALID RDC snaps, non-adjacent, none straddling the hold) |
| Full input log + trace sha | `t40r2-poll.log` (168 lines: every score + press + hold + 24 blind-snap ns stamps, walls + uptimes) + trace `6fb03830…a367c` |

Guest/trace side (R2): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32/T33/T34/T35/T36/T37/T38/T39 (BIOS L2, ExecPS2 L142330/142426,
ReBootStart L142725, first vblank L417043, first UpdateVSyncRate L456189);
×15 modes; vblanks 397 frozen (all ≤90); LoadStartModule 18; ERROR 0;
`NVRAM has not changed`; clean tail @514.2014. Census: EE 12,128,822 (52,
set-identical to T39 R1) · IOP 19,121,181 (155, set-identical to T39 R1 —
hold + blind series + gameplay adds no new called API) ·
`libsd.006: sceSdGetParam` 17919 (T39: 24610); `sceSdGetAddr` 3,804,768
(T39: 4,001,328).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R2 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate → Enter Cross → PP-LIKE settled-panel gate → X Cross → LIVE-LIKE proxy gate) |
| Cross on X Continue? | YES (XCROSS @T+434.98 R2, pre-press = pre-race panel, X Continue) |
| Live race reached at matched phase? | YES (countdown `2` @T+436 → live gameplay by T+440 → race at 41%, 6TH/6 @T+514, still running; hold window phase-matched to T38's hold / T39's sham within +4 s clock / −8 pp progress) |
| Hold with 1 s Left on live gameplay? | YES (HOLD_LEFT 1038.0 ms @T+503.09, pre-hold pair = racing 00:01:28 6TH/6 36% / 00:01:29 6TH/6 36%) |
| Sub-second series + comparison tabled? | YES — blind 10-snap series at ≈1.07 s exposures + post-hoc HUD + RDC/SCPS40/SCPS120 series + rail-rate comparison: SCPS120 railing drops 7/11 → 3/11 with the hold hop resolved (+49 @ 0.79); RDC still floods (10/12) with no gated pair straddling the hold |
| Bounded re-attempt? | none run (pre-hold = racing at a matched phase — re-attempt condition not met; brief stops at R2 + recipe; R1 was an environment failure, not an attempt on the question) |
| 1200 s cap | Not reached — R2 ≈ T+524; attempts 2–3 unexercised |
| Chain end | Live Snow Jam race (6TH/6, 41%, 00:01:46) after a 1 s Left hold + blind 10-snap sub-second series; race not yet finished at capture end |

## T40-4. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t40 R2 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules → Cross → game load → cinematic → pre-race panel → Cross → countdown → live gameplay → blind pre-hold pair → 1 s Left hold → blind 10-snap series, T+~524) | 43,480,989 / 2,782,052,936 | `6fb03830dfa816abb077cfbacaabd26c6b71444cfafde14ecfd2a9a39fea367c` (analyze-sha on H30 = post-restart re-verify on H31 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t40r2.txt`, same size+sha (match; streamed via `wsl cat`, no C: staging) + committed head/tail 2000+2000 (`t40r2-trace-head.txt` 149019 B sha `63af833438ad…`, `t40r2-trace-tail.txt` 132101 B sha `8b06ec9ae9e6…`) |
| `emulog-pre-t40-20260921T123238Z.txt` = t40 R1 wedged partial (chain to ZC hops, guest wedge at T+185) | — / 1,103,446,016 | `b77089b3c6438375c6ab08055cc02b1d76fb1dc9416ce475d115d6540cab22f5` (pre-rotation = post-rotation re-verify; match) | bytesize-only (discarded environment-failure run; no SSD copy, no slices) |
| `emulog-pre-t40-20260921T114358Z.txt` = t39 R1 (preserved at R1 boot) | — / 2,898,445,035 | `749b8c93dcb961ec047f5e0d506aedf11e92041c9f751a47ab6f3f3be1744249` (re-verified post-wedge: matches T39) | bytesize-only (T39 precedent; SSD holds T39's own copy) |

Channel census (T4 `t4-census.py`, same script): R2 EE 12,128,822 (52
distinct, set-identical to T39 R1) · IOP 19,121,181 (155, set-identical
to T39 R1) · vblanks 397. Committed: `t40r2-census.txt` (11695 B sha
`466da1c755b8…`), `t40r2-samples.txt` (5874 B sha `8e01dc8ca120…`),
`t40r2-poll.log` (168 lines, 10317 B sha `2b55ebb7e0e4…`),
`t40r2-stdout.txt` (451 lines, 29549 B),
`t40r2-stderr.txt` (full `set -x` shell trace, 2551 lines, 134817 B),
`t40r2-trace-head.txt` / `t40r2-trace-tail.txt`.
Trace-head note: same 149019 B as T34/T35/T36/T37/T38/T39 R1 heads but sha
differs (`63af8334…` vs `76bc8871…`) — timestamp-stripped content differs
across timing/wall-clock/shader-cache lines (same standing pattern).

## T40-5. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); one `wsl` call per ssh):

```
# reuse verification (pipe-free; one wsl call per ssh)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H29 …892 (fresh, up 2 s)
ssh bytesize 'wsl dmesg' > /tmp/t40-dmesg-pre.txt                     # 440 lines, 0 AcceptAsync (H29)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t40-eventlog-pre.txt  # head H29-create 07:41:33
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/…100909.nvm'                       # da021d2a…
ssh bytesize 'wsl grep -n "Cross\s*=\|Left\s*=" …/inis/PCSX2.ini'      # Left :576, Cross :579
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t35-ref-panel.ppm'    # all 9 refs reproduce
ssh bytesize 'wsl bash -c "df -h / /mnt/c"'                           # 871G / C: 1.4G
ssh bytesize 'wsl ls -la …/logs/emulog.txt'                           # 2898445035 B = T39 R1
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # 749b8c93… T39R1 live
# T39 ref snaps (local): 12/12 sizes reproduce T39 §chain
# freeze t40 scripts (copies of T39; press_hold restored + bsnap blind phase; bash -n; cropdiff/track/vcount cmp-identical)
# staging (T25 recipe: scp to C: then wsl cp)
scp t40-auto.sh t40-analyze.sh t40-vcount.sh t40-cropdiff.py "bytesize:pcsx2-t4/"
ssh bytesize 'wsl bash -c "cp /mnt/c/Users/bradr/pcsx2-t4/t40-… /home/brad/pcsx2-t4/; sha256sum …"'  # staged shas match local
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H29
ssh bytesize 'wsl python3 …/t40-cropdiff.py …REFPP …; date -u; cat /proc/uptime; grep btime /proc/stat'  # 0.0000/0 PPM, H29 …892 up 81
# R1 (ONE ssh; wedged at T+185 in ZC hops — C: 1.4G→116KB, guest exec dead; ssh killed by me; NO T40_DONE)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t40-auto.sh' > /tmp/t40r1-run-stdout.txt 2>/tmp/t40r1-run-stderr.txt
# wedge forensics (Windows-side; WSL exec dead): echo/wsl --list/wevtutil/fsutil/tasklist probes; C: 116KB; Volsnap 24/35
# C: fix (by me): powershell inventory (Steam 342G/Ubisoft 110G/GOG 85G untouched) + Remove-Item C:\Users\bradr\pcsx2-t4\emulog-*.txt (~30G) → 29.1G free
# recovery (by me): sc stop WslService (STOP_PENDING) + taskkill vmwp 17860 + taskkill wslservice 7252 → STOPPED + sc start → RUNNING
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H30 …883 (fresh)
ssh bytesize 'wsl dmesg' > /tmp/t40-dmesg-vmH30-fresh.txt             # 423 lines, 0 AcceptAsync (H30)
ssh bytesize 'wsl ls -la …/logs/' > /tmp/t40-logs-ls.txt              # 28 emulogs; R1 partial 1103446016 B frozen at wedge
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t40-20260921T114358Z.txt'  # 749b8c93… T39R1 intact
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; date -u; …'            # b77089b3… R1 partial; H30 …883
ssh bytesize 'wsl wc -l …/t40-poll.log'                               # 48 (NUL-torn tail — disk-full writes)
ssh bytesize 'wsl tail -n 4 …/t40-poll.log'                           # MC series + NULs (stdout ran ahead to ZC)
ssh bytesize 'wsl sha256sum …100909.nvm'                              # da021d2a… intact
ssh bytesize 'wsl sha256sum …/t40-auto.sh …'                          # 4 staged shas intact
ssh bytesize 'wsl rm -f …/t40-*.jpg …/t40-*.ppm …/t40-*.xwd …/t40-poll.log'  # wedged-R1 snaps deleted unfetched
ssh bytesize 'wsl bash -c "df -h / /mnt/c"'                           # 870G / C: 27G
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt'                            # 6719f5d6… intact
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix'  # on VM-H30
ssh bytesize 'wsl python3 …/t40-cropdiff.py …REFPP …; date -u; …'      # 0.0000/0 PPM, H30 …883 up 65
# R2 (ONE ssh; exit 0; LIVE-LIKE → BLIND PRE-PAIR → HOLD → blind 10)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t40-auto.sh' > /tmp/t40r2-run-stdout.txt 2>/tmp/t40r2-run-stderr.txt  # T40_DONE, up 75→599
ssh bytesize 'wsl dmesg' > /tmp/t40-dmesg-vmH30-post.txt              # IMMEDIATELY after run ssh: 451 lines, 1 AcceptAsync [614.65] (H30, post-window)
ssh bytesize 'wsl bash …/t40-analyze.sh'                              # 6fb03830…, 43480989 L
ssh bytesize 'wsl bash …/t40-vcount.sh'                               # 397 frozen
ssh bytesize 'wsl wc -l …/t40-poll.log'                               # 168
ssh bytesize 'wsl cp <34 chain jpg> /mnt/c/…'                         # (explicit list, one wsl call)
ssh bytesize 'wsl cp <27 race/dense jpg + poll.log + census/samples> /mnt/c/…'  # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t40-…" /tmp/t40-fetch/                         # 61 jpg + logs (r2 files)
# R2 post-hoc (local batch scorer, 4/4 bit-exact): chain panel, hops, 15 panel pairs, 15 X pairs, 66 D pairs, xrun, census set-compare, t40-track.py dense series
ssh bytesize 'wevtutil …' > /tmp/t40-eventlog-post.txt                # head H30-teardown 08:45:45; ZERO in-window entries of any kind
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H31 …763 (fresh, created by this call)
ssh bytesize 'wsl dmesg' > /tmp/t40-dmesg-vmH31-post.txt              # 450 lines, 0 AcceptAsync (H31)
ssh bytesize 'wsl sha256sum …100909.nvm'                               # da021d2a… untouched
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # 6fb03830… re-verified
ssh bytesize 'wsl ls -la …/logs/' > /tmp/t40-logs-final.txt           # 29 emulogs incl. both pre-t40 rotations
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t40-20260921T123238Z.txt'  # b77089b3… R1 partial preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t40r2-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t40r2-trace-tail.txt         # 2000 lines, clean tail @514.2014
ssh bytesize 'wsl grep -c LoadStartModule …/logs/emulog.txt'           # 18
# SSD copy (COPYFILE_DISABLE=1; streamed via wsl cat — no C: staging — then shasum re-verify)
ssh bytesize 'wsl cat <trace>' > "/Volumes/Extreme SSD/ps2x-t4/emulog-t40r2.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t40r2.txt"         # 6fb03830… match
ssh bytesize 'wsl bash -c "df -h / /mnt/c"'                           # 867G / C: 27G
ssh bytesize 'wsl du -sh …/logs/'                                     # 43G
ssh bytesize 'wevtutil qe System /c:12 /rd:true /f:text' > /tmp/t40-eventlog-final.txt  # H30-teardown 08:45:45, H31-create 08:46:03
# evidence assembly (COPYFILE_DISABLE=1; r2-prefixed renames) + report (chunks; receipts include tail -3)
cp /tmp/t40-dmesg-*.txt /tmp/t40-eventlog-*.txt /tmp/t40r2-run-stdout.txt … local/research/T40/  # renamed per §evidence
tail -3 local/research/T40/REPORT.md
git add -f local/research/T40/<83 files by name>                      # ignored dir, forced
git commit -m "[T40] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T40-6. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (steering characterization) | Reproduce the R2 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate (departed + non-SE + static) → Cross on Continue → PP-LIKE settled-panel gate (departed + static ×3 + non-MR) → Cross on X Continue → LIVE-LIKE proxy gate (departed + non-panel + motion ×2) → ≤3 attempts) → live gameplay; then ONE 1 s D-pad Left hold acts on the live race (R2: pre-hold pair 00:01:28 6TH/6 36% / 00:01:29 6TH/6 36%, blind 10-snap series at ≈1.07 s exposures to 00:01:46 6TH/6 41% scored post-hoc — SCPS120 railing drops to 3/11 with the hold hop RESOLVED (+49 @ 0.79), SCPS40 rails 4/11 incl. the hold hop, RDC gated out 10/12 with no gated pair straddling the hold; race clock ~1.5× wall under turbo). Next, ONE variant per attempt: sub-second `sleep 0.5` blind cadence with the same hold (capture-bound at ~70 ms + scheduler), testing whether SCPS40 resolves the hold hop too — OR an RDC ROI/gate retune for forest/wall scenes (higher dark threshold, smaller ROI, or gradient-based rider lock), never both at once. Gate note: the hold→gameplay whole-frame hop is large (~6.72–16.60 dense) because the race never stops moving — gate on the HUD (clock/position/progress/speed/score), not the frame. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | R1 C:-full guest wedge (environment failure) + 1 pre-session + 1 post-everything restart (all not by me) + my service-restart recovery | R1 wedged at T+185 (ZC hops): C: drained 1.4 G → 116 KB by VHDX growth → guest exec wedged permanently (25+ min zero output; `wsl --shutdown`/`--terminate` stuck) → discarded per T27 §4, re-run as R2. Recovery by me: `sc stop WslService` → taskkill vmwp 17860 → taskkill wslservice 7252 → start → fresh VM-H30. AcceptAsync exact counts 0/0/1/0 across the 4 committed dmesg files, all outside the R2 window (H29-pre 0; H30-fresh 0; H30-post 1×[614.65] post-window — run ended uptime 599; H31-post 0) + 1 pre-session VM restart between T39 and T40 (H28-teardown 07:08:25 → H29-create 07:41:33) + 1 post-everything VM restart (H30-teardown 08:45:45 → H31-create 08:46:03, after all R2 WSL work — only final state reads ran on H31). ZERO event entries in-window (R2 08:33:58–08:41:22 local). R2 completed exit 0 with T40_DONE + all 61 snaps + clean trace tail, i.e. effects-verified per the T27 §4 rule (the immediate post-run dmesg read closed T33's sequencing gap). Precautions stand + C: headroom is now a pre-run gate (see G8). No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: ZERO in-window entries; boundaries bound all restarts + the wedge | Newest-30 reads (pre/post/final): H28 create 07:02:40 → H28 teardown 07:08:25 → H29 create 07:41:33 → Volsnap 24 @07:46:44 (shadow storage cannot grow) → Volsnap 35 @08:05:15 (shadow copies aborted) → H29 kill (partial 71/69 @08:31:23 + 233 @08:29:20 + 7034 @08:30:51 — no full teardown pair; VM was killed, not shut down) → H30 create 08:31:23 → H30 teardown 08:45:45; inside the R2 window 08:33:58–08:41:22 (local): ZERO entries of any kind. Final newest-12: H30 teardown 08:45:45 → H31 create 08:46:03. `wevtutil` local-as-Z (+4 h → UTC) stands |
| G4 | Hold count 132/132 (534 ms-class) + 2/2 steering taps (300 ms-class) + 2/2 steering holds (1 s) + 1/1 sham (no input) | 534 ms-class holds register 132/132 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33+T34+T35+T36+T37+T38+T39+T40 (T40 R1-wedged: 535.5/534.7/535.5 ms — chain advanced to ZC before the wedge; T40 R2: 536.1/538.0/535.6/536.6/540.0/536.1/541.5/538.1/536.1/537.7 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect. Separately: the 300 ms-class steering tap delivered 2/2 (T36/T37), the 1 s steering hold delivered 2/2 (T38 1037.3 ms, T40 R2 1038.0 ms), and the no-input sham delivered 1/1 (T39) — different input classes, not bisections |
| G5 | Title/menu/SC/ZC/SP/SM/SE/MR frozenness; attract differs; snowflake shimmer on title/SE + MR; panel animation + lineup lottery on arrival; countdown near-frozen; gameplay lottery | Title text-band near-frozen across showings (0.0467/1 R2 vs 0.0468/1 T39 — snowflake shimmer breaks bit-equality, pair 0.0358/0); ZERO bit-identical frames this run (nearest a1-post15 0.0007/0 max 6 — shimmer breaks the T35→T39 five-run bit-identity streak); menu whole-frame ≤0.08/p99 ≤1 cross-run; SC cross-run 0.10–0.30/p99 2–7; ZC cross-run 0.11–0.22/p99 2–6; SP cross-run ≤0.11/p99 ≤1; SM cross-run 0.04–0.10/p99 0–1; Select Event ≤0.07/p99 ≤1 cross-run (rc-post1/3 near-identical 0.037/0.010 but NOT bit-identical — shimmer phase); My Rules ≤0.14/p99 ≤1 cross-run; pre-race panel ≤0.26/p99 ≤11 within run over 80 s (panel shimmer/animation) + AI rider lineup differs run to run (T40 `Zoe/Griff/Viggo/Allegra/Elise/Seeiah` vs T39 `Zoe/Marisol/Viggo/Nate/Allegra/Moby` vs T38 `Zoe/Seeiah/Elise/Viggo/Kaori/Moby` vs T37 `Zoe/Viggo/Eddie/Allegra/Kaori/Nate` vs T36 `Zoe/Moby/Nate/Luther/Griff/Marty` vs T35 `Zoe/Kaori/Brodi/Viggo/Elise/Griff` vs T34 `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`) + SE-TAG crop on panel constant within run but run-dependent (48.5996/133 vs T39's 50.7398/131 vs T38's 49.4844/132 vs T37's 48.2320/132 vs T36's 48.5186/132 vs T35's 48.5040/133 vs T34's 50.8209/132); load→panel transition timing is lottery-dependent (T40: 17% @+1, 97% @+3, cinematic @+8, panel @+15 — same shape as T35/T36/T37/T38/T39, different cinematic track: Jerk it Out Caesars 39 Minutes of Bliss vs Deep End Utah Saints Remix Swollen Members Balance) — the settled-panel gate handled all timings; countdown-`2` gate frame near-frozen cross-run (0.8667/29); gate-exit x-post3 close cross-run again (4.8181/74 — same 5TH @00:00:02 1% 39 MPH starts); live gameplay never static (8.67–15.18 X, 5.86–21.08 D). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the blind-hold run | `WaitVblankStart` stops after log ≤90 in T40 R2 including countdown + live gameplay + pre-pair + hold window + blind dense series (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T39-R1-identical modulo counts). The attract/title/menu/submenu/game sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical; IOP count shifts on audio) | Like prior arrivals, hold + blind series + gameplay adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T39 R1; counts shift (`GetThreadId` 5.12M→5.03M, EE total 12.39M→12.13M; IOP 20.06M→19.12M; `sceSdGetParam` 24610→17919, `sceSdGetAddr` 4.00M→3.80M — shorter run, less race audio traffic). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts + C: pressure RELIEVED (was CRITICAL) | `…/logs/` now holds ~43 GB across 29 emulogs (T17→T40 chain, all preserved, incl. the R1-wedged partial); C: 27 G avail final (1.4 G pre-run → 116 KB at the wedge → 29.1 G after clearing 20 stale `emulog-*.txt` transfer copies ~30 GB from `C:\Users\bradr\pcsx2-t4\` → 27 G after R2). Owner's game installs (Steam/Ubisoft/GOG), Docker, and Temp untouched (536/16/7 GB respectively — not mine). C: headroom (~5 GB+) is now a pre-run gate: any full run needs ~3.5 GB VHDX growth. T40 R2 full trace SSD-copied + sha-verified (2.78 GB: `emulog-t40r2.txt`, streamed via `wsl cat` to avoid C: staging); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T40 brief cites `t39-auto.sh`, `t39-cropdiff.py`, `t39-track.py`, `t39-analyze.sh`, `t39-vcount.sh` — all 5 exist in `local/research/T39/` and were copied (not modified) for T40. T28 G9 lesson holds |
| G10 | Session wall + run durations | ~2 h active of the 4 h box (one wedged run + recovery + one clean run + report/commit); zero lease waits (no lease exists for T40). R1 wall ~200 s to wedge + 25 min stall (discarded); R2 wall 524 s — 164 s over the ≤6 min guidance (X-phase scoring + dense tail), −38 s vs T39 R1's 562 s from blind capture; R2 full dmesg coverage, zero flaps |
| G11 | X11 mount needed twice (wedge recovery), harmless | The `/tmp/.X11-unix` tmpfs mount landed first on VM-H29, then re-landed on VM-H30 after the wedge recovery (service restart by me); no restart between the H30 mount and R2; R2 started Xvfb :99 cleanly (exit 0 + 61 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 – T39 G11 stand) |
| G12 | Remote-vs-PIL gap receipted again on the panel whole bar: ~1.4×, bar holds even remotely | R2's in-script vs-pp receipt reads 0.71–0.93/p99 10–16 on panel-side PIL 0.46–0.69 (≈1.4× inflation at the ~0.5 scale — T39's 2.0–3.4× receipt re-confirmed on a new run at a new scale), so the < 2.0 whole bar holds even as an in-script leg (2.1× margin on the worst remote 0.9340). The TAG-crop gap re-confirmed at ~280× (2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated in PIL transfer to remote with single-digit inflation near zero and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars |
| G13 | Blind-capture method validated (post-hoc scoring reproduces the chain) | `bsnap` ns stamps recover exposure gaps to the ms (10 × 1.071–1.074 s + hold hop 2.111 s; capture itself 65–70 ms); post-hoc PIL scores reproduce the scored phases' remote hops ≤0.05 (max Δ 0.049); dense-phase PIL-only scores + HUD + tracking need no in-script counterpart. The brief's "score post-hoc, not in-script" recipe works end to end: −38 s run time, ≈1.07 s exposures, first resolved input hop |

## Evidence files

`REPORT.md` (this file),
scripts: `t40-auto.sh`,
`t40-cropdiff.py` (T39 logic, byte-identical),
`t40-track.py` (frozen rider-pixel tracker: RDC + validity gate + SCPS40 + SCPS120, byte-identical),
`t40-analyze.sh`, `t40-vcount.sh` (output-name deltas only; vcount
byte-identical);
R2: `t40r2-start.jpg`, `t40r2-a1-now.jpg`, `t40r2-a1-poll01.jpg`,
`t40r2-a1-pre.jpg`, `t40r2-a1-post{3,8,15,25}.jpg`, `t40r2-menupre.jpg`,
`t40r2-mc-post{1,3,8,15}.jpg`, `t40r2-scpre.jpg`,
`t40r2-zc-post{1,3,8}.jpg`, `t40r2-ccpre.jpg`,
`t40r2-sp-post{1,3,8}.jpg`, `t40r2-sppre.jpg`,
`t40r2-pc-post{1,3,8}.jpg`, `t40r2-smpre.jpg`,
`t40r2-rc-post{1,3,8}.jpg`, `t40r2-sepre.jpg`,
`t40r2-sj-post{1,3,8}.jpg`, `t40r2-mrpre.jpg`,
`t40r2-mr-post{1,3,8,15,25,40}.jpg`, `t40r2-mr-stab{1,2}.jpg`,
`t40r2-pppre.jpg`, `t40r2-x-post{1,3,8,15,25,40}.jpg`,
`t40r2-npre{1,2}.jpg`, `t40r2-d-post{1,2,3,4,5,6,7,8,9,10}.jpg` (61 snaps),
`t40r2-census.txt`, `t40r2-samples.txt`, `t40r2-poll.log`,
`t40r2-stdout.txt`, `t40r2-stderr.txt`, `t40r2-trace-head.txt` / `t40r2-trace-tail.txt`;
R1-wedge: `t40r1-wedged-stdout.txt` (8771 B), `t40r1-wedged-stderr.txt`
(41831 B);
flaps: `t40-dmesg-vmH29-pre.txt` (0 AcceptAsync on H29, pre-run) /
`t40-dmesg-vmH30-fresh.txt` (0 AcceptAsync on H30, pre-R2) /
`t40-dmesg-vmH30-post.txt` (1 AcceptAsync [614.65], post-R2-window;
full R2-window coverage, zero in-window) /
`t40-dmesg-vmH31-post.txt` (0 AcceptAsync on H31, fresh boot),
`t40-eventlog-pre.txt` / `t40-eventlog-post.txt` / `t40-eventlog-final.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t40r2.txt`
(2,782,052,936 B `6fb03830…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T39 R1
(`…-20260921T114358Z.txt` `749b8c93…`) and R1-wedged partial
(`…-20260921T123238Z.txt` `b77089b3…`).
