# N8D7M12 Part 5M3 — corrected Mac OFF driver with cwd fixture (PREPARED, unexecuted)

**State: PREPARED, unexecuted. Outcome sought: A = exact reviewed-SHA
driver ready for a separate orchestrator SHA release (no runtime result).
No replay, boot, build, device, lease, install or launch action was
executed in this part; no binary/stream/source/fork edit was made. Text
<512 KiB. The Part 1 Mac ON and Part 5M2 receipts are preserved untouched.
No Mac OFF result and no graphics verdict are produced here. A diagnostic
wall time would never be a speed number.**

Brief: `local/muse/prompts/N8D7M12P5M3.md`. Goal: the Part 5M1 driver had
exactly one defect. Part 5M2 ran it once and produced OFF
`parallel.hashes`/PPM byte-identical to Mac ON, but the overall binary
exited 1 because one unrelated CodeGenerator suite test could not find
`ps2xRecomp/include/ps2recomp/instructions.h` relative to the driver's
private cwd (`ps2xTest/src/code_generator_tests.cpp:1141-1150`, suite
584/585). This part prepares a corrected driver for a separate release:
same pins, same OFF env, same guards, plus a pre-run private cwd fixture
symlink `cwd/ps2xRecomp` → the pinned Part 1 fork's `ps2xRecomp` tree so
the first candidate resolves. The fixture is a test-suite fixture only.

## 1. Pins (re-verified by the checker)

| Item | Path | Size | SHA-256 |
| --- | --- | --- | --- |
| Driver (prepared, unreleased) | `local/research/N8D7M12P5M3/mac_off.py` | — | `1056304d3f2d559936f56ae189c419813581bb46f7cf35ae26d0dc7ad12d6738` |
| Binary (Part 1) | `~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests` | 8,369,016 B | `2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5` |
| Stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | 1,100,696,462 B | `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| Mac ON hashes | `~/dev/ssx3-work/N8D7M12/mac-parallel/parallel.hashes` | 2,686 B | `94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290` |
| Mac ON PPM | `~/dev/ssx3-work/N8D7M12/mac-parallel/vq-002050.ppm` | 688,143 B | `9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e` |
| Fork (Part 1) | `~/dev/ssx3-work/N8D7M12/PS2Recomp` | branch `n8d7m12-replay-core` | HEAD `24801bcfa42611e5e36c8990183b793d28b4e5e8` |
| Fork header | `…/PS2Recomp/ps2xRecomp/include/ps2recomp/instructions.h` | 31,244 B | `b8de8745e16d6a814763f69b0e8d1d54d957bf427f94ec2bc57f63e509f970cd` |
| Vulkan runtime | `/opt/homebrew/lib/libvulkan.1.dylib` | — | `GRANITE_VULKAN_LIBRARY` env |

Private scratch (outside git): `~/dev/ssx3-work/N8D7M12P5M3/mac-off/`
(`cwd/`, `frames/`, `parallel.hashes`, `run.log`).

## 2. Env matrix — exact ON minus three flags plus output paths (unchanged from Part 5M1)

`mac_off.py` holds the exact Mac ON env as `ON_ENV` (Part 1 §4) and
derives OFF. The checker recomputes the semantic diff and additionally
compares `ON_ENV` and the OFF env against the Part 5M1 module, requiring
every replay key except the two private output paths to be byte-identical.

| Key | Mac ON | Mac OFF (this driver) |
| --- | --- | --- |
| `PS2X_GS_REPLAY_CAPTURE` | `<stream>` | identical |
| `PS2X_GS_REPLAY_BACKEND` | `parallel` | identical |
| `PS2X_GS_REPLAY_STEP` | `50` | identical |
| `PS2X_GS_REPLAY_PPM_TICKS` | `2050` | identical (tick2050 PPM) |
| `PS2X_N8D7F_SELECTED_CAPTURE` | `1` | **absent (unset, not `0`)** |
| `PS2X_N8D7L_ORACLE` | `1` | **absent** |
| `PS2X_N8D5_TILE_CAPTURE` | `1` | **absent** |
| `PS2X_GS_REPLAY_PPM_DIR` | `…/N8D7M12/mac-parallel` | `…/N8D7M12P5M3/mac-off/frames` |
| `PS2X_GS_REPLAY_OUT` | `…/mac-parallel/parallel.hashes` | `…/mac-off/parallel.hashes` |
| `GRANITE_VULKAN_LIBRARY` | `/opt/homebrew/lib/libvulkan.1.dylib` | identical |

Semantic diff proven by `off_env_diff_exact`: keys removed == exactly the
three flags, keys added == none, keys whose value changed == only
`PS2X_GS_REPLAY_PPM_DIR` and `PS2X_GS_REPLAY_OUT`. Live keys asserted
absent: `PS2X_GS_CAPTURE*`, `PS2X_PAD_SCRIPT*`, `PS2X_CD_IMAGE`. **No
`PS2X_*` replay env value changes** versus Part 5M1.

## 3. Correction — pre-run private cwd fixture (test-suite only)

Part 5M2's single predeclared failure was the cwd-relative CodeGenerator
suite test. The corrected driver adds, before the lease claim and the run:

1. `check_fork_pins()` — verifies the pinned fork HEAD **twice**
   (`read_worktree_head`, a read-only `.git`/HEAD/ref read, no git
   process) equals `24801bc…5e8`, and the `ps2xRecomp` header **twice**
   hashes to `b8de8745…970cd` at 31,244 B.
2. `make_cwd_fixture()` — refuses if `cwd/ps2xRecomp` already exists,
   creates the symlink `cwd/ps2xRecomp → <pinned fork>/ps2xRecomp`, then
   requires `os.path.realpath` of the link to equal the pinned tree
   exactly (and stay under the pinned fork), requires the first
   cwd-relative candidate (`ps2xRecomp/include/ps2recomp/instructions.h`)
   to be readable, and requires the linked header to resolve to the pinned
   header and hash to `b8de8745…970cd` **twice**.

The symlink is a **test-suite fixture only**: it lives in the private
`mac-off/cwd` run directory, is never on the replay path, and changes no
`PS2X_*` replay env. `output_bytes_under` does not follow the symlink
(`pathlib.rglob` does not recurse into symlinked directories on this
Python), so the 64 MiB output cap still counts only produced artifacts.

## 4. Driver contract and guards (`mac_off.py`)

- Refuses reuse of the private output dir `…/N8D7M12P5M3/mac-off` and of
  an existing `result.json`/`driver.log` (one-run guard); refuses a
  pre-existing `cwd/ps2xRecomp` fixture.
- Double-hashes the binary and stream (two matching reads) and checks
  their sizes plus the Part 1 ON hashes/PPM pins **before** claiming a
  slot or running; the fork HEAD and header are double-checked before the
  fixture is created.
- Claims exactly one mini P-lane slot dynamically via
  `local/tooling/p_lane_lease.py` `claim(LEASE_LABEL)` (`None` => stop,
  busy) and releases that same slot in `finally`; no slot is hardcoded.
- Runs the binary from its own private cwd (`mac-off/cwd`) with the OFF
  env and explicit stream/backend/step50/PPM2050/output paths and
  `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`.
- Keeps the OS environment (PATH, Vulkan loader, ...) but clears **every**
  inherited `PS2X_*` key before adding the OFF env; the child's `PS2X_*`
  key set must equal exactly the OFF env's set
  (`ambient_ps2x_cannot_leak`).
- Active wall capped at 300 s; the child is stopped only by its own PID
  (`proc.terminate()` then `proc.kill()`); no `pkill`/`pgrep`/`killall`.
- Log capped at 16 MiB and outputs at 64 MiB; on failure the lease is
  released and the child terminated in `finally`.
- Requires `--released-sha <mac_off.py SHA-256>`; no run happens otherwise.

## 5. Predeclared run outcomes (separately gated run only)

The later receipt must report, in order: **binary exit 0 and suite
585/585/0**, `GB4_REPLAY_SUMMARY` (parallel, markers=2050), `GB4_FRAME
tick=2050`, the exact 41 ordered ticks 50…2050, `vq-002050.ppm`, and lease
cleanup. If the suite still fails, the receipt is **FAIL even if the
`parallel.hashes` and PPM match Mac ON**. Then it compares all 41 OFF rows
and the OFF PPM against the pinned Mac ON `parallel.hashes`/`vq-002050.ppm`
(helper `classify_off_vs_on`). No comparison is run now.

| Observation (OFF vs Mac ON, same binary/stream) | Reading |
| --- | --- |
| 41/41 rows and PPM byte-equal | `flag-unperturbed` — Mac output is insensitive to the three flags |
| Any difference at ticks ≤2000 | `void-pre2050` — the flags are unread before tick2050, so the Mac ON/OFF causal test is void (harness/nondeterminism) |
| Rows ≤2000 equal, tick2050 row and/or PPM differ | `tick2050-only` — suggests a flag effect on Mac at tick2050 |
| Non-zero exit, suite ≠ 585/585, parse/backend error, wrong row count/sequence, missing PPM | FAIL/void; record the first error, no comparison |
| All equal but suite still fails | FAIL — artifacts are an observation, not an accepted control |

## 6. Acceptance / stop table

| # | Gate | Required | On failure |
| --- | --- | --- | --- |
| 1 | Binary + stream pins (2×SHA, sizes) and Part 1 ON hashes/PPM pins | §1 exact | stop, no run |
| 2 | Fork HEAD (2×) + header SHA (2×) match; cwd fixture resolves to pinned tree only | §3 | stop, no run |
| 3 | OFF env == ON minus exactly the three flags + output paths; unchanged vs 5M1; live keys absent | §2 | stop, no run |
| 4 | Fresh reviewed `mac_off.py` SHA released (require `--released-sha`) | new gate | stop, no run |
| 5 | One P-lane slot claimed dynamically; released in `finally` | §4 | stop/cleanup |
| 6 | 300 s wall, child stopped by own PID only; 16 MiB log, 64 MiB output caps | §4 | stop with reason |
| 7 | Exit 0 + suite 585/585/0 + `GB4_REPLAY_SUMMARY` (parallel, markers=2050) + `GB4_FRAME tick=2050` + exact 41 ordered ticks 50…2050 + `vq-002050.ppm` + no parse/backend error | §5 (PROVISIONAL PASS) | FAIL/void, first error recorded |
| 8 | 41-row + PPM OFF-vs-ON comparison in a separate gate using §5 | §5 | void per §5 |
| 9 | No speed number from the diagnostic wall; no graphics verdict | standing rules | — |

## 7. Exact unexecuted command (separate run gate)

```sh
python3 -u local/research/N8D7M12P5M3/mac_off.py --released-sha 1056304d3f2d559936f56ae189c419813581bb46f7cf35ae26d0dc7ad12d6738
python3 local/research/N8D7M12P5M3/check.py --self-check
```

`mac_off.py` refuses without its own reviewed SHA and refuses if
`mac-off/` or a prior `result.json`/`driver.log` exists. No run occurs if
any gate fails. A later part may release **one** replay using the exact
reviewed SHA.

## 8. Validation (static only)

`check.py --self-check`: see `check-result.json` / `check-selfcheck.txt`.
It proves the pins (binary, stream, ON hashes/PPM hashed on disk), grounds
the fixture (`read_worktree_head(FORK)` twice equals the pinned HEAD;
header hashed twice equals the pinned SHA at the pinned size), proves the
change set is limited to path/labels/fixture handling (5M3 body equals the
5M1 body once the `# P5M3-FIXTURE-BEGIN/END` regions are stripped and the
private root/lease labels normalized), proves no `PS2X_*` replay env value
changed versus 5M1, functionally exercises the cwd-relative candidate
resolution (`read_first_candidate`) in a temporary directory (no fixture ⇒
no resolution; candidate 1, candidate 2 fallback, and empty-file
fall-through all checked) with no binary, no lease and no device, plus the
one-run/lease/own-PID/wall/log/output guards, the exact 41 ordered tick
sequence, PPM tick2050, the parse/backend error gate and the predeclared
outcomes. Importing `mac_off.py` creates no output and claims no lease.

## 9. Gaps / handback

- No runtime result: the corrected suite `exit0`/585/585 and OFF-vs-ON
  comparison are unproved until the separately gated run.
- The run needs a fresh orchestrator SHA release of `mac_off.py`; this
  preparation part releases nothing.
- **No Mac OFF result exists** and **no graphics** root cause or speed is
  established here.
- Recommended next action (orchestrator decision): review the `mac_off.py`
  SHA, then release the single corrected Mac OFF replay in a separate gate.

| Condition | Outcome | Next action |
| --- | --- | --- |
| Driver + checker ready, no runtime result | **A (this report)** | Orchestrator SHA-gates one Mac OFF replay |
| Fixture path/provenance cannot be grounded | B | State the smallest gap |
| Preparation failure | OTHER | Diagnose scope first |

Receipts (committed, explicit paths only): `REPORT.md`, `mac_off.py`,
`check.py`, `check-result.json`, `check-selfcheck.txt`,
`no-run-receipt.txt` — commit `[N8D7M12] Part 5M3` with
`Orchestrated-By: opencode`, no push.
