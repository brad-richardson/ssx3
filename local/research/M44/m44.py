#!/usr/bin/env python3
"""M44 same-column opposite standings: c298 wipe-vs-growth + c311 11-vs-1.

Usage: m44.py M16_DIR M15_DIR M34TSV WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt, the M15 triplet (baseline
guard only), and m34-census.tsv (c298/c311 mover counts + standings
to reproduce); raw XFB dumps, 573440 B = 640x448 YUYV. Read-only
inputs; receipt text goes to stdout (redirect to WORK_DIR/m44.txt);
PNG split-column map to WORK_DIR (evidence copy iff the DESIGN.md
rule meets, decided at report time).

Tasks (see DESIGN.md, recorded before running):
  1: c298 wipe-vs-growth (row-lists + per-site values + comparison)
  2: c311 11-vs-1 (mover table + per-site values + comparison)
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
# ---- M44 pinned c298/c311 rows (from m34-census.tsv, §Definitions) ----
C298_S0 = [28, 29, 34, 35]
C298_MOVERS = [709, 732]
C298_NOV = {709: (0, 0), 732: (6, 4)}
C298_TAILJ = {709: (97, "0.9510"), 732: (95, "0.8942")}
C311_S0 = [296, 297, 298, 299]
C311_MOVERS = [2, 3, 9, 380, 381, 382, 383, 384, 386, 387, 389, 700]
C311_EXTRA_MOVERS = [2, 3, 380, 381, 382, 383, 384, 386, 387, 389, 700]
C311_NOV = {9: (3, 3), 2: (5, 4), 3: (5, 4), 380: (5, 4),
            381: (5, 4), 382: (5, 4), 383: (5, 4), 384: (5, 4),
            386: (5, 4), 387: (5, 4), 389: (5, 4), 700: (5, 4)}
C311_TAILJ = {9: (117, "0.7520"), 2: (103, "0.9159"),
              3: (103, "0.9340"), 380: (103, "0.9903"),
              381: (103, "0.9903"), 382: (103, "0.9903"),
              383: (103, "0.9903"), 384: (103, "0.9903"),
              386: (103, "0.9903"), 387: (103, "0.9903"),
              389: (103, "0.9903"), 700: (114, "0.8462")}
S9_C311_MISS = [296]  # M35
C311_KNOWN_EXTRAS = {2: [259], 3: [258], 700: [259]}  # M36
M35_LONE_VALS = {"ad": 10, "ostat": "noncell", "gQ": 24, "gO": 7}
ANALYZED = [0, 709, 732, 9, 2, 3, 380, 381, 382, 383, 384, 386,
            387, 389, 700]


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


def kept_lines(tag, sites, dA, dB, v0A, fullA, v0B, fullB, tA, tB):
    """Both-frame value rows for kept (shared-tail) sites (M44-only)."""
    L = []
    pl = plane_of_byte()
    pr, pc = plane_coords()
    aA = np.frombuffer(v0A, np.uint8).astype(np.int16)
    bA = np.frombuffer(fullA, np.uint8).astype(np.int16)
    aB = np.frombuffer(v0B, np.uint8).astype(np.int16)
    bB = np.frombuffer(fullB, np.uint8).astype(np.int16)
    gA, gB = aA - bA, aB - bB
    for o in sorted(int(x) for x in np.nonzero(sites)[0]):
        assert tA[o] and tB[o], f"{tag} kept o={o}: not tail on both?!"
        L.append(f"{tag} kept o={o} plane={PNAME[int(pl[o])]} "
                 f"rc=({int(pr[o])},{int(pc[o])}) adA={int(abs(int(dA[o])))} "
                 f"adB={int(abs(int(dB[o])))} gA={int(gA[o])} gB={int(gB[o])}")
    return L


def load_triplet(m16d: Path, s: int):
    vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
    mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
    ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
    return vv, mm, ff, synth_w_bytes(vv, ff, 0.5)


def analyze(m16d: Path):
    """Cell-7 + tail + c298/c311 row sets for s0 + all movers."""
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
    A = {"T": T, "pl": pl, "pr": pr, "pc": pc}
    # c298 row sets
    t0 = T[0]["t"]
    A["r0_298"] = y_col_rows(t0, 298, pl, pr, pc)
    A["r709_298"] = y_col_rows(T[709]["t"], 298, pl, pr, pc)
    A["r732_298"] = y_col_rows(T[732]["t"], 298, pl, pr, pc)
    A["wipe298"] = np.zeros(N, bool)  # s0 sites missing on 709
    for r in sorted(set(A["r0_298"]) - set(A["r709_298"])):
        A["wipe298"][off_of(r, 298)] = True
    A["grow298"] = np.zeros(N, bool)  # 732 sites extra over s0
    for r in sorted(set(A["r732_298"]) - set(A["r0_298"])):
        A["grow298"][off_of(r, 298)] = True
    A["keep298"] = np.zeros(N, bool)  # shared s0+732 sites
    for r in sorted(set(A["r732_298"]) & set(A["r0_298"])):
        A["keep298"][off_of(r, 298)] = True
    # c311 row sets
    A["r0_311"] = y_col_rows(t0, 311, pl, pr, pc)
    A["rows311"] = {}
    A["crowd"] = []  # 11 (mover, offset) pairs, mover order
    for q in C311_MOVERS:
        rq = y_col_rows(T[q]["t"], 311, pl, pr, pc)
        ex = sorted(set(rq) - set(A["r0_311"]))
        mi = sorted(set(A["r0_311"]) - set(rq))
        A["rows311"][q] = {"rows": rq, "ex": ex, "mi": mi}
        for r in ex:
            A["crowd"].append((q, off_of(r, 311)))
    A["lone311"] = np.zeros(N, bool)  # s0 sites missing on s9
    for r in A["rows311"][9]["mi"]:
        A["lone311"][off_of(r, 311)] = True
    A["keep311"] = np.zeros(N, bool)  # s0 c311 rows kept by every mover
    keptrows = set(A["r0_311"])
    for q in C311_MOVERS:
        keptrows &= set(A["rows311"][q]["rows"])
    for r in sorted(keptrows):
        A["keep311"][off_of(r, 311)] = True
    A["crowd_union"] = np.zeros(N, bool)
    for _, o in A["crowd"]:
        A["crowd_union"][o] = True
    return A


def sgn(x):
    return "+" if x > 0 else ("-" if x < 0 else "0")


def task_lines(A):
    """All Task 1-2 receipt lines (row-lists + value rows + comparisons)."""
    L = []
    T, pl, pr, pc = A["T"], A["pl"], A["pr"], A["pc"]
    v0, full0, d0, m0 = T[0]["v0"], T[0]["full"], T[0]["d"], T[0]["mask"]
    # ---- Task 1: c298 ----
    L.append(f"c298 rows s0={A['r0_298']} s709={A['r709_298']} "
             f"s732={A['r732_298']}")
    L.append(f"c298 wipe rows={sorted(set(A['r0_298']) - set(A['r709_298']))} "
             f"n={int(A['wipe298'].sum())}")
    L.append(f"c298 grow rows={sorted(set(A['r732_298']) - set(A['r0_298']))} "
             f"n={int(A['grow298'].sum())}")
    L.append(f"c298 keep rows={sorted(set(A['r732_298']) & set(A['r0_298']))} "
             f"n={int(A['keep298'].sum())}")
    z = np.zeros(N, bool)
    T709, T732 = T[709], T[732]
    la, _ = attrib_lines("c298wipe", z, A["wipe298"], z, d0, m0,
                         T709["d"], T709["mask"], v0, full0,
                         T709["v0"], T709["full"])
    L += la
    la, _ = attrib_lines("c298grow", A["grow298"], z, z, d0, m0,
                         T732["d"], T732["mask"], v0, full0,
                         T732["v0"], T732["full"])
    L += la
    L += kept_lines("c298keep732", A["keep298"], d0, T732["d"], v0, full0,
                    T732["v0"], T732["full"], T[0]["t"], T732["t"])
    L += dstats_lines("c298wipe", z, A["wipe298"], T709["d"], d0)
    L += dstats_lines("c298grow", A["grow298"], z, T732["d"], d0)
    L += gapsign_lines("c298wipe", z, A["wipe298"], v0, full0,
                       T709["v0"], T709["full"])
    L += gapsign_lines("c298grow", A["grow298"], z, v0, full0,
                       T732["v0"], T732["full"])
    # wipe-vs-growth comparison (numbers only)
    w_idx = [int(o) for o in np.nonzero(A["wipe298"])[0]]
    g_idx = [int(o) for o in np.nonzero(A["grow298"])[0]]
    k_idx = [int(o) for o in np.nonzero(A["keep298"])[0]]
    w_ad = sorted(int(abs(int(d0[o]))) for o in w_idx)
    g_ad = sorted(int(abs(int(T732["d"][o]))) for o in g_idx)
    k_ad0 = sorted(int(abs(int(d0[o]))) for o in k_idx)
    k_adQ = sorted(int(abs(int(T732["d"][o]))) for o in k_idx)
    L.append(f"c298cmp wiped-adS0 list=[{','.join(map(str, w_ad))}] "
             f"n={len(w_ad)}")
    L.append(f"c298cmp grown-ad732 list=[{','.join(map(str, g_ad))}] "
             f"n={len(g_ad)}")
    L.append(f"c298cmp kept-adS0 list=[{','.join(map(str, k_ad0))}] "
             f"kept-ad732 list=[{','.join(map(str, k_adQ))}] n={len(k_idx)}")
    w_non = sum(1 for o in w_idx if not T709["mask"][o])
    g_non = sum(1 for o in g_idx if not m0[o])
    L.append(f"c298cmp wiped-noncell-on709 {w_non}/{len(w_idx)} "
             f"grown-noncell-ons0 {g_non}/{len(g_idx)}")
    # ---- Task 2: c311 ----
    L.append(f"c311 rows s0={A['r0_311']}")
    for q in C311_MOVERS:
        e = A["rows311"][q]
        stand = ("missing" if e["mi"] and not e["ex"]
                 else ("extra" if e["ex"] and not e["mi"] else "mixed"))
        L.append(f"c311 mover s{q}: rows={e['rows']} ex={e['ex']} "
                 f"mi={e['mi']} stand={stand}")
    T9 = T[9]
    la, _ = attrib_lines("c311lone", z, A["lone311"], z, d0, m0,
                         T9["d"], T9["mask"], v0, full0,
                         T9["v0"], T9["full"])
    L += la
    for q in C311_EXTRA_MOVERS:
        ex = np.zeros(N, bool)
        for r in A["rows311"][q]["ex"]:
            ex[off_of(r, 311)] = True
        TQ = T[q]
        la, _ = attrib_lines(f"c311x{q}", ex, z, z, d0, m0,
                             TQ["d"], TQ["mask"], v0, full0,
                             TQ["v0"], TQ["full"])
        L += la
    L += dstats_lines("c311lone", z, A["lone311"], T9["d"], d0)
    L += gapsign_lines("c311lone", z, A["lone311"], v0, full0,
                       T9["v0"], T9["full"])
    # lone-vs-crowd comparison over the 11 per-mover pairs (numbers only)
    a0 = np.frombuffer(v0, np.uint8).astype(np.int16)
    f0a = np.frombuffer(full0, np.uint8).astype(np.int16)
    g0 = a0 - f0a
    lone_o = [int(o) for o in np.nonzero(A["lone311"])[0]]
    lo = lone_o[0] if len(lone_o) == 1 else None
    if lo is not None:
        a9 = np.frombuffer(T9["v0"], np.uint8).astype(np.int16)
        f9a = np.frombuffer(T9["full"], np.uint8).astype(np.int16)
        g9 = a9 - f9a
        L.append(f"c311cmp lone o={lo} rc=({int(pr[lo])},{int(pc[lo])}) "
                 f"adS0={int(abs(int(d0[lo])))} "
                 f"ostat={'bulk' if T9['mask'][lo] else 'noncell'} "
                 f"gS0={int(g0[lo])} g9={int(g9[lo])} "
                 f"sign={sgn(int(g0[lo]))}{sgn(int(g9[lo]))}")
    crowd_ads, crowd_bulk, crowd_non = [], 0, 0
    crowd_signs = {}
    for q, o in A["crowd"]:
        TQ = T[q]
        adq = int(abs(int(TQ["d"][o])))
        crowd_ads.append(adq)
        if m0[o]:
            crowd_bulk += 1
        else:
            crowd_non += 1
        aQ = np.frombuffer(TQ["v0"], np.uint8).astype(np.int16)
        fQa = np.frombuffer(TQ["full"], np.uint8).astype(np.int16)
        gQ = aQ - fQa
        k = (sgn(int(gQ[o])), sgn(int(g0[o])))
        crowd_signs[k] = crowd_signs.get(k, 0) + 1
    crowd_ads_s = sorted(crowd_ads)
    a = np.asarray(crowd_ads_s, dtype=np.float64)
    L.append(f"c311cmp crowd-adQ list=[{','.join(map(str, crowd_ads_s))}] "
             f"n={len(crowd_ads_s)} min={a.min():.0f} "
             f"med={np.median(a):.1f} mean={a.mean():.4f} max={a.max():.0f}")
    L.append(f"c311cmp crowd-ons0 bulk={crowd_bulk} noncell={crowd_non} "
             f"n={len(crowd_ads)}")
    order = [(x, y) for x in ("+", "-", "0") for y in ("+", "-", "0")]
    L.append("c311cmp crowd-signs n=11 "
             + " ".join(f"{x}{y}={crowd_signs.get((x, y), 0)}"
                        for x, y in order))
    L.append(f"c311cmp crowd-union-sites n={int(A['crowd_union'].sum())} "
             f"(11 pairs)")
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
        print("MISMATCH vs M17-M43 baselines: STOP, tabled.")
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
    print(f"union tail-Y cols (all 764): n={len(allcols)}")
    print(f"UNNAMED (union minus named8): n={len(UNNAMED)} (want 33)")
    print(f"s0-bearing unnamed (n0>0): n={len(n0pos)} (want 13)")
    print(f"pure-private unnamed (n0==0): n={len(n0zero)} (want 20)")

    # ---- FULL unnamed TSV guard (M34 match or stop) ----
    print("== unnamed TSV guard (M34 match or stop) ==")
    tsv_lines = m34tsv.read_text(errors="replace").splitlines()
    want_hdr = "\t".join(["shape", "tail_n", "J_vs_s0"]
                         + [f"{k}{c}" for c in UNNAMED
                            for k in ("n", "ov", "pres")])
    hdr_cols = []
    for tok in tsv_lines[0].split("\t")[3:]:
        if tok.startswith("n"):
            hdr_cols.append(int(tok[1:]))
    print(f"m34-census.tsv rows={len(tsv_lines) - 1} "
          f"hdr_match={tsv_lines[0] == want_hdr} "
          f"universe_match={hdr_cols == UNNAMED}")
    tsv_ok = (tsv_lines[0] == want_hdr and len(tsv_lines) == 765
              and hdr_cols == UNNAMED and len(UNNAMED) == 33
              and len(n0pos) == 13 and len(n0zero) == 20)
    first_bad = None
    for s in range(764):
        rec = per[s]
        cen = census_unnamed_of(rec["ycols"], s0u)
        rec["ucen"] = cen
        rec["umoved"] = sorted(c for c in UNNAMED if cen[c]["pres"] == 0)
        row = [str(s), str(rec["tail"]), f"{rec['j']:.4f}"]
        for c in UNNAMED:
            row += [str(cen[c]["n"]), str(cen[c]["ov"]),
                    str(cen[c]["pres"])]
        if "\t".join(row) != tsv_lines[s + 1]:
            tsv_ok = False
            if first_bad is None:
                first_bad = s
    print(f"unnamed TSV full match (764 rows): {tsv_ok}"
          + ("" if tsv_ok else f" first_bad_shape={first_bad}"))
    print("TSV guard: " + ("OK" if tsv_ok else
                           "MISMATCH vs M34: STOP, tabled."))
    if not tsv_ok:
        return

    # ---- c298/c311 row guards (M34 match or stop) ----
    print("== c298 row guard (M34 match or stop) ==")
    m298 = sorted(s for s in range(764) if per[s]["ucen"][298]["pres"] == 0)
    print(f"s0 c298 rows={s0u[298]} (want {C298_S0})")
    print(f"c298 movers={m298} (want {C298_MOVERS})")
    ok298 = (s0u[298] == C298_S0 and m298 == C298_MOVERS)
    mo298 = eo298 = mx298 = 0
    for q in C298_MOVERS:
        e = per[q]["ucen"][298]
        wn, wov = C298_NOV[q]
        wt, wj = C298_TAILJ[q]
        stand = ("missing" if e["miss"] > 0 and e["extra"] == 0
                 else ("extra" if e["miss"] == 0 and e["extra"] > 0
                       else "mixed"))
        if stand == "missing":
            mo298 += 1
        elif stand == "extra":
            eo298 += 1
        else:
            mx298 += 1
        good = (e["n"] == wn and e["ov"] == wov
                and per[q]["tail"] == wt
                and f"{per[q]['j']:.4f}" == wj and e["pres"] == 0)
        ok298 = ok298 and good
        print(f"c298 s{q}: n/ov={e['n']}/{e['ov']} (want {wn}/{wov}) "
              f"tail/J={per[q]['tail']}/{per[q]['j']:.4f} "
              f"(want {wt}/{wj}) stand={stand} match={good}")
    print(f"c298 standings miss/extra/mixed={mo298}/{eo298}/{mx298} "
          f"(want 1/1/0)")
    ok298 = ok298 and (mo298, eo298, mx298) == (1, 1, 0)
    print("c298 guard: " + ("OK" if ok298 else
                            "MISMATCH vs M34: STOP, tabled."))
    if not ok298:
        return

    print("== c311 row guard (M34 match or stop) ==")
    m311 = sorted(s for s in range(764) if per[s]["ucen"][311]["pres"] == 0)
    print(f"s0 c311 rows={s0u[311]} (want {C311_S0})")
    print(f"c311 movers={m311} (want {C311_MOVERS})")
    ok311 = (s0u[311] == C311_S0 and m311 == C311_MOVERS)
    mo311 = eo311 = mx311 = 0
    for q in C311_MOVERS:
        e = per[q]["ucen"][311]
        wn, wov = C311_NOV[q]
        wt, wj = C311_TAILJ[q]
        stand = ("missing" if e["miss"] > 0 and e["extra"] == 0
                 else ("extra" if e["miss"] == 0 and e["extra"] > 0
                       else "mixed"))
        if stand == "missing":
            mo311 += 1
        elif stand == "extra":
            eo311 += 1
        else:
            mx311 += 1
        good = (e["n"] == wn and e["ov"] == wov
                and per[q]["tail"] == wt
                and f"{per[q]['j']:.4f}" == wj and e["pres"] == 0)
        ok311 = ok311 and good
        print(f"c311 s{q}: n/ov={e['n']}/{e['ov']} (want {wn}/{wov}) "
              f"tail/J={per[q]['tail']}/{per[q]['j']:.4f} "
              f"(want {wt}/{wj}) stand={stand} match={good}")
    print(f"c311 standings miss/extra/mixed={mo311}/{eo311}/{mx311} "
          f"(want 1/11/0)")
    ok311 = ok311 and (mo311, eo311, mx311) == (1, 11, 0)
    print("c311 guard: " + ("OK" if ok311 else
                            "MISMATCH vs M34: STOP, tabled."))
    if not ok311:
        return

    # ---- analyzed triplets + row-list guards (M35/M36 match or stop) ----
    print("== analyzed triplets + row-list guards ==")
    A = analyze(m16d)
    T = A["T"]
    dd_bad = sum(1 for s in ANALYZED
                 if int((T[s]["d"][T[s]["mask"]] == 0).sum()) != 0)
    print(f"analyzed delta==0 violations: n={dd_bad} shapes (want 0)")
    print(f"c298 s709 rows={A['r709_298']} (want []) "
          f"wipe==C298_S0: {sorted(set(A['r0_298']) - set(A['r709_298'])) == C298_S0}")
    print(f"c298 s732 rows={A['r732_298']} keep==C298_S0: "
          f"{sorted(set(A['r732_298']) & set(A['r0_298'])) == C298_S0} "
          f"grow-n={int(A['grow298'].sum())} (want 2)")
    print(f"c311 s9 mi={A['rows311'][9]['mi']} (want {S9_C311_MISS})")
    row_ok = (dd_bad == 0
              and A["r709_298"] == []
              and sorted(set(A["r0_298"]) - set(A["r709_298"])) == C298_S0
              and sorted(set(A["r732_298"]) & set(A["r0_298"])) == C298_S0
              and int(A["grow298"].sum()) == 2
              and A["rows311"][9]["mi"] == S9_C311_MISS)
    for q, want_ex in C311_KNOWN_EXTRAS.items():
        got = A["rows311"][q]["ex"]
        print(f"c311 s{q} ex={got} (want {want_ex}) match={got == want_ex}")
        row_ok = row_ok and got == want_ex
    # every c311 extra-only mover adds exactly 1 row (n/ov 5/4 cross-check)
    for q in C311_EXTRA_MOVERS:
        e = A["rows311"][q]
        one = (len(e["ex"]) == 1 and len(e["mi"]) == 0)
        row_ok = row_ok and one
        if not one:
            print(f"c311 s{q} ROW GUARD FAIL: ex={e['ex']} mi={e['mi']}")
    # all c298/c311 delta sites Y-plane
    planes298 = {int(pl[o]) for o in
                 list(np.nonzero(A["wipe298"])[0])
                 + list(np.nonzero(A["grow298"])[0])}
    planes311 = {int(pl[o]) for _, o in A["crowd"]}
    planes311 |= {int(pl[o]) for o in np.nonzero(A["lone311"])[0]}
    print(f"c298 delta-site planes={sorted(planes298)} "
          f"c311 delta-site planes={sorted(planes311)} (want [0] both)")
    row_ok = row_ok and planes298 == {0} and planes311 == {0}
    # lone value cross-check vs M35 (tabled; site already row-guarded)
    lo = int(np.nonzero(A["lone311"])[0][0])
    a9x = np.frombuffer(T[9]["v0"], np.uint8).astype(np.int16)
    f9x = np.frombuffer(T[9]["full"], np.uint8).astype(np.int16)
    g9x = a9x - f9x
    a0x = np.frombuffer(v0, np.uint8).astype(np.int16)
    f0x = np.frombuffer(full0, np.uint8).astype(np.int16)
    g0x = a0x - f0x
    lone_match = (int(abs(int(d0[lo]))) == M35_LONE_VALS["ad"]
                  and (not T[9]["mask"][lo])
                  and int(g0x[lo]) == M35_LONE_VALS["gQ"]
                  and int(g9x[lo]) == M35_LONE_VALS["gO"])
    print(f"c311 lone M35 value cross-check: ad={int(abs(int(d0[lo])))} "
          f"(want {M35_LONE_VALS['ad']}) "
          f"ostat={'bulk' if T[9]['mask'][lo] else 'noncell'} "
          f"(want {M35_LONE_VALS['ostat']}) gS0/g9={int(g0x[lo])}/"
          f"{int(g9x[lo])} (want {M35_LONE_VALS['gQ']}/"
          f"{M35_LONE_VALS['gO']}) match={lone_match}")
    print("row-list guards: " + ("OK" if row_ok else
                                 "MISMATCH: STOP, tabled."))
    if not row_ok:
        return

    # ---- Tasks 1-2 ----
    print("== Task 1 (c298): row-lists + value tables ==")
    print("== Task 2 (c311): mover table + value tables ==")
    t1 = time.time()
    canon = task_lines(A)
    for ln in canon:
        print(ln)
    print(f"(Tasks-1/2 wall: {time.time() - t1:.1f}s)")

    # ---- determinism re-run (Tasks 1-2, fresh loads) ----
    print("== determinism re-run (Tasks 1-2, second pass) ==")
    A2 = analyze(m16d)
    canon2 = task_lines(A2)
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"canon lines: n={len(canon)}/{len(canon2)} "
          f"match={canon == canon2}")

    # ---- PNG split-column value map ----
    print("== PNG split-column map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid0, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    im_k298, _, _ = flat_to_planes(A["keep298"])
    im_w298, _, _ = flat_to_planes(A["wipe298"])
    im_g298, _, _ = flat_to_planes(A["grow298"])
    im_k311, _, _ = flat_to_planes(A["keep311"])
    im_l311, _, _ = flat_to_planes(A["lone311"])
    im_c311, _, _ = flat_to_planes(A["crowd_union"])
    over[im_k298] = np.array([0, 255, 0])      # c298 kept green
    over[im_k311] = np.array([0, 255, 0])      # c311 kept green
    over[im_w298] = np.array([255, 0, 0])      # c298 wiped red
    over[im_g298] = np.array([255, 255, 0])    # c298 grown yellow
    over[im_l311] = np.array([255, 0, 255])    # c311 lone magenta
    over[im_c311] = np.array([0, 255, 255])    # c311 crowd cyan
    p = workd / "m44-splitmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: c298 wiped=red kept=green grown=yellow; "
          "c311 kept=green lone=magenta crowd=cyan (s0 geometry; Y only)")

    # ---- falsification-bar measurements ----
    print("== falsification-bar measurements ==")
    w_idx = [int(o) for o in np.nonzero(A["wipe298"])[0]]
    g_idx = [int(o) for o in np.nonzero(A["grow298"])[0]]
    w_non = sum(1 for o in w_idx if not T[709]["mask"][o])
    g_non = sum(1 for o in g_idx if not mask0[o])
    a709 = np.frombuffer(T[709]["v0"], np.uint8).astype(np.int16)
    f709 = np.frombuffer(T[709]["full"], np.uint8).astype(np.int16)
    g709 = a709 - f709
    w_pp = sum(1 for o in w_idx if int(g0x[o]) > 0 and int(g709[o]) > 0)
    crowd_mm = 0
    crowd_non = 0
    crowd_ads = []
    for q, o in A["crowd"]:
        TQ = T[q]
        crowd_ads.append(int(abs(int(TQ["d"][o]))))
        if not mask0[o]:
            crowd_non += 1
        aQ = np.frombuffer(TQ["v0"], np.uint8).astype(np.int16)
        fQ = np.frombuffer(TQ["full"], np.uint8).astype(np.int16)
        gQ = aQ - fQ
        if int(gQ[o]) < 0 and int(g0x[o]) < 0:
            crowd_mm += 1
    crowd_ads_s = sorted(crowd_ads)
    import statistics as _st
    crowd_med = _st.median(crowd_ads_s)
    lone_ad = int(abs(int(d0[lo])))
    print(f"H1_WIPESET: wiped noncell-on709 {w_non}/{len(w_idx)} "
          f"({w_non / len(w_idx) if w_idx else 0:.4f}; bar >=0.50)")
    print(f"H2_GROWSET: grown noncell-ons0 {g_non}/{len(g_idx)} "
          f"({g_non / len(g_idx) if g_idx else 0:.4f}; bar >=0.50)")
    print(f"H3_CROWDSET: crowd noncell-ons0 {crowd_non}/{len(A['crowd'])} "
          f"({crowd_non / len(A['crowd']):.4f}; bar >=0.50)")
    print(f"H4_WIPEGAP: wiped ++ {w_pp}/{len(w_idx)} "
          f"({w_pp / len(w_idx) if w_idx else 0:.4f}; bar >=0.50)")
    print(f"H5_CROWDGAP: crowd -- {crowd_mm}/{len(A['crowd'])} "
          f"({crowd_mm / len(A['crowd']):.4f}; bar >=0.50)")
    print(f"H6_LONEMAG: lone ad {lone_ad} vs crowd med {crowd_med}: "
          f"{lone_ad >= crowd_med} (bar: lone>=crowd-med)")
    print("N: 0 explained; tail stands (attribution, not explanation)")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: T1=c298-wipe-vs-growth T2=c311-11-vs-1 R=controls")


if __name__ == "__main__":
    main()

