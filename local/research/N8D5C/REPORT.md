# N8D5C — explicit shader resource layout

Worker receipt. One source candidate, one Release/Ninja configure/build, one taps-OFF suite. The orchestrator ran the one outside-sandbox Mac replay; formal `[orch]` gate pending. No device run or device verdict.

## Gate written before source edit

| Outcome | Required observation on the pinned N8D4 stream at tick 2050, FBP 112, PMODE `ff21`, 512×448 |
| --- | --- |
| Mac PASS | Control = 128; GPU sampled and raw active tile counts both >=500 of 896. This validates the Mac probe only. |
| A, later device prediction | Control = 128; sampled <=100 and raw <=100 active tiles. |
| B, later device prediction | Control = 128; sampled >=500 and raw <=100 active tiles. |
| OTHER / stop before Odin | Failed control, pipeline error, mismatched alignment, or any off-table pair. No cause verdict. |

The A/B rows preserve N8D5B's device hypotheses as future predictions. **No device observation was made here.** The orchestrator must gate the Mac replay first.

## Receipts

| Item | Result / exact receipt |
| --- | --- |
| Fork source | Base `ef344024ff1a899d56cd3df21545caa7ad706c5f` (N8D5B); local branch `n8d5c-layout`, commit `a847d0fe8ee6957154fe85986dc371c8e1ec0f1e`. Only `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` changed. SHA-256 twice: `ed87b66d981186725469c8bfa85a857c47813aa85d3fd5ff843516e5b17e9a61`. |
| Exact source diff | [source.patch](source.patch): initialize `Vulkan::ResourceLayout`, set set 0 sampled and float masks `0x3`, storage buffer mask `0x4`, push constant size `8`, and pass `&layout` to `request_program`. No shader/control/threshold/tick/page/raw-copy change. |
| G43 private input | Read-only `~/dev/ssx3-work/N8D5B/parallel-gs` at `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`; Granite `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5`. Its carried diagnostic hunks and shader header were left untouched. `gs/n8d5_tile_spirv.hpp` SHA-256 twice: `19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9`. |
| N8D4 stream | `/Users/brad/dev/ssx3-work/N8D4/n8d4.gs`; SHA-256 twice: `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d`. |
| E54F2 external codegen | `/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp`; SHA-256 twice: `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`. |
| Configure/build | PASS, Release/Ninja `ps2x_tests`. [cmake.log](cmake.log), [build.log](build.log); CMake cache confirms paraLLEl ON, G43 private path, external codegen, diagnostic taps/runtime/aggressive logs OFF and Granite SPIRV-Cross OFF. |
| Taps-OFF suite | PASS, **585/585**, 0 failed, invoked from new fork worktree root. [suite-off.log](suite-off.log). |
| Replay binary | `/Users/brad/dev/ssx3-work/N8D5C/build/ps2xTest/ps2x_tests`; SHA-256 twice: **`fd0f0f9849a08f1e1dd5bf994e9b03455237462c81e6b430d56a3e61d67b5b76`**. |
| Runner directory | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty after fork commit. |
| Byte caps | N8D5C scratch 1.4 GiB (under 4 GiB); committed text receipts under 4 MiB (about 185 KiB before `source.patch`); global internal usage 134.4 GB of 200 GB. |
| Mac replay | Orchestrator reported one outside-sandbox replay against pinned binary after fork commit: control **128/128**, tick 2050/FBP 112/PMODE `ff21`/512×448; sampled and raw 896 tile words byte-for-byte equal, each **567 active tiles** and **128,292 occupied pixels**. Orchestrator viewed the generated frame and will record the formal `[orch]` gate. Worker attempted no replay. |
| Odin, bytesize, APK, game boot, push | None. |

## Source connection

G43 `Granite/vulkan/shader.cpp:909-925` maps two float sampled images at set 0/bindings 0 and 1 to `sampled_image_mask=0x3`, `fp_mask=0x3`; `:1003-1014` maps the binding-2 SSBO to `storage_buffer_mask=0x4`; `:1040-1047` obtains the two-`uint` push constant size of 8. The fields are declared in `Granite/vulkan/shader.hpp:52-60` and `Granite/vulkan/descriptor_set.hpp:47-61`. `Granite/vulkan/device.cpp:403-409` forwards the layout; `Granite/vulkan/shader.cpp:1095-1103` uses it directly when present. G43 `gs/shaders/slangmosh.hpp:19684-19705` passes `&layout` to `request_program` in the standalone path. No LSP tool was exposed in this worker session; these connections were checked by source reads.

## Exact commands

Worktree root: `/Users/brad/dev/ssx3-work/N8D5C/PS2Recomp`.

```sh
cmake -S . -B /Users/brad/dev/ssx3-work/N8D5C/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/N8D5B/parallel-gs -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF
cmake --build /Users/brad/dev/ssx3-work/N8D5C/build --target ps2x_tests -j 6
/Users/brad/dev/ssx3-work/N8D5C/build/ps2xTest/ps2x_tests
```

For the orchestrator's **one outside-sandbox replay**, run from the same worktree root after rechecking the binary and input SHAs. Worker did not run this command:

```sh
env PS2X_N8D5_TILE_CAPTURE=1 PS2X_GS_REPLAY_CAPTURE=/Users/brad/dev/ssx3-work/N8D4/n8d4.gs PS2X_GS_REPLAY_PPM_TICKS=2050 PS2X_GS_REPLAY_PPM_DIR=/Users/brad/dev/ssx3-work/N8D5C/replay-ppm PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_OUT=/Users/brad/dev/ssx3-work/N8D5C/parallel.hashes PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib /Users/brad/dev/ssx3-work/N8D5C/build/ps2xTest/ps2x_tests
```

## Gaps

- Outside-sandbox replay values above are the orchestrator's reported observation; the formal `[orch]` gate and any full replay log receipt are owned by the orchestrator. The worker did not run or inspect that replay.
