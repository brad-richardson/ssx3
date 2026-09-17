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


class PlatformPsqMerge(unittest.TestCase):
    MERGED_LOAD = "u8* ptr = get_ram_ptr(cpu, ea, 8, NULL);"
    MERGED_STORE = "u8* ptr = get_ram_ptr(cpu, ea, 8, &offset);"

    def test_cpu_header_carries_merged_psq_access(self):
        patch = (ROOT / "native/patches/recompcore-platform.patch").read_text()
        blocks = patch.split("diff --git a/GXRuntime/include/core/cpu.h b/GXRuntime/include/core/cpu.h")
        self.assertEqual(len(blocks), 2, "platform patch must carry exactly one cpu.h block")
        block = blocks[1].split("diff --git ")[0]
        self.assertIn("+" + "        " + self.MERGED_LOAD, block)
        self.assertIn("+" + "        " + self.MERGED_STORE, block)
        header = ROOT / "third_party/ModernGekko/vendor/dolphin/GXRuntime/include/core/cpu.h"
        if header.exists():
            text = header.read_text()
            self.assertIn(self.MERGED_LOAD, text)
            self.assertIn(self.MERGED_STORE, text)

    def test_cpu_header_forces_psq_inline(self):
        # M5 showed both psq helpers outlined as ~1% leaves; the per-site
        # LSQE/w folding only happens when the body actually inlines.
        patch = (ROOT / "native/patches/recompcore-platform.patch").read_text()
        blocks = patch.split("diff --git a/GXRuntime/include/core/cpu.h b/GXRuntime/include/core/cpu.h")
        self.assertEqual(len(blocks), 2, "platform patch must carry exactly one cpu.h block")
        block = blocks[1].split("diff --git ")[0]
        for name in ("ppc_psq_load_inline", "ppc_psq_store_inline"):
            self.assertIn(
                f"+static inline __attribute__((always_inline)) bool {name}(", block)


if __name__ == "__main__":
    unittest.main()
