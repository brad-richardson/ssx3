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

    def run_compare(self, a, b, strict=False):
        out = self.root / (a.name + '-' + b.name + '.json')
        args = mock.Mock(a=a, b=b, output=out, strict=strict)
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

    def test_duplicate_dispatch_is_rejected(self):
        path = self.root / 'duplicate.csv'
        write_trace(path, [(0, 'a', 'b', 'c', 'd', 0), (0, 'other', 'b', 'c', 'd', 0)])
        with self.assertRaisesRegex(ValueError, 'Duplicate dispatch'):
            det.load_trace(path)

    def strict_pair(self):
        rows = [(i * det.DISPATCH_STRIDE, 'a', 'b', 'c', 'd', i) for i in range(3)]
        folders = [self.make(name, rows) for name in ('a', 'b')]
        for folder in folders:
            path = folder / 'determinism.json'
            data = json.loads(path.read_text())
            data.update(movie_sha256='movie', provenance=dict(cpu_thread=False, runner_sha256='runner',
                        world_archive_sha256='world', core_config_sha256='config'),
                        execution_status=dict(exit_code=0, stopped_on_fault=None),
                        evidence=dict(invalid_memory_accesses=0, gpu_command_errors=0,
                                      module_loaded=True, fallback_jit_runs=0,
                                      unknown_guest_instructions=0, shutdown_counters=dict(smc_failed=0, native=100)))
            path.write_text(json.dumps(data))
        return folders

    def test_strict_control_flow_pass_is_not_gameplay_equivalence(self):
        code, result = self.run_compare(*self.strict_pair(), strict=True)
        self.assertEqual(code, 0)
        self.assertTrue(result['control_flow_gate_passed'])
        self.assertFalse(result['gameplay_equivalence_verified'])

    def test_strict_rejects_matching_tail(self):
        a, b = self.strict_pair()
        for folder in (a, b):
            path = folder / 'dispatch.csv'
            path.write_text('\n'.join(path.read_text().splitlines()[1:]) + '\n')
        code, result = self.run_compare(a, b, strict=True)
        self.assertEqual(code, 1)
        self.assertFalse(result['contiguous_prefix'])

    def test_strict_rejects_mismatched_movie_and_runtime_errors(self):
        a, b = self.strict_pair()
        path = b / 'determinism.json'
        data = json.loads(path.read_text())
        data['movie_sha256'] = 'different'
        data['evidence']['invalid_memory_accesses'] = 1
        path.write_text(json.dumps(data))
        code, result = self.run_compare(a, b, strict=True)
        self.assertEqual(code, 1)
        self.assertIn('Missing or mismatched movie_sha256', result['control_flow_gate_issues'])
        self.assertIn('Run 2: invalid_memory_accesses is missing or nonzero', result['control_flow_gate_issues'])

    def test_observed_transitions_ignore_host_sample_rate(self):
        a, b = self.strict_pair()
        for folder, states in ((a, [0, 0, 3, 3, 0]), (b, [0, 3, 0, 0])):
            (folder / 'rider.jsonl').write_text(''.join(json.dumps(dict(state=s)) + '\n' for s in states))
        code, result = self.run_compare(a, b, strict=True)
        self.assertEqual(code, 0)
        self.assertTrue(result['observed_state_transitions_equal'])
        self.assertFalse(result['gameplay_equivalence_verified'])

    def test_config_normalization_ignores_only_analytics_id_and_checks_receipt(self):
        config = self.root / 'Config/Dolphin.ini'
        config.parent.mkdir()

        def digest(identifier, core='False'):
            config.write_text(f'[Core]\nCPUThread = {core}\n[Analytics]\nID = {identifier}\n')
            return det.comparable_config(dict(profile=str(self.root), core_config_sha256=det.sha256(config)))

        original = digest('a')
        self.assertEqual(original, digest('b'))
        self.assertNotEqual(original, digest('b', 'True'))
        self.assertIsNone(det.comparable_config(dict(profile=str(self.root), core_config_sha256='stale')))

    def test_empty_observations_do_not_claim_matching_gameplay(self):
        a, b = self.strict_pair()
        for folder in (a, b):
            (folder / 'rider.jsonl').write_text('')
        _, result = self.run_compare(a, b, strict=True)
        self.assertIsNone(result['observed_state_transitions_equal'])

    def test_strict_rejects_non_native_execution_and_failed_exit(self):
        a, b = self.strict_pair()
        path = b / 'determinism.json'
        data = json.loads(path.read_text())
        data['evidence'].update(module_loaded=False, fallback_jit_runs=100)
        data['evidence']['shutdown_counters']['native'] = 0
        data['execution_status'] = dict(exit_code=1, stopped_on_fault='invalid access')
        path.write_text(json.dumps(data))
        code, result = self.run_compare(a, b, strict=True)
        self.assertEqual(code, 1)
        self.assertIn('Run 2: native module execution is not established', result['control_flow_gate_issues'])
        self.assertIn('Run 2: fallback_jit_runs is missing or nonzero', result['control_flow_gate_issues'])
        self.assertIn('Run 2: successful exit without a fault is not established', result['control_flow_gate_issues'])

    def test_current_movie_cannot_supply_missing_historical_hash(self):
        a, b = self.strict_pair()
        movie = self.root / 'replaced.dtm'
        movie.write_bytes(b'this might not be the recorded input')
        for folder in (a, b):
            path = folder / 'determinism.json'
            data = json.loads(path.read_text())
            del data['movie_sha256']
            data['movie'] = str(movie)
            path.write_text(json.dumps(data))
        code, result = self.run_compare(a, b, strict=True)
        self.assertEqual(code, 1)
        self.assertFalse(result['control_flow_gate_passed'])
        self.assertEqual(result['provenance'][0]['movie_hash_source'], 'current_file_only')

    def test_finish_preserves_failed_execution_status(self):
        output = self.root / 'run'
        output.mkdir()
        receipt = self.root / 'receipt.json'
        receipt.write_text(json.dumps(dict(exit_code=1, stopped_on_fault='invalid access')))
        with mock.patch.object(det, 'latest_receipt', return_value=(receipt, self.root / 'missing.csv')):
            det.finish(output)
        summary = json.loads((output / 'determinism.json').read_text())
        self.assertEqual(summary['execution_status'], dict(exit_code=1, stopped_on_fault='invalid access'))


if __name__ == '__main__':
    unittest.main()
