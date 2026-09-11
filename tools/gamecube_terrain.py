#!/usr/bin/env python3
"""Replace a GameCube SSX 3 location's terrain with a GameCube Tricky course.

GameCube counterpart of replace_terrain.py's terrain path. Terrain resources
are 430 bytes: header 0-31, corner UVs 32-63, 16 power-basis coefficient
vectors at 64 (big-endian floats, w = 1), bounding sphere at 320, four corner
positions at 336, bounds min/max at 384, ordinal (track << 24 | rid) at 408,
page reference at 412, packed index at 416, links at 420/424, two zero bytes.
Decoded by diffing the same Snow Jam patch on both discs (2026-09-11).
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from gamecube_world import World, assemble, sha256
from import_terrain import transform_coefficients, surface_samples, UV_CORNERS
from probe_worlds import patch_point
from replace_terrain import placement

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
    before = list(records)
    new_records, added = replace_patches(records, args.template_rid, patches, matrix, translation)
    removed = {}
    if args.drop_kind:
        kept = []
        for e, p in new_records:
            if e['kind'] in args.drop_kind:
                removed[e['kind']] = removed.get(e['kind'], 0) + 1
            else:
                kept.append((e, p))
        new_records = kept
    archive, layout = assemble(world, {group: new_records}, jobs=args.jobs)

    # Readback verification.
    check = World(archive, 'big')
    got = check.records(group)
    if [e['rid'] for e, _ in got if e['kind'] == 1] != [e['rid'] for e, _ in added]:
        raise RuntimeError('Readback terrain rids differ')
    if [p for e, p in got if e['kind'] == 1] != [p for e, p in added]:
        raise RuntimeError('Readback terrain payloads differ')
    for g in world.index['groups']:
        if g['index'] != group and check.group_bytes(g['index']) != world.group_bytes(g['index']):
            raise RuntimeError(f'Group {g["index"]} changed unexpectedly')
    g = check.index['groups'][group]
    if g['count'] != len(new_records):
        raise RuntimeError('Group index count mismatch after rebuild')

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'BAM.BIG').write_bytes(archive)
    pts = [patch_point(c, u, v) for _, c in [(None, [struct.unpack_from('>4f', p, 64 + 16 * j)[:3] for j in range(16)]) for _, p in added] for u, v in ((0, 0), (1, 1))]
    experiment = dict(mode='gamecube-replace-terrain', location=args.location, group=group,
                      track=added[0][0]['track'], old_patch_count=sum(1 for e, _ in before if e['kind'] == 1),
                      patch_count=len(added), template_rid=args.template_rid,
                      source_anchor=args.source_anchor, target_anchor=args.target_anchor,
                      yaw_degrees=args.yaw, scale=args.scale, matrix=matrix, translation=translation,
                      bounds=[[min(p[k] for p in pts) for k in range(3)], [max(p[k] for p in pts) for k in range(3)]],
                      removed_resource_counts=removed, source_archive_sha256=sha256(original),
                      donor_nbd_sha256=sha256(args.nbd.read_bytes()), output_sha256=sha256(archive),
                      group_index=dict(count=g['count'], memsize=g['memsize'], kind_counts=g['kind_counts']),
                      layout=[l for l in layout if l['replaced']])
    (args.output / 'experiment.json').write_text(json.dumps(experiment, indent=2) + '\n')
    print(json.dumps({k: v for k, v in experiment.items() if k not in ('matrix', 'translation', 'layout')}, indent=2))


if __name__ == '__main__':
    main()
