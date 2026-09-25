#!/usr/bin/env python3
"""RR1: packet timeline for one tick of our capture: per GIF packet, path, size,
A+D/state regs written (TEST/ALPHA/ZBUF/FRAME/TEX0 tbp) and draws (count, first tbp/alpha/test).
Usage: rr1_timeline.py <gs.cap> <tick> [first_n]"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import rr1_census as rc
import rr1_cap as cap
g = rc.g
NAMES = {0x42: 'ALPHA1', 0x43: 'ALPHA2', 0x47: 'TEST1', 0x48: 'TEST2', 0x4e: 'ZBUF1', 0x4f: 'ZBUF2',
         0x4c: 'FRAME1', 0x4d: 'FRAME2', 0x06: 'TEX0_1', 0x07: 'TEX0_2', 0x53: 'TRXDIR', 0x61: 'FINISH',
         0x60: 'SIGNAL', 0x3f: 'TEXFLUSH', 0x18: 'XYOFF1', 0x40: 'SCISSOR1'}


def main():
    path, tick = sys.argv[1], int(sys.argv[2])
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    gs = g.GS()
    decs = {}
    log = []
    orig = g.GS.write
    def w(self, reg, val):
        if reg in NAMES:
            if reg in (0x06, 0x07):
                log.append(f"{NAMES[reg]}(tbp={val & 0x3fff},psm={(val>>20)&0x3f})")
            else:
                log.append(f"{NAMES[reg]}={val:#x}")
        orig(self, reg, val)
    g.GS.write = w
    idx = 0
    for kind, tk, body in cap.iter_records(path, tick, tick):
        if kind != 1:
            if kind == 5:
                print(f"#{idx} native-upload")
            idx += 1
            continue
        pth = body[0]
        (sz,) = struct.unpack_from('<I', body, 1)
        n0 = len(gs.prims)
        log.clear()
        gs.meta = dict(vsync=tk, path=pth, pc=None)
        decs.setdefault(pth, g.PathDecoder(gs)).feed(body[5:5 + sz])
        new = [p for p in gs.prims[n0:] if not p.get('adc')]
        desc = ''
        if new:
            p = new[0]
            t = g.tex0_fields(p['tex0'])
            kinds = {}
            for q in new:
                tq = g.tex0_fields(q['tex0'])
                k = (tq['tbp0'] if q['tme'] else -1, hex(q['alpha']), hex(q['test']))
                kinds[k] = kinds.get(k, 0) + 1
            desc = ' draws=' + ' '.join(f"{k[0]}/{k[1]}/{k[2]}x{v}" for k, v in kinds.items())
        if idx < first:
            print(f"#{idx} p{pth} {sz}B regs[{' '.join(log[:12])}{' …' if len(log) > 12 else ''}]{desc}")
        idx += 1

if __name__ == '__main__':
    main()
