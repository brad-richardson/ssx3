import hashlib
from pathlib import Path
import struct
import tempfile
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from course_route import (Route, race_paths, ai_paths, make_reset_aip, ssx3_paths, route_points,
                          donor_paths, start_list)


def donor_file(ai_count=2, race_count=1, starts=(0, 1)):
    """A minimal Tricky path container; `.aip` and `.sop` share this layout."""
    geometry = struct.pack('<9f8f', 10, 20, 30, 10, 20, 28, 12, 23, 30,
                           1, 0, -1, 2, 0, 1, 0, 3)
    ai = struct.pack('<9I', 1, 1, 0, 2, 100, 4, 50, 2, 0) + geometry
    race = struct.pack('<3If2I', 1, 0, 4, 100, 2, 0) + geometry
    section = struct.pack('<2I', ai_count, len(starts)) + struct.pack(f'<{len(starts)}I', *starts) + ai * ai_count
    out = struct.pack('<4I', 0x0a0a0a0a, 2, 0, len(section)) + section
    out += struct.pack('<4I', 1, 8 + len(race) * race_count, race_count, 0) + race * race_count
    return out


class DonorPathFileTests(unittest.TestCase):
    def test_sop_and_aip_use_one_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            for suffix in ('.aip', '.sop'):
                path = Path(tmp) / f'course{suffix}'
                path.write_bytes(donor_file())
                donor = donor_paths(path)
                self.assertEqual(len(donor['ai_paths']), 2)
                self.assertEqual(len(donor['race_paths']), 1)
                self.assertEqual(donor['start_list'], [0, 1])
                self.assertEqual(donor['sha256'], hashlib.sha256(donor['data']).hexdigest())

    def test_a_start_outside_the_ai_section_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'course.sop'
            path.write_bytes(donor_file(starts=(0, 9)))
            self.assertEqual(start_list(path.read_bytes()), [0, 9])
            with self.assertRaisesRegex(ValueError, 'absent path'):
                donor_paths(path)


class RouteTests(unittest.TestCase):
    def test_reset_conversion_transforms_paths_and_omits_foreign_events(self):
        geometry = struct.pack('<9f8f', 10, 20, 30, 10, 20, 28, 12, 23, 30,
                               1, 0, -1, 2, 0, 1, 0, 3)
        event = struct.pack('<2I2f', 101, 99, 1, 2)
        ai = struct.pack('<3I9I', 1, 1, 0, 2, 100, 4, 50, 101, 4, 1, 2, 1) + geometry + event
        race = struct.pack('<3If2I', 1, 0, 4, 100, 2, 1) + geometry + event
        donor = struct.pack('<4I', 0x0a0a0a0a, 2, 0, len(ai)) + ai
        donor += struct.pack('<4I', 1, 8 + len(race), 1, 0) + race
        self.assertEqual(ai_paths(donor)[0]['points'][-1], (12, 23, 28))
        start = struct.pack('<2I6f2I', 1, 1, 10, 20, 30, 1, 0, 0, 0, 0)
        other_start = struct.pack('<2I6f2I', 2, 1, 40, 50, 60, 0, 1, 0, 2, 0)
        tail = struct.pack('<2I', 0, 2) + start + other_start
        original = struct.pack('<2I', 0x69696969, 3) + ai[12:] * 3
        original += struct.pack('<I', 1) + race + tail
        result, report = make_reset_aip(donor, [[0, -2, 0], [2, 0, 0], [0, 0, 2]], [100, 200, 300], 2, original)
        self.assertEqual(struct.unpack_from('<2I', result), (0x69696969, 3))
        paths, tracks, kept_tail, starts = ssx3_paths(result)
        self.assertEqual(paths[0], ai[12:])
        self.assertEqual(struct.unpack_from('<I', paths[2], 24)[0], 0)
        self.assertEqual(tracks[0], race)
        self.assertEqual(kept_tail, tail)
        self.assertEqual(struct.unpack_from('<2I', paths[1], 28), (2, 0))
        self.assertEqual(struct.unpack_from('<3f', paths[1], 36), (60, 220, 360))
        self.assertEqual(struct.unpack_from('<4f', paths[1], 72), (0, 1, -1, 4))
        self.assertEqual(struct.unpack_from('<4f', paths[1], 88), (-1, 0, 0, 6))
        self.assertEqual(report['donor_path_events'], 0)
        self.assertEqual(report['disabled_original_reset_paths'], 1)
        self.assertEqual(report['replaced_path_indices'], [1])
        moved, movement = make_reset_aip(donor, [[0, -2, 0], [2, 0, 0], [0, 0, 2]],
                                         [100, 200, 300], 2, original, relocate_start=True)
        moved_paths, moved_tracks, _, moved_starts = ssx3_paths(moved)
        self.assertEqual(len(moved_paths), 3)
        self.assertEqual(len(moved_tracks), 1)
        self.assertEqual(moved_starts[0][:2], (1, 1))
        self.assertEqual(moved_starts[0][-2:], (0, 0))
        self.assertEqual(moved_starts[1], starts[1])
        self.assertEqual(moved_starts[0][2:5], (60, 220, 360))
        self.assertAlmostEqual(moved_starts[0][6], 2 ** -.5, places=6)
        self.assertAlmostEqual(moved_starts[0][7], -(2 ** -.5), places=6)
        self.assertEqual(struct.unpack_from('<3f', moved_paths[0], 36), (60, 220, 360))
        self.assertEqual(struct.unpack_from('<3f', moved_tracks[0], 24), (60, 220, 360))
        self.assertEqual(struct.unpack_from('<2I', moved_tracks[0], 16), (2, 0))
        self.assertEqual(movement['freeride_start']['before_position'], (10, 20, 30))
        bad_start = bytearray(donor)
        struct.pack_into('<I', bad_start, 24, 99)
        with self.assertRaisesRegex(ValueError, 'absent path'):
            make_reset_aip(bad_start, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0], 1,
                           original, relocate_start=True)
        oversized = struct.pack('<2I', 0x69696969, 201) + ai[12:] * 201
        oversized += struct.pack('<I', 1) + race + tail
        with self.assertRaisesRegex(ValueError, '200-entry'):
            make_reset_aip(donor, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0], 1, oversized)
        gate_a = struct.pack('<2I6f2I', 0, 0, 0, 0, 0, 1, 0, 0, 0, 0)
        gate_b = struct.pack('<2I6f2I', 1, 0, 0, 4, 0, 1, 0, 0, 0, 0)   # 4 units to the left of gate_a
        raced = original[:-len(tail)] + struct.pack('<2I', 0, 4) + start + other_start + gate_a + gate_b
        moved, report = make_reset_aip(donor, [[0, -2, 0], [2, 0, 0], [0, 0, 2]], [100, 200, 300], 2, raced,
                                       relocate_race_starts=True)
        _, moved_tracks, _, moved_starts = ssx3_paths(moved)
        self.assertEqual(moved_starts[0], ssx3_paths(raced)[3][0])   # freeride start untouched
        centre = [(moved_starts[2][2 + k] + moved_starts[3][2 + k]) / 2 for k in range(3)]
        self.assertEqual([round(v, 6) for v in centre], [60, 220, 360])
        self.assertAlmostEqual(moved_starts[2][6], 2 ** -.5, places=6)
        spacing = ((moved_starts[2][2] - moved_starts[3][2]) ** 2 + (moved_starts[2][3] - moved_starts[3][3]) ** 2) ** .5
        self.assertAlmostEqual(spacing, 8, places=5)   # 4 units scaled by 2, across the new direction
        self.assertEqual(struct.unpack_from('<3f', moved_tracks[0], 24), (60, 220, 360))
        self.assertEqual(report['race_starts']['track_path'], 0)
        for bad in (original[:-1], original + b'\0', original[:20]):
            with self.assertRaises(ValueError):
                ssx3_paths(bad)
        for bad in (donor[:30], donor[:len(ai)], bytes(24)):
            with self.assertRaises(ValueError):
                ai_paths(bad)

    def test_projection_and_distance_follow_corners(self):
        route = Route([(0, 0, 0), (10, 0, 0), (10, 0, 0), (10, 10, 0)])
        self.assertEqual(route.length, 20)
        hit = route.nearest((12, 6, 0))
        self.assertEqual(hit['segment'], 2)
        self.assertAlmostEqual(hit['progress'], 16)
        self.assertAlmostEqual(hit['distance'], 2)
        self.assertEqual(route.at(12), [10, 2, 0])
        self.assertEqual(route.at(40), [10, 10, 0])
        self.assertLess(route.nearest((12, 6, 0), end=1)['progress'], 11)

    def test_placement_anchor_does_not_silently_skip_opening_turn(self):
        paths = [dict(points=[(0, 0, 0), (10, 0, 0), (10, -10, -1), (10, -20, -2)])]
        experiment = dict(matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                          translation=[0, 0, 0], target_anchor=[10, -10, -1])
        points, first = route_points(paths, [0], experiment)
        self.assertEqual(first, 0)
        self.assertEqual(points, [list(p) for p in paths[0]['points']])
        partial, first = route_points(paths, [0], experiment, from_anchor=True)
        self.assertEqual(first, 2)
        self.assertEqual(partial, points[2:])

    def test_tricky_vectors_accumulate_and_bounds_are_checked(self):
        row = struct.pack('<3If2I9f', 1, 0, 4, 100, 2, 1,
                          10, 20, 30, 0, 0, 0, 100, 100, 100)
        row += struct.pack('<8f', 1, 0, -1, 2, 0, 1, 0, 3)
        row += struct.pack('<2I2f', 9, 0, 10, 11)
        data = struct.pack('<8I', 0x0a0a0a0a, 2, 0, 0, 1, 8 + len(row), 1, 0) + row
        path = race_paths(data)[0]
        self.assertEqual(path['points'], [(10, 20, 30), (12, 20, 28), (12, 23, 28)])
        self.assertEqual(path['events'], [(9, 0, 10, 11)])
        for bad in (data[:-1], data + b'\0', data[:20]):
            with self.assertRaises(ValueError):
                race_paths(bad)


if __name__ == '__main__':
    unittest.main()
