# N8D7J — selected-input raw-VRAM discriminator (source audit)

**State: read-only source audit complete. No run proposed: the pinned code has
no Android-available raw-byte observable, so the A/B discriminator cannot be
measured under the <6 MiB / one-run rules without a source hook. Exact missing
hook stated in §5. No source edit, build, boot, device, web, upstream or push.**

## 1. Pins and scope

| Item | Pin |
| --- | --- |
| Private fork | `~/dev/ssx3-work/N8D7F/PS2Recomp` HEAD `0678dd96e496a65bbb09af5467f17240ae2bbdc8` |
| Fork file | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` blob `203bb72d23af613b11c095d0d41b498860d5d2e3` |
| Private G43 | `~/dev/ssx3-work/N8D7F/parallel-gs` HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` + dirty |
| G43 dirty files | `gs_renderer.cpp` `1812a3e57c365a5b435674c91ba97927cc87dec9`, `gs_renderer.hpp` `247d5ef1b1290ba9906458ed50d2d6a49f10b128`, `gs_interface.hpp` `acd9612284db72cb79175fc95fb240a0fa08fb71` |
| Inputs | N8D7I `REPORT.md`/`ORCH-GATE.md`, N8D7G `ORCH-GATE.md`, N8D7F `REPORT.md` + patches, G43 `REPORT.md`, todo item N8D7J |

The G43 tree is dirty by design (the G43 hunk + N8D5/N8D7F diagnostics); the
fork commit carries the N8D7F backend probe. Lines below are from these exact
trees. Mac and Odin ran different GS streams, so no byte-identical comparison
is made.

## 2. Data path (confirmed by read + LSP definition/references)

The selected capture is requested in the fork at
`ps2_gs_parallel_backend.cpp:372-378` when `PS2X_N8D7F_SELECTED_CAPTURE=1` and
`request.vsyncTick == 2050`, and it forces the N8D5 tile path on
(`tileRequested = selectedRequested || …`, line 375). `Present()` then calls
`m_iface->flush()` and `m_iface->vsync(vsync)` (384-385).

Inside `GSRenderer::vsync` (G43 `gs_renderer.cpp:4396`):

1. **Raw snapshot.** At 4806-4820, before circuit1 is drawn, the full 4 MiB
   `buffers.gpu` is copied into `selected_vram_staging`
   (`cmd.copy_buffer(..., *buffers.gpu, 0, 4u*1024u*1024u)`, 4816). Barriers:
   `COMPUTE_SHADER|TRANSFER_WRITE -> TRANSFER_READ` (4813-4815) then
   `TRANSFER_READ -> FRAGMENT_SHADER_READ` (4818-4819). This is the **earliest
   host-visible raw VRAM bytes** once mapped. The barrier set does **not**
   include `COLOR_ATTACHMENT_OUTPUT`; the snapshot is whatever `buffers.gpu`
   holds at that instant.
2. **GPU circuit1.** `sample_crtc_circuit` (4834, body 4262-4318) draws the
   512×224 `circuit1` image with `sample_quad` reading `buffers.gpu`
   (4282). The shader `shaders/sample_circuit.frag:108-115` computes
   `coord = pixel*(1,phase_stride) + (dbx, dby+phase)` and
   `addr = swizzle_PS2(coord.x, coord.y, fbp*PGS_BLOCKS_PER_PAGE, fbw, PSM, VRAM_MASK)`.
   Push constants are set at 4307-4313 from the same `dispfb`/`rect` values
   recorded into the result at 4779-4792.
3. **circuit1 readback.** On the merged path (not the raw-circuit early return
   at 4990-5031), 5054-5077 copies `circuit1` into `circuit1_staging`
   (458752 B), with `FRAGMENT_SHADER_READ -> TRANSFER_READ` then
   `TRANSFER_WRITE -> HOST_READ`.
4. **Completion.** `vsync` ends with `flush_submit(0)` (5354); the backend
   builds its own cmd, `m_device->submit(cmd); m_device->wait_idle();`
   (533-534), then maps. Host visibility is gated on `wait_idle`.

Back in the fork (535-599): `map_host_buffer` of `selected_vram_staging`
(553), `circuit1_staging` (555) and `stages[0].counts` (557). `selectedDecode`
(98-128) reads the raw 4 MiB through `vram_readback<PSM>` (110-125,
`gs_util.hpp:50-110`), which computes `effective_y=(y+src_y)&2047`,
`effective_x=(x+src_x)&2047`, `addr=swizzle_PS2(...)` (gs_util.hpp:66), and
indexes the raw buffer at `addr` (word/halfword). `base =
shot.selected_fbp * PGS_BLOCKS_PER_PAGE` (103) — the **same** base and the
**same** `swizzle_PS2` the GPU shader uses.

## 3. What N8D7I's "input" count actually measures

`input` is the output of `selectedDecode` (CPU raw-VRAM read at the swizzled
addresses + PSM expansion) fed to `selectedTileCounts`
(`ps2_gs_parallel_backend.cpp:62-79`, called at 570): a 16×16 tile census with
`max(r,g,b) >= 32`. `circuit` (571) is the same census applied to the CPU copy
of the **GPU-produced** circuit1 image. `stage` (572-578) is the GPU tile
shader (`n8d5_tile.comp`) census of that same GPU circuit1 image. So the three
N8D7I vectors are: CPU-decode-of-raw, CPU-census-of-GPU-image, GPU-census-of-
GPU-image. The equality `input==circuit==stage` at 448/448 therefore does not
separate raw-byte sparsity from address/decode loss: `input` and `circuit`
depend on the same `buffers.gpu` bytes and the same `swizzle_PS2`/base
(gs_util.hpp:66 vs sample_circuit.frag:115), exactly the N8D7G caveat that the
host decoder and GPU shader share `swizzle_PS2`. The only raw-VRAM output is
`vram_sha256` (579-580), and `selectedSha256` returns `"unavailable"` off
Apple (`ps2_gs_parallel_backend.cpp:45-60`, line 57) — so on the Odin there is
**no** raw-byte observation at all.

## 4. Source map

See [source-map.tsv](source-map.tsv) — 12 rows, columns
`stage, file_line, object_bytes, producer_consumer, clock_or_order,
observable, limit`.

## 5. The discriminator, preregistered A/B/OTHER

**One same-Odin-run observation that separates (A) from (B):** an
**address-independent raw-word occupancy tally of the selected FBP page
window** in the already-mapped 4 MiB `selected_vram_staging` — count non-zero
32-bit words in the contiguous byte window the selected display can occupy
(`base = selected_fbp * PGS_PAGE_ALIGNMENT_BYTES = 8192`,
`span ≈ max(fbw*PGS_BUFFER_WIDTH_SCALE, 512) * 224 * 4` for PSMCT24),
computed by a linear scan of raw bytes that never calls `swizzle_PS2`.
Swizzle permutes only within a page, so the touched page set is fixed by
FBP/FBW, not by the address algorithm. Reported together with the existing
`input` census, this is the only observation that does not inherit the shared
`swizzle_PS2` circularity: high raw-window occupancy with a sparse `input` is
(B); near-zero raw-window occupancy with a sparse `input` is (A).

| Category | Raw-window evidence | Existing `input` | Decision |
| --- | --- | --- | --- |
| A sparse raw | non-zero word count below predeclared floor (near zero) | active ≤100 | raw VRAM already sparse |
| B conversion loss | non-zero word count substantially above floor | active ≤100 | bytes present, decode/address/PSM loses them |
| OTHER | intermediate tally, or any of: `promoted≠0`, `samples≠1`, `status≠2`, `psm` outside supported set, `fbp≠112`, `pmode≠ff21`, map/decode error, missing tally line, control≠128 | any | not interpretable |

- **Byte cap:** existing capture is 4 MiB + 458752 circuit + 458752 decoded +
  65536 counts = 5,177,344 B < 6 MiB (N8D7F). A scalar tally adds no buffer.
- **Null / positive control:** run the same linear tally over a VRAM region
  known to hold data (a texture/command page) and require it high; the
  Mac N8D4 OFF/ON replay (frame known populated, N8D7G) is the positive
  control that the FBP window tally rises when the frame is present. The
  existing 16×16 checkerboard `control=128` remains the census-path control.
- **One-run stop:** stop at the first aligned tick2050 receipt; stop on any
  OTHER row above; no second run.

**But the pinned code cannot emit this.** The raw 4 MiB is mapped on Android
(553) yet the only consumer that reports raw bytes is the Apple-only SHA
(45-60, 579-580); there is no raw census and no linear-window scan. Under the
brief's rule ("if the current code cannot expose an independent raw-byte
observation under these caps, stop"), **no run is proposed**. The exact
missing hook: a `#if defined(__ANDROID__)`-safe raw-word census of
`shot.selected_vram_staging` (plus the FBP-window tally and, for the exact
test below, a correct-address comparison) emitted as text next to the
`[n8d7f] bytes=` line at `ps2_gs_parallel_backend.cpp:579-583`. That is a
source edit, out of scope here.

## 6. Safe exact pixel test and its shared-code limitation

A raw byte tally is not a decoded-pixel census. The existing synthetic fixture
is `ps2xTest/src/ps2_gs_tests.cpp:282-356`: `referenceAddrPSMCT32` (hand-coded
block/column tables) with `writeReferenceFramePSMCT32Pixel` /
`readReferenceFramePSMCT32Pixel`, which write a sentinel pixel at a known
(x,y) and read it back at an independently-coded address. The safe test is to
place a unique sentinel at a known (x,y) in the selected frame buffer and
require the selected decode to return that exact sentinel; a black result then
means a wrong address/PSM (B), not sparse content.

**Limitation:** the fixture's reference address is a hand-derived copy of the
same GS swizzle family, and it lives in the CPU `GS` backend tests — not the
parallel-GS `swizzle_PS2`/`vram_readback` path used by the selected capture —
and it covers only PSMCT32 with FBW=10, whereas the selected input is
`psm=1` (PSMCT24). Passing it validates self-consistency, not the parallel
path's address algorithm; it cannot break the shared-code circularity.

## 7. Gaps

No device, build, replay or measurement was performed. Category labels (A/B)
are preregistered, not observed. The `input`/`circuit` equality in N8D7I is
explained by shared `swizzle_PS2`; whether Odin's raw `buffers.gpu` is
genuinely sparse is unresolved and needs the §5 hook. The recommended next
observable is the Android raw-word/FBP-window tally from `selected_vram_staging`.
