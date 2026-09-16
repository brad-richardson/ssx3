"""Keep GPU-trace capture honest without requiring a device."""
import argparse
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import metal_capture


def capture_args(**overrides):
    values = dict(device="IPAD", sequence=Path("seq.json"), template="Metal System Trace",
                  attach_delay=160, window=60, output=None, internal_scale=1,
                  cpu_thread=True, single_core=False, smoothing_at=155.0,
                  f_at=None, combo_at=None, textures="remaster",
                  preload_textures="on", course_manifest=None)
    values.update(overrides)
    return argparse.Namespace(**values)


class MetalCaptureTests(unittest.TestCase):
    def test_record_command_attaches_by_process_name_with_bounds(self):
        self.assertEqual(
            metal_capture.build_record_command(device="IPAD", template="Metal System Trace",
                                               window=60, output=Path("/tmp/c.trace")),
            ["xctrace", "record", "--template", "Metal System Trace", "--device", "IPAD",
             "--attach", "SSXNative", "--time-limit", "60s",
             "--no-prompt", "--output", "/tmp/c.trace"])

    def test_check_passes_on_clean_probe_and_fails_dirty(self):
        ok = SimpleNamespace(returncode=0, stderr="")
        self.assertTrue(metal_capture.check_device("IPAD", run=lambda *a, **k: ok))
        bad = SimpleNamespace(returncode=1, stderr="no DDI")
        with self.assertRaises(RuntimeError):
            metal_capture.check_device("IPAD", run=lambda *a, **k: bad)

    def test_capture_rejects_nonsense_window(self):
        with self.assertRaises(ValueError):
            metal_capture.capture(capture_args(window=0))
        with self.assertRaises(ValueError):
            metal_capture.capture(capture_args(attach_delay=-1))

    def test_capture_drives_launch_record_collect_and_receipt(self):
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp) / "cap"
            trace = outdir / "capture.trace"
            seq = Path(tmp) / "seq.json"
            seq.write_text("{}")
            args = capture_args(sequence=seq, output=outdir)
            record = SimpleNamespace(returncode=0, stderr="")

            def fake_run(cmd, **kwargs):
                calls.append(cmd[1])
                trace.write_bytes(b"trace-bytes")
                return record

            with mock.patch.object(metal_capture.mobile_gamecube, "launch") as launch, \
                    mock.patch.object(metal_capture.mobile_gamecube, "collect") as collect, \
                    mock.patch.object(metal_capture.time, "sleep") as sleep:
                receipt = metal_capture.capture(args, clock=sleep, run=fake_run)
            launch.assert_called_once()
            sent = launch.call_args[0][0]
            self.assertEqual(sent.device, "IPAD")
            self.assertEqual(sent.smoothing_at, 155.0)
            self.assertEqual(sent.preload_textures, "on")
            sleep.assert_called_once_with(160)
            collect.assert_called_once()
            self.assertEqual(calls, ["record"])
            saved = json.loads((outdir / "receipt.json").read_text())
            self.assertEqual(saved["trace_sha256"], receipt["trace_sha256"])
            self.assertEqual(saved["run_flags"]["textures"], "remaster")

    def test_capture_surfaces_xctrace_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp) / "cap"
            seq = Path(tmp) / "seq.json"
            seq.write_text("{}")
            args = capture_args(sequence=seq, output=outdir)
            record = SimpleNamespace(returncode=1, stderr="attach refused")
            with mock.patch.object(metal_capture.mobile_gamecube, "launch"), \
                    mock.patch.object(metal_capture.mobile_gamecube, "collect") as collect:
                with self.assertRaises(RuntimeError):
                    metal_capture.capture(args, clock=lambda s: None,
                                          run=lambda *a, **k: record)
                collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
