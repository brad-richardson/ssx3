# I5 — First Simulator launch: install, run, record window-or-crash (tables, no verdicts)

- Date: 2026-09-19. Runbook `local/muse/prompts/I5.md` (first launch is a measurement). Tables, no verdicts.
- I4 (`local/research/I4/REPORT.md`, all of it: Release `.app` product, SDL_main-unlinked note, entry/lifecycle open questions, disk + Simulator constraints) read first.
- Fork: `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`, HEAD `53bac61` (`git log --oneline -1`, recorded not assumed — no later P-lane work present). `register_functions.cpp` still `M` (unstaged) throughout; never staged. Fork READ ONLY: no edits, no commits, no pushes there.
- Product: `/Volumes/Extreme SSD/ps2x-i4/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app` (binary `ps2EntryRunner`, 120264240 bytes, Mach-O 64-bit arm64). Read from `ps2x-i4`, never written into it.
- Rules honored: host + Simulator only (no `adb`, no device, no lease); Simulator = installed iOS 27.0 runtime + existing iPhone 17 `4DE6C37C-77EF-45AE-827E-26286E68D022` only, no substitution, no downloads; scratch on `/Volumes/Extreme SSD/ps2x-i5/` (new dir); `/tmp/p1-link`, `/tmp/ps2xgs-build*`, `/tmp/ps2x-ios-spike`, `ps2x-i3`, `ps2x-i4`, other agents' dirs never touched; evidence `local/research/I5/` committed with `git add -f`, prefix `[I5]`, trailer `Orchestrated-By: Muse Code`; no `git push` in ssx3.
- Outcome shape: install failed (exit 13, missing bundle ID). Per runbook Step 1, Steps 2–3 launch work stops here; this report carries the blockers. No fixes attempted.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i5/`, `APP` = the I4 Release `.app` above, `UDID` = `4DE6C37C-77EF-45AE-827E-26286E68D022`.

## Step 1 — Install

| Item | Receipt |
|---|---|
| Runtime inventory | `simctl list runtimes`: iOS 27.0 (`com.apple.CoreSimulator.SimRuntime.iOS-27-0`) + watchOS 27.0 installed; nothing downloaded |
| Device inventory | iPhone 17 `4DE6C37C-…` present, was `(Shutdown)`; no substitution |
| Boot | `simctl boot` exit 0 (`logs/boot.log`, empty = no stderr); `simctl bootstatus -b` exit 0, `Finished` after 00:22 (`logs/bootstatus.log`); device `(Booted)` |
| Install | `simctl install` exit 13 (`logs/install.log`, full text in Log excerpts) |
| Bundle id | None: install reports `Missing bundle ID`; `Info.plist` contains no `CFBundleIdentifier` (`logs/Info.plist.txt`); `listapps` shows no ps2/EntryRunner entry (39 apps, none ours) |

### Log excerpts

`logs/install.log` (complete, 352 bytes):

```text
An error was encountered processing the command (domain=IXErrorDomain, code=13):
Simulator device failed to install the application.
Missing bundle ID.
Underlying error (domain=IXErrorDomain, code=13):
	Failed to get bundle ID from /Volumes/Extreme SSD/ps2x-i4/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app
	Missing bundle ID.
```

`logs/bootstatus.log` (first 3 + last 2 lines; full 4803 bytes in file):

```text
Monitoring boot status for iPhone 17 (4DE6C37C-77EF-45AE-827E-26286E68D022).
[2026-09-19 23:22:03 +0000] Status=1, isTerminal=NO, Elapsed=00:02.
	Waiting on BackBoard
...
[2026-09-19 23:22:23 +0000] Status=4294967295, isTerminal=YES, Elapsed=00:22.
	Finished
```

## Step 2 — Launch (not reached)

| Item | Receipt |
|---|---|
| Launch command | None issued: no bundle id exists for `simctl launch`, and the runbook Step-1 stop rule applies (install exit 13 → report, no workarounds) |
| `main` / SDL init / first window | Unmeasured — the app was never installed, so nothing executed |
| First 100 / last 100 log lines | N/A — no launch produced no logs |
| Crash report | None — no launch, no crash; `simctl diagnose` not run (nothing to collect) |
| Screenshot | None taken. Absence reasoned: with install failing, no process ran and no window could appear; a screenshot would show only the home screen |

## Step 3 — Entry/lifecycle mapping (static evidence only; no Step-2 logs exist)

No launch logs exist, so the `main` → `SDL_Init` → `InitWindow` → `PS2Runtime::run` call order is unmeasured. What the as-built product statically shows:

| Observation | Evidence line |
|---|---|
| `_main` present in binary | `logs/nm-entry.log`: `T _main` |
| `_SDL_Init` + `_InitWindow` present | `logs/nm-entry.log`: `T _SDL_Init`, `T _InitWindow`; `logs/nm-sdl-count.log`: 292 `T _SDL_` symbols (matches I4) |
| `_SDL_main` + `_SDL_UIKitRunApp` absent (SDL2main still unlinked, per I4) | `logs/nm-entry.log` contains no such lines (grep for all five entry symbols returned three) |
| Link set = libSystem + SDL iOS frameworks + libc++/AVFAudio/CoreFoundation/libobjc | `logs/otool-L.log` (UIKit, OpenGLES, Metal, AVFoundation, … — matches I4) |
| Adhoc signature present; no team | `logs/codesign.log`: `Signature=adhoc`, `TeamIdentifier=not set`, `Identifier=ps2EntryRunner-5555…` (derived, not a bundle id) |
| Entry is plain `int main(int argc, char *argv[])`, no iOS branch (only `__ANDROID__` has one) | Fork `ps2xRuntime/src/main.cpp:167` (read-only); flow: `getExecutablePath(argc, argv)` → `PS2Runtime` + `runtime.initialize(windowTitle)` → `runtime.loadELF(filePathStr)` |
| Fork sets no bundle identifier anywhere | `add_executable(ps2EntryRunner …)` has no `MACOSX_BUNDLE` / `MACOSX_BUNDLE_GUI_IDENTIFIER` / `XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER`; only bundle-adjacent lines are the `install() BUNDLE DESTINATION` comment at `ps2xRuntime/CMakeLists.txt:618–625` |

`Info.plist` key inventory (from `logs/Info.plist.txt`; Xcode-generated, 19 entries):

| Key | Present | Value / note |
|---|---|---|
| `CFBundleExecutable` | Yes | `ps2EntryRunner` |
| `CFBundlePackageType` | Yes | `APPL` |
| `CFBundleSupportedPlatforms` | Yes | `iPhoneSimulator` |
| `CFBundleDevelopmentRegion` | Yes | `English` |
| `MinimumOSVersion` | Yes | `27.0` |
| `UIDeviceFamily` | Yes | `1` |
| `DT*` build keys | Yes | Xcode 27.0 / `iphonesimulator27.0` |
| `CFBundleIdentifier` | **No** | Install blocker (exact error above) |
| `CFBundleVersion` / `CFBundleShortVersionString` | No | Observed absent |
| `CFBundleName` / `CFBundleDisplayName` | No | Observed absent |
| `UILaunchStoryboardName` / storyboards / scene manifest | No | Observed absent |
| `UIRequiredDeviceCapabilities` / `LSRequiresIPhoneOS` | No | Observed absent |

### Gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | No `CFBundleIdentifier` → install fails, nothing downstream measurable | `logs/install.log`: `Missing bundle ID.` + `logs/Info.plist.txt`: no such key + fork CMake: no `MACOSX_BUNDLE_GUI_IDENTIFIER` | Brief that sets a bundle identifier (plist template or `MACOSX_BUNDLE_GUI_IDENTIFIER`), rebuilds the sim `.app`, and re-runs this brief's install+launch measurement |
| 2 | Call order `main` → SDL init → window → `PS2Runtime` unmeasured | Absence: no launch logs exist (install exit 13) | Re-run of this brief's Step 2–3 after gap 1 clears (launch, capture stdout, screenshot, crash log if any) |
| 3 | `main` derives its ELF path from `argv` and calls `loadELF`; no game data in scope | Fork `main.cpp:167–176` + runbook scope note (no ISO) | Brief that defines what first launch is given instead of a game (aufake path / bundled stub / missing-resource dialog) and records the exact behavior — only after gap 2 produces a launch |
| 4 | SDL2main / `SDL_UIKitRunApp` lifecycle interplay still open (I4 deferred it) | `logs/nm-entry.log`: no `SDL_UIKitRunApp`; fork CMake: no `SDL2main` linkage | Brief that maps UIKit entry (SDL2main link vs plain `main` + lifecycle callbacks) against real launch logs — only after gap 1 clears |

## Step 4 — Report (this file)

| Item | Receipt |
|---|---|
| Evidence dir | `local/research/I5/` (REPORT.md + `logs/`, 32K total on internal disk, under the 5 MB cap; no screenshots committed) |
| Scratch | `W/logs/` holds the same 8 log files (source copies); nothing else written to `W` |
| Sim shutdown | `simctl shutdown` issued at end; device verified `(Shutdown)` (command in Exact commands) |
| Commit | `[I5]` + `Orchestrated-By: Muse Code` trailer; `git add -f` (dir is git-ignored); no push |

## Exact commands

```sh
# --- pre-flight: fork HEAD (read-only) + product verify ---
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" log --oneline -1
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" branch --show-current
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" status --short | head -20
ls -lh "/Volumes/Extreme SSD/ps2x-i4/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app/ps2EntryRunner"
file "/Volumes/Extreme SSD/ps2x-i4/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app/ps2EntryRunner"

# --- inventory: runtimes, devices, bundle ---
mkdir -p "/Volumes/Extreme SSD/ps2x-i5" "/Volumes/Extreme SSD/ps2x-i5/logs"
xcrun simctl list runtimes
xcrun simctl list devices
/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" "…/ps2EntryRunner.app/Info.plist"   # Does Not Exist
plutil -p "…/ps2EntryRunner.app/Info.plist"
stat -f "%z bytes" "…/ps2EntryRunner.app/ps2EntryRunner"                                # 120264240 bytes

# --- Step 1: boot + install ---
UDID="4DE6C37C-77EF-45AE-827E-26286E68D022"
xcrun simctl boot "$UDID"            # exit 0
xcrun simctl bootstatus "$UDID" -b   # exit 0, Finished 00:22
xcrun simctl install "$UDID" "/Volumes/Extreme SSD/ps2x-i4/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app"  # exit 13
xcrun simctl listapps "$UDID" | grep -i -A2 -B2 "ps2\|EntryRunner"   # no match

# --- static evidence (read-only; no Step-2 logs exist) ---
nm -g "…/ps2EntryRunner" | grep -E " T _(main|SDL_main|SDL_Init|InitWindow|SDL_UIKitRunApp|UIApplicationMain)$"
nm -g "…/ps2EntryRunner" | grep -c " T _SDL_"     # 292
otool -L "…/ps2EntryRunner"
codesign -dvv "…/ps2EntryRunner.app"
grep -n "ps2EntryRunner\|add_executable\|MACOSX_BUNDLE\|XCODE_ATTRIBUTE\|set_target_properties" FORK/ps2xRuntime/CMakeLists.txt
grep -rn -i "bundle\|MACOSX\|CFBundle\|Info.plist\|GUI_IDENTIFIER\|BUNDLE_ID" FORK/ps2xRuntime/CMakeLists.txt FORK/CMakeLists.txt
grep -n "int main\|SDL_main\|argc" FORK/ps2xRuntime/src/main.cpp

# --- Step 4: evidence + commit + shutdown ---
cp W/logs/*.log W/logs/Info.plist.txt local/research/I5/logs/
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/I5/
git -C /Users/bradrichardson/dev/ssx3 commit -m "[I5] …" -m "Orchestrated-By: Muse Code"
xcrun simctl shutdown "$UDID"
xcrun simctl list devices | grep "$UDID"   # (Shutdown)
```

(`…` = the I4 `.app` path above; `W` = `/Volumes/Extreme SSD/ps2x-i5/`; `FORK` = fork clone. Full untruncated commands are in shell history; log files hold the outputs.)

## Receipt paths

- `local/research/I5/REPORT.md` (this file)
- `local/research/I5/logs/boot.log` (empty), `bootstatus.log`, `install.log`, `nm-entry.log`, `nm-sdl-count.log`, `otool-L.log`, `Info.plist.txt`, `codesign.log`
- `W/logs/` (same 8 files, source copies)
- I4 product (read-only): `/Volumes/Extreme SSD/ps2x-i4/ios-runtime-rel/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app`
- Fork HEAD `53bac61` on `fork ssx3` (no new commits; fork untouched)

## What I could not do

- Launch the app / reach `main` / open a first window / collect a crash log — install exit 13 stands in front of all of it.
- Entry/lifecycle mapping from launch evidence — no Step-2 logs exist; only the static table above.
- Device slice (`ios-arm64`) — unchanged from I4 (not attempted per scope rule).
- Signing beyond observing adhoc — `TeamIdentifier=not set`; no provisioning profiles touched.
- Bundle resources / `IoPaths` sandbox behavior — nothing installed, so no container exists to inspect.
- Touch / keyboard / MFi / audio-session / GLES-render verification — unchanged from I4 (no running app).
- Debug-config codegen question — unchanged from I4 (Release only; Debug stall unmeasured).
- The 80 Release-build warnings — still untriaged (counts only, per I4).
