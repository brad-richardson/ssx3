# First bounded rebuild experiment

Date: 2026-09-10. Status: **file-level validation passed; emulator testing pending**.
This changes an original SSX 3 patch. It is not the Garibaldi import.

## Artifacts

Root: `/Volumes/share-1/brad/games/ssx3-workbench/builds/`

| Build | Image | Purpose |
| --- | --- | --- |
| control-001 | control-001/SSX3-control.iso | Exercise our compressor with identical decoded game data |
| bump-001 | bump-001/SSX3-bump.iso | Test whether changing terrain coefficients affects visible/ridden terrain |

Each directory also contains its rebuilt `BAM.BIG`, `experiment.json`, `image.json`,
and `patch-before.obj` / `patch-after.obj`. The small OBJ files sample the selected
patch at 17×17 vertices, in original game coordinates, without textures or normals.

Each image is 3,005,415,424 bytes. Together with rebuilt archives, these experiments
use approximately 5.8 GiB on the network share. No source ISO, memory card, emulator
configuration, or source archive was modified.

## What was rebuilt

1. Read and hash-check the original archive against the initial investigation.
2. Decode group 2, which is owned by location `A` and contains 291 terrain patches.
3. Parse and reserialize every resource header/payload in that group, verifying an
   exact unchanged round trip, including unknown resource types and fields.
4. Recompress the one block containing the selected patch, preserving its original
   decoded boundaries, 32,768-byte stored size, and header. Keep all other blocks
   byte-identical. The encoder uses standard RefPack commands with a one-byte
   lookahead; pure greedy parsing was slightly too large for these blocks.
5. Decode the reconstructed group and compare it against the intended raw bytes.
6. Save and reread the archive, then rerun the full world-stream inspector.
7. Stream the original ISO into each fresh output, replacing only the verified
   block. Read every output byte back and compare with the predicted SHA-256.

This is a real compression/decompression round trip for **one block**, not a
general rebuild of all world data. All 23 blocks of group 2 decode correctly after
the operation, and the rest of the 159 groups are unchanged. Some other blocks
exceeded capacity with the current encoder; the builder refuses overflow rather
than moving offsets or increasing file sizes.

### Block details

| Property | Value |
| --- | ---: |
| Group | 2 (`A`) |
| Block within group, zero-based | 12 |
| Offset within SSB | 1,081,344 |
| Offset within BAM.BIG | 1,118,208 |
| Offset within ISO | 1,773,193,216 |
| Stored block length | 32,768 |
| Decoded block length | 52,396 |
| Original compressed payload | 32,755 |
| Control compressed payload | 32,670 |
| Bump compressed payload | 32,676 |

SSB has eight-byte block headers, leaving 32,760 bytes for compression and padding.

## Terrain edit

Name lookup through the PHM/PSM tables identifies the selected resource as
**`patch_A_hub_1237`**, track 1, RID 76. Its payload is 432 bytes. The location name
and patch name come from the disc; the precise in-game landmark has not yet been
visually correlated. Start investigation in the Peak 1/base hub area, but confirm
the actual location before claiming a successful terrain/collision test.

The edit adds this displacement along the stored Z axis:

```text
deltaZ(u,v) = 1600 * u * (1-u) * v * (1-v)
```

It reaches 100 game units at the centre and zero along every patch edge. Do not
assume a metres conversion until calibrated against gameplay. Only four float32
coefficients change; the exact offsets and old/new values are in `experiment.json`.

| Point | X | Y | Z |
| --- | ---: | ---: | ---: |
| Original centre | -103508.6842 | 37805.3969 | -220359.0417 |
| Edited centre | -103508.6842 | 37805.3969 | -220259.0417 |

The altered control points fit within the patch's existing bounding box and sphere.
The validator permits only original rounding discrepancies plus 0.02 game units;
it rejects edits that escape those bounds. No spatial-index expansion is required
for this selected experiment. Other interpretations/dependencies of these fields
still need runtime validation.

All edge samples have exactly zero displacement for this edit. All four corner
vectors, UVs, materials, sphere/bounds, resource headers, and unknown fields remain
unchanged. Separately stored collision resources remain unchanged deliberately:
the experiment is intended to determine whether the rider follows the edited
patch directly or requires additional collision updates. This has not been proven.

## Validation results

- **13 tests pass**: known RefPack encodings, random and repetitive round trips,
  long-distance/overlapping matches, malformed input, geometry bounds, fixed edges,
  preservation of unknown resource data, and substitutions spanning copy buffers.
- Full world inspection passes for both rebuilt archives: 3,328 blocks, 159 groups,
  30,644 terrain patches, and all SDB resource counts still agree.
- Control: every decoded group SHA-256 is identical to the original.
- Bump: only group 2 changes; resource counts and corner checks remain identical.
- Both saved archives pass readback hashes.
- Both ISO directory inventories match the original and complete image readback
  hashes match the expected stream with one block substituted.

### SHA-256

| File | SHA-256 |
| --- | --- |
| Original SSX 3 ISO | 3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5 |
| Control ISO | 0e636fb1957fdbf40eda94544b712c2f786d7707c863ab8c7a0ab97d14ebdd2b |
| Bump ISO | fa5f98b7f1731edd90a8d7bfe0416feacefde4075742a9fc733adbdef95434f1 |
| Control BAM.BIG | 04d2ed5e69bdc051f9597d89b8d86dfd379d24acf3234edc965a6e63b88607a3 |
| Bump BAM.BIG | 1ca2aeca5df92f28a754df0e65605684d6cef85d94e09348a647b6b9e1629cff |

These hashes identify the supplied source and generated outputs; they are not a
comparison against an external disc-preservation database.

## Emulator test procedure

1. Use a working PCSX2 setup and a copy of a suitable memory card/save for repeatable
   comparisons. Cold-boot the original ISO and record normal loading in the A hub.
2. Cold-boot `SSX3-control.iso`. Load and ride the same area, including transitions
   that stream it in. A menu/title-screen boot alone does not exercise this block.
3. If the control works, cold-boot `SSX3-bump.iso` and locate the target patch using
   the coordinates and mesh previews above. Confirm the visible deformation.
4. Ride across it slowly and at speed, jump/land, and reset nearby. Record whether
   the rider follows the bump, passes through it, or reacts at the original surface.
5. If the control fails, investigate compression/block handling first. If control
   works but only rendering changes, investigate the terrain collision path next.

As of this run, `/Applications` and Spotlight did not reveal the PCSX2 application.
An existing configuration under `~/Library/Application Support/PCSX2/inis` points
to `~/Downloads/PS2_BIOS`, which is missing; the profile's default `bios/` is empty.
No emulator was launched and no graphics/collision behavior was observed. The user
has been asked for the working emulator location. Test image manifests explicitly
record `emulator_tested: false`.

## Reproduction

Use new build directories; the commands refuse to overwrite existing artifacts.

```sh
python3 tools/build_world_experiment.py '/Volumes/share-1/brad/games/ssx3-workbench/source/ssx3/BAM.BIG' --output '/Volumes/share-1/brad/games/ssx3-workbench/builds/control-002'
python3 tools/build_world_experiment.py '/Volumes/share-1/brad/games/ssx3-workbench/source/ssx3/BAM.BIG' --height 100 --output '/Volumes/share-1/brad/games/ssx3-workbench/builds/bump-002'
python3 tools/build_test_images.py '/Volumes/share-1/brad/games/SSX 3 (USA).iso' '/Volumes/share-1/brad/games/ssx3-workbench/builds/control-002' '/Volumes/share-1/brad/games/ssx3-workbench/builds/bump-002'
```

The next gate is runtime validation of the control and bump. A Garibaldi import
will need more work on resource assignment, collision, joins, and potentially
streaming/index rebuilding beyond this deliberately fixed-size edit.
