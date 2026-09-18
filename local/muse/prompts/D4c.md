# D4c — Display proof, Part 3: presents counted by SurfaceFlinger timestats

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. Runbook:
exact steps, receipts named up front, **tables, no verdicts**. Read
first: `local/muse/prompts/D4.md` (all sections: rules, parity arm,
isolation), `/Volumes/Extreme SSD/android-spike/D4/REPORT.md` (Part 2:
§Parity arm, §Display-timestamp arms, §Timestamps unavailable, §Recipes)
and `/Volumes/Extreme SSD/android-spike/D4/run-notes.log`. Everything D4
Part 2 built stays as is: driver `D4/run-apk.sh` (v11), the calibrated
`at=120 secs=4 budget=154`, capped seed, imm movie, pinned emu→cpu7 and
video→cpu6, APKs `trial-d4.apk` (42c52be2) and `trial-d4-fps.apk`
(19b4a9c9). Evidence root `/Volumes/Extreme SSD/android-spike/D4/`,
new subdir `part3/`.

## Why

EGL frame timestamps return nothing on this Adreno path, so D4 Part 2
could not count distinct display presents. SurfaceFlinger can:
`dumpsys SurfaceFlinger --timestats -enable`, `-clear`, `-dump` prints,
globally and **per layer**, `totalFrames`, `droppedFrames`, a
`presentToPresent` histogram in 1 ms buckets and `displayConfigStats`
(time at 120fps). Verified on the device at 19:35 (`-dump` works, panel
shows `120fps`). Our layer is the APK's surface; find its exact
`layerName` in the per-layer sections while the app runs
(`dumpsys SurfaceFlinger --list | grep -i ssx3` gives the candidates).

## Rules

As D4: device serial from `local/odin-serial` (USB `622c49b1`; do not
use the Wi-Fi serial), claim `/data/local/tmp/mg/LEASE` with
`printf 'D4c\n'` only when it is empty, remove it at the end; if
`dumpsys user | grep State:` shows `RUNNING_LOCKED`, stop and write a
waiting note (never touch the PIN). Thermal and battery rules as D4
(wait for every cpu zone < 50 °C before an arm; battery ≥ 20 and
charging). Host builds not needed (no APK change). Never change device
settings. Never `git add -A`; commit nothing in the repo (all outputs
on the SSD). Time box 3 hours.

## Steps

1. **Sampler script.** `D4/part3/sfstats.sh <tag>` runs on the device
   (push to `/data/local/tmp/mg/`): `dumpsys SurfaceFlinger --timestats
   -enable` then `-clear`, then every 1.0 s append
   `=== <epoch.ms>` + the full `-dump` to `/data/local/tmp/mg/sfstats-<tag>.log`
   until a stop file `/data/local/tmp/mg/sfstats-<tag>.stop` appears or
   the app pid dies; then `-disable`. Wire it into the driver's
   bootstrap the same way `d4-sampler.sh` is started (same cwd fix,
   same run-as caveats do not apply: dumpsys runs as shell). Pull the
   log after each arm.
2. **Analyzer.** `D4/part3/sfstats_analyze.py <log> <layer-substring>
   <swaplog>`: per 1 s tick, for our layer and for the global section:
   delta `totalFrames`, delta `droppedFrames`, and from the delta of the
   `presentToPresent` histogram the median/p95/p99 spacing in ms (bucket
   midpoints); alongside, the swap-hook swaps in the same second from
   the existing swap log. Mark the trial window (request → complete
   wall times from the existing analyzer) and print the window
   aggregate: presents/s, spacing med/p95/p99, swaps/s, and the ratio
   presents/swaps. Test the analyzer on a 10 s idle capture of the
   launcher first (expect ~0 presents once the screen is static).
3. **Arms** (one warm run each, same order, same tags with `-p3` suffix,
   pinned, capped seed, at=120 s=4 b=154, imm movie):
   a. `d4-p3-default` with `trial-d4.apk` (framerate=0);
   b. `d4-p3-120fps` with `trial-d4-fps.apk` (framerate=120, expect the
      `OT_FRAMERATE req=120 rc=0` line and the SF explicit-rate column);
   c. `d4-p3-uncapped-notrial`: the parity configuration (uncapped seed,
      at=999 never fires) for 60 s, as the reference for what the panel
      presents when the emulator runs free.
   For each arm keep: swap log, sfstats log, the in-window screenshot,
   pin log, sampler log, `sf-*.txt` composition dumps, tombstone note.
4. **Report.** Append `## Part 3` to `D4/REPORT.md`: the per-arm table
   (rows: swaps/s in window, SF presents/s in window (layer), SF
   presents/s (global), dropped, present spacing med/p95/p99 ms, swap-
   return spacing med/p95/p99 from the existing analyzer, panel config
   time at 120fps during the run, composition type, explicit-rate
   column), the per-second series for the 120fps arm (before/during/
   after the window), the exact layer name used, the scripts quoted,
   exact commands, receipt paths, "What I could not do". Acceptance
   frame of reference as D4 (≥117 presents/s, med ≤8.6, p95 ≤10, p99
   ≤17 ms); do not declare a pass. Release the lease. Stop.
