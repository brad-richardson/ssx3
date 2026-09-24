# X11 — default dense Qwen scheduler trial, incomplete

This is an orchestrator audit, not a worker verdict. X11 used local
Qwen3.8-27B through opencode with the default `thinking_budget=8192`.
The only allowed source input was the 7,345-byte excerpt at fork
`4f93216` (`source-excerpts.txt`, SHA-256
`21ae4769d3550f3cf5c3ed901d156354555b56ed413775de9a640b3e75342d05`).

| Observation | Result |
| --- | --- |
| Named reads | Brief, pinned excerpt and report skeleton were read. |
| First report write | None by the 3-minute draft deadline or approximately 10-minute total cap. The orchestrator's nudge remained queued while the model stayed in its first reasoning step. |
| LSP probe | Not called. Tool usefulness was not measured in this arm. |
| Source rows / checker / commit | None. The report skeleton remained unchanged until this orchestrator audit. |
| Visible context | OpenCode footer stayed at about 13.9k context (14%) during the long reasoning step. |

The pane was stopped and closed at the cap. No scheduler claim, source
edit, build, boot or device action was accepted from X11. X11B repeats
the same excerpt, rows, LSP probe and checker with only the per-pane
thinking budget reduced to 512; it tests whether the output delay is
caused by the default thinking allowance.
