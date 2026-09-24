# N8D7G orchestrator gate — pinned Mac OFF/ON replay

Verdict: **PASS for Mac same-stream calibration**. This is a diagnostic replay, with no Odin or GS-cause verdict and no speed measurement.

I read the whole worker report and bounded excerpt, verified worker commit `5baf7f9` contains three named text receipts with `Orchestrated-By: opencode`, checked the exact private fork at `0678dd9`, the runner-dir guard from the N8D7F gate, and independently rehashed the binary, N8D4 stream, codegen, both logs, both hash files and both frame PPMs. The one mini lease is free. OFF/ON each exited 0 in about six seconds, with no cap or pipeline error. Full logs and PPMs remain private under `~/dev/ssx3-work/N8D7F/`.

The worker's saved result passed 24/24 checks after an orchestrator parser correction; the first checker invocation failed on the literal field name `packed_sha256`, and no replay was rerun. I then extended the same checker to verify both 896-word sampled/raw vectors and their summary arithmetic in each saved log. It now passes **34/34** checks on the same runs.

| Same-stream observable | OFF | ON |
| --- | --- | --- |
| Alignment | tick 2050, FBP112, PMODE `ff21`, 512×448 | same |
| Selected source | silent (flag OFF) | PSM1/FBW8, DBX/DBY0, phase0/stride2, 4 MiB mask, samples1, promoted0, 512×224 valid, status2 |
| circuit1 / merged GPU stage | each 448 tiles, 64,374 occupied, 300 active, control128 | same |
| Host input / circuit / GPU stage | unrun | all 448/448 exact, each 64,374 occupied and 300 active; packed SHA `e1dc4c5c…78a593` |
| Final sampled/raw | 896/896 exact, 128,292 occupied, 567 active, control128 | same |
| Present hash | `7bf5c012` | `7bf5c012` |
| Tick-2050 frame | 512×448 PPM SHA `8c85489e…a25d4d` | byte-identical |

I converted the ON PPM to PNG for inspection and viewed the 512×448 race frame: HUD timer at 00:00:05 and 1% progress, snowy slope and a small rider visible, much of the lower image dark. The OFF frame has the identical SHA. This agrees with the known Mac reference; it does not establish what happened on the Odin's different stream. The host decoder and GPU shader also share `swizzle_PS2`, so agreement is not an independent proof of the address algorithm.

Next: prepare a default-OFF Android diagnostic package from the gated source and private G43 patch, verify packaged native member/source pins and runner guard, then one same-Odin-frame selected-input/circuit1 capture under device lease. Stop on promoted input, count≠1, copy/map/metadata error or failed control; do not interpret cross-device image differences as same-stream divergence.
