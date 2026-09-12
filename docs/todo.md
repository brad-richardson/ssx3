# Working todo

Living list, most recent first within each section. Move items to Done with
the build or commit that closed them.

## Now

- [ ] Control mapping doc (partly done in `native/ios/README.md` Controls): one table of action → GameCube input → Xbox pad →
      touch control, kept in `native/ios/README.md`.
- [ ] Odin: test the GameCube Garibaldi in Dolphin for Android; the disc
      builder is done, the handheld run is not. `SSX3-gc-gari-005.iso` is on the
      share; `local/builds/gc-gari-008/SSX3-gc-gari-008.iso` (own textures)
      still needs copying there.
- [ ] 120 Hz spike: finish the color-only measurement on `spike/120hz`, then
      decide between MetalFX with depth-reprojected motion vectors and the
      color-only path.

## Garibaldi in the GameCube engine

- [ ] Scenery, rails and object collision from the donor.
- [ ] Opponents: give AI slots 0-5 the donor race lines instead of Snow Jam's.
- [ ] Progress meter starts at 28%: align the race track path origin with the
      relocated gate.
- [ ] Remove Snow Jam kind-2 scenery that now floats over the imported course.
- [ ] Course name and description in the GameCube frontend (DOL/locale edit).

## Controls

- [ ] Touch control for the C-stick (board press), currently unmapped.
- [ ] Optional DOL patch: four-input grab mask to restore the eight PS2-only grabs.
- [ ] Exercise the physical-controller path with a real pad (untested so far).

## Mobile

- [ ] 15-minute sustained soak on the iPhone (thermal, audio starvation).
- [ ] Save / memory-card behaviour on the phone.
- [ ] Android native build (Vulkan backend, NDK toolchain); user has a dev
      account to configure. Not needed for the Odin while Dolphin runs the
      patched disc with JIT.
- [ ] Exception-vector interpreter fallback (0x0C00/0x0500): measure, then
      translate or hook if phone timings need it.

## Done

- [x] 2026-09-11 gc-gari-008: Garibaldi's own textures and lightmaps from the
      GameCube Tricky `.gsh` sheets (`tools/gamecube_textures.py`); the race
      rides in Garibaldi art with zero invalid accesses. Rids are reclaimed
      from Snow Jam because other texture groups stay resident and rids
      above about 800 do not resolve. Lightmap orientation verified offline
      (`tools/lightmap_orientation.py`): both engines use the same cell mapping.
- [x] 2026-09-11 Xbox prompt glyphs: `tools/patch_ui_glyphs.py` repaints the
      B/X/Y icons in the three UI sheets; in-game menu shows green A and blue X.
      Installed on the phone, in the gc-gari-005 disc root and the shared ISO.

- [x] 2026-09-11 `tools/build_gc_iso.py` rebuilds a GameCube ISO; stock FST
      reproduced byte for byte.
- [x] 2026-09-11 Touch overlay relabelled to Xbox positions (A bottom, B right,
      X left, Y top, LB/RB).
- [x] 2026-09-11 gc-gari-005: first rideable GameCube Garibaldi (race start,
      ride, restart, zero invalid accesses).
- [x] 2026-09-11 Two-stick touch overlay; right stick drives the D-pad for spins.
- [x] 2026-09-11 PS2-position physical pad mapping with grab translation.
- [x] 2026-09-11 iPhone smoke run at 60 FPS, no JIT.
