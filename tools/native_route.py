#!/usr/bin/env python3
"""Waypoint steering for the native ride harness: heading, error, stick.

A recorded movie replays only the line it recorded, so reaching a chosen object
or a finish needs steering. The harness observes the rider's position several
times a second and can write `SET MAIN x y` to the controller pipe, so the loop
is: infer the heading from how the rider actually moved, compare it with the
bearing to the next waypoint, and push the stick to close the difference.

Two things are deliberately not assumed. **Which way left turns**: the sign
between stick x and the heading's rotation is a property of the game and the
camera, so the route calibrates it at the start by holding one steady input and
watching which way the heading goes. And **the vertical axis**: steering is
computed in the x/z plane because y is up in this game's world coordinates
(a rider climbing gains y), so height differences never enter the bearing.
"""
import json
import math
from pathlib import Path

# Held stick offset used while calibrating, and the guest seconds to hold it.
CALIBRATION_X = 0.15
CALIBRATION_SECONDS = 1.5
# Below this horizontal step between samples the heading is noise, not motion.
MIN_STEP = 3.0


def horizontal(sample):
    return (sample['x'], sample['z'])


def heading(previous, current, minimum=MIN_STEP):
    """Direction of travel in the x/z plane, or None when barely moving."""
    dx, dz = current[0] - previous[0], current[1] - previous[1]
    return math.atan2(dz, dx) if math.hypot(dx, dz) >= minimum else None


def bearing(position, waypoint):
    return math.atan2(waypoint[1] - position[1], waypoint[0] - position[0])


def angle_error(from_angle, to_angle):
    """Signed difference wrapped to [-pi, pi]."""
    return (to_angle - from_angle + math.pi) % (2 * math.pi) - math.pi


def steer(error, gain=1.0, sign=1):
    """Stick x in [0, 1]; 0.5 is centred. Saturates rather than wrapping."""
    return min(1.0, max(0.0, 0.5 + sign * gain * error / math.pi))


def load_route(path):
    """A route is waypoints plus the options that shape how they are followed."""
    data = json.loads(Path(path).read_text())
    waypoints = data['waypoints'] if isinstance(data, dict) else data
    points = []
    for point in waypoints:
        values = [point[k] for k in 'xyz'] if isinstance(point, dict) else list(point)
        if len(values) != 3 or not all(isinstance(v, (int, float)) for v in values):
            raise ValueError('Each waypoint needs three numbers')
        points.append((float(values[0]), float(values[2])))
    if not points:
        raise ValueError('A route needs at least one waypoint')
    options = data if isinstance(data, dict) else {}
    return Route(points, tolerance=float(options.get('tolerance', 500.0)),
                 gain=float(options.get('gain', 1.5)),
                 sign=options.get('sign'))


class Route:
    """Follows waypoints, calibrating the steering sign on the way to the first."""

    def __init__(self, waypoints, tolerance=500.0, gain=1.5, sign=None):
        if tolerance <= 0 or not 0 < gain <= 10:
            raise ValueError('Tolerance must be positive and gain within (0, 10]')
        self.waypoints = list(waypoints)
        self.tolerance = tolerance
        self.gain = gain
        self.sign = sign
        self.index = 0
        self.previous = None
        self.calibration = None   # (started_t, heading at that moment)
        self.events = []

    @property
    def done(self):
        return self.index >= len(self.waypoints)

    def reached(self, position):
        target = self.waypoints[self.index]
        return math.hypot(target[0] - position[0], target[1] - position[1]) <= self.tolerance

    def update(self, sample):
        """(stick_x, stick_y) for this sample, or None to leave the stick alone."""
        position = horizontal(sample)
        previous, self.previous = self.previous, position
        if self.done:
            return None
        while not self.done and self.reached(position):
            self.events.append({'t': sample['t'], 'reached': self.index,
                                'waypoint': self.waypoints[self.index]})
            self.index += 1
        if self.done:
            return None
        if previous is None:
            return None
        current = heading(previous, position)
        if current is None:
            return None   # stationary or resetting: do not steer on noise
        if self.sign is None:
            if self.calibration is None:
                self.calibration = (sample['t'], current)
                self.events.append({'t': sample['t'], 'calibration': 'started'})
                return (0.5 + CALIBRATION_X, 0.5)
            started, before = self.calibration
            if sample['t'] - started < CALIBRATION_SECONDS:
                return (0.5 + CALIBRATION_X, 0.5)
            turned = angle_error(before, current)
            if abs(turned) < math.radians(2):
                # No measurable turn: keep holding rather than guess a sign.
                self.calibration = (sample['t'], current)
                return (0.5 + CALIBRATION_X, 0.5)
            # A positive stick offset produced `turned`; steer with that sense.
            self.sign = 1 if turned > 0 else -1
            self.events.append({'t': sample['t'], 'calibration': 'done',
                                'turned_degrees': math.degrees(turned), 'sign': self.sign})
        error = angle_error(current, bearing(position, self.waypoints[self.index]))
        return (steer(error, self.gain, self.sign), 0.5)

    def report(self):
        return {'waypoints': len(self.waypoints), 'reached': self.index,
                'complete': self.done, 'sign': self.sign,
                'tolerance': self.tolerance, 'gain': self.gain, 'events': self.events}
