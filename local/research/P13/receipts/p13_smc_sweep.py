#!/usr/bin/env python3
"""P13: LUI-only sibling-scan miss census (analysis_passes self-modifying signal).
For each SW/SH/SB/SQ in CSV code ranges: LUI<=5 back to rs? intervening ORI/ADDIU?
Compare LUI-only target vs LUI+lowhalf target membership in code sections."""
import struct, csv
elf_path = "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"
csv_path = "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv"
with open(elf_path, 'rb') as f:
    data = f.read()
end = '<'
e_phoff = struct.unpack(end+'I', data[0x1C:0x20])[0]
e_phentsize, e_phnum = struct.unpack(end+'HH', data[0x2A:0x2E])
segs = []
for i in range(e_phnum):
    o = e_phoff + i*e_phentsize
    t, off, va, pa, fz, mz, fl, al = struct.unpack(end+'IIIIIIII', data[o:o+32])
    segs.append((t, off, va, fz))
e_shoff = struct.unpack(end+'I', data[0x20:0x24])[0]
e_shentsize, e_shnum = struct.unpack(end+'HH', data[0x2E:0x32])
code_secs = []
for i in range(e_shnum):
    o = e_shoff + i*e_shentsize
    name, typ, flags, addr, off, size = struct.unpack(end+'IIIIII', data[o:o+24])
    if flags & 0x4:
        code_secs.append((addr, addr+size))
def rw(va):
    for t, off, va0, fz in segs:
        if t == 1 and va0 <= va < va0 + fz:
            return struct.unpack(end+'I', data[off+(va-va0):off+(va-va0)+4])[0]
    return None
def in_code(va):
    return any(a <= va < b for a, b in code_secs)
OP = lambda w: (w>>26)&0x3F; RS = lambda w: (w>>21)&0x1F; RT = lambda w: (w>>16)&0x1F
IMM = lambda w: w & 0xFFFF
def sx16(v): return v - 0x10000 if v & 0x8000 else v
rows = list(csv.DictReader(open(csv_path)))
n_store = n_lui = n_writer = miss = hit_both = only_low = 0
examples = []
for r in rows:
    st, en = int(r['start'],0), int(r['end'],0)
    a = st
    while a < en:
        w = rw(a)
        if w is None: break
        if OP(w) in (0x2B, 0x29, 0x28, 0x3F):  # SW SH SB SQ
            n_store += 1
            rs = RS(w)
            lui_imm = None
            for back in range(1, 6):
                pw = rw(a - back*4)
                if pw is None: break
                if OP(pw) == 0x0F and RT(pw) == rs:
                    lui_imm = IMM(pw); break
            if lui_imm is not None:
                n_lui += 1
                base = (lui_imm << 16) & 0xFFFFFFFF
                # intervening same-reg ORI/ADDIU strictly between (nearest-LUI approx: scan back region)
                writers = 0
                for back in range(1, 6):
                    mw = rw(a - back*4)
                    if mw is None: break
                    if OP(mw) == 0x0F and RT(mw) == rs: break
                    if RT(mw) == rs and RS(mw) == rs and OP(mw) in (0x0D, 0x09):
                        writers += 1
                        if OP(mw) == 0x0D: base |= IMM(mw)
                        else: base = (base + sx16(IMM(mw))) & 0xFFFFFFFF
                tgt_lui = ((lui_imm << 16) + sx16(IMM(w))) & 0xFFFFFFFF
                tgt_full = (base + sx16(IMM(w))) & 0xFFFFFFFF
                if writers: n_writer += 1
                c_lui, c_full = in_code(tgt_lui), in_code(tgt_full)
                if c_lui and c_full: hit_both += 1
                elif c_full and not c_lui:
                    only_low += 1
                    if len(examples) < 10: examples.append((hex(a), hex(tgt_lui), hex(tgt_full)))
        a += 4
print(f"stores={n_store} with_lui={n_lui} with_writer={n_writer} hit_both={hit_both} only_with_lowhalf={only_low}")
for x in examples: print("  MISS", x)
