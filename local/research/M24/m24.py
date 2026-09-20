#!/usr/bin/env python3
"""M24 K45+ near-hit mass: residual-sign tables + sub-rounding fits (offline).

Usage: m24.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text goes
to stdout (redirect to WORK_DIR/m24.txt); PNG residual-sign map to
WORK_DIR (evidence copy iff discriminating per DESIGN.md, decided
at report time).

Tasks (see DESIGN.md, recorded before running):
  1: residual-sign tables (r = d - K45+(g), signed)
  2: sub-rounding fits (fixed 4-list, exact-hit scoring + transfer)
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
M20_TAIL = {"s0": 102, "m15": 134}
M20_TAIL_SUB = {"s0": (28, 74), "m15": (50, 84)}  # (8-15, 16+)
M20_TAIL_MAX = {"s0": 47, "m15": 48}
M19_NEGRATE = {"s0": 0.8093, "m15": 0.8019}  # P(d>0) on cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
M18_P1_EDGES = {"s0": "0 1 2 2 4 6 8 12 18 29 176",
                "m15": "0 0 1 2 4 6 9 13 19 30 181"}
STREAK_COLS = (257, 277, 296, 301, 321, 340, 341, 342, 343)
XSHAPE_IDS = (1, 2, 733)  # DESIGN.md: M23's 3 verbatim
CORR_IDS = ["SIGN", "FRAC", "PARITY", "POS"]
LEVEL_NAMES = {"SIGN": ["neg", "pos"],
               "FRAC": ["LO", "HI"],
               "PARITY": ["even", "odd"],
               "POS": ["b0d0", "b0d1", "b1d0", "b1d1", "b2d0", "b2d1"]}
M23_K45 = {"s0": (14, 32), "m15": (15, 49)}  # (exact, near)


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
BAND_OF_ROW = np.zeros(H, np.int32)
for _bi, _rows in enumerate(BAND_ROWS):
    BAND_OF_ROW[_rows] = _bi


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


# ---- fixed correction machinery (DESIGN.md list, exact integer arith) ----

def k45mag(a: np.ndarray) -> np.ndarray:
    return (9 * np.abs(a) + 10) // 20


def k45pred(g: np.ndarray) -> np.ndarray:
    s = np.sign(g).astype(np.int64)
    return (s * k45mag(g)).astype(np.int16)


def frac_hi(g: np.ndarray) -> np.ndarray:
    """HI level of frac(0.45*g): ((9g) mod 20) >= 10, exact integers.

    NumPy % with a positive divisor yields the non-negative remainder.
    """
    return (((9 * g) % 20) >= 10).astype(np.int32)


def rhalf_away_mean(s: int, n: int) -> int:
    """round-half-away-from-zero of s/n (n>0), exact integer arithmetic."""
    if s >= 0:
        return (2 * s + n) // (2 * n)
    return -((2 * (-s) + n) // (2 * n))


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


def clamp1(v: int) -> int:
    return max(-1, min(1, v))


def site_cells(off: np.ndarray, dec: np.ndarray, rr: np.ndarray,
               cc: np.ndarray, pl: np.ndarray) -> np.ndarray:
    """POS cell id = band*2 + (dec==9); U/V via co-located Y (r,2c)."""
    ycol = np.where(pl == 0, cc, 2 * cc)
    d9 = (dec[rr[off], ycol[off]] == 9).astype(np.int32)
    return BAND_OF_ROW[rr[off]] * 2 + d9


def corr_levels(cid: str, gt: np.ndarray, off: np.ndarray,
                dec: np.ndarray, rr: np.ndarray, cc: np.ndarray,
                pl: np.ndarray) -> np.ndarray:
    """Level id per site for a fixed correction split (DESIGN.md)."""
    if cid == "SIGN":
        return np.where(gt < 0, 0, np.where(gt > 0, 1, 2))
    if cid == "FRAC":
        return frac_hi(gt)
    if cid == "PARITY":
        return (np.abs(gt) % 2).astype(np.int32)
    if cid == "POS":
        return site_cells(off, dec, rr, cc, pl)
    raise ValueError(cid)


def fit_corr(cid: str, lv: np.ndarray, r: np.ndarray):
    """Per-level c = clamped median of r; empties -> global clamped median.

    SIGN level 2 (g==0) is fixed c=0 per DESIGN.md.
    """
    nlev = {"SIGN": 2, "FRAC": 2, "PARITY": 2, "POS": 6}[cid]
    fb = clamp1(int_median(r)) if len(r) else 0
    c = {}
    empt = []
    for lev in range(nlev):
        vv = r[lv == lev]
        if len(vv):
            c[lev] = clamp1(int_median(vv))
        else:
            empt.append(lev)
            c[lev] = fb
    if cid == "SIGN":
        c[2] = 0
    return {"c": c, "fallback": fb, "empties": empt}


def apply_corr(cid: str, gt: np.ndarray, off: np.ndarray, dec: np.ndarray,
               rr: np.ndarray, cc: np.ndarray, pl: np.ndarray,
               fit) -> np.ndarray:
    """delta' = K45+(g) + c(level) with a fitted constant map."""
    lv = corr_levels(cid, gt, off, dec, rr, cc, pl)
    cc = np.array([fit["c"].get(int(L), fit["fallback"]) for L in lv],
                  np.int16)
    return (k45pred(gt).astype(np.int64) + cc.astype(np.int64)).astype(
        np.int16)


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


def rclass_counts(r: np.ndarray):
    """(n_{-1}, n_0, n_{+1}, n_other) with other = |r|>1."""
    r = r.astype(np.int64)
    return (int((r == -1).sum()), int((r == 0).sum()),
            int((r == 1).sum()), int((np.abs(r) > 1).sum()))


def rstat_line(prefix: str, r: np.ndarray) -> str:
    m1, z, p1, other = rclass_counts(r)
    r = r.astype(np.int64)
    return (f"{prefix}: n={len(r)} m1={m1} z={z} p1={p1} other={other} "
            f"mean={float(r.mean()) if len(r) else 0:.3f} "
            f"amean={float(np.abs(r).mean()) if len(r) else 0:.3f} "
            f"rlist: {exact_counts(r)}")


def score_corr_lines(prefix: str, d: np.ndarray, preds: dict):
    """Exact-hit scoring lines per correction; preds cid->array."""
    L = []
    hits = {}
    for cid in CORR_IDS:
        p = preds[cid]
        err = p.astype(np.int64) - d.astype(np.int64)
        ae = np.abs(err)
        nh = int((ae == 0).sum())
        nn = int((ae == 1).sum())
        miss = ae[(ae != 0) & (ae != 1)]
        bins = [(2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        L.append(f"{prefix} {cid}: n={len(d)} hits={nh} "
                 f"rate={nh / len(d):.4f} near={nn} "
                 f"nearrate={nn / len(d):.4f} miss|err| "
                 f"{coarse_hist(miss, bins)}")
        L.append(f"{prefix} {cid} errvalues: {exact_counts(ae)}")
        hits[cid] = nh
    return L, hits


def task1_resid_lines(tag, v0b, midb, fullb, synth, ym, rr, cc, pl):
    """Task 1 residual tables for one frame; returns (lines, art)."""
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
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    g = (a - b).astype(np.int16)  # signed gap
    off = np.flatnonzero(tail)
    dt = delta[tail].astype(np.int64)
    gt = g[tail].astype(np.int64)
    agt = np.abs(gt)

    # K45+ repro guard (M23 scores must match exactly or stop)
    k45 = k45pred(gt).astype(np.int64)
    ae0 = np.abs(k45 - dt)
    h0, n0 = int((ae0 == 0).sum()), int((ae0 == 1).sum())
    want_h, want_n = M23_K45[tag]
    L.append(f"{tag} K45+ repro: hits={h0} (want {want_h}) near={n0} "
             f"(want {want_n})")
    L.append(f"{tag} K45+ errvalues: {exact_counts(ae0)}")
    if (h0, n0) != (want_h, want_n):
        L.append(f"{tag} K45+ SCORE MISMATCH vs M23: STOP, tabled.")
        return L, None
    r = (dt - k45).astype(np.int64)  # signed residual

    # P1 deciles (POS cells need them; guard edges like M23)
    mag, qs, dec = p1_gradient(ym)
    estrs = " ".join(f"{q:.0f}" for q in qs)
    L.append(f"{tag} P1 edges: {estrs} (m18.txt want {M18_P1_EDGES[tag]}) "
             f"match={estrs == M18_P1_EDGES[tag]}")

    # 1.1: residual-sign joint, one table per split
    for cid in CORR_IDS:
        lv = corr_levels(cid, gt, off, dec, rr, cc, pl)
        for lev, nm in enumerate(LEVEL_NAMES[cid]):
            L.append(rstat_line(f"{tag} rsjoint {cid} {nm}", r[lv == lev]))
        if cid == "SIGN":
            L.append(rstat_line(f"{tag} rsjoint SIGN zero(fallback)",
                                r[lv == 2]))

    # 1.2: (gap, r) joint per M23 gap bin
    for lo, hi in ((16, 31), (32, 63), (64, 1 << 15)):
        sel = (agt >= lo) & (agt <= hi)
        lab = f"{lo}-{hi}" if hi < 999 else "64+"
        L.append(rstat_line(f"{tag} gapbin {lab}", r[sel]))

    # 1.3: position join — streak columns + band x decile note
    is_y = pl[off] == 0
    for ccol in STREAK_COLS:
        sel = is_y & (cc[off] == ccol)
        rrws = rr[off[sel]]
        L.append(rstat_line(
            f"{tag} streakcol c={ccol} rows="
            f"[{int(rrws.min()) if len(rrws) else -1},"
            f"{int(rrws.max()) if len(rrws) else -1}]", r[sel]))
    selo = is_y & ~np.isin(cc[off], np.array(STREAK_COLS))
    L.append(rstat_line(f"{tag} streakcol other", r[selo]))
    n_nony = int((~is_y).sum())
    L.append(f"{tag} streakcol nonY-tail n={n_nony} (M23 want 0)")
    L.append(f"{tag} bandxdec: = rsjoint POS table above (referenced, "
             f"not re-emitted)")

    # H-helper views (formatted re-views of the same tables; bars scored
    # at report time)
    for cid in CORR_IDS:
        lv = corr_levels(cid, gt, off, dec, rr, cc, pl)
        for lev, nm in enumerate(LEVEL_NAMES[cid]):
            vv = r[lv == lev].astype(np.int64)
            pm1 = vv[np.abs(vv) == 1]
            if len(pm1):
                pur = max(int((pm1 == 1).sum()),
                          int((pm1 == -1).sum())) / len(pm1)
            else:
                pur = 0.0
            L.append(f"{tag} h3view {cid} {nm}: npm1={len(pm1)} "
                     f"purity={pur:.4f}")
    npm1_all = int((np.abs(r) == 1).sum())
    for lo, hi in ((16, 31), (32, 63), (64, 1 << 15)):
        sel = (agt >= lo) & (agt <= hi)
        lab = f"{lo}-{hi}" if hi < 999 else "64+"
        k = int((np.abs(r[sel]) == 1).sum())
        L.append(f"{tag} h4view gapbin {lab}: npm1={k} "
                 f"share={k / npm1_all if npm1_all else 0:.4f}")
    for ccol in STREAK_COLS:
        sel = is_y & (cc[off] == ccol)
        pm1 = r[sel][np.abs(r[sel]) == 1]
        if len(pm1):
            coh = bool(((pm1 == 1).all() or (pm1 == -1).all()))
        else:
            coh = False
        L.append(f"{tag} h6view streakcol c={ccol}: npm1={len(pm1)} "
                 f"single_sign={coh}")

    art = {"n": n, "nt": nt, "mask": mask, "delta": delta, "tail": tail,
           "off": off, "dt": dt, "gt": gt, "r": r, "dec": dec, "g": g,
           "k45": k45}
    return L, art


def build_preds(art, fits, rr, cc, pl):
    """Correction arrays for a scored frame given fitted constant maps."""
    preds = {}
    for cid in CORR_IDS:
        preds[cid] = apply_corr(cid, art["gt"], art["off"], art["dec"],
                                rr, cc, pl, fits[cid])
    return preds


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0)
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
        print("MISMATCH vs M17-M23 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== Task 1: residual tables s0 ==")
    t1 = time.time()
    L0, art0 = task1_resid_lines("s0", v0, mid, full, b0, ym0, rr, cc, pl)
    for ln in L0:
        print(ln)
        canon.append(ln)
    print(f"(Task-1 s0 wall: {time.time() - t1:.1f}s)")
    if art0 is None:
        print("cell-7/tail/K45+ guard failed on s0: STOP before Task 1.1.")
        return
    print("== Task 1: residual tables m15 ==")
    t1 = time.time()
    L15, art15 = task1_resid_lines("m15", v015, mid15, full15, b15, ym15,
                                   rr, cc, pl)
    for ln in L15:
        print(ln)
    print(f"(Task-1 m15 wall: {time.time() - t1:.1f}s)")
    if art15 is None:
        print("cell-7/tail/K45+ guard failed on m15: STOP before Task 1.1.")
        return
    print(f"self jaccard s0={jaccard(art0['tail'], art0['tail']):.4f} "
          f"(want 1.0) m15={jaccard(art15['tail'], art15['tail']):.4f}")

    # ---- fits ----
    print("== Task 2 fits ==")
    fits0, fits15 = {}, {}
    for cid in CORR_IDS:
        lv0 = corr_levels(cid, art0["gt"], art0["off"], art0["dec"], rr,
                          cc, pl)
        lv15 = corr_levels(cid, art15["gt"], art15["off"], art15["dec"],
                           rr, cc, pl)
        fits0[cid] = fit_corr(cid, lv0, art0["r"])
        fits15[cid] = fit_corr(cid, lv15, art15["r"])
        print(f"fit {cid} s0: "
              + " ".join(f"{LEVEL_NAMES[cid][lev]}={fits0[cid]['c'][lev]}"
                         for lev in sorted(fits0[cid]["c"])
                         if lev < len(LEVEL_NAMES[cid]))
              + f" fallback={fits0[cid]['fallback']} "
              f"empties={fits0[cid]['empties']}")
        print(f"fit {cid} m15: "
              + " ".join(f"{LEVEL_NAMES[cid][lev]}={fits15[cid]['c'][lev]}"
                         for lev in sorted(fits15[cid]["c"])
                         if lev < len(LEVEL_NAMES[cid]))
              + f" fallback={fits15[cid]['fallback']} "
              f"empties={fits15[cid]['empties']}")

    # ---- Task 2.1: same-frame scoring ----
    print("== Task 2.1: same-frame scores s0 ==")
    preds0 = build_preds(art0, fits0, rr, cc, pl)
    LS0, H0 = score_corr_lines("score s0", art0["dt"], preds0)
    for ln in LS0:
        print(ln)
    print("== Task 2.1: same-frame scores m15 ==")
    preds15 = build_preds(art15, fits15, rr, cc, pl)
    LS15, H15 = score_corr_lines("score m15", art15["dt"], preds15)
    for ln in LS15:
        print(ln)

    # ---- best correction (DESIGN.md rule) + residual ----
    order = {cid: i for i, cid in enumerate(CORR_IDS)}
    best = sorted(CORR_IDS,
                  key=lambda p: (-H0[p], -H15[p], order[p]))[0]
    print(f"best correction: {best} (s0hits={H0[best]} "
          f"m15hits={H15[best]} pooled={H0[best] + H15[best]})")
    for tag, art, pr in (("s0", art0, preds0), ("m15", art15, preds15)):
        resid = np.abs(art["dt"].astype(np.int64)
                       - pr[best].astype(np.int64))
        bins = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        print(f"residual {tag} best={best}: {coarse_hist(resid, bins)}")
        print(f"residual {tag} best={best} values: {exact_counts(resid)}")
        print(f"explained {tag}: {int((resid == 0).sum())}/{art['nt']} "
              f"standing={int((resid != 0).sum())}")

    # ---- separation view: post-best-correction hit rates per level of
    # every split on s0 (PNG evidence-copy decision input) ----
    print("== separation view (s0, post-best-correction hits by level) ==")
    hit0 = (art0["dt"].astype(np.int64)
            - preds0[best].astype(np.int64)) == 0
    for cid in CORR_IDS:
        lv = corr_levels(cid, art0["gt"], art0["off"], art0["dec"], rr,
                         cc, pl)
        for lev, nm in enumerate(LEVEL_NAMES[cid]):
            sel = lv == lev
            hh = int(hit0[sel].sum())
            print(f"separation s0 {cid} {nm}: n={int(sel.sum())} "
                  f"hits={hh} rate={hh / sel.sum() if sel.sum() else 0:.4f}")

    # ---- Task 2.2: cross-frame both directions ----
    print("== Task 2.2: fit-s0 score-m15 ==")
    pxf_0_15 = build_preds(art15, fits0, rr, cc, pl)
    LX1, HX1 = score_corr_lines("xframe fit-s0/score-m15", art15["dt"],
                                pxf_0_15)
    for ln in LX1:
        print(ln)
    print("== Task 2.2: fit-m15 score-s0 ==")
    pxf_15_0 = build_preds(art0, fits15, rr, cc, pl)
    LX2, HX2 = score_corr_lines("xframe fit-m15/score-s0", art0["dt"],
                                pxf_15_0)
    for ln in LX2:
        print(ln)

    # ---- Task 2.3: cross-shape (shapes 1, 2, 733; s0 constants) ----
    print("== Task 2.3: cross-shape, best correction + s0 constants ==")
    for s in XSHAPE_IDS:
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        yms = split_planes(np.frombuffer(mm, np.uint8))[0]
        sp = interior_sites(vv, mm, ff, bl)
        tk, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        aa = np.frombuffer(vv, np.uint8).astype(np.int16)
        bb = np.frombuffer(ff, np.uint8).astype(np.int16)
        gg = (aa - bb).astype(np.int16)
        offs = np.flatnonzero(tk)
        dd = sp["delta"][tk].astype(np.int64)
        ggg = gg[tk].astype(np.int64)
        _, _, decs = p1_gradient(yms)
        pv = apply_corr(best, ggg, offs, decs, rr, cc, pl, fits0[best])
        err = pv.astype(np.int64) - dd
        ae = np.abs(err)
        nh = int((ae == 0).sum())
        nn = int((ae == 1).sum())
        miss = ae[(ae != 0) & (ae != 1)]
        bins = [(2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        print(f"xshape {s}: best={best} tailn={len(dd)} hits={nh} "
              f"rate={nh / len(dd) if len(dd) else 0:.4f} near={nn} "
              f"miss|err| {coarse_hist(miss, bins)}")
        print(f"xshape {s}: errvalues: {exact_counts(ae)}")
        print(f"xshape {s}: jacc vs s0={jaccard(tk, art0['tail']):.4f} "
              f"(M22 table) vs m15={jaccard(tk, art15['tail']):.4f}")

    # ---- determinism re-run (Task 1 on s0, canonical text) ----
    print("== determinism re-run (Task 1 on s0, second pass) ==")
    L0b, art0b = task1_resid_lines("s0", v0, mid, full, b0, ym0, rr, cc,
                                   pl)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0b is not None and art0['n'] == art0b['n']}"
          f" tail counts identical="
          f"{art0b is not None and art0['nt'] == art0b['nt']}")

    # ---- PNG residual-sign map (work dir; evidence copy iff per rule) ----
    print("== PNG residual-sign map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    hit_y = np.zeros((H, W), bool)
    p1_y = np.zeros((H, W), bool)
    m1_y = np.zeros((H, W), bool)
    other_y = np.zeros((H, W), bool)
    for o, e in zip(art0["off"], art0["r"]):
        if pl[o] == 0:
            if e == 0:
                hit_y[rr[o], cc[o]] = True
            elif e == 1:
                p1_y[rr[o], cc[o]] = True
            elif e == -1:
                m1_y[rr[o], cc[o]] = True
            else:
                other_y[rr[o], cc[o]] = True
    over[other_y] = np.array([255, 0, 0])     # |r|>1 red
    over[m1_y] = np.array([0, 255, 255])      # r=-1 cyan
    over[p1_y] = np.array([255, 255, 0])      # r=+1 yellow
    over[hit_y] = np.array([0, 255, 0])       # r=0 green
    p = workd / "m24-rsignmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: green=r0 n={int(hit_y.sum())} "
          f"yellow=r+1 n={int(p1_y.sum())} cyan=r-1 n={int(m1_y.sum())} "
          f"red=other n={int(other_y.sum())} (tail Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=residual-tables T2=subrounding-fits R=controls")


if __name__ == "__main__":
    main()
