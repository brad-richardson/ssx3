# N8D7M12 Part 3 — isolated Android APK build/package

Worker receipt. **One `assembleRelease` only, no device action (no Odin/iOS
launch, lease, push, stream copy, second build, fork/source edit, upstream
contact, or generated game code in git).** Source/default-OFF path is
statically gated; **no runtime OFF-path or Turnip/HMI behavior is proved
without a later Odin run.**

Brief: `local/muse/prompts/N8D7M12P3.md`. Goal: arm64 APK from the gated
`a608ed1` source, preserving N8D7M1's G43/Turnip/HAL and external codegen.

## 1. Evidence table

| Item | Value |
| --- | --- |
| WSL root | `/home/brad/n8d7m12p3` (new); baseline `/home/brad/n8d7m1` |
| Mac fork (read-only input) | `~/dev/ssx3-work/N8D7M12P2/PS2Recomp`, rev `a608ed1e161f60334a0cf3a80d1af3e54b692bd2` |
| Overlay | exactly the seven `git diff --name-only d1ba1d4 a608ed1` files, tar over `ssh bytesize`, no other source |
| Overlay Mac SHAs (2 reads each) | CMakeLists `b229b7ac…fddcf`, cpu_backend.h `0d0377ed…e3a46`, replay_core.h `d80f9af2…f9964`, cpu_backend.cpp `c762efd6…ec57f`, replay_core.cpp `c5fdaf64…f396c`, main.cpp `7ab53178…4c17bf`, replay_tests.cpp `db2e9c7c…9611ae` (`mac-overlay-pins.txt`) |
| Overlay WSL SHAs (2 reads each, post-transfer) | all seven equal the Mac reads (`overlay-sha-post.txt`, `source-gate.json`) |
| Prebuild source diff vs N8D7M1 | added 2 (`gs_replay_core.h/.cpp`), modified 5, removed 0; parallel [] jniLibs []; no `ps2xRuntime/src/runner` files; 345,799,259 B (`source-gate.json` PASS) |
| Postbuild source diff vs N8D7M1 | identical PASS, root 7,453,799,492 B (6.94 GiB < 10 GiB) (`source-gate-postbuild.json`) |
| Build | one `assembleRelease`, `BUILD SUCCESSFUL in 5m 18s`, 48 tasks, no repair (`build.txt`, `build-tail.txt`) |
| APK, WSL (2 reads) | `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512`, 153,753,116 B |
| APK, Mac (2 reads) | `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512`, 153,753,116 B |
| arm64 runner | `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d`, 139,512,968 B (new vs N8D7M1 `f3de999a…c1bf`) |
| arm64 Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`, 14,188,488 B (pin unchanged) |
| arm64 HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`, 7,112 B (pin unchanged) |
| Runner Build ID | `65ce162abca08d664223a362824b70c86aea6f4f` (new; N8D7M1 was `73291620f0c62fdc01ac0b603e9e5cca3114d0a5`) |
| Caps | WSL root 6.94 GiB (<10 GiB); Mac `N8D7M12P3` 147 MiB (<500 MiB); receipts 104 KiB (<512 KiB); global 148.5→148.6/200 GB |

## 2. Exact commands

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M12P3/preflight.sh > local/research/N8D7M12P3/preflight.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M12P3/prepare.sh > local/research/N8D7M12P3/prepare.txt 2>&1
# overlay exactly the seven Mac fork files via tar over ssh bytesize (two matching SHA reads each before/after)
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7M12P3/source_gate.py > local/research/N8D7M12P3/source-gate.json 2> local/research/N8D7M12P3/source-gate.err
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M12P3/build.sh > local/research/N8D7M12P3/build.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7M12P3/source_gate.py > local/research/N8D7M12P3/source-gate-postbuild.json 2> local/research/N8D7M12P3/source-gate-postbuild.err
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7M12P3/apk_gate.py > local/research/N8D7M12P3/apk-gate.json 2> local/research/N8D7M12P3/apk-gate.err
ssh bytesize 'wsl -d Ubuntu -- cat /home/brad/n8d7m12p3/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk' > /Users/brad/dev/ssx3-work/N8D7M12P3/app-release.apk
python3 local/research/N8D7M12P3/mac_apk_gate.py > local/research/N8D7M12P3/mac-apk-gate.json 2> local/research/N8D7M12P3/mac-apk-gate.err
python3 local/research/N8D7M12P3/check.py
```

`build.sh` is N8D7M1's command with root `n8d7m12p3`, preserving Java/SDK/Gradle
locations, external `/home/brad/n8b1/codegen-ssx3`, `-Pps2xGsShadowParallel=ON`,
new root's parallel-gs/jniLibs, five diagnostic defaults OFF, `--max-workers=4`,
and the N8D7M1 memory governor.

## 3. Seven-file overlay (vs N8D7M1)

```
  added:    ps2xRuntime/include/runtime/gs/gs_replay_core.h (new)
            ps2xRuntime/src/lib/gs/gs_replay_core.cpp (new)
  modified: ps2xRuntime/CMakeLists.txt
            ps2xRuntime/include/runtime/gs/gs_cpu_backend.h
            ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp
            ps2xRuntime/src/main.cpp
            ps2xTest/src/ps2_gs_replay_tests.cpp
  removed:  (none)
  parallel: []  jniLibs: []  ps2xRuntime/src/runner: absent
```

The pre-overlay tree copy proved **zero** noncache differences vs N8D7M1
(`prepare.txt`: all three `diff -rq` empty, `PRE_CANDIDATE_DIFFS_EMPTY`), then
exactly the seven `d1ba1d4..a608ed1` files were overlaid via tar. N8D7M1's
oracle backend (`ps2_gs_parallel_backend.cpp` `84a13a80…`) is preserved
untouched. Every overlay/header/codegen/Turnip/HAL pin was double-read
(`source-gate.json`, postbuild, `mac-overlay-pins.txt`,
`overlay-sha-post.txt`). `ps2xRecomp/src/runner/main.cpp` is identical tracked
tool source in both roots (`65d0813a…`, not generated guest code).

## 4. Package members and cache

| Artifact | Size (bytes) | SHA-256 (two reads each) | Status |
| --- | ---: | --- | --- |
| APK | 153,753,116 | `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512` | PASS (new) |
| arm64 runner | 139,512,968 | `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d` | PASS (new) |
| arm64 Turnip | 14,188,488 | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` | PASS (pin unchanged) |
| arm64 HAL shim | 7,112 | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | PASS (pin unchanged) |

Exactly these three native members, no x86. Runner Build ID
`65ce162abca08d664223a362824b70c86aea6f4f` is **new** (≠ N8D7M1).

Required packaged strings all present (23/23): `PS2X_GS_REPLAY_ONDEVICE`,
`PS2X_GS_REPLAY_CAPTURE`, `PS2XGSC1`, `GB4_REPLAY_SUMMARY`,
`PS2X_N8D7F_SELECTED_CAPTURE`, `PS2X_N8D7L_ORACLE`, `[n8d7f]`, `[n8d7l]`,
`vram_sha256=`, `input_sha256=`, `circuit_sha256=`, `input_circuit_equal=`,
`circuit_stage_equal=`, `PS2X_N8D5_TILE_CAPTURE`, `circuit1`,
`pre_deinterlace_merged`, `stage=final`, `control=`, `sampled_summary`,
`raw_summary`, `PNG write failed path=`, `oracle_controls=`,
`oracle_input_equal=`.

Sole arm64 CMake cache:
`/home/brad/n8d7m12p3/PS2Recomp/android/app/.cxx/RelWithDebInfo/4f434a1x/arm64-v8a/CMakeCache.txt`.
It records `PS2X_GS_SHADOW_PARALLEL=ON`, G43 source
`/home/brad/n8d7m12p3/parallel-gs`, external codegen
`/home/brad/n8b1/codegen-ssx3`, and `PS2X_BUILD_TEST`,
`PS2X_ENABLE_DIAG_TAPS`, `PS2X_ENABLE_RUNTIME_LOGS`,
`PS2X_ENABLE_AGRESSIVE_LOGS`, `PS2X_ENABLE_IOP_RPC_TRACE`,
`PS2X_ENABLE_DEBUG_UI` all **OFF**.

## 5. Build tail

```
> Task :app:mergeReleaseNativeDebugMetadata
> Task :app:assembleRelease

BUILD SUCCESSFUL in 5m 18s
48 actionable tasks: 48 executed
```

One `assembleRelease`, no repair loop. (`build.txt` has exactly one
`BUILD SUCCESSFUL` and no `FAILED`; `check.py` row `build_one_success_no_retry`.)

## 6. Caps

WSL root `/home/brad/n8d7m12p3` 7,453,799,492 B (6.94 GiB < 10 GiB). Mac scratch
`~/dev/ssx3-work/N8D7M12P3` 147 MiB (<500 MiB; APK 146.6 MiB). Receipt dir
104 KiB (<512 KiB). Global mini ssx3 internal usage 148.5 GB before, 148.6 GB
after (cap 200 GB). bytesize preflight `HEAVY_JOBS []`, `/dev/sdc` 756 G free.
`check.py` verdict **A** (10/10 rows, `check-result.json`/`result.json`).

## 7. Gaps

- Source/default-OFF path is statically gated; no runtime OFF-path or
  Turnip/HMI behavior is proved without a later Odin run.
- The APK stays outside git (private Mac scratch + WSL root).

## 8. Receipts

`preflight.sh`/`preflight.txt`, `prepare.sh`/`prepare.txt`,
`source_gate.py`/`source-gate.json`/`source-gate.err`,
`source-gate-postbuild.json`/`source-gate-postbuild.err`,
`build.sh`/`build.txt`/`build-tail.txt`, `apk_gate.py`/`apk-gate.json`/`apk-gate.err`,
`mac_apk_gate.py`/`mac-apk-gate.json`/`mac-apk-gate.err`,
`mac-overlay-pins.txt`, `overlay-sha-post.txt`, `check.py`/`check-result.json`/
`result.json`, `disk-budget-before.txt`/`disk-budget-after.txt`/`disk-budget.txt`.
