# VR2 — VU1 recompile stage C: cut per-pair overhead, flag liveness, block functions (Opus, ≤ 8 h, staged)

## Goal
VU1 is still the Odin race's biggest cost (N11: 118 of 145 ms before VR1/VB1; N12 is re-measuring on F5, race now ~68 ms/frame at 0.244×). Inside the generated pair functions (VB1, Mac `xctrace`): loads 48 %, integer ALU 19 %, FP double 12 %, stores 10 %: **state traffic and per-pair control, not the math**. Brad (09-25) approved the next VU1 step. Make generated VU1 code cheaper while staying **bit-exact** (det-hash and the VU1 differential test).

## Facts
- VR1 (`local/research/VR1/REPORT.md`): pair-per-function images chained with musttail (`PS2X_VU1_MUSTTAIL`, required on every handoff: F4 crash). VB1 (`local/research/VB1/REPORT.md`): commit-at-issue; `## What's left` lists measured levers: (1) generated pairs skip the dev-only `m_traceArmed`/`m_entryArmed` checks (armed runs go to the interpreter), (2) hoist per-pair `next()` checks (budget, pc bound, stop) to block granularity when a block's worst-case cycles fit the budget, (3) keep `m_flagValidMask`/`m_directPendingUntil` updates off the common path. (NP1 already removed the 64 KiB XGKICK clear.)
- Q1 (`local/research/Q1/REPORT.md`): PCSX2 microVU computes stalls statically per block (ready-counter table carried block to block, normalized at block end), and decides per instruction which flag instances must be written (`microFlagInst.doFlag`, `mVUsetFlags`, tail window of ~4 instructions for the next block's readers, FSSET dedup). Our pairs compute MAC/status/clip flags on every FMAC even when nothing reads them.
- Exactness tools: `ps2_vu1_tests.cpp` differential test (VB1: random programs, direct vs queued commit; extend it to generated vs interpreter), det-hash gate (`local/tooling/boot/baseline.py compare` vs key `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`), `PS2X_VU1_STATS` (100 % generated in F5). Small-stack test (`PS2X_GAME_THREAD_STACK_KB=512`) for anything touching the chain.
- Build/boot: `local/tooling/build/mac_build.sh` (ccache), `local/tooling/boot/ssx3_boot.py`; VU1 images regenerated with `PS2X_VU1_RECOMP_DUMP` (F5 `## VU1 images`) into your own dir, never into `vu1gen-ssx3`. Speed: exclusive lease ≤ 5 min per hold, ABBA vs the F5 clean runner, race vsyncs/s ÷ 59.94.
- Fork `ssx3` `a3efbfe`; worktree `~/dev/ssx3-work/VR2/PS2Recomp`, local branch `vr2`; never push. Generated code never in git.

## Stages (each: suite green, differential test green, det-hash IDENTICAL, small-stack pass, then an ABBA speed pair)
1. **Quick levers** (1)–(3) above, one commit each, measured separately.
2. **Flag liveness:** static per-block analysis in the emitter so an FMAC skips MAC/status/clip computation when no reader can observe that instance before it's overwritten (conservative at block exits and at XGKICK/E-bit/branches, per Q1's tail rule). Extend the differential test to programs that read flags at every distance 0–5.
3. **Stop and hand back** with the table. Stage 4 (block-level functions: one host function per basic block, VF/VI kept in locals, stalls resolved statically as microVU does) is decided by the orchestrator from stages 1–2 and N12, as a Part 2.

## Rules
≤ 10 Mac builds, ≤ 20 boots (one slot each) + ≤ 4 exclusive speed holds (≤ 5 min each; SS1/VK1/HS1 share the mini — claim properly). No Odin (the orchestrator schedules an Odin check after the gate). Runner-dir check empty; never `git add -f` in the fork. Scratch `~/dev/ssx3-work/VR2/` ≤ 15 GB. Text only in git; workers don't edit `docs/`. A candidate that isn't bit-exact is dropped, not tuned. First unexpected failure: save the error and hand back.

## Deliverable
`local/research/VR2/REPORT.md` (per-commit table: exactness gates + ABBA race rate + VU1 share from a profile, flag-liveness stats: share of flag computations skipped, stage-4 sketch with an estimate, exact commands, SHAs, gaps) + an `[VR2]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`); fork commits stay local. Hand back the tables; the orchestrator decides.
