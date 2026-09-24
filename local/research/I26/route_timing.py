#!/usr/bin/env python3
"""I26: route timing from a boot log with PS2X_FRAME_DUMP_DIR set.

Reads '[frame:dump] seq= tick= ... fnv1a=' (one per host upload) and
'[padscript] press/release' lines, in log order. Prints:
  - presses: index, button, guest ms, tick (ms*5994/100000)
  - hash runs: maximal tick spans whose frame hash stays constant for
    >= --min-run ticks (a static screen), plus 'moving' spans between.
Usage: route_timing.py boot.log [--min-run 30] [--from T] [--to T]
"""
import argparse, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--min-run", type=int, default=30)
ap.add_argument("--from", dest="t0", type=int, default=0)
ap.add_argument("--to", dest="t1", type=int, default=1 << 40)
a = ap.parse_args()

FD = re.compile(r"\[frame:dump\] seq=(\d+) tick=(\d+) size=(\d+)x(\d+) .*fallback=(\d) fnv1a=([0-9a-f]+)")
PR = re.compile(r"\[padscript\] press i=(\d+) now=(\d+)ms at=(\d+)ms hold=(\d+)ms buttons=0x([0-9a-f]+)")
RL = re.compile(r"\[padscript\] release i=(\d+) now=(\d+)ms")
BTN = {0x0008: "start", 0x4000: "cross", 0x0040: "down", 0x0010: "up", 0x2000: "circle", 0x1000: "triangle", 0x8000: "square"}

frames, events = [], []
for line in open(a.log, errors="replace"):
    m = FD.search(line)
    if m:
        frames.append((int(m.group(2)), m.group(6), int(m.group(5))))
        continue
    m = PR.search(line)
    if m:
        ms = int(m.group(2)); b = int(m.group(5), 16)
        events.append(("press", int(m.group(1)), ms, ms * 5994 // 100000, BTN.get(b, hex(b)), int(m.group(4))))
        continue
    m = RL.search(line)
    if m:
        ms = int(m.group(2))
        events.append(("release", int(m.group(1)), ms, ms * 5994 // 100000, "", 0))

print("# presses")
for e in events:
    if e[0] == "press":
        print(f"press i={e[1]:2d} {e[4]:6s} ms={e[2]:6d} tick={e[3]:5d} hold={e[5]}")

print(f"# hash runs (>= {a.min_run} ticks constant), frames={len(frames)}")
runs, cur = [], None
for t, h, fb in frames:
    if not (a.t0 <= t <= a.t1):
        continue
    if cur and cur[2] == h:
        cur[1] = t
    else:
        if cur: runs.append(cur)
        cur = [t, t, h, fb]
if cur: runs.append(cur)
prev_end = None
for s, e, h, fb in runs:
    if e - s + 1 >= a.min_run:
        if prev_end is not None and s - prev_end > 1:
            print(f"  moving {prev_end + 1:5d}-{s - 1:5d}")
        print(f"  static {s:5d}-{e:5d} ({e - s + 1:4d} ticks) {h}{' FALLBACK' if fb else ''}")
        prev_end = e
if prev_end is not None and runs and runs[-1][1] > prev_end:
    print(f"  moving {prev_end + 1:5d}-{runs[-1][1]:5d}")
