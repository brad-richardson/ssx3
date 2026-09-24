#!/usr/bin/env python3
"""N9 Part 2 one-install/one-launch live race on fork-tip APK; device writes use its lease.

Adapted from N8D2/launch.py: same I26-FAST vsync pad route and dump ticks, no
PS2X_PGS_* env anywhere, menu screencap at guest tick>=1000 plus race screencap
at host dump tick>=2050, original device ps2x.env saved before push and
restored after force-stop. Battery gate per standing rule (Brad): AC powered and level>=20, status ignored. One launch; any fatal loader/backend line,
black-screen verdict excluded (human reads the PNGs), or missing capture fails.
"""
import atexit
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

D = '622c49b1'
PKG = 'com.ps2x.runner'
ROOT = Path('/Users/brad/dev/ssx3-work/N9/run')
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
DUMP = f'{FILES}/n9-frames'
APK = Path('/Users/brad/dev/ssx3-work/N9/app-release.apk')
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000')
PINS = {
    'apk': '25711bfe1fedec6c4f60cf554b6401df1ca523bc06a82a5c736b2c9cebc08152',
    'elf': '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
    'iso': '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
}
receipt = {'hashes': {}, 'images': [], 'screencaps': [], 'events': [], 'result': 'not found'}
lease_claimed = False
force_stopped = False
env_restored = False
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


def restore_env():
    global env_restored
    orig = ROOT / 'ps2x.env.orig'
    if not orig.exists():
        event('RESTORE no saved original; skipping')
        return
    want = hashlib.sha256(orig.read_bytes()).hexdigest()
    adb('push', str(orig), f'{FILES}/ps2x.env')
    got = [sh(f'sha256sum {FILES}/ps2x.env').split()[0] for _ in range(2)]
    event(f'RESTORE ps2x.env want={want} got={got[0]} {got[1]}')
    if got != [want, want]:
        raise RuntimeError('ps2x.env restore SHA mismatch')
    receipt['env_restored_sha'] = want
    env_restored = True


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
        if not env_restored:
            try:
                restore_env()
            except Exception as e:
                event('CLEANUP restore error=' + repr(e))
        try:
            adb('shell', "echo 'LEASE_FREE N9 done' > /data/local/tmp/mg/LEASE", timeout=30)
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
    ac = re.search(r'AC powered: (\w+)', battery)
    ac_powered = ac.group(1) if ac else 'unknown'
    showing = re.search(r'KeyguardServiceDelegate\s+showing=(\w+)', policy)
    if not showing:
        showing = re.search(r'KeyguardServiceDelegate.*?showing=(\w+)', policy, re.S)
    event(f'PREFLIGHT device={state} lease={lease!r} keyguard={showing.group(1) if showing else "unknown"} battery={level}% status={status} ac={ac_powered}')
    free_or_ours = lease.startswith('LEASE_FREE') or (allow_ours and lease == 'N9 one-launch')
    if state != 'device' or not free_or_ours or not showing or showing.group(1) != 'false' or ac_powered != 'true' or level < 20:
        raise RuntimeError('preflight gate failed (need device + lease + unlocked + AC + >=20%)')


def device_hash(label, path, pin):
    reads = [sh(f'sha256sum {path}', timeout=240).split()[0] for _ in range(2)]
    receipt['hashes'][label] = reads
    event(f'HASH {label} {reads[0]} {reads[1]}')
    if reads != [pin, pin]:
        raise RuntimeError(f'{label} SHA mismatch')


def capture(label, tick):
    remote = f'/data/local/tmp/n9-{label}.png'
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
    data = (ROOT / 'logcat-all.txt').read_text(errors='replace') if (ROOT / 'logcat-all.txt').exists() else ''
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


def main():
    global lease_claimed, force_stopped, logger, log_file, launch_start
    ROOT.mkdir(parents=True, exist_ok=True)
    if PINS['apk'] == 'N9_APK_PIN_TBD' or len(PINS['apk']) != 64:
        raise RuntimeError('APK pin not set')
    if 'PGS_' in (ROOT / 'ps2x.env').read_text() if (ROOT / 'ps2x.env').exists() else False:
        raise RuntimeError('stale ps2x.env contains PS2X_PGS_*')
    preflight()
    sh("echo 'N9 one-launch' > /data/local/tmp/mg/LEASE")
    lease_claimed = True
    event('LEASE claimed=' + sh('cat /data/local/tmp/mg/LEASE'))
    if sh('cat /data/local/tmp/mg/LEASE') != 'N9 one-launch':
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
    adb('pull', f'{FILES}/ps2x.env', str(ROOT / 'ps2x.env.orig'), timeout=60)
    orig_sha = hashlib.sha256((ROOT / 'ps2x.env.orig').read_bytes()).hexdigest()
    event(f'ENV_ORIG sha={orig_sha}')
    env = (f'PS2X_GS_BACKEND=parallel\nPS2X_GS_TURNIP=1\nPS2X_SKIP_MOVIE=1\n'
           f'PS2X_CD_IMAGE={FILES}/SSX3.iso\nPS2X_PAD_SCRIPT={ROUTE}\n'
           f'PS2X_PAD_SCRIPT_CLOCK=vsync\nPS2X_VSYNC_RATE_LOG=1\n'
           f'PS2X_FRAME_DUMP_DIR={DUMP}\nPS2X_FRAME_DUMP_ONCE_TICKS=1840,1950,2050\n')
    assert 'PGS_' not in env
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
    menu_image = False
    race_image = False
    last_tick = 0
    while True:
        elapsed = time.monotonic() - start
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
        if tick >= 1000 and elapsed >= 20 and not menu_image:
            event(f'TRIGGER menu at guest_tick={tick} t={elapsed:.1f}')
            capture('menu', tick)
            menu_image = True
        race_dumps = [(int(seq), int(host_tick)) for seq, host_tick in re.findall(r'\[frame:dump\] seq=(\d+) tick=(\d+)', text) if int(host_tick) >= 2050]
        if race_dumps and not race_image:
            seq, host_tick = race_dumps[0]
            receipt['trigger_dump'] = {'seq': seq, 'host_tick': host_tick}
            event(f'TRIGGER frame-dump seq={seq} host_tick={host_tick} latest_guest_tick={tick} t={elapsed:.1f}')
            capture('race', host_tick)
            race_image = True
            if menu_image:
                receipt['result'] = 'menu and race captured'
                event(f'STOP both screens captured after race dump host_tick={host_tick}')
                break
            receipt['result'] = 'race captured without menu'
            event('STOP race captured but menu missing')
            break
        if tick >= 2100:
            receipt['result'] = 'tick 2100 without race dump'
            event('STOP tick>=2100 without race dump')
            break
        if elapsed >= 180:
            receipt['result'] = 'route progress cap'
            event(f'STOP route cap tick={tick}')
            break
        if elapsed >= 240:
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
    pull_frame_pairs()
    restore_env()


try:
    main()
except Exception as exc:
    receipt['result'] = 'first failed step: ' + str(exc)
    event('ERROR ' + repr(exc))
finally:
    (ROOT / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')

if receipt['result'] != 'menu and race captured':
    raise SystemExit(1)
