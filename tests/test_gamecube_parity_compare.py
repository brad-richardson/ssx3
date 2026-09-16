"""Guest-time-aligned parity reports match, divergence, and tick grouping."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_parity_compare import compare


TB = 40500000 // 60


def row(tb, wall=150, repeat=0, skipped=0, h=1, offs=(), event='update',
        words=None):
    return {'event': event, 'repeat': repeat, 'skipped_update': skipped,
            'wall': wall, 'tb_start': tb, 'tb_end': tb + 100,
            'body_hash_after': h, 'body_offsets': list(offs),
            'body_words': words}


def write(rows):
    f = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False)
    for r in rows:
        f.write(json.dumps(r) + '\n')
    f.close()
    return f.name


class ParityCompareTests(unittest.TestCase):
    def test_identical_replays_report_parity(self):
        tb0 = 10**16
        mk = lambda: [row(tb0 + i * TB, h=100 + i, offs=[240]) for i in range(5)]
        rep = compare(write(mk()), write(mk()))
        self.assertEqual(rep['verdict'], 'parity')
        self.assertEqual(rep['matched_ticks'], 5)
        self.assertEqual(rep['exact_ticks'], 5)

    def test_first_divergence_names_tick_and_offsets(self):
        tb0 = 10**16
        a = [row(tb0 + i * TB, h=100 + i, offs=[240]) for i in range(5)]
        b = [row(tb0 + 7 + i * TB, h=100 + i, offs=[240]) for i in range(5)]
        b[3] = row(tb0 + 7 + 3 * TB, h=999, offs=[240, 256])
        rep = compare(write(a), write(b))
        self.assertEqual(rep['verdict'], 'divergent')
        self.assertEqual(rep['exact_ticks'], 4)
        self.assertEqual(rep['first_divergence']['tick_a'], 3)
        self.assertEqual(rep['first_divergence']['offsets_b'], [240, 256])

    def test_repeat_bodies_group_into_their_tick(self):
        tb0 = 10**16
        base = [row(tb0 + i * TB, h=100 + i) for i in range(3)]
        v1 = [row(tb0 + i * TB, h=100 + i) for i in range(3)]
        v1.insert(1, row(tb0 + 50, repeat=1, h=100))  # tick 0 re-entry, same end hash
        rep = compare(write(base), write(v1))
        self.assertEqual(rep['verdict'], 'parity')
        self.assertEqual(rep['matched_ticks'], 3)

    def test_body_dump_reports_diverged_words(self):
        tb0 = 10**16
        a = [row(tb0, h=1, words=[10, 20, 30, 40])]
        b = [row(tb0, h=2, words=[10, 21, 30, 42])]
        rep = compare(write(a), write(b))
        self.assertEqual(rep['verdict'], 'divergent')
        self.assertEqual(rep['first_divergence']['diverged_word_offsets'], [4, 12])
        self.assertEqual(rep['first_divergence']['diverged_word_count'], 2)

    def test_different_epochs_do_not_align(self):
        a = [row(10**16 + i * TB, h=i) for i in range(4)]
        b = [row(9 * 10**15 + i * TB, h=i) for i in range(4)]
        rep = compare(write(a), write(b))
        self.assertEqual(rep['verdict'], 'unmatched')
        self.assertEqual(rep['matched_ticks'], 0)


if __name__ == '__main__':
    unittest.main()
