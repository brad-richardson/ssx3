#!/usr/bin/env python3
"""Mid/side comparison of two 36 kHz stereo s16 tag-1 WAVs (orchestrator, 09-24).

usage: midside.py OURS.wav PCSX2.wav [--start 5] [--dur 59]
Finds the lag of OURS inside PCSX2 by normalized cross-correlation (mono, 5 s window at
--start), refines to the sample on L, then reports L/R/Mid/Side RMS, NCC and diff/ref,
plus per-4-s side level and NCC. AU6 baseline (pre-E54C): Mid NCC 0.9985, Side NCC 0.434,
Side RMS 313 ours vs 382 PCSX2 (-1.8 dB).
"""
import sys, wave
import numpy as np

SR = 36000


def rd(path):
    w = wave.open(path)
    assert w.getframerate() == SR and w.getnchannels() == 2 and w.getsampwidth() == 2, path
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float64)


def ncc(x, y):
    return float(np.dot(x, y) / np.sqrt(np.dot(x, x) * np.dot(y, y)))


def main():
    args = sys.argv[1:]
    start = float(args[args.index("--start") + 1]) if "--start" in args else 5.0
    dur = float(args[args.index("--dur") + 1]) if "--dur" in args else 59.0
    ours, ref = rd(args[0]), rd(args[1])
    a = ours[int(start * SR):int((start + 5) * SR)].mean(1)
    a = a - a.mean()
    refm = ref.mean(1)
    n = 1 << (len(refm) + len(a)).bit_length()
    c = np.fft.irfft(np.fft.rfft(refm, n) * np.conj(np.fft.rfft(a, n)), n)[:len(refm) - len(a)]
    cs = np.concatenate([[0], np.cumsum(refm ** 2)])
    e = cs[len(a):len(a) + len(c)] - cs[:len(c)]
    k = int(np.argmax(c / np.sqrt(np.maximum(e, 1) * np.dot(a, a))))
    base = k - int(start * SR)
    seg = ours[int(start * SR):int((start + 10) * SR), 0]
    adj = max(range(-40, 41), key=lambda d: np.dot(seg, ref[base + int(start * SR) + d:base + int((start + 10) * SR) + d, 0]))
    lag = base + adj
    s0, s1 = int(start * SR), int((start + dur) * SR)
    o = ours[s0:s1]
    p = ref[lag + s0:lag + s1]
    m = min(len(o), len(p))
    o, p = o[:m], p[:m]
    print(f"lag_s {lag / SR:.6f} (sample {lag}) span {start}-{start + dur} s")
    parts = {"L": lambda x: x[:, 0], "R": lambda x: x[:, 1],
             "Mid": lambda x: (x[:, 0] + x[:, 1]) / 2, "Side": lambda x: (x[:, 0] - x[:, 1]) / 2}
    for name, f in parts.items():
        x, y = f(o), f(p)
        print(f"{name:4s} rms ours {np.sqrt((x**2).mean()):8.1f} ref {np.sqrt((y**2).mean()):8.1f} "
              f"ncc {ncc(x, y):.4f} diff/ref {np.sqrt(((x - y)**2).mean() / (y**2).mean()):.3f}")
    print("t side_dB side_ncc")
    side = parts["Side"]
    for t in range(0, int(dur) - 2, 4):
        i = slice(t * SR, (t + 2) * SR)
        xs, ys = side(o[i]), side(p[i])
        print(t + start, f"{20 * np.log10(np.sqrt((xs**2).mean()) / np.sqrt((ys**2).mean())):+.2f}", f"{ncc(xs, ys):.3f}")


if __name__ == "__main__":
    main()
