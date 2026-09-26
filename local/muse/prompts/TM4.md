# TM4 — where does the rider's per-update step come from? (muse, 2.5 h, research only)

## Goal
TM3 (`local/research/TM3/REPORT.md`, read it fully) showed SSX 3's manager can run 2 updates per VBlank (rate 120 / dt 1/120 / multiplier 2), but the rider integrators (`sqc2` at `0x1380b4` in `sub_00137D18`, `0x13e0dc` in `sub_0013D818`: `pos += delta`, `delta` precomputed on the stack `[sp+0x60]`/`[sp+0x50]`) take full-size steps and the HUD clock divides by 60. For a true 120 Hz simulation we need the per-update step constants. Find where `delta` is computed and which constants (1/60 literals, per-update velocity scales, friction/accel/gravity per step) feed it; then one coherent probe that halves them together with the manager change and checks motion per game-second.

## Steps
1. **Trace `delta`:** in the two owning functions (codegen `~/dev/ssx3-work/codegen-ssx3/`, read-only; derived from game data, never committed), follow the stores to `[sp+0x60]`/`[sp+0x50]` back to their inputs: velocity fields of `obj` (`0x1465c40`), and every float constant or global multiplied in. Use TM2/TM3's watch tooling (`PS2X_DIAG_WATCH` on the velocity fields over ticks 1799–1899) and TM1's tap to confirm live values. Table: symbol/address, value, what it scales, whether it equals 1/60, 60, or a multiple.
2. **Census of timestep literals:** search the ELF's float constants for 1/60 (`0x3c888889`), 60.0 (`0x42700000`), 1/30, 30.0, 0.5×-scaled variants, and list which of them are read during the race window (a read-watch if the tooling supports it, else code references from the integrator call tree two levels down). Distinguish physics, animation, camera, HUD, audio.
3. **One coherent probe** (dev knob `PS2X_TM_RATE120=2`, default off; builds on TM3's `=1`): manager rate/dt/multiplier as in TM3 **plus** halve the step constants you identified for the rider path (and the HUD clock divisor if found). Measure as TM3 did: updates/VBlank, rider distance per VBlank and per HUD-second (target: per-VBlank ≈ stock, i.e. 2 half-steps), HUD clock slope, route reaches the race. If motion per game-second doesn't match stock within ~5 %, report the first unconverted consumer; no tuning loops.

## Rules
Worktree `~/dev/ssx3-work/TM4/PS2Recomp`, branch `tm4` from fork `ssx3` tip (+ TM1/TM2/TM3 commits cherry-picked); never push; runner-dir check empty; diag build on the mini (`mac_build.sh --det --diag`), one slot per boot. ≤ 3 builds, ≤ 6 boots. Text only in git; screenshots in scratch. Workers don't edit `docs/`. First failure: stop, save the error, hand back.

## Deliverable
`local/research/TM4/REPORT.md` (delta source table, literal census, probe table vs stock, first unconverted consumer, commands, SHAs, gaps) + `[TM4]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
