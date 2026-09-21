# MF2 — MetalFX interpolation as a smoothing-style app option: integration map + toggle prototype

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables +
hypothesis + next-action recommendation, no verdicts.** Read first:
`local/research/MF1/REPORT.md` (all — session-1 numbers, gaps G1–G10,
especially motion vectors) + the smoothing-option implementation end to end
(start: `tools/mobile_gamecube.py`, `tools/native_gamecube.py`,
`tools/gamecube_schedule_check.py`, `tools/mobile_pacing_check.py` — flag /
config / trial plumbing through to the runtime switch) + the G7/G8 adoption
context if relevant (`docs/research/review-2026-09-20-first-frame-and-gs.md`
§paraLLEl-GS). Goal per user: MetalFX frame interpolation as a NEW APP
OPTION, on/off like smoothing was done — on the GC recomp path, where perf
likely misses but the learnings pay. This brief maps the integration and
prototypes the toggle; full integration is MF3.

## Facts you start from

- MF1 proved the interpolator runs headless on all three targets
  (exact-motion interior bit-exact, 1.3–5.3 ms GPU + 16.67 ms structural
  latency) and named the blockers: GX motion-vector export (G1), no
  sustained pass, UI/HUD path choice (two MF1 paths measured).
- The smoothing option is the template: map it fully (user-facing flag →
  trial config → build/run plumbing → runtime switch → measurable effect)
  before designing MF's. Table each hop with file+line.
- Integration map must cover: GC recomp frame boundaries (where the
  interpolator inserts), motion-vector source OPTIONS (what exists today,
  what GX export needs, synthetic-motion fallback and what it can/can't
  prove), UI/HUD routing (which MF1 path and why), and a perf model for
  GC recomp on device (frame budget vs MF1's measured costs — show why it
  likely misses and what content/load change would flip that).
- Prototype scope: wire the option plumbing smoothing-style (flag → config
  → runtime switch) with the interpolator stage PRESENT but BYPASSED until
  motion exists. A synthetic-motion demo mode is allowed ONLY if it falls
  out of the bypass naturally (no new subsystems). No game-content moves,
  no toolchain changes, no trial-infra refactor.

## Gates and rules

- Prototype edits confined to NAMED files (table the diff; keep it small
  and reviewable). No PS2 boots → no lease. Builds `-j2` (subordinate to
  other lanes). Byte caps declared up front, tracked in ALLOCATED bytes;
  SSD only, nothing new on `/`.
- Verification: sim-first. A device install needs a fresh orchestrator
  prompt first (never `--force-install` on your own — the phones are the
  user's). If verification doesn't fit the box, table the exact verify
  recipe + what is/isn't proven instead of rushing a build.
- Evidence dir `local/research/MF2/` (STANDALONE). Commit with `git add -f`,
  prefix `[MF2]`, trailer `Orchestrated-By: Muse Code`. Do not push (the
  orchestrator pushes at poll when the tree is clean). Prototype diffs to
  tracked files ride in the SAME commit, separately listed in the report.
- Experiment contract up front (hypothesis/observable/alternatives/stop).
  Time box: 6 h. Tables + hypothesis + next-action recommendation.

## Task 1 — smoothing map + MF integration map

1. Smoothing end-to-end table (flag → config → plumbing → switch →
   effect), each hop file+line.
2. MF integration table: insertion point(s), motion options (existence +
   cost each), UI/HUD routing decision, perf model (budget vs MF1 costs +
   flip conditions). Gaps as OPEN rows with owners (MF3 vs G-lane).

## Task 2 — toggle prototype (+ conditional demo)

1. Wire the option smoothing-style with interpolator BYPASSED. Table the
   diff (files + lines + behavior with on/off).
2. Synthetic-motion demo ONLY if natural. Verify per the gates above (or
   table the recipe). Hypothesis verdict + the ONE next action (MF3 shape).

## Report

`local/research/MF2/REPORT.md`: contract, smoothing map, integration map,
perf model, prototype diff table, verification (or recipe), license notes
(if any third-party interface touched), exact commands, gaps. Commit
evidence (`[MF2]`, prototype diffs listed), stop.
