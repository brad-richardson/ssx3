# GameCube collision and reset behavior

## Direct terrain reset flag and grounded recovery paths (027 native verified)

The shared profile is now `tricky-gc-to-ssx3-gc-reset-v2`. Tricky surface **0**
means reset. In SSX 3, terrain **flag 0x0002 at offset 10** requests a direct
course-path reset. The surface halfword at offset 8 remains ordinary snow (0),
so the engine reaches the flag check. Garibaldi has 622 authored reset patches.

GXBE69 `80008650`/`80008654` copies patch +10 to rider +684; `8000606C` through
`80006084` checks bit 1 and calls `reset(rider, 0, 1)`. The nonzero reason selects
the course-path reset. This is distinct from the surface-18 wipeout path.

The initial v1/build 023 experiment used surface 18. It passed a normal ride and
targeted late-river/upper-bridge checks and was installed with checksum readback.
A longer collision-development run then exposed repeated recovery onto reset
terrain around 64%, near source `(118505,168347,-182933)`. **V1 is superseded and
must not be used for new imports.** Build 027 passes the replacement native
checks and is installed on the phone with matching checksum readback. The 024 static candidate also
inherits v1 and must not be installed unchanged.

The direct flag alone is insufficient: targeted native check `c33` on build
025's waterfall fixture reproduced the loop with zero stable recoveries.
Donor AI path 26 (target slot 20) crosses an airborne jump over reset terrain.
SSX 3 can select its XY position and fall onto the hazard below. Keep 025/026
off the phone too. The upper-bridge control `c34` rode without a reset loop.

`gamecube_reset_paths.py` now separates reset eligibility from racer geometry.
It samples all donor race routes, rejects absent ground, reset terrain, large
height differences and slopes above 45 degrees, splits at each unsafe gap,
and trims the resulting endpoints. Grounded runs become independent appended
AI records. Original indexed AI geometry/events, track paths, start records
and references remain byte-identical except for disabling original reset
eligibility. The 200-path capacity guard fails before serialization. This is
a conservative sampled check, not a continuous proof of all terrain contact;
native waterfall, river and normal-course checks remain release gates.

Build 027 applies this shared compiler after the v2 surface translation. Both
the original terrain importer and the incremental surface rebuild use it.
The latter verifies the donor AIP hash against the original recipe and rejects
already-compiled input rather than appending duplicate reset networks.

027 native results: normal-course `c35` passed with one stable hazard recovery;
waterfall fixture `c37` passed with two; river fixture `c39` passed with five.
All three had no reset loops or native runtime errors. Upper-bridge `c40` also
passed with no reset, preserving safe riding above the river. The archive has 129 retained indexed AI paths and 68 appended
grounded reset paths (197 total). SHA256:
`a67ec9e518a46fb07c1ed433ecc8c4300dd734e42347b4290e8befcfb3318e7f`.

Repeatable scenario definitions are in
`native/diagnostics/garibaldi-course-checks.json`. The shared
`gamecube_course_fixture.py` verifies source/archive hashes and changes only
race start coordinates/directions. It preserves paths and references, performs
archive readback, and emits a fresh immutable recipe with the actual output
hash. Use another course's scenario data with the same builder and
`gamecube_course_check.py`; do not put course coordinates in either converter.

`gamecube_surfaces.py` checks the NBD header/extents and matches every transformed
float32 coefficient against the corresponding target patch before assigning
behavior. Wrong placement, reordered patches, duplicate IDs and count mismatches
fail. V2 writes surface 0 and ORs reset bit 2, retaining the other collision flags,
rendering state and geometry. Other donor surface types remain explicitly
unmapped; powder, ice, rock, showoff-only and non-colliding terrain still need
separate verified mappings. `--surface-profile template` retains the input
header as a diagnostic control.

```sh
python3 tools/gamecube_surface_import.py \
  --base-build local/builds/gc-gari-023 \
  --nbd local/source/gamecube/tricky/gari.nbd \
  --output local/builds/gc-gari-025
```

The rebuild verifies source hash and course ownership, reads back all changed
records, and requires every other group's compressed blocks to remain identical.
Build 025 SHA256 is
`2c8d1acd7274f0779f7040bb05a3ca7c3a5f3557a3e2dcc5cddf5f5b194aa430`.
Build 023's archived SHA256 is
`dc2883f1c296c005c98f92530e25deef8dbf0b46c6a973cdb96d344f66c2f94b`.

## Runtime evidence, September 12

Pinned GXBE69 DOL SHA256:
`b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce`.
The disassembly under `local/evidence/garibaldi-scenery/ssx3-disasm.txt` shows:

- `801DCAF0`/`801DEED4`: terrain surface halfword at patch +8 enters the contact
  result at +76. `80008698`–`800086B8` copies that to rider +1016.
- `80005ED4`: surface 18 dispatches a wipeout action. Surface 13 is impassable
  powder, not a verified reset surface. The separate surface-table reset flag
  at each 176-byte record's +68 is false in the stock defaults.
- `800333C0`: reset function enters main rider state **9**, through `80028D20`.
  Main state is reached through rider +1816, then +3376; rider +1012 is not the
  main state field.

`gamecube_telemetry.py` reads the first rider through Dolphin MemoryWatcher;
no guest memory is written. Its pointer chains are executable-specific. The
protocol reports changed words only, with implicit initial zero values. State
6 also exists during loading, so an allocated rider does not prove the briefing
is ready. The course check repeats bounded start requests in state 6 after menu
navigation and requires subsequent riding, rather than claiming acceptance
from a button press alone.

Evidence lives under `local/evidence/garibaldi-collision/`:

| Check | Evidence | Result |
| --- | --- | --- |
| Exaggerated all-hazard diagnostic (never installed) | `probe-001-rider-2.jsonl`; native `20260912-222426` | Repeated surface 18 → wipeout → state 9 reset |
| Normal course, only 622 authored reset patches converted | `probe-002-rider.jsonl`; native `20260912-223318` | 382-second run, normal snow and rail contact, natural hazard reset and continued riding |
| Start beneath late bridge at source `(160800, 218550, -235955)` | `river-check/`; native `20260912-224100` | Riverbed surface 18 resets onto ordinary course terrain above, followed by riding; two completed sequences observed |
| Start above the same XY at source Z `-229950` | `bridge-check/`; native `20260912-224613` | Normal riding, no hazard contact or reset; reaches finish from the late-course fixture |

The two targeted fixtures only relocate race start records in an isolated AIP;
production start positions and the reset path network are unchanged. In the
river test, the first reset moves from approximately
`(-207479, 136295, -359377)` to `(-207421, 136678, -354768)` in target space.
The first river test required a manually observed briefing input while the
new harness was being corrected; the upper bridge test uses the corrected
start loop. These are targeted gameplay checks, not full-course acceptance.
The native receipts include archive hashes, fresh screenshots and runtime
error counters. Device installation/readback is recorded separately.

## Remaining collision work

The source inventory is in
`local/evidence/garibaldi-visibility/collision-backlog-audit.json`: 412 collision
models, 56 physics definitions and 3,098 collision-enabled placements. The 44
water objects use physics/effect callbacks, including reset opcode 13. At their
bbox centers, 43 have reset terrain underneath; one has rock. Terrain recovery
does not implement the callbacks or certify every water footprint.

The static object pass needs both kind-12 meshes and kind-16 instance bindings.
The latter dereferences each instance ID from zero through count minus one
without a null check (`80246158`–`80246218`), so IDs must be consecutive. Build
022 removed 51 hidden draw instances and left holes. Any compaction must audit
kind-13 object references, kind-18 NIS references, course ownership and disabled
host programs; do not restore the hidden red start geometry to fill the holes.

The target triangle format has uint8 indices, sequential submeshes and one
bbox for each ten triangles. Source meshes use uint32 indices; partition at
256 vertices while retaining each triangle's normal. Render opcode 0x9B uses
an instance geometry compensation of four, so matching collision vertices must
be divided by four. Native impact tests are still required before enabling this
conversion on the phone.


### Static collision compiler development

`gamecube_collision.py` decodes all 412 source mesh resources, partitions uint32
indices into uint8 target meshes, and generates conservative per-ten-triangle
bounds. It also decodes the 281 stock Snow Jam type-1 triangle resources. Three
stock resources (24, 40, 159) have bbox misses of 1–2 units; the new encoder
requires exact enclosure and does not reproduce those misses.

`gamecube_collision_import.py` currently selects visible, collision-enabled
mode-1 objects with no effect callback: 2,118 instances sharing 42 meshes
(168,584 bytes). It verifies each placement against its source, checks 108,422
records for retained object/NIS references and ownership, compacts surviving
instance IDs, and preserves the rail bindings. Physics, bounds-only shapes and
objects with effect callbacks remain explicit omissions.

The first native candidate 005 failed during loading and was never installed.
Definition +8 was incorrectly interpreted as a model ID. GXBE69 `80245F5C`
loads that field and `80245F84` indexes the **24-byte effect callback table**
with it. No-callback objects must use `FFFFFFFF`, not a model reference.
Candidate 008 corrects this and is undergoing native validation. Candidate 006
inherits the rejected metadata and must not be used for gameplay acceptance.

008/024/026 load and ride without native errors, but impact is still unverified.
The opening-lane rock pair (`c36`/`c38`, fixtures 013/014) did not alter the rider
trajectory. Geometry inspection found the rider below the rock's collision
surface and partly below its instance bounds, so this is inconclusive rather
than a demonstrated collision failure. A lower placement fixture 019 is being
prepared to force an encounter with the front surface.

The native narrow phase at `801DDD08` through `801DE43C` iterates render-model
parts and advances one collision mesh per part. A collision-only partition
cannot introduce another visited part. The static binder now skips multipart
collision resources unless their render topology is supported; its validator
requires matching render/collision part counts. This excludes 12 Garibaldi
instances (four source resources), leaving 2,106 instances / 38 resources in
candidate 028. Old candidates with unmatched parts are superseded. This
limitation is reported explicitly and must not silently discard later meshes.

September 13 winding audit found an independent format mismatch: all 6,092
Tricky collision faces have positive `dot(cross(b-a,c-a), normal)`; all 8,959
stock SSX 3 faces have negative dot products. The v2 encoder reverses each
triangle's second and third index while retaining its authored outward normal.
The reader now rejects positive orientation. All 281 stock type-1 resources
pass that validator (with their documented bounds tolerance); candidate 028
is correctly rejected and must not be installed. Candidate 029 includes this
generic ABI conversion and still requires native impact acceptance.

The lower-rock `c41` run was confounded by an input-generated jump just after
GO. State 6 spans the countdown; the course harness now leaves 15 seconds
between briefing retries to avoid making the next A press an in-race jump.
Coast controls `c42`/`c43` use that corrected input schedule.

The grounded pair confirmed that the old collider did not alter the opening
trajectory. Correct winding is necessary format validation but **did not by
itself produce an impact**: fixture 020 / `c46` on candidate 029 still crossed
the obstacle with state 0 and the same terrain height. Normal-course `c45`
passed with one stable hazard recovery and no native errors. None of the static
collision candidates is ready for phone installation. Next investigate live
instance/property binding, collision-list registration and native contact
dispatch; do not infer physics correctness from a healthy load or screenshots.

Candidate 030 additionally protects the verified reset routes. Its conservative
segment/AABB check omits 49 otherwise eligible instances near reset corridors
(35 target-unit horizontal margin, 150-unit rider height). This is a safe
initial omission policy, not a narrow-phase geometry proof; report the omitted
source IDs and replace it with verified shape clearance as that support matures.
030 is also **unverified for impacts and not installed**. The phone remains 027.

The failed run produced a repeated-error log; its first 2 MiB and final 64 KiB
are retained, with original byte count in `failure-005.json`. The native runner
now kills its owned diagnostic on the first detected invalid access/unknown GPU
command, or a log over 32 MiB, instead of waiting for the full run deadline.
Missing shutdown counters after this stop are a failure, never a passing run.


The recovery gate now requires actual ground contact and three subsequent
hazard-free seconds. Brief aerial state 4/5 after a teleport is not a completed
recovery. Three failed resets close together in time and position fail the check.
Telemetry records the terrain flags and the reset-state course-path request byte
(rider +1816, then +728), in addition to position, main state and surface.
