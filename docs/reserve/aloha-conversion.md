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
`docs/reserve/gamecube-world.md`, `docs/reserve/gamecube-scenery.md`, `docs/reserve/gamecube-rails.md`,
`docs/reserve/gamecube-collision.md` and the recorded recipes in
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
# 1. terrain + art + paths + race line  (docs/reserve/gamecube-world.md:300-309)
python3 tools/gamecube_terrain.py local/source/gamecube/ssx3/BAM.BIG \
  --nbd local/source/gamecube/tricky/gari.nbd --location ARA1 --template-rid 1673 \
  --source-anchor=-1214.8,-195.5,-768.547891 --target-anchor=-118613.68,15753.8,-228880.14 \
  --yaw 73 --scale .55 --drop-kind 3 --drop-kind 12 --clear-instance-references \
  --clear-script-bindings --disable-course-scripts --pin-texture-group 31 \
  --reset-aip local/source/gamecube/tricky/gari.aip --relocate-freeride-start --race-course \
  --textures local/source/gamecube/tricky/gari.gsh \
  --lightmaps local/source/gamecube/tricky/gari_L.gsh --output local/builds/gc-gari-013

# 2. scenery  (docs/reserve/gamecube-scenery.md:148-156; defaults --group 36 --texture-group 31 --page 0x0008001f)
python3 tools/gamecube_scenery_import.py --base-build local/builds/gc-gari-013 \
  --nbd local/source/gamecube/tricky/gari.nbd --gsf local/source/gamecube/tricky/gari.gsf \
  --textures local/source/gamecube/tricky/gari.gsh \
  --reclaim-host-models --reclaim-geometry-textures --output local/builds/gc-gari-020

# 3. rails  (docs/reserve/gamecube-rails.md:94-101)
python3 tools/gamecube_spline_import.py --base-build local/builds/gc-gari-020 \
  --nbd local/source/gamecube/tricky/gari.nbd --gsf local/source/gamecube/tricky/gari.gsf \
  --output local/builds/gc-gari-021

# 5/6. surfaces, then grounded reset paths  (docs/reserve/gamecube-collision.md:67-72)
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
(`docs/reserve/full-course-experiment.md`) — Aloha's is derived analytically, because
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

- **Scoring and the end of the run.** Answered in §10: it is the executable's
  mode path, not the course script — no builtin or handler name distinguishes
  the slopestyle courses' scripts from any other discipline's. So the stubbed
  LUN programs cost props and animation rather than scoring, and what remains
  is running the event *as* slopestyle (the `mode` limitation in
  [course selection](course-selection.md)) plus medal targets in
  `behiloc.dbb`.
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
- ~~**Static collision** (§6) — `scenery.instance_source_ids` has to move into
  `gamecube_scenery_import.py`.~~ Done, §8.1; the build order against rails is
  answered in §8.5, and §9.3 has the native impact check: the engine returns
  contacts against an imported collider and the ride differs from the same
  archive without collision. Per-object query ownership is still unproven.
- **Reaching the event** (§7) — either the frontend's Select Event list has to
  offer R&B (a save/unlock question), or the DOL pin and the recompiled module
  have to accept a repointed event table.
- ~~**The 0xFFFF scenery material** — eight Aloha models are excluded until
  `gamecube_scenery_import.py` treats it as "no texture".~~ Done, §8.2: the
  untextured mesh is dropped, six of the eight models import, and the two that
  are nothing else are refused without losing a visible placement.
- **Flipbook cycling.** Aloha's beach/stadium art is flipbook-heavy and nothing
  advances a frame index.

## 8. Static collision, unblocked (September 15)

Both §6 blockers are fixed in `tools/gamecube_scenery_import.py`, and Aloha now
has a static-collision build.

### 8.1 The placement map is recorded where the decision is made

`compile_static` now writes `scenery.instance_source_ids` — target instance RID
(as a JSON string) → donor scene instance index — at the moment it appends each
placement, next to the visibility test that decides whether the placement exists
at all. That is the field `gamecube_collision_import.bind_static` needs, and it
replaces the retired `local/evidence/garibaldi-visibility/build-022.py`. Nothing
else about the archive changes: the map lives only in `scenery.json` /
`experiment.json`.

Re-deriving it afterwards is impossible for the reasons in
`local/research/aloha/collision-blocker.md`, and the fix is to stop trying.

**Garibaldi is byte-identical.** The stage that reads `gc-gari-013` — scenery —
was rebuilt twice from the §1 command, once with HEAD's tools and once with the
changed ones:

| Build | Archive SHA-256 |
| --- | --- |
| `local/builds/gc-gari-regress-scenery-head` (HEAD tools) | `c479370fffd7d0d771875d846cfb4d603862ca31ebb7ba7f2bd8b80813276664` |
| `local/builds/gc-gari-regress-scenery-new` (changed tools) | `c479370fffd7d0d771875d846cfb4d603862ca31ebb7ba7f2bd8b80813276664` |

**Identical**, 624 models and 3,252 placements either way. The recipe JSON gains
exactly three keys (`instance_source_ids`, `untextured_materials`,
`untextured_meshes_skipped`) and no existing value changes.

The new Garibaldi map also cross-checks against the retired script's: the 3,252
pairs are in the same order as `gc-gari-022`'s 3,239, and the 13 extra entries
are exactly the instances 022 removed. Aloha's map is checked much harder — see
§8.3.

### 8.2 Texture index 0xFFFF is the donor's untextured material

A GC Tricky material opens with the same four texture-stage halfwords SSX 3
uses, and `0xffff` marks an unused stage. Of the 2,575 stock SSX 3 materials,
2,456 leave stages 1-3 unset and 119 use two stages, so the stages are an array
the engine walks, skipping `0xffff`. Aloha's material 1 leaves **stage 0** unset
as well and clears flags bit 3 (`0x00015000` against `0x00015008` /`0x00055008`
on the textured ones), which is the donor's own "untextured" marking — not an
out-of-range image ID.

It is **not** passed through. No stock SSX 3 material leaves stage 0 unset (0 of
2,575), so a material with no base texture is an unverified target encoding, and
this pipeline does not emit untested forms (the same rule that keeps donor
geometry flags out of the model record). `--models` is no longer needed either
way, because the sentinel is now handled instead of avoided:

- `untextured_materials()` collects the donor materials with texture `0xffff`.
- `mesh_items()` drops **only those meshes**; the rest of the model imports.
- `eligibility()` refuses a model only when it has *nothing else*
  (`untextured material only`).

All 8 affected models use the single material 1 for exactly one mesh each, and
every one of those meshes is a small untextured box or quad:

| model | meshes | dropped mesh | donor placements (visible) | outcome |
| ---: | ---: | --- | ---: | --- |
| 128 | 2 | 6 quads | 4 (4) | imported without it |
| 135 | 3 | 6 quads | 23 (23) | imported without it |
| 136 | 3 | 8 quads | 23 (23) | imported without it |
| 139 | 3 | 3 quads | 1 (0) | imported without it |
| 216 | 5 | 2 strips, 10 verts | 3 (3) | imported without it |
| 443 | 2 | 6 quads | 4 (4) | imported without it |
| 247 | 1 | the whole model (1 quad) | 1 (0) | **refused** |
| 469 | 1 | the whole model (1 flat quad) | 1 (0) | **refused** |

So **no visible placement is lost**: 247 and 469 have one donor instance each
and both are hidden. Eligible models go from 640 (the §6 `--models` workaround)
to **646** of 687.

### 8.3 The builds

```sh
python3 tools/gamecube_scenery_import.py --base-build local/builds/gc-aloha-001 \
  --nbd local/source/gamecube/tricky/aloha.nbd --gsf local/source/gamecube/tricky/aloha.gsf \
  --textures local/source/gamecube/tricky/aloha.gsh \
  --group 48 --texture-group 42 --page 0x000b002a \
  --reclaim-host-models --reclaim-geometry-textures \
  --output local/builds/gc-aloha-004

python3 tools/gamecube_collision_import.py --base-build local/builds/gc-aloha-004 \
  --nbd local/source/gamecube/tricky/aloha.nbd --gsf local/source/gamecube/tricky/aloha.gsf \
  --output local/builds/gc-aloha-005
```

| build | stage | archive SHA-256 |
| --- | --- | --- |
| `gc-aloha-004` | scenery, no `--models` | `5acf74c2b2b9a9253df109022ab1b7922b69592147b5e4ccac1d0fb76468c14e` |
| `gc-aloha-005` | static collision | `c0d0b336a436e6ad3877c722014bbba55afb7e95d5f919fad8fb7a357832360c` |

`gc-aloha-004` (scenery), against `gc-aloha-002`'s 640/1,594:

| | |
| --- | ---: |
| models imported | **646** of 687 (omitted: 26 animated, 5 local matrix, 4 normal palette, 4 multipart, 2 untextured-only) |
| placements | **1,651** (189 hidden donor instances skipped) |
| untextured meshes dropped | 6, one each on models 128/135/136/139/216/443 |
| new scenery textures | 80 |
| host records reclaimed | 567 (1,136,476 B) |
| group 48 records / memsize | 7,289 / 2,283,186 (stock 5,602 / 2,504,486) |
| resources (capacity-validated) | 107,298 |
| `instance_source_ids` | 1,651 pairs |

`gc-aloha-005` (static collision):

| | |
| --- | ---: |
| colliding instances enabled | **677** of 1,651 |
| collision resources / bytes | 163 / 307,116 |
| distinct donor collision meshes | 163 |
| binding definitions | 164 (163 colliding + 1 shared non-colliding) |
| skipped | 329 — 92 `mode-2/effect-8`, 44 protected-reset-corridor, 36 `mode-3/effect-51`, 35 `mode-2/effect-35`, 7 multipart-collision, and 115 more across 20 mode/effect pairs |
| non-colliding placements (no GSF collision flag) | 645 |
| group 48 records / memsize | 7,452 / 2,591,606 |
| resources (capacity-validated) | 107,461; 107,298 reference records audited |

The memsize is 3.5% over ASS1's stock 2,504,486. That is well inside the
precedent: `gc-gari-031` runs ARA1's group 36 at 2,825,886 against a stock
2,397,894 (+18%).

### 8.4 What was validated, and what was not

Every static check the two tools own passed, and one of them is a direct proof
of the new map: `bind_static` re-derives each placement's 160-byte instance
record from the donor instance the map names and requires it to match the bytes
already in the archive, so all **1,651** pairs are confirmed against the donor,
not merely plausible. Also:

- `validate_static_bindings` on the rebuilt binding table: 1,651 bound
  instances, extents, definition kinds, no effect callbacks, and collision part
  count equal to render-model part count on every colliding definition.
- Archive readback: group 48 re-read from the assembled archive equals what was
  written, record for record; every other group's blocks are byte-identical.
- `validate_resource_capacities`: all 107,461 resources within their
  RID-indexed tables.
- No retained object/NIS references anywhere (107,298 records audited).

**Not validated: anything at runtime.** `native_impact_verified` is still false
and no contact-return check exists that does not need the native runtime — the
only checker, `tools/gamecube_collision_check.py`, consumes a native trace.
Another agent held the runtime for this task's window, so nothing was ridden and
nothing was observed either way.

### 8.5 The ordering question, answered

`gc-aloha-004`/`005` was the scenery→collision chain without rails:
`gc-aloha-003` had been built on the superseded `gc-aloha-002` scenery, so no
single archive held all four stages. Re-running the chain in the Garibaldi
order — scenery → splines → collision — closes it, and the conversion needed
no change:

```sh
python3 tools/gamecube_spline_import.py --base-build local/builds/gc-aloha-004 \
  --nbd local/source/gamecube/tricky/aloha.nbd --gsf local/source/gamecube/tricky/aloha.gsf \
  --output local/builds/gc-aloha-006

python3 tools/gamecube_collision_import.py --base-build local/builds/gc-aloha-006 \
  --nbd local/source/gamecube/tricky/aloha.nbd --gsf local/source/gamecube/tricky/aloha.gsf \
  --output local/builds/gc-aloha-007
```

| build | stage | archive SHA-256 |
| --- | --- | --- |
| `gc-aloha-006` | rails on the new scenery | `f52893ffbdf11292315c4fe7ac409da4f4816cb2f60b6757791a3b2d12fea569` |
| `gc-aloha-007` | **terrain + scenery + rails + collision** | `73ad0ab6ceab2ff1f7e3e31a5e57ed231b9b45eba354c986c1141cd0eeedd2d7` |

The two stages are independent, which is the useful part. `gc-aloha-006`'s rails
report equals `gc-aloha-003`'s to the digit — 133 splines, 454 segments,
replacing 268 host splines, 116,678 audit samples, max position error 0.0167
units, max join gap 0.0308, zero bound violations — so re-seating the stage on
646 models instead of 640 changed nothing about the conversion. And
`gc-aloha-007`'s collision report is identical to `gc-aloha-005`'s field for
field (163 collision resources / 307,116 B, 164 definitions, the same 329
skipped instances across the same 25 mode/effect reasons, no unsupported
transforms) except for the three values that *must* move: the base and output
hashes and the record counts the rails stage changed (107,163 audited reference
records against 005's 107,298, because rails replaced 268 host splines with
133). Placement accounting still adds up: 1,651 placements = 677 colliding +
645 non-colliding + 329 skipped.

`gc-aloha-007` is the build to ride, install and carry forward; `005` is
superseded. Its group 48 holds **7,317 records / 2,497,358 B** against ASS1's
stock 5,602 / 2,504,486 — the four-stage course now fits *under* the stock
memsize, because the rails stage replaced 268 host splines with 133 and cut
spline geometry from 164,928 to 71,760 bytes, more than paying for the 307,116
bytes of collision.

## 9. The ride (September 15)

The [boot-time course redirect](course-selection.md) removed the §7 blocker, so
`gc-aloha-007` was ridden on the native runtime. Four bounded 200-second checks,
each on a fresh isolated profile, all exit 0, all `riding_observed_after_start:
true`, none with a detected reset loop, and every one with zero invalid memory
accesses, GPU command errors, unknown guest instructions and JIT fallback runs:

| run | archive ridden | game directory | profile | receipt |
| --- | --- | --- | --- | --- |
| `ride-003` | `gc-aloha-007` (`73ad0ab6`) | `game-aloha-007` | `sg-aloha-7` | `20260915-084429` |
| `ride-004` | `gc-aloha-006` (`f52893ff`), no collision | `game-aloha-006` | `sg-aloha-6` | `20260915-084941` |
| `ride-005` | `gc-aloha-007` again | `game-aloha-007` | `sg-aloha-7b` | `20260915-085350` |
| `ride-006` | `gc-aloha-007` as `alo.big` | `game-two-course-001` | `sg-2crs-1` | `20260915-085730` |

All four are under `local/research/aloha/`; the manifests are
`aloha-007-ass1.txt` and `two-course-alo.txt`. Every run spawned at exactly
`(-113667.5, 72738.8, -228282.9)`, and across all four the rider stayed inside
ASS1's corridor: x −142,947…−113,667, y 61,361…87,235, z −291,840…−228,283. The
stock control `ride-002`, same archive but no redirect, rode ARA1 instead — x
down to −196,811 and y no higher than 45,879 — so the corridor is what
identifies the course that loaded. Screenshots under each profile's
`ScreenShots/GXBE69/` show the rider on Aloha's geometry at 36–67 mph with its
scenery standing, and the trick score rising (840 at one capture).

So **the four-stage course rides**: terrain, scenery, rails and collision in one
archive, reached with a stock DOL through the event-row redirect.

### 9.1 Two courses resident at once

`ride-006` is the course-picker data model rather than another Aloha check.
`tools/gamecube_game_dir.py` staged a game directory holding **both** stock
`bam.big` (symlinked, untouched) and `gc-aloha-007` installed as `alo.big` with
its BIGF world members renamed to `data/worlds/alo.*`, and the manifest pointed
event 0 at `archive = alo`. The runtime logged
`event 0 archive at 802ce630: "BAM" -> "alo"`, and the ride spawned on Aloha at
the same coordinates as `ride-003`. Adding a course therefore replaces no stock
file and needs no rebuild — only an archive and a manifest line.

That exposed one provenance gap, now fixed: `tools/native_gamecube.py` hashed
`files/data/worlds/bam.big` alone, so in a two-course directory the receipt
named the stock archive rather than the one ridden. The receipt now also carries
`world_archives_sha256` for every installed `*.big`, and
`gamecube_collision_check.py` accepts a candidate that is any installed archive
instead of requiring it to be `bam.big`.

### 9.2 A free-running ride cannot A/B anything

`ride-003`/`ride-004` were meant to be a controlled A/B of static collision:
the two archives differ only by the collision stage, and the harness sends no
riding input, so a path difference would have been the colliders doing
something. `ride-005` is the control that says whether that reasoning holds,
and it says it does not. `tools/ride_compare.py` (added here; it re-bases each
trace at its own race start, because the harness repeats its start request
until riding is observed and the runs leave the gate 15 guest seconds apart):

| pair | archives | median separation | max | first beyond 10 units |
| --- | --- | ---: | ---: | --- |
| `ride-003` vs `ride-005` (the floor) | **same** (`gc-aloha-007` twice) | 449 | 69,184 | 14.5 units, 0.21 s after the start |
| `ride-003` vs `ride-004` (the A/B) | 007 with collision vs 006 without | 4,883 | 68,988 | 16.1 units, 0.31 s after the start |

Both pairs start at a separation of exactly 0 and both leave the 10-unit
tolerance within a third of a second. Two runs of the *same* archive,
single-core, with identical scripted input, end up a median 449 units and a
maximum 69,184 units apart, so the harness's free-running ride is not
reproducible at all. The A/B's median is about eleven times the floor's, which
is suggestive and nothing more: one control pair whose own maximum is 69,184
units cannot support attributing a 4,883-unit median to the colliders.
**This free-run A/B is inconclusive by design, not by result.** Reports:
`local/research/aloha/floor-007-vs-007.json` and `ab-007-vs-006.json`.

What this rules in is the instrument, not more runs. §9.3 uses the one that
works.

Not shown by the four free runs: a completed run, gate or checkpoint passage,
scoring at the end, or anything about the donor's own art (the geometry is
untextured). The HUD still reads a race — "3rd/6" with a lap timer — which is
the known `mode` limitation in [course selection](course-selection.md), not an
Aloha problem.

### 9.3 Static collision, observed under movie playback

`tools/native_determinism_check.py` records a Dolphin input movie and replays
it with the guest clock fixed, and it now takes `--course-manifest` so both arms
are redirected identically. One movie was recorded on `gc-aloha-007`
(`det-record-007.dtm`, `05cf8cb7`) and replayed three times, 200 s each, exit 0
with clean counters throughout.

**Playback is deterministic.** Two replays on the same archive
(`det-play-007-a`, `det-play-007-b`) agree on **all 879** sampled control-flow
rows — dispatch 0 through 920,649,728, equal pc, lr, ctr, cr and guest timebase
— with equal observed rider state transitions
(`dispatch-playback-floor.json`). Their rider traces read as *exactly* equal at
many sampled instants and never exceed 113 units apart except for one 1,860-unit
sampling spike, which is the host-timed observer catching the two runs at
slightly different guest instants rather than a path difference
(`floor-playback.json`).

**The same movie on the same course without collision rides differently.**
Replaying it on `gc-aloha-006` (`det-play-006`) tracks the collision arm for
twenty seconds — separations inside the floor's envelope, exactly 0.0 as late as
t = 20.01 s after the race start — and then parts permanently:

| t after the start | floor (007 vs 007) | A/B (007 vs 006) |
| ---: | ---: | ---: |
| 10 s | 0 | 111 |
| 20 s | 0 | 0 |
| 30 s | 88 | 2,956 |
| 40 s | 0 | 12,852 |
| 60 s | 113 | 21,572 |
| 75 s | 0 | 53,261 |

The A/B's median separation is 10,840 units against the floor's 24, and it
passes the floor's *maximum* at t = 22.03 s and never returns
(`ab-playback-007-vs-006.json`).

**What happens at the split is a contact.** From t = 20.9 s the collision arm's
rider holds a constant height — y = 68,742 exactly — for 1.8 s while its x
reverses direction, and it is inside the world-space volume of enabled collider
**rid 524** (donor scene instance **1128**, 48 collision vertices, world box
x −119,497…−117,747, y 67,588…69,395, z −271,320…−265,669) the whole time. The
no-collision arm passes through the same volume without slowing and keeps
climbing, y 68,661 → 70,263, into the next object's volume. Same recorded pad
input, one archive difference.

**And the engine says so directly.** Replaying the movie once more with the
existing collision-trace module (`a8d6b3b1`) and
`SSX_COLLISION_INSTANCE=0x0B00020C` — track 11, instance 524 — then
`tools/gamecube_collision_check.py --source-instance 1128`:

```
"stages": {"bound": 1, "broad_contact": 632, "narrow_enter": 592, "narrow_exit": 592},
"contact_return_histogram": {"0": 591, "3": 1},
"positive_returns": 1,
"selected_obstacle_contact_verified": true
```

The imported obstacle registers with world bounds the engine computes itself,
is broad-phase tested 632 times, reaches the narrow phase 592 times, and returns
**3 contacts** once. That return's query box centre is 59.5 units from the
player's own position 0.4 s after its constrained interval ends. Report:
`local/research/aloha/contact-524/contact-report.json`.

Two limits stay, and they are the checker's own: the trace can observe opponents
too, so `player_query_identity_verified` is **false** — the positive return is
not *proven* to be the player's query, only to be against the selected object
at the player's position and time. And one positive return across a 1.8-second
constrained interval is fewer than a sustained slide along the object would
suggest, so the held height may be terrain with the traced contact a separate
event. What is established is that Aloha's imported static collision is live in
the engine and changes the ride; which surface held the rider for those 1.8
seconds is not.

This also makes `gc-gari-interactions-002` testable the same way: record a
movie, aim `SSX_COLLISION_INSTANCE` at a bound block or pane, and the
deliberate-contact question becomes a replay instead of a lucky autopilot.

## 10. Phase 2: scoring is not in the course script (September 15)

The open item said "whether that lives in the executable's mode-3 path or in
ASS1's kind-16 LUN programs is undetermined", and costed a script-side scoring
driver at 2-4 days. It is the executable, so that driver should not be written.

Every stock course's kind-16 script was disassembled with `tools/gamecube_lun.py`
— all 17 courses across the five disciplines, 2,000-odd programs, every one of
them decoding cleanly — and two vocabularies compared: the builtin indices each
program calls, and the name hashes it registers handlers under.

| discipline | courses | builtins common / union | handler names common / union |
| --- | ---: | ---: | ---: |
| race | 5 | 42 / 63 | 7 / 45 |
| slopestyle | 3 | 40 / 54 | 3 / 41 |
| big air | 3 | 37 / 55 | 3 / 33 |
| halfpipe | 3 | 35 / 43 | 3 / 19 |
| backcountry | 3 | 39 / 53 | 7 / 45 |

**No builtin and no handler name is common to a discipline's courses and absent
from every other discipline — except backcountry.** Slopestyle, big air,
halfpipe and race each contribute an empty set; backcountry's three courses
share five name hashes nothing else uses, so that discipline does have
script-side machinery of its own. A slopestyle course's script is props and
decoration, the same as a race course's.

So the discipline is engine-side, and this reframes what Aloha still needs:

1. **Run the event as slopestyle.** This is the `mode` limitation already
   measured in [course selection](course-selection.md): setting the event's
   mode word to 3 does not switch the HUD or the briefing, because the Single
   Event menu passes the discipline the player picked, and the consumer at
   `0x801093D0` reads the event's own word only when its caller passes 7. That
   is the blocker — not a missing script. Disabling the imported course's
   scripts costs props and animation, not scoring.
2. **Medal targets.** `behiloc.dbb` row 5 is five descending scores and no tool
   writes it.
3. The kind-21 slopestyle trailer (`b = 4` with the two type-1 markers) and the
   three-gate start line the importer already produces.

What is still unmeasured: whether a redirected event that *is* reached as
slopestyle scores and finishes correctly with converted data. Reaching a finish
at all needs steering ([route control](route-control.md)), which is why that
work comes first.
## 11. The event *can* be selected: the Freestyle branch (September 15)

Section 7's first blocker is gone, and it was never a table problem. Single
Event's **Select Peak → Select Mode** offers **Race** and **Freestyle**; the
harness's fixed controller sequence had always taken Race, whose Peak 1 list is
Snow Jam / Metro-City / Happiness. One D-pad press takes Freestyle, and its
Peak 1 list is **R&B / Crow's Nest / The Junction / Happiness Jam**.

`native/diagnostics/course-start-freestyle.json` walks it. Two details cost a
run each: the branch inserts a **My Rules** screen between the event list and
the briefing, so the sequence needs one more A; and the slots have to be
**ten seconds**, because boot speed varies by about five seconds between runs
and a five-second slot put the Freestyle press on the Select Peak screen, which
walked the highlight onto a locked peak where A does nothing.

**Stock R&B through that path rides as slopestyle** (`fs-stock-2`, 1,192
observed samples): score in the corner, `OPPONENT +31841`, no lap counter, a
"Single Event - Slopestyle" briefing and a standings screen with a 340,000
record score. So the discipline follows the *event the player picks*, and a
donor course wants a slot of its own discipline - which ASS1 already is. No
`mode` patch, no manifest at all: `game-aloha-007` stages the Aloha build as
`bam.big`, and event 5 already carries `code = ASS1`, `location = 5`,
`mode = 3`.

### The converted course crashes on the slopestyle load path

Reproducible in two runs (`ride-freestyle-001`, `-002`): the menu reaches the
R&B standings screen, then the run dies on `Invalid read from 0x903d850c,
PC = 0x80222b80`, followed by reads from `0xc`, `0x18`, `0x0` - a null
structure pointer, not a stray address. Stock R&B through the identical
sequence rides fine, so this is the converted content on a path the event-0
race host never exercised.

One concrete fault found while looking, `tools/gamecube_slot_probe.py` against
the build: **every imported patch carries page word `0x0008002a`** - texture
group 42 (right) with track **8** (wrong; ASS1 is track 11). `bind_patch`
hard-coded `0x80000 | group`, which is correct only for ARA1, whose track *is*
8, so the Garibaldi lineage never noticed. Fixed: the page word is now
`track << 16 | group` and the track defaults to the target record's own, so
both lineages get their own slot's value. Whether that is *the* crash is
unproven - it needs a stage-1 rebuild and another ride.

The kind-21 race line, at least, is right: 248 nodes, four trailer entries,
total 154,184.8 with type-1 markers at 0.2833 and 0.6938 of it, matching stock
ASS1's fractions.

