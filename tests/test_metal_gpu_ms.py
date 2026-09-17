"""Keep the GPU-ms recipe honest without requiring a trace bundle."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import metal_gpu_ms


def row(start, dur, depth, frame, channel, process, ref=None):
    proc = f'<process ref="{ref}"/>' if ref else f'<process id="p{start}" fmt="{process}"><pid>1</pid></process>'
    frame_cell = f"<gpu-frame-number>{frame}</gpu-frame-number>" if frame else "<sentinel/>"
    return (f"<row><start-time>{start}</start-time><duration>{dur}</duration>"
            f'<gpu-channel-name fmt="{channel}"/>{frame_cell}'
            f"<duration>0</duration>"
            f"<metal-nesting-level>{depth}</metal-nesting-level>"
            f"<formatted-label/>"
            f"<gpu-state/><connection-uuid64/><render-buffer-depth/>"
            f"{proc}"
            f"<metal-device-name/><metal-object-label/><formatted-label/>"
            f"<size-in-bytes/><metal-command-buffer-id/><metal-command-buffer-id/>"
            f"<uint64/></row>")


def fixture(rows):
    # Frame numbers ride in the sentinel slot's place when present.
    return ("<?xml version=\"1.0\"?><trace-query-result>" + "".join(rows) +
            "</trace-query-result>")


class GpuMsTests(unittest.TestCase):
    def test_union_counts_nested_intervals_once(self):
        xml = fixture([
            row(0, 1_000_000, 0, "7", "Vertex", "SSXNative (1029)"),
            row(100_000, 200_000, 1, "7", "Vertex", "SSXNative (1029)", ref="p0"),
            row(2_000_000, 500_000, 0, "8", "Fragment", "SSXNative (1029)", ref="p0"),
            row(0, 100_000, 0, "", "Vertex", "backboardd (73)"),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intervals.xml"
            path.write_text(xml)
            report = metal_gpu_ms.summarize(metal_gpu_ms.parse_intervals(path), "SSXNative")
        self.assertEqual(report["intervals"], 3)
        self.assertAlmostEqual(report["gpu_busy_ms"], 1.5)
        self.assertEqual(report["channels_ms"], {"Vertex": 1.0, "Fragment": 0.5})
        self.assertEqual(report["frames"], 2)
        self.assertAlmostEqual(report["per_frame_gpu_ms"]["median"], 0.75)
        self.assertEqual(report["other_processes"][0]["process"], "backboardd (73)")
        self.assertAlmostEqual(report["other_processes"][0]["union_ms"], 0.1)

    def test_missing_process_names_what_was_seen(self):
        xml = fixture([row(0, 1_000_000, 0, "", "Vertex", "backboardd (73)")])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intervals.xml"
            path.write_text(xml)
            rows = metal_gpu_ms.parse_intervals(path)
        with self.assertRaisesRegex(RuntimeError, "backboardd"):
            metal_gpu_ms.summarize(rows, "SSXNative")

    def test_report_from_trace_exports_then_parses(self):
        calls = []

        def fake_export(trace, destination):
            calls.append((str(trace), destination.suffix))
            destination.write_text(fixture(
                [row(0, 2_000_000, 0, "", "Vertex", "SSXNative (1029)")]))
            return destination

        with mock.patch.object(metal_gpu_ms, "export_intervals",
                               side_effect=fake_export):
            with mock.patch.object(metal_gpu_ms.sys, "argv",
                                   ["metal_gpu_ms.py", "report", "--trace", "c.trace",
                                    "--process", "SSXNative"]):
                with mock.patch("builtins.print") as printed:
                    metal_gpu_ms.main()
        self.assertEqual(len(calls), 1)
        report = json.loads(printed.call_args[0][0])
        self.assertAlmostEqual(report["gpu_busy_ms"], 2.0)


if __name__ == "__main__":
    unittest.main()
