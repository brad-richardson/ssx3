#!/usr/bin/env python3
"""Find writer/reader pieces of an intra-tick hazard on the Odin.
Stream: SRC records up to marker END; tick END-1 GIF packets split at EOP; a marker after piece j iff j in set.
Fixes iff some marker j with w <= j < r."""
import os, struct, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from gsstream import records
from mkstream import eop_pieces, rec_bytes, marker
SRC, END, GOOD = sys.argv[1], int(sys.argv[2]), sys.argv[3]
F = '/storage/emulated/0/Android/data/com.ps2x.runner/files'
W = '/Users/brad/dev/ssx3-work/N8X1'
prefix, pieces = bytearray(b'PS2XGSC1'), []
tail = []
for off, k, t, rec in records(SRC, END):
    if k == 4 and t == END: break
    if t == END - 1 and k == 1:
        size = struct.unpack_from('<I', rec, 10)[0]
        for pc in eop_pieces(rec[14:14 + size]):
            pieces.append(rec_bytes(rec[:10] + struct.pack('<I', len(pc)) + pc))
    elif t == END - 1 and pieces:
        pieces.append(rec_bytes(rec))  # priv etc after first piece: keep order as its own "piece"
    else:
        prefix += rec_bytes(rec)
N = len(pieces); print('pieces', N, flush=True)
def run(label, S):
    path = f'{W}/streams/hb-{label}.gs'
    with open(path, 'wb') as o:
        o.write(prefix)
        for j, pc in enumerate(pieces):
            o.write(pc)
            if j in S: o.write(marker(END))
        o.write(marker(END))
    subprocess.run(['adb', '-s', '622c49b1', 'push', path, f'{F}/n8x1-hb.gs'], capture_output=True, check=True)
    subprocess.run([f'{W}/tools/run_odin.sh', f'hb-{label}', f'{F}/n8x1-hb.gs'], capture_output=True, env=dict(os.environ, PPM_TICKS='0'))
    last = open(f'{W}/runs/odin-hb-{label}/parallel.hashes').read().split('\n')[-2]
    ok = GOOD in last
    print(f'{label} markers={len(S)} ok={ok} {last}', flush=True)
    os.remove(path)
    return ok
if run('none', set()): print('no hazard without markers?'); sys.exit()
assert run('all', set(range(N)))
lo, hi = 0, N  # smallest k with prefix {0..k-1} ok
while lo < hi:
    m = (lo + hi) // 2
    if run(f'pre{m}', set(range(m))): hi = m
    else: lo = m + 1
w = lo - 1
lo, hi = 0, N  # largest k with suffix {k..N-1} ok
while lo < hi:
    m = (lo + hi + 1) // 2
    if run(f'suf{m}', set(range(m, N))): lo = m
    else: hi = m - 1
r = lo + 1
print(f'RESULT writer piece w={w} reader piece r={r} (marker in [w, r) fixes)')
assert run(f'single{w}', {w}) or True
with open(f'{W}/hazard-{END}.txt', 'w') as f: f.write(f'{w} {r}\n')
