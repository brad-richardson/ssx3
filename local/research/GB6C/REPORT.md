# GB6C — opt-in paraLLEl fold gate after capture-driver repair

Orchestrator: Codex. This is a focused continuation after [GB6](../GB6/REPORT.md)
and [GB6B](../GB6B/REPORT.md). GB6's source and matched replay passed;
both prior live-capture attempts lacked a second race frame because of
capture-driver errors. No fork source, generated code, or build changed
for this run.

| Gate | Evidence |
| --- | --- |
| Pin | Local `gb6-fold` at `293fd81ade60afb56b47434297c6f2241843dfff`; fork `ssx3` was `1aaed05256bf53881824a9edd96a7cd5b7e8bbcc` before the push. Canonical E54D codegen register SHA remained `8ea8ed43…e662d688a3`. |
| One named script repair | Copied GB6B's bounded driver into `~/dev/ssx3-work/GB6C/run/`, retargeted its output/lease label, and changed only its frame-cap expression from `p.stat()` to `Path(p).stat()` for string paths. `driver.diff` SHA-256 `63d84be0ad6022abc7143e8869c72a96062fb3dd31c23aecdf762069bd227fdc`; `gb6c_boot.py` SHA-256 `74e2671615f0aa91da6c564798d229c00e548ae27bf0191c80a54c0f39ec5225`. `py_compile` and static checks passed before boot: exactly three capture ticks `1810,2050,2150`, no PKLOG/diagnostic park, 32 MiB combined log and 25 MiB frame caps. |
| Input SHA pairs | Two independent `shasum -a 256` reads matched byte for byte (`input-sha-read1/2.txt`): stock ISO `3c2f8eb1…ae3f5`, ELF `1b49d05c…67af7bc`, GB6 runner `047f29e7…3f5aac1`, canonical register file `8ea8ed43…e662d688a3`. Full hashes are in the receipt files and GB6B report. |
| One leased live run | Mini slot 1, own runner PID 21518, I26-FAST route, `PS2X_GS_BACKEND=parallel`, `PS2X_SKIP_MOVIE=1` dev-only, missing-function stop, wall cap 500 s. Wrapper reached its `target` condition at guest tick 2218 in 70.65 s and then terminated its own runner (`rc=-15` is the wrapper's SIGTERM, not a guest crash). PID gone; both mini slots free. `result.json` SHA-256 `5115af12a74075408baf324de6049009903e7f7172bd075469be42dc3cafb42c`. |
| Bounded output | Boot log 5,999,848 bytes, no PKLOG, saved race frames 329,580 bytes combined. GB6C tree 6.7 MiB; global internal usage 111.1/200 GB after run. No diagnostic timing is reported as speed. |
| Fork safety and push | Orchestrator viewed both frames; `git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner` was empty and `1aaed05` was an ancestor of `293fd81`. Fast-forward `git push fork gb6-fold:ssx3` succeeded; `git ls-remote fork refs/heads/ssx3` afterward returned `293fd81ade60afb56b47434297c6f2241843dfff`. No generated guest source/game data/binary was pushed. |

## Viewed race frames

| Tick | SHA-256 | Observation |
| ---: | --- | --- |
| 1810 | `df23d8872d052460295c3b9ee6c91d228082dc4df6f56ec7c6ff29df678cc1e6` | Race HUD `00:00:01`, 0% progress; rider/track and snow visible with the known large dark GS composite region. |
| 2050 | `2c059efa144a362746df24fe7fdcda4bec9a0d3f328059867fae949023d45097` | Race HUD `00:00:05`, 1% progress; scene and course-map arrow changed, rider/terrain still visible. Dark composite and small-text damage remain. |

The distinct frame hashes and advancing HUD show functional live race
progress on this folded source. They do not establish visual parity with
the CPU backend, clean guest speed, or a fix for the glyph/dark-region
defects. The GB5D matched replay still shows damaged title copyright
text by tick 300 and button labels by tick 700. The backend remains
opt-in (`PS2X_GS_SHADOW_PARALLEL=OFF` by default at build time and
`PS2X_GS_BACKEND=parallel` required at runtime).

## Exact commands and limits

From `~/dev/ssx3-work/GB6C/run`: `python3 -m py_compile gb6c_boot.py`,
then `python3 gb6c_boot.py --label parallel-one --wall 500 --target 2200
--capture > boot-driver.log 2>&1`. The script claimed/released mini slot
1 and capped wall, progress, logs and frame bytes. Before the run, two
separate `shasum -a 256` invocations read the ISO, ELF, runner and
register file; `cmp input-sha-read1.txt input-sha-read2.txt` returned
0. Afterward, the orchestrator checked `result.json` without printing
its large process list, verified frame SHAs, viewed both PNGs, checked
the lease/PID, disk budget, fork worktree status and runner-dir diff,
then performed the fork fast-forward and verified its remote tip.
