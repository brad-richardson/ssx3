# D1 — Odin measurement matrix: REPORT

## Status: STOPPED at a stop-list item

During the first full arm (`d1-base-a`), thermal zone `cpu-1-1-1`
reached **92.3 °C**, and 121 of 152 sampler ticks read ≥ 70 °C on a
`cpu-*` zone. The brief's stop list names "a thermal zone above 70 °C",
so all further device runs were cancelled and this report was written.
No crash, tombstone, foreign lease/process, or `verified:false` pin
occurred. The device was left idle (post-run zone read 51.2 °C and
falling), `/data/local/tmp/mg/LEASE` was removed, and
`performance_mode` was restored to 0 (verified by read-back).

Completed before the stop: Step 0 in full (sampler + flags + test +
60 s smoke verification), one full `base` arm, the clock-setting
investigation, the read-only parts of Steps 2–3. Everything else in
Steps 1–2 (all remaining arms and repeats, menu-only FP run, dispatch
samples) was not run.

## Table (per arm and repeat)

All arms pinned `--affinity emu=80,video=40` (verified in run.json
before the race window), EGL, idle on, screenshots every 2 s,
`m3-menu.dtm`, module `gGXBE69_recomp.so`, pace binary sha
`84de2c22…`. Sampler tick bracketing for the race rows is ±5 metric
samples (≈ ±9 s at the observed 1.81 s/tick); guest frames = HUD Δ × 60.

| Arm/repeat | Race-window HUD pace | Min speed s50–90 | Tail speed s120–270 | Emu ms/guest-frame | Video ms/guest-frame | Emu-core freq mean/min (race) | Max cpu-* / gpuss temp (race) | Shutdown counters (full run) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d1-base-a (aff-tpl, uncapped) | 1.071× (HUD 0:00→0:15 over 14 s wall; 2 s shot granularity → wall 12–16 s, pace 0.94–1.25) | 0.952 @s60 | 1.966 (mean) | 19.23 | 8.27 | cpu7 3.072 / 3.072 GHz (every race-window sample at the cap) | 76.0 / 51.7 °C | native=2351156756 fallback=0 native_exc=371619 hook_fb=427506 |
| d1-smoke (aff-tpl, 60 s timeout, partial) | n/a (run ends at sample ~45, pre-race) | n/a | n/a | n/a | n/a | n/a | n/a | native=241554546 fallback=0 native_exc=53331 hook_fb=373066 |
| aff-pin2 reference (prior session) | 1.000 | 0.940 | 1.976 | — | — | — | — | — |

Race-window anchors for `d1-base-a` (screenshot-verified): gate
`GO!` HUD 0:00 at 20:48:59, last racing shot HUD 0:15 5th 44 MPH at
20:49:13, pause menu from 20:49:15. Mid-window check: 0:04→0:10 over
6 s wall (20:49:03→20:49:09). Trajectory matches the `aff-pin2` shape
(loading 22% at 20:48:45, briefing at 20:48:55).

Full-run thermal/frequency trace for `d1-base-a` (152 ticks, 275 s
span, effective 1.81 s/tick against the requested 1 s interval — the
per-tick `taskset/ps/chrt/sysfs` body costs ~0.8 s):
152 ticks, max cpu-* 92.3 °C (`cpu-1-1-1`), max gpuss 65.2 °C;
121/152 ticks ≥ 70 °C, first at tick 31 (≈ sample 70, 74.4 °C).
Emu thread PSR=cpu7 on all 151 placed ticks. cpu7 `scaling_cur_freq`
full-run min 2.246 / mean 2.987 / max 3.072 GHz; 17/152 samples below
the 3.072 cap. `gpuclk` 660–1050 MHz across the run.

## Clock arm (setting investigation; arm itself not run)

- Odin performance mode exists: `performance_mode` in `settings
  system` (was 0), QS tile `performancemode` ("Performance /
  Standard", inactive), `fan_mode=4`, `vendor.perfservice` running.
- Headless enable attempted two ways: `cmd statusbar click-tile
  performancemode` (no effect, still 0); `settings put system
  performance_mode 1` (sticks, reads back 1).
- With the mode at 0 and at 1, `cpu7 scaling_max_freq` reads 3072000
  in both cases against `cpuinfo_max_freq` 4320000 (temps ~37 °C, so
  the cap is policy, not thermal). Restored to 0 afterward.
- The `clock` arm (mode 1 under saturated load) was not run because
  of the thermal stop.

## FP-fault rate (partial)

- `d1-base-a` full-run counters: `native_exc=371619`,
  `hook_fb=427506`, `fallback=0` over samples 0–285. No separate
  menu-only run exists, so the in-race exception rate (difference ÷
  race seconds) could not be computed.
- The `STATICRECOMP_DISPATCH_SAMPLES=1` extra run was not done; no
  share at `0x800`–`0x81C` / `0x500` / `0x900` to report.

## Shader cache (read-only part only)

- After the graceful-stop `d1-base-a` (SIGTERM via harness
  `timeout`; shutdown counters printed):
  `ls -R /data/local/tmp/mg/user-d1-base-a/Cache` → no such
  directory; `find … -iname "*cache*"` → nothing. Same for
  `user-d1-smoke`. User dir size 18 M.
- `grep -i shader|cache` over both runs' stderr/stdout finds no
  shader-cache lines (only the `[staticrecomp] shutdown:` counter
  line).
- The extra 30 s-past-race arm was not run (thermal stop); nothing
  was fixed.

## `detnone` note

Template `user-aff-detnone` was created on device (`user-aff-tpl`
copy + `GPUDeterminismMode = none` under `[Core]`, verified by
read-back) but never run. No trajectory comparison exists.

## Exact commands

Pre-run (all `adb -s 622c49b1 shell …` unless noted):

- `ps -A | grep moderngekko` → empty; `cat …/LEASE` → absent; then
  `echo D1 > /data/local/tmp/mg/LEASE`.
- Pace binary provenance: on-device `moderngekko-run-trial` hashed
  `84de2c22…` (= plan's pace-egl sha; the harness pushes whatever
  `--binary` under the trial name). Pulled to
  `D1/moderngekko-run-pace-egl` (re-verified same sha) and reused as
  `--binary` for every arm, so each run re-pushed identical bytes.
  Local trial TU `trial/moderngekko-run-trial` is `c59d173e…`
  (matches `trial/build.json`) but was never pushed (control-probe
  never ran).
- Thermal gate before each arm: `/tmp/d1_thermal_wait.sh <tag>`
  (waits until all `cpu-*` zones < 45 °C, 30 s polls; log appended
  to `D1/thermal-waits.log`). `d1-smoke` and `d1-base-a` were both
  clear on first poll (35–38 °C).
- `d1-smoke`: `python3 tools/android_trial.py run --binary
  D1/moderngekko-run-pace-egl --tag d1-smoke --output
  D1/d1-smoke-receipts --template aff-tpl --movie m3-menu.dtm
  --module gGXBE69_recomp.so --graphics OGL --idle on --affinity
  emu=80,video=40 --sampler --screenshot-seconds 2 --timeout 60
  --serial 622c49b1`.
- `d1-base-a`: same with `--tag d1-base-a --output
  D1/d1-base-a-receipts --timeout 300`.
- Unit tests: `python3 -m unittest tests.test_android_trial`
  (21 tests, OK; no pytest on this host).

Sampler wiring (committed): `tools/odin_sampler.sh` is
`aff-sampler.sh` plus per-tick `scaling_cur_freq` cpu0–7, thermal
zones with type `cpu-*`/`gpuss*`/`skin*` (type + temp), and
`kgsl-3d0/gpuclk`; existing CPU/PSR columns untouched. `--sampler`
pushes it (sha-verified against the repo copy — match confirmed
post-run), starts it against the real child PID at 1 s interval
after affinity, `nticks = timeout + 180`, and pulls
`<tag>-sampler.log` into the receipts (`run.json:sampler`).
`--graphics` gained a `Null` choice (never exercised — `nullvideo`
never ran). `--probe-quiet` sets `SSX_NATIVE_QUIET=1` (never
exercised — `control-probe` never ran).

## File list

- Evidence root `/Volumes/Extreme SSD/android-spike/D1/`:
  `REPORT.md` (this file), `analyze.py`,
  `moderngekko-run-pace-egl` (84de2c22…),
  `d1-smoke-receipts/` (err/out/GFX+Dolphin-post/run.json/
  sampler.log/138 shots; probe pull false — the pace binary writes
  no probe file), `d1-base-a-receipts/` (same set, 138+ shots),
  `thermal-waits.log`.
- Repo commit (one commit, `[D1]` prefix, per-file `git add`):
  `tools/odin_sampler.sh` (new), `tools/android_trial.py`
  (`--sampler`, `--probe-quiet`, `Null` graphics), 
...[truncated 911 chars]

---

# Part 2 (D1b continuation, 2026-09-17 ~21:02–22:27 EDT)

Step 0 was not redone. `D1/analyze.py` and the `d1-base-a` receipts were
reused; Part 1 above is intact. Interleave order as run:
`base-b`, `clock-a`, `detnone-a`, `base-stock-a`, `nullvideo-a`,
`detnone-b`, `base-stock-b`, `nullvideo-b`, `capped1x`, `menu-only`
(+`menu-pre` correction), `dispatch`, `control-probe` (+`fb` fallback),
`cache-late`. Never the same arm twice in a row.

## Regime change (orchestrator steers, mid-matrix)

- At ~21:0x the user set Performance mode via the device UI and raised the
  fan from Silent. `d1-base-b` launched under `performance_mode=0` but the
  mode read 1 at 21:07 mid-run: base-b is perf-mode-MIXED.
- At ~21:35 the user removed a user-installed underclock tool. Before:
  cpu7 `scaling_max_freq` 3072000, cpu0 2745600. After: cpu6/7 4320000,
  cpu0–5 3532800 (stock). Pre-launch reads confirmed stock caps before
  every later arm.
- Labels: `d1-base-a` and `d1-base-b` ran under the HMS "underclock 3.07";
  every later arm is "stock". `clock-b` was dropped (at most one clock arm);
  `base-stock-a`/`base-stock-b` were added as the stock base pair (the DVFS
  answer). `performance_mode` was left at 1 at the end per steer (not
  restored to 0).
- Thermal rules were revised twice: (1) D1b replaced the 70 °C stop with
  wait-<50 °C, stop only on cpu-* > 95 °C or emu freq < 2.0 GHz for >5
  consecutive race ticks; (2) after `clock-a` read 104.7 °C with the
  governor still holding 4.2 GHz, the orchestrator ratified continuing,
  with kill only on any zone >= 110 °C or cpu7 < 2.0 GHz for >5
  consecutive ticks. No arm ever reached either kill condition
  (max 104.7, zero ticks < 2.0 GHz on all 16 runs).

## Table (analyze.py output, full matrix)

Race windows follow the metric-dip core checked against screenshot
gate/pause walls; ticks bracketed +-5 samples. `base-a` window (50,68)
differs from Part 1's (65,75): the dip core is samples 50-70, so Part 1's
ms/f row used the late half of the race. Busy = thread CPU-s / sampler
wall-s over the race ticks. `--` = not applicable (counters-only / crash).

```text
tag | regime | pace | min50-90 | tail120+ | emu ms/f | vid ms/f | emu busy | vid busy | cpu7 mean/min/max GHz | tmax cpu/gpu C | native_exc | hook_fb
d1-base-a | underclock-3.07 | 1.071x | 0.952@s60 | 1.965 | 27.42 | 7.96 | 0.89 | 0.26 | 2.98/2.25/3.07 | 74.4/50.5 | 371619 | 427506
d1-base-b | underclock-3.07 | 1.071x | 0.943@s60 | 1.975 | 27.24 | 7.76 | 0.88 | 0.25 | 3.02/2.25/3.07 | 76.8/52.9 | 372735 | 427698
d1-clock-a | stock | 1.273x | 1.185@s50 | 2.230 | 26.35 | 11.19 | 0.92 | 0.39 | 4.28/4.09/4.32 | 103.5/61.7 | 442751 | 439650
d1-detnone-a | stock | 1.364x | 2.252@s75 | 2.221 | 23.61 | 10.87 | 0.96 | 0.44 | 4.31/4.20/4.32 | 104.3/64.1 | 466467 | 443754
d1-base-stock-a | stock | 1.273x | 1.213@s50 | 2.221 | 26.42 | 11.21 | 0.93 | 0.39 | 4.30/4.09/4.32 | 103.9/64.5 | 438749 | 438968
d1-nullvideo-a | stock | 1.250x | 1.198@s50 | 2.212 | 24.39 | 10.40 | 0.93 | 0.39 | 4.30/4.20/4.32 | 104.3/63.7 | 439135 | 439034
d1-detnone-b | stock | 1.364x | 2.261@s75 | 2.238 | 24.91 | 12.03 | 0.96 | 0.46 | 4.32/4.32/4.32 | 104.3/62.9 | 469006 | 444186
d1-base-stock-b | stock | 1.273x | 1.230@s50 | 2.232 | 24.20 | 10.08 | 0.92 | 0.38 | 4.31/4.20/4.32 | 103.9/62.1 | 443442 | 439768
d1-nullvideo-b | stock | 1.273x | 1.212@s50 | 2.208 | 24.45 | 10.21 | 0.92 | 0.39 | 4.32/4.32/4.32 | 103.9/64.5 | 440152 | 439212
d1-capped1x | stock | 1.000x | 0.999@s50 | 1.000 | 25.31 | 11.87 | 0.58 | 0.27 | 3.79/3.28/4.32 | 94.6/57.9 | 180619 | 394932
d1-menu-only | stock | counters-only | 1.226@s50 | nan | -- | -- | -- | -- | -- | -- | 120621 | 384672
d1-menu-pre | stock | counters-only | nan | nan | -- | -- | -- | -- | -- | -- | 46640 | 11495
d1-dispatch | stock | 1.250x | 1.173@s50 | 2.218 | 24.18 | 10.13 | 0.92 | 0.39 | 4.31/4.20/4.32 | 104.3/62.9 | 442251 | 439562
d1-control-probe | stock | CRASH/ABORT (no shutdown counters)
d1-control-probe-fb | stock | CRASH/ABORT (no shutdown counters)
d1-cache-late | stock | 1.273x | 1.185@s50 | 2.229 | 26.24 | 11.05 | 0.92 | 0.39 | 4.29/4.09/4.32 | 103.9/63.7 | 487752 | 447338
```

Pre-launch settings: all stock arms `performance_mode=1 fan_mode=4
cpu7max=4320000 cpu0max=3532800` (read back each launch, in
`run-notes.log`). Thermal waits (<50 °C gate) elapsed: base-b 1s, clock-a
31s, detnone-a 31s, base-stock-a 0s, nullvideo-a 31s, detnone-b 1s,
base-stock-b 0s, nullvideo-b 31s, capped1x 31s, menu-only 0s/1s(r2),
menu-pre 31s, dispatch 1s, control-probe 0s, control-probe-fb 61s,
cache-late 31s (full log in `thermal-waits.log`).
Emu thread PSR=cpu7 on every placed tick of every arm; affinity verified
at sample 10–15 in each run.json.

## Per-arm race anchors (screenshot-verified, HUD timer visible)

- base-b: gate GO! 0:00 @21:03:32, 0:12 5th 44MPH @21:03:44, 0:15 5th 39MPH
  @21:03:46, pause @21:03:48. Pace 15/14 = 1.071x (replicates base-a).
- clock-a: 0:03 5th @21:09:33, 0:14 5th 40MPH @21:09:41, pause @21:09:43;
  gate ~21:09:30. Pace 14/11 = 1.273x. cpu7 race mean 4.28 GHz (cap moved).
- detnone-a: 0:05 6th 50MPH @21:16:30, 0:15 5th 38MPH @21:16:36, pause
  @21:16:38; gate ~21:16:25. Pace 15/11 = 1.364x. Boot-to-gate +19s vs +35s
  EGL (menu phases much faster without determinism sync). TRAJECTORY
  MATCHES base (0:15 frame same family: 5th/7%/38-39MPH airborne).
- base-stock-a: 0:03 5th @21:23:23, 0:11 5th 50MPH @21:23:29, 0:14 5th 41MPH
  @21:23:31, pause @21:23:33; gate ~21:23:20. Pace 14/11 = 1.273x.
- nullvideo-a: 0:03 5th @21:29:46, 0:11 5th 52MPH @21:29:52, pause @21:29:56;
  gate ~21:29:43. Pace 15/12 = 1.250x. Screenshots NOT blank (rendered
  normally). Anchor used: stock-base window gate ~45-50 / pause ~58-62;
  the brief's guessed ~100 / ~115-120 does not match any arm's dip or
  screenshots and was not used. fps/vps read 0.000 on ALL arms incl EGL
  (headless, no present stats), so they do not indicate the backend.
- detnone-b: 0:02 5th @21:37:18, 0:12 5th 39MPH @21:37:24, 0:15 5th 46MPH
  @21:37:26, pause @21:37:28; gate ~21:37:16. Pace 15/11 = 1.364x.
  TRAJECTORY MATCHES (0:12 arch same scene as base-b). 0:15 46 vs
  detnone-a 38 MPH is normal inter-repeat noise (base-a/b also differ 44
  vs 39 at 0:15 under deterministic EGL), not divergence.
- base-stock-b: countdown 0:00 @21:43:40, 0:11 5th 51MPH @21:43:50, 0:14 5th
  39MPH @21:43:52, pause @21:43:54; gate ~21:43:41. Pace 14/11 = 1.273x.
- nullvideo-b: briefing @21:50:15, 0:14 5th 39MPH @21:50:29 (frame-identical
  to base-stock-b 0:14); gate ~21:50:18. Pace 14/11 = 1.273x.
- capped1x: title @21:56:44, setup @21:57:04, event select @21:57:24,
  loading 91% @21:57:44, 0:07 5th 48MPH @21:58:04, pause @21:58:20; gate
  ~21:57:57. Pace 15/15 = 1.000x (cap exact). Busy fractions in race:
  emu 0.58, video 0.27.
- dispatch: gate countdown 0:00 @22:09:21, 0:15 5th 38MPH @22:09:33.
  Pace 15/12 = 1.250x.
- cache-late: countdown 0:00 @22:21:28, 0:14 5th 46MPH @22:21:40;
  gate ~22:21:29. Pace 14/11 = 1.273x.
- menu-only (95s): attempt 1 hung single-threaded at boot (futex_wait,
  zero stderr, affinity threads never appeared; no tombstone; killed by
  its own timeout; transient — attempt 2 clean). Attempt 2 ends in the
  pause menu (last shot + speeds 75-85 = 2.28 tail): under stock timing
  gate is ~sample 45-50, so timeout 95 overshoots the race. Kept as a
  race+tail counters point (native_exc=120621 hook_fb=384672).
- menu-pre (timeout 40, added correction): ends in the My Rules menu, last
  sample=30, no race dip. Pre-race baseline: native_exc=46640
  hook_fb=11495.

## Derived numbers (no verdicts)

- In-race exception rate, stock: (base-stock-a − menu-pre) / 11 s wall =
  native_exc 35,646/s, hook_fb 38,861/s. Underclock reference with the
  stock baseline (mixed-regime caveat): (base-a − menu-pre) / 14 s =
  23,213/s and 29,715/s.
- Dispatch samples (`STATICRECOMP_DISPATCH_SAMPLES=1`, hand launch, same
  command line otherwise): 176,374 samples total; 0 (0.000%) at
  0x00000800–0x0000081C, 0 at 0x00000500, 0 at 0x00000900. Top 10 PCs:
  802b1694 x32867, 801c3358 x26826, 80286190 x16709, 80286168 x16532,
  802a2c44 x7243, 8029d1f4 x7040, 8029d4bc x7027, 8029d7c4 x6993,
  8029d7f8 x6973, 8029d2e8 x6964 (full list: 16 `dispatch-site` lines in
  `d1-dispatch.err`).
- control-probe: trial binary sha verified against `trial/build.json`
  (c59d173e…). Probe file pulled with exactly ONE row (`configured`,
  at=-1): per-callback update/render rows appear ONLY during a trial.
  The no-trial run FIFO-panicked mid-race (see below), so no CPU/wall
  medians or p95 exist. Fallback smoothing trial (`--trial-at 128
  --trial-secs 30`, labelled `d1-control-probe-fb`) panicked identically
  at ~sample 55 before reaching wall 128. Question blocked.
- Crash records (2): `d1-control-probe` and `d1-control-probe-fb` both
  aborted with `FIFO is overflowed by GatherPipe! CPU thread is too
  fast!` (GatherPipeBursted, CommandProcessor.cpp:394) at ~sample 55 in
  the race dip (rows 40-55: 1.05-1.40), after reaching 0:11 5th.
  Deterministic across both attempts, not flaky. 28 sampler ticks each,
  no shutdown counters (abort, not graceful stop). The trial TU plausibly
  lacks the pace binary's FIFO fix; at stock 4.3 GHz the CPU thread
  outruns the video thread in the race scene. Pace-binary arms (same
  scenes, same clocks) never panicked.
- Shader cache: after the graceful-stop 330s `cache-late` run, still NO
  `<user dir>/Cache` (19M user dir: Config/Dump/GC/Load/ScreenShots/Wii/
  config.ini only) and zero shader/cache lines in err+out. Nothing fixed.
- Temperatures: every stock arm's prime-cluster zone cpu-1-1-1 reads up
  to exactly 104.7 (identical full-run max on 7 arms: likely a reading
  clamp, not coincidence); the sensor is live (reads 46.5 idle post-run). 70-92 °C
  was normal per the revised rules; 95-104.7 occurred in-race on all
  stock arms with no freq collapse (governor held >= 3.28 GHz), no crash,
  no tombstone. capped1x peaked 94.6 (coolest full arm).

## Exact commands

Pre-run each arm (all `adb -s 622c49b1 shell …`): `ps -A | grep
moderngekko` empty (checked), LEASE contains `D1`, `/tmp/d1b_thermal_wait.sh
<tag>` gate to all cpu-* < 50 °C, then a settings snapshot
(`performance_mode`, `fan_mode`, cpu7/cpu0 `scaling_max_freq`).
Launch shape (all arms; `run` = `python3 tools/android_trial.py run`):

- base-b/clock-a/detnone-a/base-stock-a/detnone-b/base-stock-b:
  `run --binary D1/moderngekko-run-pace-egl --tag <tag> --output
  D1/<tag>-receipts --template {aff-tpl|aff-detnone} --movie m3-menu.dtm
  --module gGXBE69_recomp.so --graphics OGL --idle on --affinity
  emu=80,video=40 --sampler --screenshot-seconds 2 --timeout 300 --serial
  622c49b1` (clock-a: mode already 1 via user UI, no `settings put`
  needed, no restore per steer).
- nullvideo-a/b: same with `--graphics Null --template aff-tpl`.
- capped1x: same with `--template m6h` (no EmulationSpeed line = 1.0).
- menu-only: same base shape with `--timeout 95`. menu-pre: `--timeout 40`.
- dispatch: hand launch `/tmp/d1b_dispatch.py` (imports
  tools/android_trial, wraps launch_env to add
  `STATICRECOMP_DISPATCH_SAMPLES=1`; identical push/template/affinity/
  sampler/pulls; exact remote command line saved as
  `d1-dispatch-receipts/d1-dispatch-remote-cmdline.txt`).
- control-probe: trial binary `/Volumes/Extreme SSD/android-spike/trial/
  moderngekko-run-trial` with `--build-json trial/build.json`,
  `--probe-quiet`, no `--trial-at`, `--timeout 300`.
- control-probe-fb: same + `--trial-at 128 --trial-secs 30`.
- cache-late: base shape with `--timeout 330`, then
  `ls -R user-d1-cache-late/Cache` + `find -iname '*cache*'` + grep of
  both logs for shader/cache lines.

## File list (new in Part 2)

- `D1/` on the SSD, added: `d1-base-b`, `d1-clock-a`, `d1-detnone-a`,
  `d1-base-stock-a`, `d1-nullvideo-a`, `d1-detnone-b`, `d1-base-stock-b`,
  `d1-nullvideo-b`, `d1-capped1x`, `d1-menu-only`, `d1-menu-pre`,
  `d1-dispatch` (incl. `-remote-cmdline.txt`), `d1-control-probe`,
  `d1-control-probe-fb`, `d1-cache-late` receipt dirs (each: err/out,
  GFX+Dolphin-post, run.json, sampler.log, shots; probe jsonl only for
  the two probe arms, 1 row each); `run-notes.log` (per-arm settings,
  anchors, decisions); `thermal-waits.log` (appended).
  `D1/analyze.py` extended to the full table (lives on the SSD, not in
  git). Pace binary and module unchanged (84de2c22…).
- Repo: no changes, no commits (Step 0 flags already committed as f2ca65b;
  analyze.py is SSD-only per brief).

## What I could not do

- control-probe per-callback medians/p95: blocked by the deterministic
  FIFO panic (needs a FIFO-fix trial relink; M4/S1 territory).
- clock-b: dropped per orchestrator steer (at most one clock arm; the
  stock pair answers the clock question instead).
- menu-only as briefed (`--timeout 95` stops before the race): false
  under stock timing; corrected with `menu-pre` (`--timeout 40`).
- Null-backend screenshots were expected blank but render normally; the
  brief's nullvideo sample anchor (~100/~115-120) matches no arm and was
  replaced with the measured stock window (43-57), stated above.
- No verdicts, per the plan: the numbers above are the deliverable.


