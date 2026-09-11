import json
from pathlib import Path
import tempfile
import unittest

from tools.mobile_report import summarize


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


if __name__ == "__main__":
    unittest.main()
