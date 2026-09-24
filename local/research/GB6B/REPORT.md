# GB6B — bounded live capture repair

**Gate failed on the one authorized boot. Stopped without retry or source edit.** The copied driver raised an `AttributeError` in its new frame-cap check after saving the first race frame. The second frame and tick 2200 were not reached. Exact traceback: `~/dev/ssx3-work/GB6B/run/boot-driver.log`.

## Pins and pre-use SHA pairs

| Item | Pin / SHA-256 | Evidence |
| --- | --- | --- |
| GB6 local fork worktree | Clean `gb6-fold` at `293fd81ade60afb56b47434297c6f2241843dfff` | `git status --short`, `git branch --show-current`, `git rev-parse HEAD` |
| Remote fork `ssx3` | `1aaed05256bf53881824a9edd96a7cd5b7e8bbcc`; local `fork/ssx3` matched | `git ls-remote fork refs/heads/ssx3`, `git rev-parse fork/ssx3` |
| Stock ISO | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` | Two matching pre-use reads |
| Stock ELF | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` | Two matching pre-use reads |
| GB6 Release runner | `047f29e744de32187a3cbf184ca520068829bbc2dd28951d9064d0b803f5aac1` | Two matching pre-use reads; no rebuild |
| Canonical E54D register file | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` | Two matching pre-use reads; no regeneration |

The complete receipts are `~/dev/ssx3-work/GB6B/run/input-sha-read1.txt` and `input-sha-read2.txt`; `cmp` returned 0. GB6's CMake cache has `PS2X_ENABLE_DIAG_TAPS=OFF`, `PS2X_ENABLE_RUNTIME_LOGS=OFF`, `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`, `PS2X_GS_SHADOW_PARALLEL=ON`, and canonical E54D codegen.

## Driver diff and one-boot result

| Gate | Evidence |
| --- | --- |
| Preflight | Copied `GB6/run/gb6_boot.py` to `GB6B/run/gb6b_boot.py`; complete changes in `GB6B/run/driver.diff`. Python AST/static assertions passed before boot. Exactly three targets `1810,2050,2150`; race windows 1810–2049 and 2050–2269; guest target 2200; wall cap 500 s; progress cap 120 s; combined log cap 32 MiB; frame cap 25 MiB. Removed `PS2X_PKLOG`, `PS2X_DIAG_PARK` and its directory. Kept parallel backend, dev-only movie bypass, I26-FAST route, missing-function stop, vsync progress and frame dumps. |
| Lease and PID | One boot started in mini slot 1 with runner PID 21179. The wrapper's `finally` block released the slot and killed its own PID after the exception. Escalated `ps -p 21179 -o pid=,stat=,comm=` showed no process; both mini lease files were absent. No retry. |
| Failure and rc | Driver exited 1 with `AttributeError: 'str' object has no attribute 'stat'` at `gb6b_boot.py:108–109`: `result['frames']` stores string paths, but the new cap sum calls `p.stat()`. No `result.json` was written, so runner rc and exact elapsed time are **not available**. |
| Guest progress | Last `[vsync-rate]` line: tick 1786; `[frame:dump]` and saved frame: tick 1810. Tick 2200 was **not established**. |
| Byte bounds | `boot.log` 4,576,508 bytes and no PKLOG file, below 32 MiB. Frame directory 297,912 bytes (two PNGs and two sidecars); saved race PNG 148,836 bytes; combined frame files 446,748 bytes, below 25 MiB. The cap check itself caused the stop. |
| Disk | `local/tooling/disk_budget.sh` before and after: 111.1/200 GB internal usage, 131 GiB free. |

| Frame | Tick | SHA-256 | Viewed result |
| --- | ---: | --- | --- |
| `~/dev/ssx3-work/GB6B/run/parallel-one/race_early-tick1810.png` | 1810 | `404d9fd608eb47e28d9c3d8ffb571a56f7950b18c5c639efb9e89bbc0968f246` | HUD `00:00:01`; rider/track and snow visible; large dark terrain region persists. |
| Second race frame | **not found** | **not found** | HUD advance and distinct image SHA could not be checked. |

I viewed GB6's prior title, menu and race PNGs without editing them. The menu has broken/blocky glyph strokes and the race frame has dark GS composite regions. This run makes no new parity or speed claim; the one PNG is functional evidence only.

## Exact commands, gaps, recommendation

Preflight from `~/dev/ssx3`: `local/tooling/disk_budget.sh`; `git -C ~/dev/ssx3-work/GB6/PS2Recomp ls-remote fork refs/heads/ssx3`; local branch/status/revision checks; `rg` of GB6's CMake cache; Python AST/static assertions on the copied driver. Two separate identical `shasum -a 256` commands read the ISO, ELF, runner and register file, redirected to `input-sha-read1.txt` and `input-sha-read2.txt`, then `cmp` checked them. The complete copied-driver diff is `driver.diff`.

The sole escalated boot command from `~/dev/ssx3-work/GB6B/run` was `python3 gb6b_boot.py --label parallel-one --wall 500 --target 2200 --capture > boot-driver.log 2>&1`. After failure, read-only inspection used `cat boot-driver.log`, `rg -n '\[vsync-rate\]|\[frame:dump\]' parallel-one/boot.log`, `wc -c` and `shasum -a 256` on the saved PNG, escalated `ps -p 21179 -o pid=,stat=,comm=`, and the second disk-budget check.

**Gaps:** no second race frame, no advancing HUD comparison, no established tick 2200, and no clean runner rc. Per the first-failure stop rule, no driver repair or second boot was attempted.

**Recommendation on fold readiness:** hold the fold gate until a separately authorized run repairs the wrapper's string-path cap check and establishes two race frames with HUD progression. GB6's source, suite and replay evidence remains in `local/research/GB6/REPORT.md`; this run adds no renderer verdict.
