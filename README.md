# SSX 3 course-port investigation

The first donor course is **Garibaldi from SSX Tricky (PS2)**. The goal is a short,
rideable section inside the original SSX 3 engine, followed by a complete course
if terrain, collision, and streaming can be rebuilt reliably.

This repository contains inspection tools, a **bounded rebuild experiment**, and
emulator-driving tools. Three test ISOs have been built: an unchanged-content
compression control and two single-patch SSX 3 terrain bumps. All cold-boot and
reach gameplay in PCSX2. For the second bump, the rider's ground contact and the
rendered snow follow the edited coefficients, measured against the control on the
same line. Garibaldi has not yet been imported.

## Current results

- Both supplied PS2 disc inventories parsed and independently matched `bsdtar`.
- SSX 3's executable matches the decompilation project's supported NTSC-U version.
- SSX 3's complete world archive decodes: 159 groups, 30,644 terrain patches.
- Garibaldi's terrain decodes: 3,885 patches; an untextured OBJ preview is staged.
- Staged archives are byte-identical to independent extraction from the ISOs.
- Recompressed one terrain-containing SSB block without changing decoded data.
- Built a second version with a 100-game-unit bump in one A-hub terrain patch.
- Both complete test ISOs pass readback hashes; all bytes outside the selected
  32 KiB block and every ISO directory entry are unchanged.
- Original, control, and bump images cold-boot and reach gameplay in an isolated
  PCSX2 profile on the share. Control and bump load the target patch at Green
  Station; their in-memory coefficients differ by exactly the four planned floats.
- A second bump (75 units, `patch_A_hub_1024`) lies on the Green Station free-ride
  line. Riding through it, the rider sits up to 73 units above the original surface,
  matching the edited surface within 4 units; on the control the rider stays within
  3 units of the original. A visible crest appears at the same spot.
- Live PCSX2 memory reads (PINE) and a position-feedback autopilot drive these tests;
  the rider position lives at EE offset `0x5409c0` in this game version.

See [the investigation log](docs/investigation.md) for evidence, format findings,
limitations, upstream provenance, and the next implementation steps.
See [the rebuild experiment](docs/rebuild-experiment.md) for test image paths,
the exact edit, validation results, and emulator test instructions.
The [runtime comparison](docs/runtime-validation.json) records state hashes,
memory offsets, and the four verified coefficient changes.

## Storage

Code, tests, and small reports live here. Large files live on the network share:

```text
/Volumes/share-1/brad/games/
  ps2/
    SSX 3 (USA).iso                # original, read-only input
    SSX Tricky (USA).iso           # original, read-only input
  ssx3-workbench/
    source/ssx3/BAM.BIG            # exact archive extracted from SSX 3
    source/tricky/GARI.BIG         # exact archive extracted from Tricky
    extracted/garibaldi/
      gari.pbd                    # decompressed terrain/scene container
      garibaldi-terrain.obj        # terrain preview, original coordinates
    builds/
      control-001/                 # unchanged-content recompression control
        BAM.BIG
        SSX3-control.iso
        experiment.json
        image.json
      bump-001/                    # one original SSX 3 patch has a centre bump
        BAM.BIG
        SSX3-bump.iso
        experiment.json
        image.json
      bump-002/                    # bump on the Green Station line, ridden and rendered
    emulator/test-002/             # isolated PCSX2 profile, launchers, evidence/
```

`local/` and `third_party/` are ignored by Git. No game assets, executables, ISOs,
or generated meshes belong in commits. The upstream clone is only about 3.3 MiB.

## Running the tools

Python 3.10+ and the standard library suffice for the inspection and build tools.
The independent verification tool also uses macOS's `bsdtar`. The emulator-driving
tools need PCSX2 with PINE enabled, `swiftc` for the small input helpers
(`sh tools/macos/build.sh`), and the screen-recording permission for window capture.
No .NET runtime, game SDK, or additional BIOS is needed.

Inventory the discs and relevant archive directories without copying whole ISOs:

```sh
python3 tools/inspect_disc.py '/Volumes/share-1/brad/games/ps2/SSX 3 (USA).iso' --archive DATA/WORLDS/BAM.BIG --output local/reports/ssx3-disc.json
python3 tools/inspect_disc.py '/Volumes/share-1/brad/games/ps2/SSX Tricky (USA).iso' --archive DATA/MODELS/GARI.BIG --output local/reports/tricky-disc.json
```

Reproduce reports from the staged archives (read-only):

```sh
python3 tools/probe_worlds.py ssx3 '/Volumes/share-1/brad/games/ssx3-workbench/source/ssx3/BAM.BIG' --report local/reports/ssx3-world.json
python3 tools/probe_worlds.py tricky '/Volumes/share-1/brad/games/ssx3-workbench/source/tricky/GARI.BIG' --report local/reports/garibaldi.json
python3 tools/verify_inputs.py --staging '/Volumes/share-1/brad/games/ssx3-workbench'
python3 -m unittest discover -s tests -v
```

`inspect_disc.py --extract PATH --output FILE` extracts one file as stored,
optionally from `--archive`; it refuses to overwrite an existing file. For a new
Tricky preview, pass `probe_worlds.py tricky ... --assets NEW_DIRECTORY`.
Preview output files must not already exist. Reports may be regenerated in place.
`--hash-iso` optionally hashes a whole disc, which reads several GB over the share;
full-disc hashing was not needed for this initial investigation.
The image-building stage subsequently computed the SSX 3 full-disc SHA-256;
it is recorded in each build's `image.json`.

The OBJ has no textures, props, or validated collision. It samples each bicubic
patch on a 5×5 vertex grid and retains original game axes and units. It is suitable
for inspection in a mesh viewer, not direct insertion into SSX 3.

## Upstream reference

[GlitcherOG/SSX-Library](https://github.com/GlitcherOG/SSX-Library), GPL-3.0,
is cloned under `third_party/SSX-Library` at commit
`5c345e08dc521b0b1041734925cf0ece085e84c9`. Its binary layout and compression
implementations informed these tools; several labels needed correction against
the actual discs. The Python tools do not require or build the C# library.

To obtain the same reference in another checkout:

```sh
git clone https://github.com/GlitcherOG/SSX-Library.git third_party/SSX-Library
git -C third_party/SSX-Library checkout 5c345e08dc521b0b1041734925cf0ece085e84c9
```
