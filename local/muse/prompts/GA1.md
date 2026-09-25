# GA1 — GIF arbiter drain-sort inversions (muse, 2 h, Mac)

Execute `docs/research/review-2026-09-25-fable.md` §1 "Brief sketch, suspect 1 (GA1)" — **Part 1 only** (measure; no arbiter change). Pins and rules:
- Base fork `ssx3` **`56a5e8a`**; worktree `~/dev/ssx3-work/GA1/PS2Recomp`, branch `ga1-order`. The `PS2X_PK_ORDER=<file>` tap is default-off and compiled in only behind its own `PS2X_ENABLE_PK_ORDER` CMake option (release unchanged).
- Code: `ps2_gif_arbiter.cpp:91-129` (drain sort), `ps2_memory.cpp:2245,2332,2355,2361` (drain/noteSubmit sites) — confirm with `lsp` before editing.
- One det boot (paraLLEl env as GB8, I26-FAST, empty mc0, `PS2X_DETERMINISTIC=1`) to t2400, one mini slot. Script `local/research/GA1/inversions.py`: inversions per vsync (processed order ≠ submit order across paths), the first ten with EE tick, path, bytes, and whether a PATH3 IMAGE packet was processed after a PATH1/2 draw submitted later in the same drain. Compare tick 1795 with the PCSX2 order (`local/research/RR1/rr1_timeline_pcsx2.py`, `~/dev/ssx3-work/RR1/pcsx2-timeline.txt`).
- Budget: 1 build (+1 if a test flag needs it), 1 boot (+1 spare), 2 h. Never push; runner-dir check empty; text only in git; scratch ≤ 10 GB. First failure: stop, hand back.
- Deliverable: `local/research/GA1/REPORT.md` (inversion table, per-vsync counts, PCSX2 comparison, recommendation for Part 2 per the review's stop rule); commit `[GA1] Part 1 …` (explicit paths, `git add -f`, `Orchestrated-By: Muse Code`), no push.
