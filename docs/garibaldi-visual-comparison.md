# Garibaldi visual comparison — September 12, 2026

**Update: build gc-gari-013 repairs the terrain lighting scale mismatch.**
The original and uncorrected import use identical images with different
lightmap multipliers: 1× in Tricky, 2× in SSX 3, confirmed across 108 matching
image pairs. The shared importer now translates that convention and records
each conversion. New native gameplay captures retain snow detail that build
012 clipped to white. See the [new comparison gallery](../local/evidence/garibaldi-material/lighting-comparison.html),
[comparison sheet](../local/evidence/garibaldi-material/lighting-comparison.png)
and [reusable material workflow](gamecube-materials.md).

This fixes a demonstrated cause, not every visual difference. The import
still uses SSX 3 fog/backdrop and lacks donor scenery; exact camera matching
and the jump visibility regression remain open. All screenshot comparisons
below and in the new gallery use different viewpoints/race times.

The original build-012 investigation follows. Original Tricky
gameplay on both PS2 and GameCube has more gray-blue snow, darker ice and
better separation between adjacent slopes. Build **gc-gari-012** often turns
those surfaces into bright white and cyan. The difference also reproduces
on Mac using the archive previously verified on the iPhone.

Open the [side-by-side gallery](../local/evidence/garibaldi-comparison/comparison.html)
or the [comparison sheet](../local/evidence/garibaldi-comparison/comparison.png).
Each gallery image links to its full-resolution, unmodified PNG.

## What was compared

| Capture | Source and execution |
| --- | --- |
| PS2 original | `SSX Tricky (USA).iso` on `/Volumes/share/brad/games/ps2/`, running in PCSX2 2.8.2 with a separate profile; Single Event → Race → Amateur → Garibaldi |
| GameCube original | `SSX Tricky (USA).rvz` on the same share, extracted into `local/game/gste69-original`; unmodified GSTE69 game data, JIT CPU, no SSX 3 module or mods |
| Current import | `gc-gari-012`, running in the project's Mac AOT player through the Snow Jam Race slot |

The GameCube reference player uses the project's existing Dolphin/Metal
renderer libraries. A separate local executable selects the normal JIT CPU
core; the production player and its game restrictions were not changed.
Both Mac GameCube runs used the Metal validation layer. The original's
startup logged a FIFO warning; the selected captures are later gameplay,
with the PS2 captures providing an independent reference for the broad
visual findings. These are emulator captures, not console-hardware captures.
The players and screenshot encoding ran concurrently; their timing is not
an isolated performance benchmark or an iPhone performance result.

The gallery compares representative ice, painted banks and warning ramps.
Camera positions, riders, routes and race times differ. It is a qualitative
comparison, not a registered pixel comparison or a numerical fidelity score.
There is no color correction; only the displayed thumbnails are resized.

The import archive is 101,519,744 bytes, SHA-256
`0a619708659ab5136a2a1354ad51c15ea536719adcaff4a0cc98d61369053fed`.
It matches the earlier actual iPhone readback. The phone required its
passcode during this comparison, so these are **not new iPhone screenshots**.

## Findings

1. **The remaining color problem is visible in final rendering.** The
   originals retain variation within white snow and darker blue-gray areas
   on ice and shaded banks. The import contains much larger nearly white
   areas and stronger cyan highlights. Seeing this against the GameCube
   original as well as PS2 makes console-version differences an insufficient
   explanation. It does not identify the exact shader or material operation
   responsible.

2. **Correct image bytes are necessary but insufficient.** The donor image
   payload audit passes, and recognizable ice and red paint survive in the
   import, yet their rendered appearance differs. Inspect terrain material
   selection, lightmap combination, vertex color and fog together. The
   importer currently copies one Snow Jam patch template's surface type and
   flags onto all donor patches (`make_record`), then replaces image bindings
   (`bind_patch`). That is a concrete place to investigate, not a proven
   explanation for every color difference. The earlier normal/lightmap
   correlation result did not establish correct rendered brightness.

3. **Missing scenery changes how the course reads.** The originals have
   trees, yellow barriers, turn/jump signs, grandstands and structural edges
   around the terrain. The import lacks these donor objects and shows the
   SSX 3 mountain backdrop. Those objects communicate the edge of the track,
   the direction of a turn and the distance to a landing. Their absence is
   visible; how much it contributes to the reported surprise at a particular
   jump remains an inference.

4. **Some seams exist in the reference too.** Original captures contain
   abrupt ice/snow transitions and visible patch boundaries. A seam should
   be classified against its corresponding source patch before changing UVs
   or geometry. The current views do not establish which individual import
   seams are wrong.

5. **These stills do not close the pop-in report.** The earlier fixes remove
   obsolete host occlusion curtains and make terrain bounds conservative.
   This run reaches gameplay and results, but the sparse screenshots and
   unsteered resets do not prove that every approach remains visible from
   frame to frame. Brightness and missing scenery can obscure terrain that
   is already being drawn; actual late visibility needs a separate motion
   check at the reported location.

## Recommended next work, in order

1. **Capture equivalent terrain draw state and fix the material/lightmap
   mismatch.** Select a known donor patch in an ice bowl and a painted ramp.
   Compare texture inputs, lightmap coordinates, color-combine operations,
   vertex color and fog between Tricky and SSX 3. Change one variable at a
   time and keep source image bytes available as the control. Acceptance is
   restored snow detail and shadow/color balance at repeatable camera poses.

2. **Make a short visibility regression for each suspect jump.** Add rider
   and camera coordinates plus visible patch IDs to capture metadata. Record
   the approach, takeoff and landing at short frame intervals, including a
   reset/restart. This can distinguish missing draw calls from low contrast
   and prevents a healthy FPS log from being treated as a visual pass.

3. **Import the course environment as a complete set.** Bring in Garibaldi's
   backdrop, fog, scenery, rails and object collision, with explicit ownership
   of retained SSX 3 content. Start with barriers, jump signs and objects that
   define landings. Treat this as part of course correctness.

4. **Keep source captures and build identity with each course build.** Store
   the source patch/camera pose, game variant, renderer settings and world
   hash alongside a small reference set. Keep archive validity, visual
   fidelity, route completion and phone performance as separate checks.

These are the immediate visual priorities within the broader
[architecture recommendations](architecture-review.md).

## Evidence

All captures and game files remain under ignored `local/`.

- `local/evidence/garibaldi-comparison/comparison-manifest.json`: selected
  source paths and SHA-256 hashes; nine copied PNGs verified against originals.
- `local/evidence/garibaldi-comparison/verification.json`: archive identity,
  production-player identity and source-disc checks.
- `local/evidence/garibaldi-comparison/ps2-profile/PCSX2/snaps/`: original PS2
  capture sequence, including the first jump and subsequent banks.
- `local/native/profiles/tricky-original-review/ScreenShots/GSTE69/`: original
  GameCube sequence; local reference run exits successfully after 720 seconds.
- `local/native/profiles/gari-comparison-012/ScreenShots/GXBE69/`: fresh build
  012 sequence. Run report: `local/reports/native-runs/20260912-123140.json`.
  The run exits successfully with native execution, zero logged invalid
  memory accesses and zero failed code verifications.
- `local/evidence/garibaldi-comparison/iphone-lock-state.json`: direct phone
  capture was unavailable because a passcode was required.

## Build 013 repair evidence

- `local/evidence/garibaldi-material/validation.json`: consolidated build,
  runtime and phone identity; all 108 repository tests pass, including the
  exhaustive RGB565 transfer, texture layout and draw-comparison regressions.
- `local/evidence/garibaldi-material/paired-materials.json`: 108 matching
  terrain base/lightmap pairs, all source scale 1 and target scale 2. Full
  raw captures and diagnostic build commands are in the same directory.
- `local/builds/gc-gari-013/experiment.json`: versioned material profile and
  per-lightmap source/output hashes and error bounds.
- `local/evidence/garibaldi-material/archive-audit.json`: only 16 donor
  lightmaps differ; terrain records and base textures are byte-identical to 012.
- Build identity: 101,749,120 bytes; SHA-256
  `3efd84fffab68df7caba7b6e8dfa04859ea0ada545d7711e9953ce363c7e6032`.
- `local/evidence/garibaldi-material/lighting-comparison-manifest.json`:
  nine unmodified original/before/after captures and their hashes.
- `local/evidence/garibaldi-material/durable-run-verification.json`: the
  reusable diagnostic tool built a separate original player, captured 108
  valid schema-1 draw records and exited successfully.
- `local/reports/native-runs/20260912-133252.json`: the unchanged production
  AOT player ran for 481.5 seconds, reached gameplay/results and exited 0,
  with 2,636,220,256 native dispatches, zero invalid memory accesses, zero
  failed code verifications and no JIT fallback runs. Process lifetime includes
  menus and loading; this is not an uninterrupted route or phone performance test.
- `local/evidence/garibaldi-material/iphone-world-verification.json`: build
  013 copied to the iPhone and read back byte-for-byte. The phone still requires
  its passcode, so the repaired screenshots are Mac captures, not phone captures.

The source traces also show a different fog state, reinforcing that lighting
transfer alone does not restore the entire environment. The gallery is a
qualitative check of the repair, not a registered pixel comparison.
