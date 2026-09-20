#!/usr/bin/env python3
"""M20 interior-cell mechanism: mid-vs-blend offsets + filter-tap fits (offline).

Usage: m20.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text goes
to stdout (redirect to WORK_DIR/m20.txt); PNG delta map (if
discriminating) to EVID_DIR, else work dir only.

Tasks (see DESIGN.md, recorded before running):
  1: offset distribution (delta hist + plane split + edge distance +
     P1 decile join + sign joint + ratio dist)
  2: filter-tap fits (fixed stencil list + parity + 701 carrier cut)
  3: controls (control.py) + determinism + shas + Model-0 recompute
Tables, no verdicts.
"""
import hashlib
import re
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 640, 448
N = W * H * 2  # YUYV bytes
ROWB = W * 2
R0_M16, R0_M15 = 22815, 13418
FNV_S0, FNV_M15 = "6b9ffda25bd76c6f", "306b5c778898b64a"
M19_INTERIOR = {"s0": 2475, "m15": 2539}
M18_P1_EDGES = {"s0": "0 1 2 2 4 6 8 12 18 29 176",
                "m15": "0 0 1 2 4 6 9 13 19 30 181"}
M18_701_NREM = 649
M19_701_INTERIOR = 367
M16_701_SHARE = 1126


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


def flat_to_planes(x: np.ndarray):
    """Scatter a flat (N,) array to (Y, U, V) planes (same geometry)."""
    r = x.reshape(H, ROWB)
    y = np.empty((H, W), x.dtype)
    y[:, 0::2] = r[:, 0::4]
    y[:, 1::2] = r[:, 2::4]
    return y, r[:, 1::4].copy(), r[:, 3::4].copy()


def yuv_to_rgb(y: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    uu = np.repeat(u.astype(np.float32), 2, axis=1)
    vv = np.repeat(v.astype(np.float32), 2, axis=1)
    yy = y.astype(np.float32)
    r = yy + 1.402 * (vv - 128)
    g = yy - 0.344136 * (uu - 128) - 0.714136 * (vv - 128)
    b = yy + 1.772 * (uu - 128)
    return np.clip(np.stack([r, g, b], -1), 0, 255).astype(np.uint8)


def xdiff(a: bytes, b: bytes):
    aa = np.frombuffer(a, np.uint8).astype(np.int16)
    bb = np.frombuffer(b, np.uint8).astype(np.int16)
    d = np.abs(aa - bb)
    nz = d[d > 0]
    if len(nz) == 0:
        return 0, 0, 0.0
    return int(len(nz)), int(nz.max()), float(nz.mean())


def mag_hist(d: np.ndarray):
    nz = d[d > 0]
    return [int(((nz >= lo) & (nz < hi)).sum())
            for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 1 << 15))]


BAND_ROWS = np.array_split(np.arange(H), 3)


def bands_of(f: np.ndarray):
    return [int(f[b].sum()) for b in BAND_ROWS]


def synth_w_bytes(v0b: bytes, fullb: bytes, w: float) -> bytes:
    # M18 verbatim: full + floor(w*(v0-full)); at w=0.5 == (v0+full)//2.
    a = np.frombuffer(v0b, np.uint8).astype(np.float64)
    b = np.frombuffer(fullb, np.uint8).astype(np.float64)
    return np.clip(b + np.floor(w * (a - b)), 0, 255).astype(np.uint8).tobytes()


def interior_sites(v0b: bytes, midb: bytes, fullb: bytes, synth: bytes):
    """Cell-7 membership (M19 id 7 verbatim) + delta = mid - blend.

    Returns dict with mask (bool [N]), delta (int16 [N]), n.
    """
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    res = s != m
    moved = a != b
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    mask = res & moved & (m > lo) & (m < hi)
    return {"mask": mask, "delta": (m - s).astype(np.int16),
            "n": int(mask.sum())}


def plane_of_byte():
    """Flat (N,) plane ids: 0=Y, 1=U, 2=V."""
    t = np.arange(N) % 4
    return np.where((t == 0) | (t == 2), 0, np.where(t == 1, 1, 2))


def plane_coords():
    """Flat (N,) plane-native (row, col) coords: Y (H,W), U/V (H,W/2)."""
    o = np.arange(N)
    r = (o // ROWB).astype(np.int32)
    t = o % ROWB
    g = t // 4
    c = np.where((t % 4 == 0) | (t % 4 == 2),
                 (2 * g + (t % 4 == 2)).astype(np.int32),
                 g.astype(np.int32))
    return r, c


def bfs_edge(static: np.ndarray):
    """Manhattan distance to nearest static site + (dr,dc) components.

    static: bool (h,w), True = static (v0==full). Exact BFS with
    nearest-source tracking. Returns (dist, dr, dc) int32.
    """
    h, w = static.shape
    dist = np.full((h, w), -1, np.int32)
    sr = np.full((h, w), -1, np.int32)
    sc = np.full((h, w), -1, np.int32)
    ys, xs = np.nonzero(static)
    dist[ys, xs] = 0
    sr[ys, xs] = ys
    sc[ys, xs] = xs
    q = deque(zip(ys.tolist(), xs.tolist()))
    while q:
        r, c = q.popleft()
        nd = int(dist[r, c]) + 1
        orr, occ = int(sr[r, c]), int(sc[r, c])
        if r > 0 and dist[r - 1, c] == -1:
            dist[r - 1, c] = nd
            sr[r - 1, c] = orr
            sc[r - 1, c] = occ
            q.append((r - 1, c))
        if r + 1 < h and dist[r + 1, c] == -1:
            dist[r + 1, c] = nd
            sr[r + 1, c] = orr
            sc[r + 1, c] = occ
            q.append((r + 1, c))
        if c > 0 and dist[r, c - 1] == -1:
            dist[r, c - 1] = nd
            sr[r, c - 1] = orr
            sc[r, c - 1] = occ
            q.append((r, c - 1))
        if c + 1 < w and dist[r, c + 1] == -1:
            dist[r, c + 1] = nd
            sr[r, c + 1] = orr
            sc[r, c + 1] = occ
            q.append((r, c + 1))
    rr = np.arange(h, dtype=np.int32)[:, None]
    cc = np.arange(w, dtype=np.int32)[None, :]
    return dist, np.abs(rr - sr).astype(np.int32), np.abs(cc - sc).astype(np.int32)


def p1_gradient(ym: np.ndarray):
    """M18 grad_tables P1 block verbatim: mag + quantile edges + deciles."""
    yp = np.pad(ym.astype(np.int16), 1, mode="edge")
    gx = (yp[1:-1, 2:] - yp[1:-1, :-2]) // 2
    gy = (yp[2:, 1:-1] - yp[:-2, 1:-1]) // 2
    mag = np.abs(gx) + np.abs(gy)
    qs = np.quantile(mag, np.linspace(0, 1, 11))
    dec = np.clip(np.digitize(mag, qs[1:-1], right=True), 0, 9)
    return mag, qs, dec


def parse_loo(path: Path):
    out = {}
    pat = re.compile(r"^\|\s*(\d+)\s*\|\s*\([^)]*\)\s*\|\s*(\d+)\s*\|\s*(\d+)")
    for line in path.read_text(errors="replace").splitlines():
        m = pat.match(line)
        if m:
            out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return out


def stencil_hits(P: np.ndarray, M: np.ndarray, I: np.ndarray, sid: str):
    """Hit counts for one stencil on one plane (both roundings).

    P: source plane int16, M: mid plane int16, I: interior bool mask.
    Returns {rounding: (hits, n)} with border taps excluded.
    """
    h, w = P.shape
    out = {}
    if sid == "h2":
        num = P[:, :-1] + P[:, 1:]
        ok = np.zeros_like(I)
        ok[:, :-1] = I[:, :-1]
        out["floor"] = (num // 2, ok, (slice(None), slice(0, w - 1)))
        out["halfup"] = ((num + 1) // 2, ok, (slice(None), slice(0, w - 1)))
    elif sid == "v2":
        num = P[:-1, :] + P[1:, :]
        ok = np.zeros_like(I)
        ok[:-1, :] = I[:-1, :]
        out["floor"] = (num // 2, ok, (slice(0, h - 1), slice(None)))
        out["halfup"] = ((num + 1) // 2, ok, (slice(0, h - 1), slice(None)))
    elif sid == "b22":
        num = P[:-1, :-1] + P[:-1, 1:] + P[1:, :-1] + P[1:, 1:]
        ok = np.zeros_like(I)
        ok[:-1, :-1] = I[:-1, :-1]
        out["floor"] = (num // 4, ok, (slice(0, h - 1), slice(0, w - 1)))
        out["halfup"] = ((num + 2) // 4, ok, (slice(0, h - 1), slice(0, w - 1)))
    elif sid == "h3":
        num = P[:, :-2] + 2 * P[:, 1:-1] + P[:, 2:]
        ok = np.zeros_like(I)
        ok[:, 1:-1] = I[:, 1:-1]
        out["floor"] = (num // 4, ok, (slice(None), slice(1, w - 1)))
        out["halfup"] = ((num + 2) // 4, ok, (slice(None), slice(1, w - 1)))
    elif sid == "h4":
        num = -P[:, :-3] + 9 * P[:, 1:-2] + 9 * P[:, 2:-1] - P[:, 3:]
        ok = np.zeros_like(I)
        ok[:, 1:-2] = I[:, 1:-2]
        out["floor"] = (num // 16, ok, (slice(None), slice(1, w - 2)))
        out["halfup"] = ((num + 8) // 16, ok, (slice(None), slice(1, w - 2)))
    else:
        raise ValueError(sid)
    res = {}
    for rnd, (pred, ok, sl) in out.items():
        tgt = M[sl]
        okc = ok[sl]
        hits = int(((pred == tgt) & okc).sum())
        res[rnd] = (hits, int(okc.sum()))
    return res


def task1_lines(tag, v0b, midb, fullb, synth, ym):
    """Canonical Task-1 receipt lines for one frame; returns (lines, art)."""
    L = []
    sp = interior_sites(v0b, midb, fullb, synth)
    mask, delta, n = sp["mask"], sp["delta"], sp["n"]
    L.append(f"{tag}: cell7 n={n} (M19 want {M19_INTERIOR[tag]})")
    if n != M19_INTERIOR[tag]:
        L.append(f"{tag} COUNT MISMATCH: STOP, tabled.")
        return L, None
    d = delta[mask]
    L.append(f"{tag} delta==0 count={int((d == 0).sum())} (want 0)")
    # 1. signed hist + |d| hist + plane split
    vals, counts = np.unique(d, return_counts=True)
    L.append(f"{tag} dhist range=[{int(vals.min())},{int(vals.max())}] "
             + " ".join(f"{int(v)}:{int(c)}" for v, c in zip(vals, counts)))
    ad = np.abs(d).astype(np.int16)
    L.append(f"{tag} adhist={mag_hist(ad)} max={int(ad.max())} "
             f"mean={float(ad.mean()):.3f} p1={float((ad == 1).mean()):.4f}")
    pl = plane_of_byte()[mask]
    for pid, nm in ((0, "Y"), (1, "U"), (2, "V")):
        dd = d[pl == pid]
        aa = np.abs(dd)
        L.append(f"{tag} plane {nm}: n={len(dd)} "
                 f"adhist={mag_hist(aa) if len(dd) else [0, 0, 0, 0, 0]} "
                 f"mean={float(dd.mean()) if len(dd) else 0:.3f} "
                 f"amean={float(aa.mean()) if len(dd) else 0:.3f}")
    dd = d[pl != 0]
    aa = np.abs(dd)
    L.append(f"{tag} plane U+V: n={len(dd)} mean={float(dd.mean()):.3f} "
             f"amean={float(aa.mean()):.3f}")
    # 2a. edge distance (BFS per plane) + (dr,dc) cross
    a = np.frombuffer(v0b, np.uint8)
    b = np.frombuffer(fullb, np.uint8)
    stat_y, stat_u, stat_v = flat_to_planes((a == b))
    im_y, im_u, im_v = flat_to_planes(mask)
    dy, _, _ = flat_to_planes(delta)
    du = flat_to_planes(delta)[1]
    dv = flat_to_planes(delta)[2]
    bins = [1, 2, 3, 4, 5]
    for pname, st, im, dd in (("Y", stat_y, im_y, dy),
                              ("U", stat_u, im_u, du),
                              ("V", stat_v, im_v, dv)):
        dist, dr, dc = bfs_edge(st)
        dd = dd[im].astype(np.float64)
        ds = dist[im]
        L.append(f"{tag} edge {pname}: dmin={int(ds.min())} "
                 f"dmax={int(ds.max())} (want dmin>=1)")
        for lo in bins:
            sel = ds == lo if lo < 5 else ds >= 5
            lab = f"d={lo}" if lo < 5 else "d=5+"
            L.append(f"{tag} edge {pname} {lab}: n={int(sel.sum())} "
                     f"meand={float(dd[sel].mean()) if sel.sum() else 0:.3f} "
                     f"sd={float(dd[sel].std()) if sel.sum() else 0:.3f} "
                     f"amean={float(np.abs(dd[sel]).mean()) if sel.sum() else 0:.3f}")
        # (dr,dc) component cross, bins {0,1,2,3+}
        rrs, ccs = dr[im], dc[im]
        rb = np.clip(rrs, 0, 3)
        cb = np.clip(ccs, 0, 3)
        row = []
        for i in range(4):
            for j in range(4):
                sel = (rb == i) & (cb == j)
                row.append(f"({i},{j}):n={int(sel.sum())}"
                           f"/m={float(dd[sel].mean()) if sel.sum() else 0:.2f}")
        L.append(f"{tag} edge {pname} drxdc: " + " ".join(row))
    # 2b. P1 decile join (M18 code verbatim; edges guarded)
    mag, qs, dec = p1_gradient(ym)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    L.append(f"{tag} P1 edges: {estrs} (m18.txt want {M18_P1_EDGES[tag]}) "
             f"match={estrs == M18_P1_EDGES[tag]}")
    for dci in range(10):
        sel = im_y & (dec == dci)
        dd = dy[sel].astype(np.float64)
        L.append(f"{tag} P1dec Y {dci}: n={int(sel.sum())} "
                 f"mean={float(dd.mean()) if sel.sum() else 0:.3f} "
                 f"sd={float(dd.std()) if sel.sum() else 0:.3f} "
                 f"amean={float(np.abs(dd).mean()) if sel.sum() else 0:.3f}")
    # secondary U/V join via co-located Y decile (r,2c)
    dec_u = dec[:, 0::2]
    for pname, im, dd in (("U", im_u, du), ("V", im_v, dv)):
        row = []
        for dci in range(10):
            sel = im & (dec_u == dci)
            row.append(f"{dci}:{int(sel.sum())}")
        L.append(f"{tag} P1dec {pname} n-by-dec: " + " ".join(row))
    # 3. sign joint + ratio dist
    ai = np.frombuffer(v0b, np.uint8).astype(np.int16)[mask]
    bi = np.frombuffer(fullb, np.uint8).astype(np.int16)[mask]
    sgn_d = np.sign(ai - bi)
    sgn_o = np.sign(d)
    cells = {(1, 1): 0, (1, -1): 0, (-1, 1): 0, (-1, -1): 0}
    for x, y in zip(sgn_d.tolist(), sgn_o.tolist()):
        cells[(x, y)] += 1
    L.append(f"{tag} joint d>0/o>0={cells[(1, 1)]} d>0/o<0={cells[(1, -1)]} "
             f"d<0/o>0={cells[(-1, 1)]} d<0/o<0={cells[(-1, -1)]} "
             f"(d=v0-full, o=delta)")
    L.append(f"{tag} joint P(o>0)={float((d > 0).mean()):.4f} "
             f"P(o<0)={float((d < 0).mean()):.4f} "
             f"P(o>0|d>0)={cells[(1, 1)] / (cells[(1, 1)] + cells[(1, -1)]):.4f} "
             f"P(o>0|d<0)={cells[(-1, 1)] / (cells[(-1, 1)] + cells[(-1, -1)]):.4f}")
    gap = np.abs(ai - bi).astype(np.float64)
    rho = d.astype(np.float64) / gap
    L.append(f"{tag} rho maxabs={float(np.abs(rho).max()):.4f} (want <0.5) "
             f"meanabs={float(np.abs(rho).mean()):.4f}")
    edges = np.arange(-0.5, 0.5001, 0.1)
    hist, _ = np.histogram(rho, bins=edges)
    L.append(f"{tag} rhohist bins[-0.5..0.5/0.1]: " + " ".join(map(str, hist)))
    art = {"n": n, "delta": d, "im_y": im_y, "dy": dy, "dec": dec,
           "mag": mag, "qs": qs}
    return L, art


def task2_lines(tag, v0b, midb, fullb, synth):
    """Task-2 receipt lines: stencils + parity (carrier cut is s0-only)."""
    L = []
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    sp = interior_sites(v0b, midb, fullb, synth)
    mask = sp["mask"]
    y0, u0, v0 = split_planes(np.frombuffer(v0b, np.uint8))
    ym, um, vm = split_planes(np.frombuffer(midb, np.uint8))
    y1, u1, v1 = split_planes(np.frombuffer(fullb, np.uint8))
    im_y, im_u, im_v = flat_to_planes(mask)
    planes = {"Y": (y0.astype(np.int16), ym.astype(np.int16),
                    y1.astype(np.int16), im_y),
              "U": (u0.astype(np.int16), um.astype(np.int16),
                    u1.astype(np.int16), im_u),
              "V": (v0.astype(np.int16), vm.astype(np.int16),
                    v1.astype(np.int16), im_v)}
    for sid in ("h2", "v2", "b22", "h3", "h4"):
        for src in ("v0", "full"):
            tot = {}
            for pname, (P0, M, P1, I) in planes.items():
                P = P0 if src == "v0" else P1
                hh = stencil_hits(P, M, I, sid)
                for rnd, (hits, nn) in hh.items():
                    t = tot.setdefault(rnd, [0, 0])
                    t[0] += hits
                    t[1] += nn
                    L.append(f"{tag} stencil {sid} {src} {rnd} {pname}: "
                             f"hits={hits} n={nn} "
                             f"rate={hits / nn if nn else 0:.4f}")
            for rnd, (hits, nn) in tot.items():
                L.append(f"{tag} stencil {sid} {src} {rnd} ALL: hits={hits} "
                         f"n={nn} rate={hits / nn if nn else 0:.4f}")
    # positional fit: (v0-full) parity + coordinate parity
    d = sp["delta"][mask].astype(np.float64)
    pard = ((a - b) & 1)[mask]
    for p in (0, 1):
        sel = pard == p
        L.append(f"{tag} parity dpar={p}: n={int(sel.sum())} "
                 f"mean={float(d[sel].mean()):.3f} "
                 f"sd={float(d[sel].std()):.3f} "
                 f"amean={float(np.abs(d[sel]).mean()):.3f}")
    pl = plane_of_byte()[mask]
    for pid, nm in ((0, "Y"), (1, "U"), (2, "V")):
        row = []
        for p in (0, 1):
            sel = (pl == pid) & (pard == p)
            row.append(f"par{p}:n={int(sel.sum())}"
                       f"/m={float(d[sel].mean()) if sel.sum() else 0:.2f}")
        L.append(f"{tag} parity {nm} " + " ".join(row))
    r, c = plane_coords()
    r, c = r[mask], c[mask]
    pc = (r & 1) * 2 + (c & 1)
    for q in range(4):
        sel = pc == q
        L.append(f"{tag} parity coord (r%2={q // 2},c%2={q % 2}): "
                 f"n={int(sel.sum())} "
                 f"mean={float(d[sel].mean()):.3f} "
                 f"sd={float(d[sel].std()):.3f} "
                 f"amean={float(np.abs(d[sel]).mean()):.3f}")
    for pid, nm in ((0, "Y"), (1, "U"), (2, "V")):
        row = []
        for q in range(4):
            sel = (pl == pid) & (pc == q)
            row.append(f"({q // 2},{q % 2}):n={int(sel.sum())}"
                       f"/m={float(d[sel].mean()) if sel.sum() else 0:.2f}")
        L.append(f"{tag} parity {nm} coord " + " ".join(row))
    return L


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0)

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin", m15d / "m15-v0.bin",
              m15d / "m15-mid.bin", m15d / "m15-full.bin",
              m16d / "m16-v0-s0701.bin", m16d / "m16-mid-s0701.bin",
              m16d / "m16-full-s0701.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")

    print("== loo.txt (shape-701 row only) ==")
    loo = parse_loo(m16d / "loo.txt")
    print(f"loo.txt parsed R_s rows: n={len(loo)} (want 764)")
    share701 = R0_M16 - loo[701][1] if 701 in loo else None
    print(f"shape-701 share: {share701} (want {M16_701_SHARE}) "
          f"ok={len(loo) == 764 and share701 == M16_701_SHARE}")

    print("== model 0 (baseline recompute) ==")
    v015 = load_dump(m15d / "m15-v0.bin")
    mid15 = load_dump(m15d / "m15-mid.bin")
    full15 = load_dump(m15d / "m15-full.bin")
    ym15 = split_planes(np.frombuffer(mid15, np.uint8))[0]
    b15 = synth_w_bytes(v015, full15, 0.5)
    r15 = xdiff(b15, mid15)[0]
    f15 = f"{fnv1a(b15):016x}"
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    ym0 = split_planes(np.frombuffer(mid, np.uint8))[0]
    b0 = synth_w_bytes(v0, full, 0.5)
    r0 = xdiff(b0, mid)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17/M18/M19 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== Task 1: offsets s0 ==")
    t1 = time.time()
    L0, art0 = task1_lines("s0", v0, mid, full, b0, ym0)
    for ln in L0:
        print(ln)
        canon.append(ln)
    print(f"(Task-1 s0 wall: {time.time() - t1:.1f}s)")
    if art0 is None:
        print("cell-7 count guard failed on s0: STOP before Task 2.")
        return
    print("== Task 1: offsets m15 ==")
    t1 = time.time()
    L15, art15 = task1_lines("m15", v015, mid15, full15, b15, ym15)
    for ln in L15:
        print(ln)
    print(f"(Task-1 m15 wall: {time.time() - t1:.1f}s)")
    if art15 is None:
        print("cell-7 count guard failed on m15: STOP before Task 2.")
        return

    print("== Task 2: stencils + parity s0 ==")
    for ln in task2_lines("s0", v0, mid, full, b0):
        print(ln)
    print("== Task 2: stencils + parity m15 ==")
    for ln in task2_lines("m15", v015, mid15, full15, b15):
        print(ln)

    # ---- carrier cut: 701 removed mask vs rest (s0 interior Y) ----
    print("== Task 2: carrier cut (701 mask, s0 interior Y) ==")
    vv = load_dump(m16d / "m16-v0-s0701.bin")
    mm = load_dump(m16d / "m16-mid-s0701.bin")
    ff = load_dump(m16d / "m16-full-s0701.bin")
    bl = synth_w_bytes(vv, ff, 0.5)
    yb = split_planes(np.frombuffer(bl, np.uint8))[0]
    yms = split_planes(np.frombuffer(mm, np.uint8))[0]
    sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
    res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
    ress = yb.astype(np.int16) != yms.astype(np.int16)
    removed = res0 & ~ress
    nrem = int(removed.sum())
    print(f"701 removed Y px={nrem} (M18 want {M18_701_NREM}) "
          f"bands={bands_of(removed.astype(np.int64))}")
    im_y = art0["im_y"]
    dy = art0["dy"].astype(np.float64)
    inside = im_y & removed
    outside = im_y & ~removed
    print(f"701 interior-in-mask Y={int(inside.sum())} "
          f"(M19 want {M19_701_INTERIOR})")
    for nm, sel in (("inside", inside), ("outside", outside)):
        dd = dy[sel]
        vals, counts = np.unique(dd.astype(np.int16), return_counts=True)
        print(f"701 {nm}: n={int(sel.sum())} mean={float(dd.mean()):.3f} "
              f"sd={float(dd.std()):.3f} amean={float(np.abs(dd).mean()):.3f} "
              f"pos={int((dd > 0).sum())} neg={int((dd < 0).sum())}")
        print(f"701 {nm} dhist: "
              + " ".join(f"{int(v)}:{int(c)}" for v, c in zip(vals, counts)))

    # ---- determinism re-run (Task 1 on s0, canonical text) ----
    print("== determinism re-run (Task 1 on s0, second pass) ==")
    L0b, art0b = task1_lines("s0", v0, mid, full, b0, ym0)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0b is not None and art0['n'] == art0b['n']}")

    # ---- PNG delta map (work dir; evidence copy iff discriminating) ----
    print("== PNG delta map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    ddy = art0["dy"]
    pos = im_y & (ddy > 0)
    neg = im_y & (ddy < 0)
    over[pos] = np.array([255, 0, 0])      # delta>0 red
    over[neg] = np.array([0, 128, 255])    # delta<0 blue
    big = np.abs(ddy) >= 4
    over[im_y & big & (ddy > 0)] = np.array([255, 255, 0])   # big+ yellow
    over[im_y & big & (ddy < 0)] = np.array([255, 0, 255])   # big- magenta
    p = workd / "m20-deltamap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: red=d>0 blue=d<0 yellow=d>=+4 magenta=d<=-4 "
          "(interior Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=offset-dist T2=stencil+parity+carrier R=controls")


if __name__ == "__main__":
    main()
