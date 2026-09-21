# T33 report — Cross on Snow Jam from the Select Event park: next screen (bytesize, no lease)

Brief: T33 (Cross on Snow Jam from the Select Event park). Tables, no
verdicts. Two boots ran on bytesize (R1 NO-SE-PARK on a true SE park —
remote TAG-crop gap underestimated; R2 with widened gate); laptop-side work
was ssh/scp + local reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T32/REPORT.md` (all: R1 reached Select
Event via Cross on Race @T+266.01, Snow Jam highlighted (orange bar) /
Metro-City / Happiness, course-map `Race` panel, tagline `Snow Jam is an
exciting BEGINNER track with heavy forests and patches of fog.`, 12 snaps
over 133 s pairwise ≤0.064/p99 ≤1, no reclaim; G1 proposes one 534 ms Cross
(× Select) on Snow Jam, WITH A GATE WARNING — read it). This brief executes
T32's G1.

Experiment contract (up front): hypothesis — one 534 ms-class Cross on the
parked Select Event (Snow Jam highlighted) chooses Snow Jam / enters the
next screen; observable — pre-press snap = Select Event (whole-frame match
vs T32 `rc-stab6` ref under the calibrated < 0.2 gate + TAG-crop line +
viewed snap), post-press snap series + per-hop whole diffs + arrival
stability N; screen content read off viewed snaps; alternatives — screen
ignores Cross (post series still Select Event), slow next-screen load
(change lands late in the +40 s tail), press never acted on arrival
(pre-press ≠ Select Event → ONE bounded variant allowed); stop — table the
exact observed behavior + recipe, no button-mashing survey.

## T33-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T33; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T33]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T33 observed | Match |
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
| T32 reference snaps present | — | all 12 arrival shas reproduce T32 §T32-2 (`post{1,3,8,15,25,40}` + `stab{1…6}` full sha256 + sizes) | yes |
| Free space | — | WSL `/` 894 G avail; C: 24 G (836 G); laptop `/` 11 Gi avail; SSD 417 Gi free | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) ×1 (VM-H7; wiped by H7→H8 restart, R1/R2 unaffected — T32 G11 stands) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached by the script (`pkill` + `setsid nohup`) |
| Dirs/files created | `/home/brad/pcsx2-t4/t33-{auto,analyze,vcount,cropdiff}.sh/.py`, `t33-ref-se.ppm` (3,932,177 B, sha `4baec4bc…bedd889d`), `t33-{r2-census,samples}.txt` (via analyze), `t33-*.jpg/.ppm/.log`, `…/logs/emulog-pre-t33-*.txt` (rotation chain, see trace table), `boot-t33.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t33*` + `emulog-t33r2.txt` staging |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits), live NVM (`da021d2a…`, mtime Sep 20 15:20) |
| VM restarts (not by me) | 1 mid-session (H7→H8 between staging and R1) + 2 pre-session between T32 and T33 (H6→short-lived→H7; parallel briefs active — inference, T25 G2 precedent) |

WSL session log (clocks: WSL `date -u` true UTC; `wevtutil` renders
local-as-Z, +4 h → UTC, re-confirmed on VM-H7 btime:
01:29:59→`1789968599`):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 05:13:55 | VM-H6 teardown (T32's VM, after T32's session) | eventlog-pre (IDs 69/71) |
| 2 | 05:15:41–05:16:58 | Short-lived VM create→teardown (~77 s lifetime) | eventlog-pre (IDs 292… create, 69/71 teardown) |
| 3 | 05:29:59 ([0] VM-H7) | VM-H7 started fresh ~2 s before first ssh | btime `…8599`, eventlog-pre head (IDs 292/67/291/233/232/102/291) |
| 4 | 05:30:01–~05:33 | Pre-run checks + staging on VM-H7 (all ssh exit 0, zero flaps) | `t33-dmesg-vmH7-pre.txt` (0 kills, 417 lines) |
| 5 | 05:33:59 ([0] VM-H8) | VM-H7 teardown → VM-H8 create (mid-session restart, NOT by me; between staging and R1; every ssh exit 0 across it; staged files persist — same VHD) | btime `…8839`, eventlog-post (to be tabled) |
| 6 | 05:32:15–05:33:59 | VM-H7 teardown → VM-H8 create (mid-session restart, NOT by me; between staging and R1; 104 s gap with no VM; every ssh exit 0 across it; staged files persist — same VHD) | btime `…8839`, eventlog-post (IDs 69/71 teardown, 292/67/291/233/232/102/291 create) |
| 7 | 05:34:27–05:39:30 ([28]→[331] H8) | R1 single-shot exit 0, `T33_DONE`, clean shutdown, ZERO flaps in-window (full dmesg coverage, no restart in-window) | exit 0, 29 snaps, trace sha |
| 8 | 05:39:45, 05:40:56 ([346.39],[416.67] H8) | Flaps #1–#2 on VM-H8, BOTH post-R1 (each ssh still exit 0; R1 artifacts fetched + sha-valid after) | `t33-dmesg-vmH8-mid.txt` (full boot→420 coverage) |
| 9 | 05:42:58–05:50:23 ([539]→[983] H8) | R2 single-shot exit 0, `T33_DONE`, clean shutdown, effects-verified (complete coherent artifacts + clean trace tail + census); NO dmesg coverage of the R2 window — H8 destroyed by the post-run restart before a post-R2 dmesg read (sequencing gap, §T33-5); zero VM boundaries in-window | exit 0, 42 snaps, trace sha, eventlog-post |
| 10 | 05:51:04–~05:54 | R2 analyze (exit 0) + all R2 fetches (exit 0, sha-valid) on VM-H8 | `t33r2-census.txt`, 42 JPGs |
| 11 | 05:54:05–05:54:31 | VM-H8 teardown → VM-H9 create (post-everything restart, NOT by me; 26 s gap; only dmesg-post/btime/eventlog reads ran on H9) | btime `…0071`, eventlog-post head (IDs 69/71 teardown, 292/67/291/233/232/102/291 create) |
| 12 | 05:54:42 ([11.59] H9) | VM-H9 fresh, 0 kills | `t33-dmesg-vmH9-post.txt` (416 lines, boot coverage) |
| 13 | event log | Newest-30 reads (pre/post): head moves H7-create 01:29:59 → H9-create 01:54:31; boundaries H7-teardown 01:32:15, H8-create 01:33:59, H8-teardown 01:54:05, H9-create 01:54:31; zero entries at either flap time (01:39:45, 01:40:56 local) and zero VM-boundary events inside either run window — userland kills leave no Windows trace (T17/T21/T23/T25/T27/T28/T29/T30/T31/T32 precedent stands) | `t33-eventlog-{pre,post}.txt` |
| 14 | dmesg noise | `Ioctl failed` lines 0 pre (H7, read at uptime ~2 s) / 46 mid (H8) / 0 post (H9, read at uptime ~12 s) — steady boot/GPU-query noise, not kills | dmesg files |

## T33-1. SE detector + calibration (thresholds, match scores)

Tool: `t33-cropdiff.py` (copy of T32's, unmodified logic — byte-identical;
`t33-vcount.sh` likewise). Title text-band method unchanged (thresholds
frozen: TITLE band mean < 2.0 AND p99 ≤ 10; STATIC whole mean < 1.0; MENU
whole-vs-menu mean < 2.0; NONMENU / NONSC / NONZC / NONSP whole-vs-ref mean
> 5.0; DEPARTED whole hop mean > 5.0). New: Select Event reference
`t33-ref-se.ppm` (3,932,177 B, sha
`4baec4bcbda0f87dffc9433e0b6df1a06850c15465477d7104bb719dbedd889d`),
derived from T32's `t32r1-rc-stab6.jpg` via
`Image.open(...).convert('RGB').save(...)` (exact command in §T33-4; T28
§T28-1 recipe). Ref-vs-JPEG recipe check: 0.0000/0 (JPEG decode
deterministic, T28 G9 lesson holds).

Game-area geometry (new this brief): the game renders 640×480-ish at frame
top-left (non-black x∈[0,~640], y∈[20,~515]; all SM-vs-SE diffs with |d|>25
inside x∈[40,565], y∈[68,456]).

SE whole-frame calibration matrix (candidate vs `t32r1-rc-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post1 vs stab6 | 0.0523 | 0 | 45 | SE-SE (whole) |
| post3 vs stab6 | 0.0496 | 0 | 45 | SE-SE (whole) |
| post8 vs stab6 | 0.0477 | 0 | 48 | SE-SE (whole) |
| post15 vs stab6 | 0.0375 | 0 | 45 | SE-SE (whole) |
| post25 vs stab6 | 0.0633 | 1 | 45 | SE-SE (whole, worst mean) |
| post40 vs stab6 | 0.0353 | 0 | 45 | SE-SE (whole) |
| stab1 vs stab6 | 0.0453 | 0 | 52 | SE-SE (whole) |
| stab2 vs stab6 | 0.0350 | 0 | 45 | SE-SE (whole) |
| stab3 vs stab6 | 0.0456 | 0 | 45 | SE-SE (whole) |
| stab4 vs stab6 | 0.0462 | 0 | 52 | SE-SE (whole) |
| stab5 vs stab6 | 0.0357 | 0 | 45 | SE-SE (whole) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| smpre (T32 SM) vs stab6 | 0.5071 | 8 | 236 | SM-vs-SE (whole) |
| pc-post1 (T32 SM) vs stab6 | 0.5333 | 11 | 236 | SM-vs-SE (whole) |
| pc-post3 (T32 SM) vs stab6 | 0.5195 | 10 | 236 | SM-vs-SE (whole) |
| pc-post8 (T32 SM) vs stab6 | 0.5275 | 10 | 236 | SM-vs-SE (whole) |
| sppre (T32 SP) vs stab6 | 5.3707 | 122 | 242 | SP-vs-SE (whole) |
| sp-post1/3/8 (T32 SP) vs stab6 | 5.3717/5.3329/5.3108 | 122/121/121 | 242 | SP-vs-SE (whole) |
| ccpre (T32 ZC) vs stab6 | 10.2180 | 165 | 244 | ZC-vs-SE (whole) |
| zc-post1/3/8 (T32 ZC) vs stab6 | 10.2376/10.2303/10.2257 | 164/165/164 | 244 | ZC-vs-SE (whole) |
| scpre (T32 SC) vs stab6 | 11.9078 | 159 | 255 | SC-vs-SE (whole) |
| mc-post1/3/8/15 (T32 SC) vs stab6 | 11.9080/11.9338/11.8896/11.8877 | 158/157/157/157 | 255 | SC-vs-SE (whole) |
| menupre (T32) vs stab6 | 10.9426 | 177 | 240 | menu-vs-SE (whole) |
| a1-post3/8/15/25 (T32 menu) vs stab6 | 10.9548/10.9446/10.9433/10.9424 | 177 | 240 | menu-vs-SE (whole) |
| a1-pre = a1-poll01 (T32 title) vs stab6 | 16.2477 | 160 | 249 | title-vs-SE (whole) |
| start (T32 attract) vs stab6 | 16.0063 | 169 | 245 | attract-vs-SE (whole) |
| a1-now (T32 attract) vs stab6 | 15.9396 | 177 | 243 | attract-vs-SE (whole) |
| ref PPM vs stab6 JPEG | 0.0000 | 0 | 0 | recipe exact (JPEG decode deterministic) |
| ref PPM vs ref PPM | 0.0000 | 0 | 0 | self |

TAG-crop calibration matrix (`40,415,330,450`, tagline band; candidate vs
`t32r1-rc-stab6.jpg`, PIL mode):

| Pair | mean | p99 | max | Class |
|---|---|---|---|---|
| post1 vs stab6 | 0.0112 | 0 | 7 | SE-SE (TAG) |
| post3 vs stab6 | 0.0114 | 0 | 7 | SE-SE (TAG) |
| post8 vs stab6 | 0.0098 | 0 | 7 | SE-SE (TAG) |
| post15 vs stab6 | 0.0330 | 1 | 7 | SE-SE (TAG) |
| post25 vs stab6 | 0.0669 | 2 | 7 | SE-SE (TAG) |
| post40 vs stab6 | 0.0808 | 2 | 9 | SE-SE (TAG) |
| stab1 vs stab6 | 0.1401 | 4 | 15 | SE-SE (TAG, worst mean) |
| stab2 vs stab6 | 0.0094 | 0 | 7 | SE-SE (TAG) |
| stab3 vs stab6 | 0.0094 | 0 | 7 | SE-SE (TAG) |
| stab4 vs stab6 | 0.1033 | 2 | 16 | SE-SE (TAG) |
| stab5 vs stab6 | 0.0094 | 0 | 7 | SE-SE (TAG) |
| stab6 vs stab6 | 0.0000 | 0 | 0 | self |
| smpre / pc-post1/3/8 (T32 SM) vs stab6 | 14.1390/14.1390/14.1390/14.1405 | 88 | 101 | SM-vs-SE (TAG) |
| sppre / sp-post1/3/8 (T32 SP) vs stab6 | 14.0029/14.0026/14.0026/14.0026 | 89 | 101 | SP-vs-SE (TAG) |
| ccpre / zc-post1/3/8 (T32 ZC) vs stab6 | 15.3303/15.3006/15.3231/15.3218 | 91 | 101 | ZC-vs-SE (TAG) |
| scpre / mc-post1/3/8/15 (T32 SC) vs stab6 | 26.5696–26.5708 | 90 | 107 | SC-vs-SE (TAG) |
| menupre / a1-post3/8/15/25 (T32 menu) vs stab6 | 26.1512–26.1728 | 106 | 149 | menu-vs-SE (TAG) |
| a1-pre = a1-poll01 (T32 title) vs stab6 | 106.6172 | 205 | 218 | title-vs-SE (TAG) |
| start / a1-now (T32 attract) vs stab6 | 44.0097/84.2620 | 163/195 | 184/230 | attract-vs-SE (TAG) |

Backup-crop summary (PIL; full per-pair rows omitted, ranges tabled):

| Crop | SE-SE range | SM-vs-SE | SP | ZC | SC | menu | title | attract | Frozen? |
|---|---|---|---|---|---|---|---|---|---|
| LIST `110,195,270,270` | 0.0000–0.1488/p99 ≤3 | 21.7416–21.7440/144 | 45.10–45.48/159 | 50.03–52.07/148 | 51.10–51.65/147–148 | 44.39–44.46/115 | 99.4033/221 | 54.59–72.79 | backup (unused) |
| PTITLE `310,110,410,135` | 0.0000/0 all 12 | 16.1399–16.5133/119 | 17.9912/121 | 56.5619/97 | 49.5028/114 | 59.1963/102 | 51.4588/118 | 47.43–68.00 | backup (unused) |
| HDR `40,60,280,110` | 0.0000–3.5463/p99 ≤37 | 4.9762–5.2103/52 | 4.3584–5.1531/41–47 | 19.5104/89 | 18.50–18.95/91–95 | 18.92–19.31/85–86 | 19.6954/99 | 46.41–61.05 | REJECTED (SE-SE up to 3.55 overlaps SP 4.36) |

SE gate (R1 as frozen pre-run, R2 as widened): in-script park criterion =
arrival static (rc hops post1→post3 and post3→post8 both < 1.0) AND non-SP
(post8 vs-sp > 5.0) AND se-tag (post8 TAG-crop-vs-SE-ref mean < 2.0 in R1,
< 5.0 in R2 — R1 NO-SE-PARKed on a true SE park: remote se-tag 2.6271/p99
11 on all 3 RC snaps vs PIL 0.009–0.012, a ~290× remote-vs-PIL inflation on
the text-dense crop from JPEG ringing in the ref around glyph edges, vs ~9×
on whole-frame; SM side PIL 14.14 / remote ≈14+). The SnowJam Cross press
does NOT depend on a strict whole-frame SE gate (T28 MENU / T29 SC / T30 ZC
/ T31 SP / T32 SM precedent); the post-hoc "Cross acted on SE" bar is
whole-vs-SE-ref mean < 0.2 PIL + se-tag < 2.0 PIL + viewed snap. Margins:
whole post-hoc SE-side worst 0.0633→3.2×, SM-side nearest 0.5071→2.5×;
in-script R2 SE-side 2.63 vs 5.0 (1.9×), SM-side ~14 vs 5.0 (2.8×);
non-SP-side 5.28–5.46 vs 5.0 (1.06–1.09× — tight, tabled).

Script deltas vs `t32-auto.sh` (committed originals untouched; `t33-auto.sh`
is the adapted copy; `t33-auto-r1.sh` preserves the R1 gate):

| Area | T32 R1 script | T33 script |
|---|---|---|
| Chain | park phase + MENU Cross + mc series to +15 + scpre + ZOE Cross + zc series to +8 + ccpre + CONT Cross + sp series to +8 + sppre + PEAK Cross + pc series to +8 + smpre + RACE Cross + rc series to +40 + 6×10 s stab | identical through RACE Cross; rc series shortened to rc-post1/3/8 (each + se-tag score; vs-sp + whole-vs-se on post8 only), + `smpre` se-tag line (R2 only) |
| SE park | (arrival was the end) | SE-park gate (static + non-SP + se-tag; DEPARTED deliberately NOT used — T32 G1 warning) + `sepre` snap (se-tag + vs-se + vs-sm + vs-sp + titleband) |
| T33 press | — | ONE `SNOWJAM_CROSS` (K), arrival series +1/+3/+8/+15/+25/+40 (each titleband + vs-se + se-tag), 6 per-hop whole diffs, 6×10 s arrival stability (band + se-tag in-script; whole-vs-se post-hoc local) |
| Self-tests | SELF_TEST + SELF_WHOLE + SELF_MENU + SELF_SC + SELF_ZC + SELF_SP + SELF_SM | + SELF_SE (whole) + SELF_SETAG (TAG crop) |
| No-park paths | explicit `NO-PARK` + … + `NO-SM-PARK` | + explicit `NO-SE-PARK` plog, still clean shutdown + `T33_DONE` (trace preserved) |
| R1→R2 delta | — | `SETAG_MEAN_MAX` 2.0→5.0 + `SMPRE se-tag` line + gate comment (4-line diff, tabled in §T33-4) |

Local scoring note: post-hoc PIL scores below were computed with a numpy
port of `t33-cropdiff.py` (`/tmp/t33-fastdiff.py`, NOT committed —
analysis scratch), validated bit-exact (mean/p99/max/npix identical, only
the mode tag differs) against the committed tool on 4 diverse pairs
(whole SE-SE, whole SM-SE, TAG SM-SE, TAG SE-SE). Any score reproduces with
the committed `t33-cropdiff.py`, slower.

## T33-2. R1 — park reproduced, gate misfire (NO-SE-PARK on a true SE park)

Run: `t33-auto-r1.sh` (SETAG bar 2.0), ONE fresh boot, T_BOOT wall
1789968873 (uptime 34, VM-H8), 05:34:27–05:39:30 UTC (uptime 28→331 =
303 s), WID 2097159 (same as T31 R1 / T32 R1), exit 0, `T33_DONE`, clean
SIGTERM shutdown. SELF_TEST 0.0000/0, SELF_WHOLE 0.0000, SELF_MENU
0.0000/0, SELF_SC 0.0000/0, SELF_ZC 0.0000/0, SELF_SP 0.0000/0, SELF_SM
0.0000/0, SELF_SE 0.0000/0, SELF_SETAG 0.0000/0. Attempt 1 of ≤3 consumed.

### R1 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+99, score 0.4329/6 remote / 0.0468/1 PIL (T32: 0.4329/6 / 0.0468/1 — poll01 frame bit-identical to T32's = T30's, see identities) | Cross 535.4 ms @T+97.29 (attract-skip) + Start 536.7 ms @T+100.55 (on title, ≤1.6 s after exposure-second start) | Main Menu by +4 s; menu-like gate (non-title + whole-static 0.0391/0.0201) + post25-vs-menu 0.3033/5 → park for menu Cross |
| A2–A3 | A2 ran as R2 (recalibrated gate); A3 not needed (Cross advanced) | — | — |

### R1 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789968970.291504768 → 1789968970.826944650 | 535.4 ms | T+97.29→97.83 | 131 | `a1-now` attract (27.3481/172 remote; 27.3564/173 PIL) | `a1-poll01` TITLE (0.4329/6; 0.0468/1) |
| A1 Start (Return) | 1789968973.552157767 → 1789968974.088881049 | 536.7 ms | T+100.55→101.09 | 134 | `a1-pre` ≡ `a1-poll01` (sha `6e3d747fd514`, TITLE, bit-identical to T32's viewed frame) | `a1-post3` Main Menu (16.2540/139; 16.2551/138) |
| MENU Cross (K) | 1789969012.697723000 → 1789969013.235198075 | 537.5 ms | T+139.70→140.24 | 173 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0274/0 PIL; vs-title 16.2610/139) | `mc-post1` Select Character (vs-menu 10.2148/106; vs-sc 0.4964/8; titleband 12.5512/164) |
| ZOE Cross (K) | 1789969052.637189690 → 1789969053.174437421 | 537.2 ms | T+179.64→180.17 | 213 | `scpre` Select Character, Zoe selected (vs-sc 0.5542/8 remote; 0.2083/4 PIL; vs-menu 10.1969/105; vs-title 12.6457/164) | `zc-post1` Setup Character (vs-sc 7.2285/100; vs-zc 0.5228/9; titleband 15.9280/128) |
| CONT Cross (K) | 1789969081.364348348 → 1789969081.902836158 | 538.5 ms | T+208.36→208.90 | 242 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4133/7 remote; 0.1774/4 PIL; vs-sc 7.2722/100; vs-title 15.7921/128) | `sp-post1` Select Peak (vs-zc 9.4698/154; vs-sp 0.3729/6; titleband 23.1273/171) |
| PEAK Cross (K) | 1789969110.040260232 → 1789969110.575833763 | 535.6 ms | T+237.04→237.58 | 270→271 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.4244/6 remote; 0.0796/0 PIL; vs-zc 9.5213/154; vs-title 23.1279/171) | `pc-post1` Select Mode (vs-sp 5.3724/121; vs-sm 0.4115/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789969138.728968524 → 1789969139.264096250 | 535.1 ms | T+265.73→266.26 | 299→300 | `smpre` Select Mode, Race highlighted (vs-sm 0.3920/6 remote; 0.0410/0 PIL; vs-sp 5.3517/121; vs-title 26.3170/183) | `rc-post1` Select Event (vs-sm 0.8071/11; se-tag 2.6271/11; titleband 26.2118/183) |

Within-dwell receipts R1: Cross-keyup → Start-keydown 2.7 s; poll01
exposure-second start (1789968972) → Start-keydown 1789968973.552 ≤ 1.6 s;
R2-measured title persistence 15–17 s ⇒ press inside the window with an
order of magnitude to spare. Start-keyup → MenuCross-keydown 38.6 s;
MenuCross-keyup → ZoeCross-keydown 39.4 s; ZoeCross-keyup →
ContCross-keydown 28.2 s; ContCross-keyup → PeakCross-keydown 28.1 s;
PeakCross-keyup → RaceCross-keydown 28.2 s (no dwell pressure — all parks
static, T27 G1 / T28 G1 / T29 G1 / T30 G1 / T31 G1 / T32 G1 precedent).

### R1 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|
| start (T+95) | 53729B / `d534f82a3319` | 17.3311/125 | 10.5106/116 | 12.7399/135 | 10.6067/111 | 13.3747/149 | 13.5706/160 | 13.6944/161 | 59.7444/139 | Attract |
| a1-now (T+96, pre-Cross) | 58121B / `02e91a400317` | 27.3564/173 | 16.0345/163 | 15.0894/162 | 15.7603/154 | 15.4211/169 | 14.7423/166 | 14.8462/167 | 51.4389/156 | Attract |
| a1-poll01 = a1-pre (T+99, pre-Start) | 58374B / `6e3d747fd514` | 0.0468/1 T | 14.1347/151 | 11.3076/152 | 12.2567/146 | 15.3703/156 | 16.1499/158 | 16.2477/160 | 106.6172/205 | TITLE |
| a1-post3 (T+104) | 50107B / `d76dc057a28a` | 16.2551/138 | 0.0822/1 | 10.1414/105 | 6.9326/93 | 10.4164/170 | 10.9446/177 | 10.9614/177 | 26.1710/106 | Main Menu |
| a1-post8 (T+109) | 50012B / `547b3d2f2b2f` | 16.2902/138 | 0.0680/1 | 10.1190/105 | 6.9242/93 | 10.3917/170 | 10.9219/177 | 10.9469/177 | 26.1720/106 | Main Menu |
| a1-post15 (T+117) | 49634B / `4c56f8159c76` | 16.2622/138 | 0.0256/0 | 10.1073/105 | 6.9081/93 | 10.3855/170 | 10.9184/177 | 10.9433/177 | 26.1710/106 | Main Menu |
| a1-post25 (T+128) | 49804B / `410ae0ac2c97` | 16.2622/138 | 0.0478/0 | 10.1228/105 | 6.9157/93 | 10.3954/170 | 10.9285/177 | 10.9424/177 | 26.1676/106 | Main Menu |
| menupre (T+138, pre-MCross) | 49628B / `1307199a73f1` | 16.2622/138 | 0.0274/0 | 10.1077/105 | 6.9079/93 | 10.3848/170 | 10.9178/177 | 10.9428/177 | 26.1637/106 | Main Menu, Single Event highlighted |
| mc-post1 (T+141) | 70220B / `d5e6c34299f0` | 12.4795/163 | 10.1474/105 | 0.1488/3 | 7.1838/101 | 11.3734/158 | 11.8410/158 | 11.9119/158 | 26.5701/90 | Select Character, Zoe |
| mc-post3 (T+145) | 70480B / `ca05fda145ba` | 12.4827/163 | 10.1612/107 | 0.1505/3 | 7.2191/100 | 11.4027/158 | 11.8676/157 | 11.9377/157 | 26.5700/90 | Select Character |
| mc-post8 (T+153) | 70275B / `db3ea60609d6` | 12.4587/163 | 10.1478/105 | 0.2543/4 | 7.2316/100 | 11.3548/158 | 11.8212/157 | 11.8966/157 | 26.5695/90 | Select Character |
| mc-post15 (T+163) | 70046B / `90e4c30e058d` | 12.4587/163 | 10.1289/105 | 0.0027/0 | 7.2298/100 | 11.3506/158 | 11.8131/157 | 11.8815/157 | 26.6085/90 | Select Character |
| scpre (T+176, pre-ZCross) | 70190B / `481e9d73a4ce` | 12.5672/163 | 10.1297/105 | 0.2083/4 | 7.2066/100 | 11.3539/158 | 11.8304/157 | 11.9010/157 | 26.5696/90 | Select Character, Zoe selected |
| zc-post1 (T+181) | 51477B / `b1dfc39aa83e` | 15.9045/129 | 6.9264/93 | 7.2004/100 | 0.2908/7 | 9.3667/153 | 10.1361/164 | 10.2473/164 | 15.2978/91 | Setup Character, Zoe |
| zc-post3 (T+185) | 51590B / `e23b93c7028a` | 15.8290/128 | 6.9111/92 | 7.2651/101 | 0.2326/6 | 9.3446/153 | 10.1064/165 | 10.2195/165 | 15.3047/91 | Setup Character |
| zc-post8 (T+193) | 51395B / `2bb47f81b6a6` | 15.8302/128 | 6.9322/92 | 7.0991/100 | 0.2475/6 | 9.3794/153 | 10.1312/164 | 10.2240/164 | 15.3051/91 | Setup Character |
| ccpre (T+205, pre-ContCross) | 51426B / `4bf7f2013bd2` | 15.7753/128 | 6.8982/92 | 7.2460/100 | 0.1774/4 | 9.3485/153 | 10.1019/164 | 10.2144/164 | 15.3296/91 | Setup Character, Zoe + Continue |
| sp-post1 (T+209) | 65296B / `461336b00db7` | 23.1259/171 | 10.4254/170 | 11.3466/158 | 9.3894/153 | 0.0259/0 | 5.2240/121 | 5.3308/121 | 14.0029/89 | Select Peak, Peak 1 |
| sp-post3 (T+214) | 65415B / `d1c1c56fbef8` | 23.1259/171 | 10.4359/170 | 11.3784/158 | 9.3817/153 | 0.0454/0 | 5.2450/121 | 5.3475/121 | 14.0026/89 | Select Peak |
| sp-post8 (T+222) | 65247B / `774f16718db8` | 23.1273/171 | 10.4061/170 | 11.3503/158 | 9.3728/153 | 0.0046/0 | 5.2067/121 | 5.3099/121 | 14.0026/89 | Select Peak |
| sppre (T+234, pre-PeakCross) | 65751B / `57469598e6fa` | 23.1259/171 | 10.4761/170 | 11.4197/158 | 9.4424/153 | 0.0796/0 | 5.2800/121 | 5.3621/121 | 14.0026/89 | Select Peak, Peak 1 highlighted |
| pc-post1 (T+238) | 67567B / `4545eb2c8828` | 26.3046/183 | 10.9354/178 | 11.8226/157 | 10.1207/164 | 5.2067/121 | 0.0643/0 | 0.4754/6 | 14.1329/88 | Select Mode, Race |
| pc-post3 (T+243) | 67420B / `4a4cb240f6ba` | 26.3046/183 | 10.9147/178 | 11.8044/157 | 10.1017/164 | 5.1822/121 | 0.0408/0 | 0.5121/9 | 14.1406/88 | Select Mode |
| pc-post8 (T+250) | 67648B / `3c6f5ec1347a` | 26.3232/183 | 10.9427/178 | 11.8047/157 | 10.1288/164 | 5.2123/121 | 0.0654/1 | 0.5409/12 | 14.1664/88 | Select Mode |
| smpre (T+263, pre-RaceCross) | 67455B / `14005864526c` | 26.3046/183 | 10.9152/178 | 11.8052/157 | 10.1034/164 | 5.1824/121 | 0.0410/0 | 0.5125/9 | 14.1390/88 | Select Mode, Race highlighted |
| rc-post1 (T+267) | 69438B / `7330257e2626` | 26.1983/183 | 10.9385/178 | 11.8587/157 | 10.2162/164 | 5.2823/121 | 0.5092/9 | 0.0318/0 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+271) | 69533B / `49b8b5ce6180` | 26.1964/183 | 10.9530/178 | 11.8682/157 | 10.2303/164 | 5.2982/121 | 0.5224/10 | 0.0487/0 | 0.0123/0 | Select Event |
| rc-post8 (T+278) | 69596B / `b6351798bb92` | 26.1964/183 | 10.9494/178 | 11.8693/157 | 10.2234/164 | 5.2977/121 | 0.5209/10 | 0.0474/0 | 0.0094/0 | Select Event (viewed) |

### R1 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1196 | 10.1271/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1264 | 0.1547/3 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2673 | 0.2920/7 | same screen |
| post8 → post15 (mc) | 0.2357 | 0.2558/4 | same screen |
| post15 → scpre (park span) | — | 0.2098/4 | same screen |
| scpre → zc-post1 | 7.2039 | 7.2284/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.2959 | 0.3190/9 | arrival settling |
| post3 → post8 (zc) | 0.2920 | 0.3132/7 | same screen |
| post8 → ccpre (park span) | — | 0.2962/7 | same screen |
| ccpre → sp-post1 | 9.3197 | 9.3563/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0585 | 0.0646/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0384 | 0.0423/0 | same screen |
| post8 → sppre (park span) | — | 0.0765/0 | same screen |
| sppre → pc-post1 | 5.2320 | 5.2563/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0337 | 0.0373/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0391 | 0.0437/0 | same screen |
| post8 → smpre (park span) | — | 0.0439/0 | same screen |
| smpre → rc-post1 | 0.4567 | 0.4822/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps) |
| post1 → post3 (rc) | 0.0160 | 0.0181/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0298 | 0.0338/0 | same screen |

### R1 NO-SE-PARK characterization (gate legs + post-hoc park proof)

| Gate leg (in-script, remote) | Value | Bar | Pass? |
|---|---|---|---|
| Arrival static p1→p3 | 0.0160 | < 1.0 | yes |
| Arrival static p3→p8 | 0.0298 | < 1.0 | yes |
| Non-SP (post8 vs-sp) | 5.4595/121 | > 5.0 | yes |
| SE-TAG (post8 TAG-crop-vs-SE) | 2.6271/11 (identical on post1/3/8) | < 2.0 (R1 bar) | NO → `NO-SE-PARK`, no SnowJam Cross pressed |

| Post-hoc park proof (PIL) | Value | Bar | Pass? |
|---|---|---|---|
| rc-post1/3/8 whole-vs-SE | 0.0318/0.0487/0.0474, p99 0 | < 0.2 | yes (inside T32's SE-SE spread 0.0350–0.0633; post1 0.0318 a hair below its min — same class) |
| rc-post1/3/8 SE-TAG | 0.0094/0.0123/0.0094, p99 0 | < 2.0 PIL | yes (inside ≤0.14) |
| rc-post1/3/8 whole-vs-SM | 0.5092/0.5224/0.5209, p99 9–10 | SE band ~0.51–0.53 | yes |
| Viewed snap | `rc-post8`: Select Event, Snow Jam highlighted (orange bar) / Metro-City / Happiness, `Race` panel, Snow Jam tagline | — | yes |
| Remote-vs-PIL TAG ratio | 2.6271 / ~0.010 ≈ 260–280× (JPEG ringing in the ref around glyph edges; whole-frame ratio on the same snaps ≈ 8.7×) | — | tabled |

R1 outcome: the park reproduced (Select Event, Snow Jam highlighted) but
the R1 se-tag bar (2.0) was set from the PIL domain without a remote-gap
receipt; the remote TAG read (2.6271) exceeded it on a true SE park. R2
widened the bar to 5.0 (SM side PIL 14.14 / R2-remote 14.3325) with no other
logic change (4-line diff, §T33-1).

### R1 cross-run frame identities (T33 R1 vs T32 R1, full sha256)

| Frame | T33 R1 sha | T32 R1 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `6e3d747fd514…` (cp-identical, pair 0.0000/0) | `6e3d747fd514…` | BIT-IDENTICAL (whole-file `cmp`; ∴ also ≡ T30's frame per T32 §T32-2) |
| a1-post15 | `4c56f8159c76…` | `4c56f8159c76…` | BIT-IDENTICAL (whole-file `cmp`) |
| a1-post25 | `410ae0ac2c97…` | `410ae0ac2c97…` | BIT-IDENTICAL (whole-file `cmp`) |
| start | `d534f82a3319…` 53729 B | `de26d7d0ce08…` 67132 B | differ; pair 15.77/144 (attract-loop phase differs) |
| a1-now | `02e91a400317…` | `713437fb5465…` | differ; pair 15.26/154 (attract phase differs) |
| a1-post3 | `d76dc057a28a…` | `f1287a7be3a6…` | differ; pair 0.0424/0 |
| a1-post8 | `547b3d2f2b2f…` | `88ae592f89f5…` | differ; pair 0.0395/0 |
| menupre | differ | differ | whole pair 0.0019/0 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.151/3, 0.155/4, 0.111/3, 0.211/4 |
| scpre | differ | differ | whole pair 0.2428/5 |
| zc-post1/3/8 | differ | differ | whole pairs 0.516/12, 0.283/7, 0.290/5 (zc-post1 arrival settling) |
| ccpre | differ | differ | whole pair 0.2665/6 |
| sp-post1/3/8 | differ | differ | whole pairs 0.086/1, 0.096/1, 0.002/0 |
| sppre | differ | differ | whole pair 0.1413/1 |
| pc-post1/3/8 | differ | differ | whole pairs 0.059/0, 0.021/0, 0.058/0 (park reproduced tightly) |
| smpre vs T32 smpre | `14005864526c…` | `a72020196915…` | whole pair 0.0069/0 |
| smpre vs T32 `rc-stab6` | `14005864526c…` | `c246f4c9bf9f…` | whole 0.5125/9, TAG 14.1390/88 (SM class, matches calibration exactly) |
| rc-post1/3/8 vs T32 `rc-stab6` | (above) | `c246f4c9bf9f…` | whole 0.0318/0.0487/0.0474, TAG 0.0094/0.0123/0.0094 (SE class) |

### R1 trace (bytes + sha; no census — partial run, no press)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Bytes | sha256 |
|---|---|---|
| `emulog-pre-t33-20260921T054304Z.txt` = R1 (chain to SE park, NO-SE-PARK, T+~300) | 1,706,068,225 | `1915aaf93fe11b5db9c2b661665e991aef9304513b069af6fe23d4c7eb5fd6dc` (live-sha at R1 end = preserved-sha post-run; match) |

## T33-2 (cont). R2 — park reproduced, Cross → My Rules

Run: `t33-auto.sh` (SETAG bar 5.0), ONE fresh boot, T_BOOT wall 1789969384
(uptime 545, VM-H8), 05:42:58–05:50:23 UTC (uptime 539→983 = 444 s; 84 s
over the ≤6 min guidance — the added SE phase + full arrival tail;
effects-verified: exit 0, `T33_DONE`, clean shutdown, 42/42 artifacts
coherent; R2-window dmesg lost to the post-run H8→H9 restart — sequencing
gap, tabled in §T33-5), WID 2097159 (same as T31 R1 / T32 R1 / T33 R1),
exit 0, `T33_DONE`, clean SIGTERM shutdown. SELF_TEST 0.0000/0, SELF_WHOLE
0.0000, SELF_MENU 0.0000/0, SELF_SC 0.0000/0, SELF_ZC 0.0000/0, SELF_SP
0.0000/0, SELF_SM 0.0000/0, SELF_SE 0.0000/0, SELF_SETAG 0.0000/0. Attempt 2
of ≤3 consumed; attempt 3 not needed (Cross advanced, arrival mapped).

### R2 attempt table (park reproduction)

| Attempt | Detect (menu-wall) | Presses | Outcome |
|---|---|---|---|
| A1 | TITLE at poll01 @T+100, score 0.4331/6 remote / 0.0467/1 PIL (T31: 0.4331/6 / 0.0467/1 — poll01 frame bit-identical to T31's, see identities) | Cross 535.8 ms @T+97.53 (attract-skip) + Start 535.2 ms @T+100.80 (on title, ≤1.0 s after exposure) | Main Menu by +4 s; menu-like gate (non-title + whole-static 0.0336/0.0122) + post25-vs-menu 0.2953/5 → park for menu Cross |
| A3 | not run (Cross advanced) | — | — |

### R2 cross-run frame identities (T33 R2 vs T32 R1, full sha256; T31 shas from T31 §T31-2)

| Frame | T33 R2 sha | T32 R1 sha | Identity |
|---|---|---|---|
| a1-poll01 = a1-pre | `d977309dd891…` (cp-identical, pair 0.0000/0) 58352 B | `6e3d747fd514…` | differ vs T32 (pair 0.0358/0 = T32-vs-T31 value); BIT-IDENTICAL to T31's frame (whole-file `cmp`, 58352 B) |
| a1-post3 | `45bcb1c63256…` 49966 B | `f1287a7be3a6…` | differ vs T32 (pair 0.0574/1); BIT-IDENTICAL to T31's frame (`cmp`, 49966 B) |
| a1-post8 | `91771d70d2bb…` 50015 B | `88ae592f89f5…` | differ vs T32 (pair 0.0567/1); BIT-IDENTICAL to T31's frame (`cmp`, 50015 B) |
| a1-post15 | `20ce007cdbfb…` | `4c56f8159c76…` | differ; pair 0.0003/0 max 4 (single-px JPEG shimmer) |
| a1-post25 | `4e4e15409746…` | `410ae0ac2c97…` | differ; pair 0.0274/0 |
| start | `2d121f1da1a1…` 58423 B | `de26d7d0ce08…` 67132 B | differ; pair 17.29/162 (attract-loop phase differs) |
| a1-now | `bf1d64ff9406…` | `713437fb5465…` | differ; pair 15.70/170 (attract phase differs) |
| menupre | differ | differ | whole pair 0.0022/0 |
| mc-post1/3/8/15 | differ | differ | whole pairs 0.143/3, 0.123/3, 0.096/3, 0.211/4 |
| scpre | differ | differ | whole pair 0.2327/5 |
| zc-post1/3/8 | differ | differ | whole pairs 0.528/13, 0.288/7, 0.292/6 (zc-post1 arrival settling) |
| ccpre | differ | differ | whole pair 0.3206/9 |
| sp-post1/3/8 | differ | differ | whole pairs 0.087/1, 0.090/1, 0.002/0 |
| sppre | differ | differ | whole pair 0.1101/1 |
| pc-post1/3/8 | differ | differ | whole pairs 0.044/0, 0.019/0, 0.046/0 (park reproduced tightly) |
| smpre vs T32 smpre | `9d3a9379ef35…` | `a72020196915…` | whole pair 0.0056/0 |
| rc-post1/3/8 vs T32 rc-post1/3/8 | differ | differ | whole pairs 0.0256/0, 0.0191/0, 0.0779/0 (rc-post8 shimmer elevated both runs — snowflake animation over SE; R2's 69867 B vs ~69433–69495 B) |
| sepre vs T32 `rc-stab6` | `b6857d04a7a7…` | `c246f4c9bf9f…` | whole pair 0.0379/0 (inside T32's own 0.0350–0.0633 SE-SE spread) |
| sepre vs R1 `rc-post8` | `b6857d04a7a7…` | `b6351798bb92…` (R1) | whole pair 0.0231/0 (park reproduced across T33 runs) |
| rc-post1 R2 vs R1 | `beb1cc74e973…` | `7330257e2626…` (R1) | whole pair 0.0048/0 max 24 |
| smpre R2 vs R1 | `9d3a9379ef35…` | `14005864526c…` (R1) | whole pair 0.0110/0 max 22 |

### R2 press log (button / hold / T+ / pre-post snaps)

| Press | Keydown → keyup (UTC wall) | Hold | T+ | Uptime | Pre-press snap | Post-press snap |
|---|---|---|---|---|---|---|
| A1 Cross (K) | 1789969481.528785498 → 1789969482.064563193 | 535.8 ms | T+97.53→98.06 | 642 | `a1-now` attract (29.1402/171 remote; 29.1646/172 PIL) | `a1-poll01` TITLE (0.4331/6; 0.0467/1) |
| A1 Start (Return) | 1789969484.803399949 → 1789969485.338602775 | 535.2 ms | T+100.80→101.34 | 645→646 | `a1-pre` ≡ `a1-poll01` (sha `d977309dd891`, TITLE, bit-identical to T31's viewed frame) | `a1-post3` Main Menu (16.2559/139; 16.2584/138) |
| MENU Cross (K) | 1789969523.915834811 → 1789969524.451952008 | 536.1 ms | T+139.92→140.45 | 684→685 | `menupre` Main Menu, Single Event highlighted (vs-menu 0.2872/5 remote; 0.0276/0 PIL; vs-title 16.2610/139) | `mc-post1` Select Character (vs-menu 10.2132/106; vs-sc 0.4951/8; titleband 12.5521/164) |
| ZOE Cross (K) | 1789969563.885028877 → 1789969564.421180451 | 536.2 ms | T+179.89→180.42 | 724→725 | `scpre` Select Character, Zoe selected (vs-sc 0.5429/8 remote; 0.1984/4 PIL; vs-menu 10.1950/105; vs-title 12.6285/164) | `zc-post1` Setup Character (vs-sc 7.2292/100; vs-zc 0.5303/9; titleband 15.9173/128) |
| CONT Cross (K) | 1789969592.651355328 → 1789969593.187037539 | 535.7 ms | T+208.65→209.19 | 753 | `ccpre` Setup Character, Zoe + Continue highlighted (vs-zc 0.4705/8 remote; 0.2355/6 PIL; vs-sc 7.2957/101; vs-title 15.8275/128) | `sp-post1` Select Peak (vs-zc 9.4662/154; vs-sp 0.3724/6; titleband 23.1287/171) |
| PEAK Cross (K) | 1789969621.366494584 → 1789969621.903054421 | 536.6 ms | T+237.37→237.90 | 782 | `sppre` Select Peak, Peak 1 highlighted (vs-sp 0.3924/6 remote; 0.0484/0 PIL; vs-zc 9.4661/154; vs-title 23.1279/171) | `pc-post1` Select Mode (vs-sp 5.3600/121; vs-sm 0.3989/6; titleband 26.3170/183) |
| RACE Cross (K) | 1789969650.706389702 → 1789969651.243497222 | 537.1 ms | T+266.71→267.24 | 811 | `smpre` Select Mode, Race highlighted (vs-sm 0.3909/6 remote; 0.0397/0 PIL; se-tag 14.3325/89 remote / 14.1480/88 PIL; vs-sp 5.3505/121; vs-title 26.3170/183) | `rc-post1` Select Event (vs-sm 0.8103/11; se-tag 2.6271/11; titleband 26.2104/183) |
| SNOWJAM Cross (K) | 1789969681.797521647 → 1789969682.333943312 | 536.4 ms | T+297.80→298.33 | 842→843 | `sepre` Select Event, Snow Jam highlighted (se-tag 2.6286/11 remote; 0.0547/2 PIL; vs-se 0.4076/6; 0.0379/0; vs-sm 0.8119/11; 0.5155/10; vs-sp 5.4516/121; 5.2879/121; vs-title 26.2104/183 — viewed) | `sj-post1` My Rules (vs-se 10.6667/143; se-tag 26.4007/92; titleband 9.8510/137 — viewed) |

Within-dwell receipts R2: Cross-keyup → Start-keydown 2.7 s; poll01 snap
exposure (05:45:24 UTC, 1 s resolution) → Start-keydown 05:45:24.803 ≤
1.0 s; R2-measured title persistence 15–17 s ⇒ press inside the window
with an order of magnitude to spare. Start-keyup → MenuCross-keydown
38.6 s; MenuCross-keyup → ZoeCross-keydown 39.4 s; ZoeCross-keyup →
ContCross-keydown 28.2 s; ContCross-keyup → PeakCross-keydown 28.2 s;
PeakCross-keyup → RaceCross-keydown 28.8 s; RaceCross-keyup →
SnowJamCross-keydown 30.6 s (no dwell pressure — all parks static, T27 G1 /
T28 G1 / T29 G1 / T30 G1 / T31 G1 / T32 G1 precedent).

### R2 screen chain (snap sha + diff scores per hop; PIL band vs title-ref / whole vs menu-ref / whole vs SC-ref / whole vs ZC-ref / whole vs SP-ref / whole vs SM-ref / whole vs SE-ref / TAG-crop vs SE-ref)

T+ = snap exposure wall (stdout `date -u`, 1 s resolution) minus T_BOOT.

| Snap (T+) | Size / sha12 | Band vs title | Whole vs menu | Whole vs SC | Whole vs ZC | Whole vs SP | Whole vs SM | Whole vs SE | SE-TAG | Content |
|---|---|---|---|---|---|---|---|---|---|---|
| start (T+96) | 58423B / `2d121f1da1a1` | 17.8510/144 | 11.8832/120 | 14.0003/154 | 12.8156/126 | 15.7976/164 | 16.1476/181 | 16.2181/182 | 91.7444/217 | Attract |
| a1-now (T+96) | 60637B / `bf1d64ff9406` | 29.1646/172 | 16.4391/155 | 15.8796/163 | 15.7174/151 | 15.4957/159 | 15.3018/164 | 15.3539/165 | 39.5976/110 | Attract |
| a1-poll01 (T+100) | 58352B / `d977309dd891` | 0.0467/1 | 14.1355/151 | 11.3102/152 | 12.2550/146 | 15.3725/156 | 16.1512/158 | 16.2492/160 | 106.6242/205 | TITLE |
| a1-pre (T+100) | 58352B / `d977309dd891` | 0.0467/1 | 14.1355/151 | 11.3102/152 | 12.2550/146 | 15.3725/156 | 16.1512/158 | 16.2492/160 | 106.6242/205 | TITLE (identical cp) |
| a1-post3 (T+104) | 49966B / `45bcb1c63256` | 16.2584/138 | 0.0647/1 | 10.1249/105 | 6.9128/93 | 10.3972/170 | 10.9266/177 | 10.9446/177 | 26.1710/106 | Main Menu |
| a1-post8 (T+110) | 50015B / `91771d70d2bb` | 16.2939/138 | 0.0628/1 | 10.1156/105 | 6.9187/93 | 10.3887/170 | 10.9184/177 | 10.9433/177 | 26.1623/106 | Main Menu |
| a1-post15 (T+117) | 49643B / `20ce007cdbfb` | 16.2622/138 | 0.0259/0 | 10.1072/105 | 6.9080/93 | 10.3854/170 | 10.9184/177 | 10.9433/177 | 26.1710/106 | Main Menu |
| a1-post25 (T+128) | 49738B / `4e4e15409746` | 16.2622/138 | 0.0408/0 | 10.1145/105 | 6.9042/92 | 10.3854/170 | 10.9186/177 | 10.9407/177 | 26.1687/106 | Main Menu |
| menupre (T+138) | 49618B / `9543989c151e` | 16.2622/138 | 0.0276/0 | 10.1076/105 | 6.9078/93 | 10.3848/170 | 10.9177/177 | 10.9427/177 | 26.1473/106 | Main Menu, Single Event highlighted |
| mc-post1 (T+141) | 70213B / `19cd910c09de` | 12.4799/163 | 10.1456/105 | 0.1479/3 | 7.1821/101 | 11.3732/158 | 11.8398/158 | 11.9106/158 | 26.5706/90 | Select Character, Zoe |
| mc-post3 (T+146) | 70579B / `140cfc1b127d` | 12.4825/163 | 10.1627/107 | 0.1432/3 | 7.2273/100 | 11.4016/158 | 11.8650/157 | 11.9348/157 | 26.5699/90 | Select Character |
| mc-post8 (T+153) | 70215B / `15a4a2e8b80f` | 12.4587/163 | 10.1417/105 | 0.2510/4 | 7.2254/100 | 11.3474/158 | 11.8157/157 | 11.8910/157 | 26.5695/90 | Select Character |
| mc-post15 (T+163) | 70048B / `d694e5328f00` | 12.4587/163 | 10.1290/105 | 0.0027/0 | 7.2299/100 | 11.3506/158 | 11.8131/157 | 11.8815/157 | 26.6037/90 | Select Character |
| scpre (T+177) | 70188B / `3d01f9b9eb1c` | 12.5525/163 | 10.1270/105 | 0.1984/4 | 7.2007/100 | 11.3583/158 | 11.8320/157 | 11.9025/157 | 26.5695/90 | Select Character, Zoe selected |
| zc-post1 (T+181) | 51477B / `adc1b2a6af51` | 15.8935/129 | 6.9235/93 | 7.2011/100 | 0.2983/8 | 9.3647/153 | 10.1369/164 | 10.2489/164 | 15.2985/91 | Setup Character, Zoe |
| zc-post3 (T+186) | 51550B / `2f6abdc4b8cb` | 15.8394/128 | 6.9121/92 | 7.2677/101 | 0.2330/6 | 9.3483/153 | 10.1096/165 | 10.2226/165 | 15.2988/91 | Setup Character |
| zc-post8 (T+193) | 51428B / `ed353c11d835` | 15.8302/128 | 6.9302/93 | 7.1078/100 | 0.2275/5 | 9.3800/153 | 10.1316/164 | 10.2290/164 | 15.2961/91 | Setup Character |
| ccpre (T+206) | 51607B / `467d3ec7c690` | 15.8056/128 | 6.9119/92 | 7.2698/101 | 0.2355/6 | 9.3493/153 | 10.1135/165 | 10.2267/165 | 15.3324/91 | Setup Character, Zoe + Continue |
| sp-post1 (T+210) | 65369B / `783c5e396e0b` | 23.1266/171 | 10.4250/170 | 11.3570/158 | 9.3866/153 | 0.0266/0 | 5.2281/121 | 5.3310/121 | 14.0042/89 | Select Peak, Peak 1 |
| sp-post3 (T+214) | 65492B / `1f9529b76800` | 23.1259/171 | 10.4304/170 | 11.3668/158 | 9.3918/153 | 0.0378/0 | 5.2373/121 | 5.3385/121 | 14.0026/89 | Select Peak |
| sp-post8 (T+222) | 65237B / `7d667a57a78b` | 23.1273/171 | 10.4059/170 | 11.3503/158 | 9.3727/153 | 0.0048/0 | 5.2072/121 | 5.3100/121 | 14.0026/89 | Select Peak |
| sppre (T+234) | 65468B / `ccad28974c5a` | 23.1259/171 | 10.4383/170 | 11.3792/158 | 9.3853/153 | 0.0484/0 | 5.2492/121 | 5.3373/121 | 14.0026/89 | Select Peak, Peak 1 highlighted |
| pc-post1 (T+238) | 67467B / `61ba05253356` | 26.3046/183 | 10.9216/178 | 11.8103/157 | 10.1030/164 | 5.1925/121 | 0.0492/0 | 0.5225/10 | 14.1392/88 | Select Mode, Race |
| pc-post3 (T+243) | 67385B / `ad4a9232ac4f` | 26.3046/183 | 10.9137/178 | 11.8035/157 | 10.1002/164 | 5.1810/121 | 0.0397/0 | 0.5111/9 | 14.1443/88 | Select Mode |
| pc-post8 (T+251) | 67540B / `ec9bce5777bb` | 26.2941/183 | 10.9331/178 | 11.8036/157 | 10.1131/164 | 5.2004/121 | 0.0606/1 | 0.5317/11 | 14.1512/88 | Select Mode |
| smpre (T+263) | 67409B / `9d3a9379ef35` | 26.3046/183 | 10.9141/178 | 11.8034/157 | 10.1009/164 | 5.1811/121 | 0.0397/0 | 0.5111/9 | 14.1480/88 | Select Mode, Race highlighted |
| rc-post1 (T+268) | 69493B / `beb1cc74e973` | 26.1964/183 | 10.9417/178 | 11.8619/157 | 10.2199/164 | 5.2861/121 | 0.5136/10 | 0.0354/0 | 0.0094/0 | Select Event, Snow Jam |
| rc-post3 (T+272) | 69433B / `53292fe1285e` | 26.1975/183 | 10.9384/178 | 11.8586/157 | 10.2160/164 | 5.2823/121 | 0.5092/9 | 0.0319/0 | 0.0094/0 | Select Event |
| rc-post8 (T+279) | 69867B / `edba54df5821` | 26.1964/183 | 10.9945/178 | 11.9102/157 | 10.2647/164 | 5.3441/121 | 0.5731/13 | 0.0665/0 | 0.0094/0 | Select Event |
| sepre (T+293, pre-SnowJamCross) | 69495B / `b6857d04a7a7` | 26.1964/183 | 10.9433/178 | 11.8633/157 | 10.2203/164 | 5.2879/121 | 0.5155/10 | 0.0379/0 | 0.0547/2 | Select Event, Snow Jam highlighted (viewed) |
| sj-post1 (T+299) | 58981B / `b6d6f28c421d` | 9.8270/135 | 10.1134/96 | 5.6466/117 | 7.0851/104 | 9.8534/137 | 10.4604/143 | 10.6243/143 | 26.4126/92 | My Rules, Continue (viewed) |
| sj-post3 (T+303) | 58481B / `159f88582037` | 9.8145/135 | 10.0796/96 | 5.6086/117 | 7.0490/104 | 9.8169/137 | 10.4260/143 | 10.5899/143 | 26.4148/92 | My Rules |
| sj-post8 (T+310) | 58731B / `0692f7682731` | 9.8242/135 | 10.0895/97 | 5.6253/117 | 7.0692/104 | 9.8443/137 | 10.4449/143 | 10.6082/143 | 26.4126/92 | My Rules |
| sj-post15 (T+320) | 59271B / `b6f51bbcb89f` | 9.8182/135 | 10.1443/97 | 5.6872/117 | 7.0980/104 | 9.8884/137 | 10.4969/143 | 10.6588/143 | 26.4126/92 | My Rules |
| sj-post25 (T+332) | 59175B / `f258398dae41` | 9.9043/135 | 10.1062/96 | 5.6204/117 | 7.0852/104 | 9.8457/139 | 10.4659/144 | 10.6304/144 | 26.4126/92 | My Rules |
| sj-post40 (T+349) | 58789B / `611ec41559b5` | 9.8218/135 | 10.0784/96 | 5.6425/117 | 7.0820/104 | 9.8189/137 | 10.4188/143 | 10.5827/143 | 26.4126/92 | My Rules |
| sj-stab1 (T+371) | 58834B / `adedb5b0eb9b` | 9.8877/137 | 10.1047/98 | 5.6410/117 | 7.0838/104 | 9.8596/137 | 10.4642/143 | 10.6273/143 | 26.4126/92 | My Rules |
| sj-stab2 (T+382) | 59127B / `a8bff106d3c1` | 9.9087/135 | 10.1219/97 | 5.6514/117 | 7.0873/104 | 9.8768/137 | 10.4925/143 | 10.6565/144 | 26.4126/92 | My Rules |
| sj-stab3 (T+393) | 58514B / `2ea8f2ac2f1b` | 9.8145/135 | 10.0789/96 | 5.6082/117 | 7.0492/104 | 9.8161/137 | 10.4252/143 | 10.5892/143 | 26.4126/92 | My Rules |
| sj-stab4 (T+405) | 59410B / `253572b9934e` | 9.8118/135 | 10.0918/97 | 5.6711/117 | 7.0614/104 | 9.8678/138 | 10.4743/143 | 10.6375/143 | 26.4126/92 | My Rules |
| sj-stab5 (T+416) | 59075B / `e93ac17e4834` | 9.8810/135 | 10.1244/99 | 5.6665/118 | 7.1026/105 | 9.8831/137 | 10.4832/143 | 10.6522/143 | 26.4529/93 | My Rules |
| sj-stab6 (T+427) | 59055B / `df39d72548a3` | 9.9185/135 | 10.0984/96 | 5.6137/117 | 7.0793/104 | 9.8374/138 | 10.4490/143 | 10.6130/144 | 26.4126/92 | My Rules, Continue (viewed) |

In-script (remote) vs PIL agreement: ≤0.17 mean on menu/title-band/
vs-sp/vs-sm/vs-se scores at scale (e.g. sepre band 26.2104 vs 26.1964;
sj-post1 vs-se 10.6667 vs 10.6243 with p99 143/143; sj-post1 se-tag
26.4007 vs 26.4126); the known ~6–11× remote-lossless gap on near-zero
whole means (poll01 band 0.4331/6 remote vs 0.0467/1 PIL; sepre vs-se
0.4076/6 vs 0.0379/0 — T27 title / T28 menu / T29 SC / T30 ZC / T31 SP /
T32 SM precedent); hops ≤0.03. The TAG crop is the exception: ~260–280×
on near-zero TAG means (se-tag 2.6271/11 remote vs 0.0094/0 PIL — JPEG
ringing in the ref around glyph edges), while large TAG means agree
(smpre se-tag 14.3325/89 remote vs 14.1480/88 PIL).

### R2 transition hops (whole-frame, per hop)

| Hop | Remote (in-script) | PIL | Reading |
|---|---|---|---|
| menupre → mc-post1 | 10.1179 | 10.1252/105 | screen change within +1 s |
| post1 → post3 (mc) | 0.1345 | 0.1622/4 | arrival settling/shimmer |
| post3 → post8 (mc) | 0.2666 | 0.2907/7 | same screen |
| post8 → post15 (mc) | 0.2320 | 0.2526/4 | same screen |
| post15 → scpre (park span) | — | 0.2000/4 | same screen |
| scpre → zc-post1 | 7.2036 | 7.2281/100 | screen change within +1 s |
| post1 → post3 (zc) | 0.3057 | 0.3285/9 | arrival settling |
| post3 → post8 (zc) | 0.2891 | 0.3109/7 | same screen |
| post8 → ccpre (park span) | — | 0.3225/8 | same screen |
| ccpre → sp-post1 | 9.3207 | 9.3582/153 | screen change within +1 s |
| post1 → post3 (sp) | 0.0483 | 0.0569/1 | arrival settling/shimmer |
| post3 → post8 (sp) | 0.0290 | 0.0349/0 | same screen |
| post8 → sppre (park span) | — | 0.0460/0 | same screen |
| sppre → pc-post1 | 5.2056 | 5.2317/121 | screen change within +1 s |
| post1 → post3 (pc) | 0.0190 | 0.0213/0 | arrival settling/shimmer |
| post3 → post8 (pc) | 0.0269 | 0.0305/0 | same screen |
| post8 → smpre (park span) | — | 0.0305/0 | same screen |
| smpre → rc-post1 | 0.4588 | 0.4844/7 | screen change within +1 s (Select Mode → Select Event; small whole-frame distance — shared background; content read off viewed snaps) |
| post1 → post3 (rc) | 0.0042 | 0.0048/0 | arrival settling/shimmer |
| post3 → post8 (rc) | 0.0615 | 0.0660/0 | same screen (rc-post8 snowflake shimmer; still SE: se-tag 0.0094) |
| post8 → sepre (park span) | — | 0.0720/0 | same screen |
| sepre → sj-post1 | 10.5818 | 10.6053/143 | screen change within +1 s (Select Event → My Rules; decisive hop) |
| post1 → post3 (sj) | 0.0542 | 0.0564/0 | arrival settling/shimmer |
| post3 → post8 (sj) | 0.0475 | 0.0561/0 | same screen |
| post8 → post15 (sj) | 0.1338 | 0.1467/2 | same screen (snowflake drift) |
| post15 → post25 (sj) | 0.1682 | 0.1790/3 | same screen (snowflake drift) |
| post25 → post40 (sj) | 0.1217 | 0.1304/1 | same screen (snowflake drift) |
| post40 → stab1 (sj) | — | 0.1145/1 | same screen |
| stab1 → stab6 (sj) | — | 0.1346/2 | same screen |
| post1 → stab6 (sj span) | — | 0.1206/1 | arrival endpoints same screen |

### R2 arrival (My Rules)

| Item | Value |
|---|---|
| Arrival snap | `t33r2-sj-post1.jpg` @T+299 (+1 s after SnowJam Cross keyup; no intermediate screen captured at +1 s cadence) |
| Stability N | 12 snaps (post1/3/8/15/25/40 + stab1–6) spanning T+299→T+427 (128 s) |
| Whole-frame pairwise (PIL) | 0.0132–0.2012/p99 ≤3 across all 66 pairs (snowflake-drift shimmer; JPEG shas distinct) |
| Vs-SE (whole) | 10.58–10.66/p99 143–144 across all 12 (not Select Event) |
| Vs-SM (whole) | 10.42–10.50/p99 143–144 across all 12 (not Select Mode) |
| Vs-SP (whole) | 9.82–9.89/p99 137–139 across all 12 (not Select Peak) |
| Vs-ZC (whole) | 7.05–7.10/p99 104–105 across all 12 (not Setup Character) |
| Vs-menu (whole) | 10.08–10.14/p99 96–99 across all 12 (not menu) |
| Vs-SC (whole) | 5.61–5.69/p99 117–118 across all 12 (not Select Character; nearest prior screen — T34 gate note) |
| Vs-title (band) | 9.81–9.93/p99 135–137 across all 12 (not title) |
| SE-TAG (crop) | 26.41–26.45/p99 92–93 across all 12 (tagline band fully changed) |
| What is highlighted/selected | "My Rules" header; `Continue` (highlighted, orange bar) / `Super AI` / `AI Headstart` / `Start with full boost` / `Unlimited boost` / `No boost` / `KO boost only` / `No uber tricks` / `No uber rails` / `No knockdowns` / `Leaky adrenaline` (all Off); footer `Accept current rules and enter game.`, `× Enter game`, `△ Previous`, `○ Options` |
| Reclaim after arrival? | none observed in 128 s (all 12 snaps My Rules) |

### R2 SE-park gate legs (in-script, remote)

| Gate leg | Value | Bar | Pass? |
|---|---|---|---|
| Arrival static p1→p3 | 0.0042 | < 1.0 | yes |
| Arrival static p3→p8 | 0.0615 | < 1.0 | yes |
| Non-SP (post8 vs-sp) | 5.5028/121 | > 5.0 | yes |
| SE-TAG (post8 TAG-crop-vs-SE) | 2.6271/11 | < 5.0 (R2 bar) | yes → `SE-LIKE`, SnowJam Cross pressed |
| SM-side receipt (smpre se-tag) | 14.3325/89 | ≫ 5.0 | yes (2.9× margin; PIL 14.1480/88) |

### R2 success bars (tabled, not verdicts)

| Bar | Receipt |
|---|---|
| Arrival park reproduced (snap match vs T32's `t32r1-rc-stab6.jpg`) | rc-post1/3 + sepre whole-vs-stab6 0.0319–0.0379/p99 0–2 (all under the 0.2 gate; inside T32's own 0.0350–0.0633 spread modulo post1/sepre a hair below its min — same class); rc-post8 0.0665/0 (snowflake shimmer, still far under 0.2); 4 chain frames bit-identical to T31's run |
| Cross acted on it (pre-press = Select Event, Snow Jam highlighted) | `sepre` se-tag 2.6286/11 remote, 0.0547/2 PIL; vs-se 0.4076/6 remote, 0.0379/0 PIL; viewed: Select Event, Snow Jam highlighted (orange bar), Metro-City/Happiness, Race course-map panel, tagline `Snow Jam is an exciting BEGINNER track with heavy forests and patches of fog.` |
| Next-screen snaps + stability N | 12 snaps over 128 s, pairwise 0.013–0.201/p99 ≤3, endpoints 0.1206/1 |
| Full input log + trace sha | `t33r2-poll.log` (113 lines: every score + press, walls + uptimes) + trace `757497b8…43af3d` |

Guest/trace side (R2): boot prefix line-identical to T25/T27/T28/T29/T30/
T31/T32 (BIOS L2, ExecPS2 L142330/142426, ReBootStart L142725, first vblank
L417043, first UpdateVSyncRate L456189); ×15 modes; vblanks 397 frozen
(all ≤90); LoadStartModule 18; ERROR 0; `NVRAM has not changed`; clean
tail @428.0992. Census: EE 5,751,570 (52, set-identical to T32 R1) · IOP
18,653,793 (155, set-identical to T32 R1 — My Rules arrival adds no new
called API) · `libsd.006: sceSdGetParam` 1652 (R1-T32: 1426);
`sceSdGetAddr` 3,728,400 (R1-T32: 3,468,480).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Park reproduced? | YES (R1 A1 and R2 A1: TITLE at poll01 → Start → menu-like gate → Menu Cross → SC-LIKE gate → Zoe Cross → ZC-LIKE gate → Continue Cross → SP-LIKE gate → Peak Cross → SM-LIKE gate → Race Cross → SE-LIKE gate in R2) |
| Cross on Snow Jam? | YES (SNOWJAM Cross @T+297.80 R2, pre-press = Select Event, Snow Jam highlighted) |
| Next screen reached? | YES (My Rules @T+299, stable 128 s) |
| Bounded variant? | R2 (recalibrated se-tag bar 2.0→5.0 after R1's gate misfire on a proven-true park); no press-variant needed (first SnowJam press provably acted on the Select Event park) |
| 1200 s cap | Not reached — R1 ≈ T+300, R2 ≈ T+440; attempt 3 unexercised |
| Chain end | My Rules, Continue highlighted, awaiting input |

## T33-3. Traces (bytes + sha, SSD paths, slices)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t33 R2 (Cross + Start-on-title → menu → Cross → Select Character → Cross → Setup Character → Cross → Select Peak → Cross → Select Mode → Cross → Select Event → Cross → My Rules, T+~440) | 36,351,245 / 2,403,143,826 | `757497b860cd8100ec9452bb4371b0a67902b9770544ad3eee2867004743af3d` (analyze-sha on H8 = post-restart re-verify on H9 = SSD-sha; match) | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t33r2.txt`, same size+sha (match) + committed head/tail 2000+2000 (`t33r2-trace-head.txt` 149019 B sha `9baf9ac8d466…`, `t33r2-trace-tail.txt` 134261 B sha `6969f5eaef0b…`) |
| `emulog-pre-t33-20260921T054304Z.txt` = t33 R1 (preserved at R2 boot) | — / 1,706,068,225 | `1915aaf93fe11b5db9c2b661665e991aef9304513b069af6fe23d4c7eb5fd6dc` (re-verified post-run: matches R1 live-sha) | bytesize-only (T32 precedent) |
| `emulog-pre-t33-20260921T053433Z.txt` = t32 R1 (preserved at R1 boot) | — / 2,259,205,200 | `7f14d876145e…777af9cc3c` (re-verified post-run: matches T32) | bytesize-only (T32 precedent; SSD holds T32's own copy) |

Channel census (T4 `t4-census.py`, same script): R2 EE 5,751,570 (52
distinct, set-identical to T32 R1) · IOP 18,653,793 (155, set-identical
to T32 R1) · vblanks 397. Committed: `t33r2-census.txt` (11695 B sha
`17831139ceb5…`), `t33r2-samples.txt` (5875 B sha `3022d3afc957…`),
`t33r1-poll.log` (91 lines, 5297 B sha `d94986e9cd88…`),
`t33r2-poll.log` (113 lines, 6845 B sha `5943859c43d8…`),
`t33r1-stdout.txt` (237 lines, 15045 B),
`t33r1-stderr.txt` (full `set -x` shell trace, 1390 lines, 72518 B),
`t33r2-stdout.txt` (312 lines, 20254 B),
`t33r2-stderr.txt` (full `set -x` shell trace, 1797 lines, 97823 B),
`t33r2-trace-head.txt` / `t33r2-trace-tail.txt`.

## T33-4. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — NO pipes inline (piped logic in staged scripts
or filtered locally); `;`-chaining works INSIDE one `wsl` call only;
one `wsl` call per ssh):

```
# reuse verification (pipe-free; ;-chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H7 …8599
ssh bytesize 'wsl dmesg' > /tmp/t33-dmesg-pre.txt                     # 417 lines, 0 kills (H7)
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t33-eventlog-pre.txt  # head 01:29:59
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C …/pcsx2 rev-parse HEAD; git -C …/pcsx2 status --short'  # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl sha256sum …/bios/….nvm; grep -n Cross …/inis/PCSX2.ini'  # da021d2a… / :579 K
ssh bytesize 'wsl sha256sum …t27-ref-title.ppm …t28-ref-menu.ppm …t29-ref-sc.ppm …t30-ref-zc.ppm …t31-ref-sp.ppm …t32-ref-sm.ppm; df -h / /tmp; df -h /mnt/c; du -sh …/logs/; ls …/logs/'  # all 6 refs + 894G / C: 24G / 20G
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …/logs/emulog.txt'  # 7f14d876… T32R1 live
# T32 ref snaps (local): 12/12 full-sha256+sizes reproduce T32 §T32-2
# SE ref + calibration (local; t33-cropdiff.py = T32 copy, byte-identical)
python3 -c "Image.open(rc-stab6).convert('RGB').save('/tmp/t33-ref-se.ppm')"  # ref 3932177 B 4baec4bc…
python3 /tmp/t33-fastdiff.py <valid 4/4 exact vs t33-cropdiff.py>
python3 /tmp/t33-fastdiff.py <12 SE + 4 SM + 4 SP + 4 ZC + 5 SC + 5 menu + 2 title + 2 attract> vs SE-ref × {WHOLE, TAG 40,415,330,450, LIST 110,195,270,270, HDR 40,60,280,110, PTITLE 310,110,410,135}
# -> WHOLE SE-SE <=0.0633, SM 0.5071-0.5333; TAG SE-SE <=0.1401, SM 14.1390; LIST SE-SE <=0.1488, SM 21.74; PTITLE SE-SE 0.0, SM 16.14; HDR REJECTED (SE-SE to 3.55 overlaps SP)
# adapt t33-auto.sh from the T32 copy (SE gate + SNOWJAM_CROSS + sj arrival; bash -n), t33-analyze.sh names
# staging (T25 recipe: scp to C: then wsl cp)
scp t33-auto.sh t33-analyze.sh t33-vcount.sh t33-cropdiff.py /tmp/t33-ref-se.ppm "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t33-… /home/brad/pcsx2-t4/; sha256sum …'  # 4baec4bc…
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls …'  # on VM-H7 (wiped by H7→H8 restart; R1/R2 unaffected)
ssh bytesize 'wsl python3 …/t33-cropdiff.py …REFSE …; …REFSE …TAG; …REFSM …'  # 0.0000/0 ×3 PPM
# R1 (ONE ssh; exit 0; chain → NO-SE-PARK on true SE park, gate bar 2.0 vs remote 2.6271)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t33-auto.sh' > /tmp/t33r1-run-stdout.txt 2>/tmp/t33r1-run-stderr.txt  # T33_DONE, up 28→331
ssh bytesize 'wsl cp <29 jpg + poll.log> /mnt/c/…'   # (explicit list, one wsl call)
scp "bytesize:pcsx2-t4/t33-…" /tmp/t33-fetch/                         # 29 jpg + log (r1-prefixed local)
# R1 post-hoc (local fastdiff): park IS SE (whole-vs-se <=0.049, TAG <=0.012, viewed rc-post8); remote TAG gap ~270x
ssh bytesize 'wsl dmesg' > /tmp/t33-dmesg-mid.txt                    # 482 lines, 2 kills (both post-R1, H8)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H8 …8839 (H7→H8 restart mid-session)
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la …/logs/emulog.txt'  # 1915aaf9… R1 live
# R2 script: SETAG 2.0→5.0 + SMPRE se-tag line (4-line diff; bash -n); stage t33-auto.sh only; grep-verify 5.0 remote
scp /tmp/t33-auto.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t33-auto.sh /home/brad/pcsx2-t4/t33-auto.sh; grep -n SETAG_MEAN_MAX …'
# R2 (ONE ssh; exit 0; SE-LIKE → SNOWJAM Cross → My Rules)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t33-auto.sh' > /tmp/t33r2-run-stdout.txt 2>/tmp/t33r2-run-stderr.txt  # T33_DONE, up 539→983
ssh bytesize 'wsl bash …/t33-analyze.sh'                              # 757497b8…, 36351245 L
ssh bytesize 'wsl bash …/t33-vcount.sh'                                # 397 frozen (all ≤90)
ssh bytesize 'wsl grep -c LoadStartModule …; grep NVRAM …'             # 18; has not changed
ssh bytesize 'wsl cp <30 jpg + poll.log + census/samples> /mnt/c/…'   # (explicit lists, one wsl call each)
ssh bytesize 'wsl cp <12 sj jpg> /mnt/c/…; wc -l …/t33-poll.log'       # 113-line log
scp "bytesize:pcsx2-t4/t33-…" /tmp/t33-fetch/                         # 42 jpg + logs (r2-prefixed local)
# R2 post-hoc (local fastdiff): chain scores, xrun pairs, 66 arrival pairs, census set-compare
ssh bytesize 'wsl dmesg' > /tmp/t33-dmesg-post.txt                    # 416 lines, 0 kills (VM-H9 — restarted post-everything)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # VM-H9 …0071
ssh bytesize 'wevtutil …' > /tmp/t33-eventlog-post.txt                # head H9-create 01:54:31; H7→H8 01:32:15/01:33:59, H8→H9 01:54:05/01:54:31; no in-window entries
ssh bytesize 'wsl sha256sum …/bios/….nvm; ls -la …/bios/; sha256sum …/logs/emulog.txt; ls -la …/logs/; df -h / /mnt/c'  # da021d2a… untouched; 757497b8… re-verified; 21 emulogs; C: 23G
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t33-20260921T054304Z.txt …/logs/emulog-pre-t33-20260921T053433Z.txt'  # 1915aaf9… R1 + 7f14d876… T32R1 preserved
ssh bytesize 'wsl head -n 2000 <trace>' > t33r2-trace-head.txt         # 2000 lines
ssh bytesize 'wsl tail -n 2000 <trace>' > t33r2-trace-tail.txt         # 2000 lines, clean tail @428.0992
# SSD copy (COPYFILE_DISABLE=1; wsl cp to staging, then scp, then shasum re-verify)
ssh bytesize 'wsl cp <trace> /mnt/c/Users/bradr/pcsx2-t4/emulog-t33r2.txt; ls -la …'
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t33r2.txt" "/Volumes/Extreme SSD/ps2x-t4/"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t33r2.txt"         # 757497b8… match
# report (chunks; receipts include tail -3)
cp /tmp/t33-dmesg-*.txt /tmp/t33-eventlog-*.txt /tmp/t33r1-run-stdout.txt … local/research/T33/  # renamed per §evidence
tail -3 local/research/T33/REPORT.md
git add -f local/research/T33/<92 files by name>                      # ignored dir, forced
git commit -m "[T33] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T33-5. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (My Rules park) | Reproduce the R2 chain (fresh boot → Cross → detector-TITLE → Start → menu-like gate → Cross on Single Event → SC-LIKE gate → Cross on Zoe → ZC-LIKE gate → Cross on Continue → SP-LIKE gate → Cross on Peak 1 → SM-LIKE gate → Cross on Race → SE-LIKE gate (static + non-SP + se-tag<5.0 remote) → ≤3 attempts) → My Rules with Continue highlighted; then a single 534 ms Cross (× Enter game, footer `Accept current rules and enter game.`) to accept the rules, screenshot-verify the next screen. Gate note: the SE→MR whole-frame hop is decisive (~10.58–10.61 remote/PIL), so DEPARTED > 5.0 fires normally here; a My Rules ref (from `t33r2-sj-stab6.jpg`, PIL `convert('RGB').save` recipe) plus the standard < 2.0-style whole bar should work — nearest prior screen is SC at ~5.61–5.69 (whole, PIL), so margins resemble the early submenu gates; the arrival shimmers (pairwise ≤0.201/p99 ≤3 from snowflake drift — wider than SE's ≤0.064, still far under 2.0). Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The arrival screen is static (128 s, no reclaim) so no dwell pressure on arrival→next presses |
| G2 | WSL killer continues + 2 mid-session restarts (H7→H8 pre-R1, H8→H9 post-everything, not by me) | 2 userland `AcceptAsync` kills on VM-H8, both post-R1 ([346.39] during R1-fetch staging, [416.67] during mid-dmesg read; each ssh still exit 0, artifacts sha-valid after) + 1 mid-session VM restart between staging and R1 (H7 05:29:59→05:32:15, H8 create 05:33:59; 104 s gap; every ssh exit 0 across it; staged files persist on the same VHD) + 1 mid-session VM restart post-everything (H8→H9 05:54:05–05:54:31; only post reads ran on H9) + 2 pre-session VM restarts between T32 and T33 (H6→short-lived→H7; T32: 7 flaps + 2 pre-session restarts). R1 completed exit 0 with zero in-window flaps on the dmesg record (no T27 §4 effects-verification needed); R2 completed exit 0 but its window has NO dmesg coverage (H8 destroyed before a post-R2 dmesg read — my sequencing put analyze+fetches before the post dmesg; a dmesg read immediately after the R2 ssh returned would have captured it) so R2 stands effects-verified (exit 0, `T33_DONE`, clean shutdown + clean trace tail, complete coherent artifacts, zero VM boundaries in-window per eventlog). Precautions stand. No toolchain switch made (brief forbids mid-brief); T27's Windows-native-Devel recommendation stays tabled |
| G3 | Windows event log: zero flap entries; boundaries bound both restarts | Newest-30 reads (pre/post): H7 create 01:29:59 → H7 teardown 01:32:15 → H8 create 01:33:59 → H8 teardown 01:54:05 → H9 create 01:54:31; zero entries at either flap time and zero boundaries inside either run window (precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on VM-H7 btime |
| G4 | Hold count 60/60 | 534 ms-class holds register 60/60 across T17c+T19+T21+T23+T25+T27+T28+T29+T30+T31+T32+T33 (T33 R1: 535.4/536.7/537.5/537.2/538.5/535.6/535.1 ms; T33 R2: 535.8/535.2/536.1/536.2/535.7/536.6/537.1/536.4 ms). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Title/menu/SC/ZC/SP/SM/SE frozenness; attract differs; snowflake shimmer on SE + MR | Title text-band frozen across showings (0.0468/1 R1, 0.0467/1 R2); R1's 4 frames bit-identical to T32's run (a1-poll01/pre, a1-post15/25 — the attract/title/menu timing lottery landed back on T32's=T30's phase) and R2's 4 frames bit-identical to T31's run (a1-poll01/pre, a1-post3/8 — landed on T31's phase); a1-post15 xrun 0.0003–0.0004/0 max 4–7 again (single-px JPEG shimmer); menu whole-frame ≤0.082/p99 ≤1 cross-run; SC cross-run 0.10–0.26/p99 3–5; ZC cross-run 0.18–0.53/p99 4–13 (zc-post1 settling, 0.52–0.53 in-run hop); SP cross-run ≤0.14/p99 ≤1; SM cross-run 0.02–0.07/p99 0–1; Select Event ≤0.078/p99 0 cross-run over both T33 runs (rc-post8 elevated by snowflake animation — R1 0.0338, R2 0.0660 in-run p3→p8 hops); My Rules ≤0.201/p99 ≤3 over 128 s (snowflake drift — widest arrival spread to date, still far under any gate). Whole-sha equality usable only where frozenness is proven per-screen, never assumed (T23 rule stands) |
| G6 | Vblank freeze persists into the sixth-submenu run | `WaitVblankStart` stops after log ≤90 in T33 R2 including My Rules arrival (397 total — counts, `LoadStartModule` 18, and EE/IOP name sets all T32-R1-identical modulo counts). The attract/title/menu/submenu sync mechanism still unmapped (T25 G6 stands) |
| G7 | Submenu guest-side correlate: none (sets identical) | Like prior arrivals, My Rules arrival adds NO new called API: EE 52/52 and IOP 155/155 sets identical to T32 R1; only counts grow (`sceSdGetParam` 1426→1652, `sceSdGetAddr` 3.47M→3.73M). A rerun with `EnableEEConsole/EnableIOPConsole=true` (T25 G8, still off) would add game-side strings around the transition |
| G8 | Logs-dir growth + SSD receipts | `…/logs/` now holds ~24 GB across 21 emulogs (T17→T33 chain, all preserved); C: 23 G avail (pre 24 G — run staging + traces; T32 pre was 26 G). T33 R2 full trace SSD-copied + sha-verified (2.40 GB: `emulog-t33r2.txt`); committed slices only (2 × 2000-line head/tail). R1 trace (1.71 GB) bytesize-only |
| G9 | Brief-name check: all real | The T33 brief cites `t32r1-rc-post{1,3,8,15,25,40}.jpg` + `t32r1-rc-stab{1…6}.jpg` — all 12 exist with full shas+sizes reproducing T32 §T32-2; the PIL `convert('RGB').save` ref recipe reproduces byte-exactly (PPM-vs-JPEG 0.0000/0). T28 G9 lesson holds |
| G10 | Session wall + run durations | ~95 min active of the 4 h box (two runs + report/commit); zero lease waits (no lease exists for T33). R1 wall 303 s; R2 wall 444 s — 84 s over the ≤6 min guidance (added SE-phase scoring + arrival tail); R1 full dmesg coverage, R2 effects-verified (G2) |
| G11 | X11 mount landed on the wrong generation again; two operator pipe typos | The `/tmp/.X11-unix` tmpfs mount ran on VM-H7 and was wiped by the H7→H8 restart, yet R1+R2 both started Xvfb :99 cleanly on H8 regardless (exit 0 + 29/42 snaps) — the mount is belt-and-braces, not load-bearing, on current WSL (T32 G11 stands). Two remote calls failed first try with pipes outside the `wsl` call (`head`/`wc` reaching Windows cmd); both retried pipe-free per the T32 recipe. No run impact either way |
| G12 | Remote-vs-PIL gap is crop-dependent: calibrate text-dense crops remotely or bar generously | New this brief: the TAG text crop inflated ~260–280× remote-vs-PIL (2.6271 vs ~0.010) while whole-frame on the same snaps inflated only ~9× — JPEG ringing in the JPEG-derived ref concentrates around glyph edges. PIL-domain bars on text-dense crops need either a remote receipt (score a staged candidate… currently impossible without PIL on WSL — a chicken-and-egg for pre-run calibration) or a generous bar with a measured-remote first run (this brief's R1→R2 path). Large means agree across modes in both domains (≤1.03× at scale ≥5, ≤1.6× at scale ~0.5–0.8), so the safe pattern is: discriminating crop + bar between the remote-measured true-side value and the far non-side cluster, with the first run doubling as the remote calibration |

## Evidence files

`REPORT.md` (this file),
scripts: `t33-auto.sh` (R2 gate), `t33-auto-r1.sh` (R1 gate),
`t33-cropdiff.py` (T32 logic, byte-identical),
`t33-analyze.sh`, `t33-vcount.sh` (byte-identical);
R1: `t33r1-start.jpg`, `t33r1-a1-now.jpg`, `t33r1-a1-poll01.jpg`,
`t33r1-a1-pre.jpg`, `t33r1-a1-post{3,8,15,25}.jpg`, `t33r1-menupre.jpg`,
`t33r1-mc-post{1,3,8,15}.jpg`, `t33r1-scpre.jpg`,
`t33r1-zc-post{1,3,8}.jpg`, `t33r1-ccpre.jpg`,
`t33r1-sp-post{1,3,8}.jpg`, `t33r1-sppre.jpg`,
`t33r1-pc-post{1,3,8}.jpg`, `t33r1-smpre.jpg`,
`t33r1-rc-post{1,3,8}.jpg` (29 snaps),
`t33r1-poll.log`, `t33r1-stdout.txt`, `t33r1-stderr.txt`;
R2: `t33r2-start.jpg`, `t33r2-a1-now.jpg`, `t33r2-a1-poll01.jpg`,
`t33r2-a1-pre.jpg`, `t33r2-a1-post{3,8,15,25}.jpg`, `t33r2-menupre.jpg`,
`t33r2-mc-post{1,3,8,15}.jpg`, `t33r2-scpre.jpg`,
`t33r2-zc-post{1,3,8}.jpg`, `t33r2-ccpre.jpg`,
`t33r2-sp-post{1,3,8}.jpg`, `t33r2-sppre.jpg`,
`t33r2-pc-post{1,3,8}.jpg`, `t33r2-smpre.jpg`,
`t33r2-rc-post{1,3,8}.jpg`, `t33r2-sepre.jpg`,
`t33r2-sj-post{1,3,8,15,25,40}.jpg`, `t33r2-sj-stab{1…6}.jpg` (42 snaps),
`t33r2-census.txt`, `t33r2-samples.txt`, `t33r2-poll.log`,
`t33r2-stdout.txt`, `t33r2-stderr.txt`, `t33r2-trace-head.txt` / `t33r2-trace-tail.txt`;
flaps: `t33-dmesg-vmH7-pre.txt` (0 kills on H7, pre-run) /
`t33-dmesg-vmH8-mid.txt` (2 kills on H8, both post-R1; full R1-window
coverage) / `t33-dmesg-vmH9-post.txt` (0 kills on H9, fresh boot),
`t33-eventlog-pre.txt` / `t33-eventlog-post.txt`.
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t33r2.txt`
(2,403,143,826 B `757497b8…`, sha-verified, NOT in git) + bytesize
original `…/logs/emulog.txt` (same) with preserved T33 R1
`…-20260921T054304Z.txt` `1915aaf9…` and T32 R1
`…-20260921T053433Z.txt` `7f14d876…`.
