#!/usr/bin/env python3
"""Build a repeatable race-start fixture without altering production course paths.

Scenario coordinates live in per-course JSON, expressed in donor coordinates.
The shared builder changes only race start positions/directions; normal course
geometry, reset paths, collision, race progress and finish data remain intact.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from course_route import ssx3_paths
from gamecube_world import World, assemble, validate_resource_capacities
from import_terrain import apply


def relocate_race_gates(aip, position, direction, spacing):
    _, _, _, starts = ssx3_paths(aip)
    if (len(position) != 3 or len(direction) != 3 or
            not all(math.isfinite(v) for v in [*position, *direction, spacing]) or spacing < 0):
        raise ValueError('Expected finite start vectors and nonnegative spacing')
    length = math.hypot(*direction)
    if length == 0 or math.hypot(*direction[:2]) == 0:
        raise ValueError('Start direction must have a horizontal component')
    direction = [v/length for v in direction]
    side = [-direction[1], direction[0], 0.]
    norm = math.hypot(*side)
    side = [v/norm for v in side]
    gates = [i for i, s in enumerate(starts) if s[1] == 0]
    if not gates:
        raise ValueError('No race gates in course')
    out = bytearray(aip)
    edits = []
    for order, i in enumerate(gates):
        point = [position[k] + side[k]*spacing*order for k in range(3)]
        offset = len(aip) - 40*len(starts) + 40*i + 8
        struct.pack_into('<6f', out, offset, *point, *direction)
        edits.append(dict(start=i, offset=offset, position=point, direction=direction))
    allowed = {j for e in edits for j in range(e['offset'], e['offset']+24)}
    if any(a != b and i not in allowed for i, (a,b) in enumerate(zip(aip,out))):
        raise RuntimeError('Unexpected fixture change outside start coordinates')
    ssx3_paths(out)
    return bytes(out), edits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-build', type=Path, required=True)
    ap.add_argument('--scenarios', type=Path, required=True)
    ap.add_argument('--scenario', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Choose a fresh fixture output')
    recipe = json.loads((args.base_build/'experiment.json').read_text())
    scenarios = json.loads(args.scenarios.read_text())
    if scenarios['donor_nbd_sha256'] != recipe['donor_nbd_sha256']:
        raise ValueError('Scenario source does not match the imported course')
    scenario = scenarios['scenarios'][args.scenario]
    archive = (args.base_build/'BAM.BIG').read_bytes()
    if hashlib.sha256(archive).hexdigest() != recipe['output_sha256']:
        raise ValueError('Base build archive does not match its recipe')
    world = World(archive)
    group = recipe['group']
    rows = world.records(group)
    paths = [(e,p) for e,p in rows if e['kind']==14 and p]
    if len(paths) != 1 or paths[0][0]['track'] != recipe['track']:
        raise ValueError('Expected one owned course AIP')
    position = apply(recipe['matrix'], recipe['translation'], scenario['position'])
    direction = apply(recipe['matrix'], [0,0,0], scenario['direction'])
    aip, edits = relocate_race_gates(paths[0][1], position, direction, 55*recipe['scale'])
    changed = [(dict(e,size=len(aip)),aip) if e==paths[0][0] else (e,p) for e,p in rows]
    result, _ = assemble(world, {group:changed})
    check = World(result)
    if check.records(group) != changed:
        # Serialized entries may carry additional reader metadata. Compare
        # resource identity and payload rather than incidental dictionary keys.
        key = lambda r: [((e['kind'],e['track'],e['rid']),p) for e,p in r]
        if key(check.records(group)) != key(changed):
            raise RuntimeError('Fixture readback differs')
    for g in world.index['groups']:
        i = g['index']
        if i != group and check.original_group_blocks(i) != world.original_group_blocks(i):
            raise RuntimeError('Fixture changed another course group')
    receipt = dict(scenario=args.scenario, definition=scenario, edits=edits,
        base_archive_sha256=recipe['output_sha256'], scenarios_sha256=hashlib.sha256(args.scenarios.read_bytes()).hexdigest(),
        resource_count=validate_resource_capacities(check), native_verified=False)
    recipe['diagnostic_start'] = receipt
    recipe['output_sha256'] = hashlib.sha256(result).hexdigest()
    args.output.mkdir(parents=True)
    (args.output/'BAM.BIG').write_bytes(result)
    (args.output/'experiment.json').write_text(json.dumps(recipe,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
