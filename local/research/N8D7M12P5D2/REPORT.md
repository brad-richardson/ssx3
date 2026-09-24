# N8D7M12 Part 5D2 — one same-APK Odin OFF replay (COMPLETE, comparison VOID)

**State: device run COMPLETE. Exactly one install and one launch of
the reviewed OFF launcher SHA
`223fd15ec0aa45079f44bed7ceffd3e19381d12ac0c51587a0284afb9cd03170`.
No retry, no second install/launch, no script/APK/stream/source/fork
edit, no Mac replay, no push, no board/global edit, no upstream
contact. Text <512 KiB; PPM/logcat/hashes stay outside git in
`~/dev/ssx3-work/N8D7M12P5D1/`. ON receipts preserved byte-exact.
Elapsed time is run control only, never a speed number. No
OFF selected tile census is expected or claimed. No graphics
root-cause verdict — evidence rows only, verdict left to the
orchestrator.**

Brief: `local/muse/prompts/N8D7M12P5D2.md`. Released command, from
`/Users/brad/dev/ssx3`:

```sh
python3 -u local/research/N8D7M12P5D1/launch.py --released-sha 223fd15ec0aa45079f44bed7ceffd3e19381d12ac0c51587a0284afb9cd03170
```

## 1. Preflight (all PASS before launch)

| # | Gate | Observation |
| --- | --- | --- |
| 1 | Script SHA == reviewed final | `223fd15e…03170` exact |
| 2 | `check.py --self-check` | 30/30 PASS, verdict A |
| 3 | `py_compile` | OK |
| 4 | No OFF `result.json`/`driver.log` | both absent before launch |
| 5 | ON receipts pinned | `parallel.hashes` `0e89a493…c82a` (2686 B), `vq-002050.ppm` `39b70d67…0d41` (688,143 B) |
| 6 | Serial | `622c49b1` |
| 7 | Lease free | `LEASE_FREE N8D7M12P5A done` |
| 8 | No app run | `pidof com.ps2x.runner` empty |
| 9 | Battery | 100%, status 5 |
| 10 | Free | ~24.8 GB on /data (≥10 GiB) |
| 11 | Keyguard | `showing=false` pre-install and pre-start |
| 12 | No simultaneous host heavy job | only clangd LSP |

## 2. Run receipt (one install, one launch)

| Field | Observation |
| --- | --- |
| Lease | `N8D7M12P5D1 replay` claimed, re-read persists; released `LEASE_FREE N8D7M12P5D1 done` (tag ours) |
| Install | one `adb install -r`, Success; device APK `caa11102…f512` ×2 |
| Device stream (verify only) | `f6a78f71…a593` ×2, 1,100,696,462 B |
| Env preserve | `176eff84…cef32d` 2 device + 2 local match; replay env `1e2284a6…51aaf99` (OFF: three flags absent) |
| Launch | one `am start`, PID 8778; BACK once ~6 s |
| Stop | `first complete tick2050 summary/frame (PROVISIONAL OFF)`, elapsed 14.277 s (control only) |
| Progress | 41 `GB4_REPLAY` rows, exact ticks 50..2050; no error row; no drain path |
| Markers | SUMMARY queue/parallel 862958/11499/25445/2050; FRAME 2050 parallel ff21 `1dc1aba8`; `replay ok` 862958/2050 |
| Caps | logcat gzip 2,376 B (≤16 MiB); PPM+hashes 690,829 B (≤64 MiB) |
| Postrun | `am force-stop`, PID absent (re-verified after run) |
| Env restore | pre-existing bytes restored, 2+2 reads match `176eff84…cef32d` |
| `first_failure` / `cleanup_errors` | `not found` / none |
| Verdict | `PROVISIONAL PASS`, provisional until orchestrator views OFF PPM |

## 3. OFF artifacts (private scratch `~/dev/ssx3-work/N8D7M12P5D1/`)

| File | SHA-256 (2 device + 2 local) | Size |
| --- | --- | --- |
| `vq-002050.ppm` | `5e0caca3773096d51595530fe3278cc92ca42b59f590a5c4e0d3e84d05adbea4` | 688,143 B |
| `parallel.hashes` | `19738cc310ff81552546477ae040061f780124b19fefbccad0f671537c783af9` | 2,686 B |

Absolute OFF PPM path for orchestrator viewing:
`/Users/brad/dev/ssx3-work/N8D7M12P5D1/vq-002050.ppm`

## 4. ON/OFF comparison (OFF vs `~/dev/ssx3-work/N8D7M12P5A/parallel.hashes`)

Both sides: 41 rows, exact ordered ticks 50,100,…,2050.

| Field | Match |
| --- | --- |
| priv | **41/41** |
| vram | 19/41 |
| present | 25/41 (tick1200 present matches, vram differs) |
| First differing row | **tick850** (≤2000) |
| Differing ticks (22) | 850,900,950,1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1650,1700,1750,1800,1850,1900,1950,2000,2050 |
| Matching ticks (19) | 50–800 (16 rows), 1500,1550,1600 |
| tick2050 | ON `vram=4ba27b77 priv=6621fe06 present=b167a719`; OFF `vram=9035e824 priv=6621fe06 present=1dc1aba8` (priv equal) |
| PPM | ON `39b70d67…0d41` vs OFF `5e0caca3…adbea4` — differ |

Example first difference (tick850):
ON `vram=00c4eed5 priv=60a25873 present=6e74ea59` vs
OFF `vram=23589ef3 priv=60a25873 present=9d6d204c` (priv equal).

## 5. Outcome table (predeclared P5C §4 rule applied)

| Condition | Outcome | Next action |
| --- | --- | --- |
| OFF rows differ from ON at ticks ≤2000 (first at tick850) | **VOID — nondeterministic device variance or harness fault (this run)** | Diagnose variance before any ON/OFF comparison; do not read a measurement effect |
| Rows match through 2000, tick2050/PPM differ | possible measurement effect (not this run) | — |
| All rows and PPM match | persistence without measurement flags (not this run) | — |

Reading: the three flags are unread on ticks 50–2000 (P5C §2 rows
2–4), so divergence starting at tick850 cannot be instrumentation. The
41/41 priv equality shows the emulated logic stream is identical; only
GPU-side vram/present hashes vary run-to-run (intermittent: 19 ticks
match mid-run, including 1500/1550/1600 after a diverging stretch).
The OFF PPM difference is uninterpretable for the measurement-effect
question under this void. These are evidence rows, not a root-cause
verdict.

## 6. Validation

`check.py` (this dir): **14/14 PASS, verdict A** (`check-result.json`).
Covers OFF launcher SHA, ON byte-preservation, OFF result presence +
replay-ok + one-install/launch + no-failure + clean cleanup, OFF
41-row exact-tick gate, 41×41 comparison with VOID classification,
OFF PPM presence/SHA/path. Device-free. ON receipts rehashed after
the run: exact pins hold.

## 7. Gaps / handback

- The ON/OFF measurement-effect comparison is VOID on this pair:
  GPU-side hash nondeterminism across same-APK Odin runs must be
  characterized before any instrumentation reading is possible.
- Frame content unviewed by this worker; OFF PPM listed above for
  orchestrator viewing.
- No OFF selected/oracle/tile census by design; not compared, not invented.
- Device stream history after N8D7M6 remains untraced; only current
  exact bytes gated (two device SHAs here).
- Recommended next action (orchestrator decision): determine whether
  vram/present run-to-run variance reproduces (repeat-same-env pair)
  before re-attempting the ON/OFF measurement comparison.

Receipts: `REPORT.md`, `check.py`, `check-result.json` — commit
`[N8D7M12] Part 5D2` with `Orchestrated-By: opencode`, explicit paths
only, no push.

(End of file)
