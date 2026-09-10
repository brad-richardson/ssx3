#!/usr/bin/env python3
"""Map a ride log's positions to SSX 3 locations by nearest terrain patch centre.

Usage: ride_locations.py LOG.jsonl [--world-report local/reports/ssx3-world.json]
Prints the sequence of locations visited with entry times and sample counts.
Patch centres come from the staged original archive; a coarse grid keeps it fast.
"""
import argparse, json, math, struct, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from inspect_disc import Region, big_members, file_region
from probe_worlds import refpack, resource_records, patch_point

CELL = 4000


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('log', type=Path)
    ap.add_argument('--archive', type=Path, default=Path('/Volumes/share-1/brad/games/ssx3-workbench/source/ssx3/BAM.BIG'))
    ap.add_argument('--world-report', type=Path, default=ROOT / 'local/reports/ssx3-world.json')
    ap.add_argument('--max-distance', type=float, default=2500)
    a = ap.parse_args()
    report = json.loads(a.world_report.read_text())
    grid = defaultdict(list)
    with a.archive.open('rb') as f:
        region = Region(f, 0, a.archive.stat().st_size); _, members = big_members(region)
        ssb = file_region(region, members, 'data/worlds/bam.ssb')
        for g in report['groups']:
            if not g['kinds'].get('1'):
                continue
            raw = b''.join(refpack(ssb.read(b['offset'], b['size'])[8:])[0] for b in g['blocks'])
            for e, p in resource_records(raw):
                if e['kind'] == 1:
                    c = [struct.unpack_from('<4f', p, 64 + i * 16)[:3] for i in range(16)]
                    x, y, z = patch_point(c, .5, .5)
                    grid[(int(x // CELL), int(y // CELL))].append((x, y, z, g['locations'][0]))
    def nearest(x, y, z):
        cx, cy = int(x // CELL), int(y // CELL); best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for px, py, pz, loc in grid.get((cx + dx, cy + dy), ()):
                    d = math.hypot(px - x, py - y) + 0.5 * abs(pz - z)
                    if best is None or d < best[0]: best = (d, loc)
        return best
    visits = []
    for line in a.log.open():
        r = json.loads(line)
        b = nearest(r['x'], r['y'], r['z'])
        loc = b[1] if b and b[0] < a.max_distance else None
        if loc and (not visits or visits[-1]['location'] != loc):
            visits.append(dict(location=loc, t=r['t'], samples=0, first=(round(r['x']), round(r['y']), round(r['z']))))
        if loc: visits[-1]['samples'] += 1
    for v in visits: print(json.dumps(v))
    print('locations:', [v['location'] for v in visits])


if __name__ == '__main__':
    main()
