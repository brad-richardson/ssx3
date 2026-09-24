# GB7A orchestrator gate — title-text source map

Verdict: **PASS as a read-only source map with corrections**. No glyph producer, packet identity, texture mechanism or GS cause is established.

I read the whole report and nine-row TSV, reran `check.py` (9 rows, 17,247 bytes, PASS), verified the pinned GB4 fork `f796669`, worker commit `6896f1f` scope and `Orchestrated-By: opencode` trailer, and independently checked the GS packet seam, TEX0/CLAMP decode, CPU sprite raster and Present source anchors. The map correctly places the first shared instrumentation seam at `GS::processGIFPacket` before the raw-GIF fanout. The worker correctly treats tick-950 packet 144266 as a display sprite candidate, not a proved glyph producer; the earlier visible damage is at copyright text by tick 300 and button labels by tick 700.

Two corrections constrain the proposed Part 2:

1. The TSV's upload-path cell calls the capture source `ps2x_gs_capture.cpp`. The file is `ps2xRuntime/src/lib/gs/gs_stream_capture.cpp`; `ps2x_gs_capture` is its namespace. A later brief must cite the actual file.
2. With one pinned capture replayed twice, the packet bytes at the shared seam should already be identical. The proposed A1 packet-entry log is an **input/null control**; a mismatch means a replay/capture-path fault, while equality cannot by itself identify the guest text producer. The first useful discriminator after that is per-draw state and source texels for a spatially identified glyph batch. The G43 paraLLEl source pin and full capture SHA need to be fixed before that run.

Next: a bounded Part 2 instrumenting spatially identified title-text draws at existing markers 300/600/700, with packet-input equality as the null control, then compare per-batch state, texture-source bytes and the cropped output. Stop if no unique glyph batch can be identified under the byte cap; hand the candidate table back before a device run. No new replay or device action occurred in this gate.
