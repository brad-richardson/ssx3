# T36 report — first steering nudge in the live Snow Jam race: HUD effect (bytesize, no lease)

Brief: T36 (first steering nudge in the live Snow Jam race). Tables, no
verdicts. One boot ran on bytesize (R1: chain reproduced to live gameplay,
ONE 300 ms-class D-pad Left tap on the live race at 00:01:18, bounded +40 s
post-nudge tail mapped); laptop-side work was ssh/scp + local
reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T35/REPORT.md` (all of it: R1 reached
the pre-race panel via ENTER Cross on My Rules @T+326.78, then ONE 537.9 ms
Cross (X Continue) @T+432.05 → countdown `2` at +0.4 s → live gameplay from
+4 s → race at 84%, 4TH/6, 00:02:52, 4330 pts by +130 s with ZERO further
input (race clock ~1.3× wall under turbo); G1 proposes the first steering
input OR a finish capture — this brief takes the STEERING option). This
brief executes T35's G1 (steering half).

Experiment contract (up front): hypothesis — one bounded steering nudge
(single D-pad Left tap, 300 ms keydown) delivered to live Snow Jam gameplay
produces a measurable HUD delta (heading/position/speed/score) over a
bounded +40 s tail; observable — pre-nudge snap = live race (race clock +
position/progress HUD read off the viewed snap), the nudge row (control /
direction / duration / T+), post-nudge snap series + per-hop whole diffs +
HUD reads per hop; screen content read off viewed snaps; alternatives —
nudge shows no measurable HUD effect at the sampled cadence (deadzone,
wrong control, needs longer hold → table the exact non-behavior + recipe),
nudge provably never acted on live gameplay (pre-nudge ≠ racing → ONE
bounded variant allowed); stop — table the exact observed behavior +
recipe, one input variant per attempt, never blind multi-presses.

## T36-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T36; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T36]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; re-verified
on VM-H17 after the mid-session restart, before R1):

| Item | T4 value | T36 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Pad binding (D-pad) | — | `Up/Right/Down/Left = Keyboard/Up/Right/Down/Left` (`:573–576`) | receipted |
| Pad binding (sticks) | — | `LUp/LRight/LDown/LLeft = Keyboard/W/D/S/A` (`:589–592`), `RUp/RRight/RDown/RLeft = Keyboard/T/H/G/F` (`:593–596`) | receipted |
| Pad deadzones | — | `Deadzone = 0`, `ButtonDeadzone = 0`, `AxisScale = 1.33`, `Start = Keyboard/Return` (`:582`) | receipted |
| Nudge binding used | — | `Left = Keyboard/Left` (`PCSX2.ini:576`), xdotool key `Left` | tabled §T36-1 |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…580eb6` reproduces T35 (already staged, reused) | yes |
| T35 reference snaps present | — | all 12 arrival shas+sizes reproduce T35 §T35-2 (`x-post{1,3,8,15,25,40}` + `x-stab{1…6}`) | yes |
| Free space | — | WSL `/` 884 G avail; C: 13 G (836 G); laptop `/` 2.3 Gi avail; SSD 353 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1, on VM-H17 (the H16→H17 restart fell between pre-checks and staging per event boundaries + file mtimes; mount verified present on H17 pre-R1 — T32 G11 stands) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t36-{auto,analyze,vcount,cropdiff}.sh/.py`, `t36-{r1-census,samples}.txt` (via analyze), `t36-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t36-*.txt` (rotation chain, see trace table), `boot-t36.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t36*` + `emulog-t36r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 1 pre-session between T35 and T36 (H15→H16) + 1 mid-session between pre-checks and staging (H16→H17, 41 s gap with no VM; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified) + 2 post-everything (H17→H18 after all fetch WSL calls; H18→H19 between trace-staging and df-final; only final state reads ran on H18/H19) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H17 btime:
03:42:46→`1789976565`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 07:27:09 | VM-H15 teardown (T35's post-everything VM, after T35's session) | eventlog-pre (IDs 71/69/233/234/234) |
| 2 | 07:38:44 ([0] VM-H16) | VM-H16 started fresh ~1 s before first ssh | btime `…6323`, eventlog-pre head (IDs 292/67/291/233/232/102/291/102/291/291) |
| 3 | 07:38:45–~07:42 | Pre-run checks on VM-H16 (all ssh exit 0, zero flaps) + C:-staging (VM-independent) | `t36-dmesg-vmH16-pre.txt` (0 AcceptAsync, 440 lines, 23 `Ioctl failed` — captured at uptime ~2 s, before dxg queries) |
| 4 | 07:42:05–07:42:46 | VM-H16 teardown → VM-H17 create (mid-session restart, NOT by me; between pre-checks and WSL-staging; 41 s gap with no VM; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified; mount + ref-checks verified on H17) | btime `…6565`, eventlog-post (IDs 71/69/233/234/234 teardown, 292/67/291/233/232/102/291/102/291/291 create), `t36-dmesg-vmH17-pre.txt` (1 AcceptAsync [21.79] pre-window, 473 lines) |
| 5 | 07:43:42–07:53:13 ([57]→[628] H17) | R1 single-shot exit 0, `T36_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart in-window) | exit 0, 56 snaps, trace sha |
| 6 | 07:53:13–~07:57 | R1 analyze (exit 0) + all R1 fetches + ref fetch (exit 0) on VM-H17 | `t36-census.txt`, 56 JPGs + logs, 9 ref PPMs |
| 7 | 07:57:43 | VM-H17 teardown → (post-everything restart #1, NOT by me; no WSL call ran 07:57:43–08:08:13 — next call shows uptime 2.15 s) | eventlog-post head (IDs 71/69/233/234/234 teardown) |
| 8 | 08:08:13–08:11:18 (VM-H18) | VM-H18 fresh: identity + dmesg + NVM/trace/logs/preserved-sha re-verifies + trace head/tail slices + SSD staging (exit 0) | `t36-dmesg-vmH18-post.txt` (1 AcceptAsync [17.19], 448 lines, boot coverage) |
| 9 | 08:11:18–08:11:31 | VM-H18 teardown → VM-H19 create (post-everything restart #2, NOT by me; 13 s gap; only df-final ran on H19) | eventlog-final (ID 71 teardown 04:11:18, create burst 04:11:31) |
| 10 | event log | Newest-30 reads (pre/post): head moves H16-create 03:38:44 → H17-teardown 03:57:43; boundaries H15-teardown 03:27:09, H16-create 03:38:44, H16-teardown 03:42:05, H17-create 03:42:46, H17-teardown 03:57:43; in-window (03:43:42–03:53:13 local) entries: NONE of any kind (zero Volsnap, zero Hyper-V-VmSwitch — userland kills leave no Windows trace, T17/T21/T23/T25/T27/T28/T29/T30/T31/T32/T33/T34/T35 precedent stands) | `t36-eventlog-{pre,post,final}.txt` |
| 11 | dmesg noise | `Ioctl failed` lines 23 pre (H16, uptime-2 s capture) / 46 pre (H17) / 46 post-R1 (H17) / 23 post (H18, fresh boot) — steady boot/GPU-query noise, not kills; kill-pattern grep (`killed process\|out of memory\|panic\|oops\|segfault`) matches only the 2 `panic=-1` cmdline echoes per file | dmesg files |

AcceptAsync exact counts with uptime-stamp positions relative to the R1
window (T_BOOT uptime 57 → end 628, all on VM-H17):

| Committed file | Lines | AcceptAsync count | Uptime stamps | Position vs run window |
|---|---|---|---|---|
| `t36-dmesg-vmH16-pre.txt` | 440 | 0 | — | different VM (pre-restart); outside |
| `t36-dmesg-vmH17-pre.txt` | 473 | 1 | [21.789198] | before window (21 < 57); outside |
| `t36-dmesg-vmH17-post.txt` | 474 | 1 | [21.789198] | same single pre-window line; ZERO in-window |
| `t36-dmesg-vmH18-post.txt` | 448 | 1 | [17.192881] | different VM (post-everything, no run); outside |

## T36-1. Nudge selection + LIVE calibration (thresholds, match scores)

Tool: `t36-cropdiff.py` (copy of T35's, byte-identical; `cmp` clean;
`t36-vcount.sh` byte-identical to T35's; `t36-analyze.sh` differs only in
output names). Title text-band method unchanged (thresholds frozen: TITLE
band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu
mean < 2.0; NONMENU / NONSC / NONZC / NONSP / NONSE / NONMR whole-vs-ref
mean > 5.0; DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). Panel
reference reused (`t35-ref-panel.ppm`, already staged, sha re-verified).
No new reference (no new static screen to gate on). Remote PPM-mode
self-checks pre-run: panel ref 0.0000/0, MR ref 0.0000/0.

Nudge selection (tabled BEFORE the run, per brief — pick ONE):

| Item | Value |
|---|---|
| Control | D-pad Left (NOT analog) |
| Binding | `Left = Keyboard/Left` (`PCSX2.ini:576`) |
| xdotool key | `Left` |
| Duration | Single 300 ms tap (`keydown`, `sleep 0.3`, `keyup`; NOT a 534 ms-class menu hold — different input class, brief-authorized "single D-pad tap") |
| Direction | Left |
| Why D-pad over analog | Single digital binding, zero deadzone ambiguity (`ButtonDeadzone = 0`; D-pad is digital anyway); analog-via-keyboard (`LLeft = Keyboard/A`) would use the same key-tap mechanism with `AxisScale = 1.33` semantics — no advantage, more interpretation surface |
| When | After the X arrival series, on the LIVE-LIKE proxy gate (≈T+500, deep in live gameplay per T35's race shape) |

LIVE calibration (T35 R1 receipts; no new calibration run — the gate is a
proxy, the criterion is HUD-read):

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

Script deltas vs `t35-auto.sh` (committed originals untouched; `t36-auto.sh`
is the adapted copy):

| Area | T35 script | T36 script |
|---|---|---|
| Chain | park phase + full menu→MR chain + PP gate + XCROSS + x series to +40 + 6×10 s stab | identical through the x-post40 hop scoring; 6×10 s stab REPLACED by the LIVE-gate + nudge phase |
| LIVE gate | — | LIVE-LIKE proxy gate (departed + non-panel + motion ×2; `NO-LIVE-PARK` plog, still clean shutdown + `T36_DONE`) + `is_nonpp()` + `NONPP_MEAN_MIN=5.0` |
| T36 nudge | — | `npre` snap (vs-pp + titleband) + ONE `press_nudge Left` (300 ms) + post-nudge series +1/+3/+8/+15/+25/+40 (each titleband + vs-pp) + 6 per-hop whole diffs |
| Self-tests | SELF_TEST + … + SELF_MR + SELF_PP | unchanged (all 11 re-run) |
| No-park paths | explicit `NO-PARK` + … + `NO-PP-PARK` | + explicit `NO-LIVE-PARK` plog, still clean shutdown + `T36_DONE` (trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
port of `t36-cropdiff.py` (`/tmp/t36-fastdiff.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical, mode
tag PIL in both) against the committed tool on 4 diverse pairs (whole
panel-panel 0.3757/17, whole gameplay-motion 7.9696/118, text-band
21.4018/153, SE-TAG crop 0.0000/0). Any score reproduces with the committed
`t36-cropdiff.py`, slower. The 9 ref PPMs were fetched to `/tmp/t36-refs/`
for post-hoc scoring (all 9 shas re-verified, match §T36-0).

## T36-2. R1 — race reproduced, ONE steering nudge on live gameplay

Run: `t36-auto.sh`, ONE fresh boot, T_BOOT wall 1789976622 (uptime 57,
VM-H17), 07:43:42–07:53:13 UTC (uptime 57→628 = 571 s; 211 s over the
≤6 min guidance — the X phase + nudge tail; full dmesg coverage, zero
flaps in-window), WID 2097159 (same as T31 R1 / T32 R1 / T33 R1 / T33 R2 /
T34 R1 / T35 R1), exit 0, `T36_DONE`, clean SIGTERM shutdown.
SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC
0.0000/0, SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM 0.0000/0, SELF_SE
0.0000/0, SELF_SETAG 0.0000/0, SELF_MR 0.0000/0, SELF_PP 0.0000/0.
Attempt 1 of ≤3 consumed; attempts 2–3 not needed (chain advanced to the
nudge, arrival mapped). No bounded variant run (pre-nudge = racing —
variant condition not met, brief stops here).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+101, score 0.4311/5 remote / 0.0474/1 PIL (T35 R1: 0.4331/6 / 0.0465/1 — same detector reading, frame differs by 0.0348/0) | Cross 535.1 ms @T+98.97 (attract-skip) + Start 535.0 ms @T+102.25 (on title, ≤1.3 s after exposure) | Main Menu by +4 s; menu-like gate (non-title + whole-static 0.0389/0.0201) + post25-vs-menu 0.3033/5 → park for menu Cross |
| A2–A3 | not run (chain advanced) | — | — |

### R1 cross-run frame identities (T36 R1 vs T35 R1, full sha256)

| Frame | T36 R1 sha | T35 R1 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `6e0c68accf47…` (cp-identical, pair 0.0000/0) 58293 B | `769c641d640f…` 58339 B | differ; pair 0.0348/0 max 51 (title timing lottery, nearby phase) |
| a1-post3/8/25 | differ | differ | whole pairs 0.051/1, 0.048/0, 0.021/0 |
| a1-post15 | `4c56f8159c76…` 49634 B | `4c56f8159c76…` 49634 B | BIT-IDENTICAL (`cmp` clean) |
| menupre | differ | differ | whole pair 0.0021/0 max 13 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.158/3, 0.173/4, 0.158/4, 0.095/2 |
| scpre | differ | differ | whole pair 0.2242/5 |
| zc-post1/3/8 | differ | differ | whole pairs 0.124/3, 0.096/2, 0.095/2 |
| ccpre | differ | differ | whole pair 0.0866/1 |
| sp-post1/3/8 | differ | differ | whole pairs 0.033/0, 0.068/1, 0.001/0 |
| sppre | differ | differ | whole pair 0.0767/0 |
| pc-post1/3/8 | differ | differ | whole pairs 0.046/0, 0.007/0, 0.022/0 |
| smpre | differ | differ | whole pair 0.0065/0 |
| rc-post1 | `d86c39d523f9…` 69432 B | `d86c39d523f9…` 69432 B | BIT-IDENTICAL (`cmp` clean; 3rd run — also T34 R1) |
| rc-post3 | `f7ad3226d405…` 69412 B | `f7ad3226d405…` 69412 B | BIT-IDENTICAL (`cmp` clean) |
| rc-post8 | differ | differ | whole pair 0.0312/0 (snowflake shimmer) |
| sepre | differ | differ | whole pair 0.0058/0 |
| sj-post1/3/8 | differ | differ | whole pairs 0.031/0, 0.012/0, 0.073/0 |
| mrpre vs T35 `mrpre` | `4c29825b3816…` | `c23d59754221…` | whole pair 0.0085/0 |
| mr-post1 (load) | `de707d1d5ed5…` 66795 B | `de707d1d5ed5…` 66795 B | BIT-IDENTICAL (`cmp` clean; both Loading 18%) |
| mr-post3 (load) | `04d24cebdc71…` 67139 B | `12cc2598c966…` 67087 B | differ; pair 1.6633/66 (both Loading 97%; snowflake/percentage shimmer) |
| mr-post8 | `6e0a12fc113d…` 53961 B | `c394b40e0064…` 53943 B | differ; pair 7.2476/129 (both race-intro cinematic, different phase/track: Clockworks vs Buffet of Breaks) |
| mr-post15/25/40 | differ | differ | whole pairs 0.3855/6, 0.3202/6, 0.5182/11 (both pre-race panel; AI lineup differs run to run) |
| mr-stab1/2 | differ | differ | whole pairs 0.4223/7, 0.3917/6 (both pre-race panel; lineup differs) |
| pppre vs T35 `pppre` | `294e4249044e…` 59704 B | `108024fdc48f…` 59445 B | whole-vs-panel-ref 0.4845/7 PIL (under the 2.0 gate; lineup differs) |
| x-post1 (countdown) | `c5e4a07a7e94…` 70304 B | `c6f732d3dfe4…` 69186 B | differ; pair 1.9403/57 (both countdown `2` gates — near-frozen) |
| x-post3/8/15/25/40 | differ | differ | whole pairs 6.95/109, 5.19/87, 8.83/126, 12.70/119, 14.00/133 (gameplay lottery) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789976720.975 → 1789976721.510 | 535.1 ms | T+98.97→99.51 | 155 | `a1-now` attract (23.4864/155 remote; 23.4852/155 PIL) | `a1-poll01` TITLE (0.4311/5; 0.0474/1) |
| A1 Start (Return) | 1789976724.254 → 1789976724.789 | 535.0 ms | T+102.25→102.79 | 158→159 | `a1-pre` ≡ `a1-poll01` (sha `6e0c68accf47`, TITLE) | `a1-post3` Main Menu (16.2542/139; 16.2552/138) |
| MENU Cross (K) | 1789976763.422 → 1789976763.958 | 536.3 ms | T+141.42→141.96 | 197→198 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0276/0 PIL; vs-title 16.2610/139) | `mc-post1` Select Character (vs-menu 10.2190/106; vs-sc 0.4998/8; titleband 12.5486/164) |
| ZOE Cross (K) | 1789976803.403 → 1789976803.940 | 536.7 ms | T+181.40→181.94 | 237→238 | `scpre` Select Character, Zoe selected (vs-sc 0.5093/8 remote; 0.1626/3 PIL; vs-menu 10.1810/105; vs-title 12.6287/164) | `zc-post1` Setup Character (vs-sc 7.2195/99; vs-zc 0.5174/9; titleband 15.8868/128) |
| CONT Cross (K) | 1789976832.102 → 1789976832.637 | 535.0 ms | T+210.10→210.64 | 266 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4496/8 remote; 0.2150/6 PIL; vs-sc 7.2853/100; vs-title 15.8330/128) | `sp-post1` Select Peak (vs-zc 9.4676/154; vs-sp 0.3717/6; titleband 23.1281/171) |
| PEAK Cross (K) | 1789976860.767 → 1789976861.304 | 536.6 ms | T+238.77→239.30 | 295 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.4120/6 remote; 0.0684/0 PIL; vs-zc 9.5048/154; vs-title 23.1279/171) | `pc-post1` Select Mode (vs-sp 5.3616/121; vs-sm 0.4022/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789976890.021 → 1789976890.558 | 537.1 ms | T+268.02→268.56 | 324 | `smpre` Select Mode, Race highlighted (vs-sm 0.3921/6 remote; 0.0414/0 PIL; se-tag 14.3278/89 remote / 14.1390/88 PIL; vs-sp 5.3518/121; vs-title 26.3170/183) | `rc-post1` Select Event (vs-sm 0.8074/11; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789976921.112 → 1789976921.648 | 535.9 ms | T+299.11→299.65 | 355 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6271/11 remote, 0.0094/0 PIL; vs-se 0.4072/6, 0.0371/0; vs-sm 0.8115/11; vs-sp 5.4513/121; vs-title 26.2104/183) | `sj-post1` My Rules (vs-se 10.6374/143; vs-mr 0.4159/7; titleband 9.8531/137) |
| ENTER Cross (K) | 1789976949.772 → 1789976950.308 | 536.0 ms | T+327.77→328.31 | 384 | `mrpre` My Rules, Continue highlighted (vs-mr 0.3999/7 remote; 0.0795/0 PIL; vs-se 10.6337/143; vs-title 9.8393/137 — viewed) | `mr-post1` game load 18% (vs-mr 12.4898/148; vs-pp 21.0617/169; titleband 17.2808/168 — viewed) |
| XCROSS (K) | 1789977054.847 → 1789977055.385 | 538.1 ms | T+432.85→433.39 | 489 | `pppre` pre-race panel, X Continue (vs-pp 0.7376/10 remote; 0.4845/7 PIL; vs-mr 19.5233/153; vs-title 34.5011/184 — viewed) | `x-post1` countdown 2, starting gate (vs-pp 14.5648/153; titleband 18.7168/151 — viewed) |
| NUDGE Left (Left) | 1789977122.821 → 1789977123.160 | 338.6 ms | T+500.82→501.16 | 557 | `npre` live race 00:01:18 6TH/6 30% (vs-pp 17.3794/134 remote; 17.3764/135 PIL; vs-title 19.0180/111 — viewed) | `n-post1` live race 00:01:23 6TH/6 31% (vs-pp 15.2364/154; titleband 34.4177/167 — viewed) |

Within-dwell receipts R1: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (1 s resolution) → Start-keydown ≤1.3 s; T33-R2-measured title
persistence 15–17 s ⇒ press inside the window with an order of magnitude
to spare. Start-keyup → MenuCross-keydown 38.6 s; MenuCross-keyup →
ZoeCross-keydown 39.4 s; ZoeCross-keyup → ContCross-keydown 28.2 s;
ContCross-keyup → PeakCross-keydown 28.1 s; PeakCross-keyup →
RaceCross-keydown 28.7 s; RaceCross-keyup → SnowJamCross-keydown 30.6 s;
SnowJamCross-keyup → EnterCross-keydown 28.1 s; EnterCross-keyup →
XCross-keydown 104.5 s (panel settling + PP gate); XCross-keyup →
Nudge-keydown 67.4 s (X arrival series + LIVE gate; no dwell pressure — the
race runs input-free, T35 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / whole vs panel-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | Whole vs panel | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+97) | 57021B / `dbec7685fcbb` | 35.2270/192 | 20.0531/172 | 18.1869/160 | 19.4621/158 | 15.7003/164 | 15.8784/166 | 15.9808/166 | 16.9850/141 | 10.7476/137 | 65.2228/168 | Attract |
| a1-now (T+98, pre-Cross) | 57858B / `94fe8342e73a` | 23.4852/155 | 16.3909/182 | 15.8632/149 | 16.8146/166 | 16.2686/156 | 16.1358/154 | 16.1902/156 | 15.3422/144 | 14.0133/142 | 96.1075/223 | Attract |
| a1-poll01 (T+101, pre-Start) | 58293B / `6e0c68accf47` | 0.0474/1 T | 14.1351/151 | 11.3058/152 | 12.2566/146 | 15.3696/156 | 16.1498/158 | 16.2476/160 | 9.7671/143 | 22.1512/183 | 106.6165/205 | TITLE |
| a1-pre (T+101) | 58293B / `6e0c68accf47` | 0.0474/1 | 14.1351/151 | 11.3058/152 | 12.2566/146 | 15.3696/156 | 16.1498/158 | 16.2476/160 | 9.7671/143 | 22.1512/183 | 106.6165/205 | TITLE (identical cp) |
| a1-post3 (T+105) | 50085B / `f1287a7be3a6` | 16.2552/138 | 0.0786/1 | 10.1367/105 | 6.9271/93 | 10.4114/170 | 10.9394/177 | 10.9548/177 | 10.1028/96 | 19.3220/178 | 26.1710/106 | Main Menu |
| a1-post8 (T+111) | 50006B / `88ae592f89f5` | 16.2984/139 | 0.0678/1 | 10.1178/105 | 6.9227/93 | 10.3936/170 | 10.9196/177 | 10.9446/177 | 10.0933/96 | 19.3354/178 | 26.1728/106 | Main Menu |
| a1-post15 (T+119) | 49634B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | 10.1073/105 | 6.9081/93 | 10.3855/170 | 10.9184/177 | 10.9433/177 | 10.0761/96 | 19.2985/178 | 26.1710/106 | Main Menu |
| a1-post25 (T+129) | 49804B / `410ae0ac2c97` | 16.2622/138 | 0.0478/0 | 10.1228/105 | 6.9157/93 | 10.3954/170 | 10.9285/177 | 10.9424/177 | 10.0905/96 | 19.3012/178 | 26.1676/106 | Main Menu |
| menupre (T+139, pre-MCross) | 49670B / `0e6e1e232f10` | 16.2622/138 | 0.0276/0 | 10.1077/105 | 6.9076/93 | 10.3851/170 | 10.9180/177 | 10.9429/177 | 10.0750/96 | 19.2996/178 | 26.1385/106 | Main Menu, Single Event highlighted |
| mc-post1 (T+142) | 70171B / `96d61656da50` | 12.4766/163 | 10.1513/106 | 0.1513/3 | 7.1876/101 | 11.3765/158 | 11.8450/157 | 11.9159/157 | 5.6452/117 | 19.4495/172 | 26.5677/90 | Select Character, Zoe |
| mc-post3 (T+147) | 70450B / `1187ca5095c9` | 12.4821/163 | 10.1585/107 | 0.1566/3 | 7.2092/100 | 11.3974/158 | 11.8619/157 | 11.9322/157 | 5.6605/117 | 19.4683/172 | 26.5696/90 | Select Character |
| mc-post8 (T+155) | 70254B / `102abd4892dc` | 12.4588/163 | 10.1556/105 | 0.2360/4 | 7.2304/100 | 11.3621/158 | 11.8337/157 | 11.9050/157 | 5.6319/117 | 19.4544/172 | 26.5695/90 | Select Character |
| mc-post15 (T+164) | 70110B / `9b2e0fda1f91` | 12.4587/163 | 10.1333/105 | 0.0859/2 | 7.1941/100 | 11.3523/158 | 11.8145/157 | 11.8843/157 | 5.6150/117 | 19.4189/172 | 26.6618/91 | Select Character |
| scpre (T+178, pre-ZCross) | 70112B / `e98437c8ccab` | 12.5514/163 | 10.1135/105 | 0.1626/3 | 7.2008/100 | 11.3677/159 | 11.8314/158 | 11.9015/157 | 5.6278/117 | 19.4435/172 | 26.5695/90 | Select Character, Zoe selected |
| zc-post1 (T+182) | 51390B / `b9fb15c9295d` | 15.8649/128 | 6.9187/92 | 7.1905/99 | 0.2846/7 | 9.3596/154 | 10.1313/165 | 10.2426/165 | 7.0456/103 | 20.1872/164 | 15.2973/91 | Setup Character, Zoe |
| zc-post3 (T+187) | 51514B / `45e62923f6e0` | 15.9031/130 | 6.9061/92 | 7.2657/100 | 0.2364/6 | 9.3527/153 | 10.1113/164 | 10.2243/164 | 7.0531/103 | 20.1790/165 | 15.2979/91 | Setup Character |
| zc-post8 (T+195) | 51413B / `7ec4ef2d4975` | 15.8302/128 | 6.9304/93 | 7.0859/100 | 0.2065/4 | 9.3772/153 | 10.1294/164 | 10.2388/164 | 7.0831/104 | 20.1672/164 | 15.2962/91 | Setup Character |
| ccpre (T+207, pre-ContCross) | 51608B / `611263c0802e` | 15.8119/128 | 6.9122/93 | 7.2610/100 | 0.2150/6 | 9.3512/153 | 10.1160/165 | 10.2284/165 | 7.0482/103 | 20.1836/164 | 15.3312/91 | Setup Character, Zoe + Continue |
| sp-post1 (T+211) | 65310B / `33639ed8d6a6` | 23.1261/171 | 10.4238/170 | 11.3503/158 | 9.3877/153 | 0.0253/0 | 5.2274/121 | 5.3303/121 | 9.8235/138 | 16.5609/157 | 14.0042/89 | Select Peak, Peak 1 |
| sp-post3 (T+216) | 65496B / `5e2165a0f24c` | 23.1259/171 | 10.4333/170 | 11.3677/158 | 9.3922/153 | 0.0418/0 | 5.2411/121 | 5.3434/121 | 9.8581/138 | 16.5750/158 | 14.0026/89 | Select Peak |
| sp-post8 (T+223) | 65229B / `79e06cca6a9a` | 23.1271/171 | 10.4061/170 | 11.3502/158 | 9.3727/153 | 0.0046/0 | 5.2069/121 | 5.3099/121 | 9.8373/138 | 16.5443/157 | 14.0026/89 | Select Peak |
| sppre (T+236, pre-PeakCross) | 65653B / `7ff7b771b8de` | 23.1259/171 | 10.4633/170 | 11.4050/158 | 9.4254/153 | 0.0684/0 | 5.2680/121 | 5.3368/121 | 9.8936/138 | 16.5805/157 | 14.0026/89 | Select Peak, Peak 1 highlighted |
| pc-post1 (T+240) | 67466B / `525762167b7a` | 26.3046/183 | 10.9231/178 | 11.8105/157 | 10.0963/164 | 5.1944/121 | 0.0539/0 | 0.5202/10 | 10.4712/143 | 16.4248/160 | 14.1394/88 | Select Mode, Race |
| pc-post3 (T+244) | 67420B / `16d7feb76a26` | 26.3046/183 | 10.9152/178 | 11.8049/157 | 10.1020/164 | 5.1827/121 | 0.0413/0 | 0.5125/9 | 10.4642/143 | 16.4142/160 | 14.1347/88 | Select Mode |
| pc-post8 (T+252) | 67651B / `2df4968f6b8c` | 26.3168/183 | 10.9375/178 | 11.8025/157 | 10.1217/164 | 5.2070/121 | 0.0646/1 | 0.5375/12 | 10.4490/143 | 16.4370/160 | 14.1701/88 | Select Mode |
| smpre (T+264, pre-RaceCross) | 67467B / `41b6c1dc0bf6` | 26.3046/183 | 10.9154/178 | 11.8052/157 | 10.1034/164 | 5.1828/121 | 0.0414/0 | 0.5129/9 | 10.4662/143 | 16.4148/160 | 14.1390/88 | Select Mode, Race highlighted |
| rc-post1 (T+269) | 69432B / `d86c39d523f9` | 26.1964/183 | 10.9382/178 | 11.8584/157 | 10.2158/164 | 5.2819/121 | 0.5095/9 | 0.0312/0 | 10.5897/144 | 16.4267/160 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+273) | 69412B / `f7ad3226d405` | 26.2007/183 | 10.9401/178 | 11.8582/157 | 10.2161/164 | 5.2832/121 | 0.5118/9 | 0.0336/0 | 10.5896/144 | 16.4272/160 | 0.0094/0 | Select Event |
| rc-post8 (T+281) | 69809B / `20f3d5d484f9` | 26.1964/183 | 10.9915/178 | 11.9137/157 | 10.2708/164 | 5.3399/121 | 0.5674/13 | 0.0906/0 | 10.6438/144 | 16.4386/161 | 0.0094/0 | Select Event |
| sepre (T+294, pre-SnowJamCross) | 69540B / `66d05dd2a45f` | 26.1964/183 | 10.9427/178 | 11.8629/157 | 10.2208/164 | 5.2878/121 | 0.5154/10 | 0.0371/0 | 10.5945/144 | 16.4312/160 | 0.0094/0 | Select Event, Snow Jam highlighted |
| sj-post1 (T+300) | 58611B / `413a8d019b9c` | 9.8274/135 | 10.0835/96 | 5.6119/117 | 7.0548/104 | 9.8235/137 | 10.4295/143 | 10.5933/143 | 0.1000/1 | 19.5422/153 | 26.4126/92 | My Rules, Continue |
| sj-post3 (T+305) | 58485B / `1cdb0d453ffd` | 9.8145/135 | 10.0838/96 | 5.6126/117 | 7.0539/104 | 9.8208/137 | 10.4299/143 | 10.5939/143 | 0.0850/1 | 19.5286/152 | 26.4925/92 | My Rules |
| sj-post8 (T+312) | 58922B / `19b3bd47a18f` | 9.8559/136 | 10.1124/99 | 5.6482/117 | 7.0773/104 | 9.8621/137 | 10.4713/143 | 10.6352/143 | 0.1429/2 | 19.5818/154 | 26.4123/92 | My Rules |
| mrpre (T+325, pre-EnterCross) | 58477B / `4c29825b3816` | 9.8145/135 | 10.0797/96 | 5.6086/117 | 7.0491/104 | 9.8165/137 | 10.4256/143 | 10.5896/143 | 0.0795/0 | 19.5251/152 | 26.4159/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+329) | 66795B / `de707d1d5ed5` | 17.2333/167 | 15.2283/157 | 14.2067/157 | 13.6711/152 | 14.7146/153 | 15.0815/152 | 15.2094/153 | 12.4617/148 | 21.0504/169 | 83.2100/222 | Loading 18% (viewed) |
| mr-post3 (T+333) | 67139B / `04d24cebdc71` | 17.5926/169 | 15.2772/158 | 14.1745/157 | 13.6444/153 | 14.6957/153 | 15.0625/153 | 15.1897/154 | 12.4507/149 | 21.0188/169 | 84.9108/225 | Loading 97% (viewed) |
| mr-post8 (T+341) | 53961B / `6e0a12fc113d` | 32.2570/237 | 22.6211/218 | 21.8092/210 | 21.7423/189 | 20.3750/218 | 21.1256/218 | 21.0877/218 | 20.8457/197 | 17.9013/190 | 48.1891/145 | Race intro cinematic, gate interior, EA RADIO BIG / Clockworks / Autopilot Off / Make a Sound (viewed) |
| mr-post15 (T+351) | 59451B / `85a21471a0ff` | 34.4967/184 | 19.0673/177 | 19.1893/172 | 19.9328/162 | 16.3893/157 | 16.2211/159 | 16.2243/159 | 19.3447/154 | 0.6768/17 | 48.5186/132 | Pre-race panel (viewed) |
| mr-post25 (T+364) | 59850B / `8c9e988a5134` | 34.5008/184 | 19.4145/179 | 19.4963/172 | 20.2654/164 | 16.6136/157 | 16.5081/161 | 16.5105/160 | 19.6683/154 | 0.4389/7 | 48.5186/132 | Pre-race panel |
| mr-post40 (T+382) | 59694B / `be671dbeeba7` | 34.4960/184 | 19.2557/178 | 19.3538/172 | 20.1070/164 | 16.4928/157 | 16.3763/160 | 16.3791/160 | 19.5128/154 | 0.4829/7 | 48.5186/132 | Pre-race panel |
| mr-stab1 (T+404) | 59863B / `ee63143a57a7` | 34.4895/184 | 19.4043/178 | 19.4858/172 | 20.2519/164 | 16.5999/157 | 16.5044/161 | 16.5069/160 | 19.6539/154 | 0.4298/6 | 48.5186/132 | Pre-race panel |
| mr-stab2 (T+417) | 59770B / `d100bffedfa2` | 34.5007/184 | 19.3568/178 | 19.4453/172 | 20.2108/164 | 16.5737/157 | 16.4570/160 | 16.4596/160 | 19.6146/154 | 0.3765/6 | 48.5186/132 | Pre-race panel |
| pppre (T+429, pre-XCross) | 59704B / `294e4249044e` | 34.4959/184 | 19.2535/178 | 19.3527/172 | 20.1102/164 | 16.4987/157 | 16.3690/160 | 16.3718/159 | 19.5166/154 | 0.4845/7 | 48.5186/132 | Pre-race panel, X Continue (viewed) |
| x-post1 (T+434) | 70304B / `c5e4a07a7e94` | 18.7093/151 | 15.7556/158 | 13.9582/137 | 15.6222/150 | 15.7418/156 | 16.0115/158 | 16.0975/158 | 13.2300/129 | 14.5170/153 | 93.2626/175 | Countdown 2, starting gate, 00:00:00, 0 MPH (viewed) |
| x-post3 (T+438) | 68162B / `258f66aa158f` | 21.6277/145 | 13.5127/145 | 12.6187/129 | 12.0131/136 | 12.5667/135 | 12.6083/140 | 12.6727/141 | 11.7298/119 | 15.6363/139 | 24.3433/104 | 4TH/6, 00:00:02, 1%, 38 MPH (viewed) |
| x-post8 (T+444) | 68172B / `9f84a2224b58` | 12.0331/121 | 16.1259/143 | 13.0113/143 | 14.1938/153 | 15.5748/159 | 16.3837/157 | 16.5206/159 | 11.4119/116 | 21.3225/166 | 99.2395/183 | 4TH/6, 00:00:10, 5%, 51 MPH (viewed) |
| x-post15 (T+453) | 64860B / `42d5428ce457` | 16.2136/145 | 21.3688/172 | 16.7281/158 | 18.4440/166 | 19.5126/174 | 20.0337/176 | 20.1297/177 | 15.5388/133 | 24.6085/182 | 117.7010/206 | 3RD/6, 00:00:23, 11%, 51 MPH (viewed) |
| x-post25 (T+465) | 61932B / `b19f58c74f28` | 11.8578/127 | 17.4637/139 | 14.2361/153 | 15.3304/157 | 17.2762/170 | 18.4751/168 | 18.5668/170 | 12.6241/123 | 22.9643/173 | 117.8978/201 | 1ST/6, 00:00:39, 21%, 51 MPH (viewed) |
| x-post40 (T+482) | 56485B / `9f264b045687` | 11.4002/115 | 13.0151/140 | 13.0467/128 | 13.1185/126 | 16.0811/154 | 16.8913/156 | 16.9417/157 | 12.2211/124 | 16.3481/145 | 86.0173/173 | 6TH/6, 00:00:59, 23%, 52 MPH (viewed) |
| npre (T+498, pre-nudge) | 60331B / `efe6c70294ce` | 19.0187/111 | 15.0564/132 | 11.9843/124 | 12.1824/132 | 13.7601/131 | 14.0955/134 | 14.2091/137 | 10.4390/106 | 17.3764/135 | 77.4340/163 | 6TH/6, 00:01:18, 30%, 48 MPH, 0 pts (viewed) |
| n-post1 (T+502) | 68874B / `c66f2caefe6b` | 34.4152/167 | 17.2468/167 | 16.7160/173 | 15.7528/159 | 14.7062/162 | 14.6395/161 | 14.6743/161 | 15.9093/151 | 15.2273/155 | 36.4906/111 | 6TH/6, 00:01:23, 31%, 45 MPH, 110, combo banner (viewed) |
| n-post3 (T+505) | 58811B / `aa823f5437fd` | 21.1520/126 | 11.1825/124 | 14.5894/144 | 12.9606/118 | 14.1245/142 | 13.8365/147 | 13.8446/148 | 14.2384/117 | 16.0494/173 | 25.7562/99 | 6TH/6, 00:01:28, 34%, 49 MPH, 110 (viewed) |
| n-post8 (T+512) | 62484B / `961b1feb54b7` | 29.6624/136 | 15.1424/175 | 15.5901/136 | 15.4199/160 | 14.0711/162 | 14.2112/164 | 14.3030/164 | 15.0361/123 | 12.7059/124 | 31.4147/110 | 6TH/6, 00:01:37, 38%, 69 MPH, 110 (viewed) |
| n-post15 (T+521) | 58362B / `bf61b15aaf63` | 19.4224/135 | 12.7793/149 | 13.1586/117 | 12.8117/133 | 14.1104/144 | 13.7364/138 | 13.8351/139 | 12.4578/114 | 15.6198/140 | 52.9621/136 | 6TH/6, 00:01:49, 44%, 19 MPH, 110 (viewed) |
| n-post25 (T+533) | 57495B / `478f5671b956` | 13.7340/98 | 15.8178/147 | 13.5539/132 | 12.3915/126 | 15.5397/149 | 15.9917/149 | 16.0730/149 | 12.0236/131 | 21.5808/187 | 62.1503/142 | 6TH/6, 00:02:05, 52%, 50 MPH, 2170, FS Rail (viewed) |
| n-post40 (T+550) | 63807B / `a8a42ee9966c` | 16.1397/136 | 11.6413/141 | 12.3668/129 | 11.3462/136 | 14.2905/157 | 14.6980/154 | 14.7123/154 | 12.0862/127 | 16.4341/156 | 34.1083/122 | 6TH/6, 00:02:29, 59%, 43 MPH, 2170 (viewed) |

In-script (remote) vs PIL agreement: ≤0.06 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr/vs-pp scores at scale (e.g. npre band 19.0180 vs
19.0187; npre vs-pp 17.3794 vs 17.3764; n-post1 band 34.4177 vs 34.4152);
the known ~3–11× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.3999/7 remote vs 0.0795/0 PIL ≈ 5×; sepre vs-se 0.4072/6
vs 0.0371/0 ≈ 11× — T27 title / T28 menu / T29 SC / T30 ZC / T31 SP /
T32 SM / T33 SE / T34 MR / T35 precedent); hops ≤0.05. Vs-panel remote
receipt reads 0.67–0.93/p99 9–17 on panel-side PIL 0.38–0.68
(≈1.4–1.8× inflation at the ~0.5 scale — T35's 1.3–1.6× receipt
re-confirmed), so the < 2.0 whole bar holds even remotely (worst
remote 0.9275, 2.2× margin). The TAG crop gap re-confirmed at ~280×
(2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated
in PIL transfer to remote with single-digit inflation near zero and ~1×
at scale ≥5; text-dense crops need remote receipts or generous bars.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1236 | 10.1309/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1186 | 0.1471/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2455 | 0.2710/7 | same screen |
| post8 → post15 (mc) | 0.2005 | 0.2222/4 | same screen |
| post15 → scpre (park span) | — | 0.1533/3 | same screen |
| scpre → zc-post1 | 7.1633 | 7.1894/99 | screen change within +1 s |
| post1 → post3 (zc) | 0.2883 | 0.3122/9 | arrival settling |
| post3 → post8 (zc) | 0.2898 | 0.3116/7 | same screen |
| post8 → ccpre (park span) | — | 0.3156/8 | same screen |
| ccpre → sp-post1 | 9.3183 | 9.3556/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0516 | 0.0594/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0329 | 0.0388/0 | same screen |
| post8 → sppre (park span) | — | 0.0653/0 | same screen |
| sppre → pc-post1 | 5.2217 | 5.2466/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0218 | 0.0257/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0343 | 0.0391/0 | same screen |
| post8 → smpre (park span) | — | 0.0392/0 | same screen |
| smpre → rc-post1 | 0.4564 | 0.4820/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps in T32/T33) |
| post1 → post3 (rc) | 0.0014 | 0.0024/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0593 | 0.0620/0 | same screen (rc-post8 snowflake shimmer; still SE: se-tag 0.0094) |
| post8 → sepre (park span) | — | 0.0653/0 | same screen |
| sepre → sj-post1 | 10.5517 | 10.5748/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.0365 | 0.0411/0 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.0763 | 0.0838/1 | same screen |
| post8 → mrpre (park span) | — | 0.0786/0 | same screen |
| mrpre → mr-post1 | 12.4583 | 12.4204/148 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 1.6340 | 1.6530/61 | loading progress 18% → 97% |
| post3 → post8 (mr) | 25.4709 | 25.4807/253 | loading screen → race intro cinematic (no black frame captured this run — transition timing lottery) |
| post8 → post15 (mr) | 17.9800 | 17.9772/190 | cinematic → pre-race panel (panel arrived by +15, one sample early vs T34) |
| post15 → post25 (mr) | 0.3872 | 0.3919/18 | same screen (panel shimmer/animation) |
| post25 → post40 (mr) | 0.1901 | 0.1962/8 | same screen |
| post40 → stab1 (mr) | 0.1808 | 0.1861/8 | same screen |
| stab1 → stab2 (mr) | 0.0765 | 0.0825/3 | same screen |
| stab2 → pppre (park span) | — | 0.1295/5 | same screen |
| pppre → x-post1 | 14.4414 | 14.4247/153 | screen change within +1 s (pre-race panel → countdown/gate; decisive hop) |
| post1 → post3 (x) | 14.0666 | 14.0551/131 | countdown → live gameplay (gate → slope) |
| post3 → post8 (x) | 14.1580 | 14.2072/121 | live gameplay motion |
| post8 → post15 (x) | 9.6527 | 9.6973/138 | live gameplay motion |
| post15 → post25 (x) | 8.2685 | 8.3156/126 | live gameplay motion |
| post25 → post40 (x) | 12.2252 | 12.2641/129 | live gameplay motion |
| post40 → npre (span) | — | 11.5430/108 | live gameplay motion |
| npre → n-post1 | 14.2111 | 14.2700/113 | live gameplay motion (nudge tap lands inside this hop) |
| post1 → post3 (n) | 13.3862 | 13.4296/146 | live gameplay motion |
| post3 → post8 (n) | 11.0586 | 11.0873/160 | live gameplay motion |
| post8 → post15 (n) | 9.7593 | 9.7553/132 | live gameplay motion |
| post15 → post25 (n) | 12.4359 | 12.4341/180 | live gameplay motion |
| post25 → post40 (n) | 13.2286 | 13.2392/187 | live gameplay motion |

### R1 arrival park (pre-race panel)

| Item | Value |
|---|---|
| Post-Enter frames | `t36r1-mr-post1.jpg` @T+329 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 18% Loading…; `mr-post3` @T+333: same screen, 97% Loading…; `mr-post8` @T+341: race intro cinematic, gate interior (`EA RADIO BIG / Clockworks / Autopilot Off / Make a Sound` overlay, `Press X to skip`); `mr-post15` @T+351: pre-race panel = arrival (one sample early vs T34's +25) |
| Stability N (panel) | 6 snaps (post15/25/40 + stab1/2 + pppre) spanning T+351→T+429 (78 s) |
| Whole-frame pairwise (PIL) | 0.0243–0.3919/p99 ≤18 across all 15 pairs (panel shimmer/animation; min post40–pppre 0.0243/0, max post15–post25 0.3919/18; JPEG shas distinct) |
| Vs-panel-ref (whole) | 0.38–0.68/p99 6–17 across all 6 (all under the 2.0 gate; margins 3.0–5.3×) |
| Vs-MR (whole) | 19.34–19.67/p99 154 across all 6 (not My Rules) |
| Vs-SE (whole) | 16.22–16.51/p99 159–160 across all 6 (not Select Event) |
| Vs-SM (whole) | 16.22–16.51/p99 159–161 across all 6 (not Select Mode) |
| Vs-SP (whole) | 16.39–16.61/p99 157 across all 6 (not Select Peak) |
| Vs-ZC (whole) | 19.93–20.27/p99 162–164 across all 6 (not Setup Character) |
| Vs-SC (whole) | 19.19–19.50/p99 172 across all 6 (not Select Character) |
| Vs-menu (whole) | 19.07–19.41/p99 177–179 across all 6 (not menu) |
| Vs-title (band) | 34.49–34.50/p99 184 across all 6 (not title) |
| SE-TAG (crop) | 48.5186/132 identical across all 6 (tagline band static within run; T35's run read 48.5040/133, T34's 50.8209/132 — run-dependent, lineup/background phase) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Moby / Nate / Luther / Griff / Marty` (AI lineup differs run to run — T35: `Zoe/Kaori/Brodi/Viggo/Elise/Griff`, T34: `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`); `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 78 s (all 6 snaps pre-race panel) |

### R1 arrival (countdown → live gameplay; input-free until the nudge)

| Snap (wall T+) | Race clock | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|
| x-post1 (T+434, +0.6 s after XCROSS keyup) | 00:00:00 | gates | — | 0 MPH | — | countdown `2` over the starting gate; riders in gates |
| x-post3 (T+438) | 00:00:02 | 4TH/6 | 1% | 38 MPH | 0 | leaving the gate, start straight |
| x-post8 (T+444) | 00:00:10 | 4TH/6 | 5% | 51 MPH | 0 | open slope, jump crest ahead |
| x-post15 (T+453) | 00:00:23 | 3RD/6 | 11% | 51 MPH | 0 | banked turn, jostling AI rider |
| x-post25 (T+465) | 00:00:39 | 1ST/6 | 21% | 51 MPH | 0 | terrain-park approach |
| x-post40 (T+482) | 00:00:59 | 6TH/6 | 23% | 52 MPH | 0 | backcountry traverse (no-input rider falls to last) |

Race-clock vs wall-clock (wall since XCROSS keyup 1789977055.385; race
clock read off HUD, HH:MM:SS):

| Snap | Wall since keyup (s) | Race clock (s) | Ratio |
|---|---|---|---|
| x-post1 | 0.6 | 0 | — (countdown) |
| x-post3 | 4.6 | 2 | 0.43 |
| x-post8 | 10.6 | 10 | 0.94 |
| x-post15 | 19.6 | 23 | 1.17 |
| x-post25 | 31.6 | 39 | 1.23 |
| x-post40 | 48.6 | 59 | 1.21 |

Stability N (X): not a static arrival — 6 snaps over 48 s, all 15
whole-frame pairs 7.44–17.85/p99 ≤173 (live gameplay motion; min
x-post8–x-post25 7.4397/122, max x-post3–x-post15 17.8463/149; JPEG shas
distinct). Vs-panel-ref 14.52–24.61 across all 6 (decisively non-panel);
vs-MR 11.41–15.54 (non-MR). No reclaim to any menu/panel (all 6 snaps
countdown/live gameplay, positions/progress/timer all advancing).

### R1 nudge (ONE D-pad Left tap on live gameplay + bounded tail)

Nudge row (control / direction / duration / T+ / delivery):

| Item | Value |
|---|---|
| Control | D-pad Left (`Left = Keyboard/Left`, `PCSX2.ini:576`) |
| Direction | Left |
| xdotool key | `Left` (`windowfocus --sync` + `keydown`/`keyup`, all exit 0) |
| Keydown wall | 1789977122.820885527 (T+500.82, uptime 557) |
| Keyup wall | 1789977123.159512139 (T+501.16, uptime 557) |
| Tap duration | 338.6 ms (300 ms `sleep` + ~39 ms xdotool overhead) |
| Pre-nudge snap | `npre` @T+498 (2.8 s before keydown): live race, HUD read below |
| Delivery | Receipted in-script (`NUDGE_LEFT_KEYDOWN/HELD/KEYUP_WALL` + uptimes in `t36r1-poll.log`); same xdotool path as the 89/89 menu holds |

Pre-nudge HUD (read off the viewed `npre` snap):

| Item | Value |
|---|---|
| Race clock | 00:01:18 |
| Position | 6TH/6 |
| Progress | 30% |
| Speed | 48 MPH |
| Score | 0 pts |
| Scene | Rider mid-slope approaching a jump crest, starting-gate arena behind; race running |

Post-nudge HUD delta series (read off viewed snaps; wall since nudge
keyup 1789977123.160; race advanced = race clock minus npre 78 s; wall
span = exposure wall minus npre wall 1789977120):

| Snap (wall T+) | Wall + | Race clock (+adv) | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|---|
| npre (T+498) | −2.8 s (pre) | 00:01:18 (+0) | 6TH/6 | 30% | 48 MPH | 0 | pre-nudge baseline |
| n-post1 (T+502) | +0.8 s | 00:01:23 (+5) | 6TH/6 | 31% | 45 MPH | 110 | past the crest, combo banner |
| n-post3 (T+505) | +3.8 s | 00:01:28 (+10) | 6TH/6 | 34% | 49 MPH | 110 | carving, chevron barriers |
| n-post8 (T+512) | +10.8 s | 00:01:37 (+19) | 6TH/6 | 38% | 69 MPH | 110 | forest straight, speed lines |
| n-post15 (T+521) | +19.8 s | 00:01:49 (+31) | 6TH/6 | 44% | 19 MPH | 110 | near trees, slow |
| n-post25 (T+533) | +31.8 s | 00:02:05 (+47) | 6TH/6 | 52% | 50 MPH | 2170 | `FS Rail` trick label |
| n-post40 (T+550) | +48.8 s | 00:02:29 (+71) | 6TH/6 | 59% | 43 MPH | 2170 | open slope, pines |

Race-advance vs wall-span (race-advanced-since-npre / wall-since-npre):

| Snap | Race adv (s) | Wall span (s) | Ratio |
|---|---|---|---|
| n-post1 | 5 | 4 | 1.25 |
| n-post3 | 10 | 7 | 1.43 |
| n-post8 | 19 | 14 | 1.36 |
| n-post15 | 31 | 23 | 1.35 |
| n-post25 | 47 | 35 | 1.34 |
| n-post40 | 71 | 52 | 1.37 |

Post-nudge frame motion (whole-frame PIL): all 21 N pairs 9.05–16.85/p99
≤187 (min npre–n-post25 9.0465/135, max n-post3–n-post25 16.8469/175;
JPEG shas distinct). Motion throughout — no static frame, no freeze, no
menu/panel reclaim in the 52 s tail. Vs-panel-ref 12.71–21.58 across all 7
(decisively non-panel).

Observed (non-)effect characterization (tabled, not verdicts):

| Question | Observed |
|---|---|
| Did position change? | No — 6TH/6 in all 7 snaps (pre + 6 post) |
| Did progress change? | Progress advances monotonically 30% → 59% (race-clock-driven, no jumps) |
| Did the clock change? | Advances steadily: +71 s race over +52 s wall (~1.35×, matches turbo) |
| Did speed change? | Varies 48→45→49→69→19→50→43 MPH across the tail (69 MPH forest straight @+8 s, 19 MPH near trees @+15 s) — ordinary race-speed excursions distributed across the tail, none coincident with the +0.8 s sample |
| Did score change? | 0 → 110 by +1 s (jump/combo off the crest the rider was approaching in `npre`) → 2170 by +25 s (`FS Rail`) — ordinary race scoring, distributed across the tail |
| Did heading change? | Rider visible and racing down-course in all 7 snaps; no stop/crash/reversal; chase cam centers the rider so small heading changes are not directly readable |
| Any HUD discontinuity at the tap? | None at the sampled cadence — position/progress/clock advance monotonically; no freeze, no menu, no reclaim |
| In-game registration? | Delivery receipted (focus + keydown/keyup exit 0, 338.6 ms); in-game effect below sampling resolution — see isolation limit |
| Isolation limit | Single run, no same-seed control (AI lineup/RNG differ run to run); a 300 ms tap's positional contribution is not separable from the race's own progression in this 1/3/8/15/25/40 s sampling |
| Recipe (one variant per attempt) | (a) denser post-nudge sampling (1 s cadence ×10 s) + rider-pixel tracking to resolve the immediate heading response; (b) longer-hold variant (e.g. 1 s) for a larger maneuver; (c) no-nudge control run at a matched race phase (match phase, not seed — RNG differs run to run) |

### R1 PP-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Departure mrpre→post1 | 12.4583 | > 5.0 | yes |
| Arrival static p25→p40 | 0.1901 | < 1.0 | yes |
| Arrival static p40→s1 | 0.1808 | < 1.0 | yes |
| Arrival static s1→s2 | 0.0765 | < 1.0 | yes → `PP-LIKE`, X-Continue Cross pressed |
| Non-MR (stab2 vs-mr) | 19.6210/154 | > 5.0 | yes |
| Vs-pp receipt (post15/25/40) | 0.9275/17, 0.7009/9, 0.7357/10 | (not a leg — receipt) | tabled (≈1.4–1.6× vs PIL 0.38–0.68; under 2.0 even remotely) |
| Vs-pp receipt (stab1/2) | 0.6929/9, 0.6658/9 | (not a leg — receipt) | tabled |
| Vs-pp receipt (pppre) | 0.7376/10 | (not a leg — receipt) | tabled (≈1.5× vs PIL 0.4845) |

### R1 LIVE gate legs (in-script proxy, remote)

| Gate leg | Value | Bar | Margin | Pass? |
|---|---|---|---|---|
| Departure pppre→x-post1 | 14.4414 | > 5.0 | 2.9× | yes |
| Non-panel (x-post40 vs-pp) | 16.3774/145 | > 5.0 | 3.3× | yes |
| Motion (x-post15→x-post25) | 8.2685 | > 5.0 | 1.7× | yes |
| Motion (x-post25→x-post40) | 12.2252 | > 5.0 | 2.4× | yes → `LIVE-LIKE`, pre-nudge snap + ONE nudge pressed |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Live race reproduced (HUD advancing, rider moving) | countdown `2` at +0.6 s, live gameplay from +4.6 s, race 6TH/6 at 59% by +117 s wall with one steering tap; clock/progress advance monotonically, all X+N hops 8.27–14.44 (motion) |
| Nudge acted on it (pre-nudge = racing with HUD read) | `npre` viewed: 00:01:18, 6TH/6, 30%, 48 MPH, 0 pts, rider mid-slope; vs-pp 17.38 (non-panel) |
| Post-nudge HUD delta table (or exact non-effect characterization) | 6-snap HUD series above (position constant 6TH/6, progress 30→59%, clock +71 s, speed/score excursions distributed across the tail, no discontinuity at the tap) + isolation limit + recipe |
| Full input log + trace sha | `t36r1-poll.log` (152 lines: every score + press, walls + uptimes) + trace `a6f43f21…91842bf` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32/T33/T34/T35 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725,
first vblank L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks
397 frozen (all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not
changed`; clean tail @561.3993. Census: EE 11,745,810 (52, set-identical
to T35 R1) · IOP 20,231,468 (155, set-identical to T35 R1 — nudge +
gameplay adds no new called API) · `libsd.006: sceSdGetParam` 23484
(T35: 26065); `sceSdGetAddr` 4,038,240 (T35: 4,077,648).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R1 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate → SnowJam Cross → MR-LIKE gate → Enter Cross → PP-LIKE settled-panel gate → X Cross → LIVE-LIKE proxy gate) |
| Cross on X Continue? | YES (XCROSS @T+432.85 R1, pre-press = pre-race panel, X Continue) |
| Live race reached? | YES (countdown `2` @T+434 → live gameplay by T+438 → race at 59%, 6TH/6 @T+550, still running) |
| Nudge on live gameplay? | YES (NUDGE Left 338.6 ms @T+500.82, pre-nudge = racing 00:01:18 6TH/6 30%) |
| Bounded variant? | none run (pre-nudge = racing — variant condition not met; brief stops at R1 + recipe) |
| 1200 s cap | Not reached — R1 ≈ T+571; attempts 2–3 unexercised |
| Chain end | Live Snow Jam race (6TH/6, 59%, 00:02:29) after ONE steering tap; race not yet finished at capture end |

## T36-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t36 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules → Cross → game load → cinematic → pre-race panel → Cross → countdown → live gameplay → D-pad Left tap → 40 s tail, T+~571) | 44,868,142 / 2,885,188,969 | `a6f43f21064fe9b5a9ae6e18333af219fb4118fd8495afd046c4beab918142bf` (analyze-sha on H17 = post-restart re-verify on H18 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t36r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t36r1-trace-head.txt` 149019 B sha `8682e642714d…`, `t36r1-trace-tail.txt` 129907 B sha `c0a1cf603566…`) |
| `emulog-pre-t36-20260921T074342Z.txt` = t35 R1 (preserved at R1 boot) | — / 2,919,779,317 | `e337f8e8304eba0ca963302e0234737e35938ace54a7775417b5bc2dafc60865` (re-verified post-run: matches T35) | bytesize-only (T35 precedent; SSD holds T35's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 11,745,810 (52
distinct, set-identical to T35 R1) · IOP 20,231,468 (155, set-identical
to T35 R1) · vblanks 397. Committed: `t36r1-census.txt` (11694 B sha
`b65a8c1dccb4…`), `t36r1-samples.txt` (5874 B sha `8913e720404d…`),
`t36r1-poll.log` (152 lines, 9266 B sha `80410a917c70…`),
`t36r1-stdout.txt` (410 lines, 26727 B),
`t36r1-stderr.txt` (full `set -x` shell trace, 2422 lines, 132849 B),
`t36r1-trace-head.txt` / `t36r1-trace-tail.txt`.
Trace-head note: same 149019 B as T34/T35 R1 heads but sha differs
(`8682e642…` vs `78fb01a6…`) — timestamp-stripped content differs across
timing/wall-clock/shader-cache lines (`gl_programs.idx` cache entries:
287 vs 240 vs 173 — shader cache growth across runs).

## T36-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H16 …6323
ssh bytesize 'wsl dmesg' > /tmp/t36-dmesg-pre.txt                     # 440 lines, 0 AcceptAsync (H16)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t36-eventlog-pre.txt  # head 03:38:44
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl grep -n Up …; grep -n Down …; grep -n Left …; grep -n Right …'  # D-pad arrows :573-576, sticks W/D/S/A + T/H/G/F
ssh bytesize 'wsl grep -n Start …; sed -n 565,600p …/inis/PCSX2.ini'   # Start :582 Return, Deadzone 0, full pad section
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t35-ref-panel.ppm'    # all 9 refs reproduce
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c; du -sh …/logs/'         # 884G / C: 13G / 29G
ssh bytesize 'wsl ls …/logs/; ls -la …/logs/emulog.txt'                # 23 emulogs, live = T35 R1
ssh bytesize 'wsl sha256sum …/logs/emulog.txt'                        # e337f8e8… T35R1 live
# T35 ref snaps (local): 12/12 sizes+sha12 reproduce T35 §T35-2
# adapt t36-auto.sh from the T35 copy (LIVE gate + nudge + N tail; bash -n), t36-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t36-auto.sh t36-analyze.sh t36-vcount.sh t36-cropdiff.py "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t36-… /home/brad/pcsx2-t4/; sha256sum …'  # staged shas match local
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H17
ssh bytesize 'wsl sha256sum …/t36-auto.sh …/t36-cropdiff.py …/t35-ref-panel.ppm; ls …'  # staged shas survive restart
ssh bytesize 'wsl python3 …/t36-cropdiff.py …REFPP …; python3 … REFMR …'  # 0.0000/0 PPM x2
ssh bytesize 'wsl dmesg' > /tmp/t36-dmesg-preH17.txt                  # 473 lines, 1 AcceptAsync [21.79] (H17)
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat …; git … rev-parse HEAD; … status --short; sha256sum …nvm; grep -n Cross …; grep -n Left …'  # full re-verify on H17
# R1 (ONE ssh; exit 0; LIVE-LIKE → NUDGE → 40 s tail)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t36-auto.sh' > /tmp/t36r1-run-stdout.txt 2>/tmp/t36r1-run-stderr.txt  # T36_DONE, up 57→628
ssh bytesize 'wsl dmesg' > /tmp/t36-dmesg-post-r1.txt                 # IMMEDIATELY after run ssh: 474 lines, 1 AcceptAsync [21.79] (H17, full R1 coverage)
ssh bytesize 'wsl bash …/t36-analyze.sh'                              # a6f43f21…, 44868142 L
ssh bytesize 'wsl bash …/t36-vcount.sh; wc -l …/t36-poll.log; ls …/t36-*.jpg'  # 397 frozen / 152 / 56 JPGs
ssh bytesize 'wsl cp <30 chain jpg> /mnt/c/…'                          # (explicit list, one wsl call)
ssh bytesize 'wsl cp <26 n/mr/x jpg + poll.log + census/samples> /mnt/c/…'  # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t36-…" /tmp/t36-fetch/                         # 56 jpg + logs (r1-prefixed local)
ssh bytesize 'wsl cp <9 ref PPMs> /mnt/c/…'                            # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t*-ref-*.ppm" /tmp/t36-refs/                   # 9 refs, shas re-verified
# R1 post-hoc (local fastdiff, 4/4 bit-exact): chain panel, hops, 15 panel pairs, 15 X pairs, 21 N pairs, xrun, census set-compare
ssh bytesize 'wevtutil …' > /tmp/t36-eventlog-post.txt                # head H17-teardown 03:57:43; H16→H17 03:42:05/03:42:46; ZERO in-window entries
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H18 …8093 (fresh, created by this call)
ssh bytesize 'wsl dmesg' > /tmp/t36-dmesg-post-h18.txt                # 448 lines, 1 AcceptAsync [17.19] (H18)
ssh bytesize 'wsl sha256sum …nvm; ls -la …nvm; sha256sum …/logs/emulog.txt; ls -la …; ls …/logs/'  # NVM untouched, a6f43f21… re-verified, 24 emulogs
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t36-20260921T074342Z.txt; ls -la …'  # e337f8e8… T35R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t36r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t36r1-trace-tail.txt         # 2000 lines, clean tail @561.3993
ssh bytesize 'wsl grep -c LoadStartModule …/logs/emulog.txt'           # 18
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t36r1.txt; ls -la …'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t36r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t36r1.txt"         # a6f43f21… match
ssh bytesize 'wsl df -h / /mnt/c; du -sh …/logs/; date -u; cat /proc/uptime; grep btime /proc/stat'  # 881G / C: 3.9G / 32G / VM-H19
ssh bytesize 'wevtutil qe System /c:12 /rd:true /f:text' > /tmp/t36-eventlog-final.txt  # H18-teardown 04:11:18, H19-create 04:11:31
# report (chunks; receipts include tail -3)
cp /tmp/t36-dmesg-*.txt /tmp/t36-eventlog-*.txt /tmp/t36r1-run-stdout.txt … local/research/T36/  # renamed per §evidence
tail -3 local/research/T36/REPORT.md
git add -f local/research/T36/<75 files by name>                      # ignored dir, forced
git commit -m "[T36] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T36-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (steering characterization) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate (departed + non-SE + static) → Cross on Continue → PP-LIKE settled-panel gate (departed + static ×3 + non-MR) → Cross on X Continue → LIVE-LIKE proxy gate (departed + non-panel + motion ×2) → ≤3 attempts) → live gameplay; then a single 300 ms D-pad Left tap acts on the live race (R1: pre-nudge 00:01:18 6TH/6 30%, post-nudge tail to 00:02:29 6TH/6 59% with no measurable HUD discontinuity at the 1/3/8/15/25/40 s sampling; race clock ~1.35× wall under turbo). Next, ONE variant per attempt: (a) denser post-nudge sampling (1 s cadence ×10 s) + rider-pixel tracking to resolve the immediate heading response; (b) longer-hold variant (e.g. 1 s) for a larger maneuver; (c) no-nudge control run at a matched race phase (match phase, not seed — AI lineup/RNG differ run to run). Gate note: the nudge→gameplay whole-frame hop is large (~14.27) because the race never stops moving — gate on the HUD (clock/position/progress/speed/score), not the frame. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | Zero in-window flaps this session + 1 pre-session + 1 mid-session + 2 post-everything restarts (all not by me) | 0 userland kills on any VM this session; AcceptAsync exact counts 0/1/1/1 across the 4 committed dmesg files, all outside the run window (H16-pre 0; H17-pre 1×[21.79] pre-window; H17-post 1×[21.79] pre-window, zero in-window; H18-post 1×[17.19] post-everything VM) + 1 pre-session VM restart between T35 and T36 (H15→H16; T35: 1 pre-session restart) + 1 mid-session VM restart between pre-checks and staging (H16 07:38:44→07:42:05, H17 create 07:42:46; 41 s gap with no VM; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified) + 2 post-everything VM restarts (H17→H18 07:57:43, after all fetch WSL calls — proven by H18's 2.15 s uptime at the 08:08:15 identity check; H18→H19 08:11:18/08:11:31, between trace-staging and df-final; only final state reads + trace slices ran on H18/H19). R1 completed exit 0 with zero in-window flaps on the dmesg record — no T27 §4 effects-verification needed (the immediate post-run dmesg read closed T33's sequencing gap). Precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero entries of any kind in-window; boundaries bound all restarts | Newest-30 reads (pre/post): H15 teardown 03:27:09 → H16 create 03:38:44 → H16 teardown 03:42:05 → H17 create 03:42:46 → H17 teardown 03:57:43; inside the R1 window 03:43:42–03:53:13 (local): ZERO entries of any kind (no Volsnap this run — C: filled 13 G → 3.9 G after the window; no Hyper-V-VmSwitch — precedent stands). Final newest-12: H18 teardown 04:11:18 → H19 create 04:11:31. `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H17 btime |
| G4 | Hold count 89/89 (534 ms-class) + 1/1 nudge tap (300 ms-class) | 534 ms-class holds register 89/89 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33+T34+T35+T36 (T36 R1: 535.1/535.0/536.3/536.7/535.0/536.6/537.1/535.9/536.0/538.1 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect. Separately: the 300 ms-class steering tap delivered 1/1 (338.6 ms wall: 300 ms sleep + ~39 ms xdotool overhead) — different input class, not a bisection |
| G5 | Title/menu/SC/ZC/SP/SM/SE/MR frozenness; attract differs; snowflake shimmer on SE + MR; panel animation + lineup lottery on arrival; countdown near-frozen; gameplay lottery | Title text-band frozen across showings (0.0474/1 R1); R1's 4 frames bit-identical to T35 R1's run (a1-post15, rc-post1, rc-post3, mr-post1 — rc-post1 now identical across THREE runs T34/T35/T36); menu whole-frame ≤0.08/p99 ≤1 cross-run; SC cross-run 0.09–0.22/p99 2–5; ZC cross-run 0.09–0.12/p99 1–3; SP cross-run ≤0.08/p99 ≤1; SM cross-run 0.007–0.05/p99 0; Select Event ≤0.04/p99 0 cross-run (rc-post8 snowflake animation); My Rules ≤0.08/p99 0 (snowflake drift); pre-race panel ≤0.39/p99 ≤18 within run over 78 s (panel shimmer/animation) + AI rider lineup differs run to run (T36 `Zoe/Moby/Nate/Luther/Griff/Marty` vs T35 `Zoe/Kaori/Brodi/Viggo/Elise/Griff` vs T34 `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`) + SE-TAG crop on panel constant within run but run-dependent (48.5186/132 vs T35's 48.5040/133 vs T34's 50.8209/132); load→panel transition timing is lottery-dependent (T36: 97% @+3, cinematic @+8, panel @+15 — same shape as T35, different cinematic track: Clockworks vs Buffet of Breaks) — the settled-panel gate handled all timings; countdown-`2` gate frame near-frozen cross-run (1.9403/57); live gameplay never static (7.44–17.85 X, 9.05–16.85 N). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the nudge run | `WaitVblankStart` stops after log ≤90 in T36 R1 including countdown + live gameplay + nudge (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T35-R1-identical modulo counts). The attract/title/menu/submenu/game sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical; IOP count shifts on audio) | Like prior arrivals, nudge + gameplay adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T35 R1; counts shift (`GetThreadId` 5.02M→4.73M, EE total 12.28M→11.75M; IOP 20.35M→20.23M; `sceSdGetParam` 26065→23484, `sceSdGetAddr` 4.08M→4.04M — race audio traffic). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts + C: pressure | `…/logs/` now holds ~32 GB across 24 emulogs (T17→T36 chain, all preserved); C: 3.9 G avail (pre 13 G — run staging + 9 ref PPMs + 2.9 GB trace staging; T35 pre was 14 G). C: at 100% — next session should clear `C:\Users\bradr\pcsx2-t4\` staging (owner's call; left in place per precedent). T36 R1 full trace SSD-copied + sha-verified (2.89 GB: `emulog-t36r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T36 brief cites `t35r1-x-post{1,3,8,15,25,40}.jpg` + `t35r1-x-stab{1…6}.jpg` — all 12 exist with sizes+sha12 reproducing T35 §T35-2. T28 G9 lesson holds |
| G10 | Session wall + run durations | ~40 min active of the 4 h box (one run + report/commit); zero lease waits (no lease exists for T36). R1 wall 571 s — 211 s over the ≤6 min guidance (X-phase scoring + nudge tail); R1 full dmesg coverage, zero flaps |
| G11 | X11 mount needed once, harmless | The single `/tmp/.X11-unix` tmpfs mount landed on VM-H17 (the H16→H17 restart fell between pre-checks and staging); mount verified present on H17 pre-R1, R1 started Xvfb :99 cleanly regardless (exit 0 + 56 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 / T33 G11 / T34 G11 / T35 G11 stand) |
| G12 | Remote-vs-PIL gap receipted again on the panel whole bar: ~1.4–1.8×, bar holds even remotely | R1's in-script vs-pp receipt reads 0.67–0.93/p99 9–17 on panel-side PIL 0.38–0.68 (≈1.4–1.8× inflation at the ~0.5 scale — T35's 1.3–1.6× receipt re-confirmed on a new run), so the < 2.0 whole bar holds even as an in-script leg (2.2× margin on the worst remote 0.9275). The TAG-crop gap re-confirmed at ~280× (2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated in PIL transfer to remote with single-digit inflation near zero and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars |

## Evidence files

`REPORT.md` (this file),
scripts: `t36-auto.sh`,
`t36-cropdiff.py` (T35 logic, byte-identical),
`t36-analyze.sh`, `t36-vcount.sh` (output-name deltas only; vcount
byte-identical);
R1: `t36r1-start.jpg`, `t36r1-a1-now.jpg`, `t36r1-a1-poll01.jpg`,
`t36r1-a1-pre.jpg`, `t36r1-a1-post{3,8,15,25}.jpg`, `t36r1-menupre.jpg`,
`t36r1-mc-post{1,3,8,15}.jpg`, `t36r1-scpre.jpg`,
`t36r1-zc-post{1,3,8}.jpg`, `t36r1-ccpre.jpg`,
`t36r1-sp-post{1,3,8}.jpg`, `t36r1-sppre.jpg`,
`t36r1-pc-post{1,3,8}.jpg`, `t36r1-smpre.jpg`,
`t36r1-rc-post{1,3,8}.jpg`, `t36r1-sepre.jpg`,
`t36r1-sj-post{1,3,8}.jpg`, `t36r1-mrpre.jpg`,
`t36r1-mr-post{1,3,8,15,25,40}.jpg`, `t36r1-mr-stab{1,2}.jpg`,
`t36r1-pppre.jpg`, `t36r1-x-post{1,3,8,15,25,40}.jpg`,
`t36r1-npre.jpg`, `t36r1-n-post{1,3,8,15,25,40}.jpg` (56 snaps),
`t36r1-census.txt`, `t36r1-samples.txt`, `t36r1-poll.log`,
`t36r1-stdout.txt`, `t36r1-stderr.txt`, `t36r1-trace-head.txt` / `t36r1-trace-tail.txt`;
flaps: `t36-dmesg-vmH16-pre.txt` (0 AcceptAsync on H16, pre-run) /
`t36-dmesg-vmH17-pre.txt` (1 AcceptAsync [21.79] pre-window on H17) /
`t36-dmesg-vmH17-post.txt` (1 AcceptAsync [21.79] pre-window; full R1-window
coverage, zero in-window) / `t36-dmesg-vmH18-post.txt` (1 AcceptAsync
[17.19] on H18, fresh boot),
`t36-eventlog-pre.txt` / `t36-eventlog-post.txt` / `t36-eventlog-final.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t36r1.txt`
(2,885,188,969 B `a6f43f21…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T35 R1
`…-20260921T074342Z.txt` `e337f8e8…`.

