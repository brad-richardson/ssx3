#!/usr/bin/env python3
"""T47 Mission 2: extract the ENTER->panel loading window from T46 R3 trace.
One streaming pass over the SSD copy: verify sha256 (T46 committed
19c1b583...ae84), bucket lines with ts in [LO,HI] by channel, per-second
census of EE/IOP/CDVD/SIF + verbatim slices for the tail.
Usage: python3 t47-window.py TRACE LO HI OUTDIR
"""
import hashlib
import os
import re
import sys
from collections import Counter

TRACE, LO, HI, OUTDIR = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
os.makedirs(OUTDIR, exist_ok=True)
TS = re.compile(rb"^\[\s*(\d+\.\d+)\]")
EE = re.compile(rb"Bios call: (\S+) \((\S+)\)")
IOP = re.compile(rb"\b([a-z0-9_]+\.\d+): (\S+)")
CDVD = re.compile(rb"CDVD\s+:")

h = hashlib.sha256()
n = 0
sec_ee = Counter()
sec_iop = Counter()
sec_cdvd = Counter()
sec_sif = Counter()
sec_all = Counter()
slices = {}
cap = {"ee": 4000, "iop": 4000, "cdvd": 20000, "sif": 20000, "misc": 2000}
for k in cap:
    slices[k] = open(os.path.join(OUTDIR, f"win-{k}.txt"), "wb")
counts = Counter()

with open(TRACE, "rb") as f:
    for line in f:
        h.update(line)
        n += 1
        m = TS.match(line)
        if not m:
            continue
        ts = float(m.group(1))
        if ts < LO or ts > HI:
            continue
        sec = int(ts)
        sec_all[sec] += 1
        me = EE.search(line)
        if me:
            name = me.group(1).decode("ascii", "replace")
            sec_ee[(sec, name)] += 1
            if counts["ee"] < cap["ee"]:
                slices["ee"].write(b"%d %s" % (n, line))
                counts["ee"] += 1
            continue
        mi = IOP.search(line)
        if mi and b"Bios call" not in line:
            key = mi.group(1).decode("ascii", "replace") + ":" + mi.group(2).decode("ascii", "replace")
            sec_iop[(sec, key)] += 1
            if counts["iop"] < cap["iop"]:
                slices["iop"].write(b"%d %s" % (n, line))
                counts["iop"] += 1
            continue
        if CDVD.search(line):
            sec_cdvd[sec] += 1
            if counts["cdvd"] < cap["cdvd"]:
                slices["cdvd"].write(b"%d %s" % (n, line))
                counts["cdvd"] += 1
            continue
        if b"SIF" in line:
            sec_sif[sec] += 1
            if counts["sif"] < cap["sif"]:
                slices["sif"].write(b"%d %s" % (n, line))
                counts["sif"] += 1
            continue
        if counts["misc"] < cap["misc"]:
            slices["misc"].write(b"%d %s" % (n, line))
            counts["misc"] += 1

for k in slices:
    slices[k].close()

print("lines=%d sha=%s" % (n, h.hexdigest()))
print("win_lines=%d" % sum(sec_all.values()))
print("sec: total ee_top iop_top cdvd sif")
secs = sorted(sec_all)
for s in secs:
    ee = sorted(((c, k[1]) for (k, c) in sec_ee.items() if k[0] == s), reverse=True)[:4]
    io = sorted(((c, k[1]) for (k, c) in sec_iop.items() if k[0] == s), reverse=True)[:4]
    print("%d: n=%d ee=%s iop=%s cdvd=%d sif=%d" % (s, sec_all[s], ee, io, sec_cdvd[s], sec_sif[s]))
print("caps_hit=", dict(counts))
