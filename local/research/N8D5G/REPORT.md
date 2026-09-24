# N8D5G — one Odin tile probe

**State:** Released script completed one Odin install and one launch. The orchestrator still owns visual inspection of the frame and the causal verdict.

## Preregistered gate

| Category | Required first aligned live receipt at tick 2050 |
| --- | --- |
| A | FBP 112, PMODE `ff21`, 512×448; control `128 expected=128 PASS`; both summaries have 896 tiles; sampled active ≤100 and raw active ≤100; matching tick-2050 frontend PNG and metadata. |
| B | Same alignment, control, summary size and frontend requirements; sampled active ≥500 and raw active ≤100. |
| OTHER | Every other observation, including a missing frontend PNG. No causal verdict. |

## Fixed inputs and intended run

| Field | Pin or plan |
| --- | --- |
| Main gate | `a5fc957`; orchestrator states N8D5F package PASS. |
| APK | `/Users/brad/dev/ssx3-work/N8D5F/app-release.apk`; SHA-256 `8c101c4824adbda8f2fa7126692791189e4d05df7e450680ff2b6e67d0be66a0`. |
| Packaged runner | SHA-256 `d1916d7bce3cc789c3e25d8e90c4db9cd0d1bcbfb037d27d4b3a6b1932476456`; Build ID `f01ab9e6c249f488717eab21f5f3c6cf43130190`. |
| Turnip | SHA-256 `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`. |
| Installed ELF | SHA-256 `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`. |
| Installed ISO | SHA-256 `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`. |
| Odin | Serial `622c49b1`; lease `/data/local/tmp/mg/LEASE`; one install and one launch after release. |
| Environment | `PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`, `PS2X_SKIP_MOVIE=1`, installed ISO, I26-FAST vsync pad route, `PS2X_N8D5_TILE_CAPTURE=1`, `PS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999`, unique dump dir, `PS2X_VSYNC_RATE_LOG=1`. |
| Script | `local/research/N8D5G/launch.py`; SHA-256 `b17b948b18cebc7f8d142668d49f0163cf36048a472937f7462c70b5bed889f6` on both reads. |
| Launch command | `python3 -u local/research/N8D5G/launch.py --released-sha b17b948b18cebc7f8d142668d49f0163cf36048a472937f7462c70b5bed889f6` from repo root, only after orchestrator release. |

## Run receipt

| Field | Observation |
| --- | --- |
| Local APK double SHA read | `8c101c4824adbda8f2fa7126692791189e4d05df7e450680ff2b6e67d0be66a0` on both reads; matches release pin. |
| Device preflight | `device`, lease `LEASE_FREE N8D5E done`, keyguard `false`, battery 100%/status 5, 25,921,806,336 free bytes. Final prelaunch check: lease held by N8D5G, keyguard `false`, battery 100%/status 5, 25,920,737,280 free bytes. |
| Install and installed inputs | One `adb install -r`: `Success`. Installed APK `8c101c48…66a0`, ELF `1b49d05c…7bc`, ISO `3c2f8eb1…ebf5`: each matched its pin on two device SHA reads. `mc0` empty. Packaged runner and Turnip each matched their pins on two APK reads. |
| Launch PID, elapsed time, final progress tick and stop reason | One launch, PID `6908`; 115.103 s; last progress log tick 2020; stopped at first complete tile receipt and frontend dump at tick 2050. One BACK key after 6 s. |
| Alignment and control | Tick 2050, FBP 112, PMODE `ff21`, 512×448; control `128 expected=128 PASS`. |
| Sampled and raw summaries | Sampled `tiles=896 occupied=6045 active=34`; raw `tiles=896 occupied=6045 active=34`. Each continued logcat vector has 896 words, sum 6045, and 34 entries meeting the probe's `>=32` active threshold. Exact equality: 896/896. Both little-endian u32 packed vectors have SHA-256 `789afcc6579d1260a90797451f8cc649c6beed1da167a9c454e8349fb4973743`. |
| Frontend PNG and metadata | Sequence 0, tick 2050, 512×448, display/source FBP 112/112, fallback 0, `fnv1a=bd15b9c0`, PMODE `0xff21`. PNG SHA `94c6e8aa9c705849c477d50633eb850cb5185130b0060d7c00c0b061253388f3` (23,644 bytes); metadata SHA `ca9e81bd99a414b4294d8aa64b1eff9406c7924203f1597a731acf38b2ab9691` (120 bytes). Each matched on two device and two local reads. Orchestrator visual inspection pending. |
| Environment | `PS2X_GS_BACKEND=parallel`, Turnip, dev movie bypass, installed ISO, I26-FAST vsync pad route, N8D5 tile capture, frame dump only at tick 2050, progress log. Full file [ps2x.env](ps2x.env), SHA `e2f7eeb78bf98d154dd569d6681740f3889caeb5dd31f2be4f0c0021b5caeacb` matched on device. |
| Force-stop, PID gone and lease release | Force-stop completed; PID absent; lease `LEASE_FREE N8D5G done`. |
| First failed brief step | None. |
| Handoff category | `A` under the preregistered numeric/metadata gate; no causal verdict. |

N8D5E is the launcher and route source; N8D5F is the package source. This file records thresholds and pins before any launch. The orchestrator owns the frame view and gate decision.

## Preparation receipt

`launch.py` parses as Python. Its diff from N8D5E is limited to the N8D5G run ID, scratch and frame paths, N8D5F APK path, and APK/runner SHA pins. The route, environment, timing caps, same-PID log handling, frame pull, force-stop, and lease cleanup are unchanged. Two consecutive `shasum -a 256` reads matched for the script and local APK. No Odin preflight, install, or launch was performed.

## Execution and bounded receipts

The orchestrator released script SHA `b17b948b18cebc7f8d142668d49f0163cf36048a472937f7462c70b5bed889f6`. Two new `shasum -a 256 local/research/N8D5G/launch.py` reads matched before execution. Command from repo root:

```text
python3 -u local/research/N8D5G/launch.py --released-sha b17b948b18cebc7f8d142668d49f0163cf36048a472937f7462c70b5bed889f6
```

The one-run scratch directory is `/Users/brad/dev/ssx3-work/N8D5G/`. It holds the closed full `logcat-all.txt.gz` (5,207 bytes, SHA-256 `c8711e3ad700f3ba5d018b012b693a868f1447d38089c6c006d54a3c3c211d12`), `driver.log`, and same-PID `logcat-pid.txt`. The bounded committed evidence is [tile-excerpt.txt](tile-excerpt.txt), [result.json](result.json), [upload-0.png](upload-0.png), and [upload-0.txt](upload-0.txt). The PNG file header independently reports 512×448 RGBA. The full log remains in scratch as its single compressed copy.
