# N8D7H orchestrator gate — Android selected-input diagnostic package

Verdict: **PASS for source and package isolation only.** The APK is ready for one bounded Odin selected-input/circuit/GPU-stage run. No device behavior, GS cause or speed result follows from this build.

I read the full report, prepare/build/source/package gate scripts and JSON receipts, verified worker commit `9bdcfe44` scope and `Orchestrated-By: opencode` trailer, and reran the corrected Mac APK/member gate on the retained artifact. It passed: APK 153,736,732 bytes, WSL/Mac double SHA `86fca856b6de0148aea24fb53b63119e4ec1382eb9cf3490d2ce0db2031df14a`. The archive contains exactly the arm64 runner, unchanged Turnip and HAL shim; runner SHA `8e32841d8a6fff8f45862ca806c74ed92ec31469638f71281f9139e2fc32c683`, Build ID `1c1bce61bfe6bc21cd2ac86d473da323f480eb7b`. Required capture/stage strings are present; the sole arm64 CMake cache points to N8D7H G43 and external codegen, with five diagnostic/UI flags OFF.

The pre-overlay diff was empty. The postbuild source gate has exactly one fork backend and three G43 files changed from N8D6B, with jniLibs identical and double source SHAs matching N8D7F. One arm64 release build succeeded in 5m17s (48 tasks), with no compile repair. WSL root 7,590,835,753 bytes is under 10 GiB; Mac APK copy 147 MiB and global internal use 141.3/200 GB are within caps. The private fork's runner-dir guard is empty. No APK, native binary, game data or generated code was committed.

During review I found the worker's first Mac size assertion used a missing JSON key with a self-value fallback. The worker changed it to require `wsl['apk_size']` and reran the gate on the same transferred APK; I independently reran that corrected gate. No build or transfer rerun was needed.

Next: one lease-held Odin install/launch to tick 2050, requiring same-frame selected input, circuit1 and GPU stage rows, stage/tile controls and a viewed same-run PNG. Compare **within that Odin frame only**; the Mac and Odin GS streams are not assumed byte-identical. Apply the fixed comma-led tile-vector parser before release, then force-stop the app and release the lease after the run.
