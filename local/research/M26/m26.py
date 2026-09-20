#!/usr/bin/env python3
"""M26 within-column hump profiles: shape tables + hump/quadratic fits.

Usage: m26.py M16_DIR M15_DIR M25_TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, and the M25
receipt (column profiles to reproduce); raw XFB dumps, 573440 B =
640x448 YUYV. Read-only inputs; receipt text goes to stdout (redirect
to WORK_DIR/m26.txt); PNG shape-fit map to WORK_DIR (evidence copy
iff discriminating per DESIGN.md, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: profile-shape tables (hump metrics + cross-frame shape match)
  2: hump fits (fixed 3-list, exact-hit scoring + transfer + baseline)
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


def main():
    m16d, m15d, m25t, workd, evidd = (Path(a) for a in sys.argv[1:6])
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
    m25text = m25t.read_text(errors="replace")
    print(f"input {m25t}: bytes={len(m25text)} "
          f"sha256={hashlib.sha256(m25text.encode()).hexdigest()}")

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
        print("MISMATCH vs M17-M25 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== Task 1: profiles s0 ==")
    t1 = time.time()
    L0, art0 = task1_profile_lines("s0", v0, mid, full, b0, rr, cc, pl)
    for ln in L0:
        print(ln)
        canon.append(ln)
    print(f"(Task-1 s0 wall: {time.time() - t1:.1f}s)")
    if art0 is None:
        print("cell-7/tail/column guard failed on s0: STOP.")
        return
    print("== Task 1: M25 profile-line match s0 ==")
    LM0, ok0 = m25_match_lines("s0", L0, m25text)
    for ln in LM0:
        print(ln)
    if not ok0:
        print("M25 PROFILE MISMATCH on s0: STOP, tabled.")
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
    print("== Task 1: M25 profile-line match m15 ==")
    LM15, ok15 = m25_match_lines("m15", L15, m25text)
    for ln in LM15:
        print(ln)
    if not ok15:
        print("M25 PROFILE MISMATCH on m15: STOP, tabled.")
        return
    print(f"self jaccard s0={jaccard(art0['tail'], art0['tail']):.4f} "
          f"(want 1.0) m15={jaccard(art15['tail'], art15['tail']):.4f}")

    print("== Task 1.3: cross-frame shape match ==")
    for ln in xshape_lines(art0, art15):
        print(ln)

    # ---- fits ----
    print("== Task 2 fits ==")
    fit0 = fit_frame(art0)
    fit15 = fit_frame(art15)
    for tag, fit in (("s0", fit0), ("m15", fit15)):
        ql = " ".join(
            f"c{c}=" + (f"a={fit['quad'][c][0]:.6f},"
                        f"b={fit['quad'][c][1]:.6f},"
                        f"c={fit['quad'][c][2]:.6f}"
                        if fit["quad"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        print(f"fit {tag} QUAD: {ql} qfb={fit['qfb']}")
        tl = " ".join(
            f"c{c}=" + (f"p={fit['tri'][c]['p']},"
                        f"h={fit['tri'][c]['h']},"
                        f"e={fit['tri'][c]['e']},"
                        f"w={fit['tri'][c]['w']}"
                        + (",flat" if fit['tri'][c]['flat'] else "")
                        if fit["tri"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        print(f"fit {tag} TRI: {tl} tfb={fit['tfb']}")
        wl = " ".join(
            f"c{c}=" + (f"top={fit['two'][c][0]},"
                        f"bot={fit['two'][c][1]}"
                        if fit["two"][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        print(f"fit {tag} TWO: {wl} wfb={fit['wfb']}")
        cl = " ".join(f"c{c}={fit['const'][c]}" for c in NAMED_COLS)
        print(f"fit {tag} CONST: {cl} fallback={fit['fallback']} "
              f"empties={fit['empties']}")
        cm = all(fit["const"][c] == M25_CONST[tag][c]
                 for c in NAMED_COLS)
        print(f"fit {tag} CONST-vs-M25: match={cm}")

    # ---- Task 2.1: same-frame scoring ----
    print("== Task 2.1: same-frame scores s0 ==")
    preds0 = {fid: apply_fit(fid, fit0, art0) for fid in FIT_IDS + ["CONST"]}
    LS0, H0 = score_fit_lines("score s0", art0, preds0, FIT_IDS + ["CONST"])
    for ln in LS0:
        print(ln)
    print("== Task 2.1: same-frame scores m15 ==")
    preds15 = {fid: apply_fit(fid, fit15, art15)
               for fid in FIT_IDS + ["CONST"]}
    LS15, H15 = score_fit_lines("score m15", art15, preds15,
                                FIT_IDS + ["CONST"])
    for ln in LS15:
        print(ln)

    # ---- best fit (DESIGN.md rule) + residual ----
    order = {fid: i for i, fid in enumerate(FIT_IDS)}
    best = sorted(FIT_IDS,
                  key=lambda p: (-H0[p], -H15[p], order[p]))[0]
    print(f"best fit: {best} (s0hits={H0[best]} "
          f"m15hits={H15[best]} pooled={H0[best] + H15[best]})")
    for tag, art, pr in (("s0", art0, preds0), ("m15", art15, preds15)):
        truth = named_truth(art)
        t = np.concatenate([truth[c] for c in NAMED_COLS])
        p = np.concatenate([pr[best][c] for c in NAMED_COLS])
        resid = np.abs(t.astype(np.int64) - p.astype(np.int64))
        bins = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        print(f"residual {tag} best={best}: {coarse_hist(resid, bins)}")
        print(f"residual {tag} best={best} values: {exact_counts(resid)}")
        print(f"explained {tag}: {int((resid == 0).sum())}/{art['nt']} "
              f"tail standing={int((resid != 0).sum())} "
              f"(named-col scope; outside-named untabled here)")

    # ---- Task 2.2: cross-frame both directions ----
    print("== Task 2.2: fit-s0 score-m15 ==")
    pxf_0_15 = {fid: apply_fit(fid, fit0, art15) for fid in FIT_IDS}
    LX1, HX1 = score_fit_lines("xframe fit-s0/score-m15", art15, pxf_0_15,
                               FIT_IDS)
    for ln in LX1:
        print(ln)
    print("== Task 2.2: fit-m15 score-s0 ==")
    pxf_15_0 = {fid: apply_fit(fid, fit15, art0) for fid in FIT_IDS}
    LX2, HX2 = score_fit_lines("xframe fit-m15/score-s0", art0, pxf_15_0,
                               FIT_IDS)
    for ln in LX2:
        print(ln)

    # ---- Task 2.3: beat-the-baseline (best shape vs M25 CONST) ----
    print("== Task 2.3: best-vs-CONST head-to-head ==")
    for tag, art, pr, HH in (("s0", art0, preds0, H0),
                               ("m15", art15, preds15, H15)):
        truth = named_truth(art)
        cells = []
        for ccol in NAMED_COLS:
            hb = int(((pr[best][ccol].astype(np.int64) - truth[ccol]) == 0).sum())
            hc = int(((pr["CONST"][ccol].astype(np.int64) - truth[ccol]) == 0).sum())
            cells.append(f"c{ccol}={hb}v{hc}:{hb - hc:+d}")
        print(f"headtohead {tag} {best}-vs-CONST: {' '.join(cells)} "
              f"pooled={HH[best]}v{HH['CONST']}:{HH[best] - HH['CONST']:+d} "
              f"(M25 CONST want {M25_CONST_HITS[tag]})")

    # ---- determinism re-run (Task 1 on s0, canonical text) ----
    print("== determinism re-run (Task 1 on s0, second pass) ==")
    L0b, art0b = task1_profile_lines("s0", v0, mid, full, b0, rr, cc, pl)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0b is not None and art0['n'] == art0b['n']}"
          f" tail counts identical="
          f"{art0b is not None and art0['nt'] == art0b['nt']}")

    # ---- PNG shape-fit map (work dir; evidence copy iff per rule) ----
    print("== PNG shape-fit map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    truth0 = named_truth(art0)
    hit_y = np.zeros((H, W), bool)
    near_y = np.zeros((H, W), bool)
    miss_y = np.zeros((H, W), bool)
    for ccol in NAMED_COLS:
        pr = art0["profs"][ccol]
        t = truth0[ccol].astype(np.int64)
        p = preds0["TRI"][ccol].astype(np.int64)
        ae = np.abs(p - t)
        for r, e in zip(pr["rows"], ae):
            if e == 0:
                hit_y[int(r), ccol] = True
            elif e == 1:
                near_y[int(r), ccol] = True
            else:
                miss_y[int(r), ccol] = True
    p = workd / "m26-shapemap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: green=TRI-hit n={int(hit_y.sum())} "
          f"yellow=TRI-near n={int(near_y.sum())} "
          f"red=TRI-miss n={int(miss_y.sum())} "
          f"(s0 named-col tail Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=shape-tables T2=hump-fits R=controls")


if __name__ == "__main__":
    main()
