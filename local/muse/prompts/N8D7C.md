# N8D7C — CPU display-input decoder adapter (Sol medium)

You are a Codex Sol **medium** worker on one read-only source study. Follow
`~/dev/AGENTS.md` worker rules, repo `AGENTS.md`, and `local/AGENTS.local.md`.
Read this brief, `local/research/N8D7B/{REPORT.md,ORCH-GATE.md}`, and the
named source paths below. No build, boot, device, source/config edit, web,
push, or upstream contact. Only write `local/research/N8D7C/REPORT.md` and
`adapter.tsv` (each <100 KiB). Wall cap 10 minutes, context target <30k.
Use LSP goToDefinition/findReferences if available; record empty/error.

Why: N8D6C's one Odin frame was already sparse at circuit1 (21/448 active)
but formal category is OTHER. N8D7B separated three same-frame alternatives:
selected input sparse (V), input broad but circuit1 sparse (S), or both broad
but stage tap sparse (T). A raw GPU VRAM dump is swizzled, and the current
receipt lacks the actual promotion selection. Orchestrator found a potential
CPU helper **outside N8D7B's allowed sources**: G43 `gs/gs_util.hpp`
`vram_readback<PSM>` around lines 50-110 uses `swizzle_PS2` on the host.
This is a candidate, not yet proven equivalent to circuit sampling.

Read only these source files in pinned
`/Users/brad/dev/ssx3-work/G43/parallel-gs` (record HEAD):
`gs/gs_util.hpp`, `gs/shaders/swizzle_utils.h`,
`gs/shaders/data_structures.h`, `gs/shaders/utils.h`,
`gs/shaders/sample_circuit.frag`, `gs/gs_renderer.cpp`,
`gs/gs_renderer.hpp`, `gs/gs_interface.cpp`. Use `rg` within these files,
not broad repo scans. Read the N8D6A backend source only if needed for the
tile threshold/control and cite exact lines. Confirm the host helper's
caller, input buffer, PSM variants, x/y wrapping, output channel packing,
and whether its `src_x/src_y` parameters can represent the shader's
`phase_stride` (especially phase_stride 2). Confirm shader super-sample
validity and promotion branches. Distinguish shared address-code agreement
from independent execution (CPU vs GPU); no claim that two callers of
`swizzle_PS2` validate its algorithm independently.

Deliver `adapter.tsv` with header
`field<TAB>shader_anchor<TAB>cpu_anchor<TAB>adapter_or_gap<TAB>check` and
exactly these rows: `selected_source`, `fbp_base`, `fbw_stride`,
`coordinate_phase`, `psm_payload`, `vram_mask_wrap`, `super_samples`,
`output_census`. Every source claim needs `file:line` anchors. In
`REPORT.md`, give (1) a correct-behavior mapping for **one 512×224 field**;
(2) a bounded CPU adapter design using existing helper if feasible, or the
smallest missing loop/decoder and why; (3) a **script-checkable synthetic
fixture** with nonuniform known pixels that covers FBP, stride, phase,
PSM16/32, and wrap, plus Mac same-stream calibration before any Odin run;
(4) a table of what V/S/T would observe, and stop branches for promotion,
sample count, missing metadata, or mismatched frame; (5) exact source pins,
commands, LSP result and gaps. No implementation or device run. Hand back
tables and a recommended next brief; **do not conclude a cause**. Commit
only the two receipts as `[N8D7C]` with `Orchestrated-By: Codex`, explicit
paths, no push.
