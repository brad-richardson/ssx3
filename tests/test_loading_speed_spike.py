import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import loading_speed_spike as spike


class LoadingEvidenceTests(unittest.TestCase):
    def rows(self, fast=False):
        rows = []
        for i, event in enumerate(spike.REQUIRED):
            rows += [dict(event=event, elapsed_seconds=i + 10.,
                          guest_timebase=100000 + i * 40500000),
                     dict(event='loading_config', startup_event=event, fast_disc_speed=fast)]
        return rows

    def test_matching_effective_setting_and_complete_states(self):
        result = spike.analyze_events(self.rows(True), True)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['intervals']['main_menu_loading_to_main_menu_ready'],
                         dict(wall_seconds=1., guest_seconds=1.))

    def test_requested_setting_without_effective_proof_fails(self):
        for value in (None, 'True', 1, False):
            with self.subTest(value=value):
                rows = self.rows(True)
                rows[-1]['fast_disc_speed'] = value
                self.assertFalse(spike.analyze_events(rows, True)['accepted'])

    def test_missing_menu_or_configuration_event_fails(self):
        for remove in (-1, -2):
            rows = self.rows()
            del rows[remove]
            self.assertFalse(spike.analyze_events(rows, False)['accepted'])

    def test_duplicate_or_failed_title_state_is_not_menu_acceptance(self):
        rows = self.rows()
        rows.append(copy.deepcopy(rows[8]))
        self.assertFalse(spike.analyze_events(rows, False)['accepted'])
        rows = self.rows()
        rows[8]['event'] = 'movie_skip_precondition_failed'
        self.assertFalse(spike.analyze_events(rows, False)['accepted'])

    def test_unknown_or_backwards_clock_fails(self):
        for field, value in (('elapsed_seconds', None), ('elapsed_seconds', float('nan')),
                             ('elapsed_seconds', 0), ('guest_timebase', '0'),
                             ('guest_timebase', 0)):
            rows = self.rows()
            rows[-2][field] = value
            self.assertFalse(spike.analyze_events(rows, False)['accepted'])

    def test_only_analytics_identity_is_excluded_from_config(self):
        result = spike.canonical_config('[Analytics]\nID = random\nEnabled = True\n'
                                        '[Core]\nFastDiscSpeed = False\nID = keep\n')
        self.assertEqual(result, {'Analytics': {'Enabled': 'True'},
                                 'Core': {'FastDiscSpeed': 'False', 'ID': 'keep'}})

    def test_copy_observes_effective_setting_without_rewriting_original_logic(self):
        source = 'before\n  std::fflush(output);\nafter\n'
        changed = spike.inject_config_observer(source)
        self.assertIn('Config::Get(Config::MAIN_FAST_DISC_SPEED)', changed)
        self.assertIn('  std::fflush(output);\nafter', changed)
        with self.assertRaises(ValueError):
            spike.inject_config_observer(source + source)


if __name__ == '__main__':
    unittest.main()
