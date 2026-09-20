#!/usr/bin/env python3
"""M52 peak-row vs value agreement: peak-anchored residual tables.

Usage: m52.py M16_DIR M15_DIR M25_TXT M26_TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet, the M25
receipt (H5 xmatch lines to reproduce) and the M26 receipt (hump +
xshape lines to reproduce); raw XFB dumps, 573440 B = 640x448 YUYV.
Read-only inputs; receipt text goes to stdout (redirect to
WORK_DIR/m52.txt); PNG residual-agreement map to WORK_DIR (evidence
copy iff discriminating per DESIGN.md, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: H5 + peak reproduction (agree sites + peaks + peak x agree join)
  2: peak-anchored residuals (residual + distance + residual-agreement)
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
# H5 pins (M25): pooled 6/65; per-column agrees over shared n.
M25_H5_AGREE = {257: 0, 277: 0, 296: 1, 301: 0, 321: 2, 340: 2, 342: 0,
                343: 1}
M25_H5_SHARED = {257: 10, 277: 10, 296: 9, 301: 11, 321: 10, 340: 8,
                 342: 5, 343: 2}
# Peak pins (M26): (s0 peakrow, m15 peakrow); agree 5/8.
M26_PEAKS = {257: (25, 25), 277: (25, 25), 296: (26, 26), 301: (27, 27),
             321: (25, 26), 340: (26, 32), 342: (27, 27), 343: (27, 289)}
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


# ---- peak-anchored machinery (DESIGN.md pinned, exact integer arith) ----

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


def peak_residual(rows: np.ndarray, deltas: np.ndarray):
    """Peak-anchored residual (DESIGN.md pinned, exact integer arith).

    Peak = argmax first-on-ties (hump_metrics); res = delta - peakval;
    off = row - peakrow (signed); dist = |off|. Returns (hump, res,
    off, dist) as int64 arrays aligned with the input row order."""
    hm = hump_metrics(rows, deltas)
    p, h = hm["peakrow"], hm["peakval"]
    rr = rows.astype(np.int64)
    dd = deltas.astype(np.int64)
    res = dd - h
    off = rr - p
    return hm, res, off, np.abs(off)


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


def xshape_lines(art0, art15, cols=NAMED_COLS):
    """Task 1.3: per-column s0-vs-m15 shape match."""
    L = []
    peakagree = 0
    for ccol in cols:
        h0 = art0["profs"][ccol]["hump"]
        h1 = art15["profs"][ccol]["hump"]
        peq = h0["peakrow"] == h1["peakrow"]
        peakagree += 1 if peq else 0
        L.append(f"xshape c={ccol}: peakrow s0={h0['peakrow']} "
                 f"m15={h1['peakrow']} equal={peq} "
                 f"risefall s0=({h0['rise']},{h0['fall']}) "
                 f"m15=({h1['rise']},{h1['fall']}) "
                 f"third s0={h0['third']} m15={h1['third']}")
    L.append(f"xshape pooled H5: peakagree={peakagree}/{len(cols)} "
             f"share={peakagree / len(cols):.4f}")
    return L


# ---- Task 1: H5 + peak reproduction (M25/M26-verbatim) ----

def xframe_match_lines(art0, art15, cols=NAMED_COLS):
    """Task 1.1 xmatch: per-column s0-vs-m15 profile match (M25-verbatim,
    byte-identical format for the m25.txt guard)."""
    L = []
    shared_all, agree_all = 0, 0
    for ccol in cols:
        p0, p1 = art0["profs"][ccol], art15["profs"][ccol]
        m0 = {int(r): int(x) for r, x in zip(p0["rows"], p0["d"])}
        m1 = {int(r): int(x) for r, x in zip(p1["rows"], p1["d"])}
        s0rows, m15rows = set(m0), set(m1)
        shared = sorted(s0rows & m15rows)
        s0only = sorted(s0rows - m15rows)
        m15only = sorted(m15rows - s0rows)
        agree = sum(1 for r in shared if m0[r] == m1[r])
        mad = (sum(abs(m0[r] - m1[r]) for r in shared) / len(shared)
               if shared else float("nan"))
        shared_all += len(shared)
        agree_all += agree
        L.append(f"xmatch c={ccol}: rows_equal={s0rows == m15rows} "
                 f"shared={len(shared)} s0only={s0only} "
                 f"m15only={m15only} agree={agree} "
                 f"all_equal={agree == len(shared) and len(shared) > 0} "
                 f"meanabsdiff={mad:.3f}")
    share = agree_all / shared_all if shared_all else 0.0
    L.append(f"xmatch pooled H5: shared={shared_all} agree={agree_all} "
             f"share={share:.4f}")
    return L


def agree_site_lines(art0, art15, cols=NAMED_COLS):
    """Task 1.1: one line per shared site (col,row order): s0-d vs
    m15-d + agree flag + |diff|. Returns (lines, agree_sites)."""
    L = []
    agree_sites = []
    n = 0
    for ccol in cols:
        p0, p1 = art0["profs"][ccol], art15["profs"][ccol]
        m0 = {int(r): int(x) for r, x in zip(p0["rows"], p0["d"])}
        m1 = {int(r): int(x) for r, x in zip(p1["rows"], p1["d"])}
        for r in sorted(set(m0) & set(m1)):
            ag = m0[r] == m1[r]
            n += 1
            if ag:
                agree_sites.append((ccol, r))
            L.append(f"agree c={ccol} r={r}: s0d={m0[r]} m15d={m1[r]} "
                     f"agree={ag} absdiff={abs(m0[r] - m1[r])}")
    L.append(f"agree pooled: shared={n} agree={len(agree_sites)} "
             f"sites={agree_sites}")
    return L, agree_sites


def peakjoin_lines(art0, art15, agree_sites, cols=NAMED_COLS):
    """Task 1.3: per-column peak-agree x n-agree + pooled split (do
    peak-agreeing columns hold the agrees?)."""
    L = []
    in_n, in_ag, out_n, out_ag = 0, 0, 0, 0
    for ccol in cols:
        h0 = art0["profs"][ccol]["hump"]
        h1 = art15["profs"][ccol]["hump"]
        peq = h0["peakrow"] == h1["peakrow"]
        nag = sum(1 for (c, _) in agree_sites if c == ccol)
        p0, p1 = art0["profs"][ccol], art15["profs"][ccol]
        nsh = len(set(int(r) for r in p0["rows"])
                  & set(int(r) for r in p1["rows"]))
        if peq:
            in_n += nsh
            in_ag += nag
        else:
            out_n += nsh
            out_ag += nag
        L.append(f"peakjoin c={ccol}: peakagree={peq} shared={nsh} "
                 f"agree={nag}")
    L.append(f"peakjoin pooled: in-peakagree-cols shared={in_n} "
             f"agree={in_ag}; outside shared={out_n} agree={out_ag}")
    return L


# ---- Task 2: peak-anchored residuals (DESIGN.md pinned) ----

def resid_lines(tag, art, cols=NAMED_COLS):
    """Task 2.1: per column: peak p/h + row-order (row:d:res:off) quads
    via peak_residual (same code path as control.py)."""
    L = []
    for ccol in cols:
        pr = art["profs"][ccol]
        hm, res, off, _ = peak_residual(pr["rows"], pr["d"])
        quads = " ".join(
            f"{int(r)}:{int(x)}:{int(s)}:{int(o)}"
            for r, x, s, o in zip(pr["rows"], pr["d"], res, off))
        L.append(f"{tag} resid c={ccol}: peak={hm['peakrow']}/"
                 f"{hm['peakval']} n={len(pr['rows'])} quads: {quads}")
    return L


def dist_table(art0, art15, cols=NAMED_COLS):
    """Task 2.2 core: per-shared-site dicts with d_s0/d_m15, res_s0/
    res_m15, agree flags. Shared code path (control.py runs this exact
    function on listed profiles)."""
    rows = []
    for ccol in cols:
        p0, p1 = art0["profs"][ccol], art15["profs"][ccol]
        h0, res0, _, d0 = peak_residual(p0["rows"], p0["d"])
        h1, res1, _, d1 = peak_residual(p1["rows"], p1["d"])
        m0 = {int(r): (int(x), int(s), int(q))
              for r, x, s, q in zip(p0["rows"], p0["d"], res0, d0)}
        m1 = {int(r): (int(x), int(s), int(q))
              for r, x, s, q in zip(p1["rows"], p1["d"], res1, d1)}
        for r in sorted(set(m0) & set(m1)):
            x0, s0, q0 = m0[r]
            x1, s1, q1 = m1[r]
            rows.append({"c": ccol, "r": r, "d0": x0, "d1": x1,
                         "agd": x0 == x1, "adiff": abs(x0 - x1),
                         "q0": q0, "q1": q1, "s0": s0, "s1": s1,
                         "agr": s0 == s1,
                         "rdiff": abs(s0 - s1)})
    return rows


def dist_lines(distrows):
    """Task 2.2: one line per shared site: distances vs agree flags."""
    L = []
    for t in distrows:
        L.append(f"dist c={t['c']} r={t['r']}: s0d={t['d0']} "
                 f"m15d={t['d1']} agree_d={t['agd']} "
                 f"d_s0={t['q0']} d_m15={t['q1']} "
                 f"res_s0={t['s0']} res_m15={t['s1']} "
                 f"agree_res={t['agr']}")
    return L


def distmarg_lines(distrows):
    """Task 2.2 marginals: d-agree + res-agree rates by d_s0 / d_m15
    bin (0/1/2/3/4+), pooled over shared sites."""
    L = []
    for key, lab in (("q0", "d_s0"), ("q1", "d_m15")):
        cells = []
        for lo, hi, nm in ((0, 0, "0"), (1, 1, "1"), (2, 2, "2"),
                           (3, 3, "3"), (4, 1 << 30, "4+")):
            sel = [t for t in distrows if lo <= t[key] <= hi]
            n = len(sel)
            ad = sum(1 for t in sel if t["agd"])
            ar = sum(1 for t in sel if t["agr"])
            cells.append(f"{nm}:n={n},agd={ad},agr={ar}")
        L.append(f"distmarg {lab}: " + " ".join(cells))
    n = len(distrows)
    ad0 = sum(1 for t in distrows if t["agd"] and t["q0"] == 0)
    ad15 = sum(1 for t in distrows if t["agd"] and t["q1"] == 0)
    ar0 = sum(1 for t in distrows if t["agr"] and t["q0"] == 0)
    L.append(f"distmarg pooled: shared={n} "
             f"agd_at_d0s0={ad0} agd_at_d0m15={ad15} "
             f"agr_at_d0s0={ar0}")
    return L


def xres_lines(art0, art15, distrows, cols=NAMED_COLS):
    """Task 2.3: H5 re-scored on peak-subtracted residuals (xmatch
    format + near counts). Same shared sets as H5."""
    L = []
    byc = {}
    for t in distrows:
        byc.setdefault(t["c"], []).append(t)
    sh_all, ag_all, nr_all = 0, 0, 0
    for ccol in cols:
        sel = byc.get(ccol, [])
        n = len(sel)
        ag = sum(1 for t in sel if t["agr"])
        nr = sum(1 for t in sel if (not t["agr"]) and t["rdiff"] == 1)
        sh_all += n
        ag_all += ag
        nr_all += nr
        L.append(f"xres c={ccol}: shared={n} resagree={ag} "
                 f"share={ag / n if n else 0.0:.4f} near={nr} "
                 f"sites={sorted(t['r'] for t in sel if t['agr'])}")
    L.append(f"xres pooled: shared={sh_all} resagree={ag_all} "
             f"share={ag_all / sh_all if sh_all else 0.0:.4f} "
             f"near={nr_all}")
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
        print("MISMATCH vs M17-M51 baselines: STOP, tabled.")
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
    print(f"self jaccard s0={jaccard(art0['tail'], art0['tail']):.4f} "
          f"(want 1.0) m15={jaccard(art15['tail'], art15['tail']):.4f}")

    print("== Task 1.1: H5 xmatch (M25-verbatim) + guard ==")
    LX = xframe_match_lines(art0, art15)
    for ln in LX:
        print(ln)
        canon.append(ln)
    wantx = [ln for ln in m25text.splitlines() if ln.startswith("xmatch")]
    okx = LX == wantx
    print(f"xmatch m25match: lines={len(LX)}/{len(wantx)} match={okx}")
    if not okx:
        for i, (g, w) in enumerate(zip(LX, wantx)):
            if g != w:
                print(f"xmatch m25match FIRSTDIFF idx={i}")
                print(f"  got:  {g}")
                print(f"  want: {w}")
                break
        if len(LX) != len(wantx):
            print("xmatch m25match LEN differs: STOP, tabled.")
        print("M25 H5 MISMATCH: STOP, tabled.")
        return
    LA, agsites = agree_site_lines(art0, art15)
    for ln in LA:
        print(ln)
    h5pin = [f"c{c}={sum(1 for (cc, _) in agsites if cc == c)}/"
             f"{M25_H5_AGREE[c]}" for c in NAMED_COLS]
    print(f"H5 pins: pooled agree={len(agsites)}/6 "
          f"per-column got/want: {' '.join(h5pin)}")

    print("== Task 1.2: peaks (M26-verbatim) + guard ==")
    LH = [ln for ln in L0 + L15
          if re.match(r"^(s0|m15) hump c=", ln)]
    LXS = xshape_lines(art0, art15)
    for ln in LXS:
        print(ln)
        canon.append(ln)
    wanth = [ln for ln in m26text.splitlines()
             if re.match(r"^(s0|m15) hump c=", ln)]
    wantxs = [ln for ln in m26text.splitlines() if ln.startswith("xshape")]
    okh = LH == wanth
    okxs = LXS == wantxs
    print(f"hump m26match: lines={len(LH)}/{len(wanth)} match={okh}")
    print(f"xshape m26match: lines={len(LXS)}/{len(wantxs)} match={okxs}")
    if not (okh and okxs):
        for lab, g, w in (("hump", LH, wanth), ("xshape", LXS, wantxs)):
            for i, (gg, ww) in enumerate(zip(g, w)):
                if gg != ww:
                    print(f"{lab} m26match FIRSTDIFF idx={i}")
                    print(f"  got:  {gg}")
                    print(f"  want: {ww}")
                    break
            if len(g) != len(w):
                print(f"{lab} m26match LEN differs: STOP, tabled.")
        print("M26 PEAK MISMATCH: STOP, tabled.")
        return
    pkpin = " ".join(
        f"c{c}={art0['profs'][c]['hump']['peakrow']}/"
        f"{art15['profs'][c]['hump']['peakrow']}"
        f"(want {M26_PEAKS[c][0]}/{M26_PEAKS[c][1]})"
        for c in NAMED_COLS)
    print(f"peak pins: {pkpin}")

    print("== Task 1.3: peak x agree join ==")
    for ln in peakjoin_lines(art0, art15, agsites):
        print(ln)

    # ---- Task 2.1: peak-anchored residual tables ----
    print("== Task 2.1: residual tables s0 ==")
    for ln in resid_lines("s0", art0):
        print(ln)
    print("== Task 2.1: residual tables m15 ==")
    for ln in resid_lines("m15", art15):
        print(ln)

    # ---- Task 2.2: distance table + marginals ----
    print("== Task 2.2: distance table ==")
    dtab = dist_table(art0, art15)
    for ln in dist_lines(dtab):
        print(ln)
    for ln in distmarg_lines(dtab):
        print(ln)

    # ---- Task 2.3: residual agreement (H5 re-scored) ----
    print("== Task 2.3: residual agreement ==")
    LR = xres_lines(art0, art15, dtab)
    for ln in LR:
        print(ln)
    # PNG-rule input: per-column residual-agrees minus d-agrees.
    pngcells = []
    for ccol in NAMED_COLS:
        sel = [t for t in dtab if t["c"] == ccol]
        nsh = len(sel)
        ad = sum(1 for t in sel if t["agd"])
        ar = sum(1 for t in sel if t["agr"])
        pngcells.append(f"c{ccol}:nsh={nsh},agd={ad},agr={ar},"
                        f"gap={ar - ad}")
    print("pngrule: " + " ".join(pngcells))

    # ---- determinism re-run (Task 1 on s0+m15, canonical text) ----
    print("== determinism re-run (Task 1 on s0+m15, second pass) ==")
    L0b, art0b = task1_profile_lines("s0", v0, mid, full, b0, rr, cc, pl)
    L15b, art15b = task1_profile_lines("m15", v015, mid15, full15, b15, rr,
                                       cc, pl)
    okb = art0b is not None and art15b is not None
    LXb = xframe_match_lines(art0b, art15b) if okb else []
    LXSb = xshape_lines(art0b, art15b) if okb else []
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b + L15b + LXb + LXSb).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={okb and art0['n'] == art0b['n'] and art15['n'] == art15b['n']}"
          f" tail counts identical="
          f"{okb and art0['nt'] == art0b['nt'] and art15['nt'] == art15b['nt']}")

    # ---- PNG residual map (work dir; evidence copy iff per rule) ----
    print("== PNG residual map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    resmap = {(t["c"], t["r"]): t for t in dtab}
    nag = nnr = ndi = nun = 0
    for ccol in NAMED_COLS:
        for r in art0["profs"][ccol]["rows"]:
            t = resmap.get((ccol, int(r)))
            if t is None:
                over[int(r), ccol] = (128, 128, 128)
                nun += 1
            elif t["agr"]:
                over[int(r), ccol] = (0, 255, 0)
                nag += 1
            elif t["rdiff"] == 1:
                over[int(r), ccol] = (255, 255, 0)
                nnr += 1
            else:
                over[int(r), ccol] = (255, 0, 0)
                ndi += 1
    p = workd / "m52-resmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.NEAREST).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: green=res-agree n={nag} yellow=res-near n={nnr} "
          f"red=res-disagree n={ndi} grey=unshared n={nun} "
          f"(s0 named-col tail Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=h5-peaks T2=residuals R=controls")


if __name__ == "__main__":
    main()
