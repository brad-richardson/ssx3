"""Countdown staging must preserve active course data and executable guards."""
from pathlib import Path
import struct
import tempfile
import unittest

from tests.test_gamecube_scenery import fixture  # Adds tools to sys.path.
from gamecube_startgate import append_hidden_bindings
from gamecube_startgate_trace import read_observations, summarize


def script_fixture():
    script = bytearray(172)
    script[:4] = bytes.fromhex('00100000')
    struct.pack_into('>3I', script, 56, 1, 92, 132)
    struct.pack_into('>I', script, 92, 96)
    script[96:132] = bytes.fromhex(
        '004e554c0000001400000024000000242aff0000ffffffec000000000000000200000000')
    struct.pack_into('>7I', script, 64, 132, 1, 160, 1, 164, 1, 168)
    script[132:160] = struct.pack('>4I3f', 0, 0x10000, 0xffffffff, 0xffffffff, 0, 0, 0)
    script[168:172] = bytes.fromhex('0003000a')
    return script


class StartgateTests(unittest.TestCase):
    def test_hidden_additions_preserve_existing_programs_definitions_and_splines(self):
        original = script_fixture()
        changed, report = append_hidden_bindings(original, 1, 3)
        self.assertFalse(report['initially_visible'])
        self.assertFalse(report['collision'])
        self.assertEqual(changed[92:160], original[92:160])
        count, table, definitions, offsets, splines, spline_at = struct.unpack_from('>6I', changed, 68)
        self.assertEqual((count, definitions, splines), (4, 2, 1))
        self.assertEqual(struct.unpack_from('>4H', changed, table), (0, 1, 1, 1))
        self.assertEqual(struct.unpack_from('>2I', changed, offsets), (0, 28))
        self.assertEqual(struct.unpack_from('>4I', changed, 160), (0, 0, 0xffffffff, 0xffffffff))
        self.assertEqual(changed[spline_at:], original[168:])

    def test_rejects_live_programs_and_incorrect_instance_ownership(self):
        original = script_fixture()
        with self.assertRaisesRegex(ValueError, 'extents'):
            append_hidden_bindings(original, 2, 3)
        original[112] = 0x27
        with self.assertRaisesRegex(ValueError, 'Disable host course programs'):
            append_hidden_bindings(original, 1, 3)

    def test_rejects_invalid_definition_reference(self):
        original = script_fixture()
        struct.pack_into('>H', original, 160, 1)
        with self.assertRaisesRegex(ValueError, 'definition indices'):
            append_hidden_bindings(original, 1, 3)

    def test_observer_cap_cannot_be_mistaken_for_event_absence(self):
        lookup = dict(stage='event_lookup', ticks=10, r4=8, r5=0x0dfb527e)
        value = dict(stage='event_value', ticks=11, value_type=0)
        report = summarize([lookup, value]*500)
        self.assertEqual(len(report['truncated_translation_units']), 1)
        self.assertEqual(report['named_lookups'][0]['hash'], 0x0dfb527e)
        self.assertFalse(report['named_lookups'][0]['callback'])

    def test_countdown_window_comes_from_the_first_dispatch_of_each_event(self):
        rows = [dict(stage='startlight_begin', ticks=0, r4=0x0ebf88fe),
                dict(stage='startgate_open', ticks=405000, r4=0x0dfb527e),
                dict(stage='startgate_open', ticks=810000, r4=0x0dfb527e)]
        self.assertAlmostEqual(summarize(rows)['countdown_window_seconds'], 0.01)
        self.assertIsNone(summarize(rows[:1])['countdown_window_seconds'])

    def test_rejects_a_dispatch_whose_event_hash_does_not_match(self):
        rows = [dict(stage='startgate_open', ticks=0, r4=0x0ebf88fe)]
        with self.assertRaisesRegex(ValueError, 'event hash'):
            summarize(rows)

    def test_reads_observer_lines_only_and_requires_at_least_one(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory)/'runtime.log'
            log.write_text('noise\n[ssx-startgate] {"stage":"event_lookup","ticks":1}\nmore\n')
            self.assertEqual(read_observations(log), [dict(stage='event_lookup', ticks=1)])
            log.write_text('runtime output with no observations\n')
            with self.assertRaisesRegex(ValueError, 'No countdown observations'):
                read_observations(log)


if __name__ == '__main__':
    unittest.main()
