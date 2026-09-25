#!/usr/bin/env python3
"""PX1: per-draw-class full-state + vertex census on a PS2XGSC1 capture tick.

For each non-ADC prim at theyear given tick, records the full draw state
(ctxt, PRIM attrs, TEX0/1, MIPTBP, CLAMP, FOG, SCISSOR, ALPHA, TEST, FBA,
PABE, TEXA, TEXCLUT, FRAME, ZBUF, XYOFFSET) and vertex stats (count, NaN/Inf
in x/y/z/s/t/q, xyz ranges, q range, alpha range). Aggregates by draw class
so a working tick (menu) can be diffed against a broken tick (race).

Usage: px1_vertcheck.py <gs.cap> <tick>
"""
import math, os, struct, sys
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RR1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'E51'))
import rr1_census as rc
g = rc.g

REG_MIPTBP1, REG_MIPTBP2 = 0x34, 0x35
REG_DT = 0x45

_orig_write = g.GS.write
def write(self, reg, val):
    if reg in (REG_MIPTBP1, REG_MIPTBP2):
        setattr(self.ctx[reg - REG_MIPTBP1], 'miptbp', val)
    elif reg == REG_DT:
        self.dthe = val
    _orig_write(self, reg, val)
g.GS.write = write
g.Ctx.miptbp = 0
g.GS.dthe = 0

_orig_kick = g.GS.kick
def kick(self, x, y, z, drawing):
    n0 = len(self.prims)
    _orig_kick(self, x, y, z, drawing)
    if len(self.prims) > n0 and not self.prims[-1].get('adc'):
        p = self.prims[-1]
        c = self.ctx[p['ctxt']]
        p['miptbp'] = getattr(c, 'miptbp', 0)
        p['fog'] = getattr(self, 'fog', 0)
        p['dthe'] = getattr(self, 'dthe', 0)
        p['zbuf'] = c.zbuf
g.GS.kick = kick


def isbad(v):
    return math.isnan(v) or math.isinf(v)


def main():
    cap, tick = sys.argv[1], int(sys.argv[2])
    gs = g.GS()
    decs = defaultdict(lambda: g.PathDecoder(gs))
    with open(cap, 'rb') as f:
        assert f.read(8) == b'PS2XGSC1'
        while True:
            h = f.read(4)
            if len(h) < 4:
                break
            (n,) = struct.unpack('<I', h)
            kind = f.read(1)[0]
            (tk,) = struct.unpack('<Q', f.read(8))
            body = f.read(n - 9)
            if tk < tick:
                continue
            if tk > tick:
                break
            if kind == 1:
                path = body[0]
                (sz,) = struct.unpack_from('<I', body, 1)
                gs.meta = {}
                decs[path].feed(body[5:5 + sz])
    agg = {}
    for p in gs.prims:
        if p.get('adc'):
            continue
        tbp = p['tex0'] & 0x3FFF
        psm = (p['tex0'] >> 20) & 0x3F
        key = (p['ctxt'], p['type'], p['tme'], p['fst'], tbp, psm,
               p.get('alpha', 0), p.get('test', 0) if 'test' in p else p['test'])
        a = agg.setdefault(key, dict(n=0, bad=0, xs=[], ys=[], zs=[], qs=[],
                                     alphas=[], prims=set(), tex1=set(), clamp=set(),
                                     scissor=set(), frame=set(), zbuf=set(), miptbp=set(),
                                     xyoffset=set(), fba=set(), texa=set(), pabe=set(),
                                     texclut=set(), fog=set(), dthe=set()))
        for v in p['verts']:
            a['n'] += 1
            if any(isbad(v[k]) for k in ('x', 'y', 'z', 's', 't', 'q')):
                a['bad'] += 1
            a['xs'].append(v['x']); a['ys'].append(v['y']); a['zs'].append(v['z'])
            a['qs'].append(v['q']); a['alphas'].append(v['a'])
        a['prims'].add(p['prim']); a['tex1'].add(p['tex1']); a['clamp'].add(p['clamp'])
        a['scissor'].add(p['scissor']); a['frame'].add(p['frame']); a['zbuf'].add(p['zbuf'])
        a['miptbp'].add(p['miptbp']); a['xyoffset'].add(p['xyoffset'])
        a['fba'].add(p.get('fba', 0)); a['texa'].add(p.get('texa', 0))
        a['pabe'].add(p.get('pabe', 0)); a['texclut'].add(p.get('texclut', 0))
        a['fog'].add(p.get('fog', 0)); a['dthe'].add(p.get('dthe', 0))
    for key in sorted(agg):
        a = agg[key]
        rng = lambda v: (min(v), max(v)) if v else None
        print(f"ctxt={key[0]} type={key[1]} tme={key[2]} fst={key[3]} tbp={key[4]} "
              f"psm={key[5]} alpha=0x{key[6]:x} test=0x{key[7]:x}")
        print(f"  verts={a['n']} bad_xy zstq={a['bad']} x={rng(a['xs'])} y={rng(a['ys'])} "
              f"z={rng(a['zs'])} q={rng(a['qs'])} a={rng(a['alphas'])}")
        for name in ('prims', 'tex1', 'clamp', 'scissor', 'frame', 'zbuf', 'miptbp',
                     'xyoffset', 'fba', 'texa', 'pabe', 'texclut', 'fog', 'dthe'):
            vals = sorted(a[name])
            print(f"  {name}=" + ",".join(f"0x{v:x}" for v in vals))


if __name__ == '__main__':
    main()
