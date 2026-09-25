#!/usr/bin/env python3
"""PX1: convert our PS2XGSC1 capture (PS2X_GS_CAPTURE) to a PCSX2 .gs dump.

Adapted from RR1's rr1_cap2gs.py (= G46's g46_rec2gs.py header/state constants).
  Packet(1)       -> Transfer (path 1 -> Path1New=3, 2 -> Path2=1, 3 -> Path3=2)
  NativeUpload(5) -> a PATH3 packet: A+D BITBLTBUF/TRXPOS/TRXREG/TRXDIR, then IMAGE
  PrivWrite(2)    -> updates the priv block (offset & 0x1FFF)
  VBlank(4)       -> Regs + VSync (field = tick & 1)
  Transfer(3)     -> skipped (the TRXDIR write is already inside a Packet)
  ClearContext(7), LocalToHost(6) -> counted, not converted (gap)
Usage: px1_cap2gs.py <gs.cap> <out.gs> [--to TICK] [--force-smode1-ntsc]
                     [--texflush-after-upload] [--p3-to-p1]
Writes <out.gs>.ticks (vsync index -> tick).

--texflush-after-upload (PX1 candidate fix, REFUTED 2026-09-25: full-stream
replay byte-identical to baseline, md5 41d7b61f…; texture cache is not the
issue): after every packet
containing an IMAGE transfer, append a PATH3 Transfer with a single A+D
TEXFLUSH write. Lead mechanism (REPORT.md): the race uploads pixels as CT32
but samples them as PSMT8/PSMT4 (mixed-PSM), and PCSX2-HW's texture cache
misses the cross-PSM invalidation, serving stale-black entries; our backends
have no texture cache and sample VRAM directly. Menus upload native-PSM and
replay correctly. TEXFLUSH is a hardware-neutral cache hint (flush is always
safe), so the flag cannot change a correct replay, only force re-fetch.
Validate: convert the full capture with the flag, replay on the T48-pinned
gsrunner, expect the race world (not HUD-only) at 1800/2100/2400.

--p3-to-p1 (PX1 experiment): relabel PATH3 packets as PATH1 (Transfer
index 3). Rationale: healthy PCSX2 dumps of this game carry zero PATH2/3
traffic (T48), so the replayer's PATH3-IMAGE path is untested; our stream
delivers all uploads on PATH3. Our capture has no path-interleaved
transfers (px1_imgspan: zero mid-stream label flips), so for a serial
replayer the path label is effect-neutral and relabeling is
semantics-preserving. If the world appears, the mechanism is a
PATH3-conditional drop in the replayer.
"""
import struct, sys

STATE_SIZE = 4194813
SERIAL = b"SLUS-20772"
CRC = 150990861
PATH_MAP = {1: 3, 2: 1, 3: 2}
REG_TEXFLUSH = 0x3F


def packet_has_image(data):
    """True if the GIF stream contains an IMAGE-mode GIFtag with NLOOP > 0."""
    try:
        o, n = 0, len(data)
        while o + 16 <= n:
            tag_lo, tag_hi = struct.unpack_from("<QQ", data, o)
            o += 16
            nloop = tag_lo & 0x7FFF
            flg = (tag_lo >> 58) & 3
            nreg = (tag_lo >> 60) & 0xF
            if nreg == 0:
                nreg = 16
            if flg == 0:
                o += nloop * nreg * 16
            elif flg == 1:
                o += nloop * nreg * 8 + (8 if (nloop * nreg) & 1 else 0)
            else:
                if nloop > 0:
                    return True
                # NLOOP 0: no payload; keep scanning
            if o > n:
                break
    except struct.error:
        pass
    return False


def texflush_packet():
    """One PACKED GIFtag (NLOOP=1 EOP NREG=1 REGS=A+D) + TEXFLUSH A+D write."""
    tag = struct.pack("<QQ", 1 | (1 << 15) | (1 << 60), 0xE)
    return tag + struct.pack("<QQ", 0, REG_TEXFLUSH)


def main():
    a = sys.argv[1:]
    force = "--force-smode1-ntsc" in a
    texflush = "--texflush-after-upload" in a
    pmap = dict(PATH_MAP)
    if "--p3-to-p1" in a:
        pmap[3] = 3
    to = int(a[a.index("--to") + 1]) if "--to" in a else None
    ntexflush = 0
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
            payload = body[5:5 + sz]
            o.write(struct.pack("<BBI", 0, pmap[path], sz))
            o.write(payload)
            if texflush and packet_has_image(payload):
                pk = texflush_packet()
                o.write(struct.pack("<BBI", 0, 2, len(pk)))
                o.write(pk)
                ntexflush += 1
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
    print("records", counts, "vsyncs", len(ticks), "last_tick", ticks[-1] if ticks else None,
          "texflush_inserted", ntexflush)


if __name__ == "__main__":
    main()
