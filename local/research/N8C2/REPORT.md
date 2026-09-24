# N8C2 — app-local libhardware probe

Report-only continuation by Codex. Sources: [N8C2 brief](../../muse/prompts/N8C2.md), [continuation](../../muse/prompts/N8C2R.md), receipts here, and scripts/results in `~/dev/ssx3-work/N8C2/`. The orchestrator owns the verdict. No new build, device action, fork edit, or push.

## Source and build

| Item | Receipt-backed result |
| --- | --- |
| Pins | N8B1 `n8-turnip-apk` @ `17e90ded3689685ad359b76a9168c80a1f752e2d`; source tar SHA-256 `6d091b62c1152f1c68488b853c42654ccab1b57e39795feef09285778d42a6a6`; codegen register SHA `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`; G43 paraLLEl as N8B1; wrapper JAR `498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17`; Turnip `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`. `prepare.sh` checks input/copy pairs. |
| Diagnostic source | [hwcompat.c](hwcompat.c), SHA `f6eee805b2f426dc0edd867e42a887f1d3495df37154a842973e53be379e41a3` twice in [source-elf-sha.txt](source-elf-sha.txt), verified once locally here. Source header states MIT; constructor logs mapped path; the only exported function nulls a nonnull output and returns `-ENOENT`, with bounded call logging. |
| Shim command | `prepare.sh`: `aarch64-linux-android28-clang -std=c11 -O2 -fPIC -fvisibility=hidden -shared -Wl,-soname,libhardware.so -Wl,--no-undefined -o /home/brad/n8c2/jniLibs/arm64-v8a/libhardware.so /home/brad/n8c2/hwcompat.c -llog -ldl`. Staged ELF SHA `d7add7e8e2e31f3c49b83941c6686fa66ab3d844c650e8d70c93b026f90cafa0` twice. [shim-elf.txt](shim-elf.txt) shows SONAME `libhardware.so`, public NDK `DT_NEEDED` only `liblog.so`, `libdl.so`, `libc.so`, and sole defined dynamic export `hw_get_module`. |
| Build | Budget 2/2 used per continuation brief: one missing-wrapper packaging repair, then `assembleRelease` succeeded in 5m 29s, 48 tasks ([build-tail.txt](build-tail.txt)). First failed build log/command is absent from bounded receipts, so the attempt history is brief-reported. |
| Exact final Gradle command | From `/home/brad/n8c2/PS2Recomp/android`, with `JAVA_HOME=/home/brad/n2/toolchain/jdk-17`, `ANDROID_HOME=ANDROID_SDK_ROOT=/home/brad/n2/toolchain/android-sdk`, `GRADLE_USER_HOME=/home/brad/n2/gradle-home`: `./gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/n8b1/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=/home/brad/n8b1/parallel-gs -Pps2xJniLibsDir=/home/brad/n8c2/jniLibs --max-workers=4 --console=plain --warning-mode=none` (`build.sh`). |
| APK gate | [apk-gate.json](apk-gate.json): pass, APK SHA `86ee7b723979c6727f03aaeaa031e9bd6dd3481a640af3b1eb06fd41e6fc7640` twice. Only three arm64 native members below, no x86. RelWithDebInfo cache `x4p4f656/arm64-v8a`: `PS2X_ENABLE_DIAG_TAPS`, `PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`, `PS2X_ENABLE_IOP_RPC_TRACE`, `PS2X_ENABLE_DEBUG_UI` all `OFF`. |

| APK member | SHA-256 (each member twice) | Bytes |
| --- | --- | ---: |
| `libhardware.so` | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | 7,112 |
| `libps2EntryRunner.so` | `760c6f4ffe318ee987e2b5262c1a8d3950d965a5e91e3e95d842d4c4ebe18a83`; Build ID `df500211e9272b1849ac25be3ae58fc7e693ef88` | 139,474,968 |
| `libvulkan_freedreno.so` | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` = pin | 14,188,488 |

Staged shim and APK member SHAs differ. [shim-member-elf.txt](shim-member-elf.txt) has identical dynamic-section/symbol text to the staged ELF receipt. The build tail includes `stripReleaseDebugSymbols`, but the receipts do not directly establish which package transformation changed the bytes. Neither ELF is committed.

## One Odin launch

Exact device commands in `~/dev/ssx3-work/N8C2/launch.py`: `adb -s 622c49b1 get-state`, `shell cat /data/local/tmp/mg/LEASE`, `shell dumpsys window policy`, `shell dumpsys battery`; lease claim; `install -r ~/dev/ssx3-work/N8C2/app-release.apk`; two device `sha256sum` reads each of installed `base.apk`, `files/SLUS_207.72`, `files/SSX3.iso`; empty `files/mc0` check; env push; preflight again; `shell am start -n com.ps2x.runner/android.app.NativeActivity`; bounded log and three `screencap -p`/pull/SHA pairs; `shell am force-stop com.ps2x.runner` and lease release. Event order: [driver.log](driver.log) and work-dir `result.json`.

| Ordered stage | Observation |
| --- | --- |
| Preflight/install | Odin connected; lease `LEASE_FREE N8C1 done`; keyguard `showing=false`; battery 100%, status 5. Claimed `N8C2 one-launch`; install `Success`. Installed APK matched `86ee7b72…fc7640` twice; stock ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` twice; ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` twice. Card empty. [ps2x.env](ps2x.env) SHA `d2ab46b4c725b2a7ecca2c50ac26b9184d0b10f8d4d62629afde6a9c038404a5`; parallel/Turnip, dev movie bypass, I26-FAST vsync pad route. Prelaunch keyguard/battery/owned lease rechecked. |
| Loader/HAL, PID 13597 | [Same-PID log](logcat-pid.txt): app-local shim mapped from installed APK; HMI mapped bundled Turnip from same APK; HAL `open` rc=0, nonnull device, `close`/`enum_ext`/`create_inst`/`get_proc` addresses. Four `hw_get_module` calls requested `gralloc`, output null, return `-2` (`-ENOENT`). |
| Backend/progress | Same PID: `[gs:parallel] init ok`; periodic `gif=21209`, `presents=300`, later `gif=643992`, `presents=1500`. BACK sent for USB dialog. Menu screenshot tick 809; race screenshot ticks 1844 and 2087; stopped at >=2050 after 122.4 s. Active counters do not establish correct visible composite. |
| Cleanup | Force-stop left PID absent; lease read back `LEASE_FREE N8C2 done`. One install and one launch only. |

| Viewed SHA-paired PNG | View |
| --- | --- |
| [menu-tick809.png](menu-tick809.png), `213336f44f7acf95a4ebe7fc864dce4671881a63eb45a73caedb2479c6b13f7a` | Mostly black, broad blue striped blocks and scattered fragments; no readable menu. |
| [race1-tick1844.png](race1-tick1844.png), `cad5e4b9da31f5a54669b919c200049ff185da4f0f8671fa85718fe03bf8fd35` | Mostly black, a few striped and pale fragments; no usable stock race frame. |
| [race2-tick2087.png](race2-tick2087.png), `953b40a0f22ba1a906e4bbbbb14865e62182b0f5fa88d8635145335dfe8aa356` | Mostly black, sparse dark striped rectangles; no usable stock race frame. |

## Bounds and gaps

| Item | Status |
| --- | --- |
| Stage distinction | App-local dependency loaded, bundled HMI/HAL and parallel backend initialized; visible-frame gate failed in all three viewed images. Composite defect cause is unproved. |
| Vulkan identity | No Vulkan device/API/driver identity logged. Raylib's OpenGL Adreno 830 line does not prove Turnip Vulkan identity. Expected G43 API 1.4.359 / driver 26.2.99 unverified here. |
| Budgets | One launch within 600 s; three images total 267,913 bytes (<10 MiB); bounded local receipts ~328 KiB (<32 MiB text); local work directory ~147 MiB (<1 GiB Mac). Bytesize scratch total and first failed build log absent; 20 GiB bytesize cap cannot be independently audited from bounded receipts. |
| Speed | Diagnostic probe with vsync progress logging/image capture; no speed measurement or speed claim. |
