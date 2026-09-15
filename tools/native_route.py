#!/usr/bin/env python3
"""Waypoint steering for the native ride harness: heading, pursuit, stick.

A recorded movie replays only the line it recorded, so reaching a chosen object
or a finish needs steering. The harness observes the rider's position several
times a second and can write `SET MAIN x y` to the controller pipe, so the loop
is: infer the heading from how the rider actually moved, compare it with the
bearing to the next waypoint, and push the stick to close the difference.

Two things are deliberately not assumed. **Which way left turns**: the sign
between stick x and the heading's rotation belongs to the game and its camera,
and it cannot be measured by holding an input and watching the heading — the
terrain turns the rider far harder than a test offset does, so that reading is
dominated by the course. Instead the route steers with a tentative sign and
watches its own heading error: if the error grows over the first second and a
half of steering, the sign was backwards and it flips once. And **the vertical
axis**: steering is computed in the x/z plane because y is up in this game's
world coordinates (a rider climbing gains y), so height differences never enter
the bearing.
"""
import json
import math
from pathlib import Path

# Guest seconds of steering to judge before deciding the sign is backwards, and
# the growth in mean heading error that counts as "backwards".
SIGN_TRIAL_SECONDS = 1.5
SIGN_TRIAL_GROWTH = 1.15
# At most one flip: more than that is oscillation, not calibration.
SIGN_FLIPS = 1
# Below this horizontal step between samples the heading is noise, not motion.
MIN_STEP = 3.0
# Default look-ahead along the route, in world units. A rider at 50 mph covers
# roughly 1,500 units a second here, so this is about a second and a half of
# travel: far enough that the aim point does not jitter, near enough to turn
# before reaching it.
LOOK_AHEAD = 2000.0


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


def project(point, start, end):
    """Closest point on a segment, as (position, fraction along it)."""
    sx, sz = start
    dx, dz = end[0] - sx, end[1] - sz
    length = dx * dx + dz * dz
    if length <= 0:
        return start, 0.0
    fraction = min(1.0, max(0.0, ((point[0] - sx) * dx + (point[1] - sz) * dz) / length))
    return (sx + fraction * dx, sz + fraction * dz), fraction


def look_ahead_point(polyline, segment, position, distance):
    """Aim point `distance` along the polyline from the rider's projection.

    Pure pursuit: steering at a point ahead *along the path* rather than at the
    next waypoint is what keeps something fast on a curve — aiming straight at a
    corner makes it cut the corner and then chase.
    """
    closest, fraction = project(position, polyline[segment], polyline[segment + 1])
    remaining = distance
    index = segment
    start = closest
    while index + 1 < len(polyline):
        end = polyline[index + 1]
        span = math.hypot(end[0] - start[0], end[1] - start[1])
        if span >= remaining:
            if span <= 0:
                return end, index
            step = remaining / span
            return (start[0] + step * (end[0] - start[0]),
                    start[1] + step * (end[1] - start[1])), index
        remaining -= span
        index += 1
        start = end
    return polyline[-1], len(polyline) - 2


def advance_segment(polyline, segment, position):
    """Monotonic progress: keep the earliest segment the rider has not passed."""
    while segment + 2 < len(polyline):
        _, fraction = project(position, polyline[segment], polyline[segment + 1])
        if fraction < 1.0:
            break
        segment += 1
    return segment


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
                 sign=options.get('sign'),
                 look_ahead=float(options.get('look_ahead', LOOK_AHEAD)),
                 engage_within=(float(options['engage_within'])
                                if options.get('engage_within') is not None else None))


class Route:
    """Follows a polyline by pure pursuit, correcting the steering sign in flight.

    With a single waypoint the polyline is the line from wherever the rider was
    when the route engaged, so the same controller covers "go to this object".
    """

    def __init__(self, waypoints, tolerance=500.0, gain=0.8, sign=None,
                 look_ahead=LOOK_AHEAD, engage_within=None):
        if tolerance <= 0 or not 0 < gain <= 10 or look_ahead <= 0:
            raise ValueError('Tolerance, gain and look-ahead must be positive, gain within (0, 10]')
        if engage_within is not None and engage_within <= 0:
            raise ValueError('engage_within must be positive when given')
        self.waypoints = list(waypoints)
        self.tolerance = tolerance
        self.gain = gain
        self.look_ahead = look_ahead
        self.engage_within = engage_within
        self.sign = sign if sign is not None else 1
        self.sign_given = sign is not None
        self.flips = 0
        self.trial = None          # (started_t, |error| sum, samples) since this sign
        self.polyline = None
        self.segment = 0
        self.index = 0
        self.previous = None
        self.engaged = False
        self.events = []

    @property
    def done(self):
        return self.index >= len(self.waypoints)

    def _distance(self, position, waypoint):
        return math.hypot(waypoint[0] - position[0], waypoint[1] - position[1])

    def reached(self, position):
        return self._distance(position, self.waypoints[self.index]) <= self.tolerance

    def _judge_sign(self, t, error):
        """Flip once if steering has been making the heading error worse."""
        if self.sign_given or self.flips >= SIGN_FLIPS:
            return
        magnitude = abs(error)
        if self.trial is None:
            self.trial = [t, magnitude, 1, magnitude]
            return
        started, total, count, first = self.trial
        self.trial = [started, total + magnitude, count + 1, first]
        if t - started < SIGN_TRIAL_SECONDS or count < 4:
            return
        mean = (total + magnitude) / (count + 1)
        if mean > first * SIGN_TRIAL_GROWTH and mean > math.radians(10):
            self.sign = -self.sign
            self.flips += 1
            self.events.append({'t': t, 'sign_flipped_to': self.sign,
                                'mean_error_degrees': math.degrees(mean),
                                'first_error_degrees': math.degrees(first)})
        self.trial = None

    def update(self, sample):
        """(stick_x, stick_y) for this sample, or None to leave the stick alone."""
        position = horizontal(sample)
        previous, self.previous = self.previous, position
        if self.done:
            return None
        # Engaging late is how a short route near its target avoids trying to
        # drive the whole descent.
        if not self.engaged:
            if (self.engage_within is not None
                    and self._distance(position, self.waypoints[0]) > self.engage_within):
                return None
            self.engaged = True
            self.polyline = [position, *self.waypoints]
            self.events.append({'t': sample['t'], 'engaged': True,
                                'distance_to_first': round(self._distance(position, self.waypoints[0]), 1)})
        while not self.done and self.reached(position):
            self.events.append({'t': sample['t'], 'reached': self.index,
                                'waypoint': self.waypoints[self.index]})
            self.index += 1
            self.segment = min(self.index, len(self.polyline) - 2)
        if self.done or previous is None:
            return None
        current = heading(previous, position)
        if current is None:
            return None   # stationary or resetting: do not steer on noise
        self.segment = advance_segment(self.polyline, self.segment, position)
        aim, _ = look_ahead_point(self.polyline, self.segment, position, self.look_ahead)
        error = angle_error(current, bearing(position, aim))
        self._judge_sign(sample['t'], error)
        return (steer(error, self.gain, self.sign), 0.5)

    def report(self):
        return {'waypoints': len(self.waypoints), 'reached': self.index,
                'complete': self.done, 'sign': self.sign, 'sign_given': self.sign_given,
                'sign_flips': self.flips, 'engaged': self.engaged,
                'tolerance': self.tolerance, 'gain': self.gain,
                'look_ahead': self.look_ahead, 'engage_within': self.engage_within,
                'events': self.events}
