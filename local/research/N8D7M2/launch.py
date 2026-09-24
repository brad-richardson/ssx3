#!/usr/bin/env python3
"""N8D7M2: one leased Odin install and launch after orchestrator review.

Adapted from ``local/research/N8D7I/launch.py`` for one N8D7M1 install and one
launch. It enables ``PS2X_N8D7L_ORACLE=1`` together with the N8D7I
selected/stage/tile flags, parses the full 448-word ``[n8d7f] oracle_tile_counts``
vector and the ``[n8d7l]`` metadata / ``oracle_controls`` / ``oracle_input_equal``
lines alongside the N8D7I vectors, checks the eight literal control addresses
against the N8D7L Mac control set, and classifies the same tick-2050 frame into
A-D or OTHER. No device action may run before the orchestrator releases the
reviewed SHA in this pane.
"""

import gzip
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import subprocess
import sys
import time
from zipfile import ZipFile

SERIAL = '622c49b1'
PKG = 'com.ps2x.runner'
SCRATCH = Path('/Users/brad/dev/ssx3-work/N8D7M2')
APK = Path('/Users/brad/dev/ssx3-work/N8D7M1/app-release.apk')
APK_SIZE = 153736732
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
LEASE = '/data/local/tmp/mg/LEASE'
LEASE_TAG = 'N8D7M2 one-launch'
LOG_CAP = 16 * 1024 * 1024
COMPLETE = 'first complete oracle and vector receipt with frontend dump'
PINS = {
    'apk': 'e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1',
    'runner': 'f3de999acc9227b82a9d9fab6a4a0b5b7fb279e6205991c1b3022da781e3c1bf',
    'turnip': '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d',
    'hal': '1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387',
    'elf': '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
    'iso': '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
}
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000')
# Literal (byte-address) control set from N8D7L REPORT §1, in kOracleControls
# order (ps2_gs_parallel_backend.cpp). Addresses are compile-time constants, so
# they must match the device log exactly; the eight word values are the on-device
# VRAM reads and are compared to the Mac literal set only as a separate
# observation, never inferred as cross-device identity.
CONTROL_ADDRS = (0x0E0000, 0x0E0534, 0x0E0040, 0x1BFFF4,
                 0x0E2000, 0x0F0000, 0x0E1FFC, 0x0F2000)
MAC_CONTROLS = {
    0x0E0000: 0x00260803, 0x0E0534: 0x00260802, 0x0E0040: 0x00260804,
    0x1BFFF4: 0x000C0000, 0x0E2000: 0x00260802, 0x0F0000: 0xFF230401,
    0x0E1FFC: 0x003D2B00, 0x0F2000: 0x00604400,
}

result = {'brief': 'N8D7M2', 'install_count': 0, 'launch_count': 0,
          'hashes': {}, 'events': [], 'category': 'not found',
          'first_failure': 'not found'}
lease_claimed = False
launched = False
force_stopped = False
logger = None
log_stream = None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def record(message):
    print(message, flush=True)
    result['events'].append(message)
    with (SCRATCH / 'driver.log').open('a') as handle:
        handle.write(message + '\n')
    (SCRATCH / 'result.json').write_text(json.dumps(result, indent=2) + '\n')


def adb(*args, timeout=90, check=True):
    completed = subprocess.run(['adb', '-s', SERIAL, *args], capture_output=True,
                               text=True, timeout=timeout)
    if check and completed.returncode:
        raise RuntimeError(f'adb {args} rc={completed.returncode}: '
                           f'{completed.stderr.strip()} {completed.stdout.strip()}')
    return completed.stdout


def shell(command, timeout=90):
    return adb('shell', command, timeout=timeout).strip()


def pidof():
    return adb('shell', f'pidof {PKG}', check=False).strip()


def preflight(ours=False):
    state = adb('get-state').strip()
    lease = shell(f'cat {LEASE}')
    policy = shell('dumpsys window policy')
    battery = shell('dumpsys battery')
    showing = re.search(r'KeyguardServiceDelegate\s+showing=(\w+)', policy)
    if not showing:
        showing = re.search(r'KeyguardServiceDelegate.*?showing=(\w+)', policy, re.S)
    level_match = re.search(r'\blevel:\s*(\d+)', battery)
    status_match = re.search(r'\bstatus:\s*(\d+)', battery)
    level = int(level_match.group(1)) if level_match else -1
    status = int(status_match.group(1)) if status_match else -1
    free = int(shell('df -k /storage/emulated/0').splitlines()[-1].split()[3]) * 1024
    keyguard = showing.group(1) if showing else 'unknown'
    record(f'PREFLIGHT state={state} lease={lease!r} keyguard={keyguard} '
           f'battery={level}% status={status} free_bytes={free}')
    free_lease = lease.startswith('LEASE_FREE') or (ours and lease == LEASE_TAG)
    if state != 'device' or not free_lease or keyguard != 'false' or level < 20 \
            or status not in (2, 5) or free < 1024**3:
        raise RuntimeError('preflight failed (device, lease, unlock, charging, or storage)')


def check_device_sha(label, remote, pin):
    reads = [shell(f'sha256sum {shlex.quote(remote)}', timeout=240).split()[0]
             for _ in range(2)]
    result['hashes'][label] = reads
    record(f'HASH {label} {reads[0]} {reads[1]}')
    if reads != [pin, pin]:
        raise RuntimeError(f'{label} SHA mismatch')


def check_apk():
    if APK.stat().st_size != APK_SIZE:
        raise RuntimeError('local APK size mismatch')
    reads = [file_sha(APK) for _ in range(2)]
    result['hashes']['local_apk'] = reads
    if reads != [PINS['apk']] * 2:
        raise RuntimeError('local APK SHA mismatch')
    with ZipFile(APK) as archive:
        for label, member in (
            ('runner', 'lib/arm64-v8a/libps2EntryRunner.so'),
            ('turnip', 'lib/arm64-v8a/libvulkan_freedreno.so'),
            ('hal', 'lib/arm64-v8a/libhardware.so'),
        ):
            pair = [sha256(archive.read(member)) for _ in range(2)]
            result['hashes']['packaged_' + label] = pair
            if pair != [PINS[label]] * 2:
                raise RuntimeError(f'packaged {label} SHA mismatch')
    record('APK size and packaged runner/Turnip/HAL SHA pairs match N8D7M1 pins')


def same_pid_lines(pid):
    path = SCRATCH / 'logcat-all.txt'
    if path.stat().st_size > LOG_CAP:
        raise RuntimeError('16 MiB log cap exceeded')
    lines = path.read_text(errors='replace').splitlines()
    pattern = re.compile(rf'^\s*\d+\.\d+\s+{re.escape(pid)}\s+')
    return [line for line in lines if pattern.search(line)]


def tile_vector(lines, name, words, pack):
    """Parse one wrapped ``<name>_tile_counts=`` logcat vector.

    ``name`` is the vector stem without the suffix: ``sampled``/``raw`` for the
    896-word ``[n8d5b]`` vectors, ``input``/``circuit``/``stage``/``oracle`` for
    the 448-word ``[n8d7f]`` vectors. ``words`` is the exact accepted length and
    ``pack`` the little-endian struct format used for the packed SHA.

    A logcat segment boundary can swallow the separator comma, so the wrapped
    continuation line starts with exactly one leading comma; that comma is the
    real separator, not an empty field. Any incompleteness, wrong length,
    malformed field or inconsistent continuation returns ``None``.
    """
    marker = f'{name}_tile_counts='
    prefix = re.compile(r'^.*?\bI ps2x\s+: (.*)$')
    values = []
    collecting = False
    pending = 0
    for line in lines:
        if marker in line:
            values = []
            collecting = True
            pending = 0
            payload = line.split(marker, 1)[1]
        elif collecting:
            match = prefix.match(line)
            if not match or match.group(1).startswith('['):
                break
            payload = match.group(1)
            leading = len(payload) - len(payload.lstrip(','))
            if pending + leading != 1:
                return None
            payload = payload.lstrip(',')
        else:
            continue
        trailing = len(payload) - len(payload.rstrip(','))
        if trailing > 1:
            return None
        pending = trailing
        fields = payload.rstrip(',').split(',')
        if any(not field.isdecimal() for field in fields):
            return None
        values.extend(map(int, fields))
        if len(values) > words:
            return None
        if len(values) == words:
            packed = struct.pack(pack, *values)
            return {'words': words, 'occupied': sum(values),
                    'active': sum(value >= 32 for value in values),
                    'sha256': sha256(packed), 'values': values}
    return None


def parse_controls(payload):
    """Parse ``[n8d7l] oracle_controls=0xADDR=0xVALUE,...`` into 8 pairs.

    Returns ``None`` unless there are exactly eight well-formed ``addr=value``
    hex pairs; addresses are returned as ints in log order.
    """
    if payload is None:
        return None
    parts = payload.split(',')
    if len(parts) != 8:
        return None
    out = []
    for part in parts:
        pair = part.split('=')
        if len(pair) != 2:
            return None
        try:
            out.append((int(pair[0], 16), int(pair[1], 16)))
        except ValueError:
            return None
    return out


def oracle_details(p):
    """Bounded same-run report: controls, equality and oracle summary."""
    oracle = p.get('oracle', {})
    selected = p.get('selected', {})
    vectors = p.get('vectors', {})
    details = {'metadata': oracle.get('metadata'), 'summary': selected.get('oracle'),
               'equal_logged': None, 'equal_recomputed': None, 'vector_sha': None,
               'controls_present': 0, 'addresses_ok': False, 'value_matches': 0,
               'control_words': []}
    if oracle.get('equal'):
        details['equal_logged'] = int(oracle['equal'][0])
    ov = vectors.get('oracle')
    iv = vectors.get('input')
    if ov:
        details['vector_sha'] = ov['sha256']
    if ov and iv:
        details['equal_recomputed'] = sum(a == b for a, b in zip(ov['values'], iv['values']))
    controls = parse_controls(oracle['controls'][0]) if oracle.get('controls') else None
    if controls:
        details['controls_present'] = len(controls)
        details['addresses_ok'] = [a for a, _ in controls] == list(CONTROL_ADDRS)
        details['control_words'] = [
            {'addr': f'0x{addr:06X}', 'value': f'0x{value:08X}',
             'mac': f'0x{MAC_CONTROLS[addr]:08X}' if addr in MAC_CONTROLS else None,
             'match': MAC_CONTROLS.get(addr) == value}
            for addr, value in controls]
        details['value_matches'] = sum(w['match'] for w in details['control_words'])
    return details


def probe(lines):
    relevant = [line.split('[n8d5b] ', 1)[1] for line in lines if '[n8d5b] ' in line]
    stage_lines = [line.split('[n8d6a] ', 1)[1] for line in lines if '[n8d6a] ' in line]
    selected_lines = [line.split('[n8d7f] ', 1)[1] for line in lines if '[n8d7f] ' in line]
    oracle_lines = [line.split('[n8d7l] ', 1)[1] for line in lines if '[n8d7l] ' in line]
    out = {}
    patterns = {
        'alignment': r'alignment tick=(\d+) fbp=(\d+) pmode=([0-9a-fA-F]+) width=(\d+) height=(\d+)',
        'control': r'control=(\d+) expected=(\d+) (PASS|FAIL)',
        'sampled': r'sampled_summary tiles=(\d+) occupied=(\d+) active=(\d+)',
        'raw': r'raw_summary tiles=(\d+) occupied=(\d+) active=(\d+)',
    }
    for key, pattern in patterns.items():
        matches = [re.search(pattern, line) for line in relevant]
        out[key] = next((m.groups() for m in matches if m), None)
    out['stages'] = {}
    stage_pattern = re.compile(
        r'^stage=(circuit1|pre_deinterlace_merged|final) width=(\d+) height=(\d+) '
        r'tiles=(\d+) occupied=(\d+) active=(\d+) control=(\d+)$')
    for line in stage_lines:
        match = stage_pattern.fullmatch(line)
        if match:
            name, *values = match.groups()
            out['stages'][name] = tuple(map(int, values))
    out['selected'] = {}
    selected_patterns = {
        'metadata': (r'tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) '
                     r'phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+) '
                     r'extent=(\d+)x(\d+) valid=(\d+)x(\d+) status=(\d+)'),
        'bytes': r'bytes=(\d+) vram_sha256=(\S+) input_sha256=(\S+) circuit_sha256=(\S+)',
        'input': r'input tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)',
        'circuit': r'circuit tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)',
        'stage': r'stage tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)',
        'oracle': r'oracle tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)',
        'equal': r'input_circuit_equal=(\d+)/448 circuit_stage_equal=(\d+)/448',
    }
    for key, pattern in selected_patterns.items():
        matches = [re.search(pattern, line) for line in selected_lines]
        out['selected'][key] = next((m.groups() for m in matches if m), None)
    out['oracle'] = {}
    oracle_patterns = {
        'metadata': (r'tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) '
                     r'phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+)'),
        'controls': r'oracle_controls=(\S+)',
        'equal': r'oracle_input_equal=(\d+)/448',
    }
    for key, pattern in oracle_patterns.items():
        matches = [re.search(pattern, line) for line in oracle_lines]
        out['oracle'][key] = next((m.groups() for m in matches if m), None)
    out['vectors'] = {
        'sampled': tile_vector(lines, 'sampled', 896, '<896I'),
        'raw': tile_vector(lines, 'raw', 896, '<896I'),
        'input': tile_vector(lines, 'input', 448, '<448H'),
        'circuit': tile_vector(lines, 'circuit', 448, '<448H'),
        'stage': tile_vector(lines, 'stage', 448, '<448H'),
        'oracle': tile_vector(lines, 'oracle', 448, '<448H'),
    }
    out['errors'] = [line for line in relevant + stage_lines + selected_lines + oracle_lines
                     if 'ERROR' in line or 'alignment=OTHER' in line or 'OTHER' in line]
    out['errors'] += [line for line in lines if re.search(
        r'\b(pipeline|probe)\b.*\b(error|failed)\b', line, re.I)]
    return out


def first_dump(lines):
    pattern = re.compile(r'\[frame:dump\] seq=(\d+) tick=(\d+) size=(\d+)x(\d+) '
                         r'fbp=(\d+)/(\d+) fallback=(\d+)')
    for line in lines:
        match = pattern.search(line)
        if match and int(match.group(2)) >= 2050:
            return tuple(int(x) for x in match.groups())
    return None


def frame_ready(dump, frame):
    seq, tick, *_ = frame
    if tick != 2050:
        return False
    name = f'upload-{seq}'
    remote = f'{dump}/{name}.txt'
    metadata = shell(f'if test -f {shlex.quote(remote)}; then cat {shlex.quote(remote)}; fi')
    if not metadata or not re.search(r'\btick=2050\b', metadata):
        return False
    exists = shell(f'if test -f {shlex.quote(dump + "/" + name + ".png")}; '
                   'then echo yes; else echo no; fi')
    return exists == 'yes'


def pull_frame(dump, frame):
    seq, tick, width, height, display_fbp, source_fbp, fallback = frame
    if tick != 2050 or fallback or (width, height) != (512, 448):
        raise RuntimeError('no tick-2050 frontend upload with expected dimensions')
    entry = {'seq': seq, 'tick': tick, 'size': [width, height],
             'fbp': [display_fbp, source_fbp], 'fallback': fallback}
    for suffix in ('png', 'txt'):
        name = f'upload-{seq}.{suffix}'
        remote = f'{dump}/{name}'
        local = SCRATCH / name
        device = [shell(f'sha256sum {shlex.quote(remote)}').split()[0] for _ in range(2)]
        adb('pull', remote, str(local), timeout=90)
        local_pair = [file_sha(local) for _ in range(2)]
        if len(set(device + local_pair)) != 1:
            raise RuntimeError(f'{name} SHA mismatch after pull')
        entry[suffix] = {'name': name, 'sha_device': device, 'sha_local': local_pair,
                         'bytes': local.stat().st_size}
    entry['metadata'] = (SCRATCH / f'upload-{seq}.txt').read_text().strip()
    expected_metadata = (f'seq={seq} tick=2050 size=512x448 displayFbp=112 '
                         'sourceFbp=112 preferred=0 fallback=0')
    if not entry['metadata'].startswith(expected_metadata) \
            or not re.search(r'\bpmode=0xff21\b', entry['metadata']):
        raise RuntimeError('frontend metadata mismatch')
    result['frame'] = entry
    record(f'FRAME {entry["metadata"]} PNG_SHA={entry["png"]["sha_device"][0]}')


def classify(p, frame):
    selected = p.get('selected', {})
    oracle = p.get('oracle', {})
    vectors = p.get('vectors', {})
    stages = p.get('stages', {})
    if not all(p.get(key) for key in ('alignment', 'control', 'sampled', 'raw')) \
            or not frame or not all(selected.values()) \
            or not all(oracle.values()) \
            or not all(vectors.get(kind) for kind in
                       ('sampled', 'raw', 'input', 'circuit', 'stage', 'oracle')) \
            or set(stages) != {'circuit1', 'pre_deinterlace_merged', 'final'}:
        return 'OTHER'
    tick, fbp, pmode, width, height = p['alignment']
    control, expected, status = p['control']
    sampled_tiles, sampled_occupied, sampled_active = p['sampled']
    raw_tiles, raw_occupied, raw_active = p['raw']
    circuit1 = stages['circuit1']
    merged = stages['pre_deinterlace_merged']
    final = stages['final']
    (s_tick, s_fbp, s_fbw, s_psm, s_dbx, s_dby, s_phase, s_stride, s_mask,
     s_samples, s_promoted, s_ew, s_eh, s_vw, s_vh, s_status) = selected['metadata']
    in_tiles, in_occ, in_active, in_sha = selected['input']
    ci_tiles, ci_occ, ci_active, ci_sha = selected['circuit']
    st_tiles, st_occ, st_active, st_sha = selected['stage']
    o_tiles, o_occ, o_active, o_sha = selected['oracle']
    ic_equal, cs_equal = selected['equal']
    (r_tick, r_fbp, r_fbw, r_psm, r_dbx, r_dby, r_phase, r_stride, r_mask,
     r_samples, r_promoted) = oracle['metadata']
    oracle_equal, = oracle['equal']
    controls = parse_controls(oracle['controls'][0])
    # Every shared selected/oracle metadata field must describe the same frame:
    # tick, FBP, FBW, PSM, DBX, DBY, phase, stride, mask, samples, promoted.
    # A field that disagrees between [n8d7f] and [n8d7l] is OTHER.
    selected_shared = (s_tick, s_fbp, s_fbw, s_psm, s_dbx, s_dby, s_phase, s_stride,
                       s_mask, s_samples, s_promoted)
    oracle_shared = (r_tick, r_fbp, r_fbw, r_psm, r_dbx, r_dby, r_phase, r_stride,
                     r_mask, r_samples, r_promoted)
    if p['errors'] \
            or (int(tick), int(fbp), pmode.lower(), int(width), int(height)) \
            != (2050, 112, 'ff21', 512, 448) \
            or (control, expected, status) != ('128', '128', 'PASS') \
            or (sampled_tiles, raw_tiles) != ('896', '896') \
            or frame[1] != 2050 or frame[2:7] != (512, 448, 112, 112, 0) \
            or circuit1[:3] != (512, 224, 448) or merged[:3] != (512, 224, 448) \
            or final[:3] != (512, 448, 896) \
            or any(stage[5] != 128 for stage in stages.values()) \
            or (final[3], final[4]) != (int(sampled_occupied), int(sampled_active)) \
            or (int(s_tick), int(s_fbp), int(s_samples), int(s_promoted), int(s_status)) \
            != (2050, 112, 1, 0, 2) \
            or (int(s_vw), int(s_vh)) != (512, 224) \
            or (in_tiles, ci_tiles, st_tiles, o_tiles) != ('448', '448', '448', '448') \
            or (int(r_tick), int(r_fbp), int(r_fbw), int(r_psm), int(r_samples),
                int(r_promoted), int(r_mask)) != (2050, 112, 8, 1, 1, 0, 4194303) \
            or selected_shared != oracle_shared \
            or controls is None or [a for a, _ in controls] != list(CONTROL_ADDRS):
        return 'OTHER'
    for kind, summary in (('sampled', p['sampled']), ('raw', p['raw'])):
        vector = vectors[kind]
        if (vector['occupied'], vector['active']) != (int(summary[1]), int(summary[2])):
            return 'OTHER'
    # The packed SHA is Apple-only: selectedSha256() logs "unavailable" on
    # Android. Recompute it from the full parsed vector and compare only when
    # the firmware printed a real digest.
    for kind, summary in (('input', selected['input']), ('circuit', selected['circuit']),
                          ('stage', selected['stage']), ('oracle', selected['oracle'])):
        vector = vectors[kind]
        if (vector['occupied'], vector['active']) != (int(summary[1]), int(summary[2])):
            return 'OTHER'
        if summary[3] != 'unavailable' and summary[3] != vector['sha256']:
            return 'OTHER'
    if vectors['sampled']['values'] != vectors['raw']['values']:
        return 'OTHER'
    in_values = vectors['input']['values']
    ci_values = vectors['circuit']['values']
    st_values = vectors['stage']['values']
    or_values = vectors['oracle']['values']
    if (int(ic_equal), int(cs_equal)) != (sum(a == b for a, b in zip(in_values, ci_values)),
                                          sum(a == b for a, b in zip(ci_values, st_values))):
        return 'OTHER'
    # The logged oracle/input equality must equal the recomputed cell-by-cell
    # equality; A/D require 448/448, B/C require <448/448.
    logged_equal = int(oracle_equal)
    recomputed_equal = sum(a == b for a, b in zip(or_values, in_values))
    if logged_equal != recomputed_equal:
        return 'OTHER'
    in_active = vectors['input']['active']
    or_active = vectors['oracle']['active']
    full = logged_equal == 448
    if full and or_active <= 100 and in_active <= 100:
        return 'A'
    if full and or_active >= 250 and in_active >= 250:
        return 'D'
    if not full and or_active >= 250 and in_active <= 100:
        return 'B'
    if not full and or_active <= 100 and in_active >= 250:
        return 'C'
    return 'OTHER'


def write_excerpt(p):
    lines = ['N8D7M2 same-run vectors reconstructed from the parsed same-PID log.',
             '448-word [n8d7f] vectors pack as little-endian uint16 for packed_sha256;',
             '896-word [n8d5b] vectors pack as little-endian uint32.', '']
    for tag, kinds in (('[n8d7f]', ('input', 'circuit', 'stage', 'oracle')),
                       ('[n8d5b]', ('sampled', 'raw'))):
        for kind in kinds:
            vector = p.get('vectors', {}).get(kind)
            if vector:
                lines.append(f'{tag} {kind}_tile_counts=' + ','.join(map(str, vector['values'])))
    details = oracle_details(p)
    lines += ['', 'oracle metadata: ' + repr(details['metadata']),
              'oracle summary:  ' + repr(details['summary']),
              'oracle equal logged/recomputed: '
              f'{details["equal_logged"]}/{details["equal_recomputed"]}',
              'controls present/addresses_ok/value_matches: '
              f'{details["controls_present"]}/{details["addresses_ok"]}/{details["value_matches"]}']
    for word in details['control_words']:
        lines.append(f'  {word["addr"]}={word["value"]} mac={word["mac"]} match={word["match"]}')
    (SCRATCH / 'tile-excerpt.txt').write_text('\n'.join(lines) + '\n')


def close_logger():
    global logger, log_stream
    if logger is not None:
        logger.terminate()
        try:
            logger.wait(timeout=3)
        except subprocess.TimeoutExpired:
            logger.kill()
            logger.wait(timeout=3)
        logger = None
    if log_stream is not None:
        log_stream.close()
        log_stream = None
    path = SCRATCH / 'logcat-all.txt'
    if path.exists():
        if path.stat().st_size > LOG_CAP:
            result['first_failure'] = '16 MiB log cap exceeded'
        with path.open('rb') as source, gzip.open(SCRATCH / 'logcat-all.txt.gz', 'wb') as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)
        path.unlink()
        record(f'LOG_CLOSED gzip_bytes={(SCRATCH / "logcat-all.txt.gz").stat().st_size}')


def run():
    global lease_claimed, launched, force_stopped, logger, log_stream
    if len(sys.argv) != 3 or sys.argv[1] != '--released-sha':
        raise SystemExit('review hold: require --released-sha <reviewed launch.py SHA-256>')
    script_sha = file_sha(Path(__file__))
    if sys.argv[2] != script_sha:
        raise SystemExit('review hold: launch.py SHA differs from reviewed pin')
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if (SCRATCH / 'result.json').exists() or (SCRATCH / 'driver.log').exists():
        raise SystemExit('one-run guard: N8D7M2 receipt already exists')
    result['script_sha'] = script_sha
    record(f'SCRIPT_SHA {script_sha}')
    check_apk()
    preflight()
    shell(f"echo '{LEASE_TAG}' > {LEASE}")
    lease_claimed = True
    if shell(f'cat {LEASE}') != LEASE_TAG:
        raise RuntimeError('lease claim did not persist')
    record(f'LEASE claimed {LEASE_TAG}')
    installed_result = adb('install', '-r', str(APK), timeout=180).strip()
    result['install_count'] = 1
    record('INSTALL ' + installed_result.replace('\n', ' | '))
    installed = shell(f'pm path {PKG}').removeprefix('package:')
    if not installed.endswith('/base.apk'):
        raise RuntimeError('installed base.apk path absent')
    result['installed_path'] = installed
    check_device_sha('installed_apk', installed, PINS['apk'])
    check_device_sha('elf', f'{FILES}/SLUS_207.72', PINS['elf'])
    check_device_sha('iso', f'{FILES}/SSX3.iso', PINS['iso'])
    card = shell(f'ls -A {FILES}/mc0')
    record(f'CARD mc0 entries={card!r}')
    if card:
        raise RuntimeError('mc0 is not empty')
    dump = f'{FILES}/n8d7m2-frames-{int(time.time())}'
    if shell(f'if test -e {shlex.quote(dump)}; then echo present; else echo absent; fi') != 'absent':
        raise RuntimeError('frame directory already exists')
    shell(f'mkdir -p {shlex.quote(dump)}')
    if shell(f'ls -A {shlex.quote(dump)}'):
        raise RuntimeError('frame directory is not empty')
    result['frame_dir'] = dump
    env = (f'PS2X_GS_BACKEND=parallel\nPS2X_GS_TURNIP=1\nPS2X_SKIP_MOVIE=1\n'
           f'PS2X_CD_IMAGE={FILES}/SSX3.iso\nPS2X_PAD_SCRIPT={ROUTE}\n'
           f'PS2X_PAD_SCRIPT_CLOCK=vsync\nPS2X_N8D5_TILE_CAPTURE=1\n'
           f'PS2X_N8D7F_SELECTED_CAPTURE=1\nPS2X_N8D7L_ORACLE=1\n'
           f'PS2X_FRAME_DUMP_DIR={dump}\n'
           f'PS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999\n'
           f'PS2X_VSYNC_RATE_LOG=1\n')
    (SCRATCH / 'ps2x.env').write_text(env)
    adb('push', str(SCRATCH / 'ps2x.env'), f'{FILES}/ps2x.env')
    result['env_sha'] = shell(f'sha256sum {FILES}/ps2x.env').split()[0]
    if result['env_sha'] != file_sha(SCRATCH / 'ps2x.env'):
        raise RuntimeError('environment push SHA mismatch')
    record(f'ENV sha={result["env_sha"]} frame_dir={dump}')
    adb('shell', f'am force-stop {PKG}')
    adb('logcat', '-c')
    log_stream = (SCRATCH / 'logcat-all.txt').open('wb')
    logger = subprocess.Popen(['adb', '-s', SERIAL, 'logcat', '-v', 'epoch',
                               '-b', 'main', '-b', 'crash', '-s', 'ps2x',
                               'ps2x-hwcompat', 'raylib', 'DEBUG', 'libc',
                               'AndroidRuntime'], stdout=log_stream,
                              stderr=subprocess.STDOUT)
    preflight(ours=True)  # Final unlock, charge and storage check immediately before am start.
    start = time.monotonic()
    launched = True
    result['launch_count'] = 1
    am = shell(f'am start -n {PKG}/android.app.NativeActivity')
    record('LAUNCH ' + am.replace('\n', ' | '))
    pid = ''
    for _ in range(20):
        pid = pidof()
        if pid:
            break
        time.sleep(0.5)
    if not pid:
        raise RuntimeError('launch PID absent')
    result['pid'] = pid
    record(f'PID {pid}')
    last_tick = 0
    back_sent = False
    stop_reason = ''
    selected_frame = None
    selected_probe = {}
    while True:
        elapsed = time.monotonic() - start
        lines = same_pid_lines(pid)
        ticks = re.findall(r'\[vsync-rate\] tick=(\d+)', '\n'.join(lines))
        tick = int(ticks[-1]) if ticks else 0
        if tick > last_tick:
            last_tick = tick
            record(f'PROGRESS elapsed={elapsed:.1f}s tick={tick}')
        fatal = next((line for line in lines if any(token in line for token in
                     ('Turnip dlopen failed', 'Turnip HMI dlsym failed',
                      'Turnip dladdr(HMI) failed', 'Turnip HMI layout/open invalid',
                      'Turnip HAL open failed', 'Turnip HAL get-proc is null',
                      '[gs:parallel] FATAL:', 'Fatal signal', 'FATAL EXCEPTION'))), None)
        if fatal:
            stop_reason = 'first fatal: ' + fatal
            break
        if not pidof():
            stop_reason = 'process exited'
            break
        if elapsed >= 6 and not back_sent:
            shell('input keyevent 4')
            back_sent = True
            record('BACK sent once for USB dialog')
        selected_probe = probe(lines)
        selected_frame = first_dump(lines)
        if selected_probe['errors']:
            stop_reason = 'tile probe error: ' + selected_probe['errors'][0]
            break
        if selected_probe['control'] and selected_probe['control'] != ('128', '128', 'PASS'):
            stop_reason = 'tile control failed: ' + repr(selected_probe['control'])
            break
        if all(selected_probe.get(k) for k in ('alignment', 'control', 'sampled', 'raw')) \
                and set(selected_probe['stages']) == {'circuit1', 'pre_deinterlace_merged', 'final'} \
                and all(selected_probe['vectors'].values()) \
                and all(selected_probe['selected'].values()) \
                and all(selected_probe['oracle'].values()) \
                and selected_frame and frame_ready(dump, selected_frame):
            stop_reason = COMPLETE
            break
        if tick >= 2100:
            stop_reason = 'tick 2100 without complete receipt'
            break
        if elapsed >= 180 and tick < 1700:
            stop_reason = '180 s route cap below tick 1700'
            break
        if elapsed >= 300:
            stop_reason = '300 s wall cap'
            break
        time.sleep(1)
    result['final_tick'] = last_tick
    result['elapsed_s'] = round(time.monotonic() - start, 3)
    result['stop_reason'] = stop_reason
    result['probe'] = selected_probe
    result['frame_log'] = selected_frame
    record('STOP ' + stop_reason)
    lines = same_pid_lines(pid)
    (SCRATCH / 'logcat-pid.txt').write_text('\n'.join(lines) + '\n')
    adb('shell', f'am force-stop {PKG}', timeout=30)
    force_stopped = True
    time.sleep(1)
    if pidof():
        raise RuntimeError('force-stop left app PID present')
    record('POSTRUN pid absent')
    if stop_reason == COMPLETE:
        pull_frame(dump, selected_frame)
    # Report oracle details and the reconstructed vectors before writing bounded JSON.
    result['oracle'] = oracle_details(selected_probe)
    write_excerpt(selected_probe)
    result['category'] = classify(selected_probe, selected_frame if result.get('frame') else None)
    for vector in result['probe'].get('vectors', {}).values():
        if vector:
            del vector['values']
    record('CATEGORY ' + result['category'])
    if stop_reason != COMPLETE:
        raise RuntimeError(stop_reason)


if __name__ == '__main__':
    try:
        run()
    except (Exception, SystemExit) as exc:
        if SCRATCH.exists() and (SCRATCH / 'driver.log').exists():
            result['first_failure'] = str(exc)
            record('ERROR ' + repr(exc))
        raise
    finally:
        if lease_claimed:
            try:
                if launched and not force_stopped:
                    adb('shell', f'am force-stop {PKG}', timeout=30)
                    force_stopped = True
                    time.sleep(1)
                record('CLEANUP pid-after=' + (pidof() or 'none'))
            except Exception as exc:
                record('CLEANUP force-stop error=' + repr(exc))
            try:
                shell(f"echo 'LEASE_FREE N8D7M2 done' > {LEASE}")
                record('CLEANUP lease=' + shell(f'cat {LEASE}'))
            except Exception as exc:
                record('CLEANUP lease error=' + repr(exc))
        close_logger()
        if SCRATCH.exists() and (SCRATCH / 'driver.log').exists():
            (SCRATCH / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
