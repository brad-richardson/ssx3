# GV1 — VU1 on the GPU: feasibility spike (Opus, design-only + one Mac microbenchmark, 4 h)

## Goal
Brad (09-26) likes the moonshot: run SSX 3's VU1 microprograms as GPU compute and feed their primitive output to
paraLLEl-GS on the GPU, taking the MTVU unit thread (~32 ms/frame on the Odin, the frame's bottleneck) off the CPU.
It is parked as product work; this spike answers whether it could ever work, what it would cost, and what the first
proof would be. **No product code.**

## Facts
- VU1 today: static recompile (7 images, `~/dev/ssx3-work/vu1gen-ssx3`), blocks (VR2), exact SIMD FMAC core (VR4,
  `local/research/VR4/REPORT.md`: bit-exact over 20M cases), threaded unit (MT1). CP1 Table 3 hot blocks.
- GS: paraLLEl-GS (fork `ssx3` `3d72467`) — find how it ingests GS packets today (CPU-side parsing into GPU batches?).
- Odin GPU is **not idle**: CP1 Table 4, kgsl busy ~50 % at 660 MHz ≈ 24.8 ms GPU time per frame at 0.425× — so GPU
  headroom at full speed is limited unless clocks rise. Budget this honestly.
- Accuracy target: PCSX2 parity (AGENTS.md); determinism required.

## Questions
1. **Program census** of the 7 images: loop structure (per-vertex loops?), branches, XGKICK points per run, EFU ops
   (ESQRT, ERSQRT, …), integer/flag use, memory access patterns. Which programs cover most unit time?
2. **Exactness on GPU:** PS2 float semantics (no denormals/inf/NaN, clamping, rounding differences) in a compute
   shader. Port the VR4 exact FMAC core (or its hot subset) to a GLSL/SPIR-V compute kernel and **microbenchmark it on
   the Mac** (MoltenVK) against the CPU SIMD core: ops/s exact vs plain float. Bit-exact check on a sample of VR4's
   test vectors. This is the one allowed prototype.
3. **Data path:** VIF1 unpack → VU1 memory → XGKICK → GIF → paraLLEl-GS. What would move to the GPU, what stays on the
   CPU, what would paraLLEl-GS need to consume a GPU-produced primitive stream, and where are the sync points
   (EE reads of VU1 state — MT1 census hooks; PATH3 interleaving; VIF1 stalls)?
4. **Cost model:** GPU time per frame for today's VU1 work (from the microbenchmark and the census), CPU time saved,
   added latency (frames), dispatch overhead per job vs batching a frame's jobs, and the effect on the Odin's GPU budget.
5. **Verdict + staged plan:** go/no-go criteria, the smallest proof (e.g. one hot program on the GPU, output compared
   bit-exact with the CPU path on a trace), and the risks. Relate to what any PS2 emulator has done (PCSX2 and newer
   ones per `docs/research/review-2026-09-26-astra-emulators.md`).

## Rules / budgets
Read anything under `~/dev`. Code only in `~/dev/ssx3-work/GV1/` (the microbenchmark; not in any fork). Mac only: no
Odin, no device installs. The microbenchmark must not disturb speed holds: check `p_lane_lease.py` and don't run it
while another lane holds all four mini slots. 4 h. Read-only fan-out subagents are fine.

## Deliverable
`local/research/GV1/REPORT.md`: census table, exactness + microbenchmark results (with the kernel's source SHA and
exact commands), data-path diagram in text, cost model with its assumptions, verdict, staged plan, gaps. Commit
`[GV1] …` with `git add -f` (report + small text receipts), trailer `Orchestrated-By: Claude Code`, no push.
