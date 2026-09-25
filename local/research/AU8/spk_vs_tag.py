#!/usr/bin/env python3
"""AU8: compare a speaker capture (48 kHz stereo) against tag-1 PCM (36 kHz) from the SAME run.

usage: spk_vs_tag.py TAG36.wav SPK48.wav --tag-at SEC [--dur 20] [--out prefix]
Resamples tag-1 36k->48k (polyphase 4/3), finds it in the speaker by NCC (mono, 5 s window),
then fits a per-channel least-squares gain and reports L/R/Mid/Side NCC, residual/ref and
per-band residual (speaker minus fitted tag). Writes <out>-resid.wav (the "missing" part).
"""
import sys, wave
import numpy as np
from scipy.signal import resample_poly


def rd(path):
    w = wave.open(path)
    sr = w.getframerate()
    assert w.getnchannels() == 2 and w.getsampwidth() == 2, path
    return sr, np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float64)


def wr(path, x, sr):
    w = wave.open(path, "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(np.clip(np.round(x), -32768, 32767).astype(np.int16).tobytes())
    w.close()


def ncc(x, y):
    return float(np.dot(x, y) / np.sqrt(np.dot(x, x) * np.dot(y, y) + 1e-9))


def find(hay, needle):
    n = 1 << (len(hay) + len(needle)).bit_length()
    c = np.fft.irfft(np.fft.rfft(hay, n) * np.conj(np.fft.rfft(needle, n)), n)[:len(hay) - len(needle)]
    cs = np.concatenate([[0], np.cumsum(hay ** 2)])
    e = cs[len(needle):len(needle) + len(c)] - cs[:len(c)]
    v = c / np.sqrt(np.maximum(e, 1) * np.dot(needle, needle))
    k = int(np.argmax(v))
    return k, float(v[k])


def band(x, sr, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    X[(f < lo) | (f >= hi)] = 0
    return np.fft.irfft(X, len(x))


def main():
    a = sys.argv[1:]
    opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    t0, dur, out = opt("--tag-at", 0.0), opt("--dur", 20.0), opt("--out", "")
    sr1, tag = rd(a[0]); sr2, spk = rd(a[1])
    assert sr1 == 36000 and sr2 == 48000
    tag48 = resample_poly(tag, 4, 3, axis=0)
    SR = 48000
    s0, s1 = int(t0 * SR), int((t0 + dur) * SR)
    nd = tag48[s0:s0 + 5 * SR].mean(1); nd = nd - nd.mean()
    k, v = find(spk.mean(1), nd)
    lag = k - s0  # speaker index = tag48 index + lag
    print(f"coarse: tag {t0:.3f}s -> spk {k / SR:.4f}s ncc {v:.4f} lag {lag / SR:+.5f}s")
    T = tag48[s0:s1]; S = spk[s0 + lag:s1 + lag]
    m = min(len(T), len(S)); T, S = T[:m], S[:m]
    # sub-sample refine is unnecessary for a first read; try +-3 samples
    best = max(range(-3, 4), key=lambda d: ncc(tag48[s0:s0 + m, 0], spk[s0 + lag + d:s0 + lag + d + m, 0]))
    lag += best; S = spk[s0 + lag:s0 + lag + m]
    parts = {"L": lambda x: x[:, 0], "R": lambda x: x[:, 1],
             "Mid": lambda x: (x[:, 0] + x[:, 1]) / 2, "Side": lambda x: (x[:, 0] - x[:, 1]) / 2}
    resid = np.zeros_like(S)
    g = []
    for c in (0, 1):
        gc = np.dot(S[:, c], T[:, c]) / np.dot(T[:, c], T[:, c])
        g.append(gc)
        resid[:, c] = S[:, c] - gc * T[:, c]
    print(f"refined lag {lag / SR:+.6f}s  gain L {g[0]:.4f} R {g[1]:.4f} ({20*np.log10(g[0]):+.2f} dB)")
    for name, f in parts.items():
        x, y, r = f(T), f(S), f(resid)
        print(f"{name:4s} rms tag48 {np.sqrt((x**2).mean()):8.1f} spk {np.sqrt((y**2).mean()):8.1f} "
              f"ncc {ncc(x, y):.4f} resid/spk {np.sqrt((r**2).mean() / (y**2).mean()):.3f}")
    print("band      spk_rms  resid_rms  resid/spk (mono mid)")
    mid = lambda x: (x[:, 0] + x[:, 1]) / 2
    for lo, hi in ((0, 150), (150, 500), (500, 2000), (2000, 6000), (6000, 12000), (12000, 18000), (18000, 24000)):
        y, r = band(mid(S), SR, lo, hi), band(mid(resid), SR, lo, hi)
        print(f"{lo:5d}-{hi:5d} {np.sqrt((y**2).mean()):9.1f} {np.sqrt((r**2).mean()):9.1f} {np.sqrt((r**2).mean() / max((y**2).mean(), 1e-9)):.3f}")
    print("per-2s: t ncc_mid resid/spk")
    for t in range(0, int(dur) - 1, 2):
        i = slice(t * SR, (t + 2) * SR)
        y, r, x = mid(S[i]), mid(resid[i]), mid(T[i])
        print(f"{t0 + t:7.1f} {ncc(x, y):.4f} {np.sqrt((r**2).mean() / max((y**2).mean(), 1e-9)):.3f}")
    if out:
        wr(out + "-resid.wav", resid, SR)
        wr(out + "-spk.wav", S, SR)
        wr(out + "-tag48.wav", T * np.array(g), SR)


if __name__ == "__main__":
    main()
