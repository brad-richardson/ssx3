#!/usr/bin/env python3
"""M59 dec-1 all-positive delta: per-bin sign census joined with columns (offline).

Usage: m59.py M16_DIR M15_DIR M58TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, and the M58
receipt (decile-bin table to reproduce); raw XFB dumps, 573440 B =
640x448 YUYV. Read-only inputs; receipt text goes to stdout (redirect
to WORK_DIR/m59.txt); PNG sign map to WORK_DIR (evidence copy iff
the DESIGN.md rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: bin-sign reproduction (binsign + dec-1 sites + background)
  2: sign-by-column census (colsign + bincol + colmode)
  3: controls (control.py) + determinism + shas + Model-0 recompute
Tables, no verdicts.
"""
import hashlib
import math
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
M20_TAIL = {"s0": 102, "m15": 134}
M20_TAIL_SUB = {"s0": (28, 74), "m15": (50, 84)}  # (8-15, 16+)
M20_TAIL_MAX = {"s0": 47, "m15": 48}
M19_POSRATE = {"s0": 0.8093, "m15": 0.8019}  # P(d>0) on cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
M19_REMOVED = [4888, 1208, 649, 448, 248, 244, 191, 174, 190, 202]
M19_REMOVED_BANDS = [[3415, 1442, 31], [824, 384, 0], [186, 463, 0],
                     [0, 0, 448], [0, 0, 248], [0, 0, 244], [0, 0, 191],
                     [0, 0, 174], [0, 0, 190], [0, 187, 15]]
M18_P1_EDGE_S0 = "0 1 2 2 4 6 8 12 18 29 176"
NAMED8 = (257, 277, 296, 301, 321, 340, 342, 343)
NAMED9 = [257, 277, 296, 301, 321, 340, 341, 342, 343]
# Per-column guard: (n, minrow, maxrow, sum delta); rows (-1,-1) when n==0.
COL_GUARD = {
    "s0": {257: (10, 23, 32, 255), 277: (10, 23, 32, 244),
           296: (9, 24, 34, 294), 301: (11, 23, 33, 339),
           321: (10, 23, 32, 227), 340: (8, 24, 34, 292),
           341: (0, -1, -1, 0), 342: (5, 27, 35, -94),
           343: (2, 26, 27, -57)},
    "m15": {257: (10, 23, 32, 172), 277: (10, 23, 32, 172),
            296: (9, 24, 34, 306), 301: (11, 23, 33, 291),
            321: (10, 23, 32, 252), 340: (9, 24, 34, 311),
            341: (1, 280, 280, -9), 342: (5, 27, 35, -87),
            343: (4, 25, 289, -97)},
}
# M58 pins: m15 tail-Y decile histogram + decile-bin table + dec-1 sites
# (recompute must match exactly or stop).
M58_HIST_M15 = {"n": 134, "counts": {0: 13, 1: 12, 2: 0, 3: 19, 4: 5,
                                     5: 2, 6: 1, 7: 2, 8: 5, 9: 75}}
# dec -> (n, {delta: count}, min, max, sum, pos, neg); None min/max when n==0.
M58_DECBIN = {
    0: (13, {-9: 6, -8: 1, 10: 1, 15: 1, 18: 2, 20: 2},
        -9, 20, 39, 6, 7),
    1: (12, {9: 2, 10: 2, 14: 1, 15: 1, 19: 1, 21: 1, 22: 1,
             23: 1, 29: 1, 33: 1}, 9, 33, 214, 12, 0),
    2: (0, {}, None, None, 0, 0, 0),
    3: (19, {-18: 1, -16: 1, -15: 1, -9: 2, -8: 2, 8: 1, 9: 1,
             10: 1, 11: 1, 13: 1, 14: 1, 19: 1, 22: 3, 24: 1,
             46: 1}, -18, 46, 137, 12, 7),
    4: (5, {-8: 2, 8: 1, 17: 1, 26: 1}, -8, 26, 35, 3, 2),
    5: (2, {9: 1, 20: 1}, 9, 20, 29, 2, 0),
    6: (1, {-35: 1}, -35, -35, -35, 0, 1),
    7: (2, {11: 1, 46: 1}, 11, 46, 57, 2, 0),
    8: (5, {-14: 1, -9: 2, 14: 1, 23: 1}, -14, 23, 5, 2, 3),
    9: (75, {-36: 1, -34: 1, -26: 3, -22: 1, -21: 1, -20: 1,
             -19: 2, -17: 1, -14: 1, -13: 1, -12: 1, -8: 2, 8: 2,
             10: 1, 12: 3, 13: 1, 14: 2, 15: 1, 16: 5, 18: 3,
             19: 5, 20: 8, 23: 1, 24: 3, 28: 2, 29: 2, 30: 2,
             31: 2, 35: 1, 37: 3, 38: 3, 40: 3, 46: 2, 47: 2,
             48: 2}, -36, 48, 1179, 59, 16),
}
# dec-1 sites: {(row, col): delta} x12 (M58 site-51 pins).
M58_DEC1 = {(320, 307): 9, (327, 309): 10, (321, 310): 10,
            (320, 311): 22, (318, 312): 19, (319, 312): 9,
            (341, 312): 14, (373, 312): 33, (374, 312): 15,
            (378, 312): 23, (339, 313): 29, (336, 315): 21}
M58_OFF51_POSNEG = (35, 16)  # pooled off-51 pos/neg
M58_DEC9_POSNEG = (59, 16)  # dec-9 pos/neg
OFF51_MAXDEC = 5  # off-mode = s0-P1 decile <= 5
NULL4_COLS = (313, 332, 314, 311)
FAR_THRESH = 100
PNAME = ("Y", "U", "V")


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


def load_triplet(m16d: Path, s: int):
    vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
    mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
    ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
    return vv, mm, ff, synth_w_bytes(vv, ff, 0.5)


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


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    inter = int((a & b).sum())
    union = int((a | b).sum())
    if union == 0:
        return 1.0  # both empty: identical (tabled, see receipt)
    return inter / union


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


def rhalf(x: float) -> int:
    """Round-half-away-from-zero of a float."""
    if x >= 0:
        return int(math.floor(x + 0.5))
    return -int(math.floor(-x + 0.5))


def quadfit(rows: np.ndarray, deltas: np.ndarray):
    """OLS delta ~ a*r^2 + b*r + c (float64 lstsq). Returns (a, b, c)
    or None if degenerate (n<3)."""
    n = len(rows)
    if n < 3:
        return None
    r = rows.astype(np.float64)
    d = deltas.astype(np.float64)
    X = np.stack([r ** 2, r, np.ones(n)], axis=1)
    sol, *_ = np.linalg.lstsq(X, d, rcond=None)
    return (float(sol[0]), float(sol[1]), float(sol[2]))


def tri_pred_float(r, p: int, h: float, e: float, w: int) -> float:
    return e + (h - e) * max(0.0, 1.0 - abs(float(r) - float(p)) / float(w))


def trifit(rows: np.ndarray, deltas: np.ndarray):
    """Symmetric triangle fit (DESIGN.md pinned). Returns dict with
    p/h/e/w + flat flag. Degenerate (h==e or Wmax<1) -> constant-h."""
    rr = rows.astype(np.int64)
    dd = deltas.astype(np.int64)
    k = int(np.argmax(dd))  # first occurrence on ties
    p = int(rr[k])
    h = int(dd[k])
    e = int(min(int(dd[0]), int(dd[-1])))  # row-order first/last
    if h == e:
        return {"p": p, "h": h, "e": e, "w": 1, "flat": True}
    wmax = max(p - int(rr.min()), int(rr.max()) - p)
    if wmax < 1:
        return {"p": p, "h": h, "e": e, "w": 1, "flat": True}
    best_w, best_sse = 1, None
    for w in range(1, wmax + 1):
        sse = sum((float(x) - tri_pred_float(r, p, float(h), float(e), w)) ** 2
                  for r, x in zip(rr.tolist(), dd.tolist()))
        if best_sse is None or sse < best_sse:
            best_sse = sse
            best_w = w
    return {"p": p, "h": h, "e": e, "w": best_w, "flat": False}


def tri_apply(rows: np.ndarray, fit) -> np.ndarray:
    return np.array([rhalf(tri_pred_float(r, fit["p"], float(fit["h"]),
                                          float(fit["e"]), fit["w"]))
                     for r in rows.astype(np.int64).tolist()], np.int64)


def hump_metrics(rows: np.ndarray, deltas: np.ndarray):
    """Hump metrics (DESIGN.md pinned, no special-casing)."""
    rr = rows.astype(np.int64)
    dd = deltas.astype(np.int64)
    n = len(dd)
    k = int(np.argmax(dd))  # first occurrence on ties
    peakrow, peakval = int(rr[k]), int(dd[k])
    first, last = int(dd[0]), int(dd[-1])
    rise, fall = peakval - first, peakval - last
    third = "top" if 3 * k < n else ("bottom" if 3 * k >= 2 * n else "mid")
    return {"peakrow": peakrow, "peakval": peakval, "first": first,
            "last": last, "rise": rise, "fall": fall,
            "sym": abs(rise - fall), "k": k, "n": n, "third": third}


def hole_ranges(rows: np.ndarray) -> str:
    """Missing rows within [min,max] as compact ranges; 'none' if full."""
    if len(rows) == 0:
        return "(empty)"
    present = set(int(r) for r in rows)
    lo, hi = min(present), max(present)
    holes = [r for r in range(lo, hi + 1) if r not in present]
    if not holes:
        return "none"
    out, s, p = [], holes[0], holes[0]
    for r in holes[1:] + [None]:
        if r is not None and r == p + 1:
            p = r
            continue
        out.append(f"{s}" if s == p else f"{s}-{p}")
        s = p = r
    return ",".join(out) + f" (nholes={len(holes)})"


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


def off_y(r: int, c: int) -> int:
    """Y-byte offset of (row, Y-col)."""
    return int(r) * ROWB + (int(c) // 2) * 4 + (0 if int(c) % 2 == 0 else 2)


def y_col_dict(tail: np.ndarray, pr: np.ndarray, pc: np.ndarray,
               pl: np.ndarray, delta: np.ndarray):
    """Tail-Y column profiles: col -> rows/deltas/offs sorted by row."""
    out = {}
    idx = np.nonzero(tail & (pl == 0))[0]
    tmp = {}
    for o in idx:
        o = int(o)
        c, r = int(pc[o]), int(pr[o])
        tmp.setdefault(c, []).append((r, int(delta[o]), o))
    for c, lst in tmp.items():
        lst.sort()
        out[c] = {"rows": [r for r, _, _ in lst],
                  "deltas": [d for _, d, _ in lst],
                  "offs": [o for _, _, o in lst]}
    return out


def far_info(rows):
    """Nearest-neighbor row distance per site (DESIGN.md pinned).

    rows: sorted ascending list. Returns (d, lo, hi) lists with
    None for the singleton case (n==1, no band).
    """
    n = len(rows)
    if n == 1:
        return [None], [None], [None]
    d, lo, hi = [], [], []
    for i, r in enumerate(rows):
        l = rows[i - 1] if i > 0 else None
        h = rows[i + 1] if i < n - 1 else None
        dl = r - l if l is not None else None
        dh = h - r if h is not None else None
        if dl is None:
            best = dh
        elif dh is None:
            best = dl
        else:
            best = min(dl, dh)
        d.append(best)
        lo.append(l)
        hi.append(h)
    return d, lo, hi


def aux_dist(r: int, rows):
    """Auxiliary distances vs rest rows (d_out, d_lim). Rows includes r."""
    rest = [x for x in rows if x != r]
    if not rest:
        return None, None
    mn, mx = min(rest), max(rest)
    if mn < r < mx:
        d_out = 0
    elif r < mn:
        d_out = mn - r
    else:
        d_out = r - mx
    d_lim = min(abs(r - mn), abs(r - mx))
    return d_out, d_lim


def pooled_d(r: int, pooled_rows):
    """Nearest-neighbor distance vs pooled-union rows (excluding r)."""
    rest = [x for x in pooled_rows if x != r]
    if not rest:
        return None
    return min(abs(r - x) for x in rest)


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


def _parse_dcounts(inner: str):
    if inner.strip() in ("none", ""):
        return {}
    out = {}
    for tok in inner.split():
        m = re.match(r"^([+-]?\d+):(\d+)$", tok)
        if not m:
            return None
        out[int(m.group(1))] = int(m.group(2))
    return out


def parse_m58_bins(txt: str):
    """m15 hist + decile-bin table + dec-1 site match targets from m58.txt."""
    m_h = re.search(r"^hist4 m15: n=(\d+) "
                    r"0:(\d+) 1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) "
                    r"5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+)",
                    txt, re.M)
    if not m_h:
        return None
    hist = {"n": int(m_h.group(1)),
            "counts": {d: int(m_h.group(2 + d)) for d in range(10)}}
    bins = {}
    for dci in range(10):
        m = re.search(rf"^decbin m15 dec={dci}: n=(\d+) deltas=\[([^\]]*)\] "
                      r"min=(\S+) max=(\S+) sum=(-?\d+) "
                      r"pos=(\d+) neg=(\d+)",
                      txt, re.M)
        if not m:
            return None
        dc = _parse_dcounts(m.group(2))
        if dc is None:
            return None
        lo = None if m.group(3) == "None" else int(m.group(3))
        hi = None if m.group(4) == "None" else int(m.group(4))
        bins[dci] = {"n": int(m.group(1)), "counts": dc, "min": lo,
                     "max": hi, "sum": int(m.group(5)),
                     "pos": int(m.group(6)), "neg": int(m.group(7))}
    dec1 = {}
    for m in re.finditer(r"^site51: m15 c=(\d+) r=(\d+) "
                         r"delta=([+-]?\d+) dec=1\b",
                         txt, re.M):
        dec1[(int(m.group(2)), int(m.group(1)))] = int(m.group(3))
    if len(dec1) != 12:
        return None
    return {"hist": hist, "bins": bins, "dec1": dec1}


def seat_of(r: int, c: int, cols, dec_plane, masks):
    """s0-anchored seat of one Y site (DESIGN.md pinned).

    cols: tail-Y column dict for the site's frame (or None ->
    peak/atpeak N/A, synthetic path). dec_plane: (H,W) int
    deciles. masks: {shape: (H,W) bool} or None (carrier N/A).
    Returns dict(band, dec, streak, carrier_in, split701, peak,
    atpeak). Pure function of (plane, sites) for control reuse.
    """
    band = int(ROW_BAND[int(r)])
    dec = int(dec_plane[int(r), int(c)])
    streak = str(int(c)) if int(c) in NAMED9 else "other"
    if masks is None:
        carrier_in, split701 = None, None
    else:
        carrier_in = [rank for rank, s in enumerate(M16_TOP10, 1)
                      if bool(masks[s][int(r), int(c)])]
        split701 = "in" if bool(masks[701][int(r), int(c)]) else "out"
    if cols is None or int(c) not in cols:
        peak, atpeak = None, None
    else:
        prof = cols[int(c)]
        hm = hump_metrics(np.array(prof["rows"], np.int64),
                          np.array(prof["deltas"], np.int64))
        peak, atpeak = hm["peakrow"], (int(r) == hm["peakrow"])
    return {"band": band, "dec": dec, "streak": streak,
            "carrier_in": carrier_in, "split701": split701,
            "peak": peak, "atpeak": atpeak}


def decile_hist(sites, dec_plane):
    """Per-decile histogram over sites (list of (r,c)) on a dec plane.

    Returns dict(counts 0-9, n, dec9share, mode, modeshare, rank_of).
    rank_of(d) = 1 + #{deciles with count strictly greater than d's}.
    Pure function of (plane, sites) for control reuse.
    """
    counts = {d: 0 for d in range(10)}
    for (r, c) in sites:
        counts[int(dec_plane[int(r), int(c)])] += 1
    n = len(sites)
    d9 = counts[9] / n if n else 0.0
    top = max(counts.values()) if n else 0
    modes = sorted(d for d in range(10) if counts[d] == top) if n else []
    mode = modes[-1] if modes else None  # ties -> highest dec, disclosed

    def rank_of(d):
        return 1 + sum(1 for k in range(10) if counts[k] > counts[d])

    return {"counts": counts, "n": n, "dec9share": d9, "mode": mode,
            "modeshare": (top / n if n else 0.0), "modes": modes,
            "rank_of": rank_of}


def tail_y_sites(tail, pr, pc, pl):
    """Sorted (r,c) tail-Y sites of a tail mask."""
    idx = np.nonzero(tail & (pl == 0))[0]
    return sorted((int(pr[o]), int(pc[o])) for o in idx)


def off51_select(sites, dec_plane, maxdec=OFF51_MAXDEC):
    """Off-mode subset of sites (dec <= maxdec), sorted by (dec,col,row).

    Pure function of (plane, sites) for control reuse.
    """
    return sorted(((int(dec_plane[r, c]), c, r) for (r, c) in sites
                   if int(dec_plane[r, c]) <= maxdec))


def col_counts(sites):
    """{col: n} over sites (list of (r,c)), sorted by col.

    Pure function of sites for control reuse.
    """
    out = {}
    for (_r, c) in sites:
        out[int(c)] = out.get(int(c), 0) + 1
    return dict(sorted(out.items()))


def band_hist(sites):
    """{band: n} over sites (list of (r,c)) via ROW_BAND.

    Pure function of sites for control reuse.
    """
    out = {}
    for (r, _c) in sites:
        b = int(ROW_BAND[int(r)])
        out[b] = out.get(b, 0) + 1
    return dict(sorted(out.items()))


def bin_sign_rows(sites, dec_plane, deltas):
    """Per-decile sign rows over sites (list of (r,c)).

    dec_plane: (H,W) int deciles. deltas: {(r,c): delta}.
    Returns {dec: {n, counts, min, max, sum, pos, neg, posshare}}
    for dec 0-9 (posshare None when n==0). Pure function of
    (plane, sites, deltas) for control reuse.
    """
    out = {}
    for dci in range(10):
        ds = [deltas[(r, c)] for (r, c) in sites
              if int(dec_plane[int(r), int(c)]) == dci]
        if ds:
            v, cnt = np.unique(np.array(ds, np.int64), return_counts=True)
            dc = {int(x): int(n) for x, n in zip(v, cnt)}
            npos = sum(1 for x in ds if x > 0)
            nneg = sum(1 for x in ds if x < 0)
            out[dci] = {"n": len(ds), "counts": dc, "min": min(ds),
                        "max": max(ds), "sum": sum(ds), "pos": npos,
                        "neg": nneg, "posshare": npos / len(ds)}
        else:
            out[dci] = {"n": 0, "counts": {}, "min": None, "max": None,
                        "sum": 0, "pos": 0, "neg": 0, "posshare": None}
    return out


def col_sign_rows(sites, deltas):
    """Per-column sign rows over sites (list of (r,c)).

    deltas: {(r,c): delta}. Returns {col: {n, pos, neg, posshare,
    min, max, sum}} sorted by col. Pure function of (sites,
    deltas) for control reuse.
    """
    tmp = {}
    for (r, c) in sites:
        tmp.setdefault(int(c), []).append(deltas[(r, c)])
    out = {}
    for col in sorted(tmp):
        ds = tmp[col]
        npos = sum(1 for x in ds if x > 0)
        out[col] = {"n": len(ds), "pos": npos,
                    "neg": sum(1 for x in ds if x < 0),
                    "posshare": npos / len(ds), "min": min(ds),
                    "max": max(ds), "sum": sum(ds)}
    return out


def col_mode_rows(sites, dec_plane, deltas):
    """Per-column modal decile + modal sign over sites (list of (r,c)).

    Modal decile ties -> highest dec (decile_hist convention);
    pos==neg -> modesign 'tie'. Returns {col: {n, modedec,
    modedec_n, modedec_share, modesign, modesign_n,
    modesign_share}} sorted by col. Pure function of (plane,
    sites, deltas) for control reuse.
    """
    tmp = {}
    for (r, c) in sites:
        tmp.setdefault(int(c), []).append(
            (int(dec_plane[int(r), int(c)]), deltas[(r, c)]))
    out = {}
    for col in sorted(tmp):
        rows = tmp[col]
        n = len(rows)
        dc = {}
        for d, _ in rows:
            dc[d] = dc.get(d, 0) + 1
        top = max(dc.values())
        modedec = max(d for d, k in dc.items() if k == top)
        npos = sum(1 for _, x in rows if x > 0)
        nneg = sum(1 for _, x in rows if x < 0)
        if npos > nneg:
            ms, msn = "pos", npos
        elif nneg > npos:
            ms, msn = "neg", nneg
        else:
            ms, msn = "tie", npos
        out[col] = {"n": n, "modedec": modedec, "modedec_n": top,
                    "modedec_share": top / n, "modesign": ms,
                    "modesign_n": msn, "modesign_share": msn / n}
    return out


def _deltamap(cols):
    out = {}
    for col, prof in cols.items():
        for r, d in zip(prof["rows"], prof["deltas"]):
            out[(r, col)] = d
    return out


def _dmap(cols):
    out = {}
    for col in sorted(cols):
        rows = cols[col]["rows"]
        if len(rows) == 1:
            out[(rows[0], col)] = (None, None, None)
            continue
        dd, lo, hi = far_info(rows)
        for r, d, l, h in zip(rows, dd, lo, hi):
            out[(r, col)] = (d, l, h)
    return out


def task1_sign_lines(t0, t15, pr, pc, pl, cols0, cols15, dec_s0,
                     masks, d0, d15, mask0, mask15, tgt):
    """Task 1 receipt lines: binsign + dec-1 sites + background."""
    L = []
    canon = []
    s0sites = tail_y_sites(t0, pr, pc, pl)
    m15sites = tail_y_sites(t15, pr, pc, pl)
    deltamap = _deltamap(cols15)
    # hist m15 (guard input): recomputed + M58 match flags
    hh = decile_hist(m15sites, dec_s0)
    cc = hh["counts"]
    row = " ".join(f"{d}:{cc[d]}" for d in range(10))
    want_txt = tgt["hist"]
    want_des = M58_HIST_M15
    m_txt = (hh["n"] == want_txt["n"] and cc == want_txt["counts"])
    m_des = (hh["n"] == want_des["n"] and cc == want_des["counts"])
    L.append(f"hist m15: n={hh['n']} {row} "
             f"dec9={cc[9]}/{hh['n']} "
             f"({hh['dec9share']:.4f}) mode={hh['mode']} "
             f"m58txt_match={m_txt} design_match={m_des}")
    canon.append(L[-1])
    # binsign: per-bin n + pos/neg + pos share + delta min/max/sum
    brows = bin_sign_rows(m15sites, dec_s0, deltamap)
    for dci in range(10):
        b = brows[dci]
        want_txt = tgt["bins"][dci]
        want_des = M58_DECBIN[dci]
        dc = ("none" if not b["counts"] else
              " ".join(f"{x}:{b['counts'][x]}" for x in sorted(b["counts"])))
        ps = "n/a" if b["posshare"] is None else f"{b['posshare']:.4f}"
        m_txt = (b["n"] == want_txt["n"] and b["counts"] == want_txt["counts"]
                 and b["min"] == want_txt["min"] and b["max"] == want_txt["max"]
                 and b["sum"] == want_txt["sum"] and b["pos"] == want_txt["pos"]
                 and b["neg"] == want_txt["neg"])
        m_des = (b["n"] == want_des[0] and b["counts"] == want_des[1]
                 and b["min"] == want_des[2] and b["max"] == want_des[3]
                 and b["sum"] == want_des[4] and b["pos"] == want_des[5]
                 and b["neg"] == want_des[6])
        L.append(f"binsign m15 dec={dci}: n={b['n']} pos={b['pos']} "
                 f"neg={b['neg']} posshare={ps} min={b['min']} "
                 f"max={b['max']} sum={b['sum']} deltas=[{dc}] "
                 f"m58txt_match={m_txt} design_match={m_des}")
        canon.append(L[-1])
    allpos = sorted(d for d in range(10)
                    if brows[d]["n"] > 0 and brows[d]["neg"] == 0)
    allpos10 = sorted(d for d in allpos if brows[d]["n"] >= 10)
    L.append(f"binsign allpos: decs={allpos} n10={allpos10} "
             f"(H2/H3: dec-1 all-pos? unique at n>=10?)")
    canon.append(L[-1])
    # dec-1 site table: the 12 sites' (row,col)/delta + seats + d
    dmap = _dmap(cols15)
    dec1 = sorted((r, c) for (r, c) in m15sites
                  if int(dec_s0[r, c]) == 1)
    L.append(f"dec1 summary: n={len(dec1)} (want 12)")
    canon.append(L[-1])
    for (r, c) in sorted(dec1, key=lambda t: (t[1], t[0])):
        st = seat_of(r, c, cols15, dec_s0, masks)
        cin = ("none" if not st["carrier_in"]
               else ",".join(str(x) for x in st["carrier_in"]))
        d, lo, hi = dmap[(r, c)]
        L.append(f"dec1 site: m15 c={c} r={r} delta={deltamap[(r, c)]:+d} "
                 f"dec=1 band={st['band']} streak={st['streak']} "
                 f"carrier_in=[{cin}] split701={st['split701']} "
                 f"peak={st['peak']} atpeak={st['atpeak']} "
                 f"d={d} lo={lo} hi={hi}")
        canon.append(L[-1])
    dec1set = {(r, c): deltamap[(r, c)] for (r, c) in dec1}
    m_txt = dec1set == tgt["dec1"]
    m_des = dec1set == M58_DEC1
    L.append(f"dec1 setguard: m58txt_match={m_txt} design_match={m_des}")
    canon.append(L[-1])
    # background: dec-1 12/12 vs M19 P(d>0) + pooled off-51 + dec-9
    p0 = float((d0[mask0] > 0).mean())
    p15 = float((d15[mask15] > 0).mean())
    off = off51_select(m15sites, dec_s0)
    offrc = [(r, c) for (dec, c, r) in off]
    offpos = sum(1 for (r, c) in offrc if deltamap[(r, c)] > 0)
    offneg = sum(1 for (r, c) in offrc if deltamap[(r, c)] < 0)
    offsum = sum(deltamap[(r, c)] for (r, c) in offrc)
    b1, b9 = brows[1], brows[9]
    L.append(f"background dec1: n={b1['n']} pos={b1['pos']} neg={b1['neg']} "
             f"posshare={b1['posshare']:.4f} sum={b1['sum']:+d}")
    canon.append(L[-1])
    L.append(f"background m19: s0_P={p0:.4f} (want "
             f"{M19_POSRATE['s0']}) m15_P={p15:.4f} (want "
             f"{M19_POSRATE['m15']})")
    canon.append(L[-1])
    L.append(f"background off51: n={len(offrc)} pos={offpos} neg={offneg} "
             f"posshare={offpos / len(offrc) if offrc else 0:.4f} "
             f"sum={offsum:+d} (M58 want "
             f"{M58_OFF51_POSNEG[0]}/{M58_OFF51_POSNEG[1]})")
    canon.append(L[-1])
    L.append(f"background dec9: n={b9['n']} pos={b9['pos']} neg={b9['neg']} "
             f"posshare={b9['posshare']:.4f} sum={b9['sum']:+d} "
             f"(M58 want {M58_DEC9_POSNEG[0]}/{M58_DEC9_POSNEG[1]})")
    canon.append(L[-1])
    info = {"hist": hh, "brows": brows, "dec1": dec1, "off": off,
            "s0sites": s0sites, "m15sites": m15sites,
            "offposneg": (offpos, offneg)}
    return L, canon, info


def task2_colsign_lines(m15sites, cols0, cols15, dec_s0, brows):
    """Task 2 receipt lines: colsign + bincol + colmode.

    brows: bin_sign_rows output over m15 tail-Y (Task 1 info).
    """
    L = []
    canon = []
    deltamap = _deltamap(cols15)
    # colsign: pos/neg splits per column over the 33 union cols (m15)
    allcols = sorted(set(cols0) | set(cols15))
    L.append(f"colsign union: ncols={len(allcols)} cols={allcols}")
    canon.append(L[-1])
    crows = col_sign_rows(m15sites, deltamap)
    for col in allcols:
        s0n = len(cols0.get(col, {"rows": []})["rows"])
        if col in crows:
            b = crows[col]
            members = sorted((r, c2) for (r, c2) in m15sites if c2 == col)
            det = " ".join(f"{r}:{deltamap[(r, col)]:+d}/"
                           f"dec{int(dec_s0[r, col])}" for (r, _) in members)
            L.append(f"colsign c={col}: s0_n={s0n} m15_n={b['n']} "
                     f"pos={b['pos']} neg={b['neg']} "
                     f"posshare={b['posshare']:.4f} min={b['min']} "
                     f"max={b['max']} sum={b['sum']:+d} "
                     f"sites=[{det}]")
        else:
            L.append(f"colsign c={col}: s0_n={s0n} m15_n=0 pos=0 "
                     f"neg=0 posshare=n/a sites=[none]")
        canon.append(L[-1])
    allpos = sorted(c for c, b in crows.items() if b["neg"] == 0)
    allpos2 = sorted(c for c in allpos if crows[c]["n"] >= 2)
    split2 = sorted(c for c, b in crows.items()
                    if b["n"] >= 2 and b["neg"] > 0)
    L.append(f"colsign allpos: cols={allpos} n2={allpos2} "
             f"split_n2={split2} (H6 input)")
    canon.append(L[-1])
    b312 = crows.get(312)
    if b312 is not None:
        L.append(f"colsign c312: m15_n={b312['n']} pos={b312['pos']} "
                 f"neg={b312['neg']} posshare={b312['posshare']:.4f} "
                 f"(H4: want split)")
        canon.append(L[-1])
    null = {c: crows[c] for c in NULL4_COLS if c in crows}
    nnull = sum(b["n"] for b in null.values())
    pnull = sum(b["pos"] for b in null.values())
    L.append(f"colsign null4: cols={list(NULL4_COLS)} m15_n={nnull} "
             f"pos={pnull} neg={nnull - pnull} "
             f"posshare={pnull / nnull if nnull else 0:.4f} "
             f"(H5: want split)")
    canon.append(L[-1])
    named = {c: crows[c] for c in NAMED9 if c in crows}
    nrow = " ".join(f"{c}:{named[c]['pos']}/{named[c]['neg']}"
                    for c in sorted(named))
    L.append(f"colsign named9: {nrow if nrow else 'none'} "
             f"(pos/neg per named streak col)")
    canon.append(L[-1])
    # bincol: dec-1's 8 columns vs other bins' columns
    dec1cols = sorted({c for (r, c) in m15sites
                       if int(dec_s0[r, c]) == 1})
    L.append(f"bincol dec1cols: n={len(dec1cols)} cols={dec1cols} "
             f"(want 8)")
    canon.append(L[-1])
    for col in dec1cols:
        per = {}
        negper = {}
        for (r, c) in m15sites:
            if c != col:
                continue
            d = int(dec_s0[r, c])
            per[d] = per.get(d, 0) + 1
            if deltamap[(r, c)] < 0:
                negper[d] = negper.get(d, 0) + 1
        brow = " ".join(f"d{d}:{per[d]}" for d in sorted(per))
        nrow = ("none" if not negper else
                " ".join(f"d{d}:{negper[d]}" for d in sorted(negper)))
        L.append(f"bincol c={col}: bins=[{brow}] negs=[{nrow}]")
        canon.append(L[-1])
    onset = set(dec1cols)
    for dci in range(10):
        members = [(r, c) for (r, c) in m15sites
                   if int(dec_s0[r, c]) == dci]
        non = sum(1 for (r, c) in members if c in onset)
        L.append(f"bincol bin d={dci}: n={len(members)} "
                 f"on_dec1cols={non}")
        canon.append(L[-1])
    # colmode: per-column modal decile joined with modal sign (m15)
    mrows = col_mode_rows(m15sites, dec_s0, deltamap)
    for col in allcols:
        if col in mrows:
            m = mrows[col]
            L.append(f"colmode c={col}: m15_n={m['n']} "
                     f"modedec={m['modedec']} "
                     f"({m['modedec_n']}/{m['n']} "
                     f"{m['modedec_share']:.4f}) modesign={m['modesign']} "
                     f"({m['modesign_n']}/{m['n']} "
                     f"{m['modesign_share']:.4f})")
        else:
            L.append(f"colmode c={col}: m15_n=0 modedec=n/a "
                     f"modesign=n/a")
        canon.append(L[-1])
    info = {"crows": crows, "mrows": mrows, "dec1cols": dec1cols,
            "allpos": allpos, "allpos2": allpos2, "split2": split2}
    return L, canon, info


def main():
    m16d, m15d, m58t, workd, evidd = (Path(a) for a in sys.argv[1:6])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin",
              m15d / "m15-v0.bin", m15d / "m15-mid.bin",
              m15d / "m15-full.bin"]
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    m58b = m58t.read_bytes()
    m58sha = hashlib.sha256(m58b).hexdigest()
    print(f"input {m58t}: bytes={len(m58b)} sha256={m58sha}")
    print(f"m58.txt sha prefix={m58sha[:8]}..{m58sha[-8:]} (tabled)")
    tgt = parse_m58_bins(m58b.decode(errors="replace"))
    if tgt is None:
        print("m58.txt HIST/DECBIN/SITE51 LINES NOT FOUND: STOP, tabled.")
        return
    hh = tgt["hist"]
    row = " ".join(f"{d}:{hh['counts'][d]}" for d in range(10))
    print(f"m58.txt target hist m15: n={hh['n']} {row}")
    for dci in range(10):
        b = tgt["bins"][dci]
        print(f"m58.txt target decbin dec={dci}: n={b['n']} "
              f"min={b['min']} max={b['max']} sum={b['sum']} "
              f"pos={b['pos']} neg={b['neg']}")
    print(f"m58.txt target dec1 sites: n={len(tgt['dec1'])}")

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
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M58 baselines: STOP, tabled.")
        return
    if not carriers_ok:
        print("carrier mismatch: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== R_s vs loo cross-check (s0) ==")
    xd = xdiff(b0, mid0)[0]
    rs = loo.get(0, ("?", "?"))[1]
    print(f"s0: R_s={xd} R_loo={rs} match={xd == rs}")
    if xd != rs:
        print("R_s mismatch on s0: STOP, tabled.")
        return
    print("R_s cross-check: OK")

    print("== cell-7 + tail + column guard (s0 + m15) ==")
    sp0 = interior_sites(v0, mid0, full0, b0)
    sp15 = interior_sites(v015, mid15, full15, b15)
    mask0, d0 = sp0["mask"], sp0["delta"]
    mask15, d15 = sp15["mask"], sp15["delta"]
    t0, _ = tail_bulk_masks(mask0, d0)
    t15, _ = tail_bulk_masks(mask15, d15)
    pl = plane_of_byte()
    pr, pc = plane_coords()
    for tag, sp, dd in (("s0", sp0, d0[mask0]),
                        ("m15", sp15, d15[mask15])):
        print(f"{tag} cell7 n={sp['n']} (want {M19_INTERIOR[tag]})")
        if sp["n"] != M19_INTERIOR[tag]:
            print(f"{tag} COUNT MISMATCH: STOP, tabled.")
            return
    dd0, dd15 = d0[mask0], d15[mask15]
    print(f"s0 delta==0 count={int((dd0 == 0).sum())} (want 0); "
          f"m15 delta==0 count={int((dd15 == 0).sum())} (want 0)")
    if int((dd0 == 0).sum()) != 0 or int((dd15 == 0).sum()) != 0:
        print("delta==0 MISMATCH: STOP, tabled.")
        return
    for tag, dd in (("s0", dd0), ("m15", dd15)):
        p = float((dd > 0).mean())
        print(f"{tag} P(d>0)={p:.4f} (M19/M20 want {M19_POSRATE[tag]})")
        if float(f"{p:.4f}") != M19_POSRATE[tag]:
            print(f"{tag} P(d>0) MISMATCH: STOP, tabled.")
            return
    for tag, t, dd in (("s0", t0, d0), ("m15", t15, d15)):
        nt = int(t.sum())
        ad = np.abs(dd[t]).astype(np.int16)
        n815 = int(((ad >= 8) & (ad < 16)).sum())
        n16p = int((ad >= 16).sum())
        mx = int(ad.max())
        print(f"{tag} tail n={nt} (want {M20_TAIL[tag]}); "
              f"8-15={n815} 16+={n16p} "
              f"(want {M20_TAIL_SUB[tag][0]}+{M20_TAIL_SUB[tag][1]}); "
              f"max={mx} (want {M20_TAIL_MAX[tag]})")
        if (nt != M20_TAIL[tag] or (n815, n16p) != M20_TAIL_SUB[tag]
                or mx != M20_TAIL_MAX[tag]):
            print(f"{tag} TAIL MISMATCH: STOP, tabled.")
            return
    for tag, t in (("s0", t0), ("m15", t15)):
        pp = pl[t]
        print(f"{tag} tail planes: Y={int((pp == 0).sum())} "
              f"U={int((pp == 1).sum())} V={int((pp == 2).sum())}")
        if tag == "s0" and (int((pp == 0).sum()), int((pp == 1).sum()),
                            int((pp == 2).sum())) != (102, 0, 0):
            print("s0 TAIL-PLANE MISMATCH: STOP, tabled.")
            return
        if tag == "m15" and (int((pp == 0).sum()), int((pp == 1).sum()),
                             int((pp == 2).sum())) != (134, 0, 0):
            print("m15 TAIL-PLANE MISMATCH: STOP, tabled.")
            return
    cols0 = y_col_dict(t0, pr, pc, pl, d0)
    cols15 = y_col_dict(t15, pr, pc, pl, d15)
    for tag, cols in (("s0", cols0), ("m15", cols15)):
        for col in sorted(COL_GUARD[tag]):
            want = COL_GUARD[tag][col]
            prof = cols.get(col, {"rows": [], "deltas": []})
            rows = prof["rows"]
            n = len(rows)
            mn = min(rows) if rows else -1
            mx = max(rows) if rows else -1
            sm = int(sum(prof["deltas"])) if rows else 0
            ok = (n, mn, mx, sm) == want
            print(f"{tag} colguard c={col}: n={n} rows=[{mn},{mx}] "
                  f"sum={sm} (want n={want[0]} rows=[{want[1]},{want[2]}] "
                  f"sum={want[3]}) match={ok}")
            if not ok:
                print(f"{tag} c={col} COLUMN MISMATCH: STOP, tabled.")
                return
    print(f"s0 named-col tail bytes n={sum(len(cols0.get(c, {'rows': []})['rows']) for c in NAMED8)} "
          f"(want 65)")
    print(f"m15 named-col tail bytes n={sum(len(cols15.get(c, {'rows': []})['rows']) for c in NAMED8)} "
          f"(want 68)")
    print(f"self Jaccard={jaccard(t0, t0):.4f} (want 1.0000)")

    print("== s0 P1 + carrier masks ==")
    dec_s0, qs, masks, checks = compute_dec_masks(m16d, mid0, b0)
    qe = " ".join(str(int(round(float(x)))) for x in qs)
    print(f"s0 P1 edges rounded: {qe} (want {M18_P1_EDGE_S0})")
    if qe != M18_P1_EDGE_S0:
        print("P1 EDGE MISMATCH: STOP, tabled.")
        return
    for rank, s, nrem, bd, ok in checks:
        print(f"carrier rank {rank} shape {s}: removedYpx={nrem} bands={bd} "
              f"match={ok}")
        if not ok:
            print("CARRIER MASK MISMATCH: STOP, tabled.")
            return

    print("== Task 1: bin-sign reproduction (binsign + dec1 + bg) ==")
    t1, canon1, sign1 = task1_sign_lines(t0, t15, pr, pc, pl,
                                         cols0, cols15, dec_s0,
                                         masks, d0, d15, mask0, mask15, tgt)
    for ln in t1:
        print(ln)
    # bin guard: hist m15 + all 10 bins + dec-1 set value-exact
    brows = sign1["brows"]
    hh = sign1["hist"]
    okh = (hh["n"] == tgt["hist"]["n"]
           and hh["counts"] == tgt["hist"]["counts"]
           and hh["n"] == M58_HIST_M15["n"]
           and hh["counts"] == M58_HIST_M15["counts"])
    print(f"hist-guard: m15_match={okh}")
    okb = True
    for dci in range(10):
        b = brows[dci]
        wt, wd = tgt["bins"][dci], M58_DECBIN[dci]
        m = (b["n"] == wt["n"] and b["counts"] == wt["counts"]
             and b["min"] == wt["min"] and b["max"] == wt["max"]
             and b["sum"] == wt["sum"] and b["pos"] == wt["pos"]
             and b["neg"] == wt["neg"]
             and b["n"] == wd[0] and b["counts"] == wd[1]
             and b["min"] == wd[2] and b["max"] == wd[3]
             and b["sum"] == wd[4] and b["pos"] == wd[5]
             and b["neg"] == wd[6])
        print(f"bin-guard dec={dci}: match={m}")
        if not m:
            okb = False
    dec1set = {(r, c): _deltamap(cols15)[(r, c)]
               for (r, c) in sign1["dec1"]}
    oks = dec1set == tgt["dec1"] == M58_DEC1
    print(f"dec1-guard: set_match={oks}")
    if not (okh and okb and oks):
        print("M58 BIN/HIST/DEC1 MISMATCH: STOP, tabled.")
        return

    print("== Task 2: sign-by-column census (colsign+bincol+colmode) ==")
    t2b, canon2, geo = task2_colsign_lines(sign1["m15sites"], cols0,
                                           cols15, dec_s0, brows)
    for ln in t2b:
        print(ln)
    # H-bar inputs (tabled, no verdicts)
    b1 = brows[1]
    allpos10 = sorted(d for d in range(10)
                      if brows[d]["n"] >= 10 and brows[d]["neg"] == 0)
    c312 = geo["crows"].get(312, {"n": 0, "pos": 0, "neg": 0})
    nnull = sum(geo["crows"][c]["n"] for c in NULL4_COLS
                if c in geo["crows"])
    pnull = sum(geo["crows"][c]["pos"] for c in NULL4_COLS
                if c in geo["crows"])
    print(f"bars: bin_match={okb} dec1_pos={b1['pos']}/{b1['n']} "
          f"allpos_n10={allpos10} "
          f"c312_posneg={c312['pos']}/{c312['neg']} "
          f"null4_posneg={pnull}/{nnull - pnull} "
          f"allpos_n2={geo['allpos2']} split_n2n={len(geo['split2'])}")

    print("== determinism re-run (Task 1 on s0+m15, fresh loads) ==")
    v0b, mid0b, full0b, b0b = load_triplet(m16d, 0)
    sp0b = interior_sites(v0b, mid0b, full0b, b0b)
    sp15b = interior_sites(v015, mid15, full15, b15)
    mask0b, d0b = sp0b["mask"], sp0b["delta"]
    mask15b, d15b = sp15b["mask"], sp15b["delta"]
    t0b, _ = tail_bulk_masks(mask0b, d0b)
    t15b, _ = tail_bulk_masks(mask15b, d15b)
    cols0b = y_col_dict(t0b, pr, pc, pl, d0b)
    cols15b = y_col_dict(t15b, pr, pc, pl, d15b)
    _, canon1b, _sign1b = task1_sign_lines(t0b, t15b, pr, pc, pl,
                                           cols0b, cols15b, dec_s0,
                                           masks, d0b, d15b, mask0b,
                                           mask15b, tgt)
    canon_pass1 = canon1
    canon_pass2 = canon1b
    h1 = hashlib.sha256(("\n".join(canon_pass1) + "\n").encode()).hexdigest()
    h2 = hashlib.sha256(("\n".join(canon_pass2) + "\n").encode()).hexdigest()
    print(f"canon pass1: {h1}")
    print(f"canon pass2: {h2}")
    print(f"canon identical={h1 == h2} lines={len(canon_pass1)}")
    print(f"cell identical={sp0['n'] == sp0b['n'] and sp15['n'] == sp15b['n']} "
          f"tail identical={int(t0.sum()) == int(t0b.sum()) and int(t15.sum()) == int(t15b.sum())}")

    print("== PNG sign map (m15 tail-Y by bin-1/sign) ==")
    img = Image.new("RGB", (320, 224), (0, 0, 0))
    px = img.load()
    deltamap = _deltamap(cols15)
    m15sites = sign1["m15sites"]
    for (r, c) in m15sites:
        x, y = c // 2, r // 2
        is1 = int(dec_s0[r, c]) == 1
        pos = deltamap[(r, c)] > 0
        if is1 and pos:
            col3 = (255, 255, 0)  # yellow: dec-1 pos
        elif is1:
            col3 = (255, 165, 0)  # orange: dec-1 neg (expect 0)
        elif pos:
            col3 = (0, 255, 0)  # green: other-bin pos
        else:
            col3 = (255, 0, 0)  # red: other-bin neg
        cur = px[x, y]
        # precedence: yellow > orange > red > green > black
        pri = {(0, 0, 0): 0, (0, 255, 0): 1, (255, 0, 0): 2,
               (255, 165, 0): 3, (255, 255, 0): 4}
        if pri[col3] >= pri.get(cur, 0):
            px[x, y] = col3
    pngp = workd / "m59-signmap.png"
    img.save(pngp)
    h3 = allpos10 == [1]
    print(f"signmap: {pngp} bytes={pngp.stat().st_size} "
          f"(evidence iff H3 dec1unique10; allpos_n10={allpos10} "
          f"h3={h3})")

    wall = time.time() - t_start
    print(f"== done: wall={wall:.1f}s ==")


if __name__ == "__main__":
    main()
