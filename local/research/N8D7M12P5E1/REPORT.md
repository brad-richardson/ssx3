# N8D7M12 Part 5E1 — same-settings OFF repeat launcher (PREPARED, unexecuted)

**State: PREPARED, no device action. Outcome sought: A = exact
same-settings script ready for a separate orchestrator SHA release (no
runtime result). No adb/device command, install, launch, lease, build,
push, APK/stream/source/fork edit, or board/global edit was executed in
this part. Text <512 KiB. P5D1 and ON receipts preserved untouched. No ON or OFF graphics verdict. Outcome stays PROVISIONAL until the
orchestrator SHA-gates and releases the OFF repeat run.**

Brief: `local/muse/prompts/N8D7M12P5E1.md`. Goal: a reviewed-SHA-held
**OFF vs OFF** repeat to measure run-to-run GPU variance on Odin. Part
5D2's OFF replay passed all run controls but differed from same-APK ON
at tick850, before the three capture flags act; 41 priv hashes matched
ON while VRAM matched 19/41 and present 25/41
(`local/research/N8D7M12P5D2/REPORT.md` §4). The ON/OFF causal
comparison is void. A second OFF run with the exact same
APK/stream/env/backend distinguishes reproducible OFF output from
same-settings variance; it still cannot by itself identify a renderer
root cause.

## 1. Pins (static, same as OFF1/P5D1 and ON)

| Item | Value |
| --- | --- |
| APK (local `~/dev/ssx3-work/N8D7M12P3/app-release.apk`) | 153,753,116 B, `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512` |
| arm64 runner | `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d` |
| Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` (unchanged) |
| HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` (unchanged) |
| Stream (local `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, device `<FILES>/n8d7m6.gs`) | 1,100,696,462 B, `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| Odin serial | `622c49b1` read at runtime from `local/odin-serial` |
| Source base | fork `n8d7m12-app` @ `a608ed1` (Part 2 gate A) |
| Scratch (outside git, OFF2-private) | `~/dev/ssx3-work/N8D7M12P5E1/` |
| OFF1 launcher SHA (P5D1 final, not reused) | `223fd15ec0aa45079f44bed7ceffd3e19381d12ac0c51587a0284afb9cd03170` |
| OFF2 launcher SHA | `ad22755d07cd4ce87cbd6823144181389e0b50d2a2f081f3cf879f54b80af4ca` |
| Checker result | `check.py --self-check`: **33/33 PASS, verdict A** (`check-result.json`, `check-selfcheck.txt`) |

OFF1 receipts preserved: `local/research/N8D7M12P5D1/` (`REPORT.md`,
`ORCH-GATE.md`, `launch.py`, `check.py`, `check-result.json`,
`check-selfcheck.txt`) untouched by this part. ON receipts preserved:
`local/research/N8D7M12P5A/` and OFF1 run scratch
`~/dev/ssx3-work/N8D7M12P5D1/parallel.hashes` untouched (read never,
written never in this part).

## 2. OFF2 env diff vs OFF1 (exact: labels/paths only)

| Key | OFF1 (P5D1 `launch.py`) | OFF2 (this dir `launch.py`) |
| --- | --- | --- |
| `PS2X_GS_REPLAY_ONDEVICE` | `1` | identical |
| `PS2X_GS_REPLAY_CAPTURE` | `<FILES>/n8d7m6.gs` | identical |
| `PS2X_GS_REPLAY_BACKEND` | `parallel` | identical |
| `PS2X_GS_TURNIP` | `1` | identical |
| `PS2X_N8D7F_SELECTED_CAPTURE` | absent | absent |
| `PS2X_N8D7L_ORACLE` | absent | absent |
| `PS2X_N8D5_TILE_CAPTURE` | absent | absent |
| `PS2X_GS_REPLAY_STEP` | `50` | identical |
| `PS2X_GS_REPLAY_PPM_TICKS` | `2050` | identical |
| `PS2X_GS_REPLAY_PPM_DIR` | OFF1 unique dir `n8d7m12p5d1-frames-<stamp>` | OFF2 unique dir `n8d7m12p5e1-frames-<stamp>` |
| `PS2X_GS_REPLAY_OUT` | OFF1 unique path `n8d7m12p5d1-<stamp>.hashes` | OFF2 unique path `n8d7m12p5e1-<stamp>.hashes` |

Only other text differences: scratch dir `N8D7M12P5D1` →
`N8D7M12P5E1`, lease tag `N8D7M12P5D1 replay` →
`N8D7M12P5E1 replay`, lease-free string, result `brief`, one-run guard
label, remote basenames `n8d7m12p5d1-` → `n8d7m12p5e1-`, and header
wording `Part 5D1 … OFF-control` → `Part 5E1 … OFF-repeat`. No pin, backend, stride, tick, cap,
install/launch-count, SHA-read, preflight, BACK, force-stop, PID,
env-restore, or `finally`-order change. Normalized proof: new launcher
with `N8D7M12P5E1`→`N8D7M12P5D1`, `n8d7m12p5e1-`→`n8d7m12p5d1-`,
`Part 5E1`→`Part 5D1` is byte-identical to the final P5D1 launcher
(checker `off2_normalized_identical_to_off1`).

Live keys asserted absent in both: `PS2X_GS_CAPTURE*`,
`PS2X_PAD_SCRIPT*`, `PS2X_CD_IMAGE` (`FORBIDDEN_ENV_KEYS` kept).

## 3. OFF2 receipt/census acceptance (same as OFF1)

OFF2 still requires: `GB4_REPLAY_SUMMARY markers=2050` (parallel), the
exact ordered `GB4_REPLAY` tick list 50,100,…,2050 through tick2050
(`EXPECTED_TICKS = tuple(range(50, 2051, 50))`, 41 rows, no duplicates,
none missing), `GB4_FRAME tick2050` tick=2050, `[n8d7m12] replay ok
markers=2050`, no `GB4_REPLAY_PARSE_ERROR` / `replay failed|rejected` /
parallel FATAL / Turnip fail, pull of `vq-002050.ppm` + hashes with 2+2
SHA match, and intact cleanup (force-stop, PID absent, env 2+2 restore,
lease release; any cleanup failure flips even a complete receipt to
FAIL).

OFF2 does **not** require: `[n8d5b]` control/sampled/raw, `[n8d6a]`
stages, `[n8d7f]` selected metadata/vectors, `[n8d7l]` oracle
metadata/controls/equality, `control=128/128`, or 448/896-tile vector
parsing. The ported N8D7M6 `tile_vector`/`parse_controls`/`probe`
parsers are retained verbatim for logging only; `census_gate` is an OFF
stub that always passes so missing markers cannot fail OFF, and the
error gate uses replay-marker errors only (`markers["errors"]`), never
census absence. `replay_complete` requires `replay_rows == 41` **and**
`replay_ticks == list(EXPECTED_TICKS)`; the `replay_rows` count is
retained for progress tracking only.

## 4. Predeclared OFF2-vs-OFF1 run comparison (later run gate only)

After the separately released OFF2 run, compare
`~/dev/ssx3-work/N8D7M12P5E1/parallel.hashes` against OFF1
`~/dev/ssx3-work/N8D7M12P5D1/parallel.hashes`:

- Both sides must hold 41 rows with the exact ordered ticks
  50,100,…,2050; any input/preflight/cleanup failure (including
  `first_failure` set or `cleanup_errors` non-empty) voids the
  comparison.
- Equality tallies: priv equality count, VRAM equality count, present
  equality count, first differing tick (or all-equal), PPM SHA equality
  plus orchestrator visual view of both `vq-002050.ppm` files.
- If OFF2 differs from OFF1 at any tick ≤2050 (in particular before
  2050): same-settings GPU variance is observed; reproducible-OFF is
  rejected on this pair.
- If OFF2 equals OFF1 across all 41 rows and PPM SHA/visual: the OFF
  output reproduces, and the earlier ON/OFF tick850 difference needs a
  separately controlled ON repeat or an env-state audit; no renderer
  root cause is identified by this pair alone.
- No diagnostic elapsed time is speed.

## 5. Exact unexecuted command (separate run gate)

```sh
python3 -u local/research/N8D7M12P5E1/launch.py --released-sha <reviewed OFF2 launch.py SHA-256>
python3 local/research/N8D7M12P5E1/check.py --self-check
```

`launch.py` refuses without `--released-sha <its own SHA>` and refuses
if `result.json`/`driver.log` already exist (one-run guard). No launch
occurs if any gate fails. A later part may release **one**
install/launch only using the exact reviewed SHA; no device call now.

## 6. Acceptance / stop table

| # | Gate | Required | On failure |
| --- | --- | --- | --- |
| 1 | Local APK 2×SHA + size; 3 member 2×SHA; replay strings | exact pins §1 | stop, no device action |
| 2 | Local stream 2×SHA + size | exact pin §1 | stop |
| 3 | Serial `local/odin-serial` == `622c49b1`; all adb `-s` | match | stop |
| 4 | OFF2 env is OFF1 env with only unique output paths; live keys absent; three flags absent both sides | §2 | stop, no run |
| 5 | OFF2 launcher is a fresh reviewed SHA (P5D1 SHA not reused); normalized diff identical | new gate | stop, no run |
| 6 | OFF2 yields SUMMARY (markers=2050, parallel) + exact tick list 50,…,2050 + `GB4_FRAME tick=2050` + `replay ok markers=2050` + PPM + hashes | §3 | FAIL/void, first error recorded |
| 7 | Missing selected/oracle/tile markers never fail OFF2 | §3 stub + checker | preparation FAIL if checker fails |
| 8 | Lease claim persists; one `install -r` + one `am start`; BACK once ~6 s | P5D1 rules kept | stop/cleanup |
| 9 | 600 s wall, 180 s progress, 16 MiB log, 64 MiB output caps | kept | stop w/ reason |
| 10 | Force-stop, PID absent, PPM+hashes 2+2 pull, env 2+2 restore, lease release in `finally`; any cleanup failure → FAIL | kept | record first failure |
| 11 | Keyguard `showing=false` pre-install and pre-start | BLOCKER, never worked around | report, no run |
| 12 | OFF2-vs-OFF1 comparison predeclared; any input/preflight/cleanup failure voids it | §4 | void comparison |
| 13 | No ON/OFF graphics verdict in this preparation part | — | — |

## 7. Validation (static only)

`check.py --self-check`: **33/33 PASS, verdict A** (`check-result.json`).
Launch SHA `ad22755d07cd4ce87cbd6823144181389e0b50d2a2f081f3cf879f54b80af4ca`.
Covers pins, OFF1 SHA pin, OFF env exactness, OFF2-vs-OFF1 env semantic
identity, normalized byte-identity (only listed path/label changes),
live-key absence, one-run guard, single install/launch, stream
protection, env 2+2 preserve/restore, frame filename, marker success
syntax, OFF census non-requirement, 41-row requirement, exact
tick-sequence gate (static + functional: exact passes,
duplicated/missing tick fails), PPM pull, keyguard blocker, caps,
unique OFF2 outputs, finally cleanup, provisional marking,
complete-before-exit + wall-clamped 15 s drain, cleanup-failure-fails,
no graphics verdict, REPORT table plus predeclared OFF2-vs-OFF1
comparison, and checker device-freedom. `launch.py` compiles
(`py_compile`). No adb, install, launch, lease, or build was touched;
`result.json`/`driver.log` do not exist.

## 8. Gaps / handback

- No runtime result: OFF2 replay success, row/PPM bytes, and any
  OFF2-vs-OFF1 comparison are all unproved until the separately gated
  run.
- Device stream history after N8D7M6 is untraced; only current exact
  bytes are gated at run time (two device SHAs).
- Same-input/output contract across runs is unprovable here (B): this
  preparation only proves the script is ready for an independent
  orchestrator SHA gate.
- Recommended next action (orchestrator decision): review this OFF2
  SHA, then release the single OFF repeat run in a separate gate.

| Condition | Outcome | Next action |
| --- | --- | --- |
| Script/checker ready, no runtime result | **A (this report)** | Orchestrator SHA-gates one OFF repeat run |
| Same-input/output contract unprovable statically | B | State smallest gap |
| Preparation failure | OTHER | Diagnose scope first |

Receipts: `REPORT.md`, `launch.py`, `check.py`, `check-result.json`,
`check-selfcheck.txt` — commit `[N8D7M12] Part 5E1` with
`Orchestrated-By: opencode`, explicit paths only, no push.

(End of file)
