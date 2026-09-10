"""Steer the rider toward XY waypoints using live PINE position feedback and D-pad keys.

Rider position: EE offset 0x5409c0 (three floats, observed stable across transports in SLUS-20772).
Only one PINE client may be connected at a time; this script owns the connection while it runs.

Usage: ride_autopilot.py LOG SECONDS --wps 'x1,y1;x2,y2' [--sign +1|-1] [--radius R]
Resumes from the pause menu first (Cross), pauses (Start) at the end.
"""
import sys, time, json, math, subprocess, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / 'local' / 'bin'
sys.path.insert(0, str(ROOT / 'tools'))
from pine import Pine
ADDR = 0x5409c0
LEFT, RIGHT, CROSS, START = 123, 124, 7, 36
ap = argparse.ArgumentParser()
ap.add_argument('log'); ap.add_argument('seconds', type=float); ap.add_argument('--wps', required=True, help='x,y;x,y;...')
ap.add_argument('--sign', type=float, default=1.0, help='+1 if Left turns the heading counter-clockwise in XY')
ap.add_argument('--radius', type=float, default=600)
ap.add_argument('--no-resume', action='store_true'); ap.add_argument('--no-pause', action='store_true')
ap.add_argument('--deadband', type=float, default=6.0)
ap.add_argument('--gain', type=float, default=60.0, help='degrees of error for a 100%% duty cycle')
ap.add_argument('--cycle', type=float, default=0.2)
ap.add_argument('--capture-dir'); ap.add_argument('--capture-radius', type=float, default=3000)
ap.add_argument('--capture-at', help='x,y centre for captures (default: last waypoint)')
ap.add_argument('--overrun', type=float, default=1.5, help='seconds to keep going after the last waypoint')
a = ap.parse_args()
wps = [tuple(map(float, w.split(','))) for w in a.wps.split(';')]
kd = subprocess.Popen([str(BIN / 'keyd')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def cmd(c):
    kd.stdin.write(c + '\n'); kd.stdin.flush(); kd.stdout.readline()
p = Pine(); log = open(a.log, 'w')
if not a.no_resume:
    cmd(f'tap {CROSS}'); time.sleep(0.4)
held = None
def hold(key):
    global held
    if held == key: return
    if held is not None: cmd(f'up {held}')
    if key is not None: cmd(f'down {key}')
    held = key
hist = []; t0 = time.time(); wi = 0; status = 'timeout'; shots = []; reached_t = None
cap_at = tuple(map(float, a.capture_at.split(','))) if a.capture_at else wps[-1]
wid = subprocess.check_output([str(BIN / 'window_id')]).decode().strip() if a.capture_dir else None
try:
    while time.time() - t0 < a.seconds:
        x, y, z = p.read_floats(ADDR, 3); t = time.time() - t0
        hist.append((t, x, y, z))
        tx, ty = wps[wi]
        dist = math.hypot(tx - x, ty - y)
        fx, fy = cap_at; fdist = math.hypot(fx - x, fy - y)
        if wid and fdist < a.capture_radius and (not shots or time.time() - shots[-1][0] > 0.45):
            path = f'{a.capture_dir}/approach_{len(shots)+1:02d}.png'
            subprocess.Popen(['screencapture', '-x', '-l', wid, path]); shots.append((time.time(), path, x, y, z, fdist))
        if reached_t is None and dist < a.radius:
            wi += 1
            if wi >= len(wps): status = 'reached'; reached_t = time.time(); wi = len(wps) - 1
            tx, ty = wps[wi]
        if reached_t and time.time() - reached_t > a.overrun: break
        entry = dict(t=round(t, 2), x=round(x, 1), y=round(y, 1), z=round(z, 1), wp=wi, dist=round(dist, 1))
        old = [h for h in hist if t - h[0] >= 0.2]
        if old:
            _, ox, oy, _ = old[-1]
            vx, vy = x - ox, y - oy
            if math.hypot(vx, vy) > 15:
                heading = math.degrees(math.atan2(vy, vx)); bearing = math.degrees(math.atan2(ty - y, tx - x))
                err = (bearing - heading + 180) % 360 - 180   # +: target is counter-clockwise of heading
                entry.update(heading=round(heading), bearing=round(bearing), err=round(err))
                if abs(err) >= a.deadband:
                    # Pulsed proportional steering: hold for a fraction of a short cycle.
                    duty = min(1.0, max(0.25, abs(err) / a.gain))
                    key = LEFT if err * a.sign > 0 else RIGHT
                    cmd(f'down {key}'); time.sleep(a.cycle * duty); cmd(f'up {key}')
                    if duty < 1.0: time.sleep(a.cycle * (1 - duty))
                    entry.update(key='L' if key == LEFT else 'R', duty=round(duty, 2))
                    log.write(json.dumps(entry) + '\n'); log.flush()
                    continue
        log.write(json.dumps(entry) + '\n'); log.flush()
        time.sleep(0.08)
finally:
    hold(None)
    if not a.no_pause: cmd(f'tap {START}')
    cmd('quit')
print(json.dumps(dict(status=status, waypoint=wi, last=hist[-1] if hist else None)))
for sh in shots: print('shot', sh[1].split('/')[-1], 'xyz=(%.0f,%.0f,%.0f) fdist=%.0f' % sh[2:])
