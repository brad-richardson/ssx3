#!/usr/bin/env python3
"""E43 analyzer: draw-record census by mode, producers by fn, h394 calls.

Usage:
  python3 local/research/E43/e43_analyze.py ~/dev/ssx3-work/E43-run/e43-e43a.txt
"""

import re
import sys
from collections import defaultdict

DREC = re.compile(r"^drec vsync=(\d+) src=0x([0-9a-f]+) mode=(\S+) count=(\d+)\s*$")
DRECS = re.compile(
    r"^drecs vsync=(\d+) src=0x([0-9a-f]+) mode=(\S+) addr=0x([0-9a-f]+) wmode=(\S+) "
    r"w0=(\S+) w1=(\S+) w2=(\S+) w3=(\S+)\s*$")
DPROD = re.compile(
    r"^dprod vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) mode=(\d+) "
    r"pc=0x([0-9a-f]+) ra=0x([0-9a-f]+) fn=(\S+) src=(\S+) raw=0x([0-9a-f]+)\s*$")
H394 = re.compile(
    r"^h394 vsync=(\d+) s1=0x([0-9a-f]+) w0=(\S+) w1=(\S+) w2=(\S+) w3=(\S+) "
    r"hash=0x([0-9a-f]+) ret=0x([0-9a-f]+) stores=(\d+)\s*$")


def main(path):
    drec, drecs, dprod, h394, other = [], [], [], [], defaultdict(int)
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            m = DREC.match(line)
            if m:
                drec.append(tuple(m.groups()))
                continue
            m = DRECS.match(line)
            if m:
                drecs.append(tuple(m.groups()))
                continue
            m = DPROD.match(line)
            if m:
                dprod.append(tuple(m.groups()))
                continue
            m = H394.match(line)
            if m:
                h394.append(tuple(m.groups()))
                continue
            other[line.split(" ", 1)[0] if line.strip() else "(blank)"] += 1

    print(f"file: {path}")
    print(f"drec={len(drec)} drecs={len(drecs)} dprod={len(dprod)} h394={len(h394)} "
          f"other={dict(other)}")

    if drec:
        print("\nTable 1 -- records walked per (vsync, src, mode):")
        print("| vsync | src | mode | count |")
        for vsync, src, mode, count in sorted(drec, key=lambda r: (int(r[0]), r[1], r[2])):
            print(f"| {vsync} | 0x{src} | {mode} | {count} |")
        print("\nTable 1b -- mode totals:")
        tot = defaultdict(int)
        for vsync, src, mode, count in drec:
            tot[(src, mode)] += int(count)
        for (src, mode) in sorted(tot):
            print(f"| src=0x{src} mode={mode} | {tot[(src, mode)]} |")

    if drecs:
        print("\nTable 2 -- record sample (first 20 drecs):")
        print("| vsync | src | mode | addr | wmode | w0 | w1 | w2 | w3 |")
        for r in drecs[:20]:
            print(f"| {r[0]} | 0x{r[1]} | {r[2]} | 0x{r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} |")
        if len(drecs) > 20:
            print(f"... ({len(drecs) - 20} more)")
        mismatch = [r for r in drecs if r[2] != "X" and r[4] != "-" and r[2] != r[4]]
        print(f"drecs mode!=wmode: {len(mismatch)}")
        for r in mismatch[:5]:
            print(f"  vsync={r[0]} mode={r[2]} wmode={r[4]} addr=0x{r[3]}")

    if dprod:
        print("\nTable 3 -- producers by fn:")
        print("| fn | n | pcs | addrs (up to 4) |")
        by_fn = defaultdict(list)
        for r in dprod:
            by_fn[r[6]].append(r)
        for fn in sorted(by_fn, key=lambda f: -len(by_fn[f])):
            ps = by_fn[fn]
            pcs = sorted({p[4] for p in ps})
            addrs = sorted({p[1] for p in ps})
            show = ",".join("0x" + a for a in addrs[:4]) + ("..." if len(addrs) > 4 else "")
            print(f"| {fn} | {len(ps)} | {','.join('0x' + p for p in pcs[:6])} | {show} |")
        print("\nTable 3b -- producer detail (first 20):")
        print("| vsync | addr | value | mode | pc | fn | src |")
        for r in dprod[:20]:
            print(f"| {r[0]} | 0x{r[1]} | 0x{r[2]} | {r[3]} | 0x{r[4]} | {r[6]} | {r[7]} |")

    if h394:
        print("\nTable 4 -- h394 hash calls:")
        print("| vsync | s1 | w0 | w1 | w2 | w3 | hash | ret | stores |")
        for r in h394:
            print(f"| {r[0]} | 0x{r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | 0x{r[6]} | "
                  f"0x{r[7]} | {r[8]} |")
        hashes = sorted({r[6] for r in h394})
        print(f"distinct hashes: {len(hashes)}: {','.join('0x' + h for h in hashes[:20])}")
        print(f"stores=1: {sum(1 for r in h394 if r[9] == '1')}/{len(h394)}")


if __name__ == "__main__":
    main(sys.argv[1])
