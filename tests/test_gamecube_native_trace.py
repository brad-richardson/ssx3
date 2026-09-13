"""Prevent skipped rendering and incomplete traces from looking like 120 Hz."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_native_trace import summarize


def event(kind='render', repeat=0, **values):
    row = dict(event=kind, repeat=repeat, wall=150, app=1, rider=2,
               same_rider=1, same_view=1, position_changed=0, rng_changed=0,
               view_offsets=[], body_offsets=[], app_offsets=[],
               state_before=0, state_after=0)
    row.update(values)
    return row


class NativeTraceTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
