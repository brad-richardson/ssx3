#!/usr/bin/env python3
"""E36 trace analyzer: per-startPC census + detail summary.

Usage: python3 local/research/E36/e36_analyze.py <vu1-trace-file>

Prints:
  1. census table per startPC (count, cycles min/max, total xgkick)
  2. one summary per detail block (MSCAL snapshot, header words,
     hist top-5, branch line, body op sequence)
"""
import re
import sys
from collections import Counter

path = sys.argv[1]
text = open(path).read().splitlines()

census = Counter()
cyc = {}
xg = {}
details = []
cur = None
for line in text:
    m = re.match(r"census vsync=(\d+) startPC=(0x[0-9a-f]+) cycles=(\d+) xgkick=(\d+)", line)
    if m:
        vs, pc, cy, xk = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))
        census[pc] += 1
        cyc.setdefault(pc, []).append(cy)
        xg[pc] = xg.get(pc, 0) + xk
        continue
    m = re.match(r"detail startPC=(0x[0-9a-f]+)(.*)", line)
    if m:
        cur = {"startPC": m.group(1), "head": m.group(2).strip(), "lines": []}
        details.append(cur)
        continue
    if cur is not None and re.match(r"(topq|itopq|vi|hist|taken|branch|body|entry) ", line):
        cur["lines"].append(line)

print("== census per startPC ==")
print(f"{'startPC':>10} {'n':>6} {'cyc_min':>8} {'cyc_max':>8} {'xgkick':>7}")
for pc, n in census.most_common():
    cs = cyc[pc]
    print(f"{pc:>10} {n:>6} {min(cs):>8} {max(cs):>8} {xg[pc]:>7}")
print(f"total exhausted programs: {sum(census.values())}, distinct startPCs: {len(census)}")

print()
print("== detail blocks ==")
for d in details:
    print(f"--- {d['startPC']} {d['head']}")
    for line in d["lines"]:
        if line.startswith("body "):
            m = re.match(r"body (0x[0-9a-f]+) lo=(0x[0-9a-f]+) up=(0x[0-9a-f]+)(.*?) (.*?) \| (.*)", line)
            if m:
                print(f"    {m.group(1)}: {m.group(5)} | {m.group(6)} [{m.group(4).strip() or 'noflag'}]")
            else:
                print(f"    {line}")
        elif line.startswith("topq") or line.startswith("itopq"):
            w = line.split()[1:]
            nz = [(i, x) for i, x in enumerate(w) if x != "00000000"]
            print(f"    {line.split()[0]} nonzero words: {len(nz)}/32" +
                  (f" e.g. {nz[:8]}" if nz else " (all zero)"))
        else:
            print(f"    {line}")
