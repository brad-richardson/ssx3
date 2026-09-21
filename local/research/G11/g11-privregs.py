#!/usr/bin/env python3
# G11: per-vsync PrivRegs decode from the G8 dump's own bytes (read-only).
# Framing: G10 g10-boundary.py (id0 Transfer / id1 Vsync:u8 phase /
# id2 ReadFIFO / id3 PrivRegs:8192B). Priv layout: paraLLEl-GS
# PrivRegisterState (gs_interface.hpp:70) == PS2 GS HW offsets, 16B stride:
# pmode@0 smode1@16 smode2@32 dispfb1@112 display1@128 dispfb2@144
# display2@160 extwrite@208 bgcolor@224 csr@4096. Each reg = 2x u32 LE.
# Answers: does DISPFB FBP flip per vsync (double-buffer) or stay constant
# (single-buffer)? INT/FFMD/EN1/EN2 per vsync? VSync phase per vsync?
import struct, sys, hashlib

def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def dispfb(b, o):
    w0, w1 = u32(b, o), u32(b, o + 4)
    return dict(FBP=w0 & 0x1ff, FBW=(w0 >> 9) & 0x3f, PSM=(w0 >> 15) & 0x1f,
                DBX=w1 & 0x7ff, DBY=(w1 >> 11) & 0x7ff)

def display(b, o):
    w0, w1 = u32(b, o), u32(b, o + 4)
    return dict(DX=w0 & 0xfff, DY=(w0 >> 12) & 0x7ff, MAGH=(w0 >> 23) & 0xf,
                MAGV=(w0 >> 27) & 0x3, DW=w1 & 0xfff, DH=(w1 >> 12) & 0x7ff)

def main(path):
    b = open(path, 'rb').read()
    n = len(b)
    print(f"size={n} sha256={hashlib.sha256(b).hexdigest()[:16]}")
    o = 8
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o); o += 36
    o += serial_sz + shot_sz + state_size + 8192
    ordinal, nv = 0, 0
    cur = []  # transfer sizes since last vsync
    priv = None
    while o < n:
        pid = b[o]; o += 1
        assert pid in (0, 1, 2, 3), (o, pid)
        if pid == 0:
            idx = b[o]; o += 1
            sz = u32(b, o); o += 4
            cur.append((idx, sz)); o += sz
        elif pid == 3:
            priv = o; o += 8192
        elif pid == 1:
            f = b[o]; o += 1
            p = priv
            pm = u32(b, p + 0)
            sm1 = u32(b, p + 16)
            sm2 = u32(b, p + 32)
            f1, d1 = dispfb(b, p + 112), display(b, p + 128)
            f2, d2 = dispfb(b, p + 144), display(b, p + 160)
            exw = u32(b, p + 208)
            bg = u32(b, p + 224)
            csr = u32(b, p + 4096)
            nx = len(cur); tb = sum(s for _, s in cur)
            print(f"dump-vsync#{nv}: phase={f} nxfer={nx} xferB={tb}")
            print(f"  PMODE EN1={(pm>>0)&1} EN2={(pm>>1)&1} MMOD={(pm>>5)&1} "
                  f"SLBG={(pm>>7)&1} ALP={(pm>>8)&0xff}")
            print(f"  SMODE1 CMOD={(sm1>>13)&3} LC={(sm1>>3)&0x7f} "
                  f"SMODE2 INT={(sm2>>0)&1} FFMD={(sm2>>1)&1} "
                  f"CSR NFIELD={(csr>>12)&1} FIELD={(csr>>13)&1}")
            print(f"  DISPFB1 FBP={f1['FBP']} FBW={f1['FBW']} PSM={f1['PSM']} "
                  f"DBX={f1['DBX']} DBY={f1['DBY']}")
            print(f"  DISPLAY1 DX={d1['DX']} DY={d1['DY']} MAGH={d1['MAGH']} "
                  f"MAGV={d1['MAGV']} DW={d1['DW']} DH={d1['DH']}")
            print(f"  DISPFB2 FBP={f2['FBP']} FBW={f2['FBW']} PSM={f2['PSM']} "
                  f"DBX={f2['DBX']} DBY={f2['DBY']}")
            print(f"  DISPLAY2 DX={d2['DX']} DY={d2['DY']} MAGH={d2['MAGH']} "
                  f"MAGV={d2['MAGV']} DW={d2['DW']} DH={d2['DH']}")
            print(f"  EXTWRITE={exw&1} BGCOLOR=({bg&0xff},{(bg>>8)&0xff},{(bg>>16)&0xff})")
            nv += 1; cur = []
        elif pid == 2:
            o += 4
        ordinal += 1
    print(f"EOF_SYNC={'yes' if o == n else f'NO off={o-n}'} vsyncs={nv}")

if __name__ == '__main__':
    main(sys.argv[1])
