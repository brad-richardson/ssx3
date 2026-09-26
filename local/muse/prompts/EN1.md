# EN1 — one SSX 3 engine-timing reference: GameCube + PS2 findings, mapped (muse, 2.5 h, docs only)

## Goal
Brad (09-26): the GameCube 120 Hz attempt (parked reserve route) learned a lot about SSX 3's engine and simulation; the PS2 work (RV6, TM1–TM4) is rediscovering the same structure (app manager `checkHalt` loop, timer accumulator, a 30-entry buffered input ring). Write **one current-state reference** so nobody rediscovers either: what the engine does per frame, where each piece lives on **both** platforms, what was proven, what failed, and what's still open. Docs only; no builds, boots or code.

## Sources (read; cite section for every claim)
- GameCube: `docs/research/120hz-analysis.md` (esp. "Resolved callback boundaries"), `120hz-native-path.md`, `120hz-independent-schedule.md`, `120hz-host-replay.md`, `120hz-render-seam.md`, `120hz-native-interpolation.md`, `120hz-reprojection.md`, `120hz-f-spike.md`, `120hz-pacing-acceptance.md`, `120hz-cpu-overhead-spikes.md`, `120hz-review-followup.md`, `docs/reserve/plan-120fps-2026-09-17.md`, `docs/reserve/architecture-review.md`, and the determinism/timing bullets of `docs/reserve.md`. Skim the rest of `docs/reserve/` only for engine facts (world/collision/rails are course data, mostly out of scope).
- PS2: `docs/research/review-2026-09-26-astra-120hz.md` (RV6), `local/research/TM1/REPORT.md`, `TM2`, `TM3`, `TM4` (all parts + orchestrator gates), `docs/research/review-2026-09-26-astra-emulators.md` §4 (community patches), `docs/facts.md` (timing rows).

## Deliverable: `docs/research/ssx3-engine-timing.md` (≤ ~400 lines)
1. **The frame, end to end** (engine-level, platform-neutral): timer/VBlank → producer/accumulator → ring → consumer → app update(s) → integrators → snapshot → render gate → present; catch-up rules; what a "tick", an "update", a "render" and a "present" are.
2. **Address map table:** each engine piece (manager object and fields — rate, dt, multiplier, accumulator, catch-up bound, render mode; producer/consumer/ring; app-update slot; rider integrators and their private 1/60 constants; countdown time base; snapshot copy; HUD clock input; frame-skip gate) → **GameCube address / PS2 address / confidence (proven live, static only, inferred) / source**. Leave a cell "not found" rather than guess; mark every GC↔PS2 correspondence as *structural match* or *verified same role*.
3. **What each experiment proved or ruled out**, both platforms (e.g. GC host replay / interpolation / independent schedule outcomes; PS2 rate-120 probe, half-step constants, countdown phase breakage; community patch semantics).
4. **Open questions for true 120 Hz** in dependency order (merge TM4's Part 3 leads with any GC findings that already answer them — say explicitly if GC already solved something the PS2 lane is about to redo).
5. A short "how to measure" section pointing at the existing tools (TM1 tap, `PS2X_DIAG_WATCH` + `_TICKS`, the GC present-trace tooling) instead of repeating recipes.

## Rules
Write only that file. Don't edit other docs (the orchestrator links it). No game data or generated code quoted beyond a few addresses/instruction mnemonics. Commit `[EN1] …` with the explicit path, trailer `Orchestrated-By: Muse Code`, no push.
