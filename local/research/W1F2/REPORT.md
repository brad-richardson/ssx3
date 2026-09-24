# W1F2 — iOS startup repair and deferred installs

Worker: Codex. Brief: `local/muse/prompts/W1F2.md`. The orchestrator decides the gate. Fork `w1f-fold` source commit `bc1c70fd08398c4b615fbb34b959aad009dfc7f6` was fast-forward pushed to `fork/ssx3`. The iPhone app was built, signed, and installed only. The iPad run is pending unlock.

## Gate table

| Gate | Result | Receipt |
| --- | --- | --- |
| Source pin | `git fetch fork ssx3`, `git ls-remote fork refs/heads/ssx3`, and local HEAD all read `8acb4b300866cb663569a60fca6b8b708ae50a91` before the repair. Worktree `w1f-fold` was clean. E56 `register_functions.cpp`, stock ELF, and ISO had two matching SHA reads before use. | `input-sha.txt` |
| Repair | Commit `bc1c70f` adapts I25 `31d988d` startup, env, pad, and parser tests plus I25 `8a70aa6` scene/CMake wiring to W1F. Current I26 `ps2_ios_runtime.mm` was retained and compiled into `ps2_runtime`; no E/G/GS, generated-code, guest-data, or W1 aspect edit. Source worktree clean afterward. | `git diff --name-status 8acb4b3 bc1c70f`; `sim-build-key.txt`, `device-build-key.txt` |
| Mac Release | Pass. Reconfigured/rebuilt W1F `build` with taps OFF, runtime/aggressive logs OFF and canonical codegen. `ps2x_tests` run from the fork root: **559/559**, including 3 `Ps2EnvFile` cases, `Ps2PresentGeometry` W1 mode cases, and `Ps2VirtualPad`. No new Mac race boot. | `~/dev/ssx3-work/W1F/{cmake.log,build.log,suite-w1f2.log}` |
| Simulator build/install | Pass from `bc1c70f` and E56 canonical codegen (9,455 game sources; 0 in-tree). Xcode log shows `ps2_ios_runtime.mm` CompileC, `libps2_runtime.a` Libtool, final app Ld and `BUILD SUCCEEDED`. Rebuilt app has scene manifest, landscape, launch screen. Staged/ad-hoc-signed binary two SHA reads matched; `simctl install` passed. | `~/dev/ssx3-work/W1F/{ios-sim-w1f2.txt,ios-sim-install-w1f2.txt}`; `sim-build-key.txt` |
| Simulator run | Pass, one bounded I26-FAST run, lease slot 1, 140 s requested wall cap (script stopped at its next 10 s check, t=146 s), own process terminated and lease released. Console reads bundled `ps2x.env`, uses `PS2X_BOOT_ELF`, attaches UIWindowScene, arms 31 route presses, and selects W1 default guest mode 2. Viewed title, Setup Character after Select Character, and race HUD at 00:00:01 and 00:00:07; tick reaches 2206. Visual race retains the known large dark GS composite region. | `sim-console.log` (11,413 B, line endings normalized), `sim-run.txt`, frames under `~/dev/ssx3-work/W1F/run-w1f2/` |
| iPad | **Pending unlock.** `devicectl list devices` said connected. `device info lockState` read `passcodeRequired: true`, `unlockedSinceBoot: true` initially and on two later checks. No iPad install or launch attempted. Orchestrator told promptly; Brad was asked to unlock. | `ipad-lock.txt`; `~/dev/ssx3-work/W1F/ipad-lock-final-w1f2.json` |
| iPhone | Pass: ID reread as `00008140-0002505001F3001C` (`available (paired)`). Same-source `iphoneos` app built and linked with `.mm`; staged and signed with Apple Development identity, team `LQ3V7772Q2`, wildcard profile `f0793278-db43-413c-9260-f120dc740845`. Signed app and staged ELF/ISO had two matching SHA reads. One `devicectl device install app` succeeded (`databaseUUID 785BBB17-DB09-46DE-AD18-9A0B97F679C0`). **No iPhone launch, test, screenshot, or device driving.** | `device-build-key.txt`, `device-sha.txt`, `install-iphone.txt`; `~/dev/ssx3-work/W1F/{ios-device-w1f2.txt,ios-device-stage-sign-w1f2.txt}` |
| Fork push | Runner-dir diff `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` was empty before and after push. `git diff --name-status 8acb4b3 HEAD` listed only the 11 repair/test files. Existing upstream-tracked `register_functions.cpp` did not change; no new guest source, game data, or binary tracked. Fast-forward push `8acb4b3..bc1c70f`; remote readback `bc1c70fd08398c4b615fbb34b959aad009dfc7f6`. No ssx3 `main` push. | `git push fork w1f-fold:ssx3`; `git ls-remote fork refs/heads/ssx3` |

## Conflict resolution

`git cherry-pick --no-commit 31d988d` conflicted in the existing I26 iOS header and Settings plist, W1/I26 runtime declarations, and test registration. The resolution kept I26 virtual controls and W1 presentation calls, added I25 env parser declarations and three tests, and retained the existing Objective-C++ `ps2_ios_runtime.mm`. The newly staged I25 `.cpp` duplicate was removed. The second I25 commit's scene-related CMake, per-frame window sync, error-only raylib logging, and iOS debug-panel exclusion were adapted manually because its `.mm` already existed in W1F from I26. No E/G design conflict arose. An argv-free unit test was not added because `getExecutablePath` is private to `main.cpp` and its env branch is iOS-only; the Simulator home-screen launch exercised it end to end.

## Two-read SHA-256 ledger

| Item | SHA-256, both reads | Location |
| --- | --- | --- |
| E56 codegen `register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` | `input-sha.txt` |
| Stock ELF, source and staged device | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` | `input-sha.txt`, `device-sha.txt` |
| Stock ISO, source and staged device | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` | same; Simulator staging script also verified ISO twice |
| Simulator staged/ad-hoc-signed binary | `133fd38a3e46313890d01f3420ce5372cfb7e5b5f8d317c8d5a6b767aad711af` | `sim-sha.txt` |
| iPhone signed binary | `bcb9f024234efe3ab8dee07b7afbfe50b3f17836e46b40c0c03c44fec6d594ff` | `device-sha.txt` |

## Viewed Simulator frames

| Frame | Viewed observation | SHA-256 |
| --- | --- | --- |
| `shot-0010s.png` | SSX 3 title logo, landscape scene with virtual pad | `b64fffdf8206ae588c839397ded03e8b723cd0093625806244c12496383cfc96` |
| `shot-0031s.png` | Setup Character, Zoe rendered; route has passed Select Character | `819b3bc91c6ba0ecb763003c44b920ef34ee9f0c719b85a5d40a2287fe774ff5` |
| `shot-0083s.png` | Happiness race HUD 2nd/2, timer 00:00:01 | `ee8d4f96c9685875c4b2fa652d0ca8745d13b5ba36a6eff7d37dc10763e5eebc` |
| `shot-0136s.png` | Race HUD 00:00:07 and 1% progress | `c336d5ac5647b960d95005998670bc6bc842169f7ecdacc9a7eb650df36d897c` |

The 10-second capture cadence missed the brief Select Character interval; the next captured screen is Setup Character. This is a visual-evidence gap, not a failed route. No second Simulator run was made.

## Exact gate commands and budget

Run from `~/dev/ssx3-work/W1F/PS2Recomp` unless noted:

```sh
git fetch fork ssx3
git ls-remote fork refs/heads/ssx3
git cherry-pick --no-commit 31d988daeba6515f8c380906df6ec04872243109
# Resolve I26/W1 overlaps as above; adapt I25 8a70aa6 scene changes into the existing .mm.
git commit -m '[W1F2] Restore iOS startup and scene wiring' -m 'Adapt I25 env, boot, scene, and pad startup to the W1F fold while retaining I26 touch controls and W1 presentation.' -m 'Orchestrated-By: Codex'
zsh /Users/brad/dev/ssx3-work/W1F/build.sh
/Users/brad/dev/ssx3-work/W1F/build/ps2xTest/ps2x_tests
TARGET=sim bash /Users/brad/dev/ssx3-work/W1F/build-install.sh configure build stage
TARGET=sim bash /Users/brad/dev/ssx3-work/W1F/build-install.sh sim_install
LABEL=w1f2 WALL=140 SHOT_S=10 bash /Users/brad/dev/ssx3-work/W1F/sim-run.sh
xcrun devicectl list devices
xcrun devicectl device info lockState --device 00008112-001224302184A01E
TARGET=device bash /Users/brad/dev/ssx3-work/W1F/build-install.sh configure build
TARGET=device bash /Users/brad/dev/ssx3-work/W1F/build-install.sh stage sign
TARGET=device bash /Users/brad/dev/ssx3-work/W1F/build-install.sh install
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
git push fork w1f-fold:ssx3
git ls-remote fork refs/heads/ssx3
```

The first Simulator configure was blocked inside the sandbox by Xcode DerivedData `Operation not permitted` and CoreSimulatorService failure; the same command passed with escalated permissions. This did not consume a corrective build. Mac: one build and suite. Simulator: one build, one run. Device: one build, one iPhone install. iPad: zero runs while locked. W1F directory grew from about 4.2 to 7.7 GB (about 3.5 GB additional, under the 8 GB W1F2 cap); global `disk_budget.sh` read 105.8/200 GB after the builds. Simulator and device full build logs remain under W1F; only bounded text receipts are checked in here.

## Outstanding gap

The iPad needs a fresh `lockState` result with `passcodeRequired: false` before installation or its one allowed run. It remained true on the final check. No further device work was attempted.
