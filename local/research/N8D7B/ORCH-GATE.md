# N8D7B orchestrator gate — 2026-09-24

**PASS as a static feasibility study; no GS-cause or device verdict.** Worker
commit `f32c628` has only `REPORT.md` and `source-map.tsv`, the required
`Orchestrated-By: Codex` trailer, and no whitespace error. The whole report
and all six map rows were read. The source anchors for `sample_crtc_circuit`,
its `sample_quad[promoted ? 1 : 0]` binding, shader `swizzle_PS2`, and the
`circuit1` draw were checked directly in the pinned G43 clone. The report
keeps historical G31 comments separate from G37's withdrawn interpretation
and G38's earlier matched-boundary result.

The V/S/T table predicts distinct pairs for decoded selected input and an
independent circuit1 image census on the *same Odin frame*: sparse/sparse,
broad/sparse, and broad/broad, respectively, while the existing tap is sparse.
Raw VRAM byte occupancy or a hash cannot substitute for decoded input pixels.
`map_vram_read` maps `buffers.cpu`; the draw may use `buffers.gpu` or a
promoted image. The N8D6C receipt lacks per-frame promotion state. The
named sources do not provide an independent host decoder for the shader's
swizzled field coordinates. Accordingly, the probe is a design only and its
decoder feasibility stop is accepted. No new Odin run is authorized by this
gate.

Next: inspect the shader helpers and any existing CPU GS address decoder,
specify a bounded independent decoder and calibration test, then decide
whether to implement the one-frame probe. Keep N8D6C formal OTHER and its
same-run recovered A measurements; do not infer a precise upstream cause.
