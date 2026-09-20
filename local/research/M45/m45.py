#!/usr/bin/env python3
"""M45 shape-22 bottom-cluster full-set attribution (offline).

Usage: m45.py M16_DIR M15_DIR M34TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m34-census.tsv (s22's unnamed row to reproduce);
raw XFB dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt
text goes to stdout (redirect to WORK_DIR/m45.txt); PNG cluster
map to WORK_DIR (evidence copy iff the DESIGN.md rule meets,
decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: s22 moved-set census (moved cells + private table + completeness)
  2: full-set attribution + cluster geometry + c296 side-by-side
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
M19_CELL_S0 = 2475
M20_TAIL_S0 = 102
M20_TAIL_S0_SUB = (28, 74)  # (8-15, 16+)
M20_TAIL_S0_MAX = 47
M19_POSRATE_S0 = 0.8093  # P(d>0) on s0 cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
NAMED8 = [257, 277, 296, 301, 321, 340, 342, 343]
S0_NAMED_ROWS = {257: list(range(23, 33)), 277: list(range(23, 33)),
                 296: [24, 25, 26, 27, 28, 31, 32, 33, 34],
                 301: list(range(23, 34)), 321: list(range(23, 33)),
                 340: [24, 25, 26, 27, 31, 32, 33, 34],
                 342: [27, 28, 29, 34, 35], 343: [26, 27]}
M18_P1_EDGE_S0 = "0 1 2 2 4 6 8 12 18 29 176"
INBAND_LO, INBAND_HI = 393, 402
# ---- M45 pinned s22 rows (M29 REPORT + m34-census.tsv, §Definitions) ----
BOT = [(400, 296), (401, 296), (393, 307), (402, 295)]  # (r,c) pinned
S22_TAIL, S22_J = 106, "0.9623"
S22_NAMED_MOVED = [296]
S22_C296_NOV = (11, 9)
S22_C296_EX = [400, 401]
S22_UNNAMED_MOVED = [295, 307]
S22_C295_NOV = (1, 0)
S22_C307_NOV = (2, 1)
S0_C295_ROWS = []
S0_C307_ROWS = [404]
S22_C295_EX = [402]
S22_C307_EX = [393]
S22_C307_KEPT = [404]
C296_PAIR_VALS = {(400, 296): {"ad": 8, "gQ": 22, "gO": -1, "dec": 9},
                  (401, 296): {"ad": 8, "gQ": 24, "gO": -2, "dec": 9}}
# pinned pooled-extra refs (committed REPORTs, cited not recomputed):
REF_M29_EXTRA_ALL = (0, 3, 2)  # M29 extra[all] n=5 near/far/non
REF_M29_EXTRA_229 = (0, 1, 2)  # M29 extra[22,9] n=3 near/far/non
REF_M36_GRAND = (14, 0, 10)  # M36 grand pooled extras n=24
ANALYZED = [0, 22]


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
    """Per-site private + missing rows with cross values (M27/M35 verbatim)."""
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
    """Signed-gap sign tables (g_Q x g_O per site; M35 verbatim)."""
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
    """|d| stats per set (|d_B| on priv, |d_A| on miss; M35 verbatim)."""
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


def sgn(x):
    return "+" if x > 0 else ("-" if x < 0 else "0")


def inband(r: int) -> bool:
    return INBAND_LO <= r <= INBAND_HI


def load_triplet(m16d: Path, s: int):
    vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
    mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
    ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
    return vv, mm, ff, synth_w_bytes(vv, ff, 0.5)


def analyze(m16d: Path, UNNAMED, s0u):
    """Cell-7 + tail + s22 full sets + named/unnamed row sets (fresh loads).

    UNNAMED/s0u are the guarded full-pass universe (stable inputs);
    every s22 row below is recomputed from fresh s0+s22 loads.
    """
    pl = plane_of_byte()
    pr, pc = plane_coords()
    T = {}
    for s in ANALYZED:
        vv, mm, ff, bl = load_triplet(m16d, s)
        sp = interior_sites(vv, mm, ff, bl)
        t, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        T[s] = {"v0": vv, "mid": mm, "full": ff, "blend": bl,
                "sp": sp, "mask": sp["mask"], "d": sp["delta"],
                "t": t}
    A = {"T": T, "pl": pl, "pr": pr, "pc": pc,
         "UNNAMED": list(UNNAMED), "s0u": dict(s0u)}
    t0, t22 = T[0]["t"], T[22]["t"]
    P = t22 & ~t0
    M = t0 & ~t22
    S = t22 & t0
    A["P"], A["M"], A["S"] = P, M, S
    A["tail22"] = int(t22.sum())
    A["j22"] = jaccard(t22, t0)
    A["priv_rc"] = sorted((int(pr[o]), int(pc[o]))
                         for o in np.nonzero(P)[0])
    A["miss_rc"] = sorted((int(pr[o]), int(pc[o]))
                         for o in np.nonzero(M)[0])
    # named census over NAMED8 (exact-match, M28 rule)
    A["r0_named"] = {c: y_col_rows(t0, c, pl, pr, pc) for c in NAMED8}
    A["r22_named"] = {c: y_col_rows(t22, c, pl, pr, pc) for c in NAMED8}
    A["named_moved"] = sorted(c for c in NAMED8
                              if A["r22_named"][c] != A["r0_named"][c])
    # unnamed census over the guarded universe (exact-match, M34 rule)
    A["ycols22"] = tail_y_cols(t22, pl, pr, pc)
    A["ucen22"] = census_unnamed_of(A["ycols22"], s0u)
    A["unam_moved"] = sorted(c for c in UNNAMED
                             if A["ucen22"][c]["pres"] == 0)
    # s22 delta-row sets per moved cell
    A["r0_296"] = A["r0_named"][296]
    A["r22_296"] = A["r22_named"][296]
    A["r0_295"] = y_col_rows(t0, 295, pl, pr, pc)
    A["r22_295"] = y_col_rows(t22, 295, pl, pr, pc)
    A["r0_307"] = y_col_rows(t0, 307, pl, pr, pc)
    A["r22_307"] = y_col_rows(t22, 307, pl, pr, pc)
    ex296 = sorted(set(A["r22_296"]) - set(A["r0_296"]))
    ex295 = sorted(set(A["r22_295"]) - set(A["r0_295"]))
    ex307 = sorted(set(A["r22_307"]) - set(A["r0_307"]))
    A["ex296"], A["ex295"], A["ex307"] = ex296, ex295, ex307
    A["mi296"] = sorted(set(A["r0_296"]) - set(A["r22_296"]))
    A["keep307"] = sorted(set(A["r22_307"]) & set(A["r0_307"]))
    A["ex296mask"] = np.zeros(N, bool)
    for r in ex296:
        A["ex296mask"][off_of(r, 296)] = True
    A["outpriv"] = np.zeros(N, bool)  # outside-col (c295/c307) extras
    for r in ex295:
        A["outpriv"][off_of(r, 295)] = True
    for r in ex307:
        A["outpriv"][off_of(r, 307)] = True
    A["bot_offs"] = [off_of(r, c) for r, c in BOT]
    return A


def task1_lines(A):
    """Task 1 receipt lines: moved cells + private table + completeness."""
    L = []
    T = A["T"]
    t0 = T[0]["t"]
    P, M, S = A["P"], A["M"], A["S"]
    pl = A["pl"]
    # full sets + planes
    L.append(f"s22 sets: tail22={A['tail22']} J={A['j22']:.4f} "
             f"priv={int(P.sum())} miss={int(M.sum())} "
             f"shared={int(S.sum())}")
    for nm, q in (("priv", P), ("miss", M), ("shared", S)):
        pp = pl[q]
        L.append(f"s22 planes {nm}: Y={int((pp == 0).sum())} "
                 f"U={int((pp == 1).sum())} V={int((pp == 2).sum())} "
                 f"n={int(q.sum())}")
    L.append(f"s22 priv_rc={A['priv_rc']}")
    L.append(f"s22 miss_rc={A['miss_rc']}")
    # moved-cell table: named
    L.append(f"s22 named_moved={A['named_moved']} "
             f"named_still={sorted(set(NAMED8) - set(A['named_moved']))}")
    for c in A["named_moved"]:
        r0, rQ = A["r0_named"][c], A["r22_named"][c]
        ov = len(set(rQ) & set(r0))
        mi = sorted(set(r0) - set(rQ))
        ex = sorted(set(rQ) - set(r0))
        stand = ("missing" if mi and not ex
                 else ("extra" if ex and not mi else "mixed"))
        L.append(f"s22 namedcell c{c}: n/ov={len(rQ)}/{ov} "
                 f"delta={len(mi) + len(ex)} stand={stand} "
                 f"s0rows={r0} s22rows={rQ} ex={ex} mi={mi}")
    # moved-cell table: unnamed
    L.append(f"s22 unam_moved={A['unam_moved']} "
             f"k={len(A['unam_moved'])} "
             f"unam_still_n={len(A['UNNAMED']) - len(A['unam_moved'])}")
    for c in A["unam_moved"]:
        e = A["ucen22"][c]
        r0 = A["s0u"][c]
        rQ = A["ycols22"].get(c, [])
        mi = sorted(set(r0) - set(rQ))
        ex = sorted(set(rQ) - set(r0))
        stand = ("missing" if mi and not ex
                 else ("extra" if ex and not mi else "mixed"))
        L.append(f"s22 unamcell c{c}: n/ov={e['n']}/{e['ov']} "
                 f"delta={e['delta']} stand={stand} "
                 f"s0rows={r0} s22rows={rQ} ex={ex} mi={mi}")
    # private table: outside-col sites + their columns' s0 rows
    for r, c in ((393, 307), (402, 295)):
        r0 = y_col_rows(t0, c, A["pl"], A["pr"], A["pc"])
        seat = "s0-bearing" if r0 else "s0-empty"
        L.append(f"s22 privcell site=({r},{c}) s0rows_c{c}={r0} "
                 f"seat={seat} s22rows_c{c}={A['ycols22'].get(c, [])}")
    # completeness table: bottom group vs full moved set
    pin = [rc for rc in A["priv_rc"] if inband(rc[0])]
    pout = [rc for rc in A["priv_rc"] if not inband(rc[0])]
    minb = [rc for rc in A["miss_rc"] if inband(rc[0])]
    mout = [rc for rc in A["miss_rc"] if not inband(rc[0])]
    L.append(f"s22 complete priv_in={len(pin)} {pin} "
             f"priv_out={len(pout)} {pout}")
    L.append(f"s22 complete miss_in={len(minb)} {minb} "
             f"miss_out={len(mout)} {mout}")
    for cnm, rows in (("c296ex", A["ex296"]), ("c295ex", A["ex295"]),
                      ("c307ex", A["ex307"])):
        ib = [r for r in rows if inband(r)]
        ob = [r for r in rows if not inband(r)]
        L.append(f"s22 complete {cnm}: in={ib} out={ob}")
    whole = (sorted(A["priv_rc"]) == sorted(BOT) and not A["miss_rc"])
    L.append(f"s22 complete wholeset={whole} "
             f"(priv==BOT[{len(BOT)}] and miss empty)")
    return L


def geo_lines(sites, tag):
    """Pairwise row/col distances + span over 4 cluster sites (shared)."""
    L = []
    b = list(sites)
    L.append(f"{tag} sites={b} band=[{INBAND_LO},{INBAND_HI}]")
    for i in range(len(b)):
        for j in range(i + 1, len(b)):
            (r1, c1), (r2, c2) = b[i], b[j]
            L.append(f"{tag} pair ({r1},{c1})-({r2},{c2}): "
                     f"drow={abs(r1 - r2)} dcol={abs(c1 - c2)}")
    L.append(f"{tag} rowspan: min={min(r for r, _ in b)} "
             f"max={max(r for r, _ in b)} "
             f"span={max(r for r, _ in b) - min(r for r, _ in b)}")
    return L


def task2_lines(A, dec):
    """Task 2 receipt lines: value rows + geometry + c296 side-by-side."""
    L = []
    T, pl, pr, pc = A["T"], A["pl"], A["pr"], A["pc"]
    v0, full0, d0, m0 = T[0]["v0"], T[0]["full"], T[0]["d"], T[0]["mask"]
    T22 = T[22]
    P, M, S = A["P"], A["M"], A["S"]
    # per-site value rows (M36-style) + dec annotation
    la, summ = attrib_lines("s22", P, M, S, d0, m0,
                            T22["d"], T22["mask"], v0, full0,
                            T22["v0"], T22["full"])
    L += la
    dec_u = dec[:, 0::2]

    def dec_of(o):
        r, c = int(pr[o]), int(pc[o])
        if int(pl[o]) == 0:
            return int(dec[r, c])
        return int(dec_u[r, c])

    moved_offs = sorted(int(o) for o in
                        np.nonzero(P | M)[0])
    n9 = 0
    for o in moved_offs:
        dc = dec_of(o)
        n9 += dc == 9
        L.append(f"s22dec o={o} rc=({int(pr[o])},{int(pc[o])}) dec={dc}")
    L.append(f"s22dec pooled: dec9={n9}/{len(moved_offs)} "
             f"({n9 / len(moved_offs) if moved_offs else 0:.4f})")
    L += dstats_lines("s22", P, M, T22["d"], d0)
    L += gapsign_lines("s22", P, M, v0, full0,
                       T22["v0"], T22["full"])
    # cluster geometry over the 4 pinned bottom sites
    L += geo_lines(list(BOT), "s22geo")
    rows296 = {400, 401}
    rows_out = {393, 402}
    cols296 = {296}
    cols_out = {307, 295}
    L.append(f"s22geo shared_rows_296_vs_out="
             f"{sorted(rows296 & rows_out)} "
             f"shared_cols_296_vs_out={sorted(cols296 & cols_out)}")
    for c in (295, 307):
        L.append(f"s22geo colseat c{c}: delta_vs_c296={c - 296} "
                 f"abs={abs(c - 296)}")
    # c296 side-by-side: measured pair + pooled splits vs pinned refs
    pair_offs = [off_of(400, 296), off_of(401, 296)]
    pn = pf = pnn = 0
    for o in pair_offs:
        if m0[o]:
            ad = int(abs(int(d0[o])))
            if ad in (6, 7):
                pn += 1
            else:
                pf += 1
        else:
            pnn += 1
    L.append(f"s22side pair296: near/far/non={pn}/{pf}/{pnn} (n=2)")
    ps = summ["priv"]
    L.append(f"s22side pooled4: near/far/non={ps['near']}/{ps['far']}/"
             f"{ps['non']} (n={ps['n']})")
    L.append(f"s22side ref M29-extra-all n=5 near/far/non="
             f"{REF_M29_EXTRA_ALL[0]}/{REF_M29_EXTRA_ALL[1]}/"
             f"{REF_M29_EXTRA_ALL[2]} (M29 REPORT Task 2, pinned)")
    L.append(f"s22side ref M29-extra-22-9 n=3 near/far/non="
             f"{REF_M29_EXTRA_229[0]}/{REF_M29_EXTRA_229[1]}/"
             f"{REF_M29_EXTRA_229[2]} (M29 REPORT Task 2, pinned)")
    L.append(f"s22side ref M36-grand n=24 near/far/non="
             f"{REF_M36_GRAND[0]}/{REF_M36_GRAND[1]}/"
             f"{REF_M36_GRAND[2]} (M36 REPORT Task 1, pinned)")
    return L


def main():
    m16d, m15d, m34tsv, workd, evidd = (Path(a) for a in sys.argv[1:6])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    print("== inputs (read-only) ==")
    inputs = []
    for s in ANALYZED:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    inputs += [m15d / "m15-v0.bin", m15d / "m15-mid.bin",
               m15d / "m15-full.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    qb = m34tsv.read_bytes()
    print(f"input {m34tsv}: bytes={len(qb)} "
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
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M44 baselines: STOP, tabled.")
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
    # s0 named reference rows (M27/M28)
    named_ok = True
    for c in NAMED8:
        rows = y_col_rows(t0, c, pl, pr, pc)
        ok = rows == S0_NAMED_ROWS[c]
        named_ok = named_ok and ok
        if not ok:
            print(f"s0 named c{c} MISMATCH: {rows} want {S0_NAMED_ROWS[c]}")
    print(f"s0 named rows guard: {'OK' if named_ok else 'MISMATCH: STOP'}")
    if not named_ok:
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
    print(f"union tail-Y cols (all 764): n={len(allcols)} (want 41)")
    print(f"UNNAMED (union minus named8): n={len(UNNAMED)} (want 33)")
    print(f"s0-bearing unnamed (n0>0): n={len(n0pos)} (want 13)")
    print(f"pure-private unnamed (n0==0): n={len(n0zero)} (want 20)")
    dom_ok = (len(allcols) == 41 and len(UNNAMED) == 33
              and len(n0pos) == 13 and len(n0zero) == 20)
    print("domain guard: " + ("OK" if dom_ok else
                              "MISMATCH vs M34: STOP, tabled."))
    if not dom_ok:
        return

    # ---- s22 TSV-row guard (M34 match or stop) ----
    print("== s22 TSV-row guard (M34 match or stop) ==")
    tsv_lines = m34tsv.read_text(errors="replace").splitlines()
    want_hdr = "\t".join(["shape", "tail_n", "J_vs_s0"]
                         + [f"{k}{c}" for c in UNNAMED
                            for k in ("n", "ov", "pres")])
    hdr_cols = []
    for tok in tsv_lines[0].split("\t")[3:]:
        if tok.startswith("n"):
            hdr_cols.append(int(tok[1:]))
    uni_ok = (tsv_lines[0] == want_hdr and len(tsv_lines) == 765
              and hdr_cols == UNNAMED)
    print(f"m34-census.tsv rows={len(tsv_lines) - 1} "
          f"hdr_match={tsv_lines[0] == want_hdr} "
          f"universe_match={hdr_cols == UNNAMED}")
    rec = per[22]
    cen22 = census_unnamed_of(rec["ycols"], s0u)
    row = [str(22), str(rec["tail"]), f"{rec['j']:.4f}"]
    for c in UNNAMED:
        row += [str(cen22[c]["n"]), str(cen22[c]["ov"]),
                str(cen22[c]["pres"])]
    row_ok = uni_ok and "\t".join(row) == tsv_lines[23]
    print(f"s22 TSV row match: {row_ok}")
    if not row_ok:
        got = "\t".join(row).split("\t")
        want = tsv_lines[23].split("\t")
        for i, (g, w) in enumerate(zip(got, want)):
            if g != w:
                print(f"  field {i}: got {g} want {w}")
        print("MISMATCH vs M34 s22 row: STOP, tabled.")
        return

    # ---- s22 pinned spot guards ----
    print("== s22 spot guards (M29/M34 match or stop) ==")
    umoved = sorted(c for c in UNNAMED if cen22[c]["pres"] == 0)
    spot_ok = (rec["tail"] == S22_TAIL and f"{rec['j']:.4f}" == S22_J
               and umoved == S22_UNNAMED_MOVED
               and (cen22[295]["n"], cen22[295]["ov"]) == S22_C295_NOV
               and (cen22[307]["n"], cen22[307]["ov"]) == S22_C307_NOV
               and s0u[295] == S0_C295_ROWS and s0u[307] == S0_C307_ROWS)
    print(f"s22 tail/J={rec['tail']}/{rec['j']:.4f} "
          f"(want {S22_TAIL}/{S22_J})")
    print(f"s22 unnamed moved={umoved} k={len(umoved)} "
          f"(want {S22_UNNAMED_MOVED})")
    for c, wn in ((295, S22_C295_NOV), (307, S22_C307_NOV)):
        e = cen22[c]
        print(f"s22 c{c}: n/ov={e['n']}/{e['ov']} (want {wn[0]}/{wn[1]})")
    print(f"s0 c295 rows={s0u[295]} (want {S0_C295_ROWS}) "
          f"s0 c307 rows={s0u[307]} (want {S0_C307_ROWS})")
    # named side (fresh ycols from the full pass)
    y0n = {c: sorted(r for r in s0y.get(c, [])) for c in NAMED8}
    y22n = {c: sorted(r for r in rec["ycols"].get(c, [])) for c in NAMED8}
    nmoved = sorted(c for c in NAMED8 if y22n[c] != y0n[c])
    n296 = y22n[296]
    ov296 = len(set(n296) & set(y0n[296]))
    print(f"s22 named moved={nmoved} (want {S22_NAMED_MOVED})")
    print(f"s22 c296: n/ov={len(n296)}/{ov296} "
          f"(want {S22_C296_NOV[0]}/{S22_C296_NOV[1]})")
    spot_ok = spot_ok and nmoved == S22_NAMED_MOVED \
        and (len(n296), ov296) == S22_C296_NOV
    print("spot guards: " + ("OK" if spot_ok else
                             "MISMATCH: STOP, tabled."))
    if not spot_ok:
        return

    # ---- analyzed triplets (fresh loads) + tier-2 guards ----
    print("== analyzed triplets + tier-2 row-list/set guards ==")
    A = analyze(m16d, UNNAMED, s0u)
    T = A["T"]
    dd_bad = sum(1 for s in ANALYZED
                 if int((T[s]["d"][T[s]["mask"]] == 0).sum()) != 0)
    print(f"analyzed delta==0 violations: n={dd_bad} shapes (want 0)")
    print(f"s22 c296 ex={A['ex296']} (want {S22_C296_EX}) "
          f"mi={A['mi296']} (want [])")
    print(f"s22 c295 ex={A['ex295']} (want {S22_C295_EX})")
    print(f"s22 c307 ex={A['ex307']} (want {S22_C307_EX}) "
          f"keep={A['keep307']} (want {S22_C307_KEPT})")
    print(f"s22 priv_rc={A['priv_rc']} (want {sorted(BOT)})")
    print(f"s22 miss_rc={A['miss_rc']} (want [])")
    t2_ok = (dd_bad == 0 and A["ex296"] == S22_C296_EX
             and A["mi296"] == [] and A["ex295"] == S22_C295_EX
             and A["ex307"] == S22_C307_EX
             and A["keep307"] == S22_C307_KEPT
             and sorted(A["priv_rc"]) == sorted(BOT)
             and A["miss_rc"] == []
             and int(A["S"].sum()) == 102
             and f"{A['j22']:.4f}" == S22_J
             and A["named_moved"] == S22_NAMED_MOVED
             and A["unam_moved"] == S22_UNNAMED_MOVED)
    planesP = {int(A["pl"][o]) for o in np.nonzero(A["P"])[0]}
    print(f"s22 moved-site planes={sorted(planesP)} (want [0])")
    t2_ok = t2_ok and planesP == {0}
    print("tier-2 guards: " + ("OK" if t2_ok else
                               "MISMATCH: STOP, tabled."))
    if not t2_ok:
        return

    # ---- s0 P1 (M18 edge guard) + c296-pair value cross-check ----
    print("== s0 P1 + c296-pair value cross-check (M29 match or stop) ==")
    ym0 = split_planes(np.frombuffer(mid0, np.uint8))[0]
    _, qs, dec = p1_gradient(ym0)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    print(f"s0 P1 edges: {estrs} (m18.txt want {M18_P1_EDGE_S0}) "
          f"match={estrs == M18_P1_EDGE_S0}")
    if estrs != M18_P1_EDGE_S0:
        print("P1 edge MISMATCH: STOP, tabled.")
        return
    T22 = T[22]
    a0x = np.frombuffer(v0, np.uint8).astype(np.int16)
    f0x = np.frombuffer(full0, np.uint8).astype(np.int16)
    g0x = a0x - f0x
    a22 = np.frombuffer(T22["v0"], np.uint8).astype(np.int16)
    f22 = np.frombuffer(T22["full"], np.uint8).astype(np.int16)
    g22 = a22 - f22
    pair_ok = True
    for (r, c), w in C296_PAIR_VALS.items():
        o = off_of(r, c)
        ad = int(abs(int(T22["d"][o])))
        ost = "bulk" if mask0[o] else "noncell"
        dc = int(dec[r, c])
        ok = (ad == w["ad"] and ost == "noncell"
              and int(g22[o]) == w["gQ"] and int(g0x[o]) == w["gO"]
              and dc == w["dec"])
        pair_ok = pair_ok and ok
        print(f"c296pair ({r},{c}): ad={ad} (want {w['ad']}) ost={ost} "
              f"gQ/gO={int(g22[o])}/{int(g0x[o])} "
              f"(want {w['gQ']}/{w['gO']}) dec={dc} "
              f"(want {w['dec']}) match={ok}")
    print("pair cross-check: " + ("OK" if pair_ok else
                                  "MISMATCH vs M29: STOP, tabled."))
    if not pair_ok:
        return

    # ---- Tasks 1-2 ----
    print("== Task 1 (s22 census): moved cells + privates + completeness ==")
    t1 = time.time()
    canon = task1_lines(A)
    for ln in canon:
        print(ln)
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")
    print("== Task 2 (s22 attribution): values + geometry + side-by-side ==")
    t1 = time.time()
    t2 = task2_lines(A, dec)
    for ln in t2:
        print(ln)
    print(f"(Task-2 wall: {time.time() - t1:.1f}s)")

    # ---- determinism re-run (Task 1 on s0+22, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+22, second pass) ==")
    A2 = analyze(m16d, UNNAMED, s0u)
    canon2 = task1_lines(A2)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")

    # ---- PNG bottom-cluster map ----
    print("== PNG bottom-cluster map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    im_s, _, _ = flat_to_planes(A["S"])
    im_e296, _, _ = flat_to_planes(A["ex296mask"])
    im_out, _, _ = flat_to_planes(A["outpriv"])
    over[im_s] = np.array([0, 255, 0])        # s22 shared green
    over[im_e296] = np.array([255, 255, 0])   # c296 extras yellow
    over[im_out] = np.array([255, 0, 0])      # outside-col privates red
    p = workd / "m45-clusmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: s22 shared=green c296-extras=yellow "
          "outside-col-privates=red (s0 geometry; Y only)")

    # ---- falsification-bar measurements ----
    print("== falsification-bar measurements ==")
    d22 = T22["d"]
    h_near = h_non = h_dec9 = h_opp = 0
    new_ads = {}
    for o in A["bot_offs"]:
        r, c = int(pr[o]), int(pc[o])
        if mask0[o]:
            if int(abs(int(d0[o]))) in (6, 7):
                h_near += 1
        else:
            h_non += 1
        if int(dec[r, c]) == 9:
            h_dec9 += 1
        if int(g22[o]) * int(g0x[o]) < 0:
            h_opp += 1
        if (r, c) in ((393, 307), (402, 295)):
            new_ads[(r, c)] = int(abs(int(d22[o])))
    h6 = all(v == 8 for v in new_ads.values()) and len(new_ads) == 2
    whole = (sorted(A["priv_rc"]) == sorted(BOT) and not A["miss_rc"])
    print(f"H1_BOTNEAR: bottom near {h_near}/4 "
          f"({h_near / 4:.4f}; bar >=0.50)")
    print(f"H2_BOTSET: bottom noncell-ons0 {h_non}/4 "
          f"({h_non / 4:.4f}; bar >=0.50)")
    print(f"H3_BOTDEC9: bottom dec9 {h_dec9}/4 "
          f"({h_dec9 / 4:.4f}; bar >=0.50)")
    print(f"H4_WHOLESET: priv==BOT and miss-empty: {whole} "
          f"(bar: tier-2 pass)")
    print(f"H5_GAPOPP: bottom opposite-sign gaps {h_opp}/4 "
          f"({h_opp / 4:.4f}; bar >=0.50)")
    print(f"H6_NEWMAG: new privates ad {new_ads}: {h6} "
          f"(bar: both ==8)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=s22-census T2=s22-attribution R=controls")


if __name__ == "__main__":
    main()


