#!/usr/bin/env python3
"""GB2 Part 4: diff [pkbytes] captures between two pklog files, decode GIF tags.

Usage:
  python3 local/research/GB2/gb2_pktdecode.py <pklogA> <pklogB> <idx> [<idx>...]

For each idx: prints len/src/base/tick per side, GIF-tag decode per side,
and every differing qword with its structural role (tag / A+D addr+data /
packed reg / image word).
"""
import re
import sys

REG_NAMES = {
    0x00: "PRIM", 0x01: "RGBAQ", 0x02: "ST", 0x03: "UV",
    0x04: "XYZF2", 0x05: "XYZ2", 0x06: "TEX0_1", 0x07: "TEX0_2",
    0x08: "CLAMP_1", 0x09: "CLAMP_2", 0x0A: "FOG", 0x0C: "XYZF3",
    0x0D: "XYZ3", 0x0E: "A+D", 0x0F: "NOP",
}
AD_NAMES = {
    0x00: "PRIM", 0x01: "RGBAQ", 0x02: "ST", 0x03: "UV", 0x04: "XYZF2",
    0x05: "XYZ2", 0x06: "TEX0_1", 0x07: "TEX0_2", 0x08: "CLAMP_1",
    0x09: "CLAMP_2", 0x0A: "FOG", 0x0C: "XYZF3", 0x0D: "XYZ3",
    0x0F: "TEX1_1", 0x10: "TEX1_2", 0x11: "TEX2_1", 0x12: "TEX2_2",
    0x13: "XYOFFSET_1", 0x14: "XYOFFSET_2", 0x15: "PRMODECONT",
    0x16: "PRMODE", 0x17: "TEXCLUT", 0x18: "SCANMSK", 0x19: "MIPTBP1_1",
    0x1A: "MIPTBP1_2", 0x1B: "MIPTBP2_1", 0x1C: "MIPTBP2_2", 0x1D: "TEXA",
    0x1E: "FOGCOL", 0x1F: "TEXFLUSH", 0x20: "SCISSOR_1", 0x21: "SCISSOR_2",
    0x22: "ALPHA_1", 0x23: "ALPHA_2", 0x24: "DIMX", 0x25: "DTHE",
    0x26: "COLCLAMP", 0x27: "TEST_1", 0x28: "TEST_2", 0x29: "PABE",
    0x2A: "FBA_1", 0x2B: "FBA_2", 0x2C: "FRAME_1", 0x2D: "FRAME_2",
    0x2E: "ZBUF_1", 0x2F: "ZBUF_2", 0x30: "BITBLTBUF", 0x31: "TRXPOS",
    0x32: "TRXREG", 0x33: "TRXDIR", 0x34: "HWREG", 0x3F: "SIGNAL",
    0x40: "FINISH", 0x41: "LABEL",
}
FLG_NAMES = {0: "PACKED", 1: "REGLIST", 2: "IMAGE", 3: "DISABLED"}

PKB = re.compile(
    r"\[pkbytes\] idx=(\d+) tick=(\d+) len=(\d+) src=(\S+) base=(\S+) data=([0-9a-f]+)")


def parse(path):
    out = {}
    with open(path) as f:
        for line in f:
            m = PKB.search(line)
            if m:
                idx = int(m.group(1))
                out[idx] = {
                    "tick": int(m.group(2)), "len": int(m.group(3)),
                    "src": m.group(4), "base": m.group(5),
                    "bytes": bytes.fromhex(m.group(6)),
                }
    return out


def qwords(buf):
    return [int.from_bytes(buf[i:i + 16], "little") for i in range(0, len(buf), 16)]


def tag_decode(qw):
    lo = qw & 0xFFFFFFFFFFFFFFFF
    hi = (qw >> 64) & 0xFFFFFFFFFFFFFFFF
    nloop = lo & 0x7FFF
    eop = (lo >> 15) & 1
    pre = (lo >> 46) & 1
    prim = (lo >> 47) & 0x7FF
    flg = (lo >> 58) & 3
    nreg = (lo >> 60) & 0xF
    regs = [(hi >> (4 * i)) & 0xF for i in range(16)]
    return {"nloop": nloop, "eop": eop, "pre": pre, "prim": prim,
            "flg": flg, "nreg": nreg or 16, "regs": regs}


def tag_str(t):
    regs = ",".join(f"{r:02x}({REG_NAMES.get(r, '?')})" for r in t["regs"][:t["nreg"]])
    return (f"NLOOP={t['nloop']} EOP={t['eop']} PRE={t['pre']} "
            f"FLG={FLG_NAMES.get(t['flg'], '?')} NREG={t['nreg']} [{regs}]")


def walk_roles(qw):
    """role[qword_offset] = description; walks all GIF tags in the packet."""
    roles = {}
    pos = 0
    nq = len(qw)
    tag_no = 0
    while pos < nq:
        if pos + 1 > nq:
            break
        t = tag_decode(qw[pos])
        roles[pos] = f"tag#{tag_no} {tag_str(t)}"
        pos += 1
        flg, nloop, nreg, regs = t["flg"], t["nloop"], t["nreg"], t["regs"]
        if flg == 2:  # IMAGE: NLOOP qwords of image data
            for i in range(nloop):
                if pos >= nq:
                    break
                roles[pos] = f"tag#{tag_no} image[{i}]"
                pos += 1
        elif flg == 0:  # PACKED: NLOOP iters x NREG qwords
            for loop in range(nloop):
                for r in range(nreg):
                    if pos >= nq:
                        break
                    reg = regs[r]
                    rn = REG_NAMES.get(reg, f"{reg:02x}?")
                    roles[pos] = f"tag#{tag_no} packed loop{loop} {rn}"
                    pos += 1
        elif flg == 1:  # REGLIST: NLOOP iters x NREG words (2/qword)
            words = []
            for loop in range(nloop):
                for r in range(nreg):
                    words.append((loop, regs[r]))
            for j in range(0, len(words), 2):
                if pos >= nq:
                    break
                w0 = words[j]
                w1 = words[j + 1] if j + 1 < len(words) else None
                d = f"tag#{tag_no} reglist loop{w0[0]} {REG_NAMES.get(w0[1], '?')}"
                if w1:
                    d += f"+loop{w1[0]} {REG_NAMES.get(w1[1], '?')}"
                roles[pos] = d
                pos += 1
        else:
            roles[pos - 1] += " (DISABLED: walk stops)"
            break
        tag_no += 1
        if tag_no > 64:
            break
    return roles


def ad_decode(qw):
    lo = qw & 0xFFFFFFFFFFFFFFFF
    hi = (qw >> 64) & 0xFFFFFFFFFFFFFFFF
    addr = hi & 0xFF
    return f"A+D addr=0x{addr:02x}({AD_NAMES.get(addr, '?')}) data=0x{lo:016x}"


def main():
    if len(sys.argv) < 4:
        print(__doc__.strip().splitlines()[4])
        return 2
    a = parse(sys.argv[1])
    b = parse(sys.argv[2])
    rc = 0
    for tok in sys.argv[3:]:
        idx = int(tok)
        pa, pb = a.get(idx), b.get(idx)
        print(f"=== idx {idx} ===")
        if pa is None or pb is None:
            print(f"  MISSING: A={'yes' if pa else 'no'} B={'yes' if pb else 'no'}")
            rc = 1
            continue
        print(f"  A: tick={pa['tick']} len={pa['len']} src={pa['src']} base={pa['base']}")
        print(f"  B: tick={pb['tick']} len={pb['len']} src={pb['src']} base={pb['base']}")
        if pa["len"] != pb["len"]:
            print(f"  LEN DIFFERS: {pa['len']} vs {pb['len']}")
            rc = 1
        qa, qb = qwords(pa["bytes"]), qwords(pb["bytes"])
        if len(qa) == 0 or len(qb) == 0:
            print("  EMPTY")
            rc = 1
            continue
        print(f"  A tag0: {tag_str(tag_decode(qa[0]))}")
        print(f"  B tag0: {tag_str(tag_decode(qb[0]))}")
        ra, rb = walk_roles(qa), walk_roles(qb)
        ndiff = 0
        for off in range(max(len(qa), len(qb))):
            va = qa[off] if off < len(qa) else None
            vb = qb[off] if off < len(qb) else None
            if va == vb:
                continue
            ndiff += 1
            sa = f"0x{va:032x}" if va is not None else "(short)"
            sb = f"0x{vb:032x}" if vb is not None else "(short)"
            print(f"  qw[{off}] role={ra.get(off, '?')}")
            print(f"    A {sa}")
            print(f"    B {sb}")
            # A+D detail when the role mentions it
            role = ra.get(off, "") + rb.get(off, "")
            if "A+D" in role or "reglist" in role:
                if va is not None:
                    print(f"    A {ad_decode(va)}")
                if vb is not None:
                    print(f"    B {ad_decode(vb)}")
            # word-level diff detail
            if va is not None and vb is not None:
                for w in range(4):
                    wa = (va >> (32 * w)) & 0xFFFFFFFF
                    wb = (vb >> (32 * w)) & 0xFFFFFFFF
                    if wa != wb:
                        print(f"    word[{w}] (byte+{off * 16 + w * 4}): "
                              f"A=0x{wa:08x} B=0x{wb:08x}")
        print(f"  differing qwords: {ndiff}/{max(len(qa), len(qb))}")
        if ndiff:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
