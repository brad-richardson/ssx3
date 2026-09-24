#!/usr/bin/env python3
"""Copy a PS2XGSC1 stream, forcing every A+D TEX1_1/TEX1_2 write to nearest filtering
(MMAG=0; MMIN 1->0, 3/4/5->2). Prints counts."""
import struct, sys
MMIN_MAP = {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 2}
def patch_gif(d, cnt):
    p, n = 0, len(d)
    while p + 16 <= n:
        lo, hi = struct.unpack_from('<QQ', d, p); p += 16
        nloop = lo & 0x7fff; flg = (lo >> 58) & 3; nreg = (lo >> 60) & 0xf or 16
        if flg == 0:
            regs = [(hi >> (4 * i)) & 0xf for i in range(nreg)]
            if 0xe in regs:
                for l in range(nloop):
                    for r in regs:
                        if r == 0xe and p + 16 <= n:
                            a = d[p + 8]
                            if a in (0x14, 0x15):
                                v, = struct.unpack_from('<Q', d, p)
                                mmag = (v >> 5) & 1; mmin = (v >> 6) & 7
                                nv = (v & ~(0xf << 5)) | (MMIN_MAP.get(mmin, mmin) << 6)
                                if nv != v:
                                    struct.pack_into('<Q', d, p, nv); cnt['patched'] += 1
                                cnt['tex1'] += 1
                        p += 16
            else:
                p += nloop * nreg * 16
        elif flg == 1:
            p += ((nloop * nreg * 8) + 15) & ~15
        else:
            p += nloop * 16
src, dst = sys.argv[1], sys.argv[2]
cnt = {'tex1': 0, 'patched': 0, 'gif': 0}
with open(src, 'rb') as f, open(dst, 'wb') as o:
    o.write(f.read(8))
    while True:
        h = f.read(4)
        if len(h) < 4: break
        L, = struct.unpack('<I', h); rec = bytearray(f.read(L))
        if rec[0] == 1:
            size, = struct.unpack_from('<I', rec, 10)
            mv = memoryview(rec)[14:14 + size]
            patch_gif(mv, cnt); cnt['gif'] += 1
        o.write(h); o.write(rec)
print(cnt)
