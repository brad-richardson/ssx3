# Host-side frame replay — September 13, 2026

Follow-up to the [pose interpolation prototype](120hz-native-interpolation.md).
The implementation review supersedes the initial acceptance claims below:
this prototype is isolated research and is not enabled in the phone app.
It still applies memory updates before their recorded FIFO positions, overwrites
live guest RAM without restoring it, restores starting registers only once for
the replay sequence, and may trigger guest-visible completion effects. Its
reference capture is one frame early. Exact-frame fidelity, memory/event
isolation and per-replay state restoration are required before phone replay.
See the [review follow-up](120hz-review-followup.md) for the current gate.

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

Established: a guest frame can be captured and re-rendered on the host with
no guest execution, deterministically, with a reversible camera change. Next,
in order: restore-then-continue validation on the phone, HUD and backdrop
exclusion, a real camera delta from two consecutive frames instead of a
translation, then interpolation of the rider palettes using the ownership
mapping from the pose prototype, then cost measurement without display
throttling.
