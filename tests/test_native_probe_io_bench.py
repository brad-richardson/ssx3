import json
from pathlib import Path
import tempfile
import unittest

from tools.native_probe_io_bench import COUNTERS, instrument_header, normalized_digest, recipes


class NativeProbeIOBenchTests(unittest.TestCase):
    def test_source_change_cannot_silently_instrument_another_flush(self):
        self.assertEqual(instrument_header('void Emit(){\n std::fflush(file);\n}'),
                         'void Emit(){\n ProbeFlush(file);\n}')
        for source in ('void Emit(){}', ' std::fflush(file);\n std::fflush(file);'):
            with self.assertRaises(ValueError):
                instrument_header(source)

    def test_fidelity_ignores_timing_only_and_detects_changed_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'trace.jsonl'
            row = dict(event='render', wall=1, duration_ms=3, cpu_duration_ms=2,
                       body_offsets=[], same_rider=1, state_after=5)
            path.write_text(json.dumps(row)+'\n')
            before = normalized_digest(path)
            row.update(wall=2, duration_ms=4, cpu_duration_ms=None)
            path.write_text(json.dumps(row)+'\n')
            self.assertEqual(before, normalized_digest(path))
            row['body_offsets'] = [240]
            path.write_text(json.dumps(row)+'\n')
            self.assertNotEqual(before, normalized_digest(path))

    def test_missing_final_newline_is_not_a_preserved_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'trace.jsonl'
            path.write_text('{"event":"render"}')
            with self.assertRaises(ValueError):
                normalized_digest(path)

    def test_only_callback_records_and_bounded_offsets_enter_recipes(self):
        row = dict(event='render', repeat=1, result=1, tb_start=100, tb_end=200,
                   app=1000, rider=2000, same_rider=1, view=3000, same_view=1,
                   state_before=5, state_after=5, position_changed=0, rng_changed=0,
                   body_offsets=[], app_offsets=[], view_offsets=[])
        row.update({field: 0 for field in COUNTERS})
        encoded = recipes([dict(event='schedule', action='restore_mode'), row])
        self.assertEqual(len(encoded), 1)
        self.assertTrue(encoded[0].startswith('0 1 1 100 200 '))
        for offset in (0x800, -4, 3):
            row['body_offsets'] = [offset]
            with self.assertRaises(ValueError):
                recipes([row])


if __name__ == '__main__':
    unittest.main()
