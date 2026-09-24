# N8D7M8 orchestrator gate — B, bounded source design (2026-09-24)

Read the complete corrected REPORT and worker commits `57b51229` and `f92c204a`; `git show --check` passed. Reran `check.py`: 34 cited rows, zero errors. Independently checked the selected 4 MiB copy before circuit sampling in the pinned paraLLEl source. This was a read-only design: no build, replay, device action, new frame, or speed number.

The mapped hooks do not identify which live Odin draw completed before the original selected copy. The fork assigns its packet tick/index when the GS worker processes the queue, and the raw-GIF backend passes only path and bytes into paraLLEl. Flush timelines and wait-idle completion cover groups of work, not an identified draw. The existing copy and later circuit sample can distinguish a sparse copy from a broad later source in some cases, but both-sparse cannot separate late writes from writes absent for that Present. Timestamps and labels likewise do not name completed draws. This accepts **B for the inspected source paths**, not proof that no possible device extension exists.

The worker's initial EXP1 recommendation was corrected: a Mac replay serializes the captured stream under different threading and cannot resolve the live Odin EE/GS interleave. EXP1 could calibrate replay logging only. Source checker success establishes cited structure and table consistency, not GPU execution or Turnip behavior. The old N8D4 packet examples do not prove writes on the N8D7M6 same-stream capture.

Next: design, read-only, an identity-carrying witness from EE enqueue through GS worker, raw-GIF recording, submit and the original selected copy; quantify its synchronization and byte costs and test whether it perturbs the order. Do not launch the Odin from this report alone.
