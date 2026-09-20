#!/usr/bin/env python3
"""M33 shape-9 full-set attribution: mid-frame cluster privates + missings (offline).

Usage: m33.py M16_DIR M15_DIR M29TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt (only s0 + s9 + m15 +
top-10 carriers are loaded), the M15 triplet (baseline guard
only), and m29.txt (shape-9 full-set counts to reproduce:
tail 117, priv 23, miss 8, shared 94, J 0.7520, outside-col
22/8 + (row,col) lists); raw XFB dumps, 573440 B = 640x448
YUYV. Read-only inputs; receipt text goes to stdout (redirect
to WORK_DIR/m33.txt); PNG cluster map to WORK_DIR (evidence
copy iff the DESIGN.md rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: cluster per-site tables (22 priv + 8 miss) + near-miss shares
  2: s0-anchored joins + displacement + 8-conn components + occupancy
  3: controls (control.py) + determinism + shas + Model-0 recompute
Tables, no verdicts.
"""
import hashlib
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 640, 448
N = W * H * 2  # YUYV bytes
ROWB = W * 2
R0_M16, R0_M15 = 22815, 13418
FNV_S0, FNV_M15 = "6b9ffda25bd76c6f", "306b5c778898b64a"
M19_INTERIOR = {"s0": 2475, "m15": 2539}
M20_TAIL_S0 = 102
M20_TAIL_S0_SUB = (28, 74)  # (8-15, 16+)
M20_TAIL_S0_MAX = 47
M19_POSRATE_S0 = 0.8093  # P(d>0) on s0 cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
M19_REMOVED = [4888, 1208, 649, 448, 248, 244, 191, 174, 190, 202]
M19_REMOVED_BANDS = [[3415, 1442, 31], [824, 384, 0], [186, 463, 0],
                     [0, 0, 448], [0, 0, 248], [0, 0, 244], [0, 0, 191],
                     [0, 0, 174], [0, 0, 190], [0, 187, 15]]
M18_P1_EDGE_S0 = "0 1 2 2 4 6 8 12 18 29 176"
M29_TAIL_9, M29_JACC_9 = 117, "0.7520"
M29_PRIV_9, M29_MISS_9, M29_SHARED_9 = 23, 8, 94
M29_CPRIV_N, M29_CMISS_N = 22, 8
M29_INCOL_RC = (266, 321)
S0_C321 = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
M29_CPRIV_SET = {(226, 351), (232, 327), (233, 327), (234, 337),
                 (235, 337), (239, 336), (239, 339), (240, 318),
                 (241, 318), (243, 318), (244, 316), (245, 315),
                 (245, 316), (246, 314), (248, 312), (252, 310),
                 (269, 313), (270, 313), (274, 322), (289, 315),
                 (290, 315), (305, 332)}
M29_CMISS_SET = {(266, 315), (269, 314), (273, 315), (288, 314),
                 (289, 314), (296, 311), (299, 312), (301, 312)}
NAMED_COLS = [257, 277, 296, 301, 321, 340, 341, 342, 343]


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


BAND_ROWS = np.array_split(np.arange(H), 3)


def bands_of(f: np.ndarray):
    return [int(f[b].sum()) for b in BAND_ROWS]


ROW_BAND = np.zeros(H, np.int32)
for _bi, _rows in enumerate(BAND_ROWS):
    ROW_BAND[_rows] = _bi


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


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    inter = int((a & b).sum())
    union = int((a | b).sum())
    if union == 0:
        return 1.0  # both empty: identical (tabled, see receipt)
    return inter / union


PNAME = ("Y", "U", "V")


def attrib_lines(tag, priv, miss, shared, dA, mA, dB, mB,
                 v0A, fullA, v0B, fullB):
    """Task 1.1/1.2: per-site private + missing rows with cross values.

    A = s0, B = other shape (9). priv = T_B - T_A (or the cluster
    subset), miss = T_A - T_B. Returns (lines, summary_dict).
    Offsets in ascending order. (M27 verbatim.)
    """
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    aA = np.frombuffer(v0A, np.uint8).astype(np.int16)
    bA = np.frombuffer(fullA, np.uint8).astype(np.int16)
    aB = np.frombuffer(v0B, np.uint8).astype(np.int16)
    bB = np.frombuffer(fullB, np.uint8).astype(np.int16)
    gA = aA - bA
    gB = aB - bB
    out = {}
    for nm, q, dQ, dO, mO, gQ, gO in (
            ("priv", priv, dB, dA, mA, gB, gA),
            ("miss", miss, dA, dB, mB, gA, gB)):
        idx = np.nonzero(q)[0]
        n_near = n_far = n_non = 0
        bulk_ads = []
        geq = ageq = 0
        for o in idx:
            o = int(o)
            adq = int(abs(int(dQ[o])))
            if mO[o]:
                ad = int(abs(int(dO[o])))
                assert ad < 8, f"{tag} {nm} o={o}: other-frame tail?!"
                st = "bulk"
                bulk_ads.append(ad)
                if ad in (6, 7):
                    n_near += 1
                else:
                    n_far += 1
                ado = str(ad)
            else:
                st = "noncell"
                n_non += 1
                ado = "n/a"
            if int(gQ[o]) == int(gO[o]):
                geq += 1
            if abs(int(gQ[o])) == abs(int(gO[o])):
                ageq += 1
            L.append(f"{tag} {nm} o={o} plane={PNAME[int(pl[o])]} "
                     f"rc=({int(pr[o])},{int(pc[o])}) adQ={adq} "
                     f"ostat={st} adO={ado} gQ={int(gQ[o])} gO={int(gO[o])}")
        n = len(idx)
        L.append(f"{tag} {nm} summary: n={n} near={n_near} "
                 f"({n_near / n if n else 0:.4f}) far={n_far} "
                 f"({n_far / n if n else 0:.4f}) noncell={n_non} "
                 f"({n_non / n if n else 0:.4f})")
        if bulk_ads:
            ba = np.array(bulk_ads, np.int16)
            vals, cnts = np.unique(ba, return_counts=True)
            L.append(f"{tag} {nm} bulk-adO values: "
                     + " ".join(f"{int(v)}:{int(c)}"
                                for v, c in zip(vals, cnts)))
        else:
            L.append(f"{tag} {nm} bulk-adO values: (none: all noncell)")
        L.append(f"{tag} {nm} gaps: signed-eq={geq}/{n} "
                 f"({geq / n if n else 0:.4f}) abs-eq={ageq}/{n} "
                 f"({ageq / n if n else 0:.4f})")
        out[nm] = {"n": n, "near": n_near, "far": n_far, "non": n_non}
    out["shared_n"] = int(shared.sum())
    return L, out


def posjoin_lines(tag, priv, miss, shared, dec_s0, masks):
    """Task 1.3: s0-anchored position joins (band/decile/streak/carrier).

    dec_s0: P1 deciles on s0 mid-Y. masks: {shape: removed-Y-bool}.
    Returns lines; sets compared side by side per level.
    (M27 verbatim.)
    """
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    dec_u = dec_s0[:, 0::2]
    sets = (("priv", priv), ("miss", miss), ("shared", shared))

    def band_of(o):
        return int(ROW_BAND[int(pr[o])])

    def dec_of(o):
        r, c = int(pr[o]), int(pc[o])
        if int(pl[o]) == 0:
            return int(dec_s0[r, c])
        return int(dec_u[r, c])  # co-located Y (r,2c): M22 verbatim

    def ycol_of(o):
        if int(pl[o]) == 0:
            return int(pc[o])
        return 2 * int(pc[o])  # co-located Y column

    # planes first (expect all-Y per M22's 0/764 tail-U/V pass)
    for nm, s in sets:
        pp = pl[s]
        L.append(f"{tag} posjoin plane {nm}: Y={int((pp == 0).sum())} "
                 f"U={int((pp == 1).sum())} V={int((pp == 2).sum())} "
                 f"n={int(s.sum())}")
    # band thirds (geometry: same for all frames)
    for bi in range(3):
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            n = sum(1 for o in idx if band_of(o) == bi)
            row.append(f"{nm}={n} ({n / int(s.sum()) if int(s.sum()) else 0:.4f})")
        L.append(f"{tag} posjoin band {bi}: " + " ".join(row))
    # gradient decile (s0-anchored P1)
    for dci in range(10):
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            n = sum(1 for o in idx if dec_of(o) == dci)
            row.append(f"{nm}={n}")
        L.append(f"{tag} posjoin dec {dci}: " + " ".join(row))
    for nm, s in sets:
        idx = np.nonzero(s)[0]
        n9 = sum(1 for o in idx if dec_of(o) == 9)
        L.append(f"{tag} posjoin dec9share {nm}: {n9}/{int(s.sum())} "
                 f"({n9 / int(s.sum()) if int(s.sum()) else 0:.4f})")
    # streak columns (Y-native; U/V via co-located 2c, own row)
    for c in NAMED_COLS + ["other"]:
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            if c == "other":
                n = sum(1 for o in idx if ycol_of(o) not in NAMED_COLS)
            else:
                n = sum(1 for o in idx if ycol_of(o) == c)
            row.append(f"{nm}={n}")
        L.append(f"{tag} posjoin streakcol {c}: " + " ".join(row))
    for nm, s in sets:
        idx = np.nonzero(s)[0]
        nuv = sum(1 for o in idx if int(pl[o]) != 0)
        L.append(f"{tag} posjoin streakcol nonY-co-located {nm}: {nuv}")
    # carrier masks (M22-verbatim removed = res0 & ~ress on Y)
    for rank, shape in enumerate(M16_TOP10, 1):
        rm = masks[shape]
        rm_u = rm[:, 0::2]
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            n = 0
            for o in idx:
                r, c = int(pr[o]), int(pc[o])
                inside = rm[r, c] if int(pl[o]) == 0 else rm_u[r, c]
                n += int(bool(inside))
            row.append(f"{nm}_in={n}")
        L.append(f"{tag} posjoin carrier rank{rank}/s{shape}: " + " ".join(row))
    # 701 split
    rm701 = masks[701]
    rm701_u = rm701[:, 0::2]
    for nm, s in sets:
        idx = np.nonzero(s)[0]
        nin = 0
        for o in idx:
            r, c = int(pr[o]), int(pc[o])
            inside = rm701[r, c] if int(pl[o]) == 0 else rm701_u[r, c]
            nin += int(bool(inside))
        L.append(f"{tag} posjoin 701split {nm}: in={nin} "
                 f"out={int(s.sum()) - nin} n={int(s.sum())}")
    return L


def displace_lines(tag, priv, miss, shared):
    """Task 2.1: nearest-shared-site Manhattan distance per private site
    (same plane, plane-native coords, brute-force exact). Missing mirror
    tabled the same way. Returns lines. (M27 verbatim.)
    """
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    for nm, q in (("priv", priv), ("miss", miss)):
        idx = np.nonzero(q)[0]
        dists = []
        for o in idx:
            o = int(o)
            p = int(pl[o])
            qs = np.nonzero(shared & (pl == p))[0]
            if len(qs) == 0:
                L.append(f"{tag} displace {nm} o={o} plane={PNAME[p]} "
                         f"rc=({int(pr[o])},{int(pc[o])}) dmin=n/a "
                         f"(no shared on plane)")
                continue
            d = int((np.abs(pr[qs].astype(np.int32) - int(pr[o]))
                     + np.abs(pc[qs].astype(np.int32) - int(pc[o]))).min())
            assert d >= 1, f"{tag} {nm} o={o}: dmin=0?!"
            dists.append(d)
            L.append(f"{tag} displace {nm} o={o} plane={PNAME[p]} "
                     f"rc=({int(pr[o])},{int(pc[o])}) dmin={d}")
        hist = {b: sum(1 for d in dists if (d == b if b < 5 else d >= 5))
                for b in (1, 2, 3, 4, 5)}
        n = len(dists)
        L.append(f"{tag} displace {nm} hist: "
                 + " ".join(f"{b if b < 5 else '5+'}:{hist[b]}" for b in hist)
                 + f" n={n} d1share={hist[1] / n if n else 0:.4f}")
    return L


def comp_lines(tag, tail, nt):
    """Task 2.2: 8-conn tail components on Y (M22 verbatim) + U/V counts."""
    L = []
    im_y, im_u, im_v = flat_to_planes(tail)
    sz, big = connected_components(im_y, True)
    nb1 = sum(1 for s in sz if s == 1)
    nb2 = sum(1 for s in sz if s == 2)
    nb34 = sum(1 for s in sz if 3 <= s <= 4)
    nb58 = sum(1 for s in sz if 5 <= s <= 8)
    nb9 = sum(1 for s in sz if s >= 9)
    L.append(f"{tag} comp8 Y: comps={len(sz)} "
             f"sizes[1/2/3-4/5-8/9+]={nb1}/{nb2}/{nb34}/{nb58}/{nb9} "
             f"largest={sz[0] if sz else 0} "
             f"share={sz[0] / nt if sz else 0:.4f} (of tail n={nt})")
    L.append(f"{tag} comp8 Y sizelist: "
             + (" ".join(map(str, sz)) if sz else "(empty)"))
    for (s, cr, cc, r0, r1, c0, c1) in big:
        L.append(f"{tag} comp8 Y comp5+: size={s} "
                 f"centroid=({cr:.1f},{cc:.1f}) bbox=r[{r0},{r1}]c[{c0},{c1}]")
    L.append(f"{tag} comp8 U: n={int(im_u.sum())} V: n={int(im_v.sum())} "
             f"(want 0/0 per M22's 764-shape pass)")
    return L


def off_of(r: int, c: int) -> int:
    """Flat byte offset of Y site (r, c). (M29 verbatim.)"""
    return r * ROWB + (c // 2) * 4 + (0 if c % 2 == 0 else 2)


def y_col_rows(mask: np.ndarray, c: int, pl, pr, pc):
    """Sorted Y-tail rows of mask in column c. (M29 verbatim.)"""
    idx = np.nonzero(mask & (pl == 0) & (pc == c))[0]
    return sorted(int(pr[o]) for o in idx)


def comp_labels(sites: np.ndarray):
    """8-conn union-find labeling (same neighbor set as
    connected_components); returns (label_plane, members) with
    labels 0..K-1 ordered by size desc."""
    h, w = sites.shape
    ys, xs = np.nonzero(sites)
    n = len(ys)
    lab = np.full((h, w), -1, np.int32)
    if n == 0:
        return lab, {}
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
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and idx[rr, cc] != -1:
                union(k, int(idx[rr, cc]))
    members = {}
    for k in range(n):
        members.setdefault(find(k), []).append((int(ys[k]), int(xs[k])))
    order = sorted(members, key=lambda rk: -len(members[rk]))
    for li, rk in enumerate(order):
        for (r, c) in members[rk]:
            lab[r, c] = li
    return lab, {li: members[rk] for li, rk in enumerate(order)}


def occupancy_lines(tag, tail, cpriv_rc, cmiss_rc=frozenset()):
    """Per-8-conn-comp cluster occupancy on a tail (or union) mask."""
    L = []
    im_y, _, _ = flat_to_planes(tail)
    _, members = comp_labels(im_y)
    cp, cm = set(cpriv_rc), set(cmiss_rc)
    best = 0
    for li in sorted(members):
        mem = members[li]
        ncp = sum(1 for rc in mem if rc in cp)
        ncm = sum(1 for rc in mem if rc in cm)
        best = max(best, ncp)
        rs = [p[0] for p in mem]
        cs = [p[1] for p in mem]
        L.append(f"{tag} comp li={li} size={len(mem)} cpriv={ncp} "
                 f"cmiss={ncm} bbox=r[{min(rs)},{max(rs)}]c[{min(cs)},{max(cs)}]")
    tot_cpriv = sum(1 for mem in members.values()
                    for rc in mem if rc in cp)
    tot_cmiss = sum(1 for mem in members.values()
                    for rc in mem if rc in cm)
    L.append(f"{tag} occupancy: comps={len(members)} "
             f"max-cpriv-in-one={best} cpriv-covered={tot_cpriv} "
             f"cmiss-covered={tot_cmiss}")
    return L, best


def dmin_list(q, shared, pl, pr, pc):
    """Nearest-shared-site Manhattan dmin per site of q (bar math)."""
    out = []
    for o in np.nonzero(q)[0]:
        o = int(o)
        p = int(pl[o])
        qs = np.nonzero(shared & (pl == p))[0]
        if len(qs) == 0:
            out.append(None)
            continue
        out.append(int((np.abs(pr[qs].astype(np.int32) - int(pr[o]))
                        + np.abs(pc[qs].astype(np.int32) - int(pc[o]))).min()))
    return out


def load_triplet(m16d: Path, s: int):
    vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
    mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
    ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
    return vv, mm, ff, synth_w_bytes(vv, ff, 0.5)


def compute_sets(v0, mid0, full0, b0, v9, mid9, full9, b9):
    """Cell-7 + tail + full/cluster sets for s0+9 (shared pass 1/2)."""
    sp0 = interior_sites(v0, mid0, full0, b0)
    sp9 = interior_sites(v9, mid9, full9, b9)
    mask0, d0 = sp0["mask"], sp0["delta"]
    mask9, d9 = sp9["mask"], sp9["delta"]
    t0, _ = tail_bulk_masks(mask0, d0)
    t9, _ = tail_bulk_masks(mask9, d9)
    priv = t9 & ~t0
    miss = t0 & ~t9
    shared = t9 & t0
    pl = plane_of_byte()
    pr, pc = plane_coords()
    incol = priv & (pl == 0) & (pc == 321)
    cpriv = priv & ~incol
    return {"sp0": sp0, "sp9": sp9, "mask0": mask0, "d0": d0,
            "mask9": mask9, "d9": d9, "t0": t0, "t9": t9,
            "priv": priv, "miss": miss, "shared": shared,
            "incol": incol, "cpriv": cpriv, "pl": pl, "pr": pr,
            "pc": pc}


def compute_dec_masks(m16d: Path, mid0: bytes, b0: bytes):
    """s0 P1 deciles + M22-verbatim carrier masks (shared pass 1/2)."""
    ym0 = split_planes(np.frombuffer(mid0, np.uint8))[0]
    _, qs, dec = p1_gradient(ym0)
    sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
    res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
    masks = {}
    checks = []
    for rank, s in enumerate(M16_TOP10, 1):
        vv, mm, ff, bl = load_triplet(m16d, s)
        yb = split_planes(np.frombuffer(bl, np.uint8))[0]
        yms = split_planes(np.frombuffer(mm, np.uint8))[0]
        ress = yb.astype(np.int16) != yms.astype(np.int16)
        removed = res0 & ~ress
        masks[s] = removed
        nrem = int(removed.sum())
        bd = bands_of(removed.astype(np.int64))
        checks.append((rank, s, nrem, bd,
                       nrem == M19_REMOVED[rank - 1]
                       and bd == M19_REMOVED_BANDS[rank - 1]))
    return dec, qs, masks, checks


def task1_lines(sets, v0, full0, v9, full9, dec, masks):
    """All Task-1 receipt lines (per-site full+cluster, both joins)."""
    L = []
    la_full, _ = attrib_lines("s9full", sets["priv"], sets["miss"],
                             sets["shared"], sets["d0"], sets["mask0"],
                             sets["d9"], sets["mask9"], v0, full0, v9,
                             full9)
    L += la_full
    la_clus, summ = attrib_lines("s9clus", sets["cpriv"], sets["miss"],
                                sets["shared"], sets["d0"], sets["mask0"],
                                sets["d9"], sets["mask9"], v0, full0, v9,
                                full9)
    L += la_clus
    L += posjoin_lines("s9full", sets["priv"], sets["miss"],
                       sets["shared"], dec, masks)
    L += posjoin_lines("s9clus", sets["cpriv"], sets["miss"],
                       sets["shared"], dec, masks)
    return L, summ


def parse_m29_targets(txt: str):
    """Shape-9 full-set match targets from m29.txt (or Nones)."""
    m_full = re.search(r"^s9 full sets: priv=(\d+) miss=(\d+) "
                       r"shared=(\d+) tail=(\d+) J=([\d.]+)", txt, re.M)
    m_p = re.search(r"^s9 outside-col priv: n=(\d+) rc=\[(.*)\]\s*$",
                    txt, re.M)
    m_m = re.search(r"^s9 outside-col miss: n=(\d+) rc=\[(.*)\]\s*$",
                    txt, re.M)

    def tupset(s):
        return {(int(a), int(b))
                for a, b in re.findall(r"\((\d+),\s*(\d+)\)", s)}
    if not (m_full and m_p and m_m):
        return None
    return {"priv": int(m_full.group(1)), "miss": int(m_full.group(2)),
            "shared": int(m_full.group(3)), "tail": int(m_full.group(4)),
            "j": m_full.group(5),
            "cpriv_n": int(m_p.group(1)), "cpriv_set": tupset(m_p.group(2)),
            "cmiss_n": int(m_m.group(1)), "cmiss_set": tupset(m_m.group(2))}


def main():
    m16d, m15d, m29t, workd, evidd = (Path(a) for a in sys.argv[1:6])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin",
              m16d / "m16-v0-s0009.bin", m16d / "m16-mid-s0009.bin",
              m16d / "m16-full-s0009.bin",
              m15d / "m15-v0.bin", m15d / "m15-mid.bin",
              m15d / "m15-full.bin"]
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    m29b = m29t.read_bytes()
    print(f"input {m29t}: bytes={len(m29b)} "
          f"sha256={hashlib.sha256(m29b).hexdigest()}")
    tgt = parse_m29_targets(m29b.decode(errors="replace"))
    if tgt is None:
        print("m29.txt TARGET ROWS NOT FOUND: STOP, tabled.")
        return
    print(f"m29.txt target s9: tail={tgt['tail']} J={tgt['j']} "
          f"priv={tgt['priv']} miss={tgt['miss']} shared={tgt['shared']} "
          f"cpriv_n={tgt['cpriv_n']} cmiss_n={tgt['cmiss_n']}")
    pin_ok = (tgt["cpriv_set"] == M29_CPRIV_SET
              and tgt["cmiss_set"] == M29_CMISS_SET
              and tgt["tail"] == M29_TAIL_9 and tgt["j"] == M29_JACC_9
              and tgt["priv"] == M29_PRIV_9 and tgt["miss"] == M29_MISS_9
              and tgt["shared"] == M29_SHARED_9)
    print(f"m29.txt targets vs DESIGN-pinned M29 wants: match={pin_ok}")
    if not pin_ok:
        print("m29.txt vs DESIGN TRANSCRIPTION MISMATCH: STOP, tabled.")
        return

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
          + ("OK" if carriers_ok else "MISMATCH: STOP, tabled"))

    print("== model 0 (baseline recompute) ==")
    v015 = load_dump(m15d / "m15-v0.bin")
    mid15 = load_dump(m15d / "m15-mid.bin")
    full15 = load_dump(m15d / "m15-full.bin")
    b15 = synth_w_bytes(v015, full15, 0.5)
    r15 = xdiff(b15, mid15)[0]
    f15 = f"{fnv1a(b15):016x}"
    v0, mid0, full0, b0 = load_triplet(m16d, 0)
    v9, mid9, full9, b9 = load_triplet(m16d, 9)
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M32 baselines: STOP, tabled.")
        return
    if not carriers_ok:
        print("carrier mismatch: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== R_s vs loo cross-check (s0/9) ==")
    for s, bl, mm in ((0, b0, mid0), (9, b9, mid9)):
        xd = xdiff(bl, mm)[0]
        rs = loo.get(s, ("?", "?"))[1]
        print(f"s{s}: R_s={xd} R_loo={rs} match={xd == rs}")
        if xd != rs:
            print(f"R_s mismatch on s{s}: STOP, tabled.")
            return
    print("R_s cross-check: OK")

    # ---- cell-7 + tail + full-set/cluster guards (match M29 or stop) ----
    print("== cell-7 + tail + M29 set guard (s0 + 9) ==")
    sets = compute_sets(v0, mid0, full0, b0, v9, mid9, full9, b9)
    mask0, d0 = sets["mask0"], sets["d0"]
    mask9, d9 = sets["mask9"], sets["d9"]
    t0, t9 = sets["t0"], sets["t9"]
    priv, miss, shared = sets["priv"], sets["miss"], sets["shared"]
    cpriv, incol = sets["cpriv"], sets["incol"]
    pl, pr, pc = sets["pl"], sets["pr"], sets["pc"]
    n0 = sets["sp0"]["n"]
    print(f"s0 cell7 n={n0} (want {M19_INTERIOR['s0']})")
    if n0 != M19_INTERIOR["s0"]:
        print("s0 COUNT MISMATCH: STOP, tabled.")
        return
    dd0 = d0[mask0]
    dd9 = d9[mask9]
    print(f"s0 delta==0 count={int((dd0 == 0).sum())} (want 0); "
          f"s9 delta==0 count={int((dd9 == 0).sum())} (want 0)")
    if int((dd0 == 0).sum()) != 0 or int((dd9 == 0).sum()) != 0:
        print("delta==0 MISMATCH: STOP, tabled.")
        return
    print(f"s0 P(d>0)={float((dd0 > 0).mean()):.4f} "
          f"(M19/M20 want {M19_POSRATE_S0})")
    if float(f"{float((dd0 > 0).mean()):.4f}") != M19_POSRATE_S0:
        print("s0 P(d>0) MISMATCH: STOP, tabled.")
        return
    nt0, nt9 = int(t0.sum()), int(t9.sum())
    ad0 = np.abs(d0[t0]).astype(np.int16)
    n815 = int(((ad0 >= 8) & (ad0 < 16)).sum())
    n16p = int((ad0 >= 16).sum())
    print(f"s0 tail n={nt0} (want {M20_TAIL_S0}); 8-15={n815} 16+={n16p} "
          f"(want {M20_TAIL_S0_SUB[0]}+{M20_TAIL_S0_SUB[1]}); "
          f"max={int(ad0.max())} (want {M20_TAIL_S0_MAX})")
    if (nt0 != M20_TAIL_S0 or (n815, n16p) != M20_TAIL_S0_SUB
            or int(ad0.max()) != M20_TAIL_S0_MAX):
        print("s0 TAIL MISMATCH: STOP, tabled.")
        return
    j9 = jaccard(t9, t0)
    npriv, nmiss, nshared = int(priv.sum()), int(miss.sum()), int(shared.sum())
    print(f"s9 tail n={nt9} (M29 want {tgt['tail']}); "
          f"J(T_9,T_s0)={j9:.4f} (M29 want {tgt['j']}); "
          f"inter={int((t9 & t0).sum())} union={int((t9 | t0).sum())}")
    print(f"s9 full sets: priv={npriv} (want {tgt['priv']}) "
          f"miss={nmiss} (want {tgt['miss']}) "
          f"shared={nshared} (want {tgt['shared']})")
    set_ok = (nt9 == tgt["tail"] and f"{j9:.4f}" == tgt["j"]
              and npriv == tgt["priv"] and nmiss == tgt["miss"]
              and nshared == tgt["shared"])
    # cluster split + (row,col) set guards
    incol_rows = sorted(int(pr[o]) for o in np.nonzero(incol)[0])
    cpriv_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(cpriv)[0]}
    cmiss_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(miss)[0]}
    cpriv_planes = {(int(pl[o])) for o in np.nonzero(cpriv)[0]}
    cmiss_planes = {(int(pl[o])) for o in np.nonzero(miss)[0]}
    incol_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(incol)[0]}
    print(f"s9 in-c321 priv rows={incol_rows} (want [266]); "
          f"rc={sorted(incol_rc)} (want [{M29_INCOL_RC}])")
    print(f"s9 cluster priv: n={len(cpriv_rc)} (want {tgt['cpriv_n']}) "
          f"planes={sorted(cpriv_planes)} (want [0]=all-Y)")
    print(f"s9 cluster miss: n={len(cmiss_rc)} (want {tgt['cmiss_n']}) "
          f"planes={sorted(cmiss_planes)} (want [0]=all-Y)")
    clus_ok = (incol_rows == [266] and incol_rc == {M29_INCOL_RC}
               and cpriv_rc == tgt["cpriv_set"] and cmiss_rc == tgt["cmiss_set"]
               and cpriv_planes == {0} and cmiss_planes == {0})
    if not clus_ok:
        print(f"s9 cluster priv rc sorted={sorted(cpriv_rc)}")
        print(f"s9 cluster miss rc sorted={sorted(cmiss_rc)}")
    rows9_c321 = y_col_rows(t9, 321, pl, pr, pc)
    c321_ok = rows9_c321 == S0_C321 + [266]
    print(f"s9 c321 rows: n={len(rows9_c321)} match=s0-rows+[266] -> {c321_ok}")
    print(f"s9 cell7 n={sets['sp9']['n']}")
    print(f"self Jaccard={jaccard(t0, t0):.4f} (want 1.0000)")
    print("M29 set guard: "
          + ("OK" if (set_ok and clus_ok and c321_ok)
             else "MISMATCH vs M29: STOP, tabled."))
    if not (set_ok and clus_ok and c321_ok):
        return

    # ---- P1 (s0-anchored) + carrier masks ----
    print("== s0 P1 + carrier masks ==")
    dec, qs, masks, checks = compute_dec_masks(m16d, mid0, b0)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    print(f"s0 P1 edges: {estrs} (m18.txt want {M18_P1_EDGE_S0}) "
          f"match={estrs == M18_P1_EDGE_S0}")
    if estrs != M18_P1_EDGE_S0:
        print("P1 edge MISMATCH: STOP, tabled.")
        return
    for rank, s, nrem, bd, ok in checks:
        print(f"carrier rank {rank} shape {s}: removedYpx={nrem} bands={bd} "
              + ("OK" if ok else "MISMATCH: STOP, tabled"))
        if not ok:
            return

    # ---- Task 1: per-site tables + joins ----
    print("== Task 1 (s9): full + cluster per-site tables ==")
    t1 = time.time()
    canon, _ = task1_lines(sets, v0, full0, v9, full9, dec, masks)
    for ln in canon:
        print(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.1: displacement ----
    print("== Task 2.1 (s9): nearest-shared displacement ==")
    for ln in displace_lines("s9full", priv, miss, shared):
        print(ln)
    for ln in displace_lines("s9clus", cpriv, miss, shared):
        print(ln)

    # ---- Task 2.2: components + cluster occupancy ----
    print("== Task 2.2: 8-conn components s0 vs s9 ==")
    for ln in comp_lines("s0", t0, nt0):
        print(ln)
    for ln in comp_lines("s9", t9, nt9):
        print(ln)
    print("== Task 2.2: per-comp cluster occupancy (s9 tail) ==")
    locc, h5best = occupancy_lines("s9tail", t9, cpriv_rc)
    for ln in locc:
        print(ln)
    print("== Task 2.2: union-mask comps (T_9 | T_s0, all 30 sites) ==")
    locc_u, _ = occupancy_lines("union", t9 | t0, cpriv_rc, cmiss_rc)
    for ln in locc_u:
        print(ln)

    # ---- determinism re-run (Task 1 on s0+9, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+9, second pass) ==")
    v0b, mid0b, full0b, b0b = load_triplet(m16d, 0)
    v9b, mid9b, full9b, b9b = load_triplet(m16d, 9)
    sets2 = compute_sets(v0b, mid0b, full0b, b0b, v9b, mid9b, full9b, b9b)
    dec2, _, masks2, _ = compute_dec_masks(m16d, mid0b, b0b)
    canon2, _ = task1_lines(sets2, v0b, full0b, v9b, full9b, dec2, masks2)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")
    print(f"sets identical: priv={int(sets2['priv'].sum())} "
          f"cpriv={int(sets2['cpriv'].sum())} "
          f"miss={int(sets2['miss'].sum())} "
          f"shared={int(sets2['shared'].sum())}")

    # ---- PNG cluster map (work dir; evidence copy iff rule meets) ----
    print("== PNG cluster map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    im_p, _, _ = flat_to_planes(cpriv)
    im_m, _, _ = flat_to_planes(miss)
    im_s, _, _ = flat_to_planes(shared)
    im_i, _, _ = flat_to_planes(incol)
    over[im_s] = np.array([0, 255, 0])        # shared green
    over[im_p] = np.array([255, 255, 0])      # cluster-priv yellow
    over[im_m] = np.array([255, 0, 255])      # cluster-miss magenta
    over[im_i] = np.array([255, 0, 0])        # in-column priv red
    p = workd / "m33-clusmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: green=shared tail(Y) yellow=cluster-priv(22) "
          "magenta=cluster-miss(8) red=in-column priv r266 "
          "(s0 geometry; Y only)")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    a0 = np.frombuffer(v0, np.uint8).astype(np.int16)
    f0a = np.frombuffer(full0, np.uint8).astype(np.int16)
    a9 = np.frombuffer(v9, np.uint8).astype(np.int16)
    f9a = np.frombuffer(full9, np.uint8).astype(np.int16)
    _ = (a0, f0a, a9, f9a)  # gaps already tabled per-site above
    cp_idx = np.nonzero(cpriv)[0]
    cm_idx = np.nonzero(miss)[0]
    sh_idx = np.nonzero(shared)[0]
    cp_near = sum(1 for o in cp_idx
                  if sets["mask0"][o] and int(abs(int(d0[o]))) in (6, 7))
    cp_non = sum(1 for o in cp_idx if not sets["mask0"][o])
    cm_non = sum(1 for o in cm_idx if not sets["mask9"][o])
    cp_dmin = dmin_list(cpriv, shared, pl, pr, pc)
    cp_d1 = sum(1 for d in cp_dmin if d == 1)
    cp_b1 = sum(1 for o in cp_idx if int(ROW_BAND[int(pr[o])]) == 1)
    sh_b1 = sum(1 for o in sh_idx if int(ROW_BAND[int(pr[o])]) == 1)
    cp_d9 = sum(1 for o in cp_idx if int(dec[int(pr[o]), int(pc[o])]) == 9)
    sh_d9 = sum(1 for o in sh_idx if int(dec[int(pr[o]), int(pc[o])]) == 9)
    ncp, nsh, ncm = len(cp_idx), len(sh_idx), len(cm_idx)
    band_leg = abs(cp_b1 / ncp - sh_b1 / nsh) if ncp and nsh else 0.0
    dec_leg = abs(cp_d9 / ncp - sh_d9 / nsh) if ncp and nsh else 0.0
    print(f"H1_CLUSNEAR: near {cp_near}/{ncp} "
          f"({cp_near / ncp if ncp else 0:.4f}; bar >=0.50)")
    print(f"H2_CLUSSET: noncell {cp_non}/{ncp} "
          f"({cp_non / ncp if ncp else 0:.4f}; bar >=0.50)")
    print(f"H3_DISPLACE: d1 {cp_d1}/{ncp} "
          f"({cp_d1 / ncp if ncp else 0:.4f}; bar >=0.50)")
    print(f"H4_LOCALIZE: band-1 cpriv {cp_b1}/{ncp} "
          f"({cp_b1 / ncp if ncp else 0:.4f}) vs shared {sh_b1}/{nsh} "
          f"({sh_b1 / nsh if nsh else 0:.4f}) |diff|={band_leg:.4f} "
          f"(bar >=0.25); dec-9 cpriv {cp_d9}/{ncp} "
          f"({cp_d9 / ncp if ncp else 0:.4f}) vs shared {sh_d9}/{nsh} "
          f"({sh_d9 / nsh if nsh else 0:.4f}) |diff|={dec_leg:.4f} "
          f"(bar >=0.25)")
    print(f"H5_ONECOMP: max-cpriv-in-one-s9comp {h5best}/{ncp} "
          f"({h5best / ncp if ncp else 0:.4f}; bar >=0.50)")
    print(f"H6_MISSSET: noncell {cm_non}/{ncm} "
          f"({cm_non / ncm if ncm else 0:.4f}; bar >=0.50)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=cluster-sites T2=joins+displace+comps R=controls")


if __name__ == "__main__":
    main()
