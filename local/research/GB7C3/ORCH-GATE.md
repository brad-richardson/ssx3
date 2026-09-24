# GB7C3 orchestrator gate — PARTIAL design, no run

Worker commit `57a7de9b` (`Orchestrated-By: opencode`) contains a
read-only report, four-row candidate table and provenance checker; no
fork edit, build, replay, device action or push. Pinned GB4 fork remains
`7bd8349`. I read the whole report/table/checker and reran it: its
syntactic/provenance checks pass against the saved 320-row GB7C2 trace.

The four proposed source coordinates are real changed C1 pixels in
packet47176, with nonzero T4 nibbles. The candidate destination pixels
fall within packet47240 carrier rectangles. All **observed** carrier
samples, however, came from source y=375 background; the asserted
`src=dst+(1,1)` at glyph y=378/381 is an extrapolation. Neither the
glyph-row carrier sample, its prior destination word, its actual CLAMP,
fbmsk/ABE/vertex color state, nor its swizzled VRAM address was captured.
The table's `src_linear_off` is a linear row offset and explicitly is
**not** a GS storage address. Thus the brief's exact-address and
discriminating-outcome conditions remain unmet.

Verdict: **PARTIAL**. The table is a useful candidate list, but the
proposed one-pixel perturbation is not yet ready to run or interpret.
First instrument and replay one bounded carrier glyph-row sample with
actual UV/CLAMP, source storage address, mask/blend state and destination
old/new. Use those measured values to choose an injection and predict
distinct outcomes before any perturbation. No displayed-glyph or GPU
damage cause follows from this static design.
