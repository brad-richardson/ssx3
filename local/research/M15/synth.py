#!/usr/bin/env python3
"""M15 synth-vs-truth: warp interpolation between dumped v0/v1 XFB frames.

Usage: synth.py DUMP_DIR OUT_DIR [--probe PROBE_JSONL]

Reads m15-v0.bin / m15-mid.bin / m15-full.bin (raw XFB scratch dumps,
expected 573440 B = 640x448 YUYV), estimates the dominant global shift
between v0 and full on the Y plane (SAD search), builds:
  synth = mean(warp(v0, +half), warp(full, -half))   (plane-separated Y/U/V)
  blend = byte-mean(v0, full)                        (no-motion baseline)
then diffs synth and blend against truth (mid dump) in M14 analyze.py
shape (xd/xdmax/xdmean over raw bytes). Writes base/synth/truth/diff-map
PNGs (downscaled 320x224) to OUT_DIR plus m15-synth.bin to DUMP_DIR.
Tables, no verdicts.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 640, 448
N = W * H * 2  # YUYV bytes
SEARCH_R = 24


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


def main():
    dump_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    probe = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    out_dir.mkdir(parents=True, exist_ok=True)
    v0 = load_dump(dump_dir / "m15-v0.bin")
    mid = load_dump(dump_dir / "m15-mid.bin")
    full = load_dump(dump_dir / "m15-full.bin")
    print(f"dumps: v0={len(v0)} mid={len(mid)} full={len(full)} "
          f"(want {N} = {W}x{H} YUYV)")
    for name, b in (("v0", v0), ("mid", mid), ("full", full)):
        print(f"dump {name}: fnv={fnv1a(b):016x} "
              f"sha256={hashlib.sha256(b).hexdigest()[:16]}...")
    if probe:
        win = None
        with open(probe, errors="replace") as h:
            for line in h:
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if o.get("event") == "replay" and o.get("action") == "m15_win":
                    win = o.get("detail", "")
        print(f"m15_win: {win}")
        if win:
            for tag, b in (("dvhash", v0), ("dmhash", mid), ("dfhash", full)):
                m = re.search(r"(?:^|\s)%s=([0-9a-f]+)" % tag, win)
                got = m.group(1) if m else "?"
                want = f"{fnv1a(b):016x}"
                print(f"dump-vs-probe {tag}: file={want} probe={got} "
                      f"match={got == want}")
    y0, u0, v0p = split_planes(np.frombuffer(v0, np.uint8))
    ym, um, vm = split_planes(np.frombuffer(mid, np.uint8))
    y1, u1, v1p = split_planes(np.frombuffer(full, np.uint8))
    mask = y0 != y1
    print(f"moved-Y mask: {int(mask.sum())}/{mask.size} px "
          f"({mask.mean():.4f})")
    (dx, dy), sad, sad00 = sad_shift(y0, y1, SEARCH_R, mask)
    print(f"masked shift full-vs-v0 on Y: dx={dx} dy={dy} sad={sad} "
          f"sad00={sad00} (search +- {SEARCH_R})")
    # Half-shift split preserving dx: v0 moves +ceil/2, full moves -floor/2.
    hx0, hy0 = (dx + 1) // 2 if dx >= 0 else dx // 2, \
        (dy + 1) // 2 if dy >= 0 else dy // 2
    hx1, hy1 = dx - hx0, dy - hy0
    print(f"half shifts: v0=({hx0},{hy0}) full=({-hx1},{-hy1}) "
          f"(hx0+hx1 dx={hx0 + hx1} dy={hy0 + hy1})")
    # U/V are half-width: halve the Y shifts (round half away via +1/-1).
    def half(s):
        return (s + 1) // 2 if s >= 0 else -((-s + 1) // 2)
    ux0, uy0, ux1, uy1 = half(hx0), half(hy0), half(hx1), half(hy1)
    print(f"uv half shifts: v0=({ux0},{uy0}) full=({-ux1},{-uy1})")
    sy = ((shift_plane(y0, hx0, hy0).astype(np.uint16)
           + shift_plane(y1, -hx1, -hy1).astype(np.uint16)) // 2).astype(np.uint8)
    su = ((shift_plane(u0, ux0, uy0).astype(np.uint16)
           + shift_plane(u1, -ux1, -uy1).astype(np.uint16)) // 2).astype(np.uint8)
    sv = ((shift_plane(v0p, ux0, uy0).astype(np.uint16)
           + shift_plane(v1p, -ux1, -uy1).astype(np.uint16)) // 2).astype(np.uint8)
    synth = join_planes(sy, su, sv).tobytes()
    blend = (((np.frombuffer(v0, np.uint8).astype(np.uint16)
               + np.frombuffer(full, np.uint8).astype(np.uint16)) // 2)
             .astype(np.uint8).tobytes())
    (dump_dir / "m15-synth.bin").write_bytes(synth)
    print(f"synth: fnv={fnv1a(synth):016x} "
          f"sha256={hashlib.sha256(synth).hexdigest()[:16]}... "
          f"wrote {dump_dir / 'm15-synth.bin'}")
    print(f"blend: fnv={fnv1a(blend):016x} "
          f"sha256={hashlib.sha256(blend).hexdigest()[:16]}...")
    print("| pair | xd | xdmax | xdmean | frac_moved |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for name, a, b in (("full-vs-v0", full, v0), ("mid-vs-v0", mid, v0),
                       ("full-vs-mid", full, mid),
                       ("synth-vs-truth", synth, mid),
                       ("blend-vs-truth", blend, mid)):
        xd, xm, xn = xdiff(a, b)
        print(f"| {name} | {xd} | {xm} | {xn:.3f} | {xd / N:.4f} |")
    # Diagnostics: |d| histograms on Y + residual vertical bands + SAD minimum.
    d01 = np.abs(y0.astype(np.int16) - y1.astype(np.int16))
    dsr = np.abs(sy.astype(np.int16) - ym.astype(np.int16))
    for name, d in (("v0-vs-full-Y", d01), ("synth-vs-truth-Y", dsr)):
        nz = d[d > 0]
        bins = [int(((nz >= lo) & (nz < hi)).sum())
                for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 256))]
        print(f"Y-|d| {name}: moved_px={int((d > 0).sum())} "
              f"hist[1,2-3,4-7,8-15,16+]={bins}")
    bands = np.array_split(np.arange(H), 3)
    res = (dsr > 0).astype(np.int64)
    print(f"residual-Y bands top/mid/bot px: {[int(res[b].sum()) for b in bands]} "
          f"(rows 0-148/149-297/298-447)")
    mov = (d01 > 0).astype(np.int64)
    print(f"moved-Y bands top/mid/bot px: {[int(mov[b].sum()) for b in bands]}")
    ai, bi = y0.astype(np.int16), y1.astype(np.int16)
    print("masked SAD 3x3 around best (cols dx-1..dx+1):")
    for oy in range(dy - 1, dy + 2):
        row = []
        for ox in range(dx - 1, dx + 2):
            s = shift_plane(ai, ox, oy)
            row.append(str(int(np.abs(s - bi)[mask].sum())))
        print(f"dy={oy}: {' '.join(row)}")
    # PNGs: base / synth / truth + red-over-truth diff map, 320x224.
    rgb0 = yuv_to_rgb(y0, u0, v0p)
    rgbs = yuv_to_rgb(sy, su, sv)
    rgbm = yuv_to_rgb(ym, um, vm)
    d = np.abs(sy.astype(np.int16) - ym.astype(np.int16))
    a = np.clip(d / 32.0, 0, 1)[..., None]
    over = ((1 - a) * rgbm.astype(np.float32)
            + a * np.array([255, 0, 0], np.float32)).astype(np.uint8)
    total = 0
    for name, arr in (("m15-base.png", rgb0), ("m15-synth.png", rgbs),
                      ("m15-truth.png", rgbm), ("m15-diffmap.png", over)):
        p = out_dir / name
        Image.fromarray(arr).resize((320, 224), Image.BILINEAR).save(p)
        total += p.stat().st_size
        print(f"png {p}: {p.stat().st_size} B")
    print(f"png total: {total} B (budget 5242880)")


if __name__ == "__main__":
    main()
