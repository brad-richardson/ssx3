#!/usr/bin/env python3
"""T58 analyze: first writers per word, value timelines, ebwlast summary,
VU0/VIF0 counts, window spans. Handles empty and non-empty cases.
"""
import re
import sys
from collections import defaultdict

EBW = re.compile(
    r"^ebw vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) "
    r"via=(store|spr-from|sif0|dma-ch7|dma-ch3) src=0x([0-9a-f]+) "
    r"pc=0x([0-9a-f]+) ra=0x([0-9a-f]+) (a0=.*)$")
EBWLAST = re.compile(
    r"^ebwlast vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) "
    r"via=(store|spr-from|sif0|dma-ch7|dma-ch3) pc=0x([0-9a-f]+) ra=0x([0-9a-f]+)$")
CALL = re.compile(
    r"^vu0call vsync=(\d+) caller_pc=0x([0-9a-f]+) via=(cop2|vif0|unknown) "
    r"startPC=0x([0-9a-f]+) cycles=(\d+) vi1=0x([0-9a-f]+) vi2=0x([0-9a-f]+)"
    r"( ms=0x([0-9a-f]+))?( mark=sub_0037D968)?( end=abort)?$")
CENSUS = re.compile(r"^vif0op vsync=(\d+) op=([A-Z]+) n=(\d+)$")
CAP = re.compile(r"^T58_CAP vsync=(\d+) addr=0x([0-9a-f]+)$")
CAPLAST = re.compile(r"^T58_CAPLAST vsync=(\d+)$")
T57CAP = re.compile(r"^T57_CAP vsync=(\d+)$")
PATHS = re.compile(r"^T48_PATHS vsync=(\d+) ")
WIN = re.compile(r"^T51C_WINDOW vsync=(\d+)$")
WCAP = re.compile(r"^T51C_CAP vsync=(\d+)$")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "t58-trace.txt"
    ebw, last, calls, cen = [], [], [], []
    caps, caplast, t57cap, paths, wins = [], [], [], [], []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            m = (EBW.match(ln) or EBWLAST.match(ln) or CALL.match(ln)
                 or CENSUS.match(ln) or CAP.match(ln) or CAPLAST.match(ln)
                 or T57CAP.match(ln) or PATHS.match(ln) or WIN.match(ln)
                 or WCAP.match(ln))
            assert m is not None, "unparsed: %r" % ln[:140]
            if ln.startswith("ebw "):
                ebw.append(m)
            elif ln.startswith("ebwlast"):
                last.append(m)
            elif ln.startswith("vu0call"):
                calls.append(m)
            elif ln.startswith("vif0op"):
                cen.append(m)
            elif ln.startswith("T58_CAP "):
                caps.append(m)
            elif ln.startswith("T58_CAPLAST"):
                caplast.append(m)
            elif ln.startswith("T57_CAP"):
                t57cap.append(m)
            elif ln.startswith("T48_PATHS"):
                paths.append(m)
            else:
                wins.append(m)
    pvs = sorted(set(int(m.group(1)) for m in paths))
    print("rows: ebw=%d ebwlast=%d T58_CAP=%d T58_CAPLAST=%d vu0call=%d "
          "vif0op=%d T57_CAP=%d PATHS=%d WINDOW=%d" % (
              len(ebw), len(last), len(caps), len(caplast), len(calls),
              len(cen), len(t57cap), len(paths), len(wins)))
    if pvs:
        print("paths span: vsync %d..%d (%d distinct)" % (pvs[0], pvs[-1], len(pvs)))
    evs = sorted(set(int(m.group(1)) for m in ebw)) if ebw else []
    if evs:
        print("ebw vsync span: %d..%d (%d distinct)" % (evs[0], evs[-1], len(evs)))

    print("--- Table 1: first writer of each word ---")
    seen = {}
    for idx, m in enumerate(ebw):
        w = m.group(2)
        if w not in seen:
            seen[w] = (idx, m)
    if not seen:
        print("(empty: no writes to any watched word)")
    for w in sorted(seen, key=lambda x: int(x, 16)):
        idx, m = seen[w]
        print("addr=0x%s first=#%d vsync=%s value=0x%s via=%s src=0x%s pc=0x%s ra=0x%s" % (
            w, idx, m.group(1), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7)))

    print("--- Table 2: value timeline per word (vsync:value:via ...) ---")
    if not ebw:
        print("(empty)")
    byw = defaultdict(list)
    for m in ebw:
        byw[m.group(2)].append(m)
    for w in sorted(byw, key=lambda x: int(x, 16)):
        tl = " ".join("%s:0x%s:%s" % (m.group(1), m.group(3), m.group(4)) for m in byw[w])
        print("addr=0x%s n=%d %s" % (w, len(byw[w]), tl))

    print("--- Table 3: ebwlast (per-vsync last writer) ---")
    if not last:
        print("(empty)")
    byv = defaultdict(list)
    for m in last:
        byv[int(m.group(1))].append(m)
    for vs in sorted(byv):
        for m in sorted(byv[vs], key=lambda m: int(m.group(2), 16)):
            print("vsync=%d addr=0x%s value=0x%s via=%s pc=0x%s ra=0x%s" % (
                vs, m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)))
    print("ebwlast distinct vsyncs: %d" % len(byv))

    print("--- Table 4: VU0/VIF0 in window ---")
    print("vu0call=%d vif0op-lines=%d (total cmds=%d) T57_CAP=%d" % (
        len(calls), len(cen), sum(int(m.group(3)) for m in cen), len(t57cap)))
    byop = defaultdict(int)
    for m in cen:
        byop[m.group(2)] += int(m.group(3))
    if byop:
        print("vif0 ops: " + " ".join("%s=%d" % kv for kv in sorted(byop.items())))
    byd = defaultdict(list)
    for m in ebw:
        byd[m.group(4)].append(m)
    if byd:
        print("ebw by via: " + " ".join("%s=%d" % (k, len(v)) for k, v in sorted(byd.items())))
    print("T58_ANALYZE_DONE")


if __name__ == "__main__":
    main()
