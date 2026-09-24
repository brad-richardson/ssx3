# GB4 report — stopped during source inspection

| Item | Result |
|---|---|
| References read | `local/AGENTS.local.md`; all of GB3 report (including §§0, 5, 6, 8); GB2 Part 1 report including the 256-packet captured-stream test template |
| Source fork | `~/dev/PS2Recomp` at `eac6cba` (`ssx3`), clean before GB4 setup |
| GB4 worktree / branch / starting commit | `~/dev/ssx3-work/GB4/PS2Recomp`, branch `gb4-replay`, based at `574354a` (`[GB3] Part 1b: sceGsResetGraph stub applies SetGsCrt's SMODE effect`) |
| Build / generated-code inputs | No build run. Canonical codegen dir exists at `~/dev/ssx3-work/codegen-ssx3`; existing GB3 build is at `~/dev/ssx3-work/GB3/build`. |
| Capture boot / capture size / end tick | Not run |
| Replay direct vs capture live | Not run |
| Queue gate (direct, queue, repeat) | Not run |
| Negative control | Not run |
| Part 2 paraLLEl | Not run (Part 1 not run) |
| Runner SHA-256 ×2 | Not found (no runner built) |
| Runner-dir diff check | Not run |
| Boots / lease | 0 boots; no lease claimed |
| Storage | Initial `disk_budget.sh`: 80.2/200 GB; 162 GiB free. GB4 cap: 12 GB. |
| Commands / receipts | Read `git -C ~/dev/PS2Recomp` status/worktree list and confirmed `574354a`; created the GB4 worktree with `git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/GB4/PS2Recomp -b gb4-replay 574354a`. |

## Stop condition

Stopped on the first source-inspection command error as required by `~/dev/AGENTS.md`. The command ran from `/Users/brad/dev/ssx3` with fork-relative paths, so `rg` reported `ps2xRuntime/src/lib/gs: No such file or directory` (and analogous errors for `ps2_memory.cpp`, `EeScheduler.cpp`, and `ps2Test/src`). No source files were edited and no build, boot, or lease was started. The path error is recorded without retrying.
