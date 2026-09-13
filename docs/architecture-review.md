# Architecture review — September 12, 2026

The GameCube AOT runtime is the right foundation for the intended iPhone
experience: Tricky courses with SSX 3 handling. The most urgent work is in
course conversion and acceptance checks. The native runtime already boots
and rides; imported content can still be internally valid enough to run
while displaying the wrong art or hiding a real slope.

This review covers the September 9–11 Claude/Codex project sessions, their
commits and evidence, the current importer and iOS shell, and the separate
`spike/120hz` worktree. Historical conclusions were checked against the
archives and new runs where possible. Local screenshots and game bytes
remain under ignored `local/`; they are not repository assets.

## Findings addressed in this change

| Problem | Evidence | Correction |
| --- | --- | --- |
| Snow sometimes acquires stock tree/rock art | 51 of 52 donor texture IDs in build 009 collide with different payloads elsewhere in the world | Allocate global IDs, grow the GDB global tables, preserve stock resources, validate the whole rebuilt archive |
| Slopes disappear behind empty space | Snow Jam's 17 occlusion curtains survived terrain replacement; one crosses 210 forward route sight lines | Remove the host curtains during full replacement |
| Curved terrain has underestimated bounds | Dense samples exceed old bounds by over one unit on 1,131 patches, up to 24.01 units | Bound the Bezier control hull of the serialized coefficients, with outward float32 rounding |
| A failed launch can count as a successful run | A Metal initialization failure still emitted module/shutdown markers with zero native dispatches | Require actual native execution and reject logged invalid accesses or code verification failures |
| Earlier art verification was overstated | Normal/brightness correlation favors an orientation but never compares final rendered pixels to Tricky | Keep orientation evidence separate from visual fidelity acceptance |

The first three corrections preserve the imported terrain coefficients,
UVs and lightmap cells. Build 012's 52 textures and 16 lightmaps retain the
donor pixel payloads. They address specific artifacts. A subsequent
[original-game screenshot comparison](garibaldi-visual-comparison.md) confirms
that rendered snow/ice color and the course environment still differ.
See [the format notes](gamecube-world.md) for offsets and build findings.

The follow-up build **gc-gari-013** fixes a demonstrated material mismatch:
108 matching image pairs use a lightmap multiplier of 1 in Tricky and 2 in
SSX 3. The shared [material profile](gamecube-materials.md) translates that
convention, preserving base textures and recording each lightmap conversion.
This is the first piece of the proposed validated course compiler. Separate
diagnostic builds now make material-state comparisons reproducible. Donor
environment ownership and frame-by-frame visibility checks remain priorities.

## Prioritized recommendations

1. **Make course import a validated compilation step.** Start with a small
   course model containing patch geometry, image bindings, paths, visibility
   and resource references, then serialize it through the GameCube writer.
   Keep the source readers and endian-specific writers separate from shared
   geometry and route logic. Add checks at these boundaries rather than
   repeatedly fixing raw offsets in experiment scripts. The global image
   audit and conservative bounds added here are the first part. Next, check
   every retained resource reference and the complete set of surface/material
   flags. Completion means a bad reference or undersized resource table fails
   the build with a source patch or resource ID before the game is launched.
   The scenery work adds another requirement: budget geometry pools and image
   residency separately. RAM snapshots found geometry fully loaded while the
   image bank stalled, despite similar total archive size. Derive residency
   from surviving page users, preserve sparse table reservations across
   sibling-group updates, and encode target flags through explicit profiles.
   A donor flag copied verbatim corrupted display lists during riding.

2. **Make ride checks observe game state and compare to the source.** Current
   timed menu input can stop at a briefing and still produce hundreds of
   healthy FPS samples. Add a narrow runtime telemetry interface for game
   state, rider/camera position, progress and reset events. Replay should wait
   for a state with a deadline, then capture fixed route checkpoints and
   restart. Compare those views against original Tricky, including the
   approach to each landing. Track boot, ride, route completion, restart and
   visual comparison as separate results. The new execution gate is only a
   basic prerequisite. Prefer a short, repeatable route check now; the long
   phone soak the user chose to defer should stay deferred.
   The gate now also rejects stale screenshots and malformed GPU commands;
   cached healthy FPS readings persisted throughout a stalled load.

3. **Give an imported course explicit ownership of its environment.** Replacing
   Snow Jam's patches leaves its surrounding mountain, sky/fog settings,
   scenery and event dependencies available to stream. Define a course
   manifest listing what is imported, retained, removed and referenced.
   Bring over donor scenery, rails and collision together so the visible
   course and rideable course agree. Resolve adjoining-location visibility
   and resets deliberately. Initially keep the existing Single Event slot;
   add narrow loader/event hooks when ownership cannot be expressed in the
   world data. Completion means the opening, descent, landings and finish
   work without depending on accidental Snow Jam residency.

4. **Use one immutable recipe and a verifiable device content version.** Tie
   source hashes, transform, cleanup choices, converter revision, output hash
   and runtime build to one manifest. Build and validate once, then copy that
   artifact to Mac, iPhone or a Dolphin ISO. The terrain tool now refuses to
   overwrite an existing build directory. Next, stage device content, verify
   it, and activate it on a cold launch; record the active world hash alongside
   phone logs. This prevents a phone report or screenshot from silently being
   attached to a different experiment. Retain shared source caches and
   separate per-branch outputs, particularly for the 120 Hz worktree.

5. **Separate the iOS session, input routing and interface.** `App.mm` currently
   owns controls, audio/lifecycle coordination, a background runtime, logging
   and benchmark behavior. Extract a small `RuntimeSession` with explicit
   start/stop/error states and an `InputRouter` with a shared action map.
   Let touch and physical controllers feed the same actions, with release on
   interruption. This makes save/relaunch and controller checks tractable
   without changing game physics. Do this incrementally around the working
   app; there is no need for an engine rewrite.

6. **Keep 120 Hz presentation as a measured, isolated experiment.** The
   existing branch's recorded color-only attempt did not meet its budget:
   roughly 4.9 game FPS at 0.36× speed versus the approximately 59.4 FPS
   baseline, with substantial submission-to-presentation delay. Those are
   measurements of that implementation, not proof that interpolation is
   impossible. The September 13 source check finds the explicit wait in teardown,
   not the frame loop; instrument drawable acquisition, GPU and presentation
   scheduling before attributing the stall. See the
   [follow-up timing analysis](research/120hz-analysis.md). Then compare a lower-cost path with depth/camera-assisted vectors and
   HUD exclusion. Preserve the game's 60 Hz simulation. Promote the feature
   only after an actual ride shows lower latency and acceptable artifacts on
   the phone, with a reliable 60 Hz fallback.

Keep the pinned GameCube/Dolphin/RecompCore stack and targeted reverse
engineering. Moving the runtime to PS2 or rewriting SSX physics would create
a much larger validation problem without addressing these importer bugs.
The Odin can continue using the same compiled course in Dolphin while a
native Android shell remains a separate deliverable.

## Evidence and remaining limits

The archive and geometry audits are in
`local/evidence/garibaldi-review/`: `global-image-audit.json`,
`bounds-audit.json`, and `course-audit.json`. Build 010's Mac run is
`local/reports/native-runs/20260912-111628.{json,log}` with captures in
`local/native/profiles/gari-review-fixed/ScreenShots/GXBE69/`.
It reaches gameplay and results with no logged invalid accesses. An
unsteered run includes resets and a backward progress reading; it does not
establish a clean traversal of every checkpoint or finish trigger.

Pixel payload preservation and corrected resource lookup are verified;
the later PS2 and GameCube source captures show that rendered color and
environment fidelity remain open. Mac GPU runs
used the Metal debug layer after this machine's initial render-encoder
initialization failure; their timing is a functional check, not an iPhone
performance result.

The geometry/resource repair build is **gc-gari-012**. Its global image audit and dense box/sphere
audit are in `final-course-audit.json`; the full synthetic test suite passes
100 tests. Device copy and readback succeeded, recorded in
`iphone-world-verification.json`. The first attempted phone smoke launch was
blocked by iOS because the device was locked; that attempt supplies no new
phone gameplay or performance evidence.

Later September 12 update: the share was remounted and
[automatic share recovery](share-recovery.md) is installed. Original PS2 and
GameCube Garibaldi gameplay was captured alongside a fresh build 012 run.
The [comparison](garibaldi-visual-comparison.md) prioritizes material/lightmap
rendering, repeatable jump-visibility checks and donor environment ownership.
The views are representative rather than camera-registered; frame-by-frame
pop-in acceptance and new phone captures remain open.

The subsequent lighting repair is **gc-gari-013**, copied to the iPhone and
verified by actual readback. Its native run exits successfully with zero
invalid accesses and failed code checks. The phone still requires its
passcode, so corrected rendering is verified on Mac, with new phone gameplay
and performance evidence still open. See `local/evidence/garibaldi-material/`.
