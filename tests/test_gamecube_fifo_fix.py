"""FIFO watermark-interrupt fix records (patch + tree carry the carve-out)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "native/patches/recompcore-platform.patch"
CORE = ROOT / "third_party/ModernGekko/vendor/dolphin"

# Files the fix touches. All three must be owned by exactly one patch layer
# (recompcore-platform.patch, the CORE_STACK base) so the per-layer
# reverse-check cannot silently lose the fix to an overlap exclusion.
FIX_FILES = (
    "Source/Core/VideoCommon/CommandProcessor.cpp",
    "Source/Core/VideoCommon/CommandProcessor.h",
    "Source/Core/Core/HW/GPFifo.cpp",
)
UPPER_STACK = (
    "native/patches/recompcore-course-redirect.patch",
    "native/patches/moderngekko-memcard-read-rate.patch",
    "native/patches/moderngekko-dolphin-mixer-skip-silent.patch",
)


def patch_block(patch_text, path):
    marker = f"diff --git a/{path} b/{path}"
    blocks = patch_text.split(marker)
    if len(blocks) != 2:
        return None
    return blocks[1].split("diff --git ")[0]


class FifoFixRecords(unittest.TestCase):
    def test_platform_patch_carries_exactly_one_block_per_file(self):
        text = PATCH.read_text()
        for path in FIX_FILES:
            with self.subTest(path=path):
                marker = f"diff --git a/{path} b/{path}"
                self.assertEqual(text.count(marker), 1,
                                 f"platform patch must carry exactly one {path} block")

    def test_platform_patch_carries_carve_out(self):
        block = patch_block(PATCH.read_text(),
                            "Source/Core/VideoCommon/CommandProcessor.cpp")
        self.assertIsNotNone(block)
        for line in ("+bool FifoWmIntFixEnabled()",
                     "+    const char* e = std::getenv(\"SSX3_FIFO_FIX\");",
                     "+    const bool async_ok =",
                     "+        !(FifoWmIntFixEnabled() && m_system.GetFifo().UseDeterministicGPUThread());",
                     "+    if (async_ok)"):
            self.assertIn(line, block)

    def test_platform_patch_carries_gate_default_on(self):
        block = patch_block(PATCH.read_text(),
                            "Source/Core/VideoCommon/CommandProcessor.cpp")
        self.assertIsNotNone(block)
        # Default-on (only an explicit SSX3_FIFO_FIX=0 restores the wedge);
        # flipping this default reintroduces the deterministic FIFO panic.
        self.assertIn("+    return !(e && e[0] == '0' && e[1] == '\\0');", block)

    def test_platform_patch_carries_gp_fifo_skip(self):
        block = patch_block(PATCH.read_text(), "Source/Core/Core/HW/GPFifo.cpp")
        self.assertIsNotNone(block)
        for line in ("+#include \"Core/Config/MainSettings.h\"",
                     "+    static const bool skip_fifo_write_check =",
                     "+        Config::Get(Config::MAIN_CPU_CORE) == PowerPC::CPUCore::StaticRecomp;",
                     "+    if (!skip_fifo_write_check)"):
            self.assertIn(line, block)

    def test_platform_patch_carries_header_decl(self):
        block = patch_block(PATCH.read_text(),
                            "Source/Core/VideoCommon/CommandProcessor.h")
        self.assertIsNotNone(block)
        self.assertIn("+bool FifoWmIntFixEnabled();", block)

    def test_tree_carries_fix(self):
        if not (CORE / ".git").exists():
            self.skipTest("ModernGekko checkout not present")
        checks = {
            "Source/Core/VideoCommon/CommandProcessor.cpp":
                ["bool FifoWmIntFixEnabled()", "const bool async_ok =",
                 "UseDeterministicGPUThread()"],
            "Source/Core/VideoCommon/CommandProcessor.h": ["bool FifoWmIntFixEnabled();"],
            "Source/Core/Core/HW/GPFifo.cpp":
                ["skip_fifo_write_check", "PowerPC::CPUCore::StaticRecomp"],
        }
        for path, lines in checks.items():
            text = (CORE / path).read_text()
            for line in lines:
                with self.subTest(path=path, line=line):
                    self.assertIn(line, text)

    def test_no_temp_diag_remnants(self):
        # The fifo-panic investigation used env-gated stderr tracing
        # (SSX3_FIFO_DEBUG / SSX3_FIFO_LOW_WM / [ssx3-fifo]); none of it may
        # leak into the deliverable tree or patch.
        banned = ("SSX3_FIFO_DEBUG", "SSX3_FIFO_LOW_WM", "[ssx3-fifo]",
                  "WEDGE-ARM", "segmax", "FifoDiag", "OVERRUN-IMMINENT")
        text = PATCH.read_text()
        for token in banned:
            with self.subTest(token=token):
                self.assertNotIn(token, text)
        if (CORE / ".git").exists():
            for path in FIX_FILES:
                body = (CORE / path).read_text()
                for token in banned:
                    with self.subTest(path=path, token=token):
                        self.assertNotIn(token, body)

    def test_fix_files_unowned_above_base(self):
        # Overlaps with upper CORE_STACK layers are excluded from the base
        # reverse-check, so a shared file could lose the fix silently.
        for name in UPPER_STACK:
            text = (ROOT / name).read_text()
            for path in FIX_FILES:
                with self.subTest(patch=name, path=path):
                    self.assertNotIn(f"diff --git a/{path} b/{path}", text)


if __name__ == "__main__":
    unittest.main()
