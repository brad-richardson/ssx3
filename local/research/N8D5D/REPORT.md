# N8D5D — Android tile-probe package gate

Worker receipt. Build and package only; no Odin action or device verdict.

## Source and package gates (recorded before build)

| Gate | Required observation | Result |
| --- | --- | --- |
| Candidate backend | Mac N8D5L `ps2_gs_parallel_backend.cpp` commit `ab8155bbcbbdd478d17f2cd90a2feff3eb9a865b`, SHA-256 `4e3efc51d8d104ab5d3c537076e85c6cfcd8344c8e6c147de02f5a5015c8f1e5`, two reads on each host | PASS; Mac and WSL each read twice, matching [source-gate.json](source-gate.json) |
| Shader header | Mac N8D5B `gs/n8d5_tile_spirv.hpp` SHA-256 `19b9ba5fc747d8fcb70d712b86bd5738c64424d4b5ed58219f71bac9`, two reads on each host | PASS; Mac and WSL each read twice |
| Source isolation | Private N8D5D source snapshot matches N8B1 except those two named files; codegen, G43 and N8D3 `jniLibs` remain separate inputs | PASS; only backend and header differ, before and [after](source-gate-postbuild.json) build |
| Build | One arm64 `assembleRelease`; shadow paraLLEl ON; diagnostics, runtime/aggressive logs, IOP RPC trace and debug UI OFF | PASS; one build, 5m 56s, 48 tasks. [build-tail.txt](build-tail.txt) |
| APK archive | Two matching SHA-256 reads on WSL and Mac | PASS; `a6a0c3793e31310fc8794e7a0d6b6cc282e5060d59cfe116b919236b9f50612a` on all four reads |
| Package members | Exactly runner, Turnip and HAL shim under `lib/arm64-v8a/`; no x86; each member SHA-256 twice | PASS; [apk-gate.json](apk-gate.json) |
| Turnip and shim | Turnip `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`; stripped shim `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | PASS; packaged member SHA pairs equal pins |
| Runner | Build ID and packaged `PS2X_N8D5_TILE_CAPTURE`, `control=`, `sampled_summary`, and `raw_summary` strings | PASS; Build ID `ab1bdc3b61faf1fe99cd5844e8c90ffaee8f54f6`, all strings present |
| Fork runner guard | Mac fork diff against `14b1e5cb` empty | PASS; N8D5L fork at `ab8155b` |

## Private snapshot preparation

| Item | Observation |
| --- | --- |
| WSL scratch | `/home/brad/n8d5d/`: 379 MiB; `PS2Recomp` 23 MiB, `parallel-gs` 344 MiB, `jniLibs` 14 MiB. Inputs `/home/brad/n8b1/` and `/home/brad/n8d3/` were read only. |
| Fork snapshot | `rsync -a` from N8B1 with `.cxx`, `build`, `.gradle`, and `ps2xRuntime/src/runner/` excluded. `diff -rq` against N8B1 with those exclusions yielded no differences. Backend remains base SHA `38b7a5afe495dee479c3532e4b0f4ca3972f61ae3764710d94fb89609795e519`. |
| ParaLLEl snapshot | `rsync -a` from N8B1, excluding build caches; matching `diff -rq`. `gs_interface.cpp` SHA `5ccc962f080bbb1e1fc637155799823008409f2fd3b283d1f2f0e9d6eb5077f4`, `CMakeLists.txt` SHA `7430d2be046c511d16a57fdeb3eb0968ea03d5abffd3397e2628f2c7a539150a`, Granite `shader.cpp` SHA `7ea802a0ff030f8b5fffc637a0e6bd9aa701d2e987e6650c8d765ab4176f08a1`; all match Mac N8D5B. |
| Package input snapshot | `jniLibs` copied from N8D3 with matching `diff -rq`. Input Turnip SHA `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` twice. Input `libhardware.so` SHA `d7add7e8e2e31f3c49b83941c6686fa66ab3d844c650e8d70c93b026f90cafa0` twice; N8D3's stripped package SHA is checked after build. |
| External codegen | N8B1 `register_functions.cpp` SHA `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` twice; remains external. |
| Host contention | No Gradle, Ninja, clang, or PCSX2 process found in WSL `/proc` at preparation check. |
| Runner guard | Mac N8D5L fork `ab8155bbcbbdd478d17f2cd90a2feff3eb9a865b`; `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty. |
| Mac disk | Internal ssx3 usage 134.4 GiB / 200 GB cap before preparation; N8D5D Mac scratch 8 KiB. |

## APK handoff table

| Artifact | Size | SHA-256 (two reads) |
| --- | ---: | --- |
| APK, WSL and Mac | 153,720,348 bytes | `a6a0c3793e31310fc8794e7a0d6b6cc282e5060d59cfe116b919236b9f50612a` |
| `lib/arm64-v8a/libps2EntryRunner.so` | 139,482,472 bytes | `6a93af327b3cb1c5ebd9b3b81dc68ae1eb5e259633c9c61b78a82ba06428d162` |
| `lib/arm64-v8a/libvulkan_freedreno.so` | 14,188,488 bytes | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` |
| `lib/arm64-v8a/libhardware.so` | 7,112 bytes | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` |

APK retained outside Git at `/home/brad/n8d5d/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk` and `/Users/brad/dev/ssx3-work/N8D5D/app-release.apk`. [mac-apk-hashes.txt](mac-apk-hashes.txt) records the two Mac reads. No x86 member was present. The runner SHA was also checked twice after extraction; its Build ID and strings are in [apk-gate.json](apk-gate.json).

## Build and bounds

The single `assembleRelease` used JDK 17, Android SDK and Gradle home under `/home/brad/n2/`, external N8B1 codegen, private N8D5D paraLLEl and `jniLibs` snapshots, and N8B1's memory governor. Its arm64 `RelWithDebInfo` CMake cache is `/home/brad/n8d5d/PS2Recomp/android/app/.cxx/RelWithDebInfo/4k53s4a1/arm64-v8a/CMakeCache.txt`: `PS2X_GS_SHADOW_PARALLEL=ON`, source path `/home/brad/n8d5d/parallel-gs`, codegen path `/home/brad/n8b1/codegen-ssx3`, and all five named diagnostics/UI flags `OFF`. [build.sh](build.sh), [apk_gate.py](apk_gate.py) and [apk-gate.json](apk-gate.json) carry the command and exact checks. There was no build repair retry.

Private WSL scratch was 7.2 GiB (<10 GiB); Mac scratch 148 MiB (<500 MiB); text receipts under 36 KiB (<8 MiB); global mini ssx3 usage 136.0 GB (<200 GB). The source-gate script initially used the wrong `diff -rq` text format for an added file; its assertion was corrected before the successful source check and before the build. No source mismatch was observed. No auto-review issue, Odin install/launch, bytesize game/emulator boot, or push occurred.

## Exact commands

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D5D/prepare.sh
ssh bytesize 'wsl -d Ubuntu -- tee /home/brad/n8d5d/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp' < ~/dev/ssx3-work/N8D5L/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp > /dev/null
ssh bytesize 'wsl -d Ubuntu -- tee /home/brad/n8d5d/parallel-gs/gs/n8d5_tile_spirv.hpp' < ~/dev/ssx3-work/N8D5B/parallel-gs/gs/n8d5_tile_spirv.hpp > /dev/null
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D5D/source_gate.py > local/research/N8D5D/source-gate.json
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D5D/build.sh
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D5D/apk_gate.py > local/research/N8D5D/apk-gate.json
ssh bytesize 'wsl -d Ubuntu -- cat /home/brad/n8d5d/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk' > ~/dev/ssx3-work/N8D5D/app-release.apk
shasum -a 256 ~/dev/ssx3-work/N8D5D/app-release.apk ~/dev/ssx3-work/N8D5D/app-release.apk
```

The Codex orchestrator paused transfer and build while it added bounded summary lines and ran the Mac validation. It reported the N8D5L PASS in [its report](../N8D5L/REPORT.md) and then released this build. The APK is a package result only; device behavior remains for the orchestrator's later gate.
