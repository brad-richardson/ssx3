# N8D7M12 Part 5A — one-run Odin replay script (prepared, unexecuted)

**State: PREPARED, no device action. Outcome sought: A = script/checker ready
for orchestrator release (no runtime result). No adb/device command, install,
launch, lease, build, edit, or push was executed in this part. Text <512 KiB.**

Brief: `local/muse/prompts/N8D7M12P5A.md`. Goal: a reviewed-SHA-held
`launch.py` for exactly one diagnostic replay of the already-staged
1,100,696,462-byte N8D7M6 stream on the Odin, using the gated APK. Device
patterns follow N8D7M6 `launch.py`; replay env enters before EE boot via the
Part 2 branch (`ps2xRuntime/src/main.cpp:215-269` @ `a608ed1`).

## 1. Pins

| Item | Value |
| --- | --- |
| APK (local `~/dev/ssx3-work/N8D7M12P3/app-release.apk`) | 153,753,116 B, `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512` |
| arm64 runner | `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d` |
| Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` (unchanged) |
| HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` (unchanged) |
| Stream (local `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, device `<FILES>/n8d7m6.gs`) | 1,100,696,462 B, `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| Odin serial | `622c49b1` read at runtime from `local/odin-serial` |
| Source base | fork `n8d7m12-app` @ `a608ed1` (Part 2 gate A) |
| Scratch (outside git) | `~/dev/ssx3-work/N8D7M12P5A/` |

## 2. Source-grounded frame/marker syntax (confirmed by direct read)

- Frame file: `ps2_vq::dumpPpm(dir, tick)` writes `"%s/vq-%06llu.ppm"`
  (`ps2xRuntime/include/ps2_vq.h:115-125`), so tick 2050 with
  `PS2X_GS_REPLAY_PPM_DIR=<ppm_dir>` yields `<ppm_dir>/vq-002050.ppm`.
- Markers (`ps2xRuntime/src/lib/gs/gs_replay_core.cpp`): `GB4_REPLAY_SUMMARY
  mode=.. backend=.. packets=.. markers=..` (`:678-690`),
  `GB4_REPLAY tick=.. vram=.. priv=.. present=..` (sampled rows, `:505-510`),
  `GB4_FRAME tick=2050 backend=parallel pmode=.. present=..` (`:464-471`),
  `GB4_PARALLEL_STATS packets=.. init_ok=..`, `[n8d7f]/[n8d7l]` census lines.
- Exit lines (`ps2xRuntime/src/main.cpp`): `[n8d7m12] replay ok:
  packets=.. markers=..` + `_Exit(0)` on full gate (`:253-269`);
  `[n8d7m12] replay failed: ..` / `replay rejected: ..` + `_Exit(1)`.
- Replay-path census proven present: the Part 1 exact-stream Mac replay
  (`~/dev/ssx3-work/N8D7M12/mac-parallel.log:78279-78305`) emits
  `[n8d5b] alignment`, `control=128 expected=128 PASS`,
  `[n8d6a]` circuit1/pre_deinterlace_merged/final stages,
  `[n8d7f]` selected numerics + 448-tile vectors, `[n8d7l]`
  metadata/controls/equal, `GB4_FRAME tick=2050`, and
  `GB4_REPLAY_SUMMARY ... markers=2050` — the exact lines the ported
  N8D7M6 probe parses. On-device the same lines arrive via logcat with
  `I ps2x :` wrapping, which the ported `tile_vector` handles.

## 3. Replay env (no live capture, no pad — replay enters before EE boot)

`PS2X_GS_REPLAY_ONDEVICE=1`, `PS2X_GS_REPLAY_CAPTURE=<FILES>/n8d7m6.gs`,
`PS2X_GS_REPLAY_BACKEND=parallel`, `PS2X_GS_TURNIP=1`,
`PS2X_N8D7F_SELECTED_CAPTURE=1`, `PS2X_N8D7L_ORACLE=1`,
`PS2X_N8D5_TILE_CAPTURE=1`, `PS2X_GS_REPLAY_STEP=50`,
`PS2X_GS_REPLAY_PPM_TICKS=2050`, `PS2X_GS_REPLAY_PPM_DIR=<unique ppm_dir>`,
`PS2X_GS_REPLAY_OUT=<unique hashes_path>`. Forbidden and asserted absent:
`PS2X_GS_CAPTURE*`, `PS2X_PAD_SCRIPT*`, `PS2X_CD_IMAGE`. Pre-existing device
`ps2x.env` bytes are preserved with two device SHA reads + pull + two local
reads (all four must match) and restored the same way (push + two device
reads vs two local reads) in `finally` after force-stop; if none pre-existed
the pushed file is removed. Any cleanup failure (force-stop residue, env
restore mismatch, lease not ours) flips even a complete receipt to FAIL.
The pinned stream is verified only — never pushed, altered, or deleted.

## 4. Exact unexecuted command (separate run gate)

```sh
python3 -u local/research/N8D7M12P5A/launch.py --released-sha <reviewed launch.py SHA-256>
python3 local/research/N8D7M12P5A/check.py --self-check
```

`launch.py` refuses without `--released-sha <its own SHA>` and refuses if
`result.json`/`driver.log` already exist (one-run guard). No launch occurs
if any gate fails.

## 5. Acceptance / stop table

| # | Gate | Required | On failure |
| --- | --- | --- | --- |
| 1 | Local APK 2×SHA + size; 3 member 2×SHA; replay strings | exact pins §1 | stop, no device action |
| 2 | Local stream 2×SHA + size | exact pin §1 | stop |
| 3 | Serial `local/odin-serial` == `622c49b1`; all adb `-s` | match | stop |
| 4 | Lease free → claim unique tag → re-read | persists | stop |
| 5 | `adb install -r` even if present; 2 device SHAs installed APK + stream | exact pins | stop, cleanup |
| 6 | Battery charging (status 2/5) ≥20%; free ≥10 GiB | met | stop, cleanup |
| 7 | Keyguard `showing=false` (pre-install and pre-start) | false | **BLOCKER, report; never worked around** |
| 8 | App stopped immediately before `am start` | empty pidof | stop, cleanup |
| 9 | One launch only; BACK once ~6 s | — | — |
| 10 | Stop at first complete tick2050 receipt, evaluated BEFORE process liveness: `GB4_REPLAY_SUMMARY markers=2050` + `GB4_FRAME tick=2050` + `[n8d7m12] replay ok markers=2050` + full numeric census (parsed `control=128 expected=128 PASS`, tick-2050 alignment, selected 11-shared-field metadata, 448-tile summaries consistent with independently parsed vectors incl. packed SHA, 8 literal control addresses, recomputed oracle equality; N8D7M6 `tile_vector`/`parse_controls` rules reused verbatim) | COMPLETE (provisional) | — |
| 11 | Stop at first `GB4_REPLAY_PARSE_ERROR` / `replay failed|rejected` / parallel FATAL / Turnip fail / control FAIL / census mismatch | FAIL, first error recorded | cleanup |
| 12 | Process `_Exit` before receipt → short final drain (≤15 s, extends only on new lines, hard-clamped to the launch start + 600 s wall deadline so the run cannot overrun the cap after exit), re-probe, then COMPLETE or "process exited without complete receipt"; 180 s without new `GB4_REPLAY` rows; 600 s wall | stop w/ reason | cleanup |
| 13 | logcat ≤16 MiB; PPM+hashes ≤64 MiB | caps | stop w/ reason |
| 14 | Force-stop (even on `_Exit`), PID absent, pull `vq-002050.ppm` + hashes w/ 2+2 SHA match, env restore verified 2+2, release lease iff tag still ours; any cleanup failure → FAIL | cleanup | record first failure |

Outcome is marked **PROVISIONAL** until the orchestrator views `vq-002050.ppm`
and checks same-binary controls. One replay does not establish default-off
behavior (no same-binary OFF control is run or claimed in this part),
a root cause, or speed.

## 6. Validation (static only)

`check.py --self-check`: 24/24 PASS, verdict A (`check-result.json`). Covers
pins/sizes, serial scoping, replay keys, live-key absence, one-run guard,
single install/launch, stream protection, env 2+2-SHA preserve/restore,
frame filename, marker/census syntax, keyguard blocker, caps, unique
outputs, finally cleanup, provisional marking, complete-before-exit +
wall-clamped 15 s drain, control-128 numeric census (ported N8D7M6 parser),
cleanup-failure-fails-outcome, no OFF-control claim, REPORT table, and
checker device-freedom. `launch.py` compiles (`py_compile`). No adb,
install, launch, or lease was touched; `result.json`/`driver.log` do not
exist.

## 7. Receipts

- ssx3 (this dir): `REPORT.md`, `launch.py`, `check.py`, `check-result.json`,
  `check-selfcheck.txt` — commit `[N8D7M12] Part 5A` with
  `Orchestrated-By: opencode`, explicit paths only, no push.
- Script SHA: see `check-result.json` `launch_sha` (recomputed at release).

## 8. Gaps / handback

- No runtime result: default-off behavior, Turnip loader path, census values,
  frame content, and speed are all unproved until the gated run.
- Device stream history after N8D7M6 is untraced; only current exact bytes
  are gated at run time (two device SHAs).
- Same-binary ON/OFF controls and orchestrator frame view are required before
  any A/B-style comparison claim. No same-binary OFF control is run or
  claimed in this part — the census gate characterizes the ON replay only.
- Recommended next action (orchestrator decision): review this SHA, then
  release the single run in a separate gate.

| Condition | Outcome | Next action |
| --- | --- | --- |
| Script/checker ready, no runtime result | **A (this report)** | Orchestrator releases one run |
| Source/receipt mismatch | B (state smallest fix) | Fix and re-run `check.py` |
| Permission/resource failure | OTHER | Diagnose scope first |
