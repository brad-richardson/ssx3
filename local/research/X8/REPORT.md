# X8 low-thinking dense Qwen trial — incomplete (orchestrator audit)

This is an orchestrator record, not a worker verdict. The X8 opencode
pane used local dense Qwen3.8-27B with a per-tab
`thinking_budget=512` override. It repeated X7's four-family
sign-branch source task from pinned E54D fork commit `1aaed05`.

| Observation | X7 default 8192 | X8 override 512 |
| --- | ---: | ---: |
| First reasoning step after brief read | 7m35s | 45.3s |
| Early report within 3 minutes | No | No |
| Context at stop | about 20.3k after 12m | 43.8k after about 4m |
| Completed worker table / commit | No / no | No / no |

X8 pinned the correct worktree and read the emitter and macro header,
but broad file reads inflated context well past the 18k brief cap.
The pane was closed at that cap breach. No source edit, build, boot,
device use, or accepted semantic conclusion came from X8.

Next controlled trial: hand the model short, exact source excerpts and
fixed tool commands; retain the low thinking budget and require the
table file before any further source search. This tests whether
tool-output size, rather than reasoning time alone, is the remaining
failure mode.
