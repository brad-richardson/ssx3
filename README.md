# SSX 3 preservation and performance research

GameCube static recompilation of SSX 3 on a Dolphin-derived runtime, 120 Hz
display work, the PS2 route, and the ps2xGS capture/replay harness.

The GameCube path recompiles the stock GXBE69 game ahead of time and runs it
natively on macOS and iOS (Metal graphics, CPU JIT fallback disabled). The
120 Hz work covers in-engine doubled simulation (route F), host-side frame
replay, and native pose smoothing. The PS2 route re-examines SSX 3
(SLUS-20772) under PS2Recomp on the Mac, with `ps2xGS` as the standalone
Graphics Synthesizer capture/replay harness feeding a GPU-backend loop.

## Status

Current measured numbers live in `docs/numbers-ledger.md`; the working plan is `docs/todo.md`.

- GameCube native runtime: boots, menus and races on macOS/iOS.
- 120 Hz: host replay measured at ~0.7–0.9 ms per replayed frame on the Odin 3.
- PS2 route: recompiled boot climbing the SDK/IOP ladder, with `ps2xGS` as the GS harness.

On the GameCube side, stock SSX 3 boots through menus and runs Snow Jam on
the Mac with Metal rendering and CPU JIT fallback disabled; donor courses
ride: Garibaldi (build gc-gari-013 lineage) and Aloha Ice Jam in the ASS1
slopestyle slot (gc-aloha-007) via a boot-time course-redirect manifest that
changes no byte of `main.dol`. See `docs/aloha-conversion.md`,
`docs/course-selection.md`, `native/README.md`.

## Repository map

```text
README.md            this file
docs/                plans, references, runbooks (index: docs/README.md)
docs/todo.md         living working list (most recent first per section)
docs/numbers-ledger.md  the one table for every quoted metric
docs/plan-120fps-2026-09-17.md   120 fps plan of record
docs/plan-gs-gpu-backend-2026-09-18.md  GPU GS backend plan (ps2xGS loop)
native/              GameCube native prototype (README, patches, diagnostics)
native/ios/          iOS development app
tools/               inspection, conversion, harness and measurement scripts
                     (index: tools/README.md; 120 scripts, stdlib-first)
tests/               unit tests (run: python3 -m unittest discover -s tests -v)
third_party/         vendored upstream trees (own licenses, see below)
local/               ignored: game data, builds, reports, receipts (never committed)
```

## Building what can be built without game data

Prerequisites: Python 3.11+, Git, CMake, Ninja, Apple Clang on macOS
(GameCube runtime); Xcode + signing identity + device (iOS app);
Python 3.10+ stdlib + macOS `bsdtar` (inspection tools).

```sh
python3 -m unittest discover -s tests -v   # no game data needed
python3 tools/inspect_disc.py --help       # read-only disc/archive inspection
python3 tools/native_gamecube.py bootstrap # fetches pinned submodules only
```

Anything that compiles the game module, stages a game directory, launches
the runtime, or opens the iOS app requires user-supplied game data (below)
and stays under ignored `local/` or the device. Fetched submodules land in
ignored `third_party/`; generated guest code is never committed.

## Configuration

Author-machine data locations come from the environment (defaults live in
`tools/paths.py`); the repository itself contains no game data. Every tool
that reads discs, extracted trees, or staged builds takes an explicit path
flag — the variables below apply only when a flag is omitted.

- `SSX3_WORKBENCH`: root of the ssx3-workbench tree — `builds/` (staged
  experiment builds), `source/` (e.g. `source/ssx3/BAM.BIG`), `extracted/`
  (e.g. `extracted/garibaldi/gari.pbd`), `native/` (e.g. `native/GXBE69`,
  the extracted GameCube tree), `emulator/` (PCSX2 profiles).
- `SSX3_GAMES`: root of the local games library — `ps2/`
  (e.g. `SSX 3 (USA).iso`), `gamecube/` (e.g. `SSX 3 (USA).rvz`).

A tool that needs one of these paths and finds neither the flag nor the
variable exits with an error naming the variable.

## Deliberately not included

Game images, extracted assets and recompiled guest code are never in this
repository: this clone contains no game images, no extracted game assets,
and no recompiled guest code — no `.iso`/`.rvz`/`.gcm`,
no `BAM.BIG`/`GARI.BIG` contents, no `main.dol`/`SLUS_207.72` copies, no
generated `output/` trees. You must supply them yourself from your own
retail copies:

- GameCube: SSX 3 (USA), Game ID GXBE69 rev 0 — verified by SHA-256 at
  build and launch (`b92162d6…fa29ce` per `native/research.md`); SSX Tricky
  (GameCube) for donor courses.
- PS2: SSX 3 (USA) SLUS-207.72 and SSX Tricky (USA) for the PS2-route tools.

Extract with the documented commands (see `native/README.md`) into ignored
`local/` paths; originals stay read-only.

## Licensing

MIT for this repository's own code and documentation (see `LICENSE`); the
vendored trees under `third_party/` keep their own licenses (GPL-3 for
ModernGekko, SSX-Library and sunpad-reference); the patches under
`native/patches/` modify GPL-3 code and are GPL-3; any build that combines
them is GPL-3; `tests/float-conversion-original-generated.h` is DolRecomp
(GPL-3) tool output kept as a test oracle.

## Related repositories

- `brad-richardson/ps2xGS` — standalone GS capture/replay harness + census
  (public, GPL-3).
- `brad-richardson/PS2Recomp` branch `ssx3` — fork for SSX 3 fixes, on top
  of upstream `14b1e5cb`; generated runner sources are never pushed.
- Upstream `ran-j/PS2Recomp` — the PS2 static-recompilation project.
- `ModernGekko/DolRecomp` — the GameCube static-recompilation upstream
  behind the native runtime.
