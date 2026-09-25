import sys, numpy as np
sys.argv = ['x', '--swap']
sys.path.insert(0, '/Users/brad/dev/ssx3/local/research/AU8')
import tapcmp as T
tap = np.fromfile('spu2-tap-last70.bin', dtype='<i2').reshape(-1, 16).astype(np.float64)
planar, _, _, _ = T.load_tag('pcsx2-tag1.bin')
inp = tap[:, 0:2]
SR = 48000; t0 = 20 * SR
needle = inp[t0:t0 + 5 * SR].mean(1)
for phi in (0.0, 0.25, 0.5):
    n = len(planar); pos = np.arange(int((n - 3) * 4 / 3)) * 0.75 + phi
    m = np.stack([np.interp(pos, np.arange(n), planar[:, c]) for c in (0, 1)], 1)
    k, v = T.find(m.mean(1), needle - needle.mean())
    best = None
    for d in range(-2, 3):
        lo = k - t0 + d
        L = min(len(m) - lo, len(tap))
        mm, s = m[lo:lo + L], inp[:L]
        r = s - mm
        rr = np.sqrt((r ** 2).mean() / (s ** 2).mean())
        if best is None or rr < best[0]:
            best = (rr, d, np.abs(r).max(), r, s)
    rr, d, mx, r, s = best
    exact = (np.abs(r) <= 1).mean()
    print(f"phi {phi}: ncc {v:.5f} shift {d} resid/in {rr:.5f} max {mx:.0f} |r|<=1: {exact*100:.2f}%")
    if phi == 0.5:
        # where are the big residuals? tick-periodic?
        big = np.where(np.abs(r).max(1) > 64)[0]
        print('  n big', len(big), ' first', big[:10], ' mod 512:', np.bincount(big % 512, minlength=512).argsort()[-5:] if len(big) else '')
        seg = [(i, np.sqrt((r[i:i+SR]**2).mean())) for i in range(0, len(r) - SR, 5 * SR)]
        print('  per-5s resid rms', ' '.join(f"{x:.0f}" for _, x in seg))
        np.save('e7-resid.npy', r.astype(np.float32))
