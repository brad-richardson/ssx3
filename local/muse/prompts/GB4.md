# GB4 — GS queue and paraLLEl gated by stream replay, not free-running boots

You are a worker in a herdr pane in the ssx3 repo (`~/dev/ssx3`, Mac mini).
Follow `~/dev/AGENTS.md`. **Tables + receipts; recommend, the orchestrator
decides.** Read first:
- `AGENTS.md` (two-slot lease: `local/tooling/p_lane_lease.py`; kill by PID);
- `local/AGENTS.local.md`;
- `local/research/GB3/REPORT.md` (all of it; §0, §5, §6 and §8 matter most);
- `local/research/GB2/REPORT.md` Part 1 (the 256-packet captured-stream
  test: your template).

## Why

GB3 showed that free-running VQ can't gate the GS queue. The tick at which
the game reaches `sceGsResetGraph` (packet 0) already differs by ±1 between
boots, before the GS does any work, and queue-off boots land in the same
attractors (GB2's baseline C was a +1 boot). Also, VRAM is a pure function
of the GS command stream on the CPU backend (GB3 §5). So we gate on the
**same stream in, same VRAM out**: capture once, replay through every
backend. Timeline determinism is a separate lane (E55).

## Part 1 — capture + replay harness, queue gate

Work on fork worktree `~/dev/ssx3-work/GB3/PS2Recomp` (branch `gb3-gs`,
`574354a`; its build dir `~/dev/ssx3-work/GB3/build`). New commits go on a
new branch `gb4-replay` from `gb3-gs`.

1. **Capture** (env-gated, e.g. `PS2X_GS_CAPTURE=<file>`, off by default,
   zero cost when off): at the GS frontend's entry, record every GIF packet
   (path + bytes), every priv/HLE register write (GB3's `privWrite` sites:
   reg, value), every local→host / host→local transfer, and a tick marker at
   each VBlank. Binary, length-prefixed, zstd or gzip on close. **Byte cap
   6 GB uncompressed per capture**; stop capturing at the cap and log it.
2. **Replay tool** (a `ps2x_tests` case or a small `ps2xGsReplay` binary in
   the fork's tools/test tree, not in `runner/`): reads a capture, feeds it
   to a chosen backend + mode (`direct` / `queue`), and at every Nth tick
   marker writes the VRAM fnv, the priv-reg fnv, and the Present hash;
   optionally PPMs at named ticks.
3. **One capture boot** (queue off; the GB3 route; `PS2X_PAD_SCRIPT_CLOCK=vsync`,
   `PS2X_SKIP_MOVIE=1`; ≤540 s) that runs **into the race** (GB3's gb3a
   reached race load at tick ~4056 and the race frames later). Record where
   the capture ends (tick) and its size.
4. **Queue gate:** replay the capture direct vs queue (fence on), and queue
   twice. Pass = VRAM + priv + Present hashes identical at every marker, in
   all three. Also compare replay-direct to the capture boot's own live VQ
   lines at matching ticks (proves the capture is complete).
5. Negative control: replay with the priv-write stream dropped must fail.

## Part 2 — paraLLEl live (after Part 1 passes)

- Build `gb3-parallel-wip` (`f907deb`) rebased as new commits onto
  `gb4-replay` (cherry-pick, no history rewrite) with
  `PS2X_GS_SHADOW_PARALLEL=ON`. Fix compile errors in the WIP only.
- **Replay** the same capture through `PS2X_GS_BACKEND=parallel`. At the
  Select Character ticks and ≥3 race ticks, give PSNR vs replay-direct CPU,
  and view the side-by-sides yourself (write what you see: rider, terrain,
  HUD, fonts). Record the `unsupported` counters (HLE clears, debug VRAM I/O).
- **One live boot** with `PS2X_GS_BACKEND=parallel`: does it reach the race?
  Presents/s and the GameThread/GsWorker CPU split. **Label it diagnostic.**
- Check whether `PS2X_GS_SHADOW_FORCE_SMODE1` is still needed now that
  `sceGsResetGraph` programs SMODE1 (GB3 Part 1b).

## Budgets and stop rules

≤4 boots (one lease slot each; other lanes share the mini: `nice` builds,
wait for a free slot), 8 h, cap 12 GB new bytes (captures included; delete
superseded captures). If the replay direct vs capture-boot live check
(step 4) disagrees, stop there and hand back the first differing tick and
what the capture lacks. If queue replay fails, hand back the first
differing marker plus the command index. Don't go to Part 2.

## Deliverable

`local/research/GB4/REPORT.md` (tables, commands, runner SHAs ×2, capture
sizes, side-by-side PNGs ≤10 MB total). `[GB4]` commit (`git add -f
local/research/GB4 local/muse/prompts/GB4.md`, `git log -1` first).
Fork commits stay on local `gb4-replay`; no push. Runner-dir check
(`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty) in the
report.
