# RD1 — the player's rider is mostly missing in races; AI riders look normal (Opus exploratory, 3 h, Mac + bytesize)

Worker: Claude Code (Opus), exploratory, Brad-approved class. You choose the experiments. Read `~/dev/AGENTS.md` (exploratory freedom overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, `docs/orchestration.md` §3, then `local/research/{RR1,UV1,GB8,F2,E38,E39}/REPORT.md`.

## Observation
Brad (09-25, iPhone, paraLLEl build `0ed07c4`, playing **Mac** from his save): "my character's 3D model is mostly missing during the race, where the other racers look normal." Our own Mac race frames (I26-FAST picks **Zoe**) show the player's rider faint/see-through at screen centre (e.g. `~/dev/ssx3-work/F2/run/B1/frames/snap/snap-002090t-0062.47s.png`, `~/dev/ssx3-work/RR1/run-g/frames/upload-latest.png`), while the rival looks solid. E38/E39 once saw "no 3D rider model" at Select Character (since fixed).

## Leads (hypotheses, not facts)
- **UV1:** V2/V3 UNPACK leave z/w (V2) or w (V3) stale; PCSX2 fills them (`local/research/UV1/REPORT.md`, 53 % of unpacks). Skinned player models often pack weights/normals/UVs as V2/V3. **UV1 Part 2 (same fork base) is implementing the PCSX2 rules now** on branch `uv1-unpack` in `~/dev/ssx3-work/UV1/PS2Recomp`; check its state first (`git -C ~/dev/PS2Recomp log --oneline 0ed07c4..uv1-unpack`) and try your repro on its build before anything else.
- Player-only assets: the player's rider streams a high-detail texture pack (`DATA/CHAR/<NAME>TXP.BIG`, e.g. `MACTXP.BIG`, `ZOETXP.BIG`) and may use a different VU1 program (skinning with more bones), a different alpha/fog path, or a motion-blur/ghost pass.
- Reference: PCSX2 on bytesize (`~/pcsx2-g7`, T47/T48 captures, gsrunner; PINE one client; one heavy job at a time) and `local/research/G46/g46_rec2gs.py` / RR1's `rr1_cap2gs.py` to replay our GS stream in PCSX2 (upstream vs GS test).

## Suggested path (your call)
1. Same-scene pair: our race frame vs PCSX2's with the same rider. Replay our stream in PCSX2's gsrunner: if PCSX2 also draws the rider faint from our stream, it's upstream of the GS.
2. Isolate the rider's draws (texture TBPs of the TXP pack, VU1 program startPC, vertex counts, ALPHA/TEST/FBA state), compare with PCSX2's, name the first divergent producer (UNPACK, VU1 program output, texture upload, GS state).
3. One fix candidate with a unit test on a local branch, a deterministic Mac boot with frames viewed (Zoe via I26-FAST; also Mac if you can route to him cheaply: the menu defaults to Mac only with Brad's save — use a copy of `~/dev/ssx3-work/E55D16/mc0/` as `PS2X_MC_ROOT` **in scratch only**, never committed).

## Rules
Mac paraLLEl env (`PS2X_GS_BACKEND=parallel`, `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`, `PGS_HIER_BINNING=force`), `PS2X_SOUND=1`, deterministic. One mini slot per boot. Local branch `rd1-rider` from fork `ssx3` `0ed07c4` in `~/dev/ssx3-work/RD1/`; never push; never `git add -f` in the fork; runner-dir check empty. Text only in git; Brad's save bytes never in git. Verify labels with `local/tooling/ee/*`. Time box 3 h, notebook every ~30 min.

## Deliverables (commit `[RD1] …`, explicit paths, trailer `Orchestrated-By: Claude Code`, no push)
`local/research/RD1/NOTEBOOK.md` and `REPORT.md`: mechanism with evidence rows, fix SHA + `--stat` + suite + runner-dir check, before/after frame paths for the orchestrator to view, gaps.
