# GB5 Part 1 — Which replay packet changes the damaged glyph pixels?

You are a Codex worker in `~/dev/ssx3`. Follow `~/dev/AGENTS.md` and
`AGENTS.md`. Read `local/research/GB4/REPORT.md` Part 6,
`local/research/GB4/glyph-packet-p6.txt`, and
`local/research/X5/REPORT.md` first. Hand back evidence tables; the
orchestrator decides the mechanism and next step.

Problem: paraLLEl replay of GB4's capture has broken strokes in Setup
Character text even when CPU raw read and CPU Present agree on the same
display page. At tick 950, packet 144266 is a PATH3 full-height sprite
composite that covers the area, but it is **not proved** to draw the
glyphs. X5 has a verified 922-row index for ticks 949–950. The CPU
reference and paraLLEl image are side by side in
`local/research/GB4/parallel-side-950-p6.png` (512×448 each).

Hypotheses: H1 the composite packet changes the damaged crop; H2 an
earlier texture/upload or draw packet changes it; H3 CPU output is
unchanged there by all packets in this window (earlier state). The
observable is the **first packet index whose replay advances the CPU
display-page pixel values** in two crops, not a GIF bounding box.

## Scope and method

Use only `~/dev/ssx3-work/GB4/PS2Recomp` (`gb4-parallel` at `c5913e4`),
`~/dev/ssx3-work/GB4/` for bounded build/replay outputs, and
`local/research/GB5/` for report/text receipts. Do not touch the E/W1F2
worktree, fork `ssx3`, the existing capture/path files, or GB4's prior
receipts. No device or mini boot. Wait while W1F2 Xcode builds are active.

First confirm the capture SHA and X5 index, then inspect the existing
`PS2GSReplay` case and CPU raw display-page read. Add one **replay-only,
default-off** probe that emits a compact row after each packet in the
tick-949/950 window whose CPU page-112 pixel crop changes. Use two
per-frame crops in 512×448 coordinates: upper text `(320,120)-(420,205)`
and lower labels `(340,360)-(430,420)`. Hash decoded pixels, not raw
VRAM bytes. Every row: tick, packet index, corrected path, GIF byte/FNV
from X5, before/after crop hash and changed-pixel count. Limit output to
1,000 rows and avoid full-frame dumps per packet. Record how the probe
matches X5's packet numbering. Use one CPU replay run; inspect the
existing final tick-950 CPU image as the control. If the existing replay
API cannot expose an intermediate CPU page without changing guest/GS
semantics, stop with the exact API gap and a proposed seam; do not guess.

Only if the row table points to a single candidate packet, use one
replay-only negative control that drops **that one** packet and compare
the final CPU crop hash/image with baseline. Preserve all other packet
ordering and paths. Do not interpret the paraLLEl defect from CPU-only
data; this Part 1 identifies producer candidates for a later backend
differential.

Budget: one configure/build attempt plus one correction, at most two
CPU replays, 90 minutes, ≤2 GB new files. Reuse the 2.75 GB capture;
no copy. Run the host replay suite from the fork root if source changes,
and state counts. Do not push `gb4-parallel` or fork `ssx3`. Commit any
probe source as `[GB5]` on the local G branch, with
`Orchestrated-By: Codex`; no generated guest files. Write
`local/research/GB5/REPORT.md` with exact pins, commands, hashes,
candidate table, observed crop pixels, negative-control result or gap,
and budget. Commit report `[GB5]` on ssx3 with the same trailer; no
ssx3 `main` push. Stop at the first failed gate after one clear repair.
