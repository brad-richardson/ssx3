# TM2 — who writes the rider position and the race clock? (muse, 2 h, observation only)

## Goal
TM1 (`local/research/TM1/REPORT.md`, read the Outcome, "Rider position" and "HUD race clock" sections) confirmed SSX 3's 60 Hz update chain live, but found that the rider triple at `0x5409c0` is **bit-identical before and after all 601 app updates** (`0x2306b8`) although it moves every VBlank, and that the HUD race clock is not a stored word TM1 could find. For any 120 Hz simulation work we need the real integrator. Find the code (or DMA) that writes `0x5409c0..0x5409cb` during a race, when in the VBlank it runs relative to the app update and render, and what drives the HUD clock. Observation only.

## Facts
- The runtime has a write watchpoint: `PS2X_DIAG_WATCH=<addr,...>` (`ps2xRuntime/src/lib/ps2_runtime.cpp:1836+`), compiled in only with `PS2X_ENABLE_DIAG_TAPS=ON`. Check whether it sees (a) EE stores through the FAST RAM path, (b) DMA writes into RDRAM (e.g. SPR→RDRAM `fromSPR`, IPU), (c) 128-bit stores (`SQ`, `SQC2`). If a path isn't covered, add minimal default-off coverage for it (one commit, same knob) and say so.
- DIAG-taps builds are slow on bradflix (`local/research/HS1/REPORT.md` §1: one TU takes ~25 min with taps on); build on the **mini** with `local/tooling/build/mac_build.sh` plus `-DPS2X_ENABLE_DIAG_TAPS=ON` (add a `--diag` flag to the script if it's a one-liner; otherwise pass the CMake arg in your own configure and report it). Det runs are fine on the Mac (one mini slot each).
- TM1's tap (`ps2_tm1_tap.h` on fork branch `tm1`, bundle ref on bradflix) gives the per-VBlank chain order; reuse it for the "when" (cherry-pick onto your branch if needed).
- Guest code: `~/dev/ssx3-work/codegen-ssx3/` (read-only; derived from game data, never committed). HUD clock hypothesis from TM1: derived at render time from the update counter `A+0x1c`.

## Steps
1. Branch `tm2` from fork `ssx3` tip in `~/dev/ssx3-work/TM2/PS2Recomp`; diag build (≤ 2 builds).
2. Race boots FR1-R1 to t2400 with the watch armed on `0x5409c0`, `0x5409c4`, `0x5409c8` for ticks 1800–1900 (bounded log): for each write — guest PC (and owning `sub_`), the write path (EE store / DMA channel / other), value, tick, and its position relative to TM1's chain events (producer, consume, app update, render). Then follow one level up: which function calls the writer and on which thread (EE thread id).
3. HUD clock: find the render-time code that formats the clock digits (search the render call `0x22b008`'s callees for a divide by 60 / the digit glyph path, or watch the string buffer if one exists) and name its input.
4. Confirm the guest is unperturbed (det-hash vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` with the watch compiled in but unset).

## Rules
Never push; runner-dir check empty. ≤ 2 builds, ≤ 4 boots (one mini slot each). Bounded logs. Text only in git. Workers don't edit `docs/`. First failure: stop, save the error, hand back.

## Deliverable
`local/research/TM2/REPORT.md` (writer table, call chain, timing within the VBlank, HUD-clock source, commands, SHAs, gaps) + `[TM2]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
