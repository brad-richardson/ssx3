import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DolphinPatchRecords(unittest.TestCase):
    def test_dcblock_record_matches_nested_tree(self):
        dolphin = ROOT / "third_party/ModernGekko/vendor/dolphin"
        patch = ROOT / "native/patches/moderngekko-dolphin-ios-dcblock.patch"
        if not (dolphin / ".git").exists():
            self.skipTest("ModernGekko checkout not present")
        self.assertTrue(patch.is_file())

        def applies(*extra):
            return subprocess.run(
                ["git", "-C", str(dolphin), "apply", "--check", *extra, str(patch)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

        forward = applies()
        reverse = applies("--reverse")
        # Exactly one direction applies: the record is either cleanly
        # applicable to the pinned tree or already applied to it. Neither
        # means the record and the tree silently diverged.
        self.assertTrue(forward != reverse,
                        "DC-block patch neither applies nor reverse-applies; record diverged")


if __name__ == "__main__":
    unittest.main()
