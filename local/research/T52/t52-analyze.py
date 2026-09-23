#!/usr/bin/env python3
# T52 analyze: phase tables + LBN ranges from the extracted T52 trace.
# Usage: python3 t52-analyze.py <trace>
import re
import sys

CDREAD = re.compile(
    r"T52_CDREAD seq=(\d+) vsync=(\d+) kind=(CD|DVD|CDDA) lbn=(\d+) sectors=(\d+) "
    r"blocksize=(\d+) speed=(\d+)x spindle=(CAV|CLV) readmode=(0x[0-9a-f]+) dest=-"
)
MARK = re.compile(r"T52_MARK vsync=(\d+) label=(title|menu|scentry|scsettled)")


def ranges(lbns):
    if not lbns:
        return []
    ss = sorted(set(lbns))
    out, a, b = [], ss[0], ss[0]
    for x in ss[1:]:
        if x == b + 1:
            b = x
        else:
            out.append((a, b))
            a = b = x
    out.append((a, b))
    return out


def main():
    reads, marks = [], {}
    with open(sys.argv[1]) as f:
        for line in f:
            m = CDREAD.search(line)
            if m:
                g = m.groups()
                reads.append(dict(seq=int(g[0]), vsync=int(g[1]), kind=g[2],
                                  lbn=int(g[3]), sectors=int(g[4]), bs=int(g[5]),
                                  speed=int(g[6]), spindle=g[7], mode=g[8]))
                continue
            m = MARK.search(line)
            if m:
                marks[m.group(2)] = int(m.group(1))
    print("marks:", marks)
    vmax = max([r["vsync"] for r in reads] + list(marks.values()))
    bounds = [("boot>title", 0, marks["title"]), ("title>menu", marks["title"], marks["menu"]),
              ("menu>scentry", marks["menu"], marks["scentry"]),
              ("scentry>scsettled", marks["scentry"], marks["scsettled"]),
              ("scsettled>end", marks["scsettled"], vmax + 1)]
    print("=== reads per phase (count, total sectors, sectors*2048 bytes) ===")
    for name, lo, hi in bounds:
        rs = [r for r in reads if lo <= r["vsync"] < hi]
        sec = sum(r["sectors"] for r in rs)
        kinds = {}
        for r in rs:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        print("%s vsync=[%d,%d) n=%d sectors=%d bytes=%d kinds=%s" % (
            name, lo, hi, len(rs), sec, sec * 2048, kinds))
    print("=== distinct LBN ranges: menu>scentry + scentry>scsettled (transition) ===")
    tr = [r["lbn"] for r in reads if marks["menu"] <= r["vsync"] < marks["scsettled"]]
    rr = ranges(tr)
    print("transition reads=%d distinct_lbn=%d ranges=%d" % (len(tr), len(set(tr)), len(rr)))
    for a, b in rr:
        print("  %d..%d (%d sectors)" % (a, b, b - a + 1))
    print("=== distinct LBN ranges: scentry>end (SC on screen) ===")
    sc = [r["lbn"] for r in reads if r["vsync"] >= marks["scentry"]]
    rr = ranges(sc)
    print("sc reads=%d distinct_lbn=%d ranges=%d" % (len(sc), len(set(sc)), len(rr)))
    for a, b in rr:
        print("  %d..%d (%d sectors)" % (a, b, b - a + 1))
    print("=== whole boot: n=%d sectors=%d ===" % (len(reads), sum(r["sectors"] for r in reads)))


main()
