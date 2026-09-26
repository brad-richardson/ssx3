# MT1 — VU1 on its own thread (MTVU), deterministic by design (Opus, staged, ≤ 8 h)

## Goal
Brad (09-26) un-parked MTVU under the new **PCSX2-parity** rule (`AGENTS.md` "Accuracy target"). On the Odin, VU1 is ~47 of the 68 ms race frame (N12 gate), and the game thread's other work is ~21 ms; running VU1 on another core could approach max(VU1, rest) instead of their sum (~1.4× today, more as VR2 shrinks VU1). The det-hash must keep working, so the threaded result must be **deterministic**: the guest must observe VU1 at fixed guest-time points, never host timing.

## Design principle (start here; improve it with evidence, don't weaken it)
Split *guest semantics* from *host execution*:
1. **Semantics:** pick a deterministic guest-time model for VU1 completion that PCSX2 also uses (e.g. PCSX2's default instant-VU1 behaviour, or "completes at a fixed cycle count from kick"), and make the **synchronous** runtime use it. This step may change the det-hash once (a deliberate parity change): validate and re-baseline per the rule.
2. **Execution:** run VU1 microprograms on a worker thread; the EE side continues until it would *observe* VU1 (VU1 data/code memory reads/writes, VIF1 STAT/VU busy bits, MSCAL of a busy VU1, VIF1 unpacks into VU1 memory, XGKICK/PATH1 GS ordering vs PATH2/PATH3, VU0 access to VU1 regs, FBRST, save states), where it waits for the worker. With the semantics fixed in step 1, the threaded build must be **det-hash IDENTICAL to the synchronous step-1 build**, every run. That equality is the correctness proof.

## Facts
- VU1 today: runs synchronously on the GameThread from VIF1 (`processVIF1Data` → `VU1Interpreter::run`, generated images VR1/VB1/VR2), 65,536-cycle budget per program with resume (`docs/facts.md`); XGKICK/PATH1 progress is interleaved with VU1 cycles (`progressXgkick`). RR1 fixed a PATH3 ordering bug (`local/research/RR1/REPORT.md`): the same class of risk.
- PCSX2 reference: `MTVU.h/.cpp` and microVU files are in `local/research/Q1/src/` (read-only; GPL: techniques only, no code). RV7 (`docs/research/review-2026-09-26-astra-emulators.md` §2) and RV4 §4 discuss MTVU's ordering obligations.
- VR2 is concurrently changing the generated VU1 code (`local/research/VR2/REPORT.md`, branch `vr2-blocks`): work at the dispatch/sync layer, keep out of the generated-pair internals, and rebase onto fork `ssx3` when VR2 folds.
- Tools: `local/tooling/build/mac_build.sh` (ccache), `local/tooling/build/bradflix_build.sh`, `local/tooling/boot/ssx3_boot.py` (`--host bradflix` for det boots), `baseline.py` (+ save states), `local/tooling/p_lane_lease.py`. Small-stack test (`PS2X_GAME_THREAD_STACK_KB=512`).

## Stages (stop after each with a table; the orchestrator gates)
1. **Map + design** (commit first): every point where the EE side can observe or affect VU1 (file:line), the chosen guest-time model with the PCSX2 behaviour it matches (cite source), the worker/queue design (bounded queue, ownership of VU1 memory, how VIF1 unpacks into VU1 data memory are ordered against a running program, GS path ordering), save-state interaction, Android/iOS threading (the Odin has two prime cores 6/7; GameThread uses one).
2. **Semantics change, synchronous:** implement the model behind a knob; det boots show it deterministic (two runs identical); visual/sound/race parity check (frames at 1090/1800/2100 viewed, a finished race, SND counters sane); speed pair; new baseline key.
3. **Threaded execution** behind `PS2X_MTVU=1` (default off): det-hash IDENTICAL to stage 2 on repeated runs (Mac and bradflix, 3 runs each, plus 512 KB stack), a stress run with host jitter (e.g. an artificial random delay in the worker) still IDENTICAL, Mac speed ABBA vs stage 2. Stop before any Odin run; the orchestrator schedules it.

## Rules
Fork worktree `~/dev/ssx3-work/MT1/PS2Recomp`, local branch `mt1` from fork `ssx3` tip; never push; runner-dir check empty; suite green. ≤ 12 builds, boots on bradflix (det) and the mini (speed, exclusive ≤ 5 min when quiet). Text only in git. First unexpected failure: save the error and hand back.

## Deliverable
`local/research/MT1/REPORT.md` (map, design, per-stage tables, determinism proofs, speed, fork commits, gaps) + `[MT1]` commits (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`), no push.
