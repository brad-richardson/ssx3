#!/usr/bin/env python3
"""T50 analyzer: mpgpay/dmareg/srcread tables for the E40 diff."""
import re
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "t50c-trace.txt"
mpg = []   # (vsync, num, raw, masked, mode, tag)
dm = []    # (vsync, reg, value, pc, ra)
src = []
caps = []
for line in open(path, encoding="utf-8"):
    line = line.strip()
    m = re.match(r"^mpgpay vsync=(\d+) imm=0 num=(\d+) src=0x([0-9a-f]+)&0x([0-9a-f]+) mode=(\S+) tag_at=(\S+)", line)
    if m:
        mpg.append((int(m.group(1)), int(m.group(2)), int(m.group(3), 16), int(m.group(4), 16), m.group(5), m.group(6)))
        continue
    m = re.match(r"^dmareg vsync=(\d+) reg=(\S+) value=0x([0-9a-f]+) pc=0x([0-9a-f]+) ra=0x([0-9a-f]+)", line)
    if m:
        dm.append((int(m.group(1)), m.group(2), int(m.group(3), 16), int(m.group(4), 16), int(m.group(5), 16)))
        continue
    m = re.match(r"^srcread ", line)
    if m:
        src.append(line)
        continue
    m = re.match(r"^(T50_\w+)", line)
    if m:
        caps.append(line)
        continue
    print("UNPARSED: " + line[:120])

print("== totals: mpgpay=%d dmareg=%d srcread=%d caps=%d" % (len(mpg), len(dm), len(src), len(caps)))
for c in caps:
    print("  " + c)
if mpg:
    vs = [x[0] for x in mpg]
    print("== mpgpay vsync span: %d..%d  distinct=%d" % (min(vs), max(vs), len(set(vs))))
    print("== mpgpay num: %s" % Counter(x[1] for x in mpg))
    print("== mpgpay mode: %s" % Counter(x[4] for x in mpg))
    print("== mpgpay distinct masked src (all):")
    for v, n in Counter(x[3] for x in mpg).most_common():
        print("   0x%08x x%d" % (v, n))
    print("== mpgpay distinct tag_at (top 20):")
    for v, n in Counter(x[5] for x in mpg).most_common(20):
        print("   %s x%d" % (v, n))
    print("== mpgpay distinct (src,tag_at) (top 20):")
    for v, n in Counter((x[3], x[5]) for x in mpg).most_common(20):
        print("   src=0x%08x tag=%s x%d" % (v[0], v[1], n))
    print("== mpgpay per-vsync (first 8 + last 4):")
    c = Counter(x[0] for x in mpg)
    ks = sorted(c)
    for k in ks[:8] + ks[-4:]:
        print("   vsync=%d x%d" % (k, c[k]))
if dm:
    vs = [x[0] for x in dm]
    print("== dmareg vsync span: %d..%d distinct=%d" % (min(vs), max(vs), len(set(vs))))
    print("== dmareg per-reg distinct values:")
    regs = {}
    for _, r, v, pc, ra in dm:
        regs.setdefault(r, []).append((v, pc, ra))
    for r in sorted(regs):
        vals = Counter(v for v, _, _ in regs[r])
        pcs = Counter((v, pc) for v, pc, _ in regs[r])
        print("   %s n=%d distinct_values=%d:" % (r, len(regs[r]), len(vals)))
        for v, n in vals.most_common(12):
            print("     value=0x%x x%d" % (v, n))
        print("     (value,pc) top 8:")
        for (v, pc), n in pcs.most_common(8):
            print("       value=0x%x pc=0x%x x%d" % (v, pc, n))
    print("== dmareg distinct ra (top 8):")
    for v, n in Counter(x[4] for x in dm).most_common(8):
        print("   ra=0x%x x%d" % (v, n))
print("== T50_ANALYZE_DONE")
