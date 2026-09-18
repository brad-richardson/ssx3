# Current numbers ledger

One table for every quoted metric. Documents cite rows here instead of
restating values. Status: **live** (trust it) | **contested**
(conflicting evidence, do not quote) | **stale** (superseded config,
re-run before quoting) | **void** (measured broken, never quote).

Rules that keep this table honest (perf-review §1+§7):

- Verdict-grade runs get an exclusive host AND device: no sibling
  builds, runs, or device shells during the window.
- Under any cap, report host CPU-ms per guest frame (or busy fraction)
  as the primary number; speed is pass/fail only (it saturates at 1.00
  and hides wins as idle).
- Uncapped means `EmulationSpeed = 0` (true unlimited), never 10.
- Every race number is screenshot-verified as racing (timer/HUD/slope);
  menu pace is never reported as race pace.
- Every receipt records module sha, backend (true, post-movie-override),
  cap, determinism mode, vertex loader, and validation-layer state.

## Live

| Metric | Value | Date | Device / config | How measured |
| --- | --- | --- | --- | --- |
| Odin race pace, OGL | 0.83× mean / 0.63× low (~50/~38 fps) | 09-17 | Odin 3, m3-menu verified racing (gate→0:07/49 MPH), dual-core detGPU, idle ON, null audio, speed 10 fixed | 4–5 sample window, `pace-hunt/pace-menu-egl-receipts/` |
| Odin race pace, Vulkan (true) | 0.73× mean / 0.64× low (~44/~38 fps) | 09-17 | Same, backend-patched DTM | Same, `pace-menu-vk-receipts/` |
| Odin menu pace | ~1.3–1.4× OGL, ~1.5× VK | 09-17 | Same runs, menu windows | Same receipts |
| Desktop menu ceiling | 3.89× OGL / 4.0× Metal / 6.6× idle-skip | 09-17 | Mac, m3-menu, post-throttle-fix | pace-hunt Phase 1 |
| Throttle proof | speed9: 0.15× pre (= predicted 0.1626×) → 3.66× post; speed10 menus 3.89×; speed1/2 intact; throttle sleep 56% → 0% | 09-17 | Desktop + Odin | `1f1bc2d` |
| FIFO fix | Control panics sample 140 (tombstoned GatherPipe stack); fix runs clean to completion, zero tombstones; desktop baseline panics ~129 s, fix exits 0 at 200 s; movie A/B 2234-prefix identical | 09-17 | Odin + desktop | `309f639`, `panic-fix/` |
| Pinned PAUSE tail, NOT race (emu→7, vid→6) | 1.974× (+25%) / 14.93 ms/frame (−19.5%) vs 1.578×/18.52 unpinned; samples 120–270 are the scripted post-race pause menu | 09-17 | Odin 3 (2+6, prime cpu6–7 @4.32GHz), m3-menu EGL, speed 0 | `23c5b86`, `affinity/` (pin2/both agree; flag replicates manual within 0.6%) |
| Pinned RACE window (gate→last racing shot) | HUD pace base 0.938 → pin2 1.000 / both 1.071 / fd-pin 1.00 (±20%: 5 s CPU ticks over 14–16 s windows); lows 0.63–0.70 → 0.94+ are the LOAD phase, not racing | 09-17 | Same runs | `affinity-summary.json` results.race_hud_pace; "remainder is GPU-driver-bound" there is an inference from the desktop OGL det-GPU profile, contradicted by M7 on the Odin (emu thread ~98% busy, video 15% of samples) — treat as unproven |
| Pinned load dip | 0.70 → 1.15 (+64%); lows 0.63–0.70 → 0.94+ | 09-17 | Same | Same; FD alone +37%, FD+pin stacks ≈1.41× |
| Priority / quarantine | renice −10: nil; emu→cpu0 control: −41% tail | 09-17 | Same | Same (contaminated pin1 kept as negative control) |
| Capped/uncapped reconciliation | RESOLVED: capped saturates 1.0 while sub-capability dips run identically in both regimes — content + cap saturation, no DVFS paradox | 09-17 | Odin, m3-menu capped arm + busy fraction | Affinity hunt |
| Snow scorer calibration | clean ≤0.05 (iPad) / ≤0.08 (Odin menu); corrupt ≥0.17 transition / ≥0.38 full; threshold 0.12 | 09-17 | Archived shots | `tools/gamecube_snow_check.py` |
| Onscreen trial | 25/25 presented + correlated | 09-17 | Odin onscreen | `8df3c42` |
| FP-unavailable fault rate, desktop | ~1,640/s in-race (41,022 in a 25 s race window); ~610–690/s whole-run average (menus dilute) | 09-17 | Mac, C backend module, `hle_vectors=1` (syscall vector already HLE'd) | `native_exc` counters in `android-spike/codegen/` ab2 receipts and RESULTS.md, read by M2; per-fault host cost NOT yet measured (M2b); Odin rate NOT yet measured (D1b dispatch-samples arm) |
| Odin clock caps | The 3.072 GHz prime / 2.75 GHz mid `scaling_max_freq` caps seen in D1 part 1 were a user-installed underclock tool running by default; removed 09-17 ~21:35, stock caps now read cpu6–7 4.32 GHz, cpu0–5 3.53 GHz, GPU max 1.1 GHz. `performance_mode` 0/1 never changed the caps. **Every Odin number dated 09-17 before ~21:35 (pace hunt, affinity, D1 base-a/base-b) was measured underclocked at ≤3.07 GHz on the emulation core.** D1b re-runs base at stock; the stock-vs-underclock base pair is the DVFS answer | 09-17 | Odin 3 | adb sysfs read-back; `android-spike/D1/REPORT.md` Part 1 for the underclocked arm (emu core 3.072 GHz every race sample, cpu zones 74–92 °C) |

## Contested

None currently. (Resolved 09-17: M5-vs-0.83× — see Live "Capped/uncapped
reconciliation".)

## Stale (re-run before quoting)

| Metric | Why stale |
| --- | --- |
| Desktop cost table ("needs 1.3–1.9×") | Predates the FP wave by a day; taken with Metal validation on |
| M5 profile ("CPU core now the frontier") | Module predates Wave B (no fast-FP, no conversion split) |
| "Endian helpers 12.1 → 0.00" | Reads "inlined, now unattributable" — cost moved into `func_*` bodies |

## Void (measured at the phantom 1.16 wall — never quote)

fast-FP "0.00 prize" + STOP decision · "every CPU opt ~0%" ·
determinism-off 0.0% · pinning 0.0% · EGL==Vulkan to 4 decimals ·
EFB-2× "full speed" · desktop 1.17 bind + validation-on/off-identical ·
psq wall-clock null · "1.16 is STRUCTURAL". All re-measured or queued
for re-measurement off the wall (perf-review §1, `todo.md` Now).
