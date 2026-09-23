#!/usr/bin/env python3
"""Compress a T47 tail file into run-length rows:
ts_first ts_last count line-signature (args beyond the call name collapsed
to a stable signature: identical full line = same run).
Usage: python3 t47-runs.py TAILFILE
"""
import re
import sys

TS = re.compile(rb"^\[\s*(\d+\.\d+)\]")
rows = []
cur = None
for raw in open(sys.argv[1], "rb"):
    line = raw.rstrip(b"\n")
    m = TS.match(line)
    ts = float(m.group(1)) if m else -1.0
    body = line[m.end():] if m else line
    # signature: channel + call name + first arg (mode/id), rest collapsed
    sig = re.sub(rb"0x[0-9a-fA-F]+", b"H", body)
    sig = re.sub(rb"\b[0-9a-fA-F]{5,}\b", b"H", sig)
    if cur and cur[2] == sig:
        cur[1] = ts
        cur[3] += 1
    else:
        if cur:
            rows.append(cur)
        cur = [ts, ts, sig, 1]
if cur:
    rows.append(cur)
for (a, b, sig, c) in rows:
    print("%.4f %.4f %6d %s" % (a, b, c, sig.decode("ascii", "replace")))
