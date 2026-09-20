#!/usr/bin/env python3
"""M53 index-top argmax concentration: plateau-aware peak tables.

Usage: m53.py M16_DIR M15_DIR M25_TXT M26_TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, the M25
receipt (column profiles to reproduce) and the M26 receipt (hump +
xshape lines to reproduce); raw XFB dumps, 573440 B = 640x448 YUYV.
Read-only inputs; receipt text goes to stdout (redirect to
WORK_DIR/m53.txt); PNG plateau map to WORK_DIR (evidence copy iff
discriminating per DESIGN.md, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: first-tie reproduction + all-tie rows + tie shapes + census
  2: run-center rules (R1/R2 peaks + thirds + agreement + TRI-p)
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
# M51 cited TRI p (Task 2.3 citation, NOT refit; DESIGN.md pinned).
M51_TRI_P = {
    "s0": {257: 25, 277: 25, 296: 26, 301: 27, 321: 25, 340: 26,
           342: 27, 343: 27},
    "m15": {257: 25, 277: 25, 296: 26, 301: 27, 321: 26, 340: 32,
            342: 27, 343: 289},
}
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


def hump_metrics(rows: np.ndarray, deltas: np.ndarray):
    """Hump metrics (M26 DESIGN.md pinned, no special-casing)."""
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


# ---- M53 tie + plateau machinery (DESIGN.md pinned) ----

def third_of(k: int, n: int) -> str:
    """Index-thirds convention (M26 verbatim formula)."""
    return "top" if 3 * k < n else ("bottom" if 3 * k >= 2 * n else "mid")


def row_runs(present_rows, vals, target) -> list:
    """Maximal runs of ROW-NUMBER-consecutive present rows whose value
    equals target (a hole breaks a run). Returns list of row lists."""
    out, cur = [], []
    for r, x in zip(present_rows, vals):
        r, x = int(r), int(x)
        if x == target and cur and r == cur[-1] + 1:
            cur.append(r)
        elif x == target and not cur:
            cur = [r]
        elif x == target:
            out.append(cur)
            cur = [r]
        else:
            if cur:
                out.append(cur)
                cur = []
    if cur:
        out.append(cur)
    return out


def tie_info(rows: np.ndarray, deltas: np.ndarray):
    """All-tie rows + max-tie runs + tie shape (DESIGN.md pinned)."""
    rr = [int(r) for r in rows]
    dd = [int(x) for x in deltas]
    m = max(dd)
    tierows = [r for r, x in zip(rr, dd) if x == m]
    runs = row_runs(rr, dd, m)
    t = len(tierows)
    if t == 1:
        shape = "singleton"
    elif len(runs) == 1:
        shape = "run"
    elif all(len(run) == 1 for run in runs):
        shape = "scattered"
    else:
        shape = "multirun"
    return {"max": m, "T": t, "rows": tierows, "runs": runs,
            "shape": shape}


def plateau_census(rows: np.ndarray, deltas: np.ndarray):
    """Maximal equal-d runs with L>=2, row-number-consecutive
    (DESIGN.md pinned). Returns list of (start, end, val, L)."""
    rr = [int(r) for r in rows]
    dd = [int(x) for x in deltas]
    out, s, p, v = [], None, None, None
    for r, x in list(zip(rr, dd)) + [(None, None)]:
        if r is not None and s is not None and x == v and r == p + 1:
            p = r
            continue
        if s is not None and p - s + 1 >= 2:
            out.append((s, p, v, p - s + 1))
        if r is None:
            break
        s, p, v = r, r, x
    return out


def census_str(census) -> str:
    if not census:
        return "none"
    return ";".join(f"{s}-{e}:{v}x{L}" for s, e, v, L in census)


def runcenter_r1(rows: np.ndarray, tinfo):
    """R1 middle-of-longest-run (PRIMARY, DESIGN.md pinned). Returns
    (peakrow, k, third)."""
    rr = [int(r) for r in rows]
    runs = tinfo["runs"]
    best = max(range(len(runs)), key=lambda i: (len(runs[i]), -runs[i][0]))
    run = runs[best]
    peak = run[(len(run) - 1) // 2]  # lower-middle for even L
    k = rr.index(peak)
    return peak, k, third_of(k, len(rr))


def runcenter_r2(rows: np.ndarray, tinfo):
    """R2 mean-of-ties, rhalf (AUXILIARY, DESIGN.md pinned). Returns
    (peakrow, present, kprime, third)."""
    rr = [int(r) for r in rows]
    peak = rhalf(sum(tinfo["rows"]) / len(tinfo["rows"]))
    present = peak in set(rr)
    kp = sum(1 for r in rr if r < peak)
    return peak, present, kp, third_of(kp, len(rr))


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

    # Hump metrics (M26 Task 1.1/1.2, M26-identical: guard input).
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


def m26_match_lines(tag, lines, m26text: str):
    """Task 1 guard: hump lines byte-exact vs m26.txt or stop."""
    L = []
    pat = re.compile(rf"^{tag} hump c=\d+")
    want = [ln for ln in m26text.splitlines() if pat.match(ln)]
    got = [ln for ln in lines if pat.match(ln)]
    ok = got == want
    L.append(f"{tag} m26match: lines={len(got)}/{len(want)} match={ok}")
    if not ok:
        for i, (g, w) in enumerate(zip(got, want)):
            if g != w:
                L.append(f"{tag} m26match FIRSTDIFF idx={i}")
                L.append(f"  got:  {g}")
                L.append(f"  want: {w}")
                break
        if len(got) != len(want):
            L.append(f"{tag} m26match LEN differs: STOP, tabled.")
    return L, ok


def m26_xshape_match_lines(lines, m26text: str):
    """Task 1 guard: xshape lines byte-exact vs m26.txt or stop."""
    L = []
    pat = re.compile(r"^xshape ")
    want = [ln for ln in m26text.splitlines() if pat.match(ln)]
    got = [ln for ln in lines if pat.match(ln)]
    ok = got == want
    L.append(f"xshape m26match: lines={len(got)}/{len(want)} match={ok}")
    if not ok:
        for i, (g, w) in enumerate(zip(got, want)):
            if g != w:
                L.append("xshape m26match FIRSTDIFF "
                         f"idx={i}")
                L.append(f"  got:  {g}")
                L.append(f"  want: {w}")
                break
        if len(got) != len(want):
            L.append("xshape m26match LEN differs: STOP, tabled.")
    return L, ok


def xshape_lines(art0, art15):
    """Task 1.3: per-column s0-vs-m15 shape match (M26-identical)."""
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


def task1_tie_lines(tag, art):
    """Task 1.2/1.3: all-tie rows + tie shapes + submax census."""
    L = []
    for ccol in NAMED_COLS:
        pr = art["profs"][ccol]
        ti = tie_info(pr["rows"], pr["d"])
        pr["tie"] = ti
        L.append(f"{tag} tie c={ccol}: max={ti['max']} T={ti['T']} "
                 f"rows={ti['rows']}")
        L.append(f"{tag} tieshape c={ccol}: shape={ti['shape']} "
                 f"nruns={len(ti['runs'])} "
                 f"runlens={[len(r) for r in ti['runs']]} "
                 f"runs={ti['runs']}")
        cen = plateau_census(pr["rows"], pr["d"])
        pr["census"] = cen
        L.append(f"{tag} plateau c={ccol}: nruns={len(cen)} "
                 f"runs={census_str(cen)}")
    return L


def task2_rule_lines(tag, art):
    """Task 2.1: R1/R2 peaks + thirds per column per frame."""
    L = []
    for ccol in NAMED_COLS:
        pr = art["profs"][ccol]
        ft = pr["hump"]["peakrow"]
        p1, k1, t1 = runcenter_r1(pr["rows"], pr["tie"])
        pr["rc1"] = {"peak": p1, "k": k1, "third": t1}
        L.append(f"{tag} rc1 c={ccol}: peak={p1} k={k1}/{len(pr['rows'])} "
                 f"third={t1} moved={p1 != ft}")
        p2, pres2, k2, t2 = runcenter_r2(pr["rows"], pr["tie"])
        pr["rc2"] = {"peak": p2, "present": pres2, "k": k2, "third": t2}
        L.append(f"{tag} rc2 c={ccol}: peak={p2} present={pres2} "
                 f"k={k2}/{len(pr['rows'])} third={t2} moved={p2 != ft}")
    return L


def pooled_thirds_lines(rule, art0, art15):
    """Pooled thirds per rule (FT/R1/R2) per frame."""
    L = []
    for tag, art in (("s0", art0), ("m15", art15)):
        for rid, key in (("FT", "hump"), ("R1", "rc1"), ("R2", "rc2")):
            if rule != rid:
                continue
            ts = [art["profs"][c][key]["third"] for c in NAMED_COLS]
            L.append(f"topthird {rid} {tag}: "
                     f"top={ts.count('top')}/8 "
                     f"mid={ts.count('mid')}/8 "
                     f"bottom={ts.count('bottom')}/8")
    return L


def rcagree_lines(rid, key, art0, art15):
    """Task 2.2: peak-row agreement under run-center."""
    L = []
    agree = 0
    for ccol in NAMED_COLS:
        a = art0["profs"][ccol][key]["peak"]
        b = art15["profs"][ccol][key]["peak"]
        eq = a == b
        agree += 1 if eq else 0
        L.append(f"rcagree {rid} c={ccol}: s0={a} m15={b} equal={eq}")
    L.append(f"rcagree {rid} pooled: agree={agree}/8 "
             f"share={agree / 8:.4f}")
    return L


def trip_lines(art0, art15):
    """Task 2.3: TRI-p impact (M51 p cited, not refit)."""
    L = []
    for ccol in NAMED_COLS:
        for tag, art in (("s0", art0), ("m15", art15)):
            pr = art["profs"][ccol]
            pc = M51_TRI_P[tag][ccol]
            r1 = pr["rc1"]["peak"]
            r2 = pr["rc2"]["peak"]
            L.append(f"trip c={ccol} {tag}: p_cited={pc} rc1={r1} "
                     f"pimpact={r1 != pc} rc2={r2} pimpact2={r2 != pc}")
    return L


def main():
    m16d, m15d, m25t, m26t, workd, evidd = (Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0+m15)
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
    m26text = m26t.read_text(errors="replace")
    print(f"input {m26t}: bytes={len(m26text)} "
          f"sha256={hashlib.sha256(m26text.encode()).hexdigest()}")

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
        print("MISMATCH vs M17-M52 baselines: STOP, tabled.")
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
    print("== Task 1: M26 hump-line match s0 ==")
    LH0, okh0 = m26_match_lines("s0", L0, m26text)
    for ln in LH0:
        print(ln)
    if not okh0:
        print("M26 HUMP MISMATCH on s0: STOP, tabled.")
        return
    print("== Task 1: profiles m15 ==")
    t1 = time.time()
    L15, art15 = task1_profile_lines("m15", v015, mid15, full15, b15, rr,
                                     cc, pl)
    for ln in L15:
        print(ln)
        canon.append(ln)
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
    print("== Task 1: M26 hump-line match m15 ==")
    LH15, okh15 = m26_match_lines("m15", L15, m26text)
    for ln in LH15:
        print(ln)
    if not okh15:
        print("M26 HUMP MISMATCH on m15: STOP, tabled.")
        return
    print(f"self jaccard s0={jaccard(art0['tail'], art0['tail']):.4f} "
          f"(want 1.0) m15={jaccard(art15['tail'], art15['tail']):.4f}")

    print("== Task 1.3: cross-frame shape match ==")
    LX = xshape_lines(art0, art15)
    for ln in LX:
        print(ln)
        canon.append(ln)
    print("== Task 1: M26 xshape-line match ==")
    LXm, okx = m26_xshape_match_lines(LX, m26text)
    for ln in LXm:
        print(ln)
    if not okx:
        print("M26 XSHAPE MISMATCH: STOP, tabled.")
        return

    print("== Task 1: first-tie thirds pooled ==")
    for ln in pooled_thirds_lines("FT", art0, art15):
        print(ln)

    print("== Task 1.2/1.3: all-tie rows + shapes + census s0 ==")
    LT0 = task1_tie_lines("s0", art0)
    for ln in LT0:
        print(ln)
        canon.append(ln)
    print("== Task 1.2/1.3: all-tie rows + shapes + census m15 ==")
    LT15 = task1_tie_lines("m15", art15)
    for ln in LT15:
        print(ln)
        canon.append(ln)

    # ---- Task 2.1: run-center peaks + thirds ----
    print("== Task 2.1: run-center peaks s0 ==")
    for ln in task2_rule_lines("s0", art0):
        print(ln)
    print("== Task 2.1: run-center peaks m15 ==")
    for ln in task2_rule_lines("m15", art15):
        print(ln)
    print("== Task 2.1: thirds pooled under run-center ==")
    for ln in pooled_thirds_lines("R1", art0, art15):
        print(ln)
    for ln in pooled_thirds_lines("R2", art0, art15):
        print(ln)

    # ---- Task 2.2: agreement under run-center ----
    print("== Task 2.2: agreement under run-center ==")
    for ln in rcagree_lines("R1", "rc1", art0, art15):
        print(ln)
    for ln in rcagree_lines("R2", "rc2", art0, art15):
        print(ln)

    # ---- Task 2.3: TRI-p impact (M51 p cited, not refit) ----
    print("== Task 2.3: M51 p-citation check ==")
    pck = []
    for ccol in NAMED_COLS:
        for tag, art in (("s0", art0), ("m15", art15)):
            ft = art["profs"][ccol]["hump"]["peakrow"]
            pc = M51_TRI_P[tag][ccol]
            pck.append(pc == ft)
            print(f"pcheck c={ccol} {tag}: p_cited={pc} "
                  f"firsttie={ft} match={pc == ft}")
    if not all(pck):
        print("M51 P-CITATION MISMATCH: STOP Task 2.3 only, tabled.")
    else:
        print("== Task 2.3: TRI-p impact ==")
        for ln in trip_lines(art0, art15):
            print(ln)

    # ---- determinism re-run (Task 1 on s0+m15, second pass) ----
    print("== determinism re-run (Task 1 on s0+m15, second pass) ==")
    L0b, art0b = task1_profile_lines("s0", v0, mid, full, b0, rr, cc, pl)
    L15b, art15b = task1_profile_lines("m15", v015, mid15, full15, b15,
                                       rr, cc, pl)
    LXb = xshape_lines(art0b, art15b) if art0b and art15b else []
    LT0b = task1_tie_lines("s0", art0b) if art0b else []
    LT15b = task1_tie_lines("m15", art15b) if art15b else []
    canon2 = L0b + L15b + LXb + LT0b + LT15b
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical="
          f"{art0b is not None and art15b is not None
              and art0['n'] == art0b['n'] and art15['n'] == art15b['n']}"
          f" tail counts identical="
          f"{art0b is not None and art15b is not None
              and art0['nt'] == art0b['nt'] and art15['nt'] == art15b['nt']}")

    # ---- PNG plateau map (work dir; evidence copy iff per rule) ----
    print("== PNG plateau map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    over = (0.35 * rgbm.astype(np.float32))
    n_run, n_sing, n_other = 0, 0, 0
    for ccol in NAMED_COLS:
        pr = art0["profs"][ccol]
        ti = pr["tie"]
        runrows = set()
        for run in ti["runs"]:
            if len(run) >= 2:
                runrows.update(run)
        tierows = set(ti["rows"])
        for r in pr["rows"]:
            r = int(r)
            if r in runrows:
                over[r, ccol] = (0, 255, 0)
                n_run += 1
            elif r in tierows:
                over[r, ccol] = (255, 255, 0)
                n_sing += 1
            else:
                over[r, ccol] = (255, 0, 0)
                n_other += 1
    p = workd / "m53-plateaumap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: green=max-tie-run-member n={n_run} "
          f"yellow=singleton/scattered-max-tie n={n_sing} "
          f"red=other n={n_other} (s0 named-col tail Y only)")
    split = [(c, art0["profs"][c]["hump"]["peakrow"],
              art0["profs"][c]["rc1"]["peak"])
             for c in NAMED_COLS if len(art0["profs"][c]["rows"]) >= 8]
    qual = [c for c, ft, r1 in split if ft != r1]
    print(f"pngrule: s0 n>=8 cols={sorted(c for c, _, _ in split)} "
          f"R1-moved={qual} evidence_copy={len(qual) > 0}")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=plateau-ties T2=run-center R=controls")


if __name__ == "__main__":
    main()
