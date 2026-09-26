# CP1 — Odin critical-path timeline on the MTVU play build (muse, 3 h)

## Goal
F7 (`local/research/F7/REPORT.md`): Brad's Odin play build runs the race at **0.391×** with `PS2X_MTVU=1 PS2X_VU1_BLOCKS=1` (GameThread pinned to cpu6, MTVU unit to cpu7), 0.425× with LAG. With MTVU the long pole moved to the **unit thread** (VIF1 + VU1 + GIF + GS frontend) and possibly the **GsWorker** blocked in paraLLEl `flush_submit` (VK1 2A: 23 ms/present at 1×). RV4 §3 (`docs/research/review-2026-09-26-astra-perf.md`) ranked a matched-window critical-path timeline as the single most decision-changing measurement. Produce it: per thread, running vs blocked, and on what, for the race window, so the next speed lever is chosen from data.

## Facts
- Play state: `~/dev/ssx3-work/odin-play/` (APK `825b436d…`, env `ef9f94e1…`); restore with `local/tooling/odin_restore_play.sh <LABEL>` after every run. **Every install/launch/force-stop holds the lease via `local/tooling/odin_lease.sh`.**
- Driver: F7's `local/research/F7/launch.py` + `cooldown.py` (`--env`, cool-down to status 0 + fixed 180 s). Profiling: N12's method (`local/research/N12/REPORT.md`: `simpleperf record -g --app`, symbolization on the mini with NDK host simpleperf + the unstripped `.so`). The unstripped `.so` for `825b436d…` is in VR3's bytesize build tree (`/home/brad/vr3/PS2Recomp/android/app/build/intermediates/` or `.cxx/RelWithDebInfo/*/obj/arm64-v8a/`); check its Build ID against the APK's.
- Existing counters: `[mtvu] threaded` (waits by reason), `[gs:parallel] sync` (flush_submit calls/wall, frame-context waits), `[present-vk]`, `PS2X_VSYNC_RATE_LOG=1`.
- Off-CPU time: use `simpleperf record --trace-offcpu` (or `-e sched:sched_switch` if allowed for a profileable app) and per-thread `/proc/<pid>/task/<tid>/stat` + `schedstat` sampling; `/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq` for frequency residency. If a method isn't permitted on the device, say so and use the next.

## Runs (≤ 5 launches; play env, 1× pipelined, unpaced, sound on, I26-FAST; the race window ticks ~1900–2500)
1. Clean speed run (anchor) with the counters logged.
2. `simpleperf record -g --trace-offcpu` (or equivalent) for 20 s in the race window.
3. A run with `flush_submit` split: add (fork branch `cp1` from fork `ssx3` `5d5c382`, one Android build, default-off timers in the paraLLEl fork's `flush_submit`: `device->submit` vs the two `submit_empty` vs `drain_compilation_tasks_nonblock`) — only if run 2 shows the GsWorker blocked there on the critical path.
4. Optional: the same timeline with `PS2X_MTVU_LAG=1` (what LAG changes).

## Deliverable table (the point of the lane)
Per thread (GameThread, MTVU unit, GsWorker(s), main, AAudio) in ms per guest frame over the matched window: **running**, **runnable-but-waiting**, **blocked** (with the wait object/reason: MTVU vblank/sync waits, GS queue full/empty, fence/kgsl, futex), and CPU frequency residency of the core it ran on. Then the critical path: which thread gates frame completion, and the top 5 self-time symbols on that thread (VU1 generated code vs VIF1 vs GS frontend vs paraLLEl submit). GPU busy % and, if obtainable, GPU time per frame.

## Rules
Measurement only (plus the default-off timer commit if step 3 runs); never push. Brad's save untouched; `mc0-test` for runs; force-stop after each; keyguard/battery checks. Text only in git (no perf.data). Scratch `~/dev/ssx3-work/CP1/` ≤ 5 GB. First failure: stop, save the error, hand back. Hand back the tables; don't conclude.

## Deliverable
`local/research/CP1/REPORT.md` + `[CP1]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
