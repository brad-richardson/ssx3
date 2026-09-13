# GameCube donor rail conversion

`tools/gamecube_splines.py` reads Tricky's linked rail curves and encodes
SSX 3 GameCube kind-8 resources. `tools/gamecube_spline_import.py` integrates
them into a separate experimental scenery build. It does not deploy to a device.

## Build 021 scope

Garibaldi has 169 splines / 542 segments. All source GSF entries are
`(1, 1, 13)`; the MAP names identify fences and metal/showoff rails.
Build 021 replaces Snow Jam's 171 splines / 777 segments, retaining build
020's terrain, scenery and materials. The geometry allocation falls by
33,952 bytes, including resource headers. Other groups decode identically;
all 9,626 non-spline/non-script resources in group 36 are unchanged.

The target script binding uses the explicit diagnostic value `0003000a`,
already present in Snow Jam. This is **not** a verified translation of
Tricky's rail sound/effect style 13. Successful loading and ordinary riding
do not establish rail mounting, grinding, transfers or faithful effects.
The user requested this candidate on iPhone for testing; it was installed
September 12 with a matching archive checksum read back from the device.
Grind and effect acceptance remains open.

Native run `20260912-191826` completed 301.9 seconds including startup and
menus, with zero invalid memory accesses, GPU command errors, JIT fallback
runs or failed code verifications. Eighteen captures continued to the end;
reviewed riding frames show 9%, 19%, 31% and 61% progress. This is a smoke
check, not full-course or grind acceptance. All 139 Python tests pass.
The phone now contains build 021; device gameplay has not been verified by
this deployment. The changed asset hash causes one fresh boot instead of
restoring a checkpoint made against build 020.

## Layout and transform rules

NBD header words 8/9 give spline/segment counts and 23/24/25 delimit their
tables. Spline headers are 40 bytes, followed by up to 15 alignment bytes.
Segments are 128 bytes. GSF header words 17/18 locate the matching 8-byte
state/style table. Walk segment links; storage order is not traversal order.

The target spline header is 48 bytes and each segment is 144 bytes.
**GameCube coefficients start at segment +12.** The reference PS2 reader's
+16 offset is wrong for this target. GXBE69 loader `8024807C` establishes
the stride and rewrites previous/next links at +92/+96 and the parent at
+100. Registration at `80247970` consumes bounds at +104/+116.

| Segment offset | Target GameCube field |
| --- | --- |
| 0–11 | Runtime spatial fields, initialized to zero |
| 12–75 | Four homogeneous power coefficient vectors: cubic to constant |
| 76–91 | Cubic inverse-distance coefficients |
| 92, 96, 100 | Previous, next, parent links; loader fixes pointers |
| 104, 116 | Minimum and maximum bounds |
| 128, 132 | Segment length and cumulative preceding length |
| 136–143 | Opaque target trailer, checked against the supported profile |

Apply the course matrix to all four position coefficients, and translation
only to the constant vector. Compute conservative Bezier control-hull
bounds from the **serialized float32** coefficients, then round them
outward. Using only endpoints loses intermediate humps.

Tricky's inverse-distance fit takes source distance divided by 100;
the target fit takes world distance. Under uniform course scale `s`,
divide cubic/quadratic/linear coefficients by `(100*s)^3`, `(100*s)^2`,
and `100*s`; leave the constant alone. Scale segment/cumulative lengths
by `s`. Reject nonuniform scale and shear, which would invalidate this
reuse of the donor distance fit. The Tricky reference's
`BezierUtil.CalcCoefficients` explicitly fits metre distances; stock target
straight-rail coefficients independently agree with target world units.

The encoder preserves donor approximation error. The largest Garibaldi
inverse-fit endpoint error is about 0.261 in normalized curve parameter;
this predates conversion. Investigate its actual gameplay impact before
replacing the fit algorithm or treating it as an import regression.

## Ownership and rejection rules

The reader rejects malformed extents, nonfinite values, shared/orphan
segments, wrong parents, nonreciprocal links, discontinuous joins and
inconsistent cumulative distances. Open and closed chains are supported.
The encoder rejects unknown source flags/styles and target trailer layouts.

The integrator requires matching scenery/source hashes, a complete dense
host rail table, one course-owned script table, and no spline/script
resources for that track in other groups. Before reusing dense rail IDs,
it checks that every host course program is the known empty-return body
plus zero padding. It replaces the final spline binding table and count
together; unrelated script bytes stay intact. Existing global/resource
capacity validation still runs before compression and after assembly.
Every import also runs the numerical curve/distance audit before assembly
and records its metrics in the build report.

## Reproduce and validate

```sh
python3 tools/gamecube_spline_import.py \
  --base-build local/builds/gc-gari-020 \
  --nbd local/source/gamecube/tricky/gari.nbd \
  --gsf local/source/gamecube/tricky/gari.gsf \
  --output local/builds/<fresh-rail-candidate>
PYTHONPATH=tools python3 -m unittest tests.test_gamecube_splines -v
```

Build 021 archive SHA-256:
`4dff4bb071614ae20e16a43b6d681a69c84298f405f287b95a260250a3d0e60d`.
Input/output hashes and the explicit binding profile are in
`local/builds/gc-gari-021/rails.json`.

Evidence in `local/evidence/garibaldi-scenery/`:

- `rails-conversion-audit-021.json`: 139,294 sampled points, zero bound
  violations, maximum transformed-position error 0.016924 world units,
  maximum inverse-parameter conversion error 1.46e-7.
- `rails-crosscheck-021.json`: decoded archive scope and memory comparison.
- `test-results-021.txt`: complete Python test suite.
- `rails-validation-021.json`: native run, test, compiler and archive hashes,
  reviewed progress and explicit unverified gameplay scope.
- `rails-descent-021.png`, `rails-canyon-021.png`, `rails-route-021.png`:
  reviewed gameplay captures at 19%, 31% and 61% progress.

Next acceptance steps: observe mounting and leaving a straight rail,
travel across a curved multisegment rail, transfers and re-entry after a
reset, and verify target sounds/effects against the original. Exercise
these behaviors on iPhone after its fresh runtime/asset reload.

Follow-up evidence: build 022's native visibility regression run captured
a labeled “50/50 Rail” grind at race time 00:36 / 20%. See
`local/evidence/garibaldi-visibility/grind-50-50-022.png`. Basic grinding is
observed; transfers, curved traversal and effect fidelity remain open.
