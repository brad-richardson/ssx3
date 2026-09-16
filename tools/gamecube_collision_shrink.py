#!/usr/bin/env python3
"""Measure imported colliders against their art, and scale them if asked.

Written to chase a report that Garibaldi's trees and buildings collide like
boxes around the whole object. They do not, and the first measurement said they
did because it was wrong - worth recording, because the wrong version was one
command from shipping.

Stored collider extent compared with world-space instance bounds puts every one
of the 38 colliders at a median 1.45x the art (p90 1.82x). But GXBE69 801DDFA4
divides the collision query by `instance+124`, so a collider's effective size
is its stored size *times* that scalar, and for all 2,059 Garibaldi instances
the scalar is 0.550 - the donor's geometry scale. The 1.8x was 1/0.55 being
rediscovered. Corrected:

    stored collider / visual bounds     p10 1.071  median 1.454  p90 1.816
    effective collider / visual bounds  p10 0.590  median 0.799  p90 0.999

The colliders sit *inside* the art, which is what a collider should do. Their
response property is stock-standard too: mass 1e30, restitution 0, behaviour 3,
surface -1 is 229 of 253 definitions in stock group 48, 569 of 591 in group 177.
So nothing about the import is wrong, and the aggressive feel is that static
collision now exists at all on a course that had been ridden without it.

What remains is a gameplay lever rather than a fix. `--target` says how large a
collider may be relative to its art, and anything above it is scaled about its
own centre - uniformly, so authored surface normals stay exactly as they are.
At the default target of 1.0 nothing qualifies, which is the useful answer. Pass
`--target 0.8` or lower to deliberately make scenery more forgiving.

Payloads are rewritten in place in the built archive, and only where the result
is byte-identical in length, so no block header, resource table, capacity or
group offset moves.

  python3 tools/gamecube_collision_shrink.py BUILD [--output OUT] [--target 0.8]

`BUILD` is a directory holding `BAM.BIG` and the `experiment.json` whose
`collisions.enabled_instances` records which instances use which collider.
"""

import argparse
import json
import statistics
import struct
from pathlib import Path

from gamecube_collision import read_collision, encode_collision
from gamecube_world import World

# Nothing is scaled below this fraction of its authored size. A collider that
# wants a huge correction is far more likely to be a bounds-derived shape or a
# mismatched pairing than a genuine 4x error, and shrinking it that far would
# let the rider through solid scenery.
FLOOR = 0.55
INSTANCE_BOUNDS_AT = 88


def collider_extent(meshes):
    low = [1e30] * 3
    high = [-1e30] * 3
    for mesh in meshes:
        for vertex in mesh['vertices']:
            for axis in range(3):
                low[axis] = min(low[axis], vertex[axis])
                high[axis] = max(high[axis], vertex[axis])
    if low[0] > 1e29:
        return None, None
    return low, [high[axis] - low[axis] for axis in range(3)]


def visual_extent(payload):
    bounds = struct.unpack_from('>6f', payload, INSTANCE_BOUNDS_AT)
    return [bounds[axis + 3] - bounds[axis] for axis in range(3)]


def instance_scale(payload):
    """The uniform scale the engine applies to this instance's collider.

    GXBE69 801DDFA4 divides the collision query by instance+124, so the
    collider's effective world size is its stored size *times* this. Comparing
    stored collider extent with world-space instance bounds without it makes
    every collider look about 1.8x too big - which is just 1/0.55, the donor's
    geometry scale, rediscovered.
    """
    return struct.unpack_from('>f', payload, 124)[0]


def wanted_factor(collider, visuals, target=1.0, floor=FLOOR):
    """How much to scale one collider, from the instances that use it.

    The median over axes and instances, not the maximum: one instance whose
    bounds were recomputed differently should not decide the shape every other
    instance collides with.
    """
    ratios = []
    for visual in visuals:
        for axis in range(3):
            if visual[axis] > 1 and collider[axis] > 0:
                ratios.append(collider[axis] / visual[axis])
    if not ratios:
        return 1.0
    ratio = statistics.median(ratios)
    if ratio <= target:
        return 1.0                      # already tight; never inflate
    return max(floor, target / ratio)


def scale_meshes(meshes, low, extent, factor):
    """Scale vertices about the collider's own centre, normals untouched.

    Uniform scaling leaves surface normals unchanged, so the response direction
    the engine reads stays exactly as authored.
    """
    centre = [low[axis] + extent[axis] / 2 for axis in range(3)]
    scaled = []
    for mesh in meshes:
        vertices = [tuple(centre[axis] + (vertex[axis] - centre[axis]) * factor
                          for axis in range(3))
                    for vertex in mesh['vertices']]
        scaled.append(dict(vertices=vertices, triangles=mesh['triangles'],
                           normals=mesh['normals']))
    return scaled


def plan(build, target=1.0, floor=FLOOR):
    """What each collider should be scaled by, and the evidence for it."""
    recipe = json.loads((Path(build) / 'experiment.json').read_text())
    enabled = recipe['collisions']['enabled_instances']
    group = recipe['group']
    world = World((Path(build) / 'BAM.BIG').read_bytes())
    records = world.records(group)
    colliders = {e['rid']: p for e, p in records if e['kind'] == 12 and p}
    instances = {e['rid']: p for e, p in records if e['kind'] == 3 and p}
    users = {}
    for entry in enabled:
        users.setdefault(entry['collision'], []).append(entry['instance'])
    rows = []
    for rid, payload in sorted(colliders.items()):
        try:
            meshes = read_collision(payload)
        except Exception as error:                  # not ours to interpret
            rows.append(dict(collider=rid, skipped=str(error)))
            continue
        low, extent = collider_extent(meshes)
        if low is None:
            rows.append(dict(collider=rid, skipped='no vertices'))
            continue
        visuals, scales = [], []
        for i in users.get(rid, []):
            if i not in instances:
                continue
            visuals.append(visual_extent(instances[i]))
            scales.append(instance_scale(instances[i]))
        scale = statistics.median(scales) if scales else 1.0
        effective = [v * scale for v in extent]
        factor = wanted_factor(effective, visuals, target, floor)
        rows.append(dict(collider=rid, uses=len(visuals), factor=round(factor, 4),
                         triangles=sum(len(m['triangles']) for m in meshes),
                         extent=[round(v) for v in extent],
                         instance_scale=round(scale, 4),
                         effective=[round(v) for v in effective],
                         floored=factor <= floor + 1e-9))
    return dict(build=str(build), group=group, target=target, floor=floor,
                colliders=len(colliders), rows=rows)


def shrink(build, output, target=1.0, floor=FLOOR):
    """Write a build whose colliders are scaled to their own art."""
    build = Path(build)
    output = Path(output)
    report = plan(build, target, floor)
    factors = {r['collider']: r['factor'] for r in report['rows'] if 'factor' in r}
    world = World((build / 'BAM.BIG').read_bytes())
    group = report['group']
    replacements = {}
    for entry, payload in world.records(group):
        if entry['kind'] != 12 or not payload:
            continue
        factor = factors.get(entry['rid'], 1.0)
        if factor >= 1.0:
            continue
        meshes = read_collision(payload)
        low, extent = collider_extent(meshes)
        data = encode_collision(scale_meshes(meshes, low, extent, factor))
        read_collision(data)                        # the encoder's own round-trip gate
        if len(data) != len(payload):
            # A same-size payload keeps every downstream offset and capacity
            # untouched, which is what makes an in-place rewrite safe at all.
            raise ValueError(f'Collider {entry["rid"]} changed size '
                             f'{len(payload)} -> {len(data)}')
        replacements[entry['rid']] = data
    report['rewritten'] = len(replacements)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'BAM.BIG').write_bytes(
        world.replace_records(group, 12, replacements) if hasattr(world, 'replace_records')
        else _splice(build / 'BAM.BIG', world, group, replacements))
    (output / 'collision-shrink.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def _splice(archive, world, group, replacements):
    """Overwrite equal-length collision payloads where they sit in the stream.

    Every replacement is byte-for-byte the same length as the record it
    replaces, so nothing moves: no block header, resource table, capacity or
    group offset changes, and the archive stays the one the recipe describes
    apart from the vertices themselves.
    """
    data = bytearray(Path(archive).read_bytes())
    written = 0
    for entry, payload in world.records(group):
        if entry['kind'] != 12 or entry['rid'] not in replacements:
            continue
        new = replacements[entry['rid']]
        offset = entry.get('stream_offset')
        if offset is None:
            raise ValueError('Resource records carry no stream offset; cannot splice')
        if bytes(data[offset:offset + len(new)]) != payload:
            raise ValueError(f'Collider {entry["rid"]} is not at its recorded offset')
        data[offset:offset + len(new)] = new
        written += 1
    if written != len(replacements):
        raise ValueError(f'Spliced {written} of {len(replacements)} colliders')
    return bytes(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('build', type=Path, help='Build directory with BAM.BIG and experiment.json')
    ap.add_argument('--output', type=Path, help='Write the shrunk build here')
    ap.add_argument('--target', type=float, default=1.0,
                    help='Collider extent as a multiple of visual bounds (default 1.0)')
    ap.add_argument('--floor', type=float, default=FLOOR,
                    help=f'Smallest fraction of the authored size (default {FLOOR})')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if args.dry_run or not args.output:
        report = plan(args.build, args.target, args.floor)
    else:
        report = shrink(args.build, args.output, args.target, args.floor)
    scaled = [r for r in report['rows'] if r.get('factor', 1.0) < 1.0]
    print(f"{report['colliders']} colliders, {len(scaled)} to shrink, "
          f"{sum(1 for r in scaled if r['floored'])} at the floor")
    for row in sorted(scaled, key=lambda r: r['factor'])[:10]:
        print(f"  x{row['factor']:.3f}  uses {row['uses']:4}  tris {row['triangles']:4}  "
              f"extent {row['extent']}")


if __name__ == '__main__':
    main()
