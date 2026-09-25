# VB1 — VU1 stage B: static stall schedules per block (Opus exploratory, 3 h, Mac)

Worker: Claude Code (Opus), exploratory, Brad-approved class. Read `~/dev/AGENTS.md` (exploratory freedom overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, `docs/orchestration.md` §3, then `local/research/{VR1,E57,NP1}/REPORT.md` and `docs/research/review-2026-09-25-fable.md` §3 rank 4. If `local/research/Q1/REPORT.md` exists (local-Qwen research on PCSX2 microVU's hazard analysis), use it as input and check its citations before relying on them.

## Goal
After VR1's stage A (all VU1 cycles in generated code, Mac race 1.44×), VU1 is still ~62 % of Mac busy samples; what remains is the dynamic scoreboard (`commitReadyPipelines`, `calculatePairReadyCycle`, `markPairWrites`) and FMAC exact-result arithmetic. On the Odin, hazard bookkeeping was 25.7 ms of a 121 ms frame before stage A. Stage B: per basic block, precompute stalls from the block-entry pipeline state with a cheap guard (compare the entry scoreboard to the assumed one; fall back to the stage A path on mismatch). Must preserve (E57 sketch step 3): flag-pipeline visibility at exact cycles (FMAND/FSAND/FCAND), Q/P latencies and WAITQ/WAITP, LSU commit before PATH1 consumes a qword, XGKICK per-cycle progress, VI branch backup, E-bit and D/T-bit delay slots, budget truncation at 65,536 cycles, resume at any pair PC.

## Base and oracle
- Base: VR1's branch `vr1-vu1-recomp` at `1f51e48` (stage A + chaining) in a new worktree `~/dev/ssx3-work/VB1/PS2Recomp`, branch `vb1-stageb`; generated sources `~/dev/ssx3-work/vu1gen-ssx3` (game-derived; outside any repo; regenerate into `~/dev/ssx3-work/VB1/gen` if the emitter changes).
- Oracle: `local/research/VR1/` gates: det-hash 2,400/2,400 equal and the CPU-backend strict GS SHA equal vs base (`local/research/E57/check.py`, VR1's `gs_types.py` for paraLLEl per-path). Total VU1 cycles must stay identical (959,411,166 on the route; `PS2X_VU1_RECOMP_STATS=1`). Bit-exact is the only acceptance.
- Speed: Mac, paraLLEl, exclusive lease ABBA vs `1f51e48`, `PS2X_UNPACED=1` if the base has FP1 pacing (it doesn't; `1f51e48` is pre-FP1). Leave at least one slot free between your holds (others need the mini); ≤ 5 min per hold.

## Rules
Never push; never `git add -f` in the fork; runner-dir check empty. Text only in git; generated code never in git. Scratch ≤ 15 GB; delete build dirs you no longer need. Time box 3 h, notebook every ~30 min.

## Deliverables (commit `[VB1] …`, explicit paths, trailer `Orchestrated-By: Claude Code`, no push)
`local/research/VB1/NOTEBOOK.md` and `REPORT.md`: design (block formation, entry-state key, guard, fallback), commits + `--stat`, suite, gate results, speed ABBA, share of VU1 cycles on the fast path, what's left, gaps.
