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

IDENTITY = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

# A display-list vertex stores its position index as a halfword.
POSITION_LIMIT = 0x10000


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


def geometry_part_items(model):
    """The parts that actually carry geometry, with their index in `parts`.

    Every multipart donor model has exactly one part with no meshes: a
    transform-free root the geometry hangs from (parent 0xffffffff, no matrix,
    no bounds). Counting it made a model with a single geometry part look
    multipart, which dropped models 132/133/153 -- 13 placements -- although
    they need nothing the importer does not already do. An empty part that
    carries its own matrix is a real transform, so it stays counted; without
    `--compose-local-matrices` the model is still rejected.

    The index is the part's own position in `model['parts']`, which is what
    `parent` references and what keys the composed per-part vertex copies.
    """
    return [(i, p) for i, p in enumerate(model['parts']) if p['meshes'] or p['matrix'] is not None]


def geometry_parts(model):
    return [p for _, p in geometry_part_items(model)]


def multiply(a, b):
    """Row-vector 4x4 product: `a` applied first, then `b`."""
    return tuple(sum(a[4*r+k] * b[4*k+c] for k in range(4)) for r in range(4) for c in range(4))


def transform_point(m, p):
    return [sum(p[k] * m[4*k+c] for k in range(3)) + m[12+c] for c in range(3)]


def transform_direction(m, v):
    return [sum(v[k] * m[4*k+c] for k in range(3)) for c in range(3)]


def composed_matrices(model):
    """Every part's matrix composed with its parent chain.

    A donor part matrix is 16 floats in the same row-vector layout the importer
    already reads from an instance: rows 0-2 are the basis and row 3 is the
    translation, which is how `instance_record` consumes `src[row*4:row*4+3]`
    and `src[12:15]`. Verified against the donor rather than assumed: composing
    model 49's parts as child x parent and pushing its vertices through the
    donor instance matrix reproduces that instance's own authored bounds to
    0.2 units, which ignoring the part matrices does not.

    `parent` indexes an earlier part (the reader rejects a forward or cyclic
    reference); the transform-free root is 0xffffffff.
    """
    out = []
    for part in model['parts']:
        local = part['matrix'] if part['matrix'] is not None else IDENTITY
        out.append(local if part['parent'] == 0xffffffff else multiply(local, out[part['parent']]))
    return out


def orthonormal(m, tolerance=1e-4):
    """A rigid transform: normals may be rotated instead of inverse-transposed."""
    if tuple(m[3::4]) != (0.0, 0.0, 0.0, 1.0):
        return False
    rows = [m[4*i:4*i+3] for i in range(3)]
    return all(abs(sum(rows[a][k]*rows[b][k] for k in range(3)) - (a == b)) <= tolerance
               for a in range(3) for b in range(3))


def needs_composition(model):
    """Whether importing this model means baking part matrices into vertices."""
    parts = geometry_parts(model)
    return len(parts) != 1 or parts[0]['matrix'] is not None


def eligibility(model, animated_as_static=False, compose_local_matrices=False):
    """Why this model cannot be imported, or None.

    `animated_as_static` admits a model whose single geometry part carries
    animation, importing its rest-pose display lists and ignoring the
    animation. That is a deliberate downgrade, not animation support: the
    part's geometry is read the same way either way, since `animated` only
    reports that the part object names separate animation data.

    `compose_local_matrices` admits a model whose parts carry local matrices by
    baking each composed matrix into transformed vertex copies (see
    `composition`). It is likewise a downgrade, not a scene-graph: the parts
    collapse into one rigid target part and any animation that would have
    driven those matrices is discarded.
    """
    parts = geometry_parts(model)
    composing = compose_local_matrices and needs_composition(model)
    if not composing and len(parts) != 1:
        return 'multipart'
    if any(p['animated'] for p in parts) and not animated_as_static:
        return 'animated'
    if not composing and parts[0]['matrix'] is not None:
        return 'local matrix'
    if composing:
        if not any(p['meshes'] for p in parts):
            return 'no geometry to compose'
        # Rotating a normal by the basis is only the inverse transpose for a
        # rigid transform. Every Garibaldi part matrix is orthonormal to 1e-11.
        if not all(orthonormal(m) for m in composed_matrices(model)):
            return 'non-orthonormal local matrix'
    items = geometry_part_items(model)
    normals = {(i, v[1]) for i, p in items for mesh in p['meshes']
               for strip in mesh['strips'] for v in strip['vertices']}
    if len(normals) > 256:
        return 'normal palette exceeds 256'
    opcodes = {strip['opcode'] for _, p in items for mesh in p['meshes'] for strip in mesh['strips']}
    if len(opcodes) != 1:
        return 'mixed or absent position formats'
    return None


def model_scale(model):
    """The instance compensation for this model's donor position format.

    The target VAT reads quarter units. A donor 0x9b model stores whole units,
    so its instance basis is multiplied by 4 and its local bounds divided by
    it. Shared by the collision importer so both derive one scale per model
    rather than reading the first part's first strip.
    """
    opcodes = {strip['opcode'] for _, p in geometry_part_items(model)
               for mesh in p['meshes'] for strip in mesh['strips']}
    if len(opcodes) != 1:
        raise ValueError(f'Model {model["rid"]}: mixed or absent position formats')
    return 4 if opcodes.pop() == 0x9b else 1


def composition(scene, model):
    """Bake a matrix-carrying model's part transforms into vertex copies.

    None when the model needs none. Otherwise a dict of

    * `vertices`: `{(part, source position): stored signed-16 triple}`
    * `normals`: `{(part, source normal): unit float triple}`
    * `bounds`: 6 donor-unit floats recomputed from the transformed positions
    * `parts`: how many geometry parts were composed

    Strip vertices index globally shared arrays, so a matrix cannot be applied
    in place; the caller appends these copies and remaps that model's indices.

    Donor stored positions are quarter units for the 1x format and whole units
    for the 4x one, so a donor-unit point is `stored/4` or `stored` and the
    inverse restores the encoding. A transformed position that leaves the
    signed 16-bit range raises: the model is refused, never re-encoded wrong.
    """
    if not needs_composition(model):
        return None
    matrices = composed_matrices(model)
    scale = model_scale(model)
    unit = 0.25 if scale == 1 else 1.0
    vertices, normals, stored = {}, {}, []
    for i, part in geometry_part_items(model):
        matrix = matrices[i]
        for mesh in part['meshes']:
            for strip in mesh['strips']:
                for position, normal, _ in strip['vertices']:
                    if (i, position) not in vertices:
                        point = transform_point(matrix, [v*unit for v in scene.positions[position]])
                        value = tuple(math.floor(v/unit + 0.5) for v in point)
                        if any(not -0x8000 <= v <= 0x7fff for v in value):
                            raise ValueError(
                                f'Model {model["rid"]}: composed position {value} on part {i} '
                                f'leaves the signed 16-bit {scale}x encoding')
                        vertices[i, position] = value
                        stored.append(value)
                    if (i, normal) not in normals:
                        direction = transform_direction(matrix, [v/16384 for v in scene.normals[normal]])
                        length = math.dist(direction, (0, 0, 0)) or 1.0
                        normals[i, normal] = tuple(v/length for v in direction)
    bounds = tuple([min(v[k] for v in stored)*unit for k in range(3)] +
                   [max(v[k] for v in stored)*unit for k in range(3)])
    return dict(vertices=vertices, normals=normals, bounds=bounds,
                parts=sum(1 for _, p in geometry_part_items(model) if p['meshes']))


def screen_compositions(scene, omitted):
    """Refuse models whose composed positions leave the 16-bit encoding.

    The range check needs the transformed vertices, so it cannot live in
    `eligibility()`. `omitted` gains the model with a reason; the returned map
    keeps the message, so the receipt names the model instead of the importer
    silently emitting a re-encoded position that does not fit.
    """
    out_of_range = {}
    for model in scene.models:
        if model['rid'] in omitted or not needs_composition(model):
            continue
        try:
            composition(scene, model)
        except ValueError as error:
            out_of_range[model['rid']] = str(error)
            omitted[model['rid']] = 'local matrix out of range'
    return out_of_range


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


def model_record(model, oid, model_id, buffer_id, material_ids, animated_as_static=False, compose=None):
    """One rigid target part. `compose` bakes donor part matrices into it.

    When composing, `compose` is a `composition()` result carrying an extra
    `index` map from `(part, source position)` to the global position index of
    the transformed copy. Every geometry part's meshes are emitted into the one
    target part, because the matrices that separated them are now in the
    vertices; the palette and bounds follow the transformed data.
    """
    reason = eligibility(model, animated_as_static, compose is not None)
    if reason:
        raise ValueError(f'Model {model["rid"]}: {reason}')
    meshes = [(i, mesh) for i, part in geometry_part_items(model) for mesh in part['meshes']]
    normals = sorted({(i, v[1]) for i, mesh in meshes for strip in mesh['strips'] for v in strip['vertices']})
    normal_ids = {n: i for i, n in enumerate(normals)}
    materials = list(dict.fromkeys(mesh['material'] for _, mesh in meshes))
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
    scale = model_scale(model)
    # Composed bounds come from the transformed copies, not the donor's
    # per-part bounds, which are stated in each part's own pre-matrix space.
    bounds = compose['bounds'] if compose else geometry_parts(model)[0]['bounds']
    # Donor geometry flags are not a target ABI. Copying Tricky bit 0 makes
    # SSX 3 mutate unrelated display-list bytes during riding (probe 018).
    # Encode the tested static/precolored path explicitly; translating the
    # donor's dynamic lighting behavior needs its own storage/layout profile.
    struct.pack_into('>6f3I', data, geometry, *(v/scale for v in bounds),
                     0, len(meshes), table)
    for i, (part_index, mesh) in enumerate(meshes):
        display = bytearray()
        for strip in mesh['strips']:
            display += pack('BH', 0x9a, len(strip['vertices']))
            for position, normal, uv in strip['vertices']:
                if compose:
                    position = compose['index'][part_index, position]
                display += pack('HBHH', position, normal_ids[part_index, normal], position, uv)
        display += bytes(-len(display) % 32)
        struct.pack_into('>I', data, table + 4*i, headers + 12*i)
        struct.pack_into('>HHII', data, headers + 12*i, materials.index(mesh['material']),
                         1, len(data) - display_lists, len(display))
        data += display
    return bytes(data), normals, scale


def instance_record(source, matrix, translation, scale, oid, instance_id, model_id, color_id, page,
                    local_bounds=None):
    """`local_bounds` replaces the donor's authored world bounds for a composed
    model. The donor's bounds for models 280-282 were authored from the
    unrotated part, so they no longer contain the composed geometry; the model
    box is taken through the instance matrix instead. The collision importer
    re-derives this record byte for byte, so it composes the same bounds.
    """
    src = source['matrix']
    transformed = []
    for row in range(3):
        transformed += [v*scale for v in apply(matrix, [0, 0, 0], src[row*4:row*4+3])] + [0]
    transformed += apply(matrix, translation, src[12:15]) + [1]
    box = source['bounds'] if local_bounds is None else local_bounds
    corners = [apply(matrix, translation, c if local_bounds is None else transform_point(src, c))
               for c in itertools.product(*[(box[k], box[k+3]) for k in range(3)])]
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
                   reclaim_host_models=False, animated_as_static=(), compose_local_matrices=False):
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
    added = []
    for src, dst in material_ids.items():
        texture = texture_ids[source.materials[src]['texture']]
        added.append(record(0, dst, pack('4HI2HI', texture, 65535, 65535, 65535, 0, 7, 1, 0xffffffff), track))
    # Transformed vertex copies extend the shared arrays rather than replacing
    # entries in them: a stored position is referenced by every model that
    # happens to use that value.
    positions = list(source.positions)
    reuse = {}
    for i, value in enumerate(positions):
        reuse.setdefault(value, i)
    converted, instances, hidden, composed = [], [], [], {}
    for index, source_id in enumerate(model_ids):
        model = source.models[source_id]
        model_id, buffer_id, normal_id = first_model+index, first_buffer+index, first_normal+index
        compose = composition(source, model) if compose_local_matrices else None
        if compose is not None:
            compose['index'] = {}
            for key, value in compose['vertices'].items():
                if value not in reuse:
                    reuse[value] = len(positions)
                    positions.append(value)
                compose['index'][key] = reuse[value]
            composed[source_id] = compose['parts']
        data, normals, scale = model_record(model, oid, model_id, buffer_id, material_ids,
                                            source_id in animated_as_static, compose)
        added.append(record(26, normal_id, b''.join(
            pack('3f', *(compose['normals'][key] if compose else
                         [x/16384 for x in source.normals[key[1]]])) for key in normals), track))
        added.append(record(23, buffer_id, buffer_group(oid(position_id), oid(uv_id), oid(normal_id)), track))
        converted.append(record(2, model_id, data, track))
        for source_instance_id, instance in enumerate(source.instances):
            if instance['model'] == source_id:
                if not instance.get('gameplay', {}).get('visible', True):
                    hidden.append(source_instance_id)
                    continue
                rid = first_instance + len(instances)
                data = instance_record(instance, matrix, translation, scale, oid, rid, model_id,
                                       color_id, page, compose and compose['bounds'])
                instances.append(record(3, rid, data, track))
    if len(positions) > POSITION_LIMIT:
        raise ValueError(f'Composed positions exceed the halfword vertex index: {len(positions)}')
    added = [record(25, position_id, b''.join(pack('3h', *v) for v in positions), track),
             record(27, uv_id, b''.join(pack('2h', *v) for v in source.uvs), track),
             record(24, color_id, pack('H', 0x7bef) * len(positions), track)] + added
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
                        # Part matrices baked into vertex copies, per model the
                        # number of geometry parts collapsed into one rigid
                        # part. This is composition, never animated transforms.
                        local_matrix_composed={str(k): v for k, v in sorted(composed.items())},
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
    parser.add_argument('--compose-local-matrices', action='store_true',
                        help='Admit models whose parts carry a local matrix by baking each composed '
                             'part matrix into transformed vertex copies. The parts collapse into one '
                             'rigid part; this is not a scene graph and not animated transforms. A '
                             'model whose result leaves the signed 16-bit encoding is refused and '
                             'listed as local_matrix_out_of_range.')
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
               if (reason := eligibility(m, args.animated_as_static, args.compose_local_matrices))}
    out_of_range = screen_compositions(source, omitted) if args.compose_local_matrices else {}
    # A frozen model's animation is discarded at its rest pose, whether or not
    # its parts were also composed, so this set never widens past the imported.
    frozen = {m['rid'] for m in source.models
              if args.animated_as_static and m['rid'] not in omitted
              and any(p['animated'] for p in geometry_parts(m))}
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
                                     frozen & set(ids), args.compose_local_matrices)
    if args.reclaim_geometry_textures:
        textures, report['texture_residency'] = prune_geometry_texture_page(
            world, {args.group: records, args.texture_group: textures}, args.texture_group)
    archive, _ = assemble(world, {args.group: records, args.texture_group: textures})
    report.update(omitted_models=omitted, local_matrix_out_of_range={str(k): v for k, v in out_of_range.items()},
                  new_textures=needed, texture_ids=texture_ids,
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
