#!/usr/bin/env python3
"""RR1: per-draw state census (TEX0/ALPHA/TEST/FRAME) on a PCSX2 .gs dump.

Extends E51's decoder with ALPHA_1/2 (0x42/0x43), FBA, TEXA, PABE.
Usage: rr1_census.py <dump.gs> [max_vsyncs] [--tbp N]
Prints, per vsync window, prim counts keyed by (ctxt, tbp0, psm, tw, th, cbp, alpha, abe, test, frame-fbp).
"""
import sys, os
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'E51'))
import e51_gif as g

REG_ALPHA_1, REG_ALPHA_2, REG_TEXA, REG_PABE, REG_FBA_1, REG_FBA_2 = 0x42, 0x43, 0x3B, 0x49, 0x4A, 0x4B
REG_FOGCOL, REG_TEXCLUT, REG_DTHE, REG_COLCLAMP = 0x3D, 0x1C, 0x45, 0x46

_orig_write = g.GS.write
def write(self, reg, val):
    if reg in (REG_ALPHA_1, REG_ALPHA_2):
        self.ctx[reg - REG_ALPHA_1].alpha = val
    elif reg in (REG_FBA_1, REG_FBA_2):
        self.ctx[reg - REG_FBA_1].fba = val
    elif reg == REG_TEXA:
        self.texa = val
    elif reg == REG_PABE:
        self.pabe = val
    elif reg == REG_FOGCOL:
        self.fogcol = val
    elif reg == REG_TEXCLUT:
        self.texclut = val
    _orig_write(self, reg, val)
g.GS.write = write
for k, v in dict(alpha=0, fba=0).items():
    setattr(g.Ctx, k, v)
for k, v in dict(texa=0, pabe=0, fogcol=0, texclut=0).items():
    setattr(g.GS, k, v)

_orig_kick = g.GS.kick
def kick(self, x, y, z, drawing):
    n0 = len(self.prims)
    _orig_kick(self, x, y, z, drawing)
    if len(self.prims) > n0 and not self.prims[-1].get('adc'):
        p = self.prims[-1]
        c = self.ctx[p['ctxt']]
        p['alpha'] = c.alpha
        p['fba'] = c.fba
        p['texa'] = self.texa
        p['pabe'] = self.pabe
        p['prim'] = self.attrs()
        p['rgba'] = self.rgbaq
g.GS.kick = kick


def key(p):
    t = g.tex0_fields(p['tex0'])
    return (p['ctxt'], p['tme'], t['tbp0'] if p['tme'] else -1, t['psm'] if p['tme'] else -1,
            t['tw'] if p['tme'] else -1, t['th'] if p['tme'] else -1, t['cbp'] if p['tme'] else -1,
            p['abe'], hex(p['alpha']), hex(p['test']), p['frame'] & 0x1FF, hex(p['tex1'] & 0xffffffff))


def main():
    path = sys.argv[1]
    mx = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    gs, _ = g.load_pcsx2(path, max_vsyncs=mx)
    c = Counter()
    for p in gs.prims:
        if p.get('adc'):
            continue
        c[(p['vsync'],) + key(p)] += 1
    print('vsync ctxt tme tbp0 psm tw th cbp abe alpha test fbp tex1lo : prims')
    for k, n in sorted(c.items()):
        print(*k, ':', n)

if __name__ == '__main__':
    main()
