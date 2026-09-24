#!/usr/bin/env python3
"""AU4: validate/de-dup SND tag-1 records, align menu PCM, and compare 36 kHz mixes.

Inputs are AU2's raw 0x620-byte records and AU4's [u32 EE vsync][0x620 bytes]
records. Outputs (WAV, PNG, CSV, JSON) go only to the supplied work directory.
"""
import argparse
import csv
import hashlib
import json
import struct
import wave
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

RATE = 36000
FRAMES = 384
PAYLOAD = 0x620


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def records(path, prefixed, csv_path, wav_path):
    stride = PAYLOAD + (4 if prefixed else 0)
    raw = np.fromfile(path, dtype=np.uint8)
    if raw.size % stride:
        raise ValueError(f'{path}: trailing {raw.size % stride} bytes')
    rows = raw.reshape(-1, stride)
    p = 4 if prefixed else 0
    tag1 = rows[:, p:p + 4].copy().view('<u4').ravel()
    length = rows[:, p + 4:p + 8].copy().view('<u4').ravel()
    zero1 = rows[:, p + 8:p + 12].copy().view('<u4').ravel()
    zero2 = rows[:, p + 12:p + 16].copy().view('<u4').ravel()
    tag5 = rows[:, p + 0x610:p + 0x614].copy().view('<u4').ravel()
    serial = rows[:, p + 0x614:p + 0x618].copy().view('<u4').ravel()
    valid = (tag1 == 1) & (length == 0x600) & (zero1 == 0) & (zero2 == 0) & (tag5 == 5)
    if not valid.all():
        raise ValueError(f'{path}: {(~valid).sum()} bad layouts; first bad index {np.flatnonzero(~valid)[0]}')
    vsync = rows[:, 0:4].copy().view('<u4').ravel() if prefixed else None
    order = np.argsort(serial, kind='stable')
    _, unique_at = np.unique(serial[order], return_index=True)
    keep = order[unique_at]
    serial = serial[keep]
    vsync = vsync[keep] if vsync is not None else None
    pcm = rows[keep, p + 0x10:p + 0x610].copy().view('<i2').reshape(-1, FRAMES, 2)
    gaps = np.diff(serial.astype(np.int64))
    with wave.open(str(wav_path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(['record_index', 'serial', 'ee_vsync', 'min', 'max', 'rms', 'nonzero_samples', 'zero_crossings'])
        for i in range(min(100, len(pcm))):
            q = pcm[i].astype(np.float64)
            crossings = int(np.sum((q[1:] * q[:-1]) < 0))
            writer.writerow([i, int(serial[i]), int(vsync[i]) if vsync is not None else '', int(q.min()), int(q.max()),
                             round(float(np.sqrt(np.mean(q * q))), 3), int(np.count_nonzero(q)), crossings])
    return pcm.reshape(-1, 2), {
        'raw_records': int(len(rows)), 'unique_records': int(len(keep)), 'duplicates': int(len(rows) - len(keep)),
        'first_serial': int(serial[0]), 'last_serial': int(serial[-1]),
        'serial_gaps': int(np.sum(gaps != 1)), 'record_seconds': float(len(keep) * FRAMES / RATE),
        'first_vsync': int(vsync[0]) if vsync is not None else None,
        'last_vsync': int(vsync[-1]) if vsync is not None else None,
        'wav_sha256': sha(wav_path),
    }


def read_wav(path):
    with wave.open(str(path), 'rb') as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (2, 2, RATE):
            raise ValueError(f'{path}: expected stereo s16 36000 Hz')
        return np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2).copy()


def coarse_align(ref, target, target_limit_s=330):
    # Match several 5-second music excerpts. Each candidate is normalized over
    # its local target energy; decimation is common to both streams.
    f = 18
    p = signal.resample_poly(target[:int(target_limit_s * RATE)].astype(np.float64).mean(axis=1), 1, f)
    best = None
    for t in (5, 10, 15, 20, 25):
        r0 = int(t * RATE); r1 = int((t + 5) * RATE)
        if r1 > len(ref):
            continue
        q = signal.resample_poly(ref[r0:r1].astype(np.float64).mean(axis=1), 1, f)
        q -= q.mean()
        qenergy = float(np.dot(q, q))
        if qenergy < 1:
            continue
        c = signal.fftconvolve(p, q[::-1], mode='valid')
        cs = np.concatenate(([0.0], np.cumsum(p * p)))
        sm = np.concatenate(([0.0], np.cumsum(p)))
        pe = (cs[len(q):] - cs[:-len(q)]) - (sm[len(q):] - sm[:-len(q)])**2 / len(q)
        valid = pe > len(q) * 100**2  # Ignore silent/near-silent target windows.
        ncc = np.zeros_like(c)
        ncc[valid] = c[valid] / np.sqrt(pe[valid] * qenergy)
        i = int(np.argmax(np.abs(ncc)))
        item = {'template_start_au2_s': t, 'target_template_start_s': i * f / RATE,
                'lag_s': i * f / RATE - t, 'correlation': float(ncc[i])}
        if best is None or abs(item['correlation']) > abs(best['correlation']):
            best = item
    return best


def refine_align(ref, target, coarse):
    t = coarse['template_start_au2_s']
    ref0 = int((t + 1) * RATE)
    q = ref[ref0:ref0 + RATE].astype(np.float64).mean(axis=1)
    q -= q.mean()
    approx = int((t + 1 + coarse['lag_s']) * RATE)
    lo = max(0, approx - RATE)
    hi = min(len(target), approx + 2 * RATE)
    p = target[lo:hi].astype(np.float64).mean(axis=1)
    c = signal.fftconvolve(p, q[::-1], mode='valid')
    cs = np.concatenate(([0.0], np.cumsum(p * p)))
    sm = np.concatenate(([0.0], np.cumsum(p)))
    pe = (cs[len(q):] - cs[:-len(q)]) - (sm[len(q):] - sm[:-len(q)])**2 / len(q)
    valid = pe > len(q) * 100**2
    ncc = np.zeros_like(c)
    ncc[valid] = c[valid] / np.sqrt(pe[valid] * np.dot(q, q))
    i = int(np.argmax(np.abs(ncc)))
    target0 = lo + i
    return {'lag_frames': target0 - ref0, 'lag_s': (target0 - ref0) / RATE,
            'correlation': float(ncc[i]), 'reference_template_start_s': (t + 1),
            'target_template_start_s': target0 / RATE}


def local_stats(x, offset_frames=0):
    a = x.astype(np.float64)
    delta = np.abs(np.diff(a, axis=0))
    seam = (np.arange(1, len(a)) + offset_frames) % FRAMES == 0
    seam_ratio = float(delta[seam].mean() / delta[~seam].mean()) if seam.any() and delta[~seam].mean() else None
    zc = int(np.sum((a[1:] * a[:-1]) < 0))
    return {'seam_ratio': seam_ratio, 'zero_crossings_per_second_both_channels': zc / (len(a) / RATE),
            'rms': float(np.sqrt(np.mean(a * a))), 'peak_abs': int(np.max(np.abs(a)))}


def bands(d, ref):
    result = {}
    n = len(d)
    df = np.fft.rfftfreq(n, 1 / RATE)
    result_array = []
    for ch in range(2):
        result_array.append((np.fft.rfft(d[:, ch].astype(np.float64)), np.fft.rfft(ref[:, ch].astype(np.float64))))
    for low, high in ((0, 2000), (2000, 6000), (6000, 12000), (12000, 18000)):
        sel = (df >= low) & (df < high if high < 18000 else df <= high)
        # Parseval: one-sided bins interior count twice.
        weight = np.ones(np.count_nonzero(sel)); weight[(df[sel] != 0) & (df[sel] != RATE / 2)] = 2
        de = sum(float(np.sum(np.abs(a[sel])**2 * weight)) for a, _ in result_array) / (n*n*2)
        re = sum(float(np.sum(np.abs(b[sel])**2 * weight)) for _, b in result_array) / (n*n*2)
        result[f'{low}-{high}Hz'] = {'diff_rms': de**0.5, 'signal_rms': re**0.5,
                                    'diff_over_signal': (de/re)**0.5 if re else None}
    return result


def comparison(ref, target, lag_frames, duration_s=30):
    # AU2 menu starts ~3 s and changes to the race track at ~43 s.
    r0 = 5 * RATE
    t0 = r0 + lag_frames
    n = min(int(duration_s * RATE), len(ref) - r0, len(target) - t0)
    if t0 < 0 or n < 5 * RATE:
        raise ValueError('Insufficient aligned menu overlap')
    a = ref[r0:r0+n].astype(np.float64)
    b = target[t0:t0+n].astype(np.float64)
    d = a - b
    ar = np.sqrt(np.mean(a*a)); br = np.sqrt(np.mean(b*b))
    return {'au2_start_s': r0 / RATE, 'target_start_s': t0 / RATE, 'duration_s': n / RATE,
            'bit_exact_stereo_frames_pct': float(100 * np.mean(np.all(a == b, axis=1))),
            'gain_rms_au2_over_target': float(ar/br) if br else None,
            'gain_least_squares_au2_on_target': float(np.sum(a*b)/np.sum(b*b)) if np.sum(b*b) else None,
            'diff_rms_over_target_rms': float(np.sqrt(np.mean(d*d))/br) if br else None,
            'au2_stats': local_stats(a, r0), 'target_stats': local_stats(b, t0),
            'difference_bands': bands(d, b)}


def spectrogram_pair(ref, target, start_ref, start_target, out, title):
    n = 30 * RATE
    a = ref[start_ref:start_ref+n].astype(np.float32).mean(axis=1) / 32768
    b = target[start_target:start_target+n].astype(np.float32).mean(axis=1) / 32768
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True, constrained_layout=True)
    for ax, x, label in zip(axes, (a, b), ('AU2 au2b', 'PCSX2')):
        f, t, z = signal.stft(x, RATE, nperseg=1024, noverlap=768)
        db = 20 * np.log10(np.maximum(np.abs(z), 1e-6))
        im = ax.pcolormesh(t, f / 1000, db, cmap='magma', vmin=-95, vmax=-20, shading='auto')
        ax.set_ylim(0, 18); ax.set_ylabel(f'{label}\nkHz')
    axes[-1].set_xlabel('Seconds from selected menu excerpt')
    fig.colorbar(im, ax=axes, label='dBFS')
    fig.suptitle(title)
    fig.savefig(out, dpi=115)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcsx2-bin', required=True, type=Path)
    ap.add_argument('--au2-bin', required=True, type=Path)
    ap.add_argument('--au2-wav', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--pc-sc-record', type=int, default=0)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    pc, pcm = records(args.pcsx2_bin, True, args.out/'pcsx2-first100.csv', args.out/'pcsx2-tag1-36k.wav')
    au, aum = records(args.au2_bin, False, args.out/'au2-first100.csv', args.out/'au2-from-records-36k.wav')
    aum['matches_existing_wav'] = np.array_equal(au, read_wav(args.au2_wav))
    coarse = coarse_align(au, pc)
    refined = refine_align(au, pc, coarse) if coarse else None
    result = {'pcsx2': pcm, 'au2': aum, 'coarse_alignment': coarse, 'refined_alignment': refined}
    if refined and abs(refined['correlation']) >= 0.5:
        result['comparison'] = comparison(au, pc, refined['lag_frames'])
        r0 = 5 * RATE; t0 = r0 + refined['lag_frames']
        spectrogram_pair(au, pc, r0, t0, args.out/'menu-spectrogram-pair.png',
                         f'Menu audio aligned at lag {refined["lag_s"]:.3f} s')
        result['status'] = 'aligned'
    else:
        # Stop-rule evidence: equal-scale spectrograms, but no pairwise error table.
        r0 = 5 * RATE
        t0 = min(args.pc_sc_record * FRAMES, max(0, len(pc) - 30 * RATE))
        spectrogram_pair(au, pc, r0, t0, args.out/'menu-spectrogram-pair.png',
                         'Unaligned menu excerpts (AU2 5 s; PCSX2 SC marker)')
        result['status'] = 'stop: menu correlation below 0.5'
    (args.out/'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
