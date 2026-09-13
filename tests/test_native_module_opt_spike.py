from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from tools.native_module_opt_spike import (
    audit_callback_evidence, core_config_without_analytics_id, module_flags, runtime_receipt,
)


class ModuleOptSpikeTests(unittest.TestCase):
    def check_flags(self, flags, level):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'build.ninja'
            path.write_text('build CMakeFiles/gGXBE69_recomp.dir/chunk.c.o: COMPILE chunk.c\n'
                            '  FLAGS = '+flags+'\n\n')
            return module_flags(path, level)

    def test_last_opt_flag_wins_not_release_prefix(self):
        flags = '-O3 -DNDEBUG -flto=thin -O2 -ffp-contract=off -fno-fast-math'
        self.assertEqual(self.check_flags(flags, 2)['object_count'], 1)
        with self.assertRaisesRegex(ValueError, 'Effective compiler optimization'):
            self.check_flags(flags, 3)

    def test_strict_fp_and_actual_thinlto_are_required(self):
        flags = '-O3 -flto=thin -ffp-contract=off -fno-fast-math'
        for removed in ('-flto=thin', '-ffp-contract=off', '-fno-fast-math'):
            with self.assertRaises(ValueError):
                self.check_flags(flags.replace(removed, ''), 3)
        with self.assertRaises(ValueError):
            self.check_flags(flags+' -ffast-math', 3)

    def test_actual_runtime_module_and_player_must_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root/'local/reports/native-runs'
            reports.mkdir(parents=True)
            case = root/'case'
            case.mkdir()
            log = reports/'run.log'
            (case/'runtime.log').write_text('Log: '+str(log)+'\n')
            receipt = dict(module_sha256='o2', runner_sha256='common', evidence={},
                           core_config_sha256='config', world_archive_sha256='world')
            log.with_suffix('.json').write_text(json.dumps(receipt))
            with patch('tools.native_module_opt_spike.ROOT', root):
                self.assertEqual(runtime_receipt(case, 'o2', 'common')['module_sha256'], 'o2')
                for module, player in (('o3', 'common'), ('o2', 'other')):
                    with self.assertRaisesRegex(ValueError, 'Actual executed'):
                        runtime_receipt(case, module, player)

    def test_runtime_receipt_cannot_point_outside_native_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            case = Path(directory)
            (case/'runtime.log').write_text('Log: '+str(case/'unexpected.log')+'\n')
            with self.assertRaisesRegex(ValueError, 'outside the native report'):
                runtime_receipt(case, 'o2', 'common')

    def test_unknown_watched_fields_and_observer_warnings_remain_visible(self):
        row = dict(event='render', repeat=1, position_changed=0, rng_changed=0,
                   same_rider=1, same_view=1, state_before=0, state_after=0,
                   body_offsets=[], app_offsets=[], view_offsets=[])
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory)/'trace.jsonl'
            trace.write_text(json.dumps(row)+'\n'+json.dumps(dict(row, body_offsets=None))+'\n')
            result = audit_callback_evidence(trace, 'Unable to resolve read address 803da1f8 PC 958\n')
            self.assertEqual(result['callback_count'], 2)
            self.assertEqual(result['unknown_watched_callbacks'], 1)
            self.assertEqual(result['unresolved_address_warning_count'], 1)
            self.assertEqual(result['changed_extra_callbacks'], 0)
            trace.write_text(json.dumps(row))
            self.assertTrue(audit_callback_evidence(trace, '')['trace_issues'])

    def test_config_comparison_ignores_only_analytics_nonce(self):
        text = '[Core]\nCPUCore = 4\nID = retained\n[Analytics]\nID = nonce-a\nEnabled = False\n'
        canonical = core_config_without_analytics_id(text)
        self.assertEqual(canonical, core_config_without_analytics_id(text.replace('nonce-a', 'nonce-b')))
        self.assertIn('ID = retained', canonical)
        for before, after in (('CPUCore = 4', 'CPUCore = 1'), ('Enabled = False', 'Enabled = True')):
            self.assertNotEqual(canonical, core_config_without_analytics_id(text.replace(before, after)))


if __name__ == '__main__':
    unittest.main()
