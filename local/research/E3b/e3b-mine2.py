#!/usr/bin/env python3
"""E3b miner part 2: R3 transfers, live-s1 R2, pc map inputs."""
import re
from collections import Counter, defaultdict

LOG = "/Volumes/Extreme SSD/ps2recomp-spike/P1/run/boot-e3b-1.log"

r1, r2, r3 = [], [], []
with open(LOG, "rb") as f:
    for raw in f:
        if b"[e3:r" not in raw:
            continue
        try:
            line = raw.decode("ascii").strip()
        except UnicodeDecodeError:
            continue
        m = re.match(r"\[e3:(r[123])\] (.*)", line)
        if not m:
            continue
        kv = dict(re.findall(r"(\w+)=([^\s]+)", m.group(2)))
        kv["_seq"] = int(kv["seq"])
        {"r1": r1, "r2": r2, "r3": r3}[m.group(1)].append(kv)

# R2 dedupe (same rule)
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

# R3 transfers: group consecutive seqs with same (dst,size,x)
r3s = sorted(r3, key=lambda r: r["_seq"])
transfers = []
cur = []
for r in r3s:
    key = (r["dst"], r["size"], r["x"])
    if cur and (cur[0]["dst"], cur[0]["size"], cur[0]["x"]) == key and r["_seq"] == cur[-1]["_seq"] + 1:
        cur.append(r)
    else:
        if cur:
            transfers.append(cur)
        cur = [r]
if cur:
    transfers.append(cur)
print(f"R3 transfers: {len(transfers)}")
for t in transfers:
    print(f"  seqs {t[0]['_seq']}-{t[-1]['_seq']} frame={t[0]['frame']} dst={t[0]['dst']} size={t[0]['size']} "
          f"nwin={len(t)} x={t[0]['x']}")

# Live s1 windows
live10 = {f"0x{0x70001C10 + k*0x80:x}" for k in range(20)}
live18 = {f"0x{0x70001C18 + k*0x80:x}" for k in range(20)}
live = live10 | live18

print("\nR3 rows on LIVE s1 windows (first transfer only):")
t0 = transfers[0]
for r in sorted(t0, key=lambda r: r["win"]):
    if r["win"] in live:
        print(f"  {r['win']} before={r['before']} after={r['after']}")

print("\nR2 solo on LIVE s1 addrs:")
live_r2 = [r for r in r2solo if r.get("addr") in live or
           (r.get("addr", "").startswith("0x70001c") or r.get("addr", "").startswith("0x70001d") or
            r.get("addr", "").startswith("0x70001e") or r.get("addr", "").startswith("0x70001f") or
            r.get("addr", "").startswith("0x700020") or r.get("addr", "").startswith("0x700021") or
            r.get("addr", "").startswith("0x700022") or r.get("addr", "").startswith("0x700023") or
            r.get("addr", "").startswith("0x700024") or r.get("addr", "").startswith("0x700025"))]
print(f"  count={len(live_r2)}")
for r in sorted(live_r2, key=lambda r: r["_seq"])[:40]:
    print(f"  seq={r['_seq']} addr={r['addr']} w={r['width']} old={r['oldlo']} new={r['newlo']} pc={r['pc']}")

print("\nR2 RAM (0x5014xx) rows:", sum(1 for r in r2solo if r.get("addr", "").startswith("0x5014")))
print("R2 non-scratchpad rows:", [(r.get("addr"), r.get("pc")) for r in r2solo
      if not r.get("addr", "").startswith("0x7000")][:10])

# R1 entry seqs per k (inv 1000-label)
print("\nR1 inv=1000-label entry seqs + s1e==a1 check:")
bad = 0
for r in sorted([x for x in r1 if x["inv"] == "1000"], key=lambda x: int(x["n"])):
    if r["s1e"] != r["a1"]:
        bad += 1
        print(f"  MISMATCH n={r['n']} a1={r['a1']} s1e={r['s1e']}")
print(f"  s1e!=a1: {bad}/20")
for r in sorted([x for x in r1 if x["inv"] == "1000"], key=lambda x: int(x["n"]))[:3]:
    print(f"  n={r['n']} k={r['k']} seqEntry={r['seqEntry']} a0={r['a0']} a1={r['a1']} a2={r['a2']} ra={r['ra']} src={r['src']}")
