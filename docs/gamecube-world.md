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
