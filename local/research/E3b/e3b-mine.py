#!/usr/bin/env python3
"""E3b miner: parse [e3:*] rows, dedupe R2 macro/store pairs, emit tables."""
import re
import sys

LOG = "/Volumes/Extreme SSD/ps2recomp-spike/P1/run/boot-e3b-1.log"

r1, r2, r3, r4, r4sum, markers = [], [], [], [], [], []
torn = 0
total_e3 = 0
with open(LOG, "rb") as f:
    for raw in f:
        if b"[e3:" not in raw:
            continue
        total_e3 += 1
        try:
            line = raw.decode("ascii").strip()
        except UnicodeDecodeError:
            torn += 1
            continue
        m = re.match(r"\[e3:([a-z0-9-]+)\] (.*)", line)
        if not m:
            torn += 1
            continue
        kind, rest = m.group(1), m.group(2)
        kv = dict(re.findall(r"(\w+)=([^\s]+)", rest))
        if kind == "r1":
            if "out" not in kv or kv["out"] not in ("call", "skip"):
                torn += 1
                continue
            r1.append(kv)
        elif kind == "r2":
            r2.append(kv)
        elif kind == "r3":
            r3.append(kv)
        elif kind == "r4":
            r4.append(kv)
        elif kind == "r4sum":
            r4sum.append(kv)
        elif kind in ("armed", "span-complete", "byte-cap"):
            markers.append(line)

print(f"total_e3={total_e3} torn={torn}")
print(f"r1={len(r1)} r2={len(r2)} r3={len(r3)} r4={len(r4)} r4sum={len(r4sum)}")
for m in markers:
    print(f"MARK {m}")

# R2 dedupe: adjacent (macro,store) identical (addr,width,newlo,newhi,pc,thread) pairs.
dedup = 0
r2solo = []
i = 0
while i < len(r2):
    a = r2[i]
    if (i + 1 < len(r2) and a.get("src") == "macro" and r2[i + 1].get("src") == "store"
            and all(a.get(k) == r2[i + 1].get(k) for k in ("addr", "width", "newlo", "newhi", "pc", "thread"))):
        # merged store: keep macro row, tag it
        a = dict(a)
        a["src"] = "macro+store"
        r2solo.append(a)
        dedup += 1
        i += 2
    else:
        r2solo.append(a)
        i += 1
print(f"r2_dedup_pairs={dedup} r2_solo={len(r2solo)}")

# R2 by addr/pc
from collections import Counter
print("R2 addr x count:", Counter(r.get("addr", "?") for r in r2solo).most_common(12))
print("R2 pc x count:", Counter(r.get("pc", "?") for r in r2solo).most_common(12))
print("R2 src x count:", Counter(r.get("src", "?") for r in r2solo).most_common(6))
print("R3 tag x count:", Counter(r.get("tag", "?") for r in r3).most_common(20))

# R1 outcomes
print("R1 out x count:", Counter((r["inv"], r["out"]) for r in r1).most_common(6))
skips = [r for r in r1 if r["out"] == "skip"]
for r in skips:
    print(f"SKIP n={r['n']} inv={r['inv']} a1={r['a1']} k={r['k']} pre={r['h10p']},{r['h1cp']},{r['h1ep']} "
          f"post={r['h10o']},{r['h1co']},{r['h1eo']} base={r['base']}")

# R1: any pre!=post?
changed = [r for r in r1 if (r["h10p"], r["h1cp"], r["h1ep"]) != (r["h10o"], r["h1co"], r["h1eo"])]
print(f"R1 pre!=post: {len(changed)}")
for r in changed:
    print(f"  CHG n={r['n']} k={r['k']} pre={r['h10p']},{r['h1cp']},{r['h1ep']} post={r['h10o']},{r['h1co']},{r['h1eo']}")

# R4
for r in r4:
    print(f"R4 seq={r['seq']} inv={r['inv']} fn={r['fn']} ra={r['ra']} src={r['src']}")
for r in r4sum:
    print(f"R4SUM inv={r['inv']} nrec={r['nrec']} s1min={r['s1min']} s1max={r['s1max']} nbases={r['nbases']} drift={r['drift']}")

# seq monotonicity
seqs = []
for r in r1:
    seqs.append(int(r["seq"]))
for r in r2:
    seqs.append(int(r["seq"]))
for r in r3:
    seqs.append(int(r["seq"]))
for r in r4:
    seqs.append(int(r["seq"]))
for r in r4sum:
    seqs.append(int(r["seq"]))
print(f"seq min={min(seqs)} max={max(seqs)} unique={len(set(seqs))} total={len(seqs)}")
