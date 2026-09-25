#!/usr/bin/env python3
"""RD1: summarize a PS2X_RD1_TRACE log for an xgk ordinal range.

For each MSCAL whose program emits xgk ordinals in [lo, hi]: startPC, TOP, and the UNPACKs
since the previous MSCAL (fmt, num, addr, usn, mask, cl/wl, mode/men, zero-word fraction).
Usage: rd1_trace.py <trace> <lo> <hi> [--max 6]
"""
import sys, re, argparse
from collections import Counter

def parse(path):
    ev = []
    for l in open(path, errors='replace'):
        l = l.rstrip('\n')
        if l.startswith('vumem'):
            continue
        ev.append(l)
    return ev

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('trace'); ap.add_argument('lo', type=int); ap.add_argument('hi', type=int)
    ap.add_argument('--max', type=int, default=6)
    ap.add_argument('--census', action='store_true', help='only per-format census over the range')
    a = ap.parse_args()
    ev = parse(a.trace)
    # group: segments between MSCALs; attach xgks after an MSCAL to it
    segs = []
    cur = dict(mscal=None, pre=[], xgk=[])
    pending = []
    for l in ev:
        if l.startswith('vif ') or l.startswith('dma ') or l.startswith('dlv '):
            pending.append(l)
        elif l.startswith('mscal '):
            segs.append(cur)
            cur = dict(mscal=l, pre=pending, xgk=[])
            pending = []
        elif l.startswith('xgk '):
            cur['xgk'].append(int(l.split()[1]))
    segs.append(cur)
    sel = [s for s in segs if s['xgk'] and any(a.lo <= x <= a.hi for x in s['xgk'])]
    print('segments with xgk in range:', len(sel))
    pcs = Counter(re.search(r'pc=(\S+)', s['mscal']).group(1) for s in sel if s['mscal'])
    print('startPCs:', dict(pcs))
    fc = Counter()
    for s in sel:
        for l in s['pre']:
            if l.startswith('vif UNPACK'):
                m = re.search(r'num=(\d+) addr=(\S+) fmt=(\S+) usn=(\S) mask=(\S+) cl=(\d+) wl=(\d+) data=(.*?)( \+more=\d+)? mode=(\d) men=(\d)', l)
                num, addr, fmt, usn, mask, cl, wl, data, _, mode, men = m.groups()
                words = data.split()
                z = sum(1 for w in words if w == '00000000')
                fc[(fmt, usn, mask if men == '1' else '-', cl + 'x' + wl, mode)] += 1
    print('UNPACK census (fmt, usn, mask-if-enabled, cl x wl, mode):')
    for k, n in fc.most_common():
        print('  ', k, n)
    if a.census:
        return
    for s in sel[:a.max]:
        print('----', s['mscal'], 'xgk', s['xgk'])
        for l in s['pre']:
            if l.startswith('vif UNPACK'):
                m = re.search(r'num=(\d+) addr=(\S+) fmt=(\S+) usn=(\S) mask=(\S+) cl=(\d+) wl=(\d+) data=(.*?)( \+more=\d+)? mode=(\d) men=(\d)', l)
                num, addr, fmt, usn, mask, cl, wl, data, _, mode, men = m.groups()
                words = data.split()
                z = sum(1 for w in words if w == '00000000')
                print('   UNPACK %-6s num=%-3s addr=%-10s usn=%s men=%s mask=%s %sx%s words=%d zero=%d first=%s' % (
                    fmt, num, addr, usn, men, mask, cl, wl, len(words), z, ' '.join(words[:8])))
            elif l.startswith('dma '):
                print('  ', l)
            elif l.startswith('vif ') and not l.startswith('vif NOP'):
                print('  ', l[:160])

if __name__ == '__main__':
    main()
