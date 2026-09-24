#!/usr/bin/env python3
"""N5: bucket rollup of a simpleperf `--sort comm,symbol` self report."""
import re, sys
B = [('VU1 interpreter', r'VU1Interpreter::'),
     ('GS CPU rasterizer / GS memory', r'GSCpuBackend::|GSMem::|combineTexture|__func<unsigned int \(\*\)\(unsigned char\*|__func<void \(\*\)\(unsigned char\*|GS::|GifArbiter|GSTex'),
     ('Guest code (sub_*)', r'\bsub_[0-9A-Fa-f]{8}'),
     ('PLT stubs', r'@plt'),
     ('libc / kernel / vdso', r'__mem|clock_gettime|__kernel|\[kernel|pthread|futex|scudo|malloc|free\b|memcpy|memset'),
     ('VIF/DMA/memory/scheduler', r'PS2Memory::|VIF|EeScheduler|PS2Runtime::'),
     ('Present/upload (GL)', r'adreno|gl[A-Z]|egl|raylib|rl[A-Z]')]
tot = {}; rows = 0; covered = 0.0
for line in open(sys.argv[1]):
    m = re.match(r'\s*([\d.]+)%\s+(\S+)\s+(.*)', line)
    if not m: continue
    p, sym = float(m.group(1)), m.group(3); rows += 1; covered += p
    for name, rx in B:
        if re.search(rx, sym):
            tot[name] = tot.get(name, 0) + p; break
    else:
        tot['other'] = tot.get('other', 0) + p
print(f'rows={rows} covered={covered:.2f}% (rows >= 0.05%)')
print('| Bucket | Self % |\n|---|---|')
for k, v in sorted(tot.items(), key=lambda x: -x[1]): print(f'| {k} | {v:.2f}% |')
