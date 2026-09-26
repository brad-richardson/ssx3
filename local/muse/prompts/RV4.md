# RV4 — frontier perf review: the path to real time (and 120 Hz) on the Odin (GPT Astra, read-only, ≤ 1.5 h)

Brad (09-26) offered his remaining Codex quota for a second set of eyes on performance. You are a reviewer: read, reason, write one document. No builds, boots, device use or source edits (read-only `git`, `rg`, `lsp` on the forks are fine). Budget is tight: read the listed sections, not whole trees.

## Where we are (numbers are in `docs/numbers-ledger.md`)
- Odin race **0.244×** (68.3 ms/guest frame, need 16.7 for real time, ~8.3 for 120 Hz sim). N12 breakdown (`local/research/N12/REPORT.md` Table 2 + gate): VU1 46.7 ms (generated pairs 38.0, interpreter/other 6.2, issue/hazard 2.5), guest EE code 8.7, libc/kernel 10.8, VU0 ≈ 5.5 (still interpreted), GsWorker 7.2 ms CPU on another core, GPU 35–37 % busy.
- Since then (not yet on the Odin): VR2 stage 1 **1.095× on the Mac** (`local/research/VR2/REPORT.md`; per-pair levers, bit-exact; flag liveness held at +0.6 %). VR2 stage 4 (**block functions**: one host function per VU1 basic block, registers in locals, static stalls behind an entry guard) is being built now; its sketch and estimate (≈1.12–1.2× Mac) are in the same report.
- VK1 (`local/research/VK1/REPORT.md`): Odin 4×+hi-res costs 31 % = GameThread stall behind GPU work serialized in paraLLEl `flush()`/`vsync()`; hypothesis: `next_frame_context()` per flush with 4 frame contexts. Frame-context experiment running.
- Parked by Brad: **VU1 on its own thread** (N12 gate sizes it at ~1.4× now). Brad's rule: correctness before complexity.
- History/background as needed: Q1 microVU research (`local/research/Q1/REPORT.md`), VB1 profile (`local/research/VB1/REPORT.md` "VU1 profile share" + "What's left"), the last review `docs/research/review-2026-09-25-fable.md` (don't repeat it; say where you disagree).
- Code: `~/dev/PS2Recomp` fork branch `ssx3` (tip `173b31f`), VU1 core `ps2xRuntime/src/lib/*vu1*`, `ps2xRuntime/include/runtime/ps2_vu1.h`, generated VU1 images in `~/dev/ssx3-work/vu1gen-ssx3/` (derived from game data: read, never quote more than a few lines), EE codegen in `~/dev/ssx3-work/codegen-ssx3/` (same rule), paraLLEl `~/dev/ssx3-work/parallel-gs-ssx3`.

## Questions (evidence rows: file:line or report section for every claim)
1. **Rank the levers to real time on the Odin** with an ms-per-frame estimate, confidence and cost each: VU1 block functions; VU1 flag/scoreboard work beyond that; VU0 static recompile; the parked VU1 thread; guest EE code (8.7 ms: anything cheap, e.g. how the codegen handles memory access, branches, calls); libc/kernel 10.8 ms (what is it likely to be?); compiler/toolchain levers for the Android build (-O level, LTO/ThinLTO, PGO, `-mcpu` for the Odin's cores, NDK version, `-fno-plt`/Bsymbolic already done); big.LITTLE placement. Say what the ceiling looks like if everything lands.
2. **Challenge our estimates and designs:** is the stage-4 block-function design (VR2 report, "Stage 4 sketch") right, and what would you do differently to get more of the 48 % "loads" (state traffic) out? Is the ≈1.12–1.2× estimate too high or low? Is there a cheaper design that captures most of it?
3. **What are we measuring wrong or not at all?** (e.g., Mac speedups vs Odin speedups, thermal state, unpaced vs paced, profile attribution.) Name the one measurement that would most change the plan.
4. **120 Hz simulation:** given the above, is ~8.3 ms/guest frame on the Odin plausible at all, and what architecture would it take (be concrete about threads, VU1, GS)?
5. Anything else we are getting wrong about performance.

## Deliverable
`docs/research/review-2026-09-26-astra-perf.md` (≤ ~300 lines): an executive summary of ≤ 8 bullets, then one section per question with ranked recommendations tagged **do now / queue / park**, each with a one-paragraph brief sketch for "do now". Commit `[RV4] …` with the explicit path, trailer `Orchestrated-By: Codex`, no push. The orchestrator decides what to adopt.
