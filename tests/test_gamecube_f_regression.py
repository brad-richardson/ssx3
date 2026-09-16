"""F-candidate regression battery: counter rate, repeats, restore, drift."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_f_regression import check_counter, check_repeats, check_restore, check_drift


def row(tb, counter, repeat=0, wall=150):
    words = [0] * 512
    words[12] = counter
    return {'event': 'update', 'repeat': repeat, 'wall': wall,
            'tb_start': tb, 'tb_end': tb + 100, 'body_words': words}


def write_events(rows):
    f = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False)
    for r in rows:
        f.write(json.dumps(r) + '\n')
    f.close()
    return f.name


def write_rider(speeds, dt=0.1):
    f = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False)
    x = 1.0
    for i, s in enumerate(speeds):
        f.write(json.dumps({'t': 100.0 + i * dt, 'wall_time': 1.0 + i * dt,
                            'rider': 1, 'x': x, 'y': 0.0, 'z': 0.0,
                            'state': 0}) + '\n')
        x += s * dt
    f.close()
    return f.name


def load_events(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        e = json.loads(line)
        if e.get('event') == 'update' and e.get('body_words'):
            rows.append(e)
    rows.sort(key=lambda e: e['tb_start'])
    return rows


class CounterRateTests(unittest.TestCase):
    def test_plus_one_per_tick_passes(self):
        rows = load_events(write_events([row(10**16 + i * 675000, 100 + i) for i in range(10)]))
        rep = check_counter(rows)
        self.assertEqual(rep['verdict'], 'pass')
        self.assertEqual(rep['max_step'], 1)

    def test_plus_two_per_tick_fails(self):
        rows = load_events(write_events([row(10**16 + i * 675000, 100 + 2 * i) for i in range(10)]))
        rep = check_counter(rows)
        self.assertEqual(rep['verdict'], 'fail')
        self.assertEqual(rep['violations'][0]['before'], 100)
        self.assertEqual(rep['violations'][0]['after'], 102)

    def test_creation_jump_and_frozen_prefix_pass(self):
        counters = [0, 0, 0, 181, 182, 183, 184]
        rows = load_events(write_events([row(10**16 + i * 675000, c) for i, c in enumerate(counters)]))
        rep = check_counter(rows)
        self.assertEqual(rep['verdict'], 'pass')

    def test_repeat_rows_do_not_count_as_ticks(self):
        rows = [row(10**16 + i * 675000, 100 + i) for i in range(4)]
        rows.insert(2, row(10**16 + 675000 + 50, 101, repeat=1))
        rep = check_counter(load_events(write_events(rows)))
        self.assertEqual(rep['verdict'], 'pass')
        self.assertEqual(rep['ticks'], 4)


class RepeatCountTests(unittest.TestCase):
    def test_exact_count_passes(self):
        rows = [row(10**16 + i * 675000, i) for i in range(3)]
        rows.append(row(10**16 + 50, 0, repeat=1))
        rep = check_repeats(load_events(write_events(rows)), 1)
        self.assertEqual(rep['verdict'], 'pass')

    def test_wrong_count_fails(self):
        rows = [row(10**16 + i * 675000, i) for i in range(3)]
        rep = check_repeats(load_events(write_events(rows)), 1)
        self.assertEqual(rep['verdict'], 'fail')


class RestoreTests(unittest.TestCase):
    def test_full_speed_tail_passes(self):
        rider = write_rider([2000.0] * 400)
        rep = check_restore(rider, 20.0, 2.0)
        self.assertEqual(rep['verdict'], 'pass')

    def test_half_speed_tail_fails(self):
        rider = write_rider([2000.0] * 200 + [900.0] * 200)
        rep = check_restore(rider, 20.0, 2.0)
        self.assertEqual(rep['verdict'], 'fail')
        self.assertAlmostEqual(rep['ratio'], 0.45, places=1)


class DriftTests(unittest.TestCase):
    def test_identical_lines_report_unity(self):
        rider = write_rider([1500.0] * 100)
        rep = check_drift(rider, rider, 0.1)
        self.assertEqual(rep['verdict'], 'pass')
        self.assertAlmostEqual(rep['ratios']['t1.0'], 1.0)

    def test_bound_violation_fails(self):
        base = write_rider([1000.0] * 100)
        fast = write_rider([2000.0] * 100)
        rep = check_drift(fast, base, 0.1)
        self.assertEqual(rep['verdict'], 'fail')
        self.assertGreater(rep['worst_deviation'], 0.9)


if __name__ == '__main__':
    unittest.main()
