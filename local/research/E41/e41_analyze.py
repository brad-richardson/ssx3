#!/usr/bin/env python3
"""E41 analyzer: phase tables + LBN ranges + file names + plant attribution.

Usage:
  python3 local/research/E41/e41_analyze.py ~/dev/ssx3-work/E41-run/cdread-e41a.txt

Phase anchors from the E33 vsync route (guest ms -> tick = ms*5994/100000):
  title [0,620): boot to start press @10350ms
  main menu [620,1238): start to cross#1 @20650ms
  ->SC [1238,1360): cross#1 to SC-settled snap (~tick 1350-1379, E33a/E40)
  SC settled [1360,inf)
"""

import re
import sys
from collections import defaultdict

PHASES = [
    ("title", 0, 620),
    ("main menu", 620, 1238),
    ("-> Select Character", 1238, 1360),
    ("SC settled", 1360, 10**18),
]

CDREAD = re.compile(
    r"^cdread seq=(\d+) vsync=(\d+) lbn=0x([0-9a-f]+) sectors=(\d+) "
    r"mode=(\S+) dest=0x([0-9a-f]+) file=(\S+)\s*$")
CDSEARCH = re.compile(
    r"^cdsearch vsync=(\d+) name=(\S+) lbn=0x([0-9a-f]+) size=(\d+)\s*$")
CDOPEN = re.compile(
    r"^cdopen vsync=(\d+) name=(\S+) host=(\S+) fd=(-?\d+)\s*$")
FIOREAD = re.compile(
    r"^fioread vsync=(\d+) fd=(-?\d+) buf=0x([0-9a-f]+) bytes=(\d+) name=(\S+)\s*$")
PLANT = re.compile(
    r"^plant vsync=(\d+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+) "
    r"via=(\S+) src=(\S+) seq=(\S+)\s*$")


def phase_of(vsync):
    for name, lo, hi in PHASES:
        if lo <= vsync < hi:
            return name
    return "?"


def main(path):
    reads = []
    searches = []
    opens = []
    fioreads = []
    plants = []
    other = 0
    with open(path, errors="replace") as f:
        for line in f:
            m = CDREAD.match(line)
            if m:
                reads.append((int(m.group(1)), int(m.group(2)),
                              int(m.group(3), 16), int(m.group(4)),
                              m.group(5), int(m.group(6), 16), m.group(7)))
                continue
            m = CDSEARCH.match(line)
            if m:
                searches.append((int(m.group(1)), m.group(2),
                                 int(m.group(3), 16), int(m.group(4))))
                continue
            m = CDOPEN.match(line)
            if m:
                opens.append((int(m.group(1)), m.group(2), m.group(3),
                              int(m.group(4))))
                continue
            m = FIOREAD.match(line)
            if m:
                fioreads.append((int(m.group(1)), int(m.group(2)),
                                 int(m.group(3), 16), int(m.group(4)),
                                 m.group(5)))
                continue
            m = PLANT.match(line)
            if m:
                plants.append((int(m.group(1)), m.group(2), m.group(3),
                               m.group(4), m.group(5), m.group(6)))
                continue
            if line.strip():
                other += 1

    print(f"== {path}: {len(reads)} cdread, {len(searches)} cdsearch, "
          f"{len(opens)} cdopen, {len(fioreads)} fioread, "
          f"{len(plants)} plant, {other} other = "
          f"{len(reads)+len(searches)+len(opens)+len(fioreads)+len(plants)+other}")

    print("\n== reads per phase (count, total sectors, by mode)")
    by_phase = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for seq, vsync, lbn, sectors, mode, dest, file in reads:
        cell = by_phase[phase_of(vsync)][mode]
        cell[0] += 1
        cell[1] += sectors
    for name, _, _ in PHASES:
        modes = by_phase.get(name, {})
        n = sum(v[0] for v in modes.values())
        s = sum(v[1] for v in modes.values())
        detail = ", ".join(f"{m}:{v[0]}r/{v[1]}s"
                           for m, v in sorted(modes.items()))
        print(f"  {name:22s} {n:6d} reads {s:8d} sectors  [{detail}]")

    print("\n== distinct LBN ranges, menu -> SC transition (vsync 620-1360)")
    trans = sorted((lbn, sectors, vsync, mode, file)
                   for _, vsync, lbn, sectors, mode, _, file in reads
                   if 620 <= vsync < 1360)
    ranges = []
    for lbn, sectors, vsync, mode, file in trans:
        if ranges and lbn == ranges[-1][1]:
            ranges[-1][1] = lbn + sectors
            ranges[-1][2] += sectors
            ranges[-1][3] = min(ranges[-1][3], vsync)
            ranges[-1][4] = max(ranges[-1][4], vsync)
            ranges[-1][5].add(mode)
            ranges[-1][6].add(file)
        else:
            ranges.append([lbn, lbn + sectors, sectors, vsync, vsync,
                           {mode}, {file}])
    for lo, hi, s, v0, v1, modes, files in ranges:
        print(f"  lbn 0x{lo:x}-0x{hi:x} ({s} sectors) vsync {v0}-{v1} "
              f"modes={sorted(modes)} files={sorted(files)}")
    if not ranges:
        print("  (none)")

    print("\n== distinct LBN ranges, SC settled (vsync >= 1360)")
    settled = sorted((lbn, sectors, vsync, mode, file)
                     for _, vsync, lbn, sectors, mode, _, file in reads
                     if vsync >= 1360)
    ranges = []
    for lbn, sectors, vsync, mode, file in settled:
        if ranges and lbn == ranges[-1][1]:
            ranges[-1][1] = lbn + sectors
            ranges[-1][2] += sectors
            ranges[-1][4] = max(ranges[-1][4], vsync)
            ranges[-1][5].add(mode)
            ranges[-1][6].add(file)
        else:
            ranges.append([lbn, lbn + sectors, sectors, vsync, vsync,
                           {mode}, {file}])
    for lo, hi, s, v0, v1, modes, files in ranges[:40]:
        print(f"  lbn 0x{lo:x}-0x{hi:x} ({s} sectors) vsync {v0}-{v1} "
              f"modes={sorted(modes)} files={sorted(files)}")
    if len(ranges) > 40:
        print(f"  ... +{len(ranges)-40} more ranges")
    if not ranges:
        print("  (none)")

    print("\n== file names (cdsearch + cdopen + cdread file=)")
    names = defaultdict(int)
    for _, name, _, _ in searches:
        names[f"search:{name}"] += 1
    for _, name, host, _ in opens:
        names[f"open:{name} (host {host})"] += 1
    for _, _, _, _, _, _, file in reads:
        if file != "-":
            names[f"read-file:{file}"] += 1
    for name in sorted(names):
        print(f"  {names[name]:6d}x {name}")
    if not names:
        print("  (none)")

    print("\n== plant lines with attributed cdread")
    by_seq = {seq: (vsync, lbn, sectors, mode, dest, file)
              for seq, vsync, lbn, sectors, mode, dest, file in reads}
    for vsync, addr, value, via, src, seq in plants:
        if seq != "-" and seq.isdigit() and int(seq) in by_seq:
            r = by_seq[int(seq)]
            print(f"  plant vsync={vsync} addr=0x{addr} value=0x{value} "
                  f"via={via} src={src} seq={seq} "
                  f"-> cdread vsync={r[0]} lbn=0x{r[1]:x} sectors={r[2]} "
                  f"mode={r[3]} dest=0x{r[4]:08x} file={r[5]}")
        else:
            print(f"  plant vsync={vsync} addr=0x{addr} value=0x{value} "
                  f"via={via} src={src} seq={seq} -> (unattributable)")


if __name__ == "__main__":
    main(sys.argv[1])
