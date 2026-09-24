# N8D6A — Mac preparation and build

Worker receipt. The Mac Vulkan replay is **pending** for the orchestrator. No replay, game boot, device action, APK, push, or device-cause verdict occurred. LSP was unavailable (no LSP tool exposed); source connections were checked by direct reads.

| Source stage | Implementation and citation | Retention/read layout |
| --- | --- | --- |
| Circuit1 | `parallel-gs/gs/gs_renderer.cpp:4774-4787` creates the image and calls `sample_crtc_circuit`; `:4999-5006` changes it from attachment to read-only before merge. `gs_renderer.hpp:26` and `gs_renderer.cpp:4934-4935` retain its shared handle when requested. | Granite `vulkan/image.hpp:524` defines `ImageHandle` as `IntrusivePtr<Image>`. The backend adds a read-only image barrier before compute sampling (`ps2_gs_parallel_backend.cpp:371-380`). |
| Pre-deinterlace merged | `gs_renderer.cpp:4995-4997` creates the merged field; `:5131-5142` ends the merge pass and changes it to read-only for the interlaced path. `:5239-5258` retains the handle before moving `merged` into field history and deinterlacing. | `gs_renderer.hpp:27` holds a shared handle; the backend samples it with the same shader and a stage-sized buffer. |
| Final | `gs_renderer.cpp:5275-5286` returns the final image after deinterlace; the backend keeps the existing sampled vector, raw copy/vector, and summary path (`ps2_gs_parallel_backend.cpp:397-486`). | Existing final read-only image and copy path. |

`gs_interface.hpp:159` adds a default-OFF-by-zero-initialization `capture_scanout_stages` flag. The backend sets it only for tick 2050 with `PS2X_N8D5_TILE_CAPTURE=1` (`ps2_gs_parallel_backend.cpp:248-252`). The existing shader, explicit `ResourceLayout`, threshold 32, checkerboard control, and 16×16 tile method are reused. Each extra stage has its own image dimensions, dispatch, and count buffer. Missing image, invalid dimensions, allocation, or map errors log `ERROR`.

| Pin or step | Result |
| --- | --- |
| Fork source | Fresh local `n8d6a-scanout-stages` worktree from N8D5L `ab8155bbcbbdd478d17f2cd90a2feff3eb9a865b`; source SHA-256 before edits `4e3efc51d8d104ab5d3c537076e85c6cfcd8344c8e6c147de02f5a5015c8f1e5`. One backend-file commit `81682dfb5fa05e6737e12e40531f63bc65dfd6cf`; after-edit source SHA-256 `e730b9f05994c9887f9c5605f9a34b2fe6f4ac1c239bb964f17cdfc515b1fb5c`. [Exact backend diff](fork-backend.patch), SHA-256 `463b05ac64a32e01db3452232913c14b6fc477912fe36afae544d52c6107649b`. Runner-dir diff against `14b1e5cb` empty before and after commit. |
| Private G43 copy | Copied from N8D5B `parallel-gs` at `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`, Granite `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5`. Original private changes: [paraLLEl patch](g43-private.patch) SHA-256 `807f161bcf10e0a7a17d1c191d0a826d18c6692f038c35de492288c2f64c5e8f2`; [Granite patch](g43-granite.patch) SHA-256 `54745a3cebbbd5565512c8c0c93cb8680a1ce86ba808fc0cb727a27f0c04bbc9`. [Exact new G-stage diff from source copy](g43-stage.patch), SHA-256 `013b23508b678d2852f61fad066c4f498762e42aa6226aa1c7ea8cb4af0390a4`. Shader header unchanged, SHA-256 `19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9`; shader source `84d3cb9a7bc51867ab9d1d2ecda9e5585d2b157e59af54dd7a6f0f2673c89425`, SPIR-V `76818c169fe53b517f08435d4cef9fcc0315f9fd44ce852a234993f0a4aa1980`. |
| Configure/build | One Release/Ninja configure and one `ps2x_tests` build passed. CMake cache: paraLLEl ON, private N8D6A G43 path, canonical external codegen, diagnostics taps/runtime/aggressive logs OFF, Granite SPIRV-Cross OFF. [Configure log](cmake.log), [build log](build.log). |
| Suite | One taps-OFF run from the fork root: **585 passed, 0 failed**. [Suite log](suite.log). |
| Binary and replay inputs | `/Users/brad/dev/ssx3-work/N8D6A/build/ps2xTest/ps2x_tests` SHA-256 twice `4ea777acf3f6dffc3d3462a5ef805838115a494fb4e58713c287b503030ea075`; `/Users/brad/dev/ssx3-work/N8D4/n8d4.gs` SHA-256 twice `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d`; `/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp` SHA-256 twice `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`. |
| Limits and gaps | N8D6A scratch 2.5 GiB of 5 GiB; global internal ssx3 138.5/200 GB. Receipts under 0.3 MiB of 4 MiB. Mac replay pending, so stage dimensions, tile counts, controls, occupancy, final sampled/raw equality, and pipeline errors are **not observed**. No Odin inference. |

## Exact commands

```sh
cmake -S . -B /Users/brad/dev/ssx3-work/N8D6A/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/N8D6A/parallel-gs -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DGRANITE_VULKAN_SPIRV_CROSS=OFF
nice -n 10 cmake --build /Users/brad/dev/ssx3-work/N8D6A/build --target ps2x_tests -j 6
/Users/brad/dev/ssx3-work/N8D6A/build/ps2xTest/ps2x_tests
```

Run this **one replay outside the worker sandbox from the fork worktree root** after rechecking the three SHA pairs. The command is a handoff and was not run here:

```sh
cd /Users/brad/dev/ssx3-work/N8D6A/PS2Recomp
env PS2X_N8D5_TILE_CAPTURE=1 PS2X_GS_REPLAY_CAPTURE=/Users/brad/dev/ssx3-work/N8D4/n8d4.gs PS2X_GS_REPLAY_PPM_TICKS=2050 PS2X_GS_REPLAY_PPM_DIR=/Users/brad/dev/ssx3-work/N8D6A/replay-ppm PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_OUT=/Users/brad/dev/ssx3-work/N8D6A/parallel.hashes PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib /Users/brad/dev/ssx3-work/N8D6A/build/ps2xTest/ps2x_tests > /Users/brad/dev/ssx3-work/N8D6A/replay.log 2>&1
```

Orchestrator gate: tick2050/FBP112/PMODE `ff21`/512×448; all three stage summaries and controls=128; final sampled/raw exact 896/896 with ≥500 active; circuit1 and merged dimensions/tile counts internally consistent and both ≥50% active; no pipeline errors. Anything else is OTHER and no Odin release. These values are predictions, not worker observations.
