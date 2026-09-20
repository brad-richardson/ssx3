#!/usr/bin/env python3
"""M54 QUAD underfit: per-column quadratic-residual tables (offline).

Usage: m54.py M16_DIR M15_DIR M26_TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, and the M26
receipt (QUAD fits + scores to reproduce); raw XFB dumps, 573440 B =
640x448 YUYV. Read-only inputs; receipt text goes to stdout (redirect
to WORK_DIR/m54.txt); PNG residual map to WORK_DIR (evidence copy
iff per DESIGN.md rule, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: QUAD reproduction (8x2 fits + same-frame scores + fit ladder)
  2: quadratic residuals (per-site tables + 2-3 census + curvature)
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
M19_NEGRATE = {"s0": 0.8093, "m15": 0.8019}  # P(d>0) on cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
NAMED_COLS = (257, 277, 296, 301, 321, 340, 342, 343)
ALL_COLS = (257, 277, 296, 301, 321, 340, 341, 342, 343)
NAMED_N = {"s0": 65, "m15": 68}
FIT_IDS = ["QUAD", "TRI", "TWO"]
M25_CONST = {"s0": {257: 29, 277: 27, 296: 35, 301: 32, 321: 26,
                    340: 41, 342: -17, 343: -29},
             "m15": {257: 19, 277: 19, 296: 37, 301: 23, 321: 28,
                     340: 38, 342: -19, 343: -24}}
M25_CONST_HITS = {"s0": 12, "m15": 13}
# M26 QUAD pins (DESIGN.md; fit-line match is parsed from m26.txt).
M26_QUAD_A2 = {  # 2dp curvature pins (None = CONST-fb expected)
    "s0": {257: -0.69, 277: -0.64, 296: -0.40, 301: -1.16,
           321: -0.68, 340: -1.39, 342: 0.21, 343: None},
    "m15": {257: -0.48, 277: -0.48, 296: -0.87, 301: -1.14,
            321: -0.80, 340: -0.94, 342: -0.02, 343: 0.01},
}
M26_QUAD_HITS = {"s0": 4, "m15": 3}
M26_QUAD_NEAR = {"s0": 8, "m15": 18}
M26_QUAD_MISS = {"s0": (32, 14, 6, 1), "m15": (23, 12, 12, 0)}
M26_QUAD_COLHITS = {
    "s0": {257: 1, 277: 1, 296: 0, 301: 0, 321: 2, 340: 0, 342: 0,
           343: 0},
    "m15": {257: 1, 277: 0, 296: 0, 301: 1, 321: 0, 340: 0, 342: 0,
            343: 1},
}
# M26 ladder pins (comparison only, not guards).
M26_LADDER_HITS = {
    "s0": {"QUAD": 4, "TRI": 18, "TWO": 15, "CONST": 12},
    "m15": {"QUAD": 3, "TRI": 16, "TWO": 12, "CONST": 13},
}
M26_LADDER_COLHITS = {
    "s0": {"QUAD": {257: 1, 277: 1, 296: 0, 301: 0, 321: 2, 340: 0,
                    342: 0, 343: 0},
           "TRI": {257: 3, 277: 2, 296: 2, 301: 3, 321: 2, 340: 2,
                   342: 2, 343: 2},
           "TWO": {257: 3, 277: 5, 296: 1, 301: 1, 321: 2, 340: 0,
                   342: 1, 343: 2},
           "CONST": {257: 4, 277: 2, 296: 1, 301: 1, 321: 3, 340: 0,
                     342: 1, 343: 0}},
    "m15": {"QUAD": {257: 1, 277: 0, 296: 0, 301: 1, 321: 0, 340: 0,
                     342: 0, 343: 1},
            "TRI": {257: 3, 277: 2, 296: 2, 301: 2, 321: 2, 340: 1,
                    342: 2, 343: 2},
            "TWO": {257: 2, 277: 3, 296: 1, 301: 1, 321: 3, 340: 1,
                    342: 1, 343: 0},
            "CONST": {257: 2, 277: 3, 296: 2, 301: 1, 321: 2, 340: 2,
                      342: 1, 343: 0}},
}
M26_TXT_SHA_HEAD, M26_TXT_SHA_TAIL = "9a3d522b", "060ff8f8"  # M51 record
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


# ---- fixed fit machinery (DESIGN.md list, exact integer arith + OLS) ----

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


def twolevel(rows: np.ndarray, deltas: np.ndarray):
    """Two-level fit (DESIGN.md pinned). Returns (topmed, botmed) or
    None if degenerate (n<2)."""
    n = len(deltas)
    if n < 2:
        return None
    k = n // 2
    dd = deltas.astype(np.int64)
    return (int_median(dd[:k]), int_median(dd[k:]))


def two_apply(rows: np.ndarray, fit) -> np.ndarray:
    n = len(rows)
    k = n // 2
    top, bot = fit
    return np.array([top] * k + [bot] * (n - k), np.int64)


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


def count_runs(vals) -> int:
    """Maximal runs of equal values over a list (0 when empty)."""
    v = [int(x) for x in vals]
    if not v:
        return 0
    return 1 + sum(1 for a, b in zip(v, v[1:]) if b != a)


def task1_profile_lines(tag, v0b, midb, fullb, synth, rr, cc, pl):
    """Task 1 profile tables for one frame; returns (lines, art)."""
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
    off = np.flatnonzero(tail)
    dt = delta[tail].astype(np.int64)
    is_y = pl[off] == 0

    # Column-membership guard (M22/M23: n/rows/sum exact or stop).
    colok = True
    profs = {}
    for ccol in ALL_COLS:
        sel = is_y & (cc[off] == ccol)
        ooc = off[sel]
        ddc = dt[sel]
        rrc = rr[ooc]
        if len(rrc):
            got = (len(rrc), int(rrc.min()), int(rrc.max()),
                   int(ddc.sum()))
        else:
            got = (0, -1, -1, 0)
        want = COL_GUARD[tag][ccol]
        ok = got == want
        colok = colok and ok
        L.append(f"{tag} colguard c={ccol}: n={got[0]} "
                 f"rows=[{got[1]},{got[2]}] sum={got[3]} "
                 f"(want n={want[0]} rows=[{want[1]},{want[2]}] "
                 f"sum={want[3]}) match={ok}")
        if ccol in NAMED_COLS:
            ord_ = np.argsort(rrc)
            profs[ccol] = {"rows": rrc[ord_].astype(np.int64),
                           "d": ddc[ord_].astype(np.int64)}
    named_n = sum(len(profs[c]["rows"]) for c in NAMED_COLS)
    L.append(f"{tag} named-col tail bytes n={named_n} "
             f"(want {NAMED_N[tag]})")
    if not colok or named_n != NAMED_N[tag]:
        L.append(f"{tag} COLUMN MEMBERSHIP MISMATCH vs M22/M23: "
                 f"STOP, tabled.")
        return L, None
    n_nony = int((~is_y).sum())
    L.append(f"{tag} nonY-tail n={n_nony} (M23 want 0)")

    # Per-row delta lists + holes (M25-identical format: guard input).
    for ccol in NAMED_COLS:
        pr = profs[ccol]
        pairs = " ".join(f"{int(r)}:{int(x)}"
                         for r, x in zip(pr["rows"], pr["d"]))
        L.append(f"{tag} prof c={ccol}: n={len(pr['rows'])} "
                 f"rows=[{int(pr['rows'].min()) if len(pr['rows']) else -1},"
                 f"{int(pr['rows'].max()) if len(pr['rows']) else -1}] "
                 f"rowdelta: {pairs}")
        L.append(f"{tag} prof c={ccol} holes: "
                 f"{hole_ranges(pr['rows'])}")

    # Column shape stats (M25-identical format: guard input).
    for ccol in NAMED_COLS:
        pr = profs[ccol]
        dd = pr["d"].astype(np.float64)
        nn = len(dd)
        sd = float(dd.std()) if nn else 0.0
        signs = np.sign(pr["d"].astype(np.int64))
        sr = count_runs(signs)
        vr = count_runs(pr["d"])
        k = nn // 2
        topm = float(dd[:k].mean()) if k else float("nan")
        botm = float(dd[k:].mean()) if nn - k else float("nan")
        L.append(f"{tag} shape c={ccol}: n={nn} "
                 f"min={int(dd.min()) if nn else 0} "
                 f"max={int(dd.max()) if nn else 0} "
                 f"range={int(dd.max() - dd.min()) if nn else 0} "
                 f"sd={sd:.3f} signruns={sr} valueruns={vr} "
                 f"topmean={topm:.3f} botmean={botm:.3f}")
        L.append(f"{tag} shape c={ccol} roworder: "
                 + " ".join(str(int(x)) for x in pr["d"]))

    # Hump metrics (M26 Task 1.1/1.2).
    for ccol in NAMED_COLS:
        pr = profs[ccol]
        hm = hump_metrics(pr["rows"], pr["d"])
        L.append(f"{tag} hump c={ccol}: peakrow={hm['peakrow']} "
                 f"peakval={hm['peakval']} first={hm['first']} "
                 f"last={hm['last']} rise={hm['rise']} fall={hm['fall']} "
                 f"sym={hm['sym']} argmax_k={hm['k']}/{hm['n']} "
                 f"third={hm['third']}")
        profs[ccol]["hump"] = hm

    art = {"n": n, "nt": nt, "mask": mask, "delta": delta, "tail": tail,
           "off": off, "dt": dt, "profs": profs}
    return L, art


def m25_match_lines(tag, lines, m25text: str):
    """Task 1 guard: prof/shape lines byte-exact vs m25.txt or stop."""
    L = []
    pat = re.compile(rf"^{tag} (prof|shape) c=\d+")
    # prof+rowdelta / prof+holes / shape+stats / shape+roworder only;
    # M25's h6view lines never match this pattern.
    want = [ln for ln in m25text.splitlines() if pat.match(ln)]
    got = [ln for ln in lines if pat.match(ln)]
    ok = got == want
    L.append(f"{tag} m25match: lines={len(got)}/{len(want)} match={ok}")
    if not ok:
        for i, (g, w) in enumerate(zip(got, want)):
            if g != w:
                L.append(f"{tag} m25match FIRSTDIFF idx={i}")
                L.append(f"  got:  {g}")
                L.append(f"  want: {w}")
                break
        if len(got) != len(want):
            L.append(f"{tag} m25match LEN differs: STOP, tabled.")
    return L, ok


def xshape_lines(art0, art15):
    """Task 1.3: per-column s0-vs-m15 shape match."""
    L = []
    peakagree = 0
    for ccol in NAMED_COLS:
        h0 = art0["profs"][ccol]["hump"]
        h1 = art15["profs"][ccol]["hump"]
        peq = h0["peakrow"] == h1["peakrow"]
        peakagree += 1 if peq else 0
        L.append(f"xshape c={ccol}: peakrow s0={h0['peakrow']} "
                 f"m15={h1['peakrow']} equal={peq} "
                 f"risefall s0=({h0['rise']},{h0['fall']}) "
                 f"m15=({h1['rise']},{h1['fall']}) "
                 f"third s0={h0['third']} m15={h1['third']}")
    L.append(f"xshape pooled H5: peakagree={peakagree}/8 "
             f"share={peakagree / 8:.4f}")
    return L


# ---- Task 2 fits ----

def fit_frame(art):
    """Fit all 3 fixed fits on one frame's named-column profiles."""
    pr = art["profs"]
    alld = np.concatenate([pr[c]["d"] for c in NAMED_COLS])
    fb = int_median(alld)
    quad, tri, two, const = {}, {}, {}, {}
    empt, qfb, tfb, wfb = [], [], [], []
    for ccol in NAMED_COLS:
        dd = pr[ccol]["d"]
        if len(dd):
            const[ccol] = int_median(dd)
        else:
            empt.append(ccol)
            const[ccol] = fb
        qf = quadfit(pr[ccol]["rows"], dd) if len(dd) else None
        if qf is None:
            qfb.append(ccol)
        quad[ccol] = qf
        if len(dd):
            tf = trifit(pr[ccol]["rows"], dd)
            if tf["flat"]:
                tfb.append(ccol)
            tri[ccol] = tf
        else:
            empt.append(f"tri@{ccol}")
            tri[ccol] = None
        wf = twolevel(pr[ccol]["rows"], dd) if len(dd) else None
        if wf is None:
            wfb.append(ccol)
        two[ccol] = wf
    return {"quad": quad, "tri": tri, "two": two, "const": const,
            "fallback": fb, "empties": empt, "qfb": qfb, "tfb": tfb,
            "wfb": wfb}


def apply_fit(fid, fit, art):
    """Predictions over the scored frame's named-column sites (row order
    per column, columns in NAMED_COLS order)."""
    pr = art["profs"]
    out = {}
    for ccol in NAMED_COLS:
        dd = pr[ccol]
        nn = len(dd["rows"])
        if fid == "QUAD":
            qf = fit["quad"][ccol]
            if qf is None:
                out[ccol] = np.full(nn, fit["const"][ccol], np.int64)
            else:
                a, b, c = qf
                out[ccol] = np.array(
                    [rhalf(a * float(r) ** 2 + b * float(r) + c)
                     for r in dd["rows"]], np.int64)
        elif fid == "TRI":
            tf = fit["tri"][ccol]
            if tf is None:
                out[ccol] = np.full(nn, fit["const"][ccol], np.int64)
            else:
                out[ccol] = tri_apply(dd["rows"], tf)
        elif fid == "TWO":
            wf = fit["two"][ccol]
            if wf is None:
                out[ccol] = np.full(nn, fit["const"][ccol], np.int64)
            else:
                out[ccol] = two_apply(dd["rows"], wf)
        elif fid == "CONST":
            out[ccol] = np.full(nn, fit["const"][ccol], np.int64)
        else:
            raise ValueError(fid)
    return out


def named_truth(art):
    return {c: art["profs"][c]["d"].astype(np.int64) for c in NAMED_COLS}


def score_fit_lines(prefix, art, preds, fids):
    """Exact-hit scoring lines per fit; preds fid->{col:array}."""
    L = []
    truth = named_truth(art)
    hits = {}
    for fid in fids:
        tall, pall = [], []
        for ccol in NAMED_COLS:
            tall.append(truth[ccol])
            pall.append(preds[fid][ccol])
        t = np.concatenate(tall).astype(np.int64)
        p = np.concatenate(pall).astype(np.int64)
        ae = np.abs(p - t)
        nh = int((ae == 0).sum())
        nn = int((ae == 1).sum())
        miss = ae[(ae != 0) & (ae != 1)]
        bins = [(2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        L.append(f"{prefix} {fid}: n={len(t)} hits={nh} "
                 f"rate={nh / len(t):.4f} near={nn} "
                 f"nearrate={nn / len(t):.4f} miss|err| "
                 f"{coarse_hist(miss, bins)}")
        L.append(f"{prefix} {fid} errvalues: {exact_counts(ae)}")
        ch = " ".join(
            f"c{c}={int(((preds[fid][c].astype(np.int64) - truth[c]) == 0).sum())}"
            f"/{len(truth[c])}" for c in NAMED_COLS)
        L.append(f"{prefix} {fid} colhits: {ch}")
        hits[fid] = nh
    return L, hits


# ---- M54 Task 2: QUAD residuals + seats + census + curvature ----

def quad_predict(rows: np.ndarray, qf, const: int) -> np.ndarray:
    """QUAD predictions over rows (M26 apply_fit QUAD path verbatim)."""
    if qf is None:
        return np.full(len(rows), const, np.int64)
    a, b, c = qf
    return np.array([rhalf(a * float(r) ** 2 + b * float(r) + c)
                     for r in rows.astype(np.int64).tolist()], np.int64)


def site_seat(row: int, peakrow: int, minrow: int, maxrow: int) -> str:
    """Seat label (DESIGN.md pinned): peak > edge > interior."""
    if row == peakrow:
        return "peak"
    if row == minrow or row == maxrow:
        return "edge"
    return "interior"


def site_holeadj(row: int, present: set, minrow: int, maxrow: int) -> bool:
    """True if row-1 or row+1 within [minrow,maxrow] is not present."""
    for nb in (row - 1, row + 1):
        if minrow <= nb <= maxrow and nb not in present:
            return True
    return False


def quad_residual_table(rows: np.ndarray, deltas: np.ndarray, qf,
                        const: int):
    """Per-site QUAD residual table (DESIGN.md pinned).

    res = delta - pred (signed). Returns dict with per-site lists
    (rows, d, pred, res, abs, seats, holes) + peakrow + aggregates.
    """
    rr = rows.astype(np.int64)
    dd = deltas.astype(np.int64)
    pred = quad_predict(rr, qf, const)
    res = (dd - pred).astype(np.int64)
    ab = np.abs(res).astype(np.int64)
    peakrow = int(rr[int(np.argmax(dd))])  # first-tie (hump_metrics verbatim)
    lo, hi = (int(rr.min()), int(rr.max())) if len(rr) else (-1, -1)
    present = set(int(r) for r in rr.tolist())
    seats = [site_seat(int(r), peakrow, lo, hi) for r in rr.tolist()]
    holes = [site_holeadj(int(r), present, lo, hi) for r in rr.tolist()]
    return {"rows": [int(r) for r in rr.tolist()],
            "d": [int(x) for x in dd.tolist()],
            "pred": [int(x) for x in pred.tolist()],
            "res": [int(x) for x in res.tolist()],
            "abs": [int(x) for x in ab.tolist()],
            "seats": seats, "holes": holes, "peakrow": peakrow,
            "hits": int((ab == 0).sum()), "near": int((ab == 1).sum()),
            "mass23": int((((ab == 2) | (ab == 3))).sum()),
            "pos": int((res > 0).sum()), "neg": int((res < 0).sum())}


def quad_depth(rows: np.ndarray, qf):
    """Cap depth = -a * span^2 (None for CONST-fallback columns)."""
    if qf is None or len(rows) == 0:
        return None
    span = int(rows.max()) - int(rows.min())
    return -qf[0] * span * span


def parse_m26_quad(m26text: str, tag: str):
    """Parse `fit {tag} QUAD:` line: {col: (a,b,c)-6dp-strings | None}.

    Returns (fits, qfb) or (None, None) if the line is missing.
    """
    for line in m26text.splitlines():
        if line.startswith(f"fit {tag} QUAD:"):
            rest = line.split(f"fit {tag} QUAD:")[1]
            m = re.search(r"qfb=\[([0-9, ]*)\]\s*$", rest)
            qfb = [int(x) for x in m.group(1).split(",") if x.strip()]
            fits = {}
            for cm in re.finditer(r"c(\d+)=(\S+)", rest):
                ccol = int(cm.group(1))
                cell = cm.group(2)
                if cell == "CONST-fb":
                    fits[ccol] = None
                else:
                    am = re.match(r"a=([^,]+),b=([^,]+),c=(\S+)", cell)
                    fits[ccol] = (am.group(1), am.group(2), am.group(3))
            return fits, qfb
    return None, None


def res_lines(tag, art, fit):
    """Task 2.1/2.2/2.3 receipt lines for one frame (DESIGN.md formats)."""
    L = []
    tables = {}
    for ccol in NAMED_COLS:
        pr = art["profs"][ccol]
        t = quad_residual_table(pr["rows"], pr["d"], fit["quad"][ccol],
                                fit["const"][ccol])
        tables[ccol] = t
        sites = " ".join(
            f"{r}:{d}/{p}/{rs:+d}/{a}/{s}/{1 if h else 0}"
            for r, d, p, rs, a, s, h in zip(
                t["rows"], t["d"], t["pred"], t["res"], t["abs"],
                t["seats"], t["holes"]))
        L.append(f"res {tag} c={ccol}: n={len(t['rows'])} sites=[{sites}]")
    L.append(f"mass23 {tag}: "
             + " ".join(f"c{c}={tables[c]['mass23']}/{len(tables[c]['rows'])}"
                        for c in NAMED_COLS)
             + f" pooled={sum(tables[c]['mass23'] for c in NAMED_COLS)}")
    cens = [(c, r, rs, s) for c in NAMED_COLS for r, rs, a, s in
            zip(tables[c]["rows"], tables[c]["res"], tables[c]["abs"],
                tables[c]["seats"]) if a in (2, 3)]
    L.append(f"census {tag}: n23={len(cens)} sites=["
             + " ".join(f"{c}:{r}:{rs:+d}:{s}" for c, r, rs, s in cens)
             + "]")
    seats = [s for _, _, _, s in cens]
    holes23 = sum(1 for c in NAMED_COLS for r, a, h in
                  zip(tables[c]["rows"], tables[c]["abs"], tables[c]["holes"])
                  if a in (2, 3) and h)
    L.append(f"census {tag} seats: peak={seats.count('peak')} "
             f"edge={seats.count('edge')} "
             f"interior={seats.count('interior')} holeadj={holes23}")
    for ccol in NAMED_COLS:
        pr = art["profs"][ccol]
        dep = quad_depth(pr["rows"], fit["quad"][ccol])
        t = tables[ccol]
        meanabs = (sum(t["abs"]) / len(t["abs"])) if t["abs"] else 0.0
        maxabs = max(t["abs"]) if t["abs"] else 0
        if dep is None:
            L.append(f"curve {tag} c={ccol}: CONST-fb depth=N/A "
                     f"meanabs={meanabs:.4f} maxabs={maxabs}")
        else:
            a = fit["quad"][ccol][0]
            span = int(pr["rows"].max()) - int(pr["rows"].min())
            L.append(f"curve {tag} c={ccol}: a={a:.6f} span={span} "
                     f"depth={dep:.4f} meanabs={meanabs:.4f} "
                     f"maxabs={maxabs}")
    nres = sum(len(tables[c]["rows"]) for c in NAMED_COLS)
    L.append(f"ressign {tag}: nres={nres} "
             f"pos={sum(tables[c]['pos'] for c in NAMED_COLS)} "
             f"neg={sum(tables[c]['neg'] for c in NAMED_COLS)} "
             f"zero={sum(tables[c]['hits'] for c in NAMED_COLS)}")
    return L, tables


def main():
    m16d, m15d, m26t, workd, evidd = (Path(a) for a in sys.argv[1:6])
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
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} "
              f"sha256={hashlib.sha256(b).hexdigest()}")
    m26text = m26t.read_text(errors="replace")
    m26sha = hashlib.sha256(m26text.encode()).hexdigest()
    print(f"input {m26t}: bytes={len(m26text)} sha256={m26sha}")
    print(f"m26.txt sha vs M51 record: head={m26sha[:8]} "
          f"(want {M26_TXT_SHA_HEAD}) tail={m26sha[-8:]} "
          f"(want {M26_TXT_SHA_TAIL}) "
          f"match={m26sha[:8] == M26_TXT_SHA_HEAD and m26sha[-8:] == M26_TXT_SHA_TAIL} "
          f"(non-guarding comparison, tabled)")

    print("== loo.txt cross-check (no resynth needed: no carrier task) ==")
    loo = parse_loo(m16d / "loo.txt")
    print(f"loo.txt parsed R_s rows: n={len(loo)} (want 764)")
    shares = {s: (R0_M16 - rs) for s, (_, rs) in loo.items() if s != 0}
    top10 = sorted(shares, key=lambda s: -shares[s])[:10]
    print(f"derived top-10 shapes: {top10}")
    print(f"derived shares: {[shares[s] for s in top10]}")
    print("carrier cross-check vs M16 REPORT: "
          + ("OK" if top10 == M16_TOP10
             and [shares[s] for s in top10] == M16_TOP10_SHARES
             and len(loo) == 764 else "MISMATCH: tabled (non-guarding)"))

    print("== model 0 (baseline recompute) ==")
    v015 = load_dump(m15d / "m15-v0.bin")
    mid15 = load_dump(m15d / "m15-mid.bin")
    full15 = load_dump(m15d / "m15-full.bin")
    b15 = synth_w_bytes(v015, full15, 0.5)
    r15 = xdiff(b15, mid15)[0]
    f15 = f"{fnv1a(b15):016x}"
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    b0 = synth_w_bytes(v0, full, 0.5)
    r0 = xdiff(b0, mid)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M53 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== Task 1: profiles s0 ==")
    t1 = time.time()
    L0, art0 = task1_profile_lines("s0", v0, mid, full, b0, rr, cc, pl)
    for ln in L0:
        print(ln)
    print(f"(Task-1 s0 wall: {time.time() - t1:.1f}s)")
    if art0 is None:
        print("cell-7/tail/column guard failed on s0: STOP.")
        return
    print("== Task 1: profiles m15 ==")
    t1 = time.time()
    L15, art15 = task1_profile_lines("m15", v015, mid15, full15, b15, rr,
                                     cc, pl)
    for ln in L15:
        print(ln)
    print(f"(Task-1 m15 wall: {time.time() - t1:.1f}s)")
    if art15 is None:
        print("cell-7/tail/column guard failed on m15: STOP.")
        return
    print(f"self jaccard s0={jaccard(art0['tail'], art0['tail']):.4f} "
          f"(want 1.0) m15={jaccard(art15['tail'], art15['tail']):.4f}")

    # ---- Task 1.1: fits (M26-identical format) ----
    print("== Task 1.1: QUAD fits ==")
    fit0 = fit_frame(art0)
    fit15 = fit_frame(art15)
    for tag, fit in (("s0", fit0), ("m15", fit15)):
        ql = " ".join(
            f"c{c}=" + (f"a={fit['quad'][c][0]:.6f},"
                        f"b={fit['quad'][c][1]:.6f},"
                        f"c={fit['quad'][c][2]:.6f}"
                        if fit["quad"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        ln = f"fit {tag} QUAD: {ql} qfb={fit['qfb']}"
        print(ln)
        canon.append(ln)
        tl = " ".join(
            f"c{c}=" + (f"p={fit['tri'][c]['p']},"
                        f"h={fit['tri'][c]['h']},"
                        f"e={fit['tri'][c]['e']},"
                        f"w={fit['tri'][c]['w']}"
                        + (",flat" if fit['tri'][c]['flat'] else "")
                        if fit["tri"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        ln = f"fit {tag} TRI: {tl} tfb={fit['tfb']}"
        print(ln)
        canon.append(ln)
        wl = " ".join(
            f"c{c}=" + (f"top={fit['two'][c][0]},"
                        f"bot={fit['two'][c][1]}"
                        if fit["two"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        ln = f"fit {tag} TWO: {wl} wfb={fit['wfb']}"
        print(ln)
        canon.append(ln)
        cl = " ".join(f"c{c}={fit['const'][c]}" for c in NAMED_COLS)
        ln = (f"fit {tag} CONST: {cl} fallback={fit['fallback']} "
              f"empties={fit['empties']}")
        print(ln)
        canon.append(ln)
        cm = all(fit["const"][c] == M25_CONST[tag][c]
                 for c in NAMED_COLS)
        print(f"fit {tag} CONST-vs-M25: match={cm}")

    # ---- M26 QUAD fit-line match guard ----
    print("== Task 1.1: M26 QUAD fit-line match ==")
    ok_all = True
    for tag, fit in (("s0", fit0), ("m15", fit15)):
        want, wqfb = parse_m26_quad(m26text, tag)
        if want is None:
            print(f"{tag} m26fit: NO `fit {tag} QUAD:` line in m26.txt: "
                  f"STOP, tabled.")
            ok_all = False
            continue
        match_cols = []
        for c in NAMED_COLS:
            qf = fit["quad"][c]
            got = (f"{qf[0]:.6f}", f"{qf[1]:.6f}", f"{qf[2]:.6f}") \
                if qf is not None else None
            w = want.get(c)
            ok = got == w
            match_cols.append(ok)
            if not ok:
                print(f"{tag} m26fit FIRSTDIFF c={c}: got={got} want={w}")
                break
        qfb_ok = fit["qfb"] == wqfb
        if not qfb_ok:
            print(f"{tag} m26fit qfb: got={fit['qfb']} want={wqfb}")
        ok = all(match_cols) and len(want) == 8 and qfb_ok
        print(f"{tag} m26fit: cols={sum(match_cols)}/8 qfb={qfb_ok} "
              f"match={ok}")
        pin_ok = all(
            (fit["quad"][c] is None and M26_QUAD_A2[tag][c] is None)
            or (fit["quad"][c] is not None
                and M26_QUAD_A2[tag][c] is not None
                and round(fit["quad"][c][0], 2) == M26_QUAD_A2[tag][c])
            for c in NAMED_COLS)
        print(f"{tag} designpin: match={pin_ok}")
        ok_all = ok_all and ok and pin_ok
    if not ok_all:
        print("M26 QUAD FIT MISMATCH: STOP, tabled.")
        return
    print("m26fit cross-check: OK")

    # ---- Task 1.2: same-frame scores ----
    print("== Task 1.2: same-frame scores s0 ==")
    preds0 = {fid: apply_fit(fid, fit0, art0) for fid in FIT_IDS + ["CONST"]}
    LS0, H0 = score_fit_lines("score s0", art0, preds0, FIT_IDS + ["CONST"])
    for ln in LS0:
        print(ln)
        canon.append(ln)
    print("== Task 1.2: same-frame scores m15 ==")
    preds15 = {fid: apply_fit(fid, fit15, art15)
               for fid in FIT_IDS + ["CONST"]}
    LS15, H15 = score_fit_lines("score m15", art15, preds15,
                                FIT_IDS + ["CONST"])
    for ln in LS15:
        print(ln)
        canon.append(ln)
    hit_ok = (H0["QUAD"] == M26_QUAD_HITS["s0"]
              and H15["QUAD"] == M26_QUAD_HITS["m15"])
    print(f"sameframe QUAD hit guard: s0 {H0['QUAD']}/{M26_QUAD_HITS['s0']} "
          f"m15 {H15['QUAD']}/{M26_QUAD_HITS['m15']} match={hit_ok}")
    if not hit_ok:
        print("SAME-FRAME QUAD HIT MISMATCH: STOP, tabled.")
        return
    for tag, art, pr in (("s0", art0, preds0), ("m15", art15, preds15)):
        truth = named_truth(art)
        chq = {c: int(((pr["QUAD"][c].astype(np.int64) - truth[c]) == 0).sum())
               for c in NAMED_COLS}
        print(f"sameframe QUAD colhits vs M26 {tag}: "
              + " ".join(f"c{c}={chq[c]}/{M26_QUAD_COLHITS[tag][c]}"
                         for c in NAMED_COLS))

    # ---- Task 1.3: fit ladder per column ----
    print("== Task 1.3: fit ladder ==")
    for tag, art, pr, HH in (("s0", art0, preds0, H0),
                             ("m15", art15, preds15, H15)):
        truth = named_truth(art)
        for ccol in NAMED_COLS:
            ch = {}
            for fid in FIT_IDS + ["CONST"]:
                ch[fid] = int(((pr[fid][ccol].astype(np.int64)
                                 - truth[ccol]) == 0).sum())
            ln = (f"ladder {tag} c={ccol}: "
                  + " ".join(f"{fid}={ch[fid]}/{len(truth[ccol])}"
                             for fid in FIT_IDS + ["CONST"]))
            print(ln)
            canon.append(ln)
        print(f"ladder {tag} pooled vs M26: "
              + " ".join(f"{fid}={HH[fid]}/{M26_LADDER_HITS[tag][fid]}"
                         for fid in FIT_IDS + ["CONST"]))

    # ---- Task 2: residuals + census + curvature ----
    print("== Task 2: QUAD residuals s0 ==")
    LR0, T0 = res_lines("s0", art0, fit0)
    for ln in LR0:
        print(ln)
    print("== Task 2: QUAD residuals m15 ==")
    LR15, T15 = res_lines("m15", art15, fit15)
    for ln in LR15:
        print(ln)
    n23 = (sum(T0[c]["mass23"] for c in NAMED_COLS)
           + sum(T15[c]["mass23"] for c in NAMED_COLS))
    print(f"census pooled: n23={n23} "
          f"(s0={sum(T0[c]['mass23'] for c in NAMED_COLS)} "
          f"m15={sum(T15[c]['mass23'] for c in NAMED_COLS)})")
    npos = sum(T0[c]["pos"] for c in NAMED_COLS) + sum(
        T15[c]["pos"] for c in NAMED_COLS)
    nneg = sum(T0[c]["neg"] for c in NAMED_COLS) + sum(
        T15[c]["neg"] for c in NAMED_COLS)
    nzero = sum(T0[c]["hits"] for c in NAMED_COLS) + sum(
        T15[c]["hits"] for c in NAMED_COLS)
    print(f"ressign pooled: nres={npos + nneg + nzero} pos={npos} "
          f"neg={nneg} zero={nzero}")

    # ---- determinism re-run (Task 1 on s0+m15, canonical text) ----
    print("== determinism re-run (Task 1 on s0+m15, second pass) ==")
    canon2 = []
    fit0b = fit_frame(art0)
    fit15b = fit_frame(art15)
    for tag, fit in (("s0", fit0b), ("m15", fit15b)):
        ql = " ".join(
            f"c{c}=" + (f"a={fit['quad'][c][0]:.6f},"
                        f"b={fit['quad'][c][1]:.6f},"
                        f"c={fit['quad'][c][2]:.6f}"
                        if fit["quad"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        canon2.append(f"fit {tag} QUAD: {ql} qfb={fit['qfb']}")
        tl = " ".join(
            f"c{c}=" + (f"p={fit['tri'][c]['p']},"
                        f"h={fit['tri'][c]['h']},"
                        f"e={fit['tri'][c]['e']},"
                        f"w={fit['tri'][c]['w']}"
                        + (",flat" if fit['tri'][c]['flat'] else "")
                        if fit["tri"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        canon2.append(f"fit {tag} TRI: {tl} tfb={fit['tfb']}")
        wl = " ".join(
            f"c{c}=" + (f"top={fit['two'][c][0]},"
                        f"bot={fit['two'][c][1]}"
                        if fit["two"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        canon2.append(f"fit {tag} TWO: {wl} wfb={fit['wfb']}")
        cl = " ".join(f"c{c}={fit['const'][c]}" for c in NAMED_COLS)
        canon2.append(f"fit {tag} CONST: {cl} fallback={fit['fallback']} "
                      f"empties={fit['empties']}")
    prb = {}
    for tag, art, fit in (("s0", art0, fit0b), ("m15", art15, fit15b)):
        pr = {fid: apply_fit(fid, fit, art) for fid in FIT_IDS + ["CONST"]}
        prb[tag] = pr
        LSC, _ = score_fit_lines(f"score {tag}", art, pr,
                                 FIT_IDS + ["CONST"])
        canon2.extend(LSC)
    for tag, art in (("s0", art0), ("m15", art15)):
        pr = prb[tag]
        truth = named_truth(art)
        for ccol in NAMED_COLS:
            ch = {}
            for fid in FIT_IDS + ["CONST"]:
                ch[fid] = int(((pr[fid][ccol].astype(np.int64)
                                 - truth[ccol]) == 0).sum())
            canon2.append(
                f"ladder {tag} c={ccol}: "
                + " ".join(f"{fid}={ch[fid]}/{len(truth[ccol])}"
                           for fid in FIT_IDS + ["CONST"]))
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0['n'] == art0['n']} "
          f"tail counts identical={art0['nt'] == art0['nt']}")

    # ---- PNG residual map (work dir; evidence copy iff per rule) ----
    print("== PNG residual map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    nhit = nnear = n23p = n4p = 0
    for ccol in NAMED_COLS:
        t = T0[ccol]
        for r, a in zip(t["rows"], t["abs"]):
            if a == 0:
                over[int(r), ccol] = (0, 255, 0)
                nhit += 1
            elif a == 1:
                over[int(r), ccol] = (255, 255, 0)
                nnear += 1
            elif a in (2, 3):
                over[int(r), ccol] = (255, 165, 0)
                n23p += 1
            else:
                over[int(r), ccol] = (255, 0, 0)
                n4p += 1
    p = workd / "m54-residmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: green=QUAD-hit n={nhit} yellow=QUAD-near n={nnear} "
          f"orange=QUAD-2-3 n={n23p} red=QUAD-4+ n={n4p} "
          f"(s0 named-col tail Y only)")
    cand = [(T0[c]["mass23"], c) for c in NAMED_COLS
            if len(T0[c]["rows"]) >= 8]
    bestm, bestc = max(cand) if cand else (0, -1)
    print(f"pngrule: maxmass23_n8={bestm} col={bestc} qualifies={bestm >= 6}")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=quad-repro T2=quad-residuals R=controls")


if __name__ == "__main__":
    main()
