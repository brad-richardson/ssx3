#!/usr/bin/env python3
"""AU8: is the runtime's host output (PS2X_SOUND_WAV, 36 kHz) the planar reading of its own tag-1?

usage: hostcheck.py HOST.wav TAG1.bin
Host output = ring pops with underrun zeros, so compare 0.5 s windows of non-silent host audio:
locate each in the planar (block0->R) and interleaved readings by NCC and count exact samples.
"""
import sys, wave
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from tapcmp import find

w = wave.open(sys.argv[1]); sr = w.getframerate()
host = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float64)
raw = np.fromfile(sys.argv[2], dtype=np.uint8)
rec = raw[:len(raw) // 0x620 * 0x620].reshape(-1, 0x620)
pcm = rec[:, 16:16 + 0x600].copy().view('<i2').reshape(-1, 768).astype(np.float64)
reads = {'planar': pcm.reshape(-1, 2, 384).transpose(0, 2, 1).reshape(-1, 2)[:, ::-1],
         'interleaved': pcm.reshape(-1, 2)}
print(f"host {len(host) / sr:.1f} s at {sr} Hz; tag {len(pcm)} records; host silent frames "
      f"{(np.abs(host).sum(1) == 0).mean() * 100:.1f}%")
nz = (np.abs(host).sum(1) != 0).astype(np.int8)
edges = np.flatnonzero(np.diff(np.concatenate([[0], nz, [0]])))
runs = [(a, b) for a, b in zip(edges[::2], edges[1::2]) if b - a >= 1500]
print(f"non-silent runs >= 1500 frames: {len(runs)}")
tot = {k: [0, 0] for k in reads}
for a, b in runs[::max(1, len(runs) // 15)]:
    win = host[a + 20:b - 20]
    W = len(win)
    row = [f"host {a / sr:6.2f} s len {W}"]
    for k, x in reads.items():
        kk, v = find(x[:, 0], win[:, 0] - win[:, 0].mean())
        seg = x[kk:kk + W]
        ex = (seg == win).all(1).mean() if len(seg) == W else 0.0
        tot[k][0] += ex * W; tot[k][1] += W
        row.append(f"{k} ncc {v:.4f} exact {ex * 100:5.1f}%")
    print('  '.join(row))
for k, (e, n) in tot.items():
    print(f"{k}: exact frames {e / max(n, 1) * 100:.2f}% of {n} checked")
