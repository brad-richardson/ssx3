#!/usr/bin/env python3
"""M36 still-below unnamed cells (2/3/700): per-site value table + joins (offline).

Usage: m36.py M16_DIR M15_DIR M34TXT M34TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m34.txt + m34-census.tsv (2/3/700 unnamed rows to
reproduce: k 6/7/8 + cell lists + standings + deltas); raw XFB dumps,
573440 B = 640x448 YUYV. Read-only inputs; receipt text goes to stdout
(redirect to WORK_DIR/m36.txt); PNG value maps to WORK_DIR
(evidence copy iff the DESIGN.md rule meets, decided at report
time).

Tasks (see DESIGN.md, recorded before running):
  1: per-site value tables (all 21 unnamed cells over 3 shapes, M27-style rows)
  2: joins (s0-anchored band/decile + gap-sign + |d| stats, per shape + pooled)
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
M19_CELL_S0 = 2475  # s2/s3/s700 cell counts unpinned: tabled as measured
M20_TAIL_S0 = 102
M20_TAIL_S0_SUB = (28, 74)  # (8-15, 16+)
M20_TAIL_S0_MAX = 47
M19_POSRATE_S0 = 0.8093  # P(d>0) on s0 cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
M19_REMOVED = [4888, 1208, 649, 448, 248, 244, 191, 174, 190, 202]
M19_REMOVED_BANDS = [[3415, 1442, 31], [824, 384, 0], [186, 463, 0],
                     [0, 0, 448], [0, 0, 248], [0, 0, 244], [0, 0, 191],
                     [0, 0, 174], [0, 0, 190], [0, 187, 15]]
M18_P1_EDGE_S0 = "0 1 2 2 4 6 8 12 18 29 176"
NAMED8 = [257, 277, 296, 301, 321, 340, 342, 343]
NAMED_COLS = [257, 277, 296, 301, 321, 340, 341, 342, 343]  # streak set
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


def attrib_lines(tag, priv, miss, shared, dA, mA, dB, mB,
                 v0A, fullA, v0B, fullB):
    """Task 1.1/1.2: per-site private + missing rows with cross values.

    A = s0, B = other shape (9). priv = T_B - T_A (or the per-cell
    extra subset), miss = T_A - T_B (or the per-cell missing
    subset). Returns (lines, summary_dict). Offsets in ascending
    order. (M27/M33 verbatim.)
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


def posjoin_lines(tag, priv, miss, shared, dec_s0, masks):
    """Task 1.3/2.1: s0-anchored position joins (band/decile/streak/carrier).

    dec_s0: P1 deciles on s0 mid-Y. masks: {shape: removed-Y-bool}.
    Returns lines; sets compared side by side per level.
    (M27/M33 verbatim.)
    """
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    dec_u = dec_s0[:, 0::2]
    sets = (("priv", priv), ("miss", miss), ("shared", shared))

    def band_of(o):
        return int(ROW_BAND[int(pr[o])])

    def dec_of(o):
        r, c = int(pr[o]), int(pc[o])
        if int(pl[o]) == 0:
            return int(dec_s0[r, c])
        return int(dec_u[r, c])  # co-located Y (r,2c): M22 verbatim

    def ycol_of(o):
        if int(pl[o]) == 0:
            return int(pc[o])
        return 2 * int(pc[o])  # co-located Y column

    # planes first (expect all-Y per M22's 0/764 tail-U/V pass)
    for nm, s in sets:
        pp = pl[s]
        L.append(f"{tag} posjoin plane {nm}: Y={int((pp == 0).sum())} "
                 f"U={int((pp == 1).sum())} V={int((pp == 2).sum())} "
                 f"n={int(s.sum())}")
    # band thirds (geometry: same for all frames)
    for bi in range(3):
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            n = sum(1 for o in idx if band_of(o) == bi)
            row.append(f"{nm}={n} ({n / int(s.sum()) if int(s.sum()) else 0:.4f})")
        L.append(f"{tag} posjoin band {bi}: " + " ".join(row))
    # gradient decile (s0-anchored P1)
    for dci in range(10):
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            n = sum(1 for o in idx if dec_of(o) == dci)
            row.append(f"{nm}={n}")
        L.append(f"{tag} posjoin dec {dci}: " + " ".join(row))
    for nm, s in sets:
        idx = np.nonzero(s)[0]
        n9 = sum(1 for o in idx if dec_of(o) == 9)
        L.append(f"{tag} posjoin dec9share {nm}: {n9}/{int(s.sum())} "
                 f"({n9 / int(s.sum()) if int(s.sum()) else 0:.4f})")
    # streak columns (Y-native; U/V via co-located 2c, own row)
    for c in NAMED_COLS + ["other"]:
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            if c == "other":
                n = sum(1 for o in idx if ycol_of(o) not in NAMED_COLS)
            else:
                n = sum(1 for o in idx if ycol_of(o) == c)
            row.append(f"{nm}={n}")
        L.append(f"{tag} posjoin streakcol {c}: " + " ".join(row))
    for nm, s in sets:
        idx = np.nonzero(s)[0]
        nuv = sum(1 for o in idx if int(pl[o]) != 0)
        L.append(f"{tag} posjoin streakcol nonY-co-located {nm}: {nuv}")
    # carrier masks (M22-verbatim removed = res0 & ~ress on Y)
    for rank, shape in enumerate(M16_TOP10, 1):
        rm = masks[shape]
        rm_u = rm[:, 0::2]
        row = []
        for nm, s in sets:
            idx = np.nonzero(s)[0]
            n = 0
            for o in idx:
                r, c = int(pr[o]), int(pc[o])
                inside = rm[r, c] if int(pl[o]) == 0 else rm_u[r, c]
                n += int(bool(inside))
            row.append(f"{nm}_in={n}")
        L.append(f"{tag} posjoin carrier rank{rank}/s{shape}: " + " ".join(row))
    # 701 split
    rm701 = masks[701]
    rm701_u = rm701[:, 0::2]
    for nm, s in sets:
        idx = np.nonzero(s)[0]
        nin = 0
        for o in idx:
            r, c = int(pr[o]), int(pc[o])
            inside = rm701[r, c] if int(pl[o]) == 0 else rm701_u[r, c]
            nin += int(bool(inside))
        L.append(f"{tag} posjoin 701split {nm}: in={nin} "
                 f"out={int(s.sum()) - nin} n={int(s.sum())}")
    return L


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
    """Task 2.3: |d| stats per set (|d_9| on priv, |d_s0| on miss)."""
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


def task1_lines_for(Q, sets, v0, full0, vQ, fullQ, dec, masks,
                      headliner=False):
    """All Task-1 receipt lines for one shape (per-cell + pooled + join)."""
    L = []
    d0, m0 = sets["d0"], sets["mask0"]
    dQ, mQ = sets["dQ"], sets["maskQ"]
    shared = sets["shared"]
    ex_all = np.zeros(N, bool)
    mi_all = np.zeros(N, bool)
    for c in SHAPES[Q]["moved"]:
        ex, mi = sets["cells"][c]["ex"], sets["cells"][c]["mi"]
        ex_all |= ex
        mi_all |= mi
        la, _ = attrib_lines(f"s{Q}c{c}", ex, mi, shared, d0, m0,
                             dQ, mQ, v0, full0, vQ, fullQ)
        L += la
    la_pool, summ = attrib_lines(f"s{Q}pool", ex_all, mi_all, shared,
                                 d0, m0, dQ, mQ, v0, full0, vQ,
                                 fullQ)
    L += la_pool
    if headliner:
        # headliner value stats (all 8 cells of shape 700, c54 split out)
        for c in SHAPES[Q]["moved"]:
            ex, mi = sets["cells"][c]["ex"], sets["cells"][c]["mi"]
            L.append(f"head c{c}: s0rows={sets['cells'][c]['r0']} "
                     f"s{Q}rows={sets['cells'][c]['rQ']} "
                     f"miss_n={int(mi.sum())} extra_n={int(ex.sum())}")
            L += dstats_lines(f"head{c}", ex, mi, dQ, d0)
            L += gapsign_lines(f"head{c}", ex, mi, v0, full0, vQ, fullQ)
    L += posjoin_lines(f"s{Q}all", ex_all, mi_all, shared, dec, masks)
    return L, summ, ex_all, mi_all


def main():
    m16d, m15d, m34t, m34tsv, workd, evidd = (Path(a) for a in sys.argv[1:7])
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
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    for q in (m34t, m34tsv):
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
        print(f"s{Q} cell7 n={sets['spQ']['n']} (unpinned: tabled) "
              f"delta==0 count={int((ddQ == 0).sum())} (want 0)")
        pool_ok = pool_ok and int((ddQ == 0).sum()) == 0
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

    # ---- P1 (s0-anchored) + carrier masks ----
    print("== s0 P1 + carrier masks ==")
    dec, qs, masks, checks = compute_dec_masks(m16d, mid0, b0)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    print(f"s0 P1 edges: {estrs} (m18.txt want {M18_P1_EDGE_S0}) "
          f"match={estrs == M18_P1_EDGE_S0}")
    if estrs != M18_P1_EDGE_S0:
        print("P1 edge MISMATCH: STOP, tabled.")
        return
    for rank, s, nrem, bd, ok in checks:
        print(f"carrier rank {rank} shape {s}: removedYpx={nrem} bands={bd} "
              + ("OK" if ok else "MISMATCH: STOP, tabled"))
        if not ok:
            return

    # ---- Task 1: per-shape per-cell per-site tables + pooled + joins ----
    print("== Task 1 (s2/s3/s700): per-cell per-site tables (21 cells) ==")
    t1 = time.time()
    canon = []
    ex_byQ, mi_byQ = {}, {}
    for Q in QLIST:
        vQ, _, fullQ, _ = trips[Q]
        cl, _, ex_all, mi_all = task1_lines_for(
            Q, allsets[Q], v0, full0, vQ, fullQ, dec, masks,
            headliner=(Q == 700))
        ex_byQ[Q], mi_byQ[Q] = ex_all, mi_all
        canon += [f"--- shape {Q} ---"] + cl
    for ln in canon:
        print(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.1: per-cell joins ----
    print("== Task 2.1 (s2/s3/s700): per-cell s0-anchored joins ==")
    for Q in QLIST:
        shared = allsets[Q]["shared"]
        for c in SHAPES[Q]["moved"]:
            ex = allsets[Q]["cells"][c]["ex"]
            mi = allsets[Q]["cells"][c]["mi"]
            for ln in posjoin_lines(f"s{Q}c{c}join", ex, mi, shared,
                                    dec, masks):
                print(ln)

    # ---- Task 2.2/2.3: gap-sign + |d| stats (per shape + per cell) ----
    print("== Task 2.2/2.3 (s2/s3/s700): gap-sign + |d| stats ==")
    for Q in QLIST:
        vQ, _, fullQ, _ = trips[Q]
        dQ = allsets[Q]["dQ"]
        for ln in gapsign_lines(f"s{Q}pool", ex_byQ[Q], mi_byQ[Q],
                                v0, full0, vQ, fullQ):
            print(ln)
        for ln in dstats_lines(f"s{Q}pool", ex_byQ[Q], mi_byQ[Q],
                               dQ, d0):
            print(ln)
        for c in SHAPES[Q]["moved"]:
            ex = allsets[Q]["cells"][c]["ex"]
            mi = allsets[Q]["cells"][c]["mi"]
            for ln in gapsign_lines(f"s{Q}c{c}", ex, mi, v0, full0,
                                    vQ, fullQ):
                print(ln)
            for ln in dstats_lines(f"s{Q}c{c}", ex, mi, dQ, d0):
                print(ln)

    # ---- determinism re-run (Task 1 on s0+2/3/700, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+2/3/700, second pass) ==")
    v0b, mid0b, full0b, b0b = load_triplet(m16d, 0)
    trips2 = {Q: load_triplet(m16d, Q) for Q in QLIST}
    dec2, _, masks2, _ = compute_dec_masks(m16d, mid0b, b0b)
    canon2 = []
    for Q in QLIST:
        vQb, midQb, fullQb, bQb = trips2[Q]
        sets2 = compute_sets_for(v0b, mid0b, full0b, b0b, vQb, midQb,
                                 fullQb, bQb, SHAPES[Q]["moved"])
        cl2, _, _, _ = task1_lines_for(Q, sets2, v0b, full0b, vQb,
                                       fullQb, dec2, masks2,
                                       headliner=(Q == 700))
        canon2 += [f"--- shape {Q} ---"] + cl2
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")
    for Q in QLIST:
        print(f"sets identical s{Q}: ex={int(ex_byQ[Q].sum())} "
              f"mi={int(mi_byQ[Q].sum())} "
              f"shared={int(allsets[Q]['shared'].sum())}")

    # ---- PNG value maps (work dir; evidence copy iff rule meets) ----
    print("== PNG value maps ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    for Q in QLIST:
        over = base.copy()
        shared = allsets[Q]["shared"]
        maskQ = allsets[Q]["maskQ"]
        im_s, _, _ = flat_to_planes(shared)
        im_eb, _, _ = flat_to_planes(ex_byQ[Q] & mask0)
        im_en, _, _ = flat_to_planes(ex_byQ[Q] & ~mask0)
        im_mb, _, _ = flat_to_planes(mi_byQ[Q] & maskQ)
        im_mn, _, _ = flat_to_planes(mi_byQ[Q] & ~maskQ)
        over[im_s] = np.array([0, 255, 0])        # shared green
        over[im_eb] = np.array([255, 255, 0])     # extra-bulk yellow
        over[im_en] = np.array([255, 0, 0])       # extra-noncell red
        over[im_mb] = np.array([0, 255, 255])     # missing-bulk cyan
        over[im_mn] = np.array([255, 0, 255])     # miss-noncell magenta
        p = workd / f"m36-valuemap-s{Q:04d}.png"
        Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                      Image.BILINEAR).save(p)
        print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: green=shared tail(Y) yellow=extra-bulk "
          "red=extra-noncell cyan=missing-bulk magenta=missing-noncell "
          "(s0 geometry; Y only)")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    g0 = (np.frombuffer(v0, np.uint8).astype(np.int16)
          - np.frombuffer(full0, np.uint8).astype(np.int16))
    # pooled H1/H2/H3/H5 over all 3 shapes (extras vs s0; missings vs own Q)
    p_ex_near = p_ex_non = p_ex_n = 0
    p_mi_non = p_mi_pp = p_mi_n = 0
    p_ex_b1 = p_ex_d9 = 0
    for Q in QLIST:
        vQ, _, fullQ, _ = trips[Q]
        gQ = (np.frombuffer(vQ, np.uint8).astype(np.int16)
              - np.frombuffer(fullQ, np.uint8).astype(np.int16))
        maskQ = allsets[Q]["maskQ"]
        for o in np.nonzero(ex_byQ[Q])[0]:
            o = int(o)
            p_ex_n += 1
            if mask0[o] and int(abs(int(d0[o]))) in (6, 7):
                p_ex_near += 1
            if not mask0[o]:
                p_ex_non += 1
            if int(ROW_BAND[int(pr[o])]) == 1:
                p_ex_b1 += 1
            if int(dec[int(pr[o]), int(pc[o])]) == 9:
                p_ex_d9 += 1
        for o in np.nonzero(mi_byQ[Q])[0]:
            o = int(o)
            p_mi_n += 1
            if not maskQ[o]:
                p_mi_non += 1
            if int(g0[o]) > 0 and int(gQ[o]) > 0:
                p_mi_pp += 1
    print(f"H1_STILLNEAR: near {p_ex_near}/{p_ex_n} "
          f"({p_ex_near / p_ex_n if p_ex_n else 0:.4f}; bar >=0.50)")
    print(f"H2_STILLSET: noncell {p_ex_non}/{p_ex_n} "
          f"({p_ex_non / p_ex_n if p_ex_n else 0:.4f}; bar >=0.50)")
    print(f"H3_STILLMISS: noncell {p_mi_non}/{p_mi_n} "
          f"({p_mi_non / p_mi_n if p_mi_n else 0:.4f}; bar >=0.50)")
    # H4 per shape (extras vs own shared, s0-anchored) + pooled table-only
    h4_any = False
    for Q in QLIST:
        ex_idx = np.nonzero(ex_byQ[Q])[0]
        sh_idx = np.nonzero(allsets[Q]["shared"])[0]
        ex_b1 = sum(1 for o in ex_idx if int(ROW_BAND[int(pr[o])]) == 1)
        sh_b1 = sum(1 for o in sh_idx if int(ROW_BAND[int(pr[o])]) == 1)
        ex_d9 = sum(1 for o in ex_idx
                    if int(dec[int(pr[o]), int(pc[o])]) == 9)
        sh_d9 = sum(1 for o in sh_idx
                    if int(dec[int(pr[o]), int(pc[o])]) == 9)
        nex, nsh = len(ex_idx), len(sh_idx)
        band_leg = abs(ex_b1 / nex - sh_b1 / nsh) if nex and nsh else 0.0
        dec_leg = abs(ex_d9 / nex - sh_d9 / nsh) if nex and nsh else 0.0
        h4_any = h4_any or band_leg >= 0.25 or dec_leg >= 0.25
        print(f"H4_STILLLOCALIZE s{Q}: band-1 extras {ex_b1}/{nex} "
              f"({ex_b1 / nex if nex else 0:.4f}) vs shared {sh_b1}/{nsh} "
              f"({sh_b1 / nsh if nsh else 0:.4f}) |diff|={band_leg:.4f} "
              f"(bar >=0.25); dec-9 extras {ex_d9}/{nex} "
              f"({ex_d9 / nex if nex else 0:.4f}) vs shared {sh_d9}/{nsh} "
              f"({sh_d9 / nsh if nsh else 0:.4f}) |diff|={dec_leg:.4f} "
              f"(bar >=0.25)")
    print(f"H4_STILLLOCALIZE pooled-extra table-only: band-1 "
          f"{p_ex_b1}/{p_ex_n} "
          f"({p_ex_b1 / p_ex_n if p_ex_n else 0:.4f}); dec-9 "
          f"{p_ex_d9}/{p_ex_n} "
          f"({p_ex_d9 / p_ex_n if p_ex_n else 0:.4f}); any-shape={h4_any}")
    print(f"H5_STILLMISSGAP: plusplus {p_mi_pp}/{p_mi_n} "
          f"({p_mi_pp / p_mi_n if p_mi_n else 0:.4f}; bar >=0.50)")
    # H6: shape-700 headliner bulk share (c54 split out)
    mask700 = allsets[700]["maskQ"]
    head_ex = np.nonzero(ex_byQ[700])[0]
    head_mi = np.nonzero(mi_byQ[700])[0]
    head_bulk = (sum(1 for o in head_ex if mask0[o])
                 + sum(1 for o in head_mi if mask700[o]))
    nhead = len(head_ex) + len(head_mi)
    c54_ex = np.nonzero(allsets[700]["cells"][54]["ex"])[0]
    c54_bulk = sum(1 for o in c54_ex if mask0[o])
    print(f"H6_700BULK: headliner bulk {head_bulk}/{nhead} "
          f"({head_bulk / nhead if nhead else 0:.4f}; bar >=0.50); "
          f"c54 extras bulk {c54_bulk}/{len(c54_ex)}")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=per-cell-values T2=joins+gaps+dstats R=controls")


if __name__ == "__main__":
    main()
