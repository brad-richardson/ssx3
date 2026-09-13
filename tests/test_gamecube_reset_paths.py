import math
import struct
import unittest

from gamecube_reset_paths import safe_runs, sample_line, compile_reset_paths
from gamecube_terrain import make_record
from course_route import ssx3_paths
from race_course import path_geometry


def fixture(count=1):
    points = [(100, 500, 20), (11900, 500, 20)]
    body = path_geometry(points)
    ai = struct.pack('<9I', 2, 100, 4, 50, 101, 4, 1, 1, 1) + body + b'event preserved!'
    track = struct.pack('<3If2I', 1, 0, 4, 11800, 1, 0) + body
    start = struct.pack('<2I6f2I', 0, 0, *points[0], 1, 0, 0, 0, 0)
    aip = struct.pack('<2I', 0x69696969, count) + ai * count + struct.pack('<I', 1) + track
    aip += struct.pack('<2I', 0, 1) + start
    section = struct.pack('<2I', 0, 0)
    donor = struct.pack('<4I', 0x0a0a0a0a, 2, 0, len(section)) + section
    donor += struct.pack('<4I', 1, 8+len(track), 1, 0) + track
    records = []
    for i in range(3):
        c = [[0., 0., 0.] for _ in range(16)]
        c[15] = [i*4000., 0., 0.]
        c[14] = [4000., 0., 0.]
        c[11] = [0., 1000., 0.]
        p = bytearray(make_record(bytes(430), c, i, 8))
        struct.pack_into('>H', p, 10, 2 if i==1 else 0)
        records.append((dict(kind=1, rid=i, track=8, size=430), bytes(p)))
    return aip, donor, records


class ResetPathTests(unittest.TestCase):
    def test_hazard_gap_stays_disconnected_and_endpoints_have_margin(self):
        points = [(x, 0, 0) for x in range(0, 10001, 100)]
        classify = lambda p: (None, 'hazard') if 4000 <= p[0] <= 6000 else (p, 'safe')
        runs, reasons = safe_runs(points, classify)
        self.assertEqual(len(runs), 2)
        self.assertEqual((runs[0][0][0], runs[0][-1][0]), (300, 3600))
        self.assertEqual((runs[1][0][0], runs[1][-1][0]), (6400, 9700))
        self.assertEqual(reasons['hazard'], 21)

    def test_compile_preserves_indexed_geometry_events_and_starts(self):
        aip, donor, records = fixture()
        out, report = compile_reset_paths(aip, donor, records, [[1,0,0],[0,1,0],[0,0,1]], [0,0,0], 1)
        old = ssx3_paths(aip); new = ssx3_paths(out)
        self.assertEqual(new[1:], old[1:])
        self.assertEqual(new[0][0], old[0][0][:24]+bytes(4)+old[0][0][28:])
        self.assertEqual(report['reset_paths'], 2)
        for p in new[0][1:]:
            low, high = struct.unpack_from('<3f', p, 48), struct.unpack_from('<3f', p, 60)
            self.assertTrue(high[0] < 4000 or low[0] > 8000)
            self.assertEqual(low[2], 10)

    def test_runtime_capacity_fails_before_writing(self):
        aip, donor, records = fixture(199)
        with self.assertRaisesRegex(ValueError, 'slots available'):
            compile_reset_paths(aip, donor, records, [[1,0,0],[0,1,0],[0,0,1]], [0,0,0], 1)

    def test_sampling_bounds_each_segment_and_keeps_final_point(self):
        pts = [(0,0,0),(0,0,500),(500,0,500)]
        out = list(sample_line(pts, 180))
        self.assertEqual(out[-1], pts[-1])
        self.assertTrue(all(math.dist(a,b)<=180 for a,b in zip(out,out[1:])))
