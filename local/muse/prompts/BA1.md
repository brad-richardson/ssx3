# BA1 — Android build flags: the Odin build is -O2 without ThinLTO (muse, 3 h)

## Goal
RV4 (`docs/research/review-2026-09-26-astra-perf.md` §1 "Android build evidence", orchestrator adoption) found, and the orchestrator verified: `android/app/build.gradle:69` builds `-DCMAKE_BUILD_TYPE=RelWithDebInfo` (CMake default `-O2 -g -DNDEBUG`), and `ps2xRuntime/cmake/ReleaseMode.cmake` sets only `INTERPROCEDURAL_OPTIMIZATION_RELEASE`, so the APK gets no IPO. Every Mac speed number comes from `Release` (`-O3`) with IPO on `ps2_runtime`/`ps2EntryRunner` (`CMakeLists.txt:769-770`); the EE archive `ps2_game_objects` gets none on either. Measure what `-O3` and ThinLTO are worth on the Odin, keeping symbols and exact FP.

## Facts
- Fork `ssx3` tip **`173b31f`** (pushed). APK recipe: `local/research/F5/build-android.sh` on bytesize (hold the ssh open; `ps aux` first — VK1 and VR2 also build there; one heavy job at a time, wait your turn). NDK `28.2.13676358` (`build.gradle:17`). Codegen/VU1/paraLLEl inputs as F5 (paraLLEl now fork `ssx3` `464f263`).
- Odin method: `local/research/F5/launch.py` + `cooldown.py` (cool to status 0 + fixed 180 s; I26-FAST, unpaced, sound on, `PS2X_PGS_PRESENT_PIPELINE=1`, stop 4500; race rate via `local/research/F4/phases.py`). Brad's play env pin `a8d651a7…`; his save in `files/mc0/` is never touched (`mc0-test` empty); restore his play APK + env after every run (VK1's `local/research/VK1/restore-play.sh` does this). **VK1 is on the Odin now; wait for `LEASE_FREE`.**
- The Mac is not a proxy here (already `-O3`+IPO).

## Steps
1. **Audit (no Odin):** from the base APK build's `compile_commands.json`/ninja log on bytesize, record the effective flags for a generated EE TU, a VU1 image TU, a runtime TU, and the link line (`-O`, `-g`, `-flto*`, `-march/-mcpu`, `-fno-plt`, `-Bsymbolic`, exceptions/FP flags). Table it.
2. **Candidates, one variable at a time** (a fork worktree `~/dev/ssx3-work/BA1/PS2Recomp`, local branch `ba1` from `173b31f`, never push):
   - **O3:** RelWithDebInfo with `-O3 -g -DNDEBUG` for all our targets (e.g. `CMAKE_{C,CXX}_FLAGS_RELWITHDEBINFO` in the gradle `arguments`, or one CMake line). Keep `-g`.
   - **O3+ThinLTO:** plus `-flto=thin` on compile and link for `ps2_runtime`, `ps2EntryRunner` and `ps2_game_objects` (check the NDK's lld handles it, link time and peak memory on bytesize's 12 GB WSL; if it OOMs, report and stop that candidate). No full LTO, no fast-math.
   Each: APK size, build wall, `.text` size of `libps2EntryRunner.so`, and a Mac det check is not needed (same source) — instead confirm guest identity on the Odin by the route reaching the same screens with 0 FATAL.
3. **Odin ABBA** (≤ 8 launches): base (F5-style APK from `173b31f`, current flags) vs O3; then base vs O3+ThinLTO if O3 is kept. Race rate, per-phase table (menus/loading too), thermal at launch, GPU busy.

## Rules
≤ 4 Android builds. No source changes except build flags. Suite not needed (no source change); state it. Scratch `~/dev/ssx3-work/BA1/` ≤ 10 GB; bytesize `/home/brad/ba1`. Text only in git. Workers don't edit `docs/`. First failure: stop, save the error, hand back.

## Deliverable
`local/research/BA1/REPORT.md` (flag audit table, build/size table, ABBA table with legs, exact commands, APK SHAs, gaps) + `[BA1]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push. Hand back; the orchestrator decides what goes into F6.
