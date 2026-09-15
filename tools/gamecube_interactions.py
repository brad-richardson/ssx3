#!/usr/bin/env python3
"""Bind donor physics objects to SSX 3 behaviour classes in the course script.

Stock SSX 3 has no "pushable" builtin. Behaviour is attached per definition:
definition word 2 is a behaviour-class oid whose rid indexes the script
record's 24-byte class table, and each row's six slots name a program for an
event kind (1 = create/attach, 2 = rider contact, ...). A pushable block is a
class row whose create slot runs a one-function program calling builtin 6
(AnimTeeter) on the firing instance. Every imported definition has word 2 =
-1, which is why nothing has ever fired. Decoded in
local/research/startgate/breakables-recipe.md.

--pushable-blocks selects the donor's collision-mode-3 placements (a physics
reference plus an effect slot: models 7, 19 and 1 on Garibaldi), clones their
current definitions with the class pointer set, claims a free class row, and
writes the AnimTeeter program into the smallest free stub slot that is not a
load-time program. Nothing else in the record moves except the definition
table, which grows the same way the countdown staging grows it.

The AnimTeeter parameters are the stock values (mass 1000, no damping, 120
travel) with the donor's own restitution; the donor's 56 physics definitions
are not decoded, so mass is not translated.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from gamecube_lun import (assemble, call_builtin, program_spans, push_byte, push_float,
                          replace_program, return_nil, EMPTY_RETURN)
from gamecube_scenery import TrickyScenery
from gamecube_world import World, assemble as assemble_world, validate_resource_capacities

CLASS_TRACK = 1          # every stock behaviour-class oid carries track 1
CREATE_SLOT = 1          # event kind 1: instance create / attach behaviour
COUNTDOWN_SLOT = 3       # reserved for the countdown registration program
PUSHABLE_MODELS = {7, 19, 1}
STOCK_MASS, STOCK_DAMPING, STOCK_TRAVEL = 1000.0, 0, 120.0


def teeter_program(restitution, mass=STOCK_MASS, damping=STOCK_DAMPING, travel=STOCK_TRAVEL):
    """Stock ARA1 program 66: AnimTeeter on the firing instance (slot 0 default)."""
    return assemble([dict(code=[
        push_float(1, mass), push_byte(2, damping), push_float(5, 0.0),
        push_float(4, restitution), push_float(3, travel),
        call_builtin(2, 6, 5), return_nil()], params=3, stack=5)])


def header(script):
    load_count, load_at, class_count, class_at = struct.unpack_from('>4I', script, 16)
    base = struct.unpack_from('>I', script, 64)[0]
    count, table, definitions, offsets, splines, spline_at = struct.unpack_from('>6I', script, 68)
    if (not 92 <= base < table or not table+count*2 <= offsets <= table+count*2+3 or
            offsets+definitions*4 != spline_at or spline_at+splines*4 != len(script) or
            class_at+class_count*24 > base or load_at+load_count*4 > base):
        raise ValueError('Unsupported course script layout')
    return dict(load_count=load_count, load_at=load_at, class_count=class_count, class_at=class_at,
                base=base, count=count, table=table, definitions=definitions, offsets=offsets,
                splines=splines, spline_at=spline_at)


def load_time_programs(script, h):
    return {oid & 0xffffff for oid in struct.unpack_from(f'>{h["load_count"]}I', script, h['load_at'])}


def free_class_row(script, h):
    for row in range(h['class_count']):
        at = h['class_at'] + 24*row
        if struct.unpack_from('>6I', script, at) == (0xffffffff,)*6:
            return row
    raise ValueError('No free behaviour-class row')


def free_program_slot(script, h, size):
    reserved = load_time_programs(script, h) | {COUNTDOWN_SLOT}
    spans = program_spans(script)
    candidates = [(span, i) for i, (start, span) in enumerate(spans)
                  if i not in reserved and span >= size
                  and script[start:start+len(EMPTY_RETURN)] == EMPTY_RETURN]
    if not candidates:
        raise ValueError(f'No free program slot of {size} bytes')
    return min(candidates)[1]


def bind_pushables(script, track, targets):
    """targets: {instance rid: restitution}. Returns (script, report)."""
    if not targets:
        raise ValueError('No pushable placements')
    h = header(script)
    ordinals = list(struct.unpack_from(f'>{h["count"]}H', script, h['table']))
    starts = list(struct.unpack_from(f'>{h["definitions"]}I', script, h['offsets']))
    if any(rid >= h['count'] for rid in targets):
        raise ValueError('Pushable placement outside the instance table')
    ends = starts[1:] + [h['table']-h['base']]
    restitution = sorted({round(r, 4) for r in targets.values()})
    if len(restitution) != 1:
        raise ValueError(f'One AnimTeeter program per restitution is not implemented: {restitution}')
    program = teeter_program(restitution[0])
    slot = free_program_slot(script, h, len(program))
    row = free_class_row(script, h)
    class_oid = CLASS_TRACK << 24 | row
    # Clone each distinct current definition once, with the class pointer set;
    # word 3 (the collision model) and the LOD entries stay as authored.
    clones, added = {}, b''
    for rid in sorted(targets):
        current = ordinals[rid]
        if current not in clones:
            record = bytearray(script[h['base']+starts[current]:h['base']+ends[current]])
            if len(record) < 28 or (len(record)-16) % 12:
                raise ValueError('Unsupported instance definition size')
            if struct.unpack_from('>I', record, 8)[0] != 0xffffffff:
                raise ValueError('Placement already carries a behaviour class')
            struct.pack_into('>I', record, 8, class_oid)
            clones[current] = (h['definitions']+len(clones), len(added))
            added += bytes(record)
        ordinals[rid] = clones[current][0]
    defs_end = h['table']-h['base']
    out = bytearray(script[:h['table']] + added)
    new_table = len(out)
    out += struct.pack(f'>{h["count"]}H', *ordinals)
    out += bytes(-len(out) % 4)
    new_offsets = len(out)
    out += struct.pack(f'>{h["definitions"]}I', *starts)
    out += struct.pack(f'>{len(clones)}I', *(defs_end+at for _, at in clones.values()))
    new_spline_at = len(out)
    out += script[h['spline_at']:]
    struct.pack_into('>6I', out, 68, h['count'], new_table, h['definitions']+len(clones),
                     new_offsets, h['splines'], new_spline_at)
    struct.pack_into('>I', out, h['class_at']+24*row+4*CREATE_SLOT, track << 24 | slot)
    out = bytearray(replace_program(bytes(out), slot, program))
    header(bytes(out))
    return bytes(out), dict(
        class_row=row, class_oid=class_oid, program_slot=slot, program_size=len(program),
        program=program.hex(), restitution=restitution[0],
        anim_teeter=dict(mass=STOCK_MASS, damping=STOCK_DAMPING, travel=STOCK_TRAVEL,
                         restitution=restitution[0], source='stock ARA1 program 66 values; '
                         'donor physics definitions are not decoded'),
        cloned_definitions={str(k): v[0] for k, v in clones.items()},
        placements=sorted(targets), verified=False)


def pushable_targets(recipe, scene):
    """Target instance rid -> donor restitution for the mode-3 physics placements."""
    source_of = {int(k): v for k, v in recipe['scenery']['instance_source_ids'].items()}
    targets, skipped = {}, []
    for rid, source in source_of.items():
        instance, play = scene.instances[source], scene.gameplay[source]
        if play['collision_mode'] != 3:
            continue
        if instance['model'] not in PUSHABLE_MODELS or play['immovable']:
            skipped.append(dict(target=rid, source=source, model=instance['model']))
            continue
        targets[rid] = play['bounce']
    return targets, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base-build', 'nbd', 'gsf', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--pushable-blocks', action='store_true')
    args = parser.parse_args()
    if not args.pushable_blocks:
        parser.error('Nothing to bind; pass --pushable-blocks')
    if args.output.exists():
        raise ValueError('Use a fresh candidate directory')
    recipe = json.loads((args.base_build/'experiment.json').read_text())
    original = (args.base_build/'BAM.BIG').read_bytes()
    nbd, gsf = args.nbd.read_bytes(), args.gsf.read_bytes()
    if (hashlib.sha256(original).hexdigest() != recipe['output_sha256'] or
            hashlib.sha256(nbd).hexdigest() != recipe['scenery']['source_sha256']):
        raise ValueError('Base archive or donor NBD does not match recipe')
    scene = TrickyScenery(nbd, gsf)
    group, track = recipe['group'], recipe['track']
    world = World(original)
    rows = world.records(group)
    scripts = [i for i, (e, _) in enumerate(rows) if e['kind'] == 16 and e['track'] == track]
    if len(scripts) != 1:
        raise ValueError('Expected one course-owned script binding table')
    targets, skipped = pushable_targets(recipe, scene)
    entry, payload = rows[scripts[0]]
    script, report = bind_pushables(payload, track, targets)
    rows = list(rows)
    rows[scripts[0]] = (dict(entry, size=len(script)), script)
    result, _ = assemble_world(World(original), {group: rows})
    report.update(skipped=skipped, base_sha256=recipe['output_sha256'],
                  archive_sha256=hashlib.sha256(result).hexdigest(),
                  resource_count=validate_resource_capacities(World(result)),
                  limitation='Binds the create-time AnimTeeter behaviour only; no run has yet '
                             'shown a block move, and the donor effect/physics records are untranslated.')
    recipe['interactions'] = report
    recipe['output_sha256'] = report['archive_sha256']
    args.output.mkdir(parents=True)
    (args.output/'BAM.BIG').write_bytes(result)
    (args.output/'experiment.json').write_text(json.dumps(recipe, indent=2)+'\n')
    (args.output/'interactions.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ('class_row', 'program_slot', 'program_size',
                                             'placements', 'cloned_definitions', 'archive_sha256')}, indent=2))


if __name__ == '__main__':
    main()
