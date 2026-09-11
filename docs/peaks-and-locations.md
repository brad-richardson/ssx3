# Peaks, locations and the level selector in SSX 3

Date: 2026-09-10. Answers "could all of Tricky's courses live on one SSX 3
mountain, and how is the level selector wired?" from a survey of the NTSC-U
executable and disc files. Probing was done by reading the ISO by offset with
the file table in `local/reports/ssx3-disc.json`; nothing on the share changed.

## Findings

1. The level selector's names are not in the `.LOC` string tables. They are in
   two plain tables inside `SLUS_207.72`: an **event table** and a
   **location table**. Renaming or repointing a course is an executable edit
   of fixed-size records, no UI file work.
2. The event table (file offset `0x33e940`, 24 records of 100 bytes) lists the
   17 events, the 5 stations, and a debug track. Each record is five u32
   words, then display name (32 bytes), short name (16), SDB location code
   (16), world archive name (16, always `BAM`).
3. The location table (file offset `0x33f24c`, 24-byte records: u32 kind, u32
   index, code[16]) lists all 49 SDB locations in SDB order plus `dbg`. The
   count and order match `bam.sdb` exactly, so the SDB is keyed by code.
4. Every event's terrain is one SDB location. Green Base Station is the event
   whose code is `A`; runs are `ARA1`..`EBC3`. Connectors (`A_ARA1`) and
   skies (`ASKY`) are locations without events.
5. Per-location audio sessions are named in the same executable
   (`ses_ARA1`, `ses_HUB_A`, records 44 bytes apart from `0x341774`).
6. `DATA/SCRIPTS/SCDAT.BIG` holds 214 members: `scmaster.dat`, a debug copy,
   and numbered scripts `00000000.big` onwards, not keyed by location name.
   Event scripting (start, finish, medals) most likely lives there.
7. `MUSIC.INF` is a text file mapping songs to pathfinder data, not locations.
8. `.LOC` files contain `LOCH`/`LOCT`/`LOCL` tables with UTF-16LE strings.
   Snow Jam's transport description is `CMNAMER.LOC` entry 549. It can be
   replaced within its existing slot; see [locale tables](locale-tables.md).
9. Adding 1,439 Garibaldi patches (633 KB decoded) to the hub's terrain
   group loads and rides (scale-002). This is a tested lower bound, not proof
   that a full race replacement fits: run-gari-001 stalls after loading the
   complete 3,885-patch replacement. See [the full-course experiments](full-course-experiment.md).
10. Recommendation: a "Tricky mountain" is best built by **replacing the 17
    existing events** (names, terrain, and later scripts) rather than adding a
    sixth peak. Tricky has 10 courses; SSX 3 has 5 race, 3 slopestyle, 3 big
    air, 3 halfpipe and 3 backcountry slots.

## The event table

| # | Display name | Short | Code | Words 0–3 |
| --- | --- | --- | --- | --- |
| 0 | Snow Jam | Snow Jam | ARA1 | 0 0 0 0 |
| 1 | Metro-City | Metro | BRA2 | 0 0 0 0 |
| 2 | Ruthless Ridge | Ridge | CRA3 | 0 0 1 0 |
| 3 | Intimidator | Intimid | DRA4 | 1 0 2 1 |
| 4 | Gravitude | Gravitude | ERA5 | 1 0 3 2 |
| 5 | R&B | R&B | ASS1 | 2 0 4 2 |
| 6 | Style Mile | Style | DSS2 | 0 0 6 0 |
| 7 | Kick Doubt | Kick | ESS3 | 1 0 7 1 |
| 8 | Crow's Nest | Crow | ABA1 | 2 0 8 2 |
| 9 | Launch Time | Launch | CBA2 | 0 0 9 0 |
| 10 | Much-2-Much | Much | EBA3 | 1 0 10 1 |
| 11 | The Junction | Disfunk | BHP1 | 2 0 11 2 |
| 12 | Schizophrenia | Schizo | CHP2 | 0 0 12 0 |
| 13 | Perpendiculous | Perpend | EHP3 | 1 0 13 1 |
| 14 | Happiness | Happiness | ABC1 | 2 0 14 2 |
| 15 | Ruthless | Ruthless | DBC2 | 0 0 15 0 |
| 16 | The Throne | Throne | EBC3 | 1 0 16 1 |
| 17 | Green Base Station | Green Station | A | 2 0 17 2 |
| 18 | Blue Base Station | Blue Station | B | 0 1 18 0 |
| 19 | Yellow Mid Station | Yellow Station | C | 0 1 19 0 |
| 20 | Red Mid Station | Red Station | D | 1 1 20 1 |
| 21 | Black Top Station | Black Station | E | 1 1 21 1 |
| 22 | Debug Track | DEBUG | dbg (archive DBG) | 2 1 22 2 |

Word 4 is the record index. Word 1 is 1 for stations. Words 0, 2 and 3 are
not yet understood (word 2 looks like an ordering; words 0 and 3 cycle
through 0, 1, 2). The strings are NUL-padded; the transport menu shows the
display name, and the short name appears in HUD/results text.

The location table follows at `0x33f24c`: kind 0 for the 17 runs and hub A,
1 for hubs B–E, 2 for the 21 connectors and `TRANSP`, 3 for `ASKY`, 4 for the
other skies and `dbg`. Index equals SDB order. A `World Circuit` string sits
right after it.

## What "one mountain with all Tricky courses" would take

Two routes, in order of cost.

### Replace events (recommended)

- Terrain: convert a Tricky course into the run location's groups (the M4
  pipeline generalised: rotate and translate the whole course so its start
  sits at the run's start, keep the location's other resource kinds).
- Names: overwrite the display and short names in the event table. Two
  strings per event, at most 31 and 15 characters. The SDB code stays.
  Done: `tools/patch_executable.py`, verified in name-001 (the menu shows
  "Garibaldi"). The event description is also decoded and changed through
  `CMNAMER.LOC` entry 549; see [locale tables](locale-tables.md).
- Scripts, start, finish, AI paths, textures, props: still the M5 list; the
  event keeps its script and mode (race, slopestyle, ...), so a race slot
  should receive a race course.
- The transport map and course pictures (`DATA/UI/COURSPIC.BIG`,
  `MAPGFX.BIG`) would still show the old artwork until replaced; cosmetic.

Nothing in this route needs new table entries, new SDB locations, or changes
to the front end, so it is the path to a "level selector" with Tricky names.

### Add a sixth peak (not recommended yet)

Would need: new SDB location records (and the spatial/streaming records that
link hubs, connectors and runs), new entries in both executable tables and any
code that sizes them (the location table has exactly 50 entries in place),
transport-menu entries in `FE.LUI`, map artwork, sessions and scripts. The
tables are fixed-size arrays in the executable's data segment, so growing
them means relocating them and patching every reference. Not blocked in
principle, but it is code patching, which is a different project from data
conversion. Revisit only after replacement is working.

## Scaling evidence (scale-001, scale-002)

Same pipeline as gari-003 with wider Garibaldi corridors, appended to hub A's
group 2 and ridden on the Green Station line.

| Build | Patches | Group 2 blocks | Loaded and rode | Notes |
| --- | ---: | ---: | --- | --- |
| gari-003 | 92 | 24 | yes | M4 gate |
| scale-001 | 658 | 29 | yes | reached both waypoints, 59 fps |
| scale-002 | 1,439 | 35 | yes | rider trapped in imported bowl geometry near x −73,500; no reset |

Decoded group 2 grows from 1.34 MB to 1.97 MB at 1,439 patches. The first
scale-001 boot timed out while another image was being written to the share
at the same time; the retry booted normally, so keep the share idle while
booting.
