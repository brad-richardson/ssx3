# SSX 3 preservation and performance research

GameCube static recompilation of SSX 3 on a Dolphin-derived runtime, 120 Hz
display work, the PS2 route, and the ps2xGS capture/replay harness.

The GameCube path recompiles the stock GXBE69 game ahead of time and runs it
natively on macOS and iOS (Metal graphics, CPU JIT fallback disabled). The
120 Hz work covers in-engine doubled simulation (route F), host-side frame
replay, and native pose smoothing. The PS2 route re-examines SSX 3
(SLUS-20772) under PS2Recomp on the Mac, with `ps2xGS` as the standalone
Graphics Synthesizer capture/replay harness feeding a GPU-backend loop.

## Status as of 2026-09-18 (quoted, not invented)

From `docs/numbers-ledger.md` (Live rows):

- "Odin race pace, OGL | 0.83× mean / 0.63× low (~50/~38 fps) | 09-17"
- "Odin race pace, Vulkan (true) | 0.73× mean / 0.64× low (~44/~38 fps) | 09-17"
- "Host replay capacity, Odin EGL (S2, fixed) — 200/200 replays, `done`
  verified, two arms | Wall per replay median 0.665 / 0.866 ms ...
  Capacity gate (≤6 ms) PASSED ~7×."
- "PS2 throughput gate: stock SSX 3 (SLUS-20772) uncapped in NetherSX2 on the
  Odin, Snow Jam race | 4.2–4.4× real time in the race ... 2.5× capped rerun:
  open riding HOLDS the cap at 253% / 151.6 fps in every riding frame"
- "Upstream C module on the patched-upstream runtime, desktop | 10.23 ms CPU
  per guest frame capped 1.0 (speed 1.0095), 9.96 uncapped (1.64× headroom),
  race verified (HUD 0:37, 1st/6, 75 MPH)"
- "ps2xGS harness + census on synthetic streams (G0) | ... identity replay
  CPU→CPU byte-exact on all 78 ... CTest 6/6"
- "PS2Recomp re-spike on the Mac, arm64 (P1) | ... the game loads, starts,
  sets up its heap, then spins in the SDK's kernel-patch scanner
  (`sub_0042C1F0`) ... fix = TOML `ret0@0x0042c1f0` (P1b)"

From `docs/todo.md` (Now):

- "Plan of record for 120 fps (September 17 evening):
  docs/plan-120fps-2026-09-17.md — owner-held gates, muse briefs D1/M1
  launched, M2/M3/M4/D2/D3/D4 queued, S1/S2 gated."
- "G0 read (09-18 15:40) — harness + census DONE, pushed"
- "P1 read (09-18 14:10) — PS2Recomp boots to the kernel-patch scanner;
  P1b launched"
- "ssx3 publication audit LAUNCHED (09-18 16:00), user decision"

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

## Deliberately not included

This clone contains no game images, no extracted game assets, and no
recompiled guest code: no `.iso`/`.rvz`/`.gcm`, no `BAM.BIG`/`GARI.BIG`
contents, no `main.dol`/`SLUS_207.72` copies, no generated `output/` trees.
You must supply your own retail copies:

- GameCube: SSX 3 (USA), Game ID GXBE69 rev 0 — verified by SHA-256 at
  build and launch (`b92162d6…fa29ce` per `native/research.md`); SSX Tricky
  (GameCube) for donor courses.
- PS2: SSX 3 (USA) SLUS-207.72 and SSX Tricky (USA) for the PS2-route tools.

Extract with the documented commands (see `native/README.md`) into ignored
`local/` paths; originals stay read-only.

## Licensing

MIT for the project's own code. `third_party/` trees keep their own
licenses, GPL-3 for ModernGekko and its patches; any build that combines
them is GPL-3.

## Related repositories

- `brad-richardson/ps2xGS` — standalone GS capture/replay harness + census
  (public, GPL-3).
- `brad-richardson/PS2Recomp` branch `ssx3` — fork for SSX 3 fixes, on top
  of upstream `14b1e5cb`; generated runner sources are never pushed.
- Upstream `ran-j/PS2Recomp` — the PS2 static-recompilation project.
- `ModernGekko/DolRecomp` — the GameCube static-recompilation upstream
  behind the native runtime.
