#!/usr/bin/env python3
"""AU1: attribute PS2X_CD_READ_TRACE lines to ISO files (iso-lbn-map.txt).
Usage: au1_cdfiles.py <cdread.txt> <iso-lbn-map.txt>  -> per-file table."""
import bisect, re, sys, collections
spans = []
for ln in open(sys.argv[2]):
    l, n, s, p = ln.split(None, 3); spans.append((int(l, 16), int(n), p.strip()))
starts = [s[0] for s in spans]
def owner(lbn):
    i = bisect.bisect_right(starts, lbn) - 1
    if i >= 0 and lbn < spans[i][0] + max(spans[i][1], 1): return spans[i][2]
    return "(no file)"
agg = collections.OrderedDict(); other = collections.Counter()
for ln in open(sys.argv[1]):
    m = re.search(r"vsync=(\d+) lbn=0x([0-9a-f]+) sectors=(\d+) mode=(\S+)", ln)
    if not m:
        other[ln.split()[0] if ln.split() else ""] += 1; continue
    v, lbn, n, mode = int(m[1]), int(m[2], 16), int(m[3]), m[4]
    f = owner(lbn)
    a = agg.setdefault(f, {"reads": 0, "sectors": 0, "first": v, "last": v, "modes": collections.Counter()})
    a["reads"] += 1; a["sectors"] += n; a["last"] = v; a["modes"][mode] += 1
print("| File | Reads | Sectors | MiB | First vsync | Last vsync | Modes |")
print("| --- | ---: | ---: | ---: | ---: | ---: | --- |")
for f, a in sorted(agg.items(), key=lambda kv: kv[1]["first"]):
    print(f"| `{f}` | {a['reads']} | {a['sectors']} | {a['sectors']*2048/2**20:.2f} | {a['first']} | {a['last']} | "
          + ", ".join(f"{k} {c}" for k, c in a["modes"].items()) + " |")
if other: print("\nnon-read lines:", dict(other))
