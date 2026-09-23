#!/usr/bin/env python3
"""T49 analyzer: per-startPC summary + first vi03/vi13 writers + vi-entry/exit
+ 0x257-before-0x8 ordering check from the T48_VU1 stream.

Usage: t49-analyze.py <trace-file> [<t48-vu1-file>]
"""
import re
import sys

def parse(fn):
    progs = []
    cur = None
    for line in open(fn, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if line.startswith("T49_BEGIN"):
            m = dict(re.findall(r"(\w+)=([^\s]+)", line))
            cur = {"begin": m, "vientry": None, "vumem": 0,
                   "vif": [], "pairs": [], "viexit": None, "end": None}
            progs.append(cur)
        elif line.startswith("vi-entry") and cur is not None and cur["vientry"] is None:
            cur["vientry"] = dict(re.findall(r"vi(\d+)=([0-9a-f]+)", line))
        elif line.startswith("vumem ") and cur is not None:
            cur["vumem"] += 1
        elif line.startswith("vif ") and cur is not None:
            cur["vif"].append(line)
        elif line.startswith("pair ") and cur is not None:
            cur["pairs"].append(line)
        elif line.startswith("vi-exit"):
            m = dict(re.findall(r"(\w+)=([^\s]+)", line))
            vi = dict(re.findall(r"vi(\d+)=([0-9a-f]+)", line))
            if cur is not None:
                cur["viexit"] = (m, vi)
        elif line.startswith("T49_END"):
            m = dict(re.findall(r"(\w+)=([^\s]+)", line))
            if cur is not None:
                cur["end"] = m
            cur = None
    return progs

def first_vi_writes(pairs, regs=(3, 13)):
    found = {}
    for p in pairs:
        m = re.search(r"\| vi(.*?)\| vf", p)
        if not m:
            continue
        for mm in re.finditer(r"(\d+):([0-9a-f]+)->([0-9a-f]+)", m.group(1)):
            r = int(mm.group(1))
            if r in regs and r not in found:
                pc = re.search(r"pc=(0x[0-9a-f]+)", p).group(1)
                dis = re.search(r"lo=[0-9a-f]+ \S+ (\S+)", p)
                up = re.search(r"up=([0-9a-f]+)", p).group(1)
                lo = re.search(r"lo=([0-9a-f]+)", p).group(1)
                found[r] = (pc, up, lo, dis and dis.group(1), mm.group(2), mm.group(3))
        if len(found) == len(regs):
            break
    return found

def ordering(vu1fn, vsync):
    """In T48_VU1 records at `vsync`: does a start_pc=0x257 precede the first 0x8?"""
    seq = []
    pat = re.compile(r"start_pc=0x([0-9a-f]+)")
    for line in open(vu1fn, encoding="utf-8", errors="replace"):
        m = re.search(r"vsync=(%s)\b" % vsync, line)
        if not m:
            continue
        c = pat.search(line)
        if c:
            seq.append(c.group(1))
    if "8" not in seq:
        return "no-0x8-in-vsync"
    first8 = seq.index("8")
    before = seq[:first8]
    if "257" in before:
        return "257-before-8 (last257@%d, first8@%d of %d progs)" % (
            len(before) - 1 - before[::-1].index("257"), first8, len(seq))
    return "no-257-before-first-8 (%d progs before)" % first8

def main():
    progs = parse(sys.argv[1])
    print("programs=%d" % len(progs))
    for pr in progs:
        b = pr["begin"]
        print("--- start_pc=%s bytepc=%s vsync=%s vumem_rows=%d vif_lines=%d pairs=%d end=%s" % (
            b.get("start_pc"), b.get("bytepc"), b.get("vsync"),
            pr["vumem"], len(pr["vif"]), len(pr["pairs"]),
            pr["end"] and (pr["end"].get("reason") + "/" + pr["end"].get("pairs"))))
        if pr["vientry"]:
            e = pr["vientry"]
            print("    vi-entry: " + " ".join(
                "vi%02d=%s" % (i, e.get("%02d" % i, "?")) for i in (0, 1, 2, 3, 11, 13, 14, 15)))
        else:
            print("    vi-entry: MISSING")
        pcs = [int(re.search(r"pc=(0x[0-9a-f]+)", p).group(1), 16) for p in pr["pairs"]]
        arr = [i for i, c in enumerate(pcs) if c == 0x418]
        print("    arrivals@0x418: count=%d first_pair_idx=%s" % (len(arr), arr[0] if arr else None))
        fw = first_vi_writes(pr["pairs"])
        for r in (3, 13):
            if r in fw:
                pc, up, lo, dis, old, new = fw[r]
                print("    vi%02d first-write: pc=%s up=%s lo=%s dis=%s %s->%s" % (r, pc, up, lo, dis, old, new))
            else:
                print("    vi%02d first-write: NOT FOUND in traced span" % r)
        if pr["viexit"]:
            m, vi = pr["viexit"]
            print("    vi-exit pairs=%s: " % m.get("pairs") + " ".join(
                "vi%02d=%s" % (i, vi.get("%02d" % i, "?")) for i in (0, 1, 2, 3, 11, 13, 14, 15)))
    if len(sys.argv) > 2:
        for pr in progs:
            if pr["begin"].get("start_pc") == "0x8":
                print("ordering@vsync=%s: %s" % (
                    pr["begin"].get("vsync"), ordering(sys.argv[2], pr["begin"].get("vsync"))))

if __name__ == "__main__":
    main()
