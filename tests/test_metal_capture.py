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
    def test_record_command_attaches_by_pid_with_bounds(self):
        self.assertEqual(
            metal_capture.build_record_command(device="IPAD", template="Metal System Trace",
                                               window=60, output=Path("/tmp/c.trace"), pid=4242),
            ["xctrace", "record", "--template", "Metal System Trace", "--device", "IPAD",
             "--attach", "4242", "--time-limit", "60s",
             "--no-prompt", "--output", "/tmp/c.trace"])

    def test_record_command_all_processes_skips_attach(self):
        self.assertEqual(
            metal_capture.build_record_command(device="IPAD", template="Metal System Trace",
                                               window=60, output=Path("/tmp/c.trace"),
                                               all_processes=True),
            ["xctrace", "record", "--template", "Metal System Trace", "--device", "IPAD",
             "--all-processes", "--time-limit", "60s",
             "--no-prompt", "--output", "/tmp/c.trace"])

    def test_wait_for_process_matches_executable_basename(self):
        # device_call returns the already-unwrapped "result" object.
        hit = {"deviceIdentifier": "IPAD", "runningProcesses": [
            {"executable": "file:///sbin/launchd", "processIdentifier": 1},
            {"executable": "file:///private/var/containers/Bundle/Application/x/SSXNative.app/SSXNative",
             "processIdentifier": 4242}]}
        with mock.patch.object(metal_capture.mobile_gamecube, "device_call",
                               return_value=hit) as call:
            self.assertEqual(metal_capture.wait_for_process("IPAD", sleep=lambda s: None), 4242)
            call.assert_called_once()

    def test_wait_for_process_retries_then_times_out(self):
        empty = {"deviceIdentifier": "IPAD", "runningProcesses": []}
        with mock.patch.object(metal_capture.mobile_gamecube, "device_call",
                               return_value=empty):
            with self.assertRaises(RuntimeError):
                metal_capture.wait_for_process("IPAD", timeout_s=0, sleep=lambda s: None)

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
                    mock.patch.object(metal_capture, "wait_for_process",
                                      return_value=4242) as wait, \
                    mock.patch.object(metal_capture.time, "sleep") as sleep:
                receipt = metal_capture.capture(args, clock=sleep, run=fake_run)
                wait.assert_called_once_with("IPAD")
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

    def test_capture_all_processes_skips_pid_wait(self):
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp) / "cap"
            trace = outdir / "capture.trace"
            seq = Path(tmp) / "seq.json"
            seq.write_text("{}")
            args = capture_args(sequence=seq, output=outdir, all_processes=True)
            record = SimpleNamespace(returncode=0, stderr="")

            def fake_run(cmd, **kwargs):
                self.assertIn("--all-processes", cmd)
                self.assertNotIn("--attach", cmd)
                trace.write_bytes(b"trace-bytes")
                return record

            with mock.patch.object(metal_capture.mobile_gamecube, "launch"), \
                    mock.patch.object(metal_capture.mobile_gamecube, "collect"), \
                    mock.patch.object(metal_capture, "wait_for_process") as wait, \
                    mock.patch.object(metal_capture.time, "sleep"):
                receipt = metal_capture.capture(args, clock=lambda s: None, run=fake_run)
                wait.assert_not_called()
            self.assertEqual(receipt["target"], "all-processes")

    def test_receipt_hashes_directory_trace_bundles(self):
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp) / "cap"
            outdir.mkdir()
            trace = outdir / "capture.trace"
            (trace / "instrument_data").mkdir(parents=True)
            (trace / "instrument_data" / "run.bin").write_bytes(b"trace-bytes")
            seq = Path(tmp) / "seq.json"
            seq.write_text("{}")
            args = capture_args(sequence=seq, output=outdir)
            receipt = metal_capture.write_receipt(outdir, trace, args, target="all-processes")
            saved = json.loads((outdir / "receipt.json").read_text())
            self.assertEqual(saved["trace_sha256"], receipt["trace_sha256"])
            self.assertEqual(saved["target"], "all-processes")
            self.assertEqual(metal_capture.trace_size(trace), 11)
            # Order-independent: same content re-hashes identically.
            again = Path(tmp) / "cap2"
            (again / "capture.trace" / "instrument_data").mkdir(parents=True)
            (again / "capture.trace" / "instrument_data" / "run.bin").write_bytes(b"trace-bytes")
            self.assertEqual(metal_capture.sha(again / "capture.trace"),
                             receipt["trace_sha256"])

    def test_capture_surfaces_xctrace_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp) / "cap"
            seq = Path(tmp) / "seq.json"
            seq.write_text("{}")
            args = capture_args(sequence=seq, output=outdir)
            record = SimpleNamespace(returncode=1, stderr="attach refused")
            with mock.patch.object(metal_capture.mobile_gamecube, "launch"), \
                    mock.patch.object(metal_capture, "wait_for_process", return_value=4242), \
                    mock.patch.object(metal_capture.mobile_gamecube, "collect") as collect:
                with self.assertRaises(RuntimeError):
                    metal_capture.capture(args, clock=lambda s: None,
                                          run=lambda *a, **k: record)
                collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
