#!/usr/bin/env python3
"""E44 boot wrapper: vsync-clock pad script + scratchpad write watch.

Usage:
  python3 local/research/E44/e44_boot.py --label e44a --wall 300 --snap 30 \
      --script "<E33 route>" [--spw-from 1270 --spw-to 1280] [--extra 0x...,...]

Env added over E31's base: PS2X_E44_TRACE=<run>/e44-<label>.txt plus the
FROM/TO window (default 1270..1280) and PS2X_E44_EXTRA for the Boot-B
follow-up on a DMA source word.
"""

import os
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
b.SPIKE = WORK
b.RUN = os.path.join(WORK, "E44-run")
b.RUNNER = os.path.join(WORK, "E32-build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

import argparse
import json
import subprocess

pre = argparse.ArgumentParser(add_help=False)
pre.add_argument("--spw-from", type=str, default=None)
pre.add_argument("--spw-to", type=str, default=None)
pre.add_argument("--extra", type=str, default=None)
pre.add_argument("--append", action="store_true",
                 help="set PS2X_E44_APPEND=1 (Part 4 append/template watch)")
known, rest = pre.parse_known_args()
sys.argv = [sys.argv[0]] + rest

label = None
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]
    elif a.startswith("--label="):
        label = a.split("=", 1)[1]

trace_file = os.path.join(b.RUN, f"e44-{label}.txt") if label else None

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
}
if trace_file:
    BASE["PS2X_E44_TRACE"] = trace_file
if known.spw_from is not None:
    BASE["PS2X_E44_FROM"] = known.spw_from
if known.spw_to is not None:
    BASE["PS2X_E44_TO"] = known.spw_to
if known.extra is not None:
    BASE["PS2X_E44_EXTRA"] = known.extra
if known.append:
    BASE["PS2X_E44_APPEND"] = "1"
if "--script" in sys.argv or any(a.startswith("--script=") for a in sys.argv):
    BASE["PS2X_SKIP_MOVIE"] = "1"
b.BASE_ENV = BASE

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

# Two-slot regime: claim via p_lane_lease.py (first free slot), point
# the driver at that lease path, and excuse already-running other-slot
# runners from the alive-check. The driver releases the lease file at
# end; our release() then no-ops.
sys.path.insert(0, os.path.join(REPO, "local/tooling"))
from p_lane_lease import SLOTS, claim, release

if "--help" in sys.argv or "-h" in sys.argv:
    sys.exit(b.main())
slot = claim(label if label else "e44x")
if slot is None:
    print("REFUSE: no free boot slot (p_lane_lease.py status)", file=sys.stderr)
    sys.exit(2)
b.LEASE = SLOTS[slot]
pp = subprocess.run(["pgrep", "-x", "ps2EntryRunner"],
                    capture_output=True, text=True)
peers = [x for x in pp.stdout.split() if x.strip().isdigit()] \
    if pp.returncode == 0 else []
os.environ["P_LANE_PEER_PIDS"] = ",".join(peers)
os.environ["P_LANE_HOLD"] = "1"
print(json.dumps({"event": "slot", "slot": slot, "peers": peers}),
      flush=True)

rc = 99
try:
    rc = b.main()
finally:
    release(slot)
sys.exit(rc)
