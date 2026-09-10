# Roadmap: Garibaldi in SSX 3, and a generic Tricky → SSX 3 course patcher

Date: 2026-09-10. This plans the work after the first ridden terrain edit. Each
milestone has a gate that must be demonstrated in a cold-booted PCSX2 session
before the next one starts. Dates are deliberately absent; the gates are the plan.

## Where we are

- Formats decoded: SSX 3 BIGF/SSB/SDB/PHM/PSM, Tricky C0FB/PBD, RefPack 10FB.
- One 32 KiB block can be recompressed in place; the engine accepts it.
- Editing a terrain patch's coefficients changes both the rendered snow and the
  rider's ground contact, with no change to the separate type-12 collision data.
- We can read live emulator memory, steer the rider to a waypoint, and measure
  the rider against any patch surface.

## What belongs in this repository

Keep the repository public-safe from the start. It should hold **tools, tests,
and documentation**, never game data, whatever the current visibility is.

In:

- Python tools and the `ssxport` package (below), with synthetic-data unit tests.
- Format notes, experiment logs, manifests of hashes, offsets, counts, names.
- Small derived numbers that identify results (SHA-256 values, byte offsets).

Out (stays on the network share or in ignored `local/`):

- ISOs, extracted archives, decompressed streams, meshes, textures.
- Emulator profiles, BIOS, memory cards, save states, memory dumps.
- Game screenshots and window captures. They are EA imagery; keep them as
  evidence on the share and describe them in the docs instead.
- Reports that embed disc bytes (the world reports include header samples).

Licensing: the Python tools are our own implementations, but their layouts were
learned from GlitcherOG/SSX-Library (GPL-3.0). Releasing under **GPL-3.0** avoids
any compatibility argument and matches the reference and decompilation
communities. This is a recommendation, not yet applied; adding `LICENSE` is a
decision for the repository owner.

Distribution model for a public patcher: the tool runs on the user's own SSX 3
and SSX Tricky discs and writes a new image locally. It must never ship or
download game data. A binary diff between an EA image and our output would
contain EA data, so **the patcher is the deliverable, not a patch file**.

## Package shape

Grow the current `tools/` scripts into one package with a CLI, migrating one
command at a time so the verified scripts keep working:

```text
ssxport/
  iso.py          ISO9660 read, directory-entry rewrite, streamed image build
  big.py          BIGF and C0FB archives
  refpack.py      10FB decoder and encoder (optimal parse)
  ssx3/           sdb.py, ssb.py, patch.py, names.py, collision.py
  tricky/         pbd.py, ssh.py, ltg.py
  geometry.py     bicubic evaluation, fitting, transforms, joins
  build.py        world rebuild: groups → blocks → SSB/SDB → archive → image
  emu/            pine.py, autopilot, crossing analysis (optional extras)
  cli.py          ssxport inspect | extract | build | patch | verify | ride
```

`ssxport patch --ssx3 SSX3.iso --tricky TRICKY.iso --course garibaldi --into
LOCATION --output OUT.iso` is the end-state command. `verify` reads the output
back and reports every hash the docs cite. `ride` wraps the emulator tools and is
macOS-only.

## Milestones and gates

### M2. Growable world rebuild

Today's edits must fit inside one 32 KiB block. A course import needs groups of
arbitrary size and an archive larger than the original.

Facts that shape this:

- `DATA/WORLDS/BAM.BIG` is immediately followed by `MUSIC.BIG`; there is no slack.
- The disc has two 256 MiB padding files, `PAD1.000` at offset 6,088,704 and
  `PAD0.000` at 274,524,160. Rewriting the world archive's ISO9660 directory
  entry to an extent inside a padding file gives up to 256 MiB without changing
  the image size or moving any other file.
- The SDB group record (68 bytes) carries the resource count, group index, SSB
  offset, a memory-size field that is not simply the decoded size, and per-kind
  resource counts. The 96-byte spatial records carry min/max boxes per location.

Steps and gates:

1. **Full in-place recompress control.** (Encoder done: the optimal parser fits
   the worst blocks with room to spare; control-002 build and ride pending.)
   Re-encode all 3,328 blocks with our encoder at the original boundaries. Gate: a byte-verified image cold-boots and
   plays through at least three locations. If blocks exceed capacity, first
   improve the encoder (optimal parsing over the 10FB command set) rather than
   moving boundaries.
2. **Relocated archive control.** Done as control-003: unchanged `BAM.BIG`
   written into `PAD0.000`'s space with a rewritten directory entry cold-boots,
   streams Green Station, and rides normally. The game reads the archive through
   the file system, not a hard-coded LBA.
3. **Re-laid-out stream control.** Done as control-005: our own block
   boundaries (3,343 blocks), regenerated SDB offsets, relocated archive;
   plays hub E, hub A, and connector A_ASS1. A race location is still to be
   ridden. (control-004 hung because the BIGF writer altered member names;
   fixed.) The memory-size field is decoded: bytes of kinds
   0–12 including headers (see the investigation log), so a same-content
   re-layout only rewrites each group's stream offset.
4. **Grown group.** Done as grown-001: five raised patch copies appended to
   hub A's group with updated SDB and location counts; they render and the
   rider rides on them. Whether large additions hit a per-location memory
   budget is still untested (add hundreds of patches next, then thousands).

Image size is not a constraint: `relocate_archive.py --append` grows the ISO
(control-006 plays); the padding-file mode remains as an option that keeps the
image size unchanged.

### M3. Patch record semantics

Only 64 of the 432 bytes of a patch are understood. Needed for import: UV/texture
assignment, surface type (speed, sound, particle), lightmap references, and the
unknown header/tail words. Method: one-field-at-a-time edits ridden on the
natural line with `patch_crossing.py` and captures. Also: move a patch outside
its stored bounds to learn what the bounds and spatial boxes gate (culling,
collision, both), and delete a patch to learn how holes behave.

Bisection so far: id words 336/340/416 bind textures/lightmaps (foreign values
render dark); material word 8 selects the surface response (0x90003 sinks the
rider like deep snow); location word, flags, lightmap rectangle, and corner UVs
showed nothing on a hub snow patch. Still needed: a texture swap that renders
(use id words from a patch in the *same* location with a different look), and
the meaning of the flags word on jumps, rails, and walls.

Gate: a table of every patch field with an observed effect or a "no visible
effect within tested range" entry, and a texture swap that renders.

### M4. Garibaldi shape in an SSX 3 location (fixed size)

Replace the patches of one existing connector or run section with transformed
Garibaldi patches, keeping patch count and SSX 3 materials, so M2 is not yet
required. Transform: scale to SSX 3 units (calibrate with rider speed and known
object sizes), rotate so downhill is −Z, translate onto the existing start
point. Join the ends to the surrounding SSX 3 terrain with fitted boundary
curves so there is no seam or drop.

Gate: ride from the SSX 3 spawn through Garibaldi geometry and back out onto
SSX 3 terrain without a reset. This is the first "Garibaldi in SSX 3" moment.

Status: **met by gari-003** (92 Garibaldi patches overlaid on the Green Station
line; the rider rides two imported stretches and returns to hub terrain, no
reset). Open: interleaving surfaces trap the rider late in the section, flat
lighting from a shared lightmap rectangle, and the Tricky/SSX 3 unit ratio.

### M5. Full Garibaldi course

All 3,885 patches into a run location, using M2 for size. Then the non-terrain
content: textures (`gari.ssh` → SSX 3 texture resources), lighting/lightmaps,
collision for props (type-12 and instances), rails and jumps as SSX 3 objects,
start and finish, reset points, AI paths for opponents (`gari.aip`), course
name in PHM/PSM and the transport map. Replace an existing SSX 3 race so menus
and progression need no new entries.

Status (2026-09-10): memory budget verified (scale-002: 1,439 imported
patches load and ride, see docs/peaks-and-locations.md); the level selector
is two fixed tables in the executable, so course names can be swapped without
UI work. The "all of Tricky on one mountain" idea maps onto replacing the 17
events, not a sixth peak. name-001 shows "Garibaldi" in the transport menu
(tools/patch_executable.py). Non-terrain content still open.

Gate: a race on Garibaldi with medals awarded, no soft locks, on desktop PCSX2.

### M6. Generic patcher

Turn the Garibaldi pipeline into `ssxport patch` for any Tricky course:
per-course transform presets, a destination table of SSX 3 locations with
their capacities, and a verification report. Test with at least two more
Tricky courses, one of them a freestyle course.

Gate: a second course imports with configuration only, no code changes.

### M7. Odin and release

Run the M5 image on the Odin's PCSX2 build; measure frame time in the imported
course against the original; fix streaming hitches (block sizes, group order).
Public release: GPL-3.0, no game data, reproducible verification hashes.

## Risks and unknowns

- The memory-size field and per-group limits in the engine may cap group size
  below a full course; a course may have to be split across groups with
  streaming boundaries that follow the original design.
- Textures and lightmaps are entirely unexplored; Tricky and SSX 3 texture
  formats may differ in swizzling and palette layout.
- Tricky's collision, rails, and AI paths have no examined SSX 3 counterparts.
- Emulator-only validation cannot rule out behaviour that differs on hardware,
  but the Odin target is also an emulator, so this risk is acceptable.

## Immediate next steps

1. M2 step 1: measure the full in-place recompress; improve the encoder if
   needed; build and ride control-002.
2. M2 step 2: relocated-archive control-003.
3. Start the `ssxport` package with `iso.py`, `refpack.py`, and the existing
   tests, moving one script at a time.
