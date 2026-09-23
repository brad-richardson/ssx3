#!/usr/bin/env python3
"""G46: convert a PS2X_GS_SHADOW_REC stream (G46REC1) to a PCSX2 .gs dump.

Usage: g46_rec2gs.py <rec> <out.gs> [--to TICK] [--force-smode1-ntsc]

The .gs starts from a clean GS (state v9, all-zero registers + VRAM; the
recorder runs from boot so every upload is in the stream). Each recorder
'V' (one present, with the EE-visible priv regs) becomes a Registers
packet + a VSync packet (field = tick & 1). 'G' packets become Transfer
packets (path 1 -> Path1New=3, 2 -> Path2=1, 3 -> Path3=2). 'R' (HLE reg
writes) become a one-register A+D PATH3 packet.

--force-smode1-ntsc mirrors G44's DIAGNOSTIC shadow override: when the
game's SMODE1 is 0, write the PCSX2 NTSC value 0x40814504 (G29) so the scanout has a mode.
A tick list (vsync index -> guest tick) is written to <out.gs>.ticks.
"""
import struct
import sys

STATE_SIZE = 4194813   # t48b-dump.gs header (PCSX2 9056c083, STATE_VERSION 9)
SERIAL = b"SLUS-20772"
CRC = 150990861        # t48b-dump.gs header crc
PATH_MAP = {1: 3, 2: 1, 3: 2}


def priv_block(v, force):
    # GSPrivRegSet: 0x2000 bytes; regs at 16-byte strides from 0.
    b = bytearray(0x2000)
    names = ["pmode", "smode1", "smode2", "srfsh", "synch1", "synch2", "syncv",
             "dispfb1", "display1", "dispfb2", "display2", "extbuf", "extdata",
             "extwrite", "bgcolor"]
    for i, val in enumerate(v):
        if names[i] == "smode1" and force and val == 0:
            val = 0x40814504  # G13/G29 PCSX2 SMODE1: RC=4 LC=32 T1248=1 CMOD=NTSC
        struct.pack_into("<Q", b, i * 16, val)
    # CSR at 0x1000: FIELD bit toggles are not needed by the replayer.
    return bytes(b)


def main():
    args = sys.argv[1:]
    force = "--force-smode1-ntsc" in args
    to = None
    if "--to" in args:
        to = int(args[args.index("--to") + 1])
    rec, out = [a for a in args if not a.startswith("--") and not a.isdigit()][:2]
    data = open(rec, "rb").read()
    assert data[:8] == b"G46REC1\0", "bad magic"
    o = open(out, "wb")
    hdr_size = 36 + len(SERIAL)
    o.write(struct.pack("<II", 0xFFFFFFFF, hdr_size))
    o.write(struct.pack("<9I", 9, STATE_SIZE, 36, len(SERIAL), CRC, 0, 0,
                        36 + len(SERIAL), 0))
    o.write(SERIAL)
    state = bytearray(STATE_SIZE)
    struct.pack_into("<I", state, 0, 9)
    o.write(state)
    # Initial regs: first V record's values (scan ahead).
    first_v = data.find(b"V", 8)
    p = 8
    ticks = []
    wrote_init = False
    counts = {"G": 0, "R": 0, "V": 0}
    while p < len(data):
        t = data[p:p + 1]
        if t == b"G":
            path, size = struct.unpack_from("<BI", data, p + 1)
            pkt = data[p + 6:p + 6 + size]
            if len(pkt) < size:
                break
            if not wrote_init:
                o.write(bytes(0x2000))
                wrote_init = True
            o.write(struct.pack("<BBI", 0, PATH_MAP[path], size))
            o.write(pkt)
            p += 6 + size
        elif t == b"R":
            addr, val = struct.unpack_from("<BQ", data, p + 1)
            if not wrote_init:
                o.write(bytes(0x2000))
                wrote_init = True
            # GIFtag: NLOOP=1 EOP=1 FLG=PACKED NREG=1 REGS=0xE (A+D)
            tag = struct.pack("<QQ", 1 | (1 << 15) | (1 << 60), 0xE)
            ad = struct.pack("<QQ", val, addr)
            o.write(struct.pack("<BBI", 0, 2, 32))
            o.write(tag + ad)
            p += 10
        elif t == b"V":
            if p + 1 + 128 > len(data):
                break
            v = struct.unpack_from("<16Q", data, p + 1)
            tick = v[0]
            if to is not None and tick >= to:
                break
            if not wrote_init:
                o.write(priv_block(v[1:], force))
                wrote_init = True
            o.write(struct.pack("<B", 3))
            o.write(priv_block(v[1:], force))
            o.write(struct.pack("<BB", 1, tick & 1))
            ticks.append(tick)
            p += 129
        else:
            raise SystemExit(f"bad record type {t!r} at {p}")
        counts[t.decode()] += 1
    o.close()
    with open(out + ".ticks", "w") as f:
        for i, t in enumerate(ticks):
            f.write(f"{i} {t}\n")
    print(f"records G={counts['G']} R={counts['R']} V={counts['V']} "
          f"vsyncs={len(ticks)} last_tick={ticks[-1] if ticks else None}")


if __name__ == "__main__":
    main()
