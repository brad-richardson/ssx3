#!/usr/bin/env python3
"""E44 analyzer: summarize spw (scratchpad write watch) lines.

Usage:
  python3 local/research/E44/e44_analyze.py <trace.txt>

Prints per-word writer tables: (vsync range, n, via, value set, pc set,
ra set, fn set, src set) plus the full register state of the first line
per (addr, via, pc) for the codegen join.
"""

import sys
from collections import defaultdict

REG_FIELDS = ("a0 a1 a2 a3 v0 v1 t0 t1 t2 t3 t4 t5 t6 t7 t8 t9 "
              "s0 s1 s2 s3 s4 s5 s6 s7").split()


def parse(path):
    rows = []
    eb = []
    last = []
    torn = 0
    with open(path, errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("ebwlast "):
                parts = line.split()
                try:
                    d = {}
                    for p in parts[1:]:
                        k, v = p.split("=", 1)
                        d[k] = v
                    for k in ("vsync", "addr", "value", "via", "pc",
                              "ra", "fn"):
                        if k not in d:
                            raise ValueError(k)
                    d["vsync"] = int(d["vsync"])
                    eb.append(d)
                except ValueError:
                    torn += 1
                continue
            if line.startswith("spwlast "):
                last.append(line)
                continue
            if not line.startswith("spw "):
                continue
            parts = line.split()
            try:
                d = {}
                for p in parts[1:]:
                    k, v = p.split("=", 1)
                    d[k] = v
                # grammar: all keys present
                for k in ("vsync", "addr", "value", "via", "src", "pc",
                          "ra", "fn") + tuple(REG_FIELDS):
                    if k not in d:
                        raise ValueError(k)
                d["vsync"] = int(d["vsync"])
                rows.append(d)
            except ValueError:
                torn += 1
    return rows, eb, last, torn


def main():
    path = sys.argv[1]
    rows, eb, last, torn = parse(path)
    print(f"file={path} spw_rows={len(rows)} ebwlast_rows={len(eb)} "
          f"spwlast_rows={len(last)} torn={torn}")
    if eb:
        print("\n## ebwlast (last writer per word per changed vsync)")
        for r in eb:
            print(f"  vsync={r['vsync']} addr={r['addr']} value={r['value']} "
                  f"via={r['via']} pc={r['pc']} ra={r['ra']} fn={r['fn']}")
    if last:
        print(f"\n## spwlast ({len(last)} lines)")
        for line in last[:45]:
            print(f"  {line[:360]}")
    by_addr = defaultdict(list)
    for r in rows:
        by_addr[r["addr"]].append(r)
    for addr in sorted(by_addr):
        rs = by_addr[addr]
        vs = sorted(r["vsync"] for r in rs)
        print(f"\n## {addr} n={len(rs)} vsync={vs[0]}..{vs[-1]}")
        print(f"  value={sorted(set(r['value'] for r in rs))}")
        print(f"  via={sorted(set(r['via'] for r in rs))}")
        print(f"  pc={sorted(set(r['pc'] for r in rs))}")
        print(f"  ra={sorted(set(r['ra'] for r in rs))}")
        print(f"  fn={sorted(set(r['fn'] for r in rs))}")
        print(f"  src={sorted(set(r['src'] for r in rs))}")
        seen = set()
        for r in rs:
            key = (r["via"], r["pc"])
            if key in seen:
                continue
            seen.add(key)
            regs = " ".join(f"{k}={r[k]}" for k in REG_FIELDS)
            print(f"  first via={r['via']} pc={r['pc']} vsync={r['vsync']} "
                  f"value={r['value']} src={r['src']} ra={r['ra']} fn={r['fn']}")
            print(f"    {regs}")


if __name__ == "__main__":
    main()
