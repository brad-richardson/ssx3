# N8D1 — Odin menu image-stage probe

Brief: `local/muse/prompts/N8D1.md`. Worker: Codex. One diagnostic source candidate, one successful arm64 build, one Odin install and launch. The orchestrator owns the renderer verdict. The observed images provide a **timing-limited partial split**: host uploads change markedly across ticks 781–840, while the later tick-861 screencap is readable with fine horizontal lines. These are different frames, so this run does not establish a stable same-frame GL/backend separation or a renderer cause.

## Pins, source, and candidate

| Item | Value and receipt |
| --- | --- |
| N8B1 source | `17e90ded3689685ad359b76a9168c80a1f752e2d`; `ps2_runtime.cpp` SHA-256 `68aa9c2ac559033b726b81948867a2ed1be581e30825291ef7b88241fd7d9f87` twice; [local-pins.txt](local-pins.txt). |
| N8C2 APK input | `86ee7b723979c6727f03aaeaa031e9bd6dd3481a640af3b1eb06fd41e6fc7640` twice before use; [local-pins.txt](local-pins.txt). |
| WSL inputs | Source tar `6d091b62c1152f1c68488b853c42654ccab1b57e39795feef09285778d42a6a6`, codegen register `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`, Turnip staged `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`, shim staged `d7add7e8e2e31f3c49b83941c6686fa66ab3d844c650e8d70c93b026f90cafa0`, wrapper `498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17`; each read twice before copy. Copied inputs rechecked; [input-hashes.json](input-hashes.json), [prepare.py](prepare.py), [prepare.log](prepare.log). |
| Guest files | Stock ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`; ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`; each read twice on Odin before launch in [result.json](result.json). |
| Isolated source | N8C2 source/package copied to `/home/brad/n8d1/`, excluding `.cxx`, `build`, `.gradle`; codegen and paraLLEl inputs stayed pinned under `/home/brad/n8b1/`. No fork source edit. |
| Candidate | Only the two `ExportImage(img, pngPath)` calls in `dumpPresentationFrame` became `ExportImageToMemory(img, ".png", &encodedSize)` + binary `std::ofstream` + `MemFree`, with at most three PNG error messages. Diff: [source.diff](source.diff). New source SHA-256 `358d726bf39e319b906e7e15407e1bf361cd2cdbdd8e79d4a96b25a9588c3f96` twice in [source-hashes.json](source-hashes.json). |

## Build and APK gate

`ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/n8d1/build.sh"'` from the mini, with the full Gradle command and property values in [build.sh](build.sh). `assembleRelease` succeeded in 5m 31s, 48 tasks; one build, no repair build. [build-tail.txt](build-tail.txt).

| APK gate | Result |
| --- | --- |
| APK SHA-256 | `ece8b84ce3bce6bb85e42e21c432f6a6123ccae6e61dd91293e9da696fc63ae2` twice in WSL, twice after copy to Mac; [apk-gate.json](apk-gate.json), [local-apk-hashes.txt](local-apk-hashes.txt). |
| Native members | Exactly `lib/arm64-v8a/libps2EntryRunner.so`, `libvulkan_freedreno.so`, `libhardware.so`; no x86. Each member hashed twice by [apk_gate.py](apk_gate.py). |
| Runner | Member SHA-256 `75ff0e4d78f1c317401c63e314d5786a25119b0223b0886c1baf6d7c01ed364e`; Build ID `dad1994cdf0f7c2854b1d2ffb8eecd374d4062c7`. |
| Turnip and shim | Package members match N8C2: Turnip `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`; shim `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`. |
| Flags | `PS2X_ENABLE_DIAG_TAPS`, `PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`, `PS2X_ENABLE_IOP_RPC_TRACE`, `PS2X_ENABLE_DEBUG_UI` all `OFF` in arm64 CMake cache. |

## One Odin menu launch

Exact commands and stops are in [launch.py](launch.py); same backend, bundled Turnip, movie bypass, I26-FAST vsync pad route as N8C2, with only `PS2X_FRAME_DUMP_DIR` and `PS2X_FRAME_DUMP_ONCE_TICKS=780,810,840` added in [ps2x.env](ps2x.env). Device `622c49b1`; preflight found lease free, keyguard `showing=false`, battery 100% status 5. Claimed lease, installed this APK (`Success`), then obtained two matching device SHA reads for installed `base.apk`, stock ELF, and ISO; memory card was empty and dump directory empty. Prelaunch preflight repeated. The one NativeActivity PID was `21022`. [driver.log](driver.log), [result.json](result.json).

Same-PID [logcat-pid.txt](logcat-pid.txt) records bundled Turnip HMI mapping, HAL open `rc=0`, `[gs:parallel] init ok`, `[frame:dump]` for seq 0/1/2 at ticks 781/810/840, and vsync progress through tick 861. BACK was sent for the USB dialog. The launch stopped at the first logged tick ≥850, 30.7 s after start, below the 180 s title and 240 s hard caps. No second launch. Force-stop left PID absent and lease `LEASE_FREE N8D1 done`. The third host pair was pulled read-only under a separate receipt lease after the launch, without launching the app, then the lease was released again; [pull_latest.py](pull_latest.py). No device action followed the orchestrator's instruction to stop device work.

| Stage image | Tick and dimensions | Viewed appearance | SHA-256 |
| --- | --- | --- | --- |
| [upload-0.png](upload-0.png) + [metadata](upload-0.txt) | seq 0, tick 781, 512×448, `fallback=0` | Recognizable blue mountain background. | `d728f45769cfba9b1b887f7375182fba42fa234e9e132e5f186442a1a3816a5f` |
| [upload-1.png](upload-1.png) + [metadata](upload-1.txt) | seq 1, tick 810, 512×448, `fallback=0` | Wide black horizontal blocks over the mountain scene. | `bcab25a0ec25b8d71356149786fddfa097722a7c85b5a973b477b446a9727658` |
| [upload-latest.png](upload-latest.png) + [metadata](upload-latest.txt) | seq 2, tick 840, 512×448, `fallback=0` | Broad black bands, fine stripes, and small menu fragments over the mountain. | `49e5f59927e6ccec66a0caead7f21a3b1bc697ccb0a0ae4cf89be32aff285dba` |
| [menu-tick861.png](menu-tick861.png) | logged tick 861, 1920×1080 screencap | Readable menu and mountain background with fine horizontal lines. Captured after the requested 809–850 range because the progress log advanced from 806 to 861. | `c599950ca832ea39e933358c6cb7b366f4cdc62dd8d4bb7d069290aee95939ad` |

Each host PNG and text sidecar has two matching device SHA reads and two matching local reads in [result.json](result.json). The screencap's device/local SHA pair also matches. All four PNGs decoded at the listed dimensions and had nonuniform content. [accept.py](accept.py) and [accept.log](accept.log) check declared files, hash pairs, same-PID log, cleanup, and full PNG decode; result: `N8D1 acceptance PASS`.

## Bounds and gaps

| Item | Status |
| --- | --- |
| Stage comparison | Partial and timing-limited. Upload tick 810/840 and screencap tick 861 show different scene states and artifact shapes. The probe did not capture a same-frame host/screen pair; no stable GL/backend or renderer-cause verdict. |
| Exact Vulkan identity | Unproved. Same-PID log names the bundled HMI path, while raylib logs OpenGL renderer `Adreno (TM) 830`; neither supplies Turnip Vulkan device/API/driver identity. |
| Budgets | One WSL build, one Odin install/launch; WSL scratch 6.8 GiB (<10 GiB), Mac APK/work scratch <1 GiB, committed images 711,374 bytes (<10 MiB), text logs <16 MiB. [wsl-disk.txt](wsl-disk.txt). No speed number from this diagnostic run. |
| Fork | No fold, fork edit, or push. |
