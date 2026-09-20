# T6 — Build cache check (measurement)

Tables, no verdicts. Spec: `docs/research/review-2026-09-19-progress.md` Part 2 §12 row T6.

## T6-0. Setup

| Item | Value |
|---|---|
| Date / window | 2026-09-20 02:49–03:43 EDT |
| Host | Apple M4, 10 CPUs, macOS; ninja 1.13.2; `/opt/homebrew/opt/llvm/bin/clang(++)` |
| Fork | `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3` |
| Fork HEAD start | `935a4ebf6db16c4057c30f5dd5cdba23af0ff3b6` (T9 ladder_diff) |
| Fork HEAD end | `935a4ebf6db16c4057c30f5dd5cdba23af0ff3b6` (unmoved) |
| Fork worktree start/end | `M ps2xRuntime/src/runner/register_functions.cpp` (398,774+/5− vs HEAD), `?? tools/__pycache__/` (identical both ends; touches were mtime-only, content verified unchanged) |
| Build dir | `/tmp/t6-link/runtime` (fresh; peer dirs untouched) |
| Source | `-S $R` directly (no worktree: T6 carries no source changes) |
| Targets | `ps2x_tests ps2EntryRunner` (T1's line), `-j4` MAX, all builds |
| No-lease rule | No boots, no `adb`; no `git push` in ssx3; zero fork commits |

## T6-1. Flag set (T1 verbatim, verified)

Configure line (from T1 REPORT §T1-5, `-S`/`-B` repointed):

```
cmake -S $R -B /tmp/t6-link/runtime -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DPS2X_BUILD_ANALYZER=ON -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_STUDIO=OFF \
  -DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON -DPS2X_ENABLE_DEBUG_UI=ON -DPS2X_ENABLE_FFMPEG=ON \
  -DPS2X_ENABLE_IOP_RPC_TRACE=ON -DPS2X_ENABLE_RUNNER_PCH=ON -DPS2X_ENABLE_RUNNER_UNITY_BUILD=ON \
  -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_SCCACHE=ON -DPS2X_IOP_ENABLE_PLUGINS=OFF \
  -DPS2X_RUNNER_UNITY_BUILD_BATCH_SIZE=32
cmake --build /tmp/t6-link/runtime --target ps2x_tests ps2EntryRunner -j4
```

| Check | Result |
|---|---|
| `diff` of `^PS2X_` cache lines, t6 vs t1 | identical (see `flags-ps2x.txt`) |
| `CMAKE_BUILD_TYPE` / compilers / generator | Release / homebrew llvm clang / Ninja (same as T1) |
| `PS2X_ENABLE_SCCACHE=ON` effective? | No: cache records `PS2X_SCCACHE_PROGRAM-NOTFOUND`; no `sccache`/`ccache` binary on PATH |
| `PS2X_RUNNER_UNITY_BUILD_BATCH_SIZE` | 32 → 290 `unity_*` batches over 9,278 `runner/` files |
| IPO | `ps2xRuntime/cmake/ReleaseMode.cmake:38` sets `INTERPROCEDURAL_OPTIMIZATION_RELEASE` → link line carries `-flto=thin` (observed in `ninja -t commands`) |

## T6-2. Full configure + full build wall (uncontended)

| Step | Wall | Exit | Detail |
|---|---|---|---|
| Configure | 69 s | 0 | `Configuring done (67.6s)`, `Generating done (1.9s)` |
| Full build | 472 s (7.9 min) | 0 | 535 edges: 400 `Building CXX` + 13 `Linking` (remainder: glob re-check, PCH, `ar`) |
| Configure + build | 541 s | — | Pre-check quiet; no peer edges in window (p1/t1/t5 logs silent) |

Full-build edge ranking (from `.ninja_log`, paths included):

| Rank | Edge | Duration |
|---|---|---|
| 1 | `ps2xRuntime/ps2EntryRunner` link | 330.4 s (70% of build wall, serial tail) |
| 2 | slowest unity compile (`unity_73`) | 18.6 s |
| 3 | `unity_176` | 15.8 s |
| … | `unity_0` (batch containing 398k-line `register_functions.cpp`) | 6.9 s |
| — | `ps2xTest/ps2x_tests` link | 5.9 s |
| — | Σ compile-edge time / 4 jobs | 553 s / 4 ≈ 138 s parallel |

Link inputs/outputs: 290 unity `.o` = 313 MB → `ps2EntryRunner` 156 MB (`81bee6c5…`); `ps2x_tests` 5.2 MB (`dc0b64bc…`).

## T6-3. Incremental matrix (one run per cell, exact)

Touch files: (a) `ps2xRuntime/src/lib/ps2_runtime.cpp`, (b) `ps2xRuntime/include/ps2_log.h` (9,293 includers under `ps2xRuntime/`+`ps2xTest/`), (c) `ps2xTest/src/ps2_memory_tests.cpp`, (d) nothing. Per-step timestamps via `NINJA_STATUS='[%f/%t %e] '`; durations cross-checked against `.ninja_log`.

| Cell | Wall | Exit | Rebuilt (from build log) | Contention |
|---|---|---|---|---|
| (a) hot `.cpp` | 315 s (5.25 min) | 0 | 1 compile + 1 `ar` + tests link + runner link (5 edges) | none |
| (b) wide header, clean rerun | 658 s (11.0 min) | 0 | PCH + 338 compiles + 3 `ar` + 2 links (345 edges) | none (0 peer edges in window) |
| (b) wide header, first run | 844 s (14.1 min) | 0 | same 345-edge set | CONTENDED (peer p1-link 329 edges 03:11:11–03:21:21 inside 03:08:28–03:22:32) |
| (c) test `.cpp` | 8 s | 0 | 1 compile + 1 `ar` + tests link (4 edges; no runner relink) | none |
| (d) no-op floor | 0 s (sub-second) | 0 | `ninja: no work to do` | none |

3-minute gate (180 s): (a) 315 s — over; (b) 658 s clean — over; (c) 8 s — under; (d) — under.

## T6-4. Dominance table (which step owns the incremental wall)

Cell (a), 315 s wall (`cell-a-build.log` + `ninja-log.txt` lines 538–542):

| Phase | Duration | Share |
|---|---|---|
| compile `ps2_runtime.cpp.o` | 1.1 s | 0.4% |
| `ar libps2_runtime.a` | 0.1 s | 0.0% |
| link `ps2x_tests` | 9.1 s | 2.9% |
| link `ps2EntryRunner` (`-flto=thin`, 313 MB in) | 312.8 s | 99.3% |

Cell (b) clean, 658 s wall (lines 892–1236):

| Phase | Duration | Share |
|---|---|---|
| PCH rebuild (`cmake_pch.hxx.pch`) | 1.2 s | 0.2% |
| 338 compiles (Σ edge 1,018 s ÷ 4) | ~250 s parallel | ~38% |
| slowest batch `unity_73` / `unity_0` (giant-TU batch) | 49.2 s / 14.2 s | (inside parallel span) |
| `ar` × 3 | ≤0.3 s | 0.0% |
| link `ps2x_tests` | 12.0 s | 1.8% |
| link `ps2EntryRunner` (`-flto=thin`) | 396.7 s | 60.3% |

Runner-link samples across the session:

| Sample | Duration | Window state |
|---|---|---|
| full build | 330.4 s | uncontended |
| cell (a) | 312.8 s | uncontended |
| cell (b) clean | 396.7 s | uncontended |
| cell (b) first | 541.3 s | contended (peer −j4 overlap) |

Slowest-compile samples (`unity_73`): 18.6 s (full) / 63.2 s (contended) / 49.2 s (clean) — spread unattributed (gap row).

## T6-5. Task 2 — fix analysis (no fork changes)

Gate: fork changes ONLY if incremental >3 min AND the fix is contained (ccache enablement and/or generated-output split).

| Row | Content |
|---|---|
| Bite condition | Met: (a) 315 s, (b) 658 s clean both exceed 180 s |
| Miss location | Link, not recompile: 312.8/315 s (99%) in (a); 396.7/658 s (60%) in (b); ThinLTO (`-flto=thin`) over 313 MB unity objects |
| ccache applicability (brief: "if the miss is recompile") | Miss is not recompile: compile is 1.1 s of 315 s in (a). ccache caches compiles only; cannot move (a) or (b) under 180 s. Not implemented. |
| Generated-output split applicability (brief: "if the miss is one giant TU") | Miss is not one giant TU: the 398k-line `register_functions.cpp` sits in `unity_0`, compiling in 6.9–14.2 s; output is already 9,278 files in 290 batches. Splitting cannot shrink the 313 MB link input. Not implemented. |
| Fork diff | Zero (verified: HEAD `935a4eb` both ends, worktree state identical) |
| Suite after fix | N/A — no fix, no Task-2 build; suite not run this brief |
| Before/after matrix | N/A — nothing changed to re-measure |

## T6-6. Contention + waits record

Canonical log: `/Volumes/Extreme SSD/ps2recomp-spike/P1/run/t6-waits.log` (copied here as `t6-waits.log`).

| Window | Pre-check | What happened |
|---|---|---|
| configure 02:49, full build 02:50–02:58 | quiet (ps + literal `pgrep -f`, exit 1) | no contention |
| cells (d)(a)(c) 03:01–03:08 | quiet each | no contention |
| cell (b) 03:08:28–03:22:32 | quiet at start | peer p1-link build (329 edges: 290 unity + 39) ran 03:11:11–03:21:21 inside my window; sample kept as contended |
| 03:27–03:31 | peer runner link (PID 33495) still running | WAITED ~4 min per etiquette (logged), reran (b) clean at 03:31 |
| cell (b) clean 03:31:16–03:42:14 | quiet | 0 peer edges (p1 last write 03:28:00); clean |

Method notes: macOS `pgrep -f` prints bare PIDs and self-matches the invoking shell wrapper (observed PID 16663); every check paired it with a self-excluding `ps aux | grep -E '[c]make…'` read. `ninja -d explain -n` dry-runs never enumerated the rebuild set because `CONFIGURE_DEPENDS` glob re-check forces a cmake re-run first (222-byte output every cell); the "what rebuilt" column comes from the `NINJA_STATUS`-timestamped build logs instead. Medians of 1 run per cell per the brief.

## T6-7. Gap rows

| # | Gap |
|---|---|
| 1 | Runner-link spread 313–397 s across three uncontended samples is unattributed (no CPU temp/frequency/load logging; no `ld` phase timing) |
| 2 | `unity_73` compile spread 18.6–49.2 s uncontended is unattributed (same cause candidates as #1) |
| 3 | No ccache-installed measurement exists (neither `ccache` nor `sccache` on PATH; install + fork wiring deliberately not attempted — see §T6-5) |
| 4 | No ThinLTO-off / dev-build-config variant measured (outside the brief's allowed fix class) |
| 5 | Single run per cell (brief allows it); no variance estimate within a cell |
| 6 | Suite not run (no fork change; Task-2 suite gate not triggered) |

## T6-8. Evidence files (this dir, standalone)

`REPORT.md` (this file), `flags-ps2x.txt`, `configure-tail.txt`, `full-build.log`, `cell-a-build.log`, `cell-b-contended-build.log`, `cell-b-clean-build.log`, `cell-c-build.log`, `cell-d-build.log`, `ninja-log.txt` (1,235 edges, paths included), `t6-waits.log` (copy of canonical). Build tree retained at `/tmp/t6-link/` (not committed).
