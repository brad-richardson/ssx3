# N8D2 — same-run settled-race host upload and Odin screen

Brief: `local/muse/prompts/N8D2.md`. Worker: Codex. One no-build Odin race capture after I27A's Simulator run and cleanup. The orchestrator owns the image-stage verdict; this report records the image pair without a cause verdict.

## Pins and method

The N8D1 APK at `/Users/brad/dev/ssx3-work/N8D1/app-release.apk` was read twice on the Mac before use: SHA-256 `ece8b84ce3bce6bb85e42e21c432f6a6123ccae6e61dd91293e9da696fc63ae2` both times. [pins.json](pins.json) records the N8D1 package receipt and full pins. Its packaged arm64 runner SHA is `75ff0e4d78f1c317401c63e314d5786a25119b0223b0886c1baf6d7c01ed364e` (Build ID `dad1994cdf0f7c2854b1d2ffb8eecd374d4062c7`); Turnip member SHA `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`; shim member SHA `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`. The five diagnostic CMake flags in the N8D1 arm64 receipt are `OFF`. There was no new build or fork edit.

The N8D1 [launcher](launch.py) was copied into fresh `~/dev/ssx3-work/N8D2/` and adapted to use the original APK, a fresh `n8d2-frames` directory, and `PS2X_FRAME_DUMP_ONCE_TICKS=1840,1950,2050`. [ps2x.env](ps2x.env) otherwise matches N8D1: parallel backend, bundled Turnip, dev movie bypass, I26-FAST vsync pad route and empty card. The script waits for a same-PID `[frame:dump]` at race tick ≥2050, requests one screencap in that polling iteration, stops the app, and pulls up to three host PNG/text pairs. The host upload's metadata tick and the periodic guest-vsync log tick are reported separately.

Exact run command: `python3 -u /Users/brad/dev/ssx3-work/N8D2/launch.py` from `/Users/brad/dev/ssx3`. The script contains the exact `adb -s 622c49b1` commands for preflight, lease, install, SHA reads, env push, launch, screenshot, pair pulls, force-stop and cleanup. Local verification command: `python3 local/research/N8D2/accept.py` from the repo root. No second install or launch.

## One Odin run

Preflight found device connected, lease free, keyguard `showing=false`, battery 100% and full/charging (status 5). Lease `N8D2 one-launch` was claimed. Install returned `Success`; two device SHA reads each matched the installed APK pin above, stock ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`, and ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`. `mc0` and the new dump directory were empty. Prelaunch keyguard, battery and owned lease passed again. [driver.log](driver.log) and [result.json](result.json) record the order and all SHA pairs.

The one NativeActivity PID was `23698`. The bounded [same-PID log](logcat-pid.txt) records paraLLEl initialization and host dumps at ticks 1840, 1950 and 2050. The script sent BACK for the USB dialog. The tick-2050 dump triggered the screencap at 113.842 s after launch; the screencap pull and SHA checks completed at 114.187 s. The latest periodic guest-vsync log available at capture was tick 2029; it lags the tick-2050 dump and does **not** date the exact screen frame. The screenshot was requested in the same polling iteration that detected the dump. The app was force-stopped before host-pair pulls, PID was absent, and the lease read back `LEASE_FREE N8D2 done`. Launch-to-exit was 115.8 s, within the 180 s route and 240 s hard caps.

## Image table

All four PNGs were decoded and viewed. Host uploads are 512×448 with `fallback=0`, `displayFbp=sourceFbp=112`; the screencap is 1920×1080. Each PNG and each host text sidecar has two matching device SHA reads and two matching local reads in [result.json](result.json).

| Host upload tick and image | Nearby screen image | Visible regions | Timing gap |
| --- | --- | --- | --- |
| seq 0, tick 1840, [upload-0.png](upload-0.png) ([metadata](upload-0.txt)); SHA `7b50e6481776641b409e92fea3009d58070b2fcef8dfe6f43812419c88b635c4` | No screen capture at this tick | Mostly black; small pale fragments along the upper edge and left middle. | Earlier host sample, 210 ticks before the screen-triggering upload. |
| seq 1, tick 1950, [upload-1.png](upload-1.png) ([metadata](upload-1.txt)); SHA `a5cdea6bc83eabf831bcaa50409dbeac926960047e808c36c22365c2aa9d10ab` | No screen capture at this tick | Mostly black; partial top HUD (`0:0`), a right-side dollar glyph and sparse pale blocks. | Earlier host sample, 100 ticks before the screen-triggering upload. |
| seq 2, tick 2050, [upload-latest.png](upload-latest.png) ([metadata](upload-latest.txt)); SHA `06aad5b79731b6c972443d132616120ebabc595a3005ac5b102968504b78f1ba` | [race.png](race.png); SHA `d0691572782e775b951b0b36e75b48959f121c76d74a9d62fa50eb6aa0ac3e88` | Both images are mostly black with partial top HUD, a pale blue/white rectangular region toward the right, and isolated lower pale fragments. The screen also shows fine horizontal stripes and larger stepped blocks. The scene is fragmented in both views. | Screen request at 113.842 s, completed at 114.187 s, after the tick-2050 dump trigger at about 113.8 s. Exact screen guest tick is unobserved; latest periodic vsync log was tick 2029. |

The host and screen are nearby in one run, with recognizable matching HUD and fragment locations, but they are not a proven same-frame pair. The receipt does not identify an exact Vulkan driver/API version or provide a clean speed measurement.

## Acceptance and bounds

[accept.py](accept.py) checks the APK/package and device SHA pairs, exactly one install/launch, ≤3 host pairs, metadata ticks, full PNG decodes and dimensions, same PID, screen timing, env, force-stop/PID/lease cleanup, and limits. [accept.log](accept.log): `N8D2 acceptance PASS`. Mac work scratch was 348 KiB; report directory 324 KiB; four PNGs total 242,145 bytes, below the 12 MiB image cap. Logs were below 16 MiB. No device action followed cleanup.
