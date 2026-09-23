#!/usr/bin/env python3
"""T51c analyze: chain-tag dump (capture A) + tagaddrwrite (capture B).

Usage: t51c-analyze.py <trace>
- ctag table: per-tag lines, id histogram, CALL targets (0x435bd0 vs 0x434990),
  per-chain structure (group by contiguous tag_at runs), END count (= kicks).
- Prints the /tmp/t51-watch candidate list: tag_at+4 of every CALL tag with
  addr == 0x434990 (deduped, sorted).
- dmareg/st/sema/irq summaries as context.
"""
import re
import sys
from collections import Counter

trace = open(sys.argv[1], encoding="utf-8").read().splitlines()

ctag_re = re.compile(r"^ctag tag_at=(0x[0-9a-f]+) id=(\d+) qwc=(\d+) addr=(0x[0-9a-f]+) tte=([0-9a-f]{16})$")
dm_re = re.compile(r"^dmareg vsync=(\d+) reg=(D1_\w+) value=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+)")

ctags = []
for ln in trace:
    m = ctag_re.match(ln)
    if m:
        tag_at, iid, qwc, addr, tte = m.groups()
        ctags.append((tag_at, int(iid), int(qwc), addr, tte))

print("CWINDOW: %s" % [x for x in trace if "T51C_WINDOW" in x])
print("CCAP: %s" % [x for x in trace if "T51C_CAP" in x])
print("n_ctag=%d" % len(ctags))
print()
print("=== id histogram ===")
c = Counter(i for _, i, _, _, _ in ctags)
names = {0: "REFE", 1: "CNT", 2: "NEXT", 3: "REF", 4: "REFS", 5: "CALL", 6: "RET", 7: "END"}
for k in sorted(c):
    print("  id=%d %s x%d" % (k, names.get(k, "?"), c[k]))
print()
print("=== CALL targets ===")
calls = [(t, q, a) for t, i, q, a, _ in ctags if i == 5]
c2 = Counter(a for _, _, a in calls)
for k in sorted(c2):
    print("  addr=%s x%d" % (k, c2[k]))
print()
print("=== CALL -> 0x434990 sites (tag_at, qwc) ===")
sites = sorted(set((t, q) for t, q, a in calls if a == "0x434990"))
for t, q in sites:
    print("  tag_at=%s qwc=%d watch=%s" % (t, q, hex(int(t, 16) + 4)))
print("n_90_sites=%d" % len(sites))
print()
print("=== CALL -> 0x435bd0 sites (tag_at, qwc) ===")
sites0 = sorted(set((t, q) for t, q, a in calls if a == "0x435bd0"))
for t, q in sites0:
    print("  tag_at=%s qwc=%d" % (t, q))
print("n_b0_sites=%d" % len(sites0))
print()
print("=== END tags (= chain count) ===")
ends = [(t, q, a) for t, i, q, a, _ in ctags if i == 7]
print("n_end=%d" % len(ends))
print()
print("=== tag_at range ===")
ats = sorted(set(t for t, _, _, _, _ in ctags), key=lambda x: int(x, 16))
print("distinct_tag_at=%d first=%s last=%s" % (len(ats), ats[0] if ats else "-", ats[-1] if ats else "-"))
print()
print("=== dmareg (kick context) ===")
dms = [dm_re.match(ln).groups() for ln in trace if ln.startswith("dmareg ")]
c3 = Counter((r, v, p, ra) for _, r, v, p, ra in dms)
for k in sorted(c3):
    print("  %s=%s pc=%s ra=%s x%d" % (k[0], k[1], k[2], k[3], c3[k]))
print("n_dm=%d" % len(dms))
print()
for pat in ("st vsync=", "sema vsync=", "semaid vsync=", "irq vsync=", "gsreg vsync=", "T51_WINDOW", "T51_ST_CAP", "T51_SEMA_CAP", "T51_IRQ_CAP", "T51_GS_CAP", "T50_DMAREG_CAP"):
    print("%-16s %d" % (pat, sum(1 for ln in trace if pat in ln)))
print("T51C_ANALYZE_DONE")
