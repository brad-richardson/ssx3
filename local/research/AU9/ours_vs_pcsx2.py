# AU9: our boot's guest-time mix (PS2X_SND_MIX_RAW: s16 music L/R, voices L/R per 48 kHz frame) vs PCSX2 taps.
# 1) menu: first voice onset in each capture, 2 s after onset, NCC over a +-2000 sample lag search (event alignment).
# 2) race: voice-layer statistics (RMS, share of energy < 1 kHz, L/R NCC, active share) for the race segment of each.
import numpy as np, sys
SR = 48000
mix = np.fromfile(sys.argv[1], dtype='<i2').reshape(-1, 4).astype(np.float64)
menu = np.fromfile(sys.argv[2], dtype='<i2').reshape(-1, 16).astype(np.float64)
race = np.fromfile(sys.argv[3], dtype='<i2').reshape(-1, 16).astype(np.float64)
race_from = int(sys.argv[4])  # our frame index where the race starts (from the boot's tick of race load)
ov = mix[:, 2:4]; pm = menu[:, 4:6] + menu[:, 6:8]
def onset(v): return int(np.where(np.abs(v).max(1) > 0)[0][0])
o1, o2 = onset(ov), onset(pm)
L = 2 * SR
a = ov[o1:o1 + L].mean(1)
best = max(((np.dot(a, pm[o2 + d:o2 + d + L].mean(1)) / np.sqrt(np.dot(a, a) * np.dot(pm[o2 + d:o2 + d + L].mean(1), pm[o2 + d:o2 + d + L].mean(1))), d) for d in range(-2000, 2001) if o2 + d >= 0), key=lambda x: x[0])
print(f'menu: our first voice onset at frame {o1} ({o1/SR:.2f} s guest), PCSX2 at tap window +{o2}; best NCC over 2 s = {best[0]:.4f} at lag {best[1]}')
for s in (0, 1):
    sl = slice(o1 + s * SR, o1 + (s + 1) * SR); sp = slice(o2 + best[1] + s * SR, o2 + best[1] + (s + 1) * SR)
    print(f'  second {s}: rms ours {np.sqrt((ov[sl]**2).mean(0)).round()} pcsx2 {np.sqrt((pm[sp]**2).mean(0)).round()}')
def stats(v, name):
    m = v.mean(1); f = np.abs(np.fft.rfft(m)) ** 2; fr = np.fft.rfftfreq(len(m), 1 / SR)
    act = (np.abs(v).max(1) > 0).mean()
    lr = np.dot(v[:, 0], v[:, 1]) / np.sqrt(np.dot(v[:, 0], v[:, 0]) * np.dot(v[:, 1], v[:, 1]))
    print(f'{name}: {len(v)/SR:.1f} s, voice rms L/R {np.sqrt((v**2).mean(0)).round()}, energy <1 kHz {f[fr < 1000].sum()/f.sum()*100:.1f}%, L/R NCC {lr:.3f}, nonzero share {act*100:.1f}%')
stats(mix[race_from:, 2:4], 'ours race voices')
stats(race[72701 + 459:, 4:6] + race[72701 + 459:, 6:8], 'pcsx2 race voices')
stats(mix[race_from:, 0:2], 'ours race music')
