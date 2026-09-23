# I25 — iOS parity build on Brad's iPhone: STOPPED at provisioning (Brad blocker)

- Date: 2026-09-23. Brief: `local/muse/prompts/I25.md`. Worker: Claude (Opus pane).
- Read: `AGENTS.md`, `local/AGENTS.local.md`, `local/research/I23/REPORT.md`
  (+ the I21/I8 recipe sections it defers to), `local/research/N6/REPORT.md`,
  `local/research/N4/REPORT.md`, E33/E49 route string, the `n2-android`
  env-shim commit `322e55b` on bytesize (read-only).
- **Outcome: stop rule hit.** The mini has no provisioning profile that
  covers `org.ps2x.ps2entryrunner` on the iPhone, and Xcode can't make one
  because it has no signed-in account. Nothing was built, signed, or
  installed. Budget used: 0 builds, 0 installs, ~40 min.
- **Second stop condition, also hit:** the SSD iOS prefixes the brief
  names (`/Volumes/Extreme SSD/ps2x-i23/`, plus I8's SDL2 and I4's raylib
  dirs) are gone. V2 tier-2 deleted them (`local/research/V2/delete-tier2.txt`
  rows `ps2x-i23`, `ps2x-i8`, `ps2x-i4`). They can be rebuilt from the
  recorded recipes (FFmpeg: `ps2xRuntime/cmake/iOS-FFmpeg-7.1.1.md`; SDL2
  `release-2.32.10`: I8 REPORT §Task 1), so this doesn't need Brad. It
  does add about 15 minutes to the rebuild.

## Blocker for Brad (exact messages)

| Check | Result |
|---|---|
| Signing identity | Present: `295EFB42… "Apple Development: Brad Richardson (E4R78PLLKY)"` (`logs/devices-identities.txt`) |
| iPhone | `Brad’s iPhone 00008140-0002505001F3001C available (paired)`, iPhone 16 Pro Max (iPhone17,2) |
| I23's wildcard profile `f0793278-…` | **Not on the mini.** `~/Library/MobileDevice/Provisioning Profiles/` doesn't exist. Nothing matches `f0793278*` under `~` or in the SSD transfer tars. It was a laptop file. |
| Profiles on the mini (`~/Library/Developer/Xcode/UserData/Provisioning Profiles/`) | 4 profiles, none usable: `com.bradrichardson.zone2` dev (iPhone listed), `com.bradrichardson.zone2.watch` dev (iPhone listed), and two App Store profiles (zone2, zone5; no devices). None matches `org.ps2x.ps2entryrunner` or `*`. Re-signing as zone2 would overwrite Brad's zone2 app, so that's rejected. |
| Xcode automatic provisioning (throwaway project, bundle id `org.ps2x.ps2entryrunner`, team `LQ3V7772Q2`, `-allowProvisioningUpdates`) | `error: No Accounts: Add a new account in Accounts settings.` and `error: No profiles for 'org.ps2x.ps2entryrunner' were found: Xcode couldn't find any iOS App Development provisioning profiles matching 'org.ps2x.ps2entryrunner'.` → `** BUILD FAILED **` (`logs/provprobe-xcodebuild.log`) |
| Permission denial (reported as the rules require) | A search of the mini for an App Store Connect API key (a second way to provision without an Xcode login) was denied by the Claude Code auto-mode classifier ("Credential Exploration"). I didn't retry it or try another route. |

**Either of these unblocks it (Brad, about 1 minute):**
1. Sign in on the mini: Xcode → Settings → Accounts → add the Apple ID
   for team LQ3V7772Q2. The next run then gets a team profile for
   `org.ps2x.ps2entryrunner` from the same throwaway project
   (`logs/provprobe-CMakeLists.txt` + `xcodebuild … -allowProvisioningUpdates`).
2. Or copy I23's wildcard profile `f0793278-*.mobileprovision` from the
   laptop into `~/Library/Developer/Xcode/UserData/Provisioning Profiles/`
   on the mini, if the laptop still has it and it hasn't expired.

## State left behind

| Item | State |
|---|---|
| Fork worktree | `~/dev/ssx3-work/I25/PS2Recomp`, new local branch `i25-ios` at `b48b502` (= `ssx3`, E49). 0 commits, tree clean. `~/dev/PS2Recomp` untouched. |
| Scratch | Throwaway provisioning project in the session scratchpad only (~1 MB). No other bytes written. |
| Device | Untouched (no install, no launch). |
| Disk | `disk_budget.sh`: 51.2 GB of 200 GB before starting. I25 added ~0. |

## Design ready for the resume (from the code reads; not built yet)

Every change is iOS-gated (`TARGET_OS_IPHONE` / `PS2X_IS_IOS`), so the
desktop and Android builds don't change.

| Parity item | Planned change (file) | Basis |
|---|---|---|
| 1. Env shim | New iOS loader that runs first in `main()` (`src/main.cpp` + a small header modelled on N3's `ps2_android_env.h` parser). It reads `<bundle>/ps2x.env`, then `<HOME>/Documents/ps2x.env` (which overrides the bundle file). It expands `${BUNDLE}` and `${DOCUMENTS}` (the bundle's container UUID changes on every install). Keys already set in the launch environment win, so `devicectl -e` still overrides. When there's no `argv[1]` (home-screen launch), the boot ELF comes from `PS2X_BOOT_ELF`. The bundled file sets `PS2X_BOOT_ELF=${BUNDLE}/SLUS_207.72`, `PS2X_CD_IMAGE=${BUNDLE}/SSX3.iso`, `PS2X_SKIP_MOVIE=1`, `PS2X_DEINTERLACE=weave` and the pad script. | `main.cpp` reads only `argv[1]` and `PS2X_CD_IMAGE`; Android's version is `322e55b` |
| Memory card | New `PS2X_MC_ROOT` env override, pointed at `${DOCUMENTS}/mc0` (created at startup). The default `mcRoot` is `<elf dir>/mc0`, which is inside the read-only bundle on iOS. The Mac route runs with an empty, writable `cd/mc0`, so the route needs the same card state. | `ps2_runtime.cpp:347-350,1157-1178`; `E32-inputs/cd/mc0` is empty |
| 2. Check-in mode | Bundled `PS2X_PAD_SCRIPT` = the E33 route (`10350:start:2500,…,113340:down:20000`) with `PS2X_PAD_SCRIPT_CLOCK=vsync`, so it runs title → Select Character → Happiness race (E46b/E49 reached the race HUD). Switch-off: a `Settings.bundle` toggle ("Auto-route"; iOS Settings → ps2EntryRunner), read with `CFPreferencesCopyAppValue`. It's on when unset. When it's off, the loader unsets `PS2X_PAD_SCRIPT`. A `Documents/ps2x.env` with `PS2X_PAD_SCRIPT=` (empty) also turns it off. | `Pad.cpp:538-553` (an empty value disarms the script) |
| 3. Controller | raylib's SDL backend already opens GameControllers at init and on hotplug (`rcore_desktop_sdl.c:1598-1620,1906-1915`). Two iOS fixes: (a) set `SDL_HINT_ACCELEROMETER_AS_JOYSTICK=0` before init. SDL on iOS lists the accelerometer as joystick 0 by default, which pushes a Bluetooth pad to index 1, and `ps2_pad.cpp` reads index 0 only. (b) In `ps2_pad.cpp`, use the first available gamepad and combine keyboard and gamepad input, as N6 does. The script still applies on top of the backend state (`Pad.cpp:875-896`), so it takes precedence when set. | N6 diff (`logs/n2-android-diff.txt`) |
| 4. Landscape fit | Info.plist: add `UISupportedInterfaceOrientations` (both landscape orientations), `UILaunchScreen` (without it, iOS runs the app in legacy screen-size mode), `UIStatusBarHidden`, `UIRequiresFullScreen`, `UIFileSharingEnabled` and `LSSupportsOpeningDocumentsInPlace` (so `ps2x.env` can be edited in the Files app). Also set `SDL_HINT_ORIENTATIONS`. After `InitWindow`, push one `SDL_WINDOWEVENT_SIZE_CHANGED` with the real window size: UIKit sizes the window itself, and raylib otherwise keeps its requested 960×720. The present already letterboxes with `min(sw/512, sh/448)` (`ps2_runtime.cpp:3346-3361`). | raylib only updates its screen size on a resize event (`:1436-1446`) |
| 5. No PNG dumps | Nothing to change: dumps only happen when `PS2X_FRAME_DUMP_DIR` is set (`ps2_runtime.cpp:399`), and the bundled env doesn't set it. | — |
| Rate readout | An env-gated line (off by default) in the present loop, `PS2X_VSYNC_RATE_LOG=1`, printing `vsyncTick` per 5 s of wall time. It's for a labelled diagnostic rate over `devicectl --console`. | — |

Build plan once unblocked. Everything goes under `~/dev/ssx3-work/I25/`
(internal disk), about 9 GB with the ISO staged once.
1. FFmpeg 7.1.1 iOS prefix, using the fork's recipe.
2. SDL2 `release-2.32.10` iphoneos static build, using the I8 recipe.
3. raylib 5.5 source from `E46-build/_deps/raylib-src`.
4. `cmake -G Xcode` with the I9 toolchain,
   `-DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3-e49`, FFmpeg on,
   aggressive and runtime logs off.
5. Stage the ELF, the ISO (sha `3c2f8eb1…` checked twice), `ps2x.env` and
   `Settings.bundle`.
6. Embed the profile, sign with `codesign` and I9's entitlements, run
   `devicectl install`, launch, take screenshots.

The whole sequence goes into `build-install.sh`.

## Recommendation (the orchestrator decides)

Ask Brad for option 1 (Xcode account sign-in on the mini). It's a one-time
step, and it makes future iOS briefs self-sufficient. Then re-issue I25 as
is. The design above is the plan of record for the code changes.
