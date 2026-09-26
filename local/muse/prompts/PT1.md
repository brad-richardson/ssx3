# PT1 — one-command Odin profiler (muse, 3 h, tooling; no device needed to build it)

## Goal
Every speed lane now needs a per-thread breakdown on the Odin (running / runnable / blocked by reason, top self symbols per thread, stage buckets). CP1 (`local/research/CP1/REPORT.md` §Method, §Symbolization; its scripts in `local/research/CP1/` and scratch `~/dev/ssx3-work/CP1/classify.py`) and N12 (`local/research/N12/buckets.py`) did it by hand over ~2 h. Make it **one command** so lanes get it in minutes, and Brad's 90 % push can re-aim after every change.

## Deliverable: `local/tooling/odin_profile.py`
`odin_profile.py --apk <path> --apk-sha <sha> --label L [--env K=V …] [--window 1900,2500] [--profile-secs 20] [--offcpu] [--symso <unstripped .so or bytesize path>]`:
1. Uses `local/tooling/odin_lease.sh`, the F7/CP1 launch path (cool-down to status 0 + fixed 180 s, keyguard/battery checks, `mc0-test`), installs, runs I26-FAST unpaced to the window, records `simpleperf record -g -e cpu-clock [--trace-offcpu]` for the window **plus** the concurrent schedstat/cpufreq/gpubusy sampler, force-stops, and restores with `local/tooling/odin_restore_play.sh`.
2. Symbolizes on the **mini** (NDK host simpleperf at `/opt/homebrew/share/android-ndk/simpleperf/`; check the unstripped `.so` Build ID matches the APK; pull it from bytesize via `local/tooling/bytesize_lock.sh`-free plain `ssh … cat` if needed — reading a file is not a heavy job) — no bytesize needed.
3. Writes `local/research/<L>/profile/` text reports: per-thread table (CP1 Table 2 format: running/runnable/blocked with the blocked split by wait object — reuse CP1's classifier logic, promoted into the tool), top-25 self symbols per thread, N12-style stage buckets (updated for VU1 blocks `VU1RecompImage<…>::B*`, SIMD FMAC, MTVU, GS frontend, paraLLEl submit), GPU busy/clock, and the `[mtvu]`/`[gs:parallel] sync`/`[present-vk]` counter lines. perf.data stays in scratch.
4. `--from-perf <perf.data> --symso <so>` mode re-analyses an existing capture offline.

## Validation (no new device run required)
Re-run the analysis on CP1's capture (`~/dev/ssx3-work/CP1/odin/R2b/perf-R2b.data` + its schedstat samples + the VR3 unstripped `.so` on bytesize) and reproduce CP1's Table 2 and Table 3 within ~5 %. One live smoke run on the Odin is optional and only if the lease is free (FS2 and AP1 have priority); if you do one, use the play APK and settings.

## Rules
Only `local/tooling/odin_profile.py` (+ a README section in it) and `local/research/PT1/REPORT.md`. Text only in git. Never touch Brad's save; restore play state after any device run. Commit `[PT1] …` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
