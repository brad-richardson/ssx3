#!/usr/bin/env python3
"""M46 shape-9 far/near private split: per-sub-block value/join split (offline).

Usage: m46.py M16_DIR M15_DIR M33TXT M34TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), m33.txt (the 22 dmins + statuses to reproduce) and
m34-census.tsv (FULL TSV guard); raw XFB dumps, 573440 B = 640x448
YUYV. Read-only inputs; receipt text goes to stdout (redirect
to WORK_DIR/m46.txt); PNG sub-block map to WORK_DIR (evidence
copy iff the DESIGN.md rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: displacement reproduction (22 dmins + statuses + mixed-comp membership)
  2: per-sub-block value/join split (far-16 vs near-6 + missing contrast)
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
M19_CELL_S0, M33_CELL_S9 = 2475, 2670
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
M33_TAIL_9, M33_JACC_9 = 117, "0.7520"
M33_PRIV_9, M33_MISS_9, M33_SHARED_9 = 23, 8, 94
M29_INCOL_RC = (266, 321)
S0_C321 = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
S9_MOVED15 = [310, 311, 312, 313, 314, 315, 316, 318, 322, 327, 332,
              336, 337, 339, 351]
M33_CPRIV_SET = {(226, 351), (232, 327), (233, 327), (234, 337),
                 (235, 337), (239, 336), (239, 339), (240, 318),
                 (241, 318), (243, 318), (244, 316), (245, 315),
                 (245, 316), (246, 314), (248, 312), (252, 310),
                 (269, 313), (270, 313), (274, 322), (289, 315),
                 (290, 315), (305, 332)}
M33_CMISS_SET = {(266, 315), (269, 314), (273, 315), (288, 314),
                 (289, 314), (296, 311), (299, 312), (301, 312)}
FAR_DMINS = {(226, 351): 26, (232, 327): 43, (233, 327): 42,
             (234, 337): 48, (235, 337): 49, (239, 336): 45,
             (239, 339): 48, (240, 318): 26, (241, 318): 25,
             (243, 318): 23, (244, 316): 20, (245, 315): 20,
             (245, 316): 19, (246, 314): 20, (248, 312): 20,
             (252, 310): 18}
NEAR_DMINS = {(269, 313): 3, (270, 313): 4, (274, 322): 7,
              (289, 315): 3, (290, 315): 4, (305, 332): 1}
FAR_SET = set(FAR_DMINS)
NEAR_SET = set(NEAR_DMINS)
M33_HIST = {1: 1, 2: 0, 3: 2, 4: 2, 5: 17}  # 5 == 5+
M33_MISSHIST = {1: 6, 2: 2, 3: 0, 4: 0, 5: 0}
FAR_NON = {(226, 351), (239, 339), (252, 310)}
FAR_NEAR = {(239, 336): 6}
NEAR_BULK = {(269, 313): 1, (270, 313): 1}
NEAR_NON = {(274, 322), (289, 315), (290, 315), (305, 332)}
MIXA = {"size": 6, "cpriv": 2, "cmiss": 2,
        "bbox": (266, 270, 313, 315),
        "priv": {(269, 313), (270, 313)},
        "miss": {(266, 315), (269, 314)}}
MIXB = {"size": 5, "cpriv": 2, "cmiss": 2,
        "bbox": (287, 290, 314, 315),
        "priv": {(289, 315), (290, 315)},
        "miss": {(288, 314), (289, 314)}}


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


def connected_components(sites: np.ndarray, conn8: bool):
    """Union-find components of a bool plane; returns sorted size list desc
    plus per-component member coords for components >= 5."""
    h, w = sites.shape
    ys, xs = np.nonzero(sites)
    n = len(ys)
    if n == 0:
        return [], []
    idx = np.full((h, w), -1, np.int32)
    idx[ys, xs] = np.arange(n, dtype=np.int32)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for k in range(n):
        r, c = int(ys[k]), int(xs[k])
        for dr, dc in ((-1, 0), (0, -1), (-1, -1), (-1, 1)):
            if dr == 0 and dc == 0:
                continue
            if not conn8 and dr != 0 and dc != 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and idx[rr, cc] != -1:
                union(k, int(idx[rr, cc]))
    sizes = {}
    members = {}
    for k in range(n):
        rk = find(k)
        sizes[rk] = sizes.get(rk, 0) + 1
        members.setdefault(rk, []).append((int(ys[k]), int(xs[k])))
    sz = sorted(sizes.values(), reverse=True)
    big = []
    for rk, mem in members.items():
        if len(mem) >= 5:
            rs = [p[0] for p in mem]
            cs = [p[1] for p in mem]
            big.append((len(mem), sum(rs) / len(rs), sum(cs) / len(cs),
                        min(rs), max(rs), min(cs), max(cs)))
    big.sort(reverse=True)
    return sz, big


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    inter = int((a & b).sum())
    union = int((a | b).sum())
    if union == 0:
        return 1.0  # both empty: identical (tabled, see receipt)
    return inter / union


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

    A = s0, B = other shape (9). priv = T_B - T_A (or a block
    subset), miss = T_A - T_B (or empty). Returns (lines,
    summary_dict). Offsets in ascending order. (M27/M33 verbatim.)
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
    """Task 2: s0-anchored position joins (band/decile/streak/carrier).

    dec_s0: P1 deciles on s0 mid-Y. masks: {shape: removed-Y-bool}.
    Returns lines; sets compared side by side per level.
    (M27/M33/M35 verbatim.)
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


def displace_lines(tag, priv, miss, shared):
    """Task 1: nearest-shared-site Manhattan distance per private site
    (same plane, plane-native coords, brute-force exact). Missing mirror
    tabled the same way. Returns lines. (M27/M33 verbatim.)
    """
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    for nm, q in (("priv", priv), ("miss", miss)):
        idx = np.nonzero(q)[0]
        dists = []
        for o in idx:
            o = int(o)
            p = int(pl[o])
            qs = np.nonzero(shared & (pl == p))[0]
            if len(qs) == 0:
                L.append(f"{tag} displace {nm} o={o} plane={PNAME[p]} "
                         f"rc=({int(pr[o])},{int(pc[o])}) dmin=n/a "
                         f"(no shared on plane)")
                continue
            d = int((np.abs(pr[qs].astype(np.int32) - int(pr[o]))
                     + np.abs(pc[qs].astype(np.int32) - int(pc[o]))).min())
            assert d >= 1, f"{tag} {nm} o={o}: dmin=0?!"
            dists.append(d)
            L.append(f"{tag} displace {nm} o={o} plane={PNAME[p]} "
                     f"rc=({int(pr[o])},{int(pc[o])}) dmin={d}")
        hist = {b: sum(1 for d in dists if (d == b if b < 5 else d >= 5))
                for b in (1, 2, 3, 4, 5)}
        n = len(dists)
        L.append(f"{tag} displace {nm} hist: "
                 + " ".join(f"{b if b < 5 else '5+'}:{hist[b]}" for b in hist)
                 + f" n={n} d1share={hist[1] / n if n else 0:.4f}")
    return L


def block_dmin_lines(tag, nm, q, shared):
    """Task 1: nearest-shared-site dmin rows + hist for one block
    (same-plane Manhattan core identical to displace_lines)."""
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    idx = np.nonzero(q)[0]
    dists = []
    for o in idx:
        o = int(o)
        p = int(pl[o])
        qs = np.nonzero(shared & (pl == p))[0]
        if len(qs) == 0:
            L.append(f"{tag} displace {nm} o={o} plane={PNAME[p]} "
                     f"rc=({int(pr[o])},{int(pc[o])}) dmin=n/a "
                     f"(no shared on plane)")
            continue
        d = int((np.abs(pr[qs].astype(np.int32) - int(pr[o]))
                 + np.abs(pc[qs].astype(np.int32) - int(pc[o]))).min())
        assert d >= 1, f"{tag} {nm} o={o}: dmin=0?!"
        dists.append(d)
        L.append(f"{tag} displace {nm} o={o} plane={PNAME[p]} "
                 f"rc=({int(pr[o])},{int(pc[o])}) dmin={d}")
    hist = {b: sum(1 for d in dists if (d == b if b < 5 else d >= 5))
            for b in (1, 2, 3, 4, 5)}
    n = len(dists)
    L.append(f"{tag} displace {nm} hist: "
             + " ".join(f"{b if b < 5 else '5+'}:{hist[b]}" for b in hist)
             + f" n={n} d1share={hist[1] / n if n else 0:.4f}")
    return L, {int(pr[o]): None for o in []}  # rows tabled above


def comp_lines(tag, tail, nt):
    """Task 1: 8-conn tail components on Y (M22 verbatim) + U/V counts."""
    L = []
    im_y, im_u, im_v = flat_to_planes(tail)
    sz, big = connected_components(im_y, True)
    nb1 = sum(1 for s in sz if s == 1)
    nb2 = sum(1 for s in sz if s == 2)
    nb34 = sum(1 for s in sz if 3 <= s <= 4)
    nb58 = sum(1 for s in sz if 5 <= s <= 8)
    nb9 = sum(1 for s in sz if s >= 9)
    L.append(f"{tag} comp8 Y: comps={len(sz)} "
             f"sizes[1/2/3-4/5-8/9+]={nb1}/{nb2}/{nb34}/{nb58}/{nb9} "
             f"largest={sz[0] if sz else 0} "
             f"share={sz[0] / nt if sz else 0:.4f} (of tail n={nt})")
    L.append(f"{tag} comp8 Y sizelist: "
             + (" ".join(map(str, sz)) if sz else "(empty)"))
    for (s, cr, cc, r0, r1, c0, c1) in big:
        L.append(f"{tag} comp8 Y comp5+: size={s} "
                 f"centroid=({cr:.1f},{cc:.1f}) bbox=r[{r0},{r1}]c[{c0},{c1}]")
    L.append(f"{tag} comp8 U: n={int(im_u.sum())} V: n={int(im_v.sum())} "
             f"(want 0/0 per M22's 764-shape pass)")
    return L


def off_of(r: int, c: int) -> int:
    """Flat byte offset of Y site (r, c). (M29 verbatim.)"""
    return r * ROWB + (c // 2) * 4 + (0 if c % 2 == 0 else 2)


def y_col_rows(mask: np.ndarray, c: int, pl, pr, pc):
    """Sorted Y-tail rows of mask in column c. (M29 verbatim.)"""
    idx = np.nonzero(mask & (pl == 0) & (pc == c))[0]
    return sorted(int(pr[o]) for o in idx)


def comp_labels(sites: np.ndarray):
    """8-conn union-find labeling (same neighbor set as
    connected_components); returns (label_plane, members) with
    labels 0..K-1 ordered by size desc."""
    h, w = sites.shape
    ys, xs = np.nonzero(sites)
    n = len(ys)
    lab = np.full((h, w), -1, np.int32)
    if n == 0:
        return lab, {}
    idx = np.full((h, w), -1, np.int32)
    idx[ys, xs] = np.arange(n, dtype=np.int32)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for k in range(n):
        r, c = int(ys[k]), int(xs[k])
        for dr, dc in ((-1, 0), (0, -1), (-1, -1), (-1, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and idx[rr, cc] != -1:
                union(k, int(idx[rr, cc]))
    members = {}
    for k in range(n):
        members.setdefault(find(k), []).append((int(ys[k]), int(xs[k])))
    order = sorted(members, key=lambda rk: -len(members[rk]))
    for li, rk in enumerate(order):
        for (r, c) in members[rk]:
            lab[r, c] = li
    return lab, {li: members[rk] for li, rk in enumerate(order)}


def occupancy_lines(tag, tail, cpriv_rc, cmiss_rc=frozenset()):
    """Per-8-conn-comp cluster occupancy on a tail (or union) mask."""
    L = []
    im_y, _, _ = flat_to_planes(tail)
    _, members = comp_labels(im_y)
    cp, cm = set(cpriv_rc), set(cmiss_rc)
    best = 0
    for li in sorted(members):
        mem = members[li]
        ncp = sum(1 for rc in mem if rc in cp)
        ncm = sum(1 for rc in mem if rc in cm)
        best = max(best, ncp)
        rs = [p[0] for p in mem]
        cs = [p[1] for p in mem]
        L.append(f"{tag} comp li={li} size={len(mem)} cpriv={ncp} "
                 f"cmiss={ncm} bbox=r[{min(rs)},{max(rs)}]c[{min(cs)},{max(cs)}]")
    tot_cpriv = sum(1 for mem in members.values()
                    for rc in mem if rc in cp)
    tot_cmiss = sum(1 for mem in members.values()
                    for rc in mem if rc in cm)
    L.append(f"{tag} occupancy: comps={len(members)} "
             f"max-cpriv-in-one={best} cpriv-covered={tot_cpriv} "
             f"cmiss-covered={tot_cmiss}")
    return L, best


def mixed_member_lines(tag, tail, cpriv_rc, cmiss_rc):
    """Per-member (r,c) + priv/miss/shared flags for mixed union comps."""
    L = []
    im_y, _, _ = flat_to_planes(tail)
    _, members = comp_labels(im_y)
    cp, cm = set(cpriv_rc), set(cmiss_rc)
    nmix = 0
    for li in sorted(members):
        mem = members[li]
        ncp = sum(1 for rc in mem if rc in cp)
        ncm = sum(1 for rc in mem if rc in cm)
        if ncp > 0 and ncm > 0:
            nmix += 1
            ps = sorted(rc for rc in mem if rc in cp)
            ms = sorted(rc for rc in mem if rc in cm)
            ss = sorted(rc for rc in mem if rc not in cp and rc not in cm)
            rs = [p[0] for p in mem]
            cs = [p[1] for p in mem]
            L.append(f"{tag} mixed li={li} size={len(mem)} cpriv={ncp} "
                     f"cmiss={ncm} bbox=r[{min(rs)},{max(rs)}]"
                     f"c[{min(cs)},{max(cs)}] priv={ps} miss={ms} "
                     f"shared={ss}")
    L.append(f"{tag} mixed summary: nmix={nmix}")
    return L


def dmin_list(q, shared, pl, pr, pc):
    """Nearest-shared-site Manhattan dmin per site of q (bar math)."""
    out = []
    for o in np.nonzero(q)[0]:
        o = int(o)
        p = int(pl[o])
        qs = np.nonzero(shared & (pl == p))[0]
        if len(qs) == 0:
            out.append(None)
            continue
        out.append(int((np.abs(pr[qs].astype(np.int32) - int(pr[o]))
                        + np.abs(pc[qs].astype(np.int32) - int(pc[o]))).min()))
    return out


def gapsign_lines(tag, priv, miss, v0A, fullA, v0B, fullB):
    """Task 2: signed-gap sign tables (g_Q x g_O per site). (M35 verbatim.)"""
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
    """Task 2: |d| stats per set (|d_9| on priv, |d_s0| on miss).
    (M35 verbatim.)"""
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


def compute_sets(v0, mid0, full0, b0, v9, mid9, full9, b9):
    """Cell-7 + tail + full/cluster/far/near sets for s0+9."""
    sp0 = interior_sites(v0, mid0, full0, b0)
    sp9 = interior_sites(v9, mid9, full9, b9)
    mask0, d0 = sp0["mask"], sp0["delta"]
    mask9, d9 = sp9["mask"], sp9["delta"]
    t0, _ = tail_bulk_masks(mask0, d0)
    t9, _ = tail_bulk_masks(mask9, d9)
    priv = t9 & ~t0
    miss = t0 & ~t9
    shared = t9 & t0
    pl = plane_of_byte()
    pr, pc = plane_coords()
    incol = priv & (pl == 0) & (pc == 321)
    cpriv = priv & ~incol
    far = np.zeros(N, bool)
    near = np.zeros(N, bool)
    for (r, c) in FAR_SET:
        far[off_of(r, c)] = True
    for (r, c) in NEAR_SET:
        near[off_of(r, c)] = True
    return {"sp0": sp0, "sp9": sp9, "mask0": mask0, "d0": d0,
            "mask9": mask9, "d9": d9, "t0": t0, "t9": t9,
            "priv": priv, "miss": miss, "shared": shared,
            "incol": incol, "cpriv": cpriv, "far": far, "near": near,
            "pl": pl, "pr": pr, "pc": pc}


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


def task1_lines(sets, v0, full0, v9, full9):
    """All Task-1 receipt lines (pooled + per-block per-site, dmins,
    union occupancy + mixed membership)."""
    L = []
    far, near = sets["far"], sets["near"]
    empty = np.zeros(N, bool)
    la_pool, _ = attrib_lines("s9clus", sets["cpriv"], sets["miss"],
                             sets["shared"], sets["d0"], sets["mask0"],
                             sets["d9"], sets["mask9"], v0, full0, v9,
                             full9)
    L += la_pool
    la_far, summ_far = attrib_lines("s9far", far, empty,
                                   sets["shared"], sets["d0"],
                                   sets["mask0"], sets["d9"],
                                   sets["mask9"], v0, full0, v9, full9)
    L += la_far
    la_near, summ_near = attrib_lines("s9near", near, empty,
                                     sets["shared"], sets["d0"],
                                     sets["mask0"], sets["d9"],
                                     sets["mask9"], v0, full0, v9, full9)
    L += la_near
    L += displace_lines("s9clus", sets["cpriv"], sets["miss"],
                        sets["shared"])
    Lb_far, _ = block_dmin_lines("s9far", "priv", far, sets["shared"])
    L += Lb_far
    Lb_near, _ = block_dmin_lines("s9near", "priv", near, sets["shared"])
    L += Lb_near
    cpriv_rc = {(int(sets["pr"][o]), int(sets["pc"][o]))
                for o in np.nonzero(sets["cpriv"])[0]}
    cmiss_rc = {(int(sets["pr"][o]), int(sets["pc"][o]))
                for o in np.nonzero(sets["miss"])[0]}
    locc_u, _ = occupancy_lines("union", sets["t9"] | sets["t0"],
                               cpriv_rc, cmiss_rc)
    L += locc_u
    L += mixed_member_lines("union", sets["t9"] | sets["t0"],
                            cpriv_rc, cmiss_rc)
    return L, summ_far, summ_near


def task2_lines(sets, v0, full0, v9, full9, dec, masks):
    """All Task-2 receipt lines (per-block dstats + gapsign + joins,
    missing-contrast joins)."""
    L = []
    far, near = sets["far"], sets["near"]
    empty = np.zeros(N, bool)
    L += dstats_lines("s9far", far, empty, sets["d9"], sets["d0"])
    L += dstats_lines("s9near", near, empty, sets["d9"], sets["d0"])
    L += dstats_lines("s9miss", empty, sets["miss"], sets["d9"],
                      sets["d0"])
    L += gapsign_lines("s9far", far, empty, v0, full0, v9, full9)
    L += gapsign_lines("s9near", near, empty, v0, full0, v9, full9)
    L += gapsign_lines("s9miss", empty, sets["miss"], v0, full0, v9,
                       full9)
    L += posjoin_lines("s9far", far, empty, sets["shared"], dec,
                       masks)
    L += posjoin_lines("s9near", near, empty, sets["shared"], dec,
                       masks)
    L += posjoin_lines("s9missjoin", empty, sets["miss"],
                       sets["shared"], dec, masks)
    return L


def main():
    m16d, m15d, m33t, m34tsv, workd, evidd = (Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin",
              m16d / "m16-v0-s0009.bin", m16d / "m16-mid-s0009.bin",
              m16d / "m16-full-s0009.bin",
              m15d / "m15-v0.bin", m15d / "m15-mid.bin",
              m15d / "m15-full.bin"]
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    for q in (m33t, m34tsv):
        qb = q.read_bytes()
        print(f"input {q}: bytes={len(qb)} "
              f"sha256={hashlib.sha256(qb).hexdigest()}")
    tgt = parse_m33_targets(m33t.read_text(errors="replace"))
    if tgt is None:
        print("m33.txt TARGET ROWS NOT FOUND: STOP, tabled.")
        return
    want_d = dict(FAR_DMINS)
    want_d.update(NEAR_DMINS)
    pin_d = (tgt["dpriv"] == want_d)
    print(f"m33.txt parsed s9clus dmins: priv={len(tgt['dpriv'])} "
          f"miss={len(tgt['dmiss'])} statt={len(tgt['statt'])} "
          f"unioncomps={len(tgt['comps'])}")
    print(f"m33.txt 22 dmins vs DESIGN pins: match={pin_d}")
    # transcription: far/near statuses in m33.txt vs DESIGN pins
    t_far_non = {rc for rc in FAR_SET if tgt["statt"][rc][0] == "noncell"}
    t_far_near = {rc: int(tgt["statt"][rc][1]) for rc in FAR_SET
                  if tgt["statt"][rc][0] == "bulk"
                  and int(tgt["statt"][rc][1]) in (6, 7)}
    t_near_bulk = {rc: int(tgt["statt"][rc][1]) for rc in NEAR_SET
                   if tgt["statt"][rc][0] == "bulk"}
    t_near_non = {rc for rc in NEAR_SET
                  if tgt["statt"][rc][0] == "noncell"}
    t_mix = sorted([(c["size"], c["cpriv"], c["cmiss"], c["bbox"])
                    for c in tgt["comps"] if c["cpriv"] > 0 and c["cmiss"] > 0])
    want_mix = sorted([(MIXA["size"], MIXA["cpriv"], MIXA["cmiss"],
                        MIXA["bbox"]),
                       (MIXB["size"], MIXB["cpriv"], MIXB["cmiss"],
                        MIXB["bbox"])])
    pin_s = (t_far_non == FAR_NON and t_far_near == FAR_NEAR
             and t_near_bulk == NEAR_BULK and t_near_non == NEAR_NON
             and t_mix == want_mix)
    print(f"m33.txt far statuses: non={sorted(t_far_non)} "
          f"near={t_far_near} (want non={sorted(FAR_NON)} "
          f"near={FAR_NEAR})")
    print(f"m33.txt near statuses: bulk={t_near_bulk} "
          f"non={sorted(t_near_non)} (want bulk={NEAR_BULK} "
          f"non={sorted(NEAR_NON)})")
    print(f"m33.txt mixed union comps: {t_mix} (want {want_mix})")
    print(f"m33.txt statuses+comps vs DESIGN pins: match={pin_s}")
    if not (pin_d and pin_s):
        print("m33.txt vs DESIGN TRANSCRIPTION MISMATCH: STOP, tabled.")
        return

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
    v9, mid9, full9, b9 = load_triplet(m16d, 9)
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M45 baselines: STOP, tabled.")
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
    print(f"fold vs M28/M34/M35 want: match={fold == M34_FOLD}")
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

    # ---- FULL unnamed TSV guard (M34/M35 match or stop) ----
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
    print("TSV guard: " + ("OK" if tsv_ok else
                           "MISMATCH vs M34: STOP, tabled."))
    if not tsv_ok:
        return

    # ---- s9 row guard ----
    print("== shape-9 row guard ==")
    r9 = per[9]
    print(f"s9 tail={r9['tail']} (want {M33_TAIL_9}) "
          f"J={r9['j']:.4f} (want {M33_JACC_9})")
    print(f"s9 umoved={r9['umoved']} (want {S9_MOVED15})")
    row_ok = (r9["tail"] == M33_TAIL_9
              and f"{r9['j']:.4f}" == M33_JACC_9
              and r9["umoved"] == S9_MOVED15)
    print("shape-9 row guard: " + ("OK" if row_ok else
                                   "MISMATCH vs M33/M34: STOP, tabled."))
    if not row_ok:
        return

    # ---- s0+9 sets + M33 cluster-set guard + far/near partition ----
    print("== s0+9 sets + M33 cluster-set guard ==")
    sets = compute_sets(v0, mid0, full0, b0, v9, mid9, full9, b9)
    mask9, d9 = sets["mask9"], sets["d9"]
    t9 = sets["t9"]
    priv, miss, shared = sets["priv"], sets["miss"], sets["shared"]
    cpriv, incol = sets["cpriv"], sets["incol"]
    far, near = sets["far"], sets["near"]
    print(f"s9 cell7 n={sets['sp9']['n']} (want {M33_CELL_S9})")
    dd9 = d9[mask9]
    print(f"s9 delta==0 count={int((dd9 == 0).sum())} (want 0)")
    npriv, nmiss, nshared = (int(priv.sum()), int(miss.sum()),
                             int(shared.sum()))
    print(f"s9 full sets: priv={npriv} (want {M33_PRIV_9}) "
          f"miss={nmiss} (want {M33_MISS_9}) "
          f"shared={nshared} (want {M33_SHARED_9})")
    incol_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(incol)[0]}
    cpriv_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(cpriv)[0]}
    cmiss_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(miss)[0]}
    far_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(far)[0]}
    near_rc = {(int(pr[o]), int(pc[o])) for o in np.nonzero(near)[0]}
    print(f"s9 in-c321 priv rc={sorted(incol_rc)} (want [{M29_INCOL_RC}])")
    print(f"cluster priv: n={len(cpriv_rc)} (want 22) ==M33: "
          f"{cpriv_rc == M33_CPRIV_SET}")
    print(f"cluster miss: n={len(cmiss_rc)} (want 8) ==M33: "
          f"{cmiss_rc == M33_CMISS_SET}")
    print(f"far block: n={len(far_rc)} (want 16) "
          f"near block: n={len(near_rc)} (want 6) "
          f"partition={far_rc == FAR_SET and near_rc == NEAR_SET} "
          f"disjoint={not (far_rc & near_rc)} "
          f"union==cpriv={(far_rc | near_rc) == cpriv_rc}")
    rows9_c321 = y_col_rows(t9, 321, pl, pr, pc)
    c321_ok = rows9_c321 == S0_C321 + [266]
    print(f"s9 c321 rows: n={len(rows9_c321)} match=s0-rows+[266] -> {c321_ok}")
    clus_ok = (sets["sp9"]["n"] == M33_CELL_S9
               and int((dd9 == 0).sum()) == 0
               and npriv == M33_PRIV_9 and nmiss == M33_MISS_9
               and nshared == M33_SHARED_9
               and incol_rc == {M29_INCOL_RC}
               and cpriv_rc == M33_CPRIV_SET
               and cmiss_rc == M33_CMISS_SET
               and far_rc == FAR_SET and near_rc == NEAR_SET
               and (far_rc | near_rc) == cpriv_rc and c321_ok)
    print("M33 cluster-set guard: "
          + ("OK" if clus_ok else "MISMATCH vs M33: STOP, tabled."))
    if not clus_ok:
        print(f"cpriv rc sorted={sorted(cpriv_rc)}")
        print(f"cmiss rc sorted={sorted(cmiss_rc)}")
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

    # ---- Task 1: pooled + per-block per-site + dmins + comps ----
    print("== Task 1 (s9): far/near per-site tables + dmins + comps ==")
    t1 = time.time()
    canon, summ_far, summ_near = task1_lines(sets, v0, full0, v9, full9)
    for ln in canon:
        print(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task-1 guards: 22 dmins + statuses + mixed comps ----
    print("== Task-1 guards (dmin + status + comp reproduction) ==")
    d_all = {}
    for o in np.nonzero(cpriv)[0]:
        o = int(o)
        p = int(pl[o])
        qs0 = np.nonzero(shared & (pl == p))[0]
        d_all[(int(pr[o]), int(pc[o]))] = int(
            (np.abs(pr[qs0].astype(np.int32) - int(pr[o]))
             + np.abs(pc[qs0].astype(np.int32) - int(pc[o]))).min())
    d_ok = all(d_all.get(rc) == want_d.get(rc) for rc in want_d) \
        and set(d_all) == set(want_d)
    hist = {b: sum(1 for d in d_all.values() if (d == b if b < 5 else d >= 5))
            for b in (1, 2, 3, 4, 5)}
    hist_ok = hist == M33_HIST
    print(f"22 dmins exact: {d_ok} (far16={all(d_all.get(rc) == FAR_DMINS.get(rc) for rc in FAR_SET)} "
          f"near6={all(d_all.get(rc) == NEAR_DMINS.get(rc) for rc in NEAR_SET)})")
    print(f"hist 1:{hist[1]} 2:{hist[2]} 3:{hist[3]} 4:{hist[4]} 5+:{hist[5]} "
          f"(want 1:{M33_HIST[1]} 2:{M33_HIST[2]} 3:{M33_HIST[3]} "
          f"4:{M33_HIST[4]} 5+:{M33_HIST[5]}) match={hist_ok}")
    if not (d_ok and hist_ok):
        print(f"recomputed dmins: {sorted(d_all.items())}")
        print("DMIN MISMATCH: STOP, tabled.")
        return
    d_miss = {}
    for o in np.nonzero(miss)[0]:
        o = int(o)
        p = int(pl[o])
        qs0 = np.nonzero(shared & (pl == p))[0]
        d_miss[(int(pr[o]), int(pc[o]))] = int(
            (np.abs(pr[qs0].astype(np.int32) - int(pr[o]))
             + np.abs(pc[qs0].astype(np.int32) - int(pc[o]))).min())
    mhist = {b: sum(1 for d in d_miss.values() if (d == b if b < 5 else d >= 5))
             for b in (1, 2, 3, 4, 5)}
    print(f"miss dmins == m33.txt parse: {d_miss == tgt['dmiss']} "
          f"hist 1:{mhist[1]} 2:{mhist[2]} (want 1:6 2:2) "
          f"match={mhist == M33_MISSHIST}")
    if d_miss != tgt["dmiss"] or mhist != M33_MISSHIST:
        print("MISS-DMIN MISMATCH: STOP, tabled.")
        return
    # per-site statuses recomputed vs pins
    r_far_non, r_far_near, r_far_rest = set(), {}, set()
    for o in np.nonzero(far)[0]:
        o = int(o)
        rc = (int(pr[o]), int(pc[o]))
        if not mask0[o]:
            r_far_non.add(rc)
        else:
            ad = int(abs(int(d0[o])))
            if ad in (6, 7):
                r_far_near[rc] = ad
            else:
                r_far_rest.add(rc)
    r_near_bulk, r_near_non = {}, set()
    for o in np.nonzero(near)[0]:
        o = int(o)
        rc = (int(pr[o]), int(pc[o]))
        if not mask0[o]:
            r_near_non.add(rc)
        else:
            r_near_bulk[rc] = int(abs(int(d0[o])))
    stat_ok = (r_far_non == FAR_NON and r_far_near == FAR_NEAR
               and r_near_bulk == NEAR_BULK and r_near_non == NEAR_NON)
    print(f"far statuses: far={len(r_far_rest)}/16 near={r_far_near} "
          f"non={sorted(r_far_non)} (want 12/1/3) "
          f"summ={summ_far['priv']}")
    print(f"near statuses: bulk={r_near_bulk} non={sorted(r_near_non)} "
          f"(want 2 bulk / 4 non) summ={summ_near['priv']}")
    print(f"status reproduction: match={stat_ok}")
    if not stat_ok:
        print("STATUS MISMATCH: STOP, tabled.")
        return
    # mixed union comps recomputed vs pins
    _, members = comp_labels(flat_to_planes(t9 | t0)[0])
    cp, cm = cpriv_rc, cmiss_rc
    found = []
    for li in sorted(members):
        mem = members[li]
        ncp = sum(1 for rc in mem if rc in cp)
        ncm = sum(1 for rc in mem if rc in cm)
        if ncp > 0 and ncm > 0:
            rs = [p[0] for p in mem]
            cs = [p[1] for p in mem]
            found.append({"size": len(mem), "cpriv": ncp, "cmiss": ncm,
                          "bbox": (min(rs), max(rs), min(cs), max(cs)),
                          "priv": {rc for rc in mem if rc in cp},
                          "miss": {rc for rc in mem if rc in cm}})
    want_m = [{"size": MIXA["size"], "cpriv": MIXA["cpriv"],
               "cmiss": MIXA["cmiss"], "bbox": MIXA["bbox"],
               "priv": MIXA["priv"], "miss": MIXA["miss"]},
              {"size": MIXB["size"], "cpriv": MIXB["cpriv"],
               "cmiss": MIXB["cmiss"], "bbox": MIXB["bbox"],
               "priv": MIXB["priv"], "miss": MIXB["miss"]}]
    comp_ok = (len(found) == 2 and all(f in want_m for f in found))
    print(f"mixed union comps: n={len(found)} (want 2) match={comp_ok}")
    for f in found:
        print(f"  mixed size={f['size']} cpriv={f['cpriv']} "
              f"cmiss={f['cmiss']} bbox=r[{f['bbox'][0]},{f['bbox'][1]}]"
              f"c[{f['bbox'][2]},{f['bbox'][3]}] priv={sorted(f['priv'])} "
              f"miss={sorted(f['miss'])}")
    if not comp_ok:
        print("COMP-MEMBERSHIP MISMATCH: STOP, tabled.")
        return
    print("Task-1 guards: OK")

    # ---- Task 2: per-block values + joins + missing contrast ----
    print("== Task 2 (s9): per-block values + joins + missing contrast ==")
    t2 = time.time()
    t2lines = task2_lines(sets, v0, full0, v9, full9, dec, masks)
    for ln in t2lines:
        print(ln)
    print(f"(Task-2 wall: {time.time() - t2:.1f}s)")

    # ---- determinism re-run (Task 1 on s0+9, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+9, second pass) ==")
    v0b, mid0b, full0b, b0b = load_triplet(m16d, 0)
    v9b, mid9b, full9b, b9b = load_triplet(m16d, 9)
    sets2 = compute_sets(v0b, mid0b, full0b, b0b, v9b, mid9b, full9b, b9b)
    canon2, _, _ = task1_lines(sets2, v0b, full0b, v9b, full9b)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")
    print(f"sets identical: priv={int(sets2['priv'].sum())} "
          f"cpriv={int(sets2['cpriv'].sum())} "
          f"far={int(sets2['far'].sum())} "
          f"near={int(sets2['near'].sum())} "
          f"miss={int(sets2['miss'].sum())} "
          f"shared={int(sets2['shared'].sum())}")

    # ---- PNG sub-block map (work dir; evidence copy iff rule meets) ----
    print("== PNG sub-block map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    im_f, _, _ = flat_to_planes(far)
    im_q, _, _ = flat_to_planes(near)
    im_m, _, _ = flat_to_planes(miss)
    im_s, _, _ = flat_to_planes(shared)
    im_i, _, _ = flat_to_planes(incol)
    over[im_s] = np.array([0, 255, 0])        # shared green
    over[im_f] = np.array([255, 255, 0])      # far-block yellow
    over[im_q] = np.array([255, 165, 0])      # near-block orange
    over[im_m] = np.array([255, 0, 255])      # cluster-miss magenta
    over[im_i] = np.array([255, 0, 0])        # in-column priv red
    p = workd / "m46-splitmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: green=shared tail(Y) yellow=far-block(16) "
          "orange=near-block(6) magenta=cluster-miss(8) "
          "red=in-column priv r266 (s0 geometry; Y only)")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    far_idx = np.nonzero(far)[0]
    near_idx = np.nonzero(near)[0]
    miss_idx = np.nonzero(miss)[0]
    far_bulk = sum(1 for o in far_idx if mask0[o])
    near_bulk = sum(1 for o in near_idx if mask0[o])
    miss_bulk = sum(1 for o in miss_idx if mask9[o])
    a0 = np.frombuffer(v0, np.uint8).astype(np.int16)
    f0a = np.frombuffer(full0, np.uint8).astype(np.int16)
    a9 = np.frombuffer(v9, np.uint8).astype(np.int16)
    f9a = np.frombuffer(full9, np.uint8).astype(np.int16)
    g0, g9 = a0 - f0a, a9 - f9a
    far_pp = sum(1 for o in far_idx if int(g9[o]) > 0 and int(g0[o]) > 0)
    near_pp = sum(1 for o in near_idx if int(g9[o]) > 0 and int(g0[o]) > 0)
    far_b1 = sum(1 for o in far_idx if int(ROW_BAND[int(pr[o])]) == 1)
    near_b1 = sum(1 for o in near_idx if int(ROW_BAND[int(pr[o])]) == 1)
    far_d9 = sum(1 for o in far_idx
                 if int(dec[int(pr[o]), int(pc[o])]) == 9)
    near_d9 = sum(1 for o in near_idx
                  if int(dec[int(pr[o]), int(pc[o])]) == 9)
    far_med = float(np.median(np.abs(d9[far].astype(np.float64))))
    near_med = float(np.median(np.abs(d9[near].astype(np.float64))))
    nf, nq, nm = len(far_idx), len(near_idx), len(miss_idx)
    lab, members2 = comp_labels(flat_to_planes(t9 | t0)[0])
    near_mixed = 0
    for (r, c) in near_rc:
        li = int(lab[r, c])
        mem = members2[li]
        ncp = sum(1 for rc in mem if rc in cp)
        ncm = sum(1 for rc in mem if rc in cm)
        near_mixed += int(ncp > 0 and ncm > 0)
    h1v = abs(far_bulk / nf - near_bulk / nq)
    h2v = abs(far_pp / nf - near_pp / nq)
    h3b = abs(far_b1 / nf - near_b1 / nq)
    h3d = abs(far_d9 / nf - near_d9 / nq)
    h4v = abs(near_bulk / nq - miss_bulk / nm)
    h5v = abs(far_med - near_med)
    print(f"H1_FARNEAR_BULK: far-bulk {far_bulk}/{nf} "
          f"({far_bulk / nf:.4f}) vs near-bulk {near_bulk}/{nq} "
          f"({near_bulk / nq:.4f}) |diff|={h1v:.4f} (bar >=0.25)")
    print(f"H2_FARNEAR_GAP: far-++ {far_pp}/{nf} "
          f"({far_pp / nf:.4f}) vs near-++ {near_pp}/{nq} "
          f"({near_pp / nq:.4f}) |diff|={h2v:.4f} (bar >=0.25)")
    print(f"H3_FARNEAR_SEAT: band-1 far {far_b1}/{nf} "
          f"({far_b1 / nf:.4f}) vs near {near_b1}/{nq} "
          f"({near_b1 / nq:.4f}) |diff|={h3b:.4f} (bar >=0.25); "
          f"dec-9 far {far_d9}/{nf} ({far_d9 / nf:.4f}) vs near "
          f"{near_d9}/{nq} ({near_d9 / nq:.4f}) |diff|={h3d:.4f} "
          f"(bar >=0.25)")
    print(f"H4_NEARMISS: near-bulk {near_bulk}/{nq} "
          f"({near_bulk / nq:.4f}) vs miss-bulk {miss_bulk}/{nm} "
          f"({miss_bulk / nm:.4f}) |diff|={h4v:.4f} (bar <0.25)")
    print(f"H5_FARNEAR_MED: far-med {far_med:.1f} vs near-med "
          f"{near_med:.1f} |diff|={h5v:.1f} (bar >=4)")
    print(f"H6_NEARMIX: near-in-mixed {near_mixed}/{nq} "
          f"({near_mixed / nq if nq else 0:.4f}; bar >=0.50)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=displacement T2=block-split R=controls")


def parse_m33_targets(txt: str):
    """Cluster dmin + status + union-comp match targets from m33.txt."""
    dpriv, dmiss, statt = {}, {}, {}
    for m in re.finditer(r"^s9clus displace priv o=(\d+) plane=(\S+) "
                         r"rc=\((\d+),(\d+)\) dmin=(\d+)", txt, re.M):
        dpriv[(int(m.group(3)), int(m.group(4)))] = int(m.group(5))
    for m in re.finditer(r"^s9clus displace miss o=(\d+) plane=(\S+) "
                         r"rc=\((\d+),(\d+)\) dmin=(\d+)", txt, re.M):
        dmiss[(int(m.group(3)), int(m.group(4)))] = int(m.group(5))
    for m in re.finditer(r"^s9clus priv o=(\d+) plane=(\S+) "
                         r"rc=\((\d+),(\d+)\) adQ=(\d+) ostat=(\S+) "
                         r"adO=(\S+) gQ=(-?\d+) gO=(-?\d+)", txt, re.M):
        statt[(int(m.group(3)), int(m.group(4)))] = (
            m.group(6), m.group(7), int(m.group(5)),
            int(m.group(8)), int(m.group(9)))
    comps = []
    for m in re.finditer(r"^union comp li=(\d+) size=(\d+) cpriv=(\d+) "
                         r"cmiss=(\d+) bbox=r\[(\d+),(\d+)\]"
                         r"c\[(\d+),(\d+)\]", txt, re.M):
        comps.append({"li": int(m.group(1)), "size": int(m.group(2)),
                      "cpriv": int(m.group(3)),
                      "cmiss": int(m.group(4)),
                      "bbox": (int(m.group(5)), int(m.group(6)),
                               int(m.group(7)), int(m.group(8)))})
    if len(dpriv) != 22 or len(dmiss) != 8 or len(statt) != 22 \
            or not comps:
        return None
    return {"dpriv": dpriv, "dmiss": dmiss, "statt": statt,
            "comps": comps}


if __name__ == "__main__":
    main()
