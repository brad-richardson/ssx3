#!/usr/bin/env python3
"""AU1: ISO9660 walk -> "lbn sectors size path" for every file (sorted by LBN)."""
import struct, sys
iso = open(sys.argv[1], "rb")
def sec(l, n=1): iso.seek(l * 2048); return iso.read(n * 2048)
pvd = sec(16); root = pvd[156:190]
out = []
def walk(rec, path):
    lbn, size = struct.unpack_from("<I", rec, 2)[0], struct.unpack_from("<I", rec, 10)[0]
    data = sec(lbn, (size + 2047) // 2048); p = 0
    while p < size:
        ln = data[p]
        if ln == 0: p = (p // 2048 + 1) * 2048; continue
        r = data[p:p+ln]; nl = r[32]; name = r[33:33+nl].decode("latin1")
        if name not in ("\x00", "\x01"):
            flg = r[25]; nm = name.split(";")[0]
            if flg & 2: walk(r, path + nm + "/")
            else:
                l, s = struct.unpack_from("<I", r, 2)[0], struct.unpack_from("<I", r, 10)[0]
                out.append((l, (s + 2047) // 2048, s, path + nm))
        p += ln
walk(root, "/")
for l, n, s, pth in sorted(out): print(f"{l:#09x} {n:8d} {s:11d} {pth}")
