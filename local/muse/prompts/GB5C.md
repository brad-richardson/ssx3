# GB5C Part 1 — bracket replay pixel divergence

You are a Codex worker in `~/dev/ssx3`. Follow `~/dev/AGENTS.md` and
`AGENTS.md`. Read `local/research/GB5B/REPORT.md` and GB4 `REPORT.md`
Part 6. Hand back a table; the orchestrator decides the gate. This is
replay-only evidence gathering, not a renderer fix. No mini, Odin, iOS,
or live boot; no source edits or fork push.

Use the existing local G worktree
`~/dev/ssx3-work/GB4/PS2Recomp` branch `gb4-parallel` at `f796669`
(verify) and run outputs under `~/dev/ssx3-work/GB4/run/gb5c/` only.
Reuse `run/gb4p4.capture.bin` (SHA-256
`a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851`)
and `run/gb4p4.paths.txt`; two matching capture SHA reads before use.
Do not copy the capture or change prior receipts. CPU raw DISPFB1 page
112 PPMs already exist at ticks 899,900,901,902,921,922,949,950.

Correct comparison: replay the **same capture and path sidecar** through
paraLLEl at those eight markers. GB4 Part 6 already ruled out a simple
N±1 present offset at five markers, but it did not bracket the damaged
Setup Character glyphs. GB5B found 13 crop-changing instances of the
recurring 1,696-byte PATH3 composite at ticks 902–921. If paraLLEl
crop damage appears before tick 902, that packet cannot be its first
cause; if it starts during 902–921, inspect packet/state next. This
comparison only brackets a mismatch, not a producer.

1. Verify the eight CPU raw PPM inputs exist and the G pin. Run the
   existing `ps2x_tests` replay harness once with
   `PS2X_GS_REPLAY_BACKEND=parallel`, same capture/path sidecar,
   `PS2X_GS_REPLAY_PPM_TICKS=899,900,901,902,921,922,949,950`, and
   `PS2X_GS_REPLAY_PPM_DIR=../run/gb5c/parallel-ppm` from the G fork
   root. Set `PS2X_GS_REPLAY_STEP=50` as in GB5B. Do not rebuild unless
   the existing binary is absent/stale (one build allowed). Require
   556/556 and zero null/unsupported operations. Cap new PPMs at 100 MiB.
2. Write a small **read-only** comparison script under
   `run/gb5c/` that parses P6 PPMs and, for each tick and both GB5 crop
   rectangles (`upper=(320,120)-(420,205)`,
   `lower=(340,360)-(430,420)`), records CPU/paraLLEl differing pixel
   count, RGB mean absolute error, first differing `(x,y)`, and each
   crop's FNV-1a hash. Also record full-frame differing pixel count.
   Check PPM dimensions/format and fail on mismatch. Do not equate a
   crop hash with glyph-stroke identity.
3. Make side-by-side PNGs for 899,902,921,950 with crop outlines, view
   them, and describe visible differences in plain terms. Keep them
   under `run/gb5c/`, ≤25 MiB total. Compare the earliest observed
   mismatch with `(901,921]` and say what is and is not excluded.

Budget: one GPU replay (+one correction if path/tool failure), ≤1 build,
≤90 min, ≤1 GiB new data. If replay fails after one clear repair, stop
and report; no tuning loop. No speed number from replay. Deliver
`local/research/GB5C/REPORT.md` with pins, exact commands, 8×2 table,
frame observations, suite/stats, data cap and gaps. Commit only the
report `[GB5C]` with trailer `Orchestrated-By: Codex`; no source commit
and no push. The orchestrator will inspect images and choose Part 2.
