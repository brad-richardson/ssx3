# T23 report — G1 fourth input: confirm Standard advances to Settings-completed park (bytesize, no lease)

Brief `local/muse/prompts/T23.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
6 h; session wall ~19:11–19:23 UTC 2026-09-20 (~12 min).

Stale-reading guard: `local/research/T21/REPORT.md` (all: gap G1 = this
brief, T21 DST park, WSL precautions G2–G5),
`local/research/T21/t21-post*.jpg` (the DST park to reproduce),
`local/research/T19/REPORT.md` (T19 Time Zone park),
`local/research/T17/REPORT.md` (T17c User Prefs park, flap/event-log notes),
`local/research/T4/REPORT.md` (T4-0..T4-4 SHAPE, reuse recipe, trace format).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); fresh boot reproduces the T4/T17/T19/T21 language park
bit-identically (sha `b6ca1aa9…`); press-1 (single 534.8 ms K hold)
reproduces User Prefs / Language / English (text-band region diff vs
`t17c-post15.jpg`: mean 0.10, p99 0); press-2 (single 534.5 ms K hold)
reproduces User Prefs / Time Zone / Kabul (region diff vs `t19-post15.jpg`:
mean 0.02, p99 0); press-3 (single 533.5 ms K hold) reproduces User
Preferences / Daylight Savings Time / Standard (region diff vs
`t21-post15.jpg`: mean 0.07, p99 1); press-4 (single 533.7 ms K hold,
confirm Standard) advances to a new STATIC park, `Settings completed. /
Settings can be adjusted later / in System Configuration.` (✕ Enter only),
captured in 6 sha-identical snaps + an 8,340,484-line / 589,666,091 B
same-4-channel trace (SSD copy sha-matched). No retry press was needed. WSL
flapped 5× (4 pre-run, 1 post-run, all `AcceptAsync` userland kills, same
kernel throughout); the run itself completed exit 0 in a flap-free window
with a clean SIGTERM shutdown. Per F3 rec 18 the flaps were captured in
full dmesg + newest-30 Windows System-log reads (zero entries across the
flap window).

## T23-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T23; P-lane lease never touched) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no apt installs this session) |
| ssx3 HEAD at commit | `9b03c7a`, clean before evidence add |
| Evidence commit | Below (`[T23]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T23 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes | yes |
| Pad binding | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) before the run; reverted by the post-run userland restart (expected) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached (`setsid nohup`), `xdotool getdisplaygeometry` → `1280 1024`; dead by the post-run flap, verified gone (no `pkill` needed) |
| Dirs/files created | `/home/brad/pcsx2-t4/t23-auto.sh`, `t23-analyze.sh`, `t23-vcount.sh`, `t23-*.jpg/.xwd`, `t23-census.txt`, `t23-samples.txt`, `…/logs/emulog-pre-t23-20260920T191402Z.txt` + `boot-t23.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t23*` staging (scripts, snaps, census/samples, `emulog-t23.txt`) |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits) |

WSL session log (context for every timestamp below; btime `1789931482` =
2026-09-20 19:11:22 UTC, constant all session — kernel never rebooted):

| # | UTC | Event | Receipt |
|---|---|---|---|
| 1 | 19:11:22 | WSL VM started fresh on first ssh (new VM; prev VM torn down clean 14:22:24 rendered per event log — the T21→T23 kernel change was shutdown+start, not a crash) | btime, VmSwitch NIC create @15:11:23 rendered + delete @14:22:24 rendered |
| 2 | 19:11:43–19:13:24 | Flaps #1–#4 (`AcceptAsync` @dmesg [20.52],[71.88],[105.60],[122.97] → sdc remount → fresh login each); all pre-run AND pre-mount-effective — mount + all checks re-done after #4 (root login @[141.68] = re-mount) | full dmesg (pre/pre2) |
| 3 | 19:13:57–19:20:21 | Quiet: single-shot run uptime 155→538 (exit 0, `T23_DONE`, clean shutdown) + trace analysis; uptime stamps monotonic, zero `AcceptAsync` in [155,538] | run stdout, uptime stamps, post dmesg |
| 4 | 19:21:34–19:22:07 | Flap #5 (`AcceptAsync` @[612.61] → remount @[644.96] → fresh init @[646.07]); post-run; kill-to-remount 32 s = time to next `wsl` use (inside T21's 3–48 s datum); Xvfb dead by it, `/tmp/.X11-unix` reverted | full dmesg (post), init `etime 00:38` at uptime 684 (684−646=38), dead pids, reverted dir |
| 5 | event log | Newest-30 System reads (pre + post): VmSwitch NIC create @15:11:23 rendered (this VM), delete @14:22:24 rendered (post-T21 teardown), create @14:10:02 rendered (T21's VM); ZERO entries 15:11–15:23 rendered covering all 5 flaps — userland kills leave no Windows trace | `wevtutil qe System /c:30 /rd:true /f:text` ×2 |
| 6 | clocks | WSL `date -u` used throughout (true UTC); `wevtutil` renders local-as-Z (EDT, +4 h → UTC, T17 G3 re-confirmed: 15:11:23 rendered = 19:11:23 UTC = btime) | cross-check |

## T23-1. Task 1 — park chain

### Park-1 table (fresh boot reproduces the language park?)

| Item | T4/T21 value | T23 observed | Match |
|---|---|---|---|
| Screenshot | `b6ca1aa9…`, 35367 B | `t23-park.jpg`, 35367 B, sha `b6ca1aa93ab3b8112a6b71caf5fd54a728284575af42c57f5c6fc0e9cb76f084` | BIT-IDENTICAL |
| BIOS line | line 2 | line 2 (`BIOS Found: USA v02.00(14/06/2004)`) | yes |
| ExecPS2 ×2 | lines 142369/142465 | lines 142369/142465 (log 0.8376/0.8651 — times vary, lines identical) | lines yes |
| ReBootStart | line 142764 | line 142764 | yes |
| sceCdInit | line 405737 | line 405737 | yes |
| First vblank + LoadStartModule ×2 | lines 417152–417619 | first vblank @417152; LoadStartModule @417354/@417619 | yes |
| UpdateVSyncRate DVD NTSC | line 456475 (×1) | line 456475 (×1 total) | yes |
| First SIF / sceSifGetReg | lines 138615 / 138785 | lines 138615 / 138785 | yes |
| Vblank rate | ~67–68/s | 25,325 / 368.7 s ≈ 68.7/s | yes |
| Vblanks at park snap (log ≤90) | 6,102 (T21) | 6,100 (pace phase) | −2 (pace) |
| Vblanks at press-1 (log ≤100) | 6,773 (T21) | 6,768 | −5 (boundary timing) |

Boot log prefix is deterministic to the line across runs (same build/inputs/flags); only log-times vary.

### Press table (the four ✕ presses)

Method for all: `xdotool windowfocus --sync 2097159` then `keydown K` /
`sleep 0.5` / `keyup K` (exit 0 each), WID 2097159 (`SSX 3`, only visible
window). Menu-wall = seconds since boot launch (boot wall 1789931642).

| Press | Keydown → keyup (UTC wall) | Hold | Menu-wall | Kernel uptime | Single-press proof | Screen effect |
|---|---|---|---|---|---|---|
| 1 | 1789931742.792859233 → 1789931743.327638226 | 534.8 ms | T+100.79 → T+101.33 | 259→260 | one down/up pair, exit 0 each; exactly one screen transition (no double-advance) | PARK-1 BROKEN: User Prefs / Language / English by T+110 (see below) |
| 2 (confirm English) | 1789931753.392803624 → 1789931753.927345561 | 534.5 ms | T+111.39 → T+111.93 | 270→271 | one down/up pair, exit 0 each; exactly one screen transition | PARK-2 BROKEN: User Prefs / Time Zone / Kabul by +8 s (see below) |
| 3 (confirm Kabul) | 1789931761.992634977 → 1789931762.526139350 | 533.5 ms | T+119.99 → T+120.53 | 279 | one down/up pair, exit 0 each; exactly one screen transition | PARK-3 BROKEN: Daylight Savings Time / Standard by +8 s (see below) |
| 4 (confirm Standard) | 1789931770.591547518 → 1789931771.125226016 | 533.7 ms | T+128.59 → T+129.13 | 287→288 | one down/up pair, exit 0 each; exactly one screen transition | PARK-4 BROKEN: Settings-completed screen by +5 s (see T23-2) |

Press-1 region-match vs T17 User Prefs (`t17c-post15.jpg`, caption present
in both; whole-sha not compared — spinner animates):

| Item | T23 `t23-prefs.jpg` | T17 `t17c-post15.jpg` | Match |
|---|---|---|---|
| Screen text | User Preferences / Language / English (◀ ▶), `Select language.` caption, ✕ Enter ○ Back | same | perceptual yes |
| Text-band crop (380,200,1180,480) mean abs diff | 0.10 (p99 0, max 135; JPEG noise only) | — | region yes |
| Whole-sha | `e7677564…` (31343 B) | different (spinner rotated) | n/a by design |

Press-2 region-match vs T19 Time Zone (`t19-post15.jpg`, caption present
in both):

| Item | T23 `t23-tz.jpg` | T19 `t19-post15.jpg` | Match |
|---|---|---|---|
| Screen text | User Preferences / Time Zone / GMT +4:30 Kabul (◀ ▶), `Select time zone.` caption, ✕ Enter ○ Back | same | perceptual yes |
| Text-band crop (380,200,1180,480) mean abs diff | 0.02 (p99 0, max 104; JPEG noise only) | — | region yes |
| Whole-sha | `dbfa9cb9…` (31543 B) | different (spinner rotated) | n/a by design |

Press-3 region-match vs T21 DST (`t21-post15.jpg`, caption present
in both):

| Item | T23 `t23-dst.jpg` | T21 `t21-post15.jpg` | Match |
|---|---|---|---|
| Screen text | User Preferences / Daylight Savings Time (Summer Time) / Standard (Winter Time) (◀ ▶), `Is daylight savings time in effect?` caption, ✕ Enter ○ Back | same | perceptual yes |
| Text-band crop (380,200,1180,480) mean abs diff | 0.07 (p99 1, max 66; JPEG noise only) | — | region yes |
| Whole-sha | `0553ce87…` (37016 B) | different (spinner rotated) | n/a by design |

Retry row: not needed — press-4 registered on the first hold (new screen by
+5 s; no ≤1000 ms retry press was sent).

## T23-2. Task 2 — next-epoch capture (press-4 at T+128.6)

### Epoch table (screens reached after the confirm-Standard press)

| Snap (press-4-relative) | Size / sha256 (short) | Screen content |
|---|---|---|
| dst (T+~128, pre-press-4) | 37016 B / `0553ce87` | User Preferences / Daylight Savings Time (Summer Time) / Standard (Winter Time), `Is daylight savings time in effect?` caption, ✕ Enter ○ Back |
| +5 s | 31057 B / `37c57308` | NEW static screen: `Settings completed. / Settings can be adjusted later / in System Configuration.`, ✕ Enter only (no Back, no spinner) |
| +15 s | 31057 B / `37c57308` | Same screen, byte-identical |
| +30 s | 31057 B / `37c57308` | Same screen, byte-identical |
| +60 s | 31057 B / `37c57308` | Same screen, byte-identical |
| +120 s | 31057 B / `37c57308` | Same screen, byte-identical |
| +240 s | 31057 B / `37c57308` | Same screen, byte-identical (run end T+~378, SIGTERM → clean shutdown) |

All six post-press-4 snaps are sha-identical (`37c573082276…f4122`) —
no spinner, no caption blink; the first fully static screen in the chain.

Guest/trace side: single DVD-NTSC mode throughout (one `UpdateVSyncRate`);
no new `LoadStartModule` after boot (2 total, both pre-press); menu loop
continues (sema/event/timer storm + per-vblank `sceCdApplySCmd2` ×25,296 vs
25,325 vblanks, −29 — the same delta as T21's 24,328 vs 24,357);
zero ERROR lines; play-time line `Add 368 seconds play time to SLUS-20772
-> now 2334` (1966+368 — accumulates from T21); shutdown markers
`(VMManager) Pausing…` @368.7197, `DEV9close`, `Unloading EGL`,
`NVRAM saved`, `Releasing host memory` at log 368.72–368.79.

### Trace table (same-4 channels, same ini)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t23 (four presses, T+~378) | 8,340,484 / 589,666,091 | `d94cef1a…268f4` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t23.txt`, same size+sha (match; bytesize original re-verified post-flap, same) |
| `emulog-pre-t23-20260920T191402Z.txt` = t21 (preserved at boot) | — / 567,984,708 | `f4e7e8e1…200ec7` (re-verified post-flap: matches T21's t21 sha) | SSD `emulog-t21.txt` (T21) |

t23 channel census (T4 `t4-census.py`, same script): `EE.Bios` 977,568
(42 distinct names) · `IOP.Bios` 5,696,960 (103 distinct) · `MISC.sif`
1,023,502 · CDVD 490,918 · vblanks 25,325.
Format check vs T4 `samples.txt` (line numbers + timestamps normalized):
identical except total-lines header and two SIF fifo `pos` data values
(92 vs 48) — the same two deviations as T21 — same-4 format confirmed.
Committed: `t23-census.txt` (9575 B), `t23-samples.txt` (5878 B).

### Park table (first new stable park)

| Item | Value |
|---|---|
| Screen | `Settings completed. / Settings can be adjusted later / in System Configuration.`, ✕ Enter only (no ○ Back) |
| Awaiting | ✕ (the sole prompt) |
| Reached by | +5 s post-press-4 (T+~134), held through +240 s (T+~378, run end) |
| Vblanks at new park | ≤8,804 at log 130 (first post-press-4 mark); 25,325 at log 368 (= TOTAL) |
| 1200 s cap | Not reached — stopped at first new stable park per brief (T+~378); the 1200 s alternative was not exercised (park found by +5 s, WSL ≤6 min precaution) |

## T23-3. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'` (Windows); all
remote phases sequential, one ssh at a time; outer single quotes required —
cmd.exe eats double-quoted pipes, so NO pipes inline: piped logic lives in
staged scripts; `;`-chaining inside one `wsl` call works; remote→local
filtering pipes locally, e.g. `ssh bytesize 'wsl dmesg' | tail`):

```
# reuse verification (pipe-free; ; -chained)
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # btime 1789931482
ssh bytesize 'wsl dmesg' | tail -n 30                                 # fresh boot, no AcceptAsync in tail yet
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C … rev-parse HEAD; git -C … status --short'   # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs; ls -la …/dat/PCSX2/bios'            # sizes
ssh bytesize 'wsl grep -n Cross …/dat/PCSX2/inis/PCSX2.ini'           # :579 Cross = Keyboard/K
ssh bytesize 'wsl which xdotool xwd xwdtopnm pnmtojpeg'               # all present
ssh bytesize 'wsl ls -la …/t4-census.py …/t4-sample.py …/t17-snap.sh'  # helpers present
ssh bytesize 'wsl ls -la …/dat/PCSX2/logs'                            # emulog.txt = t21, 567984708 B
# t21 preservation proof + display
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la /tmp/.X11-unix; …'  # f4e7e8e1… (t21 match)
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; …'
# pre-run flap check (F3 rec 18): AcceptAsync count 2→4 across checks
ssh bytesize 'wsl dmesg' > /tmp/t23-dmesg-pre1.txt                     # 3 flaps @[20.52],[71.88],[105.60]
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text'              # VM-boundary events only; zero across flaps
ssh bytesize 'wsl -u root mount …; …'                                 # re-mount after flap #4 @[122.97]
ssh bytesize 'wsl dmesg' > /tmp/t23-dmesg-pre2.txt                     # flap #4 placed; mount intact
# scripts (written locally under local/research/T23/, staged per file)
scp t23-auto.sh t23-analyze.sh t23-vcount.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t23-auto.sh …/t23-analyze.sh …/t23-vcount.sh /home/brad/pcsx2-t4; …'
# run (ONE ssh; full stdout in session log; key lines in §T23-1/2)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t23-auto.sh'                # exit 0, T23_DONE
# analysis (read-only streaming)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t23-analyze.sh'             # sha, wc -l, markers, tail, census+samples via t4 scripts
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t23-vcount.sh; grep -c LoadStartModule …; grep -c sceCdApplySCmd2 …; grep -m1 -n play.time …; grep -m1 -n Pausing …'
ssh bytesize 'wsl cp …/t23-park.jpg …/t23-prefs.jpg …/t23-tz.jpg …/t23-dst.jpg …/t23-post5.jpg …/t23-post15.jpg …/t23-post30.jpg …/t23-post60.jpg …/t23-post120.jpg …/t23-post240.jpg …/t23-census.txt …/t23-samples.txt /mnt/c/Users/bradr/pcsx2-t4; …'
# (first-SIF line 138615 taken from t23-samples.txt §SIF FIRST 10 — the dmaSIF0 grep hits an earlier RegisterIntrHandler line instead, T21 precedent)
# retrieval (remote stage + scp home; hashes local)
scp "bytesize:pcsx2-t4/t23-park.jpg" "bytesize:pcsx2-t4/t23-prefs.jpg" "bytesize:pcsx2-t4/t23-tz.jpg" "bytesize:pcsx2-t4/t23-dst.jpg" "bytesize:pcsx2-t4/t23-post5.jpg" "bytesize:pcsx2-t4/t23-post15.jpg" "bytesize:pcsx2-t4/t23-post30.jpg" "bytesize:pcsx2-t4/t23-post60.jpg" "bytesize:pcsx2-t4/t23-post120.jpg" "bytesize:pcsx2-t4/t23-post240.jpg" "bytesize:pcsx2-t4/t23-census.txt" "bytesize:pcsx2-t4/t23-samples.txt" local/research/T23/
shasum -a 256 local/research/T23/t23-*.jpg
# full-trace retrieval to SSD (590 MB < 1 GB, so a home copy exists AND the bytesize original stays)
ssh bytesize 'wsl cp …/logs/emulog.txt /mnt/c/Users/bradr/pcsx2-t4/emulog-t23.txt; sha256sum …/emulog-t23.txt; …'  # d94cef1a… (staging match)
scp "bytesize:pcsx2-t4/emulog-t23.txt" "/Volumes/Extreme SSD/ps2x-t4/emulog-t23.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t23.txt"            # d94cef1a… (match)
# local mining
python3 /tmp/t21-cropdiff.py T23/t23-prefs.jpg T17/t17c-post15.jpg     # region match (see §T23-1)
python3 /tmp/t21-cropdiff.py T23/t23-tz.jpg T19/t19-post15.jpg         # region match (see §T23-1)
python3 /tmp/t21-cropdiff.py T23/t23-dst.jpg T21/t21-post15.jpg        # region match (see §T23-1)
bash -c 'diff <(sed … T4/samples.txt) <(sed … T23/t23-samples.txt)'    # format check (see §T23-2)
# post-run flap characterization (F3 rec 18) + teardown verification
ssh bytesize 'wsl dmesg' > /tmp/t23-dmesg-post.txt                     # full signature: 5× AcceptAsync @[20],[71],[105],[122],[612]; run window [155,538] clean
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text'               # VM-boundary VmSwitch events only; zero entries across flap window
ssh bytesize 'wsl ps -o pid,etime,cmd -p 1; cat /proc/uptime; …'       # init 00:38 at uptime 684 → flap #5 found
ssh bytesize 'wsl pgrep -a Xvfb; pgrep -a pcsx2-qt; ls -la /tmp/.X11-unix; …'  # both dead; X11 reverted
ssh bytesize 'wsl ls -la …/logs; sha256sum …/emulog-pre-t23-20260920T191402Z.txt; grep btime /proc/stat; sha256sum …/logs/emulog.txt; …'  # t21 f4e7e8e1… preserved; btime constant; t23 d94cef1a… post-flap match
# report (chunks; receipts include tail -3)
git add -f local/research/T23/<21 files by name>                      # ignored dir, forced
git commit -m "[T23] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T23-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Settings-completed park) | Boot fresh to the language park, single 534 ms K hold → User Prefs, second single 534 ms K hold → Time Zone, third single 534 ms K hold → Daylight Savings Time, fourth single 534 ms K hold → Settings completed, then a fifth single 534 ms K hold on ✕ Enter (the sole prompt — no ○ Back on this screen); screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | WSL killer still active (5 flaps, run flap-free 155→538) | 5 userland `AcceptAsync` kills this session (4 pre-run in a 123 s cluster + 1 post-run); kernel never rebooted. Datum holds: flap #5 kill-to-remount 32 s = time-to-next-`wsl`-use (inside T21's 3–48 s range). Pre-run cluster shows the killer hot at VM start — mount + checks must be re-done after the last pre-run flap. Precautions stand: single-shot unattended scripts, runs ≤6 min, preserve emulogs before every boot, re-check `dmesg` + btime + init age before trusting any background process; flap scans use unfiltered dmesg only (err-level misses `AcceptAsync`) |
| G3 | Windows event log around flaps: zero entries | Newest-30 System captures (pre + post) show VM-boundary VmSwitch events only (this VM NIC create 15:11:23 rendered; post-T21 teardown 14:22:24 rendered; T21 VM create 14:10:02 rendered — cross-confirms T21's rows); zero entries 15:11–15:23 rendered across all 5 flaps — userland kills leave no Windows trace (T17/T21 precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed |
| G4 | Hold threshold still unmapped | 534 ms holds register 10/10 across T17c+T19+T21+T23 (1+2+3+4 presses, one further new screen broken); ~18 ms tap = no effect (T17a). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | New park fully static; animated screens still need region compare | All six post-press-4 snaps sha-identical (`37c57308…`) — no spinner, no caption blink on the Settings-completed screen (first static screen in the chain). Screen-change detection stays perceptual/region-based for animated screens; whole-sha equality is usable only where staticity is proven per-screen, never assumed |
| G6 | Game printfs still off | `EnableEEConsole/EnableIOPConsole=false` carried from T4 (defaults kept); EE `sysPrintOut` + IOP stdout absent. A rerun with both `=true` would add game-side strings |
| G7 | Session wall | ~12 min active of the 6 h box; zero lease waits (no lease exists for T23) |

## Evidence files

`REPORT.md` (this file), `t23-census.txt` (channel census + markers),
`t23-samples.txt` (EE/SIF/CDVD-hw samples, format-checked vs T4),
`t23-park.jpg` (language park, bit-identical to T4/T17/T19/T21),
`t23-prefs.jpg` (User Prefs / English, region-matched to T17c),
`t23-tz.jpg` (User Prefs / Time Zone / Kabul, region-matched to T19),
`t23-dst.jpg` (Daylight Savings Time / Standard, region-matched to T21),
`t23-post5/15/30/60/120/240.jpg` (the Settings-completed epoch series,
all sha-identical),
`t23-dmesg-pre.txt` / `t23-dmesg-pre2.txt` / `t23-dmesg-post.txt` (full
unfiltered dmesg: pre-run flaps #1–#3, flap #4 placed, full 5-flap
signature + clean run window),
`t23-eventlog-pre.txt` / `t23-eventlog-post.txt` (newest-30 Windows
System log around the flaps, UTF-16),
scripts `t23-auto.sh`, `t23-analyze.sh`, `t23-vcount.sh`. Full t23 trace:
`/Volumes/Extreme SSD/ps2x-t4/emulog-t23.txt` (589,666,091 B, sha
`d94cef1a…268f4`, NOT in git) + bytesize original
`/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt` (same, re-verified
post-flap).
