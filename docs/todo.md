# Working todo

Living list, most recent first within each section. Move items to Done with
the build or commit that closed them.

## Now

- [ ] Course texture/lighting review (user, September 16): wild-looking
      textures with the lighting observed in-course as a casual observer —
      particularly ground/snow. Needs a review pass over the course's
      textures and lightmaps.
- [ ] 120 Hz verdict re-issue after the generation fix (September 16): the
      architecture review ([review-2026-09-16-architecture.md](research/review-2026-09-16-architecture.md)
      finding 1) withdrew gate-4b MECHANICS GREEN and the phone Combined
      oracle — every extra under F doubling was drawn unblended. The
      one-generation-per-tick fix, the blended validator gate, and the
      trialExtrasBlended phone metric are in; still needed: rerun interp-fx
      and the lifecycle combined leg and confirm blended > 0, re-run the
      phone Combined trial with blending actually on (that number, not the
      recorded one, decides whether retained host palettes are next), and
      re-issue both verdicts.
- [ ] Arch-review findings 2–4 (September 16): (2) consolidate the trial
      state machine (four headers of file-scope statics; SSXResetNativeTrial
      misses counters) into per-namespace TrialState with a single Finish;
      (3) add a tainted-guest guard so a verify-failed halved guest can never
      be checkpointed; (4) decide explicitly whether the ship path doubles
      unconditionally or keeps the rider-state gate, and record it in the
      plan of record. Plus the §5 smaller items (Output() abort on device,
      App.mm trial-flag table, stale menu label, Deadline/alpha periods).
- [ ] iPad GPU trace analysis (September 16): first Metal System Trace of a
      smoothing trial window captured (local/reports/gpu-captures/20260917-015031,
      191 MB, receipted, trial Finished). Still needed: the per-process
      GPU-ms extraction recipe (xctrace export --toc/--xpath) for SSXNative.
- [ ] Plan of record: [implementation plan, September 15](impl-plan-2026-09-15.md).
      The three in-flight agents landed (Aloha collision, boot-time course
      redirect, breaking glass) and are pushed. **Done September 15 (later):**
      the Aloha chain is re-ordered into one archive — `gc-aloha-006` (rails on
      the new scenery) then `gc-aloha-007` (terrain + scenery + rails +
      collision, `73ad0ab6`) — and it **rides** through the redirect, including
      one run with stock `bam.big` and the course's own `alo.big` resident at
      the same time ([the ride](aloha-conversion.md#9-the-ride-september-15)).
      Static collision on the new course is **observed**: under movie playback
      the collision archive and the same archive without collision ride the same
      line for 20 s and then part for good, and the engine's narrow phase
      returns contacts against imported collider 524 (§9.3). Next in the plan's
      order: the app's course picker (item 3), Aloha phase 2 (item 5, the
      scoring driver), and the deliberate-contact ride of
      `gc-gari-interactions-002`, which is now a movie-playback job rather than
      a lucky autopilot.
- [ ] Route control for the native runtime (measured September 15). A
      free-running ride cannot A/B anything: two runs of the *same* archive,
      single core, identical scripted input, diverge within 0.21 guest seconds
      of the race start and end a median 449 / max 69,184 world units apart.
      **Movie playback is the instrument and it works** — two replays of one
      recorded movie agree on all 879 sampled control-flow rows and their rider
      traces stay inside 113 units, so `tools/native_determinism_check.py
      play --course-manifest ...` is now the way to compare two archives or
      chase one object
      ([evidence](aloha-conversion.md#93-static-collision-observed-under-movie-playback)).
      What is still missing is *steering on demand*: a movie only replays the
      line it recorded, so hitting a chosen object still depends on that line
      passing through it. A waypoint autopilot would fix that —
      `tools/gamecube_input.py` already has `stick x y` and
      `gamecube_course_check.py` already reads rider samples live, so the
      follower is the missing piece; the PS2 tools (`ride_route.py`,
      `ride_autopilot.py`) drive PINE and do not apply. Movie playback should
      also settle the phone A/B noted below.
      **September 15 (later): steering exists, following does not.**
      `gamecube_course_check.py --route FILE` follows waypoints from the live
      rider samples and writes `SET MAIN x y` to the pad pipe (opened per write;
      a held writer gets EPIPE when the runtime reopens its read end). It
      calibrates the steering sense itself and measured it: a positive stick x
      turns the heading clockwise in the x/z plane, so `sign = -1`. One route
      reached 2 of 6 waypoints, a second reached 0 of 3 — a proportional
      controller on heading error will not hold a line down a mountain. Pure
      pursuit with late engagement does: routed at a collider 2,637 units off
      the natural line, the rider closed to **868** units and the engine
      narrow-phase tested that object 19 times where it had never tested it
      before — no contact yet, 68 units outside its own tolerance. The steering
      sign is now inferred from the controller's own error growth, because
      holding an input to calibrate it reads the terrain rather than the stick.
      Next: vertical alignment (steering is horizontal, so a route can arrive
      beside an object it passes over), tolerance and gain, and speed control.
      See [route control](route-control.md).
- [ ] Next Tricky course, not a race (user, September 14): after Garibaldi
      reaches parity (physics interactions and sprite/animation cycling are
      the remaining gaps), pick a Tricky Showoff course and map it onto one of
      SSX 3's non-race event types (slopestyle, big air, halfpipe,
      backcountry). Spike done September 14, see
      `local/research/next-course-spike.md`. **Recommendation: Aloha Ice Jam
      Showoff (`aloha.sop`) into `ASS1` "R&B", event 5, slopestyle.** Closest
      length match of any donor/slot pair, fits the slot's 6.99 MB without
      growth, decorative rather than machinery-driven, and on the peak the
      harness already rides. All twelve GameCube Tricky archives are already
      under `local/game/gste69-original/files/data/models/`. Facts: Tricky's
      mode data is `.aip` (Race) vs `.sop` (Showoff), same format, plus
      `RaceMode`/`ShowoffMode` GSF programs; no `.sop` reader exists and no
      showoff scoring table was found. SSX 3's event mode is the second word
      of the `0x802E2C18` row (2 race, 3 slopestyle, 4 big air, 5 halfpipe, 6
      backcountry), not the peak. Kind 21 is the only mode-gated record kind
      (absent in big air and halfpipe) and its header word is 4 for
      slopestyle with two extra distance markers, which `race_course.py`
      hard-codes as race; gate counts differ too (race 6, slopestyle 3).
      Pipedream rejected (its `.sop` equals its `.aip`, halfpipe has no kind
      21); Megaplex rejected while layer (c) is stubbed. Gap about 9-14 days,
      the largest items the scoring driver in the course script (2-4 d) and
      the per-course transform preset (2-3 d); the script driver is the same
      work Garibaldi's glass/block physics and flipbooks need.
      **September 15: the scoring driver should not be written.** Disassembling
      every stock course's script across all five disciplines shows no builtin
      and no handler name that belongs to the slopestyle courses and to no
      other discipline (only backcountry has any), so scoring is engine-side.
      What Aloha needs instead is to be *reached* as slopestyle — the `mode`
      word alone does not switch it — plus medal targets in `behiloc.dbb`.
      See [Aloha §10](aloha-conversion.md#10-phase-2-scoring-is-not-in-the-course-script-september-15).
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
      **Done September 15: all 17 SSX 3 courses, no C++ written.** The 2-4 day
      gxcore estimate above was wrong about the renderer: the native build
      compiles Dolphin's `HiresTextures.cpp`, not the aurora replacement path,
      so dumping and replacement are configuration
      (`tools/native_gamecube.py --texture-dump/--texture-pack`,
      `[Video_Settings]` in the per-game layer) and the hash reconciliation
      never arose. 17 dumps four at a time, 907 distinct course textures,
      per-family models (PBRify V4 for CMPR, Real-ESRGAN for everything else),
      288 MB at 4x, about 40 minutes end to end; ridden clean on three courses;
      an iPhone switch and a course picker in the pause menu. The runbook is
      [texture remaster](texture-remaster.md).
      **Quality gate, same day:** `tools/texture_pack_audit.py` measures
      colour shift, structure drift, alpha drift and flat invention per texture
      against its source. 109 of 907 flagged, nearly all of them improvements;
      the two real defect classes were flat fills gaining grain (15 textures,
      repaired with Lanczos in the shipped pack) and soft particle sprites
      gaining hard outlines (unfixed - no classifier separates a soft gradient
      from a blurred edge yet). Remaining: the particle family, weighting by
      on-screen area, mipmap sidecars, archive repacking, and the PS2 path
      (PCSX2's mechanism, different key).
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
      **Done September 15: the boot-time redirect exists.** The runtime
      patches Snow Jam's event row in guest RAM from a manifest
      (`SSX_COURSE_MANIFEST`, `--course-manifest`, `-ssxCourseManifest`;
      schema in [course selection](course-selection.md)); no DOL byte or
      module changes. The archive basename must match the BIGF member
      basenames inside it; case folds. `sg-redirect-5` is the first ride of
      the converted Aloha course. Open: `mode` alone does not switch the
      HUD or briefing (the Single Event menu overrides it), the save record
      keys by event slot, and the picture/drop/length stay the host's.
      **September 15 (later):** two courses are resident at once — stock
      `bam.big` plus `alo.big`, selected by `archive = alo` — staged by the new
      `tools/gamecube_game_dir.py`, which renames an archive's BIGF world
      members so a second course can live beside the stock one. The receipt now
      hashes every installed `*.big`. **Done September 15: the picker.**
      `tools/course_manifests.py` writes one manifest per event from the DOL's
      own tables, `mobile_gamecube.py courses` copies them to the phone, and the
      pause menu's Course row lists them; a launch flag still wins over the
      stored choice. Compiles for the device; not yet exercised on it.
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
- [ ] 120 Hz route F (double update, halved dt) is the live track; its probes
      are on main. `gamecube_native_trace.py build` injects
      `native/diagnostics/native_callback_trace.h` into a diagnostic copy of
      the run loop under `local/`, so DOUBLE_UPDATE, HALF_CADENCE, HALF_DT,
      GUEST_WINDOW, SPEED_GATE and COUNTER_RESTORE can never reach a shipped
      build; each is off unless its variable is set. Next is the kill order in
      [the F spike plan](research/120hz-f-spike.md): the 2x-update workload
      probe on desktop first, since a desktop CPU that cannot hold
      `guest_seconds_per_host_second` >= 0.95 ends F before any dt work.
      Compare arms with `gamecube_parity_compare.py` (absolute guest timebase,
      end-of-tick body hashes) and gate them with `gamecube_f_regression.py`.
      The two rough edges found in review are fixed: `WriteConstSet` now
      verifies all fourteen addresses before writing any, and the parity tool
      leaves HALF_CADENCE skip rows off the alignment grid.
      **Phone trial shipped September 15 (night):** `NativeTrial::Kind::F`,
      trial-armed v3b drivers, a Try 120Hz sim menu entry, `-ssxFAt`/`--f-at`,
      graceful drift handling and stock-dt restore before finish/checkpoint.
      First live fire (single-core snow-jam-smoke, `--f-at 155`): 533/534
      doubled, clean restore, guard-limited at 10 s on 0.82 speed; update
      pair 5.12 ms fits but render costs 12.25 ms at saved 3x internal
      ([results](research/120hz-f-spike.md#phase-4b-phone-attribution-trial-shipped-first-live-fire-in-progress)).
      **Bias battery PASS-leaning (overnight):** 4 movies, matched player;
      lateral drift mixed signs with <1% mean, flip == engage in all four
      ([results](research/120hz-f-spike.md#bias-battery-results-overnight-post-merge)).
      **Idle-cancel stuck fixed September 16:** a cancel landing with nothing
      in flight restored consts but never cleared Running (return-site finish
      unreachable); F now also finishes at the update entry (13 ms desktop,
      phone-verified 537 doubled + clean finish). Lifecycle test grows a third
      leg + restore-after-idle-cancel gate (`1dd045b`).
      **A/B flags September 16:** `--course-manifest` (bare name or `stock`)
      and `--textures stock|remaster` override menu choices per launch
      (`d6441dd`); course/texture session events record effective values.
- [ ] 120 Hz render test on the F sim backend (user, September 15): when F sim
      is validated, prove >60 FPS presentation driven by doubled updates.
      Gated order: (1) F sim correctness — CLOSED September 16: reset
      sequencer is counter-driven (40 vs 41 ticks, +20 phase event exact,
      no double-fires), first tumble under F enters exact and exits +2
      (float threshold), 0x100 trap shows symmetric float physics with no
      state-8 integer writer, bias battery PASS-leaning
      ([evidence](research/120hz-f-spike.md#crashstate-timer-coverage-desktop-gate-1-closed-september-16));
      Adversarially reviewed same day: envelope 41=41 exact (stronger),
      mid-tick entry disclosed, phase +20/+21 1-tick residual (non-counter
      gate input), 484s are transition one-shots (11x cruise rate open),
      governor silent whole tumble, k computed (renorm candidate), r2 fix;
      accepted risks logged (same-context reset, 484 rate, renorm call,
      router flags);
      (2) input latching — RE-SCOPED September 16 as desktop research
      tooling only (movie-stream gating for menu-window measurement;
      all F results to date have zero input confound, live re-poll is
      already correct, no product change) — not blocking phone/render; (3) phone F headroom at 1x internal (pair + render + system <
      8.33 ms sustained); (4) 120 Hz draws from sim state — DESKTOP
      VERDICT September 16: back-to-back render-every-update draws
      fully but the game's single-slot queue evicts the ordinary draw
      (59/59 rejected) — net 60 Hz half-stale, so true-120 needs
      VI-paced 2-deep queue (backlog 10) or the smoothing/XFB path
      (phone path PROVEN additive: 783 displays = 60/s + 32/s extras,
      zero eviction — gate-4b de-risked);
      DESKTOP 4b September 16: MECHANICS GREEN (F + schedule + pose
      interp compose: 60/60 doubled, 36/36 interpolated extras at
      alpha 0.6–0.78, zero eviction, zero wedge) — remaining 4b is
      the combined trial kind on the phone with present.csv oracle.
      **WITHDRAWN September 16 (later)** — the 36/36 extras were
      unblended duplicates (generation double-count; review finding 1).
      Re-issue needs the interp-fx/lifecycle reruns with blended > 0.
      Trap logged: DTM playback stomps GFX config from the movie
      header (fixed via det-sched.dtm byte 149);
      (5) pacing acceptance (>=117 displayed/s + sim speed >= 0.98 +
      input-latency measurement) with fallback to F-sim/60-draws, then
      stock, on budget miss. No step starts until the gate before it passes.
- [ ] 120 Hz headroom backlog (user, September 15): measured budget is
      update pair ~5.1 ms + render ~12.3 ms at 3x single-core on the phone vs
      8.33 ms. Biggest first: (1) F + dual-core phone run — unknown, and
      dual-core previously moved render 9.5 → 7.8 ms with 25% headroom; the
      ship config may be F+dual-core while tests stay single-core;
      (2) 1x internal for 120 Hz mode — render dominates, config-only change,
      isolates the F update question; (3) production-quiet probe delta — the
      trial's per-body Diff/Hash/Emit/fflush rides in every measured pair,
      size the ship prize with a quiet-mode run — CLOSED September 16
      (~0.1 ms med, ~2% per pair; no headroom); (4) phase-tagged update
      breakdown — CLOSED September 16 (pc histogram: update ~99%
      traversal+physics, bookkeeping ~1%, view 0%; render runs 2x the
      guest instructions of update); (5) update-pair tail —
      CLOSED September 16 as host-attributed (crash-f window: CPU max
      5.35, wall max 7.90, zero over 8.33; spikes show wall≫cpu); (6) fast-FP phone measurement (built, pending)
      plus hot-chunk float-conversion where the breakdown points; (7) fewer
      chassis round-trips (existing item); (8) 1x BC texture pack for perf
      mode (bandwidth, not the 4x quality pack); (9) view/camera at 60 +
      physics at 120 split — CLOSED September 16 as answered-NO (no
      view work inside the doubled update to split); (10) VI-paced true-120 (2x update+render) vs
      back-to-back halves — end-architecture question, needs 1–3 first.
      **Measured September 16 (4 phone runs):** 1x helps (render 12.25 →
      9.37 same-window, speed 0.82 → 0.91) but pair+render ≈ 12 ms still
      misses 8.33 — (2) alone does not reach budget; dual-core shows no
      F-trial win (CPU-saturated updates leave nothing to overlap) and no
      dual-specific trial stalls; cross-run render medians (9.4–13.0) are
      section-dominated (blind sequence doesn't hold a line). Fast-FP
      kitchen-sink (1x + dual + fast-FP) bounds the possible next.
      **Kitchen-sink HELD September 16:** 1x + dual + fast-FP rode 25 s at
      speed 1.0 with 1479 doubled, no limit — the first F trial to hold a
      full window. Attribution split the credit: single-core + fast-FP
      limited at ~10 s / 503 doubled (speed 0.97 → 0.83 on trial start,
      present oracle pure 60 Hz), so dual-core carries F doubling;
      smoothing under dual-core held its full 35 s window untouched
      (1097 extras, no limit) with the present oracle at ~91/s median
      8.4 ms — 60 originals + ~32 extras/s, every extra reaching glass.
      Combined kind (`e07d74a`) merges both paths next.
      **Combined oracle September 16:** kind=2 rode 155 → 173 at kitchen-sink
      settings, then the floor limited on long_rate 0.946 < 0.95 (2 s
      window) — not on output: doubled held full rate (1048, 58/s) while
      extras trickled at half the pure-smoothing rate (278, 16/s), presents
      44% above-60 in bursts (fps peaked 102). Both costs compose, as
      predicted; the finish proved the kind's real point on device —
      completion_mode at start, restore_mode + dt-const restore 0.5 ms
      apart at the end, clean Finished, no stuck Running. Post-trial fps
      dip at seq ~196 repeats run B's at the same sequence point: section
      confounder, not trial-related.
      **ORACLE UNDERSTATED September 16 (later)** — the immediate-XF upload
      path was effectively disabled (zero blends), so the composed cost
      understates; the honest re-run number decides retained host palettes.
      **Perf spikes September 16 (desktop, phone down):** five parallel
      spikes, zero tracked edits, artifacts in local/research/120hz/spike-*/.
      Render breakdown maps 11.05ms quiet pair+render (top: 4.73ms update-pair
      host, 2.74ms ph2 GPU-completion wait; EFB/uploads/shaders closed as
      levers); res curve keeps 1x (all toggle deltas within noise, 1x
      minimizes fill by construction); adaptive extra-capping is a negative
      (displays fall 1:1 with extras); fast-libm doubling cut is real but
      tiny (-0.16ms/pair, parity questions). Only merge: `--preload-textures`
      launch override (`f8e2f75`) scoping pack-decode cost out of trial
      windows. DDS pack (-85% resident) queued for phone verify.
      **Preload A/B September 16 (phone):** remaster + smoothing, flag on vs
      off, both held the full 35 s window unlimited. Preload is a tail fix,
      as designed: trial p99 medians 14.1 vs 15.1 ms, worst second 22 vs
      35 ms — the off arm's worst second lands exactly on trial start
      (first extras + fresh angles decoding on demand); +66 extras with
      preload (1238 vs 1172). Pre-trial tails identical (worst hitches are
      section/sim, not texture). First attempt voided: user pause shifted
      run 1 into a heavier section (limited), run 2 stillborn on likely
      auto-lock suspend — keep the phone awake during chains.
      Audio skipping in heavy areas is a budget-overrun symptom (CPU
      starvation → DMA underrun), fixed by headroom, not audio work.
      **Menu static fixed September 16:** separate mechanism — an idled AX
      task leaves pushed DSP at a frozen nonzero constant (whole seconds,
      2 distinct samples, proven in DSP dumps); DC-blocker in the iOS
      backend settles it to silence, user-confirmed fixed. `--audio-dump`
      + dump collect stays as the pushed-sample oracle.
- [ ] 120 Hz by frame generation is ruled out, not pending. The Metal
      interpolation prototype on `spike/120hz` (worktree
      `../ssx3-120hz`, unmerged on purpose) cut emulation to 4.9 FPS at 0.36
      speed against 59.4/0.99 stock, and cost 10.4 ms of GPU per synthesized
      frame - more than half a frame period on its own. The branch's own
      diagnosis blames a CPU wait on the interpolation command buffer, but
      there is no `waitUntilCompleted` on the per-frame path; the likely cause
      is `[layer nextDrawable]` back-pressure, since it presents twice per game
      frame with `presentAfterMinimumDuration:1/120` on a 60 Hz panel that can
      retire only one - which the branch's own iOS section had predicted would
      throttle emulation. Keep the branch for its approach-2 reading: the
      `rawProjection` to near/far/fov/aspect derivation, the XFB-copy snapshot
      point for EFB depth, and the `MTLFXFrameInterpolator` contract including
      the `uiTexture` input that would fix HUD ghosting. Do not re-measure
      frame generation on the Mac's 60 Hz display; it cannot show the cadence.
      Its `check_stacked_patches` change to `tools/native_gamecube.py` must not
      be merged as written: it engages whenever `spike-120hz.patch` merely
      exists, which breaks `configure`/`build`/`run` on main, and its stack
      omits `recompcore-course-redirect.patch`, so it fails even with the spike
      applied (residual: `Source/Core/Core/CMakeLists.txt`). A correct version
      keys on which overlays are *applied* and lists them all.
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
      `instance_gameplay()` now exposes them as `immovable` and `bounce`.
      **Pushable blocks bound September 15 (`tools/gamecube_interactions.py
      --pushable-blocks`).** The stock mechanism, decoded in
      `local/research/startgate/breakables-recipe.md`: definition word 2 is
      a behaviour-class oid indexing the script record's 24-byte class table,
      whose slot 1 (create) names a program; the stock pushable is a
      one-function program calling builtin 6 AnimTeeter on the firing
      instance. Every imported definition had word 2 = -1, which is why no
      event ever fired. The tool clones the 63 mode-3 placements' definition
      with the class pointer set, claims class row 0, and writes the teeter
      program (stock mass/travel, donor restitution 0.20) into stub slot 69.
      `gc-gari-interactions-001` (on top of the countdown build) rides a
      clean 300 s check and is **installed on the iPhone** (September 15,
      00:06). Not yet observed: a block actually moving on contact; the
      donor's physics and effect records stay untranslated. Glass next: the
      23 hidden mode-2 trigger volumes need a contact-slot program (stock
      ABC1 program 171 shape: restore self, AnimObject per debris piece, 52
      inline particle args), and the debris models are not yet identified.
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
      DeadNode (`script-evidence/`). **Lights done too (script-003):** the
      handler calls builtin 0 to create the instance's modifier host, then
      builtin 22; the lamps cycle through the countdown and the gate returns
      after a restart (engine course reset). Remaining polish: the donor's
      authored 1.0/0.5/0.5/0.5 s beats versus the free-running 1.3 flips/s
      loop. Earlier attempt, kept for the record:
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
      2026-09-15: the hand-installed copy was lost when the phone's container
      was rebuilt, because `provision` copies `files/` from the pristine disc.
      Now re-applied by `provision` itself (`--stock-glyphs` opts out) and
      covered by `tests/test_patch_ui_glyphs.py`.

- [x] 2026-09-11 `tools/build_gc_iso.py` rebuilds a GameCube ISO; stock FST
      reproduced byte for byte.
- [x] 2026-09-11 Touch overlay relabelled to Xbox positions (A bottom, B right,
      X left, Y top, LB/RB).
- [x] 2026-09-11 gc-gari-005: first rideable GameCube Garibaldi (race start,
      ride, restart, zero invalid accesses).
- [x] 2026-09-11 Two-stick touch overlay; right stick drives the D-pad for spins.
- [x] 2026-09-11 PS2-position physical pad mapping with grab translation.
- [x] 2026-09-11 iPhone smoke run at 60 FPS, no JIT.
