#!/usr/bin/env python3
"""M47 shape-711 pair wipe: singleton + far private-column listing (offline).

Usage: m47.py M16_DIR M15_DIR M28TSV M34TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m28/m34-census.tsv (FULL TSV guards); raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt text
goes to stdout (redirect to WORK_DIR/m47.txt); PNG wipe/pool map
to WORK_DIR (evidence copy iff the DESIGN.md rule meets, decided
at report time).

Tasks (see DESIGN.md, recorded before running):
  1: 711 wipe reproduction (wipe rows + wiped values + no-cand rows)
  2: singleton + far private-column listing (the new data)
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
S711 = {"tail": 95, "j": "0.9314", "moved": [342, 343]}
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
    """Group tail-mask Y sites by column -> {col: sorted rows}."""
    out = {}
    for o in np.nonzero(t & (pl == 0))[0]:
        out.setdefault(int(pc[o]), []).append(int(pr[o]))
    return {c: sorted(v) for c, v in out.items()}


def priv_y_cols(priv: np.ndarray, pl, pr, pc):
    """Group private-mask Y sites by column -> {col: sorted rows}."""
    return tail_y_cols(priv, pl, pr, pc)


def census_of_shape(colrows):
    """Per-named-column presence: exact-match rule (M28 pinned)."""
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


def fmt_f(x):
    return "%g" % (x,)


def main():
    m16d, m15d, m28tsv, m34tsv, workd, evidd = (Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0+711)

    print("== inputs (read-only) ==")
    guard_bins = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
                  m16d / "m16-full-s0000.bin",
                  m16d / "m16-v0-s0711.bin", m16d / "m16-mid-s0711.bin",
                  m16d / "m16-full-s0711.bin",
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
        print("MISMATCH vs M17-M46 baselines: STOP, tabled.")
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

    # ---- 711 row guard + singleton-count guard ----
    print("== 711 row guard ==")
    r711 = per[711]
    mv711 = sorted(c for c in NAMED8 if r711["cen"][c]["pres"] == 0)
    umv711 = sorted(c for c in UNNAMED if r711["ucen"][c]["pres"] == 0)
    print(f"s711: tail={r711['tail']} (want 95) J={r711['j']:.4f} "
          f"(want 0.9314) moved={mv711} (want [342, 343])")
    for c in (342, 343):
        print(f"s711 c{c}: n={r711['cen'][c]['n']} "
              f"ov={r711['cen'][c]['ov']} (want 0/0)")
    print(f"s711 unnamed moved: {umv711} (want [] — purely named)")
    g711 = (r711["tail"] == 95 and f"{r711['j']:.4f}" == "0.9314"
            and mv711 == [342, 343]
            and all(r711["cen"][c]["n"] == 0
                    and r711["cen"][c]["ov"] == 0 for c in (342, 343))
            and umv711 == [])
    print("711-row guard: " + ("OK" if g711 else "MISMATCH: STOP, tabled."))
    if not g711:
        return
    movers = sorted(s for s in range(764)
                    if any(per[s]["cen"][c]["pres"] == 0 for c in NAMED8))
    print(f"recomputed named movers: {movers} (want {M28_MOVERS}) "
          f"match={movers == M28_MOVERS}")
    if movers != M28_MOVERS:
        print("MOVER-LIST MISMATCH: STOP, tabled.")
        return
    sing = [(s, c) for s in movers for c, v in per[s]["pcols"].items()
            if len(v) == 1]
    print(f"singleton private Y-cols (movers): n={len(sing)} (want 11)")
    if len(sing) != 11:
        print("SINGLETON-COUNT MISMATCH: STOP, tabled.")
        return
    sing = sorted(sing)
    print(f"singleton (shape,col): {sing}")
    far = sorted((s, c) for s in movers for c, v in per[s]["pcols"].items()
                 if len(v) >= 2)
    print(f"far (multi-private) Y-cols (movers): n={len(far)}")
    print(f"far (shape,col): {far}")

    # ---- load triplets for 711 + movers (Task 1/2 value tables) ----
    def load_sets(s):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        sp = interior_sites(vv, mm, ff, bl)
        t, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        return {"v0": vv, "mid": mm, "full": ff, "mask": sp["mask"],
                "d": sp["delta"], "t": t}

    q711 = load_sets(711)
    t711 = q711["t"]
    p711 = t711 & ~t0
    m711 = t0 & ~t711
    s711sh = t711 & t0
    print(f"s711 sets: priv={int(p711.sum())} miss={int(m711.sum())} "
          f"shared={int(s711sh.sum())} tail={int(t711.sum())}")

    # ---- Task 1.1: wipe table ----
    print("== Task 1.1: wipe table (c342 + c343) ==")
    for c in (342, 343):
        r0c = S0_ROWS[c]
        rqc = y_col_rows(t711, c, pl, pr, pc)
        missc = sorted(set(r0c) - set(rqc))
        print(f"wipe c{c}: s0-rows={r0c} s711-rows={rqc} miss={missc} "
              f"n/ov={r711['cen'][c]['n']}/{r711['cen'][c]['ov']}")
        canon.append(f"canon wipe c{c}: s0={r0c} q={rqc} miss={missc}")

    # ---- Task 1.2: wiped-value table (M36-style) ----
    print("== Task 1.2: wiped-value table (7 rows, M36-style) ==")
    empty = np.zeros(N, bool)
    wlines, wout = attrib_lines("wipe711", empty, m711, s711sh,
                                d0, mask0, q711["d"], q711["mask"],
                                v0, full0, q711["v0"], q711["full"])
    for ln in wlines:
        print(ln)
        if ln.startswith("wipe711 miss o="):
            canon.append("canon " + ln)
    for ln in gapsign_lines("wipe711", empty, m711,
                            v0, full0, q711["v0"], q711["full"]):
        print(ln)
        canon.append("canon " + ln)
    for ln in dstats_lines("wipe711", empty, m711, q711["d"], d0):
        print(ln)
        canon.append("canon " + ln)

    # ---- Task 1.3: no-cand table (M28 rule rows) ----
    print("== Task 1.3: no-cand table (M28 rule rows) ==")
    pcols711 = priv_y_cols(p711, pl, pr, pc)
    print(f"s711 private Y-cols: {pcols711 if pcols711 else '(none)'}")
    print(f"s711 private U/V sites: "
          f"{int(p711.sum()) - sum(len(v) for v in pcols711.values())}")
    cands711 = {c: v for c, v in pcols711.items() if len(v) >= 2}
    print(f"s711 >=2-site candidates: {cands711 if cands711 else '(none)'}")
    canon.append(f"canon nocand pcols711={sorted(pcols711.items())}")
    for c in (342, 343):
        a = assign_one(c, pcols711)
        if a["status"] == "ok":
            print(f"move s711 c{c}->{a['dest']}: off={a['off']:+d} "
                  f"rshift={fmt_f(a['rshift'])} minshift={a['minshift']:+d}")
        else:
            print(f"move s711 c{c}->none: status=none({a['status']}) "
                  f"npriv-cands={len(cands711)} miss-rows={S0_ROWS[c]}")
        canon.append(f"canon nocand c{c}: dest={a['dest']} off={a['off']} "
                     f"status={a['status']}")

    # ---- Task 2.1: singleton table (name all 11) ----
    print("== Task 2.1: singleton table (all 11, M36-style rows) ==")
    t1 = time.time()
    sing_sets = {"priv": np.zeros(N, bool)}
    mov_cache = {}
    for s, c in sing:
        if s not in mov_cache:
            mov_cache[s] = load_sets(s)
        q = mov_cache[s]
        t = q["t"]
        o = off_of(per[s]["pcols"][c][0], c)
        assert t[o] and not t0[o], f"singleton s{s} c{c}: not private?!"
        sing_sets["priv"][o] = True
        print(f"sing s{s} c{c}: row={per[s]['pcols'][c][0]} off={o}")
    # per-shape value rows (attrib needs per-shape frames)
    sing_sum = {"near": 0, "far": 0, "non": 0}
    sing_ads = []
    for s in sorted({s for s, _ in sing}):
        q = mov_cache[s]
        t = q["t"]
        sub = np.zeros(N, bool)
        for (ss, c) in sing:
            if ss == s:
                sub[off_of(per[s]["pcols"][c][0], c)] = True
        sh = t & t0
        slines, sout = attrib_lines(f"singQ{s}", sub, empty, sh,
                                    d0, mask0, q["d"], q["mask"],
                                    v0, full0, q["v0"], q["full"])
        for ln in slines:
            print(ln)
        sing_sum["near"] += sout["priv"]["near"]
        sing_sum["far"] += sout["priv"]["far"]
        sing_sum["non"] += sout["priv"]["non"]
        for ln in gapsign_lines(f"singQ{s}", sub, empty,
                                v0, full0, q["v0"], q["full"]):
            print(ln)
        for ln in dstats_lines(f"singQ{s}", sub, empty, q["d"], d0):
            print(ln)
        for (ss, c) in sing:
            if ss == s:
                sing_ads.append(
                    int(abs(int(q["d"][off_of(per[s]["pcols"][c][0], c)]))))
    print(f"singleton pooled status: near={sing_sum['near']} "
          f"far={sing_sum['far']} noncell={sing_sum['non']} "
          f"bulk-share={(sing_sum['near'] + sing_sum['far']) / 11:.4f}")
    sa = np.asarray(sorted(sing_ads), dtype=np.float64)
    print(f"singleton pooled |dQ|: list={sorted(sing_ads)} "
          f"min={sa.min():.0f} med={np.median(sa):.1f} "
          f"mean={sa.mean():.4f} max={sa.max():.0f}")
    print(f"(Task-2.1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.2: far-column table ----
    print("== Task 2.2: far-column table (multi-private, listed) ==")
    t1 = time.time()
    far_ads_all = []
    for s, c in far:
        if s not in mov_cache:
            mov_cache[s] = load_sets(s)
        q = mov_cache[s]
        t = q["t"]
        rows = per[s]["pcols"][c]
        sub = np.zeros(N, bool)
        for r in rows:
            sub[off_of(r, c)] = True
        sh = t & t0
        print(f"far s{s} c{c}: n={len(rows)} rows={rows} "
              f"d342={abs(c - 342)} d343={abs(c - 343)}")
        slines, sout = attrib_lines(f"farQ{s}c{c}", sub, empty, sh,
                                    d0, mask0, q["d"], q["mask"],
                                    v0, full0, q["v0"], q["full"])
        for ln in slines:
            print(ln)
        for ln in gapsign_lines(f"farQ{s}c{c}", sub, empty,
                                v0, full0, q["v0"], q["full"]):
            print(ln)
        for ln in dstats_lines(f"farQ{s}c{c}", sub, empty, q["d"], d0):
            print(ln)
        for r in rows:
            far_ads_all.append(int(abs(int(q["d"][off_of(r, c)]))))
    fa = np.asarray(sorted(far_ads_all), dtype=np.float64)
    print(f"far pooled: ncols={len(far)} nsites={len(far_ads_all)} "
          f"|dQ| min={fa.min():.0f} med={np.median(fa):.1f} "
          f"mean={fa.mean():.4f} max={fa.max():.0f}")
    print(f"(Task-2.2 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.3: per-move count listing ----
    print("== Task 2.3: per-move count listing (numbers only) ==")
    n_sing_rows = len(sing)
    n_far_rows = len(far_ads_all)
    for c, w in ((342, 5), (343, 2)):
        print(f"move c{c}: wiped={w} singleton-pool={n_sing_rows} "
              f"(cover-by-count={n_sing_rows >= w}) "
              f"far-pool={n_far_rows} (cover-by-count={n_far_rows >= w})")

    # ---- determinism re-run (Task 1 on s0+711, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+711, second pass) ==")
    canon2 = []
    vv = load_dump(m16d / "m16-v0-s0711.bin")
    mm = load_dump(m16d / "m16-mid-s0711.bin")
    ff = load_dump(m16d / "m16-full-s0711.bin")
    bl = synth_w_bytes(vv, ff, 0.5)
    spq = interior_sites(vv, mm, ff, bl)
    tq, _ = tail_bulk_masks(spq["mask"], spq["delta"])
    for c in (342, 343):
        r0c = S0_ROWS[c]
        rqc = y_col_rows(tq, c, pl, pr, pc)
        missc = sorted(set(r0c) - set(rqc))
        canon2.append(f"canon wipe c{c}: s0={r0c} q={rqc} miss={missc}")
    pq2, mq2 = tq & ~t0, t0 & ~tq
    sh2 = tq & t0
    wlines2, _ = attrib_lines("wipe711", empty, mq2, sh2,
                              d0, mask0, spq["delta"], spq["mask"],
                              v0, full0, vv, ff)
    for ln in wlines2:
        if ln.startswith("wipe711 miss o="):
            canon2.append("canon " + ln)
    for ln in gapsign_lines("wipe711", empty, mq2, v0, full0, vv, ff):
        canon2.append("canon " + ln)
    for ln in dstats_lines("wipe711", empty, mq2, spq["delta"], d0):
        canon2.append("canon " + ln)
    pcols2 = priv_y_cols(pq2, pl, pr, pc)
    canon2.append(f"canon nocand pcols711={sorted(pcols2.items())}")
    for c in (342, 343):
        a = assign_one(c, pcols2)
        canon2.append(f"canon nocand c{c}: dest={a['dest']} off={a['off']} "
                      f"status={a['status']}")
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon lines: pass1={len(canon)} pass2={len(canon2)}")
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"lines match: "
          f"{sum(1 for a, b in zip(canon, canon2) if a == b)}/{len(canon)}")

    # ---- PNG wipe/pool map ----
    print("== PNG wipe/pool map ==")
    img = np.zeros((224, 320, 3), np.uint8)
    # wiped s0 sites (red) at (col//2, row//2)
    for c in (342, 343):
        for r in S0_ROWS[c]:
            img[r // 2, c // 2] = (255, 0, 0)
    # singleton pool (cyan), far pool (yellow)
    for s, c in sing:
        img[per[s]["pcols"][c][0] // 2, c // 2] = (0, 255, 255)
    for s, c in far:
        for r in per[s]["pcols"][c]:
            img[r // 2, c // 2] = (255, 255, 0)
    p = workd / "m47-poolmap.png"
    Image.fromarray(img).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: x=col//2 y=row//2; red=wiped s0 c342/c343, "
          "cyan=singleton pool (11), yellow=far pool")

    # ---- falsification-bar measurements ----
    print("== falsification-bar measurements ==")
    npriv711 = int(p711.sum())
    print(f"H1_PUREWIPE: s711 priv={npriv711} (bar ==0)")
    sb = sing_sum["near"] + sing_sum["far"]
    print(f"H2_SINGBULK: singleton bulk {sb}/11 ({sb / 11:.4f}; bar >=0.50)")
    print(f"H3_FARPOOL: far (shape,col) n={len(far)} (bar >=6)")
    wb = wout["miss"]["near"] + wout["miss"]["far"]
    print(f"H4_WIPEBULK: wiped bulk {wb}/7 ({wb / 7:.4f}; bar >=0.50)")
    # ++ share on wiped miss set (recompute signs here for the bar line)
    aA = np.frombuffer(v0, np.uint8).astype(np.int16)
    bA = np.frombuffer(full0, np.uint8).astype(np.int16)
    aB = np.frombuffer(q711["v0"], np.uint8).astype(np.int16)
    bB = np.frombuffer(q711["full"], np.uint8).astype(np.int16)
    gA, gB = aA - bA, aB - bB
    pp = sum(1 for o in np.nonzero(m711)[0]
             if int(gA[int(o)]) > 0 and int(gB[int(o)]) > 0)
    print(f"H5_WIPEGG: wiped ++ {pp}/7 ({pp / 7:.4f}; bar >=0.50)")
    print(f"H6_POOLMED: |far med {np.median(fa):.1f} - sing med "
          f"{np.median(sa):.1f}| = "
          f"{abs(float(np.median(fa)) - float(np.median(sa))):.1f} "
          f"(bar >=4)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=wipe-repro T2=pools R=controls")


if __name__ == "__main__":
    main()

