# N8D7M12 Part 5M1 — same-binary Mac OFF replay (PREPARED, unexecuted)

**State: PREPARED, unexecuted. Outcome sought: A = exact reviewed-SHA
driver ready for a separate orchestrator SHA release (no runtime result).
No replay, boot, build, device, lease, install or launch action was
executed in this part, and no binary/stream/source/fork edit was made.
Text <512 KiB. Mac ON receipts preserved untouched. No Mac OFF result
and no graphics verdict are produced here. This is a Mac control,
separate from the Odin run-to-run variance work; it does not touch a
device. A diagnostic wall time is never a speed number.**

Brief: `local/muse/prompts/N8D7M12P5M1.md`. Goal: a bounded Mac OFF
replay of the Part 1 Mac ON inputs — same binary and stream, `parallel`
backend, step 50, PPM tick 2050 — dropping exactly the three measurement
flags so a separately gated run can test whether the Mac ON/OFF output is
flag-unperturbed. The ON side is the Part 1 exact-stream replay
(`local/research/N8D7M12/REPORT.md` §§1,3,4); the OFF side with that same
binary `2a0446e8…ae5` and stream `n8d7m6.gs` was never run
(`local/research/N8D7M12P5C/REPORT.md` §1 row 11).

## 1. Pins (re-verified by the checker)

| Item | Path | Size | SHA-256 |
| --- | --- | --- | --- |
| Binary (Part 1) | `~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests` | 8,369,016 B | `2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5` |
| Stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | 1,100,696,462 B | `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| Mac ON hashes | `~/dev/ssx3-work/N8D7M12/mac-parallel/parallel.hashes` | 2,686 B | `94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290` |
| Mac ON PPM | `~/dev/ssx3-work/N8D7M12/mac-parallel/vq-002050.ppm` | 688,143 B | `9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e` |
| Vulkan runtime | `/opt/homebrew/lib/libvulkan.1.dylib` | — | `GRANITE_VULKAN_LIBRARY` env |

Private scratch (outside git): `~/dev/ssx3-work/N8D7M12P5M1/mac-off/`
(`cwd/`, `frames/`, `parallel.hashes`, `run.log`).

Prepared driver `mac_off.py` SHA-256:
`bec9a4c626092b5a2e66a8f1597f90235c1335631aa2f2cba432851de6ecd9f1` (the
reviewed SHA to release for the separate run gate; also recorded as
`mac_off_sha` in `check-result.json`).

## 2. Env matrix — exact ON minus three flags plus output paths

`mac_off.py` holds the exact Mac ON env as `ON_ENV` (Part 1 §4) and
derives OFF. The checker recomputes the semantic diff and requires it to
be exactly this.

| Key | Mac ON | Mac OFF (this driver) |
| --- | --- | --- |
| `PS2X_GS_REPLAY_CAPTURE` | `<stream>` | identical |
| `PS2X_GS_REPLAY_BACKEND` | `parallel` | identical |
| `PS2X_GS_REPLAY_STEP` | `50` | identical |
| `PS2X_GS_REPLAY_PPM_TICKS` | `2050` | identical (tick2050 PPM) |
| `PS2X_N8D7F_SELECTED_CAPTURE` | `1` | **absent (unset, not `0`)** |
| `PS2X_N8D7L_ORACLE` | `1` | **absent** |
| `PS2X_N8D5_TILE_CAPTURE` | `1` | **absent** |
| `PS2X_GS_REPLAY_PPM_DIR` | `…/N8D7M12/mac-parallel` | `…/N8D7M12P5M1/mac-off/frames` |
| `PS2X_GS_REPLAY_OUT` | `…/mac-parallel/parallel.hashes` | `…/mac-off/parallel.hashes` |
| `GRANITE_VULKAN_LIBRARY` | `/opt/homebrew/lib/libvulkan.1.dylib` | identical |

Semantic diff proven by `off_env_diff_exact`: keys removed == exactly the
three flags, keys added == none, keys whose value changed == only
`PS2X_GS_REPLAY_PPM_DIR` and `PS2X_GS_REPLAY_OUT`. Live keys asserted
absent: `PS2X_GS_CAPTURE*`, `PS2X_PAD_SCRIPT*`, `PS2X_CD_IMAGE`.

## 3. Driver contract and guards (`mac_off.py`)

- Refuses reuse of the private output dir `…/N8D7M12P5M1/mac-off` and of
  an existing `result.json`/`driver.log` (one-run guard).
- Double-hashes the binary and stream (two matching reads) and checks
  their sizes plus the Part 1 ON hashes/PPM pins **before** claiming a
  slot or running.
- Claims exactly one mini P-lane slot dynamically via
  `local/tooling/p_lane_lease.py` `claim(LEASE_LABEL)` (`None` => stop,
  busy) and releases that same slot in `finally`; no slot is ever
  hardcoded.
- Runs the binary from its own private cwd (`mac-off/cwd`) with the OFF
  env and explicit stream/backend/step50/PPM2050/output paths and
  `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`.
- Keeps the OS environment (PATH, Vulkan loader, ...) but clears **every**
  inherited `PS2X_*` key before adding the OFF env, so no ambient live or
  replay setting can leak into the run; the child's `PS2X_*` key set must
  equal exactly the OFF env's set (checker `ambient_ps2x_cannot_leak`).
- Active wall capped at 300 s; the child is stopped only by its own PID
  (`proc.terminate()` then `proc.kill()`); no `pkill`/`pgrep`/`killall`.
- Log capped at 16 MiB and outputs at 64 MiB; on failure the lease is
  released and the child terminated in `finally`.
- Requires `--released-sha <mac_off.py SHA-256>`; no run happens otherwise.

## 4. Predeclared run outcomes (separately gated run only)

The later receipt compares all 41 OFF rows and the OFF PPM against the
pinned Mac ON `parallel.hashes`/`vq-002050.ppm` (helper
`classify_off_vs_on`). No comparison is run now.

| Observation (OFF vs Mac ON, same binary/stream) | Reading |
| --- | --- |
| 41/41 rows and PPM byte-equal | `flag-unperturbed` — Mac output is insensitive to the three flags |
| Any difference at ticks ≤2000 | `void-pre2050` — the flags are unread before tick2050, so the Mac ON/OFF causal test is void (harness/nondeterminism) |
| Rows ≤2000 equal, tick2050 row and/or PPM differ | `tick2050-only` — suggests a flag effect on Mac at tick2050 |
| Parse/backend error, wrong row count/sequence, missing PPM, or non-zero exit | FAIL/void; record the first error, no comparison |

All 41 rows and the PPM must be compared after a separately gated run;
none is compared here. No Mac OFF result and no graphics cause exist in
this preparation part.

## 5. Acceptance / stop table

| # | Gate | Required | On failure |
| --- | --- | --- | --- |
| 1 | Binary + stream pins (2×SHA, sizes) and Part 1 ON hashes/PPM pins | §1 exact | stop, no run |
| 2 | OFF env == ON minus exactly the three flags + output paths; live keys absent | §2 | stop, no run |
| 3 | Fresh reviewed `mac_off.py` SHA released (require `--released-sha`) | new gate | stop, no run |
| 4 | One P-lane slot claimed dynamically; released in `finally` | §3 | stop/cleanup |
| 5 | 300 s wall, child stopped by own PID only; 16 MiB log, 64 MiB output caps | §3 | stop with reason |
| 6 | Exit 0 + `GB4_REPLAY_SUMMARY` (parallel, markers=2050) + `GB4_FRAME tick=2050` + exact 41 ordered ticks 50…2050 + `vq-002050.ppm` + no parse/backend error | §4 (PROVISIONAL PASS) | FAIL/void, first error recorded |
| 7 | 41-row + PPM OFF-vs-ON comparison in a separate gate using §4 | §4 | void per §4 |
| 8 | No speed number from the diagnostic wall; no graphics verdict | standing rules | — |

## 6. Exact unexecuted command (separate run gate)

```sh
python3 -u local/research/N8D7M12P5M1/mac_off.py --released-sha <reviewed mac_off.py SHA-256>
python3 local/research/N8D7M12P5M1/check.py --self-check
```

`mac_off.py` refuses without its own reviewed SHA and refuses if
`mac-off/` or a prior `result.json`/`driver.log` exists. No run occurs if
any gate fails. A later part may release **one** replay using the exact
reviewed SHA.

## 7. Validation (static only)

`check.py --self-check`: see `check-result.json` / `check-selfcheck.txt`.
It proves the pins (binary, stream, ON hashes/PPM hashed on disk), the
exact ON-minus-three-plus-output-paths env semantic diff, that an ambient
`PS2X_*` setting cannot leak into the child env (`ambient_ps2x_cannot_leak`
injects an evil `PS2X_GS_REPLAY_CAPTURE`/backend and a stray
selected-capture flag plus `PS2X_LIVE_JUNK` and requires them cleared while
PATH/Vulkan stay intact), `--self-check` runs no replay and no
device/lease action, the one-run/lease/own-PID/wall/log/output guards, the
exact 41 ordered tick sequence (static and functional: exact passes;
duplicate, missing, wrong-exit, parse-error all fail), PPM tick2050, the
parse/backend error gate, and the three predeclared outcomes. `mac_off.py`
compiles (`py_compile`); importing it creates no output, claims no lease
and starts no process.

## 8. Gaps / handback

- No runtime result: Mac OFF rows/PPM and the OFF-vs-ON reading are
  unproved until the separately gated run.
- The Mac OFF run needs a fresh orchestrator SHA release of `mac_off.py`;
  this preparation part releases nothing.
- The Odin run-to-run variance work is separate; this Mac control makes
  no device claim.
- Recommended next action (orchestrator decision): review the `mac_off.py`
  SHA, then release the single Mac OFF replay in a separate gate.

| Condition | Outcome | Next action |
| --- | --- | --- |
| Driver + checker ready, no runtime result | **A (this report)** | Orchestrator SHA-gates one Mac OFF replay |
| Control contract unprovable statically | B | State the smallest gap |
| Preparation failure | OTHER | Diagnose scope first |

Receipts: `REPORT.md`, `mac_off.py`, `check.py`, `check-result.json`,
`check-selfcheck.txt` — commit `[N8D7M12] Part 5M1` with
`Orchestrated-By: opencode`, explicit paths only, no push.
