# N8D7E — selected-input + circuit1 Mac capture design (read-only Part 1)

## Pins

- G43 `parallel-gs` `/Users/brad/dev/ssx3-work/G43/parallel-gs` HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`, dirty: `M CMakeLists.txt`, `m Granite`, `M gs/gs_interface.cpp`, `M gs/gs_renderer.cpp`, `M gs/gs_renderer.hpp`, `M tools/CMakeLists.txt`, `M tools/gs_dump_replayer.cpp` (verified `git rev-parse HEAD` + `git status --short` this session). Cited line numbers are these working-tree files.
- N8D6A backend `/Users/brad/dev/ssx3-work/N8D6A/PS2Recomp` HEAD `81682dfb5fa05e6737e12e40531f63bc65dfd6cf` (per N8D7C report; `git log --oneline -3` top entry `81682df [N8D6A]` confirmed this session). Read only `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` for stage tap/flags.
- Prior receipts: `local/research/N8D7B/{REPORT.md,ORCH-GATE.md}`, `local/research/N8D7C/{REPORT.md,ORCH-GATE.md,adapter.tsv}`, `local/research/N8D7D2/ORCH-GATE.md`.
- Ledger: G37 row (`docs/numbers-ledger.md:353`): G30/G31 mis-sampling interpretation WITHDRAWN; G38 row (`:356`): first matched-boundary divergence at seq1, Mac-B updated vs Odin-B at load. Neither is N8D6C cause proof (N8D7B gate; N8D7D2 gate).
- N8D6C frame: tick2050/FBP112/PMODE `ff21`, circuit1 21/448, formal OTHER after logcat-continuation parse miss. N8D6A pinned Mac same-stream replay: circuit1 300/448. Streams not byte-identical.
- No build, boot, replay, device, push, or source edit performed. LSP not invoked (orchestrator budget stop after context nudge); connections confirmed by exact call sites/text reads. `source-map.tsv` written first in this directory.

## Commands run

From `/Users/brad/dev/ssx3`: `cat` of brief, N8D7B/N8D7C reports+gate, N8D7D2 gate, N8D7C `adapter.tsv`. `git -C /Users/brad/dev/ssx3-work/G43/parallel-gs rev-parse HEAD` + `status --short`. `git -C /Users/brad/dev/ssx3-work/N8D6A/PS2Recomp log --oneline -3`. Targeted `rg`/`read` only in the eight named G43 paths plus the N8D6A backend file. `mkdir -p local/research/N8D7E`. No broad tree scans after the budget nudge. `Granite/vulkan/device.hpp` not read (copy/map signatures confirmed in `command_buffer.hpp` + call sites; device.hpp not needed).

## Source map (summary; full rows in source-map.tsv)

| Step | Anchor | Finding |
| --- | --- | --- |
| priv_snapshot | `ps2_gs_parallel_backend.cpp:247-258`, `:654-680` | `syncPriv` copies dispfb1/display1 before `flush`+`vsync` |
| promotion_selection | `gs_interface.cpp:5540-5552`; `gs_renderer.cpp:4455-4458` | FBP lookup gated on EN1/EN2; layer-count rejection; selected = promoted image or `buffers.gpu` |
| gpu_vram_barrier | `gs_renderer.cpp:1614-1617`; `:4997-5003`; `:5017-5018` | Ordered barrier pattern exists (G40 probe); no dedicated pre-sample VRAM barrier in vsync path (narrow gap) |
| input_copy | `gs_renderer.cpp:1619-1634`; `command_buffer.hpp:364-365` | Ordered `buffers.gpu`→staging `copy_buffer` demonstrated by G40; no selected-input copy in vsync path (not found as integrated site) |
| sample_quad | `gs_renderer.cpp:4278-4282`, `:4292-4313`; `sample_circuit.frag:98-115` | `sample_quad[promoted ? 1 : 0]`; VRAM mode binds `buffers.gpu`; FBP*32 base, raw FBW page stride, DBX/DBY+phase+stride*row |
| circuit1_store | `gs_renderer.cpp:4784-4786`; `:4953-4961` | Per-field create+draw, `Circuit1` name; raw-c1 fast path may move it to `result.image` |
| circuit1_readback | `command_buffer.hpp:380-383`; `gs_renderer.cpp:1649-1659` | API + G40 image-copy pattern exist; no circuit1 readback site in pinned G43 (not found as integrated path) |
| host_decode_census | `gs_util.hpp:50-66`; `sample_circuit.frag:56-70`; backend `:420-430` | `vram_readback<PSM>` + shader-accurate expand + tile rule; N8D7D2 12-case pass shares `swizzle_PS2` (stated limit) |
| mac_replay_entry | backend `:247-258`, `:296-300` | Same `Present` entry; N8D6A gate env+tick+geometry+pmode; new-probe flag absent; Mac calibration unrun |

## API support statement (precise)

- Ordered GPU VRAM slice copy: YES, callable path exists. `GSRenderer::g40_record_probes` (`gs_renderer.cpp:1614-1634`) issues a compute/transfer-write → transfer-read `barrier` then `cmd.copy_buffer(staging, 0, *buffers.gpu, page_base, page_len)` into a `CachedHost` `TRANSFER_DST` buffer. `copy_buffer` signature at `Granite/vulkan/command_buffer.hpp:364-365`. What is missing is only a vsync-path call site capturing the *selected* rectangle slice (G40 copies B pages 112..223).
- Independent circuit1 image-to-host copy: API YES, integrated path NO. `copy_image_to_buffer` overloads at `command_buffer.hpp:380-383`; G40 tex probe (`gs_renderer.cpp:1649-1659`) shows layout transition + copy + restore pattern. No circuit1 staging copy exists in the pinned G43 vsync path, and pinned `ScanoutResult` (`gs_renderer.hpp:23-53`) retains no `circuit1` handle (retention `shot.circuit1` lives only in the N8D6A fork-local extension, backend `:290-293`). A Part 2 probe must add both the handle retention (or in-vsync copy) and the copy site; no new callable needs inventing.
- `map_vram_read` (`gs_interface.cpp:5126-5150`) maps `buffers.cpu` after a tracked host-read timeline wait. On non-UMA it is NOT the selected GPU input (`gs_renderer.cpp:385-397`: `cpu` aliases `gpu` only on UMA). It must not substitute for the ordered `buffers.gpu` copy.

## Same-frame V/S/T predictions (one aligned tick2050/FBP112/PMODE ff21 frame, stage tap sparse)

Grid: matched 512x224 field, 16x16 tiles, occupied pixel `max(R,G,B)>=32`, active tile `>=32` hits (backend `:420-430`); 448 counts. "Broad" ~= N8D6A Mac-replay magnitude (~300/448); "sparse" ~= N8D6C Odin magnitude (~21/448). Raw-byte occupancy or FNV alone cannot discriminate (swizzle/PSM/DBX/DBY/phase decide sampled pixels, `sample_circuit.frag:98-123`).

| Alternative | Selected-input host census | Independent circuit1 host census | Existing tap | Separating check |
| --- | --- | --- | --- | --- |
| V input sparse/circuit sparse | sparse at shader-selected addresses | sparse | sparse | Requires promotion-state log: if promoted1 selected, VRAM census is inapplicable; inspect promoted image instead |
| S input broad/circuit sparse | broad/correct | sparse | sparse | Input-vs-circuit split separates S from V; bounds to sample/draw/visibility path, isolates no single op |
| T input broad/circuit broad, tap sparse | broad/correct | broad | sparse | Circuit-image readback separates T from S; checkerboard control=128 (backend `:302-340`) covers a different image path, not circuit census |

## One candidate capture placement (design only)

Gate: default-OFF `PS2X_N8D7E_SELECTED_CAPTURE=1`, single aligned tick2050/FBP112/PMODE `ff21` Mac replay frame, `SUPER_SAMPLES==1`, non-promoted-or-captured-promoted only.

1. In `GSRenderer::vsync` (direct cmd, `gs_renderer.cpp:4403-4405` region), after pending work is submitted (same ordering as `flush_submit`, `:5276`) and BEFORE `sample_crtc_circuit` draws circuit1 (`:4784-4785`): record final selection — `promoted1` pointer null/nonnull + layers/format/dims (cf. `:4455-4456`, interface `:5593-5597` pattern) and the exact push/specialization values (`:4292-4313`).
2. VRAM mode: issue the G40-style barrier (`:1614-1617`) then `copy_buffer` of the minimal page set covering the selected rectangle's swizzled addresses into a `CachedHost` staging buffer (same `copy_buffer` API, `command_buffer.hpp:364-365`). Promoted mode: `copy_image_to_buffer` the selected promoted layer-0 extent instead (`command_buffer.hpp:381-383`, pattern `:1649-1659`). No draw-order change: transfer-only copies + barriers before the circuit draw.
3. After the circuit1 draw and its ATTACHMENT→READ_ONLY barrier (`:4997-5003`), issue an independent `copy_image_to_buffer` of `circuit1` valid extent (`rect.valid_extent`, `:4773-4775`) to a second staging buffer, then continue vsync unchanged (merge/blit consume the image as today).
4. After submit+wait, map both staging buffers host-side, hash bytes, run the N8D7C adapter (`vram_readback` per-row at `src_y=DBY+phase+row*stride` for stride 2, `gs_util.hpp:50-66`) into a 512x224 RGBA field, expand payloads per shader (`sample_circuit.frag:56-70`), and count tiles with the backend rule (`>=32` px of `max(R,G,B)>=32` per tile). Also host-count the circuit1 staging copy with the same tile rule (independent of the N8D5 tile shader).

Metadata per capture (all required or stop): tick, FBP/FBW/PSM/DBX/DBY, phase/stride, `rect.valid_extent` vs `image_extent`, super_samples, promotion pointer/layers/format, vram mask, slice byte ranges, both staging SHAs, decoded-field SHA, 448+448 tile vectors, control=128 receipt, copy/map error flags.

Byte cap (<6 MiB): 4 MiB VRAM slice max + 458,752 B circuit1 RGBA + 458,752 B decoded field + 64 KiB metadata/tile vectors = 5,046,272 B < 6 MiB. Circuit1 at other-than-512x224 valid extent aborts (cap math assumes 512x224x4).

## Script acceptance table (one pinned Mac same-stream replay)

| # | Check | Pass criterion |
| --- | --- | --- |
| 1 | alignment | tick 2050, FBP112, pmode `ff21`, 512x448 final (backend `:296-300`) else stop/mismatch |
| 2 | selection identity | logged promoted pointer/layers + push/specialization equal the draw's values (`:4278-4313`) |
| 3 | input bytes | staging copy complete, SHA recorded, page range covers selected rectangle |
| 4 | decode | 512x224 RGBA, 458,752 B, field SHA recorded; stride-2 uses 224 height-1 calls |
| 5 | circuit bytes | independent circuit1 staging SHA + 448 host tile counts recorded |
| 6 | consistency | input census vs circuit census vs existing tap all present; classify only per V/S/T table |
| 7 | control | checkerboard control == 128 (backend `:302-340` pattern) |
| 8 | caps | total bytes < 6 MiB; flag default OFF verified (unset env = zero new work) |

## Stop branches (any → OTHER, no cause inferred)

Promotion surviving layer check without promoted-image capture; `SUPER_SAMPLES!=1` (and `==2` has no shader output branch, `sample_circuit.frag:119-147`); unsupported PSM/geometry/phase/stride/mask; any coordinate reaching 2048 on the helper path (`gs_util.hpp:59-66` masks to 11 bits while the shader passes coords unmasked); copy/map/calibration failure; tick/FBP/PMODE/geometry/source/frame hash misalignment; Mac calibration mismatch (decoder vs circuit vs tap inconsistent on the same stream). G37-withdrawn VRAM-misread reading and G38 earlier-boundary divergence stay context only.

## Recommended Part 2 brief

Implement (default-OFF `PS2X_N8D7E_SELECTED_CAPTURE`) in the G43 checkout: (a) retain-or-copy circuit1 in vsync + ordered selected-input slice copy per placement above; (b) N8D7C count-1 adapter with per-row stride-2 calls + shader-accurate 16-bit expansion; (c) run the N8D7D2 synthetic fixture verbatim, then one pinned Mac same-stream replay acceptance table; gate any Odin same-frame run on all-green Mac calibration. Budgets: one probe hunk, one Mac replay, no Odin run in Part 2. No V/S/T verdict follows from this design.

## Gaps

No N8D6C per-frame promotion state, selected-input bytes, shader specialization/rect metadata, decoded pixels, or independent circuit1 host census in allowed receipts. Mac calibration unrun. `device.hpp` unread (not needed). No cause concluded.
