#!/usr/bin/env python3
"""AC1 helper: read-only ELF word reads + gap-tolerant MIPS disassembly.

Same ELF mapping as /tmp/a0_elf.py (A0/K1 precedent, read-only). Differs only
in that disassembly is per-word and gap-tolerant: words capstone rejects (e.g.
R5900 MULT with rd>3) are printed as `.word` instead of aborting the sweep.
"""
import struct, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ELF = "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"

def load_segments(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"\x7fELF", "not ELF"
    e_phoff = struct.unpack("<I", data[0x1C:0x20])[0]
    e_phentsize = struct.unpack("<H", data[0x2A:0x2C])[0]
    e_phnum = struct.unpack("<H", data[0x2C:0x2E])[0]
    segs = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack("<IIIIIIII", data[off:off+32])
        segs.append((p_type, p_offset, p_vaddr, p_filesz, p_memsz))
    return data, segs

DATA, SEGS = load_segments(ELF)

def vaddr_to_off(v):
    for (t, off, va, fsz, msz) in SEGS:
        if t != 1:
            continue
        if va <= v < va + msz:
            if v - va >= fsz:
                return None
            return off + (v - va)
    return None

def read_words(v, n):
    out = []
    for i in range(n):
        o = vaddr_to_off(v + 4*i)
        out.append(None if o is None else struct.unpack("<I", DATA[o:o+4])[0])
    return out

MD = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
MD.detail = False

def disas_gap(v, ninsn):
    for i in range(ninsn):
        a = v + 4*i
        o = vaddr_to_off(a)
        if o is None:
            print(f"0x{a:08x}: -------- BSS/unmapped")
            continue
        raw = DATA[o:o+4]
        w = struct.unpack("<I", raw)[0]
        ok = False
        for ins in MD.disasm(raw, a):
            print(f"0x{ins.address:08x}: {ins.bytes.hex():<10} {ins.mnemonic:<10} {ins.op_str}")
            ok = True
            break
        if not ok:
            print(f"0x{a:08x}: {raw.hex():<10} .word      0x{w:08x}")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "words":
        v = int(sys.argv[2], 0); n = int(sys.argv[3])
        for i, w in enumerate(read_words(v, n)):
            print(f"0x{v+4*i:08x}: {w if w is None else f'0x{w:08x} ({w})'}")
    elif cmd == "dis":
        disas_gap(int(sys.argv[2], 0), int(sys.argv[3]))
    elif cmd == "segs":
        for s in SEGS:
            print(s)
