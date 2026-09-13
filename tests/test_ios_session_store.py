"""Exercise the real Foundation persistence implementation on macOS."""
import pathlib
import platform
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@unittest.skipUnless(platform.system() == 'Darwin' and
                     (ROOT / 'third_party/ModernGekko/src/runtime/game.cpp').exists(),
                     'requires macOS Foundation and the pinned runtime checkout')
class SessionStoreTest(unittest.TestCase):
    def test_persistence_and_failure_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = pathlib.Path(directory) / 'session-store-test'
            subprocess.run([
                'xcrun', 'clang++', '-std=c++23', '-fobjc-arc', '-Wno-deprecated-declarations',
                '-framework', 'Foundation', '-I', str(ROOT / 'native/ios'),
                '-I', str(ROOT / 'third_party/ModernGekko/include'),
                str(ROOT / 'native/ios/SessionStore.mm'),
                str(ROOT / 'native/ios/tests/session_store.mm'),
                str(ROOT / 'third_party/ModernGekko/src/runtime/game.cpp'),
                '-o', str(binary)], check=True, capture_output=True)
            subprocess.run([str(binary)], check=True, capture_output=True)
