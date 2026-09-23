#!/usr/bin/env python3
# T52 fix1: dedent the three t52_cdread calls to the `if` level so they read
# as unconditional (they are) with no -Wmisleading-indentation warning.
# Usage on bytesize: python3 t52-fix1.py (aborts unless exactly 3 lines change)
import sys

CDVD = "/home/brad/pcsx2-g7/pcsx2/pcsx2/CDVD/CDVD.cpp"
OLD = "\n\t\t\t\tt52_cdread("
NEW = "\n\t\t\tt52_cdread("

with open(CDVD) as f:
    c = f.read()
n = c.count(OLD)
print("old-indent count=%d want=3" % n)
if n != 3 or 't52_cdread("CD")' not in c:
    print("T52_FIX1_ABORT")
    sys.exit(1)
c = c.replace(OLD, NEW)
with open(CDVD, "w") as f:
    f.write(c)
print("T52_FIX1_DONE")
