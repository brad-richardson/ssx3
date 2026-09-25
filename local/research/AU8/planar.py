#!/usr/bin/env python3
"""AU8: reinterpret tag-1 records (written as 384 interleaved frames per tick) as planar
(384 s16 right, then 384 s16 left), per SNDDRV SNDIOP_ee36_iop24_spu48 (EE input stride 0x300 per channel).

usage: planar.py IN36.wav OUT36.wav   -> prints smoothness stats for both readings
"""
import sys, wave
import numpy as np


def rd(p):
    w = wave.open(p)
    assert w.getframerate() == 36000 and w.getnchannels() == 2 and w.getsampwidth() == 2
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def stats(name, x):
    x = x.astype(np.float64)
    d = np.abs(np.diff(x[:, 0])).mean(), np.abs(np.diff(x[:, 1])).mean()
    mid, side = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2
    # seam: |delta| across the 384-frame record boundary vs elsewhere (ch0)
    dd = np.abs(np.diff(x[:, 0]))
    seam = dd[383::384].mean() / dd.mean()
    half = dd[191::384].mean() / dd.mean()
    ncc = np.dot(x[:, 0] - x[:, 0].mean(), x[:, 1] - x[:, 1].mean()) / np.sqrt(((x[:, 0] - x[:, 0].mean()) ** 2).sum() * ((x[:, 1] - x[:, 1].mean()) ** 2).sum())
    print(f"{name:12s} mean|dL| {d[0]:7.1f} mean|dR| {d[1]:7.1f}  mid rms {np.sqrt((mid**2).mean()):7.1f} side rms {np.sqrt((side**2).mean()):7.1f}"
          f"  L/R ncc {ncc:.4f}  seam384 {seam:.2f} mid192 {half:.2f}")


s = rd(sys.argv[1])
n = len(s) // 768 * 768
s = s[:n]
inter = s.reshape(-1, 2)
rec = s.reshape(-1, 2, 384)            # per record: [ch][sample]
planar = rec.transpose(0, 2, 1).reshape(-1, 2)
planar = planar[:, ::-1]  # first block -> right channel (AU8 E5/E7, PCSX2 SPU2 input)
stats("interleaved", inter)
stats("planar", planar)
if len(sys.argv) > 2:
    w = wave.open(sys.argv[2], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(36000)
    w.writeframes(planar.astype(np.int16).tobytes()); w.close()
