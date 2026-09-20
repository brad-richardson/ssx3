# I6 — Bundle ID fix: set identifier, rebuild sim .app, re-run install+launch (tables, no verdicts)

- Date: 2026-09-19/20. Runbook `local/muse/prompts/I6.md` (I5 gap 1's exact next brief). Tables, no verdicts.
- I5 (`local/research/I5/REPORT.md`, all of it: install exit 13, the 19-key Info.plist with no `CFBundleIdentifier`, the static entry table, the 4 gap rows) read first.
- Fork: `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`, `53bac61` → `bdae295` (`CMake: set iOS bundle identifier for the sim .app (I6)`). Pushed `53bac61..bdae295` to `fork ssx3` (`ls-remote` confirms `bdae295`, first try). The push also published P-lane's already-committed `8d10619` (P23-1, final message + trailers), which sat unpushed in the shared clone; `register_functions.cpp` stayed `M` (unstaged) throughout and was never staged. Only `ps2xRuntime/CMakeLists.txt` staged/committed.
- Product: `/Volumes/Extreme SSD/ps2x-i6/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app` (binary `ps2EntryRunner`, 120264208 bytes, Mach-O 64-bit arm64). Fresh dir; nothing reused from `ps2x-i4` except read-only `-DSDL2_DIR` / `-DFETCHCONTENT_SOURCE_DIR_RAYLIB` inputs.
- Rules honored: no PS2 boots → no lease; builds `-jobs 4`; Simulator = installed iOS 27.0 runtime + existing iPhone 17 `4DE6C37C-77EF-45AE-827E-26286E68D022` only, no substitution, no downloads, booted by me, shut down at end; build + logs under `/Volumes/Extreme SSD/ps2x-i6/` (new dir); `/tmp/p1-link`, `/tmp/ps2xgs-build*`, `/tmp/ps2x-ios-spike`, `ps2x-i3`, `ps2x-i4` (read-only inputs only), other agents' dirs never written; evidence `local/research/I6/` committed with `git add -f`, prefix `[I6]`, trailer `Orchestrated-By: Muse Code`; no `git push` in ssx3; no screenshots committed (none taken — reasoned below).
- Outcome shape: install now succeeds (exit 0); `main` runs. No-arg launch fatals cleanly on the missing ELF path; argv-probe launch reaches raylib/SDL init, SDL video init fails, and the process SIGSEGVs in `rlLoadTexture` (crash report captured). No window ever appeared.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i6/`, `APP` = the rebuilt Release `.app` above, `UDID` = `4DE6C37C-77EF-45AE-827E-26286E68D022`, `FORK` = fork clone.

## Step 1 — Minimal fork edit

Choice: `MACOSX_BUNDLE_GUI_IDENTIFIER` on `ps2EntryRunner`, guarded by `PS2X_IS_IOS` (I4's desktop-inert pattern). No `MACOSX_BUNDLE` change: Xcode-generator iOS executables are already bundles (I5's `.app` had `CFBundlePackageType=APPL`), so only the identifier was missing. Verified pre-edit that fork `ps2xRuntime/CMakeLists.txt` still sets no bundle identifier (only the `install() BUNDLE DESTINATION` comment at lines 617–626; line drift of −1 vs I5's 618–625).

```diff
@@ -614,6 +614,16 @@ if(PS2X_IS_ANDROID)
     target_sources(ps2EntryRunner PRIVATE src/lib/ps2_android_runtime.cpp)
 endif()

+if(PS2X_IS_IOS)
+    # I6: simctl install requires a CFBundleIdentifier (was: install exit
+    # 13 "Missing bundle ID"). Xcode-generator iOS executables are always
+    # bundles, so only the identifier is needed. Desktop-inert: PS2X_IS_IOS
+    # is OFF when CMAKE_SYSTEM_NAME is Darwin.
+    set_target_properties(ps2EntryRunner PROPERTIES
+        MACOSX_BUNDLE_GUI_IDENTIFIER "org.ps2x.ps2entryrunner"
+    )
+endif()
+
 if(APPLE)
```

| Item | Receipt |
|---|---|
| Diff | One hunk, 10 insertions, `ps2xRuntime/CMakeLists.txt` only (`logs/fork-commit.log`) |
| Commit | `bdae295` subject + body; P-lane file never staged (`status` shows only its pre-existing `M`) |
| Trailers | `Co-Authored-By: Muse Code <muse-code@users.noreply.github.com>` + `Muse-Session: striped-proteus (01a0bc11-…)`. Deviation recorded: the runbook's "copy the two trailers" names a specific Claude session (`session_01H9…`) that is not this run, so verbatim copy would misattribute; shape kept, values honest |
| Pull --rebase | Attempted; refused (`cannot pull with rebase: You have unstaged changes` — P-lane's file, which this brief must not touch). Proven no-op instead: fresh `fetch fork ssx3`, then `fork/ssx3` is an ancestor of HEAD and `HEAD..fork/ssx3` is empty (remote strictly behind) |
| Push | `git push fork ssx3` → `53bac61..bdae295`, first try; `ls-remote` confirms `bdae295` (`logs/fork-push.log`). Push issued ONLY in the fork clone to the `fork` remote |

## Step 2 — Rebuild

Same I4 configure shape, fresh `W/ios-runtime-rel` (`-G Xcode`, I1 `ios-simulator.toolchain.v2.cmake`, `CMAKE_CONFIGURATION_TYPES=Release`, `RECOMP/ANALYZER/TEST/STUDIO OFF`, `SCCACHE OFF`, `-DSDL2_DIR=W-i4/sdl2-ios-sim/lib/cmake/SDL2`, `-DFETCHCONTENT_SOURCE_DIR_RAYLIB=W-i4/raylib-5.5`). Env `CC=/opt/homebrew/opt/llvm/bin/clang`, `CXX` unset (matches I4's runtime-configure provenance). Build `--config Release -- -jobs 4`. The tree includes P-lane's unstaged `register_functions.cpp` WIP, as in I4.

| Item | Receipt |
|---|---|
| Configure | Exit 0: `Configuring done (71.9s) / Generating done (19.5s)` (`logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, 0 errors, 5m20s (`logs/ios-runtime-build-tail.log`; full 1.0 MB log stays in `W/logs/`) |
| Binary | 120264208 bytes (I4: 120264240, −32), Mach-O 64-bit arm64 |
| Entry symbols | `T _main`, `T _SDL_Init`, `T _InitWindow` present; `_SDL_main`, `_SDL_UIKitRunApp`, `_UIApplicationMain` absent — reproduces I5 baseline (`logs/nm-entry.log`) |
| SDL count | 292 `T _SDL_` symbols — matches I4/I5 (`logs/nm-sdl-count.log`) |
| Link set | libSystem + SDL iOS frameworks (UIKit, OpenGLES, Metal, AVFoundation, …) — matches I5 (`logs/otool-L.log`) |
| Signature | Adhoc, `TeamIdentifier=not set`; `Identifier=org.ps2x.ps2entryrunner` (was derived `ps2EntryRunner-5555…`); `Info.plist entries=20` (`logs/codesign.log`) |
| `CFBundleIdentifier` | `org.ps2x.ps2entryrunner` in the built `.app/Info.plist` (was: absent). Mechanism: Xcode project sets `INFOPLIST_FILE` to CMake's generated plist, which now carries the identifier (`logs/Info.plist.txt`) |
| Warnings | 81 total, 19 unique texts (I4: 80, untriaged). New-by-construction: `User-supplied CFBundleIdentifier value 'org.ps2x.ps2entryrunner' in the Info.plist must be the same as the PRODUCT_BUNDLE_IDENTIFIER build setting value ''`. Rest untriaged (dominated by `-Wshorten-64-to-32`, 60 of 81) |

`Info.plist` key delta vs I5's 19-key inventory: +`CFBundleIdentifier` = 20 keys. `CFBundleVersion`/`CFBundleShortVersionString`/`CFBundleName`/storyboards/scene manifest/`UIRequiredDeviceCapabilities` remain absent (observed, not blockers — install exit 0).

## Step 3 — I5 Steps 1–3 re-run

### Install

| Item | Receipt |
|---|---|
| Runtime / device | iOS 27.0 runtime installed, nothing downloaded; iPhone 17 `4DE6C37C-…` was `(Shutdown)`; no substitution |
| Boot | `simctl boot` exit 0 (`logs/boot.log`, empty); `bootstatus -b` exit 0, `Finished` (`logs/bootstatus.log`) |
| Install | `simctl install` exit 0 (`logs/install.log`, empty = no stderr) |
| Listing | `listapps` shows `org.ps2x.ps2entryrunner`, `ApplicationType = User`, bundle + data containers provisioned |
| Data container | Fresh `Library/{Preferences,Caches}`, `Documents`, `tmp`, `SystemData` — nothing written by the app (it never got past init) |

### Launch attempts

Four launches, two harness failures then two real measurements:

| # | Command shape | Result |
|---|---|---|
| 1 | `launch --stdout=W/… --stderr=W/…` (external volume) | Exit 3, `NSPOSIXErrorDomain code=3`, `did not return a process handle` (`logs/launch.log`). No stdout/stderr files created |
| 2 | Retry of #1 | Exit 3, `FBSOpenApplicationServiceErrorDomain code=3`, `Process failed to launch` |
| 3 | `launch --console` (shell redirect to `W/…`), no argv | Exit 0 in ~1s; process ran and `_Exit(1)`'d (see console text). No crash report |
| 4 (probe) | `launch --console` with argv `["/nonexistent-boot.elf"]` | Exit 0 in ~1s; process ran, SDL init failed, SIGSEGV (see console text + crash report) |

Root cause of #1/#2 (harness, not the app): `launchd_sim` runs as `mobile` and cannot open redirect paths on the external ExFAT volume:

```text
launchd_sim: Service could not initialize: Unable to open stdout path
(/Volumes/Extreme SSD/ps2x-i6/logs/launch2-stdout.log), error 0x1 - Operation not permitted
```

followed by `runningboardd: job failed to spawn` and `SpringBoard: Bootstrapping failed … RBSRequestErrorDomain code 5` (`logs/logshow-ps2.log`, `logs/logshow-launch.log`). Same sandbox wall blocks `simctl io screenshot` to the external volume (`NSCocoaErrorDomain code=513 … Operation not permitted`); the fix used here is `--console` with a shell redirect (shell writes fine) — proven by #3/#4.

### Log excerpts (console texts are complete — first+last 100 subsume them)

`logs/launch.log` (attempt #1, complete, 331 bytes):

```text
An error was encountered processing the command (domain=NSPOSIXErrorDomain, code=3):
Simulator device failed to launch org.ps2x.ps2entryrunner.
No such process
Underlying error (domain=NSPOSIXErrorDomain, code=3):
	Application launch for 'org.ps2x.ps2entryrunner' did not return a process handle nor launch error.
	No such process
```

`logs/launch3-console.log` (no-arg launch, complete, 155 bytes):

```text
[main] fatal exception: Unable to determine executable path. Pass the guest ELF as argv[1] or define PS2X_DEFAULT_BOOT_ELF.
org.ps2x.ps2entryrunner: 28325
```

(`28325` is simctl's PID line. Code path: fork `main.cpp:143–165` throws since `argc<2` and `PS2X_DEFAULT_BOOT_ELF` is undefined in this build; `main.cpp:249–257` prints and `std::_Exit(1)`. `main` provably ran.)

`logs/launch4-argv-console.log` (argv probe, complete, 487 bytes):

```text
Using argv boot path
INFO: Initializing raylib 5.5
INFO: Platform backend: DESKTOP (SDL)
INFO: Supported raylib modules:
INFO:     > rcore:..... loaded (mandatory)
INFO:     > rlgl:...... loaded (mandatory)
INFO:     > rshapes:... loaded (optional)
INFO:     > rtextures:. loaded (optional)
INFO:     > rtext:..... loaded (optional)
INFO:     > rmodels:... loaded (optional)
INFO:     > raudio:.... loaded (optional)
WARNING: SDL: Failed to initialize SDL
org.ps2x.ps2entryrunner: 28506
```

(`Using argv boot path` = `main.cpp:145–149`; raylib lines precede `runtime.initialize` returning; `Failed to initialize PS2 runtime` / `Failed to load ELF` never print — the crash below lands first. `loadELF` never reached.)

Crash report `logs/crash-argv.ips` (9157 bytes, `ps2EntryRunner-2026-09-19-200153.ips`, pid 28506, parent `launchd_sim`):

| Item | Value |
|---|---|
| Exception | `EXC_BAD_ACCESS` / `SIGSEGV`, `KERN_INVALID_ADDRESS at 0x0` |
| Termination | `SIGNAL`, code 11, `Segmentation fault: 11` |
| Threads | 1; faulting thread 0 |
| Stack (function-level from `.ips`) | `rlLoadTexture` ← `rlglInit` ← `InitWindow` ← `PS2Runtime::initialize(char const*)` ← `main` ← `start_sim` ← `start` |

No crash report exists for launch #3 (clean `_Exit(1)`); host `DiagnosticReports` and the device `CrashReporter` dir show nothing else new.

Measurement caveat (observed): `simctl launch --console` exits 0 for all of clean-fatal (`_Exit(1)`), crash (SIGSEGV), and would-be success — it reports launch success, not app exit. Exit behavior must be read from console text + `.ips` presence, not the simctl exit code.

### Screenshot

None taken. Absence reasoned: launch #3 exited in ~1s before any window path; the argv probe crashed inside `InitWindow` before window creation (`WARNING: SDL: Failed to initialize SDL` precedes any window). No window ever existed to capture; a screenshot would show only the home screen. (Secondary: `simctl io screenshot` cannot write to the external scratch volume — EPERM above — so any future capture must target an internal path first.)

## Entry/lifecycle map from REAL logs (I5 gaps 2/4)

Measured call order (argv probe):

```text
SpringBoard bootstrap → posix_spawn (launchd_sim) → start_sim → main (main.cpp:167)
  → getExecutablePath → "Using argv boot path" → PS2Runtime::initialize
  → InitWindow (raylib 5.5, DESKTOP/SDL backend, modules loaded)
  → SDL_Init FAILS ("WARNING: SDL: Failed to initialize SDL")
  → rlglInit → rlLoadTexture → EXC_BAD_ACCESS at 0x0 (no GL context behind it)
```

No-arg order: same through `main`, then `getExecutablePath` throws → `[main] fatal exception` → `_Exit(1)`; SDL never attempted.

I5 gap disposition:

| I5 gap | Status after I6 evidence |
|---|---|
| 1 — No `CFBundleIdentifier` | Closed: install exit 0 with `org.ps2x.ps2entryrunner` |
| 2 — Call order unmeasured | Closed as far as evidence goes: order above measured from console + crash logs. `loadELF`/`run` order still unreached (blocked behind SDL init) |
| 3 — What first launch is given instead of a game | Partially informed: `simctl launch` forwards argv and `argv[1]` is honored (`Using argv boot path`); still needs its brief for the real strategy (`loadELF` never ran — SDL fails first) |
| 4 — SDL2main / `SDL_UIKitRunApp` interplay | One side measured: with plain `main` and no `SDL2main`/`UIApplicationMain`, SDL video init fails on the sim (WARNING + downstream SEGV). The fix side belongs to a later brief |

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | SDL video init fails on sim without UIKit entry; `InitWindow` then SEGVs in `rlLoadTexture` | `logs/launch4-argv-console.log`: `WARNING: SDL: Failed to initialize SDL` + `logs/crash-argv.ips`: SEGV stack `rlLoadTexture ← rlglInit ← InitWindow ← initialize ← main` | Brief that wires UIKit entry (link `SDL2main` / call `UIApplicationMain` / SDL iOS bootstrap — implementer's call), rebuilds the sim `.app`, and re-runs this brief's install+launch measurement; expect `InitWindow` to proceed to `loadELF` |
| 2 | `loadELF`/`run` order + missing-resource behavior still unmeasured | Absence: crash precedes `loadELF` in launch #4; launch #3 fatals before `initialize` | Re-run of this brief's launch measurement after gap 1 clears (argv probe + no-arg), capturing console + screenshot if a window appears |
| 3 | Harness: simctl-owned file writes fail on the external volume | `logshow-*.log`: `Unable to open stdout path … Operation not permitted`; screenshot EPERM `code=513` | No code brief — standing measurement rule for later briefs: `--console` with shell redirect for stdout (proven), screenshot to an internal path then `mv` |
| 4 | `simctl launch --console` exit code does not propagate app exit/crash | Exit 0 observed for `_Exit(1)` (launch #3) and SIGSEGV (launch #4) | Standing measurement rule: read exit behavior from console text + `.ips` presence, never the simctl exit code |
| 5 | Xcode warns the Info.plist identifier has no matching `PRODUCT_BUNDLE_IDENTIFIER` build setting | Build log: `User-supplied CFBundleIdentifier … must be the same as the PRODUCT_BUNDLE_IDENTIFIER build setting value ''` | Optional hardening brief: also set `XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER` and confirm the warning clears with install still exit 0 (install works regardless) |
| 6 | First-launch boot-path strategy still open (I5 gap 3 carried) | `logs/launch3-console.log`: no-arg fatal names `argv[1]` / `PS2X_DEFAULT_BOOT_ELF`; argv forwarding proven but `loadELF` unreached | Brief that defines what first launch is given (argv probe path / `PS2X_DEFAULT_BOOT_ELF` / bundled stub) — only after gap 1 clears so `loadELF` actually runs |

## Step 4 — Report (this file)

| Item | Receipt |
|---|---|
| Evidence dir | `local/research/I6/` (REPORT.md + `logs/`, 18 files, 612K total, under the 5 MB cap; no screenshots) |
| Scratch | `W/logs/` holds the same files plus the full 1.0 MB `ios-runtime-build.log` (only the tail is committed); `W/ios-runtime-rel/` (5.4G) is the build tree |
| Sim shutdown | `simctl shutdown` exit 0; device verified `(Shutdown)` |
| Commit | `[I6]` + `Orchestrated-By: Muse Code` trailer; `git add -f` (dir is git-ignored); no push |
| Time box | ~25 min wall (configure 1.5 min, build 5.5 min, remainder measurement); 4h box not binding |

## Exact commands

```sh
# --- Step 1: fork edit (ONE file), commit, pull --rebase attempt, push fork only ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"
git -C "$FORK" log --oneline -5; git -C "$FORK" branch --show-current
git -C "$FORK" status --short   # M ps2xRuntime/.../register_functions.cpp (P-lane, pre-existing)
grep -n "MACOSX_BUNDLE\|GUI_IDENTIFIER\|XCODE_ATTRIBUTE" "$FORK/ps2xRuntime/CMakeLists.txt"  # no match (verified)
# (edit: insert PS2X_IS_IOS set_target_properties block before if(APPLE))
git -C "$FORK" diff ps2xRuntime/CMakeLists.txt        # one hunk
git -C "$FORK" add ps2xRuntime/CMakeLists.txt         # that ONE file only
git -C "$FORK" commit -m "CMake: set iOS bundle identifier for the sim .app (I6)" -m "<body>" -m "Co-Authored-By: Muse Code <muse-code@users.noreply.github.com>" -m "Muse-Session: striped-proteus (01a0bc11-e0ee-7c03-9943-3d2927f82dda)"
git -C "$FORK" pull --rebase fork ssx3                # refused: unstaged P-lane file; proven no-op instead:
git -C "$FORK" fetch fork ssx3; git -C "$FORK" log --oneline HEAD..fork/ssx3  # empty
git -C "$FORK" merge-base --is-ancestor fork/ssx3 HEAD && echo ancestor-ok
git -C "$FORK" push fork ssx3                        # 53bac61..bdae295; ONLY in fork clone to fork remote
git -C "$FORK" ls-remote fork ssx3                   # bdae295…

# --- Step 2: fresh Release-iphonesimulator build in W ---
W="/Volumes/Extreme SSD/ps2x-i6"; mkdir -p "$W/logs"
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE=/Users/bradrichardson/dev/ssx3/local/research/I1/logs/ios-simulator.toolchain.v2.cmake \
  -DCMAKE_CONFIGURATION_TYPES=Release \
  -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF \
  -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i4/sdl2-ios-sim/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -S "$FORK" -B "$W/ios-runtime-rel"                 # exit 0 (71.9s + 19.5s)
cmake --build "$W/ios-runtime-rel" --config Release -- -jobs 4   # BUILD SUCCEEDED, 5m20s
APP="$W/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app"
stat -f "%z bytes" "$APP/ps2EntryRunner"; file "$APP/ps2EntryRunner"
/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" "$APP/Info.plist"   # org.ps2x.ps2entryrunner
nm -g "$APP/ps2EntryRunner" | grep -E " T _(main|SDL_main|SDL_Init|InitWindow|SDL_UIKitRunApp|UIApplicationMain)$"
nm -g "$APP/ps2EntryRunner" | grep -c " T _SDL_"     # 292
otool -L "$APP/ps2EntryRunner"; codesign -dvv "$APP"

# --- Step 3: boot + install + launches ---
UDID="4DE6C37C-77EF-45AE-827E-26286E68D022"
xcrun simctl boot "$UDID"; xcrun simctl bootstatus "$UDID" -b
xcrun simctl install "$UDID" "$APP"                   # exit 0
xcrun simctl listapps "$UDID" | grep -A10 org.ps2x
xcrun simctl launch --stdout="$W/…" --stderr="$W/…" "$UDID" org.ps2x.ps2entryrunner        # exit 3 (EPERM)
xcrun simctl launch --stdout="$W/…" --stderr="$W/…" "$UDID" org.ps2x.ps2entryrunner        # exit 3 (retry)
xcrun simctl launch --console "$UDID" org.ps2x.ps2entryrunner                             # exit 0, [main] fatal
xcrun simctl launch --console "$UDID" org.ps2x.ps2entryrunner /nonexistent-boot.elf      # exit 0, SDL fail + SEGV
xcrun simctl spawn "$UDID" log show --last 10m --style compact --predicate 'eventMessage CONTAINS "ps2" OR …'
xcrun simctl spawn "$UDID" log show --last 6m --style compact --predicate 'process == "ps2EntryRunner" OR …'
cp ~/Library/Logs/DiagnosticReports/ps2EntryRunner-2026-09-19-200153.ips "$W/logs/crash-argv.ips"

# --- Step 4: evidence + commit + shutdown ---
cp W/logs/{boot,bootstatus,install,launch,launch3-console,launch4-argv-console,crash-argv.ips,logshow-ps2,logshow-launch,nm-entry,nm-sdl-count,otool-L,codesign,Info.plist,ios-runtime-configure,ios-runtime-build-tail,fork-commit,fork-push} local/research/I6/logs/
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/I6/
git -C /Users/bradrichardson/dev/ssx3 commit -m "[I6] …" -m "Orchestrated-By: Muse Code"
xcrun simctl shutdown "$UDID"; xcrun simctl list devices | grep "$UDID"   # (Shutdown)
```

(`W` = `/Volumes/Extreme SSD/ps2x-i6/`; full untruncated commands in shell history; log files hold the outputs.)

## Receipt paths

- `local/research/I6/REPORT.md` (this file)
- `local/research/I6/logs/fork-commit.log`, `fork-push.log` (fork diff receipt + push receipt)
- `local/research/I6/logs/ios-runtime-configure.log` (full), `ios-runtime-build-tail.log` (last 80 lines; full log in `W/logs/`)
- `local/research/I6/logs/boot.log` (empty), `bootstatus.log`, `install.log` (empty), `launch.log`
- `local/research/I6/logs/launch3-console.log`, `launch4-argv-console.log` (complete console texts)
- `local/research/I6/logs/logshow-ps2.log`, `logshow-launch.log` (device-log excerpts incl. EPERM smoking gun)
- `local/research/I6/logs/crash-argv.ips` (SIGSEGV report), `nm-entry.log`, `nm-sdl-count.log`, `otool-L.log`, `codesign.log`, `Info.plist.txt`
- `W/logs/` (same 18 files + full `ios-runtime-build.log`); `W/ios-runtime-rel/` (build tree, 5.4G)
- Rebuilt product (read/write this brief): `/Volumes/Extreme SSD/ps2x-i6/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app`
- Fork `bdae295` on `fork ssx3` (pushed; includes P-lane `8d10619`)

## What I could not do

- Reach `loadELF` / `run` / a first window — SDL video init fails first (gap 1 above owns the next step).
- Wire UIKit entry (`SDL2main`/`UIApplicationMain`) — a later brief's implementation work (observed, not designed).
- Define the first-launch boot path (`argv[1]` vs `PS2X_DEFAULT_BOOT_ELF` vs bundled stub) — later brief (gap 6).
- Screenshot a running app — no window ever existed (reasoned above, none taken).
- Symbolicate the crash to source lines — Release build without `-g`/dSYM; function-level stack from `.ips` only.
- Device slice (`ios-arm64`) — unchanged from I5 (not attempted per scope rule).
- Signing beyond observing adhoc — `TeamIdentifier=not set`; no provisioning profiles touched.
- `IoPaths` sandbox behavior — container provisioned and listed, but the app never ran far enough to write into it.
- Touch / keyboard / MFi / audio-session / GLES-render verification — unchanged from I5 (no running app).
- Debug-config codegen question — unchanged from I4 (Release only).
- The 81 Release-build warnings — still untriaged beyond the new bundle-identifier warning's identification.
