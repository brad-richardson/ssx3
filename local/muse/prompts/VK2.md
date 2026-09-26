# VK2 — fix the Android Vulkan present's buffer-release and lifecycle bugs (Opus, ≤ 6 h)

## Goal
RV5 (`docs/research/review-2026-09-26-astra-f6.md`, read **B1, B2, S1** and "Areas checked" fully) found that VK1's default-on Android present (fork `ssx3` `fb28d99`) can let the GPU overwrite an AHardwareBuffer before SurfaceFlinger releases it: **B1** a failed/timeout release wait is ignored and the slot is written anyway (also `poll()` `revents` unchecked, `EINTR` handling); **B2** a window change clears ownership and closes release fds immediately, and old-layer callbacks mutate the records of the buffer's new use (keyed by raw pointer); **S1** every retired `ASurfaceControl` is leaked (`graveyard` never drained, `release` never called). Short Odin runs never hit these paths. Fix all three so the Vulkan path can ship to Brad's Odin by default.

## Facts
- Code: `ps2xRuntime/src/lib/gs/ps2_present_vk_android.cpp` (sink), `ps2_present_vk.h`, `ps2_gs_parallel_backend.cpp` (`presentVk`, slot pool), `ps2_runtime.cpp` (window lifecycle hooks). VK1's report `local/research/VK1/REPORT.md` (design, Part 2B, gaps) and its Odin driver `local/research/VK1/launch.py`, `restore-play.sh`.
- Android contract: a buffer may be reused only after the release fence for **every** pending reference signals; a timeout grants no ownership; detaching a layer still delivers release for its last buffer when the transaction registers completion (links in RV5).
- Build: F5 Android recipe on bytesize (hold the ssh; `ps aux | grep -v grep` first; F6 and BA1 also build there). Mac suite via `local/tooling/build/mac_build.sh` (the sink's pure logic should be unit-testable on the Mac if you separate it from the NDK calls).

## Required design (RV5's fixes; you may improve, not weaken)
- Wait failure never grants ownership: keep the slot unavailable, keep its fence, propagate failure; drop the new frame or use a genuinely free slot; persistent failure → detach, retire the pool, fall back to GL. `EINTR` retried within one deadline; require `POLLIN` in `revents`; count callback timeouts and fence timeouts separately.
- Track each submission by (allocation id, layer generation, sequence). Callbacks resolve only their own submission; stale callbacks close their fd and never insert/alter current records. Register completion for the detach transaction. Window change retires old slots until their callbacks/fences finish (a refcounted retired pool is fine).
- Retire `ASurfaceControl`s with outstanding-callback accounting; release when no callback can name them; bounded live-layer / fd / record counts.

## Tests
1. Mac unit tests of the sink state machine with a fake NDK layer: delayed callbacks, unsignaled fence, `EINTR`, `POLLNVAL`, same-pointer TERM/INIT_WINDOW with callbacks outstanding, resolution change mid-flight, 100 recreate cycles → assert no blit into a held slot, no stale mutation, bounded counts.
2. Odin (≤ 6 launches; lease, keyguard, AC ≥ 20 %, cool-down, force-stop after each; Brad's play state restored after every run): (a) a lifecycle stress run — 20 background/foreground cycles plus 5 app switches in a race, logging live fd count (`/proc/<pid>/fd`), SurfaceFlinger layer count for the app, `vk_*` counters, and one screencap after each 5 cycles viewed; (b) one normal ABBA pair vs F6's APK at 1× to show no speed change; (c) pixels via gralloc at two ticks (VK1's `--compare-ticks`).
3. Mac det-hash unchanged (guest untouched): `baseline.py compare` vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`.

## Rules
Fork worktree `~/dev/ssx3-work/VK2/PS2Recomp`, local branch `vk2` from fork `ssx3` **tip** (`git fetch fork`); never push; runner-dir check empty; suite green. Never touch Brad's `files/mc0/`; iPhone not involved. ≤ 6 Android builds. Text only in git. First unexpected failure: save the error and hand back.

## Deliverable
`local/research/VK2/REPORT.md` (each RV5 finding → fix → test that proves it, stress table, ABBA, pixels, SHAs, fork commits, gaps) + `[VK2]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`), no push.
