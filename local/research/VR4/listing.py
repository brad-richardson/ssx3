#!/usr/bin/env python3
"""VR4: interleaved listing: addr, samples(ms), insn, innermost fn:line < caller."""
import json, re, sys, collections
hist_path, dis_path, sym_path, lo, hi = sys.argv[1:6]
lo, hi = int(lo, 16), int(hi, 16)
samples = collections.Counter()
for line in open(hist_path):
    p = line.split(); samples[int(p[-2], 16)] += int(p[-1])
ops = {}
for line in open(dis_path):
    m = re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)', line)
    if m: ops[int(m.group(1), 16)] = (m.group(2), re.sub(r' <.*', '', m.group(3)))
for rec in map(json.loads, open(sym_path)):
    a = int(rec['Address'], 16)
    if not lo <= a < hi: continue
    ch = rec['Symbol']
    src = ' < '.join(f"{f['FunctionName'][:24]}:{f['Line']}" for f in ch[:3])
    op, args = ops[a]
    print(f'{a:x} {samples[a]/1e6:5.2f} {op:6s} {args[:34]:34s} {src}')
