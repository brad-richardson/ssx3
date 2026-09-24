# N8D7D orchestrator gate — 2026-09-24

**FAIL_COMPILE_CAP; no fixture measurement.** Worker commit `b4f30c4`
contains the five allowed source/receipt files, has `Orchestrated-By: Codex`,
and passes `git show --check`. The entire `REPORT.md`, `result.json`, both
compile logs, and fixture source were read. The first command used relative
G43 include paths from the ssx3 root and failed to locate `gs/gs_util.hpp`.
The one allowed retry ran from the pinned G43 checkout but stopped at
`Granite/vulkan/vulkan_headers.hpp:33`, `volk.h` not found. The checkout has
the header at `Granite/third_party/volk/volk.h`; the compile command lacked
`-IGranite/third_party/volk`. Both failures are tooling setup, not evidence
for any pixel/GS alternative. `result.json` correctly marks every case and
golden-address check unrun/null. No executable, game build, boot, device
action, Mac calibration, or GS-cause verdict.

The fixture source contains twelve declared cases, including PSMCT32,
PSMCT16/S, FBP/FBW, phase stride one/two and VRAM wrap. It writes source
VRAM through `swizzle_PS2`, builds expected pixels from coordinate formulas,
and checks literal boundary offsets. Shared address code remains a limit of
any eventual PASS. Next: a narrow resume brief with the exact volk include
path, one compile and one execution, no source changes unless a single
named compile issue requires one correction. Gate every resulting case and
alias report before considering Mac replay integration.
