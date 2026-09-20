#!/usr/bin/env python3
"""M16 leave-one-out: per-shape warp synth vs truth on one recorded frame.

Usage: loo.py DUMP_DIR OUT_DIR PROBE_JSONL [WORKERS]

Reads m16-v0-sNNNN.bin / m16-mid-sNNNN.bin / m16-full.bin triplets (raw
XFB scratch dumps, 573440 B = 640x448 YUYV), warps per shape (M15
synth.py estimator verbatim: masked-SAD dominant shift, plane-separated
warp + blend), and attributes the shape-0 residual R_0 to draws via
removed shares R_0 - R_s. Writes per-shape m16-synth-sNNNN.bin to
DUMP_DIR plus base/diff-map/carrier PNGs (320x224) to OUT_DIR.
Tables, no verdicts.
"""
import hashlib
import json
import multiprocessing as mp
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 640, 448
N = W * H * 2  # YUYV bytes
SEARCH_R = 24
DEGEN_MASK_MIN = 64  # moved-Y px below which shift is (0,0) by rule


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


def join_planes(y: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    out = np.empty((H, W * 2), np.uint8)
    out[:, 0::4] = y[:, 0::2]
    out[:, 1::4] = u
    out[:, 2::4] = y[:, 1::2]
    out[:, 3::4] = v
    return out.reshape(-1)


def yuv_to_rgb(y: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    uu = np.repeat(u.astype(np.float32), 2, axis=1)
    vv = np.repeat(v.astype(np.float32), 2, axis=1)
    yy = y.astype(np.float32)
    r = yy + 1.402 * (vv - 128)
    g = yy - 0.344136 * (uu - 128) - 0.714136 * (vv - 128)
    b = yy + 1.772 * (uu - 128)
    return np.clip(np.stack([r, g, b], -1), 0, 255).astype(np.uint8)


def shift_plane(p: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """Shift by (dx,dy) with edge replicate; +dx moves content right."""
    h, w = p.shape
    xs = np.clip(np.arange(w) - dx, 0, w - 1)
    ys = np.clip(np.arange(h) - dy, 0, h - 1)
    return p[ys][:, xs]


def sad_shift(a: np.ndarray, b: np.ndarray, rng: int, mask: np.ndarray):
    """Dominant shift (dx,dy) of the MASKED (moved) pixels such that
    shift_plane(a,dx,dy) best matches b. Unmasked SAD degenerates to (0,0)
    on static-dominated frames (any nonzero shift misaligns the static
    majority), so only moved pixels vote. Returns (best, best_sad, sad00)."""
    best, best_sad = (0, 0), None
    ai = a.astype(np.int16)
    bi = b.astype(np.int16)
    sad00 = int(np.abs(ai - bi)[mask].sum())
    for dy in range(-rng, rng + 1):
        for dx in range(-rng, rng + 1):
            s = shift_plane(ai, dx, dy)
            sad = int(np.abs(s - bi)[mask].sum())
            if best_sad is None or sad < best_sad:
                best_sad, best = sad, (dx, dy)
    return best, best_sad, sad00


def xdiff(a: bytes, b: bytes):
    aa = np.frombuffer(a, np.uint8).astype(np.int16)
    bb = np.frombuffer(b, np.uint8).astype(np.int16)
    d = np.abs(aa - bb)
    nz = d[d > 0]
    if len(nz) == 0:
        return 0, 0, 0.0
    return int(len(nz)), int(nz.max()), float(nz.mean())


def half_split(dx: int, dy: int):
    hx0 = (dx + 1) // 2 if dx >= 0 else dx // 2
    hy0 = (dy + 1) // 2 if dy >= 0 else dy // 2
    return hx0, hy0, dx - hx0, dy - hy0


def half_uv(s: int):
    return (s + 1) // 2 if s >= 0 else -((-s + 1) // 2)


def warp_synth(y0, u0, v0p, y1, u1, v1p, dx: int, dy: int):
    hx0, hy0, hx1, hy1 = half_split(dx, dy)
    ux0, uy0, ux1, uy1 = half_uv(hx0), half_uv(hy0), half_uv(hx1), half_uv(hy1)
    sy = ((shift_plane(y0, hx0, hy0).astype(np.uint16)
           + shift_plane(y1, -hx1, -hy1).astype(np.uint16)) // 2).astype(np.uint8)
    su = ((shift_plane(u0, ux0, uy0).astype(np.uint16)
           + shift_plane(u1, -ux1, -uy1).astype(np.uint16)) // 2).astype(np.uint8)
    sv = ((shift_plane(v0p, ux0, uy0).astype(np.uint16)
           + shift_plane(v1p, -ux1, -uy1).astype(np.uint16)) // 2).astype(np.uint8)
    return sy, su, sv, (hx0, hy0, hx1, hy1), (ux0, uy0, ux1, uy1)


def y_hist(d: np.ndarray):
    nz = d[d > 0]
    return [int(((nz >= lo) & (nz < hi)).sum())
            for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 256))]


def bands_of(f: np.ndarray):
    bands = np.array_split(np.arange(H), 3)
    return [int(f[b].sum()) for b in bands]


def synth_shape(dump_dir: str, shape: int):
    """Full per-shape pipeline. Returns a small dict; writes the synth bin."""
    dd = Path(dump_dir)
    v0 = load_dump(dd / f"m16-v0-s{shape:04d}.bin")
    mid = load_dump(dd / f"m16-mid-s{shape:04d}.bin")
    full = load_dump(dd / f"m16-full-s{shape:04d}.bin")
    y0, u0, v0p = split_planes(np.frombuffer(v0, np.uint8))
    ym, um, vm = split_planes(np.frombuffer(mid, np.uint8))
    y1, u1, v1p = split_planes(np.frombuffer(full, np.uint8))
    mask = y0 != y1
    nmoved = int(mask.sum())
    if nmoved < DEGEN_MASK_MIN:
        dx, dy, sad, sad00, degen = 0, 0, 0, 0, 1
    else:
        (dx, dy), sad, sad00 = sad_shift(y0, y1, SEARCH_R, mask)
        degen = 0
    sy, su, sv, halves, uvhalves = warp_synth(y0, u0, v0p, y1, u1, v1p, dx, dy)
    synth = join_planes(sy, su, sv).tobytes()
    (dd / f"m16-synth-s{shape:04d}.bin").write_bytes(synth)
    xd, xm, xn = xdiff(synth, mid)
    dsr = np.abs(sy.astype(np.int16) - ym.astype(np.int16))
    return {"shape": shape, "dx": dx, "dy": dy, "sad": sad, "sad00": sad00,
            "nmoved": nmoved, "degen": degen, "halves": halves,
            "uvhalves": uvhalves, "xd": xd, "xm": xm, "xn": xn,
            "fnv": f"{fnv1a(synth):016x}",
            "sha": hashlib.sha256(synth).hexdigest()[:16],
            "yhist": y_hist(dsr), "respx": int((dsr > 0).sum()),
            "bands": bands_of((dsr > 0).astype(np.int64))}


def parse_probe(probe: Path):
    win, rows = None, {}
    with open(probe, errors="replace") as h:
        for line in h:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if o.get("event") != "replay":
                continue
            a = o.get("action")
            if a == "m16_win":
                win = o.get("detail", "")
            elif a == "m16_ref2":
                d = o.get("detail", "")
                m = re.search(r"(?:^|\s)r=(\d+)", d)
                if m:
                    rows[int(m.group(1))] = d
    return win, rows


def kv(detail: str, key: str, default=None):
    m = re.search(r"(?:^|\s)%s=([^\s]+)" % re.escape(key), detail or "")
    return m.group(1) if m else default


def main():
    dump_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    probe = Path(sys.argv[3])
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else (os.cpu_count() or 4)
    out_dir.mkdir(parents=True, exist_ok=True)
    shapes = sorted(int(p.name[8:12]) for p in dump_dir.glob("m16-v0-s*.bin"))
    print(f"shapes with v0 dumps: n={len(shapes)} "
          f"(0..{max(shapes) if shapes else '?'}"
          f"{'' if shapes == list(range(len(shapes))) else ', NONCONTIGUOUS'})")
    missing = [s for s in shapes
               if not (dump_dir / f"m16-mid-s{s:04d}.bin").exists()
               or not (dump_dir / f"m16-full-s{s:04d}.bin").exists()]
    print(f"shapes missing mid/full dumps: n={len(missing)} {missing[:10]}")
    shapes = [s for s in shapes if s not in missing]
    win, rows = parse_probe(probe)
    print(f"m16_win: {win}")
    ns = int(kv(win or "", "nshapes", "0"))
    print(f"probe m16_ref2 rows: n={len(rows)} nshapes={ns}")
    # Dump-vs-probe FNV cross-check: v0b r=ns+w, midb r=3ns+w, fullb r=5ns+w.
    mm = 0
    for s in shapes:
        for tag, r in (("v0", ns + s), ("mid", 3 * ns + s), ("full", 5 * ns + s)):
            b = (dump_dir / f"m16-{tag}-s{s:04d}.bin").read_bytes()
            want = f"{fnv1a(b):016x}"
            got = kv(rows.get(r, ""), "hash", "?")
            if got != want:
                mm += 1
                if mm <= 10:
                    print(f"DUMP-PROBE MISMATCH s={s} {tag} r={r}: "
                          f"file={want} probe={got}")
    print(f"dump-vs-probe mismatches: {mm}/{3 * len(shapes)}")
    # Shape 0 first (timed full search; the verbatim control).
    t0 = time.time()
    r0 = synth_shape(str(dump_dir), 0)
    t0 = time.time() - t0
    print(f"shape-0 full search: {t0:.1f}s nmoved={r0['nmoved']} "
          f"shift=({r0['dx']},{r0['dy']}) sad={r0['sad']} sad00={r0['sad00']} "
          f"halves={r0['halves']} uv={r0['uvhalves']}")
    print(f"shape-0 synth: fnv={r0['fnv']} sha={r0['sha']}... "
          f"R_0={r0['xd']} xdmax={r0['xm']} xdmean={r0['xn']:.3f} "
          f"frac={r0['xd'] / N:.4f}")
    print(f"shape-0 residual-Y: moved_px={r0['respx']} hist={r0['yhist']} "
          f"bands={r0['bands']}")
    rest = [s for s in shapes if s != 0]
    print(f"pool: {len(rest)} shapes x {workers} workers "
          f"(est {t0 * len(rest) / workers / 60:.1f} min at shape-0 rate)")
    t1 = time.time()
    try:
        ctx = mp.get_context("fork")
        with ctx.Pool(workers) as pool:
            got = pool.starmap(synth_shape,
                               [(str(dump_dir), s) for s in rest])
    except Exception as e:
        print(f"pool failed ({e}); sequential fallback")
        got = []
        for i, s in enumerate(rest):
            got.append(synth_shape(str(dump_dir), s))
            if (i + 1) % 50 == 0:
                print(f"  ... {i + 1}/{len(rest)}")
    t1 = time.time() - t1
    print(f"pool wall: {t1:.1f}s for {len(got)} shapes")
    res = {0: r0}
    res.update({g["shape"]: g for g in got})
    # Shift distribution + degenerate rule hits.
    shifts = {}
    for s, g in res.items():
        shifts[(g["dx"], g["dy"])] = shifts.get((g["dx"], g["dy"]), 0) + 1
    degen = sorted(s for s, g in res.items() if g["degen"])
    print(f"shift distribution (dx,dy): count = {dict(sorted(shifts.items()))}")
    print(f"degenerate-mask shapes (<{DEGEN_MASK_MIN} moved-Y): "
          f"n={len(degen)} {degen[:20]}")
    # Attribution tables (M14-autoscan shape).
    r0xd = r0["xd"]
    shares = {s: r0xd - g["xd"] for s, g in res.items() if s != 0}
    pos = sum(1 for v in shares.values() if v > 0)
    zer = sum(1 for v in shares.values() if v == 0)
    neg = sum(1 for v in shares.values() if v < 0)
    spos = sum(v for v in shares.values() if v > 0)
    print(f"| shape | shift | nmoved | R_s | removed share (R_0 - R_s) |")
    print(f"| ---: | --- | ---: | ---: | ---: |")
    for s in sorted(res):
        g = res[s]
        share = "" if s == 0 else str(r0xd - g["xd"])
        print(f"| {s} | ({g['dx']},{g['dy']}) | {g['nmoved']} | {g['xd']} | "
              f"{share} |")
    print(f"share arithmetic (R_0={r0xd}; n={len(shares)}): "
          f"pos/zero/neg={pos}/{zer}/{neg} "
          f"max={max(shares.values()) if shares else 'n/a'} "
          f"min={min(shares.values()) if shares else 'n/a'} "
          f"sum_pos={spos} ({spos / r0xd:.3f} of R_0)" if r0xd else
          f"share arithmetic: R_0=0, n={len(shares)}")
    # clk map from probe rows (b-rep of each shape carries clk).
    clk = {}
    for s in res:
        d = rows.get(5 * ns + s, "")
        try:
            clk[s] = int(kv(d, "clk", "-1"))
        except (TypeError, ValueError):
            clk[s] = -1
    ranked = sorted(shares.items(), key=lambda kv_: kv_[1], reverse=True)
    print(f"top-10 carriers by removed share (R_0={r0xd}):")
    print(f"| rank | clk | shape | surviving R_s | removed share | "
          f"shift | nmoved |")
    print(f"| ---: | ---: | ---: | ---: | ---: | --- | ---: |")
    for rank, (s, v) in enumerate(ranked[:10], 1):
        g = res[s]
        print(f"| {rank} | {clk.get(s, '?')} | {s} | {g['xd']} | {v} | "
              f"({g['dx']},{g['dy']}) | {g['nmoved']} |")
    negs = sorted(((s, v) for s, v in shares.items() if v < 0),
                  key=lambda kv_: kv_[1])
    print(f"negatives (n={len(negs)}): "
          f"{[(v, clk.get(s, '?'), s) for s, v in negs[:12]]}")
    # Removed-residual maps for the top carriers (HUD-edge analysis):
    # residual_0 Y pixels vanishing in residual_s, band-clustered.
    y0, u0, v0p = split_planes(np.frombuffer(
        load_dump(dump_dir / "m16-v0-s0000.bin"), np.uint8))
    ym0, um0, vm0 = split_planes(np.frombuffer(
        load_dump(dump_dir / "m16-mid-s0000.bin"), np.uint8))
    ys0, _, _ = split_planes(np.frombuffer(
        (dump_dir / "m16-synth-s0000.bin").read_bytes(), np.uint8))
    res0 = np.abs(ys0.astype(np.int16) - ym0.astype(np.int16)) > 0
    print(f"residual_0 Y px: {int(res0.sum())}")
    for rank, (s, v) in enumerate(ranked[:10], 1):
        yms, _, _ = split_planes(np.frombuffer(
            load_dump(dump_dir / f"m16-mid-s{s:04d}.bin"), np.uint8))
        yss, _, _ = split_planes(np.frombuffer(
            (dump_dir / f"m16-synth-s{s:04d}.bin").read_bytes(), np.uint8))
        ress = np.abs(yss.astype(np.int16) - yms.astype(np.int16)) > 0
        removed = res0 & ~ress
        print(f"carrier{rank} shape={s} clk={clk.get(s, '?')}: "
              f"removed_Y_px={int(removed.sum())} bands={bands_of(removed)} "
              f"(res0={int(res0.sum())} ress={int(ress.sum())})")
    # PNGs: base / diff-map / top-2 carrier overlays, 320x224.
    rgb0 = yuv_to_rgb(y0, u0, v0p)
    rgbm = yuv_to_rgb(ym0, um0, vm0)
    d = np.abs(ys0.astype(np.int16) - ym0.astype(np.int16))
    a = np.clip(d / 32.0, 0, 1)[..., None]
    over = ((1 - a) * rgbm.astype(np.float32)
            + a * np.array([255, 0, 0], np.float32)).astype(np.uint8)
    outs = [("m16-base.png", rgb0), ("m16-diffmap.png", over)]
    for rank, (s, v) in enumerate(ranked[:2], 1):
        yms, _, _ = split_planes(np.frombuffer(
            load_dump(dump_dir / f"m16-mid-s{s:04d}.bin"), np.uint8))
        yss, _, _ = split_planes(np.frombuffer(
            (dump_dir / f"m16-synth-s{s:04d}.bin").read_bytes(), np.uint8))
        ress = np.abs(yss.astype(np.int16) - yms.astype(np.int16)) > 0
        removed = res0 & ~ress
        stay = res0 & ress
        base = (0.35 * rgbm.astype(np.float32)).astype(np.float32)
        base[stay] = [255, 0, 0]
        base[removed] = [0, 255, 0]
        outs.append((f"m16-carrier{rank}.png", base.astype(np.uint8)))
    total = 0
    for name, arr in outs:
        p = out_dir / name
        Image.fromarray(arr).resize((320, 224), Image.BILINEAR).save(p)
        total += p.stat().st_size
        print(f"png {p}: {p.stat().st_size} B")
    print(f"png total: {total} B (budget 5242880)")


if __name__ == "__main__":
    main()
