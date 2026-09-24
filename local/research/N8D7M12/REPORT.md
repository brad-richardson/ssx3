# N8D7M12 Part 1 — shared GS replay core, desktop parity

**State: COMPLETE, outcome A. One candidate implementation, one validation
pass (1 configure + 1 build + 1 suite + 1 exact-stream Mac replay, one P-lane
slot). No Android code/build, no device action, no stream copy, no push, no
upstream contact. No wall-time speed is quoted.**

Brief: `local/muse/prompts/N8D7M12P1.md`. Goal: N8D7M11 §3's shared replay
core only, so the desktop test and a future Android app branch call the same
parser without a test harness in the runtime.

## 1. Pins

| Item | Value |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7M12/PS2Recomp`, branch `n8d7m12-replay-core` |
| Fork base / HEAD | `a8cfefa` / `24801bc` (`[N8D7M12]`, `Orchestrated-By: opencode`, no push) |
| Scratch | `~/dev/ssx3-work/N8D7M12/` (build 1.4 GB, ≤5 GB cap) |
| Reference stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, 1,100,696,462 B, SHA `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` (two matching reads before use) |
| N8D7M6 Mac baseline | `~/dev/ssx3-work/N8D7M6/mac-parallel.log` (N8D7M5 binary `d06ff1aa`), `comparison.json` broad 300/448 |
| New binary | `~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests`, SHA `2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5` (two matching reads) |
| Parallel source / codegen | `~/dev/ssx3-work/N8D7F/parallel-gs`, `~/dev/ssx3-work/codegen-ssx3` (N8D7M5 cache values) |
| Toolchain idle | no `clang`/`ninja` before build; disk 148.4 GB of 200 GB cap before and after |

## 2. Implementation (N8D7M11 §3)

| Piece | File |
| --- | --- |
| Shared core: `ps2x_gs_replay_read_event` + `ps2x_gs_replay_run()` returning `Ps2xGsReplayResult` (skip/open/header/rtz/path/words/backend/parse/trace/out/expect + counts + sampled rows); all `GB4_*` console formats unchanged | `ps2xRuntime/src/lib/gs/gs_replay_core.cpp` (new) + `ps2xRuntime/include/runtime/gs/gs_replay_core.h` (new) |
| One `target_sources` hunk + `PS2X_GS_REPLAY_WORD_WATCH=1` on that TU only when `PS2X_BUILD_TEST=ON` | `ps2xRuntime/CMakeLists.txt` (+11) |
| Thin wrapper: harness registration, tmpfile framing check via the core reader, unset-capture skip, result→assert mapping | `ps2xTest/src/ps2_gs_replay_tests.cpp` (699→~110 lines) |

Record decoding/dispatch, ordered path+priv+transfer+marker processing,
Present descriptor, tick2050 selected capture, 4 MiB snapshot and 448-tile
census flow through the same call sequence (backend code untouched). No
`main.cpp` change; no new third-party deps; no `MiniTest` string in
`ps2xRuntime` sources (`no_harness_in_runtime` PASS).

### Compile-time word-watch guard (source-review response)

All N8D7M5 code (`PS2X_GS_REPLAY_WORDS` reader, `watchAddrs`/`watchValid`,
`snapshotWords`/`emitWordLine`, `ps2xN8D7M5*` calls, `[n8d7m5]` emission) sits
in 8 balanced `#ifdef PS2X_GS_REPLAY_WORD_WATCH` regions (148 guarded lines,
`watch_verbatim` PASS: every line also present at `a8cfefa` except the two
assert→result conversion lines). The macro is TU-scoped under
`if(PS2X_BUILD_TEST)`; Android configures `OFF` (N8D7M10 §2), so the
Android-target core has no watch code, reader, or caller. Proofs:
`guard_on_flag` (TU compile command carries the flag — this build),
`guard_off_absent`/`guard_off_no_emit` (flag-free preprocess of the TU:
zero reader/snapshot/emit lines), `guard_off_decls_only` (only 2 inert
declaration lines from `gs_cpu_backend.h`, needed for `GSCpuBackend`).
Remainder (disclosed): default-off counter *definitions* in
`gs_cpu_backend.cpp` stay compiled but uncalled without the guard. Desktop
diagnostics preserved verbatim behind the flag.

## 3. Validation (A)

| Check | Result |
| --- | --- |
| Runner-dir diff vs `14b1e5cb` empty (committed + working tree) | PASS |
| Suite from fork cwd, exit 0 | 585/585/0 PASS |
| Exact-stream parallel replay, exit 0, one P-lane slot (claimed 1, released) | PASS, log 4,814,880 B (≤16 MiB), no `GB4_REPLAY_PARSE_ERROR` |
| Parser counts vs baseline | packets 862958, priv 11499, transfers 25445, markers 2050, readbacks/clears 0, samples 41 — all equal |
| Marker2050 | markers=2050, last sampled row tick=2050 |
| Selected 11-field descriptor | `2050 112 8 1 0 0 0 2 4194303 1 0` byte-equal |
| Byte hashes | bytes=5177344, vram `99053d8f…`, input==circuit `24bff99b…` equal |
| 448-tile vectors input/circuit/stage/oracle | occupied 64399, active 300, packed `1d847d50…bd988b`, full word-vectors equal |
| Oracle controls + `oracle_input_equal` | 8/8 literals + 448/448 equal |
| Named presents | `GB4_FRAME present=d19b96fe`, `GB4_REPLAY tick=2050 … present=d19b96fe` equal |
| `parallel.hashes` / `vq-002050.ppm` | byte-equal (2686 B / SHA `9490484c…`) |
| `check.py` | verdict **A** (`check-result.json`), 40/40 PASS |

No diagnostic wall time is quoted as speed.

## 4. Exact commands (repo root unless noted; worktree `~/dev/ssx3-work/N8D7M12/PS2Recomp`)

```sh
cmake -S <worktree> -B ~/dev/ssx3-work/N8D7M12/build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DPS2X_BUILD_TEST=ON \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/N8D7F/parallel-gs \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3   # rc=0
ninja ps2x_tests            # workdir=build; rc=0, 325 targets, one known ld warning
<build>/ps2xTest/ps2x_tests # workdir=worktree; rc=0, 585/585 (suite.log)
python3 local/tooling/p_lane_lease.py claim 1 n8d7m12
PS2X_GS_REPLAY_CAPTURE=.../N8D7M6/n8d7m6.gs PS2X_GS_REPLAY_BACKEND=parallel \
PS2X_N8D7F_SELECTED_CAPTURE=1 PS2X_N8D7L_ORACLE=1 PS2X_N8D5_TILE_CAPTURE=1 \
PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=2050 \
PS2X_GS_REPLAY_PPM_DIR=.../N8D7M12/mac-parallel \
PS2X_GS_REPLAY_OUT=.../mac-parallel/parallel.hashes \
GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib \
  <build>/ps2xTest/ps2x_tests   # workdir=worktree; rc=0; slot released after
python3 local/research/N8D7M12/check.py  # verdict A
```

## 5. Deviations (disclosed, no budget impact)

- First suite invocation used a wrong relative binary path (`./build/...`
  under the worktree) and executed nothing (rc=127); reran correctly. Counts
  as the one suite.
- Lease release after replay first ran with the fork worktree as cwd and
  missed the script path; released immediately after from the repo root
  (rc=0). Slot was held ~1 min extra; no other claimant.
- Build ran after the E55D11 hold was released; configure predates the hold
  and ninja re-configured for the guard edit automatically (flag confirmed in
  the TU compile command).

## 6. Receipts

- ssx3 (this dir): `REPORT.md`, `check.py`, `check-result.json`,
  `result.json`, `fork-n8d7m12.patch` — `[N8D7M12] Part 1` commit, no push.
- Scratch `~/dev/ssx3-work/N8D7M12/`: `build/`, `build.log`,
  `configure.log`, `suite.log`, `mac-parallel.log`, `mac-parallel/`,
  `guard-off.i`, `guard-off-cmd.txt`.
- Fork: `[N8D7M12]` commit `24801bc` on `n8d7m12-replay-core`, no push.

## 7. Gaps / handback

- Guard-OFF *runtime* behavior (Android branch) is Part 2's gate, not this part's.
- CPU-backend `WORDS` diagnostics were preserved by verbatim proof + compile
  proof, not by a `WORDS` replay (over the 1-replay budget).
- Recommended next action (orchestrator decision): gate Part 2 Android
  branch/build against this core.
