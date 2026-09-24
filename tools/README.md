# Tools index

120 scripts under `tools/` (plus `tools/macos/` shell helpers). One line
each, taken from each script's docstring; run `python3 tools/<name>.py
--help` for options. Most scripts need user-supplied game data, a device,
or an emulator; read-only inspectors are marked.

## Read-only inspection (stdlib-first)

- `inspect_disc.py` — read-only ISO9660 / EA BIG inspection.
- `probe_worlds.py` — inspect staged SSX world archives; export previews.
- `verify_inputs.py` — cross-check ISO inventory/extraction vs `bsdtar`.
- `inventory_tricky.py` — read-only inventory of Tricky (PS2) course archives.
- `location_inventory.py` — inventory what a location holds besides terrain.
- `gamecube_research.py` — reproducible static research leads.
- `gamecube_telemetry.py` — read-only rider observations via MemoryWatcher.
- `pine.py` — minimal read-only PINE client for running PCSX2.

## Native runtime (GameCube)

- `native_gamecube.py` — pinned macOS AOT prototype (bootstrap/configure/build/module/run).
- `gamecube_game_dir.py` — stage a game directory differing in its worlds.
- `course_manifests.py` — write per-event course-redirect manifests.
- `gamecube_course_check.py` — bounded native course check harness.
- `gamecube_course_fixture.py` — repeatable race-start fixture.
- `gamecube_input.py` — bounded input to a `--pipe-controller` run.
- `native_determinism_check.py` — record/replay/compare dispatch traces.
- `gamecube_native_trace.py` — native callback observer / JSONL summary.
- `native_route.py` — waypoint steering library for the ride harness.
- `gamecube_movie_ab.py` — deterministic-movie A/B CPU harness.
- `gamecube_parity_compare.py` — guest-time-aligned parity of two traces.
- `gamecube_f_regression.py` — F-candidate regression battery.
- `gamecube_schedule_check.py` / `gamecube_schedule_trace.py` — scheduling player/summary.
- `gamecube_perf_spike.py` — probe/diagnostic overhead comparisons.
- `native_probe_io_bench.py` — CPU/storage bound for the trace emitter.
- `gamecube_draw_trace.py` — GX draw-state diagnostic players.
- `gamecube_present_trace.py` — Metal presentation observer.
- `gamecube_replay_check.py` — captured-frame prerequisite check.
- `gamecube_startup.py` — isolated startup observer.
- `gamecube_line_tables.py` — guest-PC line tables for recomp chunks.
- `native_float_classify_spike.py` / `native_float_conversion_spike.py` / `native_float_module_spike.py` / `native_module_opt_spike.py` — isolated FP/codegen experiments.

## Course conversion (donor → stock slots)

- `gamecube_terrain.py` — replace a location's terrain with a Tricky course.
- `gamecube_scenery.py` / `gamecube_scenery_import.py` — scenery reader/importer.
- `gamecube_collision.py` / `gamecube_collision_import.py` / `gamecube_collision_check.py` / `gamecube_collision_shrink.py` / `gamecube_collision_trace.py` — collision reader/importer/checks.
- `gamecube_splines.py` / `gamecube_spline_import.py` — rail reader/importer.
- `gamecube_surfaces.py` / `gamecube_surface_import.py` — terrain behaviour transfer.
- `gamecube_materials.py` — baked terrain lighting translation.
- `gamecube_textures.py` — texture/lightmap import.
- `gamecube_interactions.py` — physics-object → behaviour-class binding.
- `gamecube_lun.py` — course-script ("LUN") assembler/placer.
- `gamecube_startgate.py` / `gamecube_startgate_handler.py` / `gamecube_startgate_trace.py` — countdown assets/handler/observer.
- `gamecube_shape.py` — shape containers (`.gsh`) list/decode/patch.
- `gamecube_slot_probe.py` — measure what a target slot needs.
- `gamecube_reset_paths.py` — grounded recovery-path compiler.
- `gamecube_cleanup.py` — dependency cleanup steps.
- `gamecube_world.py` — world archive reader/writer (`BAM.BIG`).
- `gamecube_snow_check.py` — ground/snow corruption scorer.
- `gamecube_shot_align.py` — align screenshot sequences across runs.
- `course_preset.py` / `course_route.py` / `race_course.py` — presets, route measure, race-course assembly.
- `build_gc_iso.py` — rebuild a GameCube disc image from an extracted dir.

## PS2-era archive/image tools (historical path)

- `build_world_experiment.py`, `build_test_images.py`, `build_course_image.py`
- `recompress_stream.py`, `relayout_stream.py`, `relocate_archive.py`, `grow_group.py`
- `replace_terrain.py`, `import_terrain.py`, `import_crossing.py`, `patch_crossing.py`
- `patch_executable.py`, `patch_geometry.py`, `patch_locale.py`, `patch_ui_glyphs.py`
- `grow_group.py`, `ride_*` (autopilot/compare/course/locations/route), `terrain_contact.py`, `track_position.py`
- `prepare_emulator.py`, `inspect_state_patch.py`, `frame_match.py`, `refpack_encode.py`, `refpack_optimal.py`

## 120 Hz / reprojection / media

- `gamecube_reprojection.py` / `gamecube_reprojection_hud.py` / `gamecube_reprojection_warp.py` — offline capture player, HUD alpha, camera/depth warp.
- `mobile_pacing_check.py` — gate phone smoothing trials.
- `mobile_frame_cost.py` / `mobile_report.py` — frame-cost timeline / report window summary.
- `course_census.py` — stock-track render-cost census (M3).
- `android_trial.py` — Android smoothing/interpolation trial port.
- `loading_speed_spike.py` — FastDiscSpeed A/B startup measurements.

## Texture remaster (archived rollout; see `docs/reserve/asset-policy.md`)

- `texture_pack_plan.py`, `texture_pack_union.py`, `texture_pack_audit.py`, `texture_pack_blend.py`, `texture_pack_cap.py`, `texture_pack_dds.py`, `texture_dump_inventory.py`, `texture_compare_sheet.py`, `upscale_textures.py`, `foliage_detail.py`, `pack_mipmaps.py`, `lightmap_orientation.py`

## Device / platform helpers

- `mobile_gamecube.py` — build, sign, deploy and collect the iOS app.
- `metal_capture.py` / `metal_gpu_ms.py` — GPU-trace capture / busy-time.
- `deploy_odin.py` — push a disc image to the Odin over adb.
- `live_course_request.py` — desktop live-course request protocol.
- `native_replay.py` — replay an iOS benchmark sequence on desktop.
- `ios_diagnostic_sources.py` — iOS-only diagnostic source copies.
- `macos/share_keepalive.py` — macOS SMB reconnect agent.
- `muse_mon.py` — summarize a muse exec JSON log.
- `tools/macos/*.sh`, `tools/muse_brief.sh`, `tools/odin_sampler.sh`, `tools/odin_wireless.sh` — shell helpers.
