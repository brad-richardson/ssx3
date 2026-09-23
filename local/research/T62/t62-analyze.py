#!/usr/bin/env python3
"""T62 analyzer: appx item-0 writers, v1b0 producers, appsum ax validation."""
import re, sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "t62-trace.txt"
K = int(sys.argv[2]) if len(sys.argv) > 2 else 960  # K-down vsync
APPX = re.compile(r"^appx vsync=(\d+) site=(0x[0-9a-f]+) count=(\d+) t0=(0x[0-9a-f]+) tw0=(0x[0-9a-f]+) tw1=(0x[0-9a-f]+) tw2=(0x[0-9a-f]+) tw3=(0x[0-9a-f]+) tw4=(0x[0-9a-f]+) ra=(0x[0-9a-f]+)")
AXF = re.compile(r"^axfirst vsync=(\d+) site=(0x[0-9a-f]+) v1=(\d+) t0=(0x[0-9a-f]+) tw0=(0x[0-9a-f]+) tw1=(0x[0-9a-f]+) tw2=(0x[0-9a-f]+) s0=(0x[0-9a-f]+) a0=(0x[0-9a-f]+) ra=(0x[0-9a-f]+)")
V1B0 = re.compile(r"^v1b0 vsync=(\d+) addr=(0x[0-9a-f]+) vaddr=(0x[0-9a-f]+) value=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) (.*)")
SUM = re.compile(r"^appsum vsync=(\d+) n_app=(\d+) n_tpl=(\d+) mode_hist=(\S+) ax=(\d+),(\d+),(\d+)")

appx, axf, v1b0, ssum = [], [], [], []
for ln in open(path, encoding="utf-8"):
    ln = ln.rstrip("\n")
    m = APPX.match(ln)
    if m:
        appx.append(m.groups())
        continue
    m = AXF.match(ln)
    if m:
        axf.append(m.groups())
        continue
    m = V1B0.match(ln)
    if m:
        v1b0.append(m.groups())
        continue
    m = SUM.match(ln)
    if m:
        ssum.append(m.groups())
        continue
print("rows: appx=%d axfirst=%d v1b0=%d appsum=%d" % (len(appx), len(axf), len(v1b0), len(ssum)))

print("== appx per site: n, vsync span, count min/max, t0 set, tw0 set ==")
for s in ("0x3797ec", "0x37ad44", "0x37b474"):
    r = [a for a in appx if a[1] == s]
    if not r:
        print("  site %s: NONE" % s)
        continue
    print("  site %s: n=%d vsync %s..%s count %s..%s t0=%s tw0=%s" % (
        s, len(r), r[0][0], r[-1][0],
        min(int(a[2]) for a in r), max(int(a[2]) for a in r),
        set(a[3] for a in r), set(a[4] for a in r)))
print("== appx mode-6 rows (all):")
m6 = [a for a in appx if ((int(a[4], 16) >> 6) & 0xF) == 6]
print("  n=%d" % len(m6))
for a in m6[:12]:
    print("   vsync=%s(K%+d) site=%s count=%s t0=%s tw0=%s tw1=%s ra=%s" % (
        a[0], int(a[0]) - K, a[1], a[2], a[3], a[4], a[5], a[9]))
print("== appx count<=1 rows: n=%d; per site first:" % sum(1 for a in appx if int(a[2]) <= 1))
for s in ("0x3797ec", "0x37ad44", "0x37b474"):
    r = [a for a in appx if a[1] == s and int(a[2]) <= 1]
    for a in r[:4]:
        print("   vsync=%s(K%+d) site=%s count=%s t0=%s tw0=%s ra=%s" % (
            a[0], int(a[0]) - K, a[1], a[2], a[3], a[4], a[9]))

print("== v1b0: n=%d span %s..%s" % (len(v1b0), v1b0[0][0], v1b0[-1][0]))
print("== v1b0 first 12 (K-relative):")
for b in v1b0[:12]:
    print("   vsync=%s(K%+d) addr=%s value=%s pc=%s ra=%s" % (
        b[0], int(b[0]) - K, b[1], b[3], b[4], b[5]))
print("== v1b0 per-pc totals:")
for pc, c in Counter(b[4] for b in v1b0).most_common(15):
    print("   pc=%s n=%d" % (pc, c))
print("== v1b0 value distinct:", Counter(b[3] for b in v1b0).most_common(10))
print("== v1b0 template-target rows (addr in [t0,t0+20) of 0x61c910/0x61c8fc):")
t = [b for b in v1b0 if (0x61c910 <= int(b[1], 16) < 0x61c924) or (0x61c8fc <= int(b[1], 16) < 0x61c910)]
print("  n=%d" % len(t))
for b in t[:10]:
    print("   vsync=%s(K%+d) addr=%s value=%s pc=%s ra=%s" % (
        b[0], int(b[0]) - K, b[1], b[3], b[4], b[5]))

print("== appsum ax validation: lines where n_app != ax0+ax1+ax2:")
bad = [s for s in ssum if int(s[1]) != int(s[4]) + int(s[5]) + int(s[6])]
print("  bad=%d of %d" % (len(bad), len(ssum)))
for s in bad[:5]:
    print("   ", s)
print("== appsum ax totals: ax0=%d ax1=%d ax2=%d n_app=%d" % (
    sum(int(s[4]) for s in ssum), sum(int(s[5]) for s in ssum),
    sum(int(s[6]) for s in ssum), sum(int(s[1]) for s in ssum)))
print("== appsum nonzero-ax lines (first 8 / last 4):")
nz = [s for s in ssum if (int(s[4]), int(s[5]), int(s[6])) != (0, 0, 0)]
for s in nz[:8] + nz[-4:]:
    print("   vsync=%s(K%+d) n_app=%s hist=%s ax=%s,%s,%s" % (
        s[0], int(s[0]) - K, s[1], s[3], s[4], s[5], s[6]))
print("  nonzero-ax lines: %d" % len(nz))
