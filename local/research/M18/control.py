#!/usr/bin/env python3
"""M18 positive controls (offline, recorded in DESIGN.md before running).

Usage: control.py M16_DIR  (run from the work dir; reads m18.txt for the A gate)

- W control: synthetic truth = floor(0.3*v0 + 0.7*full) on s0 ->
  coarse sweep argmin must read 0.3 exactly.
- P control: synthetic +1 residual on half the top-decile gradient px ->
  P1 top-decile rate / bottom-decile rate >= 5.
- A control (runs iff m18.txt gates Test A RUNS): s0-v0 warped by known
  p=(tx=+1.0, th=+0.5deg) -> fit must recover tx in [0.5,1.5],
  th in [0.25,0.75]deg.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m18 import (W_COARSE, affine_fit, grad_tables, load_dump, rint_u8,
                 split_planes, synth_w_bytes, warp_affine, xdiff)


def main():
    m16d = Path(sys.argv[1])
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    y0 = split_planes(np.frombuffer(v0, np.uint8))[0]
    y1 = split_planes(np.frombuffer(full, np.uint8))[0]

    print("== W control: synthetic truth at w=0.3 ==")
    tru = synth_w_bytes(v0, full, 0.3)
    got = None
    for w in W_COARSE:
        xd, _, _ = xdiff(synth_w_bytes(v0, full, w), tru)
        print(f"w={w:.1f}: R={xd}")
        if got is None and xd == 0:
            got = w
    # argmin by strict minimum, first wins (m18.py rule)
    vals = [(w, xdiff(synth_w_bytes(v0, full, w), tru)[0]) for w in W_COARSE]
    argmin = min(vals, key=lambda t: t[1])[0]
    print(f"W control: argmin={argmin} want=0.3 pass={argmin == 0.3}")

    print("== P control: synthetic +1 residual on top-decile gradient px ==")
    midb = load_dump(m16d / "m16-mid-s0000.bin")
    ym = split_planes(np.frombuffer(midb, np.uint8))[0]
    yp = np.pad(ym.astype(np.int16), 1, mode="edge")
    gx = (yp[1:-1, 2:] - yp[1:-1, :-2]) // 2
    gy = (yp[2:, 1:-1] - yp[:-2, 1:-1]) // 2
    mag = np.abs(gx) + np.abs(gy)
    qs = np.quantile(mag, np.linspace(0, 1, 11))
    dec = np.clip(np.digitize(mag, qs[1:-1], right=True), 0, 9)
    rng = np.random.default_rng(18)
    top = np.flatnonzero(dec == 9)
    pick = rng.choice(top, size=len(top) // 2, replace=False)
    sy = ym.copy()
    flat = sy.ravel()
    flat[pick] = np.clip(flat[pick].astype(np.int16) + 1, 0, 255).astype(np.uint8)
    grad_tables(ym, sy, y0, y1, "P-control")
    res = sy.astype(np.int16) != ym.astype(np.int16)
    rtop = res[dec == 9].mean()
    rbot = res[dec == 0].mean()
    print(f"P control: top-dec rate={rtop:.4f} bottom-dec rate={rbot:.4f} "
          f"ratio={'inf' if rbot == 0 else f'{rtop / rbot:.2f}'} "
          f"pass={rbot == 0 or rtop / rbot >= 5}")

    gate = Path("m18.txt").read_text(errors="replace") if Path("m18.txt").exists() else ""
    if "Test A RUNS" in gate:
        print("== A control: known warp p=(tx=+1.0, th=+0.5deg) ==")
        inj = (1.0, 0.0, 0.5, 1.0, 0.0, 0.0)
        full_syn = rint_u8(warp_affine(y0, inj))
        p, sadb, sad00, nm = affine_fit(y0, full_syn)
        print(f"A control: recovered p=(tx={p[0]:+.3f},ty={p[1]:+.3f},th={p[2]:+.3f}d,"
              f"s={p[3]:.4f},shx={p[4]:+.4f},shy={p[5]:+.4f}) sad00={sad00:.0f} "
              f"sadbest={sadb:.0f}")
        ok = (0.5 <= p[0] <= 1.5) and (0.25 <= p[2] <= 0.75)
        print(f"A control: tx in [0.5,1.5]={0.5 <= p[0] <= 1.5} "
              f"th in [0.25,0.75]={0.25 <= p[2] <= 0.75} pass={ok}")
    else:
        print("== A control: SKIPPED (m18.txt does not gate Test A RUNS) ==")


if __name__ == "__main__":
    main()
