# N8D7E — selected-input + circuit1 Mac capture design (Muse Go)

You are an OpenCode Go `muse-spark-1.3-contributor` worker on a **read-only
Part 1 design**. Brad has enabled paid training endpoints for this open
hobby project. Follow `~/dev/AGENTS.md` worker rules, repo `AGENTS.md`,
and `local/AGENTS.local.md`. No OpenCode config edit, source edit, build,
boot/replay, device, web, push or upstream contact. Read only this brief;
`local/research/N8D7B/{REPORT.md,ORCH-GATE.md}`;
`local/research/N8D7C/{REPORT.md,ORCH-GATE.md,adapter.tsv}`;
`local/research/N8D7D2/ORCH-GATE.md`; the G37/G38 rows in
`docs/numbers-ledger.md`; and the named sources below. Use LSP
goToDefinition/findReferences to confirm connections when available;
record empty/error. Cite exact file:line anchors. Context target <35k,
wall cap 12 minutes.

Facts: N8D6C's one Odin frame is sparse at circuit1 (21/448 active) but
formal category OTHER after its parser missed logcat continuations; no
selected-source or promotion receipt exists. N8D6A's one pinned Mac stream
replay has circuit1 300/448, but the two streams are not byte-identical.
N8D7D2's **synthetic** single-sample CPU adapter fixture passes twelve
cases and two literal address offsets; its writer and reader share
`swizzle_PS2`. Historical G31 VRAM-misread interpretation was withdrawn by
G37; G38 found an earlier matched-boundary divergence. Do not treat either
as N8D6C cause proof.

Question: where exactly should one default-OFF, bounded **Mac replay**
probe capture the *actual selected input to circuit1* and independently
read back circuit1, without changing draw order? Alternatives for a later
same-frame Odin run: V input sparse/circuit sparse, S input broad/circuit
sparse, T input broad/circuit broad but existing tap sparse. Work out
observable predictions before choosing a capture point.

Read only these paths in pinned
`/Users/brad/dev/ssx3-work/G43/parallel-gs` (record HEAD and dirty state):
`gs/gs_renderer.cpp`, `gs/gs_renderer.hpp`, `gs/gs_interface.cpp`,
`gs/gs_interface.hpp`, `gs/gs_util.hpp`,
`gs/shaders/sample_circuit.frag`, and `Granite/vulkan/command_buffer.hpp`
plus `Granite/vulkan/device.hpp` **only if** directly needed for copy/map
API signatures. Read N8D6A backend
`/Users/brad/dev/ssx3-work/N8D6A/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp`
only for existing stage tap/flags. Use targeted `rg` and line reads; avoid
broad tree scans.

`source-map.tsv` header:
`step<TAB>source_anchor<TAB>selected_input_or_output<TAB>ordering_or_lifetime<TAB>gap`;
exact rows: `priv_snapshot`, `promotion_selection`, `gpu_vram_barrier`,
`input_copy`, `sample_quad`, `circuit1_store`, `circuit1_readback`,
`host_decode_census`, `mac_replay_entry`. If a source API is absent,
write `not found` and the narrow missing fact. Write the table early.

`REPORT.md`: pins, commands, source map, same-frame V/S/T predictions;
**one** candidate capture placement and its order/barriers/selected-source
identity, metadata (tick/FBP/PMODE/PSM/FBW/DBX/DBY/phase/stride/extent/
sample count/promotion), byte cap <6 MiB and default-OFF flag; a script
acceptance table for one pinned Mac same-stream replay and stop branches
for promotion, multi-sample, missing metadata, copy/map mismatch, or
perturbation. State precisely whether the G43 APIs support an ordered
GPU VRAM slice copy and independent circuit1 image-to-host copy; do not
invent a callable path. Design only. Hand back tables and a recommended
Part 2 brief, **do not conclude a cause**. Write only
`local/research/N8D7E/{source-map.tsv,REPORT.md}` (<100 KiB each), commit
those explicit paths as `[N8D7E]` with `Orchestrated-By: opencode`, no push.
