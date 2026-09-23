#!/usr/bin/env python3
"""T54 analyze: walker census by mode + mode-6 records + producer watch.

Usage: t54-analyze.py <trace>
- drec: per (vsync, mode) counts; per-mode totals; vsync coverage.
- drecs: first-8 records/mode/vsync; mode-6 distinct addrs + words + mode-bit check.
- dprod: per watched addr hits grouped by (value, pc, ra, tu) + first-hit regs.
"""
import re
import sys
from collections import Counter, defaultdict

trace = open(sys.argv[1], encoding="utf-8").read().splitlines()

print("ARMED: %s" % [x for x in trace if "T54W_ARMED" in x])
print("CAP: %s" % [x for x in trace if "T54W_CAP" in x])
print("WINDOW: %s" % [x for x in trace if "T51C_WINDOW" in x])

drec = [ln for ln in trace if re.match(r"^drec vsync=", ln)]
drecs = [ln for ln in trace if ln.startswith("drecs ")]
dprod = [ln for ln in trace if ln.startswith("dprod ")]
print("n_drec=%d n_drecs=%d n_dprod=%d" % (len(drec), len(drecs), len(dprod)))

# --- drec: counts per (vsync, mode) ---
counts = defaultdict(dict)  # vs -> {mode: count}
for ln in drec:
    m = re.match(r"^drec vsync=(\d+) mode=(\d+) count=(\d+)$", ln)
    assert m, "grammar reject: %r" % ln
    vs, mode, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
    assert mode not in counts[vs], "dup drec: %r" % ln
    counts[vs][mode] = c

vss = sorted(counts)
print("drec vsyncs: n=%d range=%s" % (len(vss), ("%d..%d" % (vss[0], vss[-1]) if vss else "-")))
tot = Counter()
for vs in vss:
    for mode, c in counts[vs].items():
        tot[mode] += c
print("per-mode totals (drec): %s" % sorted(tot.items()))
print("modes ever seen: %s" % sorted(tot))
if vss:
    print("first 3 vsync rows:")
    for vs in vss[:3]:
        print("  vsync=%d %s total=%d" % (vs, sorted(counts[vs].items()), sum(counts[vs].values())))
    print("last 3 vsync rows:")
    for vs in vss[-3:]:
        print("  vsync=%d %s total=%d" % (vs, sorted(counts[vs].items()), sum(counts[vs].values())))

# --- drecs: records ---
recs = defaultdict(list)  # mode -> [(vs, addr, w0..w3)]
for ln in drecs:
    m = re.match(r"^drecs vsync=(\d+) mode=(\d+) addr=(0x[0-9a-f]+) w0=(0x[0-9a-f]+) w1=(0x[0-9a-f]+) w2=(0x[0-9a-f]+) w3=(0x[0-9a-f]+)$", ln)
    assert m, "grammar reject: %r" % ln
    vs, mode = int(m.group(1)), int(m.group(2))
    recs[mode].append((vs,) + m.groups()[2:])
print("drecs modes: %s" % sorted((m, len(v)) for m, v in recs.items()))
for mode in sorted(recs):
    hh = recs[mode]
    addrs = sorted(set(h[1] for h in hh))
    print("mode=%d addrs(n=%d): %s" % (mode, len(addrs), addrs[:16]))
    bad = 0
    for (vs, addr, w0, w1, w2, w3) in hh[:8]:
        mb = (int(w0, 16) & 0x3C0) >> 6
        flag = "" if mb == mode else "  MODEBIT_MISMATCH(bit=%d)" % mb
        if mb != mode:
            bad += 1
        print("  vsync=%d addr=%s w0=%s w1=%s w2=%s w3=%s%s" % (vs, addr, w0, w1, w2, w3, flag))
    if bad:
        print("  modebit mismatches in first-8 sample: %d" % bad)

# --- dprod: producer hits ---
by_addr = defaultdict(list)
for ln in dprod:
    m = re.match(r"^dprod vsync=(\d+) addr=(0x[0-9a-f]+) value=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+)(.*)$", ln)
    assert m, "grammar reject: %r" % ln
    vs, addr, val, pc, ra, regs = m.groups()
    tm = re.search(r" tu=(ri|swc1|sqc2)$", regs)
    tu = tm.group(1) if tm else "-"
    by_addr[addr].append((int(vs), val, pc, ra, tu, regs.strip()))
print("dprod addrs: %s" % sorted((a, len(v)) for a, v in by_addr.items()))
for addr in sorted(by_addr):
    hh = by_addr[addr]
    print()
    print("=== dprod addr %s: n=%d ===" % (addr, len(hh)))
    print("  values: %s" % sorted(set(v for _, v, _, _, _, _ in hh)))
    print("  vsync range: %d..%d" % (min(v for v, _, _, _, _, _ in hh), max(v for v, _, _, _, _, _ in hh)))
    print("  tu: %s" % sorted(set(t for _, _, _, _, t, _ in hh)))
    groups = Counter((v, p, r, t) for _, v, p, r, t, _ in hh)
    for (v, p, r, t) in sorted(groups):
        first = min(vs for vs, vv, pp, rr, tt, _ in hh if (vv, pp, rr, tt) == (v, p, r, t))
        print("  value=%s pc=%s ra=%s tu=%s x%d first_vsync=%d" % (v, p, r, t, groups[(v, p, r, t)], first))
    top = sorted(groups, key=lambda k: -groups[k])[0]
    firstline = min((h for h in hh if (h[1], h[2], h[3], h[4]) == top), key=lambda h: h[0])
    print("  first regs: vsync=%d %s" % (firstline[0], firstline[5]))
print("distinct dprod pcs: %s" % sorted(set(p for hh in by_addr.values() for _, _, p, _, _, _ in hh)))
print("T54_ANALYZE_DONE")
