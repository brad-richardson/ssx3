# N8D7D2 orchestrator host fixture gate — 2026-09-24

**PASS for the synthetic single-sample CPU adapter; no Mac/Odin or GS-cause
verdict.** After N8D7D's compile-cap stop, the orchestrator resumed the
already committed fixture `local/research/N8D7D/fixture.cpp` (SHA-256
`8c9a5d7fa209be2f3f1b6def631b5b4ab8dc9c2c437b94e19ba84567f050cf08`)
against pinned G43 source HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`.
The needed includes were `Granite/third_party/volk` and
`Granite/third_party/khronos/vulkan-headers/include`. One compile with only
the first of those failed at `vulkan/vk_platform.h`; the next compile with
both succeeded. The exact successful command, run from G43 root, was:

```text
c++ -std=c++17 -O2 -I. -Igs -IGranite/math -IGranite/vulkan -IGranite/util -IGranite/third_party -IGranite/third_party/volk -IGranite/third_party/khronos/vulkan-headers/include /Users/brad/dev/ssx3/local/research/N8D7D/fixture.cpp -o /tmp/n8d7d2-fixture
```

Compiled binary SHA-256 `745f658e5dbf2bb8bb909741f08b3cd059b2737a9f62e8a66f956ff0459c9b75`.
One execution wrote `result.json` and `run.txt` here. Independently parsed
the JSON and checked all **12 cases**: zero pixel mismatches across each
512×224 output, zero mismatches across each 448-tile vector, 458,752 output
bytes, zero aliases/conflicting writes, matching expected/actual output and
tile hashes. Literal FBP112 offset 917,504 and FBP511/DBX64 wrap offset 0
both matched. The executable was removed after verification. The emitted
`result.json` embeds the worker's older compile command without the two new
include flags; the successful command above is authoritative.

This fixture writes VRAM through the same `swizzle_PS2` implementation used
by the host reader. It validates the adapter's coordinate and payload path
and two literal address boundaries, but its full-pixel agreement does not
independently prove every swizzle address. It uses synthetic VRAM only and
does not establish which source N8D6C selected or why circuit1 was sparse.
Next: Mac same-stream calibration with an ordered copy of the selected input
and an independent host circuit1 census, after logging promotion and sample
count. Keep the N8D6C formal category OTHER.
