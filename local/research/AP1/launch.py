#!/usr/bin/env python3
"""AP1 Odin launcher: F7's launch.py (F5 lineage: mc0 pins, transport record,
screenshots-only so no cool-down; lease/dirs repointed at AP1, play-env pin
read from odin-play/SHA256SUMS). Play knobs (MTVU + LAG + blocks + pins) go
in via --env. Screenshots-only runs: variant A (1x pipelined, Vulkan present
default on) plus play knobs via --env; --vk 0 for the GL fallback,
--aspect 4:3 for the pillarbox check, --pad-probe for PS2X_VIRTUAL_PAD=1,
--swipe-tick T for the transient-bars swipe check.
  --variant A|B|VA|VB  A = 1x pipelined, B = 4x+hi-res pipelined (F5's legs);
                       VA/VB = the same + PS2X_PRESENT_VULKAN=1 (unused in AP1: default on)
  --env K=V            extra ps2x.env line (repeatable; used for every AP1 knob)
  --apk PATH --apk-sha SHA  install this APK first (two local SHA reads + base.apk SHA)
  --cpu-window S,E     per-thread CPU (/proc/<pid>/task/*/stat utime+stime) between
                       guest ticks S and E, unprofiled -> threadcpu.txt
  --compare-ticks T,.. VK pixel compare (diagnostic run: sync present + readback at T)
  --lifecycle TICK     at TICK: HOME, 8 s, screencap + layers; relaunch to foreground,
                       screencap; rotation lock 3 then restore the saved setting
Profiler command is N11's `simpleperf record -g --app`.
"""
import argparse, atexit, os, re, signal, subprocess, sys, time, hashlib, json

D = open(os.path.expanduser('~/dev/ssx3/local/odin-serial')).read().strip()  # USB 622c49b1 or Wi-Fi ip:5555
PKG = 'com.ps2x.runner'
FILES = f'/storage/emulated/0/Android/data/{PKG}/files'
DSCRAP = '/data/local/tmp/ap1'
LEASESH = os.path.expanduser('~/dev/ssx3/local/tooling/odin_lease.sh')
# Play-env pin comes from the canonical SHA256SUMS (never hard-coded: a play-env
# change must not break the driver's pre/post checks). Same file the restore
# script reads.
def _brad_env_sha():
    for line in open(os.path.expanduser('~/dev/ssx3-work/odin-play/SHA256SUMS')):
        h, _, name = line.partition('  ')
        if name.strip() == 'ps2x.env' and len(h.strip()) == 64:
            return h.strip()
    sys.exit('bad SHA256SUMS in odin-play')
BRAD_ENV_SHA = _brad_env_sha()
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
ap.add_argument('--game-cpus', default='',
                help='Part 2: PS2X_GAME_THREAD_CPUS value, e.g. 6,7 (empty = unset)')
ap.add_argument('--variant', choices=('A', 'B', 'VA', 'VB'), required=True)
ap.add_argument('--apk', default='')
ap.add_argument('--apk-sha', default='')
ap.add_argument('--cpu-window', default='')
ap.add_argument('--compare-ticks', default='')
ap.add_argument('--lifecycle', type=int, default=0)
ap.add_argument('--sf-dump-tick', default='',
                help='Part 2B: tick(s) "a,b,c" at which to save the HWC layer table (composition type per layer)')
ap.add_argument('--aspect', choices=('', '4:3', '16:9', 'native'), default='',
                help='Part 2B: PS2X_ASPECT (presenter aspect; empty = default anamorphic 16:9)')
ap.add_argument('--fc', type=int, default=0, help='Part 2A: PS2X_PGS_FRAME_CONTEXTS (0 = unset = 4)')
ap.add_argument('--vk', choices=('', '0', '1'), default='',
                help='Part 2B: PS2X_PRESENT_VULKAN value to write (empty = variant default)')
ap.add_argument('--pad-probe', action='store_true',
                help='PS2X_VIRTUAL_PAD=1 (for its [vpad] pad_in_use log) + an injected gamepad long-press at the end')
ap.add_argument('--swipe-tick', type=int, default=0,
                help='AP1: at this guest tick, swipe up from the bottom edge (transient bars), screencap, wait 3 s, screencap + focus check')
ap.add_argument('--env', action='append', default=[],
                help='extra ps2x.env line K=V (repeatable)')
a = ap.parse_args()

OUT = os.path.expanduser(f'/Users/brad/dev/ssx3/local/research/AP1/logs/{a.label}')
SCR = os.path.expanduser(f'/Users/brad/dev/ssx3-work/AP1/odin/{a.label}')
os.makedirs(OUT, exist_ok=True)
os.makedirs(SCR, exist_ok=True)
T0 = None
CLAIMED = {'v': False}
PUSHED = {'v': False}
LAUNCHED = {'v': False}


DISCONNECTS = {'n': 0}


def adb(*args, check=False, timeout=60):
    # F5: count transport failures (Wi-Fi); a dead transport mid-run voids the run.
    try:
        r = subprocess.run(['adb', '-s', D, *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        DISCONNECTS['n'] += 1
        with open(f'{OUT}/disconnects.txt', 'a') as f:
            f.write(f't={time.time() - (T0 or time.time()):.1f} TIMEOUT adb {args}\n')
        if check:
            raise SystemExit(f'adb {args} timed out')
        return ''
    if r.returncode != 0 and ('device' in r.stderr and ("not found" in r.stderr or 'offline' in r.stderr)):
        DISCONNECTS['n'] += 1
        with open(f'{OUT}/disconnects.txt', 'a') as f:
            f.write(f't={time.time() - (T0 or time.time()):.1f} TRANSPORT adb {args}: {r.stderr.strip()[:160]}\n')
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
if not (lease.startswith('LEASE_FREE') or lease.startswith('AP1 ')):
    sys.exit(f'lease held by someone else: {lease}')
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
if lease.startswith('AP1 '):
    CLAIMED['v'] = True  # outer hold (or a stale AP1 lease); we own it
else:
    r = subprocess.run(['bash', LEASESH, 'claim', 'AP1'], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        sys.exit(f'atomic claim failed: {r.stdout.strip()} {r.stderr.strip()}')
    CLAIMED['v'] = True
    log(f'LEASE claimed via odin_lease.sh: {r.stdout.strip()}')


def lease_release():
    subprocess.run(['bash', LEASESH, 'release', 'AP1'], capture_output=True, timeout=60)


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
            subprocess.run(['bash', LEASESH, 'release', 'AP1'],
                           capture_output=True, timeout=60)
    except Exception:
        pass


atexit.register(_cleanup)
signal.signal(signal.SIGTERM, lambda *_: sys.exit('SIGTERM'))

# Save Brad's env (SHA-verified above), then push our own complete env.
adb('pull', f'{FILES}/ps2x.env', f'{OUT}/ps2x.env.brad')
subprocess.run(['cp', f'{OUT}/ps2x.env.brad', f'{SCR}/ps2x.env.brad-device'], check=True)
if a.apk:
    h1 = hashlib.sha256(open(a.apk, 'rb').read()).hexdigest()
    h2 = hashlib.sha256(open(a.apk, 'rb').read()).hexdigest()
    log(f'APK local sha x2 {h1} {h2}')
    if h1 != h2 or (a.apk_sha and h1 != a.apk_sha):
        sys.exit(f'APK SHA mismatch: {h1} {h2} want {a.apk_sha}')
    log('INSTALL ' + adb('install', '-r', a.apk, timeout=600).strip().replace('\n', ' '))
    bp = sh(f'pm path {PKG}').strip().split(':', 1)[-1]
    bsha = sh(f'sha256sum {bp}').split()[0]
    log(f'INSTALLED {bp} sha={bsha} match={bsha == h1}')
    if bsha != h1:
        sys.exit('installed base.apk does not match')
env = [f'# AP1 {a.label} variant {a.variant}', 'PS2X_GS_BACKEND=parallel', 'PS2X_GS_TURNIP=1',
       f'PS2X_CD_IMAGE={FILES}/SSX3.iso', 'PS2X_SKIP_MOVIE=1', 'PS2X_SOUND=1',
       f'PS2X_MC_ROOT={FILES}/mc0-test',
       f'PS2X_PAD_SCRIPT={ROUTE}', 'PS2X_PAD_SCRIPT_CLOCK=vsync', 'PS2X_VSYNC_RATE_LOG=1',
       'PS2X_UNPACED=1']  # FP1: speed runs measure unpaced headroom
if a.variant in ('A', 'VA'):
    env.append('PS2X_PGS_PRESENT_PIPELINE=1')
else:
    env.extend(['PS2X_PGS_SSAA=4', 'PS2X_PGS_HIRES_SCANOUT=1', 'PS2X_PGS_PRESENT_PIPELINE=1'])
if a.vk:
    env.append(f'PS2X_PRESENT_VULKAN={a.vk}')
elif a.variant.startswith('V'):
    env.append('PS2X_PRESENT_VULKAN=1')
if a.fc:
    env.append(f'PS2X_PGS_FRAME_CONTEXTS={a.fc}')
if a.aspect:
    env.append(f'PS2X_ASPECT={a.aspect}')
DDUMP = f'{FILES}/ap1dump'
if a.pad_probe:
    env.append('PS2X_VIRTUAL_PAD=1')
if a.compare_ticks:
    env.append(f'PS2X_PRESENT_VK_COMPARE_TICKS={a.compare_ticks}')
    env.append(f'PS2X_PRESENT_VK_DUMP_DIR={DDUMP}')
if a.game_cpus:
    env.append(f'PS2X_GAME_THREAD_CPUS={a.game_cpus}')
for e in (a.env or []):
    if '=' not in e:
        sys.exit(f'bad --env (want K=V): {e!r}')
    env.append(e)
assert a.compare_ticks or not any(x in e for e in env for x in ('DUMP', 'TRACE', 'CAPTURE', 'ORACLE')), \
    'dump/trace key in env'
assert all(not e.startswith('PS2X_PGS') or e.split('=')[0] in
           ('PS2X_PGS_PRESENT_PIPELINE', 'PS2X_PGS_SSAA', 'PS2X_PGS_HIRES_SCANOUT', 'PS2X_PGS_FRAME_CONTEXTS')
           for e in env), \
    'unexpected PGS key in env'
open(f'{OUT}/ps2x.env', 'w').write('\n'.join(env) + '\n')
sh(f'mkdir -p {DSCRAP}; rm -f {DSCRAP}/*.png {DSCRAP}/*.data {DSCRAP}/*.ppm; rm -rf {DDUMP}; mkdir -p {DDUMP}')
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
# F5: no blind BACK over Wi-Fi (no USB dialog exists to absorb it). Send BACK
# only when a foreign window covers the app, and confirm focus after.
focus = sh('dumpsys window | grep -m1 mCurrentFocus').strip()
if PKG not in focus:
    sh('input keyevent 4')
    time.sleep(2)
    focus2 = sh('dumpsys window | grep -m1 mCurrentFocus').strip()
    log(f'BACK sent (was covered: {focus[:100]!r} now: {focus2[:100]!r})')
else:
    log(f'FOCUS app-foreground, no BACK ({focus[:100]!r})')
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
transport = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True,
                           timeout=30).stdout
open(f'{OUT}/transport-start.txt', 'w').write(f'serial={D}\n{transport}')
json.dump({'T0': T0, 'layer': layer, 'env': env, 'variant': a.variant, 'serial': D},
          open(f'{OUT}/meta.json', 'w'), indent=1)

rate_re = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)')
cpu_win = [int(x) for x in a.cpu_window.split(',')] if a.cpu_window else []
cpu_snap = {}
lifecycle_done = False
swipe_done = False
sf_ticks = [int(x) for x in a.sf_dump_tick.split(',') if x]


def task_cpu(pid):
    # tid -> (comm, utime+stime clock ticks); CLK_TCK = 100 on this ROM.
    out = sh(f'for t in /proc/{pid}/task/*; do cat $t/stat; echo; done', timeout=60)
    res = {}
    for line in out.splitlines():
        if ')' not in line:
            continue
        head, rest = line.split(')', 1)
        tid, comm = head.split('(', 1)
        f = rest.split()
        res[tid.strip()] = (comm, int(f[11]) + int(f[12]))
    return res


def write_cpu():
    (w0, k0, c0), (w1, k1, c1) = cpu_snap['start'], cpu_snap['end']
    frames = max(1, k1 - k0)
    wall = w1 - w0
    rows = []
    for tid, (comm, t1) in c1.items():
        t0 = c0.get(tid, (comm, 0))[1]
        rows.append((t1 - t0, tid, comm))
    rows.sort(reverse=True)
    with open(f'{OUT}/threadcpu.txt', 'w') as f:
        f.write(f'window ticks {k0}->{k1} ({frames} frames) wall {wall:.2f} s '
                f'= {1000 * wall / frames:.2f} ms/frame, {frames / wall:.2f} vs/s\n')
        f.write('tid comm cpu_s cpu_ms_per_frame util_pct\n')
        for d, tid, comm in rows:
            if d <= 0:
                continue
            f.write(f'{tid} {comm} {d / 100:.2f} {10 * d / frames:.2f} {100 * (d / 100) / wall:.1f}\n')


def run_lifecycle():
    log('LIFECYCLE start: HOME')
    layers0 = [l for l in sh('dumpsys SurfaceFlinger --list').splitlines() if 'ps2x' in l.lower() or PKG in l]
    log(f'LAYERS before {layers0}')
    sh('input keyevent 3')
    time.sleep(8)
    scap('bg')
    log(f'BG focus={sh("dumpsys window | grep -m1 mCurrentFocus").strip()[:120]!r} pid={sh(f"pidof {PKG}").strip()}')
    log('FG ' + sh(f'am start -n {PKG}/android.app.NativeActivity').strip().replace('\n', ' | '))
    time.sleep(8)
    scap('fg')
    layers1 = [l for l in sh('dumpsys SurfaceFlinger --list').splitlines() if 'ps2x' in l.lower() or PKG in l]
    log(f'LAYERS after-fg {layers1} focus={sh("dumpsys window | grep -m1 mCurrentFocus").strip()[:120]!r}')
    rot0 = sh('cmd window user-rotation').strip()
    log(f'ROTATION saved {rot0!r}')
    sh('cmd window user-rotation lock 3')
    time.sleep(6)
    scap('rot3')
    log(f'ROTATION lock3 display={sh("dumpsys window displays | grep -m2 -E \'mCurrentRotation|cur=\'").strip()[:200]!r}')
    m = re.search(r'(free|lock)\w*\D*(\d)?', rot0)
    if rot0.startswith('free'):
        sh('cmd window user-rotation free')
    elif m and m.group(2):
        sh(f'cmd window user-rotation lock {m.group(2)}')
    else:
        sh('cmd window user-rotation free')
    time.sleep(4)
    log(f'ROTATION restored -> {sh("cmd window user-rotation").strip()!r}')
    scap('rot-restored')

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
        # split comes from the end-of-run top -H dump instead. Part 2 adds
        # cpu6 clock + GameThread's current cpu (/proc stat field 39).
        therm = sh('echo "$(cat /sys/devices/system/cpu/cpu5/cpufreq/scaling_cur_freq) '
                   '$(cat /sys/devices/system/cpu/cpu6/cpufreq/scaling_cur_freq) '
                   '$(cat /sys/devices/system/cpu/cpu7/cpufreq/scaling_cur_freq) '
                   '$(for z in /sys/class/thermal/thermal_zone*; do [ "$(cat $z/type)" = cpu-1-1-1 ] && cat $z/temp; done) '
                   '$(dumpsys thermalservice | grep -m1 "Thermal Status" | tr -dc 0-9)"').split()
        gtcpu = '?'
        try:
            tid2, _ = game_tid()
            if tid2:
                st = sh(f'cat /proc/{pid}/task/{tid2}/stat').strip()
                if st and ')' in st:
                    gtcpu = st.split(')', 1)[1].split()[36]  # field 39 = processor
        except Exception as e:
            gtcpu = f'err:{e}'[:40]
        therm.append(f'gtcpu={gtcpu}')
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
    if cpu_win and 'start' not in cpu_snap and tick >= cpu_win[0]:
        cpu_snap['start'] = (time.time(), tick, task_cpu(pid))
        log(f'CPUWIN start tick={tick}')
    if cpu_win and 'start' in cpu_snap and 'end' not in cpu_snap and tick >= cpu_win[1]:
        cpu_snap['end'] = (time.time(), tick, task_cpu(pid))
        log(f'CPUWIN end tick={tick}')
        write_cpu()
    if sf_ticks and tick >= sf_ticks[0]:
        sf_ticks.pop(0)
        full = sh('dumpsys SurfaceFlinger', timeout=90)
        keep, on = [], False
        for ln in full.splitlines():
            if 'HWC layers' in ln:
                on = True
            if on:
                keep.append(ln)
                if len(keep) > 60 or (keep and ln.strip() == '' and len(keep) > 3):
                    on = False
        keep += [ln for ln in full.splitlines() if 'ps2x-game' in ln][:40]
        with open(f'{OUT}/sf-hwc.txt', 'a') as f:
            f.write(f'tick={tick}\n' + '\n'.join(keep) + '\n')
        log(f'SFDUMP tick={tick} lines={len(keep)}')
    if a.lifecycle and not lifecycle_done and tick >= a.lifecycle:
        lifecycle_done = True
        run_lifecycle()
    if a.swipe_tick and not swipe_done and tick >= a.swipe_tick:
        swipe_done = True
        sh('input swipe 960 1079 960 900 150')
        time.sleep(1)
        scap('swipe-bars')
        time.sleep(3)
        scap('swipe-autohide')
        log(f'SWIPE focus={sh("dumpsys window | grep -m1 mCurrentFocus").strip()[:120]!r} '
            f'pid={sh(f"pidof {PKG}").strip() or "none"}')
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
if a.pad_probe and sh(f'pidof {PKG}').strip():
    sh('input gamepad keyevent --longpress KEYCODE_BUTTON_A')
    time.sleep(3)
    vp = [l.strip()[-160:] for l in open(f'{OUT}/logcat.txt', errors='replace') if '[vpad]' in l]
    log(f'PADPROBE vpad lines: {vp[-3:]}')
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
if a.compare_ticks:
    for name in sh(f'ls {DDUMP}').split():
        adb('pull', f'{DDUMP}/{name}', f'{SCR}/{name}')
sh(f'rm -rf {DDUMP}')
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
        if name.endswith('.png') or name.endswith('.data') or name.endswith('.ppm'):
            h = hashlib.sha256(open(f'{SCR}/{name}', 'rb').read()).hexdigest()
            f.write(f'{h}  {name}\n')
transport_end = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True,
                               timeout=30).stdout
open(f'{OUT}/transport-end.txt', 'w').write(f'serial={D}\ndisconnects={DISCONNECTS["n"]}\n{transport_end}')
log(f'END pid-after={sh(f"pidof {PKG}").strip() or "none"} disconnects={DISCONNECTS["n"]}')
lease_release()
CLAIMED['v'] = False
