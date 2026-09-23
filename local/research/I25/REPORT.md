# I25 — iOS at parity with Android: installed on Brad's iPhone, validated on the Simulator

- Date: 2026-09-23. Brief: `local/muse/prompts/I25.md`. Worker: Claude (Opus pane).
- Orchestrator amendments during the run:
  1. Keep working through the provisioning block.
  2. Unblocked with I23's wildcard profile `f0793278-…`, copied from the
     laptop by the orchestrator.
  3. **Brad's rule:** the iPhone is build and install only. All launch,
     test and screenshot work moves to the Simulator first, then the iPad.
     This overrides the brief's validation section.
- **Part 2 headline (gate PASS, then rebuild):** the iPhone now has the
  build on E50's fixed tree: fork `i25-ios` = `eac6cba` + 2 commits,
  codegen `codegen-ssx3`, signed binary `296f73a8…`. It was installed, not
  launched. On the Simulator the race now draws the world (sky, fog,
  horizon, terrain surface, rider). Details are in §Part 2 below.
- **Part 1 headline:** the build then (fork `i25-ios` = E49 `b48b502` + 2
  commits, codegen `codegen-ssx3-e49`) was **installed on Brad's iPhone**
  (install only, not launched).
  - On the iOS 27 Simulator it plays itself with no controller: title →
    main menu → Select Character (the 3D rider is drawn) → Happiness race.
    The HUD is live and the timer advances 00:00:11 → 00:00:19.
  - The 3D course renders near-black. That's the same known caveat as the
    Mac (E31/E50 lane), not something iOS-specific.
  - Turning the Settings switch off stops the auto-route at "Press START
    button".
- Found and fixed on the way: **no iOS lane had ever shown a rendered
  frame.** SDL 2.32 creates its `UIWindow` without a `UIWindowScene`. iOS 27
  requires the scene manifest (I7), so the window was never displayed.
  Frame dumps showed the guest drawing menus while the screen stayed black.
- Budget: 4 device builds and 4 Simulator builds, mostly incremental (a full
  build takes ~12 min at `-jobs 8`, `nice -n 10`). 5 Simulator runs (lease
  slot each), ~1.5 h of 5 h. Disk: `~/dev/ssx3-work/I25` is 11 GB logical
  (the staged ISOs are APFS clones), plus 3.2 GB in the Simulator container.
  Cap 15 GB; `disk_budget.sh` reads 61.8 / 200 GB.

## Part 2 (2026-09-23 evening): rebuilt on E50's fixed tree

| Item | Result |
|---|---|
| Rebase | `i25-ios` rebased onto fork `ssx3` `eac6cba` (E50 FPU fix) with no conflicts. Both test registrations kept in `ps2xTest/src/main.cpp`. Branch is now `eac6cba` + `31d988d` + `8a70aa6` (the same two I25 commits, new SHAs), local only. `git diff eac6cba HEAD -- ps2xRuntime/src/runner` is empty. |
| Codegen | Canonical `~/dev/ssx3-work/codegen-ssx3` (E50 regen, 9455 sources). `build-install.sh` now points there by default; `codegen-ssx3-e49` is no longer used. |
| Host suite | 600/600 (E50 added 5 FPU tests) |
| **iPhone** | **Installed, not launched** (Brad's rule). Signed binary `296f73a8…` (read twice, both match); unsigned build output `83eb97ab…`, 357,236,408 B. Install `0AD77AA2-…` (`logs/install-iphone.log`). |
| Simulator run F (lease slot 1, stopped at 306 s) | All 13 route presses fired.<br>- Select Character at 40 s: Zoe is now placed correctly on the left; in Part 1 she overlapped the stats panel (E50's camera fix).<br>- Race: **the world draws.** At 00:00:20 there's a cloudy sky, the horizon, a dark untextured terrain surface and the rider with its trail. At 00:00:25 the camera is in fog, with snow shards. The trick score shows "900" at 00:00:12.<br>This matches E50's Mac description (`E50/REPORT.md` §e50f: sky, fog, rider, trail; terrain mostly dark and untextured). The sun and lens flare from E50's 00:00:19 frame aren't in view here; the race moments differ (1ST vs 2ND). Still short of PCSX2's textured slopes, which is E50's open gap and not iOS-specific. |
| Rate (Simulator on the M5 Pro mini, DIAGNOSTIC, not a speed number) | Menus 41.9 vsync/s = 0.70×. Race 11.7 vsync/s = 0.20×. |

Part 2 shots (`shots/`, downscaled; original sha256 prefix):

| File | What | sha256 |
|---|---|---|
| `e50-1-select-character.jpg` | Select Character, Zoe placed correctly | `db1a90ea…` |
| `e50-2-race-t12.jpg` | Race 00:00:12: sky band, snow shards, trick score "900" | `bcffed02…` |
| `e50-3-race-t20-sky-terrain-rider.jpg` | Race 00:00:20: sky with clouds, horizon, terrain, rider and trail | `d9b40589…` |
| `e50-4-race-t25-fog.jpg` | Race 00:00:25: in fog, 72 MPH | `fc903ad2…` |

Receipts: `logs/sim-run-f-e50-console.log`, `logs/sim-run-f-e50-progress.txt`,
`logs/install-iphone.log` (Part 2 install), `logs/host-tests-summary.txt`
(600/600), `logs/i25-ios-branch.diff` + `-log.txt` (now against `eac6cba`).

The Part 1 record below is unchanged, except that the how-to and the
recipe now describe the Part 2 build.

## Diff summary (fork `~/dev/ssx3-work/I25/PS2Recomp`, local branch `i25-ios`, not pushed)

| Commit | What |
|---|---|
| `39a8266` | `ps2_env_file.h`:<br>- `ps2x.env` parser (N3's format)<br>- `${BUNDLE}`/`${DOCUMENTS}` expansion<br>- layer merge where keys set by the launcher win<br>- 3 host tests<br>`ps2_ios_runtime` (iOS only):<br>- reads `<bundle>/ps2x.env`, then `<Documents>/ps2x.env`<br>- Settings.bundle `autoRoute` switch; off clears `PS2X_PAD_SCRIPT`<br>- creates the `mc0`/`mc1` dirs<br>- SDL hints: accelerometer is not a joystick; landscape only<br>`main.cpp`:<br>- `PS2X_BOOT_ELF` when launched without argv (iOS)<br>- `PS2X_MC_ROOT` override (the bundle is read-only)<br>`ps2_pad.cpp` (iOS): first ready gamepad; keyboard and gamepad combined (N6)<br>`ps2_runtime.cpp`: `PS2X_VSYNC_RATE_LOG=1` diagnostic line, off by default<br>`Info.plist`:<br>- landscape only<br>- `UILaunchScreen` (without it iOS uses legacy screen-size mode)<br>- full screen, no status bar<br>- Documents visible in the Files app<br>- display name "SSX3 PS2X" |
| `666642f` | Attach SDL's `UIWindow` to the connected window scene. `ps2_ios_runtime` becomes `.mm`. Retried each frame until the scene connects.<br>Forward every UIKit window-size change to raylib (covers rotation).<br>Exclude the imgui debug panel on iOS, as on Android (it covered the screen).<br>`SetTraceLogLevel(LOG_ERROR)` on iOS: raylib's `EndDrawing` warned from `GetWindowScaleDPI()` ~60×/s. Console volume fell from 450 KB to 8 KB per 100 s. |

- 12 files, +527 −3 (`logs/i25-ios-branch.diff`).
- Desktop and Android behaviour is unchanged: the iOS code is behind
  `PS2X_IOS`, and the new env variables do nothing when unset.
- Host suite 595/595 at the final HEAD (`logs/host-tests-summary.txt`).
- `git diff b48b502 HEAD -- ps2xRuntime/src/runner` is empty.

## Parity table (Android → iOS)

| # | Item | iOS state | Evidence |
|---|---|---|---|
| 1 | Env file (`ps2x.env`) | **Done.** Bundle file gives the defaults; `Documents/ps2x.env` overrides them; `devicectl`/`simctl` launch env overrides both. Sets `PS2X_BOOT_ELF`, `PS2X_CD_IMAGE`, `PS2X_MC_ROOT`, `PS2X_SKIP_MOVIE=1`, `PS2X_DEINTERLACE=weave`, `PS2X_PAD_SCRIPT` and `PS2X_PAD_SCRIPT_CLOCK=vsync`. Starts from the home screen with no Mac attached (no argv). | `logs/sim-run-d-console.log`: 7 `[ios-env] set` lines, `launcher kept PS2X_VSYNC_RATE_LOG`, `Using PS2X_BOOT_ELF boot path` |
| 2 | Check-in mode (no controller) | **Done, on by default.** E33 route, `armed n=13 clock=vsync`. All 13 presses fired on their guest-ms anchors (`i=0 now=10360ms` … `i=11 now=122522ms`). Race HUD at t≈285 s. Off: iOS Settings → SSX3 PS2X → Auto-route. | Run D (below) and run E (`[ios-env] Settings: Auto-route off -> PS2X_PAD_SCRIPT cleared`; title waits) |
| 3 | Controller | **Code done, not tested by hand.** SDL's MFi `GameController` path is linked (weak; `otool -L`). raylib opens pads at init and on hotplug. The accelerometer-joystick hint is off, so a Bluetooth pad isn't pushed past index 0, and the first ready pad is used. The script is applied on top of pad state (`Pad.cpp:875-896`), so it takes precedence when set. No pad was paired to the Simulator or the iPad. | Gap G1 |
| 4 | Fit 512×448 in landscape | **Done.** Window 874×402 (landscape) after the scene attach. The present keeps the aspect ratio (`min` scale), with the image centred and pillarboxed (black bars at the sides). Drawn at 1× (points), then upscaled by the system. | Shots 2–5; `[ios-window] window=874x402 drawable=874x402` |
| 5 | No PNG dumps by default | **Done.** The bundle env doesn't set `PS2X_FRAME_DUMP_DIR`. | `logs/sim-run-d-console.log` (no `frame:dump`) |
| — | Memory card | Writable `Documents/mc0` and `Documents/mc1`, matching the Mac's empty `cd/mc0` state. The route behaved the same as on the Mac (no card dialog). | Run D |

## Validation

| Target | Result |
|---|---|
| **Brad's iPhone** (`00008140-…`, iPhone 16 Pro Max, iOS 27) | **Installed, not launched** (Brad's rule). Final install 18:09. Bundle `org.ps2x.ps2entryrunner`, team `LQ3V7772Q2`, profile `f0793278-db43-413c-9260-f120dc740845` (wildcard, expires 2027-09-16), identity `295EFB42…`, I9 entitlements.<br>Signed binary `65dad256…` (read twice, both match); unsigned build output `c521827d…`, 357,203,640 B. ISO `3c2f8eb1…` (read twice, both match), ELF from `E32-inputs/cd`. `logs/install-iphone.log`. It's the only iOS build on the phone; it replaced an older `ps2EntryRunner`. |
| iOS 27 Simulator (iPhone 18 Pro `7662ACD6-…`) | Runs A–E below. The Simulator build is a separate binary (`iphonesimulator` prefixes, same source and codegen). |
| iPad (`00008112-…`) | Installed (same signed bundle). Launch refused while locked: `Unable to launch org.ps2x.ps2entryrunner because the device was not, or could not be, unlocked` (`logs/ipad-launch-attempt.log`). Tried once, not retried, as the brief says. |

| Run | Setup | Result |
|---|---|---|
| A | First Simulator build, 123 s | Env and route worked; guest reached menus by tick. **Screen all black.** raylib warnings ~450 KB per 100 s. |
| B | Diagnostic (`PS2X_FRAME_DUMP_DIR`), 82 s | Guest frame at tick 2342 = "Select Mode" menu, drawn correctly. Screen black at the same moment → the fault is in the present path (`shots/sim-0-*`). |
| C | Scene-attach fix, 101 s | `attached to window scene`, window 874×402. Game visible, but the imgui debug panel covered it. |
| **D** | Final build, 326 s (stopped after the race advanced) | Main menu at 20 s; **Select Character with Zoe's 3D model at 40 s**; menus through Select Event; **race HUD 1ST/2, 00:00:11, 3% at 285 s; 00:00:19, 4% at 326 s**. |
| E | Settings `autoRoute=NO`, 61 s | Script cleared; title holds at "Press START button"; the setting was reset after the run. |

**Guest rate, DIAGNOSTIC only.** This is the iOS Simulator on the Mac mini
(M5 Pro), using the Simulator's "Apple Software Renderer" GLES2, with the
rate-log line on. It is not a device number and not a speed number.

| Phase | Rate |
|---|---|
| Menus (ticks 1500–7100, 36 samples) | 30.6 vsync/s = 0.51× of 59.94 |
| Race (ticks 7150+, 19 samples) | 11.5 vsync/s = 0.19× of 59.94 |

## Screenshots (`shots/`, downscaled JPEG; originals `~/dev/ssx3-work/I25/run-*`)

| File | What | Original sha256 |
|---|---|---|
| `sim-0-screen-black-before-scene-fix.jpg` + `sim-0-guest-dump-black-screen-diag.jpg` | Run B: black screen while the guest draws "Select Mode" | — |
| `sim-1-title-autoroute-off.jpg` | Run E: title, "Press START button" (Auto-route off) | `3e73ed55…` |
| `sim-2-main-menu.jpg` | Run D t=20 s: Main Menu, landscape, pillarboxed | `229a67ff…` |
| `sim-3-select-character.jpg` | Run D t=40 s: Select Character, Zoe's 3D model drawn | `3fcdbee1…` |
| `sim-4-race-t11.jpg` | Run D t=285 s: race HUD 1ST/2, 00:00:11, 49 MPH, 3% | `914f477d…` |
| `sim-5-race-t19.jpg` | Run D t=326 s: 00:00:19, 4% (the race advances); 3D course near-black (known caveat) | `870084d1…` |

## Build recipe (mini), one script: `local/research/I25/build-install.sh`

```sh
local/research/I25/build-install.sh                  # iPhone: prefixes configure build stage sign install
TARGET=sim local/research/I25/build-install.sh       # Simulator: prefixes configure build stage sim_install
LABEL=x WALL=600 local/research/I25/sim-run.sh       # Simulator run: lease slot, shots every 20 s, cap, release
local/research/I25/build-install.sh ipad_install ipad_launch ipad_shot   # iPad test (unlocked iPad)
```

- `prefixes`: FFmpeg 7.1.1 (sha `73398439…` checked; fork recipe
  `iOS-FFmpeg-7.1.1.md`) and SDL2 `release-2.32.10` (`5d24957`, I8 recipe),
  built for `iphoneos` or `iphonesimulator` under `~/dev/ssx3-work/I25/`.
  About 1 minute each.
- `configure`: Xcode generator, I9 device toolchain or I1 v2 Simulator
  toolchain, FFmpeg on, aggressive and runtime logs off, raylib 5.5 from
  `E46-build/_deps`, `PS2X_GAME_CODEGEN_DIR=codegen-ssx3` (Part 2; Part 1 used `codegen-ssx3-e49`).
- `build`: waits until no other `clang++`/`ninja` is running, then
  `nice -n 10`, `-jobs 8`.
- `stage`: app + ELF + ISO (APFS clone, sha read twice) + `ps2x.env` +
  `Settings.bundle`, mode 0644.
- `sign`: finds a profile matching the bundle id or the team wildcard that
  lists the iPhone, embeds it, `codesign` with I9 entitlements, `--verify
  --strict`.
- `guard_not_iphone` stops the iPhone UDID from being used by any
  launch or screenshot stage.
- Toolchains and entitlements are copied next to the script.
- The bundled defaults are in `ps2x.env`.

## How to use it (for Brad)

1. On the iPhone, open **SSX3 PS2X**. With no controller it plays itself:
   title → Select Character → a Happiness race (about 5 minutes on the
   Mac's Simulator; phone speed not yet measured).
2. Hold the phone in landscape. The picture is centred with black bars at
   the sides.
3. To play yourself: iPhone **Settings → SSX3 PS2X → Auto-route off**, then
   swipe the app away and reopen it. Pair a controller (Xbox, PS or MFi)
   in Bluetooth settings first.
4. To change other options, put a `ps2x.env` in **Files → On My iPhone →
   SSX3 PS2X**. Its lines override the built-in ones; for example,
   `PS2X_PAD_SCRIPT=` with nothing after it also turns the auto-route off.
5. Known on every platform: the race now draws the sky, fog and rider, but
   the snow is still mostly untextured (the E-lane is on it), and speed is
   well under full.

## Gaps

| # | Gap | Next step |
|---|---|---|
| G1 | Controller not tested by hand on iOS (nothing paired to the Simulator or iPad) | Brad pairs a pad to the iPad or iPhone, Auto-route off, presses START and cross at the title (N6 §5 shape) |
| G2 | No real-hardware run of the final device binary. The iPad was locked, and the iPhone is install-only. Scene attach, GPU present and device rate are checked on the Simulator only. | One iPad run when unlocked: `ipad_install ipad_launch` + `LABEL=… ipad_shot` |
| G3 | The interlace stutter can't be judged from stills. Weave is set as on Android. | Screen recording on the iPad |
| G4 | Screen auto-lock during a long unattended check-in not verified on a device. SDL disables the idle timer by default; unmeasured. | Same iPad run |
| G5 | The Settings switch needs a full relaunch (iOS keeps the app suspended) | Documented in how-to step 3 |
| G6 | Audio: `InitAudioDevice` no longer aborts on the Simulator (I7's wall), but sound output wasn't checked | Listen during the iPad run |

## Recommendation (the orchestrator decides)

1. Accept. The iPhone has a check-in build that needs nothing from Brad,
   and the Simulator shows the full route.
2. When the iPad is unlocked, one short iPad run closes G2–G4 and G6 on
   real hardware.
3. The scene-attach fix and the debug-panel exclusion are general to any
   iOS 27 build. They are candidates for `ssx3` once E agrees (E owns the
   fork; `i25-ios` stays local).

## Receipts

- `logs/`:
  - build tails
  - install logs (iPhone, iPad)
  - iPad launch refusal
  - run D/E consoles + progress
  - run A console head
  - host test summary
  - `i25-ios-branch.diff`/`-log.txt`
  - the earlier provisioning-block receipts (`provprobe-*`, `devices-identities.txt`)
- `shots/` (7 JPEGs, ~300 KB).
- Work tree `~/dev/ssx3-work/I25/`:
  - prefixes
  - build dirs (for incremental rebuilds)
  - `staged` / `staged-sim`
  - `run-*` full-size shots
  - `host-build`
- Leases: mini slots claimed and released on every Simulator run; both
  free at close. Simulator shut down at close.
