# FR1 — finish a race, and cover more events (muse, 3 h, Mac)

## Why
No race has finished in our runtime yet: SJ1 showed the I26-FAST 30 s d-pad-down hold brakes the rider (`local/research/SJ1/REPORT.md`); with no race inputs the rider rode to 52 % by 00:02:38 before the cap. VR1's VU1 recompile covers 7 code images seen on the Happiness route; other events may use others (they fall back to the interpreter, slower but correct).

## Runs (fork `ssx3` tip — use the F3 tip if F3 has pushed by the time you build, else `0ed07c4`; paraLLEl env + `PGS_HIER_BINNING=force`, `PS2X_SOUND=1`, `PS2X_SKIP_MOVIE=1`, empty mc0, one mini slot each)
1. **Route fix:** a copy of I26-FAST without the 30 s down-hold (`local/research/I26/ROUTES.md`); write it to `local/research/FR1/ROUTES-FR1.md` with the exact string; don't edit ROUTES.md (the orchestrator will).
2. **R1 full race:** that route, no race inputs, until the results screen (approved: ≤ 1,800 s wall; stop if the race clock doesn't advance for 60 s). Frames every ~30 s; table of clock/progress/place; the end state (results screen, menu return, hang). `PS2X_COVERAGE_TICK` near the end: targets/syscalls/RPC.
3. **R2 Snow Jam** (E31 route, as SJ1 R2) and **R3 one more event of your choice** reachable from the menus without a save (e.g. Metro-City or a Freestyle event), each ≤ 700 s, with `PS2X_VU1_RECOMP_DUMP=<scratch dir>` **only if your build includes VR1's code** (it won't on `0ed07c4`/F3 — then skip the dump and just record which events load and race). Report new VU1 code-image hashes seen (the dump dir file names) if available.
Budget: 1 build, ≤ 4 boots, 3 h. No source changes; if a route needs a knob that doesn't exist, stop and report. Text only in git. Deliverable `local/research/FR1/REPORT.md`; commit `[FR1] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push.
