# TL1 — fold the GS replay harness onto fork `ssx3`, `odin-replay` CLI, GPU path logger

You are the tooling worker. Read `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, `docs/orchestration.md` §3–§6, this brief, then `local/research/N8X1/{REPORT.md,NOTEBOOK.md}` and its `tools/`, `local/research/N8D7M12P7/launch.py`, `local/research/N10/launch.py`. Own `local/research/TL1/`, scratch `~/dev/ssx3-work/TL1/`, and new files under `local/tooling/odin/`. Fork work in a worktree `~/dev/ssx3-work/TL1/PS2Recomp` on local branch `tl1-tools` from fork `ssx3` `d711506`. No push (the orchestrator pushes). No upstream contact.

**Why.** The on-device GS replay harness (shared replay core, Android replay entry, PKTSEQ fingerprint; all default-off) found the Odin black frame, but it lives only on tag `archive/n8d7m12-p5f4` (with N8D5–N8D7 probe commits underneath). N8X1's fast iteration came from ad-hoc scripts (stream surgery, `run_live.sh`). The 09-24 review (`docs/research/review-2026-09-24-time-and-bottlenecks.md`) asks for these as standard tools.

## Part 1 — fork (Mac only, no device)
1. Cherry-pick onto `tl1-tools`, **without** the N8D5–N8D7 probe commits: the replay core (`24801bc`), the Android replay entry (`1a5e3dc`, `a608ed1`), PKTSEQ (`6799681`, `4fa0df1`). Pure adjacent-addition conflicts: keep both and record them; anything that needs a probe commit's code: stop and report which symbol.
2. Add a one-time **GPU path logger**: at paraLLEl backend init, log the chosen hierarchical-binning mode and subgroup size, descriptor-buffer path and sampler-feedback setting (`[gs-path] …`), so a Mac vs Odin baseline can be checked for equivalence. Default-on single line, no per-frame cost.
3. Release build, taps OFF, suite from the worktree root, runner-dir check empty; one Mac replay of stream `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` whose 41 rows equal the Mac ON control (`local/research/N8D7M12P5F4P2/replay-excerpt.txt`, PKTSEQ + GB4_REPLAY). Commit `[TL1] Part 1`, stop, hand back.

## Part 2 — CLI + one device check (after the orchestrator pushes Part 1)
1. `local/tooling/odin/odin_replay.py`: one command to push a stream (skip if the device copy's SHA matches), write `ps2x.env` (replay env + user keys), install an APK if asked, launch once, wait for the tick-N receipt, pull the on-device hashes file and PPM (not logcat rows), diff against a Mac rows file, force-stop, restore env, release the lease; battery `AC powered: true` and ≥ 20 %; keyguard check. Fold N8X1's stream tools (EOP split + markers, variants, nearestify) into `local/tooling/odin/stream_tools.py` with a `--help` each. A `--self-test` mode with no device.
2. One Android APK from the pushed fork tips (N9 recipe on bytesize; one build) and one Odin run of the CLI on `n8d7m6.gs` to tick 2050: expect `[gs-path]` showing the wave64 path and tick-2050 hash equal to N9/N8X1 (`4483c15c` host dump; for replay compare the PPM against the Mac ON PPM visually and report the rows). Commit `[TL1] Part 2`.

Deliverables: `local/research/TL1/REPORT.md`, text receipts only (no PNG/PPM in git). Budget: Part 1 90 min, 1 Mac build; Part 2 90 min, 1 APK build, 1 Odin launch.
