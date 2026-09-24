# N8D7D — synthetic CPU display-field fixture

## Outcome and pins

**FAIL_COMPILE_CAP.** The first host compile failed because the command ran from `ssx3`, so `gs/gs_util.hpp` was outside its relative include paths (`compile.txt`). The one allowed correction changed the command to run from the pinned G43 root. That recompile failed at `Granite/vulkan/vulkan_headers.hpp:33:10` because `volk.h` was not found (`compile-final.txt`). Per the brief's one-compile-plus-one-fix cap, no executable was produced and the fixture was not run. No binary remains to remove. No game build, boot, device access, source edit in G43, web access, push, or upstream contact occurred.

G43 checkout: `/Users/brad/dev/ssx3-work/G43/parallel-gs` HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`; preexisting working-tree diagnostics in `CMakeLists.txt`, `Granite`, `gs/gs_interface.cpp`, `gs/gs_renderer.cpp`, `gs/gs_renderer.hpp`, `tools/CMakeLists.txt`, and `tools/gs_dump_replayer.cpp`. The fixture source is `fixture.cpp`; machine-readable run status and planned cases are in `result.json`.

## Case table

All cells marked **not run** have no measured value. A compile failure does not classify any case as an unsupported format or an algorithm failure.

| Case | PSM | FBP | FBW | DBX/DBY | Phase/stride | Pixel mismatches | Tile mismatches | RGBA bytes | Tile counts |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| fbp_0 | PSMCT32 | 0 | 8 | 0/0 | 0/1 | not run | not run | not run | not run |
| fbp_112 | PSMCT32 | 112 | 8 | 0/0 | 0/1 | not run | not run | not run | not run |
| fbw_8 | PSMCT32 | 1 | 8 | 0/0 | 0/1 | not run | not run | not run | not run |
| fbw_9 | PSMCT32 | 1 | 9 | 0/0 | 0/1 | not run | not run | not run | not run |
| phase_0_stride_1 | PSMCT32 | 1 | 8 | 3/4 | 0/1 | not run | not run | not run | not run |
| phase_1_stride_1 | PSMCT32 | 1 | 8 | 3/4 | 1/1 | not run | not run | not run | not run |
| phase_0_stride_2 | PSMCT32 | 1 | 8 | 3/4 | 0/2 | not run | not run | not run | not run |
| phase_1_stride_2 | PSMCT32 | 1 | 8 | 3/4 | 1/2 | not run | not run | not run | not run |
| psmct16 | PSMCT16 | 1 | 8 | 3/4 | 1/2 | not run | not run | not run | not run |
| psmct16s | PSMCT16S | 1 | 8 | 3/4 | 1/2 | not run | not run | not run | not run |
| wrap_32 | PSMCT32 | 511 | 8 | 64/0 | 0/1 | not run | not run | not run | not run |
| wrap_16 | PSMCT16 | 511 | 8 | 64/0 | 0/1 | not run | not run | not run | not run |

The fixture has literal golden expectations for byte offsets 917504 at FBP112/(0,0) and 0 at PSMCT32 FBP511/DBX64/(0,0); neither was executed. Expected and actual output hashes, full 458752-byte RGBA length, 448 tile counts, and alias checks also remain unmeasured. `result.json` records these as null rather than zero. The planned writer calls `swizzle_PS2` to fill source VRAM and rejects conflicting writes to aliased addresses; expected pixels come only from deterministic coordinate formulas. Shared writer/readback address code limits independence even if a later run passes.

## Source anchors and commands

`gs/gs_util.hpp:49-93` defines `vram_readback<PSM>`, including the helper's `& 2047` coordinate handling and raw PSMCT32/16/S payload outputs. `gs/shaders/swizzle_utils.h:329-342,352-379,405-420,444-459` defines page and pixel addressing with byte-mask wrap. `gs/shaders/data_structures.h:116-126,273-288` defines page/block constants and PSM values. `gs/shaders/utils.h:61-86` defines 16-bit color expansion. `gs/shaders/sample_circuit.frag:41-70,98-119` defines the non-promoted, count-one address and payload path. `gs/page_tracker.hpp:7-10` and `Granite/vulkan/vulkan_headers.hpp:33` identify the transitive include chain that stopped compilation. LSP was unavailable in this Codex tool set; tool-name discovery found no LSP tool.

Read: `cat local/muse/prompts/N8D7D.md`; `cat /Users/brad/dev/AGENTS.md`; `cat local/AGENTS.local.md`; `cat local/research/N8D7C/{REPORT.md,ORCH-GATE.md,adapter.tsv}`; `git status --short && git rev-parse HEAD && wc -l ...` in G43; and the five named G43 source files. First compile, from `/Users/brad/dev/ssx3`:

```text
c++ -std=c++17 -O2 -Igs -IGranite/math -IGranite/vulkan -IGranite/util -IGranite/third_party -I. local/research/N8D7D/fixture.cpp -o /tmp/n8d7d-fixture > local/research/N8D7D/compile.txt 2>&1
```

One corrected compile, from `/Users/brad/dev/ssx3-work/G43/parallel-gs`:

```text
c++ -std=c++17 -O2 -I. -Igs -IGranite/math -IGranite/vulkan -IGranite/util -IGranite/third_party /Users/brad/dev/ssx3/local/research/N8D7D/fixture.cpp -o /tmp/n8d7d-fixture > /Users/brad/dev/ssx3/local/research/N8D7D/compile-final.txt 2>&1
```

Recommended next step: have the orchestrator issue a new bounded brief that supplies G43's `volk.h` include path or avoids `gs_util.hpp`'s transitive Vulkan includes, then compiles and runs the fixture. This receipt makes no GS-cause or Mac/Odin claim.
