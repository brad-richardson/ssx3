# N8D4 preparation receipt

Status: **preparation only**. I27B Xcode compile is active. No Odin install or launch, Mac build, replay, fork edit, or APK build occurred. The scripts require `--released-after-i27b` and are for a fresh continuation pane after the orchestrator's gate.

| Gate | Result / pin |
| --- | --- |
| N8D3 APK | `/Users/brad/dev/ssx3-work/N8D3/app-release.apk`; two local SHA-256 reads match `3970011d360b86a3f93f170df11e5964e2b467f01e7351c2cd1610b615b885be` |
| Packaged capture code | Arm64 runner contains `PS2X_GS_CAPTURE_STOP_TICK`, `PS2XGSC1`, and `PS2X_N8D3_RAW_CAPTURE`; runner, Turnip and shim members match the N8D3 pins in `accept.py --prepared` |
| Current fork pin | `fork/ssx3` local tracking and `git ls-remote fork refs/heads/ssx3` both `ddaee780288adb076ce40050d87969b20bc4bb05`; local `ssx3` checkout is older (`eac6cba`) |
| Mac dependencies | Canonical `codegen-ssx3/register_functions.cpp`, G43 paraLLEl source, and Homebrew Vulkan loader exist; SHA/build pins unrun |
| Preparation check | `python3 local/research/N8D4/accept.py --prepared`: pass for script syntax, APK SHA pair, required members and packaged capture strings |

## Explicit unrun table

| Stage | Status | Tick / FBP / PMODE | SHA / size | Visual regions |
| --- | --- | --- | --- | --- |
| Odin install, launch and lease | **Unrun** | Not found | Not found | Not viewed |
| Odin GS stream | **Unrun** | Last marker not found | Not found | — |
| Odin raw/backend/frontend images | **Unrun** | Not found | Not found | Not viewed |
| Mac configure/build and suite | **Unrun** | — | Binary not found | — |
| Mac CPU replay | **Unrun** | Not found | Not found | Not viewed |
| Mac paraLLEl replay | **Unrun** | Not found | Not found | Not viewed |
| Device cleanup, byte caps, acceptance | **Unrun** | — | Not found | — |

## Source path verified

`~/dev/ssx3-work/N8B1/PS2Recomp/ps2xRuntime/src/lib/gs/gs_stream_capture.cpp` reads `PS2X_GS_CAPTURE`, writes `PS2XGSC1`, and at `vblank()` writes and flushes a type-4 marker before closing at `PS2X_GS_CAPTURE_STOP_TICK`. `EeScheduler.cpp:2676` calls it at the VBlank stream position; `ps2_runtime.cpp:920` closes any still-open stream on teardown. The capture has a 6 GiB source cap; `launch.py` enforces the stricter brief cap of 4 GiB. The N8D3 APK contains this capture code. [N8D3](../N8D3/REPORT.md) established its tick-2050 raw/backend/frontend stage path and FBP 112.

The current fork's `ps2xTest/src/ps2_gs_replay_tests.cpp` `PS2GSReplay` reads the length-prefixed stream, rejects partial records, selects CPU by default or paraLLEl with `PS2X_GS_REPLAY_BACKEND=parallel`, and writes a named-tick PPM, frame metadata and replay counts. [GB4](../GB4/REPORT.md) Part 6 supplies the replay flags and worktree-root test invocation. [GB6C](../GB6C/REPORT.md) records the parallel fold and canonical codegen. Mac replay cannot alone separate Turnip rasterization from its transfer/readback.

## Prepared continuation commands

After explicit release, from `/Users/brad/dev/ssx3`:

```text
python3 -u local/research/N8D4/launch.py --released-after-i27b
python3 local/research/N8D4/accept.py --capture
python3 -u local/research/N8D4/replay.py --released-after-i27b
python3 local/research/N8D4/accept.py --final
```

`launch.py` adapts N8D3's one-install/one-launch route: same APK, stock ELF/ISO pins, empty card, parallel/Turnip, dev movie bypass, I26-FAST and tick-2050 raw/frontend path. It adds `PS2X_GS_CAPTURE=<app-files>/n8d4.gs` and `PS2X_GS_CAPTURE_STOP_TICK=2050`, requires the frame and close marker, checks keyguard, charging battery, 10 GiB free space, 4 GiB capture, and 300 s wall cap, always force-stops after a run, checks PID absent, double-reads the capture SHA on device and pulls it once while holding the lease. Capture and raw binaries stay under `~/dev/ssx3-work/N8D4/`, outside git.

`replay.py` gates on the device receipt and complete capture, checks the remote fork pin, archives it to N8D4 scratch, uses canonical codegen and `PS2X_GS_SHADOW_PARALLEL=ON`, allows one build and one replay per backend from the extracted fork root, and requests only tick 2050. It checks `disk_budget.sh` around large writes and caps scratch at 12 GiB. `accept.py` parses the full capture through EOF and checks the last marker, SHA pairs, replay counts, FBP/PMODE alignment, image decodes, cleanup and log/image caps. A missing marker, different page metadata or timing gap leaves the split unresolved. No capture/replay speed claim is planned.
