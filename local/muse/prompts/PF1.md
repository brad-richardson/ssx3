# PF1 — Clean performance baseline of the PS2 recomp: release build, diagnostics off, profiled on the Odin (now) and the Mac (after E31)

You are muse in a herdr panel in the ssx3 repo (repo root = two up from
`local/muse/prompts/`). **Tables + receipts; recommend, the orchestrator
decides.** Read first: `local/research/N3/REPORT.md` (first Odin boot;
APK, `ps2x.env` shim, ~21 guest frames/s with frame dumping ON),
`local/research/E29/REPORT.md` (Mac build recipe), `AGENTS.md` +
`local/AGENTS.local.md`.

## Why

Every speed number so far comes from diagnostic builds: frame dumps, a
~7 MB/s function trace, and always-on dispatch tallies. The architecture
question is whether the single-threaded runtime (EE code, VU1
interpreter, CPU GS rasterizer, IOP HLE and MPEG on one host thread)
can reach real time, let alone the ~2× that 120 Hz simulation needs. It
must be answered with a clean build before more features pile on. Note
that pacing follows the wall clock (VBlank fixed at 16667 µs,
`SetTargetFPS(60)`), so speed = guest vsyncs per wall second ÷ 59.94.

## Mission 1 — Odin (N3's APK, no rebuild unless needed)

Needs the Odin lease (G42 may hold it; wait, then claim). Battery ≥ 20 %
**and charging**. If it isn't charging, stop and say so in the pane.
1. Launch N3's arm64 APK with `ps2x.env` = `PS2X_CD_IMAGE` +
   `PS2X_SKIP_MOVIE=1` only (**no** frame dump, no diag vars). Confirm
   from N3's build flags that aggressive logs are off.
2. Measure at the title screen for 3 minutes: guest vsyncs/s (from a
   cheap existing counter, or add none and use SurfaceFlinger
   `--timestats` presents/s for the layer), CPU per thread (`top -H`),
   frequencies, thermal.
3. `simpleperf record -g` for 30 s on the runner process (the NDK's
   simpleperf, `--app com.ps2x.runner` or by pid). Report the top 40
   symbols and a rollup by component: guest code (`sub_*`), VU1
   interpreter, GS CPU rasterizer, GS frontend/GIF, IOP/HLE stubs, MPEG,
   raylib/present/upload, dispatch/diagnostic overhead
   (`tallyDispatch` etc.), libc/kernel.
4. If E31 has published a pad script that reaches the Snow Jam loading
   screen or a race, one more launch with it, measuring the same way on
   the heaviest reachable screen.

## Mission 2 — Mac (only after E31 has closed; it owns the lease)

Build a release configuration in a NEW build dir on the SSD from the
fork worktree (read-only on the source; don't check anything out):
E18's recipe with `PS2X_ENABLE_RUNTIME_LOGS=OFF`,
`PS2X_ENABLE_AGRESSIVE_LOGS=OFF`, optimization as the recipe has it.
Boot with `PS2X_SKIP_MOVIE=1` under the P-lane lease, measure guest
vsyncs/s at the title screen, and profile with `xctrace` (Time Profiler)
or `sample`. Same component rollup.

## Deliverable

Per platform: speed as % of real time, CPU-ms per guest frame, a thread
table, and the component rollup with the top symbols. Then a short
recommendation on which parts would need to move off the main thread (GS,
VU1, present) to reach 1× and 2×, backed by the numbers. Also which
always-on diagnostics are worth compiling out, with their measured cost.

## Rules

- Odin: `/data/local/tmp/pf1/` for simpleperf output, removed at end;
  lease protocol; up to 3 launches. Mac: 1 build, up to 2 boots ≤ 300 s
  each, under the lease.
- No source edits on the fork; build flags only. Nothing pushed.
- Evidence `local/research/PF1/` text only (perf reports as text).
  `[PF1]` commit with `Orchestrated-By: Muse Code`, `git add -f`, no push;
  check `git log -1` first. Time box 5 h.

## Mini resume (orchestrator, 2026-09-22 evening) — scope change

You are on the Mac mini now (`~/dev/ssx3`, read `local/AGENTS.local.md`).
The Odin is on the mini's USB (`622c49b1`). `/tmp/pf1*` was restored.

1. **Wait for G42** to release the Odin lease (it goes first; ~30 min).
2. **Launch 6 targets the race, not Snow Jam.** E31 got a full stock race
   on the Mac with **Happiness (Rival Challenge)**; Snow Jam stalls at 99%.
   Use E31's e31l pad script (see `local/research/E31/REPORT.md`; if E31's
   close-out hasn't written the exact string yet, rebuild it from e31l's
   `[padscript] press` lines as you did for e31h). Same clean env as
   launch 5 otherwise. Wall cap for this launch: **900 s** (orchestrator
   OK). Measure guest vsyncs/s (tick progression) separately for title,
   menus, loading and in-race; screencap every ~35 s, and pin the first
   race-HUD screencap (timer visible) with two SHA reads. This doubles as
   the first Odin native race attempt, so say plainly whether the race
   timer advances.
3. **Mission 2 (Mac release build) is removed from PF1.** It becomes a
   separate brief on the mini after E32 lands the folded branch.
4. Then force-stop, release the lease, REPORT.md, `[PF1]` commit.
