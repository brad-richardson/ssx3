"""Compile the real hash implementation and compare both paths to hashlib."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/ModernGekko"


@unittest.skipUnless((SOURCE / "src/runtime/game.cpp").exists() and shutil.which("clang++"),
                     "requires bootstrapped ModernGekko and Clang")
class NativeHashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.folder = Path(cls.temp.name)
        cls.probes = []
        for name, flags in [("system", []), ("portable", ["-DMODERNGEKKO_PORTABLE_SHA256=1"])]:
            output = cls.folder / name
            subprocess.run(["/usr/bin/clang++", "-std=c++20", "-O2", *flags,
                            "-I", str(SOURCE / "include"), str(ROOT / "tests/native_hash_probe.cpp"),
                            str(SOURCE / "src/runtime/game.cpp"), "-o", str(output)], check=True)
            cls.probes.append(output)

    def test_padding_and_stream_boundaries(self):
        path = self.folder / "payload"
        for size in [0, 1, 55, 56, 63, 64, 65, 65535, 65536, 65537, 1048593]:
            payload = (bytes(range(256)) * (size//256+1))[:size]
            path.write_bytes(payload)
            expected = hashlib.sha256(payload).hexdigest()
            for probe in self.probes:
                with self.subTest(size=size, probe=probe.name):
                    self.assertEqual(subprocess.check_output([probe, "file", path], text=True).strip(), expected)

    def test_directory_manifest_and_missing_file(self):
        with tempfile.TemporaryDirectory(dir=self.folder) as temporary:
            folder = Path(temporary)
            files = {"b": b"second", "a/sub": b"first"}
            manifest = bytearray()
            for name, content in sorted(files.items()):
                path = folder / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                encoded = name.encode()
                manifest += len(encoded).to_bytes(8, "big") + encoded
                manifest += len(content).to_bytes(8, "big") + hashlib.sha256(content).hexdigest().encode()
            for probe in self.probes:
                self.assertEqual(subprocess.check_output([probe, "directory", folder], text=True).strip(),
                                 hashlib.sha256(manifest).hexdigest())
                self.assertNotEqual(subprocess.run([probe, "file", folder / "missing"], capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
