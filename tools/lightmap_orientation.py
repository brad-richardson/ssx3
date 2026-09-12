#!/usr/bin/env python3
"""Check which lightmap-cell orientation each engine uses, from its own stock data.

For every terrain patch, sample the surface normal on a grid of parametric points
and read the lightmap sheet at the corresponding cell point under each of the
eight dihedral orientations; fit brightness ~ n.L + c by least squares. The
orientation with the best R^2 is the engine's convention. Run from the repository
root with the GameCube sources under local/. Result on 2026-09-11: identity for
both SSX 3 Snow Jam (R^2 0.287 vs 0.223 for the next) and Tricky Garibaldi
(0.612 vs 0.515), so gamecube_textures.bind_patch copies the cell unchanged.
"""
import math
import struct
import sys
sys.path.insert(0, 'tools')
import numpy as np
from gamecube_world import World
from gamecube_textures import decode, shape_images
from probe_worlds import patch_point
from import_terrain import UV_CORNERS

MAPS = {'id (s,t)': lambda s,t:(s,t), 'flip u': lambda s,t:(1-s,t), 'flip v': lambda s,t:(s,1-t), 'flip uv': lambda s,t:(1-s,1-t),
        'swap': lambda s,t:(t,s), 'swap flip u': lambda s,t:(1-t,s), 'swap flip v': lambda s,t:(t,1-s), 'swap flip uv': lambda s,t:(1-t,1-s)}
SAMPLES = [(a,b) for a in (0.1,0.3,0.5,0.7,0.9) for b in (0.1,0.3,0.5,0.7,0.9)]

def normal(coeffs, s, t, h=1e-3):
    p = np.array(patch_point(coeffs, s, t)); pu = np.array(patch_point(coeffs, s+h, t)); pv = np.array(patch_point(coeffs, s, t+h))
    n = np.cross(pu-p, pv-p); l = np.linalg.norm(n)
    return n/l if l else None

def gray(img):
    w,h = img['width'], img['height']
    px = decode(img)
    return np.array([(r+g+b)/3 for r,g,b,a in px], dtype=float).reshape(h, w), w, h

def run(name, patches, sheets):
    # patches: list of (coeffs, sheet_id, (u,v,w,h)); sheets: {id: gray array}
    rows = {m: [] for m in MAPS}
    for coeffs, sid, (u,v,w,h) in patches:
        if sid not in sheets: continue
        g, W, H = sheets[sid]
        for s,t in SAMPLES:
            n = normal(coeffs, s, t)
            if n is None: continue
            for m, f in MAPS.items():
                a,b = f(s,t)
                x = min(W-1, max(0, int((u + a*w) * W))); y = min(H-1, max(0, int((v + b*h) * H)))
                rows[m].append((*n, 1.0, g[y, x]))
    print(name)
    for m, r in rows.items():
        A = np.array(r); X, yv = A[:, :4], A[:, 4]
        coef, *_ = np.linalg.lstsq(X, yv, rcond=None)
        pred = X @ coef; ss = ((yv-pred)**2).sum(); tot = ((yv-yv.mean())**2).sum()
        print(f'  {m:14} R2={1-ss/tot:.4f} L={np.round(coef[:3]/np.linalg.norm(coef[:3]),3)} n={len(r)}')

# SSX 3 GameCube Snow Jam
w = World(open('local/source/gamecube/ssx3/BAM.BIG','rb').read())
sheets = {}
for g in range(26, 36):
    for e,p in w.records(g):
        if e['kind'] == 10:
            wd, ht = struct.unpack_from('>HH', p, 4)
            sheets[e['rid']] = gray(dict(type=p[0], width=wd, height=ht, pixels=p[32:32+wd*ht//2], palette=None))
pats = []
worst = 0
for e,p in w.records(36):
    if e['kind'] != 1: continue
    coeffs = [list(struct.unpack_from('>4f', p, 64+16*j)[:3]) for j in range(16)]
    stored = [struct.unpack_from('>3f', p, 336+12*k) for k in range(4)]
    worst = max(worst, max(math.dist(patch_point(coeffs, s, t), stored[k]) for k,(s,t) in enumerate(UV_CORNERS)))
    pats.append((coeffs, struct.unpack_from('>H', p, 418)[0], struct.unpack_from('>4f', p, 16)))
print('snow jam corner order check (max dist)', round(worst, 3), 'patches', len(pats), 'sheets', len(sheets))
run('SSX 3 Snow Jam (GameCube)', pats, sheets)

# Tricky GameCube Garibaldi
raw = open('local/source/gamecube/tricky/gari.nbd','rb').read()
lms = shape_images(open('local/source/gamecube/tricky/gari_L.gsh','rb').read())
sheets = {i: gray(img) for i, img in enumerate(lms)}
pats = []
for i in range(3885):
    o = 160 + 448*i
    coeffs = [list(struct.unpack_from('>4f', raw, o+80+16*j)[:3]) for j in range(16)]
    pats.append((coeffs, struct.unpack_from('>h', raw, o+430)[0], struct.unpack_from('>4f', raw, o)))
run('Tricky Garibaldi (GameCube)', pats, sheets)
