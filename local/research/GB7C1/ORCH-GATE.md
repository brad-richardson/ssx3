# GB7C1 orchestrator gate — source design PASS with bounds

Read the whole report and 10-row map; checked worker commit `0378a7b9`
and key CPU raster/sample source anchors in clean GB4 worktree `09d583a`.
The worker did not build, replay or claim a paraLLEl cause. LSP returned
no results; exact caller/callee lines support the main path. The private
pinned capture and true-path sidecar were not reread in this audit.

A bounded default-OFF CPU trace is feasible at the existing replay draw
sites: the off-screen `fbp=0` T4 atlas candidates at tick600 packet47176
and tick699 packet59894 reach `SampleTexture` and `WritePixel`; a later
`fbp=112` full-height blit samples block 0. The exact **post-candidate**
carrier packet is not in the selected 16 rows and must be looked up in
the full private log before an implementation run. Packet47117 is earlier
than the tick600 candidate and cannot carry its new pixels.

Corrections for the implementation brief: the old framebuffer read at
`WritePixel:1181` is conditional on `frmw`; the diagnostic must take its
own read immediately before a successful write and never label a rejected
TEST pixel as a changed pixel. A trace of six to eight chosen pixels alone
cannot establish a glyph-shaped **region**; require a bounded before/after
ROI diff with changed-pixel coordinates or bounding box. Start with C1
only; C2's following blit may fall after the tick700 harness stop. The
current report identifies source hooks and candidates, not a glyph
producer or a rendering defect.

Next GB7C2: pin the first post-47176 carrier packet from the full TSV,
then implement one narrow trace and one same-stream CPU replay with OFF
control, cap and frame views. A separate CPU/paraLLEl comparison is still
needed for any backend-cause claim.
