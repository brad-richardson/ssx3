import struct
import unittest

from gamecube_course_fixture import relocate_race_gates
from course_route import ssx3_paths
from test_gamecube_reset_paths import fixture


class CourseFixtureTests(unittest.TestCase):
    def test_only_race_position_direction_change(self):
        aip, _, _ = fixture()
        aip = bytearray(aip)
        struct.pack_into('<I', aip, len(aip)-44, 2)
        extra = bytearray(aip[-40:])
        struct.pack_into('<2I', extra, 0, 1, 1)
        aip.extend(extra)
        out, edits = relocate_race_gates(aip, [10,20,30], [0,2,0], 30)
        old, new = ssx3_paths(aip), ssx3_paths(out)
        self.assertEqual(new[:2], old[:2])
        self.assertEqual(new[3][1], old[3][1])
        self.assertEqual(new[3][0][2:8], (10,20,30,0,1,0))
        self.assertEqual(new[3][0][-2:], old[3][0][-2:])
        self.assertEqual(len(edits), 1)

    def test_invalid_directions_and_coordinates_fail(self):
        aip, _, _ = fixture()
        for direction in ([0,0,0], [0,0,1], [float('nan'),0,0]):
            with self.assertRaises(ValueError):
                relocate_race_gates(aip, [0,0,0], direction, 30)
