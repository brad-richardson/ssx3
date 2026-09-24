# N8D5E — one Odin tile-path discrimination run

## Fixed handoff thresholds

| Category | Required first aligned live receipt at tick 2050 |
| --- | --- |
| A | FBP 112, PMODE `ff21`, 512×448; control `128 expected=128 PASS`; both summaries have 896 tiles; sampled active ≤100 and raw active ≤100; tick-2050 frontend PNG and metadata. |
| B | Same alignment, control, summary size and frontend requirements; sampled active ≥500 and raw active ≤100. |
| OTHER | Every other observation, including a missing frontend PNG. No causal verdict. |

**Handoff category: OTHER.** The aligned probe satisfies A's numeric thresholds, but the frontend PNG was not produced. The orchestrator cannot gate A or view the frame from this run. The script reached its first failed brief step, **tick 2100 without a complete receipt**, and stopped under the one-run policy. No second install or launch occurred.

## Run evidence

| Field | Observation |
| --- | --- |
| Main gate | `cc529a7`, N8D5D package PASS as released by orchestrator. |
| Exact command | `python3 -u local/research/N8D5E/launch.py --released-sha ed836a7fab7a9e6bbe375eac722ba645b111f4da50c172e4c3da355cadc857dd` from repo cwd. |
| Script SHA | `ed836a7fab7a9e6bbe375eac722ba645b111f4da50c172e4c3da355cadc857dd`, checked twice before run; script unchanged. |
| Launch / install counts | 1 / 1. Install returned `Success`. |
| APK | `/Users/brad/dev/ssx3-work/N8D5D/app-release.apk`; local ×2 and installed base.apk ×2 match `a6a0c3793e31310fc8794e7a0d6b6cc282e5060d59cfe116b919236b9f50612a`. |
| Packaged runner | SHA ×2 `6a93af327b3cb1c5ebd9b3b81dc68ae1eb5e259633c9c61b78a82ba06428d162`; N8D5D Build ID `ab1bdc3b61faf1fe99cd5844e8c90ffaee8f54f6` (package receipt, not re-read here). |
| Packaged Turnip | SHA ×2 `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`. |
| Installed ELF / ISO | Two device SHA reads each matched `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` / `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`. `mc0` empty. |
| Preflight | Device `622c49b1` online; lease initially `LEASE_FREE N8D4 done`; keyguard `false`, battery 100%, status 5 (full), free bytes 25,924,812,800. Final prelaunch check again keyguard `false`, battery 100%, status 5; free bytes 25,923,309,568. |
| Environment | `PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`, `PS2X_SKIP_MOVIE=1`, installed ISO, I26-FAST route, `PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_N8D5_TILE_CAPTURE=1`, `PS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999`, `PS2X_VSYNC_RATE_LOG=1`; env SHA `ea1177d796862bd3042c1162bb72ae4808c710978184e3321012e09a637fd57e`. |
| Frame dir | `/storage/emulated/0/Android/data/com.ps2x.runner/files/n8d5e-frames-1790250692`, unique and empty before launch. |
| Launch | PID 30780; BACK sent once after 6 s; 120.84 s elapsed; final logged tick 2110. |
| Alignment | Same PID: tick 2050, FBP 112, PMODE `ff21`, 512×448. |
| Control | `control=128 expected=128 PASS`. |
| Sampled summary | 896 tiles; occupied 15,669; active 79. |
| Raw summary | 896 tiles; occupied 15,669; active 79. |
| Frontend dump event | `seq=0 tick=2050 size=512x448 fbp=112/112 fallback=0 fnv1a=3ff212d`. |
| Frontend metadata | `upload-0.txt` exists, 119 bytes: `seq=0 tick=2050 size=512x448 displayFbp=112 sourceFbp=112 preferred=0 fallback=0 fnv1a=3ff212d smode2=0x1 pmode=0xff21`. Device SHA ×2 and local SHA ×2 match `7fba4645c95f7aa9c221e11239d24063afbefa503936d0d6d281c9535b5d2239`. |
| Frontend PNG | `upload-0.png` and `upload-latest.png` absent in the recorded dir after run. Same-PID raylib log says `Failed to open file` and `Failed to export image` for both PNG paths. No PNG SHA or viewed appearance. |
| Why `frame_ready` stayed false | It requires tick-2050 metadata **and** `upload-0.png`. The metadata exists after the run, but the PNG was absent; the log records failed PNG export. Its availability during each poll was not recorded, but missing PNG alone keeps the function false. |
| Cleanup | Script force-stopped app, verified PID absent, released lease as `LEASE_FREE N8D5E done`; read-only postrun check again found no PID and the lease free. |
| First failed brief step | Tick 2100 reached without complete receipt. Script exited 1 after cleanup. |
| Handoff category | **OTHER**; A/B both require a frontend PNG. No causal verdict. |

## Bounded receipts

Committed: [launch.py](launch.py), [result.json](result.json), [driver.log](driver.log), [logcat-selected.txt](logcat-selected.txt), and [upload-0.txt](upload-0.txt). The selected log has nine lines from the same PID: alignment, control, summaries, PNG export warnings, and frame-dump event. The full same-PID log is `/Users/brad/dev/ssx3-work/N8D5E/logcat-pid.txt` (25,352 bytes, SHA `b60f33053b55c6a278e0d810fe2463c77736fe5fa62451880fffc66aa492818f`). The closed full log is compressed at `/Users/brad/dev/ssx3-work/N8D5E/logcat-all.txt.gz` (5,518 compressed / 47,462 uncompressed bytes, SHA `588d6e22dd78f2d783e3ec115ac1ad01f321895dd444716a140f10c08517973b`). Both are below the 16 MiB cap. No GS stream, Mac replay, speed claim, device relaunch, or push was made.
