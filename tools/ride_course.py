#!/usr/bin/env python3
"""Record and optionally steer a course descent using PINE position reads.

Only keyboard input drives the rider; this tool never writes game memory.
It owns the PINE connection, logs route progress and large position jumps,
captures periodic screenshots, and pauses the game when the test ends.
"""
import argparse
import json
import math
from pathlib import Path
import subprocess
import time

from course_route import Route
from pine import Pine

ROOT = Path(__file__).resolve().parents[1]
LEFT, RIGHT, CROSS, START, SELECT = 123, 124, 7, 36, 12


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('route', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--seconds', type=float, default=360)
    ap.add_argument('--wait-spawn', action='store_true')
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--coast', action='store_true')
    ap.add_argument('--lookahead', type=float, default=1400)
    ap.add_argument('--capture-interval', type=float, default=30)
    ap.add_argument('--sign', type=float, default=1)
    ap.add_argument('--reset-at', default='', help='Comma-separated route fractions at which to test Reset')
    args = ap.parse_args()
    if not math.isfinite(args.capture_interval) or args.capture_interval <= 0:
        ap.error('--capture-interval must be finite and positive')
    args.output.mkdir(parents=True, exist_ok=False)
    route = Route(json.loads(args.route.read_text())['points'])
    reset_at = [float(v) for v in args.reset_at.split(',') if v]
    if reset_at != sorted(set(reset_at)) or any(not 0 < v < 1 for v in reset_at):
        ap.error('--reset-at fractions must be unique, increasing and between zero and one')
    p = Pine()
    kd = subprocess.Popen([str(ROOT / 'local/bin/keyd')], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, text=True, bufsize=1)

    def key(command):
        kd.stdin.write(command + '\n')
        kd.stdin.flush()
        if command != 'quit' and kd.stdout.readline().strip() != 'ok':
            raise RuntimeError('Keyboard helper failed')

    def capture(name):
        subprocess.run(['sh', str(ROOT / 'tools/macos/capture.sh'),
                        str(args.output / name)], check=True, capture_output=True)

    rows, jumps, resets = [], [], []
    started = None if args.wait_spawn else time.monotonic()
    wait_start = time.monotonic()
    next_report = next_capture = 0
    best_progress = 0
    last_advance = time.monotonic()
    status = 'timeout'
    try:
        if args.resume:
            key(f'tap {CROSS}')
        with (args.output / 'ride.jsonl').open('x') as log:
            while time.monotonic() - wait_start < args.seconds + 90:
                now = time.monotonic()
                xyz = p.read_floats(0x5409c0, 3)
                if not all(math.isfinite(v) for v in xyz):
                    raise ValueError('Nonfinite rider coordinates')
                if started is None:
                    if -125000 < xyz[0] < -105000 and -240000 < xyz[2] < -220000:
                        started = now
                        last_advance = now
                        print('Transport spawn:', xyz, flush=True)
                    elif now - wait_start > 90:
                        status = 'no_spawn'
                        break
                    else:
                        time.sleep(.1)
                        continue
                t = now - started
                nearest = route.nearest(xyz)
                progress = nearest['progress']
                row = dict(t=round(t, 3), x=xyz[0], y=xyz[1], z=xyz[2],
                           segment=nearest['segment'], progress=progress,
                           fraction=progress / route.length, route_distance=nearest['distance'])
                if rows:
                    previous = rows[-1]
                    displacement = math.dist(xyz, [previous[k] for k in ('x', 'y', 'z')])
                    if displacement > 5000 and t - previous['t'] < 1:
                        jumps.append(dict(t=t, distance=displacement, before=previous,
                                          after=dict(row)))
                        row['position_jump'] = displacement
                if progress > best_progress + 100:
                    best_progress = progress
                    last_advance = now
                target = route.at(progress + args.lookahead)
                old = next((r for r in reversed(rows) if t - r['t'] >= .25), None)
                turn = None
                if old and not args.coast:
                    dx, dy = xyz[0] - old['x'], xyz[1] - old['y']
                    if math.hypot(dx, dy) > 15:
                        heading = math.degrees(math.atan2(dy, dx))
                        bearing = math.degrees(math.atan2(target[1] - xyz[1], target[0] - xyz[0]))
                        error = (bearing - heading + 180) % 360 - 180
                        row.update(heading=heading, bearing=bearing, error=error)
                        if abs(error) > 7:
                            turn = LEFT if error * args.sign > 0 else RIGHT
                            duty = min(1, max(.2, abs(error) / 70))
                            row['key'] = 'L' if turn == LEFT else 'R'
                            row['duty'] = duty
                rows.append(row)
                if reset_at and progress / route.length >= reset_at[0]:
                    fraction = reset_at.pop(0)
                    row['reset_requested'] = fraction
                    resets.append(dict(t=t, fraction=fraction, before=xyz))
                    print('Testing Reset at', fraction, xyz, flush=True)
                    key(f'tap {SELECT}')
                    time.sleep(.4)
                    capture(f'reset-{fraction * 100:03.0f}.png')
                    turn = None
                log.write(json.dumps(row) + '\n')
                log.flush()
                if t >= next_report:
                    print(f"{t:.0f}s: {progress / route.length:.1%}, route distance {nearest['distance']:.0f}, XYZ {tuple(round(v) for v in xyz)}", flush=True)
                    next_report += 15
                if t >= next_capture:
                    capture(f'ride-{int(t):03d}.png')
                    next_capture += args.capture_interval
                if progress / route.length > .999 and math.dist(xyz, route.points[-1]) < 500:
                    status = 'route_end_reached'
                    break
                if t >= args.seconds:
                    break
                if now - last_advance > 35:
                    status = 'stalled'
                    break
                if turn:
                    key(f'down {turn}')
                    try:
                        time.sleep(.2 * duty)
                    finally:
                        key(f'up {turn}')
                    time.sleep(.2 * (1 - duty))
                else:
                    time.sleep(.1)
        key(f'tap {START}')
        capture('ride-end.png')
        (args.output / 'memory.bin').write_bytes(p.read(0, 32 << 20))
    finally:
        for k in (LEFT, RIGHT):
            key(f'up {k}')
        key('quit')
        kd.wait(timeout=5)
        p.close()
    summary = dict(status=status, samples=len(rows), seconds=rows[-1]['t'] if rows else 0,
                   initial_route_fraction=rows[0]['fraction'] if rows else None,
                   maximum_route_fraction=max((r['fraction'] for r in rows), default=0),
                   position_jumps=jumps, last=rows[-1] if rows else None,
                   route=str(args.route), coast=args.coast, lookahead=args.lookahead,
                   reset_requests=resets)
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
