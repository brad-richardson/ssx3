#!/usr/bin/env python3
"""G17: run Apple lldb batch with a host-side watchdog (macOS has no timeout).

Usage: g17-run-lldb.py <lldb-batch> <logfile> [watchdog-sec default 1500]
Exit: lldb's exit, or 124 on watchdog fire (log notes the fire).
"""
import subprocess
import sys

batch, logfile = sys.argv[1], sys.argv[2]
watch = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
with open(logfile, "w") as f:
    try:
        p = subprocess.run(["lldb", "-b", "-s", batch],
                           stdout=f, stderr=subprocess.STDOUT, timeout=watch)
        print("G17-RUNNER lldb exit=%d" % p.returncode, file=f)
        sys.exit(p.returncode)
    except subprocess.TimeoutExpired:
        print("G17-RUNNER WATCHDOG-FIRE after %ds" % watch, file=f)
        sys.exit(124)
