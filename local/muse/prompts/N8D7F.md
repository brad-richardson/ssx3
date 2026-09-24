# N8D7F — selected-input/circuit1 Mac probe, build handoff (Sol medium)

You are a Codex Sol **medium** worker. Follow `~/dev/AGENTS.md` worker rules,
repo `AGENTS.md`, `local/AGENTS.local.md`, and orchestration §§1/4/6. Read
this brief; `local/research/N8D7{C,D2,E}/ORCH-GATE.md`; N8D6A `REPORT.md`,
`g43-stage.patch`, and `orch-replay-excerpt.txt`; then only the source files
you edit plus read-only CMake/include metadata needed for the build. LSP if
available, otherwise exact call-site reads. No web, Odin,
Android, iOS, upstream contact or push. You own the sole E/fork mutator slot
for this task. Do not edit shared G43, N8D6A, `ssx3` status/todo/ledger,
runner, generated code or game data.

Make private `~/dev/ssx3-work/N8D7F/`: fork worktree branch
`n8d7f-selected` from N8D6A commit `81682dfb5fa05e6737e12e40531f63bc65dfd6cf`
and a private **copy** of N8D6A `parallel-gs` (which already contains the
G43 private diagnostics plus exact N8D6A stage patch). Pin both source
states/hashes before edits. Allowed edits only fork
`ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` and private G43
`gs/{gs_interface.hpp,gs_renderer.hpp,gs_renderer.cpp}`; if an API needs
another file, hand back the cited gap before editing it. Receipts only
under `local/research/N8D7F/` (<4 MiB); scratch ≤5 GiB, global internal
ssx3 <200 GiB.

Hypothesis/correct model: on the pinned N8D4 stream at tick2050,
FBP112/PMODE `ff21`, 512×448 final, single-sample non-promoted circuit1
input decoded from **the selected GPU VRAM slice** is broad and matches an
independent host census of the 512×224 circuit1 image; existing GPU stage
tap is broad too. Later Odin alternatives are V sparse/sparse, S
broad/sparse, T broad/broad with existing tap sparse. No Mac/Odin streams
are assumed byte-identical. Log selected promotion **after** renderer layer
rejection, sample count, PSM/FBW/DBX/DBY/phase/stride/valid extent, VRAM
mask and tick; stop as OTHER on promotion, count≠1, raw-circuit early
return, unsupported geometry/PSM, missing metadata, allocation/copy/map
error, or any coordinate≥2048.

One candidate: default-OFF `PS2X_N8D7F_SELECTED_CAPTURE=1` gates a single
tick2050 frame. In `GSRenderer::vsync`, copy one **contiguous 4 MiB**
`buffers.gpu` base slice to CachedHost staging with G40-style ordered
barriers **before** `sample_crtc_circuit`; retain the staging handle and
selected metadata in `ScanoutResult`. Preserve N8D6A circuit1 handle;
after its attachment-to-readable transition (or stop at raw early return),
copy the 512×224 circuit1 image independently to host staging. After
submit/wait, backend decodes VRAM using `vram_readback<PSM>` with one
height-one call per row for stride 2 and shader-matched PSM16 expansion;
count both host images with 16×16 tiles, pixel occupied if max RGB≥32,
tile active if ≥32 occupied pixels. Log 448-count packed SHAs, occupied/
active, input-vs-circuit 448-count equality and host-circuit-vs-existing
GPU-stage 448-count equality, plus existing controls. New probe allocation
cap <6 MiB: 4,194,304+458,752+458,752+65,536=5,177,344 B. Flag OFF
must allocate/copy/log nothing new. Do not change output order or final
present. If safe ordering/handle lifetime cannot be established, stop
before editing with a source-path table.

Budget: one implementation candidate, one Release/Ninja configure/build
of `ps2x_tests`, one taps-OFF suite, one named compile repair only. Reuse
N8D6A configure flags, changing only worktree/build/G43 paths. Build with
`nice -n 10 -j 6`, when no other heavy mini job runs. **Do not replay in
the worker sandbox**; hand the exact OFF and ON pinned N8D4-stream commands
to the orchestrator. Orchestrator acceptance script/table: OFF 585/585
and known final hash; ON tick2050/FBP112/PMODEff21, single sample,
promotion=0, both 512×224/448 counts, controls128, input/circuit/stage
tile vectors exact 448/448, circuit/input active≥224, final active≥500,
OFF/ON final hashes equal, zero pipeline errors, total new bytes <6 MiB.
Otherwise OTHER; no Odin release. Counts are functional diagnostics, not
speed numbers.

Deliver `REPORT.md` with source-path table, exact commands/pins, source
diffs and SHA pairs, build/suite logs, binary/stream/codegen double SHAs,
OFF/ON replay commands and gaps. Commit fork backend `[N8D7F]` with
`Orchestrated-By: Codex` after runner-dir guard; no fork push. Preserve
bounded private G43 patch. Commit named receipts in ssx3 `[N8D7F]` with
same trailer, explicit paths, no push. Hand back table and commands;
**do not conclude a device cause**.
