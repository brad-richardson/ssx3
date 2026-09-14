# Working todo

Living list, most recent first within each section. Move items to Done with
the build or commit that closed them.

## Now

- [ ] Follow the [September 12 architecture priorities](architecture-review.md):
      validated imports, state-aware route checks, and explicit course ownership.
- [ ] Restore donor fog/backdrop and check remaining visual differences at
      matching camera poses. Build 013 fixes the demonstrated 1×/2× terrain
      lighting mismatch; see the [comparison](garibaldi-visual-comparison.md).
- [ ] Capture jump approaches with camera/rider coordinates and visible patch
      IDs; distinguish actual late terrain visibility from low-contrast slopes.
- [ ] Check uninterrupted route progress, checkpoints and finish after resets;
      a results screen alone is not full-course acceptance.
- [ ] Control mapping doc (partly done in `native/ios/README.md` Controls): one table of action → GameCube input → Xbox pad →
      touch control, kept in `native/ios/README.md`.
- [ ] Odin: test the GameCube Garibaldi in Dolphin for Android; the disc
      builder is done, the handheld run is not. `gc-gari-009` (own textures,
      full race line) is on the share under `ssx3-workbench/builds/`.
- [ ] Odin: pair it with adb once (wireless debugging or USB) so
      `tools/deploy_odin.py` can push future ISOs straight to Dolphin's game
      folder; confirm which folder Dolphin scans on the device.
- [ ] 120 Hz: profile active callback CPU work, then reduce the dominant cost.
      Phone build 1747c62a measured 8.45 ms thread CPU within an 8.64 ms median
      extra draw (52 samples). Build 971dc928 verifies 1×/2× detail changes;
      its Half-output 2× trials reach 102.94/112.67 positive displays/s over
      8.92/18.38 seconds, but the longest warmed span is only 15.88 seconds
      at 114.34 displays/s. Half-output 1× smoothing is still unmeasured.
      Course/trajectory differences prevent a causal output-size comparison.
      Preserve the three legacy app-span alerts and lifecycle clock unknowns
      without loosening guards. The newer Garibaldi-only 113c9b20 run preserves
      all 494 extras, including the new ownership fields, but its three Match/2×
      trials end through load protection after 3.49–13.55 s. No sustained pass.
      Short high-refresh bursts are established, but sustained pacing and
      distinct interpolated motion remain open. See
      [resolution evidence](research/120hz-output-resolution.md) and
      [CPU/config spikes](research/120hz-cpu-overhead-spikes.md). The new
      [ordinary-frame profile](research/normal-frame-cpu-spike.md) attributes
      72.5% of sampled desktop CPU-thread self work to generated guest code
      (14.5% named FP/conversion helpers included), with 6.6% inclusive software
      vertex conversion. Next: phase-tagged phone attribution and one narrow,
      equivalent helper optimization; desktop 3× shares are not phone timings.
- [ ] Phone: compare 75%, Match internal and Half output on the same route
      at fixed internal detail; verify Match through menu 1× ↔ 2× changes.
      Build 113c9b20's phone run confirms Match/2×: output 1947 × 896,
      visible picture 1556 × 896, EFB 1280 × 1056. The picture looked fine;
      label these stages clearly. Audio inside-snapshot zeros do not prove
      full-trial continuity. See [resolution evidence](research/120hz-output-resolution.md).
- [ ] Replay: bind captures to the actual encoder frame, prove exact-image
      fidelity in an isolated renderer, and complete owned-memory/ordering
      gates before live replay or more interpolation. The private FIFO audit
      and 180-second capture/continuation check pass, but screenshot-request
      identity does not prove the encoder's frame identity or render fidelity.
      Carry the frame ID through FrameDumper, then compare a separate-runtime
      replay against that exact image. Phone replay remains disabled. See
      [replay evidence and remaining boundaries](research/120hz-host-replay.md).
- [ ] Make MemoryWatcher reads observational: replace unchecked HostRead
      pointer chasing with checked reads. Failed watches can reach a panic
      path that raises a PI interrupt. The 031 river check logged 48 startup
      warnings; the compiler comparison also saw warnings during gameplay
      under both O2 and O3. Preserve their distinction from guest faults while
      eliminating the observer side effect. See
      [collision diagnostics](gamecube-collision.md).

## Garibaldi in the GameCube engine

- [x] Collision priority 1: restore terrain reset recovery, including the river
      beneath the late bridge reported at 89% on iPhone build 021. Convert
      source physics/effect bindings and verify reset destination; preserve
      valid riding on the bridge above. Source inventory is in
      `local/evidence/garibaldi-visibility/collision-backlog-audit.json`.
      Build 027 combines the 622 authored reset patches' correct SSX 3 reset
      flag with grounded recovery paths separate from airborne racer paths.
      Normal-course, 64% waterfall, late river and upper-bridge native checks
      pass, with stable recovery and no loops. Supersedes 023's wipeout
      mapping and 025's airborne-path regression. Installed on iPhone with
      matching checksum readback on September 13.
      See [collision evidence and format notes](gamecube-collision.md).
- [ ] Original water physics/effect callbacks remain separate from terrain
      recovery; translate them for response at water height.
- [ ] Collision priority 2: validate broader static obstacle encounters and
      deliver candidate 031 separately from phone performance comparisons.
      The rigid-transform fix restores the engine's collision inverse while
      preserving rendered placement: a matched rock fixture now has 22
      positive contact returns versus zero before. Waterfall and river reset
      checks pass. This does not certify all 2,059 enabled instances or full
      course progression. Multipart shapes, scripted/physics objects and
      conservative reset-path clearance omissions remain explicit. Phone
      assets remain 027; see [collision evidence](gamecube-collision.md).
- [ ] Preserve donor terrain surface behavior through a verified profile:
      direct reset-flag mapping is implemented in build 025; snow/powder/ice/
      rock and non-colliding patches still inherit one target header. Do not
      assume the two games share enum values.
- [x] Build 022 compiler fix: honor initial GSF visibility and authored
      post-countdown gate removal. Removes 51 erroneous draw instances;
      timed donor gate animation remains future gameplay work.
- [x] First static scenery pass: gc-gari-020 imports 621 models / 3,290
      placements and is installed on the iPhone with checksum readback.
      Native riding verified; phone test launch is blocked by the locked
      device. See [scenery scope and evidence](gamecube-scenery.md).
- [ ] Breakable glass/blocks: translate authored break behavior and effects;
      user confirmed objects remain intact on impact (Sep 13).
- [ ] Restore the Garibaldi start gate and countdown lights; user reconfirmed
      they are missing on iPhone on September 13 (assets 027). The three gate
      models are supported static geometry, deliberately omitted by 022;
      restore their timed visibility/flipbook binding, not general mesh
      animation. Validate the suspected GC flipbook halfword-order mismatch
      and target `StartgateOpen` dispatch, then check countdown, unobstructed
      GO and restart. Keep hidden helper geometry excluded. See the
      [source audit and next spike](gamecube-scenery.md#start-gate-audit-september-13-assets-027).
- [ ] Complete donor scenery lighting/material flags, animated/multipart
      models, grind splines and object collision.
- [x] Build 021: reusable donor rail reader/encoder, topology and distance
      checks, and a separate 169-path Garibaldi candidate. See
      [rail conversion](gamecube-rails.md).
- [ ] Validate rail mounting, curved traversal and transfers; verify the
      diagnostic sound/effect binding. Build 021 is installed on iPhone at
      the user's request with checksum readback; user confirmed gate rails work on Sep 13. Curved traversal/transfers still need checks.
- [ ] Isolate host scenery, including content streamed from adjacent locations;
      dropping the target's kind-2 models alone is only a probe.
- [ ] Course name and description in the GameCube frontend (DOL/locale edit).

## Controls

- [ ] Virtual controller: explore dedicated Grab 1/2/3/4 buttons for useful
      shoulder-button combinations that are difficult or impossible on touch;
      consider replacing the individual shoulder buttons. User request Sep 13.
- [ ] Virtual controller: support boost held together with jump preparation;
      audit simultaneous touch ownership and layout. Backlog, not urgent.

- [ ] Touch control for the C-stick (board press), currently unmapped.
- [ ] Optional DOL patch: four-input grab mask to restore the eight PS2-only grabs.
- [ ] Exercise the physical-controller path with a real pad (untested so far).

## Mobile

- [x] Fast cold start to the main menu: skip pending intro movies and advance
      once after the title's first active input pass. Enabled by default,
      including Full Reset, with ordinary-boot override and checkpoint restore
      precedence. Build 113c9b20 is installed. Three final Simulator launches
      reach the real menu at 20.47–20.53 s; the phone reaches it at 20.614526 s
      after guest execution begins. User confirms fast start worked great.
      See [startup shortcut](research/startup-shortcut.md).
- [ ] Phone: verify the persisted fast-start toggle, Full Reset and checkpoint
      restore combinations, with audio continuity. Required game initialization
      and the original title-readiness wait remain; profile them separately.
- [x] Direct menu choices for output/internal detail, staying paused for
      multiple changes, and remembered selections across launches. Initial
      Half output + 2× detail confirmed by the user. Build f40bfef6 installed
      on iPhone September 13 at 20:59 EDT. Simulator UI checks verify direct
      selections, Resume, post-resize trial readiness, Match dimensions and
      a fresh launch restoring saved 75%/1× instead of defaults. Explicit
      Full/1× launch overrides and independent preference storage pass.
- [ ] Phone: verify the redesigned menu's saved choices with checkpoint
      restore/Full Reset and ordinary audio; Simulator UI checks use Null
      audio and automated sessions omit checkpoints.
- [ ] Verify lifecycle Resume repair on iPhone: return to an automatic menu
      after background/audio interruptions; reconcile actual runtime state and
      explicitly reactivate audio on Resume. Reported stuck during Sep 13 playtest.
      Build 2250d8d9's subsequent session logs three resumes and three successful
      checkpoint saves, then one failed final save. Build c2e098d3 adds save-stage
      failure reasons and common timestamps; reproduce that failure and verify
      relaunch restoration. All eight subsequent diagnostic saves succeeded
      in 97–137 ms, so the earlier failure remains unreproduced.
      Build 1747c62a adds five successful saves and two output resizes/resumes.
      Build 971dc928 adds 16 committed saves and one explicit active-trial
      cancellation for pause with drain/restoration. Verify fresh-launch
      checkpoint restoration after changing detail and repeated background/
      audio interruptions; the one cancellation does not close those gates.
      The later 113c9b20 phone session adds ten committed saves.

- [x] Menu with in-memory Resume, background checkpointing and restore across
      relaunches; Full Reset recreates the runtime and reloads files. Installed
      on iPhone; race restore and reset verified in the simulator. See
      [iOS notes](../native/ios/README.md).
- [ ] Profile cold startup separately: runtime initialization, full asset
      hashing, memory-card checking and course loading. Separate actual I/O,
      decompression/resource initialization, emulated DVD/card delays and UI
      timers. The isolated six-run FastDiscSpeed comparison reduces median
      Mac startup to menu from 20.10 to 14.85 s (26.15%), with complete startup
      states and runtime checks. Next: an explicit phone comparison, then
      course-load phase anchors; no phone default change or memory-card/course
      speedup is established. See [loading spike](research/loading-speed-spike.md)
      and [phase separation](research/startup-shortcut.md#loading-and-memory-card-follow-up).
- [ ] 15-minute sustained soak on the iPhone (thermal, audio starvation),
      deferred by the user; short functional checks take priority.
- [ ] Save / memory-card behavior on the phone, including read/write/relaunch
      and the checking-screen duration. Dolphin models asynchronous transfers
      at 512 KiB/s read and 96.125 KiB/s write; no simple fast-card flag is
      established. Measure before changing timing or completion ordering.
- [ ] Android native build (Vulkan backend, NDK toolchain); user has a dev
      account to configure. Not needed for the Odin while Dolphin runs the
      patched disc with JIT.
- [ ] Exception-vector interpreter fallback (0x0C00/0x0500): measure, then
      translate or hook if phone timings need it.

## Done

- [x] 2026-09-12 gc-gari-013: identify the terrain lightmap scale mismatch
      across 108 matched image pairs, add a shared engine material profile,
      preserve source images and conversion receipts, test every RGB565 color,
      and capture the corrected native gameplay. Add reusable isolated draw
      capture/comparison tools; see [material conversion](gamecube-materials.md).
- [x] 2026-09-12: capture original PS2 and GameCube Garibaldi alongside build
      012; preserve a side-by-side gallery and source/hash manifest. This
      confirms remaining color/environment differences, not visual acceptance.
- [x] 2026-09-12: correct global image allocation/capacities, remove obsolete
      host occlusion curtains, and conservatively bound curved terrain. Add
      archive-wide image validation and regression tests. See build findings
      in [the GameCube notes](gamecube-world.md).
- [x] 2026-09-12: reject native test runs with zero native execution, invalid
      memory accesses, or failed code verification.
- [x] 2026-09-11 gc-gari-009: full donor race line on the track chain, gates
      and opponents on Tricky's six start paths, regenerated kind-21 race-line
      table (`tools/race_course.py`); the meter starts near 0% and opponents
      ride the course.
- [x] 2026-09-11 gc-gari-008: Garibaldi's own textures and lightmaps from the
      GameCube Tricky `.gsh` sheets (`tools/gamecube_textures.py`); the race
      rides with zero invalid accesses. September 12 correction: reclamation
      still collided with other locations, and the apparent limit near 800
      was an unexpanded global table. Lightmap correlation supports the same
      cell orientation; the September 12 rendered comparison confirms that
      brightness/color fidelity remains open.
- [x] 2026-09-11 Xbox prompt glyphs: `tools/patch_ui_glyphs.py` repaints the
      B/X/Y icons in the three UI sheets; in-game menu shows green A and blue X.
      Installed on the phone, in the gc-gari-005 disc root and the shared ISO.

- [x] 2026-09-11 `tools/build_gc_iso.py` rebuilds a GameCube ISO; stock FST
      reproduced byte for byte.
- [x] 2026-09-11 Touch overlay relabelled to Xbox positions (A bottom, B right,
      X left, Y top, LB/RB).
- [x] 2026-09-11 gc-gari-005: first rideable GameCube Garibaldi (race start,
      ride, restart, zero invalid accesses).
- [x] 2026-09-11 Two-stick touch overlay; right stick drives the D-pad for spins.
- [x] 2026-09-11 PS2-position physical pad mapping with grab translation.
- [x] 2026-09-11 iPhone smoke run at 60 FPS, no JIT.
