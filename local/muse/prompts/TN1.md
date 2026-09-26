# TN1 — Turnip / driver-side tuning on the Odin (muse, 4 h)

## Goal
Brad (09-26) asked what else the driver side can give now that FS2's kgsl poll fix took the race to 0.639×.
The frame is now gated by the MTVU unit (~94 % busy), so driver work pays through **fewer core fights, fewer
compile hitches, less heat**, and occasionally frames. Four bounded probes, each answered with a table; the
orchestrator decides what to adopt.

## Facts
- FS2 Part 3 (`local/research/FS2/REPORT.md` + gate): per race frame, GsWorker ~10 ms run / **~5 ms runnable**
  / ~19 blocked; `flush_submit` 4.7 (≈ `frame_ctx_wait`, the real 4-deep frame-context wait); Turnip runs
  transient compile threads (named GsWorker, ~93 % each) inside the race window. Only GameThread (`PS2X_GAME_THREAD_CPUS=6`)
  and MTVU (`PS2X_MTVU_CPUS=7`) are pinned (`odin-play/ps2x.env`); the GsWorker has no pin knob
  (`PS2X_GAME_THREAD_CPUS` is read at `ps2_runtime.cpp` ~4355).
- Driver: Mesa fork `brad-richardson/mesa` `ssx3` `5a406e36dd4`; build script `local/research/FS2/turnip/mesa-build.sh`
  (no `-Dshader-cache` option set); jniLibs swap `local/research/FS2/turnip/apk-swap-so.sh`.
- `docs/facts.md` ~line 75: the proprietary Adreno driver **lost composite draws, varying per run** (why we ship Turnip).
  Many of our own GS/present bugs have been fixed since (wave64 binner N8X1, GS state SS3, present ownership VK2).
- Base APK for every probe: **F8's play candidate** (the F8 lane builds it now; use its APK/SHA from
  `local/research/F8/REPORT.md` once F8 commits — until then do only the read-only parts P3 and the P2 investigation).

## Probes (hypothesis → observable)
- **P1 GsWorker pin.** H: the ~5 ms runnable is core contention; pinning GsWorker to a performance core away from
  6/7 cuts it. Add an env knob `PS2X_GS_WORKER_CPUS` (default unset = today's behaviour; mirror the
  `PS2X_GAME_THREAD_CPUS` code) — one small fork change on a local branch `tn1` off fork `ssx3`, Mac suite must
  pass, runner-dir check empty. Observable: GsWorker runnable ms/frame and race vs/s, screening pair (knob off/on).
- **P2 shader disk cache.** Find out (source + logcat) whether this Turnip build has Mesa's disk shader cache and
  where it would write on Android (app has no HOME; `MESA_SHADER_CACHE_DIR`). If it's off, one Mesa build with it on
  + the env pointing at the app's cache dir. Observable: compile-thread CPU in the race window on launch 1 vs
  launch 2 (warm), race vs/s, `diff_px=0`.
- **P3 kgsl audit (read-only).** In `src/freedreno/vulkan/tu_knl_kgsl.cc` (and anything it calls on submit /
  wait / present), list every blocking ioctl or wait with its timeout semantics, as FS2 did for the zero-timeout
  case. Table: call site, when it runs on our path (cite FS2's traces), can it sleep, how long. No patch.
- **P4 proprietary-driver recheck (one launch, maybe two).** Launch F8's app on the system Adreno driver (find the
  cleanest switch: an APK without `libvulkan_freedreno.so`, or an env/loader switch — say which), play settings,
  `--compare-ticks 1100,3000` plus shots at 1500/2100/2600. Observable: `diff_px` and visible missing composites;
  if the first run is clean, one repeat (the old failure varied per run). Record race vs/s and GsWorker run ms as
  **screening** numbers. Any missing composite → stop P4, it's still broken.

## Budgets / rules
≤ 2 Mesa builds + ≤ 2 Android builds on bytesize under `local/tooling/bytesize_lock.sh` (`ninja -j8`), ≤ 8 Odin
launches (screen mode, stop 3000 unless a probe needs 4500), 4 h. Odin: every install/launch/force-stop under
`odin_lease.sh`; keyguard + AC + ≥ 20 % before each launch; `odin_restore_play.sh TN1` after every run; fan left
alone. Fork: local branch only, no push. Mesa: local branch only, no push. Write only in `local/research/TN1/`,
`~/dev/ssx3-work/TN1/`, bytesize `/home/brad/tn1/`. First failure: stop, save it, hand back.

## Deliverable
`local/research/TN1/REPORT.md`: one table per probe (with mode labels), pins/SHAs, exact commands, gaps, and a
recommended next action per probe. Commit `[TN1] …` with `git add -f`, trailer `Orchestrated-By: Muse Code`, no push.
