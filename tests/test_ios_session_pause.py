"""Check frontend pause intent against lifecycle event sequences."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SessionPauseTest(unittest.TestCase):
    def test_lifecycle_and_repeated_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = pathlib.Path(directory) / 'pause-test'
            subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-I', str(ROOT / 'native/ios'),
                            str(ROOT / 'native/ios/tests/session_pause.cpp'),
                            '-o', str(binary)], check=True, capture_output=True)
            subprocess.run([str(binary)], check=True, capture_output=True)
