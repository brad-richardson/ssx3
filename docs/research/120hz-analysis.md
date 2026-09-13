# 120 Hz investigation — September 13, 2026

The [imported handoff](ssx3-120hz-handoff-2026-09-13.md) is preserved verbatim
from Downloads. Its external claims are a research snapshot, not results from
this repository. No timing changes have been deployed to the phone.

## Initial local findings

- The local GXBE69 executable matches both this project's SHA256 pin and the
  handoff's SHA1 `5aae61dc3bd5c7abb92d158c4477f1a9ca4de385`.
- Retrieved the complete GameCube symbol map at the handoff's pinned revision.
  Many relevant routines still have anonymous names; the PS2 replay symbols
  cannot simply be translated to GameCube addresses.
- `0x801CD33C` is a strong application-loop candidate: it calls the named
  `cAppMan::checkHalt`, dispatches virtual callbacks, loops through state
  handling, and is entered from `0x801CD750`.
- `0x801CD750` initializes an object field at offset 20 to 60 and passes it
  to an execution-manager callback. This is a scheduling lead, not proof that
  changing it to 120 preserves gameplay. It is an initialization/entry routine,
  not established as a constructor.
- `0x801CD248` advances an accumulator at offset 44 using offset 40, derives
  an integer callback count, and invokes a virtual callback that many times.
  Trace the actual callback targets and timestep consumers before labelling
  this a physics update or rendering hook.
- The app's existing frame-interval metric uses Dolphin's after-frame event.
  It is not a measurement of display presentation, nor a direct count of game
  simulation steps. A state restore can also emit this event.

Local-only evidence: `local/research/120hz/static-hook-manifest.json` contains
fingerprints and original-byte checks for candidate hooks. The downloaded map
and game disassembly remain excluded from version control.

## Existing prototype

The separate `spike/120hz` worktree contains a color-only frame-generation
prototype. Its README's later measurement section supersedes its older
"not run" introduction. Recorded September 11 Mac results at 1556×966:

| Metric | Native presentation | Color-only prototype |
| --- | ---: | ---: |
| Game FPS | 59.4 | 4.9 |
| Emulation speed | 0.99× | 0.36× |
| Displayed frames/s | 58.9 | 8.1 |
| Synthetic frame GPU cost | — | 10.4 ms average |
| Real-frame submit-to-present | 46.3 ms average | 204.9 ms average |

These results reject that implementation, not all interpolation. They are
neither iPhone measurements nor measurements of true higher-rate simulation.
The only explicit `waitUntilCompleted` in the inspected FrameGen implementation
is in its destructor. The older notes' claim of a per-frame explicit wait is
not supported by this source. The frame loop instead acquires two drawables
before committing their command buffer. Measure drawable acquisition and
presentation backpressure separately; moving work into completion callbacks
alone is not a demonstrated fix.

The prototype also runs motion estimation at the host backbuffer size. Its
1.5-million-pixel test is about five times the pixel count of 640×480; the
reported cost is not a native-resolution or iPhone benchmark. This is a reason
to test a bounded-resolution pipeline, not to predict a fivefold speedup.

## Next decision gate

Continue separating guest updates, game renders, VI events and actual host
presents. The baseline below measures two application counters and display
presentation; it does not directly count physics substeps or all guest renders. Resolve the virtual callbacks above and
inspect whether repeated draws advance animation, RNG, trails or streaming.
Only then compare native higher-rate updates against render-state interpolation
and depth-assisted image interpolation. A displayed FPS counter alone cannot
establish smoother, distinct scene frames or preserved gameplay.

## Resolved callback boundaries

The read-only run observes the global application manager through `0x803DA9D8`.
Its vtable is `0x802E5468`; the active application's vtable is `0x802E543C`.

| Boundary | GXBE69 address | Evidence / limitation |
| --- | --- | --- |
| Timer callback wrapper | `0x801CD144` | Loads the singleton and calls the accumulator routine |
| Accumulator callback | `0x8010EEA0` | Resolved live from manager vtable offset 32; leads to a buffered multi-channel reader |
| Buffered work availability | `0x8010EECC` | Resolved live from manager vtable offset 28; consumes buffer entries and loops over four channels |
| Application update candidate | `0x8010550C` | Active application vtable offset 28; called after incrementing manager offset 32 |
| Application render candidate | `0x8010A4C8` | Active application vtable offset 32; independently gated in the main loop |

The buffered reader (`0x801D14C4`) fills records and advances a 30-entry ring;
`0x801D158C` advances its consumer. The four-channel handling is consistent with
controller input, not proof of a physics substep. A counter's name in the
experimental observer is a working label, not a recovered game symbol.

The update and render candidates are both substantial routines with mutable
state and many calls. Their separation is encouraging, but it does not prove
that the render candidate is safe to invoke twice. No render-side-effect audit
or timestep-normalization experiment has been performed yet.

## Feasibility recommendation

**First implementation candidate: preserve the original game updates and test
GPU frame interpolation on iPhone, with a strict frame-pacing budget and a
native-rate fallback.** Prefer MetalFX as the first Apple backend if the target
GPU reports support. It avoids writing an optical-flow model or fully retaining
the game's scene. It still requires validated depth, motion and UI separation;
this is a promising experiment, not an established drop-in feature.

The installed iPhoneOS 26.5 SDK exposes `MTLFXFrameInterpolatorDescriptor`,
`supportsDevice:`, previous/current color, depth, motion and separate UI inputs.
Apple describes those requirements and the need for explicit frame pacing in
[its frame-interpolation session](https://developer.apple.com/videos/play/wwdc2025/211/).
The app currently supports older iOS versions too, so runtime availability and
GPU capability checks must keep ordinary presentation working.

Use the renderer's EFB depth access as a starting point. GX position matrices
may already combine object and camera transforms, and some vertices carry
matrix indices; a single assumed camera matrix will not cover rider animation.
Depth clears, projection changes, transparent snow and thin rail geometry must
be checked in actual captures. Orthographic projection alone is not a reliable
HUD classifier. UIKit touch controls are already outside the game image, but
the game's speed/score/boost HUD is inside it.

Rank the other paths as follows:

1. **Render-state interpolation:** best long-term control over geometry and
   visual quality, but higher engineering cost now. There is no verified
   immutable scene snapshot or GameCube replay seam. Replaying FIFO commands
   is not equivalent to re-rendering scene state from a new camera, and doing
   two full draws repeats CPU vertex work in this no-JIT renderer.
2. **True 120 Hz game updates:** now has specific scheduler/callback leads,
   but carries the largest gameplay-validation burden. The original callback
   rate does not identify every physics substep, timer or animation update.
   A universal change from 60 to 120 is not justified by this investigation.
3. **Custom learned interpolation:** defer. First establish whether a standard
   backend and correctly formed motion/depth inputs work. There is not yet
   valid 60→120 training ground truth or a mobile inference budget.

Before implementing interpolation, run a presentation-only cadence probe on
the phone: measure drawable waits, GPU work, real displayed timestamps and
missed deadlines, with bounded buffering. Duplicated frames are acceptable as
a scheduling control, but must never count as a 120-fps visual success. Then
add one midpoint from two frames at bounded resolution, separate the HUD, and
inspect cuts, rails, rider tricks and snow spray. Keep input and simulation
untouched. Any budget miss returns to the real frame without building a queue.

The Mac's 60 Hz display can validate overhead and scheduling failure modes;
it cannot establish sustained 120 Hz presentation on the iPhone. No phone
installation or high-refresh acceptance claim is part of this analysis.

## Measured unchanged baseline

Two isolated 200-second Garibaldi 027 runs completed with native execution and
no invalid-access or GPU-validation failures. The first uses the production
player; the second adds read-only Metal presentation probes. Over the same
140–190 second observer window, the configured rate remained 60 and the
accumulator scale remained 1.0:

| Observation | Production player | Presentation observer |
| --- | ---: | ---: |
| Timer callback counter per host second | 59.24 | 59.67 |
| Application update counter per host second | 59.24 | 59.67 |

These are host-wall rates of specific counters, not measurements of every
physics substep. The two runs used the same recorded input sequence but their
rider paths diverged; this has not established deterministic replay or
physics-equivalence tolerances. That matters before any timestep experiment.

The observer's active-course display window (140–185 seconds after its first
submission) at a 1556×934 backbuffer on the Mac's 60 Hz screen measured:

| Metric | Mean | 95th percentile |
| --- | ---: | ---: |
| Display interval | 16.90 ms | 29.13 ms |
| Drawable acquisition wait | 0.016 ms | 0.021 ms |
| Submission to actual display | 17.35 ms | 28.69 ms |
| Final render command buffer GPU time | 7.82 ms | 14.04 ms |

Actual display rate was 59.18 Hz: 2,664 callbacks with nonzero display timestamps
from 2,696 submissions in that window. Zero-timestamp callbacks are excluded
from displayed-frame counts. GPU time covers the command buffer present at
`PresentBackbuffer`, not necessarily every command buffer that rendered the
scene. Submission-to-display is not input-to-photon latency.

This baseline supplies no evidence of enough spare GPU time to simply double
full-resolution rendering. It also shows that drawable acquisition is cheap
in the normal one-frame path. The older two-frame stall needs an isolated
scheduling test; it cannot be attributed to normal single-frame acquisition.
These Mac timings do not substitute for iPhone measurements, and the modest
run-to-run difference is not an observer-overhead guarantee.

The reusable observer builder is `tools/gamecube_present_trace.py`. It compiles
one instrumented copy of the public Metal backend into a separate player,
leaving production sources and binary intact. All copied backend source,
objects, executables and raw captures stay under ignored `local/`.

```sh
python3 tools/gamecube_present_trace.py --output local/research/120hz/new-player
# Set this only on an isolated test player, with a new output path:
# SSX_PRESENT_TRACE=/absolute/path/to/local/present.csv
```

Evidence: `local/research/120hz/baseline-{1,2}/`,
`baseline-2-present.csv`, `baseline-summary.json` and
`present-player/build.json`. The timing observer is exploratory; counters and
callback identities must be revalidated against any different executable.

## Android portability decision

MetalFX is one optional Apple backend. Keep the frame-input contract and game
instrumentation shared: previous/current color, depth, motion with explicit
coordinate conventions, UI coverage/composition, simulation timestamps and
history-reset reasons. Native GPU resource handles and synchronization stay
inside each graphics backend. Camera cuts, respawns, resize and missing history
must use the same fallback rules on both platforms.

For Android, start with the existing Vulkan renderer and a native app/runtime
baseline. The Android shell is still backlog work; the current Odin workflow
uses Dolphin. A patched course archive cannot add frame generation to stock
Dolphin. We would need our Android runtime or a renderer-modified Dolphin build.

Use two independently measured parts:

1. **Presentation:** request a supported high refresh rate and pace actual
   submitted images. Android's [Swappy library](https://developer.android.com/games/sdk/frame-pacing)
   supports Vulkan presentation timestamps and synchronization. It schedules
   frames; it does not synthesize intermediate images. Android also documents
   [explicit refresh-rate requests](https://developer.android.com/games/optimize/display-refresh-rate-change)
   for games above the default rate. Measure the selected mode and actual
   display intervals rather than assuming a 120 Hz request is honored.
2. **Interpolation:** first benchmark depth/motion-assisted Vulkan compute at
   bounded resolution using the same captured sequences as the Apple backend.
   This would be an implementation experiment, not a verified Android equivalent
   of MetalFX. If motion-boundary quality is inadequate, evaluate a pretrained
   model before considering training. [MNN](https://github.com/alibaba/MNN)
   documents Android plus Vulkan/OpenCL GPU inference; model operators,
   texture interop, CPU fallbacks, latency and sustained device performance
   still need validation. No Android interpolation backend is selected as
   production-ready by this analysis.

If equal iOS/Android feature availability is required, benchmark the portable
Vulkan candidate early alongside the MetalFX trial. An iPhone-only success
cannot establish Android feasibility. Share input capture, motion/depth
reconstruction and correctness tests; allow platform-specific interpolation
implementations and performance settings. Use native-rate presentation when
the device cannot sustain the interpolation budget.
