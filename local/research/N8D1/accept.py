#!/usr/bin/env python3
"""Check N8D1 declared receipts, SHA pairs, and full PNG decodes."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

repo = Path('/Users/brad/dev/ssx3/local/research/N8D1')
work = Path('/Users/brad/dev/ssx3-work/N8D1')
required = ['REPORT.md', 'input-hashes.json', 'source-hashes.json', 'source.diff',
            'apk-gate.json', 'build-tail.txt', 'driver.log', 'logcat-pid.txt',
            'result.json', 'ps2x.env']
for name in required:
    assert (repo / name).is_file(), f'missing {name}'

inputs = json.loads((repo / 'input-hashes.json').read_text())
assert all(len(pair) == 2 and pair[0] == pair[1] for pair in inputs.values())
source = json.loads((repo / 'source-hashes.json').read_text())
assert len(source['after']) == 2 and source['after'][0] == source['after'][1]
gate = json.loads((repo / 'apk-gate.json').read_text())
assert gate['status'] == 'pass' and gate['apk'][0] == gate['apk'][1]
assert all(m['sha'][0] == m['sha'][1] for m in gate['members'].values())
result = json.loads((repo / 'result.json').read_text())
assert result['result'] == 'menu target reached', result['result']
assert all(pair[0] == pair[1] for pair in result['hashes'].values())
assert len(result['images']) in (1, 2, 3), 'host frames absent'
assert 'CLEANUP pid-after=none' in result['events']
assert 'CLEANUP lease=LEASE_FREE N8D1 done' in result['events']
pid = result['pid']
log = (repo / 'logcat-pid.txt').read_text()
assert re.search(rf'^\s*\d+\.\d+\s+{pid}\s+', log, re.M), 'same PID log absent'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

pngs = []
for image in result['images']:
    for name in (image['png'], image['txt']):
        path = repo / name
        assert path.is_file(), f'missing {name}'
        assert len(set(image[name + '_sha'])) == 1
        assert digest(path) == image[name + '_sha'][0]
    assert re.search(r'\btick=\d+', image['metadata'])
    assert re.search(r'\bsize=\d+x\d+', image['metadata'])
    pngs.append(repo / image['png'])

screen = next((x for x in result['screencaps'] if x['name'].startswith('menu-')), None)
assert screen, 'menu screencap absent'
path = repo / screen['name']
assert path.is_file()
assert digest(path) == screen['sha_remote'] == screen['sha_local']
pngs.append(path)

for path in pngs:
    dims = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                    '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                                    str(path)], text=True).strip()
    w, h = map(int, dims.split(','))
    assert 0 < w <= 4096 and 0 < h <= 4096, f'{path.name}: dimensions {dims}'
    decoded = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
                                       '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    assert len(decoded) == w * h * 3, f'{path.name}: partial decode'
    assert len(set(decoded)) > 1, f'{path.name}: uniform content'
    print(f'PNG {path.name}: {w}x{h} decoded, {len(set(decoded))} byte values')
print(f'N8D1 acceptance PASS: {len(pngs)} PNGs, SHA pairs, same PID, cleanup')
