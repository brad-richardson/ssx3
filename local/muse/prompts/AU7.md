# AU7 — does E54C's PINTEH fix restore the menu music's stereo image?

You are the A-lane worker. Read `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md`, this brief, then `local/research/AU6/REPORT.md` (pins and reproduction commands), the E54C entry in `docs/todo.md` (search `E54C PASS`), and `local/research/AU7/midside.py` (orchestrator's measurement; use it unchanged). Cite local files, not the web. Own only `local/research/AU7/` (except `midside.py`, read-only) and private scratch `~/dev/ssx3-work/AU7/`. No push, no board/ledger edit, no upstream contact, no subagents. Fork work in a new worktree `~/dev/ssx3-work/AU7/PS2Recomp` on a local branch `au7-snd`; never `git add -f` inside the fork.

**Why.** Brad listened to AU6's menu capture against an aligned PCSX2 clip: ours sounds like parts are missing, throughout the track, worse when the music gets complex. The orchestrator measured it: **Mid (L+R) matches PCSX2 (NCC 0.9985), but Side (L−R) does not (NCC 0.434, −1.8 dB)**, steady over the minute. So the stereo-panned content is wrong. The EE game code mixes this music. AU6's build (`au6-snd` `045dd6a`) **lacks E54C** (`89bec9b`, fixed PINTEH/PINTH halfword lanes; AU5 found PINTEH in the mixer candidate `0x3CB538`). The sound HLE commits never reached the shipped fork.

**Hypothesis and observable.** H1: the wrong PINTEH lanes caused the side-channel damage; on a build with E54C, `midside.py` Side NCC rises to ≥ 0.95 with Mid unchanged (≥ 0.99). H0: something else in the mixer path; Side NCC stays near 0.43. A value in between is reported as-is.

**Steps.**
1. Worktree from fork `ssx3` `04f3ace`; cherry-pick, in order, `5bb1fdd` `83167d6` `3c895ca` `ddf4f66` (AU2/AU3/AU5 sound HLE + capture). Skip `045dd6a` (snapshot tap, not needed). If a cherry-pick conflicts beyond test registration files (`ps2xTest/CMakeLists.txt`, `ps2xTest/src/main.cpp`), stop and report the conflict.
2. One Release build, diagnostics OFF except the AU5 tag-1 capture, codegen = canonical `~/dev/ssx3-work/codegen-ssx3` (external, `PS2X_GAME_CODEGEN_DIR`). Run `ps2x_tests` from the worktree root; report pass count.
3. One leased boot (one mini slot via `local/tooling/p_lane_lease.py`) with AU6's exact route and capture settings (`~/dev/ssx3-work/AU6/boot.py`; copy it to AU7 scratch and change only paths/binary), ≤ 600 s wall, own PID, release the slot.
4. Convert with `local/research/AU2/au2_pcmcap.py`, then `~/dev/ssx3-work/AU4/venv/bin/python local/research/AU7/midside.py <ours.wav> ~/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav`. Also run it on AU6's `~/dev/ssx3-work/AU6/run/tag1-36k.wav` as the control; it must reproduce Side NCC 0.434.
5. Make `~/dev/ssx3-work/AU7/AU7-menu-tag1.m4a` (same ffmpeg line as AU6), same 64 s span as AU6's clip.

**Stop rules.** Stop on the first failed step (build, suite regression below the fork's own count, boot not reaching the E33 route, capture gap). No tuning loops: one build, one boot. If H0 holds, hand back the table; do not start a mixer investigation.

**Deliverable.** `local/research/AU7/REPORT.md` with pins (branch HEAD, runner SHA ×2, codegen marker SHA), exact commands, the `midside.py` output for AU7 and the AU6 control side by side, suite count, lease/cleanup, gaps. Commit `[AU7] …` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push. Budgets: 60 min, 1 build, 1 boot, scratch ≤ 8 GB.
