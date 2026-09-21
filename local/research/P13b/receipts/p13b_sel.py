#!/usr/bin/env python3
"""P13b: selector context miner (read-only ELF scan).
For each unmatched stub selector: owner prologue, selector context disasm,
JAL-to-selector census, T5-shape materialization census, mid-function JALs.
"""
import struct, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

ELF = "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"
SELS = [
    ("_sceSifCmdIntrHdlr", 0x426230, "sub_004261F0", 0x4261f0, 0x426358),
    ("sceSifLoadIopHeap", 0x42ad28, "sub_0042AD08", 0x42ad08, 0x42b068),
    ("sceSifLoadFileReset", 0x42b1f8, "sub_0042B168", 0x42b168, 0x42b230),
    ("InitTLB", 0x42cd58, "sub_0042CCB8", 0x42ccb8, 0x42cd98),
]

data = open(ELF, "rb").read()
end = "<"
e_phoff = struct.unpack(end + "I", data[0x1C:0x20])[0]
e_phentsize, e_phnum = struct.unpack(end + "HH", data[0x2A:0x2E])
e_shoff = struct.unpack(end + "I", data[0x20:0x24])[0]
e_shentsize, e_shnum = struct.unpack(end + "HH", data[0x2E:0x32])
SHF_EXEC = 0x4
secs = []
for i in range(e_shnum):
    o = e_shoff + i * e_shentsize
    name, typ, flags, addr, off, size = struct.unpack(end + "IIIIII", data[o:o + 24])[:6]
    secs.append(dict(flags=flags, addr=addr, off=off, size=size))
code_secs = [s for s in secs if (s["flags"] & SHF_EXEC) and s["size"] >= 4]

def va_word(va):
    for s in secs:
        if s["addr"] <= va < s["addr"] + s["size"] and s["off"] + (va - s["addr"]) + 4 <= len(data):
            return struct.unpack(end + "I", data[s["off"] + (va - s["addr"]):s["off"] + (va - s["addr"]) + 4])[0]
    return None

def in_code(va):
    for s in code_secs:
        if s["addr"] <= va < s["addr"] + s["size"]:
            return s
    return None

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
md.detail = False

def dis(va, n):
    out = []
    for i in range(n):
        w = va_word(va + i * 4)
        if w is None:
            out.append((va + i * 4, None, "??"))
            continue
        b = struct.pack(end + "I", w)
        ins = list(md.disasm(b, va + i * 4, 1))
        s = f"{ins[0].mnemonic} {ins[0].op_str}".strip() if ins else "(undecodable)"
        out.append((va + i * 4, w, s))
    return out

# Pass 1: JAL census + T5-shape materialization over all code
jal_to = {}   # tgt -> [src...]
mat_to = {}   # folded -> [(lui_pc, kind)...]
OP = lambda w: (w >> 26) & 0x3F
RS = lambda w: (w >> 21) & 0x1F
RT = lambda w: (w >> 16) & 0x1F
IMM = lambda w: w & 0xFFFF
for s in code_secs:
    n = s["size"] // 4
    words = [struct.unpack(end + "I", data[s["off"] + i * 4:s["off"] + i * 4 + 4])[0] for i in range(n)]
    base = s["addr"]
    for i, w in enumerate(words):
        pc = base + i * 4
        if OP(w) == 0x03:  # JAL
            tgt = ((pc + 4) & 0xF0000000) | ((w & 0x03FFFFFF) << 2)
            jal_to.setdefault(tgt, []).append(pc)
        if OP(w) == 0x0F:  # LUI
            rt = RT(w)
            if rt == 0:
                continue
            folded = IMM(w) << 16
            applied = False
            for la in range(1, 6):
                if i + la >= n:
                    break
                m = words[i + la]
                if RT(m) == rt and RS(m) == rt:
                    if OP(m) == 0x0D:  # ORI
                        folded |= IMM(m); applied = True
                    elif OP(m) == 0x09:  # ADDIU
                        folded = (folded + struct.unpack(end + "h", struct.pack(end + "H", IMM(m)))[0]) & 0xFFFFFFFF
                        applied = True
            if applied and (folded & 3) == 0 and in_code(folded):
                mat_to.setdefault(folded, []).append((pc, "lui+low"))

for name, sel, owner, ostart, oend in SELS:
    print(f"===== {name}@0x{sel:x} owner {owner} [0x{ostart:x}-0x{oend:x}) off=+0x{sel - ostart:x} =====")
    print("-- owner entry:")
    for va, w, s in dis(ostart, 4):
        print(f"  0x{va:x}: {('0x%08x' % w) if w is not None else '????????'}  {s}")
    print("-- selector context (sel-8 .. sel+32):")
    for va, w, s in dis(sel - 8, 11):
        mark = " <== SELECTOR" if va == sel else (" <== owner entry" if va == ostart else "")
        print(f"  0x{va:x}: {('0x%08x' % w) if w is not None else '????????'}  {s}{mark}")
    js = jal_to.get(sel, [])
    print(f"-- JAL-to-selector: {len(js)} {['0x%x' % p for p in js[:20]]}")
    ms = mat_to.get(sel, [])
    print(f"-- T5-materializations of selector: {len(ms)} {['0x%x/%s' % p for p in ms[:20]]}")
    mid_jal = [(t, srcs) for t, srcs in jal_to.items() if ostart < t < oend and t != sel]
    mid_jal.sort()
    print(f"-- other mid-function JAL targets in owner: {len(mid_jal)}")
    for t, srcs in mid_jal[:15]:
        print(f"    tgt=0x{t:x} from={['0x%x' % p for p in srcs[:6]]}{'...' if len(srcs) > 6 else ''} (n={len(srcs)})")
    # JALs to owner start (is owner called?)
    os_ = jal_to.get(ostart, [])
    print(f"-- JAL-to-owner-start 0x{ostart:x}: {len(os_)} {['0x%x' % p for p in os_[:10]]}{'...' if len(os_) > 10 else ''}")
    print()
