# X15B — same dense Qwen excerpt, short thinking budget

## Inputs

- Brief: `local/muse/prompts/X15B.md`
- Excerpt: `local/research/X15/excerpt.txt`, 11,013 bytes
- Excerpt SHA-256: `eac602143522d2ec2fe3c6b062070ee822c32a5fecd258400a9e66a1a102c146` (verified with `shasum -a 256`)
- Pinned register state: `pmode=0xff21 smode2=0x1` from `upload-0.txt:1` (seq=0 tick=2050)
- Pinned checkout for LSP: `/Users/brad/dev/ssx3-work/N8D5L/PS2Recomp` (file exists, 26,060 bytes)

## Commands

1. `shasum -a 256 local/research/X15/excerpt.txt` — matched brief's SHA.
2. `ls -la /Users/brad/dev/ssx3-work/N8D5L/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` — existence check for LSP target.
3. `mkdir -p local/research/X15B && date +%s` — 1790254419 (rows.tsv written immediately after; within the 60 s cap after the excerpt read).
4. One `lsp goToDefinition` on `vsync`, `ps2_gs_parallel_backend.cpp:255` character 50 (1-based, from the excerpt's indentation).
5. `date +%s` — 1790254561.

## Timing

- Elapsed ~2.5 min total; well under the five-minute wall cap.

## Visible context

Not exposed to this session (no usage telemetry available in the opencode worker pane). Context target was <18k: one brief (7 lines) + one excerpt (194 lines) + two tool outputs.

## LSP result

`goToDefinition` on `vsync` at `ps2_gs_parallel_backend.cpp:255,50` → **empty/error**: tool returned `No results found for goToDefinition`. Recorded verbatim; the brief permits recording an empty/error result. The exact target could not be confirmed without a second read (forbidden), so the negative is not attributed to a bad column vs. missing LSP server configuration.

## Table (rows.tsv, verbatim)

| field | value | evidence |
| --- | --- | --- |
| EN1 | 1 | gs_registers.hpp:564;upload-0.txt:1;gs_renderer.cpp:4690 |
| EN2 | 0 | gs_registers.hpp:565;upload-0.txt:1;gs_renderer.cpp:4691 |
| INT | 1 | gs_registers.hpp:731;upload-0.txt:1;gs_renderer.cpp:4384 |
| FFMD | 0 | gs_registers.hpp:732;upload-0.txt:1;gs_renderer.cpp:4385 |
| force_progressive | unknown | gs_interface.hpp:164;ps2_gs_parallel_backend.cpp:248;gs_interface.cpp:5529;gs_interface.cpp:5533;gs_interface.cpp:5535 |
| is_interlaced | unknown | gs_renderer.cpp:4383;gs_renderer.cpp:4384;gs_renderer.cpp:4385;gs_renderer.cpp:4386;gs_renderer.cpp:4387;gs_renderer.cpp:4388 |
| raw_circuit_early_return | 0 | gs_renderer.cpp:4692;gs_registers.hpp:567;gs_registers.hpp:574;gs_renderer.cpp:4939;gs_renderer.cpp:4940;gs_renderer.cpp:4941;gs_renderer.cpp:4942;gs_renderer.cpp:4953;gs_renderer.cpp:4954;gs_renderer.cpp:4960;gs_renderer.cpp:4965 |
| deinterlace_branch | unknown | gs_renderer.cpp:4427;gs_renderer.cpp:4428;gs_renderer.cpp:4692;gs_registers.hpp:567;gs_renderer.cpp:5237;gs_renderer.cpp:5239;gs_renderer.cpp:5245 |

## Derivation notes

- `pmode=0xff21` = `0b1111_1111_0010_0001`: EN1(bit0)=1, EN2(bit1)=0, CRTMD(bits2-4)=0b001, MMOD(bit5)=0, AMOD=0, SLBG(bit7)=0, ALP(bits8-15)=0xff.
- `smode2=0x1`: INT(bit0)=1, FFMD(bit1)=0.
- `force_progressive`: the pinned backend block (`ps2_gs_parallel_backend.cpp:243-255`) never sets it; the only mutation shown is the `has_complex_scanmsk_timeout` clear (`gs_interface.cpp:5533-5537`), whose set-site is outside the excerpt and whose current value is unknown. → `unknown` (not `0`: the excerpt shows no assignment at all).
- `is_interlaced` (`gs_renderer.cpp:4383-4388`): INT=1, FFMD=0 → `alternative_sampling` true; the result then depends on `force_progressive` (`if (alternative_sampling && force_progressive) is_interlaced = false;`). Gate unknown → `unknown`.
- `raw_circuit_early_return`: outer gate (`gs_renderer.cpp:4939-4942`) plus `is_raw_circuit1` requires `MMOD == PMODEBits::MMOD_ALPHA_ALP` (=1, `gs_registers.hpp:574`); pinned MMOD=0, so `is_raw_circuit1`=0. `is_raw_circuit2` requires `SLBG == SLBG_ALPHA_BLEND_CIRCUIT2` (=0, `gs_registers.hpp:573`) and `circuit2 && !circuit1`; with EN2=0 the circuit2 branch (`gs_renderer.cpp:4758`) does not create circuit2, so the else-if cannot fire. Both sub-branches dead on pinned registers → early return does not execute → `0` (independent of the unknown VSyncInfo fields, so the register-grounded `0` is reported rather than `unknown`).
- `deinterlace_branch` (`gs_renderer.cpp:5237-5255`): `force_deinterlace` = `!high_resolution_scanout && FFMD && INT && CMOD!=PROGRESSIVE` = 0 because FFMD=0. `should_deinterlace` = `!high_resolution_scanout && (is_interlaced || 0)`; `is_interlaced` unknown and `high_resolution_scanout`'s set-site is not in the excerpt → `unknown`. `skip_deinterlace` also not shown as set.

## Gaps

1. `VSyncInfo` field defaults: the excerpt contains the struct declaration (`gs_interface.hpp:155-164`, `180-197`) but no constructor/aggregate-init defaults, so `force_progressive`, `high_resolution_scanout`, `skip_deinterlace` initial values are unobservable.
2. `has_complex_scanmsk_timeout` set-sites (complex SCANMSK write path) are outside the excerpt; its value at tick 2050 is unknown.
3. `priv.smode1.CMOD` is never shown (only used inside `force_deinterlace`, which is already 0 via FFMD).
4. Whether `circuit1`/`circuit2` image objects exist at this call site depends on DISPFB/DISPCNT/DISSize state not present in the excerpt; moot for `raw_circuit_early_return` given MMOD=0/EN2=0, but noted.
5. LSP negative is unattributed (bad column vs. no C++ LSP server configured) because the brief forbids a second read of the real file.

## Compliance

- Wrote only `local/research/X15B/rows.tsv` and this `REPORT.md`.
- No OpenCode config edits, no source edits, no build/boot/device/web/push.
- One LSP call, one target file.
- No image-quality or driver-cause inference.
