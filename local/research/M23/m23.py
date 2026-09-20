#!/usr/bin/env python3
"""M23 tail value mechanism: per-site value tables + predictor fits (offline).

Usage: m23.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text goes
to stdout (redirect to WORK_DIR/m23.txt); PNG residual map to WORK_DIR
(evidence copy iff discriminating, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: per-site value tables ((gap,d) / (position,d) / (carrier,d) joints)
  2: predictor fits (fixed 9-list, exact-hit scoring + transfer)
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
STREAK_COLS = (257, 277, 296, 301, 321, 340, 341, 342, 343)
XSHAPE_IDS = (1, 2, 733)  # DESIGN.md: 1, 2 + min-Jaccard 733
PRED_IDS = ["K40+", "K40-", "K45+", "K45-", "STEP1", "STEP2", "STEP3",
            "COMP", "POS"]


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
BAND_OF_ROW = np.zeros(H, np.int32)
for _bi, _rows in enumerate(BAND_ROWS):
    BAND_OF_ROW[_rows] = _bi


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


def component_labels(sites: np.ndarray):
    """8-conn union-find (same algorithm as connected_components) returning
    a deterministic label plane: ids 0..K-1 ordered by (min_r, min_c)."""
    h, w = sites.shape
    lab = np.full((h, w), -1, np.int32)
    ys, xs = np.nonzero(sites)
    n = len(ys)
    if n == 0:
        return lab, 0
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
    roots = {}
    for k in range(n):
        roots.setdefault(find(k), []).append(k)
    order = sorted(roots.values(),
                   key=lambda ks: (int(ys[ks].min()), int(xs[ks].min())))
    for cid, ks in enumerate(order):
        for k in ks:
            lab[int(ys[k]), int(xs[k])] = cid
    return lab, len(order)


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    inter = int((a & b).sum())
    union = int((a | b).sum())
    if union == 0:
        return 1.0  # both empty: identical (tabled, see receipt)
    return inter / union


# ---- fixed predictor machinery (DESIGN.md list, exact integer arith) ----

def k40mag(a: np.ndarray) -> np.ndarray:
    return (2 * np.abs(a) + 2) // 5


def k45mag(a: np.ndarray) -> np.ndarray:
    return (9 * np.abs(a) + 10) // 20


def rhalf_away_mean(s: int, n: int) -> int:
    """round-half-away-from-zero of s/n (n>0), exact integer arithmetic."""
    if s >= 0:
        return (2 * s + n) // (2 * n)
    return -((2 * (-s) + n) // (2 * n))


def int_median(vals) -> int:
    """Median of ints; even-n mean-of-middles, halves away from zero."""
    v = sorted(int(x) for x in vals)
    n = len(v)
    if n % 2 == 1:
        return v[n // 2]
    s = v[n // 2 - 1] + v[n // 2]
    if s >= 0:
        return (s + 1) // 2
    return -((-s + 1) // 2)


def formula_pred(pid: str, g: np.ndarray) -> np.ndarray:
    """Constant-free predictors K*/STEP* from signed gaps (exact ints)."""
    s = np.sign(g).astype(np.int64)
    if pid == "K40+":
        return (s * k40mag(g)).astype(np.int16)
    if pid == "K40-":
        return (-s * k40mag(g)).astype(np.int16)
    if pid == "K45+":
        return (s * k45mag(g)).astype(np.int16)
    if pid == "K45-":
        return (-s * k45mag(g)).astype(np.int16)
    if pid == "STEP1":
        return (s * 1).astype(np.int16)
    if pid == "STEP2":
        return (s * 2).astype(np.int16)
    if pid == "STEP3":
        return (s * 3).astype(np.int16)
    raise ValueError(pid)

def site_cells(off: np.ndarray, dec: np.ndarray, rr: np.ndarray,
               cc: np.ndarray, pl: np.ndarray) -> np.ndarray:
    """POS cell id = band*2 + (dec==9); U/V via co-located Y (r,2c)."""
    ycol = np.where(pl == 0, cc, 2 * cc)
    d9 = (dec[rr[off], ycol[off]] == 9).astype(np.int32)
    return BAND_OF_ROW[rr[off]] * 2 + d9


def fit_comp(im_yt: np.ndarray, ey: np.ndarray):
    """COMP fit: 8-conn component id -> rounded mean d + fallback."""
    lab, ncomp = component_labels(im_yt)
    comp_pred = {}
    for cid in range(ncomp):
        sel = lab == cid
        dd = ey[sel].astype(np.int64)
        comp_pred[cid] = rhalf_away_mean(int(dd.sum()), int(sel.sum()))
    dd_all = ey[im_yt].astype(np.int64)
    if len(dd_all):
        fallback = rhalf_away_mean(int(dd_all.sum()), len(dd_all))
    else:
        fallback = 0
    return {"labels": lab, "ncomp": ncomp, "pred": comp_pred,
            "fallback": fallback}


def fit_pos(off: np.ndarray, delta: np.ndarray, dec: np.ndarray,
            rr: np.ndarray, cc: np.ndarray, pl: np.ndarray):
    """POS fit: 6 cells -> median d + fallback (global tail median)."""
    cells = site_cells(off, dec, rr, cc, pl)
    med = {}
    empties = []
    for cell in range(6):
        vv = delta[off[cells == cell]].astype(np.int64)
        if len(vv):
            med[cell] = int_median(vv)
        else:
            empties.append(cell)
    fallback = int_median(delta[off].astype(np.int64)) if len(off) else 0
    for cell in empties:
        med[cell] = fallback
    return {"med": med, "fallback": fallback, "empties": empties}


def coarse_hist(vals: np.ndarray, bins) -> str:
    return " ".join(
        f"{lo}-{hi if hi < 999 else '+'}:"
        f"{int(((vals >= lo) & (vals <= hi)).sum())}"
        for lo, hi in bins)


def exact_counts(vals: np.ndarray) -> str:
    if len(vals) == 0:
        return "(empty)"
    v, c = np.unique(vals.astype(np.int64), return_counts=True)
    return " ".join(f"{int(x)}:{int(n)}" for x, n in zip(v, c))


def score_lines(prefix: str, d: np.ndarray, preds: dict):
    """Exact-hit scoring lines per predictor; preds pid->array or None.

    None (COMP cross-frame) reads N/A. Returns (lines, hits).
    """
    L = []
    hits = {}
    for pid in PRED_IDS:
        p = preds.get(pid)
        if p is None:
            L.append(f"{prefix} {pid}: N/A (frame-local ids, DESIGN.md)")
            hits[pid] = None
            continue
        err = p.astype(np.int64) - d.astype(np.int64)
        ae = np.abs(err)
        nh = int((ae == 0).sum())
        nn = int((ae == 1).sum())
        miss = ae[(ae != 0) & (ae != 1)]
        bins = [(2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        L.append(f"{prefix} {pid}: n={len(d)} hits={nh} "
                 f"rate={nh / len(d):.4f} near={nn} "
                 f"nearrate={nn / len(d):.4f} miss|err| "
                 f"{coarse_hist(miss, bins)}")
        L.append(f"{prefix} {pid} errvalues: {exact_counts(ae)}")
        hits[pid] = nh
    return L, hits


def task1_value_lines(tag, v0b, midb, fullb, synth, ym, masks):
    """Task 1 value tables for one frame; returns (lines, art)."""
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
    L.append(f"{tag} tail n={nt} (M22 want {M20_TAIL[tag]}); "
             f"bulk n={nb}; tail 8-15={n815} 16+={n16p} "
             f"(want {M20_TAIL_SUB[tag][0]}+{M20_TAIL_SUB[tag][1]}); "
             f"tail max={int(adt.max()) if nt else 0} "
             f"(want {M20_TAIL_MAX[tag]})")
    if (nt != M20_TAIL[tag] or (n815, n16p) != M20_TAIL_SUB[tag]
            or int(adt.max()) != M20_TAIL_MAX[tag]):
        L.append(f"{tag} TAIL MISMATCH: STOP, tabled.")
        return L, None
    pl = plane_of_byte()
    plt = pl[tail]
    for pid_, nm in ((0, "Y"), (1, "U"), (2, "V")):
        L.append(f"{tag} tailplane {nm}: n={int((plt == pid_).sum())} "
                 f"(want {'102/134' if pid_ == 0 else '0'})")
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    g = (a - b).astype(np.int16)  # signed gap
    off = np.flatnonzero(tail)
    dt = delta[tail].astype(np.int64)
    gt = g[tail].astype(np.int64)
    agt = np.abs(gt)

    # 1.1a: |g| bins from M22's hist edges
    for lo, hi in ((2, 3), (4, 7), (8, 15), (16, 31), (32, 63),
                   (64, 1 << 15)):
        sel = (agt >= lo) & (agt <= hi)
        vv = dt[sel]
        lab = f"{lo}-{hi}" if hi < 999 else "64+"
        L.append(f"{tag} gapbin {lab}: n={int(sel.sum())} "
                 f"ndistinct={len(np.unique(vv)) if len(vv) else 0} "
                 f"mean={float(vv.mean()) if len(vv) else 0:.3f} "
                 f"amean={float(np.abs(vv).mean()) if len(vv) else 0:.3f}")
        L.append(f"{tag} gapbin {lab} dlist: {exact_counts(vv)}")
    # 1.1b: exact signed-gap-value table (collisions flagged)
    gv, first, counts = np.unique(gt, return_index=True, return_counts=True)
    order = np.argsort(gv)
    n_ge2 = 0
    n_alleq = 0
    for i in order:
        sel = gt == gv[i]
        vv = dt[sel]
        coll = len(np.unique(vv)) > 1
        if int(sel.sum()) >= 2:
            n_ge2 += 1
            if not coll:
                n_alleq += 1
        L.append(f"{tag} gapval g={int(gv[i])}: n={int(sel.sum())} "
                 f"collision={coll} dlist: {exact_counts(vv)}")
    L.append(f"{tag} gapval H6: n_ge2={n_ge2} all_equal={n_alleq} "
             f"share={n_alleq / n_ge2 if n_ge2 else 0:.4f}")

    # 1.2: position tables (P1 deciles + bands + streak columns)
    mag, qs, dec = p1_gradient(ym)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    L.append(f"{tag} P1 edges: {estrs} (m18.txt want {M18_P1_EDGES[tag]}) "
             f"match={estrs == M18_P1_EDGES[tag]}")
    rr, cc = plane_coords()
    cells = site_cells(off, dec, rr, cc, pl)
    for cell in range(6):
        sel = cells == cell
        vv = dt[sel]
        L.append(f"{tag} poscell band={cell // 2} dec9={cell % 2}: "
                 f"n={int(sel.sum())} "
                 f"mean={float(vv.mean()) if len(vv) else 0:.3f} "
                 f"amean={float(np.abs(vv).mean()) if len(vv) else 0:.3f} "
                 f"dlist: {exact_counts(vv)}")
    im_yt, _, _ = flat_to_planes(tail)
    ey = flat_to_planes(delta)[0].astype(np.int64)
    for ccol in STREAK_COLS:
        sel = im_yt[:, ccol]
        vv = ey[:, ccol][sel]
        rws = np.flatnonzero(sel)
        L.append(f"{tag} streakcol c={ccol}: n={int(sel.sum())} "
                 f"rows=[{int(rws.min()) if len(rws) else -1},"
                 f"{int(rws.max()) if len(rws) else -1}] "
                 f"mean={float(vv.mean()) if len(vv) else 0:.3f} "
                 f"amean={float(np.abs(vv).mean()) if len(vv) else 0:.3f} "
                 f"dlist: {exact_counts(vv)}")
    other = np.ones(W, bool)
    other[list(STREAK_COLS)] = False
    selo = im_yt[:, other]
    vvo = ey[:, other][selo]
    L.append(f"{tag} streakcol other: n={int(selo.sum())} "
             f"mean={float(vvo.mean()) if len(vvo) else 0:.3f} "
             f"amean={float(np.abs(vvo).mean()) if len(vvo) else 0:.3f} "
             f"dlist: {exact_counts(vvo)}")

    # 1.3: carrier-context tables (inside/outside each top-10 mask)
    _, im_ut, im_vt = flat_to_planes(tail)
    for rank, s in enumerate(M16_TOP10, 1):
        rm = masks[s]
        yin = im_yt & rm
        yout = im_yt & ~rm
        rm_u = rm[:, 0::2]
        uin = int((im_ut & rm_u).sum())
        vin = int((im_vt & rm_u).sum())
        for nm2, sel in (("inside", yin), ("outside", yout)):
            vv = ey[sel]
            L.append(f"{tag} carrier rank={rank} shape={s} Y-{nm2}: "
                     f"n={int(sel.sum())} "
                     f"mean={float(vv.mean()) if len(vv) else 0:.3f} "
                     f"amean={float(np.abs(vv).mean()) if len(vv) else 0:.3f} "
                     f"dlist: {exact_counts(vv)}")
        L.append(f"{tag} carrier rank={rank} shape={s} U_in={uin} "
                 f"V_in={vin}")
    rm701 = masks[701]
    L.append(f"{tag} 701 tailY_in={int((im_yt & rm701).sum())} "
             f"(M20 want 0) tailY_out={int((im_yt & ~rm701).sum())} "
             f"(M20 want {M20_701_TAIL_OUT})")

    art = {"n": n, "nt": nt, "mask": mask, "delta": delta, "tail": tail,
           "off": off, "dt": dt, "gt": gt, "im_yt": im_yt, "ey": ey,
           "dec": dec, "g": g}
    return L, art

def build_same_preds(art, fcomp, fpos, rr, cc, pl):
    """Predictor arrays for a frame scored with its own fit."""
    preds = {}
    for pid in PRED_IDS:
        if pid in ("COMP", "POS"):
            continue
        preds[pid] = formula_pred(pid, art["gt"])
    lab = fcomp["labels"]
    site_lab = lab[rr[art["off"]], np.where(pl[art["off"]] == 0,
                                            cc[art["off"]], -1)]
    # U/V sites (col -1 indexes last col): mask them to fallback below.
    is_y = pl[art["off"]] == 0
    comp_vals = np.full(len(art["off"]), fcomp["fallback"], np.int64)
    for i in np.flatnonzero(is_y):
        cid = int(site_lab[i])
        if cid >= 0:
            comp_vals[i] = fcomp["pred"][cid]
    preds["COMP"] = comp_vals.astype(np.int16)
    cells = site_cells(art["off"], art["dec"], rr, cc, pl)
    preds["POS"] = np.array([fpos["med"][int(c)] for c in cells],
                            np.int16)
    return preds


def build_xframe_preds(scored, fit_pos_o, rr, cc, pl):
    """Cross-frame predictor arrays (fit constants from the other frame).

    K*/STEP* constant-free; POS uses fit frame medians; COMP N/A.
    """
    preds = {}
    for pid in PRED_IDS:
        if pid in ("COMP", "POS"):
            continue
        preds[pid] = formula_pred(pid, scored["gt"])
    preds["COMP"] = None
    cells = site_cells(scored["off"], scored["dec"], rr, cc, pl)
    preds["POS"] = np.array(
        [fit_pos_o["med"].get(int(c), fit_pos_o["fallback"])
         for c in cells], np.int16)
    return preds


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0)
    rr, cc = plane_coords()
    pl = plane_of_byte()

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
        print("MISMATCH vs M17-M22 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    # ---- carrier masks (M19 Test-C verbatim; needed for Task 1.3) ----
    print("== carrier masks (Task 1.3 input) ==")
    masks = {}
    if not carriers_ok:
        print("carrier mismatch: STOP before Task 1.3, tabled.")
        return
    sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
    res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
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
        print(f"rank {rank} shape {s}: removedYpx={nrem} "
              f"(want {M19_REMOVED[rank - 1]}) bands={bd} "
              f"(want {M19_REMOVED_BANDS[rank - 1]}) "
              f"match={nrem == M19_REMOVED[rank - 1] and bd == M19_REMOVED_BANDS[rank - 1]}")

    print("== Task 1: value tables s0 ==")
    t1 = time.time()
    L0, art0 = task1_value_lines("s0", v0, mid, full, b0, ym0, masks)
    for ln in L0:
        print(ln)
        canon.append(ln)
    print(f"(Task-1 s0 wall: {time.time() - t1:.1f}s)")
    if art0 is None:
        print("cell-7/tail guard failed on s0: STOP before Task 1.1.")
        return
    print("== Task 1: value tables m15 ==")
    t1 = time.time()
    L15, art15 = task1_value_lines("m15", v015, mid15, full15, b15, ym15,
                                   masks)
    for ln in L15:
        print(ln)
    print(f"(Task-1 m15 wall: {time.time() - t1:.1f}s)")
    if art15 is None:
        print("cell-7/tail guard failed on m15: STOP before Task 1.1.")
        return
    print(f"self jaccard s0={jaccard(art0['tail'], art0['tail']):.4f} "
          f"(want 1.0) m15={jaccard(art15['tail'], art15['tail']):.4f}")

    # ---- fits ----
    print("== Task 2 fits ==")
    fcomp0 = fit_comp(art0["im_yt"], art0["ey"])
    fcomp15 = fit_comp(art15["im_yt"], art15["ey"])
    print(f"fit COMP s0: ncomp={fcomp0['ncomp']} (M22 8-conn want 25) "
          f"fallback={fcomp0['fallback']}")
    print(f"fit COMP m15: ncomp={fcomp15['ncomp']} (M22 8-conn want 31) "
          f"fallback={fcomp15['fallback']}")
    for cid in sorted(fcomp0["pred"]):
        print(f"fit COMP s0 comp={cid} pred={fcomp0['pred'][cid]}")
    for cid in sorted(fcomp15["pred"]):
        print(f"fit COMP m15 comp={cid} pred={fcomp15['pred'][cid]}")
    fpos0 = fit_pos(art0["off"], art0["delta"], art0["dec"], rr, cc, pl)
    fpos15 = fit_pos(art15["off"], art15["delta"], art15["dec"], rr, cc,
                     pl)
    print(f"fit POS s0: med={[fpos0['med'][c] for c in range(6)]} "
          f"fallback={fpos0['fallback']} empties={fpos0['empties']}")
    print(f"fit POS m15: med={[fpos15['med'][c] for c in range(6)]} "
          f"fallback={fpos15['fallback']} empties={fpos15['empties']}")

    # ---- Task 2.1: same-frame scoring ----
    print("== Task 2.1: same-frame scores s0 ==")
    preds0 = build_same_preds(art0, fcomp0, fpos0, rr, cc, pl)
    LS0, H0 = score_lines("score s0", art0["dt"], preds0)
    for ln in LS0:
        print(ln)
    print("== Task 2.1: same-frame scores m15 ==")
    preds15 = build_same_preds(art15, fcomp15, fpos15, rr, cc, pl)
    LS15, H15 = score_lines("score m15", art15["dt"], preds15)
    for ln in LS15:
        print(ln)

    # ---- best predictor (DESIGN.md rule) + residual ----
    order = {pid: i for i, pid in enumerate(PRED_IDS)}
    best = sorted(PRED_IDS, key=lambda p: (-H0[p], -H15[p], order[p]))[0]
    print(f"best predictor: {best} (s0hits={H0[best]} m15hits={H15[best]} "
          f"pooled={H0[best] + H15[best]})")
    for tag, art, pr in (("s0", art0, preds0), ("m15", art15, preds15)):
        resid = np.abs(art["dt"].astype(np.int64)
                       - pr[best].astype(np.int64))
        bins = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        print(f"residual {tag} best={best}: {coarse_hist(resid, bins)}")
        print(f"residual {tag} best={best} values: {exact_counts(resid)}")
        print(f"explained {tag}: {int((resid == 0).sum())}/{art['nt']} "
              f"standing={int((resid != 0).sum())}")

    # ---- Task 2.2: cross-frame both directions ----
    print("== Task 2.2: fit-s0 score-m15 ==")
    pxf_0_15 = build_xframe_preds(art15, fpos0, rr, cc, pl)
    LX1, HX1 = score_lines("xframe fit-s0/score-m15", art15["dt"],
                           pxf_0_15)
    for ln in LX1:
        print(ln)
    print("== Task 2.2: fit-m15 score-s0 ==")
    pxf_15_0 = build_xframe_preds(art0, fpos15, rr, cc, pl)
    LX2, HX2 = score_lines("xframe fit-m15/score-s0", art0["dt"],
                           pxf_15_0)
    for ln in LX2:
        print(ln)

    # ---- Task 2.3: cross-shape (shapes 1, 2, 733; s0 constants) ----
    print("== Task 2.3: cross-shape, best predictor + s0 constants ==")
    # s0 COMP offset map for the pre-registered xshape fallback
    lab0 = fcomp0["labels"]
    off2comp = {}
    for o in art0["off"]:
        if pl[o] == 0:
            cid = int(lab0[rr[o], cc[o]])
            if cid >= 0:
                off2comp[int(o)] = fcomp0["pred"][cid]
    for s in XSHAPE_IDS:
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        yms = split_planes(np.frombuffer(mm, np.uint8))[0]
        sp = interior_sites(vv, mm, ff, bl)
        tk, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        aa = np.frombuffer(vv, np.uint8).astype(np.int16)
        bb = np.frombuffer(ff, np.uint8).astype(np.int16)
        gg = (aa - bb).astype(np.int16)
        offs = np.flatnonzero(tk)
        dd = sp["delta"][tk].astype(np.int64)
        ggg = gg[tk].astype(np.int64)
        _, _, decs = p1_gradient(yms)
        if best in ("COMP", "POS"):
            if best == "COMP":
                pv = np.array([off2comp.get(int(o), fcomp0["fallback"])
                               for o in offs], np.int16)
            else:
                cells = site_cells(offs, decs, rr, cc, pl)
                pv = np.array([fpos0["med"].get(int(c),
                                                fpos0["fallback"])
                               for c in cells], np.int16)
        else:
            pv = formula_pred(best, ggg)
        err = pv.astype(np.int64) - dd
        ae = np.abs(err)
        nh = int((ae == 0).sum())
        nn = int((ae == 1).sum())
        miss = ae[(ae != 0) & (ae != 1)]
        bins = [(2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        print(f"xshape {s}: best={best} tailn={len(dd)} hits={nh} "
              f"rate={nh / len(dd) if len(dd) else 0:.4f} near={nn} "
              f"miss|err| {coarse_hist(miss, bins)}")
        print(f"xshape {s}: errvalues: {exact_counts(ae)}")
        print(f"xshape {s}: jacc vs s0={jaccard(tk, art0['tail']):.4f} "
              f"(M22 table) vs m15={jaccard(tk, art15['tail']):.4f}")

    # ---- determinism re-run (Task 1 on s0, canonical text) ----
    print("== determinism re-run (Task 1 on s0, second pass) ==")
    L0b, art0b = task1_value_lines("s0", v0, mid, full, b0, ym0, masks)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0b is not None and art0['n'] == art0b['n']}"
          f" tail counts identical="
          f"{art0b is not None and art0['nt'] == art0b['nt']}")

    # ---- PNG residual map (work dir; evidence copy iff discriminating) ----
    print("== PNG residual map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    err0 = np.abs(art0["dt"].astype(np.int64)
                  - preds0[best].astype(np.int64))
    hit_y = np.zeros((H, W), bool)
    near_y = np.zeros((H, W), bool)
    miss_y = np.zeros((H, W), bool)
    for o, e in zip(art0["off"], err0):
        if pl[o] == 0:
            if e == 0:
                hit_y[rr[o], cc[o]] = True
            elif e == 1:
                near_y[rr[o], cc[o]] = True
            else:
                miss_y[rr[o], cc[o]] = True
    over[miss_y] = np.array([255, 0, 0])       # miss red
    over[near_y] = np.array([255, 255, 0])     # near yellow
    over[hit_y] = np.array([0, 255, 0])        # hit green
    p = workd / "m23-residmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: best={best} green=hit n={int(hit_y.sum())} "
          f"yellow=near n={int(near_y.sum())} red=miss "
          f"n={int(miss_y.sum())} (tail Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=value-tables T2=predictor-fits R=controls")


if __name__ == "__main__":
    main()

