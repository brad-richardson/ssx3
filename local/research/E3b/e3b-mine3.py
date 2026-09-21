#!/usr/bin/env python3
"""E3b miner part 3: pc x addr, R1 full spans, T2 befores."""
import re
from collections import Counter, defaultdict

LOG = "/Volumes/Extreme SSD/ps2recomp-spike/P1/run/boot-e3b-1.log"

r1, r2 = [], []
with open(LOG, "rb") as f:
    for raw in f:
        if b"[e3:r1]" in raw or b"[e3:r2]" in raw:
            try:
                line = raw.decode("ascii").strip()
            except UnicodeDecodeError:
                continue
            m = re.match(r"\[e3:(r[12])\] (.*)", line)
            if not m:
                continue
            kv = dict(re.findall(r"(\w+)=([^\s]+)", m.group(2)))
            kv["_seq"] = int(kv["seq"])
            (r1 if m.group(1) == "r1" else r2).append(kv)

r2solo = []
i = 0
while i < len(r2):
    a = r2[i]
    if (i + 1 < len(r2) and a.get("src") == "macro" and r2[i + 1].get("src") == "store"
            and all(a.get(k) == r2[i + 1].get(k) for k in ("addr", "width", "newlo", "newhi", "pc", "thread"))):
        a = dict(a)
        a["src"] = "macro+store"
        r2solo.append(a)
        i += 2
    else:
        r2solo.append(a)
        i += 1

print("R2 pc x addr-region:")
for pc in sorted(set(r["pc"] for r in r2solo)):
    rows = [r for r in r2solo if r["pc"] == pc]
    regs = Counter("ramp" if r["addr"].startswith("0x70000") else
                   ("live" if 0x70001C00 <= int(r["addr"], 16) <= 0x7000259F else "other")
                   for r in rows)
    seqs = sorted(r["_seq"] for r in rows)
    print(f"  pc={pc} n={len(rows)} {dict(regs)} seqrange={seqs[0]}-{seqs[-1]}")

print("\nR1 spans (label inv -> ordinal = label-1):")
for r in sorted(r1, key=lambda x: int(x["n"])):
    print(f"  n={r['n']} lbl={r['inv']} k={r['k']} entry={r['seqEntry']} close={r['_seq']} out={r['out']} "
          f"a2={r['a2']} pre={r['h10p']},{r['h1cp']},{r['h1ep']} post={r['h10o']},{r['h1co']},{r['h1eo']}")

print("\nR2 new-values at +0x1E-bearing windows (k0-3 +0x18 wins) final-per-window:")
wins18 = [f"0x{0x70001C18 + k*0x80:x}" for k in range(4)]
for w in wins18:
    rows = sorted([r for r in r2solo if r["addr"] == w], key=lambda r: r["_seq"])
    if rows:
        last = rows[-1]
        print(f"  {w}: {len(rows)} writes, last seq={last['_seq']} new={last['newlo']} pc={last['pc']}")
    else:
        print(f"  {w}: 0 R2 writes (SPR-only)")
