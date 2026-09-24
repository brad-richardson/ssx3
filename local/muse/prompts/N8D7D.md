# N8D7D — synthetic CPU display-field fixture (Sol medium)

You are a Codex Sol **medium** worker. Follow `~/dev/AGENTS.md` worker
rules, repo `AGENTS.md`, and `local/AGENTS.local.md`. Read this brief,
`local/research/N8D7C/{REPORT.md,ORCH-GATE.md,adapter.tsv}`, and only the
G43 source files named below. This is a host-only synthetic test of the
single-sample CPU adapter, a prerequisite for a Mac replay and Odin probe.
No game build, boot, device, fork/G43 source edit, web, push, or upstream
contact. Write only `local/research/N8D7D/{fixture.cpp,result.json,REPORT.md}`
and bounded compile/output text receipts there (<100 KiB each, total <1 MiB).
Do not commit a compiled binary. Wall cap 15 minutes; context target <35k.

Pinned source: `/Users/brad/dev/ssx3-work/G43/parallel-gs` HEAD
`3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`, working-tree diagnostics
present. Read `gs/gs_util.hpp`, `gs/shaders/swizzle_utils.h`,
`gs/shaders/data_structures.h`, `gs/shaders/utils.h`, and
`gs/shaders/sample_circuit.frag`. Read CMake/include metadata only if needed
to compile the fixture. Cite exact anchors. Use LSP if available; record
empty/error otherwise.

One hypothesis: `vram_readback<PSM>` with **one height-one call per row**
for phase stride two, followed by shader-matched payload expansion, yields
the expected 512×224 RGBA field for non-promoted `SUPER_SAMPLES=1` input.
Alternatives: wrong FBP/FBW or wrap addressing, wrong phase/stride, wrong
PSM16 expansion. Observable: per-case pixel mismatch count, 448 tile-count
mismatch count, and literal golden boundary addresses. Do not use
`vram_readback` or `swizzle_PS2` to generate expected output pixels. A
fixture writer may use `swizzle_PS2` to populate source VRAM, but separately
assert the literal boundary addresses from N8D7C and disclose that shared
address code limits algorithm independence. Use deterministic nonuniform
pixel formulas and reject conflicting writes to an aliased address.

Run these cases at 512×224: PSMCT32 FBP 0/112; FBW 8/9 with a page-Y
crossing; phase (0,1) × stride (1,2) with DBX3/DBY4; PSMCT16 and PSMCT16S
with exact 5-bit RGB/alpha expansion; FBP511 page-wrap for PSMCT32 and
PSMCT16. Check all pixels and 32×14 tile counts (`max RGB>=32` per pixel,
active tile `>=32` hits). Golden offset examples from N8D7C: FBP112 pixel
(0,0) at byte 917504; PSMCT32 FBP511/DBX64/DBY0 pixel (0,0) wraps to
byte 0. If a case's aliases make unique nonuniform values impossible,
state and narrow that case; do not silently overwrite.

Budget: one host compile, one fixture execution; after one clear compile
error, one edit/recompile is allowed, then stop. No broad build. The
executable goes under `/tmp`, removed after run. `result.json` must record
source pin, compiler command, case parameters, expected/actual pixel and
tile mismatch counts, golden offsets checked, output lengths/hashes, and
any unsupported case. PASS requires every supported case to have zero
mismatches, full 458752-byte RGBA output, 448 tile counts, and both literal
offset checks; otherwise hand back FAIL/OTHER with exact evidence. No GS
cause verdict and no Mac/Odin claim. `REPORT.md` gives the full table,
commands, source anchors, gaps and recommended next step. Commit only
allowed receipts `[N8D7D]` with `Orchestrated-By: Codex`, explicit paths,
no push. Hand back the table; **do not conclude an upstream cause**.
