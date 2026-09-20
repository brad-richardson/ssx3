#!/usr/bin/env python3
"""M17 sub-pixel / local motion model for the synth residual (offline).

Usage: m17.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets (m16-v0/mid/full-sNNNN.bin) and the M15
triplet (m15-v0/mid/full.bin); raw XFB dumps, 573440 B = 640x448 YUYV.
Read-only inputs; writes compensated synths + receipt text to WORK_DIR
and PNGs to EVID_DIR.

Models (see DESIGN.md, recorded before running):
  0: baseline blend (= M16 synth, all integer shifts (0,0)), recomputed.
  G: global half-pixel: 25-candidate {dx,dy in {-1,-.5,0,.5,1}} masked
     SAD on Y, synth = mean of bilinear half-compensated v0/full.
  B: block matching: B=16 (40x28 grid), integer +-4 + half-pel refine
     per block on Y, per-block half-compensated synth.
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
HALF_GRID = (-1.0, -0.5, 0.0, 0.5, 1.0)
BLOCK = 16
BM_RANGE = 4
BM_DEGEN_MIN = 4  # moved-Y px per block below which v=(0,0) by rule
HALF8 = [(-0.5, -0.5), (0.0, -0.5), (0.5, -0.5),
         (-0.5, 0.0), (0.5, 0.0),
         (-0.5, 0.5), (0.0, 0.5), (0.5, 0.5)]


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
    """Shift by (dx,dy) with edge replicate; +dx moves content right."""
    h, w = p.shape
    xs = np.clip(np.arange(w) - dx, 0, w - 1)
    ys = np.clip(np.arange(h) - dy, 0, h - 1)
    return p[ys][:, xs]


def bilinear_sample(src: np.ndarray, cx: np.ndarray, cy: np.ndarray) -> np.ndarray:
    """Sample float frame src at outer-grid (cx, cy), edge replicate."""
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
    """Bilinear shift by (dx,dy), edge replicate; same sign as shift_plane."""
    f = p.astype(np.float64)
    h, w = f.shape
    return bilinear_sample(f, np.arange(w) - dx, np.arange(h) - dy)


def sample_block(src: np.ndarray, x0: int, y0: int, w: int, h: int,
                 dx: float, dy: float) -> np.ndarray:
    """Bilinear w*h block with top-left (x0,y0), shifted by (dx,dy)."""
    return bilinear_sample(src.astype(np.float64),
                           x0 + np.arange(w) - dx, y0 + np.arange(h) - dy)


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


# ---------------- Model G: global half-pixel ----------------

def model_g(y0, u0, v0p, y1, u1, v1p):
    """Half-pel global shift + compensated synth planes. Returns dict."""
    mask = y0 != y1
    nmoved = int(mask.sum())
    y0f = y0.astype(np.float64)
    y1f = y1.astype(np.float64)
    best, best_sad, sad00 = (0.0, 0.0), None, float(np.abs(y0f - y1f)[mask].sum())
    sads = {}
    for dy in HALF_GRID:
        for dx in HALF_GRID:
            s = shift_frac(y0f, dx, dy)
            sad = float(np.abs(s - y1f)[mask].sum())
            sads[(dx, dy)] = sad
            if best_sad is None or sad < best_sad:
                best_sad, best = sad, (dx, dy)
    hx, hy = best
    sy = ((rint_u8(shift_frac(y0f, hx / 2, hy / 2)).astype(np.uint16)
           + rint_u8(shift_frac(y1f, -hx / 2, -hy / 2)).astype(np.uint16))
          // 2).astype(np.uint8)
    su = ((rint_u8(shift_frac(u0, hx / 4, hy / 4)).astype(np.uint16)
           + rint_u8(shift_frac(u1, -hx / 4, -hy / 4)).astype(np.uint16))
          // 2).astype(np.uint8)
    sv = ((rint_u8(shift_frac(v0p, hx / 4, hy / 4)).astype(np.uint16)
           + rint_u8(shift_frac(v1p, -hx / 4, -hy / 4)).astype(np.uint16))
          // 2).astype(np.uint8)
    return {"shift": best, "sad": best_sad, "sad00": sad00,
            "nmoved": nmoved, "sads": sads, "sy": sy, "su": su, "sv": sv}


# ---------------- Model B: block matching ----------------

def block_integer_search(y0i: np.ndarray, y1i: np.ndarray, x0: int, y0: int,
                         mblk: np.ndarray):
    """Best integer (dx,dy) in +-BM_RANGE for one BxB block (masked SAD)."""
    bh, bw = mblk.shape
    yy, xx = np.mgrid[0:bh, 0:bw]
    ay = np.clip(y0 + yy, 0, H - 1)
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


def block_half_refine(y0f: np.ndarray, y1f: np.ndarray, x0: int, y0: int,
                      mblk: np.ndarray, base):
    """8 half-pel neighbors of integer best; returns (vec, sad)."""
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


def model_b(y0, u0, v0p, y1, u1, v1p):
    """Block-matched shift + compensated synth planes. Returns dict."""
    mask = y0 != y1
    y0i = y0.astype(np.int16)
    y1i = y1.astype(np.int16)
    y0f = y0.astype(np.float64)
    y1f = y1.astype(np.float64)
    u0f, u1f = u0.astype(np.float64), u1.astype(np.float64)
    v0f, v1f = v0p.astype(np.float64), v1p.astype(np.float64)
    sy = np.empty((H, W), np.uint8)
    su = np.empty((H, W // 2), np.uint8)
    sv = np.empty((H, W // 2), np.uint8)
    vecs = []
    sad00_tot, sadb_tot, moved_blocks, degen_blocks = 0.0, 0.0, 0, 0
    for by in range(0, H, BLOCK):
        for bx in range(0, W, BLOCK):
            mblk = mask[by:by + BLOCK, bx:bx + BLOCK]
            nm = int(mblk.sum())
            tgt = y1f[by:by + BLOCK, bx:bx + BLOCK]
            src0 = y0f[by:by + BLOCK, bx:bx + BLOCK]
            sad00 = float(np.abs(src0 - tgt)[mblk].sum())
            sad00_tot += sad00
            if nm < BM_DEGEN_MIN:
                vx, vy, sadb = 0.0, 0.0, sad00
                degen_blocks += 1
            else:
                (bdx, bdy), _ = block_integer_search(y0i, y1i, bx, by, mblk)
                (vx, vy), sadb = block_half_refine(y0f, y1f, bx, by, mblk,
                                                   (bdx, bdy))
                moved_blocks += 1
            sadb_tot += sadb
            vecs.append((vx, vy))
            c0 = sample_block(y0f, bx, by, BLOCK, BLOCK, vx / 2, vy / 2)
            c1 = sample_block(y1f, bx, by, BLOCK, BLOCK, -vx / 2, -vy / 2)
            sy[by:by + BLOCK, bx:bx + BLOCK] = (
                (rint_u8(c0).astype(np.uint16) + rint_u8(c1).astype(np.uint16))
                // 2).astype(np.uint8)
            ux = bx // 2
            c0u = sample_block(u0f, ux, by, BLOCK // 2, BLOCK, vx / 4, vy / 4)
            c1u = sample_block(u1f, ux, by, BLOCK // 2, BLOCK, -vx / 4, -vy / 4)
            su[by:by + BLOCK, ux:ux + BLOCK // 2] = (
                (rint_u8(c0u).astype(np.uint16) + rint_u8(c1u).astype(np.uint16))
                // 2).astype(np.uint8)
            c0v = sample_block(v0f, ux, by, BLOCK // 2, BLOCK, vx / 4, vy / 4)
            c1v = sample_block(v1f, ux, by, BLOCK // 2, BLOCK, -vx / 4, -vy / 4)
            sv[by:by + BLOCK, ux:ux + BLOCK // 2] = (
                (rint_u8(c0v).astype(np.uint16) + rint_u8(c1v).astype(np.uint16))
                // 2).astype(np.uint8)
    return {"vecs": vecs, "sad00": sad00_tot, "sadbest": sadb_tot,
            "moved_blocks": moved_blocks, "degen_blocks": degen_blocks,
            "nmoved": int(mask.sum()), "sy": sy, "su": su, "sv": sv}


def residual_row(sy, ym, synth: bytes, mid: bytes):
    xd, xm, xn = xdiff(synth, mid)
    dsr = np.abs(sy.astype(np.int16) - ym.astype(np.int16))
    return {"xd": xd, "xm": xm, "xn": xn, "yhist": y_hist(dsr),
            "respx": int((dsr > 0).sum()),
            "bands": bands_of((dsr > 0).astype(np.int64)),
            "fnv": f"{fnv1a(synth):016x}",
            "sha": hashlib.sha256(synth).hexdigest()[:16]}


def parse_loo_shapes(loo_path: Path):
    """shape -> R_s from loo.txt's per-shape table (| s | shift | nm | Rs |)."""
    out = {}
    if not loo_path.exists():
        return out
    pat = re.compile(r"^\|\s*(\d+)\s*\|\s*\([^)]*\)\s*\|\s*(\d+)\s*\|\s*(\d+)")
    for line in loo_path.read_text(errors="replace").splitlines():
        m = pat.match(line)
        if m:
            out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return out


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # ---- input shas ----
    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / f"m16-full-s0000.bin", m15d / "m15-v0.bin",
              m15d / "m15-mid.bin", m15d / "m15-full.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")

    def triplet(v0b: bytes, midb: bytes, fullb: bytes):
        y0, u0, v0p = split_planes(np.frombuffer(v0b, np.uint8))
        ym, um, vm = split_planes(np.frombuffer(midb, np.uint8))
        y1, u1, v1p = split_planes(np.frombuffer(fullb, np.uint8))
        return y0, u0, v0p, ym, um, vm, y1, u1, v1p

    def blend_of(v0b: bytes, fullb: bytes) -> bytes:
        return (((np.frombuffer(v0b, np.uint8).astype(np.uint16)
                  + np.frombuffer(fullb, np.uint8).astype(np.uint16)) // 2)
                .astype(np.uint8).tobytes())

    # ---- Model 0: M15 frame + M16 shape 0 ----
    print("== model 0 (baseline recompute) ==")
    v0 = load_dump(m15d / "m15-v0.bin")
    mid = load_dump(m15d / "m15-mid.bin")
    full = load_dump(m15d / "m15-full.bin")
    m15 = triplet(v0, mid, full)
    b15 = blend_of(v0, full)
    r15_0 = residual_row(split_planes(np.frombuffer(b15, np.uint8))[0],
                         m15[3], b15, mid)
    print(f"m15 baseline: R_0={r15_0['xd']} xdmax={r15_0['xm']} "
          f"xdmean={r15_0['xn']:.3f} respx={r15_0['respx']} "
          f"hist={r15_0['yhist']} bands={r15_0['bands']} fnv={r15_0['fnv']}")

    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    s0 = triplet(v0, mid, full)
    b0 = blend_of(v0, full)
    r0_0 = residual_row(split_planes(np.frombuffer(b0, np.uint8))[0],
                        s0[3], b0, mid)
    print(f"m16-s0 baseline: R_0={r0_0['xd']} xdmax={r0_0['xm']} "
          f"xdmean={r0_0['xn']:.3f} respx={r0_0['respx']} "
          f"hist={r0_0['yhist']} bands={r0_0['bands']} fnv={r0_0['fnv']}")

    # ---- Model G: M15 frame (timed single) ----
    print("== model G (global half-pixel) ==")
    t0 = time.time()
    g15 = model_g(m15[0], m15[1], m15[2], m15[6], m15[7], m15[8])
    t_g1 = time.time() - t0
    syn15g = join_planes(g15["sy"], g15["su"], g15["sv"]).tobytes()
    mid15b = load_dump(m15d / "m15-mid.bin")
    r15_g = residual_row(g15["sy"], m15[3], syn15g, mid15b)
    (workd / "m17-synth-G-m15.bin").write_bytes(syn15g)
    print(f"m15-G: {t_g1:.1f}s shift={g15['shift']} sad={g15['sad']:.0f} "
          f"sad00={g15['sad00']:.0f} nmoved={g15['nmoved']}")
    print(f"m15-G residual: R_G={r15_g['xd']} explained={r15_0['xd'] - r15_g['xd']} "
          f"xdmax={r15_g['xm']} xdmean={r15_g['xn']:.3f} respx={r15_g['respx']} "
          f"hist={r15_g['yhist']} bands={r15_g['bands']} fnv={r15_g['fnv']}")
    print("m15-G 5x5 masked SAD grid (rows dy, cols dx in "
          + str(list(HALF_GRID)) + "):")
    for dy in HALF_GRID:
        print(f"dy={dy:+.1f}: " + " ".join(f"{g15['sads'][(dx, dy)]:8.0f}"
                                           for dx in HALF_GRID))

    # ---- Model G: all 764 M16 shapes ----
    shapes = sorted(int(p.name[8:12]) for p in m16d.glob("m16-v0-s*.bin"))
    print(f"shapes: n={len(shapes)} 0..{max(shapes)}")
    loo_rs = parse_loo_shapes(m16d / "loo.txt")
    print(f"loo.txt parsed R_s rows: n={len(loo_rs)}")
    t1 = time.time()
    grows = {}
    for i, s in enumerate(shapes):
        v0 = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mid = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        full = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        y0, u0, v0p, ym, um, vm, y1, u1, v1p = triplet(v0, mid, full)
        g = model_g(y0, u0, v0p, y1, u1, v1p)
        synth = join_planes(g["sy"], g["su"], g["sv"]).tobytes()
        r = residual_row(g["sy"], ym, synth, mid)
        grows[s] = (g, r)
        if s == 0:
            (workd / "m17-synth-G-s0000.bin").write_bytes(synth)
            print("s0-G 5x5 masked SAD grid:")
            for dy in HALF_GRID:
                print(f"dy={dy:+.1f}: " + " ".join(
                    f"{g['sads'][(dx, dy)]:8.0f}" for dx in HALF_GRID))
        if (i + 1) % 200 == 0:
            print(f"  ... G {i + 1}/{len(shapes)}")
    t1 = time.time() - t1
    print(f"model-G pool wall: {t1:.1f}s for {len(shapes)} shapes (sequential)")
    dist = Counter(g["shift"] for g, _ in grows.values())
    print(f"G shift distribution (dx,dy): count = {dict(sorted(dist.items()))}")
    r0g = grows[0][1]["xd"]
    print(f"s0-G residual: R_G={r0g} explained={r0_0['xd'] - r0g} "
          f"(R_0={r0_0['xd']}) e_G={(r0_0['xd'] - r0g) / r0_0['xd']:.4f}")
    print(f"s0-G detail: shift={grows[0][0]['shift']} sad={grows[0][0]['sad']:.0f} "
          f"sad00={grows[0][0]['sad00']:.0f} respx={grows[0][1]['respx']} "
          f"hist={grows[0][1]['yhist']} bands={grows[0][1]['bands']} "
          f"fnv={grows[0][1]['fnv']}")
    print("| shape | G shift | nmoved | R_s(M16) | R_s^G | explained (R_s-R_s^G) |")
    print("| ---: | --- | ---: | ---: | ---: | ---: |")
    for s in sorted(grows):
        g, r = grows[s]
        rs = loo_rs.get(s, ("?", "?"))[1]
        exp = ("?" if rs == "?" else rs - r["xd"])
        print(f"| {s} | ({g['shift'][0]:+.1f},{g['shift'][1]:+.1f}) | "
              f"{g['nmoved']} | {rs} | {r['xd']} | {exp} |")

    # ---- Model B: shape 0 + M15 ----
    print("== model B (block matching B=16, +-4 + half refine) ==")
    t2 = time.time()
    b_s0 = model_b(*s0[:3], *s0[6:9])
    t_b1 = time.time() - t2
    syn0b = join_planes(b_s0["sy"], b_s0["su"], b_s0["sv"]).tobytes()
    mid0 = load_dump(m16d / "m16-mid-s0000.bin")
    r0_b = residual_row(b_s0["sy"], s0[3], syn0b, mid0)
    (workd / "m17-synth-B-s0000.bin").write_bytes(syn0b)
    vdist = Counter(b_s0["vecs"])
    print(f"s0-B: {t_b1:.1f}s moved_blocks={b_s0['moved_blocks']} "
          f"degen_blocks={b_s0['degen_blocks']} "
          f"est_sad00={b_s0['sad00']:.0f} est_sadbest={b_s0['sadbest']:.0f}")
    print(f"s0-B residual: R_B={r0_b['xd']} explained={r0_0['xd'] - r0_b['xd']} "
          f"(R_0={r0_0['xd']}) e_B={(r0_0['xd'] - r0_b['xd']) / r0_0['xd']:.4f}")
    print(f"s0-B detail: xdmax={r0_b['xm']} xdmean={r0_b['xn']:.3f} "
          f"respx={r0_b['respx']} hist={r0_b['yhist']} bands={r0_b['bands']} "
          f"fnv={r0_b['fnv']}")
    print(f"s0-B vector histogram (vx,vy): count = {dict(sorted(vdist.items()))}")
    mags = Counter(round(abs(vx) + abs(vy), 1) for vx, vy in b_s0["vecs"])
    print(f"s0-B |v|_1 histogram: {dict(sorted(mags.items()))}")

    t3 = time.time()
    b_15 = model_b(*m15[:3], *m15[6:9])
    t_b2 = time.time() - t3
    syn15b = join_planes(b_15["sy"], b_15["su"], b_15["sv"]).tobytes()
    mid15 = load_dump(m15d / "m15-mid.bin")
    r15_b = residual_row(b_15["sy"], m15[3], syn15b, mid15)
    (workd / "m17-synth-B-m15.bin").write_bytes(syn15b)
    vdist15 = Counter(b_15["vecs"])
    print(f"m15-B: {t_b2:.1f}s moved_blocks={b_15['moved_blocks']} "
          f"degen_blocks={b_15['degen_blocks']} "
          f"est_sad00={b_15['sad00']:.0f} est_sadbest={b_15['sadbest']:.0f}")
    print(f"m15-B residual: R_B={r15_b['xd']} explained={r15_0['xd'] - r15_b['xd']} "
          f"(R_0={r15_0['xd']}) e_B={(r15_0['xd'] - r15_b['xd']) / r15_0['xd']:.4f}")
    print(f"m15-B detail: xdmax={r15_b['xm']} xdmean={r15_b['xn']:.3f} "
          f"respx={r15_b['respx']} hist={r15_b['yhist']} bands={r15_b['bands']} "
          f"fnv={r15_b['fnv']}")
    print(f"m15-B vector histogram (vx,vy): count = {dict(sorted(vdist15.items()))}")

    # ---- determinism re-run receipt ----
    print("== determinism re-run (same inputs, second pass) ==")
    g0b = model_g(*s0[:3], *s0[6:9])
    syn0g2 = join_planes(g0b["sy"], g0b["su"], g0b["sv"]).tobytes()
    b0b = model_b(*s0[:3], *s0[6:9])
    syn0b2 = join_planes(b0b["sy"], b0b["su"], b0b["sv"]).tobytes()
    syn0g1 = (workd / "m17-synth-G-s0000.bin").read_bytes()
    syn0b1 = (workd / "m17-synth-B-s0000.bin").read_bytes()
    print(f"G s0 rerun: shift {grows[0][0]['shift']} vs {g0b['shift']} "
          f"fnv {fnv1a(syn0g1):016x} vs {fnv1a(syn0g2):016x} "
          f"identical={syn0g1 == syn0g2}")
    print(f"B s0 rerun: vecs identical={b0b['vecs'] == b_s0['vecs']} "
          f"fnv {fnv1a(syn0b1):016x} vs {fnv1a(syn0b2):016x} "
          f"identical={syn0b1 == syn0b2}")

    # ---- PNGs ----
    print("== PNGs ==")
    rgbm = yuv_to_rgb(s0[3], s0[4], s0[5])
    outs = []
    for name, syy in (("m17-diffmap-G.png", grows[0][0]["sy"]),
                      ("m17-diffmap-B.png", b_s0["sy"])):
        d = np.abs(syy.astype(np.int16) - s0[3].astype(np.int16))
        a = np.clip(d / 32.0, 0, 1)[..., None]
        over = ((1 - a) * rgbm.astype(np.float32)
                + a * np.array([255, 0, 0], np.float32)).astype(np.uint8)
        outs.append((name, over))
    nz = [(i, v) for i, v in enumerate(b_s0["vecs"]) if v != (0.0, 0.0)]
    if nz:
        base = (0.35 * rgbm.astype(np.float32)).astype(np.uint8)
        img = Image.fromarray(base)
        dr = ImageDraw.Draw(img)
        for i, (vx, vy) in nz:
            bx, by = (i % 40) * BLOCK + BLOCK // 2, (i // 40) * BLOCK + BLOCK // 2
            m = abs(vx) + abs(vy)
            col = (255, 255, 0) if m <= 0.5 else ((255, 165, 0) if m <= 2 else (255, 0, 0))
            dr.line([bx, by, bx + vx * 4, by + vy * 4], fill=col, width=2)
        outs.append(("m17-field-B.png", np.asarray(img)))
    else:
        print("field overlay skipped: all 1120 block vectors are (0,0)")
    total = 0
    for name, arr in outs:
        p = evidd / name
        Image.fromarray(arr).resize((320, 224), Image.BILINEAR).save(p)
        total += p.stat().st_size
        print(f"png {p}: {p.stat().st_size} B")
    print(f"png total: {total} B (budget 5242880)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("models: 0=blend-baseline G=global-halfpel B=block16")


if __name__ == "__main__":
    main()
