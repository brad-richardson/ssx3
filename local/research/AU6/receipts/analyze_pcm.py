#!/usr/bin/env python3
"""Bounded 5 s loudness and 1 s local alignment checks for AU6."""
import json
from pathlib import Path
import wave
import numpy as np

ROOT = Path('/Users/brad/dev/ssx3-work/AU6')
RATE = 36000


def read(p):
    with wave.open(str(p), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (2, 2, RATE)
        return np.frombuffer(f.readframes(f.getnframes()), '<i2').reshape(-1, 2).copy()


def rms(x):
    x = x.astype(np.float64)
    return float(np.sqrt(np.mean(x*x)))


def profile(x):
    return [{'start_s': t, 'end_s': min(t+5, len(x)/RATE),
             'rms': round(rms(x[t*RATE:min((t+5)*RATE, len(x))]), 3)}
            for t in range(0, len(x)//RATE, 5)]


pc = read(ROOT/'compare/pcsx2-tag1-36k.wav')
our = read(ROOT/'run/tag1-36k.wav')
au5 = read(Path('/Users/brad/dev/ssx3-work/AU5/run/tag1-36k.wav'))
lag = 3922560
local = []
for t in range(0, len(our)//RATE):
    a = our[t*RATE:(t+1)*RATE].astype(np.float64)
    j = t*RATE+lag
    if j < 0 or j+RATE > len(pc):
        continue
    b = pc[j:j+RATE].astype(np.float64)
    num = float(np.sum((a-a.mean())*(b-b.mean())))
    den = float(np.sqrt(np.sum((a-a.mean())**2)*np.sum((b-b.mean())**2)))
    local.append({'our_s': t, 'pc_s': round(j/RATE, 3),
                  'ncc': round(num/den, 6) if den else None,
                  'our_rms': round(rms(a), 2), 'pc_rms': round(rms(b), 2)})
good = [v for v in local if v['ncc'] is not None and v['ncc'] >= 0.8]
spans = []
for v in good:
    if not spans or v['our_s'] != spans[-1][-1]['our_s'] + 1:
        spans.append([])
    spans[-1].append(v)
spans.sort(key=len, reverse=True)
out = {'profiles': {'pc': profile(pc), 'au6': profile(our), 'au5': profile(au5)},
       'local_alignment': local,
       'longest_ncc_ge_0_8': {'start_our_s': spans[0][0]['our_s'],
                             'end_our_s': spans[0][-1]['our_s']+1,
                             'start_pc_s': spans[0][0]['pc_s'],
                             'end_pc_s': spans[0][-1]['pc_s']+1,
                             'seconds': len(spans[0])} if spans else None}
(ROOT/'pcm-analysis.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({'longest': out['longest_ncc_ge_0_8'],
                  'au6_profile': out['profiles']['au6'],
                  'au5_profile': out['profiles']['au5']}, indent=2))
