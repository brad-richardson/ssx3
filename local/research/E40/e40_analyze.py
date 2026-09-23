#!/usr/bin/env python3
"""E40 trace analysis: distinct REF addrs, tag_at sites, tagwrite stores.

Usage: python3 e40_analyze.py <mpg-src-trace.txt>
Prints: line counts, distinct addr table, per-addr tag_at table,
tagwrite summary (pc/ra/fn + a0-a3,v0,v1), and GPR dump for first
tagwrite per addr.
"""
import re
import sys
from collections import defaultdict

MPG = re.compile(
    r"^mpgsrc vsync=(\d+) tag_at=0x([0-9a-f]+) id=(\d+) qwc=(\d+) "
    r"addr=0x([0-9a-f]+) tte_vif=([0-9a-f]+)$")
SRC = re.compile(
    r"^srcread vsync=(\d+) addr=0x([0-9a-f]+) size=(\d+) "
    r"pc=0x([0-9a-f]+) ra=0x([0-9a-f]+) fn=(\S+) "
    r"a0=(0x[0-9a-f]+) a1=(0x[0-9a-f]+) a2=(0x[0-9a-f]+) a3=(0x[0-9a-f]+) "
    r"v0=(0x[0-9a-f]+) v1=(0x[0-9a-f]+) "
    r"t0=(0x[0-9a-f]+) t1=(0x[0-9a-f]+) t2=(0x[0-9a-f]+) t3=(0x[0-9a-f]+) "
    r"t4=(0x[0-9a-f]+) t5=(0x[0-9a-f]+) t6=(0x[0-9a-f]+) t7=(0x[0-9a-f]+) "
    r"t8=(0x[0-9a-f]+) t9=(0x[0-9a-f]+) "
    r"s0=(0x[0-9a-f]+) s1=(0x[0-9a-f]+) s2=(0x[0-9a-f]+) s3=(0x[0-9a-f]+) "
    r"s4=(0x[0-9a-f]+) s5=(0x[0-9a-f]+) s6=(0x[0-9a-f]+) s7=(0x[0-9a-f]+)$")
REGNAMES = ["a0", "a1", "a2", "a3", "v0", "v1",
            "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9",
            "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"]
TW = re.compile(
    r"^tagwrite vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) "
    r"pc=0x([0-9a-f]+) ra=0x([0-9a-f]+) fn=(\S+) "
    r"a0=(0x[0-9a-f]+) a1=(0x[0-9a-f]+) a2=(0x[0-9a-f]+) a3=(0x[0-9a-f]+) "
    r"v0=(0x[0-9a-f]+) v1=(0x[0-9a-f]+) "
    r"t0=(0x[0-9a-f]+) t1=(0x[0-9a-f]+) t2=(0x[0-9a-f]+) t3=(0x[0-9a-f]+) "
    r"t4=(0x[0-9a-f]+) t5=(0x[0-9a-f]+) t6=(0x[0-9a-f]+) t7=(0x[0-9a-f]+) "
    r"t8=(0x[0-9a-f]+) t9=(0x[0-9a-f]+)$")


def main():
    path = sys.argv[1]
    mpgs = []
    tws = []
    srcs = []
    other = 0
    with open(path, errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = MPG.match(line)
            if m:
                mpgs.append(m.groups())
                continue
            w = TW.match(line)
            if w:
                tws.append(w.groups())
                continue
            r = SRC.match(line)
            if r:
                srcs.append(r.groups())
                continue
            if line.strip():
                other += 1
    print(f"mpgsrc={len(mpgs)} tagwrite={len(tws)} srcread={len(srcs)} other={other}")

    by_addr = defaultdict(list)
    for g in mpgs:
        by_addr[g[4]].append(g)
    print(f"\ndistinct addr values: {len(by_addr)}")
    for addr in sorted(by_addr):
        rows = by_addr[addr]
        vs = sorted(set(int(r[0]) for r in rows))
        tags = sorted(set(r[1] for r in rows))
        ids = sorted(set(r[2] for r in rows))
        qwcs = sorted(set(r[3] for r in rows))
        ttes = sorted(set(r[5] for r in rows))
        print(f"addr=0x{addr} n={len(rows)} "
              f"vsync={vs[0]}..{vs[-1]} (n_vs={len(vs)}) "
              f"tag_at={','.join('0x' + t for t in tags)} "
              f"id={','.join(ids)} qwc={','.join(qwcs)} "
              f"tte_vif={','.join(ttes)}")

    by_watch = defaultdict(list)
    for g in tws:
        by_watch[g[1]].append(g)
    print(f"\nwatched words with stores: {len(by_watch)}")
    for watch in sorted(by_watch):
        rows = by_watch[watch]
        vs = sorted(set(int(r[0]) for r in rows))
        vals = sorted(set(r[2] for r in rows))
        pcs = sorted(set(r[3] for r in rows))
        fns = sorted(set(r[5] for r in rows))
        print(f"watch=0x{watch} n={len(rows)} "
              f"vsync={vs[0]}..{vs[-1]} (n_vs={len(vs)}) "
              f"values={','.join('0x' + v for v in vals)} "
              f"pc={','.join('0x' + p for p in pcs)} "
              f"fn={','.join(fns)}")
        first = rows[0]
        print(f"  first: vsync={first[0]} value=0x{first[2]} "
              f"pc=0x{first[3]} ra=0x{first[4]} fn={first[5]} "
              f"a0={first[6]} a1={first[7]} a2={first[8]} a3={first[9]} "
              f"v0={first[10]} v1={first[11]}")
        print(f"         t0={first[12]} t1={first[13]} t2={first[14]} "
              f"t3={first[15]} t4={first[16]} t5={first[17]} "
              f"t6={first[18]} t7={first[19]} t8={first[20]} t9={first[21]}")

    by_region = defaultdict(list)
    for g in srcs:
        region = "435bf8" if int(g[1], 16) >= 0x434000 else "4349b8"
        by_region[region].append(g)
    print(f"\nsrcread by region: {len(by_region)}")
    for region in sorted(by_region):
        rows = by_region[region]
        vs = sorted(set(int(r[0]) for r in rows))
        pcs = sorted(set(r[3] for r in rows))
        fns = sorted(set(r[5] for r in rows))
        print(f"region=0x{region} n={len(rows)} "
              f"vsync={vs[0]}..{vs[-1]} (n_vs={len(vs)}) "
              f"pc={','.join('0x' + p for p in pcs)} "
              f"fn={','.join(fns)}")
        first = rows[0]
        regs = " ".join(f"{REGNAMES[i]}={first[6 + i]}" for i in range(24))
        print(f"  first: vsync={first[0]} addr=0x{first[1]} size={first[2]} "
              f"pc=0x{first[3]} ra=0x{first[4]} fn={first[5]}")
        print(f"         {regs}")


if __name__ == "__main__":
    main()
