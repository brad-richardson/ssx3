# SSX Tricky course inventory (for "a whole Tricky peak" in SSX 3)

Date: 2026-09-10. Research only; nothing was launched or modified. Source:
`SSX Tricky (USA).iso` (SLUS_203.26), the twelve `DATA/MODELS/*.BIG` archives.
Reproduce with `tools/inventory_tricky.py <iso> --report <json> --world
local/reports/ssx3-world.json` (about 1 minute; reads only the archives).
Numbers below come from that report. Record layouts follow
GlitcherOG/SSX-Library `PBDHandler.cs`; field names for the patch tail are its
labels, unverified in play.

## Findings

1. Ten of the twelve archives are courses; `TRICK.BIG` is a small 351-patch
   practice hill and `SSXFE.BIG` is the front-end (menu) scene with 62 cameras.
2. Every course archive has the same eleven members: 3 `.ssh` texture packs,
   2 `.pbd` (world + sky), `.ltg`, `.map`, `.ssf`, `.aip`, `.sop`, `.adl`.
3. Courses hold 730–4,268 patches (28,484 total); SSX 3's whole mountain has
   30,644. Four courses exceed the largest SSX 3 location (ABC1, 3,041 patches).
4. In terrain-record bytes a single course is 0.3–1.8 MB (as 432-byte records);
   each fits inside a 9-group race location's 10–12.6 MB decoded budget, but
   whether the engine caps *patch count* per location is still unknown (M2).
5. All ten courses combined (12.3 MB of 432-byte records) equal the entire
   decoded stream of the largest SSX 3 location; they cannot share one location.
6. Textures dominate: `.ssh` is 28–56% of each decoded archive (2.2–5.2 MB);
   `.pbd` is 25–46%, of which the patch array is 35–48%.
7. Patch lightmap ids match the `*_L.ssh` entry count exactly in all 12 files,
   so `_L.ssh` holds lightmap pages; `.ltg` is the instance spatial grid.
8. Patches reference 1–60 distinct textures per course through a material table
   (13–117 materials used); the main `.ssh` has 28–199 shapes (rest is props).
9. Surface-type ids: 18 distinct values across courses, 5–11 per course; the
   constant tail words are identical on every patch on the disc.
10. Drops are 31–298 k units over 175–588 k units of estimated path; median
    centre slope is 25–50 degrees, with 15–39% of patches steeper than 60.

## The twelve archives

Course names and modes are from the game's menus as remembered, not decoded
from disc data. The `.aip`/`.sop` pair share a header (magic `0A0A0A0A`, same
first six words) and are almost certainly the race and showoff AI path sets;
in PIPE and TRICK the two members have identical decoded sizes, consistent
with a placeholder race path where no race exists.

| Archive | Course | Modes (recalled) | Stored MB | Decoded MB | Members |
|---|---|---|---:|---:|---:|
| GARI | Garibaldi | race, showoff | 4.38 | 10.30 | 11 |
| SNOW | Snowdream | race, showoff | 3.91 | 8.30 | 11 |
| ELYSIUM | Elysium Alps | race, showoff | 5.03 | 10.75 | 11 |
| MESA | Mesablanca | race, showoff | 4.46 | 9.60 | 11 |
| MERQUER | Merqury City Meltdown | race, showoff | 5.00 | 11.13 | 11 |
| MEGAPLE | Tokyo Megaplex | showoff only | 2.87 | 5.59 | 11 |
| ALOHA | Aloha Ice Jam | race, showoff | 4.94 | 9.20 | 11 |
| ALASKA | Alaska | race, showoff | 5.50 | 9.32 | 11 |
| PIPE | Pipedream | showoff only | 2.51 | 5.13 | 11 |
| UNTRACK | Untracked | race only | 3.29 | 6.44 | 11 |
| TRICK | practice / tutorial hill | not a circuit course | 1.04 | 2.17 | 11 |
| SSXFE | front end (menus, lodge) | not a course | 3.62 | 5.91 | 7 |

All members are RefPack (10FB) compressed; every member decoded with no
trailing bytes. Course totals: 47.0 MB stored, 85.8 MB decoded.

### Member types

| Extension | Count per course | What it is (evidence) |
|---|---|---|
| `.ssh` | 3 (`name`, `name_L`, `name_sky`) | SHPS texture packs; entry counts 28–199 / 2–17 / 25. `_L` entry count equals the patches' distinct lightmap ids in all 12 files |
| `.pbd` | 2 (`name`, `name_sky`) | world: patches, instances, models, materials, lights, splines, particles; the sky PBD is 15,456 bytes everywhere |
| `.ltg` | 1 | instance lookup grid (SSX-Library `LTGHandler`: 10,000-unit main boxes, 4x4 node boxes), 93 KB–721 KB |
| `.map` | 1 | plain-text build manifest from the ColdFusion/TGroup tool (model and spline names), 129 KB–1.36 MB; not needed at runtime is a guess |
| `.ssf` | 1 | effects, physics, collision models, functions, object properties (SSX-Library `SSFHandler`), 46 KB–1.02 MB |
| `.aip` / `.sop` | 1 + 1 | AI paths (race / showoff); layout differs from the original-SSX `AIPHandler` and is not decoded here; 2.5–98 KB |
| `.adl` | 1 | unknown binary, 3–35 KB |
| `.ser` | SSXFE only | front-end serialized data, 560 KB |

### Decoded bytes by member type (MB)

| Archive | `.ssh` entries main/L/sky | `.ssh` | `.pbd` | other (`ltg map ssf aip sop adl`) |
|---|---|---:|---:|---:|
| GARI | 121/16/25 | 3.81 (37%) | 4.11 | 2.37 |
| SNOW | 133/7/25 | 2.89 (35%) | 3.42 | 1.99 |
| ELYSIUM | 108/17/25 | 3.53 (33%) | 4.56 | 2.66 |
| MESA | 129/10/25 | 3.29 (34%) | 3.91 | 2.40 |
| MERQUER | 199/11/25 | 3.13 (28%) | 5.13 | 2.87 |
| MEGAPLE | 120/3/25 | 3.07 (55%) | 1.65 | 0.87 |
| ALOHA | 178/12/25 | 3.74 (41%) | 3.74 | 1.72 |
| ALASKA | 194/14/25 | 5.21 (56%) | 2.75 | 1.36 |
| PIPE | 73/10/25 | 2.16 (42%) | 2.32 | 0.65 |
| UNTRACK | 33/17/25 | 2.59 (40%) | 2.63 | 1.22 |
| TRICK | 28/2/25 | 1.48 (68%) | 0.39 | 0.30 |
| SSXFE | 131/3 | 4.34 (73%) | 0.80 | 0.77 |

## Terrain (main `.pbd`)

Layout as in `docs/investigation.md`: 144-byte header, 448-byte patch records
at the patch offset, coefficients at +80, bounds at +336/+348, corners at +360.
Tail (SSX-Library labels): +424 u32 surface type, +428 i16, +430 i16
"visibility" (0 or -32768), +432 i16 material index, +434 i16 lightmap id,
+436/+440/+444 u32. The material index selects a 72-byte record in the PBD
material table whose first i16 is the `.ssh` texture index.

Units: ku = thousands of game units; Z is up (top of every course is at max Z,
the AI path start point sits at max Z). Drop = Z extent of patch bounds.
Spine = polyline through the mean position of 60 equal-count elevation slices,
a path-length *estimate* that undercounts meanders and is not meaningful for
the halfpipe-like MEGAPLE/PIPE or the non-descending TRICK/SSXFE (shown as -).
Chord = straight line from top slice to bottom slice. Slope = angle of the
patch-centre normal from vertical: area-weighted mean / median, and the share
of patches under 30, 30–60, over 60 degrees (walls and props are included).

| Course | Patches | Extent X x Y (ku) | Drop | Spine | Chord | Slope aw/med | <30 / 30–60 / >60 % | Surf | Tex | Mat | LM | Hidden |
|---|---:|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| GARI | 3,885 | 225 x 297 | 274 | 487 | 423 | 50 / 47 | 23 / 44 / 33 | 9 | 19 | 52 | 16 | 60 |
| SNOW | 1,653 | 160 x 156 | 136 | 351 | 181 | 34 / 30 | 50 / 34 / 16 | 10 | 23 | 56 | 7 | 138 |
| ELYSIUM | 4,268 | 205 x 212 | 254 | 540 | 315 | 44 / 44 | 31 / 36 / 32 | 9 | 26 | 31 | 17 | 64 |
| MESA | 2,448 | 113 x 143 | 155 | 362 | 190 | 45 / 42 | 33 / 35 / 32 | 11 | 34 | 37 | 10 | 4 |
| MERQUER | 2,731 | 179 x 312 | 250 | 536 | 377 | 31 / 35 | 42 / 38 / 21 | 9 | 32 | 32 | 11 | 4 |
| MEGAPLE | 730 | 53 x 52 | 52 | - | 51 | 28 / 25 | 62 / 20 / 18 | 5 | 35 | 40 | 3 | 0 |
| ALOHA | 2,871 | 83 x 96 | 118 | 257 | 126 | 49 / 48 | 25 / 40 / 35 | 10 | 60 | 81 | 12 | 8 |
| ALASKA | 3,449 | 339 x 170 | 260 | 588 | 382 | 56 / 49 | 23 / 38 / 39 | 9 | 46 | 117 | 14 | 4 |
| PIPE | 2,332 | 28 x 106 | 31 | - | 101 | 33 / 28 | 52 / 15 / 33 | 5 | 29 | 45 | 10 | 0 |
| UNTRACK | 4,117 | 268 x 110 | 298 | 501 | 368 | 54 / 50 | 19 / 48 / 33 | 8 | 10 | 25 | 17 | 0 |
| TRICK | 351 | 80 x 67 | 45 | - | 73 | 39 / 35 | 39 / 46 / 15 | 5 | 1 | 13 | 2 | 0 |
| SSXFE | 546 | 27 x 95 | 19 | - | 15 | 54 / 61 | 26 / 23 / 51 | 1 | 1 | 42 | 3 | 0 |

Surf = distinct surface-type ids; Tex = distinct `.ssh` texture indices
reached through the material table; Mat = distinct material indices used by
patches; LM = distinct lightmap ids; Hidden = patches with the visibility
i16 set to -32768 (hypothesis: rendered invisible but still collidable).

Surface ids seen: 0–13, 16–19. The most common everywhere are 1, 3 and 5;
UNTRACK is 66% id 3, PIPE is 51% id 1, ALASKA/ALOHA are 47%/45% id 5. Ids 2,
6–8, 11–13, 16, 19 are rare (under 3% of all patches) and course-specific.
Meanings are unknown; SSX 3's material word (offset 8) has different values,
so a surface mapping table is needed before import (roadmap M3/M5).

Tail words are the same on every patch of all 12 files: +428 = 41,
+436 = 0xFFFFFFFF, +440 = 1,235,316, +444 = 4,311,690. Constants across the
whole disc are not per-course data; they look like the runtime pointer or
handle placeholders SSX 3 also carries (its constant word at 428).

### Other PBD content per course

| Course | Instances | Models | Materials | Lights | Splines / segments | Flipbooks | Particle inst / models |
|---|---:|---:|---:|---:|---|---:|---|
| GARI | 3,393 | 648 | 125 | 942 | 169 / 542 | 16 | 10 / 10 |
| SNOW | 3,230 | 1,466 | 109 | 421 | 293 / 1,088 | 10 | 0 / 0 |
| ELYSIUM | 3,933 | 819 | 114 | 218 | 296 / 442 | 16 | 59 / 19 |
| MESA | 3,079 | 1,055 | 129 | 379 | 100 / 481 | 12 | 0 / 0 |
| MERQUER | 4,445 | 1,480 | 218 | 934 | 169 / 980 | 9 | 9 / 9 |
| MEGAPLE | 1,294 | 509 | 108 | 222 | 102 / 341 | 5 | 0 / 0 |
| ALOHA | 1,997 | 687 | 171 | 413 | 133 / 454 | 14 | 11 / 11 |
| ALASKA | 1,477 | 216 | 106 | 267 | 84 / 213 | 8 | 27 / 17 |
| PIPE | 576 | 178 | 36 | 152 | 108 / 571 | 1 | 0 / 0 |
| UNTRACK | 1,134 | 130 | 15 | 78 | 77 / 364 | 0 | 4 / 4 |
| TRICK | 570 | 28 | 14 | 44 | 9 / 12 | 2 | 0 / 0 |
| SSXFE | 337 | 109 | 65 | 14 | 0 / 0 | 25 | 59 / 26 (62 cameras) |

Player-start count is 0 in every file (starts live elsewhere, probably the
`.aip`/`.sop` path header, whose first point is at the top of the course).
Splines are the rail/grind and camera curves; segments carry distances, so a
decoded spline set could later give a better path length than the spine.

## SSX 3 budget comparison

From `local/reports/ssx3-world.json`: a location's groups are
`group_start..last_group`; decoded bytes are the sum of the groups' decoded
sizes and patches are kind-1 resources (432 bytes each). The whole SSX 3
world is 162.0 MB decoded with 30,644 patches (13.2 MB of patch records).

| SSX 3 location | Groups | Decoded MB | Patches | Patch MB | Patch share |
|---|---:|---:|---:|---:|---:|
| CRA3 (largest bytes) | 9 | 12.57 | 2,272 | 0.98 | 8% |
| DRA4 | 9 | 11.88 | 2,183 | 0.94 | 8% |
| ARA1 | 9 | 10.98 | 1,913 | 0.83 | 8% |
| ABC1 (most patches) | 9 | 10.34 | 3,041 | 1.31 | 13% |
| ERA5 | 9 | 10.33 | 1,739 | 0.75 | 7% |
| ASS1 | 5 | 9.11 | 1,829 | 0.79 | 9% |
| ESS3 | 7 | 8.82 | 1,270 | 0.55 | 6% |
| BRA2 | 7 | 8.79 | 1,787 | 0.77 | 9% |
| DSS2 | 7 | 8.72 | 1,680 | 0.73 | 8% |
| EBC3 | 5 | 8.55 | 2,504 | 1.08 | 13% |
| DBC2 | 5 | 8.45 | 2,123 | 0.92 | 11% |
| hubs A–E | 2 | 1.67–2.11 | 186–308 | 0.08–0.13 | 6% |
| connectors (`X_XYZn`) | 2 | 0.72–1.36 | 132–323 | 0.06–0.14 | 8% |

Tricky courses expressed as SSX 3 432-byte records:

| Course | Patches | As 432-byte records MB | vs ABC1 patches | vs ERA5 patches |
|---|---:|---:|---:|---:|
| ELYSIUM | 4,268 | 1.84 | 140% | 245% |
| UNTRACK | 4,117 | 1.78 | 135% | 237% |
| GARI | 3,885 | 1.68 | 128% | 223% |
| ALASKA | 3,449 | 1.49 | 113% | 198% |
| ALOHA | 2,871 | 1.24 | 94% | 165% |
| MERQUER | 2,731 | 1.18 | 90% | 157% |
| MESA | 2,448 | 1.06 | 80% | 141% |
| PIPE | 2,332 | 1.01 | 77% | 134% |
| SNOW | 1,653 | 0.71 | 54% | 95% |
| MEGAPLE | 730 | 0.32 | 24% | 42% |
| all ten | 28,484 | 12.31 | 937% | 1,638% |

Reading this:

- **Bytes:** every single course's terrain records (at most 1.84 MB) fit in
  the decoded budget of any 9-group race location (10.3–12.6 MB) with room for
  everything else; patch records are only 7–13% of an SSX 3 location today,
  so a course's patches would be a 15–18% share at most.
- **Patch count:** ELYSIUM, UNTRACK, GARI and ALASKA carry more patches than
  any SSX 3 location. Whether that matters depends on an untested per-location
  patch or memory cap (roadmap M2 step 4: "add hundreds, then thousands").
  Roadmap M5 (all 3,885 Garibaldi patches into a run) is exactly this test.
- **All courses in one location:** no. 12.3 MB of terrain records alone equals
  CRA3's entire decoded stream, and 28,484 patches are 93% of the whole
  mountain. A Tricky peak means one location per course (ten locations, or
  eight if the showoff-only MEGAPLE and PIPE are treated as showoff runs).
- **What else dominates:** textures. Per course the `.ssh` packs decode to
  2.2–5.2 MB, and the non-terrain remainder of the PBD (instances, 130–1,480
  models, lights, splines) plus `.ssf` collision adds 1.6–5.0 MB. A course's
  full decoded content (5.1–11.1 MB) is the same size class as one SSX 3 race
  location, so a one-for-one replacement is plausible in size if Tricky
  textures convert at similar byte cost; the ten courses together (85.8 MB)
  would add about half of SSX 3's current world stream, which is a disc and
  streaming matter rather than a runtime one.

## Hashes

SHA-256 of each archive (as stored on disc) and its decoded main `.pbd`.

| Archive | Archive SHA-256 (first 16) | Main PBD | PBD SHA-256 (first 16) | PBD bytes |
|---|---|---|---|---:|
| GARI | 676276e83e145192 | gari.pbd | 5f12ec2edb5f0807 | 4,098,656 |
| SNOW | 6fdc21c54a2a504c | snow.pbd | af279f4ce1f7f4b0 | 3,401,936 |
| ELYSIUM | 58d409a183da52c0 | elysium.pbd | 34d7dcbcf28fb2ff | 4,547,296 |
| MESA | d9079f318c48a868 | mesa.pbd | ef8fef0e4e9e2b2f | 3,893,856 |
| MERQUER | 030dac60276e0a23 | merquer.pbd | e1f178d35a1ccc32 | 5,110,992 |
| MEGAPLE | 3cd86ccfe1c6206f | megaple.pbd | dd0127196090f9d7 | 1,632,928 |
| ALOHA | 7fe1ab081f72c76a | aloha.pbd | fde13eaa086fe346 | 3,723,248 |
| ALASKA | cd0efbae10509802 | alaska.pbd | 3490f6898bc1666a | 2,736,080 |
| PIPE | 54159365c854ee74 | pipe.pbd | aaa9779e7ecd06c8 | 2,300,736 |
| UNTRACK | 83eee144d3d9127f | untrack.pbd | 0fe3cd78b116ebf6 | 2,619,184 |
| TRICK | d500991dfff124f8 | trick.pbd | 9df3af81e0a3bd45 | 374,512 |
| SSXFE | 71bd561081b08e8f | ssxfe.pbd | a0f51caf08f65d38 | 800,176 |

GARI values match `local/reports/garibaldi.json`. Full hashes are in the
tool's JSON report.

## Open items this inventory raises

- Decode the Tricky `.aip`/`.sop` path format (start point, then what look
  like per-node records) for real race-line lengths and start positions.
- Surface-type id meanings (18 ids) and a mapping to SSX 3 material words.
- Confirm `_L.ssh` = lightmap pages by viewing one, and the `.ltg` grid's role
  in culling before deciding what SSX 3 structure (spatial records) replaces it.
- Per-location patch-count limit in SSX 3 (M2 step 4), which decides whether
  the four 3,400–4,300-patch courses need splitting across locations.
