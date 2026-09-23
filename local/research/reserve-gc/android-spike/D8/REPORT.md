# D8 — Clock floor under the 60 Hz cap: receipts

Brief: `local/muse/prompts/D8.md` (addition to `docs/plan-120fps-2026-09-17.md`).
Question: capped at 1.0, the Odin parks cpu7 at its 3.28 GHz floor and Crow's
Nest opens at 0.82× — which of (a) user "High performance" mode, (b) a
spin-instead-of-sleep pacer, (c) an ADPF hint restores 1.00× from GO, and at
what thermal cost. Executor: muse, herdr pane wN:p3, 2026-09-18. Evidence root
`/Volumes/Extreme SSD/android-spike/D8/`. No verdicts; tables and receipts only.

## 0. Gate and condition record

- Device gate opened mid-morning (S1b REPORT present, NetherSX2 closed, lease
  absent); claimed `D8` in `/data/local/tmp/mg/LEASE` (verified post-write,
  still held at report time — released at the end, §8).
- Transports: Wi-Fi (`192.168.1.53:5555`, `local/odin-serial`) for the base
  launch, then USB (`622c49b1`, serial file re-read per call, no
  adb-connect/tcpip) after Wi-Fi kept dropping. Base ran over Wi-Fi.
- Host: no desktop emulator runs (brief forbids); host lease read `S2b-build`
  during arms — no host builds were needed (binaries staged earlier).
- Arm (a) `d8-highperf-cap`: SKIPPED — `D8/USER_HIGH_PERF_ON` never appeared.
- Thermal gate per arm (hottest cpu-* zone < 60 °C or 5 min): base 42.6 °C,
  spin 37.6 °C, adpf 43.4 °C, all 0 s waits. Kill rules (zone ≥ 110 °C;
  cpu7 < 2.0 GHz > 5 ticks): never triggered — watchdog logs empty, run-max
  zone 96.1 °C, cpu7 min 3.28 GHz every arm.
- Settings identical all arms: `performance_mode=1`, `fan_mode=4`, cpu0
  2227200/3532800 walt, cpu7 3283200/4320000 walt (min/max/cur read pre-launch;
  cpu7 policy minimum 3283200 = the 3.28 GHz floor). `low_power=0` all arms.
- Battery: base 86%/status 2 (clean); spin 98%/status 3, adpf 97%/status 3,
  both under recorded `D8_BATTERY_OVERRIDE=1`. The status-3 flag read
  "discharging" all day while the level demonstrably rose 3 → 98% on the
  charger; `batterystats` shows `battery_charging_enforce_level=90` as the
  plausible mechanism (charge-limited, not draining). Safety purposes met
  (charge margin, saver off, thermals gated); the residual DVFS-state question
  is a disclosed caveat, and all D8 arms share the condition. Base battery
  status/saver unlogged (predates the battery rule); level 86 documented, not
  marked SUSPECT. Dumpsys on this device reports no instantaneous current —
  battery temperature only (36.0/31.0/32.0 °C at launch).

## 1. Builds

- Source: `d8-src` = `m4-src` copy + committed `f58470d` (M2A rounding guard)
  + `1aa479c` (S3 FP-HLE) hunks, oracle-proven (`/tmp/d8_sync.py`: m4 lacks
  exactly these hunks; post-apply `d8==live` on all 6 StaticRecomp files;
  shas in `D8/stack-sync.txt`). S3 HLE defaults OFF and `SSX_HLE_FP_UNAVAILABLE`
  was unset on all arms (`hle_fp=0` everywhere — no confound).
- `D8/spin.patch`: `SSX3_THROTTLE_SPIN=1` busy-waits (`sched_yield`) instead of
  `sleep_until` when the throttle remainder is under 4 ms (CoreTiming
  SleepUntil; analytics preserved). Activation evidence is run.json env only —
  no log marker (limitation, noted).
- `D8/adpf.patch`: `SSX3_PERF_HINT=1` creates one ADPF session for the
  emulation thread (16.6 ms target, `reportActualWorkDuration` per throttled
  frame; dlopen/dlsym, no new link edge). Activation PROVEN: spin/adpf arms'
  `.err` carry `[ssx3-perf-hint] ADPF session created for emulation thread
  (16.6 ms target)` (adpf) and its absence (spin/base). NDK android-35,
  Odin SDK 35. PowerManager sustained-mode via JNI not attempted (out of scope).
- `D8/shots.patch`: committed MG-egl screenshot hunks incl. the `!headless`
  gate removal (S1b-anchored). Device-verified: 157/160/160 real PNGs.
- Build: M4 recipe verbatim, `-j4`, fresh `core-egl-d8-build`, APFS relink
  workaround (ExFAT direct link is a zero-ghost). First configure failed only
  on 30,208 AppleDouble `._*` ghosts from `cp -a` (deleted per M1 precedent);
  rebuilt clean, ninja exit 0. Binary `D8/moderngekko-run-d8`, sha256
  `de84b42db16d71dca6ca1ac9a81ce26f641185fab2d3ed70dae7704371962175`,
  gate strings verified in the staged copy; nm outline-atomics: 3 local defs,
  identical count to the stored M4 LSE binary (flag state equivalent).
- Control binary: `D1/moderngekko-run-pace-egl`, sha256
  `84de2c226c87d831cf275ef1017343ee26c41ed470cfc7b89af66e29222f2033`.
- Skipped as unneeded: MG-headless OBJCXX/run.cpp hunks (M4/D5 lineage builds
  fine without), Mixer.cpp stale hunk (d8==live; committed hunk superseded).

## 2. Launch shape and incident

All arms: `--template m6h --movie m3-crows-nest-3min.dtm --module
gGXBE69_recomp.so --graphics OGL --idle on --affinity emu=80,video=40
--sampler --screenshot-seconds 2 --timeout 330`, movie device-sha verified
pre-launch, DOL `b92162d6…` verified, affinity verified per arm (run.json;
base post-hoc via sampler PSR). Env: base none extra; spin
`SSX3_THROTTLE_SPIN=1`; adpf `SSX3_PERF_HINT=1` (all in run.json env).
Launcher: `D8/d8_run.py` (D1b pattern: imports tools.android_trial, wraps
launch_env; preflight, thermal gate, settings snapshot, kill watchdog).

Incident: adb-over-Wi-Fi dropped mid-watch of d8-base-cap; wrapper crashed
before pulls. The timeout-bounded run completed alone; receipts pulled
manually after reconnect; run.json reconstructed (schema-identical, every
inferred field marked — pid/real-pid from sampler log, affinity post-hoc,
battery level-only, exited inferred from graceful shutdown block).
`d8_run.py` has since gained an adb connect-and-retry wrapper; spin/adpf ran
over USB without drops.

## 3. HUD method (no vision on this host)

Screenshots are not bit-deterministic across runs (11/157 exact matches), so
HUD times transfer by nearest-content match (PIL, 160×90 gray MSE) against
M3b's viewed crows-cap frames, whose HUD seconds are known. Late-race anchors
are near-exact (MSE 40–174); mid-race anchors approximate (MSE 400–1100);
countdown anchors match M3b's "2" frames (MSE 184–411), hence GO = countdown
+ 2.5 s per M3b convention. Anchor error ≈ ±1–2 s → pace ±0.03–0.05; all arms
share the method so comparisons are clean. Metric series (65 rows/arm, exact)
corroborates shape. Guest window: 91 s (M3b crows-cap value), end = last
racing frame before the pause menu.

| arm | HUD first-60 | HUD full | metric mean |
| --- | --- | --- | --- |
| d8-base-cap | 0.946 | 0.978 | 1.000 |
| d8-spin-cap | 0.946 | 0.978 | 1.000 |
| d8-adpf-cap | 0.961 | 0.989 | 1.000 |
| m3-odin-crows-cap (M3b, quoted) | 0.839 | 0.888 | 0.969 |

| arm | emu ms/f, busy | cpu7 GHz mean/min/max | run tmax cpu/gpu °C |
| --- | --- | --- | --- |
| d8-base-cap | 13.06, 0.74 | 3.39/3.28/4.32 | 86.8/55.6 |
| d8-spin-cap | 13.46, 0.77 | 3.73/3.28/4.32 | 96.1/56.3 |
| d8-adpf-cap | 13.15, 0.74 | 3.43/3.28/4.32 | 91.9/54.8 |
| m3-odin-crows-cap (M3b, quoted) | 12.58, 0.65 | 3.83/3.28/4.32 | 104.3/72.6 |

Video thread: 3.23/3.06/3.23 ms/f, busy 0.18 all arms (M3b: 3.10/0.16).
Shutdown counters (native_exc/hook_fb, fallback=0, smc=0 all arms):
base 186037/43974, spin 190813/44942, adpf 190753/44930 (M3b: 179053/42562).

| HUD segment pace | d8-base-cap | d8-spin-cap | d8-adpf-cap |
| --- | --- | --- | --- |
| 0 → 51 | 0.895 | 0.895 | 0.911 |
| 51 → 83 | 1.067 | 1.067 | 1.067 |
| 83 → 87 | 1.000 | (2.000*) | 1.000 |
| 87 → 91 | 1.000 | (0.667*) | 1.000 |

\* Spin's 83/87 anchors are the weakest matches (MSE 4391/820); the 2.000/
0.667 pair is anchor noise around a ~1.0 late race, not a real swing —
adjacent strong anchors (51 @472, 91 @508) bracket it at 1.0.

Time to first 1.00× segment: HUD 51 in all three arms (0→51 below 1.0,
51→83 above), same boundary M3b reported (segments 0:51→1:23 locked 1.00×).

## 4. Observations (no verdicts)

- The D8 control opens at 0.895×, not M3b's 0.839×; full 0.978 vs 0.888.
  Spin and adpf open at 0.895/0.911 with full 0.978/0.989 — indistinguishable
  from the control within anchor error. cpu7 parks at the 3.28 GHz floor
  (min) in all arms including M3b's.
- Differing conditions vs M3b crows-cap, all recorded: launch-zone maxima
  42.6/37.6/43.4 °C here vs 78.4 °C there (5-min thermal timeout); battery
  86–98% here vs unrecorded there; power-state flag status 3 here.
- Spin costs heat, not pace: run tmax 96.1 °C vs base 86.8 °C at same
  emulation throughput (emu busy 0.77 vs 0.74, ms/f within 3%).
- ADPF session creation is proven in-log; its pace/busy/clock numbers match
  the control to the second decimal.

## 5. What I could not do

- Arm (a): orchestrator never signalled the quick-setting switch; skipped.
- No vision or OCR on this host: HUD times transfer by content match (§3)
  with stated error bars; countdown digits identified by cross-match.
- Base `run.json` reconstructed after the adb drop (every inference marked);
  base probe file was never written on device (pull false, same as harness
  behavior); base watchdog/remote-cmdline likewise reconstructed.
- Spin activation rests on run.json env (no log marker in this build).
- Instantaneous battery current: not reported by this device's dumpsys.
- No base repeat: unnecessary — base launched clean (86%/status 2).
- PowerManager sustained-mode: out of scope per brief.

## 6. Files and exact commands

- `D8/REPORT.md` (this file), `waits.log`, `stack-sync.txt`, `spin.patch`,
  `adpf.patch`, `shots.patch`, `build-d8.sh`, `build.log`, `d8_run.py`,
  `moderngekko-run-d8` (sha above), `d8-{base,spin,adpf}-cap-receipts/`
  (run.json, .out/.err, -sampler.log, shots in `shots/` with a
  run-varying `GXBE69` vs `ScreenShots/GXBE69` nesting from adb pull,
  post-run inis, -prelaunch.json, -remote-cmdline.txt, -watchdog.json).
- Arms: `D8_BATTERY_OVERRIDE=1 python3 D8/d8_run.py --arm {base,spin,adpf}`
  (override documented in §0; base ran before the gate existed, at 86%/status 2).
- Analysis: `/tmp/d8_match.py`, `/tmp/d8_nearest.py`, `/tmp/d8_analyze.py`
  (scratch, uncommitted); method mirrors `M3/analyze.py` + D1 sampler math.
- Nothing committed anywhere (brief lists no committable repo files; the
  earlier `--env` harness edit was reverted per orchestrator steer).
- Device lease `/data/local/tmp/mg/LEASE` (was `D8`) removed on completion;
  host lease untouched (not mine).
