# N8D7H — isolated Android selected-input probe package

Worker receipt. Source/binary packaging gate only. No Odin install/launch, no
app run, no game boot, no replay, no push. Package contents are proved; device
behavior remains unobserved, so no device-cause verdict follows.

Goal: one arm64 APK carrying the Mac-calibrated default-OFF
`PS2X_N8D7F_SELECTED_CAPTURE` probe, for a later same-Odin-frame V/S/T test.
The Odin stream is not assumed byte-identical to the Mac stream.

## Source pins and double SHA pairs

Overlay sources (Mac, read from the N8D7F private worktree):

| Role | Path | SHA-256 (two reads) |
| --- | --- | --- |
| Fork backend | `~/dev/ssx3-work/N8D7F/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f` |
| G43 interface | `~/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_interface.hpp` | `3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d` |
| G43 renderer hpp | `~/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_renderer.hpp` | `fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a` |
| G43 renderer cpp | `~/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_renderer.cpp` | `85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e` |

Canonical pins after overlay (WSL, each read twice):

| Pin | WSL path | SHA-256 | Status |
| --- | --- | --- | --- |
| Fork backend | `.../N8D7H/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f` | PASS |
| G43 interface | `.../N8D7H/parallel-gs/gs/gs_interface.hpp` | `3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d` | PASS |
| G43 renderer hpp | `.../N8D7H/parallel-gs/gs/gs_renderer.hpp` | `fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a` | PASS |
| G43 renderer cpp | `.../N8D7H/parallel-gs/gs/gs_renderer.cpp` | `85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e` | PASS |
| Writer | `.../N8D7H/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp` | `358d726bf39e319b906e7e15407e1bf361cd2cdbdd8e79d4a96b25a9588c3f96` | PASS |
| Shader header | `.../N8D7H/parallel-gs/gs/n8d5_tile_spirv.hpp` | `19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9` | PASS |
| Codegen | `/home/brad/n8b1/codegen-ssx3/register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` | PASS |
| Turnip source | `.../N8D7H/jniLibs/arm64-v8a/libvulkan_freedreno.so` | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` | PASS |
| HAL shim source | `.../N8D7H/jniLibs/arm64-v8a/libhardware.so` | `d7add7e8e2e31f3c49b83941c6686fa66ab3d844c650e8d70c93b026f90cafa0` | PASS |

## Source diff table vs N8D6B

N8D7H is an `rsync` copy of the N8D6B WSL snapshot (excluding `.cxx`, `build`,
`.gradle`, runner) that proved **zero differences** before overlay
([prepare.txt](prepare.txt)), then exactly four files were overlaid.

| Tree | Path | N8D6B before | N8D7H after | Expected |
| --- | --- | --- | --- | --- |
| fork | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | `e730b9f05994c9887f9c5605f9a34b2fe6f4ac1c239bb964f17cdfc515b1fb5c` | `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f` | differs |
| parallel | `gs/gs_interface.hpp` | `4c78cf9d90e0dfa313275aa3417b7d1a8e0c631f60e94be51a17772d2d44639c` | `3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d` | differs |
| parallel | `gs/gs_renderer.hpp` | `8f511a44d66f4bc7e9d238e48964ab88e4dfbcdb63544ce1a47f4cae0a0d59b5` | `fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a` | differs |
| parallel | `gs/gs_renderer.cpp` | `3322481421db8d0c182cb7916d826fde5853425cae2385828587507863988534` | `85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e` | differs |
| jniLibs | all files | — | — | identical |

`source_gate.py` enforced the file-set match and exactly
`{'fork': [backend], 'parallel': [3 G43 files], 'jniLibs': []}`
([source-gate.json](source-gate.json)); the same gate re-passed after the build
([source-gate-postbuild.json](source-gate-postbuild.json)).

Mac fork runner guard: fork rev `0678dd96e496a65bbb09af5467f17240ae2bbdc8`,
`git diff --stat 14b1e5cb -- ps2xRuntime/src/runner` **empty**
([mac-fork-guard.txt](mac-fork-guard.txt)).

## Build

| Check | Required | Observed |
| --- | --- | --- |
| Host jobs | No other heavy bytesize job | PASS; `HEAVY_JOBS []` ([preflight.txt](preflight.txt)) |
| Build | One arm64 `assembleRelease`, five OFF flags, same codegen/Turnip/HAL/Gradle | PASS; `BUILD SUCCESSFUL in 5m 17s`, 48 tasks, no compile repair ([build-tail.txt](build-tail.txt)) |
| Postbuild isolation | Same source gate passes | PASS; [source-gate-postbuild.json](source-gate-postbuild.json) |

Build tail:

```
> Task :app:mergeReleaseNativeDebugMetadata
> Task :app:assembleRelease

BUILD SUCCESSFUL in 5m 17s
48 actionable tasks: 48 executed
```

## Package member/flags table

| Artifact | Size (bytes) | SHA-256, two reads each | Status |
| --- | ---: | --- | --- |
| APK, WSL | 153,736,732 | `86fca856b6de0148aea24fb53b63119e4ec1382eb9cf3490d2ce0db2031df14a` | PASS |
| APK, Mac | 153,736,732 | `86fca856b6de0148aea24fb53b63119e4ec1382eb9cf3490d2ce0db2031df14a` | PASS |
| arm64 runner | 139,494,296 | `8e32841d8a6fff8f45862ca806c74ed92ec31469638f71281f9139e2fc32c683` | PASS |
| arm64 Turnip | 14,188,488 | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` | PASS (pin unchanged) |
| arm64 HAL shim | 7,112 | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | PASS (pin unchanged) |

The APK has exactly these three native members with no x86
([WSL gate](apk-gate.json), [Mac gate](mac-apk-gate.json)).

Runner Build ID: `1c1bce61bfe6bc21cd2ac86d473da323f480eb7b`.

Required packaged strings all present: `PS2X_N8D7F_SELECTED_CAPTURE`, `[n8d7f]`,
`vram_sha256=`, `input_sha256=`, `circuit_sha256=`, `input_circuit_equal=`,
`circuit_stage_equal=`, `PS2X_N8D5_TILE_CAPTURE`, `circuit1`,
`pre_deinterlace_merged`, `stage=final`, `control=`, `sampled_summary`,
`raw_summary`, `PNG write failed path=`.

Sole arm64 CMake cache:
`/home/brad/n8d7h/PS2Recomp/android/app/.cxx/RelWithDebInfo/v6d6b611/arm64-v8a/CMakeCache.txt`.
It records shadow paraLLEl ON, source `/home/brad/n8d7h/parallel-gs`, external
codegen `/home/brad/n8b1/codegen-ssx3`, and `PS2X_ENABLE_DIAG_TAPS`,
`PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`,
`PS2X_ENABLE_IOP_RPC_TRACE`, `PS2X_ENABLE_DEBUG_UI` all OFF.

## Exact commands

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7H/preflight.sh > local/research/N8D7H/preflight.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7H/prepare.sh > local/research/N8D7H/prepare.txt 2>&1
# overlay four files (Mac -> WSL), e.g.
ssh bytesize 'wsl -d Ubuntu -- bash -c "cat > /home/brad/n8d7h/parallel-gs/gs/gs_interface.hpp"' < /Users/brad/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_interface.hpp
ssh bytesize 'wsl -d Ubuntu -- bash -c "cat > /home/brad/n8d7h/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp"' < /Users/brad/dev/ssx3-work/N8D7F/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7H/source_gate.py > local/research/N8D7H/source-gate.json
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7H/build.sh > local/research/N8D7H/build.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7H/source_gate.py > local/research/N8D7H/source-gate-postbuild.json
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7H/apk_gate.py > local/research/N8D7H/apk-gate.json
ssh bytesize 'wsl -d Ubuntu -- cat /home/brad/n8d7h/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk' > /Users/brad/dev/ssx3-work/N8D7H/app-release.apk
python3 local/research/N8D7H/mac_apk_gate.py > local/research/N8D7H/mac-apk-gate.json
```

`build.sh` is the N8D6B command with root `n8d7h`, preserving the exact
codegen/Turnip/HAL/Gradle arguments and the five OFF defaults.

## Caps

WSL root `/home/brad/n8d7h` 7,590,835,753 bytes (<10 GiB). Mac scratch
`~/dev/ssx3-work/N8D7H` 147 MiB (<500 MiB). Receipt dir 64 KiB (<8 MiB).
Global mini ssx3 internal usage 141.3/200 GB before and after the Mac write.

## Gaps

The APK remains outside Git at
`/home/brad/n8d7h/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk`
and `/Users/brad/dev/ssx3-work/N8D7H/app-release.apk`. The four overlay source
SHAs were verified twice on Mac before transfer and twice on WSL after overlay;
the packaged runner SHA and Build ID are new and were not compared to any prior
device artifact. No Odin install/launch, app run, game boot, replay, push, or
device-cause verdict. Package contents are proved; device behavior remains
unobserved.
