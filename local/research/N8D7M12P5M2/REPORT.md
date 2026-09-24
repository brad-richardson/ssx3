# N8D7M12 Part 5M2 — one same-binary Mac OFF replay (executed)

**State: EXECUTED, outcome A-for-receipts / acceptance FAIL. One released
Mac OFF replay ran with the reviewed driver SHA and the pinned Part 1
binary/stream. It produced the exact 41 rows and PPM, and both are
byte-identical to the pinned Mac ON artifacts — but the test binary
exited 1 on a cwd-relative CodeGenerator test unrelated to the replay, so
the predeclared `exit0` acceptance gate is not met. No retry. No
source/binary/stream edit, no device action, no push. ON artifacts
preserved byte-for-byte. No graphics root-cause verdict; the 6.1 s
diagnostic wall is control only, never speed.**

Brief: `local/muse/prompts/N8D7M12P5M2.md`. Goal: run the one Mac OFF
replay the Part 5M1 driver was prepared and reviewed for, holding the
Part 1 Mac ON binary `2a0446e8…ae5` and stream `f6a78f71…a593` fixed,
dropping exactly the three tick2050 capture flags, then compare all 41
rows and the tick2050 PPM against the pinned Mac ON.

## 1. Pins (re-verified before the run and by `check.py` after)

| Item | Path | Size | SHA-256 |
| --- | --- | --- | --- |
| Driver (reviewed/released) | `local/research/N8D7M12P5M1/mac_off.py` | — | `bec9a4c626092b5a2e66a8f1597f90235c1335631aa2f2cba432851de6ecd9f1` |
| Binary (Part 1) | `~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests` | 8,369,016 B | `2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5` |
| Stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | 1,100,696,462 B | `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| Mac ON hashes (pinned) | `~/dev/ssx3-work/N8D7M12/mac-parallel/parallel.hashes` | 2,686 B | `94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290` |
| Mac ON PPM (pinned) | `~/dev/ssx3-work/N8D7M12/mac-parallel/vq-002050.ppm` | 688,143 B | `9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e` |
| **OFF hashes (produced)** | `~/dev/ssx3-work/N8D7M12P5M1/mac-off/parallel.hashes` | 2,686 B | `94b433df…10c290` (== ON) |
| **OFF PPM (produced)** | `~/dev/ssx3-work/N8D7M12P5M1/mac-off/frames/vq-002050.ppm` | 688,143 B | `9490484c…14fce3e` (== ON) |

## 2. Preflight (all green before the single run)

| # | Preflight | Result |
| --- | --- | --- |
| 1 | Driver SHA == reviewed `bec9a4c6…` | PASS |
| 2 | `check.py --self-check` | PASS, **A 32/32** |
| 3 | `py_compile` driver + checker | PASS |
| 4 | No prior private OFF result/output | PASS (scratch absent) |
| 5 | Binary/stream/ON hashes/ON PPM pins + sizes | PASS |
| 6 | Disk budget <200 GB, ≥1 GB headroom | PASS, 150.4 GB of 200 GB cap, 99 GB free |
| 7 | One free mini P-lane slot, no heavy host build | PASS, both slots free |

One released command, from repo root:

```sh
python3 -u local/research/N8D7M12P5M1/mac_off.py --released-sha bec9a4c626092b5a2e66a8f1597f90235c1335631aa2f2cba432851de6ecd9f1
```

## 3. Run result — acceptance gate FAIL on exit code

| Gate | Required | Observed | Verdict |
| --- | --- | --- | --- |
| exit 0 | 0 | **1** | **FAIL** |
| parallel summary, markers2050 | yes | `GB4_REPLAY_SUMMARY mode=queue backend=parallel … markers=2050 samples=41` | PASS |
| `GB4_FRAME tick=2050` | yes | `…backend=parallel pmode=ff21 … present=d19b96fe` | PASS |
| exact 41 ordered ticks 50…2050 | yes | 41 rows, exact sequence | PASS |
| PPM present | yes | `vq-002050.ppm`, 688,143 B | PASS |
| bounded outputs | ≤16 MiB log / ≤64 MiB tree | 4.58 MiB log; tree 5.24 MiB | PASS |
| child stopped, lease free | yes | exit_code=1 (self-exit), slot 1 released | PASS |

Driver verdict: `FAIL (provisional)`, `stop_reason = no complete 41-row
tick2050 receipt` (`replay_complete` requires `rc == 0` and no error line).

`elapsed_s = 6.071` is a diagnostic control time, **not** a speed number.

### 3a. First failure (recorded, no retry)

`run.log` tail: `Total Tests: 585 / Passed: 584 / Failed: 1`. The single
failure is a **cwd-relative unit test, not the replay**:

```
[Suite]: CodeGenerator
[Run]: VU0 macro mappings cover all S1/S2 enums   [Failed]
    - instructions.h should be readable from the test working directory
    - VU0_S1 enum list should not be empty
    - VU0_S2 enum list should not be empty
```

`ps2xTest/src/code_generator_tests.cpp:1142-1149` reads `instructions.h`
from candidates `ps2xRecomp/include/ps2recomp/instructions.h`,
`../ps2xRecomp/...`, `../../ps2xRecomp/...` — all **relative to the test
working directory**. The driver runs the full `ps2x_tests` from its
private cwd `~/dev/ssx3-work/N8D7M12P5M1/mac-off/cwd`, so the header is
not found. In Part 1 the suite ran with `workdir=worktree`, where it
resolved (585/585). The driver's error regex `Failed: [1-9]\d*` also
matches the suite total line `Failed: 1`, so `replay_complete` rejects the
run on that line too.

**Consequence:** the reviewed Part 5M1 driver cannot satisfy its own
`exit0` acceptance gate from its private cwd regardless of the three
flags. This is a driver/harness defect, not a replay or backend error: the
`PS2GSReplay` test itself **passed** (its `[Passed]` immediately follows
the tick2050 row block), and there is no `GB4_REPLAY_PARSE_ERROR`.

## 4. OFF vs pinned Mac ON — 41 rows and PPM

All comparison fields are **byte-equal**:

| Field | OFF | pinned Mac ON | Match |
| --- | --- | --- | --- |
| `parallel.hashes` SHA-256 | `94b433df…10c290` | `94b433df…10c290` | identical (2686 B) |
| 41 rows, tick sequence | 50…2050 exact | 50…2050 exact | 41/41 rows byte-equal |
| `vq-002050.ppm` SHA-256 | `9490484c…14fce3e` | `9490484c…14fce3e` | identical (688143 B) |
| tick2050 present | `d19b96fe` | `d19b96fe` | identical |
| parser counts | packets 862958, priv 11499, transfers 25445, markers 2050 | same | identical |

Full row list: `row-comparison.txt` (all 41 marked `==`). Predeclared
classifier reading of the produced artifacts: **`flag-unperturbed`** (41/41
rows equal AND PPM byte-equal).

**Bounded reading (do not over-lift):** the replay artifacts are
flag-unperturbed, but the release acceptance gate is FAIL (exit 1), so this
is an artifact-level observation, not an accepted control result. The exact
renderer source bytes at the old Mac binary build remain unpinned, so
nothing is attributed to current dirty source. ON artifacts are untouched
(`pins_unchanged` PASS). No graphics root cause is established.

## 5. Absolute OFF PPM for orchestrator viewing

```
/Users/brad/dev/ssx3-work/N8D7M12P5M1/mac-off/frames/vq-002050.ppm
SHA-256 9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e  (688,143 B)
```

## 6. Cleanup

| Item | State |
| --- | --- |
| Lease | slot 1 claimed dynamically, released in `finally`; both slot files absent |
| Child | self-exited (exit_code=1); PID 85548 gone (`os.kill(pid,0)` → `ProcessLookupError`) |
| Stop | own PID only; no `pkill`/`pgrep`/`killall` |
| Outputs | log 4.58 MiB (≤16 MiB), tree 5.24 MiB (≤64 MiB) |
| Retry | none — exactly one released command was issued |

## 7. Handback table

| Condition | Outcome | Next action |
| --- | --- | --- |
| One released replay ran; artifacts byte-equal to ON but suite exit 1 | **acceptance FAIL, artifacts `flag-unperturbed`** | If a clean `exit0` control is required, re-review a driver revision that runs the suite from the worktree (or excludes the cwd-relative CodeGenerator test); the reviewed `bec9a4c6…` SHA cannot pass as written |
| Driver defect does not affect the replay path | observed | The 41 rows + PPM tick2050 comparison is still available as bounded evidence |

## 8. Receipts (committed, explicit paths only)

| File | Content |
| --- | --- |
| `local/research/N8D7M12P5M2/REPORT.md` | this report |
| `local/research/N8D7M12P5M2/check.py` | narrow read-only receipt checker |
| `local/research/N8D7M12P5M2/check-result.json` | checker output, `A 15/15`, `acceptance=FAIL`, `artifact_reading=flag-unperturbed` |
| `local/research/N8D7M12P5M2/driver.log` | driver stdout (13 lines) |
| `local/research/N8D7M12P5M2/off-result.json` | driver `result.json` (pins, env diff, 41 rows, first_failure) |
| `local/research/N8D7M12P5M2/off-parallel.hashes` | produced OFF 41-row hash file |
| `local/research/N8D7M12P5M2/row-comparison.txt` | 41 OFF rows vs ON, all `==` |
| `local/research/N8D7M12P5M2/markers.txt` | GB4 summary/frame/stats rows |
| `local/research/N8D7M12P5M2/first-failure.txt` | bounded failing-test excerpt + totals |

Commit `[N8D7M12] Part 5M2` with `Orchestrated-By: opencode`, explicit
paths only, no push. Private scratch (not committed, outside git):
`~/dev/ssx3-work/N8D7M12P5M1/{driver.log,result.json,mac-off/}`.
