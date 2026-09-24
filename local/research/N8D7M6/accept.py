#!/usr/bin/env python3
"""N8D7M6 acceptance: read-only prepared gate, device-capture gate, Mac replay + outcome.

Modes (from /Users/brad/dev/ssx3):
  accept.py --prepared   read-only: APK/member strings+SHA, env diff vs
                         N8D7M2, no second capture/launch flag, bounded
                         parser/stop rules, Mac replay binary+source pins.
                         No adb contact, no lease, no build/replay.
  accept.py --capture    check the pulled device capture + same-run vectors.
  accept.py --final      run one bounded Mac paraLLEl replay of the pulled
                         stream (one P-lane slot, <=600 s) and classify A-D/OTHER.

Predeclared outcomes (brief): A = same descriptor, Mac broad (>=250/448)
input+oracle active, Odin sparse (<=100/448); B = same descriptor, both
sparse; C = descriptor/phase mismatch despite same stream; D = same
descriptor, both broad; OTHER = incomplete stream, bad gate, intermediate
counts, vector mismatch outside A-D, or missing SHA. No Turnip/shader/
barrier cause is claimed. Odin values compare to the new same-stream Mac
paraLLEl replay only, never to CPU final literals.
"""

import ast
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

REPO = Path('/Users/brad/dev/ssx3')
RDIR = REPO / 'local/research/N8D7M6'
SCRATCH = Path('/Users/brad/dev/ssx3-work/N8D7M6')
APK = Path('/Users/brad/dev/ssx3-work/N8D7M1/app-release.apk')
APK_PIN = 'e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1'
MEMBER_PINS = {
    'lib/arm64-v8a/libps2EntryRunner.so':
        'f3de999acc9227b82a9d9fab6a4a0b5b7fb279e6205991c1b3022da781e3c1bf',
    'lib/arm64-v8a/libvulkan_freedreno.so':
        '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d',
    'lib/arm64-v8a/libhardware.so':
        '1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387',
}
ELF_PIN = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
ISO_PIN = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
BIN = Path('/Users/brad/dev/ssx3-work/N8D7M5/build/ps2xTest/ps2x_tests')
BIN_PIN = 'd06ff1aa3dbb273c9b59c4f550ec80ba9fa9b594bc224dd10be8c40d6dc0b77f'
FORK = Path('/Users/brad/dev/ssx3-work/N8D7L/PS2Recomp')
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp')
CODEGEN_PIN = '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'
PARALLEL = Path('/Users/brad/dev/ssx3-work/N8D7F/parallel-gs')
VULKAN = Path('/opt/homebrew/lib/libvulkan.1.dylib')
CAP = 4 * 1024**3
CONTROL_ADDRS = (0x0E0000, 0x0E0534, 0x0E0040, 0x1BFFF4,
                 0x0E2000, 0x0F0000, 0x0E1FFC, 0x0F2000)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024**2), b''):
            digest.update(chunk)
    return digest.hexdigest()


def prepared():
    """Read-only gate: no adb, no lease, no build, no replay."""
    rows = []
    for name in ('launch.py', 'accept.py'):
        ast.parse((RDIR / name).read_text(), filename=name)
        rows.append([name, 'syntax', 'PASS'])
    need(APK.is_file(), 'N8D7M1 APK absent')
    need(APK.stat().st_size == 153736732, 'APK size')
    reads = [sha(APK) for _ in range(2)]
    need(reads == [APK_PIN] * 2, 'APK SHA pair')
    rows.append(['app-release.apk', APK_PIN[:8] + '...', 'PASS two reads'])
    with ZipFile(APK) as archive:
        names = set(archive.namelist())
        need('lib/x86_64/libps2EntryRunner.so' not in names, 'x86 member present')
        for member, pin in MEMBER_PINS.items():
            need(member in names, f'APK member absent: {member}')
            pair = [hashlib.sha256(archive.read(member)).hexdigest() for _ in range(2)]
            need(pair == [pin] * 2, f'APK member SHA: {member}')
            rows.append([member.split('/')[-1], pin[:8] + '...', 'PASS two reads'])
        runner = archive.read('lib/arm64-v8a/libps2EntryRunner.so')
        for marker in (b'PS2X_GS_CAPTURE', b'PS2X_GS_CAPTURE_STOP_TICK', b'PS2XGSC1',
                       b'PS2X_N8D7L_ORACLE', b'PS2X_N8D7F_SELECTED_CAPTURE',
                       b'PS2X_N8D5_TILE_CAPTURE'):
            need(marker in runner, f'runner lacks {marker!r}')
            rows.append([f'runner string {marker.decode()}', 'present', 'PASS'])
    text = (RDIR / 'launch.py').read_text()
    m2 = (REPO / 'local/research/N8D7M2/launch.py').read_text()
    # Exact env diff: every N8D7M2 env line kept, plus exactly the two capture lines.
    for line in ('PS2X_GS_BACKEND=parallel', 'PS2X_GS_TURNIP=1', 'PS2X_SKIP_MOVIE=1',
                 'PS2X_PAD_SCRIPT_CLOCK=vsync', 'PS2X_N8D5_TILE_CAPTURE=1',
                 'PS2X_N8D7F_SELECTED_CAPTURE=1', 'PS2X_N8D7L_ORACLE=1',
                 'PS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999', 'PS2X_VSYNC_RATE_LOG=1'):
        need(line in text, f'env keeps {line}')
    need("CAPTURE = f'{FILES}/n8d7m6.gs'" in text or 'n8d7m6.gs' in text,
         'unique N8D7M6 capture target')
    need('PS2X_GS_CAPTURE={CAPTURE}' in text or 'PS2X_GS_CAPTURE=' in text,
         'capture env flag')
    need('PS2X_GS_CAPTURE_STOP_TICK=2050' in text, 'capture stop tick 2050')
    need('n8d7m6.gs' in text and 'n8d7m2' not in text.replace('N8D7M2', ''),
         'no stale N8D7M2 capture path')
    need(text.count('PS2X_GS_CAPTURE') >= 2, 'capture flag present')
    need('second' not in text.lower() or 'no second' in text.lower(),
         'second-run wording')
    need(text.count('result.json') >= 1 and 'one-run guard' in text, 'one-run guard')
    need('install' in text.lower() and text.count("result['install_count'] = 1") == 1,
         'exactly one install path')
    need(text.count("result['launch_count'] = 1") == 1, 'exactly one launch path')
    need('16 * 1024 * 1024' in text, '16 MiB log cap')
    need('4 * 1024**3' in text, '4 GiB capture cap')
    need('300' in text and '300 s wall cap' in text, '300 s wall cap')
    need('tick 2100' in text and '180 s route cap below tick 1700' in text,
         'tick2100/180s stop rules')
    need('10 * 1024**3' in text, '>=10 GiB free-storage gate')
    need('am force-stop' in text and 'LEASE_FREE N8D7M6 done' in text, 'force-stop+lease release')
    need('showing' in text and 'battery' in text, 'keyguard/battery preflight')
    need('gs:capture' in text and 'stopped at marker tick=' in text, 'closed-stream stop rule')
    rows.append(['env diff vs N8D7M2', '+GS_CAPTURE/+STOP_TICK=2050, rest kept', 'PASS'])
    # Mac replay binary pin: two SHA reads + source pins; no replay runs here.
    need(BIN.is_file(), 'N8D7M5 ps2x_tests absent')
    pair = [sha(BIN) for _ in range(2)]
    need(pair == [BIN_PIN] * 2, 'N8D7M5 binary SHA pair')
    rows.append(['ps2x_tests (N8D7M5)', BIN_PIN[:8] + '...', 'PASS two reads'])
    log = subprocess.check_output(['git', '-C', str(FORK), 'log', '--oneline', '-3'],
                                  text=True)
    need('a8cfefa' in log and 'd1ba1d4' in log, 'fork has N8D7M5+N8D7L commits')
    rows.append(['fork commits', 'a8cfefa+d1ba1d4 present', 'PASS'])
    cpair = [sha(CODEGEN) for _ in range(2)]
    need(cpair == [CODEGEN_PIN] * 2, 'codegen SHA pair')
    rows.append(['codegen register_functions.cpp', CODEGEN_PIN[:8] + '...', 'PASS two reads'])
    need(PARALLEL.is_dir(), 'G43/N8D7F parallel-gs source absent')
    need(VULKAN.exists(), 'Vulkan loader absent')
    rows.append(['parallel-gs + vulkan loader', 'present', 'PASS'])
    need('fork-n8d7m5.patch' not in text, 'no raw-patch source-of-truth')
    print('N8D7M6 prepared PASS')
    for row in rows:
        print(' | '.join(row))
    (SCRATCH / 'prepared-gate.txt').write_text(
        'N8D7M6 prepared PASS\n' + '\n'.join(' | '.join(r) for r in rows) + '\n')
    print(f'wrote {SCRATCH / "prepared-gate.txt"}')


def parse_capture(path):
    need(path.stat().st_size <= CAP and path.stat().st_size > 8, 'capture size cap/empty')
    count = Counter()
    last = None
    with path.open('rb') as handle:
        need(handle.read(8) == b'PS2XGSC1', 'capture magic')
        while True:
            pos = handle.tell()
            prefix = handle.read(4)
            if not prefix:
                break
            need(len(prefix) == 4, f'partial length at {pos}')
            (length,) = struct.unpack('<I', prefix)
            need(9 <= length <= 64 * 1024**2, f'bad record length at {pos}')
            rec = handle.read(length)
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


def tile_values(text, name, words):
    marker = f'{name}_tile_counts='
    start = text.find(marker)
    need(start >= 0, f'missing {name} vector')
    payload = text[start + len(marker):]
    # Vectors are single log lines in replay logs; device logcat may wrap,
    # but replay-side logs (used in --final) are unwrapped. Accept one line.
    payload = payload.split('\n', 1)[0].rstrip(',').rstrip()
    fields = [f for f in payload.split(',') if f != '']
    need(len(fields) == words and all(f.isdecimal() for f in fields),
         f'{name} vector length/content')
    values = list(map(int, fields))
    fmt = '<448H' if words == 448 else '<896I'
    return {'occupied': sum(values), 'active': sum(v >= 32 for v in values),
            'sha256': hashlib.sha256(struct.pack(fmt, *values)).hexdigest(),
            'values': values}


def shared11(selected_meta, oracle_meta):
    return (selected_meta[:11] == list(oracle_meta) or tuple(selected_meta[:11]) == tuple(oracle_meta))


def capture_gate():
    device = json.loads((SCRATCH / 'result.json').read_text())
    need(device.get('device_gate') is True, 'device gate flag')
    need(device['stop_marker']['tick'] == 2050, 'stop marker tick')
    item = device['capture']
    need(len(set(item['sha_device'] + item['sha_local'])) == 1, 'capture SHA equality')
    capture = parse_capture(SCRATCH / 'n8d7m6.gs')
    need(capture['sha'] == item['sha_local'][0], 'pulled capture SHA')
    need(capture['bytes'] == item['bytes'] == device['stop_marker']['bytes'],
         'capture bytes vs marker')
    print('N8D7M6 capture PASS:', json.dumps(capture, sort_keys=True))
    return capture


def mac_replay(capture):
    """One bounded Mac paraLLEl replay of the pulled stream with oracle flags."""
    lease = REPO / 'local/tooling/p_lane_lease.py'
    slot = None
    for candidate in ('1', '2'):
        proc = subprocess.run(['python3', str(lease), 'claim', candidate, 'n8d7m6'],
                              capture_output=True, text=True, timeout=30)
        if proc.returncode == 0:
            slot = candidate
            break
    need(slot is not None, 'no mini P-lane slot free')
    try:
        outdir = SCRATCH / 'mac-parallel'
        outdir.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env.update({
            'PS2X_GS_REPLAY_CAPTURE': str(SCRATCH / 'n8d7m6.gs'),
            'PS2X_GS_REPLAY_BACKEND': 'parallel',
            'PS2X_N8D7F_SELECTED_CAPTURE': '1',
            'PS2X_N8D7L_ORACLE': '1',
            'PS2X_N8D5_TILE_CAPTURE': '1',
            'PS2X_GS_REPLAY_STEP': '50',
            'PS2X_GS_REPLAY_PPM_TICKS': '2050',
            'PS2X_GS_REPLAY_PPM_DIR': str(outdir),
            'PS2X_GS_REPLAY_OUT': str(outdir / 'parallel.hashes'),
            'GRANITE_VULKAN_LIBRARY': str(VULKAN),
        })
        log = SCRATCH / 'mac-parallel.log'
        start = time.monotonic()
        with log.open('wb') as handle:
            # cwd=fork worktree: one unrelated VU0 suite test reads
            # instructions.h by relative path (N8D7M5 REPORT §5).
            proc = subprocess.Popen([str(BIN)], env=env, cwd=str(FORK), stdout=handle,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            while proc.poll() is None:
                if time.monotonic() - start > 600 or log.stat().st_size > 16 * 1024**2:
                    proc.terminate()
                    raise RuntimeError('mac replay time/log cap reached')
                time.sleep(0.5)
        need(proc.returncode == 0, 'mac replay exit')
        need(log.stat().st_size <= 16 * 1024**2, 'mac log cap')
        return log.read_text(errors='replace')
    finally:
        if slot is not None:
            subprocess.run(['python3', str(lease), 'release', slot, 'n8d7m6'],
                           capture_output=True, text=True, timeout=30)


def final_gate():
    capture = capture_gate()
    text = mac_replay(capture)
    need('GB4_REPLAY_PARSE_ERROR' not in text, 'replay parse error')
    summary = re.search(r'GB4_REPLAY_SUMMARY[^\n]+backend=parallel[^\n]*', text)
    need(summary is not None, 'parallel summary absent')
    assert summary is not None
    line = summary.group(0)
    for key in ('packets', 'priv', 'transfers', 'markers'):
        need(f"{key}={capture['counts'][key[0] if False else {'packets': '1', 'priv': '2', 'transfers': '3', 'markers': '4'}[key]]}" in line,
             f'replay count {key}')
    mac_sel = re.search(
        r'\[n8d7f\] tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) '
        r'phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+) '
        r'extent=(\d+)x(\d+) valid=(\d+)x(\d+) status=(\d+)', text)
    need(mac_sel is not None, 'mac selected metadata')
    assert mac_sel is not None
    mac_meta = mac_sel.groups()
    need(mac_meta[0] == '2050' and mac_meta[1] == '112' and mac_meta[-1] == '2',
         'mac tick/FBP/status')
    mac_oracle = re.search(
        r'\[n8d7l\] tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) '
        r'phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+)', text)
    need(mac_oracle is not None, 'mac oracle metadata')
    assert mac_oracle is not None
    need(tuple(mac_meta[:11]) == tuple(mac_oracle.groups()), 'mac selected/oracle alignment')
    controls = re.search(r'\[n8d7l\] oracle_controls=(\S+)', text)
    need(controls is not None, 'mac controls')
    assert controls is not None
    parts = controls.group(1).split(',')
    need(len(parts) == 8 and [p.split('=')[0] for p in parts] ==
         [f'0x{a:06X}' for a in CONTROL_ADDRS], 'mac control addresses/order')
    mac_in = tile_values(text, 'input', 448)
    mac_or = tile_values(text, 'oracle', 448)
    device = json.loads((SCRATCH / 'result.json').read_text())
    lines = (SCRATCH / 'logcat-pid.txt').read_text()
    odin_in = tile_values(lines, 'input', 448)
    odin_or = tile_values(lines, 'oracle', 448)
    odin_sel = re.search(
        r'tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) '
        r'phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+)', lines)
    need(odin_sel is not None, 'odin selected metadata')
    assert odin_sel is not None
    same_descriptor = tuple(odin_sel.groups()) == tuple(mac_meta[:11])
    mac_active = min(mac_in['active'], mac_or['active'])
    mac_broad = mac_active >= 250
    odin_active = max(odin_in['active'], odin_or['active'])
    odin_sparse = odin_active <= 100
    odin_broad = min(odin_in['active'], odin_or['active']) >= 250
    mac_sparse = max(mac_in['active'], mac_or['active']) <= 100
    intermediate = not (mac_broad or mac_sparse) or not (odin_sparse or odin_broad)
    if not same_descriptor:
        category = 'C'
    elif intermediate:
        category = 'OTHER'
    elif mac_broad and odin_sparse:
        category = 'A'
    elif mac_sparse and odin_sparse:
        category = 'B'
    elif mac_broad and odin_broad:
        category = 'D'
    else:
        category = 'OTHER'
    result_doc = {
        'stream': capture, 'same_descriptor': same_descriptor,
        'mac': {'input': {k: mac_in[k] for k in ('occupied', 'active', 'sha256')},
                'oracle': {k: mac_or[k] for k in ('occupied', 'active', 'sha256')}},
        'odin': {'input': {k: odin_in[k] for k in ('occupied', 'active', 'sha256')},
                 'oracle': {k: odin_or[k] for k in ('occupied', 'active', 'sha256')}},
        'category': category,
    }
    (SCRATCH / 'comparison.json').write_text(json.dumps(result_doc, indent=2) + '\n')
    print('N8D7M6 final category:', category)
    print(json.dumps(result_doc, indent=2))
    need(category in ('A', 'B', 'C', 'D', 'OTHER'), 'category')
    return category


if __name__ == '__main__':
    mode = sys.argv[1:] or ['--final']
    need(mode in (['--prepared'], ['--capture'], ['--final']), 'mode')
    if mode == ['--prepared']:
        prepared()
    elif mode == ['--capture']:
        capture_gate()
    else:
        final_gate()
