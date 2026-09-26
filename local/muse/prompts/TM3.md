# TM3 — confirm the rider integrator, then the first 120 Hz conversion probe (muse, 2.5 h)

## Goal
TM1 confirmed SSX 3's 60 Hz chain live (1 producer → 1 consume → 1 app update `0x2306b8` → 1 render per VBlank; manager A: rate `A+0x10`=60, dt `A+0x14`=float(1/60) `0x3c888889`, multiplier `A+0x24`=1.0, accumulator `A+0x28`, catch-up bound `A+0x20`=12). TM2 (`local/research/TM2/REPORT.md`) found `0x5409c0` is a per-VBlank snapshot copy (`sq` at `0x120e40`) of the rider object's live position `[obj+0x110]`. This lane (1) names the writer of `[obj+0x110]`, and (2) runs RV6's **partial conversion probe** (`docs/research/review-2026-09-26-astra-120hz.md` §5 rank 2) to see which game-time consumers follow the manager's rate/dt and which don't. Research only: nothing ships.

## Part A — the integrator (≤ 1 build, ≤ 2 boots)
Using TM2's diag build and `PS2X_DIAG_WATCH` (+ `PS2X_DIAG_WATCH_TICKS`), resolve `obj` (TM2's `a0` at `0x120e40`; log it once) and watch `[obj+0x110..0x11f]` over ticks 1799–1899: writer PC(s), owning `sub_`, caller chain two levels, thread, and whether the write is inside the app update (`0x2306b8`'s dynamic extent: bracket it with TM1's tap). Table it; also note any use of `A+0x14` (dt) or `A+0x10` (rate) on that path (read the owning functions in `~/dev/ssx3-work/codegen-ssx3/`, read-only).

## Part B — the probe (≤ 2 builds, ≤ 4 boots)
A default-off dev knob `PS2X_TM_RATE120=1` that, at the manager's init (after its constructor stores the stock values; verify them first and refuse on mismatch), sets `A+0x10=120`, `A+0x14=0x3c088889` (float 1/120), `A+0x24=2.0`, `A+0x28=0.0`, leaving `A+0x20`, render mode, hardware clocks and audio untouched. Boots: FR1-R1 to t2400 stock (control) and probe, det mode, on the mini, with TM1's tap + the watch from Part A. Report, per VBlank in the race window: producer records, consumes, app updates, renders; rider distance per VBlank and per game-clock second; HUD clock at ticks 1800/2100/2400 (screenshots viewed); SND counters; whether the route still reaches the race (if not, report where it diverged — do **not** patch the route). Expected per RV6: 2 updates per VBlank; the question is which motion/clock consumers halve their step (follow dt) and which don't (hard-coded 1/60 or per-update constants).

## Rules
Fork worktree `~/dev/ssx3-work/TM3/PS2Recomp`, branch `tm3` from fork `ssx3` tip (+ TM1's tap and TM2's watch commits cherry-picked as needed); never push; runner-dir check empty. Speed numbers are not the point: the diag build is slow. Bounded logs. Text only in git; screenshots stay in scratch. Workers don't edit `docs/`. First failure: stop, save the error, hand back.

## Deliverable
`local/research/TM3/REPORT.md` (integrator table; probe table stock vs probe; which consumers follow dt; the first unconverted consumer if identifiable; commands, SHAs, gaps) + `[TM3]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
