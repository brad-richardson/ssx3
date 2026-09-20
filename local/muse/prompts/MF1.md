# MF1 — MetalFX frame-interpolation spike, session 1: integrate + first quality/cost/latency numbers (GameCube track)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `docs/research/120hz-reprojection.md` first (all
of it — the failed color-only block matcher (10.4 ms GPU +
4.9 FPS, do NOT repeat it), the offline warp precedent
(footprint splat, HUD alpha solved), and the key line:
MetalFX frame interpolation was NEVER built), plus
`docs/plan-120fps-2026-09-17.md` (the layering: 60 Hz guest
sim + perf fixes produce real frames; interpolation sits in
PRESENTATION between consecutive real frames — the sim never
runs faster) and `docs/research/120hz-pacing-acceptance.md`
(the bars: 16.67 ms aggregate budget, 8.33 ms presentation
deadlines). User authorized 09-20; user is curious about
MetalFX QUALITY first, understands the latency cost. This is
session 1 of an estimated 2–4 session spike.

## Facts you start from

- The layering (fixed): 60 Hz guest sim (GameCube recomp
  core) + landed perf fixes (dual-core default, fast-FP,
  chunk LUT, determinism gate) render REAL frames;
  `MTLFXFrameInterpolator` synthesizes the in-between frame
  from consecutive real frames (color + depth + motion,
  UI separated for the HUD — the alpha/HUD constraints in
  120hz-reprojection.md apply); presentation runs 120 Hz.
- The device: iPhone 16 Pro Max (A18 Pro — MetalFX frame
  interpolation qualified). Reachability TBD at brief time:
  in the FIRST hour, table device reachability (USB/wifi,
  pairing, trial-harness install — reuse the phone-trial
  infra that produced builds `1747c62a` etc.); if the
  iPhone is unreachable, continue on the Mac (Apple
  Silicon Metal) + iPad (wifi, confirmed 09-20) and table
  the iPhone run as queued-for-user with the exact
  command/build to run. Do NOT stall on the device.
- The inputs: matched color+depth capture path exists (the
  reprojection batch `tools/gamecube_reprojection.py` +
  `local/research/120hz/` — reuse, do not rebuild);
  MOTION vectors are the open input (table what the GX
  path emits vs what MetalFX wants — gap, not blocker:
  session 1 may use estimated/uniform motion where the API
  demands it, tabled exactly).
- Baselines to beat/table (or table why not comparable):
  block matcher 10.4 ms GPU (failed); the 1–2 ms warp hope
  (unmeasured); extra-draw bursts ~117 displays/s (8–16 s
  windows, no sustained pass); static-wall MAE precedent.
- NO lease of any kind (GameCube track — no PS2 boots).
  No fork changes (PS2Recomp untouched). Isolated harness
  only (never edit vendor sources, the production player,
  or phone settings — reprojection-batch discipline).

## Gates and rules

- Evidence dir `local/research/MF1/` (STANDALONE) + the
  spike harness (new files under `local/` or `tools/`,
  ignored-build discipline per the reprojection precedent
  — table paths). Commit with `git add -f`, prefix `[MF1]`,
  trailer `Orchestrated-By: Muse Code`. Do not push (the
  orchestrator pushes at poll when clean).
- `export COPYFILE_DISABLE=1` on every step touching the SSD.
- Time box: 6 h. Tables + receipts, no verdicts.
- Hygiene: write the report in chunks with a tail receipt
  (truncated tail fails the gate).

## Task 1 — integrate (does MetalFX run in the harness?)

1. Input table: color/depth/motion/UI availability per
   source (capture path vs MetalFX descriptor needs —
   match/gap per input, with the motion fallback tabled).
2. Integration table: harness shape (files added, player
   untouched proof), MetalFX version/entry used, first
   successful interpolated frame (where? what res?).
3. Device table: iPhone reachability receipt (or Mac+iPad
   fallback with the queued iPhone command recorded).

## Task 2 — first numbers (quality? cost? latency?)

1. Quality table: interpolated vs real-next-frame diffs
   (static-wall MAE vs precedent; HUD/alpha regions
   separated; motion-boundary notes — quality FIRST per
   the user).
2. Cost table: GPU ms per interpolated frame (vs 10.4 ms
   matcher + 1–2 ms hope), CPU overhead, memory delta.
3. Latency table: end-to-end added latency (later-frame
   wait + warp + composite vs the 16.67/8.33 budgets —
   measured where possible, bounded where not).

## Report

`local/research/MF1/REPORT.md`: integration + first-numbers
tables, exact commands/builds, gaps (session-2 needs:
sustained pass? motion vectors? device runs?). Commit
evidence (`[MF1]`), stop.
