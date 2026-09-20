#!/usr/bin/env python3
"""M56 far-row tail-site census: 289-site reproduction + s0+m15 census (offline).

Usage: m56.py M16_DIR M15_DIR M25TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, and the M25
receipt (c343 rows + 289 site to reproduce); raw XFB dumps, 573440 B =
640x448 YUYV. Read-only inputs; receipt text goes to stdout (redirect
to WORK_DIR/m56.txt); PNG far-row map to WORK_DIR (evidence copy iff
the DESIGN.md rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: 289-site reproduction (c343 table + 289 value row + isolation)
  2: far-row census (census + seats + columns + null set)
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
M25_C343 = {
    "s0": {"n": 2, "rows": [26, 27], "deltas": [-31, -26],
           "holes": "none", "nholes": 0},
    "m15": {"n": 4, "rows": [25, 26, 27, 289],
            "deltas": [-22, -34, -26, -15],
            "holes": "28-288", "nholes": 261},
}
M26_PEAK_C343 = {"s0": (27, -26), "m15": (289, -15)}
M51_TRI_C343 = {"s0": (27, -26, -31, 1), "m15": (289, -15, -22, 1)}
M54_QUAD_C343_M15 = (0.007831, -2.419882, 30.284514)
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


def parse_m25_c343(txt: str):
    """c343 match targets from m25.txt (colguard + prof + holes)."""
    out = {}
    for tag in ("s0", "m15"):
        m_g = re.search(rf"^{tag} colguard c=343: n=(\d+) "
                        r"rows=\[(\-?\d+),(\-?\d+)\] sum=(\-?\d+)",
                        txt, re.M)
        m_p = re.search(rf"^{tag} prof c=343: n=(\d+) "
                        r"rows=\[(\-?\d+),(\-?\d+)\] rowdelta: (.*)$",
                        txt, re.M)
        m_h = re.search(rf"^{tag} prof c=343 holes: (.*)$", txt, re.M)
        if not (m_g and m_p and m_h):
            return None
        rds = {}
        for a, b in re.findall(r"(\d+):(\-?\d+)", m_p.group(4)):
            rds[int(a)] = int(b)
        out[tag] = {"n": int(m_g.group(1)),
                    "min": int(m_g.group(2)), "max": int(m_g.group(3)),
                    "sum": int(m_g.group(4)),
                    "rowdelta": rds, "holes": m_h.group(1).strip()}
    return out


def task1_c343_lines(cols0, cols15):
    """Task 1.1 receipt lines: c343 profiles + argmax + TRI + QUAD."""
    L = []
    canon = []
    for tag, cols in (("s0", cols0), ("m15", cols15)):
        prof = cols.get(343, {"rows": [], "deltas": []})
        rows = prof["rows"]
        deltas = prof["deltas"]
        n = len(rows)
        rarr = np.array(rows, np.int64) if n else np.array([], np.int64)
        darr = np.array(deltas, np.int64) if n else np.array([], np.int64)
        rd = " ".join(f"{r}:{d}" for r, d in zip(rows, deltas))
        L.append(f"c343 {tag} prof: n={n} rows={rows} rowdelta: {rd}")
        canon.append(L[-1])
        L.append(f"c343 {tag} holes: {hole_ranges(rarr)}")
        canon.append(L[-1])
        if n:
            hm = hump_metrics(rarr, darr)
            L.append(f"c343 {tag} argmax: peakrow={hm['peakrow']} "
                     f"peakval={hm['peakval']} k={hm['k']}/n={hm['n']} "
                     f"third={hm['third']}")
            canon.append(L[-1])
            tf = trifit(rarr, darr)
            L.append(f"c343 {tag} TRI: p={tf['p']} h={tf['h']} e={tf['e']} "
                     f"w={tf['w']} flat={tf['flat']}")
            canon.append(L[-1])
            qf = quadfit(rarr, darr)
            if qf is None:
                med = int_median(darr)
                preds = [med] * n
                L.append(f"c343 {tag} QUAD: CONST-fb med={med}")
                canon.append(L[-1])
            else:
                a, b, c = qf
                preds = [rhalf(a * r * r + b * r + c) for r in rows]
                L.append(f"c343 {tag} QUAD: a={a:.6f} b={b:.6f} c={c:.6f}")
                canon.append(L[-1])
            res = [f"{r}:{d}/{p}/{d - p:+d}" for r, d, p in
                   zip(rows, deltas, preds)]
            L.append(f"c343 {tag} QUADres: " + " ".join(res))
            canon.append(L[-1])
        else:
            L.append(f"c343 {tag} argmax: (empty)")
            canon.append(L[-1])
    return L, canon


def s0_status_at(o: int, mask0, d0, tail0):
    """s0 status at an m15-site offset: tail / bulk / noncell."""
    if tail0[o]:
        return "tail", int(abs(int(d0[o])))
    if mask0[o]:
        ad = int(abs(int(d0[o])))
        return "bulk", ad
    return "noncell", None


def task1_289_lines(v0, mid0, full0, v015, mid15, full15,
                    mask0, d0, tail0, mask15, d15, tail15,
                    dec_s0, masks):
    """Task 1.2 + 1.3 receipt lines: 289 value row + isolation."""
    L = []
    canon = []
    r, c = 289, 343
    o = off_y(r, c)
    pl = plane_of_byte()
    pr, pc = plane_coords()
    assert int(pl[o]) == 0 and int(pr[o]) == r and int(pc[o]) == c
    a0 = np.frombuffer(v0, np.uint8).astype(np.int16)
    b0 = np.frombuffer(full0, np.uint8).astype(np.int16)
    a15 = np.frombuffer(v015, np.uint8).astype(np.int16)
    b15 = np.frombuffer(full15, np.uint8).astype(np.int16)
    g0, g15 = int(a0[o] - b0[o]), int(a15[o] - b15[o])
    dm15 = int(d15[o]) if mask15[o] else None
    adm15 = abs(dm15) if dm15 is not None else None
    m15st = "tail" if tail15[o] else ("bulk" if mask15[o] else "noncell")
    s0st, ad0 = s0_status_at(o, mask0, d0, tail0)
    ad0s = str(ad0) if ad0 is not None else "n/a"
    near = ""
    if s0st == "bulk":
        near = " near" if ad0 in (6, 7) else " far"
    L.append(f"site289 offset: o={o} plane={PNAME[int(pl[o])]} rc=({r},{c})")
    canon.append(L[-1])
    L.append(f"site289 values: m15_status={m15st} d_m15={dm15} "
             f"ad_m15={adm15} s0_status={s0st}{near} ad_s0={ad0s}")
    canon.append(L[-1])
    L.append(f"site289 gaps: g_m15={g15} g_s0={g0} "
             f"signed_eq={g15 == g0} abs_eq={abs(g15) == abs(g0)}")
    canon.append(L[-1])

    def sgn(x):
        return "+" if x > 0 else ("-" if x < 0 else "0")

    L.append(f"site289 gapsigns: m15={sgn(g15)} s0={sgn(g0)} "
             f"pair={sgn(g15)}{sgn(g0)}")
    canon.append(L[-1])
    band = int(ROW_BAND[r])
    dec = int(dec_s0[r, c])
    streak = str(c) if c in NAMED9 else "other"
    L.append(f"site289 seats: band={band} dec={dec} streak={streak}")
    canon.append(L[-1])
    inside = []
    for rank, s in enumerate(M16_TOP10, 1):
        if bool(masks[s][r, c]):
            inside.append(f"{rank}/s{s}")
    in701 = bool(masks[701][r, c])
    L.append(f"site289 carrier: inside=[{','.join(inside) if inside else 'none'}] "
             f"n_in={len(inside)} split701={'in' if in701 else 'out'}")
    canon.append(L[-1])
    # isolation: nearest band row above / tail row below / hole contents
    L.append("site289 isolation: lo=27 hi=None d=262 hole=28-288 (nholes=261)")
    canon.append(L[-1])
    hole_rows = list(range(28, 289))
    for tag, mask, dd, tail in (("m15", mask15, d15, tail15),
                                ("s0", mask0, d0, tail0)):
        n_bulk, n_non, n_tail = 0, 0, 0
        bulk_rows = []
        for hr in hole_rows:
            ho = off_y(hr, c)
            if tail[ho]:
                n_tail += 1
                bulk_rows.append(f"{hr}:TAIL{int(dd[ho]):+d}")
            elif mask[ho]:
                n_bulk += 1
                bulk_rows.append(f"{hr}:{int(abs(int(dd[ho])))}")
            else:
                n_non += 1
        L.append(f"site289 hole {tag}: bulk={n_bulk} noncell={n_non} "
                 f"tail={n_tail} n=261")
        canon.append(L[-1])
        L.append(f"site289 hole {tag} bulkrows: "
                 + (" ".join(bulk_rows) if bulk_rows else "(none)"))
        canon.append(L[-1])
    return L, canon


def task2_census_lines(cols0, cols15, dec_s0, masks):
    """Task 2 receipt lines: far census + null + seats + columns."""
    L = []
    far = []  # dicts: frame,col,row,d,delta,lo,hi,d_out,d_lim,d_pool
    nonfar = []
    singletons = {"s0": 0, "m15": 0}
    allcols = sorted(set(cols0) | set(cols15))
    pooled_rows = {}
    for col in allcols:
        r0 = cols0.get(col, {"rows": []})["rows"]
        r15 = cols15.get(col, {"rows": []})["rows"]
        pooled_rows[col] = sorted(set(r0) | set(r15))
    for tag, cols in (("s0", cols0), ("m15", cols15)):
        for col in sorted(cols):
            rows = cols[col]["rows"]
            deltas = cols[col]["deltas"]
            if len(rows) == 1:
                singletons[tag] += 1
                continue
            dd, lo, hi = far_info(rows)
            for row, delta, d, l, h in zip(rows, deltas, dd, lo, hi):
                d_out, d_lim = aux_dist(row, rows)
                d_pool = pooled_d(row, pooled_rows[col])
                rec = {"frame": tag, "col": col, "row": row, "d": d,
                       "delta": delta, "lo": l, "hi": h,
                       "d_out": d_out, "d_lim": d_lim, "d_pool": d_pool}
                if d >= FAR_THRESH:
                    far.append(rec)
                else:
                    nonfar.append(rec)
    far.sort(key=lambda q: (q["frame"], q["col"], q["row"]))
    L.append(f"census far: n={len(far)} thresh={FAR_THRESH} "
             f"singletons_s0={singletons['s0']} "
             f"singletons_m15={singletons['m15']}")
    for q in far:
        hole = ""
        if q["lo"] is not None and q["hi"] is not None:
            ha = q["row"] - q["lo"] - 1
            hb = q["hi"] - q["row"] - 1
            hole = f"hole_above={q['lo'] + 1}-{q['row'] - 1}x{ha} " \
                   f"hole_below={q['row'] + 1}-{q['hi'] - 1}x{hb}"
        elif q["lo"] is not None:
            ha = q["row"] - q["lo"] - 1
            hole = f"hole={q['lo'] + 1}-{q['row'] - 1}x{ha}"
        else:
            hb = q["hi"] - q["row"] - 1
            hole = f"hole={q['row'] + 1}-{q['hi'] - 1}x{hb}"
        L.append(f"census far site: {q['frame']} c={q['col']} r={q['row']} "
                 f"d={q['d']} delta={q['delta']:+d} lo={q['lo']} hi={q['hi']} "
                 f"{hole} d_out={q['d_out']} d_lim={q['d_lim']} "
                 f"d_pool={q['d_pool']}")
    # null set: top-5 non-far by d desc
    nonfar.sort(key=lambda q: (-q["d"], q["frame"], q["col"], q["row"]))
    null5 = nonfar[:5]
    maxnon = nonfar[0]["d"] if nonfar else None
    L.append(f"census null: n_nonfar={len(nonfar)} max_d={maxnon} top5n={len(null5)}")
    for q in null5:
        L.append(f"census null site: {q['frame']} c={q['col']} r={q['row']} "
                 f"d={q['d']} delta={q['delta']:+d} lo={q['lo']} hi={q['hi']} "
                 f"d_out={q['d_out']} d_lim={q['d_lim']} d_pool={q['d_pool']}")
    # seats per far site
    for q in far:
        r, col = q["row"], q["col"]
        band = int(ROW_BAND[r])
        dec = int(dec_s0[r, col])
        streak = str(col) if col in NAMED9 else "other"
        inside = [str(rank) for rank, s in enumerate(M16_TOP10, 1)
                  if bool(masks[s][r, col])]
        in701 = bool(masks[701][r, col])
        cols = cols0 if q["frame"] == "s0" else cols15
        prof = cols[col]
        hm = hump_metrics(np.array(prof["rows"], np.int64),
                          np.array(prof["deltas"], np.int64))
        atpeak = (r == hm["peakrow"])
        L.append(f"census seat: {q['frame']} c={col} r={r} band={band} "
                 f"dec={dec} streak={streak} "
                 f"carrier_in=[{','.join(inside) if inside else 'none'}] "
                 f"split701={'in' if in701 else 'out'} peak={hm['peakrow']} "
                 f"atpeak={atpeak}")
    # column table
    fcols = sorted({q["col"] for q in far})
    L.append(f"census columns: distinct_far_cols={len(fcols)} "
             f"far_cols={fcols if fcols else []}")
    for col in allcols:
        r0 = cols0.get(col, {"rows": []})["rows"]
        r15 = cols15.get(col, {"rows": []})["rows"]
        f0 = sum(1 for q in far if q["frame"] == "s0" and q["col"] == col)
        f15 = sum(1 for q in far if q["frame"] == "m15" and q["col"] == col)
        L.append(f"census col c={col}: s0_n={len(r0)} m15_n={len(r15)} "
                 f"s0_far={f0} m15_far={f15} pooled_far={f0 + f15}")
    info = {"far": far, "nonfar": nonfar, "null5": null5,
            "singletons": singletons, "fcols": fcols}
    return L, info


def main():
    m16d, m15d, m25t, workd, evidd = (Path(a) for a in sys.argv[1:6])
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
    m25b = m25t.read_bytes()
    m25sha = hashlib.sha256(m25b).hexdigest()
    print(f"input {m25t}: bytes={len(m25b)} sha256={m25sha}")
    print(f"m25.txt sha vs M26 record dbbe5d66..567f63b3: "
          f"prefix={m25sha[:8]}..{m25sha[-8:]}")
    tgt = parse_m25_c343(m25b.decode(errors="replace"))
    if tgt is None:
        print("m25.txt C343 ROWS NOT FOUND: STOP, tabled.")
        return
    print(f"m25.txt target s0 c343: n={tgt['s0']['n']} "
          f"rows=[{tgt['s0']['min']},{tgt['s0']['max']}] sum={tgt['s0']['sum']} "
          f"rowdelta={tgt['s0']['rowdelta']} holes={tgt['s0']['holes']}")
    print(f"m25.txt target m15 c343: n={tgt['m15']['n']} "
          f"rows=[{tgt['m15']['min']},{tgt['m15']['max']}] "
          f"sum={tgt['m15']['sum']} rowdelta={tgt['m15']['rowdelta']} "
          f"holes={tgt['m15']['holes']}")

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
        print("MISMATCH vs M17-M55 baselines: STOP, tabled.")
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

    print("== Task 1: c343 reproduction ==")
    t1, canon1 = task1_c343_lines(cols0, cols15)
    for ln in t1:
        print(ln)
    # m25.txt c343 guard (value-exact)
    ok343 = True
    for tag, cols in (("s0", cols0), ("m15", cols15)):
        prof = cols.get(343, {"rows": [], "deltas": []})
        rows, deltas = prof["rows"], prof["deltas"]
        want = tgt[tag]
        rd = {r: d for r, d in zip(rows, deltas)}
        hole = hole_ranges(np.array(rows, np.int64))
        # m25 holes field: "none" or "28-288 (nholes=261)"
        match = (len(rows) == want["n"]
                 and (min(rows) if rows else -1) == want["min"]
                 and (max(rows) if rows else -1) == want["max"]
                 and sum(deltas) == want["sum"]
                 and rd == want["rowdelta"]
                 and hole == want["holes"])
        print(f"c343 {tag} m25-guard: match={match}")
        if not match:
            ok343 = False
    # DESIGN-pinned c343 guard (rows/deltas/holes)
    for tag, cols in (("s0", cols0), ("m15", cols15)):
        prof = cols.get(343, {"rows": [], "deltas": []})
        want = M25_C343[tag]
        match = (prof["rows"] == want["rows"]
                 and prof["deltas"] == want["deltas"])
        print(f"c343 {tag} DESIGN-guard: match={match}")
        if not match:
            ok343 = False
    # peak guard (first-tie argmax)
    for tag, cols in (("s0", cols0), ("m15", cols15)):
        prof = cols[343]
        hm = hump_metrics(np.array(prof["rows"], np.int64),
                          np.array(prof["deltas"], np.int64))
        want = M26_PEAK_C343[tag]
        match = (hm["peakrow"], hm["peakval"]) == want
        print(f"c343 {tag} peak-guard: peakrow={hm['peakrow']} "
              f"peakval={hm['peakval']} (want {want[0]}/{want[1]}) "
              f"match={match}")
        if not match:
            ok343 = False
    if not ok343:
        print("C343 MISMATCH: STOP, tabled.")
        return
    # TRI/QUAD comparison (tabled, not stopping)
    for tag, cols in (("s0", cols0), ("m15", cols15)):
        prof = cols[343]
        tf = trifit(np.array(prof["rows"], np.int64),
                    np.array(prof["deltas"], np.int64))
        want = M51_TRI_C343[tag]
        match = (tf["p"], tf["h"], tf["e"], tf["w"]) == want
        print(f"c343 {tag} TRI-compare: p/h/e/w={tf['p']}/{tf['h']}/"
              f"{tf['e']}/{tf['w']} (want {want[0]}/{want[1]}/{want[2]}/"
              f"{want[3]}) match={match}")
    prof15 = cols15[343]
    qf = quadfit(np.array(prof15["rows"], np.int64),
                 np.array(prof15["deltas"], np.int64))
    if qf is None:
        print("c343 m15 QUAD-compare: CONST-fb (want near-flat "
              "a=+0.01) match=False")
    else:
        a, b, c = qf
        wa, wb, wc = M54_QUAD_C343_M15
        match = (f"{a:.6f}" == f"{wa:.6f}" and f"{b:.6f}" == f"{wb:.6f}"
                 and f"{c:.6f}" == f"{wc:.6f}")
        preds = [rhalf(a * r * r + b * r + c) for r in prof15["rows"]]
        res289 = prof15["deltas"][-1] - preds[-1]
        print(f"c343 m15 QUAD-compare: a/b/c={a:.6f}/{b:.6f}/{c:.6f} "
              f"(want {wa:.6f}/{wb:.6f}/{wc:.6f}) match={match} "
              f"res289={res289:+d} (want +0)")
    prof0 = cols0[343]
    qf0 = quadfit(np.array(prof0["rows"], np.int64),
                  np.array(prof0["deltas"], np.int64))
    print(f"c343 s0 QUAD-compare: {'CONST-fb (want CONST-fb) match=True' if qf0 is None else 'NON-FB match=False'}")

    print("== Task 1: 289 value + isolation ==")
    t289, canon289 = task1_289_lines(v0, mid0, full0, v015, mid15,
                                     full15, mask0, d0, t0, mask15,
                                     d15, t15, dec_s0, masks)
    for ln in t289:
        print(ln)

    print("== Task 2: far-row census ==")
    t2, info = task2_census_lines(cols0, cols15, dec_s0, masks)
    for ln in t2:
        print(ln)

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
    _, canon1b = task1_c343_lines(cols0b, cols15b)
    _, canon289b = task1_289_lines(v0b, mid0b, full0b, v015, mid15,
                                   full15, mask0b, d0b, t0b, mask15b,
                                   d15b, t15b, dec_s0, masks)
    canon_pass1 = canon1 + canon289
    canon_pass2 = canon1b + canon289b
    h1 = hashlib.sha256(("\n".join(canon_pass1) + "\n").encode()).hexdigest()
    h2 = hashlib.sha256(("\n".join(canon_pass2) + "\n").encode()).hexdigest()
    print(f"canon pass1: {h1}")
    print(f"canon pass2: {h2}")
    print(f"canon identical={h1 == h2} lines={len(canon_pass1)}")
    print(f"cell identical={sp0['n'] == sp0b['n'] and sp15['n'] == sp15b['n']} "
          f"tail identical={int(t0.sum()) == int(t0b.sum()) and int(t15.sum()) == int(t15b.sum())}")

    print("== PNG far-row map (m15 tail-Y) ==")
    img = Image.new("RGB", (320, 224), (0, 0, 0))
    px = img.load()
    farset = {(q["row"], q["col"]) for q in info["far"]
              if q["frame"] == "m15"}
    # singleton Y cols on m15
    singcols = {c for c, p in cols15.items() if len(p["rows"]) == 1}
    for c, p in cols15.items():
        for r in p["rows"]:
            x, y = c // 2, r // 2
            if (r, c) in farset:
                col3 = (255, 0, 0)
            elif c in singcols:
                col3 = (128, 128, 128)
            else:
                col3 = (0, 255, 0)
            cur = px[x, y]
            # precedence: red > green > gray > black
            pri = {(0, 0, 0): 0, (128, 128, 128): 1, (0, 255, 0): 2,
                   (255, 0, 0): 3}
            if pri[col3] >= pri.get(cur, 0):
                px[x, y] = col3
    pngp = workd / "m56-farmap.png"
    img.save(pngp)
    print(f"farmap: {pngp} bytes={pngp.stat().st_size} "
          f"(evidence iff pooled far>=2; far={len(info['far'])})")

    wall = time.time() - t_start
    print(f"== done: wall={wall:.1f}s ==")


if __name__ == "__main__":
    main()
