#!/usr/bin/env python3
"""N5 Odin launch: E33 vsync-clock route, PS2X_VSYNC_RATE_LOG=1, optional
frame dumps, SurfaceFlinger --latency polls, tick-triggered screencaps,
optional simpleperf after the race window.

Usage: launch.py --label L1 [--dumps] [--profile-after-tick N] [--wall 600]
Preconditions (checked, not fixed): lease free or ours, keyguard
showing=false, battery >= 20 % and charging (override --min-battery).
"""
import argparse, os, re, subprocess, sys, time, hashlib, json

D = '622c49b1'
PKG = 'com.ps2x.runner'
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
DSCRAP = '/data/local/tmp/n5'
ROUTE = ('10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,'
         '30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,'
         '64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,'
         '113340:down:20000')

ap = argparse.ArgumentParser()
ap.add_argument('--label', required=True)
ap.add_argument('--dumps', action='store_true')
ap.add_argument('--wall', type=float, default=600.0)
ap.add_argument('--stop-tick', type=int, default=11100)
ap.add_argument('--profile-after-tick', type=int, default=0)
ap.add_argument('--profile-secs', type=int, default=30)
ap.add_argument('--scap-ticks', default='1300,1800,2600,7500,9000,10800')
ap.add_argument('--scap-every', type=float, default=30.0)
ap.add_argument('--min-battery', type=int, default=20)
a = ap.parse_args()

OUT = os.path.expanduser(f'~/dev/ssx3-work/N5/{a.label}')
os.makedirs(OUT, exist_ok=True)
T0 = None


def adb(*args, check=False, timeout=60):
    r = subprocess.run(['adb', '-s', D, *args], capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise SystemExit(f'adb {args} failed: {r.stderr}')
    return r.stdout


def sh(cmd, timeout=60):
    return adb('shell', cmd, timeout=timeout)


def log(msg):
    t = '' if T0 is None else f' t+{time.time() - T0:7.1f}'
    line = f'[{time.strftime("%H:%M:%S")}{t}] {msg}'
    print(line, flush=True)
    with open(f'{OUT}/driver.log', 'a') as f:
        f.write(line + '\n')


# --- preconditions ---
lease = sh('cat /data/local/tmp/mg/LEASE').strip()
kg = sh('dumpsys window policy | grep -m1 showing').strip()
bat = sh('dumpsys battery')
level = int(re.search(r'level: (\d+)', bat).group(1))
status = int(re.search(r'status: (\d+)', bat).group(1))
log(f'PRE lease="{lease}" keyguard="{kg}" battery={level}% status={status}')
if not (lease.startswith('LEASE_FREE') or lease.startswith('N5 ')):
    sys.exit('lease held by someone else')
if 'showing=false' not in kg:
    sys.exit('keyguard showing: ask Brad to unlock')
if level < a.min_battery or status != 2:
    sys.exit(f'battery {level}% status {status}: need >= {a.min_battery}% and charging (2)')
sh(f'echo "N5 {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} {a.label}" > /data/local/tmp/mg/LEASE')

env = [f'# N5 {a.label}', f'PS2X_CD_IMAGE={FILES}/SSX3.iso', 'PS2X_SKIP_MOVIE=1',
       f'PS2X_PAD_SCRIPT={ROUTE}', 'PS2X_PAD_SCRIPT_CLOCK=vsync', 'PS2X_VSYNC_RATE_LOG=1']
if a.dumps:
    env.append(f'PS2X_FRAME_DUMP_DIR={FILES}/frames')
open(f'{OUT}/ps2x.env', 'w').write('\n'.join(env) + '\n')
sh(f'mkdir -p {DSCRAP}; rm -f {DSCRAP}/*.png {DSCRAP}/*.data; rm -rf {FILES}/frames; mkdir -p {FILES}/frames')
adb('push', f'{OUT}/ps2x.env', f'{FILES}/ps2x.env', check=True)
log('ENV ' + sh(f'sha256sum {FILES}/ps2x.env').strip())
sh(f'am force-stop {PKG}')
adb('logcat', '-c')
lc = open(f'{OUT}/logcat.txt', 'w')
lcp = subprocess.Popen(['adb', '-s', D, 'logcat', '-v', 'epoch', '-b', 'main', '-b', 'crash',
                        '-s', 'ps2x', 'raylib', 'DEBUG', 'libc', 'AndroidRuntime'],
                       stdout=lc, stderr=subprocess.STDOUT)
T0 = time.time()
log('AM ' + sh(f'am start -n {PKG}/android.app.NativeActivity').strip().replace('\n', ' | '))
time.sleep(6)
sh('input keyevent 4')
log('BACK sent')
time.sleep(2)
layer = ''
for l in sh('dumpsys SurfaceFlinger --list').splitlines():
    if PKG in l and 'NativeActivity' in l and 'Background' not in l:
        layer = l.strip()
log(f'LAYER {layer!r}')
json.dump({'T0': T0, 'layer': layer, 'env': env}, open(f'{OUT}/meta.json', 'w'), indent=1)

rate_re = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)')
scap_ticks = [int(x) for x in a.scap_ticks.split(',') if x]
n_scap = 0
last_scap = 0.0
last_lat = 0.0
profiled = False
tick = 0


def scap(tag):
    global n_scap
    n_scap += 1
    name = f'sc{n_scap:02d}-{tag}-t{int(time.time() - T0)}.png'
    sh(f'screencap -p {DSCRAP}/{name}')
    log(f'SCAP {name} tick~{tick}')


while True:
    el = time.time() - T0
    try:
        txt = open(f'{OUT}/logcat.txt', errors='replace').read()
    except OSError:
        txt = ''
    m = rate_re.findall(txt)
    if m:
        tick = int(m[-1][0])
    if 'FATAL' in txt or 'Fatal signal' in txt:
        log('FATAL seen in logcat')
        break
    pid = sh(f'pidof {PKG}').strip()
    if not pid:
        log('process gone')
        break
    if el - last_lat >= 10:
        last_lat = el
        with open(f'{OUT}/sf-latency.txt', 'a') as f:
            f.write(f'POLL t={el:.1f} tick={tick}\n')
            f.write(sh(f"dumpsys SurfaceFlinger --latency '{layer}'"))
    while scap_ticks and tick >= scap_ticks[0]:
        scap(f'tick{scap_ticks.pop(0)}')
        last_scap = el
    if el - last_scap >= a.scap_every:
        scap('periodic')
        last_scap = el
    if a.profile_after_tick and not profiled and tick >= a.profile_after_tick:
        profiled = True
        log(f'PROFILE start tick={tick}')
        out = sh(f'simpleperf record -g --app {PKG} -o {DSCRAP}/perf-race.data --duration {a.profile_secs}',
                 timeout=a.profile_secs + 120)
        open(f'{OUT}/simpleperf-record.txt', 'w').write(out)
        log(f'PROFILE end tick~{tick}')
        scap('postprofile')
        break
    if tick >= a.stop_tick and not a.profile_after_tick:
        log(f'STOP tick {tick} >= {a.stop_tick}')
        break
    if el >= a.wall:
        log(f'STOP wall cap {a.wall}s tick={tick}')
        break
    time.sleep(2)

scap('final')
time.sleep(1)
log('THREADS\n' + sh(f'top -H -b -n1 -p $(pidof {PKG}) | head -20'))
log('BATTERY ' + ' '.join(l.strip() for l in sh('dumpsys battery').splitlines() if 'level' in l or 'status' in l))
sh(f'am force-stop {PKG}')
time.sleep(2)
lcp.terminate()
for name in sh(f'ls {DSCRAP}').split():
    adb('pull', f'{DSCRAP}/{name}', f'{OUT}/{name}')
if a.dumps:
    adb('pull', f'{FILES}/frames/upload-latest.txt', f'{OUT}/upload-latest.txt')
with open(f'{OUT}/scap-sha.txt', 'w') as f:
    for name in sorted(os.listdir(OUT)):
        if name.endswith('.png'):
            f.write(f'{hashlib.sha256(open(f"{OUT}/{name}", "rb").read()).hexdigest()}  {name}\n')
log(f'END pid-after={sh(f"pidof {PKG}").strip() or "none"}')
