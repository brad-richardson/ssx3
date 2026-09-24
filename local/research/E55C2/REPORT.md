# E55C2 — bounded VBlank XXH64 repeatability tap

Worker: Codex. Brief: `local/muse/prompts/E55C2.md`. This is evidence for the orchestrator, not a gate verdict. No fork push.

## Source and build pins

| Item | Observation | Receipt |
| --- | --- | --- |
| Fork | `fork/ssx3` pin `779e8048cd584586f6896fde0f049fa758f287db`; isolated `~/dev/ssx3-work/E55C2/PS2Recomp` branch `e55-vblank-hash`. Source/test commit `ddaee780288adb076ce40050d87969b20bc4bb05`, trailer `Orchestrated-By: Codex`. | Fork git log/status |
| XXH64 source | Official xxHash tag `v0.8.4`, `https://raw.githubusercontent.com/Cyan4973/xxHash/v0.8.4/xxhash.h`; vendored unmodified header SHA-256 `3dc8d161e867a62d3417f7885b55fdaded8b7b497e2f165d05c94f4fe24f2ca4`, with BSD-2-Clause notice. `XXH_NO_XXH32`, `XXH_NO_XXH3`, and `XXH_INLINE_ALL` apply only in the ON scheduler translation unit. | `ps2xRuntime/include/runtime/third_party/xxhash.h`, `EeScheduler.cpp` |
| Mechanism | `PS2X_ENABLE_DET_HASH_TAP` defaults OFF. ON parses `PS2X_DET_HASH_EVERY` once per scheduler instance; unset/empty/decimal zero disable, exact decimal positive values select `tick % N == 0`, invalid/overflow emit one bounded error then disable. At VBlankStart after guest flag/tick writes and callback/IRQ queueing, it streams RDRAM (32 MiB), scratchpad, VU1 data and code (16 KiB each), then eight explicit little-endian VU1 start-count bytes. Four region XXH64s and the combined XXH64 print with tick, EE cycle and numeric count. Null/unbound region disables output. A process-wide 4096-line budget reserves its last line for the stop notice; no line exceeds 256 bytes. | `EeScheduler.cpp`, scheduler header, runtime CMake |
| VU1 count | Incremented only for `VU1Interpreter::execute()` on the VU1 instance; `resume()`/MSCNT and VU0 excluded. Reset in the interpreter `reset()`. Count accessor/field/increment compile only in ON builds. The VIF1 MSCAL and EE CMSAR1 callers both enter `execute()`; MSCNT enters `resume()`. | `ps2_vu1_core.cpp`, `ps2_vu1.h`; E55C1 source map |
| OFF binary check | The OFF runner had no `[det-hash` or `PS2X_DET_HASH_EVERY` strings; source compile guards exclude the 32 MiB scan call and VU1 count increment. The OFF test sets the env and checks no hash output. | `strings .../build/ps2xRuntime/ps2EntryRunner`, OFF suite |
| Runner guard | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty after the commit. Fork worktree clean; no push. | Fork git diff/status |

**Memory-size boundary:** `makeDetHashSnapshot()` scans `PS2_RAM_SIZE`. `PS2Memory::initialize(size_t)` can allocate a nondefault RDRAM size and exposes no size accessor. Production initializes the default 32 MiB, and the focused test uses that default. The null/bound-pointer guard does **not** prove a nondefault-size allocation safe. No source change was made for that separate boundary.

## Build and focused tests

| Gate | Result | Receipt |
| --- | --- | --- |
| Mac Release/Ninja taps OFF | One configure/build, full suite from fork worktree root: **585/585**, zero failed. | `~/dev/ssx3-work/E55C2/{cmake-off,build-off,suite-off}.log` |
| Mac Release/Ninja taps ON, first suite | One configure/build, full suite: **683/684**, one failed assertion: `reordered regions differ`. The test restored every one-byte perturbation before reordering, so all regions were zero-filled. Swapping those regions left the concatenated bytes unchanged. Production hashing was not implicated by that assertion. | `suite-on.log`; `suite-on-failure.txt` |
| Authorized named test-only repair | Seeded distinct bytes in the four regions, recomputed the expected base hash, rebuilt only `ps2x_tests`, and reran the full ON suite: **684/684**, zero failed. No production source changed in this repair. | `build-on-repair.log`, `suite-on-repair.log`; fork test diff |
| Focused coverage | Official seed-zero empty and `hello` vectors; incremental versus one-shot; one-byte perturbation of each region; ordered stream and explicit count bytes; VU1 execute/resume/VU0/reset; strict env parser including overflow; OFF env behavior; actual VBlank event after guest writes and callback/IRQ queueing; 256-byte line and 4096-line cap. The scheduler fixture initializes actual `PS2Memory`. | `ps2_runtime_kernel_tests.cpp`, `ps2_vu1_tests.cpp`; suites |

`build.sh off` and `build.sh on` ran from the fork worktree. Both configured Release/Ninja with `/opt/homebrew/opt/llvm/bin/clang{,++}`, canonical external `PS2X_GAME_CODEGEN_DIR`, local E50 FetchContent source directories, `PS2X_BUILD_TEST=ON`, studio/log options OFF, and `PS2X_ENABLE_DIAG_TAPS`/`PS2X_ENABLE_DET_HASH_TAP` both OFF or both ON. The OFF build targeted `ps2x_tests ps2EntryRunner`; the ON build targeted the same. The one repair command was `nice -n 10 cmake --build ~/dev/ssx3-work/E55C2/build-taps --parallel 8 --target ps2x_tests`. Both full suites were invoked from `~/dev/ssx3-work/E55C2/PS2Recomp`, the fork root. No generated guest code was regenerated; canonical codegen held 9,457 files.

## Two-read preboot SHA-256 pairs

Each path was read twice before boots; the two ordered four-line blocks match exactly in `input-sha.txt`.

| Input | SHA-256 on both reads |
| --- | --- |
| ISO `E32-inputs/SSX 3 (USA).iso` | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF `E32-inputs/cd/SLUS_207.72` | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| ON `ps2EntryRunner` | `cd2c611c54dfa40a95923ca4d6ad4cbdfa6c19fb2c42bde2e44f546f36208a5b` |
| Canonical `register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |

The ISO, ELF and register SHA values match the brief's pins. The fork runner-dir guard was empty before boots.

## Bounded three-boot observation

All runs used the same ON runner, ELF, ISO, external codegen, `PS2X_DETERMINISTIC=1`, dev-only `PS2X_SKIP_MOVIE=1`, `PS2X_DET_HASH_EVERY=1`, I26-FAST vsync pad script, and no frame dump. Each had its own cwd and `PS2X_MC_ROOT` under that cwd. Both `mc0` and `mc1` were empty before every run; their canonical initial manifest SHA-256 was the same `f94015964371517ad24d36c71ea0c9bdc6fb4a23f3c46d7cc0def479feccb9ce`. `hidutil list` showed no gamepad/controller/joystick name match before boots; the harness did not inject physical pad input. The loaded run alone started four CPU-bound `yes >/dev/null` children, PIDs 70368–70371; an escalated `ps -p` check after the run found none of them or runner PID 70372. Each boot claimed and released mini lease slot 1; both slots were free afterward.

| Run | Host load | Bound, wall time | Complete hash rows / last tick | Log bytes | Receipt |
| --- | --- | --- | --- | --- | --- |
| idle-1 | no load children | target, 122.977 s | 2053 / 2053 | 373,675 | `result-idle-1.json`, external `run/idle-1/boot.log` |
| idle-2 | no load children | target, 121.446 s | 2053 / 2053 | 373,675 | `result-idle-2.json`, external `run/idle-2/boot.log` |
| loaded | four recorded `yes` children | target, 127.700 s | 2052 / 2052 | 373,494 | `result-loaded.json`, external `run/loaded/boot.log` |

All three traces start at tick 1, are consecutive and schema-valid, have no hash error or cap marker, and have maximum hash-line length 180 bytes. `runner_rc=-15` in each result records deliberate SIGTERM after the tick target, not a crash. The progress cap was 120 s without a new tick, the wall cap 500 s (hard below 600 s), and the boot-log cap 4 MiB. No run met those caps. The runner was launched from each run's own cwd, and only its recorded PID was terminated. These are diagnostic runs; the elapsed times are not speed numbers.

| Pair | Common complete tick prefix | First differing tick/field | Last common tick |
| --- | ---: | --- | ---: |
| idle-1 / idle-2 | 1–2053 | none | 2053 |
| idle-1 / loaded | 1–2052 | none | 2052 |
| idle-2 / loaded | 1–2052 | none | 2052 |

The comparison checked `(tick, eeCycle, rdram, scratch, vu1Data, vu1Code, combined, count)` for every complete row. It did not classify a shorter trace as a pass beyond its common prefix. Receipt: `comparison.txt`.

## Budgets, commands and gaps

One OFF configure/build and one ON configure/build were used, followed by the authorized one ON test-only rebuild; three boots, no rerun. `~/dev/ssx3-work/E55C2` was 2.3 GiB against the 5 GiB lane cap. `local/tooling/disk_budget.sh` measured 113.5 GB before builds and 115.7 GB after boots, below the 200 GB global cap. Each boot log was below 4 MiB; the three logs total 1,120,844 bytes. Committed text receipts are below 16 MiB. No frames or new guest code were written.

Exact gate invocations: `/bin/zsh ~/dev/ssx3-work/E55C2/build.sh off`; `~/dev/ssx3-work/E55C2/build/ps2xTest/ps2x_tests > suite-off.log 2>&1`; `/bin/zsh ~/dev/ssx3-work/E55C2/build.sh on`; `~/dev/ssx3-work/E55C2/build-taps/ps2xTest/ps2x_tests > suite-on.log 2>&1`; the single repair build command above; the same ON suite redirected to `suite-on-repair.log`; then `python3 ~/dev/ssx3-work/E55C2/e55c2_boot.py --label idle-1`, `--label idle-2`, and `--label loaded`, each redirected to its named `boot-*.txt`. The boot script holds the exact environment, route, lease, PID, progress, wall and log-cap logic. `input-sha.txt` holds the literal two-read `shasum -a 256` paths and values.

Gaps: This is a Mac mini live-run observation through tick 2052 across all three runs. It does not prove later ticks, another platform, or all possible host schedules. Live pad merge, card state on other inputs, and `ExternalWake` timing remain possible divergence sources. The nondefault RDRAM allocation boundary above is not covered by this tap. The null pointer fail-closed path was source-reviewed but not exercised by a dedicated focused test. No speed measurement was made.
