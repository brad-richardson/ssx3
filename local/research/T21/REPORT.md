# T21 report — G1 third input: confirm Kabul advances to Daylight Savings Time park (bytesize, no lease)

Brief `local/muse/prompts/T21.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
6 h; session wall ~18:10–18:22 UTC 2026-09-20 (~12 min).

Stale-reading guard: `local/research/T19/REPORT.md` (all: gap G1 = this
brief, T19 Time Zone park, WSL precautions G2–G4),
`local/research/T19/t19-post*.jpg` (the Time Zone park to reproduce),
`local/research/T17/REPORT.md` (T17c User Prefs park, flap/event-log notes),
`local/research/T4/REPORT.md` (T4-0..T4-4 SHAPE, reuse recipe, trace format).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); fresh boot reproduces the T4/T17/T19 language park bit-identically
(sha `b6ca1aa9…`); press-1 (single 535.4 ms K hold) reproduces User Prefs /
Language / English (text-band region diff vs `t17c-post15.jpg`: mean 0.10,
p99 0); press-2 (single 534.4 ms K hold) reproduces User Prefs / Time Zone /
Kabul (region diff vs `t19-post15.jpg`: mean 0.02, p99 0); press-3 (single
534.5 ms K hold, confirm Kabul) advances to a new stable park, User
Preferences / Daylight Savings Time / Standard (Winter Time), captured in a
6-snap series + an 8,037,470-line / 567,984,708 B same-4-channel trace (SSD
copy sha-matched). No retry press was needed. WSL flapped 6× (1 pre-run, 5
post-run, all `AcceptAsync` userland kills, same kernel throughout); the run
itself completed exit 0 in a flap-free window with a clean SIGTERM shutdown.
Per F3 rec 18 the post-run flaps were captured in full dmesg + a newest-30
Windows System-log read (zero entries across the flap window).

## T21-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T21; P-lane lease never touched) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no apt installs this session) |
| ssx3 HEAD at commit | `7770435` (plus foreign `M tools/trace_align.py`, untouched) |
| Evidence commit | Below (`[T21]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T21 observed | Match |
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
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) before the run; reverted by the post-run userland restarts (expected) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached (`setsid nohup`), `xdotool getdisplaygeometry` → `1280 1024`; dead by the post-run flaps, verified gone (no `pkill` needed) |
| Dirs/files created | `/home/brad/pcsx2-t4/t21-auto.sh`, `t21-analyze.sh`, `t21-vcount.sh`, `t21-*.jpg/.xwd`, `t21-census.txt`, `t21-samples.txt`, `…/logs/emulog-pre-t21-20260920T181117Z.txt` + `boot-t21.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t21*` staging (scripts, snaps, census/samples, `emulog-t21.txt`) |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits) |

WSL session log (context for every timestamp below; btime `1789927801` =
2026-09-20 18:10:01 UTC, constant all session — kernel never rebooted):

| # | UTC | Event | Receipt |
|---|---|---|---|
| 1 | 18:10:01 | WSL VM started fresh on first ssh (new VM; prev VM torn down clean 16:23:17Z per event log — the T19→T21 kernel change was shutdown+start, not a crash) | btime, VmSwitch NIC create @14:10:02 EDT + delete @12:23:17 EDT |
| 2 | 18:10:43 | Flap #1 (`AcceptAsync` @dmesg [41.85] → sdc remount [59] → fresh login [60]); pre-run AND pre-mount — mount + all checks re-done after it | full dmesg |
| 3 | 18:11–18:17 | Quiet: reuse verification + full T21 single-shot run (exit 0, `T21_DONE`, clean shutdown) + trace analysis completed; uptime stamps monotonic 71→~468 | run stdout, uptime stamps |
| 4 | 18:18:04–18:20:26 | Flaps #2–#6 (`AcceptAsync` @[482.75],[507.43],[526.55],[595.58],[624.84], each → remount → unclean journal → fresh init); every post-flap ssh ran in a fresh userland with coherent output; kill-to-remount gap = time to next `wsl` use (3–48 s); Xvfb dead by these, `/tmp/.X11-unix` reverted | full dmesg, init `etime 00:01` ×2, dead pids, reverted dir |
| 5 | event log | Newest-30 System read: VmSwitch NIC create @14:10:02 EDT (this VM), delete @12:23:17 EDT (post-T19 teardown), create @12:19:08 EDT (T19's reboot VM); ZERO entries 14:10–14:22 EDT covering all 6 flaps — userland kills leave no Windows trace | `wevtutil qe System /c:30 /rd:true /f:text` |
| 6 | clocks | WSL `date -u` used throughout (true UTC); `wevtutil` renders local-as-Z (EDT, +4 h → UTC, T17 G3 re-confirmed) | cross-check |

## T21-1. Task 1 — park chain

### Park-1 table (fresh boot reproduces the language park?)

| Item | T4/T19 value | T21 observed | Match |
|---|---|---|---|
| Screenshot | `b6ca1aa9…`, 35367 B | `t21-park.jpg`, 35367 B, sha `b6ca1aa93ab3b8112a6b71caf5fd54a728284575af42c57f5c6fc0e9cb76f084` | BIT-IDENTICAL |
| BIOS line | line 2 | line 2 (`BIOS Found: USA v02.00(14/06/2004)`) | yes |
| ExecPS2 ×2 | lines 142369/142465 | lines 142369/142465 (log 0.8770/0.9041 — times vary, lines identical) | lines yes |
| ReBootStart | line 142764 | line 142764 | yes |
| sceCdInit | line 405737 | line 405737 | yes |
| First vblank + LoadStartModule ×2 | lines 417152–417619 | first vblank @417152; LoadStartModule @417354/@417619 | yes |
| UpdateVSyncRate DVD NTSC | line 456475 (×1) | line 456475 (×1 total) | yes |
| First SIF / sceSifGetReg | lines 138615 / 138785 | lines 138615 / 138785 | yes |
| Vblank rate | ~67–68/s | 24,357 / 360.2 s ≈ 67.6/s | yes |
| Vblanks at park snap (log ≤90) | 6,108 (T19) | 6,102 (67.80/s vs 67.87/s — pace phase) | −6 (pace) |
| Vblanks at press-1 (log ≤100) | 6,776 (T19) | 6,773 | −3 (boundary timing) |

Boot log prefix is deterministic to the line across runs (same build/inputs/flags); only log-times vary.

### Press table (the three ✕ presses)

Method for all: `xdotool windowfocus --sync 2097159` then `keydown K` /
`sleep 0.5` / `keyup K` (exit 0 each), WID 2097159 (`SSX 3`, only visible
window). Menu-wall = seconds since boot launch (boot wall 1789927877).

| Press | Keydown → keyup (UTC wall) | Hold | Menu-wall | Kernel uptime | Single-press proof | Screen effect |
|---|---|---|---|---|---|---|
| 1 | 1789927977.378312830 → 1789927977.913701229 | 535.4 ms | T+100.38 → T+100.91 | 175→176 | one down/up pair, exit 0 each; exactly one screen transition (no double-advance) | PARK-1 BROKEN: User Prefs / Language / English by T+110 (see below) |
| 2 (confirm English) | 1789927987.980077479 → 1789927988.514508441 | 534.4 ms | T+110.98 → T+111.51 | 186 | one down/up pair, exit 0 each; exactly one screen transition | PARK-2 BROKEN: User Prefs / Time Zone / Kabul by +8 s (see below) |
| 3 (confirm Kabul) | 1789927996.580838760 → 1789927997.115296233 | 534.5 ms | T+119.58 → T+120.12 | 194→195 | one down/up pair, exit 0 each; exactly one screen transition | PARK-3 BROKEN: Daylight Savings Time screen by +5 s (see T21-2) |

Press-1 region-match vs T17 User Prefs (`t17c-post15.jpg`, caption present
in both; whole-sha not compared — spinner animates):

| Item | T21 `t21-prefs.jpg` | T17 `t17c-post15.jpg` | Match |
|---|---|---|---|
| Screen text | User Preferences / Language / English (◀ ▶), `Select language.` caption, ✕ Enter ○ Back | same | perceptual yes |
| Text-band crop (380,200,1180,480) mean abs diff | 0.10 (p99 0, max 90; JPEG noise only) | — | region yes |
| Whole-sha | `d917fe3e…` (31333 B) | different (spinner rotated) | n/a by design |

Press-2 region-match vs T19 Time Zone (`t19-post15.jpg`, caption present
in both):

| Item | T21 `t21-tz.jpg` | T19 `t19-post15.jpg` | Match |
|---|---|---|---|
| Screen text | User Preferences / Time Zone / GMT +4:30 Kabul (◀ ▶), `Select time zone.` caption, ✕ Enter ○ Back | same | perceptual yes |
| Text-band crop (380,200,1180,480) mean abs diff | 0.02 (p99 0, max 16; JPEG noise only) | — | region yes |
| Whole-sha | `dae29df1…` (31665 B) | different (spinner rotated) | n/a by design |

Retry row: not needed — press-3 registered on the first hold (new screen by
+5 s; no ≤1000 ms retry press was sent).

## T21-2. Task 2 — next-epoch capture (press-3 at T+119.6)

### Epoch table (screens reached after the confirm-Kabul press)

| Snap (press-3-relative) | Size / sha256 (short) | Screen content |
|---|---|---|
| tz (T+~119, pre-press-3) | 31665 B / `dae29df1` | User Preferences / Time Zone / GMT +4:30 Kabul, `Select time zone.` caption, ✕ Enter ○ Back |
| +5 s | 36909 B / `a4fa5663` | NEW stable screen: User Preferences / Daylight Savings Time (Summer Time) / Standard (Winter Time) (◀ ▶), `Is daylight savings time in effect?` caption, ✕ Enter ○ Back |
| +15 s | 36897 B / `a491fba3` | Same DST screen (spinner rotated) |
| +30 s | 36725 B / `b32b93c3` | Same DST screen (spinner rotated) |
| +60 s | 36924 B / `364d562e` | Same DST screen (spinner rotated) |
| +120 s | 37001 B / `9d1c9d8c` | Same DST screen (spinner rotated) |
| +240 s | 36708 B / `972a1097` | Same DST screen (run end T+~370, SIGTERM → clean shutdown) |

Guest/trace side: single DVD-NTSC mode throughout (one `UpdateVSyncRate`);
no new `LoadStartModule` after boot (2 total, both pre-press); menu loop
continues (sema/event/timer storm + per-vblank `sceCdApplySCmd2` ×24,328);
zero ERROR lines; play-time line `Add 360 seconds play time to SLUS-20772
-> now 1966`; shutdown markers `(VMManager) Pausing…` @360.12,
`DEV9close`, `Unloading EGL`, `Releasing host memory` at log 360.18–360.19.

### Trace table (same-4 channels, same ini)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t21 (three presses, T+~370) | 8,037,470 / 567,984,708 | `f4e7e8e1…200ec7` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t21.txt`, same size+sha (match; bytesize original re-verified post-flap, same) |
| `emulog-pre-t21-20260920T181117Z.txt` = t19 (preserved at boot) | — / 555,405,357 | `8882a6bb…d0ad6f70` (re-verified post-flap: matches T19's t19 sha) | SSD `emulog-t19.txt` (T19) |

t21 channel census (T4 `t4-census.py`, same script): `EE.Bios` 950,148
(42 distinct names) · `IOP.Bios` 5,484,275 (103 distinct) · `MISC.sif`
985,149 · CDVD 472,113 · vblanks 24,357.
Format check vs T4 `samples.txt` (line numbers + timestamps normalized):
identical except total-lines header and two SIF fifo `pos` data values
(92 vs 48) — same-4 format confirmed. Committed: `t21-census.txt`
(9560 B), `t21-samples.txt` (5878 B).

### Park table (first new stable park)

| Item | Value |
|---|---|
| Screen | User Preferences, Daylight Savings Time (Summer Time) = Standard (Winter Time) (◀ ▶), `Is daylight savings time in effect?` caption, ✕ Enter ○ Back |
| Awaiting | ✕ (confirm Standard) or ○ (back to Time Zone) |
| Reached by | +5 s post-press-3 (T+~125), held through +240 s (T+~370, run end) |
| Vblanks at new park | ≤8,198 at log 121 (first post-press-3 mark); 24,357 at log 362 (= TOTAL) |
| 1200 s cap | Not reached — stopped at first new stable park per brief (T+~370) |

## T21-3. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL) or `ssh bytesize 'wevtutil …'` (Windows); all
remote phases sequential, one ssh at a time; outer single quotes required —
cmd.exe eats double-quoted pipes, so NO pipes inline: piped logic lives in
staged scripts; `;`-chaining inside one `wsl` call works):

```
# reuse verification (pipe-free; ; -chained)
ssh bytesize 'wsl date -u'                                            # 18:10:03Z
ssh bytesize 'wsl date -u; cat /proc/uptime; grep btime /proc/stat'   # btime 1789927801
ssh bytesize 'wsl dmesg; ps -o pid,etime,cmd -p 1; cat /proc/uptime'   # fresh boot, init 00:21
ssh bytesize 'wsl sha256sum …/bin/pcsx2-qt; stat -c %s …'              # 6719f5d6…ee327 / 130929856
ssh bytesize 'wsl git -C … rev-parse HEAD; git -C … status --short'   # 9056c08349… / empty
ssh bytesize 'wsl ls -la …/inputs; ls -la …/dat/PCSX2/bios'            # sizes
ssh bytesize 'wsl grep -n Cross …/dat/PCSX2/inis/PCSX2.ini'           # :579 Cross = Keyboard/K
ssh bytesize 'wsl which xdotool xwd xwdtopnm pnmtojpeg'               # all present
ssh bytesize 'wsl ls -la …/t4-census.py …/t4-sample.py …/t17-snap.sh'  # helpers present
ssh bytesize 'wsl ls -la …/dat/PCSX2/logs'                            # emulog.txt = t19, 555405357 B
# t19 preservation proof + display
ssh bytesize 'wsl sha256sum …/logs/emulog.txt; ls -la /tmp/.X11-unix; …'  # 8882a6bb… (t19 match)
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix; …'
# scripts (written locally under local/research/T21/, staged per file)
scp t21-auto.sh t21-analyze.sh t21-vcount.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t21-auto.sh …/t21-analyze.sh …/t21-vcount.sh /home/brad/pcsx2-t4; …'
# run (ONE ssh; full stdout in session log; key lines in §T21-1/2)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t21-auto.sh'                # exit 0, T21_DONE
# analysis (read-only streaming)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t21-analyze.sh'             # sha, wc -l, markers, tail, census+samples via t4 scripts
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t21-vcount.sh; grep -m1 -n dmaSIF0 …; grep -c LoadStartModule …; grep -c sceCdApplySCmd2 …; grep -m1 -n play.time …; grep -m1 -n Pausing …; …'
ssh bytesize 'wsl grep -m1 -n dmaSIF0 …; cp …/t21-park.jpg …/t21-prefs.jpg …/t21-tz.jpg …/t21-post5.jpg …/t21-post15.jpg …/t21-post30.jpg …/t21-post60.jpg …/t21-post120.jpg …/t21-post240.jpg …/t21-census.txt …/t21-samples.txt /mnt/c/Users/bradr/pcsx2-t4; …'
# (first-SIF line 138615 taken from t21-samples.txt §SIF FIRST 10 — the dmaSIF0 grep hits an earlier RegisterIntrHandler line instead)
# retrieval (remote stage + scp home; hashes local)
scp "bytesize:pcsx2-t4/t21-park.jpg" "bytesize:pcsx2-t4/t21-prefs.jpg" "bytesize:pcsx2-t4/t21-tz.jpg" "bytesize:pcsx2-t4/t21-post5.jpg" "bytesize:pcsx2-t4/t21-post15.jpg" "bytesize:pcsx2-t4/t21-post30.jpg" "bytesize:pcsx2-t4/t21-post60.jpg" "bytesize:pcsx2-t4/t21-post120.jpg" "bytesize:pcsx2-t4/t21-post240.jpg" "bytesize:pcsx2-t4/t21-census.txt" "bytesize:pcsx2-t4/t21-samples.txt" local/research/T21/
shasum -a 256 local/research/T21/t21-*.jpg
# full-trace retrieval to SSD (568 MB < 1 GB, so a home copy exists AND the bytesize original stays)
ssh bytesize 'wsl cp …/logs/emulog.txt /mnt/c/Users/bradr/pcsx2-t4/emulog-t21.txt; sha256sum …/emulog-t21.txt; …'  # f4e7e8e1… (staging match)
scp "bytesize:pcsx2-t4/emulog-t21.txt" "/Volumes/Extreme SSD/ps2x-t4/emulog-t21.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t21.txt"            # f4e7e8e1… (match)
# local mining
python3 /tmp/t21-cropdiff.py T21/t21-prefs.jpg T17/t17c-post15.jpg     # region match (see §T21-1)
python3 /tmp/t21-cropdiff.py T21/t21-tz.jpg T19/t19-post15.jpg         # region match (see §T21-1)
bash -c 'diff <(sed … T4/samples.txt) <(sed … T21/t21-samples.txt)'    # format check (see §T21-2)
# post-run flap characterization (F3 rec 18) + teardown verification
ssh bytesize 'wsl grep btime /proc/stat; ps -o pid,etime,cmd -p 1; dmesg --level=emerg,alert,crit,err; pgrep -a pcsx2-qt; pgrep -a Xvfb; sha256sum …/logs/emulog-pre-t21-20260920T181117Z.txt; …'  # init 00:01 → flap found; NOTE err-level filter MISSES AcceptAsync (logged below err) — flap scan must use unfiltered dmesg
ssh bytesize 'wsl dmesg; ps -o pid,etime,cmd -p 1; ls -la /tmp/.X11-unix; grep btime /proc/stat; pgrep -a Xvfb; ls -la …/logs/emulog.txt; sha256sum …/logs/emulog.txt; …'  # full signature: 6× AcceptAsync @[41],[482],[507],[526],[595],[624]; X11 reverted; emulog.txt f4e7e8e1… post-flap match
ssh bytesize 'wevtutil qe System /c:30 /rd:true /f:text'               # VM-boundary VmSwitch events only; zero entries across flap window
# report (chunks; receipts include tail -3)
git add -f local/research/T21/<15 files by name>                       # ignored dir, forced
git commit -m "[T21] …" -m "…" -m "Orchestrated-By: Muse Code"         # NO push
```

## T21-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (DST park) | Boot fresh to the language park, single 534 ms K hold → User Prefs, second single 534 ms K hold → Time Zone, third single 534 ms K hold → Daylight Savings Time, then a fourth single 534 ms K hold to confirm Standard (Winter Time); screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | WSL killer still active (6 flaps, new timing datum) | 6 userland `AcceptAsync` kills this session (1 pre-run + 5 post-run; run itself flap-free 71→~468); kernel never rebooted. New datum: kill-to-remount gap equals time-to-next-`wsl`-use (3–48 s observed) — remount + fresh init happen on the next ssh. Precautions stand: single-shot unattended scripts, runs ≤6 min, preserve emulogs before every boot, re-check `dmesg` + btime + init age before trusting any background process. Correction: an err-level dmesg filter misses the `AcceptAsync` signature (logged below err) — flap scans must use unfiltered dmesg |
| G3 | Windows event log around flaps: zero entries | Newest-30 System capture shows VM-boundary VmSwitch events only (this VM NIC create 14:10:02 EDT; post-T19 teardown 12:23:17 EDT; T19 reboot-VM create 12:19:08 EDT — cross-confirms T19's rows); zero entries 14:10–14:22 EDT across all 6 flaps — userland kills leave no Windows trace (T17 precedent stands). `wevtutil` local-as-Z (+4 h → UTC) re-confirmed |
| G4 | Hold threshold still unmapped | 534 ms holds register 6/6 across T17c+T19+T21 (1+2+3 presses, four new screens broken); ~18 ms tap = no effect (T17a). Minimum reliable hold still unknown — brief says reuse 534 ms, do NOT bisect |
| G5 | Caption steady this run, spinner animates | `Is daylight savings time in effect?` caption present in all 6 post-press-3 snaps (no blink observed), but the spinner rotates every snap — screen-change detection must stay perceptual/region-based, never whole-file sha |
| G6 | Game printfs still off | `EnableEEConsole/EnableIOPConsole=false` carried from T4 (defaults kept); EE `sysPrintOut` + IOP stdout absent. A rerun with both `=true` would add game-side strings |
| G7 | Session wall | ~12 min active of the 6 h box; zero lease waits (no lease exists for T21) |

## Evidence files

`REPORT.md` (this file), `t21-census.txt` (channel census + markers),
`t21-samples.txt` (EE/SIF/CDVD-hw samples, format-checked vs T4),
`t21-park.jpg` (language park, bit-identical to T4/T17/T19), `t21-prefs.jpg`
(User Prefs / English, region-matched to T17c), `t21-tz.jpg` (User Prefs /
Time Zone / Kabul, region-matched to T19),
`t21-post5/15/30/60/120/240.jpg` (the Daylight Savings Time epoch series),
scripts `t21-auto.sh`, `t21-analyze.sh`, `t21-vcount.sh`. Full t21 trace:
`/Volumes/Extreme SSD/ps2x-t4/emulog-t21.txt` (567,984,708 B, sha
`f4e7e8e1…200ec7`, NOT in git) + bytesize original
`/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt` (same, re-verified
post-flap).
