#!/usr/bin/env python3
"""M60 c312 unique sign-split column: unanimity census + span join (offline).

Usage: m60.py M16_DIR M15_DIR M59TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, and the M59
receipt (column-sign table to reproduce); raw XFB dumps, 573440 B =
640x448 YUYV. Read-only inputs; receipt text goes to stdout (redirect
to WORK_DIR/m60.txt); PNG unanimity map to WORK_DIR (evidence copy
iff the DESIGN.md rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: unanimity reproduction (unanim + c312 rows/runs + span)
  2: split-vs-unanimous census (spanjoin + decmix + dprof)
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
# M59 pins: m15 tail-Y column-sign table + c312 site detail
# (recompute must match exactly or stop).
# col -> (s0_n, m15_n, pos, neg, min, max, sum); None min/max when m15_n==0.
M59_COLSIGN = {
    38: (1, 0, 0, 0, None, None, 0),
    65: (0, 2, 0, 2, -17, -8, -25),
    76: (0, 1, 0, 1, -35, -35, -35),
    257: (10, 10, 10, 0, 8, 20, 172),
    277: (10, 10, 10, 0, 8, 20, 172),
    289: (0, 2, 0, 2, -16, -8, -24),
    292: (1, 0, 0, 0, None, None, 0),
    293: (1, 0, 0, 0, None, None, 0),
    296: (9, 9, 9, 0, 16, 46, 306),
    298: (4, 7, 0, 7, -26, -8, -114),
    299: (0, 1, 0, 1, -36, -36, -36),
    301: (11, 11, 11, 0, 12, 48, 291),
    306: (0, 2, 2, 0, 23, 46, 69),
    307: (1, 1, 1, 0, 9, 9, 9),
    308: (0, 2, 0, 2, -18, -8, -26),
    309: (0, 2, 2, 0, 8, 10, 18),
    310: (0, 1, 1, 0, 10, 10, 10),
    311: (4, 6, 6, 0, 9, 46, 129),
    312: (3, 23, 13, 10, -9, 33, 130),
    313: (4, 5, 5, 0, 17, 29, 113),
    314: (7, 2, 2, 0, 15, 24, 39),
    315: (7, 5, 5, 0, 11, 21, 83),
    316: (1, 0, 0, 0, None, None, 0),
    321: (10, 10, 10, 0, 14, 31, 252),
    332: (2, 0, 0, 0, None, None, 0),
    340: (8, 9, 9, 0, 14, 48, 311),
    341: (0, 1, 0, 1, -9, -9, -9),
    342: (5, 5, 0, 5, -21, -13, -87),
    343: (2, 4, 0, 4, -34, -15, -97),
    344: (0, 1, 1, 0, 8, 8, 8),
    353: (0, 1, 0, 1, -9, -9, -9),
    372: (1, 0, 0, 0, None, None, 0),
    617: (0, 1, 1, 0, 10, 10, 10),
}
M59_UNION_COLS = sorted(M59_COLSIGN)
# c312 sites: {(row, col): (delta, dec)} x23, row order (M59 colsign pins).
M59_C312 = {(316, 312): (11, 7), (317, 312): (20, 5),
            (318, 312): (19, 1), (319, 312): (9, 1),
            (341, 312): (14, 1), (342, 312): (22, 3),
            (343, 312): (9, 3), (353, 312): (-9, 0),
            (354, 312): (-9, 0), (355, 312): (-9, 0),
            (356, 312): (-9, 0), (362, 312): (-8, 3),
            (363, 312): (-8, 4), (364, 312): (-9, 3),
            (365, 312): (-9, 0), (366, 312): (-9, 0),
            (367, 312): (-8, 0), (369, 312): (14, 3),
            (373, 312): (33, 1), (374, 312): (15, 1),
            (377, 312): (18, 0), (378, 312): (23, 1),
            (379, 312): (10, 3)}
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


def _parse_colsign_sites(inner: str):
    if inner.strip() in ("none", ""):
        return {}
    out = {}
    for tok in inner.split():
        m = re.match(r"^(\d+):([+-]?\d+)/dec(\d+)$", tok)
        if not m:
            return None
        out[(int(m.group(1)), None)] = (int(m.group(2)), int(m.group(3)))
    return out


def parse_m59_colsign(txt: str):
    """Column-sign table + c312 site match targets from m59.txt."""
    m_u = re.search(r"^colsign union: ncols=(\d+) cols=\[([^\]]*)\]",
                    txt, re.M)
    if not m_u:
        return None
    union = [int(x) for x in m_u.group(2).split(",") if x.strip() != ""]
    cols = {}
    for col in union:
        m = re.search(rf"^colsign c={col}: s0_n=(\d+) m15_n=(\d+) "
                      r"pos=(\d+) neg=(\d+) posshare=(\S+)"
                      rf"(?: min=(\S+) max=(\S+) sum=([+-]?\d+))? "
                      r"sites=\[([^\]]*)\]",
                      txt, re.M)
        if not m:
            return None
        m15_n = int(m.group(2))
        if m15_n == 0:
            cols[col] = {"s0_n": int(m.group(1)), "m15_n": 0,
                         "pos": 0, "neg": 0, "min": None,
                         "max": None, "sum": 0, "sites": {}}
            continue
        det = _parse_colsign_sites(m.group(9))
        if det is None:
            return None
        sites = {(r, col): dd for ((r, _), dd) in det.items()}
        cols[col] = {"s0_n": int(m.group(1)), "m15_n": m15_n,
                     "pos": int(m.group(3)), "neg": int(m.group(4)),
                     "min": int(m.group(6)), "max": int(m.group(7)),
                     "sum": int(m.group(8)), "sites": sites}
    if 312 not in cols or len(cols[312]["sites"]) != 23:
        return None
    return {"union": union, "cols": cols, "c312": cols[312]["sites"]}


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


def unanimity_rows(sites, deltas):
    """Per-column unanimity rows over sites (list of (r,c)).

    deltas: {(r,c): delta}. Returns {col: {n, pos, neg, posshare,
    min, max, sum, uclass}} sorted by col (uclass in
    all-pos/all-neg/split; split iff pos>0 and neg>0).
    Pure function of (sites, deltas) for control reuse.
    """
    tmp = {}
    for (r, c) in sites:
        tmp.setdefault(int(c), []).append(deltas[(r, c)])
    out = {}
    for col in sorted(tmp):
        ds = tmp[col]
        npos = sum(1 for x in ds if x > 0)
        nneg = sum(1 for x in ds if x < 0)
        if npos > 0 and nneg > 0:
            uc = "split"
        elif npos == len(ds):
            uc = "all-pos"
        else:
            uc = "all-neg"
        out[col] = {"n": len(ds), "pos": npos, "neg": nneg,
                    "posshare": npos / len(ds), "min": min(ds),
                    "max": max(ds), "sum": sum(ds), "uclass": uc}
    return out


def span_rows(sites, dec_plane):
    """Per-column span rows over sites (list of (r,c)).

    dec_plane: (H,W) int deciles. Returns {col: {n, rowmin,
    rowmax, rowspan, decspan, dechist, decmaxshare}} sorted by
    col (rowspan = rowmax-rowmin; decspan = distinct deciles).
    Pure function of (plane, sites) for control reuse.
    """
    tmp = {}
    for (r, c) in sites:
        tmp.setdefault(int(c), []).append(
            (int(r), int(dec_plane[int(r), int(c)])))
    out = {}
    for col in sorted(tmp):
        rows = tmp[col]
        n = len(rows)
        rs = sorted(r for r, _ in rows)
        dc = {}
        for _, d in rows:
            dc[d] = dc.get(d, 0) + 1
        top = max(dc.values())
        out[col] = {"n": n, "rowmin": rs[0], "rowmax": rs[-1],
                    "rowspan": rs[-1] - rs[0], "decspan": len(dc),
                    "dechist": dict(sorted(dc.items())),
                    "decmaxshare": top / n}
    return out


def runs_rows(rows_sorted, deltas):
    """Sign runs over one column's sites sorted by row.

    rows_sorted: sorted [(r,c)] of one column; deltas:
    {(r,c): delta}. Returns [(sign, rstart, rend, length)] in
    row order (sign in pos/neg). Pure function of (rows,
    deltas) for control reuse.
    """
    runs = []
    for (r, c) in rows_sorted:
        s = "pos" if deltas[(r, c)] > 0 else "neg"
        if runs and runs[-1][0] == s:
            runs[-1][2] = int(r)
            runs[-1][3] += 1
        else:
            runs.append([s, int(r), int(r), 1])
    return [(s, a, b, n) for (s, a, b, n) in runs]


def dprof_rows(sites):
    """Per-column d-profile rows over sites (list of (r,c)).

    Returns {col: {n, dhist, na, dmax, dmode}} via `far_info`
    on sorted rows (singleton -> na=1, dmax/dmode None; dmode
    ties -> smallest d). Pure function of sites for control
    reuse.
    """
    tmp = {}
    for (r, c) in sites:
        tmp.setdefault(int(c), []).append(int(r))
    out = {}
    for col in sorted(tmp):
        rows = sorted(tmp[col])
        if len(rows) == 1:
            out[col] = {"n": 1, "dhist": {}, "na": 1,
                        "dmax": None, "dmode": None}
            continue
        dd, _lo, _hi = far_info(rows)
        hist = {}
        for d in dd:
            hist[d] = hist.get(d, 0) + 1
        top = max(hist.values())
        out[col] = {"n": len(rows), "dhist": dict(sorted(hist.items())),
                    "na": 0, "dmax": max(hist),
                    "dmode": min(d for d, k in hist.items() if k == top)}
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


def task1_unanim_lines(t0, t15, pr, pc, pl, cols0, cols15, dec_s0,
                       masks, d0, d15, mask0, mask15, tgt):
    """Task 1 receipt lines: unanim + c312 rows/runs + span."""
    L = []
    canon = []
    s0sites = tail_y_sites(t0, pr, pc, pl)
    m15sites = tail_y_sites(t15, pr, pc, pl)
    deltamap = _deltamap(cols15)
    # unanim: per-column n + pos/neg + class over the 33 union cols
    allcols = sorted(set(cols0) | set(cols15))
    L.append(f"unanim union: ncols={len(allcols)} cols={allcols}")
    canon.append(L[-1])
    urows = unanimity_rows(m15sites, deltamap)
    for col in allcols:
        s0n = len(cols0.get(col, {"rows": []})["rows"])
        want_txt = tgt["cols"].get(col)
        want_des = M59_COLSIGN.get(col)
        if col in urows:
            b = urows[col]
            m_txt = (want_txt is not None and s0n == want_txt["s0_n"]
                     and b["n"] == want_txt["m15_n"]
                     and b["pos"] == want_txt["pos"]
                     and b["neg"] == want_txt["neg"]
                     and b["min"] == want_txt["min"]
                     and b["max"] == want_txt["max"]
                     and b["sum"] == want_txt["sum"])
            m_des = (want_des is not None and s0n == want_des[0]
                     and b["n"] == want_des[1] and b["pos"] == want_des[2]
                     and b["neg"] == want_des[3] and b["min"] == want_des[4]
                     and b["max"] == want_des[5] and b["sum"] == want_des[6])
            L.append(f"unanim c={col}: s0_n={s0n} m15_n={b['n']} "
                     f"pos={b['pos']} neg={b['neg']} "
                     f"posshare={b['posshare']:.4f} min={b['min']} "
                     f"max={b['max']} sum={b['sum']:+d} "
                     f"class={b['uclass']} "
                     f"m59txt_match={m_txt} design_match={m_des}")
        else:
            m_txt = (want_txt is not None and s0n == want_txt["s0_n"]
                     and want_txt["m15_n"] == 0)
            m_des = (want_des is not None and s0n == want_des[0]
                     and want_des[1] == 0)
            L.append(f"unanim c={col}: s0_n={s0n} m15_n=0 pos=0 "
                     f"neg=0 posshare=n/a class=s0-only "
                     f"m59txt_match={m_txt} design_match={m_des}")
        canon.append(L[-1])
    split = sorted(c for c, b in urows.items() if b["uclass"] == "split")
    split2 = sorted(c for c in split if urows[c]["n"] >= 2)
    allpos2 = sorted(c for c, b in urows.items()
                     if b["uclass"] == "all-pos" and b["n"] >= 2)
    allneg2 = sorted(c for c, b in urows.items()
                     if b["uclass"] == "all-neg" and b["n"] >= 2)
    L.append(f"unanim split: cols={split} n2={split2} "
             f"(H2/H3: c312 splits? only split at n>=2?)")
    canon.append(L[-1])
    L.append(f"unanim unan2: allpos={allpos2} allneg={allneg2}")
    canon.append(L[-1])
    # c312 row table: the 23 sites in row order + runs + d/lo/hi
    dmap = _dmap(cols15)
    c312rows = sorted((r, c) for (r, c) in m15sites if c == 312)
    L.append(f"c312 summary: n={len(c312rows)} (want 23)")
    canon.append(L[-1])
    for (r, c) in c312rows:
        dd = deltamap[(r, c)]
        sg = "pos" if dd > 0 else "neg"
        d, lo, hi = dmap[(r, c)]
        L.append(f"c312 site: m15 c=312 r={r} delta={dd:+d} sign={sg} "
                 f"dec={int(dec_s0[r, c])} d={d} lo={lo} hi={hi}")
        canon.append(L[-1])
    runs = runs_rows(c312rows, deltamap)
    rrow = " ".join(f"{s}:{a}-{b}x{n}" for (s, a, b, n) in runs)
    L.append(f"c312 runs: nruns={len(runs)} runs=[{rrow}] "
             f"(H6: 3 runs 7/10/6? r316 in run 1?)")
    canon.append(L[-1])
    c312set = {(r, c): (deltamap[(r, c)], int(dec_s0[r, c]))
               for (r, c) in c312rows}
    m_txt = c312set == tgt["c312"]
    m_des = c312set == M59_C312
    L.append(f"c312 setguard: m59txt_match={m_txt} design_match={m_des}")
    canon.append(L[-1])
    # span: per-column row-span + decile-span + n
    srows = span_rows(m15sites, dec_s0)
    for col in allcols:
        if col in srows:
            s = srows[col]
            dh = " ".join(f"d{d}:{s['dechist'][d]}"
                          for d in sorted(s["dechist"]))
            L.append(f"span c={col}: m15_n={s['n']} "
                     f"rows={s['rowmin']}-{s['rowmax']} "
                     f"rowspan={s['rowspan']} decspan={s['decspan']} "
                     f"dechist=[{dh}] "
                     f"decmaxshare={s['decmaxshare']:.4f}")
        else:
            L.append(f"span c={col}: m15_n=0 rows=n/a rowspan=n/a "
                     f"decspan=n/a dechist=[none]")
        canon.append(L[-1])
    info = {"urows": urows, "srows": srows, "c312rows": c312rows,
            "runs": runs, "s0sites": s0sites, "m15sites": m15sites,
            "split": split, "split2": split2, "allpos2": allpos2,
            "allneg2": allneg2}
    return L, canon, info


def task2_spanjoin_lines(m15sites, cols0, cols15, dec_s0, info1):
    """Task 2 receipt lines: spanjoin + decmix + dprof.

    info1: task1_unanim_lines info (urows + srows over m15 tail-Y).
    """
    L = []
    canon = []
    deltamap = _deltamap(cols15)
    urows = info1["urows"]
    srows = info1["srows"]
    # spanjoin: unanimous vs split columns by row-span + decile-span
    order = sorted(srows, key=lambda c: (-srows[c]["rowspan"], c))
    L.append(f"spanjoin order: cols_by_rowspan_desc={order}")
    canon.append(L[-1])
    for col in order:
        s = srows[col]
        L.append(f"spanjoin c={col}: class={urows[col]['uclass']} "
                 f"m15_n={s['n']} rowspan={s['rowspan']} "
                 f"decspan={s['decspan']}")
        canon.append(L[-1])
    for cls in ("split", "all-pos", "all-neg"):
        grp = sorted(c for c, b in urows.items()
                     if b["uclass"] == cls and b["n"] >= 2)
        rs = sorted(srows[c]["rowspan"] for c in grp)
        ds = sorted(srows[c]["decspan"] for c in grp)
        L.append(f"spanjoin summary class={cls}: ncols={len(grp)} "
                 f"cols={grp} rowspans={rs} decspans={ds}")
        canon.append(L[-1])
    sing = sorted(c for c, b in urows.items() if b["n"] == 1)
    L.append(f"spanjoin summary class=singleton: ncols={len(sing)} "
             f"cols={sing} (rowspan 0 / decspan 1 by construction)")
    canon.append(L[-1])
    # decmix: per-column decile histogram class
    for col in sorted(srows):
        s = srows[col]
        dh = " ".join(f"d{d}:{s['dechist'][d]}"
                      for d in sorted(s["dechist"]))
        L.append(f"decmix c={col}: class={urows[col]['uclass']} "
                 f"m15_n={s['n']} ndec={s['decspan']} hist=[{dh}] "
                 f"maxshare={s['decmaxshare']:.4f}")
        canon.append(L[-1])
    ndec_rank = sorted(srows, key=lambda c: (-srows[c]["decspan"],
                                            -srows[c]["n"], c))
    L.append(f"decmix rank: cols_by_ndec_desc={ndec_rank} "
             f"(H5: c312 unique max at 6?)")
    canon.append(L[-1])
    # dprof: per-column d histogram class (M56 far_info)
    drows = dprof_rows(m15sites)
    for col in sorted(drows):
        p = drows[col]
        dh = ("none" if not p["dhist"] else
              " ".join(f"{d}:{p['dhist'][d]}" for d in sorted(p["dhist"])))
        L.append(f"dprof c={col}: class={urows[col]['uclass']} "
                 f"m15_n={p['n']} dhist=[{dh}] na={p['na']} "
                 f"dmax={p['dmax']} dmode={p['dmode']}")
        canon.append(L[-1])
    info = {"drows": drows}
    return L, canon, info


def main():
    m16d, m15d, m59t, workd, evidd = (Path(a) for a in sys.argv[1:6])
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
    m59b = m59t.read_bytes()
    m59sha = hashlib.sha256(m59b).hexdigest()
    print(f"input {m59t}: bytes={len(m59b)} sha256={m59sha}")
    print(f"m59.txt sha prefix={m59sha[:8]}..{m59sha[-8:]} (tabled)")
    tgt = parse_m59_colsign(m59b.decode(errors="replace"))
    if tgt is None:
        print("m59.txt COLSIGN UNION/COLS LINES NOT FOUND: STOP, tabled.")
        return
    print(f"m59.txt target union: ncols={len(tgt['union'])} "
          f"cols={tgt['union']}")
    for col in sorted(tgt["cols"]):
        b = tgt["cols"][col]
        print(f"m59.txt target colsign c={col}: s0_n={b['s0_n']} "
              f"m15_n={b['m15_n']} pos={b['pos']} neg={b['neg']} "
              f"min={b['min']} max={b['max']} sum={b['sum']}")
    print(f"m59.txt target c312 sites: n={len(tgt['c312'])}")

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
        print("MISMATCH vs M17-M59 baselines: STOP, tabled.")
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

    print("== Task 1: unanimity reproduction (unanim + c312 + span) ==")
    t1, canon1, sign1 = task1_unanim_lines(t0, t15, pr, pc, pl,
                                           cols0, cols15, dec_s0,
                                           masks, d0, d15, mask0, mask15, tgt)
    for ln in t1:
        print(ln)
    # colsign guard: union + all 33 cols + c312 set value-exact
    allcols = sorted(set(cols0) | set(cols15))
    oku = (allcols == tgt["union"] == M59_UNION_COLS)
    print(f"union-guard: match={oku}")
    urows = sign1["urows"]
    okc = True
    for col in allcols:
        s0n = len(cols0.get(col, {"rows": []})["rows"])
        wt = tgt["cols"].get(col)
        wd = M59_COLSIGN.get(col)
        if col in urows:
            b = urows[col]
            m = (wt is not None and wd is not None
                 and s0n == wt["s0_n"] == wd[0]
                 and b["n"] == wt["m15_n"] == wd[1]
                 and b["pos"] == wt["pos"] == wd[2]
                 and b["neg"] == wt["neg"] == wd[3]
                 and b["min"] == wt["min"] == wd[4]
                 and b["max"] == wt["max"] == wd[5]
                 and b["sum"] == wt["sum"] == wd[6])
        else:
            m = (wt is not None and wd is not None
                 and s0n == wt["s0_n"] == wd[0]
                 and wt["m15_n"] == 0 and wd[1] == 0)
        print(f"col-guard c={col}: match={m}")
        if not m:
            okc = False
    c312set = {(r, c): (_deltamap(cols15)[(r, c)], int(dec_s0[r, c]))
               for (r, c) in sign1["c312rows"]}
    oks = c312set == tgt["c312"] == M59_C312
    print(f"c312-guard: set_match={oks}")
    if not (oku and okc and oks):
        print("M59 UNION/COLSIGN/C312 MISMATCH: STOP, tabled.")
        return

    print("== Task 2: split-vs-unanimous census (spanjoin+decmix+dprof) ==")
    t2b, canon2, geo = task2_spanjoin_lines(sign1["m15sites"], cols0,
                                            cols15, dec_s0, sign1)
    for ln in t2b:
        print(ln)
    # H-bar inputs (tabled, no verdicts)
    c312 = urows.get(312, {"n": 0, "pos": 0, "neg": 0})
    s312 = sign1["srows"].get(312, {"rowspan": -1, "decspan": -1})
    print(f"bars: col_match={okc} c312_posneg={c312['pos']}/{c312['neg']} "
          f"split_n2={sign1['split2']} "
          f"c312_rowspan={s312['rowspan']} "
          f"c312_decspan={s312['decspan']} "
          f"c312_runs={[(s, n) for (s, _a, _b, n) in sign1['runs']]} "
          f"c312_dmode={geo['drows'].get(312, {}).get('dmode')}")

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
    _, canon1b, _sign1b = task1_unanim_lines(t0b, t15b, pr, pc, pl,
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

    print("== PNG unanimity map (m15 tail-Y by column class) ==")
    img = Image.new("RGB", (320, 224), (0, 0, 0))
    px = img.load()
    deltamap = _deltamap(cols15)
    m15sites = sign1["m15sites"]
    only_split = sign1["split2"] == [312]
    for (r, c) in m15sites:
        x, y = c // 2, r // 2
        uc = urows[c]["uclass"]
        if uc == "split" and only_split:
            col3 = (255, 255, 0)  # yellow: split column c312
        elif uc == "split":
            col3 = (255, 165, 0)  # orange: split, non-unique (expect 0)
        elif uc == "all-pos":
            col3 = (0, 255, 0)  # green: unanimous-pos column
        else:
            col3 = (255, 0, 0)  # red: unanimous-neg column
        cur = px[x, y]
        # precedence: yellow > orange > red > green > black
        pri = {(0, 0, 0): 0, (0, 255, 0): 1, (255, 0, 0): 2,
               (255, 165, 0): 3, (255, 255, 0): 4}
        if pri[col3] >= pri.get(cur, 0):
            px[x, y] = col3
    pngp = workd / "m60-unanmap.png"
    img.save(pngp)
    h3 = only_split
    print(f"unanmap: {pngp} bytes={pngp.stat().st_size} "
          f"(evidence iff H3 c312unique; split_n2={sign1['split2']} "
          f"h3={h3})")

    wall = time.time() - t_start
    print(f"== done: wall={wall:.1f}s ==")


if __name__ == "__main__":
    main()
