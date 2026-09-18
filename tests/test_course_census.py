"""Unit tests for the M3 census analysis helpers (no emulator needed)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import course_census as census


def probe_row(event, cpu, **extra):
    row = dict(event=event, repeat=0, rider=1, same_rider=1, state_before=0,
               state_after=0, result=255, view_matrix_calls=3,
               frame_end_calls=1, cpu_duration_ms=cpu)
    row.update(extra)
    return row


class FrameFileTests(unittest.TestCase):
    def test_parse_and_spans(self):
        rows, skipped = census.parse_frame_file('0,10,100\n1,20,200\nbad\n2,30\n3,30,300\n')
        self.assertEqual(rows, [(0, 10, 100), (1, 20, 200), (3, 30, 300)])
        self.assertEqual(skipped, 2)
        spans = census.frame_spans(rows)
        self.assertEqual(len(spans), 2)

    def test_trim_margin(self):
        span = [(i, 10, 100) for i in range(6)]
        self.assertEqual(len(census.trim_span(span, 2)), 2)
        self.assertEqual(census.trim_span(span[:4], 2), [])

    def test_median_p95(self):
        median, p95 = census.median_p95([1, 2, 3, 4, 5])
        self.assertEqual((median, p95), (3, 4))
        self.assertEqual(census.median_p95([]), (None, None))


class ProbeStatsTests(unittest.TestCase):
    def test_riding_filter(self):
        rows = [probe_row('update', 1.0), probe_row('update', 3.0),
                probe_row('render', 10.0), probe_row('render', 12.0),
                probe_row('render', 99.0, repeat=1),
                probe_row('render', 99.0, state_before=6),
                probe_row('render', 99.0, same_rider=0),
                probe_row('render', 99.0, result=0),
                probe_row('update', -1.0)]
        stats = census.probe_riding_stats(rows)
        self.assertEqual(stats['update_n'], 2)
        self.assertEqual(stats['update_cpu_ms_median'], 2.0)
        self.assertEqual(stats['render_n'], 2)
        self.assertEqual(stats['render_cpu_ms_median'], 11.0)

    def test_empty(self):
        stats = census.probe_riding_stats([probe_row('render', 5.0, rider=0)])
        self.assertEqual(stats['render_n'], 0)
        self.assertIsNone(stats['render_cpu_ms_median'])


class RankTests(unittest.TestCase):
    def test_heaviest_first_missing_last(self):
        entries = [
            dict(profile='b', render_cpu_ms_median=5.0, draws_p95=100),
            dict(profile='a', render_cpu_ms_median=9.0, draws_p95=50),
            dict(profile='c', render_cpu_ms_median=None, draws_p95=999),
        ]
        ranked = census.rank_rows(entries)
        self.assertEqual([e['profile'] for e in ranked], ['a', 'b', 'c'])

    def test_manifest_code(self):
        text = '# Snow Jam (ARA1, race)\nevent = 0\ncode = ARA1\nlocation = 0\nmode = 2\n'
        self.assertEqual(census.manifest_code(text), 'ARA1')
        self.assertIsNone(census.manifest_code('event = 0\n'))


if __name__ == '__main__':
    unittest.main()
