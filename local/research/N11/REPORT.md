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
