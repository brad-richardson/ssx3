# Working todo

Living list, most recent first within each section. Move items to Done with
the build or commit that closed them.

## Now

- [ ] Visual remaster with trained upscalers (user, September 14; SSX 3 first,
      the PS2 games after). Hybrid pipeline, not "an image model upscales the
      game": classify assets → dedicated super-resolution per asset family
      (PBRify DAT2/SPAN, Real-ESRGAN baselines) → generative restoration only
      for a hand-picked top slice → automated QA → repack in the engine's own
      texture formats. Hardware: RTX 4070 12 GB available now, a 64 GB M5 Pro
      mini arrives the week of September 21 as orchestrator. First experiment:
      ~30 representative SSX 3 textures across environment, snow, clothing,
      boards, UI and effects, run through Lanczos / Real-ESRGAN / PBRify SPAN /
      PBRify DAT2, then put back in the actual game, not just contact sheets.
      Fact-finding done September 14, see `local/research/texture-remaster.md`:
      prototype **runtime replacement keyed by texture hash** first, not
      archive repacking. The native GPU backend already carries most of it
      (`texture_replacement.cpp`, PNG/DDS loaders, a 4 GB LRU cache) with no
      caller yet; the remaining work is a pack-directory flag, a dump flag, and
      the lookup in `gxcore_draw.cpp`'s texture resolve, about 2-4 days. The
      one real decision is reconciling the gxcore content hash (XXH3 over GX
      bytes + TLUT) with the dump-filename key (XXH64) so packs stay portable
      with Dolphin's convention. Repacking into archives needs CMPR/RGB5A3
      encoders, a GX tiler, a mip writer and a palette quantiser that do not
      exist, and ARA1 already sits near the 24 MiB wall. The 30-texture
      experiment and tooling gaps are itemised in the report.
- [ ] Course selection for added tracks (user, September 14): a menu or
      selection path that lists every imported course so new tracks can be
      added without a rebuild and without replacing a stock event. Today
      Garibaldi replaces Snow Jam's event and inherits its script slot, name,
      description and location tables. Fact-finding first: how the frontend
      enumerates events/locations, where names and descriptions come from
      (see [locale tables](locale-tables.md) and
      [peaks and locations](peaks-and-locations.md)), and whether the tables
      can grow in place or need a DOL patch. Design later.
      Fact-finding done September 14, see
      `local/research/course-selection.md`: the event table (23 x 100 B at
      `0x802CE5EC`) and location table (50 x 24 B at `0x802CEEE8`) abut each
      other and the next string with zero slack, so in-place growth is out;
      counts are hard-coded in a handful of enumerable sites (23 at
      `0x8005D638`, 50/49 at `0x801084B0`/`0x80109414`) plus `behiloc.dbb`
      and `bam.gdb`. The world archive name is the event record's `+68`
      string joined to `data/worlds/`, so a different archive loads by
      rewriting 16 bytes. Descriptions live in `cmnamer.loc` (little-endian,
      Snow Jam is index 508, no empty slots, hash function unsolved). Any DOL
      patch forces a module regeneration (`dol_sha256` is enforced).
      Recommended first step: keep Snow Jam's event row and let the native
      runtime patch the archive-name and title strings in guest memory at
      boot from a host-side manifest, then add a picker in the app's menu.
      Unknowns: file-name case folding on the FST, and whether the save record
      is a fixed event-indexed array.
- [ ] September 14 priority: course restoration is the main track; keep 120 Hz
      research bounded. First reprojection batch captured eight matching riding
      frames and demonstrated an offline half-step warp. September 14: a
      footprint splat closes 77-81% of the point splat's holes across five
      frame pairs, with static-wall MAE moving under 0.02 units. Absolute
      uncovered area is frame-dependent though: 0.44% on the calm frame 7559
      but 1.2-2.4% on the movie-driven 7500-7507 pairs, whose p95 motion runs
      76-128 px. Raster coverage is answered; near-field motion is not.
      The alpha HUD layer is now done: three movie-driven runs over natural,
      black and white backgrounds solve the tail exactly on all eight frames
      7500-7507 (7.04% coverage, mean alpha 0.727, every pixel within two
      levels of the untouched run). The EFB is RGB8_Z24 with no destination
      alpha, so a transparent render target could not have worked.
      Next: GPU-resident cost measurement, and near-field motion for the
      rider/board, which better rasterizing cannot address.
      No live smoothing mode or phone budget is established. See the
      [revised reprojection evidence](research/120hz-reprojection.md).
- [ ] Fast-FP needs route-controlled phone input before it can be measured.
      The [bounded pair](research/performance-batch2-followup.md) ran both arms
      cleanly on September 14 (186 s each, no fault, no JIT fallback, thermal
      nominal, 87 riding rows each) and is **inconclusive**: dual-core is not
      deterministic, so the two runs separate within three seconds of the race
      start and share only 4 of 86 riding seconds within 100 units, median
      separation 13,614. The 12.9% render-callback difference tracks a 10.5%
      draw-call difference and the update callback moves the other way.
      Repeating this design cannot settle it. Next: either a deterministic
      single-core arm, which isolates the compile option but is not the
      shipping configuration, or movie-driven input on the device. The
      historical desktop 1,022 control-register rows still match with the
      strict-provenance movie-hash gap unchanged. Baseline 94f5096e is now the
      installed phone build; the signed 53e2e1e4 archive is preserved.
- [ ] Performance: follow the [September 13 performance review](research/performance-review-2026-09-13.md).
      Done September 13: always-on callback timer, dispatch sampling opt-in,
      dual-core validated on Mac and phone (stadium section 0.89 → 1.00 speed,
      render callback 9.5 → 7.8 ms) and made the persisted default in build 1b.
      Batch 2 (same evening): movie-based determinism gate, chunk-granular
      lookup table, and the fast-FP module, matching baseline over
      1,022 sampled control-register rows (see September 14 provenance limit
      above); phone module built, measurement pending. Next: measure
      fast FP on the phone, fewer chassis round-trips, a 15-minute dual-core
      thermal soak at 3× (still deferred). The bounded
      [depth reprojection experiment](research/120hz-reprojection.md) uses
      the last frame's color, depth and predicted camera; 3× Match at
      100–120 with speed ≥ 0.95 remains a target, not a result. Helper
      micro-spikes are closed.
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
      at 114.34 displays/s. The newer f40bfef6 Garibaldi-only run measures
      Half/1× at 117.22 displays/s over its best 7.75-second warmed window,
      still too short with unresolved audio boundaries. Most collected thermal
      samples are serious; repeat a fixed route after returning to nominal.
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
      The [conversion spike](research/float-conversion-spike.md) passes all
      float32 bit patterns but trades call removal against code growth and
      rare-input regressions. Keep it scoped to a private hot-chunk build until
      workload evidence supports promotion. The independent
      [FMA classifier spike](research/float-arithmetic-audit.md) preserves full
      tested guest/host state; small, noisy timing gains do not justify a phone
      change. Existing phone builds already use optimized Release settings.
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
      September 14: original-position rock and sign fixtures produce 44 and 8
      positive engine contact returns with clean runtime checks. Player query
      ownership remains unknown; the tree fixture missed its obstacle.
      Next: a steered player encounter/query identity and route/bridge clearance.
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
- [ ] Scene animation is missing across the board, in three independent
      layers; the user reported no moving scenery on September 14 (direction
      arrows, block interactions, breaking glass, crowd). Measured against the
      donor NBD/GSF, not guessed:
      **(a) Animated and multipart prefabs are never imported.**
      `eligibility()` rejects them, so 102 of Garibaldi's 3,393 placements
      (3.0%) are absent entirely. These are missing objects, not still ones.
      September 14: every multipart donor model carries exactly one *meshless*
      part — a transform-free root (parent 0xffffffff, no matrix, no bounds)
      that the geometry hangs from. Counting it made models with a single
      geometry part look multipart, so the 102 split three ways rather than
      needing one big pipeline:
      **(a1) 13 placements needed nothing.** Models 132/133/153 are one
      geometry part, not animated, no local matrix. `geometry_parts()` now
      ignores transform-free empty roots and they import: 624 models / 3,303
      placements, up from 621 / 3,290. Models 133 and 153 are long tall
      banners (108 verts, extent 43x112x2470) whose materials carry a 2-frame
      flipbook on texture 61 — the best direction-arrow candidates in the
      donor. Model 132 is a 4-vertex quad flat in Y (3x0x1362), a ground
      decal.
      **(a2) done September 14: 64 of the 79 land frozen.**
      `--animated-as-static` admits a single-geometry-part animated model and
      imports its rest-pose display lists; `animated` only reports that the
      part names separate animation data, and the geometry is read the same
      way regardless. 641 models / 3,367 placements, up from 624 / 3,303. The
      receipt lists them as `animated_imported_as_static` so their presence is
      never read as animation support. The remaining three models (280-282,
      15 placements) carry a local matrix and now report `local matrix`,
      joining (a3) instead of hiding behind `animated`.
      **(a3) done September 14: `--compose-local-matrices`** lands all six
      models (647 models / 3,392 placements); build
      `gc-gari-scenery-localmatrix-001` rides a clean 180 s check (exit 0,
      zero faults). Visual confirmation of the rotated crowd figures is still
      unverified, and 49/86/90 add no drawn instances (all placements start
      hidden). Original scoping kept below.
      **(a3) 25 placements need local-matrix composition** — models 49/86/90
      (10, genuinely multipart: 23 geometry parts, 22 matrices each) plus
      280/281/282 (15, single part with a matrix). Scoped September 14 and
      **not** a quick win: strip vertices are index triples into globally
      shared position/uv/normal arrays written once for the whole import, so a
      local matrix cannot be applied in place without moving every other model
      that shares those positions. It needs transformed position copies, index
      remapping, a 16-bit signed range check against the model's 1x/4x scale,
      and the same composition mirrored in `gamecube_collision_import.py`,
      which re-derives and compares instance records. Model 32 (normal palette
      over 256, 1 placement) remains separate.
      **(b) Material flipbooks are staged but never sequenced.** 16 of 125
      donor materials carry a 2-5 frame flipbook, covering 74 placements;
      the countdown light is one of them (material 66, flipbook 5, five
      frames). The start gate work proves the images import correctly and
      that nothing advances them.
      September 14: SSX 3's own frame-sequence format is decoded and written.
      A plain 20-byte kind-0 material is marked by `mode == 0xffffffff`; an
      animated one appends a count and that many global image IDs. 25 of the
      archive's 2,687 kind-0 records are extended, consistently. `mode` is
      not an enable (the same two-frame sequence appears under 0, 1 and 2),
      so it is chosen by analogy: the only two five-frame records are the
      host's own countdown lights and both use mode 1.
      **Validated September 14: neither mode advances the sequence.** The
      mode 1 run is clean (896 samples, exit 0) and its light column holds the
      same lamp pattern through the countdown, as mode 0 does. The control is
      four mode 0 frames (16:09:32-35) showing an identical column; the
      apparent change in earlier crops is a translucent blue panel that tints
      the column at one camera angle, present in the first frame of both runs.
      The test was capable: donor images 69-73 are five distinct textures
      forming a progressive countdown (dim, red, +yellow, green last).
      Evidence in `local/research/startgate/flipbook-evidence/`.
      Writing the extended record is therefore necessary but not sufficient —
      something must drive the frame index and nothing in the course does, so
      **the countdown flipbook belongs to (c), not (b)**, exactly like the
      gate visibility bit before it. Do not generalise flipbook emission to
      the other 15 materials / 74 placements until (c) can drive one; the
      records would be correct and inert.
      **(c) Every LUN course program is an empty stub** (235 disabled), so no
      authored scripted behaviour runs at all: timed gates, block and glass
      interactions, effects. The
      [start gate](gamecube-scenery.md) is the first probe at re-attaching
      one event, and it found the visibility bit is plain data, which is the
      cheap half of (c).
      Original sequencing was (b) → (c) → (a), on the assumption that (a)
      needed a whole new pipeline. The empty-root finding retires that: only
      10 of (a)'s 102 placements do. Current order, most visible payoff per
      unit of work first: **(a1) done** → **(a2) crowd as static, 79
      placements** → **scenery interactions (glass, blocks), the visible
      slice of (c)** → **(a3) local matrices, 10 placements** → the runtime
      animation binding and the rest of (c). (b) is written, validated as
      inert, and now folded into (c): the records are correct and will stay
      dormant until something drives a frame index.
- [ ] Scenery interactions — breaking glass and scattering blocks. User
      request September 14: queued as the batch after the (a1)/(a2) geometry
      work. Objects remain intact on impact (user, Sep 13). This is layer (c)
      applied to a specific, visible case, so it inherits the LUN stub
      problem: the authored break behaviour lives in disabled course programs.
      **Inventory done September 14** — the identify step is complete; see
      [collision evidence](gamecube-collision.md). `u0` in the GSF property
      record is an immovability sentinel: 483 of 531 records hold 1e30, only
      48 hold a finite value. `collision_mode` separates the classes, and
      **mode 3 carries both a physics reference and an effect slot**, always
      with the low 0.20 restitution: models 7 (39 placements), 19 (22) and 1
      (2) — 63 placements, the scattering-block candidates. A further 23
      mode 2 records are hidden and carry an effect with no physics, the shape
      of a trigger volume; the crowd prefabs 269-288 carry effect slots 4/5/6.
      `instance_gameplay()` decodes `u0` and `bounce` but drops them from the
      dict — expose them first.
      Nothing is translated to target behaviour, and it is gated behind the
      same driver problem as the gate bit and the flipbook: correct data alone
      stays inert while every LUN program is a stub.
- [ ] Restore the Garibaldi start gate and countdown lights; user reconfirmed
      they are missing on iPhone on September 13 (assets 027). The three gate
      models are supported static geometry, deliberately omitted by 022;
      restore their timed visibility/flipbook binding, not general mesh
      animation. September 14: native loader proves the flipbook is a full
      signed 32-bit field at +68; the shared reader is corrected and tested.
      Hidden staging candidate retains all five light frames and three models;
      its event binding is still unimplemented. The first observer run confirms
      the dispatch side: `StartlightBegin` and `StartgateOpen` each fire once,
      3.72 s apart, with the staged instances bound, and both named lookups
      return value type 0 rather than a callback — so the lookup is the
      attachment point and nothing runs there yet. September 14: the reversible
      visibility operation is found and is pure data, not an engine call.
      Every instance selects one of the course script's 28-byte definitions;
      word 1 bit 16 draws and bit 21 collides, matching the donor GSF's own
      bit 0 and bit 5 shifted by 16. Definition 39 is used by the three staged
      countdown instances and nothing else, so that one record decides whether
      the gate and lights exist in the scene. That bit is **load-time only**.
      `--visible` builds
      `gc-gari-startgate-visible-001`, which differs from the hidden candidate
      by seven bytes, all inside that definition. Two clean 185 s checks
      confirm it: at the same countdown number and camera the visible run
      draws the canopy, six starting stalls and the light column, and the
      hidden control run draws none of them, with riding unaffected.
      The restart is observed too, over three races in one 481 s check:
      both events re-dispatch (windows 3.919 s and 3.736 s), so a handler
      must be re-entrant; re-entering the course after a finish raises
      `StartgateOpen` **alone**, so it must not assume the pair; and the
      three instances bind once and survive both, so the course is not
      reloaded and a handler can hold the definition. All five lookups
      still return value type 0.
      **Visibility solved September 14 (handler-004): the runtime bit is bit 0
      of the same `+128` word.** The visible build reads back `0x10003`, the
      hidden one `2`, and handler-003 only ever wrote `0x10002`. Builtin 2's
      command 1 mirrors the property half into the low half (`srawi 16; or`),
      which is what pointed at it. With `SSX_STARTGATE_MIRROR=1` the handler
      drives bit 0 too, and the gate draws at countdown "3" and is gone at GO,
      on both the first race and after the restart (clean 300 s check).
      Evidence in `local/research/startgate/handler-evidence/`.
      **Course-side script path works (September 14).** User chose course-side
      scripts over host hooks. `tools/gamecube_lun.py` assembles Luno bytecode
      (round-trips all 238 stock programs) and `--countdown-script RATE`
      writes a program into slot 3: the observer shows both named lookups now
      return a callback (type 5) and both closures are invoked; the probe
      variant removes the canopy and stalls during the countdown by script-side
      DeadNode (`script-evidence/`). Open: builtin 22 does not advance the
      light flipbook (diagnosis in progress), and whether a DeadNode'd gate
      returns after a restart is unobserved. Earlier attempt, kept for the record:
      **The handler is written and the flag write does not work.**
      `gamecube_startgate_handler.py` sets the bit on the lights and clears
      it on the gate, in the shared definition and in every live instance's
      own `+128` word: four effective writes over two races, no redundant
      write, no refusal -- and the gate is never drawn. The bit decides what
      the course loads with, not what it draws now; the likely mechanism is
      membership of a draw structure built once at load. Next: characterise
      builtin 2 (`8019193c`) `DeadNode`/`RestoreNode`, which the September 13
      audit identified and warned not to assume reversible. It has to be
      understood rather than avoided, and the handler will drive it once it
      is. Countdown length (both windows exceed the donor's 2.5 s of
      authored waits), the flipbook sequence and the authored gate
      appearance remain open.
      Validate
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
