#!/usr/bin/env python3
"""M27 shape-733 tail divergence: per-byte attribution of private sites (offline).

Usage: m27.py M16_DIR M15_DIR M22TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m22.txt (733's 100 B + Jaccard 0.6694 match target);
raw XFB dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt
text goes to stdout (redirect to WORK_DIR/m27.txt); PNG private-site
map to WORK_DIR (evidence copy iff the DESIGN.md rule meets, decided
at report time).

Tasks (see DESIGN.md, recorded before running):
  1: private/missing per-site tables + s0-anchored position joins
  2: displacement distances + components + 731 cross-check
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
M19_INTERIOR = {"s0": 2475, "m15": 2539}
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
M22_TAIL_733, M22_JACC_733 = 100, "0.6694"
M22_TAIL_731, M22_JACC_731 = 100, "0.6833"
NAMED_COLS = [257, 277, 296, 301, 321, 340, 341, 342, 343]
H5_COLS = [257, 277, 296, 301, 321, 340]


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


def mag_hist(d: np.ndarray):
    nz = d[d > 0]
    return [int(((nz >= lo) & (nz < hi)).sum())
            for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 1 << 15))]


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


def dist4(x):
    a = np.asarray(x, dtype=np.float64)
    return (float(a.min()), float(np.median(a)), float(a.mean()),
            float(a.max()))


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    inter = int((a & b).sum())
    union = int((a | b).sum())
    if union == 0:
        return 1.0  # both empty: identical (tabled, see receipt)
    return inter / union


PNAME = ("Y", "U", "V")


def attrib_lines(tag, priv, miss, shared, dA, mA, dB, mB,
                 v0A, fullA, v0B, fullB):
    """Task 1.1/1.2: per-site private + missing rows with cross values.

    A = s0, B = other shape (733/731). priv = T_B - T_A, miss = T_A - T_B.
    Returns (lines, summary_dict). Offsets in ascending order.
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
    """Task 1.3: s0-anchored position joins (band/decile/streak/carrier).

    dec_s0: P1 deciles on s0 mid-Y. masks: {shape: removed-Y-bool}.
    Returns lines; sets compared side by side per level.
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
    """Task 2.1: nearest-shared-site Manhattan distance per private site
    (same plane, plane-native coords, brute-force exact). Missing mirror
    tabled the same way. Returns lines."""
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


def comp_lines(tag, tail, nt):
    """Task 2.2: 8-conn tail components on Y (M22 verbatim) + U/V counts."""
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


def streak_presence_lines(tailA, tailB, labA="s0", labB="s733"):
    """Task 2.2 streak view: per named column (n, rows, row-overlap)."""
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    rowsA, rowsB = {}, {}
    for c in NAMED_COLS:
        sa = sorted(int(pr[o]) for o in np.nonzero(
            tailA & (pl == 0) & (pc == c))[0])
        sb = sorted(int(pr[o]) for o in np.nonzero(
            tailB & (pl == 0) & (pc == c))[0])
        rowsA[c], rowsB[c] = sa, sb
        ov = sorted(set(sa) & set(sb))
        L.append(f"streak col {c}: {labA} n={len(sa)} "
                 f"rows={'-'.join(map(str, (min(sa), max(sa)))) if sa else '-'} "
                 f"{labB} n={len(sb)} "
                 f"rows={'-'.join(map(str, (min(sb), max(sb)))) if sb else '-'} "
                 f"overlap={len(ov)}")
        L.append(f"streak col {c} rowlists: {labA}=[{','.join(map(str, sa))}] "
                 f"{labB}=[{','.join(map(str, sb))}]")
    npresent = 0
    for c in H5_COLS:
        present = len(rowsB[c]) >= 8 and len(set(rowsA[c]) & set(rowsB[c])) >= 5
        npresent += int(present)
        L.append(f"streak H5 col {c}: present={present} "
                 f"(n{labB}={len(rowsB[c])}>=8, "
                 f"overlap={len(set(rowsA[c]) & set(rowsB[c]))}>=5)")
    L.append(f"streak H5: {npresent}/{len(H5_COLS)} present (want>=4 for H5)")
    return L, npresent


def main():
    m16d, m15d, m22t, workd, evidd = (Path(a) for a in sys.argv[1:6])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0+733)

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin",
              m16d / "m16-v0-s0733.bin", m16d / "m16-mid-s0733.bin",
              m16d / "m16-full-s0733.bin",
              m16d / "m16-v0-s0731.bin", m16d / "m16-mid-s0731.bin",
              m16d / "m16-full-s0731.bin",
              m15d / "m15-v0.bin", m15d / "m15-mid.bin",
              m15d / "m15-full.bin"]
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    m22b = m22t.read_bytes()
    print(f"input {m22t}: bytes={len(m22b)} "
          f"sha256={hashlib.sha256(m22b).hexdigest()}")
    for shp in (733, 731):
        hit = [ln for ln in m22b.decode(errors="replace").splitlines()
               if ln.startswith(f"| {shp} |")]
        print(f"m22.txt target row s{shp}: "
              + (hit[0] if hit else "(NOT FOUND)"))

    print("== loo.txt + top-10 carriers ==")
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
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid0 = load_dump(m16d / "m16-mid-s0000.bin")
    full0 = load_dump(m16d / "m16-full-s0000.bin")
    ym0 = split_planes(np.frombuffer(mid0, np.uint8))[0]
    b0 = synth_w_bytes(v0, full0, 0.5)
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M26 baselines: STOP, tabled.")
        return
    if not carriers_ok:
        print("carrier mismatch: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    # R_s vs loo on s0/733/731 (M22 precedent: want all equal)
    print("== R_s vs loo cross-check (s0/733/731) ==")
    trips = {}
    for s in (0, 733, 731):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        xd = xdiff(bl, mm)[0]
        rs = loo.get(s, ("?", "?"))[1]
        print(f"s{s}: R_s={xd} R_loo={rs} match={xd == rs}")
        if xd != rs:
            print(f"R_s mismatch on s{s}: STOP, tabled.")
            return
        trips[s] = (vv, mm, ff, bl)
    print("R_s cross-check: OK")

    # cell-7 + tail on s0 + 733
    print("== cell-7 + tail (s0 + 733) ==")
    sp0 = interior_sites(*trips[0])
    sp733 = interior_sites(*trips[733])
    mask0, d0, n0 = sp0["mask"], sp0["delta"], sp0["n"]
    mask733, d733 = sp733["mask"], sp733["delta"]
    print(f"s0 cell7 n={n0} (want {M19_INTERIOR['s0']})")
    if n0 != M19_INTERIOR["s0"]:
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
    t733, _ = tail_bulk_masks(mask733, d733)
    nt0, nt733 = int(t0.sum()), int(t733.sum())
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
    j733 = jaccard(t733, t0)
    print(f"s733 tail n={nt733} (M22 want {M22_TAIL_733}); "
          f"J(T_733,T_s0)={j733:.4f} (M22 want {M22_JACC_733}); "
          f"inter={int((t733 & t0).sum())} union={int((t733 | t0).sum())}")
    if nt733 != M22_TAIL_733 or f"{j733:.4f}" != M22_JACC_733:
        print("733 TAIL/JACCARD MISMATCH vs M22: STOP, tabled.")
        return
    print(f"self Jaccard={jaccard(t0, t0):.4f} (want 1.0000)")
    print("count/J guard: OK")

    p733 = t733 & ~t0
    m733 = t0 & ~t733
    s733 = t733 & t0
    print(f"733 sets: priv={int(p733.sum())} miss={int(m733.sum())} "
          f"shared={int(s733.sum())}")

    # P1 (s0-anchored) + carrier masks (M22 verbatim)
    mag, qs, dec = p1_gradient(ym0)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    print(f"s0 P1 edges: {estrs} (m18.txt want {M18_P1_EDGE_S0}) "
          f"match={estrs == M18_P1_EDGE_S0}")
    if estrs != M18_P1_EDGE_S0:
        print("P1 edge MISMATCH: STOP, tabled.")
        return
    sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
    res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
    masks = {}
    for rank, s in enumerate(M16_TOP10, 1):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        yb = split_planes(np.frombuffer(bl, np.uint8))[0]
        yms = split_planes(np.frombuffer(mm, np.uint8))[0]
        ress = yb.astype(np.int16) != yms.astype(np.int16)
        removed = res0 & ~ress
        masks[s] = removed
        nrem = int(removed.sum())
        bd = bands_of(removed.astype(np.int64))
        ok = nrem == M19_REMOVED[rank - 1] and bd == M19_REMOVED_BANDS[rank - 1]
        print(f"carrier rank {rank} shape {s}: removedYpx={nrem} bands={bd} "
              + ("OK" if ok else "MISMATCH: STOP, tabled"))
        if not ok:
            return

    # ---- Task 1 (733): per-site tables + position joins ----
    print("== Task 1 (733): private/missing per-site tables ==")
    t1 = time.time()
    la, summ733 = attrib_lines("s733", p733, m733, s733, d0, mask0, d733,
                              mask733, v0, full0, trips[733][0], trips[733][2])
    for ln in la:
        print(ln)
        canon.append(ln)
    print("== Task 1 (733): s0-anchored position joins ==")
    lj = posjoin_lines("s733", p733, m733, s733, dec, masks)
    for ln in lj:
        print(ln)
        canon.append(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.1 (733): displacement ----
    print("== Task 2.1 (733): nearest-shared displacement ==")
    for ln in displace_lines("s733", p733, m733, s733):
        print(ln)

    # ---- Task 2.2: components s0 vs 733 + streak presence ----
    print("== Task 2.2: 8-conn components s0 vs s733 ==")
    for ln in comp_lines("s0", t0, nt0):
        print(ln)
    for ln in comp_lines("s733", t733, nt733):
        print(ln)
    print("== Task 2.2: streak-column presence ==")
    ls, npresent = streak_presence_lines(t0, t733)
    for ln in ls:
        print(ln)

    # ---- Task 2.3: 731 cross-check ----
    print("== Task 2.3: 731 cross-check ==")
    sp731 = interior_sites(*trips[731])
    mask731, d731 = sp731["mask"], sp731["delta"]
    t731, _ = tail_bulk_masks(mask731, d731)
    nt731 = int(t731.sum())
    j731 = jaccard(t731, t0)
    print(f"s731 tail n={nt731} (M22 want {M22_TAIL_731}); "
          f"J(T_731,T_s0)={j731:.4f} (M22 want {M22_JACC_731}); "
          f"inter={int((t731 & t0).sum())} union={int((t731 | t0).sum())}")
    if nt731 != M22_TAIL_731 or f"{j731:.4f}" != M22_JACC_731:
        print("731 TAIL/JACCARD MISMATCH vs M22: cross-check stopped, "
              "Tasks 1-2.2 stand.")
    else:
        p731 = t731 & ~t0
        m731 = t0 & ~t731
        s731 = t731 & t0
        print(f"731 sets: priv={int(p731.sum())} miss={int(m731.sum())} "
              f"shared={int(s731.sum())}")
        la2, summ731 = attrib_lines("s731", p731, m731, s731, d0, mask0,
                                   d731, mask731, v0, full0,
                                   trips[731][0], trips[731][2])
        for ln in la2:
            print(ln)
        for ln in posjoin_lines("s731", p731, m731, s731, dec, masks):
            print(ln)
        for ln in displace_lines("s731", p731, m731, s731):
            print(ln)
        jp = jaccard(p733, p731)
        jm = jaccard(m733, m731)
        print(f"set overlap J(P_733,P_731)={jp:.4f} "
              f"inter={int((p733 & p731).sum())} "
              f"union={int((p733 | p731).sum())} (H6 want>=0.50)")
        print(f"set overlap J(M_733,M_731)={jm:.4f} "
              f"inter={int((m733 & m731).sum())} "
              f"union={int((m733 | m731).sum())}")

    # ---- determinism re-run (Task 1 on s0+733, canonical text) ----
    print("== determinism re-run (Task 1 on s0+733, second pass) ==")
    la_b, _ = attrib_lines("s733", p733, m733, s733, d0, mask0, d733,
                           mask733, v0, full0, trips[733][0], trips[733][2])
    lj_b = posjoin_lines("s733", p733, m733, s733, dec, masks)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(la_b + lj_b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"sets identical: priv={int(p733.sum())} miss={int(m733.sum())} "
          f"shared={int(s733.sum())}")

    # ---- PNG private-site map (work dir; evidence copy iff rule meets) ----
    print("== PNG private-site map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    im_p, _, _ = flat_to_planes(p733)
    im_m, _, _ = flat_to_planes(m733)
    im_s, _, _ = flat_to_planes(s733)
    over[im_s] = np.array([0, 255, 0])        # shared green
    over[im_p] = np.array([255, 255, 0])      # 733-private yellow
    over[im_m] = np.array([255, 0, 255])      # missing magenta
    p = workd / "m27-privmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: green=shared tail(Y) yellow=733-private magenta=missing "
          "(s0 geometry; Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=attrib-sites T2=displace+731 R=controls")


if __name__ == "__main__":
    main()
