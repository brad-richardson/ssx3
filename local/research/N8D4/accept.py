#!/usr/bin/env python3
"""N8D4 independent preparation, capture, and final acceptance gates."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from zipfile import ZipFile

REPO = Path('/Users/brad/dev/ssx3')
REPORT = REPO / 'local/research/N8D4'
ROOT = Path('/Users/brad/dev/ssx3-work/N8D4')
APK = Path('/Users/brad/dev/ssx3-work/N8D3/app-release.apk')
APK_PIN = '3970011d360b86a3f93f170df11e5964e2b467f01e7351c2cd1610b615b885be'
ELF_PIN = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
ISO_PIN = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
CAP = 4 * 1024**3


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(chunk)
    return h.hexdigest()


def prepared():
    for name in ('launch.py', 'replay.py', 'accept.py'):
        ast.parse((REPORT / name).read_text(), filename=name)
    reads = [sha(APK) for _ in range(2)]
    need(reads == [APK_PIN] * 2, 'N8D3 APK SHA pair')
    with ZipFile(APK) as z:
        names = set(z.namelist())
        members = {'lib/arm64-v8a/libps2EntryRunner.so',
                   'lib/arm64-v8a/libvulkan_freedreno.so', 'lib/arm64-v8a/libhardware.so'}
        need(members <= names, 'required APK members')
        runner = z.read('lib/arm64-v8a/libps2EntryRunner.so')
        need(all(s in runner for s in (b'PS2X_GS_CAPTURE_STOP_TICK', b'PS2XGSC1',
                                      b'PS2X_N8D3_RAW_CAPTURE')), 'capture code in packaged runner')
        for name, pin in (('lib/arm64-v8a/libps2EntryRunner.so',
                           '3628e772505d3329575ffece647a5840e09580b254137872e624ae7f7dbe6277'),
                          ('lib/arm64-v8a/libvulkan_freedreno.so',
                           '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d'),
                          ('lib/arm64-v8a/libhardware.so',
                           '1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387')):
            need(hashlib.sha256(z.read(name)).hexdigest() == pin, f'APK member {name}')
    print('N8D4 preparation PASS: script syntax, APK SHA pair, packaged capture strings')


def parse_capture(path):
    need(path.stat().st_size <= CAP and path.stat().st_size > 8, 'capture size cap/empty')
    count = Counter()
    last = None
    with path.open('rb') as f:
        need(f.read(8) == b'PS2XGSC1', 'capture magic')
        while True:
            pos = f.tell()
            prefix = f.read(4)
            if not prefix:
                break
            need(len(prefix) == 4, f'partial length at {pos}')
            (length,) = struct.unpack('<I', prefix)
            need(9 <= length <= 64 * 1024**2, f'bad record length at {pos}')
            rec = f.read(length)
            need(len(rec) == length, f'partial record at {pos}')
            kind = rec[0]
            tick = struct.unpack_from('<Q', rec, 1)[0]
            need(1 <= kind <= 7, f'unknown kind {kind} at {pos}')
            if kind == 1:
                need(length >= 14 and struct.unpack_from('<I', rec, 10)[0] == length - 14,
                     f'packet length at {pos}')
            elif kind == 4:
                need(length == 9, f'marker length at {pos}')
            count[kind] += 1
            last = (kind, tick)
    need(last == (4, 2050), f'last event is {last}, expected marker 2050')
    need(count[1] > 0 and count[4] == 2050, 'packet or marker count')
    return {'bytes': path.stat().st_size, 'sha': sha(path),
            'counts': {str(k): count[k] for k in range(1, 8)}, 'last': last}


def capture_gate():
    device = json.loads((ROOT / 'result.json').read_text())
    events = device['events']
    need(device['result'] == 'capture and race stages captured', 'device result')
    need(sum(e.startswith('INSTALL ') for e in events) == 1, 'exactly one install')
    need(sum(e.startswith('LAUNCH ') for e in events) == 1, 'exactly one launch')
    need('POSTRUN pid-after=none' in events and 'CLEANUP pid-after=none' in events,
         'app force-stop/PID cleanup')
    need('CLEANUP lease=LEASE_FREE N8D4 done' in events, 'Odin lease cleanup')
    need(device['stop_marker']['tick'] == 2050 and
         device['trigger_dump']['host_tick'] == 2050, 'same target marker/frame')
    need(device['route_elapsed_seconds'] <= 300, 'device wall cap')
    need(all(int(re.search(r'device_free=(\d+)', e).group(1)) >= 10 * 1024**3 and
             int(re.search(r'capture_bytes=(\d+)', e).group(1)) <= CAP
             for e in events if e.startswith('BUDGET ')), 'device space/capture budget')
    for name, pin in (('local_apk', APK_PIN), ('installed_apk', APK_PIN),
                      ('elf', ELF_PIN), ('iso', ISO_PIN)):
        need(device['hashes'][name] == [pin] * 2, f'{name} SHA pair')
    env = (ROOT / 'ps2x.env').read_text()
    for line in ('PS2X_GS_BACKEND=parallel', 'PS2X_GS_TURNIP=1',
                 'PS2X_SKIP_MOVIE=1', 'PS2X_PAD_SCRIPT_CLOCK=vsync',
                 'PS2X_N8D3_RAW_CAPTURE=1', 'PS2X_GS_CAPTURE_STOP_TICK=2050',
                 'PS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999'):
        need(line + '\n' in env, f'env {line}')
    need('PS2X_GS_CAPTURE=/storage/emulated/0/Android/data/com.ps2x.runner/files/n8d4.gs\n' in env,
         'capture target')
    need("CARD mc0 entries=''" in events, 'empty card')
    need(any('keyguard=false' in e and re.search(r'battery=(\d+)% status=(2|5)', e) and
             int(re.search(r'battery=(\d+)%', e).group(1)) >= 20
             for e in events if e.startswith('PREFLIGHT ')), 'prelaunch keyguard/battery')
    item = device['capture']
    need(len(set(item['sha_device'] + item['sha_local'])) == 1 and
         len(item['sha_device']) == len(item['sha_local']) == 2, 'capture SHA pairs')
    capture = parse_capture(ROOT / 'n8d4.gs')
    need(capture['sha'] == item['sha_local'][0] and capture['bytes'] == item['bytes'] ==
         device['stop_marker']['bytes'], 'capture local/device/marker bytes')
    need(len(device['stage_files']) == 3 and len(device['images']) == 2,
         'N8D3 raw/packed/frontend stage outputs')
    for part in device['stage_files']:
        need(len(set(part['sha'])) == 1 and len(part['sha']) == 4 and
             sha(ROOT / part['name']) == part['sha'][0], f"stage SHA {part['name']}")
    raw = ROOT / 'n8d3-raw.bin'
    packed = ROOT / 'n8d3-packed.bin'
    need(raw.stat().st_size == packed.stat().st_size == 512 * 448 * 4,
         'raw/packed RGBA size')
    need(sha(raw) == sha(packed), 'raw and backend packed bytes')
    for image in device['images']:
        need('tick=2050' in image['metadata'] and 'displayFbp=112' in image['metadata'],
             'frontend tick/FBP metadata')
        for filename in (image['png'], image['txt']):
            reads = image[filename + '_sha']
            need(len(reads) == 4 and len(set(reads)) == 1 and sha(ROOT / filename) == reads[0],
                 f'frontend image/metadata SHA {filename}')
        dims = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                        '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                                        str(ROOT / image['png'])], text=True).strip()
        need(dims == '512,448', 'frontend PNG decode/dimensions')
    frontend = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(ROOT / device['images'][0]['png']),
                                        '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'])
    need(len(frontend) == 512 * 448 * 4 and hashlib.sha256(frontend).hexdigest() == sha(raw),
         'frontend decoded RGBA matches raw capture')
    need((ROOT / 'logcat-all.txt').stat().st_size <= 16 * 1024**2, 'device log cap')
    print('N8D4 capture PASS:', json.dumps(capture, sort_keys=True))
    return capture


def ppm(path):
    with path.open('rb') as f:
        need(f.readline() == b'P6\n' and f.readline() == b'512 448\n' and
             f.readline() == b'255\n', f'PPM header {path}')
        need(len(f.read()) == 512 * 448 * 3, f'PPM pixels {path}')


def final_gate(capture):
    replay = json.loads((ROOT / 'replay-result.json').read_text())
    need(replay['status'] == 'both replays complete', 'both replays')
    need(len(set(replay['capture_sha'])) == 1 and
         replay['capture_sha'][0] == capture['sha'], 'same capture both replays')
    need(len(set(replay['codegen_register_sha'])) == 1 and
         len(set(replay['binary_sha'])) == 1, 'codegen/binary SHA pairs')
    need(re.fullmatch(r'[0-9a-f]{40}', replay['fork_pin']) is not None, 'fork commit pin')
    need(set(replay['commands']) == {'configure', 'build', 'cpu', 'parallel'},
         'one configure/build and two replays')
    need(replay['scratch_bytes'] <= 12 * 1024**3, 'scratch cap')
    frame = {}
    sample_counts = {}
    for backend in ('cpu', 'parallel'):
        log = (ROOT / f'{backend}.log').read_text(errors='replace')
        need('GB4_REPLAY_PARSE_ERROR' not in log and re.search(r'Failed:\s*0', log),
             f'{backend} suite/parse')
        summary = re.search(r'GB4_REPLAY_SUMMARY[^\n]+', log)
        need(summary is not None and f'backend={backend}' in summary.group() and
             f"packets={capture['counts']['1']}" in summary.group() and
             f"priv={capture['counts']['2']}" in summary.group() and
             f"transfers={capture['counts']['3']}" in summary.group() and
             f"markers={capture['counts']['4']}" in summary.group() and
             f"readbacks={capture['counts']['6']}" in summary.group() and
             f"clears={capture['counts']['7']}" in summary.group(),
             f'{backend} replay counts')
        sample_counts[backend] = int(re.search(r'\bsamples=(\d+)', summary.group()).group(1))
        need(sample_counts[backend] > 0, f'{backend} samples')
        if backend == 'parallel':
            stats = re.search(r'GB4_PARALLEL_STATS[^\n]+', log)
            need(stats is not None and
                 f"packets={capture['counts']['1']}" in stats.group() and
                 'null_scanouts=0' in stats.group() and 'init_ok=1' in stats.group() and
                 'init_failed=0' in stats.group(), 'parallel backend stats')
        frames = re.findall(r'GB4_FRAME tick=2050[^\n]+', log)
        need(len(frames) == 1, f'{backend} named frame')
        frame[backend] = frames[0]
        need('display_fbp=112 source_fbp=112' in frames[0], f'{backend} FBP 112')
        path = ROOT / f'{backend}-ppm/vq-002050.ppm'
        ppm(path)
        need(len(list((ROOT / f'{backend}-ppm').glob('*.ppm'))) == 1,
             f'{backend} single image')
        need((ROOT / f'{backend}.hashes').is_file(), f'{backend} hash output')
        rows = (ROOT / f'{backend}.hashes').read_text().splitlines()
        need(len(rows) == sample_counts[backend] and any('tick=2050' in x for x in rows),
             f'{backend} output rows/tick')
        need((ROOT / f'{backend}.log').stat().st_size <= 16 * 1024**2,
             f'{backend} log cap')
    def field(line, name):
        return re.search(rf'\b{name}=([^\s]+)', line).group(1)
    need(field(frame['cpu'], 'pmode') == field(frame['parallel'], 'pmode') and
         field(frame['cpu'], 'dispfb1') == field(frame['parallel'], 'dispfb1'),
         'CPU/parallel PMODE/DISPFB alignment')
    need(sum(p.stat().st_size for p in ROOT.glob('*.log')) +
         (ROOT / 'logcat-all.txt').stat().st_size <= 16 * 1024**2,
         'combined text log cap')
    need(sum(p.stat().st_size for p in ROOT.rglob('*.ppm')) +
         sum(p.stat().st_size for p in ROOT.glob('*.png')) <= 12 * 1024**2,
         'image byte cap')
    print('N8D4 final acceptance PASS:', json.dumps(frame, sort_keys=True))


if __name__ == '__main__':
    mode = sys.argv[1:] or ['--final']
    need(mode in (['--prepared'], ['--capture'], ['--final']), 'mode')
    if mode == ['--prepared']:
        prepared()
    else:
        result = capture_gate()
        if mode == ['--final']:
            final_gate(result)
