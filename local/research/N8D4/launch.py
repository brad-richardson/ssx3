#!/usr/bin/env python3
"""N8D4 one-install/one-launch settled-race image probe; device writes use its lease."""
import atexit
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from zipfile import ZipFile

D = '622c49b1'
PKG = 'com.ps2x.runner'
ROOT = Path('/Users/brad/dev/ssx3-work/N8D4')
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
DUMP = f'{FILES}/n8d4-frames'
APK = Path('/Users/brad/dev/ssx3-work/N8D3/app-release.apk')
CAPTURE = f'{FILES}/n8d4.gs'
CAP = 4 * 1024**3
LOG_CAP = 16 * 1024**2
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000')
PINS = {
    'apk': '3970011d360b86a3f93f170df11e5964e2b467f01e7351c2cd1610b615b885be',
    'elf': '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
    'iso': '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
}
receipt = {'hashes': {}, 'images': [], 'screencaps': [], 'events': [], 'result': 'not found'}
lease_claimed = False
force_stopped = False
logger = None
log_file = None
launch_start = None


def adb(*args, timeout=90, check=True):
    p = subprocess.run(['adb', '-s', D, *args], text=True, capture_output=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(f'adb {args} rc={p.returncode}: {p.stderr.strip()} {p.stdout.strip()}')
    return p.stdout


def sh(command, timeout=90):
    return adb('shell', command, timeout=timeout).strip()


def pidof():
    return adb('shell', f'pidof {PKG}', check=False).strip()


def event(s):
    print(s, flush=True)
    receipt['events'].append(s)
    (ROOT / 'driver.log').open('a').write(s + '\n')
    (ROOT / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')


def local_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(chunk)
    return h.hexdigest()


def space_and_capture_size():
    df = sh('df -k /storage/emulated/0').splitlines()[-1].split()
    free = int(df[3]) * 1024
    size = int(sh(f'if test -f {CAPTURE}; then stat -c %s {CAPTURE}; else echo 0; fi'))
    event(f'BUDGET device_free={free} capture_bytes={size}')
    if free < 10 * 1024**3 or size > CAP:
        raise RuntimeError('device free-space or capture-size cap reached')
    return size


def cleanup():
    global logger, log_file, force_stopped
    if lease_claimed:
        try:
            if not force_stopped:
                adb('shell', f'am force-stop {PKG}', timeout=30)
                force_stopped = True
                time.sleep(1)
            event('CLEANUP pid-after=' + (pidof() or 'none'))
        except Exception as e:
            event('CLEANUP force-stop error=' + repr(e))
        try:
            adb('shell', "echo 'LEASE_FREE N8D4 done' > /data/local/tmp/mg/LEASE", timeout=30)
            event('CLEANUP lease=' + sh('cat /data/local/tmp/mg/LEASE'))
        except Exception as e:
            event('CLEANUP lease error=' + repr(e))
    if logger:
        logger.terminate()
        try:
            logger.wait(timeout=3)
        except subprocess.TimeoutExpired:
            logger.kill()
    if log_file:
        log_file.close()
    if launch_start is not None:
        event(f'CLEANUP launch-to-exit={time.monotonic() - launch_start:.1f}s')


atexit.register(cleanup)


def preflight(allow_ours=False):
    state = adb('get-state').strip()
    lease = sh('cat /data/local/tmp/mg/LEASE')
    policy = sh('dumpsys window policy')
    battery = sh('dumpsys battery')
    level = int(re.search(r'level: (\d+)', battery).group(1))
    status = int(re.search(r'status: (\d+)', battery).group(1))
    showing = re.search(r'KeyguardServiceDelegate\s+showing=(\w+)', policy)
    if not showing:
        showing = re.search(r'KeyguardServiceDelegate.*?showing=(\w+)', policy, re.S)
    event(f'PREFLIGHT device={state} lease={lease!r} keyguard={showing.group(1) if showing else "unknown"} battery={level}% status={status}')
    free_or_ours = lease.startswith('LEASE_FREE') or (allow_ours and lease == 'N8D4 one-launch')
    if state != 'device' or not free_or_ours or not showing or showing.group(1) != 'false' or level < 20 or status not in (2, 5):
        raise RuntimeError('preflight gate failed')


def device_hash(label, path, pin):
    reads = [sh(f'sha256sum {path}', timeout=240).split()[0] for _ in range(2)]
    receipt['hashes'][label] = reads
    event(f'HASH {label} {reads[0]} {reads[1]}')
    if reads != [pin, pin]:
        raise RuntimeError(f'{label} SHA mismatch')


def capture(label, tick):
    remote = f'/data/local/tmp/n8d4-{label}.png'
    local = ROOT / f'{label}.png'
    request_elapsed = time.monotonic() - launch_start
    sh(f'screencap -p {remote}', timeout=30)
    remote_shas = [sh(f'sha256sum {remote}').split()[0] for _ in range(2)]
    adb('pull', remote, str(local), timeout=60)
    local_shas = [hashlib.sha256(local.read_bytes()).hexdigest() for _ in range(2)]
    if len(set(remote_shas + local_shas)) != 1:
        raise RuntimeError(f'image {label} SHA mismatch')
    receipt['screencaps'].append({'name': local.name, 'trigger_host_tick': tick,
                                  'latest_logged_guest_tick': receipt.get('latest_logged_guest_tick', 0),
                                  'request_elapsed_seconds': round(request_elapsed, 3),
                                  'end_elapsed_seconds': round(time.monotonic() - launch_start, 3),
                                  'sha_remote': remote_shas, 'sha_local': local_shas,
                                  'bytes': local.stat().st_size})
    event(f'IMAGE {local.name} trigger_host_tick={tick} latest_logged_guest_tick={receipt.get("latest_logged_guest_tick", 0)} sha={remote_shas[0]} bytes={local.stat().st_size}')


def same_pid_log(pid):
    log = ROOT / 'logcat-all.txt'
    if log.exists() and log.stat().st_size > LOG_CAP:
        raise RuntimeError('log cap reached')
    data = log.read_text(errors='replace') if log.exists() else ''
    lines = [l for l in data.splitlines() if re.search(rf'^\s*\d+\.\d+\s+{pid}\s+', l)]
    (ROOT / 'logcat-pid.txt').write_text('\n'.join(lines[-120000:]) + '\n')
    return '\n'.join(lines)


def pull_frame_pairs():
    names = sh(f'ls -1 {DUMP}').splitlines()
    numbered = [n for n in names if re.fullmatch(r'(upload|fallback)-(?:\d+|latest)\.txt', n)]
    numbered.sort(key=lambda n: (n.endswith('-latest.txt'), int(re.search(r'-(\d+)\.txt$', n).group(1)) if re.search(r'-(\d+)\.txt$', n) else 9999))
    event('FRAME_DIR names=' + ','.join(names[:30]))
    for name in numbered[:3]:
        png = name[:-4] + '.png'
        if png not in names:
            event('FRAME_MISSING_PNG ' + png)
            continue
        entry = {'kind': name.split('-')[0], 'png': png, 'txt': name}
        for filename in (png, name):
            remote = f'{DUMP}/{filename}'
            remote_shas = [sh(f'sha256sum {remote}').split()[0] for _ in range(2)]
            local = ROOT / filename
            adb('pull', remote, str(local), timeout=60)
            local_shas = [hashlib.sha256(local.read_bytes()).hexdigest() for _ in range(2)]
            if len(set(remote_shas + local_shas)) != 1:
                raise RuntimeError(f'{filename} SHA pair mismatch')
            entry[filename + '_sha'] = remote_shas + local_shas
            entry[filename + '_bytes'] = local.stat().st_size
        entry['metadata'] = (ROOT / name).read_text().strip()
        receipt['images'].append(entry)
        event(f'FRAME {png} {entry["metadata"]} sha={entry[png + "_sha"][0]}')


def pull_stage_files():
    names = sh(f'ls -1 {DUMP}').splitlines()
    required = ('n8d3-raw.bin', 'n8d3-packed.bin', 'n8d3-stage.txt')
    receipt['stage_files'] = []
    for name in required:
        if name not in names:
            raise RuntimeError(f'stage capture missing: {name}')
        remote = f'{DUMP}/{name}'
        local = ROOT / name
        remote_shas = [sh(f'sha256sum {remote}').split()[0] for _ in range(2)]
        adb('pull', remote, str(local), timeout=60)
        local_shas = [hashlib.sha256(local.read_bytes()).hexdigest() for _ in range(2)]
        if len(set(remote_shas + local_shas)) != 1:
            raise RuntimeError(f'{name} SHA pair mismatch')
        receipt['stage_files'].append({'name': name, 'sha': remote_shas + local_shas,
                                       'bytes': local.stat().st_size})
        event(f'STAGE {name} sha={remote_shas[0]} bytes={local.stat().st_size}')
    receipt['result'] = 'capture and race stages captured'


def pull_capture():
    size = space_and_capture_size()
    if size <= 8:
        raise RuntimeError('capture absent or empty')
    hashes = [sh(f'sha256sum {CAPTURE}', timeout=300).split()[0] for _ in range(2)]
    if hashes[0] != hashes[1]:
        raise RuntimeError('device capture SHA pair mismatch')
    local = ROOT / 'n8d4.gs'
    subprocess.run(['/Users/brad/dev/ssx3/local/tooling/disk_budget.sh'], check=True)
    adb('pull', CAPTURE, str(local), timeout=600)
    subprocess.run(['/Users/brad/dev/ssx3/local/tooling/disk_budget.sh'], check=True)
    local_hashes = [local_hash(local) for _ in range(2)]
    if local.stat().st_size != size or hashes != local_hashes:
        raise RuntimeError('pulled capture SHA/size mismatch')
    receipt['capture'] = {'path': CAPTURE, 'bytes': size, 'sha_device': hashes,
                          'sha_local': local_hashes}
    event(f'CAPTURE bytes={size} sha={hashes[0]}')


def main():
    global lease_claimed, force_stopped, logger, log_file, launch_start
    ROOT.mkdir(parents=True, exist_ok=True)
    if (ROOT / 'result.json').exists() or (ROOT / 'n8d4.gs').exists():
        raise RuntimeError('N8D4 one-run receipt already exists')
    local_apk_hashes = [local_hash(APK) for _ in range(2)]
    receipt['hashes']['local_apk'] = local_apk_hashes
    if local_apk_hashes != [PINS['apk']] * 2:
        raise RuntimeError('local APK pin mismatch')
    with ZipFile(APK) as z:
        runner = z.read('lib/arm64-v8a/libps2EntryRunner.so')
    if any(marker not in runner for marker in (b'PS2X_GS_CAPTURE_STOP_TICK', b'PS2XGSC1',
                                               b'PS2X_N8D3_RAW_CAPTURE')):
        raise RuntimeError('APK runner lacks capture or raw-stage code')
    receipt['apk_capture_strings'] = True
    event('APK capture strings present; local SHA pair=' + local_apk_hashes[0])
    preflight()
    sh("echo 'N8D4 one-launch' > /data/local/tmp/mg/LEASE")
    lease_claimed = True
    event('LEASE claimed=' + sh('cat /data/local/tmp/mg/LEASE'))
    if sh('cat /data/local/tmp/mg/LEASE') != 'N8D4 one-launch':
        raise RuntimeError('lease claim did not persist')
    event('INSTALL ' + adb('install', '-r', str(APK), timeout=180).strip().replace('\n', ' | '))
    installed = sh(f'pm path {PKG}').removeprefix('package:')
    if not installed.endswith('/base.apk'):
        raise RuntimeError('installed base.apk path absent')
    receipt['installed_path'] = installed
    device_hash('installed_apk', installed, PINS['apk'])
    device_hash('elf', f'{FILES}/SLUS_207.72', PINS['elf'])
    device_hash('iso', f'{FILES}/SSX3.iso', PINS['iso'])
    mc0 = sh(f'ls -A {FILES}/mc0')
    event(f'CARD mc0 entries={mc0!r}')
    if mc0:
        raise RuntimeError('mc0 is not empty')
    sh(f'mkdir -p {DUMP}')
    if sh(f'ls -A {DUMP}'):
        raise RuntimeError('frame dump dir not empty')
    event('FRAME_DIR empty=' + DUMP)
    if sh(f'if test -e {CAPTURE}; then echo present; else echo absent; fi') != 'absent':
        raise RuntimeError('capture target already exists')
    space_and_capture_size()
    env = (f'PS2X_GS_BACKEND=parallel\nPS2X_GS_TURNIP=1\nPS2X_SKIP_MOVIE=1\n'
           f'PS2X_CD_IMAGE={FILES}/SSX3.iso\nPS2X_PAD_SCRIPT={ROUTE}\n'
           f'PS2X_PAD_SCRIPT_CLOCK=vsync\nPS2X_VSYNC_RATE_LOG=1\n'
           f'PS2X_FRAME_DUMP_DIR={DUMP}\nPS2X_FRAME_DUMP_ONCE_TICKS=2050,999999,999999\n'
           f'PS2X_N8D3_RAW_CAPTURE=1\n'
           f'PS2X_GS_CAPTURE={CAPTURE}\nPS2X_GS_CAPTURE_STOP_TICK=2050\n')
    (ROOT / 'ps2x.env').write_text(env)
    adb('push', str(ROOT / 'ps2x.env'), f'{FILES}/ps2x.env')
    event('ENV sha=' + sh(f'sha256sum {FILES}/ps2x.env').split()[0])
    preflight(allow_ours=True)
    adb('shell', f'am force-stop {PKG}')
    adb('logcat', '-c')
    log_file = (ROOT / 'logcat-all.txt').open('w')
    logger = subprocess.Popen(['adb', '-s', D, 'logcat', '-v', 'epoch', '-b', 'main', '-b', 'crash', '-s', 'ps2x', 'ps2x-hwcompat', 'raylib', 'DEBUG', 'libc', 'AndroidRuntime'], stdout=log_file, stderr=subprocess.STDOUT)
    start = time.monotonic()
    launch_start = start
    am = sh(f'am start -n {PKG}/android.app.NativeActivity')
    event('LAUNCH ' + am.replace('\n', ' | '))
    pid = ''
    for _ in range(20):
        pid = pidof()
        if pid:
            break
        time.sleep(0.5)
    if not pid:
        raise RuntimeError('launch PID absent')
    receipt['pid'] = pid
    event(f'PID {pid}')
    back_sent = False
    race_image = False
    last_tick = 0
    last_budget_check = -10
    while True:
        elapsed = time.monotonic() - start
        if elapsed - last_budget_check >= 5:
            space_and_capture_size()
            last_budget_check = elapsed
        text = same_pid_log(pid)
        ticks = re.findall(r'\[vsync-rate\] tick=(\d+)', text)
        tick = int(ticks[-1]) if ticks else 0
        receipt['latest_logged_guest_tick'] = tick
        if tick > last_tick:
            last_tick = tick
            event(f'PROGRESS t={elapsed:.1f} tick={tick}')
        fatal = [l for l in text.splitlines() if any(s in l for s in ('Turnip dlopen failed', 'Turnip HMI dlsym failed', 'Turnip dladdr(HMI) failed', 'Turnip HMI layout/open invalid', 'Turnip HAL open failed', 'Turnip HAL get-proc is null', '[gs:parallel] FATAL:', 'Fatal signal', 'FATAL EXCEPTION'))]
        if fatal:
            receipt['result'] = 'definitive loader/backend/crash failure'
            event('FIRST_FATAL ' + fatal[0])
            break
        if not pidof():
            receipt['result'] = 'process exited'
            event('STOP process gone')
            break
        if elapsed >= 6 and not back_sent:
            sh('input keyevent 4')
            back_sent = True
            event('BACK sent for USB dialog')
        race_dumps = [(int(seq), int(host_tick)) for seq, host_tick in re.findall(r'\[frame:dump\] seq=(\d+) tick=(\d+)', text) if int(host_tick) >= 2050]
        marker = re.search(r'\[gs:capture\] stopped at marker tick=(\d+) bytes=(\d+)', text)
        if marker and int(marker.group(1)) != 2050:
            raise RuntimeError('capture stopped at wrong marker')
        if race_dumps and marker and not race_image:
            seq, host_tick = race_dumps[0]
            receipt['trigger_dump'] = {'seq': seq, 'host_tick': host_tick}
            event(f'TRIGGER frame-dump seq={seq} host_tick={host_tick} latest_guest_tick={tick} t={elapsed:.1f}')
            race_image = True
            receipt['stop_marker'] = {'tick': int(marker.group(1)), 'bytes': int(marker.group(2))}
            receipt['result'] = 'race frontend and capture marker triggered'
            event(f'STOP frontend dump and capture marker at host_tick={host_tick}')
            break
        if tick >= 2100:
            receipt['result'] = 'tick 2100 without race dump'
            event('STOP tick>=2100 without race dump')
            break
        if elapsed >= 180 and tick < 1700:
            receipt['result'] = 'route progress cap'
            event(f'STOP route cap tick={tick}')
            break
        if elapsed >= 300:
            receipt['result'] = 'wall cap'
            event(f'STOP wall cap tick={tick}')
            break
        time.sleep(1)
    same_pid_log(pid)
    event('FINAL tick=' + str(last_tick))
    receipt['route_elapsed_seconds'] = round(time.monotonic() - start, 3)
    adb('shell', f'am force-stop {PKG}', timeout=30)
    force_stopped = True
    time.sleep(1)
    stopped_pid = pidof()
    event('POSTRUN pid-after=' + (stopped_pid or 'none'))
    if stopped_pid:
        raise RuntimeError('force-stop left launch PID present')
    if receipt['result'] != 'race frontend and capture marker triggered':
        raise RuntimeError(receipt['result'])
    pull_frame_pairs()
    pull_stage_files()
    pull_capture()


if sys.argv[1:] != ['--released-after-i27b']:
    raise SystemExit('N8D4 is prepared only; use --released-after-i27b after explicit orchestrator release')

try:
    main()
except Exception as exc:
    receipt['result'] = 'first failed step: ' + str(exc)
    event('ERROR ' + repr(exc))
finally:
    (ROOT / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')

if receipt['result'] != 'capture and race stages captured':
    raise SystemExit(1)
