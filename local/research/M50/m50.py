#!/usr/bin/env python3
"""M50 731/733 full-set attribution: wipe rows + dest recount + static census.

Usage: m50.py M16_DIR M15_DIR M28TSV M34TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), m28-census.tsv (731/733 named wipe rows to reproduce)
and m34-census.tsv (731/733/761 unnamed dest rows to reproduce);
raw XFB dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt
text goes to stdout (redirect to WORK_DIR/m50.txt); PNG static-site
maps to WORK_DIR (evidence copy iff the DESIGN.md rule meets,
decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: wipe reproduction (4 wipe cells: s0-rows vs Q-rows vs miss)
     + dest recount (5 dest cells: extras + g_s0==0) + full-set
     + 0-outside checks
  2: wiped values (41 sites M36-style) + static census (g==0 by
     side + |d| at static) + wipe-vs-dest side-by-side (measured
     vs M43-cited)
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
M19_CELL_S0 = 2475  # s761/s731/s733 cell counts unpinned: tabled as measured
M20_TAIL_S0 = 102
M20_TAIL_S0_SUB = (28, 74)  # (8-15, 16+)
M20_TAIL_S0_MAX = 47
M19_POSRATE_S0 = 0.8093  # P(d>0) on s0 cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
NAMED8 = [257, 277, 296, 301, 321, 340, 342, 343]
S0_ROWS = {  # M28-pinned s0 named rows (wipe row pins derive from these)
    257: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    277: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    296: [24, 25, 26, 27, 28, 31, 32, 33, 34],
    301: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
    321: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    340: [24, 25, 26, 27, 31, 32, 33, 34],
    342: [27, 28, 29, 34, 35],
    343: [26, 27],
}
# Per-shape pins from the M28 (named wipes) + M34 (unnamed dests) TSV rows.
# NOV: {col: (n, ov)}; N0: {col: s0 n}; STAND: {col: (miss, extra, delta, stand)}.
SHAPES = {
    761: {"tail": 106, "jacc": "0.9623",
          "wipes": [], "dests": [54],
          "nov": {54: (4, 0)},
          "n0": {54: 0},
          "stand": {54: (0, 4, 4, "extra")},
          "pool": (4, 0)},  # (dest extras, wipe missings)
    731: {"tail": 100, "jacc": "0.6833",
          "wipes": [257, 277], "dests": [259, 279],
          "nov": {257: (0, 0), 277: (0, 0), 259: (9, 0), 279: (9, 0)},
          "n0": {257: 10, 277: 10, 259: 0, 279: 0},
          "stand": {257: (10, 0, 10, "missing"),
                    277: (10, 0, 10, "missing"),
                    259: (0, 9, 9, "extra"),
                    279: (0, 9, 9, "extra")},
          "pool": (18, 20)},  # (dest extras, wipe missings)
    733: {"tail": 100, "jacc": "0.6694",
          "wipes": [301, 321], "dests": [303, 323],
          "nov": {301: (0, 0), 321: (0, 0), 303: (9, 0), 323: (10, 0)},
          "n0": {301: 11, 321: 10, 303: 0, 323: 0},
          "stand": {301: (11, 0, 11, "missing"),
                    321: (10, 0, 10, "missing"),
                    303: (0, 9, 9, "extra"),
                    323: (0, 10, 10, "extra")},
          "pool": (19, 21)},  # (dest extras, wipe missings)
}
QLIST = [761, 731, 733]
QWIPES = [731, 733]  # shapes with wipe cells (761 dest-recount only)
# Dest row pins (M43 §Task 1, recount targets — rows only, values cited).
DEST_ROWS = {761: {54: [259, 261, 263, 274]},
             731: {259: list(range(25, 34)), 279: list(range(25, 34))},
             733: {303: list(range(25, 34)), 323: list(range(25, 35))}}
# Dest g_s0==0 pins per cell (M43 gap-sign tables: -0 counts).
DEST_G0 = {761: {54: 0}, 731: {259: 7, 279: 6}, 733: {303: 8, 323: 7}}
# M43 CITED dest per-site rows (REPORT §Task 2, by reference — never
# recomputed; used ONLY for the Task-2.2 dest |d| at-static split and
# the Task-2.3 side-by-side). Entries: (adQ, gQ, g0).
M43_CITED_DEST = {
    (731, 259): [(10, -23, 0), (15, -37, 0), (17, -43, 0), (18, -44, 0),
                 (17, -43, 0), (17, -42, 0), (17, -40, 0), (16, -38, -1),
                 (13, -30, -6)],
    (731, 279): [(11, -27, 0), (16, -39, 0), (17, -41, 0), (17, -40, 0),
                 (16, -40, 0), (16, -41, 0), (17, -43, -1), (19, -46, -3),
                 (16, -38, -9)],
    (733, 303): [(11, -24, 0), (16, -38, 0), (15, -39, 0), (13, -35, 0),
                 (13, -32, 0), (13, -31, 0), (13, -31, 0), (12, -31, 0),
                 (9, -25, -3)],
    (733, 323): [(11, -29, 0), (18, -42, 0), (18, -42, 0), (17, -40, 0),
                 (16, -39, 0), (16, -41, 0), (16, -41, 0), (19, -44, -3),
                 (15, -38, -9), (8, -20, -11)],
}
# M43 CITED dest stats (REPORT §Task 2, by reference).
M43_CITED_STATS = {
    "pooled41_med": 16.0, "pooled41_mean": 14.2927,
    "pooled37_med": 16.0, "s731_med": 16.5, "s731_mean": 15.8333,
    "s733_med": 15.0, "s733_mean": 14.1579,
    "bulk41": 4, "bulk37": 0, "mm41": 13, "m041": 28, "mm37": 9,
    "m037": 28,
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


def census_named_of(colrows, s0n):
    """Per-named-column presence over NAMED8 (exact-match rule, M28 verbatim).

    colrows: {col: rows} (missing key == []); s0n: {col: rows0}.
    Returns {col: {n, ov, pres, miss, extra, delta}}.
    """
    out = {}
    for c, r0 in s0n.items():
        rs = colrows.get(c, [])
        ov = len(set(rs) & set(r0))
        miss, extra = len(r0) - ov, len(rs) - ov
        out[c] = {"n": len(rs), "ov": ov,
                  "pres": 1 if rs == r0 else 0,
                  "miss": miss, "extra": extra, "delta": miss + extra}
    return out


PNAME = ("Y", "U", "V")


def attrib_lines(tag, priv, miss, shared, dA, mA, dB, mB,
                 v0A, fullA, v0B, fullB):
    """Task 1.1/1.2: per-site private + missing rows with cross values.

    A = s0, B = other shape. priv = T_B - T_A (or the per-cell
    extra subset), miss = T_A - T_B (or the per-cell missing
    subset). Returns (lines, summary_dict). Offsets in ascending
    order. (M27/M33/M36 verbatim.)
    """
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    aA = np.frombuffer(v0A, np.uint8).astype(np.int16)
    bA = np.frombuffer(fullA, np.uint8).astype(np.int16)
    aB = np.frombuffer(v0B, np.uint8).astype(np.int16)
    bB = np.frombuffer(fullB, np.uint8).astype(np.int16)
    gA = aA - bA
    gB = aB - bB
    out = {}
    for nm, q, dQ, dO, mO, gQ, gO in (
            ("priv", priv, dB, dA, mA, gB, gA),
            ("miss", miss, dA, dB, mB, gA, gB)):
        idx = np.nonzero(q)[0]
        n_near = n_far = n_non = 0
        bulk_ads = []
        geq = ageq = 0
        for o in idx:
            o = int(o)
            adq = int(abs(int(dQ[o])))
            if mO[o]:
                ad = int(abs(int(dO[o])))
                assert ad < 8, f"{tag} {nm} o={o}: other-frame tail?!"
                st = "bulk"
                bulk_ads.append(ad)
                if ad in (6, 7):
                    n_near += 1
                else:
                    n_far += 1
                ado = str(ad)
            else:
                st = "noncell"
                n_non += 1
                ado = "n/a"
            if int(gQ[o]) == int(gO[o]):
                geq += 1
            if abs(int(gQ[o])) == abs(int(gO[o])):
                ageq += 1
            L.append(f"{tag} {nm} o={o} plane={PNAME[int(pl[o])]} "
                     f"rc=({int(pr[o])},{int(pc[o])}) adQ={adq} "
                     f"ostat={st} adO={ado} gQ={int(gQ[o])} gO={int(gO[o])}")
        n = len(idx)
        L.append(f"{tag} {nm} summary: n={n} near={n_near} "
                 f"({n_near / n if n else 0:.4f}) far={n_far} "
                 f"({n_far / n if n else 0:.4f}) noncell={n_non} "
                 f"({n_non / n if n else 0:.4f})")
        if bulk_ads:
            ba = np.array(bulk_ads, np.int16)
            vals, cnts = np.unique(ba, return_counts=True)
            L.append(f"{tag} {nm} bulk-adO values: "
                     + " ".join(f"{int(v)}:{int(c)}"
                                for v, c in zip(vals, cnts)))
        else:
            L.append(f"{tag} {nm} bulk-adO values: (none: all noncell)")
        L.append(f"{tag} {nm} gaps: signed-eq={geq}/{n} "
                 f"({geq / n if n else 0:.4f}) abs-eq={ageq}/{n} "
                 f"({ageq / n if n else 0:.4f})")
        out[nm] = {"n": n, "near": n_near, "far": n_far, "non": n_non}
    out["shared_n"] = int(shared.sum())
    return L, out


def gapsign_lines(tag, priv, miss, v0A, fullA, v0B, fullB):
    """Task 2.2: signed-gap sign tables (g_Q x g_O per site)."""
    L = []
    aA = np.frombuffer(v0A, np.uint8).astype(np.int16)
    bA = np.frombuffer(fullA, np.uint8).astype(np.int16)
    aB = np.frombuffer(v0B, np.uint8).astype(np.int16)
    bB = np.frombuffer(fullB, np.uint8).astype(np.int16)
    gA, gB = aA - bA, aB - bB

    def sgn(x):
        return "+" if x > 0 else ("-" if x < 0 else "0")

    for nm, q, gQ, gO in (("priv", priv, gB, gA),
                          ("miss", miss, gA, gB)):
        idx = [int(o) for o in np.nonzero(q)[0]]
        n = len(idx)
        cells = {}
        for o in idx:
            k = (sgn(int(gQ[o])), sgn(int(gO[o])))
            cells[k] = cells.get(k, 0) + 1
        order = [(a, b) for a in ("+", "-", "0") for b in ("+", "-", "0")]
        L.append(f"{tag} gapsign {nm}: n={n} "
                 + " ".join(f"{a}{b}={cells.get((a, b), 0)}"
                            for a, b in order))
        pp = cells.get(("+", "+"), 0)
        L.append(f"{tag} gapsign {nm} plusplus: {pp}/{n} "
                 f"({pp / n if n else 0:.4f})")
    return L


def dstats_lines(tag, priv, miss, dB, dA):
    """Task 2.3: |d| stats per set (|d_Q| on priv, |d_s0| on miss)."""
    L = []
    for nm, q, dQ in (("priv", priv, dB), ("miss", miss, dA)):
        idx = [int(o) for o in np.nonzero(q)[0]]
        ads = sorted(int(abs(int(dQ[o]))) for o in idx)
        n = len(ads)
        if n:
            a = np.asarray(ads, dtype=np.float64)
            L.append(f"{tag} dstats {nm}: n={n} list=[{','.join(map(str, ads))}] "
                     f"min={a.min():.0f} med={np.median(a):.1f} "
                     f"mean={a.mean():.4f} max={a.max():.0f}")
        else:
            L.append(f"{tag} dstats {nm}: n=0 (empty set)")
    return L


def load_triplet(m16d: Path, s: int):
    vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
    mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
    ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
    return vv, mm, ff, synth_w_bytes(vv, ff, 0.5)


def compute_sets_for(v0, mid0, full0, b0, vQ, midQ, fullQ, bQ, cols):
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
    # per-cell extra/missing masks over this shape's wipe+dest cells
    cells = {}
    for c in cols:
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


def static_counts(mask, gA, gB):
    """g==0 counts on a site mask: (n, n_gA0, n_gB0, n_either0, n_both0)."""
    idx = [int(o) for o in np.nonzero(mask)[0]]
    n = len(idx)
    a0 = sum(1 for o in idx if int(gA[o]) == 0)
    b0 = sum(1 for o in idx if int(gB[o]) == 0)
    e0 = sum(1 for o in idx if int(gA[o]) == 0 or int(gB[o]) == 0)
    both0 = sum(1 for o in idx if int(gA[o]) == 0 and int(gB[o]) == 0)
    return n, a0, b0, e0, both0


def ad_split_lines(tag, mask, dV, gOther):
    """|d| lists split by other-frame static (gOther==0) vs non-static."""
    L = []
    st = sorted(int(abs(int(dV[o]))) for o in np.nonzero(mask)[0]
                if int(gOther[o]) == 0)
    ns = sorted(int(abs(int(dV[o]))) for o in np.nonzero(mask)[0]
                if int(gOther[o]) != 0)
    for nm, v in (("static", st), ("nonstatic", ns)):
        if v:
            a = np.asarray(v, dtype=np.float64)
            L.append(f"{tag} ad-{nm}: n={len(v)} list=[{','.join(map(str, v))}] "
                     f"med={np.median(a):.1f} mean={a.mean():.4f}")
        else:
            L.append(f"{tag} ad-{nm}: n=0 (empty set)")
    return L


def task1_lines_for(Q, sets, v0, full0, vQ, fullQ):
    """Task-1 receipt lines: wipe rowlists + dest recount + full-set."""
    L = []
    g0 = (np.frombuffer(v0, np.uint8).astype(np.int16)
          - np.frombuffer(full0, np.uint8).astype(np.int16))
    gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
          - np.frombuffer(fullQ, np.uint8).astype(np.int16))
    wipe_mi = np.zeros(N, bool)
    dest_ex = np.zeros(N, bool)
    for c in SHAPES[Q]["wipes"]:
        ex, mi = sets["cells"][c]["ex"], sets["cells"][c]["mi"]
        wipe_mi |= mi
        r0, rQ = sets["cells"][c]["r0"], sets["cells"][c]["rQ"]
        ov = len(set(r0) & set(rQ))
        wipe = (len(rQ) == 0 and ov == 0 and int(ex.sum()) == 0)
        L.append(f"wiperow s{Q}c{c}: s0rows={r0} s{Q}rows={rQ} "
                 f"mi_rows={sorted(set(r0) - set(rQ))} "
                 f"ex_rows={sorted(set(rQ) - set(r0))} "
                 f"miss_n={int(mi.sum())} extra_n={int(ex.sum())}")
        L.append(f"wipeproof s{Q}c{c}: nQ={len(rQ)} ov={ov} "
                 f"miss={int(mi.sum())} extra={int(ex.sum())} "
                 f"delta={int(mi.sum()) + int(ex.sum())} wipe={wipe}")
    for c in SHAPES[Q]["dests"]:
        ex, mi = sets["cells"][c]["ex"], sets["cells"][c]["mi"]
        dest_ex |= ex
        r0, rQ = sets["cells"][c]["r0"], sets["cells"][c]["rQ"]
        ov = len(set(r0) & set(rQ))
        fresh = (len(r0) == 0 and ov == 0 and int(mi.sum()) == 0)
        n_g0 = sum(1 for o in np.nonzero(ex)[0] if int(g0[int(o)]) == 0)
        L.append(f"destrow s{Q}c{c}: s0rows={r0} s{Q}rows={rQ} "
                 f"ex_rows={sorted(set(rQ) - set(r0))} "
                 f"mi_rows={sorted(set(r0) - set(rQ))} "
                 f"miss_n={int(mi.sum())} extra_n={int(ex.sum())}")
        L.append(f"destrecount s{Q}c{c}: n0={len(r0)} ov={ov} "
                 f"miss={int(mi.sum())} extra={int(ex.sum())} "
                 f"fresh={fresh} g_s0eq0={n_g0}/{int(ex.sum())}")
    # kept g==0 counts + full-set + 0-outside checks
    shared = sets["shared"]
    n, a0, b0, e0, both0 = static_counts(shared, g0, gQ)
    L.append(f"keptstatic s{Q}: shared_n={n} g_s0eq0={a0} g_Qeq0={b0} "
             f"either0={e0} both0={both0}")
    priv, miss = sets["priv"], sets["miss"]
    tQ = sets["tQ"]
    out_priv = priv & ~dest_ex
    out_miss = miss & ~wipe_mi
    L.append(f"fullset s{Q}: tail={int(tQ.sum())} priv={int(priv.sum())} "
             f"miss={int(miss.sum())} shared={int(shared.sum())} "
             f"dest_ex={int(dest_ex.sum())} wipe_mi={int(wipe_mi.sum())} "
             f"outside_priv={int(out_priv.sum())} "
             f"outside_miss={int(out_miss.sum())} "
             f"priv_is_dest={bool((priv == dest_ex).all())} "
             f"miss_is_wipe={bool((miss == wipe_mi).all())}")
    if int(out_priv.sum()) or int(out_miss.sum()):
        pl, pr, pc = sets["pl"], sets["pr"], sets["pc"]
        L.append(f"outside s{Q} priv_rc="
                 f"{sorted((int(pr[o]), int(pc[o])) for o in np.nonzero(out_priv)[0])}")
        L.append(f"outside s{Q} miss_rc="
                 f"{sorted((int(pr[o]), int(pc[o])) for o in np.nonzero(out_miss)[0])}")
    return L, wipe_mi, dest_ex


def task2_lines_for(Q, sets, v0, full0, vQ, fullQ):
    """Task-2 receipt lines: wiped values + static census (wipes only)."""
    L = []
    d0, m0 = sets["d0"], sets["mask0"]
    dQ, mQ = sets["dQ"], sets["maskQ"]
    shared = sets["shared"]
    g0 = (np.frombuffer(v0, np.uint8).astype(np.int16)
          - np.frombuffer(full0, np.uint8).astype(np.int16))
    gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
          - np.frombuffer(fullQ, np.uint8).astype(np.int16))
    empty = np.zeros(N, bool)
    wipe_mi = np.zeros(N, bool)
    for c in SHAPES[Q]["wipes"]:
        mi = sets["cells"][c]["mi"]
        wipe_mi |= mi
        # wiped-value rows: miss leg carries |d_s0| + Q status/gaps
        la, _ = attrib_lines(f"s{Q}w{c}", empty, mi, shared, d0, m0,
                             dQ, mQ, v0, full0, vQ, fullQ)
        L += la
        L += dstats_lines(f"s{Q}w{c}", empty, mi, dQ, d0)
        L += gapsign_lines(f"s{Q}w{c}", empty, mi, v0, full0, vQ, fullQ)
        n, a0, b0, e0, both0 = static_counts(mi, g0, gQ)
        L.append(f"wipestatic s{Q}w{c}: n={n} g_s0eq0={a0} g_Qeq0={b0} "
                 f"either0={e0} both0={both0}")
        L += ad_split_lines(f"s{Q}w{c}", mi, d0, gQ)
    la_pool, summ = attrib_lines(f"s{Q}wpool", empty, wipe_mi, shared,
                                 d0, m0, dQ, mQ, v0, full0, vQ,
                                 fullQ)
    L += la_pool
    L += dstats_lines(f"s{Q}wpool", empty, wipe_mi, dQ, d0)
    L += gapsign_lines(f"s{Q}wpool", empty, wipe_mi, v0, full0, vQ,
                       fullQ)
    n, a0, b0, e0, both0 = static_counts(wipe_mi, g0, gQ)
    L.append(f"wipestatic s{Q}wpool: n={n} g_s0eq0={a0} g_Qeq0={b0} "
             f"either0={e0} both0={both0}")
    L += ad_split_lines(f"s{Q}wpool", wipe_mi, d0, gQ)
    return L, summ, wipe_mi


def main():
    m16d, m15d, m28tsv, m34tsv, workd, evidd = (
        Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin",
              m16d / "m16-v0-s0761.bin", m16d / "m16-mid-s0761.bin",
              m16d / "m16-full-s0761.bin",
              m16d / "m16-v0-s0731.bin", m16d / "m16-mid-s0731.bin",
              m16d / "m16-full-s0731.bin",
              m16d / "m16-v0-s0733.bin", m16d / "m16-mid-s0733.bin",
              m16d / "m16-full-s0733.bin",
              m15d / "m15-v0.bin", m15d / "m15-mid.bin",
              m15d / "m15-full.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    for tsv in (m28tsv, m34tsv):
        qb = tsv.read_bytes()
        print(f"input {tsv}: bytes={len(qb)} "
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
        print("MISMATCH vs M17-M42 baselines: STOP, tabled.")
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
    rows0 = {c: y_col_rows(t0, c, pl, pr, pc) for c in NAMED8}
    ref_ok = all(rows0[c] == S0_ROWS[c] for c in NAMED8)
    for c in NAMED8:
        print(f"s0 ref col {c}: n={len(rows0[c])} match={rows0[c] == S0_ROWS[c]}")
    if not ref_ok:
        print("s0 NAMED REF ROWS MISMATCH vs M28: STOP, tabled.")
        return

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

    # ---- FULL named TSV guard (M28 match or stop) ----
    print("== named TSV guard (M28 match or stop) ==")
    s0n = {c: per[0]["ycols"].get(c, []) for c in NAMED8}
    tsv28_lines = m28tsv.read_text(errors="replace").splitlines()
    want_hdr28 = "\t".join(["shape", "tail_n", "J_vs_s0"]
                           + [f"{k}{c}" for c in NAMED8
                              for k in ("n", "ov", "pres")])
    hdr28_cols = []
    for tok in tsv28_lines[0].split("\t")[3:]:
        if tok.startswith("n"):
            hdr28_cols.append(int(tok[1:]))
    print(f"m28-census.tsv rows={len(tsv28_lines) - 1} "
          f"hdr_match={tsv28_lines[0] == want_hdr28} "
          f"universe_match={hdr28_cols == NAMED8}")
    tsv28_ok = (tsv28_lines[0] == want_hdr28 and len(tsv28_lines) == 765
                and hdr28_cols == NAMED8)
    first_bad28 = None
    for s in range(764):
        rec = per[s]
        cen = census_named_of(rec["ycols"], s0n)
        rec["ncen"] = cen
        rec["nmoved"] = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
        row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in NAMED8:
            row += [str(cen[c]["n"]), str(cen[c]["ov"]),
                    str(cen[c]["pres"])]
        if "\t".join(row) != tsv28_lines[s + 1]:
            tsv28_ok = False
            if first_bad28 is None:
                first_bad28 = s
    print(f"named TSV full match (764 rows): {tsv28_ok}"
          + ("" if tsv28_ok else f" first_bad_shape={first_bad28}"))
    if first_bad28 is not None:
        print(f"m28 row: {tsv28_lines[first_bad28 + 1]}")
        rec = per[first_bad28]
        row = [str(first_bad28), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in NAMED8:
            row += [str(rec["ncen"][c]["n"]), str(rec["ncen"][c]["ov"]),
                    str(rec["ncen"][c]["pres"])]
        print(f"mine row: {'\t'.join(row)}")
    print("named TSV guard: " + ("OK" if tsv28_ok else
                                 "MISMATCH vs M28: STOP, tabled."))
    if not tsv28_ok:
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

    # ---- 731/733/761 row guards (named wipes + unnamed dests or stop) ----
    print("== 731/733/761 row guards (wipes + dests or stop) ==")
    row_ok = True
    for Q in QLIST:
        spec = SHAPES[Q]
        rQ = per[Q]
        print(f"s{Q} tail={rQ['tail']} (want {spec['tail']}) "
              f"J={rQ['j']:.4f} (want {spec['jacc']})")
        print(f"s{Q} nmoved={rQ['nmoved']} (want {spec['wipes']}) "
              f"umoved={rQ['umoved']} (want {spec['dests']})")
        row_ok = (row_ok and rQ["tail"] == spec["tail"]
                  and f"{rQ['j']:.4f}" == spec["jacc"]
                  and rQ["nmoved"] == spec["wipes"]
                  and rQ["umoved"] == spec["dests"])
        for c in spec["wipes"]:
            e = rQ["ncen"][c]
            wn, wov = spec["nov"][c]
            wn0 = spec["n0"][c]
            wm, we, wd, wst = spec["stand"][c]
            stand = ("missing" if e["miss"] > 0 and e["extra"] == 0
                     else ("extra" if e["miss"] == 0 and e["extra"] > 0
                           else "mixed"))
            good = (e["n"] == wn and e["ov"] == wov and len(s0n[c]) == wn0
                    and e["miss"] == wm and e["extra"] == we
                    and e["delta"] == wd and stand == wst
                    and e["pres"] == 0)
            row_ok = row_ok and good
            print(f"s{Q} wipe c{c}: n/ov={e['n']}/{e['ov']} "
                  f"(want {wn}/{wov}) n0={len(s0n[c])} (want {wn0}) "
                  f"miss/extra/delta={e['miss']}/{e['extra']}/{e['delta']} "
                  f"(want {wm}/{we}/{wd}) stand={stand} (want {wst}) "
                  f"match={good}")
        for c in spec["dests"]:
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
            print(f"s{Q} dest c{c}: n/ov={e['n']}/{e['ov']} "
                  f"(want {wn}/{wov}) n0={len(s0u[c])} (want {wn0}) "
                  f"miss/extra/delta={e['miss']}/{e['extra']}/{e['delta']} "
                  f"(want {wm}/{we}/{wd}) stand={stand} (want {wst}) "
                  f"match={good}")
    print("731/733/761 row guards: " + ("OK" if row_ok else
                                        "MISMATCH vs M28/M34: STOP, tabled."))
    if not row_ok:
        return

    # ---- s0+Q sets + pooled-count guards + dest g_s0==0 guard ----
    print("== s0+Q sets + pooled-count guards ==")
    allsets = {}
    pool_ok = True
    g0 = (np.frombuffer(v0, np.uint8).astype(np.int16)
          - np.frombuffer(full0, np.uint8).astype(np.int16))
    for Q in QLIST:
        vQ, midQ, fullQ, bQ = trips[Q]
        cols = SHAPES[Q]["wipes"] + SHAPES[Q]["dests"]
        sets = compute_sets_for(v0, mid0, full0, b0, vQ, midQ, fullQ, bQ,
                                cols)
        allsets[Q] = sets
        maskQ, dQ = sets["maskQ"], sets["dQ"]
        ddQ = dQ[maskQ]
        print(f"s{Q} cell7 n={sets['spQ']['n']} (unpinned: tabled) "
              f"delta==0 count={int((ddQ == 0).sum())} (want 0)")
        pool_ok = pool_ok and int((ddQ == 0).sum()) == 0
        ex_n = sum(int(sets["cells"][c]["ex"].sum())
                   for c in SHAPES[Q]["dests"])
        mi_n = sum(int(sets["cells"][c]["mi"].sum())
                   for c in SHAPES[Q]["wipes"])
        wex, wmi = SHAPES[Q]["pool"]
        print(f"s{Q} pooled dest extras={ex_n} (want {wex}) "
              f"wipe missings={mi_n} (want {wmi})")
        pool_ok = pool_ok and ex_n == wex and mi_n == wmi
    wipe_planes = {int(pl[o]) for Q in QWIPES for c in SHAPES[Q]["wipes"]
                   for o in np.nonzero(allsets[Q]["cells"][c]["mi"])[0]}
    dest_planes = {int(pl[o]) for Q in QLIST for c in SHAPES[Q]["dests"]
                   for o in np.nonzero(allsets[Q]["cells"][c]["ex"])[0]}
    print(f"pooled wipe-miss planes={sorted(wipe_planes)} (want [0]=all-Y)")
    print(f"pooled dest-extra planes={sorted(dest_planes)} (want [0]=all-Y)")
    pool_ok = pool_ok and wipe_planes == {0} and dest_planes == {0}
    # dest g_s0==0 guard (28/41 or stop)
    g0n, g0want = 0, 0
    for Q in QLIST:
        for c in SHAPES[Q]["dests"]:
            ex = allsets[Q]["cells"][c]["ex"]
            got = sum(1 for o in np.nonzero(ex)[0]
                      if int(g0[int(o)]) == 0)
            want = DEST_G0[Q][c]
            g0n += got
            g0want += want
            okc = (got == want
                   and allsets[Q]["cells"][c]["rQ"] == DEST_ROWS[Q][c])
            pool_ok = pool_ok and okc
            print(f"destrecount-guard s{Q}c{c}: rows_match="
                  f"{allsets[Q]['cells'][c]['rQ'] == DEST_ROWS[Q][c]} "
                  f"g_s0eq0={got} (want {want}) match={okc}")
    print(f"destrecount-guard pooled g_s0eq0={g0n} (want {g0want}=28/41)")
    pool_ok = pool_ok and g0n == 28 and g0want == 28
    # cell-7 moved guards: wiped g_s0!=0, dest g_Q!=0, kept both!=0
    for Q in QLIST:
        vQ, _, fullQ, _ = trips[Q]
        gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
              - np.frombuffer(fullQ, np.uint8).astype(np.int16))
        for c in SHAPES[Q]["wipes"]:
            mi = allsets[Q]["cells"][c]["mi"]
            bad = sum(1 for o in np.nonzero(mi)[0]
                      if int(g0[int(o)]) == 0)
            pool_ok = pool_ok and bad == 0
        for c in SHAPES[Q]["dests"]:
            ex = allsets[Q]["cells"][c]["ex"]
            bad = sum(1 for o in np.nonzero(ex)[0]
                      if int(gQ[int(o)]) == 0)
            pool_ok = pool_ok and bad == 0
        sh = allsets[Q]["shared"]
        bad = sum(1 for o in np.nonzero(sh)[0]
                  if int(g0[int(o)]) == 0 or int(gQ[int(o)]) == 0)
        print(f"moved-guard s{Q}: kept g0-bad={bad} (want 0)")
        pool_ok = pool_ok and bad == 0
    print("pooled-count guards: "
          + ("OK" if pool_ok else "MISMATCH: STOP, tabled."))
    if not pool_ok:
        for Q in QLIST:
            ex_rc = sorted((int(pr[o]), int(pc[o]))
                           for c in SHAPES[Q]["dests"]
                           for o in np.nonzero(allsets[Q]["cells"][c]["ex"])[0])
            mi_rc = sorted((int(pr[o]), int(pc[o]))
                           for c in SHAPES[Q]["wipes"]
                           for o in np.nonzero(allsets[Q]["cells"][c]["mi"])[0])
            print(f"s{Q} dest extras rc={ex_rc}")
            print(f"s{Q} wipe missings rc={mi_rc}")
        return

    # ---- Task 1: wipe rowlists + dest recount + full-set ----
    print("== Task 1 (731/733/761): wipes + dest recount + full-set ==")
    t1 = time.time()
    canon = []
    wipe_byQ, dest_byQ = {}, {}
    for Q in QLIST:
        vQ, _, fullQ, _ = trips[Q]
        cl, wmi, dex = task1_lines_for(
            Q, allsets[Q], v0, full0, vQ, fullQ)
        wipe_byQ[Q], dest_byQ[Q] = wmi, dex
        canon += [f"--- shape {Q} ---"] + cl
    for ln in canon:
        print(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2: wiped values + static census (731/733 wipes) ----
    print("== Task 2 (731/733): wiped values + static census ==")
    t1 = time.time()
    t2lines = []
    for Q in QWIPES:
        vQ, _, fullQ, _ = trips[Q]
        cl, _, _ = task2_lines_for(Q, allsets[Q], v0, full0, vQ, fullQ)
        t2lines += [f"--- shape {Q} wiped values ---"] + cl
    for ln in t2lines:
        print(ln)
    print(f"(Task-2 wall: {time.time() - t1:.1f}s)")

    # ---- wipe-vs-dest side-by-side (measured vs M43-cited) ----
    print("== wipe-vs-dest side-by-side (measured vs M43-cited) ==")
    print(f"M43 cited dest pooled41: med={M43_CITED_STATS['pooled41_med']} "
          f"mean={M43_CITED_STATS['pooled41_mean']} bulk=4/41 "
          f"mm=13/41 m0=28/41 (by reference, not re-attributed)")
    print(f"M43 cited dest pooled37 (731/733): med="
          f"{M43_CITED_STATS['pooled37_med']} bulk=0/37 mm=9/37 "
          f"m0=28/37 (by reference)")
    # dest |d| at-static split from CITED per-site rows (no triplet re-read)
    st_ad, ns_ad = [], []
    for key, rows in M43_CITED_DEST.items():
        for ad, gq, g0c in rows:
            (st_ad if g0c == 0 else ns_ad).append(ad)
    for nm, v in (("static(g0==0)", sorted(st_ad)),
                  ("nonstatic", sorted(ns_ad))):
        a = np.asarray(v, dtype=np.float64)
        print(f"cited-dest ad-{nm}: n={len(v)} list=[{','.join(map(str, v))}] "
              f"med={np.median(a):.1f} mean={a.mean():.4f}")
    for Q in QWIPES:
        d0 = allsets[Q]["d0"]
        mQ = allsets[Q]["maskQ"]
        dQ = allsets[Q]["dQ"]
        vQ, _, fullQ, _ = trips[Q]
        gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
              - np.frombuffer(fullQ, np.uint8).astype(np.int16))
        for c in SHAPES[Q]["wipes"]:
            mi = allsets[Q]["cells"][c]["mi"]
            idx = [int(o) for o in np.nonzero(mi)[0]]
            n = len(idx)
            ads = sorted(int(abs(int(d0[o]))) for o in idx)
            a = np.asarray(ads, dtype=np.float64)
            nbulk = sum(1 for o in idx if mQ[o])
            nmm = sum(1 for o in idx
                      if int(g0[o]) < 0 and int(gQ[o]) < 0)
            nm0 = sum(1 for o in idx if int(gQ[o]) == 0)
            print(f"sbs-wiped s{Q}w{c}: n={n} med={np.median(a):.1f} "
                  f"mean={a.mean():.4f} bulk={nbulk}/{n} "
                  f"s0negQneg={nmm}/{n} Qstatic={nm0}/{n}")

    # ---- determinism re-run (Task 1 on s0+731+733+761, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+731+733+761, second pass) ==")
    v0b, mid0b, full0b, b0b = load_triplet(m16d, 0)
    trips2 = {Q: load_triplet(m16d, Q) for Q in QLIST}
    canon2 = []
    for Q in QLIST:
        vQb, midQb, fullQb, bQb = trips2[Q]
        cols = SHAPES[Q]["wipes"] + SHAPES[Q]["dests"]
        sets2 = compute_sets_for(v0b, mid0b, full0b, b0b, vQb, midQb,
                                 fullQb, bQb, cols)
        cl2, _, _ = task1_lines_for(Q, sets2, v0b, full0b, vQb,
                                    fullQb)
        canon2 += [f"--- shape {Q} ---"] + cl2
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")
    for Q in QLIST:
        print(f"sets identical s{Q}: dest_ex={int(dest_byQ[Q].sum())} "
              f"wipe_mi={int(wipe_byQ[Q].sum())} "
              f"shared={int(allsets[Q]['shared'].sum())}")

    # ---- PNG static-site maps (work dir; evidence copy iff rule meets) ----
    print("== PNG static-site maps ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    for Q in QWIPES:
        vQ, _, fullQ, _ = trips[Q]
        gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
              - np.frombuffer(fullQ, np.uint8).astype(np.int16))
        over = base.copy()
        shared = allsets[Q]["shared"]
        w_st = np.zeros(N, bool)  # wiped static (gQ==0): magenta
        w_ns = np.zeros(N, bool)  # wiped non-static: cyan
        for o in np.nonzero(wipe_byQ[Q])[0]:
            (w_st if int(gQ[int(o)]) == 0 else w_ns)[int(o)] = True
        d_st = np.zeros(N, bool)  # dest static (g0==0): red
        d_ns = np.zeros(N, bool)  # dest non-static: yellow
        for o in np.nonzero(dest_byQ[Q])[0]:
            (d_st if int(g0[int(o)]) == 0 else d_ns)[int(o)] = True
        im_s, _, _ = flat_to_planes(shared)
        im_wst, _, _ = flat_to_planes(w_st)
        im_wns, _, _ = flat_to_planes(w_ns)
        im_dst, _, _ = flat_to_planes(d_st)
        im_dns, _, _ = flat_to_planes(d_ns)
        over[im_s] = np.array([0, 255, 0])        # shared green
        over[im_wns] = np.array([0, 255, 255])    # wiped non-static cyan
        over[im_wst] = np.array([255, 0, 255])    # wiped static magenta
        over[im_dns] = np.array([255, 255, 0])    # dest non-static yellow
        over[im_dst] = np.array([255, 0, 0])      # dest static red
        p = workd / f"m50-staticmap-s{Q:04d}.png"
        Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                      Image.BILINEAR).save(p)
        print(f"png {p}: {p.stat().st_size} B (budget 5242880) "
              f"wipe_st={int(w_st.sum())} wipe_ns={int(w_ns.sum())} "
              f"dest_st={int(d_st.sum())} dest_ns={int(d_ns.sum())} "
              f"shared_n={int(shared.sum())}")
    print("legend: green=shared tail(Y) magenta/cyan=wiped static/nonstatic "
          "(gQ==0?) red/yellow=dest static/nonstatic (g0==0?) "
          "(s0 geometry; Y only; per-site coloring per DESIGN.md)")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    w_n = w_q0 = w_bulk = 0
    w_ads = []
    d_n = d_g0 = 0
    k_n = k_e0 = 0
    fullset_ok = True
    for Q in QWIPES:
        vQ, _, fullQ, _ = trips[Q]
        gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
              - np.frombuffer(fullQ, np.uint8).astype(np.int16))
        d0 = allsets[Q]["d0"]
        mQ = allsets[Q]["maskQ"]
        for o in np.nonzero(wipe_byQ[Q])[0]:
            o = int(o)
            w_n += 1
            w_ads.append(int(abs(int(d0[o]))))
            if int(gQ[o]) == 0:
                w_q0 += 1
            if mQ[o]:
                w_bulk += 1
        for o in np.nonzero(dest_byQ[Q])[0]:
            o = int(o)
            d_n += 1
            if int(g0[o]) == 0:
                d_g0 += 1
        sh = allsets[Q]["shared"]
        for o in np.nonzero(sh)[0]:
            o = int(o)
            k_n += 1
            if int(g0[o]) == 0 or int(gQ[o]) == 0:
                k_e0 += 1
        priv, miss = allsets[Q]["priv"], allsets[Q]["miss"]
        fullset_ok = fullset_ok and bool((priv == dest_byQ[Q]).all())
        fullset_ok = fullset_ok and bool((miss == wipe_byQ[Q]).all())
    w_med = float(np.median(np.asarray(w_ads, dtype=np.float64)))
    print(f"H1_WIPESTATIC: wiped gQ==0 {w_q0}/{w_n} "
          f"({w_q0 / w_n if w_n else 0:.4f}; bar >=0.50)")
    print(f"H2_DESTSTATIC: dest g0==0 {d_g0}/{d_n} "
          f"({d_g0 / d_n if d_n else 0:.4f}; bar >=0.50; "
          f"M43 28/37=0.7568, pooled 28/41)")
    print(f"H3_WIPEBULK: wiped Q-bulk {w_bulk}/{w_n} "
          f"({w_bulk / w_n if w_n else 0:.4f}; bar >=0.50; "
          f"dest-cited 0/37)")
    print(f"H4_FULLSET: priv==dest+miss==wipe both shapes: {fullset_ok} "
          f"(bar: exact)")
    print(f"H5_VALUEMED: wiped med {w_med:.1f} vs cited dest pooled med "
          f"{M43_CITED_STATS['pooled37_med']:.1f} "
          f"differs={w_med != M43_CITED_STATS['pooled37_med']} "
          f"(bar: differs)")
    print(f"H6_KEEPSTATIC: kept either0 {k_e0}/{k_n} "
          f"({k_e0 / k_n if k_n else 0:.4f}; bar >=0.50)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=wiperows+recount+fullset T2=wipedvalues+static R=controls")


if __name__ == "__main__":
    main()
