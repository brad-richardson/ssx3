#!/usr/bin/env python3
"""PX1: force STQ/RGBAQ Q to 1.0 on every PACKED/A+D STQ/RGBAQ write in a .gs
(except PATH3 transfers, so the composite is untouched). Discriminates
whether tiny-Q (3e-05..6e-04 on world verts; menus are Q=1.0) is what breaks
PCSX2: if the world appears, Q handling diverges (our backends mask it).
Usage: px1_qone.py <in.gs> <out.gs>
"""
import struct, sys

QONE = struct.pack('<f', 1.0)
src, dst = sys.argv[1], sys.argv[2]
b = bytearray(open(src, 'rb').read())
o = 8
ver, ss, so, ssz, crc, w, h, sho, shs = struct.unpack_from('<9I', b, o)
o += 36 + ssz + shs + ss + 8192
n = len(b)
nq = 0


def patch_stream(data):
    global nq
    o = 0
    ln = len(data)
    while o + 16 <= ln:
        tag_lo, tag_hi = struct.unpack_from('<QQ', data, o)
        o += 16
        nloop = tag_lo & 0x7FFF
        flg = (tag_lo >> 58) & 3
        nreg = (tag_lo >> 60) & 0xF
        if nreg == 0:
            nreg = 16
        if flg == 0:
            regs = [(tag_hi >> (4 * i)) & 0xF for i in range(nreg)]
            for _ in range(nloop):
                for r in regs:
                    if o + 16 > ln:
                        break
                    if r == 0x2:  # STQ: Q = float at bytes 8..12
                        data[o + 8:o + 12] = QONE
                        nq += 1
                    elif r == 0x1:  # RGBAQ: Q = float at bytes 4..8
                        data[o + 4:o + 8] = QONE
                        nq += 1
                    elif r == 0xE:  # A+D
                        v0, v1, aid = struct.unpack_from('<IIQ', data, o)
                        if (aid & 0xFF) == 0x02:  # STQ
                            data[o + 8:o + 12] = QONE
                            nq += 1
                        elif (aid & 0xFF) == 0x01:  # RGBAQ
                            data[o + 4:o + 8] = QONE
                            nq += 1
                    o += 16
        elif flg == 1:
            vals = nloop * nreg
            o += vals * 8 + (8 if vals & 1 else 0)
        else:
            o += nloop * 16
        if o > ln:
            break


while o < n:
    pid = b[o]
    o += 1
    if pid == 0:
        idx = b[o]
        size = struct.unpack_from('<I', b, o + 1)[0]
        o += 5
        if idx != 2:
            seg = b[o:o + size]
            patch_stream(seg)
            b[o:o + size] = seg
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
print(f'q_patched={nq}')
