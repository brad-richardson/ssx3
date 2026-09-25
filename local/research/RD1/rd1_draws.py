#!/usr/bin/env python3
"""RD1: draw-batch census over a PS2XGSC1 capture (our GS stream) or PCSX2 .gs.

Groups consecutive drawing prims with identical state into batches and prints, per batch:
index, path, prims, type, tme, tbp0/psm/tw/th/cbp, abe, ALPHA, TEST, FBA, FRAME fbp/fbmsk, ZBUF,
screen bbox (after XYOFFSET), RGBA min/max over vertices, Q range.
Usage: rd1_draws.py cap|pcsx2 <gs.stream|dump.gs> <tick|vsync> [--bbox x0,y0,x1,y1] [--min 1]
"""
import sys, os, struct, argparse
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RR1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'E51'))
import rr1_census as rc  # patches ALPHA/FBA/TEXA into e51_gif
g = rc.g

_orig_kick = g.GS.kick
def kick(self, x, y, z, drawing):
    # same as e51_gif.GS.kick, plus full RGBA/fog per vertex and more per-prim state
    self.queue.append(dict(x=x / 16.0, y=y / 16.0, z=z, s=self.s, t=self.t, q=self.q,
                           u=self.u / 16.0, v=self.v / 16.0, a=(self.rgbaq >> 24) & 0xFF,
                           rgba=self.rgbaq, fog=self.fog))
    ptype = self.prim & 7
    need = g.NEEDED.get(ptype, 0)
    if need == 0 or len(self.queue) < need:
        return
    verts = self.queue[-need:] if ptype != 5 else [self.queue[0]] + self.queue[-2:]
    if drawing:
        a = self.attrs()
        ci = (a >> 9) & 1
        c = self.ctx[ci]
        self.prims.append(dict(type=ptype, tme=(a >> 4) & 1, fst=(a >> 8) & 1, abe=(a >> 6) & 1,
                               ctxt=ci, tex0=c.tex0, tex1=c.tex1, clamp=c.clamp, xyoffset=c.xyoffset,
                               scissor=c.scissor, test=c.test, frame=c.frame, verts=[dict(v) for v in verts],
                               alpha=c.alpha, fba=c.fba, zbuf=c.zbuf, texa=self.texa, pabe=self.pabe,
                               fge=(a >> 5) & 1, iip=(a >> 3) & 1, seq=self.seq, **self.meta))
    else:
        self.prims.append(dict(type=ptype, adc=True, **self.meta))
    if ptype in (0, 1, 3, 6):
        self.queue = []
    elif ptype in (2, 4):
        self.queue = self.queue[-(need - 1):]
    elif ptype == 5:
        self.queue = [self.queue[0], self.queue[-1]]
g.GS.kick = kick
g.GS.seq = 0

def iter_cap(path, t_from, t_to):
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
                f.seek(bsz, 1); continue
            if tick > t_to:
                return
            yield kind, tick, f.read(bsz)

def load_cap(path, t_from, t_to):
    gs = g.GS()
    decs = defaultdict(lambda: g.PathDecoder(gs))
    pk = 0
    for kind, tick, body in iter_cap(path, t_from, t_to):
        if kind == 1:
            pth = body[0]
            (sz,) = struct.unpack_from('<I', body, 1)
            gs.meta = dict(vsync=tick, path=pth, pc=None)
            gs.seq = pk; pk += 1
            decs[pth].feed(body[5:5 + sz])
    return gs

def key(p):
    t = g.tex0_fields(p['tex0'])
    tex = (t['tbp0'], t['psm'], t['tw'], t['th'], t['cbp'], t['tfx'], t['tcc']) if p['tme'] else None
    return (p['vsync'], p['path'], p['type'], p['tme'], tex, p['abe'], p['alpha'], p['test'], p['fba'],
            p['frame'], p['zbuf'], p['fge'], p['ctxt'])

def batches(prims):
    out = []
    for p in prims:
        if p.get('adc'):
            continue
        k = key(p)
        if out and out[-1]['key'] == k:
            out[-1]['prims'].append(p)
        else:
            out.append(dict(key=k, prims=[p]))
    return out

def summarize(b):
    ps = b['prims']
    xo = ps[0]['xyoffset']; ox = (xo & 0xFFFF) / 16.0; oy = ((xo >> 32) & 0xFFFF) / 16.0
    xs = [v['x'] - ox for p in ps for v in p['verts']]
    ys = [v['y'] - oy for p in ps for v in p['verts']]
    rg = [v.get('rgba', 0) for p in ps for v in p['verts']]
    ch = lambda s: (min((c >> s) & 0xFF for c in rg), max((c >> s) & 0xFF for c in rg))
    qs = [v['q'] for p in ps for v in p['verts']]
    return dict(bbox=(min(xs), min(ys), max(xs), max(ys)), r=ch(0), g=ch(8), b=ch(16), a=ch(24),
                q=(min(qs), max(qs)), n=len(ps), seq=ps[0]['seq'])

def fmt(i, b, s):
    (tick, path, typ, tme, tex, abe, alpha, test, fba, frame, zbuf, fge, ctxt) = b['key']
    x0, y0, x1, y1 = s['bbox']
    tx = 'tbp=%d psm=%#x %dx%d cbp=%d tfx=%d tcc=%d' % (tex[0], tex[1], 1 << tex[2], 1 << tex[3], tex[4], tex[5], tex[6]) if tex else 'untex'
    return ('#%d pk%d p%d n=%d type=%d ctx%d %s abe=%d alpha=%#x test=%#x fba=%d fbp=%d fbmsk=%#x zbuf=%#x fge=%d '
            'bbox=(%.0f,%.0f)-(%.0f,%.0f) R%s G%s B%s A%s q=(%.3g,%.3g)' % (
            i, s['seq'], path, s['n'], typ, ctxt, tx, abe, alpha, test, fba, frame & 0x1FF, frame >> 32, zbuf, fge,
            x0, y0, x1, y1, s['r'], s['g'], s['b'], s['a'], s['q'][0], s['q'][1]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('path'); ap.add_argument('tick', type=int)
    ap.add_argument('--bbox'); ap.add_argument('--min', type=int, default=1)
    ap.add_argument('--tbp', type=int)
    a = ap.parse_args()
    if a.src == 'pcsx2':
        gs, _ = g.load_pcsx2(a.path, a.tick + 1)
        gs.prims = [p for p in gs.prims if p['vsync'] == a.tick]
    else:
        gs = load_cap(a.path, a.tick, a.tick)
    bs = batches(gs.prims)
    print('prims', sum(len(b['prims']) for b in bs), 'batches', len(bs))
    bb = [float(v) for v in a.bbox.split(',')] if a.bbox else None
    for i, b in enumerate(bs):
        s = summarize(b)
        if s['n'] < a.min:
            continue
        if a.tbp is not None and (not b['key'][4] or b['key'][4][0] != a.tbp):
            continue
        if bb:
            x0, y0, x1, y1 = s['bbox']
            if x1 < bb[0] or x0 > bb[2] or y1 < bb[1] or y0 > bb[3]:
                continue
        print(fmt(i, b, s))

if __name__ == '__main__':
    main()
