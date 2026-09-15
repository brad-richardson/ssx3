# Course selection by runtime redirect (GameCube)

SSX 3's frontend reads which world to load, what to call it and which discipline
to run out of plain data in the DOL's `data5` section. The native runtime
rewrites that data in guest RAM at boot from a host-side manifest, so a course
is selected without changing a byte of `sys/main.dol`: the pinned `dol_sha256`
in `native/dependencies.json` stays valid, the runtime CMake pin is unchanged,
and the generated module is never regenerated. The module hashes only *code*
chunks, and every field below is data, so the chassis SMC guard is untouched.

This is mechanism (c) of `local/research/course-selection.md`, now measured.

## The manifest

Plain text, one `key = value` per line. `#` starts a comment; blank lines are
ignored. An `event = N` line opens a block, and every following key applies to
that event until the next `event` line. Keys may appear once per block, and a
block must set at least one field.

| key | writes | guest address (event 0) | accepted values |
| --- | --- | --- | --- |
| `event` | selects the block's event index | — | 0–22; event 0 is Snow Jam |
| `name` | event record `+4`, 32 B | `0x802CE5F0` | ≤ 31 printable ASCII bytes |
| `short` | event record `+36`, 16 B | `0x802CE610` | ≤ 15 printable ASCII bytes |
| `code` | event record `+52`, 16 B | `0x802CE620` | ≤ 15; the SDB location code, e.g. `ASS1` |
| `archive` | event record `+68`, 16 B | `0x802CE630` | ≤ 15; the world archive basename |
| `location` | topology row `+16` | `0x802E2890` | 0–49, the location-table id |
| `mode` | mode row `+4` | `0x802E2C1C` | 1 station/debug, 2 race, 3 slopestyle, 4 big air, 5 halfpipe, 6 backcountry |

Tables: events `0x802CE5EC` (23 × 100 B), topology `0x802E2880` (23 × 40 B),
mode `0x802E2C18` (23 × 8 B). All three are indexed by event and all three start
each row with the event index; the runtime verifies all 69 of those words before
writing anything, so a different executable fails loudly instead of corrupting
memory. Strings are written NUL-padded to the full field width.

Example — point Snow Jam at an imported course that lives in
`files/data/worlds/alo.big` under location `ASS1`:

```
event = 0
archive = alo
code = ASS1
name = Aloha Ice Jam
short = Aloha
location = 5
mode = 3
```

## Applying it

- Desktop: `SSX_COURSE_MANIFEST=/path/course.txt`, or
  `tools/gamecube_course_check.py --course-manifest /path/course.txt`, which
  validates the file before it starts a run, copies it into the evidence
  directory and records the parsed redirects in `observations.json`.
- iOS: `-ssxCourseManifest <name>`, a bare file name inside the app's
  `Documents/`; `native/ios/App.mm` turns it into the same environment variable.

The hook is `SSX3::ApplyCourseManifest` (`Ssx3CoursePatch.cpp`), called at the
end of `CBoot::BootUp` in the vendored Dolphin chassis, after every boot arm has
placed the executable image in guest RAM and before the CPU runs. `BootUp` is
the only entry point that loads a title, so a re-boot or a full reset
re-applies the manifest. With no manifest the hook returns immediately. Each
write is logged to stderr with its address and its pre-patch value:

```
[ssx3-course] applying /…/aloha-ass1.txt
[ssx3-course] event 0 code at 802ce620: "ARA1" -> "ASS1"
[ssx3-course] event 0 location at 802e2890: 0 -> 5
```

## What the fields actually do — measured

Four bounded native checks, 200 s each, `tools/gamecube_course_check.py`,
evidence under `local/research/course-redirect/`.

**The archive name chooses the disc file *and* the member names inside it.**
`run-ala-001` (profile `sg-redirect-4`) booted a game directory whose only world
archive is `files/data/worlds/ala.big` — the stock `bam.big` with its five BIGF
member names rewritten `data/worlds/bam.*` → `data/worlds/ala.*`, the same
length so the rest of the 100 MB archive is byte-identical — with a manifest
setting `archive = ala` and nothing else. It rode. There is no `bam.big` on that
disc at all, so the `+68` field alone drove the load.

The member rename is required, and that is the trap. `run-gari-name-001`
(`sg-redirect-1`) set `archive = gari` against `gari.big` holding the *unrenamed*
stock members and faulted at course load (`Invalid write to 0x00000014,
PC = 0x80256440`), as did `run-aloha-gari-001` (`sg-redirect-2`) with the Aloha
archive under the same name. The path builder at `0x80106574` keeps the
extension-less `data/worlds/<archive>` string and appends `.big`, `.gdb`, `.gsb`
from it, so a `gari.big` whose members are still called `data/worlds/bam.gdb`
resolves to a NULL resource. **Rule: the archive basename and the BIGF member
basenames must match.**

**Case does not matter.** `ala` and `gari` were written lowercase against
lowercase files; stock writes `BAM` against `bam.big`. The game's own
`DVDConvertPathToEntrynum` folds case (mirrored in
`GXRuntime/src/dvd.c:name_matches`), and Dolphin's DirectoryBlob rebuilds the
FST from `files/` on every boot (`BuildFSTFromFolder`), so a newly added
`files/data/worlds/<name>.big` is visible without touching `sys/fst.bin`.

**The code and the location id must move with the archive.**
`run-aloha-ass1-001` (`sg-redirect-5`) redirected event 0 to
`local/builds/gc-aloha-003`, the imported Aloha Ice Jam course, which presents
its content under `ASS1` (group 48, track 11) rather than Garibaldi's `ARA1`.
Setting `code = ASS1`, `location = 5` and `mode = 3` — with the archive name left
at `BAM`, because that build ships as `bam.big` — **rode the Aloha terrain**: 6
screenshots under `local/native/profiles/sg-redirect-5/ScreenShots/`, the
briefing reading "Peak 1-Aloha Ice Jam" and the ride showing Aloha's untextured
geometry and its props, scoring tricks. This is the first ride of the converted
course; `docs/aloha-conversion.md` §7 lists it as blocked.

Both consumers matter: `0x80106574` builds the archive path from the event
record, while `0x80108AEC` and `0x801085B0` reach the location's SDB records and
its script container through the topology row's location id. Changing one
without the other loads the archive but looks up the wrong location.

**`name` reaches the frontend; `short` and `mode` do not obviously.**
`run-name-only-001` (`sg-redirect-3`) is the control: only `name` and `short`
patched, everything else stock. It rode stock Snow Jam, proving the hook is
inert for the rest of the boot. The briefing screen shows the patched `name`
("Aloha Ice Jam" in `sg-redirect-5`). The course picture, the vertical drop and
the course length on that screen stayed Snow Jam's — they are not in these
tables.

## Still unknown

- **`mode` did not switch the HUD.** With `mode = 3` (slopestyle) the ride's HUD
  still showed a race — "1st/6" and a lap timer — and the briefing header still
  read "Single Event - Race". The consumer at `0x801093D0` takes the event's own
  word only when its caller passes 7, and the Single Event menu path evidently
  passes the discipline the player picked. So the mode word is real but the menu
  overrides it on this path; what still reads it is untraced.
- **Scoring and the end of a run** are unproven for a redirected event, as in
  `docs/aloha-conversion.md`. The Aloha ride scored tricks but was not taken to a
  finish.
- **Save records.** Nothing here establishes how `rwrdngc.dat` keys medals and
  best times. A redirected event 0 will write Snow Jam's slot with another
  course's result; treat existing saves as at risk.
- **Description text.** `cmnamer.loc`'s LOCT hash function is still unsolved
  (`local/research/course-selection.md` §3), so the briefing description stays
  the stock event's.
- **`courspic`/`mapgfx`/`behiloc`** are keyed elsewhere and are not redirected:
  the course picture and the medal targets remain the host event's.
- **In-game listing.** One event row means the list of imported courses lives in
  the host manifest, not in the game's menu.
