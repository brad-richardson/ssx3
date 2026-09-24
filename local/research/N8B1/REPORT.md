# N8B1 — Android Turnip APK source/build gate

Worker: Codex. Brief: `local/muse/prompts/N8B1.md`. The orchestrator decides the gate. No Odin use or push.

## Pin and transfer table

| Input | Mac pin / two reads | bytesize transfer / two reads |
| --- | --- | --- |
| Fork `fork/ssx3` | Remote `git ls-remote` and local ref both `4f932166c773e04522ffa007228670894f8b4f44`; local `n8-turnip-apk` worktree created there | Attempt-1 source archive SHA-256 `54f0bdad2d219e5141fa1bb9a721b2bdea789ba8b6437c53881a68fef79f5055` ×2 on Mac and bytesize; repaired/final source archive `6d091b62c1152f1c68488b853c42654ccab1b57e39795feef09285778d42a6a6` ×2 on Mac and bytesize (`~/n8b1/inputs/PS2Recomp-repair.tar`) |
| Canonical external codegen | 9,457 files; `register_functions.cpp` SHA-256 `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` ×2; tar stream `1fb4585de96bf00d3dbcc7769080d4094d73e918c5dffaf73a83a2817d47dcb7` ×2 | Same tar SHA ×2; extracted register SHA matches and file count 9,457; streamed directly from canonical Mac directory, no Mac copy |
| G43 paraLLEl/Granite working copy | Main HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`, tracked diff SHA `86e42c59516d0cc81b869e1e3cce342c7b21d6d7bfd407553bd2219efe16e0f8` ×2; Granite HEAD `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5`, tracked diff SHA `8ffa13bff31e9d028c59c9b5b145e5a37c36ff64f44f3b25c554eb7622ab7934` ×2; tar stream `af12671af90b5dd4c3a9a3e012babb5a002bb5495f80f0f25ed43741c53a14cd` ×2 | Same tar SHA ×2; extracted `~/n8b1/parallel-gs`. Main diff SHA includes later G43 working-copy content and differs from N8A's earlier hunk receipt. |
| N7 Android source | bytesize `n7-android` `81aa92d12341074927c332ce9305c7fb28f57b01` | Env parser/runtime/test read from that revision; no N7 branch cherry-pick |
| Gradle wrapper for bytesize build | N7's existing bytesize wrapper was outside Git | `gradle-wrapper.jar` source/copy SHA-256 `498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17`, copied into the source snapshot's `android/gradle/wrapper` after extraction; matching destination read twice |
| Turnip v36 | `libvulkan_freedreno.so` SHA-256 `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` ×2; 14,188,488 bytes | Same SHA ×2 at `~/n8b1/jniLibs/arm64-v8a/libvulkan_freedreno.so`; driver outside Git |

## Source and host-test table

| Check | Result |
| --- | --- |
| Source scope | `android/app/build.gradle`; `ps2xRuntime/include/ps2_android_env.h`; `ps2xRuntime/src/lib/ps2_android_runtime.cpp`; `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp`; `ps2xTest/CMakeLists.txt`, `src/main.cpp`, `src/ps2_android_env_tests.cpp`. No scheduler edits. |
| N7 pieces | External codegen property, Android static env initializer/parser and four-case unit test, arm64-only ABI. Existing test registrations preserved. |
| In-process Turnip path | Exact `PS2X_GS_TURNIP=1` on Android requests basename `dlopen`, `dlsym(HMI)`, `dladdr(HMI)`, HAL `open("vulkan0")`, and a non-null HAL proc address for Granite. LP64 module/device offset assertions use G43's corrected `reserved[12]`. Requested failure returns false, with no system-loader retry. Other values and non-Android retain default loader. |
| Host suite | `cmake -S …/PS2Recomp -B …/host-build -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF`; `cmake --build …/host-build --parallel 8 --target ps2x_tests`; from fork worktree root `…/host-build/ps2xTest/ps2x_tests`: **585/585 passed**, 0 failed. Receipts `~/dev/ssx3-work/N8B1/host-{configure,build,tests}.log`. |

## APK build/cache gate

| Item | Observation |
| --- | --- |
| Attempt 1 | `assembleRelease` succeeded in 10m 33s, 48 Gradle tasks, producing APK `a4dbabcb9b30aba8274ce8c170d867f0285ab77f47d61c4a754e9399517f8d5d`. Its package member gate passed, but the final CMake cache retained `PS2X_ENABLE_IOP_RPC_TRACE=ON` and `PS2X_ENABLE_DEBUG_UI=ON`; the requested diagnostics-off gate failed. APK and gate JSON are preserved as `~/n8b1/attempt1.apk` and `apk-gate1.json` on bytesize. |
| One named repair / attempt 2 | Added explicit `-DPS2X_ENABLE_IOP_RPC_TRACE=OFF` and `-DPS2X_ENABLE_DEBUG_UI=OFF` to Android Gradle CMake arguments. From source snapshot `6d091b62…`, `assembleRelease` succeeded in 5m 47s, 48 tasks (11 executed, 37 up-to-date). This exhausted the 2/2 APK build budget; no other source change or tuning. |
| Final CMake flags | `CMAKE_BUILD_TYPE=RelWithDebInfo` under Gradle `assembleRelease`; native cache `3a5j4t6h/arm64-v8a`. `PS2X_GS_SHADOW_PARALLEL=ON`; `PS2X_PARALLEL_GS_SOURCE_DIR=/home/brad/n8b1/parallel-gs`; `PS2X_GAME_CODEGEN_DIR=/home/brad/n8b1/codegen-ssx3`; `PS2X_ENABLE_DIAG_TAPS=OFF`, `PS2X_ENABLE_RUNTIME_LOGS=OFF`, `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`, `PS2X_ENABLE_IOP_RPC_TRACE=OFF`, `PS2X_ENABLE_DEBUG_UI=OFF`. Full PS2X cache excerpt: `~/dev/ssx3-work/N8B1/cache-flags.txt`. |
| Error tail | No compile, link, or packaging error in final build. Bounded final tail `~/dev/ssx3-work/N8B1/assembleRelease-tail.txt`; complete 31,797-byte bytesize log `~/n8b1/assembleRelease.log`. |

Exact build command, from bytesize `/home/brad/n8b1/PS2Recomp/android` with `JAVA_HOME=/home/brad/n2/toolchain/jdk-17`, `ANDROID_HOME=ANDROID_SDK_ROOT=/home/brad/n2/toolchain/android-sdk`, and `GRADLE_USER_HOME=/home/brad/n2/gradle-home`:

```sh
./gradlew assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/n8b1/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=/home/brad/n8b1/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/n8b1/jniLibs \
  --max-workers=4 --console=plain --warning-mode=none
```

## APK member, SHA, build-ID gate

| Item | Observation |
| --- | --- |
| Final APK | bytesize `~/n8b1/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk`, 153,687,506 bytes; SHA-256 `1096a28e2e343fbcfc1d28390ea72a8e3d2aee32f3c40b81102e773c50b190da` on two independent reads. |
| Runner member | `lib/arm64-v8a/libps2EntryRunner.so`, uncompressed 139,474,968 bytes; SHA-256 `cdbaa6dd6eaf77a9026fb1fc5a291c15054f4d396e44b37ee3655705d10eb033` on two APK-member reads and two extracted-file reads; ELF Build ID `28340bbe3652b251a6ecda201cf6ae01f6550add`. |
| Turnip member | `lib/arm64-v8a/libvulkan_freedreno.so`, uncompressed 14,188,488 bytes; SHA-256 `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` on two APK-member reads, equal to the pinned input. |
| ABI / HMI link | Exactly those two `lib/arm64-v8a/` members and no `lib/x86_64/` member. Final native build produced `ps2_gs_parallel_backend.cpp.o` (813,896 bytes) in `ps2_gs_shadow`; packaged runner contains the exact Turnip request, HMI mapped-path, HAL-open and failure strings plus dynamic `dlopen`, `dlsym`, `dladdr` symbols. This is compile/link evidence for the in-process loader, not a runtime driver-identity observation. JSON gate receipt: `~/dev/ssx3-work/N8B1/apk-gate.json` (same as bytesize `~/n8b1/apk-gate.json`). |

## Runner guard, commits, and budgets

| Check | Result |
| --- | --- |
| Runner-dir guard | `git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner` returned 0 with empty diff before each source commit and after final HEAD. No guest codegen, Turnip binary, APK, or source tarball is tracked in the fork. |
| Local fork commits | `a4babc6dfa682da2f32c59c6540368b55b608be3` source candidate; `17e90ded3689685ad359b76a9168c80a1f752e2d` diagnostics flag repair, branch `n8-turnip-apk`. Both `[N8B1]` with `Orchestrated-By: Codex`; no push. |
| Host suite / bytes | One host suite: 585/585. bytesize N8B1 scratch 14 GiB of 20 GiB; Mac N8B1 scratch 1.3 GiB of 5 GiB; global internal usage 113.3/200 GB, disk-budget check exit 0. New Mac text receipts total 162,856 bytes, bytesize final Gradle/governor logs 33,420 bytes, below 32 MiB. |

## Source-only gaps and Part-2 launch inputs

App namespace loading and driver identity are unproved until an authorized one-launch Part 2. The Part-2 inputs are the gated APK, external `ps2x.env` with `PS2X_GS_BACKEND=parallel` and `PS2X_GS_TURNIP=1`, stock ISO/ELF, I26-FAST vsync pad route, and dev-only `PS2X_SKIP_MOVIE=1`. Require same-PID HMI mapped path, HAL ops, Granite Turnip identity, backend init/counters, and a visible race frame. No device action in N8B1.
