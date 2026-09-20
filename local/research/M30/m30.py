#!/usr/bin/env python3
"""M30 span-windowed census rule: proposal + 764-shape re-run (offline).

Usage: m30.py M16_DIR M15_DIR M28_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m28.txt + m28-census.tsv (exact-match census to
reproduce: 10 movers / 15 cells / standings); raw XFB dumps,
573440 B = 640x448 YUYV. Read-only inputs; receipt text goes to
stdout (redirect to WORK_DIR/m30.txt); windowed census TSVs + PNG
mover map to WORK_DIR (evidence copies iff the DESIGN.md rules
meet, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: windowed re-run per K + off-span tables + exact-vs-windowed deltas
  2: standing stability + below-0.95 joins per K + adjacent-K diffs
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
KS = [2, 5, 10]  # FIXED K list (DESIGN.md pinned, no mid-run additions)
M28_MOVERS = [9, 22, 708, 709, 710, 711, 731, 732, 733, 734]
WANT_STANDING = {
    (9, 321): "none(extra-only)", (22, 296): "none(extra-only)",
    (708, 296): "none(no-cand)", (709, 301): "none(no-cand)",
    (710, 340): "none(no-cand)", (711, 342): "none(no-cand)",
    (711, 343): "none(no-cand)", (731, 257): "ok", (731, 277): "ok",
    (732, 296): "ok", (733, 301): "ok", (733, 321): "ok",
    (734, 340): "ok", (734, 342): "none(extra-only)", (734, 343): "ok",
}
FAR_EXTRAS = [(9, 321, 266), (22, 296, 400), (22, 296, 401)]
NEAR_EXTRAS = [(734, 342, 26), (734, 342, 33)]
MISS_ROWS = [(708, 296, 28), (709, 301, 33), (710, 340, 31), (710, 340, 34)]
BELOW95 = {733: (100, "0.6694"), 731: (100, "0.6833"),
           9: (117, "0.7520"), 700: (114, "0.8462"),
           734: (94, "0.8846"), 732: (95, "0.8942"),
           2: (103, "0.9159"), 711: (95, "0.9314"),
           3: (103, "0.9340")}


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


def priv_y_cols(priv: np.ndarray, pl, pr, pc):
    """Group private-mask Y sites by column -> {col: sorted rows}."""
    out = {}
    for o in np.nonzero(priv & (pl == 0))[0]:
        out.setdefault(int(pc[o]), []).append(int(pr[o]))
    return {c: sorted(v) for c, v in out.items()}


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


def span_dist(r: int, c: int) -> int:
    """Row distance to the nearest s0 span row of column c."""
    return min(abs(r - r0) for r0 in S0_ROWS[c])


def wcensus_of_shape(colrows, K: int):
    """Per-named-column windowed presence (DESIGN.md pinned)."""
    out = {}
    for c in NAMED8:
        rs, r0 = colrows[c], S0_ROWS[c]
        win = [r for r in rs if span_dist(r, c) <= K]
        off = [r for r in rs if span_dist(r, c) > K]
        ov = len(set(win) & set(r0))
        out[c] = {"nK": len(win), "ovK": ov,
                  "presK": 1 if win == r0 else 0,
                  "missK": len(r0) - ov, "extraK": len(win) - ov,
                  "win": win, "off": off}
    return out


def offspan_sites(colrows, K: int):
    """{(col, row)} named-column Y-tail sites beyond ±K (DESIGN.md)."""
    return {(c, r) for c in NAMED8 for r in colrows[c]
            if span_dist(r, c) > K}


def standing_of_K(c, wc_c, pcols):
    """M28 standing rule on windowed miss/extra + FULL privates."""
    if wc_c["missK"] == 0:
        return "none(extra-only)"
    a = assign_one(c, pcols)
    return "ok" if a["status"] == "ok" else "none(no-cand)"


def parse_m28_tsv(path: Path):
    """{shape: {tail, j, cen: {col: {n, ov, pres}}}} from m28-census.tsv."""
    lines = path.read_text().splitlines()
    head = lines[0].split("\t")
    assert head[:3] == ["shape", "tail_n", "J_vs_s0"], head[:3]
    out = {}
    for ln in lines[1:]:
        f = ln.split("\t")
        s = int(f[0])
        cen = {}
        for i, c in enumerate(NAMED8):
            n, ov, pres = int(f[3 + 3 * i]), int(f[4 + 3 * i]), int(f[5 + 3 * i])
            cen[c] = {"n": n, "ov": ov, "pres": pres}
        out[s] = {"tail": int(f[1]), "j": f[2], "cen": cen}
    return out


def parse_m28_moves(path: Path):
    """{(shape, col): standing-token} from m28.txt move lines."""
    import re
    out = {}
    pat_ok = re.compile(r"^move s(\d+) c(\d+)->(\d+):")
    pat_none = re.compile(r"^move s(\d+) c(\d+)->none: status=(\S+)")
    for ln in path.read_text(errors="replace").splitlines():
        m = pat_none.match(ln)
        if m:
            out[(int(m.group(1)), int(m.group(2)))] = m.group(3)
            continue
        m = pat_ok.match(ln)
        if m:
            out[(int(m.group(1)), int(m.group(2)))] = "ok"
    return out


def fmt_f(x):
    return "%g" % (x,)


def main():
    m16d, m15d, m28d, workd, evidd = (Path(a) for a in sys.argv[1:6])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 exact on s0+9+22)

    print("== inputs (read-only) ==")
    bins = []
    for s in [0] + M28_MOVERS:
        bins += [m16d / f"m16-v0-s{s:04d}.bin",
                 m16d / f"m16-mid-s{s:04d}.bin",
                 m16d / f"m16-full-s{s:04d}.bin"]
    bins += [m15d / "m15-v0.bin", m15d / "m15-mid.bin",
             m15d / "m15-full.bin"]
    for s in M16_TOP10:
        bins += [m16d / f"m16-v0-s{s:04d}.bin",
                 m16d / f"m16-mid-s{s:04d}.bin",
                 m16d / f"m16-full-s{s:04d}.bin"]
    for p in bins:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} "
              f"sha256={hashlib.sha256(b).hexdigest()}")
    for p in (m28d / "m28.txt", m28d / "m28-census.tsv"):
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} "
              f"sha256={hashlib.sha256(b).hexdigest()}")
    tsv = parse_m28_tsv(m28d / "m28-census.tsv")
    print(f"m28-census.tsv parsed shapes: n={len(tsv)} (want 764)")
    moves28 = parse_m28_moves(m28d / "m28.txt")
    print(f"m28.txt parsed move rows: n={len(moves28)} (want 15)")

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
        print("MISMATCH vs M17-M29 baselines: STOP, tabled.")
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

    # ---- window == interval check (DESIGN.md pinned) ----
    print("== window geometry check (dist-rows vs span interval) ==")
    geo_ok = True
    for K in KS:
        for c in NAMED8:
            lo, hi = min(S0_ROWS[c]) - K, max(S0_ROWS[c]) + K
            interval = set(range(max(0, lo), min(H, hi + 1)))
            distset = {r for r in range(H) if span_dist(r, c) <= K}
            same = interval == distset
            geo_ok = geo_ok and same
            print(f"K={K} col {c}: span=[{min(S0_ROWS[c])},{max(S0_ROWS[c])}] "
                  f"win=[{max(0, lo)},{min(H - 1, hi)}] n={len(distset)} "
                  f"interval-match={same}")
    print("window geometry: " + ("OK" if geo_ok else
                                 "MISMATCH: tabled (rule still runs)"))

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
        named_y = sum(len(v) for v in colrows.values())
        priv = t & ~t0
        pcols = priv_y_cols(priv, pl, pr, pc)
        npuv = int(priv.sum()) - sum(len(v) for v in pcols.values())
        per[s] = {"tail": nt, "j": jj, "rs": xd, "colrows": colrows,
                  "pcols": pcols, "npuv": npuv,
                  "npriv": int(priv.sum()),
                  "nmiss": int((t0 & ~t).sum()),
                  "nout": nt - named_y}
    fold = hashlib.sha256("".join(loo_hexes).encode()).hexdigest()
    print(f"triplet fold sha (764x3 bins): {fold}")
    print(f"R_s vs loo mismatches: n={len(rs_bad)} {rs_bad[:20]}")
    print(f"delta==0 violations: n={d0_bad} shapes")
    print(f"shapes recorded: n={len(per)} (want 764)")
    print(f"(full-pass wall: {time.time() - t1:.1f}s)")
    if rs_bad or d0_bad or len(per) != 764:
        print("FULL-PASS MISMATCH: STOP, tabled.")
        return

    # ---- exact-match M28 guard (TSV + movers + standings or stop) ----
    print("== exact-match M28 guard (TSV + movers + standings or stop) ==")
    t1 = time.time()
    exact_ok = True
    tsv_bad = 0
    for s in range(764):
        rec = per[s]
        cen = census_of_shape(rec["colrows"])
        rec["cen"] = cen
        mv = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
        rec["moved"] = mv
        t = tsv[s]
        if (rec["tail"] != t["tail"] or f"{rec['j']:.4f}" != t["j"]
                or any(cen[c]["n"] != t["cen"][c]["n"]
                       or cen[c]["ov"] != t["cen"][c]["ov"]
                       or cen[c]["pres"] != t["cen"][c]["pres"]
                       for c in NAMED8)):
            tsv_bad += 1
            exact_ok = False
            if tsv_bad <= 3:
                print(f"TSV MISMATCH s{s}: recomputed tail={rec['tail']} "
                      f"J={rec['j']:.4f} vs tsv tail={t['tail']} J={t['j']}")
    print(f"TSV match on all 764: bad={tsv_bad}")
    movers = sorted(s for s in range(764) if per[s]["moved"])
    print(f"recomputed movers: n={len(movers)} shapes={movers}")
    print(f"M28 want: n=10 shapes={M28_MOVERS}")
    if movers != M28_MOVERS:
        exact_ok = False
    # exact standings vs m28.txt move lines
    exact_moves = []  # (shape, col, standing-token)
    for s in movers:
        rec = per[s]
        for c in rec["moved"]:
            if rec["cen"][c]["miss"] == 0:
                st = "none(extra-only)"
            else:
                a = assign_one(c, rec["pcols"])
                st = "ok" if a["status"] == "ok" else "none(no-cand)"
            exact_moves.append((s, c, st))
    print(f"recomputed moved cells: n={len(exact_moves)} (want 15)")
    st_bad = 0
    for (s, c, st) in exact_moves:
        w28 = moves28.get((s, c), "(NOT FOUND)")
        wpin = WANT_STANDING.get((s, c), "(NOT PINNED)")
        good = (st == w28 == wpin)
        if not good:
            st_bad += 1
            exact_ok = False
        print(f"exact move s{s} c{c}: standing={st} m28txt={w28} "
              f"pinned={wpin} match={good}")
    extra28 = sorted(set(moves28) - {(s, c) for s, c, _ in exact_moves})
    if extra28:
        exact_ok = False
        print(f"m28.txt rows with NO recomputed cell: {extra28}")
    print(f"standing mismatches: n={st_bad}")
    # below-0.95 guard (M28 constants)
    below = sorted(s for s in range(764) if per[s]["j"] < 0.95)
    j9_ok = (set(below) == set(BELOW95)
             and all(per[s]["tail"] == BELOW95[s][0]
                     and f"{per[s]['j']:.4f}" == BELOW95[s][1]
                     for s in below))
    print(f"recomputed below-0.95: n={len(below)} shapes={below} "
          f"guard={'OK' if j9_ok else 'MISMATCH'}")
    if not j9_ok:
        exact_ok = False
    print(f"(exact-guard wall: {time.time() - t1:.1f}s)")
    print("exact-match guard: " + ("OK" if exact_ok else
                                   "MISMATCH vs M28: STOP, tabled."))
    if not exact_ok:
        return

    # ---- Task 1: windowed re-run per K ----
    print("== Task 1: windowed census per K ==")
    t1 = time.time()
    wres = {}  # K -> {movers, moves, wcen per shape, offspan per shape}
    for K in KS:
        wmovers, wmoves = [], []
        wcen_all, off_all = {}, {}
        part_bad = 0
        for s in range(764):
            rec = per[s]
            wc = wcensus_of_shape(rec["colrows"], K)
            wcen_all[s] = wc
            off = offspan_sites(rec["colrows"], K)
            off_all[s] = off
            inw = sum(len(wc[c]["win"]) for c in NAMED8)
            if inw + len(off) + rec["nout"] != rec["tail"]:
                part_bad += 1
            mv = sorted(c for c in NAMED8 if wc[c]["presK"] == 0)
            rec[f"wmoved{K}"] = mv
            if mv:
                wmovers.append(s)
            for c in mv:
                st = standing_of_K(c, wc[c], rec["pcols"])
                if st == "ok":
                    a = assign_one(c, rec["pcols"])
                    wmoves.append((s, c, st, a["dest"], a["off"],
                                   a["rshift"], a["minshift"]))
                else:
                    wmoves.append((s, c, st, None, None, None, None))
        wres[K] = {"movers": wmovers, "moves": wmoves, "wcen": wcen_all,
                   "off": off_all}
        print(f"K={K}: partition violations: n={part_bad} (want 0)")
        print(f"K={K}: windowed movers: n={len(wmovers)} shapes={wmovers}")
        print(f"K={K}: windowed moved cells: n={len(wmoves)}")
        # per-column windowed mover counts
        for c in NAMED8:
            mc = [s for s in wmovers if c in per[s][f"wmoved{K}"]]
            print(f"K={K} per-col {c}: movers={len(mc)} shapes={mc}")
        # full per-cell rows
        for (s, c, st, d, o, r, mn) in wmoves:
            wc = wcen_all[s][c]
            if st == "ok":
                print(f"K={K} wmove s{s} c{c}: nK={wc['nK']}/ovK={wc['ovK']} "
                      f"->dest {d} off={o:+d} rshift={fmt_f(r)} "
                      f"minshift={mn:+d} fresh={d not in NAMED8}")
            else:
                print(f"K={K} wmove s{s} c{c}: nK={wc['nK']}/ovK={wc['ovK']} "
                      f"->none status={st}")
        # windowed census TSV
        tsvw = ["\t".join(["shape", "tail_n", "J_vs_s0"]
                          + [f"{k}{c}" for c in NAMED8
                             for k in ("n", "ov", "pres")])]
        for s in range(764):
            rec = per[s]
            row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
            for c in NAMED8:
                wc = wcen_all[s][c]
                row += [str(wc["nK"]), str(wc["ovK"]), str(wc["presK"])]
            tsvw.append("\t".join(row))
        (workd / f"m30-census-K{K}.tsv").write_text("\n".join(tsvw) + "\n")
        print(f"K={K}: windowed TSV: rows={len(tsvw) - 1} "
              f"bytes={(workd / f'm30-census-K{K}.tsv').stat().st_size}")
    # s0 windowed-present guard
    s0w_ok = all(wres[K]["wcen"][0][c]["presK"] == 1
                 for K in KS for c in NAMED8)
    print(f"s0 windowed-present on all 8 at every K: {s0w_ok}")
    print(f"(Task-1 census wall: {time.time() - t1:.1f}s)")

    # ---- Task 1.2: off-span tail tables per K ----
    print("== Task 1.2: off-span tail tables per K ==")
    for K in KS:
        off_all = wres[K]["off"]
        nsh = sum(1 for s in range(764) if off_all[s])
        ntot = sum(len(off_all[s]) for s in range(764))
        print(f"K={K}: shapes with off-span: n={nsh}; "
              f"pooled off-span sites: n={ntot}")
        for s in range(764):
            if off_all[s]:
                det = sorted(f"c{c}r{r}(d{span_dist(r, c):+d})"
                             for (c, r) in off_all[s])
                print(f"K={K} offspan s{s}: n={len(off_all[s])} "
                      f"sites=[{','.join(det)}]")
        print(f"K={K}: outside-census (non-named-col) tail per mover:")
        for s in M28_MOVERS:
            print(f"K={K} outcensus s{s}: nout={per[s]['nout']} "
                  f"tail={per[s]['tail']}")
        nout_all = sum(1 for s in range(764) if per[s]["nout"])
        print(f"K={K}: shapes with outside-census tail: n={nout_all} "
              f"(K-invariant by construction)")

    # ---- Task 1.3: delta exact-vs-windowed per K ----
    print("== Task 1.3: exact-vs-windowed deltas per K ==")
    exact_stand = {(s, c): st for (s, c, st) in exact_moves}
    for K in KS:
        wmovers = wres[K]["movers"]
        wstand = {(s, c): st for (s, c, st, _, _, _, _) in wres[K]["moves"]}
        surv = sorted(set(movers) & set(wmovers))
        unmoved = sorted(set(movers) - set(wmovers))
        newmov = sorted(set(wmovers) - set(movers))
        print(f"K={K}: exact movers surviving: n={len(surv)} shapes={surv}")
        print(f"K={K}: exact movers un-moved: n={len(unmoved)} "
              f"shapes={unmoved}")
        print(f"K={K}: newly moving (nonmover->mover): n={len(newmov)} "
              f"shapes={newmov}")
        print(f"K={K}: per-exact-cell standing changes:")
        for (s, c, st) in exact_moves:
            wst = wstand.get((s, c), "present")
            mark = "SAME" if wst == st else "CHANGED"
            print(f"K={K} cell s{s} c{c}: exact={st} windowed={wst} {mark}")
        # M29 far/near extras classification
        for (s, c, r) in FAR_EXTRAS:
            isoff = (c, r) in wres[K]["off"][s]
            print(f"K={K} far-extra s{s} c{c} r{r} "
                  f"(d{span_dist(r, c):+d}): offspan={isoff}")
        for (s, c, r) in NEAR_EXTRAS:
            isin = r in wres[K]["wcen"][s][c]["win"]
            print(f"K={K} near-extra s{s} c{c} r{r} "
                  f"(d{span_dist(r, c):+d}): inwindow={isin}")
        for (s, c, r) in MISS_ROWS:
            isin = span_dist(r, c) <= K
            print(f"K={K} missing-row s{s} c{c} r{r} "
                  f"(d{span_dist(r, c):+d}): inwindow={isin}")

    # ---- Task 2.1: standing stability per K ----
    print("== Task 2.1: standing stability (exact + per K) ==")
    ea = sum(1 for m in exact_moves if m[2] == "ok")
    ee = sum(1 for m in exact_moves if m[2] == "none(extra-only)")
    en = sum(1 for m in exact_moves if m[2] == "none(no-cand)")
    print(f"exact: movers={len(movers)} cells={len(exact_moves)} "
          f"assigned={ea} extra-only={ee} no-cand={en}")
    for K in KS:
        wm = wres[K]["moves"]
        a = sum(1 for m in wm if m[2] == "ok")
        e = sum(1 for m in wm if m[2] == "none(extra-only)")
        n = sum(1 for m in wm if m[2] == "none(no-cand)")
        print(f"K={K}: movers={len(wres[K]['movers'])} cells={len(wm)} "
              f"assigned={a} extra-only={e} no-cand={n}")

    # ---- Task 2.2: below-0.95 join per K ----
    print("== Task 2.2: below-0.95 join (exact + per K) ==")
    bset = set(below)
    mset = set(movers)
    print(f"exact join mover+below: "
          f"n={len(mset & bset)} shapes={sorted(mset & bset)}")
    print(f"exact join mover+above: "
          f"n={len(mset - bset)} shapes={sorted(mset - bset)}")
    print(f"exact join still+below: "
          f"n={len(bset - mset)} shapes={sorted(bset - mset)}")
    print(f"exact join still+above: n={764 - len(mset | bset)}")
    for K in KS:
        wset = set(wres[K]["movers"])
        print(f"K={K} join mover+below: n={len(wset & bset)} "
              f"shapes={sorted(wset & bset)}")
        print(f"K={K} join mover+above: n={len(wset - bset)} "
              f"shapes={sorted(wset - bset)}")
        print(f"K={K} join still+below: n={len(bset - wset)} "
              f"shapes={sorted(bset - wset)}")
        print(f"K={K} join still+above: n={764 - len(wset | bset)}")

    # ---- Task 2.3: K-sensitivity (adjacent-K diffs) ----
    print("== Task 2.3: K-sensitivity (adjacent-K diffs) ==")
    for (Ka, Kb) in zip(KS, KS[1:]):
        flips = []
        for s in range(764):
            for c in NAMED8:
                pa = wres[Ka]["wcen"][s][c]["presK"]
                pb = wres[Kb]["wcen"][s][c]["presK"]
                if pa != pb:
                    flips.append((s, c, pa, pb))
        ma = set(wres[Ka]["movers"])
        mb = set(wres[Kb]["movers"])
        print(f"K{Ka}->K{Kb}: flipping cells: n={len(flips)} {flips[:20]}")
        print(f"K{Ka}->K{Kb}: mover flips: n={len(ma ^ mb)} "
              f"only-K{Ka}={sorted(ma - mb)} only-K{Kb}={sorted(mb - ma)} "
              f"identical={ma == mb}")

    # ---- determinism re-run (Task 1 exact-match on s0+9+22) ----
    print("== determinism re-run (Task 1 exact on s0+9+22, second pass) ==")
    for s in (0, 9, 22):
        rec = per[s]
        ln = (f"canon s{s}: tail={rec['tail']} J={rec['j']:.4f} "
              + " ".join(f"c{c}:n{rec['cen'][c]['n']}"
                         f"/ov{rec['cen'][c]['ov']}"
                         f"/p{rec['cen'][c]['pres']}" for c in NAMED8))
        canon.append(ln)
        for c in rec["moved"]:
            if rec["cen"][c]["miss"] == 0:
                canon.append(f"canon s{s} move c{c}->none(extra-only)")
            else:
                a = assign_one(c, rec["pcols"])
                canon.append(
                    f"canon s{s} move c{c}->{a['dest']}:off={a['off']}:"
                    f"rs={fmt_f(a['rshift']) if a['rshift'] is not None else '-'}:"
                    f"{a['status']}")
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    canon2 = []
    for s in (0, 9, 22):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        if s == 0:
            t = t0
        else:
            sp = interior_sites(vv, mm, ff, bl)
            t, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        colrows = {c: y_col_rows(t, c, pl, pr, pc) for c in NAMED8}
        cen = census_of_shape(colrows)
        mv = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
        priv = t & ~t0
        pcols = priv_y_cols(priv, pl, pr, pc)
        ln = (f"canon s{s}: tail={int(t.sum())} J={jaccard(t, t0):.4f} "
              + " ".join(f"c{c}:n{cen[c]['n']}/ov{cen[c]['ov']}"
                         f"/p{cen[c]['pres']}" for c in NAMED8))
        canon2.append(ln)
        for c in mv:
            if cen[c]["miss"] == 0:
                canon2.append(f"canon s{s} move c{c}->none(extra-only)")
            else:
                a = assign_one(c, pcols)
                canon2.append(
                    f"canon s{s} move c{c}->{a['dest']}:off={a['off']}:"
                    f"rs={fmt_f(a['rshift']) if a['rshift'] is not None else '-'}:"
                    f"{a['status']}")
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon lines: n={len(canon)} vs {len(canon2)} "
          f"match={canon == canon2}")
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"sets identical: movers-s0={per[0]['moved']} "
          f"movers-s9={per[9]['moved']} movers-s22={per[22]['moved']}")

    # ---- PNG windowed-census mover map ----
    print("== PNG windowed-census mover map ==")
    arr = np.zeros((4, 764, 3), np.uint8)
    rows = [("exact", set(movers))] + [(f"K{K}", set(wres[K]["movers"]))
                                       for K in KS]
    for i, (_, mset) in enumerate(rows):
        for s in range(764):
            arr[i, s] = (0, 255, 0) if s not in mset else (255, 0, 255)
    p = workd / "m30-windowmap.png"
    Image.fromarray(arr).resize((764, 256), Image.NEAREST).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: x=shape 0..763, rows=exact,K2,K5,K10; "
          "green=still magenta=mover")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    for K in KS:
        nfar = sum(1 for (s, c, r) in FAR_EXTRAS
                   if (c, r) in wres[K]["off"][s])
        print(f"W1_FAROFF K={K}: far extras off-span {nfar}/3 (bar 3/3)")
    for K in KS:
        nnear = sum(1 for (s, c, r) in NEAR_EXTRAS
                    if r in wres[K]["wcen"][s][c]["win"])
        print(f"W2_NEARIN K={K}: near extras in-window {nnear}/2 (bar 2/2)")
    for K in KS:
        nm = len(wres[K]["movers"])
        print(f"W3_UNMOVE K={K}: windowed movers {nm} (bar <10)")
    for (Ka, Kb) in zip(KS, KS[1:]):
        same = set(wres[Ka]["movers"]) == set(wres[Kb]["movers"])
        print(f"W4_KSTABLE K{Ka}v{Kb}: mover sets identical={same} "
              f"(bar True)")
    for K in KS:
        wm = wres[K]["movers"]
        nb = sum(1 for s in wm if per[s]["j"] < 0.95)
        print(f"W5_BELOW95 K={K}: windowed movers below-0.95 {nb}/{len(wm)} "
              f"({nb / len(wm) if wm else 0:.4f}; bar >=0.50)")
    for K in KS:
        nmi = sum(1 for (s, c, r) in MISS_ROWS if span_dist(r, c) <= K)
        print(f"W6_MISSIN K={K}: missing rows in-window {nmi}/4 (bar 4/4)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=windowed+offspan+delta T2=stability+join+Ksense "
          "R=controls")


if __name__ == "__main__":
    main()
