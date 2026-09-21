# T38 report — longer-hold steering variant (1 s D-pad Left) on the live race (bytesize, no lease)

Brief: T38 (T37's G1(a): longer hold). Tables, no verdicts. One boot ran
on bytesize (R1: chain reproduced to live gameplay, ONE 1 s D-pad Left HOLD
on the live race at 00:01:31 2ND/6 44%, PRE-hold pair + DENSE 10-snap
post-hold series mapped with rider-pixel tracking + T37 refinements);
laptop-side work was ssh/scp + local reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T37/REPORT.md` (all of it: R1
reproduced the chain to LIVE gameplay, ONE 338.2 ms D-pad Left tap @T+505.09
on a live race (pre-pair 00:01:26 2ND/6 40% / 00:01:31 3RD/6 42%), dense
10-snap post-tap series to 00:02:11 3RD/6 60% with NO separable tap response
— position 2ND↔3RD swaps occur with and without the tap, RDC validity-
flooded 6/12 snaps, SCPS rails ±40 nearly every step including the no-input
pre-pair gap; race clock ~1.4× wall under turbo; G1 proposes (a) longer
hold, (b) no-nudge control — this brief takes option (a)). This brief
executes T37's G1(a).

Experiment contract (up front): hypothesis — one bounded 1 s steering hold
(single D-pad Left keydown, `sleep 1`, keyup — brief-authorized new input
class, the ONLY input change vs T36/T37) delivered to live Snow Jam
gameplay produces a separable heading response resolvable by dense (1 s
cadence × 10 s) post-hold sampling + rider-pixel tracking; observable —
pre-hold pair = live race (race clock + position/progress HUD read off the
viewed snaps), the hold row (control / direction / duration / T+), dense
10-snap series + per-snap HUD + tracking metrics + per-hop whole diffs;
screen content read off viewed snaps; alternatives — dense series +
tracking STILL show no separable hold response (deadzone, wrong control,
response below pixel resolution → table the exact observed series +
tracking + noise floor + recipe), hold provably never acted on live
gameplay (pre-hold ≠ racing → ONE bounded variant allowed); stop — table
the exact observed behavior + recipe, one input variant per attempt, never
blind multi-presses.

## T38-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T38; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T38]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; verified
on VM-H23 before R1):

| Item | T4 value | T38 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Hold binding used | — | `Left = Keyboard/Left` (`PCSX2.ini:576`), xdotool key `Left` | tabled §T38-1 |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…580eb6` reproduces T35 | yes |
| T37 reference snaps present | — | all 12 sizes reproduce T37 §chain (`npre1/2` 46913/51033, `d-post1..10` 59303/58477/56495/68564/57334/52931/67745/51731/68713/58463) | yes |
| Free space | — | WSL `/` 877 G pre / 874 G final; C: 8.0 G pre / 4.6 G final (100%); laptop `/` 1.4 Gi avail; SSD 302 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1, on VM-H23 pre-R1 (no restart between pre-checks and staging this session) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t38-{auto,analyze,vcount,cropdiff}.sh/.py`, `t38-{r1-census,samples}.txt` (via analyze), `t38-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t38-*.txt` (rotation chain, see trace table), `boot-t38.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t38*` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 1 pre-session between T37 and T38 (H22→H23) + 2 post-everything (H23→H24 09:56:06, H24→H25 10:04:31–10:05:25, both after all fetch WSL calls); ZERO mid-session, ZERO in-window |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H24 btime:
05:59:36→`1789984776`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 09:05:54 | VM-H22 teardown (T37's post-everything VM, after T37's session) | eventlog-pre (IDs 71/69/233/234/234) |
| 2 | 09:41:21 ([0] VM-H23) | VM-H23 started fresh ~1 s before first ssh | btime `…680`, eventlog-pre head (IDs 292/67/291/233/232/102/291/102/291/291) |
| 3 | 09:41:22–09:42:42 | Pre-run checks (all ssh exit 0) + C:-staging + WSL-staging (shas match local) + X11 mount + PPM self-check 0.0000/0, all on VM-H23 (btime re-verified `…680`, uptime 81 — no restart between pre-checks and staging) | `t38-dmesg-vmH23-pre.txt` (0 AcceptAsync, 440 lines, 23 `Ioctl failed` — captured at uptime ~2 s, before dxg queries) |
| 4 | 09:42:48–09:52:17 ([94]→[657] H23) | R1 single-shot exit 0, `T38_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart in-window; ZERO Volsnap/Hyper-V entries in-window) | exit 0, 61 snaps, trace sha |
| 5 | 09:52:17–~09:55 | R1 dmesg read (IMMEDIATELY after run ssh) + analyze (exit 0) + vcount + all R1 fetches (exit 0) on VM-H23 | `t38-dmesg-vmH23-post.txt` (474 lines, 1 AcceptAsync [25.74] pre-window boot), `t38-census.txt`, 61 JPGs + logs |
| 6 | 09:56:06 | VM-H23 teardown (post-everything restart #1, NOT by me) | eventlog-post head (IDs 71/69/233/234/234 teardown) |
| 7 | 09:59:36–~10:04 (VM-H24) | VM-H24 fresh: identity + dmesg + NVM/trace/preserved-sha re-verifies + trace head/tail slices + SSD stream + df-final (exit 0) | `t38-dmesg-vmH24-post.txt` (1 AcceptAsync [16.89], 448 lines, boot coverage) |
| 8 | 10:04:31–10:05:25 | VM-H24 teardown → VM-H25 create (post-everything restart #2, NOT by me; only a final identity read ran on H25) | btime `…125`, `t38-eventlog-h25.txt` (IDs 71/69/233/234/234 teardown, 292/67/291/233/232/102/291/… create) |
| 9 | event log | Newest-30 reads (pre/post): head moves H23-create 05:41:21 → H23-teardown 05:56:06; boundaries H22-teardown 05:05:54, H23-create 05:41:21, H23-teardown 05:56:06, H24-create 05:59:36, H24-teardown 06:04:31, H25-create 06:05:25; in-window (05:42:48–05:52:17 local) entries: ZERO of any kind — userland kills would leave no Windows trace (T17/T21/T23/T25/T27/T28/T29/T30/T31/T32/T33/T34/T35/T36/T37 precedent stands) | `t38-eventlog-{pre,post,final,h25}.txt` |
| 10 | dmesg noise | `Ioctl failed` lines 23/46/23 across the 3 files (pre 23 boot/GPU-query noise; post-R1 46 — run-window dxg queries add 23 more of the same class; kill-pattern grep (`killed process\|out of memory\|panic\|oops\|segfault`) matches only the 2 `panic=-1` cmdline echoes per file | dmesg files |

AcceptAsync exact counts with uptime-stamp positions relative to the R1
window (T_BOOT uptime 94 → end 657, all on VM-H23):

| Committed file | Lines | AcceptAsync count | Uptime stamps | Position vs run window |
|---|---|---|---|---|
| `t38-dmesg-vmH23-pre.txt` | 440 | 0 | — | same VM, pre-window; outside |
| `t38-dmesg-vmH23-post.txt` | 474 | 1 | [25.737950] | same VM, full R1-window coverage; stamp is pre-window boot (T_BOOT uptime 94); ZERO in-window (kernel quiet after uptime 76 — last line [76.08]) |
| `t38-dmesg-vmH24-post.txt` | 448 | 1 | [16.886705] | different VM (post-everything, no run); outside |

## T38-1. Hold selection + series shape + tracking method (frozen BEFORE the run) + LIVE calibration

Tool: `t38-cropdiff.py` (copy of T37's, byte-identical; `cmp` clean;
`t38-vcount.sh` byte-identical to T37's; `t38-analyze.sh` differs only in
output names). Title text-band method unchanged (thresholds frozen: TITLE
band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu
mean < 2.0; NONMENU / NONSC / NONZC / NONSP / NONSE / NONMR whole-vs-ref
mean > 5.0; DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). Panel
reference reused (`t35-ref-panel.ppm`, already staged, sha re-verified).
No new reference (no new static screen to gate on). Remote PPM-mode
self-check pre-run: panel ref 0.0000/0.

Hold selection (tabled BEFORE the run, per brief — the ONLY input-class
change vs T36/T37; do NOT stack taps):

| Item | Value |
|---|---|
| Control | D-pad Left (NOT analog) |
| Binding | `Left = Keyboard/Left` (`PCSX2.ini:576`) |
| xdotool key | `Left` |
| Duration | Single 1 s HOLD (`keydown`, `sleep 1`, `keyup`) |
| Direction | Left |
| When | After the X arrival series, on the LIVE-LIKE proxy gate (≈T+505, deep in live gameplay per T35's/T36's/T37's race shape) |

Series-shape choice (tabled BEFORE the run, per brief — pick ONE):

| Option | Shape | Choice |
|---|---|---|
| Dense (T37's) | 1 s cadence × 10 s post-hold series | CHOSEN — the T36 tap and T37 tap both showed no gross effect, so resolution is prioritized over span; a gross hold effect still reads at 1 s cadence |
| Sparse (T36's) | +1/+3/+8/+15/+25/+40 tail | rejected pre-run (span buys nothing if the response is immediate; the brief's "gross effect" clause cannot be evaluated before the run, so the denser default stands) |

Tracking method (tabled BEFORE the run, per brief — frozen in committed
`t38-track.py`, sha `58afa004…91c108`; T37's RDC + SCPS(±40) computed
unchanged for comparability, plus the two cheap T37 recipe refinements):

| Metric | Definition (fixed) | Rationale |
|---|---|---|
| RDCX/RDCY | T37-frozen: centroid (0.1 px) of dark pixels (luminance < 80) inside rider ROI x[150,540] y[100,460]. Reports cx/cy/npix/dark-fraction; npix is the validity channel | Rider outfit is near-black against bright snow; a Left carve displaces the rider sprite laterally before the chase cam re-centers |
| RDC gate (NEW) | VALID iff 200 ≤ npix ≤ 6000 (rider-scale band; T37 calibration: valid snaps npix 1299–3786, mixed 8595–12177, flooded ≥ 18624; T36 npre rider-clean 2462). Gated-out snaps print INVALID and their cx/cy must not be used for deltas | T37 recipe: validity-gated RDC (skip snaps with npix ≫ rider-scale) |
| SCPS40 | T37-frozen: snow column-profile shift (integer lag px in [−40,+40]) between consecutive snaps over x[150,540] of rows y[380,460], normalized xcorr best lag (+ = scene moved right). Reports lag + peak corr; corr is the validity channel | Under a chase cam the world rotates around the rider, so a heading change reads as background lateral shift even when the rider stays centered |
| SCPS120 (NEW) | Same normalized-xcorr column-profile shift over lag in [−120,+120] (3× the T37 window) | T37 recipe: wider SCPS lag window (motion exceeded ±40 px at ~3 s exposure gaps under turbo — T37 railed nearly every step incl. the no-input pre-pair gap) |

Noise-floor measurement plan (frozen BEFORE the run): the script captures
a PRE-hold pair (`npre1`, `sleep 2`, `npre2`) with NO input between; the
noise floor N = |M(npre2) − M(npre1)| per metric (race motion over the
no-input gap). A hold-correlated delta may be claimed only for a post-hold
excursion/kink exceeding N with hold-coincident timing. Determinism check
pre-run: tracker run twice on T37 npre2/d-post1 → `cmp` clean (identical
bytes in, identical numbers out, no RNG). Cross-check pre-run: T38 RDC +
SCPS40 reproduce T37's numbers exactly on T37 npre2/d-post1 (cx 387.9/309.9,
npix 2139/32372, SCPS40 +40 @ 0.6592); SCPS120 resolves the same pair at
+82 @ 0.8588 (wide window demonstrably un-rails a T37-railed hop).

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
position/progress HUD present — is read off VIEWED snaps post-hoc, not
whole-frame scores (T35 G1 gate note: gate on the HUD, not the frame).
Every proxy leg carries ≥1.9× margin on the T35 receipts.

Script deltas vs `t37-auto.sh` (committed originals untouched; `t38-auto.sh`
is the adapted copy):

| Area | T37 script | T38 script |
|---|---|---|
| Chain | park phase + full menu→MR chain + PP gate + XCROSS + x series to +40 + LIVE gate + pre-pair + nudge + dense d-post1..10 + 11 per-hop whole diffs | identical through the LIVE-LIKE gate; hold phase identical except the input |
| Hold input | ONE `press_nudge Left` (300 ms `sleep`) | ONE `press_hold Left` (1 s `sleep`) — the ONLY input-class change; label `HOLD_LEFT`; pre-pair + dense d-post1..10 + 11 per-hop whole diffs unchanged |
| Self-tests | SELF_TEST + … + SELF_MR + SELF_PP | unchanged (all 11 re-run) |
| No-park paths | explicit `NO-PARK` + … + `NO-LIVE-PARK` | unchanged (still clean shutdown + `T38_DONE`, trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
batch port of `t38-cropdiff.py` (`/tmp/t38-batch.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical)
against the committed tool on 4 diverse pairs (panel-panel 0.0927/3,
gameplay-motion 15.1396/155, title-vs-ref 0.0453/0, SE-vs-ref 0.0363/0).
Any score reproduces with the committed `t38-cropdiff.py`, slower. The 9
ref PPMs were reused from `/tmp/t36-refs/` for post-hoc scoring (all 9
shas re-verified, match §T38-0).

## T38-2. R1 — race reproduced, ONE 1 s steering hold + dense series on live gameplay

Run: `t38-auto.sh`, ONE fresh boot, T_BOOT wall 1789983775 (uptime 94,
VM-H23), 09:42:48–09:52:17 UTC (uptime 94→657 = 563 s; 203 s over the
≤6 min guidance — the X phase + dense tail; full dmesg coverage, zero
flaps in-window), WID 2097159 (same as T31 R1 / T32 R1 / T33 R1 / T33 R2 /
T34 R1 / T35 R1 / T36 R1 / T37 R1), exit 0, `T38_DONE`, clean SIGTERM shutdown.
SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC
0.0000/0, SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM 0.0000/0, SELF_SE
0.0000/0, SELF_SETAG 0.0000/0, SELF_MR 0.0000/0, SELF_PP 0.0000/0.
Attempt 1 of ≤3 consumed; attempts 2–3 not needed (chain advanced to the
hold, dense series mapped). No bounded variant run (pre-hold = racing —
variant condition not met, brief stops here).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+100, score 0.4337/6 remote / 0.0453/0 PIL (T37 R1: identical 0.4337/6 / 0.0453/0 — same detector reading AND bit-identical frame, see xrun) | Cross 535.2 ms @T+98.39 (attract-skip) + Start 535.5 ms @T+101.67 (on title, ≤1.8 s after exposure) | Main Menu by +5 s; menu-like gate (non-title + whole-static 0.0366/0.0168) + post25-vs-menu 0.3002/5 → park for menu Cross |
| A2–A3 | not run (chain advanced) | — | — |

### R1 cross-run frame identities (T38 R1 vs T37 R1, full sha256)

| Frame | T38 R1 sha | T37 R1 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `4a9c7cf6b67d…` (cp-identical, pair 0.0000/0) 58388 B | `4a9c7cf6b67d…` 58388 B | BIT-IDENTICAL (`cmp` clean) |
| a1-post3 | `429d299f85ab…` 50023 B | `429d299f85ab…` 50023 B | BIT-IDENTICAL (`cmp` clean) |
| a1-post8 | differ | differ | whole pair 0.0392/0 max 53 |
| a1-post15 | `4c56f8159c76…` 49634 B | `4c56f8159c76…` 49634 B | BIT-IDENTICAL (`cmp` clean; 4th run — also T35/T36 R1) |
| a1-post25 | differ | differ | whole pair 0.0323/0 max 41 |
| menupre | differ | differ | whole pair 0.0027/0 max 13 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.165/4, 0.206/5, 0.139/3, 0.098/2 |
| scpre | differ | differ | whole pair 0.2364/5 |
| zc-post1/3/8 | differ | differ | whole pairs 0.100/1, 0.143/4, 0.131/3 |
| ccpre | differ | differ | whole pair 0.1427/4 |
| sp-post1/3/8 | differ | differ | whole pairs 0.047/1, 0.029/0, 0.001/0 |
| sppre | differ | differ | whole pair 0.0312/0 |
| pc-post1/3/8 | differ | differ | whole pairs 0.013/0, 0.004/0, 0.020/0 |
| smpre | differ | differ | whole pair 0.0065/0 |
| rc-post1/3 | differ | differ | whole pairs 0.0017/0, 0.0013/0 (near-identical; snowflake shimmer breaks bit-equality) |
| rc-post8 | differ | differ | whole pair 0.0918/0 (snowflake shimmer) |
| sepre | differ | differ | whole pair 0.0085/0 |
| sj-post1/3/8 | differ | differ | whole pairs 0.087/0, 0.034/0, 0.119/1 |
| mrpre vs T37 `mrpre` | `6cedfa418439…` | `0bdff41c4c6c…` | whole pair 0.0143/0 |
| mr-post1 (load) | `7466eb3a972d…` 66766 B | `023fa9d54af9…` 66749 B | differ; pair 1.5404/56 (18% vs 17% Loading) |
| mr-post3 (load) | `7a583908e39d…` 67123 B | `d54e4c3785cc…` 67389 B | differ; pair 2.1088/72 (98% vs 97% Loading) |
| mr-post8 | `48e97cac1997…` 54557 B | `728cb8569f3d…` 54851 B | differ; pair 4.7497/95 (both race-intro cinematic, different phase/track: Way Away Yellowcard Ocean Ave vs Deep End Utah Saints Remix) |
| mr-post15/25/40 | differ | differ | whole pairs 0.5137/11, 0.3871/5, 0.6004/15 (both pre-race panel; AI lineup differs run to run) |
| mr-stab1/2 | differ | differ | whole pairs 0.5285/11, 0.4938/9 (both pre-race panel; lineup differs) |
| pppre vs T37 `pppre` | `c8e3c1b2a9c9…` 60067 B | `33044a7b2ed3…` 59465 B | whole pair 0.5648/13; whole-vs-panel-ref 0.3086/7 PIL |
| x-post1 (countdown) | `9e6da142acbc…` 69253 B | `caf455395db9…` 70313 B | differ; pair 1.1551/43 (both countdown `2` gates — near-frozen) |
| x-post3 | differ | differ | whole pair 1.7504/33 (similar gate exit: 4TH/5TH at 00:00:02, 1%, ~39 MPH) |
| x-post8/15/25/40 | differ | differ | whole pairs 11.62/149, 9.23/135, 12.86/133, 10.54/107 (gameplay lottery) |
| npre1/2 | differ | differ | whole pairs 16.21/172, 8.54/110 (gameplay lottery) |
| d-post1..10 | differ | differ | whole pairs 9.89/139, 10.21/155, 13.49/143, 19.74/169, 14.61/132, 13.14/161, 13.16/154, 5.98/86, 9.72/138, 10.83/122 (gameplay lottery) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789983873.393 → 1789983873.928 | 535.2 ms | T+98.39→98.93 | 192→193 | `a1-now` attract (26.9623/156 remote; 26.9600/156 PIL — viewed) | `a1-poll01` TITLE (0.4337/6; 0.0453/0 — viewed) |
| A1 Start (Return) | 1789983876.668 → 1789983877.203 | 535.5 ms | T+101.67→102.20 | 195→196 | `a1-pre` ≡ `a1-poll01` (sha `4a9c7cf6b67d`, TITLE) | `a1-post3` Main Menu (16.2553/139; 16.2568/138) |
| MENU Cross (K) | 1789983915.823 → 1789983916.358 | 535.2 ms | T+140.82→141.36 | 235 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0276/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2176/106; vs-sc 0.4988/8; titleband 12.5493/164) |
| ZOE Cross (K) | 1789983955.849 → 1789983956.384 | 535.2 ms | T+180.85→181.38 | 275 | `scpre` Select Character, Zoe selected (vs-sc 0.4868/8 remote; 0.1395/3 PIL; vs-menu 10.1777/105; vs-title 12.6464/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.2058/98; vs-zc 0.5155/9; titleband 15.8601/128) |
| CONT Cross (K) | 1789983984.586 → 1789983985.121 | 535.0 ms | T+209.59→210.12 | 303→304 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4544/8 remote; 0.2185/5 PIL; vs-sc 7.2929/101; vs-title 15.8299/128 — viewed) | `sp-post1` Select Peak (vs-zc 9.4684/154; vs-sp 0.3729/6; titleband 23.1294/171) |
| PEAK Cross (K) | 1789984013.283 → 1789984013.818 | 535.2 ms | T+238.28→238.82 | 332→333 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.3930/6 remote; 0.0478/0 PIL; vs-zc 9.4616/154; vs-title 23.1279/171 — viewed) | `pc-post1` Select Mode (vs-sp 5.3585/121; vs-sm 0.3947/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789984042.536 → 1789984043.071 | 535.3 ms | T+267.54→268.07 | 361→362 | `smpre` Select Mode, Race highlighted (vs-sm 0.3905/6 remote; 0.0398/0 PIL; se-tag 14.3278/89 remote / 14.1390/88 PIL; vs-sp 5.3502/121; vs-title 26.3170/183 — viewed) | `rc-post1` Select Event (vs-sm 0.8076/11; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789984073.587 → 1789984074.124 | 537.2 ms | T+298.59→299.12 | 392→393 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6294/11 remote, 0.0257/1 PIL; vs-se 0.4065/6, 0.0363/0; vs-sm 0.8108/11; vs-sp 5.4506/121; vs-title 26.2104/183 — viewed) | `sj-post1` My Rules (vs-se 10.6628/143; vs-mr 0.4297/7; titleband 9.8238/136) |
| ENTER Cross (K) | 1789984102.205 → 1789984102.740 | 535.6 ms | T+327.20→327.74 | 421→422 | `mrpre` My Rules, Continue highlighted (vs-mr 0.4001/7 remote; 0.0804/1 PIL; vs-se 10.6337/143; vs-title 9.8393/137 — viewed) | `mr-post1` game load 18% (vs-mr 12.4891/148; vs-pp 21.0725/169; titleband 17.2673/169 — viewed) |
| XCROSS (K) | 1789984207.240 → 1789984207.777 | 536.7 ms | T+432.24→432.78 | 526→527 | `pppre` pre-race panel, X Continue (vs-pp 0.5885/8 remote; 0.3086/7 PIL — viewed) | `x-post1` countdown 2, starting gate (vs-pp 14.5112/153; titleband 19.5860/174 — viewed) |
| HOLD Left (Left) | 1789984279.544 → 1789984280.581 | 1037.3 ms | T+504.54→505.58 | 598→599 | `npre2` live race 00:01:31 2ND/6 44% (vs-pp 15.6021/144 remote; 15.5920/143 PIL; vs-title 19.0236/124 — viewed) | `d-post1` live race 00:01:37 2ND/6 46% (vs-pp 14.4634/135; titleband 26.5669/133 — viewed) |

Within-dwell receipts R1: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (1 s resolution) → Start-keydown ≤1.8 s; T33-R2-measured title
persistence 15–17 s ⇒ press inside the window with an order of magnitude
to spare. Start-keyup → MenuCross-keydown 38.6 s; MenuCross-keyup →
ZoeCross-keydown 39.5 s; ZoeCross-keyup → ContCross-keydown 28.2 s;
ContCross-keyup → PeakCross-keydown 28.2 s; PeakCross-keyup →
RaceCross-keydown 28.7 s; RaceCross-keyup → SnowJamCross-keydown 30.5 s;
SnowJamCross-keyup → EnterCross-keydown 28.1 s; EnterCross-keyup →
XCross-keydown 104.5 s (panel settling + PP gate); XCross-keyup →
Hold-keydown 71.8 s (X arrival series + LIVE gate; no dwell pressure — the
race runs input-free, T35 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / whole vs panel-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | Whole vs panel | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+96) | 56214B / `150e5f1dd56d` | 38.1316/191 | 20.4867/173 | 19.3135/170 | 20.2582/159 | 16.8193/166 | 16.8058/167 | 16.8825/167 | 18.3248/155 | 10.4327/129 | 60.9567/157 | Attract |
| a1-now (T+97, pre-Cross) | 56195B / `15bf4796c020` | 26.9600/156 | 16.9776/184 | 16.3553/156 | 17.2881/167 | 15.6649/160 | 15.4472/153 | 15.5187/155 | 15.8066/146 | 13.1607/138 | 94.5070/219 | Attract (viewed) |
| a1-poll01 (T+100, pre-Start) | 58388B / `4a9c7cf6b67d` | 0.0453/0 T | 14.1348/151 | 11.3077/152 | 12.2562/146 | 15.3709/156 | 16.1499/158 | 16.2477/160 | 9.7680/142 | 22.1504/183 | 106.6222/205 | TITLE (viewed; bit-identical to T37 R1) |
| a1-pre (T+100) | 58388B / `4a9c7cf6b67d` | 0.0453/0 | 14.1348/151 | 11.3077/152 | 12.2562/146 | 15.3709/156 | 16.1499/158 | 16.2477/160 | 9.7680/142 | 22.1504/183 | 106.6222/205 | TITLE (identical cp) |
| a1-post3 (T+105) | 50023B / `429d299f85ab` | 16.2568/138 | 0.0738/1 | 10.1330/105 | 6.9225/93 | 10.4066/170 | 10.9355/177 | 10.9500/177 | 10.0997/96 | 19.3218/178 | 26.1710/106 | Main Menu (bit-identical to T37 R1) |
| a1-post8 (T+110) | 50017B / `878f14c4eef4` | 16.2990/139 | 0.0655/1 | 10.1186/105 | 6.9220/93 | 10.3929/170 | 10.9177/177 | 10.9427/177 | 10.0923/96 | 19.3332/178 | 26.1705/106 | Main Menu |
| a1-post15 (T+118) | 49634B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | 10.1073/105 | 6.9081/93 | 10.3855/170 | 10.9184/177 | 10.9433/177 | 10.0761/96 | 19.2985/178 | 26.1710/106 | Main Menu (bit-identical to T35/T36/T37 R1) |
| a1-post25 (T+129) | 49786B / `4680fcd0480a` | 16.2622/138 | 0.0451/0 | 10.1195/105 | 6.9113/93 | 10.3911/170 | 10.9242/177 | 10.9320/177 | 10.0871/96 | 19.3018/178 | 26.1708/106 | Main Menu |
| menupre (T+139, pre-MCross) | 49670B / `0e6e1e232f10` | 16.2622/138 | 0.0276/0 | 10.1077/105 | 6.9076/93 | 10.3851/170 | 10.9180/177 | 10.9429/177 | 10.0750/96 | 19.2996/178 | 26.1385/106 | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+142) | 70231B / `5c5b539136b8` | 12.4784/163 | 10.1503/106 | 0.1503/3 | 7.1870/101 | 11.3746/158 | 11.8440/157 | 11.9148/157 | 5.6442/117 | 19.4485/172 | 26.5708/90 | Select Character, Zoe |
| mc-post3 (T+147) | 70426B / `9d484b91e75a` | 12.4811/163 | 10.1588/107 | 0.1725/4 | 7.1929/100 | 11.3937/158 | 11.8572/158 | 11.9281/157 | 5.6586/117 | 19.4678/172 | 26.5696/90 | Select Character |
| mc-post8 (T+154) | 70349B / `30905af418de` | 12.4609/163 | 10.1542/105 | 0.2450/4 | 7.2342/100 | 11.3597/158 | 11.8297/157 | 11.9032/157 | 5.6328/117 | 19.4540/172 | 26.5695/90 | Select Character |
| mc-post15 (T+164) | 70094B / `ccbdfdca3cf2` | 12.4587/163 | 10.1332/105 | 0.0933/2 | 7.1876/100 | 11.3528/158 | 11.8155/157 | 11.8856/157 | 5.6161/117 | 19.4189/172 | 26.6618/91 | Select Character |
| scpre (T+178, pre-ZCross) | 70092B / `00482d893d95` | 12.5661/163 | 10.1102/105 | 0.1395/3 | 7.2068/100 | 11.3697/159 | 11.8315/158 | 11.9014/157 | 5.6248/117 | 19.4450/172 | 26.5695/90 | Select Character, Zoe selected (viewed) |
| zc-post1 (T+182) | 51316B / `cb364d5af182` | 15.8408/128 | 6.9188/92 | 7.1769/98 | 0.2824/7 | 9.3585/154 | 10.1324/164 | 10.2435/165 | 7.0406/103 | 20.1852/164 | 15.2974/91 | Setup Character, Zoe |
| zc-post3 (T+187) | 51353B / `bf4be1df93e5` | 15.8049/128 | 6.9116/92 | 7.2420/100 | 0.2248/6 | 9.3544/153 | 10.1166/164 | 10.2292/164 | 7.0449/103 | 20.1760/164 | 15.2959/91 | Setup Character |
| zc-post8 (T+194) | 51358B / `a136396a64e4` | 15.8302/128 | 6.9314/93 | 7.1350/100 | 0.2217/5 | 9.3785/153 | 10.1273/164 | 10.2416/164 | 7.0860/104 | 20.1699/164 | 15.2956/91 | Setup Character |
| ccpre (T+206, pre-ContCross) | 51656B / `5aec5e22f352` | 15.8071/128 | 6.9106/92 | 7.2667/101 | 0.2185/5 | 9.3477/153 | 10.1084/165 | 10.2215/165 | 7.0553/103 | 20.1801/164 | 15.3084/91 | Setup Character, Zoe + Continue (viewed) |
| sp-post1 (T+211) | 65444B / `ea32dd51ab3f` | 23.1277/171 | 10.4251/170 | 11.3513/158 | 9.3893/153 | 0.0264/0 | 5.2273/121 | 5.3308/121 | 9.8335/138 | 16.5623/157 | 14.0084/89 | Select Peak, Peak 1 |
| sp-post3 (T+215) | 65500B / `53ab3335e235` | 23.1258/171 | 10.4281/170 | 11.3686/158 | 9.3910/153 | 0.0328/0 | 5.2323/121 | 5.3326/121 | 9.8552/138 | 16.5665/157 | 14.0026/89 | Select Peak |
| sp-post8 (T+223) | 65255B / `efdf6933e817` | 23.1270/171 | 10.4059/170 | 11.3503/158 | 9.3727/153 | 0.0047/0 | 5.2074/121 | 5.3100/121 | 9.8374/138 | 16.5443/157 | 14.0026/89 | Select Peak |
| sppre (T+235, pre-PeakCross) | 65433B / `7dd5179ac121` | 23.1259/171 | 10.4359/170 | 11.3781/158 | 9.3796/153 | 0.0478/0 | 5.2481/121 | 5.3478/121 | 9.8672/138 | 16.5802/158 | 14.0026/89 | Select Peak, Peak 1 highlighted (viewed) |
| pc-post1 (T+239) | 67497B / `6860a5ec19b6` | 26.3046/183 | 10.9210/178 | 11.8105/157 | 10.1050/164 | 5.1907/121 | 0.0449/0 | 0.5208/10 | 10.4711/143 | 16.4220/160 | 14.1390/88 | Select Mode, Race |
| pc-post3 (T+244) | 67400B / `8639db9bead3` | 26.3046/183 | 10.9130/178 | 11.8027/157 | 10.0995/164 | 5.1805/121 | 0.0393/0 | 0.5106/9 | 10.4621/143 | 16.4124/160 | 14.1496/88 | Select Mode |
| pc-post8 (T+252) | 67565B / `177523e04584` | 26.2927/183 | 10.9328/178 | 11.8027/157 | 10.1124/164 | 5.2001/121 | 0.0598/1 | 0.5310/11 | 10.4411/143 | 16.4307/160 | 14.1495/88 | Select Mode |
| smpre (T+264, pre-RaceCross) | 67457B / `5cce282e9fd3` | 26.3046/183 | 10.9135/178 | 11.8033/157 | 10.1010/164 | 5.1812/121 | 0.0398/0 | 0.5112/9 | 10.4634/143 | 16.4130/160 | 14.1390/88 | Select Mode, Race highlighted (viewed) |
| rc-post1 (T+269) | 69427B / `45ec8b6489ce` | 26.1964/183 | 10.9384/178 | 11.8585/157 | 10.2162/164 | 5.2823/121 | 0.5099/9 | 0.0316/0 | 10.5901/144 | 16.4268/160 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+273) | 69407B / `cf78e2d7a0fc` | 26.1980/183 | 10.9385/178 | 11.8586/157 | 10.2161/164 | 5.2824/121 | 0.5097/9 | 0.0320/0 | 10.5896/144 | 16.4272/160 | 0.0094/0 | Select Event |
| rc-post8 (T+280) | 69959B / `265359cdd914` | 26.1964/183 | 11.0118/178 | 11.9315/157 | 10.2911/164 | 5.3606/121 | 0.5887/15 | 0.0938/0 | 10.6659/144 | 16.4517/160 | 0.0094/0 | Select Event |
| sepre (T+294, pre-SnowJamCross) | 69480B / `16188e5ba2d7` | 26.1964/183 | 10.9420/178 | 11.8616/157 | 10.2193/164 | 5.2869/121 | 0.5145/10 | 0.0363/0 | 10.5925/144 | 16.4301/160 | 0.0257/1 | Select Event, Snow Jam highlighted (viewed) |
| sj-post1 (T+300) | 58893B / `c03cef15a536` | 9.7989/135 | 10.1065/96 | 5.6283/117 | 7.0700/104 | 9.8474/137 | 10.4564/143 | 10.6203/143 | 0.1129/1 | 19.5572/153 | 26.4126/92 | My Rules, Continue |
| sj-post3 (T+304) | 58562B / `57aed0ab788f` | 9.8145/135 | 10.0872/96 | 5.6152/117 | 7.0563/104 | 9.8237/137 | 10.4328/143 | 10.5961/143 | 0.0894/1 | 19.5316/152 | 26.4590/92 | My Rules |
| sj-post8 (T+312) | 59006B / `0db3d3080272` | 9.8162/135 | 10.1056/98 | 5.6532/117 | 7.0847/104 | 9.8677/137 | 10.4769/143 | 10.6408/143 | 0.1460/2 | 19.5867/153 | 26.4136/92 | My Rules |
| mrpre (T+324, pre-EnterCross) | 58441B / `6cedfa418439` | 9.8145/135 | 10.0798/96 | 5.6082/117 | 7.0487/104 | 9.8165/137 | 10.4256/143 | 10.5896/143 | 0.0804/1 | 19.5253/152 | 26.4174/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+328) | 66766B / `7466eb3a972d` | 17.2224/168 | 15.2166/157 | 14.1996/157 | 13.6588/152 | 14.7045/153 | 15.0716/152 | 15.1994/153 | 12.4607/148 | 21.0610/169 | 83.5785/220 | Loading 18% (viewed) |
| mr-post3 (T+333) | 67123B / `7a583908e39d` | 17.4329/172 | 15.1910/157 | 14.1256/157 | 13.5942/152 | 14.6318/153 | 15.0002/152 | 15.1274/153 | 12.3793/147 | 21.0228/168 | 80.1358/217 | Loading 98% (viewed) |
| mr-post8 (T+341) | 54557B / `48e97cac1997` | 28.8535/237 | 21.2456/218 | 20.5841/200 | 21.0051/191 | 20.7695/218 | 21.5588/218 | 21.4550/218 | 20.1176/197 | 19.5569/190 | 51.5938/171 | Race intro cinematic, nightclub, EA RADIO BIG / Way Away / Yellowcard / Ocean Ave (viewed) |
| mr-post15 (T+350) | 60201B / `447885476660` | 34.4893/184 | 19.3489/178 | 19.4351/172 | 20.1971/164 | 16.5548/157 | 16.4538/161 | 16.4561/160 | 19.6083/153 | 0.2218/3 | 49.4844/132 | Pre-race panel (viewed) |
| mr-post25 (T+363) | 60153B / `bc6f425ed8ac` | 34.4960/184 | 19.3173/178 | 19.4087/172 | 20.1690/164 | 16.5368/157 | 16.4253/160 | 16.4277/160 | 19.5818/153 | 0.1757/2 | 49.4844/132 | Pre-race panel |
| mr-post40 (T+381) | 59805B / `dea005a254af` | 34.4887/184 | 19.0036/177 | 19.1308/172 | 19.8708/162 | 16.3404/157 | 16.1666/159 | 16.1697/159 | 19.2931/153 | 0.5103/17 | 49.4844/132 | Pre-race panel |
| mr-stab1 (T+404) | 60147B / `51ad6e36f37d` | 34.4989/184 | 19.3145/178 | 19.4042/172 | 20.1609/164 | 16.5260/157 | 16.4238/160 | 16.4262/160 | 19.5734/153 | 0.1798/2 | 49.4844/132 | Pre-race panel |
| mr-stab2 (T+417) | 60079B / `3bae87f16d61` | 34.4892/184 | 19.2605/178 | 19.3578/172 | 20.1112/164 | 16.4920/157 | 16.3807/160 | 16.3832/160 | 19.5254/153 | 0.2393/4 | 49.4844/132 | Pre-race panel |
| pppre (T+429, pre-XCross) | 60067B / `c8e3c1b2a9c9` | 34.4926/184 | 19.1944/178 | 19.3003/172 | 20.0557/163 | 16.4551/157 | 16.3170/160 | 16.3197/159 | 19.4719/153 | 0.3086/7 | 49.4844/132 | Pre-race panel, X Continue (viewed) |
| x-post1 (T+433) | 69253B / `9e6da142acbc` | 19.5851/174 | 16.1461/164 | 14.0293/137 | 15.9397/152 | 15.6981/157 | 15.7904/157 | 15.8947/158 | 13.4186/130 | 14.4626/153 | 93.2604/175 | Countdown 2, starting gate, 00:00:00, 0 MPH (viewed) |
| x-post3 (T+437) | 67706B / `d639c92ccbe7` | 22.1636/141 | 12.9679/142 | 12.7018/134 | 12.2774/133 | 12.1240/136 | 12.0319/136 | 12.1287/136 | 11.3937/108 | 16.3109/147 | 37.7398/123 | 4TH/6, 00:00:02, 1%, 39 MPH (viewed) |
| x-post8 (T+444) | 67226B / `20b04ab4f404` | 12.3146/136 | 13.5713/129 | 12.8955/145 | 13.6799/128 | 15.9263/169 | 15.9605/162 | 16.0479/164 | 11.5433/122 | 21.5780/181 | 118.8978/200 | 6TH/6, 00:00:09, 3%, 25 MPH (viewed) |
| x-post15 (T+453) | 68542B / `2735add45747` | 13.6831/132 | 16.9482/142 | 14.1127/155 | 15.4273/144 | 18.7420/182 | 19.2955/177 | 19.3948/178 | 12.9408/130 | 25.0814/185 | 121.0701/210 | 5TH/6, 00:00:21, 9%, 55 MPH (viewed) |
| x-post25 (T+464) | 85144B / `11ab71ed502e` | 18.8215/147 | 12.3535/136 | 12.2323/138 | 11.5784/125 | 14.0664/151 | 14.8173/159 | 14.9133/159 | 11.4651/124 | 18.1430/168 | 60.0869/163 | 2ND/6, 00:00:38, 13%, 52 MPH, 50/50 Rail (viewed) |
| x-post40 (T+481) | 67573B / `c6727cde6808` | 17.9446/131 | 13.9557/148 | 11.9735/121 | 12.0061/133 | 13.2953/142 | 13.6670/142 | 13.7383/143 | 10.9155/114 | 16.9121/134 | 67.1392/148 | 1ST/6, 00:00:59, 30%, 49 MPH (viewed) |
| npre1 (T+498, pre-hold pair) | 64346B / `3e7fc6b72659` | 24.5271/146 | 16.6680/137 | 14.3789/146 | 12.9560/132 | 14.5971/144 | 14.9969/146 | 15.0791/146 | 12.5745/122 | 18.9345/156 | 41.8199/126 | 2ND/6, 00:01:25, 40%, 35 MPH, 300 pts (viewed) |
| npre2 (T+502, pre-hold) | 56884B / `a3663a94b65e` | 18.9994/124 | 12.5565/147 | 13.4814/123 | 13.2103/137 | 14.1702/149 | 13.6208/140 | 13.7296/141 | 12.3631/111 | 15.5920/143 | 50.2488/129 | 2ND/6, 00:01:31, 44%, 17 MPH, 300 pts (viewed) |
| d-post1 (T+506) | 54298B / `085dcb850bde` | 26.5387/133 | 17.1978/150 | 16.3592/144 | 16.0200/136 | 15.8266/150 | 15.8723/151 | 15.9901/151 | 15.2051/130 | 14.4641/135 | 24.3469/100 | 2ND/6, 00:01:37, 46%, 17 MPH, 300 pts (viewed) |
| d-post2 (T+509) | 58301B / `6bc7cef9c724` | 15.0594/120 | 12.8880/117 | 11.9634/133 | 11.2230/119 | 14.7606/136 | 15.0167/151 | 15.1370/151 | 10.4579/113 | 20.8875/160 | 72.3013/158 | 3RD/6, 00:01:41, 47%, 49 MPH, 300 pts (viewed) |
| d-post3 (T+512) | 58560B / `45dfb5003cb4` | 25.0032/153 | 19.4206/188 | 17.1594/161 | 17.7230/188 | 19.3560/184 | 18.9485/190 | 19.0650/191 | 16.3268/140 | 25.0627/201 | 89.6692/188 | 3RD/6, 00:01:45, 49%, 22 MPH, 300 pts (viewed) |
| d-post4 (T+515) | 65319B / `6156d711f986` | 26.3058/187 | 18.6678/191 | 18.6372/151 | 19.2517/170 | 17.4604/176 | 17.6804/181 | 17.7316/181 | 18.0823/141 | 12.4504/137 | 55.5698/144 | 3RD/6, 00:01:49, 50%, 44 MPH, 300 pts (viewed) |
| d-post5 (T+518) | 66326B / `7bf25a6db947` | 35.8457/185 | 21.3522/178 | 19.6863/181 | 18.7849/173 | 17.5809/176 | 17.0807/178 | 17.1193/178 | 18.3110/162 | 20.7918/193 | 33.4156/118 | 3RD/6, 00:01:53, 52%, 44 MPH, 300 pts (viewed) |
| d-post6 (T+520) | 60148B / `2364683b272c` | 26.5331/133 | 15.0950/182 | 14.1515/131 | 12.9614/168 | 13.9398/155 | 13.6803/162 | 13.7481/162 | 12.6857/125 | 18.1024/155 | 35.7372/114 | 5TH/6, 00:01:56, 54%, 26 MPH, 300 pts (viewed) |
| d-post7 (T+523) | 54031B / `4d1a94673d77` | 30.6019/166 | 17.7060/178 | 15.8660/141 | 15.6586/165 | 13.8628/170 | 14.2736/170 | 14.3544/170 | 15.0116/131 | 14.3338/148 | 53.2986/136 | 5TH/6, 00:02:01, 55%, 7 MPH, 300 pts, RECOVER (viewed) |
| d-post8 (T+526) | 62294B / `bcf4a1e69667` | 13.3641/135 | 13.3248/118 | 12.7319/140 | 11.4499/122 | 14.9901/152 | 15.4805/155 | 15.5719/155 | 10.9457/114 | 22.6508/162 | 79.7174/164 | 5TH/6, 00:02:05, 56%, 43 MPH, 300 pts (viewed) |
| d-post9 (T+529) | 56039B / `e7c0a79b1719` | 12.8781/166 | 15.7161/155 | 13.8893/160 | 14.9651/134 | 18.7807/180 | 19.0158/180 | 19.1396/180 | 13.4234/139 | 26.0834/203 | 107.4499/193 | 6TH/6, 00:02:09, 57%, 27 MPH, 300 pts (viewed) |
| d-post10 (T+532) | 59312B / `f65fab9c6b7b` | 15.0478/112 | 10.7589/111 | 11.9866/126 | 11.0588/117 | 12.9683/133 | 12.9482/129 | 13.0015/130 | 11.1769/117 | 15.8616/136 | 44.8317/125 | 6TH/6, 00:02:12, 58%, 37 MPH, 300 pts (viewed) |

In-script (remote) vs PIL agreement: ≤0.06 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr/vs-pp scores at scale (e.g. npre2 band 19.0236 vs
18.9994; npre2 vs-pp 15.6021 vs 15.5920; d-post1 band 26.5669 vs 26.5387);
the known ~5–11× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.4001/7 remote vs 0.0804/1 PIL ≈ 5×; sepre vs-se 0.4065/6
vs 0.0363/0 ≈ 11× — T27 title / T28 menu / T29 SC / T30 ZC / T31 SP /
T32 SM / T33 SE / T34 MR / T35 / T36 / T37 precedent); hops ≤0.07
(max Δ 0.070 on x-post25→x-post40 11.3331 vs 11.4032; dense hops ≤0.03).
Vs-panel
remote receipt reads 0.49–0.79/p99 7–17 on panel-side PIL 0.18–0.51
(≈1.5–2.8× inflation at the ~0.3 scale — T35/T36/T37 receipt
re-confirmed), so the < 2.0 whole bar holds even remotely (worst
remote 0.7871, 2.5× margin). The TAG crop gap re-confirmed at ~100–280×
(2.6271 vs 0.0094; 2.6294 vs 0.0257). Standing pattern holds:
whole-frame bars calibrated in PIL transfer to remote with single-digit
inflation near zero and ~1× at scale ≥5; text-dense crops need remote
receipts or generous bars.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1223 | 10.1300/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.0866 | 0.0971/1 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2460 | 0.2718/7 | same screen |
| post8 → post15 (mc) | 0.2074 | 0.2286/4 | same screen |
| post15 → scpre (park span) | — | 0.1411/3 | same screen |
| scpre → zc-post1 | 7.1347 | 7.1619/98 | screen change within +1 s |
| post1 → post3 (zc) | 0.2643 | 0.2868/8 | arrival settling |
| post3 → post8 (zc) | 0.2509 | 0.2721/7 | same screen |
| post8 → ccpre (park span) | — | 0.3013/8 | same screen |
| ccpre → sp-post1 | 9.3271 | 9.3641/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0437 | 0.0513/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0241 | 0.0298/0 | same screen |
| post8 → sppre (park span) | — | 0.0451/0 | same screen |
| sppre → pc-post1 | 5.2043 | 5.2290/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0167 | 0.0193/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0260 | 0.0293/0 | same screen |
| post8 → smpre (park span) | — | 0.0298/0 | same screen |
| smpre → rc-post1 | 0.4551 | 0.4807/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps in T32/T33) |
| post1 → post3 (rc) | 0.0007 | 0.0012/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0789 | 0.0817/0 | same screen (rc-post8 snowflake shimmer; still SE: se-tag 0.0094) |
| post8 → sepre (park span) | — | 0.0860/0 | same screen |
| sepre → sj-post1 | 10.5766 | 10.5998/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.0549 | 0.0592/0 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.0843 | 0.0913/1 | same screen |
| post8 → mrpre (park span) | — | 0.0826/0 | same screen |
| mrpre → mr-post1 | 12.4575 | 12.4193/148 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 1.2383 | 1.2607/49 | loading progress 18% → 98% |
| post3 → post8 (mr) | 25.3249 | 25.3346/253 | loading screen → race intro cinematic (no black frame captured this run — transition timing lottery) |
| post8 → post15 (mr) | 19.5694 | 19.5643/190 | cinematic → pre-race panel (panel arrived by +15, one sample early vs T34) |
| post15 → post25 (mr) | 0.0515 | 0.0609/2 | same screen (panel shimmer/animation) |
| post25 → post40 (mr) | 0.3411 | 0.3497/16 | same screen |
| post40 → stab1 (mr) | 0.3390 | 0.3481/16 | same screen |
| stab1 → stab2 (mr) | 0.0710 | 0.0802/3 | same screen |
| stab2 → pppre (park span) | — | 0.0927/3 | same screen |
| pppre → x-post1 | 14.3810 | 14.3650/153 | screen change within +1 s (pre-race panel → countdown/gate; decisive hop) |
| post1 → post3 (x) | 13.6861 | 13.6758/134 | countdown → live gameplay (gate → slope) |
| post3 → post8 (x) | 13.1088 | 13.1476/125 | live gameplay motion |
| post8 → post15 (x) | 11.2681 | 11.3086/135 | live gameplay motion |
| post15 → post25 (x) | 14.9953 | 15.0519/146 | live gameplay motion |
| post25 → post40 (x) | 11.3331 | 11.4032/114 | live gameplay motion |
| post40 → npre1 (span) | — | 10.4015/118 | live gameplay motion |
| npre1 → npre2 | 13.8183 | 13.8106/147 | live gameplay motion (PRE-hold pair, NO input between) |
| npre2 → d-post1 | 11.3079 | 11.3096/159 | live gameplay motion (hold lands inside this hop) |
| d1 → d2 | 15.1523 | 15.1396/155 | live gameplay motion |
| d2 → d3 | 13.3064 | 13.3090/145 | live gameplay motion |
| d3 → d4 | 22.3273 | 22.3271/213 | live gameplay motion |
| d4 → d5 | 21.8580 | 21.8390/206 | live gameplay motion |
| d5 → d6 | 12.7979 | 12.7897/147 | live gameplay motion |
| d6 → d7 | 11.3124 | 11.3320/144 | live gameplay motion |
| d7 → d8 | 15.1284 | 15.1042/152 | live gameplay motion |
| d8 → d9 | 10.0479 | 10.0737/135 | live gameplay motion |
| d9 → d10 | 14.9198 | 14.9048/153 | live gameplay motion |

### R1 arrival park (pre-race panel)

| Item | Value |
|---|---|
| Post-Enter frames | `t38r1-mr-post1.jpg` @T+328 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 18% Loading…; `mr-post3` @T+333: same screen, 98% Loading…; `mr-post8` @T+341: race intro cinematic, nightclub (`EA RADIO BIG / Way Away / Yellowcard / Ocean Ave` overlay, `Press X to skip`); `mr-post15` @T+350: pre-race panel = arrival (one sample early vs T34's +25) |
| Stability N (panel) | 6 snaps (post15/25/40 + stab1/2 + pppre) spanning T+350→T+429 (79 s) |
| Whole-frame pairwise (PIL) | 0.0198–0.3862/p99 ≤18 across all 15 pairs (panel shimmer/animation; min post25–stab1 0.0198/0, max post15–post40 0.3862/18; JPEG shas distinct) |
| Vs-panel-ref (whole) | 0.18–0.51/p99 2–17 across all 6 (all under the 2.0 gate; margins 3.9–11.4×) |
| Vs-MR (whole) | 19.29–19.61/p99 153 across all 6 (not My Rules) |
| Vs-SE (whole) | 16.17–16.46/p99 159–160 across all 6 (not Select Event) |
| Vs-SM (whole) | 16.17–16.45/p99 159–161 across all 6 (not Select Mode) |
| Vs-SP (whole) | 16.34–16.55/p99 157 across all 6 (not Select Peak) |
| Vs-ZC (whole) | 19.87–20.20/p99 162–164 across all 6 (not Setup Character) |
| Vs-SC (whole) | 19.13–19.44/p99 172 across all 6 (not Select Character) |
| Vs-menu (whole) | 19.00–19.35/p99 177–178 across all 6 (not menu) |
| Vs-title (band) | 34.49–34.50/p99 184 across all 6 (not title) |
| SE-TAG (crop) | 49.4844/132 identical across all 6 (tagline band static within run; T37's run read 48.2320/132, T36's 48.5186/132, T35's 48.5040/133, T34's 50.8209/132 — run-dependent, lineup/background phase) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Seeiah / Elise / Viggo / Kaori / Moby` (AI lineup differs run to run — T37: `Zoe/Viggo/Eddie/Allegra/Kaori/Nate`, T36: `Zoe/Moby/Nate/Luther/Griff/Marty`, T35: `Zoe/Kaori/Brodi/Viggo/Elise/Griff`, T34: `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`); `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 79 s (all 6 snaps pre-race panel) |

### R1 arrival (countdown → live gameplay; input-free until the hold)

| Snap (wall T+) | Race clock | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|
| x-post1 (T+433, +0.2 s after XCROSS keyup) | 00:00:00 | gates | 0% | 0 MPH | 0 | countdown `2` over the starting gate; riders in gates |
| x-post3 (T+437) | 00:00:02 | 4TH/6 | 1% | 39 MPH | 0 | leaving the gate, start straight, gondola |
| x-post8 (T+444) | 00:00:09 | 6TH/6 | 3% | 25 MPH | 0 | open slope, sun glare, chevron fences |
| x-post15 (T+453) | 00:00:21 | 5TH/6 | 9% | 55 MPH | 0 | wide groomed run, orange rails right |
| x-post25 (T+464) | 00:00:38 | 2ND/6 | 13% | 52 MPH | 300 + COMBO 184 | airborne over halfpipe, `50/50 Rail` banner |
| x-post40 (T+481) | 00:00:59 | 1ST/6 | 30% | 49 MPH | 300 | halfpipe area, sponsor banners |

Race-clock vs wall-clock (wall since XCROSS keyup 1789984207.777; race
clock read off HUD, HH:MM:SS):

| Snap | Wall since keyup (s) | Race clock (s) | Ratio |
|---|---|---|---|
| x-post1 | 0.2 | 0 | — (countdown) |
| x-post3 | 4.2 | 2 | 0.48 |
| x-post8 | 11.2 | 9 | 0.80 |
| x-post15 | 20.2 | 21 | 1.04 |
| x-post25 | 31.2 | 38 | 1.22 |
| x-post40 | 48.2 | 59 | 1.22 |

Stability N (X): not a static arrival — 6 snaps over 48 s, all 15
whole-frame pairs 9.68–16.98/p99 ≤185 (live gameplay motion; min
x-post3–x-post40 9.6829/124, max x-post3–x-post15 16.9835/144; JPEG shas
distinct). Vs-panel-ref 14.46–25.08 across all 6 (decisively non-panel);
vs-MR 10.92–13.42 (non-MR). No reclaim to any menu/panel (all 6 snaps
countdown/live gameplay, positions/progress/timer all advancing).

### R1 hold (ONE 1 s D-pad Left hold on live gameplay + dense series + tracking)

Hold row (control / direction / duration / T+ / delivery):

| Item | Value |
|---|---|
| Control | D-pad Left (`Left = Keyboard/Left`, `PCSX2.ini:576`) |
| Direction | Left |
| xdotool key | `Left` (`windowfocus --sync` + `keydown`/`keyup`, all exit 0) |
| Keydown wall | 1789984279.543735553 (T+504.54, uptime 598) |
| Keyup wall | 1789984280.581059351 (T+505.58, uptime 599) |
| Hold duration | 1037.3 ms (1 s `sleep` + ~37 ms xdotool overhead; T36/T37 taps: 338.6/338.2 ms — brief-authorized new input class) |
| Pre-hold pair | `npre1` @T+498 (6.5 s before keydown) + `npre2` @T+502 (2.5 s before keydown), NO input between |
| Delivery | Receipted in-script (`HOLD_LEFT_KEYDOWN/HELD/KEYUP_WALL` + uptimes in `t38r1-poll.log`); same xdotool path as the 109/109 menu holds |

Pre-hold HUD (read off the viewed `npre1`/`npre2` snaps):

| Item | npre1 | npre2 |
|---|---|---|
| Race clock | 00:01:25 | 00:01:31 |
| Position | 2ND/6 | 2ND/6 |
| Progress | 40% | 44% |
| Speed | 35 MPH | 17 MPH |
| Score | 300 pts | 300 pts |
| Scene | Riding past tree, log left | Snowy trees, rider mid-distance by log/rail |

Dense post-hold HUD series (read off viewed snaps; wall since hold
keyup 1789984280.581; race advanced = race clock minus npre2 91 s; wall
span = exposure wall minus npre2 wall 1789984277; nominal 1 s cadence =
`sleep 1` + ~2 s in-script scoring per snap):

| Snap (wall T+) | Wall + | Race clock (+adv) | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|---|
| npre1 (T+498) | −7.6 s (pre) | 00:01:25 (−6) | 2ND/6 | 40% | 35 MPH | 300 | pre-hold baseline, tree/log section |
| npre2 (T+502) | −3.6 s (pre) | 00:01:31 (+0) | 2ND/6 | 44% | 17 MPH | 300 | pre-hold baseline, forest |
| d-post1 (T+506) | +0.4 s | 00:01:37 (+6) | 2ND/6 | 46% | 17 MPH | 300 | under dark overhang, slope |
| d-post2 (T+509) | +3.4 s | 00:01:41 (+10) | 3RD/6 | 47% | 49 MPH | 300 | banked chevron turn, carving |
| d-post3 (T+512) | +6.4 s | 00:01:45 (+14) | 3RD/6 | 49% | 22 MPH | 300 | airborne off jump, sun glare |
| d-post4 (T+515) | +9.4 s | 00:01:49 (+18) | 3RD/6 | 50% | 44 MPH | 300 | camera inside dark foliage, occluded |
| d-post5 (T+518) | +12.4 s | 00:01:53 (+22) | 3RD/6 | 52% | 44 MPH | 300 | grinding log past SSX banner, chevron post |
| d-post6 (T+520) | +14.4 s | 00:01:56 (+25) | 5TH/6 | 54% | 26 MPH | 300 | open purple slope carve, red panel at right edge |
| d-post7 (T+523) | +17.4 s | 00:02:01 (+30) | 5TH/6 | 55% | 7 MPH | 300 | `RECOVER - 0` banner, against rock wall |
| d-post8 (T+526) | +20.4 s | 00:02:05 (+34) | 5TH/6 | 56% | 43 MPH | 300 | open bowl, arch right |
| d-post9 (T+529) | +23.4 s | 00:02:09 (+38) | 6TH/6 | 57% | 27 MPH | 300 | uphill crest into sun glare |
| d-post10 (T+532) | +26.4 s | 00:02:12 (+41) | 6TH/6 | 58% | 37 MPH | 300 | carving slope, chevron post left |

Race-advance vs wall-span (race-advanced-since-npre2 / wall-since-npre2):

| Snap | Race adv (s) | Wall span (s) | Ratio |
|---|---|---|---|
| d-post1 | 6 | 4 | 1.50 |
| d-post2 | 10 | 7 | 1.43 |
| d-post3 | 14 | 10 | 1.40 |
| d-post4 | 18 | 13 | 1.38 |
| d-post5 | 22 | 16 | 1.38 |
| d-post6 | 25 | 18 | 1.39 |
| d-post7 | 30 | 21 | 1.43 |
| d-post8 | 34 | 24 | 1.42 |
| d-post9 | 38 | 27 | 1.41 |
| d-post10 | 41 | 30 | 1.37 |

Rider-pixel tracking series (committed `t38-track.py`; RDC = rider
dark-centroid + validity gate; SCPS40 = T37-frozen ±40 window; SCPS120 =
wide ±120 window; whole hop = PIL per-hop from §hops):

| Snap | RDC cx/cy (px) | RDC npix (frac) + gate | SCPS40 lag (corr) into this snap | SCPS120 lag (corr) into this snap | Whole hop into this snap |
|---|---|---|---|---|---|
| npre1 | 375.7 / 253.0 | 19897 (0.142) INVALID (trees flood ROI) | — | — | — |
| npre2 | 274.2 / 168.1 | 21156 (0.151) INVALID (trees/fog bank) | +40 (−0.23) rail, no match | +120 (0.20) RAIL | 13.8106/147 |
| d-post1 | 305.0 / 166.4 | 24739 (0.176) INVALID (overhang) | −40 (−0.56) rail, no match | −120 (0.15) RAIL | 11.3096/159 |
| d-post2 | 333.8 / 286.0 | 1420 (0.010) VALID | +40 (0.39) rail, weak | −120 (0.60) RAIL | 15.1396/155 |
| d-post3 | 469.3 / 268.9 | 7869 (0.056) INVALID (over gate) | +40 (0.13) rail, no match | +120 (0.64) RAIL | 13.3090/145 |
| d-post4 | 334.1 / 229.4 | 77480 (0.552) INVALID (foliage fills frame) | −40 (−0.62) rail, no match | +120 (0.40) RAIL | 22.3271/213 |
| d-post5 | 411.5 / 327.1 | 55902 (0.398) INVALID (log/banner) | −40 (−0.10) rail, no match | −120 (0.30) RAIL | 21.8390/206 |
| d-post6 | 403.1 / 237.6 | 7603 (0.054) INVALID (over gate) | +16 (0.61) | +16 (0.61) resolved | 12.7897/147 |
| d-post7 | 448.9 / 231.4 | 47384 (0.338) INVALID (rock wall) | +40 (0.74) RAIL | +48 (0.75) resolved | 11.3320/144 |
| d-post8 | 324.8 / 185.2 | 4421 (0.032) VALID | −15 (−0.20) no match | +120 (0.24) RAIL | 15.1042/152 |
| d-post9 | 168.9 / 250.4 | 125 (0.001) INVALID (under gate — snow glare) | −5 (0.20) no match | +95 (0.52) resolved | 10.0737/135 |
| d-post10 | 295.2 / 202.1 | 8094 (0.058) INVALID (over gate) | −23 (0.36) weak | −23 (0.36) resolved | 14.9048/153 |

Noise floors on the PRE-hold pair (no input between npre1/npre2):

| Metric | npre1 → npre2 (no-input gap, 4 s wall / 6 s race) | Noise floor N |
|---|---|---|
| HUD position | 2ND → 2ND (no swap this run; T37's pre-pair swapped 2ND→3RD) | 0–1 swaps per ~4 s is ordinary |
| HUD progress/clock | 40% → 44%, +6 s race | monotonic, matches turbo |
| RDC cx | 375.7 → 274.2 BUT both npix INVALID (19897/21156) | UNMEASURED — both baseline ends fail the validity gate |
| SCPS40 | +40 @ −0.23 (RAIL, no match) | rail-class shift per gap is ordinary |
| SCPS120 | +120 @ 0.20 (RAIL) | rail-class shift per gap persists at 3× the window |
| Whole hop | 13.8106/147 | motion-class, matches surrounding hops |

Observed (non-)effect characterization (tabled, not verdicts):

| Question | Observed |
|---|---|
| Did position change? | Yes — three times, all AFTER the hold hop: 2ND→3RD at d1→d2, 3RD→5TH at d5→d6, 5TH→6TH at d8→d9; the hold hop itself (npre2→d1) holds 2ND→2ND and the pre-pair gap holds 2ND→2ND. No hold-coincident step — position degrades 2ND→6TH distributed across the 26 s tail |
| Did progress change? | Advances monotonically 40% → 58% (race-clock-driven, no jumps) |
| Did the clock change? | Advances steadily: +41 s race over +30 s wall (~1.4×, matches turbo) |
| Did speed change? | Varies 35→17→17→49→22→44→44→26→7→43→27→37 MPH (7 MPH `RECOVER` @d7) — ordinary race-speed excursions distributed across the series, none hold-coincident |
| Did score change? | Flat 300 throughout (banked pre-hold at the x-post25 rail) — no scoring events in the dense window either way |
| Did heading change (rider pixels)? | RDC gated OUT on 10/12 snaps (npix ≫ rider-scale: trees/overhang/foliage/log/rock flood the ROI; d-post9 under-gated at npix=125 in snow glare); only d-post2 (1420) and d-post8 (4421) VALID — non-adjacent, so no gated delta exists anywhere in the series. SCPS40 rails ±40 on 6/11 hops; SCPS120 STILL rails ±120 on 7/11 hops incl. the no-input pre-pair gap (+120 @ 0.20) and the hold hop (−120 @ 0.15) — background motion exceeds even the 3× window at ~3 s exposure gaps under turbo. The 4 SCPS120-resolved hops (d5→d6 +16 @ 0.61, d6→d7 +48 @ 0.75, d8→d9 +95 @ 0.52, d9→d10 −23 @ 0.36) are mid/late-tail, none hold-adjacent |
| Any HUD discontinuity at the hold? | None separable — position/speed/score show no hold-coincident step; progress/clock monotonic; no freeze, no menu, no reclaim |
| In-game registration? | Delivery receipted (focus + keydown/keyup exit 0, 1037.3 ms); in-game effect below sampling resolution — see isolation limit |
| Isolation limit | Single run, no same-seed control (AI lineup/RNG differ run to run); the hold's contribution is not separable from the race's own progression in this dense sampling — position decay, rail-class background shifts, and scene-flooded RDC occur with and without the hold |
| Recipe (one variant per attempt) | (a) no-hold control run at a matched race phase (match phase, not seed — T36 G1(c), still open); (b) exposure gaps closer to true 1 s (score post-hoc, not in-script) so SCPS stops railing and a gated RDC pair can straddle the input; tracking note: the ±120 window resolves ~1/3 of hops — a steer-discriminating window needs sub-second exposures, not wider lags |

Post-hold frame motion (whole-frame PIL): all 66 D pairs 7.70–23.06/p99
≤213 (min d-post2–d-post8 7.7038/125, max d-post4–d-post9 23.0617/211;
JPEG shas distinct). Motion throughout — no static frame, no freeze, no
menu/panel reclaim in the 34 s tail. Vs-panel-ref 12.45–26.08 across all 12
(decisively non-panel).

### R1 PP-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Departure mrpre→post1 | 12.4575 | > 5.0 | yes |
| Arrival static p25→p40 | 0.3411 | < 1.0 | yes |
| Arrival static p40→s1 | 0.3390 | < 1.0 | yes |
| Arrival static s1→s2 | 0.0710 | < 1.0 | yes → `PP-LIKE`, X-Continue Cross pressed |
| Non-MR (stab2 vs-mr) | 19.5326/153 | > 5.0 | yes |
| Vs-pp receipt (post15/25/40) | 0.5124/7, 0.4925/7, 0.7871/17 | (not a leg — receipt) | tabled (≈1.5–2.8× vs PIL 0.18–0.51; under 2.0 even remotely) |
| Vs-pp receipt (stab1/2) | 0.4958/7, 0.5245/7 | (not a leg — receipt) | tabled |
| Vs-pp receipt (pppre) | 0.5885/8 | (not a leg — receipt) | tabled (≈1.9× vs PIL 0.3086) |

### R1 LIVE gate legs (in-script proxy, remote)

| Gate leg | Value | Bar | Margin | Pass? |
|---|---|---|---|---|
| Departure pppre→x-post1 | 14.3810 | > 5.0 | 2.9× | yes |
| Non-panel (x-post40 vs-pp) | 16.9189/134 | > 5.0 | 3.4× | yes |
| Motion (x-post15→x-post25) | 14.9953 | > 5.0 | 3.0× | yes |
| Motion (x-post25→x-post40) | 11.3331 | > 5.0 | 2.3× | yes → `LIVE-LIKE`, pre-hold pair + ONE hold pressed |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Live race reproduced (HUD advancing, rider moving) | countdown `2` at +0.2 s, live gameplay from +4.2 s, race 6TH/6 at 58% by +99 s wall with one steering hold; clock/progress advance monotonically, all X+D hops 10.07–22.33 (motion) |
| Hold acted on it (pre-hold = racing with HUD read) | `npre2` viewed: 00:01:31, 2ND/6, 44%, 17 MPH, 300 pts, rider mid-forest; vs-pp 15.59 (non-panel); `npre1` viewed: 00:01:25, 2ND/6, 40% |
| Dense 10-snap series + tracking table (or exact non-separability finding with noise floor) | 12-snap HUD series above (position 2ND→6TH decay distributed post-hold, progress 40→58%, clock +41 s, speed excursions + `RECOVER` @d7 distributed, score flat 300) + RDC/SCPS40/SCPS120 per-snap table + pre-pair noise floors (RDC unmeasured/invalid both ends, SCPS40+120 rail) + isolation limit + recipe |
| Full input log + trace sha | `t38r1-poll.log` (158 lines: every score + press, walls + uptimes) + trace `1180c368…73609a3` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32/T33/T34/T35/T36/T37 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725,
first vblank L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks
397 frozen (all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not
changed`; clean tail @552.4688. Census: EE 12,315,862 (52, set-identical
to T37 R1) · IOP 20,151,004 (155, set-identical to T37 R1 — hold + dense
series + gameplay adds no new called API) · `libsd.006: sceSdGetParam` 24547
(T37: 23391); `sceSdGetAddr` 4,025,424 (T37: 4,023,600).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R1 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate → Enter Cross → PP-LIKE settled-panel gate → X Cross → LIVE-LIKE proxy gate) |
| Cross on X Continue? | YES (XCROSS @T+432.24 R1, pre-press = pre-race panel, X Continue) |
| Live race reached? | YES (countdown `2` @T+433 → live gameplay by T+437 → race at 58%, 6TH/6 @T+532, still running) |
| Hold on live gameplay? | YES (HOLD Left 1037.3 ms @T+504.54, pre-hold pair = racing 00:01:25 2ND/6 40% / 00:01:31 2ND/6 44%) |
| Separable hold response? | NOT separated — dense HUD + RDC/SCPS40/SCPS120 series tabled with pre-pair noise floors; hold-hop behavior matches no-input behavior class (no position step at the hold; rail-class shift in both) |
| Bounded variant? | none run (pre-hold = racing — variant condition not met; brief stops at R1 + recipe) |
| 1200 s cap | Not reached — R1 ≈ T+563; attempts 2–3 unexercised |
| Chain end | Live Snow Jam race (6TH/6, 58%, 00:02:12) after ONE 1 s steering hold + dense 10-snap series; race not yet finished at capture end |

## T38-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t38 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules → Cross → game load → cinematic → pre-race panel → Cross → countdown → live gameplay → pre-hold pair → 1 s D-pad Left hold → dense 10-snap series, T+~563) | 45,280,260 / 2,903,385,415 | `1180c368852527a5ce33201470fb4a656ad320a6a9b3736dbce78283973609a3` (analyze-sha on H23 = post-restart re-verify on H24 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t38r1.txt`, same size+sha (match; streamed via `wsl cat`, no C: staging — C: at 8.0 G falling to 4.6 G) + committed head/tail 2000+2000 (`t38r1-trace-head.txt` 149019 B sha `3a28d99d73e1…`, `t38r1-trace-tail.txt` 131569 B sha `2abb4d39b44e…`) |
| `emulog-pre-t38-20260921T094255Z.txt` = t37 R1 (preserved at R1 boot) | — / 2,907,114,770 | `1ade45733595b77b7e597f87a277be69b7a051e682e648610f1d6418d7da7cc1` (re-verified post-run: matches T37) | bytesize-only (T37 precedent; SSD holds T37's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 12,315,862 (52
distinct, set-identical to T37 R1) · IOP 20,151,004 (155, set-identical
to T37 R1) · vblanks 397. Committed: `t38r1-census.txt` (11699 B sha
`eb04cda35580…`), `t38r1-samples.txt` (5886 B sha `aab0b155c300…`),
`t38r1-poll.log` (158 lines, 9680 B sha `9b2202914561…`),
`t38r1-stdout.txt` (438 lines, 28660 B),
`t38r1-stderr.txt` (full `set -x` shell trace, 2556 lines, 141377 B),
`t38r1-trace-head.txt` / `t38r1-trace-tail.txt`.
Trace-head note: same 149019 B as T34/T35/T36/T37 R1 heads but sha differs
(`3a28d99d…` vs `3df9f1be…`) — timestamp-stripped content differs across
timing/wall-clock/shader-cache lines (same standing pattern).

## T38-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); one `wsl` call per ssh):

```
# reuse verification (pipe-free; one wsl call per ssh)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H23 …680 (fresh, up 2 s)
ssh bytesize 'wsl dmesg' > /tmp/t38-dmesg-pre.txt                     # 440 lines, 0 AcceptAsync (H23)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t38-eventlog-pre.txt  # head H23-create 05:41:21
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/…100909.nvm; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl grep -n Left …/inis/PCSX2.ini'                      # Left = Keyboard/Left :576
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t35-ref-panel.ppm'    # all 9 refs reproduce
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c'                         # 877G / C: 8.0G
ssh bytesize 'wsl ls …/logs/; ls -la …/logs/emulog.txt'                # 24 emulogs + live = T37 R1
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # 1ade4573… T37R1 live
# T37 ref snaps (local): 12/12 sizes reproduce T37 §chain
# freeze t38-track.py (RDC gate + SCPS120) + cross-check vs T37 numbers + determinism cmp clean
# adapt t38-auto.sh from the T37 copy (press_hold 1 s; bash -n), t38-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t38-auto.sh t38-analyze.sh t38-vcount.sh t38-cropdiff.py "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t38-… /home/brad/pcsx2-t4/; sha256sum …'  # staged shas match local
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H23
ssh bytesize 'wsl python3 …/t38-cropdiff.py …REFPP …; date -u; cat /proc/uptime; grep btime /proc/stat'  # 0.0000/0 PPM, H23 …680 up 81
# R1 (ONE ssh; exit 0; LIVE-LIKE → PRE-PAIR → 1 s HOLD → dense 10)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t38-auto.sh' > /tmp/t38r1-run-stdout.txt 2>/tmp/t38r1-run-stderr.txt  # T38_DONE, up 94→657
ssh bytesize 'wsl dmesg' > /tmp/t38-dmesg-post-r1.txt                 # IMMEDIATELY after run ssh: 474 lines, 1 AcceptAsync [25.74] pre-window (H23, full R1 coverage)
ssh bytesize 'wsl bash …/t38-analyze.sh'                              # 1180c368…, 45280260 L
ssh bytesize 'wsl bash …/t38-vcount.sh'                               # 397 frozen
ssh bytesize 'wsl wc -l …/t38-poll.log'                               # 158
ssh bytesize 'wsl ls …/t38-*.jpg'                                     # 61 JPGs
ssh bytesize 'wsl cp <30 chain jpg> /mnt/c/…'                         # (explicit list, one wsl call)
ssh bytesize 'wsl cp <31 d/mr/x jpg + poll.log + census/samples> /mnt/c/…'  # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t38-…" /tmp/t38-fetch/                         # 61 jpg + logs (r1-prefixed local)
# R1 post-hoc (local batch scorer, 4/4 bit-exact): chain panel, hops, 15 panel pairs, 15 X pairs, 66 D pairs, xrun, census set-compare, t38-track.py dense series
ssh bytesize 'wevtutil …' > /tmp/t38-eventlog-post.txt                # head H23-teardown 05:56:06; ZERO in-window entries of any kind
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H24 …776 (fresh, created by this call)
ssh bytesize 'wsl dmesg' > /tmp/t38-dmesg-post.txt                   # 448 lines, 1 AcceptAsync [16.89] (H24)
ssh bytesize 'wsl sha256sum …100909.nvm'                               # da021d2a… untouched
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # 1180c368… re-verified
ssh bytesize 'wsl ls …/logs/'                                         # 26 emulogs incl. emulog-pre-t38-20260921T094255Z.txt
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t38-20260921T094255Z.txt'  # 1ade4573… T37R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t38r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t38r1-trace-tail.txt         # 2000 lines, clean tail @552.4688
ssh bytesize 'wsl grep -c LoadStartModule …/logs/emulog.txt'           # 18
# SSD copy (COPYFILE_DISABLE=1; streamed via wsl cat — no C: staging — then shasum re-verify)
ssh bytesize 'wsl cat <trace>' > "/Volumes/Extreme SSD/ps2x-t4/emulog-t38r1.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t38r1.txt"         # 1180c368… match
ssh bytesize 'wsl df -h / /mnt/c'                                     # 874G / C: 4.6G
ssh bytesize 'wsl du -sh …/logs/'                                     # 37G
ssh bytesize 'wevtutil qe System /c:12 /rd:true /f:text' > /tmp/t38-eventlog-final.txt  # H23-teardown 05:56:06, H24-create 05:59:36
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H25 …125 (fresh; H24 tore down 06:04:31)
ssh bytesize 'wevtutil qe System /c:16 /rd:true /f:text' > /tmp/t38-eventlog-h25.txt  # H24-teardown 06:04:31, H25-create 06:05:25
# report (chunks; receipts include tail -3)
cp /tmp/t38-dmesg-*.txt /tmp/t38-eventlog-*.txt /tmp/t38r1-run-stdout.txt … local/research/T38/  # renamed per §evidence
tail -3 local/research/T38/REPORT.md
git add -f local/research/T38/<81 files by name>                      # ignored dir, forced
git commit -m "[T38] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T38-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (steering characterization) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate (departed + non-SE + static) → Cross on Continue → PP-LIKE settled-panel gate (departed + static ×3 + non-MR) → Cross on X Continue → LIVE-LIKE proxy gate (departed + non-panel + motion ×2) → ≤3 attempts) → live gameplay; then a single 1 s D-pad Left hold acts on the live race (R1: pre-hold pair 00:01:25 2ND/6 40% / 00:01:31 2ND/6 44%, dense 10-snap series to 00:02:12 6TH/6 58% with no separable hold response — position decays 2ND→6TH distributed post-hold with no hold-coincident step, RDC gated out 10/12 snaps, SCPS120 STILL rails ±120 on 7/11 hops including the no-input pre-pair gap and the hold hop; race clock ~1.4× wall under turbo). Next, ONE variant per attempt: (a) no-hold control run at a matched race phase (match phase, not seed — AI lineup/RNG differ run to run; T36 G1(c), still open); (b) exposure gaps closer to true 1 s (score post-hoc, not in-script) so SCPS stops railing and a gated RDC pair can straddle the input. Tracking note: the ±120 window resolves ~1/3 of hops — a steer-discriminating window needs sub-second exposures, not wider lags. Gate note: the hold→gameplay whole-frame hop is large (~10.07–22.33 dense) because the race never stops moving — gate on the HUD (clock/position/progress/speed/score), not the frame. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | Zero in-window flaps this session + 1 pre-session + 2 post-everything restarts (all not by me) | 0 userland kills on any VM this session; AcceptAsync exact counts 0/1/1 across the 3 committed dmesg files, all outside the run window (H23-pre 0; H23-post 1×[25.74] pre-window boot, full R1-window coverage, zero in-window; H24-post 1×[16.89] post-everything VM) + 1 pre-session VM restart between T37 and T38 (H22→H23; T37: 1 pre-session restart) + 2 post-everything VM restarts (H23→H24 09:56:06, H24→H25 10:04:31–10:05:25, both after all fetch WSL calls — proven by H24's 1.85 s uptime at the 09:59:38 identity check and H25's 1.97 s uptime at 10:05:27; only final state reads ran on H24, only an identity read on H25). ZERO Volsnap/Hyper-V entries in-window (T37 had 2× in-window Volsnap; this session's newest-30 shows zero entries of any kind inside 05:42:48–05:52:17 local). R1 completed exit 0 with T38_DONE + all 61 snaps + clean trace tail, i.e. effects-verified per the T27 §4 rule (the immediate post-run dmesg read closed T33's sequencing gap). Precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: ZERO in-window entries; boundaries bound all restarts | Newest-30 reads (pre/post): H22 teardown 05:05:54 → H23 create 05:41:21 → H23 teardown 05:56:06; inside the R1 window 05:42:48–05:52:17 (local): ZERO entries of any kind (no Volsnap, no Hyper-V-VmSwitch — precedent stands). Final newest-12: H23 teardown 05:56:06 → H24 create 05:59:36. Supplementary newest-16: H24 teardown 06:04:31 → H25 create 06:05:25. `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H24 btime |
| G4 | Hold count 109/109 (534 ms-class) + 2/2 steering taps (300 ms-class) + 1/1 steering hold (1 s) | 534 ms-class holds register 109/109 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33+T34+T35+T36+T37+T38 (T38 R1: 535.2/535.5/535.2/535.2/535.0/535.2/535.3/537.2/535.6/536.7 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect. Separately: the 300 ms-class steering tap delivered 2/2 (T36/T37) and the 1 s steering hold delivered 1/1 (1037.3 ms wall: 1 s sleep + ~37 ms xdotool overhead) — different input classes, not bisections |
| G5 | Title/menu/SC/ZC/SP/SM/SE/MR frozenness; attract differs; snowflake shimmer on SE + MR; panel animation + lineup lottery on arrival; countdown near-frozen; gameplay lottery | Title text-band frozen across showings (0.0453/0 R1); R1's 3 frames bit-identical to T37 R1's run (a1-poll01, a1-post3, a1-post15 — a1-post15 now identical across FOUR runs T35/T36/T37/T38); menu whole-frame ≤0.07/p99 ≤1 cross-run; SC cross-run 0.10–0.24/p99 1–5; ZC cross-run 0.10–0.14/p99 1–4; SP cross-run ≤0.05/p99 ≤1; SM cross-run 0.004–0.02/p99 0–1; Select Event ≤0.09/p99 0 cross-run except rc-post8 snowflake animation (rc-post1/3 near-identical 0.0017/0.0013 but NOT bit-identical — shimmer phase); My Rules ≤0.15/p99 ≤2 (snowflake drift); pre-race panel ≤0.39/p99 ≤18 within run over 79 s (panel shimmer/animation) + AI rider lineup differs run to run (T38 `Zoe/Seeiah/Elise/Viggo/Kaori/Moby` vs T37 `Zoe/Viggo/Eddie/Allegra/Kaori/Nate` vs T36 `Zoe/Moby/Nate/Luther/Griff/Marty` vs T35 `Zoe/Kaori/Brodi/Viggo/Elise/Griff` vs T34 `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`) + SE-TAG crop on panel constant within run but run-dependent (49.4844/132 vs T37's 48.2320/132 vs T36's 48.5186/132 vs T35's 48.5040/133 vs T34's 50.8209/132); load→panel transition timing is lottery-dependent (T38: 98% @+5, cinematic @+8, panel @+15 — same shape as T35/T36/T37, different cinematic track: Way Away Yellowcard Ocean Ave vs Deep End Utah Saints Remix vs Clockworks vs Buffet of Breaks) — the settled-panel gate handled all timings; countdown-`2` gate frame near-frozen cross-run (1.1551/43); gate-exit x-post3 unusually close cross-run this time (1.7504/33 — similar 4TH/5TH @00:00:02 starts); live gameplay never static (9.68–16.98 X, 7.70–23.06 D). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the hold run | `WaitVblankStart` stops after log ≤90 in T38 R1 including countdown + live gameplay + pre-pair + 1 s hold + dense series (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T37-R1-identical modulo counts). The attract/title/menu/submenu/game sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical; IOP count shifts on audio) | Like prior arrivals, hold + dense series + gameplay adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T37 R1; counts shift (`GetThreadId` 5.13M→5.06M, EE total 12.43M→12.32M; IOP 20.13M→20.15M; `sceSdGetParam` 23391→24547, `sceSdGetAddr` 4.02M→4.03M — race audio traffic). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts + C: pressure | `…/logs/` now holds ~37 GB across 26 emulogs (T17→T38 chain, all preserved); C: 4.6 G avail final (8.0 G pre-run — staging + trace growth consumed ~3.4 G; T37 final was 8.0 G). C: still at 100% — next session should clear `C:\Users\bradr\pcsx2-t4\` staging (owner's call; left in place per precedent). T38 R1 full trace SSD-copied + sha-verified (2.90 GB: `emulog-t38r1.txt`, streamed via `wsl cat` to avoid C: staging); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T38 brief cites `t37-auto.sh`, `t37-cropdiff.py`, `t37-track.py`, `t37-analyze.sh`, `t37-vcount.sh` — all 5 exist in `local/research/T37/` and were copied (not modified) for T38. T28 G9 lesson holds |
| G10 | Session wall + run durations | ~105 min active of the 4 h box (one run + report/commit); zero lease waits (no lease exists for T38). R1 wall 563 s — 203 s over the ≤6 min guidance (X-phase scoring + dense tail); R1 full dmesg coverage, zero flaps |
| G11 | X11 mount needed once, harmless | The single `/tmp/.X11-unix` tmpfs mount landed on VM-H23 pre-R1 (no restart between pre-checks and staging this session); R1 started Xvfb :99 cleanly (exit 0 + 61 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 / T33 G11 / T34 G11 / T35 G11 / T36 G11 / T37 G11 stand) |
| G12 | Remote-vs-PIL gap receipted again on the panel whole bar: ~1.5–2.8×, bar holds even remotely | R1's in-script vs-pp receipt reads 0.49–0.79/p99 7–17 on panel-side PIL 0.18–0.51 (≈1.5–2.8× inflation at the ~0.3 scale — T35's 1.3–1.6× / T36's 1.4–1.8× / T37's 1.3–1.6× receipts re-confirmed on a new run), so the < 2.0 whole bar holds even as an in-script leg (2.5× margin on the worst remote 0.7871). The TAG-crop gap re-confirmed at ~100–280× (2.6271 vs 0.0094; 2.6294 vs 0.0257). Standing pattern holds: whole-frame bars calibrated in PIL transfer to remote with single-digit inflation near zero and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars |

## Evidence files

`REPORT.md` (this file),
scripts: `t38-auto.sh`,
`t38-cropdiff.py` (T37 logic, byte-identical),
`t38-track.py` (frozen rider-pixel tracker: RDC + validity gate + SCPS40 + SCPS120),
`t38-analyze.sh`, `t38-vcount.sh` (output-name deltas only; vcount
byte-identical);
R1: `t38r1-start.jpg`, `t38r1-a1-now.jpg`, `t38r1-a1-poll01.jpg`,
`t38r1-a1-pre.jpg`, `t38r1-a1-post{3,8,15,25}.jpg`, `t38r1-menupre.jpg`,
`t38r1-mc-post{1,3,8,15}.jpg`, `t38r1-scpre.jpg`,
`t38r1-zc-post{1,3,8}.jpg`, `t38r1-ccpre.jpg`,
`t38r1-sp-post{1,3,8}.jpg`, `t38r1-sppre.jpg`,
`t38r1-pc-post{1,3,8}.jpg`, `t38r1-smpre.jpg`,
`t38r1-rc-post{1,3,8}.jpg`, `t38r1-sepre.jpg`,
`t38r1-sj-post{1,3,8}.jpg`, `t38r1-mrpre.jpg`,
`t38r1-mr-post{1,3,8,15,25,40}.jpg`, `t38r1-mr-stab{1,2}.jpg`,
`t38r1-pppre.jpg`, `t38r1-x-post{1,3,8,15,25,40}.jpg`,
`t38r1-npre{1,2}.jpg`, `t38r1-d-post{1,2,3,4,5,6,7,8,9,10}.jpg` (61 snaps),
`t38r1-census.txt`, `t38r1-samples.txt`, `t38r1-poll.log`,
`t38r1-stdout.txt`, `t38r1-stderr.txt`, `t38r1-trace-head.txt` / `t38r1-trace-tail.txt`;
flaps: `t38-dmesg-vmH23-pre.txt` (0 AcceptAsync on H23, pre-run) /
`t38-dmesg-vmH23-post.txt` (1 AcceptAsync [25.74] pre-window; full R1-window
coverage, zero in-window) / `t38-dmesg-vmH24-post.txt` (1 AcceptAsync
[16.89] on H24, fresh boot),
`t38-eventlog-pre.txt` / `t38-eventlog-post.txt` / `t38-eventlog-final.txt` /
`t38-eventlog-h25.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t38r1.txt`
(2,903,385,415 B `1180c368…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T37 R1
`…-20260921T094255Z.txt` `1ade4573…`.
