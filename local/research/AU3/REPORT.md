# AU3 report: blocked before implementation

Brief: `local/muse/prompts/AU3.md`. Worker: Codex. Commit trailer requested:
`Orchestrated-By: Codex`.

## Stop condition

| Item | Result | Evidence |
| --- | --- | --- |
| Required checkout | Not created | AU3 requires a worktree off the PS2Recomp fork at `ssx3` `eac6cba`, with AU2 commit `7c2a02e` cherry-picked, on local branch `au3-snd`. |
| Worker write scope | Conflict | `~/dev/AGENTS.md` says “Write only inside the folder you were started in.” The start folder is `/Users/brad/dev/ssx3`; the required fork checkout is `~/dev/PS2Recomp`, outside it. |
| Existing worktrees | No suitable checkout | `git worktree list` in the start folder listed only `/Users/brad/dev/ssx3` at `5b2e922` (`main`). |
| Implementation, build, tests, boots | Not run | Stopped before the first operation that would write outside the allowed folder. |
| Runner SHA ×2 | Not found | No AU3 runner was built or used. |
| Suite count | Not found | No suite was run. |
| Runner-dir check | Not run | No fork branch was created or pushed. |

## Context read

Read `AGENTS.md`, `local/AGENTS.local.md`, all of `local/research/AU2/REPORT.md`
(including §AU2-4), and `local/research/AU1/REPORT.md` including the semaphore
36 and sound-thread sections. AU2 reports that tag 1 contains 384 stereo s16
frames per tick at 36 kHz, and the type-0 cid-1 handler stores the tag-buffer
address and signals semaphore 36. AU2 also documents the harness/LLDB lease
incident; no debugger was attached and no lease or boot was used here.

## Repository state at stop

The start-folder checkout was `main` at `5b2e922`. Before this report was
created, `git status --short --branch` showed pre-existing modifications to:

- `local/research/N5/scripts/__pycache__/launch.cpython-314.pyc`
- `local/research/N5/scripts/launch.py`
- `local/research/N5/scripts/mem_governor.sh`

These are outside AU3 and were left untouched.

## Required next action

The orchestrator must provide a worker start folder or authorization/workflow
that allows creating and editing the required fork worktree. No implementation
recommendation is made because the brief's code and validation work did not
start.
