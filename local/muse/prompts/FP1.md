# FP1 — pace the guest to real time when it can outrun it (muse, 2 h, Mac)

## Why
On the Mac the F1/F2 builds run menus at **1.287×** (F1 B2): guest vsyncs aren't paced, only host presents are (`SetTargetFPS(60)`, `ps2_runtime.cpp:~1153` at `0ed07c4`). For Brad's play (Mac/iOS menus, and the Odin later) the game must never run faster than a PS2: 59.94 guest vsyncs per wall second max. Speed runs must keep measuring headroom, so they need an unpaced knob.

## Correct-behaviour model and observables
- Default (play): guest VBlank events never outrun wall clock: over any 5 s window, guest vsyncs/s ≤ 59.94 (+1 % tolerance); below 1× nothing changes (no added sleeps when behind).
- `PS2X_UNPACED=1` (dev/speed): today's behaviour, byte-for-byte.
- Pacing must not change guest state: det-hash identical paced vs unpaced to t2400 under `PS2X_DETERMINISTIC=1` (pacing only adds wall-clock waits; if the deterministic mode already decouples guest time from wall time, say where).
- Audio: the SND host stream at 48 kHz should stop underrunning in paced menus (count underruns before/after in the menu window).

## Steps
1. Read how guest VBlank ticks are scheduled vs wall clock (EeScheduler VBlank events, `[vsync-rate]`, host present/`WaitTime` path); cite file:line (grep; `lsp` isn't available here). Fork worktree `~/dev/ssx3-work/FP1/PS2Recomp`, branch `fp1-pace`, from fork `ssx3` `0ed07c4`.
2. One implementation: a wall-clock deadline per guest vsync (next = prev + 1/59.94 s; if ahead, sleep until the deadline; if behind by > 2 frames, resync the deadline instead of bursting). Default on; `PS2X_UNPACED=1` disables. Unit test of the deadline logic with a fake clock.
3. Suite from the worktree root. Mac boots (paraLLEl env + `PGS_HIER_BINNING=force`, I26-FAST, empty mc0, `PS2X_SOUND=1`, one slot each): **P1** paced det boot to t2400 vs **P2** `PS2X_UNPACED=1` det boot → det-hash identical; per-phase vsyncs/s table (menus ≤ 1.0× paced; race unchanged); underrun counts in menus.
4. Update the lane tooling that measures speed (`local/research/{F1,F2}/launch.py`, `f1_boot.py`/`f2_boot.py` patterns, `local/research/N11/launch.py`) to set `PS2X_UNPACED=1` — list every script you changed; don't touch device play envs.
Budget: ≤ 2 builds, ≤ 3 boots, 2 h. Never push; runner-dir check empty; text only in git. Deliverable `local/research/FP1/REPORT.md`; commit `[FP1] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push. Hand back; the orchestrator decides.
