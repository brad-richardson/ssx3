# N8D7F worker receipt

## Source-path and ordering gate

| Path | Source anchor | Finding |
| --- | --- | --- |
| selected input | private `parallel-gs/gs/gs_renderer.cpp:4455-4458`, `:4278-4313` | Renderer rejects undersized promoted layers before `sample_crtc_circuit`; the draw binds either promoted image or `buffers.gpu`. |
| VRAM copy | `gs_renderer.cpp:1614-1634`, `:4773-4786` | G40 ordered `buffers.gpu` copy is available in `direct_cmd`; N8D7F can copy the full base slice before circuit1 draw. |
| circuit1 copy | `gs_renderer.cpp:4934-5006` | N8D6A retains circuit1; normal path transitions attachment to readable before merge. N8D7F can transition to transfer source, copy, and restore readable there. Raw-circuit early return precedes this site and must stop as OTHER. |
| lifetime | `gs_renderer.cpp:5280`, backend `ps2_gs_parallel_backend.cpp:257-294` | `flush_submit` submits `direct_cmd`; `ScanoutResult` can retain staging handles through backend wait and map. |

Safe ordering established for the normal path. Source pins before edits: fork `81682dfb5fa05e6737e12e40531f63bc65dfd6cf`, backend SHA-256 `e730b9f05994c9887f9c5605f9a34b2fe6f4ac1c239bb964f17cdfc515b1fb5c`; private G43 copy HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`, interface/header/renderer SHA-256 `4c78cf9d90e0dfa313275aa3417b7d1a8e0c631f60e94be51a17772d2d44639c` / `8f511a44d66f4bc7e9d238e48964ab88e4dfbcdb63544ce1a47f4cae0a0d59b5` / `3322481421db8d0c182cb7916d826fde5853425cae2385828587507863988534`.

| Item | Result |
| --- | --- |
| Candidate and diffs | One default-OFF `PS2X_N8D7F_SELECTED_CAPTURE=1` candidate. Private fork commit `0678dd9`; [backend diff](fork-backend.patch), SHA-256 `46e3e13c5feff473a83ba79f864d70a4eb3f2531990236b3295a4b25102b98df`. [private G43 delta](g43-selected.patch) against N8D6A, SHA-256 `b20b5e258d22da34faab281e20a6b317e198c2b3601cafd15e76576b5c05f47f`. Both patches use zero context for clean text receipts. No shared G43/N8D6A edit. |
| After-edit source SHAs | Backend `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f`; private G43 interface/header/renderer `3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d` / `fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a` / `85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e`. |
| Configure/build | One Release/Ninja configure and one `nice -n 10` `ps2x_tests` build passed. Exact commands below; [configure log](cmake.log), [build log](build.log). Build log confirms `gs_renderer.cpp` and backend compiled. Logs are text-normalized for carriage-return progress and trailing whitespace. No compile repair. |
| Taps-OFF suite | One run from private fork root: **585 passed, 0 failed**; [suite log](suite.log). Cache pins `PS2X_ENABLE_DIAG_TAPS=OFF`, runtime/aggressive logs OFF, parallel GS ON and the private G43 path. |
| Binary/stream/codegen double SHAs | Two independent SHA-256 reads each matched: binary `66457eb47ac6c29a8ffca38795d88122fb1c03e4e19e4f55e977f716eb70a804`; stream `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d`; codegen `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`. |
| Caps | Private copy 1.0 GiB + build 1.4 GiB + fork worktree 22 MiB, under 5 GiB. Receipt dir 208 KiB, under 4 MiB. Global internal ssx3 141.1/200 GB. New probe byte ledger: 4,194,304 GPU staging + 458,752 circuit staging + 458,752 decoded RGBA + 65,536 allowance = **5,177,344 B**, under 6 MiB. |
| Gaps | OFF/ON Mac replay and same-frame tile comparisons are pending orchestrator execution outside this worker. Copy/map and pipeline status are therefore unobserved. No Odin or device-cause verdict. |

The selected input metadata is taken after promoted-layer rejection: FBP, FBW, PSM, DBX, DBY, phase, stride, VRAM mask, valid/image extents, sample count, and promotion. Count-one, no promotion, 512×224, supported PSM, 4 MiB mask and all coordinates below 2048 gate the copy. A raw-circuit early return leaves status `1` (OTHER); normal path records status `2` only after both copies. The backend maps after submit/wait, decodes one row at a time with `vram_readback<PSM>`, counts independent 16×16 input/circuit tiles, packs each 448-count vector as little-endian `uint16_t` for SHA-256, and compares both to the existing GPU stage vector. Apple CommonCrypto supplies the packed SHA for this Mac probe.

## Exact configure, build, suite commands

Run from `/Users/brad/dev/ssx3-work/N8D7F/PS2Recomp`:

```sh
cmake -S . -B /Users/brad/dev/ssx3-work/N8D7F/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/N8D7F/parallel-gs -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DGRANITE_VULKAN_SPIRV_CROSS=OFF
nice -n 10 cmake --build /Users/brad/dev/ssx3-work/N8D7F/build --target ps2x_tests -j 6
/Users/brad/dev/ssx3-work/N8D7F/build/ps2xTest/ps2x_tests
```

## Exact Mac replay handoff — not executed by worker

Recheck the three SHA pairs above before either run. Run both from the private fork root outside the worker sandbox. Expected known N8D6A final hash is `7bf5c012`; equality and all tile acceptance checks remain pending.

OFF:

```sh
cd /Users/brad/dev/ssx3-work/N8D7F/PS2Recomp
env PS2X_N8D7F_SELECTED_CAPTURE=0 PS2X_N8D5_TILE_CAPTURE=1 PS2X_GS_REPLAY_CAPTURE=/Users/brad/dev/ssx3-work/N8D4/n8d4.gs PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_OUT=/Users/brad/dev/ssx3-work/N8D7F/off.hashes PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib /Users/brad/dev/ssx3-work/N8D7F/build/ps2xTest/ps2x_tests > /Users/brad/dev/ssx3-work/N8D7F/off.log 2>&1
```

ON:

```sh
cd /Users/brad/dev/ssx3-work/N8D7F/PS2Recomp
env PS2X_N8D7F_SELECTED_CAPTURE=1 PS2X_N8D5_TILE_CAPTURE=1 PS2X_GS_REPLAY_CAPTURE=/Users/brad/dev/ssx3-work/N8D4/n8d4.gs PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_OUT=/Users/brad/dev/ssx3-work/N8D7F/on.hashes PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib /Users/brad/dev/ssx3-work/N8D7F/build/ps2xTest/ps2x_tests > /Users/brad/dev/ssx3-work/N8D7F/on.log 2>&1
```

No worker replay, Odin, push, or device-cause conclusion.
