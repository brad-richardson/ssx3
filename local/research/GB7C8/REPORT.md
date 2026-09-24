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
Because HEAD does not pin dirty content, SHA-256 of every cited dirty file is
recorded in §0a; all behaviour claims are source-structure claims, and no
built-behavior claim is made (binary provenance unproved, §0a).

## 0a. Cited-source identity (orchestrator review)

| File | SHA-256 (working tree at check time) |
| --- | --- |
| `G43/parallel-gs/gs/gs_interface.cpp` | `5ccc962f080bbb1e1fc637155799823008409f2fd3b283d1f2f0e9d6eb5077f4` |
| `G43/parallel-gs/gs/gs_renderer.cpp` | `8071dd2edb5f51ae29a759afa8dd956765dc968f8a42d414bb8648769ac3c65a` |
| `G43/parallel-gs/gs/gs_renderer.hpp` | `7f7a1e2b7d69014a02e91c790c070cfb4cabd1bf4dd7161cf128ac4caa2d48a3` |
| `G43/parallel-gs/gs/page_tracker.cpp` | `96edd79a27a48e0a5dc84d130aea3da4c09f3111d9df65ee1986243ff4893fd1` |
| `G43/parallel-gs/gs/gs_interface.hpp` | `b74f5d22e75629d57951e213d184ffaebe81e8f2c3bbeb65895bec9` |

Replay binary observed (NOT pinned as built behaviour):
`~/dev/ssx3-work/GB4/build/ps2xTest/ps2x_tests` (8,252,216 B, Sep 24 13:16)
SHA-256 `b6fa3bdb8c2c03d659503ca98c637dcb865ccba3bb76a710ca4fed7dad39a738`.
Build/source identity is **unproved**: no build was performed in this part,
the binary postdates the GB7C7P2 build-5 binary of identical size, and which
source revisions/flags produced it was not established. Any future run must
rebuild from pinned sources and record binary + source SHAs at run time.
`check.py` verifies strings/pins/scans only — it cannot prove runtime
behaviour.

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
  the common case, but it is **not guaranteed**: mid-stream render-pass cuts
  exist (correction, orchestrator review — verified in the dirty G43
  worktree, see §3a). Whether packet5470 itself trips one is a runtime
  question (accumulated counts unknowable without execution) and cannot be
  settled from source alone.

### 3a. Mid-stream render-pass cut exception (correction)

`GSRenderer::check_flush_stats()` (`gs_renderer.cpp:879-909`) sets a memory
pressure flag via `tracker.mark_memory_pressure()` when pending work exceeds
thresholds (`MinimumPrimitivesForFlush` 4096, `MinimumRenderPassForFlush`
1024, image-memory-per-flush budget, 100 MB scratch, 16k copies, palette
uploads; `gs_renderer.cpp:31-39,884-909`). The flag is consumed on draw paths
by `PageTracker::flush_if_memory_pressure()` → `flush_render_pass(
PressureFlush)` (`page_tracker.cpp:965-976`) at `handle_tex0_write`
(`gs_interface.cpp:1629`) and `post_draw_kick_handler` (`:3811-3823`), the
latter also cutting on `Overflow` caps (`MaxPrimitivesPerFlush` 64k,
`MaxTextures`, `MaxStateVectors`; `gs_renderer.hpp:154-156`). Further
mid-stream cuts: `TextureHazard` (`gs_interface.cpp:1739,1747`) and
`FBPointer` (`:1815`). So a render-pass boundary **can** fall inside or
immediately around packet5470's batches under pressure — §3's "no per-packet
submit boundary" overstates. What stands: (i) full Vulkan command submission
still happens only at `flush()` → `flush_submit`, `vsync`, or the
`map_vram_read` internal submit; a render-pass cut is segmentation, not
completion/readback; (ii) every host-visible observation still forces
`flush`/`flush_submit` + `wait`, i.e. the §5 intervention; (iii) pressure/
overflow cut points depend on accumulated counts, so an added probe or forced
flush perturbs them too. The A-rejection is unchanged; the B confounder
(§6) is unchanged.

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
121 more tick259 packets, then 122/tick for ticks 260–299) plus 40 VBlank
markers and 240 priv writes interleaved in that span (0 transfers/native/
local-to-host/clear records); marker301 is **5123 packets** after (packets
seen 10594). A marker mismatch therefore narrows the stage only to "something
in the 5001-packet prefix after packet5470" — it cannot be attributed to
packet5470/batch10 without an execution witness, which §5 shows does not
exist nonperturbingly. (Prefer marker260 per §6a: 121-packet confounder.)

### 6a. Marker260 first (orchestrator review; recommended before 300/301)

Marker260 (offset 6702775, packets seen 5592) is the first post-packet
marker: only **121 intervening packets** (5471..5591, all tick259) and
**zero** interleaved non-packet records in that span (independent scan;
compare 5001 packets + 40 markers + 240 priv writes before marker300, 5123
before marker301). The existing harness can sample it: `dumpTick` accepts an
arbitrary `PS2X_GS_REPLAY_PPM_TICKS` list (`ps2_gs_replay_tests.cpp:245-263`),
and `GB4_FRAME` + PPM + `presentForDiagnostics` run for every named tick
independent of `STEP` (`:880-906`, `if (!sampled) continue` only gates the
hash rows at `:940`). `PS2X_GS_REPLAY_PPM_TICKS=259,260` (+`STEP=1` if
per-tick hash rows are wanted) samples marker260 with no harness change.
Recommendation: run the §6 matched comparison at **marker260 first** (same
tick259, 121-packet confounder, no interleaved priv/transfer records); go to
300/301 only if 260 agrees. The 300/301 design above is retained because the
brief constrains it and the named PPM infrastructure already samples those
ticks. Verdict stays B; no run and no cause claim in this part.

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
| Cited dirty-source identity (SHA-256 per file, §0a); binary provenance unproved, no built-behaviour claim | §0a table; observed binary SHA `b6fa3bdb…39a738` | RECORDED (identity unproved by design) |
| Packet5470 enters paraLLEl via `RawGifPacket` → `gif_transfer` as recorded state, not executed commands | `gs_frontend.cpp:953-956`; `ps2_gs_parallel_backend.cpp:273-283`; `gs_interface.cpp:5191-` | SOURCE-GROUNDED |
| 17 batches accumulate in open render pass; full submit only at `flush()`/`vsync`/internal map submit — but mid-stream render-pass cuts exist (pressure/overflow/hazard) | §3a: `gs_renderer.cpp:879-909,31-39`; `page_tracker.cpp:965-976`; `gs_interface.cpp:1629,3811-3823,1739,1747,1815` | SOURCE-GROUNDED (exception recorded) |
| Every VRAM observation forces flush/submit/wait | `map_vram_read` (`gs_interface.cpp:5126-5151`); `SnapshotVram` (`ps2_gs_parallel_backend.cpp:245-264`); `Present` copy+`wait_idle` (`:174-190`); frontend triple (`gs_frontend.cpp:804-812,858-864`) | SOURCE-GROUNDED |
| **A** (nonperturbing per-packet witness exists) | none — §5 shows every candidate observation perturbs batching/timing (and cut points depend on counts) | **REJECTED** |
| **B** (bounded marker comparison narrows stage, limits stated) | §6 design (300/301) + §6a marker260-first (121-packet confounder, harness samplable, no harness change) | **ACCEPTED (design only; no run performed)** |
| **OTHER** (pin/path/citation gap) | none open — all pins verify, all cited rows read | NONE |
| GPU cause of title damage | not tested; explicitly excluded | NOT CLAIMED |
| Texture-word producer / whole glyph | unchanged gaps from GB7C6/GB7C7P2 | NOT CLAIMED |

## 8. Gaps

- ParaLLEl-GS source is dirty at `3a66c19`; cited dirty files are pinned by
  SHA-256 in §0a (not by HEAD). A future run must rebuild from pinned sources
  and record binary + source SHAs at run time; the observed
  `build/ps2xTest/ps2x_tests` SHA is receipt-only (provenance unproved).
  Canonical `~/dev/parallel-gs` (`faf6400`) is unrelated to the GB4 build.
- Whether packet5470's own batches trip a pressure/overflow render-pass cut
  (§3a) is runtime-only: accumulated counts are unknowable without execution.
  A future run's A1/input logging must not itself move the cut points it is
  compared against — same-binary ON/OFF control required.
- No per-batch TEX0/FRAME/UV log exists on the paraLLEl side (source-control
  gap, §4); wiring one is a source edit outside this read-only part.
- No replay, boot, device action, or speed number in this part. `check.py`
  verifies pins, SHA strings and cited rows from strings/scans only — it
  cannot prove runtime behaviour.
- Recommended next action (for the orchestrator): gate this design, then
  brief the matched run at **marker260 first** (§6a:
  `PS2X_GS_REPLAY_PPM_TICKS=259,260`, A1 log equality first, one binary per
  backend pair with ON/OFF control); go to 300/301 only if 260 agrees.
  This review arrived after commit `016f4086`; the corrections above are
  a second commit, no amend.

## 9. Receipts

- ssx3 `local/research/GB7C8/`: `REPORT.md` (this file),
  `observable-table.tsv`, `check.py`, `check-result.txt`. No capture bytes
  committed (hashes + offsets only). Text < 512 KiB; no build/boot/replay.
- Commit `[GB7C8]` with `Orchestrated-By: opencode`, no push.
