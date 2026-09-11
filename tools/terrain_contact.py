#!/usr/bin/env python3
"""Measure rider contact with decoded SSX 3 terrain records.

Invert each candidate bicubic's XY coordinates with Newton iteration and compare
its exact surface Z to the recorded rider. Bounds prune candidates; a coarse UV
grid supplies the initial guess. Folded/vertical surfaces may be missed, so these
are contact observations, not proof that every ride sample has been classified.
Multiple --original groups can cover both a run and its entry connector.
"""
import argparse
import json
import math
import struct
import statistics
from pathlib import Path
from probe_worlds import patch_point, resource_records


def patches(path):
    out = []
    for e, p in resource_records(Path(path).read_bytes()):
        if e['kind'] != 1:
            continue
        c = [struct.unpack_from('<4f', p, 64 + 16 * j)[:3] for j in range(16)]
        lo, hi = struct.unpack_from('<3f', p, 344), struct.unpack_from('<3f', p, 356)
        grid = [(u / 4, v / 4, patch_point(c, u / 4, v / 4)) for u in range(5) for v in range(5)]
        out.append((e['rid'], c, lo, hi, grid))
    return out


def hit(surfaces, x, y, z):
    hits = []
    for rid, c, lo, hi, grid in surfaces:
        if not lo[0] - 1 <= x <= hi[0] + 1 or not lo[1] - 1 <= y <= hi[1] + 1:
            continue
        u, v, _ = min(grid, key=lambda p: (p[2][0] - x) ** 2 + (p[2][1] - y) ** 2)
        singular = False
        for _ in range(12):
            p = patch_point(c, u, v)
            pu, pv = patch_point(c, u + 1e-4, v), patch_point(c, u, v + 1e-4)
            a, b = (pu[0] - p[0]) / 1e-4, (pv[0] - p[0]) / 1e-4
            cc, d = (pu[1] - p[1]) / 1e-4, (pv[1] - p[1]) / 1e-4
            determinant = a * d - b * cc
            if abs(determinant) < 1e-10:
                singular = True
                break
            dx, dy = p[0] - x, p[1] - y
            if math.hypot(dx, dy) < .01:
                break
            du, dv = (d * dx - b * dy) / determinant, (-cc * dx + a * dy) / determinant
            u, v = max(-.1, min(1.1, u - du)), max(-.1, min(1.1, v - dv))
        if singular:
            continue
        p = patch_point(c, u, v)
        if -.0001 <= u <= 1.0001 and -.0001 <= v <= 1.0001 and math.dist(p[:2], (x, y)) < .1:
            hits.append(dict(rid=rid, z=p[2], residual=z - p[2], u=u, v=v))
    return min(hits, key=lambda h: abs(h['residual'])) if hits else None

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('ride', type=Path)
    ap.add_argument('terrain', type=Path, help='Decoded resource records, e.g. terrain.bin')
    ap.add_argument('--original', type=Path, action='append', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    new = patches(args.terrain)
    old = [p for path in args.original for p in patches(path)]
    result = []
    for line in args.ride.read_text().splitlines():
        r = json.loads(line)
        if not all(math.isfinite(r[k]) for k in ('x', 'y', 'z')):
            raise ValueError('Ride contains nonfinite coordinates')
        h = hit(new, r['x'], r['y'], r['z'])
        o = hit(old, r['x'], r['y'], r['z'])
        result.append(dict(**r, imported=h, original=o))
    contact = [r for r in result if r['imported'] and abs(r['imported']['residual']) < 5
               and (r['original'] is None or abs(r['original']['residual']) > 20)]
    summary = dict(samples=len(result), on_imported_distinct_from_original=len(contact),
                   patches=sorted({r['imported']['rid'] for r in contact}),
                   median_imported_residual=statistics.median(r['imported']['residual'] for r in contact) if contact else None,
                   first_contact=contact[0] if contact else None, last_contact=contact[-1] if contact else None,
                   contact_tolerance=5, minimum_original_separation=20,
                   original_groups=[str(p) for p in args.original])
    args.output.write_text(json.dumps(dict(summary=summary, samples=result), indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
