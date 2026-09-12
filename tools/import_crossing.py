#!/usr/bin/env python3
"""Compare a ride log with an imported terrain section and the original hub surface.

Usage: import_crossing.py LOG.jsonl BUILD_DIR
BUILD_DIR holds surface-samples.json from import_terrain.py. For each logged sample,
prints the rider Z against the nearest imported-surface sample and the nearest
original hub patch sample (group 2), so it is clear which surface the rider is on.
"""
import json, math, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from inspect_disc import Region, big_members, file_region
from probe_worlds import refpack, resource_records, patch_point

log, build = Path(sys.argv[1]), Path(sys.argv[2])
samples = json.loads((build / 'surface-samples.json').read_text())
exp = json.loads((build / 'experiment.json').read_text())
report = json.load(open(ROOT / 'local/reports/ssx3-world.json'))
src = Path('/Volumes/share/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')
with src.open('rb') as f:
    a = Region(f, 0, src.stat().st_size); _, ms = big_members(a); ssb = file_region(a, ms, 'data/worlds/bam.ssb')
    raw = b''.join(refpack(ssb.read(b['offset'], b['size'])[8:])[0] for b in report['groups'][exp['group']]['blocks'])
hub = []
for e, p in resource_records(raw):
    if e['kind'] == 1:
        c = [struct.unpack_from('<4f', p, 64 + 16 * j)[:3] for j in range(16)]
        hub.extend(patch_point(c, i / 8, j / 8) for i in range(9) for j in range(9))


def nearest(pts, x, y, box=600):
    near = [p for p in pts if abs(p[0] - x) < box and abs(p[1] - y) < box]
    if not near:
        return None
    p = min(near, key=lambda q: (q[0] - x) ** 2 + (q[1] - y) ** 2)
    return p if math.hypot(p[0] - x, p[1] - y) < 350 else None


print(f"{'t':>6} {'x':>8} {'y':>7} {'rider_z':>9} {'import_z':>9} {'hub_z':>9} {'vs_import':>9} {'vs_hub':>7}  on")
on_import = 0
for line in log.open():
    r = json.loads(line)
    x, y, z = r['x'], r['y'], r['z']
    if not (-90000 < x < -70000):
        continue
    si, sh = nearest(samples, x, y), nearest(hub, x, y)
    vi = z - si[2] if si else None; vh = z - sh[2] if sh else None
    on = 'import' if vi is not None and abs(vi) < 25 and (vh is None or abs(vi) < abs(vh)) else 'hub' if vh is not None and abs(vh) < 25 else 'air/other'
    on_import += on == 'import'
    print(f"{r['t']:6.2f} {x:8.0f} {y:7.0f} {z:9.0f} {si[2] if si else float('nan'):9.0f} {sh[2] if sh else float('nan'):9.0f} {vi if vi is not None else float('nan'):9.1f} {vh if vh is not None else float('nan'):7.1f}  {on}")
print('samples on imported surface:', on_import)
