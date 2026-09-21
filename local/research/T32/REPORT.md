# T32 report — Cross on Race from the Select Mode park: next screen (bytesize, no lease)

Brief: T32 (Cross on Race from the Select Mode park). Tables, no
verdicts. One boot ran on bytesize; laptop-side work was ssh/scp + local
reads/analysis only. Time box 4 h; session wall ~04:40–05:15 UTC
2026-09-21 (~35 min + report/commit).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); a Select Mode reference PPM derived from T31's
`t31r1-pc-stab6.jpg` added a whole-frame SM gate (mean < 2.0; calibration
SM-SM 0.0356–0.0678/p99 0–1, SP-vs-SM 5.21–5.28, ZC-vs-SM 10.10–10.13,
SC-vs-SM 11.81–11.83, menu-vs-SM 10.92, title-vs-SM 16.15). One
single-shot run: chain reproduced (R1 details below), Race Cross → next
screen mapped (Select Event, Snow Jam highlighted, stable 12 snaps /
133 s, pairwise 0.007–0.063/p99 ≤1). Full dmesg coverage on VM-H6 (1
mid-session H5→H6 restart between pre-checks and R1, not by me; 6 flaps
on H6, 3 pre-run + 3 post-run, zero inside the run window); 2 pre-session
VM restarts between T31 and T32. NVM `da021d2a` untouched throughout.
EE/IOP name sets identical to T31 R1 (52/155); `sceSdGetParam`
1266 → 1426. R1 chain: TITLE at poll01 0.4329/6, Start ≤ 1.0 s after
exposure, menu-like gate → Menu Cross @T+139.04 → Select Character by
+1 s, SC-LIKE → Zoe Cross @T+179.26 → Setup Character by +1 s, ZC-LIKE →
Continue Cross @T+207.91 → Select Peak by +1 s, SP-LIKE → Peak Cross
@T+237.25 → Select Mode by +1 s, SM-LIKE → 4 park snaps vs-stab6
0.035–0.062/p99 0; Race Cross @T+266.01 → Select Event by +1 s.

Stale-reading guard: `local/research/T31/REPORT.md` (all: R1 reached Select
Mode via Cross on Peak 1 @T+235.37, Race highlighted (orange bar) /
Freestyle, tagline `Choose a mode and continue to select event.`, 12 snaps
over 132 s pairwise ≤0.066/p99 ≤1, no reclaim; G1 proposes one 534 ms
Cross (× Select) on Race). This brief executes T31's G1.

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
parked Select Mode (Race highlighted) chooses Race / enters the next
screen; observable — pre-press snap = Select Mode (whole-frame match vs
T31 `pc-stab6` ref), post-press snap series + per-hop whole diffs +
arrival stability N; screen content read off viewed snaps; alternatives —
screen ignores Cross (post series still Select Mode), slow next-screen
load (change lands late in the +40 s tail), press never acted on arrival
(pre-press ≠ Select Mode → ONE bounded variant allowed); stop — table the
exact observed behavior + recipe, no button-mashing survey.

## T32-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T32; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T32]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T32 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` (at `…/pcsx2-t4/pcsx2`; the parent dir is not a repo) | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| NVM end | — | same sha, same mtime (untouched throughout) | yes |
| Pad binding | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Title ref present | — | `t27-ref-title.ppm` 3932177 B sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` 3932177 B sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` 3932177 B sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` 3932177 B sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` 3932177 B sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| T31 reference snaps present | — | all 12 arrival shas reproduce T31 §T31-2 (`post{1,3,8,15,25,40}` + `stab{1…6}` sha12 + sizes) | yes |
| Free space | — | WSL `/` 896 G avail; C: 26 G (836 G); laptop `/` 13 Gi avail; SSD 425 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1 (VM-H5) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t32-{auto,analyze,vcount,cropdiff}.sh/.py`, `t32-ref-sm.ppm` (3,932,177 B, sha `e724021c…92845c2`), `t32-{r1-census,samples}.txt` (via analyze), `t32-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t32-*.txt` (rotation chain, see trace table), `boot-t32.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t32*` + `emulog-t32r1.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 0 this session; 2 pre-session restarts between T31 and T32 (H4→short-lived→H5; parallel briefs active — inference, T25 G2 precedent) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H5 btime:
00:39:14→`1789965553`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 04:22:48 | VM-H4 teardown (IDs 71/69…, after T31's session) | eventlog-pre tail (truncated at newest-30) |
| 2 | 04:37:19–04:38:48 | Short-lived VM create→teardown (~89 s lifetime) | eventlog-pre (IDs 292/67/291/233/232/102 create, 234/233/69/71 teardown) |
| 3 | 04:39:13 ([0] VM-H5) | VM-H5 started fresh ~68 s before first ssh | btime `…5553`, eventlog-pre head (IDs 292/67/291/233/232/102/291) |
| 4 | 04:39:33 ([19.56] H5) | Flap #1 on VM-H5, pre-run | `t32-dmesg-vmH5-pre.txt` (1 kill, 466 lines) |
| 5 | 04:42:54–04:43:18 | VM-H5 teardown → VM-H6 create (mid-session restart, NOT by me; between pre-checks and R1; every ssh exit 0 across it) | eventlog-post (IDs 71/69/233/234/234 teardown, 292/67/291/233/232/102/291 create) |
| 6 | 04:43:53–04:45:16 ([35.46],[90.45],[117.88] H6) | Flaps #1–#3 on VM-H6, ALL pre-run (each ssh still exit 0) | `t32-dmesg-vmH6-post.txt` (full boot→post coverage) |
| 7 | 04:46:31–04:53:28 ([193]→[610] H6) | R1 single-shot exit 0, `T32_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart in-window) | exit 0, 38 snaps, trace sha |
| 8 | 04:53:43, 04:55:50, 04:58:39 ([625.19],[751.60],[920.80] H6) | Flaps #4–#6 on VM-H6, ALL post-run (every transfer exit 0 + sha-verified after) | `t32-dmesg-vmH6-post.txt` (6 `AcceptAsync`) |
| 9 | event log | Newest-30 reads (pre/post): head moves H5-create 00:39:13 → H6-create 00:43:18; zero entries at any of the 7 flap times and zero VM-boundary events inside the run window — userland kills leave no Windows trace (T17/T21/T23/T25/T27/T28/T29/T30/T31 precedent stands) | `t32-eventlog-{pre,post}.txt` |
| 10 | dmesg noise | `Ioctl failed` lines 46 (H5 pre) / 161 (H6 boot→post) — steady boot/GPU-query noise, not kills | `t32-dmesg-vmH5-pre.txt` / `t32-dmesg-vmH6-post.txt` |

## T32-1. SM detector + calibration (thresholds, match scores)

Tool: `t32-cropdiff.py` (copy of T31's, unmodified logic — byte-identical;
`t32-vcount.sh` likewise). Title text-band method unchanged (thresholds
frozen: TITLE band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU
whole-vs-menu mean < 2.0; NONMENU whole-vs-menu mean > 5.0; NONSC
whole-vs-SC mean > 5.0; NONZC whole-vs-ZC mean > 5.0; NONSP whole-vs-SP
mean > 5.0; DEPARTED whole hop mean > 5.0). New: Select Mode reference
`t32-ref-sm.ppm` (3,932,177 B, sha
`e724021c…92845c2` full `e724021c33a1db6adec8f013434d3c06c816db7b45be00616c0fdaa9192845c2`),
derived from T31's `t31r1-pc-stab6.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T32-4; T28
§T28-1 recipe).

SM calibration matrix (candidate vs `t31r1-pc-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post1 vs stab6 | 0.0662 | 0 | 50 | SM-SM (whole) |
| post3 vs stab6 | 0.0400 | 0 | 50 | SM-SM (whole) |
| post8 vs stab6 | 0.0634 | 1 | 50 | SM-SM (whole) |
| post15 vs stab6 | 0.0435 | 0 | 50 | SM-SM (whole) |
| post25 vs stab6 | 0.0406 | 0 | 50 | SM-SM (whole) |
| post40 vs stab6 | 0.0445 | 0 | 50 | SM-SM (whole) |
| stab1 vs stab6 | 0.0361 | 0 | 50 | SM-SM (whole) |
| stab2 vs stab6 | 0.0667 | 0 | 50 | SM-SM (whole) |
| stab3 vs stab6 | 0.0518 | 0 | 50 | SM-SM (whole) |
| stab4 vs stab6 | 0.0356 | 0 | 50 | SM-SM (whole) |
| stab5 vs stab6 | 0.0678 | 0 | 50 | SM-SM (whole, worst mean) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| sppre (T31 SP) vs stab6 | 5.2788 | 121 | 242 | SP-vs-SM (whole) |
| sp-post1 (T31 SP) vs stab6 | 5.2370 | 121 | 242 | SP-vs-SM (whole) |
| sp-post3 (T31 SP) vs stab6 | 5.2483 | 121 | 242 | SP-vs-SM (whole) |
| sp-post8 (T31 SP) vs stab6 | 5.2081 | 121 | 242 | SP-vs-SM (whole) |
| ccpre (T31 ZC) vs stab6 | 10.0996 | 164 | 244 | ZC-vs-SM (whole) |
| zc-post8 (T31 ZC) vs stab6 | 10.1308 | 164 | 244 | ZC-vs-SM (whole) |
| scpre (T31 SC) vs stab6 | 11.8252 | 157 | 255 | SC-vs-SM (whole) |
| mc-post15 (T31 SC) vs stab6 | 11.8131 | 157 | 255 | SC-vs-SM (whole) |
| menupre (T31) vs stab6 | 10.9177 | 177 | 240 | menu-vs-SM (whole) |
| a1-post15 (T31 menu) vs stab6 | 10.9184 | 177 | 240 | menu-vs-SM (whole) |
| a1-pre (T31 title) vs stab6 | 16.1512 | 158 | 242 | title-vs-SM (whole) |
| start (T31 attract) vs stab6 | 14.2528 | 147 | 235 | attract-vs-SM (whole) |
| ref PPM vs stab6 JPEG | 0.0000 | 0 | 0 | recipe exact (JPEG decode deterministic) |
| ref PPM vs ref PPM | 0.0000 | 0 | 0 | self |

SM gate (frozen before R1): in-script park criterion = DEPARTED
(sppre→post1 hop > 5.0) AND NONSP (post8 vs-sp > 5.0) AND whole-static
(sm hops post1→post3 and post3→post8 both < 1.0); the vs-sm line
classifies the park. The Race Cross press does NOT depend on a strict SM
gate (T28 MENU / T29 SC / T30 ZC / T31 SP precedent); the post-hoc "Cross
acted on SM" bar is whole-vs-SM-ref mean < 2.0 PIL + viewed snap. Margins:
park departure-side 5.27 vs 5.0 (1.05× — tight, tabled); park nonsp-side
5.21 vs 5.0 (1.04× — tight, tabled; remote T31 values 5.2452 / 5.37 pass);
post-hoc SM-side worst 0.0678→29×; post-hoc non-SM-side nearest
5.21→2.6×.

Script deltas vs `t31-auto.sh` (committed originals untouched; `t32-auto.sh`
is the adapted copy):

| Area | T31 R1 script | T32 script |
|---|---|---|
| Chain | park phase + MENU Cross + mc series to +15 + scpre + ZOE Cross + zc series to +8 + ccpre + CONT Cross + sp series to +8 + sppre + PEAK Cross + pc series to +40 + 6×10 s stab | identical through PEAK Cross; pc series shortened to pc-post1/3/8 (each + vs-sm score; vs-zc/vs-sc/vs-menu post-hoc local), T31's +40 s tail moves to the Race arrival |
| SM park | (arrival was the end) | SM-park gate (departed + non-SP + static) + `smpre` snap (vs-sm + vs-sp + titleband) |
| T32 press | — | ONE `RACE_CROSS` (K), arrival series +1/+3/+8/+15/+25/+40 (each titleband + vs-sm + vs-sp), 6 per-hop whole diffs, 6×10 s arrival stability |
| Self-tests | SELF_TEST + SELF_WHOLE + SELF_MENU + SELF_SC + SELF_ZC + SELF_SP | + SELF_SM (SM ref vs itself through `score_sm`) |
| No-park paths | explicit `NO-PARK` + `NO-SC-PARK` + `NO-ZC-PARK` + `NO-SP-PARK` | + explicit `NO-SM-PARK` plog, still clean shutdown + `T32_DONE` (trace preserved) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
port of `t32-cropdiff.py` (`/tmp/t32-fastdiff.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical, only
the mode tag differs) against the committed tool on 4 diverse pairs
(band, whole-vs-menu, whole-vs-SM, whole hop). Any score reproduces with
the committed `t32-cropdiff.py`, slower.

## T32-2. R1 — park reproduced, Cross → Select Event

Run: `t32-auto.sh`, ONE fresh boot (skip re-confirmed: T+95 attract),
T_BOOT wall 1789965997 (uptime 199, VM-H6), 04:46:31–04:53:28 UTC (uptime
193→610 = 417 s; 57 s over the ≤6 min guidance — the added SM-phase
scoring; full dmesg coverage, zero in-window flaps), WID 2097159 (same as
T31 R1), exit 0, `T32_DONE`, clean SIGTERM shutdown. SELF_TEST 0.0000/0,
SELF_WHOLE 0.0000, SELF_MENU 0.0000/0, SELF_SC 0.0000/0, SELF_ZC 0.0000/0,
SELF_SP 0.0000/0, SELF_SM 0.0000/0. Attempt 1 of ≤3 consumed; attempts 2–3
not needed (Cross advanced, arrival mapped).

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+99, score 0.4329/6 remote / 0.0468/1 PIL (T31: 0.4331/6 / 0.0467/1; T30: 0.4329/6 / 0.0468/1 — poll01 frame bit-identical to T30's, see identities) | Cross 535.7 ms @T+96.65 (attract-skip) + Start 535.4 ms @T+99.92 (on title, ≤1.0 s after exposure) | Main Menu by +3 s; menu-like gate (non-title + whole-static 0.0389/0.0201) + post25-vs-menu 0.3033/5 → park for menu Cross |
| A2–A3 | not run (Cross advanced) | — | — |

Cross-run frame identities (T32 R1 vs T31 R1, full sha256):

| Frame | T32 sha | T31 sha | Identity |
|---|---|---|---|
| start | `de26d7d0ce08…` 67132 B | `2da39c9bbbd2…` 65750 B | differ; pair 16.12/154 (attract-loop phase differs this run) |
| a1-poll01 = a1-pre | `6e3d747fd514…` (cp-identical, pair 0.0000/0) | `d977309dd891…` | differ in whole sha; band-frozen (0.0468/1 vs 0.0467/1); whole pair 0.0358/0; BIT-IDENTICAL to T30's frame |
| a1-post3 | `f1287a7be3a6…` | `45bcb1c63256…` | differ in whole sha; pair 0.0574/1; BIT-IDENTICAL to T30's frame (pair = T30-vs-T31 value) |
| a1-post8 | `88ae592f89f5…` | `91771d70d2bb…` | differ; pair 0.0567/1 |
| a1-post15 | `4c56f8159c76…` | `f90c4e4f6859…` | differ in whole sha; pair 0.0004/0 max 7 (single-px JPEG shimmer); BIT-IDENTICAL to T30's frame |
| a1-post25 | `410ae0ac2c97…` | `36569614475c…` | differ in whole sha; pair 0.0317/0; BIT-IDENTICAL to T30's frame |
| menupre | differ | differ | whole pair 0.0025/0 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.162/4, 0.177/4, 0.119/3, 0.211/4 |
| scpre | differ | differ | whole pair 0.2590/6 |
| zc-post1/3/8 | differ | differ | whole pairs 0.506/11, 0.272/6, 0.270/5 (zc-post1 arrival settling) |
| ccpre | differ | differ | whole pair 0.2497/6 |
| sp-post1/3/8 | differ | differ | whole pairs 0.065/1, 0.076/0, 0.003/0 |
| sppre | differ | differ | whole pair 0.1384/1 |
| pc-post1/3/8 | differ | differ | whole pairs 0.059/0, 0.020/0, 0.062/1 (park reproduced tightly) |
| smpre vs T31 pc-stab6 | `a72020196915…` | `4cb2f586411b…` | whole pair 0.0349/0 (at T31's own 0.0356–0.0678 spread floor — 0.0007 below its min, same class) |
| rc-post1 vs T31 pc-stab6 | `5b0aad86bf74…` | `4cb2f586411b…` | whole pair 0.5252/10 (Select Event vs Select Mode distance) |
| rc-stab6 vs T31 pc-stab6 | `c246f4c9bf9f…` | `4cb2f586411b…` | whole pair 0.5386/11 |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789966093.646436293 → 1789966094.182129574 | 535.7 ms | T+96.65→97.18 | 295 | `a1-now` attract (21.1076/144 remote; 21.1100/144 PIL) | `a1-poll01` TITLE (0.4329/6; 0.0468/1) |
| A1 Start (Return) | 1789966096.918888748 → 1789966097.454327413 | 535.4 ms | T+99.92→100.45 | 298 | `a1-pre` ≡ `a1-poll01` (sha `6e3d747fd514`, TITLE, viewed) | `a1-post3` Main Menu (16.2542/139; 16.2552/138) |
| MENU Cross (K) | 1789966136.035693275 → 1789966136.572167137 | 536.5 ms | T+139.04→139.57 | 337 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2873/5 remote; 0.0276/0 PIL; vs-title 16.2610/139 — viewed) | `mc-post1` Select Character (vs-menu 10.2113/105; vs-sc 0.4290/7; titleband 12.5560/164) |
| ZOE Cross (K) | 1789966176.257314227 → 1789966176.792605994 | 535.3 ms | T+179.26→179.79 | 377→378 | `scpre` Select Character, Zoe selected (vs-sc 0.4310/7 remote; 0.0662/1 PIL; vs-menu 10.1673/105; vs-title 12.6694/164 — viewed) | `zc-post1` Setup Character (vs-sc 7.4446/102; vs-zc 0.7499/13; titleband 15.9146/128) |
| CONT Cross (K) | 1789966204.914628317 → 1789966205.451233093 | 536.6 ms | T+207.91→208.45 | 406 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4790/8 remote; 0.2482/6 PIL; vs-sc 7.1415/100; vs-title 15.8213/128 — viewed) | `sp-post1` Select Peak (vs-zc 9.5070/154; vs-sp 0.4120/6; titleband 23.1261/171) |
| PEAK Cross (K) | 1789966234.249869577 → 1789966234.800345151 | 550.5 ms | T+237.25→237.80 | 435→436 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.4103/6 remote; 0.0678/0 PIL; vs-zc 9.5055/154; vs-title 23.1259/171 — viewed) | `pc-post1` Select Mode (vs-sp 5.3708/121; vs-sm 0.4107/6; titleband 26.3170/183 — viewed) |
| RACE Cross (K) | 1789966263.013234603 → 1789966263.550661297 | 537.4 ms | T+266.01→266.55 | 464 | `smpre` Select Mode, Race highlighted (vs-sm 0.3872/6 remote; 0.0349/0 PIL; vs-sp 5.3473/121; vs-title 26.3181/183 — viewed) | `rc-post1` Select Event (vs-sm 0.8192/12; vs-sp 5.4641/122; titleband 26.2101/183 — viewed) |

Within-dwell receipts: Cross-keyup → Start-keydown 2.737 s; poll01 snap
exposure (04:48:16 UTC, 1 s resolution) → Start-keydown 04:48:16.919 ≤
1.0 s; R2-measured title persistence 15–17 s ⇒ press inside the window
with an order of magnitude to spare. Start-keyup → MenuCross-keydown
38.6 s; MenuCross-keyup → ZoeCross-keydown 39.7 s; ZoeCross-keyup →
ContCross-keydown 28.1 s; ContCross-keyup → PeakCross-keydown 28.8 s;
PeakCross-keyup → RaceCross-keydown 28.2 s (no dwell pressure — all parks
static, T27 G1 / T28 G1 / T29 G1 / T30 G1 / T31 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-JPEG / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Content |
|---|---|---|---|---|---|---|---|---|
| start (T+95) | 67132 B / `de26d7d0ce08` | 27.4158/179 | — | — | — | — | — | Attract (phase differs from T31) |
| a1-now (T+95, pre-Cross) | 52779 B / `713437fb5465` | 21.1100/144 | — | — | — | — | — | Attract |
| a1-poll01 = a1-pre (T+99, pre-Start) | 58374 B / `6e3d747fd514` | 0.0468/1 T | — | — | — | — | — | TITLE (viewed) |
| a1-post3 (T+103) | 50085 B / `f1287a7be3a6` | 16.2552/138 | 0.0786/1 | — | — | — | — | Main Menu |
| a1-post8 (T+109) | 50006 B / `88ae592f89f5` | 16.2984/139 | 0.0678/1 | — | — | — | — | Main Menu |
| a1-post15 (T+116) | 49634 B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | — | — | — | — | Main Menu |
| a1-post25 (T+127) | 49804 B / `410ae0ac2c97` | 16.2622/138 | 0.0478/0 | — | — | — | — | Main Menu |
| menupre (T+137, pre-MCross) | 49643 B / `7c080880e379` | 16.2622/138 | 0.0276/0 | — | — | — | — | Main Menu, Single Event highlighted (viewed) |
| mc-post1 (T+140) | 70223 B / `f242a3c3d915` | 12.4827/163 | 10.1433/105 | 0.0681/1 | — | — | — | Select Character, Zoe |
| mc-post3 (T+145) | 70604 B / `505355de73d9` | 12.4843/163 | 10.1630/107 | 0.0868/1 | — | — | — | Select Character |
| mc-post8 (T+152) | 70240 B / `3ba59b03c7d4` | 12.4587/163 | 10.1383/105 | 0.2509/5 | — | — | — | Select Character |
| mc-post15 (T+162) | 70278 B / `b2e69bf57e6c` | 12.4587/163 | 10.1409/105 | 0.2096/4 | — | — | — | Select Character |
| scpre (T+176, pre-ZCross) | 70348 B / `67d78ebf77f9` | 12.5913/163 | 10.1002/105 | 0.0662/1 | — | — | — | Select Character, Zoe selected (viewed) |
| zc-post1 (T+180) | 51752 B / `17ec91014df1` | 15.8896/129 | 6.9083/92 | 7.4171/102 | 0.5201/13 | — | — | Setup Character, Zoe |
| zc-post3 (T+185) | 51724 B / `c501368e93d8` | 15.7980/128 | 6.9151/93 | 7.1411/100 | 0.2069/5 | — | — | Setup Character |
| zc-post8 (T+193) | 51024 B / `5e1c5ac86c91` | 15.8302/128 | 6.9196/92 | 7.2780/100 | 0.2201/5 | — | — | Setup Character |
| ccpre (T+205, pre-ContCross) | 51455 B / `c5f736cd3cd1` | 15.8007/128 | 6.8975/93 | 7.1116/100 | 0.2482/6 | — | — | Setup Character, Zoe + Continue (viewed) |
| sp-post1 (T+209) | 65557 B / `917b23c338da` | 23.1242/171 | 10.4652/170 | 11.3808/158 | 9.4286/153 | 0.0697/0 | — | Select Peak, Peak 1 |
| sp-post3 (T+214) | 65582 B / `fb4fddabb1ac` | 23.1259/171 | 10.4544/170 | 11.3946/158 | 9.4120/153 | 0.0610/0 | — | Select Peak |
| sp-post8 (T+221) | 65237 B / `f8564412fab2` | 23.1263/171 | 10.4070/170 | 11.3502/158 | 9.3728/153 | 0.0052/0 | — | Select Peak |
| sppre (T+234, pre-PeakCross) | 65561 B / `28376ff283ba` | 23.1241/171 | 10.4633/170 | 11.3820/158 | 9.4264/153 | 0.0678/0 | — | Select Peak, Peak 1 highlighted (viewed) |
| pc-post1 (T+238) | 67528 B / `74451c726ce1` | 26.3046/183 | 10.9335/178 | 11.8227/157 | 10.1214/164 | 5.2025/121 | 0.0620/0 | Select Mode, Race (viewed) |
| pc-post3 (T+243) | 67576 B / `4648ab7d0ad9` | 26.3046/183 | 10.9203/178 | 11.8097/157 | 10.1071/164 | 5.1894/121 | 0.0443/0 | Select Mode |
| pc-post8 (T+251) | 67546 B / `6322d6d5b967` | 26.3045/183 | 10.9281/178 | 11.8125/157 | 10.1144/164 | 5.1962/121 | 0.0506/0 | Select Mode |
| smpre (T+263, pre-RaceCross) | 67331 B / `a72020196915` | 26.3055/183 | 10.9101/178 | 11.8000/157 | 10.0975/164 | 5.1767/121 | 0.0349/0 | Select Mode, Race highlighted (viewed) |
| rc-post1 (T+267) | 69598 B / `5b0aad86bf74` | 26.1963/183 | 10.9564/178 | 11.8710/157 | 10.2328/164 | 5.3019/122 | 0.5252/10 | Select Event, Snow Jam (viewed) |
| rc-post3 (T+272) | 69542 B / `4e3f62a5c418` | 26.1966/183 | 10.9554/178 | 11.8517/157 | 10.2283/164 | 5.3003/121 | 0.5279/10 | Select Event |
| rc-post8 (T+279) | 69497 B / `8e2693d65006` | 26.1964/183 | 10.9495/178 | 11.8673/157 | 10.2021/164 | 5.2981/121 | 0.5261/10 | Select Event |
| rc-post15 (T+289) | 69496 B / `37cd07345f17` | 26.1964/183 | 10.9433/178 | 11.8634/157 | 10.2203/164 | 5.2879/121 | 0.5155/10 | Select Event |
| rc-post25 (T+302) | 69670 B / `76039265e1f1` | 26.2086/183 | 10.9655/178 | 11.8610/157 | 10.2401/164 | 5.3125/121 | 0.5382/12 | Select Event |
| rc-post40 (T+319) | 69441 B / `ae887feb451b` | 26.1964/183 | 10.9413/178 | 11.8595/157 | 10.2175/164 | 5.2870/121 | 0.5146/10 | Select Event |
| rc-stab1 (T+341) | 69551 B / `b0e51710ff28` | 26.1973/183 | — | — | — | 5.2936/121 | 0.5231/10 | Select Event |
| rc-stab2 (T+353) | 69464 B / `5491ec4e94d8` | 26.2006/183 | — | — | — | 5.2821/121 | 0.5133/9 | Select Event |
| rc-stab3 (T+365) | 69508 B / `a1fb6506035c` | 26.1964/183 | — | — | — | 5.2963/121 | 0.5236/10 | Select Event |
| rc-stab4 (T+376) | 69616 B / `dcdc53d48b4e` | 26.1969/183 | — | — | — | 5.2948/121 | 0.5251/10 | Select Event |
| rc-stab5 (T+388) | 69439 B / `4d12840b6c41` | 26.1988/183 | — | — | — | 5.2848/121 | 0.5124/9 | Select Event |
| rc-stab6 (T+400) | 69657 B / `c246f4c9bf9f` | 26.1964/183 | 10.9636/178 | 11.8811/157 | 10.2392/164 | 5.3124/121 | 0.5386/11 | Select Event, Snow Jam (viewed) |

In-script (remote) vs PIL agreement: ≤0.17 mean on menu/title-band/
vs-sp/vs-sm scores at scale (e.g. smpre band 26.3181 vs 26.3055; pc-post1
vs-sp 5.3708 vs 5.2025; rc-post1 vs-sm 0.8192 vs 0.5252 with p99 12/10);
the known ~6–11× remote-lossless gap on near-zero means (poll01 band
0.4329/6 remote vs 0.0468/1 PIL; smpre vs-sm 0.3872/6 vs 0.0349/0 —
T27 title / T28 menu / T29 SC / T30 ZC / T31 SP precedent); hops ≤0.03.

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1161 | 10.1230/105 | screen change within +1 s (T31: 10.1223/10.1299) |
| post1 → post3 (mc) | 0.1060 | 0.1339/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2896 | 0.3157/8 | same screen |
| post8 → post15 (mc) | 0.1343 | 0.1592/4 | same screen |
| post15 → scpre (park span) | — | 0.2489/6 | same screen |
| scpre → zc-post1 | 7.3804 | 7.4037/102 | screen change within +1 s (T31: 7.2212/7.2443) |
| post1 → post3 (zc) | 0.4946 | 0.5181/14 | arrival settling (largest in-run hanging shimmer) |
| post3 → post8 (zc) | 0.2589 | 0.2800/7 | same screen |
| post8 → ccpre (park span) | — | 0.2909/6 | same screen |
| ccpre → sp-post1 | 9.3651 | 9.4022/153 | screen change within +1 s (T31: 9.3463/9.3826) |
| post1 → post3 (sp) | 0.1155 | 0.1242/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0540 | 0.0589/0 | same screen |
| post8 → sppre (park span) | — | 0.0670/0 | same screen |
| sppre → pc-post1 | 5.2361 | 5.2617/121 | screen change within +1 s (T31: 5.2452/5.2686) |
| post1 → post3 (pc) | 0.0383 | 0.0417/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0308 | 0.0352/0 | same screen |
| post8 → smpre (park span) | — | 0.0222/0 | same screen |
| smpre → rc-post1 | 0.4695 | 0.4976/8 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps) |
| post1 → post3 (rc) | 0.0351 | 0.0394/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0316 | 0.0356/0 | same screen |
| post8 → post15 (rc) | 0.0199 | 0.0233/0 | same screen |
| post15 → post25 (rc) | 0.0343 | 0.0391/0 | same screen |
| post25 → post40 (rc) | 0.0323 | 0.0381/0 | same screen (idle shimmer) |
| post40 → stab1 (rc) | — | 0.0194/0 | same screen |
| stab1 → stab6 (rc) | — | 0.0453/0 | same screen |
| post1 → stab6 (rc span) | — | 0.0523/0 | arrival endpoints near-identical |

### R1 arrival (Select Event)

| Item | Value |
|---|---|
| Arrival snap | `t32r1-rc-post1.jpg` @T+267 (+1 s after Race Cross keyup; no intermediate screen captured at +1 s cadence) |
| Stability N | 12 snaps (post1/3/8/15/25/40 + stab1–6) spanning T+267→T+400 (133 s) |
| Whole-frame pairwise (PIL) | 0.0069–0.0633/p99 ≤1 across all 66 pairs (idle shimmer; JPEG shas distinct) |
| Vs-SM (whole) | 0.51–0.54/p99 9–12 across all 12 (within the 2.0 SM bar — shared background; the screens differ in header/mode-list/tagline/panel-title, read off viewed snaps) |
| Vs-SP (whole) | 5.28–5.31/p99 121–122 across all 12 (not Select Peak) |
| Vs-ZC (whole) | 10.20–10.24/p99 164 across 7 scored (not Setup Character) |
| Vs-menu (whole) | 10.94–10.97/p99 178 across 7 scored (not menu) |
| Vs-SC (whole) | 11.85–11.88/p99 157 across 7 scored (not Select Character) |
| Vs-title (band) | 26.20–26.21/p99 183 across all 12 (not title) |
| What is highlighted/selected | "Select Event" header; `Snow Jam` (highlighted, orange bar) / `Metro-City` / `Happiness`; course-map panel titled `Race` (was `Peak 1`); tagline `Snow Jam is an exciting BEGINNER track with heavy forests and patches of fog.`; footer `× Select`, `△ Previous` |
| Reclaim after arrival? | none observed in 133 s (all 12 snaps Select Event) |

### R1 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Arrival park reproduced (snap match vs T31's `t31r1-pc-stab6.jpg`) | pc-post1/3/8 + smpre whole-vs-stab6 0.035–0.062/p99 0 (all under the 2.0 gate; pc-post1/3/8 inside T31's own 0.0356–0.0678 spread, smpre 0.0349 a hair below its min — same class); 5 chain frames bit-identical to T30's run |
| Cross acted on it (pre-press = Select Mode, Race highlighted) | `smpre` vs-sm 0.3872/6 remote, 0.0349/0 PIL; viewed: Select Mode, Race highlighted (orange bar), Freestyle below, Peak 1 course-map panel, tagline `Choose a mode and continue to select event.` |
| Next-screen snaps + stability N | 12 snaps over 133 s, pairwise ≤0.064/p99 ≤1, endpoints 0.0523/0 |
| Full input log + trace sha | `t32r1-poll.log` (95 lines: every score + press, walls + uptimes) + trace `7f14d876…af9cc3c` |

Guest/trace side (R1): boot prefix line-identical to T25/T27/T28/T29/T30/
T31 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725, first vblank
L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen
(all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean
tail @400.9075. Census: EE 5,473,454 (52, set-identical to T31 R1) · IOP
17,462,778 (155, set-identical to T31 R1 — Select Event arrival adds no
new called API) · `libsd.006: sceSdGetParam` 1426 (R1-T31: 1266);
`sceSdGetAddr` 3,468,480 (R1-T31: 3,207,744).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (A1, TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate) |
| Cross on Race? | YES (RACE Cross @T+266.01, pre-press = Select Mode, Race highlighted) |
| Next screen reached? | YES (Select Event @T+267, stable 133 s) |
| Bounded variant? | Not needed (first press provably acted on the Select Mode park) |
| 1200 s cap | Not reached — run ≈ T+411; attempts 2–3 unexercised |
| Chain end | Select Event, Snow Jam highlighted, awaiting input |

## T32-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t32 R1 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event, T+~411) | 34,195,845 / 2,259,205,200 | `7f14d876…af9cc3c` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t32r1.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t32r1-trace-head.txt` 149019 B sha `43647bed3b93…`, `t32r1-trace-tail.txt` 130691 B sha `69a02e7371ae…`) |
| `emulog-pre-t32-20260921T044637Z.txt` = t31 R1 (preserved at R1 boot) | — / 2,112,217,704 | `8cbf2827…896d081e` (re-verified post-run: matches T31) | bytesize-only (T31 precedent; SSD holds T31's own copy) |

Channel census (T4 `t4-census.py`, same script): R1 EE 5,473,454 (52
distinct, set-identical to T31 R1) · IOP 17,462,778 (155, set-identical
to T31 R1) · vblanks 397. Committed: `t32r1-census.txt`, `t32r1-samples.txt`,
`t32r1-poll.log` (95 lines), `t32r1-stdout.txt` (276 lines),
`t32r1-stderr.txt` (full `set -x` shell trace, 1556 lines — captured
separately this run, see §T32-4).

## T32-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H5 …5553
ssh bytesize 'wsl dmesg' > /tmp/t32-dmesg-pre.txt                     # 466 lines, 1 kill (H5)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t32-eventlog-pre.txt  # head 00:39:13
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini; ls -la …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm'  # da021d2a… / :579 K / sizes
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm; ls -la …t30-ref-zc.ppm …t31-ref-sp.ppm; sha256sum …t30-ref-zc.ppm …t31-ref-sp.ppm'  # b964856a… / 8f34385f… / dd7e4716… / 212b0970… / 1a8b1ed9…
ssh bytesize 'wsl df -h / /tmp; df -h /mnt/c; du -sh …/logs/'          # 896G / C: 26G / 18G
# T31 ref snaps (local): 12/12 sha12+sizes reproduce T31 §T31-2
# calibration (local; t32-cropdiff.py = T31 copy, byte-identical)
python3 t32-cropdiff.py <12 SM> /tmp/t32-ref-sm.ppm 0,0,1280,1024  # SM-SM 0.0356–0.0678 / p99 0–1
python3 t32-cropdiff.py <SP/ZC/SC/menu/title/attract> … 0,0,1280,1024   # SP 5.21–5.28, ZC 10.10–10.13, SC 11.81–11.83, menu 10.92, title 16.15, attract 14.25
python3 -c "Image.open(pc-stab6).convert('RGB').save('/tmp/t32-ref-sm.ppm')"  # ref 3932177 B e724021c…
# adapt t32-auto.sh from the T31 copy (SM gate + RACE_CROSS + rc arrival; bash -n), t32-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t32-auto.sh t32-analyze.sh t32-vcount.sh t32-cropdiff.py /tmp/t32-ref-sm.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t32-… /home/brad/pcsx2-t4/; sha256sum …'  # e724021c…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H5 (wiped by H5→H6 restart; R1 unaffected)
ssh bytesize 'wsl python3 …/t32-cropdiff.py …REFSM …; …REFSP …; …REFZC …; …REFSC …; …REFMENU …; …REF …'  # 0.0000/0 ×6 PPM
# R1 (ONE ssh; exit 0; TITLE at poll01 → Start → menu → Cross → SC → Cross → ZC → Cross → SP → Cross → SM → Cross → Select Event)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t32-auto.sh' > /tmp/t32r1-run-stdout.txt 2>/tmp/t32r1-run-stderr.txt  # T32_DONE, up 193→610
ssh bytesize 'wsl bash …/t32-analyze.sh'                              # 7f14d876…, 34195845 L
ssh bytesize 'wsl bash …/t32-vcount.sh'                                # 397 frozen (all ≤90)
ssh bytesize 'wsl grep -c LoadStartModule …'                          # 18
ssh bytesize 'wsl grep NVRAM …'                                       # has not changed
ssh bytesize 'wsl ls …/t32-*.jpg; wc -l …/t32-poll.log'                # 38 jpg + 95-line log
ssh bytesize 'wsl cp <38 jpg + poll.log + census/samples> /mnt/c/…'   # (explicit lists, one wsl call each)
scp "bytesize:pcsx2-t4/t32-…" /tmp/t32-fetch/                         # 38 jpg + logs (prefix fix local)
ssh bytesize 'wsl cp <6 ref PPMs> /mnt/c/…'; scp "bytesize:pcsx2-t4/*-ref-*.ppm" /tmp/t32-fetch/  # local PIL refs, shas re-verified
# R1 post-hoc (local fastdiff, validated 4/4 exact vs t32-cropdiff.py): chain scores, cross-run pairs, arrival pairs
ssh bytesize 'wsl dmesg' > /tmp/t32-dmesg-post.txt                    # 634 lines, 6 kills (3 pre + 3 post, H6)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H6 …5798 (H5→H6 restart mid-session)
ssh bytesize 'wevtutil …' > /tmp/t32-eventlog-post.txt                # head H6-create 00:43:18, no in-window entries
ssh bytesize 'wsl sha256sum …/bios/….nvm'                            # da021d2a… untouched
ssh bytesize 'wsl ls -la …/logs/'                                     # 19 emulogs, T31 R1 preserved
ssh bytesize 'wsl df -h /mnt/c'                                       # C: 26G avail
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t32-20260921T044637Z.txt'  # 8cbf2827… T31R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t32r1-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t32r1-trace-tail.txt         # 2000 lines, clean tail @400.9075
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t32r1.txt'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t32r1.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t32r1.txt"         # 7f14d876… match
# report (chunks; receipts include tail -3)
cp /tmp/t32-dmesg-*.txt /tmp/t32-eventlog-*.txt /tmp/t32r1-run-stdout.txt local/research/T32/  # renamed per §evidence
tail -3 local/research/T32/REPORT.md
git add -f local/research/T32/<54 files by name>                      # ignored dir, forced
git commit -m "[T32] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T32-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Select Event park) | Reproduce the R1 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → ≤3 attempts) → Select Event with Snow Jam highlighted; then a single 534 ms Cross (× Select, tagline `Snow Jam is an exciting BEGINNER track with heavy forests and patches of fog.`) to choose Snow Jam, screenshot-verify the next screen. Gate note: the SM→SE whole-frame distance is only ~0.50 (hop) / ~0.53 (vs-SM) — a Select Event ref (from `t32r1-rc-stab6.jpg`, PIL `convert('RGB').save` recipe) plus a tighter gate (SE-vs-SE spread is ≤0.064; nearest non-SE is SM at ~0.51, so a < 0.2-style bar or a header/list-region crop deserves calibration) is needed; DEPARTED > 5.0 does NOT fire on this hop. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The arrival screen is static (133 s, no reclaim) so no dwell pressure on arrival→next presses |
| G2 | WSL killer continues + 1 mid-session restart (H5→H6, not by me) | 6 userland `AcceptAsync` kills on VM-H6, all outside the R1 window (3 pre-run @35–118, 3 post-run @625–921) + 1 H5 flap @19.56 pre-run + 1 mid-session VM restart between pre-checks and R1 (H5 04:39:13→04:42:54, H6 create 04:43:18; every ssh exit 0 across it) + 2 pre-session VM restarts between T31 and T32 (H4→short-lived→H5; T31: 7 flaps + 1 pre-session restart). The run completed exit 0 with zero in-window flaps on the dmesg record (no T27 §4 effects-verification needed); precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero flap entries; boundaries bound the restart | Newest-30 reads (pre/post): H5 create 00:39:13 → H5 teardown 00:42:54 → H6 create 00:43:18; zero entries at any flap time and zero boundaries inside the run window (precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H6 btime |
| G4 | Hold count 45/45 | 534 ms-class holds register 45/45 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32 (T32: 535.7/535.4/536.5/535.3/536.6/550.5/537.4 ms — the 550.5 ms Peak hold is the longest to date, still acted). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/SC/ZC/SP/SM/SE frozenness; attract differs | Title text-band frozen across showings (0.0468/1 vs 0.0467/1) and 5 chain frames bit-identical T32-vs-T30 (a1-poll01/pre, a1-post3/15/25 — the attract/title/menu timing lottery landed back on T30's phase); a1-post15 xrun 0.0004/0 max 7 again (single-px JPEG shimmer); menu whole-frame ≤0.057/p99 ≤1 cross-run; SC cross-run 0.12–0.26/p99 3–6; ZC cross-run 0.25–0.51/p99 5–11 (zc-post1 settling, 0.52 in-run hop); SP cross-run ≤0.14/p99 ≤1; SM cross-run 0.02–0.06/p99 0–1; Select Event ≤0.064/p99 ≤1 over 133 s (near-frozen); attract phase differs this run (16.12/154, no phase coincidence). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the fifth-submenu run | `WaitVblankStart` stops after log ≤90 in T32 R1 including Select Event arrival (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T31-R1-identical modulo counts). The attract/title/menu/submenu sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical) | Like prior arrivals, Select Event arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T31 R1; only counts grow (`sceSdGetParam` 1266→1426, `sceSdGetAddr` 3.21M→3.47M). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~20 GB across 19 emulogs (T17→T32 chain, all preserved); C: 26 G avail (unchanged pre→post — run staging offset by parallel-brief churn; T31 pre was 31 G). T32 full trace SSD-copied + sha-verified (2.26 GB: `emulog-t32r1.txt`); committed slices only (2 × 2000-line head/tail) |
| G9 | Brief-name check: all real | The T32 brief cites `t31r1-pc-post{1,3,8,15,25,40}.jpg` + `t31r1-pc-stab{1…6}.jpg` — all 12 exist with shas+sizes reproducing T31 §T31-2; the PIL `convert('RGB').save` ref recipe reproduces byte-exactly (PPM-vs-JPEG 0.0000/0). T28 G9 lesson holds |
| G10 | Session wall + run duration | ~35 min active of the 4 h box (+ report/commit); zero lease waits (no lease exists for T32). Run wall 417 s — 57 s over the ≤6 min guidance (added SM-phase scoring); full dmesg coverage, zero in-window flaps, no re-run needed |
| G11 | X11 mount landed on the wrong generation; no operator pipe typos | The `/tmp/.X11-unix` tmpfs mount ran on VM-H5 and was wiped by the H5→H6 restart, yet R1 started Xvfb :99 cleanly on H6 regardless (exit 0 + 38 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL. All remote calls pipe-free first try. No run impact either way |

## Evidence files

`REPORT.md` (this file),
scripts: `t32-auto.sh`, `t32-cropdiff.py` (T31 logic, byte-identical),
`t32-analyze.sh`, `t32-vcount.sh` (byte-identical);
R1: `t32r1-start.jpg`, `t32r1-a1-now.jpg`, `t32r1-a1-poll01.jpg`,
`t32r1-a1-pre.jpg`, `t32r1-a1-post{3,8,15,25}.jpg`, `t32r1-menupre.jpg`,
`t32r1-mc-post{1,3,8,15}.jpg`, `t32r1-scpre.jpg`,
`t32r1-zc-post{1,3,8}.jpg`, `t32r1-ccpre.jpg`,
`t32r1-sp-post{1,3,8}.jpg`, `t32r1-sppre.jpg`,
`t32r1-pc-post{1,3,8}.jpg`, `t32r1-smpre.jpg`,
`t32r1-rc-post{1,3,8,15,25,40}.jpg`, `t32r1-rc-stab{1…6}.jpg` (38 snaps),
`t32r1-census.txt`, `t32r1-samples.txt`, `t32r1-poll.log`,
`t32r1-stdout.txt`, `t32r1-stderr.txt`, `t32r1-trace-head.txt` / `t32r1-trace-tail.txt`;
flaps: `t32-dmesg-vmH5-pre.txt` (1 kill on H5, pre-run) /
`t32-dmesg-vmH6-post.txt` (6 kills on H6: 3 pre-run + 3 post-run, full
run-window coverage),
`t32-eventlog-pre.txt` / `t32-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t32r1.txt`
(2,259,205,200 B `7f14d876…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T31 R1
`…-20260921T044637Z.txt` `8cbf2827…`.
