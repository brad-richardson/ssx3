#!/usr/bin/env python3
"""RR1: packet timeline for a PCSX2 .gs dump (same columns as rr1_timeline.py).
Usage: rr1_timeline_pcsx2.py <dump.gs> [max_vsyncs]"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import rr1_census as rc
import rr1_timeline as tl
g = rc.g


def main():
    path = sys.argv[1]
    mx = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    b = open(path, 'rb').read()
    o = 8
    ver, ss, so, ssz, c, w, h, sho, shs = struct.unpack_from('<9I', b, o)
    o += 36 + ssz + shs
    o += ss + 8192
    gs = g.GS()
    decs = {}
    log = []
    orig = g.GS.write
    def wr(self, reg, val):
        if reg in tl.NAMES:
            if reg in (0x06, 0x07):
                log.append(f"{tl.NAMES[reg]}(tbp={val & 0x3fff},psm={(val>>20)&0x3f})")
            else:
                log.append(f"{tl.NAMES[reg]}={val:#x}")
        orig(self, reg, val)
    g.GS.write = wr
    vs, idx = 0, 0
    while o < len(b):
        pid = b[o]; o += 1
        if pid == 0:
            pi = b[o]; (sz,) = struct.unpack_from('<I', b, o + 1); o += 5
            n0 = len(gs.prims); log.clear()
            gs.meta = dict(vsync=vs, path=pi, pc=None)
            decs.setdefault(pi, g.PathDecoder(gs)).feed(b[o:o + sz]); o += sz
            new = [p for p in gs.prims[n0:] if not p.get('adc')]
            kinds = {}
            for q in new:
                tq = g.tex0_fields(q['tex0'])
                k = (tq['tbp0'] if q['tme'] else -1, tq['psm'] if q['tme'] else -1, hex(q['alpha']), hex(q['test']), q['abe'])
                kinds[k] = kinds.get(k, 0) + 1
            desc = (' draws=' + ' '.join(f"{k[0]}:{k[1]}/{k[2]}/{k[3]}/abe{k[4]}x{v}" for k, v in kinds.items())) if kinds else ''
            print(f"v{vs} #{idx} idx{pi} {sz}B regs[{' '.join(log[:14])}{' …' if len(log) > 14 else ''}]{desc}")
            idx += 1
        elif pid == 1:
            o += 1; vs += 1; print(f"---- vsync {vs}")
            if vs >= mx:
                break
        elif pid == 2:
            o += 4
        elif pid == 3:
            o += 8192

if __name__ == '__main__':
    main()
