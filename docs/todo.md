# Working todo

Living list, most recent first within each section. Move items to Done with
the build or commit that closed them.

## Now

- [ ] Xbox prompt glyphs: swap the frontend button icon textures so in-game
      prompts read A/B/X/Y in Xbox positions; relabel the touch overlay to match.
- [ ] Control mapping doc: one table of action → GameCube input → Xbox pad →
      touch control, kept in `native/ios/README.md`.
- [ ] Odin: package the patched GameCube disc as an image Dolphin for Android
      can load (the archive grew 460 KB, so the FST needs rebuilding).
- [ ] 120 Hz spike: finish the color-only measurement on `spike/120hz`, then
      decide between MetalFX with depth-reprojected motion vectors and the
      color-only path.

## Garibaldi in the GameCube engine

- [ ] Import Garibaldi's own textures and lightmaps from GameCube Tricky
      (`.gsh` SHPG) in place of the pinned fallback snow material.
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

- [x] 2026-09-11 gc-gari-005: first rideable GameCube Garibaldi (race start,
      ride, restart, zero invalid accesses).
- [x] 2026-09-11 Two-stick touch overlay; right stick drives the D-pad for spins.
- [x] 2026-09-11 PS2-position physical pad mapping with grab translation.
- [x] 2026-09-11 iPhone smoke run at 60 FPS, no JIT.
