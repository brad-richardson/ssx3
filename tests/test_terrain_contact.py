from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_world_experiment import serialize_resources
from import_terrain import make_record
from terrain_contact import patches, hit


class ContactTests(unittest.TestCase):
    def test_exact_height_on_sloped_surface_and_outside_footprint(self):
        # x=10+20u, y=30+40v, z=50+3u-7v. Query at u=.37, v=.63.
        c = [[0, 0, 0] for _ in range(16)]
        c[15], c[14], c[11] = [10, 30, 50], [20, 0, 3], [0, 40, -7]
        p = make_record(bytes(432), c)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'terrain.bin'
            path.write_bytes(serialize_resources([(dict(kind=1, size=432, track=8, rid=12), p)]))
            surfaces = patches(path)
        expected_z = 50 + 3 * .37 - 7 * .63
        result = hit(surfaces, 10 + 20 * .37, 30 + 40 * .63, expected_z + 2)
        self.assertEqual(result['rid'], 12)
        self.assertAlmostEqual(result['z'], expected_z, places=6)
        self.assertAlmostEqual(result['residual'], 2, places=6)
        self.assertIsNone(hit(surfaces, 40, 80, expected_z))

    def test_zero_area_surface_does_not_invent_a_hit(self):
        c = [[0, 0, 0] for _ in range(16)]
        surfaces = [(1, c, (0, 0, 0), (0, 0, 0), [(0, 0, (0, 0, 0))])]
        self.assertIsNone(hit(surfaces, .5, .5, 0))
        self.assertIsNone(hit(surfaces, 0, 0, 0))
