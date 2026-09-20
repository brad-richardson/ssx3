#!/usr/bin/env python3
"""M22 interior far-tail mechanism: locate + isolate the |d|>=8 bytes (offline).

Usage: m22.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text goes
to stdout (redirect to WORK_DIR/m22.txt); PNG tail map to WORK_DIR
(evidence copy iff discriminating, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: locate (tail vs bulk: plane split, band/edge/P1 joins, region
     components 4/8-conn)
  2: isolate (carrier cut + 764-shape tail persistence + d-shape join)
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
M20_TAIL = {"s0": 102, "m15": 134}
M20_TAIL_SUB = {"s0": (28, 74), "m15": (50, 84)}  # (8-15, 16+)
M20_TAIL_MAX = {"s0": 47, "m15": 48}
M19_NEGRATE = {"s0": 0.8093, "m15": 0.8019}  # P(d>0) on cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
M19_REMOVED = [4888, 1208, 649, 448, 248, 244, 191, 174, 190, 202]
M19_REMOVED_BANDS = [[3415, 1442, 31], [824, 384, 0], [186, 463, 0],
                     [0, 0, 448], [0, 0, 248], [0, 0, 244], [0, 0, 191],
                     [0, 0, 174], [0, 0, 190], [0, 187, 15]]
M19_701_INTERIOR = 367
M20_701_TAIL_OUT = 102  # all s0 tail outside the 701 mask
M18_P1_EDGES = {"s0": "0 1 2 2 4 6 8 12 18 29 176",
                "m15": "0 0 1 2 4 6 9 13 19 30 181"}
M20_RHO = {"s0": [19, 107, 168, 94, 84, 254, 237, 347, 1048, 117],
           "m15": [28, 77, 200, 111, 87, 287, 284, 436, 899, 130]}


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
    """Cell-7 membership (M19 id 7 verbatim) + delta = mid - blend."""
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


def tail_bulk_masks(mask: np.ndarray, delta: np.ndarray):
    """Split a cell-7 mask into tail (|d|>=8) and bulk (|d|<8)."""
    ad = np.abs(delta)
    tail = mask & (ad >= 8)
    bulk = mask & (ad < 8)
    return tail, bulk


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
    (M20 verbatim.)
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


def connected_components(sites: np.ndarray, conn8: bool):
    """Union-find components of a bool plane; returns sorted size list desc
    plus per-component member coords for components >= 5."""
    h, w = sites.shape
    ys, xs = np.nonzero(sites)
    n = len(ys)
    if n == 0:
        return [], []
    idx = np.full((h, w), -1, np.int32)
    idx[ys, xs] = np.arange(n, dtype=np.int32)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for k in range(n):
        r, c = int(ys[k]), int(xs[k])
        for dr, dc in ((-1, 0), (0, -1), (-1, -1), (-1, 1)):
            if dr == 0 and dc == 0:
                continue
            if not conn8 and dr != 0 and dc != 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and idx[rr, cc] != -1:
                union(k, int(idx[rr, cc]))
    sizes = {}
    members = {}
    for k in range(n):
        rk = find(k)
        sizes[rk] = sizes.get(rk, 0) + 1
        members.setdefault(rk, []).append((int(ys[k]), int(xs[k])))
    sz = sorted(sizes.values(), reverse=True)
    big = []
    for rk, mem in members.items():
        if len(mem) >= 5:
            rs = [p[0] for p in mem]
            cs = [p[1] for p in mem]
            big.append((len(mem), sum(rs) / len(rs), sum(cs) / len(cs),
                        min(rs), max(rs), min(cs), max(cs)))
    big.sort(reverse=True)
    return sz, big


def dist4(x):
    a = np.asarray(x, dtype=np.float64)
    return (float(a.min()), float(np.median(a)), float(a.mean()),
            float(a.max()))


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
    L.append(f"{tag} P(d>0)={float((d > 0).mean()):.4f} "
             f"(M19/M20 want {M19_NEGRATE[tag]})")
    tail, bulk = tail_bulk_masks(mask, delta)
    nt, nb = int(tail.sum()), int(bulk.sum())
    adt = np.abs(delta[tail]).astype(np.int16)
    n815 = int(((adt >= 8) & (adt < 16)).sum())
    n16p = int((adt >= 16).sum())
    L.append(f"{tag} tail n={nt} (M20 want {M20_TAIL[tag]}); "
             f"bulk n={nb} (want {M19_INTERIOR[tag] - M20_TAIL[tag]}); "
             f"tail 8-15={n815} 16+={n16p} "
             f"(want {M20_TAIL_SUB[tag][0]}+{M20_TAIL_SUB[tag][1]}); "
             f"tail max={int(adt.max()) if nt else 0} "
             f"(want {M20_TAIL_MAX[tag]})")
    if (nt != M20_TAIL[tag] or (n815, n16p) != M20_TAIL_SUB[tag]
            or int(adt.max()) != M20_TAIL_MAX[tag]):
        L.append(f"{tag} TAIL MISMATCH: STOP, tabled.")
        return L, None
    pl = plane_of_byte()
    plt, plb = pl[tail], pl[bulk]
    dt, db = delta[tail].astype(np.float64), delta[bulk].astype(np.float64)
    # plane split: tail vs bulk side by side
    for pid, nm in ((0, "Y"), (1, "U"), (2, "V")):
        tt = delta[tail][plt == pid]
        bb = delta[bulk][plb == pid]
        at = np.abs(tt)
        L.append(f"{tag} plane {nm} tail: n={len(tt)} "
                 f"share={len(tt) / nt:.4f} "
                 f"adhist={mag_hist(at) if len(tt) else [0, 0, 0, 0, 0]} "
                 f"range=[{int(tt.min()) if len(tt) else 0},"
                 f"{int(tt.max()) if len(tt) else 0}] "
                 f"mean={float(tt.mean()) if len(tt) else 0:.3f} "
                 f"amean={float(at.mean()) if len(tt) else 0:.3f}")
        ab = np.abs(bb)
        L.append(f"{tag} plane {nm} bulk: n={len(bb)} "
                 f"adhist={mag_hist(ab) if len(bb) else [0, 0, 0, 0, 0]} "
                 f"mean={float(bb.mean()) if len(bb) else 0:.3f} "
                 f"amean={float(ab.mean()) if len(bb) else 0:.3f}")
    # bands (M19 thirds verbatim): tail-Y + tail-raw + bulk-Y + bulk-raw
    im_yt, im_ut, im_vt = flat_to_planes(tail)
    im_yb, im_ub, im_vb = flat_to_planes(bulk)
    for bi, rows in enumerate(BAND_ROWS):
        L.append(f"{tag} band {bi} tailY={int(im_yt[rows].sum())} "
                 f"bulkY={int(im_yb[rows].sum())} "
                 f"tailRaw={int(tail.reshape(H, ROWB)[rows].sum())} "
                 f"bulkRaw={int(bulk.reshape(H, ROWB)[rows].sum())}")
    # edge distance: M20 BFS verbatim, source = STATIC (DESIGN.md)
    a = np.frombuffer(v0b, np.uint8)
    b = np.frombuffer(fullb, np.uint8)
    st_y, st_u, st_v = flat_to_planes((a == b))
    ey, eu, ev = flat_to_planes(delta)
    for pname, st, imt, imb, ee in (("Y", st_y, im_yt, im_yb, ey),
                                   ("U", st_u, im_ut, im_ub, eu),
                                   ("V", st_v, im_vt, im_vb, ev)):
        dist, dr, dc = bfs_edge(st)
        dst = dist[imt] if imt.sum() else np.array([], np.int32)
        dsb = dist[imb]
        ddt = ee[imt].astype(np.float64) if imt.sum() else np.array([])
        ddb = ee[imb].astype(np.float64)
        L.append(f"{tag} edge {pname} tail: dmin="
                 f"{int(dst.min()) if len(dst) else -1} "
                 f"dmax={int(dst.max()) if len(dst) else -1} "
                 f"n={len(dst)}; bulk: dmin={int(dsb.min())} "
                 f"dmax={int(dsb.max())} n={len(dsb)} (want dmin>=1)")
        for lo in (1, 2, 3, 4, 5):
            selt = dst == lo if lo < 5 else dst >= 5
            selb = dsb == lo if lo < 5 else dsb >= 5
            lab5 = f"d={lo}" if lo < 5 else "d=5+"
            L.append(f"{tag} edge {pname} {lab5} tail: n={int(selt.sum())} "
                     f"mean={float(ddt[selt].mean()) if selt.sum() else 0:.3f} "
                     f"amean={float(np.abs(ddt[selt]).mean()) if selt.sum() else 0:.3f} "
                     f"|| bulk: n={int(selb.sum())} "
                     f"mean={float(ddb[selb].mean()) if selb.sum() else 0:.3f} "
                     f"amean={float(np.abs(ddb[selb]).mean()) if selb.sum() else 0:.3f}")
        for nm2, imm in (("tail", imt), ("bulk", imb)):
            if imm.sum() == 0:
                L.append(f"{tag} edge {pname} {nm2} drxdc: n=0")
                continue
            rrs, ccs = dr[imm], dc[imm]
            dd = ee[imm].astype(np.float64)
            rb = np.clip(rrs, 0, 3)
            cb = np.clip(ccs, 0, 3)
            row = []
            for i in range(4):
                for j in range(4):
                    sel = (rb == i) & (cb == j)
                    row.append(f"({i},{j}):n={int(sel.sum())}"
                               f"/m={float(dd[sel].mean()) if sel.sum() else 0:.2f}")
            L.append(f"{tag} edge {pname} {nm2} drxdc: " + " ".join(row))
    # P1 decile join (M18 code verbatim; edges guarded)
    mag, qs, dec = p1_gradient(ym)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    L.append(f"{tag} P1 edges: {estrs} (m18.txt want {M18_P1_EDGES[tag]}) "
             f"match={estrs == M18_P1_EDGES[tag]}")
    for dci in range(10):
        selt = im_yt & (dec == dci)
        selb = im_yb & (dec == dci)
        ddt = ey[selt].astype(np.float64)
        ddb = ey[selb].astype(np.float64)
        L.append(f"{tag} P1dec Y {dci} tail: n={int(selt.sum())} "
                 f"mean={float(ddt.mean()) if selt.sum() else 0:.3f} "
                 f"amean={float(np.abs(ddt).mean()) if selt.sum() else 0:.3f} "
                 f"|| bulk: n={int(selb.sum())} "
                 f"mean={float(ddb.mean()) if selb.sum() else 0:.3f} "
                 f"amean={float(np.abs(ddb).mean()) if selb.sum() else 0:.3f}")
    dec_u = dec[:, 0::2]
    for pname, imt, imb in (("U", im_ut, im_ub), ("V", im_vt, im_vb)):
        rt = " ".join(f"{dci}:{int((imt & (dec_u == dci)).sum())}"
                      for dci in range(10))
        rb = " ".join(f"{dci}:{int((imb & (dec_u == dci)).sum())}"
                      for dci in range(10))
        L.append(f"{tag} P1dec {pname} tail n-by-dec: {rt}")
        L.append(f"{tag} P1dec {pname} bulk n-by-dec: {rb}")
    # region: connected components of tail sites per plane (4/8-conn)
    for pname, imt in (("Y", im_yt), ("U", im_ut), ("V", im_vt)):
        for nm2, c8 in (("4conn", False), ("8conn", True)):
            sz, big = connected_components(imt, c8)
            nb1 = sum(1 for s in sz if s == 1)
            nb2 = sum(1 for s in sz if s == 2)
            nb34 = sum(1 for s in sz if 3 <= s <= 4)
            nb58 = sum(1 for s in sz if 5 <= s <= 8)
            nb9 = sum(1 for s in sz if s >= 9)
            L.append(f"{tag} region {pname} {nm2}: comps={len(sz)} "
                     f"sizes[1/2/3-4/5-8/9+]={nb1}/{nb2}/{nb34}/{nb58}/{nb9} "
                     f"largest={sz[0] if sz else 0} "
                     f"share={sz[0] / nt if sz else 0:.4f} "
                     f"(of tail n={nt})")
            L.append(f"{tag} region {pname} {nm2} sizelist: "
                     + (" ".join(map(str, sz)) if sz else "(empty)"))
            for (s, cr, cc, r0, r1, c0, c1) in big:
                L.append(f"{tag} region {pname} {nm2} comp5+: "
                         f"size={s} centroid=({cr:.1f},{cc:.1f}) "
                         f"bbox=r[{r0},{r1}]c[{c0},{c1}]")
    art = {"n": n, "nt": nt, "nb": nb, "mask": mask, "delta": delta,
           "tail": tail, "bulk": bulk, "im_yt": im_yt, "im_yb": im_yb,
           "ey": ey, "dec": dec}
    return L, art


def shape_join_lines(tag, v0b, midb, fullb, art):
    """Task 2.3: gap + rho + sign joint on tail vs bulk."""
    L = []
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    gap = np.abs(a - b).astype(np.float64)
    d = art["delta"].astype(np.float64)
    sgn_d = np.sign(a - b)
    sgn_o = np.sign(art["delta"])
    for nm, sel in (("tail", art["tail"]), ("bulk", art["bulk"])):
        g = gap[sel]
        dd = d[sel]
        rho = dd / g
        gmin, gmed, gmean, gmax = dist4(g)
        L.append(f"{tag} gap {nm}: min/med/mean/max="
                 f"{gmin:.0f}/{gmed:.0f}/{gmean:.1f}/{gmax:.0f} n={len(g)}")
        bins = [(2, 3), (4, 7), (8, 15), (16, 31), (32, 63), (64, 1 << 15)]
        row = " ".join(f"{lo}-{hi if hi < 999 else '+'}:"
                       f"{int(((g >= lo) & (g <= hi)).sum())}"
                       for lo, hi in bins)
        L.append(f"{tag} gap {nm} hist: {row}")
        L.append(f"{tag} rho {nm}: maxabs={float(np.abs(rho).max()):.4f} "
                 f"(want <0.5) meanabs={float(np.abs(rho).mean()):.4f}")
        edges = np.arange(-0.5, 0.5001, 0.1)
        hist, _ = np.histogram(rho, bins=edges)
        want = ""
        if nm == "bulk":
            want = f" (M20-all want {' '.join(map(str, M20_RHO[tag]))} net of tail)"
        L.append(f"{tag} rhohist {nm} bins[-0.5..0.5/0.1]: "
                 + " ".join(map(str, hist)) + want)
        c11 = int(((sgn_d[sel] == 1) & (sgn_o[sel] == 1)).sum())
        c1m = int(((sgn_d[sel] == 1) & (sgn_o[sel] == -1)).sum())
        cm1 = int(((sgn_d[sel] == -1) & (sgn_o[sel] == 1)).sum())
        cmm = int(((sgn_d[sel] == -1) & (sgn_o[sel] == -1)).sum())
        L.append(f"{tag} joint {nm} d>0/o>0={c11} d>0/o<0={c1m} "
                 f"d<0/o>0={cm1} d<0/o<0={cmm} "
                 f"P(o>0)={float((dd > 0).mean()):.4f}")
    return L


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    inter = int((a & b).sum())
    union = int((a | b).sum())
    if union == 0:
        return 1.0  # both empty: identical (tabled, see receipt)
    return inter / union


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0)

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin", m15d / "m15-v0.bin",
              m15d / "m15-mid.bin", m15d / "m15-full.bin"]
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")

    print("== loo.txt + top-10 carriers ==")
    loo = parse_loo(m16d / "loo.txt")
    print(f"loo.txt parsed R_s rows: n={len(loo)} (want 764)")
    shares = {s: (R0_M16 - rs) for s, (_, rs) in loo.items() if s != 0}
    top10 = sorted(shares, key=lambda s: -shares[s])[:10]
    print(f"derived top-10 shapes: {top10}")
    print(f"derived shares: {[shares[s] for s in top10]}")
    carriers_ok = (top10 == M16_TOP10
                   and [shares[s] for s in top10] == M16_TOP10_SHARES
                   and len(loo) == 764)
    print("carrier cross-check vs M16 REPORT: "
          + ("OK" if carriers_ok else "MISMATCH: STOP per-carrier, tabled"))

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
        print("MISMATCH vs M17-M21 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== Task 1: locate s0 ==")
    t1 = time.time()
    L0, art0 = task1_lines("s0", v0, mid, full, b0, ym0)
    for ln in L0:
        print(ln)
        canon.append(ln)
    print(f"(Task-1 s0 wall: {time.time() - t1:.1f}s)")
    if art0 is None:
        print("cell-7/tail guard failed on s0: STOP before Task 1.1.")
        return
    print("== Task 1: locate m15 ==")
    t1 = time.time()
    L15, art15 = task1_lines("m15", v015, mid15, full15, b15, ym15)
    for ln in L15:
        print(ln)
    print(f"(Task-1 m15 wall: {time.time() - t1:.1f}s)")
    if art15 is None:
        print("cell-7/tail guard failed on m15: STOP before Task 1.1.")
        return

    T0 = art0["tail"]
    T15 = art15["tail"]
    pl = plane_of_byte()

    # ---- Task 2.2: 764-shape tail-map pass (M21 Task-1.1 verbatim) ----
    print("== Task 2.2: coarse tail pass: all M16 shapes ==")
    shapes = sorted(int(p.name[8:12]) for p in m16d.glob("m16-v0-s*.bin"))
    print(f"shapes: n={len(shapes)} 0..{max(shapes)}")
    t1 = time.time()
    mism = 0
    occ = np.zeros(N, np.int32)
    counts, j0, j15 = [], [], []
    nempty = 0
    print("| shape | R_s | R_loo | tail | Y | U | V | jacc_s0 | jacc_m15 |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for i, s in enumerate(shapes):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        xd, _, _ = xdiff(bl, mm)
        rs = loo.get(s, ("?", "?"))[1]
        if xd != rs:
            mism += 1
        sp = interior_sites(vv, mm, ff, bl)
        tk, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        occ += tk
        plm = pl[tk]
        ny, nu, nv = (int((plm == p).sum()) for p in (0, 1, 2))
        jj0 = jaccard(tk, T0)
        jj15 = jaccard(tk, T15)
        if int(tk.sum()) == 0:
            nempty += 1
        counts.append(int(tk.sum()))
        j0.append(jj0)
        j15.append(jj15)
        print(f"| {s} | {xd} | {rs} | {int(tk.sum())} | {ny} | {nu} | {nv} | "
              f"{jj0:.4f} | {jj15:.4f} |")
        if (i + 1) % 200 == 0:
            print(f"  ... tailmap {i + 1}/{len(shapes)}")
    print(f"coarse-pass wall: {time.time() - t1:.1f}s for {len(shapes)} shapes")
    print(f"R_s vs loo.txt mismatches: {mism} (want 0)")
    print(f"empty tail maps: {nempty} (Jaccard 1.0 iff both empty, else 0.0)")
    cmin, cmed, cmean, cmax = dist4(counts)
    print(f"tail-count dist: min={cmin:.0f} med={cmed:.0f} mean={cmean:.1f} "
          f"max={cmax:.0f}")
    print(f"jacc(Tt,Ts0) all764: min/med/mean/max="
          f"{'/'.join(f'{v:.4f}' for v in dist4(j0))} (t=0 reads 1.0)")
    print(f"jacc(Tt,Ts0) t!=0: min/med/mean/max="
          f"{'/'.join(f'{v:.4f}' for v in dist4(j0[1:]))}")
    print(f"jacc(Tt,Tm15): min/med/mean/max="
          f"{'/'.join(f'{v:.4f}' for v in dist4(j15))}")
    jself = jaccard(T0, T15)
    print(f"jacc(Ts0,Tm15)={jself:.4f} inter={int((T0 & T15).sum())} "
          f"union={int((T0 | T15).sum())}")
    bins = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 63), (64, 763),
            (764, 764)]
    row = []
    for lo, hi in bins:
        row.append(f"{lo}-{hi}:{int(((occ >= lo) & (occ <= hi)).sum())}")
    print("persistence all-offsets occ-hist: " + " ".join(row))
    print(f"persistence maxocc={int(occ.max())} "
          f"n_at_max={int((occ == occ.max()).sum())}")
    for nm, mm in (("Ts0", T0), ("Tm15", T15)):
        oo = occ[mm]
        row = []
        for lo, hi in bins:
            row.append(f"{lo}-{hi}:{int(((oo >= lo) & (oo <= hi)).sum())}")
        print(f"persistence {nm}-sites occ-hist: " + " ".join(row))
        print(f"persistence {nm}-sites meanocc={float(oo.mean()):.1f} "
              f"ge50pct={int((oo >= 382).sum())} universal={int((oo == 764).sum())}")

    # ---- Task 2.1: carrier cut + 701 split ----
    print("== Task 2.1: carrier cut (tail bytes in removed masks) ==")
    if not carriers_ok:
        print("per-carrier work skipped (carrier mismatch, tabled above).")
    else:
        sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
        res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
        im_yt0 = art0["im_yt"]
        _, im_ut0, im_vt0 = flat_to_planes(T0)
        im_yb0 = art0["im_yb"]
        masks = {}
        for rank, s in enumerate(top10, 1):
            vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
            mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
            ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
            bl = synth_w_bytes(vv, ff, 0.5)
            yb = split_planes(np.frombuffer(bl, np.uint8))[0]
            yms = split_planes(np.frombuffer(mm, np.uint8))[0]
            ress = yb.astype(np.int16) != yms.astype(np.int16)
            removed = res0 & ~ress
            masks[s] = removed
            nrem = int(removed.sum())
            bd = bands_of(removed.astype(np.int64))
            yin = int(im_yt0[removed].sum())
            rm_u = removed[:, 0::2]
            uin = int((im_ut0 & rm_u).sum())
            vin = int((im_vt0 & rm_u).sum())
            ny_t = int(im_yt0.sum())
            print(f"rank {rank} shape {s}: removedYpx={nrem} "
                  f"(want {M19_REMOVED[rank - 1]}) bands={bd} "
                  f"(want {M19_REMOVED_BANDS[rank - 1]}) s0tailY_in={yin} "
                  f"share={yin / ny_t if ny_t else 0:.4f} s0tailU_in={uin} "
                  f"s0tailV_in={vin}")
        print("== Task 2.1: inside/outside-701 split (tail vs bulk) ==")
        removed701 = masks[701]
        nrem = int(removed701.sum())
        print(f"701 removed Y px={nrem} (M18 want 649)")
        im_y_all = flat_to_planes(art0["mask"])[0]
        print(f"701 interior-in-mask Y={int((im_y_all & removed701).sum())} "
              f"(M19 want {M19_701_INTERIOR})")
        ey0 = art0["ey"].astype(np.float64)
        for nm, imm in (("tail", im_yt0), ("bulk", im_yb0)):
            inside = imm & removed701
            outside = imm & ~removed701
            for nm2, sel in (("inside", inside), ("outside", outside)):
                dd = ey0[sel]
                L_ = (f"701 {nm} {nm2}: n={int(sel.sum())} "
                      f"mean={float(dd.mean()) if sel.sum() else 0:.3f} "
                      f"amean={float(np.abs(dd).mean()) if sel.sum() else 0:.3f} "
                      f"pos={int((dd > 0).sum())} neg={int((dd < 0).sum())}")
                if nm == "tail" and nm2 == "outside":
                    L_ += f" (M20 want tail-out={M20_701_TAIL_OUT})"
                print(L_)
                if sel.sum():
                    vals, cnts = np.unique(dd.astype(np.int16),
                                           return_counts=True)
                    print(f"701 {nm} {nm2} dhist: "
                          + " ".join(f"{int(v)}:{int(c)}"
                                     for v, c in zip(vals, cnts)))

    # ---- Task 2.3: d-shape join ----
    print("== Task 2.3: d-shape join s0 ==")
    for ln in shape_join_lines("s0", v0, mid, full, art0):
        print(ln)
    print("== Task 2.3: d-shape join m15 ==")
    for ln in shape_join_lines("m15", v015, mid15, full15, art15):
        print(ln)

    # ---- determinism re-run (Task 1 on s0, canonical text) ----
    print("== determinism re-run (Task 1 on s0, second pass) ==")
    L0b, art0b = task1_lines("s0", v0, mid, full, b0, ym0)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0b is not None and art0['n'] == art0b['n']}"
          f" tail counts identical="
          f"{art0b is not None and art0['nt'] == art0b['nt']}")

    # ---- PNG tail map (work dir; evidence copy iff discriminating) ----
    print("== PNG tail map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    ddy = art0["ey"]
    imy_b = art0["im_yb"]
    imy_t = art0["im_yt"]
    over[imy_b & (ddy > 0)] = np.array([255, 0, 0])       # bulk+ red
    over[imy_b & (ddy < 0)] = np.array([0, 128, 255])     # bulk- blue
    over[imy_t & (ddy > 0)] = np.array([255, 255, 0])     # tail+ yellow
    over[imy_t & (ddy < 0)] = np.array([255, 0, 255])     # tail- magenta
    p = workd / "m22-tailmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: red=bulk d>0 blue=bulk d<0 yellow=tail d>0 "
          "magenta=tail d<0 (interior Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=locate-tail T2=isolate-tail R=controls")


if __name__ == "__main__":
    main()
