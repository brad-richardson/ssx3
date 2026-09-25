# SS1 — save states for the recomp runtime: feasibility + prototype (Opus spike, ≤ 6 h)

## Goal
Every check boots from power-on: ~36 s to the race on the Mac, ~14 min to the race results, minutes per Odin run. Dolphin's save states made the GameCube harness fast. Brad (09-25) approved an Opus spike: can our runtime save at a vsync and resume bit-exactly, and what does it take? Output: a state inventory, a design, and a working prototype if feasible, all default-off.

## Facts
- Fork `ssx3` `a3efbfe` (pushed). Your worktree `~/dev/ssx3-work/SS1/PS2Recomp`, local branch `ss1-savestate`. Never push; never `git add -f` in the fork; nothing under `ps2xRuntime/src/runner/` changes.
- Why it may be feasible: the scheduler's checkpoint unwind is a longjmp-like exception back to `EeScheduler::run()` (`ps2xRuntime/include/runtime/ee_scheduler.h:20`, `checkpointDue` `:279`), so a guest thread resumes from a guest PC + `R5900Context`, not from a host stack. PF1 (`local/research/PF1/POSTRACE-REPORT.md`) documents the unwind/resume rules.
- The known obstacle (todo): runtime global/static state. Enumerate it (e.g. `nm -m` on the runner for writable `__DATA` symbols in runtime objects, plus `static` locals).
- Build: recipe in `local/research/F5/REPORT.md` `## Exact commands` (or `local/tooling/build/mac_build.sh` if RS1 has landed). Det boots: `local/research/F5/f5_boot.py --mode det` (or `local/tooling/boot/ssx3_boot.py` after RS2), compare with `local/research/GB8/gb8_hashdiff.py`. Det-hash covers rdram, scratchpad, VU1 data/code and eeCycle (`src/lib/Kernel/EeScheduler.cpp:287`), **not** GS VRAM, IOP/SPU2 or pad state, so check those separately.

## Stages
1. **Inventory + design** (commit this before coding): every piece of mutable state with its owner (file:line) and a save/restore plan: EE RAM/scratchpad, per-thread contexts + scheduler/thread tables, kernel objects (semas, events, alarms, handlers), INTC/timers, DMA/VIF/GIF, VU0/VU1 regs + memory + pipeline/scoreboard + recomp run state, IOP HLE (SIF/RPC, CDVD position + pending reads, MC fds, SND/SPU2 voices), pad, GS privileged regs + 4 MB VRAM (paraLLEl readback/upload, GsWorker queue drained), host caches that may be dropped. Where to save: a vsync boundary when every guest thread is at the dispatcher and the GS queue is drained. Mark each item captured / rebuildable / blocker. **If a true blocker appears** (host state that can't be captured or rebuilt), stop after stage 1 and hand back.
2. **Prototype**, default off: `PS2X_SAVESTATE_SAVE_AT=<tick>` + `PS2X_SAVESTATE_PATH=<file>` writes one versioned file (header with the build ID, runner SHA and pins; refuse to load on mismatch); `PS2X_SAVESTATE_LOAD=<file>` restores after init and resumes. Unit tests for the serialization of the pieces you add.
3. **Acceptance** (det build, FR1-R1, sound on): (a) straight run to t2600; (b) save at t2000, exit; (c) load and run to t2600. Pass = det-hash IDENTICAL for ticks 2001–2600, the same snd `cid0` progression, a t2100 frame viewed on both sides (rider, trail, HUD match), and the load→t2600 wall time. Then one load at a race-start state (≈t1720) to show time-to-race. If (c) diverges, bisect by state piece (turn restores on/off) and report the first differing tick + the component; no tuning loops.

## Budgets and rules
≤ 8 builds (incremental), ≤ 16 boots, one mini slot each, each ≤ 600 s. Suite from the worktree root must stay green. Scratch `~/dev/ssx3-work/SS1/` ≤ 10 GB; save files stay in scratch (they contain game RAM: never in git). No Odin or iOS use. Workers don't edit `docs/`. First unexpected failure: save the error and hand back.

## Deliverable
`local/research/SS1/REPORT.md` (inventory table with file:line, design, statics census, acceptance table, times, fork commit list, what an Android/iOS port needs, gaps) + an `[SS1]` commit in this repo (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`); fork commits stay local on `ss1-savestate`. No push. Hand back the tables; the orchestrator decides.
