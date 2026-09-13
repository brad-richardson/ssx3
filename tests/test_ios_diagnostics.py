"""Verify real Objective-C callback lifetime and fail-closed source injection."""
import pathlib
import platform
import subprocess
import tempfile
import unittest

from tools.ios_diagnostic_sources import replace_once

ROOT = pathlib.Path(__file__).resolve().parents[1]


class DiagnosticSourceTests(unittest.TestCase):
    def test_changed_or_ambiguous_seam_is_rejected(self):
        for source in ('missing', 'seam\nseam'):
            with self.assertRaises(ValueError):
                replace_once(source, 'seam', 'observer')


@unittest.skipUnless(platform.system() == 'Darwin', 'requires Apple frameworks')
class SessionDiagnosticsTests(unittest.TestCase):
    def test_delayed_callbacks_and_bounded_buffer(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = pathlib.Path(directory) / 'diagnostics-test'
            subprocess.run([
                'xcrun', 'clang++', '-std=c++23', '-fobjc-arc',
                '-framework', 'Foundation', '-framework', 'Metal', '-framework', 'QuartzCore',
                '-I', str(ROOT / 'native/ios'),
                str(ROOT / 'native/ios/SessionDiagnostics.mm'),
                str(ROOT / 'native/ios/tests/session_diagnostics.mm'),
                '-o', str(binary)], check=True, capture_output=True)
            subprocess.run([str(binary)], check=True, capture_output=True)
