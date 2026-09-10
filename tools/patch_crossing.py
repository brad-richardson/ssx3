"""Compare logged rider positions with a patch's original and edited surfaces.

Usage: patch_crossing.py LOG.jsonl BUILD_DIR   (BUILD_DIR holds experiment.json from build_world_experiment)
For each logged sample within the patch's XY footprint, prints the rider Z against the
original and bumped surface Z at the nearest (u,v). Positive 'above_orig' near the centre
that tracks 'bump' indicates the rider followed the edited geometry.
"""
import sys, json, struct, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from inspect_disc import Region, big_members, file_region
from probe_worlds import refpack, resource_records, patch_point
from build_world_experiment import coefficients
log, build = sys.argv[1], Path(sys.argv[2])
exp = json.loads((build / 'experiment.json').read_text())
report = json.load(open(ROOT / 'local' / 'reports' / 'ssx3-world.json'))
src = Path('/Volumes/share-1/brad/games/ssx3-workbench/source/ssx3/BAM.BIG')
with src.open('rb') as f:
    a = Region(f, 0, src.stat().st_size); _, ms = big_members(a); ssb = file_region(a, ms, 'data/worlds/bam.ssb')
    raw = b''.join(refpack(ssb.read(b['offset'], b['size'])[8:])[0] for b in report['groups'][exp['group']]['blocks'])
orig = next(p for e, p in resource_records(raw) if e['kind'] == 1 and e['track'] == exp['track'] and e['rid'] == exp['rid'])
edited = bytearray(orig)
for c in exp['geometry']['float_changes']:
    struct.pack_into('<f', edited, c['offset'], c['after'])
co, ce = coefficients(orig), coefficients(bytes(edited))
N = 64
grid = [((i / N, j / N), patch_point(co, i / N, j / N)) for i in range(N + 1) for j in range(N + 1)]
rows = [json.loads(l) for l in open(log)]
print(f"{'t':>6} {'x':>9} {'y':>8} {'rider_z':>10} {'orig_z':>10} {'bump_z':>10} {'above_orig':>10} {'bump':>6} {'u':>5} {'v':>5}")
for r in rows:
    x, y, z = r['x'], r['y'], r['z']
    (u, v), pt = min(grid, key=lambda g: (g[1][0] - x) ** 2 + (g[1][1] - y) ** 2)
    if math.hypot(pt[0] - x, pt[1] - y) > 60 or u in (0, 1) or v in (0, 1):
        continue
    zo = patch_point(co, u, v)[2]; ze = patch_point(ce, u, v)[2]
    print(f"{r['t']:6.2f} {x:9.0f} {y:8.0f} {z:10.1f} {zo:10.1f} {ze:10.1f} {z - zo:10.1f} {ze - zo:6.1f} {u:5.2f} {v:5.2f}")
