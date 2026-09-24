# X16 report

## Receipts

- Excerpt: `local/research/X15/excerpt.txt`
- Excerpt SHA-256: `eac602143522d2ec2fe3c6b062070ee822c32a5fecd258400a9e66a1a102c146`
- Elapsed: approximately 4 minutes; wall cap was 5 minutes.
- Visible context: not exposed by the CLI.
- Commands: `shasum -a 256 local/research/X15/excerpt.txt`; `date -u +%Y-%m-%dT%H:%M:%SZ`; `git status --short && git log --oneline -10`.
- LSP: one `goToDefinition` request at `/Users/brad/dev/ssx3-work/N8D5L/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:255`, character 51, on `vsync`; result: `No results found for goToDefinition`.

## Table

| field | value | evidence |
|---|---|---|
| EN1 | 1 | `gs_registers.hpp:564`; `upload-0.txt:1` |
| EN2 | 0 | `gs_registers.hpp:565`; `upload-0.txt:1` |
| INT | 1 | `gs_registers.hpp:731`; `gs_renderer.cpp:4384`; `upload-0.txt:1` |
| FFMD | 0 | `gs_registers.hpp:732`; `gs_interface.cpp:5530`; `upload-0.txt:1` |
| force_progressive | unknown | `ps2_gs_parallel_backend.cpp:248`; `gs_interface.cpp:5529`; `gs_interface.cpp:5533`; `gs_renderer.cpp:4383` |
| is_interlaced | unknown | `gs_renderer.cpp:4383`; `gs_renderer.cpp:4384`; `gs_renderer.cpp:4385`; `gs_renderer.cpp:4386`; `gs_renderer.cpp:4388`; `upload-0.txt:1` |
| raw_circuit_early_return | unknown | `gs_renderer.cpp:4939`; `gs_renderer.cpp:4940`; `gs_renderer.cpp:4941`; `gs_renderer.cpp:4942`; `gs_renderer.cpp:4943`; `upload-0.txt:1` |
| deinterlace_branch | unknown | `gs_renderer.cpp:5237`; `gs_renderer.cpp:5239`; `gs_renderer.cpp:4425`; `gs_renderer.cpp:4426`; `upload-0.txt:1` |

## Gaps

- The excerpt omits the middle of `GSInterface::vsync` between `gs_interface.cpp:5539` and `gs_interface.cpp:5575`; it does not establish the final `force_progressive` value or all `VSyncInfo` state.
- `is_interlaced` therefore depends on an unresolved `force_progressive` input at `gs_renderer.cpp:4383-4388`.
- The raw-circuit branch also depends on fields and state not established by the excerpt, including `raw_circuit_scanout`, CRTC offsets, overscan, external-write state, and circuit availability at `gs_renderer.cpp:4939-4965`.
- The deinterlace branch depends on unresolved `high_resolution_scanout`, `skip_deinterlace`, and the unresolved `is_interlaced` value at `gs_renderer.cpp:4425-4428` and `gs_renderer.cpp:5237-5239`.
