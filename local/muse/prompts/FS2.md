# FS2 — remove the GsWorker's ~19 ms/frame kgsl wait in paraLLEl's `submit_empty` (Opus, ≤ 6 h)

## Goal
CP1 (`local/research/CP1/REPORT.md`, read Table 2, R3 and the gate) on Brad's Odin play build: the MTVU unit gates the frame and loses 6.7 ms/frame waiting on a full GS queue, because the GsWorker is blocked ~19 ms/frame in a kgsl ioctl. R3 localised it: inside `GSRenderer::flush_submit()` (~4 flushes per present), the **two `submit_empty` timeline-signal submits** take ~5.5 ms each (main submits 6 µs, compile drain 0.4 µs). Find why they block on Turnip and remove or move the wait, keeping GS output identical.

## Facts
- paraLLEl-GS fork `ssx3` `1b3a294` (Granite `166ba21a`); CP1's timer patch is on its local branch `cp1` (`~/dev/ssx3-work/CP1/parallel-gs`, `b0e331a`) + fork branch `cp1` `10dfcb2` (print). Turnip is Mesa 26.x loaded as a HAL module (VK1 D1–D3); no WSI; kgsl backend.
- Hypotheses to separate (with an observable each): (a) Turnip implements timeline semaphores by waiting for prior submissions (emulated timelines / syncobj wait-before-signal) so a signal-only submit blocks until the GPU catches up; (b) `submit_empty` forces a queue flush / `vkQueueSubmit` with a fence the driver waits on; (c) the GPU really is behind and any submit would wait (then batching helps nothing). Check Turnip's source for its timeline path and whether a thread-submit mode exists (`TU_DEBUG` options, `MESA_VK_ENABLE_SUBMIT_THREAD`, etc.), and Granite's `submit_empty` callers (`Device::submit_empty`, `flush_frame`, the GS renderer's timeline use).
- Candidate fixes (one at a time, measured): signal the timeline in the main submit instead of a separate empty submit; one signal per present instead of per flush; move timeline signaling to a submit thread; enable a driver submit thread via env; deepen the GS queue so the unit doesn't back-pressure.
- Exactness: guest unaffected (GS-side only) — Mac det-hash IDENTICAL; rendered output identical: Mac frame dumps at fixed ticks byte-identical to before, and on the Odin VK1's gralloc pixel compare (`PS2X_PRESENT_VK_COMPARE_TICKS`) `diff_px=0`.
- Odin rules: `local/tooling/odin_lease.sh` for every install/launch/force-stop; restore with `local/tooling/odin_restore_play.sh <LABEL>` after every run; keyguard/battery; cool-down (status 0 + fixed 180 s). Driver: CP1's `launch.py` (`--env`, sync-line + schedstat sampler). Android builds: VR3's recipe on bytesize (hold the ssh; one heavy job at a time); VU0 image `-Pps2xVu0RecompDir`.

## Stages
1. Read + hypothesis test (≤ 2 Odin launches with extra timers if needed): which of (a)/(b)/(c); report the evidence.
2. One fix candidate (branch `fs2` in your own paraLLEl + fork worktrees from the fork tips), gates above, then an Odin ABBA pair on the play settings (MTVU + blocks, LAG off) vs the play APK: race rate, GsWorker blocked ms/frame, MTVU GS-queue-full ms/frame.
Stop and hand back. ≤ 4 Android builds, ≤ 8 Odin launches. Never push. Text only in git.

## Deliverable
`local/research/FS2/REPORT.md` + `[FS2]` commits (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`), no push.
