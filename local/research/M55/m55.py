#!/usr/bin/env python3
"""M55 CONST cross-frame collapse: per-column median drift tables.

Usage: m55.py M16_DIR M15_DIR M25_TXT M26_TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, the M25
receipt (8+8 CONST medians + CONST scores to reproduce) and the M26
receipt (TRI p/h peaks for the median-vs-peak table); raw XFB dumps,
573440 B = 640x448 YUYV. Read-only inputs; receipt text goes to
stdout (redirect to WORK_DIR/m55.txt); PNG drift-collapse map to
WORK_DIR (evidence copy iff per DESIGN.md rule, decided at report
time). Shared core M51 m51.py verbatim where reused; CONST fit
M25-verbatim.

Tasks (see DESIGN.md, recorded before running):
  1: CONST reproduction (8+8 medians + same-frame + collapse)
  2: median drift (delta/rank/drift-vs-keep/medpeak/xerr)
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
M25_CONST = {
    "s0": {257: 29, 277: 27, 296: 35, 301: 32,
           321: 26, 340: 41, 342: -17, 343: -29},
    "m15": {257: 19, 277: 19, 296: 37, 301: 23,
            321: 28, 340: 38, 342: -19, 343: -24},
}
M25_CONST_FB = {"s0": 27, "m15": 20}
M25_CONST_HITS = {"s0": 12, "m15": 13}
M25_CONST_NEAR = {"s0": 14, "m15": 14}
M25_CONST_MISS = {"s0": (8, 11, 13, 7), "m15": (9, 11, 15, 6)}
M25_CONST_COLHITS = {
    "s0": {257: 4, 277: 2, 296: 1, 301: 1, 321: 3, 340: 0, 342: 1, 343: 0},
    "m15": {257: 2, 277: 3, 296: 2, 301: 1, 321: 2, 340: 2, 342: 1, 343: 0},
}
M25_X_CONST = {
    ("s0", "m15"): {"hits": 0, "n": 68, "near": 2,
                    "colhits": {257: 0, 277: 0, 296: 0, 301: 0,
                                321: 0, 340: 0, 342: 0, 343: 0}},
    ("m15", "s0"): {"hits": 1, "n": 65, "near": 4,
                    "colhits": {257: 0, 277: 0, 296: 0, 301: 0,
                                321: 0, 340: 1, 342: 0, 343: 0}},
}
# M26 TRI peak pins (p/h only; non-guarding comparison for medpeak).
M26_PEAK = {
    "s0": {257: (25, 30), 277: (25, 28), 296: (26, 47), 301: (27, 47),
           321: (25, 27), 340: (26, 47), 342: (27, -16), 343: (27, -26)},
    "m15": {257: (25, 20), 277: (25, 20), 296: (26, 46), 301: (27, 48),
            321: (26, 31), 340: (32, 48), 342: (27, -13), 343: (289, -15)},
}
M25_TXT_SHA_PREFIX = "dbbe5d66"
M26_TXT_SHA_PREFIX = "9a3d522b"
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


# ---- CONST fit machinery (M25 verbatim; TRI dropped per DESIGN.md) ----

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


def const_median(deltas) -> int:
    """CONST column fit (M25-verbatim): int_median as-is, no n<3 case."""
    return int_median(deltas)


def median_drift(m0: int, m1: int):
    """Median drift m15 - s0; returns (delta, abs)."""
    d = int(m1) - int(m0)
    return d, abs(d)


def drift_ranks(absvals):
    """Rank by |d| desc; ties -> smaller column first. Input: {c: abs}.
    Returns {c: rank} (1-based, dense by position, ties share nothing —
    each column gets a distinct rank by (abs desc, col asc) order)."""
    order = sorted(absvals, key=lambda c: (-absvals[c], c))
    return {c: i + 1 for i, c in enumerate(order)}


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
    """Task 1 profiles for one frame; returns (lines, art)."""
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

    # Per-row delta lists + holes (M25/M26-identical format).
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

    art = {"n": n, "nt": nt, "mask": mask, "delta": delta, "tail": tail,
           "off": off, "dt": dt, "profs": profs}
    return L, art


def parse_m25_const(m25text: str, tag: str):
    """Parse `fit {tag} CONST:` line from m25.txt into ({col:med}, fb)."""
    pat = re.compile(rf"^fit {tag} CONST: (.*)$", re.M)
    m = pat.search(m25text)
    if not m:
        return None, None
    body = m.group(1)
    out = {}
    for cm in re.finditer(r"c(\d+)=(-?\d+)", body):
        out[int(cm.group(1))] = int(cm.group(2))
    fb = None
    fm = re.search(r"fallback=(-?\d+)", body)
    if fm:
        fb = int(fm.group(1))
    return out, fb


def parse_m26_tri(m26text: str, tag: str):
    """Parse `fit {tag} TRI:` line from m26.txt into {col:(p,h,e,w)}."""
    pat = re.compile(rf"^fit {tag} TRI: (.*)$", re.M)
    m = pat.search(m26text)
    if not m:
        return None
    body = m.group(1)
    out = {}
    for cm in re.finditer(r"c(\d+)=p=(-?\d+),h=(-?\d+),e=(-?\d+),w=(\d+)",
                          body):
        out[int(cm.group(1))] = (int(cm.group(2)), int(cm.group(3)),
                                 int(cm.group(4)), int(cm.group(5)))
    return out


def fit_frame_const(art):
    """Fit CONST on one frame's named-column profiles (M25-verbatim:
    int_median as-is, empty-column fallback only)."""
    pr = art["profs"]
    alld = np.concatenate([pr[c]["d"] for c in NAMED_COLS])
    fb = int_median(alld)
    const = {}
    empt = []
    for ccol in NAMED_COLS:
        dd = pr[ccol]["d"]
        if len(dd):
            const[ccol] = const_median(dd)
        else:
            empt.append(ccol)
            const[ccol] = fb
    return {"const": const, "fallback": fb, "empties": empt}


def apply_const(fit, art):
    """CONST predictions over the scored frame's named-column sites."""
    pr = art["profs"]
    out = {}
    for ccol in NAMED_COLS:
        dd = pr[ccol]
        nn = len(dd["rows"])
        out[ccol] = np.full(nn, fit["const"][ccol], np.int64)
    return out


def named_truth(art):
    return {c: art["profs"][c]["d"].astype(np.int64) for c in NAMED_COLS}


def score_const_lines(prefix, art, preds):
    """Exact-hit CONST scoring lines (M25-identical format); returns
    (lines, hits, near, colhits, ae)."""
    L = []
    truth = named_truth(art)
    tall, pall = [], []
    for ccol in NAMED_COLS:
        tall.append(truth[ccol])
        pall.append(preds[ccol])
    t = np.concatenate(tall).astype(np.int64)
    p = np.concatenate(pall).astype(np.int64)
    ae = np.abs(p - t)
    nh = int((ae == 0).sum())
    nn = int((ae == 1).sum())
    miss = ae[(ae != 0) & (ae != 1)]
    bins = [(2, 3), (4, 7), (8, 15), (16, 1 << 15)]
    L.append(f"{prefix} CONST: n={len(t)} hits={nh} "
             f"rate={nh / len(t):.4f} near={nn} "
             f"nearrate={nn / len(t):.4f} miss|err| "
             f"{coarse_hist(miss, bins)}")
    L.append(f"{prefix} CONST errvalues: {exact_counts(ae)}")
    ch = {}
    for c in NAMED_COLS:
        ch[c] = int(((preds[c].astype(np.int64) - truth[c]) == 0).sum())
    L.append(f"{prefix} CONST colhits: "
             + " ".join(f"c{c}={ch[c]}/{len(truth[c])}" for c in NAMED_COLS))
    return L, nh, nn, ch, ae


def main():
    m16d, m15d, m25t, m26t, workd, evidd = (Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 fits + Task 2 drift)
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
    h25 = hashlib.sha256(m25text.encode()).hexdigest()
    print(f"input {m25t}: bytes={len(m25text)} sha256={h25}")
    print(f"m25.txt sha prefix vs M26 record {M25_TXT_SHA_PREFIX}: "
          f"{'OK' if h25.startswith(M25_TXT_SHA_PREFIX) else 'MISMATCH: tabled (non-guarding)'}")
    m26text = m26t.read_text(errors="replace")
    h26 = hashlib.sha256(m26text.encode()).hexdigest()
    print(f"input {m26t}: bytes={len(m26text)} sha256={h26}")
    print(f"m26.txt sha prefix vs M51 record {M26_TXT_SHA_PREFIX}: "
          f"{'OK' if h26.startswith(M26_TXT_SHA_PREFIX) else 'MISMATCH: tabled (non-guarding)'}")

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
        print("MISMATCH vs M17-M54 baselines: STOP, tabled.")
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

    # ---- CONST fits (M25-identical format) ----
    print("== Task 1: CONST fits ==")
    fit0 = fit_frame_const(art0)
    fit15 = fit_frame_const(art15)
    for tag, fit in (("s0", fit0), ("m15", fit15)):
        tl = " ".join(f"c{c}={fit['const'][c]}" for c in NAMED_COLS)
        ln = (f"fit {tag} CONST: {tl} fallback={fit['fallback']} "
              f"empties={fit['empties']}")
        print(ln)
        canon.append(ln)

    # ---- M25 fit-line match guard ----
    print("== Task 1: M25 CONST fit-line match ==")
    ok_all = True
    for tag, fit in (("s0", fit0), ("m15", fit15)):
        want, wantfb = parse_m25_const(m25text, tag)
        if want is None:
            print(f"{tag} m25fit: NO `fit {tag} CONST:` line in m25.txt: "
                  f"STOP, tabled.")
            ok_all = False
            continue
        match_cols = []
        for c in NAMED_COLS:
            got = fit["const"][c]
            w = want.get(c)
            ok = got == w
            match_cols.append(ok)
            if not ok:
                print(f"{tag} m25fit FIRSTDIFF c={c}: got={got} want={w}")
                break
        fb_ok = fit["fallback"] == wantfb
        if not fb_ok:
            print(f"{tag} m25fit FALLBACK: got={fit['fallback']} "
                  f"want={wantfb}")
        ok = all(match_cols) and len(want) == 8 and fb_ok
        print(f"{tag} m25fit: cols={sum(match_cols)}/8 fallback={fb_ok} "
              f"match={ok}")
        # Also compare to DESIGN pins (same numbers, belt-and-braces).
        pin_ok = (all(fit["const"][c] == M25_CONST[tag][c]
                      for c in NAMED_COLS)
                  and fit["fallback"] == M25_CONST_FB[tag])
        print(f"{tag} designpin: match={pin_ok}")
        ok_all = ok_all and ok and pin_ok
    if not ok_all:
        print("M25 CONST FIT MISMATCH: STOP, tabled.")
        return
    print("m25fit cross-check: OK")

    # ---- Task 1.2: same-frame CONST scores ----
    print("== Task 1.2: same-frame CONST scores s0 ==")
    preds0 = apply_const(fit0, art0)
    LS0, H0, N0, CH0, AE0 = score_const_lines("score s0", art0, preds0)
    for ln in LS0:
        print(ln)
    canon.append(LS0[0])
    print("== Task 1.2: same-frame CONST scores m15 ==")
    preds15 = apply_const(fit15, art15)
    LS15, H15, N15, CH15, AE15 = score_const_lines("score m15", art15,
                                                  preds15)
    for ln in LS15:
        print(ln)
    canon.append(LS15[0])
    # Hit+near guard (miss/errvalues/colhits measured with comparison).
    hit_ok = (H0 == M25_CONST_HITS["s0"] and H15 == M25_CONST_HITS["m15"])
    near_ok = (N0 == M25_CONST_NEAR["s0"] and N15 == M25_CONST_NEAR["m15"])
    print(f"sameframe hit guard: s0 {H0}/{M25_CONST_HITS['s0']} m15 "
          f"{H15}/{M25_CONST_HITS['m15']} match={hit_ok}")
    print(f"sameframe near guard: s0 {N0}/{M25_CONST_NEAR['s0']} m15 "
          f"{N15}/{M25_CONST_NEAR['m15']} match={near_ok}")
    print(f"sameframe colhits vs M25 s0: "
          + " ".join(f"c{c}={CH0[c]}/{M25_CONST_COLHITS['s0'][c]}"
                     for c in NAMED_COLS))
    print(f"sameframe colhits vs M25 m15: "
          + " ".join(f"c{c}={CH15[c]}/{M25_CONST_COLHITS['m15'][c]}"
                     for c in NAMED_COLS))
    if not (hit_ok and near_ok):
        print("SAME-FRAME CONST HIT/NEAR MISMATCH: STOP, tabled.")
        return

    # ---- Task 1.3: collapse both directions ----
    print("== Task 1.3: fit-s0 score-m15 (CONST) ==")
    pxf_0_15 = apply_const(fit0, art15)
    LX1, HX1, NX1, CHX1, AEX1 = score_const_lines(
        "xframe fit-s0/score-m15", art15, pxf_0_15)
    for ln in LX1:
        print(ln)
    canon.append(LX1[0])
    print("== Task 1.3: fit-m15 score-s0 (CONST) ==")
    pxf_15_0 = apply_const(fit15, art0)
    LX2, HX2, NX2, CHX2, AEX2 = score_const_lines(
        "xframe fit-m15/score-s0", art0, pxf_15_0)
    for ln in LX2:
        print(ln)
    canon.append(LX2[0])
    x_ok = True
    for key, hx, nx, chx in ((("s0", "m15"), HX1, NX1, CHX1),
                             (("m15", "s0"), HX2, NX2, CHX2)):
        want = M25_X_CONST[key]
        ch_ok = all(chx[c] == want["colhits"][c] for c in NAMED_COLS)
        ok = (hx == want["hits"] and nx == want["near"] and ch_ok)
        x_ok = x_ok and ok
        print(f"xframe {key[0]}->{key[1]} vs M25: hits {hx}/{want['hits']} "
              f"n={want['n']} near {nx}/{want['near']} colhits={ch_ok} "
              f"match={ok} "
              + " ".join(f"c{c}={chx[c]}/{want['colhits'][c]}"
                         for c in NAMED_COLS))
    if not x_ok:
        print("XFRAME CONST HIT/NEAR/COLHIT MISMATCH: STOP, tabled.")
        return

    # ---- Kept-hit + near-hit site rows ----
    print("== Task 1.3: kept-hit site rows ==")
    for tag, art, px in (("fit-s0->m15", art15, pxf_0_15),
                         ("fit-m15->s0", art0, pxf_15_0)):
        truth = named_truth(art)
        nrows = 0
        for c in NAMED_COLS:
            t = truth[c]
            p = px[c].astype(np.int64)
            rows = art["profs"][c]["rows"]
            for r, tv, pv in zip(rows.tolist(), t.tolist(), p.tolist()):
                if tv == pv:
                    print(f"xkept {tag}: c={c} r={int(r)} d={int(tv)} "
                          f"pred={int(pv)}")
                    nrows += 1
        print(f"xkept {tag}: nrows={nrows}")
    print("== Task 1.3: near-hit site rows ==")
    for tag, art, px in (("fit-s0->m15", art15, pxf_0_15),
                         ("fit-m15->s0", art0, pxf_15_0)):
        truth = named_truth(art)
        nrows = 0
        for c in NAMED_COLS:
            t = truth[c]
            p = px[c].astype(np.int64)
            rows = art["profs"][c]["rows"]
            for r, tv, pv in zip(rows.tolist(), t.tolist(), p.tolist()):
                if abs(int(pv) - int(tv)) == 1:
                    print(f"xnear {tag}: c={c} r={int(r)} d={int(tv)} "
                          f"pred={int(pv)} err={int(pv) - int(tv):+d}")
                    nrows += 1
        print(f"xnear {tag}: nrows={nrows}")

    # ---- Task 2.1: drift ----
    print("== Task 2.1: drift table ==")
    drifts = {}
    absvals = {}
    for c in NAMED_COLS:
        m0, m1 = fit0["const"][c], fit15["const"][c]
        d, a = median_drift(m0, m1)
        drifts[c] = (m0, m1, d, a)
        absvals[c] = a
    ranks = drift_ranks(absvals)
    for c in NAMED_COLS:
        m0, m1, d, a = drifts[c]
        ln = (f"drift c={c}: s0={m0} m15={m1} delta={d:+d} abs={a} "
              f"rank={ranks[c]}")
        print(ln)
        canon.append(ln)

    print("== Task 2.2: drift-vs-keep ==")
    for c in NAMED_COLS:
        m0, m1, d, a = drifts[c]
        k1 = CHX1[c]
        k2 = CHX2[c]
        pooled = k1 + k2
        low = a <= 2
        ln = (f"driftx c={c}: abs={a} low={low} "
              f"sames0={CH0[c]}/{len(art0['profs'][c]['rows'])} "
              f"samem15={CH15[c]}/{len(art15['profs'][c]['rows'])} "
              f"k_s0m15={k1}/{len(art15['profs'][c]['rows'])} "
              f"k_m15s0={k2}/{len(art0['profs'][c]['rows'])} "
              f"pooled={pooled}")
        print(ln)
        canon.append(ln)

    # ---- Task 2.3: median-vs-peak + per-column xerr ----
    print("== Task 2.3: M26 peak pins ==")
    peaks = {}
    for tag in ("s0", "m15"):
        got = parse_m26_tri(m26text, tag)
        if got is None:
            print(f"{tag} m26peak: NO `fit {tag} TRI:` line in m26.txt: "
                  f"tabled (non-guarding).")
            peaks[tag] = {}
            continue
        ph = {c: (got[c][0], got[c][1]) for c in NAMED_COLS if c in got}
        pok = (len(ph) == 8 and all(ph[c] == M26_PEAK[tag][c]
                                    for c in NAMED_COLS))
        print(f"{tag} m26peak: cols={len(ph)}/8 pinmatch={pok}")
        if not pok:
            for c in NAMED_COLS:
                if ph.get(c) != M26_PEAK[tag][c]:
                    print(f"{tag} m26peak FIRSTDIFF c={c}: got={ph.get(c)} "
                          f"want={M26_PEAK[tag][c]}")
                    break
        peaks[tag] = ph
    print("== Task 2.3: median-vs-peak table ==")
    for tag, fit in (("s0", fit0), ("m15", fit15)):
        for c in NAMED_COLS:
            med = fit["const"][c]
            pp, hh = peaks[tag].get(c, (-1, -9999))
            eq = (med == hh)
            print(f"medpeak {tag} c={c}: med={med} p={pp} h={hh} eq={eq} "
                  f"med-h={med - hh:+d}")
    print("== Task 2.3: per-column xerr ==")
    for tag, art, px in (("fit-s0->m15", art15, pxf_0_15),
                         ("fit-m15->s0", art0, pxf_15_0)):
        truth = named_truth(art)
        for c in NAMED_COLS:
            t = truth[c].astype(np.int64)
            p = px[c].astype(np.int64)
            ae = np.abs(p - t)
            print(f"xerr {tag} c={c}: n={len(t)} "
                  f"meanabs={float(ae.mean()):.3f} maxabs={int(ae.max())}")

    # ---- determinism re-run (Task 1 on s0+m15 + drift, fresh) ----
    print("== determinism re-run (CONST fits+scores on s0+m15 + drift) ==")
    L0b, art0b = task1_profile_lines("s0", v0, mid, full, b0, rr, cc, pl)
    L15b, art15b = task1_profile_lines("m15", v015, mid15, full15, b15,
                                       rr, cc, pl)
    canon2 = []
    if art0b is not None and art15b is not None:
        fit0b = fit_frame_const(art0b)
        fit15b = fit_frame_const(art15b)
        for tag, fit in (("s0", fit0b), ("m15", fit15b)):
            tl = " ".join(f"c{c}={fit['const'][c]}" for c in NAMED_COLS)
            canon2.append(f"fit {tag} CONST: {tl} "
                          f"fallback={fit['fallback']} "
                          f"empties={fit['empties']}")
        # Task-1 score summary lines (same order as pass 1).
        pr0b = apply_const(fit0b, art0b)
        pr15b = apply_const(fit15b, art15b)
        px1b = apply_const(fit0b, art15b)
        px2b = apply_const(fit15b, art0b)
        LS0b = score_const_lines("score s0", art0b, pr0b)[0]
        LS15b = score_const_lines("score m15", art15b, pr15b)[0]
        LX1b = score_const_lines("xframe fit-s0/score-m15", art15b, px1b)[0]
        LX2b = score_const_lines("xframe fit-m15/score-s0", art0b, px2b)[0]
        canon2.append(LS0b[0])
        canon2.append(LS15b[0])
        canon2.append(LX1b[0])
        canon2.append(LX2b[0])
        absb = {}
        for c in NAMED_COLS:
            m0, m1 = fit0b["const"][c], fit15b["const"][c]
            d, a = median_drift(m0, m1)
            absb[c] = a
        rankb = drift_ranks(absb)
        for c in NAMED_COLS:
            m0, m1 = fit0b["const"][c], fit15b["const"][c]
            d, a = median_drift(m0, m1)
            canon2.append(f"drift c={c}: s0={m0} m15={m1} delta={d:+d} "
                          f"abs={a} rank={rankb[c]}")
        # driftx needs same-frame + cross-frame colhits; recompute cheaply.
        t15 = named_truth(art15b)
        t0 = named_truth(art0b)
        for c in NAMED_COLS:
            d, a = median_drift(fit0b["const"][c], fit15b["const"][c])
            h0 = int(((pr0b[c].astype(np.int64) - t0[c]) == 0).sum())
            h1 = int(((pr15b[c].astype(np.int64) - t15[c]) == 0).sum())
            k1 = int(((px1b[c].astype(np.int64) - t15[c]) == 0).sum())
            k2 = int(((px2b[c].astype(np.int64) - t0[c]) == 0).sum())
            canon2.append(
                f"driftx c={c}: abs={a} low={a <= 2} "
                f"sames0={h0}/{len(art0b['profs'][c]['rows'])} "
                f"samem15={h1}/{len(art15b['profs'][c]['rows'])} "
                f"k_s0m15={k1}/{len(art15b['profs'][c]['rows'])} "
                f"k_m15s0={k2}/{len(art0b['profs'][c]['rows'])} "
                f"pooled={k1 + k2}")
    # canon pass1 = fit + score-summary + xframe-summary + drift + driftx.
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    fits_ident = (canon == canon2)
    print(f"fits+scores+drift identical={fits_ident}")
    print(f"cell counts identical="
          f"{art0b is not None and art15b is not None and art0['n'] == art0b['n'] and art15['n'] == art15b['n']}"
          f" tail counts identical="
          f"{art0b is not None and art15b is not None and art0['nt'] == art0b['nt'] and art15['nt'] == art15b['nt']}")

    # ---- PNG drift-collapse map (work dir; evidence copy iff per rule) ----
    print("== PNG drift-collapse map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    # Pooled kept per s0 site: hit in EITHER cross-frame direction?
    # s0 sites: kept iff fit-m15->s0 hits at that (c,r). m15-only
    # kept (fit-s0->m15) has no s0 site; map shows s0-side survival.
    truth0 = named_truth(art0)
    nkept_map, nlost_map = 0, 0
    for ccol in NAMED_COLS:
        pr = art0["profs"][ccol]
        t = truth0[ccol].astype(np.int64)
        px = pxf_15_0[ccol].astype(np.int64)
        ae = np.abs(px - t)
        for r, e in zip(pr["rows"], ae):
            if e == 0:
                over[int(r), ccol] = (0, 255, 0)
                nkept_map += 1
            else:
                over[int(r), ccol] = (255, 0, 0)
                nlost_map += 1
    p = workd / "m55-driftmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: green=kept(fit-m15->s0 hit) n={nkept_map} "
          f"red=lost n={nlost_map} (s0 named-col tail Y only)")
    # Pre-registered split for the evidence-copy rule.
    for c in NAMED_COLS:
        pooled = CHX1[c] + CHX2[c]
        n0 = len(art0["profs"][c]["rows"])
        print(f"pngrule c={c}: n_s0={n0} pooled_kept={pooled} "
              f"qualifies={n0 >= 8 and pooled >= 3}")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=fit-repro T2=drift R=controls")


if __name__ == "__main__":
    main()
