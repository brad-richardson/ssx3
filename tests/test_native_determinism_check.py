import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import native_determinism_check as det


def write_trace(path, rows):
    path.write_text(''.join(','.join(map(str, r)) + '\n' for r in rows))


class CompareTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, name, rows):
        folder = self.root / name
        folder.mkdir()
        trace = folder / 'dispatch.csv'
        write_trace(trace, rows)
        (folder / 'determinism.json').write_text(json.dumps(dict(dispatch_trace=str(trace), module_sha256=name)))
        return folder

    def run_compare(self, a, b):
        out = self.root / (a.name + '-' + b.name + '.json')
        args = mock.Mock(a=a, b=b, output=out)
        try:
            det.compare(args)
            code = 0
        except SystemExit as exit:
            code = exit.code
        return code, json.loads(out.read_text())

    def test_identical_traces_pass(self):
        rows = [(1048576 * i, hex(0x80000000 + i), '80000010', '0', '20000000', 1000 * i, 7) for i in range(1, 6)]
        a = self.make('a', rows)
        b = self.make('b', rows)
        code, result = self.run_compare(a, b)
        self.assertEqual(code, 0)
        self.assertEqual(result['verdict'], 'identical over the compared rows')
        self.assertEqual(result['identical_rows'], 5)

    def test_first_divergence_is_located(self):
        rows = [(1048576 * i, hex(0x80000000 + i), '80000010', '0', '20000000', 1000 * i, 7) for i in range(1, 6)]
        other = list(rows)
        other[3] = (rows[3][0], '80001234') + rows[3][2:]
        a = self.make('a', rows)
        b = self.make('b', other)
        code, result = self.run_compare(a, b)
        self.assertEqual(code, 1)
        self.assertEqual(result['first_divergence']['dispatch'], 1048576 * 4)
        self.assertEqual(result['identical_rows'], 3)

    def test_downcount_column_is_ignored(self):
        rows = [(1048576, '80000004', '80000010', '0', '20000000', 1000, 7)]
        other = [(1048576, '80000004', '80000010', '0', '20000000', 1000, 9)]
        code, result = self.run_compare(self.make('a', rows), self.make('b', other))
        self.assertEqual(code, 0)

    def test_offset_traces_compare_on_overlap(self):
        rows = [(1048576 * i, hex(0x80000000 + i), '80000010', '0', '20000000', 1000 * i, 7) for i in range(1, 8)]
        code, result = self.run_compare(self.make('a', rows[:5]), self.make('b', rows[2:]))
        self.assertEqual(code, 0)
        self.assertEqual(result['compared_rows'], 3)
        self.assertEqual(result['identical_rows'], 3)

    def test_empty_traces_fail(self):
        code, result = self.run_compare(self.make('a', []), self.make('b', []))
        self.assertEqual(code, 1)
        self.assertEqual(result['verdict'], 'no overlapping rows')


if __name__ == '__main__':
    unittest.main()
