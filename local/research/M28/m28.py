#!/usr/bin/env python3
"""M28 streak-column census: which shapes move which columns, by how far (offline).

Usage: m28.py M16_DIR M15_DIR M27TXT WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m27.txt (733/731 swap rows to reproduce);
raw XFB dumps, 573440 B = 640x448 YUYV. Read-only inputs; receipt
text goes to stdout (redirect to WORK_DIR/m28.txt); census TSV +
PNG heatmap to WORK_DIR (evidence copies iff the DESIGN.md rules
meet, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: presence census (764x8 matrix + movers + pairing)
  2: displacement census (offsets + dests + below-0.95 join)
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
SWAP733 = {"tail": 100, "j": "0.6694",
           "miss": [301, 321], "dest": {301: 303, 321: 323},
           "privrows": {303: list(range(25, 34)), 323: list(range(25, 35))}}
SWAP731 = {"tail": 100, "j": "0.6833",
           "miss": [257, 277], "dest": {257: 259, 277: 279},
           "privrows": {259: list(range(25, 34)), 279: list(range(25, 34))}}
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
    """Per-named-column presence: exact-match rule (DESIGN.md pinned)."""
    out = {}
    for c in NAMED8:
        rs, r0 = colrows[c], S0_ROWS[c]
        ov = len(set(rs) & set(r0))
        out[c] = {"n": len(rs), "ov": ov,
                  "pres": 1 if rs == r0 else 0,
                  "miss": len(r0) - ov, "extra": len(rs) - ov}
    return out


def assign_one(c: int, privcols):
    """Displacement assignment for moved column c (DESIGN.md pinned).

    Returns dict(dest, off, rshift, minshift, status, npriv).
    """
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


def fmt_f(x):
    return "%g" % (x,)


def main():
    m16d, m15d, m27t, workd, evidd = (Path(a) for a in sys.argv[1:6])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0+733+731)

    print("== inputs (read-only) ==")
    guard_bins = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
                  m16d / "m16-full-s0000.bin",
                  m16d / "m16-v0-s0733.bin", m16d / "m16-mid-s0733.bin",
                  m16d / "m16-full-s0733.bin",
                  m16d / "m16-v0-s0731.bin", m16d / "m16-mid-s0731.bin",
                  m16d / "m16-full-s0731.bin",
                  m15d / "m15-v0.bin", m15d / "m15-mid.bin",
                  m15d / "m15-full.bin"]
    for p in guard_bins:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} "
              f"sha256={hashlib.sha256(b).hexdigest()}")
    m27b = m27t.read_bytes()
    print(f"input {m27t}: bytes={len(m27b)} "
          f"sha256={hashlib.sha256(m27b).hexdigest()}")
    m27lines = m27b.decode(errors="replace").splitlines()
    for shp in (733, 731):
        hit = [ln for ln in m27lines if ln.startswith(f"s{shp} tail n=")]
        print(f"m27.txt target tail s{shp}: "
              + (hit[0] if hit else "(NOT FOUND)"))
    for ln in m27lines:
        if ln.startswith("streak col ") and "s0 n=" in ln:
            print(f"m27.txt target {ln}")

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
        print("MISMATCH vs M17-M27 baselines: STOP, tabled.")
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
        priv = t & ~t0
        pcols = priv_y_cols(priv, pl, pr, pc)
        npuv = int(priv.sum()) - sum(len(v) for v in pcols.values())
        per[s] = {"tail": nt, "j": jj, "rs": xd, "colrows": colrows,
                  "pcols": pcols, "npuv": npuv,
                  "npriv": int(priv.sum()),
                  "nmiss": int((t0 & ~t).sum())}
    fold = hashlib.sha256("".join(loo_hexes).encode()).hexdigest()
    print(f"triplet fold sha (764x3 bins): {fold}")
    print(f"R_s vs loo mismatches: n={len(rs_bad)} {rs_bad[:20]}")
    print(f"delta==0 violations: n={d0_bad} shapes")
    print(f"shapes recorded: n={len(per)} (want 764)")
    print(f"(full-pass wall: {time.time() - t1:.1f}s)")
    if rs_bad or d0_bad or len(per) != 764:
        print("FULL-PASS MISMATCH: STOP, tabled.")
        return

    # ---- 733/731 swap guard (M27 match) ----
    print("== 733/731 swap guard (M27 match or stop) ==")
    swap_ok = True
    for s, SW in ((733, SWAP733), (731, SWAP731)):
        rec = per[s]
        cen = census_of_shape(rec["colrows"])
        moved = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
        print(f"s{s}: tail={rec['tail']} (want {SW['tail']}) "
              f"J={rec['j']:.4f} (want {SW['j']}) moved={moved} "
              f"(want {SW['miss']})")
        if rec["tail"] != SW["tail"] or f"{rec['j']:.4f}" != SW["j"]:
            swap_ok = False
        if moved != SW["miss"]:
            swap_ok = False
        for c in SW["miss"]:
            a = assign_one(c, rec["pcols"])
            want_d = SW["dest"][c]
            print(f"s{s} move c{c}: dest={a['dest']} (want {want_d}) "
                  f"off={a['off']} (want +2) npriv={a['npriv']} "
                  f"prows={rec['pcols'].get(a['dest'] or -1, [])}")
            if a["dest"] != want_d or a["off"] != 2:
                swap_ok = False
            if rec["pcols"].get(want_d) != SW["privrows"][want_d]:
                swap_ok = False
    print("swap guard: " + ("OK" if swap_ok else
                            "MISMATCH vs M27: STOP, tabled."))
    if not swap_ok:
        return

    # ---- Task 1: census matrix ----
    print("== Task 1: census matrix (764x8) ==")
    t1 = time.time()
    tsv = ["\t".join(["shape", "tail_n", "J_vs_s0"]
                     + [f"{k}{c}" for c in NAMED8
                        for k in ("n", "ov", "pres")])]
    movers, kcount = [], {}
    for s in range(764):
        rec = per[s]
        cen = census_of_shape(rec["colrows"])
        rec["cen"] = cen
        mv = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
        rec["moved"] = mv
        if mv:
            movers.append(s)
            kcount[len(mv)] = kcount.get(len(mv), 0) + 1
        row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in NAMED8:
            row += [str(cen[c]["n"]), str(cen[c]["ov"]),
                    str(cen[c]["pres"])]
        tsv.append("\t".join(row))
    (workd / "m28-census.tsv").write_text("\n".join(tsv) + "\n")
    print(f"census TSV: {(workd / 'm28-census.tsv')} "
          f"rows={len(tsv) - 1} bytes={(workd / 'm28-census.tsv').stat().st_size}")
    print(f"movers (>=1 absent): n={len(movers)}")
    print(f"mover shapes: {movers}")
    print("moved-count hist k: " + " ".join(
        f"{k}:{kcount.get(k, 0)}" for k in range(1, 9)))
    for c in NAMED8:
        mc = [s for s in movers if c in per[s]["moved"]]
        mo = sum(1 for s in mc if per[s]["cen"][c]["miss"] > 0
                 and per[s]["cen"][c]["extra"] == 0)
        eo = sum(1 for s in mc if per[s]["cen"][c]["miss"] == 0
                 and per[s]["cen"][c]["extra"] > 0)
        mx = len(mc) - mo - eo
        print(f"per-col {c}: movers={len(mc)} "
              f"rate={len(mc) / 764:.4f} miss-only={mo} "
              f"extra-only={eo} mixed={mx}")
    print("pair co-occurrence (shapes moving both; diag=per-col):")
    header = "col\\" + "".join(f"{c:>6}" for c in NAMED8)
    print(header)
    for a in NAMED8:
        cells = []
        for b in NAMED8:
            n = sum(1 for s in movers
                    if a in per[s]["moved"] and b in per[s]["moved"])
            cells.append(f"{n:>6}")
        print(f"{a:>3}" + "".join(cells))
    pats = {}
    for s in movers:
        pats.setdefault(tuple(per[s]["moved"]), []).append(s)
    print(f"distinct moved-sets: n={len(pats)}")
    for pat in sorted(pats, key=lambda p: (-len(pats[p]), p)):
        print(f"pattern {list(pat)}: n={len(pats[pat])} shapes={pats[pat]}")
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2: displacement ----
    print("== Task 2: displacement census ==")
    t1 = time.time()
    moves = []  # (shape, miss col, dest, off, rshift, minshift, status)
    singletons = 0
    for s in movers:
        rec = per[s]
        for c in rec["moved"]:
            if rec["cen"][c]["miss"] == 0:
                moves.append((s, c, None, None, None, None,
                              "none(extra-only)"))
                continue
            a = assign_one(c, rec["pcols"])
            st = "ok" if a["status"] == "ok" else "none(no-cand)"
            moves.append((s, c, a["dest"], a["off"], a["rshift"],
                          a["minshift"], st))
        singletons += sum(1 for v in rec["pcols"].values() if len(v) == 1)
    npuv_tot = sum(rec["npuv"] for rec in per.values())
    print(f"moved cells: n={len(moves)} assigned="
          f"{sum(1 for m in moves if m[6] == 'ok')} extra-only="
          f"{sum(1 for m in moves if m[6] == 'none(extra-only)')} "
          f"no-cand={sum(1 for m in moves if m[6] == 'none(no-cand)')}")
    print(f"singleton private Y-cols (movers): n={singletons}")
    print(f"private U/V sites (all 764): n={npuv_tot} (want 0)")
    offs = [m[3] for m in moves if m[6] == "ok"]
    if offs:
        vals, cnts = np.unique(np.array(offs), return_counts=True)
        print("offset hist: " + " ".join(f"{int(v)}:{int(n)}"
                                         for v, n in zip(vals, cnts)))
        a = np.asarray(offs, dtype=np.float64)
        print(f"offset summary: min={a.min():.0f} med={np.median(a):.0f} "
              f"mean={a.mean():.4f} max={a.max():.0f}")
    else:
        print("offset hist: (none assigned)")
    rs_ = [m[4] for m in moves if m[6] == "ok"]
    if rs_:
        vals, cnts = np.unique(np.array(rs_), return_counts=True)
        print("rowshift hist: " + " ".join(f"{fmt_f(v)}:{int(n)}"
                                           for v, n in zip(vals, cnts)))
        a = np.asarray(rs_, dtype=np.float64)
        print(f"rowshift summary: min={fmt_f(a.min())} "
              f"med={fmt_f(np.median(a))} mean={a.mean():.4f} "
              f"max={fmt_f(a.max())}")
    else:
        print("rowshift hist: (none assigned)")
    dests = {}
    for m in moves:
        if m[6] == "ok":
            dests[m[2]] = dests.get(m[2], 0) + 1
    print("dest cols: " + (" ".join(f"{d}:{dests[d]}"
                                    for d in sorted(dests))
                            if dests else "(none)"))
    fresh = sum(n for d, n in dests.items() if d not in NAMED8)
    named = sum(dests.values()) - fresh
    print(f"fresh-vs-named: fresh={fresh} named={named} "
          f"(of {sum(dests.values())} assigned)")
    for (s, c, d, o, r, mn, st) in moves:
        if st == "ok":
            print(f"move s{s} c{c}->{d}: off={o:+d} rshift={fmt_f(r)} "
                  f"minshift={mn:+d} fresh={d not in NAMED8}")
        else:
            print(f"move s{s} c{c}->none: status={st}")
    print(f"(Task-2 wall: {time.time() - t1:.1f}s)")

    # ---- Task 2.3: below-0.95 join ----
    print("== Task 2.3: below-0.95 join ==")
    below = sorted(s for s in range(764) if per[s]["j"] < 0.95)
    print(f"recomputed below-0.95: n={len(below)} shapes={below}")
    j9_ok = (set(below) == set(BELOW95)
             and all(per[s]["tail"] == BELOW95[s][0]
                     and f"{per[s]['j']:.4f}" == BELOW95[s][1]
                     for s in below))
    for s in below:
        w = BELOW95.get(s)
        print(f"below s{s}: tail={per[s]['tail']} "
              f"(want {w[0] if w else '?'}) J={per[s]['j']:.4f} "
              f"(want {w[1] if w else '?'})")
    print("9-list guard: " + ("OK" if j9_ok else
                              "MISMATCH vs M22: join stopped, "
                              "Tasks 1-2.2 stand."))
    if j9_ok:
        mset, bset = set(movers), set(below)
        cells = {"mover+below": sorted(mset & bset),
                 "mover+above": sorted(mset - bset),
                 "still+below": sorted(bset - mset),
                 "still+above": 764 - len(mset | bset)}
        for k in ("mover+below", "mover+above", "still+below"):
            print(f"join {k}: n={len(cells[k])} shapes={cells[k]}")
        print(f"join still+above: n={cells['still+above']}")
    else:
        cells = None

    # ---- determinism re-run (Task 1 on s0+733+731, second pass) ----
    print("== determinism re-run (Task 1 on s0+733+731, second pass) ==")
    for s in (0, 733, 731):
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
    for s in (0, 733, 731):
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
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"sets identical: movers-s0={per[0]['moved']} "
          f"movers-733={per[733]['moved']} movers-731={per[731]['moved']}")

    # ---- PNG census heatmap ----
    print("== PNG census heatmap ==")
    arr = np.zeros((8, 764, 3), np.uint8)
    for s in range(764):
        for i, c in enumerate(NAMED8):
            arr[i, s] = (0, 255, 0) if per[s]["cen"][c]["pres"] else (255, 0, 255)
    p = workd / "m28-census.png"
    Image.fromarray(arr).resize((764, 256), Image.NEAREST).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: x=shape 0..763, y=named col "
          + ",".join(map(str, NAMED8)) + "; green=present magenta=moved")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    nm = len(movers)
    k2 = sum(1 for s in movers if len(per[s]["moved"]) == 2)
    print(f"H1_PAIR: k==2 movers {k2}/{nm} "
          f"({k2 / nm if nm else 0:.4f}; bar >=0.50)")
    na = len(offs)
    p2 = sum(1 for o in offs if o == 2)
    print(f"H2_PLUS2: off==+2 {p2}/{na} "
          f"({p2 / na if na else 0:.4f}; bar >=0.50)")
    print(f"H3_FRESH: fresh dests {fresh}/{na} "
          f"({fresh / na if na else 0:.4f}; bar >=0.50)")
    nmc = len(moves)
    conc = sum(1 for m in moves if m[1] in (257, 277, 301, 321))
    print(f"H4_CONCENTRATE: in-{{257,277,301,321}} {conc}/{nmc} "
          f"({conc / nmc if nmc else 0:.4f}; bar >=0.50)")
    b5 = sum(1 for s in movers if per[s]["j"] < 0.95)
    print(f"H5_BELOW95: movers below-0.95 {b5}/{nm} "
          f"({b5 / nm if nm else 0:.4f}; bar >=0.50)")
    size2 = {p: v for p, v in pats.items() if len(p) == 2}
    if size2:
        bp = max(size2, key=lambda p: len(size2[p]))
        print(f"H6_PAIRREPEAT: modal size-2 set {list(bp)} "
              f"on {len(size2[bp])} shapes (bar >=2)")
    else:
        print("H6_PAIRREPEAT: no size-2 moved sets (reads 0; bar >=2)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=census T2=displace+join R=controls")


if __name__ == "__main__":
    main()

