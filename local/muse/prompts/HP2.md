# HP2 — audit always-on diagnostic checks on the hot paths (local Qwen, read-only, 1.5 h)

## Goal
EN2 (`docs/research/gamecube-learnings.md` §7 item 1) and HP1 (`local/research/HP1/REPORT.md`) show that dev-only diagnostics can cost real time in release builds: HP1 found a trace that formatted strings for every VIF packet even with the trace off. Find every remaining **always-on** diagnostic check or formatting on the hot paths, so the orchestrator can decide which to guard or compile out. **Read-only: you change no code. Hand back the table; don't conclude.**

## Where to look (fork source, read-only): `~/dev/ssx3-work/SS3/PS2Recomp` (fork `ssx3` `f0d2d3c`)
Hot paths, in order: `ps2xRuntime/include/ps2_runtime_macros.h` (READ/WRITE macros used by every guest memory access), `ps2xRuntime/src/lib/ps2_runtime.cpp` (`Load*`/`Store*`, `dispatchGuestBranch`), `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` (`run`, `checkpointDue`, VBlank), `ps2xRuntime/src/lib/vu/ps2_vu1_step_impl.h` + `ps2_vu1_core.cpp` (`issuePair`, `run`, `commitReadyPipelines`, `progressXgkick`), `ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp`, `ps2xRuntime/src/lib/ps2_memory.cpp` (`processPendingTransfers`, DMA), `ps2xRuntime/src/lib/gs/gs_frontend.cpp` (`processGIFPacket`), `ps2xRuntime/include/ps2_mtvu.h`.

## What counts
Any code that runs on those paths in a **release build with every `PS2X_*` debug/trace env var unset** and exists only for diagnostics: calls to `std::getenv` per call (not cached), `snprintf`/`std::string`/`std::ostringstream` building, `ps2_e3*`/`e36`/`e37`/`e41`/`e43`/`e44`/`pk`/`E7`/`RR1`/`UV1`/tap/trace/census `enabled()` checks that are **not** cached in a local/static, `thread_local` reads, atomic loads of debug flags inside tight loops, counters incremented unconditionally, `static` function-local initializers with guards on every call. Use `lsp` (findReferences/incomingCalls) to confirm a function is on the hot path, and read the definition of each `enabled()`-style check to see whether it's a cheap cached flag or does more.

## Deliverable (write early with "not found" cells, refine)
`local/research/HP2/REPORT.md`: one table row per finding — file:line, the check/formatting, which hot function it's in (with the call chain you confirmed via lsp), what it costs per call (a static/relaxed-atomic load vs a getenv vs a string build), whether a compile-time switch already exists (`PS2X_ENABLE_DIAG_TAPS`, `PS2X_ENABLE_RUNTIME_LOGS`, `NDEBUG`), and a citation for every claim. A second short table: checks you looked at that are already cheap (so they aren't re-audited). No code edits. Commit `[HP2] …` with `git add -f local/research/HP2/REPORT.md`, trailer `Orchestrated-By: opencode`, no push.

## Rules
Read anything under `~/dev`; write only `local/research/HP2/REPORT.md` in this repo. If a tool call is denied, stop and report it. First failure: stop and hand back what you have.
