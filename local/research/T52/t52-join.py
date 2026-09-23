#!/usr/bin/env python3
# T52 join: attribute trace LBNs to ISO files; per-phase file table + CD-kind list.
# Usage: python3 t52-join.py <trace> <isomap>
import re
import sys

CDREAD = re.compile(
    r"T52_CDREAD seq=(\d+) vsync=(\d+) kind=(CD|DVD|CDDA) lbn=(\d+) sectors=(\d+) "
    r"blocksize=(\d+) speed=(\d+)x spindle=(CAV|CLV) readmode=(0x[0-9a-f]+) dest=-"
)
MARK = re.compile(r"T52_MARK vsync=(\d+) label=(title|menu|scentry|scsettled)")
ISOMAP = re.compile(r"lbn=(\d+) sectors=(\d+) size=(\d+) name=(.+)")


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
            elif MARK.search(line):
                m = MARK.search(line)
                marks[m.group(2)] = int(m.group(1))
    files = []
    with open(sys.argv[2]) as f:
        for line in f:
            m = ISOMAP.search(line)
            if m:
                files.append((int(m.group(1)), int(m.group(2)), m.group(4)))

    def owner(lbn):
        for ext, sec, name in files:
            if ext <= lbn < ext + sec:
                return "%s+%d" % (name, lbn - ext)
        return "UNMAPPED"

    vmax = max([r["vsync"] for r in reads] + list(marks.values()))
    phases = [("boot>title", 0, marks["title"]), ("title>menu", marks["title"], marks["menu"]),
              ("menu>scentry", marks["menu"], marks["scentry"]),
              ("scentry>scsettled", marks["scentry"], marks["scsettled"]),
              ("scsettled>end", marks["scsettled"], vmax + 1)]
    print("=== per-phase file attribution (sectors per file) ===")
    for name, lo, hi in phases:
        rs = [r for r in reads if lo <= r["vsync"] < hi]
        byfile = {}
        for r in rs:
            for s in range(r["sectors"]):
                o = owner(r["lbn"] + s).split("+")[0]
                byfile[o] = byfile.get(o, 0) + 1
        print("%s n=%d:" % (name, len(rs)))
        for fn, sec in sorted(byfile.items(), key=lambda kv: -kv[1])[:12]:
            print("  %d %s" % (sec, fn))
    print("=== CD-kind reads (all) ===")
    for r in reads:
        if r["kind"] != "DVD":
            print("seq=%d vsync=%d kind=%s lbn=%d sectors=%d bs=%d speed=%d %s %s owner=%s" % (
                r["seq"], r["vsync"], r["kind"], r["lbn"], r["sectors"], r["bs"],
                r["speed"], r["spindle"], r["mode"], owner(r["lbn"])))
    print("=== mode/speed census ===")
    cens = {}
    for r in reads:
        k = (r["kind"], r["bs"], r["speed"], r["spindle"], r["mode"])
        cens[k] = cens.get(k, 0) + 1
    for k, n in sorted(cens.items(), key=lambda kv: -kv[1]):
        print("%s n=%d" % (k, n))


main()
