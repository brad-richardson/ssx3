# VR1 — VU1 microprogram static recompilation, stage A (Opus exploratory, 3 h, Mac only)

Worker: Claude Code (Opus), exploratory, Brad-approved class (explorer + notebook). You choose the experiments inside the rules. Read `~/dev/AGENTS.md` (exploratory freedom overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, `docs/orchestration.md` §3, then `local/research/{E57,NP1,N11,E53}/REPORT.md` and `docs/research/review-2026-09-25-fable.md` §3 (ranks 3–4).

## Goal
On the Odin the race frame is 121 ms and **VU1 execute is 62.8 ms of it, hazard bookkeeping 25.7 ms** (NP1 Part 1). E57 already took the interpreter's easy wins. Build stage A of E57's static-recompile sketch (`local/research/E57/REPORT.md` "Static recompilation…", steps 1, 2 and 4): SSX 3's VU1 programs become generated C++ with decode, usage lookups and opcode switches removed, the **scoreboard and cycle accounting unchanged**, keyed by a hash of VU1 code memory, with interpreter fallback for unknown code. Land it bit-exact with a Mac speed measurement; the Odin pair comes after the gate.

## Facts
- Fork `~/dev/PS2Recomp` `ssx3` **`0ed07c4`**; VU1 in `ps2xRuntime/src/lib/vu/ps2_vu1_{core,upper,lower}.cpp`, `ps2_vu1_detail.h`, `include/runtime/ps2_vu1.h`; tests `ps2xTest/src/ps2_vu1_tests.cpp`. 7 programs, 7,305 instructions (E53); max single program 27,360 cycles (CT1); `resume()`/MSCNT and the 65,536-cycle budget must re-enter at any pair PC.
- Oracle: E57's `local/research/E57/check.py` (suite + 2,400 `[det-hash:v1]` lines + GS stream digest vs baseline). **Bit-exact is the only acceptance.** Mac env: paraLLEl (`PS2X_GS_BACKEND=parallel`, `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`, `PGS_HIER_BINNING=force`), `PS2X_SOUND=1` optional (AU10 fixed sound-off), I26-FAST, empty mc0, deterministic. Canonical codegen `~/dev/ssx3-work/codegen-ssx3` (SBR predicates).
- Generated VU1 code is derived from game data: it lives **outside the repo** (like `PS2X_GAME_CODEGEN_DIR`), never committed; the generator and runtime hooks are fork code.
- NP1 Part 2 (running, Odin + bytesize) touches VU1 execute's per-call memset on branch `np1-link`; coordinate by keeping your changes on your own branch and noting any overlap in the report.

## Rules
- Worktree `~/dev/ssx3-work/VR1/PS2Recomp`, local branch `vr1-vu1-recomp` from `0ed07c4`; scratch `~/dev/ssx3-work/VR1/` ≤ 20 GB. Never push; never `git add -f` in the fork; runner-dir check empty on every commit. Mac only (no Odin, no bytesize, no devices).
- Boots: one mini slot each (`p_lane_lease.py`); speed pairs `--exclusive` (≤ 5 min per hold, ABBA). Text only in git.
- Time box 3 h from your first command; notebook committed every ~30 min; write up in the last 15 min.

## Deliverables (commit `[VR1] …`, explicit paths, trailer `Orchestrated-By: Claude Code`, no push)
`local/research/VR1/NOTEBOOK.md` (append-only) and `REPORT.md`: design (keying, entry points, fallback), fork commits + `--stat`, suite, `check.py` result (BIT-EXACT or first differing tick), Mac race speed base vs VR1 (ABBA, exclusive), VU1 share before/after (diagnostic profile), coverage (share of VU1 cycles run in generated code), what stage B would add, gaps. Recommend whether it's ready for an Odin pair; the orchestrator decides.
