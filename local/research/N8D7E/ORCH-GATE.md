# N8D7E orchestrator gate — 2026-09-24

**PASS as a read-only capture design with three corrections; no Mac replay,
Odin or GS-cause verdict.** Muse Spark 1.3 Contributor via OpenCode Go
accepted the task after Brad enabled paid training endpoints. Worker commit
`40e457d` contains only `REPORT.md` and `source-map.tsv`, with the required
`Orchestrated-By: opencode` trailer and no whitespace error. The whole report
and nine-row map were read; the orchestrator checked the map's order/shape,
the G43 `sample_crtc_circuit` source binding, G40 GPU-buffer and image
staging-copy APIs, the `vsync` circuit1 barrier/early-return branches, and
the N8D6A private stage patch. Pane showed **2m24 and 82.7k context**, above
the <35k target; LSP was not used after an orchestrator budget nudge.

The design correctly identifies two callable copy paths: ordered
`buffers.gpu` to CachedHost staging via `copy_buffer`, and circuit1 image to
staging via `copy_image_to_buffer`, each with appropriate barriers and
post-submit mapping. `map_vram_read` maps `buffers.cpu` and cannot stand in
for a selected GPU input. It correctly requires logging whether promotion
survived the layer-count check and stopping on unsupported sample modes.

Corrections for Part 2:

1. `vram_readback<PSM>` indexes a full VRAM slice by absolute swizzled
   addresses. A compact copy of only selected pages is unusable without an
   explicit remapping adapter. Use one contiguous **4 MiB GPU slice** for
   the first probe, or prove a remap before calibration.
2. Circuit1 retention for N8D6A was added by
   `local/research/N8D6A/g43-stage.patch` in paraLLEl-GS
   `gs_renderer.hpp/cpp`, with backend use in `fork-backend.patch`.
   It is not solely a fork-backend extension. Build Part 2 on those exact
   stage-patch files and check the raw-circuit1 early-return path before
   choosing the readback barrier/copy placement.
3. The report's byte sum is wrong: 4,194,304 + 458,752 + 458,752 + 65,536
   = **5,177,344 bytes**, still below its 6 MiB cap. The two images and
   metadata must remain bounded, and no extra double-buffer copy is counted.

The next brief should implement one default-OFF candidate in an isolated
G43/fork workspace, rerun the synthetic fixture, and calibrate once on the
pinned N8D4 stream on Mac. Define exact same-frame V/S/T thresholds and
stop on missing selected-source identity, mismatched geometry or capture
failure. No Odin run is authorized by this gate. Historical G31 misread
interpretation remains withdrawn per G37.
