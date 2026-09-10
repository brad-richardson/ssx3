# SSX 3 course-port investigation

The first donor course is **Garibaldi from SSX Tricky (PS2)**. The goal is a short,
rideable section inside the original SSX 3 engine, followed by a complete course
if terrain, collision, and streaming can be rebuilt reliably.

This repository currently contains **inspection and extraction tools**. It does
not yet build a playable mod or modify an ISO.

## Current results

- Both supplied PS2 disc inventories parsed and independently matched `bsdtar`.
- SSX 3's executable matches the decompilation project's supported NTSC-U version.
- SSX 3's complete world archive decodes: 159 groups, 30,644 terrain patches.
- Garibaldi's terrain decodes: 3,885 patches; an untextured OBJ preview is staged.
- Staged archives are byte-identical to independent extraction from the ISOs.

See [the investigation log](docs/investigation.md) for evidence, format findings,
limitations, upstream provenance, and the next implementation steps.

## Storage

Code, tests, and small reports live here. Large files live on the network share:

```text
/Volumes/share-1/brad/games/
  SSX 3 (USA).iso                  # original, read-only input
  SSX Tricky (USA).iso             # original, read-only input
  ssx3-workbench/
    source/ssx3/BAM.BIG            # exact archive extracted from SSX 3
    source/tricky/GARI.BIG         # exact archive extracted from Tricky
    extracted/garibaldi/
      gari.pbd                    # decompressed terrain/scene container
      garibaldi-terrain.obj        # terrain preview, original coordinates
```

`local/` and `third_party/` are ignored by Git. No game assets, executables, ISOs,
or generated meshes belong in commits. The upstream clone is only about 3.3 MiB.

## Running the tools

Python 3.10+ and the standard library suffice. The independent verification tool
also uses macOS's `bsdtar`. No .NET runtime, game SDK, or additional BIOS is needed
for these inspections.

Inventory the discs and relevant archive directories without copying whole ISOs:

```sh
python3 tools/inspect_disc.py '/Volumes/share-1/brad/games/SSX 3 (USA).iso' --archive DATA/WORLDS/BAM.BIG --output local/reports/ssx3-disc.json
python3 tools/inspect_disc.py '/Volumes/share-1/brad/games/SSX Tricky (USA).iso' --archive DATA/MODELS/GARI.BIG --output local/reports/tricky-disc.json
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
