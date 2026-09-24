#!/usr/bin/env python3
"""Build a synthetic stream: original records up to (not incl.) marker END_TICK,
with GIF packets of tick SPLIT_TICK split at EOP boundaries and a marker (tick=END_TICK)
inserted after each piece. Usage: mkstream.py out.gs END_TICK [--nosplit]"""
import os, struct, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from gsstream import records

def eop_pieces(data):
    p, start, pieces = 0, 0, []
    while p + 16 <= len(data):
        lo, hi = struct.unpack_from('<QQ', data, p); p += 16
        nloop = lo & 0x7fff; eop = (lo >> 15) & 1; flg = (lo >> 58) & 3; nreg = (lo >> 60) & 0xf or 16
        if flg == 0: p += nloop * nreg * 16
        elif flg == 1: p += ((nloop * nreg * 8) + 15) & ~15
        else: p += nloop * 16
        if eop:
            pieces.append(data[start:p]); start = p
    if start < len(data): pieces.append(data[start:])
    return pieces

def rec_bytes(rec): return struct.pack('<I', len(rec)) + rec
def marker(t): return rec_bytes(bytes([4]) + struct.pack('<Q', t))

def build(src, out, end_tick, split=True, extra=None):
    n = 0
    with open(out, 'wb') as o:
        o.write(b'PS2XGSC1')
        for off, k, t, rec in records(src, end_tick):
            if k == 4 and t == end_tick:
                o.write(rec_bytes(rec)); n += 1
                break
            if t == end_tick - 1 and k == 1 and split:
                size = struct.unpack_from('<I', rec, 10)[0]
                for piece in eop_pieces(rec[14:14 + size]):
                    r = rec[:10] + struct.pack('<I', len(piece)) + piece
                    o.write(rec_bytes(r)); o.write(marker(end_tick)); n += 1
            else:
                o.write(rec_bytes(rec))
    return n

if __name__ == '__main__':
    n = build(os.environ.get('SRC','/Users/brad/dev/ssx3-work/N8D7M6/n8d7m6.gs'), sys.argv[1], int(sys.argv[2]), '--nosplit' not in sys.argv)
    print('markers inserted/ending', n)
