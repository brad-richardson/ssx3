# N8D4 — one Odin GS capture and same-stream Mac replays

The I27B Simulator run was released before this continuation. Preparation is in commit `7eb1514`; this continuation used its unmodified `launch.py`, `replay.py`, and `accept.py`. There was one Odin install/launch, one Mac build, one CPU replay, and one paraLLEl replay. Both acceptance gates passed. No source, APK, or generated guest code changed.

The preparation source read verified `gs_stream_capture.cpp` writes `PS2XGSC1`, emits the type-4 VBlank marker and closes at `PS2X_GS_CAPTURE_STOP_TICK`; `EeScheduler.cpp` calls it at VBlank. The pinned APK runner contains that capture code and the N8D3 raw-stage path. Current fork `ps2_gs_replay_tests.cpp` parses the length-prefixed stream and selects paraLLEl only with `PS2X_GS_REPLAY_BACKEND=parallel`.

## Gate table

| Stage | Measured result | Receipt |
| --- | --- | --- |
| Odin preflight | Lease `LEASE_FREE N8D3 done`; keyguard `showing=false`; battery 100%, full; initial free space 27,015,606,272 bytes | [device-result.json](device-result.json), [driver.log](driver.log) |
| Inputs | APK SHA-256 `3970011d360b86a3f93f170df11e5964e2b467f01e7351c2cd1610b615b885be`, ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`, ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`; each had two matching reads, APK locally and installed | [device-result.json](device-result.json) |
| One Odin run | Parallel/Turnip, empty card, I26-FAST, dev movie bypass. Frame dump `seq=0 tick=2050`, capture stop marker 2050. Route elapsed 114.332 s; launch-to-exit including transfer 157.0 s. App force-stopped, PID absent, lease `LEASE_FREE N8D4 done` | [driver.log](driver.log), [logcat-pid.txt](logcat-pid.txt) |
| Odin stream | `PS2XGSC1`, 1,100,725,180 bytes, SHA-256 `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d`; two matching device and two Mac reads. Complete EOF at marker 2050. 862,993 packets, 11,499 priv records, 25,485 transfers, 2,050 markers; zero readbacks and clears | `accept.py --capture`, [device-result.json](device-result.json) |
| Odin frame | 512×448, `displayFbp=112 sourceFbp=112 preferred=0`, `pmode=0xff21`. Raw mapped and backend packed RGBA are byte-identical across 917,504 bytes; decoded frontend PNG also matches. | [odin-raw-2050.png](odin-raw-2050.png), [odin-frontend-2050.png](odin-frontend-2050.png), [device-result.json](device-result.json) |
| Mac pin/build | Fork `ddaee780288adb076ce40050d87969b20bc4bb05`; canonical codegen register SHA-256 `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` twice; `PS2X_GS_SHADOW_PARALLEL=ON`; `ps2x_tests` SHA-256 `58e521833878633778ff8176c670a0bf667f679537ab31d6a4c07dc9c27847a7` twice | [replay-result.json](replay-result.json) |
| CPU replay | Suite 585 passed, 0 failed. 862,993 packets, 11,499 priv, 25,485 transfers, 2,050 markers, 41 samples. Tick-2050 `pmode=ff21 dispfb1=9070 dispfb2=1400 display_fbp=112 source_fbp=112`, present `a1834096` | [cpu.log](cpu.log), [cpu.hashes](cpu.hashes), [mac-cpu-2050.png](mac-cpu-2050.png) |
| Mac paraLLEl replay | Suite 585 passed, 0 failed, same stream counts and 41 samples. Tick-2050 page/PMODE match CPU; present `7bf5c012`. Backend: 862,993 packets, 41 presents, zero null scanouts/unsupported clears/VRAM I/O, one successful init | [parallel.log.gz](parallel.log.gz), [parallel.hashes](parallel.hashes), [mac-parallel-2050.png](mac-parallel-2050.png) |
| Caps and cleanup | Capture 1.10 GB / 4 GiB; scratch 2,595,438,310 bytes / 12 GiB; text logs 5,039,650 bytes / 16 MiB; scratch images 1,699,288 bytes / 12 MiB; internal workstreams 127.1/200 GB after build. Device free space after capture 25,899,864,064 bytes, above 10 GiB. `accept.py --final` passed. | [replay-result.json](replay-result.json), [gate-lines.txt](gate-lines.txt) |

## Viewed tick-2050 regions

| Region | Odin raw/frontend | Mac CPU | Mac paraLLEl |
| --- | --- | --- | --- |
| Upper HUD/timer | Only a small cyan corner shape remains; timer and position are absent | Position `2nd/2`, timer `00:00:05` readable | Same position/timer readable; thinner glyph strokes differ |
| Course/snow/rider | Large black rectangles and narrow snow fragments; rider and slope not recognizable | Snow slope, valley, rider position, dark center/lower course recognizable | Same broad scene and dark center/lower course; snow texture and thin edges differ |
| Left course arrow and music card | Mostly absent | Arrow and `EA RADIO BIG` card visible | Arrow and card visible, with small glyph differences |
| Right meter/course map | Small disconnected fragments | Ball and vertical meter visible | Ball and vertical meter visible, with edge differences |

I viewed the Odin raw and frontend PNGs, both frontend `upload-0`/`upload-latest` copies (same SHA), and both Mac replay frames. The raw, packed, and frontend byte equality belongs to the Odin path; the Mac images are the two replays of its single GS stream. The CPU and paraLLEl images both retain a large dark lower region, so that region is part of the viewed replay comparison. A Mac replay does not split Turnip rasterization from its transfer/readback path. No capture or replay timing is reported as a clean speed number.

## Exact continuation commands and retained inputs

From `/Users/brad/dev/ssx3`, in this order:

```text
python3 -u local/research/N8D4/launch.py --released-after-i27b
python3 local/research/N8D4/accept.py --capture
python3 -u local/research/N8D4/replay.py --released-after-i27b
python3 local/research/N8D4/accept.py --final
```

The launcher installed the pinned N8D3 APK, sent the I26-FAST vsync pad script and added `PS2X_GS_CAPTURE=/storage/emulated/0/Android/data/com.ps2x.runner/files/n8d4.gs` and `PS2X_GS_CAPTURE_STOP_TICK=2050`. `replay.py` archived fork `ssx3` at the pin above into `~/dev/ssx3-work/N8D4/PS2Recomp`, configured Release/Ninja with canonical `PS2X_GAME_CODEGEN_DIR`, G43 `PS2X_PARALLEL_GS_SOURCE_DIR`, and `PS2X_GS_SHADOW_PARALLEL=ON`, then built `ps2x_tests` once. From that extracted fork root it ran the test binary once per backend with `PS2X_GS_REPLAY_CAPTURE=~/dev/ssx3-work/N8D4/n8d4.gs`, `PS2X_GS_REPLAY_PPM_TICKS=2050`, `PS2X_GS_REPLAY_STEP=50`, separate PPM/hash outputs, and `PS2X_GS_REPLAY_BACKEND=parallel` plus `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib` only for GPU. Exact argv, elapsed times, and SHA pairs are in [replay-result.json](replay-result.json); the committed scripts contain the complete environment and route.

The 1.10 GB capture, extracted fork source, build binary, raw/packed RGBA, and PPMs remain outside git in `~/dev/ssx3-work/N8D4/`. The APK remains in N8D3 scratch; ELF and ISO inputs remain on the Odin. The committed N8D4 directory contains only bounded text receipts and four small review PNGs. The script's periodic guest log last showed tick 2024 before the frame and marker at 2050; the frame metadata and closing marker agree on tick 2050. No second run was made.
