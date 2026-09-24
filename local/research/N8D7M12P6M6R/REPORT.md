# N8D7M12 Part 6M6R — one pinned Android package via external wrapper (worker receipt)

Worker receipt. Brief: `local/muse/prompts/N8D7M12P6M6R.md` (incorporates
`local/muse/prompts/N8D7M12P6M6.md`) plus orchestrator steering authorizing
the P3-root pinned Gradle wrapper as a build tool. Owns only
`local/research/N8D7M12P6M6R/` text scripts/receipts and private Mac
`~/dev/ssx3-work/N8D7M12P6M6/{app-release.apk,CMakeCache-arm64.txt}`.
No source/fork/renderer/collector edit, no Odin/emulator action, no game
bytes or binaries in git, no upstream contact, no subagents, no push.
**One `assembleRelease` only, no repair loop, no install/launch.**
These facts do not prove an Odin image or GPU cause.

Route history: SSH to `bytesize` worked on this route. The first attempt
(`build.sh`/`build.txt`, RC=127) stopped before any build because the
staged fork tracks no `android/gradlew` (wrapper script never in fork
history; P3/N8D7M1 roots carried it out-of-band). Zero builds were
attempted then. The orchestrator then pinned the P3-root wrapper files and
authorized invoking that external wrapper from the new-root `android` cwd
as a build tool, with no copies into the four staged source roots. This
report covers the full part: preflight, transfer, verify, the one build,
and the package gate.

## 1. Evidence table

| Item | Value |
| --- | --- |
| WSL root | `/home/brad/n8d7m12p6m6` (fresh; absent at preflight) |
| P6M5 checker re-run | 24 rows, 0 failing, verdict A |
| Source aggregate pre/post build | `6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a` both runs, `status=match`, added/missing/changed empty |
| Transfer | tar stream of 4 staged dirs + manifest + collector; STREAM_BYTES=669184000; 6 top-level entries, 619,387,661 B |
| External wrapper (tool, not source) | `/home/brad/n8d7m12p3/PS2Recomp/android/gradlew` `a3648413…300a3`, wrapper jar `49849512…484f17`, props `3d91f093…94884` (each double-read; props equal staged; no copies into new root) |
| Build | one `assembleRelease`, `BUILD SUCCESSFUL in 5m 34s`, 48 tasks, no repair (`build2.txt`) |
| Build argv | external gradlew + P3 flags; `-Pps2xGameCodegenDir` = new-root `codegen-ssx3`; cwd new-root `android`; Gradle 8.9, Temurin JDK 17.0.20.1+1, NDK r28c, CMake 3.22.1, build-tools 34.0.0 |
| APK, WSL (2 reads) | `da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262`, 153,753,116 B (new vs P3; same byte size as P3) |
| APK, Mac (2 reads) | `da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262`, 153,753,116 B |
| arm64 runner | `e5a3302c6bef489b04a4a143c47b01e616735f8db0acdbda663710a326c11af1`, 139,515,320 B (new vs N8D7M1 and P3) |
| arm64 Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`, 14,188,488 B (pin unchanged, pairs equal) |
| arm64 HAL | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`, 7,112 B (pin unchanged, pairs equal) |
| Runner Build ID | `4c9c9d149900cdc3494201c38124d11bfb616fa3` (new vs N8D7M1 and P3) |
| Packaged strings | 22/23 P3-set present; sole miss `PNG write failed path=` is absent from all staged inputs (fork-rev change, §5) |
| Sole arm64 CMake cache | `.../.cxx/RelWithDebInfo/6c2c3c4v/arm64-v8a/CMakeCache.txt`: 6 flags OFF, `PS2X_GS_SHADOW_PARALLEL=ON`, new-root parallel + codegen dirs, `RelWithDebInfo`; full text private (33,701 B, `fa75edad…32994`) |
| Compiled inputs | 449 `compile_commands.json` entries incl. fork frontend/worker/backend + `gs_interface.cpp` + `page_tracker.cpp` + Granite `memory_allocator.cpp`; 296 `ps2_game_objects` unity batches incl. `register_functions.cpp` + 9,455 distinct codegen `.cpp` |
| Caps | WSL root 7,867,078,980 B (7.33 GiB < 10 GiB); Mac scratch 147 MiB (<500 MiB); receipts 144 KiB (<512 KiB); global 157.5→157.7/200 GB |

## 2. Exact commands

```sh
python3 local/research/N8D7M12P6M5/check.py   # 24/24 A (preflight-p6m5-check.txt)
bash local/tooling/disk_budget.sh             # before/after (disk-budget-*.txt)
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../preflight.sh > .../preflight.txt 2>&1
bash .../transfer.sh > .../transfer.txt 2> .../transfer-bytes.txt   # 669,184,000 B streamed
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../source_verify.sh > .../source-verify-pre.json 2> ...-pre.err
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../build.sh > .../build.txt 2>&1   # RC=127, no gradlew, zero builds
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../wrapper_pins.sh > .../wrapper-pins.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../build2.sh > .../build2.txt 2>&1   # THE one build
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../source_verify.sh > .../source-verify-post.json 2> ...-post.err
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../compiled_inputs.sh > .../compiled-inputs.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- bash -s' < .../codegen_graph.sh > .../codegen-graph.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- python3 -' < .../apk_gate.py > .../apk-gate.json 2> .../apk-gate.err   # RC=1 on 1 string
ssh bytesize 'wsl -d Ubuntu -- python3 -' < .../apk_facts.py > .../apk-facts.json 2> .../apk-facts.err
ssh bytesize 'wsl -d Ubuntu -- cat .../CMakeCache.txt' > ~/dev/ssx3-work/N8D7M12P6M6/CMakeCache-arm64.txt
ssh bytesize 'wsl -d Ubuntu -- cat .../app-release.apk' > ~/dev/ssx3-work/N8D7M12P6M6/app-release.apk
python3 local/research/N8D7M12P6M6R/check.py  # 20 rows pass, verdict A
```

Transfer stderr note: remote GNU tar printed 28,049 benign `Ignoring
unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.provenance'`
lines (macOS bsdtar xattrs ignored on extract); condensed to a 517 B
summary in `transfer-bytes.txt`. Content integrity rests on the collector
`verify: match` pre and post build, not on that stderr.

## 3. Source→native→APK graph

```
[P6M5 stage 26,211 files: PS2Recomp 323 + parallel-gs 16,429 + codegen-ssx3 9,457 + jniLibs 2]
  == tar 669,184,000 B over ssh ==▶ [/home/brad/n8d7m12p6m6 same four roots]
  == collector verify pre: match 6877de87…80316a ==▶
  ── external pinned wrapper (tool): gradlew a3648413… + jar 49849512… + props 3d91f093…
     invoked from new-root android cwd; zero bytes copied into staged roots ──
  == one assembleRelease (Gradle 8.9, NDK r28c, SHADOW=ON, 6xOFF, arm64) ==▶
  ├─ compile_commands 449 entries: gs_frontend / gs_worker / parallel_backend ──▶
  ├─ gs_interface.cpp + page_tracker.cpp + Granite memory_allocator (+71 Granite) ──▶
  ├─ 296 ps2_game_objects unity batches: register_functions + 9,455 codegen .cpp ──▶
  │        ┌ libps2EntryRunner.so e5a3302c… (Build ID 4c9c9d14…, 139,515,320 B) ──▶
  ├─ Turnip 7178… ──passthrough──▶ member 7178… (14,188,488 B) ──▶
  └─ HAL staged member 1b49… ──passthrough──▶ member 1b49… (7,112 B) ──▶
                                                              ┌ app-release.apk da9a41a8… (153,753,116 B)
  == collector verify post: match 6877de87…80316a (no staged-source mutation) ==▶
  == Mac double-read da9a41a8… == WSL ==▶ (transfer intact; not installed/launched)
```

Full SHAs: aggregate
`6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a`;
APK `da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262`;
runner
`e5a3302c6bef489b04a4a143c47b01e616735f8db0acdbda663710a326c11af1`;
Turnip
`717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`;
HAL `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`;
Build ID `4c9c9d149900cdc3494201c38124d11bfb616fa3`; CMakeCache
`fa75edadbf453e01e8be9b68d724d81c3703132b390bc304c258547437632994`;
gradlew
`a3648413b47ef77af21d5ebc36c687c7d103aaef3e17f33de7d4f080a6f300a3`;
wrapper jar
`498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17`;
wrapper props
`3d91f0932da99885c41e9dc4e85c9f9a2d3bfef4f0ad87473014dc0827a94884`.

## 4. Build tail

```
> Task :app:mergeReleaseNativeDebugMetadata
> Task :app:assembleRelease

BUILD SUCCESSFUL in 5m 34s
48 actionable tasks: 48 executed
```

One `assembleRelease`, no repair loop: `assembleRelease.log` on WSL holds
exactly one `BUILD SUCCESSFUL` and zero `FAILED` lines
(`codegen-graph.txt`). The earlier `build.txt` RC=127 never reached
Gradle (missing wrapper script in staged bytes; version prologue only).

## 5. Packaged-string difference vs P3 (22/23, explained by inputs)

The strict gate (`apk_gate.py`, P3 semantics) stopped at one string:
`PNG write failed path=` is absent from the new runner; all 22 others —
replay entrypoint/core, selected/oracle, vram/input/circuit keys — are
present (`apk-gate.err`). Read-only follow-up (no rebuild):

- `grep -rl "PNG write failed"` over the **entire** P6M5 stage tree:
  empty — the string is in none of the staged inputs.
- P3-era tree: `/home/brad/n8d7m1/PS2Recomp/ps2xRuntime/src/lib/
  ps2_runtime.cpp:562` holds `[frame:dump] PNG write failed path=`.
- Staged `ps2_runtime.cpp` (@4fa0df1) mentions PNG only in comments
  (lines 482, 527).

So the miss is a fork-rev change between P3's input tree and staged
`4fa0df1`, and the packaged binary faithfully reflects its pinned inputs.
The checker pins the missing set to exactly this one string (any other
absence fails). No causal graphics claim is made from this log-line diff.

## 6. Gaps (hand-back, no Odin/GPU verdict)

1. No `PS2X_GAME_SOURCE_COUNT` message exists in the build log or cache;
   the game-input count is instead proved two ways: 9,455 distinct
   codegen `.cpp` `#include`s across the 296 `ps2_game_objects` unity
   batches plus the codegen dir listing (9,455 `.cpp` of 9,457 entries).
   The literal CMake variable remains open.
2. `ps2_android_runtime.cpp` has no dedicated `compile_commands.json`
   entry (Android TU is inside `ps2EntryRunner` unity batches: 297
   `unity_` entries); its compilation is covered by the unity batch, not
   by a named entry. Not marked open: unity batching is the recorded
   mechanism.
3. The APK is byte-identical in size to P3's (153,753,116 B) with a new
   SHA — a size coincidence, claimed as nothing more.
4. The WSL root stays in place with build outputs (7.33 GiB); no other
   lane may write it. Full build log, CMakeCache text (Mac private copy
   kept), and unity-batch lists stay out of git per the excerpts-only
   rule.
5. Source/default-OFF path is statically gated; no runtime OFF-path or
   Turnip/HMI behavior is proved without a later Odin run. The APK was
   not installed or launched.

## 7. Recommended next action

Hand the pinned APK (`da9a41a8…`, Mac scratch + WSL root) and this
source→member→APK link to the next lane step (Odin install/run per its
own brief). No rebuild is needed: inputs are pinned pre/post with equal
aggregates, the one build succeeded without retry, and the sole P3-set
string difference is explained by staged fork bytes.

## 8. Receipts

- `local/research/N8D7M12P6M6R/{REPORT.md,check.py,check-result.json}`
  (committed with `git add -f`, `[N8D7M12] Part 6M6R` /
  `Orchestrated-By: Muse Code`; no push; this build continues that part
  under orchestrator steering).
- Scripts: `preflight.sh`, `transfer.sh`, `count_bytes.py`,
  `source_verify.sh`, `build.sh` (pre-steering stop), `wrapper_pins.sh`,
  `build2.sh` (the one build), `compiled_inputs.sh`, `codegen_graph.sh`,
  `apk_gate.py` (strict, RC=1 on 1 string), `apk_facts.py` (read-only
  facts).
- Outputs: `preflight-p6m5-check.txt`, `disk-budget-before/after.txt`,
  `preflight.txt`, `transfer.txt`, `transfer-bytes.txt`,
  `transfer-tar.err` (empty), `source-verify-pre/post.json{,.err}`,
  `build.txt`, `build2.txt`, `wrapper-pins.txt`, `compiled-inputs.txt`,
  `codegen-graph.txt`, `apk-gate.json` (empty) + `apk-gate.err`,
  `apk-facts.json` + `apk-facts.err` (empty), `cmake-cache-fetch.err`
  (empty), `apk-fetch.err` (empty).
- Base commit `15027e8e`; stop-commit `743f9449` superseded in content
  by this build (kept in history, not rewritten).
- No APK, binary, or game bytes in git; no device, lease, or upstream
  action.
