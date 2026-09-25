# UP1 — upstream harvest from ran-j/PS2Recomp (Part 1 read-only map, Part 2 targeted ports)

You are the E-lane worker. Read `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, this brief. Cite the fork and local reports, not the web. Own `local/research/UP1/` and scratch `~/dev/ssx3-work/UP1/`. **No upstream contact** (read-only git fetches only). No push. No subagents.

**Why.** Upstream `ran-j/PS2Recomp` merged one large squash `75d729c` (09-19, 139 files, +15.6k/−9.1k) since our base `14b1e5cb`. Our fork `ssx3` (`fb11e18`, ~150 commits over the base) has its own versions of much of it. A wholesale merge/rebase is parked (Brad, 09-24). We want the few upstream fixes we lack, as small ports with tests. Our fork's remote branch `fork/feature/iop-emulator` holds the same work **un-squashed as 17 commits** (`git log --no-merges 14b1e5cb..fork/feature/iop-emulator`); map those, not the squash.

## Part 1 — map (read-only, no builds)

For each of the 17 commits and each named sub-item in its message (e.g. "fix wrong mmi instruction translation", "fix texture caching", `SET_GPR_ZE32`, "split SIF and IOP memory", "EE timers decoder", "cri dtx loading", analyzer constant-producing scan, ELF parser entry detection, EE scheduler refactor, GS architecture change, IOP emulator/LLE removal, VFS, VIF1 GIF image packets), write one row:
- files/functions touched (upstream);
- the equivalent in our fork, if any (cite commit + file:line; e.g. E54D LWU zero-extend vs `SET_GPR_ZE32`, our EE scheduler, AU sound HLE vs their IOP emulator, `extra_function_starts` vs their entry discovery);
- **class:** already fixed ours / needed (we have the bug) / irrelevant to SSX 3 / conflicts with our design;
- for "needed": the evidence (a failing case you can state: instruction, inputs, expected vs ours per PCSX2 or the EE manual cited in-repo), the smallest port, the test that proves it, and whether it changes codegen (needs regen).

Pay particular attention to the **MMI translation fix** (MMI lane bugs cost us the stereo image, AU7) and the **texture caching fix** + `ps2xTest/gs_cache/*` tests (our menu artifacts/square snowflakes are wrong texture-page contents upstream of the GS, G44/G46). Use `local/tooling/ee/{ee-at,ee-func,ee-xref,ee-label}` for any SSX 3 code site you name; name nothing ee-label calls unknown.

Deliver `local/research/UP1/REPORT.md` with the table, a ranked list of 2–4 recommended ports (value to the milestone, risk, codegen impact), and gaps. Commit `[UP1] Part 1` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`). **Stop and hand back** the table and ranking.

## Part 2 — ports (only after the orchestrator picks from your ranking)

Worktree from fork `ssx3` under `~/dev/ssx3-work/UP1/PS2Recomp`, one commit per port (message cites the upstream commit), a failing-then-passing test for each, taps-OFF suite from the worktree root, runner-dir check empty. If a port changes codegen: regenerate into a new dir and run one I26-FAST Mac boot to the race (one mini lease slot, ≤ 600 s), frames viewed. Commit `[UP1] Part 2`. Budgets: Part 1 90 min; Part 2 per the orchestrator's release.
