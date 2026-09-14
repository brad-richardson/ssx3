"""Exercise actual Foundation preference storage and launch override isolation."""
import pathlib
import platform
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@unittest.skipUnless(platform.system() == 'Darwin' and shutil.which('xcrun'),
                     'requires macOS Foundation')
class DisplayPreferencesTest(unittest.TestCase):
    def test_saved_preferences_and_process_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = pathlib.Path(directory) / 'display-preferences-test'
            command = [
                'xcrun', 'clang++', '-std=c++17', '-fobjc-arc', '-Wall', '-Wextra', '-Werror',
                '-framework', 'Foundation', '-I', str(ROOT / 'native/ios'),
                str(ROOT / 'native/ios/DisplayPreferences.mm'),
                str(ROOT / 'native/ios/tests/display_preferences.mm'), '-o', str(binary)]
            compiled = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
            result = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
