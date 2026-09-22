# Docs index

Grouped by the A3 audit classification (§1 of the A3 report). One line each.
"Current" means linked from a current doc or plan; historical entries are
evidence, not guidance.

## Current plans (follow these)

- `../AGENTS.md` — product direction, roles, brief contract, standing rules.
- `status.md` — the compact lane board.
- `todo.md` — open work per lane (short; history in `archive/todo-2026-09-22.md`).
- `research/review-2026-09-22-progress-and-parallelization.md` — latest review and track plan.
- `plan-gs-gpu-backend-2026-09-18.md` — GPU GS backend plan (partly stale: the G lane now uses paraLLEl-GS).
- `reserve.md` — parked GameCube/Dolphin work (not scheduled).
- `plan-120fps-2026-09-17.md`, `impl-plan-2026-09-15.md` — GameCube-route plans, in reserve.
- `asset-policy.md` — shipped-assets rule; supersedes the remaster rollout.

## Gate ledger (quote this, not the docs)

- `numbers-ledger.md` — the one table for every quoted metric with status.

## Current references (how things work now)

- `aloha-conversion.md` — Aloha Ice Jam conversion into the ASS1 slot.
- `course-selection.md` — boot-time course redirect via manifest.
- `route-control.md` — waypoint steering for the native ride harness.
- `gamecube-world.md` — GameCube SSX 3 world format (GXBE69).
- `gamecube-scenery.md` — GameCube scenery conversion.
- `gamecube-collision.md` — GameCube collision and reset behaviour.
- `gamecube-materials.md` — terrain material (lighting) conversion.
- `gamecube-rails.md` — GameCube donor rail conversion.
- `gamecube-feasibility.md` — GameCube route feasibility audit.
- `architecture-review.md` — September 12 architecture review.
- `garibaldi-visual-comparison.md` — September 12 before/after comparison.
- `texture-remaster.md` — texture remaster runbook (method; rollout archived per asset-policy).
- `share-recovery.md` — macOS share reconnect setup.
- `../native/research.md` — GXBE69 static research notebook (rev 0).

## Historical research (evidence, September 10–14 era)

- `investigation.md` — first Garibaldi→SSX 3 findings (PS2 era).
- `rebuild-experiment.md` — first bounded rebuild experiment.
- `full-course-experiment.md` — full Garibaldi replacement experiments.
- `archive/roadmap.md` — early course-patcher roadmap (archived 2026-09-18; superseded by `impl-plan-2026-09-15.md`).
- `odin-testing.md` — Garibaldi test steps on Odin 3.
- `locale-tables.md` — SSX 3 locale strings.
- `location-anatomy.md` — what a location holds besides terrain.
- `peaks-and-locations.md` — peaks, locations, level selector.
- `tricky-courses.md` — SSX Tricky course inventory.
- `research/120hz-analysis.md` — September 13 120 Hz investigation.
- `research/120hz-cpu-overhead-spikes.md` — CPU/diagnostic overhead spikes.
- `research/120hz-f-spike.md` — true-120 Hz simulation (route F) plan.
- `research/120hz-host-replay.md` — host-side frame replay.
- `research/120hz-independent-schedule.md` — independent render scheduling.
- `research/120hz-native-interpolation.md` — native pose interpolation prototype.
- `research/120hz-native-path.md` — native rendering investigation.
- `research/120hz-output-resolution.md` — output size and callback CPU timing.
- `research/120hz-pacing-acceptance.md` — phone pacing acceptance.
- `research/120hz-render-seam.md` — repeated rendering and camera experiment.
- `research/120hz-reprojection.md` — 120 Hz reprojection, first batch.
- `research/120hz-review-followup.md` — review follow-up: load protection.
- `research/float-arithmetic-audit.md` — FP arithmetic classifier spike.
- `research/float-conversion-spike.md` — generated FP conversion spike.
- `research/loading-speed-spike.md` — isolated DVD loading-speed experiment.
- `research/normal-frame-cpu-spike.md` — ordinary-frame CPU attribution.
- `research/performance-batch2-followup.md` — fast-FP batch follow-up.
- `research/performance-review-2026-09-13.md` — September 13 performance review.
- `research/review-2026-09-16-architecture.md` — Sept 15–16 change review.
- `research/review-2026-09-17-architecture.md` — Sept 16–17 change review.
- `research/review-2026-09-17-recomp-perf.md` — recomp architecture/perf dive.
- `research/startup-shortcut.md` — fast cold start to the main menu.

## Handoffs and snapshots

- `archive/ssx3-120hz-handoff-2026-09-13.md` — September 13 handoff (archived 2026-09-18; superseded by `plan-120fps-2026-09-17.md`).
- `../local/research/A2/REPORT.md`, `G0/REPORT.md`, `P1/REPORT.md`, `S2/REPORT.md`, `S2b/REPORT.md` — recent gate/audit reports (force-added under ignored `local/`).
- `research/ps2recomp-spike-2026-09-12/README.md` — recovered spike transcript index.
- `research/ps2recomp-spike-2026-09-12/commands-and-outputs.md` — every spike command with output.
