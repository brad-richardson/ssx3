#!/usr/bin/env python3
"""M21 static-site residual mechanism: maps per shape + EFB-copy diffing (offline).

Usage: m21.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text goes
to stdout (redirect to WORK_DIR/m21.txt); PNG static-site map to
WORK_DIR (evidence copy iff discriminating, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: static-site maps (764-shape counts + Jaccard/persistence overlap,
     epsilon hist + plane split, band/edge/P1 joins)
  2: EFB-copy diffing (cross-shape static-region rates, U/V joint,
     carrier cut + HUD split, fixed rule synths)
  3: controls (control.py) + determinism + shas + Model-0 recompute
Tables, no verdicts.
"""
import hashlib
import re
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 640, 448
N = W * H * 2  # YUYV bytes
ROWB = W * 2
R0_M16, R0_M15 = 22815, 13418
FNV_S0, FNV_M15 = "6b9ffda25bd76c6f", "306b5c778898b64a"
M19_STATIC = {"s0": 2368, "m15": 1476}
M19_STATIC_Y = {"s0": 463, "m15": 439}
M19_NEGRATE = {"s0": 0.5110, "m15": 0.5136}
M19_STATIC_Y_BANDS = {"s0": [15, 186, 262], "m15": [40, 217, 182]}
M19_STATIC_RAW_BANDS = {"s0": [803, 840, 725]}
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
M19_REMOVED = [4888, 1208, 649, 448, 248, 244, 191, 174, 190, 202]
M19_REMOVED_BANDS = [[3415, 1442, 31], [824, 384, 0], [186, 463, 0],
                     [0, 0, 448], [0, 0, 248], [0, 0, 244], [0, 0, 191],
                     [0, 0, 174], [0, 0, 190], [0, 187, 15]]
M19_STATIC_INMASK = [12, 5, 2, 39, 6, 19, 12, 10, 17, 8]
M18_P1_EDGES = {"s0": "0 1 2 2 4 6 8 12 18 29 176",
                "m15": "0 0 1 2 4 6 9 13 19 30 181"}
HUD_SHAPES = [368, 369, 366, 370, 376, 748]


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


def synth_w_bytes(v0b: bytes, fullb: bytes, w: float) -> bytes:
    # M18 verbatim: full + floor(w*(v0-full)); at w=0.5 == (v0+full)//2.
    a = np.frombuffer(v0b, np.uint8).astype(np.float64)
    b = np.frombuffer(fullb, np.uint8).astype(np.float64)
    return np.clip(b + np.floor(w * (a - b)), 0, 255).astype(np.uint8).tobytes()


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


def bfs_edge(static: np.ndarray):
    """Manhattan distance to nearest source site + (dr,dc) components.

    static: bool (h,w), True = source. Exact BFS with nearest-source
    tracking. Returns (dist, dr, dc) int32. (M20 verbatim; M21 feeds
    the MOVED mask as the source set — DESIGN.md.)
    """
    h, w = static.shape
    dist = np.full((h, w), -1, np.int32)
    sr = np.full((h, w), -1, np.int32)
    sc = np.full((h, w), -1, np.int32)
    ys, xs = np.nonzero(static)
    dist[ys, xs] = 0
    sr[ys, xs] = ys
    sc[ys, xs] = xs
    q = deque(zip(ys.tolist(), xs.tolist()))
    while q:
        r, c = q.popleft()
        nd = int(dist[r, c]) + 1
        orr, occ = int(sr[r, c]), int(sc[r, c])
        if r > 0 and dist[r - 1, c] == -1:
            dist[r - 1, c] = nd
            sr[r - 1, c] = orr
            sc[r - 1, c] = occ
            q.append((r - 1, c))
        if r + 1 < h and dist[r + 1, c] == -1:
            dist[r + 1, c] = nd
            sr[r + 1, c] = orr
            sc[r + 1, c] = occ
            q.append((r + 1, c))
        if c > 0 and dist[r, c - 1] == -1:
            dist[r, c - 1] = nd
            sr[r, c - 1] = orr
            sc[r, c - 1] = occ
            q.append((r, c - 1))
        if c + 1 < w and dist[r, c + 1] == -1:
            dist[r, c + 1] = nd
            sr[r, c + 1] = orr
            sc[r, c + 1] = occ
            q.append((r, c + 1))
    rr = np.arange(h, dtype=np.int32)[:, None]
    cc = np.arange(w, dtype=np.int32)[None, :]
    return dist, np.abs(rr - sr).astype(np.int32), np.abs(cc - sc).astype(np.int32)


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


def static_sites(v0b: bytes, midb: bytes, fullb: bytes, synth: bytes):
    """Cell-6 membership (M19 id 6 verbatim) + eps = mid - v0.

    Returns dict with mask (bool [N]), eps (int16 [N]), eqfull
    (int16 [N], mid - full for the identity guard), n.
    """
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    res = s != m
    mask = res & (a == b)
    return {"mask": mask, "eps": (m - a).astype(np.int16),
            "eqfull": (m - b).astype(np.int16), "n": int(mask.sum())}


def task1_lines(tag, v0b, midb, fullb, synth, ym):
    """Canonical Task-1 receipt lines for one frame; returns (lines, art)."""
    L = []
    sp = static_sites(v0b, midb, fullb, synth)
    mask, eps, n = sp["mask"], sp["eps"], sp["n"]
    pl = plane_of_byte()
    plm = pl[mask]
    ny, nu, nv = (int((plm == p).sum()) for p in (0, 1, 2))
    L.append(f"{tag}: cell6 n={n} (M19 want {M19_STATIC[tag]}); "
             f"Y/U/V={ny}/{nu}/{nv} (Y want {M19_STATIC_Y[tag]})")
    if n != M19_STATIC[tag] or ny != M19_STATIC_Y[tag]:
        L.append(f"{tag} COUNT MISMATCH: STOP, tabled.")
        return L, None
    e = eps[mask]
    L.append(f"{tag} eps==0 count={int((e == 0).sum())} (want 0); "
             f"eps==mid-full identity="
             f"{bool((eps[mask] == sp['eqfull'][mask]).all())} (want True)")
    vals, counts = np.unique(e, return_counts=True)
    L.append(f"{tag} ehist range=[{int(vals.min())},{int(vals.max())}] "
             + " ".join(f"{int(v)}:{int(c)}" for v, c in zip(vals, counts)))
    ae = np.abs(e).astype(np.int16)
    L.append(f"{tag} aehist={mag_hist(ae)} max={int(ae.max())} "
             f"mean={float(ae.mean()):.3f} p1={float((ae == 1).mean()):.4f}")
    for pid, nm in ((0, "Y"), (1, "U"), (2, "V")):
        dd = e[plm == pid]
        aa = np.abs(dd)
        L.append(f"{tag} plane {nm}: n={len(dd)} "
                 f"aehist={mag_hist(aa) if len(dd) else [0, 0, 0, 0, 0]} "
                 f"mean={float(dd.mean()) if len(dd) else 0:.3f} "
                 f"amean={float(aa.mean()) if len(dd) else 0:.3f}")
    L.append(f"{tag} P(eps>0)={float((e > 0).mean()):.4f} "
             f"(M19 negrate want {M19_NEGRATE[tag]})")
    # bands (M19 thirds verbatim): Y + raw
    im_y, im_u, im_v = flat_to_planes(mask)
    for bi, rows in enumerate(BAND_ROWS):
        L.append(f"{tag} band {bi} Y: n={int(im_y[rows].sum())} "
                 f"(want {M19_STATIC_Y_BANDS[tag][bi]})")
    lab = mask.reshape(H, ROWB)
    for bi, rows in enumerate(BAND_ROWS):
        nraw = int(lab[rows].sum())
        want = M19_STATIC_RAW_BANDS.get(tag, [None] * 3)[bi]
        L.append(f"{tag} band {bi} raw: n={nraw}"
                 + (f" (want {want})" if want is not None else ""))
    # edge distance: M20 BFS verbatim, source = MOVED (DESIGN.md)
    a = np.frombuffer(v0b, np.uint8)
    b = np.frombuffer(fullb, np.uint8)
    mv_y, mv_u, mv_v = flat_to_planes((a != b))
    st_y, st_u, st_v = flat_to_planes((a == b))
    ey, eu, ev = flat_to_planes(eps)
    for pname, mv, st, im, ee in (("Y", mv_y, st_y, im_y, ey),
                                  ("U", mv_u, st_u, im_u, eu),
                                  ("V", mv_v, st_v, im_v, ev)):
        dist, dr, dc = bfs_edge(mv)
        dd = ee[im].astype(np.float64)
        ds = dist[im]
        L.append(f"{tag} edge {pname}: dmin={int(ds.min())} "
                 f"dmax={int(ds.max())} (want dmin>=1); "
                 f"bg_static_n={int(st.sum())} "
                 f"bg_meand={float(dist[st].mean()):.3f}")
        for lo in (1, 2, 3, 4, 5):
            sel = ds == lo if lo < 5 else ds >= 5
            lab5 = f"d={lo}" if lo < 5 else "d=5+"
            L.append(f"{tag} edge {pname} {lab5}: n={int(sel.sum())} "
                     f"meane={float(dd[sel].mean()) if sel.sum() else 0:.3f} "
                     f"sd={float(dd[sel].std()) if sel.sum() else 0:.3f} "
                     f"amean={float(np.abs(dd[sel]).mean()) if sel.sum() else 0:.3f}")
        rrs, ccs = dr[im], dc[im]
        rb = np.clip(rrs, 0, 3)
        cb = np.clip(ccs, 0, 3)
        row = []
        for i in range(4):
            for j in range(4):
                sel = (rb == i) & (cb == j)
                row.append(f"({i},{j}):n={int(sel.sum())}"
                           f"/m={float(dd[sel].mean()) if sel.sum() else 0:.2f}")
        L.append(f"{tag} edge {pname} drxdc: " + " ".join(row))
    # P1 decile join (M18 code verbatim; edges guarded)
    mag, qs, dec = p1_gradient(ym)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    L.append(f"{tag} P1 edges: {estrs} (m18.txt want {M18_P1_EDGES[tag]}) "
             f"match={estrs == M18_P1_EDGES[tag]}")
    for dci in range(10):
        sel = im_y & (dec == dci)
        dd = ey[sel].astype(np.float64)
        L.append(f"{tag} P1dec Y {dci}: n={int(sel.sum())} "
                 f"mean={float(dd.mean()) if sel.sum() else 0:.3f} "
                 f"sd={float(dd.std()) if sel.sum() else 0:.3f} "
                 f"amean={float(np.abs(dd).mean()) if sel.sum() else 0:.3f}")
    dec_u = dec[:, 0::2]
    for pname, im, _ in (("U", im_u, eu), ("V", im_v, ev)):
        row = []
        for dci in range(10):
            sel = im & (dec_u == dci)
            row.append(f"{dci}:{int(sel.sum())}")
        L.append(f"{tag} P1dec {pname} n-by-dec: " + " ".join(row))
    art = {"n": n, "mask": mask, "eps": eps, "im_y": im_y,
           "ey": ey, "ny": ny, "nu": nu, "nv": nv}
    return L, art


def uv_joint_lines(tag, v0b, midb, fullb):
    """Task 2.2: U/V static-site residual joint at chroma px (both static)."""
    L = []
    v0u = split_planes(np.frombuffer(v0b, np.uint8))[1].astype(np.int16)
    midu = split_planes(np.frombuffer(midb, np.uint8))[1].astype(np.int16)
    fu = split_planes(np.frombuffer(fullb, np.uint8))[1].astype(np.int16)
    v0v = split_planes(np.frombuffer(v0b, np.uint8))[2].astype(np.int16)
    midv = split_planes(np.frombuffer(midb, np.uint8))[2].astype(np.int16)
    fv = split_planes(np.frombuffer(fullb, np.uint8))[2].astype(np.int16)
    stu = v0u == fu
    stv = v0v == fv
    resu = stu & (midu != v0u)
    resv = stv & (midv != v0v)
    pop = stu & stv
    n = int(pop.sum())
    both = int((resu & resv & pop).sum())
    uo = int((resu & ~resv & pop).sum())
    vo = int((~resu & resv & pop).sum())
    ne = int((~resu & ~resv & pop).sum())
    pu = (both + uo) / n
    pv = (both + vo) / n
    exp = n * pu * pv
    L.append(f"{tag} uvjoint pop(both-static)={n} both={both} Uonly={uo} "
             f"Vonly={vo} neither={ne}")
    L.append(f"{tag} uvjoint P(U)={pu:.4f} P(V)={pv:.4f} "
             f"P(V|U)={both / (both + uo) if both + uo else 0:.4f} "
             f"P(V|~U)={vo / (vo + ne) if vo + ne else 0:.4f} "
             f"expected_both={exp:.1f} actual/expected="
             f"{both / exp if exp else 0:.3f}")
    return L


def dist4(x):
    a = np.asarray(x, dtype=np.float64)
    return (float(a.min()), float(np.median(a)), float(a.mean()),
            float(a.max()))


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0)

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin", m15d / "m15-v0.bin",
              m15d / "m15-mid.bin", m15d / "m15-full.bin"]
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")

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
          + ("OK" if carriers_ok else "MISMATCH: STOP per-carrier, tabled"))

    print("== model 0 (baseline recompute) ==")
    v015 = load_dump(m15d / "m15-v0.bin")
    mid15 = load_dump(m15d / "m15-mid.bin")
    full15 = load_dump(m15d / "m15-full.bin")
    ym15 = split_planes(np.frombuffer(mid15, np.uint8))[0]
    b15 = synth_w_bytes(v015, full15, 0.5)
    r15 = xdiff(b15, mid15)[0]
    f15 = f"{fnv1a(b15):016x}"
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    ym0 = split_planes(np.frombuffer(mid, np.uint8))[0]
    b0 = synth_w_bytes(v0, full, 0.5)
    r0 = xdiff(b0, mid)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17/M18/M19/M20 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== Task 1: static sites s0 ==")
    t1 = time.time()
    L0, art0 = task1_lines("s0", v0, mid, full, b0, ym0)
    for ln in L0:
        print(ln)
        canon.append(ln)
    print(f"(Task-1 s0 wall: {time.time() - t1:.1f}s)")
    if art0 is None:
        print("cell-6 count guard failed on s0: STOP before Task 1.1.")
        return
    print("== Task 1: static sites m15 ==")
    t1 = time.time()
    L15, art15 = task1_lines("m15", v015, mid15, full15, b15, ym15)
    for ln in L15:
        print(ln)
    print(f"(Task-1 m15 wall: {time.time() - t1:.1f}s)")
    if art15 is None:
        print("cell-6 count guard failed on m15: STOP before Task 1.1.")
        return

    R0 = art0["mask"]
    R15 = art15["mask"]
    pl = plane_of_byte()

    # ---- Task 1.1: 764-shape static-site map pass ----
    print("== Task 1.1: coarse static-site pass: all M16 shapes ==")
    shapes = sorted(int(p.name[8:12]) for p in m16d.glob("m16-v0-s*.bin"))
    print(f"shapes: n={len(shapes)} 0..{max(shapes)}")
    t1 = time.time()
    mism = 0
    occ = np.zeros(N, np.int32)
    counts, j0, j15 = [], [], []
    in0, out0, in15, out15 = [], [], [], []
    # pooled EFB accumulators: [in_diff_sum, in_n_sum, out_diff_sum, out_n_sum]
    pool0 = np.zeros(4, np.int64)   # R_s0 mask, t != 0
    pool0all = np.zeros(4, np.int64)  # R_s0 mask, all t (reference)
    pool15 = np.zeros(4, np.int64)  # R_m15 mask, all t
    print("| shape | R_s | R_loo | stat | Y | U | V | jacc_s0 | jacc_m15 | "
          "in0 | out0 | in15 | out15 |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | "
          "---: | ---: | ---: | ---: |")
    for i, s in enumerate(shapes):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        xd, _, _ = xdiff(bl, mm)
        rs = loo.get(s, ("?", "?"))[1]
        if xd != rs:
            mism += 1
        sp = static_sites(vv, mm, ff, bl)
        mk = sp["mask"]
        occ += mk
        av = np.frombuffer(vv, np.uint8)
        bv = np.frombuffer(ff, np.uint8)
        st = av == bv
        plm = pl[mk]
        ny, nu, nv = (int((plm == p).sum()) for p in (0, 1, 2))
        inter0 = int((mk & R0).sum())
        union0 = int((mk | R0).sum())
        jj0 = inter0 / union0
        inter15 = int((mk & R15).sum())
        union15 = int((mk | R15).sum())
        jj15 = inter15 / union15
        in_n0 = int((st & R0).sum())
        i0 = inter0 / in_n0
        o_n0 = int(st.sum()) - in_n0
        o0 = (int(mk.sum()) - inter0) / o_n0
        in_n15 = int((st & R15).sum())
        i15 = inter15 / in_n15
        o_n15 = int(st.sum()) - in_n15
        o15 = (int(mk.sum()) - inter15) / o_n15
        counts.append(int(mk.sum()))
        j0.append(jj0)
        j15.append(jj15)
        in0.append(i0)
        out0.append(o0)
        in15.append(i15)
        out15.append(o15)
        pool0all += (inter0, in_n0, int(mk.sum()) - inter0, o_n0)
        if s != 0:
            pool0 += (inter0, in_n0, int(mk.sum()) - inter0, o_n0)
        pool15 += (inter15, in_n15, int(mk.sum()) - inter15, o_n15)
        print(f"| {s} | {xd} | {rs} | {int(mk.sum())} | {ny} | {nu} | {nv} | "
              f"{jj0:.4f} | {jj15:.4f} | {i0:.4f} | {o0:.4f} | {i15:.4f} | "
              f"{o15:.4f} |")
        if (i + 1) % 200 == 0:
            print(f"  ... statmap {i + 1}/{len(shapes)}")
    print(f"coarse-pass wall: {time.time() - t1:.1f}s for {len(shapes)} shapes")
    print(f"R_s vs loo.txt mismatches: {mism} (want 0)")
    cmin, cmed, cmean, cmax = dist4(counts)
    print(f"stat-count dist: min={cmin:.0f} med={cmed:.0f} mean={cmean:.1f} "
          f"max={cmax:.0f}")
    print(f"jacc(Rt,Rs0) all764: min/med/mean/max="
          f"{'/'.join(f'{v:.4f}' for v in dist4(j0))} (t=0 reads 1.0)")
    print(f"jacc(Rt,Rs0) t!=0: min/med/mean/max="
          f"{'/'.join(f'{v:.4f}' for v in dist4(j0[1:]))}")
    print(f"jacc(Rt,Rm15): min/med/mean/max="
          f"{'/'.join(f'{v:.4f}' for v in dist4(j15))}")
    jself = int((R0 & R15).sum()) / int((R0 | R15).sum())
    print(f"jacc(Rs0,Rm15)={jself:.4f} inter={int((R0 & R15).sum())} "
          f"union={int((R0 | R15).sum())}")
    # persistence histogram over all offsets + restricted to R_s0/R_m15
    bins = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 63), (64, 763),
            (764, 764)]
    row = []
    for lo, hi in bins:
        row.append(f"{lo}-{hi}:{int(((occ >= lo) & (occ <= hi)).sum())}")
    print("persistence all-offsets occ-hist: " + " ".join(row))
    print(f"persistence maxocc={int(occ.max())} "
          f"n_at_max={int((occ == occ.max()).sum())}")
    for nm, mm in (("Rs0", R0), ("Rm15", R15)):
        oo = occ[mm]
        row = []
        for lo, hi in bins:
            row.append(f"{lo}-{hi}:{int(((oo >= lo) & (oo <= hi)).sum())}")
        print(f"persistence {nm}-sites occ-hist: " + " ".join(row))
        print(f"persistence {nm}-sites meanocc={float(oo.mean()):.1f} "
              f"ge50pct={int((oo >= 382).sum())} universal={int((oo == 764).sum())}")

    # ---- Task 2.1: pooled cross-shape EFB rates ----
    print("== Task 2.1: pooled cross-shape static-region rates ==")
    for nm, pp in (("Rs0-mask/t!=0", pool0), ("Rs0-mask/all764", pool0all),
                   ("Rm15-mask/all764", pool15)):
        inr = pp[0] / pp[1]
        our = pp[2] / pp[3]
        print(f"{nm}: in_diff={pp[0]} in_n={pp[1]} in_rate={inr:.6f} "
              f"out_diff={pp[2]} out_n={pp[3]} out_rate={our:.6f} "
              f"ratio={inr / our:.3f}")
    print(f"self-frame arithmetic guard t=0: in0={in0[0]:.4f} (want 1.0) "
          f"out0={out0[0]:.4f} (want 0.0)")
    print(f"in0(t!=0) dist: min/med/mean/max="
          f"{'/'.join(f'{v:.4f}' for v in dist4(in0[1:]))}")

    print("== Task 2.2: U/V joint ==")
    for ln in uv_joint_lines("s0", v0, mid, full):
        print(ln)
    for ln in uv_joint_lines("m15", v015, mid15, full15):
        print(ln)

    # ---- Task 2.3: carrier cut + HUD split ----
    print("== Task 2.3: carrier cut (static bytes in removed masks) ==")
    if not carriers_ok:
        print("per-carrier work skipped (carrier mismatch, tabled above).")
    else:
        sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
        res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
        im_y0 = art0["im_y"]
        _, im_u0, im_v0 = flat_to_planes(R0)
        im_y15 = art15["im_y"]
        _, im_u15, im_v15 = flat_to_planes(R15)
        masks = {}
        for rank, s in enumerate(top10, 1):
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
            yin = int(im_y0[removed].sum())
            # U/V via co-located Y (r,2c) (M20 co-location verbatim)
            rm_u = removed[:, 0::2]
            uin = int((im_u0 & rm_u).sum())
            vin = int((im_v0 & rm_u).sum())
            print(f"rank {rank} shape {s}: removedYpx={nrem} "
                  f"(want {M19_REMOVED[rank - 1]}) bands={bd} "
                  f"(want {M19_REMOVED_BANDS[rank - 1]}) s0statY_in={yin} "
                  f"(want {M19_STATIC_INMASK[rank - 1]}) s0statU_in={uin} "
                  f"s0statV_in={vin}")
        print("== Task 2.3: HUD-region split ==")
        hud = np.zeros((H, W), bool)
        for s in HUD_SHAPES:
            hud |= masks[s]
        print(f"HUD region = union of removed masks {HUD_SHAPES}: "
              f"nYpx={int(hud.sum())} bands={bands_of(hud.astype(np.int64))}")
        for tag, imy, imu, imv, ny in (("s0", im_y0, im_u0, im_v0, art0["ny"]),
                                       ("m15", im_y15, im_u15, im_v15,
                                        art15["ny"])):
            yin = int(imy[hud].sum())
            hud_u = hud[:, 0::2]
            uin = int((imu & hud_u).sum())
            vin = int((imv & hud_u).sum())
            print(f"{tag} HUD split: statY_in={yin}/{ny} "
                  f"({yin / ny:.4f}) statY_out={ny - yin} "
                  f"statU_in={uin} statV_in={vin} "
                  f"raw_in={yin + uin + vin} "
                  f"(m15 joined vs s0-derived masks)")

    # ---- static-site rule synths ----
    print("== static-site rule synths ==")
    for tag, (vv, mm, ff, base) in (("s0", (v0, mid, full, r0)),
                                    ("m15", (v015, mid15, full15, r15))):
        a = np.frombuffer(vv, np.uint8).astype(np.int16)
        m = np.frombuffer(mm, np.uint8).astype(np.int16)
        b = np.frombuffer(ff, np.uint8).astype(np.int16)
        st = a == b
        bl = synth_w_bytes(vv, ff, 0.5)
        syn0 = np.frombuffer(bl, np.uint8).astype(np.int16)
        eps = m - a
        res6 = (syn0 != m) & st
        for nm, delta in (("+1", 1), ("-1", -1)):
            syn = syn0.copy()
            syn[st] = np.clip(a[st] + delta, 0, 255)
            synb = syn.astype(np.uint8).tobytes()
            xd, xm, xn = xdiff(synb, mm)
            hits = int((res6 & (eps == delta)).sum())
            print(f"{tag} rule v0{nm} on static: cell6hits={hits} R={xd} "
                  f"explained={base - xd} e={1 - xd / base:.4f} "
                  f"fnv={fnv1a(synb):016x}")

    # ---- determinism re-run (Task 1 on s0, canonical text) ----
    print("== determinism re-run (Task 1 on s0, second pass) ==")
    L0b, art0b = task1_lines("s0", v0, mid, full, b0, ym0)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0b is not None and art0['n'] == art0b['n']}")

    # ---- PNG static-site map (work dir; evidence copy iff discriminating) ----
    print("== PNG static-site map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    eey = art0["ey"]
    imy = art0["im_y"]
    pos = imy & (eey > 0)
    neg = imy & (eey < 0)
    over[pos] = np.array([255, 0, 0])      # eps>0 red
    over[neg] = np.array([0, 128, 255])    # eps<0 blue
    big = np.abs(eey) >= 4
    over[imy & big & (eey > 0)] = np.array([255, 255, 0])   # big+ yellow
    over[imy & big & (eey < 0)] = np.array([255, 0, 255])   # big- magenta
    p = workd / "m21-staticmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: red=e>0 blue=e<0 yellow=e>=+4 magenta=e<=-4 "
          "(static Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=statmap+eps+joins T2=EFB+uv+carrier+rules R=controls")


if __name__ == "__main__":
    main()
