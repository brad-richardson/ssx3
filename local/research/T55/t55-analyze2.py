#!/usr/bin/env python3
"""T55 analyze-2: two-pass structure, parity classes, mode-6 item rows."""
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

full = sorted(vs)
print("full vsyncs (224 calls): %s" % [v for v in full if len(vs[v]) == 224])
print("partial: %s" % [(v, len(vs[v])) for v in full if len(vs[v]) != 224])

# two-pass check on vsync 0
r0 = vs[0]
s1s = [r[3] for r in r0]
print("vsync0: n=%d distinct_s1=%d" % (len(r0), len(set(s1s))))
print("vsync0 first-s1=%s last-s1=%s" % (s1s[0], s1s[-1]))
p1, p2 = r0[:112], r0[112:]
print("pass1 s1 set == pass2 s1 set: %s" % (set(x[3] for x in p1) == set(x[3] for x in p2)))
print("pass1 s1 order == pass2 s1 order: %s" % ([x[3] for x in p1] == [x[3] for x in p2]))
d = sum(1 for a, b in zip(p1, p2) if a != b)
print("rows differing pass1-vs-pass2: %d/112" % d)
for a, b in zip(p1, p2):
    if a != b:
        print("  DIFF s1=%s p1[w3,hash,ret,stores]=%s,%s,%s,%s p2=%s,%s,%s,%s" % (
            a[3], a[7], a[8], a[9], a[10], b[7], b[8], b[9], b[10]))
        break

# parity classes over full vsyncs
sigs = {}
for v in full:
    if len(vs[v]) != 224:
        continue
    sig = tuple(vs[v])
    sigs.setdefault(sig, []).append(v)
print("parity classes (n_classes=%d):" % len(sigs))
for sig, members in sorted(sigs.items(), key=lambda kv: kv[1]):
    print("  vsyncs=%s n=%d" % (members[:8], len(members)))

# mode-6 items (w0==0x1b0): per parity class
for sig, members in sorted(sigs.items(), key=lambda kv: kv[1]):
    print("== class vsyncs %s ==" % members[:4])
    for r in sig:
        if r[4] == "0x1b0":
            print("  s1=%s w1=%s w2=%s w3=%s hash=%s ret=%s stores=%s" % (
                r[3], r[5], r[6], r[7], r[8], r[9], r[10]))
    break
print("T55_ANALYZE2_DONE")
