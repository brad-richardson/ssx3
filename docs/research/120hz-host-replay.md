# Host-side frame replay — September 13, 2026

Host replay remains isolated research and is **not enabled on the phone**.
The current milestone captures an original frame and audits command/resource
ordering in private memory. Replay rendering is deliberately blocked: the
normal Dolphin decoder has guest-visible and persistent GPU side effects.
The older camera-offset prototype below is historical evidence, not an
accepted implementation.

## Current correctness milestone

`native/diagnostics/native_frame_replay.h` now records one FIFO frame without
injecting guest draws or running the scheduler. It requires single-core mode,
immediate XFB, and no simultaneous scheduler/repeat experiment. Recording's
first XFB boundary arms capture; the second ends the captured frame. The
reference screenshot request now runs in that second XFB's `before_present`
event, with the recorded frame and presentation IDs in the trace. The capture
prerequisite also requires the flushed PNG artifact. Its exact encoder frame
identity is still unverified: FrameDumper consumes screenshot names on its
worker thread, so an earlier pending readback could consume a newer request.

The old loop that overwrote live RAM and executed `RunFifo<false>` is removed.
The audit instead uses Dolphin's command-size decoder with private callbacks:

- Memory updates are validated, then applied at their recorded FIFO positions.
  Equal-position and overlapping writes preserve recorder order. Invalid ranges,
  backward positions, incomplete commands and non-inlined display lists fail.
- RAM starts at zero, matching FifoRecorder's initial shadow banks; CP/BP/XF/TMEM
  start from the capture before each of three independent passes. Canonical CP
  writes are applied locally without CPState's analytics/runtime callbacks.
- Indexed XF data is read only from the private banks. Primitives are counted
  and sized; vertex loading, texture interpretation, TMEM transfers, EFB copies,
  GPU execution and presentation are **not** emulated by this audit.
- Whole allocated RAM/EXRAM banks are compared before and after auditing.
  GameCube's configured MEM2 size does not imply allocated EXRAM: null banks
  have audit size zero. This check supports the private audit's narrow claim;
  it does not prove renderer/event/cache isolation.

`tools/gamecube_replay_check.py` requires ordered schema-2 events, a bounded
FIFO v6 artifact, the same recorded/reference frame IDs, three agreeing audit
passes, a complete PNG, and the explicit renderer block. `--capture-only`
can pass this request/artifact prerequisite; it does not verify the encoder's
frame identity. The default command always exits nonzero until
renderer isolation and same-frame replay evidence exist. Optional candidate
PNGs are decoded to canonical RGBA for exact pixel comparison; even identical
pixels do not establish safe replay or same-frame candidate provenance.

The asset-independent regressions cover future/overlapping writes, invalid
ranges and positions, unavailable EXRAM, reset between passes, missing or
early reference evidence, stale or partial audits, malformed PNGs and the
requirement that identical screenshots cannot pass renderer acceptance.

### Evidence from this pass

An isolated offline audit of the first real capture
(`local/research/120hz/replay-correctness-offline/`) decoded 647,799 FIFO bytes
and 6,404 memory updates in each of three passes. Each pass found 20,159
commands, 5,942 primitives, 2,086 indexed XF loads, 13 EFB copies (one XFB),
two token commands and 19 TMEM load/sync commands. All indexed resource digests
agreed. Malformed display-list, unknown-command, CP and XF inputs were rejected
by the actual pinned audit callback.

The first live run exposed an audit bug: the whole-bank check used the
configured EXRAM size with GameCube's null EXRAM pointer. The corrected code
uses allocation presence, and a compiled regression covers that case. The
failed run is preserved as evidence and is not accepted as a completed capture
or continuation check; its screenshot request had not flushed before the crash.

The corrected final run (`replay-correctness-player6`, profile `replayaudit2`)
passed the 180-second course and runtime checks. At host second 140 it captured
390,334 FIFO bytes and 3,003 memory updates, bound the reference request to
frame **6868 / present 13737**, and flushed the complete 640×491 PNG. Visual
inspection shows riding at 34 mph. All three audits agreed on 9,774 commands,
2,874 primitives and 2,268 indexed XF loads; the full allocated RAM check
passed. This frame contains two PE tokens, seven EFB copies (one XFB), and
21 TMEM load/sync commands.

Normal guest execution continued to shutdown with zero GPU-command errors,
invalid accesses, unknown instructions, SMC failures or JIT fallback runs.
Host speed was below real time before capture and during continuation while
other builds were active; this is a correctness run, not performance evidence.

Evidence: `local/research/120hz/replay-correctness-acceptance-v2.json` explicitly
reports `capture_gate_passed: true`, `replay_accepted: false`; the completion
receipt is `replay-correctness-delivery.json` in the same folder. The reference
PNG SHA-256 is `1009caf0f5d3c19bfaf771d9e383176111746df7ccc9dfa5605a834e5de581aa`.
Six asset-independent regressions pass, in addition to the offline actual
pinned-decoder checks and live capture/continuation check.

### Running the bounded capture

Use fresh output and profile names. The captured FIFO is written beside the
JSONL trace as `EVENTS.jsonl.fifo`. Do not enable `SSX_NATIVE_SCHEDULE`.

```sh
python3 tools/gamecube_native_trace.py build --scheduler --replay \
  --game local/game/gc-gari-027 --output local/research/120hz/replay-capture-player
SSX_NATIVE_REPLAY=1 \
SSX_NATIVE_PROBE="$PWD/local/research/120hz/replay-capture-events.jsonl" \
python3 tools/gamecube_schedule_check.py \
  --player-dir local/research/120hz/replay-capture-player \
  --immediate-xfb --resolution 640x528 --game local/game/gc-gari-027 \
  --profile replay-capture --output local/research/120hz/replay-capture-run --seconds 180
python3 tools/gamecube_replay_check.py --capture-only \
  --events local/research/120hz/replay-capture-events.jsonl \
  --reference local/native/profiles/replay-capture/ScreenShots/GXBE69/native-replay-reference.png
```

## Next runtime boundary: isolate rendering before enabling replay

The following inventory comes from the pinned Dolphin source, especially
`VideoCommon/OpcodeDecoding.cpp`, `BPStructs.cpp`, `TextureCacheBase.cpp`,
`XFStructs.cpp`, `VertexLoaderManager.cpp`, `Present.cpp` and
`Core/HW/PixelEngine.cpp`. It is a starting inventory, not proof of an exhaustive
side-effect audit.

| Current path | Persistent/guest-visible effect | Required replay boundary |
| --- | --- | --- |
| BP token/draw-done | PE state and scheduled CoreTiming completion/interrupt events; also flushes deferred EFB copies | A replay execution policy must suppress PE/timing signals while retaining necessary replay-local GPU flushes. Suppression only at the scheduler is too late. |
| EFB texture/XFB copies | Writes/defers writes into guest RAM, creates and mutates texture-cache entries, may reuse earlier EFB content | Route all copy destinations and deferred completion to owned replay memory/cache resources; preserve initial color/depth contents or prove their complete reconstruction. |
| XFB copy and presenter | `after_frame` listeners, cache aging, statistics, recorder callbacks, immediate presenter counters and VI state | Separate replay frame/present events and resources from the live event bus. Ordinary game/VI/recorder completion must not advance. |
| Vertex/indexed-XF/texture/TLUT reads | Uses MemoryManager pointers and cached vertex-array/texture addresses | An explicit replay memory provider must cover every indirect read. Reject any path that resolves to live RAM, including cached pointers. |
| BP/CP/XF/TMEM, shaders, batches, bbox, queries | Mutates global registers, dirty flags, pending batches, bounding-box/query state and EFB/cache contents | Replay-owned render context, or a fully audited save/restore transaction covering all of these domains, not only a register prelude. |

First add an isolated FrameDumper observer that carries `frame_number` through
`DumpCurrentFrame` to the PNG encoder and records the successfully saved image's
frame ID. The no-FFmpeg build currently discards FrameState in `FetchState`.
That observer can close reference-image provenance without changing the phone
or the vendor checkout; a missing/mismatched encoder ID must reject fidelity.

The smallest safe **replay fidelity** experiment is a separate process/runtime that
loads the captured FIFO and renders to its own resources, then compares the
result with the exact original PNG. Its PE/RAM/cache effects cannot escape
into the paused game. That can establish image fidelity before designing a
shared-runtime replay context for the phone; its timing is not a phone speedup.

A shared-runtime spike should start with an explicit `ReplayContext` carrying
a memory provider and execution/event policy, then instrument the inventory
above with unexpected-access/event counters that fail closed. Restore the
captured initial render state before **each** candidate replay. Gate progress
on original-frame equality, unchanged guest/event state and clean normal-frame
continuation; only then add two-frame camera/rider transforms and measure
render cost separately from drawable/display throttling.

## Historical motivation and prototype (not current acceptance)

The phone trial without guards measured the guest re-entry mechanism directly:
an extra draw costs a median 11.3 ms of wall time against 11.5 ms for a real
frame, so that unguarded run of 60 Hz simulation plus extra draws ran at about
0.6 speed. Later guarded phone trials confirmed short high-refresh sections
at normal game speed; sustained headroom remains unproven. The initial result
does not rule out further optimisation of guest-side rendering.

**Direction:** produce the extra frame on the host. Retain the last frame's
GP command stream, re-run it through the video pipeline with the camera (and
later the pose palettes) transformed as matrices are loaded, and present the
result. A replay executes no guest code; its cost is the host-side decode and
GPU work only.

## Mechanism

- **Capture.** Dolphin's `FifoRecorder` is compiled into the runtime. It
  records every GP command between two `after_frame` events plus the memory
  regions those commands read (vertex arrays, indexed XF loads, display lists,
  texture data) and the initial BP/CP/XF/TMEM state. A frame is available as
  `FifoDataFile::GetFrame(0).fifoData`.
- **Replay.** `OpcodeDecoder::RunFifo<false>` decodes an arbitrary buffer with
  the normal callbacks, so the recorded bytes drive the same vertex loading,
  state changes, draws and the frame-ending EFB→XFB copy. With immediate XFB
  the copy presents. In single-core mode this runs on the CPU thread while the
  guest is parked at its idle seam.
- **Transform.** `XFReplay::g_transform` (authored hook in `XFStructs.cpp`) is
  called after each write into XF matrix memory, direct or indexed, with the
  word address and count. GX folds the view into every position matrix the
  game uploads, so a camera change is `M' = Δ · M` applied to each 3×4 position
  matrix as it lands, exactly the `camera_delta` math the interpolation
  prototype already uses on the guest side. Normal matrices take the rotation
  part. The first milestone applies a translation only.

## Milestone 1: reversible camera change from a replayed frame

`native/diagnostics/native_frame_replay.h`, built with
`gamecube_native_trace.py build --scheduler --replay` and enabled with
`SSX_NATIVE_REPLAY=1`. In the experimental window it requests a screenshot of
the next frame, records that frame, then replays it once per idle-seam visit:
40 as recorded, 40 with +500 on every position matrix's first translation
component, 40 as recorded. Screenshots are requested at replays 20, 60 and
100. Acceptance: the original and the two unmodified replays are byte-identical
PNGs; the offset replay differs; replay wall time is recorded per replay.

Known limitations of this cut: the replay reads vertex, display-list and
palette data from live guest RAM rather than from the recorded memory updates,
so it is only valid while the guest is not writing those regions (the guest is
paused at the seam during the replay, but the game advanced between recording
and replay); the initial video state is not restored before the replay; and
the transform is a translation, not an interpolated camera. Those are the next
three steps, in order, followed by rider/board palette interpolation using the
identity work from the pose prototype, and then phone measurement.

## Milestone 1 results (September 13, evening)

Third run (`local/research/120hz/replay3-*`, profile `replay-3`, 640x528,
immediate XFB): one frame recorded during riding at host second 140, then the
whole sequence executed in one idle-seam visit with the guest paused.

| Observation | Value |
| --- | ---: |
| Recorded GP command bytes | 619,886 |
| Recorded memory updates (vertex, XF palette, texture, TMEM) | 6,061 |
| Restore prelude bytes (BP, CP, XF memory and registers) | 19,719 |
| Replays completed | 120 of 120 |
| Position matrices rewritten per offset replay | 2,037 |
| Wall time per replay, median | 16.65 ms |
| Replay 20 vs replay 100 (both unmodified) | byte-identical PNG |
| Replay 20 vs replay 60 (+500 translation) | 312,676 of 314,240 pixels differ |

The unmodified replay is a complete render: terrain, rider, board, snow
spray, trees, gates and the HUD all present, and visually the same scene as
the screenshot taken one frame earlier (race timer 00:00:15 against 00:00:16).
The "original" capture is therefore one frame early; a same-frame comparison
still needs the screenshot request moved to the retrace before the recorded
frame. The offset replay shifts the world and the camera-centred backdrop and
also moves the HUD, because the translation was applied to every position
matrix; HUD draws (orthographic projection) and camera-centred backgrounds
need the same exclusions the pose prototype already applies.

The 16.65 ms per replay is the display, not the work: each replay ends with
the XFB copy and an immediate present, and the Metal drawable pool throttles
120 presents in 1.9 s to the 60 Hz screen. The single replay in the second
run, which was not display-bound, took 4.06 ms including its present, so the
decode-and-submit cost on this Mac at 640x528 is a few milliseconds at most.
A proper measurement needs presentation suppressed or GPU timestamps.

The second run showed why state restore is mandatory: replaying with the live
CP state of a later frame desynchronised the decoder (unknown opcode 0xE9),
because draw command sizes depend on the vertex descriptor. The third run
restored the recorded state before replaying and then left it in place, and
the game's own stream desynchronised afterwards for the same reason. The
fourth run (`replay4-*`, profile `replay-4`) saves the live BP/CP/XF/TMEM
state before the sequence and restores it after (`RestoreLive`): 120 replays
again (718,724 recorded bytes, 7,516 memory updates, 2,157 matrices rewritten
per offset replay, unmodified replays byte-identical, offset replay different),
then the game continued at speed 1.001 with zero GPU command errors, zero
invalid accesses and a passing course check.

These historical captures demonstrated repeatable images and reversible camera
movement in one scene. They did not establish equality to the exact original
frame or isolation of RAM, completion events, FIFO/XFB and persistent GPU state.
The current correctness gates above supersede the earlier plan to try this
prototype on the phone.
