"""Prevent skipped rendering and incomplete traces from looking like 120 Hz."""
from pathlib import Path
import sys
import unittest
import shutil
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_native_trace import summarize
import gamecube_native_trace as native_trace
from gamecube_schedule_check import validate_trial_trace


def event(kind='render', repeat=0, **values):
    row = dict(event=kind, repeat=repeat, wall=150, app=1, rider=2,
               same_rider=1, same_view=1, position_changed=0, rng_changed=0,
               view_offsets=[], body_offsets=[], app_offsets=[],
               state_before=0, state_after=0)
    row.update(values)
    return row


class NativeTraceTests(unittest.TestCase):
    def test_trial_builder_wires_driver_without_game_assets_or_compiler(self):
        class StopBeforeCompile(Exception):
            pass
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory).resolve()
            shutil.copytree(root/'native/diagnostics', temp/'native/diagnostics')
            source = temp/'vendor/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
            source.parent.mkdir(parents=True)
            source.write_text('namespace\n{\n          const u32 runtime_dispatch_address = m_guest.pc;\n}')
            game = temp/'game'
            (game/'sys').mkdir(parents=True)
            (game/'sys/boot.bin').write_bytes(b'GXBE69')
            args = SimpleNamespace(game=game, output=temp/'local/player', scheduler=True,
                                   interpolation=True, replay=False, app_trial_check=True)
            with patch.multiple(native_trace, ROOT=temp, VENDOR=temp/'vendor'), \
                    patch.object(native_trace, 'sha', return_value=native_trace.DOL_SHA256), \
                    patch.object(native_trace.subprocess, 'check_output', side_effect=StopBeforeCompile):
                with self.assertRaises(StopBeforeCompile):
                    native_trace.build(args)
            generated = (args.output/'Core_Run.cpp').read_text()
            self.assertTrue((args.output/'trial_test_driver.h').is_file())
            self.assertEqual((args.output/'callback_timing.h').read_bytes(),
                             (root/'native/diagnostics/callback_timing.h').read_bytes())
            self.assertIn('#define SSX_NATIVE_TRIAL_TEST 1', generated)
            self.assertIn('NativeTrialTest::Step(m_guest)', generated)

    def test_lifecycle_acceptance_requires_events_and_actual_unchanged_extra(self):
        actions = ['request', 'cancel_during_extra', 'quiescent', 'restart', 'quiescent', 'complete']
        rows = [dict(event='trial_test', action=a, wall=i) for i, a in enumerate(actions)]
        with self.assertRaises(RuntimeError):
            validate_trial_trace([])
        with self.assertRaises(RuntimeError):
            validate_trial_trace(rows)
        rows.append(event(repeat=1, result=1, view_matrix_calls=1, frame_end_calls=1))
        self.assertTrue(validate_trial_trace(rows)['lifecycle_complete'])
        with self.assertRaises(RuntimeError):
            validate_trial_trace(rows[1:])
        rows[-1]['rng_changed'] = 1
        with self.assertRaises(RuntimeError):
            validate_trial_trace(rows)

    def test_rejected_call_is_not_a_successful_draw(self):
        counters = dict(gate_calls=1, gate_ready=0, result=0,
                        view_matrix_calls=0, frame_end_calls=0,
                        elapsed_calls=0, queue_calls=0)
        result = summarize([event(), event(repeat=1, **counters)])
        repeat = result['groups']['repeat']
        self.assertEqual(repeat['calls'], 1)
        self.assertEqual(repeat['gate_ready'], 0)
        self.assertEqual(repeat['view_matrix_calls'], 0)
        self.assertEqual(repeat['results'], {'0': 1})
        self.assertEqual(result['repeat_pairing_failures'], 0)

    def test_legacy_trace_cannot_establish_render_coverage(self):
        repeat = summarize([event(), event(repeat=1)])['groups']['repeat']
        self.assertFalse(repeat['render_gate_instrumented'])
        self.assertNotIn('gate_ready', repeat)

    def test_update_between_draws_invalidates_repeat_pair(self):
        result = summarize([event(), event('update'), event(repeat=1)])
        self.assertEqual(result['repeat_pairing_failures'], 1)

    def test_state_pointer_changes_are_not_reported_as_stable(self):
        rows = [event(), event(repeat=1, same_view=0, state_after=4)]
        repeat = summarize(rows)['groups']['repeat']
        self.assertEqual(repeat['view_pointer_changed'], 1)
        self.assertEqual(repeat['state_changed'], 1)
        self.assertEqual(summarize(rows, after=160)['groups']['repeat']['calls'], 0)

    def test_retry_after_rejected_original_is_not_a_second_draw(self):
        complete = dict(result=1, view_matrix_calls=1, frame_end_calls=1)
        rows = [event(result=0), event(repeat=1, **complete)]
        result = summarize(rows)
        self.assertEqual(result['repeat_pairing_failures'], 0)
        self.assertEqual(result['verified_complete_render_pairs'], 0)
        self.assertEqual(result['unverified_or_incomplete_render_pairs'], 1)

    def test_both_calls_need_observed_scene_and_frame_completion(self):
        complete = dict(result=1, view_matrix_calls=1, frame_end_calls=1)
        rows = [event(**complete), event(repeat=1, **complete)]
        self.assertEqual(summarize(rows)['verified_complete_render_pairs'], 1)
        rows[0]['view_matrix_calls'] = 0
        self.assertEqual(summarize(rows)['verified_complete_render_pairs'], 0)

    def test_frozen_sequence_needs_an_original_and_no_intervening_update(self):
        complete = dict(result=1, view_matrix_calls=1, frame_end_calls=1)
        rows = [event(**complete), event(repeat=1, **complete), event(repeat=1, **complete)]
        self.assertEqual(summarize(rows, frozen_sequence=True)['verified_complete_render_pairs'], 2)
        self.assertEqual(summarize(rows)['verified_complete_render_pairs'], 1)
        self.assertEqual(summarize(rows[1:], frozen_sequence=True)['verified_complete_render_pairs'], 0)
        rows.insert(2, event('update'))
        self.assertEqual(summarize(rows, frozen_sequence=True)['verified_complete_render_pairs'], 1)

    def test_update_repeats_need_an_ordinary_update_predecessor(self):
        rows = [event('update'), event('update', repeat=1)]
        result = summarize(rows)
        self.assertEqual(result['update_repeats'], 1)
        self.assertEqual(result['verified_update_repeats'], 1)
        self.assertEqual(result['verified_complete_render_pairs'], 0)
        orphan = summarize([event('render'), event('update', repeat=1)])
        self.assertEqual(orphan['update_repeats'], 1)
        self.assertEqual(orphan['verified_update_repeats'], 0)
        self.assertEqual(result['repeat_pairing_failures'], 0)
        self.assertEqual(result['unverified_or_incomplete_render_pairs'], 0)

    def test_skipped_updates_counted_without_render_pair_pollution(self):
        rows = [event('update'), event('update', skipped_update=1),
                event('update'), event('update', skipped_update=1)]
        result = summarize(rows)
        self.assertEqual(result['skipped_updates'], 2)
        self.assertEqual(result['update_repeats'], 0)
        self.assertEqual(result['repeat_pairing_failures'], 0)
        self.assertEqual(result['unverified_or_incomplete_render_pairs'], 0)
        legacy = summarize([event('update'), event('update')])
        self.assertEqual(legacy['skipped_updates'], 0)

    def test_combo_mode_counts_repeats_and_skips_independently(self):
        rows = [event('update'), event('update', repeat=1),
                event('update', skipped_update=1)]
        result = summarize(rows)
        self.assertEqual(result['update_repeats'], 1)
        self.assertEqual(result['verified_update_repeats'], 1)
        self.assertEqual(result['skipped_updates'], 1)
        self.assertEqual(result['repeat_pairing_failures'], 0)
        self.assertEqual(result['unverified_or_incomplete_render_pairs'], 0)


if __name__ == '__main__':
    unittest.main()
