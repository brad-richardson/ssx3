"""M2 Fix A record: SyncOut programs the host rounding mode only on change.

Brief M2 Fix A: StaticRecompCore_Sync.cpp::SyncOut called
PowerPC::RoundingModeUpdated unconditionally at every burst boundary (M7:
0.51% of cycles with SetSIMDMode). The host SIMD mode depends only on FPSCR
RN (bits 0-1) and NI (bit 2), so the fix guards the call on those bits via
m_last_sync_fpscr_rm_ni. This test pins the guard in the live tree and in
native/patches/recompcore-platform.patch (which must carry the hunks).
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "native/patches/recompcore-platform.patch"
SYNC = ROOT / "third_party/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Sync.cpp"
HEADER = ROOT / "third_party/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore.h"


def patch_block(patch_text, path):
    marker = f"diff --git a/{path} b/{path}"
    parts = patch_text.split(marker)
    if len(parts) < 2:
        return None
    # One file may carry several sequential blocks (stacked hunks apply in
    # order); concatenate every block for the path.
    return "\n".join(part.split("diff --git ")[0] for part in parts[1:])


SYNC_PATH = "Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Sync.cpp"
HEADER_PATH = "Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore.h"


class FixARoundingGuard(unittest.TestCase):
    def test_sync_guards_rounding_update_on_rn_ni(self):
        text = SYNC.read_text()
        self.assertIn("m_last_sync_fpscr_rm_ni", text)
        self.assertIn("ppc.fpscr.Hex & 0x7u", text)
        self.assertIn("PowerPC::RoundingModeUpdated(ppc)", text)
        # The unconditional call must be gone: the only remaining call site
        # sits inside the rm_ni change guard.
        self.assertEqual(text.count("PowerPC::RoundingModeUpdated(ppc)"), 1)
        guard = text.split("PowerPC::RoundingModeUpdated(ppc)")[0].rsplit("SyncOut", 1)[1]
        self.assertIn("if (rm_ni != m_last_sync_fpscr_rm_ni)", guard)

    def test_header_caches_last_programmed_rn_ni(self):
        text = HEADER.read_text()
        self.assertIn("u32 m_last_sync_fpscr_rm_ni = 0xFFFFFFFFu;", text)

    def test_patch_carries_both_hunks(self):
        patch = PATCH.read_text()
        for path, needle in ((SYNC_PATH, "m_last_sync_fpscr_rm_ni"),
                             (HEADER_PATH, "m_last_sync_fpscr_rm_ni")):
            with self.subTest(path=path):
                block = patch_block(patch, path)
                self.assertIsNotNone(block, f"patch must carry a {path} block")
                self.assertIn(needle, block)


if __name__ == "__main__":
    unittest.main()
