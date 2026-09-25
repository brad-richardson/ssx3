# RV3 — frontier review to steer the next phase (Fable, 2 h, read-only)

Brad approved (09-24) a Fable review while he's offline. You are a reviewer, not a worker: read, reason, write one document. No builds, boots, device use or source edits (read-only `git`, `rg` and `lsp` on the forks are fine).

## Read first
Repo `AGENTS.md`, `docs/status.md`, `docs/todo.md`, `docs/facts.md`, `docs/numbers-ledger.md`, `docs/orchestration.md`, the last two reviews (`docs/research/review-2026-09-23-frontier-2.md`, `review-2026-09-24-time-and-bottlenecks.md`), then today's reports with their orchestrator gates: `local/research/{RR1,AU9,E57,GB8,N11,E61,AU8,TL1,I31,I32,E54E}/REPORT.md`. Fork code: `~/dev/PS2Recomp` (branch `ssx3`, plus local branches `rr1-sky`, `au9-spu`, `e57-vu1`, `n11-prof`), `~/dev/parallel-gs`.

## Questions (answer each with evidence rows: file:line or report section)
1. **Bug classes, not bugs.** Today's four root causes (planar tag-1 audio, PATH3 masked-FIFO release, V4-5 unpack, 4096-tag DMA cap, 32-bit sign branches) were all "our HLE/runtime differs from hardware semantics in a way the suite didn't cover". Which other places in the fork are likely to hide the same classes? Rank the top 10 suspects by expected player-visible impact, each with the observable a bounded brief would use.
2. **The sign-extension hunt.** E54E's global BLTZ/BGTZ fix went black; AU9 scoped it to one override. Propose the fastest way to find the runtime/HLE paths that leave non-sign-extended upper GPR bits (e.g. a debug assert on every 32-bit op result, a checker over the generated code, syscall/HLE return paths). Design the brief.
3. **Speed plan to real time on the Odin.** Odin race = 145 ms/frame, VU1 118 ms (N11), before E57's 1.35× Mac gain. Rank: VU1 microprogram static recompilation (7 programs, 7,305 instr), a cheaper hazard model, the parked VU1 thread (Brad wants it parked), menu-side Turnip driver CPU/allocator churn (N11 S3), PLT/libc (33 ms). Give rough ms estimates and risk; say what to measure first.
4. **Mac ↔ Odin alignment** (GB9 in todo): what must stay Odin-only, what can move to the Mac, and which knobs are worth adding.
5. **Process:** what in the orchestration loop cost the most time today (e.g. the overnight stall where the watcher wasn't restarted and nothing was gated for ~7 h; lease contention from exclusive speed sessions) and what to change.
6. **Anything we're getting wrong** that isn't asked above.

## Deliverable
`docs/research/review-2026-09-25-fable.md` (≤ ~400 lines): an executive summary of ≤ 10 bullets, then one section per question with ranked recommendations, each tagged **do now / queue / park** and with a one-paragraph brief sketch for the "do now" items. Commit `[RV3] …` (explicit path, trailer `Orchestrated-By: Claude Code`), no push. The orchestrator decides what to adopt.
