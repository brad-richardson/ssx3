# T30 report — Cross on Continue from the Setup Character park: Select Peak reached (bytesize, no lease)

Brief: T30 (Cross on Continue from the Setup Character park). Tables, no
verdicts. One boot ran on bytesize; laptop-side work was ssh/scp + local
reads/analysis only. Time box 4 h; session wall ~03:21–03:48 UTC
2026-09-21 (~27 min + report/commit).

Stale-reading guard: `local/research/T29/REPORT.md` (all: R1 reached Setup
Character via Cross on Zoe @T+176.26, Zoe + Continue highlighted, tagline
`Continue to peak selection.`, 12 snaps over 132 s pairwise ≤0.32/p99 ≤8,
no reclaim; G1 proposes one 534 ms Cross (× Select) on Continue). This
brief executes T29's G1.

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
parked Setup Character (Zoe + Continue highlighted) chooses Continue /
enters the next screen; observable — pre-press snap = Setup Character
(whole-frame match vs T29 `zc-stab6` ref), post-press snap series +
per-hop whole diffs + arrival stability N; screen content read off viewed
snaps; alternatives — screen ignores Cross (post series still Setup
Character), slow next-screen load (change lands late in the +40 s tail),
press never acted on arrival (pre-press ≠ Setup Character → ONE bounded
variant allowed); stop — table the exact observed behavior + recipe, no
button-mashing survey.

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); a Setup Character reference PPM derived from T29's
`t29r1-zc-stab6.jpg` added a whole-frame ZC gate (mean < 2.0; calibration
ZC-ZC 0.14–0.28, menu-vs-ZC 6.91, SC-vs-ZC 7.19–7.23, title-vs-ZC 12.26).
One single-shot run: chain reproduced (TITLE at poll01 0.4329/6, Start ≤
0.73 s after exposure, menu-like gate → Menu Cross @T+137.48 → Select
Character by +1 s, SC-LIKE gate → Zoe Cross @T+177.39 → Setup Character by
+1 s, ZC-LIKE gate → 3 park snaps whole-vs-stab6 0.17–0.29/p99 4–7),
Continue Cross @T+206.24 → Select Peak (Peak 1 highlighted) by +1 s,
stable across 12 snaps / 131 s (pairwise 0.019–0.10/p99 0–1). H2→H3 VM
restart landed 3 min AFTER the run (no dmesg coverage of the run window;
T27 §4 effects-verified path: exit 0 + `T30_DONE` + monotonic uptime
136→487 + clean trace tail @341.07 + all 30 snaps); 2 pre-session VM
restarts between T29 and T30; 6 userland flaps total, all outside the run
window. NVM `da021d2a` untouched throughout. EE/IOP name sets identical to
T29 R1 (52/155); `sceSdGetParam` 800 → 1006.

## T30-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T30; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T30]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T30 observed | Match |
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
| T29 reference snaps present | — | all 12 arrival shas reproduce T29 §T29-2 (`post{1,3,8,15,25,40}` + `stab{1…6}` sha12) | yes |
| Free space | — | WSL `/` 901 G avail; C: 35 G pre → 31 G post (836 G; run staging + parallel briefs); laptop `/` 14 Gi avail; SSD 452 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×2 (once per pre-run VM: VM-H, VM-H2; second mount lost nothing — files persist on the distro disk) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t30-{auto,analyze,vcount,cropdiff}.sh/.py`, `t30-ref-zc.ppm` (3,932,177 B, sha `212b0970…f79f722`), `t30-{r1-census,samples}.txt` (via analyze), `t30-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t30-*.txt` (rotation chain, see trace table), `boot-t30.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t30*` + `emulog-t30r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 1 this session, post-run (H2→H3 at 03:37:31–03:39:43 UTC, after all H2 artifacts home); 2 pre-session restarts between T29 and T30 (G→H, H→H2; parallel briefs active — inference, T25 G2 precedent) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H2 btime:
23:26:25→`1789961185`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 03:05:30 | VM-G teardown (IDs 71/69/233/234/234, after T29's session) | eventlog-pre tail |
| 2 | 03:21:45 ([0] VM-H) | VM-H started fresh ~2 s before first ssh | btime `…0905`, eventlog-pre head (IDs 291/102/232/233/67/292) |
| 3 | 03:22:02 ([16.93]) | Flap #1 on VM-H, pre-run (first ssh exit 0) | `t30-dmesg-vmH-pre.txt` (1 `AcceptAsync`) |
| 4 | 03:26:07 | VM-H teardown (IDs 71/69/233/234/234), pre-session | eventlog-pre2 |
| 5 | 03:26:25 ([0] VM-H2) | VM-H2 started fresh (X11 mount re-done, staged files intact on distro disk) | btime `…1185`, eventlog-pre2 (IDs 291/102/232/233/67/292) |
| 6 | 03:26:54–03:27:39 ([29.47],[50.33],[73.99]) | Flaps #2–#4 on VM-H2, ALL pre-run (each ssh still exit 0) | `t30-dmesg-vmH2-pre.txt` (3 `AcceptAsync`) |
| 7 | 03:28:41–03:34:32 ([136]→[487] VM-H2) | R1 single-shot exit 0, `T30_DONE`, clean shutdown | exit 0, snaps, trace sha; NO dmesg coverage (H2 restarted before post capture — T27 §4 effects-verified path, see below) |
| 8 | 03:37:31 | VM-H2 teardown (IDs 71/69/233/234/234), ~3 min post-run, after all run artifacts + analyze/vcount/cp-out home | eventlog-post |
| 9 | 03:39:43 ([0] VM-H3) | VM-H3 started fresh (trace staging + slices read the same distro disk; shas match across the restart) | btime `…1983`, eventlog-post (IDs 291/102/232/233/67/292) |
| 10 | 03:40:08, 03:41:07 ([24.77],[83.60]) | Flaps #5–#6 on VM-H3, ALL post-run (every transfer exit 0 + sha-verified after) | `t30-dmesg-vmH3-post.txt` (2 `AcceptAsync`) |
| 11 | post | Post-run on VM-H3 (same disk): trace sha re-verified match (`48713961…`), preserved T29 trace sha match (`77df239e…`), NVM match (`da021d2a…`), slices + SSD copy | shas below |
| 12 | event log | Newest-30 reads (pre/pre2/post): boundaries chain G→H→H2→H3 with zero entries at any of the 6 flap times and zero VM-boundary events inside the run window (rendered 23:28:41–23:34:32 empty) — userland kills leave no Windows trace (T17/T21/T23/T25/T27/T28/T29 precedent stands) | `t30-eventlog-{pre,pre2,post}.txt` |
| 13 | dmesg noise | `dxg dxgkio_* Ioctl failed` lines 23 (H) / 69 (H2 pre) / 46 (H3 post), same 3 shapes (`query_adapter_info -2/-22`, `is_feature_enabled -22`) — steady boot/GPU-query noise, not kills | `t30-dmesg-vm{H,H2,H3}-*.txt` |

T27 §4 rule (quoted, not reinvented): "NO dmesg coverage (VM-D restarted
before capture) — flap-free effects-verified (exit 0 + monotonic uptime
529→730 + clean trace tail; a mid-run kill would have killed the ssh-held
script)". T30 R1 takes exactly this path: a mid-run VM restart would have
killed the ssh-held script (it completed exit 0 with `T30_DONE` and
monotonic uptime 136→487); zero VM-boundary events inside the run window;
all 30 snaps + poll log home with continuous wall/uptime stamps; clean
trace tail @341.07. Mid-run userland-flap count on H2 is unknown (dmesg
lost to the post-run restart) — and immaterial per T29 precedent (flaps
during live ssh phases, every ssh exit 0).

## T30-1. ZC detector + calibration (thresholds, match scores)

Tool: `t30-cropdiff.py` (copy of T29's, unmodified logic — byte-identical;
`t30-vcount.sh` likewise). Title text-band method unchanged (thresholds
frozen: TITLE band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU
whole-vs-menu mean < 2.0; NONMENU whole-vs-menu mean > 5.0; NONSC
whole-vs-SC mean > 5.0; DEPARTED whole hop mean > 5.0). New: Setup
Character reference `t30-ref-zc.ppm` (3,932,177 B, sha
`212b0970b8271f593070c40a73f87987c7a2bc1544218886b595755f1f79f722`),
derived from T29's `t29r1-zc-stab6.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T30-4; T28
§T28-1 recipe).

ZC calibration matrix (candidate vs `t29r1-zc-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post1 vs stab6 | 0.2805 | 7 | 164 | ZC-ZC (whole, worst mean) |
| post3 vs stab6 | 0.2338 | 6 | 202 | ZC-ZC (whole) |
| post8 vs stab6 | 0.2385 | 6 | 196 | ZC-ZC (whole) |
| post15 vs stab6 | 0.1860 | 4 | 210 | ZC-ZC (whole) |
| post25 vs stab6 | 0.2220 | 6 | 209 | ZC-ZC (whole) |
| post40 vs stab6 | 0.2447 | 6 | 202 | ZC-ZC (whole) |
| stab1 vs stab6 | 0.2116 | 5 | 199 | ZC-ZC (whole) |
| stab2 vs stab6 | 0.2157 | 5 | 196 | ZC-ZC (whole) |
| stab3 vs stab6 | 0.1403 | 2 | 203 | ZC-ZC (whole) |
| stab4 vs stab6 | 0.1857 | 5 | 196 | ZC-ZC (whole) |
| stab5 vs stab6 | 0.2529 | 7 | 200 | ZC-ZC (whole) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| mc-stab6 (T28 SC) vs stab6 | 7.2302 | 100 | 221 | SC-vs-ZC (whole) |
| scpre (T29 SC) vs stab6 | 7.1931 | 100 | 221 | SC-vs-ZC (whole) |
| menupre (T29) vs stab6 | 6.9077 | 93 | 196 | menu-vs-ZC (whole) |
| a1-post15 (T29 menu) vs stab6 | 6.9081 | 93 | 196 | menu-vs-ZC (whole) |
| a1-pre (T29 title) vs stab6 | 12.2562 | 146 | 240 | title-vs-ZC (whole) |
| start (T29 attract) vs stab6 | 12.1474 | 143 | 208 | attract-vs-ZC (whole) |
| ref PPM vs stab6 JPEG | 0.0000 | 0 | 0 | recipe exact (JPEG decode deterministic) |
| ref PPM vs ref PPM | 0.0000 | 0 | 0 | self |

ZC gate (frozen before R1): in-script park criterion = DEPARTED
(scpre→post1 hop > 5.0) AND NONSC (post8 vs-sc > 5.0) AND whole-static
(zc hops post1→post3 and post3→post8 both < 1.0); the vs-zc line
classifies the park. The Continue Cross press does NOT depend on a strict
ZC gate (T28 MENU / T29 SC precedent); the post-hoc "Cross acted on ZC"
bar is whole-vs-ZC-ref mean < 2.0 PIL + viewed snap. Margins: park
departure-side 7.22 vs 5.0 (1.4×); park nonsc-side 7.21 vs 5.0 (1.4×,
tight band 7.14–7.30 remote); post-hoc ZC-side worst 0.28→7×; post-hoc
non-ZC-side nearest 6.91→3.5×.

Script deltas vs `t29-auto.sh` (committed originals untouched; `t30-auto.sh`
is the adapted copy):

| Area | T29 R1 script | T30 script |
|---|---|---|
| Chain | park phase + MENU Cross + mc series to +15 + scpre + ZOE Cross + zc series to +40 + 6×10 s stab | identical through ZOE Cross; zc series shortened to +1/+3/+8 (each + vs-zc score; vs-menu post-hoc local), T29's +40 s tail moves to the Continue arrival |
| ZC park | (arrival was the end) | ZC-park gate (departed + non-SC + static) + `ccpre` snap (vs-zc + vs-sc + titleband) |
| T30 press | — | ONE `CONT_CROSS` (K), arrival series +1/+3/+8/+15/+25/+40 (each titleband + vs-zc + vs-menu), 6 per-hop whole diffs, 6×10 s arrival stability |
| Self-tests | SELF_TEST + SELF_WHOLE + SELF_MENU + SELF_SC | + SELF_ZC (ZC ref vs itself through `score_zc`) |
| No-park paths | explicit `NO-PARK` + `NO-SC-PARK` | + explicit `NO-ZC-PARK` plog, still clean shutdown + `T30_DONE` (trace preserved) |

## T30-2. R1 — park reproduced, Cross → Select Peak

Run: `t30-auto.sh`, ONE fresh boot (skip re-confirmed: T+90 attract),
T_BOOT wall 1789961321 (uptime 136, VM-H2), 03:28:41–03:34:32 UTC (uptime
136→487 = 351 s, ≤6 min), WID 2097159, exit 0, `T30_DONE`, clean SIGTERM
shutdown. SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU 0.0000/0,
SELF_SC 0.0000/0, SELF_ZC 0.0000/0. Attempt 1 of ≤3 consumed; attempts 2–3
not needed (Cross advanced, arrival mapped).

Window verification (T27 §4 effects-verified — no dmesg coverage, H2
restarted 03:37:31 before post capture): exit 0 + `T30_DONE` + monotonic
uptime 136→487 + zero VM-boundary events in the run window + clean trace
tail @341.07 + all 30 snaps + poll log home with continuous wall/uptime
stamps.

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+98, score 0.4329/6 remote / 0.0468/1 PIL (T29: 0.4337/6 / 0.0453/0 — band-frozen, see identities) | Cross 535.2 ms @T+95.01 (attract-skip) + Start 536.9 ms @T+98.28 (on title, ≤0.73 s after exposure) | Main Menu by +3 s; menu-like gate (non-title + whole-static 0.0366/0.0201) + post25-vs-menu 0.3033/5 → park for menu Cross |
| A2–A3 | not run (Cross advanced) | — | — |

Cross-run frame identities (T30 R1 vs T29 R1, full sha256):

| Frame | T30 sha | T29 sha | Identity |
|---|---|---|---|
| a1-post15 | `4c56f815…cc44565` | `4c56f815…cc44565` | BIT-IDENTICAL (4th run: T27 R3 ≡ T28 R1 ≡ T29 R1 ≡ T30 R1) |
| a1-post3 | `f1287a7be3a6…` | `f1287a7be3a6…` | BIT-IDENTICAL (2nd run: T29 R1 ≡ T30 R1) |
| start (T+90) | `3dc447a9b2f5…` | `3dc447a9b2f5…` (T29 `a1-now` @T+93) | BIT-IDENTICAL (attract-loop phase coincidence; both 49769 B; scores identical: 14.7665/151 remote, 14.7560/151 PIL) |
| a1-poll01 = a1-pre | `6e3d747fd514…` | `4a9c7cf6b67d…` | differ in whole sha; band-frozen (0.0468/1 vs 0.0453/0); whole pair 0.0249/0 |
| a1-post8/post25 | differ | differ | whole pairs 0.0392/0, 0.0205/0 (same magnitudes as T29-vs-T28) |
| menupre | differ | differ | whole pair 0.0028/0 (vs T28: 0.0030/0) |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.17/4, 0.16/4, 0.14/3, 0.12/2 (within T28's own arrival spread 0.067–0.33/p99 1–8) |
| scpre | differ | differ | whole pair 0.1950/5 |
| zc-post1/3/8 | differ | differ | whole pairs 0.087/1, 0.104/2, 0.150/3 (tighter than T29's own 0.14–0.28 spread) |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789961416.011251184 → 1789961416.546404050 | 535.2 ms | T+95.01→95.55 | 230→231 | `a1-now` attract (10.2854/113 remote; 10.2721/113 PIL — attract-loop phase differs from T29) | `a1-poll01` TITLE (0.4329/6; 0.0468/1) |
| A1 Start (Return) | 1789961419.282636885 → 1789961419.819579793 | 536.9 ms | T+98.28→98.82 | 234 | `a1-pre` ≡ `a1-poll01` (sha `6e3d747fd514`, TITLE, viewed) | `a1-post3` Main Menu (16.2542/139; 16.2552/138) |
| MENU Cross (K) | 1789961458.476520416 → 1789961459.012955571 | 536.4 ms | T+137.48→138.01 | 273 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2871/5 remote; 0.0275/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2146/106; vs-sc 0.4937/8; titleband 12.5510/164) |
| ZOE Cross (K) | 1789961498.394295434 → 1789961498.929274546 | 535.0 ms | T+177.39→177.93 | 313 | `scpre` Select Character, Zoe selected (vs-sc 0.5694/8 remote; 0.2215/4 PIL; vs-menu 10.1928/105; vs-title 12.6237/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.2264/100; vs-zc 0.5207/9; titleband 15.9063/129 — viewed) |
| CONT Cross (K) | 1789961527.239825908 → 1789961527.775483368 | 535.7 ms | T+206.24→206.78 | 342 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4659/8 remote; 0.2315/6 PIL; vs-sc 7.2911/101; vs-title 15.8550/128 — viewed) | `cc-post1` Select Peak (vs-zc 9.4701/154; titleband 23.1274/171; vs-menu 10.4928/171 — viewed) |

Within-dwell receipts: Cross-keyup → Start-keydown 2.736 s; poll01 snap
exposure → Start-keydown ≤ 0.73 s (sleep-2 end ≥ T+97.55, keydown T+98.28;
same bound as T28/T29); R2-measured title persistence 15–17 s ⇒ press
inside the window with an order of magnitude to spare. Start-keyup →
MenuCross-keydown 38.7 s; MenuCross-keyup → ZoeCross-keydown 39.4 s;
ZoeCross-keyup → ContCross-keydown 28.3 s (no dwell pressure — all parks
static, T27 G1 / T28 G1 / T29 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-JPEG / whole vs ZC-ref)

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Content |
|---|---|---|---|---|---|---|
| start (T+90) | 49769 B / `3dc447a9b2f5` | 14.7560/151 | — | — | — | Attract (≡ T29 a1-now, bit-identical) |
| a1-now (T+94, pre-Cross) | 50165 B / `6e61a4169804` | 10.2721/113 | — | — | — | Attract |
| a1-poll01 = a1-pre (T+98, pre-Start) | 58374 B / `6e3d747fd514` | 0.0468/1 T | — | — | — | TITLE (viewed) |
| a1-post3 (T+102) | 50085 B / `f1287a7be3a6` | 16.2552/138 | 0.0786/1 | — | — | Main Menu (bit-identical to T29 R1) |
| a1-post8 (T+107) | 50017 B / `878f14c4eef4` | 16.2990/139 | 0.0655/1 | — | — | Main Menu |
| a1-post15 (T+114) | 49634 B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | — | — | Main Menu (bit-identical 4th run) |
| a1-post25 (T+124) | 49804 B / `410ae0ac2c97` | 16.2622/138 | 0.0478/0 | — | — | Main Menu |
| menupre (T+136, pre-MCross) | 49651 B / `3ebaf24f074b` | 16.2622/138 | 0.0275/0 | — | — | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+141) | 70172 B / `5a5f0f5c18a1` | 12.4783/163 | 10.1472/105 | 0.1455/3 | — | Select Character, Zoe |
| mc-post3 (T+144) | 70409 B / `6c7ec18b2d44` | 12.4811/163 | 10.1576/107 | 0.1323/3 | — | Select Character |
| mc-post8 (T+149) | 70297 B / `4f1fe7650ae2` | 12.4611/163 | 10.1526/105 | 0.2622/4 | — | Select Character |
| mc-post15 (T+156) | 70037 B / `662f3d52a89b` | 12.4587/163 | 10.1304/105 | 0.0256/1 | — | Select Character |
| scpre (T+175, pre-ZCross) | 70072 B / `a808c6dc289c` | 12.5478/163 | 10.1256/105 | 0.2215/4 | — | Select Character, Zoe selected (viewed) |
| zc-post1 (T+181) | 51486 B / `7af6a12e4947` | 15.8827/129 | 6.9219/93 | 7.1977/99 | 0.2883/7 | Setup Character, Zoe (viewed) |
| zc-post3 (T+184) | 51542 B / `2d300e148505` | 15.8740/129 | 6.9074/92 | 7.2615/101 | 0.2330/6 | Setup Character |
| zc-post8 (T+189) | 51382 B / `f2affbbd93a0` | 15.8302/128 | 6.9326/93 | 7.1785/100 | 0.1742/4 | Setup Character |
| ccpre (T+204, pre-ContCross) | 51560 B / `0ea1369c733b` | 15.8335/128 | 6.9102/92 | 7.2628/101 | 0.2315/6 | Setup Character, Zoe + Continue (viewed) |
| cc-post1 (T+210) | 65313 B / `9f9a8e703b05` | 23.1257/171 | 10.4258/170 | 11.3476/158 | 9.3898/153 | Select Peak, Peak 1 (viewed) |
| cc-post3 (T+213) | 65385 B / `38544d0af8c9` | 23.1259/171 | 10.4368/170 | 11.3798/158 | 9.3820/153 | Select Peak |
| cc-post8 (T+218) | 65247 B / `774f16718db8` | 23.1273/171 | 10.4061/170 | 11.3503/158 | 9.3728/153 | Select Peak |
| cc-post15 (T+225) | 65372 B / `28873ee6fec0` | 23.1192/171 | 10.4248/170 | 11.3437/158 | 9.3910/153 | Select Peak |
| cc-post25 (T+236) | 65704 B / `e57f687c1971` | 23.1259/171 | 10.4797/170 | 11.4250/158 | 9.4469/153 | Select Peak |
| cc-post40 (T+251) | 65271 B / `500f5fed7b2b` | 23.1337/171 | 10.4084/170 | 11.3504/158 | 9.3731/153 | Select Peak |
| cc-stab1 (T+283) | 65441 B / `2cbf303d1cbd` | 23.1259/171 | — | 11.3602/158 | 9.3821/153 | Select Peak |
| cc-stab2 (T+295) | 65270 B / `28b5cca59a98` | 23.1270/171 | — | — | 9.3794/153 | Select Peak |
| cc-stab3 (T+306) | 65236 B / `e00e52794653` | 23.1296/171 | — | — | 9.3728/153 | Select Peak |
| cc-stab4 (T+318) | 65361 B / `308732a723d3` | 23.1259/171 | — | — | 9.3801/153 | Select Peak |
| cc-stab5 (T+330) | 65408 B / `c9e00a5e3c0a` | 23.1264/171 | — | — | 9.3834/153 | Select Peak |
| cc-stab6 (T+341) | 65293 B / `639ca1be840c` | 23.1302/171 | 10.4081/170 | 11.3503/158 | 9.3729/153 | Select Peak, Peak 1 (viewed) |

In-script (remote) vs PIL agreement: ≤0.08 mean on menu/title-band/
vs-zc scores at scale (e.g. ccpre band 15.8550 vs 15.8335; cc-post1
vs-zc 9.4701 vs 9.3898; cc-post1 vs-menu 10.4928 vs 10.4258 with p99
171/170); the known ~10× remote-lossless gap on near-zero means (poll01
band 0.4329/6 remote vs 0.0468/1 PIL; ccpre vs-zc 0.4659/8 vs 0.2315/6 —
T27 title / T28 menu / T29 SC precedent); hops ≤0.04.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1193 | 10.1268/105 | screen change within +1 s (T29: 10.1155/10.1226) |
| post1 → post3 (mc) | 0.1397 | 0.1690/4 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2779 | 0.3033/7 | same screen |
| post8 → post15 (mc) | 0.2473 | 0.2677/5 | same screen |
| post15 → scpre (park span) | — | 0.2271/4 | same screen |
| scpre → zc-post1 | 7.2200 | 7.2429/99 | screen change within +1 s (T29: 7.1365/7.1623) |
| post1 → post3 (zc) | 0.2901 | 0.3131/9 | arrival settling/shimmer |
| post3 → post8 (zc) | 0.2484 | 0.2698/7 | same screen |
| post8 → ccpre (park span) | — | 0.2707/7 | same screen |
| ccpre → cc-post1 | 9.3257 | 9.3619/153 | screen change within +1 s |
| post1 → post3 (cc) | 0.0595 | 0.0659/1 | arrival settling/shimmer |
| post3 → post8 (cc) | 0.0391 | 0.0428/0 | same screen |
| post8 → post15 (cc) | 0.0195 | 0.0223/0 | same screen |
| post15 → post25 (cc) | 0.0971 | 0.1010/0 | same screen |
| post25 → post40 (cc) | 0.0806 | 0.0840/0 | same screen (idle shimmer) |
| post40 → stab1 (cc) | — | 0.0193/0 | same screen |
| stab1 → stab6 (cc) | — | 0.0185/0 | same screen |
| post1 → stab6 (cc span) | — | 0.0267/0 | arrival endpoints near-identical |

### R1 arrival (Select Peak)

| Item | Value |
|---|---|
| Arrival snap | `t30r1-cc-post1.jpg` @T+210 (+1 s after Continue Cross keyup; no intermediate screen captured at +1 s cadence) |
| Stability N | 12 snaps (post1/3/8/15/25/40 + stab1–6) spanning T+210→T+341 (131 s) |
| Whole-frame pairwise (PIL) | 0.019–0.10/p99 0–1 (idle shimmer; JPEG shas distinct) |
| Vs-ZC (whole) | 9.37–9.45/p99 153 across all 12 (not Setup Character) |
| Vs-menu (whole) | 10.41–10.48/p99 170 across 7 scored (not menu) |
| Vs-SC (whole) | 11.34–11.43/p99 158 across 8 scored (not Select Character) |
| Vs-title (band) | 23.12–23.13/p99 171 across all 12 (not title) |
| What is highlighted/selected | "Select Peak" header; `Peak 1` (highlighted, orange bar) / `Peak 2` (locked) / `Peak 3` (locked); mountain preview panel; tagline `Choose this peak and continue to select mode.`; footer `× Select`, `△ Previous` |
| Reclaim after arrival? | none observed in 131 s (all 12 snaps Select Peak) |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Arrival park reproduced (snap match vs T29's `t29r1-zc-stab6.jpg`) | zc-post1/3/8 + ccpre whole-vs-stab6 0.17–0.29/p99 4–7 (all under the 2.0 gate AND inside T29's own 0.14–0.28 spread bar post1's 0.2883 shimmer touch); a1-post15 bit-identical 4th run, a1-post3 bit-identical 2nd run |
| Cross acted on it (pre-press = Setup Character, Continue highlighted) | `ccpre` vs-zc 0.4659/8 remote, 0.2315/6 PIL; viewed: Setup Character, Zoe + Continue highlighted (orange bar), tagline `Continue to peak selection.` |
| Next-screen snaps + stability N | 12 snaps over 131 s, pairwise ≤0.10/p99 ≤1, endpoints 0.0267/0 |
| Full input log + trace sha | `t30r1-poll.log` (69 lines: every score + press, walls + uptimes) + trace `48713961…e609e360` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29 (BIOS
L2, ExecPS2 L142330/142426, ReBootStart L142725, first vblank L417043,
first UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen (all ≤90);
LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean tail @341.07.
Census: EE 4,931,104 (52, set-identical to T29 R1) · IOP 15,030,952 (155,
set-identical to T29 R1 — Select Peak arrival adds no new called API) ·
`libsd.006: sceSdGetParam` 1006 (R1-T29: 800); `sceSdGetAddr` 2,943,888
(R1-T29: 2,681,616).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (A1, TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate) |
| Cross on Continue? | YES (CONT Cross @T+206.24, pre-press = Setup Character, Zoe + Continue highlighted) |
| Next screen reached? | YES (Select Peak @T+210, stable 131 s) |
| Bounded variant? | Not needed (first press provably acted on the Setup Character park) |
| 1200 s cap | Not reached — run ≈ T+351; attempts 2–3 unexercised |
| Chain end | Select Peak, Peak 1 highlighted, awaiting input |

## T30-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t30 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak, T+~351) | 29,820,943 / 1,966,668,019 | `48713961…e609e360` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t30r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t30r1-trace-head.txt` 149019 B sha `21759ad2c35d…`, `t30r1-trace-tail.txt` 133200 B sha `90030f0b55a1…`) |
| `emulog-pre-t30-20260921T032841Z.txt` = t29 R1 (preserved at R1 boot) | — / 1,819,248,014 | `77df239e…e2171ebd2` (re-verified post-run: matches T29) | bytesize-only (T29 precedent; SSD holds T29's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 4,931,104 (52
distinct, set-identical to T29 R1) · IOP 15,030,952 (155, set-identical to
T29 R1) · vblanks 397. Committed: `t30r1-census.txt`, `t30r1-samples.txt`,
`t30r1-poll.log` (69 lines), `t30r1-stdout.txt` (full `set -x` shell trace,
1382 lines).

## T30-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally; two pipe typos retried pipe-free this session);
`;`-chaining works INSIDE one `wsl` call only; one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H …905, then H2 …185
ssh bytesize 'wsl dmesg' > /tmp/t30-dmesg-pre.txt                     # 448 lines, 1 kill (VM-H)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t30-eventlog-pre.txt  # head 23:21:45
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini; ls -la …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm'  # da021d2a… / :579 K / sizes
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm; df -h / /tmp; df -h /mnt/c; du -sh …/logs/'  # b964856a… / 8f34385f… / dd7e4716…; 901G / C: 35G / 14G
# T29 ref snaps (local): 12/12 sha12 reproduce T29 §T29-2
# calibration (local; t30-cropdiff.py = T29 copy, byte-identical)
python3 t30-cropdiff.py <11 ZC> /tmp/t30-ref-zc.ppm 0,0,1280,1024  # whole 0.14–0.28 / p99 2–7
python3 t30-cropdiff.py <SC/menu/title/attract> … 0,0,1280,1024   # SC 7.19–7.23, menu 6.91, title 12.26, attract 12.15
python3 -c "Image.open(zc-stab6).convert('RGB').save('/tmp/t30-ref-zc.ppm')"  # ref 3932177 B 212b0970…
# adapt t30-auto.sh from the T29 copy (ZC gate + CONT_CROSS + cc arrival; bash -n), t30-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t30-auto.sh t30-analyze.sh t30-vcount.sh t30-cropdiff.py /tmp/t30-ref-zc.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t30-… /home/brad/pcsx2-t4/; sha256sum …'  # 212b0970…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H, then again on VM-H2
ssh bytesize 'wsl python3 …/t30-cropdiff.py …REFZC …REFZC 0,0,1280,1024; …REFSC …; …REFMENU …; …REF …'  # 0.0000/0 ×4 PPM
# pre-session restart H→H2 bounded via fresh eventlog read; fresh dmesg-pre on H2 (507 lines, 3 pre-run kills)
# R1 (ONE ssh; exit 0; TITLE at poll01 → Start → menu → Cross → SC → Cross → ZC → Cross → Select Peak)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t30-auto.sh' > /tmp/t30r1-run-stdout.txt  # T30_DONE, up 136→487
ssh bytesize 'wsl bash …/t30-analyze.sh'                              # 48713961…, 29820943 L
ssh bytesize 'wsl bash …/t30-vcount.sh; grep -c LoadStartModule …; grep NVRAM …'  # 397 frozen; 18
ssh bytesize 'wsl cp <30 jpg + poll.log + census/samples> /mnt/c/…'   # (explicit names, one wsl call)
scp "bytesize:pcsx2-t4/t30-…" /tmp/t30-fetch/                         # 30 jpg + logs (prefix fix local)
# R1 post-hoc (local PIL): chain scores, 3 bit-identities vs T29 R1, arrival pairs
# post-restart H2→H3 bounded via eventlog (teardown 23:37:31, create 23:39:43); dmesg on H3 (481 lines, 2 post-run kills)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H3 …983
ssh bytesize 'wsl dmesg' > /tmp/t30-dmesg-post-h3.txt
ssh bytesize 'wevtutil …' > /tmp/t30-eventlog-post.txt
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …/logs/; sha256sum …/bios/….nvm'  # 48713961…; da021d2a…
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t30-20260921T032841Z.txt; du -sh …/logs/; df -h /mnt/c'  # 77df239e… T29R1 preserved; 16G; C: 31G
ssh bytesize 'wsl head -n 2000 <trace>' > t30r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t30r1-trace-tail.txt         # 2000 lines, clean tail @341.07
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t30r1.txt'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t30r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t30r1.txt"         # 48713961… match
# report (chunks; receipts include tail -3)
cp /tmp/t30-dmesg-*.txt /tmp/t30-eventlog-*.txt /tmp/t30r1-run-stdout.txt local/research/T30/  # renamed per §evidence
tail -3 local/research/T30/REPORT.md
git add -f local/research/T30/<47 files by name>                      # ignored dir, forced
git commit -m "[T30] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T30-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Select Peak park) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → ≤3 attempts) → Select Peak with Peak 1 highlighted; then a single 534 ms Cross (× Select, tagline `Choose this peak and continue to select mode.`) to choose Peak 1, screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The arrival screen is static (131 s, no reclaim) so no dwell pressure on arrival→next presses |
| G2 | WSL killer continues, post-run restart this session (6 flaps, 1 restart) | 6 userland `AcceptAsync` kills across VM-H/H2/H3, all outside the R1 window (1 pre-session on H @16.93, 3 pre-run on H2 @29–74, 2 post-run on H3 @24–83) + 1 post-run VM restart (H2→H3, 3 min after R1) + 2 pre-session VM restarts between T29 and T30 (G→H→H2; T29: 9 flaps + 2 pre-session restarts). The run completed exit 0; T27 §4 effects-verification substitutes for lost dmesg coverage; precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero flap entries; boundaries bound all restarts | Newest-30 reads (pre/pre2/post): boundaries chain G teardown 23:05:30 → H create 23:21:45 → H teardown 23:26:07 → H2 create 23:26:25 → H2 teardown 23:37:31 → H3 create 23:39:43; zero entries at any flap time and zero boundaries inside the run window (precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H2 btime |
| G4 | Hold count 32/32 | 534 ms-class holds register 32/32 across T17c+T19+T21+T23+T25+T27+T28+T29+T30 (T30: 535.2/536.9/536.4/535.0/535.7 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/SC/ZC/arrival frozenness; attract loops | Title text-band frozen across showings (0.0468/1 vs 0.0453/0) but whole-sha NOT bit-identical (pair 0.0249/0 — sub-shimmer outside the band); menu whole-frame ≤0.041/p99 0 cross-run with a1-post15 bit-identical a 4th run (T27 R3 ≡ T28 R1 ≡ T29 R1 ≡ T30 R1) and a1-post3 bit-identical a 2nd run (T29 R1 ≡ T30 R1); SC cross-run 0.12–0.26/p99 1–7 (inside T28's own spread); ZC cross-run 0.087–0.29/p99 1–9; Select Peak ≤0.10/p99 ≤1 over 131 s (tightest arrival yet — near-frozen); attract loop phase-coincidence bit-identity again (T30 start ≡ T29 a1-now). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the third-submenu run | `WaitVblankStart` stops after log ≤90 in T30 R1 including Select Peak arrival (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T29-R1-identical). The attract/title/menu/submenu sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical) | Like prior arrivals, Select Peak arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T29 R1; only counts grow (`sceSdGetParam` 800→1006, `sceSdGetAddr` 2.68M→2.94M). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~16 GB across 17 emulogs (T17→T30 chain, all preserved); C: 31 G avail (was 35 G pre-run — run staging + parallel-brief staging). T30 full trace SSD-copied + sha-verified (2.0 GB: `emulog-t30r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T30 brief cites `t29r1-zc-post{1,3,8,15,25,40}.jpg` + `t29r1-zc-stab{1…6}.jpg` — all 12 exist with shas reproducing T29 §T29-2; the PIL `convert('RGB').save` ref recipe reproduces byte-exactly (PPM-vs-JPEG 0.0000/0). T28 G9 lesson holds |
| G10 | Session wall | ~27 min active of the 4 h box (+ report/commit); zero lease waits (no lease exists for T30) |
| G11 | Operator pipe typos ×2 | Two `ssh bytesize 'wsl … | …'` calls failed at the Windows layer (`grep`/`tail` not recognized) — the documented no-pipes-inline rule; both retried pipe-free with identical effect. No run impact (both pre/post phases, exit-255 failures, never partial) |

## Evidence files

`REPORT.md` (this file),
scripts: `t30-auto.sh`, `t30-cropdiff.py` (T29 logic, byte-identical),
`t30-analyze.sh`, `t30-vcount.sh` (byte-identical);
R1: `t30r1-start.jpg`, `t30r1-a1-now.jpg`, `t30r1-a1-poll01.jpg`,
`t30r1-a1-pre.jpg`, `t30r1-a1-post{3,8,15,25}.jpg`, `t30r1-menupre.jpg`,
`t30r1-mc-post{1,3,8,15}.jpg`, `t30r1-scpre.jpg`,
`t30r1-zc-post{1,3,8}.jpg`, `t30r1-ccpre.jpg`,
`t30r1-cc-post{1,3,8,15,25,40}.jpg`, `t30r1-cc-stab{1…6}.jpg` (30 snaps),
`t30r1-census.txt`, `t30r1-samples.txt`, `t30r1-poll.log`,
`t30r1-stdout.txt`, `t30r1-trace-head.txt` / `t30r1-trace-tail.txt`;
flaps: `t30-dmesg-vmH-pre.txt` (1 pre-session kill) /
`t30-dmesg-vmH2-pre.txt` (3 pre-run kills; run-window coverage lost to
post-run restart) / `t30-dmesg-vmH3-post.txt` (2 post-run kills),
`t30-eventlog-pre.txt` / `t30-eventlog-pre2.txt` / `t30-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t30r1.txt`
(1,966,668,019 B `48713961…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same, re-verified post-run on VM-H3) with
preserved T29 R1 `…-20260921T032841Z.txt` `77df239e…`.
