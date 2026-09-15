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

## Staging the game directory

`tools/gamecube_game_dir.py` builds the directory the runtime boots. Every stock
entry is a symlink, so a staged course costs only the archives it installs:

```sh
# The imported course in the stock archive's place
python3 tools/gamecube_game_dir.py local/research/aloha/game-aloha-007 \
  --world local/builds/gc-aloha-007

# Or beside it, under its own name, with stock bam.big still present
python3 tools/gamecube_game_dir.py local/research/aloha/game-two-course-001 \
  --world alo=local/builds/gc-aloha-007 --receipt .../receipt.json
```

The second form is what the rule below requires: `--world NAME=PATH` rewrites the
archive's four world member names to `data/worlds/NAME.*` before installing it as
`NAME.big`. The rewrite is directory-only — the 16-byte header, every entry's
offset/size words and the directory trailer are copied, and the rebuilt
directory must still end before the first member — so all 97 MB of member data
keeps its original offsets and a same-length rename is a pure in-place
substitution. A basename that would push the directory into the first member is
refused with the length that archive allows (25 characters for SSX 3's
`bam.big`). Applied to stock `bam.big` with `ala`, the tool reproduces
`local/research/course-redirect/ala.big` — the hand-made archive `run-ala-001`
actually rode — byte for byte, which is the regression `tests/test_gamecube_game_dir.py`
runs when that evidence is present.

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

## The discipline is the menu's, so host on an event of the right discipline

**September 15 (later): the `mode` caveat below is an artifact of hosting on a
race event.** Every manifest written so far redirects **event 0, Snow Jam, a
race** (`course_manifests.py --target-event` defaults to 0), because the
harness's menu sequence walked Single Event's Race branch, whose Peak 1 list is
Snow Jam / Metro-City / Happiness. The Single Event menu passes the discipline
of the event the player picked, so a race host stays a race however the mode
word is patched.

The Freestyle branch is not locked. **Select Peak → Select Mode offers Race and
Freestyle**, and Freestyle's Peak 1 list is **R&B / Crow's Nest / The Junction /
Happiness Jam** — the slopestyle, big-air and halfpipe events. Taking it needs
one D-pad press: `native/diagnostics/course-start-freestyle.json`. Stock R&B
ridden through that path (`fs-stock-2`, 1,192 observed samples) shows the real
slopestyle HUD — score, `OPPONENT +31841`, no lap counter — and its briefing
reads "Single Event - Slopestyle" with the score standings screen and a 340,000
record score.

So a donor course goes into a slot **of its own discipline**: R&B (event 5) for
slopestyle, and no table patch is needed beyond the archive, because event 5
already carries `code = ASS1`, `location = 5` and `mode = 3`.

Two practical notes. The menu sequence is open-loop, so its slots must be
wide: five-second slots drift by enough between runs that the Freestyle press
landed on Select Peak instead and walked the highlight onto a locked peak, at
which point A does nothing and the run sits there. Ten-second slots hold. And
the Freestyle branch inserts a **My Rules** screen between the event list and
the briefing, so the sequence needs one more A than the race path.

## Still unknown

- **What reads the `mode` word.** It is real - the tables carry it and
  `0x801093D0` reads the event's own value when its caller passes 7 - but the
  Single Event path passes the player's pick, so patching it changes nothing
  there. Hosting on a same-discipline event sidesteps the question entirely.
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

## The picker (September 15)

`tools/course_manifests.py` writes one manifest per event straight out of the
DOL's own tables, and the iOS app lists them. `mobile_gamecube.py courses
--courses-dir DIR` copies a directory of manifests to `Documents/Courses`
(parsing each one first, so a malformed manifest never reaches the phone), and
the pause menu gains a **Course** row: a native menu listing "Stock event" plus
every installed manifest by name, with the current choice checked. Choosing one
stores `SSXCourseManifest` and it loads on the next Full Reset or relaunch, like
the other runtime settings.

Resolution order at boot: `-ssxCourseManifest <name>` from the launch arguments
wins (the harness keeps using it), then the stored choice, then the stock event.
Both paths take a bare file name only, so neither a launch flag nor a stored
preference can point outside the sandbox, and a preference naming a manifest
that is no longer installed falls back to stock rather than failing the boot.
The manifest a session actually booted with is recorded as `course_selection`
in its log.

## Two courses resident (September 15)

`ride-006` under `local/research/aloha/` boots a game directory that holds stock
`bam.big` *and* `alo.big` (`local/builds/gc-aloha-007` with its world members
renamed), with `archive = alo` in the manifest. The runtime logged
`event 0 archive at 802ce630: "BAM" -> "alo"` and the ride spawned on Aloha at
`(-113667.5, 72738.8, -228282.9)`, the same coordinates as the single-archive
run — so an added course replaces no stock file, and the stock archive stays
available to every other event. That is the picker's whole data model: an
archive plus a manifest line.

One consequence for evidence: `tools/native_gamecube.py` used to hash
`files/data/worlds/bam.big` as *the* world archive, which in a multi-archive
directory names a file the run never loaded. The receipt now carries
`world_archives_sha256` for every installed `*.big` alongside the old key, and
`gamecube_collision_check.py` accepts a candidate that is any installed archive.
Anything else reading `world_archive_sha256` for identity needs the same
treatment before it is trusted on a two-course directory.
