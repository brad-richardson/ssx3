#!/usr/bin/env python3
"""T56 analyze: who writes the 8 watched scratchpad words.

Tables: per-word hits/vsync-range/vias/values/pcs; DMA src addrs;
per-(addr,via,pc) writer census; settled-window (CWINDOW..PATHS) focus.
"""
import re
import sys
from collections import Counter, defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "/home/brad/pcsx2-t4/t56-trace.txt"
REGS = ("a0=([0-9a-f]+) a1=([0-9a-f]+) a2=([0-9a-f]+) a3=([0-9a-f]+) "
        "v0=([0-9a-f]+) v1=([0-9a-f]+) "
        "t0=([0-9a-f]+) t1=([0-9a-f]+) t2=([0-9a-f]+) t3=([0-9a-f]+) "
        "t4=([0-9a-f]+) t5=([0-9a-f]+) t6=([0-9a-f]+) t7=([0-9a-f]+) "
        "t8=([0-9a-f]+) t9=([0-9a-f]+) "
        "s0=([0-9a-f]+) s1=([0-9a-f]+) s2=([0-9a-f]+) s3=([0-9a-f]+) "
        "s4=([0-9a-f]+) s5=([0-9a-f]+) s6=([0-9a-f]+) s7=([0-9a-f]+)")
pat = re.compile(
    r"^spw vsync=(\d+) addr=(0x[0-9a-f]+) value=(0x[0-9a-f]+) via=([a-z0-9-]+)"
    r"( src=(0x[0-9a-f]+))? pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) " + REGS + r"$")
rows = []
windows = []
caps = []
armed = []
for line in open(path):
    line = line.strip()
    m = pat.match(line)
    if m:
        rows.append(m.groups())
        continue
    if line.startswith("T51C_WINDOW"):
        windows.append(int(line.split("=")[1]))
    elif line.startswith("T56_CAP"):
        caps.append(line)
    elif line.startswith("T56W_ARMED"):
        armed.append(line)

print("rows=%d windows=%s caps=%d armed=%s" % (len(rows), windows[:2], len(caps), armed))
if not rows:
    print("NO_ROWS")
    print("T56_ANALYZE_DONE")
    sys.exit(0)
print("vsync range: %s..%s n_vsyncs=%d" % (
    min(r[0] for r in rows), max(r[0] for r in rows), len(set(r[0] for r in rows))))
print("via distribution: %s" % Counter(r[3] for r in rows).most_common())
print("addr distribution: %s" % Counter(r[1] for r in rows).most_common())
print("src (DMA) distribution: %s" % Counter(r[5] for r in rows if r[5]).most_common(20))
print("pc distribution: %s" % Counter(r[6] for r in rows).most_common(20))
print("ra distribution: %s" % Counter(r[7] for r in rows).most_common(10))

by_addr = defaultdict(list)
for r in rows:
    by_addr[r[1]].append(r)
for addr in sorted(by_addr, key=lambda a: int(a, 16)):
    rs = by_addr[addr]
    vss = sorted(set(int(r[0]) for r in rs))
    print("=== %s n=%d vsyncs %d..%d (n=%d) vias=%s" % (
        addr, len(rs), vss[0], vss[-1], len(vss),
        Counter(r[3] for r in rs).most_common()))
    print("  values: %s" % Counter(r[2] for r in rs).most_common(10))
    print("  (via,pc,src): %s" % Counter((r[3], r[6], r[5]) for r in rs).most_common(12))
    # first + last hit full regs (a0..a3,s0..s7 brief fields)
    f, l = rs[0], rs[-1]
    print("  first: vsync=%s value=%s via=%s src=%s pc=%s ra=%s a0=%s a1=%s a2=%s a3=%s s1=%s s6=%s s7=%s" % (
        f[0], f[2], f[3], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[25], f[30], f[31]))
    print("  last:  vsync=%s value=%s via=%s src=%s pc=%s ra=%s a0=%s a1=%s a2=%s a3=%s s1=%s s6=%s s7=%s" % (
        l[0], l[2], l[3], l[5], l[6], l[7], l[8], l[9], l[10], l[11], l[25], l[30], l[31]))
print("T56_ANALYZE_DONE")
