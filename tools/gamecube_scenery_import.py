#!/usr/bin/env python3
"""Experimental static Tricky scenery import into an existing GC terrain build.

The neutral vertex colors and material flags are diagnostic controls. This
is not yet a complete donor lighting, animation, collision or rail conversion.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

from gamecube_scenery import TrickyScenery, buffer_group
from gamecube_textures import shape_images, world_image_record
from gamecube_world import World, assemble, unused_global_rids, validate_resource_capacities
from import_terrain import apply
from patch_geometry import outward_float32

# GXBE69 world group order: buffers, contiguous geometry/instances/terrain,
# then metadata. The group memory-size field counts that middle section.
WORLD_RESOURCE_ORDER = (25, 26, 27, 24, 23, 0, 6, 7, 2, 3, 4, 5, 1, 8, 12, 11,
                        13, 15, 17, 20, 14, 16, 18, 21, 22)


def pack(fmt, *values):
    return struct.pack('>' + fmt, *values)


def prune_geometry_texture_page(world, replacements, page):
    """Rebuild a static geometry page's residency from its surviving users.

    This applies to a replaced terrain/scenery page, not a character, effect,
    or scripted image bank. Global image IDs and copies on other pages stay
    intact. Follow instances through models/materials, including users in
    other groups, before removing this page's obsolete host image copies.
    """
    resources = {}
    users = []
    for group in world.index['groups']:
        rows = replacements.get(group['index'])
        if rows is None:
            if not any(group['kind_counts'].get(k) for k in (0, 1, 2, 3)):
                continue
            rows = world.records(group['index'])
        for entry, payload in rows:
            kind = entry['kind']
            if kind in (0, 2) and payload:
                key = kind, (entry['track'] << 24) | entry['rid']
                if key in resources and resources[key] != payload:
                    raise ValueError(f'Conflicting geometry resource {key}')
                resources[key] = payload
            if kind in (1, 3) and payload:
                offset = 412 if kind == 1 else 116
                if len(payload) < offset + 8:
                    raise ValueError('Truncated texture-page user')
                if struct.unpack_from('>I', payload, offset)[0] & 0xffff == page:
                    users.append((kind, payload))
    needed = {9: set(), 10: set()}
    for kind, payload in users:
        if kind == 1:
            texture, lightmap = struct.unpack_from('>HH', payload, 416)
            needed[9].add(texture)
            needed[10].add(lightmap)
            continue
        oid = struct.unpack_from('>I', payload, 120)[0]
        model = resources.get((2, oid))
        if model is None or len(model) < 36:
            raise ValueError(f'Missing model for texture page: {oid:#x}')
        table = struct.unpack_from('>I', model, 12)[0]
        if table + 4 > len(model):
            raise ValueError('Invalid model material table')
        count = struct.unpack_from('>I', model, table)[0]
        if table + 4 + 4*count > len(model):
            raise ValueError('Truncated model material table')
        for i in range(count):
            material_oid = struct.unpack_from('>I', model, table + 4 + 4*i)[0]
            material = resources.get((0, material_oid))
            if material is None or len(material) < 8:
                raise ValueError(f'Missing material for texture page: {material_oid:#x}')
            needed[9].update(struct.unpack_from('>4H', material))
    for ids in needed.values():
        ids.discard(0xffff)
    rows = replacements.get(page)
    if rows is None:
        rows = world.records(page)
    available = {k: {e['rid'] for e, _ in rows if e['kind'] == k} for k in needed}
    for kind in needed:
        if needed[kind] - available[kind]:
            raise ValueError(f'Texture page {page} lacks kind {kind}: {sorted(needed[kind] - available[kind])}')
    dropped = [(e, p) for e, p in rows if e['kind'] in needed and e['rid'] not in needed[e['kind']]]
    kept = [(e, p) for e, p in rows if e['kind'] not in needed or e['rid'] in needed[e['kind']]]
    return kept, dict(page=page, geometry_users=len(users),
                      dropped_images=[dict(kind=e['kind'], rid=e['rid']) for e, _ in dropped],
                      reclaimed_bytes=sum(8 + len(p) for _, p in dropped))


def record(kind, rid, payload, track):
    return dict(kind=kind, rid=rid, track=track, size=len(payload)), bytes(payload)


def geometry_parts(model):
    """The parts that actually carry geometry.

    Every multipart donor model has exactly one part with no meshes: a
    transform-free root the geometry hangs from (parent 0xffffffff, no matrix,
    no bounds). Counting it made a model with a single geometry part look
    multipart, which dropped models 132/133/153 -- 13 placements -- although
    they need nothing the importer does not already do. An empty part that
    carries its own matrix is a real transform, so it stays counted and the
    model is still rejected.
    """
    return [p for p in model['parts'] if p['meshes'] or p['matrix'] is not None]


def eligibility(model, animated_as_static=False):
    """Why this model cannot be imported, or None.

    `animated_as_static` admits a model whose single geometry part carries
    animation, importing its rest-pose display lists and ignoring the
    animation. That is a deliberate downgrade, not animation support: the
    part's geometry is read the same way either way, since `animated` only
    reports that the part object names separate animation data.
    """
    parts = geometry_parts(model)
    if len(parts) != 1:
        return 'multipart'
    part = parts[0]
    if part['animated'] and not animated_as_static:
        return 'animated'
    if part['matrix'] is not None:
        return 'local matrix'
    normals = {v[1] for mesh in part['meshes'] for strip in mesh['strips'] for v in strip['vertices']}
    if len(normals) > 256:
        return 'normal palette exceeds 256'
    opcodes = {strip['opcode'] for mesh in part['meshes'] for strip in mesh['strips']}
    if len(opcodes) != 1:
        return 'mixed or absent position formats'
    return None


def validate_reclamation(world, group, track):
    """Reject retained model/instance/buffer references into retired arrays."""
    retired = {(e['kind'], e['track'], e['rid']) for e, _ in world.records(group)
               if e['track'] == track and e['kind'] in (2, 23, 24, 25, 26, 27)}
    references = {2: [(24, 23)], 3: [(120, 2), (152, 24)],
                  23: [(0, 25), (4, 27), (8, 26)]}
    checked = 0
    for row in world.index['groups']:
        # Vertex groups live beside models; kind 23 has no per-group count.
        if not (row['kind_counts'].get(2) or row['kind_counts'].get(3)):
            continue
        for entry, payload in world.records(row['index']):
            key = entry['kind'], entry['track'], entry['rid']
            if key in retired:
                continue
            for offset, kind in references.get(entry['kind'], []):
                if len(payload) < offset + 4:  # Empty resource references have no body.
                    continue
                target = struct.unpack_from('>I', payload, offset)[0]
                checked += 1
                if (kind, target >> 24, target & 0xffffff) in retired:
                    raise ValueError(f'Retained resource {key} refers to retired kind {kind} ID {target:#x}')
    return checked


def model_record(model, oid, model_id, buffer_id, material_ids, animated_as_static=False):
    reason = eligibility(model, animated_as_static)
    if reason:
        raise ValueError(f'Model {model["rid"]}: {reason}')
    part = geometry_parts(model)[0]
    normals = sorted({v[1] for mesh in part['meshes'] for strip in mesh['strips'] for v in strip['vertices']})
    normal_ids = {n: i for i, n in enumerate(normals)}
    materials = list(dict.fromkeys(mesh['material'] for mesh in part['meshes']))
    meshes = part['meshes']
    objects = 36 + 4 * len(materials)
    geometry = objects + 16
    table = geometry + 36
    headers = table + 4 * len(meshes)
    display_lists = (headers + 12 * len(meshes) + 31) // 32 * 32
    data = bytearray(display_lists)
    struct.pack_into('>5If3I', data, 0, oid(model_id), 1, objects, 32, 1, 0,
                     oid(buffer_id), display_lists, len(materials))
    for i, material in enumerate(materials):
        struct.pack_into('>I', data, 36 + 4*i, oid(material_ids[material]))
    struct.pack_into('>4I', data, objects, 0xffffffff, geometry, 0, 0xffffffff)
    # The target VAT uses quarter-unit positions. Keep source whole-unit
    # vertices exact by compensating in the instance matrix and local bounds.
    scale = 4 if meshes[0]['strips'][0]['opcode'] == 0x9b else 1
    # Donor geometry flags are not a target ABI. Copying Tricky bit 0 makes
    # SSX 3 mutate unrelated display-list bytes during riding (probe 018).
    # Encode the tested static/precolored path explicitly; translating the
    # donor's dynamic lighting behavior needs its own storage/layout profile.
    struct.pack_into('>6f3I', data, geometry, *(v/scale for v in part['bounds']),
                     0, len(meshes), table)
    for i, mesh in enumerate(meshes):
        display = bytearray()
        for strip in mesh['strips']:
            display += pack('BH', 0x9a, len(strip['vertices']))
            for position, normal, uv in strip['vertices']:
                display += pack('HBHH', position, normal_ids[normal], position, uv)
        display += bytes(-len(display) % 32)
        struct.pack_into('>I', data, table + 4*i, headers + 12*i)
        struct.pack_into('>HHII', data, headers + 12*i, materials.index(mesh['material']),
                         1, len(data) - display_lists, len(display))
        data += display
    return bytes(data), normals, scale


def instance_record(source, matrix, translation, scale, oid, instance_id, model_id, color_id, page):
    src = source['matrix']
    transformed = []
    for row in range(3):
        transformed += [v*scale for v in apply(matrix, [0, 0, 0], src[row*4:row*4+3])] + [0]
    transformed += apply(matrix, translation, src[12:15]) + [1]
    corners = [apply(matrix, translation, c) for c in itertools.product(
        *[(source['bounds'][k], source['bounds'][k+3]) for k in range(3)])]
    low = [outward_float32(min(c[k] for c in corners)-1, False) for k in range(3)]
    high = [outward_float32(max(c[k] for c in corners)+1, True) for k in range(3)]
    center = [struct.unpack('>f', pack('f', (low[k]+high[k])/2))[0] for k in range(3)]
    radius = outward_float32(max(math.dist(center, c) for c in itertools.product(*zip(low, high))), True)
    data = bytearray(160)
    struct.pack_into('>16f4f6f3If', data, 8, *transformed, *center, radius, *low, *high,
                     oid(instance_id), page, oid(model_id), 1)
    struct.pack_into('>H', data, 144, 0xffff)
    struct.pack_into('>2I', data, 152, oid(color_id), 0)
    return bytes(data)


def compile_static(source, records, texture_ids, matrix, translation, track, page, model_ids,
                   reclaim_host_models=False, animated_as_static=()):
    """Preserve existing resources and allocate each new kind independently."""
    def oid(rid):
        if not 0 <= rid < 0x7fff:
            raise ValueError('Scenery RID exceeds signed table capacity')
        return track << 24 | rid

    def next_id(kind):
        return max((e['rid'] for e, _ in records if e['kind'] == kind and e['track'] == track), default=-1) + 1

    position_id, uv_id, color_id = [next_id(k) for k in (25, 27, 24)]
    first_normal, first_buffer, first_model, first_instance = [next_id(k) for k in (26, 23, 2, 3)]
    materials = sorted({mesh['material'] for i in model_ids for p in source.models[i]['parts'] for mesh in p['meshes']})
    material_ids = {src: next_id(0) + i for i, src in enumerate(materials)}
    added = [record(25, position_id, b''.join(pack('3h', *v) for v in source.positions), track),
             record(27, uv_id, b''.join(pack('2h', *v) for v in source.uvs), track),
             record(24, color_id, pack('H', 0x7bef) * len(source.positions), track)]
    for src, dst in material_ids.items():
        texture = texture_ids[source.materials[src]['texture']]
        added.append(record(0, dst, pack('4HI2HI', texture, 65535, 65535, 65535, 0, 7, 1, 0xffffffff), track))
    converted, instances, hidden = [], [], []
    for index, source_id in enumerate(model_ids):
        model_id, buffer_id, normal_id = first_model+index, first_buffer+index, first_normal+index
        data, normals, scale = model_record(source.models[source_id], oid, model_id, buffer_id,
                                            material_ids, source_id in animated_as_static)
        added.append(record(26, normal_id, b''.join(pack('3f', *(x/16384 for x in source.normals[n])) for n in normals), track))
        added.append(record(23, buffer_id, buffer_group(oid(position_id), oid(uv_id), oid(normal_id)), track))
        converted.append(record(2, model_id, data, track))
        for source_instance_id, instance in enumerate(source.instances):
            if instance['model'] == source_id:
                if not instance.get('gameplay', {}).get('visible', True):
                    hidden.append(source_instance_id)
                    continue
                rid = first_instance + len(instances)
                data = instance_record(instance, matrix, translation, scale, oid, rid, model_id, color_id, page)
                instances.append(record(3, rid, data, track))
    reclaimed = []
    if reclaim_host_models:
        if any(e['kind'] == 3 and e['track'] == track for e, _ in records):
            raise ValueError('Remove host instances and their event references before reclaiming models')
        # Preserve the ID reservations: a stale host reference must not select
        # a newly imported, unrelated model. Materials remain for particles.
        reclaimed = [r for r in records if r[0]['track'] == track and r[0]['kind'] in (2, 23, 24, 25, 26, 27)]
        records = [r for r in records if not (r[0]['track'] == track and r[0]['kind'] in (2, 23, 24, 25, 26, 27))]
    result = added + records + converted + instances
    if any(e['kind'] not in WORLD_RESOURCE_ORDER for e, _ in result):
        raise ValueError('Unsupported resource kind in scenery world group')
    result.sort(key=lambda r: WORLD_RESOURCE_ORDER.index(r[0]['kind']))
    return result, dict(source_models=model_ids, added_models=len(converted), added_instances=len(instances),
                        hidden_source_instances=hidden,
                        # Frozen at the rest pose. Named separately so a later reader cannot
                        # mistake their presence for animation support.
                        animated_imported_as_static=sorted(animated_as_static),
                        lighting_profile='neutral-diagnostic', collision=False, grind_splines=False,
                        reclaimed_host_records=len(reclaimed), reclaimed_host_bytes=sum(len(p) for _, p in reclaimed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-build', type=Path, required=True)
    parser.add_argument('--nbd', type=Path, required=True)
    parser.add_argument('--textures', type=Path, required=True)
    parser.add_argument('--gsf', type=Path, required=True,
                        help='Donor gameplay data: honor initial instance visibility')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--group', type=int, default=36)
    parser.add_argument('--texture-group', type=int, default=31)
    parser.add_argument('--page', type=lambda v: int(v, 0), default=0x0008001f)
    parser.add_argument('--models', type=int, nargs='+')
    parser.add_argument('--reclaim-host-models', action='store_true',
                        help='Remove unplaced host models/buffers while preserving their IDs as holes')
    parser.add_argument('--reclaim-geometry-textures', action='store_true',
                        help='Rebuild the replaced static geometry page from surviving terrain/model users')
    parser.add_argument('--animated-as-static', action='store_true',
                        help='Import animated single-part prefabs frozen at their rest pose. They are '
                             'absent today, so this trades still geometry for nothing at all. It is not '
                             'animation support and does not import any animation data.')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output exists; use a fresh experiment directory')
    experiment = json.loads((args.base_build/'experiment.json').read_text())
    if args.reclaim_geometry_textures and experiment.get('mode') != 'gamecube-replace-terrain':
        raise ValueError('Texture reclamation requires a replaced static terrain/scenery page')
    if args.reclaim_geometry_textures and (args.page & 0xffff) != args.texture_group:
        raise ValueError('Scenery page must match the reclaimed texture group')
    source = TrickyScenery(args.nbd.read_bytes(), args.gsf.read_bytes(), phase='racing')
    world = World((args.base_build/'BAM.BIG').read_bytes())
    records = world.records(args.group)
    location = next(l for l in world.index['locations'] if l['group_start'] <= args.group <= l['last_group'])
    reclamation_references = validate_reclamation(world, args.group, location['index']) if args.reclaim_host_models else 0
    omitted = {m['rid']: reason for m in source.models
               if (reason := eligibility(m, args.animated_as_static))}
    # Only single-geometry-part models can be frozen; a genuinely multipart one
    # is still rejected above, so this set never widens past what was imported.
    frozen = {m['rid'] for m in source.models
              if args.animated_as_static and m['rid'] not in omitted
              and geometry_parts(m)[0]['animated']}
    ids = args.models if args.models is not None else [m['rid'] for m in source.models if m['rid'] not in omitted]
    if len(set(ids)) != len(ids) or any(not 0 <= i < len(source.models) for i in ids):
        raise ValueError('Invalid or duplicate model selection')
    for i in ids:
        if i in omitted:
            raise ValueError(f'Model {i}: {omitted[i]}')
    textures = world.records(args.texture_group)
    images = shape_images(args.textures.read_bytes())
    texture_ids = {int(k): v for k, v in experiment['textures']['textures'].items()}
    needed = sorted({source.materials[mesh['material']]['texture'] for i in ids
                     for p in source.models[i]['parts'] for mesh in p['meshes']} - texture_ids.keys())
    for src, dst in zip(needed, unused_global_rids(world, 9, len(needed))):
        texture_ids[src] = dst
        textures.append(record(9, dst, world_image_record(images[src]), 255))
    records, report = compile_static(source, records, texture_ids, experiment['matrix'], experiment['translation'],
                                     location['index'], args.page, ids, args.reclaim_host_models,
                                     frozen & set(ids))
    if args.reclaim_geometry_textures:
        textures, report['texture_residency'] = prune_geometry_texture_page(
            world, {args.group: records, args.texture_group: textures}, args.texture_group)
    archive, _ = assemble(world, {args.group: records, args.texture_group: textures})
    report.update(omitted_models=omitted, new_textures=needed, texture_ids=texture_ids,
                  visibility_profile='tricky-gc-post-countdown-v1',
                  post_countdown_hidden=source.post_countdown_hidden,
                  geometry_profile='static-precolored-gc-v1',
                  reclamation_references_checked=reclamation_references,
                  resource_count=validate_resource_capacities(World(archive)),
                  archive_sha256=hashlib.sha256(archive).hexdigest(),
                  gameplay_sha256=hashlib.sha256(args.gsf.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(args.nbd.read_bytes()).hexdigest())
    experiment['scenery'] = report
    args.output.mkdir(parents=True)
    (args.output/'BAM.BIG').write_bytes(archive)
    (args.output/'scenery.json').write_text(json.dumps(report, indent=2)+'\n')
    (args.output/'experiment.json').write_text(json.dumps(experiment, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
