#!/usr/bin/env python3
"""RD1: plot selected draw batches' triangles (wireframe + flat vertex colour) scaled up, for shape checks.
Usage: rd1_plot.py <gs.stream> <tick> <out.png> <batch#> [...] [--box x0,y0,x1,y1] [--scale 8]"""
import sys, argparse
from PIL import Image, ImageDraw
import rd1_draws as d
ap = argparse.ArgumentParser()
ap.add_argument('path'); ap.add_argument('tick', type=int); ap.add_argument('out'); ap.add_argument('ids', nargs='+', type=int)
ap.add_argument('--box', default='230,205,285,285'); ap.add_argument('--scale', type=int, default=8)
a = ap.parse_args()
gs = d.load_cap(a.path, a.tick, a.tick)
bs = d.batches(gs.prims)
x0, y0, x1, y1 = [float(v) for v in a.box.split(',')]
S = a.scale
im = Image.new('RGB', (int((x1 - x0) * S), int((y1 - y0) * S)), (0, 0, 0))
dr = ImageDraw.Draw(im)
pal = [(255, 80, 80), (80, 255, 80), (80, 160, 255), (255, 255, 80), (255, 80, 255), (80, 255, 255)]
for k, i in enumerate(a.ids):
    b = bs[i]
    for p in b['prims']:
        xo = p['xyoffset']; ox = (xo & 0xFFFF) / 16.0; oy = ((xo >> 32) & 0xFFFF) / 16.0
        pts = [((v['x'] - ox - x0) * S, (v['y'] - oy - y0) * S) for v in p['verts']]
        dr.polygon(pts, outline=pal[k % len(pal)])
im.save(a.out)
print(a.out, im.size)
