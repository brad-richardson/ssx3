#!/usr/bin/env python3
"""T61 analyzer: value-filtered app/tpl, mode histogram, apc census, 0x1b0 hunt."""
import re, sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "t61-trace.txt"
APP = re.compile(r"^app vsync=(\d+) count=(\d+) t0=(0x[0-9a-f]+) tw0=(0x[0-9a-f]+) tw1=(0x[0-9a-f]+) tw2=(0x[0-9a-f]+) tw3=(0x[0-9a-f]+) tw4=(0x[0-9a-f]+) s4=(0x[0-9a-f]+) t1=(0x[0-9a-f]+) ra=(0x[0-9a-f]+)")
TPL = re.compile(r"^tpl vsync=(\d+) addr=(0x[0-9a-f]+) old=(0x[0-9a-f]+) new=(0x[0-9a-f]+) tw0=(0x[0-9a-f]+) tw1=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) (.*)")
SUM = re.compile(r"^appsum vsync=(\d+) n_app=(\d+) n_tpl=(\d+) mode_hist=(\S+)")
APC = re.compile(r"^apc vsync=(\d+)( pc=0x[0-9a-f]+:\d+(,pc=0x[0-9a-f]+:\d+)*)?$")
PC1 = re.compile(r"pc=(0x[0-9a-f]+):(\d+)")

app, tpl, ssum, apc = [], [], [], []
for ln in open(path, encoding="utf-8"):
    ln = ln.rstrip("\n")
    m = APP.match(ln)
    if m:
        app.append(tuple(m.groups()))
        continue
    m = TPL.match(ln)
    if m:
        tpl.append(m.groups())
        continue
    m = SUM.match(ln)
    if m:
        ssum.append(m.groups())
        continue
    m = APC.match(ln)
    if m:
        apc.append((m.group(1), m.group(2) or ""))
        continue

print("== row counts: app=%d tpl=%d appsum=%d apc=%d" % (len(app), len(tpl), len(ssum), len(apc)))

print("== app vsync span: %s..%s; tpl vsync span: %s..%s" % (
    app[0][0], app[-1][0], tpl[0][1 - 1] if False else tpl[0][0], tpl[-1][0]))
print("== app t0 distinct:", Counter(a[2] for a in app))
print("== app ra distinct:", Counter(a[10] for a in app))
print("== app tw0 distinct:", Counter(a[3] for a in app))
print("== app count distinct (%d): %s" % (len(set(a[1] for a in app)), sorted(set(a[1] for a in app), key=int)))
print("== app s4 distinct:", Counter(a[8] for a in app))

print("== tpl (addr,new,pc,ra) distinct:")
for k, c in Counter((t[1], t[3], t[6], t[7]) for t in tpl).most_common():
    print("   n=%d addr=%s new=%s pc=%s ra=%s" % (c, k[0], k[1], k[2], k[3]))
print("== tpl tw0-snapshot distinct:", Counter(t[4] for t in tpl))
print("== tpl tw1-snapshot distinct:", Counter(t[5] for t in tpl))

print("== 0x1b0 hunt (exact value in any app tw / tpl old,new,tw0,tw1):")
hits = []
for a in app:
    for i, w in enumerate(a[3:8]):
        if w == "0x1b0":
            hits.append(("app", a[0], i, w))
for t in tpl:
    for lab, w in (("old", t[2]), ("new", t[3]), ("tw0", t[4]), ("tw1", t[5])):
        if w == "0x1b0":
            hits.append(("tpl", t[0], lab, w))
print("   exact-0x1b0 hits:", hits if hits else "NONE")
print("== mode-6 (new&0x3C0==0x180) tpl rows:", sum(1 for t in tpl if (int(t[3], 16) & 0x3C0) == 0x180))
print("== app rows with tw0&0x180==0x180:", sum(1 for a in app if (int(a[3], 16) & 0x3C0) == 0x180))

print("== appsum: n_app total=%d n_tpl total=%d; hist union:" % (
    sum(int(s[1]) for s in ssum), sum(int(s[2]) for s in ssum)))
hu = Counter()
for s in ssum:
    if s[3] == "-":
        continue
    for kv in s[3].split(","):
        mm, cc = kv.split(":")
        hu[mm] += int(cc)
print("   hist union:", dict(sorted(hu.items(), key=lambda kv: int(kv[0]))))
print("== appsum first 5 / last 5:")
for s in ssum[:5] + ssum[-5:]:
    print("  ", s)

print("== apc: distinct pcs + totals:")
tot = Counter()
nempty = 0
for vs, rest in apc:
    pcs = PC1.findall(rest or "")
    if not pcs:
        nempty += 1
        continue
    for pc, c in pcs:
        tot[pc] += int(c)
print("   empty apc lines:", nempty)
for pc, c in tot.most_common():
    print("   pc=%s total=%d" % (pc, c))
print("== apc span: %s..%s" % (apc[0][0], apc[-1][0]))
print("== apc first 3 / last 3:")
for vs, rest in apc[:3] + apc[-3:]:
    print("   vsync=%s%s" % (vs, rest[:200]))
