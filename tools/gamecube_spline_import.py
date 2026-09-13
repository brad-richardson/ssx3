#!/usr/bin/env python3
"""Build a local, experimental donor-rail candidate from a scenery build.

Geometry/distance conversion is shared; style 13 -> target binding 0003000a
is an explicit diagnostic profile, not a verified donor sound/effect mapping.
No installation or native launch is performed by this command.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from gamecube_splines import PROFILE, audit_conversion, encode_spline, read_tricky_splines
from gamecube_world import World, assemble, validate_resource_capacities


def require_disabled_programs(script):
    if len(script) < 92 or script[:4] != bytes.fromhex('00100000'):
        raise ValueError('Unsupported course script header')
    count, table, end = struct.unpack_from('>3I', script, 56)
    if not 0 < count or table < 92 or table + count*4 > end or end > len(script):
        raise ValueError('Invalid course program table')
    starts = struct.unpack_from(f'>{count}I', script, table)
    if list(starts) != sorted(set(starts)) or starts[0] < table + count*4:
        raise ValueError('Invalid course program offsets')
    empty_return = bytes.fromhex('004e554c0000001400000024000000242aff0000ffffffec000000000000000200000000')
    for a, b in zip(starts, (*starts[1:], end)):
        if b-a < len(empty_return) or script[a:a+36] != empty_return or any(script[a+36:b]):
            raise ValueError('Disable host course programs before replacing spline IDs')


def replace_splines(records, source, matrix, translation, track):
    old = [(e, p) for e, p in records if e['kind'] == 8]
    if (not old or any(e['track'] != track for e, _ in old) or
            sorted(e['rid'] for e, _ in old) != list(range(len(old)))):
        raise ValueError('Expected complete, dense host spline table')
    for _, p in old:
        if len(p) < 48 or len(p) != 48 + 144*struct.unpack_from('>I', p, 32)[0]:
            raise ValueError('Invalid host spline record')
    scripts = [(e, p) for e, p in records if e['kind'] == 16]
    if len(scripts) != 1 or scripts[0][0]['track'] != track:
        raise ValueError('Expected one course-owned spline binding table')
    # Reusing dense IDs is required by this binding table. It is only allowed
    # after the host's executable course programs have been disabled.
    _, script = scripts[0]
    require_disabled_programs(script)
    count, table = struct.unpack_from('>II', script, 84)
    if count != len(old) or table < 92 or table + count*4 != len(script):
        raise ValueError('Unsupported host spline binding table extent')
    binding = bytes.fromhex('0003000a')
    if binding not in [script[table+4*i:table+4*i+4] for i in range(count)]:
        raise ValueError('Diagnostic rail binding absent from host profile')
    template = next((p[48:192] for _, p in old if len(p) >= 192), None)
    if template is None or not source or [s['rid'] for s in source] != list(range(len(source))):
        raise ValueError('Expected nonempty dense donor spline table')
    added = []
    for spline in source:
        rid = spline['rid']
        p = encode_spline(spline, matrix, translation, track << 24 | rid, template)
        added.append((dict(kind=8, track=track, rid=rid, size=len(p)), p))
    data = bytearray(script[:table])
    struct.pack_into('>I', data, 84, len(added))
    data += binding * len(added)
    result, inserted = [], False
    for e, p in records:
        if e['kind'] == 8:
            if not inserted:
                result.extend(added)
                inserted = True
        elif e['kind'] == 16:
            result.append((dict(e, size=len(data)), bytes(data)))
        else:
            result.append((e, p))
    return result, dict(profile=PROFILE, replaced_host_splines=len(old),
                        added_splines=len(added), segments=sum(len(s['segments']) for s in source),
                        geometry_bytes_before=sum(len(p) for _, p in old),
                        geometry_bytes_after=sum(len(p) for _, p in added),
                        binding_profile='diagnostic-host-0003000a',
                        donor_style=[1, 1, 13], native_ride_verified=False,
                        grind_transfer_verified=False, donor_effects_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-build', required=True, type=Path)
    parser.add_argument('--nbd', required=True, type=Path)
    parser.add_argument('--gsf', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output exists; use a fresh build directory')
    recipe = json.loads((args.base_build/'experiment.json').read_text())
    if recipe.get('mode') != 'gamecube-replace-terrain' or not recipe.get('scenery', {}).get('added_instances'):
        raise ValueError('Expected a replaced terrain build with donor scenery')
    nbd, gsf = args.nbd.read_bytes(), args.gsf.read_bytes()
    if hashlib.sha256(nbd).hexdigest() != recipe['scenery']['source_sha256']:
        raise ValueError('Rail source must match installed scenery source')
    source = read_tricky_splines(nbd, gsf)
    original = (args.base_build/'BAM.BIG').read_bytes()
    world = World(original)
    group, track = recipe['group'], recipe['track']
    location = world.location(recipe['location'])
    if location['index'] != track or not location['group_start'] <= group <= location['last_group']:
        raise ValueError('Course group and track ownership mismatch')
    for row in world.index['groups']:
        if row['index'] != group:
            # Kind 16 is not counted in the 14-kind group header. Inspect
            # every record so streamed metadata cannot evade this check.
            if any(e['track'] == track and e['kind'] in (8, 16) for e, _ in world.records(row['index'])):
                raise ValueError('Cross-group spline ownership needs an explicit conversion')
    records, report = replace_splines(world.records(group), source, recipe['matrix'], recipe['translation'], track)
    report['conversion_audit'] = audit_conversion(
        source, [p for e, p in records if e['kind'] == 8], recipe['matrix'], recipe['translation'])
    archive, _ = assemble(world, {group: records})
    report.update(source_nbd_sha256=hashlib.sha256(nbd).hexdigest(),
                  source_gsf_sha256=hashlib.sha256(gsf).hexdigest(),
                  base_archive_sha256=hashlib.sha256(original).hexdigest(),
                  archive_sha256=hashlib.sha256(archive).hexdigest(),
                  resource_count=validate_resource_capacities(World(archive)))
    recipe['rails'] = report
    args.output.mkdir(parents=True)
    (args.output/'BAM.BIG').write_bytes(archive)
    (args.output/'experiment.json').write_text(json.dumps(recipe, indent=2)+'\n')
    (args.output/'rails.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
