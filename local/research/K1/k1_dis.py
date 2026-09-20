#!/usr/bin/env python3
"""K1 helper: disassemble the 0x4561C0 payload at its destination base 0x80075000 (read-only)."""
import struct, sys
sys.path.insert(0, "/tmp")
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN
import importlib.util
spec = importlib.util.spec_from_file_location("a0_elf", "/tmp/a0_elf.py")
a0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a0)

SRC = 0x4561C0
DST = 0x80075000
N = int(sys.argv[1]) if len(sys.argv) > 1 else 0xCC  # 0x330 bytes = 204 insn

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
md.detail = False
o = a0.vaddr_to_off(SRC)
code = a0.DATA[o:o + 4 * N]
for ins in md.disasm(code, DST):
    print(f"0x{ins.address:08x}: {ins.bytes.hex():<10} {ins.mnemonic:<10} {ins.op_str}")
