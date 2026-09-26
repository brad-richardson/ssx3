#!/usr/bin/env python3
"""VR4: join CP1 R2b per-IP MTVU samples (iphist.txt) with an Odin block's
disassembly; print per-class sample shares and the hottest instructions."""
import re, sys, collections
hist_path, dis_path = sys.argv[1], sys.argv[2]
top = int(sys.argv[3]) if len(sys.argv) > 3 else 40
samples = collections.Counter()
for line in open(hist_path):
    parts = line.split()
    samples[int(parts[-2], 16)] += int(parts[-1])
insns = []
for line in open(dis_path):
    m = re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)', line)
    if m:
        insns.append((int(m.group(1), 16), m.group(2), m.group(3).strip()))
def cls(op, args):
    if op.startswith(('ldr', 'ldp', 'ldur', 'ld1', 'ldrb', 'ldrh', 'ldrs')): return 'load'
    if op.startswith(('str', 'stp', 'stur', 'st1')): return 'store'
    if op.startswith(('b.', 'cb', 'tb', 'b', 'ret', 'br', 'bl')) and op not in ('bic', 'bics', 'bfi', 'bfxil', 'bif', 'bit', 'bsl'): return 'branch'
    if op.startswith('f') or (args.startswith(('d', 's', 'v', 'q')) and op in ('mov', 'fmov', 'ins', 'dup', 'movi', 'and', 'orr')): return 'fp/simd'
    if op in ('csel', 'csinc', 'cset', 'csetm', 'cinc', 'ccmp', 'cmp', 'cmn', 'tst', 'ccmn'): return 'cmp/sel'
    return 'int'
tot = sum(samples[a] for a, _, _ in insns)
by = collections.Counter(); stat = collections.Counter()
for a, op, args in insns:
    c = cls(op, args); by[c] += samples[a]; stat[c] += 1
print(f'{dis_path}: {len(insns)} insns, samples {tot/1e6:.1f} ms total')
for c in sorted(stat, key=lambda c: -by[c]):
    print(f'  {c:8s} static {stat[c]:5d} ({100*stat[c]/len(insns):4.1f}%)  samples {100*by[c]/max(tot,1):5.1f}%')
ranked = sorted(insns, key=lambda t: -samples[t[0]])[:top]
print(f'top {top} instructions (sample ms, % of block):')
for a, op, args in ranked:
    print(f'  {a:x} {samples[a]/1e6:6.2f} {100*samples[a]/tot:5.2f}%  {op} {args}')
