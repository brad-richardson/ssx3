#!/usr/bin/env python3
"""Stage countdown assets in a fresh local course candidate.

This does not bind or animate a countdown. The three authored NoCountDown
instances stay non-colliding, and every course program stays empty. The
candidate supplies checked instances and complete flipbook images for a later,
independently verified StartlightBegin/StartgateOpen binding.

The added instances share one course-script definition of their own, whose
word 1 bit 16 draws and bit 21 collides. That definition is therefore the
reversible visibility operation a countdown handler needs, and it touches
those three instances alone. --visible stages them permanently drawn, by
copying the course's own visible non-colliding scenery definition verbatim,
so placement and the visibility bit can be checked before any binding exists.
--countdown-ready stages that same copy with only the visibility bit cleared,
so a handler shows and hides the gate by toggling one bit and every other word
is already the shape ordinary scenery uses.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from gamecube_scenery import TrickyScenery, post_countdown_hidden
from gamecube_scenery_import import WORLD_RESOURCE_ORDER, eligibility, instance_record, record
from gamecube_spline_import import require_disabled_programs
from gamecube_textures import shape_images, world_image_record
from gamecube_world import World, assemble, unused_global_rids, validate_resource_capacities


VISIBLE_FLAG = 0x00010000
COLLISION_FLAG = 0x00200000


def visible_scenery_definition(script, base, definitions, starts, table):
    """The course's own ordinary visible, non-colliding scenery definition.

    Copied verbatim rather than synthesized. Its trailing words carry a draw
    distance and a packed pair whose meaning is not established, so guessing
    them is not safe; requiring exactly one such shape keeps the copy honest.
    """
    shapes = set()
    for start in starts:
        row = script[base+start:base+start+28]
        if len(row) != 28:
            raise ValueError('Truncated instance definition')
        kind, flags, callback, collision = struct.unpack_from('>4I', row)
        if (kind, flags, callback, collision) == (0, VISIBLE_FLAG, 0xffffffff, 0xffffffff):
            shapes.add(bytes(row))
    if len(shapes) != 1:
        raise ValueError('Course has no single visible non-colliding scenery definition to copy')
    return shapes.pop()


MODES = ('hidden', 'visible', 'countdown')


def append_hidden_bindings(script, expected_count, added_count, mode='hidden'):
    """Extend dense instance ordinals; preserve old definitions and all LUNs.

    Definition word 1 bit 16 draws and bit 21 collides, and the staged
    countdown definition is used by those instances alone, so that record is
    the whole reversible visibility operation. The three modes stage it as:

    hidden     all zero, drawing nothing and depending on no other word
    visible    a verbatim copy of the course's own visible scenery definition
    countdown  that same copy with only the visibility bit cleared, so a
               handler drives one bit and any other word it might need is
               already correct
    """
    if mode not in MODES:
        raise ValueError(f'Unsupported countdown staging mode: {mode}')
    require_disabled_programs(script)
    base = struct.unpack_from('>I', script, 64)[0]
    count, table, definitions, offsets, splines, spline_at = struct.unpack_from('>6I', script, 68)
    if (count != expected_count or added_count <= 0 or not 92 <= base < table or
            not table+count*2 <= offsets <= table+count*2+3 or
            offsets+definitions*4 != spline_at or spline_at+splines*4 != len(script)):
        raise ValueError('Unsupported dense instance binding extents')
    indices = struct.unpack_from(f'>{count}H', script, table)
    starts = struct.unpack_from(f'>{definitions}I', script, offsets)
    if (not definitions or definitions >= 65535 or any(i >= definitions for i in indices) or
            list(starts) != sorted(set(starts)) or starts[0] != 0 or base+starts[-1] >= table):
        raise ValueError('Invalid dense instance definition indices')
    # Kind zero, no visibility/collision bits, no callbacks or collision model.
    if mode == 'hidden':
        added = struct.pack('>4I3f', 0, 0, 0xffffffff, 0xffffffff, 0, 0, 0)
    else:
        added = bytearray(visible_scenery_definition(script, base, definitions, starts, table))
        if mode == 'countdown':
            template = struct.unpack_from('>I', added, 4)[0]
            struct.pack_into('>I', added, 4, template & ~VISIBLE_FLAG)
        added = bytes(added)
    flags = struct.unpack_from('>I', added, 4)[0]
    if flags & COLLISION_FLAG or struct.unpack_from('>2I', added, 8) != (0xffffffff, 0xffffffff):
        raise ValueError('Staged countdown definition must stay non-colliding and unbound')
    out = bytearray(script[:table]+added)
    new_table = len(out)
    out += script[table:table+count*2]+struct.pack('>H', definitions)*added_count
    out += bytes(-len(out) % 4)
    new_offsets = len(out)
    out += script[offsets:spline_at]+struct.pack('>I', table-base)
    new_spline_at = len(out)
    out += script[spline_at:]
    struct.pack_into('>6I', out, 68, count+added_count, new_table, definitions+1,
                     new_offsets, splines, new_spline_at)
    require_disabled_programs(out)
    return bytes(out), dict(definition=definitions, mode=mode, flags=flags,
                            initially_visible=bool(flags & VISIBLE_FLAG),
                            handler_drives_visibility=mode == 'countdown',
                            collision=False, callback=None, added_instances=added_count)


def stage(world, recipe, scene, images, source_ids, mode='hidden'):
    group, track = recipe['group'], recipe['track']
    rows = world.records(group)
    if not source_ids:
        raise ValueError('No authored temporary countdown instances')
    source_map = {int(k): v for k, v in recipe['scenery']['instance_source_ids'].items()}
    instances = sorted((e['rid'], p) for e, p in rows if e['kind'] == 3 and e['track'] == track)
    if ([rid for rid, _ in instances] != list(range(len(instances))) or
            set(source_map) != set(range(len(instances))) or
            set(source_ids) & set(source_map.values())):
        raise ValueError('Countdown staging requires unmapped source instances and dense owned target IDs')
    models = sorted(e['rid'] for e, _ in rows if e['kind'] == 2 and e['track'] == track)
    if len(models) != len(recipe['scenery']['source_models']):
        raise ValueError('Retained model/source mapping changed')
    model_ids = dict(zip(recipe['scenery']['source_models'], models))
    color_oid = struct.unpack_from('>I', instances[0][1], 152)[0]
    page = struct.unpack_from('>I', instances[0][1], 116)[0]
    if color_oid >> 24 != track:
        raise ValueError('Expected course-owned scenery colors')
    needed, assets, added = set(), [], []
    for source_id in source_ids:
        instance = scene.instances[source_id]
        model = scene.models[instance['model']]
        if instance['model'] not in model_ids or eligibility(model):
            raise ValueError('Countdown model is not a retained supported static prefab')
        materials = sorted({m['material'] for p in model['parts'] for m in p['meshes']})
        flips = []
        for material in materials:
            m = scene.materials[material]
            needed.add(m['texture'])
            if m['flipbook'] != -1:
                frames = scene.flipbooks[m['flipbook']]
                needed.update(frames)
                flips.append(dict(material=material, flipbook=m['flipbook'], frames=frames))
        rid = len(instances)+len(added)
        scale = 4 if model['parts'][0]['meshes'][0]['strips'][0]['opcode'] == 0x9b else 1
        payload = instance_record(instance, recipe['matrix'], recipe['translation'], scale,
                                  lambda value: track << 24 | value, rid,
                                  model_ids[instance['model']], color_oid & 0xffffff, page)
        added.append(record(3, rid, payload, track))
        assets.append(dict(source_instance=source_id, target_instance=rid,
                           source_model=instance['model'], target_model=model_ids[instance['model']],
                           flipbooks=flips))
    scripts = [(e, p) for e, p in rows if e['kind'] == 16]
    if len(scripts) != 1 or scripts[0][0]['track'] != track:
        raise ValueError('Expected one course-owned script binding table')
    script, binding = append_hidden_bindings(scripts[0][1], len(instances), len(added), mode)
    changed = [(dict(e, size=len(script)), script) if e == scripts[0][0] else (e, p) for e, p in rows]
    changed += added
    changed.sort(key=lambda r: WORLD_RESOURCE_ORDER.index(r[0]['kind']))
    texture_ids = {int(k): v for k, v in recipe['scenery']['texture_ids'].items()}
    texture_group = page & 0xffff
    textures = world.records(texture_group)
    if any(source_id >= len(images) for source_id in needed):
        raise ValueError('Countdown image is absent from donor GSH')
    missing = sorted(needed-texture_ids.keys())
    for source_id, target_id in zip(missing, unused_global_rids(world, 9, len(missing))):
        texture_ids[source_id] = target_id
        textures.append(record(9, target_id, world_image_record(images[source_id]), 255))
    for source_id in needed:
        expected = world_image_record(images[source_id])
        if not any(e['kind'] == 9 and e['rid'] == texture_ids[source_id] and p == expected for e, p in textures):
            raise ValueError('Countdown image mapping does not match donor pixels')
    return {group: changed, texture_group: textures}, dict(
        profile='tricky-gc-countdown-assets-v2', assets=assets, binding=binding,
        new_images=missing, frame_texture_ids={str(k): texture_ids[k] for k in sorted(needed)},
        source_instance_map={str(a['target_instance']): a['source_instance'] for a in assets},
        runtime_binding=False, countdown_verified=False, restart_verified=False,
        limitation=dict(
            hidden='Hidden asset staging only; no countdown event, timing, visibility or flipbook execution',
            visible='Always-visible asset staging; no countdown event, timing or flipbook execution',
            countdown='Handler-ready staging; the definition differs from ordinary scenery only in the '
                      'visibility bit. Nothing drives it here, and no timing or flipbook executes.')[mode])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base-build', 'nbd', 'gsf', 'textures', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--visible', action='store_true',
                      help='Stage the countdown models always visible, to check placement '
                           'and the definition visibility bit before any event binding')
    mode.add_argument('--countdown-ready', action='store_true',
                      help='Stage them hidden but otherwise shaped like ordinary scenery, so a '
                           'handler shows and hides them by toggling the visibility bit alone')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh candidate directory')
    recipe = json.loads((args.base_build/'experiment.json').read_text())
    original = (args.base_build/'BAM.BIG').read_bytes()
    nbd, gsf = args.nbd.read_bytes(), args.gsf.read_bytes()
    if (hashlib.sha256(original).hexdigest() != recipe['output_sha256'] or
            hashlib.sha256(nbd).hexdigest() != recipe['scenery']['source_sha256'] or
            hashlib.sha256(gsf).hexdigest() != recipe['visibility']['source_gsf_sha256']):
        raise ValueError('Base archive or donor NBD/GSF does not match recipe')
    scene = TrickyScenery(nbd, gsf)
    replacements, report = stage(World(original), recipe, scene, shape_images(args.textures.read_bytes()),
                                  post_countdown_hidden(gsf, len(scene.instances)),
                                  'visible' if args.visible else
                                  'countdown' if args.countdown_ready else 'hidden')
    result, _ = assemble(World(original), replacements)
    report.update(base_sha256=hashlib.sha256(original).hexdigest(),
                  archive_sha256=hashlib.sha256(result).hexdigest(),
                  source_gsf_sha256=hashlib.sha256(gsf).hexdigest(),
                  resource_count=validate_resource_capacities(World(result)))
    recipe['startgate'] = report
    recipe['output_sha256'] = report['archive_sha256']
    # Keep the verified racing scenery map intact: hidden, unbound additions
    # live in the explicit staging report until the lifecycle compiler owns them.
    args.output.mkdir(parents=True)
    (args.output/'BAM.BIG').write_bytes(result)
    (args.output/'experiment.json').write_text(json.dumps(recipe, indent=2)+'\n')
    (args.output/'startgate.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
