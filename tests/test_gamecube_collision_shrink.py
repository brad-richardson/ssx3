"""Measuring colliders against their art.

The regression these pin down is a measurement error, not a data error: leaving
the instance's own uniform scale out of the comparison makes every collider look
1/0.55 = 1.8x too large, and the tool would then have shrunk correctly-sized
scenery to 55% and let the rider through it.
"""

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import gamecube_collision_shrink as shrink


def instance(bounds, scale):
    """A 160-byte static instance carrying bounds at 88 and uniform scale at 124."""
    payload = bytearray(160)
    struct.pack_into('>6f', payload, shrink.INSTANCE_BOUNDS_AT, *bounds)
    struct.pack_into('>f', payload, 124, scale)
    return bytes(payload)


def box(size, centre=(0.0, 0.0, 0.0)):
    """One mesh whose vertices span `size` about `centre`."""
    half = [v / 2 for v in size]
    vertices = [(centre[0] + sx * half[0], centre[1] + sy * half[1], centre[2] + sz * half[2], 1.0)
                for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    return [dict(vertices=vertices, triangles=[(0, 1, 2)], normals=[(0.0, 0.0, 1.0, 0.0)])]


class ScaleTests(unittest.TestCase):
    def test_the_instance_scalar_is_read_from_offset_124(self):
        self.assertAlmostEqual(shrink.instance_scale(instance((0,) * 6, 0.55)), 0.55, places=6)

    def test_a_collider_inside_its_art_is_left_alone(self):
        # Stored 244 wide, scalar 0.55 -> 134 effective, inside 177 of visual.
        effective = [244 * 0.55] * 3
        self.assertEqual(shrink.wanted_factor(effective, [[177.0] * 3]), 1.0)

    def test_ignoring_the_scalar_is_what_produced_the_bogus_shrink(self):
        """The bug, pinned on the real tree collider's numbers.

        Stored 244 against 177 of visible tree reads as 1.38x too wide and asks
        for a 0.73x correction, on a collider that is actually 134 wide once the
        instance's 0.55 scalar is applied - well inside the art, needing none.
        """
        self.assertAlmostEqual(shrink.wanted_factor([244.0] * 3, [[177.0] * 3]),
                               177.0 / 244.0, places=6)
        self.assertEqual(shrink.wanted_factor([244.0 * 0.55] * 3, [[177.0] * 3]), 1.0)

    def test_a_genuinely_oversized_collider_is_scaled_to_the_target(self):
        factor = shrink.wanted_factor([200.0] * 3, [[100.0] * 3], target=1.0, floor=0.1)
        self.assertAlmostEqual(factor, 0.5, places=6)

    def test_nothing_is_ever_inflated(self):
        self.assertEqual(shrink.wanted_factor([50.0] * 3, [[100.0] * 3], target=1.0), 1.0)

    def test_the_floor_bounds_the_correction(self):
        factor = shrink.wanted_factor([1000.0] * 3, [[100.0] * 3], target=1.0, floor=0.55)
        self.assertEqual(factor, 0.55)

    def test_a_collider_with_no_instances_is_left_alone(self):
        self.assertEqual(shrink.wanted_factor([500.0] * 3, []), 1.0)

    def test_a_lower_target_is_a_deliberate_gameplay_choice(self):
        factor = shrink.wanted_factor([80.0] * 3, [[100.0] * 3], target=0.6, floor=0.1)
        self.assertAlmostEqual(factor, 0.75, places=6)


class MeshTests(unittest.TestCase):
    def test_scaling_is_about_the_collider_centre_and_keeps_normals(self):
        meshes = box((100.0, 100.0, 200.0), centre=(1000.0, 0.0, -500.0))
        low, extent = shrink.collider_extent(meshes)
        scaled = shrink.scale_meshes(meshes, low, extent, 0.5)
        new_low, new_extent = shrink.collider_extent(scaled)
        for axis in range(3):
            self.assertAlmostEqual(new_extent[axis], extent[axis] * 0.5, places=4)
            # The centre does not move, so the collider stays where the art is.
            self.assertAlmostEqual(new_low[axis] + new_extent[axis] / 2,
                                   low[axis] + extent[axis] / 2, places=3)
        self.assertEqual(scaled[0]['normals'], meshes[0]['normals'])
        self.assertEqual(scaled[0]['triangles'], meshes[0]['triangles'])

    def test_collider_extent_reports_none_without_vertices(self):
        low, extent = shrink.collider_extent([dict(vertices=[], triangles=[], normals=[])])
        self.assertIsNone(low)
        self.assertIsNone(extent)

    def test_visual_extent_is_the_bounds_span(self):
        payload = instance((-10.0, -20.0, -30.0, 10.0, 20.0, 30.0), 1.0)
        self.assertEqual(shrink.visual_extent(payload), [20.0, 40.0, 60.0])


if __name__ == '__main__':
    unittest.main()
