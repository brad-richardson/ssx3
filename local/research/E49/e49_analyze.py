#!/usr/bin/env python3
"""E49 boot analyzer: the E48 predicted observables from one boot.

Usage: python3 local/research/E49/e49_analyze.py <label> [run_dir]

Reads <run>/boot-<label>-1.log(.gz) and <run>/park-<label>-1/park-snapshot.json.
Prints: park hot_pc counts for the codec/MPEG pcs, missing-target lines by
target, MPC CD reads (tick-stamped), the codec watch timeline for ticks
< 400 (alloc / release / close / open stores), and frame-hash runs.
"""

import collections
import gzip
import json
import os
import re
import sys

label = sys.argv[1]
run = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/dev/ssx3-work/E49/run")

PCS = [
    ("0x3b1050", "next-picture (vt+0x1c)"),
    ("0x402b38", "end check (sceMpegIsEnd shape)"),
    ("0x3b0fb8", "fetch (alloc + GetPicture)"),
    ("0x3b10d0", "alloc"),
    ("0x402a10", "sceMpegGetPicture"),
    ("0x3b0600", "picture fetch caller"),
    ("0x254c48", "SetPicture"),
    ("0x254dc0", "release caller"),
    ("0x3b0680", "release thunk"),
    ("0x3b1140", "release (breaker)"),
    ("0x3b0c58", "Open"),
    ("0x3b09a0", "Close"),
    ("0x3b0b40", "Open caller (Create/Init)"),
]

# Watch store pcs (E48 tables) -> event name.
WATCH_EVENTS = [
    ((0x3b10f8, 0x3b1130), "alloc"),
    ((0x3b1150, 0x3b1150), "release rc store"),
    ((0x3b116c, 0x3b1190), "release unlink/relink"),
    ((0x3b09a0, 0x3b0ad0), "close"),
    ((0x3b0908, 0x3b091c), "node dtor"),
    ((0x3b0820, 0x3b0860), "node ctor"),
    ((0x3b0e7c, 0x3b0e8c), "open push free"),
    ((0x3b0954, 0x3b0990), "codec ctor"),
    ((0x254c7c, 0x254c7c), "SetPicture holder+0xc"),
    ((0x254e08, 0x254e08), "holder+0xc=0"),
    ((0x3b103c, 0x3b103c), "count++"),
]


def open_log():
    p = os.path.join(run, f"boot-{label}-1.log")
    if os.path.exists(p):
        return open(p, "r", errors="replace")
    return gzip.open(p + ".gz", "rt", errors="replace")


park = json.load(open(os.path.join(run, f"park-{label}-1", "park-snapshot.json")))
hot = {h["pc"]: h for h in park.get("hot_pc", [])}
print(f"## {label}: park hot_pc")
print("| pc | role | count | first_ra | last_ra |")
print("|---|---|---|---|---|")
for pc, role in PCS:
    h = hot.get(pc)
    if h:
        print(f"| `{pc}` | {role} | {h['count']} | `{h.get('first_ra')}` | `{h.get('last_ra')}` |")
    else:
        print(f"| `{pc}` | {role} | 0 (absent) | | |")

tick = 0
max_tick = 0
missing = collections.Counter()
mpc = []
watch = []
frames = []
re_tick = re.compile(r"\[frame:dump\] seq=\d+ tick=(\d+) .*fnv1a=([0-9a-f]+)")
re_watch = re.compile(r"\[diag:watch\] addr=(0x[0-9a-f]+) width=\d+ value=(0x[0-9a-f]+) pc=(0x[0-9a-f]+)")
re_miss = re.compile(r"\[guest-branch:missing-target\].*? target=(0x[0-9a-f]+)")
re_cd = re.compile(r"\[diag:cd\] sceCdRead payload lbn=(0x[0-9a-f]+) .*bytes=4d504368")
lines = 0
with open_log() as f:
    for line in f:
        lines += 1
        m = re_tick.search(line)
        if m:
            tick = int(m.group(1))
            max_tick = max(max_tick, tick)
            frames.append((tick, m.group(2)))
            continue
        m = re_miss.search(line)
        if m:
            missing[m.group(1)] += 1
            continue
        m = re_cd.search(line)
        if m:
            mpc.append((tick, m.group(1)))
            continue
        m = re_watch.search(line)
        if m and tick < 400:
            pc = int(m.group(3), 16)
            for (lo, hi), name in WATCH_EVENTS:
                if lo <= pc <= hi:
                    watch.append((tick, name, m.group(1), m.group(2), m.group(3)))
                    break

print(f"\nlog lines {lines}, max frame tick {max_tick}")
print("\n## missing-target lines by target")
if not missing:
    print("none (0 lines)")
for t, n in sorted(missing.items()):
    print(f"- `{t}` x{n}")
print("\n## MPC CD reads (tick = last frame dump before the line)")
for t, lbn in mpc:
    print(f"- t{t} lbn `{lbn}`")

print("\n## codec watch timeline, ticks < 400 (collapsed per tick+event)")
agg = collections.OrderedDict()
for t, name, addr, val, pc in watch:
    agg.setdefault((t, name), []).append(f"{addr}={val}@{pc}")
for (t, name), items in agg.items():
    print(f"- t{t} {name}: {len(items)} store(s) [{', '.join(items[:4])}{' …' if len(items) > 4 else ''}]")

print("\n## frame-hash runs (first 40)")
runs = []
for t, h in frames:
    if runs and runs[-1][2] == h:
        runs[-1][1] = t
    else:
        runs.append([t, t, h])
for a, b_, h in runs[:40]:
    print(f"- t{a}..t{b_} `{h}`")
print(f"(total runs {len(runs)})")
