# EN2 — GameCube learnings inventory (everything except 120 Hz), mapped to the PS2 route (muse, 3 h, docs only)

## Goal
Brad (09-26): the parked GameCube/Dolphin route (`docs/reserve.md`) did a lot of work — performance (Dolphin/ModernGekko core and game-logic optimizations, host HLE hooks, idle handling, loading, float conversion), engine and data knowledge (courses, worlds, collision, rails, materials, textures, locale/event tables, disc rebuilds), and tooling. EN1 already covered timing/120 Hz (`docs/research/ssx3-engine-timing.md`; don't repeat it). Write **one current-state inventory** so the PS2 route doesn't rediscover any of it: what was learned, what worked, what didn't, what it cost, and **whether and how it applies to the PS2 static-recompilation runtime** (EE/VU/GS/SPU2 by recompile/HLE on the Odin, iPhone and Mac).

## Sources (skim broadly, read the performance ones closely; cite file + section for every claim)
- Performance (read closely): `docs/research/performance-review-2026-09-13.md`, `performance-batch2-followup.md`, `normal-frame-cpu-spike.md`, `loading-speed-spike.md`, `float-arithmetic-audit.md`, `float-conversion-spike.md`, `startup-shortcut.md`, `review-2026-09-17-recomp-perf.md`, `review-2026-09-16/17-architecture.md`, `docs/reserve/architecture-review.md`, `docs/reserve/odin-testing.md`, `docs/reserve/gamecube-feasibility.md`.
- Engine/data: `docs/reserve/*.md` (world, scenery, collision, rails, materials, textures/remaster, locale tables, location anatomy, peaks/locations, course selection, tricky courses, route control, rebuild experiment, aloha conversion, asset policy), `docs/facts.md` (GC-derived rows), the `tools/` directory (list what each tool does in one line; group them).
- PS2 context for the "applies?" column: `AGENTS.md`, `docs/status.md`, `docs/numbers-ledger.md`, `docs/research/review-2026-09-26-astra-perf.md` (RV4), `review-2026-09-26-astra-emulators.md` (RV7), `local/research/CP1/REPORT.md` (current Odin critical path).

## Deliverable: `docs/research/gamecube-learnings.md` (≤ ~450 lines)
1. **Summary** (≤ 10 bullets): the most reusable lessons for the PS2 route.
2. **Performance inventory table**: optimization / what it did / measured effect (with the number and its conditions) / cost & risk / **PS2 transfer**: *applies directly*, *applies as a technique*, *already done on PS2 (name the lane)*, *not applicable (why)*, or *unknown*. Include things that failed or regressed (e.g. idle skipping, host_call hooks) and why.
3. **Game-logic / engine knowledge inventory**: structures, tables, formats, behaviours learned from the GC build (addresses are GC-specific: say whether the PS2 equivalent is known, and where), grouped by subsystem.
4. **Data/asset knowledge** (courses, worlds, textures, collision, locale/event tables, disc formats): what's platform-neutral (file formats, content) vs GC-only.
5. **Tooling inventory**: `tools/` and the harness pieces, one line each, and which could be reused or adapted for the PS2 route.
6. **Measurement and process lessons** (determinism, movie record/replay, harness pitfalls, device testing) — keep only what's still relevant.
7. **Candidate PS2 work items** that fall out of this (ranked, each one line with its source), for the orchestrator to consider — don't create briefs.

## Rules
Write only that file. Don't edit other docs; the orchestrator links it. No game data or generated code quoted beyond a few addresses/names. Commit `[EN2] …` with the explicit path, trailer `Orchestrated-By: Muse Code`, no push.
