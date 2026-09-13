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
The synchronous wait and two-drawable scheduling need separate attribution;
removing a wait alone does not establish a viable 120 Hz pipeline.

## Next decision gate

Count guest updates, game renders, VI events and actual host presents
separately on an unchanged baseline. Resolve the virtual callbacks above and
inspect whether repeated draws advance animation, RNG, trails or streaming.
Only then compare native higher-rate updates against render-state interpolation
and depth-assisted image interpolation. A displayed FPS counter alone cannot
establish smoother, distinct scene frames or preserved gameplay.
