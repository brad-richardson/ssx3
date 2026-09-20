#!/usr/bin/env python3
"""M48 shape-734 triple move: dest-row listing + value table (offline).

Usage: m48.py M16_DIR M15_DIR M28TSV M34TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m28/m34-census.tsv (FULL TSV guards); raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text
goes to stdout (redirect to WORK_DIR/m48.txt); PNG collision map
to WORK_DIR (evidence copy iff the DESIGN.md rule meets, decided
at report time).

Tasks (see DESIGN.md, recorded before running):
  1: 734 wipe reproduction (wipe + dest + displacement tables)
  2: full-set value table (wiped + dest + collision tables)
  3: controls (control.py) + determinism + shas + Model-0 recompute
Tables, no verdicts.
"""
import hashlib
import statistics
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
M19_INTERIOR_S0 = 2475
M20_TAIL_S0 = 102
M20_TAIL_S0_SUB = (28, 74)  # (8-15, 16+)
M20_TAIL_S0_MAX = 47
M19_POSRATE_S0 = 0.8093  # P(d>0) on s0 cell 7
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
FOLD_WANT = "6c906897a3321e78fcc480e646353f833e0c88424ae397f8f7b346e61fd423b1"
NAMED8 = [257, 277, 296, 301, 321, 340, 342, 343]
S0_ROWS = {
    257: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    277: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    296: [24, 25, 26, 27, 28, 31, 32, 33, 34],
    301: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
    321: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    340: [24, 25, 26, 27, 31, 32, 33, 34],
    342: [27, 28, 29, 34, 35],
    343: [26, 27],
}
S0_MED = {c: statistics.median(v) for c, v in S0_ROWS.items()}
M28_MOVERS = [9, 22, 708, 709, 710, 711, 731, 732, 733, 734]
S734 = {"tail": 94, "j": "0.8846", "moved": [340, 342, 343]}
DEST_PIN = {"rows": [26, 33], "adQ": [21, 11], "adO": [3, 5],
            "gQ": [-50, -26], "gO": [-8, -13],
            "offs": [33964, 42924]}
DISP_PIN = {340: {"dest": 342, "off": 2, "rshift": 0.5, "minshift": 2},
            343: {"dest": 342, "off": -1, "rshift": 3.0, "minshift": 0}}
S0U_PIN = {
    38: [215], 292: [400], 293: [405], 298: [28, 29, 34, 35],
    307: [404], 311: [296, 297, 298, 299], 312: [299, 300, 301],
    313: [274, 275, 276, 292],
    314: [269, 276, 277, 278, 287, 288, 289],
    315: [266, 267, 268, 273, 274, 275, 276], 316: [264],
    332: [295, 304], 372: [221],
}
PUREPRIV_PIN = [54, 145, 259, 279, 295, 299, 303, 310, 318, 322,
                323, 327, 328, 336, 337, 339, 351, 602, 611, 620]
UNNAMED_PIN = sorted(list(S0U_PIN) + PUREPRIV_PIN)
PNAME = ["Y", "U", "V"]


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
    import re
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
    """Tail-Y column -> sorted rows over the full Y column space."""
    out = {}
    for o in np.nonzero(t & (pl == 0))[0]:
        out.setdefault(int(pc[o]), []).append(int(pr[o]))
    return {c: sorted(v) for c, v in out.items()}


def priv_y_cols(priv: np.ndarray, pl, pr, pc):
    """Group private-mask Y sites by column -> {col: sorted rows}."""
    out = {}
    for o in np.nonzero(priv & (pl == 0))[0]:
        out.setdefault(int(pc[o]), []).append(int(pr[o]))
    return {c: sorted(v) for c, v in out.items()}


def census_of_shape(colrows):
    """Per-named-column presence: exact-match rule (DESIGN.md pinned)."""
    out = {}
    for c in NAMED8:
        rs, r0 = colrows[c], S0_ROWS[c]
        ov = len(set(rs) & set(r0))
        out[c] = {"n": len(rs), "ov": ov,
                  "pres": 1 if rs == r0 else 0,
                  "miss": len(r0) - ov, "extra": len(rs) - ov}
    return out


def census_unnamed_of(colrows, s0u):
    """Per-unnamed-column presence over universe s0u (exact-match rule)."""
    out = {}
    for c, r0 in s0u.items():
        rs = colrows.get(c, [])
        ov = len(set(rs) & set(r0))
        miss, extra = len(r0) - ov, len(rs) - ov
        out[c] = {"n": len(rs), "ov": ov,
                  "pres": 1 if rs == r0 else 0,
                  "miss": miss, "extra": extra, "delta": miss + extra}
    return out


def assign_one(c: int, privcols):
    """Displacement assignment for moved column c (M28 pinned)."""
    cands = {col: rows for col, rows in privcols.items()
             if len(rows) >= 2}
    if not cands:
        return {"dest": None, "off": None, "rshift": None,
                "minshift": None, "status": "no-cand", "npriv": 0}
    s0 = set(S0_ROWS[c])
    best = min(cands, key=lambda col: (abs(col - c),
                                      -len(set(cands[col]) & s0), col))
    prows = cands[best]
    return {"dest": best, "off": best - c,
            "rshift": statistics.median(prows) - S0_MED[c],
            "minshift": min(prows) - min(S0_ROWS[c]),
            "status": "ok", "npriv": len(prows)}


def attrib_lines(tag, priv, miss, shared, dA, mA, dB, mB,
                 v0A, fullA, v0B, fullB):
    """Per-site private + missing rows with cross values (M36 verbatim)."""
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
    """Signed-gap sign tables (g_Q x g_O per site; M36 verbatim)."""
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
    """|d| stats per set (|d_Q| on priv, |d_s0| on miss; M36 verbatim)."""
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


def shared_lines(tag, kept, dQ, dA, v0Q, fullQ, v0A, fullA):
    """Kept-row value rows: both-frames |d| + gaps + signs (new helper).

    kept = shared (tail-on-both) sites in the dest column. Guard:
    every kept site reads tail (|d|>=8) on BOTH frames.
    """
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    aA = np.frombuffer(v0A, np.uint8).astype(np.int16)
    bA = np.frombuffer(fullA, np.uint8).astype(np.int16)
    aB = np.frombuffer(v0Q, np.uint8).astype(np.int16)
    bB = np.frombuffer(fullQ, np.uint8).astype(np.int16)
    gA, gB = aA - bA, aB - bB

    def sgn(x):
        return "+" if x > 0 else ("-" if x < 0 else "0")

    idx = [int(o) for o in np.nonzero(kept)[0]]
    cells = {}
    adQs, adOs = [], []
    geq = ageq = tailboth = 0
    for o in idx:
        adq = int(abs(int(dQ[o])))
        ado = int(abs(int(dA[o])))
        adQs.append(adq)
        adOs.append(ado)
        if adq >= 8 and ado >= 8:
            tailboth += 1
        k = (sgn(int(gB[o])), sgn(int(gA[o])))
        cells[k] = cells.get(k, 0) + 1
        if int(gB[o]) == int(gA[o]):
            geq += 1
        if abs(int(gB[o])) == abs(int(gA[o])):
            ageq += 1
        L.append(f"{tag} kept o={o} plane={PNAME[int(pl[o])]} "
                 f"rc=({int(pr[o])},{int(pc[o])}) adQ={adq} adO={ado} "
                 f"gQ={int(gB[o])} gO={int(gA[o])} sign={k[0]}{k[1]}")
    n = len(idx)
    L.append(f"{tag} kept tailboth: {tailboth}/{n}")
    order = [(a, b) for a in ("+", "-", "0") for b in ("+", "-", "0")]
    L.append(f"{tag} kept gapsign: n={n} "
             + " ".join(f"{a}{b}={cells.get((a, b), 0)}"
                        for a, b in order))
    L.append(f"{tag} kept gaps: signed-eq={geq}/{n} "
             f"({geq / n if n else 0:.4f}) abs-eq={ageq}/{n} "
             f"({ageq / n if n else 0:.4f})")
    for nm, ads in (("adQ", sorted(adQs)), ("adO", sorted(adOs))):
        a = np.asarray(ads, dtype=np.float64)
        L.append(f"{tag} kept dstats {nm}: n={n} "
                 f"list=[{','.join(map(str, ads))}] min={a.min():.0f} "
                 f"med={np.median(a):.1f} mean={a.mean():.4f} "
                 f"max={a.max():.0f}")
    return L


def fmt_f(x):
    return "%g" % (x,)


def main():
    m16d, m15d, m28tsv, m34tsv, workd, evidd = (Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0+734)

    print("== inputs (read-only) ==")
    guard_bins = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
                  m16d / "m16-full-s0000.bin",
                  m16d / "m16-v0-s0734.bin", m16d / "m16-mid-s0734.bin",
                  m16d / "m16-full-s0734.bin",
                  m15d / "m15-v0.bin", m15d / "m15-mid.bin",
                  m15d / "m15-full.bin"]
    for p in guard_bins:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} "
              f"sha256={hashlib.sha256(b).hexdigest()}")
    for q in (m28tsv, m34tsv):
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
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid0 = load_dump(m16d / "m16-mid-s0000.bin")
    full0 = load_dump(m16d / "m16-full-s0000.bin")
    b0 = synth_w_bytes(v0, full0, 0.5)
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M47 baselines: STOP, tabled.")
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
    print(f"s0 cell7 n={n0} (want {M19_INTERIOR_S0})")
    if n0 != M19_INTERIOR_S0:
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
    rows0 = {c: y_col_rows(t0, c, pl, pr, pc) for c in NAMED8}
    ref_ok = all(rows0[c] == S0_ROWS[c] for c in NAMED8)
    for c in NAMED8:
        print(f"s0 ref col {c}: n={len(rows0[c])} "
              f"rows=[{','.join(map(str, rows0[c]))}] "
              f"match={rows0[c] == S0_ROWS[c]}")
    r341 = y_col_rows(t0, 341, pl, pr, pc)
    print(f"s0 guard-only c341: n={len(r341)} (want 0)")
    if not ref_ok or len(r341) != 0:
        print("s0 REFERENCE MISMATCH: STOP, tabled.")
        return
    print(f"self Jaccard={jaccard(t0, t0):.4f} (want 1.0000)")

    # ---- full 764 pass ----
    print("== full 764 pass (R_s vs loo + cell/tail + census fields) ==")
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
        colrows = {c: y_col_rows(t, c, pl, pr, pc) for c in NAMED8}
        ycols = tail_y_cols(t, pl, pr, pc)
        priv = t & ~t0
        pcols = priv_y_cols(priv, pl, pr, pc)
        npuv = int(priv.sum()) - sum(len(v) for v in pcols.values())
        per[s] = {"tail": nt, "j": jj, "rs": xd, "colrows": colrows,
                  "ycols": ycols, "pcols": pcols, "npuv": npuv,
                  "npriv": int(priv.sum()),
                  "nmiss": int((t0 & ~t).sum())}
    fold = hashlib.sha256("".join(loo_hexes).encode()).hexdigest()
    print(f"triplet fold sha (764x3 bins): {fold}")
    print(f"want: {FOLD_WANT} match={fold == FOLD_WANT}")
    print(f"R_s vs loo mismatches: n={len(rs_bad)} {rs_bad[:20]}")
    print(f"delta==0 violations: n={d0_bad} shapes")
    print(f"shapes recorded: n={len(per)} (want 764)")
    print(f"(full-pass wall: {time.time() - t1:.1f}s)")
    if rs_bad or d0_bad or len(per) != 764 or fold != FOLD_WANT:
        print("FULL-PASS MISMATCH: STOP, tabled.")
        return

    # ---- UNNAMED domain + s0u pins ----
    print("== UNNAMED domain ==")
    allcols = set()
    for s in range(764):
        allcols |= set(per[s]["ycols"])
    UNNAMED = sorted(c for c in allcols if c not in NAMED8)
    s0y = per[0]["ycols"]
    s0u = {c: s0y.get(c, []) for c in UNNAMED}
    print(f"union tail-Y cols (all 764): n={len(allcols)} (want 41)")
    print(f"UNNAMED (union minus named8): n={len(UNNAMED)} (want 33)")
    print(f"UNNAMED == pin: {UNNAMED == UNNAMED_PIN}")
    if UNNAMED != UNNAMED_PIN:
        print(f"recomputed: {UNNAMED}")
        print(f"pinned:     {UNNAMED_PIN}")
    s0u_ok = (all(s0u[c] == S0U_PIN[c] for c in S0U_PIN)
              and all(s0u[c] == [] for c in PUREPRIV_PIN))
    for c in sorted(S0U_PIN):
        print(f"s0u col {c}: n={len(s0u[c])} rows={s0u[c]} "
              f"match={s0u[c] == S0U_PIN[c]}")
    print(f"pure-private n0==0 all-20: "
          f"{all(s0u[c] == [] for c in PUREPRIV_PIN)}")
    c341_all = sum(len(per[s]["ycols"].get(341, [])) for s in range(764))
    print(f"c341 tail sites over all 764: n={c341_all} (want 0)")
    if (len(allcols) != 41 or UNNAMED != UNNAMED_PIN or not s0u_ok
            or c341_all != 0):
        print("UNNAMED-DOMAIN MISMATCH: STOP, tabled.")
        return

    # ---- FULL TSV guards (named vs m28 + unnamed vs m34) ----
    print("== FULL TSV guards ==")
    t1 = time.time()
    ntsv = ["\t".join(["shape", "tail_n", "J_vs_s0"]
                      + [f"{k}{c}" for c in NAMED8
                         for k in ("n", "ov", "pres")])]
    utsv = ["\t".join(["shape", "tail_n", "J_vs_s0"]
                      + [f"{k}{c}" for c in UNNAMED
                         for k in ("n", "ov", "pres")])]
    for s in range(764):
        rec = per[s]
        cen = census_of_shape(rec["colrows"])
        rec["cen"] = cen
        ucen = census_unnamed_of(rec["ycols"], s0u)
        rec["ucen"] = ucen
        row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in NAMED8:
            row += [str(cen[c]["n"]), str(cen[c]["ov"]),
                    str(cen[c]["pres"])]
        ntsv.append("\t".join(row))
        urow = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in UNNAMED:
            urow += [str(ucen[c]["n"]), str(ucen[c]["ov"]),
                     str(ucen[c]["pres"])]
        utsv.append("\t".join(urow))
    ntxt, utxt = "\n".join(ntsv) + "\n", "\n".join(utsv) + "\n"
    nwant, uwant = m28tsv.read_text(), m34tsv.read_text()
    print(f"named TSV recomputed: rows={len(ntsv) - 1} bytes={len(ntxt)}; "
          f"match-target bytes={len(nwant)}")
    print(f"FULL named TSV byte-identical vs m28-census.tsv: {ntxt == nwant}")
    print(f"unnamed TSV recomputed: rows={len(utsv) - 1} bytes={len(utxt)}; "
          f"match-target bytes={len(uwant)}")
    print(f"FULL unnamed TSV byte-identical vs m34-census.tsv: {utxt == uwant}")
    if ntxt != nwant or utxt != uwant:
        print("TSV MISMATCH: STOP, tabled.")
        return
    print(f"(TSV-guard wall: {time.time() - t1:.1f}s)")

    # ---- 734 row guard + displacement guard + M29-value guard ----
    print("== 734 row guard ==")
    r734 = per[734]
    mv734 = sorted(c for c in NAMED8 if r734["cen"][c]["pres"] == 0)
    umv734 = sorted(c for c in UNNAMED if r734["ucen"][c]["pres"] == 0)
    print(f"s734: tail={r734['tail']} (want 94) J={r734['j']:.4f} "
          f"(want 0.8846) moved={mv734} (want [340, 342, 343])")
    for c in (340, 342, 343):
        print(f"s734 c{c}: n={r734['cen'][c]['n']} "
              f"ov={r734['cen'][c]['ov']}")
    print(f"s734 unnamed moved: {umv734} (want [] — purely named)")
    g734 = (r734["tail"] == 94 and f"{r734['j']:.4f}" == "0.8846"
            and mv734 == [340, 342, 343]
            and r734["cen"][340]["n"] == 0 and r734["cen"][340]["ov"] == 0
            and r734["cen"][343]["n"] == 0 and r734["cen"][343]["ov"] == 0
            and r734["cen"][342]["n"] == 7 and r734["cen"][342]["ov"] == 5
            and umv734 == [])
    print("734-row guard: " + ("OK" if g734 else "MISMATCH: STOP, tabled."))
    if not g734:
        return
    movers = sorted(s for s in range(764)
                    if any(per[s]["cen"][c]["pres"] == 0 for c in NAMED8))
    print(f"recomputed named movers: {movers} (want {M28_MOVERS}) "
          f"match={movers == M28_MOVERS}")
    if movers != M28_MOVERS:
        print("MOVER-LIST MISMATCH: STOP, tabled.")
        return

    # ---- load triplets for 734 (Task 1/2 row + value tables) ----
    def load_sets(s):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        sp = interior_sites(vv, mm, ff, bl)
        t, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        return {"v0": vv, "mid": mm, "full": ff, "mask": sp["mask"],
                "d": sp["delta"], "t": t}

    q734 = load_sets(734)
    t734 = q734["t"]
    p734 = t734 & ~t0
    m734 = t0 & ~t734
    s734sh = t734 & t0
    print(f"s734 sets: priv={int(p734.sum())} miss={int(m734.sum())} "
          f"shared={int(s734sh.sum())} tail={int(t734.sum())}")

    # ---- displacement guard (M28 rule rows) ----
    print("== 734 displacement guard (M28 rows) ==")
    pcols734 = priv_y_cols(p734, pl, pr, pc)
    print(f"s734 private Y-cols: {sorted(pcols734.items())}")
    print(f"s734 private U/V sites: "
          f"{int(p734.sum()) - sum(len(v) for v in pcols734.values())}")
    disp_ok = True
    for c in (340, 343):
        a = assign_one(c, pcols734)
        w = DISP_PIN[c]
        ok = (a["dest"] == w["dest"] and a["off"] == w["off"]
              and a["rshift"] == w["rshift"] and a["minshift"] == w["minshift"])
        print(f"move s734 c{c}->{a['dest']}: off={a['off']:+d} "
              f"(want {w['off']:+d}) rshift={fmt_f(a['rshift'])} "
              f"(want {fmt_f(w['rshift'])}) minshift={a['minshift']:+d} "
              f"(want {w['minshift']:+d}) match={ok}")
        disp_ok = disp_ok and ok
    eo342 = r734["cen"][342]["miss"] == 0
    print(f"s734 c342 extra-only (miss==0): {eo342}")
    disp_ok = disp_ok and eo342
    print("displacement guard: "
          + ("OK" if disp_ok else "MISMATCH: STOP, tabled."))
    if not disp_ok:
        return

    # ---- M29 dest-value guard ([26,33] + |d| + gaps) ----
    print("== 734 M29-value guard ==")
    a0 = np.frombuffer(v0, np.uint8).astype(np.int16)
    b0f = np.frombuffer(full0, np.uint8).astype(np.int16)
    aQ = np.frombuffer(q734["v0"], np.uint8).astype(np.int16)
    bQ = np.frombuffer(q734["full"], np.uint8).astype(np.int16)
    g0, gQ = a0 - b0f, aQ - bQ
    rows734_c342 = y_col_rows(t734, 342, pl, pr, pc)
    extra342 = sorted(set(rows734_c342) - set(S0_ROWS[342]))
    print(f"s734 c342 rows={rows734_c342} extra={extra342} "
          f"(want {DEST_PIN['rows']})")
    m29_ok = extra342 == DEST_PIN["rows"]
    for i, r in enumerate(DEST_PIN["rows"]):
        o = off_of(r, 342)
        adq = int(abs(int(q734["d"][o])))
        bulk0 = bool(sp0["mask"][o])
        ado = int(abs(int(d0[o]))) if bulk0 else None
        row_ok = (o == DEST_PIN["offs"][i] and adq == DEST_PIN["adQ"][i]
                  and bulk0 and ado == DEST_PIN["adO"][i]
                  and int(gQ[o]) == DEST_PIN["gQ"][i]
                  and int(g0[o]) == DEST_PIN["gO"][i]
                  and int(pl[o]) == 0)
        print(f"dest r{r}: o={o} (want {DEST_PIN['offs'][i]}) "
              f"adQ={adq} (want {DEST_PIN['adQ'][i]}) s0-bulk={bulk0} "
              f"adO={ado} (want {DEST_PIN['adO'][i]}) "
              f"gQ={int(gQ[o])} (want {DEST_PIN['gQ'][i]}) "
              f"gO={int(g0[o])} (want {DEST_PIN['gO'][i]}) match={row_ok}")
        m29_ok = m29_ok and row_ok
    print("M29-value guard: "
          + ("OK" if m29_ok else "MISMATCH: STOP, tabled."))
    if not m29_ok:
        return

    # ---- Task 1.1: wipe table (c340 + c343) ----
    print("== Task 1.1: wipe table (c340 + c343) ==")
    for c in (340, 343):
        r0c = S0_ROWS[c]
        rqc = y_col_rows(t734, c, pl, pr, pc)
        missc = sorted(set(r0c) - set(rqc))
        print(f"wipe c{c}: s0-rows={r0c} s734-rows={rqc} miss={missc} "
              f"n/ov={r734['cen'][c]['n']}/{r734['cen'][c]['ov']}")
        canon.append(f"canon wipe c{c}: s0={r0c} q={rqc} miss={missc}")

    # ---- Task 1.2: dest table (c342 full row-list) ----
    print("== Task 1.2: dest table (c342 kept + extras) ==")
    r0c = S0_ROWS[342]
    rqc = rows734_c342
    keptc = sorted(set(r0c) & set(rqc))
    print(f"dest c342: s0-rows={r0c} s734-rows={rqc} kept={keptc} "
          f"extra={extra342} n/ov={r734['cen'][342]['n']}/"
          f"{r734['cen'][342]['ov']}")
    canon.append(f"canon dest c342: s0={r0c} q={rqc} kept={keptc} "
                 f"extra={extra342}")

    # ---- Task 1.3: displacement table (M28 rule rows) ----
    print("== Task 1.3: displacement table (M28 rule rows) ==")
    cands734 = {c: v for c, v in pcols734.items() if len(v) >= 2}
    print(f"s734 >=2-site candidates: {sorted(cands734.items())}")
    canon.append(f"canon disp pcols734={sorted(pcols734.items())}")
    for c in (340, 343):
        a = assign_one(c, pcols734)
        print(f"move s734 c{c}->{a['dest']}: off={a['off']:+d} "
              f"rshift={fmt_f(a['rshift'])} minshift={a['minshift']:+d} "
              f"npriv={a['npriv']} prows={cands734[a['dest']]} "
              f"fresh={a['dest'] not in NAMED8}")
        canon.append(f"canon disp c{c}: dest={a['dest']} off={a['off']} "
                     f"rs={fmt_f(a['rshift'])} ms={a['minshift']} "
                     f"status={a['status']}")
    print("move s734 c342->none: status=none(extra-only)")
    canon.append("canon disp c342: dest=None status=extra-only")

    # ---- Task 2.1: wiped-value table (10 rows, M36-style) ----
    print("== Task 2.1: wiped-value table (10 rows, M36-style) ==")
    empty = np.zeros(N, bool)
    wlines, wout = attrib_lines("wipe734", empty, m734, s734sh,
                                d0, mask0, q734["d"], q734["mask"],
                                v0, full0, q734["v0"], q734["full"])
    for ln in wlines:
        print(ln)
        if ln.startswith("wipe734 miss o="):
            canon.append("canon " + ln)
    for ln in gapsign_lines("wipe734", empty, m734,
                            v0, full0, q734["v0"], q734["full"]):
        print(ln)
        canon.append("canon " + ln)
    for ln in dstats_lines("wipe734", empty, m734, q734["d"], d0):
        print(ln)
        canon.append("canon " + ln)

    # ---- Task 2.2: dest-value table (extras + kept, M36-style) ----
    print("== Task 2.2: dest-value table (extras + kept) ==")
    dlines, dout = attrib_lines("dest734", p734, empty, s734sh,
                                d0, mask0, q734["d"], q734["mask"],
                                v0, full0, q734["v0"], q734["full"])
    for ln in dlines:
        print(ln)
        if ln.startswith("dest734 priv o="):
            canon.append("canon " + ln)
    for ln in gapsign_lines("dest734", p734, empty,
                            v0, full0, q734["v0"], q734["full"]):
        print(ln)
        canon.append("canon " + ln)
    for ln in dstats_lines("dest734", p734, empty, q734["d"], d0):
        print(ln)
        canon.append("canon " + ln)
    kept = np.zeros(N, bool)
    for r in keptc:
        o = off_of(r, 342)
        assert t734[o] and t0[o], f"kept c342 r{r}: not shared-tail?!"
        kept[o] = True
    for ln in shared_lines("keep734", kept, q734["d"], d0,
                           q734["v0"], q734["full"], v0, full0):
        print(ln)
        canon.append("canon " + ln)

    # ---- Task 2.3: collision table (counts only, no assignment) ----
    print("== Task 2.3: collision table (numbers only) ==")
    n_wipe340 = len(S0_ROWS[340]) - 0  # c340 0/0: all 8 wiped
    n_wipe343 = len(S0_ROWS[343]) - 0  # c343 0/0: both wiped
    n_wipe = n_wipe340 + n_wipe343
    n_growth = len(extra342)
    n_kept = len(keptc)
    print(f"wiped rows: c340={n_wipe340} c343={n_wipe343} total={n_wipe}")
    print(f"dest c342: growth=+{n_growth} kept={n_kept} "
          f"n0={len(S0_ROWS[342])} n={r734['cen'][342]['n']}")
    print(f"full sets: priv={int(p734.sum())} miss={int(m734.sum())} "
          f"shared={int(s734sh.sum())} tailQ={int(t734.sum())} "
          f"tail0={nt0}")
    print(f"net tail delta: {int(t734.sum()) - nt0} "
          f"(wiped-growth={n_growth - n_wipe})")
    out_priv = sorted((int(pr[o]), int(pc[o]))
                     for o in np.nonzero(p734)[0] if int(pc[o]) != 342)
    out_miss = sorted((int(pr[o]), int(pc[o]))
                     for o in np.nonzero(m734)[0]
                     if int(pc[o]) not in (340, 343))
    print(f"privates outside c342: n={len(out_priv)} {out_priv}")
    print(f"missings outside c340/c343: n={len(out_miss)} {out_miss}")
    print(f"counts admit full accounting: "
          f"miss==wiped({int(m734.sum())}=={n_wipe}) "
          f"priv==growth({int(p734.sum())}=={n_growth}) "
          f"outside==0({len(out_priv) + len(out_miss)}==0)")

    # ---- determinism re-run (Task 1 on s0+734, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+734, second pass) ==")
    canon2 = []
    vv = load_dump(m16d / "m16-v0-s0734.bin")
    mm = load_dump(m16d / "m16-mid-s0734.bin")
    ff = load_dump(m16d / "m16-full-s0734.bin")
    bl = synth_w_bytes(vv, ff, 0.5)
    spq = interior_sites(vv, mm, ff, bl)
    tq, _ = tail_bulk_masks(spq["mask"], spq["delta"])
    for c in (340, 343):
        r0c = S0_ROWS[c]
        rqc = y_col_rows(tq, c, pl, pr, pc)
        missc = sorted(set(r0c) - set(rqc))
        canon2.append(f"canon wipe c{c}: s0={r0c} q={rqc} miss={missc}")
    r0c = S0_ROWS[342]
    rqc = y_col_rows(tq, 342, pl, pr, pc)
    keptc2 = sorted(set(r0c) & set(rqc))
    extra2 = sorted(set(rqc) - set(r0c))
    canon2.append(f"canon dest c342: s0={r0c} q={rqc} kept={keptc2} "
                  f"extra={extra2}")
    pq2, mq2 = tq & ~t0, t0 & ~tq
    sh2 = tq & t0
    pcols2 = priv_y_cols(pq2, pl, pr, pc)
    canon2.append(f"canon disp pcols734={sorted(pcols2.items())}")
    for c in (340, 343):
        a = assign_one(c, pcols2)
        canon2.append(f"canon disp c{c}: dest={a['dest']} off={a['off']} "
                      f"rs={fmt_f(a['rshift'])} ms={a['minshift']} "
                      f"status={a['status']}")
    canon2.append("canon disp c342: dest=None status=extra-only")
    wlines2, _ = attrib_lines("wipe734", empty, mq2, sh2,
                              d0, mask0, spq["delta"], spq["mask"],
                              v0, full0, vv, ff)
    for ln in wlines2:
        if ln.startswith("wipe734 miss o="):
            canon2.append("canon " + ln)
    for ln in gapsign_lines("wipe734", empty, mq2, v0, full0, vv, ff):
        canon2.append("canon " + ln)
    for ln in dstats_lines("wipe734", empty, mq2, spq["delta"], d0):
        canon2.append("canon " + ln)
    dlines2, _ = attrib_lines("dest734", pq2, empty, sh2,
                              d0, mask0, spq["delta"], spq["mask"],
                              v0, full0, vv, ff)
    for ln in dlines2:
        if ln.startswith("dest734 priv o="):
            canon2.append("canon " + ln)
    for ln in gapsign_lines("dest734", pq2, empty, v0, full0, vv, ff):
        canon2.append("canon " + ln)
    for ln in dstats_lines("dest734", pq2, empty, spq["delta"], d0):
        canon2.append("canon " + ln)
    kept2 = np.zeros(N, bool)
    for r in keptc2:
        kept2[off_of(r, 342)] = True
    for ln in shared_lines("keep734", kept2, spq["delta"], d0,
                           vv, ff, v0, full0):
        canon2.append("canon " + ln)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon lines: pass1={len(canon)} pass2={len(canon2)}")
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"lines match: "
          f"{sum(1 for a, b in zip(canon, canon2) if a == b)}/{len(canon)}")

    # ---- PNG collision map ----
    print("== PNG collision map ==")
    img = np.zeros((224, 320, 3), np.uint8)
    px = {}  # (x, y) -> class list (overlap table)
    for r in keptc:
        img[r // 2, 342 // 2] = (0, 255, 0)
        px.setdefault((342 // 2, r // 2), []).append("kept")
    for r in S0_ROWS[340]:
        img[r // 2, 340 // 2] = (255, 0, 0)
        px.setdefault((340 // 2, r // 2), []).append("wipe340")
    for r in S0_ROWS[343]:
        img[r // 2, 343 // 2] = (255, 0, 255)
        px.setdefault((343 // 2, r // 2), []).append("wipe343")
    for r in extra342:
        img[r // 2, 342 // 2] = (255, 255, 0)
        px.setdefault((342 // 2, r // 2), []).append("extra")
    p = workd / "m48-collision.png"
    Image.fromarray(img).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: x=col//2 y=row//2; green=kept c342(5), red=wiped "
          "c340(8), magenta=wiped c343(2), yellow=dest extras(2)")
    multi = {k: v for k, v in px.items() if len(v) > 1}
    print(f"pixel overlaps (>1 class): n={len(multi)} {multi}")

    # ---- falsification-bar measurements ----
    print("== falsification-bar measurements ==")
    print(f"H1_WIPENEAR: wiped near {wout['miss']['near']}/10 "
          f"({wout['miss']['near'] / 10:.4f}; bar >=0.50)")
    print(f"H2_WIPESET: wiped noncell {wout['miss']['non']}/10 "
          f"({wout['miss']['non'] / 10:.4f}; bar >=0.50)")
    print(f"H3_DESTNEAR: dest-extra near {dout['priv']['near']}/2 "
          f"({dout['priv']['near'] / 2:.4f}; bar >=0.50)")
    pp = sum(1 for o in np.nonzero(m734)[0]
             if int(g0[int(o)]) > 0 and int(gQ[int(o)]) > 0)
    print(f"H4_WIPEGG: wiped ++ {pp}/10 ({pp / 10:.4f}; bar >=0.50)")
    wmed = float(np.median(np.asarray(
        sorted(int(abs(int(d0[int(o)]))) for o in np.nonzero(m734)[0]),
        dtype=np.float64)))
    emed = float(np.median(np.asarray(
        sorted(int(abs(int(q734["d"][int(o)])))
               for o in np.nonzero(p734)[0]),
        dtype=np.float64)))
    print(f"H5_VALMED: wiped med {wmed:.1f} vs dest-extra med {emed:.1f} "
          f"(meets iff strictly unequal)")
    a340 = assign_one(340, pcols734)
    a343 = assign_one(343, pcols734)
    print(f"H6_COLLISION: dest(c340)={a340['dest']} dest(c343)={a343['dest']} "
          f"(meets iff both ==342)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=triple-repro T2=values+collision R=controls")


if __name__ == "__main__":
    main()
