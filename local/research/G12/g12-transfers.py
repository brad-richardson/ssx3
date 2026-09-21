#!/usr/bin/env python3
"""G12: read-only scan of .gs Transfer payloads for image-upload destinations.

Walks the GIF stream in each Transfer packet (PACKED + REGLIST tags, IMAGE-mode
accounting via TRXDIR/TRXREG+DPSM) and reports, per dump-vsync:
  - A+D writes to image-transfer regs (0x50 BITBLTBUF, 0x51 TRXPOS, 0x52 TRXREG,
    0x53 TRXDIR; ADDRs verified against Gif_Unit.cpp at the pinned rev)
  - decoded DBP/DPSM/DIR/RRW/RHW + IMAGE bytes consumed per transfer
  - (bonus) PRIM-reg values + FRAME_1/2 writes (0x3C/0x3D, standard table) to
    reconstruct the in-packet prim order (C/U/S hypothesis test)

Framing reused from G10 g10-boundary.py. Read-only; asserts EOF-sync.
"""
import struct
import sys

PSM_BPP = {0x00: 4, 0x01: 3, 0x02: 2, 0x0A: 2, 0x13: 1, 0x14: 0.5,
           0x1B: 1, 0x24: 0.5, 0x2C: 0.5, 0x30: 4, 0x31: 3, 0x32: 2, 0x3A: 2}
PACKED_NAMES = {0x0: "PRIM", 0x1: "RGBA", 0x2: "ST", 0x3: "UV", 0x4: "XYZF2",
                0x5: "XYZ2", 0x6: "TEX0_1", 0x7: "TEX0_2", 0x8: "CLAMP_1",
                0x9: "CLAMP_2", 0xA: "FOG", 0xC: "XYZF3", 0xD: "XYZ3",
                0xE: "AD", 0xF: "NOP"}


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def u64(b, o):
    return struct.unpack_from('<Q', b, o)[0]


def walk_transfer(payload, vno, tno):
    """Returns (ad_writes, image_qwads, prims, notes).
    ad_writes: list of (addr, data). prims: list of PRIM-reg values (PACKED)."""
    nq = len(payload) // 16
    q = 0
    ad, prims, notes = [], [], []
    img_left = 0  # qwads of IMAGE data still to consume
    tags = 0
    # live image-transfer regs (for IMAGE accounting)
    blt = (None, None)  # (DBP, DPSM)
    trxreg = (None, None)  # (RRW, RRH)
    while q < nq:
        if img_left > 0:
            take = min(img_left, nq - q)
            q += take
            img_left -= take
            continue
        lo, hi = u64(payload, q * 16), u64(payload, q * 16 + 8)
        q += 1
        nloop = lo & 0x7FFF
        eop = (lo >> 15) & 1
        pre = (lo >> 46) & 1
        primval = (lo >> 47) & 0x7FF
        flg = (lo >> 58) & 3
        nreg = (lo >> 60) & 0xF
        nreg = nreg if nreg else 16
        regs = [(hi >> (4 * i)) & 0xF for i in range(16)]
        tags += 1
        if pre:
            prims.append(("TAGPRE", primval))
        if flg == 2 or flg == 3:
            notes.append(f"t{q}: reserved FLG={flg}")
            break
        if nloop == 0:
            nloop = 32768
        if flg == 0:  # PACKED: NREG qwads per loop
            for _ in range(nloop):
                for r in regs[:nreg]:
                    if q >= nq:
                        notes.append("PACKED overrun")
                        break
                    d0, d1 = u64(payload, q * 16), u64(payload, q * 16 + 8)
                    q += 1
                    if r == 0xE:
                        addr = d1 & 0xFF
                        ad.append((addr, d0))
                        if addr == 0x50:
                            blt = ((d0 >> 32) & 0x3FFF, (d0 >> 56) & 0x3F)
                        elif addr == 0x52:
                            trxreg = (d0 & 0xFFF, (d0 >> 16) & 0xFFF)
                        elif addr == 0x53:
                            direction, xfer = d0 & 3, (d0 >> 2) & 1
                            ad.append(("TRXDIR", (direction, xfer)))
                            if xfer and direction == 0 and trxreg[0] and trxreg[1]:
                                bpp = PSM_BPP.get(blt[1], 4)
                                px = trxreg[0] * trxreg[1]
                                img_left = int((px * bpp + 15) // 16)
                    elif r == 0x0:
                        prims.append(("PRIM", d0 & 0x7FF))
                else:
                    continue
                break
        else:  # REGLIST: NREG 64-bit fields per loop
            qw_per = (nreg + 1) // 2
            for _ in range(nloop):
                for _ in range(qw_per):
                    if q >= nq:
                        notes.append("REGLIST overrun")
                        break
                    q += 1
                else:
                    continue
                break
            rnames = [PACKED_NAMES.get(r, f"{r:#x}") for r in regs[:nreg]]
            notes.append(f"REGLIST nloop={nloop} nreg={nreg} regs={rnames} EOP={eop}")
        if eop:
            break
    return ad, prims, notes, tags, nq - q


ADDR_NAMES = {0x00: "PRIM", 0x01: "RGBAQ", 0x02: "ST", 0x03: "UV",
              0x04: "XYZF2", 0x05: "XYZ2", 0x06: "TEX0_1", 0x07: "TEX0_2",
              0x08: "CLAMP_1", 0x09: "CLAMP_2", 0x0A: "FOG", 0x0C: "XYZF3",
              0x0D: "XYZ3", 0x14: "TEX1_1", 0x15: "TEX1_2", 0x16: "TEX2_1",
              0x17: "TEX2_2", 0x18: "XYOFFSET_1", 0x19: "XYOFFSET_2",
              0x1A: "PRMODECONT", 0x1B: "PRMODE", 0x1C: "TEXCLUT",
              0x1D: "SCANMSK", 0x27: "TEXA", 0x28: "FOGCOL", 0x2D: "TEXFLUSH",
              0x34: "DIMX", 0x35: "DTHE", 0x36: "COLCLAMP", 0x37: "TEST_1",
              0x38: "TEST_2", 0x39: "PABE", 0x3A: "FBA_1", 0x3B: "FBA_2",
              0x3C: "FRAME_1", 0x3D: "FRAME_2", 0x3E: "ZBUF_1", 0x3F: "ZBUF_2",
              0x42: "ALPHA_1", 0x43: "ALPHA_2", 0x44: "PABE?", 0x45: "FBA?",
              0x50: "BITBLTBUF", 0x51: "TRXPOS", 0x52: "TRXREG", 0x53: "TRXDIR",
              0x60: "SIGNAL", 0x61: "FINISH", 0x62: "LABEL"}


def fmt_ad(ad):
    out = []
    for a in ad:
        if a[0] == "TRXDIR":
            out.append(f"TRXDIR dir={a[1][0]} xfer={a[1][1]}")
        elif a[0] == 0x50:
            out.append(f"BITBLTBUF DBP={((a[1] >> 32) & 0x3FFF)} DPSM={((a[1] >> 56) & 0x3F):#x} "
                       f"SBP={(a[1] & 0x3FFF)} SPSM={((a[1] >> 24) & 0x3F):#x}")
        elif a[0] == 0x51:
            out.append(f"TRXPOS DSAX={((a[1] >> 32) & 0x7FF)},DSAY={((a[1] >> 48) & 0x3FF)} "
                       f"DIR={((a[1] >> 59) & 3)}")
        elif a[0] == 0x52:
            out.append(f"TRXREG RRW={(a[1] & 0xFFF)} RRH={((a[1] >> 16) & 0xFFF)}")
        elif a[0] in (0x3C, 0x3D):
            out.append(f"FRAME_{a[0] - 0x3B} FBP={((a[1]) & 0x1FF)}")
        elif a[0] in (0x06, 0x07):
            out.append(f"TEX0_{a[0] - 0x5} TBP0={((a[1]) & 0x3FFF)}")
        elif a[0] == 0x00:
            out.append(f"PRIM(AD)={(a[1] & 0x7FF):#x}")
    return out


def main(path, max_vsync=8):
    b = open(path, 'rb').read()
    n = len(b)
    o = 8
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o)
    o += 36
    o += serial_sz + shot_sz + state_size + 8192
    ordinal, nv = 0, 0
    cur = []  # (ordinal, idx, size, off)
    while o < n:
        pid = b[o]
        o += 1
        assert pid in (0, 1, 2, 3), (o, pid)
        if pid == 0:
            idx = b[o]
            o += 1
            sz = u32(b, o)
            o += 4
            cur.append((ordinal, idx, sz, o))
            o += sz
        elif pid == 1:
            f = b[o]
            o += 1
            if nv < max_vsync:
                print(f"dump-vsync#{nv} phase={f} n_xfer={len(cur)}")
                for (tord, idx, sz, off) in cur:
                    payload = b[off:off + sz]
                    ad, prims, notes, tags, left = walk_transfer(payload, nv, tord)
                    interesting = fmt_ad(ad)
                    hist = {}
                    for a in ad:
                        if a[0] == "TRXDIR":
                            continue
                        nm = ADDR_NAMES.get(a[0], f"{a[0]:#x}")
                        hist[nm] = hist.get(nm, 0) + 1
                    print(f"  xfer#{tord} path={idx} size={sz} tags={tags} "
                          f"ad_writes={len(ad)} leftover_qw={left}")
                    print(f"    ADDR_hist={dict(sorted(hist.items()))}")
                    for line in interesting:
                        print(f"    {line}")
                    if prims:
                        pv = {}
                        for k, v in prims:
                            pv.setdefault((k, v & 7, (v >> 4) & 1), 0)
                            pv[(k, v & 7, (v >> 4) & 1)] += 1
                        print(f"    prims={dict(sorted(pv.items()))}")
                    for nb in notes[:3]:
                        print(f"    note: {nb}")
            nv += 1
            cur = []
        elif pid == 2:
            sz = u32(b, o)
            o += 4
        else:
            o += 8192
        ordinal += 1
    print(f"EOF_SYNC={'yes' if o == n else 'NO'} total_vsyncs={nv}")


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8)
