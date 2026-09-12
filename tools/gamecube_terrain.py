#!/usr/bin/env python3
"""Replace a GameCube SSX 3 location's terrain with a GameCube Tricky course.

GameCube counterpart of replace_terrain.py's terrain path. Terrain resources
are 430 bytes: header 0-31, corner UVs 32-63, 16 power-basis coefficient
vectors at 64 (big-endian floats, w = 1), bounding sphere at 320, four corner
positions at 336, bounds min/max at 384, ordinal (track << 24 | rid) at 408,
page reference at 412, packed index at 416, links at 420/424, two zero bytes.
Decoded by diffing the same Snow Jam patch on both discs (2026-09-11).
With --textures/--lightmaps the donor course's own sheets are appended to the
pinned texture group and each imported patch is bound to them (see
gamecube_textures.py).
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from gamecube_world import World, assemble, sha256
from gamecube_cleanup import clear_removed_instance_references, clear_script_bindings, disable_course_scripts, pin_texture_group
from import_terrain import transform_coefficients, surface_samples, UV_CORNERS
from probe_worlds import patch_point
from replace_terrain import placement
from course_route import make_reset_aip
from gamecube_textures import shape_images, tricky_bindings, import_course_textures

TRICKY_STRIDE, TRICKY_COEFF = 448, 80
GC_PATCH_SIZE = 430


def load_tricky_gc(nbd):
    raw = Path(nbd).read_bytes()
    count = struct.unpack_from('>I', raw, 8)[0]
    offset = struct.unpack_from('>I', raw, 68)[0]
    return [[list(struct.unpack_from('>4f', raw, offset + TRICKY_STRIDE * i + TRICKY_COEFF + j * 16)[:3])
             for j in range(16)] for i in range(count)]


def make_record(template, coeffs, rid, track):
    if len(template) != GC_PATCH_SIZE:
        raise ValueError('Template is not a GameCube terrain record')
    payload = bytearray(template)
    for j in range(16):
        struct.pack_into('>4f', payload, 64 + 16 * j, *coeffs[j], 1.0)
    pts = surface_samples(coeffs, 8)
    lo = [min(p[k] for p in pts) for k in range(3)]
    hi = [max(p[k] for p in pts) for k in range(3)]
    centre = [(lo[k] + hi[k]) / 2 for k in range(3)]
    struct.pack_into('>4f', payload, 320, *centre, math.dist(lo, hi) / 2)
    for k, (u, v) in enumerate(UV_CORNERS):
        struct.pack_into('>3f', payload, 336 + 12 * k, *patch_point(coeffs, u, v))
    struct.pack_into('>3f', payload, 384, *lo)
    struct.pack_into('>3f', payload, 396, *hi)
    struct.pack_into('>I', payload, 408, (track << 24) | rid)
    return bytes(payload)


def replace_patches(records, template_rid, patches, matrix, translation):
    old = [(e, p) for e, p in records if e['kind'] == 1]
    if not old or len({e['track'] for e, _ in old}) != 1:
        raise ValueError('Expected terrain on exactly one track in the target group')
    templates = [(e, p) for e, p in old if e['rid'] == template_rid]
    if len(templates) != 1:
        raise ValueError('Template patch not found')
    entry, template = templates[0]
    rids = [e['rid'] for e, _ in old]
    rids += list(range(max(rids) + 1, max(rids) + 1 + max(0, len(patches) - len(rids))))
    added = []
    for rid, coeffs in zip(rids, patches):
        transformed = transform_coefficients(coeffs, matrix, translation)
        transformed = [struct.unpack('>3f', struct.pack('>3f', *c)) for c in transformed]
        if not all(math.isfinite(x) for c in transformed for x in c):
            raise ValueError('Nonfinite terrain coefficients')
        payload = make_record(template, transformed, rid, entry['track'])
        added.append((dict(kind=1, size=GC_PATCH_SIZE, track=entry['track'], rid=rid), payload))
    out, inserted = [], False
    for e, p in records:
        if e['kind'] == 1:
            if not inserted:
                out.extend(added)
                inserted = True
        else:
            out.append((e, p))
    return out, added


def vector(value):
    parts = [float(x) for x in value.split(',')]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError('Expected x,y,z')
    return parts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path, help='Stock GameCube BAM.BIG')
    ap.add_argument('--nbd', type=Path, required=True, help='GameCube Tricky terrain (gari.nbd)')
    ap.add_argument('--location', default='ARA1')
    ap.add_argument('--template-rid', type=int, default=1673)
    ap.add_argument('--source-anchor', type=vector, required=True)
    ap.add_argument('--target-anchor', type=vector, required=True)
    ap.add_argument('--yaw', type=float, default=0.0)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--drop-kind', type=int, action='append', default=[])
    ap.add_argument('--limit', type=int, help='Use only the first N donor patches (memory experiments)')
    ap.add_argument('--clear-instance-references', action='store_true')
    ap.add_argument('--clear-script-bindings', action='store_true')
    ap.add_argument('--disable-course-scripts', action='store_true')
    ap.add_argument('--pin-texture-group', type=int, help='Keep one texture/lightmap group resident across the location')
    ap.add_argument('--textures', type=Path, help='Donor course .gsh: import its textures into the pinned group and bind the patches')
    ap.add_argument('--lightmaps', type=Path, help='Donor course _L.gsh lightmap sheets (with --textures)')
    ap.add_argument('--reset-aip', type=Path, help='Donor Tricky AIP: convert reset paths into the kind-14 resource')
    ap.add_argument('--relocate-freeride-start', action='store_true')
    ap.add_argument('--relocate-race-starts', action='store_true')
    ap.add_argument('--race-course', action='store_true', help='Donor race line on the whole gate track chain, gate riders on the donor start paths, regenerated kind-21 table')
    ap.add_argument('--roundtrip', action='store_true', help='Control build: rewrite the group unchanged')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--jobs', type=int, default=4)
    args = ap.parse_args()

    original = args.archive.read_bytes()
    world = World(original, 'big')
    loc = world.location(args.location)
    group = loc['last_group']
    records = world.records(group)
    matrix, translation = placement(args.source_anchor, args.target_anchor, args.yaw, args.scale)
    patches = load_tricky_gc(args.nbd)
    if args.limit:
        patches = patches[:args.limit]
    before = list(records)
    if args.roundtrip:
        new_records, added = list(records), [(e, p) for e, p in records if e['kind'] == 1]
    else:
        new_records, added = replace_patches(records, args.template_rid, patches, matrix, translation)
    removed, removed_records = {}, []
    if args.drop_kind:
        kept = []
        for e, p in new_records:
            if e['kind'] in args.drop_kind:
                removed[e['kind']] = removed.get(e['kind'], 0) + 1
                removed_records.append((e, p))
            else:
                kept.append((e, p))
        new_records = kept
    cleanup = {}
    if args.clear_instance_references:
        new_records, cleanup['cleared_instance_references'] = clear_removed_instance_references(new_records, removed_records)
    if args.clear_script_bindings:
        new_records, cleanup['script_bindings'] = clear_script_bindings(new_records, removed_records)
    if args.disable_course_scripts:
        new_records, cleanup['disabled_programs'] = disable_course_scripts(new_records)
    if args.reset_aip:
        # The path resource keeps the PS2 little-endian file format on GameCube.
        candidates = [(e, p) for e, p in new_records if e['kind'] == 14 and p]
        if len(candidates) != 1 or candidates[0][0]['rid'] != 0:
            raise ValueError('Expected one populated kind-14 path resource with ID zero')
        race = {} if args.race_course else None
        reset_data, cleanup['reset_paths'] = make_reset_aip(
            args.reset_aip.read_bytes(), matrix, translation, args.scale, candidates[0][1],
            relocate_start=args.relocate_freeride_start, relocate_race_starts=args.relocate_race_starts,
            race_course=race)
        cleanup['reset_paths'] = [cleanup['reset_paths']]
        new_records = [(dict(e, size=len(reset_data)), reset_data) if e['kind'] == 14 and e['rid'] == 0 else (e, p)
                       for e, p in new_records]
        if race:
            tables = [(e, p) for e, p in new_records if e['kind'] == 21]
            if len(tables) != 1 or tables[0][0]['rid'] != 0:
                raise ValueError('Expected one kind-21 race-line table with ID zero')
            new_records = [(dict(e, size=len(race['table'])), race['table']) if e['kind'] == 21 else (e, p)
                           for e, p in new_records]
            cleanup['race_line_table'] = [dict(bytes=len(race['table']), replaced_bytes=tables[0][0]['size'])]
    pinned = None
    if args.pin_texture_group is not None:
        pts = [patch_point([struct.unpack_from('>4f', p, 64 + 16 * j)[:3] for j in range(16)], u, v)
               for _, p in added for u, v in ((0, 0), (1, 1))]
        bounds = [[min(p[k] for p in pts) for k in range(3)], [max(p[k] for p in pts) for k in range(3)]]
        world.gdb_bytes, pinned = pin_texture_group(world.gdb_bytes, args.location, args.pin_texture_group, bounds)
        world.index = __import__('gamecube_world').parse_gdb(world.gdb_bytes, 'big')
        cleanup['pinned_texture_group'] = [pinned]
    replaced, textures = {group: new_records}, None
    if args.textures or args.lightmaps:
        if not (args.textures and args.lightmaps and args.pin_texture_group is not None):
            raise ValueError('--textures needs --lightmaps and --pin-texture-group')
        bindings = tricky_bindings(args.nbd.read_bytes())[:len(added)]
        texture_groups, rebound, textures = import_course_textures(
            world, args.location, args.pin_texture_group, added, bindings,
            shape_images(args.textures.read_bytes()), shape_images(args.lightmaps.read_bytes()))
        by_rid = {e['rid']: p for e, p in rebound}
        new_records = [(e, by_rid[e['rid']]) if e['kind'] == 1 else (e, p) for e, p in new_records]
        added = rebound
        replaced = {**texture_groups, group: new_records}
    archive, layout = assemble(world, replaced, jobs=args.jobs)

    # Readback verification.
    check = World(archive, 'big')
    got = check.records(group)
    if [e['rid'] for e, _ in got if e['kind'] == 1] != [e['rid'] for e, _ in added]:
        raise RuntimeError('Readback terrain rids differ')
    if [p for e, p in got if e['kind'] == 1] != [p for e, p in added]:
        raise RuntimeError('Readback terrain payloads differ')
    for g in world.index['groups']:
        if g['index'] not in replaced and check.original_group_blocks(g['index']) != world.original_group_blocks(g['index']):
            raise RuntimeError(f'Group {g["index"]} changed unexpectedly')
    g = check.index['groups'][group]
    if g['count'] != len(new_records):
        raise RuntimeError('Group index count mismatch after rebuild')
    if textures:
        key = lambda records: [((e['kind'], e['track'], e['rid']), p) for e, p in records]
        for tg_index, tg_records in replaced.items():
            if tg_index == group:
                continue
            tg = check.index['groups'][tg_index]
            if tg['count'] != len(tg_records) or key(check.records(tg_index)) != key(tg_records):
                raise RuntimeError(f'Readback texture group {tg_index} differs')
        tg = check.index['groups'][args.pin_texture_group]
        textures['group_index'] = dict(count=tg['count'], memsize=tg['memsize'], kind_counts=tg['kind_counts'])

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'BAM.BIG').write_bytes(archive)
    pts = [patch_point(c, u, v) for _, c in [(None, [struct.unpack_from('>4f', p, 64 + 16 * j)[:3] for j in range(16)]) for _, p in added] for u, v in ((0, 0), (1, 1))]
    experiment = dict(mode='gamecube-roundtrip' if args.roundtrip else 'gamecube-replace-terrain', limit=args.limit, location=args.location, group=group,
                      track=added[0][0]['track'], old_patch_count=sum(1 for e, _ in before if e['kind'] == 1),
                      patch_count=len(added), template_rid=args.template_rid,
                      source_anchor=args.source_anchor, target_anchor=args.target_anchor,
                      yaw_degrees=args.yaw, scale=args.scale, matrix=matrix, translation=translation,
                      bounds=[[min(p[k] for p in pts) for k in range(3)], [max(p[k] for p in pts) for k in range(3)]],
                      removed_resource_counts=removed, cleanup={k: len(v) for k, v in cleanup.items()}, cleanup_detail=cleanup, source_archive_sha256=sha256(original),
                      donor_nbd_sha256=sha256(args.nbd.read_bytes()), output_sha256=sha256(archive),
                      group_index=dict(count=g['count'], memsize=g['memsize'], kind_counts=g['kind_counts']),
                      textures=textures, donor_textures_sha256=sha256(args.textures.read_bytes()) if args.textures else None,
                      donor_lightmaps_sha256=sha256(args.lightmaps.read_bytes()) if args.lightmaps else None,
                      layout=[l for l in layout if l['replaced']])
    (args.output / 'experiment.json').write_text(json.dumps(experiment, indent=2) + '\n')
    print(json.dumps({k: v for k, v in experiment.items() if k not in ('matrix', 'translation', 'layout', 'cleanup_detail', 'textures')}, indent=2))
    if textures:
        print(json.dumps({k: v for k, v in textures.items() if k not in ('textures', 'lightmaps')}, indent=2))


if __name__ == '__main__':
    main()
