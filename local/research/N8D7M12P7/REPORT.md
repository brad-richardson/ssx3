# N8D7M12 Part 7 — PKTSEQ Odin replay pair (7A launcher + 7B runs)

**State: 7A PREPARED (no device action) then 7B COMPLETE (two Odin
runs, no retries). 7B: exactly 2 installs and 2 launches of the
released launcher SHA `5983f315…b934aa` (orchestrator-amended 7A gate,
`ORCH-GATE-7A.md`). No script/APK/stream/source/fork edit, no Mac
replay, no push, no board/ledger edit, no upstream contact. Text
<512 KiB; device output ≤64 MiB per run. Elapsed time is run control
only, never a speed number. No graphics verdict — evidence rows only,
reading left to the orchestrator.**

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
| Script/checker ready, no runtime result | **A (7A part of this report)** | Orchestrator releases run1/run2 |
| Source/receipt mismatch | B (state smallest fix) | Fix and re-run `check.py` |
| Permission/resource failure | OTHER | Diagnose scope first |

---

# Part 7B — two PKTSEQ Odin runs + three-way comparison (COMPLETE)

Released commands, from `/Users/brad/dev/ssx3`:

```sh
python3 -u local/research/N8D7M12P7/launch.py --run run1 --released-sha 5983f315982ea08eb41c8fe0593e57e7b59c272faad7ae516a4300ac78b934aa
python3 -u local/research/N8D7M12P7/launch.py --run run2 --released-sha 5983f315982ea08eb41c8fe0593e57e7b59c272faad7ae516a4300ac78b934aa
python3 local/research/N8D7M12P7/compare.py
```

## 7B.1. Preflight (all PASS before each launch)

| # | Gate | run1 | run2 |
| --- | --- | --- | --- |
| 1 | Script SHA == released gated | `5983f315…b934aa` exact | same, re-verified |
| 2 | No `<run>/result.json`/`driver.log` | scratch empty | `run1/` present, no `run2/` receipt |
| 3 | Serial | `622c49b1` | `622c49b1` |
| 4 | Lease free | `LEASE_FREE N8D7M12P5E1 done` | `LEASE_FREE N8D7M12P7 run1 done` |
| 5 | No app run | `pidof` empty | `pidof` empty |
| 6 | Battery | 100%, status 3, AC powered (amended gate) | same |
| 7 | Free | ~23.1 GiB on /data (≥10 GiB) | ~23.1 GiB |
| 8 | Keyguard | `showing=false` pre-install and pre-start | same |
| 9 | No simultaneous mini boot/heavy job | P-lane slots 1+2 free; only idle procs (one 0-CPU `devicectl` iOS handle noted, not a mini job) | slot 1 held by this pair, slot 2 free |

P-lane slot 1 claimed before run1, released after run2 (both slots
free at handback).

## 7B.2. Run receipts (one install + one launch each, no retries)

| Field | run1 | run2 |
| --- | --- | --- |
| Launch SHA | `5983f315…b934aa` | same |
| Lease | `N8D7M12P7 run1 replay` claimed → `LEASE_FREE N8D7M12P7 run1 done` | `N8D7M12P7 run2 replay` claimed → `LEASE_FREE N8D7M12P7 run2 done` |
| Install | one `adb install -r`, Success; device APK `da9a41a8…e6ef262` ×2 | same |
| Device stream (verify only) | `f6a78f71…a593` ×2, 1,100,696,462 B | same |
| Env preserve | `176eff84…cef32d` 2+2 match; replay env `5ad93947…6a8b4dc` | `176eff84…cef32d` 2+2 match; replay env `68a15bdc…5d186b5` |
| Launch | one `am start`, PID 11967; BACK once ~6 s | one `am start`, PID 12374; BACK once ~6 s |
| Stop | complete tick2050 receipt, elapsed 13.149 s (control only) | complete tick2050 receipt, elapsed 13.070 s (control only) |
| Progress | 41 `GB4_REPLAY` rows, ticks 50..2050; no error; no drain path | same |
| Markers | SUMMARY queue/parallel 862958/11499/25445/2050; FRAME 2050 parallel ff21 `5d5972bc`; `replay ok` 862958/2050 | SUMMARY identical; FRAME present `883449`; `replay ok` identical |
| PKTSEQ | 41 rows, ticks 50..2050, commands_last=1737496 | same |
| Caps | logcat gzip 4,125 B (≤16 MiB); PPM+hashes 690,829 B (≤64 MiB) | gzip 4,304 B; PPM+hashes 690,829 B |
| Postrun | force-stop, PID absent (re-verified after run2: NO_PID) | force-stop, PID absent |
| Env restore | pre-existing bytes restored, 2+2 match | same |
| `first_failure` / `cleanup_errors` | `not found` / none | `not found` / none |
| Verdict | `PROVISIONAL PASS` | `PROVISIONAL PASS` |

## 7B.3. Artifacts (private scratch `~/dev/ssx3-work/N8D7M12P7/`)

| File | SHA-256 (2 device + 2 local) | Size |
| --- | --- | --- |
| `run1/vq-002050.ppm` | `65a544a7603f26aa8f3ab77badb0440b4f0abb44ac81ca81bb777d9a11fe82db` | 688,143 B |
| `run1/parallel.hashes` | `e5b1a34f566360e994f16def5357a3aa3861a276faf3e189ac4df9546426a616` | 2,686 B |
| `run2/vq-002050.ppm` | `d2261c63de5fd274a223f3ba6f2c969a3d7511ea50a0056fac2f05d5099550b6` | 688,143 B |
| `run2/parallel.hashes` | `8039561f9ff033b44c514ca30164faa576a3da3573372ed49afc582868009f90` | 2,686 B |
| Mac ON `vq-002050.ppm` | `9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e` | 688,143 B |

Absolute PPM paths for orchestrator viewing:

- `/Users/brad/dev/ssx3-work/N8D7M12P7/run1/vq-002050.ppm`
- `/Users/brad/dev/ssx3-work/N8D7M12P7/run2/vq-002050.ppm`
- `/Users/brad/dev/ssx3-work/N8D7M12P5F4/mac-pktseq/frames/vq-002050.ppm` (Mac ON control; full SHA matches the P5F4P2 pinned truncation `9490484c…14fce3e`)

## 7B.4. Three-way comparison (`compare.py`, `compare-output.txt`)

All six sides: 41 rows, exact ordered ticks 50..2050. No
input/preflight/cleanup failure, so the comparison is valid per the
predeclared rule.

| Field | run1==run2 | run1==mac | run2==mac |
| --- | --- | --- | --- |
| PKTSEQ `seq` | **41/41**, no diff | **41/41**, no diff | **41/41**, no diff |
| PKTSEQ `commands` | **41/41**, no diff | **41/41**, no diff | **41/41**, no diff |
| `priv` | **41/41**, no diff | **41/41**, no diff | **41/41**, no diff |
| `vram` | 19/41, first **tick850** | 3/41 (ticks 100, 250, 1600), first tick50 | 3/41, first tick50 |
| `present` | 25/41, first **tick850** | 0/41, first tick50 | 0/41, first tick50 |
| PPM | differ | differ | differ |

Matching vram ticks run1==run2 (19): 50–800 (16) + 1500, 1550, 1600.
Differing present ticks run1==run2 (16): 850–1150 (7) + 1650–2050 (9).

tick2050 rows:

- run1: pktseq `79ee00a3024bfb44`/1737496, `vram=8a80c3fd priv=6621fe06 present=5d5972bc`
- run2: pktseq `79ee00a3024bfb44`/1737496, `vram=6c2e01c3 priv=6621fe06 present=00883449`
- mac: pktseq `79ee00a3024bfb44`/1737496, `vram=c883a705 priv=6621fe06 present=d19b96fe`

First-difference example (tick850, oracle-confirmed by grep):

- run1: `vram=96dcc73d priv=60a25873 present=4afe2f42`
- run2: `vram=61cae10d priv=60a25873 present=03dda521`
- mac: `vram=5882f9f4 priv=60a25873 present=b0cec9c2`

(tick850 priv `60a25873` is also the value in the old-APK OFF pair and
the Mac excerpt — guest state identical across APKs and hosts at this
tick.)

41-row per-tick table (`=` equal, `X` differ; columns per field are
run1==run2, run1==mac, run2==mac; full text in `compare-output.txt`):

```text
tick=   50 === === === =XX =XX
tick=  100 === === === === =XX
tick=  150 === === === =XX =XX
tick=  200 === === === =XX =XX
tick=  250 === === === === =XX
tick=  300 === === === =XX =XX
tick=  350 === === === =XX =XX
tick=  400 === === === =XX =XX
tick=  450 === === === =XX =XX
tick=  500 === === === =XX =XX
tick=  550 === === === =XX =XX
tick=  600 === === === =XX =XX
tick=  650 === === === =XX =XX
tick=  700 === === === =XX =XX
tick=  750 === === === =XX =XX
tick=  800 === === === =XX =XX
tick=  850 === === === XXX XXX
tick=  900 === === === XXX XXX
tick=  950 === === === XXX XXX
tick= 1000 === === === XXX XXX
tick= 1050 === === === XXX XXX
tick= 1100 === === === XXX XXX
tick= 1150 === === === XXX XXX
tick= 1200 === === === XXX =XX
tick= 1250 === === === XXX =XX
tick= 1300 === === === XXX =XX
tick= 1350 === === === XXX =XX
tick= 1400 === === === XXX =XX
tick= 1450 === === === XXX =XX
tick= 1500 === === === =XX =XX
tick= 1550 === === === =XX =XX
tick= 1600 === === === === =XX
tick= 1650 === === === XXX XXX
tick= 1700 === === === XXX XXX
tick= 1750 === === === XXX XXX
tick= 1800 === === === XXX XXX
tick= 1850 === === === XXX XXX
tick= 1900 === === === XXX XXX
tick= 1950 === === === XXX XXX
tick= 2000 === === === XXX XXX
tick= 2050 === === === XXX XXX
```

(column order: seq, commands, priv, vram, present)

## 7B.5. Predeclared-reading evidence rows (orchestrator decides)

| Predeclared condition | Evidence in this pair |
| --- | --- |
| PKTSEQ equal 41/41 across all three while VRAM/present differ | **Condition met**: `seq` and `commands` 41/41 on all three pairs; vram/present differ run-vs-run from tick850 and vs Mac from tick50; all three PPMs differ |
| PKTSEQ differing between runs or from the Mac | Not observed: no differing tick on any pair |
| `commands` mismatch with equal `seq` or the reverse | Not observed |
| Preflight/cleanup failure voids the pair | No failure on either run |

## 7B.6. Gaps / handback

- Frame content unviewed by this worker; PPM paths in §7B.3 for
  orchestrator viewing.
- Device stream history after N8D7M6 remains untraced; only current
  exact bytes gated (two device SHAs per run).
- `compare.py` parses log order, not names: one priv/vram index swap
  was caught during writing (Mac-excerpt cross-check) and fixed before
  any number was quoted; key cells re-verified with `grep`/`shasum`.
- Budgets: 2 installs, 2 launches, 0 builds; active run time ~13 s
  per run (control only), well under the 600 s cap.
- Recommended next action (orchestrator decision): read §7B.5 against
  the predeclared rule; the pair is complete either way.

Receipts: `REPORT.md` (this file), `compare.py`,
`compare-output.txt` — commit `[N8D7M12] Part 7B` with
`Orchestrated-By: Muse Code`, explicit paths only, no push. (`launch.py`
is the orchestrator-amended release, committed at the 7A gate; the
7A `check.py` 36/37 read is expected and left untouched.)
