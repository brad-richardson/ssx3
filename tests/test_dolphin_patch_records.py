import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Dolphin-submodule record patches, applied on top of the bootstrap stack
# (recompcore-platform + recompcore-course-redirect). Each record must either
# apply cleanly to the pinned tree or already be applied to it.
RECORDS = [
    "native/patches/moderngekko-dolphin-ios-dcblock.patch",
    "native/patches/moderngekko-dolphin-mixer-skip-silent.patch",
]


class DolphinPatchRecords(unittest.TestCase):
    def test_records_match_nested_tree(self):
        dolphin = ROOT / "third_party/ModernGekko/vendor/dolphin"
        if not (dolphin / ".git").exists():
            self.skipTest("ModernGekko checkout not present")

        for name in RECORDS:
            with self.subTest(patch=name):
                patch = ROOT / name
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
                                f"{name} neither applies nor reverse-applies; record diverged")


if __name__ == "__main__":
    unittest.main()
