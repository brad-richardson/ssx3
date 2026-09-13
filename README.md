# SSX 3 course-port investigation

The first donor course is **Garibaldi from SSX Tricky**. The intended experience
is standalone Tricky courses with SSX 3's handling. The working prototype uses
the PS2 games; a GameCube AOT runtime now provides the native-port foundation.

The [GameCube feasibility audit](docs/gamecube-feasibility.md) compares the newly
supplied discs, verifies reusable Garibaldi terrain/path data, and records an
SSX 3 code-generation probe. The [native prototype](native/README.md) now builds
and runs stock GameCube SSX 3's Snow Jam on the Mac with Metal graphics and CPU
JIT fallback disabled. Build **gc-gari-013**, copied to the iPhone with a matching
readback hash, adds a shared [terrain material conversion](docs/gamecube-materials.md)
that fixes the 1×/2× lighting mismatch behind clipped white snow. It retains
the texture-ID, occlusion-wall and terrain-bounds repairs from build 012.
The [original/before/after comparison](docs/garibaldi-visual-comparison.md)
shows restored snow detail. Donor fog/backdrop/scenery, frame-by-frame jump
visibility, clean route/finish acceptance and save/reload remain.
The [iOS development app](native/ios/README.md) builds with a statically linked
game module, Metal graphics, and touch controls for menu navigation and riding.
Earlier physical-device smoke runs reach about 60 FPS; sustained performance
acceptance remains deferred. The [architecture review](docs/architecture-review.md)
prioritizes validated course compilation and repeatable gameplay checks.

This repository contains inspection, world-rebuild and emulator-driving tools.
A Garibaldi terrain section has been imported and ridden in the Green Station
hub. Growable archives and executable menu renames also work in PCSX2. The
earlier PS2 experiment replaces Snow Jam's entire terrain set with Garibaldi,
keeps its fallback snow material visible, and rides the complete main route
with working resets. Old prop collision and gameplay scripts are disabled.
A finished Garibaldi race remains in progress.

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
See [the full-course experiment](docs/full-course-experiment.md) for the resumed
Snow Jam replacement, its placement, reproducible commands and remaining limits.
The [runtime comparison](docs/runtime-validation.json) records state hashes,
memory offsets, and the four verified coefficient changes.

## Try it yourself

For the **iPhone app**, cold-launch SSX and choose Single Event → Snow Jam Race.
The slot currently loads **gc-gari-013**; the frontend name still needs changing.
Its world archive and build report are in `local/builds/gc-gari-013/`.

The latest **PS2** prototype is **run-gari-010**, copied and hash-verified at
`/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-010/`.
On the Mac, double-click its `launch.command` to boot with the isolated shared
test-002 profile. Choose Conquer the Mountain, the saved Mac character, then
Transport → Peak 1 → Freeride → Garibaldi. This build restores Garibaldi's
original start and opening right turn, which build 009's approach bypassed.
The main descent and five reset checks pass with no logged TLB memory faults.
The fallback snow texture/lightmap still has
repeating bands; original Garibaldi art and race setup remain unfinished.

For the **Odin 3**, copy `iso/SSX3-relocated.iso` from that build to the handheld
and open it in your Android PS2 emulator (likely NetherSX2). Cold-boot the ISO;
do not resume an older save state. See the [Odin test guide](docs/odin-testing.md),
also included as `ODIN-TESTING.md` in the shared build. The user has confirmed
that build 009 loads and rides on Odin 3 and recognizes the layout. The missing
textures and scenery make it harder to read. Build 010 still needs handheld
feedback; the measured runtime evidence is from Mac PCSX2 2.8.2.

The launcher at `local/builds/run-gari-010/` uses
`local/emulator/course-cleanup/profile` and a symlink to the shared ISO, so the
share must be mounted. Local test ISO copies and disposable caches were removed
to recover disk space; build archives, recipes, and runtime evidence remain.
Older shared builds are retained separately, with build 009's opening-coverage
correction in its notes.

For the earlier hub experiments listed below, cold-boot an image in PCSX2
(2.x), choose Conquer the Mountain with the Mac
save, pause, Transport → Peak 1 → Freeride → Green Station, and ride the main
line down the hub. The edited patch (`patch_A_hub_1024`) is about 20 seconds
after the spawn, just before the Race/Slope Style banner tent.

| Image | What to look for |
| --- | --- |
| `builds/bump-002/SSX3-bump.iso` | a rounded 75-unit crest on the trail that the board rides over |
| `builds/grown-001/iso/SSX3-relocated.iso` | a raised strip of five copied patches; the rider rides on it |
| `builds/hdr-003/SSX3-words.iso` | the same patch renders dark and untextured (foreign texture ids) |
| `builds/hdr-006/SSX3-words.iso` | the board sinks into deep snow on that patch (material word) |
| `builds/gari-003/iso/SSX3-relocated.iso` | **Garibaldi terrain in SSX 3**: big banked walls overlaid on the hub line right after the lodge |
| `builds/scale-002/iso/SSX3-relocated.iso` | 1,439 Garibaldi patches in the hub (memory-budget test); huge walls, easy to get stuck in |
| `builds/name-001/SSX3-named.iso` | **"Garibaldi" in the transport menu** (Peak 1 freeride list) and "Tricky Base Station"; same terrain as scale-002 |
| `builds/control-005/iso/SSX3-relocated.iso` | should look exactly like the original: our block layout, our archive |
| `builds/control-006/SSX3-relocated.iso` | should look exactly like the original: archive appended to a bigger image |

The test-002 profile under `emulator/` has double-clickable launchers for each
image; they use an isolated PCSX2 profile and copied memory cards, so your own
settings and saves are untouched.

## Storage

Code, tests, and small reports live here. Large inputs and archived builds live
on the network share; current test builds and evidence use ignored `local/`.

The [share recovery setup](docs/share-recovery.md) reconnects the SMB share at
login and every minute, with status and disable commands.

```text
/Volumes/share/brad/games/
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
      run-gari-002/                # earlier full-course prototype
      run-gari-009/                # terrain/resets fixed; original opening bypassed
      run-gari-010/                # original opening, main descent and resets tested
        iso/SSX3-relocated.iso
        launch.command
        ODIN-TESTING.md            # Odin 3 test steps and known limitations
        evidence/                 # saved measurements, screenshots and test log
        launch-logs/              # logs from subsequent launches
        transfer.json             # verified copy hashes and original paths
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
python3 tools/inspect_disc.py '/Volumes/share/brad/games/ps2/SSX 3 (USA).iso' --archive DATA/WORLDS/BAM.BIG --output local/reports/ssx3-disc.json
python3 tools/inspect_disc.py '/Volumes/share/brad/games/ps2/SSX Tricky (USA).iso' --archive DATA/MODELS/GARI.BIG --output local/reports/tricky-disc.json
```

Reproduce reports from the staged archives (read-only):

```sh
python3 tools/probe_worlds.py ssx3 '/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG' --report local/reports/ssx3-world.json
python3 tools/probe_worlds.py tricky '/Volumes/share/brad/games/ssx3-workbench/source/tricky/GARI.BIG' --report local/reports/garibaldi.json
python3 tools/verify_inputs.py --staging '/Volumes/share/brad/games/ssx3-workbench'
python3 -m unittest discover -s tests -v
```

Rebuild and image tools (all refuse to overwrite existing outputs and verify their
own output by readback):

```sh
python3 tools/build_world_experiment.py SRC/BAM.BIG --height 75 --rid 213 --output BUILDS/bump-00N   # one-patch edit
python3 tools/build_test_images.py 'PS2/SSX 3 (USA).iso' BUILDS/bump-00N                            # same-size archive into a new ISO
python3 tools/recompress_stream.py SRC/BAM.BIG --output BUILDS/control-00N --jobs 8                # every block re-encoded in place
python3 tools/relayout_stream.py SRC/BAM.BIG --output BUILDS/control-00N --jobs 8                  # new block boundaries, new SDB offsets
python3 tools/relocate_archive.py 'PS2/SSX 3 (USA).iso' BUILDS/x/BAM.BIG --output BUILDS/x/iso            # archive into PAD0.000 (same image size)
python3 tools/relocate_archive.py 'PS2/SSX 3 (USA).iso' BUILDS/x/BAM.BIG --output BUILDS/x/iso --append   # archive appended, image grows
python3 tools/grow_group.py SRC/BAM.BIG --group 2 --rids 152,199,29,213,270 --dz 60 --output BUILDS/grown-00N   # add patch copies to a group
python3 tools/patch_executable.py IN.iso --output OUT.iso --rename 'ARA1=Garibaldi:Gari'   # rename a level-selector entry
python3 tools/patch_locale.py IN.iso --find 'Snow Jam'                                    # inspect UTF-16 locale descriptions
python3 tools/build_course_image.py IN.iso BUILDS/x/BAM.BIG --output BUILDS/x/iso          # world + Garibaldi name + description
python3 tools/import_terrain.py SRC/BAM.BIG --line RIDE.jsonl --z-range=-24000,-19000 --lateral 3500 --output BUILDS/gari-00N  # Garibaldi section into hub A
```

Emulator tools (macOS, PCSX2 with PINE enabled in the test profile):

```sh
sh tools/macos/build.sh                                   # compiles keyd, press_keys, window_id into local/bin
python3 tools/pine.py                                     # emulator status, serial, title
SIGN=1 CAPTURE_AT=-89775,40015 sh tools/macos/green_station_ride.sh LAUNCHER OUT_DIR '-89775,40015;-93000,40400'
python3 tools/patch_crossing.py OUT_DIR/ride.jsonl BUILDS/bump-002   # rider height versus original and edited surfaces
python3 tools/ride_locations.py OUT_DIR/ride.jsonl                  # which locations a ride passed through
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

## Repository boundary

This repository contains authored tools, app integration, tests, patch files
for public runtime dependencies, and engineering notes. Retail game images,
extracted assets, disassembly, generated/recompiled game source, saves, build
products, signing credentials and device reports stay in ignored `local/`.
Dependency checkouts stay in ignored `third_party/`. Do not force-add either
directory. Reproducing a build requires supplying those inputs locally.

The current 120 Hz investigation is documented in
[the analysis notes](docs/research/120hz-analysis.md).
