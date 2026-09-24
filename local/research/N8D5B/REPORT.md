# N8D5B — same-frame GPU sampled tile candidate

Worker receipt. Source candidate and Mac compile/suite only; no device run or device verdict.

| Gate | Result | Receipt |
| --- | --- | --- |
| Pinned tile baseline | PASS: 567 Mac paraLLEl / 55 Odin raw active tiles, 896 total, 16×16, RGB channel >=32 and >=32 occupied pixels/tile. | `occupancy.json`; pinned PNG SHA values within it. |
| Fresh fork and G43 copies | Fork branch `n8d5b-tile` at N8B1 `17e90ded3689685ad359b76a9168c80a1f752e2d`; G43 copy at `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`, Granite submodule `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5`. | `g43-carried.patch`, `g43-granite-carried.patch`, `carried-hunks.txt` enumerate every pre-existing dirty hunk before edits. |
| Bounded shader feasibility | PASS: same image at backend `Present`; separate compute shader can sample its view into a 897-word storage buffer and map it. | Fork `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:239-291`; G43 `Granite/vulkan/command_buffer.hpp:401-408,483-499,542`, `Granite/vulkan/device.hpp:328-349`, `Granite/vulkan/image.hpp:57-62,290-305`; G43 `Granite/tests/sampler_precision.cpp:52-69`. |
| Candidate source diff | Default OFF `PS2X_N8D5_TILE_CAPTURE=1`, tick 2050 only. One 16×16 checkerboard control image (128 occupied pixels) and the same compute shader sample `shot.image`; 897 `uint32_t` storage words (3,588 bytes), 896 tile counts; original image-to-buffer capture remains. | Fork [candidate patch](fork-candidate.patch), commit `ef34402` on `n8d5b-tile`; [shader source](g43-n8d5_tile.comp), [embedded SPIR-V header](g43-n8d5_tile_spirv.hpp), [generator](make_spirv_header.py), [SHA receipt](g43-candidate-sha.txt). |
| Shader compile/validation | PASS: `glslangValidator -V --target-env vulkan1.2 ...`; `spirv-val` exit 0. Shader SPIR-V SHA `76818c169fe53b517f08435d4cef9fcc0315f9fd44ce852a234993f0a4aa1980`. | G43 private copy `gs/shaders/n8d5_tile.{comp,spv}`; `gs/n8d5_tile_spirv.hpp`. |
| Mac configure/build | PASS: Release/Ninja, paraLLEl ON from private G43 copy, canonical E54F2 external codegen, diagnostic taps and runtime/aggressive logs OFF; `ps2x_tests` built. Binary SHA-256 twice `50df1ab8d7ccfb0e14228e62096c6abc42c5341a3596a10c92ab1977ed39b3f9`. | [CMake](cmake.log), [build](build.log), `~/dev/ssx3-work/N8D5B/build/ps2xTest/ps2x_tests`. |
| Taps-OFF suite | PASS: 585/585, 0 failed, from fork worktree root. | [suite-off.log](suite-off.log). |
| One Mac paraLLEl replay | **INCONCLUSIVE gate:** stream parsed through 2050 (862,993 packets, 2,050 markers), but Granite logged `Failed to create Vulkan instance` and backend `init_failed=1`, `presents=0` before `Present`. No GPU control or tile counts were produced. The test harness still reported 585/585; that count does not validate the GPU probe. No retry under the first-failure rule. | [replay.log](replay.log): lines 243–251 and 1342–1344. No PPM written. |
| Orchestrator outside-sandbox Mac replay | **OTHER / inconclusive (failed control):** same pinned binary and one stream replay reached tick 2050, FBP112, PMODE `ff21`, 512×448. Raw mapped occupancy = 567/896 active tiles and 128,292 pixels, matching the pinned Mac baseline. Control returned `2149844998` instead of 128; sampled words are invalid. The compute pipeline failed and Granite dropped dispatch, so these words cannot describe `shot.image`. | [bounded excerpt](orch-replay-excerpt.txt), with SHA-256 of the full scratch log. |
| Runner diff, bytes, commit | Runner-dir diff against `14b1e5cb` empty. N8D5B scratch 2.5 GiB / 8 GiB; committed text receipts <0.5 MiB / 8 MiB; global 133.0 GB / 200 GB. Fork local commit `ef34402`; ssx3 receipt commit pending. No push or device action. | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`; `du -sh`; `local/tooling/disk_budget.sh`. |

## A/B/OTHER gate

| Outcome | Required observation |
| --- | --- |
| A | Future same-frame device run: control 128, sampled active tiles <=100, raw active tiles <=100; tick 2050, FBP112, PMODE `ff21`, 512×448. |
| B | Future same-frame device run: control 128, sampled active tiles >=500, raw active tiles <=100; same alignment. |
| OTHER | Failed/missing control, mismatched alignment, middle counts, or any off-table pair. No cause verdict. |

Mac replay validation requires control 128 and broad sampled/raw occupancy (both >=500) against the pinned Mac 567-tile baseline before any Odin build. The worker replay did not reach that check. The orchestrator replay reached it but **failed the control**, so the GPU tile counts remain unavailable.
The orchestrator viewed the generated Mac tick-2050 frame; its raw mapped tile summary is a valid Mac occupancy observation. It does not validate shader sampling.

The outside-sandbox log states `Attempted to reflect resource layout, but SPIRV-Cross is not enabled in build` at line 78252, MoltenVK's `Argument buffer resource base type could not be determined` at line 78254, then `Failed to create compute pipeline` and `dispatch will be dropped` at lines 78255–78256. Static source read identifies the likely integration issue: candidate `ps2_gs_parallel_backend.cpp:305` calls `request_program` without a `ResourceLayout`; G43 `Granite/vulkan/device.cpp:403-409` forwards that null layout to `request_shader`; Granite `vulkan/shader.cpp:1095-1103` tries reflection and logs that SPIRV-Cross is unavailable. G43 `CMakeLists.txt:38-41` forces SPIRV-Cross OFF for the standalone path, confirmed by `build/CMakeCache.txt:696`. The log establishes pipeline creation and dispatch failure; it does **not** establish a host-map error or a scanout-image cause. No source repair or replay retry was made after this receipt.

## Exact source/API connections

| Connection | Lines |
| --- | --- |
| Same scanout hook, old mapped copy | Fork `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:239-291` before edit; candidate `:253-270,331-364`. |
| Default-OFF alignment and bounded control/dispatch | Candidate `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:277-329`; [shader](g43-n8d5_tile.comp) lines 4–40. |
| Original raw mapped capture and tile log | Candidate `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:331-384`. |
| Granite GPU path | G43 `Granite/vulkan/command_buffer.hpp:401-408,483-499,542`; `Granite/vulkan/device.hpp:328-349`; `Granite/vulkan/image.hpp:57-62,290-305`; example `Granite/tests/sampler_precision.cpp:52-69`. |

The G43 copy preserves source pin `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` and Granite pin `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5`. Before the new shader files, it carried dirty hunks in `CMakeLists.txt`, `gs/gs_interface.cpp`, `gs/gs_renderer.cpp`, `gs/gs_renderer.hpp`, `tools/CMakeLists.txt`, `tools/gs_dump_replayer.cpp`, and five Granite files. [carried-hunks.txt](carried-hunks.txt) lists every hunk, with full [G43](g43-carried.patch) and [Granite](g43-granite-carried.patch) patches. Shared G43 and N8B1 trees were not edited.

## Pins and commands

N8D4 stream SHA-256 twice: `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d`. Canonical E54F2 `register_functions.cpp` SHA-256 twice: `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`. Fork base N8B1 `17e90ded3689685ad359b76a9168c80a1f752e2d`.

```text
python3 local/tooling/orch/n8d5b_occupancy.py > local/research/N8D5B/occupancy.json
glslangValidator -V --target-env vulkan1.2 -o gs/shaders/n8d5_tile.spv gs/shaders/n8d5_tile.comp
python3 local/research/N8D5B/make_spirv_header.py
spirv-val gs/shaders/n8d5_tile.spv
cmake -S . -B ~/dev/ssx3-work/N8D5B/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3 -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=~/dev/ssx3-work/N8D5B/parallel-gs -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF
nice -n 10 cmake --build ~/dev/ssx3-work/N8D5B/build --target ps2x_tests -j8
~/dev/ssx3-work/N8D5B/build/ps2xTest/ps2x_tests
env PS2X_N8D5_TILE_CAPTURE=1 PS2X_GS_REPLAY_CAPTURE=~/dev/ssx3-work/N8D4/n8d4.gs PS2X_GS_REPLAY_PPM_TICKS=2050 PS2X_GS_REPLAY_PPM_DIR=~/dev/ssx3-work/N8D5B/replay-ppm PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_OUT=~/dev/ssx3-work/N8D5B/parallel.hashes PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib ~/dev/ssx3-work/N8D5B/build/ps2xTest/ps2x_tests
```

The actual configure and worker replay argv used absolute `/Users/brad/dev/...` paths; the command block abbreviates that prefix as `~`. The replay binary is pinned by the SHA above. The orchestrator ran one separate unsandboxed Mac replay against that binary. Its full 4,812,990-byte log is retained outside git at `~/dev/ssx3-work/N8D5B/orch-replay.log`, SHA-256 `f04f59f3a57a32e35558c599d40823a495ef9139701ee2501e068584ecd2d127`; the committed excerpt contains the gate lines only.

## Gaps

- LSP tool unavailable in this worker session; no LSP output. Source connections were confirmed by the cited caller and API lines.
- The failed Mac checkerboard control invalidates sampled words. No valid Mac sampled tile result, Odin result, or device cause inference is available.
