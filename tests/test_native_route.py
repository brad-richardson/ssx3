"""Waypoint steering: geometry, sign calibration, and what it refuses to do."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from native_route import (Route, advance_segment, angle_error, bearing, heading, load_route,
                          look_ahead_point, project, steer)


def sample(t, x, z, y=0.0):
    return dict(t=t, x=x, y=y, z=z, state=0)


class GeometryTests(unittest.TestCase):
    def test_heading_ignores_height_and_small_steps(self):
        self.assertAlmostEqual(heading((0, 0), (10, 0)), 0.0)
        self.assertAlmostEqual(heading((0, 0), (0, 10)), math.pi / 2)
        self.assertIsNone(heading((0, 0), (1, 1)))

    def test_bearing_and_wrapped_error(self):
        self.assertAlmostEqual(bearing((0, 0), (0, 5)), math.pi / 2)
        self.assertAlmostEqual(angle_error(math.pi - .1, -math.pi + .1), .2, places=6)
        self.assertAlmostEqual(angle_error(1.0, 1.0), 0.0)

    def test_steering_is_centred_saturating_and_signed(self):
        self.assertAlmostEqual(steer(0.0), 0.5)
        self.assertEqual(steer(math.pi, gain=2.0), 1.0)
        self.assertEqual(steer(-math.pi, gain=2.0), 0.0)
        self.assertLess(steer(0.5, sign=-1), 0.5)
        self.assertGreater(steer(0.5, sign=1), 0.5)


class SignTests(unittest.TestCase):
    def drive(self, route, steps, turn_per_stick):
        """Fly a rider whose heading responds to the stick by `turn_per_stick`."""
        x, z, angle = 0.0, 0.0, 0.0
        for i in range(steps):
            stick = route.update(sample(i * 0.2, x, z))
            if stick:
                angle += (stick[0] - 0.5) * turn_per_stick
            x += 40 * math.cos(angle)
            z += 40 * math.sin(angle)
        return x, z

    def test_a_backwards_sign_is_flipped_once(self):
        # The rider responds opposite to the assumed sense, so the error grows.
        route = Route([(0.0, 4000.0)], tolerance=200.0, gain=1.0, look_ahead=800.0)
        self.drive(route, 40, turn_per_stick=-1.0)
        self.assertEqual(route.sign, -1)
        self.assertEqual(route.flips, 1)
        self.assertTrue(any('sign_flipped_to' in e for e in route.events))

    def test_a_correct_sign_is_left_alone(self):
        route = Route([(0.0, 4000.0)], tolerance=200.0, gain=1.0, look_ahead=800.0)
        self.drive(route, 40, turn_per_stick=1.0)
        self.assertEqual(route.sign, 1)
        self.assertEqual(route.flips, 0)

    def test_a_given_sign_is_never_second_guessed(self):
        route = Route([(0.0, 4000.0)], tolerance=200.0, gain=1.0, look_ahead=800.0, sign=1)
        self.drive(route, 40, turn_per_stick=-1.0)
        self.assertEqual((route.sign, route.flips), (1, 0))
        self.assertTrue(route.report()['sign_given'])

    def test_a_stationary_rider_is_never_steered(self):
        route = Route([(1000.0, 0.0)], sign=1)
        self.assertIsNone(route.update(sample(0, 0, 0)))
        self.assertIsNone(route.update(sample(1, 0, 0)))
        self.assertIsNone(route.update(sample(2, 1, 1)))


class FollowingTests(unittest.TestCase):
    def test_waypoints_are_consumed_in_order_and_the_route_completes(self):
        route = Route([(100.0, 0.0), (200.0, 0.0)], tolerance=30.0, gain=1.0, sign=1)
        route.update(sample(0, 0, 0))
        route.update(sample(1, 50, 0))
        self.assertEqual(route.index, 0)
        route.update(sample(2, 95, 0))
        self.assertEqual(route.index, 1)
        route.update(sample(3, 195, 0))
        self.assertTrue(route.done)
        self.assertIsNone(route.update(sample(4, 300, 0)))
        self.assertEqual(route.report()['reached'], 2)

    def test_it_steers_towards_a_waypoint_off_to_one_side(self):
        route = Route([(1000.0, 1000.0)], tolerance=50.0, gain=1.0, sign=1)
        route.update(sample(0, 0, 0))
        stick = route.update(sample(1, 50, 0))   # heading +x, waypoint 45 deg to +z
        self.assertIsNotNone(stick)
        self.assertGreater(stick[0], 0.5)
        self.assertEqual(stick[1], 0.5)

    def test_several_waypoints_at_once_are_all_consumed(self):
        route = Route([(10.0, 0.0), (20.0, 0.0), (30.0, 0.0)], tolerance=100.0, sign=1)
        route.update(sample(0, 0, 0))
        self.assertTrue(route.done)


class PursuitTests(unittest.TestCase):
    def test_projection_clamps_to_the_segment(self):
        self.assertEqual(project((5, 5), (0, 0), (10, 0)), ((5.0, 0.0), 0.5))
        self.assertEqual(project((-5, 0), (0, 0), (10, 0)), ((0.0, 0.0), 0.0))
        self.assertEqual(project((99, 0), (0, 0), (10, 0)), ((10.0, 0.0), 1.0))
        self.assertEqual(project((1, 1), (4, 4), (4, 4)), ((4, 4), 0.0))

    def test_the_aim_point_walks_along_the_polyline(self):
        line = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]
        aim, _ = look_ahead_point(line, 0, (0.0, 0.0), 50.0)
        self.assertEqual(aim, (50.0, 0.0))
        # Past the corner, the aim point turns with the path rather than cutting it.
        aim, _ = look_ahead_point(line, 0, (90.0, 0.0), 40.0)
        self.assertAlmostEqual(aim[0], 100.0)
        self.assertAlmostEqual(aim[1], 30.0)
        # Beyond the end it saturates at the last point.
        aim, _ = look_ahead_point(line, 0, (0.0, 0.0), 10_000.0)
        self.assertEqual(aim, line[-1])

    def test_segment_progress_is_monotonic(self):
        line = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (300.0, 0.0)]
        self.assertEqual(advance_segment(line, 0, (150.0, 0.0)), 1)
        self.assertEqual(advance_segment(line, 1, (250.0, 0.0)), 2)
        # Falling back does not rewind the route.
        self.assertEqual(advance_segment(line, 2, (10.0, 0.0)), 2)

    def test_a_corner_is_taken_wide_rather_than_cut(self):
        """Pure pursuit aims along the path, so the error is smaller than to the corner."""
        route = Route([(1000.0, 0.0), (1000.0, 1000.0)], tolerance=50.0, gain=1.0,
                      sign=1, look_ahead=500.0)
        route.update(sample(0, 0, 0))
        stick = route.update(sample(1, 50, 0))
        self.assertIsNotNone(stick)
        self.assertAlmostEqual(stick[0], 0.5, places=3)   # still straight ahead

    def test_a_route_can_wait_until_the_rider_is_close(self):
        route = Route([(10_000.0, 0.0)], tolerance=100.0, sign=1, engage_within=1000.0)
        self.assertIsNone(route.update(sample(0, 0, 0)))
        self.assertIsNone(route.update(sample(1, 100, 0)))
        self.assertFalse(route.engaged)
        route.update(sample(2, 9500, 0))
        self.assertTrue(route.engaged)
        self.assertTrue(any(e.get('engaged') for e in route.events))
        self.assertAlmostEqual(route.events[0]['distance_to_first'], 500.0)


class LoadTests(unittest.TestCase):
    def write(self, payload):
        path = Path(tempfile.mkdtemp()) / 'route.json'
        path.write_text(json.dumps(payload))
        return path

    def test_both_shapes_load_and_options_carry(self):
        route = load_route(self.write([[1, 2, 3], {'x': 4, 'y': 5, 'z': 6}]))
        self.assertEqual(route.waypoints, [(1.0, 3.0), (4.0, 6.0)])
        route = load_route(self.write({'waypoints': [[0, 0, 0]], 'tolerance': 9, 'gain': 2,
                                       'sign': -1, 'look_ahead': 7, 'engage_within': 8}))
        self.assertEqual((route.tolerance, route.gain, route.sign), (9.0, 2.0, -1))
        self.assertEqual((route.look_ahead, route.engage_within), (7.0, 8.0))

    def test_bad_routes_are_refused(self):
        for payload in ([], {'waypoints': []}, [[1, 2]], [['a', 'b', 'c']]):
            with self.assertRaises((ValueError, KeyError, TypeError)):
                load_route(self.write(payload))
        with self.assertRaises(ValueError):
            Route([(0.0, 0.0)], tolerance=0)
        with self.assertRaises(ValueError):
            Route([(0.0, 0.0)], gain=20)
        with self.assertRaises(ValueError):
            Route([(0.0, 0.0)], look_ahead=0)
        with self.assertRaises(ValueError):
            Route([(0.0, 0.0)], engage_within=-1)


if __name__ == '__main__':
    unittest.main()
