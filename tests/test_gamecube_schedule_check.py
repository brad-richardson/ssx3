import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_schedule_check import validate_trial_trace

ACTIONS = ['request', 'cancel_during_repeat', 'quiescent', 'restart', 'quiescent',
           'restart2', 'cancel_idle', 'quiescent', 'restart3', 'cancel_combined',
           'quiescent', 'complete']


def lifecycle(blended=5900, loaded=6000, with_loaded=True):
    """A minimal passing lifecycle trace; blend counts are tunable."""
    walls = [100, 110, 120, 200, 210, 300, 310, 320, 400, 410, 420, 430]
    rows = [dict(event='trial_test', action=a, wall=w)
            for a, w in zip(ACTIONS, walls)]
    rows += [dict(event='f_trial', action='patched', wall=150),
             dict(event='f_trial', action='restored', wall=160),
             dict(event='update', wall=155, repeat=1, same_rider=1,
                  state_before=7, state_after=7)]
    extra = dict(event='render', wall=250, repeat=1, result=1,
                 view_matrix_calls=1, frame_end_calls=1, same_rider=1,
                 same_view=1, state_before=7, state_after=7, rng_changed=0,
                 position_changed=0, body_offsets=[], app_offsets=[],
                 view_offsets=[])
    rows.append(extra)
    interp = dict(event='interpolation', wall=250, repeat=1, blended=blended)
    if with_loaded:
        interp['loaded'] = loaded
    rows.append(interp)
    rows.append(dict(event='f_trial', action='restored', wall=330))
    rows.append(dict(extra, wall=450))
    rows.append(dict(interp, wall=450))
    rows.append(dict(event='f_trial', action='restored', wall=460))
    return rows


class ValidateTrialTrace(unittest.TestCase):
    def test_healthy_lifecycle_passes_and_reports_ratios(self):
        result = validate_trial_trace(lifecycle())
        self.assertTrue(result['lifecycle_complete'])
        self.assertAlmostEqual(result['smooth_blend_ratio'], 5900 / 6000)
        self.assertAlmostEqual(result['combined_blend_ratio'], 5900 / 6000)

    def test_camera_only_regression_fails_the_ratio_floor(self):
        with self.assertRaisesRegex(RuntimeError, 'too few matrices'):
            validate_trial_trace(lifecycle(blended=1))

    def test_rows_without_loaded_keep_the_existential_gate(self):
        rows = lifecycle(with_loaded=False)
        result = validate_trial_trace(rows)
        self.assertTrue(result['lifecycle_complete'])
        self.assertIsNone(result['smooth_blend_ratio'])
        self.assertIsNone(result['combined_blend_ratio'])
        stripped = [r for r in rows if r.get('event') != 'interpolation']
        with self.assertRaisesRegex(RuntimeError, 'never blended'):
            validate_trial_trace(stripped)


if __name__ == '__main__':
    unittest.main()
