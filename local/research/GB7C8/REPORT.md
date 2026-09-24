# GB7C8 — matched GPU comparison design for packet5470 (read-only)

Predeclared outcomes (brief): **A** = a source-grounded, nonperturbing
per-packet GPU execution/readback witness with unique predictions for
source-word divergence, write/composite divergence, and later overwrite;
**B** = no such witness without an intervention, but a bounded post-packet
marker comparison can narrow the stage (limits stated); **OTHER** =
pin/path/citation gap. No GPU cause from source alone.

Verdict: **B**. No nonperturbing per-packet GPU execution/readback witness
exists in the pinned sources. The smallest brief-constrained same-stream
marker300/301 matched CPU/paraLLEl comparison is designed below; a marker
mismatch cannot be attributed to packet5470 alone (5001 intervening packets
before marker300, 5123 before marker301). No GPU cause is claimed.

## 0. Scope, pins (all verified read-only, 2026-09-24)

| Item | Value | How verified |
| --- | --- | --- |
| ssx3 HEAD | not found (record at check time) | `git -C ~/dev/ssx3 rev-parse HEAD`, tree must be clean except `local/research/GB7C8/` |
| GB4 fork `~/dev/ssx3-work/GB4/PS2Recomp` | `f54adff3ab38108300d7ab7d239f59345bae97c3` | `git rev-parse HEAD`; tree clean; branch holds `[GB7C7P2]` at tip |
| capture `run/gb4p4.capture.bin` | sha256 `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` | `sha256sum` (matches GB7C6/GB7C7P2 pins) |
| sidecar `run/gb4p4.paths.txt` | 1,982,063 lines; line 5471 = `5470 3` | `sed -n 5471p`, `grep -c` |
| paraLLEl-GS source actually used by GB4 build | `/Users/brad/dev/ssx3-work/G43/parallel-gs` @ `3a66c19`, **dirty** (M `CMakeLists.txt`, `gs/gs_interface.cpp`, `gs/gs_renderer.cpp`, `gs/gs_renderer.hpp`, `tools/CMakeLists.txt`, `tools/gs_dump_replayer.cpp`; `Granite` submodule modified) | `PS2X_PARALLEL_GS_SOURCE_DIR` in `~/dev/ssx3-work/GB4/build/CMakeCache.txt:899`; `git rev-parse HEAD` + `git status --short` in that dir |
| canonical `~/dev/parallel-gs` | `faf6400`, **NOT the build source** | `git rev-parse HEAD`; no `PS2X_PARALLEL_GS_SOURCE_DIR` points at it |
| packet5470 identity | tick 259, record offset 6673427, GIF 1696 B, embedded path 1 → corrected path 3 | independent capture scan (record layout `gs_stream_capture.cpp:86-121`); agrees with GB7C6 §1 and GB7C7P2 §0 |
| marker259 | offset 6673264, 5470 packets seen → **precedes** packet5470 at 6673427 | independent scan; agrees with GB7C7P2 §3 |
| marker260 / marker300 / marker301 | offsets 6702775 / 7883215 / 7912726; packets seen 5592 / 10472 / 10594 | independent scan |
| scope | read-only: source reads + capture scans only. No source edit, build, replay, device action, lease, push, board/global config edit, upstream contact | — |

Line citations below: fork paths at `f54adff`; paraLLEl-GS paths at
`3a66c19` working tree (dirty — exact line numbers may shift; functions named).

## 1. CPU fact to build on (GB7C7P2, accepted)

Direct CPU replay executed tick259/path3/packet5470/batch10 at FBP112 pixel
`(342,377)`, destination GS address `0x0019ae38`; sampled CT32 tap0 word
`63353341` at GS address `0x000bae74`, then raw destination
`dc302f3b→dc353341` (`tap.tsv` pixel row; REPORT §4). One pixel, not a
whole glyph or GPU cause. Capture marker259 (offset 6673264) precedes
packet5470 (offset 6673427); the marker259 frame is a **pre-write** control
and cannot show the tapped `353341`. GB7A gate: same-stream packet-entry
equality is an input/null control only.

## 2. Where packet5470 enters the paraLLEl backend

1. Replay calls `GS::processGIFPacket(bytes, size)` per kind-1 record with
   the sidecar-corrected path latched via `gs.noteGifPath`
   (`ps2_gs_replay_tests.cpp:660,680`; frontend `gs_frontend.cpp:929-949`).
2. On the worker thread the packet is captured/logged
   (`ps2x_gs_capture::packet`, `ps2_e7::packet`, `:950-952`), then the
   raw-GIF fanout runs **before** the CPU decode:
   `if (m_rawGifBackend) m_backend->RawGifPacket(m_curGifPath, data, sizeBytes)`
   (`gs_frontend.cpp:953-956`).
3. `GSParallelBackend::RawGifPacket` (live replay backend,
   `ps2_gs_parallel_backend.cpp:275-283`) early-returns on empty/uninit input,
   else calls `m_iface->gif_transfer(path, data, size)` and bumps only the
   receipt counters `gifPackets`/`gifBytes`. The shadow path is the same call:
   `ps2_gs_shadow.cpp:461` `s.iface->gif_transfer(...)`, counter `gifFed`.
4. `GSInterface::gif_transfer` (`gs_interface.cpp:5191-`) parses GIF tags
   incrementally per path (`PACKED`/`REGLIST`/`IMAGE` handlers, optimized draw
   handler fast path) and **accumulates** primitives into the current render
   pass — it submits no Vulkan work. The 17 textured sprite batches of
   packet5470/tag2 therefore enter paraLLEl as recorded path state + queued
   draw batch data, not as executed GPU commands.

Observable at this stage (receipt only): `gifPackets`/`gifBytes` counters,
`gifFed`/`regFed` shadow counters, and — only with new instrumentation — a
packet-entry log (tick, submit-index, corrected path, byte FNV) at the
`processGIFPacket` head / `RawGifPacket` entry. Such a log is the GB7A A1
**input/null control**: equality proves the same bytes entered both backends;
it proves nothing about GPU execution (GB7A gate correction).

## 3. How the 17 batches reach GPU command submission

- Submission happens later, at `GSInterface::flush()` (`gs_interface.cpp:5153`):
  `flush_pending_transfer(true)` + `tracker.mark_submission_timeline()` +
  `renderer.flush_submit(value)`. `flush_submit` (`gs_renderer.cpp:1116`)
  flushes attribute scratch, transfers, clears, triangle-setup and queued
  render passes into submitted Vulkan command buffers.
- The live replay backend's `Flush()` is a **no-op**
  (`ps2_gs_parallel_backend.cpp:136`: `void Flush() override {}`), so during
  replay nothing is submitted until `Present()` runs `m_iface->flush()`
  (`:153`) followed by `m_iface->vsync(vsync)` (`:154`). The shadow backend
  likewise only submits at its `onPresentFrame` `s.iface->flush()` + `vsync()`
  (`ps2_gs_shadow.cpp:561-562`).
- Consequence: packet5470's 17 batches sit in the open render pass together
  with packets 5471+ until the next flush/vsync boundary. There is no
  per-packet submit boundary in the pinned code — batching across packets is
  the normal case, and any forced mid-stream flush changes the batching the
  comparison is supposed to measure.

CPU contrast (why the CPU tap has no GPU analogue): the CPU backend executes
synchronously — `vertexKick` → `buildDrawBatch` → `m_backend->Submit(batch)`
(`gs_frontend.cpp:1943-1998`) → `GSCpuBackend::Submit` → `DrawPrimitive`
(`gs_cpu_backend.cpp:1466-1472`) writes VRAM immediately; `Flush`/`Sync` are
documented no-ops (`:1474-1488`) and `ReadVramUnlocked` reads the written word
directly (`:1496-1501`). The paraLLEl backend's `Submit` is even an explicit
no-op (`ps2_gs_parallel_backend.cpp:121`): everything flows through the
raw-GIF path into deferred Vulkan submission.

## 4. Where/when texture source and destination VRAM can be read

Four stages, explicitly separated (recording ≠ submission ≠ completion ≠
readback):

| Stage | paraLLEl mechanism | Source rows |
| --- | --- | --- |
| packet recording | `gif_transfer` parses into path/render-pass state; counters only | `gs_interface.cpp:5191-` (`gif_transfer`); `ps2_gs_parallel_backend.cpp:275-283` |
| command submission | `flush()` → `mark_submission_timeline` → `renderer.flush_submit` | `gs_interface.cpp:5153-5166`; `gs_renderer.cpp:1116-` |
| GPU completion | `device->submit(cmd)` + `device->wait_idle()` (Present readback) or `renderer.wait_timeline(t)` (`map_vram_read`) | `ps2_gs_parallel_backend.cpp:189-190`; `gs_interface.cpp:5126-5151` |
| host readback | (a) `Present` scanout → `copy_image_to_buffer` → map host buffer (`:174-195`); (b) `SnapshotVram`: `flush()` + `map_vram_read(0, 4MiB)` + memcpy (`:245-264`); (c) `ConsumeLocalToHostBytes` → `read_transfer_fifo` (`:223-232`) | rows cited |

Every host-visible VRAM read **forces** submission and/or waiting:

- `map_vram_read` computes the page-rect timeline and, if unsubmitted,
  `mark_submission_timeline(HostAccess)` + `flush_submit` + `wait_timeline`
  before returning the pointer (`gs_interface.cpp:5126-5151`).
- `SnapshotVram` calls `m_iface->flush()` then `map_vram_read`
  (`ps2_gs_parallel_backend.cpp:253-255`).
- `Present` calls `m_iface->flush()`, `vsync()`, then a barrier + copy +
  `submit` + `wait_idle` before mapping (`:153-190`).
- Frontend `presentForDiagnostics` always runs
  `m_backend->Flush(); m_backend->Sync(Presentation); m_backend->Present(...)`
  (`gs_frontend.cpp:858-864`); the latched variant adds the same triple
  (`:804-812`).

Active TEX0/FRAME/UV state as a source-control: on the CPU it is observable
today (GB7C7P2 `tap.tsv` `state`/`blend` columns). On paraLLEl there is no
pinned logging of per-batch TEX0/CLAMP/TEX1/FRAME/TEST/ALPHA/XYOFFSET/UV —
`get_register_state` exists (`gs_interface.cpp:5300`) but no per-draw state
log is wired to replay; reading it mid-stream still lands after the same
flush/submit boundary. So the source-control is **not observable on paraLLEl
without a source edit** (future work, not this read-only part).

## 5. Test: can an observation at exactly packet5470/batch10 avoid an intervention?

No. Any observation of paraLLEl texture source bytes (`0x000bae74`) or
destination bytes (`0x0019ae38`) at exactly packet5470/batch10 must use
`map_vram_read`, `SnapshotVram`, or `Present`/scanout readback, each of which
performs an extra `flush`/`flush_submit` and/or `wait` that the unobserved
stream would not perform at that point (§4 rows). That intervention changes
draw batching (the open render pass is cut at packet5470 instead of at the
natural later boundary) and synchronizes the GPU earlier than the comparison
stream. A byte-equal result after such a flush would show the flushed prefix,
not unperturbed per-packet execution; a mismatch would be equally consistent
with the flush reordering/batching change. Packet-entry byte equality,
queued-batch counts, the marker259 (pre-write) frame, eight isolated words,
or a flush/submit added before the observation therefore cannot witness
per-packet GPU execution. **A is rejected on source grounds.**

## 6. B design: bounded post-packet marker300/301 matched comparison

What it is: replay the pinned capture + sidecar twice on one stream —
once CPU (`PS2X_GS_REPLAY_BACKEND` unset, direct, no probe), once paraLLEl
(`PS2X_GS_REPLAY_BACKEND=parallel`, queued) — and compare at the first
brief-constrained markers after packet5470 (marker300, then marker301).

Exact coordinates and conversions (from GB7C6 §3c, GB7C7P2 §4):

- Destination: FBP112, FBW8, PSM1 (CT24) pixel `(342,377)` →
  `addrPSMCT32(112<<5, 8, 342, 377)` = `0x0019ae38`
  (`ps2_gs_psmct32.h:27-36`; block basis `fbp<<5`, `ps2_gs_common.h:42-45`).
- Source tap0: TBP0=0, TBW8, PSM0 (CT32) texel `(343,378)` →
  `addrPSMCT32(0, 8, 343, 378)` = `0x000bae74`. Tap quad, `fx=fy=0`,
  TEX0/TEX1/CLAMP/TEXA/FRAME/TEST/ALPHA/PRIM/RGBAQ per GB7C7P2 §4 row.

Comparison steps (all at marker300, repeat at marker301):

1. **A1 null control**: per-packet entry log (tick, submit-index, corrected
   path, byte FNV) at the `processGIFPacket` head on both backends; require
   byte-equality through the marker. A mismatch voids the run
   (replay/capture-path fault); equality licenses only the input, per GB7A.
2. **Source-control if observable**: log active TEX0_1/CLAMP_1/TEX1_1/FRAME_1/
   TEST_1/ALPHA_1/XYOFFSET_1/PRIM/RGBAQ + sprite rect/UV per title batch on
   the CPU (exists: GB7C7P2 probe pattern); record paraLLEl side as
   not-observable without a source edit (§4).
3. **Content comparison**: full-frame `GB4_FRAME` Present hash
   (`ps2_gs_replay_tests.cpp:899-906`), plus a cropped FBP112 read around
   `(342,377)` (suggested crop `(320,352)-(364,392)` covering batch10's strip
   neighbourhood) and the raw word at `0x0019ae38` and at source `0x000bae74`
   via the backend's legal read path (CPU `ReadVramUnlocked`; paraLLEl
   `SnapshotVram`/Present readback — both post-marker, so no mid-stream
   intervention). Compare CPU vs paraLLEl hashes/words.
4. **ON/OFF image-hash control** for any future default-OFF tap: run the same
   binary with and without the trace flag through marker301; require equal
   `GB4_FRAME` hashes and byte-equal PPMs at ticks 259/300/301 before trusting
   traced values (GB7C7P2 §3 pattern; note its adjacent-binary caveat — the
   future run must use one binary).

Confounder (must be named in any future report): marker300 is **5001 packets**
after packet5470 (packets seen 5470 → 10472; ticks 259→300; independent scan:
121 more tick259 packets, then 122/tick for ticks 260–299); marker301 is
**5123 packets** after (packets seen 10594). Plus all kind-2 priv writes,
kind-3 transfers and kind-5 native uploads interleaved in that span. A marker
mismatch therefore narrows the stage only to "something in the 5001-packet
prefix after packet5470" — it cannot be attributed to packet5470/batch10
without an execution witness, which §5 shows does not exist nonperturbingly.
(Marker260 is only 122 packets after packet5470, but the brief constrains this
design to marker300/301 where the named PPM/frame infrastructure samples;
a closer-marker variant is left to the orchestrator.)

Limits of B (state plainly): B can show (i) whether the inputs matched (A1),
(ii) whether full/cropped FBP112 content around `(342,377)` and the two
watched words agree at marker300/301, and (iii) which stage to instrument
next (texture/decode vs composite/present per GB7A §4 ladder). It cannot
identify packet5470 as the cause of any mismatch, cannot see the texture-word
producer, and cannot establish a whole glyph. No GPU cause follows from
source alone or from a later-marker comparison.

## 7. A/B/OTHER evidence table (hand back)

| Claim | Evidence | Status |
| --- | --- | --- |
| Pins (fork `f54adff`, capture SHA `a6f75fb3…ad51851`, sidecar `5470 3` / 1,982,063 lines, paraLLEl source `/Users/brad/dev/ssx3-work/G43/parallel-gs @ 3a66c19` dirty) | §0 table; `CMakeCache.txt:899`; independent capture scan | VERIFIED |
| Packet5470 enters paraLLEl via `RawGifPacket` → `gif_transfer` as recorded state, not executed commands | `gs_frontend.cpp:953-956`; `ps2_gs_parallel_backend.cpp:273-283`; `gs_interface.cpp:5191-` | SOURCE-GROUNDED |
| 17 batches accumulate in open render pass; submission only at `flush()`/`vsync` | `gs_interface.cpp:5153-5166`; `gs_renderer.cpp:1116-`; live `Flush()` no-op `ps2_gs_parallel_backend.cpp:136`; `Present` flush+vsync `:153-154` | SOURCE-GROUNDED |
| Every VRAM observation forces flush/submit/wait | `map_vram_read` (`gs_interface.cpp:5126-5151`); `SnapshotVram` (`ps2_gs_parallel_backend.cpp:245-264`); `Present` copy+`wait_idle` (`:174-190`); frontend triple (`gs_frontend.cpp:804-812,858-864`) | SOURCE-GROUNDED |
| **A** (nonperturbing per-packet witness exists) | none — §5 shows every candidate observation perturbs batching/timing | **REJECTED** |
| **B** (bounded marker300/301 comparison narrows stage, limits stated) | §6 design; confounder 5001/5123 packets + priv/transfer records quantified by independent scan | **ACCEPTED (design only; no run performed)** |
| **OTHER** (pin/path/citation gap) | none open — all pins verify, all cited rows read | NONE |
| GPU cause of title damage | not tested; explicitly excluded | NOT CLAIMED |
| Texture-word producer / whole glyph | unchanged gaps from GB7C6/GB7C7P2 | NOT CLAIMED |

## 8. Gaps

- ParaLLEl-GS source is dirty at `3a66c19` (local G-lane patch stack on top);
  line numbers cited are working-tree; a future run must pin the exact dirty
  diff (or a clean commit) and re-verify rows. Canonical `~/dev/parallel-gs`
  (`faf6400`) is unrelated to the GB4 build.
- No per-batch TEX0/FRAME/UV log exists on the paraLLEl side (source-control
  gap, §4); wiring one is a source edit outside this read-only part.
- No replay, boot, device action, or speed number in this part. `check.py`
  verifies pins and cited rows from strings only — it cannot prove runtime
  behaviour.
- Recommended next action (for the orchestrator): gate this design, then
  brief the §6 marker300/301 matched run (one binary per backend pair,
  ON/OFF hash control, A1 log equality first) before any closer-marker or
  per-packet instrumentation.

## 9. Receipts

- ssx3 `local/research/GB7C8/`: `REPORT.md` (this file),
  `observable-table.tsv`, `check.py`, `check-result.txt`. No capture bytes
  committed (hashes + offsets only). Text < 512 KiB; no build/boot/replay.
- Commit `[GB7C8]` with `Orchestrated-By: opencode`, no push.
