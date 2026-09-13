import json
from pathlib import Path
import tempfile
import unittest

from tools.mobile_report import summarize, presentation_summary


class MobileReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        (self.folder / "launch.json").write_text('{"simulator":true}')
        (self.folder / "runtime.log").write_text("")

    def metrics(self, tail="", audio=True):
        rows = []
        for second, fps in [(1, 2), (10, 59), (11, 60), (20, 3)]:
            row = dict(seconds=second, fps=fps, speed=fps/60,
                       footprintBytes=100, thermalState=0,
                       frameIntervalP95ms=18, frameIntervalP99ms=20)
            if audio:
                row["audioDMAEmptyDequeues"] = second*2
            rows.append(json.dumps(row))
        (self.folder / "metrics.jsonl").write_text("\n".join(rows)+"\n"+tail)

    def test_window_excludes_startup_and_missing_audio_is_unknown(self):
        self.metrics()
        result = summarize(self.folder, 9, 12)
        self.assertEqual(result["fps"], dict(min=59, median=59.5, max=60))
        self.assertEqual(result["audio_dma_empty_dequeues_delta"], 2)
        self.assertEqual(result["sample_count"], 2)
        self.metrics(audio=False)
        self.assertIsNone(summarize(self.folder, 9, 12)["audio_dma_empty_dequeues_delta"])

    def test_only_incomplete_final_record_can_be_skipped(self):
        self.metrics(tail='{"seconds":21,')
        self.assertTrue(summarize(self.folder, 9, 12)["incomplete_final_record"])
        self.metrics(tail='{"seconds":21,\n{}\n')
        with self.assertRaises(json.JSONDecodeError):
            summarize(self.folder, 9, 12)

    def test_nonfinite_window_is_rejected(self):
        self.metrics()
        for start, end in [(0, float("inf")), (float("nan"), 20), (3, 2)]:
            with self.assertRaises(ValueError):
                summarize(self.folder, start, end)

    def test_display_time_not_late_callback_time_defines_window(self):
        path = self.folder / 'present.csv'
        path.write_text('submit,1,100.001,640,480\nsubmit,2,100.002,640,480\n'
                        'display,1,102,100.010,0\ndisplay,2,102,100.018,0\n'
                        'submit,3,100.020,640,480\ndisplay,3,102,0,0\n'
                        'submit,4,100.030,640,480\n')
        result = presentation_summary(path, 100, 101)
        self.assertEqual(result['valid_displays'], 2)
        self.assertAlmostEqual(result['display_interval_ms']['median'], 8)
        self.assertEqual(result['zero_display_timestamps'], 1)
        self.assertEqual(result['submits_without_display_callback'], 1)
        self.assertEqual(result['displays_per_second'], 2)

    def test_missing_display_times_and_trace_loss_are_not_success(self):
        path = self.folder / 'present.csv'
        path.write_text('submit,1,100,640,480\ndisplay,1,101,0,0\ndropped,0,102,8,0\n')
        result = presentation_summary(path, 100, 103)
        self.assertIsNone(result['displays_per_second'])
        self.assertFalse(result['trace_complete'])
        path.write_text('display,1,101,100,0\ndisplay,1,102,100,0\n')
        with self.assertRaises(ValueError):
            presentation_summary(path, 100, 103)

    def test_host_window_aligns_across_pause(self):
        self.metrics()
        rows = [json.loads(line) for line in (self.folder / 'metrics.jsonl').read_text().splitlines()]
        for row in rows:
            row['host_seconds'] = row['seconds'] + (100 if row['seconds'] < 11 else 200)
        (self.folder / 'metrics.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows))
        result = summarize(self.folder, 210, 212, 'host')
        self.assertEqual(result['sample_count'], 1)
        self.assertEqual(result['actual_window'], [211, 211])


if __name__ == "__main__":
    unittest.main()
