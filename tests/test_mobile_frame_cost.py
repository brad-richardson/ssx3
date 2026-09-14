import json
import tempfile
import unittest
from pathlib import Path

import mobile_frame_cost as cost


def row(seconds, draws, frames=60, speed=1.0, fps=60.0, update=None, render=None, thermal=0):
    r = dict(seconds=seconds, fps=fps, speed=speed, thermalState=thermal, footprintBytes=400 << 20,
             audioDMAEmptyDequeues=0, maxSpeedExcludingThrottle=1.2,
             workload=dict(frameEvents=frames, drawCalls=draws * frames, primitives=5000 * frames, vertexBytes=2048 * 1024 * frames))
    if update is not None:
        r['callbackTiming'] = dict(update=dict(count=60, cpuMedianMs=update, cpuP95Ms=update + .5, wallMedianMs=update, wallP95Ms=update + .5),
                                   render=dict(count=60, cpuMedianMs=render, cpuP95Ms=render + 1, wallMedianMs=render, wallP95Ms=render + 1),
                                   cpuThread=True)
    return r


class FrameCostTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.session = Path(self.tmp.name)
        (self.session / 'launch.json').write_text(json.dumps(dict(appBuild='abcdef0123', cpuThread=True, outputWidth=1434, outputHeight=660, outputScale=.5, requestedInternalScale=2)))

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rows):
        (self.session / 'metrics.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))

    def test_menu_rows_are_excluded_and_slow_rows_counted(self):
        self.write([row(1, 5), row(2, 20), row(3, 500, update=3.3, render=7.8), row(4, 900, speed=.9, fps=54, update=3.5, render=12.8),
                    row(5, 480, update=3.2, render=7.5)])
        summary, rows, riding, slow = cost.summarize(self.session, 100)
        self.assertEqual(summary['riding_rows'], 3)
        self.assertEqual(summary['slow_rows'], 1)
        self.assertAlmostEqual(summary['update_cpu_median_ms'], 3.3)
        self.assertAlmostEqual(summary['render_cpu_median_ms'], 7.8)
        self.assertEqual(summary['cpu_thread'], True)
        self.assertAlmostEqual(summary['draw_calls_per_frame_median'], 500)

    def test_missing_timing_is_none_not_zero(self):
        self.write([row(1, 500), row(2, 500)])
        summary, *_ = cost.summarize(self.session, 100)
        self.assertIsNone(summary['update_cpu_median_ms'])
        self.assertEqual(summary['riding_rows'], 2)

    def test_comparison_filters_use_actual_settings_and_thermal(self):
        rows = [row(i, 500, update=3, render=8) for i in range(6)]
        for r in rows:
            r.update(trialStatus=0, requestedInternalScale=2, outputScale=.5)
        rows[1]['thermalState'] = 2
        rows[2]['trialStatus'] = 1
        rows[3]['requestedInternalScale'] = 3
        rows[4]['outputScale'] = 1
        del rows[5]['trialStatus']
        self.write(rows)
        summary, _, riding, _ = cost.summarize(self.session, 100, dict(
            ordinary_only=True, max_thermal=0, internal_scale=2, output_scale=.5))
        self.assertEqual(len(riding), 1)
        self.assertEqual(summary['excluded_riding_rows'], 5)
        self.assertEqual(summary['observed_configurations'], [dict(internal_scale=2, output_scale=.5,
                                                                 cpu_thread=True, rows=1)])

    def test_unfiltered_report_exposes_mixed_settings(self):
        rows = [row(1, 500), row(2, 500)]
        rows[0].update(requestedInternalScale=2, outputScale=.5)
        rows[1].update(requestedInternalScale=4, outputScale=1)
        self.write(rows)
        summary, *_ = cost.summarize(self.session, 100)
        self.assertEqual(len(summary['observed_configurations']), 2)

    def test_audio_deltas_do_not_cross_excluded_rows_or_clock_gaps(self):
        rows = [row(t, 500) for t in (1, 2, 3, 4, 10)]
        for r, count in zip(rows, (0, 100, 100, 101, 500)):
            r.update(trialStatus=0, audioDMAEmptyDequeues=count)
        rows[1]['trialStatus'] = 1
        self.write(rows)
        summary, *_ = cost.summarize(self.session, 100, dict(ordinary_only=True))
        self.assertEqual(summary['audio_empty_dequeues_delta'], 1)
        self.assertEqual(summary['audio_observed_intervals'], 1)


if __name__ == '__main__':
    unittest.main()
