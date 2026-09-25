#!/usr/bin/env python3
"""PX1: clear PRIM.TME (bit 4) on every PRIM write in a .gs to force all
draws untextured (flat vertex colors). Decisive test: if the world appears
(flat gray) the draws execute and sampling is the failure; if still black
the draws are dropped upstream of rasterization.
Usage: px1_notex.py <in.gs> <out.gs>
Patches PACKED-mode PRIM regs (0x00) and A+D PRIM writes (addr 0x00).
Skips PATH3 (index 2) transfers so the TBP0->FBP112 composite keeps
sampling (otherwise FBP 112 goes flat and hides FBP 0).
"""
import struct, sys

src, dst = sys.argv[1], sys.argv[2]
b = bytearray(open(src, 'rb').read())
o = 8
ver, ss, so, ssz, crc, w, h, sho, shs = struct.unpack_from('<9I', b, o)
o += 36 + ssz + shs + ss + 8192
n = len(b)
npack = nprim = 0


def patch_stream(data, base):
    """Patch PRIM writes in one GIF stream; returns count."""
    global nprim
    c = 0
    o = 0
    ln = len(data)
    while o + 16 <= ln:
        tag_lo, tag_hi = struct.unpack_from('<QQ', data, o)
        if (tag_lo >> 46) & 1 and (tag_lo >> 51) & 1:
            # PRE=1 with TME set in tag.PRIM: clear it (bit 51).
            struct.pack_into('<Q', data, o, tag_lo & ~(1 << 51))
            tag_lo &= ~(1 << 51)
            c += 1
        o += 16
        nloop = tag_lo & 0x7FFF
        flg = (tag_lo >> 58) & 3
        eop = (tag_lo >> 15) & 1
        nreg = (tag_lo >> 60) & 0xF
        if nreg == 0:
            nreg = 16
        if flg == 0:
            regs = [(tag_hi >> (4 * i)) & 0xF for i in range(nreg)]
            for _ in range(nloop):
                for r in regs:
                    if o + 16 > ln:
                        break
                    if r == 0x0:  # PRIM packed reg: low 11 bits
                        v, = struct.unpack_from('<Q', data, o)
                        if v & 0x10:
                            struct.pack_into('<Q', data, o, v & ~0x10)
                            c += 1
                    elif r == 0xE:  # A+D
                        v, aid = struct.unpack_from('<QQ', data, o)
                        if (aid & 0xFF) == 0x00 and v & 0x10:
                            struct.pack_into('<Q', data, o, v & ~0x10)
                            c += 1
                    o += 16
        elif flg == 1:
            regs = []
            for i in range(nreg):
                regs.append((tag_hi >> (4 * (i % 16))) & 0xF if i < 16 else 0)
            # REGLIST data: 64-bit values; descriptors repeat every 16 regs
            vals = nloop * nreg
            for i in range(vals):
                if o + 8 > ln:
                    break
                r = regs[i % nreg] if nreg <= 16 else regs[i % 16]
                if r == 0x0:
                    v, = struct.unpack_from('<Q', data, o)
                    if v & 0x10:
                        struct.pack_into('<Q', data, o, v & ~0x10)
                        c += 1
                o += 8
            if vals & 1:
                o += 8
        else:
            o += nloop * 16
        if o > ln:
            break
    nprim += c
    return c


while o < n:
    pid = b[o]
    o += 1
    if pid == 0:
        idx = b[o]
        size = struct.unpack_from('<I', b, o + 1)[0]
        o += 5
        if idx != 2:
            seg = b[o:o + size]
            patch_stream(seg, o)
            b[o:o + size] = seg
            npack += 1
        o += size
    elif pid == 1:
        o += 1
    elif pid == 2:
        o += 4
    elif pid == 3:
        o += 8192
    else:
        raise ValueError(f'bad packet id {pid}')
open(dst, 'wb').write(b)
print(f'transfers={npack} prim_tme_cleared={nprim}')
