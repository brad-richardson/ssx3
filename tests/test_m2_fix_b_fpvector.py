"""M2 Fix B record: FP-unavailable vector is measured, not emulated.

Brief M2 Fix B asked to verify the words at 0x80000800 against the SDK's
__OSFPUnavailable prologue and, if the vector body is no more than the
syscall vector was (a HID0 toggle around a sync plus rfi), emulate it
natively. Measurement (see local/research/M2/REPORT.md) shows the FP path
is NOT a leaf stub: ppc_take_exception routes FP-unavailable through the
generic exception entry (MSR save to SRR0/SRR1, vector at 0x800), whose
installed body saves the full thread context and branches to the SDK
handler -- strictly more than the 7-word syscall stub the core emulates in
TryHostHle. Per the brief's stop clause, implementation stops after the
measurement. This test pins that stop state: TryHostHle emulates only the
0xC00 syscall vector, and the FP exception still routes to vector 0x800.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SMC = ROOT / "third_party/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_SMC.cpp"
CPU_H = ROOT / "third_party/ModernGekko/vendor/dolphin/GXRuntime/include/core/cpu.h"


class FixBFpVectorStop(unittest.TestCase):
    def test_syscall_vector_still_emulated(self):
        text = SMC.read_text()
        self.assertIn("0x00000C00u", text)
        self.assertIn("m_emulate_syscall_vector", text)

    def test_fp_vector_not_emulated(self):
        text = SMC.read_text()
        self.assertNotIn("0x00000800", text,
                         "an 0x800 emulation would exceed the brief's stop clause")

    def test_fp_unavailable_routes_to_vector_0x800(self):
        text = CPU_H.read_text()
        self.assertIn("#define PPC_VECTOR_FP_UNAVAILABLE 0x00800u", text)
        self.assertIn("PPC_EXC_FP_UNAVAILABLE", text)


if __name__ == "__main__":
    unittest.main()
