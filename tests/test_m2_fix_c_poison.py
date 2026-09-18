"""M2 Fix C record: fallback-JIT code-space poisoning caller is pinned.

Brief M2 Fix C: M7 shows ARM64CodeBlock::PoisonMemory at 0.32% on the
emulation thread during play; StaticRecompCore_Run.cpp forces
InvalidateICache(lr, 4, true) on the fallback yield path. The brief asks to
count the calls per second with a temporary counter (not committed), report
the caller and the rate, and propose -- not implement -- unless the fix is a
one-line guard with an obvious A/B. No quiet-host window was available for
the counting run (see local/research/M2/REPORT.md), so this test pins the
call site and its caller for the follow-up run instead of asserting a fix.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "third_party/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp"


class FixCPoisonCaller(unittest.TestCase):
    def test_invalidate_on_host_call_passthrough_path(self):
        text = RUN.read_text()
        self.assertIn("IsHostCallAddress(m_guest.lr)", text)
        self.assertIn("InvalidateICache(m_guest.lr, 4, true)", text)
        # The invalidate must still sit on the m_host_call_passthrough branch
        # (the fallback-JIT yield path), not scattered across the run loop.
        self.assertEqual(text.count("InvalidateICache(m_guest.lr, 4, true)"), 1)
        head, sep, _ = text.partition("InvalidateICache(m_guest.lr, 4, true)")
        preceding = "\n".join(head.splitlines()[-8:])
        # Caller: the host_call passthrough branch, guarded on the link
        # register holding a host-call address (the fallback-JIT yield path).
        self.assertIn("IsHostCallAddress(m_guest.lr)", preceding + sep)
        self.assertIn("m_fallback_jit", preceding + sep)


if __name__ == "__main__":
    unittest.main()
