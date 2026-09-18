# A3 report — documentation structure audit (read-only)

Run date: 2026-09-18. Brief: `local/muse/prompts/A3.md`.
Mode: read-only. No tracked file was modified. Files were only created under
the ignored `local/research/A3/` directory. The brief's commit step
(`git add -f`, `[A3]` commit with trailers) was not executed, per the
read-only instruction for this run. No deletion or retention verdicts are
given here; the orchestrator decides. `ARCHIVE-CANDIDATES.md` in the drafts
lists classification candidates only.

Gate applied throughout step 1: a document linked from a current document
(root `README.md`, `native/README.md`, `docs/todo.md`,
`docs/plan-120fps-2026-09-17.md`, `docs/plan-gs-gpu-backend-2026-09-18.md`,
`docs/numbers-ledger.md`) is not classified stale, regardless of age.

## 1. Markdown map (`git ls-files '*.md'`, 62 files)

Columns: first heading (from first 20 lines); date found in file content;
size in bytes; last commit date (`git log -1 --format=%ad --date=short`);
classification; inbound links (basename-level `git grep -- '*.md'`,
self excluded; `README.md`/`REPORT.md` basenames are shared by several
files so their rows point to the shared hit set).

| Path | First heading | Date in file | Size | Last commit | Classification | Inbound links (tracked) |
| --- | --- | --- | --- | --- | --- | --- |
| README.md | # SSX 3 course-port investigation | — | 16044 | 2026-09-15 | README | basename shared by 4 README files; full-path `native/README.md` is linked from root README, gamecube-feasibility, plan-120fps, roadmap |
| docs/aloha-conversion.md | # Aloha Ice Jam (Showoff) into ASS1 "R&B" | 2026-09-14 | 48772 | 2026-09-15 | current reference | README, course-selection, gamecube-collision, impl-plan-2026-09-15, route-control, texture-remaster, todo |
| docs/architecture-review.md | # Architecture review — September 12, 2026 | — | 10546 | 2026-09-13 | current reference | README, garibaldi-visual-comparison, todo |
| docs/asset-policy.md | # Asset policy: shipped assets until the risky window closes | — | 3222 | 2026-09-17 | current plan | todo |
| docs/course-selection.md | # Course selection by runtime redirect (GameCube) | — | 16898 | 2026-09-17 | current reference | README, aloha-conversion, texture-remaster, todo, native/README |
| docs/full-course-experiment.md | # Complete Garibaldi terrain replacement experiments | — | 22550 | 2026-09-11 | historical research | README, aloha-conversion, peaks-and-locations, rebuild-experiment, roadmap |
| docs/gamecube-collision.md | # GameCube collision and reset behavior | — | 26766 | 2026-09-15 | current reference | aloha-conversion, route-control, todo |
| docs/gamecube-feasibility.md | # GameCube route: initial feasibility audit | 2026-09-10 | 11150 | 2026-09-13 | current reference | README, roadmap |
| docs/gamecube-materials.md | # Terrain material conversion | — | 5442 | 2026-09-13 | current reference | README, architecture-review, gamecube-world, garibaldi-visual-comparison, todo |
| docs/gamecube-rails.md | # GameCube donor rail conversion | — | 6742 | 2026-09-13 | current reference | aloha-conversion, gamecube-scenery, todo |
| docs/gamecube-scenery.md | # GameCube scenery conversion | 2026-09-12 | 49432 | 2026-09-14 | current reference | aloha-conversion, impl-plan-2026-09-15, todo |
| docs/gamecube-world.md | # GameCube SSX 3 world format (GXBE69) | 2026-09-12 | 18950 | 2026-09-13 | current reference | aloha-conversion, architecture-review, todo, native/README |
| docs/garibaldi-visual-comparison.md | # Garibaldi visual comparison — September 12, 2026 | — | 10464 | 2026-09-13 | current reference | README, architecture-review, gamecube-materials, gamecube-world, todo |
| docs/impl-plan-2026-09-15.md | # Implementation plan, September 15 2026 | — | 4806 | 2026-09-15 | current plan | todo |
| docs/investigation.md | # Garibaldi → SSX 3: initial investigation | 2026-09-10 | 12063 | 2026-09-11 | historical research | README |
| docs/locale-tables.md | # SSX 3 locale strings | — | 2270 | 2026-09-11 | historical research | full-course-experiment, peaks-and-locations, rebuild-experiment, todo |
| docs/location-anatomy.md | # What an SSX 3 location holds besides terrain | 2026-09-10 | 8135 | 2026-09-10 | historical research | tricky-courses |
| docs/numbers-ledger.md | # Current numbers ledger | — | 30656 | 2026-09-18 | gate ledger | plan-120fps-2026-09-17, todo |
| docs/odin-testing.md | # Garibaldi test on Odin 3 | — | 4898 | 2026-09-11 | historical research | README, full-course-experiment, roadmap |
| docs/peaks-and-locations.md | # Peaks, locations and the level selector in SSX 3 | 2026-09-10 | 6883 | 2026-09-11 | historical research | rebuild-experiment, roadmap, texture-remaster, todo, tricky-courses |
| docs/plan-120fps-2026-09-17.md | # 120 fps plan of record — September 17, 2026 (evening) | — | 27645 | 2026-09-17 | current plan | todo |
| docs/plan-gs-gpu-backend-2026-09-18.md | # Plan: a GPU Graphics Synthesizer backend for PS2Recomp (prep for an autonomous loop) | 2026-09-18 | 13825 | 2026-09-18 | current plan | todo |
| docs/rebuild-experiment.md | # First bounded rebuild experiment | 2026-09-10 | 34489 | 2026-09-11 | historical research | README, investigation |
| docs/research/120hz-analysis.md | # 120 Hz investigation — September 13, 2026 | 2026-09-13 | 14111 | 2026-09-13 | historical research | README, architecture-review, 120hz-native-path, 120hz-reprojection |
| docs/research/120hz-cpu-overhead-spikes.md | # CPU and diagnostic overhead spikes | — | 13884 | 2026-09-13 | historical research | performance-review-2026-09-13, todo |
| docs/research/120hz-f-spike.md | # F spike: true 120 Hz simulation — kill-first plan | — | 52366 | 2026-09-16 | historical research | review-2026-09-16-architecture, todo, native/ios/README |
| docs/research/120hz-host-replay.md | # Host-side frame replay — September 13, 2026 | — | 15916 | 2026-09-13 | historical research | plan-120fps-2026-09-17, 120hz-reprojection, normal-frame-cpu-spike, performance-review-2026-09-13, todo |
| docs/research/120hz-independent-schedule.md | # Independent native render scheduling experiment | — | 13298 | 2026-09-13 | historical research | 120hz-native-interpolation, 120hz-render-seam |
| docs/research/120hz-native-interpolation.md | # Native pose interpolation prototype — September 13, 2026 | — | 14556 | 2026-09-16 | historical research | 120hz-native-path, 120hz-reprojection, review-2026-09-16-architecture, native/ios/README |
| docs/research/120hz-native-path.md | # Native rendering investigation — September 13, 2026 | 2026-09-13 | 12594 | 2026-09-13 | historical research | 120hz-analysis, 120hz-render-seam, 120hz-reprojection |
| docs/research/120hz-output-resolution.md | # Output size, internal detail and callback CPU timing | — | 27501 | 2026-09-13 | historical research | performance-review-2026-09-13, startup-shortcut, todo |
| docs/research/120hz-pacing-acceptance.md | # Phone pacing and drawable-resolution acceptance | — | 8865 | 2026-09-13 | historical research | plan-120fps-2026-09-17 |
| docs/research/120hz-render-seam.md | # Repeated native rendering and camera experiment | — | 11499 | 2026-09-13 | historical research | 120hz-analysis, 120hz-independent-schedule, 120hz-native-path |
| docs/research/120hz-reprojection.md | # 120 Hz reprojection research — bounded first batch, September 14, 2026 | — | 21664 | 2026-09-14 | historical research | performance-review-2026-09-13, todo |
| docs/research/120hz-review-followup.md | # Review follow-up: load protection and overhead | — | 13867 | 2026-09-13 | historical research | none found |
| docs/research/float-arithmetic-audit.md | # Floating-point arithmetic classifier spike | — | 12340 | 2026-09-13 | historical research | float-conversion-spike, todo |
| docs/research/float-conversion-spike.md | # Generated floating-point conversion spike | — | 13348 | 2026-09-13 | historical research | todo |
| docs/research/loading-speed-spike.md | # Isolated DVD loading-speed experiment | — | 6757 | 2026-09-13 | historical research | review-2026-09-17-recomp-perf, startup-shortcut, todo |
| docs/research/normal-frame-cpu-spike.md | # Ordinary-frame CPU attribution | — | 9711 | 2026-09-13 | historical research | float-arithmetic-audit, float-conversion-spike, performance-review-2026-09-13, todo |
| docs/research/performance-batch2-followup.md | # Fast-FP batch follow-up — September 14, 2026 | — | 8334 | 2026-09-14 | historical research | performance-review-2026-09-13, todo |
| docs/research/performance-review-2026-09-13.md | # Performance review — September 13, 2026 | — | 20145 | 2026-09-14 | historical research | 120hz-reprojection, todo |
| docs/research/ps2recomp-spike-2026-09-12/commands-and-outputs.md | ## [0] List workspace contents | — | 96645 | 2026-09-18 | handoff or snapshot | spike README |
| docs/research/ps2recomp-spike-2026-09-12/README.md | # PS2Recomp feasibility spike (muse on the-media-server, 2026-09-11/12) — recovered transcript | 2026-09-11 | 8473 | 2026-09-18 | handoff or snapshot | basename shared with other READMEs; referenced by commands-and-outputs |
| docs/research/review-2026-09-16-architecture.md | # Architecture review of September 15–16 changes | — | 10148 | 2026-09-16 | historical research | 120hz-f-spike, todo |
| docs/research/review-2026-09-17-architecture.md | # Architecture review of September 16–17 changes | — | 14044 | 2026-09-17 | historical research | review-2026-09-17-recomp-perf, todo |
| docs/research/review-2026-09-17-recomp-perf.md | # Deep dive: recomp architecture and performance — September 17, 2026 | 2026-09-17 | 29809 | 2026-09-17 | historical research | none from tracked docs besides local gate reports |
| docs/research/ssx3-120hz-handoff-2026-09-13.md | # SSX3 / 120 Hz handoff | — | 19338 | 2026-09-13 | stale or superseded (superseded by docs/plan-120fps-2026-09-17.md) | 120hz-analysis, 120hz-native-path, 120hz-reprojection; no inbound from current plans |
| docs/research/startup-shortcut.md | # Fast cold start to the main menu | — | 17379 | 2026-09-15 | historical research | todo, native/ios/README |
| docs/roadmap.md | # Roadmap: Garibaldi in SSX 3, and a generic Tricky → SSX 3 course patcher | 2026-09-10 | 13152 | 2026-09-11 | stale or superseded (superseded by docs/impl-plan-2026-09-15.md and the native route in native/README.md) | rebuild-experiment; no inbound from current docs |
| docs/route-control.md | # Route control for the native runtime | — | 5884 | 2026-09-15 | current reference | aloha-conversion, todo |
| docs/share-recovery.md | # Persistent share connection on macOS | — | 3759 | 2026-09-13 | current reference | README, architecture-review |
| docs/texture-remaster.md | # Texture remaster: a runbook | — | 49945 | 2026-09-15 | current reference (method; rollout superseded by docs/asset-policy.md, which states this itself) | asset-policy, impl-plan-2026-09-15, todo |
| docs/todo.md | # Working todo | 2026-09-17 | 115287 | 2026-09-18 | current plan | numbers-ledger, plan-120fps-2026-09-17, plan-gs-gpu-backend-2026-09-18, performance-review-2026-09-13, review-2026-09-16-architecture, review-2026-09-17-recomp-perf, texture-remaster |
| docs/tricky-courses.md | # SSX Tricky course inventory | 2026-09-10 | 2084 | 2026-09-10 | historical research | none from tracked docs besides local gate reports |
| local/research/A2/REPORT.md | # A2 — secrets, personal data, private infrastructure: findings tables | 2026-09-17 | 29064 | 2026-09-18 | handoff or snapshot | basename shared by 5 REPORT files; no full-path inbound found (appeared mid-run as a parallel-audit commit) |
| local/research/G0/REPORT.md | # G0 report — ps2xGS skeleton + GS capture/replay harness + census (synthetic streams) | — | 21472 | 2026-09-18 | handoff or snapshot | referenced by numbers-ledger rows |
| local/research/P1/REPORT.md | # P1 report — Mac (arm64) PS2Recomp re-spike | — | 29250 | 2026-09-18 | handoff or snapshot | referenced by numbers-ledger rows |
| local/research/S2/REPORT.md | # S2 — Replay state architecture: REPORT | — | 50419 | 2026-09-18 | handoff or snapshot | referenced by numbers-ledger rows |
| local/research/S2b/REPORT.md | # S2b — host replay capacity: third EGL arm + Vulkan arms (REPORT) | 2026-09-18 | 16854 | 2026-09-18 | handoff or snapshot | referenced by numbers-ledger rows |
| native/ios/README.md | # iOS development milestone | — | 25131 | 2026-09-15 | README | README, 120hz-f-spike, 120hz-native-interpolation, startup-shortcut (basename-level) |
| native/README.md | # GameCube native prototype | 2026-09-10 | 10579 | 2026-09-17 | README | README, gamecube-feasibility, plan-120fps-2026-09-17, roadmap, todo (basename-level) |
| native/research.md | # GXBE69 research notebook | 2026-09-10 | 11839 | 2026-09-13 | current reference | plan-120fps-2026-09-17, 120hz-native-interpolation, native/README |

Note: `local/research/*` REPORT files are tracked (force-added) although
`/local/` is gitignored. `native/research.md` is tracked despite not
appearing in the brief's step-1 glob discussion; it is included here because
`git ls-files '*.md'` lists it.

## 2. README findings

`README*` in the tree: 4 tracked (`README.md`, `native/README.md`,
`native/ios/README.md`, `docs/research/ps2recomp-spike-2026-09-12/README.md`)
plus untracked/ignored copies under `local/`, `third_party/` (vendored
upstream READMEs, out of scope for content audit) and `.muse/worktrees/`.
No `tools/README.md` and no `docs/README.md` exist. Checks per brief:
(a) build instructions that no longer work, (b) references to removed tools,
(c) missing prerequisites, (d) missing no-game-data statement + how to
supply your own.

| File | What it says now | Gaps observed |
| --- | --- | --- |
| README.md (root, 16044 B, last commit 2026-09-15) | PS2 + GameCube course-port investigation; Garibaldi/Aloha build IDs (gc-gari-013, gc-aloha-007); iOS app; run-gari-010 on the share; Odin 3 steps; storage layout; PS2-era tool commands (inspect/probe/build/relocate, PCSX2+PINE, `sh tools/macos/build.sh`, `python3 -m unittest discover -s tests`) | (a) `builds/`, `emulator/` paths in the tables do not exist in the repo; Try-it-yourself depends on `/Volumes/share/...` and `local/builds/...`, neither shippable. (b) No removed-tool references found: all named scripts exist under `tools/`. (c) Prerequisites listed (Python 3.10+, bsdtar, PCSX2+PINE, swiftc, screen-recording) but no GameCube-native prerequisites (Python 3.11+, Git, CMake, Ninja, Apple Clang, submodules) — those live only in `native/README.md`. (d) No license section. No explicit "no game data is included" statement; closest is "`local/` and `third_party/` are ignored by Git. No game assets, executables, ISOs, or generated meshes belong in commits." No how-to-supply-your-own-disc section at top level (extraction commands appear only inside `native/README.md` with share paths). `ODIN-TESTING.md` is referenced as inside the shared build, not present in the repo. |
| native/README.md (10579 B, 2026-09-17) | Stock SSX 3 AOT foundation on Dolphin-derived runtime; pins in `dependencies.json`; reproduce via `tools/native_gamecube.py bootstrap/configure/build/module/run`; DOL default `local/source/gamecube/ssx3/sys/main.dol` with SHA-256 check; extracted disc default `/Volumes/share/brad/games/ssx3-workbench/native/GXBE69` with `run --game PATH` override; course staging via `tools/gamecube_game_dir.py` + manifest; run profiles, counters, patches list; determinism gate; `--fast-fp`; research leads pointer | (a) Reproduce commands reference submodule fetch + share-hosted game data; nothing to fix as commands, but they cannot run without user-supplied data (undisclosed in this file beyond the default path). (b) No removed-tool references found. (c) Prerequisites stated (Python 3.11+, Git, CMake, Ninja, Apple Clang). (d) No license section. Game-data statement is partial: "Keep dependencies in ignored `third_party/`, game files and generated code in ignored `local/`" — present, but no explicit "clone contains no game data" sentence and no extraction how-to beyond the DTK one-liner with a share path. Validation stamp reads "As of 2026-09-10" while Aloha/course-redirect work (September 15–17) is described in root README and `docs/` but not reflected here. |
| native/ios/README.md (25131 B, 406 lines, 2026-09-15) | iOS dev app: touch controls, pause/lifecycle/checkpoint semantics, fast start, build-info/course-label verification, receipts, 35 s smoothing trial, Try 120Hz sim (route F), Half/75%/Full/Match + 1x-4x detail, launch overrides (`mobile_gamecube.py launch ...`), dual-core default, simulator null-audio diagnostic | (a) Commands are launch-tool flags, all consistent with `tools/mobile_gamecube.py` options observed in-tree. (b) No removed-tool references found. (c) Prerequisites (Xcode/signing/provisioning, device) are described via receipts/build-info rather than a prerequisites list. (d) No license section; game-data sourcing is implicit (deployment command writes `Documents/course-build.json`; local records "stay outside version control"). Several behaviours are marked as needing phone validation (toggle/restore combos, detail-change checkpoint behaviour, dual-core+smoothing combination). |
| docs/research/ps2recomp-spike-2026-09-12/README.md (8473 B, 2026-09-18) | Recovered 09-11/09-12 transcript: feasibility answer, VU1 coverage from source reading, spike plan, blocked-on-disc-access notes; states its verdicts are the spike agent's words, not verified | (a–c) Not a build doc; no build instructions or prerequisites to check. (d) Not applicable (snapshot doc). Contains other-machine absolute paths (`/mmt/share/...`, `~/dev`, `/tmp/PS2Recomp`, `/tmp/ssx3vu`) as transcript content. |
| tools/README.md | Missing (no such file) | Draft provided under `drafts/tools/README.md` (generated index from docstrings). |
| docs/README.md | Missing (no such file) | Draft provided under `drafts/docs/README.md` (classified index). |

## 3. Tools usage (`tools/*.py`, 120 tracked files; `native/*.py|sh`, zero files)

Method: read-only. First line + first docstring line (first 30 lines) +
`argparse` presence (first 80 lines) + literal `usage` string in first 40
lines + `__main__` presence. No script was executed. `native/*.py` and
`native/*.sh` match no files (`ls` confirms); native code is `.h`/`.c`/`.json`
diagnostics, `ios/` sources and `patches/`.

Summary counts: 120 files have a leading docstring; 98 import `argparse`;
110 contain an `if __name__ == "__main__"` gate; 10 contain a literal
`usage`/`Usage:` string in the first 40 lines
(`gamecube_parity_compare`, `gamecube_shot_align`, `gamecube_snow_check`,
`import_crossing`, `metal_gpu_ms`, `patch_crossing`, `ride_autopilot`,
`ride_locations`, `ride_route`, `track_position`). Scripts without a usage
line generally expose `--help` via `argparse`; library-style modules
(no `argparse`, no `__main__`) are: `course_preset`, `gamecube_cleanup`,
`gamecube_collision`, `gamecube_lun`, `gamecube_materials`,
`gamecube_reset_paths`, `gamecube_splines`, `gamecube_surfaces`,
`gamecube_world`, `lightmap_orientation`, `muse_mon`, `native_route`,
`patch_geometry`, `race_course`, `refpack_encode`, plus no-main drivers
(`gamecube_present_trace`, `import_crossing`, `patch_crossing`,
`ride_autopilot`, `ride_route`, `track_position`).

Full table (docstring = first docstring line, truncated):

| Script | Docstring | argparse / main / usage-line |
| --- | --- | --- |
| tools/android_trial.py | Android smoothing/interpolation trial port: build, run, analyze. | yes / yes / no |
| tools/build_course_image.py | Build one verified image with a rebuilt world, event name and locale description. | yes / yes / no |
| tools/build_gc_iso.py | Rebuild a GameCube disc image from an extracted directory (sys/ + files/). | yes / yes / no |
| tools/build_test_images.py | Create test ISOs by substituting verified, fixed-size SSB blocks. | yes / yes / no |
| tools/build_world_experiment.py | Build a bounded SSX 3 control or terrain-bump archive for emulator testing. | yes / yes / no |
| tools/course_census.py | Stock-track census for M3: per-course render cost on one pinned player. | yes / yes / no |
| tools/course_manifests.py | Read SSX 3's own event tables out of main.dol and write one course-redirect manifest per event. | yes / yes / no |
| tools/course_preset.py | Per-course presets: the donor files, the target slot and the placement transform. | no / no / no |
| tools/course_route.py | Extract a Tricky race line and measure a ride against its transformed route. | yes / yes / no |
| tools/deploy_odin.py | Push a built GameCube disc image to the Odin (Dolphin for Android) over adb. | yes / yes / no |
| tools/foliage_detail.py | Rework an upscaled foliage cutout so it reads as needles rather than a blob. | yes / yes / no |
| tools/frame_match.py | Pair screenshots from two replays of one movie by where the rider was. | no / yes / no |
| tools/gamecube_cleanup.py | GameCube ports of replace_terrain.py's dependency cleanup steps. | no / no / no |
| tools/gamecube_collision.py | Bounded Tricky GC collision reader and SSX 3 GC triangle-mesh encoder. | no / no / no |
| tools/gamecube_collision_check.py | Summarize an owned static-obstacle trace without mistaking a clean ride for contact. | yes / yes / no |
| tools/gamecube_collision_import.py | Experimental static collision candidate; native impact validation is required. | yes / yes / no |
| tools/gamecube_collision_shrink.py | Measure imported colliders against their art, and scale them if asked. | yes / yes / no |
| tools/gamecube_collision_trace.py | Build an isolated read-only static-collision diagnostic module. | yes / yes / no |
| tools/gamecube_course_check.py | Bounded native course check with rider observations and state-aware race start. | yes / yes / no |
| tools/gamecube_course_fixture.py | Build a repeatable race-start fixture without altering production course paths. | yes / yes / no |
| tools/gamecube_draw_trace.py | Build isolated GX draw-state diagnostic players, or compare their captures. | yes / yes / no |
| tools/gamecube_f_regression.py | F-candidate regression battery over one probe trace of a movie run. | yes / yes / no |
| tools/gamecube_game_dir.py | Stage a native-runtime GameCube game directory that differs from stock in its worlds. | yes / yes / no |
| tools/gamecube_input.py | Send a bounded input to an isolated native_gamecube.py --pipe-controller run. | yes / yes / no |
| tools/gamecube_interactions.py | Bind donor physics objects to SSX 3 behaviour classes in the course script. | yes / yes / no |
| tools/gamecube_line_tables.py | Guest-PC line tables for static-recomp chunks, plus signpost selection. | yes / yes / no |
| tools/gamecube_lun.py | Assemble and place SSX 3 course-script ("LUN") programs. | no / no / no |
| tools/gamecube_materials.py | Translate baked terrain lighting between verified GameCube engine conventions. | no / no / no |
| tools/gamecube_movie_ab.py | Deterministic-movie A/B CPU harness for sub-noise module comparisons. | yes / yes / no |
| tools/gamecube_native_trace.py | Build an isolated native callback observer or summarize its JSONL events. | yes / yes / no |
| tools/gamecube_parity_compare.py | Guest-time-aligned gameplay parity between two probe traces of one movie. | yes / yes / yes |
| tools/gamecube_perf_spike.py | Sequential, isolated comparisons of native probe and diagnostic overhead. | yes / yes / no |
| tools/gamecube_present_trace.py | Build an isolated Metal presentation observer using existing native libraries. | yes / no / no |
| tools/gamecube_replay_check.py | Check the captured-frame prerequisite, keeping renderer acceptance closed. | yes / yes / no |
| tools/gamecube_reprojection.py | Build/run an isolated GPU capture player. Offline research; never presents extra frames. | yes / yes / no |
| tools/gamecube_reprojection_hud.py | Recover the HUD tail's alpha from two captures of one movie frame. | yes / yes / no |
| tools/gamecube_reprojection_warp.py | Offline camera/depth warp proof (requires numpy and Pillow). | yes / yes / no |
| tools/gamecube_research.py | Generate reproducible static research leads, never inferred function names. | yes / yes / no |
| tools/gamecube_reset_paths.py | Compile grounded recovery paths independently of airborne racer AI paths. | no / no / no |
| tools/gamecube_scenery.py | Read GameCube Tricky scenery without assuming the PS2 mesh layout. | yes / yes / no |
| tools/gamecube_scenery_import.py | Experimental static Tricky scenery import into an existing GC terrain build. | yes / yes / no |
| tools/gamecube_schedule_check.py | Run a pinned isolated scheduling player through the normal course checker. | yes / yes / no |
| tools/gamecube_schedule_trace.py | Summarize independent scheduling without counting requests as rendered frames. | yes / yes / no |
| tools/gamecube_shape.py | GameCube SSX 3 shape containers (.gsh, magic SHPG): list, decode, and patch. | yes / yes / no |
| tools/gamecube_shot_align.py | Align two screenshot sequences from different runs of the same movie. | no / yes / yes |
| tools/gamecube_slot_probe.py | Measure everything a course conversion needs to know about a target slot. | yes / yes / no |
| tools/gamecube_snow_check.py | Ground/snow corruption scorer for SSX 3 GameCube screenshots. | no / yes / yes |
| tools/gamecube_spline_import.py | Build a local, experimental donor-rail candidate from a scenery build. | yes / yes / no |
| tools/gamecube_splines.py | Strict Tricky GC rail reader and SSX 3 GC curve encoder. | no / no / no |
| tools/gamecube_startgate.py | Stage countdown assets in a fresh local course candidate. | yes / yes / no |
| tools/gamecube_startgate_handler.py | Build a bounded countdown visibility handler in an isolated native module. | yes / yes / no |
| tools/gamecube_startgate_trace.py | Build a bounded, read-only countdown observer in an isolated native module. | yes / yes / no |
| tools/gamecube_startup.py | Build an isolated startup observer; preserve production/vendor binaries. | yes / yes / no |
| tools/gamecube_surface_import.py | Rebuild an existing imported GC course with verified terrain reset semantics. | yes / yes / no |
| tools/gamecube_surfaces.py | Transfer verified terrain behavior from Tricky GC to SSX 3 GC. | no / no / no |
| tools/gamecube_telemetry.py | Read-only GXBE69 rider observations through Dolphin's MemoryWatcher. | yes / yes / no |
| tools/gamecube_terrain.py | Replace a GameCube SSX 3 location's terrain with a GameCube Tricky course. | yes / yes / no |
| tools/gamecube_textures.py | Import GameCube Tricky course textures and lightmaps into SSX 3 world records. | yes / yes / no |
| tools/gamecube_world.py | GameCube SSX 3 world archive reader/writer (BAM.BIG: bam.gdb + bam.gsb). | no / no / no |
| tools/grow_group.py | Grow one SSX 3 stream group by appending raised copies of some of its terrain patches. | yes / yes / no |
| tools/import_crossing.py | Compare a ride log with an imported terrain section and the original hub surface. | no / no / yes |
| tools/import_terrain.py | Place a section of SSX Tricky (Garibaldi) terrain into an SSX 3 location (roadmap M4). | yes / yes / no |
| tools/inspect_disc.py | Read-only ISO9660 / EA BIG inspection. Python standard library only. | yes / yes / no |
| tools/inspect_state_patch.py | Look for a disc terrain patch in a PCSX2 save state's EE memory (read-only). | yes / yes / no |
| tools/inventory_tricky.py | Read-only inventory of every SSX Tricky (PS2) course archive on the disc. | yes / yes / no |
| tools/ios_diagnostic_sources.py | Produce iOS-only diagnostic source copies; fail if an upstream seam changes. | yes / yes / no |
| tools/lightmap_orientation.py | Check which lightmap-cell orientation each engine uses, from its own stock data. | no / no / no |
| tools/live_course_request.py | File a desktop live-course request (the SSX3_COURSE_REQUEST protocol). | yes / yes / no |
| tools/loading_speed_spike.py | Isolated, fresh-process FastDiscSpeed A/B startup measurements. | yes / yes / no |
| tools/location_inventory.py | Inventory what an SSX 3 location holds besides terrain (read-only). | yes / yes / no |
| tools/macos/share_keepalive.py | Prepare, install, inspect or remove a per-user macOS SMB reconnect agent. | yes / yes / no |
| tools/metal_capture.py | GPU-trace capture around an automated trial window on a tethered iOS device. | yes / yes / no |
| tools/metal_gpu_ms.py | Per-process GPU-busy time from a Metal System Trace bundle. | yes / yes / yes |
| tools/mobile_frame_cost.py | Per-second frame-cost timeline and comparison for SSX iOS session reports. | yes / yes / no |
| tools/mobile_gamecube.py | Build, locally sign, deploy, and collect the SSX 3 iOS development app. | yes / yes / no |
| tools/mobile_pacing_check.py | Gate bounded phone smoothing trials and describe full/half drawable comparisons. | yes / yes / no |
| tools/mobile_report.py | Summarize an explicitly selected time window from an SSX iOS test report. | yes / yes / no |
| tools/muse_mon.py | Summarize a muse exec --json log. | no / no / no |
| tools/native_determinism_check.py | Record one Mac ride as a Dolphin input movie, replay it against two modules, ... | yes / yes / no |
| tools/native_float_classify_spike.py | Isolated, source-receipted GXRuntime result-classifier experiment. | yes / yes / no |
| tools/native_float_conversion_spike.py | Check and time an isolated, bit-exact split of generated float conversions. | yes / yes / no |
| tools/native_float_module_spike.py | Prepare/build one private strict-FP ThinLTO object replacement. | yes / yes / no |
| tools/native_gamecube.py | Pinned macOS SSX 3 AOT prototype. Game bytes and builds stay under local/. | yes / yes / no |
| tools/native_module_opt_spike.py | Build and compare isolated O2/O3 AOT modules with strict FP and ThinLTO. | yes / yes / no |
| tools/native_probe_io_bench.py | Isolated CPU/storage bound for the actual native callback trace emitter. | yes / yes / no |
| tools/native_replay.py | Replay an iOS benchmark input sequence through a desktop test controller. | yes / yes / no |
| tools/native_route.py | Waypoint steering for the native ride harness: heading, pursuit, stick. | no / no / no |
| tools/pack_mipmaps.py | Give every texture in a pack the mip chain the guest texture had. | yes / yes / no |
| tools/patch_crossing.py | Compare logged rider positions with a patch's original and edited surfaces. | no / no / yes |
| tools/patch_executable.py | Rename SSX 3 events in the executable inside an image (level-selector names). | yes / yes / no |
| tools/patch_geometry.py | Conservative bounds for SSX bicubic power-basis terrain patches. | no / no / no |
| tools/patch_locale.py | Inspect or replace SSX 3 LOCH/LOCT/LOCL strings in a new ISO. | yes / yes / no |
| tools/patch_ui_glyphs.py | Repaint the GameCube button glyphs in SSX 3's UI sheets as Xbox-style icons. | yes / yes / no |
| tools/pine.py | Minimal read-only PINE client for a running PCSX2 (live EE memory reads). | no / yes / no |
| tools/prepare_emulator.py | Create a separate PCSX2 profile and launchers for the terrain experiments. | yes / yes / no |
| tools/probe_worlds.py | Inspect staged SSX world archives; export a Garibaldi terrain preview. | yes / yes / no |
| tools/race_course.py | Give an SSX 3 location a donor Tricky race course: track chain, gates, AI lines, race-line table. | no / no / no |
| tools/recompress_stream.py | Re-encode every SSB block of an SSX 3 world archive in place (same offsets, same sizes). | yes / yes / no |
| tools/refpack_encode.py | Small deterministic 10FB encoder for bounded SSX 3 block experiments. | no / no / no |
| tools/refpack_optimal.py | Optimal-parse 10FB RefPack encoder for fixed-capacity SSB blocks. | no / yes / no |
| tools/relayout_stream.py | Rebuild an SSX 3 world archive with our own SSB block boundaries. | yes / yes / no |
| tools/relocate_archive.py | Write a test ISO whose world archive lives inside a padding file's extent, or ... | yes / yes / no |
| tools/replace_terrain.py | Replace a location's terrain with a complete Tricky PBD terrain set. | yes / yes / no |
| tools/ride_autopilot.py | Steer the rider toward XY waypoints using live PINE position feedback and D-pad keys. | yes / no / yes |
| tools/ride_compare.py | Compare two native rider traces of the same course, one archive change apart. | yes / yes / no |
| tools/ride_course.py | Record and optionally steer a course descent using PINE position reads. | yes / yes / no |
| tools/ride_locations.py | Map a ride log's positions to SSX 3 locations by nearest terrain patch centre. | yes / yes / yes |
| tools/ride_route.py | After selecting a Green Station transport, wait for the spawn, optionally test the steering ... | no / no / yes |
| tools/terrain_contact.py | Measure rider contact with decoded SSX 3 terrain records. | yes / yes / no |
| tools/texture_compare_sheet.py | Build a side-by-side sheet comparing upscaler passes on the same textures. | yes / yes / no |
| tools/texture_dump_inventory.py | Inventory a Dolphin texture dump, split by ride phase, with an optional contact sheet. | yes / yes / no |
| tools/texture_pack_audit.py | Audit an upscaled texture pack against the dump it was built from. | yes / yes / no |
| tools/texture_pack_blend.py | Blend over-inventing pack textures back toward a faithful upscale. | yes / yes / no |
| tools/texture_pack_cap.py | Cap a pack's texture size, because upscale factor is not free on a phone. | yes / yes / no |
| tools/texture_pack_dds.py | Convert a PNG texture pack to block-compressed DDS, chain and all. | yes / yes / no |
| tools/texture_pack_plan.py | Sort a union of dumped textures into classes, each with the model that suits it. | yes / yes / no |
| tools/texture_pack_union.py | Union many courses' texture dumps into one deduplicated, family-grouped set. | yes / yes / no |
| tools/track_position.py | Log the rider position (EE 0x5409c0) at ~10 Hz to a JSONL file for N seconds. | no / no / yes |
| tools/upscale_textures.py | Upscale a directory of dumped game textures with a spandrel model, alpha kept separate. | yes / yes / no |
| tools/verify_inputs.py | Cross-check our ISO inventory/extraction against macOS bsdtar. | yes / yes / no |

`tools/*.sh` (not in the brief's glob; recorded for completeness):
`tools/muse_brief.sh`, `tools/odin_sampler.sh`, `tools/odin_wireless.sh`,
`tools/macos/build.sh`, `tools/macos/capture.sh`,
`tools/macos/green_station_ride.sh` — shell helpers, not audited line by line.

## 4. Broken references

File-level `.md` link check: every `[text](path/to.md)` target in tracked
Markdown resolves to an existing file — 0 broken at file level. (12 links
carry `#anchor` fragments; anchor validity was not audited.)

| Kind | Evidence | Detail |
| --- | --- | --- |
| `local/` paths referenced from public docs | `git grep -c "local/" -- '*.md'`: 53 of 62 tracked docs reference `local/`; 9 do not (`docs/locale-tables.md`, `docs/location-anatomy.md`, `docs/plan-gs-gpu-backend-2026-09-18.md`, `docs/rebuild-experiment.md`, both ps2recomp-spike files, `docs/research/ssx3-120hz-handoff-2026-09-13.md`, `docs/tricky-courses.md`, `local/research/G0/REPORT.md`). Heaviest: `docs/aloha-conversion.md` (69), `docs/gamecube-scenery.md` (31), `docs/plan-120fps-2026-09-17.md` (15), `docs/numbers-ledger.md` (14). Examples: `local/builds/gc-gari-013/`, `local/builds/gc-aloha-001`, `local/source/gamecube/...`, `local/reports/native-runs/...`, `local/research/aloha/...`, `local/research/M1/REPORT.md`, `local/game/gxbe69-stock/...` | Expected by design (`/local/` is gitignored): these resolve only on the author's machine. An outside reader cannot follow them. |
| Relative paths not in the repo | Root `README.md` tables: `builds/bump-002/SSX3-bump.iso`, `builds/grown-001/...`, `builds/gari-003/...`, `builds/scale-002/...`, `builds/name-001/...`, `builds/control-005/...`, `builds/control-006/...`, `emulator/` test-002 profile + launchers | `ls builds/ emulator/` → no such directories in the repo. |
| `ODIN-TESTING.md` | Root `README.md`: "also included as `ODIN-TESTING.md` in the shared build"; `docs/full-course-experiment.md`: same | File is not in the repo; only `docs/odin-testing.md` is. |
| Absolute machine paths in docs | Root `README.md`: `/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-010/`, `/Volumes/share/brad/games/ps2/SSX 3 (USA).iso`, `/Volumes/share/brad/games/ssx3-workbench/...` (Try-it-yourself + Storage + commands). `docs/full-course-experiment.md`, `docs/rebuild-experiment.md`, `docs/investigation.md`, `docs/gamecube-feasibility.md`, `docs/garibaldi-visual-comparison.md`, `docs/share-recovery.md`: `/Volumes/share/...` throughout. `docs/numbers-ledger.md`: `/Volumes/Extreme SSD/upstream-review/build-m1`, `/Volumes/Extreme SSD/ps2recomp-spike/P1/`, `/tmp/ps2xgs-build`, `/Volumes/Extreme SSD/ps2xgs/`. `docs/plan-120fps-2026-09-17.md`: `/Volumes/Extreme SSD/android-spike/...`, `/Volumes/share/.../native/GXBE69`. `native/README.md`: `/Volumes/share/brad/games/...` default + DTK extract one-liner | Author-machine paths; not resolvable by an outside reader. `docs/share-recovery.md` uses the `smb://YOUR_SMB_HOST/share` placeholder form. |
| Device/foreign-machine paths | `docs/plan-120fps-2026-09-17.md`: `/data/local/tmp/mg/`, device serial; `docs/research/ps2recomp-spike-2026-09-12/*`: `/mmt/share/...`, `~/dev`, `/tmp/PS2Recomp`, `/tmp/ssx3vu`, `/tmp/SLUS_207.72`; `docs/research/120hz-f-spike.md`: `/tmp/ssx3-f120/...` | Transcript/plan content from other machines; recorded, not resolved. |
| Removed-tool references | Checked root + native READMEs against `git ls-files tools/` | None found: every named script exists. |

## 5. Drafts produced (under `local/research/A3/drafts/`, ignored by git)

| Draft path | Content |
| --- | --- |
| `drafts/README.md` | Root README draft per brief §5 (purpose, quoted status numbers, repo map, build-without-game-data, not-included + supply-your-own, licensing, related repos) |
| `drafts/docs/README.md` | Docs index grouped by §1 classification, one line per doc |
| `drafts/ARCHIVE-CANDIDATES.md` | The 2 docs classified stale/superseded, each with reason + superseder; no deletion performed or stated |
| `drafts/native/README.md` | Corrected native README draft (existing file is present but dated; see §2) |
| `drafts/tools/README.md` | New tools index draft (file is missing; generated from §3 docstrings) |

## 6. Exact commands run

```sh
git ls-files '*.md' | sort
git status --short | head -n 100
cat .gitignore
git ls-files '*README*' | sort
find . -maxdepth 4 -iname 'README*' -not -path './.git/*' | sort
ls -la tools/ native/ docs/ docs/research/
git log -1 --format=%ad --date=short -- <each .md>
git grep -l "<basename>" -- '*.md'
git ls-files 'tools/*.py' | wc -l
git ls-files 'tools/' | wc -l
git ls-files native | head -n 60
ls native/*.py native/*.sh
ls -la tools/README* native/README* docs/README*
grep -n -i -e license -e MIT -e GPL README.md native/README.md native/ios/README.md docs/asset-policy.md
git grep -n 'local/' -- 'README.md' 'docs/*.md' 'docs/research/*.md' 'native/README.md' 'native/ios/README.md'
git grep -n '/Volumes/' -- '*.md'
git grep -n -e '/tmp/' -e '~' -e '/mmt/' -- '*.md'
git grep -n 'ODIN-TESTING' -- '*.md'
ls builds/ emulator/
mkdir -p local/research/A3/drafts/docs local/research/A3/drafts/native local/research/A3/drafts/tools
```

Plus two read-only Python scans (docstring/argparse/usage extraction over
`tools/*.py`; Markdown-link target existence over tracked `.md`), file reads
of the four READMEs, `docs/numbers-ledger.md`, `docs/todo.md` (head),
`docs/plan-120fps-2026-09-17.md` (head),
`docs/plan-gs-gpu-backend-2026-09-18.md` (head),
`docs/impl-plan-2026-09-15.md`, `docs/asset-policy.md`,
`docs/route-control.md` (head), `native/research.md` (head), and the
ps2recomp-spike README + `commands-and-outputs.md` (head).

## 7. What I could not do / did not do

- Did not run any tool with `--help` or otherwise execute repo code; usage
  data comes from static reads only (brief allows `--help`, but static
  extraction sufficed and avoids device/game dependencies).
- Did not verify `#anchor` fragments on the 12 anchor-bearing `.md` links;
  file-level existence only.
- Did not open the vendored `third_party/` READMEs beyond listing them;
  upstream trees keep their own docs.
- `native/ios/README.md` lines ~200–406 were sampled (to line 200 in full,
  remainder via targeted grep), not read end to end.
- Inbound-link counts for the four `README.md` files and five `REPORT.md`
  files are basename-level and shared between same-named files; only
  `native/README.md` was additionally checked by full path. The §1 inbound
  column condenses to doc-tree linkers; the local gate reports (notably A2)
  additionally reference many files (see the `git grep -l` command in §6).
- `local/research/A2/REPORT.md` (the A2 secrets audit) was committed by
  parallel activity during this run: the opening file count was 61, the
  closing count 62. Its row above covers it; nothing else changed.
- Did not check per-script `--help` output, device/emulator behaviour, or
  whether build commands still succeed (no builds per brief).
- Did not commit. The brief's commit step (`git add -f` + `[A3]` commit with
  `Co-Authored-By` / `Claude-Session` trailers) was skipped per the
  read-only instruction; all output stays under ignored `local/research/A3/`
  and `git status` shows no tracked-file change.
- Time box respected: single pass, no follow-up verification runs.


