# GB5 Part 2 — locate the earlier glyph pixel producer

You are a muse worker in `~/dev/ssx3`. Follow `~/dev/AGENTS.md` and
`AGENTS.md`. Read `local/research/GB5/REPORT.md`, GB4 `REPORT.md` Part 6,
and the relevant `ps2_gs_replay_tests.cpp` probe before editing. Hand back
the evidence table; the orchestrator decides the mechanism. This is a G
replay lane, independent of the running E54B mini boot. Do not use the mini,
Odin or iOS devices.

At ticks 949–950 the CPU raw display-page 112 crop has text, but none of
922 indexed GIF packets changed either crop during processing. This leaves
an earlier GIF draw, a non-packet update, or the probe's display-page
assumption. At tick 899 the saved CPU PPM already shows Setup Character
text. Correct behavior: if a packet first produces the crop, a decoded
CPU pixel hash changes after that packet; if a non-packet event does, it
changes between packet probes or at a capture marker. A bounding box is
not proof of pixel production.

Use only `~/dev/ssx3-work/GB4/PS2Recomp` local `gb4-parallel` at
`b7d3227` and `~/dev/ssx3-work/GB4/run/`; report/text receipts under
`local/research/GB5B/`. Reuse `run/gb4p4.capture.bin` (SHA-256
`a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851`),
never copy it. Do not touch E, W, canonical codegen, prior capture or
prior receipts. No fork or ssx3 push.

1. Verify the capture SHA twice and the G branch pin. Inspect saved raw
   CPU PPMs at 899/900/901 and 949/950; calculate the two GB5 crop
   hashes and compare them with `GB5_FINAL` to identify a changed marker
   interval. View the images. Avoid assuming the text first appears at
   899: inspect earlier markers with **one** bounded CPU replay, selecting
   periodic PPM ticks up to 899 (coarse spacing ≤100 ticks). Cap new PPM
   output at 100 MiB.
2. Narrow to the first marker interval with nonblack/changed text. Extend
   the existing default-off crop probe only as needed to target that
   interval and record packet index, tick, path, GIF length/FNV, and
   before/after decoded crop hashes. Verify record numbering against the
   capture reader and pklog where available. Include non-packet capture
   records in the timeline or state the exact API gap. One targeted CPU
   replay plus, if needed, one correction replay. Cap rows at 1,000.
3. If one packet is identified, use the remaining replay budget for a
   one-packet omission control; compare the final crop hashes. If no
   packet changes it, report the tightest interval and event class. Do
   not infer the paraLLEl renderer defect from CPU-only results and do
   not make a backend fix in this part.

Budgets: ≤3 CPU replays total, 1 build + 1 correction, 90 minutes,
≤2 GB new data. Run the default host suite if source changes. Before any
source commit, check `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`
empty. Commit source `[GB5B]` on the G branch with `Orchestrated-By: Muse
Code`, and a bounded `local/research/GB5B/REPORT.md` on ssx3 main with
the same trailer; no push. Report exact commands, pins, hashes, replay
counts, changed interval/packet table, suite counts, viewed frames,
limits and gaps. Stop on a failed gate after one clear repair.
