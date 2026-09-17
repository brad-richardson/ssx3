# Asset policy: shipped assets until the risky window closes

Decided September 17, 2026 (user). Supersedes the remaster rollout for now;
the packs and tooling are archived, not deleted.

## Rule

All profiling, validation, differential testing, and device runs use the
games' actual shipped assets. No upscaled texture pack on any path:

- Desktop: run without `--texture-pack` (no `Load/Textures/GXBE69` symlink,
  no `HiresTextures = True` in any profile's `GameSettings/GXBE69.ini`).
- iOS: no pack in the app container (`remasterPackInstalled == NO`, the
  pause-menu switch reads "No texture pack installed"); tooling launches
  pass `-ssxTextures stock` / `--textures stock` so the session log proves it.
- Android: no `Load/Textures` content on the device; no per-game ini override.

## Explicitly kept

SSX Tricky level injection and its assets stay. That is game content
(course worlds, `bam.big`), not a texture pack, and device game data is not
part of this revert.

## Why

Measurements do not support the pack as a frame-rate cause (iPad GPU ~7%
busy even with the pack preloaded; Odin Adreno ~0.5% of cycles), so this
revert buys no frames. It buys a collapsed graphics-debug search space —
any remaining corruption is backend or game-data, full stop — and clean
stock baselines for the frame-compare/differential validation the
float/recompiler work requires. The pack's own audit also still has an open
defect class (soft particle sprites gaining hard outlines).

## Archive

Packs frozen in place under `local/research/remaster/` (see `ARCHIVED.md`
there). Do not push them to devices. Runbook stays at
`docs/texture-remaster.md` for the method, not the rollout.

## Enforcement

Both push paths refuse without an explicit override, so neither a tired
human nor a background agent can reintroduce the pack by accident:

- `tools/mobile_gamecube.py textures` and `tools/native_gamecube.py launch
  --texture-pack` raise unless `SSX3_ALLOW_TEXTURE_PACK=1` is set.
- `local/research/remaster/install-tonight.sh` exits early under the same rule.
- `--texture-dump` still works (read-only diagnostics on stock assets).
- `launch --textures remaster` is unchanged: it is inert with no pack
  installed, and it is the sanctioned A/B mechanism when the pack returns.

## Normalization receipts (September 17)

- iPad Air M2: was running a 927-file DDS pack preloaded
  (`HiresTextures = True`, `texture_pack_state requested/installed/preload
  all true`). Pushed a `png` prune marker and relaunched; the app's own
  format prune removed 927 files (`texture_pack_pruned`). Verified on a
  flag-free launch: `HiresTextures = False`, `installed: false`.
  Game data untouched.
- Desktop profiles: scrubbed (no `HiresTextures = True` under
  `local/native/`).
- Odin3: was already stock (no `tex1_*` on device, empty `Load` dirs, no
  per-game ini overrides). The EGL snow corruption is therefore not a pack
  artifact.
- iPhone: out of scope, state unknown, untouched.

## Re-enable criteria

After the gate-review changes land and the frame-compare harness is green:
re-ride the pack on device, re-run `tools/texture_pack_audit.py` (the
particle family is still unfixed), and only then reintroduce per-device.
