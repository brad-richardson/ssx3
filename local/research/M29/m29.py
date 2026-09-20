#!/usr/bin/env python3
"""M29 partial-move attribution: per-byte delta-row tables (offline).

Usage: m29.py M16_DIR M15_DIR M28_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m28.txt + m28-census.tsv (partial-move n/ov/
standing rows to reproduce); raw XFB dumps, 573440 B = 640x448
YUYV. Read-only inputs; receipt text goes to stdout (redirect to
WORK_DIR/m29.txt); PNG delta-row map to WORK_DIR (evidence copy
iff the DESIGN.md rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: delta-row lists + per-site tables + near-miss + position joins
  2: extra/missing comparison + 734-c342 + row-tolerant standings
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
M19_REMOVED = [4888, 1208, 649, 448, 248, 244, 191, 174, 190, 202]
M19_REMOVED_BANDS = [[3415, 1442, 31], [824, 384, 0], [186, 463, 0],
                     [0, 0, 448], [0, 0, 248], [0, 0, 244], [0, 0, 191],
                     [0, 0, 174], [0, 0, 190], [0, 187, 15]]
M18_P1_EDGE_S0 = "0 1 2 2 4 6 8 12 18 29 176"
NAMED8 = [257, 277, 296, 301, 321, 340, 342, 343]
NAMED_COLS = [257, 277, 296, 301, 321, 340, 341, 342, 343]  # posjoin set (M27)
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
PARTIALS = {22: 296, 708: 296, 709: 301, 710: 340, 9: 321, 734: 342}
ANALYZED = sorted(PARTIALS)
WANT_STANDING = {22: "none(extra-only)", 9: "none(extra-only)",
                 734: "none(extra-only)", 708: "none(no-cand)",
                 709: "none(no-cand)", 710: "none(no-cand)"}


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


def standing_of(c, cen_c, pcols):
    """M28 standing rule verbatim: extra-only / ok / no-cand."""
    if cen_c["miss"] == 0:
        return "none(extra-only)"
    a = assign_one(c, pcols)
    return "ok" if a["status"] == "ok" else "none(no-cand)"


def fmt_f(x):
    return "%g" % (x,)


PNAME = ("Y", "U", "V")


def attrib_lines(tag, priv, miss, shared, dA, mA, dB, mB,
                 v0A, fullA, v0B, fullB):
    """Task 1.1/1.2: per-site private + missing rows with cross values.

    A = s0, B = other shape. priv = extra-row sites (tail on B),
    miss = missing-row sites (tail on A). Returns (lines,
    summary_dict). Offsets in ascending order. (M27 verbatim.)
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
    (M27 verbatim.)
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


def span_pos(r, c):
    """EDGE iff row at/beyond the s0 span ends, else INTERIOR; TOP/BOTTOM half."""
    sp = S0_ROWS[c]
    edge = "EDGE" if (r <= min(sp) or r >= max(sp)) else "INTERIOR"
    half = "TOP" if r <= S0_MED[c] else "BOTTOM"
    return edge, half


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


def main():
    m16d, m15d, m28d, workd, evidd = (Path(a) for a in sys.argv[1:6])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1 on s0+22+708)

    print("== inputs (read-only) ==")
    bins = []
    for s in [0] + ANALYZED:
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
    for s in ANALYZED:
        t = tsv[s]
        c = PARTIALS[s]
        print(f"m28 target s{s}: tail={t['tail']} J={t['j']} "
              f"c{c}:n={t['cen'][c]['n']}/ov={t['cen'][c]['ov']}/"
              f"p={t['cen'][c]['pres']}")
    moves28 = parse_m28_moves(m28d / "m28.txt")
    for s in ANALYZED:
        print(f"m28 target standing s{s} c{PARTIALS[s]}: "
              f"{moves28.get((s, PARTIALS[s]), '(NOT FOUND)')} "
              f"(want {WANT_STANDING[s]})")

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
    ym0 = split_planes(np.frombuffer(mid0, np.uint8))[0]
    b0 = synth_w_bytes(v0, full0, 0.5)
    r0 = xdiff(b0, mid0)[0]
    f0 = f"{fnv1a(b0):016x}"
    print(f"m15 baseline: R_0={r15} fnv={f15} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0} fnv={f0} (want {R0_M16} / {FNV_S0})")
    if r0 != R0_M16 or r15 != R0_M15 or f0 != FNV_S0 or f15 != FNV_M15:
        print("MISMATCH vs M17-M28 baselines: STOP, tabled.")
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

    # ---- full 764 pass (R_s vs loo + cell/tail + census fields) ----
    print("== full 764 pass (R_s vs loo + cell/tail + census fields) ==")
    t1 = time.time()
    loo_hexes = []
    per = {}
    trips = {}
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
        per[s] = {"tail": nt, "j": jj, "rs": xd, "colrows": colrows,
                  "pcols": pcols, "npriv": int(priv.sum()),
                  "nmiss": int((t0 & ~t).sum())}
        if s in PARTIALS or s in M28_MOVERS:
            trips[s] = {"v": vv, "m": mm, "f": ff, "b": bl,
                        "mask": sp["mask"], "delta": sp["delta"], "tail": t}
    trips[0] = {"v": v0, "m": mid0, "f": full0, "b": b0,
                "mask": mask0, "delta": d0, "tail": t0}
    fold = hashlib.sha256("".join(loo_hexes).encode()).hexdigest()
    print(f"triplet fold sha (764x3 bins): {fold}")
    print(f"R_s vs loo mismatches: n={len(rs_bad)} {rs_bad[:20]}")
    print(f"delta==0 violations: n={d0_bad} shapes")
    print(f"shapes recorded: n={len(per)} (want 764)")
    print(f"(full-pass wall: {time.time() - t1:.1f}s)")
    if rs_bad or d0_bad or len(per) != 764:
        print("FULL-PASS MISMATCH: STOP, tabled.")
        return

    # ---- M28 n/ov/standing guard (match exactly or stop) ----
    print("== M28 n/ov/standing guard (match exactly or stop) ==")
    guard_ok = True
    for s in ANALYZED:
        rec = per[s]
        cen = census_of_shape(rec["colrows"])
        rec["cen"] = cen
        c = PARTIALS[s]
        t = tsv[s]
        ok_tw = rec["tail"] == t["tail"] and f"{rec['j']:.4f}" == t["j"]
        ok_8 = all(cen[cc]["n"] == t["cen"][cc]["n"]
                   and cen[cc]["ov"] == t["cen"][cc]["ov"]
                   and cen[cc]["pres"] == t["cen"][cc]["pres"]
                   for cc in NAMED8)
        st = standing_of(c, cen[c], rec["pcols"])
        ok_st = st == moves28.get((s, c)) == WANT_STANDING[s]
        print(f"s{s}: tail={rec['tail']}/{t['tail']} J={rec['j']:.4f}/{t['j']} "
              f"match={ok_tw}")
        print(f"s{s} c{c}: n={cen[c]['n']}/{t['cen'][c]['n']} "
              f"ov={cen[c]['ov']}/{t['cen'][c]['ov']} "
              f"p={cen[c]['pres']}/{t['cen'][c]['pres']} "
              f"standing={st}/{moves28.get((s, c))} match={ok_st}")
        print(f"s{s} all-8 n/ov/pres match={ok_8}")
        if not (ok_tw and ok_8 and ok_st):
            guard_ok = False
    # global partial-cell assertion (partial => moved; scan all 764)
    partial_found = set()
    for s in range(764):
        cen = per[s].get("cen") or census_of_shape(per[s]["colrows"])
        per[s]["cen"] = cen
        for cc in NAMED8:
            if (cen[cc]["pres"] == 0 and cen[cc]["ov"] > 0
                    and cen[cc]["miss"] + cen[cc]["extra"] <= 2):
                partial_found.add((s, cc))
    want_partial = {(s, PARTIALS[s]) for s in PARTIALS}
    print(f"partial cells recomputed (all 764): n={len(partial_found)} "
          f"{sorted(partial_found)}")
    print(f"partial cells want: n={len(want_partial)} {sorted(want_partial)} "
          f"match={partial_found == want_partial}")
    if partial_found != want_partial:
        guard_ok = False
    print("M28 guard: " + ("OK" if guard_ok else
                           "MISMATCH vs M28: STOP, tabled."))
    if not guard_ok:
        return

    # ---- P1 (s0-anchored) + carrier masks (M27 verbatim guards) ----
    print("== s0 P1 + carrier masks ==")
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

    # ---- Task 1: delta rows + per-site tables + joins ----
    print("== Task 1: delta-row lists + full-set counts ==")
    t1 = time.time()
    aA = np.frombuffer(v0, np.uint8).astype(np.int16)
    bA = np.frombuffer(full0, np.uint8).astype(np.int16)
    gA = aA - bA
    delta = {}   # s -> dict(extra_rows, miss_rows, extra_mask, miss_mask, ...)
    records = []  # pooled site records for Task 2 + bars
    for s in ANALYZED:
        c = PARTIALS[s]
        tr = trips[s]
        t_s, d_s, m_s = tr["tail"], tr["delta"], tr["mask"]
        rs = per[s]["colrows"][c]
        r0 = S0_ROWS[c]
        extra_rows = sorted(set(rs) - set(r0))
        miss_rows = sorted(set(r0) - set(rs))
        ex = np.zeros(N, bool)
        for r in extra_rows:
            o = off_of(r, c)
            assert t_s[o] and not t0[o], f"s{s} extra r{r}: not shape-tail?!"
            ex[o] = True
        mi = np.zeros(N, bool)
        for r in miss_rows:
            o = off_of(r, c)
            assert t0[o] and not t_s[o], f"s{s} missing r{r}: not s0-tail?!"
            mi[o] = True
        priv = t_s & ~t0
        miss = t0 & ~t_s
        shared = t_s & t0
        n_out_priv = [o for o in np.nonzero(priv & ~ex)[0]]
        n_out_miss = [o for o in np.nonzero(miss & ~mi)[0]]
        # sanity: column delta rows ARE all in-column priv/miss
        in_priv = sorted(int(pr[o]) for o in np.nonzero(
            priv & (pl == 0) & (pc == c))[0])
        in_miss = sorted(int(pr[o]) for o in np.nonzero(
            miss & (pl == 0) & (pc == c))[0])
        assert in_priv == extra_rows, f"s{s}: in-col priv {in_priv} != {extra_rows}"
        assert in_miss == miss_rows, f"s{s}: in-col miss {in_miss} != {miss_rows}"
        delta[s] = {"c": c, "extra_rows": extra_rows, "miss_rows": miss_rows,
                    "ex": ex, "mi": mi, "priv": priv, "miss": miss,
                    "shared": shared}
        epos = ",".join(f"{r}{span_pos(r, c)[0][0]}{span_pos(r, c)[1][0]}"
                        for r in extra_rows) or "-"
        mpos = ",".join(f"{r}{span_pos(r, c)[0][0]}{span_pos(r, c)[1][0]}"
                        for r in miss_rows) or "-"
        print(f"s{s} col c{c}: extra_rows={extra_rows} ({epos}) "
              f"missing_rows={miss_rows} ({mpos}) "
              f"n/ov={per[s]['cen'][c]['n']}/{per[s]['cen'][c]['ov']} "
              f"(E=EDGE I=INTERIOR T=TOP B=BOTTOM)")
        print(f"s{s} full sets: priv={int(priv.sum())} "
              f"miss={int(miss.sum())} shared={int(shared.sum())} "
              f"tail={per[s]['tail']} J={per[s]['j']:.4f}")
        print(f"s{s} outside-col priv: n={len(n_out_priv)} "
              f"rc={sorted((int(pr[o]), int(pc[o])) for o in n_out_priv)}")
        print(f"s{s} outside-col miss: n={len(n_out_miss)} "
              f"rc={sorted((int(pr[o]), int(pc[o])) for o in n_out_miss)}")
        dl = (f"deltarows s{s} c{c}: extra={extra_rows} missing={miss_rows} "
              f"n={per[s]['cen'][c]['n']} ov={per[s]['cen'][c]['ov']}")
        print(dl)
        if s in (22, 708):
            canon.append(dl)

    print("== Task 1: per-site delta-row tables ==")
    for s in ANALYZED:
        dd = delta[s]
        tr = trips[s]
        la, summ = attrib_lines(
            f"s{s}", dd["ex"], dd["mi"], dd["shared"], d0, mask0,
            tr["delta"], tr["mask"], v0, full0, tr["v"], tr["f"])
        for ln in la:
            print(ln)
            if s in (22, 708):
                canon.append(ln)
        # pooled site records (values re-derived verbatim from arrays)
        aB = np.frombuffer(tr["v"], np.uint8).astype(np.int16)
        bB = np.frombuffer(tr["f"], np.uint8).astype(np.int16)
        gB = aB - bB
        for kind, q, dQ, dO, mO, gQ, gO in (
                ("extra", dd["ex"], tr["delta"], d0, mask0, gB, gA),
                ("miss", dd["mi"], d0, tr["delta"], tr["mask"], gA, gB)):
            for o in np.nonzero(q)[0]:
                o = int(o)
                ostat = "bulk" if mO[o] else "noncell"
                records.append({
                    "s": s, "c": dd["c"], "kind": kind, "o": o,
                    "r": int(pr[o]), "pl": int(pl[o]),
                    "adQ": int(abs(int(dQ[o]))),
                    "ostat": ostat,
                    "adO": int(abs(int(dO[o]))) if mO[o] else None,
                    "gQ": int(gQ[o]), "gO": int(gO[o]),
                    "dec": int(dec[int(pr[o]), int(pc[o])])
                    if int(pl[o]) == 0 else -1,
                    "band": int(ROW_BAND[int(pr[o])]),
                    "edge": span_pos(int(pr[o]), dd["c"])[0],
                    "half": span_pos(int(pr[o]), dd["c"])[1]})
    print(f"(Task-1 attrib wall: {time.time() - t1:.1f}s)")

    print("== Task 1: per-shape position joins ==")
    for s in ANALYZED:
        dd = delta[s]
        lj = posjoin_lines(f"s{s}", dd["ex"], dd["mi"], dd["shared"],
                           dec, masks)
        for ln in lj:
            print(ln)
            if s in (22, 708):
                canon.append(ln)

    print("== Task 1: pooled position join (shared=s0 tail) ==")
    pool_ex = np.zeros(N, bool)
    pool_mi = np.zeros(N, bool)
    for s in ANALYZED:
        pool_ex |= delta[s]["ex"]
        pool_mi |= delta[s]["mi"]
    print(f"pooled delta sites: extra={int(pool_ex.sum())} "
          f"missing={int(pool_mi.sum())} total={int(pool_ex.sum()) + int(pool_mi.sum())} "
          f"(want 5+4=9)")
    for ln in posjoin_lines("pooled", pool_ex, pool_mi, t0, dec, masks):
        print(ln)

    # ---- Task 2.1: extra vs missing pools ----
    print("== Task 2.1: extra-only vs missing-only pools ==")
    ex_t21 = [r for r in records if r["kind"] == "extra" and r["s"] in (22, 9)]
    ex_all = [r for r in records if r["kind"] == "extra"]
    mi_all = [r for r in records if r["kind"] == "miss"]

    def pool_stats(tag, recs):
        ads = sorted(r["adQ"] for r in recs)
        gq = {"+": 0, "-": 0, "0": 0}
        go = {"+": 0, "-": 0, "0": 0}
        for r in recs:
            gq["+" if r["gQ"] > 0 else ("-" if r["gQ"] < 0 else "0")] += 1
            go["+" if r["gO"] > 0 else ("-" if r["gO"] < 0 else "0")] += 1
        st = {}
        for r in recs:
            st[r["ostat"]] = st.get(r["ostat"], 0) + 1
        edge = sum(1 for r in recs if r["edge"] == "EDGE")
        top = sum(1 for r in recs if r["half"] == "TOP")
        med = statistics.median(ads) if ads else None
        print(f"{tag}: n={len(recs)} adQ=min{min(ads) if ads else '-'} "
              f"med={med} max={max(ads) if ads else '-'} vals={ads}")
        print(f"{tag}: gQ signs +/{gq['+']} -/{gq['-']} 0/{gq['0']}; "
              f"gO signs +/{go['+']} -/{go['-']} 0/{go['0']}")
        print(f"{tag}: ostat={st} EDGE={edge}/{len(recs)} "
              f"TOP={top}/{len(recs)}")
        for r in sorted(recs, key=lambda r: r["o"]):
            print(f"{tag} site s{r['s']} o={r['o']} rc=({r['r']},{r['c']}) "
                  f"adQ={r['adQ']} ostat={r['ostat']} adO={r['adO']} "
                  f"gQ={r['gQ']} gO={r['gO']} dec={r['dec']} "
                  f"band={r['band']} {r['edge']}/{r['half']}")
        return med

    med_ex_t21 = pool_stats("pool extra[22,9]", ex_t21)
    med_mi = pool_stats("pool missing[708,709,710]", mi_all)
    med_ex_all = pool_stats("pool extra[all:22,9,734]", ex_all)

    # ---- Task 2.2: 734-c342 vs 22 side-by-side ----
    print("== Task 2.2: 734-c342 vs 22-c296 (both +2 extra-only) ==")
    for s in (22, 734):
        dd = delta[s]
        recs = [r for r in records if r["s"] == s]
        ads = sorted(r["adQ"] for r in recs)
        print(f"s{s} c{dd['c']}: n/ov={per[s]['cen'][dd['c']]['n']}/"
              f"{per[s]['cen'][dd['c']]['ov']} rows={dd['extra_rows']} "
              f"adQ={ads} gQ={[r['gQ'] for r in recs]} "
              f"gO={[r['gO'] for r in recs]} "
              f"ostat={[r['ostat'] for r in recs]} "
              f"dec={[r['dec'] for r in recs]} "
              f"pos=[{','.join(r['edge'][0] + r['half'][0] for r in recs)}]")

    # ---- Task 2.3: row-tolerant standings (NOT adopted) ----
    print("== Task 2.3: RT-PRES (present iff miss<=2 and extra<=2) ==")
    for s in ANALYZED:
        c = PARTIALS[s]
        cc = per[s]["cen"][c]
        tol = "present-tolerant" if (cc["miss"] <= 2 and cc["extra"] <= 2) \
            else "still-moved"
        print(f"s{s} c{c}: miss={cc['miss']} extra={cc['extra']} -> {tol} "
              f"(exact rule: moved)")
    rt_movers = []
    for s in M28_MOVERS:
        cen = per[s]["cen"]
        if any(cen[cc]["miss"] > 2 or cen[cc]["extra"] > 2 for cc in NAMED8):
            rt_movers.append(s)
    print(f"RT-PRES movers over M28 10: n={len(rt_movers)} {rt_movers} "
          f"(exact: n=10 {M28_MOVERS})")

    print("== Task 2.3: RT-DEST (missing row -> nearest private-Y, dmin<=2) ==")
    rt_assign = 0
    rt_rows = 0
    for s in ANALYZED:
        dd = delta[s]
        tr = trips[s]
        pyt = [(int(pr[o]), int(pc[o])) for o in np.nonzero(
            dd["priv"] & (pl == 0))[0]]
        for r in dd["miss_rows"]:
            rt_rows += 1
            if not pyt:
                print(f"s{s} miss r{r} c{dd['c']}: dmin=n/a "
                      f"(no private-Y sites) assigned=False")
                continue
            dmin = min(abs(r - rr) + abs(dd["c"] - ccx) for rr, ccx in pyt)
            dcols = sorted({ccx for rr, ccx in pyt
                            if abs(r - rr) + abs(dd["c"] - ccx) == dmin})
            assigned = dmin <= 2
            rt_assign += int(assigned)
            print(f"s{s} miss r{r} c{dd['c']}: dmin={dmin} "
                  f"destcol={dcols[0]} (ties={dcols}) assigned={assigned}")
        if not dd["miss_rows"]:
            print(f"s{s} c{dd['c']}: extra-only, no missing rows "
                  f"-> unassignable under RT-DEST")
    print(f"RT-DEST: assigned {rt_assign}/{rt_rows} missing rows")

    # ---- determinism re-run (Task 1 on s0+22+708, fresh loads) ----
    print("== determinism re-run (Task 1 on s0+22+708, second pass) ==")
    canon2 = []
    vv0 = load_dump(m16d / "m16-v0-s0000.bin")
    mm0 = load_dump(m16d / "m16-mid-s0000.bin")
    ff0 = load_dump(m16d / "m16-full-s0000.bin")
    bb0 = synth_w_bytes(vv0, ff0, 0.5)
    sp0b = interior_sites(vv0, mm0, ff0, bb0)
    m0b, d0b = sp0b["mask"], sp0b["delta"]
    t0b, _ = tail_bulk_masks(m0b, d0b)
    ym0b = split_planes(np.frombuffer(mm0, np.uint8))[0]
    _, _, decb = p1_gradient(ym0b)
    sy0b = split_planes(np.frombuffer(bb0, np.uint8))[0]
    res0b = sy0b.astype(np.int16) != ym0b.astype(np.int16)
    masks2 = {}
    for s in M16_TOP10:
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        yb = split_planes(np.frombuffer(bl, np.uint8))[0]
        yms = split_planes(np.frombuffer(mm, np.uint8))[0]
        masks2[s] = res0b & (yb.astype(np.int16) == yms.astype(np.int16))
    # note: res0 & ~ress == res0b & (yb==yms); same sites, tabled form
    # pass-2 canon order matches pass 1: both dl lines, then attrib
    # (22, 708), then posjoin (22, 708)
    sec = {}
    for s in (22, 708):
        c = PARTIALS[s]
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        sp = interior_sites(vv, mm, ff, bl)
        t_s, d_s, m_s = tail_bulk_masks(sp["mask"], sp["delta"])[0], \
            sp["delta"], sp["mask"]
        rs = y_col_rows(t_s, c, pl, pr, pc)
        ex_rows = sorted(set(rs) - set(S0_ROWS[c]))
        mi_rows = sorted(set(S0_ROWS[c]) - set(rs))
        ex = np.zeros(N, bool)
        for r in ex_rows:
            ex[off_of(r, c)] = True
        mi = np.zeros(N, bool)
        for r in mi_rows:
            mi[off_of(r, c)] = True
        shared = t_s & t0b
        dl = (f"deltarows s{s} c{c}: extra={ex_rows} missing={mi_rows} "
              f"n={len(rs)} ov={len(set(rs) & set(S0_ROWS[c]))}")
        la, _ = attrib_lines(f"s{s}", ex, mi, shared, d0b, m0b, d_s, m_s,
                             vv0, ff0, vv, ff)
        lj = posjoin_lines(f"s{s}", ex, mi, shared, decb, masks2)
        sec[s] = (dl, la, lj)
    for s in (22, 708):
        canon2.append(sec[s][0])
    for s in (22, 708):
        canon2 += sec[s][1]
    for s in (22, 708):
        canon2 += sec[s][2]
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")

    # ---- PNG delta-row map (work dir; evidence copy iff rule meets) ----
    print("== PNG delta-row map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    im_ex, _, _ = flat_to_planes(pool_ex)
    im_mi, _, _ = flat_to_planes(pool_mi)
    over[im_ex] = np.array([255, 255, 0])    # extra delta rows yellow
    over[im_mi] = np.array([255, 0, 255])    # missing delta rows magenta
    p = workd / "m29-deltamap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: yellow=extra delta rows (5) magenta=missing delta rows "
          "(4), pooled over 6 partial cells (s0 geometry; Y only)")

    # ---- falsification-bar measurements (values + thresholds) ----
    print("== falsification-bar measurements ==")
    npool = len(records)
    nnear = sum(1 for r in records
                if r["ostat"] == "bulk" and r["adO"] in (6, 7))
    nnon = sum(1 for r in records if r["ostat"] == "noncell")
    nd9 = sum(1 for r in records if r["dec"] == 9)
    nedge = sum(1 for r in records if r["edge"] == "EDGE")
    print(f"H1_NEARMISS: near {nnear}/{npool} "
          f"({nnear / npool if npool else 0:.4f}; bar >=0.50)")
    print(f"H2_SETCHANGE: noncell {nnon}/{npool} "
          f"({nnon / npool if npool else 0:.4f}; bar >=0.50)")
    print(f"H3_DEC9: dec-9 {nd9}/{npool} "
          f"({nd9 / npool if npool else 0:.4f}; bar >=0.50)")
    print(f"H4_EDGE: edge {nedge}/{npool} "
          f"({nedge / npool if npool else 0:.4f}; bar >=0.50)")
    print(f"H5_EXTRAMISS: med_extra_all={med_ex_all} "
          f"med_missing={med_mi} med_extra[22,9]={med_ex_t21} "
          f"differs={med_ex_all != med_mi} (bar: strictly unequal)")
    print(f"H6_TOLASSIGN: RT-DEST assigned {rt_assign}/{rt_rows} "
          f"(bar >=1)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=delta-rows T2=extra/missing+RT R=controls")


if __name__ == "__main__":
    main()

