# Garibaldi test on Odin 3

Build: **run-gari-010**. Ready for an experimental freeride test. This version
starts on Garibaldi's original opening, including its right-hand bend. The
main descent and resets at 1%, 25%, 50%, 75% and near the endpoint passed on
Mac PCSX2 2.8.2, with no logged TLB memory faults.

The user has loaded and ridden build 009 on the Odin 3 and recognizes the
layout, but finds the missing textures and scenery disorienting. Build 010
still needs a handheld test; full-route coverage and performance have not
been measured there. NetherSX2 is the likely installed app; its version is
unconfirmed.

## GameCube build in Dolphin (current path)

The GameCube builds (`gc-gari-NNN`, latest **gc-gari-009**: Garibaldi with its
own textures, lightmaps, race line and opponents) are full GameCube disc
images for Dolphin for Android, which runs them with its JIT. The image is
`ssx3-workbench/builds/gc-gari-009/SSX3-gc-gari-009.iso` on the share
(1,459,978,240 bytes, SHA-256 in `sha256.txt` next to it). Copy it to the
Odin, add its folder to Dolphin's game list, and start Single Event -> Race
-> Peak 1 Snow Jam: that event now loads Garibaldi. No save state is needed.

For later builds, pair the Odin with adb once (Developer options -> Wireless
debugging -> Pair device with pairing code, then `adb pair` and `adb connect`
on the Mac, or USB debugging) and push straight from the repository:

```sh
python3 tools/deploy_odin.py local/builds/gc-gari-009/SSX3-gc-gari-009.iso \
  --destination /sdcard/Games/GameCube
```

The tool verifies the size and MD5 on the device; point `--destination` at
whatever folder Dolphin scans. The PS2 steps below are for the earlier
`run-gari` builds and NetherSX2.

## Put the build on the handheld

1. Copy this file from the games share to the Odin's internal storage or SD card:
   `ssx3-workbench/builds/run-gari-010/iso/SSX3-relocated.iso`.
   It is 3,118,266,368 bytes (about 3.12 GB). You can name the copied file
   `SSX3-Garibaldi-run-gari-010.iso` to distinguish it from stock SSX 3.
2. Open that ISO in your existing Android PS2 emulator, likely NetherSX2.
   The ISO contains the course changes; `launch.command` is only for the Mac.
   Start with the settings that already work for your original SSX 3.
3. Boot from the beginning rather than resuming an older save state. A save
   state can restore the old course data in memory. An ordinary in-game save
   for SSX 3 (USA) is fine; use one with Peak 1 freeride available.
4. Choose **Conquer the Mountain**, load your character, then pause and choose
   **Transport → Peak 1 → Freeride → Garibaldi**. The emulator's game list may
   still label the game SSX 3 because the disc serial is unchanged.

If you need the project's test save, the existing Mac test memory card is at
`ssx3-workbench/emulator/test-002/profile/PCSX2/memcards/Mcd001.ps2` on the share.
Keep your current handheld saves backed up before importing a separate card;
the exact import steps depend on the installed emulator version.

NetherSX2's own documentation recommends Optimal/Safe defaults. Its settings
and transfer documentation is in the [official project README](https://github.com/Trixarian/NetherSX2-patch).
There is no need to change a working emulator installation for this first test.

## What to check

- Check the restored opening right turn, then ride down the main course.
  The terrain should stay visible all the way down.
- Use the game's normal Reset control near the top, middle and bottom. Check
  that it returns you to nearby Garibaldi terrain and you can keep riding.
- Note invisible walls, holes, abrupt jumps, hangs, crashes and slow sections.
  A screenshot or rough location helps reproduce a problem.
- With feedback, include the emulator name/version, renderer and resolution
  if available. A comparison with stock SSX 3 at the same settings helps
  distinguish course problems from general emulator performance.

## Expected unfinished features

The terrain currently uses a temporary SSX 3 snow texture and lightmap.
Repeating shading bands are expected; original Garibaldi textures and lighting
are not imported yet. Scenery is incomplete, and old rails, particles, camera
triggers and map art remain. Alternate routes have not all been ridden.

Use freeride: race rules, opponents, a working finish, medals and a mountain
exit are still future work. Reaching the bottom does not complete an event.

## Work after this test

1. Fix issues found on the Odin and check alternate routes and entry/exit joins.
2. Import Garibaldi's original materials, textures and lighting.
3. Restore its scenery, rails, object collision and cameras.
4. Build race starts, opponents, checkpoints, finish and medals, then repeat
   desktop and handheld performance and progression checks.

Verified ISO SHA-256:
`5e53a8151497d80f03d04381648253d4aefa834295d1f1cf52c1c0531af9fcc5`.
