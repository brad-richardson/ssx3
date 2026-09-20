#!/usr/bin/env python3
"""M34 unnamed-column partial scan: which shapes move unnamed columns (offline).

Usage: m34.py M16_DIR M15_DIR M28TXT M28TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m28.txt + m28-census.tsv (named census to
reproduce); raw XFB dumps, 573440 B = 640x448 YUYV. Read-only
inputs; receipt text goes to stdout (redirect to WORK_DIR/m34.txt);
unnamed census TSV + PNG heatmap to WORK_DIR (evidence copies iff
the DESIGN.md rules meet, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: unnamed scan (764x|U| matrix + movers + top-20 + delta hist)
  2: joins (named∩unnamed 2x2 + below-0.95 + 709-c298 rank)
  3: controls (control.py) + determinism + shas + Model-0 recompute
Tables, no verdicts.
"""
import hashlib
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
M28_MOVERS = [9, 22, 708, 709, 710, 711, 731, 732, 733, 734]
M29_709_C298_MISS = [28, 29, 34, 35]  # M29 REPORT.md:146
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


def fmt_f(x):
    return "%g" % (x,)


def main():
    m16d, m15d, m28t, m28tsv, workd, evidd = (Path(a) for a in sys.argv[1:7])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0+709)

    print("== inputs (read-only) ==")
    guard_bins = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
                  m16d / "m16-full-s0000.bin",
                  m16d / "m16-v0-s0709.bin", m16d / "m16-mid-s0709.bin",
                  m16d / "m16-full-s0709.bin",
                  m15d / "m15-v0.bin", m15d / "m15-mid.bin",
                  m15d / "m15-full.bin"]
    for p in guard_bins:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} "
              f"sha256={hashlib.sha256(b).hexdigest()}")
    for q in (m28t, m28tsv):
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
        print("MISMATCH vs M17-M33 baselines: STOP, tabled.")
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
    print(f"R_s vs loo mismatches: n={len(rs_bad)} {rs_bad[:20]}")
    print(f"delta==0 violations: n={d0_bad} shapes")
    print(f"shapes recorded: n={len(per)} (want 764)")
    print(f"(full-pass wall: {time.time() - t1:.1f}s)")
    if rs_bad or d0_bad or len(per) != 764:
        print("FULL-PASS MISMATCH: STOP, tabled.")
        return

    # ---- named census guard (M28 TSV match) ----
    print("== named census guard (M28 TSV match or stop) ==")
    tsv_lines = m28tsv.read_text(errors="replace").splitlines()
    want_hdr = "\t".join(["shape", "tail_n", "J_vs_s0"]
                         + [f"{k}{c}" for c in NAMED8
                            for k in ("n", "ov", "pres")])
    print(f"m28-census.tsv rows={len(tsv_lines) - 1} "
          f"hdr_match={tsv_lines[0] == want_hdr}")
    named_ok = tsv_lines[0] == want_hdr and len(tsv_lines) == 765
    named_movers = []
    first_bad = None
    for s in range(764):
        rec = per[s]
        colrows = {c: rec["ycols"].get(c, []) for c in NAMED8}
        cen = census_of_shape(colrows)
        rec["ncen"] = cen
        mv = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
        rec["nmoved"] = mv
        if mv:
            named_movers.append(s)
        row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in NAMED8:
            row += [str(cen[c]["n"]), str(cen[c]["ov"]),
                    str(cen[c]["pres"])]
        if "\t".join(row) != tsv_lines[s + 1]:
            named_ok = False
            if first_bad is None:
                first_bad = s
    print(f"named TSV full match (764 rows): {named_ok}"
          + ("" if named_ok else f" first_bad_shape={first_bad}"))
    if first_bad is not None:
        print(f"m28 row: {tsv_lines[first_bad + 1]}")
        rec = per[first_bad]
        row = [str(first_bad), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in NAMED8:
            row += [str(rec["ncen"][c]["n"]), str(rec["ncen"][c]["ov"]),
                    str(rec["ncen"][c]["pres"])]
        print(f"mine row: {'\t'.join(row)}")
    print(f"named movers: {named_movers} (want {M28_MOVERS})")
    if named_movers != M28_MOVERS:
        named_ok = False
    print("named guard: " + ("OK" if named_ok else
                             "MISMATCH vs M28: STOP, tabled."))
    if not named_ok:
        return

    # ---- UNNAMED domain + s0 rows ----
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
    print(f"UNNAMED (union minus named8): n={len(UNNAMED)}")
    print(f"s0-bearing unnamed (n0>0): n={len(n0pos)} cols={n0pos}")
    print(f"pure-private unnamed (n0==0): n={len(n0zero)}")
    for c in n0pos:
        print(f"s0 unnamed col {c}: n={len(s0u[c])} "
              f"rows=[{','.join(map(str, s0u[c]))}]")
    print(f"c298 in UNNAMED: {298 in UNNAMED} "
          f"c341 in UNNAMED: {341 in UNNAMED}")

    # ---- 709-c298 guard (M29 match or stop) ----
    print("== 709-c298 guard (M29 match or stop) ==")
    r0_298 = s0u.get(298, None)
    r709_298 = per[709]["ycols"].get(298, [])
    miss298 = sorted(set(r0_298 or []) - set(r709_298))
    ov298 = len(set(r709_298) & set(r0_298 or []))
    print(f"s0 c298: n={len(r0_298 or [])} rows={r0_298}")
    print(f"s709 c298: n={len(r709_298)} rows={r709_298} ov={ov298}")
    print(f"709-c298 missing={miss298} (want {M29_709_C298_MISS})")
    print(f"709 tail={per[709]['tail']} (want 97) "
          f"J={per[709]['j']:.4f} (want 0.9510)")
    c298_ok = (miss298 == M29_709_C298_MISS
               and per[709]["tail"] == 97
               and f"{per[709]['j']:.4f}" == "0.9510"
               and 298 in UNNAMED)
    print("c298 guard: " + ("OK" if c298_ok else
                            "MISMATCH vs M29: STOP, tabled."))
    if not c298_ok:
        return

    # ---- Task 1: unnamed census matrix ----
    print(f"== Task 1: unnamed census matrix (764x{len(UNNAMED)}) ==")
    t1 = time.time()
    tsv = ["\t".join(["shape", "tail_n", "J_vs_s0"]
                     + [f"{k}{c}" for c in UNNAMED
                        for k in ("n", "ov", "pres")])]
    movers, kcount = [], {}
    for s in range(764):
        rec = per[s]
        cen = census_unnamed_of(rec["ycols"], s0u)
        rec["ucen"] = cen
        mv = sorted(c for c in UNNAMED if cen[c]["pres"] == 0)
        rec["umoved"] = mv
        if mv:
            movers.append(s)
            kcount[len(mv)] = kcount.get(len(mv), 0) + 1
        row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in UNNAMED:
            row += [str(cen[c]["n"]), str(cen[c]["ov"]),
                    str(cen[c]["pres"])]
        tsv.append("\t".join(row))
    (workd / "m34-census.tsv").write_text("\n".join(tsv) + "\n")
    print(f"census TSV: {(workd / 'm34-census.tsv')} "
          f"rows={len(tsv) - 1} bytes={(workd / 'm34-census.tsv').stat().st_size}")
    print(f"unnamed movers (>=1 absent): n={len(movers)}")
    print(f"unnamed mover shapes: {movers}")
    print("moved-count hist k: " + " ".join(
        f"{k}:{kcount.get(k, 0)}" for k in sorted(kcount)))
    for s in movers:
        print(f"mover s{s}: tail={per[s]['tail']} "
              f"J={per[s]['j']:.4f} k={len(per[s]['umoved'])} "
              f"cols={per[s]['umoved']}")
    print(f"(Task-1 wall: {time.time() - t1:.1f}s)")

    # ---- Task 1: per-column mover counts + delta hist ----
    print("== Task 1: per-column mover counts ==")
    colstat = {}
    for c in UNNAMED:
        mc = [s for s in movers if c in per[s]["umoved"]]
        mo = sum(1 for s in mc if per[s]["ucen"][c]["miss"] > 0
                 and per[s]["ucen"][c]["extra"] == 0)
        eo = sum(1 for s in mc if per[s]["ucen"][c]["miss"] == 0
                 and per[s]["ucen"][c]["extra"] > 0)
        mx = len(mc) - mo - eo
        colstat[c] = {"movers": len(mc), "mo": mo, "eo": eo, "mx": mx}
    top20 = sorted(UNNAMED, key=lambda c: (-colstat[c]["movers"], c))[:20]
    print("top-20 unnamed cols by mover count:")
    for c in top20:
        st = colstat[c]
        print(f"col {c}: movers={st['movers']} "
              f"rate={st['movers'] / 764:.4f} n0={len(s0u[c])} "
              f"miss-only={st['mo']} extra-only={st['eo']} mixed={st['mx']}")
    print(f"cols with >=1 mover: "
          f"{sum(1 for c in UNNAMED if colstat[c]['movers'])}")

    print("== Task 1: row-delta distribution ==")
    deltas = []
    mo_tot = eo_tot = mx_tot = wipe_tot = fresh_tot = 0
    n0pos_moves = n0zero_moves = 0
    for s in movers:
        for c in per[s]["umoved"]:
            e = per[s]["ucen"][c]
            deltas.append(e["delta"])
            if e["miss"] > 0 and e["extra"] == 0:
                mo_tot += 1
            elif e["miss"] == 0 and e["extra"] > 0:
                eo_tot += 1
            else:
                mx_tot += 1
            if e["ov"] == 0 and len(s0u[c]) > 0 and e["n"] == 0:
                wipe_tot += 1
            if len(s0u[c]) == 0:
                fresh_tot += 1
                n0zero_moves += 1
            else:
                n0pos_moves += 1
    nmc = len(deltas)
    print(f"unnamed moved cells: n={nmc} missing-only={mo_tot} "
          f"extra-only={eo_tot} mixed={mx_tot}")
    print(f"full wipes={wipe_tot} fresh-col moves={fresh_tot} "
          f"n0>0 moves={n0pos_moves} n0==0 moves={n0zero_moves}")
    if deltas:
        vals, cnts = np.unique(np.array(deltas), return_counts=True)
        print("delta hist: " + " ".join(f"{int(v)}:{int(n)}"
                                        for v, n in zip(vals, cnts)))
        a = np.asarray(deltas, dtype=np.float64)
        print(f"delta summary: min={a.min():.0f} med={np.median(a):.1f} "
              f"mean={a.mean():.4f} max={a.max():.0f}")
        print(f"delta<=2: {sum(1 for d in deltas if d <= 2)} "
              f"ov==0: {sum(1 for s in movers for c in per[s]['umoved'] if per[s]['ucen'][c]['ov'] == 0)}")
    else:
        print("delta hist: (no unnamed moves)")

    # ---- Task 2.1: named∩unnamed 2x2 ----
    print("== Task 2.1: named x unnamed 2x2 ==")
    nset, uset = set(named_movers), set(movers)
    for tag, ss in (("named+unnamed", sorted(nset & uset)),
                    ("named-only", sorted(nset - uset)),
                    ("unnamed-only", sorted(uset - nset))):
        print(f"join {tag}: n={len(ss)} shapes={ss}")
    print(f"join still+still: n={764 - len(nset | uset)}")

    # ---- Task 2.2: below-0.95 join ----
    print("== Task 2.2: below-0.95 join ==")
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
                              "MISMATCH vs M28: join stopped, "
                              "Tasks 1-2.1 stand."))
    if j9_ok:
        bset = set(below)
        for tag, ss in (("unnamed+below", sorted(uset & bset)),
                        ("unnamed+above", sorted(uset - bset)),
                        ("still+below", sorted(bset - uset))):
            print(f"join {tag}: n={len(ss)} shapes={ss}")
        print(f"join still+above: n={764 - len(uset | bset)}")
        for s in sorted(bset - nset):  # named-still+below (want 2/3/700)
            u = per[s]["umoved"]
            print(f"named-still+below s{s}: tail={per[s]['tail']} "
                  f"J={per[s]['j']:.4f} unnamed_k={len(u)} cols={u}")

    # ---- Task 2.3: 709-c298 rank ----
    print("== Task 2.3: 709-c298 rank ==")
    e298 = per[709]["ucen"][298]
    d298 = e298["delta"]
    print(f"709-c298: n={e298['n']} ov={e298['ov']} "
          f"miss={e298['miss']} extra={e298['extra']} delta={d298}")
    if deltas:
        import statistics as _st

        med = _st.median(deltas)
        print(f"unnamed delta median={med} seed>=median: {d298 >= med}")
        print(f"cells delta>4: {sum(1 for d in deltas if d > 4)} "
              f"==4: {sum(1 for d in deltas if d == 4)} "
              f">=4: {sum(1 for d in deltas if d >= 4)} "
              f"(of {nmc}, seed included)")

    # ---- determinism re-run (Task 1 on s0+709, second pass) ----
    print("== determinism re-run (Task 1 on s0+709, second pass) ==")
    for s in (0, 709):
        rec = per[s]
        ln = (f"canon s{s}: tail={rec['tail']} J={rec['j']:.4f} "
              + " ".join(f"c{c}:n{rec['ucen'][c]['n']}"
                         f"/ov{rec['ucen'][c]['ov']}"
                         f"/p{rec['ucen'][c]['pres']}"
                         f"/d{rec['ucen'][c]['delta']}" for c in UNNAMED))
        canon.append(ln)
        canon.append(f"canon s{s} umoved={rec['umoved']}")
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    canon2 = []
    for s in (0, 709):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        if s == 0:
            t = t0
        else:
            sp = interior_sites(vv, mm, ff, bl)
            t, _ = tail_bulk_masks(sp["mask"], sp["delta"])
        ycols = tail_y_cols(t, pl, pr, pc)
        cen = census_unnamed_of(ycols, s0u)
        mv = sorted(c for c in UNNAMED if cen[c]["pres"] == 0)
        ln = (f"canon s{s}: tail={int(t.sum())} J={jaccard(t, t0):.4f} "
              + " ".join(f"c{c}:n{cen[c]['n']}/ov{cen[c]['ov']}"
                         f"/p{cen[c]['pres']}/d{cen[c]['delta']}"
                         for c in UNNAMED))
        canon2.append(ln)
        canon2.append(f"canon s{s} umoved={mv}")
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"lines match={[a == b for a, b in zip(canon, canon2)]} "
          f"n={len(canon)}")
    print(f"sets identical: umoved-s0={per[0]['umoved']} "
          f"umoved-709={per[709]['umoved']}")

    # ---- PNG unnamed census heatmap ----
    print("== PNG unnamed census heatmap ==")
    arr = np.zeros((len(UNNAMED), 764, 3), np.uint8)
    for s in range(764):
        for i, c in enumerate(UNNAMED):
            arr[i, s] = (0, 255, 0) if per[s]["ucen"][c]["pres"] else (255, 0, 255)
    p = workd / "m34-census.png"
    Image.fromarray(arr).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880) "
          f"dims=764x{len(UNNAMED)}")
    print("legend: x=shape 0..763, y=unnamed col ascending; "
          "green=present magenta=moved")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    nm = len(movers)
    n_in_u = sum(1 for s in named_movers if s in uset)
    print(f"H1_NAMEDINUNNAMED: named movers moving >=1 unnamed "
          f"{n_in_u}/10 ({n_in_u / 10:.4f}; bar >=0.50)")
    still_u = sum(1 for s in movers if s not in nset)
    print(f"H2_STILLMOVE: unnamed movers named-still {still_u}/{nm} "
          f"({still_u / nm if nm else 0:.4f}; bar >=0.50)")
    if deltas:
        import statistics as _st2

        small = sum(1 for d in deltas if d <= 2)
        ov0 = sum(1 for s in movers for c in per[s]['umoved']
                  if per[s]["ucen"][c]["ov"] == 0)
        print(f"H3_SMALLDELTA: delta<=2 {small}/{nmc} "
              f"({small / nmc:.4f}; bar >=0.50)")
        print(f"H4_WIPE: ov==0 {ov0}/{nmc} ({ov0 / nmc:.4f}; bar >=0.50)")
    else:
        print(f"H3_SMALLDELTA: no unnamed moves (reads 0; bar >=0.50)")
        print(f"H4_WIPE: no unnamed moves (reads 0; bar >=0.50)")
    b5 = sum(1 for s in movers if per[s]["j"] < 0.95)
    print(f"H5_BELOW95: unnamed movers below-0.95 {b5}/{nm} "
          f"({b5 / nm if nm else 0:.4f}; bar >=0.50)")
    if deltas:
        import statistics as _st3

        med = _st3.median(deltas)
        print(f"H6_C298RANK: seed delta {d298} vs median {med}: "
              f"{d298 >= med} (bar: seed>=median)")
    else:
        print("H6_C298RANK: no unnamed moves (reads False)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=unnamed-scan T2=joins R=controls")


if __name__ == "__main__":
    main()
