#!/usr/bin/env python3
"""T55 analyze-3: vsync0-vs-vsync2 diff; the 16 pass-stable rows; ret drift."""
import re
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "/home/brad/pcsx2-t4/t55-trace.txt"
pat = re.compile(
    r"^h394 vsync=(\d+) tgt=(0x[0-9a-f]+) a0=(0x[0-9a-f]+) s1=(0x[0-9a-f]+) "
    r"w0=(0x[0-9a-f]+) w1=(0x[0-9a-f]+) w2=(0x[0-9a-f]+) w3=(0x[0-9a-f]+) "
    r"hash=(0x[0-9a-f]+) ret=(0x[0-9a-f]+) stores=([01])$")
vs = {}
for line in open(path):
    m = pat.match(line.strip())
    if m:
        vs.setdefault(int(m.group(1)), []).append(m.groups())

r0, r2 = vs[0], vs[2]
print("vsync0 == vsync2 full-row multiset: %s" % (Counter(r0) == Counter(r2)))
c0, c2 = Counter(r0), Counter(r2)
print("only-in-0: %d only-in-2: %d" % (sum((c0 - c2).values()), sum((c2 - c0).values())))
for r in sorted((c0 - c2).elements())[:12]:
    print("  0-only: s1=%s w0=%s w1=%s w2=%s w3=%s hash=%s ret=%s stores=%s" % r[3:])
for r in sorted((c2 - c0).elements())[:12]:
    print("  2-only: s1=%s w0=%s w1=%s w2=%s w3=%s hash=%s ret=%s stores=%s" % r[3:])
# pass-1 only comparison
p0, p2 = r0[:112], r2[:112]
print("pass1 multiset equal 0-vs-2: %s" % (Counter(p0) == Counter(p2)))
# the 16 pass-stable rows in vsync 0
stable = [a for a, b in zip(r0[:112], r0[112:]) if a == b]
print("pass-stable rows: %d" % len(stable))
for r in stable:
    print("  s1=%s w0=%s w1=%s w2=%s w3=%s hash=%s ret=%s stores=%s" % r[3:])
# ret drift for the dominant bucket hash=0xd0 across vsyncs 0..5
print("hash=0xd0 rets by vsync:")
for v in range(6):
    print("  vsync %d: %s" % (v, sorted(set(r[9] for r in vs[v] if r[8] == "0xd0"))))
print("T55_ANALYZE3_DONE")
