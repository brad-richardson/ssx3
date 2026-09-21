# T31 report — Cross on Peak 1 from the Select Peak park: next screen (bytesize, no lease)

Brief: T31 (Cross on Peak 1 from the Select Peak park). Tables, no
verdicts. One boot ran on bytesize; laptop-side work was ssh/scp + local
reads/analysis only. Time box 4 h; session wall ~03:54–04:16 UTC
2026-09-21 (~22 min + report/commit).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); a Select Peak reference PPM derived from T30's
`t30r1-cc-stab6.jpg` added a whole-frame SP gate (mean < 2.0; calibration
SP-SP 0.0046–0.0832/p99 0, ZC-vs-SP 9.35–9.38, SC-vs-SP 11.35,
menu-vs-SP 10.39, title-vs-SP 15.37). One single-shot run: chain
reproduced (TITLE at poll01 0.4331/6, Start ≤ 1.0 s after exposure,
menu-like gate → Menu Cross @T+138.11 → Select Character by +1 s,
SC-LIKE gate → Zoe Cross @T+178.02 → Setup Character by +1 s, ZC-LIKE
gate → Continue Cross @T+206.68 → Select Peak by +1 s, SP-LIKE gate → 4
park snaps whole-vs-stab6 0.005–0.077/p99 0), Peak Cross @T+235.37 →
Select Mode (Race highlighted) by +1 s, stable across 12 snaps / 132 s
(pairwise 0.014–0.066/p99 ≤1). Full dmesg coverage on VM-H4 (no restart
this session; 7 userland flaps, 5 pre-run + 2 post-run, zero inside the
run window); 1 pre-session VM restart between T30 and T31. NVM
`da021d2a` untouched throughout. EE/IOP name sets identical to T30 R1
(52/155); `sceSdGetParam` 1006 → 1266.

Stale-reading guard: `local/research/T30/REPORT.md` (all: R1 reached Select
Peak via Cross on Continue @T+206.24, Peak 1 highlighted (orange bar) /
Peak 2–3 locked, tagline `Choose this peak and continue to select mode.`,
12 snaps over 131 s pairwise ≤0.10/p99 ≤1, no reclaim; G1 proposes one
534 ms Cross (× Select) on Peak 1). This brief executes T30's G1.

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
parked Select Peak (Peak 1 highlighted) chooses Peak 1 / enters the next
screen; observable — pre-press snap = Select Peak (whole-frame match vs
T30 `cc-stab6` ref), post-press snap series + per-hop whole diffs +
arrival stability N; screen content read off viewed snaps; alternatives —
screen ignores Cross (post series still Select Peak), slow next-screen
load (change lands late in the +40 s tail), press never acted on arrival
(pre-press ≠ Select Peak → ONE bounded variant allowed); stop — table the
exact observed behavior + recipe, no button-mashing survey.

## T31-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T31; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T31]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T31 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` (at `…/pcsx2-t4/pcsx2`; the parent dir is not a repo) | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| NVM end | — | same sha, same mtime (untouched throughout) | yes |
| Pad binding | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Title ref present | — | `t27-ref-title.ppm` 3932177 B sha `b964856a…e94f59` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` 3932177 B sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` 3932177 B sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` 3932177 B sha `212b0970…f79f722` reproduces T30 | yes |
| T30 reference snaps present | — | all 12 arrival shas reproduce T30 §T30-2 (`post{1,3,8,15,25,40}` + `stab{1…6}` sha12 + sizes) | yes |
| Free space | — | WSL `/` 898 G avail; C: 31 G (836 G); laptop `/` 13 Gi avail; SSD 445 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1 (VM-H4) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t31-{auto,analyze,vcount,cropdiff}.sh/.py`, `t31-ref-sp.ppm` (3,932,177 B, sha `1a8b1ed9…d22b40`), `t31-{r1-census,samples}.txt` (via analyze), `t31-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t31-*.txt` (rotation chain, see trace table), `boot-t31.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t31*` + `emulog-t31r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 0 this session; 1 pre-session restart between T30 and T31 (H3→H4; parallel briefs active — inference, T25 G2 precedent) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H4 btime:
23:54:04→`1789962843`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 03:43:33 | VM-H3 teardown (IDs 71/69/233/234/234, after T30's session) | eventlog-pre tail |
| 2 | 03:54:04 ([0] VM-H4) | VM-H4 started fresh ~34 s before first ssh | btime `…2843`, eventlog-pre head (IDs 291/102/232/233/67/292) |
| 3 | 03:55:28–03:59:11 ([83.88]–[306.84]) | Flaps #1–#5 on VM-H4, ALL pre-run (each ssh still exit 0) | `t31-dmesg-vmH4-pre.txt` (0 kills) + post (5 kills ≤306.84; pre capture predates the first flap) |
| 4 | 04:00:22–04:06:43 ([378]→[759] VM-H4) | R1 single-shot exit 0, `T31_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart) | exit 0, snaps, trace sha |
| 5 | 04:06:58, 04:07:33 ([774.28],[809.44]) | Flaps #6–#7 on VM-H4, ALL post-run (every transfer exit 0 + sha-verified after) | `t31-dmesg-vmH4-post.txt` (7 `AcceptAsync`) |
| 6 | event log | Newest-30 reads (pre/post): head stays H4-create 23:54:04, tail H3-teardown 23:43:33; zero entries at any of the 7 flap times and zero VM-boundary events inside the run window — userland kills leave no Windows trace (T17/T21/T23/T25/T27/T28/T29/T30 precedent stands) | `t31-eventlog-{pre,post}.txt` |
| 7 | dmesg noise | `dxg dxgkio_* Ioctl failed` lines 23 (pre) → 184 (post), same 3 shapes (152 `query_adapter_info -2`, 24 `query_adapter_info -22`, 8 `is_feature_enabled -22`) — steady boot/GPU-query noise, not kills | `t31-dmesg-vmH4-{pre,post}.txt` |

## T31-1. SP detector + calibration (thresholds, match scores)

Tool: `t31-cropdiff.py` (copy of T30's, unmodified logic — byte-identical;
`t31-vcount.sh` likewise). Title text-band method unchanged (thresholds
frozen: TITLE band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU
whole-vs-menu mean < 2.0; NONMENU whole-vs-menu mean > 5.0; NONSC
whole-vs-SC mean > 5.0; NONZC whole-vs-ZC mean > 5.0; DEPARTED whole hop
mean > 5.0). New: Select Peak reference `t31-ref-sp.ppm` (3,932,177 B, sha
`1a8b1ed9…d22b40` full `1a8b1ed95ae3c9e39a6f8f1e7c0b2f8a00023ae8edcbbd59264cc3f1a6d22b40`),
derived from T30's `t30r1-cc-stab6.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T31-4; T28
§T28-1 recipe).

SP calibration matrix (candidate vs `t30r1-cc-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post1 vs stab6 | 0.0267 | 0 | 28 | SP-SP (whole) |
| post3 vs stab6 | 0.0459 | 0 | 52 | SP-SP (whole) |
| post8 vs stab6 | 0.0046 | 0 | 24 | SP-SP (whole) |
| post15 vs stab6 | 0.0252 | 0 | 52 | SP-SP (whole) |
| post25 vs stab6 | 0.0832 | 0 | 53 | SP-SP (whole, worst mean) |
| post40 vs stab6 | 0.0062 | 0 | 23 | SP-SP (whole) |
| stab1 vs stab6 | 0.0185 | 0 | 41 | SP-SP (whole) |
| stab2 vs stab6 | 0.0141 | 0 | 28 | SP-SP (whole) |
| stab3 vs stab6 | 0.0051 | 0 | 30 | SP-SP (whole) |
| stab4 vs stab6 | 0.0201 | 0 | 41 | SP-SP (whole) |
| stab5 vs stab6 | 0.0200 | 0 | 50 | SP-SP (whole) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| ccpre (T30 ZC) vs stab6 | 9.3465 | 153 | 230 | ZC-vs-SP (whole) |
| zc-post8 (T30 ZC) vs stab6 | 9.3770 | 153 | 230 | ZC-vs-SP (whole) |
| scpre (T30 SC) vs stab6 | 11.3615 | 159 | 255 | SC-vs-SP (whole) |
| mc-post15 (T30 SC) vs stab6 | 11.3505 | 158 | 255 | SC-vs-SP (whole) |
| menupre (T30) vs stab6 | 10.3853 | 170 | 239 | menu-vs-SP (whole) |
| a1-post15 (T30 menu) vs stab6 | 10.3855 | 170 | 239 | menu-vs-SP (whole) |
| a1-pre (T30 title) vs stab6 | 15.3703 | 156 | 251 | title-vs-SP (whole) |
| start (T30 attract) vs stab6 | 15.6958 | 172 | 244 | attract-vs-SP (whole) |
| ref PPM vs stab6 JPEG | 0.0000 | 0 | 0 | recipe exact (JPEG decode deterministic) |
| ref PPM vs ref PPM | 0.0000 | 0 | 0 | self |

SP gate (frozen before R1): in-script park criterion = DEPARTED
(ccpre→post1 hop > 5.0) AND NONZC (post8 vs-zc > 5.0) AND whole-static
(sp hops post1→post3 and post3→post8 both < 1.0); the vs-sp line
classifies the park. The Peak Cross press does NOT depend on a strict SP
gate (T28 MENU / T29 SC / T30 ZC precedent); the post-hoc "Cross acted on
SP" bar is whole-vs-SP-ref mean < 2.0 PIL + viewed snap. Margins: park
departure-side 9.33 vs 5.0 (1.9×); park nonzc-side 9.37 vs 5.0 (1.9×);
post-hoc SP-side worst 0.0832→24×; post-hoc non-SP-side nearest
9.35→4.7×.

Script deltas vs `t30-auto.sh` (committed originals untouched; `t31-auto.sh`
is the adapted copy):

| Area | T30 R1 script | T31 script |
|---|---|---|
| Chain | park phase + MENU Cross + mc series to +15 + scpre + ZOE Cross + zc series to +8 + ccpre + CONT Cross + cc series to +40 + 6×10 s stab | identical through CONT Cross; cc series shortened to sp-post1/3/8 (each + vs-sp score; vs-sc/vs-menu post-hoc local), T30's +40 s tail moves to the Peak arrival |
| SP park | (arrival was the end) | SP-park gate (departed + non-ZC + static) + `sppre` snap (vs-sp + vs-zc + titleband) |
| T31 press | — | ONE `PEAK_CROSS` (K), arrival series +1/+3/+8/+15/+25/+40 (each titleband + vs-sp + vs-zc), 6 per-hop whole diffs, 6×10 s arrival stability |
| Self-tests | SELF_TEST + SELF_WHOLE + SELF_MENU + SELF_SC + SELF_ZC | + SELF_SP (SP ref vs itself through `score_sp`) |
| No-park paths | explicit `NO-PARK` + `NO-SC-PARK` + `NO-ZC-PARK` | + explicit `NO-SP-PARK` plog, still clean shutdown + `T31_DONE` (trace preserved) |

## T31-2. R1 — park reproduced, Cross → Select Mode

Run: `t31-auto.sh`, ONE fresh boot (skip re-confirmed: T+94 attract),
T_BOOT wall 1789963222 (uptime 378, VM-H4), 04:00:22–04:06:43 UTC (uptime
378→759 = 381 s; 21 s over the ≤6 min guidance — the added SP-phase
scoring; full dmesg coverage, zero in-window flaps), WID 2097159, exit 0,
`T31_DONE`, clean SIGTERM shutdown. SELF_TEST 0.0000/0, SELF_WHOLE
0.0000, SELF_MENU 0.0000/0, SELF_SC 0.0000/0, SELF_ZC 0.0000/0, SELF_SP
0.0000/0. Attempt 1 of ≤3 consumed; attempts 2–3 not needed (Cross
advanced, arrival mapped).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+98, score 0.4331/6 remote / 0.0467/1 PIL (T30: 0.4329/6 / 0.0468/1 — band-frozen, see identities) | Cross 534.9 ms @T+95.70 (attract-skip) + Start 537.5 ms @T+98.97 (on title, ≤1.0 s after exposure) | Main Menu by +3 s; menu-like gate (non-title + whole-static 0.0337/0.0114) + post25-vs-menu 0.2946/5 → park for menu Cross |
| A2–A3 | not run (Cross advanced) | — | — |

Cross-run frame identities (T31 R1 vs T30 R1, full sha256):

| Frame | T31 sha | T30 sha | Identity |
|---|---|---|---|
| a1-post15 | `f90c4e4f6859…` | `4c56f815…cc44565` | differ in whole sha (bit-identity streak ends at 4 runs); pair 0.0004/0 max 7 (single-px JPEG shimmer) |
| a1-post3 | `45bcb1c63256…` | `f1287a7be3a6…` | differ in whole sha (bit-identity streak ends at 2 runs); pair 0.0574/1 |
| start | `2da39c9bbbd2…` 65750 B | `3dc447a9b2f5…` 49769 B | differ; pair 14.83/146 (attract-loop phase differs this run) |
| a1-poll01 = a1-pre | `d977309dd891…` (cp-identical) | `6e3d747fd514…` | differ in whole sha; band-frozen (0.0467/1 vs 0.0468/1); whole pair 0.0358/0 |
| a1-post8/post25 | differ | differ | whole pairs 0.0454/0, 0.0317/0 |
| menupre | differ | differ | whole pair 0.0028/0 (same as T30-vs-T29) |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.057/0, 0.111/3, 0.071/1, 0.026/1 (tighter than T30-vs-T29's 0.12–0.17) |
| scpre | differ | differ | whole pair 0.0561/0 |
| zc-post1/3/8 | differ | differ | whole pairs 0.117/3, 0.127/3, 0.195/5 |
| ccpre | differ | differ | whole pair 0.2156/6 |
| sp-post1/3/8 vs cc-post1/3/8 | differ | differ | whole pairs 0.067/1, 0.061/0, 0.002/0 (park reproduced tightly) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789963317.697213685 → 1789963318.232121716 | 534.9 ms | T+95.70→96.23 | 473→474 | `a1-now` attract (25.1806/194 remote; 25.1764/194 PIL) | `a1-poll01` TITLE (0.4331/6; 0.0467/1) |
| A1 Start (Return) | 1789963320.969230153 → 1789963321.506727375 | 537.5 ms | T+98.97→99.51 | 477 | `a1-pre` ≡ `a1-poll01` (sha `d977309dd891`, TITLE, viewed) | `a1-post3` Main Menu (16.2559/139; 16.2584/138) |
| MENU Cross (K) | 1789963360.112043614 → 1789963360.646760984 | 534.7 ms | T+138.11→138.65 | 516 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2871/5 remote; 0.0275/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2176/106; vs-sc 0.4988/8; titleband 12.5493/164) |
| ZOE Cross (K) | 1789963400.020112496 → 1789963400.556266031 | 536.2 ms | T+178.02→178.56 | 556 | `scpre` Select Character, Zoe selected (vs-sc 0.5699/8 remote; 0.2236/4 PIL; vs-menu 10.1961/105; vs-title 12.6596/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.2295/100; vs-zc 0.5292/9; titleband 15.9324/128) |
| CONT Cross (K) | 1789963428.680634953 → 1789963429.215815887 | 535.2 ms | T+206.68→207.22 | 584→585 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4057/7 remote; 0.1683/4 PIL; vs-sc 7.2706/100; vs-title 15.7993/128 — viewed) | `sp-post1` Select Peak (vs-zc 9.4955/154; vs-sp 0.4021/6; titleband 23.1261/171) |
| PEAK Cross (K) | 1789963457.365809541 → 1789963457.901575138 | 535.8 ms | T+235.37→235.90 | 613→614 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.4233/6 remote; 0.0767/0 PIL; vs-zc 9.5208/154; vs-title 23.1279/171 — viewed) | `pc-post1` Select Mode (vs-sp 5.3746/121; vs-zc 10.2113/164; titleband 26.3170/183 — viewed) |

Within-dwell receipts: Cross-keyup → Start-keydown 2.737 s; poll01 snap
exposure (04:02:00 UTC, 1 s resolution) → Start-keydown 04:02:00.969 ≤
1.0 s; R2-measured title persistence 15–17 s ⇒ press inside the window
with an order of magnitude to spare. Start-keyup → MenuCross-keydown
38.6 s; MenuCross-keyup → ZoeCross-keydown 39.4 s; ZoeCross-keyup →
ContCross-keydown 28.1 s; ContCross-keyup → PeakCross-keydown 28.2 s (no
dwell pressure — all parks static, T27 G1 / T28 G1 / T29 G1 / T30 G1
precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-JPEG / whole vs ZC-ref / whole vs SP-ref)

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Content |
|---|---|---|---|---|---|---|---|
| start (T+94) | 65750 B / `2da39c9bbbd2` | 24.9901/150 | — | — | — | — | Attract (phase differs from T30) |
| a1-now (T+94, pre-Cross) | 63359 B / `83764ce672f3` | 25.1764/194 | — | — | — | — | Attract |
| a1-poll01 = a1-pre (T+98, pre-Start) | 58352 B / `d977309dd891` | 0.0467/1 T | — | — | — | — | TITLE (viewed) |
| a1-post3 (T+103) | 49966 B / `45bcb1c63256` | 16.2584/138 | 0.0647/1 | — | — | — | Main Menu |
| a1-post8 (T+108) | 50015 B / `91771d70d2bb` | 16.2939/138 | 0.0628/1 | — | — | — | Main Menu |
| a1-post15 (T+115) | 49618 B / `f90c4e4f6859` | 16.2622/138 | 0.0260/0 | — | — | — | Main Menu |
| a1-post25 (T+125) | 49749 B / `36569614475c` | 16.2622/138 | 0.0394/0 | — | — | — | Main Menu |
| menupre (T+137, pre-MCross) | 49608 B / `615b78f1c60b` | 16.2622/138 | 0.0275/0 | — | — | — | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+142) | 70231 B / `5c5b539136b8` | 12.4784/163 | 10.1503/106 | 0.1503/3 | — | — | Select Character, Zoe |
| mc-post3 (T+145) | 70490 B / `d901b53e2fcc` | 12.4814/163 | 10.1585/107 | 0.1554/3 | — | — | Select Character |
| mc-post8 (T+150) | 70246 B / `f7ab37a87d0f` | 12.4587/163 | 10.1501/105 | 0.2585/4 | — | — | Select Character |
| mc-post15 (T+157) | 70033 B / `8f463ea3d79a` | 12.4587/163 | 10.1291/105 | 0.0028/0 | — | — | Select Character |
| scpre (T+176, pre-ZCross) | 70215 B / `6f83e4eab3e9` | 12.5834/163 | 10.1289/105 | 0.2236/4 | — | — | Select Character, Zoe selected (viewed) |
| zc-post1 (T+182) | 51528 B / `675eceb9aabe` | 15.9063/129 | 6.9272/93 | 7.2014/100 | 0.2973/7 | — | Setup Character, Zoe |
| zc-post3 (T+185) | 51609 B / `ffd35538ff78` | 15.8123/128 | 6.9098/92 | 7.2668/101 | 0.2371/6 | — | Setup Character |
| zc-post8 (T+190) | 51340 B / `d0bca8090bd2` | 15.8302/128 | 6.9309/92 | 7.1079/100 | 0.2460/6 | — | Setup Character |
| ccpre (T+205, pre-ContCross) | 51449 B / `dd2168682e4c` | 15.7837/128 | 6.8964/92 | 7.2447/100 | 0.1683/4 | — | Setup Character, Zoe + Continue (viewed) |
| sp-post1 (T+210) | 65513 B / `4f8bb01e943e` | 23.1240/171 | 10.4556/170 | 11.3789/158 | 9.4151/153 | 0.0591/0 | Select Peak, Peak 1 |
| sp-post3 (T+213) | 65441 B / `ec1cdc959fcb` | 23.1259/171 | 10.4368/170 | 11.3780/158 | 9.3836/153 | 0.0477/0 | Select Peak |
| sp-post8 (T+218) | 65218 B / `2430d2441b4e` | 23.1245/171 | 10.4069/170 | 11.3499/158 | 9.3723/153 | 0.0053/0 | Select Peak |
| sppre (T+233, pre-PeakCross) | 65624 B / `661907a52713` | 23.1259/171 | 10.4738/170 | 11.4200/158 | 9.4422/153 | 0.0767/0 | Select Peak, Peak 1 highlighted (viewed) |
| pc-post1 (T+239) | 67644 B / `838989bc8bbf` | 26.3046/183 | 10.9392/178 | 11.8260/157 | 10.1259/164 | 5.2074/121 | Select Mode, Race (viewed) |
| pc-post3 (T+242) | 67459 B / `4c91192d5191` | 26.3046/183 | 10.9139/178 | 11.8034/157 | 10.1011/164 | 5.1814/121 | Select Mode |
| pc-post8 (T+247) | 67675 B / `b29efe3b1385` | 26.3335/183 | 10.9468/178 | 11.8147/157 | 10.1304/164 | 5.2167/121 | Select Mode |
| pc-post15 (T+254) | 67390 B / `4e6f28bbdc0d` | 26.3058/183 | 10.9141/178 | 11.7991/157 | 10.1027/164 | 5.1830/121 | Select Mode |
| pc-post25 (T+264) | 67469 B / `927b3fb24675` | 26.3046/183 | 10.9148/178 | 11.8047/157 | 10.1030/164 | 5.1820/121 | Select Mode |
| pc-post40 (T+279) | 67366 B / `9677e898c041` | 26.3015/183 | 10.9272/178 | 11.7899/157 | 10.1131/164 | 5.1963/121 | Select Mode |
| pc-stab1 (T+312) | 67337 B / `7a48d514737c` | 26.3044/183 | — | — | 10.0974/164 | 5.1768/121 | Select Mode |
| pc-stab2 (T+324) | 67576 B / `ebd86ed15d87` | 26.3046/183 | — | — | 10.1264/164 | 5.2069/121 | Select Mode |
| pc-stab3 (T+336) | 67680 B / `d0a77414fc4b` | 26.3404/183 | — | — | 10.1306/164 | 5.2171/121 | Select Mode |
| pc-stab4 (T+347) | 67355 B / `51a7026c5fab` | 26.3061/183 | — | — | 10.0976/164 | 5.1767/121 | Select Mode |
| pc-stab5 (T+359) | 67599 B / `1e5aa70ed358` | 26.3046/183 | — | — | 10.1274/164 | 5.2084/121 | Select Mode |
| pc-stab6 (T+371) | 67572 B / `4cb2f586411b` | 26.3298/183 | 10.9386/178 | 11.8127/157 | 10.1252/164 | 5.2099/121 | Select Mode, Race (viewed) |

In-script (remote) vs PIL agreement: ≤0.17 mean on menu/title-band/
vs-sp scores at scale (e.g. sppre band 23.1279 vs 23.1259; pc-post1
vs-sp 5.3746 vs 5.2074; pc-post1 vs-zc 10.2113 vs 10.1259 with p99
164/164); the known ~6× remote-lossless gap on near-zero means (poll01
band 0.4331/6 remote vs 0.0467/1 PIL; sppre vs-sp 0.4233/6 vs 0.0767/0 —
T27 title / T28 menu / T29 SC / T30 ZC precedent); hops ≤0.03.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1223 | 10.1299/105 | screen change within +1 s (T30: 10.1193/10.1268) |
| post1 → post3 (mc) | 0.1169 | 0.1442/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2662 | 0.2903/7 | same screen |
| post8 → post15 (mc) | 0.2407 | 0.2602/4 | same screen |
| post15 → scpre (park span) | — | 0.2253/4 | same screen |
| scpre → zc-post1 | 7.2212 | 7.2443/100 | screen change within +1 s (T30: 7.2200/7.2429) |
| post1 → post3 (zc) | 0.3100 | 0.3331/9 | arrival settling/shimmer |
| post3 → post8 (zc) | 0.2947 | 0.3152/7 | same screen |
| post8 → ccpre (park span) | — | 0.2880/7 | same screen |
| ccpre → sp-post1 | 9.3463 | 9.3826/153 | screen change within +1 s (T30: 9.3257/9.3619) |
| post1 → post3 (sp) | 0.0923 | 0.1002/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0412 | 0.0457/0 | same screen |
| post8 → sppre (park span) | — | 0.0743/0 | same screen |
| sppre → pc-post1 | 5.2452 | 5.2686/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0345 | 0.0365/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0420 | 0.0486/0 | same screen |
| post8 → post15 (pc) | 0.0435 | 0.0522/1 | same screen |
| post15 → post25 (pc) | 0.0111 | 0.0144/0 | same screen |
| post25 → post40 (pc) | 0.0228 | 0.0264/0 | same screen (idle shimmer) |
| post40 → stab1 (pc) | — | 0.0219/0 | same screen |
| stab1 → stab6 (pc) | — | 0.0361/0 | same screen |
| post1 → stab6 (pc span) | — | 0.0662/0 | arrival endpoints near-identical |

### R1 arrival (Select Mode)

| Item | Value |
|---|---|
| Arrival snap | `t31r1-pc-post1.jpg` @T+239 (+1 s after Peak Cross keyup; no intermediate screen captured at +1 s cadence) |
| Stability N | 12 snaps (post1/3/8/15/25/40 + stab1–6) spanning T+239→T+371 (132 s) |
| Whole-frame pairwise (PIL) | 0.014–0.066/p99 0–1 (idle shimmer; JPEG shas distinct) |
| Vs-SP (whole) | 5.18–5.22/p99 121 across all 12 (not Select Peak) |
| Vs-ZC (whole) | 10.10–10.13/p99 164 across all 12 (not Setup Character) |
| Vs-menu (whole) | 10.91–10.95/p99 178 across 7 scored (not menu) |
| Vs-SC (whole) | 11.79–11.83/p99 157 across 7 scored (not Select Character) |
| Vs-title (band) | 26.30–26.34/p99 183 across all 12 (not title) |
| What is highlighted/selected | "Select Mode" header; `Race` (highlighted, orange bar) / `Freestyle`; Peak 1 course-map panel (race/freestyle course lines); tagline `Choose a mode and continue to select event.`; footer `× Select`, `△ Previous` |
| Reclaim after arrival? | none observed in 132 s (all 12 snaps Select Mode) |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Arrival park reproduced (snap match vs T30's `t30r1-cc-stab6.jpg`) | sp-post1/3/8 + sppre whole-vs-stab6 0.005–0.077/p99 0 (all under the 2.0 gate AND inside T30's own 0.0046–0.0832 spread); a1-post15 near-identical 0.0004/0 (bit-identity streak ends at 4) |
| Cross acted on it (pre-press = Select Peak, Peak 1 highlighted) | `sppre` vs-sp 0.4233/6 remote, 0.0767/0 PIL; viewed: Select Peak, Peak 1 highlighted (orange bar), Peak 2–3 locked, tagline `Choose this peak and continue to select mode.` |
| Next-screen snaps + stability N | 12 snaps over 132 s, pairwise ≤0.066/p99 ≤1, endpoints 0.0662/0 |
| Full input log + trace sha | `t31r1-poll.log` (82 lines: every score + press, walls + uptimes) + trace `8cbf2827…896d081e` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30
(BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725, first vblank
L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen
(all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean
tail @370.38. Census: EE 5,199,563 (52, set-identical to T30 R1) · IOP
16,241,047 (155, set-identical to T30 R1 — Select Mode arrival adds no
new called API) · `libsd.006: sceSdGetParam` 1266 (R1-T30: 1006);
`sceSdGetAddr` 3,207,744 (R1-T30: 2,943,888).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (A1, TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate) |
| Cross on Peak 1? | YES (PEAK Cross @T+235.37, pre-press = Select Peak, Peak 1 highlighted) |
| Next screen reached? | YES (Select Mode @T+239, stable 132 s) |
| Bounded variant? | Not needed (first press provably acted on the Select Peak park) |
| 1200 s cap | Not reached — run ≈ T+381; attempts 2–3 unexercised |
| Chain end | Select Mode, Race highlighted, awaiting input |

## T31-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t31 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode, T+~381) | 31,999,707 / 2,112,217,704 | `8cbf2827…896d081e` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t31r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t31r1-trace-head.txt` 149019 B sha `80651553c74d…`, `t31r1-trace-tail.txt` 134803 B sha `ef1c8968b9d2…`) |
| `emulog-pre-t31-20260921T040022Z.txt` = t30 R1 (preserved at R1 boot) | — / 1,966,668,019 | `48713961…e609e360` (re-verified post-run: matches T30) | bytesize-only (T30 precedent; SSD holds T30's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 5,199,563 (52
distinct, set-identical to T30 R1) · IOP 16,241,047 (155, set-identical
to T30 R1) · vblanks 397. Committed: `t31r1-census.txt`, `t31r1-samples.txt`,
`t31r1-poll.log` (82 lines), `t31r1-stdout.txt` (full `set -x` shell trace,
1607 lines).

## T31-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H4 …2843
ssh bytesize 'wsl dmesg' > /tmp/t31-dmesg-pre.txt                     # 441 lines, 0 kills (pre-dates first flap)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t31-eventlog-pre.txt  # head 23:54:04
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini; ls -la …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm'  # da021d2a… / :579 K / sizes
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm; ls -la …t30-ref-zc.ppm; sha256sum …t30-ref-zc.ppm'  # b964856a… / 8f34385f… / dd7e4716… / 212b0970…
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c; du -sh …/logs/'          # 898G / C: 31G / 16G
# T30 ref snaps (local): 12/12 sha12+sizes reproduce T30 §T30-2
# calibration (local; t31-cropdiff.py = T30 copy, byte-identical)
python3 t31-cropdiff.py <12 SP> /tmp/t31-ref-sp.ppm 0,0,1280,1024  # SP-SP 0.0046–0.0832 / p99 0
python3 t31-cropdiff.py <ZC/SC/menu/title/attract> … 0,0,1280,1024   # ZC 9.35–9.38, SC 11.35, menu 10.39, title 15.37, attract 15.70
python3 -c "Image.open(cc-stab6).convert('RGB').save('/tmp/t31-ref-sp.ppm')"  # ref 3932177 B 1a8b1ed9…
# adapt t31-auto.sh from the T30 copy (SP gate + PEAK_CROSS + pc arrival; bash -n), t31-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t31-auto.sh t31-analyze.sh t31-vcount.sh t31-cropdiff.py /tmp/t31-ref-sp.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t31-… /home/brad/pcsx2-t4/; sha256sum …'  # 1a8b1ed9…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H4
ssh bytesize 'wsl python3 …/t31-cropdiff.py …REFSP …; …REFZC …; …REFSC …; …REFMENU …; …REF …'  # 0.0000/0 ×5 PPM
# R1 (ONE ssh; exit 0; TITLE at poll01 → Start → menu → Cross → SC → Cross → ZC → Cross → SP → Cross → Select Mode)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t31-auto.sh' > /tmp/t31r1-run-stdout.txt  # T31_DONE, up 378→759
ssh bytesize 'wsl bash …/t31-analyze.sh'                              # 8cbf2827…, 31999707 L
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …; wc -l …; bash …/t31-vcount.sh; grep -c LoadStartModule …; grep NVRAM …'  # 397 frozen; 18
ssh bytesize 'wsl ls …/t31-*.jpg; wc -l …/t31-poll.log'                # 34 jpg + 82-line log
ssh bytesize 'wsl cp <34 jpg + poll.log + census/samples> /mnt/c/…'   # (glob, one wsl call)
scp "bytesize:pcsx2-t4/t31-…" /tmp/t31-fetch/                         # 34 jpg + logs (prefix fix local)
# R1 post-hoc (local PIL): chain scores, cross-run pairs, arrival pairs
ssh bytesize 'wsl dmesg' > /tmp/t31-dmesg-post.txt                    # 665 lines, 7 kills (5 pre + 2 post)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H4 …2843 (no restart)
ssh bytesize 'wevtutil …' > /tmp/t31-eventlog-post.txt                # head still H4-create, no in-window entries
ssh bytesize 'wsl sha256sum …/bios/….nvm; ls -la …/logs/; du -sh …/logs/; df -h /mnt/c'  # da021d2a…; 18G; C: 29G
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t31-20260921T040022Z.txt'  # 48713961… T30R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t31r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t31r1-trace-tail.txt         # 2000 lines, clean tail @370.38
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t31r1.txt'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t31r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t31r1.txt"         # 8cbf2827… match
# report (chunks; receipts include tail -3)
cp /tmp/t31-dmesg-*.txt /tmp/t31-eventlog-*.txt /tmp/t31r1-run-stdout.txt local/research/T31/  # renamed per §evidence
tail -3 local/research/T31/REPORT.md
git add -f local/research/T31/<49 files by name>                      # ignored dir, forced
git commit -m "[T31] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T31-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Select Mode park) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → ≤3 attempts) → Select Mode with Race highlighted; then a single 534 ms Cross (× Select, tagline `Choose a mode and continue to select event.`) to choose Race, screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The arrival screen is static (132 s, no reclaim) so no dwell pressure on arrival→next presses |
| G2 | WSL killer continues, full coverage this session (7 flaps, 0 restarts) | 7 userland `AcceptAsync` kills on VM-H4, all outside the R1 window (5 pre-run @83–307, 2 post-run @774–809) + 0 VM restarts this session + 1 pre-session VM restart between T30 and T31 (H3→H4; T30: 6 flaps + 1 post-run restart). The run completed exit 0 with zero in-window flaps on the dmesg record (no T27 §4 effects-verification needed); precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero flap entries; boundaries bound the restart | Newest-30 reads (pre/post): H3 teardown 23:43:33 → H4 create 23:54:04; zero entries at any flap time and zero boundaries inside the run window (precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H4 btime |
| G4 | Hold count 38/38 | 534 ms-class holds register 38/38 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31 (T31: 534.9/537.5/534.7/536.2/535.2/535.8 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/SC/ZC/SP/arrival frozenness; attract differs | Title text-band frozen across showings (0.0467/1 vs 0.0468/1) but whole-sha NOT bit-identical (pair 0.0358/0); a1-post15 bit-identity streak ends at 4 runs (pair 0.0004/0 max 7 — single-px JPEG shimmer) and a1-post3 at 2 runs (0.0574/1); menu whole-frame ≤0.057/p99 ≤1 cross-run; SC cross-run 0.026–0.11/p99 0–3 (tighter than T30-vs-T29); ZC cross-run 0.12–0.22/p99 3–6; SP cross-run 0.002–0.077/p99 0–1 (inside T30's own spread); Select Mode ≤0.066/p99 ≤1 over 132 s (near-frozen); attract phase differs this run (no phase coincidence). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the fourth-submenu run | `WaitVblankStart` stops after log ≤90 in T31 R1 including Select Mode arrival (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T30-R1-identical). The attract/title/menu/submenu sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical) | Like prior arrivals, Select Mode arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T30 R1; only counts grow (`sceSdGetParam` 1006→1266, `sceSdGetAddr` 2.94M→3.21M). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~18 GB across 18 emulogs (T17→T31 chain, all preserved); C: 29 G avail (was 31 G pre-run — run staging + parallel-brief staging). T31 full trace SSD-copied + sha-verified (2.1 GB: `emulog-t31r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T31 brief cites `t30r1-cc-post{1,3,8,15,25,40}.jpg` + `t30r1-cc-stab{1…6}.jpg` — all 12 exist with shas+sizes reproducing T30 §T30-2; the PIL `convert('RGB').save` ref recipe reproduces byte-exactly (PPM-vs-JPEG 0.0000/0). T28 G9 lesson holds |
| G10 | Session wall + run duration | ~22 min active of the 4 h box (+ report/commit); zero lease waits (no lease exists for T31). Run wall 381 s — 21 s over the ≤6 min guidance (added SP-phase scoring); full dmesg coverage, zero in-window flaps, no re-run needed |
| G11 | No operator pipe typos this session | All remote calls pipe-free first try (T30 had ×2). No run impact either way |

## Evidence files

`REPORT.md` (this file),
scripts: `t31-auto.sh`, `t31-cropdiff.py` (T30 logic, byte-identical),
`t31-analyze.sh`, `t31-vcount.sh` (byte-identical);
R1: `t31r1-start.jpg`, `t31r1-a1-now.jpg`, `t31r1-a1-poll01.jpg`,
`t31r1-a1-pre.jpg`, `t31r1-a1-post{3,8,15,25}.jpg`, `t31r1-menupre.jpg`,
`t31r1-mc-post{1,3,8,15}.jpg`, `t31r1-scpre.jpg`,
`t31r1-zc-post{1,3,8}.jpg`, `t31r1-ccpre.jpg`,
`t31r1-sp-post{1,3,8}.jpg`, `t31r1-sppre.jpg`,
`t31r1-pc-post{1,3,8,15,25,40}.jpg`, `t31r1-pc-stab{1…6}.jpg` (34 snaps),
`t31r1-census.txt`, `t31r1-samples.txt`, `t31r1-poll.log`,
`t31r1-stdout.txt`, `t31r1-trace-head.txt` / `t31r1-trace-tail.txt`;
flaps: `t31-dmesg-vmH4-pre.txt` (0 kills; pre-dates the 5 pre-run flaps) /
`t31-dmesg-vmH4-post.txt` (7 kills: 5 pre-run + 2 post-run, full
run-window coverage),
`t31-eventlog-pre.txt` / `t31-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t31r1.txt`
(2,112,217,704 B `8cbf2827…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T30 R1
`…-20260921T040022Z.txt` `48713961…`.
