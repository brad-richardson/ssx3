# GB4 report — execution stopped before Part 1

| Item | Result |
|---|---|
| References read | `local/AGENTS.local.md`; all of GB3 report (including §§0, 5, 6, 8); GB2 Part 1 report including the 256-packet captured-stream test template |
| Required fork worktree | `~/dev/ssx3-work/GB3/PS2Recomp`, branch `gb3-gs` at `574354a`; not created or modified |
| Stop reason | The worker rule in `~/dev/AGENTS.md` says “Write only inside the folder you were started in.” This session started in `~/dev/ssx3`. GB4 requires worktree, builds, capture and replay under the sibling `~/dev/ssx3-work/GB3`, outside that allowed folder. I stopped before any outside write. |
| Capture boot / capture size / end tick | Not run |
| Replay direct vs capture live | Not run |
| Queue gate (direct, queue, repeat) | Not run |
| Negative control | Not run |
| Part 2 paraLLEl | Not run (Part 1 not run) |
| Runner SHA-256 ×2 | Not found (no runner built) |
| Runner-dir diff check | Not run |
| Boots / lease | 0 boots; no lease claimed |
| Build / new bytes | 0 builds; no worktree or build bytes created |
| Commands / receipts | Read-only reference commands: `cat ~/dev/AGENTS.md`; `cat AGENTS.md`; `cat local/muse/prompts/GB4.md`; `cat local/AGENTS.local.md`; `cat local/research/GB3/REPORT.md`; `cat local/research/GB2/REPORT.md`; targeted `sed` reads of GB3 §§5–9 and GB2 report sections. No capture/replay commands run. |

The GB4 brief cannot be executed within the worker write boundary given for this session. No recommendation or technical verdict is made.
