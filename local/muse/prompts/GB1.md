# GB1 — Design the runtime ↔ GPU GS bridge (read-only design + a costed build plan; no code lands)

You are muse in a herdr panel in the ssx3 repo (repo root = two up from
`local/muse/prompts/`). **Design document + tables; recommend, the
orchestrator decides.** Read-only everywhere: fork at
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (use `git show
fork/ssx3:<path>` / `git grep`, never check out; E31 owns the worktree),
the paraLLEl-GS clone `parallel-gs-g7` and `~/dev/ps2xGS`. Read first:
`docs/research/review-2026-09-20-first-frame-and-gs.md` (§ around line 239:
the integration review), `docs/plan-gs-gpu-backend-2026-09-18.md`
(partly stale: it describes a greenfield backend), `AGENTS.md`.

## Why

The G lane has proven paraLLEl-GS only as a standalone replayer of
PCSX2 dumps. The recomp's own GS stream has never gone through it. The
runtime's backend interface (`ps2xRuntime/include/runtime/gs/gs_backend.h`)
receives decoded primitives and returns host RGBA, but paraLLEl consumes
GIF transfers and register writes. Rebuilding GIF traffic from decoded
primitives would lose ordering and state. The presentation path today
(`gs_frontend.cpp` ~535, `ps2_runtime.cpp` ~490) flushes and syncs every
display tick, reads back host pixels, copies them, and re-uploads with raylib
`UpdateTexture`. A correct GPU GS would still stall on that.

## Deliverables (one design doc: `local/research/GB1/DESIGN.md`)

1. **Seam.** Where the runtime sees GIF packets, GS privileged register
   writes (PMODE, DISPFB, …), image transfers (host↔local), and
   readbacks today (file + function + line at `fork/ssx3`). Propose the
   interface at that boundary: a packet queue in, sync/readback points
   out. Show that the CPU backend can sit behind the same interface as
   the reference implementation.
2. **Threading.** A GS thread fed by the queue (like PCSX2's MTGS): who
   owns VRAM, when the EE must wait (readbacks, `FINISH`/`SIGNAL`/CSR,
   image transfers local→host), and ring sizing. Estimate how much moving
   even the CPU GS off the main thread would save, using PF1's numbers if
   they've landed.
3. **Presentation.** A GPU-resident path: scanout straight from the
   backend's image into the swapchain (Vulkan on Android, MoltenVK on the
   Mac, or a shared texture with raylib's GL context). Explicit
   readbacks only for transfers and diagnostics. What changes on
   Android versus the Mac.
4. **Upstream check.** Summarise upstream's `feature/iop-emulator`
   branch (`git log`/`git diff` from `fork/main` to
   `refs/remotes/fork/feature/iop-emulator` or `origin` equivalents):
   does it refactor the GS architecture in a way that changes where
   this seam should go? Read only; no contact.
5. **Build plan.** Ordered steps, each with its test: (a) CPU backend
   behind the new queue on its own thread, on the Mac; (b) paraLLEl
   backend on the Mac via MoltenVK, one live runtime frame compared
   against the CPU backend; (c) Android Vulkan; (d) presentation without
   readback, with its frame-time cost. Files per step, which lane owns
   them (E owns the fork; G owns the paraLLEl patch stack), and a size
   estimate.

## Rules

- No builds, no boots, no device, no leases, no fork mutations.
- Evidence `local/research/GB1/` text only. `[GB1]` commit with
  `Orchestrated-By: Muse Code`, `git add -f`, no push; check `git log -1`
  first. Time box 4 h.
