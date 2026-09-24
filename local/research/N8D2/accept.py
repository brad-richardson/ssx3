#!/usr/bin/env python3
"""Check N8D2 pins, the single Odin run, SHA pairs, PNGs, and cleanup."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

repo = Path('/Users/brad/dev/ssx3/local/research/N8D2')
root = Path('/Users/brad/dev/ssx3')
pins = json.loads((repo / 'pins.json').read_text())
gate = json.loads((root / pins['source_receipt']).read_text())
result = json.loads((repo / 'result.json').read_text())
events = result['events']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def same_pair(values, expected=None):
    assert len(values) == 2 and values[0] == values[1], values
    if expected:
        assert values[0] == expected, (values, expected)

same_pair(pins['apk_sha_reads'], gate['apk'][0])
assert gate['status'] == 'pass'
assert gate['members'] == pins['package_members']
assert gate['runner_build_id'] == pins['runner_build_id']
assert gate['caches'][0]['flags'] == pins['flags']
assert all(v == 'OFF' for v in pins['flags'].values())
assert digest(Path(pins['apk_path'])) == pins['apk_sha_reads'][0]
assert len([e for e in events if e.startswith('INSTALL ')]) == 1
assert len([e for e in events if e.startswith('LAUNCH ')]) == 1
assert 'Success' in next(e for e in events if e.startswith('INSTALL '))
assert result['result'] == 'race dump and screen captured', result['result']
for label, expected in [('installed_apk', pins['apk_sha_reads'][0]),
                        ('elf', pins['elf']), ('iso', pins['iso'])]:
    same_pair(result['hashes'][label], expected)
assert "CARD mc0 entries=''" in events
assert any(e.startswith('FRAME_DIR empty=') for e in events)
assert any(e.startswith('PREFLIGHT device=device lease=') for e in events)
assert any(e.startswith('PREFLIGHT device=device lease=\'N8D2 one-launch\' keyguard=false') for e in events)
assert 'LEASE claimed=N8D2 one-launch' in events
assert 'POSTRUN pid-after=none' in events
assert 'CLEANUP pid-after=none' in events
assert 'CLEANUP lease=LEASE_FREE N8D2 done' in events
exit_event = next(e for e in events if e.startswith('CLEANUP launch-to-exit='))
total_elapsed = float(re.search(r'launch-to-exit=([0-9.]+)s', exit_event).group(1))
assert result['route_elapsed_seconds'] <= 180, result['route_elapsed_seconds']
assert total_elapsed <= 240, total_elapsed
assert 1 <= len(result['images']) <= 3
assert len(result['screencaps']) == 1
assert result['trigger_dump']['host_tick'] >= 2050

log = (repo / 'logcat-pid.txt').read_text()
pid = result['pid']
assert re.search(rf'^\s*\d+\.\d+\s+{pid}\s+', log, re.M)
dump_ticks = [int(x) for x in re.findall(r'\[frame:dump\] seq=\d+ tick=(\d+)', log)]
assert any(2050 <= t <= 2100 for t in dump_ticks), dump_ticks

def check_png(path):
    dims = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                    '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                                    str(path)], text=True).strip()
    w, h = map(int, dims.split(','))
    assert 0 < w <= 4096 and 0 < h <= 4096, (path, dims)
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
                                   '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    assert len(raw) == w * h * 3 and len(set(raw)) > 1, path
    print(f'PNG {path.name}: {w}x{h} decoded')

ticks = []
for entry in result['images']:
    assert entry['kind'] in ('upload', 'fallback')
    for name in (entry['png'], entry['txt']):
        path = repo / name
        assert path.is_file(), path
        values = entry[name + '_sha']
        assert len(values) == 4 and len(set(values)) == 1, (name, values)
        assert digest(path) == values[0], name
    metadata = (repo / entry['txt']).read_text().strip()
    assert metadata == entry['metadata']
    match = re.search(r'\bseq=(\d+) tick=(\d+) size=(\d+)x(\d+)', metadata)
    assert match, metadata
    ticks.append(int(match.group(2)))
    check_png(repo / entry['png'])
assert any(t >= 2050 for t in ticks), ticks

screen = result['screencaps'][0]
assert screen['name'] == 'race.png'
same_pair(screen['sha_remote'])
same_pair(screen['sha_local'], screen['sha_remote'][0])
assert digest(repo / screen['name']) == screen['sha_remote'][0]
assert screen['trigger_host_tick'] >= 2050
assert screen['request_elapsed_seconds'] <= screen['end_elapsed_seconds'] <= 240
check_png(repo / screen['name'])

env = (repo / 'ps2x.env').read_text()
baseline = (root / 'local/research/N8D1/ps2x.env').read_text()
expected_env = baseline.replace('n8d1-frames', 'n8d2-frames').replace(
    'PS2X_FRAME_DUMP_ONCE_TICKS=780,810,840',
    'PS2X_FRAME_DUMP_ONCE_TICKS=1840,1950,2050')
assert env == expected_env
image_bytes = sum(p.stat().st_size for p in repo.glob('*.png'))
log_bytes = sum(p.stat().st_size for p in repo.glob('*.log')) + (repo / 'logcat-pid.txt').stat().st_size
assert image_bytes <= 12 * 1024 * 1024
assert log_bytes <= 16 * 1024 * 1024
print(f'N8D2 acceptance PASS: one install/launch, {len(result["images"])} host pairs, one screen, SHA pairs, cleanup, {total_elapsed:.1f}s')
