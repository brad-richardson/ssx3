#!/usr/bin/env python3
"""T47 Mission 2 (pass 4): verbatim tail [LO,HI], noise-filtered.
Keep: ioman/sifcmd/sifman/cdvdman/libsd(non-010) IOP, EE thread/sema
create/delete/start, VSync/ERROR/ExecPS2; sample SIF every 50th, CDVD
every 20th. Drop intrman/thevent/timrman/thbase/libsd.010/GetThreadId/
WaitSema/SignalSema/ReferThreadStatus/RotateThreadReadyQueue/iSignalSema.
Usage: python3 t47-tail.py TRACE LO HI OUTFILE
"""
import re
import sys

TRACE, LO, HI, OUT = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
TS = re.compile(rb"^\[\s*(\d+\.\d+)\]")
KEEP_IOP = (b"ioman.", b"sifcmd.", b"sifman.", b"cdvdman.", b"libsd.")
DROP_LIBSD010 = b"libsd.010:"
KEEP_EE = (b"CreateThread", b"StartThread", b"CreateSema", b"DeleteSema",
           b"LoadExecPS2", b"SleepThread", b"WakeupThread", b"DelayThread",
           b"SuspendThread", b"ResumeThread", b"TerminateThread")
KEEP_MISC = (b"UpdateVSyncRate", b"ERROR", b"ExecPS2", b"WaitVblankStart",
             b"LoadStartModule", b"ReBootStart", b"Deci2Call", b"GetEntryAddress",
             b"SYSTEM.CNF", b"cdvdLoadElf", b"Initializing Elf", b"Disc changed")

sif_n = cdvd_n = 0
kept = 0
with open(TRACE, "rb") as f, open(OUT, "wb") as o:
    for line in f:
        m = TS.match(line)
        if not m:
            continue
        ts = float(m.group(1))
        if ts < LO or ts > HI:
            continue
        if b"Bios call:" in line:
            if any(k in line for k in KEEP_EE):
                o.write(line)
                kept += 1
            continue
        if b"CDVD    :" in line:
            cdvd_n += 1
            if cdvd_n % 20 == 0:
                o.write(line)
                kept += 1
            continue
        if b"SIF     :" in line:
            sif_n += 1
            if sif_n % 50 == 0:
                o.write(line)
                kept += 1
            continue
        if b"Bios    :" in line:
            rest = line.split(b"Bios    :")[1].lstrip()
            if rest[:6] in (b"ioman.", b"sifcmd", b"sifman", b"cdvdma", b"libsd."):
                if DROP_LIBSD010 in line:
                    continue
                o.write(line)
                kept += 1
            continue
        if any(k in line for k in KEEP_MISC):
            o.write(line)
            kept += 1
print("kept=%d sif_total=%d cdvd_total=%d" % (kept, sif_n, cdvd_n))
