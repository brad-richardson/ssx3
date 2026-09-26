# MD1 — why loading runs at 0.32× on the Odin: count the GPU work per loading frame (muse, 2.5 h)

## Goal
N12 (`local/research/N12/REPORT.md`, gate): Odin menus now run 0.85–1.12×, but **loading (ticks ~1440–1714) runs 0.32×**. That window is GsWorker-pool-bound: ~3 GsWorker threads at 100 %, ~65 % of samples inside Turnip's driver CPU, plus Granite `HybridMutex` lock churn and scudo malloc/free. Our own paraLLEl/GS code is < 1 %. Hypothesis: loading issues many small GS uploads/draws that paraLLEl turns into many submits, descriptor updates, buffer allocations or pipeline binds, and the driver's per-call CPU cost dominates. Measure that on the Mac (same paraLLEl code; driver-independent counts), then make **one** candidate fix in the paraLLEl-GS fork if a single mechanism is named.

## Facts
- paraLLEl-GS fork `ssx3` `19d93b2` (Granite `166ba21a`); PS2Recomp fork `ssx3` `a3efbfe`. Your worktrees `~/dev/ssx3-work/MD1/{parallel-gs,PS2Recomp}` (local branches `md1`; never push).
- Build: `local/tooling/build/mac_build.sh <PS2Recomp-wt> <build-dir> --pgs <your parallel-gs wt>` (ccache). Boot: `local/tooling/boot/ssx3_boot.py` (FR1-R1, paraLLEl, `PGS_HIER_BINNING=force`); control: `local/tooling/boot/baseline.py` key `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`.
- Odin phase boundaries (I26-FAST/FR1-R1 on the vsync pad clock): Mode/Event 1099→1440, loading/Rival card 1440→1714, race 1714+.
- VK1 (Opus) is changing paraLLEl's *presentation* path on its own branch; stay out of present/scanout code.

## Steps
1. Add default-off counters (`PGS_STATS=1`, a Granite/paraLLEl-side tally printed once per guest vsync as one line): per vsync, the number of `vkQueueSubmit`/Granite `submit` calls, command buffers, descriptor-set allocations/updates, buffer/image allocations (and bytes), pipeline binds, `vkCmdCopy*` uploads, flushes/fences waited, and `HybridMutex` lock count if cheap. Cite each counter's source line.
2. One det boot with the counters to t2400 (one mini slot). Table the per-vsync means for Mode/Event, loading, and race; name the counters that jump in loading.
3. If one mechanism is named (e.g. a submit/flush per GS upload, a buffer allocated per transfer, a descriptor set per draw), make one fix that batches or reuses it, default **on** only if the det-hash stays IDENTICAL vs the baseline and frames at 1090/1800/2100 match; also print the counters after the fix. Otherwise stop and hand back the table.
4. Mac speed pair (exclusive lease ≤ 5 min, clean build, loading-phase vsyncs/s from `[vsync-rate]`, ABBA base vs fix). The orchestrator schedules the Odin check.

## Rules
≤ 5 builds, ≤ 6 boots (one slot each) + 2 exclusive holds. No Odin. Suite green; runner-dir check empty; never `git add -f` in a fork. Scratch `~/dev/ssx3-work/MD1/` ≤ 10 GB. Text only in git; workers don't edit `docs/`. First failure: stop, save the error, hand back.

## Deliverable
`local/research/MD1/REPORT.md` (counter table per phase with source lines, the named mechanism or "none", fix diff summary, det/frames result, speed pair, fork commit list, gaps) + an `[MD1]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
