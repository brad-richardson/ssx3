#!/usr/bin/env python3
"""T47 Mission 2 (pass 3): full ENTER->race timeline aggregates.
Streams trace once; for ts in [LO,HI], 5s blocks:
 - key IOP (ioman/sifcmd/cdvdman/libsd): count + first-3 full lines
 - EE thread/sema create/delete/start: count + first-3 full lines
 - VSync/ERROR/ExecPS2/WaitVblankStart: ALL verbatim
Usage: python3 t47-window3.py TRACE LO HI OUTDIR
"""
import os
import re
import sys
from collections import Counter, defaultdict

TRACE, LO, HI, OUTDIR = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
os.makedirs(OUTDIR, exist_ok=True)
TS = re.compile(rb"^\[\s*(\d+\.\d+)\]")
EE = re.compile(rb"Bios call: (\S+) \((\S+)\)")
KEY_IOP_PREFIX = (b"ioman.", b"sifcmd.", b"cdvdman.", b"libsd.")
KEY_EE_NAMES = (b"CreateThread", b"StartThread", b"CreateSema", b"DeleteSema",
                b"LoadExecPS2", b"ExitDeleteThread", b"WakeupThread")
KEY_VERBATIM = (b"UpdateVSyncRate", b"ERROR", b"ExecPS2", b"WaitVblankStart",
                b"LoadStartModule", b"ReBootStart", b"Deci2Call")

agg = Counter()
samp = defaultdict(list)
fverb = open(os.path.join(OUTDIR, "win3-verbatim.txt"), "wb")
fkey = open(os.path.join(OUTDIR, "win3-keyagg.txt"), "wb")
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
        blk = int(ts // 5) * 5
        if any(k in line for k in KEY_VERBATIM):
            fverb.write(b"%d %s" % (n, line))
        me = EE.search(line)
        if me:
            if me.group(1) in KEY_EE_NAMES:
                k = b"EE:" + me.group(1)
                agg[(blk, k)] += 1
                if len(samp[(blk, k)]) < 3:
                    samp[(blk, k)].append(b"%d %s" % (n, line))
            continue
        if b"Bios    :" in line:
            rest = line.split(b"Bios    :")[1].lstrip()
            if rest[:6] in (b"ioman.", b"sifcmd", b"cdvdma", b"libsd."):
                name = rest.split(b" ")[0]
                k = b"IOP:" + name
                agg[(blk, k)] += 1
                if len(samp[(blk, k)]) < 3:
                    samp[(blk, k)].append(b"%d %s" % (n, line))
            continue
for (blk, k) in sorted(agg):
    fkey.write(b"blk=%d %s count=%d\n" % (blk, k, agg[(blk, k)]))
    for s in samp[(blk, k)]:
        fkey.write(b"    %s" % s)
fkey.close()
fverb.close()
print("blocks=%d keys=%d" % (len({b for (b, k) in agg}), len(agg)))
