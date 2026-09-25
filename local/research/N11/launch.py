#!/usr/bin/env python3
"""N11 Odin per-stage budget: N10 launcher adapted for the TL1 play build.

Differences from N10: OUT text logs stay in git, binaries (PNG/perf.data) go
to scratch; mc0-test empty card (Brad's mc0 never touched); full N11 env with
PS2X_SOUND=1 written per run, Brad's env (SHA 9fb46f85...) restored after;
gpubusy sampler every 5 s; --pin-cpu7 for S4; --probe-at-end for the S1
simpleperf/taskset viability probes; gated atexit (force-stop/restore/release
only what this run claimed/pushed/launched).

Usage: launch.py --label S1 [--wall 600] [--stop-tick 4500]
Preconditions (checked, not fixed): lease free or ours, keyguard
showing=false, AC powered + battery >= 20 %, app not running, device env is
Brad's (SHA 9fb46f85...), mc0 SHAs match I31 pins, mc0-test empty.
"""
import argparse, atexit, os, re, signal, subprocess, sys, time, hashlib, json

D = '622c49b1'
PKG = 'com.ps2x.runner'
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
DSCRAP = '/data/local/tmp/n11'
BRAD_ENV_SHA = '9fb46f8509adb1362b5ac74d35ac63a340e39228b64914848ce5ed85d6b74d13'
# I31 odin-verify.txt full SHAs (read-only intactness check, never written).
MC0_PINS = {
    'BASLUS-20772-GAM0001/BASLUS-20772-GAM0001': '4bdaee79a3bdaceef898bb44b6bcf62058e882a24237f8c81e46953a5067b78e',
    'BASLUS-20772-GAM0001/icon.sys': 'eab225745ef6695109743410261609e0569c14edb1555bc8941a965b3890a49c',
    'BASLUS-20772-GAM0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
    'BASLUS-20772-SET0001/BASLUS-20772-SET0001': '4a31a2d7e095e277edceae2243002055aa830019b3a1be64f126aee9129002f1',
    'BASLUS-20772-SET0001/icon.sys': 'dddf2d9c81a1c8bac2fe2036e1771dfa63635e3ae676760551defec2da67ee13',
    'BASLUS-20772-SET0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
}
ROUTE = (
    '10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000'
)

ap = argparse.ArgumentParser()
ap.add_argument('--label', required=True)
ap.add_argument('--wall', type=float, default=600.0)
ap.add_argument('--stop-tick', type=int, default=4500)
ap.add_argument('--profile-after-tick', type=int, default=0)
ap.add_argument('--profile-secs', type=int, default=30)
ap.add_argument('--scap-ticks', default='2100,3000,4000')
ap.add_argument('--scap-every', type=float, default=9999.0)
ap.add_argument('--min-battery', type=int, default=20)
ap.add_argument('--pin-cpu7', action='store_true')
ap.add_argument('--probe-at-end', action='store_true')
a = ap.parse_args()

OUT = os.path.expanduser(f'/Users/brad/dev/ssx3/local/research/N11/logs/{a.label}')
SCR = os.path.expanduser(f'/Users/brad/dev/ssx3-work/N11/{a.label}')
os.makedirs(OUT, exist_ok=True)
os.makedirs(SCR, exist_ok=True)
T0 = None
CLAIMED = {'v': False}
PUSHED = {'v': False}
LAUNCHED = {'v': False}


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


# --- preconditions (before claiming anything) ---
lease = sh('cat /data/local/tmp/mg/LEASE').strip()
kg = sh('dumpsys window policy | grep -m1 showing').strip()
bat = sh('dumpsys battery')
level = int(re.search(r'level: (\d+)', bat).group(1))
acm = re.search(r'AC powered: (\w+)', bat)
ac = acm.group(1) if acm else 'unknown'
pid0 = sh(f'pidof {PKG}').strip()
dev_env_sha = sh(f'sha256sum {FILES}/ps2x.env').split()[0]
sh(f'mkdir -p {FILES}/mc0-test')
mc0t = sh(f'ls -A {FILES}/mc0-test').strip()
mc0_bad = []
for f, want in MC0_PINS.items():
    have = sh(f'sha256sum {FILES}/mc0/{f}').split()[0]
    if have != want:
        mc0_bad.append(f)
log(f'PRE lease="{lease}" keyguard="{kg}" battery={level}% ac={ac} pid0={pid0 or "none"}')
log(f'PRE device-env={dev_env_sha} mc0-test={mc0t!r} mc0-bad={mc0_bad}')
if not (lease.startswith('LEASE_FREE') or lease.startswith('N11 ')):
    sys.exit('lease held by someone else')
if 'showing=false' not in kg:
    sys.exit('keyguard showing: ask Brad to unlock')
if level < a.min_battery or ac != 'true':
    sys.exit(f'battery {level}% ac={ac}: need >= {a.min_battery}% and AC powered (status ignored)')
if pid0:
    sys.exit(f'app already running (pid {pid0}): stop, do not disturb')
if dev_env_sha != BRAD_ENV_SHA:
    sys.exit(f'device env is NOT Brads: {dev_env_sha} (refusing to touch)')
if mc0_bad:
    sys.exit(f'Brad mc0 mismatch: {mc0_bad} (refusing to run)')
if mc0t:
    sys.exit(f'mc0-test not empty: {mc0t!r}')
sh(f'echo "N11 {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} {a.label}" > /data/local/tmp/mg/LEASE')
CLAIMED['v'] = True


def _cleanup():
    # Gated: only undo what this run did (never touch a session we didn't start).
    try:
        if PUSHED['v']:
            subprocess.run(['adb', '-s', D, 'push', f'{OUT}/ps2x.env.brad', f'{FILES}/ps2x.env'],
                           capture_output=True, timeout=60)
    except Exception:
        pass
    try:
        if LAUNCHED['v']:
            subprocess.run(['adb', '-s', D, 'shell', 'am', 'force-stop', PKG],
                           capture_output=True, timeout=30)
    except Exception:
        pass
    try:
        if CLAIMED['v']:
            subprocess.run(['adb', '-s', D, 'shell', "echo 'LEASE_FREE N11 done' > /data/local/tmp/mg/LEASE"],
                           capture_output=True, timeout=30)
    except Exception:
        pass


atexit.register(_cleanup)
signal.signal(signal.SIGTERM, lambda *_: sys.exit('SIGTERM'))

# Save Brad's env (SHA-verified above), then push our own complete env.
adb('pull', f'{FILES}/ps2x.env', f'{OUT}/ps2x.env.brad')
subprocess.run(['cp', f'{OUT}/ps2x.env.brad', f'{SCR}/ps2x.env.brad-device'], check=True)
env = [f'# N11 {a.label}', 'PS2X_GS_BACKEND=parallel', 'PS2X_GS_TURNIP=1',
       f'PS2X_CD_IMAGE={FILES}/SSX3.iso', 'PS2X_SKIP_MOVIE=1', 'PS2X_SOUND=1',
       f'PS2X_MC_ROOT={FILES}/mc0-test',
       f'PS2X_PAD_SCRIPT={ROUTE}', 'PS2X_PAD_SCRIPT_CLOCK=vsync', 'PS2X_VSYNC_RATE_LOG=1']
assert not any(x in e for e in env for x in ('PGS_', 'DUMP', 'TRACE', 'CAPTURE', 'ORACLE')), 'dump/trace key in env'
open(f'{OUT}/ps2x.env', 'w').write('\n'.join(env) + '\n')
sh(f'mkdir -p {DSCRAP}; rm -f {DSCRAP}/*.png {DSCRAP}/*.data')
adb('push', f'{OUT}/ps2x.env', f'{FILES}/ps2x.env', check=True)
PUSHED['v'] = True
log('ENV ' + sh(f'sha256sum {FILES}/ps2x.env').strip())
sh(f'am force-stop {PKG}')
adb('logcat', '-c')
lc = open(f'{OUT}/logcat.txt', 'w')
lcp = subprocess.Popen(['adb', '-s', D, 'logcat', '-v', 'epoch', '-b', 'main', '-b', 'crash',
                        '-s', 'ps2x', 'raylib', 'DEBUG', 'libc', 'AndroidRuntime'],
                       stdout=lc, stderr=subprocess.STDOUT)
T0 = time.time()


log('AM ' + sh(f'am start -n {PKG}/android.app.NativeActivity').strip().replace('\n', ' | '))
LAUNCHED['v'] = True
time.sleep(6)
sh('input keyevent 4')
log('BACK sent')
time.sleep(2)


def game_tid():
    # NB: `ps -T -o tid,...` prints nothing on this ROM (S1 thermal.txt);
    # top -H (S1 THREADS) is the proven thread lister.
    pid = sh(f'pidof {PKG}').strip()
    if not pid:
        return '', ''
    for line in sh(f'top -H -b -n1 -p {pid}').splitlines():
        if 'GameThread' in line:
            return line.split()[0], pid
    return '', pid


if a.pin_cpu7:
    ok = False
    for i in range(45):
        tid, pid = game_tid()
        if tid:
            before = sh(f'taskset -p {tid}').strip().replace('\n', ' ')
            r = subprocess.run(['adb', '-s', D, 'shell', f'taskset -p 80 {tid}'],
                               capture_output=True, text=True, timeout=30)
            after = sh(f'taskset -p {tid}').strip().replace('\n', ' ')
            log(f'PIN attempt={i} tid={tid} rc={r.returncode} out={r.stdout.strip()!r} err={r.stderr.strip()!r} before={before!r} after={after!r}')
            open(f'{OUT}/pin.txt', 'w').write(f'tid={tid} rc={r.returncode} out={r.stdout} err={r.stderr} before={before} after={after}\n')
            ok = (r.returncode == 0)
            break
        time.sleep(2)
    if not ok:
        log('PIN FAILED or GameThread never appeared (run continues unpinned; see pin.txt)')


def pick_layer():
    cands = []
    for l in sh('dumpsys SurfaceFlinger --list').splitlines():
        if PKG not in l or any(x in l for x in ('leash', 'InputSink', 'Background')):
            continue
        cands += re.findall(r'(com\.ps2x\.runner/android\.app\.NativeActivity#\d+)', l)
        m = re.search(r'name=(\S+ )?(com\.ps2\.runner/[^)]*)\)', l)
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
last_gpu = 0.0
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
        # NB: per-thread ps listing prints nothing on this ROM (S1); thread
        # split comes from the end-of-run top -H dump instead.
        therm = sh('echo "$(cat /sys/devices/system/cpu/cpu5/cpufreq/scaling_cur_freq) '
                   '$(cat /sys/devices/system/cpu/cpu7/cpufreq/scaling_cur_freq) '
                   '$(for z in /sys/class/thermal/thermal_zone*; do [ "$(cat $z/type)" = cpu-1-1-1 ] && cat $z/temp; done) '
                   '$(dumpsys thermalservice | grep -m1 "Thermal Status" | tr -dc 0-9)"').split()
        with open(f'{OUT}/thermal.txt', 'a') as f:
            f.write(f't={el:.1f} tick={tick} ' + ' '.join(therm) + '\n')
        with open(f'{OUT}/sf-latency.txt', 'a') as f:
            f.write(f'POLL t={el:.1f} tick={tick}\n')
            f.write(sh(f"dumpsys SurfaceFlinger --latency '{layer}'"))
    if el - last_gpu >= 5:
        last_gpu = el
        g = sh('cat /sys/class/kgsl/kgsl-3d0/gpubusy').split()
        try:
            # S1: the two counters are NOT monotonic across reads; each read
            # is a self-contained busy/total window, so the ratio is per-sample.
            busy, total = int(g[0]), int(g[1])
            pct = 100.0 * busy / total if total > 0 else -1.0
            with open(f'{OUT}/gpubusy.txt', 'a') as f:
                f.write(f't={el:.1f} tick={tick} busy={busy} total={total} pct={pct:.1f}\n')
        except (ValueError, IndexError):
            with open(f'{OUT}/gpubusy.txt', 'a') as f:
                f.write(f't={el:.1f} tick={tick} raw={" ".join(g)}\n')
    while scap_ticks and tick >= scap_ticks[0]:
        scap(f'tick{scap_ticks.pop(0)}')
        last_scap = el
    if el - last_scap >= a.scap_every:
        scap('periodic')
        last_scap = el
    if a.profile_after_tick and not profiled and tick >= a.profile_after_tick:
        profiled = True
        log(f'PROFILE start tick={tick}')
        out = sh(f'simpleperf record -g --app {PKG} -o {DSCRAP}/perf-{a.label}.data --duration {a.profile_secs}',
                 timeout=a.profile_secs + 120)
        open(f'{OUT}/simpleperf-record.txt', 'w').write(out)
        log(f'PROFILE end rc-logged tick~{tick}')
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

if a.probe_at_end and sh(f'pidof {PKG}').strip():
    log('PROBE simpleperf 5s start')
    r = subprocess.run(['adb', '-s', D, 'shell',
                        f'simpleperf record -g --app {PKG} -o {DSCRAP}/perf-probe.data --duration 5'],
                       capture_output=True, text=True, timeout=60)
    open(f'{OUT}/probe-simpleperf.txt', 'w').write(f'rc={r.returncode}\nOUT:\n{r.stdout}\nERR:\n{r.stderr}\n')
    log(f'PROBE simpleperf rc={r.returncode} err={r.stderr.strip()[:200]!r}')
    pid_p = sh(f'pidof {PKG}').strip()
    if pid_p:
        log('PROBE simpleperf -p 3s start')
        r0 = subprocess.run(['adb', '-s', D, 'shell',
                             f'simpleperf record -g -p {pid_p} -o {DSCRAP}/perf-probe-p.data --duration 3'],
                            capture_output=True, text=True, timeout=60)
        open(f'{OUT}/probe-simpleperf-p.txt', 'w').write(f'rc={r0.returncode}\nOUT:\n{r0.stdout}\nERR:\n{r0.stderr}\n')
        log(f'PROBE simpleperf -p rc={r0.returncode} err={r0.stderr.strip()[:200]!r}')
    tid, pid = game_tid()
    if tid:
        b = sh(f'taskset -p {tid}').strip().replace('\n', ' ')
        r2 = subprocess.run(['adb', '-s', D, 'shell', f'taskset -p 80 {tid}'],
                            capture_output=True, text=True, timeout=30)
        aft = sh(f'taskset -p {tid}').strip().replace('\n', ' ')
        open(f'{OUT}/probe-taskset.txt', 'w').write(
            f'tid={tid} rc={r2.returncode} out={r2.stdout} err={r2.stderr} before={b} after={aft}\n')
        log(f'PROBE taskset tid={tid} rc={r2.returncode} before={b!r} after={aft!r}')
    else:
        open(f'{OUT}/probe-taskset.txt', 'w').write('GameThread not found\n')
        log('PROBE taskset: GameThread not found')

sh(f'am force-stop {PKG}')
LAUNCHED['v'] = False
time.sleep(2)
lcp.terminate()
for name in sh(f'ls {DSCRAP}').split():
    if name.endswith('.png') or name.endswith('.data'):
        adb('pull', f'{DSCRAP}/{name}', f'{SCR}/{name}')
adb('push', f'{OUT}/ps2x.env.brad', f'{FILES}/ps2x.env', check=True)
PUSHED['v'] = False
rest = sh(f'sha256sum {FILES}/ps2x.env').split()[0]
log(f'RESTORE {rest} match={rest == BRAD_ENV_SHA}')
mc0_bad2 = [f for f, want in MC0_PINS.items()
            if sh(f'sha256sum {FILES}/mc0/{f}').split()[0] != want]
log(f'MC0-AFTER bad={mc0_bad2}')
with open(f'{OUT}/scap-sha.txt', 'w') as f:
    for name in sorted(os.listdir(SCR)):
        if name.endswith('.png') or name.endswith('.data'):
            h = hashlib.sha256(open(f'{SCR}/{name}', 'rb').read()).hexdigest()
            f.write(f'{h}  {name}\n')
log(f'END pid-after={sh(f"pidof {PKG}").strip() or "none"}')
sh("echo 'LEASE_FREE N11 done' > /data/local/tmp/mg/LEASE")
CLAIMED['v'] = False
