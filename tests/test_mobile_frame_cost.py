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


if __name__ == '__main__':
    unittest.main()
