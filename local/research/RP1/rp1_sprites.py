#!/usr/bin/env python3
"""RP1: list individual sprite prims (type 6) at one tick of a PS2XGSC1 capture, optionally by TBP.
Usage: rp1_sprites.py gs.cap tick [--tbp N] [--bbox x0,y0,x1,y1]"""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RD1'))
import rd1_draws as rd
g = rd.g
ap = argparse.ArgumentParser(); ap.add_argument('path'); ap.add_argument('tick', type=int)
ap.add_argument('--tbp', type=int); ap.add_argument('--bbox'); ap.add_argument('--pcsx2', action='store_true')
a = ap.parse_args()
if a.pcsx2:
    gs, _ = g.load_pcsx2(a.path, a.tick + 1); gs.prims = [p for p in gs.prims if p['vsync'] == a.tick]
else:
    gs = rd.load_cap(a.path, a.tick, a.tick)
bb = [float(v) for v in a.bbox.split(',')] if a.bbox else None
for i, p in enumerate(gs.prims):
    if p.get('adc') or p['type'] != 6 or not p['tme']:
        continue
    t = g.tex0_fields(p['tex0'])
    if a.tbp is not None and t['tbp0'] != a.tbp:
        continue
    xo = p['xyoffset']; ox = (xo & 0xFFFF) / 16.0; oy = ((xo >> 32) & 0xFFFF) / 16.0
    v0, v1 = p['verts']
    x0, y0, x1, y1 = v0['x'] - ox, v0['y'] - oy, v1['x'] - ox, v1['y'] - oy
    if bb and (max(x0, x1) < bb[0] or min(x0, x1) > bb[2] or max(y0, y1) < bb[1] or min(y0, y1) > bb[3]):
        continue
    fs = lambda v: ('st=(%.3f,%.3f,q%.3g)' % (v['s'], v['t'], v['q'])) if not p['fst'] else ('uv=(%.1f,%.1f)' % (v['u'], v['v']))
    print('%5d tbp=%d psm=%#x %dx%d cbp=%d tfx=%d fst=%d clamp=%#x tex1=%#x texa=%#x alpha=%#x xy=(%.1f,%.1f)-(%.1f,%.1f) rgba=%08x %s %s' % (
        i, t['tbp0'], t['psm'], 1 << t['tw'], 1 << t['th'], t['cbp'], t['tfx'], p['fst'], p['clamp'], p['tex1'], p['texa'],
        p['alpha'], x0, y0, x1, y1, v1['rgba'] & 0xFFFFFFFF, fs(v0), fs(v1)))
