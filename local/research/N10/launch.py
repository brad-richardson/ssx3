#!/usr/bin/env python3
"""N10 Odin launch: N7 clean-speed method on the N9 fork-tip APK (GPU GS Turnip,
no dumps). I26-FAST vsync-clock route, PS2X_VSYNC_RATE_LOG=1,
SurfaceFlinger --latency polls, tick-triggered screencaps.

Usage: launch.py --label L1 [--wall 750]
Preconditions (checked, not fixed): lease free or ours, keyguard
showing=false, AC powered + battery >= 20 % (override --min-battery),
mc0 empty.
"""
import argparse, atexit, os, re, signal, subprocess, sys, time, hashlib, json

D = '622c49b1'
PKG = 'com.ps2x.runner'
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
DSCRAP = '/data/local/tmp/n10'
ROUTE = (
    '10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000'
)

ap = argparse.ArgumentParser()
ap.add_argument('--label', required=True)
ap.add_argument('--wall', type=float, default=750.0)
ap.add_argument('--stop-tick', type=int, default=4500)
ap.add_argument('--profile-after-tick', type=int, default=0)
ap.add_argument('--profile-secs', type=int, default=30)
ap.add_argument('--scap-ticks', default='2100,3000,4000')
ap.add_argument('--scap-every', type=float, default=9999.0)
ap.add_argument('--min-battery', type=int, default=20)
a = ap.parse_args()

OUT = os.path.expanduser(f'/Users/brad/dev/ssx3/local/research/N10/logs/{a.label}')
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
acm = re.search(r'AC powered: (\w+)', bat)
ac = acm.group(1) if acm else 'unknown'
mc0 = sh(f'ls -A {FILES}/mc0').strip()
log(f'PRE lease="{lease}" keyguard="{kg}" battery={level}% status={status} ac={ac} mc0={mc0!r}')
if not (lease.startswith('LEASE_FREE') or lease.startswith('N10 ')):
    sys.exit('lease held by someone else')
if 'showing=false' not in kg:
    sys.exit('keyguard showing: ask Brad to unlock')
if level < a.min_battery or ac != 'true':
    sys.exit(f'battery {level}% ac={ac}: need >= {a.min_battery}% and AC powered (status ignored)')
if mc0:
    sys.exit(f'mc0 not empty: {mc0!r}')
sh(f'echo "N10 {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} {a.label}" > /data/local/tmp/mg/LEASE')

# Rule (Brad, 09-23): force-stop right after EVERY run, including runs that
# die mid-script, so the charger can keep up.
def _force_stop():
    subprocess.run(['adb', '-s', D, 'shell', 'am', 'force-stop', PKG], capture_output=True, timeout=30)
    subprocess.run(['adb', '-s', D, 'shell', "echo 'LEASE_FREE N10 done' > /data/local/tmp/mg/LEASE"], capture_output=True, timeout=30)


atexit.register(_force_stop)
signal.signal(signal.SIGTERM, lambda *_: sys.exit('SIGTERM'))
# N9 live env minus PS2X_FRAME_DUMP_ONCE_TICKS (and the dump dir): parallel
# backend, bundled Turnip, movie bypass, I26-FAST vsync route, rate log.
env = [f'# N10 {a.label}', 'PS2X_GS_BACKEND=parallel', 'PS2X_GS_TURNIP=1',
       f'PS2X_CD_IMAGE={FILES}/SSX3.iso', 'PS2X_SKIP_MOVIE=1',
       f'PS2X_PAD_SCRIPT={ROUTE}', 'PS2X_PAD_SCRIPT_CLOCK=vsync', 'PS2X_VSYNC_RATE_LOG=1']
assert not any('PGS_' in e or 'DUMP' in e or 'TRACE' in e for e in env), 'dump/trace key in env'
adb('pull', f'{FILES}/ps2x.env', f'{OUT}/ps2x.env.orig')
open(f'{OUT}/ps2x.env', 'w').write('\n'.join(env) + '\n')
sh(f'mkdir -p {DSCRAP}; rm -f {DSCRAP}/*.png {DSCRAP}/*.data')
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

def pick_layer():
    # PF1: the app's own `com.ps2x.runner/android.app.NativeActivity#N` layer;
    # skip leash/InputSink/Background. This ROM wraps --list rows in
    # RequestedLayerState{Surface(name=<id> <name>)/@...}, so try both forms and
    # keep the first candidate whose --latency dump has frame rows.
    cands = []
    for l in sh('dumpsys SurfaceFlinger --list').splitlines():
        if PKG not in l or any(x in l for x in ('leash', 'InputSink', 'Background')):
            continue
        cands += re.findall(r'(com\.ps2x\.runner/android\.app\.NativeActivity#\d+)', l)
        m = re.search(r'name=(\S+ )?(com\.ps2x\.runner/[^)]*)\)', l)
        if m:
            cands.append(m.group(2))
        cands.append(l.strip())
    seen = []
    for c in cands:
        if c in seen:
            continue
        seen.append(c)
        rows = [r for r in sh(f"dumpsys SurfaceFlinger --latency '{c}'").splitlines() if '\t' in r]
        if len(rows) > 2:
            return c, seen
    return '', seen


layer, tried = pick_layer()
log(f'LAYER {layer!r} tried={tried}')
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
        if not layer:
            layer, tried = pick_layer()
            log(f'LAYER retry {layer!r} tried={tried}')
        therm = sh('echo "$(cat /sys/devices/system/cpu/cpu5/cpufreq/scaling_cur_freq) '
                   '$(cat /sys/devices/system/cpu/cpu7/cpufreq/scaling_cur_freq) '
                   '$(for z in /sys/class/thermal/thermal_zone*; do [ "$(cat $z/type)" = cpu-1-1-1 ] && cat $z/temp; done) '
                   '$(dumpsys thermalservice | grep -m1 "Thermal Status" | tr -dc 0-9)"; '
                   f'ps -T -p {pid} -o tid,psr,pcpu,name | grep GameThread').split()
        with open(f'{OUT}/thermal.txt', 'a') as f:
            f.write(f't={el:.1f} tick={tick} ' + ' '.join(therm) + '\n')
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
    if el >= 180 and tick < 570:
        log('STOP title not reached by 180s')
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
    if name.endswith('.png'):
        adb('pull', f'{DSCRAP}/{name}', f'{OUT}/{name}')
# Restore the device's original ps2x.env (saved before push).
adb('push', f'{OUT}/ps2x.env.orig', f'{FILES}/ps2x.env', check=True)
log('RESTORE ' + sh(f'sha256sum {FILES}/ps2x.env').strip())
with open(f'{OUT}/scap-sha.txt', 'w') as f:
    for name in sorted(os.listdir(OUT)):
        if name.endswith('.png'):
            f.write(f'{hashlib.sha256(open(f"{OUT}/{name}", "rb").read()).hexdigest()}  {name}\n')
log(f'END pid-after={sh(f"pidof {PKG}").strip() or "none"}')
