# GameCube SSX 3 world format (GXBE69)

Updated: 2026-09-12. Decoded by diffing the same Snow Jam records on the PS2 and
GameCube discs; implemented in `tools/gamecube_world.py` and
`tools/gamecube_terrain.py`, tested by `tests/test_gamecube_world.py`.

## Container

`files/data/worlds/bam.big` is the same BIGF archive as PS2 with members
`bam.gdb` (index, PS2 `bam.sdb`), `bam.gsb` (stream, PS2 `bam.ssb`), `bam.ghm`,
`bam.gsm`, `serial.txt`. The PS2 BIGF reader/writer applies unchanged.

## Index (`bam.gdb`)

Identical record layout to the PS2 SDB, with every integer big-endian:
header counts at 8 (49 locations, 275 spatial records, 205 stream groups),
88-byte location records from 80, 96-byte spatial records from the next
16-byte boundary, then 68-byte group records (u16 count, u16 index, u32 stream
offset, u32 memory bytes for kinds 0-12, 14 × u16 per-kind counts, 28 zero
bytes). Snow Jam is still `ARA1`: groups 26-36, with ten texture/lightmap
groups (kinds 9 and 10) and one gameplay group, 36, holding the same 6,884
resources by kind as the PS2's group 33 (1,913 terrain patches, 963 kind-2,
3,052 kind-3 props, 285 kind-12 collision, 130 kind-0, ...).

The header also contains **28 global resource capacities at offset 24**, one
big-endian halfword per kind. These allocate the RID-indexed tables for track
255 resources; they are separate from the per-location and per-group counts.
Stock kind 9 capacity is 788 at offset 42, kind 10 is 662 at offset 44.
GXBE69 passes GDB + 24 to the table constructor at `0x8024A69C`; the texture
loader reads offset 42 with `lha` at `0x80247C94`. New global IDs require
capacity >= max RID + 1, with the signed-halfword limit respected.

Location records likewise contain **28 capacities at offset 32**, filling
the entire 88-byte record. The constructor at `0x8024A9F8` reads four groups
of seven signed halfwords. Kinds 24–27 are the scenery color, position,
normal and UV arrays. The writer preserves their existing reservations and
grows them for new IDs, as it does kind-23 buffer groups. Reading only 24
counts concealed these tables and allowed scenery probes to overrun them.

## Stream (`bam.gsb`)

`CBXS`/`CEND` blocks of 32,768 bytes with a **little-endian** u32 length after
the tag, RefPack `10 FB` payload, zero padding. Group stream offsets in the
index are block-aligned. Resource headers inside a decoded group are kind (u8),
payload length (**big-endian** u24), track (u8), resource id (big-endian u24).
The PS2 block packer (`relayout_stream.pack_group`) produces valid GameCube
blocks because it only writes the little-endian block length.

## Terrain resource (kind 1, 430 bytes; PS2 432)

| Offset | GameCube | PS2 (432-byte) |
| ---: | --- | --- |
| 0 | 0 | per-location id |
| 4 | 0x9B7F4F tag | 0x4045B7 tag |
| 8 | signed 16-bit surface type (0 = normal snow) | same halfword meaning, little-endian |
| 10 | 16-bit collision flags (stock example 9) | same halfword meaning, little-endian |
| 12 | flags | flags |
| 16-31 | lightmap atlas offset/size (different atlas values) | same meaning |
| 32-63 | four corner UV pairs (identical values) | same |
| 64-319 | 16 coefficient vectors, big-endian f32 ×4, w = 1 | little-endian |
| 320-335 | bounding sphere centre + radius | same |
| 336-383 | **four corner positions** (12 f32) | at 368 |
| 384-407 | **bounds min, max** (6 f32) | at 344 |
| 408 | ordinal = `track << 24 \| rid` | at 336 as `rid << 8 \| track` |
| 412 | page reference | at 340 |
| 416 | packed index pair (halves swapped relative to PS2) | at 416 |
| 420, 424 | links, 0xFFFFFFFF | same |
| 428 | two zero bytes | u32 0x11483C placeholder |

All 1,913 Snow Jam patches and all 3,885 Garibaldi patches have bit-identical
coefficient vectors on both platforms, so the PS2 placement transform applies
directly: source anchor (-1214.8, -195.5, -768.55), target
(-118613.68, 15753.8, -228880.14), yaw 73°, scale 0.55.

Bounds must enclose the whole bicubic surface. The old 8×8 sampling grid
missed extrema on 1,131 Garibaldi patches by more than one game unit (worst
24.01 on a denser audit). `patch_geometry.surface_bounds` now converts the
serialized power coefficients to Bezier control points and encloses their
convex hull, rounding bounds outward to float32. The sphere encloses this
box after its centre is rounded; location bounds aggregate these full boxes.

## Other records (ported in `tools/gamecube_cleanup.py`)

Kind 13 object tables (16-byte header, first byte 1 instead of 0, count at
12, 24-byte rows with the instance id at row +12), kind 18 NIS tables (72
bytes) and kind 16 scripts (same offsets: program index at 56, definition
base at 64, kind-3 binding table at 68, definitions at 76, spline table at
84) keep the PS2 layout with big-endian words. Instance ids are
`track << 24 | rid`. The 4-byte script header bytes `00 10 00 00` are byte
identical on both discs. LUN programs are big-endian with magic 0x4E554C and
the same 20/36/36 empty-return shape. Spatial (texture-tree) records are the
same 96 bytes with big-endian floats, child indices at 80/84 and the leaf
group at 88. Template patch 1673 binds texture 13 and lightmap 109, which
lives only in texture group 31 (PS2: lightmap 144 in group 32).

Kind 11 contains the host terrain's occlusion curtains (Snow Jam has 17,
208 bytes each). Full terrain replacement removes them automatically;
round-trip builds retain them. One retained Snow Jam curtain crossed 210
forward sight lines in an offline audit of the imported Garibaldi route.
Moving the terrain without replacing its occluders can hide the slope
until the camera crosses a wall that no longer has visible geometry.

## Textures and lightmaps (kinds 9 and 10, `tools/gamecube_textures.py`)

Each record is one image: a 32-byte header, then the pixel levels, then for
CI8 a 32-byte palette chunk header (`32 000000 00ff 0001 00ff 0000 1000 0000
00000020`, padded) and 256 × u16 RGB5A3. Header: u8 type = `0x10 | GX format`
(0x19 CI8, 0x1e CMPR are the only ones in the stock world; the Tricky sheets
also use 0x14 RGB565 and 0x15 RGB5A3), u24 size (32 + pixel bytes for CI8,
0 otherwise), u16 width, u16 height, u32 0, then bytes `30 00 nn 00` with
`nn` = mip levels − 1, u32 0x20, 12 zero bytes. Pixels are in native GX
tiling (CMPR 8×8 tiles of four 4×4 DXT1 blocks, big-endian colours; 16-bit
in 4×4 tiles; CI8 in 8×4 tiles). Surveyed over all 4,571 records: kind 10
always has one level, kind 9 one to four. Kind 9 rids repeat across
locations (rid 11 is in most), kind 10 rids are unique world-wide (0-661).

A terrain patch binds its images through word 416 = `texture rid << 16 |
lightmap rid` (patch 1673: texture 13, lightmap 109) and word 412 =
`0x80000 | texture group index` (Snow Jam's ten values are groups 26-35).
Words 16-31 are the patch's rectangle in the lightmap sheet (u, v, w, h)
with a half-texel inset (a 16 px cell of a 128 px sheet is stored as
16.5/128, 15/128); words 32-63 are the four corner UV pairs in corner order.

GameCube Tricky course sheets (`gari.gsh` textures, `gari_L.gsh`
lightmaps) are SHPG containers whose entries are the same image records with
a 16-byte header. `gari.nbd` patches bind them directly: i16 at 428 is the
texture index into `gari.gsh` (the material table is not involved; the same
words on the PS2 `gari.pbd` agree), i16 at 430 is the lightmap sheet index,
the vec4 at 0 is the lightmap cell (u, v, 1/16, 1/16: 8 px cells of a 128 px
sheet) and the four vec4s at 16 are corner UVs, v in [−1, 0] where SSX 3 uses
[0, 1] for the same corner order. Garibaldi's terrain uses 52 of the 121
textures (26 snow variants, plus stripe, ramp and sign textures) and all 16
lightmaps, 947 KB in total. `--textures/--lightmaps` on the terrain replacer
appends them to the pinned group and rewrites the binding words. IDs are
allocated after the world's existing IDs and reserved global capacity;
the GDB capacities grow with the new records. Stock images are preserved.
The rebuilt archive is checked for conflicting global image payloads and
out-of-capacity IDs. Garibaldi uses texture IDs 788-839 and lightmap IDs
662-677, with capacities 840 and 678.

Build 013 adds the verified [material conversion](gamecube-materials.md):
Tricky terrain multiplies base texture and lightmap at scale 1, while SSX 3
uses scale 2. The default importer halves donor RGB565 lightmap channels and
stores them as RGBA8 (`0x16`, tiled A/R and G/B planes), preserving base
textures. This avoids the clipped white snow of a raw byte-for-byte lightmap
import. Each sheet has a conversion receipt; `--material-profile raw` retains
the old behavior for a comparison control.

The earlier reclamation approach was unsafe: 51 of the 52 donor texture
IDs in build 009 also named different stock art in other locations. Those
locations can stream their copies into the same global table. Build 007's
grey patches were caused by leaving the global capacities unchanged, not
an engine limit near 800 textures.

## Race course: track chain, gates, and the kind-21 race line (`tools/race_course.py`)

The kind-14 path resource keeps the PS2 little-endian AIP layout. Snow Jam's
race is the track-path chain 3 → 4 → 5 → 6 → 7, linked by coincident
endpoints; a track's distance word is the 2D distance from its origin to the
finish, the finish is the type-0 event on track 7 (at 19,362 along it) and
the two checkpoints are type-18 events (value 0, 1) on tracks 4 and 5. The
six start records with a zero second flag are the race gates; each names the
AI path its rider follows (Snow Jam: gates 0-5 → AI paths 2, 0, 1, 3, 4, 5,
short lines that hand over to later paths by proximity).

Kind 21 (rid 0, 6,536 bytes on Snow Jam) is the flattened race line the
progress meter reads: header (node count 325, stride 20, 2, payload size),
then per node the cumulative 2D distance of the *previous* node, the 2D
normal (−dy, dx) of the outgoing segment, and x, y, over the chained track
vertices with each following track's first vertex dropped, a last node at
the finish point that copies the previous normal, and a trailer (total, 0, 0,
u32 2, total). Node 0 carries the total instead of 0. `race_line_table`
regenerates the stock record from the stock tracks to within 0.1 units.
Builds 005-008 only replaced track 3's geometry and distance (253,411 after
scaling) while this table kept Snow Jam's 353,496 total, which is exactly
the 28% the meter showed at the gate (1 − 253,411 / 353,496).

`--race-course` on the terrain replacer chains the donor race paths (0 → 5 by
coincident endpoints, 1,000-unit tolerance) over the gate track chain, folding
surplus donor segments into the last track, recomputes every distance word
in the 2D convention, places the finish at the donor's first type-9 event on
the last segment and the checkpoints at its first two type-11 events, pairs
the six gates with the donor's six start paths by lateral order (each gate
sits on its path's origin and its rider follows that path), and regenerates
kind 21 from the new chain (Garibaldi: 348 nodes, 253,695 units to the
finish).

## Runtime findings

- `gc-ctrl-001` (round trip of the stock group through the writer) rides
  Snow Jam at 60 FPS with zero invalid accesses: the writer is sound.
- `gc-gari-001` (3,885 patches, nothing removed, 8,856 resources) stalls at
  about 40% on the loading screen with null-pointer accesses at `0x8024D314`
  (an allocator free-list pop without a null check), the same record-pool
  exhaustion the PS2 showed at 8,847 resources. Dropping the 3,052 kind-3
  props is the fix on both platforms.
- `gc-gari-003` (props dropped, no other cleanup) reaches the race at 60 FPS
  with 42,131 dangling-reference accesses, like PS2 build 002.
- `gc-gari-004` (props and collision dropped, references cleared, bindings
  and programs disabled, texture group 31 pinned) runs with **zero** invalid
  accesses. The rider still falls: Single Event uses the six race-gate start
  records (types 0-5, second flag 0) at the Snow Jam gate, about 2,500 units
  from the nearest imported patch, not the freeride start the PS2 build used.
- The kind-14 path resource is the PS2 little-endian AIP format byte for
  byte (magic 0x69696969, 129 AI paths, 8 track paths, 14 start records), so
  `course_route.make_reset_aip` applies unchanged; `--relocate-race-starts`
  moves the gates onto the donor opening.
- `gc-gari-005` (004 plus donor reset paths, freeride start and race gates
  relocated to the donor opening, race track path = donor race line) is the
  **first rideable GameCube Garibaldi**: Single Event race starts on the
  imported opening, rides at 60 FPS (70 MPH, 40% progress at 40 s), restarts
  to a six-rider countdown, zero invalid accesses. Recipe:

  ```sh
  python3 tools/gamecube_terrain.py local/source/gamecube/ssx3/BAM.BIG \
    --nbd local/source/gamecube/tricky/gari.nbd --location ARA1 --template-rid 1673 \
    --source-anchor=-1214.8,-195.5,-768.547891 --target-anchor=-118613.68,15753.8,-228880.14 \
    --yaw 73 --scale .55 --drop-kind 3 --drop-kind 12 --clear-instance-references \
    --clear-script-bindings --disable-course-scripts --pin-texture-group 31 \
    --reset-aip local/source/gamecube/tricky/gari.aip --relocate-freeride-start \
    --relocate-race-starts --output local/builds/gc-gari-005
  ```

  Known gaps: opponents still follow Snow Jam's AI lines, the progress meter
  starts at 28% because the donor race line begins after the gate, Snow Jam
  kind-2 scenery remains, and the terrain uses the fallback snow material.

- `gc-gari-006` (005 plus Garibaldi's 52 terrain textures and 16 lightmaps
  imported with `--textures/--lightmaps`, rids reused from the location's
  other texture groups) renders the course in its own art at 60 FPS with
  zero invalid accesses, but some patches drew Snow Jam textures (tree
  canopy, rock): the reused rids resolved to the stock records, so those
  groups are still resident despite the single-leaf tree.
- `gc-gari-007` (fresh rids 788-839 and 662-677) drew the patches whose
  texture rid was 795 or below and left the stripe patches (rids 819-820)
  flat grey. The September 12 audit found its global lookup tables had not
  been expanded to cover those IDs.
- `gc-gari-008` (rids reclaimed from Snow Jam: the stock textures and
  lightmaps carrying them are dropped from groups 26-30 and 32-35, 191
  records) rides the race with Garibaldi's snow, ice and striped half-pipe
  walls, zero invalid accesses, 60 FPS. Group 31 holds 140 records, 1.6 MB.
  Lightmap orientation assessed offline with `tools/lightmap_orientation.py`:
  fitting sheet brightness against the patch normal under all eight cell
  orientations picks the identity mapping for both Snow Jam (R² 0.287, next
  best 0.223) and Tricky Garibaldi (0.612, next 0.515), so the cell is copied
  unchanged. This supports the orientation choice but does not establish
  rendered color fidelity. The later world-wide audit found texture-ID
  conflicts still present in this build, so dark patches cannot all be
  attributed to Tricky's lighting.
  Recipe: the 005 command plus
  `--textures local/source/gamecube/tricky/gari.gsh --lightmaps local/source/gamecube/tricky/gari_L.gsh`.
- `gc-gari-009` (008 plus `--race-course`): the progress meter starts near
  0% and reads 10% at 0:23 and 54% at 1:23; the five opponents ride the
  imported course on the donor start paths and show on the meter; zero
  invalid accesses, 60 FPS. Recipe: the 008 command with `--race-course` in
  place of `--relocate-race-starts`.

- `gc-gari-010` fixes the global image capacities and ID collisions, removes
  host occlusion curtains, and replaces sampled terrain bounds with conservative
  bounds. Its 68 donor image payloads match the source sheets byte for byte;
  geometry coefficients, UVs and lightmap cells match build 009. A 65×65
  per-patch audit sampled 16,414,125 surface points without a bounds violation.
  The Mac native run `20260912-111628` rides the course at about 60 FPS with
  zero logged invalid accesses and reaches the results screen. Unsteered
  resets and a nonmonotonic progress reading mean this is not full race-route
  acceptance. The subsequent [source-game comparison](garibaldi-visual-comparison.md)
  confirms remaining rendered color and environment differences.
- `gc-gari-011` is a scenery probe adding `--drop-kind 2`; keep its results
  separate from the three fixes above. Adjacent locations can also contribute
  scenery: the opening still shows floating host scenery with these models
  removed. The short Mac ride logs zero invalid accesses, but this variant is
  not the phone release.
- **`gc-gari-012`** is the phone build: the three fixes in 010, with bounds
  computed from the exact float32 coefficients written to the archive and
  outward-rounded sphere/bounds. The coefficients, UVs and lightmap cells still
  match 009. Its final dense audit tests 16,414,125 points with zero box or
  sphere violations. Global image validation passes at 840 textures and 678
  lightmaps. The 101,519,744-byte world was copied to the iPhone and read back
  with matching SHA-256
  `0a619708659ab5136a2a1354ad51c15ea536719adcaff4a0cc98d61369053fed`.

  A fresh Mac run (`20260912-123140`) was compared with original PS2 and
  GameCube Tricky gameplay. The [screenshot gallery and findings](garibaldi-visual-comparison.md)
  show that snow/ice brightness and course scenery still differ. Correct
  image payloads and valid bounds do not establish rendered visual fidelity.

- `gc-gari-013`: shared Tricky→SSX 3 material profile corrects the 1×/2×
  terrain lightmap scale mismatch. All 52 base textures and terrain records
  are identical to 012; only 16 lightmaps change, to compensated RGBA8. Archive
  size 101,749,120 bytes, SHA-256
  `3efd84fffab68df7caba7b6e8dfa04859ea0ada545d7711e9953ce363c7e6032`.
  The native run reaches gameplay/results and exits 0 with zero invalid
  accesses or failed code checks. Installed on the iPhone with byte-for-byte
  readback. See [comparison evidence](garibaldi-visual-comparison.md) and the
  [reusable conversion workflow](gamecube-materials.md). Fog, donor scenery
  and frame-by-frame visibility acceptance remain open.

  Rebuild with a new, nonexistent output directory:

  ```sh
  python3 tools/gamecube_terrain.py local/source/gamecube/ssx3/BAM.BIG \
    --nbd local/source/gamecube/tricky/gari.nbd --location ARA1 --template-rid 1673 \
    --source-anchor=-1214.8,-195.5,-768.547891 --target-anchor=-118613.68,15753.8,-228880.14 \
    --yaw 73 --scale .55 --drop-kind 3 --drop-kind 12 --clear-instance-references \
    --clear-script-bindings --disable-course-scripts --pin-texture-group 31 \
    --reset-aip local/source/gamecube/tricky/gari.aip --relocate-freeride-start --race-course \
    --textures local/source/gamecube/tricky/gari.gsh \
    --lightmaps local/source/gamecube/tricky/gari_L.gsh --output local/builds/gc-gari-014
  ```
