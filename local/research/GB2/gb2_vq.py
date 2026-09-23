#!/usr/bin/env python3
"""GB2 Part 2: compare [vq] quiescent samples from two boot logs.

Usage:
  python3 local/research/GB2/gb2_vq.py <boot-off.log> <boot-on.log>

Parses lines like:
  [vq] tick=100 vram=1a2b3c4d regs=5e6f7081 size=4194304 sub=1234 reg=56
Pass = identical vram+regs fnv at every matched tick. On the first
mismatch prints the tick and the submit-index range since the previous
match. Exit 0 on pass, 1 otherwise. Also prints presents/sec for each
boot (count of [frame:dump] lines; wall comes from the wrapper result).
"""
import re
import sys

VQ_RE = re.compile(
    r"\[vq\] tick=(\d+) vram=([0-9a-f]+) regs=([0-9a-f]+) size=(\d+) sub=(\d+) reg=(\d+)"
)
DUMP_RE = re.compile(r"\[frame:dump\] seq=(\d+) tick=(\d+)")


def parse(path):
    vq = {}
    dumps = 0
    armed = False
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", "replace")
            if "[vq] armed" in line:
                armed = True
            m = VQ_RE.search(line)
            if m:
                tick = int(m.group(1))
                vq[tick] = tuple(m.groups()[1:])
                continue
            if DUMP_RE.search(line):
                dumps += 1
    return vq, dumps, armed


def main():
    off_log, on_log = sys.argv[1], sys.argv[2]
    off, off_dumps, off_armed = parse(off_log)
    on, on_dumps, on_armed = parse(on_log)
    print(f"off: {len(off)} vq samples armed={off_armed} dumps={off_dumps}")
    print(f"on:  {len(on)} vq samples armed={on_armed} dumps={on_dumps}")
    if not off_armed or not on_armed:
        print("REFUSE: VQ gate not armed in both boots")
        return 2
    common = sorted(set(off) & set(on))
    print(f"matched ticks: {len(common)}")
    if not common:
        print("REFUSE: no matched ticks")
        return 2
    print()
    print("tick   off-vram   off-regs   on-vram    on-regs    off-sub  on-sub   verdict")
    prev = None
    mism = 0
    first_mism = None
    for tick in common:
        ov, orr, osz, osub, oreg = off[tick]
        nv, nrr, nsz, nsub, nreg = on[tick]
        ok = (ov, orr) == (nv, nrr)
        if not ok:
            mism += 1
            if first_mism is None:
                prev_osub = off[prev][3] if prev is not None else "0"
                prev_nsub = on[prev][3] if prev is not None else "0"
                first_mism = (tick, prev, prev_osub, osub, prev_nsub, nsub, oreg, nreg)
        prev = tick
        print(f"{tick:<6d} {ov:>8s}   {orr:>8s}   {nv:>8s}   {nrr:>8s}   "
              f"{osub:>7s}  {nsub:>7s}  {'OK' if ok else 'MISMATCH'}")
    print()
    print(f"matched={len(common)} mismatches={mism}")
    if first_mism is not None:
        tick, prev_tick, prev_osub, osub, prev_nsub, nsub, oreg, nreg = first_mism
        print(f"FIRST MISMATCH at tick {tick} (previous matched tick: {prev_tick})")
        print(f"  packet index range since previous match: off ({prev_osub}, {osub}], "
              f"on ({prev_nsub}, {nsub}]")
        print(f"  reg writes at tick: off {oreg}, on {nreg}")
        return 1
    print("PASS: identical vram+regs fnv at every matched tick")
    return 0


if __name__ == "__main__":
    sys.exit(main())
