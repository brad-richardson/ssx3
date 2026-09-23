#!/usr/bin/env python3
"""Summarize an E39 vif-mpg log: outcome counts, non-copied rows, B-word carriers."""
import sys
from collections import Counter

path = sys.argv[1]
counts = Counter()
noncopied = []
carriers2 = []
carriers8 = []
total = 0
for line in open(path):
    line = line.strip()
    if not line.startswith("mpg "):
        continue
    total += 1
    f = dict(kv.split("=", 1) for kv in line.split()[1:] if "=" in kv)
    counts[f.get("outcome", "?")] += 1
    if f.get("outcome") != "copied":
        noncopied.append((f.get("vsync"), f.get("imm"), f.get("num"),
                          f.get("dest"), f.get("outcome"), f.get("avail"), f.get("fnv")))
    s2 = line.split("slot2=")[1].split(" slot8=")[0] if "slot2=" in line else ""
    s8 = line.split("slot8=")[1] if "slot8=" in line else ""
    if "40000048" in s2:
        carriers2.append((f.get("vsync"), f.get("imm"), f.get("num"), f.get("outcome"), s2))
    if "400000f2" in s8:
        carriers8.append((f.get("vsync"), f.get("imm"), f.get("num"), f.get("outcome"), s8))

print(f"total={total}")
for k in ("copied", "drop_addr", "drop_partial", "clipped"):
    print(f"  {k}={counts.get(k, 0)}")
for k, v in counts.items():
    if k not in ("copied", "drop_addr", "drop_partial", "clipped"):
        print(f"  {k}={v} (UNEXPECTED)")
print(f"non-copied rows: {len(noncopied)}")
for row in noncopied[:200]:
    print("  vsync=%s imm=%s num=%s dest=%s outcome=%s avail=%s fnv=%s" % row)
if len(noncopied) > 200:
    print(f"  ... +{len(noncopied) - 200} more")
print(f"slot2 carriers of 40000048: {len(carriers2)}")
for row in carriers2[:50]:
    print("  vsync=%s imm=%s num=%s outcome=%s slot2=%s" % row)
print(f"slot8 carriers of 400000f2: {len(carriers8)}")
for row in carriers8[:50]:
    print("  vsync=%s imm=%s num=%s outcome=%s slot8=%s" % row)
