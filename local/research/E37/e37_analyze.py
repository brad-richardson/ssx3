#!/usr/bin/env python3
"""E37 entry-trace analyzer: per-startPC setup tables.

Usage: python3 local/research/E37/e37_analyze.py <vu1-entry-*.txt>

Prints per block: setup pair count, arrivals, first vi03/vi13 writers
with source operands and values, VIF command census, nonzero vumem rows.
"""
import re
import sys


def parse(path):
    blocks = []
    cur = None
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("entry "):
                m = re.match(r"entry startPC=(0x[0-9a-f]+) vsync=(\d+)", line)
                cur = {"startPC": m.group(1), "vsync": int(m.group(2)),
                       "vumem": [], "vif": [], "pairs": [], "tail": ""}
            elif line.startswith("endentry "):
                cur["tail"] = line
                blocks.append(cur)
                cur = None
            elif cur is None:
                continue
            elif line.startswith("vumem "):
                cur["vumem"].append(line)
            elif line.startswith("vif "):
                cur["vif"].append(line)
            elif line.startswith("pair "):
                cur["pairs"].append(line)
    return blocks


def main():
    blocks = parse(sys.argv[1])
    for b in blocks:
        print(f"=== {b['startPC']} @vsync {b['vsync']}: {b['tail']}")
        # Setup = pairs before the first pc=0x418 arrival.
        setup = 0
        for p in b["pairs"]:
            if re.match(r"pair pc=0x418\b", p):
                break
            setup += 1
        print(f"setup pairs: {setup}, total pairs: {len(b['pairs'])}")
        for reg in ("vi3", "vi13"):
            for p in b["pairs"]:
                m = re.search(r"pair pc=(0x[0-9a-f]+) up=([0-9a-f]+) lo=([0-9a-f]+) (.*?) \| up", p)
                w = re.search(r"\| " + reg + r":([0-9a-f]+)->([0-9a-f]+)", p)
                if w:
                    print(f"first {reg}: {p.split('|')[0].strip()} :: {m.group(4)} "
                          f":: {reg} {w.group(1)}->{w.group(2)}")
                    # Full line for source operands (disasm names them).
                    print(f"    full: {p}")
                    break
        # VIF census by command name.
        census = {}
        for v in b["vif"]:
            name = v.split()[1] if len(v.split()) > 1 else "?"
            census[name] = census.get(name, 0) + 1
        print("vif census:", " ".join(f"{k}={n}" for k, n in sorted(census.items())))
        nz = [r for r in b["vumem"] if r.split()[2:] != ["00000000"] * 4]
        print(f"vumem nonzero rows: {len(nz)}/{len(b['vumem'])}")
        print()


if __name__ == "__main__":
    main()
