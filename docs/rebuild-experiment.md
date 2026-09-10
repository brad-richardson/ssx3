# First bounded rebuild experiment

Date: 2026-09-10. Status: **file-level validation passed; control and bump reach
gameplay and load their expected terrain coefficients; visual/collision checks pending**.
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
use approximately 5.8 GiB on the network share. Source ISOs and archives remain
unchanged. Runtime tests use copied cards and a separate emulator configuration;
the original BIOS files and both original memory cards still match their setup hashes.

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
and patch name come from the disc. A cold-booted control run loads its exact
coefficients and bounds after transport to Peak 1 → Freeride → Green Station.
The precise landmark within that hub has not yet been visually correlated.

The edit adds this displacement along the stored Z axis:

```text
deltaZ(u,v) = 1600 * u * (1-u) * v * (1-v)
```

It reaches 100 game units at the centre and zero along every patch edge. Do not
assume a metres conversion until calibrated against gameplay. Only four float32
coefficients change; the exact offsets and old/new values are in `experiment.json`.
The stored Z-axis edit is verified mathematically and in memory; its orientation
relative to gameplay still needs visual confirmation.

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

PCSX2 v2.8.2 is now installed at `/Applications/PCSX2-v2.8.2.app`. Its
local BIOS is present under `~/Downloads/PS2_BIOS`. The original source ISOs
have moved to `/Volumes/share-1/brad/games/ps2/`; workbench paths are unchanged.

An isolated test profile and double-clickable launchers are staged at:

```text
/Volumes/share-1/brad/games/ssx3-workbench/emulator/test-002/
  launch-original.command
  launch-control.command
  launch-bump.command
  setup.json
  profile/PCSX2/
    bios/       # verified copies, including NVM/MEC
    memcards/   # verified copies of the user's two cards
    logs/       # original.log / control.log / bump.log
    snaps/      # game-only screenshots from PCSX2's F8 shortcut
    sstates/    # experimental states, never loaded across builds in this run
```

Launch only one session at a time. On this macOS build `-datapath` appends a
`PCSX2` subdirectory; the setup tool accounts for that. Test-001 was an unused
profile-layout trial; use test-002. The test profile maps Return to Start,
X to Cross, C to Circle, and arrow keys to the D-pad; other controller bindings
are inherited. The user's normal profile is unchanged.

The original ISO cold-boots, loads the copied Mac character save into Conquer
the Mountain, and reaches visible gameplay on Peak 3. Transport to Peak 1's
Happiness also reaches visible gameplay. PCSX2 logs identify `SLUS-20772`,
CRC `08FFF00D`, and the Metal renderer on Apple M4 through Rosetta.
The first Happiness memory sample has no exact match for the target patch's
payload, coefficient array, or bounds/corners. This does not establish that the
patch is never loaded there; engine transformations/unloading remain possible.

The control ISO also cold-boots and reaches Conquer the Mountain gameplay using
the same copied save. Transport to Green Station reaches gameplay. A snapshot
after moving downhill contains intact patch coefficients from groups 8 (`A_ASS1`)
and 41 (`ASS1`), demonstrating that the byte-search method works. Repeating
transport and pausing sooner captures the actual target patch in the hub:

- Exact 256-byte coefficient array at EE offset **13,951,296**.
- Exact 72-byte bounds/corners region at EE offset **13,951,576**.
- State: `evidence/control-hub.p2s`, SHA-256
  `884c4fcbee9a114fdd685a2c68ceda796c6ac8003f1e7e526ebcbf017e51ade7`.
- Report: `evidence/control-hub-state.json`.

This confirms the game consumed and decoded the recompressed block. It does not
yet identify the patch visually or establish collision behavior. No emulator
save state was loaded during either cold-boot test.

The bump image also cold-boots, enters Conquer the Mountain, and reaches Green
Station gameplay. Its own snapshot contains the **edited** 256-byte coefficient
array at EE offset **16,864,320**, with the original bounds/corners at
**16,864,600**. Named evidence is `evidence/bump-hub.p2s`, SHA-256
`44816ee6e3579a5d0501a7a720297c2d9cd1c601757df2d7b8e2bc7ee63d84bc`.
Comparing the two states finds exactly the four planned float changes (payload
offsets 152, 168, 216, and 232). The edited coefficient array is absent from the
control state, and the original array is absent from the bump state.

The complete 432-byte payload does not match verbatim in either state: the game
modifies some nongeometry words during loading. In the control sample these are
at payload offsets 0, 4, 8, 416, and 420. Their exact runtime semantics are unknown.
This is why the inspector also checks the unchanged coefficient and bounds ranges.

These observations verify that the engine accepts both rebuilt blocks and receives
the intended terrain edit. They do **not** verify the deformation visually or the
rider's collision response. Garibaldi geometry has not yet been inserted.
See [the machine-readable runtime comparison](runtime-validation.json).

Build manifests retain their creation-time `emulator_tested: false`; subsequent
runtime evidence is recorded here and under `emulator/test-002/evidence/`.
Direct macOS window capture now works with the user's screen-recording permission;
the initial captures used PCSX2's F8 shortcut. Some F8 PNG writes to the share took
over ten seconds, so pause promptly after transport when sampling the hub.

## Reproduction

Prepare another isolated macOS emulator profile (exit PCSX2 before copying cards):

```sh
python3 tools/prepare_emulator.py --output '/Volumes/share-1/brad/games/ssx3-workbench/emulator/test-003'
```

`tools/inspect_state_patch.py STATE ARCHIVE --world-report REPORT` searches the
state's 32 MiB EE memory for the selected patch's complete payload, coefficients,
and bounds/corners. Use the matching original/control/bump world report. PCSX2's
ZIP/Zstandard states require Python 3.14 for this optional tool. Positive matches
prove byte presence only, not rendering or collision; negative matches may mean
the data was transformed or unloaded. Original/control/bump must still cold-boot
and stream their own data, rather than loading a state that contains another build.

Use new build directories; the commands refuse to overwrite existing artifacts.

```sh
python3 tools/build_world_experiment.py '/Volumes/share-1/brad/games/ssx3-workbench/source/ssx3/BAM.BIG' --output '/Volumes/share-1/brad/games/ssx3-workbench/builds/control-002'
python3 tools/build_world_experiment.py '/Volumes/share-1/brad/games/ssx3-workbench/source/ssx3/BAM.BIG' --height 100 --output '/Volumes/share-1/brad/games/ssx3-workbench/builds/bump-002'
python3 tools/build_test_images.py '/Volumes/share-1/brad/games/ps2/SSX 3 (USA).iso' '/Volumes/share-1/brad/games/ssx3-workbench/builds/control-002' '/Volumes/share-1/brad/games/ssx3-workbench/builds/bump-002'
```

The next gate is runtime validation of the control and bump. A Garibaldi import
will need more work on resource assignment, collision, joins, and potentially
streaming/index rebuilding beyond this deliberately fixed-size edit.
