# T34 report — Cross on Continue from the My Rules park: next screen (bytesize, no lease)

Brief: T34 (Cross on Continue from the My Rules park). Tables, no
verdicts. One boot ran on bytesize (R1: chain reproduced to the My Rules
park, ENTER Cross advanced into game load → race intro → pre-race panel);
laptop-side work was ssh/scp + local reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T33/REPORT.md` (all of it: R1
NO-SE-PARK on a true SE park (remote TAG-crop gap ~260–280×, honestly
tabled); R2 with widened gate reached My Rules via Cross on Snow Jam
@T+297.80, Continue highlighted (orange bar), 12 snaps over 128 s pairwise
≤0.201/p99 ≤3 (snowflake drift), no reclaim; G1 proposes one 534 ms Cross
(× Enter game) on Continue). This brief executes T33's G1.

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
parked My Rules (Continue highlighted) accepts the rules / enters the
game; observable — pre-press snap = My Rules (whole-frame match vs T33
`t33r2-sj-stab6.jpg` ref under the calibrated < 2.0 gate + viewed snap),
post-press snap series + per-hop whole diffs + arrival stability N; screen
content read off viewed snaps; alternatives — screen ignores Cross (post
series still My Rules), slow next-screen load (change lands late in the
+40 s tail), press never acted on arrival (pre-press ≠ My Rules → ONE
bounded variant allowed); stop — table the exact observed behavior +
recipe, no button-mashing survey.

## T34-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T34; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T34]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T34 observed | Match |
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
| T33 reference snaps present | — | all 12 arrival shas reproduce T33 §T33-2 (`sj-post{1,3,8,15,25,40}` + `sj-stab{1…6}` full sha256 + sizes) | yes |
| Free space | — | WSL `/` 889 G avail; C: 20 G (836 G); laptop `/` 8.8 Gi avail; SSD 389 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×2 (VM-H10, wiped by H10→H11 restart; re-mounted on VM-H11 pre-R1 — T32 G11 stands) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t34-{auto,analyze,vcount,cropdiff}.sh/.py`, `t34-ref-mr.ppm` (3,932,177 B, sha `069b1113…64d373`), `t34-{r1-census,samples}.txt` (via analyze), `t34-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t34-*.txt` (rotation chain, see trace table), `boot-t34.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t34*` + `emulog-t34r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 1 pre-session between T33 and T34 (H9→H10) + 1 mid-session between staging and R1 (H10→H11, 213 s gap with no VM) + 1 post-everything (H11→H12; only post reads ran on H12) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H10 btime:
02:15:09→`1789971309`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 05:57:29 | VM-H9 teardown (T33's VM, after T33's session) | eventlog-pre (IDs 69/71) |
| 2 | 06:15:09 ([0] VM-H10) | VM-H10 started fresh ~2 s before first ssh | btime `…1309`, eventlog-pre head (IDs 292/67/291/233/232/102/291) |
| 3 | 06:15:11–~06:18 | Pre-run checks + staging on VM-H10 (all ssh exit 0, zero flaps) | `t34-dmesg-vmH10-pre.txt` (0 kills, 440 lines) |
| 4 | 06:17:57–06:21:30 | VM-H10 teardown → VM-H11 create (mid-session restart, NOT by me; between staging and R1; 213 s gap with no VM; every ssh exit 0 across it; staged files persist — same VHD, shas re-verified) | btime `…1689`, eventlog-post (IDs 69/71 teardown, 292/67/291/233/232/102/291 create) |
| 5 | 06:22:14–06:30:02 ([44]→[512] H11) | R1 single-shot exit 0, `T34_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart in-window) | exit 0, 46 snaps, trace sha |
| 6 | 06:30:02–~06:34 | R1 analyze (exit 0) + all R1 fetches (exit 0, sha-valid) on VM-H11 | `t34-census.txt`, 46 JPGs |
| 7 | 06:34:12 | VM-H11 teardown → VM-H12 create (post-everything restart, NOT by me; only final state reads + trace slices ran on H12) | btime `…2589`, eventlog-post head (IDs 69/71 teardown) |
| 8 | 06:36:31 ([1.90] H12) | VM-H12 fresh, 0 kills | `t34-dmesg-vmH12-post.txt` (481 lines, boot coverage) |
| 9 | event log | Newest-30 reads (pre/post): head moves H10-create 02:15:09 → H11-teardown 02:34:12; boundaries H9-teardown 01:57:29, H10-create 02:15:09, H10-teardown 02:17:57, H11-create 02:21:30, H11-teardown 02:34:12; zero entries inside the R1 window (02:22:14–02:30:02 local) — userland kills leave no Windows trace (T17/T21/T23/T25/T27/T28/T29/T30/T31/T32/T33 precedent stands) | `t34-eventlog-{pre,post}.txt` |
| 10 | dmesg noise | `Ioctl failed` lines 23 pre (H10) / 23 post-R1 (H11) / 46 post (H12) — steady boot/GPU-query noise, not kills | dmesg files |

## T34-1. MR detector + calibration (thresholds, match scores)

Tool: `t34-cropdiff.py` (copy of T33's, byte-identical;
`t34-vcount.sh` likewise; `t34-analyze.sh` differs only in output names).
Title text-band method unchanged (thresholds frozen: TITLE band mean <
2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU whole-vs-menu mean < 2.0;
NONMENU / NONSC / NONZC / NONSP / NONSE whole-vs-ref mean > 5.0;
DEPARTED whole hop mean > 5.0; SE-TAG < 5.0 remote). New: My Rules
reference `t34-ref-mr.ppm` (3,932,177 B, sha
`069b111300b6096bd20d5234178fed0fd7b65d0df73544470c27a3386164d373`),
derived from T33's `t33r2-sj-stab6.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T34-4; T28
§T28-1 recipe). Ref-vs-JPEG recipe check: 0.0000/0 (JPEG decode
deterministic, T28 G9 lesson holds).

MR whole-frame calibration matrix (candidate vs `t33r2-sj-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| sj-post1 vs stab6 | 0.1206 | 1 | 56 | MR-MR (whole) |
| sj-post3 vs stab6 | 0.0796 | 0 | 56 | MR-MR (whole) |
| sj-post8 vs stab6 | 0.1173 | 1 | 57 | MR-MR (whole) |
| sj-post15 vs stab6 | 0.1711 | 3 | 69 | MR-MR (whole) |
| sj-post25 vs stab6 | 0.1046 | 1 | 56 | MR-MR (whole) |
| sj-post40 vs stab6 | 0.1225 | 1 | 56 | MR-MR (whole) |
| sj-stab1 vs stab6 | 0.1346 | 2 | 61 | MR-MR (whole) |
| sj-stab2 vs stab6 | 0.1539 | 2 | 57 | MR-MR (whole) |
| sj-stab3 vs stab6 | 0.0786 | 0 | 56 | MR-MR (whole) |
| sj-stab4 vs stab6 | 0.1744 | 3 | 75 | MR-MR (whole, worst mean) |
| sj-stab5 vs stab6 | 0.1515 | 2 | 65 | MR-MR (whole) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| sepre (T33 SE) vs stab6 | 10.5940 | 144 | 241 | SE-vs-MR (whole) |
| rc-post1/3/8 (T33 SE) vs stab6 | 10.5939/10.5899/10.6468 | 144 | 241 | SE-vs-MR (whole) |
| smpre / pc-post1/3/8 (T33 SM) vs stab6 | 10.4630/10.4711/10.4628/10.4426 | 143 | 241 | SM-vs-MR (whole) |
| sppre / sp-post1/3/8 (T33 SP) vs stab6 | 9.8685/9.8269/9.8566/9.8374 | 138 | 239 | SP-vs-MR (whole) |
| ccpre / zc-post1/3/8 (T33 ZC) vs stab6 | 7.0376/7.0495/7.0552/7.0857 | 103–104 | 209–212 | ZC-vs-MR (whole) |
| scpre / mc-post1/3/8/15 (T33 SC) vs stab6 | 5.6296/5.6395/5.6646/5.6188/5.6133 | 117 | 248 | SC-vs-MR (whole, nearest prior screen) |
| menupre / a1-post3/8/15/25 (T33 menu) vs stab6 | 10.0751/10.0918/10.0884/10.0760/10.0815 | 96 | 224 | menu-vs-MR (whole) |
| a1-pre (T33 title) vs stab6 | 9.7697 | 143 | 238 | title-vs-MR (whole) |
| start / a1-now (T33 attract) vs stab6 | 13.1879/14.6459 | 135/148 | 239/234 | attract-vs-MR (whole) |
| ref PPM vs stab6 JPEG | 0.0000 | 0 | 0 | recipe exact (JPEG decode deterministic) |
| ref PPM vs ref PPM | 0.0000 | 0 | 0 | self |

MR gate (as frozen pre-run): in-script park criterion = decisively left
SE (sepre→sj-post1 hop > 5.0) AND non-SE (post8 vs-se > 5.0) AND arrival
static (p1→p3 and p3→p8 hops < 1.0). The vs-mr line is scored in-script
as the remote receipt but is NOT a gate leg (T28 MENU / T29 SC / T30 ZC /
T31 SP / T32 SM / T33 SE precedent — the Enter Cross press does NOT
depend on a strict whole-frame MR gate); the strict whole-vs-MR < 2.0 bar
is confirmed post-hoc (T33 G12: no pre-run remote receipt exists for the
~0.17 MR-side mean — PIL on WSL chicken-and-egg). The SE→MR whole hop is
decisive (~10.58–10.61), so DEPARTED > 5.0 fires normally here. Margins:
whole post-hoc MR-side worst 0.1744→11.5×, SC-side nearest 5.61→2.8×;
remote receipt R1 MR-side 0.40–0.46 (see §T34-2).

Script deltas vs `t33-auto.sh` (committed originals untouched; `t34-auto.sh`
is the adapted copy):

| Area | T33 R2 script | T34 script |
|---|---|---|
| Chain | park phase + MENU Cross + mc series to +15 + scpre + ZOE Cross + zc series to +8 + ccpre + CONT Cross + sp series to +8 + sppre + PEAK Cross + pc series to +8 + smpre + RACE Cross + rc series to +8 + sepre + SNOWJAM Cross + sj series to +40 + 6×10 s stab | identical through SNOWJAM Cross; sj series shortened to sj-post1/3/8 (each + vs-mr score; hops pre→p1, p1→p3, p3→p8) |
| MR park | (arrival was the end) | MR-park gate (departed + non-SE + static; vs-mr scored as remote receipt) + `mrpre` snap (vs-mr + vs-se + titleband) |
| T34 press | — | ONE `ENTER_CROSS` (K), arrival series +1/+3/+8/+15/+25/+40 (each titleband + vs-mr), 6 per-hop whole diffs, 6×10 s arrival stability (band + vs-mr in-script; full vs-ref panel post-hoc local) |
| Self-tests | SELF_TEST + SELF_WHOLE + SELF_MENU + SELF_SC + SELF_ZC + SELF_SP + SELF_SM + SELF_SE + SELF_SETAG | + SELF_MR (whole, < 2.0 bar) + NONSE_MEAN_MIN + is_nonse() + score_mr() + REFMR_CHECK |
| No-park paths | explicit `NO-PARK` + … + `NO-SE-PARK` | + explicit `NO-MR-PARK` plog, still clean shutdown + `T34_DONE` (trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
port of `t34-cropdiff.py` (`/tmp/t34-fastdiff.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical, only
the mode tag differs) against the committed tool on 4 diverse pairs
(whole MR-MR, whole SE-MR, whole SC-MR, whole title-MR). Any score reproduces with
the committed `t34-cropdiff.py`, slower.

## T34-2. R1 — park reproduced, Cross → game load → pre-race panel

Run: `t34-auto.sh`, ONE fresh boot, T_BOOT wall 1789971734 (uptime 44,
VM-H11), 06:22:14–06:30:02 UTC (uptime 44→512 = 468 s; 108 s over the
≤6 min guidance — the added MR phase + full arrival tail; full dmesg
coverage, zero flaps in-window), WID 2097159 (same as T31 R1 / T32 R1 /
T33 R1 / T33 R2), exit 0, `T34_DONE`, clean SIGTERM shutdown. SELF_TEST
0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC 0.0000/0,
SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM 0.0000/0, SELF_SE 0.0000/0,
SELF_SETAG 0.0000/0, SELF_MR 0.0000/0. Attempt 1 of ≤3 consumed;
attempts 2–3 not needed (Cross advanced, arrival mapped).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+100, score 0.4331/6 remote / 0.0467/1 PIL (T33 R2: 0.4331/6 / 0.0467/1 — poll01 frame bit-identical to T33 R2's = T31's, see identities) | Cross 536.8 ms @T+97.70 (attract-skip) + Start 537.6 ms @T+100.98 (on title, ≤1.0 s after exposure) | Main Menu by +4 s; menu-like gate (non-title + whole-static 0.0336/0.0121) + post25-vs-menu 0.2953/5 → park for menu Cross |
| A2–A3 | not run (Cross advanced) | — | — |

### R1 cross-run frame identities (T34 R1 vs T33 R2/R1, full sha256)

| Frame | T34 R1 sha | T33 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `d977309dd891…` (cp-identical, pair 0.0000/0) 58352 B | `d977309dd891…` (R2) | BIT-IDENTICAL to T33 R2's (whole-file `cmp`; ∴ also ≡ T31's frame per T33 §T33-2) |
| a1-post3 | `45bcb1c63256…` 49966 B | `45bcb1c63256…` (R2) | BIT-IDENTICAL to T33 R2's (`cmp`; ∴ also ≡ T31's) |
| a1-post8 | `91771d70d2bb…` 50015 B | `91771d70d2bb…` (R2) | BIT-IDENTICAL to T33 R2's (`cmp`; ∴ also ≡ T31's) |
| a1-post25 | `4e4e15409746…` | `4e4e15409746…` (R2) | BIT-IDENTICAL to T33 R2's (`cmp`) |
| menupre | `1307199a73f1…` | `1307199a73f1…` (R1) | BIT-IDENTICAL to T33 R1's (`cmp`); differs from T33 R2's by 0.0013/0 max 6 |
| a1-post15 | `24187066e1f0…` | `20ce007cdbfb…` (R2) | differ; pair 0.0003/0 max 5 (single-px JPEG shimmer) |
| start | `3dd7c35edcba…` 59406 B | `2d121f1da1a1…` 58423 B (R2) | differ; pair 15.92/156 (attract-loop phase differs) |
| a1-now | `11a5c0db9f6f…` | `bf1d64ff9406…` (R2) | differ; pair 13.25/150 (attract phase differs) |
| mc-post1/3/8/15 | differ | differ (R2) | whole pairs 0.135/3, 0.126/3, 0.101/3, 0.070/1 |
| scpre | differ | differ (R2) | whole pair 0.1150/2 |
| zc-post1/3/8 | differ | differ (R2) | whole pairs 0.082/2, 0.062/1, 0.087/2 |
| ccpre | differ | differ (R2) | whole pair 0.1086/3 |
| sp-post1/3/8 | differ | differ (R2) | whole pairs 0.030/0, 0.051/0, 0.001/0 |
| sppre | differ | differ (R2) | whole pair 0.0609/0 |
| pc-post1/3/8 | differ | differ (R2) | whole pairs 0.019/0, 0.005/0, 0.034/0 (park reproduced tightly) |
| smpre | `4313fd4da4b7…` | `9d3a9379ef35…` (R2) | whole pair 0.0069/0 |
| rc-post1/3/8 | differ | differ (R2) | whole pairs 0.0042/0, 0.0018/0, 0.1206/1 (rc-post8 snowflake shimmer) |
| sepre | `c0200fa19c67…` | `b6857d04a7a7…` (R2) | whole pair 0.0128/0 |
| sj-post1/3/8 | differ | differ (R2) | whole pairs 0.0657/0, 0.0140/0, 0.1288/2 |
| mrpre vs T33 `sj-stab6` | `9d5331f322e3…` | `df39d72548a3…` (R2) | whole pair 0.0791/0 (inside T33's own 0.0786–0.1744 MR-MR spread) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789971831.699694903 → 1789971832.236497737 | 536.8 ms | T+97.70→98.24 | 141→142 | `a1-now` attract (33.7833/193 remote; 33.7824/193 PIL) | `a1-poll01` TITLE (0.4331/6; 0.0467/1) |
| A1 Start (Return) | 1789971834.975232166 → 1789971835.512852656 | 537.6 ms | T+100.98→101.51 | 145 | `a1-pre` ≡ `a1-poll01` (sha `d977309dd891`, TITLE, bit-identical to T33 R2's=T31's viewed frame) | `a1-post3` Main Menu (16.2559/139; 16.2584/138) |
| MENU Cross (K) | 1789971874.078128301 → 1789971874.614939064 | 536.8 ms | T+140.08→140.61 | 184 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0274/0 PIL; vs-title 16.2610/139) | `mc-post1` Select Character (vs-menu 10.2115/106; vs-sc 0.4291/7; titleband 12.5548/164) |
| ZOE Cross (K) | 1789971914.042105328 → 1789971914.578959233 | 536.9 ms | T+180.04→180.58 | 224 | `scpre` Select Character, Zoe selected (vs-sc 0.5887/8 remote; 0.2409/4 PIL; vs-menu 10.1935/105; vs-title 12.6285/164) | `zc-post1` Setup Character (vs-sc 7.2281/100; vs-zc 0.5228/9; titleband 15.9233/128) |
| CONT Cross (K) | 1789971942.782576687 → 1789971943.317664735 | 535.1 ms | T+208.78→209.32 | 252→253 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4639/8 remote; 0.2302/6 PIL; vs-sc 7.2899/100; vs-title 15.8419/128) | `sp-post1` Select Peak (vs-zc 9.4675/154; vs-sp 0.3719/6; titleband 23.1278/171) |
| PEAK Cross (K) | 1789971971.505396391 → 1789971972.041904671 | 536.5 ms | T+237.51→238.04 | 281→282 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.4006/6 remote; 0.0575/0 PIL; vs-zc 9.4850/154; vs-title 23.1279/171) | `pc-post1` Select Mode (vs-sp 5.3587/121; vs-sm 0.3987/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789972000.803452735 → 1789972001.340267013 | 536.8 ms | T+266.80→267.34 | 310→311 | `smpre` Select Mode, Race highlighted (vs-sm 0.3906/6 remote; 0.0397/0 PIL; se-tag 14.3278/89 remote / 14.1390/88 PIL; vs-sp 5.3502/121; vs-title 26.3170/183) | `rc-post1` Select Event (vs-sm 0.8074/11; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789972031.916128081 → 1789972032.451542060 | 535.4 ms | T+297.92→298.45 | 341→342 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6271/11 remote, 0.0094/0 PIL; vs-se 0.4078/6, 0.0373/0; vs-sm 0.8121/11; vs-sp 5.4519/121; vs-title 26.2104/183 — viewed) | `sj-post1` My Rules (vs-se 10.6322/143; vs-mr 0.4028/7; titleband 9.8393/137) |
| ENTER Cross (K) | 1789972060.557339596 → 1789972061.092896598 | 535.6 ms | T+326.56→327.09 | 370→371 | `mrpre` My Rules, Continue highlighted (vs-mr 0.3994/7 remote; 0.0791/0 PIL; vs-se 10.6333/143; vs-title 9.8393/137 — viewed) | `mr-post1` game load 18% (vs-mr 12.4991/149; titleband 17.1968/170 — viewed) |

Within-dwell receipts R1: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (06:23:54 UTC, 1 s resolution) → Start-keydown 06:23:54.975 ≤
1.0 s; T33-R2-measured title persistence 15–17 s ⇒ press inside the window
with an order of magnitude to spare. Start-keyup → MenuCross-keydown
38.6 s; MenuCross-keyup → ZoeCross-keydown 39.4 s; ZoeCross-keyup →
ContCross-keydown 28.2 s; ContCross-keyup → PeakCross-keydown 28.2 s;
PeakCross-keyup → RaceCross-keydown 28.8 s; RaceCross-keyup →
SnowJamCross-keydown 30.6 s; SnowJamCross-keyup → EnterCross-keydown
28.1 s (no dwell pressure — all parks static, T27 G1 / T28 G1 / T29 G1 /
T30 G1 / T31 G1 / T32 G1 / T33 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / whole vs MR-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | Whole vs MR | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|---|
| start (T+96) | 59406B / `3dd7c35edcba` | 29.6409/170 | 16.3136/164 | 15.8929/165 | 15.7107/156 | 15.3090/164 | 14.9878/167 | 15.0592/167 | 14.6092/148 | 38.8878/121 | Attract |
| a1-now (T+96, pre-Cross) | 57053B / `11a5c0db9f6f` | 33.7824/193 | 19.9708/171 | 17.7159/153 | 19.0969/158 | 15.6046/164 | 15.8332/165 | 15.9618/166 | 16.5268/138 | 61.3900/163 | Attract |
| a1-poll01 (T+100, pre-Start) | 58352B / `d977309dd891` | 0.0467/1 T | 14.1355/151 | 11.3102/152 | 12.2550/146 | 15.3725/156 | 16.1512/158 | 16.2492/160 | 9.7697/143 | 106.6242/205 | TITLE |
| a1-pre (T+100) | 58352B / `d977309dd891` | 0.0467/1 | 14.1355/151 | 11.3102/152 | 12.2550/146 | 15.3725/156 | 16.1512/158 | 16.2492/160 | 9.7697/143 | 106.6242/205 | TITLE (identical cp) |
| a1-post3 (T+104) | 49966B / `45bcb1c63256` | 16.2584/138 | 0.0647/1 | 10.1249/105 | 6.9128/93 | 10.3972/170 | 10.9266/177 | 10.9446/177 | 10.0918/96 | 26.1710/106 | Main Menu |
| a1-post8 (T+110) | 50015B / `91771d70d2bb` | 16.2939/138 | 0.0628/1 | 10.1156/105 | 6.9187/93 | 10.3887/170 | 10.9184/177 | 10.9433/177 | 10.0884/96 | 26.1623/106 | Main Menu |
| a1-post15 (T+117) | 49622B / `24187066e1f0` | 16.2622/138 | 0.0257/0 | 10.1072/105 | 6.9081/93 | 10.3854/170 | 10.9184/177 | 10.9433/177 | 10.0761/96 | 26.1710/106 | Main Menu |
| a1-post25 (T+128) | 49738B / `4e4e15409746` | 16.2622/138 | 0.0408/0 | 10.1145/105 | 6.9042/92 | 10.3854/170 | 10.9186/177 | 10.9407/177 | 10.0815/96 | 26.1687/106 | Main Menu |
| menupre (T+138, pre-MCross) | 49628B / `1307199a73f1` | 16.2622/138 | 0.0274/0 | 10.1077/105 | 6.9079/93 | 10.3848/170 | 10.9178/177 | 10.9428/177 | 10.0751/96 | 26.1637/106 | Main Menu, Single Event highlighted |
| mc-post1 (T+141) | 70254B / `ae39a67fcfd5` | 12.4814/163 | 10.1429/105 | 0.0679/1 | 7.2434/101 | 11.3759/158 | 11.8398/158 | 11.9085/158 | 5.6391/117 | 26.5707/90 | Select Character, Zoe |
| mc-post3 (T+146) | 70600B / `02257ddcdb5d` | 12.4843/163 | 10.1633/107 | 0.0951/2 | 7.2701/100 | 11.4031/158 | 11.8657/157 | 11.9341/157 | 5.6667/117 | 26.5702/90 | Select Character |
| mc-post8 (T+153) | 70276B / `4828c93efc06` | 12.4587/163 | 10.1389/105 | 0.2492/5 | 7.2032/100 | 11.3480/158 | 11.8145/157 | 11.8898/157 | 5.6208/117 | 26.5695/90 | Select Character |
| mc-post15 (T+163) | 70006B / `6aa567fe5b59` | 12.4587/163 | 10.1277/105 | 0.0719/1 | 7.2157/100 | 11.3487/158 | 11.8126/157 | 11.8815/157 | 5.6116/117 | 26.6037/90 | Select Character |
| scpre (T+177, pre-ZCross) | 70170B / `38a7ba5c1d2c` | 12.5525/163 | 10.1263/105 | 0.2409/4 | 7.2252/100 | 11.3503/158 | 11.8266/157 | 11.8976/157 | 5.6245/117 | 26.5695/90 | Select Character, Zoe selected |
| zc-post1 (T+181) | 51508B / `19be51a78083` | 15.9000/129 | 6.9257/93 | 7.1993/100 | 0.2908/7 | 9.3661/153 | 10.1355/164 | 10.2472/164 | 7.0475/103 | 15.2982/91 | Setup Character, Zoe |
| zc-post3 (T+186) | 51539B / `33dee6956278` | 15.8335/128 | 6.9112/92 | 7.2663/101 | 0.2328/6 | 9.3474/153 | 10.1084/165 | 10.2215/165 | 7.0550/103 | 15.3015/91 | Setup Character |
| zc-post8 (T+193) | 51355B / `40f78d2d58e6` | 15.8302/128 | 6.9298/93 | 7.1290/100 | 0.2044/5 | 9.3802/153 | 10.1321/164 | 10.2354/164 | 7.0848/104 | 15.2956/91 | Setup Character |
| ccpre (T+206, pre-ContCross) | 51546B / `52818e10b7b7` | 15.8192/128 | 6.9084/93 | 7.2646/100 | 0.2302/6 | 9.3574/153 | 10.1121/164 | 10.2247/164 | 7.0439/103 | 15.3217/91 | Setup Character, Zoe + Continue |
| sp-post1 (T+210) | 65280B / `2c0fe932f10c` | 23.1262/171 | 10.4242/170 | 11.3462/158 | 9.3874/153 | 0.0250/0 | 5.2263/121 | 5.3304/121 | 9.8220/138 | 14.0038/89 | Select Peak, Peak 1 |
| sp-post3 (T+214) | 65474B / `7a15a6c0510b` | 23.1259/171 | 10.4312/170 | 11.3691/158 | 9.3861/153 | 0.0418/0 | 5.2409/121 | 5.3430/121 | 9.8591/138 | 14.0026/89 | Select Peak |
| sp-post8 (T+222) | 65229B / `79e06cca6a9a` | 23.1271/171 | 10.4061/170 | 11.3502/158 | 9.3727/153 | 0.0046/0 | 5.2069/121 | 5.3099/121 | 9.8373/138 | 14.0026/89 | Select Peak |
| sppre (T+234, pre-PeakCross) | 65546B / `4551f5233b39` | 23.1259/171 | 10.4494/170 | 11.3894/158 | 9.4048/153 | 0.0575/0 | 5.2576/121 | 5.3301/121 | 9.8801/138 | 14.0026/89 | Select Peak, Peak 1 highlighted |
| pc-post1 (T+239) | 67425B / `c8c459dd5413` | 26.3046/183 | 10.9199/178 | 11.8086/157 | 10.0965/164 | 5.1908/121 | 0.0488/0 | 0.5211/10 | 10.4696/143 | 14.1392/88 | Select Mode, Race |
| pc-post3 (T+243) | 67397B / `71c2bc3bd70a` | 26.3046/183 | 10.9144/178 | 11.8041/157 | 10.1010/164 | 5.1822/121 | 0.0408/0 | 0.5121/9 | 10.4637/143 | 14.1367/88 | Select Mode |
| pc-post8 (T+251) | 67563B / `787178b2d266` | 26.3061/183 | 10.9356/178 | 11.8024/157 | 10.1182/164 | 5.2039/121 | 0.0640/1 | 0.5354/11 | 10.4454/143 | 14.1684/88 | Select Mode |
| smpre (T+263, pre-RaceCross) | 67438B / `4313fd4da4b7` | 26.3046/183 | 10.9137/178 | 11.8035/157 | 10.1008/164 | 5.1811/121 | 0.0397/0 | 0.5112/9 | 10.4633/143 | 14.1390/88 | Select Mode, Race highlighted |
| rc-post1 (T+268) | 69432B / `d86c39d523f9` | 26.1964/183 | 10.9382/178 | 11.8584/157 | 10.2158/164 | 5.2819/121 | 0.5095/9 | 0.0312/0 | 10.5897/144 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+272) | 69414B / `33793160a107` | 26.1945/183 | 10.9390/178 | 11.8582/157 | 10.2156/164 | 5.2828/121 | 0.5105/9 | 0.0323/0 | 10.5892/144 | 0.0094/0 | Select Event |
| rc-post8 (T+279) | 69957B / `467abbae4b0a` | 26.1964/183 | 11.0138/178 | 11.9343/157 | 10.2923/164 | 5.3625/121 | 0.5901/15 | 0.1004/0 | 10.6672/144 | 0.0094/0 | Select Event |
| sepre (T+293, pre-SnowJamCross) | 69493B / `c0200fa19c67` | 26.1964/183 | 10.9436/178 | 11.8638/157 | 10.2219/164 | 5.2880/121 | 0.5156/10 | 0.0373/0 | 10.5959/144 | 0.0094/0 | Select Event, Snow Jam highlighted (viewed) |
| sj-post1 (T+299) | 58455B / `b0f70415ef45` | 9.8145/135 | 10.0776/96 | 5.6044/117 | 7.0435/104 | 9.8148/137 | 10.4239/143 | 10.5882/143 | 0.0889/1 | 26.4126/92 | My Rules, Continue |
| sj-post3 (T+304) | 58466B / `4de16b5f3bf5` | 9.8145/135 | 10.0792/96 | 5.6081/117 | 7.0482/104 | 9.8157/137 | 10.4248/143 | 10.5887/143 | 0.0798/0 | 26.4250/92 | My Rules |
| sj-post8 (T+311) | 59031B / `8da4c94dcc60` | 9.8668/135 | 10.1256/99 | 5.6605/118 | 7.0793/105 | 9.8669/137 | 10.4748/143 | 10.6388/143 | 0.1523/3 | 26.4163/92 | My Rules (viewed) |
| mrpre (T+323, pre-EnterCross) | 58517B / `9d5331f322e3` | 9.8145/135 | 10.0791/96 | 5.6085/117 | 7.0492/104 | 9.8162/137 | 10.4254/143 | 10.5893/143 | 0.0791/0 | 26.4126/92 | My Rules, Continue highlighted (viewed) |
| mr-post1 (T+328) | 66681B / `600f33859c9f` | 17.1522/168 | 15.2147/157 | 14.1974/157 | 13.6527/153 | 14.7005/153 | 15.0683/152 | 15.1959/153 | 12.4712/148 | 84.8970/216 | Loading 18% (viewed) |
| mr-post3 (T+331) | 67499B / `e1ad2d6cafe4` | 18.2568/172 | 15.8000/157 | 14.7238/158 | 14.1745/154 | 15.3690/154 | 15.7430/154 | 15.8710/156 | 12.9847/151 | 93.5508/226 | Loading 92% (viewed) |
| mr-post8 (T+338) | 21267B / `07c24d0fa0ab` | 59.3831/239 | 35.9671/245 | 35.6106/243 | 36.3051/236 | 31.9509/243 | 31.7315/244 | 31.6150/244 | 36.2393/222 | 96.0167/183 | Black frame (viewed) |
| mr-post15 (T+347) | 45027B / `dfb74d3b4eda` | 43.9357/237 | 26.4870/221 | 26.4376/209 | 26.8179/204 | 23.2168/221 | 23.0365/221 | 22.9478/221 | 26.4072/200 | 39.9109/110 | Race intro cinematic (viewed) |
| mr-post25 (T+358) | 59898B / `73c31fc9ba92` | 34.5164/184 | 19.0132/177 | 19.1430/172 | 19.8804/162 | 16.3573/157 | 16.1845/159 | 16.1836/159 | 19.3033/153 | 50.8209/132 | Pre-race panel (viewed) |
| mr-post40 (T+375) | 60142B / `d77258686b97` | 34.5091/184 | 19.2216/178 | 19.3261/172 | 20.0761/164 | 16.4788/157 | 16.3568/160 | 16.3555/159 | 19.4922/153 | 50.8209/132 | Pre-race panel (viewed) |
| mr-stab1 (T+397) | 60293B / `755c87a2b812` | 34.5122/184 | 19.3604/179 | 19.4496/172 | 20.2134/164 | 16.5779/157 | 16.4709/160 | 16.4692/160 | 19.6257/153 | 50.8209/132 | Pre-race panel |
| mr-stab2 (T+409) | 60168B / `43fed917331c` | 34.5071/184 | 19.2550/178 | 19.3574/172 | 20.1147/164 | 16.5071/157 | 16.3816/160 | 16.3802/160 | 19.5301/153 | 50.8209/132 | Pre-race panel |
| mr-stab3 (T+421) | 59932B / `ac3b402c0718` | 34.5095/184 | 19.0125/177 | 19.1422/172 | 19.8823/162 | 16.3606/157 | 16.1830/159 | 16.1821/159 | 19.3056/153 | 50.8209/132 | Pre-race panel |
| mr-stab4 (T+433) | 60067B / `e47741eab286` | 34.5134/184 | 19.1663/178 | 19.2778/172 | 20.0233/163 | 16.4427/157 | 16.3100/160 | 16.3087/159 | 19.4421/153 | 50.8209/132 | Pre-race panel |
| mr-stab5 (T+444) | 60072B / `36b1eaa64223` | 34.5121/184 | 19.1396/178 | 19.2541/172 | 19.9968/163 | 16.4246/157 | 16.2895/160 | 16.2884/159 | 19.4157/153 | 50.8209/132 | Pre-race panel |
| mr-stab6 (T+456) | 60273B / `11f6801e100c` | 34.5146/184 | 19.3213/178 | 19.4142/172 | 20.1709/164 | 16.5447/157 | 16.4401/160 | 16.4385/160 | 19.5841/153 | 50.8209/132 | Pre-race panel (viewed) |

In-script (remote) vs PIL agreement: ≤0.17 mean on menu/title-band/
vs-sp/vs-sm/vs-se/vs-mr scores at scale (e.g. mrpre band 9.8393 vs
9.8145; mrpre vs-se 10.6333 vs 10.5893; mr-post25 vs-mr 19.3113 vs
19.3033); the known ~3–11× remote-lossless gap on near-zero whole means
(mrpre vs-mr 0.3994/7 remote vs 0.0791/0 PIL ≈ 5×; sj-post1 vs-mr
0.4028/7 vs 0.0889/1; sepre vs-se 0.4078/6 vs 0.0373/0 ≈ 11× — T27 title /
T28 menu / T29 SC / T30 ZC / T31 SP / T32 SM / T33 SE precedent); hops
≤0.05. The TAG crop is the exception: ~280× on near-zero TAG means
(se-tag 2.6271/11 remote vs 0.0094/0 PIL — T33 G12), while large TAG
means agree (smpre se-tag 14.3278/89 remote vs 14.1390/88 PIL).

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1162 | 10.1226/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1115 | 0.1397/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2887 | 0.3149/8 | same screen |
| post8 → post15 (mc) | 0.2116 | 0.2343/4 | same screen |
| post15 → scpre (park span) | — | 0.2275/4 | same screen |
| scpre → zc-post1 | 7.2354 | 7.2572/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.2954 | 0.3189/9 | arrival settling |
| post3 → post8 (zc) | 0.2769 | 0.2980/7 | same screen |
| post8 → ccpre (park span) | — | 0.3049/8 | same screen |
| ccpre → sp-post1 | 9.3215 | 9.3589/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0521 | 0.0596/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0331 | 0.0388/0 | same screen |
| post8 → sppre (park span) | — | 0.0547/0 | same screen |
| sppre → pc-post1 | 5.2126 | 5.2380/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0182 | 0.0207/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0317 | 0.0359/0 | same screen |
| post8 → smpre (park span) | — | 0.0348/0 | same screen |
| smpre → rc-post1 | 0.4548 | 0.4803/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps) |
| post1 → post3 (rc) | 0.0008 | 0.0011/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0809 | 0.0831/0 | same screen (rc-post8 snowflake shimmer; still SE: se-tag 0.0094) |
| post8 → sepre (park span) | — | 0.0882/0 | same screen |
| sepre → sj-post1 | 10.5465 | 10.5711/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.0186 | 0.0249/0 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.0802 | 0.0883/1 | same screen |
| post8 → mrpre (park span) | — | 0.0876/1 | same screen |
| mrpre → mr-post1 | 12.4659 | 12.4281/148 | screen change within +1 s (My Rules → game load; decisive hop) |
| post1 → post3 (mr) | 2.1158 | 2.1338/69 | loading progress 18% → 92% |
| post3 → post8 (mr) | 39.9126 | 39.9610/253 | loading screen → black frame |
| post8 → post15 (mr) | 10.1869 | 10.1902/120 | black frame → race intro cinematic |
| post15 → post25 (mr) | 15.2178 | 15.2309/190 | cinematic → pre-race panel |
| post25 → post40 (mr) | 0.2379 | 0.2473/11 | arrival settling (panel shimmer/animation) |
| post40 → stab1 (mr) | — | 0.1676/7 | same screen |
| stab1 → stab6 (mr) | — | 0.0672/2 | same screen |
| post1 → stab6 (mr span) | — | 21.0753/169 | endpoints differ (load → panel) |

### R1 arrival (pre-race panel)

| Item | Value |
|---|---|
| Post-press frames | `t34r1-mr-post1.jpg` @T+328 (+1 s after Enter Cross keyup): `Single Event - Race / Peak 1 - Snow Jam` loading screen, 18% Loading…; `mr-post3` @T+331: same screen, 92% Loading…; `mr-post8` @T+338: black frame (21267 B); `mr-post15` @T+347: race intro cinematic (starting-gate scene, `EA RADIO BIG / Mas / Kinky / SSX 3` overlay, `Press X to skip`); `mr-post25` @T+358: pre-race panel = arrival |
| Stability N | 8 snaps (post25/40 + stab1–6) spanning T+358→T+456 (98 s) |
| Whole-frame pairwise (PIL) | 0.0239–0.3950/p99 ≤18 across all 28 pairs (panel shimmer/animation; min post25–stab3 0.0239/0, max post25–stab1 0.3950/18; JPEG shas distinct) |
| Vs-MR (whole) | 19.30–19.63/p99 153 across all 8 (not My Rules) |
| Vs-SE (whole) | 16.18–16.47/p99 159–160 across all 8 (not Select Event) |
| Vs-SM (whole) | 16.18–16.47/p99 159–160 across all 8 (not Select Mode) |
| Vs-SP (whole) | 16.36–16.58/p99 157 across all 8 (not Select Peak) |
| Vs-ZC (whole) | 19.88–20.21/p99 162–164 across all 8 (not Setup Character) |
| Vs-SC (whole) | 19.14–19.45/p99 172 across all 8 (not Select Character) |
| Vs-menu (whole) | 19.01–19.36/p99 177–179 across all 8 (not menu) |
| Vs-title (band) | 34.51–34.52/p99 184 across all 8 (not title) |
| SE-TAG (crop) | 50.8209/132 identical across all 8 (tagline band static) |
| What is highlighted/selected | `Snow Jam - Race / Single Event` panel: `Race against the other riders and place in the top three to receive a medal standing.` Riders `Zoe / Viggo / Psymon / Eddie / Allegra / Moby`; `Record time: 02:57`; `X Continue` (awaiting input) |
| Reclaim after arrival? | none observed in 98 s (all 8 snaps pre-race panel) |

### R1 MR-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Departure sepre→sj-post1 | 10.5465 | > 5.0 | yes |
| Non-SE (post8 vs-se) | 10.6844/143 | > 5.0 | yes |
| Arrival static p1→p3 | 0.0186 | < 1.0 | yes |
| Arrival static p3→p8 | 0.0802 | < 1.0 | yes → `MR-LIKE`, Enter Cross pressed |
| Vs-mr receipt (post1/3/8) | 0.4028/7, 0.3992/7, 0.4608/8 | (not a leg — receipt) | tabled (≈3–5× vs PIL 0.080–0.152; under 2.0 even remotely) |
| Vs-mr receipt (mrpre) | 0.3994/7 | (not a leg — receipt) | tabled (≈5× vs PIL 0.0791) |
| SM-side receipt (smpre se-tag) | 14.3278/89 | ≫ 5.0 | yes (2.9× margin; PIL 14.1390/88) |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Arrival park reproduced (snap match vs T33's `t33r2-sj-stab6.jpg`) | sj-post1/3/8 + mrpre whole-vs-stab6 0.0791–0.1523/p99 0–3 (all under the 2.0 gate; inside T33's own 0.0786–0.1744 spread); 5 chain frames bit-identical to T33 R2's run, 1 to T33 R1's |
| Cross acted on it (pre-press = My Rules, Continue highlighted) | `mrpre` vs-mr 0.3994/7 remote, 0.0791/0 PIL; viewed: My Rules, Continue highlighted (orange bar), all options Off, footer `Accept current rules and enter game.`, `× Enter game / △ Previous / ○ Options` |
| Next-screen snaps + stability N | 12 post-press snaps; 8-snaps stable arrival over 98 s, pairwise 0.024–0.395/p99 ≤18, endpoints post25–stab6 0.3503/16 |
| Full input log + trace sha | `t34r1-poll.log` (126 lines: every score + press, walls + uptimes) + trace `e7b19750…4d13a9` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32/T33 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725, first vblank
L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen
(all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean
tail @458.1406. Census: EE 10,985,537 (52, set-identical to T33 R2) · IOP
17,245,257 (155, set-identical to T33 R2 — game-load/intro arrival adds no new
called API) · `libsd.006: sceSdGetParam` 1963 (R2-T33: 1652);
`sceSdGetAddr` 3,391,248 (R2-T33: 3,728,400).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R1 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate → SnowJam Cross → MR-LIKE gate) |
| Cross on Continue? | YES (ENTER Cross @T+326.56 R1, pre-press = My Rules, Continue highlighted) |
| Next screen reached? | YES (game load @T+328 → race intro cinematic @T+347 → pre-race panel @T+358, stable 98 s) |
| Bounded variant? | none needed (first Enter press provably acted on the My Rules park) |
| 1200 s cap | Not reached — R1 ≈ T+470; attempts 2–3 unexercised |
| Chain end | Pre-race panel (`Snow Jam - Race`), `X Continue`, awaiting input |

## T34-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t34 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules → Cross → game load → race intro → pre-race panel, T+~470) | 39,518,489 / 2,526,769,871 | `e7b19750893380b1cbf802cb1011a293ebe4be5da8fbeeed3c370a4bee4d13a9` (analyze-sha on H11 = post-restart re-verify on H12 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t34r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t34r1-trace-head.txt` 149019 B sha `5a0e8140b58d…`, `t34r1-trace-tail.txt` 128846 B sha `87402ca57fad…`) |
| `emulog-pre-t34-20260921T062214Z.txt` = t33 R2 (preserved at R1 boot) | — / 2,403,143,826 | `757497b860cd8100ec9452bb4371b0a67902b9770544ad3eee2867004743af3d` (re-verified post-run: matches T33) | bytesize-only (T33 precedent; SSD holds T33's own copy) |
| `emulog-pre-t33-20260921T054304Z.txt` = t33 R1 (preserved at T33 R2 boot) | — / 1,706,068,225 | `1915aaf93fe11b5db9c2b661665e991aef9304513b069af6fe23d4c7eb5fd6dc` (re-verified post-run: matches T33) | bytesize-only (T33 precedent) |

Channel census (T4 `t4-census.py`, same script): R1 EE 10,985,537 (52
distinct, set-identical to T33 R2) · IOP 17,245,257 (155, set-identical
to T33 R2) · vblanks 397. Committed: `t34r1-census.txt` (11697 B sha
`29754b27e066…`), `t34r1-samples.txt` (5876 B sha `2d143ca87a4c…`),
`t34r1-poll.log` (126 lines, 7487 B sha `003f142eb7eb…`),
`t34r1-stdout.txt` (342 lines, 22069 B),
`t34r1-stderr.txt` (full `set -x` shell trace, 1968 lines, 106268 B),
`t34r1-trace-head.txt` / `t34r1-trace-tail.txt`.
Trace-head note: same 149019 B as T33 R2's head but sha differs
(`5a0e8140…` vs `9baf9ac8…`) — timestamp-stripped content differs only in
timing values (104/2000 lines: GameDB ms, system time, shader ms).

## T34-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H10 …1309
ssh bytesize 'wsl dmesg' > /tmp/t34-dmesg-pre.txt                     # 440 lines, 0 kills (H10)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t34-eventlog-pre.txt  # head 02:15:09
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm …t30-ref-zc.ppm …t31-ref-sp.ppm …t32-ref-sm.ppm …t33-ref-se.ppm; df -h / /tmp; df -h /mnt/c; du -sh …/logs/; ls …/logs/'  # all 7 refs + 889G / C: 20G / 24G
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …/logs/emulog.txt'  # 757497b8… T33R2 live
# T33 ref snaps (local): 12/12 full-sha256+sizes reproduce T33 §T33-2
# MR ref + calibration (local; t34-cropdiff.py = T33 copy, byte-identical)
python3 -c "Image.open(sj-stab6).convert('RGB').save('/tmp/t34-ref-mr.ppm')"  # ref 3932177 B 069b1113…
python3 /tmp/t34-fastdiff.py <valid 4/4 exact vs t34-cropdiff.py>
python3 /tmp/t34-calib.py  # 12 MR + 4 SE + 4 SM + 4 SP + 4 ZC + 5 SC + 5 menu + 1 title + 2 attract, whole vs MR-ref
# -> WHOLE MR-MR 0.0786-0.1744/p99 0-3, nearest SC 5.61-5.66/117; post-hoc bar < 2.0 (11.5x/2.8x)
# adapt t34-auto.sh from the T33 copy (MR gate + ENTER_CROSS + mr arrival; bash -n), t34-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t34-auto.sh t34-analyze.sh t34-vcount.sh t34-cropdiff.py /tmp/t34-ref-mr.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t34-… /home/brad/pcsx2-t4/; sha256sum …'  # 069b1113…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H10 (wiped by H10→H11 restart; re-mounted on H11)
ssh bytesize 'wsl python3 …/t34-cropdiff.py …REFMR …; …REFSE …; …REFSE …TAG'  # 0.0000/0 ×3 PPM
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H11 …1689 (H10→H11 restart mid-session)
ssh bytesize 'wsl sha256sum …/t34-auto.sh …/t34-ref-mr.ppm; ls …'      # staged shas survive restart
ssh bytesize 'wsl -u root mount …; ls …'                              # re-mount on H11
# R1 (ONE ssh; exit 0; MR-LIKE → ENTER Cross → game load → pre-race panel)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t34-auto.sh' > /tmp/t34r1-run-stdout.txt 2>/tmp/t34r1-run-stderr.txt  # T34_DONE, up 44→512
ssh bytesize 'wsl dmesg' > /tmp/t34-dmesg-post-r1.txt                 # IMMEDIATELY after run ssh: 451 lines, 0 kills (H11, full R1 coverage)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H11 …1689 still
ssh bytesize 'wsl bash …/t34-analyze.sh'                              # e7b19750…, 39518489 L
ssh bytesize 'wsl bash …/t34-vcount.sh'                                # 397 frozen (all ≤90)
ssh bytesize 'wsl grep -c LoadStartModule …; grep NVRAM …; wc -l …/t34-poll.log'  # 18; has not changed; 126
ssh bytesize 'wsl ls …/t34-*.jpg'                                      # 46 JPGs (title at poll01)
ssh bytesize 'wsl cp <30 chain jpg + poll.log + census/samples> /mnt/c/…'  # (explicit list, one wsl call)
ssh bytesize 'wsl cp <16 sj/mr jpg> /mnt/c/…'                          # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t34-…" /tmp/t34-fetch/                         # 46 jpg + logs (r1-prefixed local)
# R1 post-hoc (local fastdiff): chain panel, xrun pairs, 28 arrival pairs, census set-compare
ssh bytesize 'wevtutil …' > /tmp/t34-eventlog-post.txt                # head H11-teardown 02:34:12; H10→H11 02:17:57/02:21:30; no in-window entries
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H12 …2589 (fresh, created by this call)
ssh bytesize 'wsl sha256sum …/bios/….nvm; ls -la …/bios/; sha256sum …/logs/emulog.txt; ls -la …/logs/; df -h / /mnt/c'  # da021d2a… untouched; e7b19750… re-verified; 22 emulogs; C: 17G
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t34-20260921T062214Z.txt …/logs/emulog-pre-t33-20260921T054304Z.txt'  # 757497b8… T33R2 + 1915aaf9… T33R1 preserved
ssh bytesize 'wsl grep -m1 -n BIOS\\ Found …; grep -m1 -n ExecPS2 …'    # L2; L142330
ssh bytesize 'wsl head -n 2000 <trace>' > t34r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t34r1-trace-tail.txt         # 2000 lines, clean tail @458.1406
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t34r1.txt; ls -la …'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t34r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t34r1.txt"         # e7b19750… match
ssh bytesize 'wsl dmesg' > /tmp/t34-dmesg-post-h12.txt                # 481 lines, 0 kills (H12)
# report (chunks; receipts include tail -3)
cp /tmp/t34-dmesg-*.txt /tmp/t34-eventlog-*.txt /tmp/t34r1-run-stdout.txt … local/research/T34/  # renamed per §evidence
tail -3 local/research/T34/REPORT.md
git add -f local/research/T34/<63 files by name>                      # ignored dir, forced
git commit -m "[T34] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T34-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (pre-race panel) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → Cross on Snow Jam → MR-LIKE gate (departed + non-SE + static) → ≤3 attempts) → pre-race panel (`Snow Jam - Race`, `X Continue`); then a single 534 ms Cross (X Continue) to start the race, screenshot-verify the countdown/live gameplay. Gate note: the MR→load whole-frame hop is decisive (~12.43–12.47 remote/PIL), so DEPARTED > 5.0 fires normally on the Enter transition; but the load→panel path is multi-stage (loading % → black → cinematic → panel over ~30 s), so the next arrival gate needs a settled-panel criterion (static + non-MR + a pre-race ref from `t34r1-mr-stab6.jpg`, PIL `convert('RGB').save` recipe) rather than a first-change trigger — gate on the panel, not the load. The black frame at +8 s (21267 B) is a transition, not an arrival. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The arrival panel is static (98 s, no reclaim) so no dwell pressure on arrival→next presses |
| G2 | Zero flaps this session + 2 mid-session-era restarts (H10→H11 pre-R1, H11→H12 post-everything, not by me) | 0 userland kills on any VM this session (H10 pre 440 lines, H11 post-R1 451 lines with full R1-window coverage, H12 481 lines — all 0 kills; every ssh exit 0) + 1 pre-session VM restart between T33 and T34 (H9→H10; T33: 2 flaps + 2 pre-session restarts) + 1 mid-session VM restart between staging and R1 (H10 06:15:09→06:17:57, H11 create 06:21:30; 213 s gap with no VM; every ssh exit 0 across it; staged files persist on the same VHD, shas re-verified) + 1 post-everything VM restart (H11→H12 06:34:12; only final state reads + trace slices ran on H12). R1 completed exit 0 with zero in-window flaps on the dmesg record — no T27 §4 effects-verification needed (the immediate post-run dmesg read closed T33's sequencing gap). Precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero in-window entries; boundaries bound both restarts | Newest-30 reads (pre/post): H9 teardown 01:57:29 → H10 create 02:15:09 → H10 teardown 02:17:57 → H11 create 02:21:30 → H11 teardown 02:34:12; zero entries inside the R1 window 02:22:14–02:30:02 (precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H10 btime |
| G4 | Hold count 69/69 | 534 ms-class holds register 69/69 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33+T34 (T34 R1: 536.8/537.6/536.8/536.9/535.1/536.5/536.8/535.4/535.6 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/SC/ZC/SP/SM/SE/MR frozenness; attract differs; snowflake shimmer on SE + MR; panel animation on arrival | Title text-band frozen across showings (0.0467/1 R1); R1's 5 frames bit-identical to T33 R2's run (a1-poll01/pre, a1-post3/8/25 — the attract/title/menu timing lottery landed back on T33-R2's=T31's phase) and menupre bit-identical to T33 R1's run; a1-post15 xrun 0.0003/0 max 5 again (single-px JPEG shimmer); menu whole-frame ≤0.065/p99 ≤1 cross-run; SC cross-run 0.07–0.24/p99 1–5; ZC cross-run 0.06–0.32/p99 1–9; SP cross-run ≤0.06/p99 0; SM cross-run 0.005–0.06/p99 0–1; Select Event ≤0.13/p99 ≤1 cross-run (rc-post8 snowflake animation); My Rules ≤0.15/p99 ≤3 (snowflake drift); pre-race panel ≤0.40/p99 ≤18 over 98 s (panel shimmer/animation — widest arrival spread to date, still far under any gate). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the game-load run | `WaitVblankStart` stops after log ≤90 in T34 R1 including game load + race intro + pre-race arrival (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T33-R2-identical modulo counts). The attract/title/menu/submenu/game sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical; EE count jumps) | Like prior arrivals, game-load/intro arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T33 R2; counts shift EE-ward (`GetThreadId` 1.58M→4.52M, EE total 5.75M→10.99M; IOP 18.65M→17.25M; `sceSdGetParam` 1652→1963, `sceSdGetAddr` 3.73M→3.39M). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~27 GB across 22 emulogs (T17→T34 chain, all preserved); C: 17 G avail (pre 20 G — run staging + traces; T33 pre was 24 G). T34 R1 full trace SSD-copied + sha-verified (2.53 GB: `emulog-t34r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T34 brief cites `t33r2-sj-post{1,3,8,15,25,40}.jpg` + `t33r2-sj-stab{1…6}.jpg` — all 12 exist with full shas+sizes reproducing T33 §T33-2; the PIL `convert('RGB').save` ref recipe reproduces byte-exactly (PPM-vs-JPEG 0.0000/0). T28 G9 lesson holds |
| G10 | Session wall + run durations | ~45 min active of the 4 h box (one run + report/commit); zero lease waits (no lease exists for T34). R1 wall 468 s — 108 s over the ≤6 min guidance (added MR-phase scoring + arrival tail); R1 full dmesg coverage, zero flaps |
| G11 | X11 mount landed on the wrong generation, again harmless | The `/tmp/.X11-unix` tmpfs mount ran on VM-H10 and was wiped by the H10→H11 restart; re-mounted on H11 pre-R1, R1 started Xvfb :99 cleanly regardless (exit 0 + 46 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 / T33 G11 stand) |
| G12 | Remote-vs-PIL gap receipted on the MR whole bar: ~3–5×, bar holds even remotely | Follow-up to T33 G12's chicken-and-egg: R1's in-script vs-mr receipt reads 0.40–0.46/p99 7–8 on MR-side PIL 0.08–0.15 (≈3–5× inflation at the ~0.1 scale — milder than the ~6–11× seen at the ~0.04 scale), so the < 2.0 whole bar would have held even as an in-script leg (4.3× margin). The TAG-crop gap re-confirmed at ~280× (2.6271 vs 0.0094). Standing pattern holds: whole-frame bars calibrated in PIL transfer to remote with single-digit inflation near zero and ~1× at scale ≥5; text-dense crops need remote receipts or generous bars |

## Evidence files

`REPORT.md` (this file),
scripts: `t34-auto.sh`,
`t34-cropdiff.py` (T33 logic, byte-identical),
`t34-analyze.sh`, `t34-vcount.sh` (byte-identical);
R1: `t34r1-start.jpg`, `t34r1-a1-now.jpg`, `t34r1-a1-poll01.jpg`,
`t34r1-a1-pre.jpg`, `t34r1-a1-post{3,8,15,25}.jpg`, `t34r1-menupre.jpg`,
`t34r1-mc-post{1,3,8,15}.jpg`, `t34r1-scpre.jpg`,
`t34r1-zc-post{1,3,8}.jpg`, `t34r1-ccpre.jpg`,
`t34r1-sp-post{1,3,8}.jpg`, `t34r1-sppre.jpg`,
`t34r1-pc-post{1,3,8}.jpg`, `t34r1-smpre.jpg`,
`t34r1-rc-post{1,3,8}.jpg`, `t34r1-sepre.jpg`,
`t34r1-sj-post{1,3,8}.jpg`, `t34r1-mrpre.jpg`,
`t34r1-mr-post{1,3,8,15,25,40}.jpg`, `t34r1-mr-stab{1…6}.jpg` (46 snaps),
`t34r1-census.txt`, `t34r1-samples.txt`, `t34r1-poll.log`,
`t34r1-stdout.txt`, `t34r1-stderr.txt`, `t34r1-trace-head.txt` / `t34r1-trace-tail.txt`;
flaps: `t34-dmesg-vmH10-pre.txt` (0 kills on H10, pre-run) /
`t34-dmesg-vmH11-post.txt` (0 kills on H11; full R1-window
coverage) / `t34-dmesg-vmH12-post.txt` (0 kills on H12, fresh boot),
`t34-eventlog-pre.txt` / `t34-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t34r1.txt`
(2,526,769,871 B `e7b19750…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T33 R2
`…-20260921T062214Z.txt` `757497b8…` and T33 R1
`…-20260921T054304Z.txt` `1915aaf9…`.
