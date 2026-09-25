# N11 — Odin per-stage budget on the play build (sound-on speed done; profiles + pin blocked)

Worker: Muse Code. Brief: `local/muse/prompts/N11.md` + orchestrator update
(Brad's env `9fb46f85…` is the live default; write a full env per run, restore
byte-exact after; install TL1's APK again anyway). Date: 2026-09-24/25.
Method: N10 launcher adapted (`launch.py`: text logs in git, binaries to
scratch, mc0-test empty card, `PS2X_SOUND=1`, gpubusy sampler, `--pin-cpu7`,
`--probe-at-end`). No fork edits, no builds, no push.

## Status

**2/4 launches; the per-stage table is unproducible on this build.**

- **S1 (sound on, no profiler): complete.** Full run to tick 4514, zero FATAL.
  Race **7.04 guest vsyncs/s = 0.117×**; rider moves (44 MPH at 00:00:46).
- **S2/S3 (race/menu profiles): NOT launched.** The live end-of-S1 probe of the
  exact profile command fails: the TL1 APK is a release build, not
  debuggable, no `profileableFromShell` in the fork manifest, device not
  rooted — both simpleperf selectors fail (§Probes). Launching S2/S3 would
  only re-prove the same static error.
- **S4 (pin GameThread to cpu7): pin FAILED, run completed unpinned.**
  `taskset: failed to set pid 5005's affinity: Operation not permitted`
  (shell UID ≠ app UID, no root), at launch and at end. Doubled as a second
  sound-on sample: race **6.83/s = 0.114×**, 43 MPH at 00:00:47.
- Sound-on mean (2 runs): **6.94/s = 0.116×** vs N10 sound-off 6.76/s =
  0.113×: sound costs nothing measurable (inside run-to-run spread).
- Coarse thread budget from `top` TIME+ (whole run ÷ final tick): GameThread
  ~90–93, GsWorker ~30–34, main ~5.6–5.8, AAudio ~0.4 ms CPU per guest frame.
  No finer stage split exists without a profiler.

## Build (reused TL1 APK, installed before each run)

| Item | Result |
| --- | --- |
| APK | `~/dev/ssx3-work/TL1/app-release.apk`, `aeb60d4d5e0c8418f2428a6120efd46fb0946e1a5142af24ee41dd67d1e34220`, 153,720,348 B |
| Pre-install SHA reads | `aeb60d4d…34220` ×2 match (before S1; same file before S4) |
| Installed `base.apk` SHAs | S1 `…/com.ps2x.runner-zIl1HZ6_jSf61JvTldZ-BA==/base.apk` ×2 match APK; S4 `…/com.ps2x.runner-rgj42_5oue0ArvCjdvOlhg==/base.apk` ×1 match |
| Pins | PS2Recomp `f949ff0` + paraLLEl-GS `963cb57` per TL1; diagnostics off |

## Env (full N11 env per run; Brad's restored after every run)

Live keys: `PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`,
`PS2X_CD_IMAGE=…/SSX3.iso`, `PS2X_SKIP_MOVIE=1`, `PS2X_SOUND=1`,
`PS2X_MC_ROOT=…/files/mc0-test`, I26-FAST `PS2X_PAD_SCRIPT`,
`PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_VSYNC_RATE_LOG=1`. No `PGS_`/`DUMP`/
`TRACE`/`CAPTURE`/`ORACLE` key (launcher asserts).

| Item | Result |
| --- | --- |
| S1 env SHA (device) | `3b90d8a88dcb25a02d60928f0c9253cb041a94e649678dac1d116658da6f9f62` |
| S4 env SHA (device) | `62a6acbc42c419b33ceb4b1ef982cba65e9db756dcd4af0dfc40a7edae36feef` |
| S1 vs S4 env diff | comment line only; live keys identical |
| Pre-run device env | `9fb46f85…d13` (Brad's) both runs, else abort |
| Restored env SHA | `9fb46f85…d13` match=True after S1, S4, and final check |
| Brad `mc0` | 6/6 SHAs match I31 pins before S1, after S1, after S4, final check (read-only; never written) |
| `mc0-test` | created empty, empty before each run, empty after (game wrote nothing) |

## Launches

`python3 local/research/N11/launch.py --label S1 --wall 600 --stop-tick 4500
--probe-at-end` and `--label S4 … --pin-cpu7 --probe-at-end`. Each run: lease
claimed before install, `adb install -r` Success, keyguard `showing=false`,
AC `true`, BACK after `am start`, `am force-stop` after (pid-after=none), env
restored, lease `LEASE_FREE N11 done`.

| Launch | Race duration | Result | Receipts |
| --- | --- | --- | --- |
| S1 | tick 1714→4514 = 2800 vsyncs = 46.7 s guest; 397.6 s race wall; 94 samples; 0 FATAL | STOP tick ≥4500 at t+471.0 s; battery 71→67% | `logs/S1/{driver.log,logcat.txt,sf-latency.txt,thermal.txt,gpubusy.txt,ps2x.env,ps2x.env.brad,meta.json,scap-sha.txt,probe-*.txt}` + 4 PNGs in scratch |
| S4 | tick 1714→4539 = 2825 vsyncs = 47.1 s guest; 413.8 s race wall; 98 samples; 0 FATAL | PIN failed at t+8.6 s (run unpinned); STOP tick ≥4500 at t+493.5 s; battery 67→63% | same layout under `logs/S4/` + `pin.txt`, `probe-simpleperf-p.txt` |

Device left: lease `LEASE_FREE N11 done`, app not running, env `9fb46f85…`,
mc0 data SHAs match (final independent check).

## Ledger-ready rates (sound on, TL1 APK)

Guest vsyncs per wall second; ratio ÷ 59.94; `phases.py` on epoch-stamped
`[vsync-rate]` lines at I26-FAST boundaries.

| Phase | S1 vsyncs/s | S4 vsyncs/s | S1 ratio | S4 ratio | SF presents/s S1/S4 |
| --- | ---: | ---: | ---: | ---: | --- |
| Title/startup (0→636) | 31.94 | 30.70 | 0.533× | 0.512× | 52.3 / 54.2 (n=1) |
| Main menu (636→766) | 29.23 | 30.59 | 0.488× | 0.510× | 49.2 / 53.0 (n=1) |
| Select Character (766→884) | 15.96 | 15.40 | 0.266× | 0.257× | 54.1 / 57.6 (n=1) |
| Setup Character / Peak (884→1099) | 23.41 | 21.13 | 0.391× | 0.352× | — / 51.6 (n=1) |
| Select Mode / Event / My Rules (1099→1440) | 34.88 | 37.53 | 0.582× | 0.626× | 52.3 / 53.6 (n=1) |
| Loading / Rival card (1440→1714) | 11.41 | 10.25 | 0.190× | 0.171× | 53.2–58.5 (n=3) / 58.1–58.6 (n=2) |
| **Race (1714→4514/4539)** | **7.04** | **6.83** | **0.117×** | **0.114×** | **55.8–59.4 (n=36) / 55.2–59.1 (n=38)** |

- Sound-on race mean: 6.94/s = **0.116×** (wall 142.0 ms/S1, 146.4 ms/S4 per
  race frame). N10 sound-off: 6.76/s = 0.113× (L1 0.116×, L2 0.110×).
  S4 3.0% slower than S1: heat soak (status 5 most of S4 vs 3–4 in S1).
- Race per-5s bins: S1 6.8–7.8 with one dip to 4.6–5.2 near t+172–177 s
  (recovered); S4 6.4–7.6 with a dip to 4.8–5.2 near the same window, then
  7.4–8.2 in the final bins as the rider descends. Same dip shape as N10.
- Logcat keys both runs: `[padscript] armed n=31 source=env clock=vsync`,
  `[snd-output] stream rate=36000 channels=2 bits=16` (underruns >0,
  overflows 0 — guest under 1×), `[gs-path] … subgroup_hier=wave64-fixed …
  gpu=Adreno (TM) 830`, zero FATAL.

## Thread budget (coarse — top TIME+, whole run ÷ final tick)

No simpleperf, so no stage split. TIME+ is cumulative CPU-s since process
start; ÷ 4514 (S1) / 4539 (S4) ticks. End snapshot %CPU in parentheses.

| Thread | S1 CPU-s | S1 ms/frame | S4 CPU-s | S4 ms/frame |
| --- | ---: | ---: | ---: | ---: |
| GameThread | 404.61 (84.0%) | 89.6 | 422.04 (92.5%) | 93.0 |
| GsWorker | 136.42 (32.0%) | 30.2 | 152.91 (29.6%) | 33.7 |
| main (`com.ps2x.runner`) | 25.34 (4.0%) | 5.6 | 26.36 (3.7%) | 5.8 |
| AAudio_1 | 1.63 (0.0%) | 0.36 | 1.75 (0.0%) | 0.39 |
| PGS-Waiter | 0.19 | 0.04 | 0.29 | 0.06 |

Sum ≈ 126 / 133 ms CPU per guest frame vs ≈ 104 / 109 ms wall per frame
(whole-run average; threads overlap). Race-only wall: 142.0 / 146.4 ms.

## GPU busy + thermal per phase

`gpubusy` finding: the two counters are NOT monotonic across 5 s reads, so
each read is a self-contained busy/total window — the ratio is per-sample
(S1 analysis; S4 driver records it directly). Means below; small-n menu rows
are indicative only.

| Phase | S1 GPU% (n) | S4 GPU% (n) | S1 therm | S4 therm |
| --- | ---: | ---: | --- | --- |
| Title (0→636) | 13.1 (2) | 17.1 (2) | status 0→3 | 3 |
| Menus (636→1099) | 14.1 (3) | 20.8 (4) | 3 | 3 |
| Mode/Event (1099→1440) | 23.0 (2) | 20.6 (2) | 3 | 3→5 |
| Loading (1440→1714) | 9.1 (4) | 12.4 (4) | 3 | 5 |
| **Race (1714+)** | **11.3 (61)** | **16.6 (64)** | **3→4** | **5** |

- GPU is far from saturated in the race (11–17%); the bottleneck is host CPU.
- S1 clocks: cpu5 3.53 GHz early → 1.79 most of race; cpu7 4.32 with dips
  (2.25 at the last poll); temp raw 83,000–105,100.
- S4 pre-launch check read status 0 (no wait needed); first in-run poll
  already read 3, status 5 from tick ~1434 to end. S4 launched ~4 min after
  S1 ended; the residual heat explains its 3.0% slower race (same pattern as
  N10 L2 after L1).

## Screencap readings (all 8 viewed)

Fine horizontal stripes persist (known); large black foreground early as in N10.

| Capture | Tick~ | Clock | Place | Progress | MPH | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| S1 sc01 | 2108 | 00:00:06 | 2ND/2 | 1% | hidden (EA Radio card) | "3-0", RECOVER; track: Poor Leno – Silicon Soul Remix / Royksopp |
| S1 sc02 | 3001 | 00:00:21 | 2ND/2 | 2% | 1 | small rider center |
| S1 sc03 | 4001 | 00:00:38 | 2ND/2 | 2% | 0 | same slope view |
| S1 sc04 | 4514 | 00:00:46 | 2ND/2 | 5% | **44** | snow spray, rider descending |
| S4 sc01 | 2100 | 00:00:06 | 2ND/2 | 1% | hidden (EA Radio card) | "220"; track: Emerge – Junkie XL Remix / Fischerspooner (RNG differs from S1) |
| S4 sc02 | 3001 | 00:00:21 | 2ND/2 | 2% | 1 | same view as S1 sc02 |
| S4 sc03 | 4005 | 00:00:38 | 2ND/2 | 2% | 0 | same view as S1 sc03 |
| S4 sc04 | 4539 | 00:00:47 | 2ND/2 | 5% | **43** | same fast descent as S1 sc04 |

Movement onset between tick ~4000 and ~4514 both runs, as N10.

## Probes (why S2/S3/S4-as-designed are blocked)

Exact commands and errors (full text in `logs/Sx/probe-*.txt`):

- `simpleperf record -g --app com.ps2x.runner -o … --duration 5` (S1 end,
  S4 end): rc=1,
  `simpleperf E environment.cpp:837] Package com.ps2x.runner doesn't exist
  or isn't debuggable/profileable.`
- `simpleperf record -g -p <pid> -o … --duration 3` (S4 end): rc=1,
  `simpleperf E event_selection_set.cpp:739] failed to open perf event file
  for event_type cpu-cycles: Permission denied`
- `taskset -p 80 <GameThread-TID>` (S4 t+8.6 s and S4 end): rc=1,
  `taskset: failed to set pid 5005's affinity: Operation not permitted`;
  read-back stays `ff`. GameThread TID found via `top -H` (tid 5005).
- Static causes, verified without launching: fork
  `android/app/src/main/AndroidManifest.xml` has no
  `profileableFromShell`/debuggable flag; `dumpsys package` shows no
  profileable marker and no DEBUGGABLE flag; `run-as com.ps2x.runner` →
  `package not debuggable`; `su` absent (not rooted).
- Symbol path (ready if a profileable build exists): unstripped
  `…/tl1/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/62t3q3g2/obj/arm64-v8a/libps2EntryRunner.so`
  on bytesize; host simpleperf at
  `/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/simpleperf/bin/linux/x86_64/simpleperf`
  (N5 recipe). BuildID match not verified (no perf.data to match).

## Driver notes (for the next measurer)

- `ps -T -p <pid> -o …` prints NOTHING on this ROM (S1 `thermal.txt` has only
  clocks/temp/status; N10's GameThread column was equally empty). Thread
  discovery uses `top -H -b -n1` (works; see `game_tid()`).
- N10's driver never pulled `perf-*.data` (PNG-only pull loop); N11 pulls
  `*.png` + `*.data` to scratch. The `--profile-after-tick` path is written
  but never fired (S2/S3 not launched).
- Gated atexit: force-stop only if this run launched, restore only if it
  pushed its env, release only if it claimed — a precondition abort touches
  nothing (in particular never Brad's session).

## Exact commands

```sh
mkdir -p local/research/N11/logs ~/dev/ssx3-work/N11
cp local/research/N10/launch.py local/research/N11/launch.py  # then N11 edits
cp local/research/N10/phases.py local/research/N11/phases.py  # unchanged
sha256sum ~/dev/ssx3-work/TL1/app-release.apk  # x2: aeb60d4d...34220
adb -s 622c49b1 shell "echo 'N11 prep Sx' > /data/local/tmp/mg/LEASE"
adb -s 622c49b1 install -r ~/dev/ssx3-work/TL1/app-release.apk  # before S1, S4
adb -s 622c49b1 shell 'for f in $(pm path com.ps2x.runner | cut -d: -f2); do sha256sum $f; done'
python3 local/research/N11/launch.py --label S1 --wall 600 --stop-tick 4500 --probe-at-end
python3 local/research/N11/launch.py --label S4 --wall 600 --stop-tick 4500 --pin-cpu7 --probe-at-end
python3 local/research/N11/phases.py local/research/N11/logs/S1
python3 local/research/N11/phases.py local/research/N11/logs/S4
```

## Gaps and recommended next action

| Gap | Reason |
| --- | --- |
| Per-stage ms/frame (the lane's point) | no profiler on this build (S2/S3 not launched) |
| Menu profile | same |
| Pinning effect | taskset EPERM (S4 ran unpinned) |
| Race-window-only thread split | top TIME+ is whole-run cumulative |

To get the stage table, the orchestrator needs a profileable build of the
same tips (manifest `profileableFromShell`, or debuggable — brief forbids
builds for this worker) and a re-run of S2/S3 with this driver; the
`--profile-after-tick` path and the bytesize symbol files are ready.
Budgets used: 0 builds, 2/4 launches (S1 ~475 s, S4 ~498 s wall), ~1.5 h of
2 h, N11 git dir 960 KB text-only, scratch `~/dev/ssx3-work/N11/` 3.8 MB.

## Orchestrator gate (Part 1)

**Accepted as far as it goes.** Sound-on race 0.117× / 0.114× (mean 0.116×) vs N10 sound-off
0.113×: sound costs nothing measurable. GPU 11–17 % busy in the race, so the Odin is CPU-bound.
GameThread ~84–92 % of a core at the race-end snapshot. Brad's env and card were verified intact
after every run. The profile and pinning block is a real build limit (release APK not profileable,
shell can't set app-thread affinity), correctly stopped at the probe instead of burning launches.
Part 2 released: `profileable` manifest + in-process `PS2X_GAME_THREAD_CPUS` knob on `71c952e`,
one APK, S2/S3/S4b.

---

# Part 2 — profiles on a profileable build (done)

Worker: Muse Code. Brief: `local/muse/prompts/N11.md` Part 2 (overrides
Part 1's no-fork/no-build rule for the two `n11-prof` commits + one APK;
all other Rules apply). Base: fork `ssx3` `71c952e` (moved from `f949ff0`).

Outcome: **the per-stage table exists.** S2 race profile (GameThread-bound:
VU1 hazard 70.1 + execute 48.2 ms of a 145.4 ms race frame) and S3 menu
profile (GsWorker-bound: Turnip driver 61.9 + libc 28.2 ms of a 41.9 ms
menu frame). S4b proves the affinity knob (`rc=0`, GameThread on 6/7 all
run) with no speed change vs unpinned. Device restored to Brad's exact
play state (TL1 APK + env + save) afterwards.

## Fork work (`n11-prof`, local only, never pushed)

Worktree `~/dev/ssx3-work/N11/PS2Recomp`, branch `n11-prof` from
`fork/ssx3` `71c952e` (verified `git rev-parse fork/ssx3` after fetch; the
E lane's checkout untouched). Game thread starts at
`ps2xRuntime/src/lib/ps2_runtime.cpp:3724-3726` (`PS2Runtime::run()`:
`std::thread gameThread`, `SetCurrentThreadName("GameThread")`).

- Commit A `9dadccd`: manifest `<profileable android:shell="true" />`
  inside `<application>` (release stays non-debuggable).
- Commit B `20db28f`: `PS2X_GAME_THREAD_CPUS` (`"6,7"`; unset/empty = no
  change). New `ps2xRuntime/include/ps2_thread_affinity.h` (pure
  `parseCpuList` + `pinCurrentThreadToCpus` via `sched_setaffinity(0,…)`,
  `#if defined(__linux__) || defined(__ANDROID__)`); hook at game-thread
  start prints `[affinity] game thread cpus=… rc=…` to stderr
  unconditionally (`RUNTIME_LOG` compiles out of release builds — same
  precedent as `[padscript]`/`[vsync-rate]`). Test
  `ps2xTest/src/ps2_thread_affinity_tests.cpp` (parser cases), registered
  in `ps2xTest/CMakeLists.txt` + `main.cpp`. 6 files, +121. No `git add -f`
  in the fork.
- Runner-dir check empty: `git diff --stat 14b1e5cb n11-prof --
  ps2xRuntime/src/runner` → no output.
- Suite from worktree root (TL1 recipe: Release, `PS2X_BUILD_TEST=ON`,
  taps OFF, shadow-parallel ON, parallel-gs `963cb57`, canonical codegen):
  configure rc=0, `ninja ps2x_tests` rc=0, **603/603 pass** incl. new
  `Ps2ThreadAffinity`.

## APK build (bytesize, the one build)

`ps aux` first: WSL idle (load 0.00, no PCSX2/builds). Root `/home/brad/n11`:
`PS2Recomp` = n11-prof tar (SHA `f3645909…` both ends); codegen/parallel-gs/
jniLibs = `/home/brad/tl1/*` re-verified (codegen 9457 files; parallel-gs
24310 + 3 manifest-excluded `fsr2/build` files, 8/8 sampled SHAs match
TL1's manifest; jniLibs 2 files). Detached launch died the TL1 way, so the
build ran in one held ssh: **BUILD SUCCESSFUL in 6m**, `BUILD_SH_RC=0`.

- APK `2f5c4b67bd2689939b12e887f5b15b5fe70eb10b5a403736de241b15b33d8fe9`
  (remote ×2, pulled ×2, all match), 153,720,392 B (44 B over TL1's).
- Merged manifest contains `profileable android:shell="true"`; installed
  `base.apk` SHAs match per run (3 installs).
- Unstripped `.so` kept:
  `…/n11/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/1hw2q3n2/obj/arm64-v8a/libps2EntryRunner.so`
  (997 MB, BuildID `eb91129d…`, SHA `31371b40…`). Build script: `build.sh`.

## Launches (3/3; same env/restore rules as Part 1)

Env = Part 1 N11 env + `PS2X_GAME_THREAD_CPUS=6,7` on S4b only. Driver
gains: `--game-cpus`, cpu6 clock + GameThread cpu (`/proc/.../stat`
field 39) in the 10 s poll. Thermal ≤2 verified before each launch
(1-min waits before S3/S4b recorded below). New APK installed before each
run; Brad env `9fb46f85…` + mc0 SHAs verified after every run.

| Launch | Window | Result | Receipts |
| --- | --- | --- | --- |
| S2 race profile | tick 2412→2609 = 197 vsyncs in 31.1 s wall (6.34/s, profiler-perturbed) | 30 s `simpleperf record -g --app` from t+171.4 s; `perf-S2.data` 27.6 MB (`4e557efa…`); 0 FATAL; battery 62→60% | `logs/S2/` + 3 PNGs |
| S3 menu profile | tick 676→1525 = 849 vsyncs in 35.6 s wall (23.8/s) over main menu→loading | 30 s profile from t+22.0 s; `perf-S3.data` 93.6 MB (`d53a1574…`); 0 FATAL; 4 GsWorker threads ~100% each; battery 60→59% | `logs/S3/` + 2 PNGs |
| S4b pinned clean | tick 1714→4527 = 2813 vsyncs = 47.0 s guest; 416.0 s race wall | `[affinity] game thread cpus=6,7 rc=0`; gtcpu all 6/7 (20+24 polls); STOP tick ≥4500 at t+491.1 s; 44 MPH at 00:00:46; 0 FATAL; battery 59→55% | `logs/S4b/` + 4 PNGs |

Thermal waits: S3 pre-launch 3→0 (~1 min), S4b pre-launch 3→2 (~1 min).
S2 ran at status 3, cpu6/cpu7 4.32 GHz, GameThread on cpu6 during the
profile (unpinned run roams 5→6/7: menus cpu5, race cpu6/7 per S2 gtcpu).
S3/S4b heat-soaked in-run (status 5).

After S4b the device was restored to Brad's exact play state: TL1 APK
`aeb60d4d…` reinstalled (base.apk SHA matches), env `9fb46f85…`, mc0 data
SHAs match, `/data/local/tmp/n11` + `files/mc0-test` removed, lease
`LEASE_FREE N11 done`, app not running.

Screencaps viewed: S2 sc01 race 2ND/2 00:00:06 (profile starts tick 2412,
just after); S3 sc01 Single Event Backcountry/Happiness loading 100%
(profile ends tick 1525); S4b sc04 2ND/2 00:00:46, 5%, 44 MPH.

## Symbolization

Bytesize NDK simpleperf + symdir (unstripped `.so` + device `libc.so`;
Turnip added but useless — see below). N5 `report.sh` recipe:
self/comm-sym, self/sym-dso, threads, dso, children(≥1%).

- S2: 148,317 samples, 126.66 G cycles, **0 unresolved rows**.
- S3: 601,798 samples, 428.96 G cycles, **0 unresolved rows** (our `.so`;
  Turnip/ kernel rows as below).
- Turnip `libvulkan_freedreno.so` is stripped (0 defined FUNCs in dynsym;
  APK bytes identical to jniLibs), so its ~1235 S3 rows stay
  `libvulkan_freedreno.so[+off]` — bucketed as one Vulkan-driver stage.
- Kernel rows stay `[kernel.kallsyms][+off]` (no kallsyms) — bucketed
  libc/kernel; children view attributes the big ones (GsWorker `ioctl`
  9.4% = GPU submit; `pthread_cond_signal` 3.2% = GameThread→GsWorker
  enqueue handoff).
- Reports committed: `reports/s2|s3-{self-comm-sym,threads,dso,children}.txt`
  (+ `s2-self-sym-dso.txt`; the 1.7 MB `s3-self-sym-dso.txt` stays in
  scratch). Stage mapping appendices: `reports/s2-stage-appendix.md`
  (all 98 rows ≥0.05%) and `reports/s3-stage-appendix.md` (all 302 rows
  ≥0.05%); full mapping reproducible with `buckets.py --appendix`.

## Per-stage ms per guest frame (the point of the lane)

Conversion model (stated): sample share × scale k. S2 race is
GameThread-bound (84.92% of samples; top 84–100%), so GameThread ms/frame
= clean race wall/frame W = 145.4 ms (mean of S1 142.0, S4 146.4, S4b
147.9) → k = 145.4/84.92 = 1.7122 ms per 1% (this also de-perturbs the
9% profiler slowdown: window ran 6.34/s vs ~7.0 clean). S3 menus are
GsWorker-pool-bound (87.96%; 4 workers ≈ 3.3 cores at end snapshot), so
GsWorker ms/frame = 41.9 ms window wall/frame × 3.3 → k = 1.5716
(approximate: end-snapshot anchor; unscaled for perturbation).

S2 race (shares of all samples; 92.11% covered, 7.89% tail <0.05%):

| Stage | Share | ms/frame |
| --- | ---: | ---: |
| VU1 hazard bookkeeping | 40.92% | 70.1 |
| VU1 execute | 28.17% | 48.2 |
| libc/kernel/vdso | 14.53% | 24.9 |
| PLT | 4.94% | 8.5 |
| GIF/GS packet handling | 0.80% | 1.4 |
| scheduler/sync/waits | 0.60% | 1.0 |
| EE runtime helpers | 0.53% | 0.9 |
| guest code | 0.38% | 0.7 |
| paraLLEl CPU submit | 0.36% | 0.6 |
| VIF1/DMA | 0.30% | 0.5 |
| other | 0.30% | 0.5 |
| profiler unwind overhead | 0.14% | 0.2 |
| PS2 runtime other | 0.14% | 0.2 |
| tail (<0.05%) | 7.89% | 13.5 |

S2 thread rows (CPU-s per guest frame): GameThread 145.4 (by
construction), GsWorker 20.8, main 4.5, AAudio 0.3. Total ≈ 171 ms =
1.18 cores. DSO: our `.so` 81.15%, kernel 13.21%, libc 4.16%, vdso 0.76%,
Adreno GLES 0.27%, Turnip 0.09%. Children: `EeScheduler::run` 84.6% →
guest `sub_00382760` → `Store32` → `processPendingTransfers` →
`processVIF1Data` → `VU1Interpreter::run` 77.8%.

S3 menus (71.62% covered at ≥0.01%; 28.38% diffuse tail):

| Stage | Share | ms/frame |
| --- | ---: | ---: |
| Vulkan driver CPU (Turnip, stripped) | 39.39% | 61.9 |
| libc/kernel/vdso | 17.93% | 28.2 |
| scheduler/sync/waits | 4.84% | 7.6 |
| VU1 hazard bookkeeping | 3.50% | 5.5 |
| VU1 execute | 3.19% | 5.0 |
| profiler unwind overhead | 0.87% | 1.4 |
| PLT | 0.61% | 1.0 |
| guest code | 0.55% | 0.9 |
| other | 0.38% | 0.6 |
| EE runtime helpers | 0.15% | 0.2 |
| PS2 runtime other | 0.11% | 0.2 |
| VIF1/DMA | 0.05% | 0.1 |
| paraLLEl CPU submit | 0.03% | 0.0 |
| GIF/GS packet handling | 0.02% | 0.0 |
| tail (<0.01%) | 28.38% | 44.6 |

S3 thread rows: GsWorker 138.3 (by construction), GameThread 16.5, main
2.2, AAudio 0.1. S3 top symbols: `HybridMutex::tryLock` 3.18% /
`unlock` 1.47% (GsWorker lock churn), scudo `allocate` 1.13% /
`deallocate` 0.98% / `quarantine` 0.91% (malloc traffic), `__memset` 1.10%,
`__memcpy` 0.86%. Our own PGS/GS code ≈ 0.05%: menu GsWorker time is
driver-internal + allocator + mutex, spread over ~1400 sub-1% symbols.

S2 top 5: `commitReadyPipelines` 24.96%, `calculatePairReadyCycle` 12.73%,
`VU1Interpreter::run` 7.34%, `@plt` 4.84%, `execUpper` 3.80% (all
GameThread; full top-25 in `reports/s2-self-comm-sym.txt`).

## S4b (pinned 6,7; base 71c952e) vs S1 (unpinned; base f949ff0)

Guest vsyncs/s and ratio ÷59.94. Base differs (I32 etc. landed between),
so this is pin + base-delta combined; all deltas are inside run-to-run
spread (cf. S1 vs S4).

| Phase | S1 /s | S4b /s | S1 × | S4b × |
| --- | ---: | ---: | ---: | ---: |
| Title | 31.94 | 31.27 | 0.533 | 0.522 |
| Main menu | 29.23 | 30.35 | 0.488 | 0.506 |
| Select Character | 15.96 | 18.31 | 0.266 | 0.305 |
| Setup/Peak | 23.41 | 24.51 | 0.391 | 0.409 |
| Mode/Event | 34.88 | 35.91 | 0.582 | 0.599 |
| Loading | 11.41 | 10.11 | 0.190 | 0.169 |
| **Race** | **7.04** | **6.76** | **0.117** | **0.113** |

Pinning GameThread to 6,7 changes nothing measurable (unpinned it already
runs on 6/7 in the race — S2 gtcpu). S4b GPU race 16.5% (n=63); S2 GPU
race 15.4% (n=14). S2 pre-profile phases on the new base match S1 within
noise (title 0.517×, menu 0.503×, SC 0.268×, setup 0.379×, mode 0.601×,
loading 0.189×, early race 7.2–7.8/s).

## Gaps, budgets, receipts

| Gap | Reason |
| --- | --- |
| Turnip symbol names | stripped adrenotools build; offsets only |
| Kernel symbol names | no kallsyms; call-stack attribution only |
| S3 28% diffuse tail | ~1100 symbols <0.01% each (menus spread thin) |
| S3 ms scale ±15% | GsWorker-pool anchor from end snapshot, unscaled perturbation |

Budgets: 2 fork commits (local `n11-prof`, no push), 1/1 builds (6 min),
3/3 launches (S2 ~207 s, S3 ~64 s, S4b ~495 s wall), ~2 h of 2 h, N11 git
dir 1.9 MB text-only, scratch `~/dev/ssx3-work/N11/` (APK, tars, build
dir, PNGs, perf.data, suite logs). Bytesize: `/home/brad/n11` (source,
build tree, APK, prof/, symdir/).
Committed: this section, `launch.py` (Part 2 args), `buckets.py`,
`build.sh`, `logs/S2|S3|S4b/`, `reports/`.
Key commands: the Part 1 block plus `python3 launch.py --label S2 …
--profile-after-tick 2400 --profile-secs 30`, `--label S3 …
--profile-after-tick 636 --profile-secs 30 --scap-ticks 700,1000,1400`,
`--label S4b … --game-cpus 6,7`; `simpleperf report … --symdir …` ×14
(incl. regens) on bytesize; `buckets.py <report> [--comm T] [--appendix]`.
