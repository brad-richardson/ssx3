#!/usr/bin/env python3
"""T51 analyze: per-vsync sequence table over the 5-vsync window.

Usage: t51-analyze.py <trace> [winstart]
Reads the extracted trace (st/sema/semaid/irq/gsreg/dmareg + markers),
prints: window check, per-vsync event sequence (state-word writes highlighted),
distinct-value tables. Exits 0; prints gaps plainly.
"""
import re
import sys
from collections import Counter

trace = open(sys.argv[1], encoding="utf-8").read().splitlines()
winstart = int(sys.argv[2]) if len(sys.argv) > 2 else None

st_re = re.compile(r"^st vsync=(\d+) addr=(0x[0-9a-f]+) value=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) intc=([01])$")
sema_re = re.compile(r"^sema vsync=(\d+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) call=(\w+) id=(\d+) m=(\+0x\w+)$")
semaid_re = re.compile(r"^semaid vsync=(\d+) w28=(0x[0-9a-f]+) w2c=(0x[0-9a-f]+) w4c=(0x[0-9a-f]+)$")
irq_re = re.compile(r"^irq vsync=(\d+) cause=(0x[0-9a-f]+) ch=((?:intc|dmac):\d+) handler=(0x[0-9a-f]+)$")
gs_re = re.compile(r"^gsreg vsync=(\d+) reg=(\w+)$")
dm_re = re.compile(r"^dmareg vsync=(\d+) reg=(D1_\w+) value=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+)")

INTC = {0: "GS", 1: "SBUS", 2: "VBLANK_S", 3: "VBLANK_E", 4: "VIF0", 5: "VIF1",
        6: "VU0", 7: "VU1", 8: "IPU", 9: "TIM0", 10: "TIM1", 11: "TIM2",
        12: "TIM3", 13: "SFIFO", 14: "VU0WD"}
DMAC = {0: "VIF0", 1: "VIF1", 2: "GIF", 3: "fromIPU", 4: "toIPU", 5: "SIF0",
        6: "SIF1", 7: "SIF2", 8: "fromSPR", 9: "toSPR"}

evs = []  # (vsync, order, text)
for i, ln in enumerate(trace):
    m = st_re.match(ln)
    if m:
        v, a, val, pc, ra, it = m.groups()
        evs.append((int(v), i, "st addr=%s value=%s pc=%s ra=%s intc=%s" % (a, val, pc, ra, it)))
        continue
    m = sema_re.match(ln)
    if m:
        v, pc, ra, call, sid, mm = m.groups()
        evs.append((int(v), i, "sema call=%s id=%s m=%s pc=%s ra=%s" % (call, sid, mm, pc, ra)))
        continue
    m = semaid_re.match(ln)
    if m:
        v, w28, w2c, w4c = m.groups()
        evs.append((int(v), i, "semaid w28=%s w2c=%s w4c=%s" % (w28, w2c, w4c)))
        continue
    m = irq_re.match(ln)
    if m:
        v, cause, ch, hdl = m.groups()
        src, n = ch.split(":")
        n = int(n)
        nm = (INTC if src == "intc" else DMAC).get(n, "?")
        evs.append((int(v), i, "irq %s=%s(%d) cause=%s handler=%s" % (src, nm, n, cause, hdl)))
        continue
    m = gs_re.match(ln)
    if m:
        v, reg = m.groups()
        evs.append((int(v), i, "gsreg %s" % reg))
        continue
    m = dm_re.match(ln)
    if m:
        v, reg, val, pc, ra = m.groups()
        evs.append((int(v), i, "dmareg %s=%s pc=%s ra=%s" % (reg, val, pc, ra)))
        continue

if winstart is None:
    w = [int(x.split("vsync=")[1]) for x in trace if x.startswith("T51_WINDOW tu=ee")]
    winstart = w[0] if w else None
print("winstart(ee)=%s" % winstart)
if winstart is not None:
    win = [v for v in range(winstart, winstart + 5)]
    have = sorted(set(v for v, _, _ in evs if winstart <= v <= winstart + 4))
    print("window=%s have=%s missing=%s" % (win, have, [v for v in win if v not in have]))
    w_all = [int(x.split("vsync=")[1]) for x in trace if x.startswith("T51_WINDOW")]
    print("T51_WINDOW lines: %s" % [x for x in trace if x.startswith("T51_WINDOW")])
    print("CAP lines: %s" % [x for x in trace if "_CAP" in x])
    print()
    print("=== per-vsync sequence (st to 0x62152c=state first) ===")
    for v in win:
        print("--- vsync %d ---" % v)
        for vv, _, t in sorted(evs):
            if vv == v:
                print("  %s" % t)

print()
print("=== state-word (0x62152c) writes ===")
n_state = 0
for v, _, t in sorted(evs):
    if t.startswith("st addr=0x62152c "):
        print("  vsync=%d %s" % (v, t))
        n_state += 1
print("n_state=%d" % n_state)
print()
print("=== st addr histogram ===")
c = Counter(t.split()[1] for _, _, t in evs if t.startswith("st addr="))
for k in sorted(c):
    print("  %s x%d" % (k, c[k]))
print()
print("=== sema call histogram ===")
c = Counter((t.split()[1], t.split()[2]) for _, _, t in evs if t.startswith("sema call="))
for k in sorted(c):
    print("  %s %s x%d" % (k[0], k[1], c[k]))
print()
print("=== irq histogram ===")
c = Counter(t.split()[1] for _, _, t in evs if t.startswith("irq "))
for k in sorted(c):
    print("  %s x%d" % (k, c[k]))
print()
print("=== dmareg histogram ===")
c = Counter((t.split()[1],) for _, _, t in evs if t.startswith("dmareg"))
for k in sorted(c):
    print("  %s x%d" % (k[0], c[k]))
print()
print("=== gsreg histogram ===")
c = Counter(t for _, _, t in evs if t.startswith("gsreg"))
for k in sorted(c):
    print("  %s x%d" % (k, c[k]))
print("T51_ANALYZE_DONE n_events=%d" % len(evs))
