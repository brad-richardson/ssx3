#!/usr/bin/env python3
"""M39 s3 all-delta-1 row: row-list + value comparison vs mixed cells (offline).

Usage: m39.py M16_DIR M15_DIR M34TSV M36TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), m34-census.tsv (FULL TSV guard), and m36.txt (s3's 7
cells + the 3 mixed cells to reproduce); raw XFB dumps,
573440 B = 640x448 YUYV. Read-only inputs; receipt text goes to
stdout (redirect to WORK_DIR/m39.txt); PNG uniformity map to
WORK_DIR (evidence copy iff the DESIGN.md rule meets, decided
at report time).

Tasks (see DESIGN.md, recorded before running):
  1: s3 row + mixed cells recompute (row-lists + standings + values)
  2: uniformity comparison (extra-side + missing-side + delta split)
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
M34_FOLD = ("6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e"
            "61fd423b1")
M19_CELL_S0 = 2475  # s2/s3/s700 cell counts: M36-measured, guarded equal
M20_TAIL_S0 = 102
M20_TAIL_S0_SUB = (28, 74)  # (8-15, 16+)
M20_TAIL_S0_MAX = 47
M19_POSRATE_S0 = 0.8093  # P(d>0) on s0 cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
NAMED8 = [257, 277, 296, 301, 321, 340, 342, 343]
# Per-shape pins from the M34 TSV rows (shapes 2/3/700, read before running).
# NOV: {col: (n, ov)}; N0: {col: s0 n}; STAND: {col: (miss, extra, delta, stand)}.
SHAPES = {
    2: {"tail": 103, "jacc": "0.9159",
        "moved": [311, 312, 313, 314, 332, 339],
        "nov": {311: (5, 4), 312: (2, 2), 313: (4, 3), 314: (6, 6),
                332: (3, 1), 339: (1, 0)},
        "n0": {311: 4, 312: 3, 313: 4, 314: 7, 332: 2, 339: 0},
        "stand": {311: (0, 1, 1, "extra"), 312: (1, 0, 1, "missing"),
                  313: (1, 1, 2, "mixed"), 314: (1, 0, 1, "missing"),
                  332: (1, 2, 3, "mixed"), 339: (0, 1, 1, "extra")},
        "pool": (5, 4)},  # (extras, missings)
    3: {"tail": 103, "jacc": "0.9340",
        "moved": [311, 313, 314, 316, 332, 336, 339],
        "nov": {311: (5, 4), 313: (3, 3), 314: (6, 6), 316: (2, 1),
                332: (1, 1), 336: (1, 0), 339: (1, 0)},
        "n0": {311: 4, 313: 4, 314: 7, 316: 1, 332: 2, 336: 0,
               339: 0},
        "stand": {311: (0, 1, 1, "extra"), 313: (1, 0, 1, "missing"),
                  314: (1, 0, 1, "missing"), 316: (0, 1, 1, "extra"),
                  332: (1, 0, 1, "missing"), 336: (0, 1, 1, "extra"),
                  339: (0, 1, 1, "extra")},
        "pool": (4, 3)},
    700: {"tail": 114, "jacc": "0.8462",
          "moved": [38, 54, 299, 311, 313, 314, 332, 620],
          "nov": {38: (0, 0), 54: (10, 0), 299: (1, 0), 311: (5, 4),
                  313: (5, 4), 314: (6, 6), 332: (2, 1), 620: (1, 0)},
          "n0": {38: 1, 54: 0, 299: 0, 311: 4, 313: 4, 314: 7,
                 332: 2, 620: 0},
          "stand": {38: (1, 0, 1, "missing"), 54: (0, 10, 10, "extra"),
                    299: (0, 1, 1, "extra"), 311: (0, 1, 1, "extra"),
                    313: (0, 1, 1, "extra"), 314: (1, 0, 1, "missing"),
                    332: (1, 1, 2, "mixed"), 620: (0, 1, 1, "extra")},
          "pool": (15, 3)},
}
QLIST = [2, 3, 700]
# M36-measured s0+Q cell-7 counts (M36 REPORT baseline note; guard: equal or stop).
M36_CELL = {2: 2469, 3: 2484, 700: 2605}
# Brief universe: s3's 7 delta-1 cells + the 3 mixed cells (10 cells,
# 8 extra sites + 6 missing sites = 14 sites).
BRIEF_CELLS = {3: [311, 313, 314, 316, 332, 336, 339],
               2: [313, 332], 700: [332]}
# Row-list pins (M36 REPORT + m36.txt headliner; s0 c316 measured,
# n0=1 only — M36 states the count, not the row).
S0ROWS = {311: [296, 297, 298, 299], 313: [274, 275, 276, 292],
          314: [269, 276, 277, 278, 287, 288, 289], 332: [295, 304],
          336: [], 339: []}
EXTRAROWS = {(3, 311): [258], (3, 316): [265], (3, 336): [238],
             (3, 339): [238], (2, 313): [293], (2, 332): [296, 297],
             (700, 332): [296]}
MISSROWS = {(3, 313): [276], (3, 314): [278], (3, 332): [295],
            (2, 313): [276], (2, 332): [295], (700, 332): [295]}
# M36 full missing pins: (Q, r, c) -> (offset, |d_s0|, qstat, g_s0, g_Q).
M36_MISS = {
    (2, 299, 312): (383344, 10, "noncell", 22, 22),
    (2, 276, 313): (353906, 8, "noncell", 17, 16),
    (2, 278, 314): (356468, 20, "noncell", 42, 40),
    (2, 295, 332): (378264, 10, "noncell", -22, -21),
    (3, 276, 313): (353906, 8, "noncell", 17, 16),
    (3, 278, 314): (356468, 20, "noncell", 42, 42),
    (3, 295, 332): (378264, 10, "noncell", -22, -21),
    (700, 215, 38): (275276, 12, "noncell", 25, 23),
    (700, 278, 314): (356468, 20, "noncell", 42, 42),
    (700, 295, 332): (378264, 10, "noncell", -22, -21),
}
# M36 24-site extra pins: (Q, r, c) -> (offset, adQ, ostat, adO|None, gQ, gO).
M36_EXTRAS = {
    (2, 259, 311): (332142, 17, "noncell", None, -37, -37),
    (2, 293, 313): (375666, 8, "bulk", 7, -18, -19),
    (2, 296, 332): (379544, 20, "noncell", None, -41, -41),
    (2, 297, 332): (380824, 9, "noncell", None, -20, -20),
    (2, 240, 339): (307878, 9, "noncell", None, 19, 17),
    (3, 258, 311): (330862, 34, "noncell", None, -71, -71),
    (3, 265, 316): (339832, 8, "bulk", 7, 18, 18),
    (3, 238, 336): (305312, 8, "bulk", 7, 17, 16),
    (3, 238, 339): (305318, 8, "noncell", None, 17, 18),
    (700, 245, 54): (313708, 8, "bulk", 7, -23, -22),
    (700, 246, 54): (314988, 8, "bulk", 7, -23, -23),
    (700, 247, 54): (316268, 8, "bulk", 7, -24, -23),
    (700, 252, 54): (322668, 8, "bulk", 7, -22, -21),
    (700, 253, 54): (323948, 8, "bulk", 7, -23, -22),
    (700, 258, 54): (330348, 8, "bulk", 7, -23, -22),
    (700, 259, 54): (331628, 8, "bulk", 7, -22, -22),
    (700, 278, 54): (355948, 8, "bulk", 6, -22, -21),
    (700, 279, 54): (357228, 8, "bulk", 6, -22, -21),
    (700, 283, 54): (362348, 8, "bulk", 7, -22, -21),
    (700, 25, 299): (32598, 34, "noncell", None, -71, -72),
    (700, 259, 311): (332142, 17, "noncell", None, -37, -37),
    (700, 291, 313): (373106, 8, "bulk", 7, -19, -19),
    (700, 296, 332): (379544, 20, "noncell", None, -42, -41),
    (700, 170, 620): (218840, 11, "noncell", None, -24, -23),
}
# Brief 14-site value pins = M36 pins restricted to the 10 brief cells.
_BRIEF_QC = {(Q, c) for Q, cs in BRIEF_CELLS.items() for c in cs}
M39_EXTRAS = {k: v for k, v in M36_EXTRAS.items()
              if (k[0], k[2]) in _BRIEF_QC}
M39_MISS = {k: v for k, v in M36_MISS.items()
            if (k[0], k[2]) in _BRIEF_QC}


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


def off_of(r: int, c: int) -> int:
    """Flat byte offset of Y site (r, c)."""
    return r * ROWB + (c // 2) * 4 + (0 if c % 2 == 0 else 2)


def y_col_rows(mask: np.ndarray, c: int, pl, pr, pc):
    """Sorted Y-tail rows of mask in column c."""
    idx = np.nonzero(mask & (pl == 0) & (pc == c))[0]
    return sorted(int(pr[o]) for o in idx)


def tail_y_cols(t: np.ndarray, pl, pr, pc):
    """Group tail-mask Y sites by column -> {col: sorted rows}."""
    out = {}
    for o in np.nonzero(t & (pl == 0))[0]:
        out.setdefault(int(pc[o]), []).append(int(pr[o]))
    return {c: sorted(v) for c, v in out.items()}


def census_unnamed_of(colrows, s0u):
    """Per-unnamed-column presence over universe s0u (exact-match rule).

    colrows: {col: rows} (missing key == []); s0u: {col: rows0}.
    Returns {col: {n, ov, pres, miss, extra, delta}}.
    """
    out = {}
    for c, r0 in s0u.items():
        rs = colrows.get(c, [])
        ov = len(set(rs) & set(r0))
        miss, extra = len(r0) - ov, len(rs) - ov
        out[c] = {"n": len(rs), "ov": ov,
                  "pres": 1 if rs == r0 else 0,
                  "miss": miss, "extra": extra, "delta": miss + extra}
    return out


PNAME = ("Y", "U", "V")


def load_triplet(m16d: Path, s: int):
    vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
    mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
    ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
    return vv, mm, ff, synth_w_bytes(vv, ff, 0.5)


def compute_sets_for(v0, mid0, full0, b0, vQ, midQ, fullQ, bQ, moved):
    """Cell-7 + tail + per-cell sets for s0+Q (shared pass 1/2)."""
    sp0 = interior_sites(v0, mid0, full0, b0)
    spQ = interior_sites(vQ, midQ, fullQ, bQ)
    mask0, d0 = sp0["mask"], sp0["delta"]
    maskQ, dQ = spQ["mask"], spQ["delta"]
    t0, _ = tail_bulk_masks(mask0, d0)
    tQ, _ = tail_bulk_masks(maskQ, dQ)
    priv = tQ & ~t0
    miss = t0 & ~tQ
    shared = tQ & t0
    pl = plane_of_byte()
    pr, pc = plane_coords()
    # per-cell extra/missing masks over this shape's unnamed cells
    cells = {}
    for c in moved:
        r0 = set(y_col_rows(t0, c, pl, pr, pc))
        rQ = set(y_col_rows(tQ, c, pl, pr, pc))
        ex = np.zeros(N, bool)
        mi = np.zeros(N, bool)
        for r in sorted(rQ - r0):
            ex[off_of(r, c)] = True
        for r in sorted(r0 - rQ):
            mi[off_of(r, c)] = True
        cells[c] = {"ex": ex, "mi": mi, "r0": sorted(r0),
                    "rQ": sorted(rQ)}
    return {"sp0": sp0, "spQ": spQ, "mask0": mask0, "d0": d0,
            "maskQ": maskQ, "dQ": dQ, "t0": t0, "tQ": tQ,
            "priv": priv, "miss": miss, "shared": shared,
            "pl": pl, "pr": pr, "pc": pc, "cells": cells}

def sgn(x):
    return "+" if x > 0 else ("-" if x < 0 else "0")


def _gaps_of(trips, v0, full0):
    g0 = (np.frombuffer(v0, np.uint8).astype(np.int16)
          - np.frombuffer(full0, np.uint8).astype(np.int16))
    gQ_of = {}
    for Q in QLIST:
        vQ, _, fullQ, _ = trips[Q]
        gQ_of[Q] = (np.frombuffer(vQ, np.uint8).astype(np.int16)
                    - np.frombuffer(fullQ, np.uint8).astype(np.int16))
    return g0, gQ_of


def _med(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def task1_canon_lines(allsets, trips, v0, full0):
    """Task 1 core: row-lists + standings + per-site values (10 cells).

    Determinism canon: depends only on s0+2+3+700 triplets.
    """
    L = []
    g0, gQ_of = _gaps_of(trips, v0, full0)
    # 1. row-list lines per brief cell
    for Q in sorted(BRIEF_CELLS):
        for c in BRIEF_CELLS[Q]:
            cell = allsets[Q]["cells"][c]
            ex = sorted(set(cell["rQ"]) - set(cell["r0"]))
            mi = sorted(set(cell["r0"]) - set(cell["rQ"]))
            L.append(f"rowlist s{Q}c{c}: s0rows={cell['r0']} "
                     f"Qrows={cell['rQ']} extra={ex} miss={mi}")
    # 2. standing lines per brief cell
    for Q in sorted(BRIEF_CELLS):
        for c in BRIEF_CELLS[Q]:
            cell = allsets[Q]["cells"][c]
            r0, rQ = cell["r0"], cell["rQ"]
            ov = len(set(rQ) & set(r0))
            mi, ex = len(r0) - ov, len(rQ) - ov
            stand = ("missing" if mi > 0 and ex == 0
                     else ("extra" if mi == 0 and ex > 0 else "mixed"))
            L.append(f"standing s{Q}c{c}: n/ov={len(rQ)}/{ov} "
                     f"n0={len(r0)} miss/extra/delta={mi}/{ex}/{mi + ex} "
                     f"stand={stand}")
    # 3. value lines per brief site
    for (Q, r, c) in sorted(M39_EXTRAS):
        o = off_of(r, c)
        S = allsets[Q]
        adQ = int(abs(int(S["dQ"][o])))
        ostat = "bulk" if S["mask0"][o] else "noncell"
        adO = int(abs(int(S["d0"][o]))) if S["mask0"][o] else None
        a, b = int(gQ_of[Q][o]), int(g0[o])
        L.append(f"value extra s{Q}c{c} rc=({r},{c}) o={o} adQ={adQ} "
                 f"ostat={ostat} adO={adO if adO is not None else 'n/a'} "
                 f"gQ={a} gO={b} sign={sgn(a)}{sgn(b)}")
    for (Q, r, c) in sorted(M39_MISS):
        o = off_of(r, c)
        S = allsets[Q]
        ad0v = int(abs(int(S["d0"][o])))
        qstat = "bulk" if S["maskQ"][o] else "noncell"
        a, b = int(g0[o]), int(gQ_of[Q][o])
        L.append(f"value miss s{Q}c{c} rc=({r},{c}) o={o} adS0={ad0v} "
                 f"qstat={qstat} gS0={a} gQ={b} sign={sgn(a)}{sgn(b)}")
    return L


def extracmp_lines(allsets, trips, v0, full0):
    """Task 2.1: s3's 4 extras vs the mixed cells' extra sides."""
    L = []
    g0, gQ_of = _gaps_of(trips, v0, full0)
    s3x = sorted(k for k in M39_EXTRAS if k[0] == 3)
    mixx = sorted(k for k in M39_EXTRAS if k[0] != 3)
    sums = {}
    for tag, sites in (("s3", s3x), ("mixed", mixx)):
        ads, bulks, signs, gaps = [], 0, [], []
        for (Q, r, c) in sites:
            o = off_of(r, c)
            S = allsets[Q]
            adQ = int(abs(int(S["dQ"][o])))
            ostat = "bulk" if S["mask0"][o] else "noncell"
            adO = int(abs(int(S["d0"][o]))) if S["mask0"][o] else None
            a, b = int(gQ_of[Q][o]), int(g0[o])
            ads.append(adQ)
            bulks += int(S["mask0"][o])
            signs.append(sgn(a) + sgn(b))
            gaps.append((a, b))
            L.append(f"extracmp {tag} s{Q}c{c} rc=({r},{c}) adQ={adQ} "
                     f"ostat={ostat} adO={adO if adO is not None else 'n/a'} "
                     f"gQ={a} gO={b} sign={sgn(a)}{sgn(b)}")
        pp = sum(1 for s in signs if s == "++")
        mm = sum(1 for s in signs if s == "--")
        sums[tag] = (ads, bulks, pp, mm)
        L.append(f"extracmp {tag} summary: n={len(sites)} "
                 f"adlist={sorted(ads)} med={_med(ads)} "
                 f"bulk={bulks}/{len(sites)} pp={pp} mm={mm} "
                 f"gaps={gaps}")
    a3, b3, p3, _ = sums["s3"]
    am, bm, pm, _ = sums["mixed"]
    L.append(f"extracmp match: med {_med(a3)} vs {_med(am)} "
             f"gap={abs(float(_med(a3)) - float(_med(am))):.1f} "
             f"(H3 bar <=2.0); bulk {b3}/4 vs {bm}/4; "
             f"pp-share {p3 / 4:.4f} vs {pm / 4:.4f} "
             f"gap={abs(p3 / 4 - pm / 4):.4f} (H5 bar <=0.25)")
    return L


def misscmp_lines(allsets, trips, v0, full0):
    """Task 2.2: s3's 3 missings vs the mixed cells' missing sides."""
    L = []
    g0, gQ_of = _gaps_of(trips, v0, full0)
    s3m = sorted(k for k in M39_MISS if k[0] == 3)
    mixm = sorted(k for k in M39_MISS if k[0] != 3)
    sums = {}
    for tag, sites in (("s3", s3m), ("mixed", mixm)):
        ads, noncells, signs, gaps = [], 0, [], []
        for (Q, r, c) in sites:
            o = off_of(r, c)
            S = allsets[Q]
            ad0v = int(abs(int(S["d0"][o])))
            qstat = "bulk" if S["maskQ"][o] else "noncell"
            a, b = int(g0[o]), int(gQ_of[Q][o])
            ads.append(ad0v)
            noncells += int(not S["maskQ"][o])
            signs.append(sgn(a) + sgn(b))
            gaps.append((a, b))
            L.append(f"misscmp {tag} s{Q}c{c} rc=({r},{c}) adS0={ad0v} "
                     f"qstat={qstat} gS0={a} gQ={b} "
                     f"sign={sgn(a)}{sgn(b)}")
        pp = sum(1 for s in signs if s == "++")
        mm = sum(1 for s in signs if s == "--")
        sums[tag] = (ads, noncells, pp, mm)
        L.append(f"misscmp {tag} summary: n={len(sites)} "
                 f"adlist={sorted(ads)} med={_med(ads)} "
                 f"noncell={noncells}/{len(sites)} pp={pp} mm={mm} "
                 f"gaps={gaps}")
    a3, _, p3, _ = sums["s3"]
    am, _, pm, _ = sums["mixed"]
    L.append(f"misscmp match: med {_med(a3)} vs {_med(am)} "
             f"gap={abs(float(_med(a3)) - float(_med(am))):.1f} "
             f"(H4 bar <=2.0); "
             f"pp-share {p3 / 3:.4f} vs {pm / 3:.4f} "
             f"gap={abs(p3 / 3 - pm / 3):.4f} (H6 bar <=0.34)")
    return L


def deltasplit_lines(allsets):
    """Task 2.3: per-cell |extra delta| vs |missing delta| (10 cells)."""
    L = []
    ex_gt1 = mi_gt1 = 0
    for Q in sorted(BRIEF_CELLS):
        for c in BRIEF_CELLS[Q]:
            cell = allsets[Q]["cells"][c]
            ex = len(set(cell["rQ"]) - set(cell["r0"]))
            mi = len(set(cell["r0"]) - set(cell["rQ"]))
            ex_gt1 += int(ex > 1)
            mi_gt1 += int(mi > 1)
            side = ("extra" if ex > 1 and mi <= 1
                    else ("missing" if mi > 1 and ex <= 1
                          else ("both" if mi > 1 and ex > 1 else "none")))
            L.append(f"deltasplit s{Q}c{c}: extrad={ex} missd={mi} "
                     f"delta={ex + mi} maggt1={side}")
    L.append(f"deltasplit summary: extra-side gt1={ex_gt1} "
             f"missing-side gt1={mi_gt1} (H7 bar 1/0)")
    return L

def main():
    m16d, m15d, m34tsv, m36txt, workd, evidd = (Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin",
              m16d / "m16-v0-s0002.bin", m16d / "m16-mid-s0002.bin",
              m16d / "m16-full-s0002.bin",
              m16d / "m16-v0-s0003.bin", m16d / "m16-mid-s0003.bin",
              m16d / "m16-full-s0003.bin",
              m16d / "m16-v0-s0700.bin", m16d / "m16-mid-s0700.bin",
              m16d / "m16-full-s0700.bin",
              m15d / "m15-v0.bin", m15d / "m15-mid.bin",
              m15d / "m15-full.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    for q in (m34tsv, m36txt):
        qb = q.read_bytes()
        print(f"input {q}: bytes={len(qb)} "
              f"sha256={hashlib.sha256(qb).hexdigest()}")

    print("== loo.txt + top-10 ==")
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
    trips = {Q: load_triplet(m16d, Q) for Q in QLIST}
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M34 baselines: STOP, tabled.")
        return
    if not carriers_ok:
        print("carrier mismatch: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    pl = plane_of_byte()
    pr, pc = plane_coords()

    # ---- s0 cell-7 + tail + guards ----
    print("== s0 guards ==")
    sp0 = interior_sites(v0, mid0, full0, b0)
    mask0, d0, n0 = sp0["mask"], sp0["delta"], sp0["n"]
    print(f"s0 cell7 n={n0} (want {M19_CELL_S0})")
    if n0 != M19_CELL_S0:
        print("s0 COUNT MISMATCH: STOP, tabled.")
        return
    dd0 = d0[mask0]
    print(f"s0 delta==0 count={int((dd0 == 0).sum())} (want 0)")
    print(f"s0 P(d>0)={float((dd0 > 0).mean()):.4f} "
          f"(M19/M20 want {M19_POSRATE_S0})")
    if float(f"{float((dd0 > 0).mean()):.4f}") != M19_POSRATE_S0:
        print("s0 P(d>0) MISMATCH: STOP, tabled.")
        return
    t0, _ = tail_bulk_masks(mask0, d0)
    nt0 = int(t0.sum())
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
    print(f"self Jaccard={jaccard(t0, t0):.4f} (want 1.0000)")

    # ---- full 764 pass ----
    print("== full 764 pass (R_s vs loo + cell/tail + Y colrows) ==")
    t1 = time.time()
    loo_hexes = []
    per = {}
    rs_bad, d0_bad = [], 0
    for s in range(764):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        loo_hexes += [hashlib.sha256(vv).hexdigest(),
                      hashlib.sha256(mm).hexdigest(),
                      hashlib.sha256(ff).hexdigest()]
        bl = synth_w_bytes(vv, ff, 0.5)
        xd = xdiff(bl, mm)[0]
        rs = loo.get(s, ("?", "?"))[1]
        if xd != rs:
            rs_bad.append(s)
            continue
        if s == 0:
            sp, t = sp0, t0
        else:
            sp = interior_sites(vv, mm, ff, bl)
            t, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        dd = sp["delta"][sp["mask"]]
        if int((dd == 0).sum()) != 0:
            d0_bad += 1
            continue
        nt = int(t.sum())
        jj = jaccard(t, t0)
        ycols = tail_y_cols(t, pl, pr, pc)
        per[s] = {"tail": nt, "j": jj, "rs": xd, "ycols": ycols}
    fold = hashlib.sha256("".join(loo_hexes).encode()).hexdigest()
    print(f"triplet fold sha (764x3 bins): {fold}")
    print(f"fold vs M28/M34 want: match={fold == M34_FOLD}")
    print(f"R_s vs loo mismatches: n={len(rs_bad)} {rs_bad[:20]}")
    print(f"delta==0 violations: n={d0_bad} shapes")
    print(f"shapes recorded: n={len(per)} (want 764)")
    print(f"(full-pass wall: {time.time() - t1:.1f}s)")
    if rs_bad or d0_bad or len(per) != 764 or fold != M34_FOLD:
        print("FULL-PASS MISMATCH: STOP, tabled.")
        return

    # ---- UNNAMED domain ----
    print("== UNNAMED domain ==")
    allcols = set()
    for s in range(764):
        allcols.update(per[s]["ycols"])
    UNNAMED = sorted(c for c in allcols if c not in NAMED8)
    s0y = per[0]["ycols"]
    s0u = {c: s0y.get(c, []) for c in UNNAMED}
    n0pos = sorted(c for c in UNNAMED if s0u[c])
    n0zero = sorted(c for c in UNNAMED if not s0u[c])
    print(f"union tail-Y cols (all 764): n={len(allcols)}")
    print(f"UNNAMED (union minus named8): n={len(UNNAMED)} (want 33)")
    print(f"s0-bearing unnamed (n0>0): n={len(n0pos)} (want 13)")
    print(f"pure-private unnamed (n0==0): n={len(n0zero)} (want 20)")

    # ---- FULL unnamed TSV guard (M34 match or stop) ----
    print("== unnamed TSV guard (M34 match or stop) ==")
    tsv_lines = m34tsv.read_text(errors="replace").splitlines()
    want_hdr = "\t".join(["shape", "tail_n", "J_vs_s0"]
                         + [f"{k}{c}" for c in UNNAMED
                            for k in ("n", "ov", "pres")])
    hdr_cols = []
    for tok in tsv_lines[0].split("\t")[3:]:
        if tok.startswith("n"):
            hdr_cols.append(int(tok[1:]))
    print(f"m34-census.tsv rows={len(tsv_lines) - 1} "
          f"hdr_match={tsv_lines[0] == want_hdr} "
          f"universe_match={hdr_cols == UNNAMED}")
    tsv_ok = (tsv_lines[0] == want_hdr and len(tsv_lines) == 765
              and hdr_cols == UNNAMED and len(UNNAMED) == 33
              and len(n0pos) == 13 and len(n0zero) == 20)
    first_bad = None
    for s in range(764):
        rec = per[s]
        cen = census_unnamed_of(rec["ycols"], s0u)
        rec["ucen"] = cen
        rec["umoved"] = sorted(c for c in UNNAMED if cen[c]["pres"] == 0)
        row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in UNNAMED:
            row += [str(cen[c]["n"]), str(cen[c]["ov"]),
                    str(cen[c]["pres"])]
        if "\t".join(row) != tsv_lines[s + 1]:
            tsv_ok = False
            if first_bad is None:
                first_bad = s
    print(f"unnamed TSV full match (764 rows): {tsv_ok}"
          + ("" if tsv_ok else f" first_bad_shape={first_bad}"))
    if first_bad is not None:
        print(f"m34 row: {tsv_lines[first_bad + 1]}")
        rec = per[first_bad]
        row = [str(first_bad), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in UNNAMED:
            row += [str(rec["ucen"][c]["n"]), str(rec["ucen"][c]["ov"]),
                    str(rec["ucen"][c]["pres"])]
        print(f"mine row: {'\t'.join(row)}")
    print("TSV guard: " + ("OK" if tsv_ok else
                           "MISMATCH vs M34: STOP, tabled."))
    if not tsv_ok:
        return

    # ---- 2/3/700 unnamed row guards (k 6/7/8 + standings + deltas) ----
    print("== 2/3/700 unnamed row guards (21 cells or stop) ==")
    row_ok = True
    for Q in QLIST:
        spec = SHAPES[Q]
        rQ = per[Q]
        print(f"s{Q} tail={rQ['tail']} (want {spec['tail']}) "
              f"J={rQ['j']:.4f} (want {spec['jacc']})")
        print(f"s{Q} umoved={rQ['umoved']} (want {spec['moved']})")
        row_ok = (row_ok and rQ["tail"] == spec["tail"]
                  and f"{rQ['j']:.4f}" == spec["jacc"]
                  and rQ["umoved"] == spec["moved"])
        for c in spec["moved"]:
            e = rQ["ucen"][c]
            wn, wov = spec["nov"][c]
            wn0 = spec["n0"][c]
            wm, we, wd, wst = spec["stand"][c]
            stand = ("missing" if e["miss"] > 0 and e["extra"] == 0
                     else ("extra" if e["miss"] == 0 and e["extra"] > 0
                           else "mixed"))
            good = (e["n"] == wn and e["ov"] == wov and len(s0u[c]) == wn0
                    and e["miss"] == wm and e["extra"] == we
                    and e["delta"] == wd and stand == wst
                    and e["pres"] == 0)
            row_ok = row_ok and good
            print(f"s{Q} c{c}: n/ov={e['n']}/{e['ov']} (want {wn}/{wov}) "
                  f"n0={len(s0u[c])} (want {wn0}) miss/extra/delta="
                  f"{e['miss']}/{e['extra']}/{e['delta']} "
                  f"(want {wm}/{we}/{wd}) stand={stand} (want {wst}) "
                  f"match={good}")
    print("2/3/700 row guards: " + ("OK" if row_ok else
                                    "MISMATCH vs M34: STOP, tabled."))
    if not row_ok:
        return

    # ---- s0+Q sets + pooled-count guards ----
    print("== s0+Q sets + pooled-count guards ==")
    allsets = {}
    pool_ok = True
    for Q in QLIST:
        vQ, midQ, fullQ, bQ = trips[Q]
        sets = compute_sets_for(v0, mid0, full0, b0, vQ, midQ, fullQ, bQ,
                                SHAPES[Q]["moved"])
        allsets[Q] = sets
        maskQ, dQ = sets["maskQ"], sets["dQ"]
        ddQ = dQ[maskQ]
        print(f"s{Q} cell7 n={sets['spQ']['n']} "
              f"(M36-measured want {M36_CELL[Q]}) "
              f"delta==0 count={int((ddQ == 0).sum())} (want 0)")
        pool_ok = pool_ok and int((ddQ == 0).sum()) == 0
        pool_ok = pool_ok and sets["spQ"]["n"] == M36_CELL[Q]
        ex_n = sum(int(sets["cells"][c]["ex"].sum())
                   for c in SHAPES[Q]["moved"])
        mi_n = sum(int(sets["cells"][c]["mi"].sum())
                   for c in SHAPES[Q]["moved"])
        wex, wmi = SHAPES[Q]["pool"]
        print(f"s{Q} pooled unnamed extras={ex_n} (want {wex}) "
              f"missings={mi_n} (want {wmi})")
        pool_ok = pool_ok and ex_n == wex and mi_n == wmi
    ex_planes = {int(pl[o]) for Q in QLIST for c in SHAPES[Q]["moved"]
                 for o in np.nonzero(allsets[Q]["cells"][c]["ex"])[0]}
    mi_planes = {int(pl[o]) for Q in QLIST for c in SHAPES[Q]["moved"]
                 for o in np.nonzero(allsets[Q]["cells"][c]["mi"])[0]}
    print(f"pooled extras planes={sorted(ex_planes)} "
          f"missings planes={sorted(mi_planes)} (want [0]=all-Y both)")
    pool_ok = pool_ok and ex_planes == {0} and mi_planes == {0}
    print("pooled-count guards: "
          + ("OK" if pool_ok else "MISMATCH: STOP, tabled."))
    if not pool_ok:
        for Q in QLIST:
            ex_rc = sorted((int(pr[o]), int(pc[o]))
                           for c in SHAPES[Q]["moved"]
                           for o in np.nonzero(allsets[Q]["cells"][c]["ex"])[0])
            mi_rc = sorted((int(pr[o]), int(pc[o]))
                           for c in SHAPES[Q]["moved"]
                           for o in np.nonzero(allsets[Q]["cells"][c]["mi"])[0])
            print(f"s{Q} extras rc={ex_rc}")
            print(f"s{Q} missings rc={mi_rc}")
        return

    # ---- M36 missing + extra value pins (pooled universe guard) ----
    print("== M36 value pins (10 miss + 24 extra or stop) ==")
    g0 = (np.frombuffer(v0, np.uint8).astype(np.int16)
          - np.frombuffer(full0, np.uint8).astype(np.int16))
    pin_ok = True
    for Q in QLIST:
        vQ, _, fullQ, _ = trips[Q]
        gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
              - np.frombuffer(fullQ, np.uint8).astype(np.int16))
        d0 = allsets[Q]["d0"]
        dQ = allsets[Q]["dQ"]
        m0 = allsets[Q]["mask0"]
        mQ = allsets[Q]["maskQ"]
        for (pQ, r, c), (wo, wad, wstat, wg0, wgQ) in sorted(M36_MISS.items()):
            if pQ != Q:
                continue
            o = off_of(r, c)
            in_mi = bool(allsets[Q]["cells"][c]["mi"][o])
            ad0v = int(abs(int(d0[o])))
            qstat = "bulk" if mQ[o] else "noncell"
            good = (in_mi and o == wo and ad0v == wad and qstat == wstat
                    and int(g0[o]) == wg0 and int(gQ[o]) == wgQ)
            pin_ok = pin_ok and good
            print(f"pinmiss s{Q}c{c} r={r} o={o} (want {wo}) "
                  f"ad0={ad0v} (want {wad}) qstat={qstat} "
                  f"(want {wstat}) g0={int(g0[o])} (want {wg0}) "
                  f"gQ={int(gQ[o])} (want {wgQ}) inmi={in_mi} "
                  f"match={good}")
        for (pQ, r, c), (wo, wad, wstat, wado, wgQ, wgO) in sorted(
                M36_EXTRAS.items()):
            if pQ != Q:
                continue
            o = off_of(r, c)
            in_ex = bool(allsets[Q]["cells"][c]["ex"][o])
            adqv = int(abs(int(dQ[o])))
            ostat = "bulk" if m0[o] else "noncell"
            ado = int(abs(int(d0[o]))) if m0[o] else None
            good = (in_ex and o == wo and adqv == wad and ostat == wstat
                    and ado == wado and int(gQ[o]) == wgQ
                    and int(g0[o]) == wgO)
            pin_ok = pin_ok and good
            print(f"pinextra s{Q}c{c} r={r} o={o} (want {wo}) "
                  f"adQ={adqv} (want {wad}) ostat={ostat} "
                  f"(want {wstat}) adO={ado} (want {wado}) "
                  f"gQ={int(gQ[o])} (want {wgQ}) "
                  f"gO={int(g0[o])} (want {wgO}) inex={in_ex} "
                  f"match={good}")
    # set-level: recomputed miss/extra rows per (Q,cell) == pin rows exactly
    for Q in QLIST:
        for c in SHAPES[Q]["moved"]:
            gotm = sorted(int(pr[o]) for o in
                         np.nonzero(allsets[Q]["cells"][c]["mi"])[0])
            wantm = sorted(r for (pQ, r, cc) in M36_MISS if pQ == Q
                           and cc == c)
            good = gotm == wantm
            pin_ok = pin_ok and good
            print(f"pinset s{Q}c{c}: miss rows={gotm} (want {wantm}) "
                  f"match={good}")
            gote = sorted(int(pr[o]) for o in
                         np.nonzero(allsets[Q]["cells"][c]["ex"])[0])
            wante = sorted(r for (pQ, r, cc) in M36_EXTRAS if pQ == Q
                           and cc == c)
            good = gote == wante
            pin_ok = pin_ok and good
            print(f"pinset s{Q}c{c}: extra rows={gote} (want {wante}) "
                  f"match={good}")
    print("value pins: " + ("OK" if pin_ok else
                            "MISMATCH vs M36: STOP, tabled."))
    if not pin_ok:
        return

    # ---- M39 row-list pins (10 brief cells or stop) ----
    print("== M39 row-list pins (10 brief cells or stop) ==")
    prow_ok = True
    for Q in sorted(BRIEF_CELLS):
        for c in BRIEF_CELLS[Q]:
            cell = allsets[Q]["cells"][c]
            ex = sorted(set(cell["rQ"]) - set(cell["r0"]))
            mi = sorted(set(cell["r0"]) - set(cell["rQ"]))
            wex = EXTRAROWS.get((Q, c), [])
            wmi = MISSROWS.get((Q, c), [])
            if c == 316:
                s0good = len(cell["r0"]) == 1
                qgood = sorted(cell["rQ"]) == sorted(cell["r0"] + [265])
            else:
                s0good = cell["r0"] == S0ROWS[c]
                wantQ = sorted((set(S0ROWS[c]) | set(wex)) - set(wmi))
                qgood = cell["rQ"] == wantQ
            good = bool(s0good and qgood and ex == wex and mi == wmi)
            prow_ok = prow_ok and good
            print(f"pinrow s{Q}c{c}: s0rows={cell['r0']} "
                  f"Qrows={cell['rQ']} extra={ex} (want {wex}) "
                  f"miss={mi} (want {wmi}) match={good}")
    print("row-list pins: " + ("OK" if prow_ok else
                               "MISMATCH vs M36: STOP, tabled."))
    if not prow_ok:
        return

    # ---- Task 1: s3 row + mixed cells recompute (canon for determinism) ----
    print("== Task 1: s3 row + mixed cells recompute ==")
    t1 = time.time()
    canon = task1_canon_lines(allsets, trips, v0, full0)
    for ln in canon:
        print(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.1: extra-side comparison ----
    print("== Task 2.1: extra-side comparison ==")
    for ln in extracmp_lines(allsets, trips, v0, full0):
        print(ln)

    # ---- Task 2.2: missing-side comparison ----
    print("== Task 2.2: missing-side comparison ==")
    for ln in misscmp_lines(allsets, trips, v0, full0):
        print(ln)

    # ---- Task 2.3: delta split ----
    print("== Task 2.3: delta split ==")
    for ln in deltasplit_lines(allsets):
        print(ln)

    # ---- determinism re-run (Task 1 on s0+2/3/700, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+2/3/700, second pass) ==")
    v0b, mid0b, full0b, b0b = load_triplet(m16d, 0)
    trips2 = {Q: load_triplet(m16d, Q) for Q in QLIST}
    allsets2 = {}
    for Q in QLIST:
        vQb, midQb, fullQb, bQb = trips2[Q]
        allsets2[Q] = compute_sets_for(v0b, mid0b, full0b, b0b, vQb,
                                       midQb, fullQb, bQb,
                                       SHAPES[Q]["moved"])
    canon2 = task1_canon_lines(allsets2, trips2, v0b, full0b)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")
    for Q in sorted(BRIEF_CELLS):
        ex1 = sum(int(allsets[Q]["cells"][c]["ex"].sum())
                  for c in BRIEF_CELLS[Q])
        ex2 = sum(int(allsets2[Q]["cells"][c]["ex"].sum())
                  for c in BRIEF_CELLS[Q])
        mi1 = sum(int(allsets[Q]["cells"][c]["mi"].sum())
                  for c in BRIEF_CELLS[Q])
        mi2 = sum(int(allsets2[Q]["cells"][c]["mi"].sum())
                  for c in BRIEF_CELLS[Q])
        print(f"sets identical s{Q} brief cells: extras {ex1}/{ex2} "
              f"missings {mi1}/{mi2}")

    # ---- PNG uniformity map (work dir; evidence copy iff rule meets) ----
    print("== PNG uniformity map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    over = 0.35 * rgbm.astype(np.float32)
    for (Q, r, c) in sorted(M39_EXTRAS):
        col = (np.array([0, 255, 0]) if Q == 3
               else np.array([255, 0, 0]))  # s3 extras green / mixed red
        over[r, c] = col
    for (Q, r, c) in sorted(M39_MISS):
        col = (np.array([255, 255, 0]) if Q == 3
               else np.array([255, 0, 255]))  # s3 miss yellow / mixed magenta
        over[r, c] = col
    p = workd / "m39-uniformmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: green=s3-extras red=mixed-extras yellow=s3-missings "
          "magenta=mixed-missings (s0 geometry; Y only)")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    g0b, gQb_of = _gaps_of(trips, v0, full0)
    # H1: 10/10 brief row-lists match pins
    h1_n = 0
    for Q in sorted(BRIEF_CELLS):
        for c in BRIEF_CELLS[Q]:
            cell = allsets[Q]["cells"][c]
            ex = sorted(set(cell["rQ"]) - set(cell["r0"]))
            mi = sorted(set(cell["r0"]) - set(cell["rQ"]))
            wex = EXTRAROWS.get((Q, c), [])
            wmi = MISSROWS.get((Q, c), [])
            if c == 316:
                ok = (len(cell["r0"]) == 1
                      and sorted(cell["rQ"]) == sorted(cell["r0"] + [265])
                      and ex == wex and mi == wmi)
            else:
                wantQ = sorted((set(S0ROWS[c]) | set(wex)) - set(wmi))
                ok = (cell["r0"] == S0ROWS[c] and cell["rQ"] == wantQ
                      and ex == wex and mi == wmi)
            h1_n += int(ok)
    h1 = h1_n == 10
    print(f"H1_ROW_REPRO: match={h1_n}/10 (bar 10/10; met={h1})")
    # H2: 14/14 brief value pins match
    h2_n = 0
    for (Q, r, c), (wo, wad, wstat, wado, wgQ, wgO) in sorted(
            M39_EXTRAS.items()):
        o = off_of(r, c)
        S = allsets[Q]
        ostat = "bulk" if S["mask0"][o] else "noncell"
        ado = int(abs(int(S["d0"][o]))) if S["mask0"][o] else None
        ok = (o == wo and int(abs(int(S["dQ"][o]))) == wad
              and ostat == wstat and ado == wado
              and int(gQb_of[Q][o]) == wgQ and int(g0b[o]) == wgO)
        h2_n += int(ok)
    for (Q, r, c), (wo, wad, wstat, wg0, wgQ) in sorted(M39_MISS.items()):
        o = off_of(r, c)
        S = allsets[Q]
        qstat = "bulk" if S["maskQ"][o] else "noncell"
        ok = (o == wo and int(abs(int(S["d0"][o]))) == wad
              and qstat == wstat and int(g0b[o]) == wg0
              and int(gQb_of[Q][o]) == wgQ)
        h2_n += int(ok)
    h2 = h2_n == 14
    print(f"H2_VALUE_REPRO: match={h2_n}/14 (bar 14/14; met={h2})")
    # H3/H5: extra-side medians + ++ shares, s3 vs mixed
    def exvals(sites):
        ads, pps = [], 0
        for (Q, r, c) in sites:
            o = off_of(r, c)
            S = allsets[Q]
            ads.append(int(abs(int(S["dQ"][o]))))
            pps += int(int(gQb_of[Q][o]) > 0 and int(g0b[o]) > 0)
        return ads, pps
    s3x = sorted(k for k in M39_EXTRAS if k[0] == 3)
    mixx = sorted(k for k in M39_EXTRAS if k[0] != 3)
    a3x, p3x = exvals(s3x)
    amx, pmx = exvals(mixx)
    h3_gap = abs(float(_med(a3x)) - float(_med(amx)))
    h3 = h3_gap <= 2.0
    print(f"H3_EXTRA_AD_DEEP: med {_med(a3x)} vs {_med(amx)} "
          f"gap={h3_gap:.1f} (bar <=2.0; met={h3})")
    h5_gap = abs(p3x / 4 - pmx / 4)
    h5 = h5_gap <= 0.25
    print(f"H5_EXTRA_SIGN_DEEP: pp {p3x}/4 vs {pmx}/4 "
          f"gap={h5_gap:.4f} (bar <=0.25; met={h5})")
    # H4/H6: missing-side medians + ++ shares, s3 vs mixed
    def mivals(sites):
        ads, pps = [], 0
        for (Q, r, c) in sites:
            o = off_of(r, c)
            ads.append(int(abs(int(allsets[Q]["d0"][o]))))
            pps += int(int(g0b[o]) > 0 and int(gQb_of[Q][o]) > 0)
        return ads, pps
    s3m = sorted(k for k in M39_MISS if k[0] == 3)
    mixm = sorted(k for k in M39_MISS if k[0] != 3)
    a3m, p3m = mivals(s3m)
    amm, pmm = mivals(mixm)
    h4_gap = abs(float(_med(a3m)) - float(_med(amm)))
    h4 = h4_gap <= 2.0
    print(f"H4_MISS_AD_DEEP: med {_med(a3m)} vs {_med(amm)} "
          f"gap={h4_gap:.1f} (bar <=2.0; met={h4})")
    h6_gap = abs(p3m / 3 - pmm / 3)
    h6 = h6_gap <= 0.34
    print(f"H6_MISS_SIGN_DEEP: pp {p3m}/3 vs {pmm}/3 "
          f"gap={h6_gap:.4f} (bar <=0.34; met={h6})")
    # H7: per-side deltas >1 across the 10 cells
    ex_gt1 = mi_gt1 = 0
    for Q in sorted(BRIEF_CELLS):
        for c in BRIEF_CELLS[Q]:
            cell = allsets[Q]["cells"][c]
            ex_gt1 += int(len(set(cell["rQ"]) - set(cell["r0"])) > 1)
            mi_gt1 += int(len(set(cell["r0"]) - set(cell["rQ"])) > 1)
    h7 = ex_gt1 == 1 and mi_gt1 == 0
    print(f"H7_DELTA_SIDE: extra-gt1={ex_gt1} missing-gt1={mi_gt1} "
          f"(bar 1/0; met={h7})")
    print(f"PNG rule: H1={h1} H2={h2} H3={h3} H4={h4} "
          f"(copy iff H1 and H2 and exactly one of H3/H4: "
          f"{bool(h1 and h2 and (h3 != h4))})")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=row+standing+values T2=extra+missing+delta R=controls")


if __name__ == "__main__":
    main()
