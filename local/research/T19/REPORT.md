# T19 report — G1 second input: confirm English advances to Time Zone park (bytesize, no lease)

Brief `local/muse/prompts/T19.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
6 h; session wall ~16:09–16:23 UTC 2026-09-20 (~15 min).

Stale-reading guard: `local/research/T17/REPORT.md` (all: gap G1 = this
brief, T17c User Prefs park, WSL flap precautions G2–G5),
`local/research/T17/t17c-post*.jpg` (the User Prefs park to reproduce),
`local/research/T4/REPORT.md` (T4-0..T4-4 SHAPE, reuse recipe, trace
format).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); fresh boot reproduces the T4/T17 language park bit-identically
(sha `b6ca1aa9…`); press-1 (single 534.7 ms K hold) reproduces User Prefs /
Language / English (text-band region diff vs `t17c-post15.jpg`: mean 0.09,
p99 0); press-2 (single 534.1 ms K hold, confirm English) advances to a new
stable park, User Preferences / Time Zone / GMT +4:30 Kabul, awaiting
✕/○, captured in a 6-snap series + a 7,860,627-line / 555,405,357 B
same-4-channel trace (SSD copy sha-matched). No retry press was needed.
WSL rebooted twice around the run (kernels `…0584` → `…1148`) and flapped
twice more in the 133 s after; the run itself completed exit 0 in a quiet
window with a clean SIGTERM shutdown.

## T19-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T19; P-lane lease never touched) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no apt installs this session) |
| ssx3 HEAD at commit | `383858f` (clean before evidence add; `local/` ignored, added with `-f`) |
| Evidence commit | Below (`[T19]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T19 observed | Match |
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
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) before the run; reverted by the post-run WSL restart (expected) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached (`setsid nohup`), `xdotool getdisplaygeometry` → `1280 1024`; dead after post-run restart, verified gone (no `pkill` needed) |
| Dirs/files created | `/home/brad/pcsx2-t4/t19-auto.sh`, `t19-analyze.sh`, `t19-vcount.sh`, `t19-*.jpg/.xwd`, `t19-census.txt`, `t19-samples.txt`, `…/logs/emulog-pre-t19-20260920T161129Z.txt` + `boot-t19.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t19*` staging (scripts, snaps, census/samples, `emulog-t19.txt`) |
| Untouched | `.wslconfig`, BIOS/ISO inputs, `PCSX2.ini` (no edits) |

WSL session log (context for every timestamp below):

| # | UTC | Event | Receipt |
|---|---|---|---|
| 1 | 16:09:44 | WSL kernel booted (`btime 1789920584`, fresh vs T17's `1789916743` — a reboot happened between sessions, cause unknown) | `/proc/stat`, fresh dmesg ring |
| 2 | 16:09–16:19 | Quiet: reuse verification + full T19 single-shot run (exit 0, clean shutdown) completed; uptime stamps monotonic 2→~457 | run stdout, uptime stamps |
| 3 | 16:19:08 | WSL kernel rebooted (`btime 1789921148`), right after run end (~16:18); new kernel's userland flapped 2× in its first 133 s (`p9io.cpp AcceptAsync` @[58],[125], each followed by fresh login session — same signature as T17 gap G2) | `/proc/stat`, dmesg, uptime 133 s |
| 4 | clocks | WSL `date -u` used throughout; run-script wall stamps are true UTC (T17 G3 wevtutil note not needed — no Windows events read this session) | — |

## T19-1. Task 1 — park chain

### Park-1 table (fresh boot reproduces the language park?)

| Item | T4/T17 value | T19 observed | Match |
|---|---|---|---|
| Screenshot | `b6ca1aa9…`, 35367 B | `t19-park.jpg`, 35367 B, sha `b6ca1aa93ab3b8112a6b71caf5fd54a728284575af42c57f5c6fc0e9cb76f084` | BIT-IDENTICAL |
| BIOS line | line 2 | line 2 (`BIOS Found: USA v02.00(14/06/2004)`) | yes |
| ExecPS2 ×2 | lines 142369/142465 | lines 142369/142465 (log 0.8448/0.8722 — times vary, lines identical) | lines yes |
| ReBootStart | line 142764 | line 142764 | yes |
| sceCdInit | line 405737 | line 405737 | yes |
| First vblank + LoadStartModule ×2 | lines 417152–417619 | first vblank @417152; LoadStartModule @417354/@417619 | yes |
| UpdateVSyncRate DVD NTSC | line 456475 (×1) | line 456475 (×1 total) | yes |
| First SIF / sceSifGetReg | lines 138615 / 138785 | lines 138615 / 138785 | yes |
| Vblank rate | ~67–68/s | 23,786 / 352 s ≈ 67.6/s | yes |
| Vblanks at park snap (log ≤90) | 6,108 (T17c) | 6,108 | yes |
| Vblanks at press-1 (log ≤100) | 6,777 (T17c) | 6,776 | ±1 (boundary timing) |

Boot log prefix is deterministic to the line across runs (same build/inputs/flags); only log-times vary.

### Press table (the two ✕ presses)

Method for both: `xdotool windowfocus --sync 2097159` then `keydown K` /
`sleep 0.5` / `keyup K` (exit 0 each), WID 2097159 (`SSX 3`, only visible
window). Menu-wall = seconds since boot launch (boot wall 1789920689).

| Press | Keydown → keyup (UTC wall) | Hold | Menu-wall | Kernel uptime | Single-press proof | Screen effect |
|---|---|---|---|---|---|---|
| 1 | 1789920789.493905688 → 1789920790.028624949 | 534.7 ms | T+100.5 → T+101.0 | 205 | one down/up pair, exit 0 each; exactly one screen transition (no double-advance) | PARK-1 BROKEN: User Prefs / Language / English by T+~111 (see below) |
| 2 (confirm English) | 1789920800.094844313 → 1789920800.628924293 | 534.1 ms | T+111.1 → T+111.6 | 216 | one down/up pair, exit 0 each; exactly one screen transition | PARK-2 BROKEN: User Prefs / Time Zone / Kabul by +5 s (see T19-2) |

Press-1 region-match vs T17 User Prefs (`t17c-post15.jpg`, caption present
in both; whole-sha not compared per T17 G5 — spinner animates):

| Item | T19 `t19-prefs.jpg` | T17 `t17c-post15.jpg` | Match |
|---|---|---|---|
| Screen text | User Preferences / Language / English (◀ ▶), `Select language.`, ✕ Enter ○ Back | same | perceptual yes |
| Text-band crop (380,200,1180,480) mean abs diff | 0.09 (p99 0; JPEG noise only) | — | region yes |
| Whole-sha | `1328b491…` (31366 B) | different (spinner rotated) | n/a by design |

Retry row: not needed — press-2 registered on the first hold (no ≤1000 ms
retry press was sent).

## T19-2. Task 2 — next-epoch capture (press-2 at T+111.1)

### Epoch table (screens reached after the confirm-English press)

| Snap (press-2-relative) | Size / sha256 (short) | Screen content |
|---|---|---|
| prefs (T+~111, pre-press-2) | 31366 B / `1328b491` | User Preferences / Language / English, `Select language.` caption, ✕ Enter ○ Back |
| +5 s | 31615 B / `cbdf092a` | NEW stable screen: User Preferences / Time Zone / GMT +4:30 Kabul, `Select time zone.` caption, ✕ Enter ○ Back |
| +15 s | 31736 B / `582296c0` | Same Time Zone screen (spinner rotated) |
| +30 s | 31900 B / `f0706daf` | Same Time Zone screen (spinner rotated) |
| +60 s | 31726 B / `64974016` | Same Time Zone screen (spinner rotated) |
| +120 s | 31825 B / `4aab1e4f` | Same Time Zone screen (spinner rotated) |
| +240 s | 31656 B / `ec1e164d` | Same Time Zone screen (run end T+~352, SIGTERM → clean shutdown) |

Guest/trace side: single DVD-NTSC mode throughout (one `UpdateVSyncRate`);
no new `LoadStartModule` after boot (2 total, both pre-press); menu loop
continues (sema/event/timer storm + per-vblank `sceCdApplySCmd2` ×23,757);
zero ERROR lines; play-time line `Add 351 seconds play time to SLUS-20772
-> now 1606`; shutdown markers `Pausing…`, `DEV9close`, `Unloading EGL`,
`Releasing host memory` at log 351.51–351.58.

### Trace table (same-4 channels, same ini)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t19 (two presses, T+352) | 7,860,627 / 555,405,357 | `8882a6bb…d0ad6f70` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t19.txt`, same size+sha (match) |
| `emulog-pre-t19-20260920T161129Z.txt` = t17c (preserved at boot) | — / 540,313,630 | `4f61ea83…538749` (re-verified: matches T17's t17c sha) | SSD `emulog-t17c.txt` (T17) |

t19 channel census (T4 `t4-census.py`, same script): `EE.Bios` 933,990
(42 distinct names) · `IOP.Bios` 5,360,267 (103 distinct) · `MISC.sif`
962,923 · CDVD 461,044 · vblanks 23,786.
Format check vs T4 `samples.txt` (line numbers + timestamps normalized):
identical except total-lines header and two SIF fifo `pos` data values
(12 vs 48) — same-4 format confirmed. Committed: `t19-census.txt`
(9515 B), `t19-samples.txt` (5878 B).

### Park table (first new stable park)

| Item | Value |
|---|---|
| Screen | User Preferences, Time Zone = GMT +4:30 Kabul (◀ ▶), `Select time zone.` caption, ✕ Enter ○ Back |
| Awaiting | ✕ (confirm Kabul) or ○ (back to Language) |
| Reached by | +5 s post-press-2 (T+~117), held through +240 s (T+~352, run end) |
| Vblanks at new park | ≤8,133 at log 120 (first post-press-2 mark); 23,786 at log 352 |
| 1200 s cap | Not reached — stopped at first new stable park per brief (T+352) |

## T19-3. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize 'wsl …'` (WSL); all remote phases sequential, one ssh at a
time; outer single quotes required — cmd.exe eats double-quoted pipes):

```
# reuse verification
ssh bytesize 'wsl sha256sum /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt'  # 6719f5d6…ee327
ssh bytesize 'wsl stat -c %s …/bin/pcsx2-qt'                              # 130929856
ssh bytesize 'wsl git -C /home/brad/pcsx2-t4/pcsx2 rev-parse HEAD'         # 9056c08349…
ssh bytesize 'wsl git -C … status --short'                                # (empty)
ssh bytesize 'wsl ls -la /home/brad/pcsx2-t4/inputs/ …/dat/PCSX2/bios/'    # sizes
ssh bytesize 'wsl grep -n Cross …/dat/PCSX2/inis/PCSX2.ini'               # :579 Cross = Keyboard/K
ssh bytesize 'wsl which xdotool xwd xwdtopnm pnmtojpeg'                   # all present
# WSL health (fresh kernel boot found; G2 precautions throughout)
ssh bytesize 'wsl date -u' ; 'wsl cat /proc/uptime' ; 'wsl dmesg'          # btime 1789920584
# display
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix'
# scripts (written locally under local/research/T19/, staged per file)
scp t19-auto.sh t19-analyze.sh t19-vcount.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/t19-*.sh /home/brad/pcsx2-t4/'
# run (ONE ssh; full stdout in session log; key lines in §T19-1/2)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t19-auto.sh'                   # exit 0, T19_DONE
# analysis (read-only streaming)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t19-analyze.sh'                # sha, wc -l, markers, tail, census+samples via t4 scripts
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/t19-vcount.sh'                 # robust vblank counts at log ≤90/100/112/120/352
# retrieval (remote stage + scp home; hashes local)
ssh bytesize 'wsl cp /home/brad/pcsx2-t4/t19-park.jpg …/t19-post240.jpg …/t19-census.txt …/t19-samples.txt /mnt/c/Users/bradr/pcsx2-t4/'
scp "bytesize:pcsx2-t4/t19-*.jpg" "bytesize:pcsx2-t4/t19-census.txt" "bytesize:pcsx2-t4/t19-samples.txt" local/research/T19/
shasum -a 256 local/research/T19/t19-*.jpg
# full-trace retrieval to SSD (555 MB < 1 GB, so a home copy exists AND the bytesize original stays)
ssh bytesize 'wsl cp …/logs/emulog.txt /mnt/c/Users/bradr/pcsx2-t4/emulog-t19.txt'
ssh bytesize 'wsl sha256sum /mnt/c/Users/bradr/pcsx2-t4/emulog-t19.txt'   # 8882a6bb… (staging match)
scp "bytesize:pcsx2-t4/emulog-t19.txt" "/Volumes/Extreme SSD/ps2x-t4/emulog-t19.txt"
shasum -a 256 "/Volumes/Extreme SSD/ps2x-t4/emulog-t19.txt"               # 8882a6bb… (match)
# local mining
bash -c 'diff <(sed … T4/samples.txt) <(sed … T19/t19-samples.txt)'       # format check (see §T19-2)
python3 PIL crop-diff t19-prefs.jpg vs T17/t17c-post15.jpg                # region match (see §T19-1)
# post-run restart characterization + teardown verification
ssh bytesize 'wsl cat /proc/stat'  # btime 1789921148 (2nd kernel)
ssh bytesize 'wsl dmesg'           # AcceptAsync @[58],[125]
ssh bytesize 'wsl pgrep -a Xvfb' ; 'wsl pgrep -a pcsx2-qt'                # both empty: clean
ssh bytesize 'wsl sha256sum …/logs/emulog-pre-t19-20260920T161129Z.txt'   # 4f61ea83… (t17c preserved)
# report
git add -f local/research/T19/<13 files by name>                          # ignored dir, forced
git commit -m "[T19] …" -m "…" -m "Orchestrated-By: Muse Code"            # NO push
```

## T19-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Next-input proposal (Time Zone park) | Boot fresh to the language park, single 534 ms K hold → User Prefs, second single 534 ms K hold → Time Zone, then a third single 534 ms K hold to confirm Kabul; screenshot-verify the next screen. Each screen keeps needing its own single input; map per-screen inputs one at a time, never blind multi-presses |
| G2 | WSL killer still active, now with kernel reboots | 2 kernel boots in ~10 min (`…0584` pre-session, `…1148` post-run) + 2 userland `AcceptAsync` flaps in the 133 s after the run; killer still unidentified (T17 G2 stood). A follower must keep the same precautions: single-shot unattended scripts, runs ≤6 min, preserve emulogs before every boot, re-check `dmesg` + btime + init age before trusting any background process |
| G3 | Hold threshold still unmapped | 534 ms holds register 3/3 across T17c+T19 (two new screens broken); ~18 ms tap = no effect (T17a). Minimum reliable hold still unknown — bisect between those bounds before building longer input scripts |
| G4 | Caption blink | `Select time zone.` caption present in all 6 post-press-2 snaps this run (no blink observed), but the spinner animates every snap — screen-change detection must stay perceptual/region-based, never whole-file sha |
| G5 | Game printfs still off | `EnableEEConsole/EnableIOPConsole=false` carried from T4 (defaults kept); EE `sysPrintOut` + IOP stdout absent. A rerun with both `=true` would add game-side strings |
| G6 | Session wall | ~15 min active of the 6 h box; zero lease waits (no lease exists for T19) |

## Evidence files

`REPORT.md` (this file), `t19-census.txt` (channel census + markers),
`t19-samples.txt` (EE/SIF/CDVD-hw samples, format-checked vs T4),
`t19-park.jpg` (language park, bit-identical to T4/T17), `t19-prefs.jpg`
(User Prefs / English, region-matched to T17c),
`t19-post5/15/30/60/120/240.jpg` (the Time Zone epoch series), scripts
`t19-auto.sh`, `t19-analyze.sh`, `t19-vcount.sh`. Full t19 trace:
`/Volumes/Extreme SSD/ps2x-t4/emulog-t19.txt` (555,405,357 B, sha
`8882a6bb…d0ad6f70`, NOT in git) + bytesize original
`/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt` (same).
