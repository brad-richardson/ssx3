#!/usr/bin/env python3
"""M41 near-miss triple: boundary-|d| census at unnamed cells (offline).

Usage: m41.py M16_DIR M15_DIR M34TSV M35TXT M36TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), m34-census.tsv (FULL TSV guard), m35.txt (the 3
near-miss sites to reproduce) and m36.txt (still-below near
counts to reproduce); raw XFB dumps, 573440 B = 640x448 YUYV.
Read-only inputs; receipt text goes to stdout (redirect to
WORK_DIR/m41.txt); PNG near-miss map to WORK_DIR (evidence copy
iff the DESIGN.md rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: near-miss triple recompute (per-site + near-def + rowlists)
  2: boundary-|d| census (s9 + still-below + cross-row)
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
M19_CELL_S0 = 2475  # s9 cell count: M35-measured, guarded equal
M20_TAIL_S0 = 102
M20_TAIL_S0_SUB = (28, 74)  # (8-15, 16+)
M20_TAIL_S0_MAX = 47
M19_POSRATE_S0 = 0.8093  # P(d>0) on s0 cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
NAMED8 = [257, 277, 296, 301, 321, 340, 342, 343]
# Per-shape pins from the M34 TSV rows (shape 9, read before running).
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
          "stand": {38: (1, 0, 1, "missing"),
                    54: (0, 10, 10, "extra"),
                    299: (0, 1, 1, "extra"), 311: (0, 1, 1, "extra"),
                    313: (0, 1, 1, "extra"),
                    314: (1, 0, 1, "missing"),
                    332: (1, 1, 2, "mixed"), 620: (0, 1, 1, "extra")},
          "pool": (15, 3)},
    9: {"tail": 117, "jacc": "0.7520",
        "moved": [310, 311, 312, 313, 314, 315, 316, 318, 322, 327,
                  332, 336, 337, 339, 351],
        "nov": {310: (1, 0), 311: (3, 3), 312: (2, 1), 313: (6, 4),
                314: (5, 4), 315: (8, 5), 316: (3, 1), 318: (3, 0),
                322: (1, 0), 327: (2, 0), 332: (3, 2), 336: (1, 0),
                337: (2, 0), 339: (1, 0), 351: (1, 0)},
        "n0": {310: 0, 311: 4, 312: 3, 313: 4, 314: 7, 315: 7,
               316: 1, 318: 0, 322: 0, 327: 0, 332: 2, 336: 0,
               337: 0, 339: 0, 351: 0},
        "stand": {310: (0, 1, 1, "extra"), 311: (1, 0, 1, "missing"),
                  312: (2, 1, 3, "mixed"), 313: (0, 2, 2, "extra"),
                  314: (3, 1, 4, "mixed"), 315: (2, 3, 5, "mixed"),
                  316: (0, 2, 2, "extra"), 318: (0, 3, 3, "extra"),
                  322: (0, 1, 1, "extra"), 327: (0, 2, 2, "extra"),
                  332: (0, 1, 1, "extra"), 336: (0, 1, 1, "extra"),
                  337: (0, 2, 2, "extra"), 339: (0, 1, 1, "extra"),
                  351: (0, 1, 1, "extra")},
        "pool": (22, 8)},  # (extras, missings)
}
QLIST = [2, 3, 9, 700]
# M35/M36-measured s0+Q cell-7 counts (M35/M36 REPORT baseline notes).
M41_CELL = {2: 2469, 3: 2484, 9: 2670, 700: 2605}
# Brief universe: the near-miss triple (M35 gap 2): 1 extra-side
# near (9,239,336) + 2 missing-side nears (9,299,312)+(9,301,312).
TRIPLE_EXTRA = (9, 239, 336)
TRIPLE_MISS = [(9, 299, 312), (9, 301, 312)]
# Row-list pins (M35/M40): (Q, c) -> (s0rows, Qrows, extrarows, missrows).
ROWPINS = {(9, 336): ([], [239], [239], []),
           (9, 312): ([299, 300, 301], [248, 300], [248], [299, 301])}
# M35 full missing pins: (Q, r, c) -> (offset, |d_s0|, qstat,
# adQ|None, g_s0, g_Q).
M35_MISS = {
    (9, 296, 311): (379502, 10, "noncell", None, 24, 7),
    (9, 299, 312): (383344, 10, "bulk", 6, 22, 16),
    (9, 301, 312): (385904, 9, "bulk", 7, 28, 28),
    (9, 269, 314): (344948, 12, "noncell", None, 41, 29),
    (9, 288, 314): (369268, 45, "noncell", None, 107, 84),
    (9, 289, 314): (370548, 23, "noncell", None, 54, 31),
    (9, 266, 315): (341110, 10, "bulk", 2, 64, 46),
    (9, 273, 315): (350070, 10, "bulk", 3, 23, 23),
}
# M35 22-site extra pins: (Q, r, c) -> (offset, adQ, ostat, adO|None, gQ, gO).
M35_EXTRAS = {
    (9, 252, 310): (323180, 8, "noncell", None, 22, 2),
    (9, 248, 312): (318064, 13, "bulk", 1, 33, 10),
    (9, 269, 313): (344946, 12, "bulk", 1, 39, 7),
    (9, 270, 313): (346226, 9, "bulk", 1, 28, 6),
    (9, 246, 314): (315508, 13, "bulk", 1, 32, 9),
    (9, 245, 315): (314230, 13, "bulk", 2, 60, 6),
    (9, 289, 315): (370550, 16, "noncell", None, -34, 0),
    (9, 290, 315): (371830, 11, "noncell", None, -26, -2),
    (9, 244, 316): (312952, 14, "bulk", 1, 59, 7),
    (9, 245, 316): (314232, 8, "bulk", 1, 56, 8),
    (9, 240, 318): (307836, 16, "bulk", 1, 34, 5),
    (9, 241, 318): (309116, 25, "bulk", 2, 93, 11),
    (9, 243, 318): (311676, 13, "bulk", 1, 53, 11),
    (9, 274, 322): (351364, 8, "noncell", None, 21, 2),
    (9, 232, 327): (297614, 12, "bulk", 2, 25, 5),
    (9, 233, 327): (298894, 14, "bulk", 1, 29, 4),
    (9, 305, 332): (391064, 28, "noncell", None, -62, -55),
    (9, 239, 336): (306592, 8, "bulk", 6, 17, 14),
    (9, 234, 337): (300194, 10, "bulk", 1, 21, 4),
    (9, 235, 337): (301474, 8, "bulk", 1, 17, 4),
    (9, 239, 339): (306598, 15, "noncell", None, 39, 35),
    (9, 226, 351): (289982, 19, "noncell", None, -39, -39),
}
# M36 full missing pins: (Q, r, c) -> (offset, |d_s0|, qstat,
# adQ|None, g_s0, g_Q).
M36_MISS = {
    (2, 299, 312): (383344, 10, "noncell", None, 22, 22),
    (2, 276, 313): (353906, 8, "noncell", None, 17, 16),
    (2, 278, 314): (356468, 20, "noncell", None, 42, 40),
    (2, 295, 332): (378264, 10, "noncell", None, -22, -21),
    (3, 276, 313): (353906, 8, "noncell", None, 17, 16),
    (3, 278, 314): (356468, 20, "noncell", None, 42, 42),
    (3, 295, 332): (378264, 10, "noncell", None, -22, -21),
    (700, 215, 38): (275276, 12, "noncell", None, 25, 23),
    (700, 278, 314): (356468, 20, "noncell", None, 42, 42),
    (700, 295, 332): (378264, 10, "noncell", None, -22, -21),
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
# Pooled 64-site pins: 30 s9 (M35) + 34 still-below (M36).
ALLEXTRA = dict(M35_EXTRAS)
ALLEXTRA.update(M36_EXTRAS)
ALLMISS = dict(M35_MISS)
ALLMISS.update(M36_MISS)
# M36 near/far/noncell splits (extra-side + missing-side per shape).
M36_SPLITS = {2: {"ex": (1, 0, 4), "mi": (0, 0, 4)},
              3: {"ex": (2, 0, 2), "mi": (0, 0, 3)},
              700: {"ex": (11, 0, 4), "mi": (0, 0, 3)}}
M35_SPLITS = {9: {"ex": (1, 14, 7), "mi": (2, 2, 4)}}


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


def _raw_abs(midb: bytes, synthb: bytes) -> np.ndarray:
    """Raw per-byte |mid - blend| (any status; for the raw-8 scan)."""
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    s = np.frombuffer(synthb, np.uint8).astype(np.int16)
    return np.abs(m - s)


def other_census(allsets, trips, v0, mid0, full0, b0, Q):
    """Other-frame census for shape Q's pooled sites (bulk hists + splits).

    Extras evaluated on s0; missings on Q. Returns per-side dicts with
    near/far/non (r,c) lists, |d| hist over bulk, boundary-5 count,
    and raw-|d|==8 scan hits (any status).
    """
    S = allsets[Q]
    _, midQ, _, bQ = trips[Q]
    raw0 = _raw_abs(mid0, b0)
    rawQ = _raw_abs(midQ, bQ)
    out = {}
    exn, exf, exx, exh, exr8 = [], [], [], {}, []
    for (QQ, r, c) in sorted(k for k in ALLEXTRA if k[0] == Q):
        o = off_of(r, c)
        if S["mask0"][o]:
            ad = int(abs(int(S["d0"][o])))
            exh[ad] = exh.get(ad, 0) + 1
            (exn if ad in (6, 7) else exf).append((r, c))
        else:
            exx.append((r, c))
        if int(raw0[o]) == 8:
            exr8.append((r, c))
    out["ex"] = {"near": exn, "far": exf, "non": exx, "hist": exh,
                 "b5": exh.get(5, 0), "raw8": exr8}
    min_, mif, mix, mih, mir8 = [], [], [], {}, []
    for (QQ, r, c) in sorted(k for k in ALLMISS if k[0] == Q):
        o = off_of(r, c)
        if S["maskQ"][o]:
            ad = int(abs(int(S["dQ"][o])))
            mih[ad] = mih.get(ad, 0) + 1
            (min_ if ad in (6, 7) else mif).append((r, c))
        else:
            mix.append((r, c))
        if int(rawQ[o]) == 8:
            mir8.append((r, c))
    out["mi"] = {"near": min_, "far": mif, "non": mix, "hist": mih,
                 "b5": mih.get(5, 0), "raw8": mir8}
    return out


def triple_canon_lines(allsets, trips, v0, full0):
    """Task 1 core: 3-site rows + near-def + row-list context (s9 only).

    Determinism canon: depends only on s0+9 triplets.
    """
    L = []
    g0, gQ_of = _gaps_of(trips, v0, full0)
    Q = 9
    S = allsets[Q]
    # 1. per-site rows (1 extra + 2 missings)
    (QE, rE, cE) = TRIPLE_EXTRA
    o = off_of(rE, cE)
    adQ = int(abs(int(S["dQ"][o])))
    ostat = "bulk" if S["mask0"][o] else "noncell"
    adO = int(abs(int(S["d0"][o]))) if S["mask0"][o] else None
    a, b = int(gQ_of[Q][o]), int(g0[o])
    L.append(f"triple extra s{Q}c{cE} rc=({rE},{cE}) o={o} adQ={adQ} "
             f"ostat={ostat} adO={adO if adO is not None else 'n/a'} "
             f"gQ={a} gO={b} sign={sgn(a)}{sgn(b)} gapequal={a == b}")
    for (QM, rM, cM) in TRIPLE_MISS:
        o = off_of(rM, cM)
        ad0v = int(abs(int(S["d0"][o])))
        qstat = "bulk" if S["maskQ"][o] else "noncell"
        adQ = int(abs(int(S["dQ"][o]))) if S["maskQ"][o] else None
        a, b = int(g0[o]), int(gQ_of[Q][o])
        L.append(f"triple miss s{Q}c{cM} rc=({rM},{cM}) o={o} adS0={ad0v} "
                 f"qstat={qstat} adQ={adQ if adQ is not None else 'n/a'} "
                 f"gS0={a} gQ={b} sign={sgn(a)}{sgn(b)} gapequal={a == b}")
    # 2. near-definition lines
    o = off_of(rE, cE)
    adO = int(abs(int(S["d0"][o]))) if S["mask0"][o] else None
    L.append(f"neardef extra s{Q}c{cE} rc=({rE},{cE}) other_ad="
             f"{adO if adO is not None else 'n/a'} "
             f"inband={adO in (6, 7) if adO is not None else False}")
    for (QM, rM, cM) in TRIPLE_MISS:
        o = off_of(rM, cM)
        adQ = int(abs(int(S["dQ"][o]))) if S["maskQ"][o] else None
        L.append(f"neardef miss s{Q}c{cM} rc=({rM},{cM}) other_ad="
                 f"{adQ if adQ is not None else 'n/a'} "
                 f"inband={adQ in (6, 7) if adQ is not None else False}")
    # 3. row-list context (c336 + c312)
    for (QR, cR) in sorted(ROWPINS):
        cell = allsets[QR]["cells"][cR]
        ex = sorted(set(cell["rQ"]) - set(cell["r0"]))
        mi = sorted(set(cell["r0"]) - set(cell["rQ"]))
        L.append(f"rowctx s{QR}c{cR}: s0rows={cell['r0']} "
                 f"Qrows={cell['rQ']} extra={ex} miss={mi}")
    # edge flags: extra vs s9 rows; missings vs s0 rows
    cell = allsets[Q]["cells"][cE]
    edge = (len(cell["rQ"]) == 1 or rE == min(cell["rQ"])
            or rE == max(cell["rQ"]))
    L.append(f"rowedge extra s{Q}c{cE} rc=({rE},{cE}): "
             f"ownrows={cell['rQ']} edge={edge} "
             f"singleton={len(cell['rQ']) == 1}")
    for (QM, rM, cM) in TRIPLE_MISS:
        cell = allsets[Q]["cells"][cM]
        edge = (len(cell["r0"]) == 1 or rM == min(cell["r0"])
                or rM == max(cell["r0"]))
        L.append(f"rowedge miss s{Q}c{cM} rc=({rM},{cM}): "
                 f"ownrows={cell['r0']} edge={edge} "
                 f"singleton={len(cell['r0']) == 1}")
    return L


def s9census_lines(allsets, trips, v0, mid0, full0, b0):
    """Task 2.1: s9 boundary census over all 30 pooled sites."""
    L = []
    Q = 9
    S = allsets[Q]
    cen = other_census(allsets, trips, v0, mid0, full0, b0, Q)
    for (QQ, r, c) in sorted(k for k in ALLEXTRA if k[0] == Q):
        o = off_of(r, c)
        if S["mask0"][o]:
            ad = int(abs(int(S["d0"][o])))
            st = "near" if ad in (6, 7) else "far"
            L.append(f"s9census extra c{c} rc=({r},{c}) adO={ad} {st}")
        else:
            L.append(f"s9census extra c{c} rc=({r},{c}) adO=n/a noncell")
    for (QQ, r, c) in sorted(k for k in ALLMISS if k[0] == Q):
        o = off_of(r, c)
        if S["maskQ"][o]:
            ad = int(abs(int(S["dQ"][o])))
            st = "near" if ad in (6, 7) else "far"
            L.append(f"s9census miss c{c} rc=({r},{c}) adQ={ad} {st}")
        else:
            L.append(f"s9census miss c{c} rc=({r},{c}) adQ=n/a noncell")
    ex, mi = cen["ex"], cen["mi"]
    L.append(f"s9census extra hist: {sorted(ex['hist'].items())} "
             f"noncell={len(ex['non'])} b5={ex['b5']} raw8={ex['raw8']}")
    L.append(f"s9census miss hist: {sorted(mi['hist'].items())} "
             f"noncell={len(mi['non'])} b5={mi['b5']} raw8={mi['raw8']}")
    L.append(f"s9census extra split: near/far/non={len(ex['near'])}/"
             f"{len(ex['far'])}/{len(ex['non'])} (want 1/14/7) "
             f"near_rc={ex['near']}")
    L.append(f"s9census miss split: near/far/non={len(mi['near'])}/"
             f"{len(mi['far'])}/{len(mi['non'])} (want 2/2/4) "
             f"near_rc={mi['near']}")
    L.append(f"s9census pooled near: {len(ex['near']) + len(mi['near'])}/30 "
             f"(want 3/30)")
    return L


def stillcensus_lines(allsets, trips, v0, mid0, full0, b0):
    """Task 2.2: still-below recount over 24 extras + 10 missings."""
    L = []
    pooled_ex = {"near": [], "far": [], "non": [], "hist": {},
                 "b5": 0, "raw8": []}
    pooled_mi = {"near": [], "far": [], "non": [], "hist": {},
                 "b5": 0, "raw8": []}
    for Q in (2, 3, 700):
        S = allsets[Q]
        cen = other_census(allsets, trips, v0, mid0, full0, b0, Q)
        for (QQ, r, c) in sorted(k for k in ALLEXTRA if k[0] == Q):
            o = off_of(r, c)
            if S["mask0"][o]:
                ad = int(abs(int(S["d0"][o])))
                st = "near" if ad in (6, 7) else "far"
                L.append(f"stillcensus extra s{Q}c{c} rc=({r},{c}) "
                         f"adO={ad} {st}")
            else:
                L.append(f"stillcensus extra s{Q}c{c} rc=({r},{c}) "
                         f"adO=n/a noncell")
        for (QQ, r, c) in sorted(k for k in ALLMISS if k[0] == Q):
            o = off_of(r, c)
            if S["maskQ"][o]:
                ad = int(abs(int(S["dQ"][o])))
                st = "near" if ad in (6, 7) else "far"
                L.append(f"stillcensus miss s{Q}c{c} rc=({r},{c}) "
                         f"adQ={ad} {st}")
            else:
                L.append(f"stillcensus miss s{Q}c{c} rc=({r},{c}) "
                         f"adQ=n/a noncell")
        ex, mi = cen["ex"], cen["mi"]
        wex, wmi = M36_SPLITS[Q]["ex"], M36_SPLITS[Q]["mi"]
        L.append(f"stillcensus s{Q} extra hist: "
                 f"{sorted(ex['hist'].items())} noncell={len(ex['non'])} "
                 f"b5={ex['b5']} raw8={ex['raw8']}")
        L.append(f"stillcensus s{Q} miss hist: "
                 f"{sorted(mi['hist'].items())} noncell={len(mi['non'])} "
                 f"b5={mi['b5']} raw8={mi['raw8']}")
        L.append(f"stillcensus s{Q} extra split: near/far/non="
                 f"{len(ex['near'])}/{len(ex['far'])}/{len(ex['non'])} "
                 f"(want {wex[0]}/{wex[1]}/{wex[2]}) near_rc={ex['near']}")
        L.append(f"stillcensus s{Q} miss split: near/far/non="
                 f"{len(mi['near'])}/{len(mi['far'])}/{len(mi['non'])} "
                 f"(want {wmi[0]}/{wmi[1]}/{wmi[2]})")
        for dst, src in ((pooled_ex, ex), (pooled_mi, mi)):
            for k in ("near", "far", "non", "raw8"):
                dst[k] += src[k]
            for ad, n in src["hist"].items():
                dst["hist"][ad] = dst["hist"].get(ad, 0) + n
            dst["b5"] += src["b5"]
    L.append(f"stillcensus pooled extra hist: "
             f"{sorted(pooled_ex['hist'].items())} "
             f"noncell={len(pooled_ex['non'])} b5={pooled_ex['b5']} "
             f"raw8={pooled_ex['raw8']}")
    L.append(f"stillcensus pooled miss hist: "
             f"{sorted(pooled_mi['hist'].items())} "
             f"noncell={len(pooled_mi['non'])} b5={pooled_mi['b5']} "
             f"raw8={pooled_mi['raw8']}")
    L.append(f"stillcensus pooled extra split: near/far/non="
             f"{len(pooled_ex['near'])}/{len(pooled_ex['far'])}/"
             f"{len(pooled_ex['non'])} (want 14/0/10)")
    L.append(f"stillcensus pooled miss split: near/far/non="
             f"{len(pooled_mi['near'])}/{len(pooled_mi['far'])}/"
             f"{len(pooled_mi['non'])} (want 0/0/10)")
    return L


def crossrow_lines(allsets, trips, v0, mid0, full0, b0):
    """Task 2.3: cross-row near table (s9 vs s2/s3/s700 + pooled)."""
    L = []
    cen = {Q: other_census(allsets, trips, v0, mid0, full0, b0, Q)
           for Q in QLIST}
    for side, want in (("ex", {9: (1, 14, 7), 2: (1, 0, 4),
                               3: (2, 0, 2), 700: (11, 0, 4)}),
                       ("mi", {9: (2, 2, 4), 2: (0, 0, 4),
                               3: (0, 0, 3), 700: (0, 0, 3)})):
        for Q in (9, 2, 3, 700):
            s = cen[Q][side]
            n = len(s["near"]) + len(s["far"]) + len(s["non"])
            w = want[Q]
            L.append(f"crossrow {side} s{Q}: near/far/non="
                     f"{len(s['near'])}/{len(s['far'])}/{len(s['non'])} "
                     f"n={n} share={len(s['near']) / n:.4f} "
                     f"(want {w[0]}/{w[1]}/{w[2]})")
        pn = sum(len(cen[Q][side]["near"]) for Q in (2, 3, 700))
        pf = sum(len(cen[Q][side]["far"]) for Q in (2, 3, 700))
        px = sum(len(cen[Q][side]["non"]) for Q in (2, 3, 700))
        n = pn + pf + px
        L.append(f"crossrow {side} still-pooled: near/far/non="
                 f"{pn}/{pf}/{px} n={n} share={pn / n:.4f}")
    ex9, exs = cen[9]["ex"], [cen[Q]["ex"] for Q in (2, 3, 700)]
    n9 = len(ex9["near"]) + len(ex9["far"]) + len(ex9["non"])
    ns = sum(len(s["near"]) + len(s["far"]) + len(s["non"]) for s in exs)
    sh9 = len(ex9["near"]) / n9
    shs = sum(len(s["near"]) for s in exs) / ns
    L.append(f"crossrow extra gap: |{sh9:.4f}-{shs:.4f}|="
             f"{abs(sh9 - shs):.4f} (H5 bar >=0.25)")
    mi9, mis = cen[9]["mi"], [cen[Q]["mi"] for Q in (2, 3, 700)]
    m9 = len(mi9["near"]) + len(mi9["far"]) + len(mi9["non"])
    ms = sum(len(s["near"]) + len(s["far"]) + len(s["non"]) for s in mis)
    L.append(f"crossrow miss gap: |{len(mi9['near']) / m9:.4f}-"
             f"{sum(len(s['near']) for s in mis) / ms:.4f}|="
             f"{abs(len(mi9['near']) / m9 - sum(len(s['near']) for s in mis) / ms):.4f} "
             f"(tabled; no bar)")
    return L

def main():
    m16d, m15d, m34tsv, m35txt, m36txt, workd, evidd = (
        Path(a) for a in sys.argv[1:8])
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
              m16d / "m16-v0-s0009.bin", m16d / "m16-mid-s0009.bin",
              m16d / "m16-full-s0009.bin",
              m16d / "m16-v0-s0700.bin", m16d / "m16-mid-s0700.bin",
              m16d / "m16-full-s0700.bin",
              m15d / "m15-v0.bin", m15d / "m15-mid.bin",
              m15d / "m15-full.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    for q in (m34tsv, m35txt, m36txt):
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

    # ---- unnamed row guards (k 15/6/7/8 + standings + deltas) ----
    print("== unnamed row guards (2/3/9/700 or stop) ==")
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
    print("row guards: " + ("OK" if row_ok else
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
              f"(M35/M36-measured want {M41_CELL[Q]}) "
              f"delta==0 count={int((ddQ == 0).sum())} (want 0)")
        pool_ok = pool_ok and int((ddQ == 0).sum()) == 0
        pool_ok = pool_ok and sets["spQ"]["n"] == M41_CELL[Q]
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

    # ---- pooled value pins (M35 30 + M36 34 = 64 sites) ----
    print("== pooled value pins (18 miss + 46 extra or stop) ==")
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
        for (pQ, r, c), (wo, wad, wstat, wadq, wg0, wgQ) in sorted(
                ALLMISS.items()):
            if pQ != Q:
                continue
            o = off_of(r, c)
            in_mi = bool(allsets[Q]["cells"][c]["mi"][o])
            ad0v = int(abs(int(d0[o])))
            qstat = "bulk" if mQ[o] else "noncell"
            adqv = int(abs(int(dQ[o]))) if mQ[o] else None
            good = (in_mi and o == wo and ad0v == wad and qstat == wstat
                    and adqv == wadq
                    and int(g0[o]) == wg0 and int(gQ[o]) == wgQ)
            pin_ok = pin_ok and good
            print(f"pinmiss s{Q}c{c} r={r} o={o} (want {wo}) "
                  f"ad0={ad0v} (want {wad}) qstat={qstat} "
                  f"(want {wstat}) adQ={adqv} (want {wadq}) "
                  f"g0={int(g0[o])} (want {wg0}) "
                  f"gQ={int(gQ[o])} (want {wgQ}) inmi={in_mi} "
                  f"match={good}")
        for (pQ, r, c), (wo, wad, wstat, wado, wgQ, wgO) in sorted(
                ALLEXTRA.items()):
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
            wantm = sorted(r for (pQ, r, cc) in ALLMISS if pQ == Q
                           and cc == c)
            good = gotm == wantm
            pin_ok = pin_ok and good
            print(f"pinset s{Q}c{c}: miss rows={gotm} (want {wantm}) "
                  f"match={good}")
            gote = sorted(int(pr[o]) for o in
                         np.nonzero(allsets[Q]["cells"][c]["ex"])[0])
            wante = sorted(r for (pQ, r, cc) in ALLEXTRA if pQ == Q
                           and cc == c)
            good = gote == wante
            pin_ok = pin_ok and good
            print(f"pinset s{Q}c{c}: extra rows={gote} (want {wante}) "
                  f"match={good}")
    print("value pins: " + ("OK" if pin_ok else
                            "MISMATCH vs M35/M36: STOP, tabled."))
    if not pin_ok:
        return

    # ---- M41 row-list pins (c336 + c312 or stop) ----
    print("== M41 row-list pins (c336 + c312 or stop) ==")
    prow_ok = True
    for (Q, c), (ws0, wQ, wex, wmi) in sorted(ROWPINS.items()):
        cell = allsets[Q]["cells"][c]
        ex = sorted(set(cell["rQ"]) - set(cell["r0"]))
        mi = sorted(set(cell["r0"]) - set(cell["rQ"]))
        good = bool(cell["r0"] == ws0 and cell["rQ"] == wQ
                    and ex == wex and mi == wmi)
        prow_ok = prow_ok and good
        print(f"pinrow s{Q}c{c}: s0rows={cell['r0']} (want {ws0}) "
              f"Qrows={cell['rQ']} (want {wQ}) extra={ex} (want {wex}) "
              f"miss={mi} (want {wmi}) match={good}")
    print("row-list pins: " + ("OK" if prow_ok else
                               "MISMATCH vs M35/M40: STOP, tabled."))
    if not prow_ok:
        return

    # ---- Task 1: near-miss triple recompute (canon for determinism) ----
    print("== Task 1: near-miss triple recompute ==")
    t1 = time.time()
    canon = triple_canon_lines(allsets, trips, v0, full0)
    for ln in canon:
        print(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.1: s9 boundary census ----
    print("== Task 2.1: s9 boundary census ==")
    for ln in s9census_lines(allsets, trips, v0, mid0, full0, b0):
        print(ln)

    # ---- Task 2.2: still-below recount ----
    print("== Task 2.2: still-below recount ==")
    for ln in stillcensus_lines(allsets, trips, v0, mid0, full0, b0):
        print(ln)

    # ---- Task 2.3: cross-row near table ----
    print("== Task 2.3: cross-row near table ==")
    for ln in crossrow_lines(allsets, trips, v0, mid0, full0, b0):
        print(ln)

    # ---- determinism re-run (Task 1 on s0+9, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+9, second pass) ==")
    v0b, mid0b, full0b, b0b = load_triplet(m16d, 0)
    trips2 = {Q: load_triplet(m16d, Q) for Q in QLIST}
    allsets2 = {}
    for Q in QLIST:
        vQb, midQb, fullQb, bQb = trips2[Q]
        allsets2[Q] = compute_sets_for(v0b, mid0b, full0b, b0b, vQb,
                                       midQb, fullQb, bQb,
                                       SHAPES[Q]["moved"])
    canon2 = triple_canon_lines(allsets2, trips2, v0b, full0b)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")
    for Q in QLIST:
        ex1 = sum(int(allsets[Q]["cells"][c]["ex"].sum())
                  for c in SHAPES[Q]["moved"])
        ex2 = sum(int(allsets2[Q]["cells"][c]["ex"].sum())
                  for c in SHAPES[Q]["moved"])
        mi1 = sum(int(allsets[Q]["cells"][c]["mi"].sum())
                  for c in SHAPES[Q]["moved"])
        mi2 = sum(int(allsets2[Q]["cells"][c]["mi"].sum())
                  for c in SHAPES[Q]["moved"])
        print(f"sets identical s{Q}: extras {ex1}/{ex2} "
              f"missings {mi1}/{mi2}")

    # ---- PNG near-miss map (work dir; evidence copy iff rule meets) ----
    print("== PNG near-miss map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    over = 0.35 * rgbm.astype(np.float32)
    cen_all = {Q: other_census(allsets, trips, v0, mid0, full0, b0, Q)
               for Q in QLIST}
    # Precedence (DESIGN.md): still-noncell red < s9-noncell magenta <
    # far yellow (any row) < near cyan (any row).
    painted = {}
    for Q in (2, 3, 700):
        for (r, c) in (cen_all[Q]["ex"]["non"]
                       + cen_all[Q]["mi"]["non"]):
            painted[(r, c)] = (255, 0, 0)
    for (r, c) in cen_all[9]["ex"]["non"] + cen_all[9]["mi"]["non"]:
        painted[(r, c)] = (255, 0, 255)
    for Q in QLIST:
        for (r, c) in (cen_all[Q]["ex"]["far"]
                       + cen_all[Q]["mi"]["far"]):
            painted[(r, c)] = (255, 255, 0)
    for Q in QLIST:
        for (r, c) in (cen_all[Q]["ex"]["near"]
                       + cen_all[Q]["mi"]["near"]):
            painted[(r, c)] = (0, 255, 255)
    for (r, c), col in painted.items():
        over[r, c] = np.array(col)
    p = workd / "m41-nearmissmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    for name, rgb in (("cyan-near", (0, 255, 255)),
                      ("yellow-far", (255, 255, 0)),
                      ("magenta-s9non", (255, 0, 255)),
                      ("red-stillnon", (255, 0, 0))):
        n = sum(1 for v in painted.values() if v == rgb)
        print(f"png class {name}: pixels={n}")
    print(f"png painted unique rc={len(painted)} "
          f"(s9 30 + still-below 34 site-instances, shared rc once)")
    print("legend: cyan=near(any row) yellow=far(any row) "
          "magenta=s9-noncell red=still-below-noncell "
          "(s0 geometry; Y only)")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    g0b, gQb_of = _gaps_of(trips, v0, full0)
    S9 = allsets[9]
    # H1: 3/3 triple pins match (offset + |d| + status + gaps + gapequal)
    h1_n = 0
    (QE1, rE1, cE1) = TRIPLE_EXTRA
    o = off_of(rE1, cE1)
    wo, wad, wstat, wado, wgQ, wgO = M35_EXTRAS[(QE1, rE1, cE1)]
    ostat = "bulk" if S9["mask0"][o] else "noncell"
    ado = int(abs(int(S9["d0"][o]))) if S9["mask0"][o] else None
    h1_n += int(o == wo and int(abs(int(S9["dQ"][o]))) == wad
                  and ostat == wstat and ado == wado
                  and int(gQb_of[9][o]) == wgQ and int(g0b[o]) == wgO
                  and int(gQb_of[9][o]) != int(g0b[o]))
    for (QM1, rM1, cM1) in TRIPLE_MISS:
        o = off_of(rM1, cM1)
        wo, wad, wstat, wadq, wg0, wgQ = M35_MISS[(QM1, rM1, cM1)]
        qstat = "bulk" if S9["maskQ"][o] else "noncell"
        adq = int(abs(int(S9["dQ"][o]))) if S9["maskQ"][o] else None
        geq = int(g0b[o]) == int(gQb_of[9][o])
        h1_n += int(o == wo and int(abs(int(S9["d0"][o]))) == wad
                      and qstat == wstat and adq == wadq
                      and int(g0b[o]) == wg0
                      and int(gQb_of[9][o]) == wgQ
                      and geq == ((rM1, cM1) == (301, 312)))
    h1 = h1_n == 3
    print(f"H1_TRIPLE_REPRO: match={h1_n}/3 (bar 3/3; met={h1})")
    # H2: still-below near counts reproduce M36 (per-shape + pooled)
    cen9 = other_census(allsets, trips, v0, mid0, full0, b0, 9)
    cenS = {Q: other_census(allsets, trips, v0, mid0, full0, b0, Q)
            for Q in (2, 3, 700)}
    h2_ok = True
    for Q in (2, 3, 700):
        for side in ("ex", "mi"):
            s = cenS[Q][side]
            got = (len(s["near"]), len(s["far"]), len(s["non"]))
            want = M36_SPLITS[Q][side]
            h2_ok = h2_ok and got == want
            print(f"H2 s{Q} {side}: {got[0]}/{got[1]}/{got[2]} "
                  f"(want {want[0]}/{want[1]}/{want[2]})")
    pxn = sum(len(cenS[Q]["ex"]["near"]) for Q in (2, 3, 700))
    pxf = sum(len(cenS[Q]["ex"]["far"]) for Q in (2, 3, 700))
    pxx = sum(len(cenS[Q]["ex"]["non"]) for Q in (2, 3, 700))
    pmn = sum(len(cenS[Q]["mi"]["near"]) for Q in (2, 3, 700))
    pmf = sum(len(cenS[Q]["mi"]["far"]) for Q in (2, 3, 700))
    pmx = sum(len(cenS[Q]["mi"]["non"]) for Q in (2, 3, 700))
    h2_ok = h2_ok and (pxn, pxf, pxx) == (14, 0, 10)
    h2_ok = h2_ok and (pmn, pmf, pmx) == (0, 0, 10)
    h2 = bool(h2_ok)
    print(f"H2_STILL_REPRO: pooled ex {pxn}/{pxf}/{pxx} (want 14/0/10) "
          f"mi {pmn}/{pmf}/{pmx} (want 0/0/10); met={h2}")
    # H3: s9 3/30 exact (near 3 + b5 0 both sides + splits)
    ex9, mi9 = cen9["ex"], cen9["mi"]
    h3 = (len(ex9["near"]) + len(mi9["near"]) == 3
          and ex9["b5"] == 0 and mi9["b5"] == 0
          and (len(ex9["near"]), len(ex9["far"]), len(ex9["non"]))
          == (1, 14, 7)
          and (len(mi9["near"]), len(mi9["far"]), len(mi9["non"]))
          == (2, 2, 4))
    print(f"H3_S9_EXACT: near={len(ex9['near']) + len(mi9['near'])}/30 "
          f"b5ex={ex9['b5']} b5mi={mi9['b5']} "
          f"ex={len(ex9['near'])}/{len(ex9['far'])}/{len(ex9['non'])} "
          f"mi={len(mi9['near'])}/{len(mi9['far'])}/{len(mi9['non'])} "
          f"(bar 3 + 0/0 + 1/14/7 + 2/2/4; met={h3})")
    # H4: still-below boundary census exact
    pxb5 = sum(cenS[Q]["ex"]["b5"] for Q in (2, 3, 700))
    h4 = (pxb5 == 0 and (pxn, pxf, pxx) == (14, 0, 10)
          and (pmn, pmf, pmx) == (0, 0, 10))
    print(f"H4_STILL_EXACT: exb5={pxb5} ex={pxn}/{pxf}/{pxx} "
          f"mi={pmn}/{pmf}/{pmx} "
          f"(bar 0 + 14/0/10 + 0/0/10; met={h4})")
    # H5: cross-row extra-side near-rate gap >= 0.25
    sh9 = len(ex9["near"]) / (len(ex9["near"]) + len(ex9["far"])
                               + len(ex9["non"]))
    shs = pxn / (pxn + pxf + pxx)
    h5_gap = abs(sh9 - shs)
    h5 = h5_gap >= 0.25
    print(f"H5_CROSSROW: s9 {sh9:.4f} vs still {shs:.4f} "
          f"gap={h5_gap:.4f} (bar >=0.25; met={h5})")
    # H6: all 3 nears read row-list-edge (singletons noted)
    h6_n = 0
    cellE = allsets[9]["cells"][cE1]
    h6e = (len(cellE["rQ"]) == 1 or rE1 == min(cellE["rQ"])
           or rE1 == max(cellE["rQ"]))
    h6_n += int(h6e)
    print(f"H6 edge extra ({rE1},{cE1}): ownrows={cellE['rQ']} "
          f"edge={h6e} singleton={len(cellE['rQ']) == 1}")
    for (QM1, rM1, cM1) in TRIPLE_MISS:
        cellM = allsets[9]["cells"][cM1]
        h6m = (len(cellM["r0"]) == 1 or rM1 == min(cellM["r0"])
               or rM1 == max(cellM["r0"]))
        h6_n += int(h6m)
        print(f"H6 edge miss ({rM1},{cM1}): ownrows={cellM['r0']} "
              f"edge={h6m} singleton={len(cellM['r0']) == 1}")
    h6 = h6_n == 3
    print(f"H6_ROWEDGE: edge={h6_n}/3 (bar 3/3; met={h6})")
    # H7: exactly (301,312) gap-equal among the triple
    geq = []
    o = off_of(rE1, cE1)
    if int(gQb_of[9][o]) == int(g0b[o]):
        geq.append((rE1, cE1))
    for (QM1, rM1, cM1) in TRIPLE_MISS:
        o = off_of(rM1, cM1)
        if int(g0b[o]) == int(gQb_of[9][o]):
            geq.append((rM1, cM1))
    h7 = geq == [(301, 312)]
    print(f"H7_GAPEQUAL: gapequal={geq} (bar [(301, 312)]; met={h7})")
    print(f"PNG rule: H1={h1} H2={h2} H5={h5} "
          f"(copy iff H1 and H2 and H5: "
          f"{bool(h1 and h2 and h5)})")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=triple T2=s9census+stillcensus+crossrow R=controls")


if __name__ == "__main__":
    main()
