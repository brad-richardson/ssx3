# T17 report — G1 pad automation: ✕ press breaks the language park (bytesize, no lease)

Brief `local/muse/prompts/T17.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
6 h; session wall ~15:04–15:48 UTC 2026-09-20 (~45 min).

Stale-reading guard: `local/research/T4/REPORT.md` (all: reuse recipe, §T4-1
row 8 binary identity, §T4-2 epochs/samples, gap G1 = this brief),
`local/research/T4/samples.txt` (trace format),
`local/research/T4/snap-language-select.jpg` (the park to break).

Headline readings: the T4 Devel build was reused bit-identically (no
rebuild); default pad ini already maps Cross to `K`; `xdotool` focus+XTEST
keys demonstrably reach PCSX2-Qt (SPACE pause flatlines the trace + `Paused`
OSD). A ~18 ms K tap does nothing (6/6 snaps park-identical through +240 s);
a single 534 ms K hold advances language-select to a new stable park, User
Preferences (Language=English), awaiting ✕/○, captured in a 7-snap series +
a 7,648,547-line / 540,313,630 B same-4-channel trace (SSD copy
sha-matched). Mid-session, WSL killed the Ubuntu userland ~17 times in
bursts (cause unidentified); all three single-shot runs completed in quiet
windows.

## T17-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T17; P-lane lease never touched) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; apt `xdotool` only) |
| ssx3 HEAD at commit | `f32e8b2` (plus unrelated untracked `tools/trace_align.py`, left alone) |
| Evidence commit | Below (`[T17]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly):

| Item | T4 value | T17 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes | yes |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| apt (WSL, as root) | `xdotool` 1:3.20160805.1-5build1 (key injection; T4 had installed `xvfb`+`x11-apps`+`netpbm`, all still present) |
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's stale read-only dir (as root, T4 recipe) before each Xvfb start; reverts on WSL restart |
| Xvfb | `:99 -screen 0 1280x1024x24`, started detached (`setsid nohup`), `xdotool getdisplaygeometry` → `1280 1024`; `pkill Xvfb` at teardown, verified gone |
| Dirs/files created | `/home/brad/pcsx2-t4/t17-*.sh`, `/home/brad/pcsx2-t4/t17*.jpg/.xwd`, `…/logs/emulog-pre-t17*.txt` + `boot-t17*.log/.stdout`, `C:\Users\bradr\pcsx2-t4\t17*` staging (scripts, snaps, `emulog-t17c.txt`) |
| Untouched | `.wslconfig` (`memory=10GB` intact), BIOS/ISO inputs, `PCSX2.ini` (no edits; defaults already map the pad + hotkeys) |

WSL session log (context for every timestamp below):

| # | UTC | Event | Receipt |
|---|---|---|---|
| 1 | 15:05:43 | WSL kernel booted (Hyper-V VmSwitch events; `btime 1789916743`, constant all session — kernel never rebooted) | `wevtutil`, `/proc/stat` |
| 2 | 15:05:45–15:20:24 | Ubuntu userland terminated + rebooted ~17× in bursts (kills at dmesg [62],[87],[142],[165],[188],[275],[313],[343],[398],[430],[452],[788],[856],[876]; each = `p9io.cpp AcceptAsync` exception → sdc remount → unclean journal → fresh init). Killed Xvfb+pcsx2 twice mid-run (boot-2 @~+75 s, boot-3 @~+112 s, incl. one kill during an 85 s zero-activity gap). Killer unidentified (see gap G2) | dmesg, init `etime 00:01`, dead pids, reverted `/tmp/.X11-unix`, 0-byte snap |
| 3 | 15:21–15:48 | Quiet: zero restarts; t17a (6 min), t17b (4 min), t17c (6 min), analysis, retrieval, teardown all completed | canary + run completions |
| 4 | clocks | WSL `date -u` verified against laptop true time (SSD copy mtime 11:47 EDT = 15:47 UTC vs concurrent WSL stamps 15:4x) — no skew; run-script wall stamps are true UTC. `wevtutil` renders local time with a `Z` suffix (11:05:44Z = 11:05:44 EDT = 15:05:44 UTC) | cross-check, do not subtract |

## T17-1. Task 1 — input path

### Path table (candidate key paths)

| # | Path | Try-order | Receipt |
|---|---|---|---|
| 1 | `xdotool` focus+XTEST → Xvfb `:99` | 1st | WORKS. `windowfocus --sync <WID>` + `key`/`keydown`/`keyup` to WID 2097159 (`SSX 3 [Devel]`, only visible window; no WM, so explicit focus, no `windowactivate`). Proof: SPACE toggles pause (trace flatlines 25 s + `Paused` OSD, t17b); held K advances the menu (t17c) |
| 2 | Pad ini mapping | 0th (pre-existing) | No edit needed: `[Pad1] Type=DualShock2`, `Cross = Keyboard/K` (full binding dump in §T17-3). Hotkeys likewise preset (`TogglePause=Space`, `ToggleTurbo=Tab`) |
| 3 | `xdotool key --window` (XSendEvent, focus-independent) | fallback | Not tried (path 1 worked first try). Script committed as `t17-press.sh` for a follower |
| 4 | PCSX2 input APIs / scripted movies | considered | No CLI/scriptable pad API in this build; not pursued |
| 5 | Kernel uinput | considered, rejected | Useless here: Xvfb does not read kernel evdev, and PCSX2-Qt reads keys via Qt/X11 — only X events can arrive |

### Park-match table (fresh boot reproduces T4's park?)

| Item | T4 (boot3) | T17 (t17a/b/c boots) | Match |
|---|---|---|---|
| Screenshot | `snap-language-select.jpg`, 35367 B, sha `b6ca1aa9…` | `t17-early`/`t17a-park`/`t17b-park`/`t17c-park`, all 35367 B, all sha `b6ca1aa9…` | BIT-IDENTICAL |
| BIOS line | line 2 | line 2 (`BIOS Found: USA v02.00(14/06/2004)`) | yes |
| ExecPS2 ×2 | lines 142369/142465 | lines 142369/142465 (log 0.8412/0.8688 vs T4 0.5720/0.5996 — times vary, lines identical) | lines yes |
| ReBootStart | line 142764 | line 142764 | yes |
| sceCdInit | line 405737 | line 405737 | yes |
| First vblank + LoadStartModule ×2 | lines 417152–417619 | first vblank @417152; LoadStartModule @417354/@417619 | yes |
| UpdateVSyncRate DVD NTSC | line 456475 | line 456475 | yes |
| First SIF / sceSifGetReg | lines 138615 / 138785 | lines 138615 / 138785 | yes |
| Vblank rate | 22,580 / 336 s ≈ 67.2/s | t17c: 23,107 / 341 s ≈ 67.8/s | yes |
| Vblanks at park snap (log ≤90) | not recorded by T4 | 6,108 (press at log ≤100: 6,777) | n/a (new datum) |
| Menu first seen | ≤283 s (first look) | ≤75 s (boot-2 `t17-early` already parked; T4 just looked late) | earlier bound |

Boot log prefix is deterministic to the line across runs (same build/inputs/flags); only log-times vary.

### Press table (the ✕ press)

Method for all: `xdotool windowfocus --sync 2097159` then XTEST keys (exit 0 each).
Menu-wall = seconds since boot launch (log-time ≈ same scale).

| Run | Press | Timing (UTC wall / menu-wall / kernel uptime) | Single-press proof | Screen effect |
|---|---|---|---|---|
| t17a | `key K` (tap, down→up ~18 ms: `.339→.357`) | 1789918048.34–.36 / T+100 / uptime 107 | one `key` invocation, exit 0 | NONE: 6 snaps (park,+10,+30,+60,+120,+240) all sha `b6ca1aa9` (park-identical) |
| t17b | `key space` ×2 (pause control, NOT the ✕ press) | pause T+120, resume T+155 | n/a (diagnostic) | `Paused` OSD on; trace bytes frozen 208,032,214 for 25 s, then growing — delivery proven |
| t17c | `keydown K`, 534 ms hold, `keyup K` (`.962→.496`) | T+100 (keydown 1789918723.96, keyup 1789918724.50) / uptime 782→783 | one down/up pair, exit 0 each; exactly one screen transition (no double-advance) | PARK BROKEN: new screen by +5 s (see T17-2) |

Finding: a ~18 ms tap lands between pad polls (no effect); a 534 ms hold (one pair of edges) registers. Hold threshold between 18 ms and 534 ms is unmapped (gap G4).

## T17-2. Task 2 — next-epoch capture (t17c run)

### Epoch table (screens reached after the t17c ✕ press at T+100)

| Snap (press-relative) | sha256 (short) | Screen content |
|---|---|---|
| park (T+90, pre-press) | `b6ca1aa9` | Language-select (bit-identical to T4) |
| +5 s | `927a031e` | NEW stable screen: `User Preferences / Language / English` (`◀ ▶`), `✕ Enter ○ Back`, no caption yet |
| +15 s | `224b0d90` | Same menu + `Select language.` caption (spinner rotated — animated) |
| +30 s | `e714eebe` | Same menu + caption (spinner rotated) |
| +60 s | `3d034f4a` | Same menu, caption ABSENT (caption blinks; gap G5) |
| +120 s | `29a31a80` | Same menu + caption |
| +240 s | `7ea1821d` | Same menu + caption (run end T+340, SIGTERM → clean shutdown) |

Guest/trace side: single DVD-NTSC mode throughout (one `UpdateVSyncRate`);
no new `LoadStartModule` after boot (2 total, both pre-press); menu loop
continues (sema/event/timer storm + per-vblank `sceCdApplySCmd2` ×23,078);
zero ERROR lines; shutdown markers `Pausing…`, `DEV9close`, `Unloading EGL`,
`Releasing host memory` at log 340.90–340.98.

### Trace table (same-4 channels, same ini, G2/G9 heeded)

| Trace (bytesize path `…/dat/PCSX2/logs/`) | Lines / bytes | sha256 | Second copy |
|---|---|---|---|
| `emulog.txt` = t17c (held ✕, T+340) | 7,648,547 / 540,313,630 | `4f61ea83…38749` | SSD `/Volumes/Extreme SSD/ps2x-t4/emulog-t17c.txt`, same size+sha (match) |
| `emulog-pre-t17b-…T153248Z.txt` = t17a (tap, no-op, T+340) | 7,581,760 / 535,682,684 | `b754c4db…1c06f` | bytesize only |
| `emulog-pre-t17c-…T153703Z.txt` = t17b (pause control, T+200) | 3,189,157 / 223,035,641 | `7dda30fc…9f0d4b` | bytesize only |
| `emulog-pre-t17-…T151753Z.txt` = boot-2 (killed by flap @~+75 s) | — / 125,924,723 | `01f18c93…94e456` | bytesize only |
| `emulog-pre-t17auto-…T152548Z.txt` = boot-3 (killed by flap @~+112 s) | — / 117,669,919 | not taken (sizes only) | bytesize only |
| `emulog-pre-t17-…T150727Z.txt` = T4 boot3 original (preserved, untouched) | 7,483,481 / 528,683,584 | `2433a33e…59c6a5` (re-verified at preserve) | SSD `emulog-boot3.txt` (T4) |

t17c channel census (T4 `t4-census.py`, same script): `EE.Bios` 914,791
(42 distinct names) · `IOP.Bios` 5,211,292 (103 distinct) · `MISC.sif`
936,164 · CDVD 447,901 · other 138,399 · 10 EE threads · vblanks 23,107.
Format check vs T4 `samples.txt` (line numbers + timestamps normalized):
identical except total-lines header and two SIF fifo `pos` data values
(52 vs 48) — same-4 format confirmed. Committed: `t17-census.txt`
(9560 B), `t17-samples.txt` (5878 B).

### Park table (first new stable park)

| Item | Value |
|---|---|
| Screen | User Preferences, Language = English (◀ ▶), `✕ Enter ○ Back` (+ blinking `Select language.` caption) |
| Awaiting | ✕ (confirm English) or ○ (back to language-select) |
| Reached by | +5 s post-press (T+105), held through +240 s (T+340, run end) |
| Vblanks at new park | ≤7,451 at log 110 (first post-press mark); 23,046 at log 340 |
| 1200 s cap | Not reached — stopped at first new stable park per brief (T+340) |

## T17-3. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote via
`ssh bytesize "…"` (Windows cmd) or `ssh bytesize "wsl …"` (WSL); all
remote phases sequential, one ssh at a time after the flap onset):

```
# reuse verification
ssh bytesize "wsl sha256sum /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt"  # 6719f5d6…ee327
ssh bytesize "wsl stat -c %s …/bin/pcsx2-qt"                              # 130929856
ssh bytesize "wsl git -C /home/brad/pcsx2-t4/pcsx2 rev-parse HEAD"         # 9056c08349…
ssh bytesize "wsl git -C … status --short"                                # (empty)
ssh bytesize "wsl ls -la /home/brad/pcsx2-t4/inputs/ …/dat/PCSX2/bios/"    # sizes
# key injection + display
ssh bytesize "wsl -u root apt-get -y install xdotool"                     # 3.20160805.1
ssh bytesize "wsl which xdotool xwd xwdtopnm pnmtojpeg"                   # all present
ssh bytesize "wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix"
ssh bytesize "wsl setsid nohup Xvfb :99 -screen 0 1280x1024x24"
ssh bytesize "wsl env DISPLAY=:99 xdotool getdisplaygeometry"             # 1280 1024
# bindings (no edits)
ssh bytesize "wsl sed -n 550,630p …/inis/PCSX2.ini"                       # Cross=Keyboard/K …
ssh bytesize "wsl grep -n -A 40 '\[Hotkeys\]' …/inis/PCSX2.ini"           # Space/Tab …
# scripts (written locally under local/research/T17/, staged per file)
scp <file> "bytesize:pcsx2-t4/" ; ssh bytesize "wsl cp /mnt/c/Users/bradr/pcsx2-t4/<file> /home/brad/pcsx2-t4/"
#   t17-boot.sh t17-snap.sh t17-windows.sh t17-press.sh (helpers; press.sh = untried --window candidate)
#   t17-auto.sh (t17a: tap) t17b-auto.sh (pause control) t17c-auto.sh (held ✕) t17-analyze.sh t17-vcount.sh
# runs (each ONE ssh; full stdout in session log; key lines in §T17-1/2)
ssh bytesize "wsl bash /home/brad/pcsx2-t4/t17-boot.sh"                   # boot-2 ok, killed by flap; boot-1 earlier aborted (no X: flap had killed Xvfb)
ssh bytesize "wsl bash /home/brad/pcsx2-t4/t17-auto.sh"                   # t17a T17_AUTO_DONE
ssh bytesize "wsl bash /home/brad/pcsx2-t4/t17b-auto.sh"                  # t17b T17B_DONE
ssh bytesize "wsl bash /home/brad/pcsx2-t4/t17c-auto.sh"                  # t17c T17C_DONE
# retrieval per snap set (remote stage + scp home; hashes local)
ssh bytesize "wsl cp /home/brad/pcsx2-t4/t17*.jpg /mnt/c/Users/bradr/pcsx2-t4/"
scp "bytesize:pcsx2-t4/t17a-*.jpg" local/research/T17/ ; shasum -a 256 …
# (same for t17b-*, t17c-*, t17-census.txt, t17-samples.txt)
# trace analysis + arch
...[truncated 2747 chars]