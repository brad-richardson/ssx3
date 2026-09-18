"""S3: the recomp core's host emulation of the SDK FP-unavailable handler.

Two layers:

1. Record test -- the hunks are present in the live vendor tree and carried by
   native/patches/recompcore-platform.patch, and the decoded constants (vector
   image, handler words, OSContext offsets) match main.dol.

2. Unit test -- the shipped TryHleFpUnavailable body is sliced out of
   StaticRecompCore_SMC.cpp, compiled against a minimal StaticRecompCore
   stand-in, and run on synthetic CPU states + two fake OSContexts. Its result
   is compared bit-for-bit against a reference that interprets the *actual* SDK
   instructions from main.dol (vector template at 0x800, __OSFPUnavailableHandler,
   __OSSaveFPUContext, __OSLoadFPUContext) -- so the check is against the guest
   code being replaced, not a second transcription of the listing.
"""
import os
import random
import shutil
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "third_party/ModernGekko/vendor/dolphin"
SMC = CORE / "Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_SMC.cpp"
RUN = CORE / "Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp"
HDR = CORE / "Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore.h"
CPP = CORE / "Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore.cpp"
PATCH = ROOT / "native/patches/recompcore-platform.patch"
DOL = ROOT / "local/source/gamecube/ssx3/sys/main.dol"
S3 = ROOT / "local/research/S3"
HARNESS = S3 / "harness"

sys.path.insert(0, str(S3))

EXTRACT_START = "// S3: host emulation of the SDK's FP-unavailable path (guest vector 0x800)."
EXTRACT_END = "  ++m_hle_fp;\n  return true;\n}\n"

# Addresses decoded from main.dol (see local/research/S3/REPORT.md).
EV_START, EV_END = 0x80283E6C, 0x80283F04
EV_SET_NUMBER = 0x80283ED4
FP_EXCEPTION = 7
FP_VECTOR = 0x80000800
EXC_TABLE = 0x80003000
HANDLER = 0x80285998
SAVE_FPU = 0x80285318
LOAD_FPU = 0x802851F4
SAVE_FPU_WORDS = 74
LOAD_FPU_WORDS = 73
HANDLER_WORDS = 33
CUR_CTX_PHYS, CUR_CTX, FPU_CTX = 0x800000C0, 0x800000D4, 0x800000D8
CTX_SIZE = 0x2C8
CTX_STATE = 0x1A2

MSR_CLEAR = (0x00040000 | 0x8000 | 0x4000 | 0x2000 | 0x800 | 0x400 | 0x200 | 0x100 |
             0x20 | 0x10 | 0x4 | 0x2 | 0x1)
MSR_ILE, MSR_LE, MSR_FP, MSR_RI = 0x00010000, 0x1, 0x2000, 0x2
RFI_MASK = 0x87C0FFFF
RAM_BASE, RAM_SIZE = 0x80000000, 24 * 1024 * 1024


def dol_segments(data):
    head = struct.unpack('>64I', data[:256])
    segs = []
    for off, addr, size in zip(head[0:7], head[18:25], head[36:43]):
        if size:
            segs.append((off, addr, size))
    for off, addr, size in zip(head[7:18], head[25:36], head[43:54]):
        if size:
            segs.append((off, addr, size))
    return segs


def build_ram():
    """RAM with the DOL image plus the low-memory state __OSExceptionInit leaves."""
    data = DOL.read_bytes()
    ram = bytearray(RAM_SIZE)
    for off, addr, size in dol_segments(data):
        if RAM_BASE <= addr and addr - RAM_BASE + size <= RAM_SIZE:
            ram[addr - RAM_BASE:addr - RAM_BASE + size] = data[off:off + size]
    # __OSExceptionInit: patch __OSEVSetNumber with the exception number, copy
    # __OSEVStart..__OSEVEnd to the vector, and publish the handler table.
    template = bytearray(ram[EV_START - RAM_BASE:EV_END - RAM_BASE])
    patch_off = EV_SET_NUMBER - EV_START
    word = struct.unpack_from('>I', template, patch_off)[0] | FP_EXCEPTION
    struct.pack_into('>I', template, patch_off, word)
    ram[FP_VECTOR - RAM_BASE:FP_VECTOR - RAM_BASE + len(template)] = template
    struct.pack_into('>I', ram, EXC_TABLE - RAM_BASE + 4 * FP_EXCEPTION, HANDLER)
    return ram


def exception_msr(old):
    nxt = old & ~MSR_CLEAR
    if old & MSR_ILE:
        nxt |= MSR_LE
    return nxt & 0xFFFFFFFF


class Case:
    """One synthetic fault: registers, two OSContexts, and the RAM they live in."""

    REGIONS = ((FP_VECTOR, EV_END - EV_START), (EXC_TABLE + 4 * FP_EXCEPTION, 4),
               (0x800000C0, 0x20), (HANDLER, 4 * HANDLER_WORDS),
               (SAVE_FPU, 4 * SAVE_FPU_WORDS), (LOAD_FPU, 4 * LOAD_FPU_WORDS))

    def __init__(self, rng, base_ram, corrupt=None):
        self.ram = bytearray(base_ram)
        # 8-byte aligned, deliberately not always 32: OSDumpContext builds a
        # context at r1+16, so the core may only require what stfd needs.
        self.cur = 0x80400000 + 0x1000 * rng.randrange(0, 16) + 8 * rng.randrange(0, 4)
        owner_choice = rng.choice(('same', 'other', 'none'))
        if owner_choice == 'same':
            self.owner = self.cur
        elif owner_choice == 'none':
            self.owner = 0
        else:
            self.owner = self.cur + 0x8000 + 0x1000 * rng.randrange(0, 8) + 8 * rng.randrange(0, 4)
        self.pse = rng.random() < 0.8
        self.hid2 = (0x80000000 if self.pse else 0x80000000)  # LSQE always on
        if self.pse:
            self.hid2 |= 0x20000000
        self.gqr0 = 0
        self.old_msr = rng.choice((0x9032, 0x9032, 0x9032, 0x1032, 0x9033, 0x00009036))
        self.msr = exception_msr(self.old_msr)
        self.srr1 = self.old_msr & RFI_MASK
        self.srr0 = 0x80100000 + 4 * rng.randrange(0, 1 << 16)
        self.gpr = [rng.getrandbits(32) for _ in range(32)]
        self.cr = rng.getrandbits(32)
        self.lr = 0x80200000 + 4 * rng.randrange(0, 1 << 12)
        self.ctr = rng.getrandbits(32)
        self.xer = rng.getrandbits(32) & 0xE000FFFF
        self.fpscr = rng.choice((0x00000000, 0x82004000, 0x00004000, 0x20000000))
        self.fpr = [self.fp_bits(rng) for _ in range(32)]
        self.ps1 = [self.fp_bits(rng) for _ in range(32)]

        for ctx in {self.cur, self.owner} - {0}:
            self.init_ctx(rng, ctx)
        # The context being switched in keeps the live RN/NI (the core rejects
        # a load that would change the host rounding mode).
        state = struct.unpack_from('>H', self.ram, self.cur - RAM_BASE + CTX_STATE)[0]
        if state & 1:
            saved = struct.unpack_from('>Q', self.ram, self.cur - RAM_BASE + 0x190)[0]
            saved = (saved & ~0x7) | (self.fpscr & 0x7)
            struct.pack_into('>Q', self.ram, self.cur - RAM_BASE + 0x190, saved)
        struct.pack_into('>I', self.ram, CUR_CTX - RAM_BASE, self.cur)
        struct.pack_into('>I', self.ram, CUR_CTX_PHYS - RAM_BASE, self.cur & 0x3FFFFFFF)
        struct.pack_into('>I', self.ram, FPU_CTX - RAM_BASE, self.owner)
        if corrupt is not None:
            struct.pack_into('>I', self.ram, corrupt - RAM_BASE, 0xDEADBEEF)

    @staticmethod
    def fp_bits(rng):
        return rng.choice((
            0x0000000000000000, 0x8000000000000000, 0x3FF0000000000000,
            0x7FF0000000000000, 0xFFF8000000000000, 0x7FF8000000000001,
            0x0000000000000001, 0x380FFFFFFFFFFFFF, 0x3690000000000000,
            rng.getrandbits(64), rng.getrandbits(64),
        ))

    def init_ctx(self, rng, addr):
        off = addr - RAM_BASE
        for i in range(CTX_SIZE // 4):
            struct.pack_into('>I', self.ram, off + 4 * i, rng.getrandbits(32))
        struct.pack_into('>H', self.ram, off + CTX_STATE, rng.choice((0, 1, 1, 1)))
        struct.pack_into('>I', self.ram, off + 0x190, 0xFFF80000)
        struct.pack_into('>I', self.ram, off + 0x194,
                         rng.choice((0x00000000, 0x82004000, 0x00004000)))
        struct.pack_into('>I', self.ram, off + 0x19C, self.old_msr & RFI_MASK)
        struct.pack_into('>I', self.ram, off + 0x198, self.srr0)

    # --- reference: interpret the real SDK code -----------------------------
    def reference(self):
        import ppcexec
        m = ppcexec.Machine(bytearray(self.ram))
        m.gpr = list(self.gpr)
        m.fpr = list(self.fpr)
        m.ps1 = list(self.ps1)
        m.cr, m.lr, m.ctr, m.xer = self.cr, self.lr, self.ctr, self.xer
        m.fpscr, m.msr, m.srr0, m.srr1 = self.fpscr, self.msr, self.srr0, self.srr1
        m.hid2 = self.hid2
        m.gqr[0] = self.gqr0
        m.pc = 0x800
        while m.pc != (self.srr0 & ~3):
            m.step()
            if m.steps > 4000:
                raise AssertionError("reference did not resume")
        return m

    # --- harness input ------------------------------------------------------
    def harness_input(self):
        lines = []
        for addr, length in self.REGIONS + ((self.cur, CTX_SIZE),) + (
                ((self.owner, CTX_SIZE),) if self.owner else ()):
            off = addr - RAM_BASE
            lines.append(f"ram {addr:08x} {self.ram[off:off + length].hex()}")
        for i, v in enumerate(self.gpr):
            lines.append(f"gpr {i} {v:08x}")
        for i, v in enumerate(self.fpr):
            lines.append(f"fpr {i} {v:016x}")
        for i, v in enumerate(self.ps1):
            lines.append(f"ps1 {i} {v:016x}")
        lines.append(f"gqr 0 {self.gqr0:08x}")
        for name, v in (("pc", 0x800), ("lr", self.lr), ("ctr", self.ctr), ("cr", self.cr),
                        ("xer", self.xer), ("fpscr", self.fpscr), ("msr", self.msr),
                        ("srr0", self.srr0), ("srr1", self.srr1), ("hid2", self.hid2),
                        ("exception", 0x20)):
            lines.append(f"reg {name} {v:08x}")
        for addr, length in ((self.cur, CTX_SIZE), (0x800000C0, 0x20)) + (
                ((self.owner, CTX_SIZE),) if self.owner else ()):
            lines.append(f"dump {addr:08x} {length:x}")
        lines.append("run")
        return "\n".join(lines) + "\n"


def parse_harness(text):
    out = {"gpr": {}, "fp": {}, "mem": {}}
    for line in text.splitlines():
        parts = line.split()
        if parts[0] == "result":
            out["result"] = int(parts[1])
        elif parts[0] == "counters":
            out["hle_fp"], out["rejects"] = int(parts[1]), int(parts[2])
        elif parts[0] == "downcount":
            out["downcount"] = int(parts[1])
        elif parts[0] == "state":
            for i in range(1, len(parts), 2):
                out[parts[i]] = int(parts[i + 1], 16)
        elif parts[0] == "gpr":
            out["gpr"][int(parts[1])] = int(parts[2], 16)
        elif parts[0] == "fp":
            out["fp"][int(parts[1])] = (int(parts[2], 16), int(parts[3], 16))
        elif parts[0] == "mem":
            out["mem"][int(parts[1], 16)] = bytes.fromhex(parts[2])
    return out


def build_harness(tmp):
    src = SMC.read_text()
    start = src.index(EXTRACT_START)
    start = src.rindex("// ----", 0, start)
    end = src.index(EXTRACT_END, start) + len(EXTRACT_END)
    (tmp / "s3_extract.inc").write_text(src[start:end])
    binary = tmp / "s3_hle_harness"
    cmd = [os.environ.get("CXX", "c++"), "-std=c++20", "-O1", "-o", str(binary),
           str(HARNESS / "s3_hle_harness.cpp"),
           f"-I{tmp}", f"-I{CORE / 'GXRuntime/include'}"]
    subprocess.run(cmd, check=True)
    return binary


class RecordTest(unittest.TestCase):
    def test_hunks_present_in_tree(self):
        self.assertIn("bool StaticRecompCore::TryHleFpUnavailable()", SMC.read_text())
        self.assertIn("bool TryHleFpUnavailable();", HDR.read_text())
        self.assertIn("u64 m_hle_fp = 0;", HDR.read_text())
        run = RUN.read_text()
        self.assertIn("m_hle_fp_unavailable && m_guest.exception == PPC_EXC_FP_UNAVAILABLE", run)
        self.assertIn("m_guest.pc == PPC_VECTOR_FP_UNAVAILABLE && TryHleFpUnavailable()", run)
        cpp = CPP.read_text()
        self.assertIn('std::getenv("SSX_HLE_FP_UNAVAILABLE")', cpp)
        self.assertIn("hle_fp=%llu", cpp)

    def test_hunks_carried_by_patch(self):
        patch = PATCH.read_text()
        for needle in ("bool StaticRecompCore::TryHleFpUnavailable()",
                       "+  bool TryHleFpUnavailable();",
                       "+  u64 m_hle_fp = 0;",
                       'SSX_HLE_FP_UNAVAILABLE_DEFAULT'):
            self.assertIn(needle, patch, needle)

    def test_constants_match_dol(self):
        if not DOL.exists():
            self.skipTest("main.dol not present")
        ram = build_ram()
        src = SMC.read_text()
        vector = ram[FP_VECTOR - RAM_BASE:FP_VECTOR - RAM_BASE + (EV_END - EV_START)]
        words = struct.unpack(f">{len(vector) // 4}I", vector)
        self.assertEqual(len(words), 38)
        self.assertEqual(words[26], 0x38600007, "__OSEVSetNumber patched with exception 7")
        for w in words:
            self.assertIn(f"0x{w:08x}u", src)
        handler = struct.unpack(f">{HANDLER_WORDS}I",
                                ram[HANDLER - RAM_BASE:HANDLER - RAM_BASE + 4 * HANDLER_WORDS])
        for w in handler:
            self.assertIn(f"0x{w:08x}u", src)
        self.assertEqual(handler[-1], 0x4C000064, "handler ends in rfi")
        self.assertEqual(
            struct.unpack_from(">I", ram, EXC_TABLE - RAM_BASE + 4 * FP_EXCEPTION)[0], HANDLER)
        # The two 32-instruction runs the core checks by formula.
        for base, first in ((SAVE_FPU + 0x0C, 0xD8050090), (SAVE_FPU + 0xA4, 0xF00501C8),
                            (LOAD_FPU + 0x20, 0xE00401C8), (LOAD_FPU + 0xA0, 0xC8040090)):
            for i in range(32):
                got = struct.unpack_from(">I", ram, base - RAM_BASE + 4 * i)[0]
                self.assertEqual(got, first + (i << 21) + 8 * i, f"{base:08x}+{i}")


class UnitTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        if not DOL.exists():
            raise unittest.SkipTest("main.dol not present")
        if shutil.which(os.environ.get("CXX", "c++")) is None:
            raise unittest.SkipTest("no C++ compiler")
        import tempfile
        cls._tmp = tempfile.TemporaryDirectory()
        cls.binary = build_harness(Path(cls._tmp.name))
        cls.base_ram = build_ram()

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def run_case(self, case):
        proc = subprocess.run([str(self.binary)], input=case.harness_input(),
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return parse_harness(proc.stdout)

    def check(self, case):
        got = self.run_case(case)
        self.assertEqual(got["result"], 1, "expected the fault to be emulated")
        ref = case.reference()
        self.assertEqual(got["pc"], ref.pc & 0xFFFFFFFF, "resume pc")
        self.assertEqual(got["msr"], ref.msr, "resumed msr")
        self.assertEqual(got["srr0"], ref.srr0, "srr0")
        self.assertEqual(got["srr1"], ref.srr1, "srr1")
        self.assertEqual(got["cr"], ref.cr, "cr")
        self.assertEqual(got["lr"], ref.lr, "lr")
        self.assertEqual(got["ctr"], ref.ctr, "ctr")
        self.assertEqual(got["xer"], ref.xer, "xer")
        self.assertEqual(got["fpscr"], ref.fpscr, "fpscr")
        for i in range(32):
            self.assertEqual(got["gpr"][i], ref.gpr[i], f"gpr{i}")
            self.assertEqual(got["fp"][i][0], ref.fpr[i], f"fpr{i}")
            self.assertEqual(got["fp"][i][1], ref.ps1[i], f"ps1_{i}")
        for addr, blob in got["mem"].items():
            want = bytes(ref.ram[addr - RAM_BASE:addr - RAM_BASE + len(blob)])
            self.assertEqual(blob.hex(), want.hex(), f"memory at {addr:08x}")

    def test_random_faults_match_the_sdk_code(self):
        rng = random.Random(20260918)
        seen = set()
        for _ in range(120):
            case = Case(rng, self.base_ram)
            seen.add((case.owner == case.cur, case.owner == 0, case.pse))
            self.check(case)
        self.assertGreaterEqual(len(seen), 5, "shapes covered")

    def test_ping_pong_pair_round_trips(self):
        """D5's two-thread ping-pong: A owns the FPU, B faults, then A faults."""
        rng = random.Random(7)
        case = Case(rng, self.base_ram)
        case.owner = case.cur + 0x9000
        struct.pack_into('>I', case.ram, FPU_CTX - RAM_BASE, case.owner)
        case.init_ctx(rng, case.owner)
        struct.pack_into('>H', case.ram, case.owner - RAM_BASE + CTX_STATE, 1)
        struct.pack_into('>H', case.ram, case.cur - RAM_BASE + CTX_STATE, 1)
        struct.pack_into('>I', case.ram, case.cur - RAM_BASE + 0x190, 0xFFF80000)
        struct.pack_into('>I', case.ram, case.cur - RAM_BASE + 0x194, case.fpscr)
        self.check(case)

    def test_rejects_leave_state_untouched(self):
        rng = random.Random(11)
        for corrupt in (FP_VECTOR + 4 * 26, HANDLER + 4 * 8, SAVE_FPU + 0x10,
                        LOAD_FPU + 0x24, EXC_TABLE + 4 * FP_EXCEPTION):
            case = Case(rng, self.base_ram, corrupt=corrupt)
            got = self.run_case(case)
            self.assertEqual(got["result"], 0, f"corrupting {corrupt:08x} must reject")
            self.assertEqual(got["rejects"], 1)
            self.assertEqual(got["pc"], 0x800, "pc left on the vector")
            self.assertEqual(got["downcount"], 0)
            for i in range(32):
                self.assertEqual(got["fp"][i][0], case.fpr[i])
                self.assertEqual(got["fp"][i][1], case.ps1[i])
            for addr, blob in got["mem"].items():
                want = bytes(case.ram[addr - RAM_BASE:addr - RAM_BASE + len(blob)])
                self.assertEqual(blob.hex(), want.hex(), f"memory at {addr:08x}")

    def test_rejects_unmodellable_machine_state(self):
        rng = random.Random(13)
        # A context that is not 8-byte aligned: its f64 fields would be
        # misaligned for stfd/lfd.
        case = Case(rng, self.base_ram)
        case.cur += 4
        struct.pack_into('>I', case.ram, CUR_CTX - RAM_BASE, case.cur)
        struct.pack_into('>I', case.ram, CUR_CTX_PHYS - RAM_BASE, case.cur & 0x3FFFFFFF)
        self.assertEqual(self.run_case(case)["result"], 0)
        # MSR[RI] clear sends the vector to __OSUnhandledException instead.
        case = Case(rng, self.base_ram)
        case.srr1 &= ~MSR_RI
        self.assertEqual(self.run_case(case)["result"], 0)
        # A non-default GQR0 would change what psq_st/psq_l move.
        case = Case(rng, self.base_ram)
        case.pse = True
        case.hid2 |= 0x20000000
        case.gqr0 = 0x00040004
        self.assertEqual(self.run_case(case)["result"], 0)
        # A context whose FPSCR would change the host rounding mode.
        case = Case(rng, self.base_ram)
        case.owner = case.cur + 0x9000
        struct.pack_into('>I', case.ram, FPU_CTX - RAM_BASE, case.owner)
        case.init_ctx(rng, case.owner)
        struct.pack_into('>H', case.ram, case.cur - RAM_BASE + CTX_STATE, 1)
        struct.pack_into('>I', case.ram, case.cur - RAM_BASE + 0x194, (case.fpscr & ~7) | 3)
        case.fpscr &= ~7
        self.assertEqual(self.run_case(case)["result"], 0)


if __name__ == "__main__":
    unittest.main()
