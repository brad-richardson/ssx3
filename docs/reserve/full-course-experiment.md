# Complete Garibaldi terrain replacement experiments

This resumes the last Claude session after `fa9a0e4`. That session verified
the executable menu rename but hit its quota before implementing the locale
description edit or the complete course replacement.

## Placement and build

The baseline was `name-001`. Transport → Peak 1 → Freeride → Garibaldi
spawns near `(-111402.46, 13426.05, -226412.94)`. The spawn itself is on the
`A_ARA1` connector (group 6), so anchoring exclusively to a race patch at that
position would be incorrect. Five seconds later the rider reaches
`(-118613.68, 15753.80, -228875.14)` on the approach to the race terrain.

The Tricky PBD has zero player-start records. Garibaldi's `gari.aip` instead
provides six start-path indices; the first path begins at approximately
`(6679.98, -8676.90, 992.95)`, runs west, then turns north into the descent.
Vector points are relative displacements `xyz * w`, accumulated from the
path origin (layout reference: pinned SSX-Library `AIPSOPHandler.cs`).

The chosen entry is after this opening turn: donor XY `(-1214.8, -195.5)`
lies on patch 50 at approximately `(u, v) = (0.881903, 0.020955)`, surface
Z `-768.547891`. It maps to `(-118613.68, 15753.80, -228880.14)`, five units
below the measured rider. The transform rotates **73 degrees about +Z** and
scales uniformly by **0.55**. This scale is a placement experiment, not a
verified Tricky-to-SSX-3 unit conversion.

`tools/replace_terrain.py` replaces all **1,913** ARA1 terrain patches in
group **33**, track **8**, with all **3,885** Garibaldi patches. Patch **1673**
supplies the existing snow material/texture/lightmap fields. Original patch
IDs are reused in stream order, followed by new IDs. Transformed coefficients
are rounded to their stored float32 values before regenerating bounds,
spheres and corners. SDB resource counts and memory size are updated; all
other resources and the spatial tree remain intact. The kind counts that
match the ARA1 group are kinds **0–12**; the next u16 is zero even though
kind 13 has one resource, so it must not be assumed to count kind 13.

| Property | Value |
| --- | --- |
| Group decoded bytes | 5,155,109 → 6,022,789 |
| Group stream blocks | 78 → 93 |
| Archive bytes | 113,569,920 |
| Image bytes | 3,118,987,264 |
| Archive SHA-256 | `395d342ff54e8bf37274e13b54802fde14632e4ed44e70aaea31f486587156a5` |
| Image SHA-256 | `866da251738e5b42937fbc987fbdb1d06f7bd23c219388c85feab0fbf84b3796` |

The rebuilt archive independently decodes to the planned resource inventory
and group hashes. Every group other than 33 retains its baseline decoded
content and original compressed blocks. Archive and full ISO readback hashes
pass. `tools/build_course_image.py` combines the archive with the executable
rename and the [locale description](locale-tables.md) in one image copy.

## run-gari-001 runtime result

The local image cold-boots into Peak 3. The Peak 1 transport menu shows
**Garibaldi** and the new description, correctly wrapped on two lines.
Selecting it stalls on the transport loading screen before the race spawn.
PCSX2 logs null-address memory faults in code blocks at `0x3a7768`,
`0x3a78cc`, `0x3a78f0` and `0x3a79d0`. A read-only memory capture confirms
that imported terrain coefficients are present, including the last patch.
Thus format/readback success does not establish that the full course is rideable.

Inspection of the loaded MIPS instructions around `0x3a7768` shows a routine
removing an entry from a free list (head at object +16, next at entry +20,
count at object +8) without a null-head check. This is consistent with an
exhausted record pool, but does not establish its capacity or owner. The new
group has 8,847 resources; the largest stock group has 7,111. A separate
byte-memory limit or a geometry-driven allocation limit has not been ruled out.

## run-gari-002: complete terrain loads and the entry rides

Removing all **3,052** original kind-3 prop instances resolves the loading
stall while retaining all **3,885** imported patches. Group 33 now contains
**5,795 resources**, **4,274,485 decoded bytes**, in **71 blocks**. This
reduces both resource count and byte usage, so it does not distinguish their
possible limits. No claim of an unlimited memory budget follows from this test.

| Property | run-gari-002 |
| --- | --- |
| Archive SHA-256 | `c9931dd7ae7c1673a93a459941da70d8906403e9237831ee40beff106bcb4a63` |
| Image SHA-256 | `412f0f98f18b0e5248ea2aab8b0a52bde2d4e0fde03c0eea7d817abd4ac47c7c` |
| Image bytes | 3,118,266,368 |
| Imported coefficient arrays found in EE memory | 3,885 of 3,885 |
| Recorded gameplay | 30 seconds after transport spawn |
| Distinct imported patches with measured contact | 42 |
| Contact samples | 153 |
| Median signed rider-minus-imported-surface Z | −0.586 game units |

The image cold-boots, shows the new name and description, transports to the
usual spawn, and renders the imported banks. A no-input descent enters the
replacement near `(-113851, 14101, -228055)` and ends near
`(-136102, 35236, -252747)`. The rider bails repeatedly on steep walls but
continues downstream; no return to the spawn appears in the recording.

`tools/terrain_contact.py` inverts the bicubic XY surface coordinates for
each ride sample, then compares rider Z with that surface. The 153 reported
samples are within five units of an imported patch and over 20 units from
the closest original surface, or outside its footprint. Both original ARA1
and the entry connector are included. At the first such contact, the rider
is 1.98 units below imported terrain and 462.62 below original terrain.
These observations validate the entry section, not a complete course traversal.

The stock lightmap produces flat/banded snow. Removing props also leaves
dangling references: PCSX2 reports low-address reads in the lookup block at
`0x2b6bc8`, although this test reaches gameplay. Original kind-12 collision,
particle instances, paths, scripts and triggers are still present. A robust
next build must clean up dependencies or retain required instances; the current
image is an experimental freeride prototype, not a finished race.

Reproduce with the same replacement command below plus `--drop-kind 3` and
fresh `run-gari-002` output paths. The tested build is on the share at
`/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-002/`.
Its `launch.command` uses the existing isolated test-002 profile. Saved test
evidence is in its `evidence/` directory; subsequent launches write to
`launch-logs/pcsx2-latest.log` so the original test log is preserved.
`transfer.json` records SHA-256 readback verification for every copied file.
The local build and `local/evidence/run-gari-002/` also remain available;
portable numeric results are in
[full-course-validation.json](full-course-validation.json).

Reproduce the contact measurement from the saved ride and decoded groups:

```sh
python3 tools/terrain_contact.py local/evidence/run-gari-002/ride.jsonl \
  local/builds/run-gari-002/terrain.bin \
  --original local/world-cache/group_033.bin \
  --original local/world-cache/group_006.bin \
  --output local/evidence/run-gari-002/contact-analysis.json
```

## Cleanup and descent investigation

`run-gari-003` removes the 285 original kind-12 collision objects as well as
the 3,052 prop instances. Its dependency pass clears 2,444 removed-instance
references in kind 13 and four in kind 18. It uses the loader's supported
`-1` sentinel only in parsed ID fields, with bounds checks. This eliminates
the previously observed `0x2b6bc8` lookup faults. The next exposed faults are
in the kind-16 script loader, which still binds the removed instance table.

A position-guided descent follows the transformed Tricky main race line
(paths 0–5) for **151.022 seconds**, reaching **99.54%** of its length with no
large position jumps. The original endpoint criterion stopped 1,424 units
short of the final reference point; subsequent tests require 99.9% and a
distance under 500 units. Contact analysis identifies **633** samples on
**193** imported patches, with a median signed height residual of **−0.705**.
This establishes terrain contact through the main descent, but does not
validate alternate routes or a functioning race finish.

The user's missing-terrain report is reproduced during this run. Later
screenshots show the rider over the skybox while measured ground contact
continues. All imported patches use texture 13 and lightmap 144 from template
patch 1673. Lightmap 144 exists only in texture group 32; its distinctive
payload bytes are present in the entry memory capture and absent at the end.
The original spatial tree streams that group out. The fix replaces ARA1's
15-node texture tree with one leaf for group 32 spanning the union of the
original and imported bounds. Other locations' child indices are remapped;
their resource groups retain their original compressed bytes. This keeps
the fallback material available; it does not import Garibaldi's original art.

Reset near the bottom also reproduces an independent failure: the rider
lands near `(-257672, 114001, -384408)`, along the old Snow Jam route and
outside the imported course. `run-gari-004` attempts donor reset-path
conversion but removes the transport start tables. It stalls during arrival,
with null path reads at `0x112250`, `0x26a674` and `0x26ab20`. The experiment
also removes old splines, so it is not a single-variable runtime control.
`run-gari-005` retains those splines but was not booted after inspection found
that the omitted start table contains the freeride spawn and path indices.
Neither build is a playable delivery.

`run-gari-006` preserves the indexed SSX 3 paths and start tables and appends
90 donor AI paths, growing the count from 129 to 219. This also stalls. The
nearest-path routine at `0x26afb8` explains the failure: it stores one float
per path in an 800-byte stack array, then keeps the position pointer at
stack +800. Path 201 overwrites that pointer with a distance value, producing
the observed invalid reads at `0x26a9b0`. This is evidence of a particular
200-entry scratch-array limit, not a complete inventory of engine limits.

The revised converter keeps **129 AI paths and eight track paths**, fills
81 existing eligible slots with transformed donor reset paths, disables 35
unused original reset paths, and preserves the entry connector (AI path 113).
It retains all 14 start records and omits foreign events from the converted
paths. The kind-16 cleanup disables the removed instance binding table and
collision definitions. Retained event rules and spline references still need
separate race-level work.

Local evidence: `local/evidence/run-gari-003/` and
`local/evidence/run-gari-004/`. Numeric results and build hashes belong in
[full-course-validation.json](full-course-validation.json).

### Isolated streaming fix and reset validation

`run-gari-007` retains original paths while applying the collision, binding
and streaming changes. It completes the main route in **152.332 seconds**,
finishing 101 units from the final reference point, with no position jumps.
Screenshots at 30, 90 and 150 seconds show the terrain, including sections
that disappeared in build 003. Four independent 128-byte lightmap probes
are present in the final EE memory capture; all four were absent in build
003's final capture. This supports the streaming diagnosis and fix.

`run-gari-008` adds the reset conversion with the original path counts.
It completes the main route in **161.276 seconds**, including normal Reset
inputs at 25%, 50% and 75%. The samples show the brief freeze and local
position/height snap following each input, then continued downhill travel.
A separate Reset near the endpoint stays on the imported finish-area snow,
around `(-223506, 154643, -375052)` after eight seconds, rather than returning
to Snow Jam's distant route as build 003 did.

Both builds expose further removed-instance lookups in the old gameplay
programs (including `0x30c584`, `0x34fc78`, `0x2ffc64`). The instance-binding
cleanup fixes initialization but does not disable code that later accesses
the removed objects. For the freeride prototype, `--disable-course-scripts`
uses the baseline's identical empty-return LUN programs 0 and 1 as the
replacement for all 238 indexed program slots (235 change). Every program
extent is validated; indices and later resource data stay in place. This
explicitly disables Snow Jam's gameplay programs instead of rewriting
unparsed object-ID literals inside bytecode. Race setup remains future work.

### run-gari-009: tested freeride cleanup

Coverage correction after user feedback: this build retains Snow Jam's
connector spawn and joins Garibaldi after its opening bend. The route tool
silently trimmed the first nine donor race-line points to the placement
anchor, omitting 7,228.715 transformed units (about 2.28% of the full line).
The descent numbers below describe that partial reference. All donor terrain
was imported, but the original opening was not validated in this build.

The final build combines the fixes above and disables the legacy gameplay
programs. It cold-boots and completes the main reference route in **162.496
seconds**, including Reset at 25%, 50% and 75%. The last sample is **266 units**
from the endpoint, at **99.995%** of route length. There are no position jumps
over 5,000 units and **zero logged TLB memory faults**, including the separate
endpoint Reset. This tests the main route, not every alternate branch.

Contact analysis identifies **687** samples on **198** distinct imported
patches, with median signed height residual **−0.616**. All four lightmap
probes remain present at the end, and late screenshots show the snow surface.
After the endpoint Reset, the rider is on imported patch 3790 with a signed
height residual of **−0.469**, around `(-223510, 154671, -375052)`.

| Property | run-gari-009 |
| --- | --- |
| Archive bytes | 112,617,600 |
| Archive SHA-256 | `63868739ae7b1759d6794be160078c9ad0f3a57fd1e0402bc7cc28d572f2d487` |
| Image bytes | 3,118,266,368 |
| Image SHA-256 | `ed0f3ae1a2fd9188ee24ea67b5b4c428540d05366978cc5494e21a3fa0779216` |
| Group 33 decoded bytes / blocks | 3,958,685 / 64 |
| Synthetic unit tests | 48 passed |

The tested build and launcher are in `local/builds/run-gari-009/`; evidence
is in `local/evidence/run-gari-009/`. Its launcher uses the isolated local
course-cleanup profile. The same tested ISO, archive and evidence are published
at `/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-009/`. All **39
files (3,335,114,256 bytes)** have verified readback hashes in `transfer.json`;
the ISO matches the hash above. The share does not support server-side cloning,
so the ISO was streamed from the tested local copy. Its shared Mac launcher
uses the existing isolated test-002 profile. Build 002 is retained separately.

An [Odin 3 test guide](odin-testing.md) is included as `ODIN-TESTING.md`. The
user's likely emulator is NetherSX2; its version and handheld results are
unconfirmed. The ISO needs no Mac launcher on Android. Failed/superseded local
test ISOs 003, 004 and 006 were pruned to recover space; their archives,
manifests and evidence remain.

Reproduce the final archive from the verified local input cache:

```sh
python3 tools/replace_terrain.py local/source/ssx3/BAM.BIG \
  --pbd local/source/tricky/gari.pbd --cache local/world-cache \
  --location ARA1 --template-rid 1673 \
  --source-anchor=-1214.8,-195.5,-768.547891 \
  --target-anchor=-118613.68,15753.8,-228880.14 --yaw 73 --scale .55 \
  --drop-kind 3 --drop-kind 12 --clear-instance-references \
  --clear-script-bindings --disable-course-scripts --pin-texture-group 32 \
  --reset-aip local/gari.aip --output local/builds/run-gari-009
```

For the measured ISO hash, reuse build 002's existing archive extent; this
also preserves its already verified executable and locale changes. The
original image and shared prototype are read-only inputs to this operation.

```sh
python3 tools/relocate_archive.py local/builds/run-gari-002/iso/SSX3-relocated.iso \
  local/builds/run-gari-009/BAM.BIG --output local/builds/run-gari-009/iso \
  --pad DATA/WORLDS/BAM.BIG
python3 tools/course_route.py local/gari.aip local/builds/run-gari-009/experiment.json \
  --from-anchor --output local/builds/run-gari-009/route.json
python3 tools/ride_course.py local/builds/run-gari-009/route.json \
  local/evidence/run-gari-009/descent-01 --wait-spawn --reset-at .25,.5,.75
```

The ride command starts immediately after confirming transport. It sends
ordinary keyboard inputs and reads positions through PINE; it never writes
game memory. `--resume` instead starts a ride from the paused Return menu.

### run-gari-010: restore Garibaldi's opening right turn

The user tested build 009 on the **Odin 3**, initially mistook the stripped
terrain for the old course, then recognized Garibaldi's layout. The missing
textures, buildings, trees and rails make navigation harder. This confirms
handheld loading and riding, not a complete handheld performance or reset test.
The observation about the opening turn exposed the coverage error above.

Build 010 preserves the terrain bytes from 009. It moves the existing `(1, 1)`
freeride start record (index 6) to the transformed origin of donor AI path 0:
`(-112883.224, 18542.350, -227911.316)`, on imported patch 53. Its direction
comes from the first donor segment. The donor opening turns **86.81 degrees
right** before reaching the old placement anchor. Native AI slot 113 and track
slot 1 receive that opening path; their indices and the counts of 129 AI paths,
eight track paths and 14 start records remain stable. The other start records
are unchanged. This avoids the previously observed fixed path-array limit.

`course_route.py` now includes the original opening by default. Historical
partial-route reproduction requires the explicit `--from-anchor` option.
The synthetic regression test places an anchor after a bend and checks that
the default route retains it. Start-table tests check transformed position
and direction, retained indices and other start records, and invalid donor
start references. **49 unit tests pass.**

The new ISO cold-boots at `(-112915.977, 18450.422, -227917.047)`, already
moving along the original opening. The first recorded point is at 0.074% of
the full reference. In the opening, 33 samples contact seven imported patches;
the old join is reached after 7.25 seconds, including a Reset at 1%.

The main descent reaches **99.952%** in **162.929 seconds**, ending **160 units**
from the endpoint. Resets at 1%, 25%, 50% and 75% are followed by continued
travel, with no position jumps over 5,000 units. A separate endpoint Reset
ends on imported patch 3790 with a signed height residual of **−0.500**.
There are **zero logged TLB faults**. Contact analysis identifies 694 samples
on 202 imported patches; the median signed residual is −0.709. All four
lightmap probes remain resident at the end, and late captures show the snow.

| Property | run-gari-010 |
| --- | --- |
| Archive bytes | 112,617,600 |
| Archive SHA-256 | `4ad121f52b9437ef41015b472ce7c0a2923f0d9877be85a98ca021420c5cce7e` |
| Image bytes | 3,118,266,368 |
| Image SHA-256 | `5e53a8151497d80f03d04381648253d4aefa834295d1f1cf52c1c0531af9fcc5` |
| Group 33 decoded bytes / blocks | 3,958,845 / 64 |

Reproduce the archive with the build-009 command, adding
`--relocate-freeride-start` and using a fresh `run-gari-010` output directory.
Create the route without `--from-anchor`. The image uses build 002's existing
archive extent, just as build 009 did; this local build used an APFS clone to
save disk space, then verified every output byte against the planned replacement
ranges and the source hash. The documented streamed relocation command yields
the same bytes.

The tested build is published at
`/Volumes/share/brad/games/ssx3-workbench/builds/run-gari-010/`: **53 files,
3,396,988,198 bytes**, with every readback hash recorded in `transfer.json`.
The copied ISO matches the SHA-256 above. The shared Mac launcher uses the
existing isolated test-002 profile; the Odin needs only the ISO. Build 009
is retained with corrected coverage notes and the user's handheld feedback.

Local artifacts: `local/builds/run-gari-010/`; evidence:
`local/evidence/run-gari-010/`, including `opening-audit.json` and ten-second
ride captures. The original materials and recognizable scenery are the next
priority; this build fixes the start but does not add art or race logic.

## Reproduce

These commands reproduce the original local build:

```sh
python3 tools/replace_terrain.py \
  '/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG' \
  --pbd '/Volumes/share/brad/games/ssx3-workbench/extracted/garibaldi/gari.pbd' \
  --cache local/world-cache --location ARA1 --template-rid 1673 \
  --source-anchor=-1214.8,-195.5,-768.547891 \
  --target-anchor=-118613.68,15753.8,-228880.14 \
  --yaw 73 --scale .55 --output local/builds/run-gari-001

python3 tools/build_course_image.py \
  '/Volumes/share/brad/games/ps2/SSX 3 (USA).iso' \
  local/builds/run-gari-001/BAM.BIG --output local/builds/run-gari-001/iso
```

Use a fresh output directory when rerunning. `--cache` is optional and every
cached decoded group is checked against the baseline hash. `--dry-run`
reports the transform, inventory and bounds without encoding an archive.

## Remaining scope

Textures and lighting still use one original SSX 3 snow patch. The streaming
fix keeps it resident, but repeated lightmap bands remain visible. Old rails,
particles, camera triggers, race-start tables and course-map art are retained;
their replacement requires additional work. The tests follow the main route,
not every alternate branch, and do not establish a finish or a mountain exit.
A complete race with Garibaldi art, correct resets, opponents, finish and
medals remains the M5 gate; importing every terrain patch alone does not meet it.

The next validation is an [Odin 3 freeride test](odin-testing.md) of build 010.
After device feedback and any route fixes, import Garibaldi's original materials
and lighting, then scenery and rails, and finally race starts, opponents,
finish and medals. Build 009 resolves the previously listed object-reference,
old prop-collision, texture-residency and main-route reset problems.

The failed run-gari-001 ISO was removed to recover about 3 GB; its archive,
hash manifests, load-failure memory and screenshots remain available locally.
