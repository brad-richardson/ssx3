#!/usr/bin/env python3
"""GB2 Part 3: diff [pk]/[csr] streams from two boot logs.

Usage:
  python3 local/research/GB2/gb2_pkdiff.py <boot-off.log> <boot-on.log>

Finds the first differing submitted-packet index (idx-aligned compare of
fnv/len/src, with a 5-deep indel check), prints the 10 packets before it
from both boots plus the last 10 CSR reads at or before the divergence
tick from both boots, with guest pcs. Exit 0 if streams identical.
"""
import re
import sys

PK_RE = re.compile(r"\[pk\] idx=(\d+) tick=(\d+) fnv=([0-9a-f]+) len=(\d+) src=(\S+)")
CSR_RE = re.compile(r"\[csr\] idx=(\d+) tick=(\d+) value=([0-9a-f]+) pc=([0-9a-f]+) addr=([0-9a-f]+)")


def parse(path):
    pk = {}
    csr = []
    trunc = False
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", "replace")
            m = PK_RE.search(line)
            if m:
                idx = int(m.group(1))
                pk[idx] = (int(m.group(2)), m.group(3), int(m.group(4)), m.group(5))
                continue
            m = CSR_RE.search(line)
            if m:
                csr.append((int(m.group(1)), int(m.group(2)), m.group(3), m.group(4), m.group(5)))
                continue
            if "TRUNCATED" in line:
                trunc = True
    return pk, csr, trunc


def main():
    off_pk, off_csr, off_trunc = parse(sys.argv[1])
    on_pk, on_csr, on_trunc = parse(sys.argv[2])
    print(f"off: {len(off_pk)} packets, {len(off_csr)} csr-lines, truncated={off_trunc}")
    print(f"on:  {len(on_pk)} packets, {len(on_csr)} csr-lines, truncated={on_trunc}")
    maxidx = max(max(off_pk) if off_pk else -1, max(on_pk) if on_pk else -1)
    div = None
    for i in range(maxidx + 1):
        a = off_pk.get(i)
        b = on_pk.get(i)
        if a != b:
            div = i
            break
    if div is None:
        print("IDENTICAL packet streams")
        return 0
    # Indel check: is one side ahead by k (1..5)? Needs >=3 agreements.
    # Compares (fnv,len,src), ignoring tick (extra packets may span a tick).
    def body(i, d):
        v = d.get(i)
        return v[1:] if v else None

    kind = "substitution-or-end"
    for k in range(1, 6):
        agree_on = sum(1 for j in range(6) if body(div + j, off_pk) is not None
                       and body(div + j, off_pk) == body(div + k + j, on_pk))
        agree_off = sum(1 for j in range(6) if body(div + j, on_pk) is not None
                        and body(div + j, on_pk) == body(div + k + j, off_pk))
        if agree_on >= 3:
            kind = f"indel: on-side has {k} extra packet(s) at idx {div} ({agree_on}/6 agree)"
            break
        if agree_off >= 3:
            kind = f"indel: off-side has {k} extra packet(s) at idx {div} ({agree_off}/6 agree)"
            break
    print(f"FIRST DIVERGENCE at packet idx {div} ({kind})")
    print()
    print("idx     off-tick off-fnv    off-len off-src | on-tick on-fnv     on-len on-src")
    for i in range(max(0, div - 10), div + 2):
        a = off_pk.get(i)
        b = on_pk.get(i)
        sa = f"{a[0]:<8d} {a[1]:>8s}   {a[2]:<7d} {a[3]:<7s}" if a else f"{'-':<8s} {'-':>8s}   {'-':<7s} {'-':<7s}"
        sb = f"{b[0]:<8d} {b[1]:>8s}   {b[2]:<7d} {b[3]:<7s}" if b else f"{'-':<8s} {'-':>8s}   {'-':<7s} {'-':<7s}"
        mark = " <<<" if i == div else ""
        print(f"{i:<7d} {sa} | {sb}{mark}")
    div_tick = None
    if div in off_pk:
        div_tick = off_pk[div][0]
    elif div in on_pk:
        div_tick = on_pk[div][0]
    print()
    print(f"divergence tick ~{div_tick}; last 10 CSR reads at/before it per boot:")
    print("off:")
    shown = 0
    for idx, tick, val, pc, addr in off_csr:
        if div_tick is not None and tick > div_tick:
            break
        shown += 1
    for row in [r for r in off_csr if div_tick is None or r[1] <= div_tick][-10:]:
        print(f"  csr-idx={row[0]} tick={row[1]} value={row[2]} pc={row[3]} addr={row[4]}")
    print("on:")
    for row in [r for r in on_csr if div_tick is None or r[1] <= div_tick][-10:]:
        print(f"  csr-idx={row[0]} tick={row[1]} value={row[2]} pc={row[3]} addr={row[4]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
