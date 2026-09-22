# GB1 — Runtime ↔ GPU GS bridge design (read-only; no code landed)

## Pins (all reads in this doc)

| Tree | Rev | Note |
| --- | --- | --- |
| Fork `ssx3` | `3d4feed67b8d46cdf2d4f479aafb38ce24dbb6ab` | All `fork/ssx3` line numbers below |
| Fork `main` (upstream) | `14b1e5c` | `Start the main thread with COP0 Status.IE set (#214)` |
| Upstream `feature/iop-emulator` | `78ecbae377a758595049e146b79733bd609fe274` | Same SHA on `fork/` and `origin/` remotes |
| `parallel-gs-g7` clone | `3a66c19` + uncommitted G-lane hunks (`gs_interface.cpp`, `gs_renderer.cpp/.hpp`, `tools/`, `CMakeLists.txt`, `Granite` pointer) | G26/G28/G40/G41 stack; durable home decided 09-22 (`9bf42dd`): `brad-richardson/parallel-gs` + `brad-richardson/Granite` forks, fix-only commits on branch `ssx3` after G42 |
| `~/dev/ps2xGS` | `fd781ef` | `backend/` holds only a README stub; GPU work lives in the clone |

Prior reads: the integration review (`docs/research/review-2026-09-20-first-frame-and-gs.md`
§ "paraLLEl-GS: test adoption…", from ~line 239) and the greenfield GPU plan
(`docs/plan-gs-gpu-backend-2026-09-18.md`, stale on backend choice — the G lane
uses paraLLEl, not a new compute rasterizer).

## 1. Seam

### 1a. Where the runtime sees GIF packets, priv-reg writes, transfers, readbacks

All paths below are synchronous on the caller thread today (game thread for
everything except `UploadFrame`, which runs on the main thread).

**GIF packet producers → `PS2Memory::submitGifPacket` / `GifArbiter`**

| # | Producer | File:line @ `ssx3` | Path taken |
| --- | --- | --- | --- |
| P1 | GIF DMA engine (chain + normal mode) | `ps2xRuntime/src/lib/ps2_memory.cpp:1989` (`processGIFPacket(phys,qw)`), `:2015` (`processGIFPacket(data,size)`); dispatch `:1560-1588`, `:1700-1749`; completion `:1875-1906` | `submitGifPacket(Path3, …)` → arbiter → `GS::processGIFPacket` |
| P2 | VU1 `XGkick` (PATH1) | `ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:917-927` (`finishXgkick`) | `submitGifPacket(Path1, …)` (`:923`), or direct `GS::processGIFPacket` (`:925`) when no memory is bound |
| P3 | VIF1 → GIF image data | `ps2xRuntime/src/lib/ps2_memory.cpp:1873` (`m_pendingVif1Transfers` drain inside `processPendingTransfers`) | Via pending-transfer drain into the GIF path |
| P4 | HLE `sceGsExecLoadImage` | `ps2xRuntime/src/lib/Kernel/Stubs/GS.cpp:593-672` | Builds an A+D + IMAGE packet in guest RAM, kicks GIF DMA (`:665-668`) → P1 |
| P5 | HLE `sceGsExecStoreImage` setup | `ps2xRuntime/src/lib/Kernel/Stubs/GS.cpp:674-761` | Builds an A+D TRXDIR=1 packet, kicks GIF DMA (`:751-754`) → P1, then readback R1 |
| P6 | Native image-upload fast path | `ps2xRuntime/src/lib/ps2_memory.cpp:2023-2213` (`tryProcessNativeGifImageUploadChain`) | **Bypasses the arbiter**: `gs.uploadImageNative(…)` at `:2194` |
| P7 | Native packed-GIF fast path | `ps2xRuntime/src/lib/ps2_memory.cpp:2215-2290` (`tryProcessNativeGifPackedChain`) | **Bypasses the arbiter**: `gs.processNativePackedGIFPacket(…)` at `:2269` |

Central funnel: `submitGifPacket` (`ps2_memory.h:337`, impl
`ps2_memory.cpp:1964-1987`, default `drainImmediately=true`) with the PATH3
mask queue (`:1969-1978`, flushed at `:1937-1962`). The arbiter
(`ps2_gif_arbiter.h:23-44`, impl `ps2_gif_arbiter.cpp:21-63`) **copies every
packet** (`:30-31`), stable-sorts by path priority (`:40-52`), and drains
synchronously into `m_processFn`, which `PS2Runtime::syncCoreSubsystems`
(`ps2_runtime.cpp:735-767`, wiring at `:750-752`) binds to
`m_gs.processGIFPacket(data, size)`.

**Direct register writes (bypass GIF entirely)**

| # | Writer | File:line @ `ssx3` | Effect |
| --- | --- | --- | --- |
| W1 | HLE clear packet | `Kernel/Stubs/GS.cpp:110-123` | 6 × `writeRegister` (TESTA/PRIM/RGBAQ/XYZ2a/XYZ2b/TESTB) |
| W2 | `sceGsPutDrawEnv` + display-buffer switches | `Kernel/Stubs/GS.cpp:783-795`, `:1180-1181`, `:1191-1192`, `:1220-1224` via `Support.h:1893-1901` | 8 × `writeRegister` per env (FRAME/ZBUF/XYOFFSET/SCISSOR/PRMODECONT/COLCLAMP/DTHE/…) |
| W3 | A+D unpacking inside GIF decode | `gs_frontend.cpp:1059-1064` (packed `0x0E`), `:724-738` (REGLIST) | `writeRegisterUnlocked` per address |

**Privileged-register writes (PMODE/DISPFB/DISPLAY/…, CSR/IMR)**

| # | Writer | File:line @ `ssx3` | Effect |
| --- | --- | --- | --- |
| V1 | Guest EE MMIO stores | `ps2_memory.cpp:51-100` (`gsRegPtr`: PMODE `0x0000`, SMODE2 `0x0020`, DISPFB1 `0x0070`, DISPLAY1 `0x0080`, DISPFB2 `0x0090`, DISPLAY2 `0x00A0`, BGCOLOR `0x00E0`, IMR `0x1010`, BUSDIR `0x1040`, SIGLBLID `0x1080`); handlers `:769`/`:816`/`:978`/`:1037`/`:1192` | Direct struct stores into `GSRegisters` (`ps2_memory.h:191-213`) |
| V2 | Guest CSR stores | `ps2_memory.cpp:130-…` (`writeCsrHalf`; FIFO bits 15:14 forced EMPTY `0x4000`, SIGNAL/FINISH write-1-to-clear) | Atomic read-modify-write on `GSRegisters::csr` |
| V3 | HLE `applyGsDispEnv` | `Kernel/Stubs/Helpers/Support.h:1879-1891` | Direct `pmode/smode2/dispfb1/display1/dispfb2/display2/bgcolor` stores |
| V4 | GIF-stream A+D to `0x59-0x5F` | `gs_frontend.cpp:1514-1533` | `dispfb1/display1/dispfb2/display2/bgcolor` stores from stream order |
| V5 | SIGNAL / FINISH / LABEL | `gs_frontend.cpp:1478-1513` | `siglblid` merge + `csr.fetch_or(0x1/0x2)` |
| V6 | VBlank FIELD bit | `Kernel/EeScheduler.cpp:2598-2605` | `csr` bit 13 set/clear on odd/even ticks |

**Image transfers (host↔local) and readbacks**

| # | Direction | File:line @ `ssx3` | Notes |
| --- | --- | --- | --- |
| T1 | Host→local | `gs_frontend.cpp:739-746` (IMAGE tag) → `processImageData` `:1627-1631` → `BeginTransfer` (`:1397-1412` on TRXDIR) + `UploadImage` | Setup regs travel as A+D in the same packet (P4/P6 shape) |
| T2 | Local→local | Same entry; `GSCpuBackend::PerformLocalToLocalTransfer` (`gs_cpu_backend.cpp:1501`) | No host bytes cross |
| T3 | Local→host | TRXDIR=1 packet (P5) + `PerformLocalToHostTransfer` (`:1541`) | Bytes leave via R1 |
| R1 | `consumeLocalToHostBytes` | `GS.cpp:757` (only non-test caller) ← `GS::consumeLocalToHostBytes` (`gs_frontend.cpp:1646-1650`) ← `GSCpuBackend::ConsumeLocalToHostBytes` (`gs_cpu_backend.cpp:1611`) | Synchronous; EE blocks for the bytes |
| R2 | `ReadVram` / `WriteVram` | `GS::ReadVram/WriteVram` (`gs_frontend.cpp:1681-1692`); live caller: E4 census `ps2_e4.h:427` on the game thread at VBlank; rest are tests | Synchronous single-pixel access |
| R3 | `SnapshotVram` / `refreshDisplaySnapshot` | `GS::snapshotVRAM` (`:201-214`, `Sync(DebugReadback)+SnapshotVram`), `refreshDisplaySnapshot` (`:509-512`) | Debug-panel path |
| R4 | Presentation latch | `GS::latchHostPresentationFrame` (`:535-584`): `Flush` + `Sync(Presentation)` + `Present` (`:556-558`), request built at `:514-533` from priv regs + context frames + preferred-display heuristic | Runs on the **main** thread via `UploadFrame` (`ps2_runtime.cpp:507`) |
| R5 | Presentation copy+upload | `copyLatchedHostPresentationFrame` (`gs_frontend.cpp:586-647`, 640-px-stride → packed repack) → `s_uploadBuffer` pad → `UpdateTexture` (`ps2_runtime.cpp:524-597`), called each host frame at `:3234` | 3 CPU copies + 1 GL upload per display tick (see §3) |

Backend contract crossed today: `GSRasterBackend`
(`ps2xRuntime/include/runtime/gs/gs_backend.h:8-33`) — `Initialize/Reset`,
per-primitive `Submit(batch)` (`gs_types.h:252-257`: ≤3 vertices + full
`GSDrawState`), `BeginTransfer/UploadImage`, `Flush/TextureFlush/Sync(reason)`
(**documented no-ops on the CPU backend**,
`gs_cpu_backend.cpp:574-588`, with "GPU backends may … here" comments —
the interface already anticipates this design), `Present(request)→pixels`,
`ClearFramebuffer`, `ConsumeLocalToHostBytes`, `Read/Write/SnapshotVram`,
`GetTransferSnapshot`. `setRasterBackend` (`gs_frontend.cpp:1652-1679`) hands
off through the external 4 MiB allocation (`SnapshotVram` → memcpy); VRAM
bytes are otherwise backend-private — the only `m_gsVRAM` uses outside the
backend are alloc/free and null checks (`ps2_memory.cpp:268-398`, `:1332`,
`:2029`, `:2221`; handoff `ps2_runtime.cpp:738`).

### 1b. Proposed interface at the GIF/register boundary

Place the queue **above tag decode**, at the `submitGifPacket`/`GifArbiter`
boundary — not at `GSRasterBackend`. Rebuilding GIF traffic from decoded
`Submit` batches would lose packet order, A+D interleaving, Q/ADC sticky
state, TEXFLUSH/CLUT timing, and SIGNAL/FINISH positions; the review
(§ "paraLLEl-GS…", ~line 243) already recommends interception at the
GIF/register boundary with well-defined state ownership.

```
EE/game thread (producers, unchanged call sites)        GS thread (consumer)
───────────────────────────────────────────────        ─────────────────────
P1 GIF DMA ──┐
P2 VU1 XGkick ├─ submitGifPacket ──► GifArbiter ──enqueue──► ring ──► decode + backend
P3 VIF1 ─────┘   (drain→enqueue)      (copy+sort,            │
P4/P5 HLE ──► GIF DMA ─┘             unchanged)              │  CPU mode:  existing frontend
P6/P7 native fast paths ──► enqueue as raw packets ─────────┘  decode → GSRasterBackend
W1/W2 HLE reg writes ──► reg-write cmd ────────────────────►   paraLLEl mode: gif_transfer /
V1/V3/V4 priv writes ──► priv-write cmd (ordered) ─────────►   write_register / priv stores
V2/V5/V6 CSR ──► shared atomics (see below)                    / read_transfer_fifo / vsync
R1/R2/R3/R4 ──► synchronous RPC (EE/main waits) ◄──────────►  completion + bytes/pixels
```

**Queue protocol (in):** one command stream, in EE submission order:

| Command | Payload | Consumer action (CPU mode / paraLLEl mode) |
| --- | --- | --- |
| `gif_packet` | path id, bytes (copied at enqueue, as the arbiter does today) | `processGIFPacket` decode → backend calls / `gif_transfer(path, data, size)` |
| `reg_write` | addr, u64 value | `writeRegisterUnlocked` / `write_register(addr, value)` |
| `priv_write` | priv offset, u64 value | store to backend-visible priv struct / store to `PrivRegisterState` field |
| `upload_image_native` | 4 setup regs + bytes | `uploadImageNativeUnlocked` (keeps P6/P7 wins on the GS thread) |
| `present` | vsync tick + `VSyncInfo`-equivalent | `Present(request)` → pixels (CPU) / `flush()` + `vsync()` → `ImageHandle` (paraLLEl) |
| `reset` | — | `Flush/Sync(Reset)/Reset` |

**Sync/readback points (out):** `finish_fence` (drains: EE waits until all
prior commands are consumed, then CSR bit 1 is set in stream order),
`consume_fifo(n)` → bytes (T3/R1), `read_vram/write_vram` (R2),
`snapshot_vram` (R3), `present` completion (R4/R5), `reset` completion.
SIGNAL/LABEL need **no EE wait**: the GS thread applies the `siglblid` merge
and CSR bit 0 atomically in stream order (V5 moves verbatim). There is no
GS→INTC path today (scheduler raises only timers `9+timer` and VBlank
`2`/`3`, `EeScheduler.cpp:2477/2647/2653`; IMR is stored, never tested) —
when one is wanted, paraLLEl's `SignalInterface`
(`gs_interface.hpp:240-250`: `on_signal/on_finish/on_label`, true → implicit
`flush()`) is the hook, firing INTC per IMR from the GS thread.

**CSR/vsyncTick stay shared atomics**, as today: guest CSR polling
(`0x375d10`-style spins), the VBlank FIELD flip (V6), and `vsyncTick`
(`EeScheduler.cpp:2594-2596`, lock-free per the `static_assert` in
`ps2_memory.h:216`) never touch VRAM and must not pay a round-trip.
Upstream's new GIF_STAT FQC field (§4) reads queue occupancy the same way.

**The CPU backend sits behind the same interface as the reference
implementation.** Concretely: the GS thread links the *unmodified*
`GSCpuBackend`; "CPU mode" is the existing frontend decode
(`processGIFPacket`/`writeRegisterUnlocked`/`vertexKick`/transfer state
machine) moved to run on the GS thread, fed by the ring instead of direct
calls. Validation is then a same-inputs A/B: direct-call vs queued,
byte-exact on `SnapshotVram` + `Present` pixels + `consumeLocalToHostBytes`
(see §5 step (a)). No `GSRasterBackend` change is required for the queue
itself; upstream's one new backend method (`LoadClut`, §4) rides along as a
decode-internal call in CPU mode and is a no-op mapping in paraLLEl mode
(paraLLEl manages CLUT from the register stream).

Rejected alternative: queue *decoded* batches behind `GSRasterBackend`
(keep decode on EE, move only raster). It preserves CPU behavior but cannot
feed paraLLEl, whose inputs are GIF transfers + register writes
(`gif_transfer`, `gs_interface.hpp:266`; `write_register`, `:269`; priv regs
as a bulk struct, cf. `gs_dump_parser.cpp` `PrivRegisters` case; FIFO
readback via `read_transfer_fifo`, `:304`). Rebuilding that traffic from
`GSPrimitiveBatch` reintroduces exactly the ordering/state losses the brief
rules out.

## 2. Threading

### 2a. Threads today → threads after

| Thread | Today | After |
| --- | --- | --- |
| Game (EE scheduler, `ps2_runtime.cpp:3180-3196`) | Guest code, DMA/VIF/VU1, HLE stubs, **all GIF decode + all CPU raster**, VBlank events + FIELD flip + vsync callbacks | Producers only: enqueue packets/regs/priv-writes; waits only at §2c points |
| Main (raylib loop, `ps2_runtime.cpp:3198-3264`) | `UploadFrame` (`:3234`): latch + copies + `UpdateTexture` + quad | Presents the GS thread's output (pixels today, `ImageHandle` after §3); present RPC replaces the latch call |
| **GS (new)** | — | Owns decode + backend + VRAM + priv-visible regs; serves RPCs; like PCSX2's MTGS |

Existing locks that this design retires from the hot path: `m_stateMutex`
(recursive, every `GS::` entry), `m_backendLifetimeMutex` (latch/snapshot vs
`setRasterBackend`), `m_presentationMutex` (latch vs copy), and the CPU
backend's per-method `m_mutex` (`gs_cpu_backend.cpp`, 11 sites) — all become
GS-thread-local or go away; cross-thread traffic is the ring + RPC fences.

### 2b. Ownership

- **VRAM: GS thread exclusively.** Already true in practice (§1a, VRAM
  paragraph): no EE-side writer exists. The 4 MiB `m_gsVRAM` allocation stays
  as the CPU-mode backing store and the `setRasterBackend` hand-off format;
  in paraLLEl mode VRAM lives in its GPU buffer + `page_tracker` host
  timelines, with `map_vram_read/write` as the only CPU peepholes (diagnostic
  snapshots, `gs_dump_generator.cpp:193` pattern).
- **Frontend draw state** (PRIM/contexts/vertex queue/transfer regs,
  `gs_frontend.h:187-218`): moves to the GS thread with the decode.
- **Priv regs**: split. `pmode/smode2/dispfb*/display*/bgcolor` become
  GS-thread-owned, fed by ordered `priv_write` commands (V1/V3/V4 call sites
  enqueue *and* update an EE-side shadow so EE loads still read-after-write
  consistently); `csr/vsyncTick/imr/busdir/siglblid` stay shared
  (`csr`/`vsyncTick` already atomic; `siglblid` needs an atomic or a
  GS-thread-only writer with EE-side loads — V5's merge moves to the GS
  thread, guest MMIO loads of SIGLBLID read the last merged value).
- **GIF FIFO occupancy**: the ring depth itself; upstream GIF_STAT FQC (§4)
  derives from it.

### 2c. When the EE must wait

| Wait point | Trigger (call site today) | GS-thread service | HW analogue |
| --- | --- | --- | --- |
| Ring full | Any `submitGifPacket` with no space | Drain until space | GIF FIFO full stall |
| `FINISH` (0x61) | `gs_frontend.cpp:1491-1501` | Consume all prior commands, `Flush`+fence, set CSR bit 1, wake EE | FINISH event / path drain |
| Local→host consume | `GS.cpp:757` via R1 | Run transfer to completion, `read_transfer_fifo` (paraLLEl) or staged bytes (CPU), return count | FIFO drain to EE |
| `ReadVram`/`WriteVram` | E4 census `ps2_e4.h:427`, tests, debug | Execute at stream position, return value / ack | BUSDIR host access (serializing) |
| `SnapshotVram`/debug | R3 | Copy at stream position | Same |
| `present` | R4/R5 (main thread, per display tick) | `Present`→pixels (CPU) or `flush`+`vsync`→image (paraLLEl); see §3 for removing this from the critical path | VBlank scanout |
| `reset` | `GS::reset` (`:128-194`) | Quiesce, `Flush/Sync(Reset)/Reset`, ack | GS reset |
| **No wait** | packet/reg/priv submit (space available), SIGNAL/LABEL (ordered CSR update), vsync tick, guest CSR poll | — | FIFO-queued work |

PATH3 masking (`m_path3Masked` + fifo, `ps2_memory.cpp:1969-1978`) stays on
the EE side exactly as today — masked packets never reach the ring, so mask
semantics are unchanged.

### 2d. Ring sizing (measurement-gated)

No race-traffic measurement exists yet: T26's 402,432 GIF packets / 240 s
(~28 packets/vsync) and E3b's 403,224 kicks are park-state numbers, and G0's
~21–23 ms per 64×64 synthetic present is explicitly not a scene budget
(review § "Tighten the GS plan's evidence gates"). Size the ring from data,
not guesswork:

1. Pre-step measurement (no new code): run the E7 packet log
   (`ps2_e7::packet` at `ps2_memory.cpp:1749/1954/1971`, `gs-enter` at
   `gs_frontend.cpp:655`) over an E29-bypass title run when E31 lands; take
   P50/P99/max **bytes per vsync** and max single packet (hard ceiling: DMA
   QWC is 16-bit → 1 MiB per transfer).
2. Provisional ring until then: **1024 packet descriptors / 16 MiB byte
   payload, chunked at 256 KiB** — holds ≥4 vsyncs at any plausible title/menu
   rate while a single 1 MiB DMA packet can always fit; EE-waits-full is the
   correct backpressure either way (mirrors hardware FIFO-full, and the
   arbiter already copies every packet, so enqueue memcpy is not new cost).
3. PF1 must additionally capture: per-thread CPU split (game vs main),
   `processGIFPacket`+raster self time, `Present` (snapshot+convert) time,
   `UploadFrame` copy/`UpdateTexture` time, and achieved vsync-tick rate —
   these are the five numbers that turn §2e from a model into an estimate.

### 2e. What moving even the CPU GS off-thread saves (PF1 pending — model only)

PF1 has not landed (still running per `docs/status.md`; no report in
`local/research/`), so no credible absolute number exists. Anchors that do
exist: N3's ~21 guest frames/s on the Odin **with frame dumping on** (dump
cost included, not a GS cost); the per-tick CPU copy chain quantified in §3
(≥5 MiB/frame of memcpy + a full-frame convert + GL upload on the main
thread); `Present`'s unconditional 4 MiB `SnapshotVram` +
`PresentFromLocalMemory` conversion (`gs_cpu_backend.cpp:1760-1772`).

Expected shape of the win, to be confirmed by PF1's five numbers:

- Game thread sheds all raster work (`Submit`→`DrawPrimitive` and
  `UploadImage` bulk paths) and keeps only enqueue memcpy (already paid
  today inside `GifArbiter::submit`) plus the §2c waits. If the title run is
  FINISH/readback-light, game-thread GS cost drops to ~memcpy rate.
- Main thread sheds the 4 MiB snapshot + conversion + repacks in step (d)
  (§3); in step (a) it still pays the present RPC but the snapshot/convert
  runs on the GS thread, overlapped with the next vsync's EE work.
- Cost added: one thread hop latency per vsync (present RPC) and fence waits
  at FINISH/local→host. Net win condition (falsifiable once PF1 lands):
  `raster + convert + copies  >  enqueue + present-RPC latency + waits`.
  If FINISH/local→host traffic forces near-lockstep, the win shrinks to the
  present-path overlap only — that outcome would show up in PF1's wait
  attribution, not as a design failure.

## 3. Presentation

### 3a. Today's path (per display tick with a new vsync tick)

`UploadFrame` (`ps2_runtime.cpp:490-600`) → `latchHostPresentationFrame`
(`gs_frontend.cpp:535-584`) → `copyLatched…` (`:586-647`) → pad →
`UpdateTexture` (`:597`). Byte traffic for a 512×448 RGBA frame:

| Copy | Size | Where |
| --- | --- | --- |
| `SnapshotVram` inside `Present` | 4.0 MiB | `gs_cpu_backend.cpp:1765` |
| `PresentFromLocalMemory` conversion read+write | ~0.9 MiB read + ~1.2 MiB written (640×512 stride buffer) | `:1774-1894` |
| Latch store (`m_hostPresentationFrame`) | ~1.2 MiB | `gs_frontend.cpp:570` |
| `copyLatched` repack (640-stride → packed) | ~0.9 MiB | `:617-645` |
| `s_uploadBuffer` pad + `UpdateTexture` upload | ~1.3 MiB + GL upload | `ps2_runtime.cpp:576-597` |
| **Total CPU-side per tick** | **≥8 MiB memcpy + full-frame convert + GL upload** | |

A correct GPU GS still stalls on this: `Present`→pixels→re-upload serializes
the GPU behind a full readback every tick.

### 3b. GPU-resident path

paraLLEl already produces the right object: `vsync()` returns a
`ScanoutResult` whose `image` is a `Vulkan::ImageHandle`
(`gs_renderer.hpp:23-48`), with `internal/mode_width/height`,
`interlaced/phase`, and `dst_layout/stage/access` chosen by the caller
(`VSyncInfo`, `gs_interface.hpp:155-…`; the replayer uses
`READ_ONLY_OPTIMAL` + sampled-read, `gs_dump_parser.cpp` vsync case).
Design:

1. GS thread per vsync: `iface->flush()` then `iface->vsync(info)` with
   `dst_layout = SHADER_READ_ONLY_OPTIMAL` (sampled present quad) or
   `TRANSFER_SRC_OPTIMAL` (blit to swapchain). No `map_host_buffer`, no
   `copy_image_to_buffer` (the replayer's `save_scanout_ppm` path,
   `tools/gs_dump_replayer.cpp:209-348`, is diagnostics-only and stays that
   way).
2. Present thread acquires a swapchain image, blits/samples the scanout
   image into it (aspect from `mode_*`, deinterlace already applied unless
   `skip_deinterlace`), presents. One GPU-side blit replaces the §3a chain.
3. Explicit readbacks only for: T3/R1 transfers (`read_transfer_fifo` on the
   GS thread, bytes delivered via the consume RPC), and diagnostics
   (`map_vram_read` snapshots, PPM dumps — off by default, counted).
   Step (d) proves zero steady-state readback with a counter on those two
   paths (must read 0 across N frames with no local→host traffic).

Android vs Mac:

| Topic | Android (Odin / Adreno) | Mac (MoltenVK) |
| --- | --- | --- |
| Swapchain source | `ANativeWindow` from the NDK activity; same Vulkan code as the replayer's device init | `VK_MVK_metal_surface` / MoltenVK swapchain; same Vulkan code |
| Window owner today | raylib `android_main` (N2 entry chain: NDK glue → raylib → `main`) owns the window/surface | raylib GL window + GL context |
| Interop problem | None structural: new Vulkan swapchain presenter takes the native window from (or alongside) raylib; N lane owns that seam | **raylib/GL cannot import a `VkImage`.** No shared-texture shortcut exists |
| Recommended route | Same as Mac: minimal Vulkan swapchain presenter; N ports window handoff | Minimal Vulkan swapchain presenter (new; G authors, E merges — §5). raylib keeps input/window chrome only, or is replaced by GLFW+surface at that step |
| Interim (correctness-first) step | Same interim: one GPU→CPU copy + `UpdateTexture`, cost measured, then removed in (d) | Same interim |
| Validation available | Turnip contrast exists (G42) if Adreno misbehaves; sampler-feedback workaround is env-gated (G22) | `vsync_can_skip` + `consume_flush_stats` + `get_accumulated_timestamps` for frame-time split (GPU vs present) |

Note: Android is the *easier* target here (native Vulkan swapchain, no GL
interop), but Mac comes first per the brief because the runtime, captures,
and reference comparisons all run there.

## 4. Upstream check (`feature/iop-emulator` vs `fork/main`)

`git log fork/main..fork/feature/iop-emulator`: 22 commits, HEAD `78ecbae`
("fix: fix texture caching…"). 129 files changed (+15785/−1236), but the
GS-architecture delta is small — the branch's `3b9b14c "refactor: change GS
architecture"` arrived via a merge of `feature/gs-refactor`, i.e. the same
#204 refactor already in `fork/main` (`d74a3ce`).

GS-relevant changes on the branch:

| Change | Files | Verdict vs this seam |
| --- | --- | --- |
| New backend method `LoadClut(tex0, texclut)`, called from frontend TEX0/TEX2 writes | `gs_backend.h` (+1 virtual), `gs_cpu_backend.h/.cpp`, `gs_frontend.cpp` (+2 lines: the only frontend diff) | Compatible: decode-internal call in CPU mode; no-op mapping in paraLLEl mode (CLUT comes from its register stream). No seam move |
| CPU texture page cache + cached CLUT (`TexturePageCache`, `m_clut[512]`, function-pointer PSM dispatch replacing `std::function`) | `gs_cpu_backend.*`, new `gs_texture_page_cache.h`, `ps2_gs_memory.cpp` (+35), new `ps2xTest/gs_cache/` suite | Perf work inside the backend; invisible above `GSRasterBackend`. No seam move |
| GIF_STAT (`0x10003020`) + FQC emulation: FQC derived from pending-GIF-transfer QWC (clamped to 16, `<<24`), cleared on timer advance | `ps2_memory.cpp` (GIF_STAT hunks) | **Adopt the register, re-source the value**: FQC must read *ring occupancy* under this design (same clamp). No wait on read — atomic load |
| VIF1 GIF image-packet accounting (`pendingGifImageQwc`: whole-stream tag walk replacing first-tag-only `gifImageQwcFromTag`) | `ps2_vif1_interpreter.cpp` (+36/−8) | Private helper improvement on the P3 path; packet bytes unchanged. No seam move |
| Untouched | `ps2_gif_arbiter.*`, `gs_frontend.h`, `gs_types.h`, `ps2_gs_common.h`, `submitGifPacket` signature/shape, `latchHostPresentationFrame`/`UploadFrame` path, `processGIFPacket` decode | The seam this design builds on is identical on both sides |

**Verdict: the branch does not move the seam.** The GS delta is a
backward-compatible backend-method addition, a CPU-side texture cache, one
new EE-visible FIFO-occupancy register (which this design must source from
ring depth), and a VIF1 accounting fix. Nothing in it changes where the
packet queue goes, what crosses it, or where the sync points are. Two
adaptations when rebasing onto/ past it: (1) carry the `LoadClut` call in
the moved CPU decode; (2) implement GIF_STAT FQC from ring occupancy.
(Upstream contact remains out of scope per standing rules; this was
read-only `git log`/`git diff`.)

## 5. Build plan (ordered; each step ends with its test)

Pre-step M0 (measurement, no code): E7 packet-log byte/vsync distribution +
PF1's five numbers (§2d). Gates ring constants and turns §2e into an
estimate. Owner: whoever runs E31/PF1; GB1 needs only the tables.

| Step | Work | Test (pass = …) | Files (lane) | Size |
| --- | --- | --- | --- | --- |
| (a) CPU backend behind the queue on its own thread, Mac | New `gs_worker` (ring + GS thread + moved decode core); `submitGifPacket`/arbiter drain → enqueue; P6/P7 → `upload_image_native` cmds; W1/W2 → `reg_write`; V1/V3/V4 → `priv_write` + EE shadow; R1–R4/R-reset → RPCs; `siglblid` writer moves to GS thread; `UploadFrame` → present RPC | (i) Existing suites green unmodified (`ps2_gs_tests`, `ps2_memory_tests` — EE-side API unchanged). (ii) New determinism test: direct-vs-queued on synthetic + captured packet streams, byte-exact `SnapshotVram` + `Present` pixels + consume bytes. (iii) E29-bypass boot-to-title A/B: same frame hash (`2ab49bac…` shape) with queue on/off | Fork `ps2xRuntime/{include,src}/lib/gs/gs_worker.*` (new), `gs_frontend.{h,cpp}` split, `ps2_memory.{h,cpp}` funnel, `ps2_runtime.cpp` present call, `ps2xTest` additions — **all E** | ~800–1200 lines new, ~200 touched |
| (b) paraLLEl backend on the Mac via MoltenVK | GS-thread paraLLEl mode: `gif_transfer`/`write_register`/priv stores/`read_transfer_fifo`/`flush`+`vsync`; Granite/Vulkan build wiring for the fork; interim present = one GPU→CPU copy + `UpdateTexture` (correctness first) | One live runtime frame (title or menu) through paraLLEl vs CPU backend: diff table in the G8/G10 style (same packet/vsync/field, native geometry, per-pass stats reset — review §G8/G9 corrections apply). **Not byte-exact**: paraLLEl is an independent implementation; tolerance documented per the G-lane method, with PCSX2-sw as second oracle for reference-incomplete features (plan §5a rule) | Adapter + build wiring in fork (G authors, **E merges** — E owns the fork); paraLLEl-side changes on `brad-richardson/parallel-gs`+`/Granite` `ssx3` branches (**G**); harness compare in `ps2xGS` (**G**) | ~500–800 + build files; Granite submodule bytes need their own SSD cap |
| (c) Android Vulkan | NDK build of bridge + Granite; `ANativeWindow` swapchain init; N3-shape launch | N3-shape boot on the Odin to the animating title, GPU GS on, screencap-verified; `done`-style receipt (no silent death — cf. the old D2 lesson) | Fork Android build files (**N**, E merges), bridge Android init (**G**+N), env/launch shim (**N**) | ~300–500 + build files |
| (d) Presentation without readback + frame-time cost | Vulkan swapchain presenter both platforms (§3b); readback counters on `read_transfer_fifo` + `map_vram_read`; retire interim copy | (i) Counters read 0 across N steady frames with no local→host traffic (proof of no readback). (ii) Frame-time split: `get_accumulated_timestamps` (GPU) + host present timing vs plan §5 gates (≤4 ms mini / ≤6 ms Odin at 512×448 — provisional until PF1 re-baselines them) | Presenter (G authors, E merges); counters in bridge (**G**); run receipts (**G**/N) | ~400–600 |

Ordering constraints: (a) before (b) (the queue is paraLLEl's feed);
(b)-Mac before (c) (reference comparisons run on the Mac); (c) and (d)-Mac
can overlap once (b) is green; only **one live PS2 runtime mutator** holds
the fork/P-lane lease at a time (standing rule — E owns the checkout, so
G-authored fork files land through E's queue). No step rewrites GIF decode
semantics, touches the recompiler, or contacts upstream.

## Gaps and open questions (stated plainly)

1. No race/traffic numbers exist yet (M0/PF1 pending) — ring constants and
   §2e are provisional by construction.
2. `siglblid`/`imr`/`busdir` are plain `uint64_t` shared across threads
   today; the atomicity split in §2b needs implementing, not just declaring.
3. E4's `ReadVram` census at VBlank becomes a GS round-trip per sample —
   fine at census rates, but the E4 window must be re-budgeted or moved
   GS-side in step (a).
4. The Mac swapchain presenter (§3b) is new code with no in-repo precedent;
   raylib's exact retained role (input/chrome vs replaced) is an
   implementation detail for step (d), flagged here so it isn't rediscovered.
5. Adapter-file authorship (G writes, E merges) needs an orchestrator call:
   it is the one place the "E owns the fork" rule meets "G owns the GPU
   path".
6. `ps2xGS`'s `LoadClut`-era drift: its pinned upstream CPU backend predates
   the new virtual — step (a)/(b) must decide whether `ps2xGS` re-pins or
   carries the one-method shim (recommend: shim, one line, no re-pin).

## Recommended next action

Land M0 (E7 byte/vsync table + PF1's five numbers) and gate step (a) on it;
in parallel, get the orchestrator's call on gap 5 (adapter authorship) so
step (b) has a merge path before G writes it. No code, boots, or leases were
used for this design (time box respected).
