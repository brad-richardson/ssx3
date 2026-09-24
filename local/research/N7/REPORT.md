# N7 — Odin APK on folded `ssx3`

Worker: Codex. Brief: `local/muse/prompts/N7.md`. Date: 2026-09-23/24.

## Status

**Stopped at the first failed launch gate.** The clean folded APK built, installed, and reached the drawn race on the Odin. L1 hit the 600 s boot cap at tick 4042: the I26-FAST race starts near tick 1714, so it advanced **2328 guest vsyncs = 38.84 s of racing**, confirmed by the HUD clock `00:00:38`. The brief requires two speed runs through ≥45 s; L1 did not reach that window. Per the first-failed-step rule, L2 and simpleperf were not launched. The orchestrator decides how to continue.

## Branch and codegen

| Item | Result |
| --- | --- |
| Fork base | Fetched `origin/ssx3` = `b9647f54934f9f7c448d7cf41fb42f81c74c8ed8`; local `n7-android` branched there, no rebase |
| N-local cherry-picks | `8e7d5ac→62e79e5` codegen-dir; `322e55b→e4148db` env shim; `3da81ad→a0def6f` arm64; `f9d78da→5a109e3` profileable/PNG; `ae210c9→8e8b8e2` controller; `65c95d9→81aa92d` pad log. Final HEAD `81aa92d12341074927c332ce9305c7fb28f57b01`. E45, tap guard, and vsync-rate commits were skipped because folded. |
| Conflicts | `322e55b` conflicted in `ps2xTest/CMakeLists.txt` and `ps2xTest/src/main.cpp` at adjacent test registrations. Kept folded present-fallback test and added Android env test. No other conflicts. |
| Codegen source | `~/dev/ssx3-work/codegen-ssx3` (E58 promoted) |
| Tar SHA-256 source stream | `db442a54deb268d18926ec5d3fe3edc14559badd095983df32793a788e6277e7` (`COPYFILE_DISABLE=1 tar -cf - -C ~/dev/ssx3-work codegen-ssx3 \| shasum -a 256`) |
| bytesize tar SHA-256 read 1 / 2 | `db442a54deb268d18926ec5d3fe3edc14559badd095983df32793a788e6277e7` / same; 9,457 files extracted into `~/n7/codegen-ssx3` |
| Odin ISO SHA-256 read 1 / 2 | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` / same, existing `SSX3.iso` |

## Build

| Item | Result |
| --- | --- |
| Build count | 1/2 APK builds, PASS at 2026-09-24 02:28:42 UTC. The N5 recipe's pre-Ninja and Gradle packaging each configured a native build directory (`241k161c`, `3m6g5n4m`); the latter supplied the APK. |
| Head / flags / recipe | `n7-android` @ `81aa92d`; E58 codegen at `/home/brad/n7/codegen-ssx3`; `RelWithDebInfo`; CMake caches for both dirs show `PS2X_ENABLE_DIAG_TAPS=OFF`, `PS2X_ENABLE_RUNTIME_LOGS=OFF`, `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`. `~/n7/build.sh` follows N5 `build3.sh`: Ninja `-j6` under `~/n7/mem_governor.sh`, then `./gradlew assembleRelease … -Pps2xGameCodegenDir=/home/brad/n7/codegen-ssx3`. Gradle configured a second dir and its default Ninja; the same governor was attached during that compile (`logs/governor-gradle.log`). |
| APK SHA-256 read 1 / 2 | `426d2a91119b4bd755a1cf399165cc3d2231deb637fe9f5121d0047a0cfe153f` / same on bytesize and mini; installed Odin `base.apk` reads 1/2 also match. 129 MiB. |
| Packaged `.so` / Build ID | APK member `lib/arm64-v8a/libps2EntryRunner.so`: 135,095,512 B, SHA-256 `12e697658bcaa9b3b106fbd7d5f5fe31a25f98bb0ff087f0c7cc697b42b31a9a`, Build ID `338a2a69721083ccb9fe203f2880023dba861699`. Matching unstripped `3m6g5n4m` `.so` SHA-256 `b7a9fff8faad55dd738ec4f9289a1d35590c5d902e2990f86e90b3042d6c638e` ×2, same Build ID. |

## Launches and visuals

| Launch | Race duration | Result | Receipts |
| --- | --- | --- | --- |
| L1 speed | 38.84 s guest race time (tick 1714→4042), 509.2 s wall in race | Title, menus and race reached; 120 `[vsync-rate]` samples; 0 FATAL; stopped at 600 s cap, then `am force-stop`, `pid-after=none`. Battery 99% charging at preflight, 100% at end; keyguard `showing=false`. | `logs/L1-speed/{driver.log,logcat.txt,sf-latency.txt,thermal.txt,ps2x.env,meta.json}`; 4 JPEGs in `shots/` |
| L2 speed | Not found | Not run: L1 missed ≥45 s gate | Not found |
| L3 simpleperf | Not found | Not run: L1 missed ≥45 s gate | Not found |

Launch command: `python3 local/research/N7/launch.py --label L1-speed --wall 600 --stop-tick 4500`, run with escalated permissions. The launcher used the exact I26-FAST route from `local/research/I26/ROUTES.md`, `PS2X_PAD_SCRIPT_CLOCK=vsync`, dev-only `PS2X_SKIP_MOVIE=1`, and `PS2X_VSYNC_RATE_LOG=1`; no frame-dump env var. The app was installed with `adb -s 622c49b1 install -r local/research/N7/app-release.apk` after two matching APK reads. The APK was removed from the repo report directory after installation, and the Odin `base.apk` hash matched twice.

Visuals viewed directly from the full-resolution PNGs, then kept as 960 px JPEGs (all four total 228 KiB):

| Capture | Direct view |
| --- | --- |
| `shots/L1-setup-tick884.jpg` | The capture trigger at tick 875 landed after the Select Character press: **Setup Character** with Zoe's name, but the rider is not clearly drawn; menu sprites are visibly corrupted/overlaid. A true Select Character capture is missing. |
| `shots/L1-race-tick2003.jpg` | HUD clock `00:00:04`, 2nd place, 1% progress; snowy terrain with visible blue-white surface detail, dark sky, a small rider-like shape and large black foreground. |
| `shots/L1-race-tick3015.jpg` | Clock `00:00:21`, 2% progress; snowy slope and dark sky still visible, small rider-like center shape, black foreground over much of the lower scene. |
| `shots/L1-race-tick4042.jpg` | Clock `00:00:38`, 2% progress, 0 MPH; snow/sky/HUD remain, with large black foreground. The clock advanced but visible race progress barely changed from tick 3015. |

The launcher initially wrote a blank lease line on exit because its `adb shell sh -c` release form was quoted incorrectly. I immediately wrote and verified `LEASE_FREE N7 done 2026-09-24T02:40:04Z` in `/data/local/tmp/mg/LEASE`; the app PID was absent. The committed launcher uses a single `adb shell` command string for lease release. No later launch used the lease.

## Ledger-ready rates

Guest vsyncs per wall second; ratio is rate ÷ 59.94. N5 comparison uses APK `b9737306…79ce`; E58 is one clean Mac mini run.

| Phase | N7 Odin vsyncs/s, run 1 | N7 Odin vsyncs/s, run 2 | N7 ratio ÷59.94 | N7 APK SHA-256 | N5 Odin ratio | E58 Mac ratio |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| Title/startup (0→636) | 27.69 | Not found | **0.462×** | `426d2a91…fe153f` | 0.47× | 0.67× |
| Main menu (636→766) | 23.34 | Not found | **0.389×** | same | 0.44× | 0.54× (menus) |
| Select Character (766→884) | 16.10 | Not found | **0.269×** | same | 0.33× | Not found |
| Setup Character / Peak (884→1099) | 18.83 | Not found | 0.314× | same | Not separate | Not found |
| Select Mode / Event / My Rules (1099→1440) | 24.17 | Not found | 0.403× | same | 0.39× (Mode/Event) | 0.54× (menus) |
| Loading / Rival card (1440→1714) | 9.03 | Not found | 0.151× | same | 0.19–0.28× | 0.17× |
| **Race (1714→4042)** | **4.57** | Not found | **0.076×** | same | **0.19–0.26×** | **0.13×** |

Rates are interpolated from epoch-stamped `[vsync-rate]` ticks at I26-FAST phase boundaries by `phases.py` (`samples=120`, last tick 4042). The race rate is 2328 / 509.2 wall seconds; the ~5 s bins ranged about 3.6–5.0 guest vsyncs/s. SurfaceFlinger showed 59.4–60.4 presents/s in 47 race polls; presents are not guest frames. This is one clean diagnostics-off run with host-side screencaps, so the race row is **provisional**, not the brief's two-run ≥45 s result. N5 used a different route and earlier game/GS code; the comparisons show measured outcomes, not a controlled causal test.

## Profile

Thread split by simpleperf: not found. Top 25 by self: not found. A final `top -H` sample in `driver.log` showed GameThread at 100% of one CPU and app main at 3.8%; this is not a simpleperf profile.

## Gaps and recommended next action

| Gap | Reason |
| --- | --- |
| Second ≥45 s speed run | L1 reached only 38.84 s racing at the mandatory 600 s boot cap; first-failed-step stop. |
| Simpleperf top 25 and thread split | No profile launch after L1 gate failure. |
| Select Character rider screencap | Tick-875 trigger landed on Setup Character; no later launch allowed after failure. |
| Two-run race variance | Only one race run; no stable folded-APK race range. |

Build receipts on bytesize: `~/n7/build.sh`, `~/n7/configure.log`, `~/n7/logs/{ninja.log,assembleRelease.log,governor.log,governor-gradle.log,mem.log}`, `~/n7/build-console.log`. Bounded copies are in `logs/{build-console.txt,configure.txt,governor-gradle.txt}`. The build used no other heavy bytesize job. The Gradle compile's governor paused/resumed clang processes; no OOM occurred. The brief used 1/2 APK builds and 1/4 launches.

**Recommended next action for the orchestrator:** approve a longer Odin boot cap of about 700–750 s for a true 45 s race window at the measured 4.57 guest vsyncs/s (or revise the window), then authorize the second speed run and simpleperf profile. A separate capture should trigger Select Character before tick 884. Investigate the 0.076× race rate and black foreground with the G/E lanes; the screenshots establish a drawn, advancing HUD and terrain but not visually clean gameplay.
