# T35 report — Cross on X Continue from the pre-race panel: countdown/live gameplay (bytesize, no lease)

Brief: T35 (Cross on X Continue from the pre-race panel). Tables, no
verdicts. One boot ran on bytesize (R1: chain reproduced to the pre-race
panel, ONE 534 ms-class Cross (X Continue), arrival mapped); laptop-side
work was ssh/scp + local reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T34/REPORT.md` (all of it: R1 reached
the pre-race panel via ENTER Cross on My Rules @T+326.56 (load 18% → 92% →
black frame → race intro cinematic → panel), `Snow Jam - Race`, 8 snaps
over 98 s pairwise 0.024–0.395/p99 ≤18 (panel animation), no reclaim; G1
proposes one 534 ms Cross (X Continue) to start the race). This brief
executes T34's G1.

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
settled pre-race panel (X Continue) starts the race (countdown and/or live
gameplay); observable — pre-press snap = pre-race panel (whole-frame match
vs T34 `t34r1-mr-stab6.jpg` ref under the calibrated < 2.0 gate + viewed
snap), post-press snap series + per-hop whole diffs + arrival stability N;
screen content read off viewed snaps; alternatives — screen ignores Cross
(post series still panel), slow next-screen load (change lands late in the
+40 s tail), press never acted on arrival (pre-press ≠ pre-race panel → ONE
bounded variant allowed); stop — table the exact observed behavior +
recipe, no button-mashing survey.

## T35-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T35; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T35]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T35 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| T34 reference snaps present | — | all 12 arrival shas reproduce T34 §T34-2 (`mr-post{1,3,8,15,25,40}` + `mr-stab{1…6}` full sha256 + sizes) | yes |
| Free space | — | WSL `/` 887 G avail; C: 14 G (836 G); laptop `/` 4.7 Gi avail; SSD 363 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×2, both on VM-H14 (the H13→H14 restart fell between C:-staging and WSL-staging per event boundaries + file mtimes; mount verified present on H14 pre-R1 — T32 G11 stands) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t35-{auto,analyze,vcount,cropdiff}.sh/.py`, `t35-ref-panel.ppm` (3,932,177 B, sha `192e0472…580eb6`), `t35-{r1-census,samples}.txt` (via analyze), `t35-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t35-*.txt` (rotation chain, see trace table), `boot-t35.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t35*` + `emulog-t35r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 1 pre-session between T34 and T35 (H12→H13) + 1 mid-session between staging and R1 (H13→H14, 78 s gap with no VM; every ssh exit 0 across it; staged files persist — same VHD, shas re-verified) + 1 post-everything (H14→H15; only final state reads + trace slices ran on H15) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H13 btime:
02:53:50→`1789973630`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 06:41:27 | VM-H12 teardown (T34's VM, after T34's session) | eventlog-pre (IDs 71/69 + 233/234/234) |
| 2 | 06:53:50 ([0] VM-H13) | VM-H13 started fresh ~2 s before first ssh | btime `…3630`, eventlog-pre head (IDs 292/67/291/233/232/102/291/102/291/291) |
| 3 | 06:53:52–~06:56 | Pre-run checks on VM-H13 (all ssh exit 0, zero flaps) + C:-staging (VM-independent) | `t35-dmesg-vmH13-pre.txt` (0 AcceptAsync, 417 lines, 0 `Ioctl failed` — captured at uptime ~2 s, before dxg queries) |
| 4 | 06:56:15–06:57:33 | VM-H13 teardown → VM-H14 create (mid-session restart, NOT by me; between C:-staging and WSL-staging; 78 s gap with no VM; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified; mount + ref-checks verified on H14) | btime `…3853`, eventlog-post (IDs 71/69/233/234/234 teardown, 292/67/291/233/232/102/291/102/291/291 create), `t35-dmesg-vmH14-pre.txt` (1 AcceptAsync [32.29] pre-window, 473 lines) |
| 5 | 06:58:32–07:08:14 ([65]→[640] H14) | R1 single-shot exit 0, `T35_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart in-window) | exit 0, 55 snaps, trace sha |
| 6 | 07:08:14–~07:13 | R1 analyze (exit 0) + all R1 fetches (exit 0) on VM-H14 | `t35-census.txt`, 55 JPGs + logs |
| 7 | 07:13:19 | VM-H14 teardown → VM-H15 create (post-everything restart, NOT by me; only final state reads + trace slices ran on H15) | btime `…5378`, eventlog-post head (IDs 71/69/233/234/234 teardown) |
| 8 | 07:23:00 ([1.77] H15) | VM-H15 fresh, 0 kills | `t35-dmesg-vmH15-post.txt` (4 AcceptAsync, 545 lines, boot coverage) |
| 9 | event log | Newest-30 reads (pre/post): head moves H13-create 02:53:50 → H14-teardown 03:13:19; boundaries H12-teardown 02:41:27, H13-create 02:53:50, H13-teardown 02:56:15, H14-create 02:57:33, H14-teardown 03:13:19; in-window (02:58:32–03:08:14 local) entries: 2× Volsnap ID-33 (C: shadow-copy cleanup, NOT WSL) + zero Hyper-V-VmSwitch entries — userland kills leave no Windows trace (T17/T21/T23/T25/T27/T28/T29/T30/T31/T32/T33/T34 precedent stands) | `t35-eventlog-{pre,post}.txt` |
| 10 | dmesg noise | `Ioctl failed` lines 0 pre (H13, uptime-2 s capture) / 46 pre (H14) / 46 post-R1 (H14) / 92 post (H15) — steady boot/GPU-query noise, not kills; kill-pattern grep (`killed process\|out of memory\|panic\|oops\|segfault`) matches only the 2 `panic=-1` cmdline echoes per file | dmesg files |

AcceptAsync exact counts with uptime-stamp positions relative to the R1
window (T_BOOT uptime 65 → end 640, all on VM-H14):

| Committed file | Lines | AcceptAsync count | Uptime stamps | Position vs run window |
|---|---|---|---|---|
| `t35-dmesg-vmH13-pre.txt` | 417 | 0 | — | different VM (pre-restart); outside |
| `t35-dmesg-vmH14-pre.txt` | 473 | 1 | [32.290543] | before window (32 < 65); outside |
| `t35-dmesg-vmH14-post.txt` | 482 | 2 | [32.290543], [655.259514] | [32.29] pre-window, [655.26] post-window (640 < 655, run-ssh teardown); ZERO in-window |
| `t35-dmesg-vmH15-post.txt` | 545 | 4 | [39.798355], [74.501547], [96.395900], [127.014501] | different VM (post-everything, no run); outside |

## T35-1. Panel detector + calibration (thresholds, match scores)

Tool: `t35-cropdiff.py` (copy of T34's, byte-identical;
`cmp` clean; `t35-vcount.sh` differs only in a comment line;
`t35-analyze.sh` differs only in output names + header noun).
Title text-band method unchanged (thresholds frozen: TITLE band mean <
2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu mean < 2.0;
NONMENU / NONSC / NONZC / NONSP / NONSE / NONMR whole-vs-ref mean > 5.0;
DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). New: pre-race panel
reference `t35-ref-panel.ppm` (3,932,177 B, sha
`192e04722481f77bfbb933133504c0f8ab8432c48971034a5277db1aaf580eb6`),
derived from T34's `t34r1-mr-stab6.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T35-4; T28
§T28-1 recipe). Ref-vs-JPEG recipe check: 0.0000/0 (JPEG decode
deterministic, T28 G9 lesson holds). Remote PPM-mode self-checks pre-run:
panel ref 0.0000/0, MR ref 0.0000/0.

Panel whole-frame calibration matrix (candidate vs `t34r1-mr-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post25 vs stab6 | 0.3503 | 16 | 94 | panel-panel (whole) |
| post40 vs stab6 | 0.1263 | 5 | 96 | panel-panel (whole) |
| stab1 vs stab6 | 0.0672 | 2 | 102 | panel-panel (whole) |
| stab2 vs stab6 | 0.1024 | 4 | 93 | panel-panel (whole) |
| stab3 vs stab6 | 0.3499 | 16 | 84 | panel-panel (whole) |
| stab4 vs stab6 | 0.1824 | 8 | 84 | panel-panel (whole) |
| stab5 vs stab6 | 0.2196 | 9 | 104 | panel-panel (whole) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| a1-now (attract) vs stab6 | 10.9545 | 141 | 213 | attract-vs-panel (whole, NEAREST non-panel) |
| mr-post15 (cinematic) vs stab6 | 15.0217 | 190 | 243 | cinematic-vs-panel (whole) |
| start (attract) vs stab6 | 15.3165 | 142 | 226 | attract-vs-panel (whole) |
| sepre (T34 SE) vs stab6 | 16.4320 | 160 | 230 | SE-vs-panel (whole) |
| smpre (T34 SM) vs stab6 | 16.4132 | 160 | 230 | SM-vs-panel (whole) |
| sppre (T34 SP) vs stab6 | 16.5811 | 157 | 230 | SP-vs-panel (whole) |
| menupre (T34 menu) vs stab6 | 19.2993 | 178 | 233 | menu-vs-panel (whole) |
| scpre (T34 SC) vs stab6 | 19.4522 | 172 | 224 | SC-vs-panel (whole) |
| mrpre (T34 MR) vs stab6 | 19.5250 | 152 | 200 | MR-vs-panel (whole) |
| sj-post8 (T34 MR) vs stab6 | 19.5905 | 153 | 200 | MR-vs-panel (whole) |
| ccpre (T34 ZC) vs stab6 | 20.1827 | 165 | 225 | ZC-vs-panel (whole) |
| mr-post8 (black) vs stab6 | 20.4494 | 191 | 243 | black-vs-panel (whole, TRANSITION not arrival) |
| mr-post1 (load 18%) vs stab6 | 21.0753 | 169 | 249 | load-vs-panel (whole) |
| mr-post3 (load 92%) vs stab6 | 21.1216 | 169 | 253 | load-vs-panel (whole) |
| a1-pre (T34 title) vs stab6 | 22.1514 | 183 | 232 | title-vs-panel (whole) |
| ref PPM vs stab6 JPEG | 0.0000 | 0 | 0 | recipe exact (JPEG decode deterministic) |
| ref PPM vs ref PPM | 0.0000 | 0 | 0 | self (local PIL + remote PPM modes) |

PP-LIKE settled-panel gate (as frozen pre-run): in-script park criterion =
decisively left MR (mrpre→post1 hop > 5.0) AND arrival static ×3
(post25→post40, post40→stab1, stab1→stab2 hops < 1.0, spanning ~35 s) AND
non-MR (stab2 vs-mr > 5.0). The vs-panel line is scored in-script as the
remote receipt but is NOT a gate leg (T28 MENU / T29 SC / T30 ZC / T31 SP /
T32 SM / T33 SE / T34 MR precedent — the X-Continue Cross press does NOT
depend on a strict whole-frame panel gate); the strict whole-vs-panel <
2.0 bar is confirmed post-hoc (T33 G12: no pre-run remote receipt exists
for the ~0.35 panel-side mean — PIL on WSL chicken-and-egg). The Enter
hop is decisive (~12.43–12.47), so DEPARTED > 5.0 fires normally here,
and the 3-hop static chain cannot fire on the black transition frame
(T34 R1: post1→post3 2.13, post3→post8 39.96, post8→post15 10.19,
post15→post25 15.23 — only post25→post40 0.25 static). Margins:
whole post-hoc panel-side worst 0.3503→5.7×, nearest non-panel 10.95→5.5×;
remote receipt TBD (§T35-2).

Script deltas vs `t34-auto.sh` (committed originals untouched; `t35-auto.sh`
is the adapted copy):

| Area | T34 script | T35 script |
|---|---|---|
| Chain | park phase + MENU Cross + mc series to +15 + scpre + ZOE Cross + zc series to +8 + ccpre + CONT Cross + sp series to +8 + sppre + PEAK Cross + pc series to +8 + smpre + RACE Cross + rc series to +8 + sepre + SNOWJAM Cross + sj series to +8 + mrpre + ENTER Cross + mr series to +40 + 6×10 s stab | identical through ENTER Cross; mr series shortened stab to 2×10 s (each + vs-pp score; hops pre→p1, p1→p3, p3→p8, p8→p15, p15→p25, p25→p40, p40→s1, s1→s2) |
| PP park | (arrival was the end) | PP-LIKE settled-panel gate (departed + static ×3 + non-MR; vs-pp scored as remote receipt) + `pppre` snap (vs-pp + vs-mr + titleband) |
| T35 press | — | ONE `XCROSS` (K), arrival series +1/+3/+8/+15/+25/+40 (each titleband + vs-pp), 6 per-hop whole diffs, 6×10 s arrival stability (band + vs-pp in-script; full vs-ref panel post-hoc local) |
| Self-tests | SELF_TEST + SELF_WHOLE + SELF_MENU + SELF_SC + SELF_ZC + SELF_SP + SELF_SM + SELF_SE + SELF_SETAG + SELF_MR | + SELF_PP (whole, < 2.0 bar) + NONMR_MEAN_MIN + is_nonmr() + score_pp() + REFPP_CHECK |
| No-park paths | explicit `NO-PARK` + … + `NO-MR-PARK` | + explicit `NO-PP-PARK` plog, still clean shutdown + `T35_DONE` (trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
port of `t35-cropdiff.py` (`/tmp/t35-fastdiff.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical, only
the mode tag differs) against the committed tool on 4 diverse pairs
(whole panel-panel, whole MR-panel, whole black-panel, whole
cinematic-panel). Any score reproduces with the committed `t35-cropdiff.py`,
slower.

## T35-2. R1 — panel reproduced, Cross → countdown → live gameplay

Run: `t35-auto.sh`, ONE fresh boot, T_BOOT wall 1789973919 (uptime 65,
VM-H14), 06:58:32–07:08:14 UTC (uptime 65→640 = 575 s; 215 s over the
≤6 min guidance — the added X phase + full arrival tail; full dmesg
coverage, zero flaps in-window), WID 2097159 (same as T31 R1 / T32 R1 /
T33 R1 / T33 R2 / T34 R1), exit 0, `T35_DONE`, clean SIGTERM shutdown.
SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC
0.0000/0, SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM 0.0000/0, SELF_SE
0.0000/0, SELF_SETAG 0.0000/0, SELF_MR 0.0000/0, SELF_PP 0.0000/0.
Attempt 1 of ≤3 consumed; attempts 2–3 not needed (Cross advanced,
arrival mapped).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+100, score 0.4331/6 remote / 0.0465/1 PIL (T34 R1: 0.4331/6 / 0.0467/1 — same detector reading, frame differs by 0.0241/0) | Cross 535.3 ms @T+98.03 (attract-skip) + Start 535.5 ms @T+101.30 (on title, ≤1.3 s after exposure) | Main Menu by +4 s; menu-like gate (non-title + whole-static 0.0356/0.0168) + post25-vs-menu 0.3002/5 → park for menu Cross |
| A2–A3 | not run (Cross advanced) | — | — |

### R1 cross-run frame identities (T35 R1 vs T34 R1, full sha256)

| Frame | T35 R1 sha | T34 R1 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `769c641d640f…` (cp-identical, pair 0.0000/0) 58339 B | `d977309dd891…` 58352 B | differ; pair 0.0241/0 max 43 (title timing lottery, nearby phase) |
| a1-post3 | `ac31b36fcdfb…` 50036 B | `45bcb1c63256…` 49966 B | differ; pair 0.0366/0 max 49 |
| a1-post8 | `4a1de2db4431…` 49978 B | `91771d70d2bb…` 50015 B | differ; pair 0.0359/0 max 55 |
| a1-post15 | `4c56f8159c76…` 49634 B | `24187066e1f0…` 49622 B | differ; pair 0.0001/0 max 1 (single-px JPEG shimmer) |
| a1-post25 | `4680fcd0480a…` 49786 B | `4e4e15409746…` 49738 B | differ; pair 0.0215/0 max 43 |
| menupre | `9543989c151e…` 49618 B | `1307199a73f1…` 49628 B | differ; pair 0.0013/0 max 6 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.030/0, 0.078/1, 0.073/2, 0.002/0 |
| scpre | differ | differ | whole pair 0.0709/2 |
| zc-post1/8 | differ | differ | whole pairs 0.081/2, 0.115/3 |
| zc-post3 | `33dee6956278…` 51539 B | `33dee6956278…` 51539 B | BIT-IDENTICAL (`cmp` clean) |
| ccpre | differ | differ | whole pair 0.1235/3 |
| sp-post1/3/8 | differ | differ | whole pairs 0.027/0, 0.053/0, 0.001/0 |
| sppre | differ | differ | whole pair 0.0942/0 |
| pc-post1/3/8 | differ | differ | whole pairs 0.046/0, 0.009/0, 0.041/0 |
| smpre | `d80541a86ebc…` | `4313fd4da4b7…` | whole pair 0.0079/0 |
| rc-post1 | `d86c39d523f9…` 69432 B | `d86c39d523f9…` 69432 B | BIT-IDENTICAL (`cmp` clean) |
| rc-post3/8 | differ | differ | whole pairs 0.0035/0, 0.0965/0 (rc-post8 snowflake shimmer) |
| sepre | `1b9da7e8c45c…` | `c0200fa19c67…` | whole pair 0.0104/0 |
| sj-post1/3/8 | differ | differ | whole pairs 0.037/0, 0.016/0, 0.112/1 |
| mrpre vs T34 `mrpre` | `c23d59754221…` | `9d5331f322e3…` | whole pair 0.0098/0 |
| mr-post1 (load) | `de707d1d5ed5…` 66795 B | `600f33859c9f…` 66681 B | differ; pair 1.1841/47 (both Loading 18%; snowflake/percentage shimmer) |
| mr-post3 (load) | `12cc2598c966…` 67087 B | `e1ad2d6cafe4…` 67499 B | differ; pair 2.0156/64 (97% vs 92% Loading) |
| mr-post8 | `c394b40e0064…` 53943 B | `07c24d0fa0ab…` 21267 B | differ; pair 18.8615/195 (cinematic early frame vs black frame — transition timing lottery) |
| mr-post15 | `46e74f2d4a73…` 59425 B | `dfb74d3b4eda…` 45027 B | differ; pair 15.2534/190 (pre-race panel vs race intro cinematic — panel arrived by +15 this run) |
| mr-post25/40 | differ | differ | whole pairs 0.7828/21, 0.5758/11 (both pre-race panel; AI rider lineup differs run to run) |
| mr-stab1/2 | differ | differ | whole pairs 0.4631/7, 0.4130/7 (both pre-race panel; lineup differs) |
| pppre vs T34 `mr-stab6` | `108024fdc48f…` 59445 B | `11f6801e100c…` 60273 B | whole-vs-panel-ref 0.7416/19 PIL (under the 2.0 gate; lineup differs) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789974017.031690969 → 1789974017.566959155 | 535.3 ms | T+98.03→98.57 | 163 | `a1-now` attract (19.1141/124 remote; 19.1064/124 PIL) | `a1-poll01` TITLE (0.4331/6; 0.0465/1) |
| A1 Start (Return) | 1789974020.298845121 → 1789974020.834301077 | 535.5 ms | T+101.30→101.83 | 166→167 | `a1-pre` ≡ `a1-poll01` (sha `769c641d640f`, TITLE) | `a1-post3` Main Menu (16.2559/139; 16.2578/138) |
| MENU Cross (K) | 1789974059.424231336 → 1789974059.961015459 | 536.8 ms | T+140.42→140.96 | 205→206 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0276/0 PIL; vs-title 16.2610/139) | `mc-post1` Select Character (vs-menu 10.2132/106; vs-sc 0.4306/7; titleband 12.5521/164) |
| ZOE Cross (K) | 1789974099.376434220 → 1789974099.911591092 | 535.2 ms | T+180.38→180.91 | 245→246 | `scpre` Select Character, Zoe selected (vs-sc 0.5975/9 remote; 0.2503/4 PIL; vs-menu 10.1939/105; vs-title 12.6457/164) | `zc-post1` Setup Character (vs-sc 7.2305/100; vs-zc 0.5301/9; titleband 15.9280/128) |
| CONT Cross (K) | 1789974128.088976856 → 1789974128.623613535 | 534.6 ms | T+209.09→209.62 | 274 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4463/8 remote; 0.2130/6 PIL; vs-sc 7.2801/100; vs-title 15.8238/128) | `sp-post1` Select Peak (vs-zc 9.4701/154; vs-sp 0.3731/6; titleband 23.1274/171) |
| PEAK Cross (K) | 1789974156.768758446 → 1789974157.305379969 | 536.6 ms | T+237.77→238.31 | 303 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.4237/6 remote; 0.0788/0 PIL; vs-zc 9.5199/154; vs-title 23.1279/171) | `pc-post1` Select Mode (vs-sp 5.3724/121; vs-sm 0.4115/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789974186.068395563 → 1789974186.604134353 | 535.7 ms | T+267.07→267.60 | 332 | `smpre` Select Mode, Race highlighted (vs-sm 0.3918/6 remote; 0.0409/0 PIL; se-tag 14.3278/89 remote / 14.1390/88 PIL; vs-sp 5.3515/121; vs-title 26.3170/183) | `rc-post1` Select Event (vs-sm 0.8074/11; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789974217.133909115 → 1789974217.669705031 | 535.8 ms | T+298.13→298.67 | 363→364 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6271/11 remote, 0.0094/0 PIL; vs-se 0.4068/6, 0.0364/0; vs-sm 0.8111/11; vs-sp 5.4509/121; vs-title 26.2104/183) | `sj-post1` My Rules (vs-se 10.6339/143; vs-mr 0.4106/7; titleband 9.8525/137) |
| ENTER Cross (K) | 1789974245.780096931 → 1789974246.314562548 | 534.5 ms | T+326.78→327.31 | 392 | `mrpre` My Rules, Continue highlighted (vs-mr 0.3998/7 remote; 0.0796/0 PIL; vs-se 10.6338/143; vs-title 9.8393/137 — viewed) | `mr-post1` game load 18% (vs-mr 12.4898/148; vs-pp 21.0617/169; titleband 17.2808/168 — viewed) |
| XCROSS (K) | 1789974351.046628533 → 1789974351.584564722 | 537.9 ms | T+432.05→432.58 | 497 | `pppre` pre-race panel, X Continue (vs-pp 0.9929/19 remote; 0.7416/19 PIL; vs-mr 19.2959/153; vs-title 34.5233/184 — viewed) | `x-post1` countdown 2, starting gate (vs-pp 14.4887/153; titleband 19.5704/169 — viewed) |

Within-dwell receipts R1: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (1 s resolution) → Start-keydown ≤1.3 s; T33-R2-measured title
persistence 15–17 s ⇒ press inside the window with an order of magnitude
to spare. Start-keyup → MenuCross-keydown 38.6 s; MenuCross-keyup →
ZoeCross-keydown 39.4 s; ZoeCross-keyup → ContCross-keydown 28.2 s;
ContCross-keyup → PeakCross-keydown 28.1 s; PeakCross-keyup →
RaceCross-keydown 28.8 s; RaceCross-keyup → SnowJamCross-keydown 30.5 s;
SnowJamCross-keyup → EnterCross-keydown 28.1 s; EnterCross-keyup →
XCross-keydown 104.7 s (panel settling + PP gate; no dwell pressure — all
parks static, T27 G1 / T28 G1 / T29 G1 / T30 G1 / T31 G1 / T32 G1 / T33 G1 /
T34 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / whole vs panel-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | Whole vs panel | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+96) | 53798B / `c598dcfb7281` | 13.0753/143 | 15.3904/147 | 15.3218/161 | 15.2187/148 | 16.5513/162 | 17.0734/169 | 17.1446/170 | 13.6053/125 | 19.0073/168 | 77.2235/186 | Attract |
| a1-now (T+97, pre-Cross) | 55354B / `ee95996be271` | 19.1064/124 | 15.8715/174 | 15.0044/142 | 16.2059/159 | 16.7523/160 | 16.5324/158 | 16.5910/163 | 14.5782/138 | 15.0430/158 | 104.3010/226 | Attract |
| a1-poll01 (T+100, pre-Start) | 58339B / `769c641d640f` | 0.0465/1 T | 14.1348/151 | 11.3085/152 | 12.2554/146 | 15.3715/156 | 16.1503/158 | 16.2481/160 | 9.7687/142 | 22.1505/183 | 106.6219/205 | TITLE |
| a1-pre (T+100) | 58339B / `769c641d640f` | 0.0465/1 | 14.1348/151 | 11.3085/152 | 12.2554/146 | 15.3715/156 | 16.1503/158 | 16.2481/160 | 9.7687/142 | 22.1505/183 | 106.6219/205 | TITLE (identical cp) |
| a1-post3 (T+104) | 50036B / `ac31b36fcdfb` | 16.2578/138 | 0.0692/1 | 10.1279/105 | 6.9167/93 | 10.4013/170 | 10.9300/177 | 10.9471/177 | 10.0950/96 | 19.3216/178 | 26.1710/106 | Main Menu |
| a1-post8 (T+110) | 49978B / `4a1de2db4431` | 16.2967/138 | 0.0644/1 | 10.1174/105 | 6.9216/93 | 10.3913/170 | 10.9183/177 | 10.9432/177 | 10.0912/96 | 19.3323/178 | 26.1646/106 | Main Menu |
| a1-post15 (T+118) | 49634B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | 10.1073/105 | 6.9081/93 | 10.3855/170 | 10.9184/177 | 10.9433/177 | 10.0761/96 | 19.2985/178 | 26.1710/106 | Main Menu |
| a1-post25 (T+128) | 49786B / `4680fcd0480a` | 16.2622/138 | 0.0451/0 | 10.1195/105 | 6.9113/93 | 10.3911/170 | 10.9242/177 | 10.9320/177 | 10.0871/96 | 19.3018/178 | 26.1708/106 | Main Menu |
| menupre (T+138, pre-MCross) | 49618B / `9543989c151e` | 16.2622/138 | 0.0276/0 | 10.1076/105 | 6.9078/93 | 10.3848/170 | 10.9177/177 | 10.9427/177 | 10.0751/96 | 19.2994/178 | 26.1473/106 | Main Menu, Single Event highlighted |
| mc-post1 (T+141) | 70283B / `66b1c9287cf2` | 12.4799/163 | 10.1448/105 | 0.0699/1 | 7.2450/101 | 11.3760/158 | 11.8422/158 | 11.9110/158 | 5.6411/117 | 19.4439/172 | 26.5706/90 | Select Character, Zoe |
| mc-post3 (T+146) | 70526B / `79fc3a7b9ff7` | 12.4847/163 | 10.1605/107 | 0.0852/1 | 7.2651/100 | 11.4025/158 | 11.8670/157 | 11.9355/157 | 5.6638/117 | 19.4712/172 | 26.5705/90 | Select Character |
| mc-post8 (T+154) | 70306B / `15ded98810a3` | 12.4587/163 | 10.1464/105 | 0.2596/5 | 7.2192/100 | 11.3565/158 | 11.8210/157 | 11.8965/157 | 5.6292/117 | 19.4427/172 | 26.5695/90 | Select Character |
| mc-post15 (T+163) | 69989B / `4113a3dd1727` | 12.4587/163 | 10.1276/105 | 0.0718/1 | 7.2157/100 | 11.3486/158 | 11.8125/157 | 11.8815/157 | 5.6116/117 | 19.4161/172 | 26.6085/90 | Select Character |
| scpre (T+177, pre-ZCross) | 70171B / `91b9acf5e625` | 12.5672/163 | 10.1268/105 | 0.2503/4 | 7.2284/100 | 11.3490/158 | 11.8264/157 | 11.8976/157 | 5.6274/117 | 19.4519/172 | 26.5695/90 | Select Character, Zoe selected |
| zc-post1 (T+181) | 51516B / `33a6c8b116ff` | 15.9045/129 | 6.9257/93 | 7.2028/100 | 0.2981/7 | 9.3659/153 | 10.1372/164 | 10.2486/164 | 7.0486/103 | 20.1904/164 | 15.2978/91 | Setup Character, Zoe |
| zc-post3 (T+186) | 51539B / `33dee6956278` | 15.8335/128 | 6.9112/92 | 7.2663/101 | 0.2328/6 | 9.3474/153 | 10.1084/165 | 10.2215/165 | 7.0550/103 | 20.1795/164 | 15.3015/91 | Setup Character |
| zc-post8 (T+194) | 51351B / `ed106a08384e` | 15.8302/128 | 6.9325/92 | 7.1008/100 | 0.2429/6 | 9.3809/153 | 10.1318/164 | 10.1920/164 | 7.0876/104 | 20.1510/164 | 15.2878/91 | Setup Character |
| ccpre (T+206, pre-ContCross) | 51447B / `6bf639b9e85e` | 15.8007/128 | 6.9062/93 | 7.2546/100 | 0.2130/6 | 9.3576/153 | 10.1163/164 | 10.2274/164 | 7.0408/103 | 20.1829/164 | 15.3344/91 | Setup Character, Zoe + Continue |
| sp-post1 (T+210) | 65313B / `9f9a8e703b05` | 23.1257/171 | 10.4258/170 | 11.3476/158 | 9.3898/153 | 0.0267/0 | 5.2219/121 | 5.3307/121 | 9.8201/138 | 16.5632/157 | 14.0031/89 | Select Peak, Peak 1 |
| sp-post3 (T+215) | 65385B / `38544d0af8c` | 23.1259/171 | 10.4368/170 | 11.3798/158 | 9.3820/153 | 0.0459/0 | 5.2456/121 | 5.3481/121 | 9.8664/138 | 16.5796/158 | 14.0026/89 | Select Peak |
| sp-post8 (T+222) | 65247B / `774f16718db8` | 23.1273/171 | 10.4061/170 | 11.3503/158 | 9.3728/153 | 0.0046/0 | 5.2067/121 | 5.3099/121 | 9.8373/138 | 16.5443/157 | 14.0026/89 | Select Peak |
| sppre (T+235, pre-PeakCross) | 65743B / `73c7218d007b` | 23.1259/171 | 10.4751/170 | 11.4185/158 | 9.4410/153 | 0.0788/0 | 5.2791/121 | 5.3593/121 | 9.9068/138 | 16.5707/157 | 14.0026/89 | Select Peak, Peak 1 highlighted |
| pc-post1 (T+239) | 67567B / `4545eb2c8828` | 26.3046/183 | 10.9354/178 | 11.8226/157 | 10.1207/164 | 5.2067/121 | 0.0643/0 | 0.4754/6 | 10.4833/143 | 16.4214/160 | 14.1329/88 | Select Mode, Race |
| pc-post3 (T+243) | 67442B / `66b5308d1c93` | 26.3046/183 | 10.9145/178 | 11.8039/157 | 10.1013/164 | 5.1819/121 | 0.0405/0 | 0.5118/9 | 10.4634/143 | 16.4137/160 | 14.1497/88 | Select Mode |
| pc-post8 (T+251) | 67631B / `a7536c6f5841` | 26.3184/183 | 10.9393/178 | 11.8033/157 | 10.1243/164 | 5.2094/121 | 0.0660/1 | 0.5397/12 | 10.4496/143 | 16.4393/160 | 14.1642/88 | Select Mode |
| smpre (T+263, pre-RaceCross) | 67471B / `d80541a86ebc` | 26.3046/183 | 10.9150/178 | 11.8049/157 | 10.1023/164 | 5.1823/121 | 0.0409/0 | 0.5124/9 | 10.4651/143 | 16.4145/160 | 14.1390/88 | Select Mode, Race highlighted |
| rc-post1 (T+268) | 69432B / `d86c39d523f9` | 26.1964/183 | 10.9382/178 | 11.8584/157 | 10.2158/164 | 5.2819/121 | 0.5095/9 | 0.0312/0 | 10.5897/144 | 16.4267/160 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+272) | 69412B / `f7ad3226d405` | 26.2007/183 | 10.9401/178 | 11.8582/157 | 10.2161/164 | 5.2832/121 | 0.5118/9 | 0.0336/0 | 10.5896/144 | 16.4272/160 | 0.0094/0 | Select Event |
| rc-post8 (T+280) | 69798B / `80dca191a8a5` | 26.1964/183 | 10.9965/178 | 11.9187/157 | 10.2755/164 | 5.3447/121 | 0.5722/13 | 0.0955/0 | 10.6489/144 | 16.4395/161 | 0.0094/0 | Select Event |
| sepre (T+293, pre-SnowJamCross) | 69524B / `1b9da7e8c45c` | 26.1964/183 | 10.9422/178 | 11.8624/157 | 10.2196/164 | 5.2871/121 | 0.5147/10 | 0.0364/0 | 10.5935/144 | 16.4308/160 | 0.0094/0 | Select Event, Snow Jam highlighted |
| sj-post1 (T+299) | 58556B / `1d06f97ddac8` | 9.8274/135 | 10.0786/96 | 5.6083/117 | 7.0498/104 | 9.8197/137 | 10.4258/143 | 10.5898/143 | 0.0948/1 | 19.5376/153 | 26.4126/92 | My Rules, Continue |
| sj-post3 (T+304) | 58499B / `17887882bde0` | 9.8145/135 | 10.0836/96 | 5.6123/117 | 7.0533/104 | 9.8204/137 | 10.4295/143 | 10.5934/143 | 0.0843/1 | 19.5281/152 | 26.4832/92 | My Rules |
| sj-post8 (T+311) | 58884B / `2b4bf36954bc` | 9.8722/136 | 10.1167/99 | 5.6506/117 | 7.0792/104 | 9.8671/137 | 10.4754/143 | 10.6393/143 | 0.1437/2 | 19.5825/154 | 26.4115/92 | My Rules |
| mrpre (T+324, pre-EnterCross) | 58501B / `c23d59754221` | 9.8145/135 | 10.0797/96 | 5.6086/117 | 7.0495/104 | 9.8168/137 | 10.4259/143 | 10.5899/143 | 0.0796/0 | 19.5256/152 | 26.4139/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+328) | 66795B / `de707d1d5ed5` | 17.2333/167 | 15.2283/157 | 14.2067/157 | 13.6711/152 | 14.7146/153 | 15.0815/152 | 15.2094/153 | 12.4617/148 | 21.0504/169 | 83.2100/222 | Loading 18% (viewed) |
| mr-post3 (T+332) | 67087B / `12cc2598c966` | 17.3797/170 | 15.1828/157 | 14.1206/157 | 13.5870/152 | 14.6233/152 | 14.9917/152 | 15.1189/153 | 12.3772/147 | 21.0299/168 | 80.1358/217 | Loading 97% (viewed) |
| mr-post8 (T+340) | 53943B / `c394b40e0064` | 29.3823/237 | 21.2340/219 | 20.9135/197 | 21.0428/190 | 20.6994/219 | 21.4776/219 | 21.3848/219 | 20.3339/197 | 19.1838/190 | 51.6618/162 | Race intro cinematic, gate close-up, EA RADIO BIG / Buffet of Breaks / John Morgan (viewed) |
| mr-post15 (T+350) | 59425B / `46e74f2d4a73` | 34.5145/184 | 19.0099/177 | 19.1246/172 | 19.8779/162 | 16.3454/157 | 16.1565/159 | 16.1580/159 | 19.2904/153 | 0.7466/19 | 48.5040/133 | Pre-race panel (viewed) |
| mr-post25 (T+363) | 59872B / `5fc971e36753` | 34.5127/184 | 19.4054/178 | 19.4742/172 | 20.2518/164 | 16.5916/157 | 16.4876/161 | 16.4883/160 | 19.6524/153 | 0.4575/7 | 48.5040/133 | Pre-race panel |
| mr-post40 (T+381) | 59504B / `dcfa2ff8fa24` | 34.5153/184 | 19.0727/177 | 19.1796/172 | 19.9291/162 | 16.3686/157 | 16.2109/159 | 16.2123/159 | 19.3387/153 | 0.6798/16 | 48.5040/133 | Pre-race panel |
| mr-stab1 (T+404) | 59784B / `5278834a7527` | 34.5141/184 | 19.3127/178 | 19.3914/172 | 20.1605/164 | 16.5211/157 | 16.4074/160 | 16.4084/160 | 19.5628/153 | 0.4288/7 | 48.5040/133 | Pre-race panel |
| mr-stab2 (T+416) | 59711B / `66c2e7c54397` | 34.5129/184 | 19.2925/178 | 19.3737/172 | 20.1369/164 | 16.5030/157 | 16.3963/160 | 16.3974/160 | 19.5399/153 | 0.4485/7 | 48.5040/133 | Pre-race panel |
| pppre (T+429, pre-XCross) | 59445B / `108024fdc48f` | 34.5184/184 | 19.0165/177 | 19.1295/172 | 19.8777/162 | 16.3441/157 | 16.1680/159 | 16.1695/159 | 19.2909/153 | 0.7416/19 | 48.5040/133 | Pre-race panel, X Continue (viewed) |
| x-post1 (T+433) | 69186B / `c6f732d3dfe4` | 19.5637/168 | 16.0264/163 | 14.0376/137 | 15.8714/152 | 15.6590/156 | 15.7747/157 | 15.8782/158 | 13.3434/129 | 14.4394/153 | 93.3207/174 | Countdown 2, starting gate, 00:00:00, 0 MPH (viewed) |
| x-post3 (T+437) | 69406B / `56d638453c12` | 24.7533/158 | 14.6340/158 | 13.7764/137 | 13.3705/149 | 13.4936/148 | 13.7440/149 | 13.8254/150 | 13.0729/124 | 15.2188/139 | 23.4954/99 | 4TH/6, 00:00:01, 37 MPH (viewed) |
| x-post8 (T+444) | 67887B / `9f8d96a71ff9` | 12.3056/123 | 16.5344/149 | 13.1877/144 | 14.4854/154 | 15.9490/158 | 16.6981/157 | 16.8172/158 | 11.6526/115 | 21.1561/165 | 97.6913/181 | 5TH/6, 00:00:09, 4%, 37 MPH (viewed) |
| x-post15 (T+452) | 64066B / `621c556a918e` | 16.4107/165 | 17.2790/143 | 13.7313/140 | 14.2705/146 | 15.8988/154 | 16.7449/156 | 16.8328/158 | 12.2900/118 | 21.2747/169 | 93.1418/174 | 2ND/6, 00:00:21, 11%, 50 MPH, airborne (viewed) |
| x-post25 (T+464) | 59573B / `d6d897fa9d24` | 21.4626/124 | 15.2687/128 | 13.7614/137 | 13.3100/134 | 14.9617/128 | 14.8887/131 | 14.9736/133 | 11.9187/119 | 17.2883/150 | 71.5664/158 | 1ST/6, 00:00:38, 20%, 51 MPH, 1350, COMBO +742 (viewed) |
| x-post40 (T+481) | 75093B / `36482081555d` | 21.8311/161 | 13.5427/141 | 12.7895/160 | 11.7666/141 | 13.9149/151 | 13.9249/151 | 14.0398/153 | 11.4300/135 | 18.7797/166 | 36.9661/127 | 1ST/6, 00:01:00, 31%, 35 MPH, 1350 (viewed) |
| x-stab1 (T+503) | 63180B / `02027d45e751` | 22.4316/121 | 15.4013/144 | 14.3464/133 | 13.3689/128 | 14.1033/143 | 14.5673/143 | 14.6633/144 | 12.9334/122 | 17.3360/161 | 25.5278/106 | 2ND/6, 00:01:32, 47%, 43 MPH, 1350 (viewed) |
| x-stab2 (T+515) | 55310B / `1c44aada9de5` | 19.2865/107 | 14.8131/128 | 14.7027/131 | 14.4671/136 | 15.7730/132 | 16.0520/135 | 16.0743/135 | 14.1628/132 | 13.7566/117 | 43.6953/125 | 1ST/6, 00:01:48, 53%, 45 MPH, 3540 (viewed) |
| x-stab3 (T+527) | 59861B / `aad945baacb0` | 26.3414/139 | 16.1823/144 | 16.7671/150 | 16.2484/145 | 15.9625/145 | 15.9360/147 | 15.9485/146 | 16.4188/142 | 12.9760/129 | 22.7317/93 | 3RD/6, 00:02:03, 59%, 50 MPH, 4330, FS Rail (viewed) |
| x-stab4 (T+539) | 52921B / `53a7f26da281` | 12.1579/105 | 15.7777/153 | 13.5160/135 | 14.0332/133 | 16.5916/160 | 17.1785/160 | 17.3020/160 | 11.7837/128 | 17.8789/136 | 80.2995/160 | 4TH/6, 00:02:21, 67%, 32 MPH, 4330 (viewed) |
| x-stab5 (T+551) | 62886B / `6f035d777250` | 12.4878/127 | 14.7144/135 | 11.5645/126 | 12.1438/128 | 13.7148/141 | 14.3834/141 | 14.4671/141 | 9.9785/113 | 18.1180/151 | 79.2204/171 | 4TH/6, 00:02:38, 75%, 48 MPH, 4330 (viewed) |
| x-stab6 (T+563) | 64762B / `e8ecf69fae96` | 14.6725/135 | 14.0428/128 | 12.0648/133 | 12.3988/132 | 15.0866/153 | 15.0910/154 | 15.1859/154 | 10.8325/115 | 20.3120/185 | 76.5384/156 | 4TH/6, 00:02:52, 84%, 37 MPH, 4330 (viewed) |

In-script (remote) vs PIL agreement: ≤0.17 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr scores at scale (e.g. pppre band 34.5233 vs
34.5184; pppre vs-mr 19.2959 vs 19.2909; x-post1 vs-pp 14.4887 vs
14.4394); the known ~3–11× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.3998/7 remote vs 0.0796/0 PIL ≈ 5×; sepre vs-se 0.4068/6
vs 0.0364/0 ≈ 11× — T27 title / T28 menu / T29 SC / T30 ZC / T31 SP /
T32 SM / T33 SE / T34 MR precedent); hops ≤0.06. New: the vs-panel
remote receipt reads 0.69–1.00/p99 9–19 on panel-side PIL 0.43–0.75
(≈1.3–1.6× inflation at the ~0.5 scale — milder than the ~3–5× seen at
the ~0.1 scale), so the < 2.0 whole bar holds even remotely (worst
remote 0.9968, 2.0× margin). The TAG crop gap re-confirmed at ~280×
(2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated
in PIL transfer to remote with single-digit inflation near zero and ~1×
at scale ≥5; text-dense crops need remote receipts or generous bars.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1179 | 10.1244/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1074 | 0.1346/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2996 | 0.3244/8 | same screen |
| post8 → post15 (mc) | 0.2232 | 0.2446/5 | same screen |
| post15 → scpre (park span) | — | 0.2367/4 | same screen |
| scpre → zc-post1 | 7.2495 | 7.2720/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.3043 | 0.3273/9 | arrival settling |
| post3 → post8 (zc) | 0.2904 | 0.3113/7 | same screen |
| post8 → ccpre (park span) | — | 0.3146/8 | same screen |
| ccpre → sp-post1 | 9.3228 | 9.3606/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0595 | 0.0659/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0391 | 0.0428/0 | same screen |
| post8 → sppre (park span) | — | 0.0757/0 | same screen |
| sppre → pc-post1 | 5.2290 | 5.2536/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0334 | 0.0370/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0358 | 0.0407/0 | same screen |
| post8 → smpre (park span) | — | 0.0411/0 | same screen |
| smpre → rc-post1 | 0.4560 | 0.4815/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps in T32/T33) |
| post1 → post3 (rc) | 0.0014 | 0.0024/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0641 | 0.0668/0 | same screen (rc-post8 snowflake shimmer; still SE: se-tag 0.0094) |
| post8 → sepre (park span) | — | 0.0696/0 | same screen |
| sepre → sj-post1 | 10.5472 | 10.5703/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.0308 | 0.0353/0 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.0760 | 0.0839/1 | same screen |
| post8 → mrpre (park span) | — | 0.0795/0 | same screen |
| mrpre → mr-post1 | 12.4577 | 12.4198/148 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 1.4407 | 1.4597/57 | loading progress 18% → 97% |
| post3 → post8 (mr) | 25.2533 | 25.2697/253 | loading screen → race intro cinematic (no black frame captured this run — transition timing lottery) |
| post8 → post15 (mr) | 19.2427 | 19.2404/190 | cinematic → pre-race panel (panel arrived by +15, one sample early vs T34) |
| post15 → post25 (mr) | 0.4364 | 0.4416/20 | same screen (panel shimmer/animation) |
| post25 → post40 (mr) | 0.3690 | 0.3757/17 | same screen |
| post40 → stab1 (mr) | 0.2715 | 0.2796/12 | same screen |
| stab1 → stab2 (mr) | 0.0435 | 0.0530/1 | same screen |
| stab2 → pppre (park span) | — | 0.3126/14 | same screen |
| pppre → x-post1 | 14.1920 | 14.1757/152 | screen change within +1 s (pre-race panel → countdown/gate; decisive hop) |
| post1 → post3 (x) | 14.0000 | 13.9855/124 | countdown → live gameplay (gate → slope) |
| post3 → post8 (x) | 14.9899 | 15.0396/123 | live gameplay motion |
| post8 → post15 (x) | 7.9162 | 7.9696/118 | live gameplay motion |
| post15 → post25 (x) | 11.4682 | 11.5189/121 | live gameplay motion |
| post25 → post40 (x) | 9.4272 | 9.5056/106 | live gameplay motion |
| post40 → xstab1 | — | 11.3956/121 | live gameplay motion |
| xstab1 → xstab2 | — | 11.5159/177 | live gameplay motion |
| xstab2 → xstab3 | — | 8.5116/102 | live gameplay motion |
| xstab3 → xstab4 | — | 15.1424/133 | live gameplay motion |
| xstab4 → xstab5 | — | 8.5006/116 | live gameplay motion |
| xstab5 → xstab6 | — | 9.2771/138 | live gameplay motion |
| post1 → stab6 (x span) | — | 12.9056/162 | endpoints differ (gate → mid-race) |
| post1 → stab2 (mr span) | — | 20.9550/168 | endpoints differ (load → panel) |

### R1 arrival park (pre-race panel)

| Item | Value |
|---|---|
| Post-Enter frames | `t35r1-mr-post1.jpg` @T+328 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 18% Loading…; `mr-post3` @T+332: same screen, 97% Loading…; `mr-post8` @T+340: race intro cinematic, starting-gate close-up (`EA RADIO BIG / Buffet of Breaks / John Morgan` overlay); `mr-post15` @T+350: pre-race panel = arrival (one sample early vs T34's +25) |
| Stability N (panel) | 6 snaps (post15/25/40 + stab1/2 + pppre) spanning T+350→T+429 (79 s) |
| Whole-frame pairwise (PIL) | 0.0477–0.4432/p99 ≤20 across all 15 pairs (panel shimmer/animation; min post15–pppre 0.0477/1, max post25–pppre 0.4432/20; JPEG shas distinct) |
| Vs-panel-ref (whole) | 0.43–0.75/p99 7–19 across all 6 (all under the 2.0 gate; margins 2.7–4.7×) |
| Vs-MR (whole) | 19.29–19.65/p99 153 across all 6 (not My Rules) |
| Vs-SE (whole) | 16.16–16.49/p99 159–161 across all 6 (not Select Event) |
| Vs-SM (whole) | 16.16–16.49/p99 159–161 across all 6 (not Select Mode) |
| Vs-SP (whole) | 16.34–16.59/p99 157 across all 6 (not Select Peak) |
| Vs-ZC (whole) | 19.88–20.25/p99 162–164 across all 6 (not Setup Character) |
| Vs-SC (whole) | 19.12–19.47/p99 172 across all 6 (not Select Character) |
| Vs-menu (whole) | 19.01–19.41/p99 177–178 across all 6 (not menu) |
| Vs-title (band) | 34.51–34.52/p99 184 across all 6 (not title) |
| SE-TAG (crop) | 48.5040/133 identical across all 6 (tagline band static within run; T34's run read 50.8209/132 — run-dependent, lineup/background phase) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Kaori / Brodi / Viggo / Elise / Griff` (AI lineup differs from T34's `Zoe / Viggo / Psymon / Eddie / Allegra / Moby` — run to run); `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 79 s (all 6 snaps pre-race panel) |

### R1 arrival (countdown → live gameplay; ZERO further input after XCROSS)

| Snap (wall T+) | Race clock | Position | Progress | Speed | Score | Notes |
|---|---|---|---|---|---|---|
| x-post1 (T+433, +0.4 s after keyup) | 00:00:00 | gates | — | 0 MPH | — | countdown `2` over the starting gate; riders in gates |
| x-post3 (T+437) | 00:00:01 | 4TH/6 | — | 37 MPH | — | leaving the gate, slope + ski-jump arena |
| x-post8 (T+444) | 00:00:09 | 5TH/6 | 4% | 37 MPH | — | open slope, mountains |
| x-post15 (T+452) | 00:00:21 | 2ND/6 | 11% | 50 MPH | — | airborne off a jump |
| x-post25 (T+464) | 00:00:38 | 1ST/6 | 20% | 51 MPH | 1350 | COMBO +742 |
| x-post40 (T+481) | 00:01:00 | 1ST/6 | 31% | 35 MPH | 1350 | ridge traverse, billboards |
| x-stab1 (T+503) | 00:01:32 | 2ND/6 | 47% | 43 MPH | 1350 | forest section |
| x-stab2 (T+515) | 00:01:48 | 1ST/6 | 53% | 45 MPH | 3540 | rider-down slide pose, still 1st |
| x-stab3 (T+527) | 00:02:03 | 3RD/6 | 59% | 50 MPH | 4330 | `FS Rail` trick label |
| x-stab4 (T+539) | 00:02:21 | 4TH/6 | 67% | 32 MPH | 4330 | canyon gates |
| x-stab5 (T+551) | 00:02:38 | 4TH/6 | 75% | 48 MPH | 4330 | banked turn, MERCURY/do! boards |
| x-stab6 (T+563, +130.4 s after keyup) | 00:02:52 | 4TH/6 | 84% | 37 MPH | 4330 | resort base area; race still running (record 02:57) |

Race-clock vs wall-clock (wall since XCROSS keyup 1789974351.585; race
clock read off HUD, HH:MM:SS):

| Snap | Wall since keyup (s) | Race clock (s) | Ratio |
|---|---|---|---|
| x-post1 | 0.4 | 0 | — (countdown) |
| x-post3 | 4.4 | 1 | 0.23 |
| x-post8 | 11.4 | 9 | 0.79 |
| x-post15 | 19.4 | 21 | 1.08 |
| x-post25 | 31.4 | 38 | 1.21 |
| x-post40 | 48.4 | 60 | 1.24 |
| x-stab1 | 70.4 | 92 | 1.31 |
| x-stab2 | 82.4 | 108 | 1.31 |
| x-stab3 | 94.4 | 123 | 1.30 |
| x-stab4 | 106.4 | 141 | 1.33 |
| x-stab5 | 118.4 | 158 | 1.33 |
| x-stab6 | 130.4 | 172 | 1.32 |

Stability N (X): not a static arrival — 12 snaps over 130 s, all 66
whole-frame pairs 7.97–20.23/p99 ≤186 (live gameplay motion; min
x-post8–x-post15 7.9696/118, max x-post15–x-stab3 20.2332/186; JPEG shas
distinct). Vs-panel-ref 12.98–21.27 across all 12 (decisively non-panel);
vs-MR 9.98–16.42 (non-MR). No reclaim to any menu/panel in 130 s (all 12
snaps countdown/live gameplay, positions/progress/timer all advancing).

### R1 PP-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Departure mrpre→post1 | 12.4577 | > 5.0 | yes |
| Arrival static p25→p40 | 0.3690 | < 1.0 | yes |
| Arrival static p40→s1 | 0.2715 | < 1.0 | yes |
| Arrival static s1→s2 | 0.0435 | < 1.0 | yes → `PP-LIKE`, X-Continue Cross pressed |
| Non-MR (stab2 vs-mr) | 19.5477/153 | > 5.0 | yes |
| Vs-pp receipt (post15/25/40) | 0.9968/19, 0.7198/9, 0.9281/16 | (not a leg — receipt) | tabled (≈1.3–1.6× vs PIL 0.43–0.75; under 2.0 even remotely) |
| Vs-pp receipt (stab1/2) | 0.6902/9, 0.7066/9 | (not a leg — receipt) | tabled |
| Vs-pp receipt (pppre) | 0.9929/19 | (not a leg — receipt) | tabled (≈1.3× vs PIL 0.7416) |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Arrival park reproduced (snap match vs T34's `t34r1-mr-stab6.jpg`) | post15/25/40 + stab1/2 + pppre whole-vs-stab6 0.4288–0.7466/p99 7–19 (all under the 2.0 gate); 2 chain frames bit-identical to T34 R1's run (zc-post3, rc-post1) |
| Cross acted on it (pre-press = pre-race panel, X Continue) | `pppre` vs-pp 0.9929/19 remote, 0.7416/19 PIL; viewed: pre-race panel, `Snow Jam - Race / Single Event`, riders Zoe/Kaori/Brodi/Viggo/Elise/Griff, `Record time: 02:57`, `X Continue` |
| Next-screen snaps + stability N | 12 post-press snaps; countdown `2` at +0.4 s, live gameplay from +4 s, race 4TH/6 at 84% by +130 s with zero further input; pairwise 7.97–20.23 (motion, not static) |
| Full input log + trace sha | `t35r1-poll.log` (145 lines: every score + press, walls + uptimes) + trace `e337f8e8…60865` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32/T33/T34 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725,
first vblank L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks
397 frozen (all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not
changed`; clean tail @564.8699. Census: EE 12,280,595 (52, set-identical
to T34 R1) · IOP 20,345,512 (155, set-identical to T34 R1 — countdown +
gameplay arrival adds no new called API) · `libsd.006: sceSdGetParam`
26065 (T34: 1963); `sceSdGetAddr` 4,077,648 (T34: 3,391,248).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R1 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate → SnowJam Cross → MR-LIKE gate → Enter Cross → PP-LIKE settled-panel gate) |
| Cross on X Continue? | YES (XCROSS @T+432.05 R1, pre-press = pre-race panel, X Continue) |
| Next screen reached? | YES (countdown `2` @T+433 → live gameplay by T+437 → race at 84%, 4TH/6 @T+563, still running) |
| Bounded variant? | none needed (first X press provably acted on the pre-race panel) |
| 1200 s cap | Not reached — R1 ≈ T+575; attempts 2–3 unexercised |
| Chain end | Live Snow Jam race (4TH/6, 84%, 00:02:52) with no further input; race not yet finished at capture end |

## T35-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t35 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules → Cross → game load → cinematic → pre-race panel → Cross → countdown → live gameplay, T+~575) | 45,495,816 / 2,919,779,317 | `e337f8e8304eba0ca963302e0234737e35938ace54a7775417b5bc2dafc60865` (analyze-sha on H14 = post-restart re-verify on H15 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t35r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t35r1-trace-head.txt` 149019 B sha `78fb01a63e47…`, `t35r1-trace-tail.txt` 128538 B sha `b4d618611e1d…`) |
| `emulog-pre-t35-20260921T065839Z.txt` = t34 R1 (preserved at R1 boot) | — / 2,526,769,871 | `e7b19750893380b1cbf802cb1011a293ebe4be5da8fbeeed3c370a4bee4d13a9` (re-verified post-run: matches T34) | bytesize-only (T34 precedent; SSD holds T34's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 12,280,595 (52
distinct, set-identical to T34 R1) · IOP 20,345,512 (155, set-identical
to T34 R1) · vblanks 397. Committed: `t35r1-census.txt` (11697 B sha
`549585b76f04…`), `t35r1-samples.txt` (5865 B sha `4729e70068c3…`),
`t35r1-poll.log` (145 lines, 8863 B sha `15ed4a0abc55…`),
`t35r1-stdout.txt` (398 lines, 25968 B),
`t35r1-stderr.txt` (full `set -x` shell trace, 2329 lines, 127877 B),
`t35r1-trace-head.txt` / `t35r1-trace-tail.txt`.
Trace-head note: same 149019 B as T34 R1's head but sha differs
(`78fb01a6…` vs `5a0e8140…`) — timestamp/number-stripped content differs
in exactly 1/2000 lines (`gl_programs.idx` cache entries: 240 vs 173 —
shader cache growth across runs); all other stripped lines identical.

## T35-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H13 …3630
ssh bytesize 'wsl dmesg' > /tmp/t35-dmesg-pre.txt                     # 417 lines, 0 AcceptAsync (H13)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t35-eventlog-pre.txt  # head 02:53:50
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm …t30-ref-zc.ppm …t31-ref-sp.ppm …t32-ref-sm.ppm …t33-ref-se.ppm …t34-ref-mr.ppm'  # all 8 refs reproduce
ssh bytesize 'wsl df -h / /tmp'                                       # 887G avail (split: no pipes inline)
ssh bytesize 'wsl df -h /mnt/c'                                       # C: 14G avail
ssh bytesize 'wsl du -sh …/logs/'                                     # 26G
ssh bytesize 'wsl ls …/logs/' > /tmp/t35-logs-list.txt                 # 22 emulogs
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …/logs/emulog.txt'  # e7b19750… T34R1 live
# T34 ref snaps (local): 12/12 full-sha256+sizes reproduce T34 §T34-2
# panel ref + calibration (local; t35-cropdiff.py = T34 copy, byte-identical)
python3 -c "Image.open(mr-stab6).convert('RGB').save('/tmp/t35-ref-panel.ppm')"  # ref 3932177 B 192e0472…
python3 /tmp/t35-fastdiff.py <valid 4/4 exact vs t35-cropdiff.py>
python3 /tmp/t35-calib.py  # 8 panel + MR/SE/SM/SP/ZC/SC/menu/title/2 attract/load18/load92/black/cine, whole vs panel-ref
# -> WHOLE panel-panel 0.0000-0.3503/p99 0-16, nearest attract 10.95/141; post-hoc bar < 2.0 (5.7x/5.5x)
# adapt t35-auto.sh from the T34 copy (PP gate + XCROSS + x arrival; bash -n), t35-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t35-auto.sh t35-analyze.sh t35-vcount.sh t35-cropdiff.py /tmp/t35-ref-panel.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t35-… /home/brad/pcsx2-t4/; sha256sum …'  # 192e0472…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H14
ssh bytesize 'wsl python3 …/t35-cropdiff.py …REFPP …'                  # 0.0000/0 PPM
ssh bytesize 'wsl python3 …/t35-cropdiff.py …REFMR …'                  # 0.0000/0 PPM
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H14 …3853 (H13→H14 restart mid-session)
ssh bytesize 'wsl sha256sum …/t35-auto.sh …/t35-ref-panel.ppm …/t34-ref-mr.ppm; ls …'  # staged shas survive restart
ssh bytesize 'wsl -u root mount …; ls …'                              # re-mount on H14
ssh bytesize 'wsl dmesg' > /tmp/t35-dmesg-preH14.txt                  # 473 lines, 1 AcceptAsync [32.29] (H14)
# R1 (ONE ssh; exit 0; PP-LIKE → XCROSS → countdown → live gameplay)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t35-auto.sh' > /tmp/t35r1-run-stdout.txt 2>/tmp/t35r1-run-stderr.txt  # T35_DONE, up 65→640
ssh bytesize 'wsl dmesg' > /tmp/t35-dmesg-post-r1.txt                 # IMMEDIATELY after run ssh: 482 lines, 2 AcceptAsync (H14, full R1 coverage)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H14 …3853 still
ssh bytesize 'wsl bash …/t35-analyze.sh'                              # e337f8e8…, 45495816 L
ssh bytesize 'wsl bash …/t35-vcount.sh'                                # 397 frozen (all ≤90)
ssh bytesize 'wsl grep -c LoadStartModule …'                           # 18
ssh bytesize 'wsl wc -l …/t35-poll.log'                                # 145
ssh bytesize 'wsl ls …/t35-*.jpg'                                      # 55 JPGs (title at poll01)
ssh bytesize 'wsl cp <30 chain jpg> /mnt/c/…'                          # (explicit list, one wsl call)
ssh bytesize 'wsl cp <25 mr/x jpg + poll.log + census/samples> /mnt/c/…'  # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t35-…" /tmp/t35-fetch/                         # 55 jpg + logs (r1-prefixed local)
# R1 post-hoc (local fastdiff): chain panel, xrun pairs, 15 panel pairs, 66 X pairs, census set-compare
ssh bytesize 'wevtutil …' > /tmp/t35-eventlog-post.txt                # head H14-teardown 03:13:19; H13→H14 02:56:15/02:57:33; 2 Volsnap in-window, 0 VmSwitch
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H15 …5378 (fresh, created by this call)
ssh bytesize 'wsl sha256sum …/bios/….nvm; ls -la …/bios/…'             # da021d2a… untouched
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …/logs/emulog.txt'  # e337f8e8… re-verified
ssh bytesize 'wsl ls …/logs/' > /tmp/t35-logs-post.txt                 # 23 emulogs (rotation +1)
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t35-20260921T065839Z.txt; ls -la …'  # e7b19750… T34R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t35r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t35r1-trace-tail.txt         # 2000 lines, clean tail @564.8699
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t35r1.txt; ls -la …'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t35r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t35r1.txt"         # e337f8e8… match
ssh bytesize 'wsl dmesg' > /tmp/t35-dmesg-post-h15.txt                # 545 lines, 4 AcceptAsync (H15)
ssh bytesize 'wsl df -h / /mnt/c; du -sh …/logs/'                      # 884G / C: 13G / 29G
# report (chunks; receipts include tail -3)
cp /tmp/t35-dmesg-*.txt /tmp/t35-eventlog-*.txt /tmp/t35r1-run-stdout.txt … local/research/T35/  # renamed per §evidence
tail -3 local/research/T35/REPORT.md
git add -f local/research/T35/<73 files by name>                      # ignored dir, forced
git commit -m "[T35] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T35-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (live race) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate (departed + non-SE + static) → Cross on Continue → PP-LIKE settled-panel gate (departed + static ×3 + non-MR) → ≤3 attempts) → pre-race panel (`Snow Jam - Race`, `X Continue`); then a single 534 ms Cross (X Continue) to start the race; the race runs input-free (R1: countdown `2` at +0.4 s, live gameplay from +4 s, 84% at +130 s with zero steering, race clock ~1.3× wall under turbo). Next: either capture the race finish (extend the tail past 84% — record time 02:57 suggests ~15–20 s more race clock) or map the first steering input (single D-pad/analog nudge and its HUD effect). Gate note: the panel→countdown whole-frame hop is decisive (~14.18–14.19 remote/PIL), so DEPARTED > 5.0 fires normally on the X transition; but live gameplay is never static (all 66 arrival pairs 7.97–20.23), so any post-X gate must key on HUD content (race clock / position / progress) rather than static/whole-frame arrival criteria — gate on the HUD, not the frame. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | Zero in-window flaps this session + 1 pre-session + 1 mid-session + 1 post-everything restart (all not by me) | 0 userland kills on any VM this session; AcceptAsync exact counts 0/1/2/4 across the 4 committed dmesg files, all outside the run window (H13-pre 0; H14-pre 1×[32.29] pre-window; H14-post 2×[32.29] pre + [655.26] post; H15-post 4× post-everything VM) + 1 pre-session VM restart between T34 and T35 (H12→H13; T34: 1 pre-session restart) + 1 mid-session VM restart between C:-staging and WSL-staging (H13 06:53:50→06:56:15, H14 create 06:57:33; 78 s gap with no VM; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified) + 1 post-everything VM restart (H14→H15 07:13:19; only final state reads + trace slices ran on H15). R1 completed exit 0 with zero in-window flaps on the dmesg record — no T27 §4 effects-verification needed (the immediate post-run dmesg read closed T33's sequencing gap). Precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero WSL entries in-window; 2 in-window Volsnap (C: pressure); boundaries bound all restarts | Newest-30 reads (pre/post): H12 teardown 02:41:27 → H13 create 02:53:50 → H13 teardown 02:56:15 → H14 create 02:57:33 → H14 teardown 03:13:19; inside the R1 window 02:58:32–03:08:14 (local): 2× Volsnap ID-33 (oldest C: shadow copy deleted to keep usage under limit — C: at 99%, 13–14 G avail) + zero Hyper-V-VmSwitch entries (precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H13 btime |
| G4 | Hold count 79/79 | 534 ms-class holds register 79/79 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33+T34+T35 (T35 R1: 535.3/535.5/536.8/535.2/534.6/536.6/535.7/535.8/534.5/537.9 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/SC/ZC/SP/SM/SE/MR frozenness; attract differs; snowflake shimmer on SE + MR; panel animation + lineup lottery on arrival; countdown/gameplay dynamic | Title text-band frozen across showings (0.0465/1 R1); R1's 2 frames bit-identical to T34 R1's run (zc-post3, rc-post1); a1-post15 xrun 0.0001/0 max 1 again (single-px JPEG shimmer); menu whole-frame ≤0.07/p99 ≤1 cross-run; SC cross-run 0.002–0.26/p99 0–5; ZC cross-run 0.00–0.24/p99 2–7; SP cross-run ≤0.09/p99 0; SM cross-run 0.008–0.07/p99 0–1; Select Event ≤0.10/p99 ≤1 cross-run (rc-post8 snowflake animation); My Rules ≤0.14/p99 ≤2 (snowflake drift); pre-race panel ≤0.44/p99 ≤20 within run over 79 s (panel shimmer/animation — widest static-arrival spread to date, still far under any gate) + AI rider lineup differs run to run (T35 `Zoe/Kaori/Brodi/Viggo/Elise/Griff` vs T34 `Zoe/Viggo/Psymon/Eddie/Allegra/Moby`) + SE-TAG crop on panel constant within run but run-dependent (48.5040/133 vs T34's 50.8209/132); load→panel transition timing is lottery-dependent (T35: 97% @+3, cinematic @+8, panel @+15, no black frame captured; T34: 92% @+3, black @+8, cinematic @+15, panel @+25) — the settled-panel gate handled both timings; countdown/live gameplay never static (7.97–20.23). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the live-gameplay run | `WaitVblankStart` stops after log ≤90 in T35 R1 including countdown + live gameplay (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T34-R1-identical modulo counts). The attract/title/menu/submenu/game sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical; IOP count jumps on audio) | Like prior arrivals, countdown/gameplay arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T34 R1; counts shift (`GetThreadId` 4.52M→5.02M, EE total 10.99M→12.28M; IOP 17.25M→20.35M; `sceSdGetParam` 1963→26065 ≈13×, `sceSdGetAddr` 3.39M→4.08M — race audio traffic). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~29 GB across 23 emulogs (T17→T35 chain, all preserved); C: 13 G avail (pre 14 G — run staging + traces; T34 pre was 20 G). T35 R1 full trace SSD-copied + sha-verified (2.92 GB: `emulog-t35r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T35 brief cites `t34r1-mr-post{1,3,8,15,25,40}.jpg` + `t34r1-mr-stab{1…6}.jpg` — all 12 exist with full shas+sizes reproducing T34 §T34-2; the PIL `convert('RGB').save` ref recipe reproduces byte-exactly (PPM-vs-JPEG 0.0000/0). T28 G9 lesson holds |
| G10 | Session wall + run durations | ~50 min active of the 4 h box (one run + report/commit); zero lease waits (no lease exists for T35). R1 wall 575 s — 215 s over the ≤6 min guidance (added X-phase scoring + arrival tail); R1 full dmesg coverage, zero flaps |
| G11 | X11 mount needed twice on the same generation, harmless | Both `/tmp/.X11-unix` tmpfs mounts landed on VM-H14 (the H13→H14 restart fell between C:-staging and WSL-staging); mount verified present on H14 pre-R1, R1 started Xvfb :99 cleanly regardless (exit 0 + 55 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 / T33 G11 / T34 G11 stand) |
| G12 | Remote-vs-PIL gap receipted on the panel whole bar: ~1.3–1.6×, bar holds even remotely | Follow-up to T34 G12's chicken-and-egg: R1's in-script vs-pp receipt reads 0.69–1.00/p99 9–19 on panel-side PIL 0.43–0.75 (≈1.3–1.6× inflation at the ~0.5 scale — milder than the ~3–5× seen at the ~0.1 scale and the ~6–11× at the ~0.04 scale), so the < 2.0 whole bar holds even as an in-script leg (2.0× margin on the worst remote 0.9968). The TAG-crop gap re-confirmed at ~280× (2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated in PIL transfer to remote with single-digit inflation near zero and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars |

## Evidence files

`REPORT.md` (this file),
scripts: `t35-auto.sh`,
`t35-cropdiff.py` (T34 logic, byte-identical),
`t35-analyze.sh`, `t35-vcount.sh` (comment/header deltas only);
R1: `t35r1-start.jpg`, `t35r1-a1-now.jpg`, `t35r1-a1-poll01.jpg`,
`t35r1-a1-pre.jpg`, `t35r1-a1-post{3,8,15,25}.jpg`, `t35r1-menupre.jpg`,
`t35r1-mc-post{1,3,8,15}.jpg`, `t35r1-scpre.jpg`,
`t35r1-zc-post{1,3,8}.jpg`, `t35r1-ccpre.jpg`,
`t35r1-sp-post{1,3,8}.jpg`, `t35r1-sppre.jpg`,
`t35r1-pc-post{1,3,8}.jpg`, `t35r1-smpre.jpg`,
`t35r1-rc-post{1,3,8}.jpg`, `t35r1-sepre.jpg`,
`t35r1-sj-post{1,3,8}.jpg`, `t35r1-mrpre.jpg`,
`t35r1-mr-post{1,3,8,15,25,40}.jpg`, `t35r1-mr-stab{1,2}.jpg`,
`t35r1-pppre.jpg`, `t35r1-x-post{1,3,8,15,25,40}.jpg`,
`t35r1-x-stab{1…6}.jpg` (55 snaps),
`t35r1-census.txt`, `t35r1-samples.txt`, `t35r1-poll.log`,
`t35r1-stdout.txt`, `t35r1-stderr.txt`, `t35r1-trace-head.txt` / `t35r1-trace-tail.txt`;
flaps: `t35-dmesg-vmH13-pre.txt` (0 AcceptAsync on H13, pre-run) /
`t35-dmesg-vmH14-pre.txt` (1 AcceptAsync [32.29] pre-window on H14) /
`t35-dmesg-vmH14-post.txt` (2 AcceptAsync [32.29] pre + [655.26] post; full R1-window
coverage, zero in-window) / `t35-dmesg-vmH15-post.txt` (4 AcceptAsync on H15, fresh boot),
`t35-eventlog-pre.txt` / `t35-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t35r1.txt`
(2,919,779,317 B `e337f8e8…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T34 R1
`…-20260921T065839Z.txt` `e7b19750…`.
