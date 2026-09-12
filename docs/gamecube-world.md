# GameCube SSX 3 world format (GXBE69)

Date: 2026-09-11. Decoded by diffing the same Snow Jam records on the PS2 and
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
| 8 | surface type, e.g. 0x9 | 0x90000 (same value shifted) |
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
appends them to the pinned group and rewrites the binding words. Their rids
are reclaimed from Snow Jam: build 006 showed rids reused from the location's
other texture groups still resolve to the stock art (those groups stay
resident despite the pinned tree), and build 007 showed fresh rids stop
resolving somewhere between 796 and 819 (texture 19 at rid 795 drew, the
stripe textures at 819-820 drew flat grey), so the stock records carrying the
reclaimed rids are dropped from every group of the location.

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
  flat grey, the foreign-id symptom from the PS2 hdr-003 probe.
- `gc-gari-008` (rids reclaimed from Snow Jam: the stock textures and
  lightmaps carrying them are dropped from groups 26-30 and 32-35, 191
  records) rides the race with Garibaldi's snow, ice and striped half-pipe
  walls, zero invalid accesses, 60 FPS. Group 31 holds 140 records, 1.6 MB.
  Lightmap orientation verified offline with `tools/lightmap_orientation.py`:
  fitting sheet brightness against the patch normal under all eight cell
  orientations picks the identity mapping for both Snow Jam (R² 0.287, next
  best 0.223) and Tricky Garibaldi (0.612, next 0.515), so the cell is copied
  unchanged and the darker ice sections around 25% are Tricky's own lighting.
  Recipe: the 005 command plus
  `--textures local/source/gamecube/tricky/gari.gsh --lightmaps local/source/gamecube/tricky/gari_L.gsh`.
- `gc-gari-009` (008 plus `--race-course`): the progress meter starts near
  0% and reads 10% at 0:23 and 54% at 1:23; the five opponents ride the
  imported course on the donor start paths and show on the meter; zero
  invalid accesses, 60 FPS. Recipe: the 008 command with `--race-course` in
  place of `--relocate-race-starts`.
