# RR1 — exploratory session: race rendering gaps (missing sky, dark lower region, flat textures) (Opus, 3 h)

You are an exploratory worker, approved by Brad on 2026-09-24. **You choose the experiments.** Goal: find why the race renders without sky/sun, with a large dark lower region and flat textures, on **both** our CPU GS (Mac) and paraLLEl (Odin), and ideally land a fix candidate. Read `~/dev/AGENTS.md` (exploratory freedom overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, `docs/orchestration.md` §3 (exploration mode, reference equivalence), `docs/todo.md` E section ("Race rendering gaps"), then `local/research/{E59,E60,E53,E51,G46,N8X1}/REPORT.md`.

## Facts
- Race world draws (terrain, rider, HUD) on Mac and Odin; sky and sun are gone, foliage missing, textures look flat, a dark region occludes the lower screen (viewed in N9/N10/I30 frames). Same on Mac CPU GS and Odin paraLLEl, so it's upstream of the GS backend or common to both.
- Leads: sky-like packet TBP0 11017 has ALPHA `0x1`/CBP 10756 here vs `0x2a`/14473 in PCSX2 (unmatched scenes); ~60 vs 73–74 IMAGE uploads/vsync (E51; UP1's VIF1 port changed nothing on I26-FAST); 13 vs 23 mip chains; zero-area prims ~15× T65; 9 vsyncs with 33 capped VU1 programs. Ruled out: FPMODE=ieee, the EFU revert, `sceVu0MemReadQ` (E59, E60).
- Tools: `PS2X_DETERMINISTIC=1` + VBlank XXH64 hash tap (E55); GS stream capture + the replay harness now on fork `ssx3` `f949ff0` (desktop replay via `ps2x_tests`); `local/research/G46/g46_rec2gs.py` converts our GS stream to `.gs` for PCSX2's gsrunner; PCSX2 with trace hooks on bytesize (`~/pcsx2-g7`; T47/T48 reference captures; PINE: one client).

## Suggested path (your call)
1. Get a **same-scene** pair: our deterministic race frame and PCSX2's at the same race moment (align by guest state, not wall time). Replay our GS stream in PCSX2's gsrunner: if PCSX2's GS draws the sky from **our** stream, the bug is in our GS; if not, it's upstream (VU1/VIF/DMA/EE producing wrong packets).
2. Bisect upstream: compare the sky draw's packet stream (TEX0/ALPHA/CBP, CLUT uploads) and the VU1 microprogram inputs between ours and PCSX2 at that moment; name the first divergent producer (EE store, VIF unpack, VU1 program, DMA chain).
3. Fix candidate on a local branch with a test; one deterministic Mac boot to the race, frames viewed.

## Rules
- Mac + bytesize only (no Odin, no iPhone). bytesize: one heavy job at a time (AU9 also uses PCSX2 there; check `ps aux` and wait). PINE: one client. Mac boots: one mini lease slot (`p_lane_lease.py`).
- Local branch only (worktree `~/dev/ssx3-work/RR1/PS2Recomp` from `f949ff0`); never push; never `git add -f` in the fork. Scratch `~/dev/ssx3-work/RR1/` ≤ 20 GB. **Text only in git** (no PNG/PPM/binaries). No upstream contact.
- Verify every address/label you name with `local/tooling/ee/{ee-at,ee-func,ee-xref,ee-label}`.
- Time box 3 h from your first command, then write up (15 min); notebook committed every ~30 min.

## Deliverables (commit `[RR1] …`, explicit paths, trailer `Orchestrated-By: Claude Code`, no push)
`local/research/RR1/NOTEBOOK.md` (append-only) and `REPORT.md`: explanation with evidence rows, fix diff SHA + `--stat` (if any) with suite result and runner-dir check, 3–5 frame paths under scratch for the orchestrator to view (ours vs PCSX2, before/after), next steps, gaps; hypotheses labelled.
