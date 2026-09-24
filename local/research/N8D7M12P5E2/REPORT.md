# N8D7M12 Part 5E2 — one same-settings Odin OFF repeat (COMPLETE, VARIANCE OBSERVED)

**State: device run COMPLETE. Exactly one install and one launch of
the reviewed OFF2 launcher SHA
`ad22755d07cd4ce87cbd6823144181389e0b50d2a2f081f3cf879f54b80af4ca`.
No retry, no second install/launch, no script/APK/stream/source/fork
edit, no Mac replay, no push, no board/global edit, no upstream
contact. Text <512 KiB; PPM/logcat/hashes stay outside git in
`~/dev/ssx3-work/N8D7M12P5E1/`. OFF1 (`~/dev/ssx3-work/N8D7M12P5D1/`)
and ON receipts preserved byte-exact. Elapsed time is run control
only, never a speed number. No graphics root-cause verdict — evidence
rows only, verdict left to the orchestrator.**

Brief: `local/muse/prompts/N8D7M12P5E2.md`. Released command, from
`/Users/brad/dev/ssx3`:

```sh
python3 -u local/research/N8D7M12P5E1/launch.py --released-sha ad22755d07cd4ce87cbd6823144181389e0b50d2a2f081f3cf879f54b80af4ca
```

## 1. Preflight (all PASS before launch)

| # | Gate | Observation |
| --- | --- | --- |
| 1 | Script SHA == reviewed gated | `ad22755d…0af4ca` exact |
| 2 | `check.py --self-check` (P5E1) | 33/33 PASS, verdict A |
| 3 | `py_compile` | OK |
| 4 | No OFF2 `result.json`/`driver.log` | scratch `~/dev/ssx3-work/N8D7M12P5E1/` absent before launch |
| 5 | OFF1 receipts pinned | `parallel.hashes` `19738cc3…783af9` (2686 B, 41 rows), `vq-002050.ppm` `5e0caca3…adbea4` (688,143 B) |
| 6 | Serial | `622c49b1` |
| 7 | Lease free | `LEASE_FREE N8D7M12P5D1 done` |
| 8 | No app run | `pidof com.ps2x.runner` empty |
| 9 | Battery | 100%, status 5, AC powered |
| 10 | Free | ~24.8 GB on /data (≥10 GiB) |
| 11 | Keyguard | `showing=false` pre-install and pre-start (launcher double-gated) |
| 12 | No simultaneous host heavy job | only clangd LSP |

## 2. Run receipt (one install, one launch)

| Field | Observation |
| --- | --- |
| Launch SHA | `ad22755d07cd4ce87cbd6823144181389e0b50d2a2f081f3cf879f54b80af4ca` |
| Lease | `N8D7M12P5E1 replay` claimed, released `LEASE_FREE N8D7M12P5E1 done` (tag ours) |
| Install | one `adb install -r`, Success; device APK `caa11102…f512` ×2 |
| Device stream (verify only) | `f6a78f71…a593` ×2, 1,100,696,462 B |
| Env preserve | `176eff84…cef32d` 2 device + 2 local match; replay env `ac0ae2d1…c14cce0c` (OFF: three flags absent) |
| Launch | one `am start`, PID 11301; BACK once ~6 s |
| Stop | `first complete tick2050 summary/frame (PROVISIONAL OFF)`, elapsed 13.122 s (control only) |
| Progress | 41 `GB4_REPLAY` rows, exact ticks 50..2050; no error row; no drain path |
| Markers | SUMMARY queue/parallel 862958/11499/25445/2050; FRAME 2050 parallel ff21 `5b60d0a1`; `replay ok` 862958/2050 |
| Caps | logcat gzip 2,377 B (≤16 MiB); PPM+hashes 690,829 B (≤64 MiB) |
| Postrun | `am force-stop`, PID absent (re-verified after run: NO_PID) |
| Env restore | pre-existing bytes restored, 2+2 reads match `176eff84…cef32d` |
| `first_failure` / `cleanup_errors` | `not found` / none (absent key) |
| Verdict | `PROVISIONAL PASS`, provisional until orchestrator views OFF2 PPM |

## 3. OFF2 artifacts (private scratch `~/dev/ssx3-work/N8D7M12P5E1/`)

| File | SHA-256 (2 device + 2 local) | Size |
| --- | --- | --- |
| `vq-002050.ppm` | `050d864fe17b72e1cf08ea9eab49342a9e1f079ac08d91b58df1189d49b898b6` | 688,143 B |
| `parallel.hashes` | `e78d7589db261658352f5a1216c7d62c2daa08bc7c63cfec68c4ec08ec4c580e` | 2,686 B |

Absolute OFF2 PPM path for orchestrator viewing:
`/Users/brad/dev/ssx3-work/N8D7M12P5E1/vq-002050.ppm`

## 4. OFF2-vs-OFF1 comparison (same settings, same APK/stream/env/backend)

Both sides: 41 rows, exact ordered ticks 50,100,…,2050. No
input/preflight/cleanup failure, so the comparison is valid per the
predeclared rule.

| Field | Match |
| --- | --- |
| priv | **41/41** |
| vram | 16/41 |
| present | 25/41 |
| First differing row | **tick850** |
| Differing ticks (25) | 850,900,950,1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1500,1550,1600,1650,1700,1750,1800,1850,1900,1950,2000,2050 |
| Matching ticks (16) | 50–800 (16 rows) |
| tick2050 | OFF1 `vram=9035e824 priv=6621fe06 present=1dc1aba8`; OFF2 `vram=131730e2 priv=6621fe06 present=5b60d0a1` (priv equal) |
| PPM | OFF1 `5e0caca3…adbea4` vs OFF2 `050d864f…9b898b6` — differ |

Example first difference (tick850):
OFF1 `vram=23589ef3 priv=60a25873 present=9d6d204c` vs
OFF2 `vram=f4b5d042 priv=60a25873 present=52bf27d0` (priv equal).

## 5. Outcome table (predeclared P5E1 §4 rule applied)

| Condition | Outcome | Next action |
| --- | --- | --- |
| OFF2 differs from OFF1 at ticks ≤2050 (first at tick850) | **SAME-SETTINGS VARIANCE OBSERVED; reproducible-OFF rejected on this pair (this run)** | Characterize variance before any ON/OFF causal claim; do not read a measurement effect |
| All rows and PPM match | reproduced (not this run) | — |

Reading: guest priv state is identical across all 41 ticks while
GPU-side vram/present vary from tick850 on with the same APK, stream,
env and backend. These are evidence rows, not a root-cause verdict.
No speed number from diagnostic elapsed time.

## 6. Validation

`check.py` (this dir): **16/16 PASS, verdict A** (`check-result.json`,
`check-output.txt`). Covers OFF2 launcher SHA, OFF1 byte-preservation,
OFF2 result presence + replay-ok + one-install/launch + no-failure +
clean cleanup + script SHA, OFF2 41-row exact-tick gate, 41×41
OFF1/OFF2 comparison with variance classification, OFF2 PPM
presence/SHA/path. Device-free. OFF1 receipts rehashed after the run:
exact pins hold. Read-only adb recheck: app PID absent, lease
`LEASE_FREE N8D7M12P5E1 done`.

## 7. Gaps / handback

- Frame content unviewed by this worker; OFF2 PPM listed above for
  orchestrator viewing.
- Device stream history after N8D7M6 remains untraced; only current
  exact bytes gated (two device SHAs here).
- Recommended next action (orchestrator decision): treat Odin GPU
  output as run-varying on this pair; gate any further ON/OFF
  comparison on a variance-characterization plan.

Receipts: `REPORT.md`, `check.py`, `check-result.json`,
`check-output.txt` — commit `[N8D7M12] Part 5E2` with
`Orchestrated-By: opencode`, explicit paths only, no push.

(End of file)
