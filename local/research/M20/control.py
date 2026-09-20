#!/usr/bin/env python3
"""M20 positive controls: synthetic truths with KNOWN delta.

Usage: control.py M16_DIR

Imports interior_sites + synth from m20.py (same dir); expectations
are analytic (C-d1 uniform +1, C-dpm checker +-1). The estimator
must recover each injected histogram exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m20 import (N, interior_sites, load_dump, plane_coords,  # noqa: E402
                 synth_w_bytes)


def main():
    m16d = Path(sys.argv[1])
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    synth = synth_w_bytes(v0, full, 0.5)
    sp = interior_sites(v0, mid, full, synth)
    mask = sp["mask"]
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)

    # C-d1: mid' = blend+1 on interior sites with blend<=254.
    feas1 = mask & (s <= 254)
    edge1 = mask & (s > 254)
    mid1 = m.copy()
    mid1[feas1] = s[feas1] + 1
    mid1[edge1] = s[edge1]  # drops out of cell 7 by construction
    sp1 = interior_sites(v0, mid1.astype(np.uint8).tobytes(), full, synth)
    d1 = sp1["delta"][sp1["mask"]]
    ok1 = (bool((sp1["mask"] == feas1).all())
           and bool((d1 == 1).all()) and len(d1) == int(feas1.sum()))
    print(f"C-d1: injected={int(feas1.sum())} edge(blend=255)={int(edge1.sum())} "
          f"recovered_n={int(sp1['mask'].sum())} all_d==+1={bool((d1 == 1).all())} "
          f"set_exact={bool((sp1['mask'] == feas1).all())} pass={ok1}")

    # C-dpm: mid' = blend+-1 checker on feasible interior sites.
    # Feasibility is asymmetric: +1 needs hi-lo>=3 (true on all of cell 7:
    # gap 2 forces mid==blend, hence non-residual); -1 needs hi-lo>=4,
    # else blend-1 lands on/below lo (endpoint cell, not interior).
    # Gap<4 checker-odd sites are left at blend (drop out, counted).
    av = np.frombuffer(v0, np.uint8).astype(np.int16)
    bv = np.frombuffer(full, np.uint8).astype(np.int16)
    gap = np.abs(av - bv)
    r, c = plane_coords()
    plus = ((r + c) % 2 == 0) & mask & (s <= 254)
    minus = ((r + c) % 2 == 1) & mask & (gap >= 4) & (s >= 1)
    edge2 = mask & ~(plus | minus)
    mid2 = m.copy()
    mid2[plus] = s[plus] + 1
    mid2[minus] = s[minus] - 1
    mid2[edge2] = s[edge2]
    sp2 = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    d2 = sp2["delta"][sp2["mask"]]
    want = int(plus.sum()), int(minus.sum())
    got = int((d2 == 1).sum()), int((d2 == -1).sum())
    ok2 = (bool((sp2["mask"] == (plus | minus)).all()) and want == got
           and len(d2) == want[0] + want[1])
    print(f"C-dpm: injected_plus={want[0]} injected_minus={want[1]} "
          f"edge={int(edge2.sum())} recovered_plus={got[0]} "
          f"recovered_minus={got[1]} set_exact="
          f"{bool((sp2['mask'] == (plus | minus)).all())} pass={ok2}")

    print(f"controls pass={bool(ok1 and ok2)}")


if __name__ == "__main__":
    main()
