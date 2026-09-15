"""Pairing two arms' screenshots by rider position, not by clock or index."""
import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import frame_match


class MovingTests(unittest.TestCase):
    def rows(self, positions, start=1000.0):
        return [{'x': x, 'y': y, 'z': z, 't': start + i, 'wall_time': start + i}
                for i, (x, y, z) in enumerate(positions)]

    def test_the_pre_start_hold_is_dropped(self):
        rows = self.rows([(0, 0, 0)] * 0 + [(10, 10, 10)] * 3 + [(10, 10, 5000)])
        moving = frame_match.moving(rows)
        self.assertEqual(len(moving), 1)
        self.assertEqual(moving[0]['z'], 5000)

    def test_a_run_that_never_moves_is_returned_whole(self):
        rows = self.rows([(10, 10, 10)] * 4)
        self.assertEqual(len(frame_match.moving(rows)), 4)

    def test_the_threshold_is_in_guest_units(self):
        rows = self.rows([(0, 0, 0), (0, 0, 100), (0, 0, 600)])
        self.assertEqual(frame_match.moving(rows, threshold=500.0)[0]['z'], 600)
        self.assertEqual(frame_match.moving(rows, threshold=50.0)[0]['z'], 100)


class PairTests(unittest.TestCase):
    """A synthetic pair of runs: same trajectory, different screenshot times."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.profiles = self.root / 'local/native/profiles'

    def tearDown(self):
        self.tmp.cleanup()

    def arm(self, name, wall_start, positions, shot_indices):
        run = self.root / name
        run.mkdir(parents=True)
        rows = []
        for i, (x, y, z) in enumerate(positions):
            rows.append({'x': x, 'y': y, 'z': z, 't': 100.0 + i,
                         'wall_time': wall_start + i})
        (run / 'rider.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
        shots = self.profiles / name / 'ScreenShots/GXBE69'
        shots.mkdir(parents=True)
        for i in shot_indices:
            stamp = datetime.datetime.fromtimestamp(wall_start + i).strftime('%Y-%m-%d_%H-%M-%S')
            (shots / f'GXBE69_{stamp}.png').write_bytes(b'')
        return run

    def test_frames_pair_by_position_across_a_time_offset(self):
        track = [(0, 0, 0)] + [(1000 * i, 0, 0) for i in range(1, 12)]
        a = self.arm('arm-a', 1_000_000, track, [2, 5, 9])
        b = self.arm('arm-b', 2_000_000, track, [3, 5, 8])   # different clock, slower
        original = Path.cwd()
        import os
        os.chdir(self.root)
        try:
            got = frame_match.pairs(str(a), 'arm-a', str(b), 'arm-b', count=3)
        finally:
            os.chdir(original)
        self.assertEqual(len(got), 3)
        # The closest pair is exact, because both arms hold the same positions.
        self.assertLess(got[0][0], 1.0)
        # Later pairs are spread along the course, so they settle for the
        # nearest frame that exists rather than an exact position.
        for distance, _, _, _, _ in got:
            self.assertLess(distance, 1500.0)
        chosen = [tuple(x) for _, x, _, _, _ in got]
        self.assertEqual(len(set(chosen)), 3)


if __name__ == '__main__':
    unittest.main()
