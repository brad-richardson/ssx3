# N8D7C orchestrator gate — 2026-09-24

**PASS as a CPU adapter design; fixture and Mac calibration unrun.** Worker
commit `51b23ed` contains only `REPORT.md` and `adapter.tsv`, has the required
`Orchestrated-By: Codex` trailer, and passes `git show --check`. The entire
report was read; an independent TSV check found the eight requested rows,
five populated columns each, and source anchors. The orchestrator checked
`sample_crtc_circuit` push constants and selected binding, `swizzle_PS2`
addressing, and the existing raw tile threshold against the pinned sources.

`gs_util.hpp` already provides host `vram_readback<PSM>` into linear pixels.
It advances Y by one; a 512×224 field with phase stride two needs 224
height-one calls at the shader's Y coordinates. The adapter must use an
ordered copy of the *selected* GPU input, not assume `buffers.cpu` or raw
VRAM when a promoted image is selected. PSM16 payload expansion, sample
count, coordinate wrap, and promotion must be checked before classification.
CPU and GPU call the same `swizzle_PS2` algorithm, so agreeing outputs do
not independently prove the address algorithm. The proposed synthetic
fixture includes literal boundary addresses to constrain that gap.

Next gate: implement and run a bounded, script-checkable synthetic fixture
for the count-one adapter; then perform one pinned Mac same-stream
calibration with independent circuit1 host readback. No Odin run or V/S/T
verdict follows from this static study. N8D6C remains formal OTHER.
