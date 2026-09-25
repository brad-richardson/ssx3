#!/usr/bin/env python3
"""RR1: split a PATH3 packet from our capture into EOP-terminated GIF packets.
Usage: rr1_eop.py <gs.cap> <tick> [min_bytes]  -> one line per EOP packet: tags, bytes, what it does"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import rr1_cap as cap


def split_eop(d):
    """Return list of (start, end, [tag descr]) EOP packets; handles PACKED/REGLIST/IMAGE."""
    out, o, start, tags = [], 0, 0, []
    while o + 16 <= len(d):
        lo, hi = struct.unpack_from('<QQ', d, o)
        nloop = lo & 0x7FFF; eop = (lo >> 15) & 1; flg = (lo >> 58) & 3
        nreg = (lo >> 60) & 0xF or 16
        o += 16
        if flg == 0:
            o += nloop * nreg * 16
            regs = [(hi >> (4 * i)) & 0xF for i in range(nreg)]
            tags.append(f"P{nloop}x{nreg}" + ('AD' if regs == [0xE] else ''))
        elif flg == 1:
            o += ((nloop * nreg * 8) + 15) // 16 * 16
            tags.append(f"R{nloop}x{nreg}")
        else:
            o += nloop * 16
            tags.append(f"I{nloop}")
        if eop:
            out.append((start, o, tags)); start, tags = o, []
    if start < len(d):
        out.append((start, len(d), tags + ['(no EOP)']))
    return out


def main():
    path, tick = sys.argv[1], int(sys.argv[2])
    mn = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
    for kind, tk, body in cap.iter_records(path, tick, tick):
        if kind != 1 or body[0] != 3:
            continue
        (sz,) = struct.unpack_from('<I', body, 1)
        if sz < mn:
            continue
        d = body[5:5 + sz]
        pk = split_eop(d)
        print(f"PATH3 packet {sz}B -> {len(pk)} EOP packets")
        for i, (a, b, t) in enumerate(pk):
            print(f"  eop#{i} off={a} bytes={b - a} tags={' '.join(t[:8])}{' …' if len(t) > 8 else ''}")

if __name__ == '__main__':
    main()
