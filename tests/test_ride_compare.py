"""Alignment and separation reporting for a pair of native rider traces."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from ride_compare import compare, load, motion_start, pair_by_time, rebase, separation


def row(t, x=0., y=0., z=0.):
    return dict(t=t, x=x, y=y, z=z, state=0, surface=0, terrain_flags=0)


def write(rows, directory, observations=None):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'rider.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    if observations is not None:
        (directory / 'observations.json').write_text(json.dumps(observations))
    return directory


class LoadTests(unittest.TestCase):
    def test_unplaced_rows_are_excluded_but_still_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = write([row(0), row(1, 5), row(2), row(3, 0, 0, 7)], Path(tmp) / 'run')
            rows, placed = load(run)
            self.assertEqual(len(rows), 4)
            self.assertEqual([r['t'] for r in placed], [1, 3])
            self.assertEqual(load(run / 'rider.jsonl')[1], placed)


class PairingTests(unittest.TestCase):
    def test_nearest_in_time_and_each_right_sample_used_once(self):
        left = [row(0), row(1), row(2)]
        right = [row(.02), row(1.01), row(5)]
        pairs = pair_by_time(left, right, .25)
        self.assertEqual([(a['t'], b['t']) for a, b in pairs], [(0, .02), (1, 1.01)])

    def test_window_drops_pairs_that_are_too_far_apart(self):
        self.assertEqual(pair_by_time([row(0)], [row(1)], .25), [])
        self.assertEqual(len(pair_by_time([row(0)], [row(.2)], .25)), 1)

    def test_separation_is_euclidean(self):
        self.assertAlmostEqual(separation(row(0, 3, 4), row(0)), 5.)


class RebaseTests(unittest.TestCase):
    def test_race_start_is_the_first_sample_off_the_spawn(self):
        held = [row(t / 10, x=100) for t in range(5)]
        rolling = [row(.5 + i / 10, x=100 + i * 3) for i in range(1, 4)]
        self.assertEqual(motion_start(held + rolling), 5)
        rebased = rebase(held + rolling, 1.)
        self.assertAlmostEqual(rebased[0]['t'], 0)
        self.assertAlmostEqual(rebased[-1]['t'], .2)
        self.assertEqual(len(rebased), 3)

    def test_a_rider_that_never_moves_is_refused(self):
        with self.assertRaises(ValueError):
            motion_start([row(i, x=7) for i in range(4)])
        with self.assertRaises(ValueError):
            motion_start([])


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.a = write([row(i / 10, x=i) for i in range(1, 21)], self.tmp / 'a',
                       observations={'game': 'g-a', 'profile': 'p-a', 'complete_hazard_resets': 1})
        # Identical for the first ten samples, then a metre per sample apart.
        self.b = write([row(i / 10, x=i + max(0, i - 10)) for i in range(1, 21)], self.tmp / 'b',
                       observations={'game': 'g-b', 'profile': 'p-b'})

    def test_identical_traces_report_zero_separation(self):
        report = compare(self.a, self.a, align='time')
        self.assertTrue(report['identical'])
        self.assertEqual(report['separation_world_units']['max'], 0)
        self.assertIsNone(report['first_beyond_tolerance'])
        self.assertEqual(report['samples']['paired'], 20)

    def test_first_divergence_beyond_tolerance_is_located(self):
        report = compare(self.a, self.b, tolerance=5., align='time')
        self.assertFalse(report['identical'])
        first = report['first_beyond_tolerance']
        self.assertAlmostEqual(first['guest_t'], 1.6)
        self.assertAlmostEqual(first['separation'], 6.)
        self.assertEqual(report['separation_world_units']['within_tolerance'], 15)
        self.assertEqual(report['separation_world_units']['beyond_tolerance'], 5)
        self.assertAlmostEqual(report['separation_world_units']['max'], 10.)

    def test_run_provenance_is_carried_when_observations_exist(self):
        report = compare(self.a, self.b, align='time')
        self.assertEqual(report['a_run']['game'], 'g-a')
        self.assertEqual(report['a_run']['complete_hazard_resets'], 1)
        self.assertIsNone(report['b_run']['complete_hazard_resets'])

    def test_index_alignment_pairs_row_n_with_row_n(self):
        shifted = write([row(i / 10 + 9, x=i) for i in range(1, 21)], self.tmp / 'shifted')
        with self.assertRaises(ValueError):
            compare(self.a, shifted, align='time')
        report = compare(self.a, shifted, align='index')
        self.assertTrue(report['identical'])
        self.assertEqual(report['alignment'], 'row index')

    def test_race_start_alignment_survives_a_late_gate(self):
        """The same ride, held at the spawn 9s longer, must compare as the same ride."""
        late = write([row(i / 10, x=1) for i in range(1, 91)]
                     + [row(9 + i / 10, x=i) for i in range(1, 21)], self.tmp / 'late')
        early = write([row(i / 10, x=1) for i in range(1, 6)]
                      + [row(.5 + i / 10, x=i) for i in range(1, 21)], self.tmp / 'early')
        report = compare(early, late)
        self.assertTrue(report['identical'], report['separation_world_units'])
        self.assertEqual(report['start_separation_world_units'], 0)
        self.assertIn('race start', report['alignment'])
        # Absolute time pairs the moving samples against the other run's hold.
        self.assertFalse(compare(early, late, align='time')['identical'])

    def test_a_trace_without_a_positioned_sample_is_refused(self):
        empty = write([row(0), row(1)], self.tmp / 'empty')
        with self.assertRaises(ValueError):
            compare(self.a, empty, align='time')


if __name__ == '__main__':
    unittest.main()
