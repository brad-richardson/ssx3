# Anatomy of an SSX 3 location

Date: 2026-09-10. Research only: what a run location holds besides terrain, so
that "replace ERA5's terrain with Garibaldi" can be planned. Evidence comes from
the unchanged `BAM.BIG` (SHA-256 in [investigation.md](investigation.md)) read
with `tools/location_inventory.py`; nothing was run in an emulator. Kind names
are SSX-Library's labels (see its `SSBHandler.cs`); "verified" below means
verified against the disc bytes, not in play.

## Findings

1. A location's groups are `N-1` **texture groups** (kinds 9/10 only, track 255) plus one final **main group** holding everything else (track = location index). ERA5: groups 140-147 are textures (~730-780 KB decoded each), group 148 is the run (4.37 MB, 6,175 resources).
2. The 96-byte SDB spatial records are a **binary tree of axis-aligned boxes over the texture groups**: leaves name one texture group, inner nodes hold two child indices and three split planes. Verified for all 49 locations. Textures stream by region; the main group is one unit.
3. Every patch binds its region and images directly: word 340 = `texture_group << 16 | track << 8`, word 416 = `lightmap RID << 16 | texture RID`; all 1,739 ERA5 patches name RIDs present in the group they point at. Instances carry the same region word at offset 124.
4. Collision (kind 12, 200 in ERA5) is **prop collision**, named `<model>_CollideModel_{ProgMesh,ConvexHull,SphereTree}`; terrain has none (consistent with bump-002). Reset volumes, start/finish planes, gates and collectibles are all model **instances** (kind 3).
5. Kind 14 RID 0 (AIP, 66.8 KB in ERA5) holds 88 AI lines, 9 track-path segments (the course centreline, distance-to-go 355,192 units) and 14 spawn records: 6 start-grid slots at the top of the run and 8 respawn points down the course. Hub A's 3 spawn records sit within 600 units of the ridden Green Station spawn.
6. Kind 21 (only in the 11 runs) is the 2D course polyline for the radar/progress bar (353 × 20 bytes: distance, direction, x, y). Kinds 13 and 16 are per-instance tables (their words decode to ERA5 instance IDs); kind 17 is camera boxes; kind 18 lists 14 cutscene anchor instances; kind 22 is the ERA5 avalanche animation (empty in 42 locations).
7. PHM/PSM name exactly kinds 1, 3, 2, 8, 12 (all entries named; one entry per resource, order-matched between the two files). Kinds 0, 4-7, 9-11, 13-22 have no names.
8. Replacing ERA5's terrain therefore needs, besides patches: texture groups + spatial tree (or reuse), AIP (spawns, track path, AI lines), radar, and a decision for the 2,803 instances, 757 models, 200 collisions, 241 lights, 131 halos, 138 rail splines, 12 vis curtains, camera boxes and the instance tables that all sit in ERA5's coordinates.
9. Nothing outside the location's own groups was found to reference its RIDs, except the world-wide PHM/PSM tables and whatever the executable does with location names.
10. Unknown: kind 15/16/13 internals, per-location memory budget, how collision records bind to models (not by RID, not by PHM hash), and how the engine picks a spawn set.

## Method

```sh
python3 tools/location_inventory.py ARCHIVE --cache DIR locations
python3 tools/location_inventory.py ARCHIVE --cache DIR inventory ERA5 A A_ARA1
python3 tools/location_inventory.py ARCHIVE --cache DIR spatial ERA5
python3 tools/location_inventory.py ARCHIVE --cache DIR kinds [--location ERA5]
python3 tools/location_inventory.py ARCHIVE --cache DIR names --location ERA5
```

The first run decodes all 159 groups into `DIR/group_NNN.bin` (17 s); later
runs read the cache. The scratch probes that produced the numbers below are not
kept; every claim can be re-derived from the cache with a few lines of `struct`.

## Groups, tracks and the spatial tree

| Location | Groups | Texture groups (kinds 9+10, decoded bytes) | Main group | Spatial records |
| --- | --- | --- | --- | --- |
| ERA5 (Peak 3 race) | 140-148 | 140-147: 74+7, 50+6, 64+3, 59+6, 65+2, 61+3, 48+5, 60+3 records; 726-781 KB each | 148: 6,175 records, 4,365,701 B (67 blocks) | 155-169 (15) |
| A (Peak 1 hub) | 1-2 | 1: 62+4 records, 769,280 B | 2: 1,209 records, 1,338,393 B (23 blocks) | 1 (1) |
| A_ARA1 (connector) | 5-6 | 5: 34+3 records, 338,072 B | 6: 530 records, 524,633 B (9 blocks) | 3 (1) |

- Resource header track byte: 255 in texture groups, otherwise the location's
  index in the SDB table (ERA5 = 45, A = 1, A_ARA1 = 3). RIDs restart at 0 per
  location and per kind.
- The SDB group `memsize` word equals the decoded bytes of kinds 0-12 with
  headers; for texture groups that is the whole group. The location record's
  per-kind counts omit kinds 9 and 10 (they are only in group records).
- Spatial-record count is `2 × (groups − 1) − 1`, i.e. a full binary tree with
  one leaf per texture group. Single-group `?SKY` locations have one leaf with
  group −1.

96-byte spatial record (verified on all 183):

| Offset | Content |
| ---: | --- |
| 0-15 | box min (x, y, z, 1.0) |
| 16-31 | box max (x, y, z, 1.0) |
| 32-79 | inner node: three planes (normal, d): +axis at left child's max, −axis at right child's min, +axis at a value between them; leaf: zeros |
| 80, 84 | inner node: left and right child record index; leaf: −1, −1 |
| 88 | leaf: texture group index; inner node: −1 |
| 92 | 0 |

Inner boxes are the union of their children (all 49 locations). ERA5's root box
is x −378k..−168k, y 16k..137k, z 245k..496k; all 1,739 patch boxes lie inside
it, and each patch centre lies in one or two leaf boxes (overlaps of ~10%).
Hub A's single box is x −106k..−62k, y 28k..58k, z −221k..−210k, which matches
the ridden hub. The tree keys **texture streaming**; it says nothing about
which patches load.

Textures are duplicated across regions so each region is self-contained: ERA5
has 516 texture records but 179 unique (kind, RID) pairs; 3.08 MB of the 6.0 MB
of ERA5 texture data is duplication. Texture headers: format byte 1/2/5
(4-bit, 8-bit palettised, 32-bit), 16×16 to 128×128; lightmaps (kind 10) are
mostly 128×128 32-bit (65,664 B).

## Kinds present in a run (ERA5 unless noted)

| Kind | Label | ERA5 count / bytes | Record | Positional? | What is known |
| ---: | --- | --- | --- | --- | --- |
| 0 | material | 128 / 3.6 KB | 20 B (rarely 32/44) | no | ten i16; first is a kind-9 texture RID (128/128 valid); referenced by models |
| 1 | patch | 1,739 / 765 KB | 432 B | yes | terrain; see investigation.md; words 340/416 bind region and images |
| 2 | model | 757 / 1.34 MB | 416 B-74 KB | no (local space) | MDR: own id at 0 (matches header 757/757), material list of kind-0 ids (all valid), meshes; word 12 always 40, word 16 in {0,1,2,3,8} |
| 3 | instance | 2,803 / 1.42 MB | 256 B-12 KB | yes | 4×0, 4×4 matrix at 16 (position = row 3, all inside the root box), own id at 120, model id at 128 (all valid, same track), region word at 124, optional VIF vertex-colour tail |
| 4 | particle model | 7 / 2.4 KB | 336-896 B | no | unexamined |
| 5 | particle instance | 7 / 1.1 KB | 144 B | yes | matrix, bounding sphere at 80, AABB at 104/116 |
| 6 | light | 241 / 29 KB | 112 B | yes | position at 56 (239/241 inside root box); rest unexamined |
| 7 | halo | 131 / 11.5 KB | 80 B | yes | position at 28 (131/131 inside) |
| 8 | spline | 138 / 126 KB | 48 + 144·n | yes | rails and animation paths; box at 4/16; n segments of 4 control points (138/138 sizes consistent) |
| 9 | texture | 481 / 4.35 MB | 400 B-66 KB | no | SSH images, in texture groups only |
| 10 | lightmap | 35 / 1.61 MB | 4-66 KB | no | SSH images, in texture groups only |
| 11 | vis curtain | 12 / 2.6 KB | 208 B | yes | sphere, four corners, plane, box at 160/172 |
| 12 | collision | 200 / 215 KB | 68 B-18 KB | yes (model space) | prop collision meshes named after models; 185/200 match a model name in ERA5; RIDs unrelated to model RIDs |
| 13 | "sound trigger?" | 1 / 34 KB | 1,379 entries | no | header count 1,379; 1,351 words decode as ERA5 instance ids; padded with 0xCC; a per-instance table |
| 14 | AI paths | 3 / 66.8 KB | see below | yes | RID 0 = main; RIDs 1, 2 are 0 bytes in ERA5 (hub A has all three: 12.3, 5.4, 5.0 KB) |
| 15 | "world painter?" | 1 / 14.9 KB | offset table of 14 | no | header (16, 14, 64) then 14 offsets/−1; no instance ids, no positions |
| 16 | "scripts?" | 1 / 116 KB | opaque | no | header (0x1000, 0x3800, 0, 0.89 ...); 2,576 words decode as instance ids: per-instance behaviour table |
| 17 | camera trigger | 1 / 7.8 KB | 28 B header + entries | yes | counts (56, 57, 1, 1); box centre + extents per entry (stride 84 or 28); absent from 29 locations |
| 18 | NIS table | 1 / 72 B | 14 ids + 16 B | no | cutscene anchors: ERA5 → podium steps, start-gate modules, podium floor, jumbotron; A → gondola helipad, gondola station, `NIS_Transport`, `NIS_Lodge`; unused slots −1 |
| 20 | audio bank | 2 / 187 KB | `BNKl` | no | sound banks; 0 bytes in many locations |
| 21 | radar | 1 / 7.1 KB | 16 B + 353 × 20 B | yes (2D) | (distance, dir x, dir y, x, y) along the course; first entry carries the total length 355,213; runs only |
| 22 | avalanche anim | 1 / 9.9 KB | opaque | yes | contains ERA5 positions; 0 bytes in 42 of 49 locations |
| 19, 23 | — | 0 | — | — | never present on this disc |

Hub A holds the same kinds with 291 patches, 566 instances, 166 models, 77
collisions, 29 splines, 8 lights, no halos/particles, kind 17 of 100 bytes and
an empty kind 22. A_ARA1 (a connector) has no kind 17 or 21.

Instance names are the clearest gameplay inventory. ERA5's 2,803 instances by
base name: `resetvolumes` 286, fences 155+155, pinwheel trees 363, `neontube`
113, `bcmetalgate` 44, `bcvolume` 45, `collecta` 30, `challenge_reset_plane_start`
8 and `_finish` 5, `finish_gate` 1, `startgatedoorbig` 12, `startgatehandles` 7,
flags, searchlights, `treetopatrig`, `dragonTrig`, `crumbleTimer`,
`glacialShift`, `riversplash`, `snowwind`. A_ARA1 has `Load` and `Unload`
models, i.e. streaming triggers are instances too.

## Cross-references (all verified on ERA5)

```text
patch(1) ──340──> texture group          instance(3) ──128──> model(2) ──> material(0) ──> texture(9)
patch(1) ──416──> texture(9) + lightmap(10)   instance(3) ──124──> texture group
collision(12) ──name──> model(2)          kinds 13, 16 ──ids──> instance(3)     kind 18 ──ids──> instance(3)
AIP(14), radar(21), lights(6), halos(7), splines(8), curtains(11), camera(17): absolute coordinates only
```

- No instance word decodes to a collision id, and no model header word reliably
  equals its collision's RID (5 of 94 same-name pairs hit, by chance). Binding
  is by name at build time or by something not in these records.
- PHM entries are 16 bytes: two words unique per name (identical names in
  different locations share them, so probably name hashes), track, RID, and a
  per-location word (43-48 distinct values, one per location, distinct from
  patch word 0). PSM stores the strings in the same order. Array i ↔ kind:
  0→1, 1→3, 2→2, 3→8, 4→12. grown-001 showed new patch RIDs need no entries;
  whether unnamed **collision** or **model** records bind is untested.

## AIP (kind 14, RID 0) layout

Magic `0x69696969`, then:

| Section | ERA5 | Hub A | Record |
| --- | --- | --- | --- |
| AI paths | 88 | 23 | 9 words (`2, 100, 4, id, 101, 4, flag, n, events`), origin, box, n × (unit direction, length), events × (type, value, start, end) |
| track paths | 9 | 6 | 6 words (`1, 0, 4, distance-to-go as float, n, events`), origin, box, points as above |
| u0 | 6 × (0, 0) | 6 × (0, 0) | unknown, constant |
| spawn records | 14 | 3 | (slot, set, position, unit direction, point index, segment) |

Points are deltas: integrating `direction × length` from the origin lands every
point inside the segment box (274/274 in ERA5's first four segments);
SSX-Library's `x × w` does not. Segment 0 starts at (−351,771, 110,078,
490,205), just below the start grid, with distance-to-go 355,192; segments
chain 0 → 4 → 5 → 1 → 2 → 3 to the finish at z ≈ 249,800; segments 6-8 cover
the entry from hub E (z up to 503,570) and the exit into ERA5_C.

Spawn records: set 0 = six start-grid slots 0-5 in a row 120 units apart at
z 490,274 facing (0.62, −0.78, 0); set 1 = eight respawn points ordered down the
course, each with a track-path point index and segment number. Hub A: three
records at (−65,780, 33,350, −212,600) facing (−0.82, 0.40, −0.41); the ridden
Green Station spawn was (−66,300, 33,600, −212,800). AI-path events use types
100, 102, 103, 110, 111, 300 (unknown meaning; likely jump/trick cues).

## Assessment: replacing ERA5's terrain with Garibaldi

| Resource | Needed for a playable race | Notes |
| --- | --- | --- |
| patches (1) | **regenerate** | as gari-003, but full course; word 340 must name a real texture group, 416 real texture/lightmap RIDs |
| texture groups + spatial tree | **regenerate or collapse** | simplest: one region (one texture group, one leaf record) covering the course box, as hubs do; the tree then needs no split planes. Textures can be ERA5's or converted `gari.ssh`; lightmaps need `gari.ltg` work or a flat lightmap |
| AIP (14) | **regenerate** | spawn set 0 (grid), set 1 (respawns), track path (progress, rubber-band, respawn ordering), AI lines (`gari.aip` is the donor); RIDs 1-2 can stay empty |
| radar (21) | **regenerate** | 2D polyline with distances; derive from the new track path |
| instances (3), models (2), collision (12), materials (0) | **decide** | left as-is they float in ERA5's old coordinates: start gate, finish gate and reset volumes will be in the wrong places; fences and trees may intersect the new surface. Options: (a) keep a minimal set (start gate, finish gate, podium/jumbotron for NIS, a few reset planes) re-placed by transform; (b) delete most and shrink kinds 13/16 accordingly (untested) |
| kinds 13, 16 | **unknown, tied to instances** | contain instance ids; keeping instances keeps these valid; deleting instances without editing them is a soft-lock risk |
| NIS table (18) | keep valid | must point at surviving start-gate/podium instances or be −1 |
| lights (6), halos (7) | tolerate | wrong positions only affect looks; regenerate later |
| splines (8) | tolerate / regenerate | rails; Garibaldi rails need new splines and the rail-instance models that go with them |
| vis curtains (11) | probably delete | occlusion planes for the old geometry; keeping them may cull the new terrain |
| camera boxes (17) | tolerate | wrong triggers only affect cinematic cameras; 29 locations have none |
| audio banks (20) | keep | not positional |
| avalanche (22) | empty it | 42 locations have 0 bytes |
| materials (0), particle kinds (4, 5) | keep | small, non-positional |
| PHM/PSM | keep + extend if needed | new patches need no names; new models/collision are untested |

What the engine tolerates is a runtime question this survey cannot answer; the
first test should be the smallest change: new patches plus new AIP spawn/track
records and a new radar, with everything else untouched, ridden from the Peak 3
race start.

## Open questions

- Per-location memory budget: ERA5's main group is 4.37 MB decoded (memsize
  3.92 MB); Garibaldi's 3,885 patches alone are 1.7 MB of records.
- Kind 15 and 16 formats; whether kind 13 must list every instance.
- How collision records attach to models (name hash in the executable?).
- Which spawn set/slot the game uses for race, freeride and the E→ERA5 entry;
  whether `point index` and `segment` in spawn records must match the track path.
- Whether the tree's split planes are consulted (a single-leaf tree avoids them).
- Kind 17 entry stride (84 vs 28) and kind 22 contents.
