# GB3 — GS queue: in-order priv stores (VQ 26/26), SetGsCrt SMODE, then paraLLEl live on the Mac

You are a worker in a herdr pane in the ssx3 repo (`~/dev/ssx3`, Mac mini).
Follow `~/dev/AGENTS.md`. **Tables + receipts; recommend, the orchestrator
decides.** Read first:
- `AGENTS.md`;
- `local/AGENTS.local.md`;
- `local/research/GB2/REPORT.md` (all parts; Part 7's mechanism is your
  Part 1);
- `local/research/GB1/DESIGN.md` §5 (b);
- `local/research/G44/REPORT.md` (the paraLLEl shadow and the SMODE1
  override).

## Part 1 — close step (a)

Worktree off fork `ssx3` `eac6cba`, on branch `gb3-gs`, with GB2's
`gb2-gs-queue` (`c5fd6f3`) rebased onto it. Canonical codegen.

1. Route direct guest priv-register **stores** (`write32/64` →
   `gsRegs` on the game thread) through the worker as in-stream
   `RegWrite`/priv commands when the queue is on. That preserves program
   order relative to queued packets. Keep GB2 Part 7's load fence.
2. Re-run the VQ gate: queue-off vs queue-on+drain, two on-boots.
   - Pass = VRAM fnv identical at all 26 ticks **and** the two on-boots
     bit-identical.
   - Report presents/s and wall ticks/s.
3. `SetGsCrt` (syscall 0x02) HLE: program SMODE1/SMODE2 the way the real
   kernel does (NTSC/PAL, interlace, field/frame) so a real scanout
   backend doesn't need `PS2X_GS_SHADOW_FORCE_SMODE1`. Unit test it.
   Confirm the CPU presenter is unchanged (frame hashes at matched ticks
   with the queue off).

## Part 2 — step (b): paraLLEl as the live backend on the Mac (only after Part 1 passes)

- Bring G44's shadow code (`g44-parallel-shadow`) onto `gb3-gs` as a
  queue-fed live backend, `PS2X_GS_BACKEND=parallel`, with an interim
  present of one GPU→CPU copy and `UpdateTexture`.
- Validate on Select Character and in the race, against the CPU backend
  at matched ticks: G-lane diff method, PSNR plus viewed side-by-sides.
- Measure the GameThread/GsWorker CPU split and presents/s with a
  diagnostic label.

## Budgets and stop rules

Builds as needed, ≤6 boots (one slot each; other lanes share the mini:
wait for a free slot, and use `nice` for builds), 8 h, cap 8 GB. If VQ
still fails after Part 1's store routing, stop and hand back the first
differing packet or reg event.

## Deliverable

`local/research/GB3/REPORT.md`. `[GB3]` commit (`git add -f
local/research/GB3 local/muse/prompts/GB3.md`, `git log -1` first,
trailer `Orchestrated-By: Claude Code`). Fork commits stay on local
`gb3-gs`; no push.
