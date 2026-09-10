"""After selecting a Green Station transport, wait for the spawn, optionally test the steering
sign, then hand over to ride_autopilot.py for the waypoints (SIGN, CAPTURE_AT environment).

Usage: ride_route.py CAPTURE_DIR LOG.jsonl "x1,y1;x2,y2" | auto
auto picks the east or west Green Station spawn route. SIGN=1 skips the sign test (Left turns
the XY heading counter-clockwise in this game). Requires local/bin from tools/macos/build.sh.
"""
import sys, time, json, math, subprocess, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / 'local' / 'bin'
sys.path.insert(0, str(ROOT / 'tools'))
from pine import Pine
ADDR = 0x5409c0; LEFT, RIGHT, START = 123, 124, 36
out_dir, log_path = sys.argv[1], sys.argv[2]
p = Pine()
def pos(): return p.read_floats(ADDR, 3)
# 1. wait for spawn in hub A bounds and movement
t0 = time.time(); last = None
ROUTES = {'east': '-93000,40400;-97000,39600;-101500,38400;-103500,37800',
          'west': '-101500,42500;-103000,40500;-103800,39000;-103500,37800'}
while True:
    x, y, z = pos()
    if min(math.dist((x, y), sp) for sp in ((-66300, 33600), (-99560, 43660))) < 2500:
        if last is None: last = (x, y)
        elif math.dist((x, y), last) > 200: break
    time.sleep(0.2)
    if time.time() - t0 > 90: print('no spawn'); sys.exit(1)
route = ROUTES['west'] if x < -90000 else ROUTES['east']
if sys.argv[3] == 'auto': sys.argv[3] = route
wps = [tuple(map(float, w.split(','))) for w in sys.argv[3].split(';')]
print('spawned at', round(x), round(y), round(z), 'after', round(time.time() - t0, 1), 's', flush=True)
kd = subprocess.Popen([str(BIN / 'keyd')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def cmd(c): kd.stdin.write(c + '\n'); kd.stdin.flush(); kd.stdout.readline()
def heading(dt=0.4):
    x0, y0, _ = pos(); time.sleep(dt); x1, y1, _ = pos()
    return math.degrees(math.atan2(y1 - y0, x1 - x0)), math.hypot(x1 - x0, y1 - y0)
# 2. sign test: hold Left 1.2 s (skipped when SIGN env is set)
sign = float(os.environ.get('SIGN', '0'))
if not sign:
    time.sleep(2.0)
    h0, s0 = heading(); cmd(f'down {LEFT}'); time.sleep(1.2); h1, s1 = heading(); cmd(f'up {LEFT}')
    dh = (h1 - h0 + 180) % 360 - 180
    sign = 1.0 if dh > 0 else -1.0
    print(json.dumps(dict(sign_test=dict(h0=round(h0), h1=round(h1), dh=round(dh), speed0=round(s0), speed1=round(s1), sign=sign))), flush=True)
cmd('quit'); kd.wait()
# 3. autopilot (single PINE client: close ours first); it captures on approach and pauses at the end
p.close()
cmd_line = [sys.executable, str(ROOT / 'tools' / 'ride_autopilot.py'), log_path, '75', '--wps=' + sys.argv[3],
            '--sign', str(sign), '--no-resume', '--radius', '500', '--capture-dir', out_dir] + (['--capture-at=' + os.environ['CAPTURE_AT']] if os.environ.get('CAPTURE_AT') else [])
print(subprocess.run(cmd_line, capture_output=True, text=True).stdout, flush=True)
