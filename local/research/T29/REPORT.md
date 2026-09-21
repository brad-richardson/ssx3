# T29 report — Cross on Zoe from the Select Character park: Setup Character reached (bytesize, no lease)

Brief: T29 (Cross on Zoe from the Select Character park). Tables, no
verdicts. One boot ran on bytesize; laptop-side work was ssh/scp + local
reads/analysis only. Time box 4 h; session wall ~02:49–03:05 UTC
2026-09-21 (~16 min + report/commit).

Stale-reading guard: `local/research/T28/REPORT.md` (all: R1 reached Select
Character via Cross on Single Event @T+135.59, Zoe selected (slot 1 of 10,
all stats 1.0), 12 snaps over 127 s pairwise ≤0.33/p99 ≤8, no reclaim; G1
proposes one 534 ms Cross (× Select) on Zoe). This brief executes T28's G1.

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
parked Select Character (Zoe selected) chooses Zoe / enters the next screen;
observable — pre-press snap = Select Character (whole-frame match vs T28
`mc-stab6` ref), post-press snap series + per-hop whole diffs + arrival
stability N; screen content read off viewed snaps; alternatives — screen
ignores Cross (post series still Select Character), slow next-screen load
(change lands late in the +40 s tail), press never acted on arrival
(pre-press ≠ Select Character → ONE bounded variant allowed); stop — table
the exact observed behavior + recipe, no button-mashing survey.

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); a Select Character reference PPM derived from T28's
`t28r1-mc-stab6.jpg` added a whole-frame SC gate (mean < 2.0; calibration
SC-SC 0.07–0.30, menu-vs-SC 10.11, title-vs-SC 11.31). One single-shot run:
chain reproduced (TITLE at poll01 0.4337/6, Start ≤ 0.73 s after exposure,
menu-like gate → Menu Cross @T+136.19 → Select Character by +1 s, 5 park
snaps whole-vs-stab6 0.06–0.25/p99 1–4), Zoe Cross @T+176.26 → Setup
Character (Zoe, Continue highlighted) by +1 s, stable across 12 snaps /
132 s (pairwise 0.077–0.32/p99 2–8). 9 WSL flaps on VM-G, ZERO inside the
run window (direct dmesg coverage: 5 pre-run, 4 post-run); 2 pre-session
VM restarts between T28 and T29; no restart this session. NVM `da021d2a`
untouched throughout. EE/IOP name sets identical to T28 R1 (52/155);
`sceSdGetParam` 616 → 800.

## T29-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T29; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T29]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T29 observed | Match |
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
| T28 reference snaps present | — | all 12 arrival shas reproduce T28 §T28-2 (`post{1,3,8,15,25,40}` + `stab{1…6}` sha12) | yes |
| Free space | — | WSL `/` 902 G avail; C: 37 G avail (836 G); laptop `/` 14 Gi avail; SSD 451 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1 (VM-G pre-R1) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t29-{auto,analyze,vcount,cropdiff}.sh/.py`, `t29-ref-sc.ppm` (3,932,177 B, sha `dd7e4716…2c06e55`), `t29-{r1-census,samples}.txt` (via analyze), `t29-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t29-*.txt` (rotation chain, see trace table), `boot-t29.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t29*` + `emulog-t29r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 0 this session; 2 pre-session restarts between T28 and T29 (F→F2, F2→G; parallel briefs active — inference, T25 G2 precedent) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-G btime:
22:49:04→`1789958944`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 02:37:33 | VM-F teardown (IDs 71/69/…, after T28's post checks) | eventlog-pre tail |
| 2 | 02:41:36→02:46:32 | VM-F2 created → torn down (IDs 71/69/233/234/234), pre-session | eventlog-pre |
| 3 | 02:49:04 ([0] VM-G) | VM-G started fresh ~1 s before first ssh | btime `…944`, eventlog-pre head (IDs 291/102/232/233/67/292) |
| 4 | 02:50:01–02:52:08 ([56.89],[93.57],[119.90],[161.68],[183.98]) | Flaps #1–#5 on VM-G, ALL pre-run (during pre-checks/staging; each ssh still exit 0) | `t29-dmesg-vmG-post.txt` (9 `AcceptAsync`, zero other kill lines) |
| 5 | 02:52:34–02:57:56 ([210]→[531] VM-G) | Quiet: R1 single-shot exit 0, `T29_DONE`, clean shutdown | exit 0, snaps, trace sha; ZERO `AcceptAsync` in [210,531] |
| 6 | 02:59:18–03:02:33 ([664.00],[694.13],[748.86],[809.17]) | Flaps #6–#9 on VM-G, ALL post-run (during analyze/cp-out/scp; every transfer exit 0 + sha-verified after) | `t29-dmesg-vmG-post.txt` |
| 7 | post | Post-run on VM-G (no restart): trace sha re-verified match (`77df239e…`), preserved T28 trace sha match (`650c0620…`), NVM match (`da021d2a…`), slices + SSD copy | shas below |
| 8 | event log | Newest-30 reads (pre/post): identical head (VM-G create 22:49:04); no new VM-boundary events; ZERO entries at any of the 9 flap times (22:50:01–23:02:33 rendered window empty) — userland kills leave no Windows trace (T17/T21/T23/T25/T27/T28 precedent stands) | `t29-eventlog-{pre,post}.txt` |
| 9 | dmesg noise | `dxg dxgkio_* Ioctl failed` lines 23 (pre) → 230 (post), same 3 shapes (`query_adapter_info -2/-22`, `is_feature_enabled -22`) — steady boot/GPU-query noise, not kills | `t29-dmesg-vmG-{pre,post}.txt` |

T27 §4 rule (quoted, not reinvented): "NO dmesg coverage (VM-D restarted
before capture) — flap-free effects-verified (exit 0 + monotonic uptime
529→730 + clean trace tail; a mid-run kill would have killed the ssh-held
script)". T29 R1 is stronger than the rule requires: DIRECT dmesg coverage
of the run window (no restart this session) shows zero kills in [210,531],
plus exit 0 + `T29_DONE` + monotonic uptime 210→531 + clean trace tail
@311.76 + all 26 snaps + poll log home with continuous wall/uptime stamps.

## T29-1. SC detector + calibration (thresholds, match scores)

Tool: `t29-cropdiff.py` (copy of T28's, unmodified logic — byte-identical;
`t29-vcount.sh` likewise). Title text-band method unchanged (thresholds
frozen: TITLE band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU
whole-vs-menu mean < 2.0). New: Select Character reference
`t29-ref-sc.ppm` (3,932,177 B, sha
`dd7e47163297f7339548215f01f9ae108d0c63897f5e10ef5aa0428602c06e55`),
derived from T28's `t28r1-mc-stab6.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T29-4; T28
§T28-1 recipe).

SC calibration matrix (candidate vs `t28r1-mc-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post1 vs stab6 | 0.0673 | 1 | 66 | SC-SC (whole) |
| post3 vs stab6 | 0.2917 | 6 | 190 | SC-SC (whole) |
| post8 vs stab6 | 0.2988 | 6 | 192 | SC-SC (whole, worst mean) |
| post15 vs stab6 | 0.2415 | 4 | 192 | SC-SC (whole) |
| post25 vs stab6 | 0.1123 | 3 | 165 | SC-SC (whole) |
| post40 vs stab6 | 0.1009 | 2 | 185 | SC-SC (whole) |
| stab1 vs stab6 | 0.2793 | 5 | 200 | SC-SC (whole) |
| stab2 vs stab6 | 0.0906 | 2 | 75 | SC-SC (whole) |
| stab3 vs stab6 | 0.2292 | 3 | 200 | SC-SC (whole) |
| stab4 vs stab6 | 0.1088 | 2 | 75 | SC-SC (whole) |
| stab5 vs stab6 | 0.2915 | 6 | 188 | SC-SC (whole) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| menupre (T28) vs stab6 | 10.1076 | 105 | 226 | menu-vs-SC (whole) |
| a1-post15 (T28 menu) vs stab6 | 10.1073 | 105 | 226 | menu-vs-SC (whole) |
| a1-pre (T28 title) vs stab6 | 11.3085 | 152 | 251 | title-vs-SC (whole) |
| ref PPM vs stab6 JPEG | 0.0000 | 0 | 0 | recipe exact (JPEG decode deterministic) |
| ref PPM vs ref PPM | 0.0000 | 0 | 0 | self |

SC gate (frozen before R1): in-script park criterion = NONMENU
(whole-vs-menu mean > 5.0) AND whole-static (mc hops post3→post8 and
post8→post15 both < 1.0); the vs-sc line classifies the park. The Zoe
Cross press does NOT depend on a strict SC gate (T28 MENU precedent); the
post-hoc "Cross acted on SC" bar is whole-vs-SC-ref mean < 2.0 PIL +
viewed snap. Margins: park menu-side 0.29→17× below 5.0; park
arrival-side 10.19→2× above (T28 remote arrival band 10.19–10.25, tight);
post-hoc SC-side worst 0.30→6.7×; post-hoc non-SC-side nearest 10.11→5×.

Script deltas vs `t28-auto.sh` (committed originals untouched; `t29-auto.sh`
is the adapted copy):

| Area | T28 R1 script | T29 script |
|---|---|---|
| Chain | park phase + MENU Cross + mc series to +40 + 6×10 s stab | identical through MENU Cross; mc series shortened to +1/+3/+8/+15 (each + vs-sc score), T28's +40 s tail moves to the Zoe arrival |
| SC park | (arrival was the end) | SC-park gate (non-menu + static) + `scpre` snap (vs-sc + vs-menu + titleband) |
| T29 press | — | ONE `ZOE_CROSS` (K), arrival series +1/+3/+8/+15/+25/+40 (each titleband + vs-sc + vs-menu), 6 per-hop whole diffs, 6×10 s arrival stability |
| Self-tests | SELF_TEST + SELF_WHOLE + SELF_MENU | + SELF_SC (SC ref vs itself through `score_sc`) |
| No-park paths | explicit `NO-PARK` | + explicit `NO-SC-PARK` plog, still clean shutdown + `T29_DONE` (trace preserved) |

## T29-2. R1 — park reproduced, Cross → Setup Character

Run: `t29-auto.sh`, ONE fresh boot (skip re-confirmed: T+90 attract),
T_BOOT wall 1789959154 (uptime 210, VM-G), 02:52:34–02:57:56 UTC (uptime
210→531 = 321 s, ≤6 min), WID 2097159, exit 0, `T29_DONE`, clean SIGTERM
shutdown. SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0,
SELF_SC 0.0000/0. Attempt 1 of ≤3 consumed; attempts 2–3 not needed
(Cross advanced, arrival mapped).

Window verification (DIRECT dmesg coverage — no restart this session):
zero `AcceptAsync` in uptime [210,531] + exit 0 + `T29_DONE` + monotonic
uptime + clean trace tail @311.76 + all 26 snaps + poll log home with
continuous wall/uptime stamps.

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+97, score 0.4337/6 remote / 0.0453/0 PIL (T28: 0.4331/6 / 0.0465/1 — band-frozen, see identities) | Cross 535.8 ms @T+93.79 (attract-skip) + Start 535.0 ms @T+97.06 (on title, ≤0.73 s after exposure) | Main Menu by +3 s; menu-like gate (non-title + whole-static 0.0389/0.0168) + post25-vs-menu 0.3002/5 → park for menu Cross |
| A2–A3 | not run (Cross advanced) | — | — |

Cross-run frame identities (T29 R1 vs T28 R1, full sha256):

| Frame | T29 sha | T28 sha | Identity |
|---|---|---|---|
| a1-post15 | `4c56f815…cc44565` | `4c56f815…cc44565` | BIT-IDENTICAL (3rd run: T27 R3 ≡ T28 R1 ≡ T29 R1) |
| start (T+90) | `437060a7…6f5a0b` | `437060a7…6f5a0b` (T28 `a1-now` @T+92) | BIT-IDENTICAL (attract-loop phase coincidence; both 51184 B; scores identical: 11.1785/109 remote, 11.1709/109 PIL) |
| a1-poll01 = a1-pre | `4a9c7cf6…fb49059` | `769c641d…dc4b66` | differ in whole sha; band-frozen (0.0453/0 vs 0.0465/1); whole pair 0.0246/0 |
| a1-post3/post8/post25 | differ | differ | whole pairs 0.0403/0, 0.0392/0, 0.0205/0 (under T27's own 0.0862/2 max) |
| menupre | differ | differ | whole pair 0.0016/0 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.0677/1, 0.3296/8, 0.1849/5, 0.2448/5 (within T28's own arrival spread 0.067–0.33/p99 1–8) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789959247.793506836 → 1789959248.329351573 | 535.8 ms | T+93.79→94.33 | 303→304 | `a1-now` attract (14.7665/151 remote; 14.7560/151 PIL — attract-loop phase differs from T28) | `a1-poll01` TITLE (0.4337/6; 0.0453/0) |
| A1 Start (Return) | 1789959251.058242674 → 1789959251.593248567 | 535.0 ms | T+97.06→97.59 | 306→307 | `a1-pre` ≡ `a1-poll01` (sha `4a9c7cf6b67d`, TITLE, viewed) | `a1-post3` Main Menu (16.2542/139; 16.2552/138) |
| MENU Cross (K) | 1789959290.190552791 → 1789959290.726736791 | 536.2 ms | T+136.19→136.73 | 346 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2871/5 remote; 0.0275/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2109/106; vs-sc 0.4251/7; titleband 12.5548/164) |
| ZOE Cross (K) | 1789959330.257827924 → 1789959330.795688070 | 537.9 ms | T+176.26→176.80 | 386 | `scpre` Select Character, Zoe selected (vs-sc 0.5146/8 remote; 0.1670/3 PIL; vs-menu 10.1701/105; vs-title 12.6647/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.2007/98; titleband 15.8430/128; vs-menu 6.9641/92 — viewed) |

Within-dwell receipts: Cross-keyup → Start-keydown 2.729 s; poll01 snap
exposure → Start-keydown ≤ 0.73 s (sleep-2 end ≥ T+96.33, keydown T+97.06;
same bound as T28); R2-measured title persistence 15–17 s ⇒ press inside
the window with an order of magnitude to spare. Start-keyup →
MenuCross-keydown 38.6 s; MenuCross-keyup → ZoeCross-keydown 39.5 s (no
dwell pressure — both parks static, T27 G1 / T28 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref)

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Content |
|---|---|---|---|---|---|
| start (T+90) | 51184 B / `437060a78b18` | 11.1709/109 | — | — | Attract (≡ T28 a1-now, bit-identical) |
| a1-now (T+93, pre-Cross) | 49769 B / `3dc447a9b2f5` | 14.7560/151 | — | — | Attract |
| a1-poll01 = a1-pre (T+97, pre-Start) | 58388 B / `4a9c7cf6b67d` | 0.0453/0 T | — | — | TITLE (viewed) |
| a1-post3 (T+101) | 50085 B / `f1287a7be3a6` | 16.2552/138 | 0.0786/1 | — | Main Menu |
| a1-post8 (T+106) | 50006 B / `88ae592f89f5` | 16.2984/139 | 0.0678/1 | — | Main Menu |
| a1-post15 (T+113) | 49634 B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | — | Main Menu (bit-identical to T27 R3 + T28 R1) |
| a1-post25 (T+123) | 49786 B / `4680fcd0480a` | 16.2622/138 | 0.0451/0 | — | Main Menu |
| menupre (T+135, pre-MCross) | 49608 B / `615b78f1c60b` | 16.2622/138 | 0.0275/0 | — | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+140) | 70235 B / `b4850bb46048` | 12.4814/163 | 10.1429/105 | 0.0583/1 | Select Character, Zoe |
| mc-post3 (T+143) | 70531 B / `ce77d18be80a` | 12.4825/163 | 10.1620/107 | 0.0934/2 | Select Character |
| mc-post8 (T+148) | 70235 B / `81b876fd8203` | 12.4587/163 | 10.1387/105 | 0.2462/4 | Select Character |
| mc-post15 (T+155) | 70236 B / `ca1a096a5dfe` | 12.4587/163 | 10.1531/105 | 0.1161/2 | Select Character |
| scpre (T+174, pre-ZCross) | 70138 B / `b7d9a2607399` | 12.5869/163 | 10.1027/105 | 0.1670/3 | Select Character, Zoe selected (viewed) |
| zc-post1 (T+180) | 51252 B / `f6e1d6201dca` | 15.8224/128 | 6.9184/92 | 7.1716/98 | Setup Character, Zoe (viewed) |
| zc-post3 (T+183) | 51378 B / `2946d2f3472a` | 15.8329/128 | 6.9100/92 | 7.2614/101 | Setup Character |
| zc-post8 (T+188) | 51417 B / `8171373986b7` | 15.8302/128 | 6.9307/93 | 7.1001/100 | Setup Character |
| zc-post15 (T+195) | 50850 B / `e2e9b02ba67d` | 15.8302/128 | 6.8963/92 | 7.2601/100 | Setup Character |
| zc-post25 (T+206) | 51648 B / `63233d2e82d5` | 15.8189/128 | 6.9089/92 | 7.2680/101 | Setup Character |
| zc-post40 (T+221) | 51372 B / `629a0b27953d` | 15.8302/128 | 6.9330/92 | 7.1205/100 | Setup Character |
| zc-stab1 (T+253) | 51360 B / `226238fb8adf` | 15.8671/129 | 6.9065/92 | 7.2346/100 | Setup Character |
| zc-stab2 (T+265) | 51800 B / `25a00806e3eb` | 15.7856/128 | — | 7.1187/100 | Setup Character |
| zc-stab3 (T+276) | 51312 B / `95ca91c51c8e` | 15.8302/128 | — | 7.2633/101 | Setup Character |
| zc-stab4 (T+288) | 51547 B / `c1a1f2d2c604` | 15.8826/129 | — | 7.1573/100 | Setup Character |
| zc-stab5 (T+300) | 51786 B / `8677c4e59a42` | 15.7536/128 | — | 7.1906/99 | Setup Character |
| zc-stab6 (T+312) | 51328 B / `37e4d1613e96` | 15.8302/128 | 6.9303/93 | 7.2302/100 | Setup Character, Zoe (viewed) |

In-script (remote) vs PIL agreement: ≤0.08 mean on menu/title-band scores
at scale (e.g. menupre band 16.2610 vs 16.2622; zc-post1 band 15.8430 vs
15.8224; zc-post1 vs-menu 6.9641 vs 6.9184); the known ~10×
remote-lossless gap on near-zero means (poll01 band 0.4337/6 remote vs
0.0453/0 PIL; scpre vs-sc 0.5146/8 vs 0.1670/3 — T27 title / T28 menu
precedent); hops ≤0.03 (pre→post1 pairs 0.007/0.026).

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1155 | 10.1226/105 | screen change within +1 s (T28: 10.1227/10.1300) |
| post1 → post3 (mc) | 0.1042 | 0.1310/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2853 | 0.3101/8 | same screen |
| post8 → post15 (mc) | 0.2197 | 0.2412/5 | same screen |
| post15 → scpre (park span) | — | 0.1784/4 | same screen |
| scpre → zc-post1 | 7.1365 | 7.1623/98 | screen change within +1 s |
| post1 → post3 (zc) | 0.2734 | 0.2966/8 | arrival settling/shimmer |
| post3 → post8 (zc) | 0.2827 | 0.3027/7 | same screen |
| post8 → post15 (zc) | 0.2574 | 0.2756/5 | same screen |
| post15 → post25 (zc) | 0.0560 | 0.0772/2 | same screen |
| post25 → post40 (zc) | 0.2961 | 0.3180/8 | same screen (idle shimmer) |
| post40 → stab1 (zc) | — | 0.2689/6 | same screen |
| stab1 → stab6 (zc) | — | 0.2116/5 | same screen |
| post1 → stab6 (zc span) | — | 0.2805/7 | arrival endpoints near-identical |

### R1 arrival (Setup Character)

| Item | Value |
|---|---|
| Arrival snap | `t29r1-zc-post1.jpg` @T+180 (+1 s after Zoe Cross keyup; no intermediate screen captured at +1 s cadence) |
| Stability N | 12 snaps (post1/3/8/15/25/40 + stab1–6) spanning T+180→T+312 (132 s) |
| Whole-frame pairwise (PIL) | 0.077–0.32/p99 2–8 (idle shimmer; JPEG shas distinct) |
| Vs-SC (whole) | 7.10–7.27/p99 99–101 across all 12 (not Select Character) |
| Vs-menu (whole) | 6.90–6.93/p99 92–93 across all 12 (not menu) |
| Vs-title (band) | 15.75–15.88/p99 128–129 across all 12 (not title) |
| What is highlighted/selected | "Setup Character" header; `Zoe` name; menu `Continue` (highlighted, orange bar) / `Equip Gear` / `Rider Details` / `Music`; tagline `Continue to peak selection.`; Zoe model left; footer `× Select`, `△ Previous`, `○ Options` |
| Reclaim after arrival? | none observed in 132 s (all 12 snaps Setup Character) |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Arrival park reproduced (snap match vs T28's `t28r1-mc-stab6.jpg`) | mc-post1/3/8/15 + scpre whole-vs-stab6 0.058–0.25/p99 1–4 (all under the 2.0 gate AND inside T28's own 0.067–0.30 spread); a1-post15 bit-identical 3rd run |
| Cross acted on it (pre-press = Select Character) | `scpre` vs-sc 0.5146/8 remote, 0.1670/3 PIL; viewed: Select Character, Zoe selected (slot 1, all stats 1.0) |
| Next-screen snaps + stability N | 12 snaps over 132 s, pairwise ≤0.32/p99 ≤8, endpoints 0.2805/7 |
| Full input log + trace sha | `t29r1-poll.log` (56 lines: every score + press, walls + uptimes) + trace `77df239e…e2171ebd2` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28 (BIOS L2,
ExecPS2 L142330/142426, ReBootStart L142725, first vblank L417043, first
UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen (all ≤90);
LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean tail @311.76.
Census: EE 4,637,856 (52, set-identical to T28 R1) · IOP 13,814,331 (155,
set-identical to T28 R1 — Setup Character arrival adds no new called API)
· `libsd.006: sceSdGetParam` 800 (R1-T28: 616); `sceSdGetAddr` 2,681,616
(R1-T28: 2,261,904).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (A1, TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate) |
| Cross on Zoe? | YES (ZOE Cross @T+176.26, pre-press = Select Character, Zoe selected) |
| Next screen reached? | YES (Setup Character @T+180, stable 132 s) |
| Bounded variant? | Not needed (first press provably acted on the Select Character park) |
| 1200 s cap | Not reached — run ≈ T+321; attempts 2–3 unexercised |
| Chain end | Setup Character, Zoe, Continue highlighted, awaiting input |

## T29-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t29 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character, T+~321) | 27,613,592 / 1,819,248,014 | `77df239e…e2171ebd2` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t29r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t29r1-trace-head.txt` 149019 B sha `e6a9f99f2793…`, `t29r1-trace-tail.txt` 134793 B sha `db0521397b62…`) |
| `emulog-pre-t29-20260921T025234Z.txt` = t28 R1 (preserved at R1 boot) | — / 1,585,843,957 | `650c0620…aa23f57` (re-verified post-run: matches T28) | bytesize-only (T28 precedent; SSD holds T28's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 4,637,856 (52
distinct, set-identical to T28 R1) · IOP 13,814,331 (155, set-identical to
T28 R1) · vblanks 397. Committed: `t29r1-census.txt`, `t29r1-samples.txt`,
`t29r1-poll.log` (56 lines), `t29r1-stdout.txt` (full `set -x` shell trace,
64394 B).

## T29-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-G …944
ssh bytesize 'wsl dmesg' > /tmp/t29-dmesg-pre.txt                     # 440 lines, 0 kills
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t29-eventlog-pre.txt  # head 22:49:04
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini; ls/sha256sum …t27-ref-title.ppm …t28-ref-menu.ppm'  # da021d2a… / :579 K / b964856a… / 8f34385f…
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c; du -sh …/logs/'         # 902G / C: 37G / 12G
# calibration (local; t29-cropdiff.py = T28 copy, byte-identical)
python3 t29-cropdiff.py <11 SC> ../T28/t28r1-mc-stab6.jpg 0,0,1280,1024  # whole 0.07–0.30 / p99 1–6
python3 t29-cropdiff.py <menu/title> … 0,0,1280,1024                   # menu 10.11, title 11.31
python3 -c "Image.open(stab6).convert('RGB').save('/tmp/t29-ref-sc.ppm')"  # ref 3932177 B dd7e4716…
# staging (T25 recipe: scp to C: then wsl cp)
scp t29-auto.sh t29-analyze.sh t29-vcount.sh t29-cropdiff.py /tmp/t29-ref-sc.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t29-… /home/brad/pcsx2-t4/; sha256sum …'  # dd7e4716…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-G
ssh bytesize 'wsl python3 …/t29-cropdiff.py …REFSC …REFSC 0,0,1280,1024; …REFMENU …REFMENU …; …REF …REF'  # 0.0000/0 ×3 PPM
# R1 (ONE ssh; exit 0; TITLE at poll01 → Start → menu → Cross → SC → Cross → Setup Character)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t29-auto.sh' > /tmp/t29r1-run-stdout.txt  # T29_DONE, up 210→531
ssh bytesize 'wsl bash …/t29-analyze.sh'                              # 77df239e…, 27613592 L
ssh bytesize 'wsl bash …/t29-vcount.sh; grep -c LoadStartModule …; grep NVRAM …'  # 397 frozen; 18
ssh bytesize 'wsl cp <26 jpg + poll.log + census/samples> /mnt/c/…'   # (one pipe typo retried pipe-free)
scp "bytesize:pcsx2-t4/t29-…" local/research/T29/t29r1-…              # 26 jpg + logs (prefix fix local)
# refs for local PIL (T25 recipe)
ssh bytesize 'wsl cp …/t27-ref-title.ppm …/t28-ref-menu.ppm /mnt/c/Users/bradr/pcsx2-t4/'
scp "bytesize:pcsx2-t4/t2*-ref-*.ppm" /tmp/                           # shas re-verified
# R1 post-hoc (local PIL): chain scores, 2 bit-identities vs T28 R1, arrival pairs
# post (NO restart this session; direct dmesg coverage of the run window)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-G …944, up 810
ssh bytesize 'wsl dmesg' > /tmp/t29-dmesg-post.txt                     # 730 lines, 9 kills all outside [210,531]
ssh bytesize 'wevtutil …' > /tmp/t29-eventlog-post.txt                # identical head; zero flap entries
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …/logs/; sha256sum …/bios/….nvm'  # 77df239e…; da021d2a…
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t29-20260921T025234Z.txt'  # 650c0620… T28R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t29r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t29r1-trace-tail.txt         # 2000 lines
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t29r1.txt'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t29r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t29r1.txt"         # 77df239e… match
# report (chunks; receipts include tail -3)
cp /tmp/t29-dmesg-pre.txt local/research/T29/t29-dmesg-vmG-pre.txt; … (vmG-post, eventlogs, stdout)
tail -3 local/research/T29/REPORT.md
git add -f local/research/T29/<41 files by name>                      # ignored dir, forced
git commit -m "[T29] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T29-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Setup Character park) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ≤3 attempts) → Setup Character with Zoe + Continue highlighted; then a single 534 ms Cross (× Select, tagline `Continue to peak selection.`) to choose Continue, screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The arrival screen is static (132 s, no reclaim) so no dwell pressure on arrival→next presses |
| G2 | WSL killer continues, no restart this session (9 flaps, 0 restarts) | 9 userland `AcceptAsync` kills on VM-G, all outside the R1 window (5 pre-run @56–184, 4 post-run @664–809; direct dmesg coverage, T27 §4 rule exceeded) + 2 pre-session VM restarts between T28 and T29 (F→F2→G; T28: 2 flaps + 1 restart). The run completed exit 0 in a flap-free window; precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero flap entries; boundaries bound the pre-session restarts | Newest-30 reads (pre/post): identical head (VM-G create 22:49:04, no new boundaries); F teardown 22:37:33 + F2 create/teardown 22:41:36/22:46:32 bound the 2 pre-session restarts; zero entries at any flap time (precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-G btime |
| G4 | Hold count 27/27 | 534 ms-class holds register 27/27 across T17c+T19+T21+T23+T25+T27+T28+T29 (T29: 535.8/535.0/536.2/537.9 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/SC/arrival frozenness; attract loops | Title text-band frozen across showings (0.0453/0 vs 0.0465/1) but whole-sha NOT bit-identical this run (pair 0.0246/0 — sub-shimmer outside the band); menu whole-frame ≤0.041/p99 0 cross-run with a1-post15 bit-identical a 3rd run (T27 R3 ≡ T28 R1 ≡ T29 R1); SC cross-run 0.068–0.33/p99 1–8 (inside T28's own spread); Setup Character ≤0.32/p99 ≤8 over 132 s (idle shimmer, no frozen frame); attract loop phase-coincidence bit-identity (T29 start ≡ T28 a1-now). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the second-submenu run | `WaitVblankStart` stops after log ≤90 in T29 R1 including Setup Character arrival (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T28-R1-identical). The attract/title/menu/submenu sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical) | Like Select Character arrival, Setup Character arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T28 R1; only counts grow (`sceSdGetParam` 616→800, `sceSdGetAddr` 2.26M→2.68M). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~14 GB across 16 emulogs (T17→T29 chain, all preserved); C: 37 G avail (was 39 G at T28 — parallel-brief staging). T29 full trace SSD-copied + sha-verified (1.8 GB: `emulog-t29r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T29 brief cites `t28r1-mc-post{1,3,8,15,25,40}.jpg` + `t28r1-mc-stab{1…6}.jpg` — all 12 exist with shas reproducing T28 §T28-2; the PIL `convert('RGB').save` ref recipe reproduces byte-exactly (PPM-vs-JPEG 0.0000/0). T28 G9 lesson holds |
| G10 | Session wall | ~16 min active of the 4 h box (+ report/commit); zero lease waits (no lease exists for T29) |

## Evidence files

`REPORT.md` (this file),
scripts: `t29-auto.sh`, `t29-cropdiff.py` (T28 logic, byte-identical),
`t29-analyze.sh`, `t29-vcount.sh` (byte-identical);
R1: `t29r1-start.jpg`, `t29r1-a1-now.jpg`, `t29r1-a1-poll01.jpg`,
`t29r1-a1-pre.jpg`, `t29r1-a1-post{3,8,15,25}.jpg`, `t29r1-menupre.jpg`,
`t29r1-mc-post{1,3,8,15}.jpg`, `t29r1-scpre.jpg`,
`t29r1-zc-post{1,3,8,15,25,40}.jpg`, `t29r1-zc-stab{1…6}.jpg` (26 snaps),
`t29r1-census.txt`, `t29r1-samples.txt`, `t29r1-poll.log`,
`t29r1-stdout.txt`, `t29r1-trace-head.txt` / `t29r1-trace-tail.txt`;
flaps: `t29-dmesg-vmG-pre.txt` (0 kills) /
`t29-dmesg-vmG-post.txt` (9 kills, all outside the run window),
`t29-eventlog-pre.txt` / `t29-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t29r1.txt`
(1,819,248,014 B `77df239e…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same, re-verified post-run) with
preserved T28 R1 `…-20260921T025234Z.txt` `650c0620…`.
