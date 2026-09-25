# RS1 — shared compile cache (ccache) + canonical Mac build script

Worker: muse. Brief: `local/muse/prompts/RS1.md`.
Worktree `~/dev/ssx3-work/RS1/PS2Recomp`, detached at fork `ssx3`
`a3efbfe946631c44f113f20a94b3c64754d87701`, clean at close (0 porcelain lines).
First-failure rule never triggered. Never pushed; no fork commit.

## ccache config

`brew install ccache` (4.14). Non-default `ccache -p` lines, all in
`/Users/brad/Library/Preferences/ccache/ccache.conf`:

| Key | Value |
| --- | --- |
| `base_dir` | `/Users/brad/dev` |
| `compiler_check` | `content` |
| `hash_dir` | `false` |
| `max_size` | `20.0 GB` |

Cache dir is the default `/Users/brad/Library/Caches/ccache`, added to
`local/tooling/disk_budget.sh` `paths` (1-line edit). ccache 4.14 has no
`--print-config` flag (only fact worth noting; `ccache -p` shows the dir).

## Build times (mini M5 Pro, `--parallel 8`, 614 cacheable calls each)

Script: `local/tooling/build/mac_build.sh` (executable, `bash -n` clean).
F5 configure line + `-DCMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache` +
`-DPS2X_ENABLE_SCCACHE=OFF` (the in-tree sccache hook would otherwise
override the launcher if sccache is ever installed; absent today).
Defaults: canonical codegen (`register_functions.cpp` `8ea8ed43…`,
`sub_003FE828` `89953ba2…`, both match F5 pins), `vu1gen-ssx3` (7/7 SHAs
match F5 `vu1gen.sha`), F2 paraLLEl `19d93b2` (HEAD verified, clean).
Stats zeroed (`ccache -z`) before each cached build. B1 settings for boots:
`rs1_boot.py` = F5's driver with `WORK` → `~/dev/ssx3-work/RS1` and lease
label `RS1-` (scratch only, not committed).

| Build | Flags | Wall (configure+build) | ccache | Notes |
| --- | --- | --- | --- | --- |
| b0 control | `--no-cache --det` | 272 s | n/a | full compile, no launcher |
| b1 cold | `--det`, `ccache -C` + `-z` first | 266 s | 0 / 614 (0%) | = b0 within noise; caching costs nothing cold |
| b2 warm | `--det`, different dir | 78 s | 614 / 614 (100 % direct) | path-independence proven |
| b3 one-file | `--det`, 1 comment line prepended | 78 s | 613 / 614 (1 miss) | the changed unity batch only; reverted after |
| b4 non-det | first pass for these flags | 250 s | 250 / 614 (40.7 %) | flag-independent TUs (parallel-gs, tests) hit |
| b4b non-det | second dir, warm | 80 s | 614 / 614 (100 %) | 6th build; brief's "report both" warm pass |

Warm full-runner build: ~80 s (3.4× faster than 272 s cold). One-file lane
edit in a fresh dir: same ~80 s (link-dominated). Cache holds 0.2 GB after
all six builds. Script bug found and fixed: `"${EMPTY_ARR[@]}"` under
`set -u` aborts on macOS bash 3.2 — launcher flags are now appended
conditionally (comment in script).

## Correctness (det boots, FR1-R1, t2400, F5 B1 settings)

One mini slot each (slot 1, released after; all slots free at close).
`--vu1-stats --dump-ticks 1090,1800,2100`, paced, sound on.

| Boot | Runner | Wall | Last tick | Det-hash vs C0 |
| --- | --- | --- | --- | --- |
| C0 | b0 (uncached control) | 63.5 s | 2409 | base (2489 lines) |
| C2 | b2 (warm cache) | 63.0 s | 2402 | **IDENTICAL** ticks 1..2400, 0 missing (2483 lines) |

Runner SHAs (two reads each, all four match):

- b0 / `bin/runner-nocache`: `119389a74f857e56460ef448e23563d464528db9a819b249049693e563993c38`
- b2 / `bin/runner-cached`: `119389a74f857e56460ef448e23563d464528db9a819b249049693e563993c38`

The SHAs do **not** differ: the cached runner is byte-identical to the
uncached one, and both equal F5's `runner-det` SHA — the script reproduces
the F5 recipe bit-for-bit. (`cmp` implied by equal SHAs.) Non-det b4
runner carries 0 `det-hash:v1` strings, as expected.

## Proposed runbook text (for docs/orchestration.md; orchestrator adds)

```md
## Mac builds (RS1, 2026-09-25)

Build every Mac runner with `local/tooling/build/mac_build.sh
<fork-worktree> <build-dir> [--det]` (defaults: canonical codegen,
`vu1gen-ssx3`, F2 paraLLEl `19d93b2`; `--target` repeats, `--no-cache`
for controls). It uses the shared ccache (`base_dir=/Users/brad/dev`,
20 GB at `~/Library/Caches/ccache`, counted in `disk_budget.sh`):
~80 s warm vs ~270 s cold on the mini, 100 % direct hits in a fresh
dir, byte-identical runners. Det and non-det flag sets cache
independently (first non-det pass after det work is ~40 % hits).
`ccache -z` before a measured build; `ccache -s` deltas are the hit
rate. Never `ccache -C` on a shared-warm cache without asking the
orchestrator — it wipes every lane's entries.
```

## Budgets and gaps

- Builds: 6 / 6 (`--parallel 8` each). Boots: 2 / 2 (C0, C2; one slot
  each, `bound=target`, 0 FATAL, `gs_fatal=null`).
- Scratch `~/dev/ssx3-work/RS1/`: 351 MB at close (cap 15 GB). Kept:
  worktree, `bin/` (2 runners), `run/` (C0+C2), `b*.log`,
  `rs1_boot.py`. `b*` build dirs deleted.
- ccache: 0.2 GB / 20 GB. Disk: 138.4 → 141.0 / 200 GB.
- Text in git: this report + `mac_build.sh` + `disk_budget.sh` edit.
- Gaps:
  - G1. One run per build config; b0-vs-b1 "caching costs nothing"
    is a single-sample comparison (272 vs 266 s).
  - G2. Warm builds are link-dominated (~80 s incl. configure);
    link-time optimization (`PS2X_DEV_NO_THINLTO`) was not explored.
  - G3. No Android/ccache measurement — bytesize has no shared cache;
    brief was Mac-only.

## Exact commands

```sh
brew install ccache
ccache --set-config=max_size=20G; ccache --set-config=base_dir=/Users/brad/dev
ccache --set-config=hash_dir=false; ccache --set-config=compiler_check=content
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/RS1/PS2Recomp a3efbfe
S=local/tooling/build/mac_build.sh; W=~/dev/ssx3-work/RS1/PS2Recomp
bash $S $W ~/dev/ssx3-work/RS1/b0 --det --no-cache      # 272 s
ccache -C; ccache -z; bash $S $W ~/dev/ssx3-work/RS1/b1 --det   # 266 s, 0/614
ccache -z; bash $S $W ~/dev/ssx3-work/RS1/b2 --det       # 78 s, 614/614
# prepend 1 comment line to ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
ccache -z; bash $S $W ~/dev/ssx3-work/RS1/b3 --det       # 78 s, 613/614
git -C $W checkout -- ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
ccache -z; bash $S $W ~/dev/ssx3-work/RS1/b4            # 250 s, 250/614
ccache -z; bash $S $W ~/dev/ssx3-work/RS1/b4b           # 80 s, 614/614
cd ~/dev/ssx3-work/RS1
python3 rs1_boot.py --mode det --backend parallel --runner b0/ps2xRuntime/ps2EntryRunner --label C0 --stop-tick 2400 --vu1-stats --dump-ticks 1090,1800,2100
python3 rs1_boot.py --mode det --backend parallel --runner b2/ps2xRuntime/ps2EntryRunner --label C2 --stop-tick 2400 --vu1-stats --dump-ticks 1090,1800,2100
python3 ../ssx3/local/research/GB8/gb8_hashdiff.py --base run/C0 --cand run/C2  # IDENTICAL
cp b0/ps2xRuntime/ps2EntryRunner bin/runner-nocache; cp b2/ps2xRuntime/ps2EntryRunner bin/runner-cached
rm -rf b0 b1 b2 b3 b4 b4b
```
