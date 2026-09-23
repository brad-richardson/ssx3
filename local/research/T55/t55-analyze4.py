#!/usr/bin/env python3
"""T55 analyze-4: vsync-field-stripped parity classes, stores per vsync, pass-2 stores."""
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
        g = m.groups()
        vs.setdefault(int(g[0]), []).append(g[1:])  # strip vsync field

full = sorted(v for v in vs if len(vs[v]) == 224)
print("full vsyncs: %d (0..%d)" % (len(full), max(full)))
sigs = {}
for v in full:
    sigs.setdefault(tuple(vs[v]), []).append(v)
print("stripped parity classes: %d" % len(sigs))
for sig, members in sorted(sigs.items(), key=lambda kv: kv[1][0]):
    print("  n=%d vsyncs=%s" % (len(members), members))
# stores=1 per vsync (full ones) + pass split on vsync 0
for v in full[:6]:
    print("vsync %d stores=1 total=%d" % (v, sum(1 for r in vs[v] if r[9] == "1")))
r0 = vs[0]
print("vsync0 pass1 stores=1: %d pass2 stores=1: %d" % (
    sum(1 for r in r0[:112] if r[9] == "1"), sum(1 for r in r0[112:] if r[9] == "1")))
# pass-1 row multiset equality across even vsyncs / odd vsyncs
evens = [v for v in full if v % 2 == 0]
odds = [v for v in full if v % 2 == 1]
print("pass1 multiset all-evens-equal: %s" % all(Counter(vs[v][:112]) == Counter(vs[evens[0]][:112]) for v in evens))
print("pass1 multiset all-odds-equal: %s" % all(Counter(vs[v][:112]) == Counter(vs[odds[0]][:112]) for v in odds))
print("pass2 multiset all-evens-equal: %s" % all(Counter(vs[v][112:]) == Counter(vs[evens[0]][112:]) for v in evens))
# even-vs-odd pass1 diff sample
c0, c1 = Counter(vs[0][:112]), Counter(vs[1][:112])
print("pass1 rows only-even-multiset: %d only-odd: %d" % (sum((c0 - c1).values()), sum((c1 - c0).values())))
for r in sorted((c0 - c1).elements())[:6]:
    print("  even: s1=%s w3=%s hash=%s ret=%s" % (r[2], r[6], r[7], r[8]))
for r in sorted((c1 - c0).elements())[:6]:
    print("  odd:  s1=%s w3=%s hash=%s ret=%s" % (r[2], r[6], r[7], r[8]))
print("T55_ANALYZE4_DONE")
