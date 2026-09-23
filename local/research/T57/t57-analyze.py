#!/usr/bin/env python3
"""T57 analyze: VU0 calls by startPC (cycle stats, vi1/vi2) + VIF0 census.

Reads a t57-extract.sh trace. Handles the empty case (reports bounds).
"""
import re
import sys
from collections import defaultdict

CALL = re.compile(
    r"^vu0call vsync=(\d+) caller_pc=0x([0-9a-f]+) via=(cop2|vif0|unknown) "
    r"startPC=0x([0-9a-f]+) cycles=(\d+) vi1=0x([0-9a-f]+) vi2=0x([0-9a-f]+)"
    r"( ms=0x([0-9a-f]+))?( mark=sub_0037D968)?( end=abort)?$")
CENSUS = re.compile(r"^vif0op vsync=(\d+) op=([A-Z]+) n=(\d+)$")
CAP = re.compile(r"^T57_CAP vsync=(\d+)$")
PATHS = re.compile(r"^T48_PATHS vsync=(\d+) ")
WIN = re.compile(r"^T51C_WINDOW vsync=(\d+)$")
WCAP = re.compile(r"^T51C_CAP vsync=(\d+)$")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "t57a-trace.txt"
    calls, census, caps, paths, wins = [], [], [], [], []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            m = (CALL.match(ln) or CENSUS.match(ln) or CAP.match(ln)
                 or PATHS.match(ln) or WIN.match(ln) or WCAP.match(ln))
            assert m is not None, "unparsed: %r" % ln[:120]
            if ln.startswith("vu0call"):
                calls.append(m)
            elif ln.startswith("vif0op"):
                census.append(m)
            elif ln.startswith("T57_CAP"):
                caps.append(m)
            elif ln.startswith("T48_PATHS"):
                paths.append(m)
            else:
                wins.append(m)
    pvs = sorted(int(m.group(1)) for m in paths)
    print("rows: vu0call=%d vif0op=%d T57_CAP=%d T48_PATHS=%d WINDOW=%d" %
          (len(calls), len(census), len(caps), len(paths), len(wins)))
    if pvs:
        print("paths span: vsync %d..%d (%d vsyncs)" % (pvs[0], pvs[-1], len(pvs)))

    print("--- Table 1: VU0 calls by startPC ---")
    bypc = defaultdict(list)
    for m in calls:
        bypc[int(m.group(4), 16)].append(m)
    if not bypc:
        print("(empty: 0 VU0 micro-program starts in-window)")
    for pc in sorted(bypc):
        rows = bypc[pc]
        cyc = sorted(int(m.group(5)) for m in rows)
        vi1 = sorted(set(m.group(6) for m in rows))
        vi2 = sorted(set(m.group(7) for m in rows))
        vias = sorted(set(m.group(3) for m in rows))
        ms = sorted(set(m.group(8) for m in rows if m.group(8)))
        aborts = sum(1 for m in rows if m.group(10))
        marks = sum(1 for m in rows if m.group(9))
        print("startPC=0x%x n=%d vias=%s cycles[min/med/max]=%d/%d/%d "
              "vi1#=%d vi2#=%d ms=%s aborts=%d marks=%d" % (
                  pc, len(rows), ",".join(vias), cyc[0], cyc[len(cyc) // 2],
                  cyc[-1], len(vi1), len(vi2), ",".join(ms) or "-", aborts, marks))

    print("--- Table 2: VIF0 opcodes per vsync ---")
    byvs = defaultdict(lambda: defaultdict(int))
    for m in census:
        byvs[int(m.group(1))][m.group(2)] += int(m.group(3))
    if not byvs:
        print("(empty: 0 VIF0 command words in-window)")
    for vs in sorted(byvs):
        tot = sum(byvs[vs].values())
        ops = " ".join("%s=%d" % kv for kv in sorted(byvs[vs].items()))
        print("vsync=%d total=%d %s" % (vs, tot, ops))

    print("--- join keys ---")
    print("unknown-via=%d abort=%d mark37deb8=%d caps=%s" % (
        sum(1 for m in calls if m.group(3) == "unknown"),
        sum(1 for m in calls if m.group(10)),
        sum(1 for m in calls if m.group(9)),
        ",".join(m.group(1) for m in caps) or "-"))
    print("T57_ANALYZE_DONE")


if __name__ == "__main__":
    main()
