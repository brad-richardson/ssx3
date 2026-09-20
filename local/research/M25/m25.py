#!/usr/bin/env python3
"""M25 within-streak-column delta profiles: per-row gradients + column fits.

Usage: m25.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text goes
to stdout (redirect to WORK_DIR/m25.txt); PNG column-profile map to
WORK_DIR (evidence copy iff discriminating per DESIGN.md, decided
at report time).

Tasks (see DESIGN.md, recorded before running):
  1: per-row delta profiles + shape stats + cross-frame match
  2: column-gradient fits (fixed 3-list, exact-hit scoring + transfer)
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
FIT_IDS = ["CONST", "LINEAR", "SIGNC"]
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


# ---- fixed fit machinery (DESIGN.md list, exact integer arith + OLS) ----

def k45mag(a: np.ndarray) -> np.ndarray:
    return (9 * np.abs(a) + 10) // 20


def k45pred(g: np.ndarray) -> np.ndarray:
    s = np.sign(g).astype(np.int64)
    return (s * k45mag(g)).astype(np.int16)


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


def rhalf(x: float) -> int:
    """Round-half-away-from-zero of a float."""
    if x >= 0:
        return int(math.floor(x + 0.5))
    return -int(math.floor(-x + 0.5))


def linfit(rows: np.ndarray, deltas: np.ndarray):
    """OLS delta ~ a + b*row (float64). Returns (a, b) or None if
    degenerate (n<2 or Sxx==0)."""
    n = len(rows)
    if n < 2:
        return None
    r = rows.astype(np.float64)
    d = deltas.astype(np.float64)
    rbar = r.mean()
    dbar = d.mean()
    sxx = float(((r - rbar) ** 2).sum())
    if sxx == 0.0:
        return None
    sxy = float(((r - rbar) * (d - dbar)).sum())
    b = sxy / sxx
    return (float(dbar - b * rbar), float(b))


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
    """Task 1.1+1.2 profile tables for one frame; returns (lines, art)."""
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
                           "d": ddc[ord_].astype(np.int64),
                           "g": gt[sel][ord_].astype(np.int64)}
    named_n = sum(len(profs[c]["rows"]) for c in NAMED_COLS)
    L.append(f"{tag} named-col tail bytes n={named_n} "
             f"(want {NAMED_N[tag]})")
    if not colok or named_n != NAMED_N[tag]:
        L.append(f"{tag} COLUMN MEMBERSHIP MISMATCH vs M22/M23: "
                 f"STOP, tabled.")
        return L, None
    n_nony = int((~is_y).sum())
    L.append(f"{tag} nonY-tail n={n_nony} (M23 want 0)")

    # 1.1: per-row delta lists + holes.
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

    # 1.2: column shape stats.
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
        L.append(f"{tag} h6view c={ccol}: "
                 f"range={int(dd.max() - dd.min()) if nn else 0} "
                 f"nge4={nn >= 4}")

    art = {"n": n, "nt": nt, "mask": mask, "delta": delta, "tail": tail,
           "off": off, "dt": dt, "gt": gt, "g": g, "profs": profs}
    return L, art


def xframe_match_lines(art0, art15):
    """Task 1.3: per-column s0-vs-m15 profile match."""
    L = []
    shared_all, agree_all = 0, 0
    for ccol in NAMED_COLS:
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


# ---- Task 2 fits ----

def fit_frame(art):
    """Fit all 3 fixed fits on one frame's named-column profiles."""
    pr = art["profs"]
    alld = np.concatenate([pr[c]["d"] for c in NAMED_COLS])
    fb = int_median(alld)
    gmean = float(alld.mean())
    const, linear, signc = {}, {}, {}
    empt, linfb = [], []
    for ccol in NAMED_COLS:
        dd = pr[ccol]["d"]
        if len(dd):
            const[ccol] = int_median(dd)
        else:
            empt.append(ccol)
            const[ccol] = fb
        lf = linfit(pr[ccol]["rows"], dd) if len(dd) else None
        if lf is None:
            linfb.append(ccol)
            linear[ccol] = None
        else:
            linear[ccol] = lf
        if len(dd):
            mu = float(dd.mean())
            signc[ccol] = 1 if mu > 0 else (-1 if mu < 0 else 1)
            if mu == 0:
                empt.append(f"sign0@{ccol}")
        else:
            signc[ccol] = 1 if gmean >= 0 else -1
    return {"const": const, "linear": linear, "signc": signc,
            "fallback": fb, "empties": empt, "linfb": linfb}


def apply_fit(fid, fit, art):
    """Predictions over the scored frame's named-column sites (row order
    per column, columns in NAMED_COLS order)."""
    pr = art["profs"]
    out = {}
    for ccol in NAMED_COLS:
        dd = pr[ccol]
        nn = len(dd["rows"])
        if fid == "CONST":
            out[ccol] = np.full(nn, fit["const"][ccol], np.int64)
        elif fid == "LINEAR":
            lf = fit["linear"][ccol]
            if lf is None:
                out[ccol] = np.full(nn, fit["const"][ccol], np.int64)
            else:
                a, b = lf
                out[ccol] = np.array(
                    [rhalf(a + b * float(r)) for r in dd["rows"]],
                    np.int64)
        elif fid == "SIGNC":
            mag = (9 * np.abs(dd["g"]) + 10) // 20
            out[ccol] = (fit["signc"][ccol] * mag).astype(np.int64)
        else:
            raise ValueError(fid)
    return out


def named_truth(art):
    return {c: art["profs"][c]["d"].astype(np.int64) for c in NAMED_COLS}


def score_fit_lines(prefix, art, preds):
    """Exact-hit scoring lines per fit; preds fid->{col:array}."""
    L = []
    truth = named_truth(art)
    hits = {}
    for fid in FIT_IDS:
        tall, pall = [], []
        for ccol in NAMED_COLS:
            tall.append(truth[ccol])
            pall.append(preds[fid][ccol])
        t = np.concatenate(tall).astype(np.int64)
        p = np.concatenate(pall).astype(np.int64)
        ae = np.abs(p - t)
        nh = int((ae == 0).sum())
        nn = int((ae == 1).sum())
        miss = ae[(ae != 0) & (ae != 1)]
        bins = [(2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        L.append(f"{prefix} {fid}: n={len(t)} hits={nh} "
                 f"rate={nh / len(t):.4f} near={nn} "
                 f"nearrate={nn / len(t):.4f} miss|err| "
                 f"{coarse_hist(miss, bins)}")
        L.append(f"{prefix} {fid} errvalues: {exact_counts(ae)}")
        ch = " ".join(
            f"c{c}={int(((preds[fid][c].astype(np.int64) - truth[c]) == 0).sum())}"
            f"/{len(truth[c])}" for c in NAMED_COLS)
        L.append(f"{prefix} {fid} colhits: {ch}")
        hits[fid] = nh
    return L, hits


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
        print("MISMATCH vs M17-M24 baselines: STOP, tabled.")
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
    print("== Task 1: profiles m15 ==")
    t1 = time.time()
    L15, art15 = task1_profile_lines("m15", v015, mid15, full15, b15, rr,
                                     cc, pl)
    for ln in L15:
        print(ln)
    print(f"(Task-1 m15 wall: {time.time() - t1:.1f}s)")
    if art15 is None:
        print("cell-7/tail/column guard failed on m15: STOP.")
        return
    print(f"self jaccard s0={jaccard(art0['tail'], art0['tail']):.4f} "
          f"(want 1.0) m15={jaccard(art15['tail'], art15['tail']):.4f}")

    print("== Task 1.3: cross-frame profile match ==")
    for ln in xframe_match_lines(art0, art15):
        print(ln)

    # ---- fits ----
    print("== Task 2 fits ==")
    fit0 = fit_frame(art0)
    fit15 = fit_frame(art15)
    for tag, fit in (("s0", fit0), ("m15", fit15)):
        cl = " ".join(f"c{c}={fit['const'][c]}" for c in NAMED_COLS)
        print(f"fit {tag} CONST: {cl} fallback={fit['fallback']} "
              f"empties={fit['empties']}")
        ll = " ".join(
            f"c{c}=" + (f"a={fit['linear'][c][0]:.4f},"
                        f"b={fit['linear'][c][1]:.4f}"
                        if fit['linear'][c] is not None else "CONST-fb")
            for c in NAMED_COLS)
        print(f"fit {tag} LINEAR: {ll} linfb={fit['linfb']}")
        sl = " ".join(f"c{c}={fit['signc'][c]:+d}" for c in NAMED_COLS)
        print(f"fit {tag} SIGNC: {sl}")

    # ---- Task 2.1: same-frame scoring ----
    print("== Task 2.1: same-frame scores s0 ==")
    preds0 = {fid: apply_fit(fid, fit0, art0) for fid in FIT_IDS}
    LS0, H0 = score_fit_lines("score s0", art0, preds0)
    for ln in LS0:
        print(ln)
    print("== Task 2.1: same-frame scores m15 ==")
    preds15 = {fid: apply_fit(fid, fit15, art15) for fid in FIT_IDS}
    LS15, H15 = score_fit_lines("score m15", art15, preds15)
    for ln in LS15:
        print(ln)

    # ---- best fit (DESIGN.md rule) + residual ----
    order = {fid: i for i, fid in enumerate(FIT_IDS)}
    best = sorted(FIT_IDS,
                  key=lambda p: (-H0[p], -H15[p], order[p]))[0]
    print(f"best fit: {best} (s0hits={H0[best]} "
          f"m15hits={H15[best]} pooled={H0[best] + H15[best]})")
    for tag, art, pr in (("s0", art0, preds0), ("m15", art15, preds15)):
        truth = named_truth(art)
        t = np.concatenate([truth[c] for c in NAMED_COLS])
        p = np.concatenate([pr[best][c] for c in NAMED_COLS])
        resid = np.abs(t.astype(np.int64) - p.astype(np.int64))
        bins = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 1 << 15)]
        print(f"residual {tag} best={best}: {coarse_hist(resid, bins)}")
        print(f"residual {tag} best={best} values: {exact_counts(resid)}")
        print(f"explained {tag}: {int((resid == 0).sum())}/{art['nt']} "
              f"tail standing={int((resid != 0).sum())} "
              f"(named-col scope; outside-named untabled here)")

    # ---- Task 2.2: cross-frame both directions ----
    print("== Task 2.2: fit-s0 score-m15 ==")
    pxf_0_15 = {fid: apply_fit(fid, fit0, art15) for fid in FIT_IDS}
    LX1, HX1 = score_fit_lines("xframe fit-s0/score-m15", art15, pxf_0_15)
    for ln in LX1:
        print(ln)
    print("== Task 2.2: fit-m15 score-s0 ==")
    pxf_15_0 = {fid: apply_fit(fid, fit15, art0) for fid in FIT_IDS}
    LX2, HX2 = score_fit_lines("xframe fit-m15/score-s0", art0, pxf_15_0)
    for ln in LX2:
        print(ln)

    # ---- determinism re-run (Task 1 on s0, canonical text) ----
    print("== determinism re-run (Task 1 on s0, second pass) ==")
    L0b, art0b = task1_profile_lines("s0", v0, mid, full, b0, rr, cc, pl)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(L0b).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={art0b is not None and art0['n'] == art0b['n']}"
          f" tail counts identical="
          f"{art0b is not None and art0['nt'] == art0b['nt']}")

    # ---- PNG column-profile map (work dir; evidence copy iff per rule) ----
    print("== PNG column-profile map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    truth0 = named_truth(art0)
    hit_y = np.zeros((H, W), bool)
    near_y = np.zeros((H, W), bool)
    miss_y = np.zeros((H, W), bool)
    for ccol in NAMED_COLS:
        pr = art0["profs"][ccol]
        t = truth0[ccol].astype(np.int64)
        p = preds0["CONST"][ccol].astype(np.int64)
        ae = np.abs(p - t)
        for r, e in zip(pr["rows"], ae):
            if e == 0:
                hit_y[int(r), ccol] = True
            elif e == 1:
                near_y[int(r), ccol] = True
            else:
                miss_y[int(r), ccol] = True
    over[miss_y] = np.array([255, 0, 0])      # CONST miss red
    over[near_y] = np.array([255, 255, 0])    # CONST near yellow
    over[hit_y] = np.array([0, 255, 0])       # CONST hit green
    p = workd / "m25-colmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print(f"legend: green=CONST-hit n={int(hit_y.sum())} "
          f"yellow=CONST-near n={int(near_y.sum())} "
          f"red=CONST-miss n={int(miss_y.sum())} "
          f"(s0 named-col tail Y only)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=column-profiles T2=column-fits R=controls")


if __name__ == "__main__":
    main()
