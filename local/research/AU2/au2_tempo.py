#!/usr/bin/env python3
"""AU2: beat-period fingerprint. 10 ms RMS envelope -> positive onset
differences -> autocorrelation over 0.3-2.0 s lags; prints the top 4 lags.
Inputs are s16le stereo at 36 kHz (a .wav has its 44-byte header skipped).
Usage: au2_tempo.py <file> <start_s> <dur_s> [label]"""
import math, struct, sys
path, st, du = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
rate, hop = 36000, 0.01
base = 44 if path.endswith(".wav") else 0
f = open(path, "rb"); f.seek(base + int(st * rate) * 4); d = f.read(int(du * rate) * 4)
s = struct.unpack(f"<{len(d) // 2}h", d); h = int(rate * hop); e = []
for i in range(0, len(s) // 2 - h, h):
    seg = s[2 * i:2 * (i + h)]; e.append(math.sqrt(sum(x * x for x in seg) / len(seg)))
on = [max(0, e[i] - e[i - 1]) for i in range(1, len(e))]; m = sum(on) / len(on); on = [x - m for x in on]
best = sorted(((sum(on[i] * on[i + lag] for i in range(len(on) - lag)), lag) for lag in range(30, 200)), reverse=True)[:4]
print(f"{sys.argv[4] if len(sys.argv) > 4 else path} {st:g}-{st + du:g} s: top lags " + ", ".join(f"{l * hop:.2f} s" for c, l in best))
