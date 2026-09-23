#!/usr/bin/env python3
"""E48 boot wrapper: E33 route + PS2X_DIAG_WATCH on the 0x3b1140 node/pool.

Usage:
  python3 local/research/E48/e48_boot.py --build on|off --label e48b1 \
      --wall 120 --snap 1 --script "<E33 route>"

Same driver as E46 (local/research/E31/e31_boot.py via its module
globals), E48 run dir, per-variant build dir, no E44 taps. The watch list
is WATCH below (8-byte windows).
"""

import json
import os
import subprocess
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
E48 = os.path.join(WORK, "E48")

# Node 0x548840 (+0..+0x20), sibling nodes' +8 links, a 5th candidate
# node's links, codec/pool 0x587b00 (+0x10 count, +0x18 active sentinel,
# +0x20 free sentinel), holder 0x587b80 (+0 player, +0xc picture), and
# guest 0x8..0xf (targets of an unlink through close-poisoned 0xb links).
WATCH = [
    0x548840, 0x548848, 0x548850, 0x548858,
    0x548788, 0x5487c8, 0x548808, 0x548888,
    0x587b10, 0x587b18, 0x587b20,
    0x587b80, 0x587b88,
    0x8,
]

build = None
for i, a in enumerate(sys.argv):
    if a == "--build" and i + 1 < len(sys.argv):
        build = sys.argv[i + 1]
if build not in ("on", "off"):
    print("need --build on|off", file=sys.stderr)
    sys.exit(2)
i = sys.argv.index("--build")
del sys.argv[i:i + 2]

b.SPIKE = WORK
b.RUN = os.path.join(E48, "run")
b.RUNNER = os.path.join(E48, f"build-{build}", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

label = None
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
    "PS2X_DIAG_WATCH": ",".join(hex(a) for a in WATCH),
}
if "--script" in sys.argv or any(a.startswith("--script=") for a in sys.argv):
    BASE["PS2X_SKIP_MOVIE"] = "1"
b.BASE_ENV = BASE

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

sys.path.insert(0, os.path.join(REPO, "local/tooling"))
from p_lane_lease import SLOTS, claim, release

slot = claim(label if label else "e48x")
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
print(json.dumps({"event": "slot", "slot": slot, "peers": peers,
                  "build": build, "watch": BASE["PS2X_DIAG_WATCH"]}),
      flush=True)

rc = 99
try:
    rc = b.main()
finally:
    release(slot)
sys.exit(rc)
