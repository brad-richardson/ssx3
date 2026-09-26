# GG1 — Where does paraLLEl-GS spend the Odin's GPU? (muse, Part 1 = measure + rank levers, 4 h)

## Goal
The Odin's next wall after the MTVU unit is the GPU (GV1 §4, `local/research/GV1/REPORT.md` + gate): paraLLEl-GS alone
≈ **15.5 M GPU cycles per guest frame** (23.9 ms at 660 MHz; 19.7 ms at ~800 MHz, 75–78 % busy at 0.64×). Full speed
needs ≥ 930 MHz at 100 % busy; 967 MHz is the highest clock logged. To reach ~90–100 % speed with headroom we need GS
GPU work well under ~12 M cycles/frame. Part 1 finds where the cycles go and ranks the levers. **No product change in
Part 1; hand back the tables.**

## Facts
- Pins: fork `ssx3` `1c37c41` (Android side = `1425844`), paraLLEl-GS `ssx3` `3d72467`, Granite `166ba21a`; Odin play
  build = F8 once it lands (`local/research/F8/REPORT.md`; patched Turnip `a315b74a…`). Odin runs at 1× (no SSAA),
  pipelined present, Vulkan present (VK1/VK2), hierarchical binning forced (`PGS_HIER_BINNING=force`, GB9), wave64
  forced because the binner mis-bins at wave128 on Adreno (`docs/facts.md` ~line 73, N8X1).
- CP2 is profiling F8 right now and was asked for GPU clock residency + busy; read its report if it has landed.
- GPU busy is crude (kgsl busy % counts any time work is queued). This lane needs **real GPU timestamps**.

## Part 1 steps
1. Find what timing paraLLEl-GS/Granite already has (timestamp queries, per-pass labels, `PARALLEL_GS_*`/`GRANITE_*`
   env or a debug build flag). Cite file:line. If per-pass timestamps need code, add them on a local branch `gg1` of the
   paraLLEl fork (diagnostic, default off, env-gated), no push.
2. **Mac first** (MoltenVK timestamps; mini lease, bradflix can't do Metal): I26-FAST race, t1714→t3000, per-pass GPU
   ms per guest frame + per-frame counts (draws/prims, tiles binned/shaded, CLUT/palette uploads, local↔host
   transfers, the present blit). Det-hash must stay IDENTICAL with the timers on (`baseline.py`).
3. **Odin** (after F8 and CP2 release it; lease tool): the same table on F8's source + your timers (one diagnostic APK
   via bytesize under `bytesize_lock.sh`), plus devfreq facts: available GPU frequencies, max, governor, and residency
   during the race. Diagnostic build → numbers labelled diagnostic (timer overhead stated).
4. Rank levers with expected cycle savings and exactness risk. At least consider: the wave128 binner fix; hier-binning
   tuning; per-pass redundancy (clears, copies, barriers, readbacks); the present blit / 16:9 scale pass; CLUT/palette
   churn; shader codegen on Turnip (a newer Mesa, `TU_DEBUG` sysmem/gmem for the present pass); anything SSX 3-specific
   (e.g. passes that run for off-screen targets). Every lever must keep `diff_px=0` / det-hash identical unless it's a
   PCSX2-parity rendering change (name it).

## Rules / budgets
≤ 4 Mac boots (+ speed holds need all four slots only for speed numbers; timing tables don't), ≤ 1 Android build,
≤ 4 Odin launches (every install/launch/force-stop under `odin_lease.sh`, keyguard + AC + ≥ 20 %, `odin_restore_play.sh
GG1` after each, fan left alone, screen-mode cool-down). Write only in `local/research/GG1/`, `~/dev/ssx3-work/GG1/`,
the `gg1` branch, bytesize `/home/brad/gg1/`. 4 h. First failure: stop, save it, hand back.

## Deliverable
`local/research/GG1/REPORT.md`: timer method (file:line), Mac pass table, Odin pass table + devfreq facts, lever ranking
(savings, risk, cost), pins/SHAs, exact commands, gaps. Commit `[GG1] …` with `git add -f`, trailer
`Orchestrated-By: Muse Code`, no push.
