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

--breaking-glass is the other half. Garibaldi has no model named Glass, Pane or
Shard: the donor's breakables are its **LCD screen logos**, and the donor says
so itself -- the GSF function table carries ten `BreakLogo*` functions, each
of which hides one `Mdl_Lcd_ScreenLogo*` pane plus its `Mdl_Lcdscan*` sheen
overlay and reveals a pre-broken `Mdl_Lcd_ScreenLogoBroken*` twin. Each pane is
a visible collision-mode-2 record whose own effect slot is a burst of 52-word
particle emitters followed by a hide. That is the same shape as the stock
shatter, so the translation is: hide the pane and its overlay with builtin 2's
DeadNode command and emit the stock ABC1 particle block verbatim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from gamecube_lun import (assemble, call_builtin, dead_node, instruction, program_spans,
                          push_byte, push_float, push_int, replace_program, return_nil,
                          EMPTY_RETURN)
from gamecube_scenery import TrickyScenery
from gamecube_world import World, assemble as assemble_world, validate_resource_capacities

CLASS_TRACK = 1          # every stock behaviour-class oid carries track 1
CREATE_SLOT = 1          # event kind 1: instance create / attach behaviour
CONTACT_SLOT = 2         # event kind 2: rider contact / hit
COUNTDOWN_SLOT = 3       # reserved for the countdown registration program
PUSHABLE_MODELS = {7, 19, 1}
STOCK_MASS, STOCK_DAMPING, STOCK_TRAVEL = 1000.0, 0, 120.0

# Definition word 0 ("kind") selects where the collider comes from. Over all
# 11,802 stock definitions the correlation is exact: kind 0 never has a
# collision resource and never sets the collide flag, kind 1 always names one
# (word 3 != -1), and kind 2 always has word 3 = -1 *with* the collide flag set
# (1,124 draw+collide, 374 collide-only) -- an instance-bounds volume. The
# imported panes draw with kind 0 and have no collision resource, so kind 2
# plus draw+collide is the only way to give them a contact without importing a
# collision mesh.
DEF_KIND_BOUNDS_VOLUME = 2
DEF_FLAGS_DRAW_COLLIDE = 0x00210000    # stock's hidden trigger volumes use 0x00200000


def teeter_program(restitution, mass=STOCK_MASS, damping=STOCK_DAMPING, travel=STOCK_TRAVEL):
    """Stock ARA1 program 66: AnimTeeter on the firing instance (slot 0 default)."""
    return assemble([dict(code=[
        push_float(1, mass), push_byte(2, damping), push_float(5, 0.0),
        push_float(4, restitution), push_float(3, travel),
        call_builtin(2, 6, 5), return_nil()], params=3, stack=5)])


def particle_block():
    """The 52-argument builtin 26 (AddDynamicParticleData) call, verbatim from stock.

    Taken byte for byte from ABC1 (Merqury City Meltdown) program 171, whose
    four debris pieces each carry an identical copy of these 55 instructions.
    The recipe names what it can; every slot it does not name keeps the stock
    value, and the three instructions that are not pushes are copied as raw
    opcodes because opcodes 22/32/35/37/41 are not decoded.

    Named by the recipe: slot 3 = 1.9, slot 4/6 = 100, slot 8 = 0.012,
    slots 21/25/29 = 800.0 spawn extents, slots 33-40 = the two RGBA ramps,
    slots 49/50/51 = texture, blend and 400-unit lifetime. Slots 9-11, 15-20,
    22-24, 26-28, 30-31, 37, 41-48 are pushed by opcode 41 with no operand,
    i.e. left at the marshalling template's default.
    """
    return [
        push_byte(0, 1), push_byte(1, 0),
        instruction(41, 9, 0, 0), instruction(41, 10, 0, 0), instruction(41, 11, 0, 0),
        push_byte(12, 0), push_byte(13, 0), push_byte(14, 0),
        instruction(41, 15, 0, 0), instruction(41, 16, 0, 0), instruction(41, 17, 0, 0),
        push_byte(5, 1),
        instruction(41, 7, 0, 0), instruction(41, 30, 0, 0), instruction(41, 31, 0, 0),
        instruction(22, 2, 0, 0, 2000), instruction(35, 2, 2, 0), instruction(32, 32, 2, 0),
        instruction(41, 18, 0, 0), instruction(41, 19, 0, 0), instruction(41, 20, 0, 0),
        push_float(21, 800.0),
        instruction(41, 22, 0, 0), instruction(41, 23, 0, 0), instruction(41, 24, 0, 0),
        push_float(25, 800.0),
        instruction(41, 26, 0, 0), instruction(41, 27, 0, 0), instruction(41, 28, 0, 0),
        push_float(29, 800.0),
        push_float(33, 0.25), push_float(34, 0.6499999761581421),
        push_float(35, 0.75), push_float(36, 0.8999999761581421),
        instruction(41, 37, 0, 0),
        push_float(38, 0.6499999761581421), push_float(39, 0.75),
        push_float(40, 0.8999999761581421),
        instruction(41, 41, 0, 0), instruction(41, 42, 0, 0), instruction(41, 43, 0, 0),
        instruction(41, 44, 0, 0), instruction(41, 45, 0, 0), instruction(41, 46, 0, 0),
        instruction(41, 47, 0, 0), instruction(41, 48, 0, 0),
        push_byte(2, 1), push_float(3, 1.899999976158142), push_byte(4, 100),
        instruction(37, 51, 0, 0, 400),
        push_byte(6, 100), push_float(8, 0.012000000104308128),
        push_byte(49, 25), push_byte(50, 1),
        call_builtin(2, 26, 52)]


def debris_block(oid, rate):
    """Stock per-piece prologue: AnimObject(piece, 0, rate) then builtin 44."""
    return [push_int(0, oid), push_byte(1, 0), push_byte(5, rate), call_builtin(2, 3, 3),
            push_int(0, oid), call_builtin(2, 44, 1)]


def shatter_program(hide_oids, pieces=()):
    """Retarget stock ABC1 program 171 at a pane that has to vanish.

    Stock opens with builtin 2 command 3 (RestoreNode) on the firing instance,
    because its shatter trigger is an invisible volume that stays alive and the
    drawn debris is what changes. Our pane *is* the drawn object, so the
    command becomes 0 (DeadNode, 0x802EC1CC -> 0x801FB794 remove) and the oid
    is explicit: the donor's own break hides the pane and its scan-line
    overlay together, and only the firing instance can be addressed implicitly.

    The particle block runs first. Builtin 26 takes no position argument -- all
    three position slots are left at the template default -- so the emitter can
    only be reading the firing instance, and removing the node before emitting
    would be reading a freed node. Stock never orders these two the other way
    round because stock never issues DeadNode from script at all.

    `pieces` is [(oid, anim_rate)] for debris twins; Garibaldi imports none, so
    it is exercised only by the tests.
    """
    if not hide_oids:
        raise ValueError('A shatter needs at least one instance to remove')
    code = list(particle_block())
    for oid, rate in pieces:
        code += debris_block(oid, rate)
    for oid in hide_oids:
        code += dead_node(oid)
    return assemble([dict(code=code + [return_nil()], params=3, stack=52)])


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


def free_class_row(script, h, taken=()):
    for row in range(h['class_count']):
        at = h['class_at'] + 24*row
        if row not in taken and struct.unpack_from('>6I', script, at) == (0xffffffff,)*6:
            return row
    raise ValueError('No free behaviour-class row')


def free_program_slot(script, h, size, taken=()):
    reserved = load_time_programs(script, h) | {COUNTDOWN_SLOT} | set(taken)
    spans = program_spans(script)
    candidates = [(span, i) for i, (start, span) in enumerate(spans)
                  if i not in reserved and span >= size
                  and script[start:start+len(EMPTY_RETURN)] == EMPTY_RETURN]
    if not candidates:
        raise ValueError(f'No free program slot of {size} bytes')
    return min(candidates)[1]


def bind_definitions(script, assignments):
    """Clone each placement's definition once per distinct edit and repoint it.

    assignments: {instance rid: (class_oid, kind or None, flags or None)}. The
    definition table is the only thing that moves; word 3 (the collision
    resource) and the LOD entries are always kept as authored. Returns
    (script, {instance rid: (old definition index, new definition index)}).
    """
    h = header(script)
    ordinals = list(struct.unpack_from(f'>{h["count"]}H', script, h['table']))
    starts = list(struct.unpack_from(f'>{h["definitions"]}I', script, h['offsets']))
    if any(rid >= h['count'] for rid in assignments):
        raise ValueError('Placement outside the instance table')
    ends = starts[1:] + [h['table']-h['base']]
    clones, added, bound = {}, b'', {}
    for rid in sorted(assignments):
        edit = (ordinals[rid],) + tuple(assignments[rid])
        if edit not in clones:
            class_oid, kind, flags = assignments[rid]
            record = bytearray(script[h['base']+starts[edit[0]]:h['base']+ends[edit[0]]])
            if len(record) < 28 or (len(record)-16) % 12:
                raise ValueError('Unsupported instance definition size')
            if struct.unpack_from('>I', record, 8)[0] != 0xffffffff:
                raise ValueError('Placement already carries a behaviour class')
            if kind is not None:
                struct.pack_into('>I', record, 0, kind)
            if flags is not None:
                struct.pack_into('>I', record, 4, flags)
            struct.pack_into('>I', record, 8, class_oid)
            clones[edit] = (h['definitions']+len(clones), len(added))
            added += bytes(record)
        bound[rid] = (edit[0], clones[edit][0])
        ordinals[rid] = clones[edit][0]
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
    header(bytes(out))
    return bytes(out), bound


def bind_pushables(script, track, targets):
    """targets: {instance rid: restitution}. Returns (script, report)."""
    if not targets:
        raise ValueError('No pushable placements')
    h = header(script)
    restitution = sorted({round(r, 4) for r in targets.values()})
    if len(restitution) != 1:
        raise ValueError(f'One AnimTeeter program per restitution is not implemented: {restitution}')
    program = teeter_program(restitution[0])
    slot = free_program_slot(script, h, len(program))
    row = free_class_row(script, h)
    class_oid = CLASS_TRACK << 24 | row
    # Clone each distinct current definition once, with the class pointer set;
    # word 3 (the collision model) and the LOD entries stay as authored.
    out, bound = bind_definitions(script, {rid: (class_oid, None, None) for rid in targets})
    clones = {old: new for old, new in bound.values()}
    out = bytearray(out)
    struct.pack_into('>I', out, h['class_at']+24*row+4*CREATE_SLOT, track << 24 | slot)
    out = bytearray(replace_program(bytes(out), slot, program))
    header(bytes(out))
    return bytes(out), dict(
        class_row=row, class_oid=class_oid, program_slot=slot, program_size=len(program),
        program=program.hex(), restitution=restitution[0],
        anim_teeter=dict(mass=STOCK_MASS, damping=STOCK_DAMPING, travel=STOCK_TRAVEL,
                         restitution=restitution[0], source='stock ARA1 program 66 values; '
                         'donor physics definitions are not decoded'),
        cloned_definitions={str(k): v for k, v in clones.items()},
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


def breakable_logos(gsf, scene):
    """Decode the donor's own `Break*` GSF functions into pane/overlay/debris sets.

    A Break function is a list of opcode-7 `(instance, effect)` commands. The
    effect bodies split cleanly in two: `opcode 0 / size 16 / words (5, 4)` is
    the hide that the pane and its `Mdl_Lcdscan*` sheen overlay get, and
    `opcode 0 / size 52 / words (20, 1, 0.03, 2.0, ...)` is the reveal that the
    pre-broken twin gets. The pane is the member that is itself a visible
    collision-mode-2 record, i.e. the one the rider can hit; its own effect
    slot is the authored burst (nine or ten 52-word particle emitters followed
    by a hide), which is why the target translation is particles plus removal.

    Anything else in a Break function fails closed rather than being guessed.
    """
    if len(gsf) < 76:
        raise ValueError('Truncated GSF function header')
    effects, effect_table, functions, function_table, _, end = struct.unpack_from('>6I', gsf, 36)
    base = effect_table + effects*8
    if not (76 <= function_table <= effect_table <= base <= end <= len(gsf)) or \
            function_table+24*functions != effect_table:
        raise ValueError('Invalid GSF function/effect tables')

    def commands(table, stride, index, limit):
        if not 0 <= index < limit:
            raise ValueError('GSF call is outside its table')
        count, relative = struct.unpack_from('>II', gsf, table+stride*index)
        pos, out = base+relative, []
        if pos < base or pos > end or count > (end-pos)//8:
            raise ValueError('Invalid GSF program extent')
        for _ in range(count):
            opcode, size = struct.unpack_from('>II', gsf, pos)
            if size < 8 or size % 4 or pos+size > end:
                raise ValueError('Invalid GSF command size')
            out.append((opcode, size, struct.unpack_from(f'>{(size-8)//4}I', gsf, pos+8)))
            pos += size
        return out

    names = [gsf[function_table+24*i+8:function_table+24*i+24].split(b'\0')[0].decode()
             for i in range(functions)]
    result = []
    for i, name in enumerate(names):
        if not name.startswith('Break'):
            continue
        entry = dict(function=name, pane=None, hide=[], reveal=[])
        for opcode, size, words in commands(function_table, 24, i, functions):
            if opcode != 7 or size != 16:
                raise ValueError(f'Unsupported command {opcode}/{size} in {name}')
            instance, effect = words
            if instance >= len(scene.instances):
                raise ValueError('GSF break instance is outside the scene')
            body = commands(effect_table, 8, effect, effects)
            if body == [(0, 16, (5, 4))]:
                entry['hide'].append(instance)
                play = scene.gameplay[instance]
                if play['collision_mode'] == 2 and play['visible']:
                    if entry['pane'] is not None:
                        raise ValueError(f'{name} names two collidable panes')
                    entry['pane'] = instance
            elif len(body) == 1 and body[0][0] == 0 and body[0][2][:2] == (20, 1):
                entry['reveal'].append(instance)
            else:
                raise ValueError(f'Unsupported break effect {effect} in {name}')
        if entry['pane'] is None:
            raise ValueError(f'{name} has no collidable pane')
        result.append(entry)
    return result


def glass_targets(recipe, scene, gsf):
    """Target rids for every imported breakable pane, plus what was left behind.

    Returns ({pane rid: [rids to remove on contact]}, skipped). A pane is only
    a target if the pane instance itself was imported; its companion overlays
    and debris twins are included only when they were imported too, and the
    omissions are reported rather than silently dropped.
    """
    source_of = {int(k): v for k, v in recipe['scenery']['instance_source_ids'].items()}
    target_of = {source: rid for rid, source in source_of.items()}
    targets, skipped = {}, []
    for entry in breakable_logos(gsf, scene):
        pane = target_of.get(entry['pane'])
        missing = [i for i in entry['hide']+entry['reveal'] if i not in target_of]
        record = dict(function=entry['function'], pane_source=entry['pane'], pane=pane,
                      pane_model=scene.instances[entry['pane']]['model'],
                      not_imported=sorted(missing),
                      debris_sources=sorted(entry['reveal']))
        if pane is None:
            skipped.append(dict(record, reason='pane model not imported'))
            continue
        targets[pane] = [target_of[i] for i in entry['hide'] if i in target_of]
        record['removes'] = sorted(targets[pane])
        skipped.append(dict(record, reason='bound'))
    return targets, skipped


def bind_glass(script, track, targets):
    """targets: {pane rid: [rids to remove on contact]}. Returns (script, report).

    Design: one class row and one program per pane, and the pane's *own*
    definition carries the binding.

    The stock shatter hangs off a separate invisible collision volume, and
    Garibaldi does have 23 hidden collision-mode-2 volumes -- but they are
    `Mdl_FWTrigger_*` (fireworks), none of them is imported, and the nearest
    one to any pane is ~2,900 donor units away, so there is nothing to attach
    to. The pane itself is the rider-collidable record in the donor, so its own
    definition is repointed instead: kind 2 (instance-bounds volume) and
    flags 0x00210000 (draw + collide), which is the only stock definition shape
    that collides without naming a collision resource.

    One program per pane rather than one shared self-addressed program: the
    donor break removes the pane *and* its separate scan-line overlay, and only
    the firing instance can be addressed implicitly, so the overlay needs an
    explicit oid anyway.
    """
    if not targets:
        raise ValueError('No breakable glass placements')
    h = header(script)
    ordinals = struct.unpack_from(f'>{h["count"]}H', script, h['table'])
    starts = struct.unpack_from(f'>{h["definitions"]}I', script, h['offsets'])
    for pane in sorted(targets):
        if pane >= h['count']:
            raise ValueError('Breakable pane outside the instance table')
        kind, _, _, collision = struct.unpack_from('>4I', script, h['base']+starts[ordinals[pane]])
        # kind 2 is a bounds volume and stock never pairs it with a collision
        # resource. A pane that already names one is a shape this does not know
        # how to convert, so fail rather than invent one.
        if collision != 0xffffffff or kind not in (0, DEF_KIND_BOUNDS_VOLUME):
            raise ValueError(f'Pane {pane} already has a collision resource (kind {kind})')
    rows, slots, panes = [], [], {}
    for pane in sorted(targets):
        removes = sorted({pane} | set(targets[pane]))
        program = shatter_program([track << 24 | rid for rid in removes])
        slot = free_program_slot(script, h, len(program), slots)
        row = free_class_row(script, h, rows)
        rows.append(row)
        slots.append(slot)
        panes[pane] = dict(class_row=row, class_oid=CLASS_TRACK << 24 | row, program_slot=slot,
                           program_size=len(program), removes=removes, program=program.hex())
    out, bound = bind_definitions(script, {
        pane: (panes[pane]['class_oid'], DEF_KIND_BOUNDS_VOLUME, DEF_FLAGS_DRAW_COLLIDE)
        for pane in targets})
    for pane, (old, new) in bound.items():
        panes[pane].update(definition=new, cloned_from=old)
    out = bytearray(out)
    for pane, info in panes.items():
        struct.pack_into('>I', out, h['class_at']+24*info['class_row']+4*CONTACT_SLOT,
                         track << 24 | info['program_slot'])
        out = bytearray(replace_program(bytes(out), info['program_slot'],
                                        bytes.fromhex(info['program'])))
    header(bytes(out))
    return bytes(out), dict(
        panes={str(k): v for k, v in sorted(panes.items())},
        class_rows=rows, program_slots=slots,
        definition=dict(kind=DEF_KIND_BOUNDS_VOLUME, flags=DEF_FLAGS_DRAW_COLLIDE,
                        source='kind 2 is the only stock shape that collides with word 3 = -1'),
        particles='stock ABC1 program 171 builtin 26 block, verbatim',
        verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base-build', 'nbd', 'gsf', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--pushable-blocks', action='store_true')
    parser.add_argument('--breaking-glass', action='store_true')
    args = parser.parse_args()
    if not (args.pushable_blocks or args.breaking_glass):
        parser.error('Nothing to bind; pass --pushable-blocks and/or --breaking-glass')
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
    entry, script = rows[scripts[0]]
    reports = {}
    if args.pushable_blocks:
        targets, skipped = pushable_targets(recipe, scene)
        script, report = bind_pushables(script, track, targets)
        report.update(skipped=skipped, limitation='Binds the create-time AnimTeeter behaviour '
                      'only; no run has yet shown a block move, and the donor effect/physics '
                      'records are untranslated.')
        reports['interactions'] = report
    if args.breaking_glass:
        targets, skipped = glass_targets(recipe, scene, gsf)
        script, report = bind_glass(script, track, targets)
        report.update(donor=skipped, limitation='Removes the pane and its scan overlay and emits '
                      'the stock particle block; the donor also reveals a pre-broken twin, whose '
                      'models 49/86/90 are omitted as multipart, and the collider is the '
                      'instance bounds volume, not the pane mesh. No run has shown a break.')
        reports['glass'] = report
    rows = list(rows)
    rows[scripts[0]] = (dict(entry, size=len(script)), script)
    result, _ = assemble_world(World(original), {group: rows})
    summary = dict(base_sha256=recipe['output_sha256'],
                   archive_sha256=hashlib.sha256(result).hexdigest(),
                   resource_count=validate_resource_capacities(World(result)))
    for key, report in reports.items():
        report.update(summary)
        recipe[key] = report
    recipe['output_sha256'] = summary['archive_sha256']
    args.output.mkdir(parents=True)
    (args.output/'BAM.BIG').write_bytes(result)
    (args.output/'experiment.json').write_text(json.dumps(recipe, indent=2)+'\n')
    for key, report in reports.items():
        name = 'interactions.json' if key == 'interactions' else key+'.json'
        (args.output/name).write_text(json.dumps(report, indent=2)+'\n')
    brief = dict(summary)
    if 'interactions' in reports:
        brief['pushables'] = {k: reports['interactions'][k]
                              for k in ('class_row', 'program_slot', 'program_size', 'placements')}
    if 'glass' in reports:
        brief['glass'] = {pane: {k: info[k] for k in
                                 ('class_row', 'program_slot', 'program_size', 'removes')}
                          for pane, info in reports['glass']['panes'].items()}
    print(json.dumps(brief, indent=2))


if __name__ == '__main__':
    main()
