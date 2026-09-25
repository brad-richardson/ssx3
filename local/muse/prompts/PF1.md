# PF1 — after a finished race, the game jumps to garbage (Opus exploratory, 3 h, Mac)

Worker: Claude Code (Opus), exploratory, Brad-approved class. Read `~/dev/AGENTS.md` (exploratory freedom overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, `docs/orchestration.md` §3, then `local/research/{FR1,CT1,TC1,RD1}/REPORT.md`.

## Observation (FR1 R1)
The first finished stock race (Happiness, 2nd 04:18, results screen, no inputs after the route) ran on until tick 20063, when an indirect call at `0x39e724` (`sub_0039E6B8`: object list walk, `lw $v0,0x48($s0)` → `lw $v1,0x8C($v0)` → `jalr $v1`) jumped to `0x6c058000` (not code; "vtable reads all zero") and `PS2X_MISSING_FUNCTION_POLICY=stop` aborted. Release builds use `ContinueToTarget`, which would hide it. A real PS2 would crash there too, so our runtime put a bad object on that list or corrupted one. Route: `local/research/FR1/` (FR1-R1 = I26-FAST minus the final 30 s down-hold), 1,459 s wall on the Mac at ~0.25×.

## Leads (hypotheses)
- Post-race work with an **empty memory card**: records/ghost save, replay buffer, "save your progress?" path (mc0 empty in tests; Brad plays with a card).
- A freed or reused object (a use-after-free the PS2's allocator would hide differently), an uninitialized object, or a missed interrupt/callback (INTC 5/7 aren't dispatched; CT1/IN1).
- Something our HLE returns wrongly at race end (CD reads, SIF/RPC, `sceMc*`).

## Suggested path (your call)
- Faster reproduction: the F4 build (VU1 recompile, ~0.36×) when F4 pushes, else the F3 tip `ec2dbf1`; `PS2X_UNPACED=1`; maybe also try with Brad's seeded card copy (scratch-only, `~/dev/ssx3-work/E55D16/mc0/`) to see if the path changes. **Approved: up to 1,800 s wall per boot.**
- Watch the object list head / the object at `$s0` (`PS2X_DIAG_WATCH`, diag build) around the race end; find who wrote the bad `0x48` field or inserted the object; `ee-func`/`ee-xref` every address you name.
- One fix candidate with a test if a single mechanism is named; a validation boot that reaches the results screen and idles ≥ 2 min past tick 20063 without a missing target.

## Rules
Mac only; one mini slot per boot (`p_lane_lease.py`); fork branch `pf1-postrace` from the current fork `ssx3` tip; never push; never `git add -f` in the fork; runner-dir check empty. Text only in git; Brad's save bytes never in git. Time box 3 h; notebook every ~30 min.

## Deliverables (commit `[PF1] …`, explicit paths, trailer `Orchestrated-By: Claude Code`, no push)
`local/research/PF1/NOTEBOOK.md` + `REPORT.md`: mechanism with evidence, fix SHA + `--stat` + suite + runner-dir check, frames viewed, gaps.
