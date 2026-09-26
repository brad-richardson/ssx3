# CP2 — Odin timeline on the next play candidate (muse, 2 h, measurement only)

## Goal
Re-aim the 90 % push: after FS2's patched Turnip and VR4's SIMD FMAC land in one APK, produce CP1's per-thread table again (running / runnable / blocked by reason, top self symbols per thread, GPU busy/clock) on the play settings, with and without LAG. Use **PT1's `local/tooling/odin_profile.py`** if it's committed; otherwise CP1's method (`local/research/CP1/REPORT.md`).

## Facts
- Wait for: (1) FS2's Turnip result (`local/research/FS2/REPORT.md`) and (2) the orchestrator's note naming the candidate APK (fork `b97b241`+ with the patched `libvulkan_freedreno.so`). Don't start device work before that note.
- Odin rules: `odin_lease.sh`, `odin_restore_play.sh`, cool-down, keyguard/battery; Brad's save untouched.

## Runs (≤ 4 launches)
Clean anchor (play settings) + profile window; same with `PS2X_MTVU_LAG=0` for the LAG delta. Table as CP1, plus the unit thread's top-25 symbols bucketed (VU1 blocks / SIMD FMAC / issuePair state / commit / VIF1 / GIF+GS frontend / enqueue / libc / kernel).

## Deliverable
`local/research/CP2/REPORT.md` + `[CP2]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push. Hand back the tables; don't conclude.
