#!/usr/bin/env python3
"""T63 analyzer: template-array histories, 0x1b0 bound, value sources."""
import re, sys
from collections import Counter

TW = re.compile(r"^tw vsync=(\d+) addr=(0x[0-9a-f]+) vaddr=(0x[0-9a-f]+) old=(0x[0-9a-f]+) new=(0x[0-9a-f]+) via=([A-Za-z0-9-]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) (.*)")
BASE = re.compile(r"^twbase vsync=(\d+) addr=(0x[0-9a-f]+) value=(0x[0-9a-f]+)")
T0 = 0x61c8fc


def load(path):
    tw, base = [], []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        m = TW.match(ln)
        if m:
            tw.append(m.groups())
            continue
        m = BASE.match(ln)
        if m:
            base.append(m.groups())
    return tw, base


def tmpl(addr):
    return (int(addr, 16) - T0) // 0x14


def word(addr):
    return ((int(addr, 16) - T0) % 0x14) // 4


for path in sys.argv[1:]:
    tw, base = load(path)
    print("===== %s: tw=%d base=%d span=%s..%s" % (
        path, len(tw), len(base), tw[0][0] if tw else "-", tw[-1][0] if tw else "-"))
    print("  base:", [(b[1], b[2]) for b in base])
    print("  per-template:", Counter(tmpl(t[1]) for t in tw))
    print("  via:", Counter(t[5] for t in tw))
    print("  top (pc,via):", Counter((t[6], t[5]) for t in tw).most_common(10))
    w0 = [t for t in tw if t[1] == "0x61c910"]
    print("  t2w0 rows: %d %s" % (len(w0), ("values=" + str(set(t[4] for t in w0))) if w0 else "(virgin)"))
    if w0:
        print("    first:", w0[0][:7])
        print("    last:", w0[-1][:7])
    b0 = [t for t in tw if t[4] == "0x1b0"]
    print("  new=0x1b0 rows (any addr): %d" % len(b0))
    for t in b0[:5]:
        print("   ", t[:8])
    t2 = [t for t in tw if tmpl(t[1]) == 1]
    print("  template-2 all: %d rows addrs=%s" % (len(t2), sorted(set(t[1] for t in t2))))
    for t in t2[:8]:
        print("   ", t[:7])
