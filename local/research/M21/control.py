#!/usr/bin/env python3
"""M21 positive controls: synthetic truths with KNOWN static-site injections.

Usage: control.py M16_DIR

Imports static_sites + synth from m21.py (same dir); expectations
are analytic (C-S1 +-1 injections, C-S2 +-2 injections on
currently-triple-equal static sites). The estimator must recover
each injected count + values + map exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m21 import load_dump, static_sites, synth_w_bytes  # noqa: E402


def run_case(v0, full, synth, mask0, eps0, kval, tag):
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    m = np.frombuffer(mid_g, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    # candidates: triple-equal static sites with room for +-kval
    cand = (a == b) & (s == m) & (a >= kval) & (a <= 255 - kval)
    idx = np.nonzero(cand)[0][:500]
    inj = np.zeros(len(a), bool)
    inj[idx] = True
    sgn = np.where((np.arange(len(a)) % 2 == 0), 1, -1).astype(np.int16)
    mid2 = m.copy()
    mid2[inj] = a[inj] + sgn[inj] * kval
    sp = static_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    want = mask0 | inj
    set_ok = bool((sp["mask"] == want).all())
    got = sp["eps"][sp["mask"]]
    # values on injected sites must equal the known injections
    val_ok = bool((sp["eps"][inj] == (sgn[inj] * kval)).all())
    # original members' eps unchanged
    keep_ok = bool((sp["eps"][mask0] == eps0[mask0]).all())
    npos = int((sgn[idx] > 0).sum())
    nneg = len(idx) - npos
    ok = (set_ok and val_ok and keep_ok and len(idx) == 500
          and not bool((mask0 & inj).any()))
    print(f"{tag}: injected={len(idx)} (+{kval}x{npos}/-{kval}x{nneg}) "
          f"disjoint={not bool((mask0 & inj).any())} "
          f"recovered_n={int(sp['mask'].sum())} "
          f"(want {int(want.sum())}) set_exact={set_ok} values_exact={val_ok} "
          f"orig_kept={keep_ok} pass={ok}")
    return ok


mid_g = None


def main():
    global mid_g
    m16d = Path(sys.argv[1])
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid_g = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    synth = synth_w_bytes(v0, full, 0.5)
    sp0 = static_sites(v0, mid_g, full, synth)
    mask0, eps0 = sp0["mask"], sp0["eps"]
    print(f"baseline R_s0 cell6 n={sp0['n']} (want 2368)")

    ok1 = run_case(v0, full, synth, mask0, eps0, 1, "C-S1")
    ok2 = run_case(v0, full, synth, mask0, eps0, 2, "C-S2")
    print(f"controls pass={bool(ok1 and ok2)}")


if __name__ == "__main__":
    main()
