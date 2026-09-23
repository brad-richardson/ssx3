#!/usr/bin/env python3
"""T47 Mission 2 (pass 2): dense loading-window timeline.
Streams the T46 R3 trace once; for ts in [LO,HI]:
 - per-0.5s census: EE top-6, IOP top-6, cdvd/sif/misc counts
 - verbatim: ALL ioman/sifcmd/cdvdman/libsd lines, ALL EE thread/sema-create
   lines, ALL LoadExecPS2/UpdateVSyncRate/WaitVblankStart/ERROR lines
Usage: python3 t47-window2.py TRACE LO HI OUTDIR
"""
import os
import re
import sys
from collections import Counter

TRACE, LO, HI, OUTDIR = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
os.makedirs(OUTDIR, exist_ok=True)
TS = re.compile(rb"^\[\s*(\d+\.\d+)\]")
EE = re.compile(rb"Bios call: (\S+) \((\S+)\)")
IOP = re.compile(rb"\b([a-z0-9_]+\.\d+): (\S+)")
KEY_IOP = (b"ioman.", b"sifcmd.", b"cdvdman.", b"libsd.")
KEY_EE = (b"CreateThread", b"StartThread", b"CreateSema", b"DeleteSema",
          b"LoadExecPS2", b"GetOsdConfigParam", b"SetOsdConfigParam")
KEY_MISC = (b"UpdateVSyncRate", b"WaitVblankStart", b"ERROR", b"ExecPS2",
            b"LoadStartModule", b"ReBootStart", b"Deci2Call", b"GetEntryAddress")

half_ee = Counter()
half_iop = Counter()
half_cdvd = Counter()
half_sif = Counter()
half_misc = Counter()
half_n = Counter()
fkey = open(os.path.join(OUTDIR, "win2-key.txt"), "wb")
n = 0
with open(TRACE, "rb") as f:
    for line in f:
        n += 1
        m = TS.match(line)
        if not m:
            continue
        ts = float(m.group(1))
        if ts < LO or ts > HI:
            continue
        h = int(ts * 2) / 2.0
        half_n[h] += 1
        me = EE.search(line)
        if me:
            name = me.group(1)
            half_ee[(h, name.decode("ascii", "replace"))] += 1
            if any(k in line for k in KEY_EE):
                fkey.write(b"%d %s" % (n, line))
            continue
        if b"CDVD    :" in line:
            half_cdvd[h] += 1
            continue
        if b"SIF     :" in line:
            half_sif[h] += 1
            continue
        mi = IOP.search(line)
        if mi and b"Bios    :" in line:
            key = (mi.group(1) + b":" + mi.group(2)).decode("ascii", "replace")
            half_iop[(h, key)] += 1
            if line.split(b"Bios    :")[1].lstrip()[:12].split(b".")[0] + b"." in KEY_IOP or \
               any(line.split(b"Bios    :")[1].lstrip().startswith(k) for k in KEY_IOP):
                fkey.write(b"%d %s" % (n, line))
            continue
        half_misc[h] += 1
        if any(k in line for k in KEY_MISC):
            fkey.write(b"%d %s" % (n, line))
fkey.close()
print("half: n ee_top6 iop_top6 cdvd sif misc")
for h in sorted(half_n):
    ee = sorted(((c, k[1]) for (k, c) in half_ee.items() if k[0] == h), reverse=True)[:6]
    io = sorted(((c, k[1]) for (k, c) in half_iop.items() if k[0] == h), reverse=True)[:6]
    print("%.1f: n=%d ee=%s" % (h, half_n[h], ee))
    print("    iop=%s cdvd=%d sif=%d misc=%d" % (io, half_cdvd[h], half_sif[h], half_misc[h]))
