#!/usr/bin/env python3
"""M19 endpoint-direction split on the M18 residual (offline).

Usage: m19.py M16_DIR M15_DIR WORK_DIR EVID_DIR

Reads M16 per-shape triplets + loo.txt and the M15 triplet; raw XFB
dumps, 573440 B = 640x448 YUYV. Read-only inputs; writes receipt
text to WORK_DIR and (if discriminating) a PNG split map to EVID_DIR.

Tasks (see DESIGN.md, recorded before running):
  1: direction split (8-cell partition + marginals + dout + static + sign)
  2: carrier/band cut of the Task-1 cells
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
M16_TOP10 = [694, 693, 701, 368, 369, 366, 370, 376, 748, 750]
M16_TOP10_SHARES = [6525, 1580, 1126, 441, 393, 372, 262, 260, 245, 239]
M18_EPV0 = {"s0": 9412, "m15": 5281}
M18_EPFULL = {"s0": 8339, "m15": 3924}
M18_INTERIOR = {"s0": 2475, "m15": 2539}
M18_OUTSIDE = {"s0": 2589, "m15": 1674}
M18_P4_STATIC_Y = {"s0": 463, "m15": 439}
CELL_NAMES = ["ep-v0-max", "ep-v0-min", "ep-full-max", "ep-full-min",
              "above", "below", "static", "interior"]


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


def y_hist(d: np.ndarray):
    nz = d[d > 0]
    return [int(((nz >= lo) & (nz < hi)).sum())
            for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 256))]


BAND_ROWS = np.array_split(np.arange(H), 3)


def bands_of(f: np.ndarray):
    return [int(f[b].sum()) for b in BAND_ROWS]


def cell_band_shares(ymap: np.ndarray):
    """Per-cell fractional shares over BAND_ROWS (s0 Y map -> 8x3 floats).

    Regression note: an int() cast here once truncated every share to
    0.0000; control.py's B-share check pins fractional, unit-sum output.
    """
    out = []
    for c in range(8):
        tot = int((ymap == c).sum())
        out.append([((ymap[rows] == c).sum() / tot if tot else 0.0)
                    for rows in BAND_ROWS])
    return out


def synth_w_bytes(v0b: bytes, fullb: bytes, w: float) -> bytes:
    # M18 verbatim: full + floor(w*(v0-full)); at w=0.5 == (v0+full)//2.
    a = np.frombuffer(v0b, np.uint8).astype(np.float64)
    b = np.frombuffer(fullb, np.uint8).astype(np.float64)
    return np.clip(b + np.floor(w * (a - b)), 0, 255).astype(np.uint8).tobytes()


def residual_row(sy, ym, synth: bytes, mid: bytes):
    xd, xm, xn = xdiff(synth, mid)
    dsr = np.abs(sy.astype(np.int16) - ym.astype(np.int16))
    return {"xd": xd, "xm": xm, "xn": xn, "yhist": y_hist(dsr),
            "respx": int((dsr > 0).sum()),
            "bands": bands_of((dsr > 0).astype(np.int64)),
            "fnv": f"{fnv1a(synth):016x}"}


def direction_split(v0b: bytes, midb: bytes, fullb: bytes, synth: bytes):
    """8-cell partition of residual bytes (DESIGN.md ids 0..7).

    Returns dict with labels (int8 [N], -1 = non-residual), dout
    (int16 [N], outside distance, 0 unless cells 4/5), neg
    (bool [N], synth<mid on residual), counts (8,), negcounts (8,).
    """
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    res = s != m
    moved = a != b
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    lab = np.full(N, -1, np.int8)
    lab[res & (m == a) & (a > b)] = 0
    lab[res & (m == a) & (a < b)] = 1
    lab[res & (m == b) & (b > a)] = 2
    lab[res & (m == b) & (b < a)] = 3
    lab[res & moved & (m > hi)] = 4
    lab[res & moved & (m < lo)] = 5
    lab[res & ~moved] = 6
    lab[res & moved & (m > lo) & (m < hi)] = 7
    dout = np.zeros(N, np.int16)
    dout[lab == 4] = (m - hi)[lab == 4]
    dout[lab == 5] = (lo - m)[lab == 5]
    neg = np.zeros(N, bool)
    neg[res] = (s < m)[res]
    counts = np.array([(lab == c).sum() for c in range(8)], np.int64)
    negcounts = np.array([int((neg & (lab == c)).sum()) for c in range(8)],
                         np.int64)
    return {"labels": lab, "dout": dout, "neg": neg, "counts": counts,
            "negcounts": negcounts, "n": int(res.sum())}


def y_cell_map(labels: np.ndarray) -> np.ndarray:
    """Scatter byte labels at Y positions into a (H,W) int8 map (-1 default)."""
    lab2 = labels.reshape(H, ROWB)
    out = np.full((H, W), -1, np.int8)
    out[:, 0::2] = lab2[:, 0::4]
    out[:, 1::2] = lab2[:, 2::4]
    return out


def dout_hist(d: np.ndarray):
    nz = d[d > 0]
    return [int(((nz >= lo) & (nz < hi)).sum())
            for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 1 << 15))]


def parse_loo(path: Path):
    out = {}
    pat = re.compile(r"^\|\s*(\d+)\s*\|\s*\([^)]*\)\s*\|\s*(\d+)\s*\|\s*(\d+)")
    for line in path.read_text(errors="replace").splitlines():
        m = pat.match(line)
        if m:
            out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return out


def task1_lines(tag, v0b, midb, fullb, synth):
    """Canonical Task-1 receipt lines for one frame; also returns artifacts."""
    L = []
    sp = direction_split(v0b, midb, fullb, synth)
    c, ng, n = sp["counts"], sp["negcounts"], sp["n"]
    ep = int(c[0] + c[1] + c[2] + c[3])
    L.append(f"{tag}: n={n} partition_sum={int(c.sum())} "
             f"(want n, else STOP)")
    for i in range(8):
        L.append(f"{tag} cell {i} {CELL_NAMES[i]}: n={int(c[i])} "
                 f"share={c[i] / n:.4f} neg={int(ng[i])} "
                 f"negrate={ng[i] / c[i] if c[i] else 0:.4f}")
    L.append(f"{tag} marginal mid==max(c0+c2)={int(c[0] + c[2])} "
             f"({(c[0] + c[2]) / ep:.4f} of endpoint); "
             f"mid==min(c1+c3)={int(c[1] + c[3])} ({(c[1] + c[3]) / ep:.4f})")
    L.append(f"{tag} marginal mid==v0(c0+c1)={int(c[0] + c[1])} "
             f"(M18 want {M18_EPV0[tag]}); mid==full(c2+c3)={int(c[2] + c[3])} "
             f"(M18 want {M18_EPFULL[tag]})")
    L.append(f"{tag} interior(c7)={int(c[7])} (M18 want {M18_INTERIOR[tag]}); "
             f"static+above+below={int(c[6] + c[4] + c[5])} "
             f"(M18 outside want {M18_OUTSIDE[tag]})")
    d = sp["dout"]
    for cid, nm in ((4, "above"), (5, "below")):
        dd = d[sp["labels"] == cid]
        L.append(f"{tag} dout {nm}: n={len(dd)} hist={dout_hist(dd)} "
                 f"max={int(dd.max()) if len(dd) else 0} "
                 f"mean={float(dd.mean()) if len(dd) else 0:.3f}")
    dd = d[(sp["labels"] == 4) | (sp["labels"] == 5)]
    L.append(f"{tag} dout combined: n={len(dd)} hist={dout_hist(dd)} "
             f"max={int(dd.max()) if len(dd) else 0} "
             f"mean={float(dd.mean()) if len(dd) else 0:.3f}")
    # sign reconciliation: byte-level overall + Y-byte-only vs M18 Y-px
    idx = np.arange(N)
    ypos = (idx % 4 == 0) | (idx % 4 == 2)
    lab, neg = sp["labels"], sp["neg"]
    yres = (lab >= 0) & ypos
    L.append(f"{tag} sign overall byte-level: neg={int(neg.sum())}/{n} "
             f"rate={neg.sum() / n:.4f}")
    L.append(f"{tag} sign Y-byte-only: neg={int((neg & ypos).sum())}/"
             f"{int(yres.sum())} "
             f"rate={(neg & ypos).sum() / yres.sum():.4f} "
             f"(M18 Y-px want ~0.917 s0 / ~0.865 m15)")
    # static-Y reconciliation with P4
    stat_y = int(((lab == 6) & ypos).sum())
    L.append(f"{tag} static-site Y bytes={stat_y} "
             f"(P4 outside-mask Y px want {M18_P4_STATIC_Y[tag]})")
    ok = (int(c.sum()) == n
          and int(c[0] + c[1]) == M18_EPV0[tag]
          and int(c[2] + c[3]) == M18_EPFULL[tag]
          and int(c[7]) == M18_INTERIOR[tag]
          and int(c[6] + c[4] + c[5]) == M18_OUTSIDE[tag]
          and stat_y == M18_P4_STATIC_Y[tag])
    L.append(f"{tag} Task-1 guards: {'OK' if ok else 'MISMATCH: STOP, tabled'}")
    return L, sp


def main():
    m16d, m15d, workd, evidd = (Path(a) for a in sys.argv[1:5])
    workd.mkdir(parents=True, exist_ok=True)
    evidd.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    canon = []  # determinism canonical text (Task 1+2 on s0)

    print("== inputs (read-only) ==")
    inputs = [m16d / "m16-v0-s0000.bin", m16d / "m16-mid-s0000.bin",
              m16d / "m16-full-s0000.bin", m15d / "m15-v0.bin",
              m15d / "m15-mid.bin", m15d / "m15-full.bin"]
    for s in M16_TOP10:
        inputs += [m16d / f"m16-v0-s{s:04d}.bin",
                   m16d / f"m16-mid-s{s:04d}.bin",
                   m16d / f"m16-full-s{s:04d}.bin"]
    for p in inputs:
        b = p.read_bytes()
        print(f"input {p}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")

    print("== model 0 (baseline recompute) ==")
    v015 = load_dump(m15d / "m15-v0.bin")
    mid15 = load_dump(m15d / "m15-mid.bin")
    full15 = load_dump(m15d / "m15-full.bin")
    ym15 = split_planes(np.frombuffer(mid15, np.uint8))[0]
    b15 = synth_w_bytes(v015, full15, 0.5)
    r15 = residual_row(split_planes(np.frombuffer(b15, np.uint8))[0],
                       ym15, b15, mid15)
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    ym0 = split_planes(np.frombuffer(mid, np.uint8))[0]
    b0 = synth_w_bytes(v0, full, 0.5)
    r0 = residual_row(split_planes(np.frombuffer(b0, np.uint8))[0],
                      ym0, b0, mid)
    print(f"m15 baseline: R_0={r15['xd']} fnv={r15['fnv']} (want {R0_M15})")
    print(f"s0 baseline: R_0={r0['xd']} fnv={r0['fnv']} "
          f"(want {R0_M16} / {FNV_S0})")
    if r0["xd"] != R0_M16 or r15["xd"] != R0_M15 or r0["fnv"] != FNV_S0 \
            or r15["fnv"] != FNV_M15:
        print("MISMATCH vs M17/M18 baselines: STOP, tabled.")
        return
    print("baseline cross-check: OK")

    print("== Task 1: direction split s0 ==")
    L0, sp0 = task1_lines("s0", v0, mid, full, b0)
    for ln in L0:
        print(ln)
        canon.append(ln)
    print("== Task 1: direction split m15 ==")
    L15, sp15 = task1_lines("m15", v015, mid15, full15, b15)
    for ln in L15:
        print(ln)

    # ---- Task 2: band cut (Y-residual + raw-byte) ----
    print("== Task 2: band cut (s0 Y-residual bytes) ==")
    ymap0 = y_cell_map(sp0["labels"])
    for bi, rows in enumerate(BAND_ROWS):
        sel = ymap0[rows]
        nres = int((sel >= 0).sum())
        cells = " ".join(f"c{c}={int((sel == c).sum())}" for c in range(8))
        print(f"s0 band {bi} rows {rows[0]}..{rows[-1]}: nY={nres} {cells}")
        canon.append(f"s0 band {bi}: nY={nres} {cells}")
    print("== Task 2: band cut (s0 raw residual bytes) ==")
    lab0 = sp0["labels"].reshape(H, ROWB)
    for bi, rows in enumerate(BAND_ROWS):
        sel = lab0[rows].ravel()
        nres = int((sel >= 0).sum())
        cells = " ".join(f"c{c}={int((sel == c).sum())}" for c in range(8))
        print(f"s0 band {bi} raw: n={nres} {cells}")
    print("== Task 2: band cut (m15 Y-residual bytes) ==")
    ymap15 = y_cell_map(sp15["labels"])
    for bi, rows in enumerate(BAND_ROWS):
        sel = ymap15[rows]
        nres = int((sel >= 0).sum())
        cells = " ".join(f"c{c}={int((sel == c).sum())}" for c in range(8))
        print(f"m15 band {bi} rows {rows[0]}..{rows[-1]}: nY={nres} {cells}")
    print("== Task 2: concentration per cell over bands (s0 Y) ==")
    for c, shares in enumerate(cell_band_shares(ymap0)):
        tot = int((ymap0 == c).sum())
        print(f"s0 cell {c} {CELL_NAMES[c]}: nY={tot} "
              f"bandshares={'/'.join(f'{s:.4f}' for s in shares)}")
        canon.append(f"s0 cellband {c}: nY={tot} "
                     + "/".join(f"{s:.4f}" for s in shares))

    # ---- Task 2: per-carrier masked cell shares ----
    print("== Task 2: top-10 carriers from loo.txt ==")
    loo = parse_loo(m16d / "loo.txt")
    print(f"loo.txt parsed R_s rows: n={len(loo)} (want 764)")
    shares = {s: (R0_M16 - rs) for s, (_, rs) in loo.items() if s != 0}
    top10 = sorted(shares, key=lambda s: -shares[s])[:10]
    print(f"derived top-10 shapes: {top10}")
    print(f"derived shares: {[shares[s] for s in top10]}")
    carriers_ok = (top10 == M16_TOP10
                   and [shares[s] for s in top10] == M16_TOP10_SHARES
                   and len(loo) == 764)
    if not carriers_ok:
        print("CARRIER MISMATCH vs M16 REPORT top-10: STOP per-carrier, tabled.")
    else:
        print("carrier cross-check vs M16 REPORT: OK")
        sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
        res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
        for rank, s in enumerate(top10, 1):
            vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
            mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
            ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
            bl = synth_w_bytes(vv, ff, 0.5)
            yb = split_planes(np.frombuffer(bl, np.uint8))[0]
            yms = split_planes(np.frombuffer(mm, np.uint8))[0]
            ress = yb.astype(np.int16) != yms.astype(np.int16)
            removed = res0 & ~ress
            nrem = int(removed.sum())
            bd = bands_of(removed.astype(np.int64))
            inmask = ymap0[removed]
            cells = " ".join(f"c{c}={int((inmask == c).sum())}"
                             for c in range(8))
            print(f"rank {rank} shape {s}: share={shares[s]} "
                  f"removedYpx={nrem} bands={bd} cells: {cells}")
            canon.append(f"s0 carrier {s}: nrem={nrem} {cells}")
        print("== Task 2: concentration per cell over carriers (s0 Y) ==")
        # rebuild masks for the concentration pass (cheap: 10 resynths)
        masks = {}
        for s in top10:
            vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
            mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
            ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
            bl = synth_w_bytes(vv, ff, 0.5)
            yb = split_planes(np.frombuffer(bl, np.uint8))[0]
            yms = split_planes(np.frombuffer(mm, np.uint8))[0]
            ress = yb.astype(np.int16) != yms.astype(np.int16)
            masks[s] = res0 & ~ress
        for c in range(8):
            tot = int((ymap0 == c).sum())
            sh = " ".join(f"{s}:{((ymap0[masks[s]] == c).sum() / tot):.4f}"
                          if tot else f"{s}:0.0000" for s in top10)
            print(f"s0 cell {c} {CELL_NAMES[c]}: nY={tot} carriershares {sh}")
            canon.append(f"s0 cellcarrier {c}: nY={tot} {sh}")

    # ---- coarse 764-shape direction pass ----
    print("== coarse direction pass: all M16 shapes ==")
    shapes = sorted(int(p.name[8:12]) for p in m16d.glob("m16-v0-s*.bin"))
    print(f"shapes: n={len(shapes)} 0..{max(shapes)}")
    t1 = time.time()
    mism = 0
    print("| shape | R_s | R_loo | epmax | epmin | above | below | static | "
          "interior | negrate |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for i, s in enumerate(shapes):
        vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
        mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
        ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
        bl = synth_w_bytes(vv, ff, 0.5)
        xd, _, _ = xdiff(bl, mm)
        sp = direction_split(vv, mm, ff, bl)
        c = sp["counts"]
        rs = loo.get(s, ("?", "?"))[1]
        if xd != rs:
            mism += 1
        nr = float(sp["neg"].sum() / sp["n"]) if sp["n"] else 0.0
        print(f"| {s} | {xd} | {rs} | {int(c[0] + c[2])} | {int(c[1] + c[3])} "
              f"| {int(c[4])} | {int(c[5])} | {int(c[6])} | {int(c[7])} "
              f"| {nr:.4f} |")
        if (i + 1) % 200 == 0:
            print(f"  ... dir {i + 1}/{len(shapes)}")
    print(f"coarse-pass wall: {time.time() - t1:.1f}s for {len(shapes)} shapes")
    print(f"R_s vs loo.txt mismatches: {mism} (want 0)")

    # ---- direction-rule synths ----
    print("== direction-rule synths ==")
    for tag, (vv, mm, ff, base) in (("s0", (v0, mid, full, r0["xd"])),
                                    ("m15", (v015, mid15, full15, r15["xd"]))):
        a = np.frombuffer(vv, np.uint8)
        b = np.frombuffer(ff, np.uint8)
        rules = {"max": np.maximum(a, b).tobytes(),
                 "min": np.minimum(a, b).tobytes(),
                 "v0": vv, "full": ff}
        for name, syn in rules.items():
            xd, xm, xn = xdiff(syn, mm)
            print(f"{tag} rule {name}: R={xd} explained={base - xd} "
                  f"e={1 - xd / base:.4f} xdmax={xm} xdmean={xn:.3f} "
                  f"fnv={fnv1a(syn):016x}")

    # ---- determinism re-run (Task 1+2 on s0, canonical text) ----
    print("== determinism re-run (Task 1+2 on s0, second pass) ==")
    L0b, sp0b = task1_lines("s0", v0, mid, full, b0)
    canon2 = list(L0b)
    ymap0b = y_cell_map(sp0b["labels"])
    for bi, rows in enumerate(BAND_ROWS):
        sel = ymap0b[rows]
        canon2.append(f"s0 band {bi}: nY={int((sel >= 0).sum())} "
                      + " ".join(f"c{c}={int((sel == c).sum())}"
                                 for c in range(8)))
    for c, shares8 in enumerate(cell_band_shares(ymap0b)):
        tot = int((ymap0b == c).sum())
        canon2.append(f"s0 cellband {c}: nY={tot} "
                      + "/".join(f"{s:.4f}" for s in shares8))
    if carriers_ok:
        sy0 = split_planes(np.frombuffer(b0, np.uint8))[0]
        res0 = sy0.astype(np.int16) != ym0.astype(np.int16)
        masks = {}
        for s in top10:
            vv = load_dump(m16d / f"m16-v0-s{s:04d}.bin")
            mm = load_dump(m16d / f"m16-mid-s{s:04d}.bin")
            ff = load_dump(m16d / f"m16-full-s{s:04d}.bin")
            bl = synth_w_bytes(vv, ff, 0.5)
            yb = split_planes(np.frombuffer(bl, np.uint8))[0]
            yms = split_planes(np.frombuffer(mm, np.uint8))[0]
            ress = yb.astype(np.int16) != yms.astype(np.int16)
            removed = res0 & ~ress
            inmask = ymap0b[removed]
            canon2.append(f"s0 carrier {s}: nrem={int(removed.sum())} "
                          + " ".join(f"c{c}={int((inmask == c).sum())}"
                                     for c in range(8)))
            masks[s] = removed
        for c in range(8):
            tot = int((ymap0b == c).sum())
            canon2.append(f"s0 cellcarrier {c}: nY={tot} "
                          + " ".join(f"{s}:{((ymap0b[masks[s]] == c).sum() / tot):.4f}"
                                     if tot else f"{s}:0.0000"
                                     for s in top10))
    h1 = hashlib.sha256("\n".join(canon).encode()).hexdigest()
    h2 = hashlib.sha256("\n".join(canon2).encode()).hexdigest()
    print(f"canon sha pass1={h1}")
    print(f"canon sha pass2={h2} identical={h1 == h2}")
    print(f"cell counts identical={bool((sp0['counts'] == sp0b['counts']).all())}")

    # ---- PNG split map ----
    print("== PNG split map ==")
    y0p, u0p, v0p = split_planes(np.frombuffer(mid, np.uint8))
    rgbm = yuv_to_rgb(y0p, u0p, v0p)
    cols = np.array([[255, 255, 0],    # 0 ep-v0-max  (yellow)
                     [0, 255, 0],      # 1 ep-v0-min  (green)
                     [255, 165, 0],    # 2 ep-full-max (orange)
                     [0, 128, 255],    # 3 ep-full-min (blue)
                     [255, 0, 0],      # 4 above      (red)
                     [255, 0, 255],    # 5 below      (magenta)
                     [255, 255, 255],  # 6 static     (white)
                     [128, 128, 128]]) # 7 interior   (gray)
    base = 0.35 * rgbm.astype(np.float32)
    over = base.copy()
    for c in range(8):
        over[ymap0 == c] = cols[c]
    p = evidd / "m19-splitmap.png"
    Image.fromarray(over.astype(np.uint8)).resize((320, 224),
                                                  Image.BILINEAR).save(p)
    print(f"png {p}: {p.stat().st_size} B (budget 5242880)")
    print("legend: yellow=ep-v0-max green=ep-v0-min orange=ep-full-max "
          "blue=ep-full-min red=above magenta=below white=static gray=interior")

    print(f"== total wall: {time.time() - t_start:.1f}s ==")
    print("tests: D1=direction-split D2=carrier/band-cut R=rule-synths")


if __name__ == "__main__":
    main()
