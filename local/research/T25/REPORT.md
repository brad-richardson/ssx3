# T25 report — NVM-verify + scripted path: settings skip to attract, title reached 3× (bytesize, no lease)

Brief `local/muse/prompts/T25.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
6 h; session wall ~20:14–20:37 UTC 2026-09-20 (~23 min + report/commit).

Stale-reading guard: `local/research/T23/REPORT.md` (all: STATIC
Settings-completed park, 6/6 snaps sha-identical, `NVRAM saved` marker —
the premise of Part 4 decision 7), `local/research/T23/t23-post*.jpg`
(the completed park, sha `37c57308…`, re-verified at session start),
T23 gaps G2–G5 (WSL precautions: single-shot scripts, runs ≤6 min,
preserve emulogs first, re-check dmesg + btime + init age; UNFILTERED
`dmesg` + Windows event log around any flap; 534 ms holds, 10/10
reliable — do NOT bisect; static screens may use whole-sha, animated
need region compare).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); ONE fresh no-input boot lands in the game's attract loop
(night halfpipe @T+90, Elise Riggs card @T+120) — the setup chain is
SKIPPED with the live post-T23 NVM (`da021d2a…`, `NVRAM has not
changed`, 397 vblanks all ≤ log 90, 15 early mode changes, 18
`LoadStartModule`, zero ERROR); the laptop Sep 10 `.nvm` was located
(`~/Downloads/PS2_BIOS/`, 1024 B, sha `914d2d7c…`, byte-identical to
the bytesize inputs copy) and NOT copied (SKIPPED → Phase 1b N/A).
The single `t25-auto.sh` then drove attract → TITLE 3× (P1 Cross
532.9 ms, P2 Start 533.0 ms — first Start-button use): title at +10 s
after both presses plus once spontaneously with no press in the
prior 130 s (all three region-identical, text-band p99 0); attract
reclaims within 10–20 s twice (≤80 s once), so no press ever acted
on a displayed title and the first menu was not reached — the chain
ends title/attract-cycling with a 37,793,425-line / 2,482,598,052 B
same-4-channel trace (first >1 GB trace: bytesize-only, head/tail
2000+2000 committed). WSL flapped 6× on the old VM plus 1× on a new
VM after the first-ever mid-session WSL kernel restart (clean NIC
teardown 16:34:14 rendered + start 16:34:17, cause unknown); both
runs completed exit 0 in flap-free windows with clean SIGTERM
shutdowns, and all three traces re-verified post-reboot bit-identical.

## T25-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T25; P-lane lease never touched) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no apt installs this session) |
| ssx3 HEAD at commit | `2b068a0`, clean before evidence add |
| Evidence commit | Below (`[T25]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T25 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes | yes |
| Pad binding | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged; full dump: `Start = Keyboard/Return`, Circle L, Triangle I, Square J, Select Backspace, D-pad arrows | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) before each phase (×3: initial, post-flap-#3, post-flaps-#4/5); reverted by flaps #3/#4-5/#6 and the VM restart (expected) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached (`setsid nohup`) per phase, `xdotool getdisplaygeometry` → `1280 1024` both; Phase-1 Xvfb (PID 468) dead by flaps #4/5, Phase-2 Xvfb (PID 438) dead by flap #6, both verified gone (no `pkill` needed beyond the scripts' tolerant restart) |
| Dirs/files created | `/home/brad/pcsx2-t4/t25-{nvm,nvm-analyze,nvm-vcount,auto,analyze,vcount}.sh`, `t25-*.jpg/.xwd`, `t25-{nvm-,}census.txt`, `t25-{nvm-,}samples.txt`, `…/logs/emulog-pre-t25nvm-20260920T201813Z.txt` (= T23) + `emulog-pre-t25-20260920T202407Z.txt` (= Phase 1) + `boot-t25nvm.log/.stdout` + `boot-t25.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t25*` staging (scripts, snaps, census/samples, `emulog-t25nvm.txt`) |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits) |
| VM restart (not by me) | Old WSL VM NIC torn down clean 16:34:14 rendered, new VM up 16:34:17 (btime `1789935290` → `1789936457`); cause unknown (no `wsl --shutdown` from this session; parallel briefs active — inference, see G2) |

WSL session log (context for every timestamp below; clocks: WSL `date -u`
true UTC; `wevtutil` renders local-as-Z, +4 h → UTC, re-confirmed on
both btimes: 16:14:50 rendered = btime `1789935290` = 20:14:50 UTC,
16:34:17 rendered = btime `1789936457` = 20:34:17 UTC):

| # | UTC (uptime) | Event | Receipt |
|---|---|---|---|
| 1 | 20:14:50 ([0]) | WSL VM1 started fresh on first ssh (new VM; prev VM NIC teardown 16:13:34 rendered in newest-30) | btime, VmSwitch NIC create 16:14:50 rendered |
| 2 | 20:15:57–20:17:08 ([67.29],[100.41],[137.95]) | Flaps #1–#3 (`AcceptAsync` → sdc remount → fresh login each); kill-to-remount 16/2/15 s; all pre-Phase-1 AND pre-mount-effective — mount + all checks re-done after #3 (root login @[122.91] = first mount, reverted by #3; re-mount effective) | full dmesg (pre) |
| 3 | 20:18:09–20:20:23 ([198,332]) | Quiet: Phase-1 single-shot run exit 0, `T25NVM_DONE`, clean shutdown; zero `AcceptAsync` in window | run stdout, uptime stamps, post dmesg |
| 4 | 20:21:54–20:23:06 ([423.89],[495.81]) | Flaps #4–#5 (`AcceptAsync` → remount @[479.73]/[515.87] → login @[480.78]/[516.96]); kill-to-remount 56/20 s; post-Phase-1 (evidence home, trace re-verified sha-match) and pre-Phase-2; Xvfb 468 dead, X11 reverted; re-mount effective | full dmesg (pre2), sha re-verify |
| 5 | 20:24:01–~20:29:57 ([550,~900]) | Quiet: Phase-2 single-shot run exit 0, clean shutdown (effects-verified: p2e snap 16:29 + shutdown tail @log 331.57–331.59 + pcsx2 dead + playtime +331); zero `AcceptAsync` in window | exit 0, snaps, trace tail, post dmesg |
| 6 | 20:30:04 ([913.64]) | Flap #6 (`AcceptAsync` → remount @[936.00] → login @[937.33]); kill-to-remount 22 s; post-run; Xvfb 438 dead, X11 reverted | full dmesg (post), dead pids, reverted dir |
| 7 | 20:34:14–20:34:17 | VM1 NIC teardown clean (IDs 234/233/69/71 @16:34:14 rendered) + VM2 start (NIC create @16:34:17 rendered); btime `…290` → `…457`; all 3 traces re-verified post-reboot bit-identical | eventlog post2, btime, 3/3 sha match |
| 8 | 20:34:43 ([25.61] VM2) | Flap #7 (`AcceptAsync` in the new VM → login @[39.79]); killer hot at VM start again; no runs pending, nothing re-done | full dmesg (post2) |
| 9 | event log | Newest-30 System reads (pre/pre2/post/post2): VM-boundary VmSwitch events only + ONE routine `Kernel-General` ID 16 (registry hive maintenance @16:29:32 rendered, unrelated to flaps); ZERO entries at any of the 6 VM1 flap kills or flap #7 — userland kills leave no Windows trace | `wevtutil qe System /c:30 /rd:true /f:text` ×4 |

## T25-1. Task 1 — NVM verify (does the chain skip?)

Run: `t25-nvm.sh`, ONE fresh boot, ZERO inputs, WID 2097159 (`SSX 3`,
only visible window), boot wall 1789935493 (T_BOOT_UPTIME 202),
20:18:09–20:20:23 UTC (uptime 198→332), exit 0, `T25NVM_DONE`, clean
SIGTERM shutdown (pgrep empty after kill+10 s).

### Fresh-boot table (screen reached with zero inputs — SKIPPED)

| Item | T4/T23 menu value | T25 Phase-1 observed | Match |
|---|---|---|---|
| Screenshot @T+90 | language park `b6ca1aa9…`, 35367 B | `t25-nvm-park.jpg`, 52881 B, sha `d6f5c82c3c9f539b59202915aa910ce7b2af26c05e84ea8ce957fd664ae4b697`: attract loop (night-city halfpipe run, SSX 3 watermark) | NOT the park |
| Screenshot @T+120 | (park holds: `b6ca1aa9…`) | `t25-nvm-park2.jpg`, 60261 B, sha `0dd8b17fc7b4d0af8f946a6594694e51ab65ef81aebeb45c8bd01d1b83ece05c`: attract loop (Elise Riggs character card) | attract continues |
| BIOS line | line 2 | line 2 (`BIOS Found: USA v02.00(14/06/2004)`) | yes |
| ExecPS2 ×2 | lines 142369/142465 | lines 142330/142426 (log 0.8440/0.8715) | lines −39 (new prefix) |
| ReBootStart | line 142764 | line 142725 | −39 |
| sceCdInit | line 405737 | line 405620 | −117 |
| First vblank + LoadStartModule ×2 | lines 417152–417619 | first vblank @417043; LoadStartModule @417245/@417510 | shifted |
| UpdateVSyncRate | line 456475 (×1 DVD NTSC) | line 456189 (×15: DVD NTSC ×7 @log 1.49–5.17, then NTSC ×8 @log 5.20–11.25; final mode NTSC) | ×15, new path |
| First SIF / sceSifGetReg | lines 138615 / 138785 | lines 138577 / 138747 (SIF line from `t25-nvm-samples.txt` §SIF FIRST 10, T21 precedent) | shifted |
| Vblank rate | ~67–68/s to shutdown | 397 TOTAL, all ≤ log 90 (LE90=397, LE120=397, LE135=397); zero after log 90 | frozen (see G6) |
| LoadStartModule total | 2 | 18 | game loading modules |
| sceCdApplySCmd2 | 25,296 (vblanks −29) | 368 (= 397 − 29, same delta) | delta yes |
| ERROR lines | 0 | 0 | yes |
| Shutdown tail | `Pausing…`, `NVRAM saved`, `Releasing host memory` | `Pausing…` @120.0532 (L14643990), play `Add 119 → now 2453` (L14643992; 2334+119 accumulates from T23), `NVRAM has not changed, not writing to disk.`, `Releasing host memory` @120.1048 | clean; no NVM write |
| NVM file across boot | (T23: rewritten, `NVRAM saved`) | sha `da021d2a…865a961` before AND after, mtime unchanged (Sep 20 15:20) | untouched |

Result: SKIPPED — no language park, no setup screen of any kind;
fresh boot with the live post-T23 NVM lands directly in the game's
attract loop. No presses were sent or needed.

### NVM table (laptop .nvm located; copy N/A — SKIPPED, Phase 1b not triggered)

| Item | Value |
|---|---|
| Laptop path | `/Users/bradrichardson/Downloads/PS2_BIOS/ps2-bios-0200a-20040614-100909.nvm` (from `PCSX2.ini:21` `Bios = ../../../Downloads/PS2_BIOS`; laptop `…/PCSX2/bios/` is empty) |
| Size / mtime | 1024 B / Sep 10 10:16:19 2026 (run-end write; Sep 10 `emulog.txt` shows NVRAM missing at boot `errno 2` then `NVRAM saved` at log 125.78 + savestate + play `now 25619`) |
| sha256 | `914d2d7c2b0c05f29cb40e6cff30460bc6233b325004625ed1f37c57f66fa12f` |
| vs bytesize inputs `.nvm` | byte-identical (`914d2d7c…`, 1024 B) |
| vs live post-T23 `.nvm` | DIFFERS (`da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, 1024 B, mtime Sep 20 15:20 = T23 shutdown) |
| Sibling shas (laptop) | `.mec` (4 B) `fbbfc6c1…e463b`; `.bin` (4194304 B) `6d23d001…be4744` (matches T4 BIOS sha) |
| Copied to bytesize? | NO — Phase 1 SKIPPED, so the brief's copy step (`iff replayed`) did not trigger; live `da021d2a…` left in place for Phase 2 |
| Second fresh boot? | N/A (same reason; Phase 2's fresh boot re-confirms the skip independently — see T25-2) |

### Park table (the no-input stable park — the script's start state)

| Item | Value |
|---|---|
| Screen | Attract loop (animated; NOT a static park: T+90 ≠ T+120, distinct shas/sizes) |
| Awaiting | Any button (attract-skip to title — exercised by Phase 2 P1/P2) |
| Vblanks at park | ≤397 at log 90 (= TOTAL; frozen thereafter) |
| Start-state proof | Phase 2 `t25-start.jpg` (T+90, fresh boot): attract again (night halfpipe, 53792 B, sha `353c7ea9…`) — skip reproduces across boots |

## T25-2. Task 2 — scripted path (one script to title/menu)

Run: `t25-auto.sh` (committed), ONE fresh boot (skip re-confirmed),
TWO timed single holds, boot wall 1789935847 (T_BOOT_UPTIME 556),
20:24:01–~20:29:57 UTC (uptime 550→~900), WID 2097159, exit 0, clean
SIGTERM shutdown. Note: the run's ssh stdout was truncated in
delivery (seen through the final `sleep 80`); completion is
effects-verified (p2e snap 16:29 + shutdown tail @log 331.57–331.59
+ pcsx2 dead + playtime +331 + exit 0 — any `fail` would exit 1).

### Script table (`t25-auto.sh` steps as committed)

| Step | T+ (menu-wall) | Action | Expected screen | Screenshot |
|---|---|---|---|---|
| boot | T+0 | fresh boot, same flags/datapath as T23 | attract loop (skip) | — |
| start snap | T+90 | `t17-snap.sh t25-start` | attract (start-state proof) | `t25-start.jpg` |
| P1 | T+100.70→T+101.23 | single K (Cross) hold, 532.9 ms | attract → title | — |
| post-P1 | T+111 / T+121 | snaps | title, settle | `t25-post-p1a.jpg` / `t25-post-p1b.jpg` |
| P2 | T+121.36→T+121.90 | single Return (Start) hold, 533.0 ms | title → first menu | — |
| post-P2 | T+132 / T+152 / T+192 / T+252 / T+332 | snap epoch series | menu, settle | `t25-post-p2a/b/c/d/e.jpg` |
| shutdown | ~T+340 | SIGTERM, 10 s settle | — | — |

Method for both presses: `xdotool windowfocus --sync 2097159`
then `keydown` / `sleep 0.5` / `keyup` (exit 0 each). One hold per
screen; no blind multi-presses; no retries (none sent — nothing
judgeable mid-run; tabled per the ≤1000 ms rule).

### Press table (the two timed inputs)

| Press | Keydown → keyup (UTC wall) | Hold | Menu-wall | Kernel uptime | Single-press proof | Screen at press → screen by +10 s |
|---|---|---|---|---|---|---|
| P1 (Cross) | 1789935947.698018636 → 1789935948.230954864 | 532.9 ms | T+100.70 → T+101.23 | 657 | one down/up pair, exit 0 each | attract (start @T+90) → TITLE (p1a @T+111) |
| P2 (Start) | 1789935968.362414036 → 1789935968.895392338 | 533.0 ms | T+121.36 → T+121.90 | 677→678 | one down/up pair, exit 0 each; first Start-button use (Return keysym) | attract (p1b @T+121) → TITLE (p2a @T+132) |

P2 acted on attract, NOT on title (p1b shows attract had already
reclaimed the screen by T+121) — so the title→menu transition was
never attempted. No press has been sent while a title was displayed.

### Epoch table (screens reached; title 3×, first menu not reached)

| Snap (press-relative) | Size / sha256 (short) | Screen content |
|---|---|---|
| start (T+90, pre-P1) | 53792 B / `353c7ea9` | Attract: night-city halfpipe run, SSX 3 watermark |
| p1a (P1+10 s, T+111) | 58180 B / `0183a72d` | TITLE: `SSX 3` logo, `Press START button`, `© 2003 Electronic Arts Inc.` |
| p1b (P1+20 s, T+121) | 55396 B / `2087c03f` | Attract: daytime halfpipe riders, SSX 3 watermark (title already gone) |
| p2a (P2+10 s, T+132) | 58421 B / `234c7cf4` | TITLE again (same screen, region-identical — see below) |
| p2b (P2+30 s, T+152) | 64005 B / `ac15e10d` | Attract: `One Mountain Three Peaks` mountain card |
| p2c (P2+70 s, T+192) | 47003 B / `39f1dc84` | Attract: sunset jump over rail |
| p2d (P2+130 s, T+252) | 58361 B / `120f688b` | TITLE spontaneously (no press in the prior 130 s; region-identical) |
| p2e (P2+210 s, T+332) | 58284 B / `03884d9e` | Attract: sunset rail slide (run end ~T+340, SIGTERM → clean shutdown) |

Title sameness (text-band crop 380,200,1180,480, `/tmp/t21-cropdiff.py`,
same tool as T17–T23): p1a-vs-p2a mean 0.06 (p99 0, max 37);
p1a-vs-p2d mean 0.04 (p99 0, max 46) — the identical title screen 3×
(JPEG noise only in-band; whole-shas differ — snowfall animates).
Title↔attract cycling data: title at +10 s after both presses (2/2)
AND once with no press in the prior 130 s (p2d); gaps between title
sightings 21 s / 120 s (irregular — not a fixed short cycle);
attract reclaims within ≤10 s (p1a→p1b), ≤20 s (p2a→p2b), ≤80 s
(p2d→p2e). All 10 T25 snaps carry distinct shas (animated everywhere).

Guest/trace side: boot prefix line-identical to Phase 1 through the
first 9 `UpdateVSyncRate` (deterministic NVM-skip prefix); same ×15
early mode changes (last 6 lines −7 vs Phase 1, same modes/times —
inputs added no mode change); vblanks frozen at the same 397 (all
≤90); `LoadStartModule` total the same 18; `sceCdApplySCmd2` the
same 368 (−29 again); EE/IOP called-API sets identical to Phase 1
(52/154 names — inputs changed counts, not the set); zero ERROR;
memcards still UNFORMATTED; shutdown markers `Pausing…` @331.5196
(L37793416), play `Add 331 → now 2784` (L37793418; 2453+331),
`NVRAM has not changed`, `Releasing host memory` @331.5867.

### Trace table (same-4 channels, same ini)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t25 Phase 2 (two presses, T+~340) | 37,793,425 / 2,482,598,052 | `1ba568cc…e15e` | bytesize ONLY (>1 GB rule); head/tail 2000+2000 lines committed (`t25-trace-head.txt` 149019 B sha `3615849b…c79c4`, `t25-trace-tail.txt` 129949 B sha `eae0ccfb…fa9d8`) |
| `emulog-pre-t25-20260920T202407Z.txt` = t25 Phase 1 (no inputs, T+~130) | 14,643,999 / 949,510,490 | `59496133…53de8e` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t25nvm.txt`, same size+sha (match; staging + post-flap + post-reboot re-verifies all match) |
| `emulog-pre-t25nvm-20260920T201813Z.txt` = t23 (preserved at Phase-1 boot) | — / 589,666,091 | `d94cef1a…268f4` (re-verified post-reboot: matches T23's t23 sha) | SSD `emulog-t23.txt` (T23) |

t25 Phase-2 channel census (T4 `t4-census.py`, same script):
`EE.Bios` 5,531,719 (52 distinct names) · `IOP.Bios` 17,430,929 (154
distinct) · `MISC.sif` 12,964,663 · CDVD 1,094,941 · vblanks 397.
Phase-1 census for comparison: `EE.Bios` 2,922,399 (52, set-identical)
· `IOP.Bios` 6,281,884 (154, set-identical) · `MISC.sif` 4,735,766 ·
CDVD 427,799 · vblanks 397.
Format check vs T4 `samples.txt` (line numbers + timestamps
normalized, both phases): FIRST sections (EE 50, SIF 10, CDVD-hw 8)
identical; DEEPEST sections differ (state-dependent guest content —
attract/title vs menu park; e.g. Phase-1 SIF deepest `pos=96` vs T4
`pos=48`, CDVD deepest `SECTOR 1460802–1460804` near disk end) —
same-4 format confirmed. Committed: `t25-census.txt` (11662 B),
`t25-samples.txt` (5893 B), `t25-nvm-census.txt` (11773 B),
`t25-nvm-samples.txt` (5879 B).

### Stop table (where the chain actually ends)

| Item | Value |
|---|---|
| Title? | YES, 3× (p1a, p2a, p2d — region-identical, `Press START button`) |
| First menu? | NO (no press ever sent while title displayed; P2 acted on attract) |
| 1200 s cap | Not reached — stopped per WSL ≤6 min precaution at first-title region per brief (runs T+~130 / T+~340); the 1200 s alternative was not exercised |
| Chain end | Title/attract-cycling (title does not persist: attract reclaims in 10–20 s twice, ≤80 s once) |

## T25-3. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'`
(Windows); all remote phases sequential, one ssh at a time; outer
single quotes required — cmd.exe eats double-quoted pipes, so NO
pipes inline: piped logic lives in staged scripts; `;`-chaining
works INSIDE one `wsl` call only (see gap note: chaining multiple
`wsl` invocations with `;` fails exit 127 — one `wsl` call per ssh);
remote→local filtering pipes locally, e.g. `ssh bytesize 'wsl
dmesg' | tail`):

```
# reuse verification (pipe-free; ; -chained inside one wsl call)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # btime 1789935290
ssh bytesize 'wsl dmesg' | tail -n 30                                 # fresh VM, flap #1 already in full log
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C … rev-parse HEAD; git -C … status --short'   # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs/; ls -la …/dat/PCSX2/bios/'          # sizes; .nvm mtime Sep 20 15:20
ssh bytesize 'wsl grep -n Cross …/inis/PCSX2.ini; which xdotool xwd xwdtopnm pnmtojpeg; ls -la …/t4-census.py …/t4-sample.py …/t17-snap.sh; ls -la …/logs/; sha256sum …/bios/….nvm; sha256sum …/inputs/….nvm; ls -la /tmp/.X11-unix; …'  # :579 K; helpers; logs; da021d2a vs 914d2d7c
ssh bytesize 'wsl pgrep -a pcsx2-qt'                                  # exit 1 (none)
ssh bytesize 'wsl ls -la …/bios/; stat -c %y …/….nvm'                  # NVM mtime 15:20:11 -0400
# laptop .nvm hunt (local only)
ls ~/Library/Application\ Support/PCSX2/{bios,inis,logs,sstates}/     # bios EMPTY; inis/logs/sstates Sep 10 10:16
grep -i bios …/inis/PCSX2.ini                                         # Bios = ../../../Downloads/PS2_BIOS
grep -n NVRAM …/logs/emulog.txt                                       # missing at boot errno 2; saved @125.78
shasum -a 256 ~/Downloads/PS2_BIOS/*                                  # .nvm 914d2d7c… (1024 B); .bin 6d23d001… (match T4)
# pre-run flap captures (F3 rec 18): flaps #1-2, then #3 (mount reverted)
ssh bytesize 'wsl dmesg' > /tmp/t25-dmesg-baseline.txt                # flap #1 @[67.29]
ssh bytesize 'wsl dmesg' > /tmp/t25-dmesg-pre1.txt                     # flaps #1-2 (@[100.41])
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t25-eventlog-pre1.txt  # newest 16:14:51; zero across flaps
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls -la /tmp/.X11-unix; …'  # mounted @uptime 122
ssh bytesize 'wsl dmesg' > /tmp/t25-dmesg-pre2.txt                     # flap #3 @[137.95] placed; mount reverted
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t25-eventlog-pre2.txt  # still newest 16:14:51
# Phase 1 (scripts written locally under local/research/T25/, staged per file)
scp t25-nvm.sh t25-nvm-analyze.sh t25-nvm-vcount.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t25-nvm.sh …-analyze.sh …-vcount.sh /home/brad/pcsx2-t4; …'
ssh bytesize 'wsl -u root mount …; wsl ls …; wsl bash …/t25-nvm.sh'    # EXIT 127: `;` does not chain wsl calls (mount itself succeeded; run never started)
ssh bytesize 'wsl ls -la /tmp/.X11-unix; cat /proc/uptime; grep btime /proc/stat'  # mount verified in place; 3 flaps
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t25-nvm.sh'                # exit 0, T25NVM_DONE (uptime 198→332)
# Phase 1 analysis (read-only streaming)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t25-nvm-analyze.sh'         # sha, wc -l, markers, tail, census+samples via t4 scripts
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t25-nvm-vcount.sh; grep -c LoadStartModule …; grep -c sceCdApplySCmd2 …; grep -m1 -n play.time …; grep -m1 -n Pausing …'
ssh bytesize 'wsl grep -n UpdateVSyncRate …/logs/emulog.txt'          # ×15 with times
ssh bytesize 'wsl dmesg' > /tmp/t25-dmesg-postnvm.txt                  # still 3 flaps; run window clean; Xvfb 468 alive; pcsx2 dead
ssh bytesize 'wsl cp …/t25-nvm-park.jpg …/t25-nvm-park2.jpg …/t25-nvm-census.txt …/t25-nvm-samples.txt /mnt/c/Users/bradr/pcsx2-t4; …'
scp "bytesize:pcsx2-t4/t25-nvm-park.jpg" "bytesize:pcsx2-t4/t25-nvm-park2.jpg" "bytesize:pcsx2-t4/t25-nvm-census.txt" "bytesize:pcsx2-t4/t25-nvm-samples.txt" local/research/T25/
shasum -a 256 local/research/T25/t25-nvm-park.jpg local/research/T25/t25-nvm-park2.jpg
# Phase 2 prep (pad dump shows Start = Keyboard/Return)
ssh bytesize 'wsl sed -n 550,640p …/inis/PCSX2.ini'                   # full [Pad1] dump, no edits
scp t25-auto.sh t25-analyze.sh t25-vcount.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t25-auto.sh …-analyze.sh …-vcount.sh /home/brad/pcsx2-t4; …'
ssh bytesize 'wsl dmesg' | grep -c AcceptAsync                         # 5 → flaps #4-5; Xvfb dead; mount reverted
ssh bytesize 'wsl dmesg' > /tmp/t25-dmesg-pre3.txt                     # flaps #4 @[423.89] #5 @[495.81] placed
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t25-eventlog-pre3.txt  # still newest 16:14:51
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; …'                     # Phase-1 trace 59496133… post-flap match
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; ls -la /tmp/.X11-unix'  # re-mounted
# Phase 2 run (ONE ssh; exit 0; stdout truncated in delivery — effects-verified)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t25-auto.sh'                # exit 0 (uptime 550→~900)
# Phase 2 analysis + retrieval
ssh bytesize 'wsl ls -la …/t25-*.jpg; pgrep -a pcsx2-qt; pgrep -a Xvfb; cat /proc/uptime'  # p2e present; both dead (flap #6)
ssh bytesize 'wsl dmesg' > /tmp/t25-dmesg-post.txt                    # flap #6 @[913.64] placed; run window [550,~900] clean
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t25-eventlog-post.txt  # newest 16:29:32 Kernel-General ID 16 (routine)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t25-analyze.sh'             # 2.48 GB trace; markers; census+samples
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t25-vcount.sh; grep -c LoadStartModule …; grep -c sceCdApplySCmd2 …; grep -m1 -n play.time …; grep -m1 -n Pausing …'
ssh bytesize 'wsl grep -n UpdateVSyncRate …/logs/emulog.txt'          # ×15, last 6 lines −7 vs Phase 1
ssh bytesize 'wsl cp …/t25-start.jpg …/t25-post-p1a.jpg …/t25-post-p1b.jpg …/t25-post-p2a.jpg …/t25-post-p2b.jpg …/t25-post-p2c.jpg …/t25-post-p2d.jpg …/t25-post-p2e.jpg …/t25-census.txt …/t25-samples.txt /mnt/c/Users/bradr/pcsx2-t4'
scp "bytesize:pcsx2-t4/t25-start.jpg" "bytesize:pcsx2-t4/t25-post-p1a.jpg" "bytesize:pcsx2-t4/t25-post-p1b.jpg" "bytesize:pcsx2-t4/t25-post-p2a.jpg" "bytesize:pcsx2-t4/t25-post-p2b.jpg" "bytesize:pcsx2-t4/t25-post-p2c.jpg" "bytesize:pcsx2-t4/t25-post-p2d.jpg" "bytesize:pcsx2-t4/t25-post-p2e.jpg" "bytesize:pcsx2-t4/t25-census.txt" "bytesize:pcsx2-t4/t25-samples.txt" local/research/T25/
shasum -a 256 local/research/T25/t25-start.jpg local/research/T25/t25-post-*.jpg
# local mining
python3 /tmp/t21-cropdiff.py T25/t25-post-p1a.jpg T25/t25-post-p2a.jpg  # title region match (see §T25-2)
python3 /tmp/t21-cropdiff.py T25/t25-post-p1a.jpg T25/t25-post-p2d.jpg  # title region match (see §T25-2)
bash -c 'diff <(sed … T4/samples.txt) <(sed … T25/t25-nvm-samples.txt)'  # format check (see §T25-2)
bash -c 'diff <(sed … T4/samples.txt) <(sed … T25/t25-samples.txt)'      # format check (see §T25-2)
bash -c 'diff <(grep … EE/IOP sets nvm) <(grep … EE/IOP sets t25)'       # called-API sets identical
# big-trace head/tail + Phase-1 SSD copy (COPYFILE_DISABLE=1 on SSD steps)
ssh bytesize 'wsl head -n 2000 …/logs/emulog.txt' > local/research/T25/t25-trace-head.txt
ssh bytesize 'wsl tail -n 2000 …/logs/emulog.txt' > local/research/T25/t25-trace-tail.txt
ssh bytesize 'wsl cp …/logs/emulog-pre-t25-20260920T202407Z.txt /mnt/c/Users/bradr/pcsx2-t4/emulog-t25nvm.txt; sha256sum …'  # 59496133… (staging match)
export COPYFILE_DISABLE=1; scp "bytesize:pcsx2-t4/emulog-t25nvm.txt" "/Volumes/Extreme SSD/ps2x-t4/emulog-t25nvm.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t25nvm.txt"         # 59496133… (match)
# teardown verification + VM-restart characterization + post-reboot re-verify
ssh bytesize 'wsl pgrep -a Xvfb; pgrep -a pcsx2-qt; ls -la /tmp/.X11-unix; grep btime /proc/stat; cat /proc/uptime; ps -o pid,etime,cmd -p 1'  # btime CHANGED …290→…457 (VM restart)
ssh bytesize 'wsl ls -la …/logs/; sha256sum …/bios/….nvm'              # all sizes same; NVM da021d2a… unchanged
ssh bytesize 'wsl dmesg' > /tmp/t25-dmesg-post2.txt                    # new VM; flap #7 @[25.61]
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text' > /tmp/t25-eventlog-post2.txt  # teardown 16:34:14 + new VM 16:34:17
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; sha256sum …/emulog-pre-t25-….txt; sha256sum …/emulog-pre-t25nvm-….txt'  # 1ba568cc… / 59496133… / d94cef1a… (3/3 post-reboot match)
# report (chunks; receipts include tail -3)
cp /tmp/t25-dmesg-pre2.txt local/research/T25/t25-dmesg-pre.txt; cp /tmp/t25-dmesg-pre3.txt local/research/T25/t25-dmesg-pre2.txt
cp /tmp/t25-eventlog-pre2.txt local/research/T25/t25-eventlog-pre.txt; cp /tmp/t25-eventlog-pre3.txt local/research/T25/t25-eventlog-pre2.txt
cp /tmp/t25-dmesg-post.txt local/research/T25/; cp /tmp/t25-eventlog-post.txt local/research/T25/
cp /tmp/t25-dmesg-post2.txt local/research/T25/; cp /tmp/t25-eventlog-post2.txt local/research/T25/
tail -3 local/research/T25/REPORT.md
git add -f local/research/T25/<31 files by name>                      # ignored dir, forced
git commit -m "[T25] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T25-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (title↔attract cycling) | Boot fresh (NVM skips to attract by ≤90 s), single 534 ms K hold → title expected by +10 s, then a single 534 ms Start (Return) hold WITHIN ≤10 s of the title appearing (attract reclaimed the title in ≤10 s once, ≤20 s once — P2 missed it by acting on attract); screenshot-verify the first menu. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses. The tight title dwell is the new constraint — a fixed T+130 P2 cannot hit a ≤10 s window reliably |
| G2 | WSL killer still active (7 flaps) + first kernel restart (VM teardown+start, cause unknown) | 7 userland `AcceptAsync` kills this session (6 on VM1 in 3 clusters + 1 on VM2 @[25.61]); kernel never rebooted within a VM (btime constant per VM). Kill-to-remount 16/2/15/56/20/22 s (datum mostly inside T21's 3–48 s; #2 at 2 s and #4 at 56 s are new extremes — still = time-to-next-`wsl`-use). NEW: first-ever mid-session WSL VM restart — clean NIC teardown 16:34:14 rendered + start 16:34:17 (btime `…290`→`…457`); not from this session (no `wsl --shutdown` run; parallel briefs were active — inference). Precautions stand, plus: re-check btime (not just dmesg+init) before trusting cross-ssh continuity, and re-verify trace shas after any reboot (3/3 matched here). Tooling datum: `;` chains only INSIDE one `wsl` call — chaining multiple `wsl` invocations in one ssh fails exit 127 (`wsl: command not found` inside WSL bash); use one `wsl` call per ssh |
| G3 | Windows event log: zero flap entries; VM-boundary sequences bound the restart | Newest-30 reads (pre/pre2/post/post2): VM-boundary VmSwitch events only across all 7 flaps (userland kills leave no Windows trace — T17/T21/T23 precedent stands) + one routine `Kernel-General` ID 16 (registry hive maintenance @16:29:32 rendered, unrelated). Old-VM teardown (IDs 234/233/69/71 @16:34:14 rendered) + new-VM create (@16:34:17) bound the restart cleanly. `wevtutil` local-as-Z (+4 h → UTC) re-confirmed on BOTH btimes |
| G4 | Hold count 12/12; Start button first use | 534 ms holds register 12/12 across T17c+T19+T21+T23+T25 (1+2+3+4+2 presses, P2 = first Start/Return use, delivered exit 0); ~18 ms tap = no effect (T17a). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Everything animates; region compare carries the title sameness | All 10 T25 snaps carry distinct shas (attract FMV + title snowfall); the 3 titles are proven the same screen only by text-band region diff (p99 0 both pairs). Whole-sha equality stays usable only where staticity is proven per-screen (T23 park), never assumed |
| G6 | Vblank freeze in NVM-skip runs (new datum) | `WaitVblankStart` stops after log ≤90 in BOTH NVM-skip runs (397 total, inputs change nothing: counts, `LoadStartModule` 18, `sceCdApplySCmd2` 368, and EE/IOP name sets all Phase-1-identical); menu runs (T4–T23) continue ~68/s to shutdown. The attract/title sync mechanism differs from the menu loop's — unmapped |
| G7 | First >1 GB trace (bytesize-only) + logs-dir growth | Phase-2 trace 2,482,598,052 B stays bytesize-only (head/tail 2000+2000 committed per brief); Phase-1 949,510,490 B SSD-copied. `…/logs/` now holds ~7.2 GB across 11 emulogs (T17→T25 chain, all preserved) — followers must check C: free before long captures |
| G8 | Game printfs still off | `EnableEEConsole/EnableIOPConsole=false` carried from T4 (defaults kept); EE `sysPrintOut` + IOP stdout absent. A rerun with both `=true` would add game-side strings |
| G9 | Session wall | ~23 min active of the 6 h box (+ report/commit); zero lease waits (no lease exists for T25) |

## Evidence files

`REPORT.md` (this file),
Phase-1: `t25-nvm.sh`, `t25-nvm-analyze.sh`, `t25-nvm-vcount.sh`,
`t25-nvm-park.jpg` (attract night halfpipe), `t25-nvm-park2.jpg`
(Elise Riggs card), `t25-nvm-census.txt`, `t25-nvm-samples.txt`;
Phase-2: `t25-auto.sh`, `t25-analyze.sh`, `t25-vcount.sh`,
`t25-start.jpg` (attract start-state), `t25-post-p1a.jpg` (TITLE),
`t25-post-p1b.jpg` (attract), `t25-post-p2a.jpg` (TITLE),
`t25-post-p2b/c.jpg` (attract), `t25-post-p2d.jpg` (TITLE,
spontaneous), `t25-post-p2e.jpg` (attract), `t25-census.txt`,
`t25-samples.txt`, `t25-trace-head.txt` / `t25-trace-tail.txt`
(2000+2000 lines of the 2.48 GB trace);
flaps: `t25-dmesg-pre.txt` (flaps #1–#3) / `t25-dmesg-pre2.txt`
(flaps #1–#5) / `t25-dmesg-post.txt` (6-flap VM1 signature + clean
run windows) / `t25-dmesg-post2.txt` (VM2 + flap #7),
`t25-eventlog-pre.txt` / `t25-eventlog-pre2.txt` (byte-identical,
VM-boundary only) / `t25-eventlog-post.txt` (+ routine ID 16) /
`t25-eventlog-post2.txt` (teardown + new VM).
Full Phase-1 trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-t25nvm.txt`
(949,510,490 B, sha `59496133…53de8e`, NOT in git) + bytesize
original `…/logs/emulog-pre-t25-20260920T202407Z.txt` (same,
re-verified post-flap + post-reboot). Full Phase-2 trace:
bytesize-only `…/logs/emulog.txt` (2,482,598,052 B, sha
`1ba568cc…e15e`, re-verified post-reboot). T23 trace preserved as
`…/logs/emulog-pre-t25nvm-20260920T201813Z.txt` (sha `d94cef1a…`,
re-verified post-reboot).
