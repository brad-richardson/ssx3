# Aloha Ice Jam (Showoff) into ASS1 "R&B"

Date: 2026-09-14. The second donor conversion: SSX Tricky's **Aloha Ice Jam**,
its **Showoff** authoring (`aloha.sop`), into SSX 3 GameCube's **ASS1** — event
5, display name "R&B", peak A, discipline word 3 (slopestyle). The candidate is
selected and justified in `local/research/next-course-spike.md` §3.

Phase 1 is *static and rideable*: terrain, art, the slopestyle kind-21 line,
scenery, collision and rails, ridden on the native runtime. Scoring, the run's
end, showoff prop switching and the start gate are phase 2 and are listed under
[Open items](#open-items).

## 1. The Garibaldi template

Everything Aloha does is a re-run of the Garibaldi→ARA1 lineage, so the
existing command sequence is written down here first. It is reconstructed from
`docs/gamecube-world.md`, `docs/gamecube-scenery.md`, `docs/gamecube-rails.md`,
`docs/gamecube-collision.md` and the recorded recipes in
`local/builds/gc-gari-*/experiment.json` (each stage's
`*.base_archive_sha256` names its input build's `output_sha256`, which is what
chains the list below).

The GameCube lineage does **not** use `tools/replace_terrain.py` — that is the
PS2 `run-gari-*` track. Stage 1 is one all-in-one tool; every later stage is an
incremental tool that reads `--base-build`'s `experiment.json` for the location,
group, track and placement matrix, so those never reappear on a command line.

| # | Build | Tool | What it adds |
| ---: | --- | --- | --- |
| 1 | `gc-gari-013` | `gamecube_terrain.py` | terrain patches, textures + lightmaps, reset paths, freeride start, race line and gates, kind-21 table |
| 2 | `gc-gari-020` | `gamecube_scenery_import.py` | donor models and static placements |
| 3 | `gc-gari-021` | `gamecube_spline_import.py` | rails |
| 4 | `gc-gari-022` | *(ad-hoc script)* | hidden-instance removal; no CLI exists |
| 5 | `gc-gari-025` | `gamecube_surface_import.py` | terrain surface types / reset semantics (v2) |
| 6 | `gc-gari-027` | `gamecube_surface_import.py` | grounded reset paths (same tool, later version) |
| 7 | `gc-gari-031` | `gamecube_collision_import.py` | static collision |
| — | *(unnumbered)* | `gamecube_startgate.py` | start gate assets, on top of 031 |

```sh
# 1. terrain + art + paths + race line  (docs/gamecube-world.md:300-309)
python3 tools/gamecube_terrain.py local/source/gamecube/ssx3/BAM.BIG \
  --nbd local/source/gamecube/tricky/gari.nbd --location ARA1 --template-rid 1673 \
  --source-anchor=-1214.8,-195.5,-768.547891 --target-anchor=-118613.68,15753.8,-228880.14 \
  --yaw 73 --scale .55 --drop-kind 3 --drop-kind 12 --clear-instance-references \
  --clear-script-bindings --disable-course-scripts --pin-texture-group 31 \
  --reset-aip local/source/gamecube/tricky/gari.aip --relocate-freeride-start --race-course \
  --textures local/source/gamecube/tricky/gari.gsh \
  --lightmaps local/source/gamecube/tricky/gari_L.gsh --output local/builds/gc-gari-013

# 2. scenery  (docs/gamecube-scenery.md:148-156; defaults --group 36 --texture-group 31 --page 0x0008001f)
python3 tools/gamecube_scenery_import.py --base-build local/builds/gc-gari-013 \
  --nbd local/source/gamecube/tricky/gari.nbd --gsf local/source/gamecube/tricky/gari.gsf \
  --textures local/source/gamecube/tricky/gari.gsh \
  --reclaim-host-models --reclaim-geometry-textures --output local/builds/gc-gari-020

# 3. rails  (docs/gamecube-rails.md:94-101)
python3 tools/gamecube_spline_import.py --base-build local/builds/gc-gari-020 \
  --nbd local/source/gamecube/tricky/gari.nbd --gsf local/source/gamecube/tricky/gari.gsf \
  --output local/builds/gc-gari-021

# 5/6. surfaces, then grounded reset paths  (docs/gamecube-collision.md:67-72)
python3 tools/gamecube_surface_import.py --base-build local/builds/gc-gari-023 \
  --nbd local/source/gamecube/tricky/gari.nbd --output local/builds/gc-gari-025

# 7. static collision  (no command block in any doc; reconstructed from the argparse + hash chain)
python3 tools/gamecube_collision_import.py --base-build local/builds/gc-gari-027 \
  --nbd local/source/gamecube/tricky/gari.nbd --gsf local/source/gamecube/tricky/gari.gsf \
  --output local/builds/gc-gari-031
```

Stages 4 and 5-v1 have **no recorded command line**: stage 4 was
`local/evidence/garibaldi-visibility/build-022.py` with hard-coded paths, and
the superseded `reset-v1` profile no longer exists in `tools/gamecube_surfaces.py`.

## 2. What was generalised

The pipeline was already almost entirely flag-driven; the transform preset in
particular is *never* in code (`yaw 73` / `scale 0.55` appear only in docs and
one numeric round-trip test). Four things were genuinely Garibaldi- or
Snow-Jam-shaped, and all four are now parameters.

1. **Per-course presets** — `tools/course_presets/<name>.json` plus
   `tools/course_preset.py`. A preset carries the donor file set, the target
   slot (location, group, track, template patch, texture group, page word), the
   placement transform *with its derivation*, and the slot's race-line shape.
   `gamecube_terrain.py --preset aloha` fills in only the options that do **not**
   appear in argv, so a command line that passes every flag — which is what the
   Garibaldi recipe above does — is unaffected.
2. **A `.sop` reader** — `course_route.donor_paths()` and
   `course_route.start_list()`. `.aip` (Race) and `.sop` (Showoff) are the same
   container; no parser changed. `gamecube_terrain.py --race-aip` feeds the race
   and gate conversion from a different file than the reset paths, and
   `make_reset_aip(..., race_data=...)` carries it.
3. **The kind-21 trailer** — `race_course.race_markers()` plus a `markers`
   argument on `race_line_table()`. Race, backcountry and hub records carry
   `b=2`; the three slopestyle records carry `b=4`. The default reproduces the
   race trailer byte for byte (`(0, 0.0), (2, total)` — the old code's
   `'>3fI f'` pack has the same bytes).
4. **Gate folding and checkpoint count** — `race_course.select_donor_starts()`
   and `convert_race_course(..., checkpoint_limit=)`. The donor always has six
   start lanes; a race slot has six gates, slopestyle three, backcountry two.
   `convert_race_course` used to raise unless the counts matched, and truncated
   checkpoints at a literal 2 ("Snow Jam has two checkpoints").
5. **Two donor NBD header words** — `gamecube_surfaces.NBD_MAGICS`, now shared
   by `gamecube_surfaces.py`, `gamecube_splines.py` and `gamecube_scenery.py`,
   which each checked for `0x00161d03` alone. Across the ten GameCube Tricky
   courses the word is `0x00161d03` on gari, merquer and snow and `0x00161b03`
   on the other seven, including aloha. Every course passes the same 448-byte
   stride and extent checks under either word, so the third byte is treated as
   a version flag rather than a layout change.
6. **Padded LUN sections** — `gamecube_cleanup.disable_course_scripts` required
   the last program's length word to equal its span exactly. That holds on ARA1
   and fails on **29 of the world's 49 locations**, which pad the last span to a
   16-byte boundary with 4, 8 or 12 zero bytes (ASS1 pads 4). The check now
   accepts zero padding under 16 bytes and nothing else. ARA1's output is
   unchanged because ARA1 has no padding.
7. **Event selection in the ride harness** — `gamecube_course_check.py
   --menu-sequence`, so a check is not pinned to
   `native/diagnostics/course-start.json`. See §7.

### Garibaldi is byte-identical

The Garibaldi stage-1 recipe above was rebuilt with the changed tools and with
HEAD's tools, into two fresh directories, and the two archives compared:

| Build | Archive SHA-256 |
| --- | --- |
| `local/builds/gc-gari-regress-head` (HEAD tools) | `5dd3c01f7871e295038fdfebc33996077fa6cd7869aa3e270c352f78eb07a28d` |
| `local/builds/gc-gari-regress-013` (changed tools) | `5dd3c01f7871e295038fdfebc33996077fa6cd7869aa3e270c352f78eb07a28d` |

**Identical.** Note that neither matches `gc-gari-013`'s recorded
`3efd84fffab68df7caba7b6e8dfa04859ea0ada545d7711e9953ce363c7e6032`: the tools
have moved on since 12 September (surface transfer and grounded reset paths are
now inside stage 1, host occlusion curtains are removed, terrain bounds are
conservative), so the recipe no longer reproduces that exact archive at HEAD
either. The HEAD-vs-changed comparison above is the controlled one — same
inputs, same command, one build per tool version.

`PYTHONPATH=tools python3 -m pytest tests -q` passes.

## 3. The donor

All eleven GameCube Aloha members are in
`local/game/gste69-original/files/data/models/aloha.big` (C0FB container,
3,452,846 B). Decompressed to `local/source/gamecube/tricky/` alongside the
Garibaldi set:

| member | stored | decoded | SHA-256 (first 16) |
| --- | ---: | ---: | --- |
| `aloha.nbd` | 1,524,546 | 2,579,394 | `ebc6d292faa5bdcc` |
| `aloha.gsh` | 1,041,704 | 1,702,816 | `f373005154619443` |
| `aloha_L.gsh` | 221,104 | 393,712 | `7133ff393bc4b3ad` |
| `aloha.gsf` | 330,832 | 582,140 | `4ddea920bec6b7d1` |
| `aloha.aip` | 43,961 | 49,496 | `ae1eb1517bc37b0c` |
| `aloha.sop` | 17,742 | 19,148 | `45593560a7aebea3` |
| `aloha.map` | 102,198 | 828,738 | `ae2c5620f62f4dc6` |
| `aloha.btg` | 61,622 | 225,804 | `41827b7d4f1b1b34` |
| `aloha.adb` | 8,366 | 14,765 | `337a53fa524d1614` |
| `aloha_sky.nbd` | 2,445 | 5,854 | `f84c157fafd2e382` |
| `aloha_sky.gsh` | 97,215 | 132,896 | `52ff8fa94d9e52cb` |

Terrain: **2,871 patches**, **81** distinct terrain textures (of 178 images in
the sheet), **12** lightmaps.

`aloha.sop` decoded: 24 AI paths (all reset-eligible), 6 start lanes
`[0..5]`, 9 race paths. Its race chain is `0 -> 1 -> 2 -> 3`, 281,964 units of
2D length, finish event (type 9) 9,295.6 into path 3, so the run is 280,335.2
units. Two checkpoints (type 11): value **120** at 67,285.8 on path 0 and value
**45** at 8,045.1 on path 2. `aloha.aip` (Race) has 85 AI paths and a different
start line, and is not used.

## 4. The ASS1 slot

Read from stock `local/game/gxbe69-stock/files/data/worlds/bam.big`:

| property | ASS1 | ARA1 (for comparison) |
| --- | --- | --- |
| location index | 11 | 8 |
| groups | 40-48 (48 is the terrain/scene group) | 26-36 (36) |
| track index | **11** | 8 |
| terrain patches | 1,829 | 1,913 |
| group 48 records / memsize | 5,602 / 2,504,486 | 6,884 / 2,397,894 |
| race gates (start flag 2 == 0) | **3** — records 0, 1, 9, AI paths 55, 0, 55, all on track path 2 | 6 |
| freeride start `(1, 1)` | record 7, AI path 59, track 4 | record 6 |
| AI paths / track paths / starts | 95 / 5 / 10 | 129 / 8 / 14 |
| track chain from the gates | 2 -> 0 -> 1, 247,477 units | 3 -> 4 -> 5 -> 6 -> 7 |
| kind-21 | 248 nodes, **b = 4**, total 246,217.5 | 325 nodes, b = 2 |
| reset-eligible AI slots | 80 | 81 |

Template patch: **rid 63** (surface 0, flags 9, texture 295, lightmap 142, page
`0x000b002a`), the nearest normal-snow patch to the gate line. Its lightmap 142
lives only in group **42**, so 42 is the pinned texture group and the scenery
page word is `0x000b002a` (`track << 16 | texture group`).

### The type-1 markers

Every slopestyle kind-21 trailer, and only those three, carries two extra
`(tag 1, distance)` pairs after the usual `(0, 0.0)` and `(2, total)`:

| location | total | marker 1 | marker 2 | as fractions | checkpoint 0 / 1 |
| --- | ---: | ---: | ---: | --- | --- |
| ASS1 | 246,217.5 | 69,760.5 | 170,814.9 | 0.2833 / 0.6938 | 70,612.4 / 130,708.3 |
| DSS2 | 247,877.5 | 68,364.1 | 162,076.2 | 0.2758 / 0.6539 | 82,039.4 / 159,511.9 |
| ESS3 | 203,388.9 | 68,429.0 | 137,992.7 | 0.3365 / 0.6785 | 94,733.9 / 164,199.1 |

They are **not** the kind-18 checkpoint events: those still exist on the track
paths and sit elsewhere. The first marker is 68.4k-69.8k on all three courses,
which looks absolute rather than proportional, but nothing confirms that. What
a type-1 marker means is still unknown.

The converter therefore reproduces them **by position only**: the preset gives
ASS1's stock fractions (0.2833, 0.6938) and `race_markers()` multiplies them by
the converted run's own total. This keeps the record structurally valid and
keeps the markers inside the run; it is not a derivation from donor data.

## 5. The Aloha placement preset

`tools/course_presets/aloha.json`. Unlike Garibaldi's — which was hand-calibrated
against a live PCSX2 rider capture five seconds after the connector spawn
(`docs/full-course-experiment.md`) — Aloha's is derived analytically, because
ASS1's own gate line is in the stock kind-14 resource and the donor's is in
`aloha.sop`:

| quantity | value | how |
| --- | --- | --- |
| `source_anchor` | `(-343.590, -2877.282, 58695.381)` | mean origin of `aloha.sop`'s six start paths |
| `target_anchor` | `(-113619.003, 72924.477, -228281.771)` | mean position of ASS1's three stock race-gate start records |
| donor heading | 90.0000° | mean 2D heading of the six donor start paths' first segments |
| ASS1 gate heading | 161.4499° | mean 2D heading of the three gate start records |
| `yaw_degrees` | **71.4499** | 161.4499 − 90.0000 |
| `scale` | **0.55** | the Garibaldi lineage's Tricky→SSX 3 unit factor, reused unchanged |

The scale is the one free choice. 0.55 treats the unit factor as a property of
the two engines rather than of the course, which is why it is reused; the
alternative is the length-matching 0.8777 (ASS1's 247,477-unit stock chain over
the donor's 281,964), which would make the converted run the same length as the
stock R&B run. At 0.55 the converted run is 154,184 units against ASS1's stock
246,218 — about 63%. Neither has been ridden against the other.

## 6. The Aloha candidate build

Stage 1, with the preset supplying everything course-specific:

```sh
python3 tools/gamecube_terrain.py local/source/gamecube/ssx3/BAM.BIG \
  --preset aloha --drop-kind 3 --drop-kind 12 --clear-instance-references \
  --clear-script-bindings --disable-course-scripts --relocate-freeride-start --race-course \
  --output local/builds/gc-aloha-001 --jobs 8
```

`gc-aloha-001`, archive SHA-256
`f4a2e07781815152621c34742c2ad2e2d92c7a4e9b6074f4c82c3e8fa1324897`:

| | |
| --- | ---: |
| terrain patches | 1,829 → **2,871** |
| group 48 records / memsize | 4,107 / 2,006,286 (stock 5,602 / 2,504,486) |
| removed | 2,301 instances (kind 3), 226 collisions (kind 12), 10 occlusion curtains (kind 11) |
| cleared instance references / script bindings / disabled LUN programs | 1,683 / 228 / 184 |
| textures + lightmaps imported | 81 + 12, into pinned group 42 (163 records, 2,051,368 B) |
| world image totals after import (validated) | 869 textures, 674 lightmaps |
| AI paths / track paths / start records | 95 → **130** / 5 / 10 |
| donor reset paths | 24, into 80 eligible slots |
| kind-21 | 248 nodes, **b = 4**, total 154,184.75, markers (1, 43,684.07) and (1, 106,966.41) |
| track chain | 2 → 0 → 1, from the donor's 0 → 1 → 2 → 3 |
| gates | 3, on donor lanes **0, 2, 5** of 6 |
| checkpoints | 2 — (18, 0) 37,007.2 into track 2; (18, 1) 4,424.8 into track 1; finish at 53,795.1 on track 1 |

Two things about the gates are worth writing down. ASS1's three gates name only
**two** distinct AI paths (records 0 and 9 both use path 55, record 1 uses path
0), so the gate→AI-path assignment map has two entries, not three, and one
donor lane's AI line is not installed. And the run is 154,185 units against the
stock 246,218, which is the `scale` choice in §5, not a conversion error.

### Stages 2-4

Then scenery, rails and static collision, which take the slot from the base
build's recipe and only need the group/texture-group/page overrides:

```sh
python3 tools/gamecube_scenery_import.py --base-build local/builds/gc-aloha-001 \
  --nbd local/source/gamecube/tricky/aloha.nbd --gsf local/source/gamecube/tricky/aloha.gsf \
  --textures local/source/gamecube/tricky/aloha.gsh \
  --group 48 --texture-group 42 --page 0x000b002a \
  --reclaim-host-models --reclaim-geometry-textures \
  --models $(...640 ids, see local/research/aloha/scenery-models.json...) \
  --output local/builds/gc-aloha-002

python3 tools/gamecube_spline_import.py --base-build local/builds/gc-aloha-002 \
  --nbd local/source/gamecube/tricky/aloha.nbd --gsf local/source/gamecube/tricky/aloha.gsf \
  --output local/builds/gc-aloha-003

python3 tools/gamecube_collision_import.py --base-build local/builds/gc-aloha-003 \
  --nbd local/source/gamecube/tricky/aloha.nbd --gsf local/source/gamecube/tricky/aloha.gsf \
  --output local/builds/gc-aloha-004
```

The explicit `--models` list is a **workaround for a converter gap**: one of
Aloha's 171 scenery materials has texture index `0xFFFF` (untextured), and
`gamecube_scenery_import.py` indexes the donor `.gsh` image list directly, so it
raises `IndexError` on it. Garibaldi has no such material, which is why it never
appeared. Eight of the 648 eligible models use it (128, 135, 136, 139, 216, 247,
443, 469) and are excluded; the other 640 import. Handling the sentinel belongs
in that tool, which another change owns right now.

Results:

| build | stage | archive SHA-256 | what it added |
| --- | --- | --- | --- |
| `gc-aloha-001` | terrain | `f4a2e07781815152621c34742c2ad2e2d92c7a4e9b6074f4c82c3e8fa1324897` | the table above |
| `gc-aloha-002` | scenery | `8495116b99b6218469654d20630402a5a7e7e6e12401df44c91ad9dcf56e1d00` | 640 models, 1,594 placements (188 initially hidden ones skipped), 78 new scenery textures, 567 host records reclaimed (1,136,476 B), 107,215 resources |
| `gc-aloha-003` | rails | `0268387eead17e3b9e9dc41af16d4fb8d4482b1c09561814c95ab6071e5e9b11` | 133 splines / 454 segments replacing 268 host splines; conversion audit 116,678 samples, max position error 0.0167 units, max join gap 0.0308, zero bound violations |
| `gc-aloha-004` | static collision | — | **blocked**, see below |

### Static collision is blocked

`gamecube_collision_import.py` needs two recipe fields that only the retired
ad-hoc visibility script (`local/evidence/garibaldi-visibility/build-022.py`)
ever wrote:

- `visibility.source_gsf_sha256`, its GSF guard. **Fixed here**: it now falls
  back to `scenery.gameplay_sha256`, which records the same file.
- `scenery.instance_source_ids`, the target-rid → donor-instance map
  `bind_static` uses to attach collision to the right placements. **Not fixed.**

Rebuilding that map outside the scenery importer does not work, and the attempt
is worth recording because it looks like it should. The 022 script rebuilt it
by walking `source_models` and matching `scene.instances` by model, which
assumes the importer wrote *every* eligible placement and that every imported
model has geometry in `parts[0]`. Neither holds any more: the scenery importer
now applies donor visibility itself (`gamecube_scenery_import.py:458` — on
Aloha it wrote 1,594 of 1,782 and reported `hidden_source_instances: 188`), and
several Aloha models have an empty `parts[0]['meshes']`, which makes 022's
opcode lookup raise `IndexError`. Garibaldi has neither problem, which is why
its lineage never noticed.

The map belongs in `gamecube_scenery_import.py`, which knows which donor
instance produced each record as it writes it. Recording it there is what
unblocks static collision for any second course. Detail:
`local/research/aloha/collision-blocker.md`.

## 7. The ride

### The event cannot be selected, for two independent reasons

**1. The frontend does not offer R&B.** The check harness walks the frontend
with a fixed controller sequence. Frames from an earlier run
(`local/research/aloha/menu-evidence/`) show the path it takes: Select Peak
(Peak 1; peaks 2 and 3 padlocked) → Select Event → briefing. The Select Event
list on Peak 1 holds exactly **three** entries — Snow Jam, Metro-City,
Happiness — because the rest are locked on a fresh profile, and the harness
always starts from a fresh isolated profile. R&B is not in the list, so no
D-pad sequence reaches it. `--menu-sequence` (added here) makes another
sequence *possible*; it does not make ASS1 *reachable*.

**2. The event table cannot be repointed either.** The obvious way round is to
make the entry the harness already selects load ASS1: the GameCube event table
is at `main.dol` file offset `0x2CB5EC` (100-byte records, SDB code at +52) and
the discipline table at `0x2DFC18` (event index, mode), both dumped and
verified here. `local/research/aloha/patch_event0_to_ass1.py` rewrites two
words of a copy — event 0's code `ARA1` → `ASS1` and its mode `2` → `3` —
producing DOL SHA-256 `383144a2f16187335f14aa3154bcba5d15735666b86327d51e8cd7d33b60758a`.
The native runtime rejects it: `tools/native_gamecube.py:229` pins the
extracted game's DOL hash to `b92162d6…`, so a patched DOL needs the pin
updated and the recompiled module regenerated. That is a native-runtime change,
not a data conversion, and it was not attempted.

So **the converted course has not been ridden.** The archive itself was taken
through a bounded native check to confirm it boots and plays:

```sh
python3 tools/gamecube_course_check.py \
  --game local/research/aloha/game-aloha-rails-001 \
  --profile sg-aloha-2 --output local/research/aloha/ride-002 --seconds 180
```

Result: **exit 0**, 817 observed samples, `riding_observed_after_start: true`,
no reset loops, 60 FPS throughout, zero invalid accesses / GPU errors / unknown
instructions / failed chunk checks in
`local/reports/native-runs/20260915-000612.log`. Screenshots:
`local/research/aloha/ride-002-screenshots/` (5 frames).

What this does and does not show. With the stock DOL the harness's first
Select Event entry is still **Snow Jam / ARA1**, and the ride confirms it: the
743 riding samples span x −199,522…−131,865, y 11,987…45,879, z
−296,883…−228,771, which is ARA1's corridor, not ASS1's
(−113,728…−233,737 / 72,830…208,559). The screenshots show stock Snow Jam with
six racers. So this establishes that the rebuilt archive **boots, streams and
plays**, and that replacing ASS1's groups and growing the world image tables to
869/674 leaves an untouched location riding normally. It is **not** evidence
about the converted course, which was never loaded.

`local/research/aloha/game-aloha-rails-001` (stock DOL, `gc-aloha-003`'s
archive, everything else symlinked from `local/game/gxbe69-stock`) and
`local/research/aloha/game-aloha-ass1-001` (the same archive plus the patched
DOL) are both staged for whoever runs it next.

## Open items

Phase 2, and everything this document does not establish:

- **Scoring and the end of the run.** A slopestyle event scores instead of
  timing (`behiloc.dbb` row 5 is five descending scores, not times). Whether
  that lives in the executable's mode-3 path or in ASS1's kind-16 LUN programs
  is undetermined, and every imported LUN program is a 36-byte stub, so the
  event cannot be expected to score or finish. This is the same layer-(c)
  blocker that keeps Garibaldi's breakables inert.
- **Type-1 marker semantics** (§4) — reproduced by position, not understood.
- **Showoff prop set.** The donor GSF's `ShowoffMode`/`HideRace` programs, and
  GSF opcode 25 (68 undecoded commands, presumed to be the `Patch_ShowOff_*`
  toggle), are not evaluated; the scenery import still uses the race profile.
- **Showoff terrain patches.** `aloha.map`'s `PATCHES` section names the
  `Patch_ShowOff_*` set; nothing selects it.
- **Which 3 of 6 donor lanes** a 3-gate slot wants. `select_donor_starts` keeps
  the outer lanes and spaces the rest evenly; the engine's own preference is
  unverified.
- **Medal targets.** No tool writes `behiloc.dbb`.
- **Name and description.** `tools/patch_executable.py` is PS2-ISO-only with
  wrong GameCube offsets, and `cmnamer.loc`'s ASS1 index and hash are unsolved,
  so the transport menu still reads "R&B".
- **Start gate.** `gamecube_startgate.py` binds Snow Jam's countdown slot
  (`COUNTDOWN_SLOT = 3`) and a six-gate race; a three-gate slopestyle start has
  not been checked.
- **Static collision** (§6) — `scenery.instance_source_ids` has to move into
  `gamecube_scenery_import.py`.
- **Reaching the event** (§7) — either the frontend's Select Event list has to
  offer R&B (a save/unlock question), or the DOL pin and the recompiled module
  have to accept a repointed event table.
- **The 0xFFFF scenery material** — eight Aloha models are excluded until
  `gamecube_scenery_import.py` treats it as "no texture".
- **Flipbook cycling.** Aloha's beach/stadium art is flipbook-heavy and nothing
  advances a frame index.
