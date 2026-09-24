# X6 sparse LWU index trial — incomplete (orchestrator audit)

This is an orchestrator record of the failed model trial, not a worker verdict.

| Item | Observed result |
| --- | --- |
| Worker | Local Qwen3.6-35B-A3B via opencode, herdr w2:p2K |
| Brief | `local/muse/prompts/X6.md` at `463c5d6` |
| Task | Write a bounded parser for static LWU comments in generated `sub_*.cpp`, produce a unique guest-site CSV, rerun it, and compare hashes |
| Outcome | Worker exceeded its 25k context cap (about 36.9k) in roughly five minutes without the named parser, CSV, report, or commit |
| Intervention | Orchestrator gave two narrow corrective prompts; the worker continued looking for unrelated or nonexistent helper/output files. The pane was closed. |
| Evidence status | No LWU count or site conclusion from this trial is accepted. No build or boot was run. |

This contrasts with X5's script-checked extraction, which did complete. A future sparse trial should be given an existing parser skeleton and only fixed input/output paths and a mechanical hash check. The E54 LWU gate remains open.
