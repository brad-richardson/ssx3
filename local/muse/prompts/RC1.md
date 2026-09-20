# RC1 — Route-comparison criteria doc: GameCube numbers now, PS2 column blank (docs brief)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read Part 1 §7 rec 10 first (in
`docs/research/review-2026-09-19-progress.md` lines ~247–252:
write the route-comparison criteria NOW — host replay vs PS2
recomp for 120 Hz — against measured numbers; decide nothing),
plus Part 4 decision 4 (this brief: it does NOT need the PS2
first frame). This ends the M lane's microscopy era: the
pane now produces the decision framework the 48 briefs never
answered a question from.

## Facts you start from

- The comparison point (rec 10, fixed): "host replay shows
  an interpolated frame on the Odin" vs "PS2 shows a first
  frame with a real GS census." Neither has happened — the
  doc holds criteria + GameCube-side measured numbers +
  blank PS2 column, not a decision.
- The three criterion families (rec 10, fixed): (a) Odin
  frame-time budget, (b) visual correctness receipt, (c)
  remaining-work estimate. Each criterion needs: what is
  measured, how (tool/command/trial), the pass bar, and
  the GameCube measured value with its evidence pointer.
- GameCube-side sources (read-only): `docs/plan-120fps-
  2026-09-17.md`, `docs/research/120hz-*.md` (extra-draw
  timings, bursts, resolution, CPU spikes, pacing
  acceptance, reprojection), `docs/odin-testing.md`,
  `docs/numbers-ledger.md` (GameCube rows), `docs/todo.md`
  (120 Hz backlog items — each open item is a remaining-
  work row).
- PS2-side sources: `docs/numbers-ledger.md` (PS2 rows) for
  what exists (synth==blend 2.34%, M15 milestone); the PS2
  column stays BLANK where no first frame exists (do not
  project numbers — blank with the receipt that would fill
  it).
- NO lease of any kind (docs brief — no boots, no builds
  needed, no harness runs). No fork changes. No `adb`.

## Gates and rules

- Deliverable: `docs/route-criteria.md` (project doc, the
  criteria + GameCube numbers + blank PS2 column) AND
  evidence dir `local/research/RC1/` (STANDALONE: how each
  number was sourced — file + line + command where
  re-derivable). Commit both with `git add -f`, prefix
  `[RC1]`, trailer `Orchestrated-By: Muse Code`. Do not
  push (the orchestrator pushes at poll when clean).
- Time box: 4 h. Tables, no verdicts (no route recommendation
  — the doc explicitly defers the decision to the comparison
  point).
- Hygiene: write in chunks with a tail receipt (truncated
  tail fails the gate); every number carries its evidence
  pointer (no unsourced cells except explicit BLANKs).

## Task 1 — criterion tables (what decides, how measured?)

1. Budget table: Odin frame-time budget criteria (per-frame
   ms bars at 1×/2×/Match, trial shape, thermal guard —
   each with GameCube measured value + pointer, PS2 BLANK
   + the receipt that fills it).
2. Correctness table: visual-correctness receipt criteria
   (interpolated-motion distinctness, static-wall MAE,
   HUD/alpha exactness, artifact bars — same columns).
3. Work table: remaining-work estimate criteria (open items
   per route with size class — GameCube from the todo
   backlog; PS2 from the live queue to first frame).

## Task 2 — doc + sourcing (is every cell traceable?)

1. Source table: every GameCube number → file + line/section
   (+ command if re-derivable in <5 min — spot-verify 3).
2. Blank table: every PS2 BLANK → the exact receipt that
   fills it (which future brief/report row).
3. Decision-point table: the comparison-point definition
   (rec 10's two quotes) + what happens at it (mechanics,
   not outcome).

## Report

`docs/route-criteria.md` (the doc) + `local/research/RC1/
REPORT.md` (sourcing + gaps: what OD1/PS2-first-frame must
supply). Commit both (`[RC1]`), stop.
