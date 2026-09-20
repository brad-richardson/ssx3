#!/usr/bin/env python3
"""M18 remainder character: filtering-scale tests on the synth residual (offline).

Usage: m18.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; writes synths +
receipt text to WORK_DIR and PNGs to EVID_DIR.

Tests (see DESIGN.md, recorded before running):
  W: blend-weight sweep (+ rounding variants, feasibility bound,
     mid-position split)
  P: edge-phase tables (gradient decile / orientation / sign / mask)
  A: global affine fit (CONDITIONAL: runs iff e_W < 0.5 on s0)
  C: per-carrier masked weight sweeps (top 10 from loo.txt)
Tables, no verdicts.
"""
import hashlib
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 640, 448
N = W * H * 2  # YUYV bytes
R0_M16, R0_M15 = 22815, 13418
FNV_BLEND_S0 = "6b9ffda25bd76c6f"
W_COARSE = [round(i / 10, 10) for i in range(11)]
W_FINE = [round(0.30 + i * 0.025, 10) for i in range(17)]
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]


def fnv1a(data: bytes) -> int:
    h = 14695981039346656037
    for b in data:
        h ^= b
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h


def load_dump(path: Path) -> bytes:
    b = path.read_bytes()
    assert len(b) == N, f"{path}: {len(b)} bytes, want {N}"
    return b


def split_planes(raw: np.ndarray):
    y = np.empty((H, W), np.uint8)
    y[:, 0::2] = raw.reshape(H, W * 2)[:, 0::4]
    y[:, 1::2] = raw.reshape(H, W * 2)[:, 2::4]
    u = raw.reshape(H, W * 2)[:, 1::4].astype(np.uint8)
    v = raw.reshape(H, W * 2)[:, 3::4].astype(np.uint8)
    return y, u, v


def join_planes(y: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    out = np.empty((H, W * 2), np.uint8)
    out[:, 0::4] = y[:, 0::2]
    out[:, 1::4] = u
    out[:, 2::4] = y[:, 1::2]
    out[:, 3::4] = v
    return out.reshape(-1)


def yuv_to_rgb(y: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    uu = np.repeat(u.astype(np.float32), 2, axis=1)
    vv = np.repeat(v.astype(np.float32), 2, axis=1)
    yy = y.astype(np.float32)
    r = yy + 1.402 * (vv - 128)
    g = yy - 0.344136 * (uu - 128) - 0.714136 * (vv - 128)
    b = yy + 1.772 * (uu - 128)
    return np.clip(np.stack([r, g, b], -1), 0, 255).astype(np.uint8)


def shift_plane(p: np.ndarray, dx: int, dy: int) -> np.ndarray:
    h, w = p.shape
    xs = np.clip(np.arange(w) - dx, 0, w - 1)
    ys = np.clip(np.arange(h) - dy, 0, h - 1)
    return p[ys][:, xs]


def bilinear_sample(src: np.ndarray, cx: np.ndarray, cy: np.ndarray) -> np.ndarray:
    hh, ww = src.shape
    x0 = np.clip(np.floor(cx).astype(np.int64), 0, ww - 1)
    y0 = np.clip(np.floor(cy).astype(np.int64), 0, hh - 1)
    x1 = np.clip(x0 + 1, 0, ww - 1)
    y1 = np.clip(y0 + 1, 0, hh - 1)
    wx = np.clip(cx - np.floor(cx), 0, 1)
    wy = np.clip(cy - np.floor(cy), 0, 1)
    a = src[y0][:, x0]
    b = src[y0][:, x1]
    c = src[y1][:, x0]
    d = src[y1][:, x1]
    wx = wx[None, :]
    wy = wy[:, None]
    return a * (1 - wx) * (1 - wy) + b * wx * (1 - wy) \
        + c * (1 - wx) * wy + d * wx * wy


def shift_frac(p: np.ndarray, dx: float, dy: float) -> np.ndarray:
    f = p.astype(np.float64)
    h, w = f.shape
    return bilinear_sample(f, np.arange(w) - dx, np.arange(h) - dy)


def bilinear_grid(src: np.ndarray, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Bilinear sample of float src at full-grid coords X,Y (edge replicate)."""
    hh, ww = src.shape
    fx, fy = np.floor(X), np.floor(Y)
    x0 = np.clip(fx.astype(np.int64), 0, ww - 1)
    y0 = np.clip(fy.astype(np.int64), 0, hh - 1)
    x1 = np.clip(x0 + 1, 0, ww - 1)
    y1 = np.clip(y0 + 1, 0, hh - 1)
    wx = np.clip(X - fx, 0, 1)
    wy = np.clip(Y - fy, 0, 1)
    return (src[y0, x0] * (1 - wx) * (1 - wy)
            + src[y0, x1] * wx * (1 - wy)
            + src[y1, x0] * (1 - wx) * wy
            + src[y1, x1] * wx * wy)


def xdiff(a: bytes, b: bytes):
    aa = np.frombuffer(a, np.uint8).astype(np.int16)
    bb = np.frombuffer(b, np.uint8).astype(np.int16)
    d = np.abs(aa - bb)
    nz = d[d > 0]
    if len(nz) == 0:
        return 0, 0, 0.0
    return int(len(nz)), int(nz.max()), float(nz.mean())


def y_hist(d: np.ndarray):
    nz = d[d > 0]
    return [int(((nz >= lo) & (nz < hi)).sum())
            for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 256))]


def bands_of(f: np.ndarray):
    bands = np.array_split(np.arange(H), 3)
    return [int(f[b].sum()) for b in bands]


def rint_u8(f: np.ndarray) -> np.ndarray:
    return np.clip(np.rint(f), 0, 255).astype(np.uint8)


# ---------------- Test W: weighted blend ----------------

def synth_w_bytes(v0b: bytes, fullb: bytes, w: float) -> bytes:
    # full + floor(w*(v0-full)): exact on static bytes (w*0==0), so no
    # float-sum artifact; at w=0.5 equals (v0+full)//2 for all int bytes.
    a = np.frombuffer(v0b, np.uint8).astype(np.float64)
    b = np.frombuffer(fullb, np.uint8).astype(np.float64)
    return np.clip(b + np.floor(w * (a - b)), 0, 255).astype(np.uint8).tobytes()


def static_flips(v0b: bytes, fullb: bytes, ws) -> int:
    a = np.frombuffer(v0b, np.uint8)
    mx = 0
    for w in ws:
        s = np.frombuffer(synth_w_bytes(v0b, fullb, w), np.uint8)
        mx = max(mx, int(((a == np.frombuffer(fullb, np.uint8)) & (s != a)).sum()))
    return mx


def residual_row(sy, ym, synth: bytes, mid: bytes):
    xd, xm, xn = xdiff(synth, mid)
    dsr = np.abs(sy.astype(np.int16) - ym.astype(np.int16))
    return {"xd": xd, "xm": xm, "xn": xn, "yhist": y_hist(dsr),
            "respx": int((dsr > 0).sum()),
            "bands": bands_of((dsr > 0).astype(np.int64)),
            "fnv": f"{fnv1a(synth):016x}",
            "sha": hashlib.sha256(synth).hexdigest()[:16]}


def sweep(v0b: bytes, midb: bytes, fullb: bytes, ws):
    ym = split_planes(np.frombuffer(midb, np.uint8))[0]
    rows = []
    for w in ws:
        s = synth_w_bytes(v0b, fullb, w)
        sy = split_planes(np.frombuffer(s, np.uint8))[0]
        r = residual_row(sy, ym, s, midb)
        rows.append((w, r, s))
    return rows


def best_of(rows):
    bi = min(range(len(rows)), key=lambda i: rows[i][1]["xd"])
    return bi, rows[bi]


def rounding_variants(v0b: bytes, fullb: bytes):
    a = np.frombuffer(v0b, np.uint8).astype(np.float64)
    b = np.frombuffer(fullb, np.uint8).astype(np.float64)
    m = (a + b) / 2.0
    return {"floor": np.clip(np.floor(m), 0, 255).astype(np.uint8).tobytes(),
            "half-up": np.clip(np.floor(m + 0.5), 0, 255).astype(np.uint8).tobytes(),
            "half-even": np.clip(np.rint(m), 0, 255).astype(np.uint8).tobytes(),
            "ceil": np.clip(np.ceil(m), 0, 255).astype(np.uint8).tobytes()}


def feasibility_bound(v0b: bytes, midb: bytes, fullb: bytes):
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    out = (m < lo) | (m > hi)
    n_raw = int(out.sum())
    yo = out.reshape(H, W * 2)
    ymask = np.empty((H, W), bool)
    ymask[:, 0::2] = yo[:, 0::4]
    ymask[:, 1::2] = yo[:, 2::4]
    return n_raw, int(ymask.sum())


def mid_split(v0b: bytes, midb: bytes, fullb: bytes, synth: bytes):
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    res = s != m
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    outside = res & ((m < lo) | (m > hi))
    static = res & (a == b) & ~outside
    eqv0 = res & (m == a) & (a != b) & ~outside
    eqfull = res & (m == b) & (a != b) & ~outside
    interior = res & ~outside & ~static & ~eqv0 & ~eqfull
    return {"n": int(res.sum()), "outside": int(outside.sum()),
            "static": int(static.sum()), "mid==v0": int(eqv0.sum()),
            "mid==full": int(eqfull.sum()), "interior": int(interior.sum())}


# ---------------- Test P: edge phase ----------------

def grad_tables(ym: np.ndarray, sy: np.ndarray, y0: np.ndarray, y1: np.ndarray, tag: str):
    yp = np.pad(ym.astype(np.int16), 1, mode="edge")
    gx = (yp[1:-1, 2:] - yp[1:-1, :-2]) // 2
    gy = (yp[2:, 1:-1] - yp[:-2, 1:-1]) // 2
    mag = np.abs(gx) + np.abs(gy)
    ang = np.arctan2(gy, gx)  # -pi..pi
    obin = np.full(mag.shape, 8, np.int8)
    nz = mag > 0
    obin[nz] = np.floor((ang[nz] + np.pi) / (np.pi / 4)).astype(np.int8) % 8
    res = sy.astype(np.int16) != ym.astype(np.int16)
    sgn = np.sign(sy.astype(np.int16) - ym.astype(np.int16))
    print(f"== {tag}: P1 residual rate per gradient decile ==")
    qs = np.quantile(mag, np.linspace(0, 1, 11))
    print("decile edges: " + " ".join(f"{q:.0f}" for q in qs))
    dec = np.clip(np.digitize(mag, qs[1:-1], right=True), 0, 9)
    for d in range(10):
        sel = dec == d
        n, r = int(sel.sum()), int((sel & res).sum())
        print(f"dec {d}: px={n} respx={r} rate={r / n if n else 0:.4f}")
    q3 = float(np.quantile(mag, 0.75))
    topq = mag >= q3
    carry = int((topq & res).sum())
    print(f"top-quartile (mag>={q3:.0f}): px={int(topq.sum())} "
          f"respx={carry} carry={carry / int(res.sum()):.4f}")
    print(f"== {tag}: P2/P3 per orientation bin (count/rate/pos-frac) ==")
    for o in range(9):
        sel = obin == o
        n = int(sel.sum())
        rsel = sel & res
        r = int(rsel.sum())
        pos = int(((sgn > 0) & rsel).sum())
        neg = int(((sgn < 0) & rsel).sum())
        nm = "flat" if o == 8 else f"{o * 45 - 180:+d}..{o * 45 - 135:+d}deg"
        print(f"obin {o} ({nm}): px={n} respx={r} rate={r / n if n else 0:.4f} "
              f"pos={pos} neg={neg} posfrac={pos / r if r else 0:.4f}")
    print(f"== {tag}: P4 moved-mask membership ==")
    mm = y0 != y1
    for name, sel in (("inside", mm), ("outside", ~mm)):
        n = int(sel.sum())
        r = int((sel & res).sum())
        print(f"{name}: px={n} respx={r} rate={r / n if n else 0:.4f}")
    return {"carry_topq": carry / int(res.sum()), "respx": int(res.sum())}


# ---------------- Test A: affine ----------------

def affine_src(p, xs: np.ndarray, ys: np.ndarray):
    """Inverse-map source coords for output grid (xs,ys); +t moves content
    +x/+y (shift_frac convention); rotation/scale/shear act about the
    frame center (origin-based rotation couples catastrophically with
    translation in coordinate descent — see REPORT). p=(tx,ty,th_deg,s,shx,shy)."""
    tx, ty, th, s, shx, shy = p
    c, sn = np.cos(np.deg2rad(th)), np.sin(np.deg2rad(th))
    Af = np.array([[c, -sn], [sn, c]]) @ (s * np.array([[1.0, shx], [shy, 1.0]]))
    Ai = np.linalg.inv(Af)
    X, Y = np.meshgrid(xs, ys)
    cx, cy = (len(xs) - 1) / 2.0, (len(ys) - 1) / 2.0
    d = np.stack([(X - cx - tx).ravel(), (Y - cy - ty).ravel()], 0)
    S = Ai @ d
    return (S[0] + cx).reshape(X.shape), (S[1] + cy).reshape(Y.shape)


def warp_affine(img: np.ndarray, p) -> np.ndarray:
    f = img.astype(np.float64)
    h, w = f.shape
    X, Y = affine_src(p, np.arange(w), np.arange(h))
    return bilinear_grid(f, X, Y)


def half_param(p, sign):
    tx, ty, th, s, shx, shy = p
    s2 = np.sqrt(s) if sign > 0 else 1.0 / np.sqrt(s)
    return (sign * tx / 2, sign * ty / 2, sign * th / 2, s2,
            sign * shx / 2, sign * shy / 2)


A_STEPS = (("tx", 0.5), ("ty", 0.5), ("th", 0.25), ("s", 0.001),
           ("shx", 0.001), ("shy", 0.001))


def affine_fit(y0: np.ndarray, y1: np.ndarray):
    mask = y0 != y1
    y0f, y1f = y0.astype(np.float64), y1.astype(np.float64)
    p = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    idx = {"tx": 0, "ty": 1, "th": 2, "s": 3, "shx": 4, "shy": 5}

    def sad(q):
        wimg = warp_affine(y0f, q)
        return float(np.abs(wimg - y1f)[mask].sum())

    cur = sad(p)
    sad00 = cur
    for _ in range(2):
        for name, delta in A_STEPS:
            i = idx[name]
            base = p[i]
            best_v, best_s = base, cur
            for k in (-2, -1, 1, 2):
                q = list(p)
                q[i] = base + k * delta
                if name == "s" and q[i] <= 0:
                    continue
                v = sad(q)
                if v < best_s:
                    best_s, best_v = v, q[i]
            p[i], cur = best_v, best_s
    return tuple(p), cur, sad00, int(mask.sum())


def affine_synth(y0, u0, v0p, y1, u1, v1p, p):
    ph = half_param(p, +1)
    mh = half_param(p, -1)
    sy = ((rint_u8(warp_affine(y0, ph)).astype(np.uint16)
           + rint_u8(warp_affine(y1, mh)).astype(np.uint16)) // 2).astype(np.uint8)
    tx, ty = p[0], p[1]
    su = ((rint_u8(shift_frac(u0, tx / 4, ty / 4)).astype(np.uint16)
           + rint_u8(shift_frac(u1, -tx / 4, -ty / 4)).astype(np.uint16)) // 2).astype(np.uint8)
    sv = ((rint_u8(shift_frac(v0p, tx / 4, ty / 4)).astype(np.uint16)
           + rint_u8(shift_frac(v1p, -tx / 4, -ty / 4)).astype(np.uint16)) // 2).astype(np.uint8)
    return sy, su, sv


# ---------------- Model B (vendored M17, for the field-fit corroboration) ----

BLOCK = 16
BM_RANGE = 4
BM_DEGEN_MIN = 4
HALF8 = [(-0.5, -0.5), (0.0, -0.5), (0.5, -0.5),
         (-0.5, 0.0), (0.5, 0.0),
         (-0.5, 0.5), (0.0, 0.5), (0.5, 0.5)]


def sample_block(src: np.ndarray, x0: int, y0: int, w: int, h: int,
                 dx: float, dy: float) -> np.ndarray:
    return bilinear_sample(src.astype(np.float64),
                           x0 + np.arange(w) - dx, y0 + np.arange(h) - dy)


def block_integer_search(y0i, y1i, x0, y0, mblk):
    bh, bw = mblk.shape
    yy, xx = np.mgrid[0:bh, 0:bw]
    tgt = y1i[y0:y0 + bh, x0:x0 + bw].astype(np.int16)
    best, best_sad = (0, 0), None
    for dy in range(-BM_RANGE, BM_RANGE + 1):
        sy = np.clip(y0 + yy - dy, 0, H - 1)
        for dx in range(-BM_RANGE, BM_RANGE + 1):
            sx = np.clip(x0 + xx - dx, 0, W - 1)
            sad = int(np.abs(y0i[sy, sx] - tgt)[mblk].sum())
            if best_sad is None or sad < best_sad:
                best_sad, best = sad, (dx, dy)
    return best, best_sad


def block_half_refine(y0f, y1f, x0, y0, mblk, base):
    tgt = sample_block(y1f, x0, y0, BLOCK, BLOCK, 0, 0)
    bdx, bdy = base
    best, best_sad = (float(bdx), float(bdy)), None
    cands = [(float(bdx), float(bdy))] + [(bdx + ox, bdy + oy) for ox, oy in HALF8]
    for dx, dy in cands:
        s = sample_block(y0f, x0, y0, BLOCK, BLOCK, dx, dy)
        sad = float(np.abs(s - tgt)[mblk].sum())
        if best_sad is None or sad < best_sad:
            best_sad, best = sad, (dx, dy)
    return best, best_sad


def model_b_vecs(y0, y1):
    mask = y0 != y1
    y0i, y1i = y0.astype(np.int16), y1.astype(np.int16)
    y0f, y1f = y0.astype(np.float64), y1.astype(np.float64)
    vecs, nms, ctrs = [], [], []
    for by in range(0, H, BLOCK):
        for bx in range(0, W, BLOCK):
            mblk = mask[by:by + BLOCK, bx:bx + BLOCK]
            nm = int(mblk.sum())
            nms.append(nm)
            ctrs.append((bx + BLOCK // 2, by + BLOCK // 2))
            if nm < BM_DEGEN_MIN:
                vecs.append((0.0, 0.0))
            else:
                (bdx, bdy), _ = block_integer_search(y0i, y1i, bx, by, mblk)
                (vx, vy), _ = block_half_refine(y0f, y1f, bx, by, mblk, (bdx, bdy))
                vecs.append((vx, vy))
    return vecs, nms, ctrs


def affine_field_fit(vecs, nms, ctrs):
    sel = [i for i, nm in enumerate(nms) if nm >= BM_DEGEN_MIN]
    A = np.array([[ctrs[i][0], ctrs[i][1], 1.0] for i in sel])
    bx = np.array([vecs[i][0] for i in sel])
    by = np.array([vecs[i][1] for i in sel])
    cx, *_ = np.linalg.lstsq(A, bx, rcond=None)
    cy, *_ = np.linalg.lstsq(A, by, rcond=None)
    px, py = A @ cx, A @ cy
    r2x = 1 - ((bx - px) ** 2).sum() / ((bx - bx.mean()) ** 2).sum()
    r2y = 1 - ((by - py) ** 2).sum() / ((by - by.mean()) ** 2).sum()
    return cx, cy, float(r2x), float(r2y), len(sel)


# ---------------- loo.txt ----------------

def parse_loo(path: Path):
    out = {}
    pat = re.compile(r"^\|\s*(\d+)\s*\|\s*\([^)]*\)\s*\|\s*(\d+)\s*\|\s*(\d+)")
    for line in path.read_text(errors="replace").splitlines():
        m = pat.match(line)
        if m:
            out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return out


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin", m15d / "m15-v0.bin",
              m15d / "m15-mid.bin", m15d / "m15-full.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")

    def triplet(v0b: bytes, midb: bytes, fullb: bytes):
        y0, u0, v0p = split_planes(np.frombuffer(v0b, np.uint8))
        ym, um, vm = split_planes(np.frombuffer(midb, np.uint8))
        y1, u1, v1p = split_planes(np.frombuffer(fullb, np.uint8))
        return y0, u0, v0p, ym, um, vm, y1, u1, v1p

    # ---- Model 0 recompute + cross-check ----
    print("== model 0 (baseline recompute) ==")
    v0 = load_dump(m15d / "m15-v0.bin")
    mid = load_dump(m15d / "m15-mid.bin")
    full = load_dump(m15d / "m15-full.bin")
    m15 = triplet(v0, mid, full)
    b15 = synth_w_bytes(v0, full, 0.5)
    r15_0 = residual_row(split_planes(np.frombuffer(b15, np.uint8))[0],
                         m15[3], b15, mid)
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    s0 = triplet(v0, mid, full)
    b0 = synth_w_bytes(v0, full, 0.5)
    r0_0 = residual_row(split_planes(np.frombuffer(b0, np.uint8))[0],
                        s0[3], b0, mid)
    print(f"m15 baseline: R_0={r15_0['xd']} fnv={r15_0['fnv']} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0_0['xd']} fnv={r0_0['fnv']} (want {R0_M16} / {FNV_BLEND_S0})")
    if r0_0["xd"] != R0_M16 or r15_0["xd"] != R0_M15 or r0_0["fnv"] != FNV_BLEND_S0:
        print("MISMATCH vs M16/M17 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK (w=0.5 floor == M15 blend byte-exact)")

    # affine self-checks (translation-only == shift_frac; identity exact)
    y0t = s0[0]
    d_tr = float(np.abs(warp_affine(y0t, (0.5, 0.0, 0, 1, 0, 0))
                         - shift_frac(y0t, 0.5, 0.0)).max())
    d_id = float(np.abs(warp_affine(y0t, (0, 0, 0, 1, 0, 0))
                         - y0t.astype(np.float64)).max())
    print(f"affine self-check: max|warp-shift_frac|@t=(0.5,0) = {d_tr}; "
          f"max|warp-id| = {d_id}")

    # ---- Test W: fine sweeps ----
    print("== Test W: fine sweep s0 ==")
    t0 = time.time()
    rows0 = sweep(v0, mid, full, W_FINE)
    t_wf = time.time() - t0
    for w, r, _ in rows0:
        print(f"w={w:.3f}: R={r['xd']} xdmax={r['xm']} xdmean={r['xn']:.3f} "
              f"respx={r['respx']} hist={r['yhist']} bands={r['bands']} fnv={r['fnv']}")
    bi0, (bw0, br0, bs0) = best_of(rows0)
    e_w0 = (r0_0["xd"] - br0["xd"]) / r0_0["xd"]
    print(f"s0-W: {t_wf:.1f}s best w={bw0:.3f} R={br0['xd']} "
          f"explained={r0_0['xd'] - br0['xd']} e_W={e_w0:.4f}")
    (workd / "m18-synth-W-s0000.bin").write_bytes(bs0)

    print("== Test W: fine sweep m15 ==")
    v015 = load_dump(m15d / "m15-v0.bin")
    mid15 = load_dump(m15d / "m15-mid.bin")
    full15 = load_dump(m15d / "m15-full.bin")
    rows15 = sweep(v015, mid15, full15, W_FINE)
    for w, r, _ in rows15:
        print(f"w={w:.3f}: R={r['xd']} xdmax={r['xm']} xdmean={r['xn']:.3f} "
              f"respx={r['respx']} hist={r['yhist']} bands={r['bands']} fnv={r['fnv']}")
    bi15, (bw15, br15, bs15) = best_of(rows15)
    e_w15 = (r15_0["xd"] - br15["xd"]) / r15_0["xd"]
    print(f"m15-W: best w={bw15:.3f} R={br15['xd']} "
          f"explained={r15_0['xd'] - br15['xd']} e_W={e_w15:.4f}")
    (workd / "m18-synth-W-m15.bin").write_bytes(bs15)
    print(f"static-flip guard (want 0): s0 max={static_flips(v0, full, W_FINE)} "
          f"m15 max={static_flips(v015, full15, W_FINE)} over fine grid")

    # ---- Test W: rounding variants ----
    print("== Test W: rounding variants @w=0.5 ==")
    for tag, (vv, mm) in (("s0", (v0, mid)), ("m15", (v015, mid15))):
        ff = full if tag == "s0" else full15
        yy = s0[3] if tag == "s0" else m15[3]
        base = r0_0["xd"] if tag == "s0" else r15_0["xd"]
        for name, s in rounding_variants(vv, ff).items():
            sy = split_planes(np.frombuffer(s, np.uint8))[0]
            r = residual_row(sy, yy, s, mm)
            print(f"{tag} {name}: R={r['xd']} explained={base - r['xd']} "
                  f"frac={1 - r['xd'] / base:.4f} fnv={r['fnv']}")

    # ---- Test W: feasibility bound + mid split ----
    print("== Test W: weight-feasibility bound (mid outside [v0,full]) ==")
    for tag, (vv, mm, ff) in (("s0", (v0, mid, full)),
                              ("m15", (v015, mid15, full15))):
        nraw, nyp = feasibility_bound(vv, mm, ff)
        base = r0_0["xd"] if tag == "s0" else r15_0["xd"]
        print(f"{tag}: raw bytes={nraw} ({nraw / base:.4f} of R_0) Y px={nyp}")
    print("== Test W: mid-position 5-way split of blend residual ==")
    for tag, (vv, mm, ff) in (("s0", (v0, mid, full)),
                              ("m15", (v015, mid15, full15))):
        bl = synth_w_bytes(vv, ff, 0.5)
        sp = mid_split(vv, mm, ff, bl)
        tot = sp["n"]
        print(f"{tag}: n={tot} " + " ".join(
            f"{k}={v}({v / tot:.4f})" for k, v in sp.items() if k != "n"))

    # ---- Test W: coarse sweep all 764 shapes ----
    print("== Test W: coarse sweep all M16 shapes ==")
    shapes = sorted(int(p.name[8:12]) for p in m16d.glob("m16-v0-s*.bin"))
    print(f"shapes: n={len(shapes)} 0..{max(shapes)}")
    loo = parse_loo(m16d / "loo.txt")
    print(f"loo.txt parsed R_s rows: n={len(loo)}")
    t1 = time.time()
    argmins = {}
    print("| shape | argmin w | Rmin | R_s(M16) | explained (R_s-Rmin) |")
    print("| ---: | ---: | ---: | ---: | ---: |")
    for i, s in enumerate(shapes):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        best_w, best_xd = 0.5, None
        for w in W_COARSE:
            syn = synth_w_bytes(vv, ff, w)
            xd, _, _ = xdiff(syn, mm)
            if best_xd is None or xd < best_xd:
                best_xd, best_w = xd, w
        rs = loo.get(s, ("?", "?"))[1]
        exp = ("?" if rs == "?" else rs - best_xd)
        argmins[s] = best_w
        print(f"| {s} | {best_w:.1f} | {best_xd} | {rs} | {exp} |")
        if (i + 1) % 200 == 0:
            print(f"  ... W {i + 1}/{len(shapes)}")
    t1 = time.time() - t1
    print(f"coarse-sweep wall: {t1:.1f}s for {len(shapes)} shapes (sequential)")
    dist = Counter(argmins.values())
    print(f"W argmin distribution: {dict(sorted(dist.items()))}")

    # ---- Test P ----
    sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
    sy15 = split_planes(np.frombuffer(b15, np.uint8))[0]
    p0 = grad_tables(s0[3], sy0, s0[0], s0[6], "s0")
    p15 = grad_tables(m15[3], sy15, m15[0], m15[6], "m15")

    # ---- Gate + Test A ----
    a_ran = False
    ra_s0, ra_15, pa_s0, pa_15 = None, None, None, None
    print(f"== Gate: e_W(s0)={e_w0:.4f} -> Test A {'RUNS' if e_w0 < 0.5 else 'SKIPPED'} ==")
    if e_w0 < 0.5:
        a_ran = True
        print("== Test A: affine fit s0 ==")
        t2 = time.time()
        pa_s0, sadb, sad00, nm = affine_fit(s0[0], s0[6])
        t_a0 = time.time() - t2
        sy, su, sv = affine_synth(*s0[:3], *s0[6:9], pa_s0)
        syna = join_planes(sy, su, sv).tobytes()
        ra_s0 = residual_row(sy, s0[3], syna, mid)
        e_a0 = (r0_0["xd"] - ra_s0["xd"]) / r0_0["xd"]
        (workd / "m18-synth-A-s0000.bin").write_bytes(syna)
        print(f"s0-A: {t_a0:.1f}s p=(tx={pa_s0[0]:+.3f},ty={pa_s0[1]:+.3f},"
              f"th={pa_s0[2]:+.3f}d,s={pa_s0[3]:.4f},shx={pa_s0[4]:+.4f},"
              f"shy={pa_s0[5]:+.4f}) est_sad00={sad00:.0f} est_sadbest={sadb:.0f} nm={nm}")
        print(f"s0-A residual: R_A={ra_s0['xd']} explained={r0_0['xd'] - ra_s0['xd']} "
              f"e_A={e_a0:.4f} xdmax={ra_s0['xm']} xdmean={ra_s0['xn']:.3f} "
              f"respx={ra_s0['respx']} hist={ra_s0['yhist']} bands={ra_s0['bands']} "
              f"fnv={ra_s0['fnv']}")
        print("== Test A: affine fit m15 ==")
        t3 = time.time()
        pa_15, sadb15, sad0015, nm15 = affine_fit(m15[0], m15[6])
        t_a15 = time.time() - t3
        sy, su, sv = affine_synth(*m15[:3], *m15[6:9], pa_15)
        syna15 = join_planes(sy, su, sv).tobytes()
        ra_15 = residual_row(sy, m15[3], syna15, mid15)
        e_a15 = (r15_0["xd"] - ra_15["xd"]) / r15_0["xd"]
        (workd / "m18-synth-A-m15.bin").write_bytes(syna15)
        print(f"m15-A: {t_a15:.1f}s p=(tx={pa_15[0]:+.3f},ty={pa_15[1]:+.3f},"
              f"th={pa_15[2]:+.3f}d,s={pa_15[3]:.4f},shx={pa_15[4]:+.4f},"
              f"shy={pa_15[5]:+.4f}) est_sad00={sad0015:.0f} est_sadbest={sadb15:.0f} nm={nm15}")
        print(f"m15-A residual: R_A={ra_15['xd']} explained={r15_0['xd'] - ra_15['xd']} "
              f"e_A={e_a15:.4f} xdmax={ra_15['xm']} xdmean={ra_15['xn']:.3f} "
              f"respx={ra_15['respx']} hist={ra_15['yhist']} bands={ra_15['bands']} "
              f"fnv={ra_15['fnv']}")
        print("== Test A corroboration: affine fit to Model-B block field (s0) ==")
        t4 = time.time()
        vecs, nms, ctrs = model_b_vecs(s0[0], s0[6])
        cx, cy, r2x, r2y, nsel = affine_field_fit(vecs, nms, ctrs)
        print(f"B-field: {time.time() - t4:.1f}s blocks={len(vecs)} fitted={nsel}")
        print(f"vx = {cx[0]:+.5f}*x {cx[1]:+.5f}*y {cx[2]:+.3f}  R2={r2x:.4f}")
        print(f"vy = {cy[0]:+.5f}*x {cy[1]:+.5f}*y {cy[2]:+.3f}  R2={r2y:.4f}")

    # ---- Test C: per-carrier masked sweeps ----
    print("== Test C: top-10 carriers from loo.txt ==")
    shares = {s: (R0_M16 - rs) for s, (_, rs) in loo.items() if s != 0}
    top10 = sorted(shares, key=lambda s: -shares[s])[:10]
    print(f"derived top-10 shapes: {top10}")
    print(f"derived shares: {[shares[s] for s in top10]}")
    if top10 != M16_TOP10 or [shares[s] for s in top10] != M16_TOP10_SHARES:
        print("CARRIER MISMATCH vs M16 REPORT top-10: STOP per-carrier, tabled.")
    else:
        print("carrier cross-check vs M16 REPORT: OK")
        res0 = sy0.astype(np.int16) != s0[3].astype(np.int16)
        for rank, s in enumerate(top10, 1):
            vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
            mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
            ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
            bl = synth_w_bytes(vv, ff, 0.5)
            yb = split_planes(np.frombuffer(bl, np.uint8))[0]
            ym = split_planes(np.frombuffer(mm, np.uint8))[0]
            ress = yb.astype(np.int16) != ym.astype(np.int16)
            removed = res0 & ~ress
            nrem = int(removed.sum())
            bd = bands_of(removed.astype(np.int64))
            print(f"rank {rank} shape {s}: share={shares[s]} removedYpx={nrem} bands={bd}")
            s0v = np.frombuffer(v0, np.uint8).astype(np.float64)
            s0f = np.frombuffer(full, np.uint8).astype(np.float64)
            s0m = np.frombuffer(mid, np.uint8)
            ysel = np.zeros(N, bool)
            ysel[0::4] = removed[:, 0::2].ravel()
            ysel[2::4] = removed[:, 1::2].ravel()
            curve = []
            for w in W_FINE:
                syn = np.clip(s0f + np.floor(w * (s0v - s0f)), 0, 255).astype(np.uint8)
                rk = int(((syn != s0m)[ysel]).sum())
                curve.append((w, rk))
            bwk = min(curve, key=lambda t: t[1])
            cstr = " ".join(f"{w:.3f}:{rk}" for w, rk in curve)
            print(f"  masked curve: {cstr}")
            print(f"  argmin w={bwk[0]:.3f} Rk={bwk[1]} (at w=0.5: "
                  f"{dict(curve)[0.5]})")

    # ---- determinism re-run ----
    print("== determinism re-run (same inputs, second pass) ==")
    rows0b = sweep(v0, mid, full, W_FINE)
    same_w = [r["xd"] for _, r, _ in rows0] == [r["xd"] for _, r, _ in rows0b]
    _, (_, _, bs0b) = best_of(rows0b)
    print(f"W s0 rerun: R-curve identical={same_w} "
          f"best fnv {fnv1a(bs0):016x} vs {fnv1a(bs0b):016x} identical={bs0 == bs0b}")
    if a_ran:
        pa2, _, _, _ = affine_fit(s0[0], s0[6])
        sy, su, sv = affine_synth(*s0[:3], *s0[6:9], pa2)
        syna2 = join_planes(sy, su, sv).tobytes()
        syna1 = (workd / "m18-synth-A-s0000.bin").read_bytes()
        print(f"A s0 rerun: p identical={pa2 == pa_s0} "
              f"fnv {fnv1a(syna1):016x} vs {fnv1a(syna2):016x} identical={syna1 == syna2}")

    # ---- PNGs ----
    print("== PNGs ==")
    rgbm = yuv_to_rgb(s0[3], s0[4], s0[5])
    outs = []
    # R(w) curve plot (PIL-drawn)
    PW, PH, PAD = 640, 400, 46
    plot = Image.new("RGB", (PW, PH), (16, 16, 16))
    dr = ImageDraw.Draw(plot)
    allr = [r["xd"] for _, r, _ in rows0] + [r["xd"] for _, r, _ in rows15]
    lo, hi = min(allr), max(allr)
    span = hi - lo or 1
    lo -= span * 0.08
    hi += span * 0.08

    def xy(w, r):
        return (PAD + (w - 0.30) / 0.40 * (PW - 2 * PAD),
                PH - PAD - (r - lo) / (hi - lo) * (PH - 2 * PAD))

    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = PH - PAD - f * (PH - 2 * PAD)
        dr.line([(PAD, yy), (PW - PAD, yy)], fill=(48, 48, 48))
        dr.text((4, yy - 6), f"{lo + f * (hi - lo):.0f}", fill=(180, 180, 180))
    for w in (0.30, 0.40, 0.50, 0.60, 0.70):
        xx = PAD + (w - 0.30) / 0.40 * (PW - 2 * PAD)
        dr.line([(xx, PAD), (xx, PH - PAD)], fill=(48, 48, 48))
        dr.text((xx - 12, PH - PAD + 4), f"{w:.2f}", fill=(180, 180, 180))
    dr.line([xy(0.5, lo), xy(0.5, hi)], fill=(90, 90, 90))
    dr.text((PAD, 6), "R(w) s0=yellow m15=cyan, vline=w0.5", fill=(220, 220, 220))
    for rows, col in ((rows0, (255, 255, 0)), (rows15, (0, 255, 255))):
        pts = [xy(w, r["xd"]) for w, r, _ in rows]
        dr.line(pts, fill=col, width=2)
        for x, y in pts:
            dr.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col)
    outs.append(("m18-wcurve.png", np.asarray(plot)))
    # orientation-colored residual phase map (fold 8 bins -> 4 edge orientations)
    yp = np.pad(s0[3].astype(np.int16), 1, mode="edge")
    gx = (yp[1:-1, 2:] - yp[1:-1, :-2]) // 2
    gy = (yp[2:, 1:-1] - yp[:-2, 1:-1]) // 2
    ang = (np.arctan2(gy, gx) + np.pi) % np.pi  # 0..pi edge orientation
    ebin = np.clip((ang / (np.pi / 4)).astype(np.int8), 0, 3)
    ebin[(np.abs(gx) + np.abs(gy)) == 0] = -1
    res = sy0.astype(np.int16) != s0[3].astype(np.int16)
    cols = np.array([[255, 0, 0], [0, 255, 0], [0, 128, 255], [255, 255, 0]])
    base = (0.35 * rgbm.astype(np.float32))
    over = base.copy()
    for e in range(4):
        sel = res & (ebin == e)
        over[sel] = cols[e]
    sel = res & (ebin == -1)
    over[sel] = np.array([255, 255, 255])
    outs.append(("m18-phasemap.png", over.astype(np.uint8)))
    total = 0
    for name, arr in outs:
        p = evidd / name
        if name == "m18-phasemap.png":
            Image.fromarray(arr).resize((320, 224), Image.BILINEAR).save(p)
        else:
            Image.fromarray(arr).save(p)
        total += p.stat().st_size
        print(f"png {p}: {p.stat().st_size} B")
    print(f"png total: {total} B (budget 5242880)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: W=weight-sweep P=edge-phase A=affine(if-gated) C=per-carrier")


if __name__ == "__main__":
    main()

