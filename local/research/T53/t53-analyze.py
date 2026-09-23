#!/usr/bin/env python3
"""T53 analyze: folded ADDR-word watch over the SC-settled statefile boot.

Usage: t53-analyze.py <trace>
- ARMED/CAP lines.
- Per watched address: hit count, distinct values, per (value, pc, ra) groups
  with n + first vsync + full register image of the first hit.
- Distinct storing pcs overall.
"""
import re
import sys
from collections import Counter, defaultdict

trace = open(sys.argv[1], encoding="utf-8").read().splitlines()

print("ARMED: %s" % [x for x in trace if "T53W_ARMED" in x])
print("CAP: %s" % [x for x in trace if "T53W_CAP" in x])
print("WINDOW: %s" % [x for x in trace if "T51C_WINDOW" in x])

WATCH = ["0x63d434", "0x63dcb4", "0x70a0b4", "0x70a934",
         "0x63c654", "0x63c8a4", "0x63cb64", "0x63cdf4"]

hits = [ln for ln in trace if ln.startswith("tagaddrwrite ")]
print("n_tagaddrwrite=%d" % len(hits))

by_addr = defaultdict(list)
for ln in hits:
    m = re.match(r"^tagaddrwrite vsync=(\d+) addr=(0x[0-9a-f]+) value=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+)(.*)$", ln)
    assert m, "grammar reject: %r" % ln
    vs, addr, val, pc, ra, regs = m.groups()
    tm = re.search(r" tu=(ri|swc1|sqc2)$", regs)
    tu = tm.group(1) if tm else "-"
    by_addr[addr].append((int(vs), val, pc, ra, tu, regs.strip()))

for addr in WATCH:
    hh = by_addr.get(addr, [])
    print()
    print("=== addr %s: n=%d ===" % (addr, len(hh)))
    if not hh:
        continue
    print("  values: %s" % sorted(set(v for _, v, _, _, _, _ in hh)))
    print("  vsync range: %d..%d" % (min(v for v, _, _, _, _, _ in hh), max(v for v, _, _, _, _, _ in hh)))
    print("  tu: %s" % sorted(set(t for _, _, _, _, t, _ in hh)))
    groups = Counter((v, p, r, t) for _, v, p, r, t, _ in hh)
    for (v, p, r, t) in sorted(groups):
        first = min(vs for vs, vv, pp, rr, tt, _ in hh if (vv, pp, rr, tt) == (v, p, r, t))
        print("  value=%s pc=%s ra=%s tu=%s x%d first_vsync=%d" % (v, p, r, t, groups[(v, p, r, t)], first))
    # full register image of the first hit of the top group
    top = sorted(groups, key=lambda k: -groups[k])[0]
    firstline = min((h for h in hh if (h[1], h[2], h[3], h[4]) == top), key=lambda h: h[0])
    print("  first regs: vsync=%d %s" % (firstline[0], firstline[5]))

other = sorted(set(a for a in by_addr if a not in WATCH))
print()
print("off-watch addrs (must be []): %s" % other)
print("distinct storing pcs: %s" % sorted(set(p for hh in by_addr.values() for _, _, p, _, _, _ in hh)))
print("T53_ANALYZE_DONE")
