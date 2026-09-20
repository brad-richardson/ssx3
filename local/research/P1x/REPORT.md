# P1x report — PCSX2 reference trace of the real boot (read-only; negative result)

Read-only research. No fork writes, no fork boots, no lease, no `adb`, no
downloads, no `git push`. The trace could not be produced headless on this
host; the exact blockers + cheapest path below ARE the deliverable per the
brief. Wall: one session ending 2026-09-20 00:12 UTC, inside the 4-hour box.

Paths: `REF = /Volumes/Extreme SSD/pcsx2-ref` (PCSX2 source @ `1275b25a`,
unbuilt, never modified), `APP = /Applications/PCSX2-v2.8.2.app`
(installed, x86_64-only), `W = /Volumes/Extreme SSD/ps2recomp-spike`,
scratch `/Volumes/Extreme SSD/ps2x-p1x/` (created, holds no artifacts —
every operation this session was a read-only query plus two receipt files
under `$W/P1/ref/`).

## P1x-0. Inputs read

| Item | Value |
|---|---|
| The ask | `docs/research/review-2026-09-19-progress.md` §7.3 (lines 221–226): PCSX2 EE syscall/thread/CD runtime trace to first menu frame, stored under `$W/P1/ref/`, so each future park starts from fork-vs-reference histogram divergence |
| Fork skeleton | `local/research/P1/REPORT.md` Part 23 `## P23-2` (lines 7682–7885); the ordered skeleton is `### d. Epoch order` (lines 7751–7774) = §P23-2d; histogram shapes are `### b` thread table (sch series, lines 7713–7730), `### c` signal/wait group-bys (lines 7732–7749), stub histograms (`### e/f`, lines 7776–7833) |
| Prior source read | `local/research/P2/REPORT.md` (all 615 lines): PCSX2 is LLE, EE `SYSCALL()` logs every call name via `BIOS_LOG` then traps to the real BIOS (`R5900OpcodeImpl.cpp:908-920`); P2 never executed anything |
| Live PCSX2 state | `~/Library/Application Support/PCSX2/inis/PCSX2.ini` (`[EmuCore/TraceLog]` all-false lines 395–430, `[Filenames] BIOS` line 456, `[Folders] Bios` line 21) and `logs/emulog.txt` (Sep 10 session: see P1x-1) |

## P1x-1. Environment receipts

| # | Item | Receipt |
|---|---|---|
| 1 | Host | macOS 27.0 build 26A428, `arch` = arm64, `machdep.cpu.brand_string` = Apple M4, `sysctl.proc_translated` = 0 |
| 2 | Installed emulator | `APP/Contents/MacOS/PCSX2`: `Mach-O 64-bit executable x86_64` (`file`); `CFBundleShortVersionString`/`CFBundleVersion` = v2.8.2; no `LSArchitecturePriority` key; only PCSX2 in `/Applications` and `~/Applications` |
| 3 | Reference clone | `REF` @ `1275b25ac02dc8138a0c43ec91bfc2c2df831f94` (`git log` works; ExFAT AppleDouble `._*.idx` sidecar noise, non-fatal); no `build/` dir; `bin/` is source subdirs (docs/resources/utils), not binaries |
| 4 | BIOS (preferred, in-repo, read-only) | `local/emulator/course-cleanup/profile/PCSX2/bios/ps2-bios-0200a-20040614-100909.bin`, 4194304 B, sha256 `6d23d001…be4744` (full in `$W/P1/ref/inputs.sha256`) |
| 5 | BIOS second copy | `/Volumes/share/brad/games/ps2/ps2-bios-0200a-20040614-100909.bin`, 4194304 B, same sha256 (`6d23d001…be4744`) |
| 6 | Game ISO (preferred) | `/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso`, 3005415424 B = 1467488 × 2048 (matches emulog's sector count), sha256 `3c2f8eb1…9761ebf5` |
| 7 | Game ISO second copy | `/Volumes/share/brad/games/ps2/SSX 3 (USA).iso`, same size, same sha256 (`3c2f8eb1…9761ebf5`) |
| 8 | Prior success on this host class | `logs/emulog.txt` Sep 10: same APP booted the same serial (`SLUS-20772`, CRC `08FFF00D`, entry `0x00100008`) under `Apple M4 (Rosetta)`, Darwin 25.6.0; `BIOS Found: USA v02.00(14/06/2004)`; ran ~44 s to pause + savestate. Proves inputs are good and the game boots under PCSX2; thetranslator is what changed (see P1x-5 B1) |
| 9 | Build deps for any local compile | `cmake` + `ninja` installed (Homebrew); Qt absent everywhere (`/opt/homebrew/Cellar` full listing has no `qt*`; no `~/Qt`, `/usr/local/Qt*`, `/opt/Qt*`, no Qt-named app); SDL2/SDL3 present. Any pcsx2-qt build needs downloads (outside this brief's rules) |

## P1x-2. Survey: how to run PCSX2 with logging (reference-source flags)

All options single-dash (no `--batch`/`--nogui` long forms exist). Help text
verbatim from `REF/pcsx2-qt/QtHost.cpp:2127-2163`; parsing at `:2173-2360`.

| # | Option | Source receipt | Headless? |
|---|---|---|---|
| 1 | `-batch` | `:2134` "Enables batch mode (exits after shutting down)"; sets `s_batch_mode` (`:2200-2204`); without autoboot it errors (`:2361-2369`) | Still full Qt app + GS window (see row 9) |
| 2 | `-nogui` | `:2135` "Hides main window while running (implies batch mode)"; sets both flags (`:2205-2210`) | Hides only the main window; app/event-loop/GS window remain (row 9) |
| 3 | positional `[boot filename]` | `:2130` `Usage: {} [parameters] [--] [boot filename]`; no-boot + batch/nogui is an error (`:2347-2369`) | The ISO path goes here |
| 4 | `-logfile <path>` | `:2141` "Writes the application log to path instead of emulog.txt"; `VMManager::Internal::SetFileLogPath` (`:2258-2262`) | The capture sink; works in any build |
| 5 | `-elf <file>` | `:2138` boot-ELF override (`:2242-2244`) | Alternative entry; not the disc boot |
| 6 | `-fastboot` / `-slowboot` | `:2143-2144`; force `fast_boot` (`:2222-2231`) | Slowboot keeps the full BIOS sequence (preferred for a reference) |
| 7 | `-turbo` / `-unlimited` | `:2154-2155` fast-forward after start | Speeds a scripted run to menu |
| 8 | `-debugger` | `:2153` "Open debugger and break on entry point" (`:2543-2547`) | GUI debugger; no CLI scripting surface in evidence |
| 9 | No true headless flag | `main()` `:2463` unconditionally constructs `PCSX2MainApplication app(argc, argv)` (`:2477`) and `MainWindow` (`:2521-2522`); `-nogui` only skips `show()` (`:2530-2536`); runs `app.exec()` (`:2556`). No `-surfaceless`/`-offscreen` flag in `ParseCommandLineOptions`; no `QT_QPA_PLATFORM` handling in `pcsx2-qt/` (searched) | A display server is mandatory even with `-nogui` |
| 10 | `pcsx2-gsrunner -surfaceless` | `REF/pcsx2-gsrunner/Main.cpp:432` + `:717-721`; harness `test_run_dumps.py:53-54` runs it surfaceless | GS-dump (`.gs`) playback only, no EE/ISO boot — not a boot-trace vehicle |
| 11 | Xvfb | No X11 path on macOS (Qt Cocoa + Metal GS; emulog shows Metal on Apple M4) | Not applicable on this host |

## P1x-3. Survey: log channels for the boot sequence

Channels are ini-only (`[EmuCore/TraceLog]`, `REF/pcsx2/Pcsx2Config.cpp:229-268`;
key names confirmed live in `PCSX2.ini:395-430`). Descriptions from
`REF/pcsx2/SourceLog.cpp`.

| # | Channel (ini key) | What it logs | Source receipt | In Release? |
|---|---|---|---|---|
| 1 | `EE.bios` | Every EE syscall name: `Bios call: <name> (<num>)` incl. thread syscalls | `BIOS_LOG` = `macTrace(EE.Bios)` (`Debug.h:226`); emit at `R5900OpcodeImpl.cpp:917`; desc "SYSCALL and DECI2 activity" (`SourceLog.cpp:121`) | NO — see row 6 |
| 2 | `IOP.bios` | IRX imports (`lib.index: func (a0..a3)`) | `PSXBIOS_LOG` = `macTrace(IOP.Bios)` (`Debug.h:245`); emit `IopBios.cpp:1413`; desc "SYSCALL and IRX activity" (`SourceLog.cpp:164`) | NO — row 6 |
| 3 | `IOP.cdvd` | CDVD hardware detail | desc "Detailed logging of CDVD hardware" (`SourceLog.cpp:186`); key `Pcsx2Config.cpp:264` | NO — row 6 |
| 4 | `MISC.sif` | EE↔IOP SIF traffic | `SIF_LOG` (`Debug.h:224`); key `Pcsx2Config.cpp:267` | NO — row 6 |
| 5 | Release-available log | ELF/CDVD-disc/Pad/GameDB lines (the emulog.txt shape) + game `printf` via `sysPrintOut` (`R5900OpcodeImpl.cpp:1138-1144`, gated by ini `EnableEEConsole`, not by DEVBUILD) | `ConsoleLogFromVM` (`Debug.h:119-122`); emulog Sep 10 session as sample | YES — but no per-syscall/thread/CD-event sequence |
| 6 | Master gate | `TraceActive(trace)` = `TraceLogging.trace.IsActive()` **only under `PCSX2_DEVBUILD**, else `(false)` (`Debug.h:216-220`); `IsActive()` = `EmuConfig.Trace.Enabled && Enabled` (`Debug.h:67-70`); `PCSX2_DEVBUILD` is defined **only for Debug and Devel CMake configs** (`cmake/BuildParameters.cmake:267-268`) | — | Release builds (incl. APP v2.8.2) compile every `*_LOG` in rows 1–4 to dead code |

Net of P1x-2 + P1x-3: the reference boot sequence needs a **Devel (or
Debug) build** + display session + `-nogui -slowboot -logfile` + ini
`Enabled/EE.bios/IOP.bios/IOP.cdvd/MISC.sif = true`. None of that exists on
this host today.

## P1x-4. Capture attempts (exact commands, wall time, exit)

| # | Command | Result |
|---|---|---|
| 1 | `"/Applications/PCSX2-v2.8.2.app/Contents/MacOS/PCSX2" --help` | `/bin/sh: …/PCSX2: Bad CPU type in executable` (exit via shell, no output). The installed Mach-O is x86_64-only; the arm64 kernel has no translator to hand it to |
| 2 | `/usr/bin/arch -x86_64 /usr/bin/true` | `arch: posix_spawnp: /usr/bin/true: Bad CPU type in executable`, rc=1. Proves the failure is translator absence, not the app bundle |
| 3 | `ls /Library/Apple/usr/libexec/oah/` + `pgrep oahd` | Contains only `RosettaLinux`; no `oahd` process. Corroborates #2 |
| 4 | `file` + PlistBuddy (P1x-1 rows 1–2) | Binary x86_64-only, bundle v2.8.2, no arch-priority override |

Wall time: attempt #1 fails at `exec` (<1 s). No PCSX2 process ever started;
no log, no window, no crash report. Furthest obtainable on this host: the
three receipts above.

## P1x-5. Blockers (each independently fatal) + cheapest path

| # | Blocker | Receipt |
|---|---|---|
| B1 | Installed binary cannot execute: x86_64-only on arm64 without Rosetta | P1x-4 rows 1–4. (Sep 10 emulog proves Rosetta + this app + these inputs worked on Darwin 25.6.0; today macOS 27.0 exec fails.) Restoring Rosetta = downloading a runtime: forbidden by this brief, needs the user + `softwareupdate` |
| B2 | Installed build is Release: all needed trace channels compile out | P1x-3 row 6. Even with Rosetta, APP could only emit emulog-shape lines (row 5), never the syscall/thread/CD sequence the fork must diff against |
| B3 | No headless ISO boot in pcsx2-qt: `-nogui` still needs a display server | P1x-2 row 9. Even with B1+B2 solved, capture needs a GUI session (scripted or attended), not an ssh/herdr-pane-only run |

Cheapest path ranking (for a future brief or the user; all outside P1x rules):

| Order | Path | Cost / caveat | Receipt |
|---|---|---|---|
| 1 | Build REF **Devel** for **arm64**, run P1x-7 recipe in a GUI session | One Qt6+deps download + one full build; NO Rosetta needed; **but** REF warns Apple Silicon has no EE/VU/IOP recompilers and runs VERY slow (`CMakeLists.txt:84-92`) — acceptable for a trace, and CI already builds an arm64 Qt artifact (`macos_build_matrix.yml:21-27`) | `BuildParameters.cmake:113-116`; `macos_build_matrix.yml` |
| 2 | User restores Rosetta, then build REF **Devel** for **x86_64** (`-DCMAKE_OSX_ARCHITECTURES=x86_64`, the documented default per `CMakeLists.txt:90`) and run P1x-7 | Same build cost + user action + runtime download; full-speed recompilers | `CMakeLists.txt:84-92` |
| 3 | Source patch instead of Devel (e.g. force-enable `EE.Bios` in Release) | Still a full Qt build + Rosetta; weakens reference purity for zero cost saving vs path 2 | `Debug.h:216-220` |
| 4 | Scripted-GUI-only on APP as-is (running under restored Rosetta) | Cheapest in build terms (no compile) but yields only emulog-shape lines, NOT the syscall/thread/CD sequence — does not satisfy §7.3 | P1x-3 row 5 |

Not paths: Xvfb (P1x-2 row 11); gsrunner (row 10); `-debugger` scripting (no
CLI surface, row 8); reinstalling anything inside this brief (forbidden).

## P1x-6. Distill: fork→reference map in the §P23-2d shape (template + gaps)

No trace bytes exist, so the ordered table + histogram are given as the exact
mapping a future capture fills in: each fork row, the reference channel that
diffs against it, and the line format to grep.

| Fork row (§P23-2) | Reference source (Devel log) | Line format / grep |
|---|---|---|
| d. Epoch order (syscall/thread/CD skeleton, `:604-:680`) | `EE.bios` + `IOP.bios` + `IOP.cdvd` interleaved by timestamp | `Bios call: <name> (<hex>)` (`R5900OpcodeImpl.cpp:917`); `<lib>.<idx>: <func>` (`IopBios.cpp:1413`); CDVD lines (`IOP.CDVD`, `SourceLog.cpp:186`) |
| b. Steady-state thread table (sch series per thread) | GAP — PCSX2 has no thread-switch trace channel (channels list, `SourceLog.cpp:113-240`); thread events visible only as `CreateThread`/`StartThread`/`ChangeThreadPriority`/`SleepThread`/`WakeupThread` names in `EE.bios` | grep `Bios call` for the thread-syscall names; no scheduler counts exist to diff sch series against |
| c. Signal/wait group-bys (sema ids, counts, sites) | `EE.bios` syscall names (`CreateSema`/`SignalSema`/`WaitSema`/`PollSema`/`iSignalSema`…) — order + relative counts only; no args/return values in the log line | `Bios call: CreateSema` etc.; counts comparable, ids/sites NOT (BIOS owns semaphores; PCSX2 never sees ids — P2 Q1–Q2) |
| e/f. Stub/poll histograms (`0x425cf0` spin, outer-loop ras) | GAP — needs per-pc execution counts; closest channel is `EE.r5900` full disasm (`SourceLog.cpp:125`), enormous volume, no histogram aggregation in-tree | Would need post-processing of `EE.r5900` (or the debugger) — out of scope for the capture brief |
| h. CD reads total (21) + callback `:611/:613` | `IOP.cdvd` + `EE.bios` (`sceCd*` are EE lib calls, not syscalls — visible only via IOP-side `cdvdman` IRX traffic in `IOP.bios`) | cross-check `IOP.cdvd` read count vs fork's 21; callback delivery is a hardware IRQ into BIOS+guest code (P2 Q3), so no fork-comparable callback line exists |

Histogram-shape note: the fork's §P23-2b/c tables count runtime-internal
events (scheduler runs, sema ids, guest ras). PCSX2's observable reference is
a flat timestamped syscall/IRX/CD line stream plus counts derivable from it.
The directly diffable artifacts are (a) the epoch-order event sequence and
(b) per-syscall-name counts — both strict subsets of §P23-2b/c/d. A future
park brief diffs those two and treats thread-table/sch-series rows as
fork-only (gap rows above).

## P1x-7. Capture recipe for the future run (not executed)

Preconditions: path 1 or 2 from P1x-5 built; GUI session available.

```sh
# 1. Point a portable data dir at the verified inputs (keeps ~/Library untouched).
DAT=/Volumes/Extreme\ SSD/ps2x-p1x/datadir  # or any writable dir
# 2. Enable the channels: in $DAT/inis/PCSX2.ini set
#    [EmuCore/TraceLog]: Enabled=true, EE.bios=true, IOP.bios=true,
#    IOP.cdvd=true, MISC.sif=true   (keys: Pcsx2Config.cpp:229-268)
#    [Logging]: EnableFileLogging=true
#    [EmuCore]: EnableFastBoot=false   # slowboot keeps the full BIOS sequence
#    [Filenames]: BIOS=ps2-bios-0200a-20040614-100909.bin with
#    [Folders]: Bios=<dir holding the P1x-1 row-4 file>
# 3. Boot headless-ish to the first menu frame, log to the canonical path:
/Applications/PCSX2-Devel.app/Contents/MacOS/PCSX2 -nogui -slowboot \
  -datapath "$DAT" -logfile "$W/P1/ref/boot-ssx3-slowboot.log" \
  -- "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"
# 4. Distill: grep the P1x-6 formats into the epoch table + per-name counts;
#    sha256sum the log next to it; append a Part to P1/REPORT.md (that brief
#    owns it, not P1x).
```

Why this shape: `-nogui` implies batch (exit after shutdown, `QtHost.cpp:2205-2210`)
but keeps the display/GS path (P1x-2 row 9); `-slowboot` preserves the BIOS
prefix the fork's skeleton starts from; `-logfile` is the only stdout-free
sink (`:2258-2262`); `-turbo` may be added after the ELF-entry line appears.

## P1x-8. Exact commands run (this session, all read-only)

```
# identity / receipts
arch; file "/Applications/PCSX2-v2.8.2.app/Contents/MacOS/PCSX2"
ls /Library/Apple/usr/libexec/oah/; pgrep -l oahd; sysctl -n sysctl.proc_translated
sw_vers | head -3; sysctl -n machdep.cpu.brand_string; date -u +%Y-%m-%dT%H:%M:%SZ
/usr/libexec/PlistBuddy -c "Print CFBundleShortVersionString" /Applications/PCSX2-v2.8.2.app/Contents/Info.plist
/usr/libexec/PlistBuddy -c "Print CFBundleVersion" /Applications/PCSX2-v2.8.2.app/Contents/Info.plist
git -C REF log --oneline -3   # AppleDouble idx noise, non-fatal; HEAD 1275b25a
# capture attempts (P1x-4)
"/Applications/PCSX2-v2.8.2.app/Contents/MacOS/PCSX2" --help
/usr/bin/arch -x86_64 /usr/bin/true; echo rc=$?
# inputs (preferred paths from the user pointer + share mirrors)
stat -f '%z %N' /Volumes/share/.../ps2-bios-0200a-20040614-100909.bin /Volumes/share/.../"SSX 3 (USA).iso" "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"
shasum -a 256 <bios share> <iso spike> ; shasum -a 256 <iso share>
stat -f '%z %N' ssx3/local/emulator/course-cleanup/profile/PCSX2/bios/ps2-bios-0200a-20040614-100909.bin && shasum -a 256 <same>
ls /Volumes/share/brad/games/ps2/ ; ls /opt/homebrew/Cellar/ | tr '\n' ' ' ; which cmake ninja brew qmake6 qmake
# dirs created (only writes outside the evidence dir)
mkdir -p "/Volumes/Extreme SSD/ps2x-p1x" "/Volumes/Extreme SSD/ps2recomp-spike/P1/ref"
# source survey: rg/file reads only (receipts inline as REF/<path>:<line>)
```

Survey reads (all `REF/…`, quoted inline above): `pcsx2-qt/QtHost.cpp`
(usage `:2127-2163`, parse `:2173-2360`, `main :2463-2566`),
`pcsx2-gsrunner/Main.cpp` (usage `:412-440`), `pcsx2/DebugTools/Debug.h`
(`:47-70`, `:212-250`), `pcsx2/SourceLog.cpp` (channels `:113-240`),
`pcsx2/Pcsx2Config.cpp` (`:227-310`), `pcsx2/R5900OpcodeImpl.cpp`
(`:917`, `:1138-1144`), `pcsx2/IopBios.cpp` (`:1411-1416`),
`cmake/BuildParameters.cmake` (`:81-142`, `:267-268`),
`CMakeLists.txt` (`:84-92`), `.github/workflows/macos_build_matrix.yml`,
`pcsx2-qt/MainWindow.cpp` (surfaceless `:714-745`, `:1511-1525` — runtime
display toggle, no CLI flag).

## P1x-9. What I could not do

- Produce any trace bytes: B1+B2+B3 (P1x-5) each independently prevent it; no
  `--help` receipt exists because the binary cannot exec (help text is cited
  from source instead, verbatim).
- Verify `~/Downloads/PS2_BIOS/` (the path `PCSX2.ini [Folders] Bios`
  resolves to): every access (`ls`, file search) hung without output and was
  abandoned; irrelevant — the in-repo BIOS (P1x-1 row 4) is verified and
  byte-identical to the share copy.
- Confirm whether an x86_64 host exists anywhere off this machine (none in
  evidence), or when/why Rosetta left this host (Sep 10 emulog shows it
  present on Darwin 25.6.0; today macOS 27.0 exec fails) — both user questions.
- Fill the §P23-2-shaped event table/histogram with reference counts (no
  trace); P1x-6 gives the exact fill-in map + gap rows instead.
- Anything requiring downloads, builds, GUI scripting, fork contact, or a
  push: all outside the brief's rules, none attempted.

## Receipt paths

- This report: `ssx3 local/research/P1x/REPORT.md` (STANDALONE; `P1/REPORT.md`
  untouched — peer brief owns it)
- Blocker marker + input hashes: `$W/P1/ref/P1x-BLOCKED.txt`,
  `$W/P1/ref/inputs.sha256` (no trace bytes; absence recorded with reasons)
- Scratch: `/Volumes/Extreme SSD/ps2x-p1x/` (created, empty by design)
- Inputs: P1x-1 rows 4–7; app + ref rev: rows 2–3
