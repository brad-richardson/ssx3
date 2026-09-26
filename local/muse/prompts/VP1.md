# VP1 — Can VU1 work run on several cores? Batch-independence census (Opus spike, design-only, 4 h)

## Goal
Brad (09-26) approved scoping multi-core VU1. The Odin race is gated by the MTVU unit thread (~32 ms/frame of work,
~94 % busy; FS2 Part 3), while other cores idle (GameThread ~40 %, GsWorker ~30 %). Idea: run consecutive VU1
microprogram runs ("jobs") on 2–3 workers and commit their GIF/GS output **in the original order**, so the GS stream
and the det-hash stay identical. This spike measures whether the work is independent enough, and designs it. **No
product code; the orchestrator and Brad decide on a build.**

## Facts
- MTVU (MT1, `local/research/MT1/REPORT.md`, `ps2xRuntime/include/ps2_mtvu.h`): unit thread runs VIF1 unpack + VU1 +
  GIF; ~16.6k jobs per 2400 ticks (`census-summary.txt`); LAG lets the EE run a frame ahead.
- CP1 Table 3 (`local/research/CP1/REPORT.md`): unit on-cpu is mostly generated VU1 blocks (`VU1RecompImage<…>::B2a10`,
  `B0628`, `B0a58`), then `commitReadyPipelines`, `processVIF1DataImpl`, `progressXgkick`.
- 7 VU1 images (`~/dev/ssx3-work/vu1gen-ssx3`), static recompile + blocks (VR2), SIMD FMAC (VR4).
- VU1 state that persists across runs: VF/VI/ACC/Q/P/flags, VU1 data memory (double buffers via TOPS/ITOP/BASE/OFFSET),
  micro memory; VIF1 registers (ROW/COL/MASK/CYCLE), GIF PATH arbitration (PATH1 XGKICK vs PATH2/3).

## Questions (answer each with numbers from a Mac race trace, I26-FAST, t1714→t3000)
1. Per job: program (image + entry), start/end, VU mem read/write ranges, registers **read before written** (live-in)
   and **written** (live-out), XGKICK count/bytes, and whether its inputs came only from this job's VIF1 upload.
2. Dependency classes: what fraction of jobs (and of unit time) depend on the previous job only through
   (a) nothing, (b) constants uploaded earlier and never rewritten, (c) registers/memory the previous job wrote.
   Per program. Which live-ins are "almost constant" (a guard + speculation could cover them)?
3. Other ordering constraints: VIF1 stalls/FLUSH/MARK, EE reads of VU1 memory or registers (the MTVU violation
   census hooks), PATH3 interleaving, interrupts.
4. Model: with 2 and 3 workers and in-order commit, estimated unit-thread time per frame (use job durations from the
   trace, dependency chains, a per-job hand-off cost you measure or bound). Compare with today's 32 ms.
5. Design sketch: static proof per program vs run-time speculation + validation (and rollback cost), where the
   commit/ordering point lives, what must stay serial, how the det-hash proves it, and how PCSX2 relates (it runs
   VU1 on one thread; say so if this goes beyond PCSX2 — it's still deterministic, but name it).

## Rules / budgets
Instrumentation only on a **local branch** of a fresh fork worktree off `ssx3` (`vp1`), diagnostic, default off, never
pushed. Mac boots under `local/tooling/p_lane_lease.py` (or bradflix via `ssx3_boot.py --host bradflix`) — ≤ 6 boots,
≤ 600 s each. No Odin, no device installs. Scratch `~/dev/ssx3-work/VP1/` ≤ 10 GB (compress traces). 4 h.
Read-only fan-out subagents are fine; edits/boots stay in your pane.

## Deliverable
`local/research/VP1/REPORT.md`: the census tables, the dependency classes per program, the 2/3-worker model with its
assumptions, the design sketch with risks, exact commands, and a go/no-go recommendation with the smallest first
implementation step. Small text receipts (compressed) only. Commit `[VP1] …` with `git add -f`, trailer
`Orchestrated-By: Claude Code`, no push.
