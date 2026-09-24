#!/usr/bin/env python3
"""AU4 Part 3: track local menu PCM lag and measure lag-corrected residual."""
import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage, signal

from compare import RATE, read_wav, sha

WINDOW = 1800                 # 50 ms at 36 kHz
HOP = 900                     # 25 ms
SEARCH = 720                 # +/-20 ms
BANDS = ((0, 2000), (2000, 6000), (6000, 12000), (12000, 18000))


def local_peak(ref, target, ref_start, base_lag):
    """NCC over stereo, with a parabolic three-point peak refinement."""
    q = ref[ref_start:ref_start + WINDOW].astype(np.float64)
    q -= q.mean(axis=0)
    lo = ref_start + base_lag - SEARCH
    p = target[lo:lo + WINDOW + 2 * SEARCH].astype(np.float64)
    dot = sum(signal.fftconvolve(p[:, ch], q[::-1, ch], mode='valid') for ch in range(2))
    sq = np.concatenate((np.zeros((1, 2)), np.cumsum(p * p, axis=0)))
    sm = np.concatenate((np.zeros((1, 2)), np.cumsum(p, axis=0)))
    en = ((sq[WINDOW:] - sq[:-WINDOW]) - (sm[WINDOW:] - sm[:-WINDOW])**2 / WINDOW).sum(axis=1)
    den = np.sqrt(np.maximum(en, 0) * np.sum(q * q))
    ncc = np.divide(dot, den, out=np.zeros_like(dot), where=den > 0)
    i = int(np.argmax(ncc))
    frac = 0.0
    if 0 < i < len(ncc) - 1:
        left, mid, right = ncc[i-1:i+2]
        denom = left - 2 * mid + right
        if denom != 0:
            frac = float(np.clip(0.5 * (left - right) / denom, -0.5, 0.5))
    return i - SEARCH + frac, float(ncc[i])


def residual_bands(ref, target, starts, lag_frames, base_lag):
    # Equal 50-ms windows give identical FFT bins in each measurement. Their
    # summed energies form an overlap-weighted RMS; no gain fitting is applied.
    freq = np.fft.rfftfreq(WINDOW, 1 / RATE)
    weight = np.full(len(freq), 2.0)
    weight[0] = 1.0
    weight[-1] = 1.0
    corrected = np.zeros((len(BANDS), 2), dtype=np.float64)
    fixed = np.zeros((len(BANDS), 2), dtype=np.float64)
    whole = np.zeros((2, 2), dtype=np.float64)
    sample_axis = np.arange(WINDOW, dtype=np.float64)
    for start, lag in zip(starts, lag_frames):
        a = ref[start:start + WINDOW].astype(np.float64)
        b0 = target[start + base_lag:start + base_lag + WINDOW].astype(np.float64)
        # Cubic spline interpolation avoids rounding the sub-sample lag to an
        # integer; the same target is used as the denominator for each ratio.
        pos = start + base_lag + lag + sample_axis
        lo = max(0, int(np.floor(pos[0])) - 4)
        hi = min(len(target), int(np.ceil(pos[-1])) + 5)
        b = np.stack([ndimage.map_coordinates(target[lo:hi, ch].astype(np.float64),
                                               [pos-lo], order=3,
                                               mode='nearest', prefilter=True)
                      for ch in range(2)], axis=1)
        for col, sig in enumerate((a-b, b)):
            whole[0, col] += np.sum(sig*sig)
        for col, sig in enumerate((a-b0, b0)):
            whole[1, col] += np.sum(sig*sig)
        spec = [np.fft.rfft(x, axis=0) for x in (a-b, b, a-b0, b0)]
        for k, (low, high) in enumerate(BANDS):
            sel = (freq >= low) & (freq < high if high < RATE/2 else freq <= high)
            corrected[k] += [np.sum(abs(spec[j][sel])**2 * weight[sel, None])
                             for j in (0, 1)]
            fixed[k] += [np.sum(abs(spec[j][sel])**2 * weight[sel, None])
                         for j in (2, 3)]
    norm = len(starts) * WINDOW * WINDOW * 2
    out = {}
    for k, (low, high) in enumerate(BANDS):
        out[f'{low}-{high}Hz'] = {
            'fixed_diff_over_pcsx2': float(np.sqrt(fixed[k, 0] / fixed[k, 1])),
            'corrected_diff_over_pcsx2': float(np.sqrt(corrected[k, 0] / corrected[k, 1])),
            'corrected_diff_rms': float(np.sqrt(corrected[k, 0] / norm)),
            'corrected_pcsx2_rms': float(np.sqrt(corrected[k, 1] / norm)),
        }
    return out, {'fixed': float(np.sqrt(whole[1, 0] / whole[1, 1])),
                 'corrected': float(np.sqrt(whole[0, 0] / whole[0, 1]))}


def run(ref_path, target_path, out, start_s, end_s, base_lag):
    ref = read_wav(ref_path)
    target = read_wav(target_path)
    starts = np.arange(round(start_s * RATE), round(end_s * RATE) - WINDOW + 1, HOP)
    if len(starts) == 0 or starts[-1] + base_lag + WINDOW + SEARCH > len(target):
        raise ValueError('Insufficient aligned menu overlap')
    lags = []
    corr = []
    for start in starts:
        lag, c = local_peak(ref, target, int(start), base_lag)
        lags.append(lag)
        corr.append(c)
    lags = np.array(lags)
    corr = np.array(corr)
    times = (starts + WINDOW/2) / RATE
    good = corr >= .8
    band, whole = residual_bands(ref, target, starts[good], lags[good], base_lag)
    all_band, all_whole = residual_bands(ref, target, starts, lags, base_lag)
    # A step needs both a >=1-sample shift and persistence across two adjacent
    # half-second bins. Only bins with >=10 reliable windows count.
    edges = np.arange(start_s, end_s + .5, .5)
    med = np.array([np.median(lags[(times >= x) & (times < x+.5) & good])
                    if np.sum((times >= x) & (times < x+.5) & good) >= 10 else np.nan
                    for x in edges[:-1]])
    jumps = []
    for k in range(1, len(med)-1):
        if np.all(np.isfinite(med[k-1:k+2])) and abs(med[k]-med[k-1]) >= 1 \
                and abs(med[k+1]-med[k-1]) >= 1:
            jumps.append({'au2_time_s': float(edges[k]),
                          'size_frames': float(med[k]-med[k-1]),
                          'size_ms': float((med[k]-med[k-1])*1000/RATE)})
    out.mkdir(parents=True, exist_ok=True)
    with (out/'lag-windows.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(('au2_center_s', 'lag_from_base_frames', 'lag_from_base_ms', 'ncc'))
        w.writerows(zip(times, lags, lags*1000/RATE, corr))
    fig, (ax, zoom) = plt.subplots(2, 1, figsize=(12, 6), sharex=True,
                                   constrained_layout=True)
    ax.scatter(times[~good], lags[~good] * 1000/RATE, s=4, color='0.6',
               label='NCC < 0.8')
    ax.scatter(times[good], lags[good] * 1000/RATE, s=4, color='tab:blue',
               label='NCC >= 0.8')
    ax.set(ylabel='Lag offset (ms)', title=f'50 ms windows / 25 ms hop; search ±20 ms; {len(lags)} windows')
    ax.legend(loc='upper right')
    zoom.scatter(times[good], lags[good] * 1000/RATE, s=4, color='tab:blue')
    zoom.axhline(np.median(lags[good]) * 1000/RATE, color='tab:orange', linewidth=1)
    zoom.set(xlabel='AU2 menu time (s)', ylabel='Reliable lag offset (ms)', ylim=(-.25, .25))
    fig.savefig(out/'menu-lag-vs-time.png', dpi=150)
    plt.close(fig)
    result = {
        'input_sha256': {'au2': sha(ref_path), 'target': sha(target_path)},
        'method': {'rate_hz': RATE, 'window_ms': 50, 'hop_ms': 25, 'search_ms': 20,
                   'base_lag_frames': base_lag, 'base_lag_s': base_lag/RATE,
                   'lag_peak': 'stereo normalized cross-correlation; 3-point parabolic interpolation',
                   'residual': 'per-window cubic-spline fractional lag; no gain fitting; overlap-weighted FFT energy'},
        'span': {'au2_start_s': start_s, 'au2_end_s': end_s,
                 'target_start_s': start_s + base_lag/RATE,
                 'target_end_s': end_s + base_lag/RATE, 'windows': len(lags)},
        'lag': {'median_ms_from_base': float(np.median(lags[good])*1000/RATE),
                'p05_ms_from_base': float(np.percentile(lags[good], 5)*1000/RATE),
                'p95_ms_from_base': float(np.percentile(lags[good], 95)*1000/RATE),
                'min_ms_from_base': float(np.min(lags[good])*1000/RATE),
                'max_ms_from_base': float(np.max(lags[good])*1000/RATE),
                'median_ncc_all': float(np.median(corr)),
                'median_ncc_reliable': float(np.median(corr[good])),
                'reliable_windows': int(np.sum(good)),
                'unreliable_windows': int(np.sum(~good)),
                'jump_rule': '>=1 sample in adjacent 0.5-s bin medians, persistent in next bin; >=10 NCC>=0.8 windows/bin',
                'jumps': jumps},
        'reliable_windows': {'whole_diff_over_pcsx2': whole, 'bands': band},
        'all_windows': {'whole_diff_over_pcsx2': all_whole, 'bands': all_band},
    }
    (out/'lag-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--au2', type=Path, required=True)
    ap.add_argument('--target', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--start', type=float, default=8.75)
    ap.add_argument('--end', type=float, default=41)
    ap.add_argument('--base-lag-frames', type=int, default=3998216)
    args = ap.parse_args()
    run(args.au2, args.target, args.out, args.start, args.end, args.base_lag_frames)
