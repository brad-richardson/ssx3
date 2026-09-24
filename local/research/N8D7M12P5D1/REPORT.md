# N8D7M12 Part 5D1 — same-APK Odin OFF launcher (prepared, unexecuted)

**State: PREPARED, no device action. Outcome sought: A = script ready for
an independent orchestrator SHA gate (no runtime result). No adb/device
command, install, launch, lease, build, edit outside this dir, or push
was executed in this part. Text <512 KiB. ON receipts preserved
untouched. No ON or OFF graphics verdict. Outcome verdict stays
PROVISIONAL until the orchestrator SHA-gates and views the OFF run.**

Brief: `local/muse/prompts/N8D7M12P5D1.md`. Goal: a reviewed-SHA-held OFF
launcher for one later Odin diagnostic replay of the **same** APK and
stream as the ON run, testing whether the tick-2050
selected/oracle/tile measurement flags caused the sparse ON frame. Part
5C design is accepted; it released no run.

## 1. Pins (static, same as ON)

| Item | Value |
| --- | --- |
| APK (local `~/dev/ssx3-work/N8D7M12P3/app-release.apk`) | 153,753,116 B, `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512` |
| arm64 runner | `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d` |
| Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` (unchanged) |
| HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` (unchanged) |
| Stream (local `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, device `<FILES>/n8d7m6.gs`) | 1,100,696,462 B, `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| Odin serial | `622c49b1` read at runtime from `local/odin-serial` |
| Source base | fork `n8d7m12-app` @ `a608ed1` (Part 2 gate A) |
| Scratch (outside git, OFF-private) | `~/dev/ssx3-work/N8D7M12P5D1/` |
| ON launcher SHA (P5A, not reused) | `287140bf370acfb105f1b64347a635822300699150e517e6b912340ae031334e` |
| OFF launcher SHA | `223fd15ec0aa45079f44bed7ceffd3e19381d12ac0c51587a0284afb9cd03170` |
| Checker result | `check.py --self-check`: **30/30 PASS, verdict A** (`check-result.json`, `check-selfcheck.txt`) |

**Correction (narrow gate, no device/run/build):** the first committed
SHA (`be8e9956…cacd`) checked only `replay_rows == 41`. `replay_complete`
now requires the exact ordered tick list `50,100,…,2050`
(`EXPECTED_TICKS`, no duplicates, none missing); the count stays for
progress tracking only. The checker runs the real parser/gate on
synthetic logs: exact sequence passes, 41 rows with tick 100 duplicated
and tick 2050 missing fails, 40 rows fails. This supersedes `be8e9956…`
for any release; that SHA must not be released.

ON receipts preserved: `local/research/N8D7M12P5A/` (`REPORT.md`,
`ORCH-GATE.md`, `launch.py`, `check.py`, `check-result.json`,
`check-selfcheck.txt`) and P5B/P5C dirs untouched by this part.

## 2. OFF env diff vs ON (exact)

| Key | ON (P5A `launch.py:70-80`) | OFF (this dir `launch.py`) |
| --- | --- | --- |
| `PS2X_GS_REPLAY_ONDEVICE` | `1` | `1` (kept) |
| `PS2X_GS_REPLAY_CAPTURE` | `<FILES>/n8d7m6.gs` | identical |
| `PS2X_GS_REPLAY_BACKEND` | `parallel` | identical |
| `PS2X_GS_TURNIP` | `1` | identical |
| `PS2X_N8D7F_SELECTED_CAPTURE` | `1` | **absent (line removed)** |
| `PS2X_N8D7L_ORACLE` | `1` | **absent (line removed)** |
| `PS2X_N8D5_TILE_CAPTURE` | `1` | **absent (line removed)** |
| `PS2X_GS_REPLAY_STEP` | `50` | identical |
| `PS2X_GS_REPLAY_PPM_TICKS` | `2050` | identical |
| `PS2X_GS_REPLAY_PPM_DIR` | ON unique dir | OFF unique dir `n8d7m12p5d1-frames-<stamp>` |
| `PS2X_GS_REPLAY_OUT` | ON unique path | OFF unique path `n8d7m12p5d1-<stamp>.hashes` |

Only other text differences: scratch dir `N8D7M12P5A` → `N8D7M12P5D1`,
lease tag `N8D7M12P5A replay` → `N8D7M12P5D1 replay`, lease-free string,
result `brief`, one-run guard label, remote basenames, header/complete
wording marked OFF, and the receipt/census acceptance (§3). No pin,
backend, stride, tick, cap, install/launch-count, SHA-read, preflight,
BACK, force-stop, PID, env-restore, or `finally`-order change.

Live keys asserted absent in both: `PS2X_GS_CAPTURE*`,
`PS2X_PAD_SCRIPT*`, `PS2X_CD_IMAGE` (`FORBIDDEN_ENV_KEYS` kept).

## 3. OFF receipt/census acceptance

OFF still requires: `GB4_REPLAY_SUMMARY markers=2050` (parallel),
the exact ordered `GB4_REPLAY` tick list 50,100,…,2050 through tick2050
(`EXPECTED_TICKS = tuple(range(50, 2051, 50))`, 41 rows, no duplicates,
none missing), `GB4_FRAME tick2050`
tick=2050, `[n8d7m12] replay ok markers=2050`, no `GB4_REPLAY_PARSE_ERROR` /
`replay failed|rejected` / parallel FATAL / Turnip fail, pull of
`vq-002050.ppm` + hashes with 2+2 SHA match, and intact cleanup
(force-stop, PID absent, env 2+2 restore, lease release; any cleanup
failure flips even a complete receipt to FAIL).

OFF does **not** require: `[n8d5b]` control/sampled/raw, `[n8d6a]`
stages, `[n8d7f]` selected metadata/vectors, `[n8d7l]` oracle
metadata/controls/equality, `control=128/128`, or 448/896-tile vector
parsing. The ported N8D7M6 `tile_vector`/`parse_controls`/`probe`
parsers are retained verbatim for logging only; `census_gate` is an OFF
stub that always passes so missing markers cannot fail OFF, and the
error gate uses replay-marker errors only (`markers["errors"]`), never
census absence. `replay_complete` requires `replay_rows == 41` **and**
`replay_ticks == list(EXPECTED_TICKS)`; the `replay_rows` count is
retained for progress tracking only.

## 4. Exact unexecuted command (separate run gate)

```sh
python3 -u local/research/N8D7M12P5D1/launch.py --released-sha <reviewed OFF launch.py SHA-256>
python3 local/research/N8D7M12P5D1/check.py --self-check
```

`launch.py` refuses without `--released-sha <its own SHA>` and refuses if
`result.json`/`driver.log` already exist (one-run guard). No launch
occurs if any gate fails. A later part may release **one**
install/launch only using the exact reviewed SHA; no device call now.

## 5. Acceptance / stop table

| # | Gate | Required | On failure |
| --- | --- | --- | --- |
| 1 | Local APK 2×SHA + size; 3 member 2×SHA; replay strings | exact pins §1 | stop, no device action |
| 2 | Local stream 2×SHA + size | exact pin §1 | stop |
| 3 | Serial `local/odin-serial` == `622c49b1`; all adb `-s` | match | stop |
| 4 | OFF env is ON minus exactly the three flags; live keys absent; unique OFF outputs | §2 | stop, no run |
| 5 | OFF launcher is a fresh reviewed SHA (P5A SHA not reused) | new gate | stop, no run |
| 6 | OFF yields SUMMARY (markers=2050, parallel) + exact tick list 50,…,2050 + `GB4_FRAME tick=2050` + `replay ok markers=2050` + PPM + hashes | §3 | FAIL/void, first error recorded |
| 7 | Missing selected/oracle/tile markers never fail OFF | §3 stub + checker | preparation FAIL if checker fails |
| 8 | Lease claim persists; one `install -r` + one `am start`; BACK once ~6 s | P5A rules kept | stop/cleanup |
| 9 | 600 s wall, 180 s progress, 16 MiB log, 64 MiB output caps | kept | stop w/ reason |
| 10 | Force-stop, PID absent, PPM+hashes 2+2 pull, env 2+2 restore, lease release in `finally`; any cleanup failure → FAIL | kept | record first failure |
| 11 | Keyguard `showing=false` pre-install and pre-start | BLOCKER, never worked around | report, no run |
| 12 | No ON/OFF graphics verdict in this preparation part | — | — |

## 6. Validation (static only)

`check.py --self-check`: **30/30 PASS, verdict A** (`check-result.json`).
Launch SHA `223fd15ec0aa45079f44bed7ceffd3e19381d12ac0c51587a0284afb9cd03170`.
Covers pins,
serial, OFF env exactness, live-key absence, one-run guard, single
install/launch, stream protection, env 2+2 preserve/restore, frame
filename, marker success syntax, OFF census non-requirement, 41-row
requirement, exact tick-sequence gate (static + functional: exact passes,
duplicated/missing tick fails), PPM pull, keyguard blocker, caps, unique OFF outputs,
finally cleanup, provisional marking, complete-before-exit +
wall-clamped 15 s drain, cleanup-failure-fails, no graphics verdict,
REPORT table, and checker device-freedom. `launch.py` compiles
(`py_compile`). No adb, install, launch, lease, or build was touched;
`result.json`/`driver.log` do not exist.

## 7. Gaps / handback

- No runtime result: OFF replay success, row/PPM bytes, and any ON/OFF
  comparison are all unproved until the separately gated run.
- Device stream history after N8D7M6 is untraced; only current exact
  bytes are gated at run time (two device SHAs).
- Same-input/output contract across devices is unprovable here (B):
  this preparation only proves the script is ready for an independent
  orchestrator SHA gate.
- Recommended next action (orchestrator decision): review this OFF SHA,
  then release the single OFF run in a separate gate.

| Condition | Outcome | Next action |
| --- | --- | --- |
| Script/checker ready, no runtime result | **A (this report)** | Orchestrator SHA-gates one OFF run |
| Same-input/output contract unprovable statically | B | State smallest gap |
| Preparation failure | OTHER | Diagnose scope first |

Receipts: `REPORT.md`, `launch.py`, `check.py`, `check-result.json`,
`check-selfcheck.txt` — commit `[N8D7M12] Part 5D1` with
`Orchestrated-By: opencode`, explicit paths only, no push.

(End of file)
