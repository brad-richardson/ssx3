# N8D3 — raw/backend/frontend race comparison

One isolated source candidate, one Android APK build, and one Odin install/launch. This is an observation table for the orchestrator; it does not assign a renderer cause.

## Pins and bounded source edit

| Item | Receipt |
| --- | --- |
| Source base | N8D1 non-git WSL copy `/home/brad/n8d1/`; backend source SHA-256 `38b7a5afe495dee479c3532e4b0f4ca3972f61ae3764710d94fb89609795e519`. [source-hashes.json](source-hashes.json) |
| N8D3 source | Fresh `/home/brad/n8d3/`, copied without `.cxx`, `build`, `.gradle`, or `ps2xRuntime/src/runner/`. Only `ps2_gs_parallel_backend.cpp` differs from N8D1; SHA-256 `63b5cffdf42b0076e0b929123b446682998782f06a0e459cf41cbf7de3bf572f` twice. [prepare.py](prepare.py), [source.diff](source.diff), [source-compare.txt](source-compare.txt) |
| Diagnostic | Default OFF. `PS2X_N8D3_RAW_CAPTURE=1` captures only backend request tick 2050. It writes raw mapped bytes before the 640-stride backend copy, then packed valid bytes and metadata with bounded binary writes and error status. N8D1's frontend PNG path remains unchanged. |
| APK | SHA-256 `3970011d360b86a3f93f170df11e5964e2b467f01e7351c2cd1610b615b885be` twice in WSL and twice on Mac. [apk-gate-output.json](apk-gate-output.json), [local-apk-hashes.txt](local-apk-hashes.txt) |
| Arm64 package | Exactly `libps2EntryRunner.so` SHA `3628e772505d3329575ffece647a5840e09580b254137872e624ae7f7dbe6277`, Build ID `06ad52c140239d9e813a41aeecdb65cc88a48b56`; bundled Turnip SHA `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`; shim SHA `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`. All members read twice. No x86 members. |
| Build flags | `PS2X_ENABLE_DIAG_TAPS`, `PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`, `PS2X_ENABLE_IOP_RPC_TRACE`, `PS2X_ENABLE_DEBUG_UI`: all `OFF` in arm64 CMake cache. No Turnip/shim replacement. |

The N8D1 WSL source confirms the pipeline: `ps2_gs_parallel_backend.cpp` maps `shot.image` and copies valid rows into 640-stride `out.pixels`; `gs_frontend.cpp` repacks the latched frame; `ps2_runtime.cpp` dumps that packed frame before `UpdateTexture`. The Vulkan header in pinned `parallel-gs` declares format value 37 as `VK_FORMAT_R8G8B8A8_UNORM`; images here are decoded in **RGBA** order. The edit is limited to the backend file. It uses the N8D1 governor, external codegen and paraLLEl source, and the N8D1 build properties.

## One Odin race run

[launch.py](launch.py) installed the APK, double-read installed APK/ELF/ISO SHAs, checked empty `mc0`, keyguard `showing=false`, battery 100% and full/AC, then launched parallel/Turnip with dev movie bypass and I26-FAST vsync pad script. [ps2x.env](ps2x.env) uses `PS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999` so the unused targets cannot consume the frontend PNG slots. The device lease was `N8D3 one-launch`. Same-PID [logcat](logcat-pid.txt) has the tick-2050 backend and frontend markers; the latest logged guest tick at stop was 2052. The run stopped at 116.157 s after launch, then force-stopped the app. PID was absent; lease read back `LEASE_FREE N8D3 done`. Total launch-to-exit was 117.9 s. [driver.log](driver.log), [result.json](result.json).

| Stage | Tick / FBP / image | Observed image and byte check | Device + local SHA reads |
| --- | --- | --- | --- |
| Raw mapped `shot.image` | 2050 / 112 / 512×448 RGBA8 (`format=37`) | [raw-rgba.png](raw-rgba.png): mostly black with top HUD, a pale right block, and sparse lower fragments. Raw buffer: 917,504 bytes. | `a7646a1b7a44f7085c42f2d813730fc24d87799bc64a742608b9f03962a1ad9c`, four matching reads in [result.json](result.json) |
| Backend `out.pixels` valid rows | 2050 / 112 / 512×448, 640-pixel source stride | [backend-rgba.png](backend-rgba.png): same visible fragments. Packed buffer: 917,504 bytes; **448/448 rows byte-for-byte equal** to raw valid rows. | Same SHA as raw; four matching reads |
| Frontend pre-`UpdateTexture` | 2050 / display/source FBP 112 / 512×448 | [frontend.png](frontend.png): same visible fragments. Decoded RGBA bytes: **917,504/917,504 equal** to raw and packed; zero differing pixels. [metadata](upload-0.txt) | PNG SHA `98ac0986cb6dd1307fea5ea1e88c04e38b4f5499ea8637bfade78911851dc0cb`; four matching reads |

[Backend metadata](n8d3-stage.txt) records the shared tick, dimensions, format, FBP, byte count, stride, and successful raw/packed writes. Raw and packed binary files remain in `~/dev/ssx3-work/N8D3/`; they are not committed. N8D3 has no nearby screencap. **The GPU scanout image versus Vulkan copy/readback boundary remains unresolved** by these host-side bytes. This diagnostic run provides no speed number and no Vulkan driver/API version inference.

## Commands, acceptance, and bounds

```text
ssh bytesize 'wsl -d Ubuntu -- python3 -' < ~/dev/ssx3-work/N8D3/prepare.py
ssh bytesize 'wsl -d Ubuntu -- bash -s' < ~/dev/ssx3-work/N8D3/build.sh
ssh bytesize 'wsl -d Ubuntu -- python3 -' < ~/dev/ssx3-work/N8D3/apk_gate.py
ssh bytesize 'wsl -d Ubuntu -- diff -rq -x .cxx -x build -x .gradle -x runner /home/brad/n8d1/PS2Recomp /home/brad/n8d3/PS2Recomp'
ssh bytesize 'wsl -d Ubuntu -- cat /home/brad/n8d3/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk' > ~/dev/ssx3-work/N8D3/app-release.apk
python3 -u ~/dev/ssx3-work/N8D3/launch.py
ffmpeg -v error -f rawvideo -pixel_format rgba -video_size 512x448 -i ~/dev/ssx3-work/N8D3/n8d3-raw.bin -frames:v 1 -y local/research/N8D3/raw-rgba.png
ffmpeg -v error -f rawvideo -pixel_format rgba -video_size 512x448 -i ~/dev/ssx3-work/N8D3/n8d3-packed.bin -frames:v 1 -y local/research/N8D3/backend-rgba.png
python3 local/research/N8D3/accept.py
```

The single build succeeded in 9m 8s, 48 Gradle tasks; [build-tail.txt](build-tail.txt). [accept.log](accept.log): `N8D3 acceptance PASS` for one build/install/launch, package pins, same tick/FBP/dimensions, byte lengths, 448 row comparisons, full PNG decodes, device/local SHA pairs, cleanup, and size limits. WSL scratch was 6.7 GiB (<10 GiB); Mac work scratch was 162 MiB (<1 GiB). Raw/packed/decoded bytes plus small images total 2,821,589 bytes (<12 MiB); selected text logs total 22,567 bytes (<16 MiB). No second launch, fork edit, or push.
