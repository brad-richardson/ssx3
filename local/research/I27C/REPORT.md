# I27C — signed iPhone build and install check-in

Worker: Codex. Brief: `local/muse/prompts/I27C.md`. This was a build, sign, and install check-in only. No iPhone launch, test, screenshot, or iPad action was performed. No fork or ssx3 push was performed.

| Stage | Result | Receipt |
| --- | --- | --- |
| Source pin and runner guard | Remote `fork/ssx3`, local remote-tracking ref, and clean I27C fork worktree HEAD all read `04f3ace599e3d9d52b94803150688f54dbf330ec`. `git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner` exited 0 with no output. Relative to I27B base `4ebb2ac`, the pinned commit changes only `ps2xRuntime/CMakeLists.txt` and adds `ps2xRuntime/cmake/patch_raylib_ios_sdl2_dpi.cmake`. No fork source was edited here. | `source-pin.txt` |
| Inputs and raylib | E54F2 canonical codegen `register_functions.cpp` SHA-256 `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`; stock ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`; stock ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`. Each had two matching source reads before use. Private raylib clone HEAD `c1ab645ca298a2801097931d1079b10ff7eb9df8`; its SDL source changed from pinned `30db3e9f…` to patched `df666c29…` during configure. FFmpeg, SDL2, toolchain, env, entitlements, and profile inputs also had matching SHA pairs. | `*-sha.txt`, `raylib-patch-result.txt` |
| Optimized iphoneos configure/build | One fresh Xcode Release configure/build passed; `ps2_ios_runtime.mm` compiled, app linked, `BUILD SUCCEEDED`. C and C++ Release cache flags are `-O3 -DNDEBUG`; Xcode game object and raylib targets show optimization level 3, and the generated guest-code compiler response has `-O3 -DNDEBUG` with no `-O0`. Diagnostic taps, runtime logs, and aggressive logs are OFF. Source app bundle ID is `org.ps2x.ps2entryrunner`; unsigned binary SHA pair `af307e59d5ca29c9d68ab7f033cdc53fa69fd7100f3b6626103f08037f1197bb`. | `release-cache.txt`, `flags-evidence.txt`, `build-key.txt`, `source-binary-sha.txt`; full configure/build logs remain in I27C scratch |
| Stage and sign | Staged stock ELF and ISO SHA pairs match source; staged profile SHA pair matches the source profile (`db3c2513…`). Existing Apple Development identity `295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1` signed the bundle with wildcard profile `f0793278-db43-413c-9260-f120dc740845`, team `LQ3V7772Q2`, valid through 2027-09-17 01:11:58. The profile includes the iPhone UDID. `codesign --verify --strict --verbose=2` passed; signed arm64 binary SHA pair `30bdafdcb21af148d7caf62cb2cc7f637fe81b6c26c54d3bb9ea3a6d92d01b68`. | `elf-stage-sha.txt`, `iso-stage-sha.txt`, `profile-sha.txt`, `profile-stage-sha.txt`, `profile-check.txt`, `identity-check.txt`, `codesign-verify.log`, `codesign-details.txt`, `signed-binary-sha.txt` |
| Paired iPhone install | Device list immediately before install showed Brad’s iPhone 16 Pro Max, UDID `00008140-0002505001F3001C`, connected. One `xcrun devicectl device install app` exited 0 for `org.ps2x.ps2entryrunner`; receipt gives `databaseUUID 785BBB17-DB09-46DE-AD18-9A0B97F679C0`. No app process command was run. | `install-iphone.log`; scratch `logs/devices-install.txt` |
| Budget | I27C scratch 3.5 GiB, under 8 GiB; committed text/script receipts about 128 KiB, under 8 MiB. Global ssx3 use 130.6 GB, under the 200 GB cap. One configure, build, stage, sign, and install; no compile repair retry. | `budget.txt` |

## Exact commands and pins

All paths in `build-install.sh` are absolute; the script records the exact CMake flags, input paths, signing identity, profile, and install target. Commands were:

```sh
git -C /Users/brad/dev/PS2Recomp fetch fork ssx3
git -C /Users/brad/dev/PS2Recomp worktree add -b i27c-ios-install /Users/brad/dev/ssx3-work/I27C/PS2Recomp 04f3ace599e3d9d52b94803150688f54dbf330ec
git clone --shared /Users/brad/dev/ssx3-work/E46-build/_deps/raylib-src /Users/brad/dev/ssx3-work/I27C/raylib-src
bash /Users/brad/dev/ssx3-work/I27C/build-install.sh preflight
bash /Users/brad/dev/ssx3-work/I27C/build-install.sh configure
xcodebuild -project /Users/brad/dev/ssx3-work/I27C/ios-runtime-device-release/PS2RetroX.xcodeproj -target ps2_game_objects -configuration Release -showBuildSettings
xcodebuild -project /Users/brad/dev/ssx3-work/I27C/ios-runtime-device-release/PS2RetroX.xcodeproj -target raylib -configuration Release -showBuildSettings
bash /Users/brad/dev/ssx3-work/I27C/build-install.sh build
bash /Users/brad/dev/ssx3-work/I27C/build-install.sh stage
bash /Users/brad/dev/ssx3-work/I27C/build-install.sh sign
bash /Users/brad/dev/ssx3-work/I27C/build-install.sh install
```

`preflight`, `configure`, `build`, `sign`, and `install` ran with sandbox escalation because the sandbox blocked CoreDevice or Xcode services. The first sandboxed read-only `devicectl list devices` timed out waiting for CoreDeviceService; the escalated retry succeeded. This was a sandbox-only retry before the brief steps, not a device/install failure. The full build log stays in `~/dev/ssx3-work/I27C/logs/device-build.log`; only bounded key lines were copied here.

## Gaps

No device rendering, input, startup, or speed evidence was collected; the brief authorized install only.
