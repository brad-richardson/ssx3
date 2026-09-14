# Isolated DVD loading-speed experiment

This experiment compares Dolphin's default `FastDiscSpeed = False` with
`True` in fresh native User profiles. Phone defaults, game data, guest clocks,
startup initialization and smoothing guards remain unchanged. Six matched
Mac startup runs reached the main menu in a median **20.104559 s with normal
disc timing versus 14.848015 s with FastDiscSpeed**: 5.256544 s, or **26.15%
less elapsed time**. This is a startup result, not a phone or gameplay speedup.

Pinned `Core/Config/MainSettings.cpp:211` defaults the setting to false.
`Core/HW/DVD/DVDInterface.cpp:1069` treats all reads as buffered when it is
enabled, changing emulated drive latency while preserving actual reads and
game initialization. Source paths are relative to
`third_party/ModernGekko/vendor/dolphin/Source/Core/`.

`tools/loading_speed_spike.py` builds one copied startup observer with the
current active-title-input gate, using existing runtime archives and the
production game module. Its private observer records the effective setting
alongside each startup event. It executes six fresh-process menu runs in
control/candidate/candidate/control/control/candidate order. All use identical
fast-start behavior, configured 1× detail, Metal validation and controller input.
There is no MemoryWatcher or smoothing injection. No shared runtime, module,
vendor source or configuration is rewritten.

The report retains phase wall/guest times, input records, screenshots, complete
runtime/shutdown receipts, config and source hashes, warning lines, and child
CPU totals across the entire bounded run (including time after menu readiness
and launcher verification subprocesses). It requires real
main-menu readiness, the expected effective setting, stable build/game identity
and clean native/graphics execution. Post-run configuration comparison excludes
only the tested `FastDiscSpeed` value and random `Analytics.ID`.

## September 13 paired results

The six 40-second checks ran after the other native profiling, Simulator and
build workloads ended. Each used game assets 027, the same production module
and one isolated player. All six passed the startup/runtime gate; their
effective FastDiscSpeed observations matched the requested setting at every
startup phase. The three controls include two runs after candidate runs, so
the result is not limited to the first process starting with a colder cache.

| Order | FastDiscSpeed | First initialized frontend | Main menu ready |
| ---: | --- | ---: | ---: |
| 1 | False | 14.057396 s | 20.095816 s |
| 2 | True | 8.775648 s | 14.813891 s |
| 3 | True | 8.771950 s | 14.863496 s |
| 4 | False | 14.061685 s | 20.104559 s |
| 5 | False | 14.064977 s | 20.153828 s |
| 6 | True | 8.776455 s | 14.848015 s |

The difference occurs before the first initialized frontend update: its median
moves from 14.061685 to 8.775648 s. Frontend-to-title-resource readiness remains
4.985–4.991 wall seconds, or approximately 4.988319 guest seconds, in both
groups. Main-menu initialization-to-readiness remains 0.417–0.419 s. The
existing title wait and normal initialization still execute. Source semantics
and the isolated setting change support reduced modeled disc latency as the
explanation; this experiment does not time individual reads or decompression.

All six runs show native execution, interpreter fallback, zero JIT fallback
runs, and clean shutdown. There are no invalid accesses, GPU-command errors,
unknown instructions, failed code checks, MemoryWatcher messages or other
warning lines. Each sends one START and releases it on the ordinary transition.
All six final 640 × 491 PNGs were visually inspected: each shows the Main Menu
with Single Event selected. The animated background differs, so this is state
and visual-continuation evidence, not exact-image equality or course acceptance.

Core configuration files match after excluding only FastDiscSpeed and random
Analytics.ID; graphics, controller and frontend configuration hashes match
without exclusions. All archived graphics files contain **InternalResolution
= 1**. The frontend maps `640x528` to scale 1; the first harness also seeded an
unused `EFBScale` key. The current helper uses the correct InternalResolution
key. No renderer EFB-dimension telemetry was collected, so 1× is a configuration
claim. The exact script used for these measurements is archived beside the
report; the seed correction was made only after all six runs completed.

Whole-run child CPU time is 15.39–16.45 s for controls and 16.32–16.49 s for
candidates. Those totals include verification subprocesses and differing time
spent at the menu after startup, so they do not measure loading CPU cost.
`pmset -g therm` reports no recorded thermal/performance warning or CPU power
status before and after; it provides no temperature measurement. OS storage
cache was not cleared. The small repeated sample supports this specific Mac
startup result without establishing physical cold-storage or phone latency.

Evidence: `local/research/loading-speed/paired1/report.json`,
`artifact-audit.json`, the archived `loading_speed_spike.run.py`, per-case
startup/input/runtime/config/PNG artifacts, and the copied build receipt.
Player SHA-256 is `b08ac67c4a28385f748ebc2d40bfa88086526cd6d35612b8735639bf6012c6be`;
module SHA-256 is `ca06dba7726f57547efe2508f9a2ebe437ad249568a30da9e127f51bdd37e547`.
Seven focused tool regressions pass. Production binaries, vendor sources and
phone defaults were not changed.

The next useful check is an opt-in loading comparison that also establishes
course readiness and riding, ordinary boot, and valid card read/write/relaunch
behavior. On-phone measurement remains necessary before adopting this setting.
It does not address the cost of ordinary or repeated gameplay render callbacks.

## Reproduction and remaining scope

```sh
python3 tools/loading_speed_spike.py build \
  --output local/research/loading-speed/player1
python3 tools/loading_speed_spike.py run \
  --player local/research/loading-speed/player1/player \
  --output local/research/loading-speed/paired1 \
  --profile-prefix loading-paired1 --seconds 40
```

Use a quiet machine and fresh output/profile names. These are fresh-process
runs with uncontrolled OS storage cache, not physically cold-storage tests.
Menu timing excludes runtime construction and asset verification. It cannot
establish course-loading performance, phone speed, or memory-card correctness.
Course/card profiling needs separate state anchors for actual I/O, decompression,
resource initialization, emulated device delays and UI timers. Memory-card
transfers model asynchronous 512 KiB/s reads and 96.125 KiB/s writes; no simple
fast-card switch is established by this spike.
