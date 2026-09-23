#!/usr/bin/env python3
"""T59 analyze: first writers (vaddr/pc/ra/regs/vsync), timelines, ebwlast,
end-state dump, VU0/VIF0 counts.
"""
import re
import sys
from collections import defaultdict

EBW = re.compile(
    r"^ebw vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) "
    r"via=(store|spr-from|sif0|dma-ch7|dma-ch3) src=0x([0-9a-f]+) "
    r"vaddr=0x([0-9a-f]+) pc=0x([0-9a-f]+) ra=0x([0-9a-f]+) (a0=.*)$")
EBWLAST = re.compile(
    r"^ebwlast vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) "
    r"via=(store|spr-from|sif0|dma-ch7|dma-ch3) pc=0x([0-9a-f]+) ra=0x([0-9a-f]+)$")
EBWEND = re.compile(
    r"^ebwend vsync=(\d+) b0=(0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+) "
    r"b1=(0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+)$")
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
    path = sys.argv[1] if len(sys.argv) > 1 else "t59-trace.txt"
    ebw, last, end, calls, cen = [], [], [], [], []
    caps, caplast, t57cap, paths, wins = [], [], [], [], []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            m = (EBW.match(ln) or EBWLAST.match(ln) or EBWEND.match(ln)
                 or CALL.match(ln) or CENSUS.match(ln) or CAP.match(ln)
                 or CAPLAST.match(ln) or T57CAP.match(ln) or PATHS.match(ln)
                 or WIN.match(ln) or WCAP.match(ln))
            assert m is not None, "unparsed: %r" % ln[:150]
            if ln.startswith("ebw "):
                ebw.append(m)
            elif ln.startswith("ebwlast"):
                last.append(m)
            elif ln.startswith("ebwend"):
                end.append(m)
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
    print("rows: ebw=%d ebwlast=%d ebwend=%d T58_CAP=%d T58_CAPLAST=%d "
          "vu0call=%d vif0op=%d T57_CAP=%d PATHS=%d WINDOW=%d" % (
              len(ebw), len(last), len(end), len(caps), len(caplast),
              len(calls), len(cen), len(t57cap), len(paths), len(wins)))
    if pvs:
        print("paths span: vsync %d..%d (%d distinct)" % (pvs[0], pvs[-1], len(pvs)))
    evs = sorted(set(int(m.group(1)) for m in ebw)) if ebw else []
    if evs:
        print("ebw vsync span: %d..%d (%d distinct)" % (evs[0], evs[-1], len(evs)))

    print("--- Table 1: first writer of each word ---")
    seen = {}
    for idx, m in enumerate(ebw):
        if m.group(2) not in seen:
            seen[m.group(2)] = (idx, m)
    for w in sorted(seen, key=lambda x: int(x, 16)):
        idx, m = seen[w]
        print("addr=0x%s first=#%d vsync=%s value=0x%s via=%s src=0x%s vaddr=0x%s pc=0x%s ra=0x%s" % (
            w, idx, m.group(1), m.group(3), m.group(4), m.group(5), m.group(6),
            m.group(7), m.group(8)))
        print("  regs: %s" % m.group(9))

    print("--- Table 2: ebw by via + vaddr segments ---")
    byd = defaultdict(int)
    for m in ebw:
        byd[(m.group(4), m.group(6)[:4])] += 1
    for k in sorted(byd):
        print("via=%s vaddr-seg=0x%s n=%d" % (k[0], k[1], byd[k]))

    print("--- Table 3: ebwlast: distinct vsyncs + tail ---")
    byv = defaultdict(list)
    for m in last:
        byv[int(m.group(1))].append(m)
    print("ebwlast distinct vsyncs: %d (span %s..%s)" % (
        len(byv), min(byv) if byv else "-", max(byv) if byv else "-"))
    if byv:
        for m in sorted(byv[max(byv)], key=lambda m: int(m.group(2), 16)):
            print("last-vsync=%d addr=0x%s value=0x%s via=%s pc=0x%s ra=0x%s" % (
                max(byv), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)))

    print("--- Table 4: end-state dump ---")
    if not end:
        print("(none)")
    for m in end:
        print("vsync=%s b0=%s %s %s %s b1=%s %s %s %s" % (
            m.group(1), m.group(2), m.group(3), m.group(4), m.group(5),
            m.group(6), m.group(7), m.group(8), m.group(9)))

    print("--- Table 5: VU0/VIF0 ---")
    print("vu0call=%d vif0op-lines=%d T57_CAP=%d" % (len(calls), len(cen), len(t57cap)))
    print("T59_ANALYZE_DONE")


if __name__ == "__main__":
    main()
