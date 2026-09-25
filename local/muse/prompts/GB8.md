# GB8 — make paraLLEl-GS (GPU) the Mac's standard backend: speed, determinism, parity (muse, 2 h)

## Goal
Brad (09-24): render on the GPU on the Mac too, with paraLLEl, so Mac boots are faster and exercise the same renderer as the Odin, and fewer questions wait on the single Odin. On the Mac the CPU GS rasterizer is now ~47–60 % of GameThread in the race (E57 profile), all on the one game thread. The paraLLEl backend already runs live on the Mac as an opt-in (GB6/GB6C: `PS2X_GS_BACKEND=parallel`, race reached tick 2218 in 70.7 s). Part 1 measures what switching the default would change; the orchestrator decides.

## Facts
- Fork `~/dev/PS2Recomp` `ssx3` `f949ff0`; paraLLEl-GS fork `ssx3` `963cb57`; Granite fork `ssx3` `166ba21a`. Build recipe with paraLLEl: `local/research/GB6/REPORT.md` / `GB6C` (CMake `PS2X_GS_SHADOW_PARALLEL=ON` + the paraLLEl source dir; confirm the exact flags there). Canonical codegen `~/dev/ssx3-work/codegen-ssx3`.
- Mac `[gs-path]`: `hier_rule=flat-always` (`#ifdef __APPLE__`), `desc=plain`; the Odin uses hierarchical binning at wave64 + descriptor buffers (TL1 gate). So Mac paraLLEl ≠ Odin path in binning; note it, don't change it.
- Known differences: small-text/glyph damage on paraLLEl vs CPU from the same stream (GB5C, GB7C7P2); bilinear rounding differs Mac vs Adreno (N8X1).
- Route I26-FAST, empty mc0, `PS2X_SKIP_MOVIE=1`, boot template `local/research/E55D16/e55d16_boot.py` (or GB6C's driver). Determinism: `PS2X_DETERMINISTIC=1` + det-hash tap build (`PS2X_ENABLE_DET_HASH_TAP`, `PS2X_DET_HASH_EVERY`; E55C2).

## Questions and observables
| Q | Observable |
| --- | --- |
| Q1 speed | clean build (diagnostics off), exclusive lease (`p_lane_lease.py claim GB8speed --exclusive`, all 4 slots, ≤ 5 min each): per-phase guest vsyncs/s ÷ 59.94 (title, menus, loading, race window 1800–2400) for CPU vs parallel, same binary. Also wall time from launch to race HUD (~t1714). |
| Q2 determinism | det-hash build, deterministic, to t2400: CPU vs parallel `[det-hash:v1]` lines — identical or first differing tick (differs only if the guest reads GS memory back). Plus parallel vs parallel (repeatability). |
| Q3 parity | frames at the same ticks from Q2's boots: Title (~600), Main Menu (~750), Select Peak (~1090), Select Mode (~1180), race (1810, 2100, 2400). View each pair; table of visible differences (glyphs, sky, dark region, stripes). Text notes only in git. |
| Q4 host cost | per-thread CPU % (`ps -M` or `top -l`) in the race for both backends: does GameThread drop, and what do GsWorker/GPU threads use? |

## Rules
Mac only. Budgets: ≤ 2 builds (clean + det-hash; each may include paraLLEl), ≤ 6 boots (2 speed, 4 det/frames), ≤ 600 s each, 2 h. One slot per non-speed boot; check/kill your runner by PID. No source changes (if a flag is missing, stop and report). Scratch `~/dev/ssx3-work/GB8/` ≤ 10 GB. Text only in git. No upstream contact. First failure: stop, save the error, hand back.

## Deliverable
`local/research/GB8/REPORT.md` (Q1–Q4 tables, exact build flags and commands, runner SHAs read twice, frame paths in scratch for the orchestrator to view, gaps) + scripts; commit `[GB8] Part 1 …` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push. Recommend a default (env in boot tooling vs build default); the orchestrator decides.
