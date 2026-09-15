"""Waypoint steering: geometry, sign calibration, and what it refuses to do."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from native_route import (CALIBRATION_SECONDS, Route, angle_error, bearing, heading,
                          load_route, steer)


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


class CalibrationTests(unittest.TestCase):
    def follow(self, route, samples):
        return [route.update(s) for s in samples]

    def test_it_holds_one_input_then_adopts_the_sense_it_measured(self):
        route = Route([(1000.0, 0.0)], tolerance=50.0)
        # Heading starts along +x and rotates towards +z while the offset is held.
        outputs = []
        x, z = 0.0, 0.0
        angle = 0.0
        for i in range(30):
            outputs.append(route.update(sample(i * 0.2, x, z)))
            angle += math.radians(3)
            x += 20 * math.cos(angle)
            z += 20 * math.sin(angle)
        self.assertEqual(route.sign, 1)
        held = [o for o in outputs[:int(CALIBRATION_SECONDS / 0.2) + 1] if o]
        self.assertTrue(all(o[0] > 0.5 for o in held), held)
        self.assertTrue(any(e.get('calibration') == 'done' for e in route.events))

    def test_the_opposite_rotation_gives_the_opposite_sign(self):
        route = Route([(1000.0, 0.0)], tolerance=50.0)
        x, z, angle = 0.0, 0.0, 0.0
        for i in range(30):
            route.update(sample(i * 0.2, x, z))
            angle -= math.radians(3)
            x += 20 * math.cos(angle)
            z += 20 * math.sin(angle)
        self.assertEqual(route.sign, -1)

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


class LoadTests(unittest.TestCase):
    def write(self, payload):
        path = Path(tempfile.mkdtemp()) / 'route.json'
        path.write_text(json.dumps(payload))
        return path

    def test_both_shapes_load_and_options_carry(self):
        route = load_route(self.write([[1, 2, 3], {'x': 4, 'y': 5, 'z': 6}]))
        self.assertEqual(route.waypoints, [(1.0, 3.0), (4.0, 6.0)])
        route = load_route(self.write({'waypoints': [[0, 0, 0]], 'tolerance': 9, 'gain': 2, 'sign': -1}))
        self.assertEqual((route.tolerance, route.gain, route.sign), (9.0, 2.0, -1))

    def test_bad_routes_are_refused(self):
        for payload in ([], {'waypoints': []}, [[1, 2]], [['a', 'b', 'c']]):
            with self.assertRaises((ValueError, KeyError, TypeError)):
                load_route(self.write(payload))
        with self.assertRaises(ValueError):
            Route([(0.0, 0.0)], tolerance=0)
        with self.assertRaises(ValueError):
            Route([(0.0, 0.0)], gain=20)


if __name__ == '__main__':
    unittest.main()
