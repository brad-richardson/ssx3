# RV6 — what "true 120 Hz" means for SSX 3's simulation (GPT Astra, read-only research, ≤ 2.5 h)

Product goal (`AGENTS.md`): **true 120 Hz simulation** — about twice the stock update rate at normal wall-clock speed. Faster emulation, duplicated presents and interpolation are different outcomes. RV4 (`docs/research/review-2026-09-26-astra-perf.md` §4) flagged that nobody has worked out how SSX 3's simulation step relates to vsync. Do that analysis.

## Start from
- `local/research/X3/REPORT.md` + `ORCH-CORRECTIONS.md`, `local/research/X2/REPORT.md` + `ORCH-CORRECTIONS.md` (earlier map: counted step loop in `sub_00316F00`, `$s1` vs `lw 0x20($s0)`, back-edge `0x317190 → 0x317128`; the published patch-site increment at `0x317184` is the delay slot of `jal checkHalt`; metro sites clear the frame-skip flag `[*(gp+0x2A74)+0x34]`). Read the corrections first: they record where earlier readings were wrong.
- `docs/facts.md` (rider position `0x5409c0`, timing facts), `docs/reserve.md` + `docs/reserve/` (the GameCube route's 120 fps host-replay and determinism work; how it relates), memory-only notes are not available to you.
- Generated EE code `~/dev/ssx3-work/codegen-ssx3/` (derived from game data: read, quote at most a few lines) and the runtime's vsync/timer/INTC delivery in `~/dev/PS2Recomp` (branch `ssx3`, `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`). Use `rg`/`lsp`.

## Questions (evidence for every claim: guest address, file:line or report section)
1. How does the race loop advance game time: fixed step per vsync, variable dt from a timer, or a step count derived from elapsed vsyncs (catch-up)? Where are dt/step constants, and which timers (vsync count, EE timers, RCNT) feed them?
2. What does the game do at 60 Hz when it can't keep up (frame-skip flag, multiple steps per frame)? What would it do if vsync ran at 120 Hz: faster game, or finer steps?
3. What would a correct 120 Hz simulation need: which constants/code change (physics dt, animation rates, timers, audio/music sync, input sampling, race clock, AI), and what a minimal experiment on our runtime looks like (a bounded patch + the observables: race timer vs wall clock, distance per wall-second under fixed input, unique update count per second).
4. Risks: determinism, replays/ghosts, online/records (race times), audio pitch, anything tied to 60 Hz.

## Deliverable
`docs/research/review-2026-09-26-astra-120hz.md` (≤ ~400 lines): the timing model with evidence, a ranked plan with **do now / queue / park** tags and a one-paragraph brief sketch for the first experiment, and open questions stated plainly. Commit `[RV6] …` with the explicit path, trailer `Orchestrated-By: Codex`, no push. Read-only everywhere else.
