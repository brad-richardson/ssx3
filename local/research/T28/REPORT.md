# T28 report — Single Event Cross from the menu park: Select Character reached (bytesize, no lease)

Brief `local/muse/prompts/T28.md`. Tables, no verdicts. One boot ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
4 h; session wall ~02:26–02:38 UTC 2026-09-21 (~12 min + report/commit).

Stale-reading guard: `local/research/T27/REPORT.md` (all: R3 reached the Main
Menu via detector-driven Start on title, ≤0.73 s after exposure, Single Event
highlighted at park, 10 snaps over 91 s pairwise ≤0.0862/p99 ≤2; G1 proposes
one 534 ms Cross on the highlighted Single Event; G2 WSL precautions:
single-shot scripts, runs ≤6 min, preserve emulogs first, re-check dmesg +
btime + init age, UNFILTERED `dmesg` + Windows event log around flaps, 534 ms
holds 20/20 do NOT bisect, `;` chains only INSIDE one `wsl` call, one `wsl`
call per ssh, no pipes inline).

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
parked Main Menu (Single Event highlighted) enters the Single Event submenu;
observable — pre-press snap = menu (whole-frame match vs T27 menu ref),
post-press snap series + per-hop whole diffs + arrival stability N; screen
content read off viewed snaps; alternatives — menu ignores Cross (post series
still menu), slow submenu load (change lands late in the +40 s tail), press
never acted on menu (pre-press ≠ menu → ONE bounded variant allowed);
stop — table the exact observed behavior + recipe, no button-mashing survey.

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); a menu reference PPM derived from T27's `t27r3-menu-stab1.jpg`
added a whole-frame MENU gate (mean < 2.0; calibration menu-menu 0.05–0.08,
title-vs-menu 14.13, attract-vs-menu 18.70). One single-shot run: park
reproduced frame-exactly at three points (poll01/pre BIT-IDENTICAL to T27 R3,
post15 BIT-IDENTICAL to T27 R3), TITLE at poll01 (0.4331/6, same as R3),
Start ≤ 0.73 s after exposure, menu-like gate → Cross on the menu @T+135.59
→ Select Character (Zoe selected) by +1 s, stable across 12 snaps / 127 s
(pairwise 0.067–0.33/p99 1–8). 2 pre-session WSL flaps + 1 VM restart this
session (E→F after all evidence home); the run completed exit 0 in a
flap-free window effects-verified per the T27 §4 rule (quoted below); trace
+ NVM re-verified post-restart, NVM `da021d2a` untouched throughout. EE/IOP
name sets identical to T27 R3 (52/155); `sceSdGetParam` 412 → 616.

## T28-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T28; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T28]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T28 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Title ref present | — | `t27-ref-title.ppm` 3932177 B sha `b964856a…e94f59` reproduces T27 | yes |
| T27 reference snaps present | — | `t27r3-menu-stab1.jpg` `42ac85486a91…`, `t27r3-a1-post25.jpg` `de8a60455071…`, `-post3` `d76dc057a28a…`, `-pre` `769c641d640f…` (sha12 all reproduce T27) | yes |
| Free space | — | WSL `/` 904 G avail; C: 39 G avail (836 G); laptop `/` 15 Gi avail; SSD 459 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1 (VM-E pre-R1); reverted by the VM-E→F restart (expected) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t28-{auto,analyze,vcount,cropdiff}.sh/.py`, `t28-ref-menu.ppm` (3,932,177 B, sha `8f34385f…ae76`), `t28-{r1-census,samples}.txt` (via analyze), `t28-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t28-*.txt` (rotation chain, see trace table), `boot-t28.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t28*` + `emulog-t28r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20, re-verified post-restart) |
| VM restarts (not by me) | 1 mid-session WSL VM restart (E→F 02:35:34 UTC, after all evidence home); cause unknown (no `wsl --shutdown` from this session; parallel briefs active — inference, T25 G2 precedent) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on both btimes:
22:24:37→`1789957477`, 22:35:34→`1789958134`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 02:24:37 ([0] VM-E) | VM-E started fresh ~2 min before first ssh | btime `…477`, eventlog-pre head (IDs 291/102/232/233/67/292) |
| 2 | 02:25:04–02:25:29 ([27.49],[52.06]) | Flaps #1–#2 on VM-E, BOTH pre-session (before first ssh); kill-to-remount unobservable directly, ≤41.6 s upper bound (#2→first-ssh @93.62; parallel use may have remounted earlier) | `t28-dmesg-vmE-pre.txt` (2 `AcceptAsync`, zero other kill lines) |
| 3 | 02:26:10–02:34 ([93.62]→~[590] VM-E) | Quiet: pre-run checks, staging, mount, R1 single-shot exit 0, `T28_DONE`, clean shutdown, analyze/vcount, cp-out, all 25 files scp'd home | exit 0, snaps, trace sha |
| 4 | 02:35:13–02:35:34 | VM-E→VM-F restart (teardown 22:35:13 IDs 71/69/233/234/234 + create 22:35:34 rendered in post log); landed between last scp home and post-run dmesg | btime `…134`, eventlog-post |
| 5 | post | Post-restart on VM-F: trace sha re-verified match (`650c0620…`), preserved T27R3 trace sha match (`31d8209c…`), NVM match (`da021d2a…`), slices + SSD copy | shas below |
| 6 | event log | Newest-30 reads (pre/post): VM-boundary VmSwitch sequences only (creates 21:34:25 / 22:24:37 / 22:35:34; teardowns 21:35:41 + 22:35:13 with IDs 71/69/233/234); ZERO entries at either flap kill (22:25:04/22:25:29 rendered window empty) — userland kills leave no Windows trace (T17/T21/T23/T25/T27 precedent stands) | `t28-eventlog-{pre,post}.txt` |

T27 §4 rule (quoted, not reinvented): "NO dmesg coverage (VM-D restarted
before capture) — flap-free effects-verified (exit 0 + monotonic uptime
529→730 + clean trace tail; a mid-run kill would have killed the ssh-held
script)". T28 R1 applies it identically (see §T28-2).

## T28-1. Menu detector + calibration (thresholds, match scores)

Tool: `t28-cropdiff.py` (copy of T27's, unmodified logic). Title text-band
method unchanged (thresholds frozen: TITLE band mean < 2.0 AND p99 ≤ 10;
STATIC whole mean < 1.0). New: menu reference `t28-ref-menu.ppm`
(3,932,177 B, sha
`8f34385f23679b9912010b94e291626b0af783a6ae391eee91f11cbbe043ae76`),
derived from T27's `t27r3-menu-stab1.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T28-5).

Brief-name gap (tabled): the brief cites `t27r3-menu01.jpg`; no such file
exists in `local/research/T27/` (T27's 10 menu snaps are
`t27r3-a1-post{3,8,15,25}.jpg` + `t27r3-menu-stab{1…6}.jpg`). `t27r3-menu-stab1.jpg`
(a mid-park stable frame) was used as the "menu01"-equivalent reference;
park scores below are reported against it AND cross-run frame pairs.

Menu calibration matrix (candidate vs `t27r3-menu-stab1.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post3 vs stab1 | 0.1647 | 6 | 39 | menu-menu (band) |
| post8 vs stab1 | 0.1951 | 7 | 39 | menu-menu (band) |
| post15/post25/stab2 vs stab1 | 0.1493 | 4 | 39 | menu-menu (band) |
| stab6 vs stab1 | 0.2382 | 10 | 39 | menu-menu (band, worst p99) |
| post3 vs stab1 | 0.0822 | 1 | 51 | menu-menu (whole) |
| post25 vs stab1 | 0.0527 | 0 | 41 | menu-menu (whole) |
| stab6 vs stab1 | 0.0552 | 1 | 39 | menu-menu (whole) |
| title (a1-pre) vs stab1 | 14.1348 | 151 | 245 | menu-title (whole) |
| attract (start) vs stab1 | 18.6958 | 164 | 248 | menu-attract (whole) |

MENU gate (frozen before R1): whole-frame vs menu ref mean < 2.0.
Menu-side margin: worst menu 0.09 → 22× (PIL); remote-lossless gap headroom
allowed (T27 title precedent ~10×: 0.43 remote vs 0.046 PIL). Non-menu-side
margin: nearest non-menu 14.13 → 7×. The Cross press does NOT depend on this
gate (T27's menu-like gate is the park criterion); MENU scores classify the
pre-press snap for the "Cross acted on the menu" bar, confirmed post-hoc.

Script deltas vs `t27-auto.sh` (committed originals untouched; `t28-auto.sh`
is the adapted copy):

| Area | T27 R3 script | T28 script |
|---|---|---|
| Park phase | identical (≤3 attempts, Cross→poll→Start, post3/8/15/25, menu-like gate) | identical, `t27-`→`t28-` names; adds post25-vs-menu score line |
| Post-park | 6×10 s menu stability | 5 s settle, `menupre` snap (vs-menu + vs-title scores), ONE `MENU_CROSS` (K) press, arrival series +1/+3/+8/+15/+25/+40 (each vs-menu + vs-title), 6 per-hop whole diffs, 6×10 s arrival stability |
| Self-tests | SELF_TEST + SELF_WHOLE | + SELF_MENU (menu ref vs itself through `score_menu`) |
| No-park path | (gate always fired in R3) | explicit `NO-PARK` plog, still clean shutdown + `T28_DONE` (trace preserved) |

## T28-2. R1 — park reproduced, Cross → Select Character

Run: `t28-auto.sh`, ONE fresh boot (skip re-confirmed: T+92 attract),
T_BOOT wall 1789957679 (uptime 202, VM-E), 02:27:53–02:32:34 UTC (uptime
196→477), WID 2097159, exit 0, `T28_DONE`, clean SIGTERM shutdown.
SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0. Attempt 1 of ≤3
consumed; attempts 2–3 not needed (Cross advanced, arrival mapped).

Window effects-verification (T27 §4 rule applied: dmesg coverage of the run
window lost to the E→F restart before post-run capture): exit 0 +
`T28_DONE` + monotonic uptime 196→477 + clean trace tail @265.14 +
trace sha re-verified post-restart (`650c0620…` match) + all 21 snaps +
poll log home with continuous wall/uptime stamps; a mid-run kill would have
killed the ssh-held script.

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+96, score 0.4331/6 remote / 0.0465/1 PIL (R3: 0.4331/6 / 0.0465/1 — identical) | Cross 535.8 ms @T+93 (attract-skip) + Start 536.0 ms @T+96 (on title, ≤0.73 s after exposure) | Main Menu by +3 s; menu-like gate (non-title + whole-static 0.0366/0.0201) + post25-vs-menu 0.3033/5 → park for menu Cross |
| A2–A3 | not run (Cross advanced) | — | — |

Cross-run frame identities (T28 R1 vs T27 R3, full sha256):

| Frame | T28 sha | T27 sha | Identity |
|---|---|---|---|
| a1-poll01 | `769c641d…dc4b66` | `769c641d…dc4b66` | BIT-IDENTICAL |
| a1-pre | `769c641d…dc4b66` | `769c641d…dc4b66` | BIT-IDENTICAL |
| a1-post15 | `4c56f815…cc44565` | `4c56f815…cc44565` | BIT-IDENTICAL |
| a1-post3/post8/post25 | differ | differ | whole pairs ≤0.074/p99 ≤1 (below T27's own 0.0862/2 max) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789957772.183005331 → 1789957772.718775153 | 535.8 ms | T+93.18→93.72 | 294→295 | `a1-now` attract (11.1785/109 remote; 11.1709/109 PIL — new run-observed mean minimum; gate still attract by p99) | `a1-poll01` TITLE (0.4331/6; 0.0465/1) |
| A1 Start (Return) | 1789957775.450778467 → 1789957775.986815665 | 536.0 ms | T+96.45→96.99 | 298 | `a1-pre` ≡ `a1-poll01` (sha `769c641d640f`, TITLE, viewed) | `a1-post3` Main Menu (16.2553/139; 16.2568/138) |
| MENU Cross (K) | 1789957814.587459757 → 1789957815.122694442 | 535.2 ms | T+135.59→136.12 | 337 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0276/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2180/106; titleband 12.5532/164 — viewed) |

Within-dwell receipts: Cross-keyup → Start-keydown 2.732 s; poll01 snap
exposure → Start-keydown ≤ 0.73 s (sleep-2 end ≥ T+95.72, keydown T+96.45;
same bound as T27 R3); R2-measured title persistence 15–17 s ⇒ press inside
the window with an order of magnitude to spare. Start-keyup → MenuCross-keydown
38.6 s (post series 25 s + settle 5 s + menupre snap/score ~8 s; no dwell
pressure — menu static, T27 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL vs p1a band / vs stab1 whole)

| Snap (T+) | Size / sha12 | Band vs p1a | Whole vs menu | Content |
|---|---|---|---|---|
| start (T+92) | 58493 B / `224514ae5d74` | 17.3421/154 | — | Attract (remote 17.3330/154) |
| a1-now (T+92, pre-Cross) | 51184 B / `437060a78b18` | 11.1709/109 | — | Attract |
| a1-poll01 = a1-pre (T+96, pre-Start) | 58339 B / `769c641d640f` | 0.0465/1 T | — | TITLE (viewed; bit-identical to T27 R3) |
| a1-post3 (T+100) | 50023 B / `429d299f85ab` | 16.2568/138 | 0.0738/1 | Main Menu |
| a1-post8 (T+105) | 50017 B / `878f14c4eef4` | 16.2990/139 | 0.0655/1 | Main Menu |
| a1-post15 (T+112) | 49634 B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | Main Menu (bit-identical to T27 R3) |
| a1-post25 (T+122) | 49804 B / `410ae0ac2c97` | 16.2622/138 | 0.0478/0 | Main Menu |
| menupre (T+134, pre-MCross) | 49618 B / `9543989c151e` | 16.2622/138 | 0.0276/0 | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+138) | 70185 B / `2cd6b6e4a50a` | 12.4773/163 | 10.1504/105 | Select Character, Zoe (viewed) |
| mc-post3 (T+140) | 70457 B / `13599fd1c61f` | 12.4791/163 | — | Select Character |
| mc-post8 (T+145) | 70505 B / `46b507ce05d3` | 12.5185/163 | — | Select Character |
| mc-post15 (T+152) | 70161 B / `d596e55a145c` | 12.4838/163 | — | Select Character |
| mc-post25 (T+162) | 70263 B / `ecc2e185aaf9` | 12.5363/163 | — | Select Character |
| mc-post40 (T+177) | 70325 B / `2b8ed633c9d6` | 12.4587/163 | 10.1411/105 | Select Character |
| mc-stab1 (T+207) | 70476 B / `a09ebafdb275` | 12.4595/163 | 10.1568/105 | Select Character |
| mc-stab2 (T+218) | 70388 B / `4ad5cd344889` | — | — | Select Character |
| mc-stab3 (T+230) | 69972 B / `74299d8a6c37` | — | — | Select Character |
| mc-stab4 (T+242) | 70654 B / `c73b837a473e` | — | — | Select Character |
| mc-stab5 (T+253) | 70377 B / `d64fca7468b4` | — | — | Select Character |
| mc-stab6 (T+265) | 70060 B / `9e5dff108826` | 12.4587/163 | 10.1280/105 | Select Character, Zoe (viewed) |

In-script (remote) vs PIL agreement on scored pairs: ≤0.08 mean on
menu/title-band scores (lossless-vs-JPEG gap, T27 precedent); pre→post1 hop
10.1227 remote vs 10.1300 PIL (0.01).

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1227 | 10.1300/105 | screen change within +1 s |
| post1 → post3 | 0.3006 | 0.3295/8 | arrival settling/shimmer |
| post3 → post8 | 0.1452 | 0.1760/4 | same screen |
| post8 → post15 | 0.0851 | 0.0962/1 | same screen |
| post15 → post25 | 0.2346 | 0.2624/5 | same screen (idle shimmer) |
| post25 → post40 | 0.0676 | 0.0943/2 | same screen |
| post40 → stab1 | — | 0.2706/6 | same screen |
| stab1 → stab6 | — | 0.2793/5 | same screen |
| post1 → stab6 (span) | — | 0.0673/1 | arrival endpoints near-identical |

### R1 arrival (Select Character)

| Item | Value |
|---|---|
| Arrival snap | `t28r1-mc-post1.jpg` @T+138 (+1 s after Menu Cross keyup; no intermediate screen captured at +1 s cadence) |
| Stability N | 12 snaps (post1/3/8/15/25/40 + stab1–6) spanning T+138→T+265 (127 s) |
| Whole-frame pairwise (PIL) | 0.067–0.33/p99 1–8 (idle shimmer; JPEG shas distinct) |
| Vs-menu (whole) | 10.13–10.22/p99 105–107 across all 12 (not menu) |
| Vs-title (band) | 12.46–12.54/p99 163–164 across all 12 (not title) |
| What is highlighted/selected | Character slot 1 of 10, "Zoe" (first silhouette orange, name plate `Zoe`, full model left, tagline `An exotic icon of adrenaline and a turbulent powerhouse.`); all stats 1.0 (Rider ranking, Acceleration, Edging, Speed, Spin, Stability, Toughness, Tricks); footer `× Select`, `△ Previous`, `○(?) Options`, `Load game` |
| Reclaim after arrival? | none observed in 127 s (all 12 snaps Select Character) |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Menu park reproduced (snap match vs T27 menu ref) | menupre/post3/8/15/25 whole-vs-stab1 0.026–0.074/p99 0–1 (all under T27's own 0.0862/2 max); 3 frames bit-identical to T27 R3 |
| Cross acted on the menu (pre-press = menu) | `menupre` vs-menu 0.2872/5 remote (gate < 2.0), 0.0276/0 PIL; viewed: Main Menu, Single Event highlighted |
| Arrival screen snaps + stability N | 12 snaps over 127 s, pairwise ≤0.33/p99 ≤8, endpoints 0.067/1 |
| Full input log + trace sha | `t28r1-poll.log` (every score + press, walls + uptimes) + trace `650c0620…23f57` |

Guest/trace side (R1): boot prefix line-identical to T25/T27 (BIOS L2,
ExecPS2 L142330/142426, ReBootStart L142725, first vblank L417043, first
UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen (all ≤90);
LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean tail @265.14.
Census: EE 4,189,791 (52, set-identical to T27 R3) · IOP 11,871,059 (155,
set-identical to T27 R3 — submenu arrival adds no new called API) ·
`libsd.006: sceSdGetParam` 616 (R3: 412); `sceSdGetAddr` 2,261,904 (R3:
1,595,760).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (A1, TITLE at poll01 → Start → menu-like gate) |
| Cross on menu? | YES (MENU Cross @T+135.59, pre-press = menu) |
| Submenu reached? | YES (Select Character @T+138, stable 127 s) |
| Bounded variant? | Not needed (first press provably acted on the menu) |
| 1200 s cap | Not reached — run ≈ T+280; attempts 2–3 unexercised |
| Chain end | Select Character, Zoe selected, awaiting input |

## T28-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t28 R1 (Cross + Start-on-title → menu → Cross → Select Character, T+~280) | 24,121,987 / 1,585,843,957 | `650c0620…23f57` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t28r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t28r1-trace-head.txt` 149019 B sha `10f80197c4b3…`, `t28r1-trace-tail.txt` 133358 B sha `23cab4d69d78…`) |
| `emulog-pre-t28-20260921T022759Z.txt` = t27 R3 (preserved at R1 boot) | 18,555,095 / 1,213,776,079 | `31d8209c…e501` (re-verified post-restart: matches T27) | bytesize-only (T27 precedent; SSD holds T27's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 4,189,791 (52
distinct, set-identical to T27 R3) · IOP 11,871,059 (155, set-identical to
T27 R3) · vblanks 397. Committed: `t28r1-census.txt`, `t28r1-samples.txt`,
`t28r1-poll.log`, `t28r1-stdout.txt` (full `set -x` shell trace).

## T28-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-E …477
ssh bytesize 'wsl dmesg' > /tmp/t28-dmesg-pre.txt                     # kills @27.49/@52.06 (pre-session)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t28-eventlog-pre.txt  # head 22:24:37
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C … rev-parse HEAD; git -C … status --short'   # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini; …t27-ref-title.ppm shas'  # da021d2a… / :579 K / b964856a…
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c; du -sh …/logs/'         # 904G / C: 39G / 11G
# calibration (local; t28-cropdiff.py = T27 copy)
python3 t28-cropdiff.py <7 menu> ../T27/t27r3-menu-stab1.jpg           # band 0.15–0.24 / p99 4–10
python3 t28-cropdiff.py <menu/title/attract> … 0,0,1280,1024            # whole menu ≤0.09, title 14.13, attract 18.70
python3 -c "Image.open(stab1).convert('RGB').save('/tmp/t28-ref-menu.ppm')"  # ref 3932177 B 8f34385f…
# staging (T25 recipe: scp to C: then wsl cp)
scp t28-auto.sh t28-analyze.sh t28-vcount.sh t28-cropdiff.py /tmp/t28-ref-menu.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t28-… /home/brad/pcsx2-t4/; sha256sum …'  # 8f34385f…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-E
ssh bytesize 'wsl python3 …/t28-cropdiff.py …REFMENU …REFMENU 0,0,1280,1024; …REF …REF'  # 0.0000/0 ×2 PPM
# R1 (ONE ssh; exit 0; TITLE at poll01 → Start → menu → Cross → Select Character)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t28-auto.sh' > /tmp/t28r1-run-stdout.txt  # T28_DONE, up 196→477
ssh bytesize 'wsl bash …/t28-analyze.sh'                              # 650c0620…, 24121987 L
ssh bytesize 'wsl bash …/t28-vcount.sh; grep … NVRAM …; grep -c LoadStartModule'  # 397 frozen; 18
ssh bytesize 'wsl cp <21 jpg + poll.log + census/samples> /mnt/c/…'
scp "bytesize:pcsx2-t4/t28-…" local/research/T28/t28r1-…              # 21 jpg + logs (prefix fix local)
# R1 post-hoc (local PIL): chain scores, 3 bit-identities vs T27 R3, arrival pairs
# post (VM-E→VM-F restart after evidence home; R1 window effects-verified)
ssh bytesize 'wsl dmesg' > /tmp/t28-dmesg-post.txt                     # VM-F fresh (0 AcceptAsync)
ssh bytesize 'wevtutil …' > /tmp/t28-eventlog-post.txt                # E→F teardown 22:35:13 + create 22:35:34
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; …'                      # 650c0620… post-restart match
ssh bytesize 'wsl ls -la …/logs/; sha256sum …/bios/….nvm'              # rotation chain; da021d2a…
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t28-20260921T022759Z.txt'  # 31d8209c… T27R3 preserved
ssh bytesize 'wsl head/tail -n 2000 <trace>' > t28r1-trace-{head,tail}.txt  # 2 slices
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t28r1.txt'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t28r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t28r1.txt"         # 650c0620… match
# report (chunks; receipts include tail -3)
cp /tmp/t28-dmesg-pre.txt local/research/T28/t28-dmesg-vmE-pre.txt; … (vmF, eventlogs, stdouts)
tail -3 local/research/T28/REPORT.md
git add -f local/research/T28/<36 files by name>                      # ignored dir, forced
git commit -m "[T28] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T28-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Select Character park) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → ≤3 attempts) → Select Character with Zoe selected; then a single 534 ms Cross (× Select) to choose Zoe, screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The arrival screen is static (127 s, no reclaim) so no dwell pressure on arrival→next presses |
| G2 | WSL killer + restarts continue (2 flaps + 1 VM restart) | 2 userland `AcceptAsync` kills pre-session on VM-E (@27.49/@52.06) + 1 full VM restart E→F 02:35:34 (after evidence home; T27: 6 flaps + 3 restarts). Every run still completed exit 0 in a flap-free window; precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero flap entries; boundaries bound the restart | Newest-30 reads (pre/post): VM-boundary VmSwitch sequences only across both flaps (precedent stands); teardown IDs (71/69/233/234) + creates bound the E→F restart (22:35:13/22:35:34 rendered). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on both btimes |
| G4 | Hold count 23/23 | 534 ms-class holds register 23/23 across T17c+T19+T21+T23+T25+T27+T28 (T28: 535.8/536.0/535.2 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/arrival frozenness; attract loops | Title text-band identical across showings (poll01/pre bit-identical across runs); menu whole-frame ≤0.074/p99 ≤1 cross-run with 1 bit-identical frame (post15); arrival Select Character ≤0.33/p99 ≤8 over 127 s (idle shimmer, no frozen frame). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the submenu run | `WaitVblankStart` stops after log ≤90 in T28 R1 including Select Character arrival (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T27-R3-identical). The attract/title/menu/submenu sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical) | Unlike menu arrival (`sceSdGetParam` ×412 R3-only vs R1/R2), Select Character arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T27 R3; only counts grow (`sceSdGetParam` 412→616, `sceSdGetAddr` 1.60M→2.26M). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~12.5 GB across 15 emulogs (T17→T28 chain, all preserved); C: 39 G avail (was 58 G at T27 — parallel-brief staging). T28 full trace SSD-copied + sha-verified (1.6 GB: `emulog-t28r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name gap: `t27r3-menu01.jpg` does not exist | T27's 10 menu snaps are `t27r3-a1-post{3,8,15,25}.jpg` + `t27r3-menu-stab{1…6}.jpg`; `t27r3-menu-stab1.jpg` used as the "menu01"-equivalent reference. Follower briefs should cite real filenames |
| G10 | Session wall | ~12 min active of the 4 h box (+ report/commit); zero lease waits (no lease exists for T28) |

## Evidence files

`REPORT.md` (this file),
scripts: `t28-auto.sh`, `t28-cropdiff.py` (T27 logic),
`t28-analyze.sh`, `t28-vcount.sh`;
R1: `t28r1-start.jpg`, `t28r1-a1-now.jpg`, `t28r1-a1-poll01.jpg`,
`t28r1-a1-pre.jpg`, `t28r1-a1-post{3,8,15,25}.jpg`, `t28r1-menupre.jpg`,
`t28r1-mc-post{1,3,8,15,25,40}.jpg`, `t28r1-mc-stab{1…6}.jpg` (21 snaps),
`t28r1-census.txt`, `t28r1-samples.txt`, `t28r1-poll.log`,
`t28r1-stdout.txt`, `t28r1-trace-head.txt` / `t28r1-trace-tail.txt`;
flaps: `t28-dmesg-vmE-pre.txt` (flaps #1–#2, pre-session) /
`t28-dmesg-vmF.txt` (fresh; R1 window effects-verified),
`t28-eventlog-pre.txt` / `t28-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t28r1.txt`
(1,585,843,957 B `650c0620…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same, re-verified post-restart) with
preserved T27 R3 `…-20260921T022759Z.txt` `31d8209c…`.
