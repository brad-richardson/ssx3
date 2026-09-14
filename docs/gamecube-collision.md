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
Candidate 008 corrected this and advanced to native validation. Candidate 006
inherits the rejected metadata and must not be used for gameplay acceptance.

The failed 005 run produced a repeated-error log; its first 2 MiB and final
64 KiB are retained, with original byte count in `failure-005.json`. The native
runner now kills its owned diagnostic on the first detected invalid access or
unknown GPU command, or a log over 32 MiB. Missing shutdown counters after this
stop are a failure, never a passing run.

008/024/026 load and ride without native errors, but impact is still unverified.
The opening-lane rock pair (`c36`/`c38`, fixtures 013/014) did not alter the rider
trajectory. Geometry inspection found the rider below the rock's collision
surface and partly below its instance bounds, so this is inconclusive rather
than a demonstrated collision failure. Lower placement fixture 019 was
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
passed with one stable hazard recovery and no native errors. These findings
motivated the live registration/contact audit below; a healthy load or
screenshots alone do not establish collision correctness.

Candidate 030 additionally protects the verified reset routes. Its conservative
segment/AABB check omits 49 otherwise eligible instances near reset corridors
(35 target-unit horizontal margin, 150-unit rider height). This is a safe
initial omission policy, not a narrow-phase geometry proof; report the omitted
source IDs and replace it with verified shape clearance as that support matures.
030 lacked impact evidence and was not installed; candidate 031 below
supersedes its transform representation. The phone remains 027.

### Live registration and rigid-transform audit

The isolated `gamecube_collision_trace.py` diagnostic copies three generated
AOT chunks and inserts read-only observations at actual instruction labels.
This covers direct same-chunk branches that do not pass through the runtime's
dispatch hook. It preserves the original module, generated sources, guest
state and course data; its bounded logs are correctness evidence, not a speed
benchmark. Select a packed instance ID with `SSX_COLLISION_INSTANCE`.

September 13 check `c47registration`, using the existing lowered-rock fixture
020, confirms that registration is working: source rock 41 / target instance
600 has flags `0x00210023`, a valid kind-1 property and one-part collision mesh,
and reaches both broad and narrow phase. All 881 completed narrow-phase calls
returned zero contacts. The run passed the course/runtime checks, with zero
invalid accesses, GPU command errors, unknown guest instructions or code
verification failures. The receipt is `local/reports/native-runs/20260913-182621.json`.

An independent ABI error explains why valid registration is not sufficient:
the scenery importer embeds uniform scale in the instance's matrix basis and
leaves the separate float at +124 equal to 1. The rock's basis has axis length
0.55. GXBE69 `801DDF98` calls `801C651C`, which inverts by transposing the basis;
that requires orthonormal axes. `801DDFA4` then scales the query separately by
the reciprocal of instance +124. The renderer also uses the separate scalar
at `8021C4C8`. The old representation therefore draws at the right size while
transforming collision queries into the wrong local coordinates.

The candidate compiler profile `tricky-gc-static-rigid-transform-v3` factors
uniform scale into +124 and normalizes collidable instance bases. It rejects
nonuniform/sheared transforms as explicit omissions and validates orthonormal
bases when reading bindings. Tests preserve forward render coordinates while
checking that the engine's rigid inverse recovers the original local point.
Canonical candidate 031 differs from 030 only in the basis/scalar bytes of
2,059 instances; effective basis coefficients differ by at most `5.96e-8`
after float32 rounding. Geometry, properties, bounds, paths, rail bindings and
the 49 reset-corridor omissions are unchanged. Candidate SHA256:
`c1e1c07b117d2379bd392231e649759a46d0c31ffaa389dba2b0ad07060df896`.

Matched fixture 021 applies only this transform correction to fixture 020
without moving its rock or changing the start. Native check `c48rigid` now
produces 22 positive narrow-phase returns (38 summed contact counts, including
repeated contacts across frames), versus zero in the control. The rider enters
reaction state 8 at 132.29 seconds near the rock, returns to normal state 0 at
136.29 seconds, and continues riding. A later terrain hazard reset completes
with ground contact and subsequent hazard-free continuation; the run ends in
ordinary riding with no reset loop or native errors. The receipt is
`local/reports/native-runs/20260913-183224.json`; the paired summary is
`local/evidence/garibaldi-collision/rigid-native-comparison.json`.

The transform repair therefore has native impact evidence. Canonical 031's
400-second normal-course check `c49rigidcourse` passed runtime checks and
continued riding through a crash/reset at 307.87 seconds, with stable ground
recovery at 312.09 seconds and no loop. Its strict `--expect-reset` gate did
**not** pass: that reset was on terrain flags 73, so no terrain-hazard reset was
observed. The receipt is `local/reports/native-runs/20260913-183644.json`.
Concurrent build work slowed this correctness run; its wall-clock duration
does not establish equivalent course coverage or a performance comparison.
Targeted waterfall fixture 022 retains 031's geometry and reset paths and
closes that missing gate: `c50rigidwaterfall` passed its 240-second check with
one flags-75 terrain hazard at 128.82 seconds, ground recovery at 131.01 seconds,
and over 100 further seconds of riding without a reset loop. The production,
uninstrumented native module reported zero runtime/code-verification failures.
Receipt: `local/reports/native-runs/20260913-184742.json`. Matching river fixture
023 / `c51rigidriver` passed its 240-second check with four completed hazard
recoveries, no reset loops and zero failures in the existing native runtime
gates. Receipt: `local/reports/native-runs/20260913-185640.json`.

The river log also contains 48 known MemoryWatcher startup messages about
unmapped reads of the rider pointer `803da1f8` during exception handlers. The
existing runtime tests explicitly distinguish these from guest invalid accesses.
The watcher currently calls `MMU::HostRead` before checking the result; its
failed hardware-read path can raise a PI interrupt. **High-priority observer
TODO:** replace this path with checked `HostTryRead` access so the observer does
not disturb the guest during startup. These warnings are recorded separately
in the paired evidence summary. No runtime/platform patch changed in this audit.

**031 remains experimental and is not installed; phone assets remain 027.**
One targeted obstacle encounter does not certify every newly solid object or
the complete course's checkpoint/finish progression.

The recovery gate now requires actual ground contact and three subsequent
hazard-free seconds. Brief aerial state 4/5 after a teleport is not a completed
recovery. Three failed resets close together in time and position fail the check.
Telemetry records the terrain flags and the reset-state course-path request byte
(rider +1816, then +728), in addition to position, main state and surface.

### Broader static encounters, September 14

Three new 180-second fixtures start near original obstacles in canonical 031.
Only the six race starts move; obstacle placement, collider geometry, rigid
transforms, reset paths and all other course resources stay unchanged. The
definitions are `static-tree`, `static-rock` and `static-sign` in
`native/diagnostics/garibaldi-course-checks.json`. Source IDs bind the observations
to the candidate's enabled-instance map instead of relying on model names.

| Fixture | Source / target instance | Narrow-phase returns / positive returns | Result |
| --- | --- | --- | --- |
| Original bushy-tree trunk | 9 / 767 | 0 / 0 | Registered and visited by broad phase; rider slid past it. Contact remains unverified. |
| Second original rock | 22 / 599 | 2,437 / 44 | Engine contact established; 54 summed contacts, including repeated frames. |
| Directional sign stand | 79 / 2,216 | 805 / 8 | Engine contact established; 23 summed contacts, including repeated frames. |

All three runs passed the native runtime gates with zero invalid accesses,
GPU command errors, unknown instructions, JIT fallback runs or failed chunk
checks, and no detected reset loops. Tree and rock runs each completed a terrain
hazard recovery. Sign continued riding but did not observe a completed terrain
hazard recovery; it was not a required gate for that scenario.

**These contacts are not yet tied to the player's query.** The read-only trace
can also observe opponents. Neither successful contact run captured a player
reaction state 8 within the selected object's expanded bounds. That does not
prove the player failed to collide (not every contact causes that state), but
does prevent claiming a player-only impact from these counters. The next
validation step is a steered player approach and explicit query ownership,
followed by route/bridge clearance checks. 031 remains experimental; phone
assets remain 027. No importer or physics behavior changed in this batch.

`tools/gamecube_collision_check.py` now checks actual archive/recipe/runtime
identity, native execution/fault evidence, selected instance registration and
positive contact returns. A clean ride with no contact is reported with a
nonzero exit status. Trace overflow is rejected. Player spatial observations
are reported separately from object-contact evidence. Four focused regressions
cover false acceptance from missing execution, wrong worlds/instances, absent
contacts and truncated traces.

Reproduce with a fresh profile and output (long profile names exceed the
platform's Unix socket path limit):

```sh
python3 tools/gamecube_course_fixture.py \
  --base-build local/builds/gc-gari-031 \
  --scenarios native/diagnostics/garibaldi-course-checks.json \
  --scenario static-rock --output local/builds/gc-gari-collision-rock-review
# Create a corresponding extracted game root using that BAM.BIG, then use
# the isolated collision-trace module with the normal course checker.
SSX_COLLISION_INSTANCE=0x08000257 python3 tools/gamecube_course_check.py \
  --game local/game/gc-gari-collision-rock-review --profile cb-rock-review \
  --output local/research/collision-batch/rock-review --seconds 180 \
  --module local/evidence/garibaldi-collision/registration-player-001/build/gGXBE69_recomp.dylib
python3 tools/gamecube_collision_check.py \
  --run local/research/collision-batch/rock-review \
  --build local/builds/gc-gari-collision-rock-review --source-instance 22 \
  --output local/research/collision-batch/rock-review/contact-report.json
```

Local reports (including archive, module, log and rider-trace hashes) are under
`local/research/collision-batch/{tree-002,rock-001,sign-001}/contact-report.json`.
Runtime receipts are `20260914-001125`, `20260914-001526` and `20260914-001907`
under `local/reports/native-runs/`. The initial `tree-001` attempt failed before
launch because its profile socket path was too long; it supplies no gameplay
evidence. All three accepted runtime runs used the same existing read-only
diagnostic module, SHA-256
`a8d6b3b1f7be2fac20385432677892335cfecf18d6c74e1f7b3f655cf0a0fe6e`.
