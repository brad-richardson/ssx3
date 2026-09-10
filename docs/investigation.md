# Garibaldi → SSX 3: initial investigation

Date: 2026-09-10. Target: original SSX 3 PS2 gameplay, ultimately playable on the
user's Odin through emulation. Donor: Garibaldi, selected by the user.

This records the initial extraction phase. The subsequent
[rebuild experiment](rebuild-experiment.md) adds a verified compression control,
two bounded terrain edits, and three test ISOs. The second edit is ridden in game:
the rider's ground contact and the rendered snow follow the edited patch
coefficients. See that log for current runtime evidence. Findings and next steps
below describe the earlier phase.

## Inputs and provenance

The source images remain unchanged, now under `/Volumes/share-1/brad/games/ps2/`.

| Input | Size (bytes) | Executable | Executable SHA-1 |
| --- | ---: | --- | --- |
| SSX 3 (USA).iso | 3,005,415,424 | SLUS_207.72 | 77114dfd1205eaccf1ccc18c5f9650097fa78bd8 |
| SSX Tricky (USA).iso | 2,902,425,600 | SLUS_203.26 | 45e9fd5fa4c0b30ffbd4155a9e256d5eabc65d23 |

SSX 3's executable SHA-1 matches the version documented by
[ssxdecomp/ssx3](https://github.com/ssxdecomp/ssx3). These checks do not claim that
every byte of either full disc has been validated against a preservation database.

Independent `bsdtar` listing agrees with our ISO9660 reader on all **163 SSX 3 files**
and **261 Tricky files**. Independent `bsdtar` extraction and SHA-256 comparison
also agree with both staged archives:

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
| DATA/WORLDS/BAM.BIG | 113,078,400 | 550c9a8dbda59055af795c4ae22c425f80e7433fa931f21db0c53ebf31741b2d |
| DATA/MODELS/GARI.BIG | 4,382,471 | 676276e83e145192e72d432d656ef219dc0a8f3539ff8e5345607fbeedb8f990 |

Raw inventories, offsets, hashes, and detailed stream reports are in ignored
`local/reports/`. Extracted assets are on the share under `ssx3-workbench/`.

## SSX 3 world archive

`BAM.BIG` is a BIGF archive with five members:

| Member | Stored bytes | Observed role |
| --- | ---: | --- |
| bam.sdb | 32,780 | Location / spatial / resource-group index |
| bam.ssb | 109,051,904 | Compressed world resource stream |
| bam.phm | 1,434,868 | Reference tool uses it for name lookup |
| bam.psm | 2,552,812 | Companion to name lookup |
| serial.txt | 128 | Build metadata |

All **3,328** SSB blocks decode using the `10 FB` RefPack variant. Blocks in this
disc are 32,768 bytes and use `CBXS` / `CEND` tags. Concatenating decoded block data
through each `CEND` yields **159** resource groups and **161,953,347 decoded bytes**.
Each resource has an eight-byte header: type (u8), payload size (little-endian
u24), track ID (u8), resource ID (little-endian u24).

Every group's resource count agrees with the SDB table. All compressed-block
trailing padding observed was zero. The stream contains **30,644 type-1 terrain
resources**, all 432 bytes, plus **4,616 type-12 resources** (collision according
to the reference parser). Terrain collision might also use patch data; the
relationship is not yet established through executable analysis or playtesting.

### Location index correction

The reference `SDBHandler.cs` labels several fields misleadingly for this disc.
The observed header counts are 49 locations, 183 spatial records, and 159 stream
groups. For each 88-byte location record, the four u32 fields after its name are:

1. Spatial-record count.
2. Stream-group count.
3. **Last** stream-group index, inclusive.
4. Starting spatial-record index.

The parser derives the first group as `last_group - group_count + 1`. This gives
exactly one location for every group, and the corresponding 68-byte group-index
records match every observed resource count. Treat spatial-record semantics beyond
these bounds as provisional. The 96-byte spatial records are not yet rebuilt.

The 68-byte stream-group records decode as follows (verified on all 159 groups,
2026-09-10 afternoon):

| Offset | Type | Meaning |
| ---: | --- | --- |
| 0 | u16 | Resource count, all kinds |
| 2 | u16 | Group index |
| 4 | u32 | SSB byte offset of the group's first block |
| 8 | u32 | Bytes of resources with kind 0–12, payload plus 8-byte header (exact for every group; kinds 13–22 excluded) |
| 12 | u16 × 13 | Resource count per kind 0–12 |
| 4–11 (u16 view 2–5) | u16 | Unknown: 0 or 32768; a rising index; a value that looks hashed; a small count. Preserve. |
| 28 | u32 | Unknown, multiples of 65,536 (likely a memory budget). Preserve. |

A same-content re-layout of the stream therefore only changes offset 4. Adding
resources changes offsets 0, 8, and the per-kind counts; the unknown words are
kept as-is until an experiment shows they matter.

Do not use the upstream `FindLocationChunk` implementation uncritically for this
disc. For example, `ARA1` occupies groups 25–33; the stored value 33 is its last
group, not its first. In-game course-name mappings have not yet been verified.

## Garibaldi donor archive

`GARI.BIG` uses the C0FB archive format, with 11 RefPack-compressed members:
`gari.ssh`, `gari_L.ssh`, `gari_sky.ssh`, `gari.pbd`, `gari_sky.pbd`, `gari.ltg`,
`gari.map`, `gari.ssf`, `gari.aip`, `gari.sop`, and `gari.adl`.

`gari.pbd` decompresses to **4,098,656 bytes**, SHA-256
`5f12ec2edb5f08071fe66690b2c72cb31601f562aed5552e136de2ae271ccee2`.
Its header reports **3,885 patches** and **3,393 instances**. The patch array starts
at byte 144 and occupies exactly 3,885 × 448 bytes up to the instance array.
Instances have only been counted, not exported or semantically validated.

The untextured preview is:

`/Volumes/share-1/brad/games/ssx3-workbench/extracted/garibaldi/garibaldi-terrain.obj`

The patch evaluator agrees with Garibaldi's stored corners to within **0.028 game
units** over every patch. This supports the geometry decoding; it does not validate
textures, triangle winding, normals, collision, or how a rider will interact with it.

## Geometry comparison

Both formats store 16 four-component vectors containing bicubic power coefficients,
in reversed row/column order. The first three components describe geometry; the
fourth components and other unknown fields should be preserved until understood.

| Field | Tricky PBD patch | SSX 3 type-1 payload |
| --- | --- | --- |
| Record size | 448 bytes | 432 bytes |
| Coefficient-array offset | 80 | 64 |
| Bounding vectors | 336, 348 | 344, 356 |
| Four corner-vector offset | 360 (vec4 stride) | 368 (vec3 stride) |

The SSX 3 bounding/corner ordering above corrects labels in upstream
`WorldPatch.cs`; use the actual corner comparison in `ssx3-world.json` as evidence.
After correcting that ordering, **all 30,644 SSX 3 patches** agree with their stored
corners to within **0.008 game units**. Using the upstream labels as-is produced
large discrepancies for 30,641 patches, so this is a substantive correction.
Identical coefficient math does **not** imply that entire records or surface,
material, lightmap, resource-ID, or visibility fields can be copied directly.

## SSX 3 patch record survey (M3 groundwork)

A field survey over all 30,644 patches (2026-09-10 afternoon) gives these
hypotheses for the bytes outside the coefficient array. None is verified in
play yet; the roadmap's M3 tests them one at a time.

| Offset | Observation | Hypothesis |
| ---: | --- | --- |
| 0 | u32, 43 distinct values; each value's count equals one location's patch count | Per-location identifier (or a pointer patched at load); must be set per destination on import |
| 4 | u32, constant 0x4045B7 | Record type/version tag |
| 8 | u32, 56 values of the form 0x9xxxx / 0xBxxxx with small low bits | Material/texture selector plus flags |
| 12 | u32, 15 values such as 0x29, 0x800029, 0xE001A9 | Surface flags (low bits) and type (high bits) |
| 16, 20 | f32 in 1/128 steps, 0.008–0.977 | Lightmap atlas U, V offset |
| 24, 28 | f32 in {1/64, 3/64, 7/64, 15/64, …} | Lightmap atlas cell size |
| 32–63 | four (u, v) float pairs, usually (0,1),(1,1),(0,0),(1,0) or tiled ranges like −4..5 | Corner texture coordinates; ranges encode tiling |
| 76 + 16i | w component of every coefficient vector | Always 1.0 |
| 320–331 | f32 ×4 | Bounding sphere centre and radius (radius 143–16,430) |
| 336 | u32, unique per patch, (n << 8) | 1 pattern | Patch ordinal/handle |
| 340 | u32, 110 distinct values such as 0x842A00 | Texture or lightmap page reference |
| 344–367 | f32 ×6 | Axis-aligned bounds min/max |
| 368–415 | f32 ×12 | Four corner positions |
| 416 | u32, 4,547 distinct, low 16 bits small (0x000C, 0x00E3) | Packed index pair, possibly lightmap page + slot |
| 420 | u32, 0xFFFFFFFF for 87%, else 0xFFFFnnnn | Neighbour/link index, −1 when absent |
| 424 | u32, constant 0xFFFFFFFF | Unused link |
| 428 | u32, constant 0x11483C | Tag or pointer placeholder |

The runtime modifies payload offsets 0, 4, 8, 416 and 420 after loading (seen in
the state comparisons), consistent with pointers or handles being resolved in
place.

## Tooling status and limitations

Reference commit: `GlitcherOG/SSX-Library` @
`5c345e08dc521b0b1041734925cf0ece085e84c9` (GPL-3.0).

Key inspected files under its `SSX-Library/` directory:

- `Internal/BIG/BIGF4.cs`, `Internal/BIG/COFB.cs`: archive formats.
- `Internal/Refpack.cs`: compression format.
- `Internal/Utilities/BezierUtil.cs`: terrain coefficient interpretation.
- `FileHandlers/LevelFiles/Tricky/PS2/PBDHandler.cs`: donor record layout.
- `FileHandlers/LevelFiles/SSX3PS2/SSBHandler.cs`: target resource stream.
- `FileHandlers/LevelFiles/SSX3PS2/SDBHandler.cs`: target index tables.
- `FileHandlers/LevelFiles/SSX3PS2/SSBData/WorldPatch.cs`: target terrain layout.
- `FileHandlers/LevelFiles/SSX3PS2/SSBData/WorldCollision.cs`: partial collision parsing.

The current library targets .NET 10. It was inspected as reference source, not built.
The SSX 3 `PackSSB` method is commented out, and `WorldPatch` has no binary writer.
General archive creation support is not evidence of a complete playable-world
rebuild pipeline. We have not yet done an unchanged world rebuild or any playtest.

Our small Python inspector explicitly rejects unsupported archive and compression
variants. It keeps original files read-only, validates offsets/counts, and avoids
extracting the many GB of unrelated audio/video data. Synthetic tests cover the
three RefPack backreference forms (including overlap), literals, malformed input,
archive bounds, resource boundaries, and a known planar patch.

## Next implementation gates

1. **Preserving rebuild:** reconstruct an unchanged small SSX 3 stream group and
   archive, retaining unknown fields, IDs, ordering, compression block boundaries,
   and untouched bytes. Decode the result and compare before any game test.
2. **Original-terrain edit:** done for one hub patch (bump-002): appearance and
   rider ground contact follow the coefficients with bounds/index data untouched.
   Still open: which fields govern surface behavior (friction, sound), whether
   type-12 data matters for walls, rails, and resets, and edits that must enlarge
   stored bounds.
3. **Garibaldi sample:** import a short contiguous terrain section with suitable
   transforms, joins, materials, collision, and reset behavior. Start inside an
   existing SSX 3 location; a new menu entry or mountain connection comes later.

At the end of the extraction phase PCSX2 was not installed. PCSX2 v2.8.2 and the
local BIOS are now available, and the later rebuild log records desktop tests.
Odin testing follows desktop validation.

No native-engine work, full-level conversion, or gameplay changes have been made.
