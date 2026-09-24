# N8D7M12 Part 7A — PKTSEQ replay-pair launcher (prepared, unexecuted)

**State: PREPARED, no device action. No adb command, install, launch,
lease, build, edit of any source/fork/APK/stream, Mac replay, push,
board/ledger edit, or upstream contact was executed in this part. Text
<512 KiB.**

Brief: `local/muse/prompts/N8D7M12P7.md` (Part 7A only). Goal: a
reviewed-SHA-held `launch.py` for exactly two same-settings diagnostic
replays (run1, run2; one launch each) of the already-staged
1,100,696,462-byte N8D7M6 stream on the Odin, using the gated P6M6 APK
with `PS2X_GS_REPLAY_PKTSEQ=1`, plus a `check.py` gate. Device patterns
follow the P5A launcher; only the five brief-listed changes differ.

## 1. Pins

| Item | Value |
| --- | --- |
| APK (local `~/dev/ssx3-work/N8D7M12P6M6/app-release.apk`) | 153,753,116 B, `da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262` |
| arm64 runner | `e5a3302c6bef489b04a4a143c47b01e616735f8db0acdbda663710a326c11af1` (Build ID `4c9c9d149900cdc3494201c38124d11bfb616fa3`) |
| Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` (unchanged) |
| HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` (unchanged) |
| Stream (local `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, device `<FILES>/n8d7m6.gs`) | 1,100,696,462 B, `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` (verify only, never pushed) |
| Odin serial | `622c49b1` read at runtime from `local/odin-serial` |
| Source base | fork `n8d7m12-app` @ `4fa0df1` (P6M6R gate A, ORCH-GATE-P2) |
| P5A launcher anchor | `local/research/N8D7M12P5A/launch.py` SHA `287140bf370acfb105f1b64347a635822300699150e517e6b912340ae031334e` |
| Scratch (outside git) | `~/dev/ssx3-work/N8D7M12P7/<run1\|run2>/` |
| Mac ON control rows | `local/research/N8D7M12P5F4P2/replay-excerpt.txt` (41 `GB4_PKTSEQ` + 41 `GB4_REPLAY`) |

## 2. The five allowed changes vs P5A (nothing else)

1. APK/runner pins to §1 values (APK path → `N8D7M12P6M6/`, size
   unchanged); Turnip/HAL/stream pins unchanged.
2. `PS2X_GS_REPLAY_PKTSEQ=1` appended to the replay env; the nine P5A
   keys stay in order, byte for byte.
3. Packaged-runner marker check gains `PS2X_GS_REPLAY_PKTSEQ` and
   `GB4_PKTSEQ tick=`; the six P5A markers stay.
4. Required `--run run1|run2` sets scratch `…/N8D7M12P7/<run>`, lease
   tag `N8D7M12P7 <run> replay` (release `LEASE_FREE N8D7M12P7 <run>
   done`), and remote basenames `n8d7m12p7-<run>-frames-<stamp>` /
   `n8d7m12p7-<run>-<stamp>.hashes`. Run-identity strings (brief
   field, one-run guard message, docstring title) renamed P5A→P7 with
   the run; nothing else renamed.
5. Post-loop, `GB4_PKTSEQ` lines are extracted from the full logcat
   into `<run>/pktseq.txt`; the run FAILS unless they are exactly 41
   rows with ticks 50..2050 in order.

Everything else (double SHAs, keyguard/battery/free checks, lease
claim, install-every-run, one launch, BACK, caps, force-stop +
PID-absent, env 2+2 restore, `finally` cleanup) stays.

## 3. Replay env (one key added; no live capture, no pad)

P5A's nine keys in order plus `PS2X_GS_REPLAY_PKTSEQ=1`, then the
per-run `PS2X_GS_REPLAY_PPM_DIR` / `PS2X_GS_REPLAY_OUT`. Forbidden and
asserted absent: `PS2X_GS_CAPTURE*`, `PS2X_PAD_SCRIPT*`,
`PS2X_CD_IMAGE`. Pre-existing device `ps2x.env` bytes are preserved
and restored with 2+2 SHA reads in `finally`, as in P5A. The pinned
stream is verified only — never pushed, altered, or deleted.

## 4. Exact unexecuted commands (separate run gate, Part 7B)

```sh
python3 -u local/research/N8D7M12P7/launch.py --run run1 --released-sha <reviewed launch.py SHA-256>
python3 -u local/research/N8D7M12P7/launch.py --run run2 --released-sha <reviewed launch.py SHA-256>
python3 local/research/N8D7M12P7/check.py --self-check
```

`launch.py` refuses without `--run run1|run2 --released-sha <its own
SHA>` and refuses if that run's `result.json`/`driver.log` already
exist (per-run one-run guard). No launch occurs if any gate fails.

## 5. Acceptance / stop table (per run; same as P5A plus PKTSEQ)

| # | Gate | Required | On failure |
| --- | --- | --- | --- |
| 1 | Local APK 2×SHA + size; 3 member 2×SHA; replay strings incl. PKTSEQ pair | exact pins §1 | stop, no device action |
| 2 | Local stream 2×SHA + size | exact pin §1 | stop |
| 3 | Serial `local/odin-serial` == `622c49b1`; all adb `-s` | match | stop |
| 4 | Lease free → claim per-run tag → re-read | persists | stop |
| 5 | `adb install -r` even if present; 2 device SHAs installed APK + stream | exact pins | stop, cleanup |
| 6 | Battery charging (status 2/5) ≥20%; free ≥10 GiB | met | stop, cleanup |
| 7 | Keyguard `showing=false` (pre-install and pre-start) | false | **BLOCKER, report; never worked around** |
| 8 | App stopped immediately before `am start` | empty pidof | stop, cleanup |
| 9 | One launch only; BACK once ~6 s | — | — |
| 10 | Stop at first complete tick2050 receipt (as P5A §10) | COMPLETE (provisional) | — |
| 11 | Stop at first parse/backend/control error | FAIL, first error recorded | cleanup |
| 12 | Process `_Exit` before receipt → wall-clamped ≤15 s drain, re-probe; 180 s without new replay rows; 600 s wall | stop w/ reason | cleanup |
| 13 | logcat ≤16 MiB; PPM+hashes ≤64 MiB | caps | stop w/ reason |
| 14 | `pktseq.txt` exactly 41 `GB4_PKTSEQ` rows, ticks 50..2050 in order | 41/41 ordered | FAIL, first failure recorded |
| 15 | Force-stop (even on `_Exit`), PID absent, pull `vq-002050.ppm` + hashes w/ 2+2 SHA match, env restore verified 2+2, release lease iff tag still ours; any cleanup failure → FAIL | cleanup | record first failure |

Outcome is marked **PROVISIONAL** until the orchestrator views the
PPMs and checks same-binary controls. No same-binary OFF control is
run or claimed in this part — the pair characterizes the ON replay
only. Elapsed time is a run control, never a speed number.

## 6. Validation (static + no-device self-tests only)

`check.py --self-check`: **37/37 PASS, verdict A** (`check-result.json`,
`check-selfcheck.txt`). Launcher SHA
`27d242fafc7fda6fcd7dd24f4069bdc5d7c580a135e49dc72eeb5853598b6d6b`.

| Group | Checks |
| --- | --- |
| Pins/anchor | P5A anchor SHA unchanged; new APK+runner present, old absent; Turnip/HAL/stream unchanged; P6M6 APK path + sizes |
| Listed changes | AST env proof (P5A block + exactly one appended key; key set = P5A ∪ PKTSEQ); 6+2 marker check; `--run` plumbing; pktseq extraction gate |
| Diff allowlist | 97 changed lines in 12 hunks: 26/26 pktseq lines exact-matched, every other non-blank line in pins/env/markers/runid, all 5 classes fired, 0 unmatched, 0 blank-only hunks |
| Preserved P5A behavior | serial scoping, replay keys, live-key absence, one-run guard, single install/launch, stream protection, env 2+2 restore, frame filename, marker syntax, keyguard blocker, caps, unique outputs, finally cleanup, provisional, wall-clamped drain, control-128 census, cleanup-fails, no OFF claim, REPORT table |
| No-device self-tests | arg-shape trio → usage rc=1; wrong SHA → hold rc=1; correct SHA + planted receipt → one-run guard rc=1 (plant removed); `pktseq_rows` accepts the 41 Mac-control rows (last = tick2050 `79ee00a3024bfb44`/1737496) and rejects drop/swap/dup/malformed/empty; `py_compile` both files; self-test paths proven to precede the first `preflight`/adb call; checker itself execs only `sys.executable launch.py` |

Negative controls (checker discriminates): appended foreign comment,
pktseq body tweak, and `PROGRESS_CAP` change each flip
`diff_only_listed_changes` to FAIL. Scratch
`~/dev/ssx3-work/N8D7M12P7/` is empty after the run. No adb, install,
launch, or lease was touched; neither run's `result.json`/`driver.log`
exists.

## 7. Receipts

- ssx3 (this dir): `REPORT.md`, `launch.py`, `check.py`,
  `check-result.json`, `check-selfcheck.txt` — commit `[N8D7M12] Part
  7A` with `Orchestrated-By: Muse Code`, explicit paths only, no push.
- Script SHA: see `check-result.json` `launch_sha` (recomputed at release).

## 8. Gaps / handback

- No runtime result: no install, launch, lease, or device contact of
  any kind happened in this part.
- Launcher SHA: `27d242fafc7fda6fcd7dd24f4069bdc5d7c580a135e49dc72eeb5853598b6d6b` (see §6).
- Recommended next action (orchestrator decision): review this SHA,
  then release the run pair in a separate gate (Part 7B).

| Condition | Outcome | Next action |
| --- | --- | --- |
| Script/checker ready, no runtime result | **A (this report)** | Orchestrator releases run1/run2 |
| Source/receipt mismatch | B (state smallest fix) | Fix and re-run `check.py` |
| Permission/resource failure | OTHER | Diagnose scope first |
