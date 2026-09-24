#!/usr/bin/env python3
"""N8D5G: one leased Odin install and launch after orchestrator review."""

import gzip
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from zipfile import ZipFile

SERIAL = '622c49b1'
PKG = 'com.ps2x.runner'
SCRATCH = Path('/Users/brad/dev/ssx3-work/N8D5G')
APK = Path('/Users/brad/dev/ssx3-work/N8D5F/app-release.apk')
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
LEASE = '/data/local/tmp/mg/LEASE'
LOG_CAP = 16 * 1024 * 1024
PINS = {
    'apk': '8c101c4824adbda8f2fa7126692791189e4d05df7e450680ff2b6e67d0be66a0',
    'runner': 'd1916d7bce3cc789c3e25d8e90c4db9cd0d1bcbfb037d27d4b3a6b1932476456',
    'turnip': '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d',
    'elf': '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
    'iso': '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
}
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000')

result = {'brief': 'N8D5G', 'install_count': 0, 'launch_count': 0,
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
    free_lease = lease.startswith('LEASE_FREE') or (ours and lease == 'N8D5G one-launch')
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
    reads = [file_sha(APK) for _ in range(2)]
    result['hashes']['local_apk'] = reads
    if reads != [PINS['apk']] * 2:
        raise RuntimeError('local APK SHA mismatch')
    with ZipFile(APK) as archive:
        for label, member in (
            ('runner', 'lib/arm64-v8a/libps2EntryRunner.so'),
            ('turnip', 'lib/arm64-v8a/libvulkan_freedreno.so'),
        ):
            pair = [sha256(archive.read(member)) for _ in range(2)]
            result['hashes']['packaged_' + label] = pair
            if pair != [PINS[label]] * 2:
                raise RuntimeError(f'packaged {label} SHA mismatch')
    record('APK and packaged runner/Turnip SHA pairs match N8D5F pins')


def same_pid_lines(pid):
    path = SCRATCH / 'logcat-all.txt'
    if path.stat().st_size > LOG_CAP:
        raise RuntimeError('16 MiB log cap exceeded')
    lines = path.read_text(errors='replace').splitlines()
    pattern = re.compile(rf'^\s*\d+\.\d+\s+{re.escape(pid)}\s+')
    return [line for line in lines if pattern.search(line)]


def probe(lines):
    relevant = [line.split('[n8d5b] ', 1)[1] for line in lines if '[n8d5b] ' in line]
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
    out['errors'] = [line for line in relevant if 'ERROR' in line or 'alignment=OTHER' in line]
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
    result['frame'] = entry
    record(f'FRAME {entry["metadata"]} PNG_SHA={entry["png"]["sha_device"][0]}')


def classify(p, frame):
    if not all(p.get(key) for key in ('alignment', 'control', 'sampled', 'raw')) or not frame:
        return 'OTHER'
    tick, fbp, pmode, width, height = p['alignment']
    control, expected, status = p['control']
    sampled_tiles, _, sampled_active = p['sampled']
    raw_tiles, _, raw_active = p['raw']
    if p['errors'] or (int(tick), int(fbp), pmode.lower(), int(width), int(height)) \
            != (2050, 112, 'ff21', 512, 448) or (control, expected, status) \
            != ('128', '128', 'PASS') or (sampled_tiles, raw_tiles) != ('896', '896') \
            or frame[1] != 2050 or frame[2:7] != (512, 448, 112, 112, 0):
        return 'OTHER'
    sampled = int(sampled_active)
    raw = int(raw_active)
    if sampled <= 100 and raw <= 100:
        return 'A'
    if sampled >= 500 and raw <= 100:
        return 'B'
    return 'OTHER'


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
        raise SystemExit('one-run guard: N8D5G receipt already exists')
    result['script_sha'] = script_sha
    record(f'SCRIPT_SHA {script_sha}')
    check_apk()
    preflight()
    shell(f"echo 'N8D5G one-launch' > {LEASE}")
    lease_claimed = True
    if shell(f'cat {LEASE}') != 'N8D5G one-launch':
        raise RuntimeError('lease claim did not persist')
    record('LEASE claimed N8D5G one-launch')
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
    dump = f'{FILES}/n8d5g-frames-{int(time.time())}'
    if shell(f'if test -e {shlex.quote(dump)}; then echo present; else echo absent; fi') != 'absent':
        raise RuntimeError('frame directory already exists')
    shell(f'mkdir -p {shlex.quote(dump)}')
    if shell(f'ls -A {shlex.quote(dump)}'):
        raise RuntimeError('frame directory is not empty')
    result['frame_dir'] = dump
    env = (f'PS2X_GS_BACKEND=parallel\nPS2X_GS_TURNIP=1\nPS2X_SKIP_MOVIE=1\n'
           f'PS2X_CD_IMAGE={FILES}/SSX3.iso\nPS2X_PAD_SCRIPT={ROUTE}\n'
           f'PS2X_PAD_SCRIPT_CLOCK=vsync\nPS2X_N8D5_TILE_CAPTURE=1\n'
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
                and selected_frame and frame_ready(dump, selected_frame):
            stop_reason = 'first complete tile receipt and frontend dump'
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
    if stop_reason == 'first complete tile receipt and frontend dump':
        pull_frame(dump, selected_frame)
    result['category'] = classify(selected_probe, selected_frame if result.get('frame') else None)
    record('CATEGORY ' + result['category'])
    if stop_reason != 'first complete tile receipt and frontend dump':
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
                shell(f"echo 'LEASE_FREE N8D5G done' > {LEASE}")
                record('CLEANUP lease=' + shell(f'cat {LEASE}'))
            except Exception as exc:
                record('CLEANUP lease error=' + repr(exc))
        close_logger()
        if SCRATCH.exists() and (SCRATCH / 'driver.log').exists():
            (SCRATCH / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
