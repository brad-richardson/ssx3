# T37 report — dense post-nudge series + rider-pixel tracking (bytesize, no lease)

Brief: T37 (T36's G1(a): denser sampling + tracking). Tables, no
verdicts. One boot ran on bytesize (R1: chain reproduced to live gameplay,
ONE 300 ms-class D-pad Left tap on the live race at 00:01:31 3RD/6 42%,
PRE-nudge pair + DENSE 10-snap post-nudge series mapped with rider-pixel
tracking); laptop-side work was ssh/scp + local reads/analysis only. Time
box 4 h.

Stale-reading guard: `local/research/T36/REPORT.md` (all of it: R1
reproduced the chain to LIVE gameplay, ONE 338.6 ms D-pad Left tap @T+500.82
on a live race (00:01:18 6TH/6 30%), +40 s tail to 00:02:29 6TH/6 59% with NO
measurable HUD discontinuity at the 1/3/8/15/25/40 s sampling — position
constant, progress/clock monotonic, speed/score excursions distributed;
isolation limit: single run, no same-seed control, tap contribution below
sampling resolution; G1 proposes (a) denser sampling + tracking, (b) longer
hold, (c) no-nudge control — this brief takes option (a)). This brief
executes T36's G1(a).

Experiment contract (up front): hypothesis — one bounded steering nudge
(single D-pad Left tap, 300 ms keydown, SAME input class as T36) delivered
to live Snow Jam gameplay produces a separable immediate heading response
resolvable by dense (1 s cadence × 10 s) post-nudge sampling + rider-pixel
tracking; observable — pre-nudge pair = live race (race clock +
position/progress HUD read off the viewed snaps), the nudge row (control /
direction / duration / T+), dense 10-snap series + per-snap HUD + tracking
metrics + per-hop whole diffs; screen content read off viewed snaps;
alternatives — dense series + tracking STILL show no separable tap response
(deadzone, wrong control, response below pixel resolution → table the exact
observed series + tracking + noise floor + recipe), nudge provably never
acted on live gameplay (pre-nudge ≠ racing → ONE bounded variant allowed);
stop — table the exact observed behavior + recipe, one input variant per
attempt, never blind multi-presses.

## T37-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T37; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T37]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; verified
on VM-H20, re-verified on VM-H21 after the mid-session restart, before R1):

| Item | T4 value | T37 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Nudge binding used | — | `Left = Keyboard/Left` (`PCSX2.ini:576`), xdotool key `Left` | tabled §T37-1 |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…580eb6` reproduces T35 | yes |
| T36 reference snaps present | — | all 13 sizes reproduce T36 §T36-2 (`npre` 60331, `n-post{1,3,8,15,25,40}` 68874/58811/62484/58362/57495/63807, `x-post{1,3,8,15,25,40}` 70304/68162/68172/64860/61932/56485) | yes |
| Free space | — | WSL `/` 881 G avail; C: 8.0 G final (3.9 G pre-run); laptop `/` 4.4 Gi avail; SSD 328 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1, on VM-H21 (the H20→H21 restart fell between pre-checks and staging per event boundaries + file mtimes; mount verified present on H21 pre-R1 — T32 G11 stands) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t37-{auto,analyze,vcount,cropdiff}.sh/.py`, `t37-{r1-census,samples}.txt` (via analyze), `t37-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t37-*.txt` (rotation chain, see trace table), `boot-t37.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t37*` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 1 pre-session between T36 and T37 (H19→H20) + 1 mid-session between pre-checks and staging (H20 08:37:50→08:39:57, H21 create 08:42:34; staged files persist on the same VHD, shas re-verified; mount + ref-checks verified on H21) + 1 post-everything (H21→H22 08:56:26, after all fetch WSL calls; only final state reads + trace slices ran on H22) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H21 btime:
04:42:34→`1789980154`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 08:16:00 | VM-H19 teardown (T36's post-everything VM, after T36's session) | eventlog-pre (IDs 71/69/233/234/234) |
| 2 | 08:37:50 ([0] VM-H20) | VM-H20 started fresh ~2 s before first ssh | btime `…870`, eventlog-pre head (IDs 292/67/291/233/232/102/291/102/291/291) |
| 3 | 08:37:52–~08:39 | Pre-run checks on VM-H20 (all ssh exit 0) + C:-staging (VM-independent) | `t37-dmesg-vmH20-pre.txt` (0 AcceptAsync, 440 lines, 23 `Ioctl failed` — captured at uptime ~2 s, before dxg queries) |
| 4 | 08:39:57–08:42:34 | VM-H20 teardown → VM-H21 create (mid-session restart, NOT by me; between pre-checks and WSL-staging; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified; mount + ref-checks verified on H21) | btime `…154`, eventlog-post (IDs 71/69/233/234/234 teardown, 292/67/291/233/232/102/291/102/291/291 create), `t37-dmesg-vmH21-pre.txt` (0 AcceptAsync, 441 lines) |
| 5 | 08:43:13–08:52:36 ([39]→[601] H21) | R1 single-shot exit 0, `T37_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart in-window; 2× in-window Volsnap ID 33 shadow-copy deletions at 08:44:31 — C: pressure housekeeping, not VM events; run effects-verified, see §T37-5 G2) | exit 0, 61 snaps, trace sha |
| 6 | 08:52:36–~08:56 | R1 analyze (exit 0) + all R1 fetches (exit 0) on VM-H21 | `t37-census.txt`, 61 JPGs + logs |
| 7 | 08:56:26 | VM-H21 teardown (post-everything restart, NOT by me) | eventlog-post head (IDs 71/69/233/234/234 teardown) |
| 8 | 09:02:07–09:04:39 (VM-H22) | VM-H22 fresh: identity + dmesg + NVM/trace/preserved-sha re-verifies + trace head/tail slices + SSD stream + df-final (exit 0) | `t37-dmesg-vmH22-post.txt` (1 AcceptAsync [17.18], 448 lines, boot coverage) |
| 9 | event log | Newest-30 reads (pre/post): head moves H20-create 04:37:50 → H21-teardown 04:56:26; boundaries H19-teardown 04:16:00, H20-create 04:37:50, H20-teardown 04:39:57, H21-create 04:42:34, H21-teardown 04:56:26, H22-create 05:02:07; in-window (04:43:13–04:52:36 local) entries: 2× Volsnap ID 33 (shadow-copy deletion, C: pressure) at 04:44:31, ZERO Hyper-V-VmSwitch, ZERO teardown/create — userland kills would leave no Windows trace (T17/T21/T23/T25/T27/T28/T29/T30/T31/T32/T33/T34/T35/T36 precedent stands) | `t37-eventlog-{pre,post,final}.txt` |
| 10 | dmesg noise | `Ioctl failed` lines 23 in all 4 files (steady boot/GPU-query noise, not kills); kill-pattern grep (`killed process\|out of memory\|panic\|oops\|segfault`) matches only the 2 `panic=-1` cmdline echoes per file | dmesg files |

AcceptAsync exact counts with uptime-stamp positions relative to the R1
window (T_BOOT uptime 39 → end 601, all on VM-H21):

| Committed file | Lines | AcceptAsync count | Uptime stamps | Position vs run window |
|---|---|---|---|---|
| `t37-dmesg-vmH20-pre.txt` | 440 | 0 | — | different VM (pre-restart); outside |
| `t37-dmesg-vmH21-pre.txt` | 441 | 0 | — | same VM, pre-window; outside |
| `t37-dmesg-vmH21-post.txt` | 442 | 0 | — | same VM, full R1-window coverage; ZERO in-window |
| `t37-dmesg-vmH22-post.txt` | 448 | 1 | [17.184563] | different VM (post-everything, no run); outside |

## T37-1. Nudge selection + tracking method (frozen BEFORE the run) + LIVE calibration

Tool: `t37-cropdiff.py` (copy of T36's, byte-identical; `cmp` clean;
`t37-vcount.sh` byte-identical to T36's; `t37-analyze.sh` differs only in
output names). Title text-band method unchanged (thresholds frozen: TITLE
band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu
mean < 2.0; NONMENU / NONSC / NONZC / NONSP / NONSE / NONMR whole-vs-ref
mean > 5.0; DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). Panel
reference reused (`t35-ref-panel.ppm`, already staged, sha re-verified).
No new reference (no new static screen to gate on). Remote PPM-mode
self-check pre-run: panel ref 0.0000/0.

Nudge selection (tabled BEFORE the run, per brief — pick ONE; UNCHANGED
from T36 — same input class, do NOT change duration/hold):

| Item | Value |
|---|---|
| Control | D-pad Left (NOT analog) |
| Binding | `Left = Keyboard/Left` (`PCSX2.ini:576`) |
| xdotool key | `Left` |
| Duration | Single 300 ms tap (`keydown`, `sleep 0.3`, `keyup`) |
| Direction | Left |
| When | After the X arrival series, on the LIVE-LIKE proxy gate (≈T+505, deep in live gameplay per T35's/T36's race shape) |

Tracking method (tabled BEFORE the run, per brief — frozen in committed
`t37-track.py`, sha `8d40a770…1a6dbf`; game area measured on the T36 npre
snap: x[0,647] y[24,511] of the 1280x1024 snap):

| Metric | Definition (fixed) | Rationale |
|---|---|---|
| RDCX/RDCY | Centroid (0.1 px) of dark pixels (luminance < 80) inside rider ROI x[150,540] y[100,460] (game-area central band; excludes position/clock/score top strip, progress bar + speed left column, trick meter right column). Reports cx/cy/npix/dark-fraction; npix is the validity channel (rider-scale ≈ low thousands — T36 npre: cx=390.2, npix=2462) | Rider outfit is near-black against bright snow; a Left carve displaces the rider sprite laterally before the chase cam re-centers |
| SCPS | Snow column-profile shift (integer lag px in [−40,+40]) between consecutive snaps: column-mean luminance profile over x[150,540] of rows y[380,460] (foreground snow band), normalized cross-correlation best lag (+ = scene moved right). Reports lag + peak corr; corr is the validity channel | Under a chase cam the world rotates around the rider, so a heading change reads as background lateral shift even when the rider stays centered |

Noise-floor measurement plan (frozen BEFORE the run): the script captures
a PRE-nudge pair (`npre1`, `sleep 2`, `npre2`) with NO input between; the
noise floor N = |M(npre2) − M(npre1)| per metric (race motion over the
no-input gap). A tap-correlated delta may be claimed only for a post-tap
excursion/kink exceeding N with tap-coincident timing. Determinism check
pre-run: tracker run twice on T36 npre → `cmp` clean (identical bytes in,
identical numbers out, no RNG).

Pre-run calibration (tracker on T36's input-free X series + npre):

| Snap(s) | RDC | SCPS | Reading |
|---|---|---|---|
| T36 npre | cx=390.2 cy=202.5 npix=2462 frac=0.0175 | — | rider cleanly isolated at viewed position |
| T36 x-post1/3/8/15/25/40 | npix 6309–42328 (frac 0.04–0.30) | lags −40..+38, corr −0.20..+0.22 | scene-dependent as expected: dark scenery (gate/forest) floods the ROI (npix ≫ rider-scale ⇒ invalid); sparse-cadence (2–15 s) pairs don't correlate (corr ≈ 0 ⇒ lag meaningless). Validity channels behave — tabled as the interpretive rule, not tuned away |

LIVE calibration (T36's, reused unchanged; T35 R1 receipts; no new
calibration run — the gate is a proxy, the criterion is HUD-read):

| Leg | T35 R1 receipt | Bar | Margin |
|---|---|---|---|
| Panel→countdown departure hop (pppre→x-post1) | 14.18–14.19 | > 5.0 (DEPARTED) | 2.8× |
| X-snaps vs-panel-ref | 12.98–21.27 | > 5.0 (NONPP) | 2.6× |
| Late-tail motion hops (x-post15→x-post25, x-post25→x-post40) | 11.52, 9.51 | > 5.0 (DEPARTED) | 1.9× |
| All 66 X-pair hops | 7.97–20.23 (never static) | — | static gate cannot fire |

LIVE-LIKE proxy gate (as frozen pre-run): in-script nudge criterion =
decisively left the panel (pppre→x-post1 hop > 5.0) AND arrival non-panel
(x-post40 vs-pp > 5.0) AND motion ×2 (x-post15→x-post25, x-post25→x-post40
hops > 5.0). The TRUE live-race criterion — race clock advancing +
position/progress HUD present — is read off VIEWED snaps post-hoc, not
whole-frame scores (T35 G1 gate note: gate on the HUD, not the frame).
Every proxy leg carries ≥1.9× margin on the T35 receipts.

Script deltas vs `t36-auto.sh` (committed originals untouched; `t37-auto.sh`
is the adapted copy):

| Area | T36 script | T37 script |
|---|---|---|
| Chain | park phase + full menu→MR chain + PP gate + XCROSS + x series to +40 + LIVE gate + nudge + n series to +40 | identical through the LIVE-LIKE gate; nudge phase REPLACED by the dense phase |
| Dense phase | `npre` + ONE `press_nudge Left` (300 ms) + post-nudge series +1/+3/+8/+15/+25/+40 + 6 per-hop whole diffs | `npre1` + `sleep 2` + `npre2` (PRE-nudge pair, no input between) + ONE `press_nudge Left` (300 ms, UNCHANGED input class) + DENSE series `d-post1..10` (`sleep 1` each, 1 s cadence × 10 s) + 11 per-hop whole diffs (pre1-pre2, pre2-d1, d1-d2 … d9-d10); each dense snap scored titleband + vs-pp in-script |
| Self-tests | SELF_TEST + … + SELF_MR + SELF_PP | unchanged (all 11 re-run) |
| No-park paths | explicit `NO-PARK` + … + `NO-LIVE-PARK` | unchanged (still clean shutdown + `T37_DONE`, trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
port of `t37-cropdiff.py` (`/tmp/t37-fastdiff.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical)
against the committed tool on 4 diverse pairs (panel-panel 0.1545/6,
gameplay-motion 13.3508/125, title-vs-ref 0.0354/0, SE-vs-ref 0.0377/0).
Any score reproduces with the committed `t37-cropdiff.py`, slower. The 9
ref PPMs were reused from `/tmp/t36-refs/` for post-hoc scoring (all 9
shas re-verified, match §T37-0).

## T37-2. R1 — race reproduced, ONE steering nudge + dense series on live gameplay

Run: `t37-auto.sh`, ONE fresh boot, T_BOOT wall 1789980193 (uptime 39,
VM-H21), 08:43:13–08:52:36 UTC (uptime 39→601 = 562 s; 202 s over the
≤6 min guidance — the X phase + dense tail; full dmesg coverage, zero
flaps in-window), WID 2097159 (same as T31 R1 / T32 R1 / T33 R1 / T33 R2 /
T34 R1 / T35 R1 / T36 R1), exit 0, `T37_DONE`, clean SIGTERM shutdown.
SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC
0.0000/0, SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM 0.0000/0, SELF_SE
0.0000/0, SELF_SETAG 0.0000/0, SELF_MR 0.0000/0, SELF_PP 0.0000/0.
Attempt 1 of ≤3 consumed; attempts 2–3 not needed (chain advanced to the
nudge, dense series mapped). No bounded variant run (pre-nudge = racing —
variant condition not met, brief stops here).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+100, score 0.4337/6 remote / 0.0453/0 PIL (T36 R1: 0.4311/5 / 0.0474/1 — same detector reading, frame differs by 0.0306/0) | Cross 535.1 ms @T+98.44 (attract-skip) + Start 536.7 ms @T+101.71 (on title, ≤1.8 s after exposure) | Main Menu by +5 s; menu-like gate (non-title + whole-static 0.0389/0.0268) + post25-vs-menu 0.3103/5 → park for menu Cross |
| A2–A3 | not run (chain advanced) | — | — |

### R1 cross-run frame identities (T37 R1 vs T36 R1, full sha256)

| Frame | T37 R1 sha | T36 R1 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `4a9c7cf6b67d…` (cp-identical, pair 0.0000/0) 58388 B | `6e0c68accf47…` 58293 B | differ; pair 0.0306/0 max 49 (title timing lottery, nearby phase) |
| a1-post3/25 | differ | differ | whole pairs 0.040/0, 0.027/0 |
| a1-post8 | `88ae592f89f5…` 50006 B | `88ae592f89f5…` 50006 B | BIT-IDENTICAL (`cmp` clean) |
| a1-post15 | `4c56f8159c76…` 49634 B | `4c56f8159c76…` 49634 B | BIT-IDENTICAL (`cmp` clean; 3rd run — also T35 R1) |
| menupre | differ | differ | whole pair 0.0027/0 max 13 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.168/4, 0.185/5, 0.152/4, 0.094/2 |
| scpre | differ | differ | whole pair 0.2174/5 |
| zc-post1/3/8 | differ | differ | whole pairs 0.090/1, 0.104/2, 0.114/2 |
| ccpre | differ | differ | whole pair 0.0910/1 |
| sp-post1/3/8 | differ | differ | whole pairs 0.037/0, 0.063/1, 0.002/0 |
| sppre | differ | differ | whole pair 0.1071/1 |
| pc-post1/3/8 | differ | differ | whole pairs 0.033/0, 0.008/0, 0.048/0 |
| smpre | differ | differ | whole pair 0.0111/0 |
| rc-post1/3 | differ | differ | whole pairs 0.0018/0, 0.0030/0 (near-identical; snowflake shimmer breaks bit-equality this run) |
| rc-post8 | differ | differ | whole pair 0.1349/1 (snowflake shimmer) |
| sepre | differ | differ | whole pair 0.0123/0 |
| sj-post1/3/8 | differ | differ | whole pairs 0.076/0, 0.032/0, 0.136/2 |
| mrpre vs T36 `mrpre` | `0bdff41c4c6c…` | `4c29825b3816…` | whole pair 0.0133/0 |
| mr-post1 (load) | `023fa9d54af9…` 66749 B | `de707d1d5ed5…` 66795 B | differ; pair 1.5941/57 (17% vs 18% Loading) |
| mr-post3 (load) | `d54e4c3785cc…` 67389 B | `04d24cebdc71…` 67139 B | differ; pair 2.0607/69 (both Loading 97%; snowflake/percentage shimmer) |
| mr-post8 | `728cb8569f3d…` 54851 B | `6e0a12fc113d…` 53961 B | differ; pair 7.2863/133 (both race-intro cinematic, different phase/track: Deep End Utah Saints Remix vs Clockworks) |
| mr-post15/25/40 | differ | differ | whole pairs 0.5765/10, 0.3936/7, 0.4606/7 (both pre-race panel; AI lineup differs run to run) |
| mr-stab1/2 | differ | differ | whole pairs 0.6562/14, 0.6391/13 (both pre-race panel; lineup differs) |
| pppre vs T36 `pppre` | `33044a7b2ed3…` 59465 B | `294e4249044e…` 59704 B | whole-vs-panel-ref 0.7468/19 PIL (under the 2.0 gate; lineup differs) |
| x-post1 (countdown) | `caf455395db9…` 70313 B | `c5e4a07a7e94…` 70304 B | differ; pair 1.9146/68 (both countdown `2` gates — near-frozen) |
| x-post3/8/15/25/40 | differ | differ | whole pairs 5.09/82, 3.63/65, 4.55/80, 17.58/185, 14.65/121 (gameplay lottery) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789980291.442 → 1789980291.977 | 535.1 ms | T+98.44→98.98 | 137 | `a1-now` attract (16.9877/134 remote; 16.9715/134 PIL) | `a1-poll01` TITLE (0.4337/6; 0.0453/0) |
| A1 Start (Return) | 1789980294.711 → 1789980295.248 | 536.7 ms | T+101.71→102.25 | 140 | `a1-pre` ≡ `a1-poll01` (sha `4a9c7cf6b67d`, TITLE) | `a1-post3` Main Menu (16.2553/139; 16.2568/138) |
| MENU Cross (K) | 1789980333.816 → 1789980334.353 | 536.6 ms | T+140.82→141.35 | 179→180 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2873/5 remote; 0.0276/0 PIL; vs-title 16.2610/139) | `mc-post1` Select Character (vs-menu 10.2108/105; vs-sc 0.4285/7; titleband 12.5585/164) |
| ZOE Cross (K) | 1789980373.783 → 1789980374.319 | 535.5 ms | T+180.78→181.32 | 219 | `scpre` Select Character, Zoe selected (vs-sc 0.5899/9 remote; 0.2427/4 PIL; vs-menu 10.1941/105; vs-title 12.6596/164) | `zc-post1` Setup Character (vs-sc 7.2280/100; vs-zc 0.5225/9; titleband 15.9314/128) |
| CONT Cross (K) | 1789980402.492 → 1789980403.028 | 536.0 ms | T+209.49→210.03 | 248 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4437/8 remote; 0.2113/6 PIL; vs-sc 7.2795/100; vs-title 15.8017/128) | `sp-post1` Select Peak (vs-zc 9.4704/154; vs-sp 0.3744/6; titleband 23.1278/171) |
| PEAK Cross (K) | 1789980431.338 → 1789980431.875 | 536.4 ms | T+238.34→238.87 | 276→277 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.3932/6 remote; 0.0484/0 PIL; vs-zc 9.4617/154; vs-title 23.1279/171) | `pc-post1` Select Mode (vs-sp 5.3577/121; vs-sm 0.3938/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789980460.606 → 1789980461.141 | 535.0 ms | T+267.61→268.14 | 306 | `smpre` Select Mode, Race highlighted (vs-sm 0.3909/6 remote; 0.0397/0 PIL; se-tag 14.3325/89 remote / 14.1480/88 PIL; vs-sp 5.3505/121; vs-title 26.3170/183) | `rc-post1` Select Event (vs-sm 0.8083/11; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789980491.714 → 1789980492.251 | 536.5 ms | T+298.71→299.25 | 337 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6292/11 remote, 0.0375/1 PIL; vs-se 0.4075/6, 0.0377/0; vs-sm 0.8117/11; vs-sp 5.4515/121; vs-title 26.2104/183) | `sj-post1` My Rules (vs-se 10.6666/143; vs-mr 0.4365/7; titleband 9.8445/136) |
| ENTER Cross (K) | 1789980520.362 → 1789980520.897 | 535.8 ms | T+327.36→327.90 | 366 | `mrpre` My Rules, Continue highlighted (vs-mr 0.3989/7 remote; 0.0777/0 PIL; vs-se 10.6324/143; vs-title 9.8393/137 — viewed) | `mr-post1` game load 17% (vs-mr 12.6253/150; vs-pp 21.0600/169; titleband 17.6707/170 — viewed) |
| XCROSS (K) | 1789980625.532 → 1789980626.071 | 538.7 ms | T+432.53→433.07 | 471 | `pppre` pre-race panel, X Continue (vs-pp 1.0008/19 remote; 0.7468/19 PIL — viewed) | `x-post1` countdown 2, starting gate (vs-pp 14.6168/153; titleband 18.7400/149 — viewed) |
| NUDGE Left (Left) | 1789980698.085 → 1789980698.423 | 338.2 ms | T+505.09→505.42 | 543→544 | `npre2` live race 00:01:31 3RD/6 42% (vs-pp 16.4212/129 remote; 16.4099/129 PIL; vs-title 14.6070/100 — viewed) | `d-post1` live race 00:01:35 2ND/6 45% (vs-pp 15.2608/141; titleband 18.9655/115 — viewed) |

Within-dwell receipts R1: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (1 s resolution) → Start-keydown ≤1.8 s; T33-R2-measured title
persistence 15–17 s ⇒ press inside the window with an order of magnitude
to spare. Start-keyup → MenuCross-keydown 38.6 s; MenuCross-keyup →
ZoeCross-keydown 39.4 s; ZoeCross-keyup → ContCross-keydown 28.2 s;
ContCross-keyup → PeakCross-keydown 28.3 s; PeakCross-keyup →
RaceCross-keydown 28.7 s; RaceCross-keyup → SnowJamCross-keydown 30.6 s;
SnowJamCross-keyup → EnterCross-keydown 28.1 s; EnterCross-keyup →
XCross-keydown 104.6 s (panel settling + PP gate); XCross-keyup →
Nudge-keydown 72.0 s (X arrival series + LIVE gate; no dwell pressure — the
race runs input-free, T35 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / whole vs panel-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | Whole vs panel | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+96) | 53999B / `4d215e1d774a` | 27.8066/159 | 18.0759/154 | 16.8465/158 | 16.2728/147 | 15.0595/153 | 15.8067/155 | 15.8221/155 | 15.7695/140 | 14.5672/152 | 36.4078/91 | Attract |
| a1-now (T+97, pre-Cross) | 66054B / `f249df663378` | 16.9715/134 | 13.7509/154 | 13.6083/149 | 12.9326/138 | 17.0752/186 | 17.6282/202 | 17.7450/203 | 12.7228/137 | 25.0175/199 | 82.2593/216 | Attract |
| a1-poll01 (T+100, pre-Start) | 58388B / `4a9c7cf6b67d` | 0.0453/0 T | 14.1348/151 | 11.3077/152 | 12.2562/146 | 15.3709/156 | 16.1499/158 | 16.2477/160 | 9.7680/142 | 22.1504/183 | 106.6222/205 | TITLE (viewed) |
| a1-pre (T+100) | 58388B / `4a9c7cf6b67d` | 0.0453/0 | 14.1348/151 | 11.3077/152 | 12.2562/146 | 15.3709/156 | 16.1499/158 | 16.2477/160 | 9.7680/142 | 22.1504/183 | 106.6222/205 | TITLE (identical cp) |
| a1-post3 (T+105) | 50023B / `429d299f85ab` | 16.2568/138 | 0.0738/1 | 10.1330/105 | 6.9225/93 | 10.4066/170 | 10.9355/177 | 10.9500/177 | 10.0997/96 | 19.3218/178 | 26.1710/106 | Main Menu |
| a1-post8 (T+110) | 50006B / `88ae592f89f5` | 16.2984/139 | 0.0678/1 | 10.1178/105 | 6.9227/93 | 10.3936/170 | 10.9196/177 | 10.9446/177 | 10.0933/96 | 19.3354/178 | 26.1728/106 | Main Menu |
| a1-post15 (T+118) | 49634B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | 10.1073/105 | 6.9081/93 | 10.3855/170 | 10.9184/177 | 10.9433/177 | 10.0761/96 | 19.2985/178 | 26.1710/106 | Main Menu |
| a1-post25 (T+129) | 49896B / `3738490e3e5e` | 16.2622/138 | 0.0547/0 | 10.1307/105 | 6.9275/93 | 10.4063/170 | 10.9393/177 | 10.9536/177 | 10.0985/96 | 19.3024/178 | 26.1732/106 | Main Menu |
| menupre (T+139, pre-MCross) | 49651B / `2c545936d7da` | 16.2622/138 | 0.0276/0 | 10.1076/105 | 6.9077/93 | 10.3844/170 | 10.9174/177 | 10.9425/177 | 10.0749/96 | 19.2991/178 | 26.1446/106 | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+142) | 70185B / `26ef0905cd20` | 12.4846/163 | 10.1424/105 | 0.0667/1 | 7.2422/101 | 11.3766/158 | 11.8383/159 | 11.9071/158 | 5.6383/117 | 19.4412/172 | 26.5704/90 | Select Character, Zoe |
| mc-post3 (T+147) | 70583B / `d7ee1b7bfb51` | 12.4860/163 | 10.1626/107 | 0.0858/1 | 7.2677/100 | 11.4012/158 | 11.8635/158 | 11.9320/157 | 5.6661/117 | 19.4720/172 | 26.5711/90 | Select Character |
| mc-post8 (T+154) | 70264B / `11a00346b860` | 12.4587/163 | 10.1417/105 | 0.2551/5 | 7.2154/100 | 11.3501/158 | 11.8159/157 | 11.8915/157 | 5.6218/117 | 19.4390/172 | 26.5695/90 | Select Character |
| mc-post15 (T+164) | 69979B / `2d9ad9688df2` | 12.4587/163 | 10.1285/105 | 0.0650/1 | 7.2198/100 | 11.3491/158 | 11.8131/157 | 11.8822/157 | 5.6120/117 | 19.4158/172 | 26.5906/90 | Select Character |
| scpre (T+178, pre-ZCross) | 70171B / `5e90e5f22725` | 12.5834/163 | 10.1268/105 | 0.2427/4 | 7.2225/100 | 11.3413/158 | 11.8223/157 | 11.8933/157 | 5.6248/117 | 19.4539/172 | 26.5695/90 | Select Character, Zoe selected (viewed) |
| zc-post1 (T+182) | 51498B / `50cd7a849f39` | 15.9068/129 | 6.9274/93 | 7.1998/100 | 0.2909/7 | 9.3679/153 | 10.1358/164 | 10.2469/164 | 7.0469/103 | 20.1910/164 | 15.2990/91 | Setup Character, Zoe |
| zc-post3 (T+186) | 51576B / `e4de288dfd17` | 15.8226/128 | 6.9108/92 | 7.2638/101 | 0.2335/6 | 9.3431/153 | 10.1042/165 | 10.2173/165 | 7.0543/103 | 20.1810/164 | 15.3043/91 | Setup Character |
| zc-post8 (T+194) | 51369B / `ad6cc8594c5b` | 15.8302/128 | 6.9326/92 | 7.1159/100 | 0.2361/5 | 9.3801/153 | 10.1310/164 | 10.1914/164 | 7.0864/104 | 20.1512/164 | 15.2878/91 | Setup Character |
| ccpre (T+206, pre-ContCross) | 51423B / `5d42f8983fc4` | 15.7829/128 | 6.9026/93 | 7.2546/100 | 0.2113/6 | 9.3533/153 | 10.1121/164 | 10.2234/164 | 7.0389/103 | 20.1805/164 | 15.3256/91 | Setup Character, Zoe + Continue (viewed) |
| sp-post1 (T+211) | 65329B / `14f65bd0626f` | 23.1263/171 | 10.4277/170 | 11.3487/158 | 9.3896/153 | 0.0289/0 | 5.2206/121 | 5.3327/121 | 9.8194/138 | 16.5648/157 | 14.0034/89 | Select Peak, Peak 1 |
| sp-post3 (T+215) | 65475B / `38d8b2f7a4b7` | 23.1254/171 | 10.4244/170 | 11.3637/158 | 9.3881/153 | 0.0300/0 | 5.2299/121 | 5.3295/121 | 9.8507/138 | 16.5632/157 | 14.0026/89 | Select Peak |
| sp-post8 (T+223) | 65228B / `a044d388e943` | 23.1271/171 | 10.4058/170 | 11.3503/158 | 9.3727/153 | 0.0045/0 | 5.2074/121 | 5.3099/121 | 9.8374/138 | 16.5443/157 | 14.0026/89 | Select Peak |
| sppre (T+235, pre-PeakCross) | 65364B / `1d1968d664a2` | 23.1259/171 | 10.4374/170 | 11.3794/158 | 9.3802/153 | 0.0484/0 | 5.2484/121 | 5.3501/121 | 9.8679/138 | 16.5809/158 | 14.0026/89 | Select Peak, Peak 1 highlighted (viewed) |
| pc-post1 (T+239) | 67544B / `621112584960` | 26.3046/183 | 10.9206/178 | 11.8104/157 | 10.1054/164 | 5.1900/121 | 0.0440/0 | 0.5202/10 | 10.4705/143 | 16.4213/160 | 14.1390/88 | Select Mode, Race |
| pc-post3 (T+244) | 67373B / `eb799c1c022f` | 26.3046/183 | 10.9126/178 | 11.8024/157 | 10.0990/164 | 5.1799/121 | 0.0388/0 | 0.5100/9 | 10.4616/143 | 16.4120/160 | 14.1496/88 | Select Mode |
| pc-post8 (T+252) | 67491B / `7fb804dc1146` | 26.2949/183 | 10.9317/178 | 11.8009/157 | 10.1113/164 | 5.1991/121 | 0.0581/1 | 0.5295/11 | 10.4410/143 | 16.4292/160 | 14.1461/88 | Select Mode |
| smpre (T+264, pre-RaceCross) | 67409B / `9d3a9379ef35` | 26.3046/183 | 10.9141/178 | 11.8034/157 | 10.1009/164 | 5.1811/121 | 0.0397/0 | 0.5111/9 | 10.4630/143 | 16.4133/160 | 14.1480/88 | Select Mode, Race highlighted (viewed) |
| rc-post1 (T+269) | 69413B / `ed9ec96fb220` | 26.1964/183 | 10.9394/178 | 11.8595/157 | 10.2176/164 | 5.2837/121 | 0.5113/9 | 0.0330/0 | 10.5915/144 | 16.4278/160 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+273) | 69426B / `6a6ffcda8cb9` | 26.1978/183 | 10.9384/178 | 11.8586/157 | 10.2161/164 | 5.2823/121 | 0.5093/9 | 0.0318/0 | 10.5899/144 | 16.4271/160 | 0.0094/0 | Select Event |
| rc-post8 (T+280) | 69998B / `61a5094b4f16` | 26.1964/183 | 11.0085/178 | 11.9264/157 | 10.2843/164 | 5.3564/122 | 0.5855/15 | 0.0790/0 | 10.6614/144 | 16.4710/160 | 0.0094/0 | Select Event |
| sepre (T+294, pre-SnowJamCross) | 69507B / `d99a9269132e` | 26.1964/183 | 10.9431/178 | 11.8631/157 | 10.2203/164 | 5.2879/121 | 0.5155/10 | 0.0377/0 | 10.5939/144 | 16.4311/160 | 0.0375/1 | Select Event, Snow Jam highlighted (viewed) |
| sj-post1 (T+300) | 58980B / `4183af80ff28` | 9.8193/135 | 10.1144/96 | 5.6451/117 | 7.0855/104 | 9.8542/137 | 10.4602/143 | 10.6242/143 | 0.1200/1 | 19.5635/153 | 26.4126/92 | My Rules, Continue |
| sj-post3 (T+304) | 58561B / `b15a166223c0` | 9.8145/135 | 10.0807/96 | 5.6096/117 | 7.0483/104 | 9.8182/137 | 10.4261/143 | 10.5900/143 | 0.0924/1 | 19.5289/152 | 26.4139/92 | My Rules |
| sj-post8 (T+312) | 58980B / `6deb16d6fdf6` | 9.7999/135 | 10.1063/98 | 5.6462/117 | 7.0822/104 | 9.8723/137 | 10.4847/143 | 10.6486/143 | 0.1483/2 | 19.5884/154 | 26.4126/92 | My Rules |
| mrpre (T+324, pre-EnterCross) | 58475B / `0bdff41c4c6c` | 9.8145/135 | 10.0784/96 | 5.6077/117 | 7.0486/104 | 9.8157/137 | 10.4248/143 | 10.5887/143 | 0.0777/0 | 19.5244/152 | 26.4126/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+328) | 66749B / `023fa9d54af9` | 17.6261/169 | 15.3901/157 | 14.3024/157 | 13.7599/154 | 14.8373/154 | 15.2048/153 | 15.3320/154 | 12.5965/149 | 21.0483/169 | 91.0281/224 | Loading 17% (viewed) |
| mr-post3 (T+333) | 67389B / `d54e4c3785cc` | 18.1971/169 | 15.6966/157 | 14.5141/158 | 13.9786/154 | 15.1592/155 | 15.5246/154 | 15.6528/155 | 12.7800/150 | 21.0603/169 | 95.1267/228 | Loading 97% (viewed) |
| mr-post8 (T+341) | 54851B / `728cb8569f3d` | 27.8820/237 | 21.2396/218 | 20.8164/200 | 21.0021/192 | 20.5638/218 | 21.3185/218 | 21.2321/218 | 20.1779/197 | 19.3185/190 | 44.4460/160 | Race intro cinematic, nightclub, EA RADIO BIG / Deep End - Utah Saints Remix (viewed) |
| mr-post15 (T+350) | 59720B / `5c9adee9b2b4` | 34.5246/184 | 19.1968/178 | 19.3237/172 | 20.0665/163 | 16.4734/157 | 16.3329/160 | 16.3305/159 | 19.4997/154 | 0.5423/9 | 48.2320/132 | Pre-race panel (viewed) |
| mr-post25 (T+363) | 59931B / `2a9afe130629` | 34.5291/184 | 19.3951/179 | 19.4992/172 | 20.2534/164 | 16.6071/157 | 16.5049/161 | 16.5022/160 | 19.6816/154 | 0.4585/7 | 48.2320/132 | Pre-race panel |
| mr-post40 (T+381) | 59812B / `87973ddf50b5` | 34.5298/184 | 19.2787/178 | 19.3961/172 | 20.1399/164 | 16.5221/157 | 16.4068/160 | 16.4044/160 | 19.5705/154 | 0.4570/7 | 48.2320/132 | Pre-race panel |
| mr-stab1 (T+404) | 59693B / `876644ea64ca` | 34.5303/184 | 19.1532/178 | 19.2860/172 | 20.0242/163 | 16.4486/157 | 16.2991/160 | 16.2968/159 | 19.4594/154 | 0.5870/11 | 48.2320/132 | Pre-race panel |
| mr-stab2 (T+417) | 59648B / `5c28f22fb20e` | 34.5212/184 | 19.1238/178 | 19.2588/172 | 19.9905/163 | 16.4235/157 | 16.2813/160 | 16.2791/159 | 19.4263/153 | 0.6143/12 | 48.2320/132 | Pre-race panel |
| pppre (T+429, pre-XCross) | 59465B / `33044a7b2ed3` | 34.5298/184 | 19.0066/177 | 19.1570/172 | 19.8853/162 | 16.3703/157 | 16.1848/159 | 16.1828/159 | 19.3262/154 | 0.7468/19 | 48.2320/132 | Pre-race panel, X Continue (viewed) |
| x-post1 (T+434) | 70313B / `caf455395db9` | 18.7356/149 | 16.0613/162 | 14.0141/136 | 15.9145/152 | 15.6745/158 | 15.8890/158 | 15.9899/159 | 13.2839/129 | 14.5672/153 | 93.2604/175 | Countdown 2, starting gate, 00:00:00, 0 MPH (viewed) |
| x-post3 (T+437) | 67605B / `9dca454aa9a1` | 21.5836/139 | 12.8474/141 | 12.6422/132 | 12.1255/133 | 12.1195/135 | 12.0004/135 | 12.0850/135 | 11.4092/110 | 16.3985/147 | 33.8340/118 | 5TH/6, 00:00:02, 1%, 39 MPH (viewed) |
| x-post8 (T+444) | 69238B / `b55081086d22` | 13.1974/122 | 16.1446/146 | 13.1231/144 | 14.1241/155 | 15.4409/159 | 16.2370/157 | 16.3645/159 | 11.5417/115 | 21.0853/165 | 96.7700/179 | 5TH/6, 00:00:10, 5%, 51 MPH (viewed) |
| x-post15 (T+453) | 61095B / `a140d5fb9b4f` | 15.1747/136 | 21.6957/173 | 17.1507/163 | 18.8048/169 | 20.1560/176 | 20.8146/178 | 20.9199/179 | 15.8309/137 | 25.6329/185 | 127.7401/212 | 2ND/6, 00:00:23, 12%, 50 MPH (viewed) |
| x-post25 (T+465) | 67358B / `9f388440b6ff` | 17.4530/137 | 13.3671/138 | 13.1707/129 | 12.5598/136 | 14.8307/145 | 15.1115/144 | 15.1044/145 | 13.1733/136 | 15.9760/147 | 25.8026/97 | 1ST/6, 00:00:38, 20%, 10 MPH (viewed) |
| x-post40 (T+482) | 69653B / `fbcc1b5f1fc3` | 27.0846/132 | 15.6234/142 | 13.9052/144 | 13.1890/135 | 12.8016/140 | 13.0375/141 | 13.1525/141 | 12.7264/125 | 15.5813/149 | 21.9149/96 | 3RD/6, 00:01:01, 28%, 47 MPH (viewed) |
| npre1 (T+499, pre-nudge pair) | 46913B / `d4cbf3e22e25` | 23.4220/197 | 17.2054/161 | 17.7362/146 | 17.6465/138 | 17.1223/162 | 17.6152/165 | 17.6556/165 | 17.4489/136 | 12.3632/129 | 26.2562/107 | 2ND/6, 00:01:26, 40%, 33 MPH, 0 pts (viewed) |
| npre2 (T+503, pre-nudge) | 51033B / `0885aa87e365` | 14.6196/100 | 11.7636/143 | 11.1226/111 | 10.8701/119 | 13.1686/150 | 13.6973/146 | 13.7821/146 | 9.9133/104 | 16.4099/129 | 56.1337/140 | 3RD/6, 00:01:31, 42%, 57 MPH, 0 pts (viewed) |
| d-post1 (T+506) | 59303B / `83bddebeaab8` | 18.9668/115 | 13.9444/149 | 13.8732/126 | 13.1710/136 | 13.7991/138 | 14.1496/142 | 14.2322/141 | 12.9196/120 | 15.2504/141 | 30.3432/111 | 2ND/6, 00:01:35, 45%, 37 MPH, 0 pts (viewed) |
| d-post2 (T+509) | 58477B / `8f4bd4da301a` | 10.5630/109 | 15.3188/124 | 13.0302/139 | 13.8615/137 | 17.0930/152 | 17.4196/154 | 17.5198/156 | 11.0936/125 | 21.2829/162 | 106.8038/190 | 2ND/6, 00:01:40, 47%, 49 MPH, 0 pts (viewed) |
| d-post3 (T+512) | 56495B / `1ca8fcf585ab` | 26.3119/155 | 15.8770/157 | 14.7163/132 | 14.2186/143 | 13.9055/151 | 13.9312/151 | 14.0618/151 | 14.2408/115 | 16.0925/159 | 35.1627/115 | 3RD/6, 00:01:44, 49%, 36 MPH, 0 pts (viewed) |
| d-post4 (T+515) | 68564B / `5217fd3a7031` | 17.8594/153 | 13.1410/128 | 13.3484/142 | 11.5669/118 | 13.5490/142 | 14.0948/141 | 14.0957/141 | 12.2185/125 | 19.8355/159 | 28.2584/91 | 3RD/6, 00:01:48, 50%, 35 MPH, 980 pts (viewed) |
| d-post5 (T+517) | 57334B / `b0dff5b05085` | 14.4803/99 | 15.8952/152 | 13.6600/130 | 12.4698/131 | 15.2526/149 | 15.6617/151 | 15.7467/152 | 12.0280/127 | 20.9739/182 | 57.6239/138 | 3RD/6, 00:01:52, 52%, 50 MPH, 1670 pts (viewed) |
| d-post6 (T+520) | 52931B / `3c9a6cc5ff67` | 26.5249/182 | 19.5370/189 | 18.8207/137 | 18.6929/166 | 16.6364/173 | 17.0676/177 | 17.1137/177 | 17.4839/131 | 13.8720/149 | 35.9354/114 | 3RD/6, 00:01:55, 54%, 20 MPH, 1670 pts, RECOVER (viewed) |
| d-post7 (T+523) | 67745B / `045d8b31e133` | 17.0031/136 | 12.7474/122 | 12.8523/134 | 11.9658/123 | 14.8578/162 | 15.2143/162 | 15.3143/162 | 11.2886/117 | 19.5053/162 | 81.7028/163 | 3RD/6, 00:01:59, 55%, 43 MPH, 1670 pts (viewed) |
| d-post8 (T+526) | 51731B / `d19b9078c433` | 11.5394/144 | 15.2819/122 | 13.3422/156 | 13.6886/142 | 17.0889/163 | 17.2451/159 | 17.3489/160 | 11.9074/130 | 25.4774/171 | 98.0770/183 | 3RD/6, 00:02:04, 57%, 49 MPH, 1670 pts (viewed) |
| d-post9 (T+529) | 68713B / `7d602cd5f5bf` | 12.4169/146 | 16.5699/152 | 14.0842/156 | 15.0408/167 | 17.9411/178 | 18.6685/186 | 18.8010/187 | 12.7440/136 | 24.1618/182 | 122.2747/223 | 3RD/6, 00:02:07, 58%, 54 MPH, 1670 pts (viewed) |
| d-post10 (T+532) | 58463B / `5a20c836ea26` | 13.5836/129 | 13.7132/160 | 11.1578/128 | 11.7332/143 | 13.9297/157 | 14.3498/157 | 14.4498/158 | 9.5552/117 | 18.3554/146 | 91.9875/179 | 3RD/6, 00:02:11, 60%, 21 MPH, 1670 pts (viewed) |

In-script (remote) vs PIL agreement: ≤0.06 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr/vs-pp scores at scale (e.g. npre2 band 14.6070 vs
14.6196; npre2 vs-pp 16.4212 vs 16.4099; d-post1 band 18.9655 vs 18.9668);
the known ~3–11× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.3989/7 remote vs 0.0777/0 PIL ≈ 5×; sepre vs-se 0.4075/6
vs 0.0377/0 ≈ 11× — T27 title / T28 menu / T29 SC / T30 ZC / T31 SP /
T32 SM / T33 SE / T34 MR / T35 / T36 precedent); hops ≤0.05. Vs-panel remote
receipt reads 0.72–1.00/p99 10–19 on panel-side PIL 0.46–0.75
(≈1.3–1.6× inflation at the ~0.5 scale — T35/T36 receipt
re-confirmed), so the < 2.0 whole bar holds even remotely (worst
remote 1.0008, 2.0× margin). The TAG crop gap re-confirmed at ~70–280×
(2.6271 vs 0.0094; 2.6292 vs 0.0375). Standing pattern holds:
whole-frame bars calibrated in PIL transfer to remote with single-digit
inflation near zero and ~1× at scale ≥5; text-dense crops need remote
receipts or generous bars.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1156 | 10.1221/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1046 | 0.1317/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2955 | 0.3205/8 | same screen |
| post8 → post15 (mc) | 0.2223 | 0.2432/4 | same screen |
| post15 → scpre (park span) | — | 0.2322/4 | same screen |
| scpre → zc-post1 | 7.2323 | 7.2546/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.2966 | 0.3198/9 | arrival settling |
| post3 → post8 (zc) | 0.2862 | 0.3074/7 | same screen |
| post8 → ccpre (park span) | — | 0.3071/8 | same screen |
| ccpre → sp-post1 | 9.3215 | 9.3589/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0425 | 0.0516/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0208 | 0.0269/0 | same screen |
| post8 → sppre (park span) | — | 0.0454/0 | same screen |
| sppre → pc-post1 | 5.2035 | 5.2285/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0153 | 0.0182/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0239 | 0.0271/0 | same screen |
| post8 → smpre (park span) | — | 0.0280/0 | same screen |
| smpre → rc-post1 | 0.4563 | 0.4820/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps in T32/T33) |
| post1 → post3 (rc) | 0.0017 | 0.0024/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0747 | 0.0783/0 | same screen (rc-post8 snowflake shimmer; still SE: se-tag 0.0094) |
| post8 → sepre (park span) | — | 0.0842/0 | same screen |
| sepre → sj-post1 | 10.5814 | 10.6050/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.0639 | 0.0685/0 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.0881 | 0.0971/1 | same screen |
| post8 → mrpre (park span) | — | 0.0825/0 | same screen |
| mrpre → mr-post1 | 12.5920 | 12.5539/149 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 1.8823 | 1.8966/65 | loading progress 17% → 97% |
| post3 → post8 (mr) | 25.3491 | 25.3593/253 | loading screen → race intro cinematic (no black frame captured this run — transition timing lottery) |
| post8 → post15 (mr) | 19.2207 | 19.2132/190 | cinematic → pre-race panel (panel arrived by +15, one sample early vs T34) |
| post15 → post25 (mr) | 0.2196 | 0.2252/10 | same screen (panel shimmer/animation) |
| post25 → post40 (mr) | 0.1368 | 0.1422/6 | same screen |
| post40 → stab1 (mr) | 0.1459 | 0.1553/6 | same screen |
| stab1 → stab2 (mr) | 0.0500 | 0.0604/2 | same screen |
| stab2 → pppre (park span) | — | 0.1545/6 | same screen |
| pppre → x-post1 | 14.4946 | 14.4777/152 | screen change within +1 s (pre-race panel → countdown/gate; decisive hop) |
| post1 → post3 (x) | 13.8760 | 13.8636/136 | countdown → live gameplay (gate → slope) |
| post3 → post8 (x) | 13.7395 | 13.7792/127 | live gameplay motion |
| post8 → post15 (x) | 9.9123 | 9.9443/137 | live gameplay motion |
| post15 → post25 (x) | 20.2312 | 20.2574/198 | live gameplay motion |
| post25 → post40 (x) | 12.3656 | 12.4071/143 | live gameplay motion |
| post40 → npre1 (span) | — | 13.5573/158 | live gameplay motion |
| npre1 → npre2 | 13.9553 | 13.9830/132 | live gameplay motion (PRE-nudge pair, NO input between) |
| npre2 → d-post1 | 8.4573 | 8.4816/91 | live gameplay motion (nudge tap lands inside this hop) |
| d1 → d2 | 13.3523 | 13.3508/125 | live gameplay motion |
| d2 → d3 | 17.8713 | 17.8561/165 | live gameplay motion |
| d3 → d4 | 10.8001 | 10.8023/128 | live gameplay motion |
| d4 → d5 | 10.1075 | 10.1197/121 | live gameplay motion |
| d5 → d6 | 14.6603 | 14.6731/179 | live gameplay motion |
| d6 → d7 | 16.1339 | 16.1218/171 | live gameplay motion |
| d7 → d8 | 10.8549 | 10.8653/145 | live gameplay motion |
| d8 → d9 | 8.5254 | 8.5471/135 | live gameplay motion |
| d9 → d10 | 9.7863 | 9.7762/115 | live gameplay motion |

### R1 arrival park (pre-race panel)

| Item | Value |
|---|---|
| Post-Enter frames | `t37r1-mr-post1.jpg` @T+328 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 17% Loading…; `mr-post3` @T+333: same screen, 97% Loading…; `mr-post8` @T+341: race intro cinematic, nightclub (`EA RADIO BIG / Deep End - Utah Saints Remix / Swollen Members / Balance` overlay, `Press X to skip`); `mr-post15` @T+350: pre-race panel = arrival (one sample early vs T34's +25) |
| Stability N (panel) | 6 snaps (post15/25/40 + stab1/2 + pppre) spanning T+350→T+429 (79 s) |
| Whole-frame pairwise (PIL) | 0.0604–0.4284/p99 ≤20 across all 15 pairs (panel shimmer/animation; min stab1–stab2 0.0604/2, max post25–pppre 0.4284/20; JPEG shas distinct) |
| Vs-panel-ref (whole) | 0.46–0.75/p99 7–19 across all 6 (all under the 2.0 gate; margins 2.7–4.4×) |
| Vs-MR (whole) | 19.33–19.68/p99 153–154 across all 6 (not My Rules) |
| Vs-SE (whole) | 16.18–16.50/p99 159–160 across all 6 (not Select Event) |
| Vs-SM (whole) | 16.18–16.50/p99 159–161 across all 6 (not Select Mode) |
| Vs-SP (whole) | 16.37–16.61/p99 157 across all 6 (not Select Peak) |
| Vs-ZC (whole) | 19.89–20.25/p99 162–164 across all 6 (not Setup Character) |
| Vs-SC (whole) | 19.16–19.50/p99 172 across all 6 (not Select Character) |
| Vs-menu (whole) | 19.01–19.40/p99 177–179 across all 6 (not menu) |
| Vs-title (band) | 34.52–34.53/p99 184 across all 6 (not title) |
| SE-TAG (crop) | 48.2320/132 identical across all 6 (tagline band static within run; T36's run read 48.5186/132, T35's 48.5040/133, T34's 50.8209/132 — run-dependent, lineup/background phase) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Viggo / Eddie / Allegra / Kaori / Nate` (AI lineup differs run to run — T36: `Zoe/Moby/Nate/Luther/Griff/Marty`, T35: `Zoe/Kaori/Brodi/Viggo/Elise/Griff`, T34: `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`); `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 79 s (all 6 snaps pre-race panel) |

### R1 arrival (countdown → live gameplay; input-free until the nudge)

| Snap (wall T+) | Race clock | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|
| x-post1 (T+434, +0.9 s after XCROSS keyup) | 00:00:00 | gates | — | 0 MPH | — | countdown `2` over the starting gate; riders in gates |
| x-post3 (T+437) | 00:00:02 | 5TH/6 | 1% | 39 MPH | 0 | leaving the gate, start straight, gondola |
| x-post8 (T+444) | 00:00:10 | 5TH/6 | 5% | 51 MPH | 0 | open slope, jump crest ahead |
| x-post15 (T+453) | 00:00:23 | 2ND/6 | 12% | 50 MPH | 0 | banked wall ride, chevron fence |
| x-post25 (T+465) | 00:00:38 | 1ST/6 | 20% | 10 MPH | 0 | in trees/powder, slow |
| x-post40 (T+482) | 00:01:01 | 3RD/6 | 28% | 47 MPH | 0 | halfpipe area, sponsor banners |

Race-clock vs wall-clock (wall since XCROSS keyup 1789980626.071; race
clock read off HUD, HH:MM:SS):

| Snap | Wall since keyup (s) | Race clock (s) | Ratio |
|---|---|---|---|
| x-post1 | 0.9 | 0 | — (countdown) |
| x-post3 | 3.9 | 2 | 0.51 |
| x-post8 | 10.9 | 10 | 0.92 |
| x-post15 | 19.9 | 23 | 1.16 |
| x-post25 | 31.9 | 38 | 1.19 |
| x-post40 | 48.9 | 61 | 1.25 |

Stability N (X): not a static arrival — 6 snaps over 48 s, all 15
whole-frame pairs 9.94–20.26/p99 ≤198 (live gameplay motion; min
x-post8–x-post15 9.9443/137, max x-post15–x-post25 20.2574/198; JPEG shas
distinct). Vs-panel-ref 14.57–25.63 across all 6 (decisively non-panel);
vs-MR 11.41–15.83 (non-MR). No reclaim to any menu/panel (all 6 snaps
countdown/live gameplay, positions/progress/timer all advancing).

### R1 nudge (ONE D-pad Left tap on live gameplay + dense series + tracking)

Nudge row (control / direction / duration / T+ / delivery):

| Item | Value |
|---|---|
| Control | D-pad Left (`Left = Keyboard/Left`, `PCSX2.ini:576`) |
| Direction | Left |
| xdotool key | `Left` (`windowfocus --sync` + `keydown`/`keyup`, all exit 0) |
| Keydown wall | 1789980698.085148914 (T+505.09, uptime 543) |
| Keyup wall | 1789980698.423350756 (T+505.42, uptime 544) |
| Tap duration | 338.2 ms (300 ms `sleep` + ~38 ms xdotool overhead; T36: 338.6 ms — same input class) |
| Pre-nudge pair | `npre1` @T+499 (6.1 s before keydown) + `npre2` @T+503 (2.1 s before keydown), NO input between |
| Delivery | Receipted in-script (`NUDGE_LEFT_KEYDOWN/HELD/KEYUP_WALL` + uptimes in `t37r1-poll.log`); same xdotool path as the 99/99 menu holds |

Pre-nudge HUD (read off the viewed `npre1`/`npre2` snaps):

| Item | npre1 | npre2 |
|---|---|---|
| Race clock | 00:01:26 | 00:01:31 |
| Position | 2ND/6 | 3RD/6 |
| Progress | 40% | 42% |
| Speed | 33 MPH | 57 MPH |
| Score | 0 pts | 0 pts |
| Scene | Rider airborne off a jump, red structure behind | Rider airborne over blue snow |

Dense post-nudge HUD series (read off viewed snaps; wall since nudge
keyup 1789980698.423; race advanced = race clock minus npre2 91 s; wall
span = exposure wall minus npre2 wall 1789980696; nominal 1 s cadence =
`sleep 1` + ~2 s in-script scoring per snap):

| Snap (wall T+) | Wall + | Race clock (+adv) | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|---|
| npre1 (T+499) | −6.4 s (pre) | 00:01:26 (−5) | 2ND/6 | 40% | 33 MPH | 0 | pre-nudge baseline, airborne |
| npre2 (T+503) | −2.4 s (pre) | 00:01:31 (+0) | 3RD/6 | 42% | 57 MPH | 0 | pre-nudge baseline, airborne |
| d-post1 (T+506) | +0.6 s | 00:01:35 (+4) | 2ND/6 | 45% | 37 MPH | 0 | landed, red pillar + beam |
| d-post2 (T+509) | +3.6 s | 00:01:40 (+9) | 2ND/6 | 47% | 49 MPH | 0 | banked chevron turn, AI rider left |
| d-post3 (T+512) | +6.6 s | 00:01:44 (+13) | 3RD/6 | 49% | 36 MPH | 0 | forest carve, wood structure |
| d-post4 (T+515) | +9.6 s | 00:01:48 (+17) | 3RD/6 | 50% | 35 MPH | 980 | riding a log, arms out |
| d-post5 (T+517) | +11.6 s | 00:01:52 (+21) | 3RD/6 | 52% | 50 MPH | 1670 | open slope, sun glare |
| d-post6 (T+520) | +14.6 s | 00:01:55 (+24) | 3RD/6 | 54% | 20 MPH | 1670 | `RECOVER - 0` banner, red structure |
| d-post7 (T+523) | +17.6 s | 00:01:59 (+28) | 3RD/6 | 55% | 43 MPH | 1670 | threading trees |
| d-post8 (T+526) | +20.6 s | 00:02:04 (+33) | 3RD/6 | 57% | 49 MPH | 1670 | open bowl, rail left |
| d-post9 (T+529) | +23.6 s | 00:02:07 (+36) | 3RD/6 | 58% | 54 MPH | 1670 | ice rail bridge |
| d-post10 (T+532) | +26.6 s | 00:02:11 (+40) | 3RD/6 | 60% | 21 MPH | 1670 | open slope carve |

Race-advance vs wall-span (race-advanced-since-npre2 / wall-since-npre2):

| Snap | Race adv (s) | Wall span (s) | Ratio |
|---|---|---|---|
| d-post1 | 4 | 3 | 1.33 |
| d-post2 | 9 | 6 | 1.50 |
| d-post3 | 13 | 9 | 1.44 |
| d-post4 | 17 | 12 | 1.42 |
| d-post5 | 21 | 14 | 1.50 |
| d-post6 | 24 | 17 | 1.41 |
| d-post7 | 28 | 20 | 1.40 |
| d-post8 | 33 | 23 | 1.43 |
| d-post9 | 36 | 26 | 1.38 |
| d-post10 | 40 | 29 | 1.38 |

Rider-pixel tracking series (committed `t37-track.py`; RDC = rider
dark-centroid + validity npix; SCPS = snow column-profile shift + validity
corr; whole hop = PIL per-hop from §hops):

| Snap | RDC cx/cy (px) | RDC npix (frac) | SCPS lag (corr) into this snap | Whole hop into this snap |
|---|---|---|---|---|
| npre1 | 335.9 / 222.2 | 86608 (0.617) INVALID (dark red structure floods ROI) | — | — |
| npre2 | 387.9 / 220.2 | 2139 (0.015) valid | −40 (0.72) RAIL | 13.9830/132 |
| d-post1 | 309.9 / 167.6 | 32372 (0.231) flooded (beam/pillar) | +40 (0.66) RAIL | 8.4816/91 |
| d-post2 | 223.8 / 163.4 | 12177 (0.087) mixed | −40 (−0.38) rail, no match | 13.3508/125 |
| d-post3 | 424.2 / 231.1 | 24831 (0.177) flooded (trees/structure) | −23 (0.89) | 17.8561/165 |
| d-post4 | 313.3 / 354.4 | 30544 (0.218) flooded (log/trees) | −40 (−0.76) rail, no match | 10.8023/128 |
| d-post5 | 436.4 / 151.2 | 9357 (0.067) mixed | +40 (0.63) RAIL | 10.1197/121 |
| d-post6 | 339.5 / 197.6 | 70701 (0.504) flooded (red structure) | −40 (−0.15) rail, no match | 14.6731/179 |
| d-post7 | 376.6 / 204.5 | 18624 (0.133) flooded (trees) | +30 (0.37) weak | 16.1218/171 |
| d-post8 | 324.9 / 300.5 | 1299 (0.009) valid | −40 (−0.41) rail, no match | 10.8653/145 |
| d-post9 | 316.3 / 147.4 | 3786 (0.027) valid-ish | −40 (0.39) rail, weak | 8.5471/135 |
| d-post10 | 448.7 / 212.5 | 8595 (0.061) mixed | −3 (0.66) | 9.7762/115 |

Noise floors on the PRE-nudge pair (no input between npre1/npre2):

| Metric | npre1 → npre2 (no-input gap, 4 s wall / 5 s race) | Noise floor N |
|---|---|---|
| HUD position | 2ND → 3RD (one swap, race's own AI jostling) | 1 swap per ~4 s is ordinary |
| HUD progress/clock | 40% → 42%, +5 s race | monotonic, matches turbo |
| RDC cx | 335.9 → 387.9 (+52.0 px) BUT npre1 npix=86608 INVALID | UNMEASURED — baseline end fails the validity channel |
| SCPS | −40 @ corr 0.72 (RAIL — shift exceeds the ±40 window) | rail-class shift per gap is ordinary |
| Whole hop | 13.9830/132 | motion-class, matches surrounding hops |

Observed (non-)effect characterization (tabled, not verdicts):

| Question | Observed |
|---|---|
| Did position change? | Yes — twice: 2ND→3RD in the PRE-pair gap (no input) and 3RD→2ND in the tap hop (npre2→d1), then 2ND→3RD at d2→d3; 3RD stable d3–d10. The tap-hop swap is the same class as the no-input pre-pair swap — not separable by the brief's own noise-floor rule |
| Did progress change? | Advances monotonically 40% → 60% (race-clock-driven, no jumps) |
| Did the clock change? | Advances steadily: +40 s race over +29 s wall (~1.4×, matches turbo) |
| Did speed change? | Varies 33→57→37→49→36→35→50→20→43→49→54→21 MPH (20 MPH `RECOVER` @d6, 21 MPH carve @d10) — ordinary race-speed excursions distributed across the series, none tap-coincident |
| Did score change? | 0 → 980 by d4 (log ride) → 1670 by d5, flat after — ordinary race scoring, distributed |
| Did heading change (rider pixels)? | RDC swings ±52–200 px step to step but 6/12 snaps fail the validity channel (npix ≫ rider-scale: structures/trees flood the ROI); SCPS alternates rails (+40/−40) nearly every step with mixed corr — the tap hop (+40 @ 0.66) matches the series' normal rail-alternation and the pre-pair gap itself railed (−40 @ 0.72) with no input. No tap-coincident kink exceeds the noise floor on either metric |
| Any HUD discontinuity at the tap? | None separable — position volatility already present pre-tap; progress/clock monotonic; no freeze, no menu, no reclaim |
| In-game registration? | Delivery receipted (focus + keydown/keyup exit 0, 338.2 ms); in-game effect below sampling resolution — see isolation limit |
| Isolation limit | Single run, no same-seed control (AI lineup/RNG differ run to run); the tap's contribution is not separable from the race's own progression in this dense sampling — position swaps, rail-class background shifts, and scene-flooded RDC occur with and without the tap |
| Recipe (one variant per attempt) | (a) longer-hold variant (e.g. 1 s) for a larger maneuver (T36 G1(b)); (b) no-nudge control run at a matched race phase (match phase, not seed — T36 G1(c)); tracking refinements for any rerun: wider SCPS lag window (motion exceeds ±40 px at ~3 s exposure gaps under turbo), validity-gated RDC (skip snaps with npix ≫ rider-scale), exposure gaps closer to true 1 s (score post-hoc, not in-script) |

Post-nudge frame motion (whole-frame PIL): all 66 D pairs 6.86–24.93/p99
≤187 (min npre2–d-post10 6.8596/80, max npre1–d-post8 24.9301/184;
JPEG shas distinct). Motion throughout — no static frame, no freeze, no
menu/panel reclaim in the 33 s tail. Vs-panel-ref 12.36–25.48 across all 12
(decisively non-panel).

### R1 PP-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Departure mrpre→post1 | 12.5920 | > 5.0 | yes |
| Arrival static p25→p40 | 0.1368 | < 1.0 | yes |
| Arrival static p40→s1 | 0.1459 | < 1.0 | yes |
| Arrival static s1→s2 | 0.0500 | < 1.0 | yes → `PP-LIKE`, X-Continue Cross pressed |
| Non-MR (stab2 vs-mr) | 19.4327/153 | > 5.0 | yes |
| Vs-pp receipt (post15/25/40) | 0.7962/10, 0.7227/10, 0.7169/10 | (not a leg — receipt) | tabled (≈1.3–1.6× vs PIL 0.46–0.54; under 2.0 even remotely) |
| Vs-pp receipt (stab1/2) | 0.8390/12, 0.8680/13 | (not a leg — receipt) | tabled |
| Vs-pp receipt (pppre) | 1.0008/19 | (not a leg — receipt) | tabled (≈1.3× vs PIL 0.7468) |

### R1 LIVE gate legs (in-script proxy, remote)

| Gate leg | Value | Bar | Margin | Pass? |
|---|---|---|---|---|
| Departure pppre→x-post1 | 14.4946 | > 5.0 | 2.9× | yes |
| Non-panel (x-post40 vs-pp) | 15.5820/149 | > 5.0 | 3.1× | yes |
| Motion (x-post15→x-post25) | 20.2312 | > 5.0 | 4.0× | yes |
| Motion (x-post25→x-post40) | 12.3656 | > 5.0 | 2.5× | yes → `LIVE-LIKE`, pre-nudge pair + ONE nudge pressed |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Live race reproduced (HUD advancing, rider moving) | countdown `2` at +0.9 s, live gameplay from +3.9 s, race 3RD/6 at 60% by +99 s wall with one steering tap; clock/progress advance monotonically, all X+D hops 8.48–20.26 (motion) |
| Tap acted on it (pre-tap = racing with HUD read) | `npre2` viewed: 00:01:31, 3RD/6, 42%, 57 MPH, 0 pts, rider airborne mid-race; vs-pp 16.41 (non-panel); `npre1` viewed: 00:01:26, 2ND/6, 40% |
| Dense 10-snap series + tracking table (or exact non-separability finding with noise floor) | 12-snap HUD series above (position 2ND↔3RD swaps pre- and post-tap, progress 40→60%, clock +40 s, speed/score excursions distributed, `RECOVER` @d6) + RDC/SCPS per-snap table + pre-pair noise floors (RDC unmeasured/invalid, SCPS rail) + isolation limit + recipe |
| Full input log + trace sha | `t37r1-poll.log` (158 lines: every score + press, walls + uptimes) + trace `1ade4573…8d7da7cc1` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32/T33/T34/T35/T36 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725,
first vblank L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks
397 frozen (all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not
changed`; clean tail @552.7102. Census: EE 12,427,624 (52, set-identical
to T36 R1) · IOP 20,134,493 (155, set-identical to T36 R1 — dense series +
gameplay adds no new called API) · `libsd.006: sceSdGetParam` 23391
(T36: 23484); `sceSdGetAddr` 4,023,600 (T36: 4,038,240).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R1 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate → Enter Cross → PP-LIKE settled-panel gate → X Cross → LIVE-LIKE proxy gate) |
| Cross on X Continue? | YES (XCROSS @T+432.53 R1, pre-press = pre-race panel, X Continue) |
| Live race reached? | YES (countdown `2` @T+434 → live gameplay by T+437 → race at 60%, 3RD/6 @T+532, still running) |
| Nudge on live gameplay? | YES (NUDGE Left 338.2 ms @T+505.09, pre-nudge pair = racing 00:01:26 2ND/6 40% / 00:01:31 3RD/6 42%) |
| Separable tap response? | NOT separated — dense HUD + RDC/SCPS series tabled with pre-pair noise floors; tap-hop behavior matches no-input behavior class (position swap, rail-class shift) |
| Bounded variant? | none run (pre-nudge = racing — variant condition not met; brief stops at R1 + recipe) |
| 1200 s cap | Not reached — R1 ≈ T+562; attempts 2–3 unexercised |
| Chain end | Live Snow Jam race (3RD/6, 60%, 00:02:11) after ONE steering tap + dense 10-snap series; race not yet finished at capture end |

## T37-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t37 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules → Cross → game load → cinematic → pre-race panel → Cross → countdown → live gameplay → pre-nudge pair → D-pad Left tap → dense 10-snap series, T+~562) | 45,362,838 / 2,907,114,770 | `1ade45733595b77b7e597f87a277be69b7a051e682e648610f1d6418d7da7cc1` (analyze-sha on H21 = post-restart re-verify on H22 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t37r1.txt`, same size+sha (match; streamed via `wsl cat`, no C: staging — C: at 3.9 G) + committed head/tail 2000+2000 (`t37r1-trace-head.txt` 149019 B sha `3df9f1befdd4…`, `t37r1-trace-tail.txt` 131136 B sha `f22e9ab61ebc…`) |
| `emulog-pre-t37-20260921T084313Z.txt` = t36 R1 (preserved at R1 boot) | — / 2,885,188,969 | `a6f43f21064fe9b5a9ae6e18333af219fb4118fd8495afd046c4beab918142bf` (re-verified post-run: matches T36) | bytesize-only (T36 precedent; SSD holds T36's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 12,427,624 (52
distinct, set-identical to T36 R1) · IOP 20,134,493 (155, set-identical
to T36 R1) · vblanks 397. Committed: `t37r1-census.txt` (11699 B sha
`acc4bee73279…`), `t37r1-samples.txt` (5882 B sha `f65bc808f996…`),
`t37r1-poll.log` (158 lines, 9686 B sha `387ebc96497e…`),
`t37r1-stdout.txt` (437 lines, 28582 B),
`t37r1-stderr.txt` (full `set -x` shell trace, 2556 lines, 141390 B),
`t37r1-trace-head.txt` / `t37r1-trace-tail.txt`.
Trace-head note: same 149019 B as T34/T35/T36 R1 heads but sha differs
(`3df9f1be…` vs `8682e642…`) — timestamp-stripped content differs across
timing/wall-clock/shader-cache lines (`gl_programs.idx` cache entries:
301 vs 287 vs 240 vs 173 — shader cache growth across runs).

## T37-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H20 …870
ssh bytesize 'wsl dmesg' > /tmp/t37-dmesg-pre.txt                     # 440 lines, 0 AcceptAsync (H20)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t37-eventlog-pre.txt  # head 04:37:50
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl grep -n Left …/inis/PCSX2.ini'                      # Left = Keyboard/Left :576
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t35-ref-panel.ppm'    # all 9 refs reproduce
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c'                         # 881G / C: 3.9G
ssh bytesize 'wsl ls …/logs/; ls -la …/logs/emulog.txt'                # 24 emulogs, live = T36 R1
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # a6f43f21… T36R1 live
# T36 ref snaps (local): 13/13 sizes reproduce T36 §T36-2
# freeze t37-track.py (RDC + SCPS) + calibrate on T36 x-series/npre (determinism cmp clean)
# adapt t37-auto.sh from the T36 copy (pre-pair + dense d-post1..10; bash -n), t37-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t37-auto.sh t37-analyze.sh t37-vcount.sh t37-cropdiff.py "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t37-… /home/brad/pcsx2-t4/; sha256sum …'  # staged shas match local
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H21
ssh bytesize 'wsl dmesg' > /tmp/t37-dmesg-preH21.txt                  # 441 lines, 0 AcceptAsync (H21)
ssh bytesize 'wsl sha256sum …/t37-auto.sh …/t37-cropdiff.py …/t35-ref-panel.ppm …/bin/pcsx2-qt'  # staged shas survive restart
ssh bytesize 'wsl python3 …/t37-cropdiff.py …REFPP …'                  # 0.0000/0 PPM
ssh bytesize 'wsl git … rev-parse HEAD; … status --short; sha256sum …nvm; grep -n Left …'  # full re-verify on H21
# R1 (ONE ssh; exit 0; LIVE-LIKE → PRE-PAIR → NUDGE → dense 10)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t37-auto.sh' > /tmp/t37r1-run-stdout.txt 2>/tmp/t37r1-run-stderr.txt  # T37_DONE, up 39→601
ssh bytesize 'wsl dmesg' > /tmp/t37-dmesg-post-r1.txt                 # IMMEDIATELY after run ssh: 442 lines, 0 AcceptAsync (H21, full R1 coverage)
ssh bytesize 'wsl bash …/t37-analyze.sh'                              # 1ade4573…, 45362838 L
ssh bytesize 'wsl bash …/t37-vcount.sh; wc -l …/t37-poll.log; ls …/t37-*.jpg'  # 397 frozen / 158 / 61 JPGs
ssh bytesize 'wsl cp <30 chain jpg> /mnt/c/…'                          # (explicit list, one wsl call)
ssh bytesize 'wsl cp <31 d/mr/x jpg + poll.log + census/samples> /mnt/c/…'  # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t37-…" /tmp/t37-fetch/                         # 61 jpg + logs (r1-prefixed local)
# R1 post-hoc (local fastdiff, 4/4 bit-exact): chain panel, hops, 15 panel pairs, 15 X pairs, 66 D pairs, xrun, census set-compare, t37-track.py dense series
ssh bytesize 'wevtutil …' > /tmp/t37-eventlog-post.txt                # head H21-teardown 04:56:26; H20→H21 04:39:57/04:42:34; 2x Volsnap ID 33 in-window 04:44:31, ZERO Hyper-V in-window
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H22 …327 (fresh, created by this call)
ssh bytesize 'wsl dmesg' > /tmp/t37-dmesg-post.txt                   # 448 lines, 1 AcceptAsync [17.18] (H22)
ssh bytesize 'wsl sha256sum …nvm; ls -la …nvm; sha256sum …/logs/emulog.txt; ls -la …; ls …/logs/'  # NVM untouched, 1ade4573… re-verified, 25 emulogs
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t37-20260921T084313Z.txt; ls -la …'  # a6f43f21… T36R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t37r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t37r1-trace-tail.txt         # 2000 lines, clean tail @552.7102
ssh bytesize 'wsl grep -c LoadStartModule …/logs/emulog.txt'           # 18
# SSD copy (COPYFILE_DISABLE=1; streamed via wsl cat — no C: staging at 3.9G — then shasum re-verify)
ssh bytesize 'wsl cat <trace>' > "/Volumes/Extreme SSD/ps2x-t4/emulog-t37r1.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t37r1.txt"         # 1ade4573… match
ssh bytesize 'wsl df -h / /mnt/c; du -sh …/logs/; date -u; cat /proc/uptime; grep btime /proc/stat'  # 877G / C: 8.0G / 34G / VM-H22
ssh bytesize 'wevtutil qe System /c:12 /rd:true /f:text' > /tmp/t37-eventlog-final.txt  # H21-teardown 04:56:26, H22-create 05:02:07
# report (chunks; receipts include tail -3)
cp /tmp/t37-dmesg-*.txt /tmp/t37-eventlog-*.txt /tmp/t37r1-run-stdout.txt … local/research/T37/  # renamed per §evidence
tail -3 local/research/T37/REPORT.md
git add -f local/research/T37/<81 files by name>                      # ignored dir, forced
git commit -m "[T37] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T37-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (steering characterization) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate (departed + non-SE + static) → Cross on Continue → PP-LIKE settled-panel gate (departed + static ×3 + non-MR) → Cross on X Continue → LIVE-LIKE proxy gate (departed + non-panel + motion ×2) → ≤3 attempts) → live gameplay; then a single 300 ms D-pad Left tap acts on the live race (R1: pre-nudge pair 00:01:26 2ND/6 40% / 00:01:31 3RD/6 42%, dense 10-snap series to 00:02:11 3RD/6 60% with no separable tap response — position 2ND↔3RD swaps occur with and without the tap, RDC validity-flooded 6/12 snaps, SCPS rails ±40 nearly every step including the no-input pre-pair gap; race clock ~1.4× wall under turbo). Next, ONE variant per attempt: (a) longer-hold variant (e.g. 1 s) for a larger maneuver; (b) no-nudge control run at a matched race phase (match phase, not seed — AI lineup/RNG differ run to run). Tracking refinements for any rerun: wider SCPS lag window (motion exceeds ±40 px at ~3 s exposure gaps under turbo), validity-gated RDC (skip snaps with npix ≫ rider-scale), exposure gaps closer to true 1 s (score post-hoc, not in-script). Gate note: the nudge→gameplay whole-frame hop is large (~8.48–17.86 dense) because the race never stops moving — gate on the HUD (clock/position/progress/speed/score), not the frame. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | Zero in-window flaps this session + 1 pre-session + 1 mid-session + 1 post-everything restarts (all not by me) + 2× in-window Volsnap (effects-verified) | 0 userland kills on any VM this session; AcceptAsync exact counts 0/0/0/1 across the 4 committed dmesg files, all outside the run window (H20-pre 0; H21-pre 0; H21-post 0, full R1-window coverage, zero in-window; H22-post 1×[17.18] post-everything VM) + 1 pre-session VM restart between T36 and T37 (H19→H20; T36: 1 pre-session restart) + 1 mid-session VM restart between pre-checks and staging (H20 08:37:50→08:39:57, H21 create 08:42:34; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified) + 1 post-everything VM restart (H21→H22 08:56:26, after all fetch WSL calls — proven by H22's 2.15 s uptime at the 09:02:09 identity check; only final state reads + trace slices ran on H22). 2× Volsnap ID 33 (shadow-copy deletion, C: pressure housekeeping) at 08:44:31 fall inside the R1 window — NOT VM events (zero Hyper-V-VmSwitch/teardown/create entries in-window, zero AcceptAsync in-window); R1 completed exit 0 with T37_DONE + all 61 snaps + clean trace tail, i.e. effects-verified per the T27 §4 rule (the immediate post-run dmesg read closed T33's sequencing gap). Precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: 2× Volsnap in-window; boundaries bound all restarts | Newest-30 reads (pre/post): H19 teardown 04:16:00 → H20 create 04:37:50 → H20 teardown 04:39:57 → H21 create 04:42:34 → H21 teardown 04:56:26; inside the R1 window 04:43:13–04:52:36 (local): 2× Volsnap ID 33 at 04:44:31 (oldest C: shadow copy deleted to keep shadow usage below limit — C: at 100%/3.9 G; no Hyper-V-VmSwitch — precedent stands). Final newest-12: H21 teardown 04:56:26 → H22 create 05:02:07. `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H21 btime |
| G4 | Hold count 99/99 (534 ms-class) + 2/2 nudge taps (300 ms-class) | 534 ms-class holds register 99/99 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33+T34+T35+T36+T37 (T37 R1: 535.1/536.7/536.6/535.5/536.0/536.4/535.0/536.5/535.8/538.7 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect. Separately: the 300 ms-class steering tap delivered 2/2 (338.2 ms wall: 300 ms sleep + ~38 ms xdotool overhead; T36: 338.6 ms) — different input class, not a bisection |
| G5 | Title/menu/SC/ZC/SP/SM/SE/MR frozenness; attract differs; snowflake shimmer on SE + MR; panel animation + lineup lottery on arrival; countdown near-frozen; gameplay lottery | Title text-band frozen across showings (0.0453/0 R1); R1's 2 frames bit-identical to T36 R1's run (a1-post8, a1-post15 — a1-post15 now identical across THREE runs T35/T36/T37); menu whole-frame ≤0.07/p99 ≤1 cross-run; SC cross-run 0.09–0.22/p99 1–5; ZC cross-run 0.09–0.11/p99 1–2; SP cross-run ≤0.11/p99 ≤1; SM cross-run 0.008–0.05/p99 0–1; Select Event ≤0.08/p99 0 cross-run except rc-post8 snowflake animation (rc-post1/3 near-identical 0.0018/0.0030 but NOT bit-identical this run — shimmer phase); My Rules ≤0.15/p99 ≤2 (snowflake drift); pre-race panel ≤0.43/p99 ≤20 within run over 79 s (panel shimmer/animation) + AI rider lineup differs run to run (T37 `Zoe/Viggo/Eddie/Allegra/Kaori/Nate` vs T36 `Zoe/Moby/Nate/Luther/Griff/Marty` vs T35 `Zoe/Kaori/Brodi/Viggo/Elise/Griff` vs T34 `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`) + SE-TAG crop on panel constant within run but run-dependent (48.2320/132 vs T36's 48.5186/132 vs T35's 48.5040/133 vs T34's 50.8209/132); load→panel transition timing is lottery-dependent (T37: 97% @+5, cinematic @+8, panel @+15 — same shape as T35/T36, different cinematic track: Deep End Utah Saints Remix vs Clockworks vs Buffet of Breaks) — the settled-panel gate handled all timings; countdown-`2` gate frame near-frozen cross-run (1.9146/68); live gameplay never static (9.94–20.26 X, 6.86–24.93 D). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the dense-series run | `WaitVblankStart` stops after log ≤90 in T37 R1 including countdown + live gameplay + pre-pair + nudge + dense series (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T36-R1-identical modulo counts). The attract/title/menu/submenu/game sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical; IOP count shifts on audio) | Like prior arrivals, dense series + gameplay adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T36 R1; counts shift (`GetThreadId` 5.02M→5.13M, EE total 11.75M→12.43M; IOP 20.23M→20.13M; `sceSdGetParam` 23484→23391, `sceSdGetAddr` 4.04M→4.02M — race audio traffic). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts + C: pressure | `…/logs/` now holds ~34 GB across 25 emulogs (T17→T37 chain, all preserved); C: 8.0 G avail final (3.9 G pre-run — Volsnap shadow cleanup freed space; T36 final was 3.9 G). C: still at 100% — next session should clear `C:\Users\bradr\pcsx2-t4\` staging (owner's call; left in place per precedent). T37 R1 full trace SSD-copied + sha-verified (2.91 GB: `emulog-t37r1.txt`, streamed via `wsl cat` to avoid C: staging); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T37 brief cites `t36-auto.sh`, `t36-cropdiff.py`, `t36-analyze.sh`, `t36-vcount.sh` — all 4 exist in `local/research/T36/` and were copied (not modified) for T37. T28 G9 lesson holds |
| G10 | Session wall + run durations | ~70 min active of the 4 h box (one run + report/commit); zero lease waits (no lease exists for T37). R1 wall 562 s — 202 s over the ≤6 min guidance (X-phase scoring + dense tail); R1 full dmesg coverage, zero flaps |
| G11 | X11 mount needed once, harmless | The single `/tmp/.X11-unix` tmpfs mount landed on VM-H21 (the H20→H21 restart fell between pre-checks and staging); mount verified present on H21 pre-R1, R1 started Xvfb :99 cleanly regardless (exit 0 + 61 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 / T33 G11 / T34 G11 / T35 G11 / T36 G11 stand) |
| G12 | Remote-vs-PIL gap receipted again on the panel whole bar: ~1.3–1.6×, bar holds even remotely | R1's in-script vs-pp receipt reads 0.72–1.00/p99 10–19 on panel-side PIL 0.46–0.75 (≈1.3–1.6× inflation at the ~0.5 scale — T35's 1.3–1.6× / T36's 1.4–1.8× receipts re-confirmed on a new run), so the < 2.0 whole bar holds even as an in-script leg (2.0× margin on the worst remote 1.0008). The TAG-crop gap re-confirmed at ~70–280× (2.6271 vs 0.0094; 2.6292 vs 0.0375). Standing pattern holds: whole-frame bars calibrated in PIL transfer to remote with single-digit inflation near zero and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars |

## Evidence files

`REPORT.md` (this file),
scripts: `t37-auto.sh`,
`t37-cropdiff.py` (T36 logic, byte-identical),
`t37-track.py` (frozen rider-pixel tracker: RDC + SCPS),
`t37-analyze.sh`, `t37-vcount.sh` (output-name deltas only; vcount
byte-identical);
R1: `t37r1-start.jpg`, `t37r1-a1-now.jpg`, `t37r1-a1-poll01.jpg`,
`t37r1-a1-pre.jpg`, `t37r1-a1-post{3,8,15,25}.jpg`, `t37r1-menupre.jpg`,
`t37r1-mc-post{1,3,8,15}.jpg`, `t37r1-scpre.jpg`,
`t37r1-zc-post{1,3,8}.jpg`, `t37r1-ccpre.jpg`,
`t37r1-sp-post{1,3,8}.jpg`, `t37r1-sppre.jpg`,
`t37r1-pc-post{1,3,8}.jpg`, `t37r1-smpre.jpg`,
`t37r1-rc-post{1,3,8}.jpg`, `t37r1-sepre.jpg`,
`t37r1-sj-post{1,3,8}.jpg`, `t37r1-mrpre.jpg`,
`t37r1-mr-post{1,3,8,15,25,40}.jpg`, `t37r1-mr-stab{1,2}.jpg`,
`t37r1-pppre.jpg`, `t37r1-x-post{1,3,8,15,25,40}.jpg`,
`t37r1-npre{1,2}.jpg`, `t37r1-d-post{1,2,3,4,5,6,7,8,9,10}.jpg` (61 snaps),
`t37r1-census.txt`, `t37r1-samples.txt`, `t37r1-poll.log`,
`t37r1-stdout.txt`, `t37r1-stderr.txt`, `t37r1-trace-head.txt` / `t37r1-trace-tail.txt`;
flaps: `t37-dmesg-vmH20-pre.txt` (0 AcceptAsync on H20, pre-run) /
`t37-dmesg-vmH21-pre.txt` (0 AcceptAsync on H21, pre-window) /
`t37-dmesg-vmH21-post.txt` (0 AcceptAsync; full R1-window
coverage, zero in-window) / `t37-dmesg-vmH22-post.txt` (1 AcceptAsync
[17.18] on H22, fresh boot),
`t37-eventlog-pre.txt` / `t37-eventlog-post.txt` / `t37-eventlog-final.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t37r1.txt`
(2,907,114,770 B `1ade4573…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T36 R1
`…-20260921T084313Z.txt` `a6f43f21…`.
