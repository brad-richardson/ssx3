# GB6 — fold opt-in paraLLEl backend onto fork `ssx3`

## Pins and cherry-picks

| Item | Result | Receipt |
| --- | --- | --- |
| Remote fork `ssx3` | `1aaed05256bf53881824a9edd96a7cd5b7e8bbcc` | `git ls-remote fork refs/heads/ssx3`; local `fork/ssx3` matches |
| Canonical E54D codegen | `/Users/brad/dev/ssx3-work/codegen-ssx3`; `register_functions.cpp` SHA-256 `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` on two reads, matching E54D report | Two `shasum -a 256` reads |
| Source branch and six commits | `gb4-parallel` at `f796669`, clean. Selected `50d03a8`, `55f8253`, `9517210`, `8f49a9c`, `520bd61`, `c5913e4` in that order; probe commits `b7d3227`, `f796669` omitted | `git log` and `git status` in GB4 worktree |
| Conflict resolution | Six clean cherry-picks; auto-merges only, no manual conflict or source edit | `git cherry-pick` output |
| Local fold branch | `gb6-fold` at `293fd81`, after new commits `52d6d5e`, `7291fde`, `307aaa7`, `2d393d2`, `8914d03`, `293fd81` | `git log -6` in GB6 worktree |

| Source | New GB6 commit | Cherry-pick result |
| --- | --- | --- |
| `50d03a8` | `52d6d5e` | Clean auto-merge |
| `55f8253` | `7291fde` | Clean |
| `9517210` | `307aaa7` | Clean |
| `8f49a9c` | `2d393d2` | Clean auto-merge |
| `520bd61` | `8914d03` | Clean |
| `c5913e4` | `293fd81` | Clean |

## Source gates

| Gate | Result | Receipt |
| --- | --- | --- |
| Default OFF, default CPU, OFF fallback | Source pass: `PS2X_GS_SHADOW_PARALLEL` CMake option defaults OFF; `requested()` only returns true for explicit `PS2X_GS_BACKEND=parallel`; unavailable build logs that it stays on CPU | `ps2xRuntime/CMakeLists.txt:489`, `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:404-412`, `ps2xRuntime/src/lib/ps2_runtime.cpp:984-1004` |
| Six-change diff and runner-dir check | 16 paths, all touched by selected commits; 1,732 insertions, 11 deletions; `git diff --check` clean; `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty | `git diff --stat 1aaed05 HEAD`; `git diff --name-only`; runner-dir check |
| Generated guest code/binaries absent from Git | One pre-existing runner-dir tracked path; no runner, binary, ELF or ISO path in fold diff | `git ls-files ps2xRuntime/src/runner`; `git diff --name-only 1aaed05 HEAD` |

## Build, suites, replay, live boot

| Gate | Result | Receipt |
| --- | --- | --- |
| Configure/build and taps | Configure 1 and build 1 passed: Release/Ninja, shadow ON, E54D codegen, G43 paraLLEl source, runtime/aggressive logs and diagnostic taps OFF. Built `ps2x_tests ps2EntryRunner` with `nice -n 10`, `-j8`; no repair attempt. | `~/dev/ssx3-work/GB6/run/{configure-1.log,build-1.log}`, `build/CMakeCache.txt` |
| Full suite and optional taps-ON suite | `suite-on-1.log` and `suite-on-2.log` are **two runs of the same taps-OFF, parallel-compiled build**, each **578/578** from the fork root, zero failures. Replay suites on that same build also passed **578/578** each. The optional **taps-ON** configuration/build/suite was **not run** after the failed live-capture gate. The `suite-on` filenames refer to the parallel option, not diagnostic taps. | `build/CMakeCache.txt` (`PS2X_ENABLE_DIAG_TAPS=OFF`), `run/suite-on-{1,2}.log`, `run/replay-{cpu,parallel}.log` |
| CPU/paraLLEl replay, counters and GB4 hashes | Both used the same GB4 capture and true-path sidecar. CPU replay: direct, 1,982,063 packets, 60 samples, output file **byte-identical** to GB4 Part 6 `replay-vq-p6-cpu.hashes` (60/60 lines). GPU replay: queue, `init_ok=1`, `init_failed=0`, 1,982,063 packets, 60 presents, `null_scanouts=0`, `unsupported_clears=0`, `unsupported_vram_io=0`. Post-use two-read SHA verification matched for both read-only inputs; see timing gap below. | `run/replay-{cpu,parallel}.{log,hashes}`, `cmp -s` exit 0, `run/replay-input-sha-read{1,2}.txt`; inputs under `~/dev/ssx3-work/GB4/run/` were only read |
| Live I26-FAST boot, frames and SHA pairs | **Failed boot frame gate; stopped.** Escalated boot used mini slot 1, parallel backend and dev-only movie bypass. Runner PID 19360 exited 0 after wrapper terminated it by PID at `bound=log_cap`; elapsed 78.779 s, last rate tick 2236 (≥2050), lease released. Title tick 300, menu tick 700 and race HUD tick 1810 were captured; second race frame absent. Two reads of ISO, ELF, runner and codegen register file matched. | `run/parallel-one/{result.json,boot.log,title-tick300.png,menu-tick700.png,race_early-tick1810.png}`, `run/boot-driver.log`, `run/input-sha-read{1,2}.txt`; no second boot |
| Byte and run budgets | GB6 tree 1.9 GB (<8 GiB); global internal usage 111.1/200 GB after boot. Configure/build 1/2, replay 2/2 (no retry), boot 1/1. | `du -sh GB6`; `local/tooling/disk_budget.sh` |

### Live boot failure and viewed frames

The live script set `PS2X_FRAME_DUMP_ONCE_TICKS=300,700,1810,2100`. The runner's `ps2_runtime.cpp:482-494` stores **exactly three** ticks in `std::array<uint64_t, 3>` and parses with `std::sscanf(env, "%llu,%llu,%llu", &a, &b, &c)`. It therefore accepted only 300, 700 and 1810; the fourth value 2100 was ignored. The three produced `[frame:dump]` lines are at those first three ticks. The wrapper required four snapshots, so it could not reach its target condition. **This is the exact cause of the missing second race frame.**

PKLOG reached **61,555,935 bytes (~61.6 MB; 58.7 MiB)**, consuming most of the 64 MiB combined log cap. The boot log was 6,173,654 bytes; together they reached 67,729,589 bytes, 620,725 bytes over 64 MiB at the wrapper's one-second poll, which triggered `bound=log_cap`. The closed PKLOG was compressed to the single `ps2_pklog.txt.zst` copy, 9.44 MiB; `zstd -t` passed. The wrapper recorded a clean runner exit (`rc=0`) and both mini lease slots were subsequently free. This run is diagnostic only, with no speed claim.

I viewed all three saved frames. Title tick 300 shows the SSX 3 logo and copyright text with damaged strokes. Menu tick 700 shows Main Menu and legible selections, but the lower `Select`, `Previous` and `Options` labels retain the known broken/blocky strokes. Race tick 1810 shows the HUD at `00:00:01`, snow and a rider/track area, with large dark terrain regions and degraded small text; only one race frame exists, so rider/terrain/HUD **advance between race frames is not established**. No visual parity is claimed.

| Artifact | SHA-256 |
| --- | --- |
| Stock ISO (two matching reads) | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| Stock ELF (two matching reads) | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| GB6 runner (two matching reads) | `047f29e744de32187a3cbf184ca520068829bbc2dd28951d9064d0b803f5aac1` |
| Canonical register file (two matching reads) | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Title frame, tick 300 | `9680fd7460f3cc4e7f9655ce016de9144ae209a0a6f2eec1eecd7f1fea5422d2` |
| Menu frame, tick 700 | `0db24270b8535f931bb0c594862aef725ad2035c51920edc28f7922f81fa5155` |
| Race frame, tick 1810 | `0d2c96bac725a13743a9042fe64f61dc610b6c611fd76e7c4d591388b3ce37ab` |
| Compressed PKLOG | `9f03ba8e79d5ee0a102945bd434c731dfbb7af9ab9168ba7725486b2b9bfe5f6` |
| GB4 capture (two matching reads after replay) | `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` |
| GB4 true-path sidecar (two matching reads after replay) | `c7e24da3f8f9c14c787bc9c70ecb584aab665e480e902bb33eb238d4c63b95aa` |

## Exact commands and gaps

From `~/dev/PS2Recomp`: `git ls-remote fork refs/heads/ssx3`, then `git worktree add -b gb6-fold ~/dev/ssx3-work/GB6/PS2Recomp 1aaed05256bf53881824a9edd96a7cd5b7e8bbcc` (git write escalated). From the GB6 worktree: `git cherry-pick 50d03a8`, then `git cherry-pick 55f8253 9517210 8f49a9c 520bd61 c5913e4` (escalated). `git diff --stat 1aaed05 HEAD`, `git diff --check 1aaed05 HEAD`, and `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` produced the source receipts above.

From `~/dev/ssx3-work/GB6`: `nice -n 10 cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/G43/parallel-gs -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF > run/configure-1.log 2>&1`; `nice -n 10 cmake --build build --target ps2x_tests ps2EntryRunner -j8 > run/build-1.log 2>&1`. The two normal suite invocations were `../build/ps2xTest/ps2x_tests` from the fork root, redirected to `../run/suite-on-{1,2}.log`.

The two replay invocations from the fork root used `PS2X_GS_REPLAY_CAPTURE=/Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin`, `PS2X_GS_REPLAY_PATH_FILE=/Users/brad/dev/ssx3-work/GB4/run/gb4p4.paths.txt`, `PS2X_GS_REPLAY_STEP=50` and `PS2X_GS_REPLAY_OUT=../run/replay-{cpu,parallel}.hashes` with `../build/ps2xTest/ps2x_tests`. The GPU invocation additionally set `PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib` and ran escalated. Both redirected to their `../run/replay-{cpu,parallel}.log`.

The one escalated boot command from `~/dev/ssx3-work/GB6/run` was `python3 gb6_boot.py --label parallel-one --wall 500 --target 2200 --capture > boot-driver.log 2>&1`. `gb6_boot.py` is a GB6-local copy of the E54D bounded driver, retargeted to the GB6 runner/run directory, parallel backend, I26-FAST route and four requested snapshots. Its four-value snapshot setting caused the documented failure. The wrapper includes progress, wall, frame-size and combined-log caps, claims/releases one mini slot, and terminates only its own runner PID.

Gaps: the live two-race-frame requirement failed; the optional taps-ON suite was not run. The GB4 capture and sidecar received two matching SHA reads **after** replay, not before use as the standing input rule requires; their current hashes match the GB4 capture pin, but this does not retroactively satisfy the timing requirement. Only one configure/build occurred, and no further boot, repair, graphics tuning or push was attempted. The fork branch has exactly the six new cherry-pick commits and no additional `[GB6]` source commit because no conflict resolution or source edit was made. The orchestrator will decide the fold gate.
