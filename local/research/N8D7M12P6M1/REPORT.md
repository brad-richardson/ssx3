# N8D7M12 Part 6M1 — exact input inventory for next Android package

Worker receipt. **No build, device, network/ssh, lease or push.** Read-only
reconciliation against build files plus the P3/ARCH1 receipts. Owns only
`local/research/N8D7M12P6M1/`; no fork, package, board, ledger, global-config
or other-receipt edits.

Brief: `local/muse/prompts/N8D7M12P6M1.md`. Goal: a reviewable
next-package input manifest plan so the Android build worker pins actual
compiled inputs instead of repeating the P3 attribution error. Hypothesis:
P3's partial SHA list may miss a compiled GS interface, page tracker,
Granite source/patch, shader or fork worker/frontend source; a file-list
comparison against the actual build configuration distinguishes covered
from uncovered inputs. Correct model: a SHA from a historical source gate
proves only that named file, not the entire APK provenance. **No old APK
is claimed to match current working trees; no blanket historical
equivalence is claimed anywhere in this report.**

Sources read in full: `~/dev/AGENTS.md`, repo `AGENTS.md`,
`local/AGENTS.local.md`, `local/research/ARCH1/REPORT.md`,
`local/research/ARCH1/ORCH-GATE.md`,
`local/research/N8D7M12P3/REPORT.md`, `.../source_gate.py`,
`.../apk_gate.py` (+ `source-gate.json`, `apk-gate.json`, `build.sh`,
`check.py` as evidence). Build-configuration evidence below is from local
mirror checkouts: fork `~/dev/ssx3-work/N8D7M12P2/PS2Recomp`
(rev `a608ed1`, the P3 Mac input rev per P3 REPORT:17) and renderer
`~/dev/ssx3-work/N8D7F/parallel-gs/`; WSL paths
(`/home/brad/n8d7m12p3/...`) are quoted only as P3 receipt pins, not as
locally re-read bytes. Current-tree hashes/diffs are labeled as such and
are NOT back-claimed onto the historical WSL root.

## 1. P3 APK and native-member pins already proved (historical, WSL double-reads)

From `local/research/N8D7M12P3/source-gate.json` + `apk-gate.json`
(+ `REPORT.md:77-85`):

| Item | SHA-256 / value (two reads each in gate) | Status |
| --- | --- | --- |
| APK `app-release.apk` | `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512`, 153,753,116 B | proven historical (apk-gate.json:2-5; P3 REPORT:24-25) |
| arm64 runner `lib/arm64-v8a/libps2EntryRunner.so` | `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d`, 139,512,968 B | proven historical, NEW vs N8D7M1 `f3de999a…c1bf` (apk-gate.json:15-21; P3 REPORT:26) |
| arm64 Turnip `lib/arm64-v8a/libvulkan_freedreno.so` | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`, 14,188,488 B member (14,188,488 B source, same SHA) | proven historical, pin unchanged (apk-gate.json:22-28; P3 REPORT:27) |
| arm64 HAL shim `lib/arm64-v8a/libhardware.so` | member `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`, 7,112 B | proven historical member, pin unchanged (apk-gate.json:8-14; P3 REPORT:28) |
| Runner Build ID | `65ce162abca08d664223a362824b70c86aea6f4f`, NEW (N8D7M1 was `73291620f0c62fdc01ac0b603e9e5cca3114d0a5`) | proven historical via llvm-readelf (apk_gate.py:79-84; apk-gate.json:46; P3 REPORT:29) |
| APK member set | exactly the 3 arm64 members above, no x86 | proven historical (apk_gate.py:63-65; P3 REPORT:84) |
| Packaged strings | 23/23 present incl. `PS2X_GS_REPLAY_ONDEVICE`, `PS2XGSC1`, `[n8d7f]/[n8d7l]`, oracle/circuit keys | proven historical (apk-gate.json:47-71; P3 REPORT:87-94) |
| Sole arm64 CMake cache | `.../.cxx/RelWithDebInfo/4f434a1x/arm64-v8a/CMakeCache.txt`: 6 flags OFF, `PS2X_GS_SHADOW_PARALLEL=ON`, G43 source + external codegen paths | proven historical (apk-gate.json:30-44; P3 REPORT:96-103) |

Backend-pin correction (ARCH1 `ORCH-GATE.md:3`, `REPORT.md:77-86`): the
actual OFF-pair package backend is
`84a13a80686be8d4ed17750a9399d298ea6b998b98f48d3720b6b5bc839a4645`
(`source-gate.json:68-73`). Predecessor `c6135b3c…d4fb41f` (F2/F3 label)
is NOT this package's source; do not cite it as the P3 backend.

## 2. Currently pinned source paths (historical WSL double-reads, file-only)

From `source-gate.json:18-144` (`source_gate.py:85-110`):

| Label | WSL path pinned | SHA (both reads) |
| --- | --- | --- |
| ov_cmakelists | `PS2Recomp/ps2xRuntime/CMakeLists.txt` | `b229b7ac…fddcf` |
| ov_cpu_backend_h | `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h` | `0d0377ed…e3a46` |
| ov_replay_core_h | `ps2xRuntime/include/runtime/gs/gs_replay_core.h` | `d80f9af2…f9964` |
| ov_cpu_backend_cpp | `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp` | `c762efd6…ec57f` |
| ov_replay_core_cpp | `ps2xRuntime/src/lib/gs/gs_replay_core.cpp` | `c5fdaf64…f396c` |
| ov_main | `ps2xRuntime/src/main.cpp` | `7ab53178…4c17bf` |
| ov_replay_tests | `ps2xTest/src/ps2_gs_replay_tests.cpp` | `db2e9c7c…9611ae` |
| backend | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | `84a13a80…a4645` |
| header | `ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h` | `9635a40e…95e71f7` |
| g43_interface | `parallel-gs/gs/gs_interface.hpp` | `3a1751b4…05954d9d` |
| g43_renderer_hpp | `parallel-gs/gs/gs_renderer.hpp` | `fae3261a…a93a401a` |
| g43_renderer_cpp | `parallel-gs/gs/gs_renderer.cpp` | `85c29cb0…3de77e` |
| writer | `ps2xRuntime/src/lib/ps2_runtime.cpp` | `358d726b…88c3f96` |
| shader_header | `parallel-gs/gs/n8d5_tile_spirv.hpp` | `19b9ba5f…71bac9` |
| codegen | `/home/brad/n8b1/codegen-ssx3/register_functions.cpp` | `8ea8ed43…662d688a3` |
| turnip (jniLibs source) | `jniLibs/arm64-v8a/libvulkan_freedreno.so` | `717812c3…54c1ac29d` (= packaged member SHA: passthrough proven) |
| shim_source (jniLibs source) | `jniLibs/arm64-v8a/libhardware.so` | `d7add7e8…90cafa0` (≠ packaged member `1b49d27c…`: transform/repack unproven, see §3) |

Also proved structurally: fork added/modified/removed file lists
(2 added / 5 modified / 0 removed), `parallel: []`, `jniLibs: []` diffs
vs N8D7M1, no `ps2xRuntime/src/runner` files (`source-gate.json:3-17,147`;
P3 REPORT:21,66-73). These are tree-shape assertions, not content pins
for the unlisted files.

## 3. Missing or ambiguous compiled inputs (the next-build manifest gap)

Each row names the exact path or bounded glob **in the build-root terms**
the next worker must hash, the evidence it enters the Android link, and
the action at the next build. "Historical" = unrecoverable from P3
receipts (P3 never hashed it); "future" = must be pinned at the next
build. Current-tree observations are labeled and prove nothing historical.

### 3a. Fork core / frontend / worker / backend (ps2xRuntime)

Build-config root: `ps2xRuntime/CMakeLists.txt` in the P2 mirror
(`~/dev/ssx3-work/N8D7M12P2/PS2Recomp/ps2xRuntime/CMakeLists.txt`).

| # | Missing/ambiguous input (build-root-relative) | Enters link: evidence (exact lines) | Next-build action |
| --- | --- | --- | --- |
| F1 | `ps2xRuntime/src/lib/gs/gs_frontend.cpp` (+ `include/runtime/gs/gs_frontend.h`, `gs_backend.h`, `gs_types.h`, `gs_worker.h`, `ps2_gs_parallel_backend.h`, `ps2_gs_common.h`, `ps2_gs_memory.h`, `ps2_gif_arbiter.h`, `gs_stream_capture.h`, `gs_replay_core.h` already pinned, `gs_cpu_backend.h` already pinned) | `ps2_runtime STATIC` member line 451 (`src/lib/gs/gs_frontend.cpp`); headers via `target_include_directories .../include` line 640-643 | double-SHA-read + record; headers hashed individually (unity build batches TUs, headers still inputs) |
| F2 | `ps2xRuntime/src/lib/gs/gs_worker.cpp` | `ps2_runtime STATIC` line 446 | double-SHA-read + record (ARCH1 S1 rehash `3300f41d…` is a current-tree read, not a P3 pin) |
| F3 | `ps2xRuntime/src/lib/gs/ps2_gs_shadow.cpp` (backend .cpp IS pinned F-pinned; shadow TU is not) | `ps2_gs_shadow STATIC` lines 503-506 (both TUs); linked into `ps2_runtime` line 535 and runner line 646-649 | double-SHA-read + record |
| F4 | `ps2xRuntime/src/lib/gs/ps2_gif_arbiter.cpp`, `gs_stream_capture.cpp`, `ps2_gs_memory.cpp`, `src/lib/game_overrides.cpp`, `ps2_audio.cpp`, `ps2_audio_vag.cpp`, `ps2_iop_host.cpp`, `ps2_memory.cpp`, `ps2_pad.cpp`, `ps2_vif1_interpreter.cpp`, `vu/ps2_vu1_core.cpp`, `vu/ps2_vu1_upper.cpp`, `vu/ps2_vu1_lower.cpp`, `games_database.cpp` (only `ps2_runtime.cpp` pinned) | `ps2_runtime STATIC` lines 442-462 | double-SHA-read each + record |
| F5 | `ps2xRuntime/src/lib/Kernel/*.cpp` (GLOB) | `file(GLOB_RECURSE KERNEL_SRC_FILES .../src/lib/Kernel/*.cpp)` lines 557-563, added via `target_sources` 561-563 | hash the GLOB expansion (record expanded file list + each SHA); capture list from build-system file list |
| F6 | `ps2xRuntime/src/runner/*.cpp` GLOB + `src/runner/main.cpp` fallback + `src/main.cpp` (only `src/main.cpp` pinned as ov_main) | lines 565-576 (`file(GLOB RUNNER_SRC_FILES .../src/runner/*.cpp)` + fallback append). Local mirror runner dir holds `register_functions.cpp` (read 2026-09-24); P3 gate proved the WSL root had NO `ps2xRuntime/src/runner/` files, so WSL `RUNNER_SRC_FILES` = in-tree glob (empty dir → glob empty) + fallback `src/main.cpp`. Historical glob expansion still unlisted | record expanded runner file list + double-SHA each; assert runner-dir-absent again at next build (`runner_files: []`) |
| F7 | `ps2xRuntime/src/lib/ps2_android_runtime.cpp` (Android-only TU) | line 752-754 (`if(PS2X_IS_ANDROID) target_sources(ps2EntryRunner PRIVATE src/lib/ps2_android_runtime.cpp)`) — compiled into THIS package, never hashed | double-SHA-read + record |
| F8 | `ps2xRuntime/src/lib/ps2_debug_panel.cpp` (expected ABSENT when DEBUG_UI=OFF) + iOS/Vita TUs (expected absent) | lines 668-674 (gated `DEBUG_UI AND NOT VITA AND NOT ANDROID AND NOT IOS`), 743-754, 756-793 | assert absence/presence per flag in the build-system file list; record the check |
| F9 | `PS2X_GAME_CODEGEN_DIR/*.cpp` GLOB (9,455 `.cpp` in local `~/dev/ssx3-work/codegen-ssx3/`, 9,457 entries total; only `register_functions.cpp` pinned) | lines 651-666 (`file(GLOB PS2X_GAME_SOURCES ...)` → `ps2_game_objects` STATIC → linked to runner line 665). Excludes `._*` line 653 | hash ALL expanded codegen inputs (list + each SHA, or list + combined manifest hash); record `PS2X_GAME_SOURCE_COUNT`; double-read `register_functions.cpp` again |
| F10 | Root `CMakeLists.txt`, `ps2xRuntime/cmake/ReleaseMode.cmake`, `cmake/CopyFfmpegDlls.cmake`, `android/app/build.gradle`, `android/{settings,gradle.properties}`, `AndroidManifest.xml` | `android/app/build.gradle:55-60` (`path '../../CMakeLists.txt'`), `ps2xRuntime/CMakeLists.txt:37` (ReleaseMode include) | hash each build script; capture full `CMakeCache.txt` text + `gradlew` flags, NDK/CMake versions |

Unity/PCH note: `PS2X_ENABLE_RUNNER_UNITY_BUILD` (default ON, batch 32)
and `PS2X_ENABLE_RUNNER_PCH` (default ON) change TU batching/PCH, not the
input set (lines 601-628). They must be recorded as flags, not as a
substitute for per-file hashes.

### 3b. paraLLEl renderer / interface / page tracker / shaders

Lib root: `parallel-gs/gs/CMakeLists.txt` (N8D7F mirror); linked via
`add_subdirectory("${PS2X_PARALLEL_GS_SOURCE_DIR}" ...)` +
`target_link_libraries(ps2_gs_shadow PUBLIC parallel-gs)` (ps2xRuntime
lines 521-533, requires `gs/gs_interface.hpp` sentinel line 522).

| # | Missing/ambiguous input | Enters link: evidence | Next-build action |
| --- | --- | --- | --- |
| G1 | `parallel-gs/gs/gs_interface.cpp` (header pinned; .cpp NOT) | `gs/CMakeLists.txt:10` (`gs_interface.cpp gs_interface.hpp` in `parallel-gs` STATIC) | double-SHA-read + record (ARCH1 S6 cites `gs_interface.cpp:5126-5165` as directly read but unpinned) |
| G2 | `parallel-gs/gs/page_tracker.cpp` + `page_tracker.hpp` | `gs/CMakeLists.txt:13` (in `parallel-gs` STATIC) | double-SHA-read both + record |
| G3 | `parallel-gs/gs/gs_util.cpp` + `gs_util.hpp` | `gs/CMakeLists.txt:11` | double-SHA-read both + record |
| G4 | `parallel-gs/gs/gs_register_addr.hpp`, `gs_registers.hpp`, `gs_registers_debug.hpp` | transitive includes of pinned `gs_renderer.cpp/hpp` + `gs_interface.hpp` (same STATIC lib; e.g. renderer verified lines per ARCH1 S5 `renderer:1194-1208,5354`) | double-SHA-read each + record |
| G5 | `parallel-gs/gs/shaders/*` EXCEPT pinned `n8d5_tile_spirv.hpp`: `slangmosh.hpp`, `slangmosh_iface.hpp`, `slangmosh.json`, `*.comp`, `*.frag`, `*.vert`, `*.h` (bounded glob `gs/shaders/*`), PLUS untracked candidates `gs/n8d5_tile_spirv.hpp`-adjacent `gs/shaders/n8d5_tile.comp`, `gs/shaders/n8d5_tile.spv` (present untracked in N8D7F mirror; presence in the next build root unknown) | embedded-shader path: P3 pins only the generated header; `PARALLEL_GS_STANDALONE=ON` uses "embedded slangmosh shaders, no runtime shader compiler" (ps2xRuntime line 525-526); `slangmosh.sh` + `slangmosh.json` drive generation | hash the full `gs/shaders/*` expansion + generation script/json; record whether `n8d5_tile.comp/.spv` exist in the build root; pin the generator inputs, not just the output header |
| G6 | `parallel-gs/CMakeLists.txt`, `parallel-gs/gs/CMakeLists.txt` | build graph roots (`add_subdirectory(gs)` line 64; lib member list above) | hash both + record |
| G7 | Granite submodule pin + dirty patches (entire `parallel-gs/Granite` tree or at minimum: submodule commit, `git diff` of dirty files, per-file SHAs of compiled Granite TUs incl. `Granite/vulkan/memory_allocator.cpp` per ARCH1 S6 `memory_allocator.cpp:480-505`) | `parallel-gs/CMakeLists.txt:62` (`add_subdirectory(Granite)`), `gs/CMakeLists.txt:16` (`granite-vulkan granite-math` link). P3 gate NEVER hashed any Granite path. N8D7F mirror shows why this matters (current-tree only): `Granite` shows as modified submodule + 5 dirty files (`application/platforms/CMakeLists.txt`, `util/timer.cpp`, `vulkan/command_buffer.cpp`, `vulkan/memory_allocator.cpp`, `vulkan/shader.cpp`) and 8-file G-lane diffstat in the superproject — but N8D7F is the G-lane patch-stack checkout (`faf6400`), NOT the P3 build root, so this dirt is NOT back-claimed onto `caa11102…` | at next build: record `git -C <build>/parallel-gs submodule status`, `git diff` (superproject + Granite), and double-SHA every compiled Granite input OR the full Granite tree manifest; historical Granite bytes for P3 are UNRECOVERABLE — mark unknown, do not reconstruct |

### 3c. Build flags (proven vs to-capture)

Proven historical (apk-gate cache + build.sh): the 6 OFF flags, `ON`,
both `-P` source dirs, `--max-workers=4`, `assembleRelease`, single
`BUILD SUCCESSFUL in 5m 18s` (P3 REPORT:47-50,96-103). Build.gradle
mirror pins the flag-forwarding lines (`build.gradle:25-42`: TEST/TAPS/
RUNTIME/AGRESSIVE/RPC/DEBUG_UI OFF forced, BOOT_ELF/CODEGEN/SHADOW/PARALLEL
forwarded; `targets 'ps2EntryRunner'`; `abiFilters 'arm64-v8a'`;
`ndkVersion '28.2.13676358'`; cmake `3.22.1`; jniLibs override lines
51-53).

To capture at next build: full `CMakeCache.txt` text, `./gradlew` command
line verbatim, Java/SDK/Gradle/NDK/CMake versions, `CMAKE_BUILD_TYPE`
(RelWithDebInfo per `.cxx/RelWithDebInfo` path — confirm, don't assume),
`PS2X_DEFAULT_BOOT_ELF` value (device ELF path, P3 `build.sh:18`), unity
batch size, PCH on/off, ThinLTO/IPO setting, `ANDROID_CPP_FEATURES`,
`minSdk/targetSdk/compileSdk`, signing config, and the CMake/Gradle
build-system file list (Ninja/Make file list or `assembleRelease` file
inputs) proving §3a–3b expansions.

### 3d. Turnip / HAL

| # | Input | Evidence | Next-build action |
| --- | --- | --- | --- |
| H1 | `jniLibs/arm64-v8a/libvulkan_freedreno.so` source `7178…` = member `7178…` | source-gate.json:131-137 vs apk-gate.json:22-28 | PROVEN passthrough; re-double-read at next build |
| H2 | `jniLibs/arm64-v8a/libhardware.so` source `d7ad…` ≠ member `1b49…` (7,112 B member) | source-gate.json:138-144 vs apk-gate.json:8-14 | AMBIGUOUS: record packaging rule (strip/zip-align/compress) + full `jniLibs/**` file list with per-file double SHAs; tie source SHA → member SHA explicitly |
| H3 | `jniLibs/**` full listing (P3 asserted `jniLibs: []` diff vs N8D7M1 but never listed contents) | source_gate.py:78-79 (diff only, no listing); build.gradle:51-53 (`jniLibs.srcDirs`) | list + hash every file under the build root's `jniLibs/`; assert the APK `lib/` set equals exactly that input set |

## 4. Artifact graph (source root → native member → APK)

Labels: PROVEN = double-read historical pin; PLANNED = next-build
capture defined in §3; UNKNOWN = historical bytes unrecoverable, future
baseline only.

```
[build root PS2Recomp/ fork sources]
  ├─ 7 overlay files + backend 84a13a80… + header + writer ──PROVEN──▶
  ├─ F1-F8 fork TUs/headers/Kernel/runner/Android TU ──UNKNOWN hist / PLANNED──▶
  │                                                              ┌ libps2EntryRunner.so 329e44db… (Build ID 65ce16…) ──PROVEN──▶
  ├─ codegen register_functions.cpp ──PROVEN──▶ ps2_game_objects ┤  (F9 rest UNKNOWN hist / PLANNED)
  │   + codegen sub_*.cpp ×~9454 ──UNKNOWN hist / PLANNED──▶     │
[build root parallel-gs/]                                        │                                              ┌ app-release.apk caa11102… ──PROVEN──▶
  ├─ gs_interface.hpp + gs_renderer.hpp/.cpp ──PROVEN──▶         │
  ├─ gs_interface.cpp, page_tracker.*, gs_util.*,                │
  │   register headers, shaders/*, CMake roots ──UNKNOWN / PLANNED──▶ parallel-gs STATIC ──(link PLANNED-proof)──▶ ps2_gs_shadow ─┤
  └─ Granite tree + submodule pin + patches ──UNKNOWN / PLANNED──┘                                                              │
[jniLibs/] Turnip 7178… ──PROVEN passthrough──▶ libvulkan_freedreno.so ──PROVEN──▶                                              │
           HAL src d7ad… ──AMBIGUOUS transform──▶ libhardware.so 1b49… ──PROVEN member──▶                                        ┘
[flags] 6×OFF + SHADOW=ON + 2 source dirs ──PROVEN──▶ + full cache/cmdline/file-list ──PLANNED──▶ (all links above)
```

Historical UNKNOWN links must NOT be filled by current-tree bytes
(P2/N8D7F mirrors, ARCH1 rehashes S1-S6); the next build establishes the
new pinned baseline and ties runner Build ID + native-member SHAs to the
new APK SHA fresh.

## 5. Proposed next-build commands (IN REPORT ONLY — not run)

```sh
# 0. Pre-copy: record pins of every §3 path in the source checkout(s),
#    two matching SHA-256 reads each (script asserts pairs equal).
python3 local/research/N8D7M12P6M1/next_source_gate.py > local/research/N8D7M12P6M1/next-source-gate.json 2> local/research/N8D7M12P6M1/next-source-gate.err
# 1. Dirty-state: inside each build-root repo + Granite submodule:
git -C <root>/PS2Recomp status --short; git -C <root>/PS2Recomp diff --stat; git -C <root>/PS2Recomp log --oneline -1
git -C <root>/parallel-gs status --short; git -C <root>/parallel-gs diff --stat; git -C <root>/parallel-gs log --oneline -1
git -C <root>/parallel-gs/Granite status --short; git -C <root>/parallel-gs submodule status
#    (record all output; any non-empty diff is part of the manifest)
# 2. Copy sources; re-read every §3 SHA twice post-copy and assert equal
#    (source-gate pattern: mac-overlay-pins.txt + overlay-sha-post.txt).
# 3. Configure+build with the P3 build.sh command line verbatim except the
#    new root; tee full log; capture the build-system file list
#    (Ninja `ninja -t inputs` / CMake file API or Gradle `--info` inputs)
#    proving the F5/F9/G5 glob expansions actually compiled.
# 4. Post-build: re-run the source gate (postbuild parity), then the APK
#    gate: double-SHA APK + each member, llvm-readelf Build ID, string set,
#    sole-cache assertion, and an explicit source-SHA → member-SHA →
#    APK-SHA linkage table (H2 transform documented, not assumed).
# 5. Capture: full CMakeCache.txt text, `gradlew` argv, toolchain versions,
#    PS2X_GAME_SOURCE_COUNT, jniLibs/** listing, Granite manifest.
# 6. Mechanical check: python3 local/research/N8D7M12P6M1/check.py
```

## 6. Gaps (hand-back)

1. Historical Granite bytes for the `caa11102…` package are
   unrecoverable from P3 receipts (no Granite path ever hashed) — future
   baseline only (§G7).
2. Historical `gs_interface.cpp` / `page_tracker.*` / `gs_util.*` /
   shader-expansion / F1-F9 fork TU bytes likewise unpinned — future
   baseline only.
3. HAL shim source→member transform (`d7ad…` → `1b49…`) unexplained —
   needs the next build's packaging rule + file list (H2).
4. Current-tree reads (P2 `a608ed1` fork, N8D7F `faf6400` patch stack,
   ARCH1 S1-S6 rehashes) were used ONLY for build-graph evidence, never
   as historical content claims.
5. No causal graphics verdict is made; equal/differing-output analysis
   belongs to the fingerprint pair (ARCH1 gates), not this manifest.

## 7. Receipts

`REPORT.md`, `check.py`, `check-result.json` (this dir). Pinned revs:
fork input `a608ed1e161f60334a0cf3a80d1af3e54b692bd2` (P3 REPORT:17);
backend `84a13a80686be8d4ed17750a9399d298ea6b998b98f48d3720b6b5bc839a4645`;
APK `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512`;
runner `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d`
(Build ID `65ce162abca08d664223a362824b70c86aea6f4f`).
