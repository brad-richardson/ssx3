# First bounded rebuild experiment

Date: 2026-09-10. Status: **rider collision and rendering follow an edited terrain
patch (bump-002); bump-001's patch was never reached in play**. These builds change
original SSX 3 patches. They are not the Garibaldi import.

## Artifacts

Root: `/Volumes/share-1/brad/games/ssx3-workbench/builds/`

| Build | Image | Purpose |
| --- | --- | --- |
| control-001 | control-001/SSX3-control.iso | Exercise our compressor with identical decoded game data |
| bump-001 | bump-001/SSX3-bump.iso | First terrain edit (`patch_A_hub_1237`); verified in memory only |
| bump-002 | bump-002/SSX3-bump.iso | Terrain edit on the Green Station line (`patch_A_hub_1024`); ridden and rendered |

Each directory also contains its rebuilt `BAM.BIG`, `experiment.json`, `image.json`,
and `patch-before.obj` / `patch-after.obj`. The small OBJ files sample the selected
patch at 17×17 vertices, in original game coordinates, without textures or normals.

Each image is 3,005,415,424 bytes. Together with rebuilt archives, these experiments
use approximately 8.7 GiB on the network share. Source ISOs and archives remain
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
The stored Z axis is up (see the second edit below), so this is a raised bump.
It is verified mathematically and in memory but was never reached in play.

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
patch directly or requires additional collision updates. bump-002 below answers
this for a hub patch: the rider follows the edited coefficients.

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

## Second edit: bump-002, ridden and rendered

`patch_A_hub_1237` sits at the far downhill edge of the Green Station hub. Two
autopilot attempts (below) reached within 7,000 game units of it along the hub's
natural line, but the terrain west of `(-98800, 42500)` funnels the rider north
into the connector and a turn toward the patch stalls. So a second edit was placed
on a patch the rider crosses on every free ride from the Green Station spawn.

Green Station transport, when arriving from Peak 3, spawns the rider at about
`(-66300, 33600, -212800)` at the top (east, high Z) of hub `A`; the rider then
descends west along the hub. One earlier transport in the same session spawned at
`(-99557, 43664)` instead; both spawns are handled by the route tool. +Z is up:
race groups descend from hub `E` (Z about +508,000) through `C`, `D`, `A` to `B`
(Z about -450,000), so the "bump" edits raise the surface.

| Property | bump-002 |
| --- | ---: |
| Patch | `patch_A_hub_1024`, group 2, track 1, RID 213 |
| Height | 75 game units (100 escaped this sloped patch's stored bounds) |
| Centre before | (-89775.0803, 40014.6902, -217132.2898) |
| Centre after | (-89775.0803, 40014.6902, -217057.2898) |
| Changed floats | payload offsets 152, 168, 216, 232 |
| Block | SSB offset 1,114,112; BAM.BIG offset 1,150,976; ISO offset 1,773,225,984 |
| Compressed payload | 32,748 original, 32,588 rebuilt |
| BAM.BIG SHA-256 | c14e8007724957bcc4acc3f0d681785bdb250bed0a46091ee70defc48467faf9 |
| ISO SHA-256 | 0907b8694addc81b5a30c2dff1900d4e23253ebb9e53a5a7d4605cc8f46885d1 |

Natural-line patches that also accept a bump: RID 270 (`patch_A_hub_1025`) at 75,
RIDs 199 and 152 (`1022`, `1021`) at 50. RIDs 29, 66, 27 and 11 reject every height
tried down to 25 because their control hulls already touch their stored bounds.

### Collision result

`tools/ride_route.py` transported to Green Station in a cold-booted bump-002 session,
steered through the patch centre using live positions read over PINE, and logged the
rider at 10 Hz. `tools/patch_crossing.py` then compared the rider's Z with the
original and edited surfaces at the nearest (u, v) of the patch. The same procedure was
repeated in a cold-booted control-001 session on the same line.

| Sample (u, v) | control-001: rider minus original surface | bump-002: rider minus original surface | Edited minus original surface at that point |
| --- | ---: | ---: | ---: |
| entry (0.7, 0.05) | -0.9 | 1.8 | 5 |
| (0.6, 0.3) | -0.1 | 49.4 | 50 |
| centre (0.5, 0.5) | -2.1 | 72.9 | 73 |
| (0.4, 0.8) | -2.6 | 47.2 | 51 |
| exit (0.4, 0.97) | 0.9 | 8.1 | 5 |

Across 11 samples inside the patch the bump-002 rider sits above the original surface
by the edited delta within 4 game units; the control rider stays within 3 units of
the original surface. Rider height is the tracked position at EE offset `0x5409c0`,
which sits on the surface on unedited patches. The separately stored type-12
collision resources were not changed, so for this patch the rider's ground contact
follows the patch coefficients directly. Whether type-12 data matters elsewhere
(walls, rails, resets) is still unknown.

### Rendering result

Window captures at the patch centre show a rounded crest under the rider in bump-002
and a flat trail in control-001 at the same spot:
`emulator/test-002/evidence/bump-002/control-vs-bump-002-centre.png` (control left,
bump right). The crest is modest on screen, consistent with a 75-unit rise on a
patch roughly 1,600 units across.

### Memory

A live PINE read of bump-002's EE memory at Green Station finds the edited 256-byte
coefficient array at offset 16,086,256 and the unchanged bounds/corners at 16,086,536
(`evidence/bump-002/live-memory.json`). Full logs and captures:

```text
emulator/test-002/evidence/bump-002/
  bump-002-ride.jsonl / control-001-ride.jsonl      # 10 Hz rider positions
  bump-002-crossing.txt / control-001-crossing.txt  # patch_crossing.py output
  bump-002-approach-0[3-8].png, control-001-approach-0[3-7].png
  control-vs-bump-002-centre.png, live-memory.json
```

## Driving the emulator

PINE is enabled in the test-002 profile (`EnablePINE = true`, default slot 28011,
socket `$TMPDIR/pcsx2.sock`). `tools/pine.py` reads EE memory in 32,000-read batches;
a full 32 MiB dump takes about half a second. **Connect one PINE client at a time.**
Twice, a second client connecting while another was mid-request was followed by PCSX2
exiting without a log entry or crash report. Killing one PCSX2 instance also removes
the socket file of any other instance, so quit through AppleScript and wait for the
process to disappear before launching another.

Keyboard input goes through small Swift helpers built by `tools/macos/build.sh`
(`press_keys` taps, `keyd` holds keys from stdin, `window_id` plus `capture.sh` grab
the PCSX2 window). Menu cursors default to the current peak, so the transport key
sequence differs from Peak 3 (Peak 3 → Down Down → Peak 1) and from Peak 1 (Peak 1
already selected). Riding back into a lodge opens the transport menu by itself.

`tools/ride_autopilot.py` steers with pulsed D-pad presses proportional to the heading
error (Left turns counter-clockwise in XY; a sign test right after spawn is unreliable
because input is ignored for the first moments). It reaches waypoints on the natural
downhill line with a few degrees of error but cannot climb or cross terrain that
channels the rider elsewhere. Build the helpers, then, from a paused Peak 3 session:

```sh
sh tools/macos/build.sh
python3 tools/pine.py                                    # status, serial, title
SIGN=1 CAPTURE_AT=-89775,40015 python3 tools/ride_route.py OUT_DIR OUT_DIR/ride.jsonl '-89775,40015;-93000,40400'
python3 tools/patch_crossing.py OUT_DIR/ride.jsonl '/Volumes/share-1/brad/games/ssx3-workbench/builds/bump-002'
```

`ride_route.py` expects the Green Station selection to have just been made; it waits
for the spawn, hands over to the autopilot, captures the window within 3,000 units of
`CAPTURE_AT`, and pauses afterwards.

## Growable rebuild groundwork (roadmap M2)

### control-003: world archive relocated into disc padding

`DATA/WORLDS/BAM.BIG` is followed immediately by `MUSIC.BIG`, so it cannot grow in
place. The disc carries two 256 MiB padding files. `tools/relocate_archive.py`
streams the original image into a new one, writes the archive bytes at `PAD0.000`'s
extent (offset 274,524,160, LBA 134,045) and rewrites only the archive's directory
record (at image offset 569,440) with the new extent and length in both byte
orders. The old archive bytes and `PAD0.000`'s own record are untouched, so the
padding entry now overlaps the archive.

| Property | control-003 |
| --- | ---: |
| Archive | original `BAM.BIG`, unchanged, 113,078,400 bytes |
| ISO SHA-256 | 4d08ca7a7d0641666155f1fe9646bfac5eee371ef9680c9a79387f6f458a5aea |
| Changed ranges | directory record (33 bytes) and 113,078,400 bytes inside `PAD0.000` |

Result: cold boot, Conquer the Mountain, transport to Green Station, and a ride
through `patch_A_hub_1024` with the rider on the original surface within 2.5
game units (`evidence/control-003/`). The game therefore reads the world archive
through the ISO9660 directory, and a rebuilt archive of up to 256 MiB can be
placed without moving any other file or changing the image size.

### Encoder capacity

Re-encoding all 3,328 blocks in place with the greedy encoder leaves 697 blocks
over capacity (up to 753 bytes over; total output 0.18% larger than EA's). EA's
packer fills blocks to within 14 bytes of capacity at the median, so any
in-place rebuild needs an encoder at least as good as EA's on every block.
`tools/refpack_optimal.py` parses optimally by dynamic programming over the 10FB
command forms. On the three worst blocks:

| Match candidates per position | Output bytes (EA: 32,750–32,753; capacity 32,760) | Time per block |
| ---: | ---: | ---: |
| 32, skip inside long matches | 32,779–32,894 | 0.7 s |
| 128, skip | 32,359–32,445 | 1.7 s |
| 128, no skip | 32,266–32,326 | 4 s |
| 512, no skip | 31,984–32,052 | 10 s |

The default (128 candidates, skip) beats EA's compressor by about 1.2% on these
blocks. Skip mode below a 64-byte match length loses to the greedy encoder on
word-repetitive data, so the default skip threshold is 64.

### control-002: every block re-encoded in place

`tools/recompress_stream.py` re-encodes all 3,328 blocks at their original
boundaries with escalating search levels. Every block fits: 3,229 at the default
level, 88 with 256 candidates, 10 with 512, 1 with 1,024 (that block lands on
exactly 32,760 bytes). Total compressed payload 104,466,997 bytes against EA's
105,497,086 (1.0% smaller; mean saving 310 bytes per block). Decoded groups are
byte-identical to the baseline; the archive keeps its size and every non-stream
byte. Archive SHA-256
b0e1b193c037c80213774f281b9ec27f4e6586fccf04b9a8060276064e52ed9f.

Runtime: the control-002 image cold-boots into Peak 3 gameplay (hub `E`),
transports to Green Station (hub `A`), and rides through `patch_A_hub_1024` with
the rider within 2.7 game units of the original surface
(`evidence/control-002/`). Both hubs stream entirely from re-encoded blocks.
A race location has not yet been ridden on this image.

## First patch-field experiment (roadmap M3): corner UVs

`build_world_experiment.py --uv-tile N` scales the four (u, v) float pairs at
payload offsets 32–63 about their minimum. On `patch_A_hub_1024` (original
corners (0,0), (0,1), (1,0), (1,1)) builds uv-001 (×4, ISO SHA-256
46006ed286a3eaace2690515f1bae0e0e08726903721b09fe7778cdfd6308516) and uv-002
(×24, ISO SHA-256 4fc63ce73f30f1408394cef421aaeee43656392ddd5c47a4022b9b686deb9938)
both cold-boot and ride normally, and the rider stays on the original surface.
Window captures at the same spots show **no visible texture change** at either
factor (`evidence/uv-001/`, `evidence/uv-002/`). This does not settle whether
the fields are texture coordinates: the hub snow texture has no feature large
enough to reveal tiling once minified. A second probe, mat-001
(`--set 8=0x9000a`, the value of the hub's one unusual patch near the lodge; ISO
SHA-256 0bf3c1e699a362f3b64c6b0d154a81fc252a189d0690010c4a0788d792ca80a0), also
rides normally with no visible change (`evidence/mat-001/`). Single-word probes on
a plain snow patch are therefore a weak method. The next M3 step transplants the
whole non-geometry header and tail (offsets 0–63 and 320–343, 416–431) from a
visually distinct patch (rock, ice, or a jump face) onto this one; if the
appearance changes, bisect the transplanted fields.

The next gates are described in [the roadmap](roadmap.md): re-laid-out streams
with regenerated SDB offsets, then a grown group, before any Garibaldi import.
