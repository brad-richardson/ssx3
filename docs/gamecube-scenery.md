# GameCube scenery conversion

The GameCube Tricky NBD is not the PS2 PBD model format. The checked reader
is `tools/gamecube_scenery.py`; it validates relative pointers, strip extents,
vertex indices, parent order and finite transforms before accepting a course.

Garibaldi source audit (2026-09-12): 648 prefabs, 3,393 instances, 824 meshes,
13,570 position entries, 6,785 normal entries and 3,922 UV entries. Twenty
models (269–288) contain animation. Evidence is under
`local/evidence/garibaldi-scenery/`; source bytes remain local.

## Verified source layout

The 160-byte big-endian NBD header gives model pointers at word 26, model
base at word 27, display-list base at word 33, position array at word 34,
UV array at word 35 and normal array at word 36. Instance records are 140
bytes with the matrix at zero, model ID at 64 and bounds at 76/88.

Each model has a 28-byte header and 24-byte object records. Object geometry,
local-matrix and animation pointers are relative to the object record.
Geometry has a 44-byte header; each mesh pointer is relative to its own
pointer word, not the start of the table. Mesh entries are 16 bytes:
length, material-block slot, display-list offset and display-list length.

Strips contain three big-endian 16-bit indices per vertex, in **position,
normal, UV** order. Ordinary `0x9a` strips use positions in quarter units;
Garibaldi's bridge model 184 uses `0x9b` with whole-unit positions. Ignoring
that distinction shrinks the bridge by four. Normals use a denominator of
16,384 and UVs 4,096. Preserve the opcode until conversion chooses the
corresponding target scale.

## Target format under validation

SSX 3 GameCube stores shared arrays in world resource kinds 24–27:
RGB565 colors, signed-16 positions, float normals and signed-16 UVs. Kind
23 contains three references in **position, UV, normal** order (confirmed by
GXBE69 loader `802467E4`, which resolves kinds 25, 27 and 26). The stock
Snow Jam references happen to use zero for both UVs and normals; those
examples alone cannot establish their order. Kind-2
models reference that buffer group; kind-3 instances reference a color
buffer plus a byte offset. These arrays are separate from the terrain's
textures and lightmaps.

Target instance matrices begin at byte 8. Instance ID, spatial-page reference
and model ID are at 112, 116 and 120; color-buffer reference and byte offset
are at 152 and 156. Copying the PS2 matrix offset produces invalid transforms.
Target mesh strips use position-u16, normal-u8, color-u16, UV-u16. A normal
palette therefore needs at most 256 entries per target buffer group; do not
truncate donor normal indices. One Garibaldi prefab exceeds that limit and
needs partitioning.

Both global and location capacity tables have **28 entries**, not 24.
GXBE69's constructor `8024A9F8` reads four groups of seven halfwords. The
last four location entries exactly match the stock color/position/normal/UV
buffer counts (3/2/1/1 for Snow Jam). Probe 002 added buffers without growing
these tables and produced invalid pointers (`0x02262624`, decoded from
uninitialized packed pointer bytes). `update_group_index` now grows kinds
14–27 while preserving existing reservations; `assemble` checks changed
records before compression. `validate_resource_capacities` audits every
resource, including kinds absent from the group counters. It passes all
104,200 resources in build 013 and rejects probe 002 at its first new
position buffer; corrected probe 003 passes 104,619 resources.

Probe 004 imports start gate, cover, lights and two tree prefabs (390
placements). Its 300-second gameplay run (`20260912-171854`) completes with
zero invalid accesses, zero failed code verification and zero JIT fallback.
The empty kind-22 bank must remain terminal: appending instances after it
caused the loader to call its bank handler with a null pointer. Moving the
new resources ahead of that existing terminal record removes the warning.

The reusable experimental writer is `tools/gamecube_scenery_import.py`.
It imports 621 supported static prefabs and 3,290 placements, reports every
omitted model and refuses explicitly requested unsupported models. Twenty
animated prefabs, multipart/local-matrix prefabs and the oversized normal
palette remain outside this first pass. Its vertex colors and material
flags are diagnostic controls, not a verified donor lighting conversion.
Grind splines and object collision are not included.

A subsequent local candidate, build 021, adds the donor's 169 rail curves
with reusable topology, transform and distance checks. Native riding passes;
mounting, transfers and effect mapping remain unverified. See
[rail conversion and evidence](gamecube-rails.md). Build 021 subsequently
replaced build 020 on the phone at the user's request, with checksum readback.

The full additive probe exhausted the location allocator. Candidate 015
reclaims 1,125,758 bytes of unused host models and arrays. New IDs remain
above the retired IDs so stale host references cannot select donor objects.
The importer checks retained instances, models and buffer groups before
reclamation. It preserves host materials and the other resource families.
Location capacity is at least the highest RID plus one, even when reclamation
leaves holes; resource count alone is insufficient.
Reservations also survive subsequent updates to sibling groups. Recounting
the texture page after the model group previously shrank its model capacity
back to the resource count; the multi-group assembly regression now covers it.

Candidate 015 still stalled at the loading screen; dense-ID probe 016 stalled
as well. The same 015 archive stalls in the independent JIT player, so this
is not specific to the iPhone's AOT execution. Neither is accepted for
deployment. FPS fields remain cached while no new frame is produced; the
native launch gate now rejects long visual runs whose newest screenshot is
over 60 seconds old. Probe 016 is rejected by that gate.

The original world stream orders kinds as
`25,26,27,24,23,0,6,7,2,3,4,5,1,8,12,11,13,15,17,20,14,16,18,21,22`.
Buffers precede a contiguous region of geometry, instances and terrain;
metadata follows it. The experimental writer now preserves those sections
instead of interleaving buffers with materials or appending instances after
metadata. Probe 017 tests this ordering independently of the content changes;
it still stalls, so ordering alone does not explain that failure.

RAM snapshots at 150 and 210 seconds identify the remaining load stall:
group 36 has completed its geometry, but texture group 31 stops at 181 of
191 records, leaving new texture IDs 881–890 unresolved. The location pool
still has four free 128 KiB blocks. New texture allocations approach the end
of the 24 MiB address space. This is a separate residency budget from the
location geometry pool; simply counting total decoded archive bytes misses it.
The snapshots and decoded counters are under
`local/evidence/garibaldi-scenery/memory-comparison.json`.

Probe 018 removes 72 obsolete host image copies from the replaced geometry
page, reclaiming 676,320 serialized bytes without changing donor image data,
global IDs or copies on other pages. It reaches riding. The reusable
`prune_geometry_texture_page` follows all terrain page bindings and instance
model/material references, including users in other groups. It reproduces
probe 018's page exactly from 7,175 surviving geometry users. This operation
is restricted to replaced static geometry pages; it is not a general garbage
collector for character, effect or scripted image banks.

**Probe 018 is not deployable:** riding exposes a malformed GPU command and
incorrect scenery rendering. The native gate rejects unknown FIFO opcodes
even if no invalid memory access follows them. Probe 019 separately tests
neutral geometry flags and completes 300 seconds with zero invalid accesses,
zero FIFO errors, zero failed code verification, zero JIT fallback and fresh
riding captures (`20260912-181829`). An isolated opcode diagnostic captures
the first bad display list and RAM without modifying the production runtime:
the start of model RID 986's display list changes from `9a000305` on disk to
`ffff9a02` before GPU decoding. Clearing copied donor geometry bit 0 prevents
the failure in the same replay. The precise target flag's behavior still
needs decoding; it must not be treated as a portable donor flag.

The writer now explicitly selects target geometry flags 0 for this static
profile. This is not a complete donor dynamic-lighting conversion. Native
probe 019's world hash is
`51109ea4db9349d6134739a7400b1cc9784c2214a40978c0087b55dbe7aa2af9`.

Reproduce the candidate from terrain build 013 in a fresh output directory:

```sh
python3 tools/gamecube_scenery_import.py \
  --base-build local/builds/gc-gari-013 \
  --nbd local/source/gamecube/tricky/gari.nbd \
  --gsf local/source/gamecube/tricky/gari.gsf \
  --textures local/source/gamecube/tricky/gari.gsh \
  --reclaim-host-models --reclaim-geometry-textures \
  --output local/builds/gc-gari-scenery-review
```

`scenery.json` records imported and omitted models, reclaimed bytes, source
and archive hashes, and validation scope. `experiment.json` retains the
terrain transform and recipe. Native run receipts also include the world
archive hash, avoiding confusion between an app update and an asset update.

## Visibility and the temporary start gate (build 022)

The iPhone report on build 021 showed a large red obstruction near 1%
progress. Two missing gameplay semantics were found: 48 imported instances
are initially hidden, and the donor has a `NoCountDown` visibility program
that hides its start gate. Rendering every instance permanently exposes
trigger meshes and leaves the countdown structure across the race. The exact
donor timing of that visibility program was not traced (see the follow-up below).

The scenery CLI now requires the matching `.gsf`. Its 24-byte object
properties have visibility/collision flags at **+8** and U2 at +10 on
GameCube, the reverse of the PS2 reference reader. Bit 0 controls initial
visibility; bit 5 enables player collision. Keep hidden instances' metadata
for the later collision/effect compiler, but omit their draw instances.

The static profile `tricky-gc-post-countdown-v1` resolves the donor's authored
`NoCountDown` function. GameCube effect commands carry their own byte length.
The checked evaluator supports function calls, instance effect calls and
the hide command `(main=0, size=16, subtype=5, mode=2)`. It rejects unknown
commands, invalid references and cycles instead of guessing. Garibaldi's
function calls `HideStartGate`, which hides source instances 136, 137 and
138. These IDs are discovered from source data, not hard-coded exclusions.

The current static race profile bakes that no-countdown state: SSX 3's
countdown HUD remains, but the temporary Tricky gate is absent even before
the start. Timed donor gate animation still requires a gameplay script pass.
This does not claim support for other scripted visibility, such as switching
between Race and Showoff props or breakable-object states.

Build 022 is derived from immutable 021. Its migration verifies all 3,290
legacy placements byte-for-byte against the source transform before removing
51 draw instances. Surviving IDs and all other resource bodies stay intact;
unused model/texture resources remain available. The normal compiler applies
the same visibility rules to future full imports. Evidence and the checked
migration script are in `local/evidence/garibaldi-visibility/`.
The reviewed `start-clear-022.png` capture at race time 00:04 shows the
opening without the red obstruction. `grind-50-50-022.png` at 00:36 / 20%
shows the rider on a rail with the game's “50/50 Rail” label. This confirms
one basic grind, not full rail/transfer or sound/effect acceptance.
All 143 tests pass. Native run `20260912-212536` completed 302.1 seconds
including startup/menus, with 18 continuing captures and zero invalid memory
accesses, GPU command errors, JIT fallback runs or failed code verification.
Build 022 SHA-256 is
`e810cf47cef91ad34e1a3029440b7bbfb0ccb99c8d5f6d53c582d25929deb54f`.
Build 022 is installed on the iPhone; the archive read back from the device
matches this SHA-256. The user confirmed the red start-area obstruction is
fixed on iPhone. The validation receipt is
`local/evidence/garibaldi-visibility/validation-022.json`.

### Start-gate audit (September 13, assets 027)

The missing gate does **not** require the general animated-prefab importer.
The donor `local/source/gamecube/tricky/gari.map` names models 30, 58 and 59
`Mdl_StartGate_1000`, `Mdl_StartGate_Cover_1000` and `Mdl_StartLights_1000`
(lines 54, 82–83; instance rows 4730–4732). The checked NBD reader finds one
part, no animation and no local matrix for all three. Their instances
136/137/138 were removed explicitly by build 022's visibility pass, at target
RIDs 2051/2444/2445; their models remain in the 027 and 031 recipes.

The donor GSF contains this small program, separate from mesh animation:

- `StartCountDown` (function 17) calls `CountDownStart` (0), which invokes
  effects 14–18 on lights instance 138, with waits of 1.0, 0.5, 0.5 and 0.5
  seconds. Effect 14 is main 0/subtype 11, the texture-flip effect in the
  reference reader; effects 15–18 are main 9 with `(2, 1.0…4.0)` parameters.
  The latter command's native meaning remains unverified.
- `EndCountDown` (18) is empty. `NoCountDown` (19) calls `HideStartGate` (1),
  hiding all three instances. Thus the static profile name “post-countdown”
  does not establish when the donor actually hides the gate.

Lights material 66 uses image 69, and NBD flipbook table 5 contains images
69–73. The original audit suggested moving the halfword reader from `+68`
to `+70`, because the latter matches all 16 non-default flipbooks. Native
loader inspection on September 14 establishes the actual field: a **signed
32-bit index at +68**. GSTE69 `8012e424` loads that word, handles `-1`, indexes
the flipbook pointer table and replaces the word with a pointer. The material
resolver at `8012e454` advances by 72 bytes and calls that virtual fixup; the
getter at `8012dffc` independently uses the same stride. Reading `+70` only
works accidentally for small indices. The checked reader now reads the full
word and validates flipbook extents, frame IDs and material references.
The 027/031 texture maps contain image 69, but not 70–73; restoring instances
alone cannot restore the light sequence.

The shortest next spike is to validate that material field and the countdown
dispatch, then bind these three supported models and their five light frames
to the target's existing start event. SSX 3 has `StartgateOpen` at
`0x802e32bc`: `0x801015b4` materializes it, calls the hash routine at
`0x801015bc`, and dispatches through `0x801016c0` at `0x801015c8` (existing
`local/evidence/garibaldi-scenery/ssx3-disasm.txt:260342`). This is a static
trace candidate, not an established patch point. The imported course's 235
LUN programs are currently replaced by empty returns, so retain those guards
and add a narrow verified binding instead of reenabling the old course scripts.
Acceptance needs the original countdown appearance, unobstructed GO, and a
correct second countdown after restart; phone assets remain unchanged.

### Countdown staging and event boundary (September 14)

`tools/gamecube_startgate.py` builds a separate **hidden asset staging**
candidate from 031. It reuses retained static models, restores only the source
instances found through the authored `NoCountDown` program, adds their missing
flipbook images, and appends an explicitly hidden, non-colliding definition.
Existing instance ordinals, definitions, spline bindings and all empty LUN
programs are preserved. Its `startgate.json` keeps ownership separate from the
verified racing scenery map. This is not a countdown implementation or a
candidate for phone installation.

Candidate `local/builds/gc-gari-startgate-assets-001` has 108,467 validated
resources and SHA-256
`dd8c6d8a9f7ab19abeffe899f4c34f1e97d13879b893e9d1f2b93fecbcce2900`.
Compared with 031, the two changed groups retain 9,901 existing resource
bodies byte-for-byte. Changes are four 2,080-byte images (RIDs 891–894),
three 160-byte instances (3239–3241), and a 36-byte extension to the script
binding record. Target models 993/1019/1020 remain unchanged. The complete
countdown frames are present, but no frame sequence executes.

```sh
python3 tools/gamecube_startgate.py \
  --base-build local/builds/gc-gari-031 \
  --nbd local/source/gamecube/tricky/gari.nbd \
  --gsf local/source/gamecube/tricky/gari.gsf \
  --textures local/source/gamecube/tricky/gari.gsh \
  --output local/builds/gc-gari-startgate-assets-review
```

The target also dispatches `StartlightBegin` (hash `0x0ebf88fe`) at
`80101804`; `StartgateOpen` is hash `0x0dfb527e`. The stock Snow Jam LUN
program 3 registers the latter using an embedded closure. Its opening closure
calls builtin 3 (`801921f0`, allocating `AnimObject`) on the stock gates.
Builtin 2 (`8019193c`) includes `DeadNode`/`RestoreNode` lifecycle commands and
special guards; it must not be substituted as an assumed reversible hide/show
operation. A fresh scoped initializer also needs the correct course table and
restart ownership. No original course scripts have been reenabled.

`tools/gamecube_startgate_trace.py` builds a read-only observer from four copied
generated chunks, leaving the original module and runtime unchanged. It
observes countdown dispatch, named-event lookup/invocation and the staged
instances' runtime binding flags, including same-chunk AOT jumps. Static source
and target excerpts, source program commands and hashes are retained under
`local/research/startgate/`. The next binding decision requires observed event
timing and a verified reversible visibility/material operation; allocation
names alone do not establish that behavior.
The observer caps each copied translation unit at 1,000 events; its summarizer
marks any unit reaching that count as truncated. Missing later events from a
capped unit are unknown, not evidence that a callback is absent.

### The reversible visibility operation is a course-script definition (September 14)

Reading the candidate's own course-script binding record settles what a
countdown handler has to touch, without reverse-engineering an engine routine.
The record holds 40 instance definitions of 28 bytes each, and every one of the
3,242 instance ordinals selects one of them:

| Definition shape | Word 0 | Word 1 | Words 2-3 | Word 4 | Word 6 | Definitions | Instances |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| Visible, non-colliding scenery | 0 | `0x00010000` | none/none | 1e30 | `0x0000ffff` | 1 | 1,180 |
| Visible, colliding | 1 | `0x00210000` | none/`0x080000xx` | 1e30 | `0x0003ffff` | 38 | 2,059 |
| Staged countdown (definition 39) | 0 | `0x00000000` | none/none | 0 | `0x00000000` | 1 | 3 |

Word 1 bit 16 draws and bit 21 collides. That is the donor GSF's own bit 0 and
bit 5 shifted left by 16, which is why `instance_gameplay` reads the same two
properties on the source side; the agreement is what makes the reading more
than a guess. Word 4 is a draw distance and word 6 is a packed pair of 16-bit
sentinels whose meaning is not established, so neither is synthesized.

This matters because definition 39 is used by the three staged countdown
instances **and nothing else**. Toggling one 28-byte record therefore shows or
hides exactly the gate and lights, reversibly, with no effect on any other
scenery and no engine call. The probe already reads this word: it is the
`property_flags` field, observed 0, at `instance+136` then `+4`.

This supersedes the earlier search for a callable hide/show routine. Builtin 2
(`8019193c`) is still not a safe substitute — its `DeadNode`/`RestoreNode`
lifecycle commands and guards remain unmodelled — but a handler no longer needs
it for visibility.

`gamecube_startgate.py --visible` stages the countdown models permanently drawn
by copying the course's own visible non-colliding definition verbatim, so
placement and the visibility bit can be checked before any binding exists.
Candidate `local/builds/gc-gari-startgate-visible-001` (SHA-256
`1b12206c7658cc5fe5222f95b461fd61739ae264ddefc7a3b8713b5446b047ef`, 108,467
validated resources) differs from the hidden candidate by seven bytes, all
inside definition 39: the visibility bit, the draw distance and the low half of
the sentinel pair. Every other resource in both changed groups is identical.

This is a static always-visible check. It is not a countdown, and it does not
establish timing, the flipbook sequence, restart behaviour or the gate's
authored appearance.

#### Result: the gate draws, and the control run proves it (September 14)

Two 185-second automated checks, identical except for the archive, both clean
(exit 0, no fault, zero invalid accesses, zero GPU command errors, zero
fallback JIT runs, module loaded):

| Run | Archive | Profile | Receipt |
| --- | --- | --- | --- |
| Visible | `1b12206c…` | `sg-vis2` | `20260914-125550.json` |
| Hidden (control) | `dd8c6d8a…` | `sg-hid2` | `20260914-125957.json` |

At the same countdown number and camera, the visible run shows a glass and
metal canopy over the start, six starting stalls with rails between the
riders, and a countdown light column beside the engine's own "2". The control
run shows riders standing on open snow with none of it. Riding after the start
is unaffected. Screenshots, hashes and the receipt references are in
`local/research/startgate/visibility-evidence/report.json`.

The only difference between the two archives is definition 39's visibility
bit, draw distance and sentinel low half, so this isolates the visibility
operation itself.

Not established by this: countdown timing, the flipbook frame sequence,
restart behaviour, the gate's authored appearance or materials, and the gate
opening animation. The staging is permanently drawn; a handler still has to
drive it.

Capturing this needed a finer screenshot cadence than the fixed 15 seconds,
which can miss a countdown entirely. `SSX3_SCREENSHOT_SECONDS` now sets it
(1-3600, default 15, unchanged when unset).

### Observed countdown events (September 14, staged candidate)

The first observer run rode the hidden staging candidate for 841 samples with
no runtime fault, and its retained lines are summarized in
`local/research/startgate/event-probe-001.json` (log
`run-assets-003-runtime.log`). Because the observer's lines go to the runtime's
own log rather than the check's `observer.log`, read them with
`python3 tools/gamecube_startgate_trace.py --summarize RUNTIME_LOG`.

| Observation | Result |
| --- | --- |
| `StartlightBegin` dispatches | 1, hash `0x0ebf88fe` as documented |
| `StartgateOpen` dispatches | 1, hash `0x0dfb527e` as documented |
| Interval between them | 3.719 s of guest time (150,611,679 ticks at 40.5 MHz) |
| Named lookup for each hash | Found, course index 8, value type 0 |
| Staged instances bound | 3239, 3240, 3241; flags 2, property flags 0 |
| Translation units reaching the 1,000-event cap | None |

This establishes the dispatch side of the binding: the imported course really
does raise both countdown events, once each, about 3.72 seconds apart, and the
three staged models are live objects by then. It does **not** establish a
handler. Both named lookups return value type 0 rather than the callback type
5, which is what the emptied LUN programs should produce — so the lookup is the
place a narrow binding would attach, and nothing currently runs there.

Because no translation unit was truncated, the absence of further events within
these four hooks is meaningful. It says nothing about code outside them: the
light material fixup, the visibility operation and restart ownership are all
unobserved. The 3.72 s figure is one run of one automated start; it is not a
verified countdown length, and the donor's authored waits total 2.5 s, so the
remaining time is unattributed.

Next: observe a restart to see whether both events dispatch again, and identify
a reversible visibility/material operation before writing any handler.

## Collision and river reset follow-up

The river screenshot at 89% is a separate, still-open gameplay issue.
Garibaldi has 412 collision-model definitions, 56 physics definitions and
3,098 collision-enabled instances, including 44 river-water placements.
The water uses physics-mode objects with collision callbacks; neither that
collision/effect graph nor ordinary tree/fence collisions is compiled yet.
`collision-backlog-audit.json` retains each water instance's source identity,
bounds, physics index and callback slots for the next pass.
An offline nearest-terrain check at the water bounding-box centers finds
source reset surface type 0 at 43 of the 44 placements (type 9 at one).
This narrows the terrain reset investigation; it is not live trigger proof.

Terrain behavior is also incomplete: the NBD surface field is at +360,
while the importer still copies a common target patch header. Source reset,
snow, powder, rock, ice and non-colliding surfaces must be mapped to verified
target semantics. Do not copy Tricky's enum numerically into SSX 3 or use a
single height cutoff under bridges: both can reset riders on valid routes.

Build **gc-gari-020** is the first shared-compiler static scenery delivery:
101,486,976 bytes, SHA-256
`ec8db19ea04957a34845133bb1660735d59e2fe98649589ea496640dcf449c2f`.
All decoded groups match passing probe 019. Only location-table reservations
differ (21 additional image slots retained by the multi-group capacity fix).
The complete 108,475-resource capacity audit and 130 tests pass. The archive
also passes its own 300-second native ride (`20260912-183500`): zero invalid
accesses, zero GPU command errors, zero failed code verification, zero JIT
fallback and 18 fresh screenshots. Start-area structures and downhill fences,
trees and signs are visible in the captured gameplay.
The archive
was installed on the iPhone and copied back with a matching checksum.
iOS rejected the test launch because the device was locked, so phone riding
with this scenery remains unverified. The installed app already includes
the persistent Menu/Resume/Full Reset work. Local delivery receipts are in
`local/evidence/garibaldi-scenery/release-020.json`.
