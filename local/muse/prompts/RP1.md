# RP1 — race visual polish: what still looks different from a real PS2 (Opus exploratory, 3 h, Mac + bytesize)

Worker: Claude Code (Opus), exploratory, Brad-approved class. Read `~/dev/AGENTS.md` (exploratory freedom overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, `docs/orchestration.md` §3, then `local/research/{RR1,PX1,RD1,DK1,ST1,HR1,G46}/REPORT.md`.

## Goal
The race now looks like SSX 3 (RR1, RD1, DK1, ST1). Find the remaining visible differences from a real PS2 and fix the most noticeable one. Known open items: RR1's PATH3 window-count gap (17 unmask windows vs PCSX2's ~27, so 3 queued EOP packets incl. the depth pass drain one frame late), the backdrop CLUT question, mip/LOD and fog on distant terrain, snow-spray/particle blending, Brad's earlier "assets popping in and out" (re-check on the current tip), and anything you spot.

## Reference
PCSX2's replay of our stream doesn't draw the race world yet (PX1), so compare against **PCSX2's own runs** on bytesize (`~/pcsx2-g7`, PINE one client, one heavy job at a time; T47/T48/T65 captures and screenshots exist) at matched race moments (race clock + progress % + camera), and against our deterministic Mac frames (paraLLEl, `PGS_HIER_BINNING=force`, I26-FAST or FR1-R1, fork `ssx3` tip). Build a small matched gallery (ours vs PCSX2) of 6–10 moments across the Happiness course; list every visible difference with a guess at its cause.

## Then
Pick the most visible difference, name its mechanism (GS state, PATH3 ordering, VU1 output, texture/CLUT upload, backend), and land one fix with a test and a det boot with frames, if one mechanism is named. Bit-exact checks don't apply to intended behaviour changes: instead show before/after frames and that nothing else changed (det-hash first-diff tick and fields).

## Rules
Fork branch `rp1-polish` from the fork `ssx3` tip; never push; never `git add -f` in the fork; runner-dir check empty. Text only in git (the gallery PNGs stay in scratch; list them for the orchestrator). One mini slot per boot. Time box 3 h; notebook every ~30 min. Commit `[RP1] …` (explicit paths, trailer `Orchestrated-By: Claude Code`), no push. Deliverables: `NOTEBOOK.md` + `REPORT.md` (difference table ranked by visibility, fix SHA + `--stat` + suite + runner-dir check, before/after frames, gaps).
