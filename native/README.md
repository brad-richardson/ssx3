# GameCube native prototype

Stock SSX 3 (GXBE69 rev 0) ahead-of-time recompiled with a Dolphin-derived
hardware runtime. macOS runs the stock game; the [iOS development
app](ios/README.md) embeds the translated module with on-screen controls.
Android remains a separate milestone.

Status as of 2026-09-18: stock boots through menus and runs Snow Jam with
Metal rendering and CPU JIT fallback disabled; donor courses ride via staged
game directories plus a boot-time course-redirect manifest (see
`docs/reserve/course-selection.md`, `docs/reserve/aloha-conversion.md`). For quoted frame
and timing numbers see `docs/numbers-ledger.md`, not this file.

## Reproduce

Pins are in `dependencies.json`. Use Apple Clang on the Mac with Python
3.11+, Git, CMake and Ninja:

```sh
python3 tools/native_gamecube.py bootstrap
python3 tools/native_gamecube.py configure
python3 tools/native_gamecube.py build --jobs 4
python3 tools/native_gamecube.py module --jobs 4
python3 tools/native_gamecube.py run --profile stock --seconds 60
```

`bootstrap` fetches the submodules used by these Metal builds into ignored
`third_party/`. To boot a converted course instead of stock, stage a game
directory with `tools/gamecube_game_dir.py` and select it with a manifest
(see `docs/reserve/course-selection.md`).

## Game data (user-supplied)

This clone contains no game data and no generated guest code. Supply your
own retail SSX 3 (USA) GameCube disc (GXBE69 rev 0; SHA-256 verified at
build and launch) and, for donor courses, your own SSX Tricky disc.
Extract into ignored `local/` paths (defaults overridable with
`run --game PATH`); originals stay read-only and the RVZ unchanged.

## Licensing

MIT for the project's own code. `third_party/` trees keep their own
licenses, GPL-3 for ModernGekko and its patches; any build that combines
them is GPL-3.

## Patches and evidence

Applied by bootstrap (see the full file for the list): platform/observability
patches, the course-redirect patch, and the mixer-skip patch. Each run writes
a log, launch receipt and sampled dispatch CSV under
`local/reports/native-runs/`. Counter semantics, the determinism gate
(`tools/native_determinism_check.py`), `--fast-fp`, and reverse-engineering
leads (`research.md`) are documented in the full file.
