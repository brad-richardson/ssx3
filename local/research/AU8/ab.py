#!/usr/bin/env python3
"""AU8: build aligned A/B WAVs from OUR tag-1 capture (AU5/AU7 hook: raw 0x620 records) and the
PCSX2 SPU2 tap (final output). A = current runtime (interleaved), B = planar fix (block0->R),
both resampled 36->48 k with SNDDRV's 3->4 interpolation; C = PCSX2 SPU2 out, aligned to B.
usage: ab.py OURS_tag1.bin TAP.bin OUTDIR [--dur 30]
"""
import sys, wave
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from tapcmp import find, ncc, wr

a = sys.argv[1:]
dur = float(a[a.index('--dur') + 1]) if '--dur' in a else 30.0
raw = np.fromfile(a[0], dtype=np.uint8)
rec = raw[:len(raw) // 0x620 * 0x620].reshape(-1, 0x620)
assert ((rec[:, :4].copy().view('<u4')[:, 0] == 1)).all()
pcm = rec[:, 16:16 + 0x600].copy().view('<i2').reshape(-1, 768).astype(np.float64)
inter = pcm.reshape(-1, 2)
planar = pcm.reshape(-1, 2, 384).transpose(0, 2, 1).reshape(-1, 2)[:, ::-1]


def up(x, phi=0.5):
    n = len(x); pos = np.arange(int((n - 3) * 4 / 3)) * 0.75 + phi
    return np.stack([np.interp(pos, np.arange(n), x[:, c]) for c in (0, 1)], 1)


A, B = up(inter), up(planar)
tap = np.fromfile(a[1], dtype='<i2').reshape(-1, 16).astype(np.float64)
C = tap[:, 14:16]
SR = 48000
print(f"ours {len(B) / SR:.1f} s, pcsx2 tap {len(C) / SR:.1f} s")
best = None
for t in range(8, int(len(B) / SR) - 6, 4):
    nd = B[t * SR:(t + 3) * SR].mean(1)
    k, v = find(C.mean(1), nd - nd.mean())
    print(f"  ours {t:3d} s -> pcsx2 tap {k / SR:6.2f} s ncc {v:.4f}")
    if best is None or v > best[2]:
        best = (t, k, v)
t, k, v = best
lag = k - t * SR
s0 = max(t * SR - int(dur / 2 * SR), -lag, 0)
L = min(int(dur * SR), len(B) - s0, len(C) - (s0 + lag))
b, c, aa = B[s0:s0 + L], C[s0 + lag:s0 + lag + L], A[s0:s0 + L]
print(f"best: ours {t} s ncc {v:.4f}; A/B window ours {s0 / SR:.2f}-{(s0 + L) / SR:.2f} s = tap {(s0 + lag) / SR:.2f} s")
for nm, x in (('A interleaved', aa), ('B planar fix', b)):
    print(f"  {nm:14s} vs PCSX2 out: L {ncc(x[:, 0], c[:, 0]):.4f} R {ncc(x[:, 1], c[:, 1]):.4f} "
          f"mid {ncc(x.mean(1), c.mean(1)):.4f} side {ncc(x[:, 0] - x[:, 1], c[:, 0] - c[:, 1]):.4f} "
          f"side rms {np.sqrt((((x[:, 0] - x[:, 1]) / 2) ** 2).mean()):.0f} vs {np.sqrt((((c[:, 0] - c[:, 1]) / 2) ** 2).mean()):.0f}")
d = b - c
print(f"  B - C: rms/C {np.sqrt((d ** 2).mean() / (c ** 2).mean()):.5f} max {np.abs(d).max():.0f}")
o = a[2]
wr(f"{o}/AU8-A-current-interleaved-48k.wav", aa)
wr(f"{o}/AU8-B-planar-fix-48k.wav", b)
wr(f"{o}/AU8-C-pcsx2-spu2-out-48k.wav", c)
