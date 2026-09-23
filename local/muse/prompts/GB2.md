# GB2 — GS bridge step (a): the CPU GS backend on its own thread behind a queue (Mac)

You are muse in a herdr panel in the ssx3 repo (`~/dev/ssx3`, Mac mini).
**Tables + receipts; recommend, the orchestrator decides.** Read first:
`AGENTS.md` (the lease rule changed 09-23: two mini boot slots),
`local/AGENTS.local.md`, `local/research/GB1/DESIGN.md` (the design; §2 and
§5 step (a) are your spec), and `local/research/G44/REPORT.md`.

## Why

The Odin title screen is bound by the GS rasterizer (N4: `WritePixel`,
`SampleTexture` and `DrawTriangle` on the GameThread). paraLLEl-GS already
matches the CPU backend frame for frame as a shadow (G44). Running it for
real needs a GS command queue and a GS thread, which is step (a). Step (a)
must change **nothing** observable: the CPU backend behind the queue is
byte-exact against direct calls.

## Where

- Worktree: `git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/GB2/PS2Recomp
  -b gb2-gs-queue ssx3`.
- Build dir: `~/dev/ssx3-work/GB2/build`, with generated code from
  `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3` (read-only; see
  `local/research/E32/REPORT.md` for the configure line).
- E44 owns `~/dev/PS2Recomp` itself and is editing `ps2_memory.cpp` /
  `ps2_runtime.cpp` there. Don't touch that checkout. At the end, report
  which files conflict with `ssx3`'s tip; E folds your branch later.

## Change (default off: `PS2X_GS_QUEUE=1`)

GB1 §5 (a): `gs_worker` (ring + GS thread + moved decode). Submits enqueue.
Readbacks and `FINISH`/`present`/`reset` are RPCs with fences, per §2c.
Ring: GB1's provisional 1024 descriptors / 16 MiB. With the flag off, the
code path is identical to today.

## Tests (pass = all three)

1. Existing suites green, unmodified (run from the worktree root, flags
   unset).
2. New determinism test: direct vs queued on synthetic streams plus one
   captured packet stream. `SnapshotVram`, `Present` pixels and consume
   bytes must be byte-exact.
3. Boot A/B (E33 vsync route to Select Character, 300 s each, queue off
   then on). Frame hashes at matched guest vsyncs must be byte-exact over
   ≥20 snapshots. Take one mini slot per boot with
   `local/tooling/p_lane_lease.py`, boot from your own cwd, and track your
   runner by PID. Diagnostic build: don't quote speed.
   Also report: GameThread vs GS-thread CPU split (from `sample` or
   `spindump`), and guest vsyncs/s for both (labelled diagnostic).

## Budgets and stop rules

Builds as needed, ≤4 boots, 6 h, cap 5 GB for new dirs. If byte-exactness
fails, stop at the first divergent command. Record the command index,
which RPC was involved, and both hashes, then hand back. Don't tune.

## Deliverable

`local/research/GB2/REPORT.md` with these sections:
- diff summary
- tests
- A/B table
- CPU split
- conflict list vs `ssx3`

Make an `[GB2]` commit (`git add -f local/research/GB2
local/muse/prompts/GB2.md`, `git log -1` first, trailer `Orchestrated-By:
Muse Code`). Commit on `gb2-gs-queue` in the fork. Don't push it: the
orchestrator decides on the fold.
