#!/usr/bin/env python3
"""RR1: convert our PS2XGSC1 capture (PS2X_GS_CAPTURE) to a PCSX2 .gs dump.

Adapted from G46's g46_rec2gs.py (same header/state constants).
  Packet(1)       -> Transfer (path 1 -> Path1New=3, 2 -> Path2=1, 3 -> Path3=2)
  NativeUpload(5) -> a PATH3 packet: A+D BITBLTBUF/TRXPOS/TRXREG/TRXDIR, then IMAGE
  PrivWrite(2)    -> updates the priv block (offset & 0x1FFF)
  VBlank(4)       -> Regs + VSync (field = tick & 1)
  Transfer(3)     -> skipped (the TRXDIR write is already inside a Packet)
  ClearContext(7), LocalToHost(6) -> counted, not converted (gap)
Usage: rr1_cap2gs.py <gs.cap> <out.gs> [--to TICK] [--force-smode1-ntsc]
Writes <out.gs>.ticks (vsync index -> tick).
"""
import struct, sys

STATE_SIZE = 4194813
SERIAL = b"SLUS-20772"
CRC = 150990861
PATH_MAP = {1: 3, 2: 1, 3: 2}


def main():
    a = sys.argv[1:]
    force = "--force-smode1-ntsc" in a
    to = int(a[a.index("--to") + 1]) if "--to" in a else None
    cap, out = [x for x in a if not x.startswith("--") and not x.isdigit()][:2]
    f = open(cap, "rb")
    assert f.read(8) == b"PS2XGSC1"
    o = open(out, "wb")
    o.write(struct.pack("<II", 0xFFFFFFFF, 36 + len(SERIAL)))
    o.write(struct.pack("<9I", 9, STATE_SIZE, 36, len(SERIAL), CRC, 0, 0, 36 + len(SERIAL), 0))
    o.write(SERIAL)
    st = bytearray(STATE_SIZE)
    struct.pack_into("<I", st, 0, 9)
    o.write(st)
    priv = bytearray(0x2000)
    o.write(bytes(priv))  # initial regs (all zero; first VBlank writes the real ones)
    ticks, counts = [], {}
    while True:
        h = f.read(4)
        if len(h) < 4:
            break
        (n,) = struct.unpack("<I", h)
        rec = f.read(n)
        if len(rec) < n:
            break
        kind = rec[0]
        (tick,) = struct.unpack_from("<Q", rec, 1)
        body = rec[9:]
        counts[kind] = counts.get(kind, 0) + 1
        if to is not None and tick >= to and kind == 4:
            break
        if kind == 1:
            path = body[0]
            (sz,) = struct.unpack_from("<I", body, 1)
            o.write(struct.pack("<BBI", 0, PATH_MAP[path], sz))
            o.write(body[5:5 + sz])
        elif kind == 5:
            bb, tp, tr, td = struct.unpack_from("<4Q", body, 0)
            (sz,) = struct.unpack_from("<I", body, 32)
            data = body[36:36 + sz]
            qw = (sz + 15) // 16
            data = data + bytes(qw * 16 - sz)
            pk = struct.pack("<QQ", 4 | (1 << 60), 0xE)  # PACKED NLOOP=4 NREG=1 A+D
            for reg, val in ((0x50, bb), (0x51, tp), (0x52, tr), (0x53, td)):
                pk += struct.pack("<QQ", val, reg)
            pk += struct.pack("<QQ", qw | (1 << 15) | (2 << 58), 0)  # IMAGE, EOP
            pk += data
            o.write(struct.pack("<BBI", 0, 2, len(pk)))
            o.write(pk)
        elif kind == 2:
            off, val = struct.unpack_from("<IQ", body, 0)
            off &= 0x1FFF
            if off + 8 <= 0x2000:
                struct.pack_into("<Q", priv, off, val)
        elif kind == 4:
            p = bytearray(priv)
            if force and struct.unpack_from("<Q", p, 0x10)[0] == 0:
                struct.pack_into("<Q", p, 0x10, 0x40814504)
            o.write(struct.pack("<B", 3))
            o.write(bytes(p))
            o.write(struct.pack("<BB", 1, tick & 1))
            ticks.append(tick)
    o.close()
    with open(out + ".ticks", "w") as t:
        for i, tk in enumerate(ticks):
            t.write(f"{i} {tk}\n")
    print("records", counts, "vsyncs", len(ticks), "last_tick", ticks[-1] if ticks else None)


if __name__ == "__main__":
    main()
