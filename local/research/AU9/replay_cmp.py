# AU9: our SPU model replayed on PCSX2's own tag-3 records vs PCSX2's tapped voice layer (dry0+dry1), same capture.
import numpy as np, sys
TAP0 = 19400000  # first tap sample in tap-race.bin
t = np.fromfile(sys.argv[1], dtype='<i2').reshape(-1, 16).astype(np.float64)
ref = t[:, 4:6] + t[:, 6:8]
ours = np.fromfile(sys.argv[2], dtype='<i2').reshape(-1, 2).astype(np.float64)
idx = np.fromfile(sys.argv[3], dtype='<u4')
start = int(idx[0]) - TAP0  # our tick 0 is near this tap sample
best = None
for lag in range(-4096, 4097):
    a0 = start + lag
    if a0 < 0: continue
    n = min(len(ours), len(ref) - a0, 48000 * 20)
    x = ours[:n].mean(1); y = ref[a0:a0 + n].mean(1)
    if (x ** 2).sum() == 0 or (y ** 2).sum() == 0: continue
    c = (x * y).sum() / np.sqrt((x ** 2).sum() * (y ** 2).sum())
    if best is None or c > best[0]: best = (c, lag)
c, lag = best
a0 = start + lag; n = min(len(ours), len(ref) - a0)
x, y = ours[:n], ref[a0:a0 + n]
print(f'global lag {lag} samples (tick0 at tap +{start}), NCC mono over {n/48000:.1f} s = {c:.4f}')
for ch, nm in ((0, 'L'), (1, 'R')):
    cc = (x[:, ch] * y[:, ch]).sum() / np.sqrt((x[:, ch] ** 2).sum() * (y[:, ch] ** 2).sum())
    print(f'  {nm}: NCC {cc:.4f}, rms ours {np.sqrt((x[:,ch]**2).mean()):.0f} pcsx2 {np.sqrt((y[:,ch]**2).mean()):.0f}, residual/ref {np.sqrt(((x[:,ch]-y[:,ch])**2).mean()/(y[:,ch]**2).mean()):.3f}')
print('sec  rms_ours rms_pcsx2  ncc')
for s in range(n // 48000):
    sl = slice(s * 48000, (s + 1) * 48000); xs, ys = x[sl].mean(1), y[sl].mean(1)
    den = np.sqrt((xs ** 2).sum() * (ys ** 2).sum())
    print(s, round(np.sqrt((x[sl] ** 2).mean())), round(np.sqrt((y[sl] ** 2).mean())), f'{(xs*ys).sum()/den:.3f}' if den else '-')
