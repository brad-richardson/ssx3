#!/usr/bin/env python3
"""E42 analyzer: attribute every plant hit to its guest function.

Usage:
  python3 local/research/E42/e42_analyze.py ~/dev/ssx3-work/E42-run/cdread-e42a.txt

Tables:
  1. hits per (via, fn, pc): n, vsync range, addrs, values
  2. per-hit detail for the watched window (function, pc, value, registers)
  3. E41-shape check (even vsyncs from 1274, all 0x435bd0, 4 words)
"""

import re
import sys
from collections import defaultdict

PLANT = re.compile(
    r"^plant vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) "
    r"via=(\S+) src=(\S+) seq=(\S+)(.*?)\s*$")
KV = re.compile(r"([A-Za-z0-9]+)=(\S+)")

REGS = ["a0", "a1", "a2", "a3", "v0", "v1",
        "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9",
        "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"]


def parse_extra(rest):
    out = {}
    for m in KV.finditer(rest or ""):
        out[m.group(1)] = m.group(2)
    return out


def main(path):
    plants = []
    other = defaultdict(int)
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            m = PLANT.match(line)
            if not m:
                kind = line.split(" ", 1)[0] if line.strip() else "(blank)"
                other[kind] += 1
                continue
            vsync, addr, value, via, src, seq, rest = m.groups()
            ex = parse_extra(rest)
            plants.append({
                "vsync": int(vsync), "addr": addr, "value": value,
                "via": via, "raw": ex.get("raw", "-"),
                "fn": ex.get("fn", "-"), "fn1": ex.get("fn1", "-"),
                "pc": ex.get("pc", "-"), "ra": ex.get("ra", "-"),
                "ex": ex, "line": line,
            })

    print(f"file: {path}")
    print(f"plant lines: {len(plants)}; other lines: {dict(other)}")
    if not plants:
        return

    vsyncs = sorted({p["vsync"] for p in plants})
    print(f"vsync range: {vsyncs[0]}..{vsyncs[-1]} ({len(vsyncs)} distinct)")
    print(f"values: {sorted({p['value'] for p in plants})}")
    print(f"addrs: {sorted({p['addr'] for p in plants})}")
    print(f"vias: {sorted({p['via'] for p in plants})}")
    print(f"raws: {sorted({p['raw'] for p in plants})}")

    print("\nTable 1 -- hits per (via, fn, pc):")
    print("| via | fn | pc | n | vsyncs | addrs | values |")
    groups = defaultdict(list)
    for p in plants:
        groups[(p["via"], p["fn"], p["pc"])].append(p)
    for (via, fn, pc) in sorted(groups):
        ps = groups[(via, fn, pc)]
        vs = sorted({p["vsync"] for p in ps})
        span = f"{vs[0]}..{vs[-1]} ({len(vs)})" if len(vs) > 1 else str(vs[0])
        print(f"| {via} | {fn} | {pc} | {len(ps)} | {span} | "
              f"{','.join(sorted({p['addr'] for p in ps}))} | "
              f"{','.join(sorted({p['value'] for p in ps}))} |")

    print("\nTable 1b -- fn1 (one level up) distribution:")
    print("| fn1 | n |")
    fn1s = defaultdict(int)
    for p in plants:
        fn1s[p["fn1"]] += 1
    for fn1 in sorted(fn1s):
        print(f"| {fn1} | {fn1s[fn1]} |")

    print("\nTable 1c -- ra (guest return) distribution:")
    print("| ra | n |")
    ras = defaultdict(int)
    for p in plants:
        ras[p["ra"]] += 1
    for ra in sorted(ras):
        print(f"| {ra} | {ras[ra]} |")

    print("\nTable 2 -- per-hit detail (first 60):")
    print("| vsync | addr | value | via | fn | pc | ra | key regs |")
    for p in plants[:60]:
        regs = " ".join(f"{r}={p['ex'].get(r, '-')}" for r in
                        ["a0", "a1", "a2", "v0", "s0", "s1", "s2", "s3"])
        print(f"| {p['vsync']} | 0x{p['addr']} | 0x{p['value']} | {p['via']} | "
              f"{p['fn']} | {p['pc']} | {p['ra']} | {regs} |")
    if len(plants) > 60:
        print(f"... ({len(plants) - 60} more)")

    # E41-shape check
    odd = sorted({p["vsync"] for p in plants if p["vsync"] % 2 == 1})
    nonbd0 = [p for p in plants if p["value"] != "00435bd0"]
    per_word = defaultdict(int)
    for p in plants:
        per_word[p["addr"]] += 1
    print("\nTable 3 -- E41-shape check:")
    print(f"odd-vsync hits: {len(odd)} {odd[:10]}")
    print(f"non-0x435bd0 hits: {len(nonbd0)}")
    for p in nonbd0[:10]:
        print(f"  {p['line']}")
    print("per-word counts: " + ", ".join(f"{a}x{n}" for a, n in sorted(per_word.items())))

    # Register stability: which regs are constant across all macro-path hits?
    macro = [p for p in plants if p["via"] == "ee-store-macro"]
    if macro:
        print(f"\nTable 4 -- register constancy over {len(macro)} macro-path hits:")
        print("| reg | distinct | values (up to 5) |")
        for r in REGS + ["pc", "ra"]:
            vals = sorted({(p["ex"].get(r, "-") if r in REGS else p[r]) for p in macro})
            show = ",".join(vals[:5]) + ("..." if len(vals) > 5 else "")
            print(f"| {r} | {len(vals)} | {show} |")


if __name__ == "__main__":
    main(sys.argv[1])
