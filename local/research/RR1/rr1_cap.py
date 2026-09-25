#!/usr/bin/env python3
"""RR1: census over our PS2XGSC1 GS capture (PS2X_GS_CAPTURE), same keys as rr1_census.py.

Record: u32 payloadSize, u8 kind, u64 tick, body. Packet(1) body = u8 path, u32 size, data.
NativeUpload(5) = bitbltbuf, trxpos, trxreg, trxdir (u64 each), u32 size, data.
Usage: rr1_cap.py <gs.cap> <from_tick> <to_tick> [census|flash]
  census: prims per (tick, key) like rr1_census.py (tick instead of vsync)
  flash : per tick, prims per coarse class (path, tme, tbp0, psm, alpha) → presence matrix
"""
import sys, os, struct
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
import rr1_census as rc
g = rc.g


def iter_records(path, t_from, t_to):
    with open(path, 'rb') as f:
        assert f.read(8) == b'PS2XGSC1'
        while True:
            h = f.read(4)
            if len(h) < 4:
                return
            (n,) = struct.unpack('<I', h)
            kind = f.read(1)[0]
            (tick,) = struct.unpack('<Q', f.read(8))
            bsz = n - 9
            if tick < t_from:
                f.seek(bsz, 1)
                continue
            if tick > t_to:
                return
            yield kind, tick, f.read(bsz)


def load(path, t_from, t_to):
    gs = g.GS()
    decs = defaultdict(lambda: g.PathDecoder(gs))
    uploads = Counter()
    for kind, tick, body in iter_records(path, t_from, t_to):
        if kind == 1:
            pth = body[0]
            (sz,) = struct.unpack_from('<I', body, 1)
            gs.meta = dict(vsync=tick, path=pth, pc=None)
            decs[pth].feed(body[5:5 + sz])
        elif kind == 5:
            uploads[tick] += 1
    return gs, uploads


def main():
    path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    mode = sys.argv[4] if len(sys.argv) > 4 else 'census'
    gs, uploads = load(path, a, b)
    c = Counter()
    for p in gs.prims:
        if p.get('adc'):
            continue
        if mode == 'census':
            c[(p['vsync'], p['path']) + rc.key(p)] += 1
        else:
            t = g.tex0_fields(p['tex0'])
            c[(p['vsync'], (p['path'], p['tme'], t['tbp0'] if p['tme'] else -1,
                            t['psm'] if p['tme'] else -1, hex(p['alpha'])))] += 1
    if mode == 'census':
        print('tick path ctxt tme tbp0 psm tw th cbp abe alpha test fbp tex1lo : prims')
        for k, n in sorted(c.items()):
            print(*k, ':', n)
    else:
        ticks = sorted({k[0] for k in c})
        classes = sorted({k[1] for k in c}, key=str)
        print('native uploads per tick:', {t: uploads[t] for t in ticks})
        print('class', *ticks)
        for cl in classes:
            print(cl, *[c.get((t, cl), 0) for t in ticks])

if __name__ == '__main__':
    main()
