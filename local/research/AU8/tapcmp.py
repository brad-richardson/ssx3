#!/usr/bin/env python3
"""AU8: compare PCSX2's SPU2 tap (same run) against tag-1 PCM read as planar and as interleaved.

usage: tapcmp.py TAP.bin TAG1.bin [--out prefix]
TAP.bin: per 48 kHz sample 16 s16 = in0 in1 dry0 dry1 wet0 wet1 ext0 out (L,R each), from the
         AU8 PCSX2 hook (Mixer.cpp spu2Mix). TAG1.bin: AU4/AU8 hook records (u32 vsync + 0x620).
Model of SNDDRV SNDIOP_ee36_iop24_spu48: per channel, 3->4 linear interpolation at input
positions j*0.75 (o0=x[p], o1=(x[p]+3x[p+1])/4, o2=(x[p+1]+x[p+2])/2, o3=(3x[p+2]+x[p+3])/4).
"""
import sys, wave
import numpy as np

SWAP = '--swap' in sys.argv
NAMES = ['in0', 'in1', 'dry0', 'dry1', 'wet0', 'wet1', 'ext0', 'out']


def load_tag(path):
    raw = np.fromfile(path, dtype=np.uint8)
    n = len(raw) // 0x624
    rec = raw[:n * 0x624].reshape(n, 0x624)
    body = rec[:, 4:]
    hdr = body[:, :16].copy().view('<u4')
    ok = (hdr[:, 0] == 1) & (hdr[:, 1] == 0x600)
    serial = body[:, 0x614:0x618].copy().view('<u4')[:, 0]
    body, serial = body[ok], serial[ok]
    _, idx = np.unique(serial, return_index=True)
    body, serial = body[idx], serial[idx]
    gaps = int((np.diff(serial) != 1).sum())
    pcm = body[:, 16:16 + 0x600].copy().view('<i2').reshape(-1, 768)
    planar = pcm.reshape(-1, 2, 384).transpose(0, 2, 1).reshape(-1, 2)
    if SWAP:  # first 384-sample block -> right channel (AU8 E5: side NCC -0.9987 unswapped)
        planar = planar[:, ::-1]
    inter = pcm.reshape(-1, 2)
    return planar.astype(np.float64), inter.astype(np.float64), len(serial), gaps


def up43(x):
    """SNDDRV-style 3->4 linear interpolation per channel."""
    n = len(x)
    pos = np.arange(int((n - 2) * 4 / 3)) * 0.75
    return np.stack([np.interp(pos, np.arange(n), x[:, c]) for c in range(x.shape[1])], 1)


def ncc(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float(np.dot(a, b) / np.sqrt(np.dot(a, a) * np.dot(b, b) + 1e-9))


def find(hay, needle):
    n = 1 << (len(hay) + len(needle)).bit_length()
    c = np.fft.irfft(np.fft.rfft(hay, n) * np.conj(np.fft.rfft(needle, n)), n)[:len(hay) - len(needle)]
    cs = np.concatenate([[0], np.cumsum(hay ** 2)])
    e = cs[len(needle):len(needle) + len(c)] - cs[:len(c)]
    v = c / np.sqrt(np.maximum(e, 1) * np.dot(needle, needle))
    k = int(np.argmax(v))
    return k, float(v[k])


def wr(path, x, sr=48000):
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(np.clip(np.round(x), -32768, 32767).astype(np.int16).tobytes()); w.close()


def main():
    a = sys.argv[1:]
    out = a[a.index('--out') + 1] if '--out' in a else ''
    tap = np.fromfile(a[0], dtype='<i2').reshape(-1, 16).astype(np.float64)
    planar, inter, nrec, gaps = load_tag(a[1])
    print(f"tap {len(tap) / 48000:.2f} s; tag records {nrec} (serial gaps {gaps}) = {nrec * 384 / 36000:.2f} s")
    print("tap stream RMS (L,R) over the whole tap:")
    for i, nm in enumerate(NAMES):
        s = tap[:, 2 * i:2 * i + 2]
        print(f"  {nm:5s} {np.sqrt((s[:, 0] ** 2).mean()):8.1f} {np.sqrt((s[:, 1] ** 2).mean()):8.1f}")
    # pick the input core with the most energy as the ADMA input
    ci = int(np.argmax([np.sqrt((tap[:, 0:2] ** 2).mean()), np.sqrt((tap[:, 2:4] ** 2).mean())]))
    inp = tap[:, 2 * ci:2 * ci + 2]
    print(f"ADMA input = in{ci}")
    SR = 48000
    t0 = 20 * SR  # a 5 s needle from the tap's 20 s point, searched in each tag reading
    needle = inp[t0:t0 + 5 * SR].mean(1)
    res = {}
    for nm, src in (('planar', planar), ('interleaved', inter)):
        m = up43(src)
        k, v = find(m.mean(1), needle - needle.mean())
        # model index k corresponds to tap index t0
        lo = max(0, k - t0); tlo = lo - k + t0
        L = min(len(m) - lo, len(tap) - tlo)
        mm, tt = m[lo:lo + L], tap[tlo:tlo + L]
        best = max(range(-3, 4), key=lambda d: ncc(mm[10:-10, 0], tap[tlo + 10 + d:tlo + L - 10 + d, 2 * ci]))
        tt = tap[tlo + best:tlo + best + L]
        mm = mm[:len(tt)]
        res[nm] = (mm, tt)
        print(f"\n[{nm}] coarse ncc {v:.4f}; aligned span {len(tt) / SR:.2f} s (sub-shift {best})")
        for i, sn in enumerate(NAMES):
            s = tt[:, 2 * i:2 * i + 2]
            if len(s) == 0 or np.sqrt((s ** 2).mean()) < 1:
                continue
            print(f"  vs {sn:5s} L ncc {ncc(mm[:, 0], s[:, 0]):.4f} R ncc {ncc(mm[:, 1], s[:, 1]):.4f} "
                  f"mid {ncc(mm.mean(1), s.mean(1)):.4f} side {ncc(mm[:, 0] - mm[:, 1], s[:, 0] - s[:, 1]):.4f}")
    mm, tt = res['planar']
    s = tt[:, 2 * ci:2 * ci + 2]
    g = [np.dot(s[:, c], mm[:, c]) / np.dot(mm[:, c], mm[:, c]) for c in (0, 1)]
    r = s - mm * np.array(g)
    print(f"\nplanar model -> in{ci}: gain L {g[0]:.4f} R {g[1]:.4f}; residual/in RMS "
          f"L {np.sqrt((r[:, 0] ** 2).mean() / (s[:, 0] ** 2).mean()):.4f} R {np.sqrt((r[:, 1] ** 2).mean() / (s[:, 1] ** 2).mean()):.4f}; "
          f"residual max |.| {np.abs(r).max():.0f}")
    o = tt[:, 14:16]
    go = [np.dot(o[:, c], s[:, c]) / np.dot(s[:, c], s[:, c]) for c in (0, 1)]
    ro = o - s * np.array(go)
    print(f"in{ci} -> out: gain L {go[0]:.4f} R {go[1]:.4f}; (out - g*in)/out RMS "
          f"L {np.sqrt((ro[:, 0] ** 2).mean() / (o[:, 0] ** 2).mean()):.4f} R {np.sqrt((ro[:, 1] ** 2).mean() / (o[:, 1] ** 2).mean()):.4f}")
    if out:
        wr(out + '-out48.wav', o)
        wr(out + '-in48.wav', s)
        wr(out + '-planar-model48.wav', mm)
        wr(out + '-interleaved-model48.wav', res['interleaved'][0])
        wr(out + '-in-resid48.wav', r)
        wr(out + '-out-minus-in48.wav', ro)


if __name__ == '__main__':
    main()
