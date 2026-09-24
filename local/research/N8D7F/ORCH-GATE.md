# N8D7F orchestrator gate — Mac probe build

Verdict: **PASS for implementation/build handoff only**. The pinned OFF/ON Mac replay remains unrun; no Odin, GS-cause, or speed verdict follows from this gate.

| Check | Orchestrator read |
| --- | --- |
| Worker commits | `3d9678d` in ssx3 contains six named receipts only; private fork `0678dd9` changes one backend file only. Both have `Orchestrated-By: Codex`. Fork runner diff against `14b1e5cb` is empty. Neither fork nor shared G43 was pushed or edited. |
| Source | Read the whole report and both bounded patches. Default-off flag gates the tick-2050 capture. Private G43 copies full contiguous 4 MiB `buffers.gpu` before circuit1 sampling, then copies circuit1 after its readable transition; staging handles survive to backend wait/map. Raw-circuit early return keeps status OTHER. Host decode uses 224 height-one `vram_readback<PSM>` calls and shader-matched PSM16 RGB expansion. |
| Build and suite | Release/Ninja private build succeeded; tapped diagnostics are OFF in CMake cache. One suite run: 585 passed, 0 failed. No frame was generated in this worker gate. |
| Pins and caps | Worker double-read binary `66457eb4…70a804`, N8D4 stream `38ace1a3…3f97d`, codegen `8ea8ed43…2ae662`; source/patch SHA claims match local reads. Private scratch 2.4 GiB <5 GiB, receipts 212 KiB <4 MiB, global internal use 141.1/200 GB. New capture byte bound 5,177,344 <6 MiB. |

Next: orchestrator rechecks all three input SHA pairs, claims a mini lease, runs the exact OFF then ON N8D4 replay from the private fork root, and checks the predeclared 448-tile and 896-tile acceptance conditions. Do not package for Odin before this calibration.
