"""Race-course conversion helpers on synthetic paths (no game bytes)."""
import math
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from race_course import (build_track, track_points, chain_tracks, race_line_table, point_along,  # noqa: E402
                         convert_race_course, race_markers, select_donor_starts,
                         FINISH_EVENT, CHECKPOINT_EVENT)


def straight(x0, n, step=100.0, y=0.0):
    return [(x0 + step * i, y, 0.0) for i in range(n + 1)]


class RaceCourseTests(unittest.TestCase):
    def test_track_round_trip_and_chain_stops_at_finish(self):
        a = build_track((1, 0, 4), straight(0, 3), 700.0, [])
        b = build_track((1, 0, 4), straight(300, 4), 400.0, [(FINISH_EVENT, 0, 350.0, 350.0)])
        c = build_track((1, 0, 4), straight(700, 2), 0.0, [])
        header, points, lengths, events = track_points(b)
        self.assertEqual(header, (1, 0, 4, 400.0))
        self.assertEqual([round(p[0]) for p in points], [300, 400, 500, 600, 700])
        self.assertEqual(lengths, [100.0] * 4)
        self.assertEqual(events, [(FINISH_EVENT, 0, 350.0, 350.0)])
        self.assertEqual(chain_tracks([a, b, c], 0), [0, 1])

    def test_race_line_table_layout(self):
        table = race_line_table([straight(0, 2), straight(200, 2)], 350.0)
        count, stride, two, size = struct.unpack_from('>4I', table)
        self.assertEqual((count, stride, two, size), (5, 20, 2, len(table) - 16))
        nodes = [struct.unpack_from('>5f', table, 16 + 20 * i) for i in range(count)]
        # node 0 carries the total; node i the cumulative distance of node i-1; normals are (-dy, dx).
        self.assertEqual([n[0] for n in nodes], [350.0, 0.0, 100.0, 200.0, 300.0])
        self.assertEqual([n[1:3] for n in nodes], [(0.0, 1.0)] * 5)
        self.assertEqual([n[3] for n in nodes], [0.0, 100.0, 200.0, 300.0, 350.0])
        self.assertEqual(struct.unpack_from('>3fIf', table, len(table) - 20), (350.0, 0.0, 0.0, 2, 350.0))
        with self.assertRaises(ValueError):
            race_line_table([straight(0, 2)], 500.0)

    def test_point_along_interpolates(self):
        self.assertEqual(point_along(straight(0, 2), 150.0), (150.0, 0.0, 0.0))
        self.assertEqual(point_along(straight(0, 2), 900.0), (200.0, 0.0, 0.0))

    def test_convert_race_course_moves_gates_and_chains_segments(self):
        races = [dict(index=0, points=straight(0, 4), events=[]),
                 dict(index=1, points=straight(400, 4), events=[(11, 60, 200.0, 200.0)]),
                 dict(index=2, points=straight(800, 4), events=[(9, 0, 300.0, 300.0)]),
                 dict(index=3, points=straight(5000, 2), events=[])]
        donor_ai = [dict(index=0, fields=(2,) * 7, points=[(0, -50, 0), (100, -50, 0)]),
                    dict(index=1, fields=(2,) * 7, points=[(0, 50, 0), (100, 50, 0)])]
        old_tracks = [build_track((1, 0, 4), straight(0, 2), 400.0, []),
                      build_track((1, 0, 4), straight(200, 2), 200.0, [(FINISH_EVENT, 0, 150.0, 150.0)])]
        starts = [(0, 0, 10.0, 30.0, 0.0, 1.0, 0.0, 0.0, 7, 0), (1, 0, 10.0, -30.0, 0.0, 1.0, 0.0, 0.0, 8, 0),
                  (1, 1, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 9, 1)]
        tail = struct.pack('<I', 0) + struct.pack('<I', len(starts)) + b''.join(struct.pack('<2I6f2I', *s) for s in starts)
        tracks, new_tail, assign, table, report = convert_race_course(
            races, donor_ai, [0, 1], lambda p: tuple(p), 1.0, old_tracks, starts, tail)
        self.assertEqual(report['track_chain'], [0, 1])
        self.assertEqual(report['donor_race_chain'], [0, 1, 2])
        # Segments 1 and 2 fold into the last track; finish 300 units into segment 2.
        self.assertEqual([round(x) for x in report['track_lengths']], [400, 800])
        self.assertAlmostEqual(report['finish_distance'], 1100.0)
        h0, p0, _, e0 = track_points(tracks[0])
        h1, p1, _, e1 = track_points(tracks[1])
        self.assertAlmostEqual(h0[3], 1100.0)
        self.assertAlmostEqual(h1[3], 700.0)
        self.assertEqual(len(p1), 9)
        self.assertEqual(e0, [])
        self.assertEqual(e1, [(CHECKPOINT_EVENT, 0, 200.0, 200.0), (FINISH_EVENT, 0, 700.0, 700.0)])
        self.assertEqual(struct.unpack_from('>I', table)[0], 1 + 4 + 4 + 3)
        # Gates pair by lateral order: the +y gate gets the +y donor path.
        self.assertEqual(assign, {7: 1, 8: 0})
        moved = struct.unpack_from('<2I6f2I', new_tail, 8)
        self.assertEqual(moved[2:5], (0.0, 50.0, 0.0))
        self.assertEqual(moved[5:8], (1.0, 0.0, 0.0))
        with self.assertRaises(ValueError):
            convert_race_course(races, donor_ai, [0], lambda p: p, 1.0, old_tracks, starts, tail)

    def test_slopestyle_markers_extend_the_trailer(self):
        self.assertEqual(race_markers(100.0), [(0, 0.0), (2, 100.0)])
        with self.assertRaises(ValueError):
            race_markers(100.0, 'race', (0.5, 0.5))
        with self.assertRaises(ValueError):
            race_markers(100.0, 'slopestyle', (0.5,))
        with self.assertRaises(ValueError):
            race_markers(100.0, 'slopestyle', (0.5, 1.5))
        markers = race_markers(200.0, 'slopestyle', (0.25, 0.75))
        self.assertEqual(markers, [(0, 0.0), (2, 200.0), (1, 50.0), (1, 150.0)])
        race = race_line_table([straight(0, 2), straight(200, 2)], 350.0)
        slope = race_line_table([straight(0, 2), straight(200, 2)], 350.0,
                                race_markers(350.0, 'slopestyle', (0.25, 0.75)))
        # Only the trailer differs: same node count, same nodes, b=4 and 16 more bytes.
        self.assertEqual(race[16:-20], slope[16:-36])
        self.assertEqual(struct.unpack_from('>4I', slope), (5, 20, 4, len(slope) - 16))
        self.assertEqual(struct.unpack_from('>f3Ifff', slope, len(slope) - 36)[0], 350.0)
        trailer = [struct.unpack_from('>If', slope, len(slope) - 32 + 8 * i) for i in range(4)]
        self.assertEqual(trailer, [(0, 0.0), (2, 350.0), (1, 87.5), (1, 262.5)])

    def test_select_donor_starts_keeps_the_outer_lanes(self):
        self.assertEqual(select_donor_starts([0, 1, 2, 3, 4, 5], 6), [0, 1, 2, 3, 4, 5])
        self.assertEqual(select_donor_starts([0, 1, 2, 3, 4, 5], 3), [0, 2, 5])
        self.assertEqual(select_donor_starts([0, 1, 2, 3, 4, 5], 2), [0, 5])
        self.assertEqual(select_donor_starts([0, 1, 2, 3, 4, 5], 1), [0])
        with self.assertRaises(ValueError):
            select_donor_starts([0, 1], 3)

    def test_fewer_gates_than_donor_lanes_and_a_slopestyle_trailer(self):
        races = [dict(index=0, points=straight(0, 4), events=[]),
                 dict(index=1, points=straight(400, 4), events=[(11, 60, 200.0, 200.0),
                                                                (11, 60, 300.0, 300.0)]),
                 dict(index=2, points=straight(800, 4), events=[(9, 0, 300.0, 300.0)])]
        donor_ai = [dict(index=i, fields=(2,) * 7,
                         points=[(0, -50 + 20 * i, 0), (100, -50 + 20 * i, 0)]) for i in range(6)]
        old_tracks = [build_track((1, 0, 4), straight(0, 2), 400.0, []),
                      build_track((1, 0, 4), straight(200, 2), 200.0, [(FINISH_EVENT, 0, 150.0, 150.0)])]
        starts = [(0, 0, 10.0, 30.0, 0.0, 1.0, 0.0, 0.0, 7, 0), (1, 0, 10.0, -30.0, 0.0, 1.0, 0.0, 0.0, 8, 0),
                  (1, 1, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 9, 1)]
        tail = struct.pack('<I', 0) + struct.pack('<I', len(starts)) + b''.join(
            struct.pack('<2I6f2I', *s) for s in starts)
        tracks, new_tail, assign, table, report = convert_race_course(
            races, donor_ai, [0, 1, 2, 3, 4, 5], lambda p: tuple(p), 1.0, old_tracks, starts, tail,
            checkpoint_limit=1, race_line_kind='slopestyle', marker_fractions=(0.25, 0.75))
        # Two gates against six donor lanes: the outer lanes are kept.
        self.assertEqual(report['selected_donor_start_indices'], [0, 5])
        self.assertEqual(sorted(assign.values()), [0, 5])
        self.assertEqual(struct.unpack_from('>I', table, 8)[0], 4)
        self.assertEqual(report['race_line_markers'][2:],
                         [(1, report['finish_distance'] * 0.25), (1, report['finish_distance'] * 0.75)])
        # checkpoint_limit=1 keeps one of the donor's two checkpoint events.
        self.assertEqual([e for e in track_points(tracks[1])[3] if e[0] == CHECKPOINT_EVENT],
                         [(CHECKPOINT_EVENT, 0, 200.0, 200.0)])


if __name__ == '__main__':
    unittest.main()
