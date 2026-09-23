#!/usr/bin/env python3
"""T60 analyze: app table (first 40 + count resets), tpl-before-reset with
setters per mode value, template constancy, end state.
"""
import re
import sys
from collections import defaultdict

APP = re.compile(
    r"^app vsync=(\d+) count=(\d+) t0=0x([0-9a-f]+) tw0=0x([0-9a-f]+) "
    r"tw1=0x([0-9a-f]+) tw2=0x([0-9a-f]+) tw3=0x([0-9a-f]+) tw4=0x([0-9a-f]+) "
    r"s4=0x([0-9a-f]+) t1=0x([0-9a-f]+) ra=0x([0-9a-f]+)$")
TPL = re.compile(
    r"^tpl vsync=(\d+) addr=0x([0-9a-f]+) old=0x([0-9a-f]+) new=0x([0-9a-f]+) "
    r"pc=0x([0-9a-f]+) ra=0x([0-9a-f]+) a0=.*$")
TPLREARM = re.compile(r"^tplrearm vsync=(\d+) old=0x([0-9a-f]+) new=0x([0-9a-f]+)$")
CAPAPP = re.compile(r"^T60_CAPAPP vsync=(\d+)$")
CAPTPL = re.compile(r"^T60_CAPTPL vsync=(\d+)$")
EBWEND = re.compile(
    r"^ebwend vsync=(\d+) b0=(0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+) "
    r"b1=(0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+) (0x[0-9a-f]+)$")
PATHS = re.compile(r"^T48_PATHS vsync=(\d+) ")
WIN = re.compile(r"^T51C_WINDOW vsync=(\d+)$")
WCAP = re.compile(r"^T51C_CAP vsync=(\d+)$")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "t60-trace.txt"
    apps, tpls, rearms, end = [], [], [], []
    capapp, captpl, paths, wins = [], [], [], []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            m = (APP.match(ln) or TPL.match(ln) or TPLREARM.match(ln)
                 or CAPAPP.match(ln) or CAPTPL.match(ln) or EBWEND.match(ln)
                 or PATHS.match(ln) or WIN.match(ln) or WCAP.match(ln)
                 or (ln.startswith("ebw") or ln.startswith("ebwlast")
                     or ln.startswith("T58_") or ln.startswith("vu0call")
                     or ln.startswith("vif0op") or ln.startswith("T57_CAP")) and "SKIP")
            if m == "SKIP":
                continue
            assert m is not None, "unparsed: %r" % ln[:150]
            if ln.startswith("app "):
                apps.append(m)
            elif ln.startswith("tpl "):
                tpls.append(m)
            elif ln.startswith("tplrearm"):
                rearms.append(m)
            elif ln.startswith("T60_CAPAPP"):
                capapp.append(m)
            elif ln.startswith("T60_CAPTPL"):
                captpl.append(m)
            elif ln.startswith("ebwend"):
                end.append(m)
            elif ln.startswith("T48_PATHS"):
                paths.append(m)
            else:
                wins.append(m)
    pvs = sorted(set(int(m.group(1)) for m in paths))
    print("rows: app=%d tpl=%d tplrearm=%d CAPAPP=%d CAPTPL=%d ebwend=%d PATHS=%d WINDOW=%d" % (
        len(apps), len(tpls), len(rearms), len(capapp), len(captpl),
        len(end), len(paths), len(wins)))
    if pvs:
        print("paths span: vsync %d..%d (%d distinct)" % (pvs[0], pvs[-1], len(pvs)))
    avs = sorted(set(int(m.group(1)) for m in apps))
    print("app vsync span: %d..%d (%d distinct)" % (avs[0], avs[-1], len(avs)))
    tvs = sorted(set(int(m.group(1)) for m in tpls)) if tpls else []
    if tvs:
        print("tpl vsync span: %d..%d (%d distinct)" % (tvs[0], tvs[-1], len(tvs)))

    print("--- Table 1: app first 40 (count, tw0, ra) ---")
    for i, m in enumerate(apps[:40]):
        print("#%d vsync=%s count=%s t0=0x%s tw0=0x%s tw1=0x%s s4=0x%s t1=0x%s ra=0x%s" % (
            i, m.group(1), m.group(2), m.group(3), m.group(4), m.group(5),
            m.group(9), m.group(10), m.group(11)))
    counts = [int(m.group(2)) for m in apps]
    print("count: min=%d max=%d distinct=%d" % (min(counts), max(counts), len(set(counts))))
    resets = [i for i in range(1, len(counts)) if counts[i] == 0 and counts[i - 1] != 0]
    print("count resets to 0 at app#=%s (n=%d)" % (resets[:20], len(resets)))
    print("ra distinct: %s" % sorted(set(m.group(11) for m in apps)))
    print("ra in-append-range-379784-379820: %s" % any(
        0x379784 <= int(m.group(11), 16) <= 0x379820 for m in apps))
    print("t0 distinct: %s" % sorted(set(m.group(3) for m in apps)))

    print("--- Table 2: tpl tw0/tw1 change sequence (first 60) ---")
    for m in tpls[:60]:
        print("vsync=%s addr=0x%s old=0x%s new=0x%s pc=0x%s ra=0x%s" % (
            m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)))
    print("--- tpl setter pcs per new mode value (tw0/tw1) ---")
    t0p = None
    if apps:
        t0v = int(apps[0].group(3), 16)
        if (t0v >> 24) in (0x00, 0x20, 0x30, 0x80, 0xA0) and (t0v & 0xFFFFFF) < 0x2000000:
            t0p = t0v & 0x1FFFFFF
    print("template t0p=0x%x" % t0p if t0p is not None else "template t0p=UNFOLDED")
    bymode = defaultdict(lambda: defaultdict(int))
    bypc = defaultdict(lambda: defaultdict(int))
    for m in tpls:
        if t0p is None:
            idx = "tw?"
        else:
            idx = "tw%d" % ((int(m.group(2), 16) - t0p) // 4)
        bymode[(idx, m.group(4))][m.group(5)] += 1
        bypc[m.group(5)][m.group(6)] += 1
    for k in sorted(bymode):
        pcs = " ".join("pc=0x%s x%d" % (pc, n) for pc, n in sorted(bymode[k].items()))
        print("%s new=0x%s: %s" % (k[0], k[1], pcs))
    print("--- tpl setter pc -> ra ---")
    for pc in sorted(bypc):
        ras = " ".join("ra=0x%s x%d" % (ra, n) for ra, n in sorted(bypc[pc].items()))
        print("pc=0x%s: %s" % (pc, ras))

    print("--- Table 3: list restarts (count=1; no count=0 exists) + preceding tpl ---")
    starts = [i for i, c in enumerate(counts) if c == 1]
    print("count=1 at app#=%s (n=%d)" % (starts[:16], len(starts)))
    missing = [v for v in range(min(counts), max(counts) + 1)
               if v not in set(counts)]
    print("missing counts (no app row): %s" % missing)
    print("tw0 by count:")
    tw0by = defaultdict(set)
    for m in apps:
        tw0by[int(m.group(2))].add(m.group(4))
    for c in sorted(tw0by):
        print("  count=%d tw0=%s" % (c, ",".join(sorted(tw0by[c]))))
    if starts:
        r0 = starts[1] if len(starts) > 1 else starts[0]
        avo = int(apps[r0].group(1))
        print("first restart at app#=%d (vsync=%s s4=0x%s); tpl at vsync<=%s (last 15):" % (
            r0, apps[r0].group(1), apps[r0].group(9), avo))
        pre = [m for m in tpls if int(m.group(1)) <= avo][-15:]
        for m in pre:
            print("vsync=%s addr=0x%s old=0x%s new=0x%s pc=0x%s ra=0x%s" % (
                m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)))
    print("--- end state ---")
    for m in end:
        print("vsync=%s b0=%s %s %s %s b1=%s %s %s %s" % (
            m.group(1), m.group(2), m.group(3), m.group(4), m.group(5),
            m.group(6), m.group(7), m.group(8), m.group(9)))
    print("T60_ANALYZE_DONE")


if __name__ == "__main__":
    main()
