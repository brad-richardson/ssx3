#!/usr/bin/env python3
"""N8D3 bounded build, device, image, and cleanup acceptance."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

repo = Path('/Users/brad/dev/ssx3/local/research/N8D3')
work = Path('/Users/brad/dev/ssx3-work/N8D3')
gate = json.loads((repo / 'apk-gate-output.json').read_text())
result = json.loads((repo / 'result.json').read_text())
source = json.loads((repo / 'source-hashes.json').read_text())
events = result['events']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

assert gate['status'] == 'pass'
assert len(gate['apk']) == 2 and len(set(gate['apk'])) == 1
assert sha(work / 'app-release.apk') == gate['apk'][0]
assert set(gate['members']) == {
    'lib/arm64-v8a/libhardware.so',
    'lib/arm64-v8a/libps2EntryRunner.so',
    'lib/arm64-v8a/libvulkan_freedreno.so',
}
for member in gate['members'].values():
    assert len(member['sha']) == 2 and len(set(member['sha'])) == 1
assert gate['members']['lib/arm64-v8a/libvulkan_freedreno.so']['sha'][0] == \
       '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d'
assert len(gate['caches']) == 1
assert len(gate['caches'][0]['flags']) == 5
assert all(v == 'OFF' for v in gate['caches'][0]['flags'].values())
assert re.fullmatch(r'[0-9a-f]{40}', gate['runner_build_id'])
assert source['n8d3'][0] == source['n8d3'][1]
assert (repo / 'source-compare.txt').read_text().splitlines() == [
    'Files /home/brad/n8d1/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp and '
    '/home/brad/n8d3/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp differ']
assert 'BUILD SUCCESSFUL' in (repo / 'build-tail.txt').read_text()
assert (repo / 'wsl-disk.txt').read_text().strip().startswith('6.7G')
assert len([e for e in events if e.startswith('INSTALL ')]) == 1
assert len([e for e in events if e.startswith('LAUNCH ')]) == 1
assert 'Success' in next(e for e in events if e.startswith('INSTALL '))
assert result['result'] == 'race stages captured'
for name, pin in (('installed_apk', gate['apk'][0]),
                  ('elf', '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'),
                  ('iso', '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5')):
    assert result['hashes'][name] == [pin, pin]
assert any("CARD mc0 entries=''" == e for e in events)
assert any("keyguard=false battery=100% status=5" in e for e in events if e.startswith('PREFLIGHT '))
assert 'POSTRUN pid-after=none' in events
assert 'CLEANUP pid-after=none' in events
assert 'CLEANUP lease=LEASE_FREE N8D3 done' in events
elapsed = float(re.search(r'launch-to-exit=([\d.]+)s', events[-1]).group(1))
assert result['route_elapsed_seconds'] <= 180 and elapsed <= 240
assert result['trigger_dump']['host_tick'] == 2050
assert result['latest_logged_guest_tick'] <= 2100
env = (repo / 'ps2x.env').read_text()
assert 'PS2X_GS_BACKEND=parallel\nPS2X_GS_TURNIP=1\nPS2X_SKIP_MOVIE=1\n' in env
assert 'PS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999\n' in env
assert 'PS2X_N8D3_RAW_CAPTURE=1\n' in env
assert 'PS2X_PAD_SCRIPT_CLOCK=vsync\n' in env
assert len(result['screencaps']) == 0

stage = {x['name']: x for x in result['stage_files']}
assert set(stage) == {'n8d3-raw.bin', 'n8d3-packed.bin', 'n8d3-stage.txt'}
for name, item in stage.items():
    assert len(item['sha']) == 4 and len(set(item['sha'])) == 1
    path = work / name
    assert path.stat().st_size == item['bytes']
    assert sha(path) == item['sha'][0]
metadata = dict(re.findall(r'(\w+)=([^\s]+)', (repo / 'n8d3-stage.txt').read_text()))
assert metadata == dict(re.findall(r'(\w+)=([^\s]+)', (work / 'n8d3-stage.txt').read_text()))
assert {k: metadata[k] for k in ('tick', 'width', 'height', 'format', 'raw_bytes',
                                  'packed_width', 'packed_height', 'packed_stride',
                                  'displayFbp', 'sourceFbp', 'raw_write', 'packed_write')} == {
    'tick': '2050', 'width': '512', 'height': '448', 'format': '37',
    'raw_bytes': '917504', 'packed_width': '512', 'packed_height': '448',
    'packed_stride': '640', 'displayFbp': '112', 'sourceFbp': '112',
    'raw_write': '1', 'packed_write': '1'}
w, h = int(metadata['width']), int(metadata['height'])
raw = (work / 'n8d3-raw.bin').read_bytes()
packed = (work / 'n8d3-packed.bin').read_bytes()
assert len(raw) == len(packed) == w * h * 4
same_rows = sum(raw[y*w*4:(y+1)*w*4] == packed[y*w*4:(y+1)*w*4] for y in range(h))
assert same_rows == h

def decode(path):
    dims = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                    '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                                    str(path)], text=True).strip()
    assert dims == f'{w},{h}', (path, dims)
    pixels = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
                                      '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'])
    assert len(pixels) == w * h * 4
    return pixels

assert decode(repo / 'raw-rgba.png') == raw
assert decode(repo / 'backend-rgba.png') == packed
frontend = decode(repo / 'frontend.png')
assert frontend == raw
assert len({raw[i:i+4] for i in range(0, len(raw), 4)}) > 1
assert len(result['images']) == 2
for item in result['images']:
    assert item['metadata'].split()[1:4] == ['tick=2050', 'size=512x448', 'displayFbp=112']
    assert 'sourceFbp=112' in item['metadata']
    for name in (item['png'], item['txt']):
        values = item[name + '_sha']
        assert len(values) == 4 and len(set(values)) == 1
        assert sha(work / name) == values[0]
assert sha(repo / 'frontend.png') == result['images'][0]['upload-0.png_sha'][0]
assert (repo / 'upload-0.txt').read_text().strip() == result['images'][0]['metadata']
assert re.search(r'\[n8d3\] tick=2050 raw=1 packed=1 format=37 size=512x448 fbp=112',
                 (repo / 'logcat-pid.txt').read_text())

images_and_rows = sum(p.stat().st_size for p in repo.glob('*.png')) + sum(
    (work / n).stat().st_size for n in ('n8d3-raw.bin', 'n8d3-packed.bin', 'frontend.rgba'))
logs = sum(p.stat().st_size for p in repo.glob('*.log')) + (repo / 'logcat-pid.txt').stat().st_size
assert images_and_rows <= 12 * 1024 * 1024
assert logs <= 16 * 1024 * 1024
assert sum(p.stat().st_size for p in work.iterdir() if p.is_file()) < 1024 * 1024 * 1024
print(f'N8D3 acceptance PASS: one build/install/launch, tick 2050, FBP 112, RGBA8, '
      f'{same_rows}/{h} raw/backend rows equal, frontend {len(frontend)}/{len(raw)} bytes equal, '
      f'SHA pairs, cleanup, {elapsed:.1f}s, rows/images {images_and_rows} B, logs {logs} B')
