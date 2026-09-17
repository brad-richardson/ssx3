"""Throttle-clock overflow fix records (patch + tree carry the widening)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "native/patches/recompcore-platform.patch"
CORE = ROOT / "third_party/ModernGekko/vendor/dolphin"

# m_throttle_adj_clock_per_sec wrapped at 2^32: EmulationSpeed=10 on the
# 486 MHz GameCube clock (4.86e9 ticks/s) truncated to 565032704, so every
# "uncapped" run throttled to exactly 565032704/486000000 = 1.16262x on all
# devices and backends. The fix widens the member and its computation to s64
# (s64, not u64, to preserve the signed division semantics at the sec_adj and
# target-time sites). Both files must be owned by exactly one patch layer
# (recompcore-platform.patch, the CORE_STACK base) so the per-layer
# reverse-check cannot silently lose the fix to an overlap exclusion.
FIX_FILES = (
    "Source/Core/Core/CoreTiming.cpp",
    "Source/Core/Core/CoreTiming.h",
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


class ThrottleOverflowRecords(unittest.TestCase):
    def test_platform_patch_carries_exactly_one_block_per_file(self):
        text = PATCH.read_text()
        for path in FIX_FILES:
            with self.subTest(path=path):
                marker = f"diff --git a/{path} b/{path}"
                self.assertEqual(text.count(marker), 1,
                                 f"platform patch must carry exactly one {path} block")

    def test_platform_patch_carries_widened_computation(self):
        block = patch_block(PATCH.read_text(), "Source/Core/Core/CoreTiming.cpp")
        self.assertIsNotNone(block)
        for line in ("-  const u32 new_clock_per_sec =",
                     "-      std::lround(m_system.GetSystemTimers().GetTicksPerSecond() * new_speed);",
                     "+  const s64 new_clock_per_sec =",
                     "+      std::llround(m_system.GetSystemTimers().GetTicksPerSecond() * new_speed);"):
            self.assertIn(line, block)

    def test_platform_patch_carries_widened_member(self):
        block = patch_block(PATCH.read_text(), "Source/Core/Core/CoreTiming.h")
        self.assertIsNotNone(block)
        for line in ("-  u32 m_throttle_adj_clock_per_sec = 0;",
                     "+  s64 m_throttle_adj_clock_per_sec = 0;"):
            self.assertIn(line, block)

    def test_tree_carries_fix(self):
        if not (CORE / ".git").exists():
            self.skipTest("ModernGekko checkout not present")
        checks = {
            "Source/Core/Core/CoreTiming.cpp":
                ["const s64 new_clock_per_sec =",
                 "std::llround(m_system.GetSystemTimers().GetTicksPerSecond() * new_speed);"],
            "Source/Core/Core/CoreTiming.h": ["s64 m_throttle_adj_clock_per_sec = 0;"],
        }
        for path, lines in checks.items():
            text = (CORE / path).read_text()
            for line in lines:
                with self.subTest(path=path, line=line):
                    self.assertIn(line, text)

    def test_tree_has_no_narrowed_remnant(self):
        if not (CORE / ".git").exists():
            self.skipTest("ModernGekko checkout not present")
        self.assertNotIn("u32 new_clock_per_sec",
                         (CORE / "Source/Core/Core/CoreTiming.cpp").read_text())
        self.assertNotIn("u32 m_throttle_adj_clock_per_sec",
                         (CORE / "Source/Core/Core/CoreTiming.h").read_text())

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
