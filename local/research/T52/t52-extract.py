#!/usr/bin/env python3
# T52 extract: emulog -> T52 trace (T52_CDREAD + T52_MARK lines, grammar-checked).
# Usage: python3 t52-extract.py <emulog> <trace-out>
import re
import sys

CDREAD = re.compile(
    r"T52_CDREAD seq=(\d+) vsync=(\d+) kind=(CD|DVD|CDDA) lbn=(\d+) sectors=(\d+) "
    r"blocksize=(\d+) speed=(\d+)x spindle=(CAV|CLV) readmode=(0x[0-9a-f]+) dest=-"
)
MARK = re.compile(r"T52_MARK vsync=(\d+) label=(title|menu|scentry|scsettled)")


def main():
    src, dst = sys.argv[1], sys.argv[2]
    n_cd = n_mark = rejects = 0
    last_seq = -1
    with open(src, errors="replace") as f, open(dst, "w") as o:
        for line in f:
            if "T52_CDREAD" in line:
                m = CDREAD.search(line)
                if not m:
                    rejects += 1
                    continue
                seq = int(m.group(1))
                if seq != last_seq + 1:
                    rejects += 1  # seq gap counts as reject (reported, line still kept)
                last_seq = seq
                n_cd += 1
                o.write(line[line.index("T52_CDREAD"):])
            elif "T52_MARK" in line:
                if not MARK.search(line):
                    rejects += 1
                    continue
                n_mark += 1
                o.write(line[line.index("T52_MARK"):])
    print("cdread=%d marks=%d rejects=%d last_seq=%d" % (n_cd, n_mark, rejects, last_seq))


main()
