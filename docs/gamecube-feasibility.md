# GameCube route: initial feasibility audit

Date: 2026-09-10 (local time). Status: disc, asset, and code-generation inspection;
this document records the initial audit. The subsequent
[native prototype](../native/README.md) has now linked and booted stock SSX 3
with Metal graphics and CPU JIT fallback disabled. The historical probe results
below remain distinct from that runtime work.

## Recommendation

Investigate **GameCube SSX 3 + ahead-of-time CPU recompilation + a Dolphin-derived
runtime** before committing to a full decompilation or a PS2 compatibility layer.
Use targeted reverse engineering for the standalone course launcher and asset
loading. Preserve the working PS2 prototype as a reference and fallback.

The intended product is standalone Tricky courses with SSX 3 handling, eventually
on iOS and Android with touch and physical controllers. Integration into SSX 3's
continuous mountain is optional. A full matching decompilation could improve
maintainability later; it is not a prerequisite for testing this route.

## Supplied images

Both images remain on `/Volumes/share/brad/games/gamecube/`. Inspection used
decomp-toolkit 1.8.4, commit `a0c455e46cab58e1d2e0885623f85089ff0499db`, reading
RVZ directly. No full ISO copies were created.

Full-disc verification passed for both images against decomp-toolkit's bundled
Redump database, including SHA-1, CRC32, and XXH64 checks.

| Property | SSX 3 | SSX Tricky |
| --- | --- | --- |
| File | `SSX 3 (USA).rvz` | `SSX Tricky (USA).rvz` |
| Disc ID / revision | `GXBE69` / 0 | `GSTE69` / 0 |
| Stored bytes | 1,043,189,072 | 800,692,148 |
| Compression | RVZ, Zstandard, 128 KiB blocks | Same |
| Files in disc filesystem | 110 | 246 |
| Main DOL bytes | 3,172,928 | 2,351,232 |
| Main DOL entry | `0x80003154` | `0x800051ec` |
| Relevant archive | `data/worlds/bam.big` | `data/models/gari.big` |

Verified full-disc SHA-1: SSX 3
`9f047c3c3389b5f2ad464afc472dd15cb0083474`; Tricky
`7adecbf91fff0c2b5907b2fd725a11d060ef95e0`.

SSX 3 DOL SHA-256:
`b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce`.

Tricky DOL SHA-256:
`d291118ff1d9b32881638ea4e5d14cf055a52c89e3ea633467c0722d1226a226`.

The DOLs have ordinary executable/data sections that decomp-toolkit can analyze.
It recognizes startup and SDK routines, including `main`; this is automatic
signature analysis, not recovered game source. SSX 3's disc filesystem has no
standalone `.rel`, `.rso`, or linker-symbol map files. Its `input.map` is input
configuration. Tricky's `gari.map` is a scene/export listing. This does not rule
out code loading or modification at runtime.

## What carries over from the PS2 work

Garibaldi's GameCube archive is the same C0FB archive family, and its members use
the RefPack decoder already in this project. All eleven members decompressed.

- Terrain uses `.nbd` in place of PS2 `.pbd`.
- **All 3,885 patches have exactly equal 16-vector shape coefficients** after
  decoding each platform's byte order. The maximum coefficient difference is 0.
- Both have 448-byte terrain records and 3,393 instance records. Equal counts
  do not establish that the instance/model formats are interchangeable.
- The GameCube terrain table starts at byte 160; PS2 starts at 144. Coefficients
  start at byte 80 within both records. Stored corners start at 364 on GameCube
  and 360 on PS2. Checking all GameCube patches against their stored corners
  gives a maximum error of 0.027884 game units.
- The 59,688-byte Garibaldi AI path file is byte-for-byte identical to PS2's.
- Textures/lightmaps use `.gsh` with `SHPG` headers; models, scenery, rails, and
  other platform-specific records still need converters.

SSX 3's GameCube archive retains the BIGF world container and related streaming
structure, but contains `.gdb/.gsb/.ghm/.gsm` instead of `.sdb/.ssb/.phm/.psm`.
The GameCube GDB tables and resource fields use big-endian numbers, while the
CBXS/CEND block-length field remains little-endian. The inspection decoded all
2,958 compressed blocks and matched every group's resource count to the GDB:

| Property | PS2 baseline | GameCube baseline |
| --- | --- | --- |
| Stream groups | 159 | 205 |
| Terrain patches | 30,644 | 30,644 |
| Terrain resource payload bytes | 432 | 430 |

GameCube has 49 locations and 275 spatial records. Its binary payload differences
mean the existing PS2 world writer cannot be applied unchanged. The terrain
math, donor route, and much of the extraction research are reusable; PS2 ELF
patches, ISO9660 packaging, and PCSX2 memory addresses are platform-specific.

## Recompilation probe

Built DolRecomp at `40637c4683bd2820ac5b23607ee344720beb26df`, using its C backend.
Its DOL, opcode, and floating-point-semantics tests passed. SSX 3 code generation
completed successfully:

- 716,958 instruction words recognized, 1,642 words classified as embedded data,
  and zero unknown instructions reported by the tool.
- 176 generated code chunks plus a dispatcher.
- All 177 generated C translation units passed Clang `-fsyntax-only` for
  `arm64-apple-ios16.0`, using the installed iPhoneOS 26.5 SDK.
- The generator flagged **115 address ranges for possible runtime code
  modification**. These are review candidates, not 115 confirmed bugs.

These results establish that the executable is accessible to the tooling and
the generated C is accepted for the target. They do **not** establish correct
execution, full native runtime coverage, game performance, or playable iOS support.
Embedded-data classification is also a static heuristic, not execution evidence.

The C probe uses the RecompCore interface. At this DolRecomp revision, selecting
the ModernGekko output interface requires its LLVM backend and LLVM 19/20; the
installed Homebrew LLVM is 23.1.0. A runtime experiment must pin compatible
generator/runtime revisions and toolchain rather than mix current heads. No
ModernGekko module was linked in this audit.

Upstream [DolRecomp](https://github.com/ExpansionPak/DolRecomp) provides CPU
translation. [ModernGekko's template](https://github.com/ExpansionPak/ModernGekko-Template)
supplies a starting point for the Dolphin-derived graphics/audio/runtime work.
[SunPad](https://github.com/chrissotraidis/sunpad) demonstrates an Apple integration
with AOT code and interpreter fallback on iOS, but its
[known issues](https://github.com/chrissotraidis/sunpad/blob/main/docs/KNOWN_ISSUES.md)
still report iPhone performance limitations and development-oriented module
provisioning. Its existence is useful precedent, not SSX 3 compatibility evidence.

## Options and decision gates

| Route | Best use | Main limitation |
| --- | --- | --- |
| Continue PS2 course import | Fastest route to improving the existing Odin prototype | Does not itself deliver a native iOS app |
| GameCube AOT + targeted reverse engineering | Recommended next native feasibility experiment | Runtime correctness, code modification, and mobile performance remain unproven |
| Full decompilation and platform port | Long-term readable engine and broad customization | Much more foundational work before a complete game is available |

1. **Compare stock GameCube SSX 3 on the Odin.** Confirm the handling and
   available tricks/control behavior suit the intended experience. Do not assume
   identical gameplay just because the title is the same.
2. **Boot stock SSX 3 through a pinned native runtime on the Mac.** Reach a
   course, ride, crash/reset, and save/reload. Record AOT dispatch, fallback,
   code-modification, graphics, audio, and simulation-speed evidence. A title
   screen alone does not pass this gate.
3. **Test a stock course on a physical iPhone early, with JIT disabled.** Check
   sustained game speed, input latency, thermals, audio, lifecycle, and saves.
   Include any runtime CPU helpers in the no-JIT audit. Native compilation alone
   does not pass this gate. Android gets a separate build and runtime check.
4. **Implement one standalone Garibaldi event.** Convert the original terrain,
   textures/lightmaps, scenery, collision and rails; add direct course entry,
   reset/retry, and return-to-menu. Reuse the verified donor coefficients and path.
5. **Expand content and package mobile controls.** Establish common gameplay
   input mapping for touch and controllers, then add more courses. Distribution
   packaging must include the prebuilt signed code and avoid depending on the
   development module-injection workflow.

## Evidence and storage

Detailed inventories, archive tables, decoded-member hashes, world counts,
codegen log, SMC address list, and iOS syntax-check receipt are under ignored
`local/reports/gamecube/`. Small extracted game files stay under ignored
`local/source/gamecube/`. No game bytes or generated game code belong in Git.

The approximately 177 MiB of generated C was removed after the check; its file
hashes and regeneration command are retained. Regenerate with:

```sh
local/tooling/dolrecomp-build/dolrecomp --gamecube --backend c \
  --game-id GXBE69 --runtime recompcore -j4 \
  local/source/gamecube/ssx3/sys/main.dol local/recomp-probe/ssx3
```

Five local PS2 test ISO copies and disposable Swift/world/Python caches were
removed. Build archives, recipes, and runtime evidence remain. Shared builds
002, 009, and 010 are retained; intermediate 007/008 ISOs can be regenerated
from their retained build archives. A fresh full SHA-256 check of shared build
010 matched its delivery receipt. Its local launcher now uses a symlink to the
shared ISO. See `local/reports/disk-cleanup.json` for the cleanup record.
