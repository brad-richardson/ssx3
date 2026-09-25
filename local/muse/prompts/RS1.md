# RS1 — shared compile cache (ccache) + one canonical Mac build script (muse, 2 h)

## Goal
Every lane builds its own runner from scratch: 9,457 generated files in unity batches of 32 plus the runtime, from the same canonical codegen. Brad (09-25) approved a shared compile cache so lanes only compile what they changed. Deliver ccache on the mini, a single build script every brief can call, and measured cold/warm/one-file times. Correctness: a cached runner must be guest-identical to an uncached one.

## Facts
- Recipe of record: `local/research/F5/REPORT.md` `## Exact commands` (the `cmake -S PS2Recomp -B build …` line: Homebrew LLVM clang, Release, `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`, paraLLEl `PS2X_GS_SHADOW_PARALLEL=ON` + `PS2X_PARALLEL_GS_SOURCE_DIR`, logs/taps off; DET builds flip `PS2X_ENABLE_DET_HASH_TAP=ON`; `PS2X_VU1_RECOMP_DIR` for the VU1 images). Runner unity build: `ps2xRuntime/CMakeLists.txt:8-9`, `:634`.
- Base: fork `ssx3` `a3efbfe` (pushed). VU1 images `~/dev/ssx3-work/vu1gen-ssx3` (F5 proved them byte-identical to its regen). paraLLEl-GS fork `ssx3` `19d93b2` (read-only use of `~/dev/ssx3-work/F2/parallel-gs` is fine; verify HEAD).
- Det gate: F5's `f5_boot.py --mode det` + `local/research/GB8/gb8_hashdiff.py` (`IDENTICAL` over ticks 1..2400).
- Disk: cap 200 GB (`local/tooling/disk_budget.sh`); the cache counts.

## Steps
1. `brew install ccache`. Config (`ccache --set-config`): `max_size=20G`, `base_dir=/Users/brad/dev`, `hash_dir=false`, `compiler_check=content`. Record `ccache -p` in the report. Add the cache dir to `disk_budget.sh`'s `paths`.
2. Write `local/tooling/build/mac_build.sh <fork-worktree> <build-dir> [--det] [--vu1 DIR] [--pgs DIR] [--target T…]`: the F5 recipe with `-DCMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache`, printing the configure line, `ccache -s` before/after, and wall time. Defaults = the recipe of record (canonical codegen, `vu1gen-ssx3`, the F2 paraLLEl dir). `--no-cache` turns the launcher off (for the control).
3. Measure on worktree `~/dev/ssx3-work/RS1/PS2Recomp` (detached at `a3efbfe`): (a) control, `--no-cache --det` into `b0`; (b) cold cache `--det` into `b1` (`ccache -C` first); (c) warm, `--det` into a *different* dir `b2` (proves path-independence); (d) one-file change: add a comment to one runtime `.cpp` (e.g. `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`), `--det` into `b3`, then revert. Table wall time + hit rate for each. Also a non-det build into `b4` (warm for the non-det flags after one cold pass is fine: report both).
4. Correctness: det boots (one mini slot each, FR1-R1, t2400, F5's B1 settings) of `b0` and `b2` runners → `gb8_hashdiff.py` IDENTICAL; runner SHAs listed (they may differ in path strings; say whether they do).
5. Add a short "Mac builds" section to `docs/orchestration.md`? **No**, workers never edit docs: put the proposed runbook text in the report and the orchestrator adds it.

## Rules
≤ 6 builds (each `--parallel 8`), ≤ 2 boots, one mini slot per boot. Never push; never commit in the fork; text only in git. Scratch `~/dev/ssx3-work/RS1/` ≤ 15 GB (delete `b*` dirs at the end, keep the two runners). First failure: stop, save the error, hand back.

## Deliverable
`local/research/RS1/REPORT.md` (config, times table, hit rates, det result, SHAs, proposed runbook text, gaps) + `local/tooling/build/mac_build.sh` + the `disk_budget.sh` edit; commit `[RS1] …` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
