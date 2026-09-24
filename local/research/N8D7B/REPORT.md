# N8D7B — static pre-circuit1 probe design

## Pins and allowed evidence

Read-only study. No build, boot, device action, source change, or push. Source pins: `ssx3-work/N8D6A/PS2Recomp` HEAD `81682dfb5fa05e6737e12e40531f63bc65dfd6cf`; `ssx3-work/G43/parallel-gs` HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`. Paths are under `/Users/brad/dev/`. The existing N8D4 Mac replay pin in its report is `ddaee780288adb076ce40050d87969b20bc4bb05`; that is a separate run/build pin, not the source-study checkout.

| Receipt | Evidence relevant here |
| --- | --- |
| `local/research/N8D6C/ORCH-GATE.md`; `vector-audit.json` | Same-run Odin tick2050/FBP112/PMODE `ff21`: circuit1 21/448 active, merged 21/448, final 39/896; controls 128. Final sampled/raw vectors equal 896/896. Viewed PNG mostly black. Formal launcher outcome OTHER after comma-led logcat continuation blocked vector parsing. |
| `local/research/N8D6A/orch-replay-excerpt.txt` | Pinned N8D4-stream Mac replay, same stated alignment: circuit1 300/448, merged 300/448, final 567/896; controls 128. |
| `local/research/N8D4/REPORT.md` | The captured Odin stream replayed on Mac produced a broad race scene; Mac replay and later live Odin are not byte-identical GS streams. The report's Mac paraLLEl replay is a replay of its *own* captured stream. |
| `docs/numbers-ledger.md:348` (G37); `:351` (G38), per orchestrator correction | G30/G31 mis-sampling interpretation was withdrawn in G37. G38's matched-boundary comparison first differed at boundary 1: Mac B updated, Odin B stayed at load. Those older runs constrain interpretation; they do not assign N8D6C's cause. |

## Source path

| Step | Exact source anchor | What the code establishes |
| --- | --- | --- |
| Priv sync | `ssx3-work/N8D6A/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:247`, `:654-680` | `Present` calls `syncPriv`; raw privileged register words, including `dispfb1` and `display1`, are copied into the interface before `flush` and `vsync` at `:257-258`. |
| Submit/order | `ssx3-work/G43/parallel-gs/gs/gs_interface.cpp:5153-5162`; `gs_renderer.cpp:1116-1195`, `:4403-4405`, `:5271-5276` | Interface flush submits pending work; renderer vsync assumes it is flushed, records scanout in its direct command, and submits before return. The listed async-transfer semaphore wait is at `gs_renderer.cpp:1149-1155`. This establishes intended order, not observed byte correctness. |
| Buffer ownership | `gs_renderer.cpp:360-396`, `:1513-1524`; `gs_interface.cpp:5126-5150` | `buffers.gpu` is VRAM scanout storage. Host maps use `buffers.cpu`, which aliases GPU only on the UMA path; otherwise host reads may trigger tracked readback. A host map alone is not an unambiguous pre-circuit GPU-input observation. |
| Existing copy mechanism | `gs_renderer.cpp:1614-1634`; `gs_interface.cpp:5612-5636` | G40 records an ordered GPU-buffer-to-host-staging copy of B pages. Historical G31 maps and hashes a raw VRAM region *after* vsync. These demonstrate raw-byte access mechanisms only. G31 comments' interpretation is withdrawn per G37 ledger row. Neither code path decodes the display rectangle. |
| Circuit input and shader | `gs_renderer.cpp:793-794`, `:4262-4318`; `gs/shaders/sample_circuit.frag:19-27`, `:30-42`, `:52-70`, `:98-123` | `sample_quad[0]` reads `buffers.gpu`; `sample_quad[1]` reads a promoted image. Push constants select FBP/FBW/DBX/DBY/phase and specialization selects PSM, VRAM mask and sample count. Fragment coordinates go through `swizzle_PS2` at shader `:115`; 16/32-bit payload is unpacked to RGBA. |
| Circuit image and tap | `gs_renderer.cpp:4773-4786`; `ps2_gs_parallel_backend.cpp:290-293`, `:369-380`, `:408-430` | `sample_crtc_circuit` draws into `circuit1`, retained as `shot.circuit1`. Backend stage tap runs the N8D5 tile compute shader on that image, then counts active tiles. Its control tests a checkerboard (`ps2_gs_parallel_backend.cpp:302-340`), not the GS decode. |
| Promotion | `gs_interface.cpp:5540-5552`, `:5576-5578`; `gs_renderer.cpp:4278-4282`, `:4455-4458` | A nonnull promoted1 can bypass VRAM and feed circuit1 as an image, subject to sample-layer check. G31 source comments predict promotion off for their historical run (`gs_interface.cpp:5580-5591`), but the allowed N8D6C excerpt contains no promotion-state receipt. It does not prove the N8D6C frame used VRAM. |

`source-map.tsv` gives one anchor per requested step. The shader includes `swizzle_utils.h`, `data_structures.h`, and `utils.h` at `sample_circuit.frag:10-12`; those files were outside this brief's read list, so the exact CPU swizzle helper implementation was not inspected.

## Same-Odin-frame V/S/T prediction table

Here “input” means the *actual selected circuit1 input* at tick2050, after the flush and before `sample_crtc_circuit`, decoded using that frame's DISPFB1/PSM/phase/extent. “Broad/sparse” must be compared at a matched 512×224 field grid and declared tile threshold; raw nonzero-byte counts or FNV alone are insufficient. A promoted image, if selected, is the input instead of VRAM. The predictions are conditional on a same-run sparse stage tap; they do not assume byte-identical Mac/Odin GS streams.

| Alternative | Decoded input observation | Independent circuit1 image observation | Existing stage tap | Separating check |
| --- | --- | --- | --- | --- |
| V — input VRAM wrong/sparse | Sparse at the addresses used by the display rectangle | Sparse | Sparse | If promoted1 is nonnull, this VRAM prediction is inapplicable; inspect selected promoted image. A raw B-region hash does not establish decoded sparsity. |
| S — sample path sparse | Broad/correct input | Sparse | Sparse | Input-vs-circuit comparison separates S from V. S includes sampler address/decode, draw, and visibility/order until circuit image is stored; it does not isolate one operation. |
| T — stage tap sparse | Broad/correct input | Broad | Sparse | Independent circuit image readback separates T from S. Existing checkerboard control=128 verifies a separate image and storage path, not the circuit image census itself. |

If input and circuit both appear sparse, V is only supported after decoder calibration and confirmation that the input actually selected by `sample_quad` was captured. If input and circuit both appear broad but the tap is sparse, T needs an independent host-side circuit-image census to avoid repeating the N8D5 tile shader. Equal raw-byte occupancy or hashes cannot resolve V versus S because swizzling, PSM, DBX/DBY and phase determine the sampled pixels (`sample_circuit.frag:98-123`).

## One candidate probe, design only; feasibility stop

Placement: gate on default-OFF `PS2X_N8D7B_INPUT_PROBE=1`, the single aligned tick2050/FBP112/PMODE `ff21` frame. In renderer `vsync`, after pending work is submitted and before `sample_crtc_circuit` draws circuit1, record whether promoted1 is selected. For VRAM mode, use a `buffers.gpu` transfer to host staging, with a compute/transfer write-to-copy-read barrier analogous to `gs_renderer.cpp:1614-1634`; keep the selected GPU input, rather than relying on `map_vram_read`'s possibly distinct CPU buffer. Cap raw input at one 4 MiB VRAM slice, circuit1 at 512×224×4 = 458,752 bytes, and metadata/tile summaries at 64 KiB; total <4.75 MiB. Capture circuit1 by a separate image-to-host readback after its draw and host-count tiles. For promoted mode, capture the promoted image instead and report its format/layers/dimensions. Abort classification if dimensions/PSM/phase or captured source do not match the shader's selected input. Keep one frame only, with exact hashes and error flags.

Required missing component: an **independent, calibrated decoder** of the captured swizzled VRAM bytes into the exact field grid used by `sample_circuit.frag:98-123` (including PSM16/32 and phase; high-resolution sample validity if enabled). None of the allowed named sources exposes such a host decoder or a decoded pre-circuit image; `map_vram_read` and G40 copy expose raw bytes. Using `sample_quad` itself to make the input census would duplicate the path under test. Therefore this brief cannot establish that the candidate meets the independently decoded-input requirement **without a new decoder**. This is the brief's feasibility stop branch: no implementation or run proposed here.

If the prerequisite decoder is authorized later, calibrate first on one pinned Mac replay using that replay's actual GS stream and priv state: decoder output and an independent circuit1 host census must be broad and spatially consistent; verify selected-input identity and hash/byte caps. Then allow exactly one Odin aligned frame. Acceptance requires complete raw-input and circuit-image receipts, matching tick/FBP/PMODE/geometry, promotion state, shader control and independent host tile counts. Classify only by the table above within that Odin run. Stop as OTHER on missing/mismatched receipt, unsupported PSM/samples, promotion without selected-image capture, map/copy failure, failed Mac calibration, or differing frame alignment. The historical G38 result is context, not a substitute for this within-run comparison.

## Gaps and LSP

No LSP goToDefinition/findReferences tool is available in this Codex tool set (tool-name discovery returned an empty list); connections above were checked by exact call sites and field passing in the allowed source files. No N8D6C per-frame promoted1 state, selected GPU input readback, decoded input grid, or independent host-side circuit1 image census appears in the allowed receipts. No engineering cause is assigned.

## Exact read commands

From `/Users/brad/dev/ssx3`: `cat local/muse/prompts/N8D7B.md`; `cat ~/dev/AGENTS.md`; `cat local/AGENTS.local.md`; `cat local/research/N8D6C/ORCH-GATE.md`; `cat local/research/N8D6C/vector-audit.json`; `cat local/research/N8D6A/orch-replay-excerpt.txt`; `cat local/research/N8D4/REPORT.md`; `rg -n 'G37|G38' docs/numbers-ledger.md`; `git -C /Users/brad/dev/ssx3-work/N8D6A/PS2Recomp rev-parse HEAD`; `git -C /Users/brad/dev/ssx3-work/G43/parallel-gs rev-parse HEAD`; targeted `rg -n` and `nl -ba ... | sed -n` reads of the five named source files and `gs/shaders/sample_circuit.frag` at the anchors above. Shader was located with `rg --files /Users/brad/dev/ssx3-work/G43/parallel-gs | rg 'sample|scanout|circuit|shader'`. An exploratory `rg` over nonexistent top-level `shaders`/`util` paths returned no matches; the shader was located under `gs/shaders`.
