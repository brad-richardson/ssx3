# TL1 Part 1 — fold GS replay harness onto fork `ssx3` + GPU path logger (report)

Worker: Muse Code, brief `local/muse/prompts/TL1.md` Part 1 only (no device).
Worktree: `~/dev/ssx3-work/TL1/PS2Recomp`, branch `tl1-tools` from fork `ssx3` `d711506`.

## Cherry-picks (without N8D5–N8D7 probe commits)

| Pick | Landed as | Result |
| --- | --- | --- |
| 24801bc replay core | 027d00a | test-file conflict (see below); CMake + 2 new files clean |
| 1a5e3dc Android replay entry | bbe57ff | clean |
| a608ed1 logcat drain correction | cfd37f3 | clean |
| 6799681 PKTSEQ | 902bc9f | clean |
| 4fa0df1 Part 5F4P3 | 78cf814 | clean |

Conflict record: `ps2xTest/src/ps2_gs_replay_tests.cpp` — one hunk. The pick
rewrites the file to a 96-line wrapper; its deletion hunks expect the N8D7M5
probe block (present in the pick's parent a8cfefa, absent on ssx3 d711506).
Resolution: took the pick's post-image (the wrapper) verbatim. Verified: the
wrapper keeps `register_ps2_gs_replay_tests()` (called by ps2xTest main.cpp),
and its only N8D7* mention is the "N8D7M12 Part 1" comment. This is not an
adjacent addition, so "keep both" does not apply; the end state contains zero
probe code (only N8D7M5 *references* remain, inside the replay core's
`#ifdef PS2X_GS_REPLAY_WORD_WATCH` blocks — see Probe-code dependency).

Probe-code dependency: `gs_replay_core.cpp` (new in 027d00a) calls
`ps2xN8D7M5SetCounting`, `ps2xN8D7M5Counts()`, and uses `Ps2xN8D7M5Counts`
(declared in `gs_cpu_backend.h`, defined in `gs_cpu_backend.cpp`) under
`#ifdef PS2X_GS_REPLAY_WORD_WATCH`. Those declarations come only from probe
commit a8cfefa [N8D7M5] and are absent on tl1-tools. The CMake hunk defines
the guard whenever PS2X_BUILD_TEST=ON, which the suite build needs — so this
TU cannot compile in the suite configuration without probe code. No probe
commits were cherry-picked; `git diff --stat 14b1e5cb tl1-tools --
ps2xRuntime/src/runner` is empty.

## GPU path logger

Commit 4348db8 on tl1-tools (`ps2_gs_parallel_backend.cpp` +66, `logGpuPath`
called once from `ensureInit` after `set_debug_mode`). Default-on `std::cerr`
single line, no per-frame cost. Fields mirror
`GSRenderer::get_target_hierarchical_binning` /
`set_hierarchical_binning_subgroup_config` via the same Granite queries
(`supports_subgroup_size_log2`, `vk11_props.subgroupSize`,
`maxComputeWorkGroupInvocations`), the enabled descriptor path
(`supports_descriptor_buffer` / `descriptorHeap` / plain), and the DebugMode
the wrapper sets (`disable_sampler_feedback`, `feedback_render_target`):

`[gs-path] hier_rule=<flat-always|hier-if-large> hier_t2=<n> hier_t4=<n>
subgroup_flat=<waveN|wave64-fixed|free-4..128> subgroup_hier=<…>
vk11_subgroup=<n> max_wg_inv=<n> desc=<buffer|heap|plain>
desc_req=push+heap+buffer sampler_feedback=<on|off> feedback_rt=<on|off>
gpu=<deviceName>`

Mac baseline output: not found (build blocked — see below)

## Build + suite (FIRST FAILURE — step 3)

Configure (rc=0, from the N8D7M12P5F4P2 recipe, taps explicitly OFF,
parallel-gs = clean canonical `~/dev/parallel-gs` @ ssx3 `963cb57`):

```sh
cmake -S ~/dev/ssx3-work/TL1/PS2Recomp -B ~/dev/ssx3-work/TL1/build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DPS2X_BUILD_TEST=ON \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/parallel-gs \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3
ninja -k 0 ps2x_tests   # workdir=build; rc=1
```

Result: exactly one failing TU, `ps2xRuntime/src/lib/gs/gs_replay_core.cpp`
(all 16 errors are the N8D7M5 probe symbols named above; the compile line
carries `-DPS2X_GS_REPLAY_WORD_WATCH=1` because PS2X_BUILD_TEST=ON). Full
receipt: [build-errors.txt](build-errors.txt); full log
`~/dev/ssx3-work/TL1/build.log` (53 KiB, scratch). No binary linked, so no
suite and no replay ran. No P-lane lease was claimed (no boot). Validated
despite the failure: every other TU compiled, including the GPU path logger
(`ps2_gs_parallel_backend.cpp.o` built at step 219/325), the PKTSEQ frontend,
the Android entry `main.cpp`, and the wrapper test TU.

Stuck to one build (no retry).

Runner-dir check: `git diff --stat 14b1e5cb tl1-tools --
ps2xRuntime/src/runner` is empty (re-verified after the logger commit).

## Mac replay vs ON control

Not run (blocked on the build). Control on file:
`local/research/N8D7M12P5F4P2/replay-excerpt.txt` (41 PKTSEQ + 41 GB4_REPLAY
rows); stream `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` untouched.

## Handoff

- tl1-tools (`~/dev/ssx3-work/TL1/PS2Recomp`, no push): `d711506` + 5 picks
  (`027d00a bbe57ff cfd37f3 902bc9f 78cf814`) + logger (`4348db8`).
- Blocked on: `Ps2xN8D7M5Counts`, `ps2xN8D7M5SetCounting(bool)`,
  `ps2xN8D7M5Counts()` — declared/defined only by probe commit a8cfefa
  [N8D7M5] in `gs_cpu_backend.{h,cpp}`. Needed to compile the replay core
  under the suite configuration (PS2X_BUILD_TEST=ON).
- Suggested next action (orchestrator decision): brief a Part 1b to either
  strip the `#ifdef PS2X_GS_REPLAY_WORD_WATCH` blocks (+ the CMake guard)
  from the replay core, or port the ~50-line M5 counter as a default-off
  test-only diagnostic; then re-run the one build + suite + replay.

## Orchestrator gate, Part 1 stop (2026-09-24)

Correct stop. The five picks and the GPU path logger are fine; the one failing TU needs N8D7M5 probe
symbols only inside `#ifdef PS2X_GS_REPLAY_WORD_WATCH`. Decision: drop the word-watch feature from
the folded replay core (it served the N8D7M5 provenance probe, archived on `archive/n8d7l-oracle`)
rather than pull in probe code. Released as Part 1b: one commit removing the CMake define and the
`#ifdef PS2X_GS_REPLAY_WORD_WATCH` blocks (plus any test that exercises word-watch), then the brief's
step 3 unchanged (build, suite, Mac replay vs the Mac ON control, `[gs-path]` line captured).

## Part 1b — word-watch removal + step 3 (Mac only, no device)

Removal commit `f949ff0` on tl1-tools (ONE commit, 4 files, +12/−194, no
probe commit cherry-picked): CMake `PS2X_GS_REPLAY_WORD_WATCH` definition
deleted; all eight `#ifdef PS2X_GS_REPLAY_WORD_WATCH` blocks deleted from
`gs_replay_core.cpp` (WORDS reader, 3× before/after snapshot pairs, teardown);
the wrapper's vacuous `wordsOk` assertion dropped; stale header comments
updated. The `wordsOk` result field stays as API (always true; still read by
the Android gate in main.cpp). Verified post-commit: no
`PS2X_GS_REPLAY_WORD_WATCH` / `PS2X_GS_REPLAY_WORDS` / `N8D7M5` /
`watchAddrs` / `snapshotWords` / `emitWordLine` references outside the TL1
removal comments.

Build (same configure as Part 1: Release, `PS2X_BUILD_TEST=ON`,
`PS2X_ENABLE_DIAG_TAPS=OFF`, `PS2X_GS_SHADOW_PARALLEL=ON`,
parallel-gs `~/dev/parallel-gs` @ ssx3 `963cb57`, codegen
`~/dev/ssx3-work/codegen-ssx3`): `ninja ps2x_tests` rc=0.
Binary `~/dev/ssx3-work/TL1/build/ps2xTest/ps2x_tests` SHA
`271324b39eaf8bc24628cd298310d736b4c74064f69beac71b5c31c839d2fbf9`.

Suite from the worktree root: rc=0, 596/596/0 (log
`~/dev/ssx3-work/TL1/suite-1b.log`, scratch).

Runner-dir check: `git diff --stat 14b1e5cb tl1-tools --
ps2xRuntime/src/runner` empty (at `f949ff0`).

Replay (P-lane slot 2 claimed, released after; stream
`n8d7m6.gs` SHA `f6a78f71…a593` twice, size 1100696462, matches pin;
probe env keys omitted — no probe code on tl1-tools):

```sh
PS2X_GS_REPLAY_CAPTURE=.../N8D7M6/n8d7m6.gs PS2X_GS_REPLAY_BACKEND=parallel \
PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=2050 \
PS2X_GS_REPLAY_PPM_DIR=.../TL1/replay-1b/frames \
PS2X_GS_REPLAY_OUT=.../TL1/replay-1b/parallel.hashes \
PS2X_GS_REPLAY_PKTSEQ=1 \
GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib \
  ../build/ps2xTest/ps2x_tests   # workdir=worktree; rc=0
```

Result vs `local/research/N8D7M12P5F4P2/replay-excerpt.txt`: PKTSEQ 41/41
identical, GB4_REPLAY 41/41 identical, GB4_FRAME/SUMMARY/STATS lines
identical (tick-2050 present `d19b96fe`, packets 862958). Log
`~/dev/ssx3-work/TL1/replay-1b.log` (scratch). One exploratory-command typo
(`timeout` missing on macOS, rc=127, wrote nothing) before the foreground
run — not a brief-step failure.

`[gs-path]` line from that run (single line, default-on):

```text
[gs-path] hier_rule=flat-always hier_t2=1 hier_t4=1 subgroup_flat=free-4..128 subgroup_hier=free-4..128 vk11_subgroup=32 max_wg_inv=1024 desc=plain desc_req=push+heap+buffer sampler_feedback=on feedback_rt=off gpu=Apple M5 Pro
```

Note: `free-4..128` on the Mac matches the renderer's observed Mac path
(N8X1 notebook: fallback `range 4..128, wg=32 (hier=1)`); MoltenVK reports
no exact subgroup size and neither descriptor buffer nor heap.

Handoff: tl1-tools at `f949ff0` (no push); Part 1b step 3 complete, suite
green, replay rows equal the Mac ON control. Ready for the orchestrator to
push and release Part 2 (CLI + device check).

## Orchestrator gate, Part 1b (2026-09-24)

**A.** Word-watch removal `f949ff0` (4 files, +12/−194, no probe code); suite 596/596 from the
worktree root; runner-dir diff empty; Mac replay of `n8d7m6.gs` equals the Mac ON control 41/41 on
PKTSEQ and GB4_REPLAY rows, frame `d19b96fe`. `[gs-path]` on the Mac: `hier_rule=flat-always`,
`subgroup_*=free-4..128`, `desc=plain` (explains why the Mac never ran the Adreno wave128 path).
Pushed `tl1-tools` to fork `ssx3` → **`f949ff0`** (fast-forward from `d711506`). Part 2 released.
