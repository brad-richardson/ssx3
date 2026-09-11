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

## Not yet decoded on GameCube

Kind 13 object tables, kind 16 scripts, kind 18 NIS tables, and the spatial
texture tree, which the PS2 cleanup steps edit (`replace_terrain.py`). Their
GameCube byte order and any layout changes need the same diff treatment
before those steps are ported.
